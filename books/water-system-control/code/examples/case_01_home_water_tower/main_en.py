#!/usr/bin/env python3
"""
案例1：家庭水塔自动供水系统

核心理论：开关控制、滞环控制
学习目标：
1. 理解开关控制的基本原理
2. 掌握滞环（死区）的作用
3. 分析控制性能指标（水位波动、开关频率）
4. 对比不同控制方法的优缺点

难度：简单（入门级）

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from code.models.water_tank.single_tank import SingleTank
from code.control.basic_controllers import OnOffController, ProportionalController

# 设置matplotlib为非交互模式（后台模式）
import matplotlib
matplotlib.use('Agg')

# 设置字体（图表标签用英文，避免乱码）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def main():
    """主函数"""
    print("="*70)
    print("案例1：家庭水塔自动供水系统")
    print("="*70)
    print("\n控制方法：开关控制（On-Off Control）")
    print("应用场景：家庭水塔、蓄水池等简单液位控制系统\n")

    # ========================================================================
    # 第一部分：系统建模
    # ========================================================================
    print("-"*70)
    print("第一部分：系统建模")
    print("-"*70)

    # 创建单水箱模型
    tank = SingleTank(
        A=2.0,    # 横截面积 2 平方米
        R=2.0,    # 阻力系数 2 分钟/平方米
        K=1.0     # 泵增益 1 立方米/分钟
    )
    tank.reset(h0=2.0)  # 初始水位2米（低于阈值，泵将启动）

    print(f"\n水箱系统参数：")
    print(f"  横截面积 A = {tank.A:.1f} m²")
    print(f"  阻力系数 R = {tank.R:.1f} min/m²")
    print(f"  泵流量增益 K = {tank.K:.1f} m³/min")
    print(f"  时间常数 tau = A×R = {tank.tau:.1f} 分钟")
    print(f"\n物理意义：")
    print(f"  - 水箱越大（A增加）→ 系统响应越慢")
    print(f"  - 阻力越大（R增加）→ 出水越慢")
    print(f"  - 时间常数 tau = {tank.tau:.1f} 分钟表示水位变化63.2%所需时间")

    # ========================================================================
    # 第二部分：开关控制器设计
    # ========================================================================
    print(f"\n{'-'*70}")
    print("第二部分：开关控制器设计")
    print("-"*70)

    controller = OnOffController(
        low_threshold=2.5,   # 下限阈值
        high_threshold=3.5,  # 上限阈值
        output_on=1.0,       # 泵开启输出
        output_off=0.0       # 泵关闭输出
    )

    print(f"\n控制器参数：")
    print(f"  下限阈值（泵开启）= {controller.low_threshold:.1f} 米")
    print(f"  上限阈值（泵关闭）= {controller.high_threshold:.1f} 米")
    print(f"  滞环宽度（死区）= {controller.high_threshold - controller.low_threshold:.1f} 米")
    print(f"\n控制逻辑：")
    print(f"  - 当水位 < 2.5米时，泵开启")
    print(f"  - 当水位 > 3.5米时，泵关闭")
    print(f"  - 在2.5-3.5米之间，保持当前状态（滞环）")

    # ========================================================================
    # Part 3: Simulation Run
    # ========================================================================
    print(f"\n{'-'*70}")
    print("Part 3: Closed-loop Simulation")
    print("-"*70)

    duration = 200  # Simulation duration ~3.3 hours for more dynamic behavior
    dt = 0.1        # Time step 0.1 minute = 6 seconds
    n_steps = int(duration / dt)

    # Initialize recording arrays
    t_history = np.zeros(n_steps)
    h_history = np.zeros(n_steps)
    u_history = np.zeros(n_steps)
    pump_switches = []  # Record pump switching events

    print(f"\nSimulation Settings:")
    print(f"  Simulation duration = {duration:.0f} minutes ({duration/60:.1f} hours)")
    print(f"  Time step = {dt:.2f} minutes ({dt*60:.0f} seconds)")
    print(f"  Number of steps = {n_steps:,}")

    # Start simulation
    print(f"\nRunning simulation...")
    tank.reset(h0=2.0)
    controller.reset()

    switch_count = 0
    last_pump_state = controller.is_on

    for i in range(n_steps):
        # Record current state
        t_history[i] = tank.t
        h_history[i] = tank.h

        # Controller calculation
        u_history[i] = controller.control(tank.h)

        # Detect pump switching action
        if controller.is_on != last_pump_state:
            switch_count += 1
            pump_switches.append({
                'time': tank.t,
                'level': tank.h,
                'action': 'ON' if controller.is_on else 'OFF'
            })
            last_pump_state = controller.is_on

        # Water tank state update
        tank.step(u_history[i], dt)

    print(f"Simulation completed!")

    # ========================================================================
    # Part 4: Performance Analysis
    # ========================================================================
    print(f"\n{'-'*70}")
    print("Part 4: Control Performance Analysis")
    print("-"*70)

    # Water level statistics
    h_mean = np.mean(h_history)
    h_std = np.std(h_history)
    h_min = np.min(h_history)
    h_max = np.max(h_history)
    h_range = h_max - h_min

    print(f"\nWater Level Statistics:")
    print(f"  Average level = {h_mean:.3f} m")
    print(f"  Standard deviation = {h_std:.3f} m")
    print(f"  Minimum value = {h_min:.3f} m")
    print(f"  Maximum value = {h_max:.3f} m")
    print(f"  Fluctuation range = {h_range:.3f} m")

    # Pump on/off statistics
    on_time = np.sum(u_history) * dt  # Total pump running time
    duty_cycle = on_time / duration * 100  # Duty cycle

    print(f"\nPump Operation Statistics:")
    print(f"  Total switches = {switch_count}")
    print(f"  Average switches per hour = {switch_count / (duration/60):.1f} times/hour")
    print(f"  Pump running time = {on_time:.1f} minutes")
    print(f"  Duty cycle = {duty_cycle:.1f}%")

    # Display first 5 switching events
    if len(pump_switches) > 0:
        print(f"\nFirst 5 Pump Switching Events:")
        for i, event in enumerate(pump_switches[:5], 1):
            print(f"  {i}. t={event['time']:>6.1f}min, h={event['level']:.2f}m -> {event['action']}")

    # Energy consumption estimation
    total_energy = np.sum(u_history) * dt * tank.K  # m^3
    print(f"\nEnergy Consumption Estimation:")
    print(f"  Total pumped water = {total_energy:.2f} m^3")
    print(f"  Average flow rate = {total_energy/duration:.3f} m^3/min")

    # ========================================================================
    # Part 5: Visualization
    # ========================================================================
    print(f"\n{'-'*70}")
    print("Part 5: Generate Visualization Charts")
    print("-"*70)

    # Figure 1: Water level and control signal time series
    create_figure1(t_history, h_history, u_history, controller, h_mean, duration)

    # Figure 2: Compare on-off control vs proportional control
    create_figure2()

    # Figure 3: Phase portrait (water level vs rate of change)
    create_figure3(h_history, dt)

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*70}")
    print("Case 1 Completed!")
    print("="*70)

    print(f"\nKey Points Summary:")
    print(f"  1. On-off control is the simplest control method, only requires setting upper and lower limits")
    print(f"  2. Hysteresis (dead band) can prevent frequent switching and extend equipment life")
    print(f"  3. Water level fluctuates between upper and lower limits, range = {h_range:.2f}m")
    print(f"  4. This case switching frequency = {switch_count/(duration/60):.1f} times/hour, reasonable range")

    print(f"\nAdvantages:")
    print(f"  + Simple implementation, low cost")
    print(f"  + Strong robustness, does not require precise model")
    print(f"  + Suitable for occasions that do not require precise control")

    print(f"\nDisadvantages:")
    print(f"  - Large water level fluctuation ({h_range:.2f}m)")
    print(f"  - Frequent switching may damage equipment ({switch_count} switches)")
    print(f"  - Cannot precisely control to target value")

    print(f"\nApplication Suggestions:")
    print(f"  - Home water towers, water tanks, and other occasions with low precision requirements")
    print(f"  - Hysteresis width should be adjusted according to actual needs:")
    print(f"    * Too narrow -> too frequent switching")
    print(f"    * Too wide -> excessive water level fluctuation")

    print(f"\nNext Learning:")
    print(f"  -> Case 2: Learn proportional control (P control)")
    print(f"  -> Case 3: Learn proportional-integral control (PI control)")
    print(f"  -> Case 4: Learn PID control and parameter tuning")

    print(f"\nGenerated Files:")
    print(f"  - water_level_control.png (Water level control time series)")
    print(f"  - control_comparison.png (Control method comparison)")
    print(f"  - phase_portrait.png (Phase portrait)")


def create_figure1(t, h, u, controller, h_mean, duration):
    """Figure 1: Water level control time series"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 9))

    # Subplot 1: Water level change
    ax1 = axes[0]
    ax1.plot(t, h, 'b-', linewidth=2, label='Water Level', alpha=0.8)
    ax1.axhline(controller.low_threshold, color='r', linestyle='--',
                linewidth=1.5, label=f'Low Threshold ({controller.low_threshold}m)', alpha=0.7)
    ax1.axhline(controller.high_threshold, color='r', linestyle='--',
                linewidth=1.5, label=f'High Threshold ({controller.high_threshold}m)', alpha=0.7)
    ax1.fill_between(t, controller.low_threshold, controller.high_threshold,
                     alpha=0.15, color='green', label='Dead Band (Hysteresis)')
    ax1.axhline(h_mean, color='orange', linestyle=':',
                linewidth=2, label=f'Mean Level ({h_mean:.2f}m)')

    ax1.set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    ax1.set_title('Case 1: Home Water Tower with On-Off Control',
                 fontsize=15, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim([0, duration])

    # Subplot 2: Pump control signal
    ax2 = axes[1]
    ax2.plot(t, u, 'g-', linewidth=2, label='Pump Control Signal', alpha=0.8)
    ax2.fill_between(t, 0, u, alpha=0.25, color='g')
    ax2.set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Control Signal\n(0=OFF, 1=ON)', fontsize=13, fontweight='bold')
    ax2.set_title('Pump On/Off Status', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim([0, duration])
    ax2.set_ylim([-0.1, 1.1])
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['OFF', 'ON'])

    plt.tight_layout()
    filename = 'water_level_control.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  Generated: {filename}")
    plt.close()


def create_figure2():
    """Figure 2: Compare on-off control vs proportional control"""
    duration = 60
    dt = 0.1
    n_steps = int(duration / dt)

    # Create two identical tanks
    tank1 = SingleTank(A=2.0, R=2.0, K=1.0)
    tank2 = SingleTank(A=2.0, R=2.0, K=1.0)
    tank1.reset(h0=2.0)
    tank2.reset(h0=2.0)

    # Two controllers
    onoff = OnOffController(low_threshold=2.8, high_threshold=3.2)
    proportional = ProportionalController(Kp=2.0, setpoint=3.0)

    # Simulation
    t = np.zeros(n_steps)
    h1 = np.zeros(n_steps)  # On-off control
    h2 = np.zeros(n_steps)  # Proportional control
    u1 = np.zeros(n_steps)
    u2 = np.zeros(n_steps)

    for i in range(n_steps):
        t[i] = tank1.t
        h1[i] = tank1.h
        h2[i] = tank2.h

        u1[i] = onoff.control(tank1.h)
        u2[i] = proportional.control(tank2.h)

        tank1.step(u1[i], dt)
        tank2.step(u2[i], dt)

    # Plotting
    fig, axes = plt.subplots(2, 1, figsize=(14, 9))

    # Water level comparison
    ax1 = axes[0]
    ax1.plot(t, h1, 'b-', linewidth=2.5, label='On-Off Control', alpha=0.7)
    ax1.plot(t, h2, 'r-', linewidth=2.5, label='Proportional Control (P)', alpha=0.7)
    ax1.axhline(3.0, color='k', linestyle='--', linewidth=1.5, label='Target Level (3.0m)', alpha=0.6)
    ax1.set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    ax1.set_title('Comparison: On-Off Control vs Proportional Control',
                 fontsize=15, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim([0, duration])

    # Control signal comparison
    ax2 = axes[1]
    ax2.plot(t, u1, 'b-', linewidth=2, label='On-Off Control Signal', alpha=0.7)
    ax2.plot(t, u2, 'r-', linewidth=2, label='Proportional Control Signal', alpha=0.7)
    ax2.set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Control Signal (0-1)', fontsize=13, fontweight='bold')
    ax2.set_title('Control Signal Comparison', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim([0, duration])

    plt.tight_layout()
    filename = 'control_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  Generated: {filename}")
    plt.close()


def create_figure3(h_history, dt):
    """Figure 3: Phase portrait (water level vs rate of change)"""
    # Calculate rate of change (derivative)
    dh_dt = np.gradient(h_history, dt)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Phase trajectory
    ax.plot(h_history, dh_dt, 'b-', linewidth=1.5, alpha=0.6)

    # Mark start and end points
    ax.plot(h_history[0], dh_dt[0], 'go', markersize=12, label='Start', zorder=5)
    ax.plot(h_history[-1], dh_dt[-1], 'ro', markersize=12, label='End', zorder=5)

    # Add arrow to indicate direction
    arrow_step = len(h_history) // 20
    for i in range(0, len(h_history)-arrow_step, arrow_step):
        ax.annotate('', xy=(h_history[i+arrow_step], dh_dt[i+arrow_step]),
                   xytext=(h_history[i], dh_dt[i]),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=1.5, alpha=0.5))

    ax.set_xlabel('Water Level h (m)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Rate of Change dh/dt (m/min)', fontsize=13, fontweight='bold')
    ax.set_title('Phase Portrait: Water Level vs Rate of Change',
                fontsize=15, fontweight='bold')
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.axvline(3.0, color='orange', linestyle='--', linewidth=1.5, label='Target Level', alpha=0.6)

    plt.tight_layout()
    filename = 'phase_portrait.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  Generated: {filename}")
    plt.close()


if __name__ == '__main__':
    main()

