# -*- coding: utf-8 -*-
"""
第10章 堰闸水力计算 - 题7：闸孔出流计算

问题描述：
    平板闸门，闸孔宽度b = 4m，开度e = 0.6m
    上游水深H1 = 3m，下游水深H2 = 1.5m
    流量系数μ = 0.60（自由出流），μs = 0.85（淹没出流）
    
    求：
    1. 自由出流与淹没出流判别
    2. 闸孔流量Q
    3. 收缩断面水深hc
    4. 下游共轭水深（水跃）
    5. 不同开度影响

核心公式：
    1. 自由出流：Q = μ·b·e·√(2g·H1)
    2. 淹没出流：Q = μs·b·e·√(2g(H1-H2))
    3. 收缩系数：ε = hc/e ≈ 0.61~0.64
    4. 淹没判别：hc/H2 < 0.7（自由），> 0.7（淹没）

考试要点：
    - 闸孔出流类型判别
    - 收缩断面计算
    - 水跃共轭水深
    - 流量系数选取

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from typing import Tuple

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SluiceGate:
    """闸孔出流计算"""
    
    def __init__(self, b: float, e: float, H1: float, H2: float, 
                 mu: float = 0.60, mu_s: float = 0.85):
        self.b = b  # 闸孔宽度
        self.e = e  # 开度
        self.H1 = H1  # 上游水深
        self.H2 = H2  # 下游水深
        self.mu = mu  # 自由出流系数
        self.mu_s = mu_s  # 淹没出流系数
        self.g = 9.8
        self.epsilon = 0.62  # 收缩系数
        
    def contraction_depth(self) -> float:
        """收缩断面水深"""
        hc = self.epsilon * self.e
        return hc
    
    def is_free_flow(self) -> bool:
        """判别是否为自由出流"""
        hc = self.contraction_depth()
        # 判别准则：hc/H2 < 0.7
        if hc / self.H2 < 0.7:
            return True
        else:
            return False
    
    def discharge_free(self) -> float:
        """自由出流流量"""
        Q = self.mu * self.b * self.e * np.sqrt(2 * self.g * self.H1)
        return Q
    
    def discharge_submerged(self) -> float:
        """淹没出流流量"""
        Q = self.mu_s * self.b * self.e * np.sqrt(2 * self.g * (self.H1 - self.H2))
        return Q
    
    def discharge(self) -> float:
        """闸孔流量（自动判别）"""
        if self.is_free_flow():
            return self.discharge_free()
        else:
            return self.discharge_submerged()
    
    def contraction_velocity(self) -> float:
        """收缩断面流速"""
        Q = self.discharge()
        hc = self.contraction_depth()
        vc = Q / (self.b * hc)
        return vc
    
    def conjugate_depth(self, h1: float, v1: float) -> float:
        """
        共轭水深（水跃）
        h2 = (-h1 + √(h1² + 8v1²h1/g)) / 2
        """
        Fr1 = v1 / np.sqrt(self.g * h1)
        if Fr1 <= 1:
            return h1  # 无水跃
        
        # 共轭水深公式
        h2 = h1/2 * (np.sqrt(1 + 8*Fr1**2) - 1)
        return h2
    
    def hydraulic_jump_check(self) -> Tuple[bool, float]:
        """水跃校核"""
        hc = self.contraction_depth()
        vc = self.contraction_velocity()
        hc2 = self.conjugate_depth(hc, vc)
        
        # 判别是否发生水跃
        if hc2 > hc and hc2 <= self.H2 * 1.05:
            return True, hc2
        else:
            return False, hc2
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        Q = self.discharge()
        hc = self.contraction_depth()
        vc = self.contraction_velocity()
        is_free = self.is_free_flow()
        has_jump, hc2 = self.hydraulic_jump_check()
        
        # 1. 闸门出流示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 上游水体
        ax1.fill_between([0, 3], [0, 0], [self.H1, self.H1], 
                        color='lightblue', alpha=0.5, label='上游水体')
        
        # 闸门
        ax1.plot([3, 3], [0, self.e], 'k-', linewidth=4, label='闸门')
        ax1.plot([3, 3.2], [self.e, self.e], 'k-', linewidth=4)
        
        # 收缩断面
        ax1.plot([3.5, 3.5], [0, hc], 'r--', linewidth=2, label=f'收缩断面hc={hc:.2f}m')
        
        # 下游
        if has_jump:
            ax1.fill_between([3.5, 5, 7], [0, 0, 0], [hc, hc, hc2], 
                            color='lightcoral', alpha=0.3, label='水跃前')
            ax1.fill_between([7, 10], [0, 0], [hc2, self.H2], 
                            color='lightgreen', alpha=0.3, label='水跃后')
        else:
            ax1.fill_between([3.5, 10], [0, 0], [hc, self.H2], 
                            color='lightgreen', alpha=0.3, label='下游水体')
        
        # 标注
        ax1.text(1.5, self.H1+0.2, f'H₁={self.H1}m', ha='center', fontsize=10, color='blue', fontweight='bold')
        ax1.text(2.5, self.e/2, f'e={self.e}m', fontsize=10, color='red', fontweight='bold')
        ax1.text(9, self.H2+0.2, f'H₂={self.H2}m', ha='center', fontsize=10, color='green', fontweight='bold')
        
        ax1.set_xlim(-0.5, 11)
        ax1.set_ylim(-0.5, self.H1+1)
        ax1.set_xlabel('距离 (m)', fontsize=10)
        ax1.set_ylabel('水深 (m)', fontsize=10)
        ax1.set_title(f'闸门出流示意（{"自由" if is_free else "淹没"}）', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        flow_type = "自由出流" if is_free else "淹没出流"
        
        ax2.text(0.5, 0.95, '闸孔参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'闸宽: b = {self.b} m', fontsize=10)
        ax2.text(0.1, 0.72, f'开度: e = {self.e} m', fontsize=10)
        ax2.text(0.1, 0.62, f'上游水深: H₁ = {self.H1} m', fontsize=10)
        ax2.text(0.1, 0.52, f'下游水深: H₂ = {self.H2} m', fontsize=10)
        ax2.text(0.1, 0.40, f'出流类型: {flow_type}', fontsize=10, color='red', fontweight='bold')
        ax2.text(0.1, 0.30, f'流量: Q = {Q:.3f} m³/s', fontsize=11, color='blue', fontweight='bold')
        ax2.text(0.1, 0.20, f'收缩水深: hc = {hc:.3f} m', fontsize=10, color='green')
        ax2.text(0.1, 0.10, f'收缩流速: vc = {vc:.3f} m/s', fontsize=10, color='green')
        ax2.text(0.1, 0.00, f'Fr数: {vc/np.sqrt(self.g*hc):.3f}', fontsize=10, color='purple')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 开度-流量关系
        ax3 = plt.subplot(3, 3, 3)
        
        e_range = np.linspace(0.2, 2, 50)
        Q_range = []
        
        for e_val in e_range:
            gate_temp = SluiceGate(self.b, e_val, self.H1, self.H2, self.mu, self.mu_s)
            Q_range.append(gate_temp.discharge())
        
        ax3.plot(e_range, Q_range, 'b-', linewidth=2, label='Q(e)')
        ax3.plot(self.e, Q, 'ro', markersize=10, label=f'e={self.e}m')
        
        ax3.set_xlabel('开度 e (m)', fontsize=10)
        ax3.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_title('开度-流量关系', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 自由vs淹没出流对比
        ax4 = plt.subplot(3, 3, 4)
        
        Q_free = self.discharge_free()
        Q_sub = self.discharge_submerged()
        
        bars = ax4.bar(['自由出流', '淹没出流', '实际流量'], 
                      [Q_free, Q_sub, Q],
                      color=['skyblue', 'lightcoral', 'lightgreen'],
                      alpha=0.7, edgecolor='black')
        
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax4.set_title('出流类型对比', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, q in zip(bars, [Q_free, Q_sub, Q]):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{q:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 5. 收缩系数影响
        ax5 = plt.subplot(3, 3, 5)
        
        eps_range = np.linspace(0.55, 0.70, 50)
        hc_range = eps_range * self.e
        Q_eps = []
        
        for hc_val in hc_range:
            # 简化：假设流量与hc成正比
            Q_eps.append(self.mu * self.b * hc_val * np.sqrt(2*self.g*self.H1) / 0.62)
        
        ax5.plot(eps_range, Q_eps, 'b-', linewidth=2)
        ax5.plot(self.epsilon, Q, 'ro', markersize=10, label=f'ε={self.epsilon}')
        ax5.axvline(0.62, color='green', linestyle='--', linewidth=1, alpha=0.7, label='标准ε=0.62')
        
        ax5.set_xlabel('收缩系数 ε', fontsize=10)
        ax5.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax5.set_title('收缩系数影响', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 水跃分析
        ax6 = plt.subplot(3, 3, 6)
        
        if has_jump:
            Fr1 = vc / np.sqrt(self.g * hc)
            
            ax6.text(0.5, 0.9, '水跃分析', fontsize=11, ha='center', fontweight='bold')
            ax6.text(0.1, 0.75, f'跃前水深: h₁ = {hc:.3f} m', fontsize=10)
            ax6.text(0.1, 0.65, f'跃前流速: v₁ = {vc:.3f} m/s', fontsize=10)
            ax6.text(0.1, 0.55, f'Fr数: Fr₁ = {Fr1:.3f}', fontsize=10, color='red')
            ax6.text(0.1, 0.45, f'跃后水深: h₂ = {hc2:.3f} m', fontsize=10, color='green')
            ax6.text(0.1, 0.35, f'下游水深: H₂ = {self.H2:.3f} m', fontsize=10)
            
            if abs(hc2 - self.H2) / self.H2 < 0.05:
                ax6.text(0.1, 0.20, '✓ 发生完全水跃', fontsize=11, color='green', fontweight='bold')
            else:
                ax6.text(0.1, 0.20, '⚠ 水深不匹配', fontsize=11, color='orange', fontweight='bold')
        else:
            ax6.text(0.5, 0.5, '无水跃\n(Fr < 1 或 h₂ ≠ H₂)', 
                    fontsize=12, ha='center', va='center', color='blue', fontweight='bold')
        
        ax6.axis('off')
        ax6.set_title('水跃判别', fontsize=12, fontweight='bold')
        
        # 7. Fr数沿程分布（简化）
        ax7 = plt.subplot(3, 3, 7)
        
        x_profile = np.array([0, 3, 3.5, 5, 7, 10])
        Fr_profile = np.array([
            vc/np.sqrt(self.g*self.H1) * 0.1,  # 上游
            vc/np.sqrt(self.g*self.H1) * 0.3,  # 闸前
            vc/np.sqrt(self.g*hc),  # 收缩断面
            vc/np.sqrt(self.g*hc),  # 水跃前
            vc/np.sqrt(self.g*hc2) if has_jump else vc/np.sqrt(self.g*self.H2),  # 水跃后
            vc/np.sqrt(self.g*self.H2)  # 下游
        ])
        
        ax7.plot(x_profile, Fr_profile, 'b-', linewidth=2, marker='o', markersize=6)
        ax7.axhline(1, color='red', linestyle='--', linewidth=1.5, label='Fr=1')
        ax7.fill_between(x_profile, 0, Fr_profile, where=Fr_profile<1, alpha=0.2, color='blue', label='缓流')
        ax7.fill_between(x_profile, 0, Fr_profile, where=Fr_profile>=1, alpha=0.2, color='orange', label='急流')
        
        ax7.set_xlabel('距离 x (m)', fontsize=10)
        ax7.set_ylabel('Froude数 Fr', fontsize=10)
        ax7.set_title('Fr数沿程分布', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 流量系数对比
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '流量系数选取', fontsize=11, ha='center', fontweight='bold')
        
        ax8.text(0.1, 0.80, '自由出流:', fontsize=10, color='blue', fontweight='bold')
        ax8.text(0.15, 0.70, f'μ = {self.mu}', fontsize=10)
        ax8.text(0.15, 0.60, f'Q_free = {Q_free:.2f} m³/s', fontsize=10, color='red')
        
        ax8.text(0.1, 0.45, '淹没出流:', fontsize=10, color='green', fontweight='bold')
        ax8.text(0.15, 0.35, f'μs = {self.mu_s}', fontsize=10)
        ax8.text(0.15, 0.25, f'Q_sub = {Q_sub:.2f} m³/s', fontsize=10, color='red')
        
        ax8.text(0.1, 0.10, f'判别: hc/H₂ = {hc/self.H2:.3f}', fontsize=10, color='purple')
        ax8.text(0.15, 0.00, '< 0.7: 自由; > 0.7: 淹没', fontsize=9, color='gray')
        
        ax8.set_title('系数选取', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['闸宽 b', f'{self.b:.2f}', 'm'],
            ['开度 e', f'{self.e:.2f}', 'm'],
            ['上游水深 H₁', f'{self.H1:.2f}', 'm'],
            ['下游水深 H₂', f'{self.H2:.2f}', 'm'],
            ['收缩水深 hc', f'{hc:.3f}', 'm'],
            ['收缩流速 vc', f'{vc:.3f}', 'm/s'],
            ['出流类型', flow_type, '-'],
            ['流量 Q', f'{Q:.3f}', 'm³/s'],
            ['水跃', '是' if has_jump else '否', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        table[(8, 1)].set_facecolor('#90EE90')
        table[(8, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch10_problem07_sluice_gate.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch10_problem07_sluice_gate.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第10章 堰闸水力计算 - 题7：闸孔出流计算")
        print("="*70)
        
        Q = self.discharge()
        hc = self.contraction_depth()
        vc = self.contraction_velocity()
        is_free = self.is_free_flow()
        has_jump, hc2 = self.hydraulic_jump_check()
        
        print(f"\n【闸门参数】")
        print(f"闸宽: b = {self.b} m")
        print(f"开度: e = {self.e} m")
        print(f"上游水深: H₁ = {self.H1} m")
        print(f"下游水深: H₂ = {self.H2} m")
        
        print(f"\n【出流判别】")
        print(f"收缩水深: hc = ε·e = {self.epsilon}×{self.e} = {hc:.3f} m")
        print(f"判别参数: hc/H₂ = {hc/self.H2:.3f}")
        print(f"出流类型: {'自由出流（hc/H₂ < 0.7）' if is_free else '淹没出流（hc/H₂ > 0.7）'}")
        
        print(f"\n【流量计算】")
        if is_free:
            print(f"Q = μ·b·e·√(2g·H₁)")
            print(f"  = {self.mu}×{self.b}×{self.e}×√(2×{self.g}×{self.H1})")
        else:
            print(f"Q = μs·b·e·√(2g(H₁-H₂))")
            print(f"  = {self.mu_s}×{self.b}×{self.e}×√(2×{self.g}×{self.H1-self.H2})")
        print(f"  = {Q:.3f} m³/s")
        
        print(f"\n【收缩断面】")
        print(f"水深: hc = {hc:.3f} m")
        print(f"流速: vc = Q/(b·hc) = {vc:.3f} m/s")
        Fr = vc / np.sqrt(self.g * hc)
        print(f"Fr数: Fr = {Fr:.3f} ({'急流' if Fr>1 else '缓流'})")
        
        if has_jump:
            print(f"\n【水跃分析】")
            print(f"跃后共轭水深: h₂' = {hc2:.3f} m")
            print(f"下游水深: H₂ = {self.H2:.3f} m")
            if abs(hc2 - self.H2) / self.H2 < 0.05:
                print(f"✓ 发生完全水跃（h₂' ≈ H₂）")
            else:
                print(f"⚠ 水深不匹配，可能发生远驱水跃或淹没水跃")
        
        print(f"\n✓ 闸孔出流计算完成")
        print(f"\n{'='*70}\n")


def main():
    b = 4
    e = 0.6
    H1 = 3
    H2 = 1.5
    
    gate = SluiceGate(b, e, H1, H2)
    gate.print_results()
    gate.plot_analysis()


if __name__ == "__main__":
    main()
