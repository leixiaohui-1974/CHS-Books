"""
《水力学考研1000题详解》配套代码
题目641：堰闸出流计算

问题描述：
一矩形薄壁堰，堰顶宽度B=2m，堰高P=1.5m，上游水深H₀=2.0m（从堰底算起）。
堰后为自由出流。流量系数m=0.42。
要求：
(1) 计算作用水头H（从堰顶算起）
(2) 计算通过堰的流量Q
(3) 分析堰流的水力特性
(4) 如果改为宽顶堰（堰顶宽度b=0.5m），计算流量
(5) 如果改为闸孔出流（闸孔高度e=0.8m），计算流量

考点：
1. 薄壁堰流量公式：Q = (2/3)m·B·√(2g)·H^(3/2)
2. 宽顶堰流量公式：Q = m·B·b·√(2g)·H^(3/2)
3. 闸孔自由出流：Q = μ·e·B·√(2g)·H
4. 闸孔淹没出流：Q = μs·e·B·√(2g)·(H₁-H₂)
5. 堰流、闸流判别

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, Arc

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WeirGateFlow:
    """堰闸出流计算类"""
    
    def __init__(self, B, P, H0, m_weir=0.42, g=9.8):
        """
        初始化
        
        参数:
            B: 堰宽（闸宽）(m)
            P: 堰高 (m)
            H0: 上游水深（从堰底算起）(m)
            m_weir: 薄壁堰流量系数
            g: 重力加速度 (m/s²)
        """
        self.B = B          # 堰宽 (m)
        self.P = P          # 堰高 (m)
        self.H0 = H0        # 上游水深 (m)
        self.m_weir = m_weir  # 流量系数
        self.g = g          # 重力加速度 (m/s²)
        
        # 计算作用水头
        self.H = self.H0 - self.P  # 从堰顶算起的水头
        
        # 薄壁堰流量计算
        self.calculate_thin_weir()
    
    def calculate_thin_weir(self):
        """计算薄壁堰流量"""
        # 薄壁堰流量公式
        # Q = (2/3) * m * B * √(2g) * H^(3/2)
        self.Q_thin = (2/3) * self.m_weir * self.B * np.sqrt(2*self.g) * (self.H ** 1.5)
        
        # 单宽流量
        self.q_thin = self.Q_thin / self.B
        
        # 收缩系数（近似）
        self.epsilon = 0.61  # 典型值
        
        # 堰顶流速
        self.v_crest = np.sqrt(2 * self.g * self.H)
    
    def calculate_broad_weir(self, b):
        """
        计算宽顶堰流量
        
        参数:
            b: 堰顶宽度 (m)
        """
        # 宽顶堰流量公式
        # Q = m * B * √(2g) * H^(3/2)
        # 对于宽顶堰，m ≈ 0.385（自由出流）
        m_broad = 0.385
        
        self.Q_broad = m_broad * self.B * np.sqrt(2*self.g) * (self.H ** 1.5)
        self.q_broad = self.Q_broad / self.B
        
        # 堰顶水深（临界水深）
        self.h_c = (2/3) * self.H
        
        # 堰顶流速
        self.v_broad = np.sqrt(self.g * self.h_c)
        
        return self.Q_broad
    
    def calculate_gate_flow(self, e, mu=0.60, submerged=False, H2=0):
        """
        计算闸孔出流
        
        参数:
            e: 闸孔高度 (m)
            mu: 流量系数
            submerged: 是否淹没出流
            H2: 下游水深（淹没出流时）(m)
        """
        if not submerged:
            # 自由出流
            # Q = μ * e * B * √(2g*H)
            H_gate = self.H0  # 从闸底算起
            self.Q_gate = mu * e * self.B * np.sqrt(2*self.g*H_gate)
            self.q_gate = self.Q_gate / self.B
            
            # 收缩断面水深
            self.h_contraction = self.epsilon * e
            
            # 收缩断面流速
            self.v_contraction = self.Q_gate / (self.B * self.h_contraction)
            
            self.gate_type = "自由出流"
            
        else:
            # 淹没出流
            # Q = μs * e * B * √(2g*(H₁-H₂))
            mu_s = 0.85 * mu  # 淹没流量系数
            H1 = self.H0
            self.Q_gate = mu_s * e * self.B * np.sqrt(2*self.g*(H1-H2))
            self.q_gate = self.Q_gate / self.B
            
            self.gate_type = "淹没出流"
            self.H2 = H2
        
        return self.Q_gate
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目641：堰闸出流计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"堰（闸）宽度: B = {self.B} m")
        print(f"堰高: P = {self.P} m")
        print(f"上游水深（从堰底算起）: H₀ = {self.H0} m")
        print(f"薄壁堰流量系数: m = {self.m_weir}")
        print(f"重力加速度: g = {self.g} m/s²")
        
        print("\n【堰闸出流基本概念】")
        print("1. 薄壁堰（Thin-plate weir）:")
        print("   • 堰顶厚度很小（<2mm）")
        print("   • 水流在堰顶发生急剧收缩")
        print("   • Q = (2/3)m·B·√(2g)·H^(3/2)")
        
        print("\n2. 宽顶堰（Broad-crested weir）:")
        print("   • 堰顶宽度较大（b > 0.67H）")
        print("   • 堰顶形成临界流")
        print("   • Q = m·B·√(2g)·H^(3/2)")
        
        print("\n3. 闸孔出流（Sluice gate flow）:")
        print("   • 自由出流: Q = μ·e·B·√(2g·H)")
        print("   • 淹没出流: Q = μs·e·B·√(2g·(H₁-H₂))")
        
        print("\n【计算过程】")
        
        # (1) 作用水头
        print("\n(1) 作用水头H（从堰顶算起）")
        print(f"    H = H₀ - P")
        print(f"      = {self.H0} - {self.P}")
        print(f"      = {self.H} m")
        
        # (2) 薄壁堰流量
        print("\n(2) 薄壁堰流量")
        print("    Q = (2/3) × m × B × √(2g) × H^(3/2)")
        print(f"      = (2/3) × {self.m_weir} × {self.B} × √(2×{self.g}) × {self.H}^(3/2)")
        print(f"      = (2/3) × {self.m_weir} × {self.B} × {np.sqrt(2*self.g):.3f} × {self.H**1.5:.3f}")
        print(f"      = {self.Q_thin:.4f} m³/s")
        print(f"\n    单宽流量: q = Q/B = {self.q_thin:.4f} m²/s")
        print(f"    堰顶流速: v = √(2gH) = {self.v_crest:.3f} m/s")
        
        # (3) 水力特性
        print("\n(3) 薄壁堰水力特性分析")
        print("    ① 水流形态:")
        print("       • 上游：缓流接近")
        print("       • 堰顶：急剧收缩，形成溢流水舌")
        print("       • 下游：跌落形成水跃")
        
        print("\n    ② 能量转换:")
        print(f"       • 位能: E_p = P + H = {self.P} + {self.H} = {self.P+self.H} m")
        print(f"       • 动能: E_k = v²/(2g) = {self.v_crest**2/(2*self.g):.3f} m")
        print(f"       • 总水头: E = {self.P+self.H+self.v_crest**2/(2*self.g):.3f} m")
        
        print("\n    ③ 水流收缩:")
        print(f"       • 收缩系数: ε ≈ {self.epsilon}")
        print("       • 下游水舌厚度减小")
        print("       • 流速增大")
        
        print("\n    ④ 适用条件:")
        print(f"       • H/P = {self.H/self.P:.3f}")
        print("       • 要求: 0.1 < H/P < 2.0（满足）" if 0.1 < self.H/self.P < 2.0 else "       • 要求: 0.1 < H/P < 2.0（不满足）")
        print("       • 上游需有足够长的渠道（> 3H）")
        print("       • 堰顶需锐缘")
    
    def print_broad_weir_results(self, b=0.5):
        """打印宽顶堰结果"""
        Q_broad = self.calculate_broad_weir(b)
        
        print("\n(4) 宽顶堰流量计算")
        print(f"    堰顶宽度: b = {b} m")
        print(f"    判别: b/H = {b/self.H:.3f}")
        
        if b/self.H > 0.67:
            print("    判断: b/H > 0.67，属于宽顶堰")
        else:
            print("    判断: b/H < 0.67，不完全满足宽顶堰条件")
        
        print("\n    宽顶堰流量公式:")
        print("    Q = m × B × √(2g) × H^(3/2)")
        print(f"      = 0.385 × {self.B} × √(2×{self.g}) × {self.H}^(3/2)")
        print(f"      = {Q_broad:.4f} m³/s")
        
        print(f"\n    堰顶临界水深: h_c = (2/3)H = {self.h_c:.3f} m")
        print(f"    堰顶流速: v = √(g·h_c) = {self.v_broad:.3f} m/s")
        print(f"    弗劳德数: Fr = v/√(g·h_c) = {self.v_broad/np.sqrt(self.g*self.h_c):.3f} ≈ 1（临界流）")
        
        print("\n    与薄壁堰比较:")
        ratio = Q_broad / self.Q_thin
        print(f"    Q_宽顶堰/Q_薄壁堰 = {ratio:.3f}")
        if ratio < 1:
            print(f"    宽顶堰流量较小（约{(1-ratio)*100:.1f}%）")
        else:
            print(f"    宽顶堰流量较大（约{(ratio-1)*100:.1f}%）")
    
    def print_gate_flow_results(self, e=0.8, mu=0.60):
        """打印闸孔出流结果"""
        Q_gate = self.calculate_gate_flow(e, mu)
        
        print("\n(5) 闸孔出流计算")
        print(f"    闸孔高度: e = {e} m")
        print(f"    流量系数: μ = {mu}")
        print(f"    出流类型: {self.gate_type}")
        
        print("\n    自由出流公式:")
        print("    Q = μ × e × B × √(2g·H₀)")
        print(f"      = {mu} × {e} × {self.B} × √(2×{self.g}×{self.H0})")
        print(f"      = {Q_gate:.4f} m³/s")
        
        print(f"\n    收缩断面水深: h_c = ε·e = {self.epsilon}×{e} = {self.h_contraction:.3f} m")
        print(f"    收缩断面流速: v_c = Q/(B·h_c) = {self.v_contraction:.3f} m/s")
        print(f"    弗劳德数: Fr = v_c/√(g·h_c) = {self.v_contraction/np.sqrt(self.g*self.h_contraction):.3f} > 1（急流）")
        
        print("\n    与薄壁堰比较:")
        ratio = Q_gate / self.Q_thin
        print(f"    Q_闸孔/Q_薄壁堰 = {ratio:.3f}")
        if ratio < 1:
            print(f"    闸孔流量较小（约{(1-ratio)*100:.1f}%）")
        else:
            print(f"    闸孔流量较大（约{(ratio-1)*100:.1f}%）")
        
        print("\n    淹没判别:")
        print("    自由出流条件: H₂/H₁ < 0.8")
        print("    淹没出流条件: H₂/H₁ ≥ 0.8")
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：薄壁堰示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_thin_weir(ax1)
        
        # 子图2：宽顶堰示意图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_broad_weir(ax2)
        
        # 子图3：闸孔出流示意图
        ax3 = plt.subplot(2, 2, 3)
        self._plot_gate_flow(ax3)
        
        # 子图4：流量对比
        ax4 = plt.subplot(2, 2, 4)
        self._plot_flow_comparison(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_thin_weir(self, ax):
        """绘制薄壁堰示意图"""
        # 堰体
        weir_width = 0.1
        weir = Rectangle((0.5-weir_width/2, 0), weir_width, self.P,
                        facecolor='gray', edgecolor='black', linewidth=2)
        ax.add_patch(weir)
        
        # 上游水体
        water_upstream = Rectangle((0, 0), 0.5-weir_width/2, self.H0,
                                  facecolor='lightblue', edgecolor='blue',
                                  linewidth=2, alpha=0.6)
        ax.add_patch(water_upstream)
        
        # 水面线
        ax.plot([0, 0.5-weir_width/2], [self.H0, self.H0], 'b-', linewidth=2)
        
        # 溢流水舌（抛物线）
        x_nappe = np.linspace(0.5+weir_width/2, 1.0, 50)
        y_nappe = self.P + self.H - 0.5*self.g*(x_nappe-0.5-weir_width/2)**2/self.v_crest**2
        y_nappe = np.maximum(y_nappe, 0)
        ax.plot(x_nappe, y_nappe, 'b-', linewidth=2)
        
        # 填充水舌
        y_bottom = np.zeros_like(x_nappe)
        ax.fill_between(x_nappe, y_bottom, y_nappe, facecolor='lightblue',
                       edgecolor='blue', alpha=0.4)
        
        # 标注
        # P
        ax.annotate('', xy=(0.3, 0), xytext=(0.3, self.P),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(0.25, self.P/2, f'P={self.P}m', fontsize=10, color='red',
               rotation=90, va='center')
        
        # H
        ax.annotate('', xy=(0.15, self.P), xytext=(0.15, self.H0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(0.10, (self.P+self.H0)/2, f'H={self.H}m', fontsize=10, color='green',
               rotation=90, va='center')
        
        # H0
        ax.annotate('', xy=(0.05, 0), xytext=(0.05, self.H0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax.text(0, self.H0/2, f'H₀={self.H0}m', fontsize=10, color='blue',
               rotation=90, va='center')
        
        # 流量
        ax.text(0.5, self.H0+0.3, f'Q={self.Q_thin:.3f}m³/s',
               fontsize=11, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(0, self.H0+0.5)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('薄壁堰出流', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_broad_weir(self, ax):
        """绘制宽顶堰示意图"""
        b = 0.5  # 堰顶宽度
        
        # 宽顶堰体（梯形）
        weir_points = [
            (0.3, 0),
            (0.3, self.P),
            (0.3+b, self.P),
            (0.3+b+0.1, 0)
        ]
        weir = Polygon(weir_points, facecolor='gray', edgecolor='black',
                      linewidth=2)
        ax.add_patch(weir)
        
        # 上游水体
        water_upstream = Rectangle((0, 0), 0.3, self.H0,
                                  facecolor='lightblue', edgecolor='blue',
                                  linewidth=2, alpha=0.6)
        ax.add_patch(water_upstream)
        
        # 堰顶水流（临界流）
        h_c = self.h_c
        water_crest = Rectangle((0.3, self.P), b, h_c,
                               facecolor='lightgreen', edgecolor='green',
                               linewidth=2, alpha=0.6)
        ax.add_patch(water_crest)
        
        # 下游跌落
        x_fall = np.linspace(0.3+b, 1.0, 30)
        y_fall = self.P + h_c - 0.5*self.g*(x_fall-0.3-b)**2/self.v_broad**2
        y_fall = np.maximum(y_fall, 0)
        ax.plot(x_fall, y_fall, 'g-', linewidth=2)
        ax.fill_between(x_fall, 0, y_fall, facecolor='lightblue', alpha=0.4)
        
        # 标注
        ax.annotate('', xy=(0.15, 0), xytext=(0.15, self.P),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(0.1, self.P/2, f'P={self.P}m', fontsize=10, color='red',
               rotation=90, va='center')
        
        ax.annotate('', xy=(0.3, self.P), xytext=(0.3+b, self.P),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
        ax.text(0.3+b/2, self.P-0.1, f'b={b}m', fontsize=10, color='purple',
               ha='center')
        
        ax.annotate('', xy=(0.05, self.P), xytext=(0.05, self.P+h_c),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(0, self.P+h_c/2, f'h_c={h_c:.2f}m', fontsize=10, color='green',
               rotation=90, va='center')
        
        # 流量
        ax.text(0.5, self.H0+0.3, f'Q={self.Q_broad:.3f}m³/s',
               fontsize=11, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(0, self.H0+0.5)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('宽顶堰出流（临界流）', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_gate_flow(self, ax):
        """绘制闸孔出流示意图"""
        e = 0.8
        
        # 闸门
        gate = Rectangle((0.5, e), 0.05, self.H0-e+0.5,
                        facecolor='brown', edgecolor='black', linewidth=2)
        ax.add_patch(gate)
        
        # 上游水体
        water_upstream = Rectangle((0, 0), 0.5, self.H0,
                                  facecolor='lightblue', edgecolor='blue',
                                  linewidth=2, alpha=0.6)
        ax.add_patch(water_upstream)
        
        # 闸孔出流（收缩）
        h_c = self.epsilon * e
        
        # 收缩断面
        x_contraction = 0.55 + e
        water_jet = Rectangle((0.55, 0), x_contraction-0.55, h_c,
                             facecolor='lightgreen', edgecolor='green',
                             linewidth=2, alpha=0.7)
        ax.add_patch(water_jet)
        
        # 下游射流扩散
        x_jet = np.linspace(x_contraction, 1.0, 30)
        y_top = h_c + (x_jet - x_contraction) * 0.3
        y_bottom = np.zeros_like(x_jet)
        ax.fill_between(x_jet, y_bottom, y_top, facecolor='lightblue',
                       edgecolor='blue', alpha=0.4)
        
        # 标注
        ax.annotate('', xy=(0.3, 0), xytext=(0.3, e),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(0.25, e/2, f'e={e}m', fontsize=10, color='red',
               rotation=90, va='center')
        
        ax.annotate('', xy=(0.15, 0), xytext=(0.15, self.H0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax.text(0.1, self.H0/2, f'H₀={self.H0}m', fontsize=10, color='blue',
               rotation=90, va='center')
        
        ax.annotate('', xy=(x_contraction+0.05, 0), xytext=(x_contraction+0.05, h_c),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(x_contraction+0.1, h_c/2, f'h_c={h_c:.2f}m', fontsize=10, color='green',
               rotation=90, va='center')
        
        # 流量
        ax.text(0.5, self.H0+0.3, f'Q={self.Q_gate:.3f}m³/s',
               fontsize=11, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 收缩系数
        ax.text(0.7, 0.15, f'ε={self.epsilon}\n（收缩系数）',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(0, self.H0+0.5)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('闸孔自由出流', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_flow_comparison(self, ax):
        """绘制流量对比"""
        # 计算三种情况的流量
        Q_thin = self.Q_thin
        Q_broad = self.calculate_broad_weir(0.5)
        Q_gate = self.calculate_gate_flow(0.8, 0.60)
        
        flow_types = ['薄壁堰', '宽顶堰', '闸孔出流']
        flows = [Q_thin, Q_broad, Q_gate]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # 柱状图
        bars = ax.bar(flow_types, flows, color=colors, edgecolor='black',
                     linewidth=2, alpha=0.7)
        
        # 标注数值
        for i, (bar, flow) in enumerate(zip(bars, flows)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                   f'{flow:.3f}m³/s',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 相对比较
        ax.axhline(Q_thin, color='red', linestyle='--', linewidth=1.5,
                  alpha=0.5, label=f'薄壁堰基准: {Q_thin:.3f}m³/s')
        
        # 百分比标注
        for i, flow in enumerate(flows[1:], 1):
            ratio = (flow / Q_thin - 1) * 100
            if ratio > 0:
                text = f'+{ratio:.1f}%'
                color = 'green'
            else:
                text = f'{ratio:.1f}%'
                color = 'red'
            ax.text(i, flow/2, text, ha='center', fontsize=10,
                   color=color, weight='bold')
        
        ax.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax.set_title('三种出流方式流量对比', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, axis='y', alpha=0.3)
        
        # 添加公式
        formulas = [
            '薄壁堰: Q=(2/3)m·B·√(2g)·H^(3/2)',
            '宽顶堰: Q=m·B·√(2g)·H^(3/2)',
            '闸孔: Q=μ·e·B·√(2g·H₀)'
        ]
        
        for i, formula in enumerate(formulas):
            ax.text(0.5, 0.9-i*0.08, formula, transform=ax.transAxes,
                   fontsize=8,
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.6))


def test_problem_641():
    """测试题目641"""
    # 已知条件
    B = 2.0      # 堰宽 (m)
    P = 1.5      # 堰高 (m)
    H0 = 2.0     # 上游水深 (m)
    m_weir = 0.42  # 流量系数
    g = 9.8      # 重力加速度 (m/s²)
    
    # 创建计算对象
    weir_gate = WeirGateFlow(B, P, H0, m_weir, g)
    
    # 打印薄壁堰结果
    weir_gate.print_results()
    
    # 打印宽顶堰结果
    weir_gate.print_broad_weir_results(b=0.5)
    
    # 打印闸孔出流结果
    weir_gate.print_gate_flow_results(e=0.8, mu=0.60)
    
    print("\n【最终答案】")
    print("="*80)
    print(f"(1) 作用水头: H = {weir_gate.H} m")
    print(f"(2) 薄壁堰流量: Q = {weir_gate.Q_thin:.4f} m³/s")
    print("(3) 水力特性:")
    print("    • 水流急剧收缩，形成溢流水舌")
    print("    • 上游缓流，下游急流")
    print(f"    • H/P = {weir_gate.H/weir_gate.P:.3f}（满足范围）")
    print(f"(4) 宽顶堰流量: Q = {weir_gate.Q_broad:.4f} m³/s")
    print(f"    堰顶形成临界流（Fr≈1）")
    print(f"(5) 闸孔出流流量: Q = {weir_gate.Q_gate:.4f} m³/s")
    print(f"    收缩断面为急流（Fr>1）")
    print("="*80)
    
    # 可视化
    print("\n生成可视化图表...")
    fig = weir_gate.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_641_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_641_result.png")
    
    # 验证
    assert weir_gate.H > 0, "作用水头必须为正"
    assert weir_gate.Q_thin > 0, "流量必须为正"
    assert weir_gate.Q_broad > 0, "宽顶堰流量必须为正"
    assert weir_gate.Q_gate > 0, "闸孔流量必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("堰闸出流是明渠流的重要应用！")
    print("• 薄壁堰: Q = (2/3)m·B·√(2g)·H^(3/2)")
    print("• 宽顶堰: 堰顶形成临界流，Fr=1")
    print("• 闸孔: 自由出流Q = μ·e·B·√(2g·H)")
    print("• 堰流vs闸流: 堰顶过水vs闸底过水")
    print("• 应用: 流量测量、水位控制、泄洪")


if __name__ == "__main__":
    test_problem_641()
