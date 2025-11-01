#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Colebrook公式迭代求解摩阻系数"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def colebrook_iteration(Re, epsilon_d, tol=1e-6, max_iter=50):
    """1/√λ = -2log₁₀(ε/(3.7d) + 2.51/(Re√λ))"""
    # 初始猜测：Haaland公式
    lambda_old = 1 / (-1.8*np.log10((epsilon_d/3.7)**1.11 + 6.9/Re))**2
    
    history = [lambda_old]
    for i in range(max_iter):
        sqrt_lambda = np.sqrt(lambda_old)
        lambda_new = 1 / (-2*np.log10(epsilon_d/3.7 + 2.51/(Re*sqrt_lambda)))**2
        history.append(lambda_new)
        
        if abs(lambda_new - lambda_old) < tol:
            return lambda_new, i+1, history
        lambda_old = lambda_new
    
    return lambda_old, max_iter, history

def plot_colebrook(filename='colebrook_iteration.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    Re, eps_d = 1e5, 0.001
    lambda_final, n_iter, history = colebrook_iteration(Re, eps_d)
    
    # 子图1：迭代收敛
    ax1 = axes[0, 0]
    ax1.plot(range(len(history)), history, 'bo-', linewidth=2, markersize=6)
    ax1.axhline(lambda_final, color='r', linestyle='--', linewidth=1.5, label=f'收敛值={lambda_final:.6f}')
    ax1.set_xlabel('迭代次数', fontsize=12)
    ax1.set_ylabel('摩阻系数 λ', fontsize=12)
    ax1.set_title(f'Colebrook迭代收敛（{n_iter}次）', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：λ vs Re（不同粗糙度）
    ax2 = axes[0, 1]
    Re_range = np.logspace(4, 7, 50)
    for eps in [0.0001, 0.001, 0.01]:
        lambdas = [colebrook_iteration(re, eps)[0] for re in Re_range]
        ax2.semilogx(Re_range, lambdas, linewidth=2, label=f'ε/d={eps}')
    ax2.set_xlabel('Reynolds数 Re', fontsize=12)
    ax2.set_ylabel('摩阻系数 λ', fontsize=12)
    ax2.set_title('Moody图（Colebrook曲线族）', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, which='both')
    
    # 子图3：迭代误差
    ax3 = axes[1, 0]
    errors = [abs(history[i+1]-history[i]) for i in range(len(history)-1)]
    ax3.semilogy(range(len(errors)), errors, 'ro-', linewidth=2, markersize=5)
    ax3.set_xlabel('迭代次数', fontsize=12)
    ax3.set_ylabel('|λₙ₊₁ - λₙ|', fontsize=12)
    ax3.set_title('迭代误差下降', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    # 对比计算
    lambda_haaland = 1 / (-1.8*np.log10((eps_d/3.7)**1.11 + 6.9/Re))**2
    lambda_swamee = 0.25 / (np.log10(eps_d/3.7 + 5.74/Re**0.9))**2
    
    info = f"""
    【Colebrook公式迭代】
    
    参数：
      Re = {Re:.0e}
      ε/d = {eps_d}
    
    迭代结果：
      λ = {lambda_final:.6f}
      迭代次数 = {n_iter}
      精度 = 1e-6
    
    对比公式：
      Haaland：λ = {lambda_haaland:.6f}
      Swamee：λ = {lambda_swamee:.6f}
      Colebrook：λ = {lambda_final:.6f}
    
    Colebrook公式：
      1/√λ = -2log₁₀(ε/(3.7d) + 2.51/(Re√λ))
    
    特点：
      • 最准确
      • 需迭代
      • 工程标准
      • Moody图理论基础
    
    收敛性：
      快速收敛（5-10次）
      二阶收敛速度
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("Colebrook公式迭代求解")
    print("="*60)
    Re, eps_d = 1e5, 0.001
    lambda_final, n_iter, history = colebrook_iteration(Re, eps_d)
    print(f"\nRe={Re:.0e}, ε/d={eps_d}")
    print(f"λ={lambda_final:.6f}")
    print(f"迭代{n_iter}次收敛")
    plot_colebrook()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
