"""
案例1：河流生态基流计算
=====================

工程背景
--------
某山区河流拟建水库，需确定下游生态基流以保障鱼类生存繁殖。

问题描述
--------
- 河流多年平均流量: Q_maf = 15.0 m³/s
- 枯水期流量: Q_dry = 3.0 m³/s
- 河段长度: L = 2000 m
- 河道平均宽度: b = 20 m
- 河床坡度: S0 = 0.001
- Manning糙率: n = 0.035 (天然河道)
- 边坡系数: m = 2.0

计算目标
--------
1. 使用Tennant法计算生态流量
2. 使用湿周法计算生态流量
3. 使用R2-Cross法计算生态流量
4. 综合评估并给出推荐值

学习目标
--------
1. 理解生态基流的概念和重要性
2. 掌握多种生态流量计算方法
3. 学会不同方法的比较分析
4. 理解流量-生境关系

作者: CHS-Books 生态水力学课程组
日期: 2025-11-02
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from code.models.channel import River, RiverReach
from code.models.ecological_flow import EcologicalFlowCalculator

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(f"{title:^80}")
    print("="*80)


def print_section(title):
    """打印章节标题"""
    print("\n" + "-"*80)
    print(title)
    print("-"*80)


def main():
    """主计算流程"""
    
    print_header("案例1：河流生态基流计算")
    
    # ========================================================================
    # 第1步：定义河流参数
    # ========================================================================
    print_section("【第1步】定义河流参数")
    
    # 创建河流对象
    river = River(
        name="某山区河流",
        mean_annual_flow=15.0  # 多年平均流量 m³/s
    )
    
    # 创建河段
    reach = RiverReach(
        length=2000.0,      # 河段长度 m
        width=20.0,         # 河道底宽 m
        slope=0.001,        # 河床坡度
        roughness=0.035,    # Manning糙率
        side_slope=2.0      # 边坡系数
    )
    
    river.add_reach(reach)
    
    print(f"河流名称: {river.name}")
    print(f"多年平均流量: {river.Q_maf} m³/s")
    print(f"河段长度: {reach.length} m")
    print(f"河道底宽: {reach.b} m")
    print(f"河床坡度: {reach.S0}")
    print(f"Manning糙率: {reach.n}")
    print(f"边坡系数: {reach.m}")
    
    # ========================================================================
    # 第2步：验证水力计算
    # ========================================================================
    print_section("【第2步】验证水力计算")
    
    # 计算多年平均流量下的水深
    h_maf = reach.solve_depth(river.Q_maf)
    props_maf = reach.get_hydraulic_properties(h_maf)
    
    print(f"\n多年平均流量 Q = {river.Q_maf} m³/s 时:")
    print(f"  水深: {props_maf['depth']:.2f} m")
    print(f"  流速: {props_maf['velocity']:.2f} m/s")
    print(f"  断面积: {props_maf['area']:.2f} m²")
    print(f"  湿周: {props_maf['wetted_perimeter']:.2f} m")
    print(f"  水面宽: {props_maf['top_width']:.2f} m")
    
    # ========================================================================
    # 第3步：创建生态流量计算器
    # ========================================================================
    print_section("【第3步】计算生态流量")
    
    calculator = EcologicalFlowCalculator(river)
    
    # 综合评估
    results = calculator.comprehensive_assessment(
        flow_range=(0.5, 15.0),  # 流量范围
        season='annual'           # 年平均情况
    )
    
    # ========================================================================
    # 第4步：输出各方法结果
    # ========================================================================
    print_section("【第4步】各方法计算结果")
    
    # Tennant法
    print("\n1. Tennant法（蒙大拿法）")
    tennant = results['tennant']
    print(f"   优秀生境: {tennant['excellent_lower']:.2f} ~ {tennant['excellent_upper']:.2f} m³/s "
          f"(60-100% MAF)")
    print(f"   良好生境: {tennant['good_lower']:.2f} ~ {tennant['good_upper']:.2f} m³/s "
          f"(40-60% MAF)")
    print(f"   一般生境: {tennant['fair_lower']:.2f} ~ {tennant['fair_upper']:.2f} m³/s "
          f"(30-40% MAF)")
    print(f"   最小流量: {tennant['minimum']:.2f} m³/s (10% MAF)")
    print(f"   → 推荐值: {results['tennant_recommended']:.2f} m³/s (30% MAF)")
    
    # 湿周法
    print("\n2. 湿周法")
    wp_result = results['wetted_perimeter']
    print(f"   生态流量: {wp_result['ecological_flow']:.2f} m³/s")
    print(f"   对应湿周: {wp_result['wetted_perimeter']:.2f} m")
    print(f"   湿周占比: {wp_result['wp_ratio']*100:.1f}%")
    print(f"   → 推荐值: {results['wp_recommended']:.2f} m³/s")
    
    # R2-Cross法
    print("\n3. R2-Cross法")
    r2_result = results['r2cross']
    print(f"   生态流量: {r2_result['ecological_flow']:.2f} m³/s")
    print(f"   对应水深: {r2_result['depth']:.2f} m")
    print(f"   水深占比: {r2_result['depth_ratio']*100:.1f}%")
    print(f"   最大水深: {r2_result['max_depth']:.2f} m")
    print(f"   → 推荐值: {results['r2cross_recommended']:.2f} m³/s")
    
    # ========================================================================
    # 第5步：综合推荐值
    # ========================================================================
    print_section("【第5步】综合推荐结果")
    
    print(f"\n各方法推荐值:")
    for i, q in enumerate(results['all_recommendations'], 1):
        print(f"  方法{i}: {q:.2f} m³/s")
    
    print(f"\n最终推荐生态流量: {results['final_recommended']:.2f} m³/s")
    print(f"占多年平均流量: {results['percentage_of_maf']:.1f}%")
    print(f"推荐范围: {results['recommendation_range'][0]:.2f} ~ "
          f"{results['recommendation_range'][1]:.2f} m³/s")
    
    # 计算推荐流量下的水深
    h_eco = reach.solve_depth(results['final_recommended'])
    props_eco = reach.get_hydraulic_properties(h_eco)
    
    print(f"\n推荐生态流量下的水力参数:")
    print(f"  水深: {props_eco['depth']:.2f} m")
    print(f"  流速: {props_eco['velocity']:.2f} m/s")
    print(f"  断面积: {props_eco['area']:.2f} m²")
    print(f"  湿周: {props_eco['wetted_perimeter']:.2f} m")
    
    # ========================================================================
    # 第6步：生成完整报告
    # ========================================================================
    print_section("【第6步】生态流量评估报告")
    
    report = calculator.generate_report(results)
    print(report)
    
    # ========================================================================
    # 第7步：可视化分析
    # ========================================================================
    print_section("【第7步】生成可视化图表")
    
    create_visualizations(river, reach, results, calculator)
    
    print("\n可视化图表已保存:")
    print("  - wetted_perimeter_curve.png: 湿周-流量关系曲线")
    print("  - depth_discharge_curve.png: 水深-流量关系曲线")
    print("  - ecological_flow_comparison.png: 各方法结果对比")
    
    # ========================================================================
    # 总结
    # ========================================================================
    print_header("计算完成！")
    print(f"\n✓ 推荐生态流量: {results['final_recommended']:.2f} m³/s")
    print(f"✓ 占多年平均流量: {results['percentage_of_maf']:.1f}%")
    print(f"✓ 能够保障河流生态系统基本功能")


def create_visualizations(river, reach, results, calculator):
    """创建可视化图表"""
    
    # 图1：湿周-流量关系曲线
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    wp_result = results['wetted_perimeter']
    flows = wp_result['flow_data']
    wp_data = wp_result['wp_data']
    Q_eco_wp = wp_result['ecological_flow']
    
    ax1.plot(flows, wp_data, 'b-', linewidth=2, label='湿周曲线')
    ax1.axvline(Q_eco_wp, color='r', linestyle='--', linewidth=2, label=f'生态流量 = {Q_eco_wp:.2f} m³/s')
    ax1.axvline(river.Q_maf, color='g', linestyle='--', alpha=0.5, label=f'多年平均流量 = {river.Q_maf:.2f} m³/s')
    ax1.scatter([Q_eco_wp], [wp_result['wetted_perimeter']], color='r', s=100, zorder=5)
    ax1.set_xlabel('流量 (m³/s)', fontsize=12)
    ax1.set_ylabel('湿周 (m)', fontsize=12)
    ax1.set_title('湿周-流量关系曲线（湿周法）', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    
    # 湿周变化率
    dP_dQ = wp_result['dP_dQ']
    ax2.plot(flows, dP_dQ, 'b-', linewidth=2, label='湿周变化率 dP/dQ')
    ax2.axvline(Q_eco_wp, color='r', linestyle='--', linewidth=2, label='生态流量')
    ax2.set_xlabel('流量 (m³/s)', fontsize=12)
    ax2.set_ylabel('湿周变化率 dP/dQ (m/(m³/s))', fontsize=12)
    ax2.set_title('湿周变化率曲线', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('wetted_perimeter_curve.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: wetted_perimeter_curve.png")
    plt.close()
    
    # 图2：水深-流量关系曲线
    fig, ax = plt.subplots(figsize=(10, 6))
    
    r2_result = results['r2cross']
    flows_r2 = r2_result['flow_data']
    depths = r2_result['depth_data']
    Q_eco_r2 = r2_result['ecological_flow']
    h_eco = r2_result['depth']
    
    ax.plot(flows_r2, depths, 'b-', linewidth=2, label='水深曲线')
    ax.axvline(Q_eco_r2, color='r', linestyle='--', linewidth=2, label=f'生态流量 = {Q_eco_r2:.2f} m³/s')
    ax.axhline(h_eco, color='r', linestyle=':', alpha=0.5, label=f'生态水深 = {h_eco:.2f} m')
    ax.axhline(r2_result['target_depth'], color='orange', linestyle='--', alpha=0.5, 
               label=f'目标水深 (25%最大) = {r2_result["target_depth"]:.2f} m')
    ax.scatter([Q_eco_r2], [h_eco], color='r', s=100, zorder=5)
    ax.set_xlabel('流量 (m³/s)', fontsize=12)
    ax.set_ylabel('水深 (m)', fontsize=12)
    ax.set_title('水深-流量关系曲线（R2-Cross法）', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('depth_discharge_curve.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: depth_discharge_curve.png")
    plt.close()
    
    # 图3：各方法结果对比
    fig, ax = plt.subplots(figsize=(10, 6))
    
    methods = ['Tennant法\n(30% MAF)', '湿周法', 'R2-Cross法', '综合推荐']
    values = [
        results['tennant_recommended'],
        results['wp_recommended'],
        results['r2cross_recommended'],
        results['final_recommended']
    ]
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    bars = ax.bar(methods, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f} m³/s\n({val/river.Q_maf*100:.1f}% MAF)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 添加MAF参考线
    ax.axhline(river.Q_maf, color='gray', linestyle='--', linewidth=2, alpha=0.5, 
               label=f'多年平均流量 = {river.Q_maf:.2f} m³/s')
    
    ax.set_ylabel('生态流量 (m³/s)', fontsize=12)
    ax.set_title('生态流量计算方法对比', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('ecological_flow_comparison.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: ecological_flow_comparison.png")
    plt.close()


if __name__ == "__main__":
    main()
