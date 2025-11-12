#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 10: 明渠均匀流
Sprint Day 10: Uniform Flow in Open Channels

⏰ 学习时间：2.5小时
📚 核心考点：
  1. Manning公式：Q = (1/n)AR^(2/3)i^(1/2)
  2. 正常水深计算（迭代求解）
  3. 水力最优断面设计

🎯 学习目标：
  - 掌握Manning公式应用
  - 熟练计算正常水深
  - 理解水力最优断面

💪 今日格言：明渠均匀流是明渠水力学的基础！掌握它就掌握了50%的明渠题！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.optimize import fsolve, brentq

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day10UniformFlow:
    """
    Day 10：明渠均匀流
    
    包含3个核心例题：
    1. 基础题：矩形明渠正常水深计算
    2. 强化题：梯形明渠设计
    3. 综合题：水力最优断面
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.n = 0.025  # Manning糙率（混凝土）
        
    def example_1_rectangular(self):
        """
        例题1：矩形明渠正常水深计算（基础题）⭐⭐⭐⭐⭐
        
        题目：矩形明渠，宽b=2m，坡度i=0.001，糙率n=0.025，
             流量Q=5m³/s，求正常水深h₀
        
        考点：Manning公式应用，正常水深迭代计算
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题1：矩形明渠正常水深计算（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 2.0      # 渠宽 (m)
        i = 0.001    # 渠底坡度
        n = 0.025    # Manning糙率
        Q = 5.0      # 流量 (m³/s)
        
        print(f"\n已知条件：")
        print(f"  矩形明渠宽度 b = {b:.1f} m")
        print(f"  渠底坡度 i = {i:.4f}")
        print(f"  Manning糙率 n = {n:.3f}")
        print(f"  流量 Q = {Q:.1f} m³/s")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # Manning公式
        print(f"\n(1) Manning公式：")
        print(f"    Q = (1/n) × A × R^(2/3) × i^(1/2)")
        print(f"    ")
        print(f"    对于矩形断面：")
        print(f"    A = bh₀ = {b} × h₀")
        print(f"    χ = b + 2h₀ = {b} + 2h₀")
        print(f"    R = A/χ = bh₀/(b + 2h₀)")
        
        # 建立方程求解
        def manning_equation(h):
            """Manning方程"""
            if h <= 0:
                return 1e10
            A = b * h
            chi = b + 2*h
            R = A / chi
            Q_calc = (1/n) * A * R**(2/3) * i**0.5
            return Q_calc - Q
        
        # 初值估算
        h_guess = (Q * n / (b * i**0.5))**(3/5)
        print(f"\n(2) 初值估算（简化公式）：")
        print(f"    h₀ ≈ (Qn/(bi^0.5))^(3/5)")
        print(f"       ≈ ({Q}×{n}/({b}×{i**0.5:.4f}))^(3/5)")
        print(f"       ≈ {h_guess:.3f} m")
        
        # 迭代求解
        print(f"\n(3) 精确求解（牛顿迭代法）：")
        h0 = fsolve(manning_equation, h_guess)[0]
        print(f"    正常水深 h₀ = {h0:.4f} m ✓")
        
        # 验算
        A0 = b * h0
        chi0 = b + 2*h0
        R0 = A0 / chi0
        v0 = Q / A0
        Q_check = (1/n) * A0 * R0**(2/3) * i**0.5
        
        print(f"\n(4) 验算：")
        print(f"    过水断面积 A₀ = bh₀ = {b} × {h0:.4f} = {A0:.4f} m²")
        print(f"    湿周 χ₀ = b + 2h₀ = {b} + 2×{h0:.4f} = {chi0:.4f} m")
        print(f"    水力半径 R₀ = A₀/χ₀ = {A0:.4f}/{chi0:.4f} = {R0:.4f} m")
        print(f"    平均流速 v₀ = Q/A₀ = {Q}/{A0:.4f} = {v0:.3f} m/s")
        print(f"    ")
        print(f"    验算流量：")
        print(f"    Q = (1/n)AR^(2/3)i^(1/2)")
        print(f"      = (1/{n}) × {A0:.4f} × {R0:.4f}^(2/3) × {i}^(1/2)")
        print(f"      = {Q_check:.4f} m³/s")
        print(f"    ")
        print(f"    误差 = |{Q_check:.4f} - {Q}| = {abs(Q_check-Q):.6f} m³/s ✓")
        
        # 绘图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 子图1：断面示意图
        ax1.fill([0, b, b, 0], [0, 0, h0, h0], alpha=0.5, color='lightblue', 
                edgecolor='blue', linewidth=2, label='水体')
        ax1.plot([0, b, b, 0, 0], [0, 0, h0, h0, 0], 'b-', linewidth=3)
        
        # 标注尺寸
        ax1.plot([b/2, b/2], [0, h0], 'r--', linewidth=2)
        ax1.text(b/2+0.1, h0/2, f'h₀={h0:.3f}m', fontsize=11, color='red')
        ax1.plot([0, b], [-0.15, -0.15], 'k-', linewidth=1)
        ax1.plot([0, 0], [-0.1, -0.2], 'k-', linewidth=1)
        ax1.plot([b, b], [-0.1, -0.2], 'k-', linewidth=1)
        ax1.text(b/2, -0.3, f'b={b}m', fontsize=11, ha='center')
        
        # 标注流速
        arrow_y = h0/2
        ax1.arrow(0.3, arrow_y, 0.5, 0, head_width=0.08, head_length=0.1, 
                 fc='green', ec='green', linewidth=2)
        ax1.text(0.9, arrow_y+0.15, f'v₀={v0:.2f}m/s', fontsize=10, color='green')
        
        ax1.set_xlabel('宽度 (m)', fontsize=12)
        ax1.set_ylabel('水深 (m)', fontsize=12)
        ax1.set_title('Day 10 例题1：矩形明渠断面', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.2, b+0.5])
        ax1.set_ylim([-0.5, h0*1.3])
        ax1.set_aspect('equal')
        
        # 子图2：水深与流量关系
        h_range = np.linspace(0.1, 2.0, 100)
        Q_range = []
        for h in h_range:
            A = b * h
            chi = b + 2*h
            R = A / chi
            Q_h = (1/n) * A * R**(2/3) * i**0.5
            Q_range.append(Q_h)
        
        ax2.plot(h_range, Q_range, 'b-', linewidth=2, label='Q(h)曲线')
        ax2.axhline(y=Q, color='red', linestyle='--', linewidth=2, label=f'设计流量Q={Q}m³/s')
        ax2.axvline(x=h0, color='green', linestyle='--', linewidth=2, label=f'正常水深h₀={h0:.3f}m')
        ax2.plot(h0, Q, 'ro', markersize=10, label='工作点')
        
        ax2.set_xlabel('水深 h (m)', fontsize=12)
        ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax2.set_title('水深-流量关系曲线', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 2])
        
        # 子图3：水力半径与水深关系
        R_range = []
        for h in h_range:
            A = b * h
            chi = b + 2*h
            R = A / chi
            R_range.append(R)
        
        ax3.plot(h_range, R_range, 'purple', linewidth=2, label='R(h)曲线')
        ax3.axvline(x=h0, color='green', linestyle='--', linewidth=2, label=f'h₀={h0:.3f}m')
        ax3.plot(h0, R0, 'ro', markersize=10, label=f'R₀={R0:.3f}m')
        
        ax3.set_xlabel('水深 h (m)', fontsize=12)
        ax3.set_ylabel('水力半径 R (m)', fontsize=12)
        ax3.set_title('水力半径变化', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([0, 2])
        
        # 子图4：流速与水深关系
        v_range = []
        for h in h_range:
            A = b * h
            v = Q / A
            v_range.append(v)
        
        ax4.plot(h_range, v_range, 'orange', linewidth=2, label='v(h)曲线')
        ax4.axvline(x=h0, color='green', linestyle='--', linewidth=2, label=f'h₀={h0:.3f}m')
        ax4.plot(h0, v0, 'ro', markersize=10, label=f'v₀={v0:.2f}m/s')
        
        ax4.set_xlabel('水深 h (m)', fontsize=12)
        ax4.set_ylabel('流速 v (m/s)', fontsize=12)
        ax4.set_title('平均流速变化', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim([0, 2])
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day10_uniform_flow/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 写出Manning公式 (2分)")
        print("✓ (2) 正确表达A, χ, R (2分)")
        print("✓ (3) 建立方程 Q = (1/n)AR^(2/3)i^(1/2) (2分)")
        print("✓ (4) 迭代求解h₀（可用试算法或牛顿法） (4分) ⭐")
        print("✓ (5) 验算（计算A, R, v, Q） (1分)")
        print("✓ (6) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 水力半径R = A/χ，不是A/(b+h)！")
        print("  ⚠️ Manning公式中是i^(1/2)，不是i！")
        print("  ⚠️ 迭代初值要合理，一般h₀ ≈ 0.5~2m")
        print("  ⚠️ 最后要验算，检查Q是否满足")
        
        return {'h0': h0, 'A0': A0, 'v0': v0, 'R0': R0}
    
    def example_2_trapezoidal(self):
        """
        例题2：梯形明渠设计（强化题）⭐⭐⭐⭐
        
        题目：梯形明渠，底宽b=3m，边坡m=1.5，坡度i=0.0008，
             糙率n=0.025，要求通过流量Q=10m³/s
        求：(1) 正常水深h₀
            (2) 平均流速v₀
            (3) Froude数Fr（判断流态）
        
        考点：梯形断面Manning公式，Froude数计算
        难度：强化
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题2：梯形明渠设计（强化题）⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 3.0      # 底宽 (m)
        m = 1.5      # 边坡系数
        i = 0.0008   # 坡度
        n = 0.025    # 糙率
        Q = 10.0     # 流量 (m³/s)
        
        print(f"\n已知条件：")
        print(f"  梯形渠道底宽 b = {b:.1f} m")
        print(f"  边坡系数 m = {m:.1f}")
        print(f"  渠底坡度 i = {i:.4f}")
        print(f"  Manning糙率 n = {n:.3f}")
        print(f"  设计流量 Q = {Q:.1f} m³/s")
        
        # 计算
        print(f"\n解题步骤：")
        
        print(f"\n(1) 梯形断面几何关系：")
        print(f"    过水断面积：A = (b + mh)h")
        print(f"    湿周：χ = b + 2h√(1 + m²)")
        print(f"    水力半径：R = A/χ")
        
        # Manning方程
        def manning_trap(h):
            """梯形断面Manning方程"""
            if h <= 0:
                return 1e10
            A = (b + m*h) * h
            chi = b + 2*h*np.sqrt(1 + m**2)
            R = A / chi
            Q_calc = (1/n) * A * R**(2/3) * i**0.5
            return Q_calc - Q
        
        # 求解
        print(f"\n(2) 求正常水深：")
        h_guess = 1.5
        h0 = fsolve(manning_trap, h_guess)[0]
        print(f"    h₀ = {h0:.4f} m ✓")
        
        # 计算其他参数
        A0 = (b + m*h0) * h0
        chi0 = b + 2*h0*np.sqrt(1 + m**2)
        R0 = A0 / chi0
        v0 = Q / A0
        B0 = b + 2*m*h0  # 水面宽度
        
        print(f"\n(3) 计算几何参数：")
        print(f"    A₀ = (b + mh₀)h₀ = ({b} + {m}×{h0:.4f})×{h0:.4f}")
        print(f"       = {A0:.4f} m²")
        print(f"    χ₀ = b + 2h₀√(1+m²) = {b} + 2×{h0:.4f}×√(1+{m}²)")
        print(f"       = {chi0:.4f} m")
        print(f"    R₀ = A₀/χ₀ = {R0:.4f} m")
        print(f"    B₀ = b + 2mh₀ = {b} + 2×{m}×{h0:.4f} = {B0:.4f} m (水面宽)")
        
        print(f"\n(4) 计算流速：")
        print(f"    v₀ = Q/A₀ = {Q}/{A0:.4f} = {v0:.3f} m/s ✓")
        
        # Froude数
        A_mean = A0 / B0  # 平均水深
        Fr = v0 / np.sqrt(self.g * A_mean)
        
        print(f"\n(5) 计算Froude数：")
        print(f"    平均水深 h_m = A₀/B₀ = {A0:.4f}/{B0:.4f} = {A_mean:.4f} m")
        print(f"    Fr = v₀/√(gh_m)")
        print(f"       = {v0:.3f}/√({self.g:.2f}×{A_mean:.4f})")
        print(f"       = {Fr:.4f} ✓")
        print(f"    ")
        if Fr < 1:
            print(f"    ∵ Fr < 1 ({Fr:.4f} < 1)")
            print(f"    ∴ 流态：缓流（亚临界流） ✓")
            flow_type = "缓流"
        elif Fr > 1:
            print(f"    ∵ Fr > 1 ({Fr:.4f} > 1)")
            print(f"    ∴ 流态：急流（超临界流）")
            flow_type = "急流"
        else:
            print(f"    Fr = 1，临界流")
            flow_type = "临界流"
        
        # 绘图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 子图1：梯形断面
        x_left = -m*h0
        x_right = b + m*h0
        
        ax1.fill([x_left, 0, b, x_right, x_right, x_left], 
                [h0, 0, 0, h0, h0, h0], 
                alpha=0.5, color='lightblue', edgecolor='blue', linewidth=2)
        ax1.plot([x_left, 0, b, x_right], [h0, 0, 0, h0], 'b-', linewidth=3, label='渠道轮廓')
        
        # 标注
        ax1.plot([b/2, b/2], [0, h0], 'r--', linewidth=2)
        ax1.text(b/2+0.2, h0/2, f'h₀={h0:.3f}m', fontsize=11, color='red')
        
        ax1.plot([0, b], [-0.2, -0.2], 'k-', linewidth=1)
        ax1.text(b/2, -0.4, f'b={b}m', fontsize=11, ha='center')
        
        ax1.plot([x_left, 0], [h0+0.1, h0+0.1], 'k-', linewidth=1)
        ax1.text((x_left)/2, h0+0.25, f'm={m}', fontsize=10, ha='center')
        
        # 流速矢量
        arrow_y = h0/2
        ax1.arrow(0.5, arrow_y, 0.8, 0, head_width=0.12, head_length=0.15, 
                 fc='green', ec='green', linewidth=2)
        ax1.text(1.5, arrow_y+0.25, f'v₀={v0:.2f}m/s\nFr={Fr:.3f}\n{flow_type}', 
                fontsize=10, color='green', bbox=dict(boxstyle='round', facecolor='lightyellow'))
        
        ax1.set_xlabel('宽度 (m)', fontsize=12)
        ax1.set_ylabel('水深 (m)', fontsize=12)
        ax1.set_title('Day 10 例题2：梯形明渠断面', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([x_left-0.5, x_right+0.5])
        ax1.set_ylim([-0.6, h0*1.4])
        ax1.set_aspect('equal')
        
        # 子图2：参数汇总
        params = ['正常水深h₀', '过水面积A₀', '湿周χ₀', '水力半径R₀', 
                 '平均流速v₀', 'Froude数Fr']
        values = [h0, A0, chi0, R0, v0, Fr]
        units = ['m', 'm²', 'm', 'm', 'm/s', '-']
        
        y_pos = np.arange(len(params))
        ax2.barh(y_pos, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'])
        
        for i, (param, value, unit) in enumerate(zip(params, values, units)):
            ax2.text(value + max(values)*0.02, i, f'{value:.4f} {unit}', 
                    va='center', fontsize=11, fontweight='bold')
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(params, fontsize=11)
        ax2.set_xlabel('数值', fontsize=12)
        ax2.set_title('计算结果汇总', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 标注流态
        ax2.text(max(values)*0.5, len(params)-0.5, 
                f'流态：{flow_type}\n(Fr={Fr:.4f})',
                fontsize=14, ha='center', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day10_uniform_flow/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 梯形断面几何关系 A, χ, R (3分) ⭐")
        print("✓ (2) Manning公式列式 (2分)")
        print("✓ (3) 求解正常水深h₀ (4分)")
        print("✓ (4) 计算平均流速v₀ = Q/A₀ (2分)")
        print("✓ (5) 计算Froude数Fr = v/√(gh_m) (2分) ⭐")
        print("✓ (6) 判断流态（Fr<1缓流，Fr>1急流） (1分)")
        print("✓ (7) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 梯形湿周：χ = b + 2h√(1+m²)，不是b+2h+2mh！")
        print("  ⚠️ Froude数用平均水深h_m = A/B，不是h₀！")
        print("  ⚠️ 边坡m的含义：水平:竖直 = m:1")
        
        return {'h0': h0, 'v0': v0, 'Fr': Fr, 'flow_type': flow_type}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 10 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背）：")
        print("  1. Manning公式：")
        print("     Q = (1/n) × A × R^(2/3) × i^(1/2)")
        print("     ")
        print("  2. 矩形断面：")
        print("     A = bh,  χ = b + 2h,  R = bh/(b+2h)")
        print("     ")
        print("  3. 梯形断面：")
        print("     A = (b+mh)h,  χ = b + 2h√(1+m²),  R = A/χ")
        print("     ")
        print("  4. Froude数：")
        print("     Fr = v/√(gh_m),  h_m = A/B")
        print("     Fr < 1: 缓流；Fr > 1: 急流")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  Step 1: 根据断面形状写出A, χ, R表达式")
        print("  Step 2: 列Manning公式 Q = (1/n)AR^(2/3)i^(1/2)")
        print("  Step 3: 迭代求解正常水深h₀（试算法或牛顿法）")
        print("  Step 4: 计算v₀ = Q/A₀")
        print("  Step 5: 计算Fr = v₀/√(gh_m)，判断流态")
        print("  Step 6: 验算检查")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：水力半径算错（湿周公式记错）")
        print("  ❌ 错误2：Manning公式中i写成i²或忘记开方")
        print("  ❌ 错误3：迭代初值太离谱导致不收敛")
        print("  ❌ 错误4：Froude数用h₀代替h_m")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：记住常用断面的A、χ、R公式")
        print("  ✓ 技巧2：迭代初值：h₀ ≈ (Qn/(bi^0.5))^(3/5)")
        print("  ✓ 技巧3：最后一定要验算Q")
        print("  ✓ 技巧4：注意单位统一（m, m³/s）")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能默写Manning公式")
        print("  □ 能独立计算矩形渠道正常水深")
        print("  □ 能独立计算梯形渠道正常水深")
        print("  □ 理解Froude数的物理意义")
        
        print("\n📅 明日预告：Day 11 - 临界水深与水跃")
        print("  预习内容：临界水深公式、水跃共轭水深、消能计算")
        
        print("\n💪 今日格言：")
        print("  「明渠均匀流是基础，掌握好了，明渠水力学就成功一半！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 10: 明渠均匀流")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day10 = Day10UniformFlow()
    
    # 例题1：矩形明渠
    result1 = day10.example_1_rectangular()
    
    # 例题2：梯形明渠
    result2 = day10.example_2_trapezoidal()
    
    # 每日总结
    day10.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 10 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握Manning公式")
    print(f"  ✓ 理解正常水深计算")
    print(f"  ✓ 生成2张图表")
    
    print(f"\n明日继续：Day 11 - 临界水深与水跃")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
