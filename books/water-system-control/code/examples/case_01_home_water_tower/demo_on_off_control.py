"""
案例1：家庭水塔自动供水系统 - 开关控制演示

教学目标：
1. 理解开关控制（On-Off Control）的原理
2. 观察滞环（Hysteresis）的作用
3. 分析控制性能（频繁启停、水位波动）
4. 与比例控制对比

适用对象：零基础学生
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.models.water_tank.single_tank import SingleTank
from src.control.basic_controllers import OnOffController, ProportionalController

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def demo_on_off_control():
    """演示开关控制"""
    
    print("=" * 70)
    print("案例1：家庭水塔自动供水系统")
    print("控制方法：开关控制（On-Off Control）")
    print("=" * 70)
    
    # 1. 创建水箱系统
    tank = SingleTank(A=2.0, R=2.0, K=1.0)
    tank.reset(h0=2.0)  # 初始水位2米
    
    print(f"\n水箱参数:")
    print(f"  横截面积: {tank.A} m²")
    print(f"  阻力系数: {tank.R} min/m²")
    print(f"  泵增益: {tank.K} m³/min")
    print(f"  时间常数: {tank.tau} 分钟")
    
    # 2. 创建开关控制器
    controller = OnOffController(
        low_threshold=2.5,   # 下限：2.5米
        high_threshold=3.5,  # 上限：3.5米
        output_on=1.0,       # 开启时全速
        output_off=0.0       # 关闭时停止
    )
    
    print(f"\n控制器参数:")
    print(f"  下限阈值: {controller.low_threshold} m")
    print(f"  上限阈值: {controller.high_threshold} m")
    print(f"  滞环宽度: {controller.high_threshold - controller.low_threshold} m")
    
    # 3. 运行仿真
    duration = 120  # 仿真2小时
    dt = 0.1  # 每步0.1分钟=6秒
    n_steps = int(duration / dt)
    
    # 记录数据
    t_history = np.zeros(n_steps)
    h_history = np.zeros(n_steps)
    u_history = np.zeros(n_steps)
    pump_state = []  # 记录泵的状态变化
    
    print(f"\n开始仿真...")
    print(f"  仿真时长: {duration} 分钟")
    print(f"  时间步长: {dt} 分钟")
    
    switch_count = 0  # 开关次数
    last_state = controller.is_on
    
    for i in range(n_steps):
        t_history[i] = tank.t
        h_history[i] = tank.h
        
        # 控制器决策
        u_history[i] = controller.control(tank.h)
        
        # 检测开关动作
        if controller.is_on != last_state:
            switch_count += 1
            pump_state.append({
                'time': tank.t,
                'level': tank.h,
                'action': 'ON' if controller.is_on else 'OFF'
            })
            last_state = controller.is_on
        
        # 水箱更新
        tank.step(u_history[i], dt)
    
    print(f"仿真完成！")
    
    # 4. 分析结果
    print(f"\n{'='*70}")
    print(f"控制性能分析")
    print(f"{'='*70}")
    
    # 水位统计
    h_mean = np.mean(h_history)
    h_std = np.std(h_history)
    h_min = np.min(h_history)
    h_max = np.max(h_history)
    
    print(f"\n水位统计:")
    print(f"  平均值: {h_mean:.3f} m")
    print(f"  标准差: {h_std:.3f} m")
    print(f"  最小值: {h_min:.3f} m")
    print(f"  最大值: {h_max:.3f} m")
    print(f"  波动范围: {h_max - h_min:.3f} m")
    
    # 开关统计
    print(f"\n泵启停统计:")
    print(f"  总开关次数: {switch_count}")
    print(f"  平均每小时开关: {switch_count / (duration/60):.1f} 次")
    
    if len(pump_state) > 0:
        print(f"\n前5次开关动作:")
        for i, event in enumerate(pump_state[:5]):
            print(f"  {i+1}. t={event['time']:.1f}min, h={event['level']:.2f}m → {event['action']}")
    
    # 能耗统计
    energy = np.sum(u_history) * dt  # 简化的能耗计算
    print(f"\n能耗:")
    print(f"  总能耗: {energy:.2f} (m³)")
    print(f"  平均功率: {energy/duration:.3f} (m³/min)")
    
    # 5. 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 子图1：水位变化
    axes[0].plot(t_history, h_history, 'b-', linewidth=2, label='Water Level')
    axes[0].axhline(controller.low_threshold, color='r', linestyle='--', 
                    linewidth=1.5, label=f'Low Threshold ({controller.low_threshold}m)')
    axes[0].axhline(controller.high_threshold, color='r', linestyle='--', 
                    linewidth=1.5, label=f'High Threshold ({controller.high_threshold}m)')
    axes[0].fill_between(t_history, controller.low_threshold, controller.high_threshold, 
                         alpha=0.2, color='green', label='Dead Band')
    axes[0].axhline(h_mean, color='orange', linestyle=':', 
                    linewidth=1.5, label=f'Mean ({h_mean:.2f}m)')
    
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Case 1: Home Water Tower with On-Off Control', 
                     fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([0, duration])
    
    # 子图2：泵控制信号
    axes[1].plot(t_history, u_history, 'g-', linewidth=2, label='Pump Control')
    axes[1].fill_between(t_history, 0, u_history, alpha=0.3, color='g')
    axes[1].set_xlabel('Time (minutes)', fontsize=12)
    axes[1].set_ylabel('Control Signal (0=OFF, 1=ON)', fontsize=12)
    axes[1].set_title('Pump On/Off Status', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([0, duration])
    axes[1].set_ylim([-0.1, 1.1])
    
    plt.tight_layout()
    plt.savefig('case01_on_off_control.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存为: case01_on_off_control.png")
    plt.show()


def compare_with_proportional():
    """对比开关控制和比例控制"""
    
    print(f"\n\n{'='*70}")
    print("对比实验：开关控制 vs 比例控制")
    print("=" * 70)
    
    duration = 60
    dt = 0.1
    n_steps = int(duration / dt)
    
    # 两个相同的水箱
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
    
    # 统计对比
    print(f"\n性能对比:")
    print(f"{'指标':<20} | {'开关控制':<15} | {'比例控制':<15}")
    print("-" * 55)
    print(f"{'平均水位 (m)':<20} | {np.mean(h1):<15.3f} | {np.mean(h2):<15.3f}")
    print(f"{'标准差 (m)':<20} | {np.std(h1):<15.3f} | {np.std(h2):<15.3f}")
    print(f"{'最大偏差 (m)':<20} | {np.max(np.abs(h1-3.0)):<15.3f} | {np.max(np.abs(h2-3.0)):<15.3f}")
    print(f"{'总能耗 (m³)':<20} | {np.sum(u1)*dt:<15.2f} | {np.sum(u2)*dt:<15.2f}")
    
    # 开关次数
    switch1 = np.sum(np.abs(np.diff(u1)) > 0.5)
    switch2 = np.sum(np.abs(np.diff(u2)) > 0.01)  # 比例控制几乎连续变化
    print(f"{'显著变化次数':<20} | {switch1:<15d} | {switch2:<15d}")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 水位对比
    axes[0].plot(t, h1, 'b-', linewidth=2, label='On-Off Control', alpha=0.7)
    axes[0].plot(t, h2, 'r-', linewidth=2, label='Proportional Control', alpha=0.7)
    axes[0].axhline(3.0, color='k', linestyle='--', linewidth=1, label='Setpoint (3.0m)')
    axes[0].set_ylabel('Water Level (m)', fontsize=12)
    axes[0].set_title('Control Performance Comparison', fontsize=14, fontweight='bold')
    axes[0].legend(loc='best', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 控制信号对比
    axes[1].plot(t, u1, 'b-', linewidth=2, label='On-Off Control', alpha=0.7)
    axes[1].plot(t, u2, 'r-', linewidth=2, label='Proportional Control', alpha=0.7)
    axes[1].set_xlabel('Time (minutes)', fontsize=12)
    axes[1].set_ylabel('Control Signal', fontsize=12)
    axes[1].set_title('Control Signal Comparison', fontsize=12, fontweight='bold')
    axes[1].legend(loc='best', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case01_control_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n对比图已保存为: case01_control_comparison.png")
    plt.show()


if __name__ == "__main__":
    # 运行开关控制演示
    demo_on_off_control()
    
    # 运行对比实验
    compare_with_proportional()
    
    print(f"\n{'='*70}")
    print("案例1演示完成！")
    print("=" * 70)
    print("\n关键要点:")
    print("1. 开关控制简单但水位会在上下限之间波动")
    print("2. 滞环（死区）可以减少开关次数")
    print("3. 比例控制可以实现更平稳的控制")
    print("4. 需要根据应用场景选择合适的控制方法")
    print("\n下一步：学习比例控制和PI控制（案例2-3）")
