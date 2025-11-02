"""
案例8：非点源污染模拟
Non-Point Source Pollution Simulation

演示：
1. SCS-CN径流计算
2. EMC污染负荷估算
3. 河流水质模拟（分布式源项）
4. 初期冲刷分析
5. 管理方案制定
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.nonpoint_source import (SCSCurveNumber, EventMeanConcentration,
                                    NonPointSourceRiver1D,
                                    calculate_first_flush_factor,
                                    calculate_buildup_washoff)


def main():
    """主函数"""
    print("=" * 70)
    print("案例8：非点源污染模拟")
    print("=" * 70)
    print()
    
    # ========================================
    # 参数设置
    # ========================================
    print("流域参数设置")
    print("-" * 70)
    
    # 降雨参数
    P = 50.0  # 降雨量 (mm)
    I = 10.0  # 降雨强度 (mm/hr)
    duration = 5.0  # 持续时间 (hour)
    days_since_rain = 7  # 距上次降雨天数
    
    print(f"降雨参数:")
    print(f"  降雨量 P = {P} mm")
    print(f"  降雨强度 I = {I} mm/hr")
    print(f"  持续时间 = {duration} hour")
    print(f"  距上次降雨 = {days_since_rain} days")
    print()
    
    # 土地利用
    landuses = {
        'agricultural': {'area': 30, 'CN': 78, 'EMC_COD': 80},
        'urban': {'area': 15, 'CN': 85, 'EMC_COD': 90},
        'forest': {'area': 25, 'CN': 55, 'EMC_COD': 30},
    }
    
    print(f"土地利用:")
    print(f"  农田: {landuses['agricultural']['area']} km², CN={landuses['agricultural']['CN']}")
    print(f"  城市: {landuses['urban']['area']} km², CN={landuses['urban']['CN']}")
    print(f"  森林: {landuses['forest']['area']} km², CN={landuses['forest']['CN']}")
    print()
    
    # 河流参数
    L_river = 15000  # 河段长度 (m)
    Q_river = 30.0   # 河流流量 (m³/s)
    u = 0.6          # 流速 (m/s)
    D = 4.0          # 扩散系数 (m²/s)
    k = 0.18 / 86400  # COD降解系数 (1/s)
    C0 = 8.0         # 上游本底COD (mg/L)
    C_standard = 20.0  # III类水标准 (mg/L)
    
    print(f"河流参数:")
    print(f"  河段长度 = {L_river/1000} km")
    print(f"  河流流量 = {Q_river} m³/s")
    print(f"  流速 = {u} m/s")
    print(f"  本底COD = {C0} mg/L")
    print(f"  水质标准 = {C_standard} mg/L")
    print()
    
    # ========================================
    # 任务1：SCS-CN径流计算
    # ========================================
    print("任务1：SCS-CN径流计算")
    print("-" * 70)
    
    runoff_results = {}
    
    for name, params in landuses.items():
        print(f"\n{name}:")
        
        # 创建SCS-CN模型
        scs = SCSCurveNumber(CN=params['CN'], area=params['area'])
        
        # 计算径流
        Q_runoff, alpha = scs.calculate_runoff(P)
        V_runoff = scs.calculate_runoff_volume(P)
        
        print(f"  径流深 Q = {Q_runoff:.1f} mm")
        print(f"  径流系数 α = {alpha:.1%}")
        print(f"  径流量 V = {V_runoff:.0f} m³")
        
        runoff_results[name] = {
            'Q': Q_runoff,
            'alpha': alpha,
            'V': V_runoff
        }
    
    print()
    
    # 总径流量
    total_V = sum(r['V'] for r in runoff_results.values())
    print(f"总径流量: {total_V:.0f} m³")
    print()
    
    # ========================================
    # 任务2：EMC污染负荷估算
    # ========================================
    print("任务2：EMC污染负荷估算")
    print("-" * 70)
    
    load_results = {}
    
    for name, params in landuses.items():
        print(f"\n{name}:")
        
        # 创建EMC模型
        emc_model = EventMeanConcentration({'COD': params['EMC_COD']})
        
        # 计算负荷
        loads = emc_model.calculate_load(runoff_results[name]['V'])
        
        print(f"  COD负荷 = {loads['COD']:.1f} kg")
        
        load_results[name] = loads['COD']
    
    # 总负荷
    total_load = sum(load_results.values())
    print(f"\n总COD负荷: {total_load:.1f} kg")
    print()
    
    # 各源贡献率
    print("污染贡献率:")
    for name, load in load_results.items():
        contribution = load / total_load * 100
        print(f"  {name}: {contribution:.1f}%")
    print()
    
    # ========================================
    # 任务3：河流水质模拟
    # ========================================
    print("任务3：河流水质模拟（分布式源项）")
    print("-" * 70)
    
    # 创建河流模型
    model = NonPointSourceRiver1D(L_river, 300, u, D, k, Q_river, C0)
    
    # 添加分布式源项（简化：均匀分布）
    # 农田：0-5km
    load_rate_agri = load_results['agricultural'] / 5000  # kg/m/day
    model.add_distributed_source(0, 5000, load_rate_agri)
    
    # 城市：5-10km
    load_rate_urban = load_results['urban'] / 5000  # kg/m/day
    model.add_distributed_source(5000, 10000, load_rate_urban)
    
    # 森林：10-15km
    load_rate_forest = load_results['forest'] / 5000  # kg/m/day
    model.add_distributed_source(10000, 15000, load_rate_forest)
    
    # 求解
    x, C = model.solve()
    
    # 识别超标河段
    exceed_mask = C > C_standard
    if np.any(exceed_mask):
        exceed_x = x[exceed_mask]
        print(f"\n超标河段:")
        print(f"  起点: {exceed_x[0]/1000:.2f} km")
        print(f"  终点: {exceed_x[-1]/1000:.2f} km")
        print(f"  长度: {(exceed_x[-1] - exceed_x[0])/1000:.2f} km")
        print(f"  最大浓度: {np.max(C[exceed_mask]):.1f} mg/L")
    else:
        print("\n✓ 全河段达标")
    print()
    
    # ========================================
    # 任务4：初期冲刷分析
    # ========================================
    print("任务4：初期冲刷分析")
    print("-" * 70)
    
    # 计算初期冲刷系数
    ff_factor = calculate_first_flush_factor(duration)
    
    # 计算累积-冲刷系数
    washoff_factor = calculate_buildup_washoff(days_since_rain, I)
    
    # 考虑初期冲刷的负荷重新分配
    print(f"\n考虑初期冲刷效应:")
    print(f"  初期30%时间内负荷: {total_load * 0.7:.1f} kg ({0.7/0.3*100:.0f}%强度)")
    print(f"  后期70%时间内负荷: {total_load * 0.3:.1f} kg ({0.3/0.7*100:.0f}%强度)")
    print()
    
    # ========================================
    # 任务5：管理方案
    # ========================================
    print("任务5：面源污染管理方案")
    print("-" * 70)
    
    # 关键源区识别
    print("\n关键源区识别（按贡献率）:")
    sorted_sources = sorted(load_results.items(), key=lambda x: x[1], reverse=True)
    for i, (name, load) in enumerate(sorted_sources, 1):
        contribution = load / total_load * 100
        print(f"  {i}. {name}: {load:.1f} kg ({contribution:.1f}%)")
    
    # 削减潜力
    print("\nBMP削减潜力估算:")
    bmp_efficiency = {
        'agricultural': 0.30,  # 植被缓冲带、测土配方施肥
        'urban': 0.40,          # 雨水花园、透水铺装
        'forest': 0.10,         # 自然林地削减潜力小
    }
    
    total_reduction = 0
    for name, efficiency in bmp_efficiency.items():
        reduction = load_results[name] * efficiency
        total_reduction += reduction
        print(f"  {name}: 削减{efficiency*100:.0f}% → {reduction:.1f} kg")
    
    print(f"\n总削减潜力: {total_reduction:.1f} kg ({total_reduction/total_load*100:.1f}%)")
    
    # 削减后负荷
    reduced_load = total_load - total_reduction
    print(f"削减后总负荷: {reduced_load:.1f} kg")
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 图1：径流和负荷对比
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 径流量对比
    names = list(runoff_results.keys())
    V_values = [runoff_results[name]['V'] for name in names]
    alpha_values = [runoff_results[name]['alpha'] for name in names]
    
    bars1 = ax1.bar(names, V_values, color=['green', 'red', 'lightgreen'],
                    edgecolor='black', linewidth=1.5, alpha=0.7)
    
    # 添加径流系数标签
    for bar, alpha in zip(bars1, alpha_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f} m³\n(α={alpha:.1%})',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax1.set_ylabel('径流量 (m³)', fontsize=11)
    ax1.set_title('不同土地利用径流量对比', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 污染负荷对比
    load_values = [load_results[name] for name in names]
    
    bars2 = ax2.bar(names, load_values, color=['orange', 'red', 'lightblue'],
                    edgecolor='black', linewidth=1.5, alpha=0.7)
    
    for bar, load in zip(bars2, load_values):
        height = bar.get_height()
        contribution = load / total_load * 100
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{load:.0f} kg\n({contribution:.0f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax2.set_ylabel('COD负荷 (kg)', fontsize=11)
    ax2.set_title('不同土地利用污染负荷对比', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('runoff_and_load.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: runoff_and_load.png")
    
    # 图2：河流水质分布
    fig2, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(x/1000, C, 'b-', linewidth=2.5, label='COD浓度')
    ax.axhline(y=C_standard, color='red', linestyle='--', linewidth=2,
               label=f'III类水标准 ({C_standard} mg/L)')
    
    # 填充超标区域
    if np.any(exceed_mask):
        ax.fill_between(x/1000, C, C_standard,
                        where=exceed_mask, alpha=0.3, color='red',
                        label='超标区域')
    
    # 标注土地利用分区
    ax.axvspan(0, 5, alpha=0.1, color='green', label='农田区')
    ax.axvspan(5, 10, alpha=0.1, color='gray', label='城市区')
    ax.axvspan(10, 15, alpha=0.1, color='lightgreen', label='森林区')
    
    ax.set_xlabel('距离 (km)', fontsize=11)
    ax.set_ylabel('COD浓度 (mg/L)', fontsize=11)
    ax.set_title('非点源影响下的河流COD浓度分布', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('river_water_quality.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: river_water_quality.png")
    
    # 图3：初期冲刷过程
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    # 模拟浓度时间过程（简化）
    t = np.linspace(0, duration, 100)
    
    # 初期冲刷模型（指数衰减）
    C_avg = total_load / total_V  # 平均浓度
    C_t = C_avg * ff_factor * np.exp(-2 * t / duration) + C_avg * (1 - np.exp(-2 * t / duration)) / ff_factor
    
    ax.plot(t, C_t, 'r-', linewidth=2.5, label='径流COD浓度')
    ax.axhline(y=C_avg, color='blue', linestyle='--', linewidth=2,
               label=f'平均浓度 ({C_avg:.1f} mg/L)')
    
    # 标注初期冲刷阶段
    t_initial = duration * 0.3
    ax.axvspan(0, t_initial, alpha=0.2, color='red', label='初期冲刷期（30%时间）')
    
    ax.set_xlabel('时间 (hour)', fontsize=11)
    ax.set_ylabel('COD浓度 (mg/L)', fontsize=11)
    ax.set_title('降雨径流COD浓度时间过程（初期冲刷效应）', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('first_flush.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: first_flush.png")
    
    # 图4：BMP削减方案
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    names_sorted = [name for name, _ in sorted_sources]
    current_loads = [load_results[name] for name in names_sorted]
    reduced_loads = [load_results[name] * (1 - bmp_efficiency[name]) for name in names_sorted]
    
    x_pos = np.arange(len(names_sorted))
    width = 0.35
    
    bars1 = ax.bar(x_pos - width/2, current_loads, width,
                   label='当前负荷', color='red', alpha=0.7, edgecolor='black')
    bars2 = ax.bar(x_pos + width/2, reduced_loads, width,
                   label='削减后负荷', color='green', alpha=0.7, edgecolor='black')
    
    # 添加数值和削减比例标签
    for i, name in enumerate(names_sorted):
        reduction_pct = bmp_efficiency[name] * 100
        reduction_kg = current_loads[i] - reduced_loads[i]
        
        ax.text(i, max(current_loads[i], reduced_loads[i]) + 20,
                f'削减{reduction_pct:.0f}%\n({reduction_kg:.0f} kg)',
                ha='center', va='bottom', fontsize=9, color='red', fontweight='bold')
    
    ax.set_ylabel('COD负荷 (kg)', fontsize=11)
    ax.set_title('BMP措施削减方案', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names_sorted)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('bmp_reduction.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: bmp_reduction.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例8完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print(f"1. 总径流量: {total_V:.0f} m³")
    print(f"2. 总COD负荷: {total_load:.1f} kg")
    print(f"3. 关键源区: {sorted_sources[0][0]} ({sorted_sources[0][1]/total_load*100:.1f}%)")
    print(f"4. 河流最大浓度: {np.max(C):.1f} mg/L")
    if np.any(exceed_mask):
        print(f"5. 超标河段长度: {(exceed_x[-1] - exceed_x[0])/1000:.2f} km")
    print(f"6. BMP削减潜力: {total_reduction/total_load*100:.1f}%")
    print()
    print("管理建议:")
    print("  1. 重点控制农田面源（贡献最大）")
    print("  2. 实施植被缓冲带、测土配方施肥")
    print("  3. 城市区建设雨水花园、透水铺装")
    print("  4. 初期雨水截流，减少峰值冲击")
    print("  5. 建立降雨-水质监测预警系统")
    print()
    print("生成的图表:")
    print("  - runoff_and_load.png      (径流和负荷对比)")
    print("  - river_water_quality.png  (河流水质分布)")
    print("  - first_flush.png          (初期冲刷过程)")
    print("  - bmp_reduction.png        (BMP削减方案)")
    print()
    
    plt.show()


if __name__ == '__main__':
    # 设置matplotlib后端
    import matplotlib
    matplotlib.use('Agg')
    
    main()
