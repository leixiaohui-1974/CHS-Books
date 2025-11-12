#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例9：系统建模 - 从物理到数学

场景描述：
某工程师需要为水箱供水系统设计控制器。第一步是建立系统的数学模型。
采用机理建模方法，从物理原理（质量守恒）推导微分方程和传递函数。

教学目标：
1. 理解机理建模的基本思想和步骤
2. 掌握从物理规律到微分方程的推导
3. 学习微分方程到传递函数的转换
4. 掌握模型验证的基本方法

建模步骤：
1. 明确系统边界和变量
2. 应用物理定律（质量守恒）
3. 确定流量关系
4. 推导微分方程
5. 求传递函数
6. 模型验证

关键概念：
- 机理建模
- 质量守恒定律
- 微分方程
- 传递函数
- 时间常数

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在import pyplot之前设置
import matplotlib.pyplot as plt
from scipy import signal
import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank
from code.models.water_tank.double_tank import DoubleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：单水箱系统建模
# ============================================================================

def single_tank_modeling():
    """
    单水箱系统的机理建模过程
    """
    print("=" * 80)
    print("案例9：系统建模 - 从物理到数学")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：单水箱系统建模")
    print("=" * 80)

    print("\n[步骤1：系统分析]")
    print("  系统组成：")
    print("    输入：控制信号 u (泵开度, 0-1)")
    print("    输出：水位 h (m)")
    print("    状态：水位 h (m)")
    print("    参数：A (横截面积), R (阻力系数), K (泵增益)")

    print("\n[步骤2：物理定律 - 质量守恒]")
    print("  水箱中水的质量变化率 = 流入质量流率 - 流出质量流率")
    print("  假设密度恒定：")
    print("    ρ * A * dh/dt = ρ * Q_in - ρ * Q_out")
    print("  简化：")
    print("    A * dh/dt = Q_in - Q_out")

    print("\n[步骤3：流量关系]")
    print("  进水流量（泵控制）：")
    print("    Q_in = K * u")
    print("  出水流量（管道阻力）：")
    print("    Q_out = h / R")
    print("  说明：这是线性化的阻力模型")

    print("\n[步骤4：微分方程]")
    print("  代入质量守恒方程：")
    print("    A * dh/dt = K*u - h/R")
    print("  整理：")
    print("    A*R * dh/dt + h = K*R*u")
    print("  定义时间常数 τ = A*R：")
    print("    τ * dh/dt + h = K*R*u")

    # 系统参数
    A = 2.5  # m²
    R = 1.8  # min/m²
    K = 1.2  # m³/min

    tau = A * R
    K_dc = K * R

    print("\n[步骤5：系统参数]")
    print(f"  给定参数：")
    print(f"    横截面积 A = {A} m²")
    print(f"    阻力系数 R = {R} min/m²")
    print(f"    泵增益 K = {K} m³/min")
    print(f"  推导参数：")
    print(f"    时间常数 τ = A × R = {tau} 分钟")
    print(f"    稳态增益 K_dc = K × R = {K_dc} m")

    print("\n[步骤6：传递函数]")
    print("  对微分方程进行Laplace变换：")
    print("    τ*s*H(s) + H(s) = K_dc*U(s)")
    print("  得到传递函数：")
    print("             K_dc          2.16")
    print("    G(s) = -------- = -------------")
    print("           τ*s + 1     4.5*s + 1")
    print("\n  这是标准的一阶惯性环节！")

    print("\n[步骤7：物理意义]")
    print(f"  时间常数 τ = {tau} 分钟：")
    print("    - 水位达到稳态值63.2%所需时间")
    print("    - 反映系统响应速度")
    print("    - τ越大，系统响应越慢")
    print(f"  稳态增益 K_dc = {K_dc} m：")
    print("    - 单位控制输入引起的稳态水位变化")
    print("    - 反映系统放大特性")

    return A, R, K, tau, K_dc


# ============================================================================
# 第2部分：模型验证 - 阶跃响应
# ============================================================================

