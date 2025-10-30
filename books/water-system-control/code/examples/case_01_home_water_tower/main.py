#!/usr/bin/env python3
"""
案例1：家庭水塔自动供水系统

核心理论：开关控制（On-Off Control）、滞环控制
学习目标：
1. 理解开关控制的基本原理
2. 掌握滞环（死区）的作用
3. 分析控制性能指标（水位波动、开关频率）
4. 对比不同控制方法的优缺点

难度：⭐（入门级）

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

# 设置matplotlib不显示图形（后台模式）
import matplotlib
matplotlib.use('Agg')

# 设置字体
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
    # 第1部分：系统建模
    # ========================================================================
    print("-"*70)
    print("第1部分：系统建模")
    print("-"*70)

    # 创建单水箱模型
    tank = SingleTank(
        A=2.0,    # 横截面积 2 m²
        R=2.0,    # 阻力系数 2 min/m²
        K=1.0     # 泵增益 1 m³/min
    )
    tank.reset(h0=2.0)  # 初始水位 2米

    print(f"\n水箱系统参数:")
    print(f"  横截面积 A = {tank.A:.1f} m²")
    print(f"  阻力系数 R = {tank.R:.1f} min/m²")
    print(f"  泵流量增益 K = {tank.K:.1f} m³/min")
    print(f"  时间常数 τ = A×R = {tank.tau:.1f} 分钟")
    print(f"\n物理意义：")
    print(f"  - 水箱越大（A↑），系统响应越慢")
    print(f"  - 阻力越大（R↑），出水越慢")
    print(f"  - 时间常数 τ = {tank.tau:.1f}分钟表示水位变化63.2%所需时间")

    # ========================================================================
    # 第2部分：开关控制器设计
    # ========================================================================
    print(f"\n{'-'*70}")
    print("第2部分：开关控制器设计")
    print("-"*70)

    controller = OnOffController(
        low_threshold=2.5,   # 下限阈值
        high_threshold=3.5,  # 上限阈值
        output_on=1.0,       # 泵开启输出
        output_off=0.0       # 泵关闭输出
    )

    print(f"\n控制器参数:")
    print(f"  下限阈值（泵开启）= {controller.low_threshold:.1f} m")
    print(f"  上限阈值（泵关闭）= {controller.high_threshold:.1f} m")
    print(f"  滞环宽度（死区）= {controller.high_threshold - controller.low_threshold:.1f} m")
    print(f"\n控制逻辑:")
    print(f"  - 当水位 < 2.5m 时，泵开启（ON）")
    print(f"  - 当水位 > 3.5m 时，泵关闭（OFF）")
    print(f"  - 在 2.5-3.5m 之间，保持上一状态（滞环）")

    # ========================================================================
    # 第3部分：仿真运行
    # ========================================================================
    print(f"\n{'-'*70}")
    print("第3部分：闭环仿真")
    print("-"*70)

    duration = 120  # 仿真时长 2小时
    dt = 0.1        # 时间步长 0.1分钟 = 6秒
    n_steps = int(duration / dt)

    # 初始化记录数组
    t_history = np.zeros(n_steps)
    h_history = np.zeros(n_steps)
    u_history = np.zeros(n_steps)
    pump_switches = []  # 记录泵的开关事件

    print(f"\n仿真设置:")
    print(f"  仿真时长 = {duration:.0f} 分钟 ({duration/60:.1f} 小时)")
    print(f"  时间步长 = {dt:.2f} 分钟 ({dt*60:.0f} 秒)")
    print(f"  仿真步数 = {n_steps:,}")

    # 开始仿真
    print(f"\n正在运行仿真...")
    tank.reset(h0=2.0)
    controller.reset()

    switch_count = 0
    last_pump_state = controller.is_on

    for i in range(n_steps):
        # 记录当前状态
        t_history[i] = tank.t
        h_history[i] = tank.h

        # 控制器计算
        u_history[i] = controller.control(tank.h)

        # 检测泵开关动作
        if controller.is_on != last_pump_state:
            switch_count += 1
            pump_switches.append({
                'time': tank.t,
                'level': tank.h,
                'action': 'ON' if controller.is_on else 'OFF'
            })
            last_pump_state = controller.is_on

        # 水箱状态更新
        tank.step(u_history[i], dt)

    print(f"仿真完成！")

    # ========================================================================
    # 第4部分：性能分析
    # ========================================================================
    print(f"\n{'-'*70}")
    print("第4部分：控制性能分析")
    print("-"*70)

    # 水位统计
    h_mean = np.mean(h_history)
    h_std = np.std(h_history)
    h_min = np.min(h_history)
    h_max = np.max(h_history)
    h_range = h_max - h_min

    print(f"\n水位统计:")
    print(f"  平均水位 = {h_mean:.3f} m")
    print(f"  标准差 = {h_std:.3f} m")
    print(f"  最小值 = {h_min:.3f} m")
    print(f"  最大值 = {h_max:.3f} m")
    print(f"  波动范围 = {h_range:.3f} m")

    # 泵启停统计
    on_time = np.sum(u_history) * dt  # 泵运行总时间
    duty_cycle = on_time / duration * 100  # 占空比

    print(f"\n泵运行统计:")
    print(f"  总开关次数 = {switch_count}")
    print(f"  平均每小时开关 = {switch_count / (duration/60):.1f} 次/小时")
    print(f"  泵运行时间 = {on_time:.1f} 分钟")
    print(f"  占空比 = {duty_cycle:.1f}%")

    # 显示前5次开关事件
    if len(pump_switches) > 0:
        print(f"\n前5次泵开关事件:")
        for i, event in enumerate(pump_switches[:5], 1):
            print(f"  {i}. t={event['time']:>6.1f}min, h={event['level']:.2f}m → {event['action']}")

    # 能耗估算
    total_energy = np.sum(u_history) * dt * tank.K  # m³
    print(f"\n能耗估算:")
    print(f"  总抽水量 = {total_energy:.2f} m³")
    print(f"  平均流量 = {total_energy/duration:.3f} m³/min")

    # ========================================================================
    # 第5部分：可视化
    # ========================================================================
    print(f"\n{'-'*70}")
    print("第5部分：生成可视化图表")
    print("-"*70)

    # 图1：水位和控制信号时序图
    create_figure1(t_history, h_history, u_history, controller, h_mean, duration)

    # 图2：对比开关控制 vs 比例控制
    create_figure2()

    # 图3：相平面图（水位 vs 水位变化率）
    create_figure3(h_history, dt)

    # ========================================================================
    # 总结
    # ========================================================================
    print(f"\n{'='*70}")
    print("案例1完成！")
    print("="*70)

    print(f"\n关键要点总结:")
    print(f"  1. 开关控制是最简单的控制方法，只需设定上下限")
    print(f"  2. 滞环（死区）可以防止频繁开关，延长设备寿命")
    print(f"  3. 水位会在上下限之间来回波动，波动范围 = {h_range:.2f}m")
    print(f"  4. 本案例开关频率 = {switch_count/(duration/60):.1f}次/小时，属于合理范围")

    print(f"\n优点:")
    print(f"  ✓ 实现简单，成本低")
    print(f"  ✓ 鲁棒性强，不需要精确模型")
    print(f"  ✓ 适合不需要精确控制的场合")

    print(f"\n缺点:")
    print(f"  ✗ 水位波动较大（{h_range:.2f}m）")
    print(f"  ✗ 频繁开关可能损害设备（{switch_count}次开关）")
    print(f"  ✗ 无法精确控制到目标值")

    print(f"\n应用建议:")
    print(f"  - 家庭水塔、蓄水池等对精度要求不高的场合")
    print(f"  - 滞环宽度应根据实际需求调整：")
    print(f"    * 宽度太小 → 开关过于频繁")
    print(f"    * 宽度太大 → 水位波动过大")

    print(f"\n下一步学习:")
    print(f"  → 案例2: 学习比例控制（P控制）")
    print(f"  → 案例3: 学习比例积分控制（PI控制）")
    print(f"  → 案例4: 学习PID控制和参数整定")

    print(f"\n生成的文件:")
    print(f"  - water_level_control.png (水位控制时序图)")
    print(f"  - control_comparison.png (控制方法对比)")
    print(f"  - phase_portrait.png (相平面图)")


def create_figure1(t, h, u, controller, h_mean, duration):
    """图1：水位和控制信号时序图"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 9))

    # 子图1：水位变化
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

    # 子图2：泵控制信号
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
    print(f"  ✓ 已生成: {filename}")
    plt.close()


