"""
案例23：长距离输水管道经济管径优化

问题描述：
某城市需从远处水源引水，已知：
- 输水距离 L = 50 km (50000 m)
- 设计流量 Q = 2.0 m³/s
- 高程差 Δz = 50 m
- 管道摩阻系数 λ = 0.020
- 运行时间 T = 7000 h/年
- 设计年限 n = 30年
- 折现率 r = 7%
- 电价 C_e = 0.6 元/kWh
- 泵站效率 η = 0.75

求解：
1. 不同管径下的建设费用和运行费用
2. 总费用净现值(NPV)最小的经济管径
3. 敏感性分析（电价、流量变化的影响）
4. 可视化经济分析曲线

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


# ==================== 经济分析函数 ====================

def pipe_velocity(Q, D):
    """计算管道流速 [m/s]"""
    v = 4 * Q / (np.pi * D**2)
    return v


def darcy_head_loss_total(lambda_f, L, D, Q, g=9.81):
    """计算总沿程损失（达西公式）[m]"""
    v = pipe_velocity(Q, D)
    h_f = lambda_f * (L / D) * (v**2 / (2 * g))
    return h_f


def pump_head(delta_z, h_f, h_m=0):
    """计算泵站扬程 [m]
    H = Δz + h_f + h_m
    """
    H = delta_z + h_f + h_m
    return H


def pump_power(rho, g, Q, H, eta):
    """计算泵站功率 [kW]
    P = (ρ × g × Q × H) / (1000 × η)
    """
    P = (rho * g * Q * H) / (1000 * eta)
    return P


def annual_operation_cost(C_e, P, T):
    """计算年运行费用 [万元]
    C_annual = 电价 × 功率 × 运行小时 / 10000
    """
    C_annual = C_e * P * T / 10000  # 转换为万元
    return C_annual


def construction_cost_pipe(k, D, a, L):
    """计算管道建设费用 [万元]
    C = k × D^a × L
    """
    C = k * (D**a) * L
    return C


def total_cost_npv(C_construction, C_annual, n, r=0.07):
    """计算总费用净现值 [万元]
    NPV = C_construction + C_annual × PV_factor
    PV_factor = [(1+r)^n - 1] / [r(1+r)^n]
    """
    if r == 0:
        PV_factor = n
    else:
        PV_factor = ((1 + r)**n - 1) / (r * (1 + r)**n)

    NPV = C_construction + C_annual * PV_factor
    return NPV


def economic_diameter_formula(Q):
    """经济管径经验公式 [m]
    D = 1.13 × Q^0.45
    """
    D_econ = 1.13 * Q**0.45
    return D_econ


def economic_velocity_formula(Q):
    """经济流速经验公式 [m/s]
    v = 1.1 × Q^0.4
    """
    v_econ = 1.1 * Q**0.4
    return v_econ


# ==================== 可视化函数 ====================

def plot_cost_vs_diameter(D_array, C_constr, C_oper_pv, C_total,
                         D_optimal, save_path='cost_vs_diameter.png'):
    """绘制费用-管径关系曲线"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 子图1：各项费用vs管径
    ax1.plot(D_array, C_constr, 'b-', linewidth=2, label='建设费用')
    ax1.plot(D_array, C_oper_pv, 'r-', linewidth=2, label='运行费用现值')
    ax1.plot(D_array, C_total, 'g-', linewidth=3, label='总费用NPV')

    # 标注最优点
    idx_optimal = np.argmin(C_total)
    ax1.plot(D_optimal, C_total[idx_optimal], 'ro', markersize=12,
            label=f'最优点 D={D_optimal:.2f}m')
    ax1.axvline(x=D_optimal, color='orange', linestyle='--', linewidth=2,
               alpha=0.7)

    ax1.set_xlabel('管径 D (m)', fontsize=12)
    ax1.set_ylabel('费用 (万元)', fontsize=12)
    ax1.set_title('各项费用 vs 管径', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=11)

    # 子图2：费用组成比例（堆叠面积图）
    ax2.fill_between(D_array, 0, C_constr, alpha=0.5, color='blue',
                    label='建设费用')
    ax2.fill_between(D_array, C_constr, C_constr + C_oper_pv,
                    alpha=0.5, color='red', label='运行费用现值')
    ax2.plot(D_array, C_total, 'k-', linewidth=3, label='总费用')

    # 标注最优点
    ax2.plot(D_optimal, C_total[idx_optimal], 'ro', markersize=12)
    ax2.axvline(x=D_optimal, color='orange', linestyle='--', linewidth=2,
               alpha=0.7, label=f'最优管径 D={D_optimal:.2f}m')

    ax2.set_xlabel('管径 D (m)', fontsize=12)
    ax2.set_ylabel('费用 (万元)', fontsize=12)
    ax2.set_title('费用组成与最优管径', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ 费用-管径曲线图已保存: {save_path}")


def plot_sensitivity_analysis(save_path='sensitivity_analysis.png'):
    """绘制敏感性分析图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 基准参数
    Q_base = 2.0
    C_e_base = 0.6
    L = 50000
    delta_z = 50
    lambda_f = 0.02
    n = 30
    r = 0.07
    T = 7000
    eta = 0.75
    rho = 1000
    g = 9.81

    # 管径范围
    D_array = np.linspace(0.8, 2.5, 50)

    # 敏感性分析1：不同电价
    C_e_values = [0.4, 0.6, 0.8, 1.0]
    colors_e = ['blue', 'green', 'orange', 'red']

    for C_e, color in zip(C_e_values, colors_e):
        C_total = []
        for D in D_array:
            # 建设费用
            k = 15  # 单位造价系数
            a = 1.5
            C_constr = construction_cost_pipe(k, D, a, L)

            # 运行费用
            h_f = darcy_head_loss_total(lambda_f, L, D, Q_base, g)
            h_m = 0.1 * h_f
            H = pump_head(delta_z, h_f, h_m)
            P = pump_power(rho, g, Q_base, H, eta)
            C_annual = annual_operation_cost(C_e, P, T)
            C_oper_pv = C_annual * (((1 + r)**n - 1) / (r * (1 + r)**n))

            C_total.append(C_constr + C_oper_pv)

        ax1.plot(D_array, C_total, color=color, linewidth=2,
                label=f'电价={C_e}元/kWh')

        # 标注最优点
        idx_opt = np.argmin(C_total)
        ax1.plot(D_array[idx_opt], C_total[idx_opt], 'o', color=color,
                markersize=8)

    ax1.set_xlabel('管径 D (m)', fontsize=12)
    ax1.set_ylabel('总费用NPV (万元)', fontsize=12)
    ax1.set_title('敏感性分析：电价变化影响', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)

    # 敏感性分析2：不同流量
    Q_values = [1.5, 2.0, 2.5, 3.0]
    colors_q = ['blue', 'green', 'orange', 'red']

    for Q, color in zip(Q_values, colors_q):
        C_total = []
        for D in D_array:
            # 建设费用
            k = 15
            a = 1.5
            C_constr = construction_cost_pipe(k, D, a, L)

            # 运行费用
            h_f = darcy_head_loss_total(lambda_f, L, D, Q, g)
            h_m = 0.1 * h_f
            H = pump_head(delta_z, h_f, h_m)
            P = pump_power(rho, g, Q, H, eta)
            C_annual = annual_operation_cost(C_e_base, P, T)
            C_oper_pv = C_annual * (((1 + r)**n - 1) / (r * (1 + r)**n))

            C_total.append(C_constr + C_oper_pv)

        ax2.plot(D_array, C_total, color=color, linewidth=2,
                label=f'Q={Q}m³/s')

        # 标注最优点
        idx_opt = np.argmin(C_total)
        ax2.plot(D_array[idx_opt], C_total[idx_opt], 'o', color=color,
                markersize=8)

    ax2.set_xlabel('管径 D (m)', fontsize=12)
    ax2.set_ylabel('总费用NPV (万元)', fontsize=12)
    ax2.set_title('敏感性分析：流量变化影响', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 敏感性分析图已保存: {save_path}")


def plot_velocity_and_power(D_array, v_array, P_array,
                           save_path='velocity_power_analysis.png'):
    """绘制流速和功率分析图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 子图1：流速vs管径
    ax1.plot(D_array, v_array, 'b-', linewidth=2, label='流速')
    ax1.axhline(y=0.6, color='orange', linestyle='--', linewidth=1.5,
               label='最小流速限制 (0.6 m/s)')
    ax1.axhline(y=3.0, color='red', linestyle='--', linewidth=1.5,
               label='最大流速限制 (3.0 m/s)')

    # 合理流速区间
    ax1.fill_between(D_array, 0.6, 3.0, alpha=0.2, color='green',
                    label='合理流速区间')

    ax1.set_xlabel('管径 D (m)', fontsize=12)
    ax1.set_ylabel('流速 v (m/s)', fontsize=12)
    ax1.set_title('流速 vs 管径', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)

    # 子图2：泵站功率vs管径
    ax2.plot(D_array, P_array, 'r-', linewidth=2, label='泵站功率')

    ax2.set_xlabel('管径 D (m)', fontsize=12)
    ax2.set_ylabel('泵站功率 P (kW)', fontsize=12)
    ax2.set_title('泵站功率 vs 管径', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 流速功率分析图已保存: {save_path}")


# ==================== 主程序 ====================

def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def main():
    """主函数"""
    print_separator("案例23：长距离输水管道经济管径优化")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    # 基本参数
    L = 50000       # 输水距离 (m)
    Q = 2.0         # 设计流量 (m³/s)
    delta_z = 50    # 高程差 (m)
    lambda_f = 0.02 # 摩阻系数
    g = 9.81        # 重力加速度 (m/s²)

    # 经济参数
    n = 30          # 设计年限 (年)
    r = 0.07        # 折现率
    T = 7000        # 年运行时间 (小时)
    C_e = 0.6       # 电价 (元/kWh)
    eta = 0.75      # 泵站效率
    rho = 1000      # 水密度 (kg/m³)

    # 管道造价参数
    k = 15          # 单位造价系数 (万元/m^a/m)
    a = 1.5         # 管径指数

    print(f"输水工程参数：")
    print(f"  输水距离 L = {L/1000} km")
    print(f"  设计流量 Q = {Q} m³/s")
    print(f"  高程差 Δz = {delta_z} m")
    print(f"  摩阻系数 λ = {lambda_f}")

    print(f"\n经济参数：")
    print(f"  设计年限 n = {n} 年")
    print(f"  折现率 r = {r*100}%")
    print(f"  年运行时间 T = {T} h")
    print(f"  电价 Ce = {C_e} 元/kWh")
    print(f"  泵站效率 η = {eta*100}%")

    print(f"\n管道造价：")
    print(f"  建设费用 = {k} × D^{a} × L (万元)")

    # ==================== 第二步：经验公式估算 ====================
    print("\n【步骤2】经验公式初步估算")
    print("-" * 80)

    D_econ_formula = economic_diameter_formula(Q)
    v_econ_formula = economic_velocity_formula(Q)

    print(f"经验公式估算：")
    print(f"  经济管径 D = 1.13 × Q^0.45 = {D_econ_formula:.3f} m")
    print(f"  经济流速 v = 1.1 × Q^0.4 = {v_econ_formula:.3f} m/s")

    # ==================== 第三步：优化计算 ====================
    print("\n【步骤3】精确优化计算")
    print("-" * 80)

    # 管径范围：0.8m到2.5m
    D_array = np.linspace(0.8, 2.5, 100)

    # 计算各管径下的费用
    C_constr_array = []      # 建设费用
    C_annual_array = []      # 年运行费用
    C_oper_pv_array = []     # 运行费用现值
    C_total_array = []       # 总费用NPV
    v_array = []             # 流速
    P_array = []             # 泵站功率

    for D in D_array:
        # 建设费用
        C_constr = construction_cost_pipe(k, D, a, L)
        C_constr_array.append(C_constr)

        # 水头损失
        h_f = darcy_head_loss_total(lambda_f, L, D, Q, g)
        h_m = 0.1 * h_f  # 局部损失按10%估算

        # 泵站扬程
        H = pump_head(delta_z, h_f, h_m)

        # 泵站功率
        P = pump_power(rho, g, Q, H, eta)
        P_array.append(P)

        # 年运行费用
        C_annual = annual_operation_cost(C_e, P, T)
        C_annual_array.append(C_annual)

        # 运行费用现值
        PV_factor = ((1 + r)**n - 1) / (r * (1 + r)**n)
        C_oper_pv = C_annual * PV_factor
        C_oper_pv_array.append(C_oper_pv)

        # 总费用NPV
        C_total = total_cost_npv(C_constr, C_annual, n, r)
        C_total_array.append(C_total)

        # 流速
        v = pipe_velocity(Q, D)
        v_array.append(v)

    # 转换为numpy数组
    C_constr_array = np.array(C_constr_array)
    C_annual_array = np.array(C_annual_array)
    C_oper_pv_array = np.array(C_oper_pv_array)
    C_total_array = np.array(C_total_array)
    v_array = np.array(v_array)
    P_array = np.array(P_array)

    # 找到最优管径
    idx_optimal = np.argmin(C_total_array)
    D_optimal = D_array[idx_optimal]
    C_optimal = C_total_array[idx_optimal]
    v_optimal = v_array[idx_optimal]
    P_optimal = P_array[idx_optimal]

    print(f"优化结果：")
    print(f"  最优管径：D = {D_optimal:.3f} m")
    print(f"  对应流速：v = {v_optimal:.3f} m/s")
    print(f"  泵站功率：P = {P_optimal:.1f} kW")
    print(f"  最小总费用：NPV = {C_optimal:.2f} 万元")

    print(f"\n费用组成（D = {D_optimal:.3f} m）：")
    print(f"  建设费用：{C_constr_array[idx_optimal]:.2f} 万元 ({C_constr_array[idx_optimal]/C_optimal*100:.1f}%)")
    print(f"  运行费用现值：{C_oper_pv_array[idx_optimal]:.2f} 万元 ({C_oper_pv_array[idx_optimal]/C_optimal*100:.1f}%)")
    print(f"  年运行费用：{C_annual_array[idx_optimal]:.2f} 万元/年")

    # ==================== 第四步：与经验公式对比 ====================
    print("\n【步骤4】与经验公式对比")
    print("-" * 80)

    diff_percent = abs(D_optimal - D_econ_formula) / D_econ_formula * 100

    print(f"优化计算管径：D = {D_optimal:.3f} m")
    print(f"经验公式管径：D = {D_econ_formula:.3f} m")
    print(f"相对误差：{diff_percent:.1f}%")

    if diff_percent < 10:
        print(f"✓ 经验公式估算准确度较高")
    else:
        print(f"⚠ 经验公式与实际优化结果差异较大，应以优化计算为准")

    # ==================== 第五步：设计校核 ====================
    print("\n【步骤5】设计校核")
    print("-" * 80)

    print(f"流速校核：")
    if 0.6 <= v_optimal <= 3.0:
        print(f"  ✓ 流速 v = {v_optimal:.3f} m/s 在合理范围 [0.6, 3.0] m/s")
    elif v_optimal < 0.6:
        print(f"  ✗ 流速过小 v = {v_optimal:.3f} m/s < 0.6 m/s，可能淤积")
    else:
        print(f"  ✗ 流速过大 v = {v_optimal:.3f} m/s > 3.0 m/s，增加损失")

    print(f"\n工程实施建议：")
    D_standard = np.ceil(D_optimal * 10) / 10  # 向上取整到0.1m
    print(f"  建议采用标准管径：D = {D_standard} m")

    # 重新计算标准管径下的费用
    h_f_std = darcy_head_loss_total(lambda_f, L, D_standard, Q, g)
    h_m_std = 0.1 * h_f_std
    H_std = pump_head(delta_z, h_f_std, h_m_std)
    P_std = pump_power(rho, g, Q, H_std, eta)
    C_constr_std = construction_cost_pipe(k, D_standard, a, L)
    C_annual_std = annual_operation_cost(C_e, P_std, T)
    C_total_std = total_cost_npv(C_constr_std, C_annual_std, n, r)
    v_std = pipe_velocity(Q, D_standard)

    print(f"  标准管径费用：NPV = {C_total_std:.2f} 万元")
    print(f"  费用增加：{C_total_std - C_optimal:.2f} 万元 ({(C_total_std-C_optimal)/C_optimal*100:.2f}%)")
    print(f"  标准管径流速：v = {v_std:.3f} m/s")

    # ==================== 第六步：生成可视化 ====================
    print("\n【步骤6】生成可视化图形")
    print("-" * 80)

    print("正在生成可视化图形...")

    # 图1：费用-管径曲线
    plot_cost_vs_diameter(D_array, C_constr_array, C_oper_pv_array,
                         C_total_array, D_optimal,
                         'cost_vs_diameter.png')

    # 图2：敏感性分析
    plot_sensitivity_analysis('sensitivity_analysis.png')

    # 图3：流速和功率分析
    plot_velocity_and_power(D_array, v_array, P_array,
                           'velocity_power_analysis.png')

    # ==================== 第七步：经济分析总结 ====================
    print("\n【步骤7】经济分析总结")
    print("-" * 80)

    print(f"1. 最优设计方案：")
    print(f"   - 推荐管径：D = {D_standard} m（标准管径）")
    print(f"   - 设计流速：v = {v_std:.2f} m/s")
    print(f"   - 泵站功率：P = {P_std:.1f} kW")

    print(f"\n2. 投资估算：")
    print(f"   - 建设投资：{C_constr_std:.2f} 万元")
    print(f"   - 年运行费用：{C_annual_std:.2f} 万元")
    print(f"   - {n}年总费用NPV：{C_total_std:.2f} 万元")

    print(f"\n3. 敏感性分析结论：")
    print(f"   - 电价对经济管径影响显著")
    print(f"   - 流量增大时，经济管径相应增大")
    print(f"   - 建议在设计时考虑远期流量增长")

    print(f"\n4. 节能潜力分析：")
    # 与最小管径(1.0m)对比
    D_small = 1.0
    h_f_small = darcy_head_loss_total(lambda_f, L, D_small, Q, g)
    h_m_small = 0.1 * h_f_small
    H_small = pump_head(delta_z, h_f_small, h_m_small)
    P_small = pump_power(rho, g, Q, H_small, eta)
    energy_saving = (P_small - P_std) * T  # kWh/年
    cost_saving_annual = energy_saving * C_e / 10000  # 万元/年

    print(f"   相比小管径方案（D={D_small}m）：")
    print(f"   - 年节约电能：{energy_saving:.0f} kWh")
    print(f"   - 年节约费用：{cost_saving_annual:.2f} 万元")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("✓ 计算完成！所有可视化图形已保存。")
    print("="*80 + "\n")

    return {
        'D_optimal': D_optimal,
        'D_standard': D_standard,
        'C_total': C_total_std,
        'P': P_std
    }


if __name__ == "__main__":
    results = main()
