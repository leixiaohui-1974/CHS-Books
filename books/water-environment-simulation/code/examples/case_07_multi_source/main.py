"""
案例7：多点源污染叠加模拟
Multi-Source Pollution Superposition Simulation

演示：
1. 单点源水质模拟
2. 多点源叠加效应
3. 达标距离计算
4. 排放方案优化
5. 敏感性分析
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.multi_source import MultiSourceRiver1D, calculate_superposition_factor


def main():
    """主函数"""
    print("=" * 70)
    print("案例7：多点源污染叠加模拟")
    print("=" * 70)
    print()
    
    # ========================================
    # 河流和排放参数设置
    # ========================================
    print("河流参数设置")
    print("-" * 70)
    
    # 河流参数
    L = 20000           # 河段长度 (m)
    nx = 500            # 空间节点数
    u = 0.8             # 流速 (m/s)
    D = 5.0             # 扩散系数 (m²/s)
    k = 0.15 / 86400    # COD降解系数 (1/s, 从day⁻¹转换)
    Q_river = 50.0      # 河流流量 (m³/s)
    C0 = 5.0            # 上游本底COD (mg/L)
    C_standard = 20.0   # III类水标准 (mg/L)
    
    print(f"河段长度 L = {L/1000} km")
    print(f"流速 u = {u} m/s")
    print(f"扩散系数 D = {D} m²/s")
    print(f"降解系数 k = {k*86400:.2f} day⁻¹")
    print(f"河流流量 Q = {Q_river} m³/s")
    print(f"上游本底 C0 = {C0} mg/L")
    print(f"水质标准 = {C_standard} mg/L (III类)")
    print()
    
    # 点源信息
    sources_info = [
        {"name": "化工厂", "x": 2000, "Q": 0.5, "C": 150},
        {"name": "印染厂", "x": 5000, "Q": 0.3, "C": 120},
        {"name": "造纸厂", "x": 8000, "Q": 0.4, "C": 100},
        {"name": "污水厂", "x": 12000, "Q": 2.0, "C": 50},
    ]
    
    print("点源排放情况:")
    print(f"{'点源':<10} {'位置(km)':<10} {'流量(m³/s)':<12} {'COD(mg/L)':<12}")
    print("-" * 50)
    for source in sources_info:
        print(f"{source['name']:<10} {source['x']/1000:<10.1f} {source['Q']:<12.1f} {source['C']:<12.0f}")
    print()
    
    # ========================================
    # 任务1：单点源水质模拟
    # ========================================
    print("任务1：单点源水质模拟（仅化工厂）")
    print("-" * 70)
    
    # 创建单点源模型
    model_single = MultiSourceRiver1D(L, nx, u, D, k, Q_river, C0)
    
    # 添加第一个点源
    source1 = sources_info[0]
    model_single.add_source(source1['x'], source1['Q'], source1['C'], source1['name'])
    
    # 求解
    x_single, C_single = model_single.solve()
    
    # 计算达标距离
    dist_single = model_single.calculate_compliance_distance(C_standard, source_idx=0)
    
    print()
    
    # ========================================
    # 任务2：多点源叠加模拟
    # ========================================
    print("任务2：多点源叠加模拟（所有点源）")
    print("-" * 70)
    
    # 创建多点源模型
    model_multi = MultiSourceRiver1D(L, nx, u, D, k, Q_river, C0)
    
    # 添加所有点源
    for source in sources_info:
        model_multi.add_source(source['x'], source['Q'], source['C'], source['name'])
    
    # 求解
    x_multi, C_multi = model_multi.solve()
    
    # 计算最大浓度
    C_max, x_max = model_multi.calculate_max_concentration()
    
    print()
    
    # ========================================
    # 任务3：达标距离计算
    # ========================================
    print("任务3：达标距离计算")
    print("-" * 70)
    
    # 计算各点源下游达标距离
    compliance_distances = []
    for i in range(len(sources_info)):
        dist = model_multi.calculate_compliance_distance(C_standard, source_idx=i)
        compliance_distances.append(dist)
    
    print()
    
    # 识别超标河段
    print("超标河段识别:")
    exceed_mask = C_multi > C_standard
    if np.any(exceed_mask):
        exceed_x = x_multi[exceed_mask]
        print(f"  超标起点: x = {exceed_x[0]/1000:.2f} km")
        print(f"  超标终点: x = {exceed_x[-1]/1000:.2f} km")
        print(f"  超标长度: {(exceed_x[-1] - exceed_x[0])/1000:.2f} km")
    else:
        print("  ✓ 全河段达标！")
    print()
    
    # ========================================
    # 任务4：排放方案优化
    # ========================================
    print("任务4：排放方案优化")
    print("-" * 70)
    
    # 识别关键点源（污水厂，流量最大）
    critical_idx = 3
    C_waste_max = model_multi.optimize_discharge(C_standard, critical_idx)
    
    print()
    
    # ========================================
    # 任务5：敏感性分析
    # ========================================
    print("任务5：敏感性分析")
    print("-" * 70)
    
    # 参数变化范围
    Q_factors = [0.8, 0.9, 1.0, 1.1, 1.2]  # 河流流量变化
    k_factors = [0.7, 0.85, 1.0, 1.15, 1.3]  # 降解系数变化
    
    # 存储结果
    C_max_Q = []
    C_max_k = []
    
    print("\n流量敏感性分析:")
    for factor in Q_factors:
        Q_test = Q_river * factor
        model_test = MultiSourceRiver1D(L, nx, u, D, k, Q_test, C0)
        for source in sources_info:
            model_test.add_source(source['x'], source['Q'], source['C'], source['name'])
        _, C_test = model_test.solve()
        C_max_test = np.max(C_test)
        C_max_Q.append(C_max_test)
        print(f"  Q = {Q_test:.1f} m³/s ({factor*100:.0f}%): C_max = {C_max_test:.2f} mg/L")
    
    print("\n降解系数敏感性分析:")
    for factor in k_factors:
        k_test = k * factor
        model_test = MultiSourceRiver1D(L, nx, u, D, k_test, Q_river, C0)
        for source in sources_info:
            model_test.add_source(source['x'], source['Q'], source['C'], source['name'])
        _, C_test = model_test.solve()
        C_max_test = np.max(C_test)
        C_max_k.append(C_max_test)
        print(f"  k = {k_test*86400:.3f} day⁻¹ ({factor*100:.0f}%): C_max = {C_max_test:.2f} mg/L")
    
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 图1：单点源 vs 多点源对比
    fig1, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(x_single/1000, C_single, 'b-', linewidth=2, label='单点源（仅化工厂）')
    ax.plot(x_multi/1000, C_multi, 'r-', linewidth=2, label='多点源（4个点源）')
    
    # 标准线
    ax.axhline(y=C_standard, color='green', linestyle='--', linewidth=2, 
               label=f'III类水标准 ({C_standard} mg/L)')
    
    # 标注点源位置
    for source in sources_info:
        ax.axvline(x=source['x']/1000, color='gray', linestyle=':', alpha=0.5)
        ax.text(source['x']/1000, ax.get_ylim()[1]*0.95, source['name'], 
                rotation=90, va='top', ha='right', fontsize=9)
    
    ax.set_xlabel('距离 (km)', fontsize=12)
    ax.set_ylabel('COD浓度 (mg/L)', fontsize=12)
    ax.set_title('单点源 vs 多点源水质对比', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('single_vs_multi_source.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: single_vs_multi_source.png")
    
    # 图2：多点源叠加详细分析
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 子图1：浓度分布
    ax1.plot(x_multi/1000, C_multi, 'r-', linewidth=2.5, label='COD浓度')
    ax1.axhline(y=C_standard, color='green', linestyle='--', linewidth=2, 
                label=f'标准 ({C_standard} mg/L)')
    
    # 填充超标区域
    exceed_mask = C_multi > C_standard
    if np.any(exceed_mask):
        ax1.fill_between(x_multi/1000, C_multi, C_standard, 
                        where=exceed_mask, alpha=0.3, color='red', 
                        label='超标区域')
    
    # 标注点源
    for i, source in enumerate(sources_info):
        ax1.axvline(x=source['x']/1000, color='gray', linestyle=':', alpha=0.5)
        y_pos = C_multi[np.argmin(np.abs(x_multi - source['x']))]
        ax1.plot(source['x']/1000, y_pos, 'ko', markersize=8)
        ax1.annotate(f"{source['name']}\n{source['C']}mg/L", 
                    xy=(source['x']/1000, y_pos),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=9, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', color='black'))
    
    # 标注最大浓度点
    ax1.plot(x_max/1000, C_max, 'r*', markersize=20, 
            label=f'最大浓度点 ({C_max:.1f} mg/L)')
    
    ax1.set_xlabel('距离 (km)', fontsize=11)
    ax1.set_ylabel('COD浓度 (mg/L)', fontsize=11)
    ax1.set_title('多点源污染叠加分析', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # 子图2：达标距离
    source_names = [s['name'] for s in sources_info]
    compliance_km = [d/1000 if d is not None else 0 for d in compliance_distances]
    colors = ['green' if d is not None and d < 5000 else 'orange' if d is not None else 'red' 
              for d in compliance_distances]
    
    bars = ax2.barh(source_names, compliance_km, color=colors, 
                    edgecolor='black', linewidth=1.5, alpha=0.7)
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, compliance_km)):
        if val > 0:
            ax2.text(val + 0.2, i, f'{val:.2f} km', 
                    va='center', fontsize=10, fontweight='bold')
        else:
            ax2.text(0.2, i, '未达标', 
                    va='center', fontsize=10, fontweight='bold', color='red')
    
    ax2.set_xlabel('达标距离 (km)', fontsize=11)
    ax2.set_title('各点源下游达标距离', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('multi_source_analysis.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: multi_source_analysis.png")
    
    # 图3：敏感性分析
    fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 流量敏感性
    ax1.plot(Q_factors, C_max_Q, 'bo-', linewidth=2, markersize=8)
    ax1.axhline(y=C_standard, color='red', linestyle='--', linewidth=2, 
                label=f'标准 ({C_standard} mg/L)')
    ax1.axvline(x=1.0, color='gray', linestyle=':', alpha=0.5, label='基准情景')
    
    ax1.set_xlabel('河流流量变化倍数', fontsize=11)
    ax1.set_ylabel('最大COD浓度 (mg/L)', fontsize=11)
    ax1.set_title('流量敏感性分析', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 降解系数敏感性
    ax2.plot(k_factors, C_max_k, 'go-', linewidth=2, markersize=8)
    ax2.axhline(y=C_standard, color='red', linestyle='--', linewidth=2, 
                label=f'标准 ({C_standard} mg/L)')
    ax2.axvline(x=1.0, color='gray', linestyle=':', alpha=0.5, label='基准情景')
    
    ax2.set_xlabel('降解系数变化倍数', fontsize=11)
    ax2.set_ylabel('最大COD浓度 (mg/L)', fontsize=11)
    ax2.set_title('降解系数敏感性分析', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('sensitivity_analysis.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: sensitivity_analysis.png")
    
    # 图4：排放优化方案
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    source_names = [s['name'] for s in sources_info]
    current_conc = [s['C'] for s in sources_info]
    
    # 计算建议浓度（简化）
    reduction_factors = [0.7, 0.8, 1.0, 0.85]  # 各点源建议削减比例
    recommended_conc = [c * f for c, f in zip(current_conc, reduction_factors)]
    
    x_pos = np.arange(len(source_names))
    width = 0.35
    
    bars1 = ax.bar(x_pos - width/2, current_conc, width, 
                   label='当前排放浓度', color='red', alpha=0.7, edgecolor='black')
    bars2 = ax.bar(x_pos + width/2, recommended_conc, width, 
                   label='建议排放浓度', color='green', alpha=0.7, edgecolor='black')
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 添加削减比例标签
    for i, factor in enumerate(reduction_factors):
        reduction = (1 - factor) * 100
        if reduction > 0:
            ax.text(i, max(current_conc[i], recommended_conc[i]) + 10,
                    f'削减{reduction:.0f}%',
                    ha='center', va='bottom', fontsize=9, color='red', fontweight='bold')
    
    ax.set_ylabel('COD排放浓度 (mg/L)', fontsize=11)
    ax.set_title('排放浓度优化方案', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(source_names)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('optimization_scheme.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: optimization_scheme.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例7完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print(f"1. 单点源（化工厂）最大浓度: {np.max(C_single):.1f} mg/L")
    print(f"2. 多点源叠加最大浓度: {C_max:.1f} mg/L（位于{x_max/1000:.1f} km）")
    if np.max(C_single) > 0:
        print(f"3. 叠加效应倍数: {C_max/np.max(C_single):.2f}")
    
    if np.any(exceed_mask):
        print(f"4. 超标河段长度: {(exceed_x[-1] - exceed_x[0])/1000:.2f} km")
    else:
        print("4. ✓ 全河段达标")
    
    print(f"5. 流量敏感性: 流量增加20% → 浓度降低{(1-C_max_Q[-1]/C_max)*100:.1f}%")
    print(f"6. 降解敏感性: 降解增加30% → 浓度降低{(1-C_max_k[-1]/C_max)*100:.1f}%")
    print()
    print("管理建议:")
    print("  1. 化工厂和印染厂需削减排放浓度20-30%")
    print("  2. 污水厂虽浓度低但流量大，建议削减15%")
    print("  3. 加强污水处理厂下游0-2km河段监测")
    print("  4. 枯水期严格控制排放，确保稀释能力")
    print()
    print("生成的图表:")
    print("  - single_vs_multi_source.png    (单源vs多源对比)")
    print("  - multi_source_analysis.png     (多源叠加分析)")
    print("  - sensitivity_analysis.png      (敏感性分析)")
    print("  - optimization_scheme.png       (优化方案)")
    print()
    
    plt.show()


if __name__ == '__main__':
    # 设置matplotlib后端（避免显示窗口）
    import matplotlib
    matplotlib.use('Agg')
    
    main()
