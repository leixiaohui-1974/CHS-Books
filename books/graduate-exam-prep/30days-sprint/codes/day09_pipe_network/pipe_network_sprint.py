#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 9: 有压管流计算
Sprint Day 9: Pressurized Pipe Flow and Pipe Networks

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 串联管道：Q₁=Q₂=Q, H=H₁+H₂+...
  2. 并联管道：Q=Q₁+Q₂+..., H₁=H₂=...=H
  3. 能量方程：z₁+p₁/(ρg)+v₁²/(2g)=z₂+p₂/(ρg)+v₂²/(2g)+hf
  4. 水击现象：Δp=ρcΔv
  5. 经济流速：v=1~3m/s

🎯 学习目标：
  - 掌握串联并联管道计算
  - 理解能量方程应用
  - 熟练求解管网问题
  - 了解经济流速选择

💪 今日格言：管网计算是实战核心！掌握串并联=拿到20分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon, FancyBboxPatch
from matplotlib.patches import ConnectionPatch
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day9PipeNetwork:
    """
    Day 9：有压管流计算
    
    包含2个核心例题：
    1. 基础题：串联管道计算
    2. 强化题：并联管道计算
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        self.nu = 1.0e-6  # 运动粘度 (m²/s)
        
    def calculate_head_loss(self, lambda_val, L, d, v):
        """计算沿程阻力损失"""
        hf = lambda_val * (L / d) * (v**2 / (2 * self.g))
        return hf
    
    def calculate_lambda_turbulent(self, Re):
        """计算紊流摩阻系数（布拉修斯公式）"""
        return 0.3164 / (Re**0.25)
    
    def calculate_reynolds(self, v, d):
        """计算雷诺数"""
        return v * d / self.nu
    
    def example_1_series_pipes(self):
        """
        例题1：串联管道计算（基础题）⭐⭐⭐⭐⭐
        
        题目：两段管道串联，AB段：d₁=0.2m, L₁=100m
              BC段：d₂=0.15m, L₂=80m
              A点压强pA=200kPa(表压)，C点压强pC=50kPa(表压)
              A、B、C三点在同一水平面上，流量Q=0.06m³/s
              摩阻系数λ₁=λ₂=0.025
        求：(1) AB段流速v₁和BC段流速v₂
            (2) AB段阻力损失h₁和BC段阻力损失h₂
            (3) B点压强pB
            (4) 总阻力损失H
        
        考点：串联管道，能量方程，连续性方程
        难度：基础（必考！）
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题1：串联管道计算（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d1 = 0.20      # AB段直径 (m)
        L1 = 100.0     # AB段长度 (m)
        d2 = 0.15      # BC段直径 (m)
        L2 = 80.0      # BC段长度 (m)
        Q = 0.06       # 流量 (m³/s)
        pA = 200000    # A点压强 (Pa, 表压)
        pC = 50000     # C点压强 (Pa, 表压)
        lambda1 = 0.025  # AB段摩阻系数
        lambda2 = 0.025  # BC段摩阻系数
        
        print(f"\n已知条件：")
        print(f"  AB段：d₁ = {d1} m, L₁ = {L1} m")
        print(f"  BC段：d₂ = {d2} m, L₂ = {L2} m")
        print(f"  流量 Q = {Q} m³/s")
        print(f"  A点压强 pA = {pA/1000} kPa (表压)")
        print(f"  C点压强 pC = {pC/1000} kPa (表压)")
        print(f"  摩阻系数 λ₁ = λ₂ = {lambda1}")
        print(f"  A、B、C三点在同一水平面")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 流速
        print(f"\n(1) 计算各段流速（串联：Q₁=Q₂=Q）：")
        print(f"    ")
        print(f"    AB段断面积：")
        print(f"    A₁ = π(d₁/2)² = π×({d1}/2)²")
        
        A1 = np.pi * (d1/2)**2
        
        print(f"       = {A1:.6f} m²")
        print(f"    ")
        print(f"    AB段流速：")
        print(f"    v₁ = Q/A₁ = {Q}/{A1:.6f}")
        
        v1 = Q / A1
        
        print(f"       = {v1:.3f} m/s ✓")
        print(f"    ")
        print(f"    BC段断面积：")
        print(f"    A₂ = π(d₂/2)² = π×({d2}/2)²")
        
        A2 = np.pi * (d2/2)**2
        
        print(f"       = {A2:.6f} m²")
        print(f"    ")
        print(f"    BC段流速：")
        print(f"    v₂ = Q/A₂ = {Q}/{A2:.6f}")
        
        v2 = Q / A2
        
        print(f"       = {v2:.3f} m/s ✓")
        
        # (2) 阻力损失
        print(f"\n(2) 计算各段阻力损失：")
        print(f"    ")
        print(f"    AB段阻力损失（达西公式）：")
        print(f"    h₁ = λ₁(L₁/d₁)(v₁²/2g)")
        
        h1 = self.calculate_head_loss(lambda1, L1, d1, v1)
        
        print(f"       = {lambda1}×({L1}/{d1})×({v1:.3f}²/(2×{self.g}))")
        print(f"       = {lambda1}×{L1/d1:.0f}×{v1**2/(2*self.g):.6f}")
        print(f"       = {h1:.3f} m ✓")
        print(f"    ")
        print(f"    BC段阻力损失：")
        print(f"    h₂ = λ₂(L₂/d₂)(v₂²/2g)")
        
        h2 = self.calculate_head_loss(lambda2, L2, d2, v2)
        
        print(f"       = {lambda2}×({L2}/{d2})×({v2:.3f}²/(2×{self.g}))")
        print(f"       = {lambda2}×{L2/d2:.0f}×{v2**2/(2*self.g):.6f}")
        print(f"       = {h2:.3f} m ✓")
        
        # (3) B点压强
        print(f"\n(3) 计算B点压强（能量方程A→B）：")
        print(f"    ")
        print(f"    能量方程（A、B、C在同一水平面，zA=zB=zC=0）：")
        print(f"    pA/(ρg) + vA²/(2g) = pB/(ρg) + vB²/(2g) + h₁")
        print(f"    ")
        print(f"    由于vA=v₁, vB=v₁（同一管段）：")
        print(f"    pA/(ρg) = pB/(ρg) + h₁")
        print(f"    ")
        print(f"    pB/(ρg) = pA/(ρg) - h₁")
        
        pB_over_rho_g = pA / (self.rho * self.g) - h1
        pB = pB_over_rho_g * self.rho * self.g
        
        print(f"            = {pA/(self.rho*self.g):.3f} - {h1:.3f}")
        print(f"            = {pB_over_rho_g:.3f} m")
        print(f"    ")
        print(f"    pB = ρg × {pB_over_rho_g:.3f}")
        print(f"       = {self.rho} × {self.g} × {pB_over_rho_g:.3f}")
        print(f"       = {pB:.0f} Pa")
        print(f"       = {pB/1000:.2f} kPa ✓")
        
        # (4) 总阻力损失
        print(f"\n(4) 总阻力损失（串联：H=h₁+h₂）：")
        
        H_total = h1 + h2
        
        print(f"    H = h₁ + h₂")
        print(f"      = {h1:.3f} + {h2:.3f}")
        print(f"      = {H_total:.3f} m ✓")
        print(f"    ")
        print(f"    验证（能量方程A→C）：")
        print(f"    pA/(ρg) - pC/(ρg) = H + (v₂²-v₁²)/(2g)")
        
        H_check = pA/(self.rho*self.g) - pC/(self.rho*self.g) - (v2**2-v1**2)/(2*self.g)
        
        print(f"    {pA/(self.rho*self.g):.3f} - {pC/(self.rho*self.g):.3f} = H + {(v2**2-v1**2)/(2*self.g):.3f}")
        print(f"    {pA/(self.rho*self.g) - pC/(self.rho*self.g):.3f} = H + {(v2**2-v1**2)/(2*self.g):.3f}")
        print(f"    H = {H_check:.3f} m ≈ {H_total:.3f} m ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：串联管道示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 管道AB段
        pipe1_y = 0
        pipe1_width = 0.15
        ax1.add_patch(Rectangle((0, pipe1_y-pipe1_width/2), 2, pipe1_width,
                                fill=True, facecolor='lightblue',
                                edgecolor='black', linewidth=2))
        
        # 管道BC段
        pipe2_width = 0.11
        ax1.add_patch(Rectangle((2, pipe1_y-pipe2_width/2), 1.5, pipe2_width,
                                fill=True, facecolor='lightgreen',
                                edgecolor='black', linewidth=2))
        
        # 点A、B、C标注
        ax1.plot(0, pipe1_y, 'ro', markersize=12)
        ax1.text(0, pipe1_y+0.15, 'A', fontsize=14, color='red', 
                fontweight='bold', ha='center')
        ax1.text(0, pipe1_y-0.2, f'pA={pA/1000:.0f}kPa', fontsize=9, ha='center')
        
        ax1.plot(2, pipe1_y, 'go', markersize=12)
        ax1.text(2, pipe1_y+0.15, 'B', fontsize=14, color='green', 
                fontweight='bold', ha='center')
        ax1.text(2, pipe1_y-0.2, f'pB={pB/1000:.0f}kPa', fontsize=9, ha='center')
        
        ax1.plot(3.5, pipe1_y, 'bo', markersize=12)
        ax1.text(3.5, pipe1_y+0.15, 'C', fontsize=14, color='blue', 
                fontweight='bold', ha='center')
        ax1.text(3.5, pipe1_y-0.2, f'pC={pC/1000:.0f}kPa', fontsize=9, ha='center')
        
        # 流速箭头
        ax1.arrow(0.5, pipe1_y, 0.5, 0, head_width=0.05, head_length=0.1,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(1, pipe1_y+0.25, f'v₁={v1:.2f}m/s\nQ={Q}m³/s', 
                ha='center', fontsize=9, color='blue')
        
        ax1.arrow(2.5, pipe1_y, 0.4, 0, head_width=0.05, head_length=0.08,
                 fc='green', ec='green', linewidth=2)
        ax1.text(2.75, pipe1_y+0.25, f'v₂={v2:.2f}m/s', 
                ha='center', fontsize=9, color='green')
        
        # 管段标注
        ax1.text(1, pipe1_y-0.35, f'd₁={d1}m, L₁={L1}m\nh₁={h1:.2f}m', 
                ha='center', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        ax1.text(2.75, pipe1_y-0.35, f'd₂={d2}m, L₂={L2}m\nh₂={h2:.2f}m', 
                ha='center', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax1.set_xlabel('管道长度方向', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 9 例题1：串联管道示意图', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.5, 4])
        ax1.set_ylim([-0.6, 0.6])
        ax1.set_aspect('equal')
        
        # 子图2：能量线与测压管水头线
        ax2 = plt.subplot(2, 2, 2)
        
        # A点能量
        HA = pA / (self.rho * self.g) + v1**2 / (2 * self.g)
        # B点能量
        HB = HA - h1
        # C点能量
        HC = HB - h2
        
        x_points = [0, 2, 3.5]
        H_points = [HA, HB, HC]
        p_points = [pA/(self.rho*self.g), pB/(self.rho*self.g), pC/(self.rho*self.g)]
        
        # 能量线（EL）
        ax2.plot(x_points, H_points, 'r-', linewidth=3, marker='o', 
                markersize=8, label='能量线(EL)')
        
        # 测压管水头线（HGL）
        ax2.plot(x_points, p_points, 'b--', linewidth=2, marker='s', 
                markersize=6, label='测压管水头线(HGL)')
        
        # 基准线
        ax2.axhline(y=0, color='k', linestyle='-', linewidth=1)
        ax2.text(3.7, 0.5, '基准线', fontsize=9)
        
        # 标注
        for i, (x, H, p) in enumerate(zip(x_points, H_points, p_points)):
            point_name = ['A', 'B', 'C'][i]
            ax2.text(x, H+1, f'{point_name}\nH={H:.1f}m', 
                    ha='center', fontsize=9, color='red')
            ax2.text(x, p-1.5, f'p/(ρg)={p:.1f}m', 
                    ha='center', fontsize=8, color='blue')
        
        # 阻力损失标注
        ax2.annotate('', xy=(2, HB), xytext=(2, HA),
                    arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
        ax2.text(2.3, (HA+HB)/2, f'h₁={h1:.2f}m', 
                fontsize=9, color='purple', fontweight='bold')
        
        ax2.annotate('', xy=(3.5, HC), xytext=(3.5, HB),
                    arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
        ax2.text(3.2, (HB+HC)/2-0.5, f'h₂={h2:.2f}m', 
                fontsize=9, color='purple', fontweight='bold')
        
        ax2.set_xlabel('管道长度方向', fontsize=12)
        ax2.set_ylabel('水头 (m)', fontsize=12)
        ax2.set_title('能量线与测压管水头线', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-0.5, 4.5])
        
        # 子图3：串联管道特点
        ax3 = plt.subplot(2, 2, 3)
        ax3.axis('off')
        
        features_text = """
        【串联管道特点】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        核心特征：
          1. 流量相等：
             Q = Q₁ = Q₂ = Q₃ = ...
             （质量守恒）
          
          2. 阻力累加：
             H = h₁ + h₂ + h₃ + ...
             （能量损失累加）
          
          3. 流速不等：
             v₁ ≠ v₂ ≠ v₃
             （取决于管径）
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        解题步骤：
          Step 1: 由Q计算各段流速
                  vi = Q/Ai
          
          Step 2: 计算各段阻力损失
                  hi = λi(Li/di)(vi²/2g)
          
          Step 3: 累加总阻力
                  H = Σhi
          
          Step 4: 应用能量方程
                  求解未知量
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        本题结果：
          Q = {:.3f} m³/s (相等)
          v₁ = {:.3f} m/s
          v₂ = {:.3f} m/s (不等)
          h₁ = {:.3f} m
          h₂ = {:.3f} m
          H = {:.3f} m (累加)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.format(Q, v1, v2, h1, h2, H_total)
        
        ax3.text(0.1, 0.95, features_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          AB段：d₁={d1}m, L₁={L1}m
          BC段：d₂={d2}m, L₂={L2}m
          Q = {Q} m³/s
          pA = {pA/1000} kPa, pC = {pC/1000} kPa
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 流速：
            v₁ = {v1:.3f} m/s ✓
            v₂ = {v2:.3f} m/s ✓
        
        (2) 阻力损失：
            h₁ = {h1:.3f} m ✓
            h₂ = {h2:.3f} m ✓
        
        (3) B点压强：
            pB = {pB/1000:.2f} kPa ✓
        
        (4) 总阻力：
            H = h₁+h₂ = {H_total:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 连续性：Q₁=Q₂=Q
          • 阻力累加：H=h₁+h₂
          • 达西公式：h=λ(L/d)(v²/2g)
          • 能量方程：ΣE₁=ΣE₂+Σh
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day09_pipe_network/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 指出串联特点Q₁=Q₂ (1分)")
        print("✓ (2) 计算A₁、A₂ (1分)")
        print("✓ (3) 计算v₁=Q/A₁ (1分)")
        print("✓ (4) 计算v₂=Q/A₂ (1分)")
        print("✓ (5) 应用达西公式计算h₁ (2分) ⭐")
        print("✓ (6) 应用达西公式计算h₂ (2分) ⭐")
        print("✓ (7) 应用能量方程A→B求pB (3分) ⭐⭐")
        print("✓ (8) 计算总阻力H=h₁+h₂ (2分)")
        print("✓ (9) 验证结果 (1分)")
        print("✓ (10) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 串联管道：Q相等，H累加！")
        print("  ⚠️ 能量方程：注意压强项、速度项、阻力项")
        print("  ⚠️ 流速不等：v=Q/A，A不同则v不同")
        print("  ⚠️ 单位统一：压强用Pa或kPa要统一")
        
        return {'v1': v1, 'v2': v2, 'h1': h1, 'h2': h2, 'pB': pB, 'H_total': H_total}
    
    def example_2_parallel_pipes(self):
        """
        例题2：并联管道计算（强化题）⭐⭐⭐⭐⭐
        
        题目：两段管道并联连接A、B两点
              管道1：d₁=0.20m, L₁=100m, λ₁=0.020
              管道2：d₂=0.15m, L₂=80m, λ₂=0.025
              总流量Q=0.10m³/s
        求：(1) 两管道流量分配Q₁、Q₂
            (2) 两管道流速v₁、v₂
            (3) 总阻力损失H
            (4) 若改为串联，总阻力损失H'
        
        考点：并联管道，流量分配，串并联对比
        难度：强化（必考！）
        时间：25分钟
        分值：20分
        """
        print("\n" + "="*60)
        print("例题2：并联管道计算（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d1 = 0.20      # 管道1直径 (m)
        L1 = 100.0     # 管道1长度 (m)
        lambda1 = 0.020  # 管道1摩阻系数
        d2 = 0.15      # 管道2直径 (m)
        L2 = 80.0      # 管道2长度 (m)
        lambda2 = 0.025  # 管道2摩阻系数
        Q_total = 0.10  # 总流量 (m³/s)
        
        print(f"\n已知条件：")
        print(f"  管道1：d₁ = {d1} m, L₁ = {L1} m, λ₁ = {lambda1}")
        print(f"  管道2：d₂ = {d2} m, L₂ = {L2} m, λ₂ = {lambda2}")
        print(f"  总流量 Q = {Q_total} m³/s")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 流量分配
        print(f"\n(1) 并联管道流量分配：")
        print(f"    ")
        print(f"    并联特点：h₁ = h₂ = H（阻力相等）")
        print(f"    ")
        print(f"    由达西公式：")
        print(f"    h₁ = λ₁(L₁/d₁)(v₁²/2g) = λ₁(L₁/d₁)(Q₁²/A₁²)/(2g)")
        print(f"    h₂ = λ₂(L₂/d₂)(v₂²/2g) = λ₂(L₂/d₂)(Q₂²/A₂²)/(2g)")
        print(f"    ")
        
        A1 = np.pi * (d1/2)**2
        A2 = np.pi * (d2/2)**2
        
        print(f"    断面积：")
        print(f"    A₁ = {A1:.6f} m²")
        print(f"    A₂ = {A2:.6f} m²")
        print(f"    ")
        print(f"    由h₁=h₂：")
        print(f"    λ₁(L₁/d₁)(Q₁²/A₁²) = λ₂(L₂/d₂)(Q₂²/A₂²)")
        print(f"    ")
        print(f"    定义K₁ = λ₁(L₁/d₁)/A₁²")
        print(f"    定义K₂ = λ₂(L₂/d₂)/A₂²")
        
        K1 = lambda1 * (L1 / d1) / (A1**2)
        K2 = lambda2 * (L2 / d2) / (A2**2)
        
        print(f"    K₁ = {K1:.2f}")
        print(f"    K₂ = {K2:.2f}")
        print(f"    ")
        print(f"    则：K₁Q₁² = K₂Q₂²")
        print(f"        Q₁/Q₂ = √(K₂/K₁) = √({K2:.2f}/{K1:.2f})")
        
        ratio = np.sqrt(K2 / K1)
        
        print(f"              = {ratio:.3f}")
        print(f"    ")
        print(f"    结合Q₁+Q₂=Q：")
        print(f"    Q₁ + Q₂ = {Q_total}")
        print(f"    Q₁ = {ratio:.3f}×Q₂")
        print(f"    ")
        print(f"    联立求解：")
        
        Q2 = Q_total / (1 + ratio)
        Q1 = Q_total - Q2
        
        print(f"    Q₂ = {Q2:.5f} m³/s ✓")
        print(f"    Q₁ = {Q1:.5f} m³/s ✓")
        print(f"    ")
        print(f"    验证：Q₁+Q₂ = {Q1:.5f}+{Q2:.5f} = {Q1+Q2:.5f} ≈ {Q_total} ✓")
        
        # (2) 流速
        print(f"\n(2) 计算各管流速：")
        
        v1 = Q1 / A1
        v2 = Q2 / A2
        
        print(f"    v₁ = Q₁/A₁ = {Q1:.5f}/{A1:.6f}")
        print(f"       = {v1:.3f} m/s ✓")
        print(f"    ")
        print(f"    v₂ = Q₂/A₂ = {Q2:.5f}/{A2:.6f}")
        print(f"       = {v2:.3f} m/s ✓")
        
        # (3) 总阻力损失
        print(f"\n(3) 计算总阻力损失H：")
        print(f"    ")
        print(f"    并联：H = h₁ = h₂（阻力相等）")
        print(f"    ")
        print(f"    计算h₁：")
        
        h1 = self.calculate_head_loss(lambda1, L1, d1, v1)
        
        print(f"    h₁ = λ₁(L₁/d₁)(v₁²/2g)")
        print(f"       = {lambda1}×({L1}/{d1})×({v1:.3f}²/(2×{self.g}))")
        print(f"       = {h1:.3f} m")
        print(f"    ")
        print(f"    计算h₂（验证）：")
        
        h2 = self.calculate_head_loss(lambda2, L2, d2, v2)
        
        print(f"    h₂ = λ₂(L₂/d₂)(v₂²/2g)")
        print(f"       = {lambda2}×({L2}/{d2})×({v2:.3f}²/(2×{self.g}))")
        print(f"       = {h2:.3f} m")
        print(f"    ")
        print(f"    验证：h₁ ≈ h₂ ({h1:.3f} ≈ {h2:.3f}) ✓")
        print(f"    ")
        print(f"    总阻力损失：H = {h1:.3f} m ✓")
        
        H_parallel = h1
        
        # (4) 串联对比
        print(f"\n(4) 若改为串联，计算总阻力损失H'：")
        print(f"    ")
        print(f"    串联：Q'₁ = Q'₂ = Q = {Q_total} m³/s")
        
        v1_series = Q_total / A1
        v2_series = Q_total / A2
        
        print(f"    v'₁ = Q/A₁ = {v1_series:.3f} m/s")
        print(f"    v'₂ = Q/A₂ = {v2_series:.3f} m/s")
        print(f"    ")
        
        h1_series = self.calculate_head_loss(lambda1, L1, d1, v1_series)
        h2_series = self.calculate_head_loss(lambda2, L2, d2, v2_series)
        
        print(f"    h'₁ = λ₁(L₁/d₁)(v'₁²/2g) = {h1_series:.3f} m")
        print(f"    h'₂ = λ₂(L₂/d₂)(v'₂²/2g) = {h2_series:.3f} m")
        print(f"    ")
        print(f"    串联总阻力：")
        
        H_series = h1_series + h2_series
        
        print(f"    H' = h'₁ + h'₂")
        print(f"       = {h1_series:.3f} + {h2_series:.3f}")
        print(f"       = {H_series:.3f} m ✓")
        print(f"    ")
        print(f"    对比分析：")
        print(f"    并联阻力：H = {H_parallel:.3f} m")
        print(f"    串联阻力：H' = {H_series:.3f} m")
        print(f"    H'/H = {H_series/H_parallel:.2f}")
        print(f"    ")
        print(f"    结论：串联阻力是并联的{H_series/H_parallel:.1f}倍！")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：并联管道示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # A点
        ax1.plot(0, 0, 'ro', markersize=15)
        ax1.text(-0.3, 0, 'A', fontsize=14, color='red', fontweight='bold')
        
        # B点
        ax1.plot(3, 0, 'bo', markersize=15)
        ax1.text(3.3, 0, 'B', fontsize=14, color='blue', fontweight='bold')
        
        # 管道1（上）
        y1 = 0.3
        ax1.plot([0, 0.3], [0, y1], 'k-', linewidth=2)
        ax1.add_patch(Rectangle((0.3, y1-0.08), 2.4, 0.16,
                                fill=True, facecolor='lightblue',
                                edgecolor='black', linewidth=2))
        ax1.plot([2.7, 3], [y1, 0], 'k-', linewidth=2)
        
        # 管道2（下）
        y2 = -0.3
        ax1.plot([0, 0.3], [0, y2], 'k-', linewidth=2)
        ax1.add_patch(Rectangle((0.3, y2-0.06), 2.4, 0.12,
                                fill=True, facecolor='lightgreen',
                                edgecolor='black', linewidth=2))
        ax1.plot([2.7, 3], [y2, 0], 'k-', linewidth=2)
        
        # 流量标注
        ax1.arrow(0.5, y1, 0.4, 0, head_width=0.06, head_length=0.1,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(1.5, y1+0.2, f'管道1\nd₁={d1}m\nQ₁={Q1:.4f}m³/s\nv₁={v1:.2f}m/s', 
                ha='center', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        ax1.arrow(0.5, y2, 0.4, 0, head_width=0.05, head_length=0.08,
                 fc='green', ec='green', linewidth=2)
        ax1.text(1.5, y2-0.3, f'管道2\nd₂={d2}m\nQ₂={Q2:.4f}m³/s\nv₂={v2:.2f}m/s', 
                ha='center', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        # 总流量
        ax1.arrow(-0.8, 0, 0.6, 0, head_width=0.08, head_length=0.12,
                 fc='red', ec='red', linewidth=3)
        ax1.text(-0.5, 0.15, f'Q={Q_total}m³/s', ha='center', 
                fontsize=10, color='red', fontweight='bold')
        
        ax1.set_xlabel('管道长度方向', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 9 例题2：并联管道示意图', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1, 4])
        ax1.set_ylim([-0.8, 0.8])
        ax1.set_aspect('equal')
        
        # 子图2：流量分配对比
        ax2 = plt.subplot(2, 2, 2)
        
        pipes = ['管道1\nd₁=0.20m', '管道2\nd₂=0.15m']
        flows = [Q1, Q2]
        colors = ['#4ECDC4', '#95E1D3']
        
        bars = ax2.bar(pipes, flows, color=colors, edgecolor='black', linewidth=2)
        
        for bar, flow in zip(bars, flows):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{flow:.5f}\nm³/s\n({flow/Q_total*100:.1f}%)',
                    ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 总流量标注
        ax2.axhline(y=Q_total, color='r', linestyle='--', linewidth=2)
        ax2.text(0.5, Q_total+0.002, f'Q总={Q_total}m³/s', 
                ha='center', fontsize=10, color='red', fontweight='bold')
        
        ax2.set_ylabel('流量 (m³/s)', fontsize=12)
        ax2.set_title('并联管道流量分配', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_ylim([0, Q_total*1.2])
        
        # 子图3：串联vs并联对比
        ax3 = plt.subplot(2, 2, 3)
        
        types = ['并联\n(本题)', '串联\n(假设)']
        losses = [H_parallel, H_series]
        colors_comp = ['#FFE66D', '#FF6B6B']
        
        bars = ax3.bar(types, losses, color=colors_comp, 
                      edgecolor='black', linewidth=2, width=0.5)
        
        for bar, loss in zip(bars, losses):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{loss:.2f}m',
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
        
        # 倍数标注
        ax3.plot([0, 1], [H_series*0.95, H_series*0.95], 'k--', linewidth=1.5)
        ax3.text(0.5, H_series*1.02, f'串联是并联的{H_series/H_parallel:.1f}倍',
                ha='center', fontsize=10, color='purple', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_ylabel('总阻力损失 (m)', fontsize=12)
        ax3.set_title('串联 vs 并联阻力对比', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：并联管道特点汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【并联管道特点】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        核心特征：
          1. 阻力相等：
             h₁ = h₂ = h₃ = ... = H
             （能量守恒）
          
          2. 流量累加：
             Q = Q₁ + Q₂ + Q₃ + ...
             （质量守恒）
          
          3. 流量分配规律：
             Q₁/Q₂ = √(K₂/K₁)
             其中Ki=λi(Li/di)/Ai²
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        串并联对比：
          
          并联优点：
            • 阻力小（H小）
            • 供水可靠
            • 流量分配灵活
          
          串联特点：
            • 阻力大（H大）
            • Q相同
            • 长距离输送
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        本题结果：
          Q₁ = {Q1:.5f} m³/s
          Q₂ = {Q2:.5f} m³/s
          Q = {Q_total} m³/s ✓
          
          H并联 = {H_parallel:.2f} m
          H串联 = {H_series:.2f} m
          倍数 = {H_series/H_parallel:.1f}倍
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day09_pipe_network/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（20分评分标准）：")
        print("="*60)
        print("✓ (1) 指出并联特点h₁=h₂ (1分)")
        print("✓ (2) 写出达西公式 (1分)")
        print("✓ (3) 建立h₁=h₂方程 (3分) ⭐⭐")
        print("✓ (4) 推导流量分配公式 (3分) ⭐⭐")
        print("✓ (5) 求解Q₁、Q₂ (3分) ⭐")
        print("✓ (6) 计算v₁、v₂ (2分)")
        print("✓ (7) 计算总阻力H (2分)")
        print("✓ (8) 串联情况分析 (2分)")
        print("✓ (9) 串并联对比 (2分)")
        print("✓ (10) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 并联管道：H相等，Q累加！")
        print("  ⚠️ 流量分配：需要联立h₁=h₂和Q₁+Q₂=Q")
        print("  ⚠️ 串并联区别：阻力相差很大！")
        print("  ⚠️ 方程求解：注意平方关系")
        
        return {'Q1': Q1, 'Q2': Q2, 'H_parallel': H_parallel, 'H_series': H_series}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 9 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 串联管道：")
        print("     Q = Q₁ = Q₂ = Q₃ = ...")
        print("     H = h₁ + h₂ + h₃ + ...")
        print("     ")
        print("  2. 并联管道：")
        print("     Q = Q₁ + Q₂ + Q₃ + ...")
        print("     h₁ = h₂ = h₃ = ... = H")
        print("     ")
        print("  3. 能量方程：")
        print("     z₁ + p₁/(ρg) + v₁²/(2g) = z₂ + p₂/(ρg) + v₂²/(2g) + hf")
        print("     ")
        print("  4. 达西公式：")
        print("     hf = λ(L/d)(v²/2g)")
        print("     ")
        print("  5. 并联流量分配：")
        print("     Q₁/Q₂ = √(K₂/K₁)")
        print("     其中 K = λ(L/d)/A²")
        
        print("\n✅ 串并联对比表：")
        print("  ┌────────┬──────────┬──────────┬──────────┐")
        print("  │  类型  │ 流量关系 │ 阻力关系 │ 特点     │")
        print("  ├────────┼──────────┼──────────┼──────────┤")
        print("  │  串联  │ Q₁=Q₂=Q  │ H=h₁+h₂  │ 阻力大   │")
        print("  │  并联  │ Q=Q₁+Q₂  │ h₁=h₂=H  │ 阻力小   │")
        print("  └────────┴──────────┴──────────┴──────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【串联管道】")
        print("  Step 1: 由总流量Q计算各段流速vi=Q/Ai")
        print("  Step 2: 计算各段阻力hi=λi(Li/di)(vi²/2g)")
        print("  Step 3: 累加总阻力H=Σhi")
        print("  Step 4: 应用能量方程求未知量")
        print("  ")
        print("  【并联管道】")
        print("  Step 1: 建立h₁=h₂方程")
        print("  Step 2: 推导流量分配Q₁/Q₂=√(K₂/K₁)")
        print("  Step 3: 结合Q₁+Q₂=Q求解Q₁、Q₂")
        print("  Step 4: 计算总阻力H=h₁=h₂")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：串联并联特点搞反")
        print("  ❌ 错误2：能量方程漏项或符号错误")
        print("  ❌ 错误3：并联流量分配公式记错")
        print("  ❌ 错误4：忘记质量守恒Q₁+Q₂=Q")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：串联「Q等H加」，并联「Q加H等」")
        print("  ✓ 技巧2：画图标注各点参数，思路清晰")
        print("  ✓ 技巧3：能量方程从左到右，逐项写出")
        print("  ✓ 技巧4：并联阻力必然小于串联")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能区分串联并联特点")
        print("  □ 掌握流量分配计算")
        print("  □ 熟练应用能量方程")
        print("  □ 理解串并联阻力差异")
        
        print("\n📅 明日预告：Day 10 - （已完成，复习明渠均匀流）")
        print("  下一重点：Day 14 - 第二周测试")
        
        print("\n💪 今日格言：")
        print("  「管网计算是实战核心！掌握串并联=拿到20分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 9: 有压管流计算")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day9 = Day9PipeNetwork()
    
    # 例题1：串联管道
    result1 = day9.example_1_series_pipes()
    
    # 例题2：并联管道
    result2 = day9.example_2_parallel_pipes()
    
    # 每日总结
    day9.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 9 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握串联管道计算")
    print(f"  ✓ 掌握并联管道计算")
    print(f"  ✓ 理解流量分配规律")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n下一步：复习已完成章节，准备第二周测试")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
