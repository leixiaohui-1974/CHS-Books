#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 5: 连续性与动量方程
Sprint Day 5: Continuity and Momentum Equations

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 连续性方程：Q = A₁v₁ = A₂v₂
  2. 动量方程：F = ρQ(v₂ - v₁)
  3. 弯管受力：F = ρQ|v₂ - v₁|

🎯 学习目标：
  - 掌握连续性方程应用
  - 熟练应用动量方程
  - 理解流体对边界的作用力

💪 今日格言：动量方程是考研重点！掌握方法=拿到18分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.patches import Arc, Wedge
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day5ContinuityMomentum:
    """
    Day 5：连续性与动量方程
    
    包含2个核心例题：
    1. 基础题：渐变管流动（连续性方程）
    2. 强化题：弯管受力（动量方程）
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        
    def example_1_continuity(self):
        """
        例题1：渐变管流动（基础题）⭐⭐⭐⭐⭐
        
        题目：圆管渐变段，入口直径d₁=0.2m，出口直径d₂=0.1m
              入口流速v₁=2m/s
        求：(1) 流量Q
            (2) 出口流速v₂
            (3) 流速变化率
        
        考点：连续性方程，质量守恒
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题1：渐变管流动（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d1 = 0.2     # 入口直径 (m)
        d2 = 0.1     # 出口直径 (m)
        v1 = 2.0     # 入口流速 (m/s)
        
        print(f"\n已知条件：")
        print(f"  入口直径 d₁ = {d1:.1f} m")
        print(f"  出口直径 d₂ = {d2:.1f} m")
        print(f"  入口流速 v₁ = {v1:.1f} m/s")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 流量
        print(f"\n(1) 计算流量Q：")
        print(f"    入口断面积：")
        print(f"    A₁ = π(d₁/2)² = π×({d1}/2)²")
        
        A1 = np.pi * (d1/2)**2
        
        print(f"       = {A1:.6f} m²")
        print(f"    ")
        print(f"    流量公式：")
        print(f"    Q = A₁ × v₁")
        
        Q = A1 * v1
        
        print(f"      = {A1:.6f} × {v1}")
        print(f"      = {Q:.6f} m³/s ✓")
        
        # (2) 出口流速
        print(f"\n(2) 计算出口流速v₂（连续性方程）：")
        print(f"    出口断面积：")
        print(f"    A₂ = π(d₂/2)² = π×({d2}/2)²")
        
        A2 = np.pi * (d2/2)**2
        
        print(f"       = {A2:.6f} m²")
        print(f"    ")
        print(f"    连续性方程（质量守恒）：")
        print(f"    Q = A₁v₁ = A₂v₂")
        print(f"    ")
        print(f"    v₂ = Q/A₂")
        
        v2 = Q / A2
        
        print(f"       = {Q:.6f}/{A2:.6f}")
        print(f"       = {v2:.2f} m/s ✓")
        
        # 验证连续性方程
        Q_check = A2 * v2
        print(f"    ")
        print(f"    验证：Q = A₂v₂ = {A2:.6f}×{v2:.2f}")
        print(f"           = {Q_check:.6f} m³/s ≈ {Q:.6f} m³/s ✓")
        
        # (3) 流速变化率
        print(f"\n(3) 流速变化率分析：")
        ratio_A = A2 / A1
        ratio_d = d2 / d1
        ratio_v = v2 / v1
        
        print(f"    面积比：A₂/A₁ = {A2:.6f}/{A1:.6f} = {ratio_A:.4f}")
        print(f"    直径比：d₂/d₁ = {d2}/{d1} = {ratio_d:.2f}")
        print(f"    流速比：v₂/v₁ = {v2:.2f}/{v1:.1f} = {ratio_v:.2f}")
        print(f"    ")
        print(f"    分析：")
        print(f"    ∵ A₂/A₁ = (d₂/d₁)² = {ratio_d:.2f}² = {ratio_d**2:.4f}")
        print(f"    ∴ v₂/v₁ = A₁/A₂ = 1/{ratio_A:.4f} = {1/ratio_A:.2f} ✓")
        print(f"    ")
        print(f"    结论：断面积减小到1/4，流速增加到4倍")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：渐变管示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 管道轮廓
        x_pipe = np.linspace(0, 3, 100)
        y_upper = d1/2 - (d1/2 - d2/2) * (x_pipe/3)
        y_lower = -(d1/2 - (d1/2 - d2/2) * (x_pipe/3))
        
        ax1.fill_between(x_pipe, y_lower, y_upper, alpha=0.3, color='lightblue', 
                        edgecolor='blue', linewidth=2)
        ax1.plot(x_pipe, y_upper, 'b-', linewidth=2)
        ax1.plot(x_pipe, y_lower, 'b-', linewidth=2)
        
        # 入口断面
        ax1.plot([0, 0], [-d1/2, d1/2], 'r-', linewidth=3, label='入口断面')
        ax1.text(-0.3, 0, f'd₁={d1}m', fontsize=11, color='red', 
                rotation=90, va='center')
        
        # 出口断面
        ax1.plot([3, 3], [-d2/2, d2/2], 'g-', linewidth=3, label='出口断面')
        ax1.text(3.3, 0, f'd₂={d2}m', fontsize=11, color='green', 
                rotation=90, va='center')
        
        # 流速箭头（入口）
        num_arrows = 3
        for i in range(num_arrows):
            y_pos = -d1/4 + i * d1/4
            ax1.arrow(-0.5, y_pos, 0.4, 0, head_width=0.02, head_length=0.08,
                     fc='red', ec='red', linewidth=2)
        ax1.text(-0.5, d1/2+0.05, f'v₁={v1}m/s', fontsize=11, color='red', 
                fontweight='bold')
        
        # 流速箭头（出口）
        for i in range(num_arrows):
            y_pos = -d2/4 + i * d2/4
            ax1.arrow(3, y_pos, 0.6, 0, head_width=0.02, head_length=0.08,
                     fc='green', ec='green', linewidth=2)
        ax1.text(3.2, d2/2+0.05, f'v₂={v2:.1f}m/s', fontsize=11, color='green', 
                fontweight='bold')
        
        # 流量标注
        ax1.text(1.5, 0.15, f'Q={Q:.4f}m³/s', fontsize=12, 
                bbox=dict(boxstyle='round', facecolor='yellow'),
                ha='center', fontweight='bold')
        
        ax1.set_xlabel('管道长度方向 (m)', fontsize=12)
        ax1.set_ylabel('管道半径 (m)', fontsize=12)
        ax1.set_title('Day 5 例题1：渐变管流动示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.8, 4])
        ax1.set_ylim([-0.15, 0.2])
        ax1.set_aspect('equal')
        
        # 子图2：流速与面积关系
        ax2 = plt.subplot(2, 2, 2)
        
        # 沿程变化
        x_range = np.linspace(0, 3, 50)
        d_range = d1 - (d1 - d2) * (x_range/3)
        A_range = np.pi * (d_range/2)**2
        v_range = Q / A_range
        
        ax2_twin = ax2.twinx()
        
        # 面积曲线
        line1 = ax2.plot(x_range, A_range*1000, 'b-', linewidth=3, label='断面积A')
        ax2.set_ylabel('断面积 A (cm²)', fontsize=12, color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        # 流速曲线
        line2 = ax2_twin.plot(x_range, v_range, 'r-', linewidth=3, label='流速v')
        ax2_twin.set_ylabel('流速 v (m/s)', fontsize=12, color='red')
        ax2_twin.tick_params(axis='y', labelcolor='red')
        
        # 标注关键点
        ax2.plot(0, A1*1000, 'bo', markersize=10)
        ax2.plot(3, A2*1000, 'bo', markersize=10)
        ax2_twin.plot(0, v1, 'ro', markersize=10)
        ax2_twin.plot(3, v2, 'ro', markersize=10)
        
        ax2.text(0, A1*1000+5, f'A₁={A1*1000:.1f}cm²', fontsize=10, color='blue')
        ax2.text(3, A2*1000+5, f'A₂={A2*1000:.1f}cm²', fontsize=10, color='blue')
        ax2_twin.text(0, v1+0.5, f'v₁={v1}m/s', fontsize=10, color='red')
        ax2_twin.text(3, v2+0.5, f'v₂={v2:.1f}m/s', fontsize=10, color='red')
        
        ax2.set_xlabel('管道长度 (m)', fontsize=12)
        ax2.set_title('流速与断面积沿程变化', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='center left')
        
        # 子图3：连续性方程验证
        ax3 = plt.subplot(2, 2, 3)
        
        categories = ['入口\nA₁v₁', '出口\nA₂v₂']
        flows = [A1*v1, A2*v2]
        colors_bar = ['#FF6B6B', '#4ECDC4']
        
        bars = ax3.bar(categories, flows, color=colors_bar, edgecolor='black', linewidth=2)
        
        for bar, flow in zip(bars, flows):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{flow:.6f}\nm³/s', ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        # 标注相等
        ax3.plot([0, 1], [Q*1.1, Q*1.1], 'k-', linewidth=2)
        ax3.text(0.5, Q*1.12, 'Q相等', ha='center', fontsize=12, 
                fontweight='bold', bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_ylabel('流量 (m³/s)', fontsize=12)
        ax3.set_title('连续性方程验证', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_ylim([0, Q*1.2])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          • 入口直径 d₁ = {d1:.1f} m
          • 出口直径 d₂ = {d2:.1f} m
          • 入口流速 v₁ = {v1:.1f} m/s
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 流量：
            A₁ = π(d₁/2)² = {A1:.6f} m²
            Q = A₁v₁ = {Q:.6f} m³/s ✓
        
        (2) 出口流速：
            A₂ = π(d₂/2)² = {A2:.6f} m²
            v₂ = Q/A₂ = {v2:.2f} m/s ✓
        
        (3) 变化率：
            A₂/A₁ = {ratio_A:.4f}
            v₂/v₁ = {ratio_v:.2f} ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          连续性方程：Q = A₁v₁ = A₂v₂
          
          结论：断面积↓ → 流速↑
               A₂ = A₁/4 → v₂ = 4v₁
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day05_continuity_momentum/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 计算入口断面积A₁ (1分)")
        print("✓ (2) 计算流量Q=A₁v₁ (2分)")
        print("✓ (3) 计算出口断面积A₂ (1分)")
        print("✓ (4) 应用连续性方程Q=A₂v₂ (3分) ⭐")
        print("✓ (5) 求解出口流速v₂ (3分)")
        print("✓ (6) 分析流速变化率 (1分)")
        print("✓ (7) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 连续性方程：Q=A₁v₁=A₂v₂，质量守恒！")
        print("  ⚠️ 断面积与直径：A=π(d/2)²=πd²/4")
        print("  ⚠️ 流速关系：A↓→v↑，成反比")
        
        return {'Q': Q, 'v2': v2, 'A1': A1, 'A2': A2}
    
    def example_2_momentum(self):
        """
        例题2：弯管受力（强化题）⭐⭐⭐⭐⭐
        
        题目：90°弯管，直径d=0.15m，流量Q=0.05m³/s
              入口水平向右，出口竖直向上，忽略重力和摩阻
        求：(1) 流速v
            (2) 水流对弯管的作用力F
            (3) 作用力方向
        
        考点：动量方程，矢量运算
        难度：强化（必考！）
        时间：20分钟
        分值：18分
        """
        print("\n" + "="*60)
        print("例题2：弯管受力（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d = 0.15     # 管道直径 (m)
        Q = 0.05     # 流量 (m³/s)
        
        print(f"\n已知条件：")
        print(f"  管道直径 d = {d:.2f} m")
        print(f"  流量 Q = {Q:.2f} m³/s")
        print(f"  弯管角度：90°")
        print(f"  入口方向：水平向右")
        print(f"  出口方向：竖直向上")
        
        # (1) 流速
        print(f"\n解题步骤：")
        print(f"\n(1) 计算流速v：")
        
        A = np.pi * (d/2)**2
        v = Q / A
        
        print(f"    断面积 A = π(d/2)² = π×({d}/2)²")
        print(f"             = {A:.6f} m²")
        print(f"    ")
        print(f"    流速 v = Q/A = {Q}/{A:.6f}")
        print(f"           = {v:.3f} m/s ✓")
        
        # (2) 动量方程
        print(f"\n(2) 应用动量方程计算弯管受力：")
        print(f"    ")
        print(f"    建立坐标系（x水平向右，y竖直向上）：")
        print(f"    ")
        print(f"    入口：v₁ = {v:.3f} m/s (水平向右)")
        print(f"          v₁ₓ = {v:.3f} m/s")
        print(f"          v₁ᵧ = 0 m/s")
        print(f"    ")
        print(f"    出口：v₂ = {v:.3f} m/s (竖直向上)")
        print(f"          v₂ₓ = 0 m/s")
        print(f"          v₂ᵧ = {v:.3f} m/s")
        
        # 速度分量
        v1x = v
        v1y = 0
        v2x = 0
        v2y = v
        
        print(f"    ")
        print(f"    动量方程（矢量形式）：")
        print(f"    F⃗ = ρQ(v⃗₂ - v⃗₁)")
        print(f"    ")
        print(f"    x方向：")
        print(f"    Fₓ = ρQ(v₂ₓ - v₁ₓ)")
        
        Fx = self.rho * Q * (v2x - v1x)
        
        print(f"       = {self.rho} × {Q} × ({v2x} - {v1x:.3f})")
        print(f"       = {Fx:.2f} N")
        print(f"       = {Fx/1000:.3f} kN ✓")
        print(f"    ")
        print(f"    y方向：")
        print(f"    Fᵧ = ρQ(v₂ᵧ - v₁ᵧ)")
        
        Fy = self.rho * Q * (v2y - v1y)
        
        print(f"       = {self.rho} × {Q} × ({v2y:.3f} - {v1y})")
        print(f"       = {Fy:.2f} N")
        print(f"       = {Fy/1000:.3f} kN ✓")
        
        # 合力
        F_total = np.sqrt(Fx**2 + Fy**2)
        alpha = np.arctan(abs(Fy/Fx)) * 180 / np.pi
        
        print(f"    ")
        print(f"    合力大小：")
        print(f"    F = √(Fₓ² + Fᵧ²)")
        print(f"      = √({Fx:.2f}² + {Fy:.2f}²)")
        print(f"      = {F_total:.2f} N")
        print(f"      = {F_total/1000:.3f} kN ✓")
        
        # (3) 方向
        print(f"\n(3) 作用力方向分析：")
        print(f"    ")
        print(f"    Fₓ = {Fx:.2f} N < 0 (向左)")
        print(f"    Fᵧ = {Fy:.2f} N > 0 (向上)")
        print(f"    ")
        print(f"    方向角（与水平面夹角）：")
        print(f"    α = arctan(|Fᵧ/Fₓ|)")
        print(f"      = arctan({abs(Fy):.2f}/{abs(Fx):.2f})")
        print(f"      = {alpha:.2f}°")
        print(f"    ")
        print(f"    说明：水流对弯管的作用力指向左上方")
        print(f"         （与入口方向相反，与出口方向相同）")
        
        # 弯管对水流的反作用力
        Fx_reaction = -Fx
        Fy_reaction = -Fy
        
        print(f"    ")
        print(f"    弯管对水流的反作用力（方向相反）：")
        print(f"    Fₓ' = {Fx_reaction:.2f} N (向右)")
        print(f"    Fᵧ' = {Fy_reaction:.2f} N (向下)")
        
        # 绘图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 子图1：弯管示意图
        # 弯管（90°）
        theta = np.linspace(0, np.pi/2, 50)
        r_inner = 0.3
        r_outer = r_inner + d
        
        # 外弧
        x_outer = r_outer * np.cos(theta)
        y_outer = r_outer * np.sin(theta)
        
        # 内弧
        x_inner = r_inner * np.cos(theta)
        y_inner = r_inner * np.sin(theta)
        
        # 绘制弯管
        ax1.fill(np.concatenate([x_outer, x_inner[::-1]]),
                np.concatenate([y_outer, y_inner[::-1]]),
                color='gray', alpha=0.7, edgecolor='black', linewidth=2)
        
        # 入口段
        ax1.fill([-0.5, 0, 0, -0.5],
                [r_inner, r_inner, r_outer, r_outer],
                color='gray', alpha=0.7, edgecolor='black', linewidth=2)
        
        # 出口段
        ax1.fill([r_inner, r_inner, r_outer, r_outer],
                [r_outer, r_outer+0.5, r_outer+0.5, r_outer],
                color='gray', alpha=0.7, edgecolor='black', linewidth=2)
        
        # 流速箭头（入口）
        ax1.arrow(-0.4, (r_inner+r_outer)/2, 0.3, 0, 
                 head_width=0.05, head_length=0.08,
                 fc='blue', ec='blue', linewidth=3)
        ax1.text(-0.4, (r_inner+r_outer)/2+0.1, f'v₁={v:.2f}m/s', 
                fontsize=11, color='blue', fontweight='bold')
        
        # 流速箭头（出口）
        ax1.arrow((r_inner+r_outer)/2, r_outer, 0, 0.3,
                 head_width=0.05, head_length=0.08,
                 fc='blue', ec='blue', linewidth=3)
        ax1.text((r_inner+r_outer)/2+0.1, r_outer+0.35, f'v₂={v:.2f}m/s', 
                fontsize=11, color='blue', fontweight='bold')
        
        # 作用力箭头（水流对弯管）
        scale = 0.001
        F_start_x = 0.2
        F_start_y = 0.2
        ax1.arrow(F_start_x, F_start_y, Fx*scale, Fy*scale,
                 head_width=0.05, head_length=0.08,
                 fc='red', ec='red', linewidth=4)
        ax1.text(F_start_x+Fx*scale-0.15, F_start_y+Fy*scale+0.05,
                f'F={F_total/1000:.2f}kN\n(水→管)', 
                fontsize=11, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.set_xlabel('x方向 (m)', fontsize=12)
        ax1.set_ylabel('y方向 (m)', fontsize=12)
        ax1.set_title('Day 5 例题2：90°弯管受力示意图', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.6, 0.8])
        ax1.set_ylim([0, 1.0])
        ax1.set_aspect('equal')
        
        # 子图2：速度矢量图
        ax2.quiver(0, 0, v1x, v1y, angles='xy', scale_units='xy', scale=1,
                  color='blue', width=0.015, label='v₁ (入口)')
        ax2.quiver(0, 0, v2x, v2y, angles='xy', scale_units='xy', scale=1,
                  color='green', width=0.015, label='v₂ (出口)')
        ax2.quiver(0, 0, v2x-v1x, v2y-v1y, angles='xy', scale_units='xy', scale=1,
                  color='red', width=0.015, label='v₂-v₁')
        
        # 标注
        ax2.text(v1x/2, -0.3, f'v₁={v:.2f}m/s', fontsize=11, color='blue', ha='center')
        ax2.text(-0.3, v2y/2, f'v₂={v:.2f}m/s', fontsize=11, color='green', rotation=90, va='center')
        ax2.text((v2x-v1x)/2-0.5, (v2y-v1y)/2, f'Δv', fontsize=12, color='red', fontweight='bold')
        
        ax2.set_xlabel('x方向 (m/s)', fontsize=12)
        ax2.set_ylabel('y方向 (m/s)', fontsize=12)
        ax2.set_title('速度矢量变化', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-3, 3])
        ax2.set_ylim([-1, 3])
        ax2.set_aspect('equal')
        ax2.axhline(y=0, color='k', linewidth=0.5)
        ax2.axvline(x=0, color='k', linewidth=0.5)
        
        # 子图3：力的分解
        categories = ['Fₓ\n(x方向)', 'Fᵧ\n(y方向)', 'F\n(合力)']
        forces = [abs(Fx)/1000, Fy/1000, F_total/1000]
        colors_bar = ['#FF6B6B', '#4ECDC4', '#FFE66D']
        
        bars = ax3.bar(categories, forces, color=colors_bar, edgecolor='black', linewidth=2)
        
        for i, (bar, force) in enumerate(zip(bars, forces)):
            height = bar.get_height()
            if i == 0:
                label = f'{force:.3f}kN\n(向左)'
            elif i == 1:
                label = f'{force:.3f}kN\n(向上)'
            else:
                label = f'{force:.3f}kN\n({alpha:.1f}°)'
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    label, ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        ax3.set_ylabel('力 (kN)', fontsize=12)
        ax3.set_title('弯管受力分解', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：动量方程总结
        ax4.axis('off')
        
        summary_text = f"""
        【动量方程应用】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        动量方程（矢量形式）：
          F⃗ = ρQ(v⃗₂ - v⃗₁)
        
        分量形式：
          Fₓ = ρQ(v₂ₓ - v₁ₓ)
          Fᵧ = ρQ(v₂ᵧ - v₁ᵧ)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        本题计算：
        
        入口速度：
          v₁ₓ = {v1x:.3f} m/s (→)
          v₁ᵧ = {v1y} m/s
        
        出口速度：
          v₂ₓ = {v2x} m/s
          v₂ᵧ = {v2y:.3f} m/s (↑)
        
        作用力：
          Fₓ = {Fx:.2f} N (←)
          Fᵧ = {Fy:.2f} N (↑)
          F = {F_total:.2f} N
          α = {alpha:.1f}° (左上方)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        物理意义：
          • 水流转向需要外力
          • 弯管提供约束力
          • 作用力与反作用力
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.05, 0.95, summary_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day05_continuity_momentum/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（18分评分标准）：")
        print("="*60)
        print("✓ (1) 计算流速v=Q/A (2分)")
        print("✓ (2) 建立坐标系 (1分)")
        print("✓ (3) 确定入口速度v₁分量 (2分)")
        print("✓ (4) 确定出口速度v₂分量 (2分)")
        print("✓ (5) 应用动量方程Fₓ=ρQ(v₂ₓ-v₁ₓ) (3分) ⭐⭐")
        print("✓ (6) 应用动量方程Fᵧ=ρQ(v₂ᵧ-v₁ᵧ) (3分) ⭐⭐")
        print("✓ (7) 计算合力F=√(Fₓ²+Fᵧ²) (2分)")
        print("✓ (8) 确定力的方向 (2分)")
        print("✓ (9) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 动量方程：F=ρQ(v₂-v₁)，是矢量方程！")
        print("  ⚠️ 速度方向：一定要分解为x、y分量")
        print("  ⚠️ 力的方向：Fₓ<0表示向左，Fᵧ>0表示向上")
        print("  ⚠️ 作用力与反作用力：水对管 vs 管对水")
        
        return {'v': v, 'Fx': Fx, 'Fy': Fy, 'F_total': F_total, 'alpha': alpha}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 5 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 连续性方程（质量守恒）：")
        print("     Q = A₁v₁ = A₂v₂ = 常数")
        print("     ")
        print("  2. 动量方程（矢量形式）：")
        print("     F⃗ = ρQ(v⃗₂ - v⃗₁)")
        print("     ")
        print("  3. 动量方程（分量形式）：")
        print("     Fₓ = ρQ(v₂ₓ - v₁ₓ)")
        print("     Fᵧ = ρQ(v₂ᵧ - v₁ᵧ)")
        print("     ")
        print("  4. 合力大小：")
        print("     F = √(Fₓ² + Fᵧ²)")
        print("     ")
        print("  5. 力的方向：")
        print("     α = arctan(Fᵧ/Fₓ)")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【连续性方程题】")
        print("  Step 1: 计算各断面面积")
        print("  Step 2: 应用Q=A₁v₁=A₂v₂")
        print("  Step 3: 求解未知流速")
        print("  ")
        print("  【动量方程题】")
        print("  Step 1: 建立坐标系")
        print("  Step 2: 确定入口、出口速度分量")
        print("  Step 3: 应用Fₓ=ρQ(v₂ₓ-v₁ₓ)")
        print("  Step 4: 应用Fᵧ=ρQ(v₂ᵧ-v₁ᵧ)")
        print("  Step 5: 计算合力F=√(Fₓ²+Fᵧ²)")
        print("  Step 6: 确定力的方向")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：连续性方程用质量流量（应该用体积流量）")
        print("  ❌ 错误2：动量方程忘记分解速度矢量")
        print("  ❌ 错误3：力的方向判断错误")
        print("  ❌ 错误4：作用力与反作用力搞混")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：连续性方程：A↓→v↑")
        print("  ✓ 技巧2：动量方程一定要画坐标系")
        print("  ✓ 技巧3：速度矢量要分解")
        print("  ✓ 技巧4：力的方向看Fₓ、Fᵧ的正负")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能熟练应用连续性方程")
        print("  □ 理解质量守恒原理")
        print("  □ 能列动量方程分量形式")
        print("  □ 能正确判断力的方向")
        
        print("\n📅 明日预告：Day 6 - 孔口管嘴出流")
        print("  预习内容：流量系数，收缩系数")
        
        print("\n💪 今日格言：")
        print("  「动量方程是考研重点！掌握矢量分解=拿到18分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 5: 连续性与动量方程")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day5 = Day5ContinuityMomentum()
    
    # 例题1：连续性方程
    result1 = day5.example_1_continuity()
    
    # 例题2：动量方程
    result2 = day5.example_2_momentum()
    
    # 每日总结
    day5.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 5 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握连续性方程")
    print(f"  ✓ 掌握动量方程")
    print(f"  ✓ 理解弯管受力")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n明日继续：Day 6 - 孔口管嘴出流")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
