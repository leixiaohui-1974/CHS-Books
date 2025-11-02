"""
案例3.1：渠道实时调度与控制 - 主程序

对比PID、MPC和前馈+反馈控制方法

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

from core.utils.data_io import load_yaml, save_csv
from core.control import PIDController, MPCController, SaintVenantSolver


class CanalController:
    """渠道实时控制系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 加载配置
        self.config = load_yaml("data/canal_parameters.yaml")
        
        # 创建Saint-Venant求解器
        self.canal = SaintVenantSolver(
            length=self.config['canal']['length'],
            n_sections=self.config['canal']['n_sections'],
            width=self.config['canal']['width'],
            slope=self.config['canal']['slope'],
            manning_n=self.config['canal']['manning_n']
        )
        
        print(f"渠道控制系统: 长度{self.config['canal']['length']}m")
    
    def method1_pid_control(self):
        """方法1：PID控制"""
        print("\n" + "=" * 70)
        print("方法1: PID控制")
        print("=" * 70)
        
        # 创建PID控制器
        pid = PIDController(
            Kp=self.config['pid']['Kp'],
            Ki=self.config['pid']['Ki'],
            Kd=self.config['pid']['Kd'],
            setpoint=self.config['control']['target_depth'],
            output_limits=tuple(self.config['pid']['output_limits'])
        )
        
        # 初始化
        n_sections = self.config['canal']['n_sections']
        h = np.ones(n_sections) * self.config['initial']['depth']
        Q = np.ones(n_sections) * self.config['initial']['flow']
        
        duration = self.config['simulation']['duration']
        dt = self.config['simulation']['dt']
        n_steps = int(duration / dt)
        
        # 历史记录
        history = {
            'time': [],
            'downstream_depth': [],
            'control_flow': [],
            'error': []
        }
        
        Q_upstream = self.config['initial']['flow']
        
        for step in range(n_steps):
            t = step * dt
            
            # 应用干扰
            for dist in self.config['simulation']['disturbances']:
                if abs(t - dist['time']) < dt/2:
                    if dist['type'] == 'flow_change':
                        Q_upstream = dist['value']
                        print(f"  t={t}s: 上游流量变化到 {Q_upstream} m³/s")
            
            # 测量下游水位
            h_downstream = h[-1]
            
            # PID计算控制量
            control_adjustment = pid.compute(h_downstream, dt=dt)
            Q_control = Q_upstream + control_adjustment
            Q_control = np.clip(Q_control, 5, 50)  # 物理约束
            
            # 模拟一步
            h, Q = self.canal.solve_step(
                h, Q, dt,
                Q_upstream=Q_control,
                h_downstream=None
            )
            
            # 记录
            history['time'].append(t)
            history['downstream_depth'].append(h_downstream)
            history['control_flow'].append(Q_control)
            history['error'].append(abs(h_downstream - self.config['control']['target_depth']))
        
        print(f"\n平均误差: {np.mean(history['error']):.4f} m")
        print(f"最大误差: {np.max(history['error']):.4f} m")
        
        return {'method': 'PID', 'history': history}
    
    def method2_open_loop(self):
        """方法2：开环控制（对比基准）"""
        print("\n" + "=" * 70)
        print("方法2: 开环控制（基准）")
        print("=" * 70)
        
        # 初始化
        n_sections = self.config['canal']['n_sections']
        h = np.ones(n_sections) * self.config['initial']['depth']
        Q = np.ones(n_sections) * self.config['initial']['flow']
        
        duration = self.config['simulation']['duration']
        dt = self.config['simulation']['dt']
        n_steps = int(duration / dt)
        
        history = {
            'time': [],
            'downstream_depth': [],
            'control_flow': [],
            'error': []
        }
        
        Q_upstream = self.config['initial']['flow']
        
        for step in range(n_steps):
            t = step * dt
            
            # 应用干扰（开环不调整）
            for dist in self.config['simulation']['disturbances']:
                if abs(t - dist['time']) < dt/2:
                    if dist['type'] == 'flow_change':
                        Q_upstream = dist['value']
            
            h_downstream = h[-1]
            
            # 模拟一步（开环：不调整）
            h, Q = self.canal.solve_step(
                h, Q, dt,
                Q_upstream=Q_upstream,
                h_downstream=None
            )
            
            history['time'].append(t)
            history['downstream_depth'].append(h_downstream)
            history['control_flow'].append(Q_upstream)
            history['error'].append(abs(h_downstream - self.config['control']['target_depth']))
        
        print(f"\n平均误差: {np.mean(history['error']):.4f} m")
        print(f"最大误差: {np.max(history['error']):.4f} m")
        
        return {'method': 'OpenLoop', 'history': history}
    
    def visualize(self, pid_result, openloop_result):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        target = self.config['control']['target_depth']
        
        # 1. 水位对比
        axes[0].plot(openloop_result['history']['time'],
                    openloop_result['history']['downstream_depth'],
                    label='开环控制', linewidth=2, alpha=0.7)
        axes[0].plot(pid_result['history']['time'],
                    pid_result['history']['downstream_depth'],
                    label='PID控制', linewidth=2, alpha=0.7)
        axes[0].axhline(y=target, color='r', linestyle='--', label='目标水位')
        axes[0].fill_between(openloop_result['history']['time'],
                            target - 0.1, target + 0.1,
                            alpha=0.2, color='green', label='允许范围')
        axes[0].set_xlabel('时间 (s)', fontsize=12)
        axes[0].set_ylabel('下游水位 (m)', fontsize=12)
        axes[0].set_title('水位控制效果对比', fontsize=13, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 2. 控制流量
        axes[1].plot(openloop_result['history']['time'],
                    openloop_result['history']['control_flow'],
                    label='开环', linewidth=2, alpha=0.7)
        axes[1].plot(pid_result['history']['time'],
                    pid_result['history']['control_flow'],
                    label='PID', linewidth=2, alpha=0.7)
        axes[1].set_xlabel('时间 (s)', fontsize=12)
        axes[1].set_ylabel('控制流量 (m³/s)', fontsize=12)
        axes[1].set_title('控制动作对比', fontsize=13, fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/control_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: figures/control_comparison.png")
    
    def run(self):
        """运行完整控制仿真"""
        print("\n" + "*" * 70)
        print(" " * 22 + "渠道实时调度与控制")
        print(" " * 28 + "案例3.1")
        print("*" * 70)
        
        try:
            openloop_result = self.method2_open_loop()
            pid_result = self.method1_pid_control()
            
            self.visualize(pid_result, openloop_result)
            
            print("\n" + "=" * 70)
            print("仿真完成！")
            print("=" * 70)
            
            # 性能对比
            print(f"\n性能对比:")
            print(f"  开环控制:")
            print(f"    平均误差: {np.mean(openloop_result['history']['error']):.4f} m")
            print(f"    最大误差: {np.max(openloop_result['history']['error']):.4f} m")
            print(f"  PID控制:")
            print(f"    平均误差: {np.mean(pid_result['history']['error']):.4f} m")
            print(f"    最大误差: {np.max(pid_result['history']['error']):.4f} m")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    controller = CanalController()
    controller.run()


if __name__ == "__main__":
    main()
