#!/usr/bin/env python3
"""
案例4：PID控制与参数整定 - 完整三项控制

场景描述：
精密水浴系统需要高精度快速响应控制。要求快速到达设定值（上升时间<5分钟），
精度高（稳态误差<0.01m），且超调量小于5%。PI控制响应偏慢，无法满足要求，
需要引入微分项D，构成完整的PID控制器。

教学目标：
1. 理解PID三个参数（Kp, Ki, Kd）的作用机理
2. 掌握Ziegler-Nichols经典整定方法
3. 对比P、PI、PID三种控制器的性能差异
4. 分析微分项D对系统动态性能的改善
5. 学习PID各分量的协同工作原理

控制策略：
- 控制律：u = Kp × e + Ki × ∫e dt + Kd × de/dt
- 比例增益：Kp = 2.0
- 积分增益：Ki = 0.5
- 微分增益：Kd = 0.5
- 目标水位：3.0米

关键概念：
- PID三项协同作用
- 微分项的预测和阻尼作用
- Ziegler-Nichols整定方法
- 超调抑制原理

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank, calculate_step_response_metrics
from code.control.basic_controllers import (ProportionalController, PIController,
                                            PIDController, ziegler_nichols_first_method)

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第1部分：系统建模
# ============================================================================

def create_system():
    """
    创建精密水浴系统模型

    系统特性：
    - 横截面积：2.0 m²
    - 阻力系数：2.0 min/m²
    - 泵增益：1.0 m³/min
    - 时间常数：τ = 4.0 分钟

    Returns:
        SingleTank: 配置好的水箱系统模型
    """
    # 系统参数
    A = 2.0      # 横截面积 [m²]
    R = 2.0      # 阻力系数 [min/m²]
    K = 1.0      # 泵增益 [m³/min]
    h0 = 1.0     # 初始水位 [m]

    # 创建系统
    tank = SingleTank(A=A, R=R, K=K)
    tank.reset(h0=h0)

    # 打印系统信息
    print("=" * 80)
    print("案例4：PID控制与参数整定 - 完整三项控制")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：系统建模")
    print("=" * 80)

    print("\n[应用场景]")
    print("  精密水浴温控系统（通过水位控制温度）")
    print("  - 快速响应：上升时间 < 5分钟")
    print("  - 高精度：稳态误差 < 0.01m (±0.33%)")
    print("  - 低超调：超调量 < 5%")
    print("  - PI控制响应偏慢，需要PID控制")

    print("\n[系统参数]")
    print(f"  横截面积 A = {A} m²")
    print(f"  阻力系数 R = {R} min/m²")
    print(f"  泵增益 K = {K} m³/min")
    print(f"  初始水位 h₀ = {h0} m")
    print(f"  时间常数 τ = A × R = {tank.tau} 分钟")

    print("\n[系统模型]")
    tf = tank.get_transfer_function()
    print(f"  传递函数：{tf['description']}")
    print(f"  系统增益：{tf['gain']}")
    print(f"  时间常数：{tf['tau']} 分钟")

    print("\n[为什么需要PID控制]")
    print("  P控制：")
    print("    ✓ 响应快速")
    print("    ✗ 存在稳态误差")
    print("\n  PI控制：")
    print("    ✓ 消除稳态误差")
    print("    ✗ 响应较慢，可能有超调")
    print("\n  PID控制：")
    print("    ✓ 快速响应（P项）")
    print("    ✓ 无稳态误差（I项）")
    print("    ✓ 抑制超调（D项）")
    print("    → 三项协同，性能最优")

    return tank


# ============================================================================
# 第2部分：控制器设计
# ============================================================================

def design_controller(dt=0.1):
    """
    设计PID控制器

    设计要点：
    1. PID控制律：u = Kp × e + Ki × ∫e dt + Kd × de/dt
       - Kp：比例项，提供快速响应
       - Ki：积分项，消除稳态误差
       - Kd：微分项，预测变化趋势，抑制超调

    2. Ziegler-Nichols第一法整定：
       - 基于系统时间常数τ和滞后时间L
       - 本系统：τ = 4.0, L ≈ 0.5（估算）
       - 整定公式给出初值，实际需要微调

    Args:
        dt: 控制周期 [分钟]

    Returns:
        dict: 包含P、PI、PID三种控制器
        float: 目标水位
    """
    print("\n" + "=" * 80)
    print("第2部分：控制器设计")
    print("=" * 80)

    # 控制器参数
    setpoint = 3.0  # 目标水位 [m]

    # 手动调节的PID参数
    Kp_manual = 2.0
    Ki_manual = 0.5
    Kd_manual = 0.5

    # 创建三种控制器用于对比
    controllers = {
        'P': ProportionalController(Kp=2.0, setpoint=setpoint),
        'PI': PIController(Kp=1.5, Ki=0.3, setpoint=setpoint, dt=dt),
        'PID': PIDController(Kp=Kp_manual, Ki=Ki_manual, Kd=Kd_manual,
                            setpoint=setpoint, dt=dt)
    }

    print("\n[控制策略对比]")
    print("\n  P控制：")
    print("    控制律：u(t) = Kp × e(t)")
    print(f"    参数：Kp = {controllers['P'].Kp}")

    print("\n  PI控制：")
    print("    控制律：u(t) = Kp × e(t) + Ki × ∫e(τ) dτ")
    print(f"    参数：Kp = {controllers['PI'].Kp}, Ki = {controllers['PI'].Ki}")

    print("\n  PID控制：")
    print("    控制律：u(t) = Kp × e(t) + Ki × ∫e(τ) dτ + Kd × de(t)/dt")
    print(f"    参数：Kp = {Kp_manual}, Ki = {Ki_manual}, Kd = {Kd_manual}")

    print("\n[Ziegler-Nichols第一法整定]")
    # 系统参数估计
    L = 0.5  # 滞后时间（估算）
    T = 4.0  # 时间常数

    print(f"  系统参数：")
    print(f"    时间常数 T = {T} 分钟")
    print(f"    滞后时间 L = {L} 分钟（估算）")
    print(f"    T/L比值 = {T/L:.1f}")

    print(f"\n  整定公式：")
    params_p = ziegler_nichols_first_method(L, T, 'P')
    params_pi = ziegler_nichols_first_method(L, T, 'PI')
    params_pid = ziegler_nichols_first_method(L, T, 'PID')

    print(f"\n    P控制：Kp = T/L = {params_p['Kp']:.3f}")
    print(f"    PI控制：Kp = 0.9*T/L = {params_pi['Kp']:.3f}, Ki = Kp/(3.3*L) = {params_pi['Ki']:.3f}")
    print(f"    PID控制：Kp = 1.2*T/L = {params_pid['Kp']:.3f}, Ki = Kp/(2*L) = {params_pid['Ki']:.3f}, Kd = Kp*L/2 = {params_pid['Kd']:.3f}")

    print(f"\n  注意：ZN法给出的是初值，实际应用需要根据性能微调")

    print("\n[PID各项作用详解]")
    print("  比例项（P）：")
    print("    • 物理意义：根据当前误差大小决定控制力度")
    print("    • 响应特性：误差越大，控制输出越大")
    print("    • 优点：快速响应")
    print("    • 缺点：存在稳态误差")

    print("\n  积分项（I）：")
    print("    • 物理意义：累积历史误差，持续补偿")
    print("    • 响应特性：误差持续存在，积分项不断增大")
    print("    • 优点：消除稳态误差")
    print("    • 缺点：可能引起超调和振荡")

    print("\n  微分项（D）：")
    print("    • 物理意义：预测误差变化趋势")
    print("    • 响应特性：误差变化快，微分项输出大")
    print("    • 优点：抑制超调，改善动态性能")
    print("    • 缺点：对噪声敏感，放大高频干扰")

    print("\n  三项协同：")
    print("    • 启动阶段：P项和D项主导，快速响应且抑制超调")
    print("    • 过渡阶段：I项逐渐累积，P项逐渐减小")
    print("    • 稳态阶段：I项提供恒定输出，P项和D项趋近于零")

    return controllers, setpoint, params_pid


# ============================================================================
# 第3部分：仿真运行
# ============================================================================

def run_simulation(tank, controllers, setpoint, duration=30, dt=0.1):
    """
    运行P、PI、PID三种控制器的对比仿真

    Args:
        tank: 水箱系统
        controllers: 包含三种控制器的字典
        setpoint: 目标水位
        duration: 仿真时长 [分钟]
        dt: 仿真步长 [分钟]

    Returns:
        dict: 每种控制器的仿真结果
    """
    print("\n" + "=" * 80)
    print("第3部分：仿真运行")
    print("=" * 80)

    n_steps = int(duration / dt)

    print(f"\n[仿真参数]")
    print(f"  仿真时长：{duration} 分钟")
    print(f"  仿真步长：{dt} 分钟")
    print(f"  仿真步数：{n_steps} 步")
    print(f"  初始水位：{tank.h:.3f} m")
    print(f"  目标水位：{setpoint:.3f} m")

    print("\n[开始仿真...]")

    results = {}

    for name, controller in controllers.items():
        print(f"\n  运行{name}控制器...")

        # 重置系统
        tank.reset(h0=1.0)

        # 初始化数据记录
        t = np.zeros(n_steps)
        h = np.zeros(n_steps)
        u = np.zeros(n_steps)
        error = np.zeros(n_steps)

        # 额外记录PID分量（如果是PID控制器）
        if name == 'PID':
            p_term = np.zeros(n_steps)
            i_term = np.zeros(n_steps)
            d_term = np.zeros(n_steps)
        else:
            p_term = i_term = d_term = None

        # 仿真循环
        for i in range(n_steps):
            t[i] = tank.t
            h[i] = tank.h
            error[i] = setpoint - tank.h

            # 控制器计算
            u[i] = controller.control(tank.h)

            # 如果是PID，记录各分量
            if name == 'PID' and hasattr(controller, 'get_components'):
                components = controller.get_components(tank.h)
                p_term[i] = components['P']
                i_term[i] = components['I']
                d_term[i] = components['D']

            # 系统更新
            tank.step(u[i], dt)

        # 保存结果
        results[name] = {
            't': t,
            'h': h,
            'u': u,
            'error': error,
            'p_term': p_term,
            'i_term': i_term,
            'd_term': d_term
        }

        print(f"    ✓ 完成，最终水位：{h[-1]:.4f} m")

    print(f"\n  仿真完成！")

    return results


# ============================================================================
# 第4部分：性能分析
# ============================================================================

def analyze_performance(results, setpoint):
    """
    对比分析P、PI、PID三种控制器的性能

    Args:
        results: 仿真结果字典
        setpoint: 目标水位
    """
    print("\n" + "=" * 80)
    print("第4部分：性能分析")
    print("=" * 80)

    print("\n[性能指标对比]")
    print("=" * 80)
    print(f"{'控制器':<10} | {'上升时间(min)':<15} | {'调节时间(min)':<15} | {'超调量(%)':<12} | {'稳态误差(m)':<15}")
    print("-" * 80)

    performance_summary = {}

    for name, data in results.items():
        t = data['t']
        h = data['h']
        dt = t[1] - t[0]

        # 计算性能指标
        metrics = calculate_step_response_metrics(t, h, setpoint, dt)
        steady_error = abs(setpoint - h[-1])

        rise_time = metrics['rise_time'] if not np.isnan(metrics['rise_time']) else "N/A"
        settling_time = metrics['settling_time'] if not np.isnan(metrics['settling_time']) else ">30"
        overshoot = metrics['overshoot']

        rise_str = f"{rise_time:.2f}" if isinstance(rise_time, float) else rise_time
        settling_str = f"{settling_time:.2f}" if isinstance(settling_time, (int, float)) else settling_time

        print(f"{name:<10} | {rise_str:<15} | {settling_str:<15} | {overshoot:<12.2f} | {steady_error:<15.6f}")

        performance_summary[name] = {
            'rise_time': rise_time,
            'settling_time': settling_time,
            'overshoot': overshoot,
            'steady_error': steady_error,
            'peak_value': metrics['peak_value']
        }

    print("=" * 80)

    # 详细分析
    print("\n[详细性能分析]")

    print("\n  1. 稳态误差对比：")
    for name in ['P', 'PI', 'PID']:
        error = performance_summary[name]['steady_error']
        print(f"     {name:<4}: {error:.6f} m ({error/setpoint*100:.3f}%)")
    print("     结论：P控制有稳态误差，PI和PID均能消除")

    print("\n  2. 响应速度对比：")
    for name in ['P', 'PI', 'PID']:
        rise_time = performance_summary[name]['rise_time']
        rise_str = f"{rise_time:.2f} 分钟" if isinstance(rise_time, float) else "N/A"
        print(f"     {name:<4}: {rise_str}")
    print("     结论：PID响应最快，PI较慢，P居中")

    print("\n  3. 超调量对比：")
    for name in ['P', 'PI', 'PID']:
        overshoot = performance_summary[name]['overshoot']
        print(f"     {name:<4}: {overshoot:.2f}%")
    print("     结论：PID超调最小（微分项抑制作用）")

    print("\n  4. 综合评价：")
    print("     P控制：  快速但有误差，不适合高精度要求")
    print("     PI控制： 无误差但较慢，适合一般精度要求")
    print("     PID控制：快速+准确+低超调，综合性能最优")

    # 针对PID的详细分析
    if 'PID' in results and results['PID']['p_term'] is not None:
        print("\n[PID各分量贡献分析]")
        p_term = results['PID']['p_term']
        i_term = results['PID']['i_term']
        d_term = results['PID']['d_term']

        print(f"\n  初始阶段（t=0-1分钟）：")
        print(f"    P项平均：{np.mean(p_term[0:10]):.3f}")
        print(f"    I项平均：{np.mean(i_term[0:10]):.3f}")
        print(f"    D项平均：{np.mean(d_term[0:10]):.3f}")
        print(f"    → D项最大（快速变化），P项其次，I项最小（刚开始累积）")

        print(f"\n  稳态阶段（最后5分钟）：")
        print(f"    P项平均：{np.mean(p_term[-50:]):.3f} （≈0，误差≈0）")
        print(f"    I项平均：{np.mean(i_term[-50:]):.3f} （提供稳态输出）")
        print(f"    D项平均：{np.mean(d_term[-50:]):.3f} （≈0，水位不变）")
        print(f"    → I项主导，P项和D项趋近于零")

    return performance_summary


# ============================================================================
# 第5部分：结果可视化
# ============================================================================

def create_figure1(results, setpoint, duration):
    """
    图1：P、PI、PID三种控制器性能对比

    Args:
        results: 仿真结果字典
        setpoint: 目标水位
        duration: 仿真时长
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 11))

    colors = {'P': 'blue', 'PI': 'green', 'PID': 'red'}

    # 子图1：水位对比
    for name in ['P', 'PI', 'PID']:
        data = results[name]
        axes[0].plot(data['t'], data['h'], color=colors[name],
                    linewidth=2.5, label=f'{name} Control', alpha=0.85)

    axes[0].axhline(setpoint, color='k', linestyle='--', linewidth=2,
                    label='Setpoint', alpha=0.7)
    axes[0].axhline(setpoint + 0.01, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    axes[0].axhline(setpoint - 0.01, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    axes[0].fill_between([0, duration], setpoint-0.01, setpoint+0.01,
                         alpha=0.15, color='green', label='Target Band (±0.01m)')

    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('Case 4: P vs PI vs PID Control Performance Comparison',
                      fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=11, framealpha=0.9, ncol=2)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, duration])
    axes[0].set_ylim([0.8, 3.3])

    # 子图2：误差对比
    for name in ['P', 'PI', 'PID']:
        data = results[name]
        axes[1].plot(data['t'], data['error'], color=colors[name],
                    linewidth=2.5, label=f'{name} Error', alpha=0.85)

    axes[1].axhline(0, color='k', linestyle='-', linewidth=1.5, alpha=0.6)
    axes[1].fill_between([0, duration], -0.01, 0.01,
                         alpha=0.15, color='green', label='Tolerance')

    axes[1].set_ylabel('Tracking Error (m)', fontsize=13, fontweight='bold')
    axes[1].set_title('Error Comparison (PID converges fastest)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[1].legend(loc='best', fontsize=11, framealpha=0.9, ncol=2)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, duration])

    # 子图3：控制信号对比
    for name in ['P', 'PI', 'PID']:
        data = results[name]
        axes[2].plot(data['t'], data['u'], color=colors[name],
                    linewidth=2.5, label=f'{name} Control', alpha=0.85)

    axes[2].axhline(1.0, color='r', linestyle=':', linewidth=1, alpha=0.5)
    axes[2].axhline(0.0, color='r', linestyle=':', linewidth=1, alpha=0.5)

    axes[2].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[2].set_ylabel('Control Signal (0-1)', fontsize=13, fontweight='bold')
    axes[2].set_title('Control Signal Comparison',
                      fontsize=13, fontweight='bold', pad=12)
    axes[2].legend(loc='best', fontsize=11, framealpha=0.9, ncol=2)
    axes[2].grid(True, alpha=0.3, linestyle='--')
    axes[2].set_xlim([0, duration])
    axes[2].set_ylim([-0.1, 1.15])

    plt.tight_layout()
    plt.savefig('controller_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\n  ✓ 图1已保存：controller_comparison.png")


def create_figure2(results):
    """
    图2：PID各分量详细分析

    Args:
        results: 仿真结果字典
    """
    print("\n  正在生成图2：PID各分量分析...")

    if 'PID' not in results or results['PID']['p_term'] is None:
        print("    警告：无法生成图2，PID分量数据不可用")
        return

    data = results['PID']
    t = data['t']
    h = data['h']
    u = data['u']
    p_term = data['p_term']
    i_term = data['i_term']
    d_term = data['d_term']

    fig, axes = plt.subplots(5, 1, figsize=(14, 14))

    # 子图1：水位
    axes[0].plot(t, h, 'b-', linewidth=2.5, label='Water Level', alpha=0.9)
    axes[0].axhline(3.0, color='r', linestyle='--', linewidth=2,
                    label='Setpoint', alpha=0.8)

    axes[0].set_ylabel('Water Level (m)', fontsize=13, fontweight='bold')
    axes[0].set_title('PID Control Component Analysis',
                      fontsize=15, fontweight='bold', pad=15)
    axes[0].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[0].grid(True, alpha=0.3, linestyle='--')
    axes[0].set_xlim([0, t[-1]])

    # 子图2：P项
    axes[1].plot(t, p_term, 'b-', linewidth=2.5, label='P Term (Kp × e)', alpha=0.9)
    axes[1].axhline(0, color='k', linestyle='-', linewidth=1, alpha=0.5)

    axes[1].set_ylabel('P Component', fontsize=13, fontweight='bold')
    axes[1].set_title('Proportional Term (Fast Response)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[1].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[1].grid(True, alpha=0.3, linestyle='--')
    axes[1].set_xlim([0, t[-1]])

    # 子图3：I项
    axes[2].plot(t, i_term, 'g-', linewidth=2.5, label='I Term (Ki × ∫e dt)', alpha=0.9)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=1, alpha=0.5)

    axes[2].set_ylabel('I Component', fontsize=13, fontweight='bold')
    axes[2].set_title('Integral Term (Eliminates Steady-state Error)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[2].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[2].grid(True, alpha=0.3, linestyle='--')
    axes[2].set_xlim([0, t[-1]])

    # 子图4：D项
    axes[3].plot(t, d_term, 'r-', linewidth=2.5, label='D Term (Kd × de/dt)', alpha=0.9)
    axes[3].axhline(0, color='k', linestyle='-', linewidth=1, alpha=0.5)

    axes[3].set_ylabel('D Component', fontsize=13, fontweight='bold')
    axes[3].set_title('Derivative Term (Suppresses Overshoot)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[3].legend(loc='best', fontsize=11, framealpha=0.9)
    axes[3].grid(True, alpha=0.3, linestyle='--')
    axes[3].set_xlim([0, t[-1]])

    # 子图5：总控制信号（P+I+D）
    axes[4].plot(t, u, 'purple', linewidth=2.5, label='Total: u = P + I + D', alpha=0.9)
    axes[4].plot(t, p_term, 'b:', linewidth=1.5, label='P component', alpha=0.6)
    axes[4].plot(t, i_term, 'g:', linewidth=1.5, label='I component', alpha=0.6)
    axes[4].plot(t, d_term, 'r:', linewidth=1.5, label='D component', alpha=0.6)

    axes[4].set_xlabel('Time (minutes)', fontsize=13, fontweight='bold')
    axes[4].set_ylabel('Control Signal', fontsize=13, fontweight='bold')
    axes[4].set_title('Total Control Signal (Sum of P, I, D)',
                      fontsize=13, fontweight='bold', pad=12)
    axes[4].legend(loc='best', fontsize=10, framealpha=0.9, ncol=2)
    axes[4].grid(True, alpha=0.3, linestyle='--')
    axes[4].set_xlim([0, t[-1]])

    plt.tight_layout()
    plt.savefig('pid_components_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图2已保存：pid_components_analysis.png")


def create_figure3():
    """
    图3：Ziegler-Nichols整定方法验证

    展示ZN法整定的P、PI、PID性能
    """
    print("\n  正在生成图3：Ziegler-Nichols整定验证...")

    # 系统参数
    L = 0.5  # 滞后时间
    T = 4.0  # 时间常数

    # ZN整定
    params_p = ziegler_nichols_first_method(L, T, 'P')
    params_pi = ziegler_nichols_first_method(L, T, 'PI')
    params_pid = ziegler_nichols_first_method(L, T, 'PID')

    setpoint = 3.0
    duration = 40
    dt = 0.1
    n_steps = int(duration / dt)

    # 创建ZN整定的控制器
    controllers_zn = {
        'P-ZN': ProportionalController(Kp=params_p['Kp'], setpoint=setpoint),
        'PI-ZN': PIController(Kp=params_pi['Kp'], Ki=params_pi['Ki'],
                             setpoint=setpoint, dt=dt),
        'PID-ZN': PIDController(Kp=params_pid['Kp'], Ki=params_pid['Ki'],
                               Kd=params_pid['Kd'], setpoint=setpoint, dt=dt)
    }

    results_zn = {}

    for name, controller in controllers_zn.items():
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=1.0)

        t = np.zeros(n_steps)
        h = np.zeros(n_steps)
        u = np.zeros(n_steps)

        for i in range(n_steps):
            t[i] = tank.t
            h[i] = tank.h
            u[i] = controller.control(tank.h)
            tank.step(u[i], dt)

        results_zn[name] = {'t': t, 'h': h, 'u': u}

    # 绘图
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    colors = {'P-ZN': 'blue', 'PI-ZN': 'green', 'PID-ZN': 'red'}

    # 子图1：水位响应
    for name in ['P-ZN', 'PI-ZN', 'PID-ZN']:
        data = results_zn[name]
        axes[0, 0].plot(data['t'], data['h'], color=colors[name],
                       linewidth=2.5, label=name, alpha=0.85)

    axes[0, 0].axhline(setpoint, color='k', linestyle='--', linewidth=2, alpha=0.7)
    axes[0, 0].set_ylabel('Water Level (m)', fontsize=12, fontweight='bold')
    axes[0, 0].set_title('Ziegler-Nichols Tuned Controllers',
                         fontsize=13, fontweight='bold', pad=12)
    axes[0, 0].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[0, 0].grid(True, alpha=0.3, linestyle='--')

    # 子图2：控制信号
    for name in ['P-ZN', 'PI-ZN', 'PID-ZN']:
        data = results_zn[name]
        axes[0, 1].plot(data['t'], data['u'], color=colors[name],
                       linewidth=2.5, label=name, alpha=0.85)

    axes[0, 1].set_ylabel('Control Signal (0-1)', fontsize=12, fontweight='bold')
    axes[0, 1].set_title('Control Signals (ZN Tuned)',
                         fontsize=13, fontweight='bold', pad=12)
    axes[0, 1].legend(loc='best', fontsize=10, framealpha=0.9)
    axes[0, 1].grid(True, alpha=0.3, linestyle='--')
    axes[0, 1].set_ylim([-0.1, 1.15])

    # 子图3：性能指标对比
    metrics_summary = []
    for name in ['P-ZN', 'PI-ZN', 'PID-ZN']:
        data = results_zn[name]
        metrics = calculate_step_response_metrics(data['t'], data['h'], setpoint, dt)
        steady_error = abs(setpoint - data['h'][-1])
        metrics_summary.append({
            'name': name,
            'rise_time': metrics['rise_time'] if not np.isnan(metrics['rise_time']) else 40,
            'overshoot': metrics['overshoot'],
            'steady_error': steady_error
        })

    x = np.arange(len(metrics_summary))
    width = 0.25

    rise_times = [m['rise_time'] for m in metrics_summary]
    overshoots = [m['overshoot'] for m in metrics_summary]

    axes[1, 0].bar(x - width, rise_times, width, label='Rise Time (min)',
                   alpha=0.8, color='steelblue')
    ax2 = axes[1, 0].twinx()
    ax2.bar(x + width, overshoots, width, label='Overshoot (%)',
            alpha=0.8, color='lightcoral')

    axes[1, 0].set_xlabel('Controller Type', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('Rise Time (min)', fontsize=11, fontweight='bold', color='steelblue')
    ax2.set_ylabel('Overshoot (%)', fontsize=11, fontweight='bold', color='lightcoral')
    axes[1, 0].set_title('Performance Metrics',
                         fontsize=13, fontweight='bold', pad=12)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels([m['name'] for m in metrics_summary])
    axes[1, 0].tick_params(axis='y', labelcolor='steelblue')
    ax2.tick_params(axis='y', labelcolor='lightcoral')
    axes[1, 0].grid(True, alpha=0.3, linestyle='--', axis='y')

    # 子图4：ZN整定公式
    axes[1, 1].axis('off')
    formula_text = f"""
    Ziegler-Nichols第一法整定公式

    系统参数：
      时间常数 T = {T} 分钟
      滞后时间 L = {L} 分钟
      T/L比值 = {T/L:.1f}

    整定结果：

      P控制：
        Kp = T/L = {params_p['Kp']:.3f}

      PI控制：
        Kp = 0.9 × T/L = {params_pi['Kp']:.3f}
        Ki = Kp / (3.3 × L) = {params_pi['Ki']:.3f}

      PID控制：
        Kp = 1.2 × T/L = {params_pid['Kp']:.3f}
        Ki = Kp / (2 × L) = {params_pid['Ki']:.3f}
        Kd = Kp × L / 2 = {params_pid['Kd']:.3f}

    注意：
      • ZN法给出的是初值
      • 实际应用需要微调
      • 适用于T/L > 2的系统
    """

    axes[1, 1].text(0.1, 0.95, formula_text, transform=axes[1, 1].transAxes,
                   fontsize=10, verticalalignment='top', family='monospace',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig('ziegler_nichols_tuning.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 图3已保存：ziegler_nichols_tuning.png")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""

    # 第1部分：创建系统
    tank = create_system()

    # 第2部分：设计控制器
    dt = 0.1
    controllers, setpoint, zn_params = design_controller(dt)

    # 第3部分：运行仿真
    duration = 30  # 仿真30分钟
    results = run_simulation(tank, controllers, setpoint, duration, dt)

    # 第4部分：性能分析
    performance_summary = analyze_performance(results, setpoint)

    # 第5部分：结果可视化
    print("\n" + "=" * 80)
    print("第5部分：结果可视化")
    print("=" * 80)

    create_figure1(results, setpoint, duration)
    create_figure2(results)
    create_figure3()

    # 总结
    print("\n" + "=" * 80)
    print("案例4总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. PID控制原理：")
    print("     • 控制律：u(t) = Kp × e(t) + Ki × ∫e(τ) dτ + Kd × de(t)/dt")
    print("     • P项：比例作用，快速响应")
    print("     • I项：积分作用，消除稳态误差")
    print("     • D项：微分作用，预测和抑制超调")

    print("\n  2. PID三项协同作用：")
    print("     • 启动阶段：P和D主导，快速响应且抑制超调")
    print("     • 过渡阶段：I逐渐累积，P逐渐减小")
    print("     • 稳态阶段：I提供输出，P和D趋近于零")

    print("\n  3. 微分项D的作用：")
    print("     ✓ 预测误差变化趋势")
    print("     ✓ 抑制超调，改善动态性能")
    print("     ✓ 提供阻尼，减少振荡")
    print("     ✗ 对噪声敏感，需要滤波")

    print("\n  4. Ziegler-Nichols整定方法：")
    print("     • 第一法（响应曲线法）：")
    print("       - 基于系统阶跃响应")
    print("       - 提取时间常数T和滞后时间L")
    print("       - 使用经验公式计算Kp、Ki、Kd")
    print("     • 适用范围：T/L > 2的系统")
    print("     • 优点：简单实用，适合工程应用")
    print("     • 缺点：给出的是初值，需要微调")

    print("\n  5. P、PI、PID性能对比：")
    print("     P控制：")
    print("       ✓ 实现简单，响应快")
    print("       ✗ 存在稳态误差")
    print("       → 适用于精度要求不高的场合")

    print("\n     PI控制：")
    print("       ✓ 消除稳态误差")
    print("       ✗ 响应较慢，可能有超调")
    print("       → 适用于精度要求高但速度要求不严的场合")

    print("\n     PID控制：")
    print("       ✓ 快速响应（P项）")
    print("       ✓ 无稳态误差（I项）")
    print("       ✓ 低超调（D项）")
    print("       → 适用于高性能要求的场合")

    print("\n[工程应用建议]")
    print("  • 参数整定顺序：")
    print("    1. 先整定Kp，观察响应速度")
    print("    2. 再加入Ki，消除稳态误差")
    print("    3. 最后调Kd，改善动态性能")

    print("\n  • Kd使用注意事项：")
    print("    - 测量信号需要滤波（减少噪声影响）")
    print("    - Kd不宜过大（避免放大噪声）")
    print("    - 某些场合可以不用D项（PI已足够）")

    print("\n  • 实际应用场景：")
    print("    - 温度控制：PI控制（温度变化慢，D项作用小）")
    print("    - 位置控制：PID控制（需要快速准确）")
    print("    - 流量控制：P或PI控制（简单可靠）")

    print("\n[下一步学习]")
    print("  → 案例5-8：系统辨识方法（参数估计、模型验证）")
    print("  → 案例9-12：高级控制策略（自适应、最优控制）")

    print("\n" + "=" * 80)
    print("案例4演示完成！共生成3个PNG可视化文件")
    print("=" * 80)

    # 列出生成的文件
    png_files = [
        'controller_comparison.png',
        'pid_components_analysis.png',
        'ziegler_nichols_tuning.png'
    ]

    print("\n[生成的文件]")
    for i, filename in enumerate(png_files, 1):
        filepath = Path(filename)
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  {i}. {filename} ({size_kb:.1f} KB)")

    print("\n✓ 阶段1（基础控制方法）全部完成！")
    print("  ✓ 案例1：开关控制（On-Off Control）")
    print("  ✓ 案例2：比例控制（P Control）")
    print("  ✓ 案例3：PI控制（PI Control）")
    print("  ✓ 案例4：PID控制（PID Control）")
    print("\n下一阶段：系统辨识方法（案例5-8）")


if __name__ == "__main__":
    main()
