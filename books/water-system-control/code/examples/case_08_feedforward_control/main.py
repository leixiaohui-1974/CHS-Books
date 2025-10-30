#!/usr/bin/env python3
"""
案例8：前馈控制 - 已知扰动补偿

场景描述：
城市供水系统应对可预测的用水高峰，采用前馈控制策略：
- 根据历史数据预测用水量（可测扰动）
- 提前调整水泵流量（前馈补偿）
- 结合反馈控制消除残余误差

教学目标：
1. 理解前馈控制的基本原理和优势
2. 掌握扰动通道建模方法
3. 学习前馈控制器设计
4. 对比纯反馈、纯前馈和组合控制

控制策略：
- 纯反馈：PID控制
- 纯前馈：基于扰动测量的补偿
- 组合控制：前馈 + 反馈

关键概念：
- 可测扰动
- 扰动通道模型
- 前馈增益
- 前馈-反馈组合

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

from code.models.water_tank.single_tank import SingleTank

# 简单PID控制器
class PIDController:
    """简单的PID控制器"""
    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0, u_min=0.0, u_max=1.0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.u_min, self.u_max = u_min, u_max
        self.integral, self.prev_error = 0.0, 0.0

    def update(self, error, dt):
        P = self.Kp * error
        self.integral += error * dt
        I = self.Ki * self.integral
        D = self.Kd * (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        u = max(self.u_min, min(self.u_max, P + I + D))
        if u >= self.u_max or u <= self.u_min:
            self.integral -= error * dt
        return u

    def reset(self):
        self.integral, self.prev_error = 0.0, 0.0

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：系统分析与扰动建模
# ============================================================================

def analyze_disturbance_effect():
    """
    分析扰动对水位的影响，建立扰动通道模型
    """
    print("=" * 80)
    print("案例8：前馈控制 - 已知扰动补偿")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：系统分析与扰动建模")
    print("=" * 80)

    # 系统参数
    A = 2.5  # 横截面积 (m²)
    R = 1.8  # 阻力系数 (min/m²)
    K = 1.2  # 泵增益 (m³/min)

    print("\n[水箱系统参数]")
    print(f"  横截面积 A = {A} m²")
    print(f"  阻力系数 R = {R} min/m²")
    print(f"  泵增益 K = {K} m³/min")
    print(f"  时间常数 τ = A × R = {A*R} 分钟")

    print("\n[系统方程]")
    print("  A * dh/dt = K*u + d(t) - h/R")
    print("  其中：")
    print("    u: 控制输入（泵开度）")
    print("    d(t): 扰动（额外进水或出水）")
    print("    h: 水位")

    print("\n[扰动类型]")
    print("  可测扰动示例：")
    print("    - 用户用水量（可预测的日变化）")
    print("    - 上游来水量（可测量）")
    print("    - 季节性变化（可预测）")

    print("\n[前馈控制原理]")
    print("  1. 测量或预测扰动 d(t)")
    print("  2. 根据扰动计算前馈补偿 u_ff(t)")
    print("  3. 总控制输入 u(t) = u_ff(t) + u_fb(t)")
    print("     其中 u_fb 是反馈控制输出")

    return A, R, K


# ============================================================================
# 第2部分：纯反馈控制（基准）
# ============================================================================

def feedback_only_control(A, R, K):
    """
    纯反馈PID控制（无前馈）
    """
    print("\n" + "=" * 80)
    print("第2部分：纯反馈PID控制（性能基准）")
    print("=" * 80)

    # 创建系统
    system = SingleTank(A=A, R=R, K=K)
    system.reset(h0=2.0)

    # PID控制器
    Kp, Ki, Kd = 0.6, 0.1, 0.5
    pid = PIDController(Kp=Kp, Ki=Ki, Kd=Kd, u_min=0.0, u_max=1.0)

    print("\n[PID参数]")
    print(f"  Kp = {Kp}, Ki = {Ki}, Kd = {Kd}")
    print(f"  目标水位：2.0 m")

    # 仿真参数
    setpoint = 2.0
    duration = 60
    dt = 0.1
    disturbance_start = 20  # 20分钟时加扰动
    disturbance_magnitude = -0.3  # 额外出水（负值）

    n_steps = int(duration / dt)
    time = np.zeros(n_steps)
    h_data = np.zeros(n_steps)
    u_data = np.zeros(n_steps)
    d_data = np.zeros(n_steps)

    print("\n[扰动设置]")
    print(f"  扰动时刻：{disturbance_start} 分钟")
    print(f"  扰动幅值：{disturbance_magnitude} m³/min（额外出水）")
    print(f"  持续时间：20 分钟")

    print("\n[开始仿真]")

    # 仿真循环
    for i in range(n_steps):
        time[i] = system.t
        h_data[i] = system.h

        # 阶跃扰动
        if disturbance_start <= system.t < disturbance_start + 20:
            d_data[i] = disturbance_magnitude
        else:
            d_data[i] = 0.0

        # PID控制
        error = setpoint - system.h
        u = pid.update(error, dt)
        u_data[i] = u

        # 系统更新（加上扰动）
        # 扰动相当于额外的流量输入/输出
        u_total = u + d_data[i] / K  # 转换为等效控制输入
        system.step(u_total, dt)

    # 性能分析
    dist_start_idx = int(disturbance_start / dt)
    dist_end_idx = int((disturbance_start + 20) / dt)

    max_deviation = np.max(np.abs(h_data[dist_start_idx:dist_end_idx+200] - setpoint))

    # 恢复时间
    recovery_time = np.nan
    for i in range(dist_end_idx, n_steps):
        if np.abs(h_data[i] - setpoint) <= 0.02 * setpoint:
            recovery_time = time[i] - (disturbance_start + 20)
            break

    print("\n[纯反馈控制性能]")
    print(f"  最大偏差：{max_deviation:.4f} m")
    print(f"  恢复时间：{recovery_time:.2f} 分钟")

    return time, h_data, u_data, d_data


# ============================================================================
# 第3部分：前馈+反馈组合控制
# ============================================================================

def feedforward_feedback_control(A, R, K):
    """
    前馈+反馈组合控制
    """
    print("\n" + "=" * 80)
    print("第3部分：前馈+反馈组合控制")
    print("=" * 80)

    # 创建系统
    system = SingleTank(A=A, R=R, K=K)
    system.reset(h0=2.0)

    # 反馈PID控制器（参数可以更小，因为有前馈帮助）
    Kp, Ki, Kd = 0.4, 0.05, 0.3
    pid = PIDController(Kp=Kp, Ki=Ki, Kd=Kd, u_min=-0.5, u_max=0.5)

    # 前馈增益设计
    # 理论上：u_ff = -d / K（完全补偿扰动）
    # 实际中可能需要调整
    Kff = -1.0 / K  # 前馈增益

    print("\n[控制器参数]")
    print(f"  反馈PID：Kp = {Kp}, Ki = {Ki}, Kd = {Kd}")
    print(f"  前馈增益：Kff = {Kff:.4f}")
    print("\n[前馈控制器设计]")
    print("  理想前馈：u_ff = -d / K")
    print("  目标：完全抵消扰动的影响")

    # 仿真参数
    setpoint = 2.0
    duration = 60
    dt = 0.1
    disturbance_start = 20
    disturbance_magnitude = -0.3

    n_steps = int(duration / dt)
    time = np.zeros(n_steps)
    h_data = np.zeros(n_steps)
    u_fb_data = np.zeros(n_steps)
    u_ff_data = np.zeros(n_steps)
    u_total_data = np.zeros(n_steps)
    d_data = np.zeros(n_steps)

    print("\n[开始仿真]")

    # 仿真循环
    for i in range(n_steps):
        time[i] = system.t
        h_data[i] = system.h

        # 阶跃扰动
        if disturbance_start <= system.t < disturbance_start + 20:
            d_data[i] = disturbance_magnitude
        else:
            d_data[i] = 0.0

        # 前馈控制（基于扰动测量）
        u_ff = Kff * d_data[i]
        u_ff_data[i] = u_ff

        # 反馈PID控制
        error = setpoint - system.h
        u_fb = pid.update(error, dt)
        u_fb_data[i] = u_fb

        # 总控制输入
        u_total = u_ff + u_fb
        u_total = max(0.0, min(1.0, u_total))  # 限幅
        u_total_data[i] = u_total

        # 系统更新
        u_with_dist = u_total + d_data[i] / K
        system.step(u_with_dist, dt)

    # 性能分析
    dist_start_idx = int(disturbance_start / dt)
    dist_end_idx = int((disturbance_start + 20) / dt)

    max_deviation = np.max(np.abs(h_data[dist_start_idx:dist_end_idx+200] - setpoint))

    recovery_time = np.nan
    for i in range(dist_end_idx, n_steps):
        if np.abs(h_data[i] - setpoint) <= 0.02 * setpoint:
            recovery_time = time[i] - (disturbance_start + 20)
            break

    print("\n[前馈+反馈组合控制性能]")
    print(f"  最大偏差：{max_deviation:.4f} m")
    print(f"  恢复时间：{recovery_time:.2f} 分钟")

    return time, h_data, u_fb_data, u_ff_data, u_total_data, d_data


# ============================================================================
# 第4部分：性能对比与可视化
# ============================================================================

def compare_and_visualize():
    """
    对比纯反馈和前馈+反馈控制性能
    """
    print("\n" + "=" * 80)
    print("第4部分：性能对比与可视化")
    print("=" * 80)

    # 系统参数
    A, R, K = analyze_disturbance_effect()

    # 纯反馈控制
    t_fb, h_fb, u_fb, d_fb = feedback_only_control(A, R, K)

    # 前馈+反馈组合控制
    t_ff, h_ff, u_fb_ff, u_ff_ff, u_total_ff, d_ff = feedforward_feedback_control(A, R, K)

    # 可视化
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    setpoint = 2.0

    # 子图1：水位对比
    ax = axes[0, 0]
    ax.plot(t_fb, h_fb, 'b-', linewidth=2, label='Feedback Only')
    ax.plot(t_ff, h_ff, 'r-', linewidth=2, label='Feedforward + Feedback')
    ax.axhline(setpoint, color='g', linestyle='--', linewidth=1.5, label='Setpoint')
    ax.axvline(20, color='gray', linestyle=':', alpha=0.7, label='Disturbance Start')
    ax.axvline(40, color='gray', linestyle=':', alpha=0.7)
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Water Level (m)')
    ax.set_title('Water Level Response Comparison')
    ax.legend()
    ax.grid(True)
    ax.set_ylim([1.5, 2.5])

    # 子图2：扰动信号
    ax = axes[0, 1]
    ax.plot(t_fb, d_fb, 'k-', linewidth=2, label='Disturbance')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Disturbance (m³/min)')
    ax.set_title('Measured Disturbance')
    ax.legend()
    ax.grid(True)
    ax.axhline(0, color='k', linestyle='--', linewidth=0.5)

    # 子图3：控制输入对比（纯反馈）
    ax = axes[1, 0]
    ax.plot(t_fb, u_fb, 'b-', linewidth=2, label='Feedback Control u')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Control Input')
    ax.set_title('Feedback Only - Control Input')
    ax.legend()
    ax.grid(True)
    ax.set_ylim([-0.1, 1.1])

    # 子图4：控制输入分解（前馈+反馈）
    ax = axes[1, 1]
    ax.plot(t_ff, u_ff_ff, 'g-', linewidth=2, label='Feedforward u_ff')
    ax.plot(t_ff, u_fb_ff, 'b-', linewidth=2, label='Feedback u_fb')
    ax.plot(t_ff, u_total_ff, 'r--', linewidth=2, label='Total u')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Control Input')
    ax.set_title('Feedforward + Feedback - Control Inputs')
    ax.legend()
    ax.grid(True)

    # 子图5：误差对比
    ax = axes[2, 0]
    error_fb = h_fb - setpoint
    error_ff = h_ff - setpoint
    ax.plot(t_fb, error_fb, 'b-', linewidth=2, label='Feedback Only')
    ax.plot(t_ff, error_ff, 'r-', linewidth=2, label='Feedforward + Feedback')
    ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
    ax.axvline(20, color='gray', linestyle=':', alpha=0.7)
    ax.axvline(40, color='gray', linestyle=':', alpha=0.7)
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Error (m)')
    ax.set_title('Control Error Comparison')
    ax.legend()
    ax.grid(True)

    # 子图6：性能指标对比
    ax = axes[2, 1]

    # 计算性能指标
    dist_start_idx = 200  # 20分钟
    dist_end_idx = 400    # 40分钟

    max_dev_fb = np.max(np.abs(h_fb[dist_start_idx:dist_end_idx+200] - setpoint))
    max_dev_ff = np.max(np.abs(h_ff[dist_start_idx:dist_end_idx+200] - setpoint))

    # 恢复时间
    recovery_fb = np.nan
    for i in range(dist_end_idx, len(h_fb)):
        if np.abs(h_fb[i] - setpoint) <= 0.02 * setpoint:
            recovery_fb = t_fb[i] - 40
            break

    recovery_ff = np.nan
    for i in range(dist_end_idx, len(h_ff)):
        if np.abs(h_ff[i] - setpoint) <= 0.02 * setpoint:
            recovery_ff = t_ff[i] - 40
            break

    metrics = ['Max Deviation\n(m)', 'Recovery Time\n(min)']
    fb_values = [max_dev_fb, recovery_fb]
    ff_values = [max_dev_ff, recovery_ff]

    x = np.arange(len(metrics))
    width = 0.35

    ax.bar(x - width/2, fb_values, width, label='Feedback Only', alpha=0.8)
    ax.bar(x + width/2, ff_values, width, label='FF + FB', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel('Value')
    ax.set_title('Performance Metrics Comparison')
    ax.legend()
    ax.grid(True, axis='y')

    plt.tight_layout()
    plt.savefig('feedforward_control_comparison.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: feedforward_control_comparison.png")

    # 性能改进
    improvement_dev = (max_dev_fb - max_dev_ff) / max_dev_fb * 100
    improvement_rec = (recovery_fb - recovery_ff) / recovery_fb * 100 if not np.isnan(recovery_fb) else 0

    print("\n" + "=" * 80)
    print("案例8总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. 前馈控制原理：")
    print("     • 基于可测扰动进行主动补偿")
    print("     • 不等误差产生就开始控制")
    print("     • 需要准确的扰动通道模型")

    print("\n  2. 前馈控制器设计：")
    print("     • 理想前馈：u_ff = -d / K")
    print("     • 目标：完全抵消扰动影响")
    print("     • 实际需要根据模型调整")

    print("\n  3. 前馈+反馈组合：")
    print("     • 前馈：快速响应，主动补偿")
    print("     • 反馈：消除残余误差，鲁棒性")
    print("     • 优势互补，性能最优")

    print("\n  4. 性能提升：")
    print(f"     • 最大偏差减少：{improvement_dev:.1f}%")
    print(f"     • 恢复时间缩短：{improvement_rec:.1f}%")

    print("\n  5. 应用条件：")
    print("     • 扰动必须可测或可预测")
    print("     • 需要准确的过程模型")
    print("     • 通常与反馈控制组合使用")

    print("\n[下一步学习]")
    print("  → 案例9：系统建模（机理建模方法）")
    print("  → 案例10：频域分析（Bode图法）")

    plt.show()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""
    compare_and_visualize()

    print("\n" + "=" * 80)
    print("案例8演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
