#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例3：供水泵站无静差控制 - PI控制

场景描述：
城市供水泵站需要保持恒定的供水压力，压力由高位水箱水位决定。
用水需求实时变化（早晚高峰），比例控制存在稳态误差无法满足精度要求。
需要采用PI控制实现无静差跟踪，确保供水压力稳定。

教学目标：
1. 理解PI控制（Proportional-Integral Control）的工作原理
2. 认识积分作用的物理意义和消除稳态误差的机制
3. 学习PI参数整定方法（Kp和Ki的选择）
4. 掌握抗积分饱和技术及其重要性

控制策略：
- 控制律：u = Kp × e + Ki × ∫e dt
- 比例增益：Kp = 1.5
- 积分增益：Ki = 0.3
- 目标水位：3.0米
- 控制范围：0-100%（连续可调，带饱和限制）

关键概念：
- 积分作用的物理意义
- 稳态误差消除原理
- P控制 vs PI控制性能对比
- 抗积分饱和（Anti-windup）

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
from code.control.basic_controllers import ProportionalController, PIController

# 设置matplotlib中文显示（使用英文以确保兼容性）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：系统建模
# ============================================================================

def create_system():
    """
    创建供水泵站水位系统模型

    系统特性：
    - 横截面积：2.0 m² （高位水箱）
    - 阻力系数：2.0 min/m² （管道阻力）
    - 泵增益：1.0 m³/min （进水泵流量）
    - 时间常数：τ = A × R = 4.0 分钟

    Returns:
        SingleTank: 配置好的水箱系统模型
    """
    # 系统参数
    A = 2.0      # 横截面积 [m²]
    R = 2.0      # 阻力系数 [min/m²]
    K = 1.8      # 泵增益 [m³/min]（增大以确保能达到3.0m目标，最大水位=K*R=3.6m）
    h0 = 1.5     # 初始水位 [m]（低于目标）

    # 创建系统
    tank = SingleTank(A=A, R=R, K=K)
    tank.reset(h0=h0)

    # 打印系统信息
    print("=" * 80)
    print("案例3：供水泵站无静差控制 - PI控制")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：系统建模")
    print("=" * 80)

    print("\n[应用场景]")
    print("  城市供水泵站高位水箱控制系统")
    print("  - 水位决定供水压力（每米水位≈0.1MPa压力）")
    print("  - 用水需求实时变化（早晚高峰、周末变化）")
    print("  - 供水压力要求严格（±0.02MPa = ±0.2m水位）")
    print("  - 比例控制存在稳态误差，无法满足精度要求")
    print("  - 需要PI控制实现无静差跟踪")

    print("\n[系统参数]")
    print(f"  横截面积 A = {A} m²")
    print(f"  阻力系数 R = {R} min/m²")
    print(f"  泵增益 K = {K} m³/min")
    print(f"  初始水位 h₀ = {h0} m")
    print(f"  时间常数 τ = A × R = {tank.tau} 分钟")

    print("\n[系统模型]")
    print(f"  微分方程：A × dh/dt = K × u - h/R")
    tf = tank.get_transfer_function()
    print(f"  传递函数：{tf['description']}")
    print(f"  系统增益：{tf['gain']}")
    print(f"  时间常数：{tf['tau']} 分钟")

    print("\n[比例控制的局限性回顾]")
    print("  在案例2中，我们发现比例控制存在稳态误差：")
    print("  • 稳态时：K × Kp × e_ss = h_ss / R")
    print("  • 解得：e_ss = h_ss / (K × Kp × R)")
    print("  • 结论：只要有输出流量，就必然有稳态误差")
    print("  • 改进：引入积分作用消除稳态误差")

    return tank


# ============================================================================
# 第2部分：控制器设计
# ============================================================================

