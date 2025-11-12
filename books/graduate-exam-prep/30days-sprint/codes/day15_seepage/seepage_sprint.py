#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 15: 渗流基础
Sprint Day 15: Seepage Flow and Darcy's Law

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 达西定律：v=kJ, Q=kvA
  2. 渗透系数：k值范围与影响因素
  3. 渗流场：流网绘制与分析
  4. 井流理论：潜水井与承压井
  5. 有效应力：σ'=σ-u

🎯 学习目标：
  - 掌握达西定律应用
  - 理解渗透系数概念
  - 熟练井流计算
  - 了解有效应力原理

💪 今日格言：渗流虽慢，但题必考！掌握达西定律=拿到15分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon, Wedge, Arc
from matplotlib.patches import ConnectionPatch
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day15Seepage:
    """
    Day 15：渗流基础
    
    包含2个核心例题：
    1. 基础题：达西定律与渗流计算
    2. 强化题：潜水井流量计算
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        self.gamma = self.rho * self.g  # 水容重 (N/m³)
        
    def example_1_darcy_law(self):
        """
        例题1：达西定律应用（基础题）⭐⭐⭐⭐⭐
        
        题目：土层厚度H=10m，上下游水头差Δh=3m
              土层水平长度L=50m，渗透系数k=0.01cm/s
              渗流断面宽度b=5m
        求：(1) 水力梯度J
            (2) 渗流速度v
            (3) 渗流量Q
            (4) 若土层孔隙率n=0.30，求实际流速u
        
        考点：达西定律，水力梯度，渗流量
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题1：达西定律应用（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        H = 10.0       # 土层厚度 (m)
        delta_h = 3.0  # 水头差 (m)
        L = 50.0       # 水平长度 (m)
        k_cm = 0.01    # 渗透系数 (cm/s)
        k = k_cm * 0.01  # 转换为 m/s
        b = 5.0        # 断面宽度 (m)
        n = 0.30       # 孔隙率
        
        print(f"\n已知条件：")
        print(f"  土层厚度 H = {H} m")
        print(f"  水头差 Δh = {delta_h} m")
        print(f"  水平长度 L = {L} m")
        print(f"  渗透系数 k = {k_cm} cm/s = {k} m/s")
        print(f"  断面宽度 b = {b} m")
        print(f"  孔隙率 n = {n}")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 水力梯度
        print(f"\n(1) 计算水力梯度J：")
        print(f"    ")
        print(f"    水力梯度定义：")
        print(f"    J = Δh / L")
        
        J = delta_h / L
        
        print(f"      = {delta_h} / {L}")
        print(f"      = {J:.4f} ✓")
        print(f"    ")
        print(f"    物理意义：每米水平距离的水头损失")
        
        # (2) 渗流速度
        print(f"\n(2) 计算渗流速度v（达西定律）：")
        print(f"    ")
        print(f"    达西定律：")
        print(f"    v = k × J")
        
        v = k * J
        
        print(f"      = {k} × {J:.4f}")
        print(f"      = {v:.6f} m/s")
        print(f"      = {v*100:.4f} cm/s")
        print(f"      = {v*86400:.3f} m/d (米/天) ✓")
        print(f"    ")
        print(f"    注意：v是渗流速度（虚拟速度），非实际流速")
        
        # (3) 渗流量
        print(f"\n(3) 计算渗流量Q：")
        print(f"    ")
        print(f"    渗流断面积：")
        print(f"    A = H × b")
        
        A = H * b
        
        print(f"      = {H} × {b}")
        print(f"      = {A} m² ✓")
        print(f"    ")
        print(f"    渗流量（达西定律）：")
        print(f"    Q = k × J × A")
        print(f"      = v × A")
        
        Q = v * A
        
        print(f"      = {v:.6f} × {A}")
        print(f"      = {Q:.6f} m³/s")
        print(f"      = {Q*1000:.4f} L/s")
        print(f"      = {Q*86400:.3f} m³/d (立方米/天) ✓")
        
        # (4) 实际流速
        print(f"\n(4) 计算实际流速u：")
        print(f"    ")
        print(f"    实际流速与渗流速度关系：")
        print(f"    u = v / n")
        print(f"    ")
        print(f"    物理意义：水在孔隙中的真实流速")
        
        u = v / n
        
        print(f"    u = {v:.6f} / {n}")
        print(f"      = {u:.6f} m/s")
        print(f"      = {u*100:.4f} cm/s")
        print(f"      = {u*86400:.3f} m/d ✓")
        print(f"    ")
        print(f"    对比：u = {u/v:.2f}×v (实际流速是渗流速度的{1/n:.2f}倍)")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：渗流示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 土层
        ax1.add_patch(Rectangle((0, 0), L, H,
                                fill=True, facecolor='sandybrown', alpha=0.5,
                                edgecolor='black', linewidth=2))
        
        # 上游水位
        h1 = H + delta_h
        ax1.fill_between([0, 0], [0, h1], color='lightblue', alpha=0.5)
        ax1.plot([0, 0], [0, h1], 'b-', linewidth=3)
        ax1.text(-3, h1/2, '上游\n水位', ha='center', fontsize=10, 
                fontweight='bold', color='blue')
        ax1.text(-3, h1+0.5, f'h₁={h1:.0f}m', ha='center', fontsize=9)
        
        # 下游水位
        h2 = H
        ax1.fill_between([L, L], [0, h2], color='lightblue', alpha=0.5)
        ax1.plot([L, L], [0, h2], 'b-', linewidth=3)
        ax1.text(L+3, h2/2, '下游\n水位', ha='center', fontsize=10, 
                fontweight='bold', color='blue')
        ax1.text(L+3, h2+0.5, f'h₂={h2:.0f}m', ha='center', fontsize=9)
        
        # 水头线（渗流线）
        x_flow = np.linspace(0, L, 100)
        h_flow = h1 - (h1 - h2) * x_flow / L
        ax1.plot(x_flow, h_flow, 'r--', linewidth=2, label='测压管水头线')
        
        # 水头差标注
        ax1.annotate('', xy=(L+8, h2), xytext=(L+8, h1),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(L+10, (h1+h2)/2, f'Δh={delta_h}m', 
                fontsize=10, color='red', fontweight='bold')
        
        # 渗流速度箭头
        for i in range(5):
            x_arrow = L * (i + 1) / 6
            y_arrow = h1 - (h1 - h2) * x_arrow / L - 1
            ax1.arrow(x_arrow, y_arrow, 5, 0, 
                     head_width=0.5, head_length=2,
                     fc='green', ec='green', linewidth=1.5)
        ax1.text(L/2, 3, f'v={v*100:.4f}cm/s', ha='center', fontsize=10,
                color='green', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 尺寸标注
        ax1.plot([0, L], [-2, -2], 'k-', linewidth=1)
        ax1.plot([0, 0], [-2.5, -1.5], 'k-', linewidth=1)
        ax1.plot([L, L], [-2.5, -1.5], 'k-', linewidth=1)
        ax1.text(L/2, -3, f'L={L}m', ha='center', fontsize=9)
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 15 例题1：渗流示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-5, L+15])
        ax1.set_ylim([-4, h1+2])
        
        # 子图2：达西定律关系
        ax2 = plt.subplot(2, 2, 2)
        
        # 准备数据（不同水力梯度）
        J_range = np.linspace(0, 0.15, 100)
        v_range = k * J_range
        Q_range = v_range * A
        
        # 绘制v-J关系
        ax2_twin = ax2.twinx()
        
        line1 = ax2.plot(J_range, v_range*100, 'b-', linewidth=2, 
                        marker='o', markevery=20, markersize=6,
                        label=f'v=kJ (k={k_cm}cm/s)')
        ax2.plot([J], [v*100], 'ro', markersize=10)
        ax2.text(J*1.1, v*100, f'本题点\nJ={J:.4f}\nv={v*100:.4f}cm/s',
                fontsize=8, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 绘制Q-J关系
        line2 = ax2_twin.plot(J_range, Q_range*1000, 'g--', linewidth=2,
                             marker='s', markevery=20, markersize=6,
                             label=f'Q=kJA (A={A}m²)')
        ax2_twin.plot([J], [Q*1000], 'mo', markersize=10)
        
        ax2.set_xlabel('水力梯度 J', fontsize=12)
        ax2.set_ylabel('渗流速度 v (cm/s)', fontsize=12, color='blue')
        ax2_twin.set_ylabel('渗流量 Q (L/s)', fontsize=12, color='green')
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2_twin.tick_params(axis='y', labelcolor='green')
        ax2.set_title('达西定律：v-J 和 Q-J 关系', fontsize=13, fontweight='bold')
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='upper left')
        
        ax2.grid(True, alpha=0.3)
        
        # 子图3：渗流速度与实际流速
        ax3 = plt.subplot(2, 2, 3)
        
        # 孔隙率变化
        n_range = np.linspace(0.2, 0.5, 100)
        u_range = v / n_range
        ratio_range = u_range / v
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(n_range, u_range*100, 'b-', linewidth=2,
                        label='实际流速 u=v/n')
        ax3.plot([n], [u*100], 'ro', markersize=10)
        ax3.axhline(y=v*100, color='r', linestyle='--', linewidth=1.5,
                   label=f'渗流速度 v={v*100:.4f}cm/s')
        
        line2 = ax3_twin.plot(n_range, ratio_range, 'g--', linewidth=2,
                             label='速度比 u/v')
        ax3_twin.plot([n], [u/v], 'mo', markersize=10)
        
        ax3.text(n, u*100*1.1, f'本题点\nn={n}\nu={u*100:.4f}cm/s',
                fontsize=8, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_xlabel('孔隙率 n', fontsize=12)
        ax3.set_ylabel('流速 (cm/s)', fontsize=12, color='blue')
        ax3_twin.set_ylabel('速度比 u/v', fontsize=12, color='green')
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='green')
        ax3.set_title('渗流速度 vs 实际流速', fontsize=13, fontweight='bold')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper right')
        
        ax3.grid(True, alpha=0.3)
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          土层厚度：H = {H} m
          水头差：Δh = {delta_h} m
          水平长度：L = {L} m
          渗透系数：k = {k_cm} cm/s
          断面宽度：b = {b} m
          孔隙率：n = {n}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 水力梯度：
            J = Δh/L = {J:.4f} ✓
        
        (2) 渗流速度：
            v = kJ = {v*100:.4f} cm/s
              = {v*86400:.3f} m/d ✓
        
        (3) 渗流量：
            A = H×b = {A} m²
            Q = vA = {Q*1000:.4f} L/s
              = {Q*86400:.3f} m³/d ✓
        
        (4) 实际流速：
            u = v/n = {u*100:.4f} cm/s
              = {u*86400:.3f} m/d ✓
            u/v = {u/v:.2f} ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 达西定律：v = kJ
          • 渗流量：Q = kvA
          • 水力梯度：J = Δh/L
          • 实际流速：u = v/n
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day15_seepage/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 写出达西定律v=kJ (2分) ⭐")
        print("✓ (2) 计算水力梯度J=Δh/L (2分)")
        print("✓ (3) 计算渗流速度v (2分)")
        print("✓ (4) 计算渗流断面积A (1分)")
        print("✓ (5) 计算渗流量Q=vA (2分) ⭐")
        print("✓ (6) 实际流速u=v/n (2分)")
        print("✓ (7) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 渗透系数单位：注意cm/s转m/s")
        print("  ⚠️ 渗流速度v：虚拟速度，非实际流速")
        print("  ⚠️ 实际流速u=v/n：水在孔隙中的真实速度")
        print("  ⚠️ 水力梯度：J=Δh/L，不是Δh/H")
        
        return {'J': J, 'v': v, 'Q': Q, 'u': u}
    
    def example_2_well_flow(self):
        """
        例题2：潜水井流量计算（强化题）⭐⭐⭐⭐⭐
        
        题目：潜水含水层厚度H=20m，渗透系数k=15m/d
              抽水井半径r₀=0.5m，影响半径R=100m
              稳定抽水时井中水深h=15m
        求：(1) 井的出水量Q
            (2) 距井中心r=10m处的水深h₁₀
            (3) 该处的水力梯度J₁₀
            (4) 该处的渗流速度v₁₀
        
        考点：潜水井流量公式，Dupuit公式
        难度：强化（必考！）
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题2：潜水井流量计算（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        H = 20.0       # 含水层厚度 (m)
        k_d = 15.0     # 渗透系数 (m/d)
        k = k_d / 86400  # 转换为 m/s
        r0 = 0.5       # 井半径 (m)
        R = 100.0      # 影响半径 (m)
        h0 = 15.0      # 井中水深 (m)
        r10 = 10.0     # 计算点距井距离 (m)
        
        print(f"\n已知条件：")
        print(f"  含水层厚度 H = {H} m")
        print(f"  渗透系数 k = {k_d} m/d")
        print(f"  井半径 r₀ = {r0} m")
        print(f"  影响半径 R = {R} m")
        print(f"  井中水深 h₀ = {h0} m")
        print(f"  计算点距井 r = {r10} m")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 井的出水量
        print(f"\n(1) 计算井的出水量Q（Dupuit公式）：")
        print(f"    ")
        print(f"    潜水完整井流量公式：")
        print(f"    Q = πk(H²-h₀²) / ln(R/r₀)")
        print(f"    ")
        print(f"    代入数据：")
        
        Q = np.pi * k_d * (H**2 - h0**2) / np.log(R / r0)
        
        print(f"    Q = π×{k_d}×({H}²-{h0}²) / ln({R}/{r0})")
        print(f"      = π×{k_d}×({H**2}-{h0**2}) / ln({R/r0:.1f})")
        print(f"      = π×{k_d}×{H**2-h0**2} / {np.log(R/r0):.4f}")
        print(f"      = {Q:.3f} m³/d")
        print(f"      = {Q/86400:.6f} m³/s")
        print(f"      = {Q/86400*1000:.3f} L/s ✓")
        
        # (2) r=10m处的水深
        print(f"\n(2) 计算r={r10}m处的水深h₁₀：")
        print(f"    ")
        print(f"    由Dupuit公式：")
        print(f"    Q = πk(H²-h²) / ln(R/r)")
        print(f"    ")
        print(f"    推导：")
        print(f"    H² - h² = Q×ln(R/r) / (πk)")
        print(f"    h² = H² - Q×ln(R/r) / (πk)")
        print(f"    ")
        print(f"    代入r={r10}m：")
        
        h10_squared = H**2 - Q * np.log(R / r10) / (np.pi * k_d)
        h10 = np.sqrt(h10_squared)
        
        print(f"    h₁₀² = {H}² - {Q:.3f}×ln({R}/{r10}) / (π×{k_d})")
        print(f"        = {H**2} - {Q:.3f}×{np.log(R/r10):.4f} / {np.pi*k_d:.3f}")
        print(f"        = {H**2} - {Q*np.log(R/r10)/(np.pi*k_d):.3f}")
        print(f"        = {h10_squared:.3f}")
        print(f"    ")
        print(f"    h₁₀ = √{h10_squared:.3f}")
        print(f"        = {h10:.3f} m ✓")
        print(f"    ")
        print(f"    降深：s₁₀ = H - h₁₀ = {H} - {h10:.3f} = {H-h10:.3f} m")
        
        # (3) 水力梯度
        print(f"\n(3) 计算r={r10}m处的水力梯度J₁₀：")
        print(f"    ")
        print(f"    水力梯度定义（径向）：")
        print(f"    J = -dh/dr")
        print(f"    ")
        print(f"    由Dupuit公式微分得：")
        print(f"    J = Q / (2πkrh)")
        print(f"    ")
        print(f"    代入r={r10}m：")
        
        J10 = Q / (2 * np.pi * k_d * r10 * h10)
        
        print(f"    J₁₀ = {Q:.3f} / (2π×{k_d}×{r10}×{h10:.3f})")
        print(f"        = {Q:.3f} / {2*np.pi*k_d*r10*h10:.3f}")
        print(f"        = {J10:.6f} ✓")
        print(f"    ")
        print(f"    物理意义：该点单位距离的水头损失")
        
        # (4) 渗流速度
        print(f"\n(4) 计算r={r10}m处的渗流速度v₁₀：")
        print(f"    ")
        print(f"    达西定律：")
        print(f"    v = k × J")
        
        v10 = k_d * J10 / 86400  # 转换为m/s
        
        print(f"    v₁₀ = k × J₁₀")
        print(f"        = {k_d} × {J10:.6f}")
        print(f"        = {k_d*J10:.6f} m/d")
        print(f"        = {v10*100:.4f} cm/s")
        print(f"        = {v10*1000:.3f} mm/s ✓")
        print(f"    ")
        print(f"    或由流量计算：")
        print(f"    Q = v × A = v × 2πrh")
        print(f"    v = Q / (2πrh)")
        
        v10_check = Q / (2 * np.pi * r10 * h10) / 86400
        
        print(f"    v₁₀ = {Q:.3f} / (2π×{r10}×{h10:.3f}) / 86400")
        print(f"        = {v10_check*100:.4f} cm/s ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：潜水井剖面图
        ax1 = plt.subplot(2, 2, 1)
        
        # 不透水层
        ax1.fill_between([-R, R], [-2, -2], [0, 0], 
                        color='gray', alpha=0.8, label='不透水层')
        ax1.plot([-R, R], [0, 0], 'k-', linewidth=2)
        
        # 含水层
        ax1.fill_between([-R, R], [0, 0], [H, H], 
                        color='sandybrown', alpha=0.3)
        
        # 潜水面曲线
        r_curve = np.linspace(r0, R, 100)
        h_curve = np.sqrt(h0**2 + (H**2 - h0**2) * np.log(r_curve / r0) / np.log(R / r0))
        
        # 右侧水面
        ax1.plot(r_curve, h_curve, 'b-', linewidth=2.5, label='潜水面')
        ax1.fill_between(r_curve, 0, h_curve, color='lightblue', alpha=0.4)
        
        # 左侧水面（镜像）
        ax1.plot(-r_curve, h_curve, 'b-', linewidth=2.5)
        ax1.fill_between(-r_curve, 0, h_curve, color='lightblue', alpha=0.4)
        
        # 原始地下水位
        ax1.plot([-R, R], [H, H], 'b--', linewidth=1.5, label=f'原水位H={H}m')
        
        # 抽水井
        ax1.add_patch(Rectangle((-r0, 0), 2*r0, h0,
                                fill=True, facecolor='white',
                                edgecolor='black', linewidth=2))
        ax1.text(0, -1, '抽水井', ha='center', fontsize=10, fontweight='bold')
        ax1.text(0, h0+1, f'h₀={h0}m', ha='center', fontsize=9, color='red')
        
        # r=10m处标注
        ax1.plot([r10, r10], [0, h10], 'r--', linewidth=1.5)
        ax1.plot(r10, h10, 'ro', markersize=10)
        ax1.text(r10, h10+1, f'r={r10}m\nh={h10:.2f}m', ha='center', 
                fontsize=9, color='red',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 影响半径标注
        ax1.plot([R, R], [0, H], 'g--', linewidth=1.5)
        ax1.text(R, H+1, f'R={R}m', ha='center', fontsize=9, color='green')
        
        # 降深标注
        ax1.annotate('', xy=(r0+2, h0), xytext=(r0+2, H),
                    arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
        ax1.text(r0+5, (H+h0)/2, f's={H-h0}m', 
                fontsize=9, color='purple', fontweight='bold')
        
        # 流向箭头
        for i in range(3):
            r_arrow = 20 + i*25
            h_arrow = np.sqrt(h0**2 + (H**2 - h0**2) * np.log(r_arrow / r0) / np.log(R / r0))
            ax1.arrow(r_arrow, h_arrow*0.5, -5, 0, 
                     head_width=0.8, head_length=2,
                     fc='green', ec='green', linewidth=1.5)
        ax1.text(50, 8, '渗流方向→', fontsize=10, color='green', fontweight='bold')
        
        ax1.set_xlabel('径向距离 r (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 15 例题2：潜水井剖面图', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-R-5, R+5])
        ax1.set_ylim([-3, H+3])
        
        # 子图2：水深变化曲线
        ax2 = plt.subplot(2, 2, 2)
        
        r_plot = np.linspace(r0, R, 100)
        h_plot = np.sqrt(h0**2 + (H**2 - h0**2) * np.log(r_plot / r0) / np.log(R / r0))
        s_plot = H - h_plot  # 降深
        
        ax2_twin = ax2.twinx()
        
        line1 = ax2.plot(r_plot, h_plot, 'b-', linewidth=2.5, label='水深h(r)')
        ax2.plot([r10], [h10], 'ro', markersize=10)
        ax2.axhline(y=H, color='b', linestyle='--', linewidth=1.5, label=f'H={H}m')
        ax2.axhline(y=h0, color='r', linestyle='--', linewidth=1.5, label=f'h₀={h0}m')
        
        line2 = ax2_twin.plot(r_plot, s_plot, 'g--', linewidth=2, label='降深s(r)')
        ax2_twin.plot([r10], [H-h10], 'mo', markersize=10)
        
        ax2.text(r10*1.2, h10, f'r={r10}m\nh={h10:.2f}m',
                fontsize=8, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax2.set_xlabel('距井距离 r (m)', fontsize=12)
        ax2.set_ylabel('水深 h (m)', fontsize=12, color='blue')
        ax2_twin.set_ylabel('降深 s (m)', fontsize=12, color='green')
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2_twin.tick_params(axis='y', labelcolor='green')
        ax2.set_title('水深与降深随距离变化', fontsize=13, fontweight='bold')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='right')
        
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([r0, R])
        
        # 子图3：水力梯度与渗流速度
        ax3 = plt.subplot(2, 2, 3)
        
        J_plot = Q / (2 * np.pi * k_d * r_plot * h_plot)
        v_plot = k_d * J_plot / 86400 * 100  # cm/s
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.semilogy(r_plot, J_plot, 'b-', linewidth=2.5, label='水力梯度J(r)')
        ax3.semilogy([r10], [J10], 'ro', markersize=10)
        
        line2 = ax3_twin.semilogy(r_plot, v_plot, 'g--', linewidth=2, label='渗流速度v(r)')
        ax3_twin.semilogy([r10], [v10*100], 'mo', markersize=10)
        
        ax3.text(r10*0.6, J10*1.5, f'r={r10}m\nJ={J10:.6f}',
                fontsize=8, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_xlabel('距井距离 r (m)', fontsize=12)
        ax3.set_ylabel('水力梯度 J', fontsize=12, color='blue')
        ax3_twin.set_ylabel('渗流速度 v (cm/s)', fontsize=12, color='green')
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='green')
        ax3.set_title('水力梯度与渗流速度（对数坐标）', fontsize=13, fontweight='bold')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper right')
        
        ax3.grid(True, alpha=0.3, which='both')
        ax3.set_xlim([r0, R])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          含水层厚度：H = {H} m
          渗透系数：k = {k_d} m/d
          井半径：r₀ = {r0} m
          影响半径：R = {R} m
          井中水深：h₀ = {h0} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 井的出水量：
            Q = πk(H²-h₀²)/ln(R/r₀)
              = {Q:.3f} m³/d
              = {Q/86400*1000:.3f} L/s ✓
        
        (2) r={r10}m处水深：
            h₁₀ = {h10:.3f} m ✓
            降深：s₁₀ = {H-h10:.3f} m
        
        (3) r={r10}m处水力梯度：
            J₁₀ = Q/(2πkrh)
                = {J10:.6f} ✓
        
        (4) r={r10}m处渗流速度：
            v₁₀ = kJ₁₀
                = {v10*100:.4f} cm/s ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • Dupuit公式：Q=πk(H²-h²)/ln(R/r)
          • 水力梯度：J=Q/(2πkrh)
          • 渗流速度：v=kJ
          • 水深分布：h²=h₀²+(H²-h₀²)ln(r/r₀)/ln(R/r₀)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day15_seepage/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 写出Dupuit公式 (2分) ⭐⭐")
        print("✓ (2) 计算井的出水量Q (3分) ⭐⭐")
        print("✓ (3) 推导h²表达式 (2分)")
        print("✓ (4) 计算r=10m处水深h₁₀ (3分) ⭐⭐")
        print("✓ (5) 推导水力梯度公式J=Q/(2πkrh) (2分)")
        print("✓ (6) 计算J₁₀ (1分)")
        print("✓ (7) 计算v₁₀=kJ₁₀ (1分)")
        print("✓ (8) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ Dupuit公式：H²-h²，不是H-h")
        print("  ⚠️ 潜水井：用H²-h₀²，承压井用H-h₀")
        print("  ⚠️ 对数项：ln(R/r₀)，不是ln(R-r₀)")
        print("  ⚠️ 水力梯度：J=Q/(2πkrh)，h是当地水深")
        
        return {'Q': Q, 'h10': h10, 'J10': J10, 'v10': v10}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 15 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 达西定律：")
        print("     v = k × J")
        print("     Q = k × J × A")
        print("     ")
        print("  2. 水力梯度：")
        print("     J = Δh / L  (一维流)")
        print("     J = -dh/dr  (径向流)")
        print("     ")
        print("  3. 实际流速：")
        print("     u = v / n")
        print("     (n为孔隙率)")
        print("     ")
        print("  4. 潜水完整井（Dupuit公式）：")
        print("     Q = πk(H²-h₀²) / ln(R/r₀)")
        print("     h² = h₀² + (H²-h₀²)×ln(r/r₀) / ln(R/r₀)")
        print("     J = Q / (2πkrh)")
        print("     ")
        print("  5. 承压完整井：")
        print("     Q = 2πkM(H-h₀) / ln(R/r₀)")
        print("     (M为承压含水层厚度)")
        
        print("\n✅ 渗透系数k值范围：")
        print("  ┌──────────┬─────────────┬──────────────┐")
        print("  │ 土类     │ k值(cm/s)   │ 渗透性       │")
        print("  ├──────────┼─────────────┼──────────────┤")
        print("  │ 砾石     │ >1          │ 强透水       │")
        print("  │ 粗砂     │ 1~0.1       │ 强透水       │")
        print("  │ 中细砂   │ 0.1~0.01    │ 中等透水     │")
        print("  │ 粉砂     │ 0.01~0.001  │ 弱透水       │")
        print("  │ 粘土     │ <0.001      │ 不透水       │")
        print("  └──────────┴─────────────┴──────────────┘")
        
        print("\n✅ 潜水井与承压井对比：")
        print("  ┌──────────┬──────────────┬──────────────┐")
        print("  │ 项目     │ 潜水井       │ 承压井       │")
        print("  ├──────────┼──────────────┼──────────────┤")
        print("  │ 自由水面 │ 有           │ 无           │")
        print("  │ 流量公式 │ H²-h²项      │ (H-h)项      │")
        print("  │ 水面形状 │ 曲线         │ 直线（近似） │")
        print("  │ 出水量   │ 较小         │ 较大         │")
        print("  └──────────┴──────────────┴──────────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【达西定律题】")
        print("  Step 1: 判断渗流类型（一维/径向）")
        print("  Step 2: 计算水力梯度J")
        print("  Step 3: 应用v=kJ计算渗流速度")
        print("  Step 4: Q=vA计算渗流量")
        print("  ")
        print("  【井流题】")
        print("  Step 1: 判断井类型（潜水/承压）")
        print("  Step 2: 选择公式（H²-h²或H-h）")
        print("  Step 3: 计算井的出水量Q")
        print("  Step 4: 求任意点水深h或水力梯度J")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：单位不统一（k用cm/s，L用m）")
        print("  ❌ 错误2：渗流速度v与实际流速u混淆")
        print("  ❌ 错误3：潜水井用H-h，应该用H²-h²")
        print("  ❌ 错误4：水力梯度公式记错")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：单位统一！k、L、t同一单位制")
        print("  ✓ 技巧2：画图！渗流示意图帮助理解")
        print("  ✓ 技巧3：区分v和u！v是虚拟速度")
        print("  ✓ 技巧4：潜水井看到H²-h²，承压井看到H-h")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能准确应用达西定律")
        print("  □ 掌握水力梯度计算")
        print("  □ 理解渗流速度与实际流速区别")
        print("  □ 熟练井流公式（潜水/承压）")
        
        print("\n📅 明日预告：Day 16 - 地下水动力学")
        print("  • 非稳定井流")
        print("  • 越流系统")
        print("  • 井群干扰")
        
        print("\n💪 今日格言：")
        print("  「渗流虽慢，但题必考！掌握达西定律=拿到15分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 15: 渗流基础")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day15 = Day15Seepage()
    
    # 例题1：达西定律
    result1 = day15.example_1_darcy_law()
    
    # 例题2：潜水井流量
    result2 = day15.example_2_well_flow()
    
    # 每日总结
    day15.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 15 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握达西定律")
    print(f"  ✓ 掌握井流计算")
    print(f"  ✓ 理解渗透系数")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n下一步：Day 16 - 地下水动力学（非稳定井流）")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
