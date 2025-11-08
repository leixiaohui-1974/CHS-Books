# -*- coding: utf-8 -*-
"""
第08章 渗流计算 - 题4：渗流网绘制与分析

问题描述：
    混凝土坝下游渗流分析
    坝高H = 20m，坝底宽B = 40m
    上游水深h1 = 18m，下游水深h2 = 2m
    地基深度D = 10m，渗透系数K = 0.0001 m/s
    
    求：
    1. 渗流网绘制（流线与等势线）
    2. 单宽渗流量q
    3. 渗透坡降分布
    4. 渗透压力分布
    5. 出逸点渗透坡降（管涌验证）

核心公式：
    1. 单宽流量：q = K·H·(nf/nd)
       nf: 流槽数, nd: 势降数
    2. 渗透坡降：i = Δh/(Δl)
    3. 出逸坡降：i_出 = Δh/Δl（最后一格）
    4. 允许坡降：[i] = (γs-γw)/γw ≈ 1.0

考试要点：
    - 渗流网基本性质
    - 正交性与曲边正方形
    - 渗流量计算
    - 管涌判别

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SeepageNet:
    """渗流网分析"""
    
    def __init__(self, H: float, B: float, h1: float, h2: float, 
                 D: float, K: float):
        self.H = H  # 坝高
        self.B = B  # 坝底宽
        self.h1 = h1  # 上游水深
        self.h2 = h2  # 下游水深
        self.D = D  # 地基深度
        self.K = K  # 渗透系数
        self.g = 9.8
        
    def head_loss(self) -> float:
        """总水头损失"""
        return self.h1 - self.h2
    
    def unit_seepage(self, nf: int = 4, nd: int = 10) -> float:
        """
        单宽渗流量
        q = K·ΔH·(nf/nd)
        nf: 流槽数（流线间隔数）
        nd: 势降数（等势线间隔数）
        """
        delta_H = self.head_loss()
        q = self.K * delta_H * (nf / nd)
        return q
    
    def generate_flow_net(self, nf: int = 4, nd: int = 10) -> Tuple[List, List]:
        """
        生成渗流网（简化）
        实际工程中需要数值解法（有限元、边界元等）
        这里采用简化的解析解近似
        """
        # 流线（简化为抛物线族）
        flowlines = []
        for i in range(nf + 1):
            ratio = i / nf
            x = np.linspace(0, self.B, 100)
            # 简化：流线从上游水位到下游水位的抛物线
            y = self.D * (1 - ratio) - (self.D * (1 - ratio) - self.h2 + self.h1 * ratio) * (x / self.B) ** 2
            flowlines.append({'x': x, 'y': y, 'id': i})
        
        # 等势线（简化为竖直线族）
        equipotentials = []
        delta_H = self.head_loss()
        for j in range(nd + 1):
            x_pos = self.B * (j / nd)
            head = self.h1 - delta_H * (j / nd)
            # 等势线高度
            y = np.linspace(-self.D, head, 50)
            x = np.ones_like(y) * x_pos
            equipotentials.append({'x': x, 'y': y, 'head': head, 'id': j})
        
        return flowlines, equipotentials
    
    def hydraulic_gradient_distribution(self, nd: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """渗透坡降分布"""
        x_range = np.linspace(0, self.B, nd + 1)
        delta_H = self.head_loss()
        
        # 简化：假设坡降沿程均匀分布
        # 实际中坡降在上下游附近较大
        i_avg = delta_H / self.B
        
        # 考虑边界效应（简化）
        i_range = []
        for x in x_range:
            if x < self.B * 0.2:  # 上游段
                i_range.append(i_avg * 1.5)
            elif x > self.B * 0.8:  # 下游段
                i_range.append(i_avg * 2.0)
            else:  # 中间段
                i_range.append(i_avg)
        
        return x_range, np.array(i_range)
    
    def exit_gradient(self) -> float:
        """出逸点渗透坡降"""
        # 出逸点通常是最大坡降位置
        delta_H = self.head_loss()
        # 简化估算：i_出 ≈ 2~3倍平均坡降
        i_avg = delta_H / self.B
        i_exit = i_avg * 2.5
        return i_exit
    
    def piping_check(self) -> Tuple[bool, float]:
        """
        管涌验证
        允许坡降：[i] = (γs-γw)/γw
        γs ≈ 26 kN/m³, γw ≈ 10 kN/m³
        [i] ≈ 1.0~1.2
        """
        i_exit = self.exit_gradient()
        i_allow = 1.0  # 允许坡降
        
        safety_factor = i_allow / i_exit
        is_safe = safety_factor > 1.5  # 安全系数>1.5
        
        return is_safe, safety_factor
    
    def seepage_pressure(self, nd: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """渗透压力分布"""
        x_range = np.linspace(0, self.B, nd + 1)
        delta_H = self.head_loss()
        
        # 渗透压力：u = γw × h（h为测压管水头）
        pressure = []
        for i, x in enumerate(x_range):
            h = self.h1 - delta_H * (i / nd)
            # 假设在地基底部
            u = self.g * 1000 * h  # Pa
            pressure.append(u / 1000)  # 转kPa
        
        return x_range, np.array(pressure)
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        nf = 4
        nd = 10
        q = self.unit_seepage(nf, nd)
        flowlines, equipotentials = self.generate_flow_net(nf, nd)
        
        # 1. 渗流网
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制坝体
        dam_x = [0, 0, self.B, self.B]
        dam_y = [0, self.H, self.H, 0]
        ax1.fill(dam_x, dam_y, color='gray', alpha=0.3, label='坝体')
        ax1.plot(dam_x + [dam_x[0]], dam_y + [dam_y[0]], 'k-', linewidth=2)
        
        # 上下游水位
        ax1.plot([-5, 0], [self.h1, self.h1], 'b-', linewidth=2, label=f'上游h₁={self.h1}m')
        ax1.plot([self.B, self.B+5], [self.h2, self.h2], 'g-', linewidth=2, label=f'下游h₂={self.h2}m')
        
        # 地基
        ax1.fill([0, self.B, self.B, 0], [-self.D, -self.D, 0, 0], 
                color='brown', alpha=0.2, label='地基')
        
        # 流线
        for fl in flowlines:
            ax1.plot(fl['x'], fl['y'], 'b-', linewidth=1, alpha=0.6)
        
        # 等势线
        for eq in equipotentials:
            ax1.plot(eq['x'], eq['y'], 'r--', linewidth=1, alpha=0.6)
        
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title(f'渗流网（nf={nf}, nd={nd}）', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-5, self.B+5)
        ax1.set_ylim(-self.D-2, self.H+2)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        delta_H = self.head_loss()
        
        ax2.text(0.5, 0.95, '渗流参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'坝高: H = {self.H} m', fontsize=10)
        ax2.text(0.1, 0.72, f'坝底宽: B = {self.B} m', fontsize=10)
        ax2.text(0.1, 0.62, f'水头差: ΔH = {delta_H} m', fontsize=10, color='red')
        ax2.text(0.1, 0.52, f'渗透系数: K = {self.K} m/s', fontsize=10)
        ax2.text(0.1, 0.40, f'流槽数: nf = {nf}', fontsize=10)
        ax2.text(0.1, 0.30, f'势降数: nd = {nd}', fontsize=10)
        ax2.text(0.1, 0.18, f'单宽流量: q = {q*1000:.3f} L/(s·m)', fontsize=10, color='blue', fontweight='bold')
        ax2.text(0.1, 0.05, f'q = K·ΔH·(nf/nd)', fontsize=9, color='gray')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 流槽数影响
        ax3 = plt.subplot(3, 3, 3)
        
        nf_range = np.arange(1, 10)
        q_nf = [self.unit_seepage(nf_val, nd)*1000 for nf_val in nf_range]
        
        ax3.plot(nf_range, q_nf, 'b-o', linewidth=2, markersize=6)
        ax3.plot(nf, q*1000, 'ro', markersize=10, label=f'nf={nf}')
        
        ax3.set_xlabel('流槽数 nf', fontsize=10)
        ax3.set_ylabel('单宽流量 q (L/(s·m))', fontsize=10)
        ax3.set_title('流槽数影响', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 渗透坡降分布
        ax4 = plt.subplot(3, 3, 4)
        
        x_i, i_range = self.hydraulic_gradient_distribution(nd)
        i_exit = self.exit_gradient()
        i_allow = 1.0
        
        ax4.plot(x_i, i_range, 'b-o', linewidth=2, markersize=6, label='坡降分布')
        ax4.axhline(i_allow, color='r', linestyle='--', linewidth=2, label=f'允许坡降[i]={i_allow}')
        ax4.axhline(i_exit, color='orange', linestyle='--', linewidth=1.5, 
                   alpha=0.7, label=f'出逸坡降i_出={i_exit:.3f}')
        
        # 标注危险区
        if i_exit > i_allow:
            ax4.fill_between([self.B*0.8, self.B], [0, 0], [2, 2], 
                            color='red', alpha=0.1, label='危险区')
        
        ax4.set_xlabel('距离 x (m)', fontsize=10)
        ax4.set_ylabel('渗透坡降 i', fontsize=10)
        ax4.set_title('渗透坡降分布', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, max(i_range)*1.2)
        
        # 5. 渗透压力分布
        ax5 = plt.subplot(3, 3, 5)
        
        x_u, u_range = self.seepage_pressure(nd)
        
        ax5.plot(x_u, u_range, 'g-o', linewidth=2, markersize=6)
        ax5.fill_between(x_u, 0, u_range, color='green', alpha=0.2)
        
        ax5.set_xlabel('距离 x (m)', fontsize=10)
        ax5.set_ylabel('渗透压力 u (kPa)', fontsize=10)
        ax5.set_title('渗透压力分布', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # 6. 管涌验证
        ax6 = plt.subplot(3, 3, 6)
        ax6.axis('off')
        
        is_safe, K_safe = self.piping_check()
        
        ax6.text(0.5, 0.95, '管涌验证', fontsize=11, ha='center', fontweight='bold')
        ax6.text(0.1, 0.80, f'出逸坡降: i_出 = {i_exit:.3f}', fontsize=10, color='red')
        ax6.text(0.1, 0.70, f'允许坡降: [i] = {i_allow:.2f}', fontsize=10, color='blue')
        ax6.text(0.1, 0.55, f'安全系数: K = {K_safe:.2f}', fontsize=11, 
                color='green' if is_safe else 'red', fontweight='bold')
        
        if is_safe:
            ax6.text(0.1, 0.40, '✓ 满足要求（K>1.5）', fontsize=10, color='green', fontweight='bold')
            ax6.text(0.1, 0.25, '渗流稳定，无管涌风险', fontsize=9)
        else:
            ax6.text(0.1, 0.40, '✗ 不满足要求（K<1.5）', fontsize=10, color='red', fontweight='bold')
            ax6.text(0.1, 0.25, '⚠ 存在管涌风险！', fontsize=9, color='red')
            ax6.text(0.1, 0.15, '建议：加反滤层', fontsize=9, color='orange')
        
        ax6.set_title('安全性评价', fontsize=12, fontweight='bold')
        
        # 7. 渗透系数影响
        ax7 = plt.subplot(3, 3, 7)
        
        K_range = np.logspace(-5, -3, 50)
        q_K = [K_val * delta_H * (nf/nd) * 1000 for K_val in K_range]
        
        ax7.plot(K_range, q_K, 'b-', linewidth=2)
        ax7.plot(self.K, q*1000, 'ro', markersize=10, label=f'K={self.K}m/s')
        
        ax7.set_xlabel('渗透系数 K (m/s)', fontsize=10)
        ax7.set_ylabel('单宽流量 q (L/(s·m))', fontsize=10)
        ax7.set_title('渗透系数影响', fontsize=12, fontweight='bold')
        ax7.set_xscale('log')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 渗流网性质
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '渗流网基本性质', fontsize=11, ha='center', fontweight='bold')
        
        ax8.text(0.1, 0.82, '1. 正交性:', fontsize=10, color='blue', fontweight='bold')
        ax8.text(0.15, 0.72, '• 流线与等势线相互正交', fontsize=9)
        
        ax8.text(0.1, 0.58, '2. 曲边正方形:', fontsize=10, color='green', fontweight='bold')
        ax8.text(0.15, 0.48, '• 流线与等势线围成的网格', fontsize=9)
        ax8.text(0.15, 0.40, '• 长宽比≈1', fontsize=9)
        
        ax8.text(0.1, 0.26, '3. 流量公式:', fontsize=10, color='red', fontweight='bold')
        ax8.text(0.15, 0.16, 'q = K·ΔH·(nf/nd)', fontsize=9)
        ax8.text(0.15, 0.08, 'nf↑ → q↑ (流槽增多)', fontsize=9)
        ax8.text(0.15, 0.00, 'nd↑ → q↓ (势降增多)', fontsize=9)
        
        ax8.set_title('理论基础', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['水头差', f'{delta_H:.1f}', 'm'],
            ['流槽数', f'{nf}', '-'],
            ['势降数', f'{nd}', '-'],
            ['单宽流量', f'{q*1000:.3f}', 'L/(s·m)'],
            ['平均坡降', f'{delta_H/self.B:.4f}', '-'],
            ['出逸坡降', f'{i_exit:.3f}', '-'],
            ['允许坡降', f'{i_allow:.2f}', '-'],
            ['安全系数', f'{K_safe:.2f}', '-'],
            ['安全性', '✓' if is_safe else '✗', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮安全性
        if is_safe:
            table[(9, 1)].set_facecolor('#90EE90')
        else:
            table[(9, 1)].set_facecolor('#FFB6C1')
        table[(9, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch08_problem04_seepage_net.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch08_problem04_seepage_net.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第08章 渗流计算 - 题4：渗流网绘制与分析")
        print("="*70)
        
        nf = 4
        nd = 10
        q = self.unit_seepage(nf, nd)
        delta_H = self.head_loss()
        i_exit = self.exit_gradient()
        is_safe, K_safe = self.piping_check()
        
        print(f"\n【工程参数】")
        print(f"坝高: H = {self.H} m")
        print(f"坝底宽: B = {self.B} m")
        print(f"上游水深: h₁ = {self.h1} m")
        print(f"下游水深: h₂ = {self.h2} m")
        print(f"地基深度: D = {self.D} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400:.3f} m/d")
        
        print(f"\n【渗流网】")
        print(f"流槽数: nf = {nf}")
        print(f"势降数: nd = {nd}")
        print(f"水头损失: ΔH = {delta_H} m")
        
        print(f"\n【单宽流量】")
        print(f"q = K·ΔH·(nf/nd)")
        print(f"  = {self.K}×{delta_H}×({nf}/{nd})")
        print(f"  = {q:.6f} m³/(s·m) = {q*1000:.3f} L/(s·m)")
        
        print(f"\n【渗透坡降】")
        print(f"平均坡降: i_avg = ΔH/B = {delta_H/self.B:.4f}")
        print(f"出逸坡降: i_出 = {i_exit:.3f}（下游出口处）")
        print(f"允许坡降: [i] = 1.0（砂性土）")
        
        print(f"\n【管涌验证】")
        print(f"安全系数: K = [i]/i_出 = {K_safe:.2f}")
        if is_safe:
            print(f"✓ K = {K_safe:.2f} > 1.5，满足要求，无管涌风险")
        else:
            print(f"✗ K = {K_safe:.2f} < 1.5，不满足要求，存在管涌风险！")
            print(f"⚠ 建议：设置反滤层、增加排水设施")
        
        print(f"\n✓ 渗流网分析完成")
        print(f"\n{'='*70}\n")


def main():
    H = 20
    B = 40
    h1 = 18
    h2 = 2
    D = 10
    K = 0.0001
    
    net = SeepageNet(H, B, h1, h2, D, K)
    net.print_results()
    net.plot_analysis()


if __name__ == "__main__":
    main()
