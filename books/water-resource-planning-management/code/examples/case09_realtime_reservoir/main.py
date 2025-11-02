"""
案例3.3：水库群实时优化调度 - 主程序

对比离线+修正、MPC滚动和鲁棒MPC三种方法

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from scipy.optimize import minimize

from core.utils.data_io import load_yaml


class RealtimeReservoirSystem:
    """水库群实时调度系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 加载配置
        self.config = load_yaml("data/realtime_config.yaml")
        
        self.n_reservoirs = len(self.config['reservoirs'])
        
        print(f"水库群实时调度系统: {self.n_reservoirs}座水库")
    
    def water_balance(self, V, I, Q, dt=1.0):
        """
        水量平衡
        
        V_{t+1} = V_t + (I_t - Q_t) * dt * 3.6
        
        dt in hours, I,Q in m³/s, V in 万m³
        """
        return V + (I - Q) * dt * 3.6 / 10000
    
    def storage_to_level(self, V, reservoir_id):
        """库容转水位（简化线性）"""
        curve = self.config['level_storage_curves'][reservoir_id]
        
        if V <= curve['dead_storage']:
            return curve['dead_level']
        
        # 线性插值
        ratio = (V - curve['dead_storage']) / (curve['normal_storage'] - curve['dead_storage'])
        level = curve['dead_level'] + ratio * (curve['normal_level'] - curve['dead_level'])
        
        return level
    
    def calculate_power(self, Q, H, efficiency=0.9):
        """
        计算发电功率
        
        P = 9.81 * Q * H * η / 1000  (MW)
        """
        if Q < 1e-6:
            return 0.0
        
        return 9.81 * Q * H * efficiency / 1000
    
    def get_inflow(self, t, with_noise=False):
        """获取来水（含噪声）"""
        inflows = {}
        for res in self.config['reservoirs']:
            res_id = res['id']
            forecast = self.config['simulation']['inflow_forecast'][res_id]
            idx = int(t) % len(forecast)
            I = forecast[idx]
            
            if with_noise:
                # 添加随机误差
                noise_std = self.config['uncertainty']['inflow_error_std']
                I = I * (1 + np.random.normal(0, noise_std))
                I = max(0, I)
            
            inflows[res_id] = I
        
        return inflows
    
    def method1_offline_correction(self):
        """方法1：离线优化+实时修正"""
        print("\n" + "=" * 70)
        print("方法1: 离线优化+实时PID修正")
        print("=" * 70)
        
        start_time = time.time()
        
        duration = self.config['simulation']['duration']
        dt = self.config['simulation']['dt']
        n_steps = int(duration / dt)
        
        # 初始库容
        V = {res['id']: self.config['simulation']['initial_storage'][res['id']] 
             for res in self.config['reservoirs']}
        
        total_generation = 0.0
        violations = 0
        
        # 离线计划（简单策略：恒定出流）
        planned_discharge = {res['id']: 200.0 for res in self.config['reservoirs']}
        
        history = {'t': [], 'generation': [], 'storage': {res['id']: [] for res in self.config['reservoirs']}}
        
        for t in range(n_steps):
            # 实际来水（含噪声）
            inflows = self.get_inflow(t, with_noise=True)
            
            # PID修正（简化）
            generation = 0.0
            
            for res in self.config['reservoirs']:
                res_id = res['id']
                I = inflows[res_id]
                Q = planned_discharge[res_id]
                
                # 水位修正
                current_level = self.storage_to_level(V[res_id], res_id)
                target_level = res['normal_level']
                error = current_level - target_level
                
                # PID修正出流（Kp=2.0）
                Q_correction = 2.0 * error
                Q = Q + Q_correction
                Q = np.clip(Q, res['min_discharge'], res['max_discharge'])
                
                # 更新库容
                V[res_id] = self.water_balance(V[res_id], I, Q, dt)
                V[res_id] = np.clip(V[res_id], res['dead_storage'], res['capacity'])
                
                # 计算发电
                H = current_level - 10  # 简化尾水位
                P = self.calculate_power(Q, H)
                generation += P
                
                # 检查约束
                if current_level < res['min_level'] or current_level > res['max_level']:
                    violations += 1
                
                history['storage'][res_id].append(V[res_id])
            
            total_generation += generation * dt
            history['t'].append(t)
            history['generation'].append(generation)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n总发电量: {total_generation:.2f} MWh")
        print(f"约束违约: {violations}次")
        print(f"计算时间: {elapsed_time:.2f} 秒")
        
        return {
            'method': 'Offline+PID',
            'generation': total_generation,
            'violations': violations,
            'time': elapsed_time,
            'history': history
        }
    
    def method2_mpc_rolling(self):
        """方法2：MPC滚动优化"""
        print("\n" + "=" * 70)
        print("方法2: MPC滚动优化")
        print("=" * 70)
        
        start_time = time.time()
        
        duration = self.config['simulation']['duration']
        dt = self.config['simulation']['dt']
        n_steps = int(duration / dt)
        horizon = self.config['mpc']['horizon']
        
        # 初始库容
        V = {res['id']: self.config['simulation']['initial_storage'][res['id']] 
             for res in self.config['reservoirs']}
        
        total_generation = 0.0
        violations = 0
        
        history = {'t': [], 'generation': [], 'storage': {res['id']: [] for res in self.config['reservoirs']}}
        
        for t in range(n_steps):
            # MPC优化
            result = self._solve_mpc(V, t, horizon)
            
            # 执行第一步决策
            Q_optimal = result['discharge'][0]
            
            # 实际来水
            inflows = self.get_inflow(t, with_noise=True)
            
            generation = 0.0
            for i, res in enumerate(self.config['reservoirs']):
                res_id = res['id']
                I = inflows[res_id]
                Q = Q_optimal[i]
                
                # 更新库容
                V[res_id] = self.water_balance(V[res_id], I, Q, dt)
                V[res_id] = np.clip(V[res_id], res['dead_storage'], res['capacity'])
                
                # 计算发电
                current_level = self.storage_to_level(V[res_id], res_id)
                H = current_level - 10
                P = self.calculate_power(Q, H)
                generation += P
                
                # 检查约束
                if current_level < res['min_level'] or current_level > res['max_level']:
                    violations += 1
                
                history['storage'][res_id].append(V[res_id])
            
            total_generation += generation * dt
            history['t'].append(t)
            history['generation'].append(generation)
            
            if (t + 1) % 6 == 0:
                print(f"  时段{t+1}: 发电={generation:.2f}MW")
        
        elapsed_time = time.time() - start_time
        
        print(f"\n总发电量: {total_generation:.2f} MWh")
        print(f"约束违约: {violations}次")
        print(f"计算时间: {elapsed_time:.2f} 秒")
        
        return {
            'method': 'MPC',
            'generation': total_generation,
            'violations': violations,
            'time': elapsed_time,
            'history': history
        }
    
    def _solve_mpc(self, V_current, t_current, horizon):
        """求解MPC优化问题"""
        n_res = self.n_reservoirs
        n_vars = n_res * horizon  # 决策变量：各水库各时段出流
        
        # 目标函数：最大化发电量
        def objective(x):
            Q = x.reshape(horizon, n_res)
            total_power = 0.0
            
            V = {res['id']: V_current[res['id']] for res in self.config['reservoirs']}
            
            for t in range(horizon):
                inflows = self.get_inflow(t_current + t, with_noise=False)
                
                for i, res in enumerate(self.config['reservoirs']):
                    res_id = res['id']
                    I = inflows[res_id]
                    q = Q[t, i]
                    
                    # 发电
                    level = self.storage_to_level(V[res_id], res_id)
                    H = level - 10
                    P = self.calculate_power(q, H)
                    total_power += P
                    
                    # 更新库容
                    V[res_id] = self.water_balance(V[res_id], I, q)
            
            return -total_power  # 最小化负发电量
        
        # 约束
        constraints = []
        
        # 初始猜测
        x0 = np.ones(n_vars) * 200.0
        
        # 变量界限
        bounds = []
        for t in range(horizon):
            for res in self.config['reservoirs']:
                bounds.append((res['min_discharge'], res['max_discharge']))
        
        # 简化求解（不加复杂约束，避免计算过慢）
        result = minimize(
            objective,
            x0,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 50}
        )
        
        Q_optimal = result.x.reshape(horizon, n_res)
        
        return {'discharge': Q_optimal}
    
    def visualize(self, offline_result, mpc_result):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. 发电功率对比
        axes[0, 0].plot(offline_result['history']['t'], 
                       offline_result['history']['generation'],
                       label='离线+PID', linewidth=2, alpha=0.7)
        axes[0, 0].plot(mpc_result['history']['t'], 
                       mpc_result['history']['generation'],
                       label='MPC', linewidth=2, alpha=0.7)
        axes[0, 0].set_xlabel('时间 (h)', fontsize=11)
        axes[0, 0].set_ylabel('发电功率 (MW)', fontsize=11)
        axes[0, 0].set_title('发电功率对比', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 总发电量对比
        methods = ['离线+PID', 'MPC']
        generations = [offline_result['generation'], mpc_result['generation']]
        colors = ['#FF6B6B', '#4ECDC4']
        
        axes[0, 1].bar(methods, generations, color=colors, alpha=0.7)
        axes[0, 1].set_ylabel('总发电量 (MWh)', fontsize=11)
        axes[0, 1].set_title('总发电量对比', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        for i, (method, gen) in enumerate(zip(methods, generations)):
            axes[0, 1].text(i, gen, f'{gen:.0f}', 
                          ha='center', va='bottom', fontsize=10)
        
        # 3. 上游水库库容变化
        res_id = 'R1'
        axes[1, 0].plot(offline_result['history']['t'], 
                       offline_result['history']['storage'][res_id],
                       label='离线+PID', linewidth=2, alpha=0.7)
        axes[1, 0].plot(mpc_result['history']['t'], 
                       mpc_result['history']['storage'][res_id],
                       label='MPC', linewidth=2, alpha=0.7)
        
        # 添加约束线
        normal_storage = self.config['reservoirs'][0]['normal_storage']
        axes[1, 0].axhline(y=normal_storage, color='r', linestyle='--', 
                          alpha=0.5, label='正常库容')
        
        axes[1, 0].set_xlabel('时间 (h)', fontsize=11)
        axes[1, 0].set_ylabel('库容 (万m³)', fontsize=11)
        axes[1, 0].set_title('上游水库库容变化', fontsize=12, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 计算时间对比
        times = [offline_result['time'], mpc_result['time']]
        
        axes[1, 1].bar(methods, times, color=colors, alpha=0.7)
        axes[1, 1].set_ylabel('计算时间 (秒)', fontsize=11)
        axes[1, 1].set_title('计算效率对比', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        for i, (method, t) in enumerate(zip(methods, times)):
            axes[1, 1].text(i, t, f'{t:.2f}s', 
                          ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/realtime_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: figures/realtime_comparison.png")
    
    def run(self):
        """运行完整实时调度仿真"""
        print("\n" + "*" * 70)
        print(" " * 20 + "水库群实时优化调度")
        print(" " * 28 + "案例3.3")
        print("*" * 70)
        
        try:
            offline_result = self.method1_offline_correction()
            mpc_result = self.method2_mpc_rolling()
            
            self.visualize(offline_result, mpc_result)
            
            print("\n" + "=" * 70)
            print("实时调度完成！")
            print("=" * 70)
            
            # 性能对比
            print(f"\n性能对比:")
            print(f"  离线+PID:")
            print(f"    总发电量: {offline_result['generation']:.2f} MWh")
            print(f"    约束违约: {offline_result['violations']}次")
            print(f"    计算时间: {offline_result['time']:.2f} 秒")
            
            print(f"\n  MPC滚动:")
            print(f"    总发电量: {mpc_result['generation']:.2f} MWh ({(mpc_result['generation']/offline_result['generation']-1)*100:+.1f}%)")
            print(f"    约束违约: {mpc_result['violations']}次")
            print(f"    计算时间: {mpc_result['time']:.2f} 秒")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = RealtimeReservoirSystem()
    system.run()


if __name__ == "__main__":
    main()
