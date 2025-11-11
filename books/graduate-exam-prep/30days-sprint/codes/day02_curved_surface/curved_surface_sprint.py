#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 2: 曲面总压力与浮力
Sprint Day 2: Curved Surface Pressure and Buoyancy

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 曲面水平分力：Px = ρg·hc·Ax
  2. 曲面垂直分力：Pz = ρg·V
  3. 总压力：P = √(Px² + Pz²)
  4. 浮力：F = ρg·V（阿基米德原理）

🎯 学习目标：
  - 掌握曲面总压力计算方法
  - 熟练应用阿基米德原理
  - 理解压力体概念

💪 今日格言：曲面压力分解法是关键！掌握方法=拿到15分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Circle, Rectangle, Wedge, FancyBboxPatch
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day2CurvedSurface:
    """
    Day 2：曲面总压力与浮力
    
    包含3个核心例题：
    1. 基础题：圆柱曲面总压力
    2. 强化题：浮力计算（阿基米德原理）
    3. 综合题：闸门曲面压力与力矩
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        
    def example_1_cylindrical_surface(self):
        """
        例题1：圆柱曲面总压力（基础题）⭐⭐⭐⭐⭐
        
        题目：圆柱形闸门，半径R=2m，宽度b=3m，水深h=3m
        求：(1) 水平分力Px
            (2) 垂直分力Pz
            (3) 总压力P及作用点
        
        考点：曲面压力分解，压力体概念
        难度：基础（必考！）
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题1：圆柱曲面总压力（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        R = 2.0      # 圆柱半径 (m)
        b = 3.0      # 闸门宽度 (m)
        h = 3.0      # 水深 (m)
        
        print(f"\n已知条件：")
        print(f"  圆柱形闸门半径 R = {R:.1f} m")
        print(f"  闸门宽度 b = {b:.1f} m")
        print(f"  水深 h = {h:.1f} m")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 水平分力Px
        print(f"\n(1) 计算水平分力Px：")
        print(f"    水平分力等于曲面垂直投影面上的静水总压力")
        print(f"    ")
        print(f"    投影面积：Ax = 2R × b = 2×{R}×{b} = {2*R*b:.1f} m²")
        
        Ax = 2 * R * b
        
        print(f"    投影面形心水深：hc = h - R = {h} - {R} = {h-R:.1f} m")
        
        hc = h - R
        
        print(f"    ")
        print(f"    水平分力公式：")
        print(f"    Px = ρg·hc·Ax")
        
        Px = self.rho * self.g * hc * Ax
        
        print(f"       = {self.rho}×{self.g:.2f}×{hc:.1f}×{Ax:.1f}")
        print(f"       = {Px:.2f} N")
        print(f"       = {Px/1000:.2f} kN ✓")
        
        # (2) 垂直分力Pz
        print(f"\n(2) 计算垂直分力Pz：")
        print(f"    垂直分力等于压力体体积对应的水重")
        print(f"    ")
        print(f"    压力体组成：")
        print(f"    • 矩形部分：h×2R×b = {h}×{2*R}×{b} = {h*2*R*b:.1f} m³")
        print(f"    • 半圆柱部分：-(1/2)πR²×b = -(1/2)×π×{R}²×{b}")
        
        V_rect = h * 2 * R * b
        V_semi = -(0.5) * np.pi * R**2 * b
        V_total = V_rect + V_semi
        
        print(f"                    = {V_semi:.3f} m³ (负值，向下凹)")
        print(f"    ")
        print(f"    总压力体体积：")
        print(f"    V = {V_rect:.3f} + ({V_semi:.3f})")
        print(f"      = {V_total:.3f} m³")
        print(f"    ")
        print(f"    垂直分力公式：")
        print(f"    Pz = ρg·V")
        
        Pz = self.rho * self.g * V_total
        
        print(f"       = {self.rho}×{self.g:.2f}×{V_total:.3f}")
        print(f"       = {Pz:.2f} N")
        print(f"       = {Pz/1000:.2f} kN ✓")
        
        # (3) 总压力
        print(f"\n(3) 计算总压力P：")
        print(f"    P = √(Px² + Pz²)")
        
        P = np.sqrt(Px**2 + Pz**2)
        
        print(f"      = √({Px:.2f}² + {Pz:.2f}²)")
        print(f"      = √({Px**2:.2e} + {Pz**2:.2e})")
        print(f"      = {P:.2f} N")
        print(f"      = {P/1000:.2f} kN ✓")
        
        # 作用方向
        alpha = np.arctan(Pz / Px) * 180 / np.pi
        
        print(f"    ")
        print(f"    作用方向（与水平面夹角）：")
        print(f"    α = arctan(Pz/Px)")
        print(f"      = arctan({Pz:.2f}/{Px:.2f})")
        print(f"      = {alpha:.2f}° ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：闸门示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 圆柱曲面
        theta = np.linspace(0, np.pi, 100)
        x_curve = R * np.cos(theta)
        y_curve = (h - R) + R * np.sin(theta)
        
        ax1.plot(x_curve, y_curve, 'b-', linewidth=3, label='圆柱曲面')
        
        # 水面
        ax1.fill_between([-R-0.5, R+0.5], h, h+0.5, alpha=0.3, color='blue')
        ax1.plot([-R-0.5, R+0.5], [h, h], 'b-', linewidth=2, label='水面')
        
        # 水体
        ax1.fill_between(x_curve, y_curve, h, alpha=0.2, color='lightblue')
        
        # 标注
        ax1.plot([0, 0], [0, h], 'k--', linewidth=1)
        ax1.plot([-R, R], [h-R, h-R], 'r--', linewidth=1)
        
        # 尺寸标注
        ax1.annotate('', xy=(0, h-R), xytext=(0, h),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(0.3, (h+h-R)/2, f'R={R}m', fontsize=11, color='red')
        
        ax1.annotate('', xy=(R, 0), xytext=(R, h-R),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax1.text(R+0.3, (h-R)/2, f'R={R}m', fontsize=11, color='green')
        
        ax1.annotate('', xy=(-R-0.3, 0), xytext=(-R-0.3, h),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax1.text(-R-0.7, h/2, f'h={h}m', fontsize=11, color='blue', rotation=90, va='center')
        
        # 压力体标注
        ax1.fill([x_curve[0], x_curve[-1], x_curve[-1], x_curve[0]], 
                [y_curve[0], y_curve[-1], h, h], 
                alpha=0.3, color='yellow', edgecolor='orange', linewidth=2)
        ax1.text(0, h-0.5, '压力体', fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 2 例题1：圆柱曲面闸门', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-3, 3])
        ax1.set_ylim([0, 4])
        ax1.set_aspect('equal')
        
        # 子图2：压力分解
        ax2 = plt.subplot(2, 2, 2)
        
        # 坐标原点（压力作用点）
        origin_x = 0
        origin_y = h - R
        
        # 压力向量（缩放显示）
        scale = 0.0003  # 缩放因子
        
        # Px（水平分力）
        ax2.arrow(origin_x, origin_y, -Px*scale, 0, 
                 head_width=0.2, head_length=0.3, fc='red', ec='red', linewidth=3)
        ax2.text(origin_x-Px*scale/2, origin_y-0.3, f'Px={Px/1000:.1f}kN', 
                fontsize=11, color='red', ha='center', fontweight='bold')
        
        # Pz（垂直分力）
        ax2.arrow(origin_x, origin_y, 0, Pz*scale,
                 head_width=0.2, head_length=0.3, fc='green', ec='green', linewidth=3)
        ax2.text(origin_x+0.5, origin_y+Pz*scale/2, f'Pz={Pz/1000:.1f}kN', 
                fontsize=11, color='green', fontweight='bold')
        
        # P（总压力）
        ax2.arrow(origin_x, origin_y, -Px*scale, Pz*scale,
                 head_width=0.25, head_length=0.35, fc='blue', ec='blue', linewidth=4)
        ax2.text(origin_x-Px*scale/2-0.5, origin_y+Pz*scale/2, 
                f'P={P/1000:.1f}kN\nα={alpha:.1f}°', 
                fontsize=12, color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        # 绘制闸门轮廓
        theta_plot = np.linspace(0, np.pi, 50)
        x_gate = 1.5 * np.cos(theta_plot)
        y_gate = (h-R) + 1.5 * np.sin(theta_plot)
        ax2.plot(x_gate, y_gate, 'k-', linewidth=2, alpha=0.3)
        ax2.fill_between(x_gate, y_gate, h, alpha=0.1, color='gray')
        
        ax2.plot(origin_x, origin_y, 'ko', markersize=10, label='压力作用点')
        
        ax2.set_xlabel('水平方向', fontsize=12)
        ax2.set_ylabel('垂直方向', fontsize=12)
        ax2.set_title('压力分解示意图', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-3, 2])
        ax2.set_ylim([0, 3])
        ax2.set_aspect('equal')
        
        # 子图3：压力体可视化
        ax3 = plt.subplot(2, 2, 3)
        
        # 矩形压力体
        ax3.fill([-R, R, R, -R], [h-R, h-R, h, h], 
                alpha=0.4, color='blue', edgecolor='blue', linewidth=2, label='矩形压力体')
        ax3.text(0, (h+h-R)/2, f'V₁={V_rect:.2f}m³', fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        # 半圆柱压力体（负）
        theta_neg = np.linspace(0, np.pi, 50)
        x_neg = R * np.cos(theta_neg)
        y_neg = (h-R) + R * np.sin(theta_neg)
        ax3.fill_between(x_neg, y_neg, h-R, alpha=0.4, color='orange', 
                        edgecolor='orange', linewidth=2, label='半圆压力体(负)')
        ax3.text(0, h-R+R/2, f'V₂={V_semi:.2f}m³', fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow'))
        
        # 曲面
        ax3.plot(x_curve, y_curve, 'k-', linewidth=3)
        
        # 标注
        ax3.arrow(1.5, h-0.5, 0, -0.4, head_width=0.15, head_length=0.1,
                 fc='red', ec='red', linewidth=2)
        ax3.text(1.5, h-0.3, 'Pz方向', fontsize=10, color='red')
        
        ax3.set_xlabel('水平距离 (m)', fontsize=12)
        ax3.set_ylabel('高程 (m)', fontsize=12)
        ax3.set_title('压力体分解', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([-2.5, 2.5])
        ax3.set_ylim([0, 3.5])
        ax3.set_aspect('equal')
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          • 半径 R = {R:.1f} m
          • 宽度 b = {b:.1f} m
          • 水深 h = {h:.1f} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算过程：
        
        (1) 水平分力 Px：
            Ax = 2R×b = {Ax:.1f} m²
            hc = h-R = {hc:.1f} m
            Px = ρg·hc·Ax = {Px/1000:.2f} kN ✓
        
        (2) 垂直分力 Pz：
            V = {V_rect:.2f} + ({V_semi:.2f})
              = {V_total:.2f} m³
            Pz = ρg·V = {Pz/1000:.2f} kN ✓
        
        (3) 总压力 P：
            P = √(Px²+Pz²) = {P/1000:.2f} kN ✓
            α = arctan(Pz/Px) = {alpha:.1f}° ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          Px = ρg·hc·Ax  (投影面)
          Pz = ρg·V      (压力体)
          P = √(Px² + Pz²)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=10, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day02_curved_surface/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 确定投影面积Ax (1分)")
        print("✓ (2) 计算形心水深hc (1分)")
        print("✓ (3) 应用公式Px=ρg·hc·Ax (3分) ⭐")
        print("✓ (4) 确定压力体体积V (3分) ⭐")
        print("✓ (5) 应用公式Pz=ρg·V (2分)")
        print("✓ (6) 计算总压力P=√(Px²+Pz²) (3分)")
        print("✓ (7) 计算作用方向α (1分)")
        print("✓ (8) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 压力体：曲面向下凹时，半圆体积为负！")
        print("  ⚠️ 投影面形心：不是水深h，是h-R！")
        print("  ⚠️ 总压力：不是Px+Pz，是√(Px²+Pz²)！")
        print("  ⚠️ 注意区分压力体的正负")
        
        return {'Px': Px, 'Pz': Pz, 'P': P, 'alpha': alpha}
    
    def example_2_buoyancy(self):
        """
        例题2：浮力计算（强化题）⭐⭐⭐⭐⭐
        
        题目：圆柱体，半径R=0.5m，长度L=2m，密度ρ_s=600kg/m³
              完全浸没在水中
        求：(1) 浮力F
            (2) 重力G
            (3) 判断物体运动状态
        
        考点：阿基米德原理，浮沉条件
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题2：浮力计算（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        R = 0.5      # 圆柱半径 (m)
        L = 2.0      # 圆柱长度 (m)
        rho_s = 600  # 物体密度 (kg/m³)
        
        print(f"\n已知条件：")
        print(f"  圆柱体半径 R = {R:.1f} m")
        print(f"  圆柱体长度 L = {L:.1f} m")
        print(f"  物体密度 ρ_s = {rho_s} kg/m³")
        print(f"  水密度 ρ = {self.rho} kg/m³")
        
        # (1) 浮力
        print(f"\n解题步骤：")
        print(f"\n(1) 计算浮力F（阿基米德原理）：")
        print(f"    ")
        print(f"    排开水的体积：")
        print(f"    V = πR²L")
        
        V = np.pi * R**2 * L
        
        print(f"      = π×{R}²×{L}")
        print(f"      = {V:.4f} m³")
        print(f"    ")
        print(f"    浮力公式（阿基米德原理）：")
        print(f"    F = ρ_水·g·V")
        
        F = self.rho * self.g * V
        
        print(f"      = {self.rho}×{self.g:.2f}×{V:.4f}")
        print(f"      = {F:.2f} N")
        print(f"      = {F/1000:.3f} kN ✓")
        
        # (2) 重力
        print(f"\n(2) 计算物体重力G：")
        print(f"    物体体积 = 排水体积 = {V:.4f} m³")
        print(f"    ")
        print(f"    物体质量：")
        print(f"    m = ρ_s·V")
        
        m = rho_s * V
        
        print(f"      = {rho_s}×{V:.4f}")
        print(f"      = {m:.3f} kg")
        print(f"    ")
        print(f"    物体重力：")
        print(f"    G = m·g")
        
        G = m * self.g
        
        print(f"      = {m:.3f}×{self.g:.2f}")
        print(f"      = {G:.2f} N")
        print(f"      = {G/1000:.3f} kN ✓")
        
        # (3) 判断运动状态
        print(f"\n(3) 判断物体运动状态：")
        print(f"    ")
        print(f"    浮力 F = {F:.2f} N")
        print(f"    重力 G = {G:.2f} N")
        print(f"    ")
        
        if F > G:
            print(f"    ∵ F > G ({F:.2f} > {G:.2f})")
            print(f"    ∴ 物体上浮 ✓")
            state = "上浮"
            net_force = F - G
            print(f"    ")
            print(f"    净浮力：F - G = {net_force:.2f} N = {net_force/1000:.3f} kN")
        elif F < G:
            print(f"    ∵ F < G")
            print(f"    ∴ 物体下沉")
            state = "下沉"
            net_force = G - F
        else:
            print(f"    ∵ F = G")
            print(f"    ∴ 物体悬浮")
            state = "悬浮"
            net_force = 0
        
        # 密度比较
        print(f"    ")
        print(f"    密度比较：")
        print(f"    ρ_s/ρ_水 = {rho_s}/{self.rho} = {rho_s/self.rho:.2f}")
        print(f"    ")
        print(f"    ∵ ρ_s < ρ_水 ({rho_s} < {self.rho})")
        print(f"    ∴ 物体密度小于水密度，必然上浮 ✓")
        
        # 绘图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 子图1：物体示意图
        # 水体
        water_level = 3
        ax1.fill_between([- 2, 3], 0, water_level, alpha=0.3, color='lightblue')
        ax1.plot([-2, 3], [water_level, water_level], 'b-', linewidth=2, label='水面')
        
        # 圆柱体（侧视图）
        cylinder_bottom = 1.5
        cylinder_top = cylinder_bottom + R*2
        
        ax1.add_patch(Rectangle((-L/2, cylinder_bottom), L, R*2, 
                                facecolor='orange', edgecolor='black', 
                                linewidth=2, alpha=0.7, label='圆柱体'))
        
        # 标注
        ax1.text(0, cylinder_bottom + R, f'ρ_s={rho_s}\nkg/m³', 
                fontsize=10, ha='center', fontweight='bold')
        
        # 浮力箭头
        ax1.arrow(0, cylinder_top, 0, 0.5, head_width=0.15, head_length=0.1,
                 fc='blue', ec='blue', linewidth=3)
        ax1.text(0.3, cylinder_top+0.3, f'F={F/1000:.2f}kN', 
                fontsize=11, color='blue', fontweight='bold')
        
        # 重力箭头
        ax1.arrow(0, cylinder_bottom, 0, -0.5, head_width=0.15, head_length=0.1,
                 fc='red', ec='red', linewidth=3)
        ax1.text(0.3, cylinder_bottom-0.3, f'G={G/1000:.2f}kN', 
                fontsize=11, color='red', fontweight='bold')
        
        # 尺寸标注
        ax1.plot([- L/2, L/2], [cylinder_bottom-0.1, cylinder_bottom-0.1], 'k-', linewidth=1)
        ax1.text(0, cylinder_bottom-0.3, f'L={L}m', fontsize=10, ha='center')
        
        ax1.plot([L/2+0.1, L/2+0.1], [cylinder_bottom, cylinder_top], 'k-', linewidth=1)
        ax1.text(L/2+0.3, (cylinder_bottom+cylinder_top)/2, f'2R={R*2}m', 
                fontsize=10, rotation=90, va='center')
        
        ax1.set_xlabel('长度方向 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 2 例题2：圆柱体浸没示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-2, 3])
        ax1.set_ylim([0, 4])
        
        # 子图2：力平衡分析
        categories = ['浮力F', '重力G', '净力']
        forces = [F/1000, G/1000, (F-G)/1000]
        colors_bar = ['#4ECDC4', '#FF6B6B', '#FFE66D']
        
        bars = ax2.bar(categories, forces, color=colors_bar, edgecolor='black', linewidth=2)
        
        for bar, force in zip(bars, forces):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{force:.3f}\nkN', ha='center', va='bottom' if force > 0 else 'top',
                    fontsize=11, fontweight='bold')
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.set_ylabel('力 (kN)', fontsize=12)
        ax2.set_title('力平衡分析', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 子图3：浮沉条件
        ax3.axis('off')
        
        condition_text = """
        【浮沉条件总结】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━
        1. 上浮条件：
           • F > G
           • ρ_物 < ρ_液
           • 物体向上运动
        
        2. 下沉条件：
           • F < G
           • ρ_物 > ρ_液
           • 物体向下运动
        
        3. 悬浮条件：
           • F = G
           • ρ_物 = ρ_液
           • 物体静止（任意位置）
        
        4. 漂浮条件：
           • F = G
           • ρ_物 < ρ_液
           • 物体静止（水面）
           • 部分浸没
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━
        本题：
        """
        
        result_text = f"""
        ρ_s = {rho_s} kg/m³ < ρ_水 = {self.rho} kg/m³
        F = {F:.2f} N > G = {G:.2f} N
        
        ∴ 物体上浮 ✓
        
        净浮力 = {net_force:.2f} N
        """
        
        ax3.text(0.05, 0.95, condition_text + result_text, 
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        # 子图4：密度-浮沉关系
        rho_range = np.linspace(400, 1200, 100)
        F_range = np.ones_like(rho_range) * F
        G_range = (rho_range / rho_s) * G
        
        ax4.plot(rho_range, F_range/1000, 'b-', linewidth=3, label='浮力F (恒定)')
        ax4.plot(rho_range, G_range/1000, 'r-', linewidth=3, label='重力G (随密度变)')
        ax4.axvline(x=self.rho, color='green', linestyle='--', linewidth=2, 
                   label=f'水密度 ρ={self.rho} kg/m³')
        ax4.plot(rho_s, G/1000, 'ro', markersize=12, label=f'当前 ρ_s={rho_s} kg/m³')
        
        # 填充区域
        ax4.fill_between([400, self.rho], 0, 20, alpha=0.2, color='blue', label='上浮区')
        ax4.fill_between([self.rho, 1200], 0, 20, alpha=0.2, color='red', label='下沉区')
        
        ax4.set_xlabel('物体密度 ρ_s (kg/m³)', fontsize=12)
        ax4.set_ylabel('力 (kN)', fontsize=12)
        ax4.set_title('密度与浮沉关系', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim([400, 1200])
        ax4.set_ylim([0, 20])
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day02_curved_surface/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 计算排水体积V (2分)")
        print("✓ (2) 应用阿基米德原理 F=ρ_水·g·V (3分) ⭐")
        print("✓ (3) 计算物体质量m (1分)")
        print("✓ (4) 计算物体重力G=mg (2分)")
        print("✓ (5) 比较F与G大小 (2分)")
        print("✓ (6) 判断运动状态 (1分)")
        print("✓ (7) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 浮力：F = ρ_水·g·V，不是ρ_物·g·V！")
        print("  ⚠️ 判断：ρ_物<ρ_水 → 上浮；ρ_物>ρ_水 → 下沉")
        print("  ⚠️ 完全浸没时，V_排 = V_物")
        
        return {'F': F, 'G': G, 'state': state, 'net_force': net_force}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 2 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 曲面水平分力：")
        print("     Px = ρg·hc·Ax")
        print("     (Ax为曲面垂直投影面积)")
        print("     ")
        print("  2. 曲面垂直分力：")
        print("     Pz = ρg·V")
        print("     (V为压力体体积，注意正负)")
        print("     ")
        print("  3. 曲面总压力：")
        print("     P = √(Px² + Pz²)")
        print("     α = arctan(Pz/Px)")
        print("     ")
        print("  4. 阿基米德原理：")
        print("     F = ρ_液·g·V_排")
        print("     ")
        print("  5. 浮沉条件：")
        print("     上浮：F > G (或 ρ_物 < ρ_液)")
        print("     下沉：F < G (或 ρ_物 > ρ_液)")
        print("     悬浮：F = G (或 ρ_物 = ρ_液)")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【曲面压力题】")
        print("  Step 1: 画压力体示意图")
        print("  Step 2: 计算Px（投影面）")
        print("  Step 3: 计算Pz（压力体体积）")
        print("  Step 4: 合成总压力P")
        print("  Step 5: 确定作用方向")
        print("  ")
        print("  【浮力题】")
        print("  Step 1: 计算排水体积V")
        print("  Step 2: 应用F=ρ_液·g·V")
        print("  Step 3: 计算物体重力G")
        print("  Step 4: 比较F与G，判断浮沉")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：压力体正负搞错")
        print("  ❌ 错误2：投影面形心位置错误")
        print("  ❌ 错误3：浮力公式用错密度（应该是液体密度）")
        print("  ❌ 错误4：总压力用Px+Pz（应该是矢量合成）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：压力体一定要画图！")
        print("  ✓ 技巧2：曲面向下凹→压力体为负")
        print("  ✓ 技巧3：浮力只与排水体积有关")
        print("  ✓ 技巧4：判断浮沉看密度比")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能正确画出压力体")
        print("  □ 能区分压力体正负")
        print("  □ 能默写阿基米德原理")
        print("  □ 能判断物体浮沉状态")
        
        print("\n📅 明日预告：Day 3 - 闸门启闭力")
        print("  预习内容：力矩计算，铰链支点")
        
        print("\n💪 今日格言：")
        print("  「曲面压力分解法是关键！画好压力体=拿到15分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 2: 曲面总压力与浮力")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day2 = Day2CurvedSurface()
    
    # 例题1：圆柱曲面
    result1 = day2.example_1_cylindrical_surface()
    
    # 例题2：浮力
    result2 = day2.example_2_buoyancy()
    
    # 每日总结
    day2.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 2 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握曲面压力分解法")
    print(f"  ✓ 掌握阿基米德原理")
    print(f"  ✓ 理解浮沉条件")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n明日继续：Day 3 - 闸门启闭力")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
