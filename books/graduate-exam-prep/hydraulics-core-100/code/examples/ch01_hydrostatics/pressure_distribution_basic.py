"""
水力学考研核心100题 - 第一章题目1
静水压强分布计算与可视化

功能：
1. 计算不同水深的压强
2. 绘制压强分布图
3. 对比相对压强和绝对压强

作者：CHS-Books考研系列
更新：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体（解决中文显示问题）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def calculate_pressure(H, rho=1000, g=9.81, p0=101.325):
    """
    计算静水压强

    Parameters:
    -----------
    H : float
        水深 (m)
    rho : float, optional
        水密度 (kg/m³), 默认1000
    g : float, optional
        重力加速度 (m/s²), 默认9.81
    p0 : float, optional
        大气压 (kPa), 默认101.325

    Returns:
    --------
    dict : 包含计算结果的字典
        - p_bottom_rel: 池底相对压强 (kPa)
        - p_bottom_abs: 池底绝对压强 (kPa)
    """
    # 池底相对压强 (kPa)
    p_bottom_rel = rho * g * H / 1000

    # 池底绝对压强 (kPa)
    p_bottom_abs = p0 + p_bottom_rel

    return {
        'p_bottom_rel': p_bottom_rel,
        'p_bottom_abs': p_bottom_abs
    }


def plot_pressure_distribution(H, rho=1000, g=9.81, p0=101.325,
                              check_depth=2.0, save_fig=True):
    """
    绘制静水压强分布图

    Parameters:
    -----------
    H : float
        总水深 (m)
    rho : float, optional
        水密度 (kg/m³)
    g : float, optional
        重力加速度 (m/s²)
    p0 : float, optional
        大气压 (kPa)
    check_depth : float, optional
        检查点深度 (m)
    save_fig : bool, optional
        是否保存图片
    """
    # 计算压强
    results = calculate_pressure(H, rho, g, p0)
    p_bottom_rel = results['p_bottom_rel']
    p_bottom_abs = results['p_bottom_abs']

    # 检查点压强
    p_check = rho * g * check_depth / 1000

    # 创建水深数组
    h = np.linspace(0, H, 100)

    # 计算相对压强和绝对压强
    p_rel = rho * g * h / 1000
    p_abs = p0 + p_rel

    # 创建图表
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # ========== 子图1：相对压强分布 ==========
    ax1 = axes[0]
    ax1.plot(p_rel, h, 'b-', linewidth=3, label='压强分布')
    ax1.axhline(y=check_depth, color='r', linestyle='--', alpha=0.7, linewidth=2,
                label=f'h={check_depth}m (p={p_check:.2f}kPa)')
    ax1.axhline(y=H, color='g', linestyle='--', alpha=0.7, linewidth=2,
                label=f'池底 (p={p_bottom_rel:.2f}kPa)')

    # 填充水体区域
    ax1.fill_betweenx(h, 0, p_rel, alpha=0.2, color='blue')

    ax1.set_xlabel('相对压强 (kPa)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('水深 h (m)', fontsize=13, fontweight='bold')
    ax1.set_title('静水压强沿水深分布\n（相对压强，大气压为零点）',
                 fontsize=14, fontweight='bold')
    ax1.invert_yaxis()  # 反转y轴，水面在上
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=11, loc='lower right')

    # 标注关键点
    ax1.plot(p_check, check_depth, 'ro', markersize=10)
    ax1.plot(p_bottom_rel, H, 'go', markersize=10)

    # ========== 子图2：绝对压强分布 ==========
    ax2 = axes[1]
    ax2.plot(p_abs, h, 'purple', linewidth=3, label='绝对压强')
    ax2.axhline(y=0, color='orange', linestyle=':', linewidth=2,
                label=f'水面 (p={p0:.1f}kPa=大气压)')
    ax2.axhline(y=H, color='g', linestyle='--', alpha=0.7, linewidth=2,
                label=f'池底 (p={p_bottom_abs:.2f}kPa)')

    ax2.fill_betweenx(h, p0, p_abs, alpha=0.2, color='purple')

    ax2.set_xlabel('绝对压强 (kPa)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('水深 h (m)', fontsize=13, fontweight='bold')
    ax2.set_title('静水压强沿水深分布\n（绝对压强）',
                 fontsize=14, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(fontsize=11, loc='lower right')

    # ========== 子图3：水池剖面与压强 ==========
    ax3 = axes[2]

    # 绘制水池容器
    pool_width = p_bottom_rel * 1.2
    ax3.plot([0, 0], [0, H], 'k-', linewidth=4)  # 左边界
    ax3.plot([pool_width, pool_width], [0, H], 'k-', linewidth=4)  # 右边界
    ax3.plot([0, pool_width], [H, H], 'k-', linewidth=4)  # 底部

    # 水体
    ax3.fill_between([0, pool_width], 0, H, alpha=0.3, color='cyan', label='水体')

    # 压强分布线
    ax3.plot(p_rel, h, 'r-', linewidth=3.5, label='压强分布')

    # 标注关键点
    ax3.plot(p_check, check_depth, 'ro', markersize=12)
    ax3.text(p_check + 2, check_depth,
            f'  ({p_check:.1f}kPa, {check_depth}m)',
            fontsize=11, fontweight='bold')

    ax3.plot(p_bottom_rel, H, 'go', markersize=12)
    ax3.text(p_bottom_rel - 10, H - 0.3,
            f'({p_bottom_rel:.1f}kPa, {H}m)',
            fontsize=11, fontweight='bold')

    ax3.set_xlabel('压强 (kPa)', fontsize=13, fontweight='bold')
    ax3.set_ylabel('深度 (m)', fontsize=13, fontweight='bold')
    ax3.set_title('水池剖面与压强分布',
                 fontsize=14, fontweight='bold')
    ax3.invert_yaxis()
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(fontsize=11, loc='upper right')
    ax3.set_xlim(-5, pool_width + 5)

    plt.tight_layout()

    if save_fig:
        plt.savefig('pressure_distribution_basic.png',
                   dpi=300, bbox_inches='tight', facecolor='white')
        print("\n✅ 图表已保存为 'pressure_distribution_basic.png'")

    plt.show()


def main():
    """主函数：执行计算和绘图"""

    # ========== 参数设置 ==========
    H = 6.0          # 水深 (m)
    rho = 1000       # 水密度 (kg/m³)
    g = 9.81         # 重力加速度 (m/s²)
    p0 = 101.325     # 大气压 (kPa)
    check_depth = 2.0  # 检查点深度 (m)

    print("=" * 70)
    print("水力学考研核心100题 - 第一章题目1")
    print("静水压强分布计算")
    print("=" * 70)

    # ========== 计算 ==========
    results = calculate_pressure(H, rho, g, p0)
    p_bottom_rel = results['p_bottom_rel']
    p_bottom_abs = results['p_bottom_abs']

    p_check = rho * g * check_depth / 1000

    # ========== 输出结果 ==========
    print(f"\n【已知条件】")
    print(f"  水深 H = {H} m")
    print(f"  水密度 ρ = {rho} kg/m³")
    print(f"  重力加速度 g = {g} m/s²")
    print(f"  大气压 p₀ = {p0} kPa")

    print(f"\n【计算结果】")
    print(f"(1) 池底压强：")
    print(f"    相对压强 = ρgH = {rho} × {g} × {H}")
    print(f"             = {p_bottom_rel:.2f} kPa")
    print(f"    绝对压强 = p₀ + ρgH")
    print(f"             = {p0} + {p_bottom_rel:.2f}")
    print(f"             = {p_bottom_abs:.2f} kPa")

    print(f"\n(2) h={check_depth}m处压强：")
    print(f"    p = ρgh = {rho} × {g} × {check_depth}")
    print(f"      = {p_check:.2f} kPa")

    print(f"\n【物理意义】")
    print(f"  • 压强随深度线性增加")
    print(f"  • 每增加1m深度，压强增加约{rho*g/1000:.1f}kPa")
    print(f"  • 池底压强相当于{p_bottom_rel/9.81:.1f}m水柱高度")

    print("\n" + "=" * 70)
    print("正在生成可视化图表...")
    print("=" * 70)

    # ========== 绘图 ==========
    plot_pressure_distribution(H, rho, g, p0, check_depth)

    # ========== 练习题提示 ==========
    print("\n" + "=" * 70)
    print("【参数调整练习】")
    print("=" * 70)
    print("1. 修改 H=10 m，重新计算池底压强")
    print("2. 修改 g=1.62 m/s²（月球重力），思考压强变化")
    print("3. 修改 rho=13600 kg/m³（水银），计算压强")
    print("\n在代码开头修改参数，重新运行观察结果变化！")
    print("=" * 70)


if __name__ == "__main__":
    main()
