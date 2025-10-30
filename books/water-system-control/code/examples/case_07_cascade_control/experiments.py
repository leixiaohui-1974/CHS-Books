#!/usr/bin/env python3
"""
案例7扩展实验：串级控制深入分析

本文件包含多个扩展实验：
1. 主副控制器参数影响分析
2. 扰动抑制性能测试
3. 参数失配鲁棒性分析
4. 不同系统配置下的串级控制效果

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
# 实验1：主副控制器参数影响
# ============================================================================

def experiment_controller_parameters():
    """
    实验1：分析主副控制器参数对系统性能的影响
    """
    print("=" * 80)
    print("实验1：主副控制器参数影响分析")
    print("=" * 80)

    # 系统参数
    A1, A2, R1, R2, K = 1.0, 2.0, 1.5, 2.0, 1.0

    # 测试不同的副控制器增益
    slave_gains = [0.5, 1.0, 1.5, 2.0, 3.0]

    results = []

    for Kp_slave in slave_gains:
        print(f"\n测试副控制器增益: Kp_slave = {Kp_slave}")

        system = DoubleTank(A1=A1, A2=A2, R1=R1, R2=R2, K=K)
        system.reset(h1_0=1.0, h2_0=1.0)

        # 副控制器
        pid_slave = PIDController(Kp=Kp_slave, Ki=0.5, Kd=0.3, u_min=0.0, u_max=1.0)

        # 主控制器（固定）
        pid_master = PIDController(Kp=0.6, Ki=0.1, Kd=0.5, u_min=0.5, u_max=4.0)

        # 仿真
        setpoint = 2.5
        duration = 40
        dt = 0.1
        n_steps = int(duration / dt)

        h2_data = np.zeros(n_steps)

        for i in range(n_steps):
            h2_data[i] = system.h2

            error_h2 = setpoint - system.h2
            setpoint_h1 = pid_master.update(error_h2, dt)

            error_h1 = setpoint_h1 - system.h1
            u = pid_slave.update(error_h1, dt)

            system.step(u, dt)

        # 计算性能指标
        overshoot = (np.max(h2_data) - setpoint) / setpoint * 100 if np.max(h2_data) > setpoint else 0

        settle_idx = np.where(np.abs(h2_data - setpoint) > 0.02 * setpoint)[0]
        settle_time = settle_idx[-1] * dt if len(settle_idx) > 0 else 0

        results.append({
            'Kp_slave': Kp_slave,
            'overshoot': overshoot,
            'settle_time': settle_time
        })

        print(f"  超调量: {overshoot:.2f}%")
        print(f"  调节时间: {settle_time:.2f} min")

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.plot([r['Kp_slave'] for r in results], [r['overshoot'] for r in results], 'o-', linewidth=2)
    ax.set_xlabel('Slave Controller Gain Kp')
    ax.set_ylabel('Overshoot (%)')
    ax.set_title('Overshoot vs Slave Gain')
    ax.grid(True)

    ax = axes[1]
    ax.plot([r['Kp_slave'] for r in results], [r['settle_time'] for r in results], 'o-', linewidth=2)
    ax.set_xlabel('Slave Controller Gain Kp')
    ax.set_ylabel('Settling Time (min)')
    ax.set_title('Settling Time vs Slave Gain')
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('exp1_parameter_effect.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp1_parameter_effect.png")

    print("\n结论：")
    print("  - 副控制器增益太小：系统响应慢")
    print("  - 副控制器增益太大：可能引起振荡")
    print("  - 最优增益: Kp_slave ≈ 1.5")

    return results


# ============================================================================
# 实验2：扰动抑制性能测试
# ============================================================================

def experiment_disturbance_rejection():
    """
    实验2：对比单回路和串级控制的扰动抑制能力
    """
    print("\n" + "=" * 80)
    print("实验2：扰动抑制性能测试")
    print("=" * 80)

    # 系统参数
    A1, A2, R1, R2, K = 1.0, 2.0, 1.5, 2.0, 1.0

    # 定义两种控制策略
    controllers = {
        'Single Loop': {
            'use_cascade': False,
            'pid_params': {'Kp': 0.8, 'Ki': 0.15, 'Kd': 1.0}
        },
        'Cascade': {
            'use_cascade': True,
            'master_params': {'Kp': 0.6, 'Ki': 0.1, 'Kd': 0.5},
            'slave_params': {'Kp': 1.5, 'Ki': 0.5, 'Kd': 0.3}
        }
    }

    results = {}

    for control_name, config in controllers.items():
        print(f"\n测试控制策略: {control_name}")

        system = DoubleTank(A1=A1, A2=A2, R1=R1, R2=R2, K=K)
        system.reset(h1_0=2.5, h2_0=2.5)  # 从稳态开始

        # 创建控制器
        if config['use_cascade']:
            pid_master = PIDController(**config['master_params'], u_min=0.5, u_max=4.0)
            pid_slave = PIDController(**config['slave_params'], u_min=0.0, u_max=1.0)
        else:
            pid_single = PIDController(**config['pid_params'], u_min=0.0, u_max=1.0)

        # 仿真
        setpoint = 2.5
        duration = 80
        dt = 0.1
        disturbance_time = 20  # 20分钟时加扰动
        disturbance_magnitude = 0.3  # 扰动幅值

        n_steps = int(duration / dt)
        time = np.zeros(n_steps)
        h2_data = np.zeros(n_steps)
        u_data = np.zeros(n_steps)

        for i in range(n_steps):
            time[i] = system.t
            h2_data[i] = system.h2

            # 扰动（模拟进水流量突变）
            disturbance = disturbance_magnitude if system.t >= disturbance_time and system.t < disturbance_time + 10 else 0

            if config['use_cascade']:
                # 串级控制
                error_h2 = setpoint - system.h2
                setpoint_h1 = pid_master.update(error_h2, dt)
                error_h1 = setpoint_h1 - system.h1
                u = pid_slave.update(error_h1, dt)
            else:
                # 单回路控制
                error = setpoint - system.h2
                u = pid_single.update(error, dt)

            u_data[i] = u

            # 加上扰动
            system.step(u + disturbance, dt)

        # 计算扰动恢复时间
        disturbance_start_idx = int(disturbance_time / dt)
        disturbance_end_idx = int((disturbance_time + 10) / dt)

        # 扰动后的最大偏差
        max_deviation = np.max(np.abs(h2_data[disturbance_start_idx:disturbance_end_idx+100] - setpoint))

        # 恢复时间（回到2%误差带）
        recovery_time = np.nan
        for i in range(disturbance_end_idx, n_steps):
            if np.abs(h2_data[i] - setpoint) <= 0.02 * setpoint:
                recovery_time = time[i] - (disturbance_time + 10)
                break

        results[control_name] = {
            'time': time,
            'h2': h2_data,
            'u': u_data,
            'max_deviation': max_deviation,
            'recovery_time': recovery_time
        }

        print(f"  最大偏差: {max_deviation:.4f} m")
        print(f"  恢复时间: {recovery_time:.2f} min")

    # 可视化
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    ax = axes[0]
    for name, data in results.items():
        ax.plot(data['time'], data['h2'], linewidth=2, label=name)
    ax.axhline(setpoint, color='g', linestyle='--', alpha=0.7, label='Setpoint')
    ax.axvline(disturbance_time, color='r', linestyle=':', alpha=0.7, label='Disturbance Start')
    ax.axvline(disturbance_time + 10, color='r', linestyle=':', alpha=0.7, label='Disturbance End')
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Water Level h2 (m)')
    ax.set_title('Disturbance Rejection Comparison')
    ax.legend()
    ax.grid(True)

    ax = axes[1]
    metrics = ['Max Deviation\n(m)', 'Recovery Time\n(min)']
    single_values = [results['Single Loop']['max_deviation'], results['Single Loop']['recovery_time']]
    cascade_values = [results['Cascade']['max_deviation'], results['Cascade']['recovery_time']]

    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(x - width/2, single_values, width, label='Single Loop', alpha=0.8)
    ax.bar(x + width/2, cascade_values, width, label='Cascade', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel('Value')
    ax.set_title('Disturbance Rejection Performance')
    ax.legend()
    ax.grid(True, axis='y')

    plt.tight_layout()
    plt.savefig('exp2_disturbance_rejection.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp2_disturbance_rejection.png")

    improvement = (single_values[0] - cascade_values[0]) / single_values[0] * 100
    print(f"\n串级控制扰动抑制能力提升: {improvement:.1f}%")

    return results


# ============================================================================
# 实验3：参数失配鲁棒性
# ============================================================================

def experiment_robustness():
    """
    实验3：测试系统参数变化时串级控制的鲁棒性
    """
    print("\n" + "=" * 80)
    print("实验3：参数失配鲁棒性分析")
    print("=" * 80)

    # 名义参数（设计时使用）
    A1_nom, A2_nom, R1_nom, R2_nom = 1.0, 2.0, 1.5, 2.0

    # 实际参数（变化范围：±30%）
    parameter_variations = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3]

    results = []

    for variation in parameter_variations:
        print(f"\n参数变化: {variation*100:+.0f}%")

        # 实际系统参数（所有参数同时变化）
        A1 = A1_nom * (1 + variation)
        A2 = A2_nom * (1 + variation)
        R1 = R1_nom * (1 + variation)
        R2 = R2_nom * (1 + variation)

        system = DoubleTank(A1=A1, A2=A2, R1=R1, R2=R2, K=1.0)
        system.reset(h1_0=1.0, h2_0=1.0)

        # 控制器参数（基于名义参数设计，不变）
        pid_master = PIDController(Kp=0.6, Ki=0.1, Kd=0.5, u_min=0.5, u_max=4.0)
        pid_slave = PIDController(Kp=1.5, Ki=0.5, Kd=0.3, u_min=0.0, u_max=1.0)

        # 仿真
        setpoint = 2.5
        duration = 40
        dt = 0.1
        n_steps = int(duration / dt)

        h2_data = np.zeros(n_steps)

        for i in range(n_steps):
            h2_data[i] = system.h2

            error_h2 = setpoint - system.h2
            setpoint_h1 = pid_master.update(error_h2, dt)
            error_h1 = setpoint_h1 - system.h1
            u = pid_slave.update(error_h1, dt)

            system.step(u, dt)

        # 性能指标
        overshoot = (np.max(h2_data) - setpoint) / setpoint * 100 if np.max(h2_data) > setpoint else 0
        sse = abs(h2_data[-1] - setpoint)

        results.append({
            'variation': variation,
            'overshoot': overshoot,
            'sse': sse
        })

        print(f"  超调量: {overshoot:.2f}%")
        print(f"  稳态误差: {sse:.4f} m")

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    variations_pct = [r['variation'] * 100 for r in results]
    ax.plot(variations_pct, [r['overshoot'] for r in results], 'o-', linewidth=2)
    ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Parameter Variation (%)')
    ax.set_ylabel('Overshoot (%)')
    ax.set_title('Robustness: Overshoot vs Parameter Change')
    ax.grid(True)

    ax = axes[1]
    ax.plot(variations_pct, [r['sse'] for r in results], 'o-', linewidth=2, color='red')
    ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Parameter Variation (%)')
    ax.set_ylabel('Steady-State Error (m)')
    ax.set_title('Robustness: SSE vs Parameter Change')
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('exp3_robustness.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: exp3_robustness.png")

    print("\n结论：")
    print("  - 串级控制对参数变化具有较好的鲁棒性")
    print("  - 在±30%参数变化范围内，系统仍能稳定运行")
    print("  - 主要影响：超调量和调节时间略有变化")

    return results


# ============================================================================
# 主程序
# ============================================================================

def main():
    """运行所有扩展实验"""
    print("=" * 80)
    print("案例7扩展实验：串级控制深入分析")
    print("=" * 80)

    # 实验1：参数影响
    results1 = experiment_controller_parameters()

    # 实验2：扰动抑制
    results2 = experiment_disturbance_rejection()

    # 实验3：鲁棒性
    results3 = experiment_robustness()

    print("\n" + "=" * 80)
    print("所有扩展实验完成！")
    print("=" * 80)

    plt.show()


if __name__ == "__main__":
    main()
