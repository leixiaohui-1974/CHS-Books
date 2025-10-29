"""
案例2：工业冷却塔精确水位控制 - 比例控制演示

教学目标：
1. 理解比例控制（P控制）的原理
2. 学习PID参数整定（Kp的选择）
3. 分析稳态误差问题
4. 掌握性能指标计算

适用对象：完成案例1的学生
前置知识：开关控制、一阶系统
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.models.water_tank.single_tank import SingleTank, calculate_step_response_metrics
from src.control.basic_controllers import OnOffController, ProportionalController

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def demo_proportional_control():
    """演示比例控制"""
    
    print("=" * 70)
    print("案例2：工业冷却塔精确水位控制")
    print("控制方法：比例控制（Proportional Control）")
    print("=" * 70)
    
    # 1. 场景说明
    print("\n[背景]")
    print("某化工厂冷却塔需要精确控制水位在3.0米：")
    print("  - 水位过高：冷却效率下降，可能溢出")
    print("  - 水位过低：循环泵吸空，设备损坏")
    print("  - 要求精度：±0.1米（±3.3%）")
    print("  - 开关控制无法满足要求，需要更精确的控制方法")
    
    # 2. 创建系统
    tank = SingleTank(A=2.0, R=2.0, K=1.0)
    tank.reset(h0=2.0)  # 初始水位2米
    
    print(f"\n[系统参数]")
    print(f"  横截面积: {tank.A} m²")
    print(f"  阻力系数: {tank.R} min/m²")
    print(f"  泵增益: {tank.K} m³/min")
    print(f"  时间常数: {tank.tau} 分钟")
    print(f"  传递函数: {tank.get_transfer_function()['description']}")
    
    # 3. 创建比例控制器
    Kp = 2.0  # 比例增益
    setpoint = 3.0  # 目标水位
    controller = ProportionalController(Kp=Kp, setpoint=setpoint)
    
    print(f"\n[控制器参数]")
    print(f"  控制类型: 比例控制（P控制）")
    print(f"  比例增益 Kp: {Kp}")
    print(f"  目标水位: {setpoint} m")
    print(f"  控制律: u = Kp × (setpoint - h)")
    
    # 4. 运行仿真
    duration = 60  # 仿真60分钟
    dt = 0.1
    n_steps = int(duration / dt)
    
    t_history = np.zeros(n_steps)
    h_history = np.zeros(n_steps)
    u_history = np.zeros(n_steps)
    error_history = np.zeros(n_steps)
    
    print(f"\n[仿真运行] 时长={duration}分钟, 步长={dt}分钟")
    
    for i in range(n_steps):
        t_history[i] = tank.t
        h_history[i] = tank.h
        
        # 计算误差
        error_history[i] = setpoint - tank.h
        
        # 控制器输出
        u_history[i] = controller.control(tank.h)
        
        # 系统更新
        tank.step(u_history[i], dt)
    
    # 5. 性能分析
    print(f"\n{'='*70}")
    print("控制性能分析")
    print("=" * 70)
    
    # 水位统计
    h_mean = np.mean(h_history[300:])  # 稳态部分（跳过前30分钟）
    h_std = np.std(h_history[300:])
    h_final = h_history[-1]
    steady_state_error = abs(setpoint - h_final)
    
    print(f"\n[水位性能]")
    print(f"  目标水位: {setpoint:.3f} m")
    print(f"  最终水位: {h_final:.3f} m")
    print(f"  平均水位: {h_mean:.3f} m")
    print(f"  标准差: {h_std:.4f} m")
    print(f"  稳态误差: {steady_state_error:.4f} m ({steady_state_error/setpoint*100:.2f}%)")
    
    # 阶跃响应指标
    metrics = calculate_step_response_metrics(t_history, h_history, setpoint, dt)
    
    print(f"\n[动态性能]")
    if not np.isnan(metrics['rise_time']):
        print(f"  上升时间: {metrics['rise_time']:.2f} 分钟")
    if not np.isnan(metrics['settling_time']):
        print(f"  调节时间: {metrics['settling_time']:.2f} 分钟")
    else:
        print(f"  调节时间: >60分钟（未稳定）")
    print(f"  超调量: {metrics['overshoot']:.2f}%")
    print(f"  峰值: {metrics['peak_value']:.3f} m")
    
    # 控制信号统计
    u_mean = np.mean(u_history[300:])
    u_std = np.std(u_history[300:])
    
    print(f"\n[控制信号]")
    print(f"  平均输出: {u_mean:.3f} (0-1)")
    print(f"  输出波动: {u_std:.4f}")
    print(f"  饱和次数: {np.sum((u_history >= 0.99) | (u_history <= 0.01))} 次")
    
    # 6. 分析比例控制的稳态误差
    print(f"\n[稳态误差分析]")
    print(f"  理论分析：")
    print(f"    在稳态时，dh/dt = 0，即 Q_in = Q_out")
    print(f"    Q_in = K × u = K × Kp × e （e为误差）")
    print(f"    Q_out = h / R")
    print(f"    因此：K × Kp × e = h / R")
    print(f"    解得：e = h / (K × Kp × R)")
    print(f"  ")
    print(f"  本例中：")
    theoretical_error = h_final / (tank.K * Kp * tank.R)
    print(f"    理论稳态误差 = {h_final:.3f} / ({tank.K} × {Kp} × {tank.R})")
    print(f"                 = {theoretical_error:.4f} m")
    print(f"    实际稳态误差 = {steady_state_error:.4f} m")
    print(f"    相对偏差 = {abs(theoretical_error - steady_state_error)/theoretical_error*100:.1f}%")
    
    # 7. 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # 子图1：水位变化
    axes[0].plot(t_history, h_history, 'b-', linewidth=2, label='Water Level')
    axes[0].axhline(setpoint, color='r', linestyle='--', linewidth=1.5, label=f'Setpoint ({setpoint}m)')
    axes[0].axhline(setpoint + 0.1, color='g', linestyle=':', linewidth=1, alpha=0.7, label='Tolerance (±0.1m)')
    axes[0].axhline(setpoint - 0.1, color='g', linestyle=':', linewidth=1, alpha=0.7)
    axes[0].fill_between(t_history, setpoint-0.1, setpoint+0.1, alpha=0.1, color='green')
    
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Case 2: Industrial Cooling Tower with Proportional Control', 
                     fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([0, duration])
    
    # 子图2：控制信号
    axes[1].plot(t_history, u_history, 'g-', linewidth=2, label='Control Signal')
    axes[1].axhline(u_mean, color='orange', linestyle=':', linewidth=1.5, 
                   label=f'Mean ({u_mean:.3f})')
    axes[1].set_ylabel('Control Signal (0-1)', fontsize=12)
    axes[1].set_title('Control Signal (Pump Speed)', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([0, duration])
    axes[1].set_ylim([-0.1, 1.1])
    
    # 子图3：误差变化
    axes[2].plot(t_history, error_history, 'r-', linewidth=2, label='Tracking Error')
    axes[2].axhline(0, color='k', linestyle='-', linewidth=1, alpha=0.5)
    axes[2].axhline(steady_state_error, color='orange', linestyle=':', 
                   linewidth=1.5, label=f'Steady-state Error ({steady_state_error:.4f}m)')
    axes[2].set_xlabel('Time (minutes)', fontsize=12)
    axes[2].set_ylabel('Error (m)', fontsize=12)
    axes[2].set_title('Tracking Error (Setpoint - Actual)', fontsize=12, fontweight='bold')
    axes[2].legend(loc='best', fontsize=10)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim([0, duration])
    
    plt.tight_layout()
    plt.savefig('case02_proportional_control.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case02_proportional_control.png")
    plt.show()


def compare_different_kp():
    """对比不同Kp值的影响"""
    
    print(f"\n\n{'='*70}")
    print("实验：不同Kp值对控制性能的影响")
    print("=" * 70)
    
    Kp_values = [0.5, 1.0, 2.0, 4.0, 8.0]
    setpoint = 3.0
    duration = 40
    dt = 0.1
    n_steps = int(duration / dt)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    results = []
    
    for Kp in Kp_values:
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=2.0)
        controller = ProportionalController(Kp=Kp, setpoint=setpoint)
        
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
            'steady_error': steady_state_error
        })
        
        # 绘图
        axes[0].plot(t, h, linewidth=2, label=f'Kp={Kp}', alpha=0.8)
        axes[1].plot(t, u, linewidth=2, label=f'Kp={Kp}', alpha=0.8)
    
    # 设置图表
    axes[0].axhline(setpoint, color='k', linestyle='--', linewidth=1.5, label='Setpoint')
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Effect of Proportional Gain Kp on Water Level', 
                     fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_xlabel('Time (minutes)', fontsize=12)
    axes[1].set_ylabel('Control Signal', fontsize=12)
    axes[1].set_title('Control Signal for Different Kp', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([-0.1, 1.1])
    
    plt.tight_layout()
    plt.savefig('case02_kp_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case02_kp_comparison.png")
    plt.show()
    
    # 打印对比表
    print(f"\n{'='*70}")
    print("不同Kp值的性能对比")
    print("=" * 70)
    print(f"{'Kp':<10} | {'上升时间(min)':<15} | {'超调量(%)':<15} | {'稳态误差(m)':<15}")
    print("-" * 70)
    for r in results:
        rise_str = f"{r['rise_time']:.2f}" if not np.isnan(r['rise_time']) else "N/A"
        print(f"{r['Kp']:<10.1f} | {rise_str:<15} | {r['overshoot']:<15.2f} | {r['steady_error']:<15.4f}")
    
    print(f"\n[观察与结论]")
    print(f"  1. Kp越大，响应越快（上升时间越短）")
    print(f"  2. Kp越大，稳态误差越小")
    print(f"  3. Kp过大可能导致振荡或超调")
    print(f"  4. 需要在快速性和稳定性之间权衡")


if __name__ == "__main__":
    # 运行比例控制演示
    demo_proportional_control()
    
    # 运行Kp对比实验
    compare_different_kp()
    
    print(f"\n{'='*70}")
    print("案例2演示完成！")
    print("=" * 70)
    print("\n关键要点:")
    print("1. 比例控制原理：u = Kp × e")
    print("2. 优点：响应快速，实现简单，控制平滑")
    print("3. 缺点：存在稳态误差")
    print("4. Kp选择：需要在快速性和稳定性之间权衡")
    print("\n下一步：学习PI控制消除稳态误差（案例3）")