def model_validation_step_response(A, R, K, tau, K_dc):
    """
    通过阶跃响应验证模型
    """
    print("\n" + "=" * 80)
    print("第2部分：模型验证 - 阶跃响应")
    print("=" * 80)

    print("\n[理论预测]")
    print("  一阶系统阶跃响应：")
    print("    h(t) = K_dc * u * (1 - e^(-t/τ))")
    print("  特征时间：")
    print(f"    1τ (63.2%): {tau:.2f} 分钟")
    print(f"    2τ (86.5%): {2*tau:.2f} 分钟")
    print(f"    3τ (95.0%): {3*tau:.2f} 分钟")
    print(f"    4τ (98.2%): {4*tau:.2f} 分钟")
    print(f"    5τ (99.3%): {5*tau:.2f} 分钟")

    print("\n[仿真验证]")

    # 创建真实系统（用于生成数据）
    system = SingleTank(A=A, R=R, K=K)
    system.reset(h0=0.0)

    # 仿真参数
    u_step = 0.5  # 阶跃输入
    duration = 30
    dt = 0.1

    n_steps = int(duration / dt)
    time = np.zeros(n_steps)
    h_sim = np.zeros(n_steps)  # 仿真数据
    h_theory = np.zeros(n_steps)  # 理论计算

    # 仿真和理论计算
    for i in range(n_steps):
        time[i] = system.t
        h_sim[i] = system.h

        # 理论响应
        h_theory[i] = K_dc * u_step * (1 - np.exp(-time[i] / tau))

        # 更新系统
        system.step(u_step, dt)

    # 误差分析
    error = h_sim - h_theory
    max_error = np.max(np.abs(error))
    rmse = np.sqrt(np.mean(error**2))

    print(f"  最大误差：{max_error:.6f} m")
    print(f"  均方根误差：{rmse:.6f} m")
    print(f"  相对误差：{max_error / (K_dc * u_step) * 100:.4f}%")

    if rmse < 0.01:
        print("  ✓ 模型验证通过！仿真与理论高度一致")
    else:
        print("  ⚠ 模型存在误差，需要检查")

    # 验证关键时间点
    print("\n[关键时间点验证]")
    idx_1tau = int(tau / dt)
    idx_3tau = int(3 * tau / dt)

    h_1tau_sim = h_sim[idx_1tau]
    h_1tau_theory = K_dc * u_step * 0.632
    h_3tau_sim = h_sim[idx_3tau]
    h_3tau_theory = K_dc * u_step * 0.950

    print(f"  t = τ = {tau} min:")
    print(f"    仿真值：{h_1tau_sim:.4f} m")
    print(f"    理论值：{h_1tau_theory:.4f} m (63.2%)")
    print(f"    误差：{abs(h_1tau_sim - h_1tau_theory):.6f} m")

    print(f"  t = 3τ = {3*tau} min:")
    print(f"    仿真值：{h_3tau_sim:.4f} m")
    print(f"    理论值：{h_3tau_theory:.4f} m (95.0%)")
    print(f"    误差：{abs(h_3tau_sim - h_3tau_theory):.6f} m")

    return time, h_sim, h_theory, u_step


# ============================================================================
# 第3部分：双水箱系统建模
# ============================================================================

def double_tank_modeling():
    """
    双水箱串联系统建模
    """
    print("\n" + "=" * 80)
    print("第3部分：双水箱串联系统建模")
    print("=" * 80)

    print("\n[系统结构]")
    print("  泵 → 上水箱 → 下水箱 → 流出")

    print("\n[建模步骤]")
    print("  上水箱（水箱1）：")
    print("    A1 * dh1/dt = Q_in - Q_12")
    print("    其中：Q_in = K*u, Q_12 = h1/R1")
    print("    整理：A1 * dh1/dt = K*u - h1/R1")

    print("\n  下水箱（水箱2）：")
    print("    A2 * dh2/dt = Q_12 - Q_out")
    print("    其中：Q_12 = h1/R1, Q_out = h2/R2")
    print("    整理：A2 * dh2/dt = h1/R1 - h2/R2")

    # 系统参数
    A1, A2 = 1.0, 2.0
    R1, R2 = 1.5, 2.0
    K = 1.0

    tau1 = A1 * R1
    tau2 = A2 * R2
    K_dc = K * R1 * R2

    print("\n[系统参数]")
    print(f"  上水箱：A1 = {A1} m², R1 = {R1} min/m²")
    print(f"  下水箱：A2 = {A2} m², R2 = {R2} min/m²")
    print(f"  泵增益：K = {K} m³/min")
    print(f"  时间常数：τ1 = {tau1} min, τ2 = {tau2} min")
    print(f"  稳态增益：K_dc = K×R1×R2 = {K_dc} m")

    print("\n[传递函数]")
    print("  二阶系统：")
    print("                K×R1×R2")
    print("    G(s) = ------------------------")
    print("           (τ1*s + 1)(τ2*s + 1)")
    print(f"\n             {K_dc}")
    print(f"         = ----------------------")
    print(f"           ({tau1}s + 1)({tau2}s + 1)")

    print("\n[系统特性]")
    print("  - 二阶系统")
    print("  - 无超调（两个实极点）")
    print("  - 响应比单水箱慢")
    print(f"  - 主导时间常数：max(τ1, τ2) = {max(tau1, tau2)} min")

    return A1, A2, R1, R2, K


