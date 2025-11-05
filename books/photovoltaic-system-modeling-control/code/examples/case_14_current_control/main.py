"""
案例14: 电流控制
演示PI、PR和dq坐标系电流控制器

实验内容:
1. PI控制器的设计与调试
2. PR控制器的谐振特性
3. PI vs PR性能对比
4. dq坐标变换与解耦控制
5. 参数整定方法

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# 添加models路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.inverter_control import (
    InverterParameters, PIController, PRController, DQCurrentController
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_pi_controller():
    """
    实验1: PI控制器基础
    展示PI控制器的阶跃响应和稳态性能
    """
    print("=" * 60)
    print("实验1: PI控制器基础")
    print("=" * 60)
    
    # 系统参数
    L = 5e-3  # 5mH电感
    R = 0.1   # 0.1Ω电阻
    
    # PI参数 (根据经验公式)
    tau = L / R  # 时间常数
    omega_c = 1000  # 期望带宽 (rad/s)
    
    Kp = L * omega_c
    Ki = R * omega_c
    
    print(f"系统参数:")
    print(f"  L = {L*1000:.1f} mH")
    print(f"  R = {R:.1f} Ω")
    print(f"  τ = L/R = {tau*1000:.2f} ms")
    print(f"\nPI参数:")
    print(f"  Kp = {Kp:.2f}")
    print(f"  Ki = {Ki:.2f}")
    print(f"  期望带宽 = {omega_c} rad/s ({omega_c/(2*np.pi):.1f} Hz)")
    
    # 创建PI控制器
    pi = PIController(Kp, Ki, v_limit=400.0)
    
    # 仿真参数
    dt = 1e-5  # 10μs采样
    t_total = 0.05  # 50ms
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    # 参考电流 (阶跃)
    i_ref = np.zeros(N)
    i_ref[int(0.01/dt):] = 10.0  # 10ms后阶跃到10A
    
    # 初始化状态
    i_actual = 0.0
    
    # 记录数组
    i_measured = np.zeros(N)
    v_control = np.zeros(N)
    error = np.zeros(N)
    
    # 仿真循环
    for i in range(N):
        # PI控制
        v_out = pi.update(i_ref[i], i_actual, dt)
        
        # 一阶RL电路动态 (简化模型)
        di_dt = (v_out - R * i_actual) / L
        i_actual += di_dt * dt
        
        # 记录
        i_measured[i] = i_actual
        v_control[i] = v_out
        error[i] = i_ref[i] - i_actual
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    time_ms = time * 1000
    
    # 子图1: 电流响应
    axes[0].plot(time_ms, i_ref, 'r--', linewidth=2, label='参考电流')
    axes[0].plot(time_ms, i_measured, 'b-', linewidth=1.5, label='实际电流')
    axes[0].set_ylabel('电流 (A)', fontsize=11)
    axes[0].set_title('PI控制器阶跃响应', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_xlim([0, 50])
    
    # 子图2: 控制输出
    axes[1].plot(time_ms, v_control, 'g-', linewidth=1.5)
    axes[1].set_ylabel('控制电压 (V)', fontsize=11)
    axes[1].set_title('控制器输出', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(400, color='r', linestyle='--', linewidth=1, alpha=0.5, label='限幅')
    axes[1].axhline(-400, color='r', linestyle='--', linewidth=1, alpha=0.5)
    axes[1].legend(fontsize=9)
    
    # 子图3: 跟踪误差
    axes[2].plot(time_ms, error, 'r-', linewidth=1.5)
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('误差 (A)', fontsize=11)
    axes[2].set_title('跟踪误差', fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_14_exp1_pi_controller.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图1已保存: case_14_exp1_pi_controller.png")
    plt.show()
    
    # 计算性能指标
    step_idx = int(0.01/dt)
    steady_idx = int(0.03/dt)  # 稳态时刻
    
    # 上升时间 (10%-90%)
    i_final = 10.0
    idx_10 = np.where(i_measured[step_idx:] >= 0.1 * i_final)[0][0] + step_idx
    idx_90 = np.where(i_measured[step_idx:] >= 0.9 * i_final)[0][0] + step_idx
    rise_time = (idx_90 - idx_10) * dt
    
    # 超调量
    overshoot = (np.max(i_measured[step_idx:steady_idx]) - i_final) / i_final * 100
    
    # 稳态误差
    steady_error = np.mean(error[steady_idx:])
    
    print(f"\n性能指标:")
    print(f"  上升时间: {rise_time*1000:.2f} ms")
    print(f"  超调量: {overshoot:.2f} %")
    print(f"  稳态误差: {abs(steady_error):.4f} A")


def experiment_2_pr_controller():
    """
    实验2: PR控制器谐振特性
    展示PR控制器对50Hz正弦信号的跟踪能力
    """
    print("\n" + "=" * 60)
    print("实验2: PR控制器谐振特性")
    print("=" * 60)
    
    # 系统参数
    L = 5e-3
    R = 0.1
    f0 = 50.0  # 基波频率
    omega_0 = 2 * np.pi * f0
    
    # PR参数
    Kp = 5.0
    Kr = 1000.0
    Ts = 1e-4  # 100μs采样周期
    
    print(f"PR参数:")
    print(f"  Kp = {Kp}")
    print(f"  Kr = {Kr}")
    print(f"  f0 = {f0} Hz")
    print(f"  Ts = {Ts*1e6:.0f} μs")
    
    # 创建PR控制器
    pr = PRController(Kp, Kr, omega_0, Ts, v_limit=400.0)
    
    # 仿真
    t_total = 0.1  # 100ms (5个周期)
    time = np.arange(0, t_total, Ts)
    N = len(time)
    
    # 参考电流 (正弦波)
    i_ref = 10 * np.sin(omega_0 * time)
    
    # 初始化
    i_actual = 0.0
    i_measured = np.zeros(N)
    v_control = np.zeros(N)
    error = np.zeros(N)
    
    # 仿真循环
    for i in range(N):
        # PR控制
        v_out = pr.update(i_ref[i], i_actual, Ts)
        
        # RL电路
        di_dt = (v_out - R * i_actual) / L
        i_actual += di_dt * Ts
        
        # 记录
        i_measured[i] = i_actual
        v_control[i] = v_out
        error[i] = i_ref[i] - i_actual
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    time_ms = time * 1000
    
    # 子图1: 电流跟踪
    axes[0].plot(time_ms, i_ref, 'r--', linewidth=2, alpha=0.7, label='参考电流')
    axes[0].plot(time_ms, i_measured, 'b-', linewidth=1.5, label='实际电流')
    axes[0].set_ylabel('电流 (A)', fontsize=11)
    axes[0].set_title('PR控制器正弦跟踪', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    
    # 子图2: 控制电压
    axes[1].plot(time_ms, v_control, 'g-', linewidth=1)
    axes[1].set_ylabel('控制电压 (V)', fontsize=11)
    axes[1].set_title('控制器输出', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # 子图3: 跟踪误差 (放大显示稳态)
    axes[2].plot(time_ms, error, 'r-', linewidth=1.5)
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('误差 (A)', fontsize=11)
    axes[2].set_title('跟踪误差', fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_14_exp2_pr_controller.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图2已保存: case_14_exp2_pr_controller.png")
    plt.show()
    
    # 稳态性能 (最后2个周期)
    steady_idx = int(0.06 / Ts)
    steady_error = error[steady_idx:]
    steady_rmse = np.sqrt(np.mean(steady_error**2))
    steady_max_error = np.max(np.abs(steady_error))
    
    print(f"\n稳态性能:")
    print(f"  RMS误差: {steady_rmse:.4f} A")
    print(f"  最大误差: {steady_max_error:.4f} A")
    print(f"  误差百分比: {steady_rmse/10*100:.3f} %")


def experiment_3_pi_vs_pr():
    """
    实验3: PI vs PR性能对比
    在相同条件下对比两种控制器的性能
    """
    print("\n" + "=" * 60)
    print("实验3: PI vs PR性能对比")
    print("=" * 60)
    
    # 系统参数
    L = 5e-3
    R = 0.1
    f0 = 50.0
    omega_0 = 2 * np.pi * f0
    Ts = 1e-4
    
    # 创建两个控制器
    pi = PIController(Kp=5.0, Ki=500.0, v_limit=400.0, name="PI")
    pr = PRController(Kp=5.0, Kr=1000.0, omega_0=omega_0, Ts=Ts, v_limit=400.0, name="PR")
    
    # 仿真
    t_total = 0.1
    time = np.arange(0, t_total, Ts)
    N = len(time)
    
    # 参考电流
    i_ref = 10 * np.sin(omega_0 * time)
    
    # 仿真两个控制器
    results = {}
    
    for controller, name in [(pi, 'PI'), (pr, 'PR')]:
        controller.reset()
        i_actual = 0.0
        i_measured = np.zeros(N)
        error = np.zeros(N)
        
        for i in range(N):
            v_out = controller.update(i_ref[i], i_actual, Ts)
            di_dt = (v_out - R * i_actual) / L
            i_actual += di_dt * Ts
            
            i_measured[i] = i_actual
            error[i] = i_ref[i] - i_actual
        
        results[name] = {'i_measured': i_measured, 'error': error}
    
    # 绘图对比
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    time_ms = time * 1000
    
    # PI电流跟踪
    axes[0, 0].plot(time_ms, i_ref, 'r--', linewidth=2, alpha=0.6, label='参考')
    axes[0, 0].plot(time_ms, results['PI']['i_measured'], 'b-', linewidth=1.5, label='PI')
    axes[0, 0].set_ylabel('电流 (A)', fontsize=10)
    axes[0, 0].set_title('PI控制器 - 电流跟踪', fontsize=11, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend(fontsize=9)
    
    # PR电流跟踪
    axes[0, 1].plot(time_ms, i_ref, 'r--', linewidth=2, alpha=0.6, label='参考')
    axes[0, 1].plot(time_ms, results['PR']['i_measured'], 'g-', linewidth=1.5, label='PR')
    axes[0, 1].set_ylabel('电流 (A)', fontsize=10)
    axes[0, 1].set_title('PR控制器 - 电流跟踪', fontsize=11, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend(fontsize=9)
    
    # PI误差
    axes[1, 0].plot(time_ms, results['PI']['error'], 'b-', linewidth=1.5)
    axes[1, 0].set_xlabel('时间 (ms)', fontsize=10)
    axes[1, 0].set_ylabel('误差 (A)', fontsize=10)
    axes[1, 0].set_title('PI控制器 - 跟踪误差', fontsize=11, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    # PR误差
    axes[1, 1].plot(time_ms, results['PR']['error'], 'g-', linewidth=1.5)
    axes[1, 1].set_xlabel('时间 (ms)', fontsize=10)
    axes[1, 1].set_ylabel('误差 (A)', fontsize=10)
    axes[1, 1].set_title('PR控制器 - 跟踪误差', fontsize=11, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_14_exp3_pi_vs_pr.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图3已保存: case_14_exp3_pi_vs_pr.png")
    plt.show()
    
    # 性能对比
    steady_idx = int(0.06 / Ts)
    
    print(f"\n性能对比:")
    print(f"  {'指标':<15} {'PI':<15} {'PR':<15}")
    print(f"  {'-'*45}")
    
    for name in ['PI', 'PR']:
        error_steady = results[name]['error'][steady_idx:]
        rmse = np.sqrt(np.mean(error_steady**2))
        max_error = np.max(np.abs(error_steady))
        
        if name == 'PI':
            pi_rmse, pi_max = rmse, max_error
        else:
            pr_rmse, pr_max = rmse, max_error
    
    print(f"  {'RMS误差(A)':<15} {pi_rmse:<15.4f} {pr_rmse:<15.4f}")
    print(f"  {'最大误差(A)':<15} {pi_max:<15.4f} {pr_max:<15.4f}")
    print(f"  {'误差百分比':<15} {pi_rmse/10*100:<15.3f} {pr_rmse/10*100:<15.3f}")
    
    print(f"\n结论:")
    if pr_rmse < pi_rmse:
        improvement = (pi_rmse - pr_rmse) / pi_rmse * 100
        print(f"  PR控制器误差比PI减小 {improvement:.1f}%")
        print(f"  PR更适合交流电流控制")
    else:
        print(f"  在此参数下性能相当")


def experiment_4_dq_control():
    """
    实验4: dq坐标系电流控制
    展示Park变换和解耦控制
    """
    print("\n" + "=" * 60)
    print("实验4: dq坐标系电流控制")
    print("=" * 60)
    
    # 系统参数
    L = 5e-3
    R = 0.1
    f0 = 50.0
    omega = 2 * np.pi * f0
    Ts = 1e-4
    
    # dq控制器参数
    Kp = 5.0
    Ki = 500.0
    
    # 创建控制器
    dq_ctrl = DQCurrentController(Kp, Ki, L, omega, v_limit=400.0)
    
    print(f"dq控制器参数:")
    print(f"  Kp = {Kp}")
    print(f"  Ki = {Ki}")
    print(f"  L = {L*1000:.1f} mH")
    print(f"  ω = {omega:.1f} rad/s")
    
    # 仿真
    t_total = 0.1
    time = np.arange(0, t_total, Ts)
    N = len(time)
    
    # 参考电流 (dq坐标)
    i_d_ref = 10.0  # 恒定d轴电流
    i_q_ref = 0.0   # q轴电流为0
    
    # 初始化三相电流
    i_a, i_b, i_c = 0.0, 0.0, 0.0
    
    # 记录数组
    i_abc = np.zeros((N, 3))
    i_dq = np.zeros((N, 2))
    v_abc = np.zeros((N, 3))
    theta_arr = np.zeros(N)
    
    # 仿真循环
    for i in range(N):
        t = time[i]
        theta = omega * t  # 同步角度
        
        # dq控制器
        v_a, v_b, v_c = dq_ctrl.update(
            i_d_ref, i_q_ref,
            i_a, i_b, i_c,
            theta, Ts,
            enable_decoupling=True
        )
        
        # 三相RL电路 (简化)
        di_a = (v_a - R * i_a) / L * Ts
        di_b = (v_b - R * i_b) / L * Ts
        di_c = (v_c - R * i_c) / L * Ts
        
        i_a += di_a
        i_b += di_b
        i_c += di_c
        
        # 计算dq电流 (用于显示)
        i_d, i_q = dq_ctrl.park_transform(i_a, i_b, i_c, theta)
        
        # 记录
        i_abc[i] = [i_a, i_b, i_c]
        i_dq[i] = [i_d, i_q]
        v_abc[i] = [v_a, v_b, v_c]
        theta_arr[i] = theta
    
    # 绘图
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    time_ms = time * 1000
    
    # 子图1: 三相电流
    axes[0, 0].plot(time_ms, i_abc[:, 0], 'r-', linewidth=1.5, label='ia', alpha=0.8)
    axes[0, 0].plot(time_ms, i_abc[:, 1], 'g-', linewidth=1.5, label='ib', alpha=0.8)
    axes[0, 0].plot(time_ms, i_abc[:, 2], 'b-', linewidth=1.5, label='ic', alpha=0.8)
    axes[0, 0].set_ylabel('电流 (A)', fontsize=10)
    axes[0, 0].set_title('三相电流 (abc坐标)', fontsize=11, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend(fontsize=9, ncol=3)
    
    # 子图2: dq电流
    axes[0, 1].plot(time_ms, i_dq[:, 0], 'r-', linewidth=2, label='id')
    axes[0, 1].plot(time_ms, i_dq[:, 1], 'b-', linewidth=2, label='iq')
    axes[0, 1].axhline(i_d_ref, color='r', linestyle='--', linewidth=1, alpha=0.5, label='id_ref')
    axes[0, 1].axhline(i_q_ref, color='b', linestyle='--', linewidth=1, alpha=0.5, label='iq_ref')
    axes[0, 1].set_ylabel('电流 (A)', fontsize=10)
    axes[0, 1].set_title('dq电流 (同步坐标系)', fontsize=11, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend(fontsize=9)
    
    # 子图3: 三相电压
    axes[1, 0].plot(time_ms, v_abc[:, 0], 'r-', linewidth=1, alpha=0.7, label='va')
    axes[1, 0].plot(time_ms, v_abc[:, 1], 'g-', linewidth=1, alpha=0.7, label='vb')
    axes[1, 0].plot(time_ms, v_abc[:, 2], 'b-', linewidth=1, alpha=0.7, label='vc')
    axes[1, 0].set_xlabel('时间 (ms)', fontsize=10)
    axes[1, 0].set_ylabel('电压 (V)', fontsize=10)
    axes[1, 0].set_title('三相控制电压', fontsize=11, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend(fontsize=9, ncol=3)
    
    # 子图4: dq误差
    error_d = i_d_ref - i_dq[:, 0]
    error_q = i_q_ref - i_dq[:, 1]
    
    axes[1, 1].plot(time_ms, error_d, 'r-', linewidth=1.5, label='ed')
    axes[1, 1].plot(time_ms, error_q, 'b-', linewidth=1.5, label='eq')
    axes[1, 1].set_xlabel('时间 (ms)', fontsize=10)
    axes[1, 1].set_ylabel('误差 (A)', fontsize=10)
    axes[1, 1].set_title('dq跟踪误差', fontsize=11, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_14_exp4_dq_control.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图4已保存: case_14_exp4_dq_control.png")
    plt.show()
    
    # 稳态性能
    steady_idx = int(0.06 / Ts)
    i_d_steady = i_dq[steady_idx:, 0]
    i_q_steady = i_dq[steady_idx:, 1]
    
    i_d_mean = np.mean(i_d_steady)
    i_q_mean = np.mean(i_q_steady)
    i_d_std = np.std(i_d_steady)
    i_q_std = np.std(i_q_steady)
    
    print(f"\ndq电流稳态值:")
    print(f"  id: {i_d_mean:.3f} ± {i_d_std:.4f} A (参考: {i_d_ref} A)")
    print(f"  iq: {i_q_mean:.3f} ± {i_q_std:.4f} A (参考: {i_q_ref} A)")
    print(f"\n解耦效果:")
    print(f"  d轴误差: {abs(i_d_mean - i_d_ref):.4f} A")
    print(f"  q轴误差: {abs(i_q_mean - i_q_ref):.4f} A")


def main():
    """主函数"""
    print("=" * 60)
    print("案例14: 电流控制")
    print("从PI到PR,再到dq坐标系控制")
    print("=" * 60)
    
    # 运行所有实验
    experiment_1_pi_controller()
    experiment_2_pr_controller()
    experiment_3_pi_vs_pr()
    experiment_4_dq_control()
    
    print("\n" + "=" * 60)
    print("✅ 所有实验完成!")
    print("=" * 60)
    print("\n总结:")
    print("  1. PI控制器: 简单有效,适用于dq坐标系")
    print("  2. PR控制器: 对特定频率无稳态误差,适用于abc坐标系")
    print("  3. dq控制: 将交流量变为直流量,实现解耦控制")
    print("  4. 解耦控制: 前馈补偿消除d/q轴耦合")
    print("  5. 参数整定: 根据系统带宽和时间常数设计")


if __name__ == "__main__":
    main()
