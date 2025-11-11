#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 3: 闸门启闭力
Sprint Day 3: Gate Opening/Closing Force

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 力矩平衡方程：∑M = 0
  2. 铰链支点位置确定
  3. 启闭力计算：F·L = P·e

🎯 学习目标：
  - 掌握力矩平衡方法
  - 熟练计算启闭力
  - 理解铰链支点作用

💪 今日格言：力矩平衡是关键！掌握方法=拿到18分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day3GateForce:
    """
    Day 3：闸门启闭力
    
    包含2个核心例题：
    1. 基础题：矩形平板闸门启闭力
    2. 强化题：铰链闸门启闭力
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        
    def example_1_simple_gate(self):
        """
        例题1：矩形平板闸门启闭力（基础题）⭐⭐⭐⭐⭐
        
        题目：矩形平板闸门，宽b=2m，高h=3m，垂直放置
              门顶在水面下d=1m，启闭力作用在闸门顶部
        求：(1) 静水总压力P
            (2) 压力作用点位置
            (3) 启闭力F
        
        考点：静水压力，力矩平衡
        难度：基础（必考！）
        时间：20分钟
        分值：18分
        """
        print("\n" + "="*60)
        print("例题1：矩形平板闸门启闭力（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 2.0      # 闸门宽度 (m)
        h = 3.0      # 闸门高度 (m)
        d = 1.0      # 门顶淹没深度 (m)
        
        print(f"\n已知条件：")
        print(f"  矩形闸门宽度 b = {b:.1f} m")
        print(f"  闸门高度 h = {h:.1f} m")
        print(f"  门顶淹没深度 d = {d:.1f} m")
        print(f"  启闭力作用点：闸门顶部")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 计算静水总压力
        print(f"\n(1) 计算静水总压力P：")
        print(f"    闸门面积：A = b × h = {b} × {h} = {b*h:.1f} m²")
        
        A = b * h
        
        print(f"    形心淹没深度：")
        print(f"    hc = d + h/2 = {d} + {h}/2 = {d + h/2:.1f} m")
        
        hc = d + h/2
        
        print(f"    ")
        print(f"    静水总压力公式：")
        print(f"    P = ρg·hc·A")
        
        P = self.rho * self.g * hc * A
        
        print(f"      = {self.rho} × {self.g:.2f} × {hc:.1f} × {A:.1f}")
        print(f"      = {P:.2f} N")
        print(f"      = {P/1000:.2f} kN ✓")
        
        # (2) 压力作用点
        print(f"\n(2) 计算压力作用点位置：")
        print(f"    ")
        print(f"    矩形闸门惯性矩：")
        print(f"    Ic = bh³/12 = {b}×{h}³/12 = {b*h**3/12:.3f} m⁴")
        
        Ic = b * h**3 / 12
        
        print(f"    ")
        print(f"    压心位置公式（从形心向下）：")
        print(f"    e = Ic/(hc·A)")
        
        e = Ic / (hc * A)
        
        print(f"      = {Ic:.3f}/({hc:.1f}×{A:.1f})")
        print(f"      = {e:.4f} m")
        print(f"    ")
        print(f"    压心从水面算起：")
        print(f"    yD = hc + e")
        
        yD = hc + e
        
        print(f"       = {hc:.1f} + {e:.4f}")
        print(f"       = {yD:.4f} m ✓")
        
        # 压心到闸门顶部距离
        yD_from_top = yD - d
        print(f"    ")
        print(f"    压心到闸门顶部距离：")
        print(f"    yD' = yD - d = {yD:.4f} - {d} = {yD_from_top:.4f} m")
        
        # (3) 启闭力计算
        print(f"\n(3) 计算启闭力F（力矩平衡法）：")
        print(f"    ")
        print(f"    以闸门底部为支点，力矩平衡：")
        print(f"    F × h = P × (h - yD')")
        print(f"    ")
        
        # 压力到闸门底部距离
        yD_from_bottom = h - yD_from_top
        
        print(f"    压力作用点到底部距离：")
        print(f"    h - yD' = {h} - {yD_from_top:.4f} = {yD_from_bottom:.4f} m")
        print(f"    ")
        print(f"    启闭力：")
        print(f"    F = P × (h - yD') / h")
        
        F = P * yD_from_bottom / h
        
        print(f"      = {P:.2f} × {yD_from_bottom:.4f} / {h}")
        print(f"      = {F:.2f} N")
        print(f"      = {F/1000:.2f} kN ✓")
        
        # 验算：力矩平衡
        M_F = F * h
        M_P = P * yD_from_bottom
        
        print(f"    ")
        print(f"    验算力矩平衡：")
        print(f"    M_F = F × h = {F:.2f} × {h} = {M_F:.2f} N·m")
        print(f"    M_P = P × (h-yD') = {P:.2f} × {yD_from_bottom:.4f} = {M_P:.2f} N·m")
        print(f"    误差 = |M_F - M_P| = {abs(M_F - M_P):.2f} N·m ≈ 0 ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：闸门受力示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 闸门（垂直）
        gate_x = [0, 0.2, 0.2, 0]
        gate_y = [0, 0, h, h]
        ax1.fill(gate_x, gate_y, color='gray', alpha=0.7, edgecolor='black', linewidth=2)
        ax1.plot([0.1, 0.1], [0, h], 'k-', linewidth=3)
        
        # 水面
        water_level = d + h
        ax1.fill_between([-1, 0], d, water_level, alpha=0.3, color='blue')
        ax1.plot([-1, 0], [water_level, water_level], 'b-', linewidth=2, label='水面')
        ax1.plot([-1, 0], [d, d], 'b--', linewidth=1)
        
        # 标注尺寸
        ax1.plot([-0.8, -0.8], [d, water_level], 'r-', linewidth=2)
        ax1.text(-1.0, (d+water_level)/2, f'd={d}m', fontsize=11, color='red', 
                rotation=90, va='center')
        
        ax1.plot([0.3, 0.3], [0, h], 'g-', linewidth=2)
        ax1.text(0.5, h/2, f'h={h}m', fontsize=11, color='green', 
                rotation=90, va='center')
        
        # 压力箭头（从压心指向闸门）
        P_start_x = -0.5
        P_y = d + yD_from_top
        ax1.arrow(P_start_x, P_y, 0.4, 0, head_width=0.15, head_length=0.1,
                 fc='red', ec='red', linewidth=3)
        ax1.text(P_start_x-0.3, P_y+0.2, f'P={P/1000:.1f}kN', 
                fontsize=11, color='red', fontweight='bold')
        
        # 压心标注
        ax1.plot(0, P_y, 'ro', markersize=10)
        ax1.text(0.25, P_y, f'压心\nyD\'={yD_from_top:.2f}m', 
                fontsize=9, color='red')
        
        # 启闭力箭头（向上）
        F_x = 0.1
        F_y_top = h
        ax1.arrow(F_x, F_y_top, 0, 0.5, head_width=0.08, head_length=0.1,
                 fc='blue', ec='blue', linewidth=3)
        ax1.text(F_x+0.2, F_y_top+0.3, f'F={F/1000:.1f}kN\n(启闭力)', 
                fontsize=11, color='blue', fontweight='bold')
        
        # 支点（底部）
        triangle = Polygon([[0.05, -0.2], [0.15, -0.2], [0.1, 0]], 
                          closed=True, facecolor='black', edgecolor='black')
        ax1.add_patch(triangle)
        ax1.text(0.1, -0.4, '支点', fontsize=10, ha='center', fontweight='bold')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 3 例题1：矩形闸门受力示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1.5, 1])
        ax1.set_ylim([-0.5, 5])
        ax1.set_aspect('equal')
        
        # 子图2：力矩分析
        ax2 = plt.subplot(2, 2, 2)
        
        # 力臂示意
        ax2.plot([0, 0], [0, h], 'k-', linewidth=3, label='闸门')
        
        # 支点
        ax2.plot(0, 0, 'ko', markersize=15, label='支点（底部）')
        
        # 压力作用点
        ax2.plot(0, yD_from_bottom, 'ro', markersize=12, label='压力作用点')
        
        # 启闭力作用点
        ax2.plot(0, h, 'bs', markersize=12, label='启闭力作用点')
        
        # 力臂标注
        ax2.plot([0.1, 0.5], [0, 0], 'k-', linewidth=1)
        ax2.plot([0.1, 0.5], [yD_from_bottom, yD_from_bottom], 'r-', linewidth=1)
        ax2.annotate('', xy=(0.3, 0), xytext=(0.3, yD_from_bottom),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax2.text(0.6, yD_from_bottom/2, f'L_P={yD_from_bottom:.2f}m', 
                fontsize=11, color='red', fontweight='bold')
        
        ax2.plot([0.1, 0.5], [h, h], 'b-', linewidth=1)
        ax2.annotate('', xy=(0.3, yD_from_bottom), xytext=(0.3, h),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax2.text(0.6, (yD_from_bottom+h)/2, f'L_F={h:.1f}m', 
                fontsize=11, color='blue', fontweight='bold')
        
        # 力矩公式
        formula_text = f"""
        力矩平衡方程：
        
        M_F = M_P
        F × L_F = P × L_P
        F × {h:.1f} = {P/1000:.1f} × {yD_from_bottom:.2f}
        
        F = {F/1000:.2f} kN ✓
        """
        ax2.text(-0.5, h/2, formula_text, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax2.set_xlabel('水平位置', fontsize=12)
        ax2.set_ylabel('垂直位置 (m)', fontsize=12)
        ax2.set_title('力矩平衡分析', fontsize=13, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-1, 1.5])
        ax2.set_ylim([-0.5, h+0.5])
        
        # 子图3：压力分布
        ax3 = plt.subplot(2, 2, 3)
        
        # 压力分布（线性）
        y_range = np.linspace(d, d+h, 50)
        p_range = self.rho * self.g * y_range / 1000  # kPa
        
        ax3.fill_betweenx(y_range-d, 0, p_range, alpha=0.3, color='lightblue', 
                         edgecolor='blue', linewidth=2, label='压力分布')
        
        # 形心位置
        ax3.axhline(y=yD_from_top, color='red', linestyle='--', linewidth=2, 
                   label=f'压心 yD\'={yD_from_top:.2f}m')
        
        # 合力位置标注
        p_at_yD = self.rho * self.g * (d + yD_from_top) / 1000
        ax3.plot(p_at_yD, yD_from_top, 'ro', markersize=10)
        ax3.arrow(p_at_yD, yD_from_top, p_at_yD*0.3, 0, 
                 head_width=0.1, head_length=p_at_yD*0.1,
                 fc='red', ec='red', linewidth=2)
        ax3.text(p_at_yD*1.5, yD_from_top+0.2, f'P={P/1000:.1f}kN', 
                fontsize=10, color='red')
        
        ax3.set_xlabel('压强 (kPa)', fontsize=12)
        ax3.set_ylabel('从闸门顶部距离 (m)', fontsize=12)
        ax3.set_title('压力分布图', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim([0, h])
        ax3.invert_yaxis()  # 顶部为0
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          • 闸门宽度 b = {b:.1f} m
          • 闸门高度 h = {h:.1f} m
          • 门顶淹没深度 d = {d:.1f} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 静水总压力：
            A = b×h = {A:.1f} m²
            hc = d+h/2 = {hc:.1f} m
            P = ρg·hc·A = {P/1000:.2f} kN ✓
        
        (2) 压心位置：
            Ic = bh³/12 = {Ic:.3f} m⁴
            e = Ic/(hc·A) = {e:.4f} m
            yD = hc+e = {yD:.4f} m
            yD' = yD-d = {yD_from_top:.4f} m ✓
        
        (3) 启闭力：
            F = P×(h-yD')/h
              = {P/1000:.2f}×{yD_from_bottom:.4f}/{h}
              = {F/1000:.2f} kN ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          P = ρg·hc·A
          e = Ic/(hc·A)
          F = P×L_P/L_F (力矩平衡)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day03_gate_force/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（18分评分标准）：")
        print("="*60)
        print("✓ (1) 计算闸门面积A (1分)")
        print("✓ (2) 计算形心淹没深度hc (1分)")
        print("✓ (3) 应用公式P=ρg·hc·A (3分) ⭐")
        print("✓ (4) 计算惯性矩Ic=bh³/12 (2分)")
        print("✓ (5) 计算偏心距e=Ic/(hc·A) (2分)")
        print("✓ (6) 确定压心位置yD (2分)")
        print("✓ (7) 列力矩平衡方程 (3分) ⭐")
        print("✓ (8) 计算启闭力F (3分)")
        print("✓ (9) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 形心深度：hc = d + h/2，不是h/2！")
        print("  ⚠️ 压心位置：从形心向下e，不是向上！")
        print("  ⚠️ 力矩平衡：注意力臂计算")
        print("  ⚠️ 启闭力方向：向上拉")
        
        return {'P': P, 'yD': yD, 'F': F, 'yD_from_top': yD_from_top}
    
    def example_2_hinged_gate(self):
        """
        例题2：铰链闸门启闭力（强化题）⭐⭐⭐⭐⭐
        
        题目：矩形闸门，b=3m，h=2m，铰链在闸门底部
              门顶在水面，启闭力作用在闸门顶部
        求：(1) 静水总压力P
            (2) 启闭力F
            (3) 铰链支反力R
        
        考点：铰链闸门，三力平衡
        难度：强化（必考！）
        时间：25分钟
        分值：20分
        """
        print("\n" + "="*60)
        print("例题2：铰链闸门启闭力（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 3.0      # 闸门宽度 (m)
        h = 2.0      # 闸门高度 (m)
        
        print(f"\n已知条件：")
        print(f"  矩形闸门宽度 b = {b:.1f} m")
        print(f"  闸门高度 h = {h:.1f} m")
        print(f"  门顶在水面")
        print(f"  铰链位置：闸门底部")
        print(f"  启闭力作用点：闸门顶部")
        
        # (1) 静水总压力
        print(f"\n解题步骤：")
        print(f"\n(1) 计算静水总压力P：")
        
        A = b * h
        hc = h / 2
        
        print(f"    A = b×h = {b}×{h} = {A:.1f} m²")
        print(f"    hc = h/2 = {h}/2 = {hc:.1f} m")
        print(f"    P = ρg·hc·A")
        
        P = self.rho * self.g * hc * A
        
        print(f"      = {self.rho}×{self.g:.2f}×{hc:.1f}×{A:.1f}")
        print(f"      = {P:.2f} N = {P/1000:.2f} kN ✓")
        
        # 压心位置
        Ic = b * h**3 / 12
        e = Ic / (hc * A)
        yD = hc + e
        
        print(f"    ")
        print(f"    压心位置（从水面算）：")
        print(f"    Ic = bh³/12 = {Ic:.3f} m⁴")
        print(f"    e = Ic/(hc·A) = {e:.4f} m")
        print(f"    yD = hc+e = {yD:.4f} m")
        
        # 从铰链到压心的距离
        L_P = h - yD
        
        print(f"    ")
        print(f"    压心到铰链距离：")
        print(f"    L_P = h - yD = {h} - {yD:.4f} = {L_P:.4f} m")
        
        # (2) 启闭力
        print(f"\n(2) 计算启闭力F（以铰链为支点）：")
        print(f"    ")
        print(f"    力矩平衡方程（以铰链为支点）：")
        print(f"    F × h = P × L_P")
        print(f"    ")
        
        F = P * L_P / h
        
        print(f"    F = P × L_P / h")
        print(f"      = {P:.2f} × {L_P:.4f} / {h}")
        print(f"      = {F:.2f} N = {F/1000:.2f} kN ✓")
        
        # (3) 铰链支反力
        print(f"\n(3) 计算铰链支反力R：")
        print(f"    ")
        print(f"    竖直方向力平衡：")
        print(f"    R = F + P")
        
        R = F + P
        
        print(f"      = {F:.2f} + {P:.2f}")
        print(f"      = {R:.2f} N = {R/1000:.2f} kN ✓")
        
        print(f"    ")
        print(f"    说明：R指向铰链，支撑整个系统")
        
        # 绘图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 子图1：铰链闸门示意图
        # 闸门（倾斜，简化为垂直）
        gate_x = [0, 0.15, 0.15, 0]
        gate_y = [0, 0, h, h]
        ax1.fill(gate_x, gate_y, color='gray', alpha=0.7, edgecolor='black', linewidth=2)
        
        # 水面
        ax1.fill_between([-1, 0], 0, h, alpha=0.3, color='blue')
        ax1.plot([-1, 0], [h, h], 'b-', linewidth=2, label='水面')
        
        # 铰链（底部）
        circle = Circle((0.075, 0), 0.08, facecolor='yellow', edgecolor='black', linewidth=2)
        ax1.add_patch(circle)
        ax1.text(0.3, 0, '铰链', fontsize=11, fontweight='bold', 
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 压力箭头
        P_start_x = -0.6
        P_y = yD
        ax1.arrow(P_start_x, P_y, 0.5, 0, head_width=0.12, head_length=0.1,
                 fc='red', ec='red', linewidth=3)
        ax1.text(P_start_x-0.2, P_y+0.15, f'P={P/1000:.1f}kN', 
                fontsize=11, color='red', fontweight='bold')
        ax1.plot(0.075, P_y, 'ro', markersize=10)
        ax1.text(0.25, P_y, f'压心\n{yD:.2f}m', fontsize=9, color='red')
        
        # 启闭力箭头（向上）
        F_x = 0.075
        ax1.arrow(F_x, h, 0, 0.4, head_width=0.08, head_length=0.08,
                 fc='blue', ec='blue', linewidth=3)
        ax1.text(F_x+0.2, h+0.25, f'F={F/1000:.1f}kN', 
                fontsize=11, color='blue', fontweight='bold')
        
        # 铰链支反力（向下）
        ax1.arrow(F_x, 0, 0, -0.4, head_width=0.08, head_length=0.08,
                 fc='green', ec='green', linewidth=3)
        ax1.text(F_x+0.2, -0.25, f'R={R/1000:.1f}kN', 
                fontsize=11, color='green', fontweight='bold')
        
        # 尺寸标注
        ax1.plot([0.25, 0.25], [0, h], 'k-', linewidth=1)
        ax1.text(0.4, h/2, f'h={h}m', fontsize=11, rotation=90, va='center')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 3 例题2：铰链闸门受力示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1.2, 0.8])
        ax1.set_ylim([-0.6, 3])
        ax1.set_aspect('equal')
        
        # 子图2：力矩分析
        categories = ['启闭力F', '静水压力P', '铰链反力R']
        forces = [F/1000, P/1000, R/1000]
        colors_bar = ['#4ECDC4', '#FF6B6B', '#95E1D3']
        
        bars = ax2.bar(categories, forces, color=colors_bar, edgecolor='black', linewidth=2)
        
        for bar, force in zip(bars, forces):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{force:.2f}\nkN', ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('力 (kN)', fontsize=12)
        ax2.set_title('三力大小对比', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 子图3：力矩平衡图解
        ax3.plot([0, 0], [0, h], 'k-', linewidth=4, label='闸门')
        
        # 铰链
        ax3.plot(0, 0, 'yo', markersize=20, label='铰链（支点）')
        
        # 压力作用点
        ax3.plot(0, yD, 'ro', markersize=15, label='压心')
        ax3.arrow(-0.3, yD, 0.25, 0, head_width=0.08, head_length=0.05,
                 fc='red', ec='red', linewidth=2)
        
        # 启闭力作用点
        ax3.plot(0, h, 'bs', markersize=15, label='启闭力作用点')
        ax3.arrow(0, h, 0, 0.3, head_width=0.08, head_length=0.05,
                 fc='blue', ec='blue', linewidth=2)
        
        # 力臂标注
        ax3.plot([0.15, 0.4], [0, 0], 'k-', linewidth=1)
        ax3.plot([0.15, 0.4], [yD, yD], 'r-', linewidth=1)
        ax3.annotate('', xy=(0.25, 0), xytext=(0.25, yD),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax3.text(0.5, yD/2, f'L_P={L_P:.2f}m', fontsize=11, color='red', fontweight='bold')
        
        ax3.plot([0.15, 0.4], [h, h], 'b-', linewidth=1)
        ax3.annotate('', xy=(0.25, yD), xytext=(0.25, h),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax3.text(0.5, (yD+h)/2, f'L_F={h}m', fontsize=11, color='blue', fontweight='bold')
        
        # 力矩公式
        formula_text = f"""
        以铰链为支点：
        
        ∑M = 0
        F × {h} = P × {L_P:.2f}
        
        F = {F/1000:.2f} kN ✓
        
        竖直力平衡：
        R = F + P = {R/1000:.2f} kN ✓
        """
        ax3.text(-0.6, h/2, formula_text, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax3.set_xlabel('水平位置', fontsize=12)
        ax3.set_ylabel('垂直位置 (m)', fontsize=12)
        ax3.set_title('力矩平衡分析', fontsize=13, fontweight='bold')
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([-0.8, 0.8])
        ax3.set_ylim([-0.3, h+0.5])
        
        # 子图4：与例题1对比
        ax4.axis('off')
        
        comparison_text = """
        【两种闸门对比】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        例题1：底部支点闸门
          • 支点：闸门底部（固定）
          • 启闭力：顶部向上拉
          • 特点：启闭力较小
        
        例题2：铰链闸门
          • 支点：铰链（底部）
          • 启闭力：顶部向上拉
          • 特点：有铰链支反力R
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
        
        1. 静水总压力：
           P = ρg·hc·A
        
        2. 压心偏心距：
           e = Ic/(hc·A)
        
        3. 力矩平衡：
           F × L_F = P × L_P
        
        4. 铰链支反力：
           R = F + P (竖直方向)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        解题技巧：
          ✓ 先算P和压心位置
          ✓ 确定支点位置
          ✓ 列力矩平衡方程
          ✓ 求解启闭力F
          ✓ 力平衡求支反力R
        """
        
        ax4.text(0.05, 0.95, comparison_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day03_gate_force/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（20分评分标准）：")
        print("="*60)
        print("✓ (1) 计算静水总压力P (3分)")
        print("✓ (2) 计算压心位置yD (3分)")
        print("✓ (3) 确定铰链位置（支点）(1分)")
        print("✓ (4) 确定力臂L_P和L_F (2分)")
        print("✓ (5) 列力矩平衡方程 ∑M=0 (4分) ⭐⭐")
        print("✓ (6) 求解启闭力F (3分)")
        print("✓ (7) 列竖直力平衡方程 (2分)")
        print("✓ (8) 求解铰链支反力R (1分)")
        print("✓ (9) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 铰链位置：支点在铰链，不是底部！")
        print("  ⚠️ 力臂：从铰链到力作用点的距离")
        print("  ⚠️ 支反力方向：铰链承受压力，向下")
        print("  ⚠️ 三力平衡：F + P = R（竖直方向）")
        
        return {'P': P, 'F': F, 'R': R, 'yD': yD, 'L_P': L_P}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 3 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 静水总压力：")
        print("     P = ρg·hc·A")
        print("     ")
        print("  2. 压心偏心距：")
        print("     e = Ic/(hc·A)")
        print("     其中 Ic = bh³/12 (矩形)")
        print("     ")
        print("  3. 力矩平衡方程：")
        print("     ∑M = 0")
        print("     F × L_F = P × L_P")
        print("     ")
        print("  4. 启闭力：")
        print("     F = P × L_P / L_F")
        print("     ")
        print("  5. 铰链支反力：")
        print("     R = F + P (竖直方向)")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【闸门启闭力题】")
        print("  Step 1: 计算静水总压力P")
        print("  Step 2: 计算压心位置yD")
        print("  Step 3: 确定支点位置")
        print("  Step 4: 确定各力的力臂")
        print("  Step 5: 列力矩平衡方程")
        print("  Step 6: 求解启闭力F")
        print("  Step 7: (若有铰链)求支反力R")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：形心深度算错（忘记加d）")
        print("  ❌ 错误2：压心位置算错（向下不是向上）")
        print("  ❌ 错误3：力臂搞错（到支点的距离）")
        print("  ❌ 错误4：力矩方向搞混")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：一定要画受力图！")
        print("  ✓ 技巧2：标清楚支点位置")
        print("  ✓ 技巧3：力臂用虚线标注")
        print("  ✓ 技巧4：先算P，再算F")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能正确计算压心位置")
        print("  □ 能列出力矩平衡方程")
        print("  □ 理解铰链支反力")
        print("  □ 能区分不同支点类型")
        
        print("\n📅 明日预告：Day 4 - 伯努利方程基础")
        print("  预习内容：能量方程，总水头线")
        
        print("\n💪 今日格言：")
        print("  「力矩平衡是关键！画好受力图=拿到18分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 3: 闸门启闭力")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day3 = Day3GateForce()
    
    # 例题1：简单闸门
    result1 = day3.example_1_simple_gate()
    
    # 例题2：铰链闸门
    result2 = day3.example_2_hinged_gate()
    
    # 每日总结
    day3.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 3 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握力矩平衡方法")
    print(f"  ✓ 掌握启闭力计算")
    print(f"  ✓ 理解铰链支反力")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n明日继续：Day 4 - 伯努利方程基础")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