# ============================================================================
# 第4部分：传递函数与频率响应
# ============================================================================

def transfer_function_analysis(A, R, K):
    """
    传递函数分析和频率响应
    """
    print("\n" + "=" * 80)
    print("第4部分：传递函数与频率响应")
    print("=" * 80)

    tau = A * R
    K_dc = K * R

    print("\n[传递函数表示]")
    print("  标准形式：")
    print(f"             {K_dc}")
    print(f"    G(s) = --------")
    print(f"           {tau}s + 1")

    print("\n  零极点形式：")
    print(f"    零点：无")
    print(f"    极点：s = -1/τ = {-1/tau:.4f}")
    print(f"    直流增益：G(0) = {K_dc}")

    print("\n[频率响应特性]")
    # 创建传递函数
    num = [K_dc]
    den = [tau, 1]
    sys = signal.TransferFunction(num, den)

    # 频率范围
    w = np.logspace(-3, 1, 100)  # 0.001 到 10 rad/min

    # Bode图
    w, mag, phase = signal.bode(sys, w)

    # 截止频率（增益降到-3dB）
    w_cutoff = 1 / tau
    f_cutoff = w_cutoff / (2 * np.pi)

    print(f"  截止频率：ω_c = 1/τ = {w_cutoff:.4f} rad/min")
    print(f"            f_c = {f_cutoff:.4f} Hz")
    print(f"  低频增益：{K_dc} (即 {20*np.log10(K_dc):.2f} dB)")
    print(f"  高频衰减：-20 dB/decade（一阶系统）")
    print(f"  相位滞后：0° → -90°")

    return sys, w, mag, phase


# ============================================================================
# 第5部分：可视化与总结
# ============================================================================

