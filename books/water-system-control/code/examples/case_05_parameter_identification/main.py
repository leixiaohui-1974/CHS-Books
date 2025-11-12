#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例5：未知水箱系统参数辨识 - 最小二乘法

场景描述：
某水箱系统参数未知（横截面积A、阻力系数R、泵增益K），需要通过实验数据辨识这些参数。
采集系统在不同控制输入下的水位响应数据，使用最小二乘法估计系统参数。

教学目标：
1. 理解系统辨识的基本概念和应用场景
2. 掌握最小二乘法参数估计原理
3. 学习模型验证和残差分析方法
4. 了解参数辨识精度的评价指标

辨识方法：
- 批处理最小二乘法（Batch Least Squares）
- 数据采集：阶跃输入实验
- 参数估计：最小化预测误差平方和
- 模型验证：交叉验证

关键概念：
- 参数辨识问题
- 最小二乘法
- 模型验证
- 残差分析

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在import pyplot之前设置
import matplotlib.pyplot as plt
from scipy.optimize import least_squares, minimize
import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：真实系统模拟（生成实验数据）
# ============================================================================

def generate_experimental_data():
    """
    模拟真实水箱系统，生成实验数据

    在实际应用中，这些数据来自传感器测量。
    这里我们用已知参数的系统模拟真实系统。

    Returns:
        tuple: (时间, 控制输入, 水位测量, 真实参数)
    """
    print("=" * 80)
    print("案例5：未知水箱系统参数辨识 - 最小二乘法")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：实验数据采集")
    print("=" * 80)

    # 真实系统参数（未知，需要辨识）
    A_true = 2.5
    R_true = 1.8
    K_true = 1.2

    print("\n[真实系统参数]（在实际应用中未知）")
    print(f"  横截面积 A = {A_true} m²")
    print(f"  阻力系数 R = {R_true} min/m²")
    print(f"  泵增益 K = {K_true} m³/min")

    # 创建真实系统
    true_system = SingleTank(A=A_true, R=R_true, K=K_true)

    # 实验设计：阶跃输入
    duration = 30  # 实验时长30分钟
    dt = 0.1
    n_steps = int(duration / dt)

    # 实验1：从u=0跳变到u=0.5
    true_system.reset(h0=1.0)
    t1 = np.zeros(n_steps)
    u1 = np.ones(n_steps) * 0.5
    h1 = np.zeros(n_steps)

    for i in range(n_steps):
        t1[i] = true_system.t
        h1[i] = true_system.h
        true_system.step(u1[i], dt)

    # 实验2：从u=0跳变到u=0.8
    true_system.reset(h0=0.8)
    t2 = np.zeros(n_steps)
    u2 = np.ones(n_steps) * 0.8
    h2 = np.zeros(n_steps)

    for i in range(n_steps):
        t2[i] = true_system.t
        h2[i] = true_system.h
        true_system.step(u2[i], dt)

    # 添加测量噪声
    noise_level = 0.01  # 1cm噪声
    h1_noisy = h1 + np.random.normal(0, noise_level, len(h1))
    h2_noisy = h2 + np.random.normal(0, noise_level, len(h2))

    print("\n[实验数据采集]")
    print(f"  实验次数：2")
    print(f"  实验时长：{duration} 分钟")
    print(f"  采样间隔：{dt} 分钟")
    print(f"  数据点数：{n_steps} × 2 = {n_steps*2}")
    print(f"  测量噪声：±{noise_level*1000:.1f} mm (高斯白噪声)")

    print("\n  实验1：u = 0.5 (恒定), h0 = 1.0 m")
    print(f"    最终水位：{h1_noisy[-1]:.3f} m")

    print("\n  实验2：u = 0.8 (恒定), h0 = 0.8 m")
    print(f"    最终水位：{h2_noisy[-1]:.3f} m")

    # 合并数据用于辨识
    t_data = np.concatenate([t1, t2 + duration])
    u_data = np.concatenate([u1, u2])
    h_data = np.concatenate([h1_noisy, h2_noisy])

    true_params = {'A': A_true, 'R': R_true, 'K': K_true}

    return t_data, u_data, h_data, true_params, dt


# ============================================================================
# 第2部分：参数辨识算法
# ============================================================================

