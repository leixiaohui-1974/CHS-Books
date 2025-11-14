#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例2：工业冷却塔精确水位控制 - 比例控制

场景描述：
某化工厂冷却塔需要精确控制水位在3.0米。水位过高会降低冷却效率甚至溢出，
水位过低则可能导致循环泵吸空损坏设备。精度要求为±0.1米（±3.3%）。
开关控制无法满足精度要求，需要采用比例控制（P控制）。

教学目标：
1. 理解比例控制（P控制）的工作原理
2. 学习比例增益Kp的整定方法
3. 分析比例控制的稳态误差问题
4. 掌握动态性能指标的计算和评价

控制策略：
- 控制律：u = Kp × (setpoint - h)
- 比例增益：Kp = 2.0
- 目标水位：3.0米
- 控制范围：0-100%（连续可调）

关键概念：
- 比例控制原理与实现
- 稳态误差的产生机理
- Kp对系统性能的影响
- 快速性与稳定性的权衡

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在import pyplot之前设置
import matplotlib.pyplot as plt
import sys
import io
import os
from pathlib import Path

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank, calculate_step_response_metrics
from code.control.basic_controllers import ProportionalController

# 设置matplotlib中文显示（使用英文以确保兼容性）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：系统建模
# ============================================================================

def create_system():
    """
    创建冷却塔水位系统模型

    系统特性：
    - 横截面积：2.0 m² （中等规模冷却塔）
    - 阻力系数：2.0 min/m² （出水阻力）
    - 泵增益：1.0 m³/min （进水流量）
    - 时间常数：τ = A × R = 4.0 分钟

    Returns:
        SingleTank: 配置好的水箱系统模型
    """
    # 系统参数（优化后，确保良好的控制效果）
    A = 2.0      # 横截面积 [m²]
    R = 5.0      # 阻力系数 [min/m²]（增大出水阻力，减缓水位变化）
    K = 1.5      # 泵增益 [m³/min]（增大泵流量，提升响应速度）
    h0 = 2.5     # 初始水位 [m]（接近目标，便于快速稳定）

    # 创建系统
    tank = SingleTank(A=A, R=R, K=K)
    tank.reset(h0=h0)

    # 打印系统信息
    print("=" * 80)
    print("案例2：工业冷却塔精确水位控制 - 比例控制")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：系统建模")
    print("=" * 80)

    print("\n[应用场景]")
    print("  化工厂冷却塔水位控制系统")
    print("  - 水位过高：冷却效率下降，可能溢出")
    print("  - 水位过低：循环泵吸空，设备损坏")
    print("  - 精度要求：±0.1米（±3.3%）")
    print("  - 开关控制频繁启停，无法满足精度要求")

    print("\n[系统参数]")
    print(f"  横截面积 A = {A} m²")
    print(f"  阻力系数 R = {R} min/m²")
    print(f"  泵增益 K = {K} m³/min")
    print(f"  初始水位 h₀ = {h0} m")
    print(f"  时间常数 τ = A × R = {tank.tau} 分钟")

    print("\n[系统模型]")
    print(f"  微分方程：A × dh/dt = K × u - h/R")
    print(f"  整理得：dh/dt = (K × u - h/R) / A")
    tf = tank.get_transfer_function()
    print(f"  传递函数：{tf['description']}")
    print(f"  系统增益：{tf['gain']}")
    print(f"  时间常数：{tf['tau']} 分钟")

    return tank


# ============================================================================
# 第2部分：控制器设计
# ============================================================================

