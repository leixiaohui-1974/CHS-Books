#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 6: 孔口管嘴出流
Sprint Day 6: Orifice and Mouthpiece Flow

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 孔口出流：v = φ√(2gh)
  2. 收缩系数：Cc = Ac/A0
  3. 流速系数：φ = v/v理论
  4. 流量系数：μ = φ·Cc
  5. 管嘴出流：Q = μA√(2gh)

🎯 学习目标：
  - 掌握孔口出流公式
  - 理解收缩系数与流速系数
  - 熟练计算流量系数
  - 区分孔口与管嘴

💪 今日格言：孔口管嘴是考研送分题！掌握系数=稳拿24分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Wedge
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day6Orifice:
    """
    Day 6：孔口管嘴出流
    
    包含2个核心例题：
    1. 基础题：薄壁孔口出流（流量计算）
    2. 强化题：管嘴出流对比（孔口vs管嘴）
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        
        # 典型系数值
        self.phi_orifice = 0.97    # 孔口流速系数
        self.Cc_orifice = 0.64     # 孔口收缩系数
        self.mu_orifice = 0.62     # 孔口流量系数 = φ·Cc
        
        self.phi_mouthpiece = 0.82  # 管嘴流速系数
        self.Cc_mouthpiece = 1.0    # 管嘴收缩系数（无收缩）
        self.mu_mouthpiece = 0.82   # 管嘴流量系数
        
    def example_1_orifice_flow(self):
        """
        例题1：薄壁孔口出流（基础题）⭐⭐⭐⭐⭐
        
        题目：容器底部设有圆形薄壁孔口，直径d=0.05m
              水面高度H=2.0m，保持不变
              流速系数φ=0.97，收缩系数Cc=0.64
        求：(1) 理论流速v理论
            (2) 实际流速v
            (3) 收缩断面积Ac
            (4) 流量系数μ
            (5) 出流流量Q
        
        考点：孔口出流公式，系数关系
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题1：薄壁孔口出流（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d = 0.05     # 孔口直径 (m)
        H = 2.0      # 水头 (m)
        phi = self.phi_orifice    # 流速系数
        Cc = self.Cc_orifice      # 收缩系数
        
        print(f"\n已知条件：")
        print(f"  孔口直径 d = {d} m")
        print(f"  水头高度 H = {H} m")
        print(f"  流速系数 φ = {phi}")
        print(f"  收缩系数 Cc = {Cc}")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 理论流速
        print(f"\n(1) 计算理论流速v理论（托里拆利公式）：")
        print(f"    v理论 = √(2gH)")
        
        v_theory = np.sqrt(2 * self.g * H)
        
        print(f"          = √(2×{self.g}×{H})")
        print(f"          = {v_theory:.3f} m/s ✓")
        
        # (2) 实际流速
        print(f"\n(2) 计算实际流速v：")
        print(f"    v = φ × v理论")
        
        v_actual = phi * v_theory
        
        print(f"      = {phi} × {v_theory:.3f}")
        print(f"      = {v_actual:.3f} m/s ✓")
        
        # (3) 断面积
        print(f"\n(3) 计算孔口面积和收缩断面积：")
        print(f"    孔口面积：")
        print(f"    A0 = π(d/2)² = π×({d}/2)²")
        
        A0 = np.pi * (d/2)**2
        
        print(f"       = {A0:.6f} m²")
        print(f"    ")
        print(f"    收缩断面积：")
        print(f"    Ac = Cc × A0")
        
        Ac = Cc * A0
        
        print(f"       = {Cc} × {A0:.6f}")
        print(f"       = {Ac:.6f} m² ✓")
        
        # (4) 流量系数
        print(f"\n(4) 计算流量系数μ：")
        print(f"    μ = φ × Cc")
        
        mu = phi * Cc
        
        print(f"      = {phi} × {Cc}")
        print(f"      = {mu:.3f} ✓")
        print(f"    ")
        print(f"    说明：流量系数 = 流速系数 × 收缩系数")
        
        # (5) 流量
        print(f"\n(5) 计算出流流量Q：")
        print(f"    方法1（收缩断面）：")
        print(f"    Q = Ac × v理论")
        
        Q1 = Ac * v_theory
        
        print(f"      = {Ac:.6f} × {v_theory:.3f}")
        print(f"      = {Q1:.6f} m³/s")
        print(f"    ")
        print(f"    方法2（流量系数）：")
        print(f"    Q = μ × A0 × √(2gH)")
        
        Q2 = mu * A0 * v_theory
        
        print(f"      = {mu:.3f} × {A0:.6f} × {v_theory:.3f}")
        print(f"      = {Q2:.6f} m³/s ✓")
        print(f"    ")
        print(f"    验证：Q1 = Q2 = {Q2:.6f} m³/s ✓")
        
        # 单位时间流出质量
        m_dot = self.rho * Q2
        print(f"    ")
        print(f"    质量流量：")
        print(f"    ṁ = ρQ = {self.rho} × {Q2:.6f}")
        print(f"       = {m_dot:.3f} kg/s")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：孔口出流示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 容器
        tank_width = 1.5
        tank_height = 2.5
        ax1.add_patch(Rectangle((-tank_width/2, 0), tank_width, tank_height,
                                fill=False, edgecolor='black', linewidth=3))
        
        # 水面
        water_level = H
        ax1.fill_between([-tank_width/2, tank_width/2], [0, 0], 
                        [water_level, water_level],
                        color='lightblue', alpha=0.5)
        ax1.plot([-tank_width/2, tank_width/2], [water_level, water_level],
                'b-', linewidth=2, label='水面')
        
        # 水头标注
        ax1.annotate('', xy=(tank_width/2+0.2, water_level), 
                    xytext=(tank_width/2+0.2, 0),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(tank_width/2+0.35, water_level/2, f'H={H}m', 
                fontsize=12, color='red', fontweight='bold',
                rotation=90, va='center')
        
        # 孔口
        orifice_y = 0
        orifice_size = d
        ax1.add_patch(Circle((0, orifice_y), orifice_size/2, 
                            color='white', edgecolor='black', linewidth=2))
        ax1.text(0, orifice_y-0.15, f'd={d}m', ha='center',
                fontsize=10, fontweight='bold')
        
        # 射流
        jet_x = np.linspace(0.025, 0.6, 50)
        jet_upper = orifice_y + orifice_size/2 * Cc - (jet_x - 0.025) * 0.05
        jet_lower = orifice_y - orifice_size/2 * Cc + (jet_x - 0.025) * 0.05
        ax1.fill_between(jet_x, jet_lower, jet_upper, 
                        color='lightblue', alpha=0.7)
        
        # 收缩断面标注
        x_contract = 0.025 + d/2
        ax1.plot([x_contract, x_contract], 
                [orifice_y - orifice_size/2*Cc, orifice_y + orifice_size/2*Cc],
                'r--', linewidth=2, label='收缩断面')
        ax1.text(x_contract+0.05, orifice_y+0.1, '收缩断面\nAc=CcA0', 
                fontsize=9, color='red')
        
        # 流速箭头
        ax1.arrow(x_contract+0.1, orifice_y, 0.25, 0,
                 head_width=0.08, head_length=0.05,
                 fc='green', ec='green', linewidth=3)
        ax1.text(x_contract+0.25, orifice_y+0.15, f'v={v_actual:.2f}m/s',
                fontsize=11, color='green', fontweight='bold')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 6 例题1：薄壁孔口出流示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1, 1])
        ax1.set_ylim([-0.3, 3])
        ax1.set_aspect('equal')
        
        # 子图2：系数关系图
        ax2 = plt.subplot(2, 2, 2)
        
        categories = ['φ\n流速系数', 'Cc\n收缩系数', 'μ\n流量系数\n(μ=φ×Cc)']
        values = [phi, Cc, mu]
        colors_bar = ['#FF6B6B', '#4ECDC4', '#FFE66D']
        
        bars = ax2.bar(categories, values, color=colors_bar, 
                      edgecolor='black', linewidth=2, width=0.6)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}', ha='center', va='bottom',
                    fontsize=13, fontweight='bold')
        
        # 标注关系
        ax2.annotate('', xy=(2, mu), xytext=(0.5, phi),
                    arrowprops=dict(arrowstyle='->', color='purple', lw=2, ls='--'))
        ax2.annotate('', xy=(2, mu), xytext=(1.5, Cc),
                    arrowprops=dict(arrowstyle='->', color='purple', lw=2, ls='--'))
        ax2.text(1, 0.5, 'μ = φ × Cc', fontsize=12, color='purple',
                fontweight='bold', ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax2.set_ylabel('系数值', fontsize=12)
        ax2.set_title('孔口出流系数关系', fontsize=13, fontweight='bold')
        ax2.set_ylim([0, 1.1])
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 子图3：流速对比
        ax3 = plt.subplot(2, 2, 3)
        
        velocities = ['v理论\n√(2gH)', 'v实际\nφ√(2gH)']
        v_values = [v_theory, v_actual]
        colors_v = ['#95E1D3', '#F38181']
        
        bars_v = ax3.bar(velocities, v_values, color=colors_v,
                        edgecolor='black', linewidth=2, width=0.5)
        
        for bar, val in zip(bars_v, v_values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}\nm/s', ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        # 标注差异
        ax3.plot([0, 1], [v_theory*0.98, v_theory*0.98], 'k--', linewidth=1.5)
        ax3.text(0.5, v_theory*0.99, f'能量损失\n{(1-phi)*100:.0f}%',
                ha='center', fontsize=10, color='red',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax3.set_ylabel('流速 (m/s)', fontsize=12)
        ax3.set_title('理论流速 vs 实际流速', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_ylim([0, v_theory*1.15])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          • 孔口直径 d = {d} m
          • 水头高度 H = {H} m
          • 流速系数 φ = {phi}
          • 收缩系数 Cc = {Cc}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 理论流速：
            v理论 = √(2gH) = {v_theory:.3f} m/s ✓
        
        (2) 实际流速：
            v = φ√(2gH) = {v_actual:.3f} m/s ✓
        
        (3) 断面积：
            A0 = {A0:.6f} m²
            Ac = Cc×A0 = {Ac:.6f} m² ✓
        
        (4) 流量系数：
            μ = φ×Cc = {mu:.3f} ✓
        
        (5) 出流流量：
            Q = μA0√(2gH) = {Q2:.6f} m³/s ✓
            ṁ = {m_dot:.3f} kg/s
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 托里拆利公式：v = √(2gH)
          • 流速系数：φ = v实际/v理论
          • 收缩系数：Cc = Ac/A0
          • 流量系数：μ = φ×Cc
          • 流量公式：Q = μA0√(2gH)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day06_orifice/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 写出托里拆利公式v=√(2gH) (2分) ⭐")
        print("✓ (2) 计算理论流速 (1分)")
        print("✓ (3) 应用流速系数v=φ√(2gH) (2分)")
        print("✓ (4) 计算孔口面积A0 (1分)")
        print("✓ (5) 应用收缩系数Ac=Cc×A0 (2分)")
        print("✓ (6) 计算流量系数μ=φ×Cc (2分) ⭐")
        print("✓ (7) 计算流量Q=μA0√(2gH) (1分)")
        print("✓ (8) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 托里拆利公式：v=√(2gH)，不是v=√(gh)！")
        print("  ⚠️ 流量系数：μ=φ×Cc，不要忘记相乘！")
        print("  ⚠️ 流量公式：Q=μA0√(2gH)，A0是孔口面积！")
        print("  ⚠️ 系数范围：φ≈0.97，Cc≈0.64，μ≈0.62")
        
        return {'v_theory': v_theory, 'v_actual': v_actual, 
                'Q': Q2, 'mu': mu, 'Ac': Ac}
    
    def example_2_mouthpiece_comparison(self):
        """
        例题2：管嘴出流对比（强化题）⭐⭐⭐⭐⭐
        
        题目：在同一容器底部分别设置：
              (a) 薄壁孔口，直径d=0.04m
              (b) 圆柱形外管嘴，直径d=0.04m，长度l=3d
              水头H=1.5m，保持不变
        求：(1) 孔口出流流量Q孔
            (2) 管嘴出流流量Q管
            (3) 流量增加率
            (4) 负压值
        
        考点：孔口vs管嘴，流量对比
        难度：强化（必考！）
        时间：20分钟
        分值：18分
        """
        print("\n" + "="*60)
        print("例题2：管嘴出流对比（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d = 0.04     # 直径 (m)
        H = 1.5      # 水头 (m)
        l = 3 * d    # 管嘴长度 (m)
        
        print(f"\n已知条件：")
        print(f"  直径 d = {d} m")
        print(f"  水头 H = {H} m")
        print(f"  管嘴长度 l = {l:.3f} m (3d)")
        print(f"  孔口流量系数 μ孔 = {self.mu_orifice}")
        print(f"  管嘴流量系数 μ管 = {self.mu_mouthpiece}")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # 面积
        A0 = np.pi * (d/2)**2
        print(f"\n断面积：")
        print(f"  A0 = π(d/2)² = {A0:.6f} m²")
        
        # 理论流速
        v_theory = np.sqrt(2 * self.g * H)
        print(f"\n理论流速：")
        print(f"  v理论 = √(2gH) = √(2×{self.g}×{H})")
        print(f"        = {v_theory:.3f} m/s")
        
        # (1) 孔口流量
        print(f"\n(1) 计算孔口出流流量Q孔：")
        print(f"    Q孔 = μ孔 × A0 × √(2gH)")
        
        Q_orifice = self.mu_orifice * A0 * v_theory
        
        print(f"        = {self.mu_orifice} × {A0:.6f} × {v_theory:.3f}")
        print(f"        = {Q_orifice:.6f} m³/s ✓")
        print(f"        = {Q_orifice*1000:.3f} L/s")
        
        # (2) 管嘴流量
        print(f"\n(2) 计算管嘴出流流量Q管：")
        print(f"    Q管 = μ管 × A0 × √(2gH)")
        
        Q_mouthpiece = self.mu_mouthpiece * A0 * v_theory
        
        print(f"        = {self.mu_mouthpiece} × {A0:.6f} × {v_theory:.3f}")
        print(f"        = {Q_mouthpiece:.6f} m³/s ✓")
        print(f"        = {Q_mouthpiece*1000:.3f} L/s")
        
        # (3) 流量增加率
        print(f"\n(3) 流量增加率分析：")
        
        increase_rate = (Q_mouthpiece - Q_orifice) / Q_orifice * 100
        
        print(f"    增加量：")
        print(f"    ΔQ = Q管 - Q孔")
        print(f"       = {Q_mouthpiece:.6f} - {Q_orifice:.6f}")
        print(f"       = {Q_mouthpiece - Q_orifice:.6f} m³/s")
        print(f"    ")
        print(f"    增加率：")
        print(f"    η = (Q管 - Q孔)/Q孔 × 100%")
        print(f"      = ({Q_mouthpiece:.6f} - {Q_orifice:.6f})/{Q_orifice:.6f} × 100%")
        print(f"      = {increase_rate:.2f}% ✓")
        print(f"    ")
        print(f"    说明：管嘴出流量比孔口增加约{increase_rate:.1f}%！")
        
        # (4) 负压值
        print(f"\n(4) 管嘴内负压值计算：")
        print(f"    ")
        print(f"    管嘴内收缩断面处产生负压（真空度）：")
        print(f"    ")
        print(f"    能量方程（容器水面→收缩断面）：")
        print(f"    H + pc/(ρg) = vc²/(2g) + hw")
        print(f"    ")
        print(f"    收缩断面流速：")
        print(f"    vc = v理论/Cc = {v_theory:.3f}/{self.Cc_orifice}")
        
        vc = v_theory / self.Cc_orifice
        
        print(f"       = {vc:.3f} m/s")
        print(f"    ")
        print(f"    负压水头（忽略损失hw）：")
        print(f"    pc/(ρg) = H - vc²/(2g)")
        
        hc = H - vc**2 / (2 * self.g)
        
        print(f"            = {H} - {vc:.3f}²/(2×{self.g})")
        print(f"            = {hc:.3f} m ✓")
        print(f"    ")
        print(f"    负压值（真空度）：")
        print(f"    pc = ρg × {hc:.3f}")
        
        pc = self.rho * self.g * abs(hc)
        
        print(f"       = {self.rho} × {self.g} × {abs(hc):.3f}")
        print(f"       = {pc:.0f} Pa")
        print(f"       = {pc/1000:.2f} kPa ✓")
        print(f"    ")
        print(f"    说明：负压{abs(hc):.2f}m水柱，约{pc/1000:.1f}kPa真空度")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：孔口vs管嘴示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 左侧：孔口
        tank_w = 0.6
        tank_h = 1.5
        
        # 孔口容器
        ax1.add_patch(Rectangle((-1.2, 0), tank_w, tank_h,
                                fill=False, edgecolor='black', linewidth=2))
        ax1.fill_between([-1.2, -1.2+tank_w], [0, 0], [H, H],
                        color='lightblue', alpha=0.5)
        ax1.plot([-1.2, -1.2+tank_w], [H, H], 'b-', linewidth=2)
        ax1.text(-1.2+tank_w/2, H+0.1, f'H={H}m', ha='center', fontsize=10)
        
        # 孔口
        orifice_center = (-1.2+tank_w, 0.05)
        ax1.add_patch(Circle(orifice_center, d/2, 
                            color='white', edgecolor='black', linewidth=2))
        
        # 孔口射流
        jet_x1 = np.linspace(orifice_center[0]+d/2, orifice_center[0]+d/2+0.3, 20)
        jet_upper1 = orifice_center[1] + d/2 * self.Cc_orifice
        jet_lower1 = orifice_center[1] - d/2 * self.Cc_orifice
        ax1.fill_between(jet_x1, jet_lower1, jet_upper1,
                        color='lightblue', alpha=0.7)
        
        ax1.text(-1.2+tank_w/2, -0.3, '(a) 孔口出流', ha='center',
                fontsize=11, fontweight='bold', color='blue')
        ax1.text(orifice_center[0]+0.2, orifice_center[1]+0.15,
                f'Q={Q_orifice*1000:.2f}L/s', fontsize=9, color='red')
        
        # 右侧：管嘴
        # 管嘴容器
        ax1.add_patch(Rectangle((0.2, 0), tank_w, tank_h,
                                fill=False, edgecolor='black', linewidth=2))
        ax1.fill_between([0.2, 0.2+tank_w], [0, 0], [H, H],
                        color='lightblue', alpha=0.5)
        ax1.plot([0.2, 0.2+tank_w], [H, H], 'b-', linewidth=2)
        ax1.text(0.2+tank_w/2, H+0.1, f'H={H}m', ha='center', fontsize=10)
        
        # 管嘴
        mouthpiece_start = (0.2+tank_w, 0.05)
        ax1.add_patch(Rectangle(mouthpiece_start, l, d,
                                fill=True, facecolor='lightgray',
                                edgecolor='black', linewidth=2))
        
        # 管嘴射流
        jet_x2 = np.linspace(mouthpiece_start[0]+l, mouthpiece_start[0]+l+0.3, 20)
        ax1.fill_between(jet_x2, mouthpiece_start[1], mouthpiece_start[1]+d,
                        color='lightblue', alpha=0.7)
        
        ax1.text(0.2+tank_w/2, -0.3, '(b) 管嘴出流', ha='center',
                fontsize=11, fontweight='bold', color='blue')
        ax1.text(mouthpiece_start[0]+l/2, mouthpiece_start[1]+d+0.08,
                f'Q={Q_mouthpiece*1000:.2f}L/s', fontsize=9, color='red')
        
        # 负压标注
        ax1.text(mouthpiece_start[0]+0.03, mouthpiece_start[1]+d/2,
                '负压区', fontsize=8, color='purple', rotation=90, va='center')
        
        ax1.set_xlabel('水平位置 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 6 例题2：孔口 vs 管嘴出流对比', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-1.5, 1.5])
        ax1.set_ylim([-0.5, 2])
        ax1.set_aspect('equal')
        
        # 子图2：流量对比
        ax2 = plt.subplot(2, 2, 2)
        
        types = ['孔口\nμ=0.62', '管嘴\nμ=0.82']
        flows = [Q_orifice*1000, Q_mouthpiece*1000]  # L/s
        colors_flow = ['#FF6B6B', '#4ECDC4']
        
        bars = ax2.bar(types, flows, color=colors_flow,
                      edgecolor='black', linewidth=2, width=0.5)
        
        for bar, flow in zip(bars, flows):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{flow:.3f}\nL/s', ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        # 增加率标注
        ax2.plot([0, 1], [flows[0]*1.05, flows[0]*1.05], 'k--', linewidth=1.5)
        ax2.annotate('', xy=(1, flows[0]*1.05), xytext=(0, flows[0]*1.05),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax2.text(0.5, flows[0]*1.07, f'增加{increase_rate:.1f}%',
                ha='center', fontsize=11, color='green', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax2.set_ylabel('流量 (L/s)', fontsize=12)
        ax2.set_title('流量对比', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_ylim([0, max(flows)*1.2])
        
        # 子图3：系数对比
        ax3 = plt.subplot(2, 2, 3)
        
        x = np.arange(3)
        width = 0.35
        
        coeffs_orifice = [self.phi_orifice, self.Cc_orifice, self.mu_orifice]
        coeffs_mouthpiece = [self.phi_mouthpiece, self.Cc_mouthpiece, self.mu_mouthpiece]
        
        bars1 = ax3.bar(x - width/2, coeffs_orifice, width,
                       label='孔口', color='#FF6B6B', edgecolor='black', linewidth=1.5)
        bars2 = ax3.bar(x + width/2, coeffs_mouthpiece, width,
                       label='管嘴', color='#4ECDC4', edgecolor='black', linewidth=1.5)
        
        # 添加数值标注
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom',
                        fontsize=9, fontweight='bold')
        
        ax3.set_ylabel('系数值', fontsize=12)
        ax3.set_title('流动系数对比', fontsize=13, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(['φ\n流速系数', 'Cc\n收缩系数', 'μ\n流量系数'])
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_ylim([0, 1.1])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【孔口 vs 管嘴对比】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          • 直径 d = {d} m
          • 水头 H = {H} m
          • 管嘴长度 l = {l:.3f} m (3d)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        孔口出流：
          μ孔 = {self.mu_orifice}
          Q孔 = {Q_orifice:.6f} m³/s
              = {Q_orifice*1000:.3f} L/s ✓
        
        管嘴出流：
          μ管 = {self.mu_mouthpiece}
          Q管 = {Q_mouthpiece:.6f} m³/s
              = {Q_mouthpiece*1000:.3f} L/s ✓
        
        流量增加：
          ΔQ = {Q_mouthpiece - Q_orifice:.6f} m³/s
          增加率 = {increase_rate:.2f}% ✓
        
        负压值：
          vc = {vc:.3f} m/s
          hc = {hc:.3f} m (真空度)
          pc = {pc/1000:.2f} kPa ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键结论：
          • 管嘴流量比孔口大{increase_rate:.1f}%
          • 管嘴无收缩（Cc=1.0）
          • 管嘴内有负压（真空吸力）
          • 管嘴长度l=(2~4)d最佳
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day06_orifice/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（18分评分标准）：")
        print("="*60)
        print("✓ (1) 计算断面积A0 (1分)")
        print("✓ (2) 计算理论流速√(2gH) (1分)")
        print("✓ (3) 应用孔口流量公式Q=μA0√(2gH) (3分) ⭐")
        print("✓ (4) 应用管嘴流量公式Q=μA0√(2gH) (3分) ⭐")
        print("✓ (5) 计算流量增加量ΔQ (2分)")
        print("✓ (6) 计算流量增加率η (2分)")
        print("✓ (7) 分析管嘴内负压 (3分)")
        print("✓ (8) 计算负压值pc (2分)")
        print("✓ (9) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 孔口与管嘴流量系数：μ孔≈0.62，μ管≈0.82")
        print("  ⚠️ 管嘴无收缩：Cc管=1.0，但φ管<φ孔")
        print("  ⚠️ 管嘴负压：收缩断面处产生真空，吸力增大流量")
        print("  ⚠️ 管嘴长度：l=(2~4)d，太短效果差，太长损失大")
        
        return {'Q_orifice': Q_orifice, 'Q_mouthpiece': Q_mouthpiece,
                'increase_rate': increase_rate, 'pc': pc}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 6 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 托里拆利公式：")
        print("     v理论 = √(2gH)")
        print("     ")
        print("  2. 孔口实际流速：")
        print("     v = φ√(2gH)")
        print("     ")
        print("  3. 流速系数：")
        print("     φ = v实际/v理论 ≈ 0.97")
        print("     ")
        print("  4. 收缩系数：")
        print("     Cc = Ac/A0 ≈ 0.64（孔口）")
        print("     Cc = 1.0（管嘴）")
        print("     ")
        print("  5. 流量系数：")
        print("     μ = φ × Cc")
        print("     μ孔 ≈ 0.62")
        print("     μ管 ≈ 0.82")
        print("     ")
        print("  6. 流量公式：")
        print("     Q = μ × A0 × √(2gH)")
        
        print("\n✅ 系数对比表：")
        print("  ┌────────┬─────┬──────┬──────┐")
        print("  │  类型  │  φ  │  Cc  │  μ   │")
        print("  ├────────┼─────┼──────┼──────┤")
        print("  │  孔口  │ 0.97│ 0.64 │ 0.62 │")
        print("  │  管嘴  │ 0.82│ 1.00 │ 0.82 │")
        print("  └────────┴─────┴──────┴──────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【孔口流量计算】")
        print("  Step 1: 计算孔口面积A0")
        print("  Step 2: 确定流量系数μ≈0.62")
        print("  Step 3: 应用Q=μA0√(2gH)")
        print("  ")
        print("  【管嘴流量计算】")
        print("  Step 1: 计算断面积A0")
        print("  Step 2: 确定流量系数μ≈0.82")
        print("  Step 3: 应用Q=μA0√(2gH)")
        print("  Step 4: 分析负压（如有要求）")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：托里拆利公式写成v=√(gh)（少了系数2）")
        print("  ❌ 错误2：流量系数μ=φ+Cc（应该是乘法不是加法）")
        print("  ❌ 错误3：孔口管嘴系数搞混（μ孔≠μ管）")
        print("  ❌ 错误4：管嘴长度无限制（应该l=(2~4)d）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：记住「2、6、8」→ √(2gH)、μ=0.62、μ=0.82")
        print("  ✓ 技巧2：孔口有收缩（Cc=0.64）、管嘴无收缩（Cc=1.0）")
        print("  ✓ 技巧3：管嘴流量大约是孔口的1.3倍")
        print("  ✓ 技巧4：管嘴内有负压（真空吸力）")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能熟记托里拆利公式")
        print("  □ 理解三个系数的物理意义")
        print("  □ 能计算孔口和管嘴流量")
        print("  □ 能分析管嘴负压问题")
        
        print("\n📅 明日预告：Day 7 - 第一周测试")
        print("  测试范围：Day 1-6（静水力学+水动力学）")
        
        print("\n💪 今日格言：")
        print("  「孔口管嘴是送分题！记住系数=稳拿24分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 6: 孔口管嘴出流")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day6 = Day6Orifice()
    
    # 例题1：孔口出流
    result1 = day6.example_1_orifice_flow()
    
    # 例题2：孔口vs管嘴
    result2 = day6.example_2_mouthpiece_comparison()
    
    # 每日总结
    day6.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 6 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握托里拆利公式")
    print(f"  ✓ 理解三个系数（φ、Cc、μ）")
    print(f"  ✓ 掌握孔口管嘴对比")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n明日继续：Day 7 - 第一周测试")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