def least_squares_identification(t_data, u_data, h_data, dt):
    """
    最小二乘法参数辨识

    目标：最小化预测误差平方和
    min Σ(h_pred - h_meas)²

    Args:
        t_data: 时间数据
        u_data: 控制输入数据
        h_data: 水位测量数据
        dt: 采样间隔

    Returns:
        dict: 辨识得到的参数
    """
    print("\n" + "=" * 80)
    print("第2部分：参数辨识算法")
    print("=" * 80)

    print("\n[最小二乘法原理]")
    print("  目标函数：J = Σ(h_pred[k] - h_meas[k])²")
    print("  其中：h_pred[k] = h[k-1] + (K*u[k] - h[k-1]/R) / A * dt")
    print("  待估参数：θ = [A, R, K]")
    print("  优化方法：非线性最小二乘（Levenberg-Marquardt算法）")

    # 定义残差函数
    def residual_function(params, t, u, h_meas, dt):
        """
        计算预测值与测量值的残差

        Args:
            params: [A, R, K]
            t, u, h_meas: 数据
            dt: 采样间隔

        Returns:
            残差向量
        """
        A, R, K = params

        # 数值仿真得到预测水位
        h_pred = np.zeros(len(h_meas))
        h_pred[0] = h_meas[0]  # 初值

        for i in range(1, len(h_meas)):
            # 一阶欧拉法
            Q_in = K * u[i-1]
            Q_out = h_pred[i-1] / R if h_pred[i-1] > 0 else 0
            dh_dt = (Q_in - Q_out) / A
            h_pred[i] = h_pred[i-1] + dh_dt * dt
            h_pred[i] = max(0, h_pred[i])  # 物理约束

        # 返回残差
        return h_pred - h_meas

    # 初始猜测值
    A0 = 2.0
    R0 = 2.0
    K0 = 1.0
    initial_guess = [A0, R0, K0]

    print("\n[参数初值]")
    print(f"  A0 = {A0} m²")
    print(f"  R0 = {R0} min/m²")
    print(f"  K0 = {K0} m³/min")

    print("\n[开始优化...]")

    # 参数边界（物理约束）
    bounds = ([0.1, 0.1, 0.1], [10.0, 10.0, 5.0])

    # 执行最小二乘优化
    result = least_squares(
        residual_function,
        initial_guess,
        args=(t_data, u_data, h_data, dt),
        bounds=bounds,
        method='trf',  # Trust Region Reflective
        verbose=0
    )

    # 提取辨识结果
    A_est, R_est, K_est = result.x

    print(f"\n[辨识结果]")
    print(f"  优化成功：{result.success}")
    print(f"  迭代次数：{result.nfev}")
    print(f"  最终残差：{np.sum(result.fun**2):.6f}")

    print(f"\n[辨识参数]")
    print(f"  A_est = {A_est:.4f} m²")
    print(f"  R_est = {R_est:.4f} min/m²")
    print(f"  K_est = {K_est:.4f} m³/min")

    identified_params = {'A': A_est, 'R': R_est, 'K': K_est}

    return identified_params, result


# ============================================================================
# 第3部分：模型验证
# ============================================================================

