#!/usr/bin/env python3
"""
案例21可执行示例：管道流水力计算与Moody图可视化

本示例展示：
1. Darcy-Weisbach公式计算管道水头损失
2. Colebrook-White方程迭代求解摩阻系数
3. Reynolds数计算
4. Moody图绘制与分析

运行方式：
    python main.py

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ========== 水力计算函数 ==========

def reynolds_number(v, D, nu):
    """计算Reynolds数"""
    Re = v * D / nu
    return Re


def darcy_friction_factor_laminar(Re):
    """层流摩阻系数"""
    lambda_f = 64 / Re
    return lambda_f


def colebrook_white(Re, epsilon_D, tol=1e-6, max_iter=100):
    """Colebrook-White方程求解摩阻系数（迭代法）

    1/√λ = -2.0*log₁₀(ε/(3.7D) + 2.51/(Re√λ))
    """
    if Re < 2320:
        return darcy_friction_factor_laminar(Re)

    # 初始猜测（Swamee-Jain公式）
    lambda_f = 0.25 / (np.log10(epsilon_D/3.7 + 5.74/Re**0.9))**2

    for i in range(max_iter):
        sqrt_lambda = np.sqrt(lambda_f)
        # Colebrook-White方程
        f_val = 1/sqrt_lambda + 2.0 * np.log10(epsilon_D/3.7 + 2.51/(Re*sqrt_lambda))

        if abs(f_val) < tol:
            return lambda_f

        # Newton-Raphson更新
        df_dlambda = -0.5 / (lambda_f**1.5) - 2.0 * 0.4343 * 2.51 / (2 * Re * lambda_f**1.5)
        lambda_f_new = lambda_f - f_val / df_dlambda

        # 限制范围
        lambda_f = max(0.008, min(lambda_f_new, 0.1))

    return lambda_f


def darcy_head_loss(lambda_f, L, D, v, g=9.81):
    """Darcy-Weisbach公式计算水头损失"""
    h_f = lambda_f * (L/D) * (v**2 / (2*g))
    return h_f


def swamee_jain(Re, epsilon_D):
    """Swamee-Jain显式公式"""
    lambda_f = 0.25 / (np.log10(epsilon_D/3.7 + 5.74/Re**0.9))**2
    return lambda_f


# ========== 格式化输出函数 ==========

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


# ========== Moody图绘制函数 ==========

def plot_moody_diagram(save_path='moody_diagram.png'):
    """绘制Moody图"""

    # Reynolds数范围（对数坐标）
    Re_array = np.logspace(2, 8, 500)

    # 相对粗糙度数组
    epsilon_D_array = [0, 0.00001, 0.00005, 0.0001, 0.0002, 0.0005,
                       0.001, 0.002, 0.005, 0.01, 0.02, 0.05]

    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))

    # 绘制层流区
    Re_laminar = np.logspace(2, 3.5, 100)
    lambda_laminar = 64 / Re_laminar
    ax.loglog(Re_laminar, lambda_laminar, 'k--', linewidth=2,
             label='层流：λ=64/Re')

    # 绘制不同粗糙度的曲线
    colors = plt.cm.viridis(np.linspace(0, 1, len(epsilon_D_array)))

    for i, eps_D in enumerate(epsilon_D_array):
        lambda_array = []
        Re_turbulent = []

        for Re in Re_array:
            if Re > 2320:  # 湍流区
                lambda_f = colebrook_white(Re, eps_D, tol=1e-4)
                lambda_array.append(lambda_f)
                Re_turbulent.append(Re)

        if len(Re_turbulent) > 0:
            if eps_D == 0:
                label = '光滑管'
            else:
                label = f'ε/D = {eps_D}'
            ax.loglog(Re_turbulent, lambda_array, color=colors[i],
                     linewidth=1.5, label=label)

    # 过渡区标注
    ax.axvspan(2320, 4000, alpha=0.2, color='yellow',
              label='过渡区')

    # 图形设置
    ax.set_xlabel('Reynolds数 Re', fontsize=12, fontweight='bold')
    ax.set_ylabel('摩阻系数 λ', fontsize=12, fontweight='bold')
    ax.set_title('Moody图（明渠水力学教材）', fontsize=14, fontweight='bold')
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    ax.set_xlim([1e2, 1e8])
    ax.set_ylim([0.008, 0.1])

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n  ✓ Moody图已保存至：{save_path}")
    plt.close()


def main():
    """主函数"""

    print_header("案例21：管道流水力计算")

    # ========== 输入参数 ==========
    print("\n【输入参数】")
    D = 0.3        # 管径 (m)
    L = 500        # 管道长度 (m)
    Q = 0.15       # 流量 (m³/s)
    epsilon = 0.00015  # 绝对粗糙度 (m，混凝土管)
    nu = 1.0e-6    # 运动粘度 (m²/s，20°C清水)
    g = 9.81       # 重力加速度 (m/s²)

    print_param("管径 D", D, "m")
    print_param("管道长度 L", L, "m")
    print_param("流量 Q", Q, "m³/s")
    print_param("绝对粗糙度 ε", epsilon, "m")
    print_param("相对粗糙度 ε/D", epsilon/D, "")
    print_param("运动粘度 ν", nu, "m²/s")
    print(f"\n  管道材料: 混凝土管")
    print(f"  水温: 20°C")

    # ========== 计算流速和Reynolds数 ==========
    print_header("流速与Reynolds数")

    A = np.pi * D**2 / 4
    v = Q / A
    Re = reynolds_number(v, D, nu)

    print("\n【基本参数】")
    print_param("断面积 A", A, "m²")
    print_param("流速 v", v, "m/s")
    print_param("Reynolds数 Re", Re, "")

    # 判断流态
    if Re < 2320:
        flow_regime = "层流"
    elif Re < 4000:
        flow_regime = "过渡流"
    else:
        flow_regime = "湍流"

    print_param("流态", flow_regime, "")

    # ========== 计算摩阻系数 ==========
    print_header("摩阻系数计算")

    epsilon_D = epsilon / D

    print("\n【Colebrook-White方程迭代求解】")
    lambda_f = colebrook_white(Re, epsilon_D)
    print_param("摩阻系数 λ (迭代法)", lambda_f, "")

    print("\n【Swamee-Jain显式公式】")
    lambda_sj = swamee_jain(Re, epsilon_D)
    print_param("摩阻系数 λ (Swamee-Jain)", lambda_sj, "")

    print("\n【对比分析】")
    error = abs(lambda_sj - lambda_f) / lambda_f * 100
    print_param("两种方法相对误差", error, "%")

    if error < 1.0:
        print("  ✓ 两种方法结果吻合良好")

    # ========== 计算水头损失 ==========
    print_header("水头损失计算")

    h_f = darcy_head_loss(lambda_f, L, D, v, g)
    h_f_per_100m = h_f / L * 100

    print("\n【Darcy-Weisbach公式】")
    print(f"  h_f = λ × (L/D) × (v²/2g)")
    print(f"  h_f = {lambda_f:.6f} × ({L}/{D}) × ({v:.4f}²/(2×{g}))")

    print("\n【计算结果】")
    print_param("总水头损失 h_f", h_f, "m")
    print_param("单位长度损失 i", h_f/L, "m/m")
    print_param("每100m损失", h_f_per_100m, "m")

    # ========== 压力损失 ==========
    print_header("压力分析")

    rho = 1000  # 水的密度 (kg/m³)
    delta_p = rho * g * h_f

    print("\n【压力损失】")
    print_param("压力损失 Δp", delta_p, "Pa")
    print_param("压力损失 Δp", delta_p/1000, "kPa")
    print_param("压力损失 Δp", delta_p/1e5, "bar")

    # ========== 功率损失 ==========
    print_header("功率损失")

    P_loss = rho * g * Q * h_f

    print("\n【能量损耗】")
    print_param("功率损失 P", P_loss, "W")
    print_param("功率损失 P", P_loss/1000, "kW")

    if L > 0:
        P_per_km = P_loss / L * 1000
        print_param("每公里功率损失", P_per_km/1000, "kW/km")

    # ========== 工程校核 ==========
    print_header("工程校核")

    print("\n【流速校核】")
    v_min = 0.6   # 最小流速 (m/s)
    v_max = 3.0   # 最大流速 (m/s)

    print_param("计算流速", v, "m/s")
    print_param("最小流速", v_min, "m/s")
    print_param("最大流速", v_max, "m/s")

    if v_min <= v <= v_max:
        print("  ✓ 流速在合理范围内")
    else:
        print("  ✗ 流速超出推荐范围")

    print("\n【水头损失校核】")
    i_max = 0.01  # 最大允许水力坡度
    i_calc = h_f / L

    print_param("计算水力坡度 i", i_calc, "")
    print_param("允许水力坡度 i_max", i_max, "")

    if i_calc <= i_max:
        print("  ✓ 水力坡度在允许范围内")
    else:
        print("  ✗ 水力坡度过大，建议增大管径")

    # ========== 生成Moody图 ==========
    print_header("Moody图生成")

    print("\n  正在绘制Moody图...")
    plot_moody_diagram('moody_diagram.png')

    # 在图上标记当前工况点
    fig, ax = plt.subplots(figsize=(12, 8))

    # 绘制简化Moody图
    Re_array = np.logspace(2, 8, 500)
    lambda_array = [colebrook_white(r, epsilon_D, tol=1e-4) for r in Re_array if r > 2320]
    Re_turbulent = [r for r in Re_array if r > 2320]

    ax.loglog(Re_turbulent, lambda_array, 'b-', linewidth=2, label=f'ε/D={epsilon_D:.6f}')

    # 标记当前工况
    ax.plot(Re, lambda_f, 'ro', markersize=12, label=f'当前工况\nRe={Re:.0f}\nλ={lambda_f:.6f}')

    # 图形设置
    ax.set_xlabel('Reynolds数 Re', fontsize=12, fontweight='bold')
    ax.set_ylabel('摩阻系数 λ', fontsize=12, fontweight='bold')
    ax.set_title(f'当前管道工况点 (D={D}m, Q={Q}m³/s)', fontsize=14, fontweight='bold')
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig('current_operating_point.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 工况点图已保存至：current_operating_point.png")
    plt.close()

    # ========== 工程建议 ==========
    print_header("工程建议")

    print("\n  1. 管道设计参数：")
    print(f"     • 管径：D = {D} m = {D*1000:.0f} mm")
    print(f"     • 长度：L = {L} m")
    print(f"     • 材料：混凝土管（ε = {epsilon*1000:.2f} mm）")

    print("\n  2. 水力特性：")
    print(f"     • 流量：Q = {Q:.3f} m³/s = {Q*1000:.1f} L/s")
    print(f"     • 流速：v = {v:.2f} m/s")
    print(f"     • Reynolds数：Re = {Re:.0f} ({flow_regime})")
    print(f"     • 摩阻系数：λ = {lambda_f:.6f}")

    print("\n  3. 损失分析：")
    print(f"     • 总水头损失：h_f = {h_f:.2f} m")
    print(f"     • 每100m损失：{h_f_per_100m:.2f} m")
    print(f"     • 功率损失：P = {P_loss/1000:.2f} kW")

    print("\n  4. 优化建议：")
    if i_calc > 0.005:
        D_opt = D * 1.1
        print(f"     • 建议增大管径至 {D_opt*1000:.0f} mm")
    else:
        print(f"     • 当前管径合理")

    print("\n" + "="*70)
    print("  计算完成！")
    print("  生成文件：moody_diagram.png, current_operating_point.png")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
