"""
案例7: PMSG建模

本案例演示:
1. PMSG稳态特性
2. 电磁转矩计算
3. dq坐标系下的电压/电流关系
4. Id=0控制策略

工程背景: 直驱式永磁风力发电机
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.generator import PMSGModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_pmsg_characteristics():
    """演示1: PMSG稳态特性"""
    print("=" * 60)
    print("演示1: PMSG稳态特性")
    print("=" * 60)
    
    pmsg = PMSGModel(
        P_rated=2e6,
        V_rated=690,
        poles=60,  # 直驱，极对数多
        Rs=0.01,
        Ld=0.8,
        Lq=0.8,
        psi_f=1.0
    )
    
    print(f"\nPMSG参数:")
    print(f"  额定功率: {pmsg.P_rated/1e6:.1f} MW")
    print(f"  极对数: {pmsg.poles}")
    print(f"  Rs: {pmsg.Rs} pu")
    print(f"  Ld=Lq: {pmsg.Ld} pu (表贴式)")
    print(f"  永磁磁链: {pmsg.psi_f} pu")
    
    # 转速范围 (低速直驱)
    omega_rpm = np.linspace(5, 20, 50)
    omega_r = omega_rpm * 2*np.pi / 60
    
    # Id=0控制（表贴式PMSG常用）
    Id = 0
    Iq_rated = 1000  # A (示例值)
    
    Te_vals = []
    Ps_vals = []
    Vd_vals = []
    Vq_vals = []
    
    print(f"\n计算PMSG特性 (Id=0控制, Iq={Iq_rated}A)...")
    for omega in omega_r:
        result = pmsg.steady_state(omega, Iq_rated, Id)
        Te_vals.append(result['Te'] / 1e3)  # kN*m
        Ps_vals.append(result['Ps'] / 1e6)  # MW
        Vd_vals.append(result['Vd'])
        Vq_vals.append(result['Vq'])
    
    print(f"\n关键点:")
    idx_mid = len(omega_rpm) // 2
    print(f"  n={omega_rpm[idx_mid]:.0f}RPM: Te={Te_vals[idx_mid]:.1f}kN*m, P={Ps_vals[idx_mid]:.2f}MW")
    print(f"  n={omega_rpm[-1]:.0f}RPM: Te={Te_vals[-1]:.1f}kN*m, P={Ps_vals[-1]:.2f}MW")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 转矩-转速
    ax = axes[0, 0]
    ax.plot(omega_rpm, Te_vals, 'b-', linewidth=2)
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('电磁转矩 (kN·m)', fontsize=12)
    ax.set_title('转矩-转速特性', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 功率-转速
    ax = axes[0, 1]
    ax.plot(omega_rpm, Ps_vals, 'g-', linewidth=2)
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('输出功率 (MW)', fontsize=12)
    ax.set_title('功率-转速特性', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # dq电压
    ax = axes[1, 0]
    ax.plot(omega_rpm, Vd_vals, 'r-', linewidth=2, label='Vd')
    ax.plot(omega_rpm, Vq_vals, 'b-', linewidth=2, label='Vq')
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('电压 (V)', fontsize=12)
    ax.set_title('dq轴电压', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 电压幅值
    ax = axes[1, 1]
    V_mag = np.sqrt(np.array(Vd_vals)**2 + np.array(Vq_vals)**2)
    ax.plot(omega_rpm, V_mag, 'purple', linewidth=2)
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('端电压 (V)', fontsize=12)
    ax.set_title('端电压幅值', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case07_pmsg_characteristics.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case07_pmsg_characteristics.png")


def demo_torque_control():
    """演示2: 转矩控制（Id变化）"""
    print("\n" + "=" * 60)
    print("演示2: PMSG转矩控制策略")
    print("=" * 60)
    
    pmsg = PMSGModel(poles=60)
    
    omega_r = 10 * 2*np.pi / 60  # 10 RPM
    Iq_vals = np.linspace(0, 2000, 50)
    
    # 三种Id控制策略
    Id_strategies = [
        ("Id=0 (标准)", 0),
        ("弱磁 (Id<0)", -500),
        ("增磁 (Id>0)", 500),
    ]
    
    print(f"\n转速: {10} RPM")
    print(f"\n不同Id控制策略:")
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, (name, Id) in enumerate(Id_strategies):
        Te_vals = []
        Ps_vals = []
        
        for Iq in Iq_vals:
            result = pmsg.steady_state(omega_r, Iq, Id)
            Te_vals.append(result['Te'] / 1e3)
            Ps_vals.append(result['Ps'] / 1e6)
        
        print(f"\n{name}:")
        print(f"  Iq=1000A: Te={pmsg.electromagnetic_torque(Id, 1000)/1e3:.1f}kN*m")
        
        ax = axes[idx]
        ax.plot(Iq_vals, Te_vals, 'b-', linewidth=2, label='转矩')
        ax_twin = ax.twinx()
        ax_twin.plot(Iq_vals, Ps_vals, 'g--', linewidth=2, label='功率')
        
        ax.set_xlabel('Iq (A)', fontsize=12)
        ax.set_ylabel('转矩 (kN·m)', fontsize=12, color='b')
        ax_twin.set_ylabel('功率 (MW)', fontsize=12, color='g')
        ax.set_title(f'{name}\n(Id={Id}A)', fontsize=13, fontweight='bold')
        ax.tick_params(axis='y', labelcolor='b')
        ax_twin.tick_params(axis='y', labelcolor='g')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case07_torque_control.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case07_torque_control.png")


def demo_operating_region():
    """演示3: PMSG运行区域"""
    print("\n" + "=" * 60)
    print("演示3: PMSG转矩-转速运行区域")
    print("=" * 60)
    
    pmsg = PMSGModel(P_rated=2e6, poles=60)
    
    omega_rpm = np.linspace(5, 20, 50)
    omega_r = omega_rpm * 2*np.pi / 60
    
    # 额定电流
    I_rated = 1200  # A
    
    Te_rated = []
    P_rated = []
    
    print(f"\n额定电流: {I_rated} A")
    
    for omega in omega_r:
        # Id=0, Iq=I_rated
        result = pmsg.steady_state(omega, I_rated, 0)
        Te_rated.append(result['Te'] / 1e3)
        P_rated.append(result['Ps'] / 1e6)
    
    # 恒转矩区和恒功率区
    idx_base = 15
    Te_base = Te_rated[idx_base]
    P_base = P_rated[idx_base]
    omega_base = omega_rpm[idx_base]
    
    # 恒功率区曲线
    Te_const_power = [P_base * 1e6 / (omega * pmsg.poles/2) / 1e3 
                      if omega > omega_r[idx_base] else Te_base
                      for omega in omega_r]
    
    print(f"\n基速点:")
    print(f"  n_base = {omega_base:.0f} RPM")
    print(f"  Te_base = {Te_base:.0f} kN*m")
    print(f"  P_base = {P_base:.2f} MW")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(omega_rpm, Te_rated, 'b-', linewidth=2, label='额定电流曲线')
    ax.plot(omega_rpm, Te_const_power, 'r--', linewidth=2, label='恒功率运行')
    ax.axvline(omega_base, color='g', linestyle='--', alpha=0.5, label=f'基速({omega_base:.0f}RPM)')
    
    # 标注区域
    ax.fill_between(omega_rpm[:idx_base+1], 0, Te_rated[:idx_base+1], 
                     alpha=0.2, color='blue', label='恒转矩区')
    ax.fill_between(omega_rpm[idx_base:], 0, Te_const_power[idx_base:], 
                     alpha=0.2, color='red', label='弱磁区')
    
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('转矩 (kN·m)', fontsize=12)
    ax.set_title('PMSG转矩-转速运行区域', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case07_operating_region.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case07_operating_region.png")


def main():
    print("\n" + "=" * 60)
    print("案例7: PMSG建模")
    print("=" * 60)
    
    demo_pmsg_characteristics()
    demo_torque_control()
    demo_operating_region()
    
    print("\n" + "=" * 60)
    print("案例7 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case07_pmsg_characteristics.png")
    print("  2. case07_torque_control.png")
    print("  3. case07_operating_region.png")
    
    print("\n核心知识点:")
    print("  ✓ PMSG dq模型")
    print("  ✓ Id=0控制策略")
    print("  ✓ 电磁转矩计算")
    print("  ✓ 恒转矩/恒功率区")
    
    plt.show()


if __name__ == "__main__":
    main()
