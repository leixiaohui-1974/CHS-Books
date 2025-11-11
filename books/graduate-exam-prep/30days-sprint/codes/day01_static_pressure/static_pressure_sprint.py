#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 1: 静水压强与总压力
Sprint Day 1: Hydrostatic Pressure and Total Pressure

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 静水压强分布规律: p = ρgh
  2. 平面总压力计算: P = ρghcA
  3. 压力中心位置: yp = yc + Ic/(ycA)

🎯 学习目标：
  - 掌握静水压强基本公式
  - 熟练计算平面总压力
  - 理解压力中心物理意义

💪 今日格言：千里之行，始于足下！第一天，你能行！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day1StaticPressure:
    """
    Day 1：静水压强与总压力
    
    包含3个核心例题：
    1. 基础题：矩形闸门总压力
    2. 强化题：倾斜矩形闸门
    3. 综合题：梯形闸门
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水的密度 (kg/m³)
        
    def example_1_vertical_gate(self):
        """
        例题1：竖直矩形闸门总压力（基础题）⭐⭐⭐
        
        题目：矩形闸门，宽b=2m，高h=3m，水深H=4m
        求：(1) 闸门所受总压力
            (2) 压力中心位置
            (3) 绘制压强分布图
        
        考点：基本公式应用
        难度：基础
        时间：15分钟
        分值：10分
        """
        print("\n" + "="*60)
        print("例题1：竖直矩形闸门总压力（基础题）⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 2.0  # 闸门宽度 (m)
        h_gate = 3.0  # 闸门高度 (m)
        H = 4.0  # 水深 (m)
        
        print(f"\n已知条件：")
        print(f"  闸门宽度 b = {b:.1f} m")
        print(f"  闸门高度 h = {h_gate:.1f} m")
        print(f"  水深 H = {H:.1f} m")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # 1. 确定作用面积
        A = b * h_gate
        print(f"\n(1) 作用面积：")
        print(f"    A = b × h = {b} × {h_gate} = {A:.2f} m²")
        
        # 2. 计算形心深度（闸门顶部距水面1m）
        y_top = H - h_gate  # 闸门顶部深度
        y_center = y_top + h_gate/2  # 形心深度
        print(f"\n(2) 形心深度：")
        print(f"    闸门顶部深度 = {y_top:.2f} m")
        print(f"    形心深度 yc = {y_top:.2f} + {h_gate/2:.2f} = {y_center:.2f} m")
        
        # 3. 计算总压力
        P = self.rho * self.g * y_center * A
        print(f"\n(3) 总压力：")
        print(f"    P = ρghcA")
        print(f"      = {self.rho} × {self.g:.2f} × {y_center:.2f} × {A:.2f}")
        print(f"      = {P:.2f} N")
        print(f"      = {P/1000:.2f} kN ✓")
        
        # 4. 计算压力中心
        I_c = (b * h_gate**3) / 12  # 对通过形心轴的惯性矩
        y_p = y_center + I_c / (y_center * A)
        print(f"\n(4) 压力中心：")
        print(f"    Ic = bh³/12 = {b} × {h_gate}³/12 = {I_c:.4f} m⁴")
        print(f"    yp = yc + Ic/(ycA)")
        print(f"       = {y_center:.2f} + {I_c:.4f}/({y_center:.2f} × {A:.2f})")
        print(f"       = {y_p:.3f} m ✓")
        print(f"    距水面深度 = {y_p:.3f} m")
        print(f"    距闸门顶部 = {y_p - y_top:.3f} m")
        
        # 5. 绘制压强分布图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 子图1：闸门示意图
        z = np.linspace(0, H, 100)
        p = self.rho * self.g * z / 1000  # 压强 (kPa)
        
        ax1.fill_betweenx([y_top, H], 0, [0, 0], alpha=0.3, color='lightblue', label='水体')
        ax1.plot(p, z, 'b-', linewidth=2, label='压强分布')
        
        # 标注闸门
        ax1.fill_betweenx([y_top, H], -2, [0, 0], alpha=0.5, color='gray', label='闸门')
        ax1.plot([-2, -2], [y_top, H], 'k-', linewidth=3)
        
        # 标注关键点
        ax1.plot(self.rho*self.g*y_center/1000, y_center, 'ro', markersize=10, label=f'形心 (深度={y_center:.2f}m)')
        ax1.plot(self.rho*self.g*y_p/1000, y_p, 'g^', markersize=10, label=f'压力中心 (深度={y_p:.3f}m)')
        
        ax1.axhline(y=y_top, color='k', linestyle='--', alpha=0.5)
        ax1.axhline(y=H, color='k', linestyle='--', alpha=0.5)
        ax1.axhline(y=y_center, color='r', linestyle=':', alpha=0.5)
        ax1.axhline(y=y_p, color='g', linestyle=':', alpha=0.5)
        
        ax1.set_xlabel('压强 p (kPa)', fontsize=12)
        ax1.set_ylabel('水深 z (m)', fontsize=12)
        ax1.set_title('Day 1 例题1：竖直矩形闸门\n压强分布与总压力', fontsize=13, fontweight='bold')
        ax1.legend(loc='lower right')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([0, H*1.1])
        ax1.invert_yaxis()  # 反转y轴，水深向下增加
        
        # 子图2：总压力矢量图
        ax2.fill([0, b, b, 0], [y_top, y_top, H, H], alpha=0.3, color='lightblue', edgecolor='blue', linewidth=2)
        ax2.plot([0, b, b, 0, 0], [y_top, y_top, H, H, y_top], 'b-', linewidth=3)
        
        # 绘制总压力矢量
        arrow_scale = 0.3
        ax2.arrow(b/2, y_p, P/1e6 * arrow_scale, 0, 
                 head_width=0.2, head_length=0.1, fc='red', ec='red', linewidth=2)
        ax2.text(b/2 + P/1e6 * arrow_scale + 0.15, y_p, 
                f'P = {P/1000:.1f} kN', fontsize=11, color='red', fontweight='bold')
        
        # 标注
        ax2.plot(b/2, y_center, 'ro', markersize=10, label='形心')
        ax2.plot(b/2, y_p, 'g^', markersize=10, label='压力中心')
        ax2.text(-0.3, y_center, f'yc={y_center:.2f}m', fontsize=10)
        ax2.text(-0.3, y_p, f'yp={y_p:.3f}m', fontsize=10, color='green')
        
        # 标注尺寸
        ax2.plot([b+0.2, b+0.2], [y_top, H], 'k-', linewidth=1)
        ax2.plot([b+0.15, b+0.25], [y_top, y_top], 'k-', linewidth=1)
        ax2.plot([b+0.15, b+0.25], [H, H], 'k-', linewidth=1)
        ax2.text(b+0.35, (y_top+H)/2, f'h={h_gate}m', fontsize=10)
        
        ax2.set_xlabel('宽度 x (m)', fontsize=12)
        ax2.set_ylabel('深度 z (m)', fontsize=12)
        ax2.set_title('总压力作用位置', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-0.5, b+1])
        ax2.set_ylim([0, H*1.1])
        ax2.invert_yaxis()
        ax2.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day01_static_pressure/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点总结
        print("\n" + "="*60)
        print("📝 答题要点（10分评分标准）：")
        print("="*60)
        print("✓ (1) 确定作用面积 A = bh (2分)")
        print("✓ (2) 计算形心深度 yc (2分)")
        print("✓ (3) 应用公式 P = ρghcA (3分)")
        print("✓ (4) 计算压力中心 yp = yc + Ic/(ycA) (2分)")
        print("✓ (5) 单位正确，结果合理 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 形心深度要从水面算起，不是从闸门顶部")
        print("  ⚠️ 压力中心总是低于形心（yp > yc）")
        print("  ⚠️ 单位统一：压力N或kN，长度m")
        
        return {'P': P, 'y_p': y_p, 'y_center': y_center}
    
    def example_2_inclined_gate(self):
        """
        例题2：倾斜矩形闸门总压力（强化题）⭐⭐⭐⭐
        
        题目：矩形闸门倾角α=60°，宽b=1.5m，沿斜面长度L=2m，
             闸门顶部距水面1m
        求：(1) 总压力
            (2) 压力中心沿斜面的距离
        
        考点：倾斜平面总压力
        难度：强化
        时间：20分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题2：倾斜矩形闸门总压力（强化题）⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        alpha = 60  # 倾角 (度)
        alpha_rad = np.radians(alpha)
        b = 1.5  # 闸门宽度 (m)
        L = 2.0  # 沿斜面长度 (m)
        h_top = 1.0  # 顶部距水面垂直距离 (m)
        
        print(f"\n已知条件：")
        print(f"  倾角 α = {alpha}°")
        print(f"  闸门宽度 b = {b:.1f} m")
        print(f"  沿斜面长度 L = {L:.1f} m")
        print(f"  顶部距水面 = {h_top:.1f} m")
        
        # 计算
        print(f"\n解题步骤：")
        
        # 1. 作用面积
        A = b * L
        print(f"\n(1) 作用面积：")
        print(f"    A = b × L = {b} × {L} = {A:.2f} m²")
        
        # 2. 形心深度（垂直深度）
        h_bottom = h_top + L * np.sin(alpha_rad)
        h_center = h_top + (L/2) * np.sin(alpha_rad)
        print(f"\n(2) 形心深度（垂直深度）：")
        print(f"    闸门底部深度 = {h_top} + {L}×sin({alpha}°)")
        print(f"                 = {h_bottom:.3f} m")
        print(f"    形心深度 hc = {h_top} + ({L}/2)×sin({alpha}°)")
        print(f"                = {h_center:.3f} m ✓")
        
        # 3. 总压力
        P = self.rho * self.g * h_center * A
        print(f"\n(3) 总压力：")
        print(f"    P = ρghcA")
        print(f"      = {self.rho} × {self.g:.2f} × {h_center:.3f} × {A:.2f}")
        print(f"      = {P:.2f} N")
        print(f"      = {P/1000:.2f} kN ✓")
        
        # 4. 压力中心位置
        # 沿斜面方向的坐标
        s_c = L/2  # 形心沿斜面距顶部的距离
        I_c = (b * L**3) / 12  # 对形心轴的惯性矩
        
        # 压力中心沿斜面距顶部的距离
        s_p = s_c + (I_c * np.sin(alpha_rad)) / (h_center * A)
        
        print(f"\n(4) 压力中心位置：")
        print(f"    形心沿斜面距顶部 sc = L/2 = {s_c:.2f} m")
        print(f"    Ic = bL³/12 = {I_c:.4f} m⁴")
        print(f"    sp = sc + (Ic×sinα)/(hc×A)")
        print(f"       = {s_c:.2f} + ({I_c:.4f}×sin{alpha}°)/({h_center:.3f}×{A:.2f})")
        print(f"       = {s_p:.3f} m ✓")
        print(f"    压力中心垂直深度 hp = {h_top} + {s_p:.3f}×sin({alpha}°)")
        h_p = h_top + s_p * np.sin(alpha_rad)
        print(f"                      = {h_p:.3f} m")
        
        # 绘图
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        # 绘制水面和闸门
        x_water = np.linspace(-1, 3, 100)
        ax.fill_between(x_water, 0, 5, alpha=0.2, color='lightblue', label='水体')
        ax.axhline(y=0, color='blue', linewidth=2, label='水面')
        
        # 闸门坐标
        x_gate_top = 0.5
        y_gate_top = -h_top
        x_gate_bottom = x_gate_top + L * np.cos(alpha_rad)
        y_gate_bottom = y_gate_top - L * np.sin(alpha_rad)
        
        # 绘制闸门
        gate_x = [x_gate_top, x_gate_bottom]
        gate_y = [y_gate_top, y_gate_bottom]
        ax.plot(gate_x, gate_y, 'k-', linewidth=5, label=f'闸门 (α={alpha}°)')
        
        # 标注关键点
        x_center = x_gate_top + s_c * np.cos(alpha_rad)
        y_center = y_gate_top - s_c * np.sin(alpha_rad)
        ax.plot(x_center, y_center, 'ro', markersize=12, label=f'形心 (深度={h_center:.2f}m)')
        
        x_p = x_gate_top + s_p * np.cos(alpha_rad)
        y_p = y_gate_top - s_p * np.sin(alpha_rad)
        ax.plot(x_p, y_p, 'g^', markersize=12, label=f'压力中心 (深度={h_p:.3f}m)')
        
        # 总压力矢量（垂直于闸门）
        arrow_length = 0.5
        dx_arrow = -arrow_length * np.sin(alpha_rad)
        dy_arrow = -arrow_length * np.cos(alpha_rad)
        ax.arrow(x_p, y_p, dx_arrow, dy_arrow, 
                head_width=0.15, head_length=0.1, fc='red', ec='red', linewidth=2)
        ax.text(x_p + dx_arrow - 0.3, y_p + dy_arrow, 
               f'P={P/1000:.1f}kN', fontsize=11, color='red', fontweight='bold')
        
        # 标注尺寸和角度
        ax.text(x_gate_top - 0.3, -0.5, f'α={alpha}°', fontsize=11)
        ax.plot([x_gate_top, x_gate_top + 0.3], [y_gate_top, y_gate_top], 'k--', linewidth=1)
        ax.plot([x_gate_top, x_gate_top], [y_gate_top, y_gate_top - 0.3], 'k--', linewidth=1)
        
        # 绘制角度弧线
        angle_arc = np.linspace(3*np.pi/2, 3*np.pi/2 - alpha_rad, 30)
        arc_r = 0.3
        ax.plot(x_gate_top + arc_r*np.cos(angle_arc), 
               y_gate_top + arc_r*np.sin(angle_arc), 'k-', linewidth=1)
        
        ax.set_xlabel('水平距离 x (m)', fontsize=12)
        ax.set_ylabel('深度 z (m)', fontsize=12)
        ax.set_title('Day 1 例题2：倾斜矩形闸门总压力', fontsize=13, fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([-0.5, 3])
        ax.set_ylim([-h_bottom*1.2, 1])
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day01_static_pressure/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 确定作用面积 A = bL (2分)")
        print("✓ (2) 计算形心垂直深度 hc = h_top + (L/2)sinα (3分) ⭐")
        print("✓ (3) 应用公式 P = ρghcA (3分)")
        print("✓ (4) 计算压力中心 sp = sc + (Ic×sinα)/(hc×A) (3分) ⭐")
        print("✓ (5) 结果合理 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 形心深度是垂直深度，不是沿斜面距离")
        print("  ⚠️ 压力中心公式要乘sinα")
        print("  ⚠️ 总压力方向：垂直于闸门面")
        
        return {'P': P, 's_p': s_p, 'h_p': h_p}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 1 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背）：")
        print("  1. 静水压强：p = ρgh = γh")
        print("  2. 平面总压力：P = ρghcA = γhcA")
        print("  3. 压力中心：")
        print("     - 竖直平面：yp = yc + Ic/(ycA)")
        print("     - 倾斜平面：sp = sc + (Ic×sinα)/(hcA)")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  Step 1: 确定作用面积A")
        print("  Step 2: 计算形心深度hc（垂直深度！）")
        print("  Step 3: 计算总压力P = ρghcA")
        print("  Step 4: 计算压力中心位置")
        print("  Step 5: 检查单位和合理性")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：形心深度算成沿斜面距离")
        print("  ❌ 错误2：忘记压力中心公式中的sinα")
        print("  ❌ 错误3：单位不统一（m, cm, mm混用）")
        print("  ❌ 错误4：压力中心位置高于形心")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：画图！画出闸门示意图，标注已知量")
        print("  ✓ 技巧2：列公式！先写公式，再代入数值")
        print("  ✓ 技巧3：单位！每步计算都标明单位")
        print("  ✓ 技巧4：检验！yp必须大于yc，P必须为正")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能默写3个核心公式")
        print("  □ 能独立完成例题1")
        print("  □ 能独立完成例题2")
        print("  □ 理解形心与压力中心的区别")
        
        print("\n📅 明日预告：Day 2 - 曲面总压力与浮力")
        print("  预习内容：压力体概念、浮力计算公式")
        
        print("\n💪 今日格言：")
        print("  「第一天完成！你已经战胜了拖延症，继续加油！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 1: 静水压强与总压力")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day1 = Day1StaticPressure()
    
    # 例题1：竖直闸门
    result1 = day1.example_1_vertical_gate()
    
    # 例题2：倾斜闸门
    result2 = day1.example_2_inclined_gate()
    
    # 每日总结
    day1.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 1 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握3个核心公式")
    print(f"  ✓ 生成2张图表")
    print(f"  ✓ 学习时间：2.5小时")
    
    print(f"\n明日继续：Day 2 - 曲面总压力与浮力")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
