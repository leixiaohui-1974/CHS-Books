#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第04章 地下水与渗流 - 题目1：达西定律基础

题目描述：
某砂土层，已知：
- 厚度H=5m
- 渗透系数k=20m/d
- 水平距离L=100m
- 两测压管水位差Δh=2m
- 孔隙率n=0.35

求：
(1) 水力坡度i
(2) 渗透流速v（达西流速）
(3) 实际流速u
(4) 单宽流量q
(5) 渗透系数变化的影响

知识点：
- 达西定律 v = ki
- 渗透流速与实际流速
- 水力坡度
- 单宽流量

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DarcyLawAnalysis:
    """达西定律分析类"""
    
    def __init__(self, H: float, k: float, L: float, delta_h: float, 
                 n: float = 0.35):
        """
        初始化参数
        
        Parameters:
        -----------
        H : float
            土层厚度 (m)
        k : float
            渗透系数 (m/d)
        L : float
            水平距离 (m)
        delta_h : float
            水位差 (m)
        n : float
            孔隙率
        """
        self.H = H
        self.k = k
        self.L = L
        self.delta_h = delta_h
        self.n = n
    
    def hydraulic_gradient(self) -> float:
        """
        计算水力坡度
        
        i = Δh / L
        
        Returns:
        --------
        float : 水力坡度
        """
        return self.delta_h / self.L
    
    def darcy_velocity(self) -> float:
        """
        计算渗透流速（达西流速）
        
        v = ki
        
        Returns:
        --------
        float : 渗透流速 (m/d)
        """
        i = self.hydraulic_gradient()
        return self.k * i
    
    def actual_velocity(self) -> float:
        """
        计算实际流速
        
        u = v / n
        
        Returns:
        --------
        float : 实际流速 (m/d)
        """
        v = self.darcy_velocity()
        return v / self.n
    
    def unit_width_discharge(self) -> float:
        """
        计算单宽流量
        
        q = vH = kiH
        
        Returns:
        --------
        float : 单宽流量 (m²/d)
        """
        v = self.darcy_velocity()
        return v * self.H
    
    def permeability_analysis(self, k_range: tuple = (10, 50), 
                             n_points: int = 50) -> tuple:
        """
        渗透系数影响分析
        
        Parameters:
        -----------
        k_range : tuple
            渗透系数范围 (m/d)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (k_array, v_array, q_array)
        """
        k_array = np.linspace(k_range[0], k_range[1], n_points)
        
        i = self.hydraulic_gradient()
        v_array = k_array * i
        q_array = v_array * self.H
        
        return k_array, v_array, q_array
    
    def gradient_analysis(self, i_range: tuple = (0.001, 0.1), 
                         n_points: int = 50) -> tuple:
        """
        水力坡度影响分析
        
        Parameters:
        -----------
        i_range : tuple
            水力坡度范围
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (i_array, v_array, q_array)
        """
        i_array = np.linspace(i_range[0], i_range[1], n_points)
        
        v_array = self.k * i_array
        q_array = v_array * self.H
        
        return i_array, v_array, q_array
    
    def thickness_analysis(self, H_range: tuple = (1, 10), 
                          n_points: int = 50) -> tuple:
        """
        土层厚度影响分析
        
        Parameters:
        -----------
        H_range : tuple
            厚度范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (H_array, q_array)
        """
        H_array = np.linspace(H_range[0], H_range[1], n_points)
        
        v = self.darcy_velocity()
        q_array = v * H_array
        
        return H_array, q_array
    
    def porosity_analysis(self, n_range: tuple = (0.2, 0.5), 
                         n_points: int = 50) -> tuple:
        """
        孔隙率影响分析
        
        Parameters:
        -----------
        n_range : tuple
            孔隙率范围
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (n_array, u_array)
        """
        n_array = np.linspace(n_range[0], n_range[1], n_points)
        
        v = self.darcy_velocity()
        u_array = v / n_array
        
        return n_array, u_array
    
    def plot_analysis(self):
        """绘制达西定律分析图"""
        fig = plt.figure(figsize=(15, 10))
        
        # 计算当前参数
        i = self.hydraulic_gradient()
        v = self.darcy_velocity()
        u = self.actual_velocity()
        q = self.unit_width_discharge()
        
        # 图1：达西定律示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制渗流示意图
        x = np.array([0, self.L])
        h1 = self.delta_h + 5  # 上游水位
        h2 = 5  # 下游水位（基准）
        
        # 水位线
        ax1.fill_between(x, 0, [h1, h2], color='lightblue', alpha=0.5, label='渗流区')
        ax1.plot(x, [h1, h2], 'b-', linewidth=2, label='水位线')
        
        # 土层
        ax1.fill_between(x, 0, -2, color='brown', alpha=0.3, label='不透水层')
        ax1.plot(x, [0, 0], 'k-', linewidth=2)
        
        # 标注
        ax1.annotate('', xy=(self.L/2, h2), xytext=(self.L/2, h1),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(self.L/2 + 5, (h1+h2)/2, f'Δh = {self.delta_h}m',
                fontsize=10, fontweight='bold', color='red')
        
        ax1.annotate('', xy=(self.L, -2.5), xytext=(0, -2.5),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax1.text(self.L/2, -3, f'L = {self.L}m',
                fontsize=10, fontweight='bold', color='blue', ha='center')
        
        # 流速矢量
        n_arrows = 5
        x_arrows = np.linspace(10, self.L-10, n_arrows)
        for x_a in x_arrows:
            h_a = h1 - (h1-h2) * x_a / self.L
            ax1.arrow(x_a, h_a - 1, 10, 0, head_width=0.3, head_length=3,
                     fc='green', ec='green', alpha=0.7)
        
        ax1.text(self.L/2, h1 - 1, f'v = {v:.3f} m/d',
                fontsize=11, fontweight='bold', color='green',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.set_xlim(-10, self.L + 20)
        ax1.set_ylim(-4, h1 + 2)
        ax1.set_xlabel('距离 (m)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('高程 (m)', fontsize=10, fontweight='bold')
        ax1.set_title('达西定律示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # 图2：达西定律公式
        ax2 = plt.subplot(3, 3, 2)
        
        formula_text = f"""
达西定律

v = ki

其中：
v = 渗透流速 (m/d)
k = 渗透系数 (m/d)
i = 水力坡度

当前计算：
i = Δh/L = {self.delta_h}/{self.L} = {i:.4f}
k = {self.k} m/d
v = {self.k} × {i:.4f} = {v:.4f} m/d

实际流速：
u = v/n = {v:.4f}/{self.n} = {u:.4f} m/d

单宽流量：
q = vH = {v:.4f} × {self.H} = {q:.4f} m²/d
"""
        
        ax2.text(0.1, 0.5, formula_text, fontsize=10, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax2.axis('off')
        ax2.set_title('达西定律计算', fontsize=13, fontweight='bold')
        
        # 图3：流速对比
        ax3 = plt.subplot(3, 3, 3)
        
        velocities = ['渗透流速\nv', '实际流速\nu']
        values = [v, u]
        colors = ['blue', 'red']
        
        bars = ax3.bar(velocities, values, color=colors, alpha=0.7)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.4f}\nm/d',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax3.set_ylabel('流速 (m/d)', fontsize=11, fontweight='bold')
        ax3.set_title('渗透流速 vs 实际流速', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        ax3.text(0.5, max(values) * 0.5, 
                f'u = v/n\n= {v:.4f}/{self.n}\n= {u:.4f} m/d\n\n实际流速是渗透流速的\n{u/v:.2f}倍',
                ha='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：渗透系数影响
        ax4 = plt.subplot(3, 3, 4)
        
        k_array, v_k, q_k = self.permeability_analysis()
        
        ax4_twin = ax4.twinx()
        
        line1 = ax4.plot(k_array, v_k, 'b-', linewidth=2.5, 
                        label='渗透流速v', marker='o', markersize=4, markevery=5)
        line2 = ax4_twin.plot(k_array, q_k, 'r-', linewidth=2.5,
                             label='单宽流量q', marker='s', markersize=4, markevery=5)
        
        # 当前点
        ax4.plot([self.k], [v], 'go', markersize=12, label='当前状态')
        
        ax4.set_xlabel('渗透系数 k (m/d)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('渗透流速 v (m/d)', fontsize=11, fontweight='bold', color='b')
        ax4_twin.set_ylabel('单宽流量 q (m²/d)', fontsize=11, fontweight='bold', color='r')
        ax4.set_title('渗透系数的影响', fontsize=13, fontweight='bold')
        
        ax4.tick_params(axis='y', labelcolor='b')
        ax4_twin.tick_params(axis='y', labelcolor='r')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax4.legend(lines, labels, fontsize=9)
        ax4.grid(True, alpha=0.3)
        
        # 标注关系
        ax4.text(35, max(v_k) * 0.6,
                'v ∝ k\nq ∝ k\n（线性关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图5：水力坡度影响
        ax5 = plt.subplot(3, 3, 5)
        
        i_array, v_i, q_i = self.gradient_analysis()
        
        ax5_twin = ax5.twinx()
        
        line1 = ax5.plot(i_array * 1000, v_i, 'b-', linewidth=2.5,
                        label='渗透流速v')
        line2 = ax5_twin.plot(i_array * 1000, q_i, 'r-', linewidth=2.5,
                             label='单宽流量q')
        
        # 当前点
        ax5.plot([i * 1000], [v], 'go', markersize=12, label='当前状态')
        
        ax5.set_xlabel('水力坡度 i (‰)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('渗透流速 v (m/d)', fontsize=11, fontweight='bold', color='b')
        ax5_twin.set_ylabel('单宽流量 q (m²/d)', fontsize=11, fontweight='bold', color='r')
        ax5.set_title('水力坡度的影响', fontsize=13, fontweight='bold')
        
        ax5.tick_params(axis='y', labelcolor='b')
        ax5_twin.tick_params(axis='y', labelcolor='r')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax5.legend(lines, labels, fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 图6：厚度影响
        ax6 = plt.subplot(3, 3, 6)
        
        H_array, q_H = self.thickness_analysis()
        
        ax6.plot(H_array, q_H, 'b-', linewidth=2.5, label='单宽流量q')
        ax6.plot([self.H], [q], 'ro', markersize=12, label='当前状态')
        
        ax6.set_xlabel('土层厚度 H (m)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('单宽流量 q (m²/d)', fontsize=11, fontweight='bold')
        ax6.set_title('土层厚度的影响', fontsize=13, fontweight='bold')
        ax6.legend(fontsize=10)
        ax6.grid(True, alpha=0.3)
        
        ax6.text(6, max(q_H) * 0.6,
                'q ∝ H\n（线性关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图7：孔隙率影响
        ax7 = plt.subplot(3, 3, 7)
        
        n_array, u_n = self.porosity_analysis()
        
        ax7.plot(n_array, u_n, 'r-', linewidth=2.5, label='实际流速u')
        ax7.plot([self.n], [u], 'go', markersize=12, label='当前状态')
        
        # 渗透流速参考线
        ax7.axhline(y=v, color='blue', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'渗透流速v={v:.3f}')
        
        ax7.set_xlabel('孔隙率 n', fontsize=11, fontweight='bold')
        ax7.set_ylabel('实际流速 u (m/d)', fontsize=11, fontweight='bold')
        ax7.set_title('孔隙率的影响', fontsize=13, fontweight='bold')
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        ax7.text(0.35, max(u_n) * 0.7,
                'u ∝ 1/n\n（反比关系）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图8：综合参数对比
        ax8 = plt.subplot(3, 3, 8)
        
        params = ['水力坡度\ni', '渗透系数\nk', '厚度\nH', '孔隙率\nn']
        values_norm = [i / 0.05, self.k / 30, self.H / 7.5, self.n / 0.4]
        colors_bar = ['blue', 'green', 'orange', 'red']
        
        bars = ax8.bar(params, values_norm, color=colors_bar, alpha=0.7)
        
        # 标注实际值
        actual_values = [i, self.k, self.H, self.n]
        for bar, val in zip(bars, actual_values):
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax8.set_ylabel('归一化值', fontsize=11, fontweight='bold')
        ax8.set_title('参数归一化对比', fontsize=13, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='y')
        ax8.set_ylim(0, max(values_norm) * 1.2)
        
        # 图9：达西定律适用性
        ax9 = plt.subplot(3, 3, 9)
        
        applicability_text = """
达西定律适用性

✓ 适用条件：
• 层流渗流（Re < 1-10）
• 连续介质
• 线性关系（v ∝ i）
• 稳定渗流

✗ 不适用条件：
• 紊流渗流（Re > 10）
• 裂隙介质
• 非线性渗流
• 非稳定渗流

物理意义：
• v：渗透流速（表观流速）
• u：实际流速（孔隙中）
• 关系：u = v/n

工程应用：
• 地下水资源评价
• 基坑降水设计
• 渗渠设计
• 坝基渗流分析
"""
        
        ax9.text(0.1, 0.5, applicability_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax9.axis('off')
        ax9.set_title('达西定律适用性', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("达西定律计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  土层厚度：H = {self.H} m")
        print(f"  渗透系数：k = {self.k} m/d")
        print(f"  水平距离：L = {self.L} m")
        print(f"  水位差：Δh = {self.delta_h} m")
        print(f"  孔隙率：n = {self.n}")
        
        # (1) 水力坡度
        i = self.hydraulic_gradient()
        
        print(f"\n(1) 水力坡度：")
        print(f"  i = Δh / L")
        print(f"    = {self.delta_h} / {self.L}")
        print(f"    = {i:.4f}")
        print(f"    = 1/{1/i:.1f}")
        
        # (2) 渗透流速
        v = self.darcy_velocity()
        
        print(f"\n(2) 渗透流速（达西流速）：")
        print(f"  达西定律：v = ki")
        print(f"    v = {self.k} × {i:.4f}")
        print(f"      = {v:.4f} m/d")
        print(f"      = {v/24:.4f} m/h")
        print(f"      = {v/86400:.2e} m/s")
        
        print(f"\n  物理意义：")
        print(f"    • 渗透流速（表观流速）")
        print(f"    • 单位面积（含孔隙和固体）的流量")
        print(f"    • 与渗透系数和水力坡度成正比")
        
        # (3) 实际流速
        u = self.actual_velocity()
        
        print(f"\n(3) 实际流速：")
        print(f"  u = v / n")
        print(f"    = {v:.4f} / {self.n}")
        print(f"    = {u:.4f} m/d")
        print(f"    = {u/24:.4f} m/h")
        
        print(f"\n  对比：")
        print(f"    渗透流速：v = {v:.4f} m/d")
        print(f"    实际流速：u = {u:.4f} m/d")
        print(f"    比值：u/v = {u/v:.3f} = 1/n")
        
        print(f"\n  物理意义：")
        print(f"    • 水在孔隙中的实际运动速度")
        print(f"    • 大于渗透流速（1/n倍）")
        print(f"    • 孔隙率越小，实际流速越大")
        
        # (4) 单宽流量
        q = self.unit_width_discharge()
        
        print(f"\n(4) 单宽流量：")
        print(f"  q = vH = kiH")
        print(f"    = {v:.4f} × {self.H}")
        print(f"    = {q:.4f} m²/d")
        print(f"    = {q/24:.4f} m²/h")
        
        print(f"\n  或：")
        print(f"  q = kiH")
        print(f"    = {self.k} × {i:.4f} × {self.H}")
        print(f"    = {q:.4f} m²/d")
        
        print(f"\n  若渠宽b=10m，则总流量：")
        Q = q * 10
        print(f"  Q = qb = {q:.4f} × 10 = {Q:.2f} m³/d")
        
        # (5) 渗透系数变化
        print(f"\n(5) 渗透系数变化影响：")
        
        k_values = [10, 20, 30, 40, 50]
        print(f"\n  {'k(m/d)':<10} {'v(m/d)':<12} {'q(m²/d)':<12} {'变化率':<10}")
        print(f"  {'-'*50}")
        
        for k_val in k_values:
            v_val = k_val * i
            q_val = v_val * self.H
            change = (k_val / self.k - 1) * 100 if self.k > 0 else 0
            marker = " ✓" if abs(k_val - self.k) < 0.1 else ""
            print(f"  {k_val:<10} {v_val:<12.4f} {q_val:<12.4f} {change:+.1f}%{marker}")
        
        print(f"\n  结论：")
        print(f"    • v ∝ k（线性关系）")
        print(f"    • q ∝ k（线性关系）")
        print(f"    • k增大1倍 → v和q增大1倍")
        
        # 影响因素总结
        print(f"\n影响因素分析：")
        print(f"  【渗透系数k】")
        print(f"    • 取决于土壤性质")
        print(f"    • 砂土：k = 1-100 m/d")
        print(f"    • 粉土：k = 0.01-1 m/d")
        print(f"    • 粘土：k < 0.01 m/d")
        
        print(f"\n  【水力坡度i】")
        print(f"    • 取决于水位差和距离")
        print(f"    • i = Δh / L")
        print(f"    • 一般：i = 0.001-0.1")
        
        print(f"\n  【厚度H】")
        print(f"    • 影响总流量q")
        print(f"    • 不影响渗透流速v")
        print(f"    • q ∝ H")
        
        print(f"\n  【孔隙率n】")
        print(f"    • 影响实际流速u")
        print(f"    • 不影响渗透流速v")
        print(f"    • u = v/n")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 达西定律：v = ki")
        print("2. 水力坡度：i = Δh/L")
        print("3. 实际流速：u = v/n")
        print("4. 单宽流量：q = vH = kiH")
        print("5. 线性关系：v ∝ k, v ∝ i, q ∝ H")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第04章 地下水与渗流 - 题目1：达西定律基础")
    print("💧" * 35 + "\n")
    
    # 题目参数
    H = 5.0           # 土层厚度5m
    k = 20.0          # 渗透系数20m/d
    L = 100.0         # 水平距离100m
    delta_h = 2.0     # 水位差2m
    n = 0.35          # 孔隙率0.35
    
    # 创建达西定律分析对象
    darcy = DarcyLawAnalysis(H=H, k=k, L=L, delta_h=delta_h, n=n)
    
    # 打印结果
    darcy.print_results()
    
    # 绘图
    print("\n正在绘制达西定律分析图...")
    darcy.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