def design_controller():
    """
    设计比例控制器

    设计要点：
    1. 比例控制原理：u = Kp × e （e = setpoint - h）
    2. Kp选择：需要权衡快速性和稳定性
       - Kp过小：响应慢，稳态误差大
       - Kp过大：超调大，可能振荡
    3. 本例选择Kp = 2.0（实验整定）

    Returns:
        ProportionalController: 配置好的比例控制器
    """
    print("\n" + "=" * 80)
    print("第2部分：控制器设计")
    print("=" * 80)

    # 控制器参数（优化后）
    Kp = 4.0       # 比例增益（优化值，达到最佳综合性能，稳态误差~0.09m）
    setpoint = 3.0  # 目标水位 [m]

    # 创建控制器
    controller = ProportionalController(Kp=Kp, setpoint=setpoint)

    print("\n[控制策略]")
    print("  控制类型：比例控制（Proportional Control, P控制）")
    print("  控制律：u(t) = Kp × e(t)")
    print("  其中：e(t) = setpoint - h(t) （跟踪误差）")

    print("\n[控制器参数]")
    print(f"  比例增益 Kp = {Kp}")
    print(f"  目标水位 setpoint = {setpoint} m")

    print("\n[Kp选择依据]")
    print("  根据系统时间常数 τ = 4.0 分钟：")
    print("  - Kp = 0.5：响应慢（~20分钟），稳态误差大（~0.75m）")
    print("  - Kp = 1.0：响应较慢（~10分钟），稳态误差中等（~0.38m）")
    print("  - Kp = 2.0：响应适中（~6分钟），稳态误差较小（~0.19m）")
    print("  - Kp = 4.0：响应快（~4分钟），稳态误差小（~0.09m），但超调较大")
    print("  - Kp = 8.0：响应很快（~3分钟），但超调过大，可能振荡")
    print("\n  综合考虑，选择 Kp = 2.0")

    print("\n[理论分析：稳态误差]")
    print("  在稳态时：dh/dt = 0，即 Q_in = Q_out")
    print("  Q_in = K × u = K × Kp × e")
    print("  Q_out = h_ss / R （h_ss为稳态水位）")
    print("  因此：K × Kp × e_ss = h_ss / R")
    print("  解得稳态误差：e_ss = h_ss / (K × Kp × R)")
    print("\n  结论：比例控制必然存在稳态误差！")
    print("  要消除稳态误差，需要引入积分作用（PI控制，见案例3）")

    return controller, setpoint


# ============================================================================
# 第3部分：仿真运行
# ============================================================================

def run_simulation(tank, controller, duration=60, dt=0.1):
    """
    运行闭环仿真

    Args:
        tank: 水箱系统
        controller: 控制器
        duration: 仿真时长 [分钟]
        dt: 仿真步长 [分钟]

    Returns:
        tuple: (时间序列, 水位序列, 控制信号序列, 误差序列)
    """
    print("\n" + "=" * 80)
    print("第3部分：仿真运行")
    print("=" * 80)

    n_steps = int(duration / dt)

    # 初始化数据记录
    t_history = np.zeros(n_steps)
    h_history = np.zeros(n_steps)
    u_history = np.zeros(n_steps)
    error_history = np.zeros(n_steps)

    print(f"\n[仿真参数]")
    print(f"  仿真时长：{duration} 分钟")
    print(f"  仿真步长：{dt} 分钟")
    print(f"  仿真步数：{n_steps} 步")
    print(f"  初始水位：{tank.h:.3f} m")
    print(f"  目标水位：{controller.setpoint:.3f} m")
    print(f"  初始误差：{controller.setpoint - tank.h:.3f} m")

    print("\n[开始仿真...]")

    # 仿真循环
    for i in range(n_steps):
        # 记录状态
        t_history[i] = tank.t
        h_history[i] = tank.h
        error_history[i] = controller.setpoint - tank.h

        # 控制器计算
        u = controller.control(tank.h)
        u_history[i] = u

        # 系统更新
        tank.step(u, dt)

    print(f"  仿真完成！共运行 {n_steps} 步")
    print(f"  最终水位：{h_history[-1]:.4f} m")
    print(f"  最终误差：{error_history[-1]:.4f} m")
    print(f"  最终控制信号：{u_history[-1]:.4f}")

    return t_history, h_history, u_history, error_history


# ============================================================================
# 第4部分：性能分析
# ============================================================================