def validate_model(t_data, u_data, h_data, identified_params, true_params, dt):
    """
    验证辨识模型的准确性

    Args:
        t_data, u_data, h_data: 实验数据
        identified_params: 辨识参数
        true_params: 真实参数
        dt: 采样间隔
    """
    print("\n" + "=" * 80)
    print("第3部分：模型验证")
    print("=" * 80)

    # 使用辨识参数仿真
    tank_est = SingleTank(
        A=identified_params['A'],
        R=identified_params['R'],
        K=identified_params['K']
    )

    # 重新仿真
    h_pred = np.zeros(len(h_data))
    h_pred[0] = h_data[0]
    tank_est.reset(h0=h_data[0])

    for i in range(1, len(h_data)):
        tank_est.step(u_data[i-1], dt)
        h_pred[i] = tank_est.h

    # 计算误差指标
    errors = h_pred - h_data
    mse = np.mean(errors**2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(errors))
    max_error = np.max(np.abs(errors))

    # 计算R²（决定系数）
    ss_res = np.sum(errors**2)
    ss_tot = np.sum((h_data - np.mean(h_data))**2)
    r_squared = 1 - (ss_res / ss_tot)

    print("\n[1. 预测精度指标]")
    print(f"  均方误差 MSE = {mse:.6f} m²")
    print(f"  均方根误差 RMSE = {rmse:.4f} m ({rmse*1000:.1f} mm)")
    print(f"  平均绝对误差 MAE = {mae:.4f} m ({mae*1000:.1f} mm)")
    print(f"  最大误差 = {max_error:.4f} m ({max_error*1000:.1f} mm)")
    print(f"  决定系数 R² = {r_squared:.6f} ({r_squared*100:.2f}%)")

    # 参数误差分析
    print("\n[2. 参数估计误差]")
    for param in ['A', 'R', 'K']:
        true_val = true_params[param]
        est_val = identified_params[param]
        abs_error = abs(est_val - true_val)
        rel_error = abs_error / true_val * 100

        print(f"  {param}:")
        print(f"    真实值：{true_val:.4f}")
        print(f"    估计值：{est_val:.4f}")
        print(f"    绝对误差：{abs_error:.4f}")
        print(f"    相对误差：{rel_error:.2f}%")

    # 模型验证结论
    print("\n[3. 模型验证结论]")
    if r_squared > 0.99:
        print(f"  ✓ 辨识模型优秀（R² = {r_squared:.4f} > 0.99）")
    elif r_squared > 0.95:
        print(f"  ✓ 辨识模型良好（R² = {r_squared:.4f} > 0.95）")
    elif r_squared > 0.90:
        print(f"  ⚠ 辨识模型一般（R² = {r_squared:.4f} > 0.90）")
    else:
        print(f"  ✗ 辨识模型较差（R² = {r_squared:.4f} < 0.90）")

    if rmse < 0.02:
        print(f"  ✓ 预测精度高（RMSE = {rmse*1000:.1f}mm < 20mm）")
    elif rmse < 0.05:
        print(f"  ⚠ 预测精度中等（RMSE = {rmse*1000:.1f}mm < 50mm）")
    else:
        print(f"  ✗ 预测精度低（RMSE = {rmse*1000:.1f}mm > 50mm）")

    return h_pred, errors, {'mse': mse, 'rmse': rmse, 'mae': mae, 'r_squared': r_squared}


# ============================================================================
# 第4部分：结果可视化
# ============================================================================

