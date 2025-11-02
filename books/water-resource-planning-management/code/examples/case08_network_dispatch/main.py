"""
案例3.2：供水管网优化调度 - 主程序

对比LP、NLP和MPC三种优化方法

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

from core.utils.data_io import load_yaml
from src import WaterNetwork, Node, Pipe, PumpStation, HydraulicSolver, NetworkOptimizer


class NetworkDispatchSystem:
    """管网调度系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 加载配置
        self.config = load_yaml("data/network_config.yaml")
        
        # 创建管网
        self.network = self._build_network()
        
        # 创建求解器
        self.solver = HydraulicSolver(self.network)
        
        # 创建优化器
        self.optimizer = NetworkOptimizer(self.network, self.solver)
        
        print(f"管网调度系统: {len(self.network.pumps)}个泵站, {len(self.network.nodes)}个节点")
    
    def _build_network(self) -> WaterNetwork:
        """构建管网模型"""
        network = WaterNetwork()
        
        # 添加水厂节点
        for plant in self.config['water_plants']:
            node = Node(
                node_id=plant['id'],
                node_type='source',
                elevation=0.0
            )
            network.add_node(node)
        
        # 添加泵站
        for ps_cfg in self.config['pump_stations']:
            pump = PumpStation(
                pump_id=ps_cfg['id'],
                capacity_range=tuple(ps_cfg['capacity']),
                efficiency=ps_cfg['efficiency'],
                head_curve=ps_cfg['head_curve']
            )
            network.add_pump(pump)
            
            # 泵站也作为节点
            node = Node(
                node_id=ps_cfg['id'],
                node_type='junction',
                elevation=0.0
            )
            network.add_node(node)
        
        # 添加用户区节点
        for zone in self.config['demand_zones']:
            node = Node(
                node_id=zone['id'],
                node_type='junction',
                elevation=0.0,
                demand=zone['base_demand'],
                min_pressure=zone['min_pressure']
            )
            network.add_node(node)
        
        # 添加管道
        for i, pipe_cfg in enumerate(self.config['pipes']):
            pipe = Pipe(
                pipe_id=f"P{i+1}",
                from_node=pipe_cfg['from'],
                to_node=pipe_cfg['to'],
                length=pipe_cfg['length'],
                diameter=pipe_cfg['diameter'],
                roughness=pipe_cfg['roughness']
            )
            network.add_pipe(pipe)
        
        return network
    
    def _get_period_demand(self, period: int) -> Dict[str, float]:
        """获取指定时段的需水量"""
        pattern = self.config['scheduling']['demand_pattern']
        multiplier = pattern[period % 24]
        
        demands = {}
        for zone in self.config['demand_zones']:
            demands[zone['id']] = zone['base_demand'] * multiplier
        
        return demands
    
    def method1_baseline(self):
        """方法1：基准调度（均匀分配）"""
        print("\n" + "=" * 70)
        print("方法1: 基准调度（均匀分配）")
        print("=" * 70)
        
        n_periods = self.config['scheduling']['time_horizon']
        
        total_cost = 0.0
        total_power = 0.0
        pressure_violations = 0
        
        for t in range(n_periods):
            demands = self._get_period_demand(t)
            total_demand = sum(demands.values())
            
            # 均匀分配
            n_pumps = len(self.network.pumps)
            avg_flow = total_demand / n_pumps
            
            flows = {}
            for pump in self.network.pumps.values():
                flows[pump.id] = np.clip(avg_flow, pump.min_flow, pump.max_flow)
            
            # 求解水力
            self.solver.solve(flows)
            
            # 统计
            power = self.network.get_total_power()
            cost = power * 0.8  # 电价
            total_cost += cost
            total_power += power
            
            # 检查压力约束
            pressure_ok = self.network.check_pressure_constraints()
            if not all(pressure_ok.values()):
                pressure_violations += 1
        
        avg_power = total_power / n_periods
        pressure_rate = (n_periods - pressure_violations) / n_periods * 100
        
        print(f"\n总成本: {total_cost:.2f} 元")
        print(f"平均功率: {avg_power:.2f} kW")
        print(f"压力满足率: {pressure_rate:.1f}%")
        
        return {
            'method': 'Baseline',
            'total_cost': total_cost,
            'avg_power': avg_power,
            'pressure_rate': pressure_rate
        }
    
    def method2_lp(self):
        """方法2：线性规划优化"""
        print("\n" + "=" * 70)
        print("方法2: 线性规划优化")
        print("=" * 70)
        
        start_time = time.time()
        
        n_periods = self.config['scheduling']['time_horizon']
        
        total_cost = 0.0
        total_power = 0.0
        pressure_violations = 0
        
        # 简化成本系数
        power_costs = {pump.id: 1.0 for pump in self.network.pumps.values()}
        
        for t in range(n_periods):
            demands = self._get_period_demand(t)
            total_demand = sum(demands.values())
            
            # LP优化
            flows = self.optimizer.optimize_lp(total_demand, power_costs)
            
            # 求解水力
            self.solver.solve(flows)
            
            # 统计
            power = self.network.get_total_power()
            cost = power * 0.8
            total_cost += cost
            total_power += power
            
            pressure_ok = self.network.check_pressure_constraints()
            if not all(pressure_ok.values()):
                pressure_violations += 1
        
        elapsed_time = time.time() - start_time
        avg_power = total_power / n_periods
        pressure_rate = (n_periods - pressure_violations) / n_periods * 100
        
        print(f"\n总成本: {total_cost:.2f} 元")
        print(f"平均功率: {avg_power:.2f} kW")
        print(f"压力满足率: {pressure_rate:.1f}%")
        print(f"计算时间: {elapsed_time:.2f} 秒")
        
        return {
            'method': 'LP',
            'total_cost': total_cost,
            'avg_power': avg_power,
            'pressure_rate': pressure_rate,
            'time': elapsed_time
        }
    
    def method3_nlp(self):
        """方法3：非线性规划优化"""
        print("\n" + "=" * 70)
        print("方法3: 非线性规划优化")
        print("=" * 70)
        
        start_time = time.time()
        
        n_periods = 6  # 只计算6个时段（节省时间）
        
        total_cost = 0.0
        total_power = 0.0
        pressure_violations = 0
        
        for t in range(n_periods):
            demands = self._get_period_demand(t)
            
            # NLP优化
            result = self.optimizer.optimize_nlp(demands, power_cost=0.8)
            
            # 统计
            total_cost += result['cost']
            total_power += result['power']
            
            if not result['pressure_ok']:
                pressure_violations += 1
            
            print(f"  时段{t+1}: 成本={result['cost']:.2f}元, 功率={result['power']:.2f}kW")
        
        elapsed_time = time.time() - start_time
        avg_power = total_power / n_periods
        pressure_rate = (n_periods - pressure_violations) / n_periods * 100
        
        print(f"\n总成本: {total_cost:.2f} 元 ({n_periods}时段)")
        print(f"平均功率: {avg_power:.2f} kW")
        print(f"压力满足率: {pressure_rate:.1f}%")
        print(f"计算时间: {elapsed_time:.2f} 秒")
        
        return {
            'method': 'NLP',
            'total_cost': total_cost,
            'avg_power': avg_power,
            'pressure_rate': pressure_rate,
            'time': elapsed_time
        }
    
    def visualize(self, baseline, lp_result, nlp_result):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        methods = [baseline, lp_result, nlp_result]
        method_names = ['基准', 'LP', 'NLP']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # 1. 总成本对比
        costs = [m['total_cost'] for m in methods]
        axes[0, 0].bar(method_names, costs, color=colors, alpha=0.7)
        axes[0, 0].set_ylabel('总成本 (元)', fontsize=11)
        axes[0, 0].set_title('总成本对比', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for i, (name, cost) in enumerate(zip(method_names, costs)):
            axes[0, 0].text(i, cost, f'{cost:.0f}', 
                          ha='center', va='bottom', fontsize=10)
        
        # 2. 平均功率对比
        powers = [m['avg_power'] for m in methods]
        axes[0, 1].bar(method_names, powers, color=colors, alpha=0.7)
        axes[0, 1].set_ylabel('平均功率 (kW)', fontsize=11)
        axes[0, 1].set_title('平均功率对比', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        for i, (name, power) in enumerate(zip(method_names, powers)):
            axes[0, 1].text(i, power, f'{power:.1f}', 
                          ha='center', va='bottom', fontsize=10)
        
        # 3. 压力满足率
        rates = [m['pressure_rate'] for m in methods]
        axes[1, 0].bar(method_names, rates, color=colors, alpha=0.7)
        axes[1, 0].set_ylabel('压力满足率 (%)', fontsize=11)
        axes[1, 0].set_title('压力约束满足率', fontsize=12, fontweight='bold')
        axes[1, 0].set_ylim([0, 105])
        axes[1, 0].axhline(y=100, color='red', linestyle='--', alpha=0.5, label='目标')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        axes[1, 0].legend()
        
        for i, (name, rate) in enumerate(zip(method_names, rates)):
            axes[1, 0].text(i, rate, f'{rate:.1f}%', 
                          ha='center', va='bottom', fontsize=10)
        
        # 4. 节能效果
        baseline_cost = baseline['total_cost']
        savings = [(baseline_cost - m['total_cost']) / baseline_cost * 100 
                  for m in methods]
        
        axes[1, 1].bar(method_names, savings, color=colors, alpha=0.7)
        axes[1, 1].set_ylabel('节能率 (%)', fontsize=11)
        axes[1, 1].set_title('相对基准的节能效果', fontsize=12, fontweight='bold')
        axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        for i, (name, saving) in enumerate(zip(method_names, savings)):
            axes[1, 1].text(i, saving, f'{saving:.1f}%', 
                          ha='center', va='bottom' if saving > 0 else 'top', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/dispatch_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: figures/dispatch_comparison.png")
    
    def run(self):
        """运行完整调度仿真"""
        print("\n" + "*" * 70)
        print(" " * 22 + "供水管网优化调度")
        print(" " * 28 + "案例3.2")
        print("*" * 70)
        
        try:
            baseline = self.method1_baseline()
            lp_result = self.method2_lp()
            nlp_result = self.method3_nlp()
            
            self.visualize(baseline, lp_result, nlp_result)
            
            print("\n" + "=" * 70)
            print("优化完成！")
            print("=" * 70)
            
            # 性能总结
            print(f"\n性能总结:")
            print(f"  基准调度:")
            print(f"    总成本: {baseline['total_cost']:.2f} 元")
            print(f"    平均功率: {baseline['avg_power']:.2f} kW")
            print(f"    压力满足率: {baseline['pressure_rate']:.1f}%")
            
            print(f"\n  线性规划:")
            print(f"    总成本: {lp_result['total_cost']:.2f} 元 (节省{(1-lp_result['total_cost']/baseline['total_cost'])*100:.1f}%)")
            print(f"    平均功率: {lp_result['avg_power']:.2f} kW")
            print(f"    计算时间: {lp_result['time']:.2f} 秒")
            
            print(f"\n  非线性规划:")
            print(f"    总成本: {nlp_result['total_cost']:.2f} 元 (节省{(1-nlp_result['total_cost']/baseline['total_cost'])*100:.1f}%)")
            print(f"    平均功率: {nlp_result['avg_power']:.2f} kW")
            print(f"    计算时间: {nlp_result['time']:.2f} 秒")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = NetworkDispatchSystem()
    system.run()


if __name__ == "__main__":
    main()