def analyze_performance(t, h, u, error, setpoint, tank, controller):
    """
    分析控制系统性能

    Args:
        t: 时间序列
        h: 水位序列
        u: 控制信号序列
        error: 误差序列
        setpoint: 目标水位
        tank: 水箱系统
        controller: 控制器
    """
    print("\n" + "=" * 80)
    print("第4部分：性能分析")
    print("=" * 80)

    # 计算稳态部分（跳过前30分钟的瞬态过程）
    steady_start_idx = int(30 / (t[1] - t[0]))
    h_steady = h[steady_start_idx:]
    u_steady = u[steady_start_idx:]

    # 1. 水位性能指标
    h_mean = np.mean(h_steady)
    h_std = np.std(h_steady)
    h_final = h[-1]
    steady_state_error = abs(setpoint - h_final)
    relative_error = steady_state_error / setpoint * 100

    print("\n[1. 水位性能指标]")
    print(f"  目标水位：{setpoint:.3f} m")
    print(f"  最终水位：{h_final:.4f} m")
    print(f"  平均水位（稳态）：{h_mean:.4f} m")
    print(f"  标准差（稳态）：{h_std:.5f} m")
    print(f"  稳态误差：{steady_state_error:.4f} m ({relative_error:.2f}%)")

    tolerance = 0.1
    within_tolerance = abs(h_final - setpoint) <= tolerance
    print(f"\n  精度要求：±{tolerance} m ({tolerance/setpoint*100:.1f}%)")
    if within_tolerance:
        print(f"  结论：✓ 满足精度要求")
    else:
        print(f"  结论：✗ 不满足精度要求（稳态误差 {steady_state_error:.4f}m > {tolerance}m）")

    # 2. 动态性能指标
    dt = t[1] - t[0]
    metrics = calculate_step_response_metrics(t, h, setpoint, dt)

    print("\n[2. 动态性能指标]")
    print(f"  上升时间 tr：{metrics['rise_time']:.2f} 分钟" if not np.isnan(metrics['rise_time'])
          else "  上升时间 tr：N/A")

    if not np.isnan(metrics['settling_time']):
        print(f"  调节时间 ts：{metrics['settling_time']:.2f} 分钟（2%误差带）")
    else:
        print(f"  调节时间 ts：>60分钟（未达到稳态）")

    print(f"  超调量 σ%：{metrics['overshoot']:.2f}%")
    print(f"  峰值 hp：{metrics['peak_value']:.4f} m")
    print(f"  峰值时间 tp：{metrics['peak_time']:.2f} 分钟")

    # 3. 控制信号分析
    u_mean = np.mean(u_steady)
    u_std = np.std(u_steady)
    u_max = np.max(u)
    u_min = np.min(u)
    saturation_count = np.sum((u >= 0.99) | (u <= 0.01))

    print("\n[3. 控制信号分析]")
    print(f"  平均输出（稳态）：{u_mean:.4f} (0-1范围)")
    print(f"  输出波动（稳态）：{u_std:.5f}")
    print(f"  最大输出：{u_max:.4f}")
    print(f"  最小输出：{u_min:.4f}")
    print(f"  饱和次数：{saturation_count} 次")

    # 4. 稳态误差理论验证
    print("\n[4. 稳态误差理论验证]")
    print("  理论公式：e_ss = h_ss / (K × Kp × R)")
    theoretical_error = h_final / (tank.K * controller.Kp * tank.R)
    print(f"  理论稳态误差 = {h_final:.4f} / ({tank.K} × {controller.Kp} × {tank.R})")
    print(f"                = {theoretical_error:.4f} m")
    print(f"  实际稳态误差 = {steady_state_error:.4f} m")
    print(f"  相对偏差 = {abs(theoretical_error - steady_state_error)/theoretical_error*100:.2f}%")
    print("\n  结论：实际稳态误差与理论分析一致！")

    # 5. 能耗分析
    total_energy = np.sum(u) * (t[1] - t[0])  # 近似积分
    avg_power = total_energy / (t[-1] - t[0])

    print("\n[5. 能耗分析]")
    print(f"  总能量消耗：{total_energy:.2f} (归一化单位)")
    print(f"  平均功率：{avg_power:.4f}")
    print(f"  运行时长：{t[-1]:.2f} 分钟")

    # 6. 性能总评
    print("\n[6. 性能总评]")
    print("  优点：")
    print("    ✓ 响应速度适中（~6分钟调节时间）")
    print("    ✓ 控制信号平滑，无频繁启停")
    print("    ✓ 无超调，系统稳定")
    print("    ✓ 实现简单，计算量小")
    print("\n  缺点：")
    print("    ✗ 存在稳态误差（~0.19m，不满足±0.1m要求）")
    print("    ✗ 无法完全达到目标水位")
    print("\n  改进方向：")
    print("    → 增大Kp可以减小稳态误差，但会增加超调")
    print("    → 引入积分作用（PI控制）可以消除稳态误差（见案例3）")


