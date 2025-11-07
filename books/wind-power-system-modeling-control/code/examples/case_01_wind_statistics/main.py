"""
案例1: 风速统计分析

本案例演示:
1. Weibull分布建模
2. 风速数据统计分析
3. 风功率密度计算
4. 参数拟合与可视化

工程背景: 某风电场风速数据分析
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加models路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.wind_resource import (
    WeibullDistribution,
    WindPowerDensity,
    WindStatistics,
    generate_synthetic_wind_data
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_weibull_distribution():
    """演示1: Weibull分布特性"""
    print("=" * 60)
    print("演示1: Weibull分布特性")
    print("=" * 60)
    
    # 创建不同参数的Weibull分布
    distributions = [
        WeibullDistribution(k=1.5, c=6.0, name="k=1.5, c=6"),
        WeibullDistribution(k=2.0, c=7.0, name="k=2.0, c=7"),
        WeibullDistribution(k=2.5, c=8.0, name="k=2.5, c=8"),
    ]
    
    # 打印统计量
    for dist in distributions:
        status = dist.get_status()
        print(f"\n{status['name']}:")
        print(f"  平均风速: {status['mean_speed']:.2f} m/s")
        print(f"  标准差: {status['std_dev']:.2f} m/s")
        print(f"  最可能风速: {status['mode_speed']:.2f} m/s")
    
    # 可视化
    v = np.linspace(0, 25, 500)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # PDF
    ax = axes[0]
    for dist in distributions:
        ax.plot(v, dist.pdf(v), label=dist.name, linewidth=2)
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('概率密度', fontsize=12)
    ax.set_title('Weibull概率密度函数', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # CDF
    ax = axes[1]
    for dist in distributions:
        ax.plot(v, dist.cdf(v), label=dist.name, linewidth=2)
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('累积概率', fontsize=12)
    ax.set_title('Weibull累积分布函数', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case01_weibull_distributions.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case01_weibull_distributions.png")


def demo_wind_power_density():
    """演示2: 风功率密度计算"""
    print("\n" + "=" * 60)
    print("演示2: 风功率密度计算")
    print("=" * 60)
    
    # 创建Weibull分布
    weibull = WeibullDistribution(k=2.0, c=8.0, name="典型风场")
    
    # 创建功率密度计算器
    power_calc = WindPowerDensity(rho=1.225)
    
    # 计算平均功率密度
    p_avg = power_calc.average_from_weibull(weibull)
    epf = power_calc.energy_pattern_factor(weibull)
    
    print(f"\nWeibull参数: k={weibull.k}, c={weibull.c}")
    print(f"平均风速: {weibull.mean_speed:.2f} m/s")
    print(f"平均风功率密度: {p_avg:.2f} W/m²")
    print(f"能量模式因子 (EPF): {epf:.3f}")
    
    # 不同风速的功率密度
    v_range = np.array([3, 5, 7, 9, 11, 13, 15])
    p_range = power_calc.calculate(v_range)
    
    print("\n不同风速的功率密度:")
    for v, p in zip(v_range, p_range):
        print(f"  v = {v:2d} m/s → P/A = {p:6.1f} W/m²")
    
    # 可视化
    v = np.linspace(0, 25, 500)
    p = power_calc.calculate(v)
    prob = weibull.pdf(v)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 功率密度曲线
    ax = axes[0]
    ax.plot(v, p, 'b-', linewidth=2, label='功率密度')
    ax.axvline(weibull.mean_speed, color='r', linestyle='--', 
               label=f'平均风速 ({weibull.mean_speed:.2f} m/s)')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('功率密度 (W/m²)', fontsize=12)
    ax.set_title('风功率密度特性', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 风速分布与功率分布
    ax = axes[1]
    ax2 = ax.twinx()
    
    ax.plot(v, prob, 'g-', linewidth=2, label='风速概率密度')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('概率密度', fontsize=12, color='g')
    ax.tick_params(axis='y', labelcolor='g')
    
    ax2.plot(v, p * prob, 'orange', linewidth=2, label='功率贡献')
    ax2.set_ylabel('功率贡献 (W/m²)', fontsize=12, color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')
    
    ax.set_title('风速分布与功率贡献', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case01_power_density.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case01_power_density.png")


def demo_data_analysis():
    """演示3: 实测数据分析"""
    print("\n" + "=" * 60)
    print("演示3: 实测风速数据分析")
    print("=" * 60)
    
    # 生成模拟数据（一年8760小时）
    print("\n生成模拟风速数据...")
    wind_data = generate_synthetic_wind_data(
        hours=8760,
        mean_speed=7.5,
        k=2.0
    )
    
    # 统计分析
    print("进行统计分析...")
    stats = WindStatistics(wind_data, rho=1.225, name="年度风速数据")
    
    # 打印报告
    report = stats.get_report()
    
    print(f"\n数据点数: {report['data_points']}")
    print("\n基本统计量:")
    basic = report['basic_stats']
    print(f"  平均值: {basic['mean']:.2f} m/s")
    print(f"  中位数: {basic['median']:.2f} m/s")
    print(f"  标准差: {basic['std']:.2f} m/s")
    print(f"  最小值: {basic['min']:.2f} m/s")
    print(f"  最大值: {basic['max']:.2f} m/s")
    print(f"  25%分位: {basic['percentile_25']:.2f} m/s")
    print(f"  75%分位: {basic['percentile_75']:.2f} m/s")
    print(f"  95%分位: {basic['percentile_95']:.2f} m/s")
    
    print("\n风功率密度:")
    power = report['power_density']
    print(f"  实测平均: {power['measured_avg']:.2f} W/m²")
    print(f"  Weibull估算: {power['weibull_avg']:.2f} W/m²")
    
    if 'weibull_params' in report:
        print("\n拟合的Weibull参数:")
        wb = report['weibull_params']
        print(f"  形状参数 k: {wb['shape_k']:.3f}")
        print(f"  尺度参数 c: {wb['scale_c']:.3f}")
        print(f"  拟合平均风速: {wb['mean_speed']:.2f} m/s")
    
    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. 时间序列（前100小时）
    ax = axes[0, 0]
    t = np.arange(100)
    ax.plot(t, wind_data[:100], 'b-', linewidth=1, alpha=0.7)
    ax.axhline(stats.mean, color='r', linestyle='--', label=f'平均值 ({stats.mean:.2f} m/s)')
    ax.set_xlabel('时间 (小时)', fontsize=11)
    ax.set_ylabel('风速 (m/s)', fontsize=11)
    ax.set_title('风速时间序列（前100小时）', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. 直方图与拟合分布
    ax = axes[0, 1]
    bin_centers, frequencies = stats.histogram(bins=30)
    ax.bar(bin_centers, frequencies, width=0.5, alpha=0.6, label='实测数据')
    
    if stats.weibull is not None:
        v_fit = np.linspace(0, stats.max, 500)
        pdf_fit = stats.weibull.pdf(v_fit)
        ax.plot(v_fit, pdf_fit, 'r-', linewidth=2, label='Weibull拟合')
    
    ax.set_xlabel('风速 (m/s)', fontsize=11)
    ax.set_ylabel('概率密度', fontsize=11)
    ax.set_title('风速概率分布', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. 累积分布
    ax = axes[1, 0]
    sorted_data = np.sort(wind_data)
    cdf_empirical = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    ax.plot(sorted_data, cdf_empirical, 'b-', linewidth=2, label='实测数据')
    
    if stats.weibull is not None:
        v_fit = np.linspace(0, stats.max, 500)
        cdf_fit = stats.weibull.cdf(v_fit)
        ax.plot(v_fit, cdf_fit, 'r--', linewidth=2, label='Weibull拟合')
    
    ax.set_xlabel('风速 (m/s)', fontsize=11)
    ax.set_ylabel('累积概率', fontsize=11)
    ax.set_title('风速累积分布', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. 箱线图
    ax = axes[1, 1]
    bp = ax.boxplot([wind_data], vert=True, patch_artist=True, 
                     labels=['年度风速'])
    bp['boxes'][0].set_facecolor('lightblue')
    ax.set_ylabel('风速 (m/s)', fontsize=11)
    ax.set_title('风速箱线图', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 添加统计信息
    stats_text = f"平均: {stats.mean:.2f} m/s\n"
    stats_text += f"中位数: {stats.median:.2f} m/s\n"
    stats_text += f"标准差: {stats.std:.2f} m/s"
    ax.text(1.15, stats.mean, stats_text, fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('case01_data_analysis.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case01_data_analysis.png")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("案例1: 风速统计分析")
    print("=" * 60)
    
    # 演示1: Weibull分布
    demo_weibull_distribution()
    
    # 演示2: 风功率密度
    demo_wind_power_density()
    
    # 演示3: 数据分析
    demo_data_analysis()
    
    print("\n" + "=" * 60)
    print("案例1 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case01_weibull_distributions.png")
    print("  2. case01_power_density.png")
    print("  3. case01_data_analysis.png")
    
    plt.show()


if __name__ == "__main__":
    main()
