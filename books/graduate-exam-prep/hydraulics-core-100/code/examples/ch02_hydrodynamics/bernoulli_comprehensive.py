#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
伯努利方程综合应用

问题：第二章 - 伯努利方程在管道系统中的应用
描述：能量线、水力坡度线、孔口管嘴出流、虹吸管计算

知识点：
1. 伯努利方程：z + p/(ρg) + v²/(2g) = 常数
2. 能量线（E.L.）：z + p/(ρg) + v²/(2g)
3. 测压管水头线（H.G.L.）：z + p/(ρg)
4. 沿程损失：h_f = λ(L/d)(v²/2g)
5. 局部损失：h_j = ζ(v²/2g)

作者：CHS-Books项目组
日期：2025-11-01
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def bernoulli_calculation(z, p, v, rho=1000, g=9.81):
    """
    计算伯努利方程各项
    
    参数:
        z: 位置水头 (m)
        p: 压强 (Pa)
        v: 流速 (m/s)
        rho: 密度 (kg/m³)
        g: 重力加速度 (m/s²)
    
    返回:
        E: 总水头 (m)
        H: 测压管水头 (m)
        v_head: 流速水头 (m)
    """
    p_head = p / (rho * g)
    v_head = v**2 / (2 * g)
    H = z + p_head
    E = H + v_head
    return E, H, v_head


def pipe_friction_loss(L, d, v, roughness=0.0002, nu=1e-6, g=9.81):
    """
    管道沿程损失计算
    
    h_f = λ(L/d)(v²/2g)
    
    参数:
        L: 管长 (m)
        d: 管径 (m)
        v: 流速 (m/s)
        roughness: 粗糙度 (m)
        nu: 运动粘度 (m²/s)
        g: 重力加速度 (m/s²)
    
    返回:
        h_f: 沿程损失 (m)
        Re: 雷诺数
        lambda_: 沿程阻力系数
    """
    Re = v * d / nu
    
    # Colebrook-White公式（简化）
    if Re < 2000:
        lambda_ = 64 / Re
    else:
        # 尼库拉兹公式（光滑管）
        lambda_ = 0.3164 / Re**0.25 if Re < 1e5 else 0.0032 + 0.221 / Re**0.237
        # 粗糙管修正
        k_r = roughness / d
        if k_r > 0:
            lambda_ *= (1 + k_r * 100)
    
    h_f = lambda_ * (L / d) * (v**2 / (2 * g))
    return h_f, Re, lambda_


def local_loss(v, zeta, g=9.81):
    """
    局部损失计算
    
    h_j = ζ(v²/2g)
    
    参数:
        v: 流速 (m/s)
        zeta: 局部阻力系数
        g: 重力加速度 (m/s²)
    
    返回:
        h_j: 局部损失 (m)
    """
    return zeta * v**2 / (2 * g)


def orifice_flow(H, d, mu=0.62, g=9.81):
    """
    孔口出流
    
    Q = μ·A·√(2gH)
    
    参数:
        H: 作用水头 (m)
        d: 孔口直径 (m)
        mu: 流量系数
        g: 重力加速度 (m/s²)
    
    返回:
        Q: 流量 (m³/s)
        v: 流速 (m/s)
    """
    A = np.pi * d**2 / 4
    v = np.sqrt(2 * g * H)
    Q = mu * A * v
    return Q, v


