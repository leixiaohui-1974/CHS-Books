#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管道沿程阻力损失计算

知识点：
1. 达西-魏斯巴赫公式：hf = λ(L/d)(v²/2g)
2. 雷诺数：Re = vd/ν
3. 尼库拉兹公式
4. Colebrook公式

作者：CHS-Books项目组
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def reynolds_number(v, d, nu=1e-6):
    """雷诺数"""
    return v * d / nu

def friction_factor_laminar(Re):
    """层流：λ = 64/Re"""
    return 64 / Re

def friction_factor_turbulent_smooth(Re):
    """紊流光滑管：尼库拉兹公式"""
    if Re < 1e5:
        return 0.3164 / Re**0.25
    else:
        return 0.0032 + 0.221 / Re**0.237

def darcy_weisbach(L, d, v, lambda_, g=9.81):
    """达西公式：hf = λ(L/d)(v²/2g)"""
    return lambda_ * (L / d) * (v**2 / (2 * g))

def plot_moody_diagram(filename='pipe_friction_loss.png'):
    """绘制Moody图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：λ-Re关系
    ax1 = axes[0, 0]
    Re_range = np.logspace(2, 6, 100)
    lambda_vals = []
    
    for Re in Re_range:
        if Re < 2000:
            lam = friction_factor_laminar(Re)
        else:
            lam = friction_factor_turbulent_smooth(Re)
        lambda_vals.append(lam)
    
    ax1.loglog(Re_range, lambda_vals, 'b-', linewidth=2)
    ax1.axvline(2000, color='r', linestyle='--', label='Re=2000（层流/紊流分界）')
    ax1.set_xlabel('雷诺数 Re', fontsize=12)
    ax1.set_ylabel('沿程阻力系数 λ', fontsize=12)
    ax1.set_title('λ-Re关系（Moody图简化）', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, which='both')
    
    # 子图2：损失计算示例
    ax2 = axes[0, 1]
    L = 100  # 管长
    d = 0.2  # 管径
    v_range = np.linspace(0.5, 3, 20)
    hf_vals = []
    
    for v in v_range:
        Re = reynolds_number(v, d)
        if Re < 2000:
            lam = friction_factor_laminar(Re)
        else:
            lam = friction_factor_turbulent_smooth(Re)
        hf = darcy_weisbach(L, d, v, lam)
        hf_vals.append(hf)
    
    ax2.plot(v_range, hf_vals, 'g-', linewidth=2)
    ax2.set_xlabel('流速 v (m/s)', fontsize=12)
    ax2.set_ylabel('水头损失 hf (m)', fontsize=12)
    ax2.set_title(f'沿程损失vs流速（L={L}m, d={d}m）', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：层流vs紊流
    ax3 = axes[1, 0]
    Re_compare = [1000, 5000, 50000]
    lambda_compare = []
    labels_compare = []
    
    for Re in Re_compare:
        if Re < 2000:
            lam = friction_factor_laminar(Re)
            regime = '层流'
        else:
            lam = friction_factor_turbulent_smooth(Re)
            regime = '紊流'
        lambda_compare.append(lam)
        labels_compare.append(f'Re={Re}\n{regime}')
    
    ax3.bar(labels_compare, lambda_compare, color=['blue', 'green', 'red'], alpha=0.7)
    ax3.set_ylabel('λ', fontsize=12)
    ax3.set_title('不同Re下的λ值', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 子图4：计算结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    v_example = 2.0
    Re_ex = reynolds_number(v_example, d)
    lam_ex = friction_factor_turbulent_smooth(Re_ex)
    hf_ex = darcy_weisbach(L, d, v_example, lam_ex)
    
    info = f"""
    【管道沿程损失计算示例】
    
    管道参数：
      长度 L = {L} m
      直径 d = {d} m
      流速 v = {v_example} m/s
    
    流态判别：
      雷诺数 Re = vd/ν
                = {Re_ex:.0f}
      Re > 2000 → 紊流 ✓
    
    阻力系数：
      λ = 0.3164/Re^0.25
        = {lam_ex:.4f}
    
    沿程损失：
      hf = λ(L/d)(v²/2g)
         = {lam_ex:.4f}×({L}/{d})×({v_example}²/19.62)
         = {hf_ex:.3f} m
    
    公式总结：
      达西公式：hf = λ(L/d)(v²/2g)
      层流：λ = 64/Re
      紊流：λ = 0.3164/Re^0.25（Re<10⁵）
    """
    
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("管道沿程阻力损失计算")
    print("="*60)
    
    L = 100
    d = 0.2
    v = 2.0
    
    Re = reynolds_number(v, d)
    print(f"\n参数：L={L}m, d={d}m, v={v}m/s")
    print(f"雷诺数：Re={Re:.0f}")
    
    if Re < 2000:
        lam = friction_factor_laminar(Re)
        print("流态：层流")
    else:
        lam = friction_factor_turbulent_smooth(Re)
        print("流态：紊流")
    
    hf = darcy_weisbach(L, d, v, lam)
    print(f"阻力系数：λ={lam:.4f}")
    print(f"沿程损失：hf={hf:.3f}m")
    
    plot_moody_diagram()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
