#!/usr/bin/env python3
"""
案例27：泵站瞬变过程

本示例展示：
1. 泵特性曲线计算
2. 泵停机转速衰减分析
3. 四象限运行状态
4. 飞轮防护设计

运行方式：
    python main.py

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ========== 泵站参数类 ==========

class PumpStation:
    """泵站类"""
    def __init__(self, Q0, H0, n0, GD2, L, D, a, H_s, H_d):
        """
        参数：
            Q0: 额定流量 (m³/s)
            H0: 额定扬程 (m)
            n0: 额定转速 (rpm)
            GD2: 转动惯量 (kg·m²)
            L: 管道长度 (m)
            D: 管径 (m)
            a: 波速 (m/s)
            H_s: 上游水位 (m)
            H_d: 下游水位 (m)
        """
        self.Q0 = Q0
        self.H0 = H0
        self.n0 = n0
        self.GD2 = GD2
        self.L = L
        self.D = D
        self.a = a
        self.H_s = H_s
        self.H_d = H_d
        self.g = 9.81

        # 特性系数
        self.a_h = 0.4  # 扬程系数
        self.a_m = 0.6  # 转矩系数
        self.b_m = 0.4

    def head_curve(self, Q, n=None):
        """
        泵扬程曲线
        H = H0 * (n/n0)² * [1 - a_h * (Q/(Q0*n/n0))²]
        """
        if n is None:
            n = self.n0
        n_ratio = n / self.n0
        Q_ratio = Q / (self.Q0 * n_ratio) if n_ratio > 1e-6 else 0
        H = self.H0 * n_ratio**2 * (1 - self.a_h * Q_ratio**2)
        return H

    def torque_curve(self, Q, n=None):
        """
        泵转矩曲线
        M = M0 * (n/n0)² * [a_m + b_m * (Q/(Q0*n/n0))]
        """
        if n is None:
            n = self.n0
        M0 = self.Q0 * self.H0 * 1000 * self.g / (2 * np.pi * self.n0 / 60)  # N·m
        n_ratio = n / self.n0
        Q_ratio = Q / (self.Q0 * n_ratio) if n_ratio > 1e-6 else 0
        M = M0 * n_ratio**2 * (self.a_m + self.b_m * Q_ratio)
        return M

    def power_curve(self, Q, n=None):
        """泵功率"""
        if n is None:
            n = self.n0
        H = self.head_curve(Q, n)
        P = 1000 * self.g * Q * H / 1000  # kW
        return P


# ========== 打印函数 ==========

def print_header(title, width=70):
    """打印标题"""
    print("\n" + "="*width)
    print(f"  {title}")
    print("="*width)


def print_param(name, value, unit="", width=50):
    """打印参数"""
    if unit:
        print(f"  {name:.<{width}} {value:>12.4f} {unit}")
    else:
        print(f"  {name:.<{width}} {value:>12}")


# ========== 演示1：泵特性曲线 ==========

def demo1_pump_characteristics():
    """演示1：泵特性曲线"""
    print_header("演示1：泵特性曲线")

    # 创建泵站
    pump = PumpStation(
        Q0=0.15, H0=40, n0=1450, GD2=50,
        L=800, D=0.4, a=1000,
        H_s=5, H_d=35
    )

    print("\n【泵站参数】")
    print_param("额定流量 Q0", pump.Q0, "m³/s")
    print_param("额定扬程 H0", pump.H0, "m")
    print_param("额定转速 n0", pump.n0, "rpm")
    print_param("转动惯量 GD²", pump.GD2, "kg·m²")

    # 计算特性曲线
    Q_array = np.linspace(0, 1.5*pump.Q0, 100)

    # 额定转速曲线
    H_rated = [pump.head_curve(Q, pump.n0) for Q in Q_array]
    P_rated = [pump.power_curve(Q, pump.n0) for Q in Q_array]

    # 不同转速曲线
    n_ratios = [0.6, 0.8, 1.0, 1.2]
    colors = ['blue', 'green', 'red', 'orange']

    # 打印额定工况点
    print("\n【额定工况点】")
    H_rated_point = pump.head_curve(pump.Q0, pump.n0)
    P_rated_point = pump.power_curve(pump.Q0, pump.n0)
    print_param("流量 Q0", pump.Q0, "m³/s")
    print_param("扬程 H0", H_rated_point, "m")
    print_param("功率 P0", P_rated_point, "kW")

    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 子图1：H-Q曲线
    for i, n_ratio in enumerate(n_ratios):
        n = n_ratio * pump.n0
        H_curve = [pump.head_curve(Q, n) for Q in Q_array]
        ax1.plot(Q_array*1000, H_curve, color=colors[i], linewidth=2,
                label=f'n = {n_ratio}n₀ = {n:.0f} rpm')

    # 标记额定工况点
    ax1.plot(pump.Q0*1000, H_rated_point, 'ro', markersize=10,
            label='额定工况点')
    ax1.annotate(f'Q₀={pump.Q0*1000:.0f} L/s\nH₀={H_rated_point:.1f} m',
                xy=(pump.Q0*1000, H_rated_point),
                xytext=(pump.Q0*1000+20, H_rated_point+5),
                fontsize=10, ha='left',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

    ax1.set_xlabel('流量 Q (L/s)', fontsize=11)
    ax1.set_ylabel('扬程 H (m)', fontsize=11)
    ax1.set_title('泵扬程特性曲线', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_xlim([0, 250])
    ax1.set_ylim([0, 80])

    # 子图2：P-Q曲线
    for i, n_ratio in enumerate(n_ratios):
        n = n_ratio * pump.n0
        P_curve = [pump.power_curve(Q, n) for Q in Q_array]
        ax2.plot(Q_array*1000, P_curve, color=colors[i], linewidth=2,
                label=f'n = {n_ratio}n₀')

    ax2.plot(pump.Q0*1000, P_rated_point, 'ro', markersize=10,
            label='额定工况点')

    ax2.set_xlabel('流量 Q (L/s)', fontsize=11)
    ax2.set_ylabel('功率 P (kW)', fontsize=11)
    ax2.set_title('泵功率特性曲线', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    ax2.set_xlim([0, 250])

    plt.tight_layout()
    plt.savefig('demo1_pump_characteristics.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo1_pump_characteristics.png")
    plt.close()


# ========== 演示2：转速衰减分析 ==========

def demo2_speed_decay():
    """演示2：转速衰减分析"""
    print_header("演示2：转速衰减分析")

    # 创建泵站
    pump = PumpStation(
        Q0=0.15, H0=40, n0=1450, GD2=50,
        L=800, D=0.4, a=1000,
        H_s=5, H_d=35
    )

    # 计算惯性时间常数
    M0 = pump.Q0 * pump.H0 * 1000 * pump.g / (2 * np.pi * pump.n0 / 60)
    M_friction = 0.05 * M0  # 假设摩擦转矩为5%额定转矩
    T_i = (pump.GD2 * pump.n0 / 60) / (2 * M_friction)  # 秒

    print("\n【惯性时间常数】")
    print_param("额定转矩 M0", M0, "N·m")
    print_param("摩擦转矩 M_f", M_friction, "N·m")
    print_param("惯性时间常数 T_i", T_i, "s")

    # 时间数组
    t_array = np.linspace(0, 60, 300)

    # 转速衰减（指数衰减）
    n_array = pump.n0 * np.exp(-t_array / T_i)

    # 转速衰减率
    dn_dt_array = -(pump.n0 / T_i) * np.exp(-t_array / T_i)

    # 打印关键时刻
    print("\n【关键时刻转速】")
    for t in [0, 10, 20, 30, 40, 50, 60]:
        i = np.argmin(np.abs(t_array - t))
        n = n_array[i]
        print_param(f"t = {t}s", n, "rpm")

    # 计算不同GD²的衰减
    GD2_array = [25, 50, 100, 200]
    colors = ['blue', 'green', 'red', 'orange']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # 子图1：转速衰减曲线
    for i, GD2 in enumerate(GD2_array):
        T_i_var = (GD2 * pump.n0 / 60) / (2 * M_friction)
        n_var = pump.n0 * np.exp(-t_array / T_i_var)
        ax1.plot(t_array, n_var, color=colors[i], linewidth=2,
                label=f'GD² = {GD2} kg·m²')

    ax1.axhline(0, color='k', linestyle='--', linewidth=1)
    ax1.set_xlabel('时间 t (s)', fontsize=11)
    ax1.set_ylabel('转速 n (rpm)', fontsize=11)
    ax1.set_title('泵停机转速衰减曲线', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_xlim([0, 60])
    ax1.set_ylim([0, 1600])

    # 子图2：转速衰减率
    for i, GD2 in enumerate(GD2_array):
        T_i_var = (GD2 * pump.n0 / 60) / (2 * M_friction)
        dn_dt_var = -(pump.n0 / T_i_var) * np.exp(-t_array / T_i_var)
        ax2.plot(t_array, dn_dt_var, color=colors[i], linewidth=2,
                label=f'GD² = {GD2} kg·m²')

    ax2.axhline(0, color='k', linestyle='--', linewidth=1)
    ax2.set_xlabel('时间 t (s)', fontsize=11)
    ax2.set_ylabel('转速衰减率 dn/dt (rpm/s)', fontsize=11)
    ax2.set_title('转速衰减率', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    ax2.set_xlim([0, 60])

    plt.tight_layout()
    plt.savefig('demo2_speed_decay.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo2_speed_decay.png")
    plt.close()


# ========== 演示3：四象限运行 ==========

def demo3_four_quadrant():
    """演示3：四象限运行"""
    print_header("演示3：四象限运行")

    # 创建泵站
    pump = PumpStation(
        Q0=0.15, H0=40, n0=1450, GD2=50,
        L=800, D=0.4, a=1000,
        H_s=5, H_d=35
    )

    print("\n【四象限定义】")
    print("  第一象限：n > 0, Q > 0（正常泵送）")
    print("  第二象限：n > 0, Q < 0（泵倒转，水倒流）")
    print("  第三象限：n < 0, Q < 0（反转泵送）")
    print("  第四象限：n < 0, Q > 0（作为水轮机）")

    # 创建四象限网格
    n_range = np.linspace(-pump.n0, pump.n0, 100)
    Q_range = np.linspace(-1.5*pump.Q0, 1.5*pump.Q0, 100)
    N_grid, Q_grid = np.meshgrid(n_range, Q_range)

    # 计算扬程（简化四象限模型）
    H_grid = np.zeros_like(N_grid)
    for i in range(len(Q_range)):
        for j in range(len(n_range)):
            n = N_grid[i, j]
            Q = Q_grid[i, j]
            if abs(n) < 1e-3:
                H_grid[i, j] = 0
            else:
                n_ratio = abs(n) / pump.n0
                Q_ratio = Q / (pump.Q0 * n_ratio) if n_ratio > 1e-6 else 0
                # 简化模型
                if n > 0 and Q >= 0:  # 第一象限
                    H_grid[i, j] = pump.H0 * n_ratio**2 * (1 - 0.4 * Q_ratio**2)
                elif n > 0 and Q < 0:  # 第二象限
                    H_grid[i, j] = pump.H0 * n_ratio**2 * (1 + 0.5 * abs(Q_ratio)**1.5)
                elif n < 0 and Q < 0:  # 第三象限
                    H_grid[i, j] = -pump.H0 * n_ratio**2 * (1 - 0.4 * Q_ratio**2)
                else:  # 第四象限
                    H_grid[i, j] = -pump.H0 * n_ratio**2 * (1 + 0.5 * Q_ratio**1.5)

    # 绘图
    fig, ax = plt.subplots(figsize=(10, 9))

    # 等值线图
    levels = np.linspace(-80, 80, 17)
    contour = ax.contourf(Q_grid*1000, N_grid, H_grid,
                         levels=levels, cmap='RdBu_r', alpha=0.8)

    # 添加等值线
    contour_lines = ax.contour(Q_grid*1000, N_grid, H_grid,
                               levels=[-60, -40, -20, 0, 20, 40, 60],
                               colors='black', linewidths=1, alpha=0.5)
    ax.clabel(contour_lines, inline=True, fontsize=9, fmt='%d m')

    # 标记四个象限
    ax.text(100, 1000, '第一象限\n正常泵送', fontsize=12, ha='center',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    ax.text(-100, 1000, '第二象限\n倒流', fontsize=12, ha='center',
           bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
    ax.text(-100, -1000, '第三象限\n反转泵送', fontsize=12, ha='center',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    ax.text(100, -1000, '第四象限\n水轮机', fontsize=12, ha='center',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    # 坐标轴
    ax.axhline(0, color='k', linewidth=2)
    ax.axvline(0, color='k', linewidth=2)

    # 标记额定工况点
    ax.plot(pump.Q0*1000, pump.n0, 'ro', markersize=12, label='额定工况点')

    # 色标
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('扬程 H (m)', fontsize=11)

    ax.set_xlabel('流量 Q (L/s)', fontsize=11)
    ax.set_ylabel('转速 n (rpm)', fontsize=11)
    ax.set_title('泵四象限运行特性', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('demo3_four_quadrant.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo3_four_quadrant.png")
    plt.close()


# ========== 演示4：飞轮防护设计 ==========

def demo4_flywheel_design():
    """演示4：飞轮防护设计"""
    print_header("演示4：飞轮防护设计")

    # 创建泵站
    pump = PumpStation(
        Q0=0.15, H0=40, n0=1450, GD2=50,
        L=800, D=0.4, a=1000,
        H_s=5, H_d=35
    )

    # 计算波动周期
    T_c = 2 * pump.L / pump.a
    print("\n【管道水锤参数】")
    print_param("管道长度 L", pump.L, "m")
    print_param("波速 a", pump.a, "m/s")
    print_param("波动周期 T_c", T_c, "s")

    # 设计要求：T_i ≥ 2*T_c
    T_i_required = 2 * T_c
    print("\n【飞轮设计要求】")
    print_param("要求惯性时间 T_i", T_i_required, "s")

    # 计算所需GD²
    M0 = pump.Q0 * pump.H0 * 1000 * pump.g / (2 * np.pi * pump.n0 / 60)
    M_friction = 0.05 * M0
    GD2_required = T_i_required * 2 * M_friction / (pump.n0 / 60)

    print_param("现有 GD²", pump.GD2, "kg·m²")
    print_param("所需 GD²", GD2_required, "kg·m²")
    GD2_flywheel = max(0, GD2_required - pump.GD2)
    print_param("飞轮 GD²", GD2_flywheel, "kg·m²")

    if GD2_flywheel > 0:
        print(f"\n  需要增加飞轮：GD² = {GD2_flywheel:.1f} kg·m²")
    else:
        print(f"\n  现有惯量已满足要求")

    # 不同GD²对压力的影响（简化估算）
    GD2_array = np.array([25, 50, 100, 200, 400])
    T_i_array = (GD2_array * pump.n0 / 60) / (2 * M_friction)

    # 估算最大压力升（Joukowsky公式修正）
    # ΔH ≈ (a*v0/g) * (1 - exp(-t/T_i))
    v0 = pump.Q0 / (np.pi * (pump.D/2)**2)
    t_peak = 0.5  # 假设0.5秒后达到最大压力

    delta_H_array = []
    for T_i in T_i_array:
        factor = 1 - np.exp(-t_peak / T_i)
        delta_H = (pump.a * v0 / pump.g) * factor
        delta_H_array.append(delta_H)

    delta_H_array = np.array(delta_H_array)

    # 打印压力表
    print("\n【飞轮效果分析】")
    print(f"  {'GD² (kg·m²)':<15} {'T_i (s)':<12} {'ΔH (m)':<12} {'评价':<10}")
    print("  " + "-"*55)
    for i in range(len(GD2_array)):
        rating = "★" * min(5, int(T_i_array[i] / 1))
        print(f"  {GD2_array[i]:<15.0f} {T_i_array[i]:<12.2f} "
              f"{delta_H_array[i]:<12.2f} {rating:<10}")

    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 子图1：惯性时间vs GD²
    ax1.plot(GD2_array, T_i_array, 'b-o', linewidth=2, markersize=8,
            label='T_i(GD²)')
    ax1.axhline(T_i_required, color='r', linestyle='--', linewidth=2,
               label=f'设计要求 T_i ≥ {T_i_required:.1f}s')
    ax1.fill_between(GD2_array, 0, T_i_required, alpha=0.2, color='red')
    ax1.fill_between(GD2_array, T_i_required, T_i_array.max()*1.1,
                     alpha=0.2, color='green')
    ax1.text(100, T_i_required-0.5, '不安全区', fontsize=11, ha='center',
            color='red', fontweight='bold')
    ax1.text(300, T_i_required+2, '安全区', fontsize=11, ha='center',
            color='green', fontweight='bold')

    ax1.set_xlabel('转动惯量 GD² (kg·m²)', fontsize=11)
    ax1.set_ylabel('惯性时间常数 T_i (s)', fontsize=11)
    ax1.set_title('飞轮惯量对惯性时间的影响', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_xlim([0, 450])
    ax1.set_ylim([0, 14])

    # 子图2：压力升vs GD²
    ax2.plot(GD2_array, delta_H_array, 'r-o', linewidth=2, markersize=8,
            label='ΔH(GD²)')
    ax2.fill_between(GD2_array, 0, delta_H_array, alpha=0.2, color='red')

    ax2.set_xlabel('转动惯量 GD² (kg·m²)', fontsize=11)
    ax2.set_ylabel('最大压力升 ΔH (m)', fontsize=11)
    ax2.set_title('飞轮惯量对压力升的影响', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    ax2.set_xlim([0, 450])

    plt.tight_layout()
    plt.savefig('demo4_flywheel_design.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图形已保存：demo4_flywheel_design.png")
    plt.close()

    # 设计建议
    print("\n【设计建议】")
    print("  1. 短管道（L < 200m）：")
    print("     • GD² = 25~50 kg·m²（仅泵自身惯量）")
    print("  2. 中长管道（L = 200~800m）：")
    print("     • GD² = 100~200 kg·m²（需增加飞轮）")
    print("  3. 长管道（L > 800m）：")
    print("     • GD² > 200 kg·m²（大惯量飞轮）")
    print("     • 或配合其他防护措施（单向阀、调压塔）")


# ========== 主函数 ==========

def main():
    """主函数"""
    print("\n" + "="*70)
    print("  案例27：泵站瞬变过程")
    print("="*70)

    # 运行所有演示
    demo1_pump_characteristics()
    demo2_speed_decay()
    demo3_four_quadrant()
    demo4_flywheel_design()

    print("\n" + "="*70)
    print("  所有演示完成！")
    print("  生成文件：")
    print("    - demo1_pump_characteristics.png")
    print("    - demo2_speed_decay.png")
    print("    - demo3_four_quadrant.png")
    print("    - demo4_flywheel_design.png")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