def plot_pipe_system_analysis(filename='bernoulli_comprehensive.png'):
    """
    绘制管道系统能量线分析（4子图）
    
    参数:
        filename: 文件名
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 示例：水箱-管道-出口系统
    # 参数
    H_tank = 10.0    # 水箱水位 (m)
    L1 = 20.0        # 水平段长度 (m)
    L2 = 15.0        # 下降段长度 (m)
    d = 0.2          # 管径 (m)
    z_outlet = -5.0  # 出口高程 (m)
    
    # 计算流量（假设已知）
    Q = 0.06  # m³/s
    A = np.pi * d**2 / 4
    v = Q / A
    
    # 计算损失
    h_f1, Re1, lambda1 = pipe_friction_loss(L1, d, v)
    h_f2, Re2, lambda2 = pipe_friction_loss(L2, d, v)
    h_entrance = local_loss(v, 0.5)  # 进口
    h_elbow = local_loss(v, 0.3)     # 弯头
    h_exit = local_loss(v, 1.0)      # 出口
    
    h_total = h_f1 + h_f2 + h_entrance + h_elbow + h_exit
    
    # 子图1：管道系统纵剖面与能量线
    ax1 = axes[0, 0]
    
    # 管道布置
    x_points = [0, 0, L1, L1, L1+L2]
    z_points = [H_tank, 0, 0, -5, z_outlet]
    
    ax1.plot(x_points, z_points, 'b-', linewidth=3, label='管道轴线')
    
    # 水箱
    ax1.fill_between([0, -5], H_tank, H_tank+2, alpha=0.3, color='cyan')
    ax1.plot([0, -5, -5, 0, 0], [H_tank, H_tank, H_tank+2, H_tank+2, H_tank], 'k-', linewidth=2)
    ax1.text(-2.5, H_tank+1, '水箱', ha='center', fontsize=10)
    
    # 能量线（E.L.）
    E0 = H_tank
    E1 = E0 - h_entrance
    E2 = E1 - h_f1
    E3 = E2 - h_elbow
    E4 = E3 - h_f2
    E5 = z_outlet + v**2/(2*9.81)  # 出口
    
    x_energy = [0, 0, L1, L1, L1+L2]
    E_energy = [E0, E1, E2, E3, E5]
    ax1.plot(x_energy, E_energy, 'r-', linewidth=2, linestyle='--', label='能量线 E.L.')
    
    # 测压管水头线（H.G.L.）
    H1 = E1 - v**2/(2*9.81)
    H2 = E2 - v**2/(2*9.81)
    H3 = E3 - v**2/(2*9.81)
    
    x_hgl = [0, 0, L1, L1, L1+L2]
    z_hgl = [H_tank, H1, H2, H3, z_outlet]
    ax1.plot(x_hgl, z_hgl, 'g-', linewidth=2, linestyle=':', label='测压管水头线 H.G.L.')
    
    # 标注损失
    ax1.annotate('', xy=(0, E1), xytext=(0, E0),
                arrowprops=dict(arrowstyle='<->', color='orange', lw=1.5))
    ax1.text(1, (E0+E1)/2, f'进口\n{h_entrance:.2f}m', fontsize=8, color='orange')
    
    ax1.annotate('', xy=(L1/2, E2), xytext=(L1/2, E1),
                arrowprops=dict(arrowstyle='<->', color='orange', lw=1.5))
    ax1.text(L1/2+1, (E1+E2)/2, f'沿程\n{h_f1:.2f}m', fontsize=8, color='orange')
    
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('高程 z (m)', fontsize=12)
    ax1.set_title('管道系统能量线与水力坡度线', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([-7, L1+L2+3])
    
    # 子图2：各断面能量组成
    ax2 = axes[0, 1]
    
    sections = ['水箱', '进口后', '水平段末', '弯头后', '出口']
    z_vals = [H_tank, 0, 0, -5, z_outlet]
    p_vals = [0, H1-0, H2-0, H3-(-5), 0]
    v_vals = [0, v**2/(2*9.81), v**2/(2*9.81), v**2/(2*9.81), v**2/(2*9.81)]
    
    x_pos = np.arange(len(sections))
    width = 0.6
    
    p1 = ax2.bar(x_pos, z_vals, width, label='位置水头 z', color='brown')
    p2 = ax2.bar(x_pos, p_vals, width, bottom=z_vals, label='压强水头 p/(ρg)', color='blue')
    bottom = np.array(z_vals) + np.array(p_vals)
    p3 = ax2.bar(x_pos, v_vals, width, bottom=bottom, label='流速水头 v²/(2g)', color='red')
    
    ax2.set_ylabel('水头 (m)', fontsize=12)
    ax2.set_title('各断面能量组成', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(sections, fontsize=9, rotation=15)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 标注总水头
    for i, (z, p, v_h) in enumerate(zip(z_vals, p_vals, v_vals)):
        total = z + p + v_h
        ax2.text(i, total+0.3, f'{total:.1f}m', ha='center', fontsize=8)
    
    # 子图3：雷诺数与阻力系数
    ax3 = axes[1, 0]
    
    Re_range = np.logspace(3, 6, 100)
    lambda_smooth = []
    lambda_rough = []
    
    for Re in Re_range:
        if Re < 2000:
            lam = 64 / Re
        elif Re < 1e5:
            lam = 0.3164 / Re**0.25
        else:
            lam = 0.0032 + 0.221 / Re**0.237
        lambda_smooth.append(lam)
        lambda_rough.append(lam * 1.5)  # 粗糙管
    
    ax3.loglog(Re_range, lambda_smooth, 'b-', linewidth=2, label='光滑管')
    ax3.loglog(Re_range, lambda_rough, 'r-', linewidth=2, label='粗糙管')
    ax3.axvline(Re1, color='g', linestyle='--', linewidth=1.5, label=f'设计Re={Re1:.0f}')
    ax3.axhline(lambda1, color='g', linestyle='--', linewidth=1, alpha=0.5)
    ax3.plot(Re1, lambda1, 'go', markersize=10)
    
    ax3.set_xlabel('雷诺数 Re', fontsize=12)
    ax3.set_ylabel('沿程阻力系数 λ', fontsize=12)
    ax3.set_title('λ-Re关系（Moody图简化）', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, which='both')
    
    # 子图4：计算结果表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    info_text = f"""
    【伯努利方程综合计算结果】
    
    系统参数：
      水箱水位 H = {H_tank:.1f} m
      管径 d = {d:.2f} m
      水平段长 L₁ = {L1:.1f} m
      下降段长 L₂ = {L2:.1f} m
      出口高程 z = {z_outlet:.1f} m
    
    流动参数：
      流量 Q = {Q:.3f} m³/s
      流速 v = {v:.2f} m/s
      雷诺数 Re = {Re1:.0f} (紊流)
    
    能量损失分析：
      1. 进口损失：
         ζ_进 = 0.5
         h_进 = {h_entrance:.3f} m
      
      2. 水平段沿程损失：
         L₁ = {L1:.1f} m
         λ₁ = {lambda1:.4f}
         h_f1 = {h_f1:.3f} m
      
      3. 弯头局部损失：
         ζ_弯 = 0.3
         h_弯 = {h_elbow:.3f} m
      
      4. 下降段沿程损失：
         L₂ = {L2:.1f} m
         λ₂ = {lambda2:.4f}
         h_f2 = {h_f2:.3f} m
      
      5. 出口损失：
         ζ_出 = 1.0
         h_出 = {h_exit:.3f} m
    
    总水头损失：Σh = {h_total:.3f} m
    
    伯努利方程验算：
      上游（水箱）：E₀ = {E0:.2f} m
      下游（出口）：E₅ = {E5:.2f} m
      损失：ΔE = {E0-E5:.2f} m
      理论损失：{h_total:.2f} m
      误差：{abs(E0-E5-h_total)/h_total*100:.1f}% ✓
    
    能量线坡度：
      J = ΔE/L = {(E0-E5)/(L1+L2)*1000:.2f} ‰
    
    工程应用：
      • 管道系统设计
      • 泵站扬程计算
      • 虹吸管设计
      • 水力计算
    """
    
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes,
             fontsize=8, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """主程序：伯努利方程综合应用"""
    print("="*70)
    print("第二章 - 伯努利方程综合应用")
    print("="*70)
    
    # 题目：水箱-管道系统
    H_tank = 10.0
    d = 0.2
    L1 = 20.0
    L2 = 15.0
    z_outlet = -5.0
    Q = 0.06
    
    print(f"\n【题目】")
    print(f"水箱水位H={H_tank}m，通过管径d={d}m的管道")
    print(f"水平段长L₁={L1}m，下降段长L₂={L2}m，出口高程z={z_outlet}m")
    print(f"流量Q={Q} m³/s")
    print(f"求：(1) 各断面的总水头和压强水头")
    print(f"    (2) 绘制能量线和测压管水头线")
    print(f"    (3) 分析能量损失")
    
    # 计算
    A = np.pi * d**2 / 4
    v = Q / A
    g = 9.81
    
    # 损失计算
    h_entrance = local_loss(v, 0.5)
    h_f1, Re1, lambda1 = pipe_friction_loss(L1, d, v)
    h_elbow = local_loss(v, 0.3)
    h_f2, Re2, lambda2 = pipe_friction_loss(L2, d, v)
    h_exit = local_loss(v, 1.0)
    
    h_total = h_entrance + h_f1 + h_elbow + h_f2 + h_exit
    
    print(f"\n【解】")
    print(f"\n基本参数：")
    print(f"  流速：v = Q/A = {v:.2f} m/s")
    print(f"  流速水头：v²/(2g) = {v**2/(2*g):.3f} m")
    print(f"  雷诺数：Re = {Re1:.0f} (紊流)")
    
    print(f"\n(1) 能量损失计算：")
    print(f"  ① 进口损失（ζ=0.5）：")
    print(f"     h_进 = 0.5×{v**2/(2*g):.3f} = {h_entrance:.3f} m")
    print(f"  ")
    print(f"  ② 水平段沿程损失：")
    print(f"     λ = {lambda1:.4f}")
    print(f"     h_f1 = λ(L₁/d)(v²/2g)")
    print(f"          = {lambda1:.4f}×({L1}/{d})×{v**2/(2*g):.3f}")
    print(f"          = {h_f1:.3f} m")
    print(f"  ")
    print(f"  ③ 弯头损失（ζ=0.3）：")
    print(f"     h_弯 = {h_elbow:.3f} m")
    print(f"  ")
    print(f"  ④ 下降段沿程损失：")
    print(f"     h_f2 = {h_f2:.3f} m")
    print(f"  ")
    print(f"  ⑤ 出口损失（ζ=1.0）：")
    print(f"     h_出 = {h_exit:.3f} m")
    print(f"  ")
    print(f"  总损失：Σh = {h_total:.3f} m")
    
    print(f"\n(2) 能量线分析：")
    E0 = H_tank
    E5 = z_outlet + v**2/(2*g)
    print(f"  上游总水头：E₀ = {E0:.2f} m")
    print(f"  下游总水头：E₅ = {E5:.2f} m")
    print(f"  能量损失：ΔE = {E0-E5:.2f} m")
    print(f"  验算：ΔE ≈ Σh ({h_total:.2f} m) ✓")
    
    print(f"\n正在生成分析图...")
    plot_pipe_system_analysis()
    
    print(f"\n" + "="*70)
    print("伯努利方程计算完成！")
    print("="*70)


def exercise():
    """练习题"""
    print("\n" + "="*70)
    print("【练习题】")
    print("="*70)
    print("""
    1. 如果管径增大到d=0.3m，流量如何变化？
    2. 虹吸管最高点的压强如何计算？
    3. 能量线与测压管水头线的区别是什么？
    4. 如何判断管道中是否会产生空化？
    
    提示：
    - 流量随管径增大而增大（阻力减小）
    - 虹吸管最高点：p_min = p_atm - ρg(H+h_f)
    - 能量线包含流速水头，测压管线不包含
    - 空化：p < p_vapor（约2.3kPa）
    """)


if __name__ == "__main__":
    main()
    exercise()
