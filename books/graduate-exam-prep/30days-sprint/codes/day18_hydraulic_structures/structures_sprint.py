#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 18: 水工建筑物
Sprint Day 18: Hydraulic Structures

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 重力坝稳定分析：抗滑、抗倾覆
  2. 渗流计算：渗流量、渗透压力
  3. 土石坝渗流：浸润线、渗流量
  4. 消能防冲：水跃消能、挑流消能
  5. 闸坝渗流：地下轮廓线法

🎯 学习目标：
  - 掌握重力坝稳定验算
  - 理解渗流计算方法
  - 熟练浸润线绘制
  - 了解消能设计

💪 今日格言：水工建筑是综合应用！掌握稳定分析=拿到15分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon, Wedge
from matplotlib.patches import ConnectionPatch
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day18HydraulicStructures:
    """
    Day 18：水工建筑物
    
    包含2个核心例题：
    1. 基础题：重力坝稳定分析
    2. 强化题：土石坝渗流计算
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho_w = 1000  # 水密度 (kg/m³)
        self.gamma_w = self.rho_w * self.g  # 水容重 (N/m³)
        self.gamma_c = 24000  # 混凝土容重 (N/m³)
        
    def example_1_gravity_dam(self):
        """
        例题1：重力坝稳定分析（基础题）⭐⭐⭐⭐⭐
        
        题目：某重力坝剖面为三角形，上游铅直面，下游坡度m=0.7
              坝高H=30m，上游水深h1=28m，下游水深h2=2m
              混凝土容重γc=24kN/m³，摩擦系数f=0.65
              取单位坝长（1m）进行计算
        求：(1) 坝体自重W
            (2) 上下游水压力P1、P2
            (3) 抗滑稳定安全系数Ks
            (4) 抗倾覆稳定安全系数K0
        
        考点：重力坝稳定，水压力，安全系数
        难度：基础（必考！）
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题1：重力坝稳定分析（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        H = 30.0       # 坝高 (m)
        h1 = 28.0      # 上游水深 (m)
        h2 = 2.0       # 下游水深 (m)
        m = 0.7        # 下游坡度系数
        gamma_c = 24.0 # 混凝土容重 (kN/m³)
        gamma_w = 10.0 # 水容重 (kN/m³)
        f = 0.65       # 摩擦系数
        L = 1.0        # 单位坝长 (m)
        
        print(f"\n已知条件：")
        print(f"  坝高 H = {H} m")
        print(f"  上游水深 h₁ = {h1} m")
        print(f"  下游水深 h₂ = {h2} m")
        print(f"  下游坡度 m = {m} (1:m)")
        print(f"  混凝土容重 γc = {gamma_c} kN/m³")
        print(f"  水容重 γw = {gamma_w} kN/m³")
        print(f"  摩擦系数 f = {f}")
        print(f"  单位坝长 L = {L} m")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 坝体自重
        print(f"\n(1) 计算坝体自重W：")
        print(f"    ")
        print(f"    三角形坝体剖面：")
        print(f"    上游面铅直，下游坡度1:{m}")
        print(f"    坝底宽度：B = mH")
        
        B = m * H
        
        print(f"            = {m}×{H}")
        print(f"            = {B} m")
        print(f"    ")
        print(f"    坝体断面积（单位坝长）：")
        print(f"    A = (1/2) × B × H")
        
        A = 0.5 * B * H
        
        print(f"      = 0.5 × {B} × {H}")
        print(f"      = {A} m²")
        print(f"    ")
        print(f"    坝体自重：")
        print(f"    W = γc × A × L")
        
        W = gamma_c * A * L
        
        print(f"      = {gamma_c} × {A} × {L}")
        print(f"      = {W} kN ✓")
        print(f"    ")
        print(f"    作用点：距坝踵x = (2/3)B = {2*B/3:.2f} m")
        
        xW = 2 * B / 3
        
        # (2) 水压力
        print(f"\n(2) 计算上下游水压力：")
        print(f"    ")
        print(f"    上游水压力P₁：")
        print(f"    P₁ = (1/2) × γw × h₁² × L")
        
        P1 = 0.5 * gamma_w * h1**2 * L
        
        print(f"       = 0.5 × {gamma_w} × {h1}² × {L}")
        print(f"       = {P1} kN ✓")
        print(f"    ")
        print(f"    作用点：距坝底y₁ = h₁/3 = {h1/3:.2f} m")
        
        y1 = h1 / 3
        
        print(f"    ")
        print(f"    下游水压力P₂：")
        print(f"    P₂ = (1/2) × γw × h₂² × L")
        
        P2 = 0.5 * gamma_w * h2**2 * L
        
        print(f"       = 0.5 × {gamma_w} × {h2}² × {L}")
        print(f"       = {P2} kN ✓")
        print(f"    ")
        print(f"    作用点：距坝底y₂ = h₂/3 = {h2/3:.2f} m")
        
        y2 = h2 / 3
        
        print(f"    ")
        print(f"    净水平力：")
        
        PH = P1 - P2
        
        print(f"    PH = P₁ - P₂ = {P1} - {P2}")
        print(f"       = {PH} kN (向下游) ✓")
        
        # (3) 抗滑稳定
        print(f"\n(3) 抗滑稳定安全系数Ks：")
        print(f"    ")
        print(f"    抗滑力：")
        print(f"    FR = f × W  (摩擦力)")
        
        FR = f * W
        
        print(f"       = {f} × {W}")
        print(f"       = {FR} kN")
        print(f"    ")
        print(f"    滑动力：")
        print(f"    FS = PH = {PH} kN")
        print(f"    ")
        print(f"    抗滑稳定安全系数：")
        print(f"    Ks = FR / FS")
        
        Ks = FR / PH
        
        print(f"       = {FR} / {PH}")
        print(f"       = {Ks:.3f} ✓")
        print(f"    ")
        print(f"    规范要求：Ks ≥ 1.05")
        
        if Ks >= 1.05:
            print(f"    判断：{Ks:.3f} ≥ 1.05，抗滑稳定满足 ✓")
        else:
            print(f"    判断：{Ks:.3f} < 1.05，抗滑稳定不满足 ⚠️")
        
        # (4) 抗倾覆稳定
        print(f"\n(4) 抗倾覆稳定安全系数K₀：")
        print(f"    ")
        print(f"    对坝踵取矩（顺时针为正）：")
        print(f"    ")
        print(f"    稳定力矩（W对坝踵的力矩）：")
        print(f"    MS = W × xW")
        
        MS = W * xW
        
        print(f"       = {W} × {xW:.2f}")
        print(f"       = {MS:.2f} kN·m")
        print(f"    ")
        print(f"    倾覆力矩（P₁对坝踵的力矩）：")
        print(f"    M₀ = P₁ × y₁ - P₂ × y₂")
        
        M0 = P1 * y1 - P2 * y2
        
        print(f"       = {P1} × {y1:.2f} - {P2} × {y2:.2f}")
        print(f"       = {P1*y1:.2f} - {P2*y2:.2f}")
        print(f"       = {M0:.2f} kN·m")
        print(f"    ")
        print(f"    抗倾覆稳定安全系数：")
        print(f"    K₀ = MS / M₀")
        
        K0 = MS / M0
        
        print(f"       = {MS:.2f} / {M0:.2f}")
        print(f"       = {K0:.3f} ✓")
        print(f"    ")
        print(f"    规范要求：K₀ ≥ 1.50")
        
        if K0 >= 1.50:
            print(f"    判断：{K0:.3f} ≥ 1.50，抗倾覆稳定满足 ✓")
        else:
            print(f"    判断：{K0:.3f} < 1.50，抗倾覆稳定不满足 ⚠️")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：重力坝示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 坐标系设置（坝踵为原点）
        # 坝体（三角形）
        dam_x = [0, 0, B, 0]
        dam_y = [0, H, 0, 0]
        ax1.fill(dam_x, dam_y, color='lightgray', alpha=0.8, 
                edgecolor='black', linewidth=2, label='坝体')
        
        # 上游水体
        water1_x = [-10, -10, 0, 0]
        water1_y = [0, h1, h1, 0]
        ax1.fill(water1_x, water1_y, color='lightblue', alpha=0.5)
        ax1.plot([0, 0], [0, h1], 'b-', linewidth=2, label='上游水位')
        
        # 下游水体
        water2_x = [B, B, B+5, B+5]
        water2_y = [0, h2, h2, 0]
        ax1.fill(water2_x, water2_y, color='lightblue', alpha=0.5)
        ax1.plot([B, B], [0, h2], 'b-', linewidth=2, label='下游水位')
        
        # 自重W
        ax1.arrow(xW, H-5, 0, -3, head_width=1, head_length=0.5,
                 fc='green', ec='green', linewidth=2)
        ax1.text(xW+1, H-3, f'W={W:.0f}kN', fontsize=10, color='green',
                fontweight='bold')
        
        # 上游水压力P1
        ax1.arrow(-8, y1, 5, 0, head_width=0.8, head_length=1,
                 fc='red', ec='red', linewidth=2)
        ax1.text(-8, y1+2, f'P₁={P1:.0f}kN', fontsize=10, color='red',
                fontweight='bold')
        
        # 下游水压力P2
        ax1.arrow(B+4, y2, -2, 0, head_width=0.5, head_length=0.5,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(B+2, y2-1.5, f'P₂={P2:.0f}kN', fontsize=9, color='blue')
        
        # 尺寸标注
        ax1.text(B/2, -2, f'B={B}m', ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow'))
        ax1.text(-2, H/2, f'H={H}m', ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 坝踵坝趾标注
        ax1.plot([0], [0], 'ro', markersize=10)
        ax1.text(-1, -1, '坝踵', fontsize=10, color='red', fontweight='bold')
        ax1.plot([B], [0], 'go', markersize=10)
        ax1.text(B+1, -1, '坝趾', fontsize=10, color='green', fontweight='bold')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 18 例题1：重力坝示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-12, B+6])
        ax1.set_ylim([-3, H+3])
        ax1.set_aspect('equal')
        
        # 子图2：力的分解
        ax2 = plt.subplot(2, 2, 2)
        
        forces = ['自重W', '上游P₁', '下游P₂', '净水平力PH', '摩擦力FR']
        values = [W, P1, P2, PH, FR]
        colors = ['green', 'red', 'blue', 'orange', 'purple']
        
        bars = ax2.barh(forces, values, color=colors, alpha=0.7,
                       edgecolor='black', linewidth=2)
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}kN',
                    ha='left', va='center', fontsize=10, fontweight='bold')
        
        ax2.set_xlabel('力 (kN)', fontsize=12)
        ax2.set_title('各力大小对比', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 子图3：安全系数
        ax3 = plt.subplot(2, 2, 3)
        
        safety_factors = ['抗滑Ks', '抗倾覆K₀']
        values_sf = [Ks, K0]
        requirements = [1.05, 1.50]
        colors_sf = ['green' if v >= r else 'red' for v, r in zip(values_sf, requirements)]
        
        x_pos = np.arange(len(safety_factors))
        bars = ax3.bar(x_pos, values_sf, color=colors_sf, alpha=0.7,
                      edgecolor='black', linewidth=2, label='实际值')
        
        # 标注数值
        for bar, val in zip(bars, values_sf):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 规范要求线
        ax3.axhline(y=1.05, color='orange', linestyle='--', linewidth=2,
                   label='Ks规范≥1.05')
        ax3.axhline(y=1.50, color='purple', linestyle='--', linewidth=2,
                   label='K₀规范≥1.50')
        
        ax3.set_ylabel('安全系数', fontsize=12)
        ax3.set_title('稳定安全系数', fontsize=13, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(safety_factors)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_ylim([0, max(values_sf)*1.2])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          坝高：H = {H} m
          上游水深：h₁ = {h1} m
          下游水深：h₂ = {h2} m
          下游坡度：m = {m}
          容重：γc = {gamma_c} kN/m³
          摩擦系数：f = {f}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 坝体自重：
            B = mH = {B} m
            A = (1/2)BH = {A} m²
            W = γcA = {W} kN ✓
        
        (2) 水压力：
            P₁ = (1/2)γwh₁² = {P1} kN ✓
            P₂ = (1/2)γwh₂² = {P2} kN ✓
            PH = P₁-P₂ = {PH} kN ✓
        
        (3) 抗滑稳定：
            FR = fW = {FR} kN
            Ks = FR/PH = {Ks:.3f} ✓
            {'满足' if Ks>=1.05 else '不满足'}规范(≥1.05)
        
        (4) 抗倾覆稳定：
            MS = W×xW = {MS:.2f} kN·m
            M₀ = P₁×y₁-P₂×y₂ = {M0:.2f} kN·m
            K₀ = MS/M₀ = {K0:.3f} ✓
            {'满足' if K0>=1.50 else '不满足'}规范(≥1.50)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 水压力：P=(1/2)γwh²
          • 抗滑：Ks=fW/(P₁-P₂)≥1.05
          • 抗倾覆：K₀=ΣMS/ΣM₀≥1.50
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day18_hydraulic_structures/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 计算坝底宽度B (1分)")
        print("✓ (2) 计算坝体自重W (2分) ⭐")
        print("✓ (3) 计算水压力P₁、P₂ (3分) ⭐⭐")
        print("✓ (4) 写出抗滑公式Ks (2分)")
        print("✓ (5) 计算抗滑安全系数 (2分) ⭐")
        print("✓ (6) 写出抗倾覆公式K₀ (2分)")
        print("✓ (7) 计算抗倾覆安全系数 (2分) ⭐")
        print("✓ (8) 规范判断 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 水压力：P=(1/2)γh²，作用点在h/3处")
        print("  ⚠️ 抗滑：摩擦力FR=fW，滑动力是净水平力")
        print("  ⚠️ 抗倾覆：对坝踵取矩，注意力臂")
        print("  ⚠️ 规范：Ks≥1.05，K₀≥1.50")
        
        return {'W': W, 'P1': P1, 'P2': P2, 'Ks': Ks, 'K0': K0}
    
    def example_2_earth_dam_seepage(self):
        """
        例题2：土石坝渗流计算（强化题）⭐⭐⭐⭐⭐
        
        题目：某均质土坝，坝高H=20m，上游水深h1=18m
              下游无水，坝顶宽B0=5m，上游坡度m1=3.0，下游坡度m2=2.5
              土料渗透系数k=0.5cm/s
        求：(1) 浸润线出逸点高度y0
            (2) 单宽渗流量q
            (3) 若采用排水棱体（坡度1:1.5），出逸点高度y0'
        
        考点：浸润线，渗流量，排水设施
        难度：强化（必考！）
        时间：25分钟
        分值：18分
        """
        print("\n" + "="*60)
        print("例题2：土石坝渗流计算（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        H = 20.0       # 坝高 (m)
        h1 = 18.0      # 上游水深 (m)
        h2 = 0.0       # 下游水深 (m)
        B0 = 5.0       # 坝顶宽 (m)
        m1 = 3.0       # 上游坡度
        m2 = 2.5       # 下游坡度
        k_cm = 0.5     # 渗透系数 (cm/s)
        k = k_cm * 0.01  # 转换为 m/s
        m_drain = 1.5  # 排水棱体坡度
        
        print(f"\n已知条件：")
        print(f"  坝高 H = {H} m")
        print(f"  上游水深 h₁ = {h1} m")
        print(f"  下游水深 h₂ = {h2} m")
        print(f"  坝顶宽 B₀ = {B0} m")
        print(f"  上游坡度 m₁ = {m1} (1:{m1})")
        print(f"  下游坡度 m₂ = {m2} (1:{m2})")
        print(f"  渗透系数 k = {k_cm} cm/s = {k} m/s")
        print(f"  排水棱体坡度 = 1:{m_drain}")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 浸润线出逸点
        print(f"\n(1) 计算浸润线出逸点高度y₀：")
        print(f"    ")
        print(f"    均质土坝浸润线（无排水设施）：")
        print(f"    出逸点高度经验公式：")
        print(f"    y₀ ≈ 0.4√(h₁L)")
        print(f"    ")
        print(f"    其中L为渗流长度（近似取坝底长度）：")
        print(f"    L = B₀ + m₁×H + m₂×H")
        
        L = B0 + m1 * H + m2 * H
        
        print(f"      = {B0} + {m1}×{H} + {m2}×{H}")
        print(f"      = {L} m")
        print(f"    ")
        print(f"    出逸点高度：")
        print(f"    y₀ ≈ 0.4√({h1}×{L})")
        
        y0 = 0.4 * np.sqrt(h1 * L)
        
        print(f"       ≈ 0.4×√{h1*L:.1f}")
        print(f"       ≈ {y0:.2f} m ✓")
        print(f"    ")
        print(f"    物理意义：浸润线与下游坡面交点距坝底的高度")
        
        # (2) 渗流量
        print(f"\n(2) 计算单宽渗流量q：")
        print(f"    ")
        print(f"    均质土坝渗流量经验公式：")
        print(f"    q = k × (h₁² - y₀²) / (2L)")
        print(f"    ")
        print(f"    代入数据：")
        
        q = k * (h1**2 - y0**2) / (2 * L)
        
        print(f"    q = {k} × ({h1}² - {y0:.2f}²) / (2×{L})")
        print(f"      = {k} × ({h1**2} - {y0**2:.2f}) / {2*L}")
        print(f"      = {k} × {h1**2 - y0**2:.2f} / {2*L}")
        print(f"      = {q:.6f} m³/(s·m)")
        print(f"      = {q*86400:.4f} m³/(d·m) ✓")
        print(f"    ")
        print(f"    单宽：每米坝长的渗流量")
        
        # (3) 排水棱体
        print(f"\n(3) 采用排水棱体（坡度1:{m_drain}）：")
        print(f"    ")
        print(f"    排水棱体作用：")
        print(f"    • 降低浸润线")
        print(f"    • 减小出逸点高度")
        print(f"    • 增加下游坡稳定")
        print(f"    ")
        print(f"    新出逸点高度（经验）：")
        print(f"    y₀' ≈ y₀ / 2")
        
        y0_new = y0 / 2
        
        print(f"        ≈ {y0:.2f} / 2")
        print(f"        ≈ {y0_new:.2f} m ✓")
        print(f"    ")
        print(f"    新渗流量：")
        
        q_new = k * (h1**2 - y0_new**2) / (2 * L)
        
        print(f"    q' = k × (h₁² - y₀'²) / (2L)")
        print(f"       = {k} × ({h1}² - {y0_new:.2f}²) / (2×{L})")
        print(f"       = {q_new:.6f} m³/(s·m)")
        print(f"       = {q_new*86400:.4f} m³/(d·m) ✓")
        print(f"    ")
        print(f"    对比分析：")
        print(f"    出逸点降低：{y0:.2f}m → {y0_new:.2f}m (降{(1-y0_new/y0)*100:.1f}%)")
        print(f"    渗流量增加：{q:.6f} → {q_new:.6f} (增{(q_new/q-1)*100:.1f}%)")
        print(f"    说明：排水棱体虽降低出逸点，但增大水力梯度")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：土石坝剖面与浸润线
        ax1 = plt.subplot(2, 2, 1)
        
        # 坝体轮廓
        x_dam = [0, 0, B0, B0+m2*H, m1*H+B0+m2*H]
        y_dam = [H, 0, 0, H, H]
        ax1.plot(x_dam[:3], y_dam[:3], 'k-', linewidth=2)  # 上游坡+坝底前段
        ax1.plot(x_dam[2:4], y_dam[2:4], 'k-', linewidth=2)  # 下游坡
        ax1.plot([x_dam[0], x_dam[4]], [y_dam[0], y_dam[4]], 'k-', linewidth=2)  # 坝顶
        ax1.fill(x_dam, y_dam, color='sandybrown', alpha=0.3, label='坝体')
        
        # 上游水体
        ax1.fill_between([-20, 0], [0, 0], [h1, h1], color='lightblue', alpha=0.5)
        ax1.plot([0, 0], [0, h1], 'b-', linewidth=2, label='上游水位')
        ax1.text(-10, h1/2, f'h₁={h1}m', fontsize=10, color='blue',
                fontweight='bold')
        
        # 浸润线（抛物线近似）
        x_seep = np.linspace(0, B0+m2*H, 100)
        # 简化模型：从h1开始，到y0结束的抛物线
        y_seep = h1 - (h1 - y0) * (x_seep / (B0+m2*H))**1.5
        ax1.plot(x_seep, y_seep, 'r--', linewidth=2.5, label='浸润线')
        
        # 出逸点
        ax1.plot([B0+m2*H], [y0], 'ro', markersize=10)
        ax1.text(B0+m2*H+5, y0, f'出逸点\ny₀={y0:.2f}m',
                fontsize=10, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 排水棱体示意
        x_drain = [B0+m2*H-10, B0+m2*H, B0+m2*H]
        y_drain = [y0_new, y0_new, 0]
        ax1.plot(x_drain, y_drain, 'g--', linewidth=2, label='排水棱体')
        ax1.fill_between([B0+m2*H-10, B0+m2*H], [0, 0], [y0_new, 0],
                        color='green', alpha=0.3)
        
        # 尺寸标注
        ax1.text(B0/2, -2, f'B₀={B0}m', ha='center', fontsize=9)
        ax1.text(B0+m2*H/2, -2, f'下游坡1:{m2}', ha='center', fontsize=9)
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 18 例题2：土石坝浸润线', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-25, L+10])
        ax1.set_ylim([-3, H+3])
        
        # 子图2：排水设施对比
        ax2 = plt.subplot(2, 2, 2)
        
        cases = ['无排水', '排水棱体']
        y0_values = [y0, y0_new]
        q_values = [q*86400, q_new*86400]
        
        x_pos = np.arange(len(cases))
        width = 0.35
        
        bars1 = ax2.bar(x_pos - width/2, y0_values, width, label='出逸点y₀(m)',
                       color='red', alpha=0.7)
        bars2 = ax2.bar(x_pos + width/2, q_values, width, label='渗流量q(m³/d·m)',
                       color='blue', alpha=0.7)
        
        # 标注数值
        for bar in bars1:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=10)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=10)
        
        ax2.set_ylabel('数值', fontsize=12)
        ax2.set_title('排水设施效果对比', fontsize=13, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(cases)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 子图3：浸润线形态
        ax3 = plt.subplot(2, 2, 3)
        
        # 详细浸润线绘制
        x_detail = np.linspace(0, B0+m2*H, 200)
        y_no_drain = h1 - (h1 - y0) * (x_detail / (B0+m2*H))**1.5
        y_with_drain = h1 - (h1 - y0_new) * (x_detail / (B0+m2*H))**1.5
        
        ax3.plot(x_detail, y_no_drain, 'r-', linewidth=2.5, label='无排水')
        ax3.plot(x_detail, y_with_drain, 'g--', linewidth=2.5, label='有排水')
        
        # 下游坡面
        x_slope = [B0, B0+m2*H]
        y_slope = [0, H]
        ax3.plot(x_slope, y_slope, 'k-', linewidth=2, label='下游坡面')
        
        # 出逸点
        ax3.plot([B0+m2*H], [y0], 'ro', markersize=10)
        ax3.plot([B0+m2*H], [y0_new], 'go', markersize=10)
        
        ax3.set_xlabel('水平距离 (m)', fontsize=12)
        ax3.set_ylabel('高度 (m)', fontsize=12)
        ax3.set_title('浸润线形态对比', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([0, B0+m2*H+5])
        ax3.set_ylim([0, H])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          坝高：H = {H} m
          上游水深：h₁ = {h1} m
          坝顶宽：B₀ = {B0} m
          坡度：m₁={m1}, m₂={m2}
          渗透系数：k = {k_cm} cm/s
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 无排水设施：
            渗流长度：L = {L} m
            出逸点高度：y₀ = {y0:.2f} m ✓
            单宽渗流量：
              q = {q:.6f} m³/(s·m)
                = {q*86400:.4f} m³/(d·m) ✓
        
        (2) 排水棱体(1:{m_drain})：
            出逸点高度：y₀' = {y0_new:.2f} m ✓
            单宽渗流量：
              q' = {q_new:.6f} m³/(s·m)
                 = {q_new*86400:.4f} m³/(d·m) ✓
        
        (3) 对比分析：
            出逸点降低：{(1-y0_new/y0)*100:.1f}%
            渗流量增加：{(q_new/q-1)*100:.1f}%
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 出逸点：y₀≈0.4√(h₁L)
          • 渗流量：q=k(h₁²-y₀²)/(2L)
          • 排水效果：降低y₀，增大q
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day18_hydraulic_structures/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（18分评分标准）：")
        print("="*60)
        print("✓ (1) 计算渗流长度L (2分)")
        print("✓ (2) 写出出逸点公式 (2分) ⭐")
        print("✓ (3) 计算y₀ (3分) ⭐⭐")
        print("✓ (4) 写出渗流量公式 (2分) ⭐")
        print("✓ (5) 计算q (3分) ⭐⭐")
        print("✓ (6) 排水棱体y₀' (2分)")
        print("✓ (7) 排水后q' (2分)")
        print("✓ (8) 对比分析 (2分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 出逸点：y₀≈0.4√(h₁L)，经验公式")
        print("  ⚠️ 渗流量：q=k(h₁²-y₀²)/(2L)，注意平方")
        print("  ⚠️ 排水作用：降低y₀，但增大梯度")
        print("  ⚠️ 单位：q是单宽流量，单位m³/(s·m)")
        
        return {'y0': y0, 'q': q, 'y0_new': y0_new, 'q_new': q_new}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 18 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 水压力：")
        print("     P = (1/2) × γw × h²")
        print("     作用点：y = h/3")
        print("     ")
        print("  2. 重力坝抗滑：")
        print("     Ks = fW / (P₁-P₂) ≥ 1.05")
        print("     (f为摩擦系数，W为自重)")
        print("     ")
        print("  3. 重力坝抗倾覆：")
        print("     K₀ = ΣMS / ΣM₀ ≥ 1.50")
        print("     (对坝踵取矩)")
        print("     ")
        print("  4. 土坝浸润线出逸点：")
        print("     y₀ ≈ 0.4√(h₁L)")
        print("     (经验公式)")
        print("     ")
        print("  5. 土坝渗流量：")
        print("     q = k(h₁²-y₀²) / (2L)")
        print("     (单宽渗流量)")
        
        print("\n✅ 重力坝稳定分析：")
        print("  ┌──────────┬─────────────┬──────────────┐")
        print("  │ 稳定类型 │ 安全系数     │ 规范要求     │")
        print("  ├──────────┼─────────────┼──────────────┤")
        print("  │ 抗滑     │ Ks=fW/FS    │ ≥1.05        │")
        print("  │ 抗倾覆   │ K₀=MS/M₀    │ ≥1.50        │")
        print("  │ 地基应力 │ σ≤[σ]       │ 按地基确定   │")
        print("  └──────────┴─────────────┴──────────────┘")
        
        print("\n✅ 排水设施对比：")
        print("  ┌────────────┬──────────┬──────────┐")
        print("  │ 设施类型   │ 降低y₀   │ 渗流量   │")
        print("  ├────────────┼──────────┼──────────┤")
        print("  │ 无排水     │ -        │ 较小     │")
        print("  │ 排水棱体   │ 明显     │ 略增     │")
        print("  │ 褥垫排水   │ 很明显   │ 增大     │")
        print("  └────────────┴──────────┴──────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【重力坝稳定题】")
        print("  Step 1: 计算坝体自重W")
        print("  Step 2: 计算水压力P₁、P₂")
        print("  Step 3: 抗滑验算Ks=fW/(P₁-P₂)")
        print("  Step 4: 抗倾覆验算K₀=MS/M₀")
        print("  ")
        print("  【土坝渗流题】")
        print("  Step 1: 确定渗流长度L")
        print("  Step 2: 计算出逸点y₀=0.4√(h₁L)")
        print("  Step 3: 计算渗流量q=k(h₁²-y₀²)/(2L)")
        print("  Step 4: 排水设施影响分析")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：水压力作用点记错（应在h/3处）")
        print("  ❌ 错误2：抗滑系数公式记反")
        print("  ❌ 错误3：浸润线出逸点公式记错")
        print("  ❌ 错误4：忘记单位转换（k的cm/s和m/s）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：重力坝→画受力图→列方程")
        print("  ✓ 技巧2：抗滑抗倾→规范要求→判断满足")
        print("  ✓ 技巧3：土坝渗流→浸润线→出逸点")
        print("  ✓ 技巧4：排水设施→降低y₀→增稳定")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能准确计算重力坝稳定")
        print("  □ 掌握浸润线出逸点")
        print("  □ 理解渗流量计算")
        print("  □ 熟练排水设施分析")
        
        print("\n📅 明日预告：Day 19 - 河流动力学")
        print("  • 泥沙运动")
        print("  • 河床演变")
        print("  • 河道整治")
        
        print("\n💪 今日格言：")
        print("  「水工建筑是综合应用！掌握稳定分析=拿到15分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 18: 水工建筑物")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day18 = Day18HydraulicStructures()
    
    # 例题1：重力坝稳定
    result1 = day18.example_1_gravity_dam()
    
    # 例题2：土坝渗流
    result2 = day18.example_2_earth_dam_seepage()
    
    # 每日总结
    day18.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 18 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握重力坝稳定")
    print(f"  ✓ 掌握土坝渗流")
    print(f"  ✓ 理解排水设施")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n下一步：Day 19 - 河流动力学")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
