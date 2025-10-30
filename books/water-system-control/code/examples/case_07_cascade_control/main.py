#!/usr/bin/env python3
"""
案例7：串级控制 - 双水箱系统

场景描述：
化工厂双层加热反应器温度控制，采用串级控制策略：
- 主回路：控制下层温度（对应下水箱水位h2）
- 副回路：控制上层温度（对应上水箱水位h1）

教学目标：
1. 理解串级控制的基本原理和结构
2. 掌握主控制器和副控制器的设计方法
3. 学习串级控制的参数整定步骤
4. 对比单回路控制和串级控制的性能

控制策略：
- 单回路：直接PID控制h2
- 串级：主PID输出给副PID设定值，副PID控制执行器

关键概念：
- 主控制器（外环）
- 副控制器（内环）
- 抗干扰性能
- 参数整定步骤

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.double_tank import DoubleTank

# 简单PID控制器实现（用于教学）
class PIDController:
    """简单的PID控制器（教学用）"""

    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0, u_min=0.0, u_max=1.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.u_min = u_min
        self.u_max = u_max
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, error, dt):
        """更新PID控制器输出"""
        P = self.Kp * error
        self.integral += error * dt
        I = self.Ki * self.integral
        D = self.Kd * (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        u = P + I + D
        u = max(self.u_min, min(self.u_max, u))
        if u >= self.u_max or u <= self.u_min:
            self.integral -= error * dt
        return u

    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.prev_error = 0.0

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：系统建模与分析
# ============================================================================

def analyze_double_tank_system():
    """
    分析双水箱串联系统的特性
    """
    print("=" * 80)
    print("案例7：串级控制 - 双水箱系统")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：双水箱系统建模与分析")
    print("=" * 80)

    # 系统参数
    A1 = 1.0  # 上水箱面积 (m²)
    A2 = 2.0  # 下水箱面积 (m²)
    R1 = 1.5  # 上水箱阻力 (min/m²)
    R2 = 2.0  # 下水箱阻力 (min/m²)
    K = 1.0   # 泵增益 (m³/min)

    print("\n[系统参数]")
    print(f"  上水箱：A1 = {A1} m², R1 = {R1} min/m²")
    print(f"  下水箱：A2 = {A2} m², R2 = {R2} min/m²")
    print(f"  泵增益：K = {K} m³/min")

    # 时间常数
    tau1 = A1 * R1
    tau2 = A2 * R2

    print("\n[时间常数]")
    print(f"  副回路：τ1 = A1 × R1 = {tau1} 分钟（快）")
    print(f"  主回路：τ2 = A2 × R2 = {tau2} 分钟（慢）")
    print(f"  τ2/τ1 = {tau2/tau1:.2f}（主回路比副回路慢{tau2/tau1:.2f}倍）")

    # 稳态增益
    K_dc = K * R1 * R2

    print("\n[系统特性]")
    print(f"  稳态增益：K_dc = K × R1 × R2 = {K_dc} m")
    print(f"  系统类型：二阶系统")
    print(f"  典型行为：响应较慢，可能有超调")

    print("\n[控制策略对比]")
    print("  单回路控制：")
    print("    - 直接控制h2")
    print("    - 扰动需经过整个系统才被抑制")
    print("    - 响应慢，超调可能较大")
    print("\n  串级控制：")
    print("    - 副回路控制h1，快速抑制进水扰动")
    print("    - 主回路控制h2，保证最终精度")
    print("    - 响应快，抗干扰能力强")

    return A1, A2, R1, R2, K


# ============================================================================
# 第2部分：单回路PID控制（基准）
# ============================================================================

def single_loop_control(A1, A2, R1, R2, K):
    """
    单回路PID控制h2（作为性能基准）
    """
    print("\n" + "=" * 80)
    print("第2部分：单回路PID控制（性能基准）")
    print("=" * 80)

    # 创建系统
    system = DoubleTank(A1=A1, A2=A2, R1=R1, R2=R2, K=K)
    system.reset(h1_0=1.0, h2_0=1.0)

    # 单回路PID控制器（控制h2）
    # 参数整定：基于二阶系统的Ziegler-Nichols方法
    Kp = 0.8
    Ki = 0.15
    Kd = 1.0

    pid = PIDController(Kp=Kp, Ki=Ki, Kd=Kd, u_min=0.0, u_max=1.0)

    print("\n[单回路PID参数]")
    print(f"  Kp = {Kp}")
    print(f"  Ki = {Ki}")
    print(f"  Kd = {Kd}")
    print(f"  控制目标：h2 = 2.5 m")

    # 仿真参数
    setpoint = 2.5
    duration = 60
    dt = 0.1

    n_steps = int(duration / dt)
    time = np.zeros(n_steps)
    h1_data = np.zeros(n_steps)
    h2_data = np.zeros(n_steps)
    u_data = np.zeros(n_steps)
    error_data = np.zeros(n_steps)

    print("\n[开始仿真]")
    print(f"  仿真时长：{duration} 分钟")
    print(f"  采样间隔：{dt} 分钟")

    # 仿真循环
    for i in range(n_steps):
        time[i] = system.t
        h1_data[i] = system.h1
        h2_data[i] = system.h2

        # PID控制
        error = setpoint - system.h2
        error_data[i] = error
        u = pid.update(error, dt)
        u_data[i] = u

        # 系统更新
        system.step(u, dt)

    # 性能指标
    settling_time = np.nan
    overshoot = 0.0
    steady_state_error = abs(h2_data[-1] - setpoint)

    # 上升时间
    rise_time_idx = np.where(h2_data >= 0.9 * setpoint)[0]
    rise_time = time[rise_time_idx[0]] if len(rise_time_idx) > 0 else np.nan

    # 超调量
    max_h2 = np.max(h2_data)
    if max_h2 > setpoint:
        overshoot = (max_h2 - setpoint) / setpoint * 100

    # 调节时间（2%准则）
    for i in range(len(h2_data) - 1, 0, -1):
        if abs(h2_data[i] - setpoint) > 0.02 * setpoint:
            settling_time = time[i]
            break

    print("\n[单回路控制性能]")
    print(f"  上升时间：{rise_time:.2f} 分钟")
    print(f"  超调量：{overshoot:.2f}%")
    print(f"  调节时间（2%）：{settling_time:.2f} 分钟")
    print(f"  稳态误差：{steady_state_error:.4f} m")

    return time, h1_data, h2_data, u_data, error_data


# ============================================================================
# 第3部分：串级PID控制
# ============================================================================

def cascade_control(A1, A2, R1, R2, K):
    """
    串级PID控制：主控制器控制h2，副控制器控制h1
    """
    print("\n" + "=" * 80)
    print("第3部分：串级PID控制")
    print("=" * 80)

    # 创建系统
    system = DoubleTank(A1=A1, A2=A2, R1=R1, R2=R2, K=K)
    system.reset(h1_0=1.0, h2_0=1.0)

    # 副控制器（内环）：控制h1，响应快
    Kp_slave = 1.5
    Ki_slave = 0.5
    Kd_slave = 0.3
    pid_slave = PIDController(Kp=Kp_slave, Ki=Ki_slave, Kd=Kd_slave,
                               u_min=0.0, u_max=1.0)

    # 主控制器（外环）：控制h2，输出作为h1的设定值
    Kp_master = 0.6
    Ki_master = 0.1
    Kd_master = 0.5
    pid_master = PIDController(Kp=Kp_master, Ki=Ki_master, Kd=Kd_master,
                                u_min=0.5, u_max=4.0)  # h1的合理范围

    print("\n[串级控制器参数]")
    print("  主控制器（控制h2）：")
    print(f"    Kp = {Kp_master}, Ki = {Ki_master}, Kd = {Kd_master}")
    print("  副控制器（控制h1）：")
    print(f"    Kp = {Kp_slave}, Ki = {Ki_slave}, Kd = {Kd_slave}")
    print(f"  控制目标：h2 = 2.5 m")

    # 仿真参数
    setpoint_h2 = 2.5
    duration = 60
    dt = 0.1

    n_steps = int(duration / dt)
    time = np.zeros(n_steps)
    h1_data = np.zeros(n_steps)
    h2_data = np.zeros(n_steps)
    u_data = np.zeros(n_steps)
    setpoint_h1_data = np.zeros(n_steps)
    error_h2_data = np.zeros(n_steps)

    print("\n[开始仿真]")

    # 仿真循环
    for i in range(n_steps):
        time[i] = system.t
        h1_data[i] = system.h1
        h2_data[i] = system.h2

        # 主控制器：根据h2误差计算h1设定值
        error_h2 = setpoint_h2 - system.h2
        error_h2_data[i] = error_h2
        setpoint_h1 = pid_master.update(error_h2, dt)
        setpoint_h1_data[i] = setpoint_h1

        # 副控制器：根据h1误差计算控制输入u
        error_h1 = setpoint_h1 - system.h1
        u = pid_slave.update(error_h1, dt)
        u_data[i] = u

        # 系统更新
        system.step(u, dt)

    # 性能指标
    settling_time = np.nan
    overshoot = 0.0
    steady_state_error = abs(h2_data[-1] - setpoint_h2)

    rise_time_idx = np.where(h2_data >= 0.9 * setpoint_h2)[0]
    rise_time = time[rise_time_idx[0]] if len(rise_time_idx) > 0 else np.nan

    max_h2 = np.max(h2_data)
    if max_h2 > setpoint_h2:
        overshoot = (max_h2 - setpoint_h2) / setpoint_h2 * 100

    for i in range(len(h2_data) - 1, 0, -1):
        if abs(h2_data[i] - setpoint_h2) > 0.02 * setpoint_h2:
            settling_time = time[i]
            break

    print("\n[串级控制性能]")
    print(f"  上升时间：{rise_time:.2f} 分钟")
    print(f"  超调量：{overshoot:.2f}%")
    print(f"  调节时间（2%）：{settling_time:.2f} 分钟")
    print(f"  稳态误差：{steady_state_error:.4f} m")

    return time, h1_data, h2_data, u_data, setpoint_h1_data, error_h2_data


# ============================================================================
# 第4部分：性能对比与可视化
# ============================================================================

def compare_and_visualize():
    """
    对比单回路和串级控制性能
    """
    print("\n" + "=" * 80)
    print("第4部分：性能对比与可视化")
    print("=" * 80)

    # 系统参数
    A1, A2, R1, R2, K = analyze_double_tank_system()

    # 单回路控制
    t_single, h1_single, h2_single, u_single, err_single = single_loop_control(
        A1, A2, R1, R2, K
    )

    # 串级控制
    t_cascade, h1_cascade, h2_cascade, u_cascade, sp_h1, err_cascade = cascade_control(
        A1, A2, R1, R2, K
    )

    # 可视化对比
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    setpoint = 2.5

    # 子图1：下水箱水位h2对比（主控制目标）
    ax = axes[0, 0]
    ax.plot(t_single, h2_single, 'b-', linewidth=2, label='Single Loop')
    ax.plot(t_cascade, h2_cascade, 'r-', linewidth=2, label='Cascade')
    ax.axhline(setpoint, color='g', linestyle='--', linewidth=1.5, label='Setpoint')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Lower Tank Level h2 (m)')
    ax.set_title('Main Control Variable Comparison')
    ax.legend()
    ax.grid(True)

    # 子图2：上水箱水位h1对比
    ax = axes[0, 1]
    ax.plot(t_single, h1_single, 'b-', linewidth=2, label='Single Loop')
    ax.plot(t_cascade, h1_cascade, 'r-', linewidth=2, label='Cascade')
    ax.plot(t_cascade, sp_h1, 'g--', linewidth=1.5, label='h1 Setpoint (Cascade)')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Upper Tank Level h1 (m)')
    ax.set_title('Secondary Variable Comparison')
    ax.legend()
    ax.grid(True)

    # 子图3：控制输入对比
    ax = axes[1, 0]
    ax.plot(t_single, u_single, 'b-', linewidth=2, label='Single Loop')
    ax.plot(t_cascade, u_cascade, 'r-', linewidth=2, label='Cascade')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Control Input u')
    ax.set_title('Control Input Comparison')
    ax.legend()
    ax.grid(True)

    # 子图4：误差对比
    ax = axes[1, 1]
    ax.plot(t_single, err_single, 'b-', linewidth=2, label='Single Loop')
    ax.plot(t_cascade, err_cascade, 'r-', linewidth=2, label='Cascade')
    ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Error (m)')
    ax.set_title('Control Error Comparison')
    ax.legend()
    ax.grid(True)

    # 子图5：性能指标对比（柱状图）
    ax = axes[2, 0]

    # 计算性能指标
    metrics = ['Rise Time\n(min)', 'Overshoot\n(%)', 'Settling\n(min)']

    # 单回路
    rise_single = t_single[np.where(h2_single >= 0.9 * setpoint)[0][0]]
    over_single = (np.max(h2_single) - setpoint) / setpoint * 100 if np.max(h2_single) > setpoint else 0
    settle_single_idx = np.where(np.abs(h2_single - setpoint) > 0.02 * setpoint)[0]
    settle_single = t_single[settle_single_idx[-1]] if len(settle_single_idx) > 0 else 0

    # 串级
    rise_cascade = t_cascade[np.where(h2_cascade >= 0.9 * setpoint)[0][0]]
    over_cascade = (np.max(h2_cascade) - setpoint) / setpoint * 100 if np.max(h2_cascade) > setpoint else 0
    settle_cascade_idx = np.where(np.abs(h2_cascade - setpoint) > 0.02 * setpoint)[0]
    settle_cascade = t_cascade[settle_cascade_idx[-1]] if len(settle_cascade_idx) > 0 else 0

    values_single = [rise_single, over_single, settle_single]
    values_cascade = [rise_cascade, over_cascade, settle_cascade]

    x = np.arange(len(metrics))
    width = 0.35

    ax.bar(x - width/2, values_single, width, label='Single Loop', alpha=0.8)
    ax.bar(x + width/2, values_cascade, width, label='Cascade', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel('Value')
    ax.set_title('Performance Metrics Comparison')
    ax.legend()
    ax.grid(True, axis='y')

    # 子图6：性能改进百分比
    ax = axes[2, 1]
    improvements = [
        (values_single[0] - values_cascade[0]) / values_single[0] * 100,
        (values_single[1] - values_cascade[1]) / values_single[1] * 100 if values_single[1] > 0 else 0,
        (values_single[2] - values_cascade[2]) / values_single[2] * 100
    ]

    colors = ['green' if imp > 0 else 'red' for imp in improvements]
    ax.barh(metrics, improvements, color=colors, alpha=0.7)
    ax.axvline(0, color='k', linestyle='--', linewidth=1)
    ax.set_xlabel('Improvement (%)')
    ax.set_title('Cascade Control Improvement over Single Loop')
    ax.grid(True, axis='x')

    plt.tight_layout()
    plt.savefig('cascade_control_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: cascade_control_comparison.png")

    print("\n" + "=" * 80)
    print("案例7总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 串级控制结构：")
    print("     • 主控制器（外环）：控制最终目标变量h2")
    print("     • 副控制器（内环）：控制中间变量h1")
    print("     • 主控制器输出作为副控制器设定值")
    print("\n  2. 参数整定步骤：")
    print("     • 第一步：关闭主回路，整定副控制器")
    print("     • 第二步：闭合主回路，整定主控制器")
    print("     • 副控制器要快，主控制器要稳")
    print("\n  3. 性能优势：")
    print(f"     • 上升时间提升：{improvements[0]:.1f}%")
    print(f"     • 超调量降低：{improvements[1]:.1f}%")
    print(f"     • 调节时间提升：{improvements[2]:.1f}%")
    print("\n  4. 适用场景：")
    print("     • 大时滞系统")
    print("     • 扰动频繁的系统")
    print("     • 多容串联系统")
    print("     • 对动态性能要求高的场合")

    print("\n[下一步学习]")
    print("  → 案例8：前馈控制（另一种抗干扰方法）")
    print("  → 案例14：状态反馈控制（现代控制方法）")

    plt.show()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""
    compare_and_visualize()

    print("\n" + "=" * 80)
    print("案例7演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