def create_figure2():
    """图2：对比开关控制 vs 比例控制"""
    duration = 60
    dt = 0.1
    n_steps = int(duration / dt)

    # 创建两个相同的水箱
    tank1 = SingleTank(A=2.0, R=2.0, K=1.0)
    tank2 = SingleTank(A=2.0, R=2.0, K=1.0)
    tank1.reset(h0=2.0)
    tank2.reset(h0=2.0)

    # 两种控制器
    onoff = OnOffController(low_threshold=2.8, high_threshold=3.2)
    proportional = ProportionalController(Kp=2.0, setpoint=3.0)

    # 仿真
    t = np.zeros(n_steps)
    h1 = np.zeros(n_steps)  # 开关控制
    h2 = np.zeros(n_steps)  # 比例控制
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

    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(14, 9))

    # 水位对比
    ax1 = axes[0]
    ax1.plot(t, h1, 'b-', linewidth=2.5, label='On-Off Control', alpha=0.7)
    ax1.plot(t, h2, 'r-', linewidth=2.5, label='Proportional Control', alpha=0.7)
    ax1.axhline(3.0, color='k', linestyle='--', linewidth=1.5,
                label='Setpoint (3.0m)', alpha=0.6)
    ax1.set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    ax1.set_title('Control Method Comparison: On-Off vs Proportional',
                 fontsize=15, fontweight='bold')
    ax1.legend(loc='best', fontsize=11, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim([0, duration])

    # 控制信号对比
    ax2 = axes[1]
    ax2.plot(t, u1, 'b-', linewidth=2.5, label='On-Off Control', alpha=0.7)
    ax2.plot(t, u2, 'r-', linewidth=2.5, label='Proportional Control', alpha=0.7)
    ax2.set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Control Signal', fontsize=13, fontweight='bold')
    ax2.set_title('Control Signal Comparison', fontsize=13, fontweight='bold')
    ax2.legend(loc='best', fontsize=11, framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim([0, duration])

    # 添加性能统计
    stats_text = f'Performance Metrics:\n'
    stats_text += f'On-Off:  STD={np.std(h1):.3f}m, Switches={np.sum(np.abs(np.diff(u1))>0.5)}\n'
    stats_text += f'Proportional: STD={np.std(h2):.3f}m, Smooth Control'
    ax1.text(0.98, 0.02, stats_text, transform=ax1.transAxes,
            fontsize=10, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    filename = 'control_comparison.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  ✓ 已生成: {filename}")
    plt.close()


def create_figure3(h_history, dt):
    """图3：相平面图（水位 vs 水位变化率）"""
    # 计算水位变化率
    dh_dt = np.gradient(h_history, dt)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # 绘制相轨迹
    scatter = ax.scatter(h_history, dh_dt, c=np.arange(len(h_history)),
                        cmap='viridis', s=10, alpha=0.6)

    # 标记起点和终点
    ax.plot(h_history[0], dh_dt[0], 'go', markersize=12,
           label='Start', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(h_history[-1], dh_dt[-1], 'ro', markersize=12,
           label='End', markeredgecolor='black', markeredgewidth=1.5)

    # 添加零线
    ax.axhline(0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(np.mean(h_history), color='orange', linestyle='--',
              linewidth=1.5, alpha=0.7, label=f'Mean={np.mean(h_history):.2f}m')

    ax.set_xlabel('Water Level (m)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Water Level Rate of Change (m/min)', fontsize=13, fontweight='bold')
    ax.set_title('Phase Portrait: Water Level vs Rate of Change',
                fontsize=15, fontweight='bold')
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')

    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Time Step', fontsize=11)

    plt.tight_layout()
    filename = 'phase_portrait.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  ✓ 已生成: {filename}")
    plt.close()


if __name__ == '__main__':
    main()
