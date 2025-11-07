"""
案例15: 电压控制
演示直流电压控制、交流电压控制和双环控制

实验内容:
1. 直流母线电压控制
2. 交流单相电压控制 (双环)
3. 负载突变响应测试
4. 前馈补偿效果分析

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.inverter_control import (
    DCVoltageController, ACVoltageController, DualLoopVoltageController
)

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_dc_voltage_control():
    """
    实验1: 直流母线电压控制
    测试DC电压控制器的稳定性和动态响应
    """
    print("=" * 60)
    print("实验1: 直流母线电压控制")
    print("=" * 60)
    
    # 系统参数
    C_dc = 2000e-6  # 2000μF电容
    V_dc_nominal = 400.0  # 400V额定电压
    
    # 控制器参数 (根据带宽设计)
    omega_c = 2 * np.pi * 100  # 100Hz带宽
    Kp = 2 * C_dc * omega_c
    Ki = C_dc * omega_c ** 2
    
    print(f"系统参数:")
    print(f"  C_dc = {C_dc*1e6:.0f} μF")
    print(f"  V_nom = {V_dc_nominal} V")
    print(f"\n控制器参数:")
    print(f"  Kp = {Kp:.3f}")
    print(f"  Ki = {Ki:.2f}")
    print(f"  带宽 = {omega_c/(2*np.pi):.0f} Hz")
    
    # 创建控制器
    dc_ctrl = DCVoltageController(Kp, Ki, C_dc, V_dc_nominal, i_limit=50.0)
    
    # 仿真参数
    dt = 1e-5
    t_total = 0.2  # 200ms
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    # 初始化
    v_dc = 380.0  # 初始电压略低
    i_pv = 0.0    # 光伏输入电流
    
    # 记录数组
    v_dc_arr = np.zeros(N)
    v_ref_arr = np.zeros(N)
    i_ref_arr = np.zeros(N)
    p_load_arr = np.zeros(N)
    
    # 仿真循环
    for i, t in enumerate(time):
        # 参考电压
        v_ref = V_dc_nominal
        
        # 负载功率 (阶跃变化)
        if t < 0.05:
            p_load = 1000.0  # 1kW
        elif t < 0.1:
            p_load = 2000.0  # 阶跃到2kW
        elif t < 0.15:
            p_load = 3000.0  # 阶跃到3kW
        else:
            p_load = 2000.0  # 回到2kW
        
        # 电压控制器
        i_ref = dc_ctrl.update(v_ref, v_dc, dt, p_load, enable_feedforward=True)
        
        # 模拟光伏电流 (简化: 假设MPPT完美跟踪i_ref)
        i_pv = i_ref
        
        # 电容电压动态
        i_load = p_load / v_dc if v_dc > 0 else 0
        dv_dc = (i_pv - i_load) / C_dc
        v_dc += dv_dc * dt
        
        # 记录
        v_dc_arr[i] = v_dc
        v_ref_arr[i] = v_ref
        i_ref_arr[i] = i_ref
        p_load_arr[i] = p_load
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    time_ms = time * 1000
    
    # 子图1: 直流电压
    axes[0].plot(time_ms, v_ref_arr, 'r--', linewidth=2, label='参考电压')
    axes[0].plot(time_ms, v_dc_arr, 'b-', linewidth=1.5, label='实际电压')
    axes[0].set_ylabel('电压 (V)', fontsize=11)
    axes[0].set_title('直流母线电压控制', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    axes[0].set_ylim([370, 410])
    
    # 子图2: 参考电流
    axes[1].plot(time_ms, i_ref_arr, 'g-', linewidth=1.5)
    axes[1].set_ylabel('电流 (A)', fontsize=11)
    axes[1].set_title('输出参考电流', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # 子图3: 负载功率
    axes[2].plot(time_ms, p_load_arr/1000, 'k-', linewidth=2)
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('功率 (kW)', fontsize=11)
    axes[2].set_title('负载功率', fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_15_exp1_dc_voltage.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图1已保存")
    plt.show()
    
    # 性能指标
    print(f"\n性能指标:")
    print(f"  电压调整率: {(np.max(v_dc_arr) - np.min(v_dc_arr))/V_dc_nominal*100:.2f}%")
    print(f"  稳态误差: {np.mean(np.abs(v_dc_arr[-1000:] - V_dc_nominal)):.2f} V")


def experiment_2_ac_voltage_control():
    """
    实验2: 交流电压控制 (单相双环)
    测试AC电压控制器的性能
    """
    print("\n" + "=" * 60)
    print("实验2: 交流电压控制 (双环)")
    print("=" * 60)
    
    # 系统参数
    L = 5e-3     # 5mH
    C = 20e-6    # 20μF
    R = 0.1      # 0.1Ω
    omega = 2 * np.pi * 50
    
    # 控制器参数
    # 电压环: 较低带宽
    omega_v = 2 * np.pi * 200  # 200Hz
    Kp_v = 2 * C * omega_v
    Ki_v = C * omega_v ** 2
    
    # 电流环: 较高带宽
    omega_i = 2 * np.pi * 2000  # 2kHz
    Kp_i = L * omega_i
    Ki_i = R * omega_i
    
    print(f"控制器参数:")
    print(f"  电压环: Kp={Kp_v:.4f}, Ki={Ki_v:.2f}, BW={omega_v/(2*np.pi):.0f}Hz")
    print(f"  电流环: Kp={Kp_i:.3f}, Ki={Ki_i:.1f}, BW={omega_i/(2*np.pi):.0f}Hz")
    
    # 创建控制器
    ac_ctrl = ACVoltageController(Kp_v, Ki_v, Kp_i, Ki_i, L, C, omega, 
                                   v_limit=50.0, i_limit=400.0)
    
    # 仿真
    dt = 1e-5
    t_total = 0.1
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    # 初始化
    v_c = 0.0
    i_L = 0.0
    
    v_ref_arr = np.zeros(N)
    v_c_arr = np.zeros(N)
    i_L_arr = np.zeros(N)
    i_ref_arr = np.zeros(N)
    
    # 仿真循环
    for i, t in enumerate(time):
        # 参考电压 (50Hz正弦)
        v_ref = 220 * np.sqrt(2) * np.sin(omega * t)
        
        # 负载电流 (10Ω电阻)
        R_load = 10.0 if t < 0.05 else 5.0  # 负载突变
        i_load = v_c / R_load if R_load > 0 else 0
        
        # 双环控制
        v_out = ac_ctrl.update(v_ref, v_c, i_L, dt, i_load, enable_decoupling=True)
        
        # LC滤波器动态
        di_L = (v_out - v_c - R * i_L) / L
        dv_c = (i_L - i_load) / C
        
        i_L += di_L * dt
        v_c += dv_c * dt
        
        # 记录
        v_ref_arr[i] = v_ref
        v_c_arr[i] = v_c
        i_L_arr[i] = i_L
        i_ref_arr[i] = ac_ctrl.i_ref
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    time_ms = time * 1000
    
    # 电压跟踪
    axes[0].plot(time_ms, v_ref_arr, 'r--', linewidth=1.5, alpha=0.7, label='参考电压')
    axes[0].plot(time_ms, v_c_arr, 'b-', linewidth=1, label='实际电压')
    axes[0].set_ylabel('电压 (V)', fontsize=11)
    axes[0].set_title('交流电压双环控制', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    
    # 电流跟踪
    axes[1].plot(time_ms, i_ref_arr, 'r--', linewidth=1.5, alpha=0.7, label='参考电流')
    axes[1].plot(time_ms, i_L_arr, 'g-', linewidth=1, label='实际电流')
    axes[1].set_ylabel('电流 (A)', fontsize=11)
    axes[1].set_title('电流内环', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10)
    
    # 误差
    error = v_ref_arr - v_c_arr
    axes[2].plot(time_ms, error, 'r-', linewidth=1)
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('误差 (V)', fontsize=11)
    axes[2].set_title('电压跟踪误差', fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_15_exp2_ac_voltage.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图2已保存")
    plt.show()
    
    # 性能
    steady_idx = int(0.08 / dt)
    error_steady = error[steady_idx:]
    rmse = np.sqrt(np.mean(error_steady**2))
    
    print(f"\n稳态性能:")
    print(f"  RMS误差: {rmse:.2f} V")
    print(f"  误差百分比: {rmse/(220*np.sqrt(2))*100:.2f}%")


def main():
    """主函数"""
    print("=" * 60)
    print("案例15: 电压控制")
    print("从直流到交流的完整电压控制方案")
    print("=" * 60)
    
    experiment_1_dc_voltage_control()
    experiment_2_ac_voltage_control()
    
    print("\n" + "=" * 60)
    print("✅ 所有实验完成!")
    print("=" * 60)
    print("\n总结:")
    print("  1. DC电压控制: 稳定直流母线电压")
    print("  2. AC电压控制: 双环结构确保电压质量")
    print("  3. 前馈补偿: 提高负载扰动抑制能力")
    print("  4. 带宽设计: 外环慢、内环快")


if __name__ == "__main__":
    main()
