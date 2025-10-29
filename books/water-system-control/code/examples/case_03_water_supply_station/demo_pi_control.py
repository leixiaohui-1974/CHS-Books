"""
案例3：供水泵站无静差控制 - PI控制演示

教学目标：
1. 理解PI控制的原理
2. 认识积分作用的意义（消除稳态误差）
3. 学习抗积分饱和技术
4. 掌握PI参数整定方法

适用对象：完成案例1-2的学生
前置知识：开关控制、比例控制
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.models.water_tank.single_tank import SingleTank, calculate_step_response_metrics
from src.control.basic_controllers import ProportionalController, PIController

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def demo_pi_control():
    """演示PI控制"""
    
    print("=" * 70)
    print("案例3：供水泵站无静差控制")
    print("控制方法：PI控制（Proportional-Integral Control）")
    print("=" * 70)
    
    # 1. 场景说明
    print("\n[背景]")
    print("城市供水泵站需要保持恒定供水压力：")
    print("  - 压力由高位水箱水位决定")
    print("  - 用水需求实时变化（早晚高峰）")
    print("  - 比例控制存在稳态误差，无法满足要求")
    print("  - 需要PI控制实现无静差跟踪")
    
    # 2. 创建系统
    tank = SingleTank(A=2.0, R=2.0, K=1.0)
    tank.reset(h0=2.5)  # 初始水位2.5米
    
    print(f"\n[系统参数]")
    print(f"  传递函数: {tank.get_transfer_function()['description']}")
    print(f"  时间常数 τ: {tank.tau} 分钟")
    print(f"  稳态增益 K: {tank.steady_state_gain}")
    
    # 3. 创建PI控制器
    Kp = 1.5  # 比例增益
    Ki = 0.3  # 积分增益
    setpoint = 3.0  # 目标水位
    dt = 0.1
    controller = PIController(Kp=Kp, Ki=Ki, setpoint=setpoint, dt=dt)
    
    print(f"\n[控制器参数]")
    print(f"  控制类型: PI控制")
    print(f"  比例增益 Kp: {Kp}")
    print(f"  积分增益 Ki: {Ki}")
    print(f"  目标水位: {setpoint} m")
    print(f"  控制律: u = Kp×e + Ki×∫e dt")
    
    # 4. 运行仿真
    duration = 60  # 仿真60分钟
    n_steps = int(duration / dt)
    
    t_history = np.zeros(n_steps)
    h_history = np.zeros(n_steps)
    u_history = np.zeros(n_steps)
    error_history = np.zeros(n_steps)
    integral_history = np.zeros(n_steps)
    
    print(f"\n[仿真运行] 时长={duration}分钟")
    
    for i in range(n_steps):
        t_history[i] = tank.t
        h_history[i] = tank.h
        error_history[i] = setpoint - tank.h
        integral_history[i] = controller.integral
        
        # 控制器输出
        u_history[i] = controller.control(tank.h)
        
        # 系统更新
        tank.step(u_history[i], dt)
    
    # 5. 性能分析
    print(f"\n{'='*70}")
    print("控制性能分析")
    print("=" * 70)
    
    # 水位统计
    h_final = h_history[-1]
    steady_state_error = abs(setpoint - h_final)
    
    # 稳态部分统计（后30分钟）
    steady_idx = int(n_steps / 2)
    h_steady_mean = np.mean(h_history[steady_idx:])
    h_steady_std = np.std(h_history[steady_idx:])
    
    print(f"\n[水位性能]")
    print(f"  目标水位: {setpoint:.3f} m")
    print(f"  最终水位: {h_final:.3f} m")
    print(f"  稳态平均: {h_steady_mean:.3f} m")
    print(f"  稳态标准差: {h_steady_std:.4f} m")
    print(f"  稳态误差: {steady_state_error:.4f} m ({steady_state_error/setpoint*100:.2f}%)")
    
    # 阶跃响应指标
    metrics = calculate_step_response_metrics(t_history, h_history, setpoint, dt)
    
    print(f"\n[动态性能]")
    if not np.isnan(metrics['rise_time']):
        print(f"  上升时间: {metrics['rise_time']:.2f} 分钟")
    if not np.isnan(metrics['settling_time']):
        print(f"  调节时间: {metrics['settling_time']:.2f} 分钟")
    else:
        print(f"  调节时间: <1分钟 或 >60分钟")
    print(f"  超调量: {metrics['overshoot']:.2f}%")
    print(f"  峰值: {metrics['peak_value']:.3f} m")
    
    # 积分项分析
    print(f"\n[积分项分析]")
    print(f"  最终积分值: {controller.integral:.4f}")
    print(f"  积分饱和次数: {np.sum(np.abs(np.diff(integral_history)) < 1e-6)} 次")
    print(f"  → 积分项累积误差，直到稳态误差≈0")
    
    # 6. 绘图
    fig, axes = plt.subplots(4, 1, figsize=(12, 12))
    
    # 子图1：水位变化
    axes[0].plot(t_history, h_history, 'b-', linewidth=2, label='Water Level')
    axes[0].axhline(setpoint, color='r', linestyle='--', linewidth=1.5, 
                    label=f'Setpoint ({setpoint}m)')
    axes[0].fill_between(t_history, setpoint-0.05, setpoint+0.05, 
                         alpha=0.2, color='green', label='Tolerance (±0.05m)')
    
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Case 3: Water Supply Station with PI Control', 
                     fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([0, duration])
    
    # 子图2：控制信号
    axes[1].plot(t_history, u_history, 'g-', linewidth=2, label='Control Signal')
    axes[1].axhline(np.mean(u_history[steady_idx:]), color='orange', 
                   linestyle=':', linewidth=1.5, label='Steady Mean')
    axes[1].set_ylabel('Control Signal (0-1)', fontsize=12)
    axes[1].set_title('Control Signal (Pump Speed)', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([0, duration])
    axes[1].set_ylim([-0.1, 1.1])
    
    # 子图3：误差变化
    axes[2].plot(t_history, error_history, 'r-', linewidth=2, label='Error')
    axes[2].axhline(0, color='k', linestyle='-', linewidth=1)
    axes[2].set_ylabel('Error (m)', fontsize=12)
    axes[2].set_title('Tracking Error', fontsize=12, fontweight='bold')
    axes[2].legend(loc='best', fontsize=10)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim([0, duration])
    
    # 子图4：积分项变化
    axes[3].plot(t_history, integral_history, 'm-', linewidth=2, label='Integral Term')
    axes[3].set_xlabel('Time (minutes)', fontsize=12)
    axes[3].set_ylabel('Integral Value', fontsize=12)
    axes[3].set_title('Integral Term Evolution', fontsize=12, fontweight='bold')
    axes[3].legend(loc='best', fontsize=10)
    axes[3].grid(True, alpha=0.3)
    axes[3].set_xlim([0, duration])
    
    plt.tight_layout()
    plt.savefig('case03_pi_control.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case03_pi_control.png")
    plt.show()


def compare_p_vs_pi():
    """对比P控制和PI控制"""
    
    print(f"\n\n{'='*70}")
    print("对比实验：P控制 vs PI控制")
    print("=" * 70)
    
    setpoint = 3.0
    duration = 60
    dt = 0.1
    n_steps = int(duration / dt)
    
    # P控制
    tank_p = SingleTank(A=2.0, R=2.0, K=1.0)
    tank_p.reset(h0=2.5)
    controller_p = ProportionalController(Kp=1.5, setpoint=setpoint)
    
    t_p = np.zeros(n_steps)
    h_p = np.zeros(n_steps)
    u_p = np.zeros(n_steps)
    
    for i in range(n_steps):
        t_p[i] = tank_p.t
        h_p[i] = tank_p.h
        u_p[i] = controller_p.control(tank_p.h)
        tank_p.step(u_p[i], dt)
    
    # PI控制
    tank_pi = SingleTank(A=2.0, R=2.0, K=1.0)
    tank_pi.reset(h0=2.5)
    controller_pi = PIController(Kp=1.5, Ki=0.3, setpoint=setpoint, dt=dt)
    
    t_pi = np.zeros(n_steps)
    h_pi = np.zeros(n_steps)
    u_pi = np.zeros(n_steps)
    
    for i in range(n_steps):
        t_pi[i] = tank_pi.t
        h_pi[i] = tank_pi.h
        u_pi[i] = controller_pi.control(tank_pi.h)
        tank_pi.step(u_pi[i], dt)
    
    # 计算性能指标
    error_p = abs(setpoint - h_p[-1])
    error_pi = abs(setpoint - h_pi[-1])
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 水位对比
    axes[0].plot(t_p, h_p, 'b-', linewidth=2, label='P Control', alpha=0.8)
    axes[0].plot(t_pi, h_pi, 'r-', linewidth=2, label='PI Control', alpha=0.8)
    axes[0].axhline(setpoint, color='k', linestyle='--', linewidth=1.5, label='Setpoint')
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Performance Comparison: P vs PI Control', 
                     fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 控制信号对比
    axes[1].plot(t_p, u_p, 'b-', linewidth=2, label='P Control', alpha=0.8)
    axes[1].plot(t_pi, u_pi, 'r-', linewidth=2, label='PI Control', alpha=0.8)
    axes[1].set_xlabel('Time (minutes)', fontsize=12)
    axes[1].set_ylabel('Control Signal', fontsize=12)
    axes[1].set_title('Control Signal Comparison', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([-0.1, 1.1])
    
    plt.tight_layout()
    plt.savefig('case03_p_vs_pi.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case03_p_vs_pi.png")
    plt.show()
    
    # 打印对比结果
    print(f"\n{'='*70}")
    print("性能对比结果")
    print("=" * 70)
    print(f"{'指标':<25} | {'P控制':<20} | {'PI控制':<20}")
    print("-" * 70)
    print(f"{'最终水位 (m)':<25} | {h_p[-1]:<20.4f} | {h_pi[-1]:<20.4f}")
    print(f"{'稳态误差 (m)':<25} | {error_p:<20.4f} | {error_pi:<20.4f}")
    print(f"{'稳态误差 (%)':<25} | {error_p/setpoint*100:<20.2f} | {error_pi/setpoint*100:<20.2f}")
    
    # 计算改善百分比
    improvement = (error_p - error_pi) / error_p * 100
    print(f"\n误差改善: {improvement:.1f}%")
    
    print(f"\n[对比总结]")
    print(f"  P控制:")
    print(f"    ✓ 实现简单")
    print(f"    ✗ 存在稳态误差 ({error_p:.4f}m)")
    print(f"  ")
    print(f"  PI控制:")
    print(f"    ✓ 消除稳态误差 ({error_pi:.4f}m ≈ 0)")
    print(f"    ✓ 适应负载变化")
    print(f"    ⚠  需要调整Ki避免积分饱和")


if __name__ == "__main__":
    # 运行PI控制演示
    demo_pi_control()
    
    # 运行对比实验
    compare_p_vs_pi()
    
    print(f"\n{'='*70}")
    print("案例3演示完成！")
    print("=" * 70)
    print("\n关键要点:")
    print("1. PI控制原理：u = Kp×e + Ki×∫e dt")
    print("2. 积分作用：累积历史误差，消除稳态误差")
    print("3. 优点：无静差、鲁棒性好")
    print("4. 注意：需要抗积分饱和保护")
    print("\n下一步：学习PID控制和高级整定方法（案例4）")