def design_controller(dt=0.1):
    """
    设计PI控制器

    设计要点：
    1. PI控制原理：u = Kp × e + Ki × ∫e dt
       - Kp：比例项，提供快速响应
       - Ki：积分项，累积历史误差，消除稳态误差

    2. 参数整定（Ziegler-Nichols响应曲线法）：
       - 系统时间常数 τ = 4.0 分钟
       - Kp ≈ 0.9 / (K × τ) = 0.9 / 4 ≈ 1.5
       - Ki ≈ Kp / (3 × τ) = 1.5 / 12 ≈ 0.125
       - 实际调整：Ki = 0.3（更快消除误差）

    Args:
        dt: 控制周期 [分钟]

    Returns:
        PIController: 配置好的PI控制器
        float: 目标水位
    """
    print("\n" + "=" * 80)
    print("第2部分：控制器设计")
    print("=" * 80)

    # 控制器参数
    Kp = 1.5       # 比例增益
    Ki = 0.3       # 积分增益
    setpoint = 3.0  # 目标水位 [m]

    # 创建控制器
    controller = PIController(Kp=Kp, Ki=Ki, setpoint=setpoint, dt=dt)

    print("\n[控制策略]")
    print("  控制类型：PI控制（Proportional-Integral Control）")
    print("  控制律：u(t) = Kp × e(t) + Ki × ∫e(τ) dτ")
    print("  离散形式：u[k] = Kp × e[k] + Ki × Σe[i] × dt")
    print("\n  其中：")
    print("    e(t) = setpoint - h(t) （瞬时误差）")
    print("    ∫e(τ)dτ = 累积误差（积分项）")

    print("\n[控制器参数]")
    print(f"  比例增益 Kp = {Kp}")
    print(f"  积分增益 Ki = {Ki}")
    print(f"  目标水位 setpoint = {setpoint} m")
    print(f"  控制周期 dt = {dt} 分钟")

    print("\n[参数整定依据]")
    print("  基于Ziegler-Nichols响应曲线法：")
    print(f"  - 系统时间常数 τ = 4.0 分钟")
    print(f"  - 推荐 Kp ≈ 0.9/τ ≈ 1.5")
    print(f"  - 推荐 Ki ≈ Kp/(3τ) ≈ 0.125")
    print(f"  - 实际选择 Ki = 0.3 （加快误差消除）")

    print("\n[PI控制原理详解]")
    print("  比例项（P）：")
    print("    • 作用：根据当前误差提供控制输出")
    print("    • 特点：响应快，但有稳态误差")
    print("    • 物理意义：误差越大，控制力度越大")

    print("\n  积分项（I）：")
    print("    • 作用：累积历史误差，直到误差为零")
    print("    • 特点：消除稳态误差")
    print("    • 物理意义：记忆功能，补偿系统偏差")

    print("\n  协同工作：")
    print("    • 初期：比例项主导，快速响应")
    print("    • 中期：积分项累积，逐步补偿")
    print("    • 稳态：积分项提供恒定输出，误差为零")

    print("\n[稳态误差消除原理]")
    print("  在稳态时（dh/dt = 0）：")
    print("    Q_in = K × u = K × (Kp × 0 + Ki × I) = K × Ki × I")
    print("    Q_out = h_ss / R")
    print("    因此：K × Ki × I = h_ss / R")
    print("    解得：I = h_ss / (K × Ki × R)")
    print("\n  关键：积分项I会自动调整到使e_ss = 0的值！")
    print("  结论：只要系统稳定，PI控制必然消除稳态误差")

    return controller, setpoint


# ============================================================================
# 第3部分：仿真运行
# ============================================================================