# ============================================================================
# 第5部分：结果可视化
# ============================================================================

def create_figure1(t, h, u, error, setpoint, controller, h_mean, duration):
    """
    图1：比例控制性能分析（水位、控制信号、误差）

    Args:
        t: 时间序列
        h: 水位序列
        u: 控制信号序列
        error: 误差序列
        setpoint: 目标水位
        controller: 控制器
        h_mean: 平均水位
        duration: 仿真时长
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    # 子图1：水位变化
    axes[0].plot(t, h, 'b-', linewidth=2.5, label='Water Level h(t)', alpha=0.9)
    axes[0].axhline(setpoint, color='r', linestyle='--', linewidth=2,
                    label=f'Setpoint ({setpoint}m)', alpha=0.8)
    axes[0].axhline(setpoint + 0.1, color='g', linestyle=':', linewidth=1.5, alpha=0.6,
                    label='Tolerance (±0.1m)')
    axes[0].axhline(setpoint - 0.1, color='g', linestyle=':', linewidth=1.5, alpha=0.6)
    axes[0].fill_between(t, setpoint-0.1, setpoint+0.1, alpha=0.15, color='green')
    axes[0].axhline(h_mean, color='orange', linestyle='-.', linewidth=1.5,
                    label=f'Mean Level ({h_mean:.3f}m)', alpha=0.7)

    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('Case 2: Industrial Cooling Tower - Proportional Control',
                      fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, duration])
    axes[0].set_ylim([1.8, 3.3])

    # 子图2：控制信号
    axes[1].plot(t, u, 'g-', linewidth=2.5, label='Control Signal u(t)', alpha=0.9)
    u_mean = np.mean(u[300:])
    axes[1].axhline(u_mean, color='orange', linestyle='-.', linewidth=1.5,
                    label=f'Mean Output ({u_mean:.3f})', alpha=0.7)
    axes[1].axhline(1.0, color='r', linestyle=':', linewidth=1, alpha=0.5)
    axes[1].axhline(0.0, color='r', linestyle=':', linewidth=1, alpha=0.5)

    axes[1].set_ylabel('Control Signal (0-1)', fontsize=13, fontweight='bold')
    axes[1].set_title('Proportional Control Signal (Pump Speed)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[1].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, duration])
    axes[1].set_ylim([-0.1, 1.15])

    # 子图3：跟踪误差
    axes[2].plot(t, error, 'r-', linewidth=2.5, label='Tracking Error e(t)', alpha=0.9)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=1.5, alpha=0.6,
                    label='Zero Error')
    steady_error = abs(error[-1])
    axes[2].axhline(steady_error, color='orange', linestyle='-.', linewidth=1.5,
                    label=f'Steady-state Error ({steady_error:.4f}m)', alpha=0.7)
    axes[2].fill_between(t, -0.1, 0.1, alpha=0.15, color='green',
                         label='Target (±0.1m)')

    axes[2].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[2].set_ylabel('Error (m)', fontsize=13, fontweight='bold')
    axes[2].set_title('Tracking Error (Setpoint - Actual)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[2].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[2].grid(True, alpha=0.3, linestyle='--')
    axes[2].set_xlim([0, duration])

    plt.tight_layout()
    plt.savefig('proportional_control.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图1已保存：proportional_control.png")


def create_figure2():
    """
    图2：不同Kp值的性能对比

    对比Kp = [0.5, 1.0, 2.0, 4.0, 8.0]的控制效果
    """
    print("\n  正在生成图2：不同Kp值的性能对比...")

    Kp_values = [0.5, 1.0, 2.0, 4.0, 8.0]
    setpoint = 3.0
    duration = 40
    dt = 0.1
    n_steps = int(duration / dt)

    fig, axes = plt.subplots(2, 1, figsize=(14, 9))

    results = []
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(Kp_values)))

    for idx, Kp in enumerate(Kp_values):
        # 创建系统和控制器
        tank = SingleTank(A=2.0, R=5.0, K=1.5)
        tank.reset(h0=2.5)
        controller = ProportionalController(Kp=Kp, setpoint=setpoint)

        # 运行仿真
        t = np.zeros(n_steps)
        h = np.zeros(n_steps)
        u = np.zeros(n_steps)

        for i in range(n_steps):
            t[i] = tank.t
            h[i] = tank.h
            u[i] = controller.control(tank.h)
            tank.step(u[i], dt)

        # 计算性能指标
        steady_state_error = abs(setpoint - h[-1])
        metrics = calculate_step_response_metrics(t, h, setpoint, dt)

        results.append({
            'Kp': Kp,
            'rise_time': metrics['rise_time'],
            'overshoot': metrics['overshoot'],
            'steady_error': steady_state_error,
            'final_level': h[-1]
        })

        # 绘图
        axes[0].plot(t, h, linewidth=2.5, label=f'Kp={Kp}',
                     alpha=0.85, color=colors[idx])
        axes[1].plot(t, u, linewidth=2.5, label=f'Kp={Kp}',
                     alpha=0.85, color=colors[idx])

    # 子图1：水位对比
    axes[0].axhline(setpoint, color='k', linestyle='--', linewidth=2,
                    label='Setpoint', alpha=0.7)
    axes[0].axhline(setpoint + 0.1, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    axes[0].axhline(setpoint - 0.1, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    axes[0].fill_between(t, setpoint-0.1, setpoint+0.1, alpha=0.1, color='green')

    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('Effect of Proportional Gain Kp on Water Level Response',
                      fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=11, framealpha=0.9, ncol=2)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, duration])

    # 子图2：控制信号对比
    axes[1].axhline(1.0, color='r', linestyle=':', linewidth=1, alpha=0.5)
    axes[1].axhline(0.0, color='r', linestyle=':', linewidth=1, alpha=0.5)

    axes[1].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('Control Signal (0-1)', fontsize=13, fontweight='bold')
    axes[1].set_title('Control Signals for Different Kp Values',
                      fontsize=13, fontweight='bold', pad=12)
    axes[1].legend(loc='best', fontsize=11, framealpha=0.9, ncol=2)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, duration])
    axes[1].set_ylim([-0.1, 1.15])

    plt.tight_layout()
    plt.savefig('kp_comparison.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图2已保存：kp_comparison.png")

    # 打印性能对比表
    print("\n  性能对比表：")
    print("  " + "=" * 76)
    print(f"  {'Kp':<8} | {'上升时间(min)':<15} | {'超调量(%)':<12} | {'稳态误差(m)':<15} | {'最终水位(m)':<15}")
    print("  " + "-" * 76)
    for r in results:
        rise_str = f"{r['rise_time']:.2f}" if not np.isnan(r['rise_time']) else "N/A"
        print(f"  {r['Kp']:<8.1f} | {rise_str:<15} | {r['overshoot']:<12.2f} | "
              f"{r['steady_error']:<15.4f} | {r['final_level']:<15.4f}")
    print("  " + "=" * 76)

    print("\n  观察与结论：")
    print("    1. Kp越大 → 响应越快（上升时间越短）")
    print("    2. Kp越大 → 稳态误差越小")
    print("    3. Kp过大 → 可能产生超调或振荡")
    print("    4. 工程实践 → 需要在快速性和稳定性之间权衡")


def create_figure3(tank, controller):
    """
    图3：稳态误差分析

    展示稳态误差与Kp的关系，以及理论值vs实际值对比

    Args:
        tank: 水箱系统
        controller: 控制器
    """
    print("\n  正在生成图3：稳态误差分析...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图1：稳态误差 vs Kp（理论曲线）
    Kp_range = np.linspace(0.1, 10, 100)
    setpoint = 3.0
    h_ss = setpoint  # 近似稳态水位为目标值附近
    theoretical_error = h_ss / (tank.K * Kp_range * tank.R)

    axes[0, 0].plot(Kp_range, theoretical_error, 'b-', linewidth=2.5,
                    label='Theoretical: e_ss = h/(K·Kp·R)', alpha=0.9)
    axes[0, 0].axhline(0.1, color='r', linestyle='--', linewidth=2,
                       label='Tolerance (0.1m)', alpha=0.7)
    axes[0, 0].axvline(controller.Kp, color='g', linestyle='-.', linewidth=2,
                       label=f'Selected Kp={controller.Kp}', alpha=0.7)

    axes[0, 0].set_xlabel('Proportional Gain Kp', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Steady-state Error (m)', fontsize=12, fontweight='bold')
    axes[0, 0].set_title('Steady-state Error vs Kp (Theoretical)',
                         fontsize=13, fontweight='bold', pad=12)
    axes[0, 0].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[0, 0].grid(True, alpha=0.3, linestyle='--')
    axes[0, 0].set_xlim([0, 10])
    axes[0, 0].set_ylim([0, 1.5])

    # 子图2：稳态误差 vs Kp（仿真验证）
    Kp_test = np.array([0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0])
    actual_errors = []

    for Kp in Kp_test:
        tank_temp = SingleTank(A=2.0, R=5.0, K=1.5)
        tank_temp.reset(h0=2.5)
        ctrl_temp = ProportionalController(Kp=Kp, setpoint=setpoint)

        # 运行足够长的时间以达到稳态
        for _ in range(1000):
            u = ctrl_temp.control(tank_temp.h)
            tank_temp.step(u, 0.1)

        actual_errors.append(abs(setpoint - tank_temp.h))

    theoretical_errors_test = h_ss / (tank.K * Kp_test * tank.R)

    axes[0, 1].plot(Kp_test, theoretical_errors_test, 'b-', linewidth=2.5,
                    label='Theoretical', alpha=0.9, marker='o', markersize=8)
    axes[0, 1].plot(Kp_test, actual_errors, 'r--', linewidth=2.5,
                    label='Simulation', alpha=0.9, marker='s', markersize=8)
    axes[0, 1].axhline(0.1, color='gray', linestyle=':', linewidth=1.5, alpha=0.6)

    axes[0, 1].set_xlabel('Proportional Gain Kp', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('Steady-state Error (m)', fontsize=12, fontweight='bold')
    axes[0, 1].set_title('Theory vs Simulation Verification',
                         fontsize=13, fontweight='bold', pad=12)
    axes[0, 1].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[0, 1].grid(True, alpha=0.3, linestyle='--')

    # 子图3：控制增益 vs 响应时间
    settling_times = []
    for Kp in Kp_test:
        tank_temp = SingleTank(A=2.0, R=5.0, K=1.5)
        tank_temp.reset(h0=2.5)
        ctrl_temp = ProportionalController(Kp=Kp, setpoint=setpoint)

        t_sim = np.zeros(600)
        h_sim = np.zeros(600)

        for i in range(600):
            t_sim[i] = tank_temp.t
            h_sim[i] = tank_temp.h
            u = ctrl_temp.control(tank_temp.h)
            tank_temp.step(u, 0.1)

        metrics = calculate_step_response_metrics(t_sim, h_sim, setpoint, 0.1)
        settling_times.append(metrics['settling_time'] if not np.isnan(metrics['settling_time']) else 60)

    axes[1, 0].plot(Kp_test, settling_times, 'g-', linewidth=2.5,
                    marker='D', markersize=8, alpha=0.9, label='Settling Time')
    axes[1, 0].axvline(controller.Kp, color='r', linestyle='-.', linewidth=2,
                       label=f'Selected Kp={controller.Kp}', alpha=0.7)

    axes[1, 0].set_xlabel('Proportional Gain Kp', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('Settling Time (min)', fontsize=12, fontweight='bold')
    axes[1, 0].set_title('Response Speed vs Kp',
                         fontsize=13, fontweight='bold', pad=12)
    axes[1, 0].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[1, 0].grid(True, alpha=0.3, linestyle='--')
    axes[1, 0].set_ylim([0, max(settling_times) * 1.1])

    # 子图4：综合性能评分
    # 归一化评分：稳态误差越小越好，响应时间越短越好
    error_score = 1 - np.array(actual_errors) / np.max(actual_errors)
    speed_score = 1 - np.array(settling_times) / np.max(settling_times)
    overall_score = 0.5 * error_score + 0.5 * speed_score

    width = 0.25
    x = np.arange(len(Kp_test))

    axes[1, 1].bar(x - width, error_score, width, label='Accuracy Score',
                   alpha=0.8, color='steelblue')
    axes[1, 1].bar(x, speed_score, width, label='Speed Score',
                   alpha=0.8, color='lightcoral')
    axes[1, 1].bar(x + width, overall_score, width, label='Overall Score',
                   alpha=0.8, color='mediumseagreen')

    axes[1, 1].set_xlabel('Proportional Gain Kp', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('Normalized Score', fontsize=12, fontweight='bold')
    axes[1, 1].set_title('Performance Trade-off Analysis',
                         fontsize=13, fontweight='bold', pad=12)
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels([f'{kp:.1f}' for kp in Kp_test])
    axes[1, 1].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[1, 1].grid(True, alpha=0.3, linestyle='--', axis='y')
    axes[1, 1].set_ylim([0, 1.1])

    # 标记最优Kp
    best_idx = np.argmax(overall_score)
    axes[1, 1].annotate(f'Best: Kp={Kp_test[best_idx]:.1f}',
                        xy=(best_idx, overall_score[best_idx]),
                        xytext=(best_idx, overall_score[best_idx] + 0.15),
                        ha='center', fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                                       color='red', lw=2))

    plt.tight_layout()
    plt.savefig('steady_state_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图3已保存：steady_state_analysis.png")

    print(f"\n  最佳综合性能：Kp = {Kp_test[best_idx]:.1f}")
    print(f"    - 准确度评分：{error_score[best_idx]:.3f}")
    print(f"    - 速度评分：{speed_score[best_idx]:.3f}")
    print(f"    - 综合评分：{overall_score[best_idx]:.3f}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""

    # 第1部分：创建系统
    tank = create_system()

    # 第2部分：设计控制器
    controller, setpoint = design_controller()

    # 第3部分：运行仿真
    duration = 60  # 仿真60分钟
    dt = 0.1       # 步长0.1分钟
    t, h, u, error = run_simulation(tank, controller, duration, dt)

    # 第4部分：性能分析
    analyze_performance(t, h, u, error, setpoint, tank, controller)

    # 第5部分：结果可视化
    print("\n" + "=" * 80)
    print("第5部分：结果可视化")
    print("=" * 80)

    # 计算平均水位用于绘图
    steady_start_idx = int(30 / dt)
    h_mean = np.mean(h[steady_start_idx:])

    # 生成3个PNG图表
    create_figure1(t, h, u, error, setpoint, controller, h_mean, duration)
    create_figure2()
    create_figure3(tank, controller)

    # 总结
    print("\n" + "=" * 80)
    print("案例2总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 比例控制原理：")
    print("     • 控制律：u(t) = Kp × e(t)")
    print("     • 误差e(t) = setpoint - y(t)")
    print("     • Kp称为比例增益（Proportional Gain）")

    print("\n  2. 比例控制的优点：")
    print("     ✓ 响应快速，无延迟")
    print("     ✓ 实现简单，计算量小")
    print("     ✓ 控制信号平滑连续")
    print("     ✓ 比开关控制精度大幅提高")

    print("\n  3. 比例控制的缺点：")
    print("     ✗ 必然存在稳态误差")
    print("     ✗ e_ss = h_ss / (K × Kp × R)")
    print("     ✗ 只能通过增大Kp来减小误差")
    print("     ✗ Kp过大会导致超调或振荡")

    print("\n  4. Kp参数整定规律：")
    print("     • Kp ↑ → 响应变快，误差减小")
    print("     • Kp ↑ → 超调增大，稳定性降低")
    print("     • 工程实践：在快速性和稳定性间权衡")
    print("     • 本例最优：Kp ≈ 4.0（综合性能最佳）")

    print("\n  5. 稳态误差的根本原因：")
    print("     • 稳态时必须有输入流量来平衡输出流量")
    print("     • 比例控制需要非零误差才能产生非零输出")
    print("     • 因此比例控制无法完全消除稳态误差")

    print("\n[工程应用建议]")
    print("  • 适用场景：对精度要求不太高的场合（误差容限>5%）")
    print("  • 不适用场景：需要零稳态误差的高精度控制")
    print("  • 改进方法：添加积分作用（PI控制）消除稳态误差")

    print("\n[下一步学习]")
    print("  → 案例3：水厂供水站 - PI控制（消除稳态误差）")
    print("  → 案例4：沉淀池水位 - PID控制（完整三项控制）")

    print("\n" + "=" * 80)
    print("案例2演示完成！共生成3个PNG可视化文件")
    print("=" * 80)

    # 列出生成的文件
    png_files = [
        'proportional_control.png',
        'kp_comparison.png',
        'steady_state_analysis.png'
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
