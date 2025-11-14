"""
案例20：多水库梯级联合调度
=========================

演示梯级水库系统的联合优化调度，
考虑上下游联动、补偿调节等。

核心内容：
1. 梯级水库系统建模
2. 上下游联动机制
from pathlib import Path
3. 联合优化调度
4. 补偿调节分析
5. 综合效益评估

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.reservoir.operation_rules import (
    ReservoirRules, FloodControlRule, ConservationRule
)

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CascadeReservoirSystem:
    """梯级水库系统类"""
    
    def __init__(self):
        """初始化梯级水库系统"""
        self.reservoirs = []
        self.connections = []  # 水库连接关系
        
    def add_reservoir(self, reservoir: ReservoirRules, name: str):
        """
        添加水库
        
        Parameters
        ----------
        reservoir : ReservoirRules
            水库对象
        name : str
            水库名称
        """
        self.reservoirs.append({
            'reservoir': reservoir,
            'name': name,
            'index': len(self.reservoirs)
        })
    
    def connect(self, upstream_idx: int, downstream_idx: int, 
                travel_time: int = 1):
        """
        连接上下游水库
        
        Parameters
        ----------
        upstream_idx : int
            上游水库索引
        downstream_idx : int
            下游水库索引
        travel_time : int
            传播时间（天）
        """
        self.connections.append({
            'upstream': upstream_idx,
            'downstream': downstream_idx,
            'travel_time': travel_time
        })
    
    def operate(self, 
                initial_levels: list,
                lateral_inflows: list,
                dt: float = 86400.0) -> dict:
        """
        执行梯级联合调度
        
        Parameters
        ----------
        initial_levels : list
            各水库初始水位
        lateral_inflows : list
            各水库区间入流序列
        dt : float
            时间步长 (s)
            
        Returns
        -------
        results : dict
            各水库调度结果
        """
        n_reservoirs = len(self.reservoirs)
        n_steps = len(lateral_inflows[0])
        
        # 初始化结果
        results = {}
        for i, res_info in enumerate(self.reservoirs):
            results[res_info['name']] = {
                'level': np.zeros(n_steps),
                'storage': np.zeros(n_steps),
                'outflow': np.zeros(n_steps),
                'inflow': np.zeros(n_steps)
            }
            results[res_info['name']]['level'][0] = initial_levels[i]
            results[res_info['name']]['storage'][0] = \
                res_info['reservoir'].level_storage_curve(initial_levels[i])
        
        # 时间推进
        for t in range(n_steps - 1):
            # 计算各水库总入流（区间入流+上游来水）
            total_inflows = [lateral_inflows[i][t] for i in range(n_reservoirs)]
            
            # 添加上游来水
            for conn in self.connections:
                up_idx = conn['upstream']
                down_idx = conn['downstream']
                delay = conn['travel_time']
                
                if t >= delay:
                    upstream_outflow = results[self.reservoirs[up_idx]['name']]['outflow'][t - delay]
                    total_inflows[down_idx] += upstream_outflow
            
            # 各水库调度
            for i, res_info in enumerate(self.reservoirs):
                reservoir = res_info['reservoir']
                name = res_info['name']
                
                current_level = results[name]['level'][t]
                current_storage = results[name]['storage'][t]
                current_inflow = total_inflows[i]
                
                results[name]['inflow'][t] = current_inflow
                
                # 调度决策
                state = {
                    'level': current_level,
                    'storage': current_storage,
                    'zone': reservoir.get_zone(current_level)
                }
                
                outflow = reservoir._select_and_apply_rule(state, current_inflow, t)
                outflow = np.clip(outflow, 0, reservoir.characteristics['max_outflow'])
                results[name]['outflow'][t] = outflow
                
                # 水量平衡
                delta_storage = (current_inflow - outflow) * dt / 1e4
                new_storage = current_storage + delta_storage
                new_storage = np.clip(
                    new_storage,
                    reservoir.characteristics['dead_storage'],
                    reservoir.characteristics['total_storage']
                )
                
                results[name]['storage'][t + 1] = new_storage
                results[name]['level'][t + 1] = reservoir._storage_to_level(new_storage)
        
        # 最后一步
        for res_info in self.reservoirs:
            name = res_info['name']
            results[name]['outflow'][-1] = results[name]['outflow'][-2]
            results[name]['inflow'][-1] = results[name]['inflow'][-2]
        
        return results


def create_cascade_system():
    """创建梯级水库系统"""
    system = CascadeReservoirSystem()
    
    # 上游水库（大型）
    res1 = ReservoirRules()
    res1.set_characteristics(
        dead_level=100.0,
        normal_level=115.0,
        flood_limit_level=120.0,
        design_flood_level=125.0,
        max_level=130.0,
        dead_storage=2000.0,
        total_storage=15000.0,
        max_outflow=800.0
    )
    res1.add_rule(FloodControlRule(120.0, 125.0, 800.0))
    res1.add_rule(ConservationRule(115.0, 100.0, 30.0, 100.0))
    system.add_reservoir(res1, "上游水库")
    
    # 中游水库（中型）
    res2 = ReservoirRules()
    res2.set_characteristics(
        dead_level=80.0,
        normal_level=92.0,
        flood_limit_level=96.0,
        design_flood_level=100.0,
        max_level=104.0,
        dead_storage=800.0,
        total_storage=8000.0,
        max_outflow=600.0
    )
    res2.add_rule(FloodControlRule(96.0, 100.0, 600.0))
    res2.add_rule(ConservationRule(92.0, 80.0, 20.0, 80.0))
    system.add_reservoir(res2, "中游水库")
    
    # 下游水库（小型）
    res3 = ReservoirRules()
    res3.set_characteristics(
        dead_level=60.0,
        normal_level=70.0,
        flood_limit_level=73.0,
        design_flood_level=76.0,
        max_level=80.0,
        dead_storage=300.0,
        total_storage=4000.0,
        max_outflow=400.0
    )
    res3.add_rule(FloodControlRule(73.0, 76.0, 400.0))
    res3.add_rule(ConservationRule(70.0, 60.0, 10.0, 60.0))
    system.add_reservoir(res3, "下游水库")
    
    # 建立连接关系
    system.connect(0, 1, travel_time=1)  # 上游→中游，1天
    system.connect(1, 2, travel_time=1)  # 中游→下游，1天
    
    return system


def run_cascade_operation():
    """运行梯级联合调度"""
    print("\n" + "="*70)
    print("案例20：多水库梯级联合调度")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 创建梯级系统
    print("1. 创建梯级水库系统...")
    system = create_cascade_system()
    
    print(f"   水库数量: {len(system.reservoirs)}")
    for res_info in system.reservoirs:
        print(f"   - {res_info['name']}: "
              f"总库容 {res_info['reservoir'].characteristics['total_storage']:.0f} 万m³")
    print()
    
    # 2. 生成区间入流
    print("2. 生成各水库区间入流...")
    n_days = 180
    
    # 上游区间入流（最大）
    inflow1 = np.ones(n_days) * 80.0
    inflow1 += 40.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    # 添加洪峰
    flood_days = [50, 100, 140]
    for day in flood_days:
        for i in range(15):
            if day + i < n_days:
                inflow1[day + i] += 300 * np.exp(-((i - 7.5) / 3)**2)
    
    # 中游区间入流（中等）
    inflow2 = np.ones(n_days) * 50.0
    inflow2 += 20.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    for day in flood_days:
        for i in range(15):
            if day + i < n_days:
                inflow2[day + i] += 150 * np.exp(-((i - 7.5) / 3)**2)
    
    # 下游区间入流（较小）
    inflow3 = np.ones(n_days) * 30.0
    inflow3 += 10.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    for day in flood_days:
        for i in range(15):
            if day + i < n_days:
                inflow3[day + i] += 80 * np.exp(-((i - 7.5) / 3)**2)
    
    lateral_inflows = [inflow1, inflow2, inflow3]
    
    print(f"   时间步数: {n_days} 天")
    print(f"   上游最大区间入流: {np.max(inflow1):.0f} m³/s")
    print(f"   中游最大区间入流: {np.max(inflow2):.0f} m³/s")
    print(f"   下游最大区间入流: {np.max(inflow3):.0f} m³/s\n")
    
    # 3. 运行联合调度
    print("3. 运行梯级联合调度...")
    initial_levels = [115.0, 92.0, 70.0]  # 各水库初始水位
    
    results = system.operate(initial_levels, lateral_inflows)
    
    print("   调度完成\n")
    
    # 4. 统计分析
    print("="*70)
    print("梯级联合调度结果统计")
    print("="*70)
    
    for res_info in system.reservoirs:
        name = res_info['name']
        res_data = results[name]
        
        print(f"\n【{name}】")
        print(f"  最高水位: {np.max(res_data['level']):.2f} m")
        print(f"  最低水位: {np.min(res_data['level']):.2f} m")
        print(f"  平均入流: {np.mean(res_data['inflow']):.1f} m³/s")
        print(f"  最大入流: {np.max(res_data['inflow']):.1f} m³/s")
        print(f"  平均出流: {np.mean(res_data['outflow']):.1f} m³/s")
        print(f"  最大出流: {np.max(res_data['outflow']):.1f} m³/s")
        
        # 削峰效果
        peak_reduction = (np.max(res_data['inflow']) - np.max(res_data['outflow'])) / \
                        np.max(res_data['inflow']) * 100
        print(f"  削峰率: {peak_reduction:.1f}%")
    
    # 系统效益
    print(f"\n【系统总体效益】")
    total_storage_capacity = sum([res_info['reservoir'].characteristics['total_storage'] 
                                  for res_info in system.reservoirs])
    print(f"  梯级总库容: {total_storage_capacity:.0f} 万m³")
    
    # 下游出流（系统最终出流）
    final_outflow = results["下游水库"]['outflow']
    total_lateral = sum([np.mean(inflow) for inflow in lateral_inflows])
    print(f"  区间平均入流总和: {total_lateral:.1f} m³/s")
    print(f"  系统平均出流: {np.mean(final_outflow):.1f} m³/s")
    print(f"  系统最大出流: {np.max(final_outflow):.1f} m³/s")
    
    # 5. 可视化
    print(f"\n4. 生成可视化...")
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
    
    time = np.arange(n_days)
    colors = ['blue', 'green', 'red']
    
    # 图1：各水库入流过程
    ax1 = fig.add_subplot(gs[0, 0])
    for i, res_info in enumerate(system.reservoirs):
        name = res_info['name']
        ax1.plot(time, results[name]['inflow'], 
                color=colors[i], linewidth=2, label=name)
    
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('入流 (m³/s)', fontsize=10)
    ax1.set_title('各水库入流过程', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2：各水库出流过程
    ax2 = fig.add_subplot(gs[0, 1])
    for i, res_info in enumerate(system.reservoirs):
        name = res_info['name']
        ax2.plot(time, results[name]['outflow'], 
                color=colors[i], linewidth=2, label=name)
    
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('出流 (m³/s)', fontsize=10)
    ax2.set_title('各水库出流过程', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 图3：各水库水位过程
    ax3 = fig.add_subplot(gs[1, 0])
    for i, res_info in enumerate(system.reservoirs):
        name = res_info['name']
        reservoir = res_info['reservoir']
        
        ax3.plot(time, results[name]['level'], 
                color=colors[i], linewidth=2, label=name)
        
        # 添加防洪限制水位线
        flood_limit = reservoir.characteristics['flood_limit_level']
        ax3.axhline(y=flood_limit, color=colors[i], linestyle='--', 
                   linewidth=1, alpha=0.5)
    
    ax3.set_xlabel('时间 (天)', fontsize=11)
    ax3.set_ylabel('水位 (m)', fontsize=10)
    ax3.set_title('各水库水位过程', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 图4：各水库库容过程
    ax4 = fig.add_subplot(gs[1, 1])
    for i, res_info in enumerate(system.reservoirs):
        name = res_info['name']
        ax4.plot(time, results[name]['storage'], 
                color=colors[i], linewidth=2, label=name)
    
    ax4.set_xlabel('时间 (天)', fontsize=11)
    ax4.set_ylabel('库容 (万m³)', fontsize=10)
    ax4.set_title('各水库库容过程', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # 图5：削峰效果对比
    ax5 = fig.add_subplot(gs[2, 0])
    reservoir_names = [res_info['name'] for res_info in system.reservoirs]
    peak_inflows = [np.max(results[name]['inflow']) for name in reservoir_names]
    peak_outflows = [np.max(results[name]['outflow']) for name in reservoir_names]
    
    x_pos = np.arange(len(reservoir_names))
    width = 0.35
    
    ax5.bar(x_pos - width/2, peak_inflows, width, 
           label='峰值入流', color='blue', alpha=0.7)
    ax5.bar(x_pos + width/2, peak_outflows, width, 
           label='峰值出流', color='red', alpha=0.7)
    
    ax5.set_xlabel('水库', fontsize=11)
    ax5.set_ylabel('流量 (m³/s)', fontsize=10)
    ax5.set_title('削峰效果对比', fontsize=12, fontweight='bold')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(reservoir_names)
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 添加削峰率
    for i, (inf, outf) in enumerate(zip(peak_inflows, peak_outflows)):
        reduction = (inf - outf) / inf * 100
        ax5.text(i, max(inf, outf) + 30, f'-{reduction:.0f}%',
                ha='center', fontsize=9, fontweight='bold')
    
    # 图6：梯级补偿效果
    ax6 = fig.add_subplot(gs[2, 1])
    
    # 对比系统入流与出流
    total_system_inflow = sum([results[res_info['name']]['inflow'] 
                              for res_info in system.reservoirs])
    system_outflow = results["下游水库"]['outflow']
    
    ax6.fill_between(time, 0, total_system_inflow, alpha=0.3, 
                    color='blue', label='系统总入流')
    ax6.plot(time, total_system_inflow, 'b-', linewidth=1, alpha=0.7)
    ax6.plot(time, system_outflow, 'r-', linewidth=2, label='系统出流')
    
    ax6.set_xlabel('时间 (天)', fontsize=11)
    ax6.set_ylabel('流量 (m³/s)', fontsize=10)
    ax6.set_title('梯级系统补偿调节效果', fontsize=12, fontweight='bold')
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3)
    
    plt.savefig(f'{output_dir}/cascade_operation.png', 
                dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/cascade_operation.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_cascade_operation()