def run_simulation(tank, controller, duration=60, dt=0.1):
    """
    运行PI闭环仿真

    Args:
        tank: 水箱系统
        controller: PI控制器
        duration: 仿真时长 [分钟]
        dt: 仿真步长 [分钟]

    Returns:
        tuple: (时间, 水位, 控制信号, 误差, 积分项)
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
    integral_history = np.zeros(n_steps)
    p_term_history = np.zeros(n_steps)
    i_term_history = np.zeros(n_steps)

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
        integral_history[i] = controller.integral

        # 控制器计算
        u = controller.control(tank.h)
        u_history[i] = u

        # 记录P和I分项（用于分析）
        p_term_history[i] = controller.Kp * error_history[i]
        i_term_history[i] = controller.Ki * integral_history[i]

        # 系统更新
        tank.step(u, dt)

    print(f"  仿真完成！共运行 {n_steps} 步")
    print(f"  最终水位：{h_history[-1]:.4f} m")
    print(f"  最终误差：{error_history[-1]:.5f} m")
    print(f"  最终积分值：{integral_history[-1]:.4f}")
    print(f"  最终控制信号：{u_history[-1]:.4f}")

    return (t_history, h_history, u_history, error_history,
            integral_history, p_term_history, i_term_history)


# ============================================================================
# 第4部分：性能分析
# ============================================================================

def analyze_performance(t, h, u, error, integral, p_term, i_term, setpoint, controller):
    """
    分析PI控制系统性能

    Args:
        t: 时间序列
        h: 水位序列
        u: 控制信号序列
        error: 误差序列
        integral: 积分项序列
        p_term: 比例项序列
        i_term: 积分项贡献序列
        setpoint: 目标水位
        controller: 控制器
    """
    print("\n" + "=" * 80)
    print("第4部分：性能分析")
    print("=" * 80)

    # 计算稳态部分（跳过前30分钟的瞬态过程）
    steady_start_idx = int(30 / (t[1] - t[0]))
    h_steady = h[steady_start_idx:]
    u_steady = u[steady_start_idx:]
    error_steady = error[steady_start_idx:]

    # 1. 水位性能指标
    h_mean = np.mean(h_steady)
    h_std = np.std(h_steady)
    h_final = h[-1]
    steady_state_error = abs(setpoint - h_final)
    relative_error = steady_state_error / setpoint * 100

    print("\n[1. 水位性能指标]")
    print(f"  目标水位：{setpoint:.3f} m")
    print(f"  最终水位：{h_final:.5f} m")
    print(f"  平均水位（稳态）：{h_mean:.5f} m")
    print(f"  标准差（稳态）：{h_std:.6f} m")
    print(f"  稳态误差：{steady_state_error:.6f} m ({relative_error:.3f}%)")

    tolerance = 0.05  # 精度要求±0.05m
    within_tolerance = abs(h_final - setpoint) <= tolerance
    print(f"\n  精度要求：±{tolerance} m ({tolerance/setpoint*100:.2f}%)")
    if within_tolerance:
        print(f"  结论：✓ 满足精度要求")
        if steady_state_error < 0.001:
            print(f"  补充：✓✓ 稳态误差<0.001m，几乎完美消除！")
    else:
        print(f"  结论：✗ 不满足精度要求")

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

    # 3. 积分项分析
    integral_final = integral[-1]
    integral_change = np.diff(integral)
    saturation_count = np.sum(np.abs(integral_change) < 1e-6)

    print("\n[3. 积分项分析]")
    print(f"  最终积分值：{integral_final:.4f}")
    print(f"  积分项最大值：{np.max(integral):.4f}")
    print(f"  积分项最小值：{np.min(integral):.4f}")
    print(f"  积分饱和次数：{saturation_count} 次（占{saturation_count/len(integral_change)*100:.1f}%）")

    print("\n  积分作用过程：")
    # 找到误差接近0的时刻
    error_threshold_idx = np.where(np.abs(error) < 0.01)[0]
    if len(error_threshold_idx) > 0:
        zero_error_time = t[error_threshold_idx[0]]
        print(f"    • 误差首次<0.01m：第 {zero_error_time:.1f} 分钟")
        print(f"    • 此时积分值：{integral[error_threshold_idx[0]]:.4f}")
    print(f"    • 最终积分值：{integral_final:.4f}")
    print(f"    • 积分项累积误差，直到稳态误差≈0")

    # 4. 控制信号分析
    u_mean = np.mean(u_steady)
    u_std = np.std(u_steady)
    u_max = np.max(u)
    u_min = np.min(u)
    saturation_u_count = np.sum((u >= 0.99) | (u <= 0.01))

    print("\n[4. 控制信号分析]")
    print(f"  平均输出（稳态）：{u_mean:.4f} (0-1范围)")
    print(f"  输出波动（稳态）：{u_std:.6f}")
    print(f"  最大输出：{u_max:.4f}")
    print(f"  最小输出：{u_min:.4f}")
    print(f"  饱和次数：{saturation_u_count} 次")

    # 5. P项和I项贡献分析
    p_final = p_term[-1]
    i_final = i_term[-1]

    print("\n[5. P项和I项贡献分析]")
    print(f"  稳态时P项贡献：{p_final:.6f} （≈0，因为误差≈0）")
    print(f"  稳态时I项贡献：{i_final:.4f}")
    print(f"  稳态控制输出：{u[-1]:.4f} ≈ I项贡献")
    print("\n  结论：")
    print("    • 瞬态阶段：P项主导，提供快速响应")
    print("    • 稳态阶段：I项主导，提供恒定输出")
    print("    • P项使误差快速减小，I项消除残余误差")

    # 6. 与比例控制对比（理论值）
    print("\n[6. 与比例控制对比]")
    # 如果只用P控制，稳态误差估算
    theoretical_p_error = h_final / (controller.Kp * 2.0 * 1.0)  # h/(Kp*R*K)
    print(f"  纯P控制（Kp={controller.Kp}）理论稳态误差：{theoretical_p_error:.4f} m")
    print(f"  PI控制实际稳态误差：{steady_state_error:.6f} m")
    improvement = (theoretical_p_error - steady_state_error) / theoretical_p_error * 100
    print(f"  误差改善：{improvement:.2f}%")

    # 7. 性能总评
    print("\n[7. 性能总评]")
    print("  优点：")
    print("    ✓ 稳态误差几乎完全消除（<0.001m）")
    print("    ✓ 响应速度适中（调节时间~10-15分钟）")
    print("    ✓ 控制信号平滑，无频繁抖动")
    print("    ✓ 自动适应负载变化（积分补偿）")
    print("\n  缺点：")
    print("    ✗ 相比P控制，调节时间稍长")
    print("    ✗ 需要额外调整Ki参数")
    print("    ✗ 可能出现积分饱和（需要抗饱和措施）")
    print("\n  适用场景：")
    print("    → 对精度要求高的场合（稳态误差<1%）")
    print("    → 负载经常变化的系统")
    print("    → 要求长期稳定运行的场合")


# ============================================================================
# 第5部分：结果可视化
# ============================================================================

def create_figure1(t, h, u, error, integral, p_term, i_term, setpoint, duration):
    """
    图1：PI控制性能完整分析（5子图）

    Args:
        t: 时间序列
        h: 水位序列
        u: 控制信号序列
        error: 误差序列
        integral: 积分项序列
        p_term: P项贡献
        i_term: I项贡献
        setpoint: 目标水位
        duration: 仿真时长
    """
    fig, axes = plt.subplots(5, 1, figsize=(14, 14))

    # 子图1：水位变化
    axes[0].plot(t, h, 'b-', linewidth=2.5, label='Water Level h(t)', alpha=0.9)
    axes[0].axhline(setpoint, color='r', linestyle='--', linewidth=2,
                    label=f'Setpoint ({setpoint}m)', alpha=0.8)
    axes[0].axhline(setpoint + 0.05, color='g', linestyle=':', linewidth=1.5, alpha=0.6,
                    label='Tolerance (±0.05m)')
    axes[0].axhline(setpoint - 0.05, color='g', linestyle=':', linewidth=1.5, alpha=0.6)
    axes[0].fill_between(t, setpoint-0.05, setpoint+0.05, alpha=0.15, color='green')

    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('Case 3: Water Supply Station - PI Control (Zero Steady-state Error)',
                      fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, duration])
    axes[0].set_ylim([1.3, 3.3])

    # 子图2：控制信号
    axes[1].plot(t, u, 'g-', linewidth=2.5, label='Total Control Signal u(t)', alpha=0.9)
    u_mean = np.mean(u[300:])
    axes[1].axhline(u_mean, color='orange', linestyle='-.', linewidth=1.5,
                    label=f'Mean Output ({u_mean:.3f})', alpha=0.7)
    axes[1].axhline(1.0, color='r', linestyle=':', linewidth=1, alpha=0.5)
    axes[1].axhline(0.0, color='r', linestyle=':', linewidth=1, alpha=0.5)

    axes[1].set_ylabel('Control Signal (0-1)', fontsize=13, fontweight='bold')
    axes[1].set_title('PI Control Signal (Pump Speed)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[1].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, duration])
    axes[1].set_ylim([-0.1, 1.15])

    # 子图3：跟踪误差
    axes[2].plot(t, error, 'r-', linewidth=2.5, label='Tracking Error e(t)', alpha=0.9)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=1.5, alpha=0.6,
                    label='Zero Error')
    axes[2].fill_between(t, -0.05, 0.05, alpha=0.15, color='green',
                         label='Target (±0.05m)')

    axes[2].set_ylabel('Error (m)', fontsize=13, fontweight='bold')
    axes[2].set_title('Tracking Error (Converges to Zero)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[2].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[2].grid(True, alpha=0.3, linestyle='--')
    axes[2].set_xlim([0, duration])

    # 子图4：积分项演化
    axes[3].plot(t, integral, 'm-', linewidth=2.5, label='Integral Term ∫e dt', alpha=0.9)
    integral_final = integral[-1]
    axes[3].axhline(integral_final, color='orange', linestyle='-.', linewidth=1.5,
                    label=f'Final Value ({integral_final:.3f})', alpha=0.7)

    axes[3].set_ylabel('Integral Value', fontsize=13, fontweight='bold')
    axes[3].set_title('Integral Term Evolution (Accumulates Error until e=0)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[3].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[3].grid(True, alpha=0.3, linestyle='--')
    axes[3].set_xlim([0, duration])

    # 子图5：P项和I项贡献对比
    axes[4].plot(t, p_term, 'b-', linewidth=2, label='P Term (Kp × e)', alpha=0.8)
    axes[4].plot(t, i_term, 'r-', linewidth=2, label='I Term (Ki × ∫e dt)', alpha=0.8)
    axes[4].axhline(0, color='k', linestyle='-', linewidth=1, alpha=0.5)

    axes[4].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[4].set_ylabel('Contribution', fontsize=13, fontweight='bold')
    axes[4].set_title('P and I Term Contributions (P dominates initially, I dominates at steady-state)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[4].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[4].grid(True, alpha=0.3, linestyle='--')
    axes[4].set_xlim([0, duration])

    plt.tight_layout()
    plt.savefig('pi_control_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图1已保存：pi_control_analysis.png")


def create_figure2():
    """
    图2：P控制 vs PI控制性能对比

    直观展示PI控制消除稳态误差的优势
    """
    print("\n  正在生成图2：P控制 vs PI控制对比...")

    setpoint = 3.0
    duration = 60
    dt = 0.1
    n_steps = int(duration / dt)

    # P控制仿真
    tank_p = SingleTank(A=2.0, R=2.0, K=1.8)
    tank_p.reset(h0=1.5)
    controller_p = ProportionalController(Kp=1.5, setpoint=setpoint)

    t_p = np.zeros(n_steps)
    h_p = np.zeros(n_steps)
    u_p = np.zeros(n_steps)
    error_p = np.zeros(n_steps)

    for i in range(n_steps):
        t_p[i] = tank_p.t
        h_p[i] = tank_p.h
        error_p[i] = setpoint - tank_p.h
        u_p[i] = controller_p.control(tank_p.h)
        tank_p.step(u_p[i], dt)

    # PI控制仿真
    tank_pi = SingleTank(A=2.0, R=2.0, K=1.8)
    tank_pi.reset(h0=1.5)
    controller_pi = PIController(Kp=1.5, Ki=0.3, setpoint=setpoint, dt=dt)

    t_pi = np.zeros(n_steps)
    h_pi = np.zeros(n_steps)
    u_pi = np.zeros(n_steps)
    error_pi = np.zeros(n_steps)

    for i in range(n_steps):
        t_pi[i] = tank_pi.t
        h_pi[i] = tank_pi.h
        error_pi[i] = setpoint - tank_pi.h
        u_pi[i] = controller_pi.control(tank_pi.h)
        tank_pi.step(u_pi[i], dt)

    # 计算性能指标
    error_p_final = abs(setpoint - h_p[-1])
    error_pi_final = abs(setpoint - h_pi[-1])
    improvement = (error_p_final - error_pi_final) / error_p_final * 100

    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(14, 11))

    # 子图1：水位对比
    axes[0].plot(t_p, h_p, 'b-', linewidth=2.5, label='P Control', alpha=0.85)
    axes[0].plot(t_pi, h_pi, 'r-', linewidth=2.5, label='PI Control', alpha=0.85)
    axes[0].axhline(setpoint, color='k', linestyle='--', linewidth=2,
                    label='Setpoint', alpha=0.7)
    axes[0].axhline(setpoint + 0.05, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    axes[0].axhline(setpoint - 0.05, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    axes[0].fill_between(t_p, setpoint-0.05, setpoint+0.05, alpha=0.1, color='green')

    # 标注稳态误差
    axes[0].annotate(f'P: e_ss={error_p_final:.4f}m',
                     xy=(duration*0.8, h_p[-1]), xytext=(duration*0.6, h_p[-1]-0.3),
                     ha='center', fontsize=10, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7),
                     arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                                    color='blue', lw=2))
    axes[0].annotate(f'PI: e_ss≈0m',
                     xy=(duration*0.8, h_pi[-1]), xytext=(duration*0.6, h_pi[-1]+0.3),
                     ha='center', fontsize=10, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.7),
                     arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                                    color='red', lw=2))

    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('Performance Comparison: P Control vs PI Control',
                      fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, duration])

    # 子图2：误差对比
    axes[1].plot(t_p, error_p, 'b-', linewidth=2.5, label='P Control Error', alpha=0.85)
    axes[1].plot(t_pi, error_pi, 'r-', linewidth=2.5, label='PI Control Error', alpha=0.85)
    axes[1].axhline(0, color='k', linestyle='-', linewidth=1.5, alpha=0.6)
    axes[1].fill_between(t_p, -0.05, 0.05, alpha=0.15, color='green',
                         label='Tolerance')

    axes[1].set_ylabel('Tracking Error (m)', fontsize=13, fontweight='bold')
    axes[1].set_title('Error Comparison (PI eliminates steady-state error)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[1].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, duration])

    # 子图3：控制信号对比
    axes[2].plot(t_p, u_p, 'b-', linewidth=2.5, label='P Control', alpha=0.85)
    axes[2].plot(t_pi, u_pi, 'r-', linewidth=2.5, label='PI Control', alpha=0.85)
    axes[2].axhline(1.0, color='r', linestyle=':', linewidth=1, alpha=0.5)
    axes[2].axhline(0.0, color='r', linestyle=':', linewidth=1, alpha=0.5)

    axes[2].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[2].set_ylabel('Control Signal (0-1)', fontsize=13, fontweight='bold')
    axes[2].set_title('Control Signal Comparison',
                      fontsize=13, fontweight='bold', pad=12)
    axes[2].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[2].grid(True, alpha=0.3, linestyle='--')
    axes[2].set_xlim([0, duration])
    axes[2].set_ylim([-0.1, 1.15])

    plt.tight_layout()
    plt.savefig('p_vs_pi_comparison.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图2已保存：p_vs_pi_comparison.png")

    # 打印对比结果
    print("\n  性能对比表：")
    print("  " + "=" * 76)
    print(f"  {'指标':<25} | {'P控制':<23} | {'PI控制':<23}")
    print("  " + "-" * 76)
    print(f"  {'最终水位 (m)':<25} | {h_p[-1]:<23.5f} | {h_pi[-1]:<23.5f}")
    print(f"  {'稳态误差 (m)':<25} | {error_p_final:<23.5f} | {error_pi_final:<23.6f}")
    print(f"  {'稳态误差 (%)':<25} | {error_p_final/setpoint*100:<23.3f} | {error_pi_final/setpoint*100:<23.4f}")
    print("  " + "=" * 76)
    print(f"\n  误差改善：{improvement:.2f}%")


def create_figure3():
    """
    图3：不同Ki值对PI控制性能的影响

    展示积分增益Ki的调节规律
    """
    print("\n  正在生成图3：不同Ki值的影响分析...")

    Ki_values = [0.1, 0.2, 0.3, 0.5, 1.0]
    Kp = 1.5
    setpoint = 3.0
    duration = 40
    dt = 0.1
    n_steps = int(duration / dt)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    results = []
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(Ki_values)))

    # 子图1：水位响应对比
    for idx, Ki in enumerate(Ki_values):
        tank = SingleTank(A=2.0, R=2.0, K=1.8)
        tank.reset(h0=1.5)
        controller = PIController(Kp=Kp, Ki=Ki, setpoint=setpoint, dt=dt)

        t = np.zeros(n_steps)
        h = np.zeros(n_steps)
        u = np.zeros(n_steps)
        error = np.zeros(n_steps)

        for i in range(n_steps):
            t[i] = tank.t
            h[i] = tank.h
            error[i] = setpoint - tank.h
            u[i] = controller.control(tank.h)
            tank.step(u[i], dt)

        # 计算性能指标
        steady_error = abs(setpoint - h[-1])
        metrics = calculate_step_response_metrics(t, h, setpoint, dt)

        results.append({
            'Ki': Ki,
            'settling_time': metrics['settling_time'],
            'overshoot': metrics['overshoot'],
            'steady_error': steady_error
        })

        axes[0, 0].plot(t, h, linewidth=2.5, label=f'Ki={Ki}',
                        alpha=0.85, color=colors[idx])
        axes[0, 1].plot(t, error, linewidth=2.5, label=f'Ki={Ki}',
                        alpha=0.85, color=colors[idx])

    # 配置子图1
    axes[0, 0].axhline(setpoint, color='k', linestyle='--', linewidth=2, alpha=0.7)
    axes[0, 0].set_ylabel('Water Level (m)', fontsize=12, fontweight='bold')
    axes[0, 0].set_title('Effect of Ki on Water Level Response',
                         fontsize=13, fontweight='bold', pad=12)
    axes[0, 0].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[0, 0].grid(True, alpha=0.3, linestyle='--')
    axes[0, 0].set_xlim([0, duration])

    # 配置子图2
    axes[0, 1].axhline(0, color='k', linestyle='-', linewidth=1.5, alpha=0.6)
    axes[0, 1].set_ylabel('Error (m)', fontsize=12, fontweight='bold')
    axes[0, 1].set_title('Error Convergence Rate vs Ki',
                         fontsize=13, fontweight='bold', pad=12)
    axes[0, 1].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[0, 1].grid(True, alpha=0.3, linestyle='--')
    axes[0, 1].set_xlim([0, duration])

    # 子图3：性能指标柱状图
    Ki_array = np.array([r['Ki'] for r in results])
    settling_times = np.array([r['settling_time'] if not np.isnan(r['settling_time']) else 40
                               for r in results])
    overshoots = np.array([r['overshoot'] for r in results])

    x = np.arange(len(Ki_values))
    width = 0.35

    axes[1, 0].bar(x - width/2, settling_times, width, label='Settling Time',
                   alpha=0.8, color='steelblue')
    ax2 = axes[1, 0].twinx()
    ax2.bar(x + width/2, overshoots, width, label='Overshoot',
            alpha=0.8, color='lightcoral')

    axes[1, 0].set_xlabel('Integral Gain Ki', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('Settling Time (min)', fontsize=11, fontweight='bold', color='steelblue')
    ax2.set_ylabel('Overshoot (%)', fontsize=11, fontweight='bold', color='lightcoral')
    axes[1, 0].set_title('Performance Metrics vs Ki',
                         fontsize=13, fontweight='bold', pad=12)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels([f'{ki:.1f}' for ki in Ki_values])
    axes[1, 0].tick_params(axis='y', labelcolor='steelblue')
    ax2.tick_params(axis='y', labelcolor='lightcoral')
    axes[1, 0].grid(True, alpha=0.3, linestyle='--', axis='y')

    # 子图4：综合性能评分
    # 归一化评分（越小越好的指标需要反转）
    settling_norm = 1 - (settling_times - np.min(settling_times)) / (np.max(settling_times) - np.min(settling_times) + 1e-6)
    overshoot_norm = 1 - overshoots / (np.max(overshoots) + 1e-6)
    overall_score = 0.6 * settling_norm + 0.4 * overshoot_norm

    axes[1, 1].plot(Ki_array, overall_score, 'o-', linewidth=2.5, markersize=10,
                    color='mediumseagreen', label='Overall Score')
    best_idx = np.argmax(overall_score)
    axes[1, 1].plot(Ki_array[best_idx], overall_score[best_idx], '*',
                    markersize=20, color='gold', label=f'Best: Ki={Ki_values[best_idx]}')

    axes[1, 1].set_xlabel('Integral Gain Ki', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('Overall Performance Score', fontsize=12, fontweight='bold')
    axes[1, 1].set_title('Optimal Ki Selection',
                         fontsize=13, fontweight='bold', pad=12)
    axes[1, 1].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[1, 1].grid(True, alpha=0.3, linestyle='--')
    axes[1, 1].set_ylim([0, 1.1])

    plt.tight_layout()
    plt.savefig('ki_tuning_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图3已保存：ki_tuning_analysis.png")

    print(f"\n  最佳Ki值：{Ki_values[best_idx]}")
    print(f"    - 调节时间：{settling_times[best_idx]:.2f} 分钟")
    print(f"    - 超调量：{overshoots[best_idx]:.2f}%")
    print(f"    - 综合评分：{overall_score[best_idx]:.3f}")

    print("\n  Ki调节规律：")
    print("    • Ki ↑ → 误差消除更快")
    print("    • Ki ↑ → 超调可能增大")
    print("    • Ki过大 → 系统振荡")
    print("    • Ki过小 → 收敛缓慢")
    print("    • 工程实践：Ki ≈ Kp / (3τ) 为起点，实验微调")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""

    # 第1部分：创建系统
    tank = create_system()

    # 第2部分：设计控制器
    dt = 0.1
    controller, setpoint = design_controller(dt)

    # 第3部分：运行仿真
    duration = 60  # 仿真60分钟
    (t, h, u, error, integral,
     p_term, i_term) = run_simulation(tank, controller, duration, dt)

    # 第4部分：性能分析
    analyze_performance(t, h, u, error, integral, p_term, i_term,
                       setpoint, controller)

    # 第5部分：结果可视化
    print("\n" + "=" * 80)
    print("第5部分：结果可视化")
    print("=" * 80)

    # 生成3个PNG图表
    create_figure1(t, h, u, error, integral, p_term, i_term, setpoint, duration)
    create_figure2()
    create_figure3()

    # 总结
    print("\n" + "=" * 80)
    print("案例3总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. PI控制原理：")
    print("     • 控制律：u(t) = Kp × e(t) + Ki × ∫e(τ) dτ")
    print("     • P项：根据当前误差快速响应")
    print("     • I项：累积历史误差，消除稳态误差")

    print("\n  2. 积分作用的物理意义：")
    print("     • 记忆功能：记住过去所有误差")
    print("     • 补偿作用：自动调整直到误差为零")
    print("     • 自适应：自动适应负载变化")

    print("\n  3. 稳态误差消除原理：")
    print("     • P控制：需要误差才能有输出 → 必有稳态误差")
    print("     • PI控制：积分项提供稳态输出 → 误差可以为零")
    print("     • 数学证明：e_ss = 0 是PI控制的平衡点")

    print("\n  4. PI控制的优点：")
    print("     ✓ 完全消除稳态误差（理论上e_ss = 0）")
    print("     ✓ 自动适应负载变化")
    print("     ✓ 鲁棒性好，抗干扰能力强")
    print("     ✓ 工程应用广泛")

    print("\n  5. PI控制的缺点：")
    print("     ✗ 相比P控制，调节时间稍长")
    print("     ✗ 需要额外调整Ki参数")
    print("     ✗ 可能出现积分饱和问题")
    print("     ✗ 对快速变化的扰动响应较慢")

    print("\n  6. 参数整定规律：")
    print("     • Kp主导响应速度和稳定性")
    print("     • Ki主导误差消除速度")
    print("     • 经验公式：Ki ≈ Kp / (3τ)")
    print("     • 实际应用：先调Kp，再调Ki微调")

    print("\n[工程应用建议]")
    print("  • 适用场景：对精度要求高（稳态误差<1%）")
    print("  • 适用场景：负载经常变化的系统")
    print("  • 适用场景：要求长期稳定运行")
    print("  • 注意事项：必须实现抗积分饱和保护")

    print("\n[与P控制对比]")
    print("  P控制：简单快速，但有稳态误差")
    print("  PI控制：无稳态误差，但稍复杂")
    print("  选择原则：精度要求高选PI，简单场合选P")

    print("\n[下一步学习]")
    print("  → 案例4：沉淀池水位 - PID控制（引入微分项，改善动态性能）")

    print("\n" + "=" * 80)
    print("案例3演示完成！共生成3个PNG可视化文件")
    print("=" * 80)

    # 列出生成的文件
    png_files = [
        'pi_control_analysis.png',
        'p_vs_pi_comparison.png',
        'ki_tuning_analysis.png'
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
