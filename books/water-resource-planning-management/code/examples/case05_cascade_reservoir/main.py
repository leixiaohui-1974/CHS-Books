"""
案例2.2：流域梯级水库群联合调度 - 主程序

运用动态规划(DP)和逐次逼近法(POA)求解梯级水库优化调度

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from core.utils.data_io import load_yaml, load_csv, save_csv
from src.reservoir_model import Reservoir, CascadeSystem
from src.progressive_optimality import ProgressiveOptimalityAlgorithm


class CascadeSchedulingOptimizer:
    """梯级水库调度优化系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 加载配置
        self.config = load_yaml("data/reservoir_config.yaml")
        self.inflow_data = load_csv("data/inflow_data.csv")
        
        # 创建水库对象
        self.reservoirs = []
        for res_config in self.config['reservoirs']:
            res = Reservoir(res_config)
            # 设置库容曲线参数
            if f"reservoir_{res.id}" in self.config['level_storage']:
                res.vs_params = self.config['level_storage'][f"reservoir_{res.id}"]
            if f"reservoir_{res.id}" in self.config['tailwater']:
                res.tw_params = self.config['tailwater'][f"reservoir_{res.id}"]
            self.reservoirs.append(res)
        
        # 创建梯级系统
        self.cascade = CascadeSystem(
            self.reservoirs,
            self.config['cascade']
        )
        
        # 准备数据
        self.prepare_data()
        
        print(f"梯级水库系统: {len(self.reservoirs)}座水库, {self.n_periods}个时段")
    
    def prepare_data(self):
        """准备输入数据"""
        # 入流数据
        self.inflows = {}
        for res in self.reservoirs:
            col_name = f"reservoir_{res.id}"
            if col_name in self.inflow_data.columns:
                self.inflows[res.id] = self.inflow_data[col_name].values.tolist()
        
        self.n_periods = len(self.inflows[1])
        
        # 初始库容
        self.initial_storages = {}
        for res in self.reservoirs:
            self.initial_storages[res.id] = res.level_to_storage(res.initial_level)
    
    def method1_baseline(self):
        """方法1：基准方案（出库=入流）"""
        print("\n" + "=" * 70)
        print("方法1: 基准方案（出库=入流）")
        print("=" * 70)
        
        # 简单策略：出库=区间入流+上游来水
        discharges = {}
        for res_id in self.cascade.reservoirs:
            discharges[res_id] = []
            for t in range(self.n_periods):
                total_inflow = self.inflows[res_id][t]
                # 加上上游来水
                for rel in self.cascade.cascade_relations:
                    if rel['downstream'] == res_id:
                        upstream_id = rel['upstream']
                        if t > 0:
                            total_inflow += discharges[upstream_id][t-1]
                discharges[res_id].append(total_inflow)
        
        # 模拟运行
        results, total_energy = self.cascade.simulate(
            self.initial_storages,
            discharges,
            self.inflows
        )
        
        print(f"\n总发电量: {total_energy:.2f} MWh")
        
        # 各水库发电量
        for res_id, reservoir in self.cascade.reservoirs.items():
            res_energy = sum(results['powers'][res_id]) * 864000 / 3600
            print(f"  {reservoir.name}: {res_energy:.2f} MWh ({res_energy/total_energy*100:.1f}%)")
        
        return {'method': 'Baseline', 'energy': total_energy, 'discharges': discharges}
    
    def method2_poa(self):
        """方法2：逐次逼近法（POA）"""
        print("\n" + "=" * 70)
        print("方法2: 逐次逼近法（POA）")
        print("=" * 70)
        
        poa = ProgressiveOptimalityAlgorithm(
            self.cascade,
            max_iterations=self.config['scheduling']['poa']['max_iterations'],
            tolerance=self.config['scheduling']['poa']['convergence_tolerance']
        )
        
        discharges, obj_history = poa.optimize(
            self.inflows,
            self.initial_storages,
            verbose=True
        )
        
        # 最终结果
        results, total_energy = self.cascade.simulate(
            self.initial_storages,
            discharges,
            self.inflows
        )
        
        print(f"\n最优总发电量: {total_energy:.2f} MWh")
        print(f"收敛迭代次数: {len(obj_history)}")
        
        # 各水库发电量
        for res_id, reservoir in self.cascade.reservoirs.items():
            res_energy = sum(results['powers'][res_id]) * 864000 / 3600
            print(f"  {reservoir.name}: {res_energy:.2f} MWh ({res_energy/total_energy*100:.1f}%)")
        
        return {
            'method': 'POA',
            'energy': total_energy,
            'discharges': discharges,
            'results': results,
            'obj_history': obj_history
        }
    
    def method3_ga(self):
        """方法3：遗传算法（对比）"""
        print("\n" + "=" * 70)
        print("方法3: 遗传算法（GA）")
        print("=" * 70)
        
        from core.optimization import GeneticAlgorithm
        
        # 编码：所有水库所有时段的出库流量
        n_vars = len(self.reservoirs) * self.n_periods
        
        # 变量边界
        bounds = []
        for res in self.reservoirs:
            for t in range(self.n_periods):
                bounds.append((
                    self.config['constraints']['min_discharge'],
                    self.config['constraints']['max_discharge']
                ))
        
        # 适应度函数
        def fitness(x):
            # 解码
            discharges = {}
            idx = 0
            for res in self.reservoirs:
                discharges[res.id] = []
                for t in range(self.n_periods):
                    discharges[res.id].append(x[idx])
                    idx += 1
            
            try:
                # 模拟
                _, energy = self.cascade.simulate(
                    self.initial_storages,
                    discharges,
                    self.inflows
                )
                return energy
            except:
                return 0
        
        # 优化
        ga = GeneticAlgorithm(
            pop_size=self.config['scheduling']['ga']['pop_size'],
            n_genes=n_vars,
            bounds=bounds,
            crossover_rate=self.config['scheduling']['ga']['crossover_rate'],
            mutation_rate=self.config['scheduling']['ga']['mutation_rate']
        )
        
        best_x, best_f = ga.optimize(
            fitness,
            n_generations=self.config['scheduling']['ga']['n_generations']
        )
        
        # 解码最优解
        discharges = {}
        idx = 0
        for res in self.reservoirs:
            discharges[res.id] = []
            for t in range(self.n_periods):
                discharges[res.id].append(best_x[idx])
                idx += 1
        
        print(f"\n最优发电量: {best_f:.2f} MWh")
        
        return {'method': 'GA', 'energy': best_f, 'discharges': discharges}
    
    def visualize(self, baseline, poa_result, ga_result):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 发电量对比
        fig, ax = plt.subplots(figsize=(10, 6))
        methods = ['基准方案', 'POA', 'GA']
        energies = [baseline['energy'], poa_result['energy'], ga_result['energy']]
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        
        bars = ax.bar(methods, energies, color=colors, alpha=0.8, edgecolor='black')
        
        # 添加数值标签
        for bar, energy in zip(bars, energies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{energy:.0f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('总发电量 (MWh)', fontsize=12)
        ax.set_title('不同方法发电量对比', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/energy_comparison.png", dpi=300)
        plt.close()
        
        # 2. POA收敛过程
        if 'obj_history' in poa_result:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(range(1, len(poa_result['obj_history'])+1),
                   poa_result['obj_history'],
                   'o-', linewidth=2, markersize=6)
            ax.set_xlabel('迭代次数', fontsize=12)
            ax.set_ylabel('发电量 (MWh)', fontsize=12)
            ax.set_title('POA收敛过程', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "figures/poa_convergence.png", dpi=300)
            plt.close()
        
        # 3. 调度过程曲线（POA结果）
        if 'results' in poa_result:
            results = poa_result['results']
            periods = range(1, self.n_periods + 1)
            
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            
            # 出库流量
            for res_id, reservoir in self.cascade.reservoirs.items():
                axes[0].plot(periods, poa_result['discharges'][res_id],
                           'o-', label=reservoir.name, linewidth=2)
            axes[0].set_xlabel('时段', fontsize=12)
            axes[0].set_ylabel('出库流量 (m³/s)', fontsize=12)
            axes[0].set_title('出库流量过程', fontsize=13, fontweight='bold')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # 水位过程
            for res_id, reservoir in self.cascade.reservoirs.items():
                axes[1].plot(periods, results['levels'][res_id][:-1],
                           'o-', label=reservoir.name, linewidth=2)
                # 添加正常蓄水位线
                axes[1].axhline(y=reservoir.normal_level,
                              linestyle='--', alpha=0.5)
            axes[1].set_xlabel('时段', fontsize=12)
            axes[1].set_ylabel('水位 (m)', fontsize=12)
            axes[1].set_title('水位过程', fontsize=13, fontweight='bold')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "figures/operation_curves.png", dpi=300)
            plt.close()
        
        print(f"  已保存: figures/")
    
    def generate_report(self, baseline, poa_result, ga_result):
        """生成优化报告"""
        print("\n" + "=" * 70)
        print("生成优化报告")
        print("=" * 70)
        
        # 对比结果
        comparison = pd.DataFrame({
            'method': ['基准方案', 'POA', 'GA'],
            'total_energy_MWh': [
                baseline['energy'],
                poa_result['energy'],
                ga_result['energy']
            ]
        })
        
        # 计算改进率
        comparison['improvement_%'] = (
            (comparison['total_energy_MWh'] - baseline['energy']) /
            baseline['energy'] * 100
        )
        
        save_csv(comparison, self.results_dir / "optimization_comparison.csv")
        
        print(f"\n优化结果已保存:")
        print(f"  - optimization_comparison.csv")
        print(f"  - figures/")
    
    def run(self):
        """运行完整优化流程"""
        print("\n" + "*" * 70)
        print(" " * 20 + "流域梯级水库群联合调度")
        print(" " * 28 + "案例2.2")
        print("*" * 70)
        
        try:
            baseline = self.method1_baseline()
            poa_result = self.method2_poa()
            ga_result = self.method3_ga()
            
            self.visualize(baseline, poa_result, ga_result)
            self.generate_report(baseline, poa_result, ga_result)
            
            print("\n" + "=" * 70)
            print("优化完成！")
            print("=" * 70)
            
            # 总结
            print(f"\n总结:")
            print(f"  基准方案: {baseline['energy']:.2f} MWh")
            print(f"  POA优化:  {poa_result['energy']:.2f} MWh (+{(poa_result['energy']-baseline['energy'])/baseline['energy']*100:.1f}%)")
            print(f"  GA优化:   {ga_result['energy']:.2f} MWh (+{(ga_result['energy']-baseline['energy'])/baseline['energy']*100:.1f}%)")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    optimizer = CascadeSchedulingOptimizer()
    optimizer.run()


if __name__ == "__main__":
    main()
