"""
案例16: 并网同步控制 - 锁相环(PLL)设计
演示SRF-PLL和单相PLL的工作原理

实验内容:
1. SRF-PLL基本原理
2. 频率阶跃响应
3. 相位阶跃响应
4. 电网扰动下的性能

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.inverter_control import SRFPLL, SinglePhasePLL

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_srf_pll_basic():
    """
    实验1: SRF-PLL基本原理
    测试PLL的锁相过程和稳态性能
    """
    print("=" * 60)
    print("实验1: SRF-PLL基本原理")
    print("=" * 60)
    
    # PLL参数
    Kp = 50.0
    Ki = 1000.0
    omega_nominal = 2 * np.pi * 50.0
    
    print(f"PLL参数:")
    print(f"  Kp = {Kp}")
    print(f"  Ki = {Ki}")
    print(f"  额定频率 = 50 Hz")
    
    # 创建PLL
    pll = SRFPLL(Kp=Kp, Ki=Ki, omega_nominal=omega_nominal)
    
    # 仿真参数
    dt = 1e-4
    t_total = 0.2  # 200ms
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    # 三相电网电压 (平衡系统)
    V_grid = 311.0  # 220Vrms * √2
    f_grid = 50.0   # 电网频率
    omega_grid = 2 * np.pi * f_grid
    phi_grid = np.pi / 6  # 初始相位30度
    
    # 记录数组
    theta_pll = np.zeros(N)
    theta_grid = np.zeros(N)
    freq_pll = np.zeros(N)
    v_d = np.zeros(N)
    v_q = np.zeros(N)
    
    # 仿真循环
    for i, t in enumerate(time):
        # 电网电压 (三相)
        theta_g = omega_grid * t + phi_grid
        va = V_grid * np.sin(theta_g)
        vb = V_grid * np.sin(theta_g - 2 * np.pi / 3)
        vc = V_grid * np.sin(theta_g + 2 * np.pi / 3)
        
        # PLL更新
        theta, omega, frequency = pll.update(va, vb, vc, dt)
        
        # 记录
        theta_pll[i] = theta
        theta_grid[i] = np.mod(theta_g, 2 * np.pi)
        freq_pll[i] = frequency
        v_d[i] = pll.v_d
        v_q[i] = pll.v_q
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    time_ms = time * 1000
    
    # 子图1: 相位跟踪
    axes[0].plot(time_ms, np.degrees(theta_grid), 'r--', linewidth=2, alpha=0.7, label='电网相位')
    axes[0].plot(time_ms, np.degrees(theta_pll), 'b-', linewidth=1.5, label='PLL相位')
    axes[0].set_ylabel('相位 (度)', fontsize=11)
    axes[0].set_title('SRF-PLL相位跟踪', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_ylim([0, 360])
    
    # 子图2: 频率估计
    axes[1].plot(time_ms, freq_pll, 'g-', linewidth=1.5)
    axes[1].axhline(f_grid, color='r', linestyle='--', linewidth=2, alpha=0.7, label='额定频率')
    axes[1].set_ylabel('频率 (Hz)', fontsize=11)
    axes[1].set_title('频率估计', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    axes[1].set_ylim([49.5, 50.5])
    
    # 子图3: dq分量
    axes[2].plot(time_ms, v_d, 'b-', linewidth=1.5, label='v_d')
    axes[2].plot(time_ms, v_q, 'r-', linewidth=1.5, label='v_q (误差)')
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('电压 (V)', fontsize=11)
    axes[2].set_title('dq坐标系电压', fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=10)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_16_exp1_srf_pll_basic.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图1已保存")
    plt.show()
    
    # 性能指标
    steady_idx = int(0.15 / dt)  # 稳态从150ms开始
    theta_error = np.abs(theta_pll[steady_idx:] - theta_grid[steady_idx:])
    theta_error = np.minimum(theta_error, 2 * np.pi - theta_error)  # 处理周期性
    
    freq_error = np.abs(freq_pll[steady_idx:] - f_grid)
    
    print(f"\n稳态性能:")
    print(f"  相位误差: {np.mean(np.degrees(theta_error)):.3f}°")
    print(f"  频率误差: {np.mean(freq_error)*1000:.3f} mHz")
    print(f"  v_q误差: {np.mean(np.abs(v_q[steady_idx:])):.2f} V")


def experiment_2_frequency_step():
    """
    实验2: 频率阶跃响应
    测试PLL对电网频率变化的跟踪能力
    """
    print("\n" + "=" * 60)
    print("实验2: 频率阶跃响应")
    print("=" * 60)
    
    # 创建PLL
    pll = SRFPLL(Kp=50.0, Ki=1000.0)
    
    # 仿真
    dt = 1e-4
    t_total = 0.4
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    V_grid = 311.0
    
    # 记录
    freq_grid = np.zeros(N)
    freq_pll = np.zeros(N)
    theta_error = np.zeros(N)
    
    theta_g = 0.0
    
    for i, t in enumerate(time):
        # 电网频率阶跃 (50Hz → 50.5Hz → 49.5Hz)
        if t < 0.1:
            f_grid = 50.0
        elif t < 0.25:
            f_grid = 50.5
        else:
            f_grid = 49.5
        
        omega_grid = 2 * np.pi * f_grid
        theta_g += omega_grid * dt
        theta_g = np.mod(theta_g, 2 * np.pi)
        
        # 三相电压
        va = V_grid * np.sin(theta_g)
        vb = V_grid * np.sin(theta_g - 2 * np.pi / 3)
        vc = V_grid * np.sin(theta_g + 2 * np.pi / 3)
        
        # PLL
        theta, omega, frequency = pll.update(va, vb, vc, dt)
        
        # 记录
        freq_grid[i] = f_grid
        freq_pll[i] = frequency
        
        # 相位误差
        err = np.abs(theta - theta_g)
        theta_error[i] = np.minimum(err, 2 * np.pi - err)
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    time_ms = time * 1000
    
    # 频率跟踪
    axes[0].plot(time_ms, freq_grid, 'r--', linewidth=2, alpha=0.7, label='电网频率')
    axes[0].plot(time_ms, freq_pll, 'b-', linewidth=1.5, label='PLL频率')
    axes[0].set_ylabel('频率 (Hz)', fontsize=11)
    axes[0].set_title('频率阶跃响应', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    
    # 相位误差
    axes[1].plot(time_ms, np.degrees(theta_error), 'g-', linewidth=1.5)
    axes[1].set_xlabel('时间 (ms)', fontsize=11)
    axes[1].set_ylabel('相位误差 (度)', fontsize=11)
    axes[1].set_title('相位跟踪误差', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_16_exp2_frequency_step.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图2已保存")
    plt.show()
    
    # 性能
    print(f"\n频率跟踪性能:")
    print(f"  +0.5Hz阶跃: 响应时间 ≈ {np.argmax(freq_pll[1000:1500] > 50.4) * dt * 1000:.1f} ms")
    print(f"  -1.0Hz阶跃: 响应时间 ≈ {np.argmax(freq_pll[2500:3000] < 49.6) * dt * 1000:.1f} ms")


def experiment_3_phase_jump():
    """
    实验3: 相位跳变响应
    测试PLL对相位突变的适应能力
    """
    print("\n" + "=" * 60)
    print("实验3: 相位跳变响应")
    print("=" * 60)
    
    # 创建PLL
    pll = SRFPLL(Kp=50.0, Ki=1000.0)
    
    # 仿真
    dt = 1e-4
    t_total = 0.3
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    V_grid = 311.0
    f_grid = 50.0
    omega_grid = 2 * np.pi * f_grid
    
    # 记录
    theta_grid = np.zeros(N)
    theta_pll = np.zeros(N)
    
    for i, t in enumerate(time):
        # 相位跳变 (+30度 at t=0.1s)
        if t < 0.1:
            phase_offset = 0.0
        else:
            phase_offset = np.radians(30.0)
        
        theta_g = omega_grid * t + phase_offset
        
        # 三相电压
        va = V_grid * np.sin(theta_g)
        vb = V_grid * np.sin(theta_g - 2 * np.pi / 3)
        vc = V_grid * np.sin(theta_g + 2 * np.pi / 3)
        
        # PLL
        theta, omega, frequency = pll.update(va, vb, vc, dt)
        
        # 记录
        theta_grid[i] = np.mod(theta_g, 2 * np.pi)
        theta_pll[i] = theta
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    time_ms = time * 1000
    
    # 相位跟踪
    axes[0].plot(time_ms, np.degrees(theta_grid), 'r--', linewidth=2, alpha=0.7, label='电网相位')
    axes[0].plot(time_ms, np.degrees(theta_pll), 'b-', linewidth=1.5, label='PLL相位')
    axes[0].set_ylabel('相位 (度)', fontsize=11)
    axes[0].set_title('相位跳变响应', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    
    # 相位误差
    error = theta_pll - theta_grid
    error = np.mod(error + np.pi, 2 * np.pi) - np.pi  # 归一化到[-π, π]
    axes[1].plot(time_ms, np.degrees(error), 'g-', linewidth=1.5)
    axes[1].set_xlabel('时间 (ms)', fontsize=11)
    axes[1].set_ylabel('相位误差 (度)', fontsize=11)
    axes[1].set_title('相位跟踪误差', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    axes[1].axvline(100, color='r', linestyle='--', linewidth=1, alpha=0.5, label='跳变时刻')
    axes[1].legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('case_16_exp3_phase_jump.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图3已保存")
    plt.show()
    
    # 性能
    jump_idx = int(0.1 / dt)
    recovery_idx = jump_idx + np.argmax(np.abs(error[jump_idx:]) < np.radians(2))
    recovery_time = (recovery_idx - jump_idx) * dt * 1000
    
    print(f"\n相位跳变性能:")
    print(f"  跳变幅度: 30°")
    print(f"  恢复时间: {recovery_time:.1f} ms (误差<2°)")


def main():
    """主函数"""
    print("=" * 60)
    print("案例16: 并网同步控制 - 锁相环(PLL)设计")
    print("三相系统的相位、频率检测与跟踪")
    print("=" * 60)
    
    experiment_1_srf_pll_basic()
    experiment_2_frequency_step()
    experiment_3_phase_jump()
    
    print("\n" + "=" * 60)
    print("✅ 所有实验完成!")
    print("=" * 60)
    print("\n总结:")
    print("  1. SRF-PLL: 快速准确的相位跟踪")
    print("  2. 频率估计: 毫赫兹级精度")
    print("  3. 动态响应: 快速适应频率/相位变化")
    print("  4. 工程应用: 并网同步的核心技术")


if __name__ == "__main__":
    main()
