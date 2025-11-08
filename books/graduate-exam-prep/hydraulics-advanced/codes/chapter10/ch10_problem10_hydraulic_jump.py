# -*- coding: utf-8 -*-
"""
第10章 堰闸水力计算 - 题10：水跃计算

问题描述：
    矩形断面渠道，b = 3m，Q = 15 m³/s
    跃前水深h1 = 0.8m
    
    求：
    1. 跃前Froude数Fr1
    2. 跃后共轭水深h2
    3. 水跃长度Lj
    4. 水跃能量损失ΔE
    5. 不同Fr1下水跃类型

核心公式：
    1. Froude数：Fr1 = v1/√(g·h1)
    2. 共轭水深：h2 = (h1/2)(√(1+8Fr1²) - 1)
    3. 水跃长度：Lj ≈ 6h2
    4. 能量损失：ΔE = (h2-h1)³/(4h1·h2)
    5. 水跃类型分类（5种）

考试要点：
    - 共轭水深公式推导
    - Fr数物理意义
    - 水跃能量损失
    - 水跃类型判别

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class HydraulicJump:
    """水跃计算"""
    
    def __init__(self, b: float, Q: float, h1: float):
        self.b = b  # 渠道宽度
        self.Q = Q  # 流量
        self.h1 = h1  # 跃前水深
        self.g = 9.8
        
    def velocity1(self) -> float:
        """跃前流速"""
        v1 = self.Q / (self.b * self.h1)
        return v1
    
    def froude1(self) -> float:
        """跃前Froude数"""
        v1 = self.velocity1()
        Fr1 = v1 / np.sqrt(self.g * self.h1)
        return Fr1
    
    def conjugate_depth(self) -> float:
        """
        共轭水深（跃后水深）
        h2 = (h1/2)(√(1+8Fr1²) - 1)
        """
        Fr1 = self.froude1()
        h2 = (self.h1 / 2) * (np.sqrt(1 + 8 * Fr1**2) - 1)
        return h2
    
    def velocity2(self) -> float:
        """跃后流速"""
        h2 = self.conjugate_depth()
        v2 = self.Q / (self.b * h2)
        return v2
    
    def froude2(self) -> float:
        """跃后Froude数"""
        v2 = self.velocity2()
        h2 = self.conjugate_depth()
        Fr2 = v2 / np.sqrt(self.g * h2)
        return Fr2
    
    def jump_length(self) -> float:
        """
        水跃长度
        经验公式：Lj ≈ 6h2
        """
        h2 = self.conjugate_depth()
        Lj = 6 * h2
        return Lj
    
    def energy_loss(self) -> float:
        """
        水跃能量损失
        ΔE = (h2-h1)³/(4h1·h2)
        """
        h2 = self.conjugate_depth()
        delta_E = (h2 - self.h1)**3 / (4 * self.h1 * h2)
        return delta_E
    
    def efficiency(self) -> float:
        """
        水跃效率（相对能量损失）
        η = ΔE/E1
        """
        v1 = self.velocity1()
        E1 = self.h1 + v1**2 / (2 * self.g)
        delta_E = self.energy_loss()
        eta = delta_E / E1
        return eta
    
    def jump_type(self) -> str:
        """
        水跃类型分类
        Fr1 < 1: 无水跃
        1 < Fr1 < 1.7: 波状水跃
        1.7 < Fr1 < 2.5: 弱水跃
        2.5 < Fr1 < 4.5: 稳定水跃
        4.5 < Fr1 < 9: 强水跃
        Fr1 > 9: 激烈水跃
        """
        Fr1 = self.froude1()
        
        if Fr1 <= 1:
            return "无水跃（Fr≤1）"
        elif Fr1 <= 1.7:
            return "波状水跃（1<Fr≤1.7）"
        elif Fr1 <= 2.5:
            return "弱水跃（1.7<Fr≤2.5）"
        elif Fr1 <= 4.5:
            return "稳定水跃（2.5<Fr≤4.5）"
        elif Fr1 <= 9:
            return "强水跃（4.5<Fr≤9）"
        else:
            return "激烈水跃（Fr>9）"
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        Fr1 = self.froude1()
        h2 = self.conjugate_depth()
        v1 = self.velocity1()
        v2 = self.velocity2()
        Lj = self.jump_length()
        delta_E = self.energy_loss()
        
        # 1. 水跃示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 水跃前
        x_before = np.array([0, 5])
        y_before = np.array([self.h1, self.h1])
        ax1.fill_between(x_before, 0, y_before, color='lightblue', alpha=0.5, label='跃前')
        ax1.plot(x_before, y_before, 'b-', linewidth=2)
        
        # 水跃区（简化为斜线）
        x_jump = np.array([5, 5+Lj])
        y_jump = np.linspace(self.h1, h2, 20)
        x_jump_arr = np.linspace(5, 5+Lj, 20)
        ax1.fill_between(x_jump_arr, 0, y_jump, color='lightcoral', alpha=0.3, label='水跃区')
        ax1.plot(x_jump_arr, y_jump, 'r-', linewidth=2)
        
        # 水跃后
        x_after = np.array([5+Lj, 15])
        y_after = np.array([h2, h2])
        ax1.fill_between(x_after, 0, y_after, color='lightgreen', alpha=0.5, label='跃后')
        ax1.plot(x_after, y_after, 'g-', linewidth=2)
        
        # 标注
        ax1.text(2.5, self.h1+0.2, f'h₁={self.h1}m\nv₁={v1:.2f}m/s\nFr₁={Fr1:.2f}', 
                ha='center', fontsize=9, color='blue', fontweight='bold')
        ax1.text(12, h2+0.2, f'h₂={h2:.2f}m\nv₂={v2:.2f}m/s', 
                ha='center', fontsize=9, color='green', fontweight='bold')
        ax1.text(5+Lj/2, h2+0.5, f'Lj={Lj:.2f}m', ha='center', fontsize=10, color='red', fontweight='bold')
        
        # 底部标注
        ax1.arrow(5, -0.5, Lj, 0, head_width=0.15, head_length=0.3, fc='red', ec='red')
        ax1.text(5+Lj/2, -0.8, f'水跃长度 Lj≈6h₂', ha='center', fontsize=9, color='red')
        
        ax1.set_xlim(-1, 16)
        ax1.set_ylim(-1.2, max(h2, self.h1*2)+1)
        ax1.set_xlabel('距离 x (m)', fontsize=10)
        ax1.set_ylabel('水深 h (m)', fontsize=10)
        ax1.set_title('水跃示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        jump_type = self.jump_type()
        
        ax2.text(0.5, 0.95, '水跃参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'渠宽: b = {self.b} m', fontsize=10)
        ax2.text(0.1, 0.72, f'流量: Q = {self.Q} m³/s', fontsize=10)
        ax2.text(0.1, 0.60, f'跃前水深: h₁ = {self.h1} m', fontsize=10)
        ax2.text(0.1, 0.50, f'跃前流速: v₁ = {v1:.3f} m/s', fontsize=10)
        ax2.text(0.1, 0.40, f'Fr数: Fr₁ = {Fr1:.3f}', fontsize=11, color='red', fontweight='bold')
        ax2.text(0.1, 0.28, f'跃后水深: h₂ = {h2:.3f} m', fontsize=10, color='green')
        ax2.text(0.1, 0.18, f'水跃长度: Lj = {Lj:.2f} m', fontsize=10, color='blue')
        ax2.text(0.1, 0.08, f'能量损失: ΔE = {delta_E:.3f} m', fontsize=10, color='purple')
        ax2.text(0.1, -0.02, f'水跃类型: {jump_type}', fontsize=9, color='orange', fontweight='bold')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. h1-h2关系曲线
        ax3 = plt.subplot(3, 3, 3)
        
        Fr1_range = np.linspace(1.1, 10, 100)
        h2_ratio_range = []
        
        for Fr in Fr1_range:
            h2_ratio = 0.5 * (np.sqrt(1 + 8*Fr**2) - 1)
            h2_ratio_range.append(h2_ratio)
        
        ax3.plot(Fr1_range, h2_ratio_range, 'b-', linewidth=2, label='h₂/h₁ = f(Fr₁)')
        ax3.plot(Fr1, h2/self.h1, 'ro', markersize=10, label=f'当前点(Fr₁={Fr1:.2f})')
        
        ax3.set_xlabel('跃前Froude数 Fr₁', fontsize=10)
        ax3.set_ylabel('水深比 h₂/h₁', fontsize=10)
        ax3.set_title('共轭水深关系', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 能量损失随Fr1变化
        ax4 = plt.subplot(3, 3, 4)
        
        delta_E_range = []
        for Fr in Fr1_range:
            h2_temp = self.h1 * 0.5 * (np.sqrt(1 + 8*Fr**2) - 1)
            dE_temp = (h2_temp - self.h1)**3 / (4 * self.h1 * h2_temp)
            delta_E_range.append(dE_temp)
        
        ax4.plot(Fr1_range, delta_E_range, 'r-', linewidth=2)
        ax4.plot(Fr1, delta_E, 'go', markersize=10, label=f'ΔE={delta_E:.3f}m')
        
        ax4.set_xlabel('跃前Froude数 Fr₁', fontsize=10)
        ax4.set_ylabel('能量损失 ΔE (m)', fontsize=10)
        ax4.set_title('能量损失随Fr₁变化', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 水跃类型分区
        ax5 = plt.subplot(3, 3, 5)
        
        Fr_types = [1, 1.7, 2.5, 4.5, 9, 12]
        colors = ['white', 'lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'pink']
        labels = ['无水跃', '波状', '弱', '稳定', '强', '激烈']
        
        for i in range(len(Fr_types)-1):
            ax5.axvspan(Fr_types[i], Fr_types[i+1], alpha=0.5, color=colors[i], label=labels[i])
        
        ax5.axvline(Fr1, color='red', linestyle='--', linewidth=3, label=f'Fr₁={Fr1:.2f}')
        
        ax5.set_xlim(0, 12)
        ax5.set_ylim(0, 1)
        ax5.set_xlabel('Froude数 Fr₁', fontsize=10)
        ax5.set_title('水跃类型分区', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=8, ncol=2)
        ax5.grid(True, alpha=0.3, axis='x')
        
        # 6. 能量线与水面线
        ax6 = plt.subplot(3, 3, 6)
        
        x_profile = np.array([0, 5, 5+Lj, 15])
        h_profile = np.array([self.h1, self.h1, h2, h2])
        
        E1 = self.h1 + v1**2/(2*self.g)
        E2 = h2 + v2**2/(2*self.g)
        E_profile = np.array([E1, E1, E2, E2])
        
        ax6.fill_between(x_profile, 0, h_profile, color='lightblue', alpha=0.5, label='水深')
        ax6.plot(x_profile, h_profile, 'b-', linewidth=2, label='水面线')
        ax6.plot(x_profile, E_profile, 'r--', linewidth=2, label='能量线')
        
        # 标注能量损失
        ax6.arrow(5+Lj/2, E1, 0, -(E1-E2), head_width=0.3, head_length=0.05, fc='red', ec='red')
        ax6.text(5+Lj/2+1, (E1+E2)/2, f'ΔE={delta_E:.2f}m', fontsize=9, color='red', fontweight='bold')
        
        ax6.set_xlabel('距离 x (m)', fontsize=10)
        ax6.set_ylabel('高程/比能 (m)', fontsize=10)
        ax6.set_title('能量线与水面线', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        ax6.set_xlim(-1, 16)
        
        # 7. 不同h1下的h2
        ax7 = plt.subplot(3, 3, 7)
        
        h1_range = np.linspace(0.3, 2, 50)
        h2_range = []
        
        for h1_val in h1_range:
            jump_temp = HydraulicJump(self.b, self.Q, h1_val)
            h2_range.append(jump_temp.conjugate_depth())
        
        ax7.plot(h1_range, h2_range, 'b-', linewidth=2, label='h₂(h₁)')
        ax7.plot(self.h1, h2, 'ro', markersize=10, label=f'h₁={self.h1}m')
        ax7.plot([0, 2], [0, 2], 'k--', linewidth=1, alpha=0.5, label='h₂=h₁')
        
        ax7.set_xlabel('跃前水深 h₁ (m)', fontsize=10)
        ax7.set_ylabel('跃后水深 h₂ (m)', fontsize=10)
        ax7.set_title('h₁-h₂关系', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 水跃效率
        ax8 = plt.subplot(3, 3, 8)
        
        eta = self.efficiency()
        eta_range = []
        
        for Fr in Fr1_range:
            jump_temp_h1 = 1.0
            jump_temp_v1 = Fr * np.sqrt(self.g * jump_temp_h1)
            jump_temp_h2 = jump_temp_h1 * 0.5 * (np.sqrt(1 + 8*Fr**2) - 1)
            E1_temp = jump_temp_h1 + jump_temp_v1**2/(2*self.g)
            dE_temp = (jump_temp_h2 - jump_temp_h1)**3 / (4 * jump_temp_h1 * jump_temp_h2)
            eta_range.append(dE_temp / E1_temp)
        
        ax8.plot(Fr1_range, eta_range, 'purple', linewidth=2)
        ax8.plot(Fr1, eta, 'ro', markersize=10, label=f'η={eta*100:.1f}%')
        
        ax8.set_xlabel('跃前Froude数 Fr₁', fontsize=10)
        ax8.set_ylabel('相对能损 η = ΔE/E₁', fontsize=10)
        ax8.set_title('水跃效率', fontsize=12, fontweight='bold')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        Fr2 = self.froude2()
        
        table_data = [
            ['参数', '跃前', '跃后'],
            ['水深(m)', f'{self.h1:.3f}', f'{h2:.3f}'],
            ['流速(m/s)', f'{v1:.3f}', f'{v2:.3f}'],
            ['Froude数', f'{Fr1:.3f}', f'{Fr2:.3f}'],
            ['比能(m)', f'{self.h1+v1**2/(2*self.g):.3f}', f'{h2+v2**2/(2*self.g):.3f}'],
            ['', '', ''],
            ['水跃长度(m)', f'{Lj:.2f}', '≈6h₂'],
            ['能量损失(m)', f'{delta_E:.3f}', ''],
            ['相对能损', f'{eta*100:.1f}%', ''],
            ['水跃类型', jump_type[:4], '']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.35, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        table[(3, 1)].set_facecolor('#90EE90')
        table[(3, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch10_problem10_hydraulic_jump.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch10_problem10_hydraulic_jump.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第10章 堰闸水力计算 - 题10：水跃计算")
        print("="*70)
        
        v1 = self.velocity1()
        Fr1 = self.froude1()
        h2 = self.conjugate_depth()
        v2 = self.velocity2()
        Fr2 = self.froude2()
        Lj = self.jump_length()
        delta_E = self.energy_loss()
        eta = self.efficiency()
        jump_type = self.jump_type()
        
        print(f"\n【渠道参数】")
        print(f"渠宽: b = {self.b} m")
        print(f"流量: Q = {self.Q} m³/s")
        
        print(f"\n【跃前参数】")
        print(f"水深: h₁ = {self.h1} m")
        print(f"流速: v₁ = Q/(b·h₁) = {v1:.3f} m/s")
        print(f"Froude数: Fr₁ = v₁/√(g·h₁) = {Fr1:.3f}")
        
        print(f"\n【共轭水深】")
        print(f"h₂ = (h₁/2)(√(1+8Fr₁²) - 1)")
        print(f"   = ({self.h1}/2)(√(1+8×{Fr1:.3f}²) - 1)")
        print(f"   = {h2:.3f} m")
        
        print(f"\n【跃后参数】")
        print(f"水深: h₂ = {h2:.3f} m")
        print(f"流速: v₂ = Q/(b·h₂) = {v2:.3f} m/s")
        print(f"Froude数: Fr₂ = {Fr2:.3f} (< 1, 缓流)")
        
        print(f"\n【水跃特性】")
        print(f"水跃长度: Lj ≈ 6h₂ = {Lj:.2f} m")
        print(f"能量损失: ΔE = (h₂-h₁)³/(4h₁h₂) = {delta_E:.3f} m")
        print(f"相对能损: η = ΔE/E₁ = {eta*100:.1f}%")
        print(f"水跃类型: {jump_type}")
        
        print(f"\n✓ 水跃计算完成")
        print(f"\n{'='*70}\n")


def main():
    b = 3
    Q = 15
    h1 = 0.8
    
    jump = HydraulicJump(b, Q, h1)
    jump.print_results()
    jump.plot_analysis()


if __name__ == "__main__":
    main()
