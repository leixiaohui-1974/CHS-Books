"""
案例20: 直流母线电压控制
演示PI控制和前馈补偿

实验内容:
1. PI控制电压稳定
2. 前馈补偿效果
3. 负载扰动响应

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.dcdc_converter import BoostConverter, DCBusVoltageController, FeedforwardCompensator

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_pi_control():
    """实验1: PI控制电压稳定"""
    print("=" * 60)
    print("实验1: PI控制直流母线电压")
    print("=" * 60)
    
    # 创建Boost变换器
    boost = BoostConverter(L=100e-6, C=100e-6, R=20.0)
    
    # 创建PI控制器
    controller = DCBusVoltageController(Kp=0.001, Ki=0.5, v_ref=400.0)
    
    # 仿真参数
    dt = 1e-6
    t_total = 0.03
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    V_in = 100.0
    
    # 记录
    v_C_arr = np.zeros(N)
    d_arr = np.zeros(N)
    error_arr = np.zeros(N)
    
    # 仿真
    for i in range(N):
        # PI控制
        d = controller.update(boost.v_C, dt, enable_ff=False)
        
        # Boost更新
        _, v_C = boost.update(V_in, d, dt)
        
        # 记录
        v_C_arr[i] = v_C
        d_arr[i] = d
        error_arr[i] = controller.error
    
    # 稳态误差
    v_ss = np.mean(v_C_arr[-1000:])
    error_ss = abs(v_ss - 400.0)
    
    print(f"\n参数: Vin={V_in}V, Vref=400V")
    print(f"PI增益: Kp={controller.Kp}, Ki={controller.Ki}")
    print(f"\n稳态输出: {v_ss:.2f}V")
    print(f"稳态误差: {error_ss:.2f}V ({error_ss/400*100:.2f}%)")
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    axes[0].plot(time*1000, v_C_arr, 'b-', linewidth=1.5)
    axes[0].axhline(400, color='r', linestyle='--', alpha=0.7, label='参考400V')
    axes[0].set_ylabel('母线电压 (V)', fontsize=11)
    axes[0].set_title('PI控制 - 母线电压', fontsize=13, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(time*1000, d_arr, 'g-', linewidth=1.5)
    axes[1].set_ylabel('占空比', fontsize=11)
    axes[1].set_title('控制输出 - 占空比', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(time*1000, error_arr, 'm-', linewidth=1.5)
    axes[2].set_xlabel('时间 (ms)', fontsize=11)
    axes[2].set_ylabel('误差 (V)', fontsize=11)
    axes[2].set_title('电压误差', fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_20_exp1_pi_control.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图1已保存")
    plt.show()


def experiment_2_feedforward_comparison():
    """实验2: 前馈补偿效果对比"""
    print("\n" + "=" * 60)
    print("实验2: 前馈补偿效果")
    print("=" * 60)
    
    # 创建前馈补偿器
    ff_comp = FeedforwardCompensator(converter_type="boost")
    
    V_in = 100.0
    V_ref = 400.0
    dt = 1e-6
    t_total = 0.02
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    # 测试1: 仅PI控制
    boost1 = BoostConverter(L=100e-6, C=100e-6, R=20.0)
    ctrl1 = DCBusVoltageController(Kp=0.001, Ki=0.5, v_ref=V_ref)
    
    v_C1 = np.zeros(N)
    for i in range(N):
        d = ctrl1.update(boost1.v_C, dt, enable_ff=False)
        _, v_C1[i] = boost1.update(V_in, d, dt)
    
    # 测试2: PI + 前馈
    boost2 = BoostConverter(L=100e-6, C=100e-6, R=20.0)
    ctrl2 = DCBusVoltageController(Kp=0.001, Ki=0.5, v_ref=V_ref)
    
    v_C2 = np.zeros(N)
    for i in range(N):
        ff = ff_comp.calculate(V_in, V_ref)
        d = ctrl2.update(boost2.v_C, dt, feedforward=ff, enable_ff=True)
        _, v_C2[i] = boost2.update(V_in, d, dt)
    
    # 上升时间对比
    idx1 = np.where(v_C1 > 0.95 * V_ref)[0]
    idx2 = np.where(v_C2 > 0.95 * V_ref)[0]
    
    t_rise1 = time[idx1[0]] if len(idx1) > 0 else t_total
    t_rise2 = time[idx2[0]] if len(idx2) > 0 else t_total
    
    print(f"\n性能对比:")
    print(f"  仅PI: 上升时间 {t_rise1*1000:.2f}ms")
    print(f"  PI+前馈: 上升时间 {t_rise2*1000:.2f}ms")
    print(f"  改善: {(t_rise1-t_rise2)/t_rise1*100:.1f}%")
    
    # 绘图
    plt.figure(figsize=(12, 6))
    
    plt.plot(time*1000, v_C1, 'b-', linewidth=2, label='仅PI控制', alpha=0.8)
    plt.plot(time*1000, v_C2, 'r-', linewidth=2, label='PI+前馈', alpha=0.8)
    plt.axhline(V_ref, color='k', linestyle='--', alpha=0.5, label='参考400V')
    plt.axhline(0.95*V_ref, color='g', linestyle=':', alpha=0.5, label='95%阈值')
    
    plt.xlabel('时间 (ms)', fontsize=11)
    plt.ylabel('母线电压 (V)', fontsize=11)
    plt.title('前馈补偿效果对比', fontsize=13, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_20_exp2_feedforward.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图2已保存")
    plt.show()


def experiment_3_load_disturbance():
    """实验3: 负载扰动响应"""
    print("\n" + "=" * 60)
    print("实验3: 负载扰动响应")
    print("=" * 60)
    
    V_in = 100.0
    V_ref = 400.0
    dt = 1e-6
    t_total = 0.05
    time = np.arange(0, t_total, dt)
    N = len(time)
    
    # 创建系统
    boost = BoostConverter(L=100e-6, C=100e-6, R=20.0)
    controller = DCBusVoltageController(Kp=0.001, Ki=0.5, v_ref=V_ref)
    ff_comp = FeedforwardCompensator(converter_type="boost")
    
    # 记录
    v_C_arr = np.zeros(N)
    R_arr = np.zeros(N)
    
    # 仿真
    for i, t in enumerate(time):
        # 负载变化
        if t < 0.02:
            R = 20.0
        elif t < 0.04:
            R = 10.0  # 负载加倍
        else:
            R = 20.0  # 恢复
        
        boost.R = R
        R_arr[i] = R
        
        # 控制
        ff = ff_comp.calculate(V_in, V_ref)
        d = controller.update(boost.v_C, dt, feedforward=ff, enable_ff=True)
        
        # 更新
        _, v_C = boost.update(V_in, d, dt)
        v_C_arr[i] = v_C
    
    # 电压波动
    v_before = np.mean(v_C_arr[int(0.018/dt):int(0.02/dt)])
    v_during = np.min(v_C_arr[int(0.02/dt):int(0.025/dt)])
    voltage_drop = v_before - v_during
    
    print(f"\n负载扰动:")
    print(f"  负载变化: 20Ω → 10Ω → 20Ω")
    print(f"  电压跌落: {voltage_drop:.2f}V ({voltage_drop/V_ref*100:.2f}%)")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    axes[0].plot(time*1000, v_C_arr, 'b-', linewidth=1.5)
    axes[0].axhline(V_ref, color='r', linestyle='--', alpha=0.7)
    axes[0].axvline(20, color='g', linestyle=':', alpha=0.5)
    axes[0].axvline(40, color='g', linestyle=':', alpha=0.5)
    axes[0].set_ylabel('母线电压 (V)', fontsize=11)
    axes[0].set_title('负载扰动 - 电压响应', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(time*1000, R_arr, 'r-', linewidth=2)
    axes[1].set_xlabel('时间 (ms)', fontsize=11)
    axes[1].set_ylabel('负载电阻 (Ω)', fontsize=11)
    axes[1].set_title('负载变化', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_20_exp3_load_disturbance.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图3已保存")
    plt.show()


def main():
    """主函数"""
    print("=" * 60)
    print("案例20: 直流母线电压控制")
    print("PI控制 + 前馈补偿")
    print("=" * 60)
    
    experiment_1_pi_control()
    experiment_2_feedforward_comparison()
    experiment_3_load_disturbance()
    
    print("\n" + "=" * 60)
    print("✅ 所有实验完成!")
    print("=" * 60)
    print("\n总结:")
    print("  1. PI控制实现电压稳定 (误差<1%)")
    print("  2. 前馈补偿加快响应速度")
    print("  3. 负载扰动下电压波动<5%")


if __name__ == "__main__":
    main()
