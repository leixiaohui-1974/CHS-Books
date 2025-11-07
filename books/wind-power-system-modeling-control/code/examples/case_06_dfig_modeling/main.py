"""
案例6: DFIG建模

本案例演示:
1. DFIG稳态特性（转差率-功率曲线）
2. DFIG等效电路分析
3. 转矩-转速特性
4. 次同步/超同步运行

工程背景: 双馈风力发电机原理
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.generator import DFIGModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_dfig_characteristics():
    """演示1: DFIG特性曲线"""
    print("=" * 60)
    print("演示1: DFIG稳态特性曲线")
    print("=" * 60)
    
    dfig = DFIGModel(
        P_rated=2e6,
        V_rated=690,
        poles=4,
        Rs=0.01,
        Rr=0.01,
        Lm=3.0,
        Lls=0.1,
        Llr=0.1
    )
    
    print(f"\nDFIG参数:")
    print(f"  额定功率: {dfig.P_rated/1e6:.1f} MW")
    print(f"  额定电压: {dfig.V_rated} V")
    print(f"  极对数: {dfig.poles}")
    print(f"  同步转速: {dfig.n_sync:.0f} RPM")
    print(f"  同步角速度: {dfig.omega_s:.2f} rad/s")
    
    # 转差率范围
    s_range = np.linspace(-0.3, 0.3, 100)
    
    Ps_vals = []
    Te_vals = []
    omega_rpm_vals = []
    
    print(f"\n计算稳态特性...")
    for s in s_range:
        result = dfig.steady_state(s)
        Ps_vals.append(result['Ps'] / 1e6)  # MW
        Te_vals.append(result['Te'] / 1e3)   # kN*m
        omega_rpm_vals.append(result['omega_r'] * 60 / (2*np.pi) * 2 / dfig.poles)
    
    # 关键点
    idx_sync = np.argmin(np.abs(s_range))
    idx_rated = np.argmin(np.abs(s_range + 0.03))  # s=-0.03 (超同步)
    
    print(f"\n关键运行点:")
    print(f"  同步点 (s=0): P={Ps_vals[idx_sync]:.2f}MW, Te={Te_vals[idx_sync]:.1f}kN*m")
    print(f"  额定点 (s=-0.03): P={Ps_vals[idx_rated]:.2f}MW, Te={Te_vals[idx_rated]:.1f}kN*m")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 功率-转差率
    ax = axes[0, 0]
    ax.plot(s_range, Ps_vals, 'b-', linewidth=2)
    ax.axvline(0, color='r', linestyle='--', label='同步点')
    ax.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax.fill_between(s_range, 0, Ps_vals, where=(np.array(s_range)<0), alpha=0.2, color='green', label='发电')
    ax.fill_between(s_range, 0, Ps_vals, where=(np.array(s_range)>0), alpha=0.2, color='red', label='电动')
    ax.set_xlabel('转差率 s', fontsize=12)
    ax.set_ylabel('定子功率 (MW)', fontsize=12)
    ax.set_title('功率-转差率特性', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 转矩-转差率
    ax = axes[0, 1]
    ax.plot(s_range, Te_vals, 'r-', linewidth=2)
    ax.axvline(0, color='g', linestyle='--')
    ax.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax.set_xlabel('转差率 s', fontsize=12)
    ax.set_ylabel('电磁转矩 (kN·m)', fontsize=12)
    ax.set_title('转矩-转差率特性', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 转矩-转速
    ax = axes[1, 0]
    ax.plot(omega_rpm_vals, Te_vals, 'g-', linewidth=2)
    ax.axvline(dfig.n_sync, color='r', linestyle='--', label=f'同步({dfig.n_sync:.0f}RPM)')
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('电磁转矩 (kN·m)', fontsize=12)
    ax.set_title('转矩-转速特性', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 功率-转速
    ax = axes[1, 1]
    ax.plot(omega_rpm_vals, Ps_vals, 'purple', linewidth=2)
    ax.axvline(dfig.n_sync, color='r', linestyle='--', label='同步转速')
    ax.axhline(dfig.P_rated/1e6, color='g', linestyle='--', label='额定功率')
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('定子功率 (MW)', fontsize=12)
    ax.set_title('功率-转速特性', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case06_dfig_characteristics.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case06_dfig_characteristics.png")


def demo_operating_modes():
    """演示2: DFIG运行模式"""
    print("\n" + "=" * 60)
    print("演示2: DFIG次同步/超同步运行模式")
    print("=" * 60)
    
    dfig = DFIGModel()
    
    # 三种运行模式
    modes = [
        ("次同步", 0.05, 1425),   # s>0, 低于同步速度
        ("同步", 0.0, 1500),       # s=0
        ("超同步", -0.05, 1575),  # s<0, 高于同步速度
    ]
    
    print(f"\n同步转速: {dfig.n_sync:.0f} RPM")
    print(f"\n不同运行模式分析:")
    print("-" * 60)
    
    results = []
    for name, s, rpm in modes:
        result = dfig.steady_state(s)
        results.append(result)
        
        print(f"\n{name}运行 (s={s:+.3f}):")
        print(f"  转速: {rpm} RPM")
        print(f"  定子功率: {result['Ps']/1e6:+.3f} MW")
        print(f"  转子功率: {-s*result['Ps']/1e6:+.3f} MW")
        print(f"  电磁转矩: {result['Te']/1e3:+.2f} kN·m")
        print(f"  功率流向: ", end="")
        if s > 0:
            print("转子吸收功率（次同步）")
        elif s < 0:
            print("转子释放功率（超同步）")
        else:
            print("转子无功率交换（同步）")
    
    # 可视化运行模式
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, (name, s, rpm) in enumerate(modes):
        ax = axes[i]
        result = results[i]
        
        Ps = result['Ps'] / 1e6
        Pr = -s * Ps
        Pm = Ps + Pr
        
        # 功率流向图
        components = ['机械功率', '定子功率', '转子功率']
        values = [Pm, Ps, Pr]
        colors = ['blue', 'green', 'red']
        
        bars = ax.barh(components, values, color=colors, alpha=0.7)
        ax.axvline(0, color='k', linewidth=0.5)
        
        # 添加数值标签
        for bar, val in zip(bars, values):
            x_pos = val + 0.05 if val > 0 else val - 0.05
            ax.text(x_pos, bar.get_y() + bar.get_height()/2, 
                   f'{val:+.2f}MW', va='center',
                   ha='left' if val > 0 else 'right')
        
        ax.set_xlabel('功率 (MW)', fontsize=11)
        ax.set_title(f'{name}运行\n(s={s:+.2f}, n={rpm}RPM)', 
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('case06_operating_modes.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case06_operating_modes.png")


def demo_speed_range():
    """演示3: DFIG变速范围"""
    print("\n" + "=" * 60)
    print("演示3: DFIG变速范围与转子功率")
    print("=" * 60)
    
    dfig = DFIGModel(P_rated=2e6)
    
    # 典型DFIG: ±30%变速范围
    s_min, s_max = -0.3, 0.3
    n_min = dfig.n_sync * (1 - s_max)
    n_max = dfig.n_sync * (1 - s_min)
    
    print(f"\nDFIG变速范围:")
    print(f"  同步转速: {dfig.n_sync:.0f} RPM")
    print(f"  最低转速: {n_min:.0f} RPM ({(1-s_max)*100:.0f}%)")
    print(f"  最高转速: {n_max:.0f} RPM ({(1-s_min)*100:.0f}%)")
    print(f"  变速范围: ±{abs(s_max)*100:.0f}%")
    
    # 不同功率水平下的转子功率
    P_levels = [0.25, 0.5, 0.75, 1.0]  # pu
    s_range = np.linspace(-0.3, 0.3, 50)
    
    print(f"\n转子功率需求:")
    print(f"{'定子功率(pu)':<15}{'次同步(s=0.3)':<20}{'超同步(s=-0.3)':<20}")
    print("-" * 55)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 转子功率
    ax = axes[0]
    for P_level in P_levels:
        Pr_vals = []
        for s in s_range:
            Ps = P_level * dfig.P_rated
            Pr = -s * Ps
            Pr_vals.append(Pr / dfig.P_rated)  # pu
        
        ax.plot(s_range, Pr_vals, linewidth=2, label=f'Ps={P_level}pu')
        
        # 打印关键点
        Pr_sub = 0.3 * P_level
        Pr_super = -0.3 * P_level
        print(f"{P_level:<15.2f}{Pr_sub:+.3f}pu ({Pr_sub*dfig.P_rated/1e6:+.2f}MW)<20"
              f"{Pr_super:+.3f}pu ({Pr_super*dfig.P_rated/1e6:+.2f}MW)")
    
    ax.axhline(0, color='k', linewidth=0.5)
    ax.axvline(0, color='r', linestyle='--', alpha=0.5)
    ax.fill_between(s_range, -0.3, 0.3, alpha=0.1, color='gray')
    ax.set_xlabel('转差率 s', fontsize=12)
    ax.set_ylabel('转子功率 (pu)', fontsize=12)
    ax.set_title('转子功率需求', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.35, 0.35)
    
    # 变流器容量
    ax = axes[1]
    Pr_max = []
    n_range = np.linspace(n_min, n_max, 50)
    s_vals = 1 - n_range / dfig.n_sync
    
    for P_level in P_levels:
        Pr_max_level = [abs(s) * P_level for s in s_vals]
        ax.plot(n_range, Pr_max_level, linewidth=2, label=f'Ps={P_level}pu')
    
    ax.axvline(dfig.n_sync, color='r', linestyle='--', label='同步转速')
    ax.set_xlabel('转速 (RPM)', fontsize=12)
    ax.set_ylabel('转子功率 (pu)', fontsize=12)
    ax.set_title('变流器容量需求', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case06_speed_range.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case06_speed_range.png")
    
    print(f"\n变流器容量: {abs(s_max)*100:.0f}% × 额定功率 = {abs(s_max)*dfig.P_rated/1e6:.1f} MW")


def main():
    print("\n" + "=" * 60)
    print("案例6: DFIG建模")
    print("=" * 60)
    
    demo_dfig_characteristics()
    demo_operating_modes()
    demo_speed_range()
    
    print("\n" + "=" * 60)
    print("案例6 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case06_dfig_characteristics.png")
    print("  2. case06_operating_modes.png")
    print("  3. case06_speed_range.png")
    
    print("\n核心知识点:")
    print("  ✓ DFIG工作原理")
    print("  ✓ 次同步/超同步运行")
    print("  ✓ 转差率-功率关系")
    print("  ✓ 变流器容量需求")
    
    plt.show()


if __name__ == "__main__":
    main()
