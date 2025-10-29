"""
案例4：PID控制与Ziegler-Nichols整定 - 完整演示

教学目标：
1. 理解PID三个参数的作用
2. 掌握Ziegler-Nichols整定方法
3. 对比P、PI、PID的性能
4. 分析微分项的作用

适用对象：完成案例1-3的学生
前置知识：开关控制、P控制、PI控制
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.models.water_tank.single_tank import SingleTank, calculate_step_response_metrics
from src.control.basic_controllers import (ProportionalController, PIController, 
                                           PIDController, ziegler_nichols_first_method)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def demo_pid_components():
    """演示PID各组成部分的作用"""
    
    print("=" * 70)
    print("案例4：PID控制与参数整定")
    print("第一部分：PID各组成部分的作用")
    print("=" * 70)
    
    # 1. 场景说明
    print("\n[背景]")
    print("某精密温控水浴系统需要高精度快速响应：")
    print("  - 要求：快速到达设定值")
    print("  - 精度：±0.01米（±0.33%）")
    print("  - 抑制：超调量<5%")
    print("  - PI控制响应偏慢，需要PID控制")
    
    # 创建系统
    tank = SingleTank(A=2.0, R=2.0, K=1.0)
    setpoint = 3.0
    duration = 30
    dt = 0.1
    n_steps = int(duration / dt)
    
    # 测试不同控制器
    controllers = {
        'P': ProportionalController(Kp=2.0, setpoint=setpoint),
        'PI': PIController(Kp=1.5, Ki=0.3, setpoint=setpoint, dt=dt),
        'PID': PIDController(Kp=2.0, Ki=0.5, Kd=0.5, setpoint=setpoint, dt=dt)
    }
    
    results = {}
    
    print(f"\n[控制器参数]")
    for name, controller in controllers.items():
        if name == 'P':
            print(f"  {name}:   Kp={controller.Kp}")
        elif name == 'PI':
            print(f"  {name}:  Kp={controller.Kp}, Ki={controller.Ki}")
        elif name == 'PID':
            print(f"  {name}: Kp={controller.Kp}, Ki={controller.Ki}, Kd={controller.Kd}")
    
    print(f"\n[仿真运行]")
    for name, controller in controllers.items():
        tank.reset(h0=2.0)
        
        t = np.zeros(n_steps)
        h = np.zeros(n_steps)
        u = np.zeros(n_steps)
        
        for i in range(n_steps):
            t[i] = tank.t
            h[i] = tank.h
            u[i] = controller.control(tank.h)
            tank.step(u[i], dt)
        
        results[name] = {'t': t, 'h': h, 'u': u}
        
        # 计算性能指标
        metrics = calculate_step_response_metrics(t, h, setpoint, dt)
        steady_error = abs(setpoint - h[-1])
        
        print(f"\n  {name}控制器:")
        if not np.isnan(metrics['rise_time']):
            print(f"    上升时间: {metrics['rise_time']:.2f}分钟")
        print(f"    超调量: {metrics['overshoot']:.2f}%")
        print(f"    稳态误差: {steady_error:.4f}m")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    colors = {'P': 'blue', 'PI': 'green', 'PID': 'red'}
    
    # 子图1：水位对比
    for name, data in results.items():
        axes[0].plot(data['t'], data['h'], color=colors[name], 
                    linewidth=2, label=f'{name} Control', alpha=0.8)
    
    axes[0].axhline(setpoint, color='k', linestyle='--', linewidth=1.5, label='Setpoint')
    axes[0].fill_between([0, duration], setpoint-0.01, setpoint+0.01, 
                         alpha=0.2, color='green', label='Target Band (±0.01m)')
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Case 4: PID Control Performance Comparison', 
                     fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([0, duration])
    
    # 子图2：控制信号对比
    for name, data in results.items():
        axes[1].plot(data['t'], data['u'], color=colors[name], 
                    linewidth=2, label=f'{name} Control', alpha=0.8)
    
    axes[1].set_xlabel('Time (minutes)', fontsize=12)
    axes[1].set_ylabel('Control Signal', fontsize=12)
    axes[1].set_title('Control Signal Comparison', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([0, duration])
    axes[1].set_ylim([-0.1, 1.1])
    
    plt.tight_layout()
    plt.savefig('case04_pid_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case04_pid_comparison.png")
    plt.show()


def demo_ziegler_nichols_tuning():
    """演示Ziegler-Nichols整定方法"""
    
    print(f"\n\n{'='*70}")
    print("第二部分：Ziegler-Nichols参数整定")
    print("=" * 70)
    
    # 系统参数
    tank = SingleTank(A=2.0, R=2.0, K=1.0)
    
    print(f"\n[系统识别]")
    print(f"  传递函数: {tank.get_transfer_function()['description']}")
    print(f"  时间常数 τ: {tank.tau} 分钟")
    print(f"  稳态增益 K: {tank.steady_state_gain}")
    
    # 估算滞后时间（对于一阶系统，可以近似为0.1τ）
    L = 0.5  # 假设滞后时间
    T = tank.tau
    
    print(f"\n[过程参数]")
    print(f"  时间常数 T: {T} 分钟")
    print(f"  滞后时间 L: {L} 分钟 (估算)")
    print(f"  T/L比值: {T/L:.2f}")
    
    # Ziegler-Nichols整定
    print(f"\n[Ziegler-Nichols整定结果]")
    
    tuning_results = {}
    for control_type in ['P', 'PI', 'PID']:
        params = ziegler_nichols_first_method(L, T, control_type)
        tuning_results[control_type] = params
        
        print(f"\n  {control_type}控制器:")
        print(f"    Kp = {params['Kp']:.3f}")
        if params['Ki'] > 0:
            print(f"    Ki = {params['Ki']:.3f}")
        if params['Kd'] > 0:
            print(f"    Kd = {params['Kd']:.3f}")
    
    # 使用整定参数进行仿真
    print(f"\n[使用整定参数仿真]")
    
    setpoint = 3.0
    duration = 40
    dt = 0.1
    n_steps = int(duration / dt)
    
    controllers = {
        'P-ZN': ProportionalController(
            Kp=tuning_results['P']['Kp'], setpoint=setpoint),
        'PI-ZN': PIController(
            Kp=tuning_results['PI']['Kp'], 
            Ki=tuning_results['PI']['Ki'], 
            setpoint=setpoint, dt=dt),
        'PID-ZN': PIDController(
            Kp=tuning_results['PID']['Kp'],
            Ki=tuning_results['PID']['Ki'],
            Kd=tuning_results['PID']['Kd'],
            setpoint=setpoint, dt=dt)
    }
    
    results_zn = {}
    
    for name, controller in controllers.items():
        tank.reset(h0=2.0)
        
        t = np.zeros(n_steps)
        h = np.zeros(n_steps)
        u = np.zeros(n_steps)
        
        for i in range(n_steps):
            t[i] = tank.t
            h[i] = tank.h
            u[i] = controller.control(tank.h)
            tank.step(u[i], dt)
        
        results_zn[name] = {'t': t, 'h': h, 'u': u}
        
        # 性能指标
        metrics = calculate_step_response_metrics(t, h, setpoint, dt)
        steady_error = abs(setpoint - h[-1])
        
        print(f"\n  {name}:")
        if not np.isnan(metrics['rise_time']):
            print(f"    上升时间: {metrics['rise_time']:.2f}分钟")
        if not np.isnan(metrics['settling_time']):
            print(f"    调节时间: {metrics['settling_time']:.2f}分钟")
        print(f"    超调量: {metrics['overshoot']:.2f}%")
        print(f"    稳态误差: {steady_error:.4f}m")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    colors = {'P-ZN': 'blue', 'PI-ZN': 'green', 'PID-ZN': 'red'}
    
    for name, data in results_zn.items():
        axes[0].plot(data['t'], data['h'], color=colors[name], 
                    linewidth=2, label=name, alpha=0.8)
    
    axes[0].axhline(setpoint, color='k', linestyle='--', linewidth=1.5, label='Setpoint')
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Ziegler-Nichols Tuned Controllers', 
                     fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([0, duration])
    
    for name, data in results_zn.items():
        axes[1].plot(data['t'], data['u'], color=colors[name], 
                    linewidth=2, label=name, alpha=0.8)
    
    axes[1].set_xlabel('Time (minutes)', fontsize=12)
    axes[1].set_ylabel('Control Signal', fontsize=12)
    axes[1].set_title('Control Signals (ZN Tuned)', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([0, duration])
    
    plt.tight_layout()
    plt.savefig('case04_zn_tuning.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case04_zn_tuning.png")
    plt.show()


def demo_pid_components_analysis():
    """详细分析PID各分量的贡献"""
    
    print(f"\n\n{'='*70}")
    print("第三部分：PID各分量详细分析")
    print("=" * 70)
    
    tank = SingleTank(A=2.0, R=2.0, K=1.0)
    tank.reset(h0=2.0)
    
    # 创建PID控制器
    pid = PIDController(Kp=2.0, Ki=0.5, Kd=0.5, setpoint=3.0, dt=0.1)
    
    duration = 20
    dt = 0.1
    n_steps = int(duration / dt)
    
    t = np.zeros(n_steps)
    h = np.zeros(n_steps)
    u = np.zeros(n_steps)
    P_terms = np.zeros(n_steps)
    I_terms = np.zeros(n_steps)
    D_terms = np.zeros(n_steps)
    
    print(f"\n[PID分量演化]")
    print(f"  时间 | 水位  | 误差  | P项   | I项   | D项   | 总输出")
    print("-" * 70)
    
    for i in range(n_steps):
        t[i] = tank.t
        h[i] = tank.h
        
        # 获取PID各分量
        components = pid.get_components(tank.h)
        P_terms[i] = components['P']
        I_terms[i] = components['I']
        D_terms[i] = components['D']
        
        # 控制输出
        u[i] = pid.control(tank.h)
        
        # 打印前10步
        if i < 10:
            print(f"  {t[i]:5.1f} | {h[i]:5.2f} | {components['error']:+5.2f} | "
                  f"{P_terms[i]:+5.2f} | {I_terms[i]:+5.2f} | {D_terms[i]:+5.2f} | {u[i]:6.3f}")
        
        tank.step(u[i], dt)
    
    # 绘图
    fig, axes = plt.subplots(4, 1, figsize=(12, 12))
    
    # 子图1：水位
    axes[0].plot(t, h, 'b-', linewidth=2, label='Water Level')
    axes[0].axhline(3.0, color='r', linestyle='--', label='Setpoint')
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('PID Control Component Analysis', fontsize=14, fontweight='bold')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)
    
    # 子图2：P项
    axes[1].plot(t, P_terms, 'b-', linewidth=2, label='P Term')
    axes[1].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
    axes[1].set_ylabel('P Component', fontsize=12)
    axes[1].legend(loc='best')
    axes[1].grid(True, alpha=0.3)
    
    # 子图3：I项
    axes[2].plot(t, I_terms, 'g-', linewidth=2, label='I Term')
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
    axes[2].set_ylabel('I Component', fontsize=12)
    axes[2].legend(loc='best')
    axes[2].grid(True, alpha=0.3)
    
    # 子图4：D项
    axes[3].plot(t, D_terms, 'r-', linewidth=2, label='D Term')
    axes[3].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
    axes[3].set_xlabel('Time (minutes)', fontsize=12)
    axes[3].set_ylabel('D Component', fontsize=12)
    axes[3].legend(loc='best')
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case04_pid_components.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case04_pid_components.png")
    plt.show()
    
    # 统计分析
    print(f"\n[分量统计分析]")
    print(f"  P项: 平均={np.mean(P_terms[50:]):.3f}, 标准差={np.std(P_terms[50:]):.3f}")
    print(f"  I项: 平均={np.mean(I_terms[50:]):.3f}, 标准差={np.std(I_terms[50:]):.3f}")
    print(f"  D项: 平均={np.mean(D_terms[50:]):.3f}, 标准差={np.std(D_terms[50:]):.3f}")
    
    print(f"\n[分量作用总结]")
    print(f"  P项: 主要贡献，快速响应误差")
    print(f"  I项: 累积误差，消除稳态偏差")
    print(f"  D项: 预测趋势，抑制超调和振荡")


if __name__ == "__main__":
    # 运行演示1：对比P/PI/PID
    demo_pid_components()
    
    # 运行演示2：Ziegler-Nichols整定
    demo_ziegler_nichols_tuning()
    
    # 运行演示3：PID分量分析
    demo_pid_components_analysis()
    
    print(f"\n{'='*70}")
    print("案例4演示完成！")
    print("=" * 70)
    print("\n关键要点:")
    print("1. PID = P + I + D，三项协同工作")
    print("2. P项：快速响应，但有稳态误差")
    print("3. I项：消除稳态误差，但可能振荡")
    print("4. D项：预测未来，抑制超调")
    print("5. Ziegler-Nichols：经典的参数整定方法")
    print("\n下一步：学习状态空间控制方法（案例5）")
