"""
案例3：河流生态水力指标体系
=========================

工程背景
--------
某河流建坝前后的水文情势变化评估，评估大坝对河流生态水力特征的影响。

问题描述
--------
- 分析时段: 建坝前10年（2000-2009）vs 建坝后10年（2010-2019）
- 数据来源: 日流量序列
- 评估内容: IHA指标、水力多样性、改变度

计算目标
--------
1. 计算建坝前后的IHA指标（33个）
2. 分析水文改变度
3. 评估水力多样性变化
4. 综合评价生态影响

学习目标
--------
1. 理解IHA指标体系
2. 掌握水文改变度评估方法
3. 学会多指标综合评价
4. 分析水坝对河流的生态影响

作者: CHS-Books 生态水力学课程组
日期: 2025-11-02
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from code.models.indicators import (
    IHACalculator,
    HydraulicDiversityIndex,
    HydrologicAlterationAssessment,
    generate_iha_report
)

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


def generate_synthetic_flow_data(years: int = 20, dam_year: int = 10) -> pd.DataFrame:
    """
    生成模拟的日流量数据
    
    模拟建坝前后的流量特征变化
    
    Parameters
    ----------
    years : int
        总年数
    dam_year : int
        建坝年份（从第几年开始）
        
    Returns
    -------
    DataFrame
        包含日期和流量的数据
    """
    np.random.seed(42)  # 设置随机种子以便复现
    
    start_date = datetime(2000, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(years * 365)]
    
    flows = []
    
    for i, date in enumerate(dates):
        year_progress = (date.timetuple().tm_yday - 1) / 365.0
        year_index = i // 365
        
        # 基础流量模式（季节性变化）
        # 春季高流量（融雪）
        seasonal_pattern = (
            50 +  # 基流
            80 * np.sin(2 * np.pi * year_progress + np.pi/2) +  # 春季高峰
            30 * np.sin(4 * np.pi * year_progress)  # 次要波动
        )
        
        # 随机扰动
        noise = np.random.normal(0, 10)
        
        # 建坝后的影响
        if year_index >= dam_year:
            # 削峰填谷效应
            seasonal_pattern = 0.7 * seasonal_pattern + 0.3 * 80  # 趋于平均值
            # 减小波动
            noise *= 0.5
            # 基流增加
            base_flow_increase = 20
        else:
            base_flow_increase = 0
        
        flow = seasonal_pattern + noise + base_flow_increase
        
        # 偶尔的洪水事件（建坝前更频繁）
        if year_index < dam_year and np.random.random() < 0.02:
            flow += np.random.uniform(100, 200)
        elif year_index >= dam_year and np.random.random() < 0.005:
            flow += np.random.uniform(50, 100)  # 建坝后洪水减少
        
        flows.append(max(flow, 10))  # 确保流量为正
    
    return pd.DataFrame({'date': dates, 'flow': flows})


def main():
    """主计算流程"""
    
    print_header("案例3：河流生态水力指标体系")
    
    # ========================================================================
    # 第1步：生成/加载流量数据
    # ========================================================================
    print_section("【第1步】生成流量数据")
    
    # 生成20年的日流量数据（前10年建坝前，后10年建坝后）
    df = generate_synthetic_flow_data(years=20, dam_year=10)
    
    print(f"数据时段: {df['date'].min().date()} ~ {df['date'].max().date()}")
    print(f"数据点数: {len(df)}")
    print(f"平均流量: {df['flow'].mean():.2f} m³/s")
    print(f"流量范围: {df['flow'].min():.2f} ~ {df['flow'].max():.2f} m³/s")
    
    # ========================================================================
    # 第2步：创建IHA计算器
    # ========================================================================
    print_section("【第2步】创建IHA计算器")
    
    calculator = IHACalculator(
        daily_flow=df['flow'].values,
        dates=df['date'].values
    )
    
    print("✓ IHA计算器已创建")
    print(f"  分析时段: 建坝前（2000-2009）vs 建坝后（2010-2019）")
    
    # ========================================================================
    # 第3步：计算IHA指标（建坝前后对比）
    # ========================================================================
    print_section("【第3步】计算IHA指标")
    
    # 定义建坝前后的时间段
    pre_dates = df[df['date'].dt.year < 2010]['date'].values
    post_dates = df[df['date'].dt.year >= 2010]['date'].values
    
    print("\n计算建坝前后的33个IHA指标...")
    results = calculator.compare_periods(pre_dates, post_dates)
    
    print("\n✓ IHA指标计算完成")
    
    # 显示关键指标
    print("\n关键指标变化：")
    print(f"{'指标':<25} {'建坝前':<12} {'建坝后':<12} {'变化率':<12}")
    print("-" * 65)
    
    key_indicators = [
        ('Jan_mean', '1月平均流量'),
        ('Jul_mean', '7月平均流量'),
        ('min_7day', '7日最小流量'),
        ('max_7day', '7日最大流量'),
        ('high_pulse_count', '高脉冲次数'),
        ('rise_rate', '涨水速率')
    ]
    
    for key, name in key_indicators:
        pre_val = results['pre'][key]
        post_val = results['post'][key]
        change = results['change'][key]
        print(f"{name:<25} {pre_val:<12.2f} {post_val:<12.2f} {change:+.1f}%")
    
    # ========================================================================
    # 第4步：水文改变度评估
    # ========================================================================
    print_section("【第4步】水文改变度评估")
    
    # 计算改变度
    alteration = HydrologicAlterationAssessment.calculate_alteration_degree(
        results['pre'],
        results['post']
    )
    
    # 计算总体改变指数
    overall = HydrologicAlterationAssessment.overall_alteration_index(alteration)
    
    print(f"\n总体改变指数:")
    print(f"  平均改变度: {overall['mean_alteration']:.1f}%")
    print(f"  中位改变度: {overall['median_alteration']:.1f}%")
    print(f"  最大改变度: {overall['max_alteration']:.1f}%")
    print(f"  改变等级: {overall['grade']}")
    
    # 显示改变度最大的指标
    print("\n改变度最大的5个指标:")
    sorted_alteration = sorted(alteration.items(), key=lambda x: x[1], reverse=True)
    for i, (key, value) in enumerate(sorted_alteration[:5], 1):
        print(f"  {i}. {key}: {value:.1f}%")
    
    # ========================================================================
    # 第5步：水力多样性分析
    # ========================================================================
    print_section("【第5步】水力多样性分析")
    
    # 建坝前后的流量数据
    pre_flow = df[df['date'].dt.year < 2010]['flow'].values
    post_flow = df[df['date'].dt.year >= 2010]['flow'].values
    
    # 计算多样性指数
    pre_shannon = HydraulicDiversityIndex.shannon_index(pre_flow, bins=20)
    post_shannon = HydraulicDiversityIndex.shannon_index(post_flow, bins=20)
    
    pre_simpson = HydraulicDiversityIndex.simpson_index(pre_flow, bins=20)
    post_simpson = HydraulicDiversityIndex.simpson_index(post_flow, bins=20)
    
    pre_pielou = HydraulicDiversityIndex.pielou_evenness(pre_flow, bins=20)
    post_pielou = HydraulicDiversityIndex.pielou_evenness(post_flow, bins=20)
    
    print(f"\n水力多样性指数:")
    print(f"{'指数':<20} {'建坝前':<12} {'建坝后':<12} {'变化':<12}")
    print("-" * 60)
    print(f"{'Shannon指数':<20} {pre_shannon:<12.3f} {post_shannon:<12.3f} {post_shannon-pre_shannon:+.3f}")
    print(f"{'Simpson指数':<20} {pre_simpson:<12.3f} {post_simpson:<12.3f} {post_simpson-pre_simpson:+.3f}")
    print(f"{'Pielou均匀度':<20} {pre_pielou:<12.3f} {post_pielou:<12.3f} {post_pielou-pre_pielou:+.3f}")
    
    # 解释
    print("\n指数解释:")
    if post_shannon < pre_shannon:
        print("  ✗ Shannon指数降低 → 流量分布的多样性减少")
    else:
        print("  ✓ Shannon指数增加 → 流量分布的多样性增加")
    
    if post_simpson < pre_simpson:
        print("  ✗ Simpson指数降低 → 流量模式的均匀性降低")
    else:
        print("  ✓ Simpson指数增加 → 流量模式的均匀性增加")
    
    # ========================================================================
    # 第6步：生成可视化图表
    # ========================================================================
    print_section("【第6步】生成可视化图表")
    
    create_visualizations(df, results, alteration, overall, 
                         pre_shannon, post_shannon,
                         pre_simpson, post_simpson)
    
    print("\n✓ 可视化图表已生成:")
    print("  - flow_timeseries.png: 流量时间序列")
    print("  - monthly_comparison.png: 月平均流量对比")
    print("  - extreme_flow_comparison.png: 极端流量对比")
    print("  - alteration_assessment.png: 改变度评估")
    print("  - diversity_indices.png: 多样性指数对比")
    
    # ========================================================================
    # 第7步：生成综合报告
    # ========================================================================
    print_section("【第7步】生成综合报告")
    
    # 生成IHA报告
    report = generate_iha_report(results)
    
    # 保存报告
    with open('iha_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n✓ 综合报告已保存: iha_report.txt")
    
    # ========================================================================
    # 总结
    # ========================================================================
    print_header("评估完成！")
    
    print(f"\n✓ 总体改变等级: {overall['grade']}")
    print(f"✓ 平均改变度: {overall['mean_alteration']:.1f}%")
    print(f"✓ Shannon指数变化: {post_shannon-pre_shannon:+.3f}")
    print(f"✓ 生态影响: {'显著' if overall['mean_alteration'] > 40 else '中等'}")


def create_visualizations(df, results, alteration, overall,
                         pre_shannon, post_shannon,
                         pre_simpson, post_simpson):
    """创建可视化图表"""
    
    # 图1：流量时间序列
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    # 完整时间序列
    pre_data = df[df['date'].dt.year < 2010]
    post_data = df[df['date'].dt.year >= 2010]
    
    ax1.plot(pre_data['date'], pre_data['flow'], 'b-', alpha=0.6, linewidth=0.5, label='Pre-dam')
    ax1.plot(post_data['date'], post_data['flow'], 'r-', alpha=0.6, linewidth=0.5, label='Post-dam')
    ax1.axvline(datetime(2010, 1, 1), color='k', linestyle='--', alpha=0.5, label='Dam construction')
    ax1.set_xlabel('Date', fontsize=11)
    ax1.set_ylabel('Flow (m³/s)', fontsize=11)
    ax1.set_title('Daily Flow Time Series', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 年平均流量对比
    annual_pre = pre_data.groupby(pre_data['date'].dt.year)['flow'].mean()
    annual_post = post_data.groupby(post_data['date'].dt.year)['flow'].mean()
    
    ax2.bar(annual_pre.index, annual_pre.values, color='blue', alpha=0.6, label='Pre-dam')
    ax2.bar(annual_post.index, annual_post.values, color='red', alpha=0.6, label='Post-dam')
    ax2.axhline(annual_pre.mean(), color='b', linestyle='--', alpha=0.5)
    ax2.axhline(annual_post.mean(), color='r', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Year', fontsize=11)
    ax2.set_ylabel('Annual Mean Flow (m³/s)', fontsize=11)
    ax2.set_title('Annual Mean Flow Comparison', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('flow_timeseries.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: flow_timeseries.png")
    plt.close()
    
    # 图2：月平均流量对比
    fig, ax = plt.subplots(figsize=(12, 6))
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pre_monthly = [results['pre'][f'{m}_mean'] for m in months]
    post_monthly = [results['post'][f'{m}_mean'] for m in months]
    
    x = np.arange(len(months))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pre_monthly, width, label='Pre-dam', 
                   color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, post_monthly, width, label='Post-dam',
                   color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Mean Flow (m³/s)', fontsize=12)
    ax.set_title('Monthly Mean Flow Comparison', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('monthly_comparison.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: monthly_comparison.png")
    plt.close()
    
    # 图3：极端流量对比
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 最小流量
    ax = axes[0]
    windows = [1, 3, 7, 30, 90]
    pre_mins = [results['pre'][f'min_{w}day'] for w in windows]
    post_mins = [results['post'][f'min_{w}day'] for w in windows]
    
    x = np.arange(len(windows))
    bars1 = ax.bar(x - width/2, pre_mins, width, label='Pre-dam', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, post_mins, width, label='Post-dam', color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Window (days)', fontsize=11)
    ax.set_ylabel('Minimum Flow (m³/s)', fontsize=11)
    ax.set_title('Minimum Flow Comparison', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([str(w) for w in windows])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 最大流量
    ax = axes[1]
    pre_maxs = [results['pre'][f'max_{w}day'] for w in windows]
    post_maxs = [results['post'][f'max_{w}day'] for w in windows]
    
    bars1 = ax.bar(x - width/2, pre_maxs, width, label='Pre-dam', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, post_maxs, width, label='Pre-dam', color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Window (days)', fontsize=11)
    ax.set_ylabel('Maximum Flow (m³/s)', fontsize=11)
    ax.set_title('Maximum Flow Comparison', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([str(w) for w in windows])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('extreme_flow_comparison.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: extreme_flow_comparison.png")
    plt.close()
    
    # 图4：改变度评估
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 改变度分布
    alt_values = list(alteration.values())
    ax1.hist(alt_values, bins=20, color='#e74c3c', alpha=0.7, edgecolor='black')
    ax1.axvline(overall['mean_alteration'], color='b', linestyle='--', linewidth=2,
               label=f"Mean: {overall['mean_alteration']:.1f}%")
    ax1.axvline(overall['median_alteration'], color='g', linestyle='--', linewidth=2,
               label=f"Median: {overall['median_alteration']:.1f}%")
    ax1.set_xlabel('Alteration Degree (%)', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('Distribution of Alteration Degree', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 改变度等级饼图
    bins = [0, 20, 40, 60, 100]
    labels = ['轻度\n(<20%)', '中度\n(20-40%)', '较大\n(40-60%)', '严重\n(>60%)']
    counts = [sum((alteration[k] >= bins[i]) and (alteration[k] < bins[i+1]) 
                  for k in alteration) for i in range(len(bins)-1)]
    
    colors = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c']
    ax2.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors,
           startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('Alteration Grade Distribution', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('alteration_assessment.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: alteration_assessment.png")
    plt.close()
    
    # 图5：多样性指数对比
    fig, ax = plt.subplots(figsize=(10, 6))
    
    indices = ['Shannon\nIndex', 'Simpson\nIndex']
    pre_values = [pre_shannon, pre_simpson]
    post_values = [post_shannon, post_simpson]
    
    x = np.arange(len(indices))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pre_values, width, label='Pre-dam',
                   color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, post_values, width, label='Post-dam',
                   color='#e74c3c', alpha=0.8)
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Index Value', fontsize=12)
    ax.set_title('Hydraulic Diversity Indices Comparison', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(indices, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('diversity_indices.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: diversity_indices.png")
    plt.close()


if __name__ == "__main__":
    main()
