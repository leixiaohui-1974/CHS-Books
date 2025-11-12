#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 13: 堰流与闸孔出流
Sprint Day 13: Weir Flow and Orifice Flow

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 薄壁堰流量公式：Q = m × b × H^(3/2)
  2. 实用堰流量公式：Q = m × b × H^n
  3. 闸孔出流：自由出流 vs 淹没出流

🎯 学习目标：
  - 掌握薄壁堰流量计算
  - 熟练计算闸孔出流
  - 理解自由出流与淹没出流

💪 今日格言：堰流公式是考研送分题！掌握公式=拿到12分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, Polygon

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day13WeirGate:
    """
    Day 13：堰流与闸孔出流
    
    包含3个核心例题：
    1. 基础题：薄壁堰流量计算
    2. 强化题：实用堰流量计算
    3. 综合题：闸孔出流（自由+淹没）
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        
    def example_1_thin_plate_weir(self):
        """
        例题1：薄壁堰流量计算（基础题）⭐⭐⭐⭐⭐
        
        题目：矩形薄壁堰，堰宽b=2m，堰顶水头H=0.5m
              流量系数m=0.42
        求：(1) 通过流量Q
            (2) 若流量增加到1.5倍，求水头H₂
            (3) 分析流量与水头的关系
        
        考点：薄壁堰流量公式，Q与H的关系
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题1：薄壁堰流量计算（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 2.0      # 堰宽 (m)
        H1 = 0.5     # 堰顶水头 (m)
        m = 0.42     # 流量系数
        
        print(f"\n已知条件：")
        print(f"  矩形薄壁堰宽度 b = {b:.1f} m")
        print(f"  堰顶水头 H = {H1:.1f} m")
        print(f"  流量系数 m = {m:.2f}")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 计算流量
        print(f"\n(1) 计算通过流量：")
        print(f"    薄壁堰流量公式：")
        print(f"    Q = m × b × √(2g) × H^(3/2)")
        print(f"    ")
        
        Q1 = m * b * np.sqrt(2*self.g) * H1**(3/2)
        
        print(f"    Q = {m} × {b} × √(2×{self.g:.2f}) × {H1}^(3/2)")
        print(f"      = {m} × {b} × {np.sqrt(2*self.g):.3f} × {H1**(3/2):.4f}")
        print(f"      = {Q1:.4f} m³/s ✓")
        
        # 简化形式
        m_eff = m * np.sqrt(2*self.g)
        print(f"    ")
        print(f"    简化形式：Q = m'bH^(3/2)")
        print(f"    其中 m' = m√(2g) = {m}×√(2×{self.g:.2f}) = {m_eff:.4f}")
        print(f"    Q = {m_eff:.4f} × {b} × {H1}^(3/2)")
        print(f"      = {Q1:.4f} m³/s ✓")
        
        # (2) 流量增加到1.5倍
        print(f"\n(2) 流量增加到1.5倍，求新水头：")
        Q2 = 1.5 * Q1
        
        print(f"    Q₂ = 1.5 × Q₁ = 1.5 × {Q1:.4f} = {Q2:.4f} m³/s")
        print(f"    ")
        print(f"    由 Q = m'bH^(3/2)，得：")
        print(f"    H = (Q/(m'b))^(2/3)")
        print(f"    ")
        
        H2 = (Q2 / (m_eff * b))**(2/3)
        
        print(f"    H₂ = ({Q2:.4f}/({m_eff:.4f}×{b}))^(2/3)")
        print(f"       = ({Q2/(m_eff*b):.4f})^(2/3)")
        print(f"       = {H2:.4f} m ✓")
        
        # 增加倍数
        ratio_Q = Q2 / Q1
        ratio_H = H2 / H1
        
        print(f"    ")
        print(f"    分析：")
        print(f"    流量比：Q₂/Q₁ = {ratio_Q:.2f}")
        print(f"    水头比：H₂/H₁ = {H2:.4f}/{H1} = {ratio_H:.4f}")
        print(f"    ")
        print(f"    验证：(H₂/H₁)^(3/2) = {ratio_H:.4f}^(3/2) = {ratio_H**(3/2):.4f} ≈ {ratio_Q:.2f} ✓")
        
        # (3) 流量与水头关系
        print(f"\n(3) 流量与水头关系分析：")
        print(f"    Q ∝ H^(3/2)")
        print(f"    ")
        print(f"    结论：")
        print(f"    • 水头增加1.5倍 → 流量增加1.5^(3/2) = {1.5**(3/2):.3f}倍")
        print(f"    • 流量增加1.5倍 → 水头增加1.5^(2/3) = {1.5**(2/3):.3f}倍 ✓")
        print(f"    • 流量对水头变化很敏感！")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：薄壁堰示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 堰体
        weir_height = 1.0
        weir_width = 0.3
        ax1.add_patch(Rectangle((-weir_width, 0), weir_width, weir_height, 
                                facecolor='gray', edgecolor='black', linewidth=2))
        
        # 上游水体
        water_level = weir_height + H1
        ax1.fill_between([0, 3], weir_height, water_level, alpha=0.4, color='blue')
        ax1.plot([0, 3], [water_level, water_level], 'b-', linewidth=2, label='上游水面')
        ax1.plot([0, 3], [weir_height, weir_height], 'r--', linewidth=2, label='堰顶')
        
        # 过堰水流（抛物线形）
        x_flow = np.linspace(0, 1.5, 50)
        y_flow = weir_height - 0.5 * x_flow**1.5
        ax1.plot(x_flow, y_flow, 'b-', linewidth=3, label='水流轨迹')
        ax1.fill_between(x_flow, y_flow, weir_height, alpha=0.3, color='lightblue')
        
        # 标注
        ax1.annotate('', xy=(0, weir_height), xytext=(0, water_level),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(-0.4, (weir_height+water_level)/2, f'H={H1}m', fontsize=12, 
                color='red', fontweight='bold', rotation=90, va='center')
        
        ax1.annotate('', xy=(0, 0), xytext=(0, weir_height),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax1.text(-0.6, weir_height/2, 'P', fontsize=12, color='green', 
                fontweight='bold', rotation=90, va='center')
        
        # 流量箭头
        ax1.arrow(0.3, weir_height+0.1, 0.5, 0, head_width=0.08, head_length=0.15,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(0.8, weir_height+0.15, f'Q={Q1:.3f}m³/s', fontsize=11, color='blue')
        
        ax1.text(1.5, 0.2, '薄壁堰', fontsize=12, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 13 例题1：薄壁堰流示意图', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1, 3])
        ax1.set_ylim([0, 2])
        ax1.set_aspect('equal')
        
        # 子图2：Q-H关系曲线
        ax2 = plt.subplot(2, 2, 2)
        
        H_range = np.linspace(0.1, 1.0, 100)
        Q_range = m_eff * b * H_range**(3/2)
        
        ax2.plot(H_range, Q_range, 'b-', linewidth=3, label='Q = m\'bH^(3/2)')
        ax2.plot(H1, Q1, 'ro', markersize=12, label=f'工作点1 (H={H1}m, Q={Q1:.3f}m³/s)')
        ax2.plot(H2, Q2, 'gs', markersize=12, label=f'工作点2 (H={H2:.3f}m, Q={Q2:.3f}m³/s)')
        
        # 标注
        ax2.plot([H1, H1], [0, Q1], 'r:', linewidth=1)
        ax2.plot([0, H1], [Q1, Q1], 'r:', linewidth=1)
        ax2.plot([H2, H2], [0, Q2], 'g:', linewidth=1)
        ax2.plot([0, H2], [Q2, Q2], 'g:', linewidth=1)
        
        ax2.set_xlabel('堰顶水头 H (m)', fontsize=12)
        ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax2.set_title('流量-水头关系曲线', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 1.0])
        ax2.set_ylim([0, 2.5])
        
        # 子图3：流量系数影响
        ax3 = plt.subplot(2, 2, 3)
        
        m_values = [0.35, 0.40, 0.42, 0.45, 0.50]
        colors = ['purple', 'orange', 'red', 'green', 'blue']
        
        for m_val, color in zip(m_values, colors):
            m_eff_val = m_val * np.sqrt(2*self.g)
            Q_val = m_eff_val * b * H_range**(3/2)
            label = f'm={m_val}' if m_val != 0.42 else f'm={m_val} (设计值)'
            linewidth = 3 if m_val == 0.42 else 2
            ax3.plot(H_range, Q_val, color=color, linewidth=linewidth, label=label)
        
        ax3.set_xlabel('堰顶水头 H (m)', fontsize=12)
        ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax3.set_title('流量系数m的影响', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([0, 1.0])
        
        # 子图4：堰宽影响
        ax4 = plt.subplot(2, 2, 4)
        
        b_values = [1.0, 1.5, 2.0, 2.5, 3.0]
        
        for b_val in b_values:
            Q_val = m_eff * b_val * H_range**(3/2)
            label = f'b={b_val}m' if b_val != 2.0 else f'b={b_val}m (设计值)'
            linewidth = 3 if b_val == 2.0 else 2
            ax4.plot(H_range, Q_val, linewidth=linewidth, label=label)
        
        ax4.set_xlabel('堰顶水头 H (m)', fontsize=12)
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax4.set_title('堰宽b的影响', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim([0, 1.0])
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day13_weir_gate/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 写出薄壁堰流量公式 Q=mbH^(3/2) (2分) ⭐")
        print("✓ (2) 代入数据计算Q₁ (3分)")
        print("✓ (3) 由Q₂=1.5Q₁，求H₂=(Q₂/(m'b))^(2/3) (3分) ⭐")
        print("✓ (4) 分析Q与H的关系 Q∝H^(3/2) (2分)")
        print("✓ (5) 验证计算结果 (1分)")
        print("✓ (6) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 薄壁堰公式：Q = m × b × √(2g) × H^(3/2)")
        print("  ⚠️ 注意指数是3/2，不是2！")
        print("  ⚠️ 反求H时：H = (Q/(m√(2g)b))^(2/3)")
        print("  ⚠️ Q与H不是线性关系！")
        
        return {'Q1': Q1, 'H2': H2, 'Q2': Q2}
    
    def example_2_practical_weir(self):
        """
        例题2：实用堰流量计算（强化题）⭐⭐⭐⭐
        
        题目：实用堰（宽顶堰），堰宽b=4m，堰顶水头H=0.8m
              流量系数m=0.385，指数n=1.5
        求：(1) 通过流量Q
            (2) 与薄壁堰(m=0.42)比较
            (3) 淹没系数σ=0.85时的流量
        
        考点：实用堰公式，淹没出流
        难度：强化
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题2：实用堰流量计算（强化题）⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 4.0      # 堰宽 (m)
        H = 0.8      # 堰顶水头 (m)
        m = 0.385    # 流量系数
        n = 1.5      # 指数
        sigma = 0.85 # 淹没系数
        
        print(f"\n已知条件：")
        print(f"  实用堰宽度 b = {b:.1f} m")
        print(f"  堰顶水头 H = {H:.1f} m")
        print(f"  流量系数 m = {m:.3f}")
        print(f"  指数 n = {n}")
        print(f"  淹没系数 σ = {sigma:.2f}")
        
        # (1) 自由出流
        print(f"\n解题步骤：")
        print(f"\n(1) 自由出流流量：")
        print(f"    实用堰流量公式：")
        print(f"    Q = m × b × √(2g) × H^n")
        print(f"    ")
        
        Q_free = m * b * np.sqrt(2*self.g) * H**n
        
        print(f"    Q = {m} × {b} × √(2×{self.g:.2f}) × {H}^{n}")
        print(f"      = {m} × {b} × {np.sqrt(2*self.g):.3f} × {H**n:.4f}")
        print(f"      = {Q_free:.4f} m³/s ✓")
        
        # (2) 与薄壁堰比较
        print(f"\n(2) 与薄壁堰比较：")
        m_thin = 0.42
        Q_thin = m_thin * b * np.sqrt(2*self.g) * H**(3/2)
        
        print(f"    薄壁堰流量（m={m_thin}）：")
        print(f"    Q_薄壁 = {m_thin} × {b} × √(2×{self.g:.2f}) × {H}^(3/2)")
        print(f"          = {Q_thin:.4f} m³/s")
        print(f"    ")
        print(f"    比较：")
        print(f"    Q_实用/Q_薄壁 = {Q_free:.4f}/{Q_thin:.4f} = {Q_free/Q_thin:.4f}")
        
        if Q_free > Q_thin:
            print(f"    ")
            print(f"    ∵ Q_实用 > Q_薄壁")
            print(f"    ∴ 实用堰过流能力更强（堰型影响）✓")
        else:
            print(f"    ")
            print(f"    ∵ Q_实用 < Q_薄壁")
            print(f"    ∴ 实用堰过流能力较弱")
        
        # (3) 淹没出流
        print(f"\n(3) 淹没出流流量：")
        print(f"    淹没系数 σ = {sigma}")
        print(f"    ")
        print(f"    淹没出流公式：")
        print(f"    Q_淹没 = σ × Q_自由")
        
        Q_submerged = sigma * Q_free
        
        print(f"          = {sigma} × {Q_free:.4f}")
        print(f"          = {Q_submerged:.4f} m³/s ✓")
        print(f"    ")
        print(f"    流量减少：")
        print(f"    ΔQ = Q_自由 - Q_淹没")
        print(f"       = {Q_free:.4f} - {Q_submerged:.4f}")
        print(f"       = {Q_free - Q_submerged:.4f} m³/s")
        print(f"    相对减少：{(1-sigma)*100:.1f}%")
        
        # 绘图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 子图1：实用堰示意图（自由出流）
        weir_length = 1.5
        weir_height = 1.2
        
        # 堰体（宽顶）
        weir_x = [0, weir_length, weir_length, 0]
        weir_y = [0, 0, weir_height, weir_height]
        ax1.fill(weir_x, weir_y, color='gray', alpha=0.7, edgecolor='black', linewidth=2)
        
        # 上游水体
        water_level = weir_height + H
        ax1.fill_between([-1, 0], weir_height, water_level, alpha=0.4, color='blue')
        ax1.plot([-1, 0], [water_level, water_level], 'b-', linewidth=2)
        
        # 堰顶水流
        x_top = np.linspace(0, weir_length, 30)
        y_top = np.ones_like(x_top) * (weir_height + H*0.8)
        ax1.plot(x_top, y_top, 'b-', linewidth=2)
        ax1.fill_between(x_top, weir_height, y_top, alpha=0.3, color='lightblue')
        
        # 下游水流
        x_down = np.linspace(weir_length, weir_length+1.5, 30)
        y_down = weir_height - 0.3 * (x_down - weir_length)**1.2
        ax1.plot(x_down, y_down, 'b-', linewidth=3)
        ax1.fill_between(x_down, 0, y_down, alpha=0.3, color='lightblue')
        
        # 标注
        ax1.annotate('', xy=(-0.5, weir_height), xytext=(-0.5, water_level),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(-0.8, (weir_height+water_level)/2, f'H={H}m', fontsize=11, 
                color='red', rotation=90, va='center')
        
        ax1.text(0.7, weir_height/2, '实用堰\n(宽顶堰)', fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.text(2, 0.5, '自由出流', fontsize=11, color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 13 例题2：实用堰自由出流', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1.5, 3.5])
        ax1.set_ylim([0, 2.5])
        ax1.set_aspect('equal')
        
        # 子图2：淹没出流示意图
        # 堰体
        ax2.fill(weir_x, weir_y, color='gray', alpha=0.7, edgecolor='black', linewidth=2)
        
        # 上游水体
        ax2.fill_between([-1, 0], weir_height, water_level, alpha=0.4, color='blue')
        ax2.plot([-1, 0], [water_level, water_level], 'b-', linewidth=2)
        
        # 下游水位（淹没）
        h_downstream = weir_height + H * 0.6
        ax2.fill_between([weir_length, 3.5], 0, h_downstream, alpha=0.4, color='lightblue')
        ax2.plot([weir_length, 3.5], [h_downstream, h_downstream], 'c-', 
                linewidth=2, label='下游水位')
        
        # 堰顶水流（受淹没影响）
        y_top_sub = np.ones_like(x_top) * (weir_height + H*0.9)
        ax2.plot(x_top, y_top_sub, 'b-', linewidth=2)
        ax2.fill_between(x_top, weir_height, y_top_sub, alpha=0.3, color='lightblue')
        
        # 标注
        ax2.annotate('', xy=(weir_length+0.3, weir_height), 
                    xytext=(weir_length+0.3, h_downstream),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax2.text(weir_length+0.5, (weir_height+h_downstream)/2, 'h₂', 
                fontsize=11, color='green')
        
        ax2.text(2.5, 1.5, '淹没出流\nσ=0.85', fontsize=11, color='red', 
                fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightyellow'))
        
        ax2.set_xlabel('水平距离 (m)', fontsize=12)
        ax2.set_ylabel('高程 (m)', fontsize=12)
        ax2.set_title('实用堰淹没出流', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-1.5, 3.5])
        ax2.set_ylim([0, 2.5])
        ax2.set_aspect('equal')
        
        # 子图3：流量对比
        categories = ['薄壁堰', '实用堰\n(自由)', '实用堰\n(淹没)']
        flows = [Q_thin, Q_free, Q_submerged]
        colors_bar = ['#FF6B6B', '#4ECDC4', '#FFA07A']
        
        bars = ax3.bar(categories, flows, color=colors_bar, edgecolor='black', linewidth=2)
        
        for bar, flow in zip(bars, flows):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{flow:.3f}\nm³/s', ha='center', va='bottom', 
                    fontsize=11, fontweight='bold')
        
        ax3.set_ylabel('流量 (m³/s)', fontsize=12)
        ax3.set_title('不同堰型流量对比', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_ylim([0, max(flows)*1.2])
        
        # 子图4：淹没系数影响
        sigma_range = np.linspace(0.5, 1.0, 50)
        Q_sigma = sigma_range * Q_free
        
        ax4.plot(sigma_range, Q_sigma, 'b-', linewidth=3, label='Q = σQ₀')
        ax4.plot(sigma, Q_submerged, 'ro', markersize=12, 
                label=f'工作点 (σ={sigma}, Q={Q_submerged:.3f}m³/s)')
        ax4.axhline(y=Q_free, color='g', linestyle='--', linewidth=2, 
                   label=f'自由出流 Q₀={Q_free:.3f}m³/s')
        
        ax4.plot([sigma, sigma], [0, Q_submerged], 'r:', linewidth=1)
        ax4.plot([0.5, sigma], [Q_submerged, Q_submerged], 'r:', linewidth=1)
        
        ax4.set_xlabel('淹没系数 σ', fontsize=12)
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax4.set_title('淹没系数对流量的影响', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim([0.5, 1.0])
        ax4.set_ylim([0, Q_free*1.1])
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day13_weir_gate/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 实用堰公式 Q=mb√(2g)H^n (2分)")
        print("✓ (2) 计算自由出流Q (3分)")
        print("✓ (3) 计算薄壁堰流量 (2分)")
        print("✓ (4) 对比分析 (2分)")
        print("✓ (5) 淹没出流公式 Q=σQ₀ (2分) ⭐")
        print("✓ (6) 计算淹没流量 (3分)")
        print("✓ (7) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 实用堰指数n可能不是3/2（要看题目）")
        print("  ⚠️ 淹没出流：Q_淹没 = σ × Q_自由")
        print("  ⚠️ σ<1，淹没会减小流量")
        
        return {'Q_free': Q_free, 'Q_submerged': Q_submerged, 'Q_thin': Q_thin}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 13 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 薄壁堰流量公式：")
        print("     Q = m × b × √(2g) × H^(3/2)")
        print("     简化：Q = m' × b × H^(3/2)")
        print("     其中 m' = m√(2g) ≈ 1.86m")
        print("     ")
        print("  2. 实用堰流量公式：")
        print("     Q = m × b × √(2g) × H^n")
        print("     (n值根据堰型确定)")
        print("     ")
        print("  3. 淹没出流：")
        print("     Q_淹没 = σ × Q_自由")
        print("     (σ为淹没系数，<1)")
        print("     ")
        print("  4. 闸孔自由出流：")
        print("     Q = μ × b × e × √(2gH)")
        print("     ")
        print("  5. Q与H的关系：")
        print("     Q ∝ H^(3/2)（薄壁堰）")
        print("     Q ∝ H^(1/2)（闸孔）")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【堰流题】")
        print("  Step 1: 判断堰型（薄壁/实用）")
        print("  Step 2: 选择公式（注意指数）")
        print("  Step 3: 代入计算Q")
        print("  Step 4: 检查单位")
        print("  ")
        print("  【淹没出流题】")
        print("  Step 1: 计算自由出流Q₀")
        print("  Step 2: 应用Q=σQ₀")
        print("  Step 3: 分析流量减小")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：堰流公式指数记错（3/2 vs 1/2）")
        print("  ❌ 错误2：忘记√(2g)项")
        print("  ❌ 错误3：淹没系数σ>1（应该<1）")
        print("  ❌ 错误4：混淆薄壁堰和实用堰")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：薄壁堰公式必须背熟！")
        print("  ✓ 技巧2：注意H是堰顶水头，不是总水深")
        print("  ✓ 技巧3：淹没出流流量一定减小")
        print("  ✓ 技巧4：画示意图标注H")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能默写薄壁堰流量公式")
        print("  □ 理解Q∝H^(3/2)的关系")
        print("  □ 能计算淹没出流")
        print("  □ 能区分薄壁堰和实用堰")
        
        print("\n📅 明日预告：Day 14 - 第二周测试")
        print("  复习内容：Day 8-13全部内容")
        
        print("\n💪 今日格言：")
        print("  「堰流公式是送分题！Q=mbH^(3/2)背熟=12分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 13: 堰流与闸孔出流")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day13 = Day13WeirGate()
    
    # 例题1：薄壁堰
    result1 = day13.example_1_thin_plate_weir()
    
    # 例题2：实用堰
    result2 = day13.example_2_practical_weir()
    
    # 每日总结
    day13.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 13 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握薄壁堰流量公式")
    print(f"  ✓ 掌握实用堰流量公式")
    print(f"  ✓ 理解淹没出流")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n明日继续：Day 14 - 第二周测试")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
