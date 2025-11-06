"""
案例10: 塔架振动

本案例演示:
1. 塔架模态分析
2. 风载荷激励
3. 振动响应
4. 疲劳分析基础

工程背景: 风力机塔架振动与疲劳寿命
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class TowerModel:
    """简化塔架模型（单自由度）"""
    
    def __init__(self, m: float, k: float, c: float, name: str = "Tower"):
        """
        m: 等效质量 (kg)
        k: 等效刚度 (N/m)
        c: 阻尼系数 (N·s/m)
        """
        self.m = m
        self.k = k
        self.c = c
        self.name = name
        
        # 固有频率和阻尼比
        self.omega_n = np.sqrt(k / m)
        self.f_n = self.omega_n / (2*np.pi)
        self.zeta = c / (2 * np.sqrt(k * m))
    
    def response(self, t: np.ndarray, F: np.ndarray) -> np.ndarray:
        """计算振动响应（数值积分）"""
        dt = t[1] - t[0]
        x = np.zeros_like(t)
        v = np.zeros_like(t)
        
        for i in range(1, len(t)):
            a = (F[i-1] - self.c * v[i-1] - self.k * x[i-1]) / self.m
            v[i] = v[i-1] + a * dt
            x[i] = x[i-1] + v[i] * dt
        
        return x


def demo_modal_analysis():
    """演示1: 塔架模态分析"""
    print("=" * 60)
    print("演示1: 塔架固有频率与模态")
    print("=" * 60)
    
    # 典型塔架参数
    tower = TowerModel(
        m=3e5,      # 300吨
        k=5e6,      # N/m
        c=1e5       # N·s/m
    )
    
    print(f"\n塔架参数:")
    print(f"  等效质量: {tower.m/1e3:.0f} 吨")
    print(f"  等效刚度: {tower.k/1e6:.1f} MN/m")
    print(f"  阻尼系数: {tower.c/1e3:.0f} kN·s/m")
    
    print(f"\n模态特性:")
    print(f"  固有频率: {tower.f_n:.3f} Hz")
    print(f"  固有周期: {1/tower.f_n:.2f} s")
    print(f"  阻尼比: {tower.zeta:.3f}")
    
    # 自由衰减响应
    t = np.linspace(0, 20, 2000)
    x0 = 0.5  # m
    x_free = x0 * np.exp(-tower.zeta * tower.omega_n * t) * np.cos(tower.omega_n * np.sqrt(1-tower.zeta**2) * t)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 自由衰减
    ax = axes[0]
    ax.plot(t, x_free, 'b-', linewidth=1.5)
    envelope = x0 * np.exp(-tower.zeta * tower.omega_n * t)
    ax.plot(t, envelope, 'r--', linewidth=1, label='包络线')
    ax.plot(t, -envelope, 'r--', linewidth=1)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('位移 (m)', fontsize=12)
    ax.set_title('自由衰减振动', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 频率响应
    freq_range = np.linspace(0, 2, 200)
    H = 1 / np.sqrt((tower.k - tower.m * (2*np.pi*freq_range)**2)**2 + 
                     (tower.c * 2*np.pi*freq_range)**2)
    H_norm = H / H.max()
    
    ax = axes[1]
    ax.plot(freq_range, H_norm, 'g-', linewidth=2)
    ax.axvline(tower.f_n, color='r', linestyle='--', label=f'固有频率({tower.f_n:.3f}Hz)')
    ax.set_xlabel('频率 (Hz)', fontsize=12)
    ax.set_ylabel('归一化幅值', fontsize=12)
    ax.set_title('频率响应函数', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case10_modal_analysis.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case10_modal_analysis.png")
    
    return tower


def demo_wind_excitation(tower):
    """演示2: 风载荷激励响应"""
    print("\n" + "=" * 60)
    print("演示2: 风载荷激励下的塔架响应")
    print("=" * 60)
    
    t = np.linspace(0, 100, 10000)
    dt = t[1] - t[0]
    
    # 模拟脉动风载荷（简化）
    F_mean = 1e5  # 平均风载荷 (N)
    F_turb = np.random.randn(len(t)) * 2e4  # 脉动分量
    
    # 添加1P和3P频率分量（叶片通过频率）
    omega_rotor = 1.0  # rad/s
    f_1P = omega_rotor / (2*np.pi)
    f_3P = 3 * f_1P
    
    F_1P = 3e4 * np.sin(2*np.pi*f_1P*t)
    F_3P = 1e4 * np.sin(2*np.pi*f_3P*t)
    
    F_total = F_mean + F_turb + F_1P + F_3P
    
    print(f"\n风载荷特性:")
    print(f"  平均载荷: {F_mean/1e3:.0f} kN")
    print(f"  1P频率: {f_1P:.3f} Hz")
    print(f"  3P频率: {f_3P:.3f} Hz")
    print(f"  塔架固有频率: {tower.f_n:.3f} Hz")
    
    # 计算响应
    print(f"\n计算振动响应...")
    x = tower.response(t, F_total)
    
    # 统计
    x_max = np.max(np.abs(x))
    x_rms = np.sqrt(np.mean(x**2))
    
    print(f"\n响应统计:")
    print(f"  最大位移: {x_max:.3f} m")
    print(f"  RMS位移: {x_rms:.3f} m")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 风载荷时程
    ax = axes[0, 0]
    ax.plot(t[:1000], F_total[:1000]/1e3, 'b-', linewidth=0.5)
    ax.set_ylabel('风载荷 (kN)', fontsize=12)
    ax.set_title('风载荷时程（前10s）', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 位移响应
    ax = axes[0, 1]
    ax.plot(t[:1000], x[:1000], 'r-', linewidth=0.8)
    ax.set_ylabel('位移 (m)', fontsize=12)
    ax.set_title('位移响应（前10s）', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 载荷频谱
    ax = axes[1, 0]
    fft_F = np.fft.fft(F_total)
    freq = np.fft.fftfreq(len(t), dt)
    ax.semilogy(freq[:len(freq)//2], np.abs(fft_F[:len(freq)//2]), 'b-', linewidth=0.8)
    ax.axvline(f_1P, color='r', linestyle='--', label=f'1P({f_1P:.3f}Hz)')
    ax.axvline(f_3P, color='g', linestyle='--', label=f'3P({f_3P:.3f}Hz)')
    ax.axvline(tower.f_n, color='purple', linestyle='--', label=f'塔架({tower.f_n:.3f}Hz)')
    ax.set_xlabel('频率 (Hz)', fontsize=12)
    ax.set_ylabel('幅值', fontsize=12)
    ax.set_title('载荷频谱', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 2)
    
    # 响应频谱
    ax = axes[1, 1]
    fft_x = np.fft.fft(x)
    ax.semilogy(freq[:len(freq)//2], np.abs(fft_x[:len(freq)//2]), 'r-', linewidth=0.8)
    ax.axvline(tower.f_n, color='purple', linestyle='--', label=f'固有频率({tower.f_n:.3f}Hz)')
    ax.set_xlabel('频率 (Hz)', fontsize=12)
    ax.set_ylabel('幅值', fontsize=12)
    ax.set_title('响应频谱', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 2)
    
    plt.tight_layout()
    plt.savefig('case10_wind_excitation.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case10_wind_excitation.png")


def demo_fatigue_analysis():
    """演示3: 疲劳分析"""
    print("\n" + "=" * 60)
    print("演示3: 塔架疲劳载荷分析")
    print("=" * 60)
    
    # 雨流计数法简化示例
    # 生成随机应力时程
    t = np.linspace(0, 1000, 10000)
    stress = 50 + 30*np.sin(2*np.pi*0.2*t) + 10*np.random.randn(len(t))
    
    # 统计应力范围
    stress_ranges = np.abs(np.diff(stress))
    
    # 统计直方图
    bins = np.linspace(0, 100, 20)
    hist, edges = np.histogram(stress_ranges, bins=bins)
    
    # S-N曲线（Wöhler曲线）
    S_range = np.linspace(10, 100, 50)
    m = 3  # 疲劳指数
    C = 1e12  # 材料常数
    N_cycles = C / S_range**m
    
    print(f"\n疲劳分析:")
    print(f"  应力范围: {stress_ranges.min():.1f} - {stress_ranges.max():.1f} MPa")
    print(f"  平均应力范围: {stress_ranges.mean():.1f} MPa")
    print(f"  S-N曲线参数: m={m}, C={C:.1e}")
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 应力时程
    ax = axes[0]
    ax.plot(t[:500], stress[:500], 'b-', linewidth=0.8)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('应力 (MPa)', fontsize=12)
    ax.set_title('应力时程', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 应力范围分布
    ax = axes[1]
    ax.bar(edges[:-1], hist, width=np.diff(edges), alpha=0.7, edgecolor='black')
    ax.set_xlabel('应力范围 (MPa)', fontsize=12)
    ax.set_ylabel('计数', fontsize=12)
    ax.set_title('应力范围分布', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # S-N曲线
    ax = axes[2]
    ax.loglog(N_cycles, S_range, 'r-', linewidth=2)
    ax.set_xlabel('循环次数 N', fontsize=12)
    ax.set_ylabel('应力范围 S (MPa)', fontsize=12)
    ax.set_title('S-N疲劳曲线', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig('case10_fatigue_analysis.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case10_fatigue_analysis.png")


def main():
    print("\n" + "=" * 60)
    print("案例10: 塔架振动")
    print("=" * 60)
    
    tower = demo_modal_analysis()
    demo_wind_excitation(tower)
    demo_fatigue_analysis()
    
    print("\n" + "=" * 60)
    print("案例10 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case10_modal_analysis.png")
    print("  2. case10_wind_excitation.png")
    print("  3. case10_fatigue_analysis.png")
    
    print("\n核心知识点:")
    print("  ✓ 塔架模态分析")
    print("  ✓ 风载荷激励")
    print("  ✓ 振动响应计算")
    print("  ✓ 疲劳分析基础")
    
    plt.show()


if __name__ == "__main__":
    main()
