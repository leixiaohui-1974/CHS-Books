"""
可视化工具

绘制仿真结果图表
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# 设置中文字体支持（如果需要）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def plot_step_response(results, show=False):
    """
    绘制阶跃响应结果

    Args:
        results: 包含仿真数据的字典
        show: 是否显示图形

    Returns:
        fig: matplotlib图形对象
    """
    time = results['time']
    h = results['h']
    h_ref = results['h_ref']
    u = results['u']
    Q_in = results['Q_in']
    Q_out = results['Q_out']
    metrics = results['metrics']

    # 创建图形
    fig = plt.figure(figsize=(12, 10))
    gs = GridSpec(4, 1, figure=fig, hspace=0.3)

    # 子图1: 水深
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(time, h_ref, 'r--', linewidth=2, label='Setpoint')
    ax1.plot(time, h, 'b-', linewidth=1.5, label='Water Level')
    ax1.axhline(h_ref[0], color='gray', linestyle=':', alpha=0.5)
    ax1.set_ylabel('Water Level (m)', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Single Pool Canal - PID Control Step Response', fontsize=14, fontweight='bold')

    # 添加性能指标文本
    textstr = f"Overshoot: {metrics['overshoot']:.1f}%\n"
    textstr += f"Rise Time: {metrics['rise_time']:.0f} s\n"
    textstr += f"Settling Time: {metrics['settling_time']:.0f} s\n"
    textstr += f"SS Error: {metrics['steady_state_error']:.4f} m"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    # 子图2: 闸门开度
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(time, u, 'g-', linewidth=1.5, label='Gate Opening')
    ax2.set_ylabel('Gate Opening (m)', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 子图3: 流量
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(time, Q_in, 'b-', linewidth=1.5, label='Inflow')
    ax3.plot(time, Q_out, 'r-', linewidth=1.5, label='Outflow')
    ax3.set_ylabel('Flow Rate (m³/s)', fontsize=12)
    ax3.legend(loc='best', fontsize=10)
    ax3.grid(True, alpha=0.3)

    # 子图4: 误差
    ax4 = fig.add_subplot(gs[3, 0])
    error = h_ref - h
    ax4.plot(time, error, 'm-', linewidth=1.5, label='Tracking Error')
    ax4.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Error (m)', fontsize=12)
    ax4.legend(loc='best', fontsize=10)
    ax4.grid(True, alpha=0.3)

    if show:
        plt.show()

    return fig


def plot_disturbance_response(results, show=False):
    """
    绘制扰动响应结果

    Args:
        results: 包含仿真数据的字典
        show: 是否显示图形

    Returns:
        fig: matplotlib图形对象
    """
    time = results['time']
    h = results['h']
    h_ref = results['h_ref']
    u = results['u']
    Q_in = results['Q_in']
    t_dist = results['t_disturbance']

    fig = plt.figure(figsize=(12, 8))
    gs = GridSpec(3, 1, figure=fig, hspace=0.3)

    # 子图1: 水深
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(time, h_ref, 'r--', linewidth=2, label='Setpoint')
    ax1.plot(time, h, 'b-', linewidth=1.5, label='Water Level')
    ax1.axvline(t_dist, color='orange', linestyle='--', alpha=0.7, label='Disturbance')
    ax1.set_ylabel('Water Level (m)', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Disturbance Rejection Performance', fontsize=14, fontweight='bold')

    # 添加性能指标
    textstr = f"Max Deviation: {results['max_deviation']:.4f} m\n"
    textstr += f"Recovery Time: {results['recovery_time']:.0f} s"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    # 子图2: 闸门开度
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(time, u, 'g-', linewidth=1.5, label='Gate Opening')
    ax2.axvline(t_dist, color='orange', linestyle='--', alpha=0.7)
    ax2.set_ylabel('Gate Opening (m)', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 子图3: 流入流量
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(time, Q_in, 'b-', linewidth=1.5, label='Inflow (Disturbance)')
    ax3.axvline(t_dist, color='orange', linestyle='--', alpha=0.7)
    ax3.set_xlabel('Time (s)', fontsize=12)
    ax3.set_ylabel('Inflow (m³/s)', fontsize=12)
    ax3.legend(loc='best', fontsize=10)
    ax3.grid(True, alpha=0.3)

    if show:
        plt.show()

    return fig


def plot_controller_comparison(results, show=False):
    """
    绘制不同控制器的对比

    Args:
        results: 包含多个控制器结果的字典
        show: 是否显示图形

    Returns:
        fig: matplotlib图形对象
    """
    time = results['time']
    h_ref = results['h_ref']

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('Controller Comparison: P vs PI vs PID', fontsize=14, fontweight='bold')

    colors = {'P': 'blue', 'PI': 'green', 'PID': 'red'}
    linestyles = {'P': '--', 'PI': '-.', 'PID': '-'}

    # 子图1: 水深响应
    ax1 = axes[0]
    ax1.plot(time, np.full_like(time, h_ref), 'k--', linewidth=2, label='Setpoint', alpha=0.7)

    for name in ['P', 'PI', 'PID']:
        if name in results:
            h = results[name]['h']
            ax1.plot(time, h, color=colors[name], linestyle=linestyles[name],
                    linewidth=1.5, label=f'{name} Controller')

    ax1.set_ylabel('Water Level (m)', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, min(time[-1], 1500)])  # 只显示前1500秒

    # 子图2: 闸门开度
    ax2 = axes[1]
    for name in ['P', 'PI', 'PID']:
        if name in results:
            u = results[name]['u']
            ax2.plot(time, u, color=colors[name], linestyle=linestyles[name],
                    linewidth=1.5, label=f'{name} Controller')

    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Gate Opening (m)', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, min(time[-1], 1500)])

    plt.tight_layout()

    # 打印性能对比表
    print("\n性能对比:")
    print(f"{'Controller':<12} {'Overshoot':<12} {'Settling Time':<15} {'SS Error':<12}")
    print("-" * 60)
    for name in ['P', 'PI', 'PID']:
        if name in results:
            metrics = results[name]['metrics']
            print(f"{name:<12} {metrics['overshoot']:>10.1f}%  "
                  f"{metrics['settling_time']:>12.0f} s  "
                  f"{metrics['steady_state_error']:>10.4f} m")

    if show:
        plt.show()

    return fig


if __name__ == "__main__":
    # 测试代码 - 生成示例数据
    print("可视化模块测试")

    # 模拟一些数据
    time = np.linspace(0, 2000, 2000)
    h_ref = np.full_like(time, 2.5)
    h_ref[:100] = 2.0
    h = 2.0 + 0.5 * (1 - np.exp(-time/300)) * (1 + 0.1*np.sin(time/50))
    h = np.clip(h, 1.5, 3.0)
    u = np.ones_like(time) * 0.5
    Q_in = np.ones_like(time) * 20.0
    Q_out = Q_in.copy()

    metrics = {
        'overshoot': 8.5,
        'rise_time': 350,
        'settling_time': 820,
        'steady_state_error': 0.005,
        'IAE': 150,
        'ISE': 45
    }

    results = {
        'time': time,
        'h': h,
        'h_ref': h_ref,
        'u': u,
        'Q_in': Q_in,
        'Q_out': Q_out,
        'metrics': metrics
    }

    fig = plot_step_response(results, show=True)
    print("测试完成!")