def create_visualizations(t_data, u_data, h_data, h_pred, errors,
                         identified_params, true_params):
    """生成3个可视化图表"""

    print("\n" + "=" * 80)
    print("第4部分：结果可视化")
    print("=" * 80)

    # 图1：实测 vs 辨识模型预测
    fig1, axes = plt.subplots(2, 1, figsize=(14, 9))

    axes[0].plot(t_data, h_data, 'b.', markersize=2, label='Measured Data', alpha=0.6)
    axes[0].plot(t_data, h_pred, 'r-', linewidth=2, label='Identified Model', alpha=0.9)
    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('Case 5: Parameter Identification - Model Validation',
                     fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, t_data[-1]])

    axes[1].plot(t_data, u_data, 'g-', linewidth=2, alpha=0.8)
    axes[1].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('Control Input', fontsize=13, fontweight='bold')
    axes[1].set_title('Control Input Profile', fontsize=13, fontweight='bold', pad=12)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, t_data[-1]])
    axes[1].set_ylim([-0.1, 1.1])

    plt.tight_layout()
    plt.savefig('parameter_identification.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图1已保存：parameter_identification.png")

    # 图2：残差分析
    fig2, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 残差时间序列
    axes[0, 0].plot(t_data, errors*1000, 'r-', linewidth=1.5, alpha=0.8)
    axes[0, 0].axhline(0, color='k', linestyle='--', linewidth=1)
    axes[0, 0].fill_between(t_data, -20, 20, alpha=0.15, color='green')
    axes[0, 0].set_xlabel('Time (minutes)', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Residual Error (mm)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Residual Time Series', fontsize=12, fontweight='bold', pad=10)
    axes[0, 0].grid(True, alpha=0.3, linestyle='--')

    # 残差直方图
    axes[0, 1].hist(errors*1000, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0, 1].set_xlabel('Residual Error (mm)', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Residual Distribution', fontsize=12, fontweight='bold', pad=10)
    axes[0, 1].grid(True, alpha=0.3, linestyle='--', axis='y')

    # 残差 vs 预测值
    axes[1, 0].scatter(h_pred, errors*1000, alpha=0.5, s=20)
    axes[1, 0].axhline(0, color='r', linestyle='--', linewidth=1.5)
    axes[1, 0].set_xlabel('Predicted Level (m)', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Residual Error (mm)', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Residual vs Predicted', fontsize=12, fontweight='bold', pad=10)
    axes[1, 0].grid(True, alpha=0.3, linestyle='--')

    # Q-Q图
    from scipy import stats
    stats.probplot(errors, dist="norm", plot=axes[1, 1])
    axes[1, 1].set_title('Normal Q-Q Plot', fontsize=12, fontweight='bold', pad=10)
    axes[1, 1].grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('residual_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图2已保存：residual_analysis.png")

    # 图3：参数对比
    fig3, ax = plt.subplots(1, 1, figsize=(10, 8))

    params = ['A', 'R', 'K']
    true_vals = [true_params[p] for p in params]
    est_vals = [identified_params[p] for p in params]

    x = np.arange(len(params))
    width = 0.35

    bars1 = ax.bar(x - width/2, true_vals, width, label='True Value',
                   alpha=0.8, color='steelblue', edgecolor='black')
    bars2 = ax.bar(x + width/2, est_vals, width, label='Identified Value',
                   alpha=0.8, color='lightcoral', edgecolor='black')

    # 添加数值标签
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax.text(bar1.get_x() + bar1.get_width()/2, height1,
               f'{height1:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.text(bar2.get_x() + bar2.get_width()/2, height2,
               f'{height2:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # 添加相对误差标签
        rel_error = abs(height2 - height1) / height1 * 100
        ax.text(i, max(height1, height2) * 1.15,
               f'Error: {rel_error:.2f}%', ha='center', fontsize=9,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

    ax.set_xlabel('Parameter', fontsize=13, fontweight='bold')
    ax.set_ylabel('Parameter Value', fontsize=13, fontweight='bold')
    # 标题已移除，保持图表简洁
    ax.set_xticks(x)
    ax.set_xticklabels([f'{p}\n(m² / min/m² / m³/min)'[i*15:(i+1)*15] for i, p in enumerate(params)])
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')

    plt.tight_layout()
    plt.savefig('parameter_comparison.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图3已保存：parameter_comparison.png")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""

    # 第1部分：生成实验数据
    t_data, u_data, h_data, true_params, dt = generate_experimental_data()

    # 第2部分：参数辨识
    identified_params, result = least_squares_identification(t_data, u_data, h_data, dt)

    # 第3部分：模型验证
    h_pred, errors, metrics = validate_model(t_data, u_data, h_data,
                                             identified_params, true_params, dt)

    # 第4部分：可视化
    create_visualizations(t_data, u_data, h_data, h_pred, errors,
                         identified_params, true_params)

    # 总结
    print("\n" + "=" * 80)
    print("案例5总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 系统辨识的概念：")
    print("     • 根据输入输出数据确定系统数学模型")
    print("     • 本质是参数估计问题")
    print("     • 广泛应用于控制系统设计")

    print("\n  2. 最小二乘法原理：")
    print("     • 目标：最小化预测误差平方和")
    print("     • 优化算法：Levenberg-Marquardt")
    print("     • 适用于线性和非线性系统")

    print("\n  3. 辨识精度评价：")
    print(f"     • RMSE = {metrics['rmse']*1000:.1f} mm")
    print(f"     • R² = {metrics['r_squared']:.4f} ({metrics['r_squared']*100:.2f}%)")
    print("     • 残差分析（正态性检验）")

    print("\n  4. 工程应用建议：")
    print("     • 实验设计：激励信号要充分（频率范围）")
    print("     • 数据质量：减小测量噪声影响")
    print("     • 模型验证：使用独立数据集")
    print("     • 参数约束：物理意义的边界")

    print("\n[下一步学习]")
    print("  → 案例6：阶跃响应法快速建模（图解法）")
    print("  → 案例7：频域辨识技术（Bode图法）")
    print("  → 案例8：递推最小二乘在线辨识（实时估计）")

    print("\n" + "=" * 80)
    print("案例5演示完成！共生成3个PNG可视化文件")
    print("=" * 80)

    # 列出生成的文件
    png_files = [
        'parameter_identification.png',
        'residual_analysis.png',
        'parameter_comparison.png'
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
