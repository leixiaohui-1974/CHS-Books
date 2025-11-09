# -*- coding: utf-8 -*-
"""
第11章 水工建筑物 - 题7：水闸调度运行

问题描述：
    某水闸控制渠道流量，闸门净宽b = 10m，闸门数n = 3孔
    上游设计水位H₁ = 8m，下游水位H₂ = 5m
    闸门启闭规则：e = 0.5H₁
    需进行水闸调度计算
    
    求：
    1. 自由出流与淹没出流判别
    2. 不同开度下的过闸流量
    3. 水位-流量关系曲线
    4. 闸门启闭调度方案
    5. 泄流能力分析

核心公式：
    1. 自由出流：Q = μ₀·b·e·√(2g·H₁)
    2. 淹没出流：Q = μs·b·e·√(2g·(H₁-H₂))
    3. 判别：hc < H₂（淹没），hc ≥ H₂（自由）
    4. 收缩系数：ε ≈ 0.62

考试要点：
    - 水闸出流计算
    - 自由与淹没判别
    - 闸门调度
    - 泄流能力

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SluiceOperation:
    """水闸调度运行"""
    
    def __init__(self, b: float, n: int, H1: float, H2: float,
                 mu0: float = 0.60, mus: float = 0.85, epsilon: float = 0.62):
        self.b = b  # 单孔净宽
        self.n = n  # 闸孔数
        self.H1 = H1  # 上游水位
        self.H2 = H2  # 下游水位
        self.mu0 = mu0  # 自由出流流量系数
        self.mus = mus  # 淹没出流流量系数
        self.epsilon = epsilon  # 收缩系数
        self.g = 9.8
        
    def contraction_depth(self, e: float) -> float:
        """
        收缩断面水深
        hc = ε·e
        """
        return self.epsilon * e
    
    def is_free_flow(self, e: float) -> bool:
        """
        判别自由出流
        hc ≥ H₂：自由
        hc < H₂：淹没
        """
        hc = self.contraction_depth(e)
        return hc >= self.H2
    
    def discharge_free(self, e: float) -> float:
        """
        自由出流流量
        Q = μ₀·b·e·√(2g·H₁)
        """
        Q_single = self.mu0 * self.b * e * np.sqrt(2 * self.g * self.H1)
        return Q_single * self.n
    
    def discharge_submerged(self, e: float) -> float:
        """
        淹没出流流量
        Q = μs·b·e·√(2g·(H₁-H₂))
        """
        delta_H = self.H1 - self.H2
        if delta_H <= 0:
            return 0
        
        Q_single = self.mus * self.b * e * np.sqrt(2 * self.g * delta_H)
        return Q_single * self.n
    
    def discharge(self, e: float) -> Tuple[float, str]:
        """
        计算过闸流量（自动判别）
        返回：(流量, 流态)
        """
        if self.is_free_flow(e):
            Q = self.discharge_free(e)
            flow_type = "自由出流"
        else:
            Q = self.discharge_submerged(e)
            flow_type = "淹没出流"
        
        return Q, flow_type
    
    def design_opening(self) -> float:
        """
        设计开度
        e = 0.5·H₁（经验）
        """
        return 0.5 * self.H1
    
    def H_Q_curve(self, e_fixed: float = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        水位-流量关系曲线（固定开度）
        """
        if e_fixed is None:
            e_fixed = self.design_opening()
        
        H1_range = np.linspace(self.H2 + 0.5, 15, 100)
        Q_range = []
        
        for H1_val in H1_range:
            sluice_temp = SluiceOperation(self.b, self.n, H1_val, self.H2, 
                                        self.mu0, self.mus, self.epsilon)
            Q_val, _ = sluice_temp.discharge(e_fixed)
            Q_range.append(Q_val)
        
        return H1_range, np.array(Q_range)
    
    def e_Q_curve(self, H1_fixed: float = None) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        开度-流量关系曲线（固定水位）
        """
        if H1_fixed is None:
            H1_fixed = self.H1
        
        e_range = np.linspace(0.5, H1_fixed*0.8, 100)
        Q_range = []
        flow_types = []
        
        for e_val in e_range:
            Q_val, flow_type = self.discharge(e_val)
            Q_range.append(Q_val)
            flow_types.append(flow_type)
        
        return e_range, np.array(Q_range), flow_types
    
    def scheduling_schemes(self) -> List[Dict]:
        """
        闸门启闭调度方案
        """
        schemes = []
        
        # 方案1：小开度（0.3H₁）
        e1 = 0.3 * self.H1
        Q1, type1 = self.discharge(e1)
        schemes.append({
            'name': '小开度',
            'e': e1,
            'e_ratio': 0.3,
            'Q': Q1,
            'flow_type': type1
        })
        
        # 方案2：中开度（0.5H₁）
        e2 = 0.5 * self.H1
        Q2, type2 = self.discharge(e2)
        schemes.append({
            'name': '中开度（设计）',
            'e': e2,
            'e_ratio': 0.5,
            'Q': Q2,
            'flow_type': type2
        })
        
        # 方案3：大开度（0.7H₁）
        e3 = 0.7 * self.H1
        Q3, type3 = self.discharge(e3)
        schemes.append({
            'name': '大开度',
            'e': e3,
            'e_ratio': 0.7,
            'Q': Q3,
            'flow_type': type3
        })
        
        # 方案4：全开（0.9H₁）
        e4 = 0.9 * self.H1
        Q4, type4 = self.discharge(e4)
        schemes.append({
            'name': '全开',
            'e': e4,
            'e_ratio': 0.9,
            'Q': Q4,
            'flow_type': type4
        })
        
        return schemes
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        e_design = self.design_opening()
        Q_design, flow_type_design = self.discharge(e_design)
        hc_design = self.contraction_depth(e_design)
        schemes = self.scheduling_schemes()
        
        # 1. 水闸示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 上游水体
        ax1.fill([0, 0, 5, 5], [0, self.H1, self.H1, 0], 
                color='lightblue', alpha=0.5, label='上游')
        
        # 闸门
        ax1.plot([5, 5], [0, self.H1-e_design], 'k-', linewidth=8)
        ax1.plot([5, 5], [self.H1-e_design, self.H1], 'r-', linewidth=4, label=f'开度e={e_design:.2f}m')
        
        # 收缩断面
        ax1.plot([7, 7], [0, hc_design], 'b--', linewidth=3, label=f'收缩hc={hc_design:.2f}m')
        
        # 下游水体
        ax1.fill([7, 7, 15, 15], [0, self.H2, self.H2, 0], 
                color='lightgreen', alpha=0.5, label='下游')
        
        # 标注
        ax1.text(2.5, self.H1+0.3, f'H₁={self.H1}m', ha='center', fontsize=10, color='blue', fontweight='bold')
        ax1.text(11, self.H2+0.3, f'H₂={self.H2}m', ha='center', fontsize=10, color='green', fontweight='bold')
        ax1.text(5.5, (self.H1-e_design/2), f'{e_design:.2f}m', ha='left', fontsize=9, color='red')
        
        ax1.set_xlabel('距离 (m)', fontsize=10)
        ax1.set_ylabel('水深 (m)', fontsize=10)
        ax1.set_title('水闸断面示意图', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-1, 16)
        ax1.set_ylim(0, self.H1+1)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '水闸参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'单孔净宽: b = {self.b} m', fontsize=10)
        ax2.text(0.1, 0.72, f'闸孔数: n = {self.n} 孔', fontsize=10)
        ax2.text(0.1, 0.62, f'总宽度: B = {self.b*self.n} m', fontsize=10)
        ax2.text(0.1, 0.52, f'上游水位: H₁ = {self.H1} m', fontsize=10, color='blue')
        ax2.text(0.1, 0.42, f'下游水位: H₂ = {self.H2} m', fontsize=10, color='green')
        ax2.text(0.1, 0.32, f'设计开度: e = {e_design:.2f} m', fontsize=10, color='red')
        ax2.text(0.1, 0.22, f'收缩深度: hc = {hc_design:.2f} m', fontsize=10)
        ax2.text(0.1, 0.12, f'流态: {flow_type_design}', fontsize=10, 
                color='orange', fontweight='bold')
        ax2.text(0.1, 0.02, f'设计流量: Q = {Q_design:.1f} m³/s', fontsize=10, 
                color='purple', fontweight='bold')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. e-Q关系曲线
        ax3 = plt.subplot(3, 3, 3)
        
        e_range, Q_e_range, flow_types = self.e_Q_curve()
        
        # 分段绘制（自由/淹没）
        free_mask = np.array([ft == "自由出流" for ft in flow_types])
        submerged_mask = ~free_mask
        
        if np.any(free_mask):
            ax3.plot(e_range[free_mask], Q_e_range[free_mask], 'b-', 
                    linewidth=2, label='自由出流')
        if np.any(submerged_mask):
            ax3.plot(e_range[submerged_mask], Q_e_range[submerged_mask], 'r-', 
                    linewidth=2, label='淹没出流')
        
        ax3.plot(e_design, Q_design, 'go', markersize=10, label=f'设计点')
        
        ax3.set_xlabel('开度 e (m)', fontsize=10)
        ax3.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_title('开度-流量关系', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. H₁-Q关系曲线
        ax4 = plt.subplot(3, 3, 4)
        
        H1_range, Q_H_range = self.H_Q_curve(e_design)
        
        ax4.plot(H1_range, Q_H_range, 'b-', linewidth=2)
        ax4.plot(self.H1, Q_design, 'ro', markersize=10, label=f'设计水位')
        
        ax4.set_xlabel('上游水位 H₁ (m)', fontsize=10)
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax4.set_title(f'水位-流量关系 (e={e_design:.2f}m)', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 调度方案对比
        ax5 = plt.subplot(3, 3, 5)
        
        scheme_names = [s['name'] for s in schemes]
        scheme_Q = [s['Q'] for s in schemes]
        colors_scheme = ['skyblue', 'green', 'orange', 'red']
        
        bars = ax5.bar(scheme_names, scheme_Q, color=colors_scheme, 
                      alpha=0.7, edgecolor='black')
        
        ax5.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax5.set_title('不同开度方案对比', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, Q in zip(bars, scheme_Q):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{Q:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 6. 流态判别
        ax6 = plt.subplot(3, 3, 6)
        
        e_test_range = np.linspace(0.5, self.H1*0.9, 100)
        hc_range = [self.contraction_depth(e_val) for e_val in e_test_range]
        
        ax6.plot(e_test_range, hc_range, 'b-', linewidth=2, label='收缩水深hc')
        ax6.axhline(self.H2, color='r', linestyle='--', linewidth=2, label=f'下游水位H₂={self.H2}m')
        
        # 填充区域
        ax6.fill_between(e_test_range, hc_range, self.H2, 
                        where=(np.array(hc_range) >= self.H2), 
                        color='blue', alpha=0.2, label='自由出流区')
        ax6.fill_between(e_test_range, hc_range, self.H2, 
                        where=(np.array(hc_range) < self.H2), 
                        color='red', alpha=0.2, label='淹没出流区')
        
        ax6.plot(e_design, hc_design, 'go', markersize=10, label='设计点')
        
        ax6.set_xlabel('开度 e (m)', fontsize=10)
        ax6.set_ylabel('水深 (m)', fontsize=10)
        ax6.set_title('流态判别图', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3)
        
        # 7. 孔数影响
        ax7 = plt.subplot(3, 3, 7)
        
        n_range = np.arange(1, 6)
        Q_n = []
        
        for n_val in n_range:
            sluice_temp = SluiceOperation(self.b, n_val, self.H1, self.H2,
                                        self.mu0, self.mus, self.epsilon)
            Q_temp, _ = sluice_temp.discharge(e_design)
            Q_n.append(Q_temp)
        
        ax7.plot(n_range, Q_n, 'b-o', linewidth=2, markersize=8)
        ax7.plot(self.n, Q_design, 'ro', markersize=12, label=f'n={self.n}孔')
        
        ax7.set_xlabel('闸孔数 n', fontsize=10)
        ax7.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax7.set_title('闸孔数影响', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        ax7.set_xticks(n_range)
        
        # 8. 流量系数影响
        ax8 = plt.subplot(3, 3, 8)
        
        mu_range = np.linspace(0.5, 0.7, 50)
        Q_mu_free = [mu_val * self.b * self.n * e_design * np.sqrt(2 * self.g * self.H1) 
                    for mu_val in mu_range]
        
        delta_H = self.H1 - self.H2
        Q_mu_sub = [mu_val * self.b * self.n * e_design * np.sqrt(2 * self.g * delta_H) 
                   for mu_val in mu_range]
        
        ax8.plot(mu_range, Q_mu_free, 'b-', linewidth=2, label='自由出流（μ₀）')
        ax8.plot(mu_range, Q_mu_sub, 'r-', linewidth=2, label='淹没出流（μs）')
        
        if flow_type_design == "自由出流":
            ax8.plot(self.mu0, Q_design, 'go', markersize=10, label=f'设计μ₀={self.mu0}')
        else:
            ax8.plot(self.mus, Q_design, 'go', markersize=10, label=f'设计μs={self.mus}')
        
        ax8.set_xlabel('流量系数 μ', fontsize=10)
        ax8.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax8.set_title('流量系数影响', fontsize=12, fontweight='bold')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # 9. 调度方案表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [['方案', '开度(m)', '开度比', '流量(m³/s)', '流态']]
        for s in schemes:
            table_data.append([
                s['name'],
                f"{s['e']:.2f}",
                f"{s['e_ratio']:.1f}",
                f"{s['Q']:.0f}",
                s['flow_type']
            ])
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.25, 0.18, 0.15, 0.22, 0.18])
        table.auto_set_font_size(False)
        table.set_fontsize(8.5)
        table.scale(1, 2.2)
        
        for i in range(5):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮设计方案
        table[(2, 0)].set_facecolor('#90EE90')
        
        ax9.set_title('调度方案汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch11_problem07_sluice_operation.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch11_problem07_sluice_operation.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第11章 水工建筑物 - 题7：水闸调度运行")
        print("="*70)
        
        e_design = self.design_opening()
        Q_design, flow_type_design = self.discharge(e_design)
        hc_design = self.contraction_depth(e_design)
        schemes = self.scheduling_schemes()
        
        print(f"\n【水闸参数】")
        print(f"单孔净宽: b = {self.b} m")
        print(f"闸孔数: n = {self.n} 孔")
        print(f"总宽度: B = {self.b * self.n} m")
        print(f"上游水位: H₁ = {self.H1} m")
        print(f"下游水位: H₂ = {self.H2} m")
        
        print(f"\n【设计开度】")
        print(f"设计开度: e = 0.5×H₁ = 0.5×{self.H1} = {e_design:.2f} m")
        print(f"收缩系数: ε = {self.epsilon}")
        print(f"收缩水深: hc = ε·e = {self.epsilon}×{e_design:.2f} = {hc_design:.2f} m")
        
        print(f"\n【流态判别】")
        if self.is_free_flow(e_design):
            print(f"hc = {hc_design:.2f} m ≥ H₂ = {self.H2} m")
            print(f"判别: {flow_type_design}")
            print(f"流量公式: Q = μ₀·n·b·e·√(2g·H₁)")
            print(f"         = {self.mu0}×{self.n}×{self.b}×{e_design:.2f}×√(2×{self.g}×{self.H1})")
        else:
            print(f"hc = {hc_design:.2f} m < H₂ = {self.H2} m")
            print(f"判别: {flow_type_design}")
            delta_H = self.H1 - self.H2
            print(f"水位差: ΔH = H₁ - H₂ = {delta_H:.2f} m")
            print(f"流量公式: Q = μs·n·b·e·√(2g·ΔH)")
            print(f"         = {self.mus}×{self.n}×{self.b}×{e_design:.2f}×√(2×{self.g}×{delta_H:.2f})")
        
        print(f"过闸流量: Q = {Q_design:.2f} m³/s")
        
        print(f"\n【调度方案】")
        for i, s in enumerate(schemes, 1):
            print(f"\n方案{i}：{s['name']}")
            print(f"  开度: e = {s['e']:.2f} m（{s['e_ratio']:.0%}×H₁）")
            print(f"  流量: Q = {s['Q']:.2f} m³/s")
            print(f"  流态: {s['flow_type']}")
        
        print(f"\n✓ 水闸调度运行分析完成")
        print(f"\n{'='*70}\n")


def main():
    b = 10
    n = 3
    H1 = 8
    H2 = 5
    mu0 = 0.60
    mus = 0.85
    epsilon = 0.62
    
    sluice = SluiceOperation(b, n, H1, H2, mu0, mus, epsilon)
    sluice.print_results()
    sluice.plot_analysis()


if __name__ == "__main__":
    main()
