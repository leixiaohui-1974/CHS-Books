"""
案例9: 传动系统建模

本案例演示:
1. 两质量模型
2. 轴扭振分析
3. 齿轮箱动态
4. 谐振频率识别

工程背景: 风力机传动系统振动与疲劳
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.generator import DrivetrainModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_two_mass_response():
    """演示1: 阶跃转矩响应"""
    print("=" * 60)
    print("演示1: 传动系统阶跃响应")
    print("=" * 60)
    
    drivetrain = DrivetrainModel(
        Jt=1e7,      # 风轮惯量
        Jg=1e5,      # 发电机惯量
        Ks=1e8,      # 轴刚度
        Cs=1e6,      # 轴阻尼
        N=100        # 齿轮比
    )
    
    print(f"\n传动系统参数:")
    print(f"  风轮惯量: {drivetrain.Jt/1e6:.0f} × 10^6 kg·m²")
    print(f"  发电机惯量: {drivetrain.Jg/1e3:.0f} × 10^3 kg·m²")
    print(f"  轴刚度: {drivetrain.Ks/1e8:.1f} × 10^8 N·m/rad")
    print(f"  齿轮比: {drivetrain.N}")
    
    # 初始稳态
    omega_0 = 1.0  # rad/s (风轮侧)
    state0 = np.array([0, omega_0, 0, omega_0 * drivetrain.N])
    
    # 转矩函数
    Tt_step = 5e5  # N*m
    Tg_avg = Tt_step / drivetrain.N
    
    def Tt_func(t):
        return Tt_step if t >= 1 else Tt_step * 0.5
    
    def Tg_func(t):
        return Tg_avg
    
    # 仿真
    print(f"\n仿真阶跃响应...")
    result = drivetrain.simulate((0, 10), state0, Tt_func, Tg_func, dt=0.001)
    
    t = result['t']
    omega_t = result['omega_t']
    omega_g = result['omega_g']
    theta_twist = result['theta_t'] - drivetrain.N * result['theta_g']
    T_shaft = drivetrain.Ks * theta_twist
    
    # 找振荡频率
    idx_osc = (t > 1) & (t < 5)
    omega_t_osc = omega_t[idx_osc] - omega_t[idx_osc].mean()
    fft_result = np.fft.fft(omega_t_osc)
    freq = np.fft.fftfreq(len(omega_t_osc), t[1]-t[0])
    idx_peak = np.argmax(np.abs(fft_result[1:len(freq)//2])) + 1
    f_osc = abs(freq[idx_peak])
    
    print(f"\n响应特性:")
    print(f"  振荡频率: {f_osc:.2f} Hz")
    print(f"  阻尼比: ~{drivetrain.Cs/np.sqrt(drivetrain.Ks*drivetrain.Jt):.3f}")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 转速
    ax = axes[0, 0]
    ax.plot(t, omega_t, 'b-', linewidth=1.5, label='风轮转速')
    ax.plot(t, omega_g/drivetrain.N, 'r--', linewidth=1.5, label='发电机转速(折算)')
    ax.axvline(1, color='g', linestyle='--', alpha=0.5)
    ax.set_ylabel('角速度 (rad/s)', fontsize=12)
    ax.set_title('转速响应', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 10)
    
    # 轴转矩
    ax = axes[0, 1]
    ax.plot(t, T_shaft/1e3, 'purple', linewidth=1.5)
    ax.axhline(Tt_step/1e3, color='r', linestyle='--', alpha=0.5, label='稳态值')
    ax.axvline(1, color='g', linestyle='--', alpha=0.5)
    ax.set_ylabel('轴转矩 (kN·m)', fontsize=12)
    ax.set_title('轴转矩振荡', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 10)
    
    # 扭转角
    ax = axes[1, 0]
    ax.plot(t, theta_twist * 180/np.pi, 'g-', linewidth=1.5)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('扭转角 (度)', fontsize=12)
    ax.set_title('轴扭转角', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 10)
    
    # FFT频谱
    ax = axes[1, 1]
    ax.plot(freq[:len(freq)//2], np.abs(fft_result[:len(freq)//2]), 'b-')
    ax.axvline(f_osc, color='r', linestyle='--', label=f'谐振({f_osc:.2f}Hz)')
    ax.set_xlabel('频率 (Hz)', fontsize=12)
    ax.set_ylabel('幅值', fontsize=12)
    ax.set_title('频谱分析', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 5)
    
    plt.tight_layout()
    plt.savefig('case09_two_mass_response.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case09_two_mass_response.png")
    
    return f_osc


def demo_resonance_analysis(f_osc):
    """演示2: 谐振分析"""
    print("\n" + "=" * 60)
    print("演示2: 传动系统谐振频率分析")
    print("=" * 60)
    
    # 参数变化对谐振频率的影响
    Ks_range = np.logspace(7, 9, 50)  # 刚度范围
    Jt_range = np.logspace(6, 8, 50)  # 惯量范围
    
    # 简化谐振频率计算
    Jt_nom = 1e7
    Jg_nom = 1e5
    N = 100
    
    # f_res ≈ 1/(2π) * sqrt(Ks * (Jt + Jg*N^2) / (Jt * Jg * N^2))
    f_vs_Ks = []
    for Ks in Ks_range:
        Jeq = Jt_nom * Jg_nom * N**2 / (Jt_nom + Jg_nom * N**2)
        f = 1/(2*np.pi) * np.sqrt(Ks / Jeq)
        f_vs_Ks.append(f)
    
    f_vs_Jt = []
    Ks_nom = 1e8
    for Jt in Jt_range:
        Jeq = Jt * Jg_nom * N**2 / (Jt + Jg_nom * N**2)
        f = 1/(2*np.pi) * np.sqrt(Ks_nom / Jeq)
        f_vs_Jt.append(f)
    
    print(f"\n谐振频率分析:")
    print(f"  实测谐振频率: {f_osc:.2f} Hz")
    print(f"  刚度影响: Ks ↑ → f_res ↑")
    print(f"  惯量影响: Jt ↑ → f_res ↓")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 刚度影响
    ax = axes[0]
    ax.semilogx(Ks_range/1e8, f_vs_Ks, 'b-', linewidth=2)
    ax.axhline(f_osc, color='r', linestyle='--', label=f'设计点({f_osc:.2f}Hz)')
    ax.set_xlabel('轴刚度 (×10⁸ N·m/rad)', fontsize=12)
    ax.set_ylabel('谐振频率 (Hz)', fontsize=12)
    ax.set_title('刚度对谐振频率的影响', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 惯量影响
    ax = axes[1]
    ax.semilogx(Jt_range/1e6, f_vs_Jt, 'g-', linewidth=2)
    ax.axhline(f_osc, color='r', linestyle='--', label=f'设计点({f_osc:.2f}Hz)')
    ax.set_xlabel('风轮惯量 (×10⁶ kg·m²)', fontsize=12)
    ax.set_ylabel('谐振频率 (Hz)', fontsize=12)
    ax.set_title('惯量对谐振频率的影响', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case09_resonance_analysis.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case09_resonance_analysis.png")


def main():
    print("\n" + "=" * 60)
    print("案例9: 传动系统建模")
    print("=" * 60)
    
    f_osc = demo_two_mass_response()
    demo_resonance_analysis(f_osc)
    
    print("\n" + "=" * 60)
    print("案例9 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case09_two_mass_response.png")
    print("  2. case09_resonance_analysis.png")
    
    print("\n核心知识点:")
    print("  ✓ 两质量模型")
    print("  ✓ 轴扭振分析")
    print("  ✓ 谐振频率计算")
    print("  ✓ 参数敏感性分析")
    
    plt.show()


if __name__ == "__main__":
    main()
