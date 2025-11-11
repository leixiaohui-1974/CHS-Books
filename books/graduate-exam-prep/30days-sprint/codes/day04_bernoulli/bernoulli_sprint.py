#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 4: 伯努利方程基础
Sprint Day 4: Bernoulli Equation Fundamentals

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 伯努利方程：z + p/(ρg) + v²/(2g) = H
  2. 总流伯努利方程（含损失）
  3. 能量线与水力坡度

🎯 学习目标：
  - 掌握伯努利方程适用条件
  - 熟练进行能量计算
  - 理解能量线绘制

💪 今日格言：伯努利方程是水力学之魂！掌握它=掌握50%的考点！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day4Bernoulli:
    """
    Day 4：伯努利方程基础
    
    包含3个核心例题：
    1. 基础题：简单管道伯努利方程
    2. 强化题：虹吸管计算
    3. 综合题：能量线绘制
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水的密度 (kg/m³)
        self.gamma = self.rho * self.g  # 重度 (N/m³)
        
    def example_1_pipe_flow(self):
        """
        例题1：简单管道伯努利方程（基础题）⭐⭐⭐⭐⭐
        
        题目：水从水箱经管道流出，水箱水面高程10m，出口高程2m，
             管径d=0.1m，忽略损失，求出口流速和流量
        
        考点：理想流体伯努利方程
        难度：基础
        时间：10分钟
        分值：10分
        """
        print("\n" + "="*60)
        print("例题1：简单管道伯努利方程（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        z1 = 10.0  # 水箱水面高程 (m)
        z2 = 2.0   # 出口高程 (m)
        d = 0.1    # 管径 (m)
        p1 = 0     # 水箱水面大气压（相对压强=0）
        p2 = 0     # 出口大气压（相对压强=0）
        v1 = 0     # 水箱水面流速≈0
        
        print(f"\n已知条件：")
        print(f"  水箱水面高程 z₁ = {z1:.1f} m")
        print(f"  出口高程 z₂ = {z2:.1f} m")
        print(f"  管径 d = {d:.2f} m")
        print(f"  忽略损失（理想流体）")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # 列伯努利方程
        print(f"\n(1) 列伯努利方程（1-1断面到2-2断面）：")
        print(f"    z₁ + p₁/(ρg) + v₁²/(2g) = z₂ + p₂/(ρg) + v₂²/(2g) + hw")
        print(f"    ")
        print(f"    已知：p₁ = p₂ = 0 (大气压)")
        print(f"          v₁ ≈ 0 (水箱很大)")
        print(f"          hw = 0 (忽略损失)")
        print(f"    ")
        print(f"    简化为：z₁ = z₂ + v₂²/(2g)")
        
        # 求出口流速
        v2 = np.sqrt(2 * self.g * (z1 - z2))
        print(f"\n(2) 求出口流速 v₂：")
        print(f"    v₂²/(2g) = z₁ - z₂ = {z1} - {z2} = {z1-z2} m")
        print(f"    v₂ = √[2g(z₁ - z₂)]")
        print(f"       = √[2 × {self.g:.2f} × {z1-z2}]")
        print(f"       = {v2:.3f} m/s ✓")
        
        # 求流量
        A = np.pi * d**2 / 4
        Q = A * v2
        print(f"\n(3) 求流量 Q：")
        print(f"    A = πd²/4 = π × {d}²/4 = {A:.6f} m²")
        print(f"    Q = Av₂")
        print(f"      = {A:.6f} × {v2:.3f}")
        print(f"      = {Q:.6f} m³/s")
        print(f"      = {Q*1000:.3f} L/s ✓")
        
        # 能量分析
        E1 = z1 + p1/(self.gamma) + v1**2/(2*self.g)
        E2 = z2 + p2/(self.gamma) + v2**2/(2*self.g)
        
        print(f"\n(4) 能量分析：")
        print(f"    断面1总水头 H₁ = z₁ + p₁/(γ) + v₁²/(2g)")
        print(f"                   = {z1} + 0 + 0 = {E1:.2f} m")
        print(f"    断面2总水头 H₂ = z₂ + p₂/(γ) + v₂²/(2g)")
        print(f"                   = {z2} + 0 + {v2**2/(2*self.g):.2f}")
        print(f"                   = {E2:.2f} m")
        print(f"    能量守恒：H₁ = H₂ ✓ ({E1:.2f} = {E2:.2f})")
        
        # 绘图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 子图1：系统示意图
        # 水箱
        ax1.fill([0, 2, 2, 0], [z1-2, z1-2, z1, z1], alpha=0.3, edgecolor='black', 
                linewidth=2, facecolor='lightgray', label='水箱')
        ax1.fill([0, 2, 2, 0], [z1-2, z1-2, z1, z1], alpha=0.5, facecolor='lightblue')
        ax1.plot([0, 2], [z1, z1], 'b-', linewidth=2)
        
        # 管道
        x_pipe = np.array([2, 4, 6, 8])
        z_pipe = np.array([z1-2, 6, 4, z2])
        ax1.plot(x_pipe, z_pipe, 'k-', linewidth=6, label='管道')
        
        # 出口射流
        x_jet = np.linspace(8, 10, 20)
        v_jet = np.linspace(v2, v2*0.8, 20)
        z_jet = z2 - 0.5*(x_jet-8)**2/2  # 抛物线
        ax1.plot(x_jet, z_jet, 'b--', linewidth=2, alpha=0.7, label='射流')
        
        # 能量线（水平线）
        ax1.axhline(y=z1, color='red', linestyle='--', linewidth=2, label=f'能量线 H={z1}m')
        
        # 测压管水头线
        ax1.plot([1, 2, 4, 6, 8], [z1, z1, 6+v2**2/(2*self.g), 
                                    4+v2**2/(2*self.g), z2+v2**2/(2*self.g)], 
                'g--', linewidth=2, label='测压管水头线')
        
        # 标注
        ax1.plot(1, z1, 'ro', markersize=10)
        ax1.text(0.5, z1+0.5, f'断面1\nz₁={z1}m\nv₁=0', fontsize=10)
        
        ax1.plot(8, z2, 'ro', markersize=10)
        ax1.text(8.2, z2+0.5, f'断面2\nz₂={z2}m\nv₂={v2:.2f}m/s', fontsize=10)
        
        # 标注高差
        ax1.plot([10.5, 10.5], [z2, z1], 'k-', linewidth=1)
        ax1.plot([10.3, 10.7], [z2, z2], 'k-', linewidth=1)
        ax1.plot([10.3, 10.7], [z1, z1], 'k-', linewidth=1)
        ax1.text(10.8, (z1+z2)/2, f'Δz={z1-z2}m', fontsize=11)
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 4 例题1：伯努利方程应用\n水箱出流', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.5, 12])
        ax1.set_ylim([0, 12])
        
        # 子图2：能量转换图
        positions = [0, 1]
        z_values = [z1, z2]
        p_values = [0, 0]
        v_values = [0, v2**2/(2*self.g)]
        
        width = 0.4
        colors = ['#8B4513', '#4169E1', '#FF6347']
        
        for i, pos in enumerate(positions):
            # 位置水头（棕色）
            ax2.bar(pos, z_values[i], width, label='位置水头 z' if i==0 else '', 
                   color=colors[0], edgecolor='black', linewidth=1.5)
            # 压强水头（蓝色）
            ax2.bar(pos, p_values[i], width, bottom=z_values[i],
                   label='压强水头 p/(ρg)' if i==0 else '', 
                   color=colors[1], edgecolor='black', linewidth=1.5)
            # 流速水头（红色）
            ax2.bar(pos, v_values[i], width, bottom=z_values[i]+p_values[i],
                   label='流速水头 v²/(2g)' if i==0 else '', 
                   color=colors[2], edgecolor='black', linewidth=1.5)
            
            # 标注总水头
            total = z_values[i] + p_values[i] + v_values[i]
            ax2.text(pos, total+0.3, f'H={total:.2f}m', ha='center', fontsize=11, fontweight='bold')
        
        # 绘制能量守恒线
        ax2.plot([positions[0], positions[1]], [E1, E2], 'r--', linewidth=2, marker='o', 
                markersize=8, label='总水头')
        
        ax2.set_xticks(positions)
        ax2.set_xticklabels(['断面1\n(水箱水面)', '断面2\n(出口)'], fontsize=11)
        ax2.set_ylabel('水头 (m)', fontsize=12)
        ax2.set_title('能量转换分析', fontsize=13, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_ylim([0, 12])
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day04_bernoulli/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（10分评分标准）：")
        print("="*60)
        print("✓ (1) 正确列出伯努利方程 (3分) ⭐")
        print("✓ (2) 合理简化（p₁=p₂=0, v₁=0, hw=0） (2分)")
        print("✓ (3) 求出口流速 v₂ = √[2g(z₁-z₂)] (3分)")
        print("✓ (4) 求流量 Q = Av₂ (1分)")
        print("✓ (5) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 伯努利方程要沿流线列，选合适的断面")
        print("  ⚠️ 注意各项的零点：位置水头选基准面，压强水头相对压强")
        print("  ⚠️ 水箱水面流速不是严格为0，但可近似为0")
        
        return {'v2': v2, 'Q': Q}
    
    def example_2_siphon(self):
        """
        例题2：虹吸管计算（强化题）⭐⭐⭐⭐
        
        题目：虹吸管从水箱抽水，水面高程5m，出口高程1m，
             顶部高程7m，管径d=0.05m，损失系数Σζ=5.0
        求：(1) 流量
            (2) 顶部压强（判断是否会发生汽蚀）
        
        考点：伯努利方程+损失+负压判断
        难度：强化
        时间：25分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题2：虹吸管计算（强化题）⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        z1 = 5.0   # 水箱水面高程 (m)
        z2 = 1.0   # 出口高程 (m)
        z3 = 7.0   # 虹吸管顶部高程 (m)
        d = 0.05   # 管径 (m)
        zeta_sum = 5.0  # 总损失系数
        p_atm = 101325  # 大气压强 (Pa)
        p_v = 2337      # 水的饱和蒸汽压（20°C） (Pa)
        
        print(f"\n已知条件：")
        print(f"  水箱水面高程 z₁ = {z1:.1f} m")
        print(f"  出口高程 z₂ = {z2:.1f} m")
        print(f"  顶部高程 z₃ = {z3:.1f} m")
        print(f"  管径 d = {d:.2f} m")
        print(f"  总损失系数 Σζ = {zeta_sum:.1f}")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 求流量
        print(f"\n(1) 求流量（列1-1到2-2伯努利方程）：")
        print(f"    z₁ + 0 + 0 = z₂ + 0 + v₂²/(2g) + hw")
        print(f"    ")
        print(f"    损失水头：hw = Σζ × v²/(2g)")
        print(f"    ")
        print(f"    代入：z₁ = z₂ + v²/(2g) + Σζ × v²/(2g)")
        print(f"           z₁ = z₂ + (1 + Σζ) × v²/(2g)")
        
        # 求流速
        v = np.sqrt(2 * self.g * (z1 - z2) / (1 + zeta_sum))
        print(f"    ")
        print(f"    v = √[2g(z₁-z₂)/(1+Σζ)]")
        print(f"      = √[2 × {self.g:.2f} × {z1-z2} / {1+zeta_sum}]")
        print(f"      = {v:.3f} m/s ✓")
        
        # 求流量
        A = np.pi * d**2 / 4
        Q = A * v
        print(f"    ")
        print(f"    Q = Av = {A:.7f} × {v:.3f}")
        print(f"      = {Q:.7f} m³/s")
        print(f"      = {Q*1000:.4f} L/s ✓")
        
        # (2) 求顶部压强
        print(f"\n(2) 求顶部压强（列1-1到3-3伯努利方程）：")
        print(f"    假设1-1到3-3的损失为总损失的一半")
        hw_13 = zeta_sum/2 * v**2 / (2*self.g)
        print(f"    hw₁₋₃ ≈ {zeta_sum/2} × v²/(2g) = {hw_13:.3f} m")
        
        print(f"    ")
        print(f"    z₁ + 0 + 0 = z₃ + p₃/(ρg) + v²/(2g) + hw₁₋₃")
        
        p3_head = z1 - z3 - v**2/(2*self.g) - hw_13
        p3 = p3_head * self.gamma
        
        print(f"    ")
        print(f"    p₃/(ρg) = z₁ - z₃ - v²/(2g) - hw₁₋₃")
        print(f"            = {z1} - {z3} - {v**2/(2*self.g):.3f} - {hw_13:.3f}")
        print(f"            = {p3_head:.3f} m")
        print(f"    ")
        print(f"    p₃ = ρg × {p3_head:.3f}")
        print(f"       = {p3:.0f} Pa (相对压强)")
        print(f"       = {p3/1000:.1f} kPa")
        
        # 绝对压强
        p3_abs = p_atm + p3
        print(f"    ")
        print(f"    绝对压强 p₃(abs) = p₃ + p_atm")
        print(f"                    = {p3:.0f} + {p_atm}")
        print(f"                    = {p3_abs:.0f} Pa ✓")
        
        # 判断汽蚀
        print(f"\n(3) 汽蚀判断：")
        print(f"    水的饱和蒸汽压（20°C）pᵥ = {p_v} Pa")
        print(f"    顶部绝对压强 p₃(abs) = {p3_abs:.0f} Pa")
        print(f"    ")
        if p3_abs > p_v:
            print(f"    ∵ p₃(abs) > pᵥ ({p3_abs:.0f} > {p_v})")
            print(f"    ∴ 不会发生汽蚀 ✓")
            cavitation = False
        else:
            print(f"    ∵ p₃(abs) < pᵥ ({p3_abs:.0f} < {p_v})")
            print(f"    ∴ 会发生汽蚀 ⚠️")
            cavitation = True
        
        # 绘图
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # 水箱
        ax.fill([0, 2, 2, 0], [z1-2, z1-2, z1, z1], alpha=0.3, edgecolor='black', 
               linewidth=2, facecolor='lightgray')
        ax.fill([0, 2, 2, 0], [z1-2, z1-2, z1, z1], alpha=0.5, facecolor='lightblue')
        ax.plot([0, 2], [z1, z1], 'b-', linewidth=2, label='水面')
        
        # 虹吸管路径
        x_pipe = [2, 3, 4, 5, 6, 7]
        z_pipe = [z1-1.5, z3-0.5, z3, z3-0.5, 4, z2]
        ax.plot(x_pipe, z_pipe, 'k-', linewidth=6, label='虹吸管')
        
        # 标注关键点
        ax.plot(1, z1, 'ro', markersize=12, label='断面1（水面）')
        ax.plot(4, z3, 'go', markersize=12, label=f'断面3（顶部）')
        ax.plot(7, z2, 'bo', markersize=12, label='断面2（出口）')
        
        # 标注文字
        ax.text(0.5, z1+0.5, f'断面1\nz₁={z1}m\np₁=0', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat'))
        ax.text(4, z3+0.7, f'断面3\nz₃={z3}m\np₃={p3/1000:.1f}kPa', fontsize=10, 
               bbox=dict(boxstyle='round', facecolor='lightgreen'))
        ax.text(7.2, z2+0.5, f'断面2\nz₂={z2}m\nv={v:.2f}m/s', fontsize=10, 
               bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        # 能量线
        # 简化：假设线性下降
        E1 = z1
        E2 = z2 + v**2/(2*self.g)
        E3 = z3 + p3_head + v**2/(2*self.g)
        
        x_energy = [1, 4, 7]
        z_energy = [E1, E3, E2]
        ax.plot(x_energy, z_energy, 'r--', linewidth=2, marker='s', markersize=8, 
               label='能量线')
        
        # 测压管水头线
        x_piezo = [1, 4, 7]
        z_piezo = [z1, z3+p3_head, z2]
        ax.plot(x_piezo, z_piezo, 'g--', linewidth=2, marker='^', markersize=8, 
               label='测压管水头线')
        
        # 标注高差
        ax.plot([8.5, 8.5], [z2, z1], 'k-', linewidth=1)
        ax.plot([8.3, 8.7], [z2, z2], 'k-', linewidth=1)
        ax.plot([8.3, 8.7], [z1, z1], 'k-', linewidth=1)
        ax.text(8.9, (z1+z2)/2, f'Δz={z1-z2}m', fontsize=11)
        
        # 标注顶部抬高
        ax.plot([4.5, 4.5], [z1, z3], 'purple', linestyle=':', linewidth=2)
        ax.text(4.7, (z1+z3)/2, f'{z3-z1}m\n(抬高)', fontsize=10, color='purple')
        
        ax.set_xlabel('水平距离 (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('Day 4 例题2：虹吸管计算\n负压与汽蚀判断', fontsize=13, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([-0.5, 10])
        ax.set_ylim([0, 8])
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day04_bernoulli/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 列1-2伯努利方程，含损失 (3分)")
        print("✓ (2) 求流速 v = √[2g(z₁-z₂)/(1+Σζ)] (3分)")
        print("✓ (3) 求流量 Q = Av (2分)")
        print("✓ (4) 列1-3伯努利方程，求p₃ (4分) ⭐")
        print("✓ (5) 汽蚀判断 p₃(abs) vs pᵥ (2分) ⭐")
        print("✓ (6) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 顶部是负压（真空），p₃ < 0")
        print("  ⚠️ 汽蚀判断用绝对压强，不是相对压强")
        print("  ⚠️ 虹吸管顶部不能抬太高，否则汽蚀")
        
        return {'Q': Q, 'p3': p3, 'cavitation': cavitation}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 4 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背）：")
        print("  1. 伯努利方程：")
        print("     z + p/(ρg) + v²/(2g) = H (常数)")
        print("     ")
        print("  2. 总流伯努利方程（含损失）：")
        print("     z₁ + p₁/(ρg) + α₁v₁²/(2g) = z₂ + p₂/(ρg) + α₂v₂²/(2g) + hw")
        print("     ")
        print("  3. 损失水头：")
        print("     hw = hf + hj = λ(L/d)×v²/(2g) + Σζ×v²/(2g)")
        print("     ")
        print("  4. 汽蚀判断：")
        print("     p_abs > pᵥ （不汽蚀）")
        
        print("\n✅ 适用条件（重要！）：")
        print("  1. 理想流体（不可压缩、无粘性）或实际流体（加损失项）")
        print("  2. 定常流动")
        print("  3. 沿同一流线")
        print("  4. 质量力只有重力")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  Step 1: 选取合适的断面（已知量多的断面）")
        print("  Step 2: 确定基准面（通常取最低点）")
        print("  Step 3: 列伯努利方程")
        print("  Step 4: 代入已知量，求未知量")
        print("  Step 5: 检查合理性（能量不增，速度合理）")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：基准面选取不一致")
        print("  ❌ 错误2：压强用绝对压强还是相对压强不明确")
        print("  ❌ 错误3：损失项忘记加或加错地方")
        print("  ❌ 错误4：汽蚀判断用相对压强（应用绝对压强）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：画图！标出所有断面、基准面、能量线")
        print("  ✓ 技巧2：符号统一！p用Pa，z用m，v用m/s")
        print("  ✓ 技巧3：损失！实际流体必有损失，理想流体才无损失")
        print("  ✓ 技巧4：负压！虹吸管、泵吸水等都会产生负压")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能默写伯努利方程（含损失）")
        print("  □ 能独立完成例题1（水箱出流）")
        print("  □ 能独立完成例题2（虹吸管+汽蚀）")
        print("  □ 理解能量线、测压管水头线")
        
        print("\n📅 明日预告：Day 5 - 连续性方程与动量方程")
        print("  预习内容：连续性方程、动量方程、水流对壁面的作用力")
        
        print("\n💪 今日格言：")
        print("  「伯努利方程掌握了，水力学就成功一半！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 4: 伯努利方程基础")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day4 = Day4Bernoulli()
    
    # 例题1：简单管道
    result1 = day4.example_1_pipe_flow()
    
    # 例题2：虹吸管
    result2 = day4.example_2_siphon()
    
    # 每日总结
    day4.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 4 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握伯努利方程")
    print(f"  ✓ 理解汽蚀现象")
    print(f"  ✓ 生成2张图表")
    
    print(f"\n明日继续：Day 5 - 连续性方程与动量方程")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
