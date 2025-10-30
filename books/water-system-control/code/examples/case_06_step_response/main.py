#!/usr/bin/env python3
"""
案例6：阶跃响应法快速建模 - 图解法参数辨识

场景描述：
现场工程师需要快速建立水箱系统模型，但没有复杂的计算工具。
使用经典的阶跃响应图解法，通过测量系统对阶跃输入的响应曲线，
用简单的图解方法提取系统参数，无需优化算法。

教学目标：
1. 理解一阶系统阶跃响应特性
2. 掌握时间常数的图解提取方法（63.2%法、切线法）
3. 学习稳态增益的估计
4. 了解图解法的优缺点和适用场景

辨识方法：
- 63.2%法：时间常数τ对应响应达到稳态值63.2%的时刻
- 切线法：初始切线与稳态值交点对应时间常数
- 双点法：利用两个时刻的响应值计算参数

关键概念：
- 一阶系统阶跃响应
- 时间常数的物理意义
- 稳态增益
- 图解法优势

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：阶跃响应实验
# ============================================================================

def conduct_step_response_experiment():
    """
    进行阶跃响应实验，采集数据

    Returns:
        tuple: (时间, 控制输入, 水位测量, 真实参数)
    """
    print("=" * 80)
    print("案例6：阶跃响应法快速建模 - 图解法参数辨识")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：阶跃响应实验")
    print("=" * 80)

    # 真实系统参数
    A_true = 2.5
    R_true = 1.8
    K_true = 1.2

    print("\n[真实系统参数]（现场未知）")
    print(f"  横截面积 A = {A_true} m²")
    print(f"  阻力系数 R = {R_true} min/m²")
    print(f"  泵增益 K = {K_true} m³/min")
    print(f"  时间常数 τ = A × R = {A_true * R_true} 分钟")
    print(f"  稳态增益 K_dc = K × R = {K_true * R_true} m")

    # 创建真实系统
    true_system = SingleTank(A=A_true, R=R_true, K=K_true)

    # 实验：阶跃输入从0跳变到0.6
    print("\n[实验设计]")
    print("  实验类型：单位阶跃响应")
    print("  控制输入：从 u=0 跳变到 u=0.6")
    print("  初始水位：h0 = 0.5 m")
    print("  测量时长：60 分钟")

    duration = 60
    dt = 0.1
    n_steps = int(duration / dt)

    true_system.reset(h0=0.5)
    u_step = 0.6  # 阶跃幅值

    t_data = np.zeros(n_steps)
    u_data = np.ones(n_steps) * u_step
    h_data = np.zeros(n_steps)

    # 运行实验
    for i in range(n_steps):
        t_data[i] = true_system.t
        h_data[i] = true_system.h
        true_system.step(u_data[i], dt)

    # 添加少量测量噪声
    noise_level = 0.005  # 5mm
    h_noisy = h_data + np.random.normal(0, noise_level, len(h_data))

    print("\n[实验数据]")
    print(f"  初始水位：{h_noisy[0]:.3f} m")
    print(f"  最终水位：{h_noisy[-1]:.3f} m")
    print(f"  水位变化：{h_noisy[-1] - h_noisy[0]:.3f} m")
    print(f"  测量噪声：±{noise_level*1000:.1f} mm")

    true_params = {'A': A_true, 'R': R_true, 'K': K_true}

    return t_data, u_data, h_noisy, true_params, u_step, dt


# ============================================================================
# 第2部分：图解法参数辨识
# ============================================================================

def graphical_identification(t, h, u_step, h0):
    """
    使用图解法辨识参数

    Args:
        t: 时间序列
        h: 水位测量
        u_step: 阶跃幅值
        h0: 初始水位

    Returns:
        dict: 辨识参数
    """
    print("\n" + "=" * 80)
    print("第2部分：图解法参数辨识")
    print("=" * 80)

    # 方法1：63.2%法提取时间常数
    print("\n[方法1：63.2%法]")
    print("  原理：一阶系统阶跃响应在t=τ时达到稳态值的63.2%")
    print("  公式：h(τ) = h_ss × (1 - e^(-1)) ≈ 0.632 × h_ss")

    # 估计稳态值（取最后10%数据的平均值）
    h_ss = np.mean(h[-int(len(h)*0.1):])
    h_change = h_ss - h0

    # 计算63.2%对应的水位
    h_632 = h0 + 0.632 * h_change

    print(f"\n  初始水位 h0 = {h0:.3f} m")
    print(f"  稳态水位 h_ss = {h_ss:.3f} m")
    print(f"  水位变化 Δh = {h_change:.3f} m")
    print(f"  63.2%水位 = {h_632:.3f} m")

    # 找到最接近63.2%的时刻
    idx_632 = np.argmin(np.abs(h - h_632))
    tau_632 = t[idx_632]

    print(f"  时间常数 τ ≈ {tau_632:.2f} 分钟")

    # 方法2：切线法
    print("\n[方法2：切线法]")
    print("  原理：初始切线斜率 = Δh/τ")

    # 计算初始斜率（使用前5%数据拟合）
    n_initial = int(len(t) * 0.05)
    coeffs = np.polyfit(t[:n_initial], h[:n_initial], 1)
    slope_initial = coeffs[0]

    # 从初始斜率计算时间常数
    tau_tangent = h_change / slope_initial if slope_initial > 0 else tau_632

    print(f"  初始斜率 = {slope_initial:.4f} m/min")
    print(f"  时间常数 τ ≈ {tau_tangent:.2f} 分钟")

    # 方法3：双点法（更鲁棒）
    print("\n[方法3：双点法]")
    print("  原理：利用两个时刻的响应值")
    print("  公式：τ = (t2-t1) / ln((h_ss-h1)/(h_ss-h2))")

    # 选择28.3%和86.5%两个点
    h_283 = h0 + 0.283 * h_change
    h_865 = h0 + 0.865 * h_change

    idx_283 = np.argmin(np.abs(h - h_283))
    idx_865 = np.argmin(np.abs(h - h_865))

    t1, t2 = t[idx_283], t[idx_865]
    h1, h2 = h[idx_283], h[idx_865]

    if (h_ss - h1) > 0 and (h_ss - h2) > 0:
        tau_two_point = (t2 - t1) / np.log((h_ss - h1) / (h_ss - h2))
    else:
        tau_two_point = tau_632

    print(f"  点1：t={t1:.2f}分, h={h1:.3f}m (28.3%)")
    print(f"  点2：t={t2:.2f}分, h={h2:.3f}m (86.5%)")
    print(f"  时间常数 τ ≈ {tau_two_point:.2f} 分钟")

    # 综合估计（取平均值）
    tau_est = np.mean([tau_632, tau_tangent, tau_two_point])

    print("\n[时间常数综合估计]")
    print(f"  63.2%法：τ = {tau_632:.2f} 分钟")
    print(f"  切线法：τ = {tau_tangent:.2f} 分钟")
    print(f"  双点法：τ = {tau_two_point:.2f} 分钟")
    print(f"  平均值：τ = {tau_est:.2f} 分钟")

    # 估计稳态增益
    print("\n[稳态增益估计]")
    K_dc_est = h_change / u_step
    print(f"  稳态增益 K_dc = Δh / Δu = {h_change:.3f} / {u_step} = {K_dc_est:.3f} m")

    # 从τ和K_dc反推A、R、K
    print("\n[参数反推]")
    print("  假设 K = 1.0 m³/min（标准泵流量）")
    K_est = 1.0  # 假设值
    R_est = K_dc_est / K_est
    A_est = tau_est / R_est

    print(f"  阻力系数 R = K_dc / K = {K_dc_est:.3f} / {K_est} = {R_est:.3f} min/m²")
    print(f"  横截面积 A = τ / R = {tau_est:.2f} / {R_est:.3f} = {A_est:.3f} m²")

    identified_params = {
        'A': A_est,
        'R': R_est,
        'K': K_est,
        'tau': tau_est,
        'K_dc': K_dc_est,
        'methods': {
            'tau_632': tau_632,
            'tau_tangent': tau_tangent,
            'tau_two_point': tau_two_point
        }
    }

    return identified_params, h_ss


# ============================================================================
# 第3部分：模型验证
# ============================================================================

def validate_model(t, u, h_meas, identified_params, true_params, u_step, h0, dt):
    """验证辨识模型"""

    print("\n" + "=" * 80)
    print("第3部分：模型验证")
    print("=" * 80)

    # 使用辨识参数仿真
    tank_est = SingleTank(
        A=identified_params['A'],
        R=identified_params['R'],
        K=identified_params['K']
    )

    tank_est.reset(h0=h0)
    h_pred = np.zeros(len(t))

    for i in range(len(t)):
        h_pred[i] = tank_est.h
        if i < len(t) - 1:
            tank_est.step(u[i], dt)

    # 计算误差
    errors = h_pred - h_meas
    rmse = np.sqrt(np.mean(errors**2))
    mae = np.mean(np.abs(errors))
    max_error = np.max(np.abs(errors))

    ss_res = np.sum(errors**2)
    ss_tot = np.sum((h_meas - np.mean(h_meas))**2)
    r_squared = 1 - (ss_res / ss_tot)

    print("\n[1. 预测精度]")
    print(f"  RMSE = {rmse*1000:.1f} mm")
    print(f"  MAE = {mae*1000:.1f} mm")
    print(f"  最大误差 = {max_error*1000:.1f} mm")
    print(f"  R² = {r_squared:.4f} ({r_squared*100:.2f}%)")

    # 参数对比
    print("\n[2. 参数估计精度]")
    for param in ['A', 'R', 'K']:
        true_val = true_params[param]
        est_val = identified_params[param]
        error = abs(est_val - true_val) / true_val * 100

        print(f"  {param}: 真实={true_val:.3f}, 估计={est_val:.3f}, 误差={error:.2f}%")

    # 时间常数对比
    tau_true = true_params['A'] * true_params['R']
    tau_est = identified_params['tau']
    tau_error = abs(tau_est - tau_true) / tau_true * 100

    print(f"\n  时间常数 τ:")
    print(f"    真实值 = {tau_true:.2f} 分钟")
    print(f"    估计值 = {tau_est:.2f} 分钟")
    print(f"    误差 = {tau_error:.2f}%")

    print("\n[3. 图解法评价]")
    print("  优点：")
    print("    ✓ 快速简便，无需计算工具")
    print("    ✓ 物理意义清晰直观")
    print("    ✓ 适合现场快速辨识")

    print("\n  缺点：")
    print("    ✗ 精度受噪声影响较大")
    print("    ✗ 仅适用于一阶系统")
    print("    ✗ 需要稳态数据（时间较长）")

    return h_pred, {'rmse': rmse, 'r_squared': r_squared}


# ============================================================================
# 第4部分：结果可视化
# ============================================================================

def create_visualizations(t, h_meas, h_pred, u_step, h0, identified_params, true_params):
    """生成3个可视化图表"""

    print("\n" + "=" * 80)
    print("第4部分：结果可视化")
    print("=" * 80)

    h_ss = np.mean(h_meas[-int(len(h_meas)*0.1):])
    h_change = h_ss - h0

    # 图1：阶跃响应拟合
    fig1, axes = plt.subplots(2, 1, figsize=(14, 9))

    axes[0].plot(t, h_meas, 'b.', markersize=3, label='Measured Data', alpha=0.6)
    axes[0].plot(t, h_pred, 'r-', linewidth=2.5, label='Identified Model', alpha=0.9)

    # 标注关键点
    tau_632 = identified_params['methods']['tau_632']
    h_632 = h0 + 0.632 * h_change
    axes[0].axhline(h_ss, color='g', linestyle='--', linewidth=1.5,
                    label=f'Steady State ({h_ss:.3f}m)', alpha=0.7)
    axes[0].axhline(h_632, color='orange', linestyle=':', linewidth=1.5,
                    label=f'63.2% Level ({h_632:.3f}m)', alpha=0.7)
    axes[0].axvline(tau_632, color='purple', linestyle='-.', linewidth=1.5,
                    label=f'Time Constant τ={tau_632:.2f}min', alpha=0.7)

    # 标注63.2%点
    axes[0].plot(tau_632, h_632, 'ro', markersize=12, markerfacecolor='yellow',
                markeredgewidth=2, zorder=5)

    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('Case 6: Step Response Method - Graphical Parameter Identification',
                     fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, t[-1]])

    axes[1].plot(t, np.ones(len(t)) * u_step, 'g-', linewidth=2.5, alpha=0.8)
    axes[1].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('Control Input', fontsize=13, fontweight='bold')
    axes[1].set_title('Step Input', fontsize=13, fontweight='bold', pad=12)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, t[-1]])
    axes[1].set_ylim([-0.1, 1.1])

    plt.tight_layout()
    plt.savefig('step_response_fit.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图1已保存：step_response_fit.png")

    # 图2：时间常数估计方法对比
    fig2, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 方法1：63.2%法
    axes[0, 0].plot(t, h_meas, 'b-', linewidth=2, alpha=0.8)
    axes[0, 0].axhline(h_ss, color='g', linestyle='--', linewidth=1.5)
    axes[0, 0].axhline(h_632, color='orange', linestyle='--', linewidth=1.5)
    axes[0, 0].axvline(tau_632, color='r', linestyle='--', linewidth=2)
    axes[0, 0].plot(tau_632, h_632, 'ro', markersize=15, markerfacecolor='yellow',
                   markeredgewidth=2)
    axes[0, 0].annotate(f'τ = {tau_632:.2f} min',
                       xy=(tau_632, h_632), xytext=(tau_632+5, h_632-0.1),
                       fontsize=11, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', lw=2))
    axes[0, 0].set_ylabel('Water Level (m)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Method 1: 63.2% Method', fontsize=12, fontweight='bold', pad=10)
    axes[0, 0].grid(True, alpha=0.3)

    # 方法2：切线法
    tau_tangent = identified_params['methods']['tau_tangent']
    # 计算切线
    n_initial = int(len(t) * 0.05)
    coeffs = np.polyfit(t[:n_initial], h_meas[:n_initial], 1)
    tangent_line = coeffs[0] * t + coeffs[1]

    axes[0, 1].plot(t, h_meas, 'b-', linewidth=2, alpha=0.8, label='Response')
    axes[0, 1].plot(t, tangent_line, 'r--', linewidth=2, alpha=0.8, label='Initial Tangent')
    axes[0, 1].axhline(h_ss, color='g', linestyle='--', linewidth=1.5, label='Steady State')

    # 找切线与稳态值交点
    if coeffs[0] != 0:
        t_intersect = (h_ss - coeffs[1]) / coeffs[0]
        if 0 < t_intersect < t[-1]:
            axes[0, 1].plot(t_intersect, h_ss, 'ro', markersize=15,
                           markerfacecolor='yellow', markeredgewidth=2)
            axes[0, 1].annotate(f'τ = {t_intersect:.2f} min',
                               xy=(t_intersect, h_ss), xytext=(t_intersect+5, h_ss-0.2),
                               fontsize=11, fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                               arrowprops=dict(arrowstyle='->', lw=2))

    axes[0, 1].set_ylabel('Water Level (m)', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Method 2: Tangent Method', fontsize=12, fontweight='bold', pad=10)
    axes[0, 1].legend(loc='best', fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)

    # 方法3：三种方法对比柱状图
    methods = ['63.2% Method', 'Tangent Method', 'Two-Point Method']
    tau_values = [
        identified_params['methods']['tau_632'],
        identified_params['methods']['tau_tangent'],
        identified_params['methods']['tau_two_point']
    ]
    tau_true = true_params['A'] * true_params['R']

    x = np.arange(len(methods))
    bars = axes[1, 0].bar(x, tau_values, alpha=0.8, color=['steelblue', 'lightcoral', 'mediumseagreen'],
                          edgecolor='black')
    axes[1, 0].axhline(tau_true, color='r', linestyle='--', linewidth=2,
                      label=f'True Value ({tau_true:.2f}min)')

    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, tau_values)):
        height = bar.get_height()
        error = abs(val - tau_true) / tau_true * 100
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, height,
                       f'{val:.2f}\n({error:.1f}%)',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')

    axes[1, 0].set_ylabel('Time Constant τ (min)', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Comparison of Estimation Methods',
                         fontsize=12, fontweight='bold', pad=10)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(methods, fontsize=9)
    axes[1, 0].legend(loc='best', fontsize=9)
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # 理论曲线 vs 实测曲线
    # 绘制理论一阶响应曲线
    tau_est = identified_params['tau']
    K_dc_est = identified_params['K_dc']
    h_theory = h0 + K_dc_est * u_step * (1 - np.exp(-t / tau_est))

    axes[1, 1].plot(t, h_meas, 'b-', linewidth=2, alpha=0.6, label='Measured')
    axes[1, 1].plot(t, h_theory, 'r--', linewidth=2.5, alpha=0.9, label='Theoretical (1st Order)')
    axes[1, 1].set_xlabel('Time (minutes)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Water Level (m)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Theoretical vs Measured Response',
                         fontsize=12, fontweight='bold', pad=10)
    axes[1, 1].legend(loc='best', fontsize=10)
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('time_constant_estimation.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图2已保存：time_constant_estimation.png")

    # 图3：模型验证
    fig3, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 实测 vs 预测
    axes[0, 0].scatter(h_meas, h_pred, alpha=0.5, s=20)
    axes[0, 0].plot([h_meas.min(), h_meas.max()],
                    [h_meas.min(), h_meas.max()],
                    'r--', linewidth=2, label='Perfect Fit')
    axes[0, 0].set_xlabel('Measured (m)', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Predicted (m)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Predicted vs Measured', fontsize=12, fontweight='bold', pad=10)
    axes[0, 0].legend(loc='best', fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)

    # 残差时间序列
    residuals = h_pred - h_meas
    axes[0, 1].plot(t, residuals*1000, 'r-', linewidth=1.5, alpha=0.8)
    axes[0, 1].axhline(0, color='k', linestyle='--', linewidth=1)
    axes[0, 1].set_xlabel('Time (minutes)', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Residual (mm)', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Residual Time Series', fontsize=12, fontweight='bold', pad=10)
    axes[0, 1].grid(True, alpha=0.3)

    # 残差直方图
    axes[1, 0].hist(residuals*1000, bins=30, edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Residual (mm)', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Residual Distribution', fontsize=12, fontweight='bold', pad=10)
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # 参数对比
    params = ['A (m²)', 'R (min/m²)', 'K (m³/min)']
    true_vals = [true_params['A'], true_params['R'], true_params['K']]
    est_vals = [identified_params['A'], identified_params['R'], identified_params['K']]

    x = np.arange(len(params))
    width = 0.35

    bars1 = axes[1, 1].bar(x - width/2, true_vals, width, label='True',
                           alpha=0.8, color='steelblue', edgecolor='black')
    bars2 = axes[1, 1].bar(x + width/2, est_vals, width, label='Estimated',
                           alpha=0.8, color='lightcoral', edgecolor='black')

    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        h1, h2 = bar1.get_height(), bar2.get_height()
        axes[1, 1].text(bar1.get_x() + bar1.get_width()/2, h1,
                       f'{h1:.2f}', ha='center', va='bottom', fontsize=9)
        axes[1, 1].text(bar2.get_x() + bar2.get_width()/2, h2,
                       f'{h2:.2f}', ha='center', va='bottom', fontsize=9)

    axes[1, 1].set_ylabel('Parameter Value', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Parameter Estimation Results',
                         fontsize=12, fontweight='bold', pad=10)
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(params, fontsize=9)
    axes[1, 1].legend(loc='best', fontsize=10)
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('model_validation.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图3已保存：model_validation.png")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""

    # 第1部分：阶跃响应实验
    t, u, h_meas, true_params, u_step, dt = conduct_step_response_experiment()

    h0 = h_meas[0]

    # 第2部分：图解法辨识
    identified_params, h_ss = graphical_identification(t, h_meas, u_step, h0)

    # 第3部分：模型验证
    h_pred, metrics = validate_model(t, u, h_meas, identified_params,
                                     true_params, u_step, h0, dt)

    # 第4部分：可视化
    create_visualizations(t, h_meas, h_pred, u_step, h0,
                         identified_params, true_params)

    # 总结
    print("\n" + "=" * 80)
    print("案例6总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 阶跃响应法原理：")
    print("     • 一阶系统特征：h(t) = K_dc × u × (1 - e^(-t/τ))")
    print("     • 时间常数τ：达到稳态值63.2%的时刻")
    print("     • 稳态增益K_dc：稳态输出/输入比值")

    print("\n  2. 三种图解法对比：")
    print("     • 63.2%法：最直观，易于理解")
    print("     • 切线法：利用初始斜率，受噪声影响较小")
    print("     • 双点法：最鲁棒，适合有噪声的数据")

    print("\n  3. 辨识结果：")
    print(f"     • 时间常数 τ = {identified_params['tau']:.2f} 分钟")
    print(f"     • 稳态增益 K_dc = {identified_params['K_dc']:.3f} m")
    print(f"     • R² = {metrics['r_squared']:.4f} ({metrics['r_squared']*100:.2f}%)")
    print(f"     • RMSE = {metrics['rmse']*1000:.1f} mm")

    print("\n  4. 图解法评价：")
    print("     优点：")
    print("       ✓ 快速简便，无需复杂计算")
    print("       ✓ 物理意义清晰")
    print("       ✓ 适合现场快速辨识")
    print("     缺点：")
    print("       ✗ 仅适用于一阶系统")
    print("       ✗ 精度受噪声影响")
    print("       ✗ 需要等待稳态（耗时）")

    print("\n[工程应用]")
    print("  适用场景：")
    print("    • 现场快速调试")
    print("    • 教学演示")
    print("    • 初步估计（为优化算法提供初值）")

    print("\n  不适用场景：")
    print("    • 高阶系统")
    print("    • 高精度要求")
    print("    • 强噪声环境")

    print("\n[下一步学习]")
    print("  → 案例7：频域辨识技术（适用于复杂系统）")
    print("  → 案例8：递推最小二乘在线辨识（实时更新）")

    print("\n" + "=" * 80)
    print("案例6演示完成！共生成3个PNG可视化文件")
    print("=" * 80)

    png_files = [
        'step_response_fit.png',
        'time_constant_estimation.png',
        'model_validation.png'
    ]

    print("\n[生成的文件]")
    for i, filename in enumerate(png_files, 1):
        filepath = Path(filename)
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  {i}. {filename} ({size_kb:.1f} KB)")

    print("\n✓ 所有任务完成！")


if __name__ == "__main__":
    main()
