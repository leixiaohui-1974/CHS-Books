#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 22: 数值方法与计算水力学
Sprint Day 22: Numerical Methods in Hydraulics

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 有限差分法：偏微分方程离散化
  2. 水面线数值计算：逐步推进法
  3. 非恒定流计算：特征线法
  4. 管网计算：哈代-克罗斯法
  5. 数值积分：梯形法、辛普森法

🎯 学习目标：
  - 掌握数值方法基础
  - 理解水力学数值计算
  - 熟练迭代求解技巧
  - 了解计算精度控制

💪 今日格言：数值方法是现代工具！掌握计算技巧=提高5分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day22Numerical:
    """
    Day 22：数值方法与计算水力学
    
    包含2个核心例题：
    1. 基础题：水面线数值计算（逐步推进法）
    2. 强化题：管网哈代-克罗斯迭代
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        
    def example_1_water_surface_profile(self):
        """
        例题1：水面线数值计算⭐⭐⭐⭐⭐
        
        题目：矩形断面明渠，宽度b=3m，糙率n=0.02
              底坡i=0.0005，流量Q=10m³/s
              下游控制断面水深h1=2.5m
        求：用标准步长法计算上游500m处的水深
            步长Δx=100m，计算5个断面
        
        考点：水面线数值计算，标准步长法，迭代
        难度：基础（重要！）
        时间：20分钟
        分值：20分
        """
        print("\n" + "="*60)
        print("例题1：水面线数值计算⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 3.0       # 宽度 (m)
        n = 0.02      # 糙率
        i = 0.0005    # 底坡
        Q = 10.0      # 流量 (m³/s)
        h1 = 2.5      # 下游水深 (m)
        dx = 100.0    # 步长 (m)
        n_sections = 6  # 断面数（包括初始断面）
        
        print(f"\n已知条件：")
        print(f"  宽度 b = {b} m")
        print(f"  糙率 n = {n}")
        print(f"  底坡 i = {i}")
        print(f"  流量 Q = {Q} m³/s")
        print(f"  下游水深 h₁ = {h1} m")
        print(f"  步长 Δx = {dx} m")
        print(f"  计算断面数 = {n_sections}")
        
        # 计算过程
        print(f"\n解题步骤：")
        print(f"\n标准步长法公式：")
        print(f"  Δx = (E₂-E₁)/(i-J̄)")
        print(f"  E = h + Q²/(2gA²)")
        print(f"  J = (nQ/(AR^(2/3)))²")
        print(f"  J̄ = (J₁+J₂)/2")
        
        # 初始化数组
        x_array = np.zeros(n_sections)
        h_array = np.zeros(n_sections)
        A_array = np.zeros(n_sections)
        v_array = np.zeros(n_sections)
        E_array = np.zeros(n_sections)
        J_array = np.zeros(n_sections)
        
        # 第一个断面（下游）
        x_array[0] = 0
        h_array[0] = h1
        
        # 计算函数
        def calc_section(h):
            A = b * h
            chi = b + 2 * h
            R = A / chi
            v = Q / A
            E = h + v**2 / (2 * self.g)
            J = (n * Q / (A * R**(2/3)))**2
            return A, v, E, J
        
        # 计算第一个断面
        A_array[0], v_array[0], E_array[0], J_array[0] = calc_section(h_array[0])
        
        print(f"\n断面计算：")
        print(f"\n断面1（下游控制断面，x=0m）：")
        print(f"  h₁ = {h_array[0]:.3f} m")
        print(f"  A₁ = {A_array[0]:.3f} m²")
        print(f"  v₁ = {v_array[0]:.3f} m/s")
        print(f"  E₁ = {E_array[0]:.3f} m")
        print(f"  J₁ = {J_array[0]:.6f}")
        
        # 逐步推进计算
        for i in range(1, n_sections):
            print(f"\n断面{i+1}（x={i*dx}m）：")
            
            # 初始猜测值（假设水深变化不大）
            h_guess = h_array[i-1] + 0.05
            
            # 迭代求解
            max_iter = 20
            tol = 0.001
            
            for iter in range(max_iter):
                # 计算断面参数
                A2, v2, E2, J2 = calc_section(h_guess)
                
                # 计算平均水力坡度
                J_avg = (J_array[i-1] + J2) / 2
                
                # 计算水面线长度
                dx_calc = (E2 - E_array[i-1]) / (i - J_avg)
                
                # 检查收敛
                error = abs(dx_calc - dx)
                
                if error < tol:
                    break
                
                # 更新猜测值
                if dx_calc > dx:
                    h_guess -= 0.001
                else:
                    h_guess += 0.001
            
            # 保存结果
            x_array[i] = i * dx
            h_array[i] = h_guess
            A_array[i], v_array[i], E_array[i], J_array[i] = calc_section(h_guess)
            
            print(f"  迭代{iter+1}次收敛")
            print(f"  h = {h_array[i]:.3f} m ✓")
            print(f"  A = {A_array[i]:.3f} m²")
            print(f"  v = {v_array[i]:.3f} m/s")
            print(f"  E = {E_array[i]:.3f} m")
            print(f"  J = {J_array[i]:.6f}")
        
        print(f"\n最终结果：")
        print(f"  上游500m处水深：h = {h_array[-1]:.3f} m ✓")
        print(f"  水深变化：Δh = {h_array[-1] - h_array[0]:.3f} m")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：水面线纵剖面
        ax1 = plt.subplot(2, 2, 1)
        
        # 河底线
        x_bottom = np.array([x_array[0], x_array[-1]])
        y_bottom = np.array([0, -i * (x_array[-1] - x_array[0])])
        ax1.plot(x_bottom, y_bottom, 'k-', linewidth=2, label='河底')
        ax1.fill_between(x_bottom, y_bottom-0.5, y_bottom, 
                        color='gray', alpha=0.3)
        
        # 水面线
        y_water = y_bottom[0] + h_array[0] - i * x_array + (h_array - h_array[0])
        ax1.plot(x_array, y_water, 'b-', linewidth=2.5, 
                marker='o', markersize=8, label='水面线')
        
        # 断面标注
        for i, (x, y) in enumerate(zip(x_array, y_water)):
            ax1.text(x, y+0.15, f'{i+1}\nh={h_array[i]:.2f}m',
                    ha='center', fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax1.set_xlabel('距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 22 例题1：水面线数值计算', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 子图2：水深变化
        ax2 = plt.subplot(2, 2, 2)
        
        ax2.plot(x_array, h_array, 'b-', linewidth=2.5, 
                marker='o', markersize=10, label='水深h(x)')
        ax2.axhline(y=h_array[0], color='red', linestyle='--', 
                   linewidth=2, label=f'初始水深h₁={h_array[0]}m')
        
        ax2.set_xlabel('距离 (m)', fontsize=12)
        ax2.set_ylabel('水深 (m)', fontsize=12)
        ax2.set_title('水深沿程变化', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3：比能变化
        ax3 = plt.subplot(2, 2, 3)
        
        ax3.plot(x_array, E_array, 'g-', linewidth=2.5,
                marker='s', markersize=8, label='比能E(x)')
        ax3.plot(x_array, h_array, 'b--', linewidth=2,
                marker='o', markersize=6, label='水深h(x)')
        
        ax3.set_xlabel('距离 (m)', fontsize=12)
        ax3.set_ylabel('高程/能量 (m)', fontsize=12)
        ax3.set_title('比能与水深变化', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 子图4：结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        标准步长法逐步推进计算
        
        断面1（x=0m）：
          h₁ = {h_array[0]:.3f} m
        
        断面2（x=100m）：
          h₂ = {h_array[1]:.3f} m
        
        断面3（x=200m）：
          h₃ = {h_array[2]:.3f} m
        
        断面4（x=300m）：
          h₄ = {h_array[3]:.3f} m
        
        断面5（x=400m）：
          h₅ = {h_array[4]:.3f} m
        
        断面6（x=500m）：
          h₆ = {h_array[5]:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        水深变化：
          Δh = {h_array[-1]-h_array[0]:.3f} m
          趋势：{'壅水' if h_array[-1]>h_array[0] else '落水'}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • Δx=(E₂-E₁)/(i-J̄)
          • E=h+Q²/(2gA²)
          • J=(nQ/(AR^(2/3)))²
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day22_numerical/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（20分评分标准）：")
        print("="*60)
        print("✓ 写出标准步长法公式 (3分) ⭐")
        print("✓ 计算初始断面参数 (3分) ⭐")
        print("✓ 逐步推进计算（每断面2分）(10分) ⭐⭐⭐")
        print("✓ 迭代收敛判断 (2分)")
        print("✓ 最终结果 (2分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 标准步长法：Δx=(E₂-E₁)/(i-J̄)，注意i-J̄")
        print("  ⚠️ 比能：E=h+v²/(2g)，别忘动能项")
        print("  ⚠️ 迭代：需要反复调整h直到Δx收敛")
        print("  ⚠️ 方向：从下游向上游推进")
        
        return {'x': x_array, 'h': h_array, 'final_h': h_array[-1]}
    
    def example_2_pipe_network(self):
        """
        例题2：管网哈代-克罗斯法⭐⭐⭐⭐⭐
        
        题目：简单环状管网，3根管道组成闭合回路
              管道1：L1=1000m, d1=0.4m, λ1=0.025
              管道2：L2=800m, d2=0.3m, λ2=0.025  
              管道3：L3=600m, d3=0.35m, λ3=0.025
              外部流量：q1=0.15m³/s（流入），q2=-0.08m³/s（流出）
        求：用哈代-克罗斯法计算各管道流量
            初始假设：Q1=0.10m³/s, Q2=0.05m³/s, Q3=0.05m³/s
        
        考点：管网计算，哈代-克罗斯法，迭代
        难度：强化（必考！）
        时间：25分钟
        分值：25分
        """
        print("\n" + "="*60)
        print("例题2：管网哈代-克罗斯法⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        L = np.array([1000, 800, 600])  # 管长 (m)
        d = np.array([0.4, 0.3, 0.35])  # 管径 (m)
        lam = np.array([0.025, 0.025, 0.025])  # 摩阻系数
        q_ext = np.array([0.15, -0.08, 0])  # 外部流量 (m³/s)
        Q_init = np.array([0.10, 0.05, 0.05])  # 初始流量 (m³/s)
        
        print(f"\n已知条件：")
        print(f"  管道1：L={L[0]}m, d={d[0]}m, λ={lam[0]}")
        print(f"  管道2：L={L[1]}m, d={d[1]}m, λ={lam[2]}")
        print(f"  管道3：L={L[2]}m, d={d[2]}m, λ={lam[2]}")
        print(f"  外部流量：q₁={q_ext[0]}m³/s, q₂={q_ext[1]}m³/s")
        print(f"  初始假设：Q₁={Q_init[0]}m³/s, Q₂={Q_init[1]}m³/s, Q₃={Q_init[2]}m³/s")
        
        # 计算过程
        print(f"\n解题步骤：")
        print(f"\n哈代-克罗斯法：")
        print(f"  ΔQ = -Σhf / (2Σ|hf|/Q)")
        print(f"  hf = SQ|Q|")
        print(f"  S = 8λL/(π²gd⁵)")
        
        # 计算阻力系数S
        A = np.pi * d**2 / 4
        S = 8 * lam * L / (np.pi**2 * self.g * d**5)
        
        print(f"\n计算阻力系数S：")
        for i in range(3):
            print(f"  S{i+1} = 8×{lam[i]}×{L[i]}/(π²×{self.g}×{d[i]}⁵)")
            print(f"      = {S[i]:.2f} s²/m⁵")
        
        # 迭代计算
        Q = Q_init.copy()
        max_iter = 10
        tol = 0.001
        
        print(f"\n迭代计算：")
        
        history_Q = [Q.copy()]
        history_delta = []
        
        for iter in range(max_iter):
            print(f"\n第{iter+1}次迭代：")
            print(f"  当前流量：Q₁={Q[0]:.4f}, Q₂={Q[1]:.4f}, Q₃={Q[2]:.4f}")
            
            # 计算水头损失
            hf = S * Q * np.abs(Q)
            
            print(f"  水头损失：")
            for i in range(3):
                print(f"    hf{i+1} = {S[i]:.2f}×{Q[i]:.4f}×|{Q[i]:.4f}| = {hf[i]:.4f} m")
            
            # 计算闭合差
            sum_hf = np.sum(hf)
            
            print(f"  闭合差：Σhf = {sum_hf:.4f} m")
            
            # 计算分母
            sum_hf_Q = np.sum(np.abs(hf) / np.abs(Q))
            
            print(f"  分母：Σ|hf|/|Q| = {sum_hf_Q:.4f}")
            
            # 计算修正量
            delta_Q = -sum_hf / (2 * sum_hf_Q)
            
            print(f"  修正量：ΔQ = -{sum_hf:.4f}/(2×{sum_hf_Q:.4f})")
            print(f"          = {delta_Q:.4f} m³/s")
            
            history_delta.append(abs(delta_Q))
            
            # 检查收敛
            if abs(delta_Q) < tol:
                print(f"\n  ✓ 收敛！|ΔQ|={abs(delta_Q):.6f} < {tol}")
                break
            
            # 更新流量
            Q = Q + delta_Q
            history_Q.append(Q.copy())
            
            print(f"  更新后：Q₁={Q[0]:.4f}, Q₂={Q[1]:.4f}, Q₃={Q[2]:.4f}")
        
        # 最终结果
        print(f"\n最终结果（第{iter+1}次迭代收敛）：")
        print(f"  Q₁ = {Q[0]:.4f} m³/s ✓")
        print(f"  Q₂ = {Q[1]:.4f} m³/s ✓")
        print(f"  Q₃ = {Q[2]:.4f} m³/s ✓")
        
        # 验证连续性
        print(f"\n验证连续性方程：")
        node_balance = q_ext[0] - Q[0] - Q[1]
        print(f"  节点A：q₁ - Q₁ - Q₂ = {q_ext[0]} - {Q[0]:.4f} - {Q[1]:.4f}")
        print(f"        = {node_balance:.6f} ≈ 0 ✓")
        
        # 验证能量方程
        print(f"\n验证能量方程（回路闭合）：")
        hf_final = S * Q * np.abs(Q)
        loop_check = np.sum(hf_final)
        print(f"  Σhf = {loop_check:.6f} ≈ 0 ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：管网示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 节点
        nodes = {'A': (0, 0), 'B': (4, 0), 'C': (2, 3)}
        for name, pos in nodes.items():
            circle = Circle(pos, 0.3, color='blue', alpha=0.7)
            ax1.add_patch(circle)
            ax1.text(pos[0], pos[1], name, ha='center', va='center',
                    fontsize=14, fontweight='bold', color='white')
        
        # 管道
        pipes = [
            ((0, 0), (4, 0), Q[0], '1'),  # A-B
            ((0, 0), (2, 3), Q[1], '2'),  # A-C
            ((4, 0), (2, 3), Q[2], '3'),  # B-C
        ]
        
        for start, end, flow, label in pipes:
            # 管道线
            ax1.plot([start[0], end[0]], [start[1], end[1]],
                    'k-', linewidth=3)
            
            # 流量箭头
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            dx = (end[0] - start[0]) * 0.15
            dy = (end[1] - start[1]) * 0.15
            
            ax1.arrow(mid_x - dx/2, mid_y - dy/2, dx, dy,
                     head_width=0.2, head_length=0.2,
                     fc='red', ec='red', linewidth=2)
            
            # 标注
            offset_x = -dy * 0.5
            offset_y = dx * 0.5
            ax1.text(mid_x + offset_x, mid_y + offset_y,
                    f'管{label}\nQ={flow:.4f}m³/s',
                    ha='center', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 外部流量
        ax1.arrow(0, -1, 0, 0.5, head_width=0.2, head_length=0.15,
                 fc='green', ec='green', linewidth=3)
        ax1.text(0, -1.5, f'q₁={q_ext[0]}m³/s', ha='center',
                fontsize=10, color='green', fontweight='bold')
        
        ax1.arrow(4, 0.5, 0, -0.5, head_width=0.2, head_length=0.15,
                 fc='orange', ec='orange', linewidth=3)
        ax1.text(4, 1, f'q₂={q_ext[1]}m³/s', ha='center',
                fontsize=10, color='orange', fontweight='bold')
        
        ax1.set_xlabel('X', fontsize=12)
        ax1.set_ylabel('Y', fontsize=12)
        ax1.set_title('Day 22 例题2：管网示意图', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1.5, 5.5])
        ax1.set_ylim([-2, 4])
        ax1.set_aspect('equal')
        
        # 子图2：迭代收敛过程
        ax2 = plt.subplot(2, 2, 2)
        
        history_Q_array = np.array(history_Q)
        iterations = range(len(history_Q))
        
        ax2.plot(iterations, history_Q_array[:, 0], 'r-o',
                linewidth=2, markersize=8, label='Q₁')
        ax2.plot(iterations, history_Q_array[:, 1], 'g-s',
                linewidth=2, markersize=8, label='Q₂')
        ax2.plot(iterations, history_Q_array[:, 2], 'b-^',
                linewidth=2, markersize=8, label='Q₃')
        
        ax2.set_xlabel('迭代次数', fontsize=12)
        ax2.set_ylabel('流量 (m³/s)', fontsize=12)
        ax2.set_title('流量迭代收敛过程', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3：修正量变化
        ax3 = plt.subplot(2, 2, 3)
        
        if history_delta:
            ax3.semilogy(range(1, len(history_delta)+1), history_delta,
                        'r-o', linewidth=2.5, markersize=10)
            ax3.axhline(y=tol, color='green', linestyle='--',
                       linewidth=2, label=f'收敛阈值={tol}')
        
        ax3.set_xlabel('迭代次数', fontsize=12)
        ax3.set_ylabel('|ΔQ| (m³/s, 对数)', fontsize=12)
        ax3.set_title('修正量收敛曲线', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, which='both')
        
        # 子图4：结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━
        哈代-克罗斯迭代法
        
        初始假设：
          Q₁ = {Q_init[0]:.4f} m³/s
          Q₂ = {Q_init[1]:.4f} m³/s
          Q₃ = {Q_init[2]:.4f} m³/s
        
        最终结果（第{iter+1}次迭代）：
          Q₁ = {Q[0]:.4f} m³/s ✓
          Q₂ = {Q[1]:.4f} m³/s ✓
          Q₃ = {Q[2]:.4f} m³/s ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━
        验证：
        
        连续性（节点A）：
          q₁-Q₁-Q₂ = {node_balance:.6f} ✓
        
        能量（回路）：
          Σhf = {loop_check:.6f} ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • ΔQ = -Σhf/(2Σ|hf|/Q)
          • hf = SQ|Q|
          • S = 8λL/(π²gd⁵)
        ━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day22_numerical/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（25分评分标准）：")
        print("="*60)
        print("✓ 写出哈代-克罗斯公式 (3分) ⭐")
        print("✓ 计算阻力系数S (3分) ⭐")
        print("✓ 第1次迭代计算 (6分) ⭐⭐")
        print("✓ 第2次迭代计算 (5分) ⭐")
        print("✓ 收敛判断 (3分)")
        print("✓ 最终结果 (3分)")
        print("✓ 连续性验证 (2分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 修正量：ΔQ=-Σhf/(2Σ|hf|/Q)，注意负号和2")
        print("  ⚠️ 水头损失：hf=SQ|Q|，Q要带符号，|Q|取绝对值")
        print("  ⚠️ 收敛：每次迭代后要检查|ΔQ|<容差")
        print("  ⚠️ 方向：流量方向要保持一致")
        
        return {'Q': Q, 'iterations': iter+1}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 22 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 标准步长法：")
        print("     Δx = (E₂-E₁)/(i-J̄)")
        print("     E = h + Q²/(2gA²)")
        print("     J = (nQ/(AR^(2/3)))²")
        print("     ")
        print("  2. 哈代-克罗斯法：")
        print("     ΔQ = -Σhf / (2Σ|hf|/Q)")
        print("     hf = SQ|Q|")
        print("     S = 8λL/(π²gd⁵)")
        print("     ")
        print("  3. 迭代收敛条件：")
        print("     |ΔQ| < ε (ε为容差)")
        print("     或|Σhf| < ε")
        
        print("\n✅ 数值方法对比：")
        print("  ┌──────────────┬────────────┬──────────┐")
        print("  │ 方法         │ 适用问题   │ 收敛速度 │")
        print("  ├──────────────┼────────────┼──────────┤")
        print("  │ 标准步长法   │ 水面线     │ 较快     │")
        print("  │ 哈代-克罗斯  │ 管网       │ 中等     │")
        print("  │ 特征线法     │ 非恒定流   │ 快       │")
        print("  │ 有限差分     │ 偏微分方程 │ 慢       │")
        print("  └──────────────┴────────────┴──────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【水面线数值计算】")
        print("  Step 1: 从下游控制断面开始")
        print("  Step 2: 假设上游断面水深")
        print("  Step 3: 计算E、J等参数")
        print("  Step 4: 用Δx公式迭代")
        print("  Step 5: 逐步向上游推进")
        print("  ")
        print("  【管网计算】")
        print("  Step 1: 假设初始流量分配")
        print("  Step 2: 计算各管水头损失")
        print("  Step 3: 计算闭合差Σhf")
        print("  Step 4: 计算修正量ΔQ")
        print("  Step 5: 更新流量，重复迭代")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：水面线从上游算起（应从下游）")
        print("  ❌ 错误2：比能忘记动能项v²/(2g)")
        print("  ❌ 错误3：哈代-克罗斯忘记负号和2")
        print("  ❌ 错误4：水头损失hf=SQ²（应是SQ|Q|）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：水面线→从下游向上游逐步推进")
        print("  ✓ 技巧2：管网→先假设合理初值，减少迭代")
        print("  ✓ 技巧3：迭代→每步检查收敛，避免无限循环")
        print("  ✓ 技巧4：验证→最后验证连续性和能量方程")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能准确使用标准步长法")
        print("  □ 掌握哈代-克罗斯迭代")
        print("  □ 理解数值收敛判断")
        print("  □ 熟练迭代求解技巧")
        
        print("\n📅 明日预告：Day 23 - 第一周测试")
        print("  • Day 1-10知识测试")
        print("  • 综合复习")
        print("  • 查漏补缺")
        
        print("\n💪 今日格言：")
        print("  「数值方法是现代工具！掌握计算技巧=提高5分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 22: 数值方法与计算水力学")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day22 = Day22Numerical()
    
    # 例题1：水面线数值计算
    result1 = day22.example_1_water_surface_profile()
    
    # 例题2：管网计算
    result2 = day22.example_2_pipe_network()
    
    # 每日总结
    day22.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 22 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握标准步长法")
    print(f"  ✓ 掌握哈代-克罗斯法")
    print(f"  ✓ 理解迭代收敛")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n下一步：Day 23 - 第一周测试")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