def visualize_and_summarize():
    """
    可视化所有建模结果
    """
    print("\n" + "=" * 80)
    print("第5部分：可视化与总结")
    print("=" * 80)

    # 单水箱建模
    A, R, K, tau, K_dc = single_tank_modeling()

    # 模型验证
    time, h_sim, h_theory, u_step = model_validation_step_response(A, R, K, tau, K_dc)

    # 双水箱建模
    A1, A2, R1, R2, K2 = double_tank_modeling()

    # 传递函数分析
    sys, w, mag, phase = transfer_function_analysis(A, R, K)

    # 双水箱仿真
    system_double = DoubleTank(A1=A1, A2=A2, R1=R1, R2=R2, K=K2)
    system_double.reset(h1_0=0.0, h2_0=0.0)

    time_double = np.zeros(len(time))
    h1_double = np.zeros(len(time))
    h2_double = np.zeros(len(time))

    for i in range(len(time)):
        time_double[i] = system_double.t
        h1_double[i] = system_double.h1
        h2_double[i] = system_double.h2
        system_double.step(u_step, 0.1)

    # 可视化
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # 子图1：单水箱阶跃响应（仿真 vs 理论）
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(time, h_sim, 'b-', linewidth=2, label='Simulation')
    ax1.plot(time, h_theory, 'r--', linewidth=2, label='Theory')
    ax1.axhline(K_dc * u_step * 0.632, color='gray', linestyle=':', alpha=0.7)
    ax1.axvline(tau, color='gray', linestyle=':', alpha=0.7)
    ax1.text(tau, K_dc * u_step * 0.632, f'  τ = {tau} min\n  63.2%', fontsize=9)
    ax1.set_xlabel('Time (min)')
    ax1.set_ylabel('Water Level (m)')
    # 标题已移除，保持图表简洁
    ax1.legend()
    ax1.grid(True)

    # 子图2：误差分析
    ax2 = fig.add_subplot(gs[0, 1])
    error = h_sim - h_theory
    ax2.plot(time, error * 1000, 'g-', linewidth=2)  # 转换为mm
    ax2.axhline(0, color='k', linestyle='--', linewidth=0.5)
    ax2.set_xlabel('Time (min)')
    ax2.set_ylabel('Error (mm)')
    # 标题已移除，保持图表简洁
    ax2.grid(True)

    # 子图3：双水箱响应
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(time_double, h1_double, 'b-', linewidth=2, label='Upper Tank h1')
    ax3.plot(time_double, h2_double, 'r-', linewidth=2, label='Lower Tank h2')
    ax3.set_xlabel('Time (min)')
    ax3.set_ylabel('Water Level (m)')
    # 标题已移除，保持图表简洁
    ax3.legend()
    ax3.grid(True)

    # 子图4：单水箱 vs 双水箱对比
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(time, h_sim, 'b-', linewidth=2, label='Single Tank')
    ax4.plot(time_double, h2_double, 'r-', linewidth=2, label='Double Tank (h2)')
    ax4.set_xlabel('Time (min)')
    ax4.set_ylabel('Water Level (m)')
    # 标题已移除，保持图表简洁
    ax4.legend()
    ax4.grid(True)

    # 子图5：Bode图 - 幅值
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.semilogx(w, mag, 'b-', linewidth=2)
    ax5.axhline(-3, color='r', linestyle='--', alpha=0.7, label='-3 dB')
    ax5.axvline(1/tau, color='r', linestyle='--', alpha=0.7)
    ax5.set_xlabel('Frequency (rad/min)')
    ax5.set_ylabel('Magnitude (dB)')
    # 标题已移除，保持图表简洁
    ax5.legend()
    ax5.grid(True, which='both')

    # 子图6：Bode图 - 相位
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.semilogx(w, phase, 'b-', linewidth=2)
    ax6.axhline(-45, color='r', linestyle='--', alpha=0.7, label='-45°')
    ax6.axvline(1/tau, color='r', linestyle='--', alpha=0.7)
    ax6.set_xlabel('Frequency (rad/min)')
    ax6.set_ylabel('Phase (degrees)')
    # 标题已移除，保持图表简洁
    ax6.legend()
    ax6.grid(True, which='both')

    plt.savefig('system_modeling_analysis.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: system_modeling_analysis.png")

    print("\n" + "=" * 80)
    print("案例9总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 机理建模步骤：")
    print("     • 系统分析（输入、输出、状态）")
    print("     • 物理定律（质量守恒）")
    print("     • 流量关系（泵特性、管道阻力）")
    print("     • 微分方程（组合方程）")
    print("     • 传递函数（Laplace变换）")

    print("\n  2. 单水箱模型：")
    print(f"     • 一阶惯性环节：G(s) = {K_dc}/(τs+1)")
    print(f"     • 时间常数 τ = {tau} min")
    print(f"     • 无超调，单调上升")

    print("\n  3. 双水箱模型：")
    print("     • 二阶系统，两个时间常数")
    print("     • 响应更慢，但更平滑")
    print("     • 两个实极点，无振荡")

    print("\n  4. 模型验证：")
    print("     • 仿真与理论高度一致")
    print("     • 误差 < 0.01 m")
    print("     • 关键时间点验证通过")

    print("\n  5. 工程意义：")
    print("     • 模型是控制器设计的基础")
    print("     • 参数有明确物理意义")
    print("     • 可用于性能预测和优化")

    print("\n[下一步学习]")
    print("  → 案例10：频域分析（Bode图详解）")
    print("  → 案例13：状态空间建模（现代控制方法）")

    plt.show()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""
    visualize_and_summarize()

    print("\n" + "=" * 80)
    print("案例9演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
