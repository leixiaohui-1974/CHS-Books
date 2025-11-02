"""
案例17：水库优化调度（基于规则）
==============================

演示基于规则的水库优化调度方法，
包括防洪调度、兴利调度等多目标优化。

核心内容：
1. 水库特征参数设置
2. 调度规则设计
3. 水位-库容关系
4. 多情景调度模拟
5. 调度效果评估

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


def run_reservoir_operation():
    """运行水库调度"""
    print("\n" + "="*70)
    print("案例17：水库优化调度（基于规则）")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 设置水库特征
    print("1. 设置水库特征参数...")
    reservoir = ReservoirRules()
    reservoir.set_characteristics(
        dead_level=95.0,        # 死水位 (m)
        normal_level=108.0,     # 正常蓄水位 (m)
        flood_limit_level=113.0, # 防洪限制水位 (m)
        design_flood_level=118.0, # 设计洪水位 (m)
        max_level=122.0,        # 校核洪水位 (m)
        dead_storage=500.0,     # 死库容 (万m³)
        total_storage=8000.0,   # 总库容 (万m³)
        max_outflow=600.0       # 最大泄流能力 (m³/s)
    )
    
    print(f"   死水位: {reservoir.characteristics['dead_level']:.1f} m")
    print(f"   正常蓄水位: {reservoir.characteristics['normal_level']:.1f} m")
    print(f"   防洪限制水位: {reservoir.characteristics['flood_limit_level']:.1f} m")
    print(f"   总库容: {reservoir.characteristics['total_storage']:.0f} 万m³")
    print(f"   最大泄流: {reservoir.characteristics['max_outflow']:.0f} m³/s\n")
    
    # 2. 添加调度规则
    print("2. 添加调度规则...")
    
    # 防洪规则
    flood_rule = FloodControlRule(
        flood_limit_level=113.0,
        design_flood_level=118.0,
        max_outflow=600.0
    )
    reservoir.add_rule(flood_rule)
    print("   ✓ 防洪调度规则")
    
    # 兴利规则
    conservation_rule = ConservationRule(
        normal_level=108.0,
        dead_level=95.0,
        min_outflow=20.0,
        target_outflow=80.0
    )
    reservoir.add_rule(conservation_rule)
    print("   ✓ 兴利调度规则\n")
    
    # 3. 生成入库流量
    print("3. 生成入库流量过程...")
    n_days = 180  # 半年
    
    # 基流
    inflow = np.ones(n_days) * 60.0
    
    # 添加季节性变化
    inflow += 30.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    
    # 添加3次洪峰
    flood_days = [45, 90, 135]
    for day in flood_days:
        duration = 15
        peak = 400.0 + np.random.rand() * 100.0
        for i in range(duration):
            if day + i < n_days:
                ratio = np.exp(-((i - duration/2) / (duration/4))**2)
                inflow[day + i] += peak * ratio
    
    print(f"   时间步数: {n_days} 天")
    print(f"   平均入流: {np.mean(inflow):.1f} m³/s")
    print(f"   最大入流: {np.max(inflow):.1f} m³/s\n")
    
    # 4. 运行调度
    print("4. 运行水库调度...")
    initial_level = 108.0  # 从正常蓄水位开始
    
    results = reservoir.operate(
        initial_level=initial_level,
        inflow_series=inflow,
        dt=86400.0  # 1天
    )
    
    print("   调度完成\n")
    
    # 5. 统计分析
    print("="*70)
    print("水库调度结果统计")
    print("="*70)
    
    levels = results['level']
    storages = results['storage']
    outflows = results['outflow']
    zones = results['zone']
    
    print(f"\n【水位变化】")
    print(f"  初始水位: {levels[0]:.2f} m")
    print(f"  最高水位: {np.max(levels):.2f} m")
    print(f"  最低水位: {np.min(levels):.2f} m")
    print(f"  平均水位: {np.mean(levels):.2f} m")
    
    print(f"\n【库容变化】")
    print(f"  初始库容: {storages[0]:.0f} 万m³")
    print(f"  最大库容: {np.max(storages):.0f} 万m³")
    print(f"  最小库容: {np.min(storages):.0f} 万m³")
    print(f"  库容利用率: {(np.mean(storages) / reservoir.characteristics['total_storage'] * 100):.1f}%")
    
    print(f"\n【出流过程】")
    print(f"  平均出流: {np.mean(outflows):.1f} m³/s")
    print(f"  最大出流: {np.max(outflows):.1f} m³/s")
    print(f"  削峰率: {((np.max(inflow) - np.max(outflows)) / np.max(inflow) * 100):.1f}%")
    
    # 统计各分区天数
    zone_names = {1: '死库容', 2: '兴利库容', 3: '限制水位', 
                  4: '防洪库容', 5: '设计洪水'}
    print(f"\n【分区统计】")
    for zone_id in [2, 3, 4]:
        days = np.sum(zones == zone_id)
        print(f"  {zone_names[zone_id]}: {days} 天 ({days/n_days*100:.1f}%)")
    
    # 6. 可视化
    print(f"\n5. 生成可视化...")
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    time = np.arange(n_days)
    
    # 图1：入库流量与出库流量
    ax1 = fig.add_subplot(gs[0, :])
    ax1.fill_between(time, 0, inflow, alpha=0.3, color='blue', label='入库流量')
    ax1.plot(time, inflow, 'b-', linewidth=1.5, alpha=0.7)
    ax1.plot(time, outflows, 'r-', linewidth=2, label='出库流量')
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('流量 (m³/s)', fontsize=10)
    ax1.set_title('【水库调度】入库与出库流量过程', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2：水位过程
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(time, levels, 'b-', linewidth=2)
    
    # 添加特征水位线
    ax2.axhline(y=reservoir.characteristics['normal_level'], 
               color='green', linestyle='--', linewidth=1.5, label='正常蓄水位')
    ax2.axhline(y=reservoir.characteristics['flood_limit_level'], 
               color='orange', linestyle='--', linewidth=1.5, label='防洪限制水位')
    ax2.axhline(y=reservoir.characteristics['design_flood_level'], 
               color='red', linestyle='--', linewidth=1.5, label='设计洪水位')
    
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('水位 (m)', fontsize=10)
    ax2.set_title('水位变化过程', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3：库容过程
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.fill_between(time, 0, storages, alpha=0.5, color='blue')
    ax3.plot(time, storages, 'b-', linewidth=2)
    ax3.set_xlabel('时间 (天)', fontsize=11)
    ax3.set_ylabel('库容 (万m³)', fontsize=10)
    ax3.set_title('库容变化过程', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 图4：分区统计
    ax4 = fig.add_subplot(gs[2, 0])
    zone_counts = []
    zone_labels = []
    colors = ['green', 'yellow', 'orange']
    
    for zone_id in [2, 3, 4]:
        count = np.sum(zones == zone_id)
        if count > 0:
            zone_counts.append(count)
            zone_labels.append(zone_names[zone_id])
    
    ax4.pie(zone_counts, labels=zone_labels, colors=colors, autopct='%1.1f%%',
           startangle=90, textprops={'fontsize': 10})
    ax4.set_title('水库分区运行时间占比', fontsize=12, fontweight='bold')
    
    # 图5：削峰效果
    ax5 = fig.add_subplot(gs[2, 1])
    
    # 找到洪峰
    peak_indices = []
    for day in flood_days:
        peak_idx = day + np.argmax(inflow[day:min(day+20, n_days)])
        if peak_idx < n_days:
            peak_indices.append(peak_idx)
    
    # 绘制洪峰对比
    x_pos = np.arange(len(peak_indices))
    width = 0.35
    
    inflow_peaks = [inflow[idx] for idx in peak_indices]
    outflow_peaks = [outflows[idx] for idx in peak_indices]
    
    ax5.bar(x_pos - width/2, inflow_peaks, width, label='入库洪峰', color='blue', alpha=0.7)
    ax5.bar(x_pos + width/2, outflow_peaks, width, label='出库洪峰', color='red', alpha=0.7)
    
    ax5.set_xlabel('洪峰编号', fontsize=11)
    ax5.set_ylabel('流量 (m³/s)', fontsize=10)
    ax5.set_title('削峰效果对比', fontsize=12, fontweight='bold')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels([f'#{i+1}' for i in range(len(peak_indices))])
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 添加削峰率标签
    for i, (inf, outf) in enumerate(zip(inflow_peaks, outflow_peaks)):
        reduction = (inf - outf) / inf * 100
        ax5.text(i, max(inf, outf) + 20, f'-{reduction:.0f}%', 
                ha='center', fontsize=9, fontweight='bold')
    
    plt.savefig(f'{output_dir}/reservoir_operation.png', dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/reservoir_operation.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_reservoir_operation()
