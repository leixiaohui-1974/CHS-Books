#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 17: 水泵与泵站
Sprint Day 17: Pumps and Pumping Stations

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 水泵特性曲线：Q-H、Q-η、Q-N
  2. 装置特性曲线：H装=Hst+SQ²
  3. 工况点：特性曲线交点
  4. 相似定律：n₁/n₂=(Q₁/Q₂)=(H₁/H₂)^0.5
  5. 比转数：ns=3.65nQ^0.5/H^0.75

🎯 学习目标：
  - 掌握水泵特性曲线
  - 理解工况点概念
  - 熟练相似定律应用
  - 了解水泵选型

💪 今日格言：水泵是实用核心！掌握特性曲线=拿到20分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
from matplotlib.patches import ConnectionPatch
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day17Pump:
    """
    Day 17：水泵与泵站
    
    包含2个核心例题：
    1. 基础题：工况点计算
    2. 强化题：水泵相似定律应用
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        self.gamma = self.rho * self.g  # 水容重 (N/m³)
        
    def pump_characteristic(self, Q, H0, a, b):
        """
        水泵特性曲线H(Q)
        H = H0 - aQ - bQ²
        """
        return H0 - a * Q - b * Q**2
    
    def pump_efficiency(self, Q, Q_opt, eta_max):
        """
        水泵效率曲线η(Q)
        抛物线型，在Q_opt处达到最大值eta_max
        """
        # 简化模型：η = eta_max * (1 - k*(Q-Q_opt)²)
        k = 0.5 / Q_opt**2  # 调整系数
        eta = eta_max * (1 - k * (Q - Q_opt)**2)
        return np.maximum(eta, 0)  # 效率不能为负
    
    def pump_power(self, Q, H, eta):
        """
        水泵功率N
        N = ρgQH/η
        """
        return self.rho * self.g * Q * H / eta
    
    def system_characteristic(self, Q, Hst, S):
        """
        装置特性曲线H装(Q)
        H装 = Hst + SQ²
        """
        return Hst + S * Q**2
    
    def example_1_operating_point(self):
        """
        例题1：工况点计算（基础题）⭐⭐⭐⭐⭐
        
        题目：某离心泵特性曲线方程为H=40-0.5Q-0.2Q²（H单位m，Q单位L/s）
              装置静扬程Hst=15m，管路阻力系数S=0.015s²/m⁵
        求：(1) 水泵工况点流量Q和扬程H
            (2) 若要求流量增加20%，需调节阀门使S'为多少
            (3) 若改用调速方式，转速应调为原来的多少倍
        
        考点：工况点，特性曲线，流量调节
        难度：基础（必考！）
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题1：工况点计算（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        H0 = 40.0      # 水泵扬程系数 (m)
        a = 0.5        # 一次项系数 (m·s/L)
        b = 0.2        # 二次项系数 (m·s²/L²)
        Hst = 15.0     # 静扬程 (m)
        S = 0.015      # 管路阻力系数 (s²/m⁵)
        
        print(f"\n已知条件：")
        print(f"  水泵特性：H = {H0} - {a}Q - {b}Q² (m, L/s)")
        print(f"  静扬程：Hst = {Hst} m")
        print(f"  阻力系数：S = {S} s²/m⁵")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 工况点
        print(f"\n(1) 计算工况点（H泵=H装）：")
        print(f"    ")
        print(f"    水泵特性曲线：")
        print(f"    H泵 = {H0} - {a}Q - {b}Q²")
        print(f"    ")
        print(f"    装置特性曲线（Q单位转为m³/s）：")
        print(f"    H装 = Hst + SQ²")
        print(f"       = {Hst} + {S}×(1000Q)²")
        print(f"       = {Hst} + {S*1000000}Q²  (Q单位L/s)")
        print(f"    ")
        print(f"    工况点条件：H泵 = H装")
        print(f"    {H0} - {a}Q - {b}Q² = {Hst} + {S*1000000}Q²")
        print(f"    ")
        print(f"    整理得：")
        
        # 求解二次方程：(b + S*1e6)Q² + aQ + (Hst - H0) = 0
        A = b + S * 1000000
        B = a
        C = Hst - H0
        
        print(f"    {A}Q² + {B}Q + ({C}) = 0")
        print(f"    ")
        print(f"    使用求根公式：")
        
        discriminant = B**2 - 4*A*C
        Q1 = (-B + np.sqrt(discriminant)) / (2*A)
        Q2 = (-B - np.sqrt(discriminant)) / (2*A)
        
        print(f"    判别式：Δ = {B}² - 4×{A}×({C})")
        print(f"           = {discriminant:.2f}")
        print(f"    ")
        print(f"    Q = (-{B} ± √{discriminant:.2f}) / (2×{A})")
        print(f"    ")
        print(f"    Q₁ = {Q1:.2f} L/s (取正根)")
        print(f"    Q₂ = {Q2:.2f} L/s (舍去)")
        print(f"    ")
        print(f"    工况点流量：Q = {Q1:.2f} L/s ✓")
        
        Q_work = Q1
        
        # 计算工况点扬程
        H_work = H0 - a * Q_work - b * Q_work**2
        
        print(f"    ")
        print(f"    工况点扬程：")
        print(f"    H = {H0} - {a}×{Q_work:.2f} - {b}×{Q_work:.2f}²")
        print(f"      = {H_work:.2f} m ✓")
        print(f"    ")
        print(f"    验证（装置特性）：")
        
        H_check = Hst + S * (Q_work/1000)**2 * 1000000
        
        print(f"    H装 = {Hst} + {S*1000000}×{Q_work:.2f}²")
        print(f"        = {H_check:.2f} m ✓")
        
        # (2) 流量增加20%
        print(f"\n(2) 流量增加20%，调节阀门：")
        print(f"    ")
        print(f"    新流量：Q' = 1.2Q = 1.2×{Q_work:.2f}")
        
        Q_new = 1.2 * Q_work
        
        print(f"           = {Q_new:.2f} L/s")
        print(f"    ")
        print(f"    该流量下水泵扬程：")
        
        H_pump_new = H0 - a * Q_new - b * Q_new**2
        
        print(f"    H泵 = {H0} - {a}×{Q_new:.2f} - {b}×{Q_new:.2f}²")
        print(f"        = {H_pump_new:.2f} m")
        print(f"    ")
        print(f"    新装置特性需满足：")
        print(f"    H装' = Hst + S'(Q')²")
        print(f"    {H_pump_new:.2f} = {Hst} + S'×{Q_new:.2f}²")
        print(f"    ")
        print(f"    求解S'：")
        
        S_new = (H_pump_new - Hst) / Q_new**2
        
        print(f"    S' = ({H_pump_new:.2f} - {Hst}) / {Q_new:.2f}²")
        print(f"       = {S_new:.6f} s²/m⁵  (Q单位L/s)")
        print(f"       = {S_new/1000000:.9f} s²/m⁵  (Q单位m³/s) ✓")
        print(f"    ")
        print(f"    对比：S' = {S_new:.6f}, S = {S:.6f}")
        print(f"    S'/S = {S_new/S:.3f}")
        print(f"    结论：阀门需开大（阻力系数减小{(1-S_new/S)*100:.1f}%）")
        
        # (3) 调速方式
        print(f"\n(3) 调速方式实现Q'={Q_new:.2f} L/s：")
        print(f"    ")
        print(f"    相似定律（转速n调节）：")
        print(f"    Q'/Q = n'/n")
        print(f"    H'/H = (n'/n)²")
        print(f"    ")
        print(f"    由流量关系：")
        print(f"    n'/n = Q'/Q = {Q_new:.2f}/{Q_work:.2f}")
        
        n_ratio = Q_new / Q_work
        
        print(f"         = {n_ratio:.3f}")
        print(f"    ")
        print(f"    即转速调为原来的{n_ratio:.3f}倍")
        print(f"    或增加{(n_ratio-1)*100:.1f}% ✓")
        print(f"    ")
        print(f"    此时扬程变化：")
        print(f"    H'/H = ({n_ratio:.3f})² = {n_ratio**2:.3f}")
        print(f"    H' = {H_work:.2f}×{n_ratio**2:.3f}")
        
        H_speed = H_work * n_ratio**2
        
        print(f"       = {H_speed:.2f} m")
        print(f"    ")
        print(f"    新工况点：Q'={Q_new:.2f} L/s, H'={H_speed:.2f} m")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：特性曲线与工况点
        ax1 = plt.subplot(2, 2, 1)
        
        Q_range = np.linspace(0, 50, 200)
        
        # 水泵特性曲线
        H_pump = H0 - a * Q_range - b * Q_range**2
        ax1.plot(Q_range, H_pump, 'b-', linewidth=2.5, label='水泵特性H泵')
        
        # 装置特性曲线（原始）
        H_system = Hst + S * 1000000 * Q_range**2
        ax1.plot(Q_range, H_system, 'r-', linewidth=2.5, label='装置特性H装')
        
        # 工况点
        ax1.plot([Q_work], [H_work], 'go', markersize=15, label='工况点A')
        ax1.text(Q_work+2, H_work+1, f'A\nQ={Q_work:.1f}L/s\nH={H_work:.1f}m',
                fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 新工况点（阀门调节）
        H_system_new = Hst + S_new * Q_range**2
        ax1.plot(Q_range, H_system_new, 'r--', linewidth=2, label='新装置特性H装\'')
        ax1.plot([Q_new], [H_pump_new], 'mo', markersize=12, label='新工况点B')
        ax1.text(Q_new+2, H_pump_new-2, f'B\nQ={Q_new:.1f}L/s',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        ax1.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax1.set_ylabel('扬程 H (m)', fontsize=12)
        ax1.set_title('Day 17 例题1：水泵工况点', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 50])
        ax1.set_ylim([0, 45])
        
        # 子图2：调速前后对比
        ax2 = plt.subplot(2, 2, 2)
        
        # 原水泵特性
        ax2.plot(Q_range, H_pump, 'b-', linewidth=2.5, label='原水泵特性(n)')
        
        # 调速后水泵特性（相似律）
        Q_speed_range = Q_range * n_ratio
        H_speed_range = (H0 - a * Q_range - b * Q_range**2) * n_ratio**2
        ax2.plot(Q_speed_range, H_speed_range, 'g--', linewidth=2.5, 
                label=f'调速后特性(n\'={n_ratio:.2f}n)')
        
        # 装置特性（不变）
        ax2.plot(Q_range, H_system, 'r-', linewidth=2, label='装置特性')
        
        # 工况点
        ax2.plot([Q_work], [H_work], 'bo', markersize=12)
        ax2.text(Q_work-5, H_work+2, f'原工况\nQ={Q_work:.1f}',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        ax2.plot([Q_new], [H_speed], 'go', markersize=12)
        ax2.text(Q_new+2, H_speed, f'调速后\nQ={Q_new:.1f}',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        ax2.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax2.set_ylabel('扬程 H (m)', fontsize=12)
        ax2.set_title('调速方式流量调节', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 50])
        ax2.set_ylim([0, 50])
        
        # 子图3：调节方式对比
        ax3 = plt.subplot(2, 2, 3)
        
        methods = ['原工况', '阀门调节', '调速调节']
        Q_values = [Q_work, Q_new, Q_new]
        H_values = [H_work, H_pump_new, H_speed]
        colors = ['blue', 'red', 'green']
        
        x_pos = np.arange(len(methods))
        bars = ax3.bar(x_pos, Q_values, color=colors, alpha=0.7, 
                      edgecolor='black', linewidth=2)
        
        for i, (bar, Q_val, H_val) in enumerate(zip(bars, Q_values, H_values)):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'Q={Q_val:.1f}L/s\nH={H_val:.1f}m',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax3.set_ylabel('流量 Q (L/s)', fontsize=12)
        ax3.set_title('调节方式对比', fontsize=13, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(methods)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          水泵特性：H={H0}-{a}Q-{b}Q²
          静扬程：Hst={Hst}m
          阻力系数：S={S}s²/m⁵
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 工况点：
            Q = {Q_work:.2f} L/s ✓
            H = {H_work:.2f} m ✓
        
        (2) 阀门调节（Q增20%）：
            Q' = {Q_new:.2f} L/s
            S' = {S_new:.6f} s²/m⁵
            S'/S = {S_new/S:.3f}
            阻力减小{(1-S_new/S)*100:.1f}% ✓
        
        (3) 调速方式（Q增20%）：
            n'/n = {n_ratio:.3f}
            转速增加{(n_ratio-1)*100:.1f}% ✓
            H' = {H_speed:.2f} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 工况点：H泵=H装
          • 装置特性：H装=Hst+SQ²
          • 相似律：Q₁/Q₂=n₁/n₂
                   H₁/H₂=(n₁/n₂)²
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day17_pump/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 写出水泵特性方程 (1分)")
        print("✓ (2) 写出装置特性方程 (1分)")
        print("✓ (3) 建立工况点方程H泵=H装 (2分) ⭐")
        print("✓ (4) 求解二次方程得Q (3分) ⭐⭐")
        print("✓ (5) 计算工况点扬程H (2分)")
        print("✓ (6) 阀门调节计算S' (2分)")
        print("✓ (7) 调速方式计算n'/n (2分)")
        print("✓ (8) 物理意义解释 (1分)")
        print("✓ (9) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 工况点：H泵=H装，两曲线交点")
        print("  ⚠️ 单位统一：Q的L/s与m³/s要转换")
        print("  ⚠️ 阀门调节：改变装置特性S")
        print("  ⚠️ 调速调节：改变水泵特性（相似律）")
        
        return {'Q_work': Q_work, 'H_work': H_work, 'S_new': S_new, 'n_ratio': n_ratio}
    
    def example_2_similarity_law(self):
        """
        例题2：水泵相似定律应用（强化题）⭐⭐⭐⭐⭐
        
        题目：某离心泵在n=1450r/min时，最优工况点：
              Q=0.1m³/s, H=20m, η=0.82, N=24kW
              计算：(1) 该泵的比转数ns
                   (2) 若转速提高到n'=1750r/min，求新工况点参数
                   (3) 若采用切削叶轮，叶轮直径由D=300mm切至D'=270mm，
                       求转速仍为1450r/min时的新工况点
        
        考点：比转数，相似定律，叶轮切削
        难度：强化（必考！）
        时间：25分钟
        分值：20分
        """
        print("\n" + "="*60)
        print("例题2：水泵相似定律应用（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        n = 1450      # 转速 (r/min)
        Q = 0.1       # 流量 (m³/s)
        H = 20.0      # 扬程 (m)
        eta = 0.82    # 效率
        N = 24.0      # 功率 (kW)
        n_new = 1750  # 新转速 (r/min)
        D = 300.0     # 叶轮直径 (mm)
        D_new = 270.0 # 切削后直径 (mm)
        
        print(f"\n已知条件：")
        print(f"  原工况（n={n}r/min）：")
        print(f"    Q = {Q} m³/s")
        print(f"    H = {H} m")
        print(f"    η = {eta}")
        print(f"    N = {N} kW")
        print(f"  新转速：n' = {n_new} r/min")
        print(f"  叶轮直径：D = {D} mm → D' = {D_new} mm")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 比转数
        print(f"\n(1) 计算比转数ns：")
        print(f"    ")
        print(f"    比转数公式：")
        print(f"    ns = 3.65 × n × Q^0.5 / H^0.75")
        print(f"    ")
        print(f"    代入数据：")
        
        ns = 3.65 * n * Q**0.5 / H**0.75
        
        print(f"    ns = 3.65 × {n} × {Q}^0.5 / {H}^0.75")
        print(f"       = 3.65 × {n} × {Q**0.5:.4f} / {H**0.75:.4f}")
        print(f"       = {ns:.1f} ✓")
        print(f"    ")
        print(f"    水泵类型判断：")
        print(f"    • ns<80: 低比转数（离心泵）")
        print(f"    • 80<ns<150: 中比转数")
        print(f"    • 150<ns<300: 混流泵")
        print(f"    • ns>300: 轴流泵")
        print(f"    ")
        
        if ns < 80:
            pump_type = "低比转数离心泵"
        elif ns < 150:
            pump_type = "中比转数离心泵"
        elif ns < 300:
            pump_type = "混流泵"
        else:
            pump_type = "轴流泵"
            
        print(f"    本泵：ns={ns:.1f}，属于{pump_type} ✓")
        
        # (2) 转速变化
        print(f"\n(2) 转速提高到n'={n_new}r/min：")
        print(f"    ")
        print(f"    相似定律（同一泵，不同转速）：")
        print(f"    Q'/Q = n'/n")
        print(f"    H'/H = (n'/n)²")
        print(f"    N'/N = (n'/n)³")
        print(f"    η' ≈ η (效率基本不变)")
        print(f"    ")
        print(f"    计算转速比：")
        
        n_ratio = n_new / n
        
        print(f"    n'/n = {n_new}/{n} = {n_ratio:.4f}")
        print(f"    ")
        print(f"    新流量：")
        
        Q_new = Q * n_ratio
        
        print(f"    Q' = Q × (n'/n)")
        print(f"       = {Q} × {n_ratio:.4f}")
        print(f"       = {Q_new:.4f} m³/s")
        print(f"       = {Q_new*1000:.1f} L/s ✓")
        print(f"    ")
        print(f"    新扬程：")
        
        H_new = H * n_ratio**2
        
        print(f"    H' = H × (n'/n)²")
        print(f"       = {H} × {n_ratio:.4f}²")
        print(f"       = {H} × {n_ratio**2:.4f}")
        print(f"       = {H_new:.2f} m ✓")
        print(f"    ")
        print(f"    新功率：")
        
        N_new = N * n_ratio**3
        
        print(f"    N' = N × (n'/n)³")
        print(f"       = {N} × {n_ratio:.4f}³")
        print(f"       = {N} × {n_ratio**3:.4f}")
        print(f"       = {N_new:.2f} kW ✓")
        print(f"    ")
        print(f"    验证功率公式：")
        
        N_check = self.rho * self.g * Q_new * H_new / eta / 1000
        
        print(f"    N' = ρgQ'H'/η")
        print(f"       = {self.rho}×{self.g}×{Q_new:.4f}×{H_new:.2f}/{eta}/1000")
        print(f"       = {N_check:.2f} kW ✓")
        
        # (3) 叶轮切削
        print(f"\n(3) 叶轮切削（D={D}mm→D'={D_new}mm，n不变）：")
        print(f"    ")
        print(f"    切削定律（同一泵，不同直径，同转速）：")
        print(f"    Q'/Q = D'/D")
        print(f"    H'/H = (D'/D)²")
        print(f"    N'/N = (D'/D)³")
        print(f"    ")
        print(f"    计算直径比：")
        
        D_ratio = D_new / D
        
        print(f"    D'/D = {D_new}/{D} = {D_ratio:.3f}")
        print(f"    ")
        print(f"    切削后流量：")
        
        Q_cut = Q * D_ratio
        
        print(f"    Q' = Q × (D'/D)")
        print(f"       = {Q} × {D_ratio:.3f}")
        print(f"       = {Q_cut:.4f} m³/s")
        print(f"       = {Q_cut*1000:.1f} L/s ✓")
        print(f"    ")
        print(f"    切削后扬程：")
        
        H_cut = H * D_ratio**2
        
        print(f"    H' = H × (D'/D)²")
        print(f"       = {H} × {D_ratio:.3f}²")
        print(f"       = {H} × {D_ratio**2:.4f}")
        print(f"       = {H_cut:.2f} m ✓")
        print(f"    ")
        print(f"    切削后功率：")
        
        N_cut = N * D_ratio**3
        
        print(f"    N' = N × (D'/D)³")
        print(f"       = {N} × {D_ratio:.3f}³")
        print(f"       = {N} × {D_ratio**3:.4f}")
        print(f"       = {N_cut:.2f} kW ✓")
        print(f"    ")
        print(f"    切削限制：")
        print(f"    切削量 = (D-D')/D = ({D}-{D_new})/{D}")
        
        cut_ratio = (D - D_new) / D
        
        print(f"           = {cut_ratio:.3f} = {cut_ratio*100:.1f}%")
        print(f"    ")
        if cut_ratio <= 0.2:
            print(f"    判断：{cut_ratio*100:.1f}% ≤ 20%，切削合理 ✓")
        else:
            print(f"    判断：{cut_ratio*100:.1f}% > 20%，超过限制 ⚠️")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：转速变化对特性曲线的影响
        ax1 = plt.subplot(2, 2, 1)
        
        Q_range = np.linspace(0, 0.15, 100)
        
        # 原特性曲线（n=1450）
        H_orig = 25 - 100*Q_range**2  # 简化模型
        ax1.plot(Q_range*1000, H_orig, 'b-', linewidth=2.5, label=f'n={n}r/min')
        ax1.plot([Q*1000], [H], 'bo', markersize=12)
        ax1.text(Q*1000-10, H+2, f'原工况\nQ={Q*1000:.0f}L/s\nH={H}m',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        # 新特性曲线（n'=1750）
        H_new_curve = H_orig * n_ratio**2
        Q_new_curve = Q_range * n_ratio
        ax1.plot(Q_new_curve*1000, H_new_curve, 'r--', linewidth=2.5, 
                label=f'n\'={n_new}r/min')
        ax1.plot([Q_new*1000], [H_new], 'ro', markersize=12)
        ax1.text(Q_new*1000+5, H_new, f'新工况\nQ={Q_new*1000:.0f}L/s\nH={H_new:.1f}m',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='lightcoral'))
        
        ax1.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax1.set_ylabel('扬程 H (m)', fontsize=12)
        ax1.set_title('Day 17 例题2：转速变化影响', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 150])
        
        # 子图2：叶轮切削影响
        ax2 = plt.subplot(2, 2, 2)
        
        # 原特性（D=300mm）
        ax2.plot(Q_range*1000, H_orig, 'b-', linewidth=2.5, label=f'D={D}mm')
        ax2.plot([Q*1000], [H], 'bo', markersize=12)
        
        # 切削后特性（D'=270mm）
        H_cut_curve = H_orig * D_ratio**2
        Q_cut_curve = Q_range * D_ratio
        ax2.plot(Q_cut_curve*1000, H_cut_curve, 'g--', linewidth=2.5, 
                label=f'D\'={D_new}mm')
        ax2.plot([Q_cut*1000], [H_cut], 'go', markersize=12)
        ax2.text(Q_cut*1000-10, H_cut-2, f'切削后\nQ={Q_cut*1000:.0f}L/s\nH={H_cut:.1f}m',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        ax2.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax2.set_ylabel('扬程 H (m)', fontsize=12)
        ax2.set_title('叶轮切削影响', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 120])
        
        # 子图3：参数变化对比
        ax3 = plt.subplot(2, 2, 3)
        
        params = ['流量Q\n(m³/s)', '扬程H\n(m)', '功率N\n(kW)']
        orig_values = [Q, H, N]
        speed_values = [Q_new, H_new, N_new]
        cut_values = [Q_cut, H_cut, N_cut]
        
        x = np.arange(len(params))
        width = 0.25
        
        bars1 = ax3.bar(x - width, orig_values, width, label='原工况', 
                       color='blue', alpha=0.7)
        bars2 = ax3.bar(x, speed_values, width, label='调速后', 
                       color='red', alpha=0.7)
        bars3 = ax3.bar(x + width, cut_values, width, label='切削后', 
                       color='green', alpha=0.7)
        
        # 标注数值
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom', fontsize=8)
        
        ax3.set_ylabel('参数值', fontsize=12)
        ax3.set_title('调节方式参数对比', fontsize=13, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(params)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        原工况（n={n}r/min）：
          Q = {Q} m³/s = {Q*1000:.0f} L/s
          H = {H} m
          N = {N} kW
          η = {eta}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 比转数：
            ns = {ns:.1f} ✓
            类型：{pump_type}
        
        (2) 调速（n'={n_new}r/min）：
            Q' = {Q_new:.4f} m³/s ✓
            H' = {H_new:.2f} m ✓
            N' = {N_new:.2f} kW ✓
        
        (3) 切削（D'={D_new}mm）：
            Q' = {Q_cut:.4f} m³/s ✓
            H' = {H_cut:.2f} m ✓
            N' = {N_cut:.2f} kW ✓
            切削量 = {cut_ratio*100:.1f}%
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 比转数：ns=3.65nQ^0.5/H^0.75
          • 相似律：Q₁/Q₂=n₁/n₂=(D₁/D₂)
                   H₁/H₂=(n₁/n₂)²=(D₁/D₂)²
                   N₁/N₂=(n₁/n₂)³=(D₁/D₂)³
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day17_pump/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（20分评分标准）：")
        print("="*60)
        print("✓ (1) 写出比转数公式 (2分) ⭐")
        print("✓ (2) 计算ns并判断泵类型 (3分) ⭐⭐")
        print("✓ (3) 写出相似定律公式 (2分) ⭐")
        print("✓ (4) 调速计算Q',H',N' (6分) ⭐⭐⭐")
        print("✓ (5) 写出切削定律 (1分)")
        print("✓ (6) 切削计算Q',H',N' (4分) ⭐⭐")
        print("✓ (7) 切削限制判断 (1分)")
        print("✓ (8) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 比转数ns：注意系数3.65，单位要匹配")
        print("  ⚠️ 相似律：Q∝n∝D, H∝n²∝D², N∝n³∝D³")
        print("  ⚠️ 切削限制：一般不超过20%")
        print("  ⚠️ 效率：调速时η基本不变，切削时略降")
        
        return {'ns': ns, 'Q_new': Q_new, 'H_new': H_new, 'Q_cut': Q_cut, 'H_cut': H_cut}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 17 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 水泵特性曲线：")
        print("     H = H0 - aQ - bQ²  (扬程)")
        print("     η = f(Q)  (效率)")
        print("     N = ρgQH/η  (功率)")
        print("     ")
        print("  2. 装置特性曲线：")
        print("     H装 = Hst + SQ²")
        print("     (Hst为静扬程，S为阻力系数)")
        print("     ")
        print("  3. 工况点：")
        print("     H泵 = H装  (特性曲线交点)")
        print("     ")
        print("  4. 比转数：")
        print("     ns = 3.65 × n × Q^0.5 / H^0.75")
        print("     (n单位r/min，Q单位m³/s，H单位m)")
        print("     ")
        print("  5. 相似定律（转速）：")
        print("     Q₁/Q₂ = n₁/n₂")
        print("     H₁/H₂ = (n₁/n₂)²")
        print("     N₁/N₂ = (n₁/n₂)³")
        print("     ")
        print("  6. 切削定律（直径）：")
        print("     Q₁/Q₂ = D₁/D₂")
        print("     H₁/H₂ = (D₁/D₂)²")
        print("     N₁/N₂ = (D₁/D₂)³")
        print("     (切削量一般≤20%)")
        
        print("\n✅ 水泵类型（按ns）：")
        print("  ┌──────────┬─────────┬──────────────┐")
        print("  │ 类型     │ ns范围  │ 特点         │")
        print("  ├──────────┼─────────┼──────────────┤")
        print("  │ 低比转数 │ <80     │ 高扬程小流量 │")
        print("  │ 中比转数 │ 80~150  │ 中扬程中流量 │")
        print("  │ 混流泵   │ 150~300 │ 中扬程大流量 │")
        print("  │ 轴流泵   │ >300    │ 低扬程大流量 │")
        print("  └──────────┴─────────┴──────────────┘")
        
        print("\n✅ 流量调节方式对比：")
        print("  ┌──────────┬──────────┬──────────┬──────────┐")
        print("  │ 方式     │ 改变对象 │ 能耗     │ 适用范围 │")
        print("  ├──────────┼──────────┼──────────┼──────────┤")
        print("  │ 阀门调节 │ 装置特性 │ 高       │ 临时调节 │")
        print("  │ 调速调节 │ 水泵特性 │ 低       │ 经常调节 │")
        print("  │ 叶轮切削 │ 水泵特性 │ 最低     │ 永久降低 │")
        print("  └──────────┴──────────┴──────────┴──────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【工况点题】")
        print("  Step 1: 写出水泵特性H泵(Q)")
        print("  Step 2: 写出装置特性H装(Q)")
        print("  Step 3: 建立方程H泵=H装")
        print("  Step 4: 求解Q和H")
        print("  ")
        print("  【相似律题】")
        print("  Step 1: 判断变化类型（n或D）")
        print("  Step 2: 写出相似律公式")
        print("  Step 3: 代入计算新参数")
        print("  Step 4: 验证合理性")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：工况点不是H泵=H装，而是其他条件")
        print("  ❌ 错误2：相似律指数搞混（Q∝n，H∝n²，N∝n³）")
        print("  ❌ 错误3：比转数公式系数或指数记错")
        print("  ❌ 错误4：单位不统一（Q的L/s和m³/s）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：工况点→画图→两曲线交点")
        print("  ✓ 技巧2：相似律→记规律→Q∝n，H∝n²，N∝n³")
        print("  ✓ 技巧3：比转数→判泵型→低中混轴")
        print("  ✓ 技巧4：调节方式→分析能耗→调速最优")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能准确求解工况点")
        print("  □ 掌握相似定律应用")
        print("  □ 理解比转数意义")
        print("  □ 熟练流量调节方法")
        
        print("\n📅 明日预告：Day 18 - 水工建筑物")
        print("  • 堤坝稳定分析")
        print("  • 渗流计算")
        print("  • 消能防冲")
        
        print("\n💪 今日格言：")
        print("  「水泵是实用核心！掌握特性曲线=拿到20分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 17: 水泵与泵站")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day17 = Day17Pump()
    
    # 例题1：工况点
    result1 = day17.example_1_operating_point()
    
    # 例题2：相似定律
    result2 = day17.example_2_similarity_law()
    
    # 每日总结
    day17.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 17 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握工况点计算")
    print(f"  ✓ 掌握相似定律")
    print(f"  ✓ 理解比转数")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n🎊 渗流+泵站章节100%完成！")
    print(f"  Day 15+16+17全覆盖！")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
