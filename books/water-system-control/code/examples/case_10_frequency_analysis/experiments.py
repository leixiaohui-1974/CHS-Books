#!/usr/bin/env python3
"""
案例10扩展实验：频域分析深入研究

本文件包含多个扩展实验：
1. PID参数对频域特性的影响
2. 不同控制器类型的频域对比
3. 稳定裕度与时域性能的关系
4. 参数不确定性的鲁棒性分析

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def calculate_margins(sys, w=None):
    """
    计算系统的增益裕度和相位裕度

    参数:
        sys: 传递函数系统
        w: 频率范围（可选）

    返回:
        gm: 增益裕度（倍数）
        pm: 相位裕度（度）
        w_gm: 增益穿越频率
        w_pm: 相位穿越频率
    """
    if w is None:
        w = np.logspace(-3, 3, 1000)

    # 计算频率响应
    w_resp, mag, phase = signal.bode(sys, w)

    # 转换为线性幅值
    mag_linear = 10 ** (mag / 20)

    # 计算增益裕度 (GM)
    # 找到相位穿越频率（相位 = -180°）
    idx_phase_cross = np.where(np.diff(np.sign(phase + 180)))[0]
    if len(idx_phase_cross) > 0:
        idx = idx_phase_cross[0]
        w_gm = w_resp[idx]
        gm = 1.0 / mag_linear[idx]
    else:
        w_gm = np.nan
        gm = np.inf

    # 计算相位裕度 (PM)
    # 找到增益穿越频率（幅值 = 0 dB）
    idx_gain_cross = np.where(np.diff(np.sign(mag)))[0]
    if len(idx_gain_cross) > 0:
        idx = idx_gain_cross[-1]  # 取最后一个穿越点
        w_pm = w_resp[idx]
        pm = 180 + phase[idx]
    else:
        w_pm = np.nan
        pm = np.nan

    return gm, pm, w_gm, w_pm


# ============================================================================
# 实验1：PID参数对频域特性的影响
# ============================================================================

def experiment_pid_parameter_effects():
    """
    实验1：分析P、I、D参数对Bode图和稳定裕度的影响
    """
    print("=" * 80)
    print("实验1：PID参数对频域特性的影响")
    print("=" * 80)

    # 系统参数
    A, R, K = 2.5, 1.8, 1.2
    tau = A * R
    K_dc = K * R

    # 被控对象传递函数
    sys_plant = signal.TransferFunction([K_dc], [tau, 1])

    # 测试不同的Kp值
    print("\n[测试比例增益Kp的影响]")
    Kp_values = [0.5, 1.0, 2.0, 4.0]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    w = np.logspace(-2, 1, 200)

    # Kp影响
    for Kp in Kp_values:
        # P控制器
        sys_controller = signal.TransferFunction([Kp], [1])
        sys_open = signal.TransferFunction(
            np.polymul(sys_controller.num, sys_plant.num),
            np.polymul(sys_controller.den, sys_plant.den)
        )

        w_temp, mag, phase = signal.bode(sys_open, w)
        gm, pm, w_gm, w_pm = calculate_margins(sys_open)

        axes[0, 0].semilogx(w_temp, mag, linewidth=2, label=f'Kp={Kp}, PM={pm:.1f}°')
        axes[1, 0].semilogx(w_temp, phase, linewidth=2, label=f'Kp={Kp}')

        print(f"  Kp={Kp}: GM={gm:.2f} dB, PM={pm:.1f}°, ωpm={w_pm:.4f} rad/min")

    axes[0, 0].set_ylabel('Magnitude (dB)')
    axes[0, 0].set_title('Effect of Kp on Bode Plot')
    axes[0, 0].legend()
    axes[0, 0].grid(True, which='both')
    axes[0, 0].axhline(0, color='r', linestyle='--', alpha=0.5)

    axes[1, 0].set_xlabel('Frequency (rad/min)')
    axes[1, 0].set_ylabel('Phase (degrees)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, which='both')
    axes[1, 0].axhline(-180, color='r', linestyle='--', alpha=0.5)

    # 测试不同的Ti值（积分时间）
    print("\n[测试积分时间Ti的影响]")
    Kp = 2.0
    Ti_values = [2.0, 5.0, 10.0, 20.0]

    for Ti in Ti_values:
        # PI控制器: Gc(s) = Kp(1 + 1/(Ti*s))
        Ki = Kp / Ti
        sys_controller = signal.TransferFunction([Kp, Ki], [1, 0])
        sys_open = signal.TransferFunction(
            np.polymul(sys_controller.num, sys_plant.num),
            np.polymul(sys_controller.den, sys_plant.den)
        )

        w_temp, mag, phase = signal.bode(sys_open, w)
        gm, pm, w_gm, w_pm = calculate_margins(sys_open)

        axes[0, 1].semilogx(w_temp, mag, linewidth=2, label=f'Ti={Ti}, PM={pm:.1f}°')
        axes[1, 1].semilogx(w_temp, phase, linewidth=2, label=f'Ti={Ti}')

        print(f"  Ti={Ti}: GM={gm:.2f} dB, PM={pm:.1f}°, ωpm={w_pm:.4f} rad/min")

    axes[0, 1].set_ylabel('Magnitude (dB)')
    axes[0, 1].set_title('Effect of Ti on Bode Plot (Kp=2.0)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, which='both')
    axes[0, 1].axhline(0, color='r', linestyle='--', alpha=0.5)

    axes[1, 1].set_xlabel('Frequency (rad/min)')
    axes[1, 1].set_ylabel('Phase (degrees)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, which='both')
    axes[1, 1].axhline(-180, color='r', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('exp1_pid_parameters.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp1_pid_parameters.png")

    print("\n结论：")
    print("  - Kp增大：幅频曲线上移，相位裕度减小，系统响应变快但稳定性下降")
    print("  - Ti增大：低频增益增加，相位裕度增大，稳态误差减小但响应变慢")
    print("  - 需要权衡快速性和稳定性")


# ============================================================================
# 实验2：不同控制器类型的频域对比
# ============================================================================

def experiment_controller_type_comparison():
    """
    实验2：对比P、PI、PID控制器的频域特性
    """
    print("\n" + "=" * 80)
    print("实验2：不同控制器类型的频域对比")
    print("=" * 80)

    # 系统参数
    A, R, K = 2.5, 1.8, 1.2
    tau = A * R
    K_dc = K * R

    # 被控对象
    sys_plant = signal.TransferFunction([K_dc], [tau, 1])

    # 控制器参数
    Kp = 2.0
    Ti = 8.0
    Td = 1.0

    controllers = {}

    # P控制器
    controllers['P'] = signal.TransferFunction([Kp], [1])

    # PI控制器
    Ki = Kp / Ti
    controllers['PI'] = signal.TransferFunction([Kp, Ki], [1, 0])

    # PID控制器（近似微分）
    Ki = Kp / Ti
    Kd = Kp * Td
    Tf = Td / 10  # 滤波时间常数
    # PID(s) = Kp + Ki/s + Kd*s/(Tf*s+1)
    num = np.polymul([Kp*Tf, Kp + Kd], [1, 0])
    num = np.polyadd(num, [0, Ki*Tf, Ki])
    den = np.polymul([Tf, 1], [1, 0])
    controllers['PID'] = signal.TransferFunction(num, den)

    # 频率响应分析
    fig, axes = plt.subplots(3, 2, figsize=(14, 14))
    w = np.logspace(-2, 1, 200)

    print("\n[控制器频域特性对比]")
    results = {}

    for name, controller in controllers.items():
        # 开环传递函数
        sys_open = signal.TransferFunction(
            np.polymul(controller.num, sys_plant.num),
            np.polymul(controller.den, sys_plant.den)
        )

        # 闭环传递函数
        sys_closed = signal.TransferFunction(
            sys_open.num,
            np.polyadd(sys_open.den, sys_open.num)
        )

        # 频域分析
        w_temp, mag_open, phase_open = signal.bode(sys_open, w)
        gm, pm, w_gm, w_pm = calculate_margins(sys_open)

        w_closed, mag_closed = signal.freqs(sys_closed.num, sys_closed.den, w)
        mag_closed_db = 20 * np.log10(np.abs(mag_closed))

        # 绘制开环Bode图
        axes[0, 0].semilogx(w_temp, mag_open, linewidth=2, label=name)
        axes[0, 1].semilogx(w_temp, phase_open, linewidth=2, label=name)

        # 绘制闭环频率响应
        axes[1, 0].semilogx(w, mag_closed_db, linewidth=2, label=name)

        # 计算带宽
        idx_bw = np.where(mag_closed_db <= -3)[0]
        if len(idx_bw) > 0:
            w_bw = w[idx_bw[0]]
        else:
            w_bw = w[-1]

        # 计算谐振峰值
        Mr_db = np.max(mag_closed_db)
        Mr = 10 ** (Mr_db / 20)

        results[name] = {
            'GM': gm,
            'PM': pm,
            'w_pm': w_pm,
            'w_bw': w_bw,
            'Mr': Mr
        }

        print(f"\n{name}控制器:")
        print(f"  增益裕度: {gm:.2f} dB")
        print(f"  相位裕度: {pm:.1f}°")
        print(f"  截止频率: {w_pm:.4f} rad/min")
        print(f"  带宽: {w_bw:.4f} rad/min")
        print(f"  谐振峰值: {Mr:.3f}")

    # 设置图表
    axes[0, 0].set_ylabel('Magnitude (dB)')
    axes[0, 0].set_title('Open-Loop Bode Plot')
    axes[0, 0].legend()
    axes[0, 0].grid(True, which='both')
    axes[0, 0].axhline(0, color='r', linestyle='--', alpha=0.5)

    axes[0, 1].set_ylabel('Phase (degrees)')
    axes[0, 1].set_title('Open-Loop Phase')
    axes[0, 1].legend()
    axes[0, 1].grid(True, which='both')
    axes[0, 1].axhline(-180, color='r', linestyle='--', alpha=0.5)

    axes[1, 0].set_ylabel('Magnitude (dB)')
    axes[1, 0].set_xlabel('Frequency (rad/min)')
    axes[1, 0].set_title('Closed-Loop Frequency Response')
    axes[1, 0].legend()
    axes[1, 0].grid(True, which='both')
    axes[1, 0].axhline(-3, color='r', linestyle='--', alpha=0.5, label='Bandwidth')

    # 时域阶跃响应对比
    print("\n[时域阶跃响应]")

    for name, controller in controllers.items():
        sys_open = signal.TransferFunction(
            np.polymul(controller.num, sys_plant.num),
            np.polymul(controller.den, sys_plant.den)
        )
        sys_closed = signal.TransferFunction(
            sys_open.num,
            np.polyadd(sys_open.den, sys_open.num)
        )

        t = np.linspace(0, 30, 300)
        t_temp, y = signal.step(sys_closed, T=t)

        # 计算性能指标
        y_final = y[-1]
        idx_rise = np.where(y >= 0.9 * y_final)[0]
        if len(idx_rise) > 0:
            t_rise = t_temp[idx_rise[0]]
        else:
            t_rise = t_temp[-1]

        overshoot = (np.max(y) - y_final) / y_final * 100

        axes[1, 1].plot(t_temp, y, linewidth=2, label=f'{name} (OS={overshoot:.1f}%)')

        print(f"{name}: 上升时间={t_rise:.2f} min, 超调={overshoot:.1f}%")

    axes[1, 1].set_xlabel('Time (min)')
    axes[1, 1].set_ylabel('Output')
    axes[1, 1].set_title('Step Response Comparison')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    axes[1, 1].axhline(1, color='r', linestyle='--', alpha=0.5)

    # 稳定裕度与时域性能的关系
    axes[2, 0].scatter([results[name]['PM'] for name in controllers.keys()],
                       [overshoot for name in controllers.keys()],
                       s=100)
    for i, name in enumerate(controllers.keys()):
        axes[2, 0].annotate(name,
                           (results[name]['PM'], overshoot),
                           xytext=(5, 5), textcoords='offset points')
    axes[2, 0].set_xlabel('Phase Margin (degrees)')
    axes[2, 0].set_ylabel('Overshoot (%)')
    axes[2, 0].set_title('PM vs Overshoot')
    axes[2, 0].grid(True)

    axes[2, 1].scatter([results[name]['w_bw'] for name in controllers.keys()],
                       [t_rise for name in controllers.keys()],
                       s=100)
    for i, name in enumerate(controllers.keys()):
        axes[2, 1].annotate(name,
                           (results[name]['w_bw'], t_rise),
                           xytext=(5, 5), textcoords='offset points')
    axes[2, 1].set_xlabel('Bandwidth (rad/min)')
    axes[2, 1].set_ylabel('Rise Time (min)')
    axes[2, 1].set_title('Bandwidth vs Rise Time')
    axes[2, 1].grid(True)

    plt.tight_layout()
    plt.savefig('exp2_controller_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp2_controller_comparison.png")

    print("\n结论：")
    print("  - P控制器：最简单，但有稳态误差，相位裕度最大")
    print("  - PI控制器：消除稳态误差，但相位裕度减小，可能有小超调")
    print("  - PID控制器：响应最快，但需要精细调参，相位裕度最小")
    print("  - 频域指标与时域性能密切相关：PM越大，超调越小；带宽越大，响应越快")


# ============================================================================
# 实验3：参数不确定性的鲁棒性分析
# ============================================================================

def experiment_robustness_analysis():
    """
    实验3：分析系统参数变化对稳定性的影响
    """
    print("\n" + "=" * 80)
    print("实验3：参数不确定性的鲁棒性分析")
    print("=" * 80)

    # 标称参数
    A_nom, R_nom, K_nom = 2.5, 1.8, 1.2
    tau_nom = A_nom * R_nom
    K_dc_nom = K_nom * R_nom

    # 设计的PI控制器（基于标称模型）
    Kp = 2.0
    Ti = 8.0
    Ki = Kp / Ti

    print(f"\n[标称系统参数]")
    print(f"  A = {A_nom} m², R = {R_nom} min/m², K = {K_nom} m³/min")
    print(f"  τ = {tau_nom} min, K_dc = {K_dc_nom}")
    print(f"\n[PI控制器参数]")
    print(f"  Kp = {Kp}, Ti = {Ti}")

    # 测试参数变化
    print("\n[测试参数变化对稳定裕度的影响]")

    # 变化范围：±50%
    variation_range = np.linspace(0.5, 1.5, 11)

    results = {
        'A_var': {'GM': [], 'PM': []},
        'R_var': {'GM': [], 'PM': []},
        'K_var': {'GM': [], 'PM': []}
    }

    # 变化A
    print("\n变化A（横截面积）:")
    for factor in variation_range:
        A = A_nom * factor
        tau = A * R_nom
        K_dc = K_nom * R_nom

        sys_plant = signal.TransferFunction([K_dc], [tau, 1])
        sys_controller = signal.TransferFunction([Kp, Ki], [1, 0])
        sys_open = signal.TransferFunction(
            np.polymul(sys_controller.num, sys_plant.num),
            np.polymul(sys_controller.den, sys_plant.den)
        )

        gm, pm, _, _ = calculate_margins(sys_open)
        results['A_var']['GM'].append(gm)
        results['A_var']['PM'].append(pm)

        if factor in [0.5, 1.0, 1.5]:
            print(f"  A = {A:.2f} ({factor*100:.0f}%): GM = {gm:.2f} dB, PM = {pm:.1f}°")

    # 变化R
    print("\n变化R（阻力系数）:")
    for factor in variation_range:
        R = R_nom * factor
        tau = A_nom * R
        K_dc = K_nom * R

        sys_plant = signal.TransferFunction([K_dc], [tau, 1])
        sys_controller = signal.TransferFunction([Kp, Ki], [1, 0])
        sys_open = signal.TransferFunction(
            np.polymul(sys_controller.num, sys_plant.num),
            np.polymul(sys_controller.den, sys_plant.den)
        )

        gm, pm, _, _ = calculate_margins(sys_open)
        results['R_var']['GM'].append(gm)
        results['R_var']['PM'].append(pm)

        if factor in [0.5, 1.0, 1.5]:
            print(f"  R = {R:.2f} ({factor*100:.0f}%): GM = {gm:.2f} dB, PM = {pm:.1f}°")

    # 变化K
    print("\n变化K（泵增益）:")
    for factor in variation_range:
        K = K_nom * factor
        tau = A_nom * R_nom
        K_dc = K * R_nom

        sys_plant = signal.TransferFunction([K_dc], [tau, 1])
        sys_controller = signal.TransferFunction([Kp, Ki], [1, 0])
        sys_open = signal.TransferFunction(
            np.polymul(sys_controller.num, sys_plant.num),
            np.polymul(sys_controller.den, sys_plant.den)
        )

        gm, pm, _, _ = calculate_margins(sys_open)
        results['K_var']['GM'].append(gm)
        results['K_var']['PM'].append(pm)

        if factor in [0.5, 1.0, 1.5]:
            print(f"  K = {K:.2f} ({factor*100:.0f}%): GM = {gm:.2f} dB, PM = {pm:.1f}°")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 增益裕度
    axes[0, 0].plot(variation_range * 100, results['A_var']['GM'], 'o-', linewidth=2, label='A variation')
    axes[0, 0].plot(variation_range * 100, results['R_var']['GM'], 's-', linewidth=2, label='R variation')
    axes[0, 0].plot(variation_range * 100, results['K_var']['GM'], '^-', linewidth=2, label='K variation')
    axes[0, 0].axhline(6, color='r', linestyle='--', alpha=0.5, label='GM=6dB (minimum)')
    axes[0, 0].set_xlabel('Parameter Variation (%)')
    axes[0, 0].set_ylabel('Gain Margin (dB)')
    axes[0, 0].set_title('Robustness: Gain Margin')
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # 相位裕度
    axes[0, 1].plot(variation_range * 100, results['A_var']['PM'], 'o-', linewidth=2, label='A variation')
    axes[0, 1].plot(variation_range * 100, results['R_var']['PM'], 's-', linewidth=2, label='R variation')
    axes[0, 1].plot(variation_range * 100, results['K_var']['PM'], '^-', linewidth=2, label='K variation')
    axes[0, 1].axhline(30, color='r', linestyle='--', alpha=0.5, label='PM=30° (minimum)')
    axes[0, 1].set_xlabel('Parameter Variation (%)')
    axes[0, 1].set_ylabel('Phase Margin (degrees)')
    axes[0, 1].set_title('Robustness: Phase Margin')
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Bode图对比（选择几个代表性的点）
    w = np.logspace(-2, 1, 200)

    for factor, style in zip([0.5, 1.0, 1.5], ['-', '--', '-.']):
        A = A_nom * factor
        tau = A * R_nom
        K_dc = K_nom * R_nom

        sys_plant = signal.TransferFunction([K_dc], [tau, 1])
        sys_controller = signal.TransferFunction([Kp, Ki], [1, 0])
        sys_open = signal.TransferFunction(
            np.polymul(sys_controller.num, sys_plant.num),
            np.polymul(sys_controller.den, sys_plant.den)
        )

        w_temp, mag, phase = signal.bode(sys_open, w)
        gm, pm, _, _ = calculate_margins(sys_open)

        axes[1, 0].semilogx(w_temp, mag, linestyle=style, linewidth=2,
                           label=f'A={factor*100:.0f}% (PM={pm:.1f}°)')
        axes[1, 1].semilogx(w_temp, phase, linestyle=style, linewidth=2,
                           label=f'A={factor*100:.0f}%')

    axes[1, 0].axhline(0, color='r', linestyle='--', alpha=0.5)
    axes[1, 0].set_ylabel('Magnitude (dB)')
    axes[1, 0].set_xlabel('Frequency (rad/min)')
    axes[1, 0].set_title('Bode Plot with A Variation')
    axes[1, 0].legend()
    axes[1, 0].grid(True, which='both')

    axes[1, 1].axhline(-180, color='r', linestyle='--', alpha=0.5)
    axes[1, 1].set_ylabel('Phase (degrees)')
    axes[1, 1].set_xlabel('Frequency (rad/min)')
    axes[1, 1].set_title('Phase Plot with A Variation')
    axes[1, 1].legend()
    axes[1, 1].grid(True, which='both')

    plt.tight_layout()
    plt.savefig('exp3_robustness.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp3_robustness.png")

    print("\n结论：")
    print("  - A变化：显著影响相位裕度，但对增益裕度影响较小")
    print("  - R变化：同时影响增益和相位裕度")
    print("  - K变化：主要影响增益裕度")
    print("  - 系统在±50%参数变化下仍保持稳定，鲁棒性良好")
    print("  - 设计时应确保足够的裕度以应对参数不确定性")


# ============================================================================
# 实验4：频域设计法
# ============================================================================

def experiment_frequency_design():
    """
    实验4：基于频域指标设计控制器
    """
    print("\n" + "=" * 80)
    print("实验4：频域设计法")
    print("=" * 80)

    # 系统参数
    A, R, K = 2.5, 1.8, 1.2
    tau = A * R
    K_dc = K * R

    sys_plant = signal.TransferFunction([K_dc], [tau, 1])

    print("\n[设计目标]")
    print("  相位裕度 PM ≥ 45°（保证良好的阻尼）")
    print("  增益裕度 GM ≥ 10 dB（保证稳定鲁棒性）")
    print("  截止频率 ωc ≈ 0.3 rad/min（保证合适的响应速度）")

    # 设计方法：试探法
    print("\n[设计过程]")

    designs = []

    # 设计1：保守设计（大裕度）
    Kp1, Ti1 = 1.0, 10.0
    Ki1 = Kp1 / Ti1
    sys_c1 = signal.TransferFunction([Kp1, Ki1], [1, 0])
    sys_o1 = signal.TransferFunction(
        np.polymul(sys_c1.num, sys_plant.num),
        np.polymul(sys_c1.den, sys_plant.den)
    )
    gm1, pm1, w_gm1, w_pm1 = calculate_margins(sys_o1)
    designs.append(('Conservative', Kp1, Ti1, gm1, pm1, w_pm1, sys_o1))

    print(f"\n设计1（保守）：Kp={Kp1}, Ti={Ti1}")
    print(f"  GM={gm1:.2f} dB, PM={pm1:.1f}°, ωc={w_pm1:.4f} rad/min")

    # 设计2：平衡设计
    Kp2, Ti2 = 2.0, 8.0
    Ki2 = Kp2 / Ti2
    sys_c2 = signal.TransferFunction([Kp2, Ki2], [1, 0])
    sys_o2 = signal.TransferFunction(
        np.polymul(sys_c2.num, sys_plant.num),
        np.polymul(sys_c2.den, sys_plant.den)
    )
    gm2, pm2, w_gm2, w_pm2 = calculate_margins(sys_o2)
    designs.append(('Balanced', Kp2, Ti2, gm2, pm2, w_pm2, sys_o2))

    print(f"\n设计2（平衡）：Kp={Kp2}, Ti={Ti2}")
    print(f"  GM={gm2:.2f} dB, PM={pm2:.1f}°, ωc={w_pm2:.4f} rad/min")

    # 设计3：激进设计（小裕度）
    Kp3, Ti3 = 3.5, 6.0
    Ki3 = Kp3 / Ti3
    sys_c3 = signal.TransferFunction([Kp3, Ki3], [1, 0])
    sys_o3 = signal.TransferFunction(
        np.polymul(sys_c3.num, sys_plant.num),
        np.polymul(sys_c3.den, sys_plant.den)
    )
    gm3, pm3, w_gm3, w_pm3 = calculate_margins(sys_o3)
    designs.append(('Aggressive', Kp3, Ti3, gm3, pm3, w_pm3, sys_o3))

    print(f"\n设计3（激进）：Kp={Kp3}, Ti={Ti3}")
    print(f"  GM={gm3:.2f} dB, PM={pm3:.1f}°, ωc={w_pm3:.4f} rad/min")

    # 可视化对比
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    w = np.logspace(-2, 1, 200)

    for name, Kp, Ti, gm, pm, wc, sys_open in designs:
        w_temp, mag, phase = signal.bode(sys_open, w)
        axes[0, 0].semilogx(w_temp, mag, linewidth=2, label=f'{name} (GM={gm:.1f}dB)')
        axes[0, 1].semilogx(w_temp, phase, linewidth=2, label=f'{name} (PM={pm:.1f}°)')

        # 时域响应
        sys_closed = signal.TransferFunction(
            sys_open.num,
            np.polyadd(sys_open.den, sys_open.num)
        )
        t = np.linspace(0, 40, 400)
        t_temp, y = signal.step(sys_closed, T=t)

        overshoot = (np.max(y) - y[-1]) / y[-1] * 100
        axes[1, 0].plot(t_temp, y, linewidth=2, label=f'{name} (OS={overshoot:.1f}%)')

    axes[0, 0].axhline(0, color='r', linestyle='--', alpha=0.5)
    axes[0, 0].set_ylabel('Magnitude (dB)')
    axes[0, 0].set_title('Open-Loop Bode Plot Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, which='both')

    axes[0, 1].axhline(-180, color='r', linestyle='--', alpha=0.5)
    axes[0, 1].axhline(-135, color='g', linestyle='--', alpha=0.3, label='PM=45°')
    axes[0, 1].set_xlabel('Frequency (rad/min)')
    axes[0, 1].set_ylabel('Phase (degrees)')
    axes[0, 1].set_title('Phase Comparison')
    axes[0, 1].legend()
    axes[0, 1].grid(True, which='both')

    axes[1, 0].axhline(1, color='r', linestyle='--', alpha=0.5)
    axes[1, 0].set_xlabel('Time (min)')
    axes[1, 0].set_ylabel('Output')
    axes[1, 0].set_title('Step Response Comparison')
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    # 性能指标总结
    headers = ['Design', 'Kp', 'Ti', 'GM(dB)', 'PM(°)', 'ωc', 'Meets?']
    table_data = []
    for name, Kp, Ti, gm, pm, wc, _ in designs:
        meets = '✓' if (gm >= 10 and pm >= 45) else '✗'
        table_data.append([name, f'{Kp:.1f}', f'{Ti:.1f}', f'{gm:.1f}',
                          f'{pm:.1f}', f'{wc:.3f}', meets])

    axes[1, 1].axis('tight')
    axes[1, 1].axis('off')
    table = axes[1, 1].table(cellText=table_data, colLabels=headers,
                             cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    axes[1, 1].set_title('Design Summary')

    plt.tight_layout()
    plt.savefig('exp4_frequency_design.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp4_frequency_design.png")

    print("\n结论：")
    print("  - 频域设计法可直接控制稳定裕度")
    print("  - GM和PM是重要的设计指标")
    print("  - 需要在快速性和稳定性之间权衡")
    print("  - 推荐使用平衡设计（设计2）")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例10扩展实验：频域分析深入研究")
    print("=" * 80)

    # 实验1：PID参数影响
    experiment_pid_parameter_effects()

    # 实验2：控制器类型对比
    experiment_controller_type_comparison()

    # 实验3：鲁棒性分析
    experiment_robustness_analysis()

    # 实验4：频域设计法
    experiment_frequency_design()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
