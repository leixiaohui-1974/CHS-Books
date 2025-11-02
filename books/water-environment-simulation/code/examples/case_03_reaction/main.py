"""
案例3：河流中的降解反应与参数率定
Degradation Reaction and Parameter Calibration

演示：
1. 不同反应级数对比（0阶、1阶、2阶、Monod）
2. 参数率定（一阶反应）
3. 温度影响分析
4. 反应-迁移耦合模型
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.reaction import ReactionKinetics
from models.reaction import ReactionTransport1D


def main():
    """主函数"""
    print("=" * 70)
    print("案例3：河流中的降解反应与参数率定")
    print("=" * 70)
    print()
    
    # ========================================
    # 任务1：不同反应级数对比
    # ========================================
    print("任务1：不同反应级数对比")
    print("-" * 70)
    
    # 参数
    C0 = 50.0  # 初始浓度 (mg/L)
    T = 50.0   # 模拟时间 (天)
    nt = 500   # 时间步数
    
    # 调整速率常数使半衰期接近
    k0 = 1.0      # 零阶 (mg/L/d)
    k1 = 0.05     # 一阶 (d⁻¹)
    k2 = 0.001    # 二阶 (L/mg/d)
    
    print(f"初始条件:")
    print(f"  初始浓度: C₀ = {C0} mg/L")
    print(f"  模拟时间: T = {T} 天")
    print()
    
    # 零阶反应
    model_0 = ReactionKinetics(T=T, nt=nt, k=k0, n=0)
    model_0.set_initial_condition(C0)
    C_zero = model_0.solve_zero_order()
    t_half_0 = C0 / (2 * k0) if k0 > 0 else np.inf
    
    print(f"零阶反应:")
    print(f"  速率常数: k₀ = {k0} mg/L/d")
    print(f"  半衰期: t₁/₂ = {t_half_0:.2f} 天")
    print()
    
    # 一阶反应
    model_1 = ReactionKinetics(T=T, nt=nt, k=k1, n=1)
    model_1.set_initial_condition(C0)
    C_first = model_1.solve_first_order()
    t_half_1 = np.log(2) / k1
    
    print(f"一阶反应:")
    print(f"  速率常数: k₁ = {k1} d⁻¹")
    print(f"  半衰期: t₁/₂ = {t_half_1:.2f} 天")
    print()
    
    # 二阶反应
    model_2 = ReactionKinetics(T=T, nt=nt, k=k2, n=2)
    model_2.set_initial_condition(C0)
    C_second = model_2.solve_second_order()
    t_half_2 = 1 / (k2 * C0)
    
    print(f"二阶反应:")
    print(f"  速率常数: k₂ = {k2} L/mg/d")
    print(f"  半衰期: t₁/₂ = {t_half_2:.2f} 天")
    print()
    
    # Monod动力学
    K_s = 10.0  # 半饱和常数 (mg/L)
    k_max = 2.0  # 最大速率 (d⁻¹)
    model_monod = ReactionKinetics(T=T, nt=nt, k=k_max, n=1)
    model_monod.set_initial_condition(C0)
    C_monod = model_monod.solve_monod(K_s=K_s)
    
    print(f"Monod动力学:")
    print(f"  最大速率: k_max = {k_max} d⁻¹")
    print(f"  半饱和常数: K_s = {K_s} mg/L")
    print()
    
    # ========================================
    # 任务2：参数率定（一阶反应）
    # ========================================
    print("任务2：参数率定（一阶反应）")
    print("-" * 70)
    
    # 模拟监测数据（带噪声）
    true_k = 0.08  # 真实速率常数
    distances = np.array([0, 5, 10, 15, 20])  # km
    velocity = 0.3  # m/s
    times = distances * 1000 / (velocity * 86400)  # 转换为天
    
    # 生成"监测数据"
    true_conc = C0 * np.exp(-true_k * times)
    noise = np.random.normal(0, 1.5, len(true_conc))
    measured_conc = true_conc + noise
    measured_conc = np.maximum(measured_conc, 0)  # 确保非负
    
    print(f"监测数据:")
    for i, (d, t, c) in enumerate(zip(distances, times, measured_conc)):
        print(f"  {d} km ({t:.2f} 天): C = {c:.2f} mg/L")
    print()
    
    # 参数率定
    model_calib = ReactionKinetics(T=times[-1], nt=100, k=0.1, n=1)
    model_calib.set_initial_condition(C0)
    
    k_fitted, C0_fitted, R2 = model_calib.fit_first_order(times, measured_conc)
    
    print(f"\n参数率定结果:")
    print(f"  拟合速率常数: k = {k_fitted:.6f} d⁻¹")
    print(f"  真实速率常数: k = {true_k:.6f} d⁻¹")
    print(f"  相对误差: {abs(k_fitted - true_k) / true_k * 100:.2f}%")
    print(f"  拟合优度: R² = {R2:.4f}")
    print(f"  半衰期: t₁/₂ = {np.log(2)/k_fitted:.2f} 天")
    print()
    
    # ========================================
    # 任务3：温度影响分析
    # ========================================
    print("任务3：温度影响分析")
    print("-" * 70)
    
    k_20 = 0.08  # 20°C时的速率常数
    theta = 1.047  # 温度系数
    
    temperatures = [10, 20, 30]
    
    print(f"温度校正 (θ = {theta}):")
    for T_water in temperatures:
        k_T = model_calib.temperature_correction(k_20, T_water, theta)
        print()
    
    # ========================================
    # 任务4：反应-迁移耦合
    # ========================================
    print("任务4：反应-迁移耦合模型")
    print("-" * 70)
    
    # 河流参数
    L_river = 50.0      # 河段长度 (km)
    u_river = 0.3       # 流速 (m/s)
    D_river = 10.0      # 扩散系数 (m²/s)
    k_river = 0.05      # 降解速率 (d⁻¹)
    
    # 转换单位
    L_m = L_river * 1000  # 转换为m
    k_s = k_river / 86400  # 转换为s⁻¹
    
    print(f"河流参数:")
    print(f"  长度: {L_river} km")
    print(f"  流速: {u_river} m/s")
    print(f"  扩散系数: {D_river} m²/s")
    print(f"  降解系数: {k_river} d⁻¹ = {k_s:.2e} s⁻¹")
    print()
    
    # 创建耦合模型
    T_sim = 200000  # 模拟时间 (s)
    nx = 200
    nt = 4000
    
    coupled_model = ReactionTransport1D(
        L=L_m, T=T_sim, nx=nx, nt=nt,
        u=u_river, D=D_river, k=k_s, n=1
    )
    
    # 初始条件：上游持续排放
    C0_river = C0
    coupled_model.set_initial_condition(0.0)
    
    # 求解
    C_coupled = coupled_model.solve(method='upwind')
    
    print(f"✓ 反应-迁移耦合模型求解完成")
    print()
    
    # 计算沿程浓度（稳态近似）
    x_river = coupled_model.x / 1000  # 转换为km
    C_steady = C_coupled[-1, :]
    
    # 理论解（稳态，纯反应）
    travel_time = x_river * 1000 / u_river  # 行程时间(s)
    travel_time_d = travel_time / 86400  # 转换为天
    C_theory_reaction = C0 * np.exp(-k_river * travel_time_d)
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 图1：不同反应级数对比
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 线性坐标
    ax1.plot(model_0.t, C_zero, 'b-', linewidth=2, label='零阶反应')
    ax1.plot(model_1.t, C_first, 'r-', linewidth=2, label='一阶反应')
    ax1.plot(model_2.t, C_second, 'g-', linewidth=2, label='二阶反应')
    ax1.plot(model_monod.t, C_monod, 'm--', linewidth=2, label='Monod动力学')
    ax1.set_xlabel('时间 t (天)', fontsize=11)
    ax1.set_ylabel('浓度 C (mg/L)', fontsize=11)
    ax1.set_title('不同反应级数对比 - 线性坐标', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, T])
    
    # 半对数坐标
    ax2.semilogy(model_0.t, C_zero, 'b-', linewidth=2, label='零阶反应')
    ax2.semilogy(model_1.t, C_first, 'r-', linewidth=2, label='一阶反应（直线）')
    ax2.semilogy(model_2.t, C_second, 'g-', linewidth=2, label='二阶反应')
    ax2.semilogy(model_monod.t, C_monod, 'm--', linewidth=2, label='Monod动力学')
    ax2.set_xlabel('时间 t (天)', fontsize=11)
    ax2.set_ylabel('浓度 C (mg/L, 对数)', fontsize=11)
    ax2.set_title('不同反应级数对比 - 半对数坐标', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, which='both')
    ax2.set_xlim([0, T])
    
    plt.tight_layout()
    plt.savefig('reaction_order_comparison.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: reaction_order_comparison.png")
    
    # 图2：参数率定
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 浓度 vs 时间
    t_fitted = np.linspace(0, times[-1], 100)
    C_fitted = C0_fitted * np.exp(-k_fitted * t_fitted)
    
    ax1.plot(times, measured_conc, 'ro', markersize=8, label='监测数据')
    ax1.plot(t_fitted, C_fitted, 'b-', linewidth=2, label=f'拟合曲线 (k={k_fitted:.4f} d⁻¹)')
    ax1.set_xlabel('时间 t (天)', fontsize=11)
    ax1.set_ylabel('浓度 C (mg/L)', fontsize=11)
    ax1.set_title('参数率定：浓度 vs 时间', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # ln(C) vs 时间（线性化）
    ln_measured = np.log(measured_conc)
    ln_fitted = np.log(C_fitted)
    
    ax2.plot(times, ln_measured, 'ro', markersize=8, label='ln(监测数据)')
    ax2.plot(t_fitted, ln_fitted, 'b-', linewidth=2, label=f'线性拟合 (R²={R2:.4f})')
    ax2.set_xlabel('时间 t (天)', fontsize=11)
    ax2.set_ylabel('ln(C)', fontsize=11)
    ax2.set_title('参数率定：对数线性化', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('parameter_calibration.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: parameter_calibration.png")
    
    # 图3：温度影响
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    T_range = np.arange(5, 35, 1)
    k_range = [model_calib.temperature_correction(k_20, T, theta) for T in T_range]
    
    ax.plot(T_range, k_range, 'b-', linewidth=2, label=f'θ = {theta}')
    ax.scatter([10, 20, 30], 
               [model_calib.temperature_correction(k_20, T, theta) for T in [10, 20, 30]],
               color='red', s=100, zorder=5, label='计算点')
    
    ax.set_xlabel('温度 T (°C)', fontsize=11)
    ax.set_ylabel('速率常数 k (d⁻¹)', fontsize=11)
    ax.set_title(f'温度对反应速率的影响 (Arrhenius方程)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('temperature_effect.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: temperature_effect.png")
    
    # 图4：反应-迁移耦合
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x_river, C_steady, 'b-', linewidth=2, label='反应-迁移耦合')
    ax.plot(x_river, C_theory_reaction, 'r--', linewidth=2, label='纯反应（无扩散）')
    ax.axhline(y=C0, color='k', linestyle=':', linewidth=1, label='初始浓度')
    
    ax.set_xlabel('距离 x (km)', fontsize=11)
    ax.set_ylabel('浓度 C (mg/L)', fontsize=11)
    ax.set_title('反应-迁移耦合模型：河流沿程浓度分布', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('reaction_transport_coupled.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: reaction_transport_coupled.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例3完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print("1. 一阶反应最常见，半衰期恒定")
    print("2. 零阶反应速率恒定，二阶反应浓度相关")
    print("3. 参数率定可通过对数线性回归实现")
    print("4. 温度显著影响反应速率（每升高10°C约增加50%）")
    print("5. 反应-迁移耦合模型更接近实际")
    print()
    print("工程应用:")
    print("  - 环境容量计算")
    print("  - 污水处理厂设计")
    print("  - 水质预测")
    print("  - 应急响应")
    print()
    print("生成的图表:")
    print("  - reaction_order_comparison.png    (反应级数对比)")
    print("  - parameter_calibration.png        (参数率定)")
    print("  - temperature_effect.png           (温度影响)")
    print("  - reaction_transport_coupled.png   (反应-迁移耦合)")
    print()
    
    plt.show()


if __name__ == '__main__':
    main()
