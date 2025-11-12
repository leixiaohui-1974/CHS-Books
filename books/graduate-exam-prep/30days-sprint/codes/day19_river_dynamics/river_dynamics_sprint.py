#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 19: 河流动力学
Sprint Day 19: River Dynamics

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 泥沙起动流速：希尔兹数、起动流速
  2. 泥沙输移：推移质、悬移质
  3. 河床演变：冲淤平衡
  4. 河道整治：弯道环流、河势控制
  5. 挟沙能力：含沙量计算

🎯 学习目标：
  - 掌握泥沙起动条件
  - 理解泥沙输移规律
  - 熟练河床演变分析
  - 了解河道整治原理

💪 今日格言：河流动力学是应用题！掌握泥沙计算=拿到16分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon, Wedge, Arc
from matplotlib.patches import ConnectionPatch
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day19RiverDynamics:
    """
    Day 19：河流动力学
    
    包含2个核心例题：
    1. 基础题：泥沙起动流速
    2. 强化题：泥沙输移与冲淤
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho_w = 1000  # 水密度 (kg/m³)
        self.rho_s = 2650  # 泥沙密度 (kg/m³)
        self.nu = 1.0e-6  # 水运动粘性系数 (m²/s)
        
    def example_1_incipient_motion(self):
        """
        例题1：泥沙起动流速（基础题）⭐⭐⭐⭐⭐
        
        题目：某河道泥沙中值粒径d50=0.5mm，河道水深h=2.0m
              河床坡度J=0.0001，曼宁系数n=0.025
              泥沙密度ρs=2650kg/m³，水密度ρw=1000kg/m³
        求：(1) 希尔兹数θc（临界值）
            (2) 起动切应力τc
            (3) 起动流速uc
            (4) 实际平均流速u（判断是否起动）
        
        考点：希尔兹数，起动流速，泥沙起动
        难度：基础（必考！）
        时间：20分钟
        分值：16分
        """
        print("\n" + "="*60)
        print("例题1：泥沙起动流速（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d50 = 0.5e-3  # 中值粒径 (m)
        h = 2.0       # 水深 (m)
        J = 0.0001    # 坡度
        n = 0.025     # 曼宁系数
        rho_s = 2650  # 泥沙密度 (kg/m³)
        rho_w = 1000  # 水密度 (kg/m³)
        g = 9.81      # 重力加速度 (m/s²)
        
        print(f"\n已知条件：")
        print(f"  中值粒径 d₅₀ = {d50*1000} mm = {d50} m")
        print(f"  水深 h = {h} m")
        print(f"  河床坡度 J = {J}")
        print(f"  曼宁系数 n = {n}")
        print(f"  泥沙密度 ρs = {rho_s} kg/m³")
        print(f"  水密度 ρw = {rho_w} kg/m³")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 希尔兹数
        print(f"\n(1) 希尔兹数θc（临界值）：")
        print(f"    ")
        print(f"    希尔兹数定义：")
        print(f"    θc = τc / [(ρs-ρw)gd]")
        print(f"    ")
        print(f"    对于中等粒径泥沙（0.1-1mm）：")
        print(f"    θc ≈ 0.05（经验值）")
        
        theta_c = 0.05
        
        print(f"    θc = {theta_c} ✓")
        print(f"    ")
        print(f"    物理意义：水流切应力与泥沙浸水重的比值")
        
        # (2) 起动切应力
        print(f"\n(2) 起动切应力τc：")
        print(f"    ")
        print(f"    从希尔兹数公式：")
        print(f"    τc = θc × (ρs-ρw) × g × d")
        print(f"    ")
        print(f"    代入数据：")
        
        tau_c = theta_c * (rho_s - rho_w) * g * d50
        
        print(f"    τc = {theta_c} × ({rho_s}-{rho_w}) × {g} × {d50}")
        print(f"       = {theta_c} × {rho_s-rho_w} × {g} × {d50}")
        print(f"       = {tau_c:.4f} N/m² ✓")
        print(f"    ")
        print(f"    物理意义：泥沙起动所需的临界底床切应力")
        
        # (3) 起动流速
        print(f"\n(3) 起动流速uc：")
        print(f"    ")
        print(f"    底床切应力公式：")
        print(f"    τ = ρw × g × h × J")
        print(f"    ")
        print(f"    起动条件：τ = τc")
        print(f"    ρw × g × hc × J = τc")
        print(f"    ")
        print(f"    起动水深：")
        
        hc = tau_c / (rho_w * g * J)
        
        print(f"    hc = τc / (ρw × g × J)")
        print(f"       = {tau_c:.4f} / ({rho_w} × {g} × {J})")
        print(f"       = {hc:.3f} m")
        print(f"    ")
        print(f"    谢才公式：u = C√(RJ)")
        print(f"    曼宁公式：C = R^(1/6) / n")
        print(f"    ")
        print(f"    起动流速（取R≈hc）：")
        
        R_c = hc
        C_c = R_c**(1/6) / n
        uc = C_c * np.sqrt(R_c * J)
        
        print(f"    C = hc^(1/6) / n = {hc}^(1/6) / {n}")
        print(f"      = {C_c:.2f} m^(1/2)/s")
        print(f"    ")
        print(f"    uc = C√(hcJ)")
        print(f"       = {C_c:.2f} × √({hc:.3f} × {J})")
        print(f"       = {C_c:.2f} × {np.sqrt(hc*J):.4f}")
        print(f"       = {uc:.4f} m/s ✓")
        
        # (4) 实际流速
        print(f"\n(4) 实际平均流速u：")
        print(f"    ")
        print(f"    给定水深h = {h} m")
        print(f"    ")
        print(f"    谢才系数：")
        
        R = h
        C = R**(1/6) / n
        
        print(f"    C = h^(1/6) / n = {h}^(1/6) / {n}")
        print(f"      = {C:.2f} m^(1/2)/s")
        print(f"    ")
        print(f"    平均流速：")
        
        u = C * np.sqrt(R * J)
        
        print(f"    u = C√(hJ)")
        print(f"      = {C:.2f} × √({h} × {J})")
        print(f"      = {C:.2f} × {np.sqrt(h*J):.4f}")
        print(f"      = {u:.4f} m/s ✓")
        print(f"    ")
        print(f"    判断：")
        
        if u > uc:
            print(f"    u ({u:.4f}) > uc ({uc:.4f})")
            print(f"    结论：泥沙起动，发生输移 ✓")
            status = "起动"
        else:
            print(f"    u ({u:.4f}) ≤ uc ({uc:.4f})")
            print(f"    结论：泥沙不起动 ✓")
            status = "不起动"
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：泥沙起动示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 河床
        x_bed = np.array([0, 10])
        y_bed = np.array([0, -J*10])
        ax1.fill_between(x_bed, y_bed, y_bed-0.5, color='sandybrown', alpha=0.5,
                        label='河床')
        ax1.plot(x_bed, y_bed, 'k-', linewidth=2)
        
        # 水体
        y_water = y_bed + h
        ax1.fill_between(x_bed, y_bed, y_water, color='lightblue', alpha=0.4,
                        label='水体')
        ax1.plot(x_bed, y_water, 'b-', linewidth=2, label='水面')
        
        # 泥沙颗粒
        np.random.seed(42)
        n_particles = 20
        x_particles = np.random.uniform(0.5, 9.5, n_particles)
        y_particles = y_bed[0] + (x_particles/10) * (y_bed[1]-y_bed[0])
        
        for xp, yp in zip(x_particles, y_particles):
            circle = Circle((xp, yp), 0.08, color='brown', alpha=0.8)
            ax1.add_patch(circle)
        
        # 流速箭头
        arrow_y = y_bed[0] + h/2
        ax1.arrow(1, arrow_y, 1.5, 0, head_width=0.15, head_length=0.3,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(2.5, arrow_y+0.3, f'u={u:.4f}m/s', fontsize=11,
                color='blue', fontweight='bold')
        
        # 切应力标注
        ax1.text(5, y_bed[0]-0.15, f'τ=ρwghJ', fontsize=10,
                ha='center', color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 尺寸标注
        ax1.text(5, arrow_y+h/2+0.1, f'h={h}m', fontsize=10,
                ha='center',
                bbox=dict(boxstyle='round', facecolor='lightcyan'))
        ax1.text(5, y_bed[0]+0.4, f'd₅₀={d50*1000}mm', fontsize=9,
                ha='center')
        
        ax1.set_xlabel('河道纵向 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 19 例题1：泥沙起动示意图', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 10])
        ax1.set_ylim([y_bed[1]-0.6, y_water[0]+0.5])
        
        # 子图2：起动流速对比
        ax2 = plt.subplot(2, 2, 2)
        
        # 粒径范围
        d_range = np.logspace(-4, -2, 50)  # 0.1mm到10mm
        uc_range = []
        
        for d in d_range:
            tau_c_temp = theta_c * (rho_s - rho_w) * g * d
            hc_temp = tau_c_temp / (rho_w * g * J)
            R_c_temp = hc_temp
            C_c_temp = R_c_temp**(1/6) / n
            uc_temp = C_c_temp * np.sqrt(R_c_temp * J)
            uc_range.append(uc_temp)
        
        ax2.loglog(d_range*1000, uc_range, 'b-', linewidth=2.5,
                  label='起动流速uc vs 粒径')
        ax2.loglog([d50*1000], [uc], 'ro', markersize=12,
                  label=f'本题：d={d50*1000}mm, uc={uc:.4f}m/s')
        ax2.axhline(y=u, color='green', linestyle='--', linewidth=2,
                   label=f'实际流速u={u:.4f}m/s')
        
        ax2.set_xlabel('粒径 d (mm)', fontsize=12)
        ax2.set_ylabel('起动流速 uc (m/s)', fontsize=12)
        ax2.set_title('起动流速与粒径关系', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3, which='both')
        
        # 子图3：希尔兹图
        ax3 = plt.subplot(2, 2, 3)
        
        # 简化希尔兹图（示意）
        Re_star = np.logspace(-1, 4, 100)
        theta_shields = 0.05 * np.ones_like(Re_star)
        
        # 三个区域
        idx1 = Re_star < 2
        theta_shields[idx1] = 0.1 * Re_star[idx1]**(-0.3)
        
        idx2 = (Re_star >= 2) & (Re_star < 100)
        theta_shields[idx2] = 0.05
        
        idx3 = Re_star >= 100
        theta_shields[idx3] = 0.045
        
        ax3.loglog(Re_star, theta_shields, 'b-', linewidth=2.5,
                  label='希尔兹曲线')
        ax3.axhline(y=theta_c, color='red', linestyle='--', linewidth=2,
                   label=f'本题：θc={theta_c}')
        
        ax3.fill_between(Re_star, 0.001, theta_shields, alpha=0.2,
                        color='green', label='稳定区（不起动）')
        ax3.fill_between(Re_star, theta_shields, 1, alpha=0.2,
                        color='red', label='输移区（起动）')
        
        ax3.set_xlabel('颗粒雷诺数 Re*', fontsize=12)
        ax3.set_ylabel('希尔兹数 θ', fontsize=12)
        ax3.set_title('希尔兹图（Shields Diagram）', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, which='both')
        ax3.set_xlim([0.1, 10000])
        ax3.set_ylim([0.01, 0.2])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          粒径：d₅₀ = {d50*1000} mm
          水深：h = {h} m
          坡度：J = {J}
          曼宁系数：n = {n}
          泥沙密度：ρs = {rho_s} kg/m³
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 希尔兹数：
            θc = {theta_c} ✓
            （中等粒径经验值）
        
        (2) 起动切应力：
            τc = θc(ρs-ρw)gd
               = {tau_c:.4f} N/m² ✓
        
        (3) 起动流速：
            hc = {hc:.3f} m
            C = {C_c:.2f} m^(1/2)/s
            uc = {uc:.4f} m/s ✓
        
        (4) 实际流速：
            C = {C:.2f} m^(1/2)/s
            u = {u:.4f} m/s ✓
            
        (5) 判断：
            u {'>' if u>uc else '≤'} uc
            泥沙{status} ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 希尔兹数：θc=τc/[(ρs-ρw)gd]
          • 起动切应力：τc=θc(ρs-ρw)gd
          • 谢才公式：u=C√(RJ)
          • 曼宁公式：C=R^(1/6)/n
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day19_river_dynamics/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（16分评分标准）：")
        print("="*60)
        print("✓ (1) 写出希尔兹数定义 (2分) ⭐")
        print("✓ (2) 取θc经验值 (1分)")
        print("✓ (3) 计算起动切应力τc (3分) ⭐⭐")
        print("✓ (4) 写出起动流速公式 (2分) ⭐")
        print("✓ (5) 计算起动流速uc (3分) ⭐⭐")
        print("✓ (6) 计算实际流速u (3分) ⭐⭐")
        print("✓ (7) 判断是否起动 (2分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 希尔兹数：θc=τc/[(ρs-ρw)gd]，注意ρs-ρw")
        print("  ⚠️ 起动切应力：τc=θc(ρs-ρw)gd，别忘记θc")
        print("  ⚠️ 谢才公式：u=C√(RJ)，C与R有关")
        print("  ⚠️ 判断：u>uc才起动，等号边界")
        
        return {'theta_c': theta_c, 'tau_c': tau_c, 'uc': uc, 'u': u, 'status': status}
    
    def example_2_sediment_transport(self):
        """
        例题2：泥沙输移与冲淤（强化题）⭐⭐⭐⭐⭐
        
        题目：某河段长L=1000m，河宽B=50m，平均水深h=3m
              进口断面含沙量S1=2.0kg/m³，出口断面含沙量S2=1.5kg/m³
              平均流速u=0.8m/s，时间Δt=1天
        求：(1) 进出口输沙率Qs1、Qs2
            (2) 河段泥沙淤积量ΔW
            (3) 河床平均淤积厚度Δz
            (4) 若河段挟沙能力S*=1.8kg/m³，分析冲淤趋势
        
        考点：输沙率，冲淤计算，挟沙能力
        难度：强化（必考！）
        时间：25分钟
        分值：20分
        """
        print("\n" + "="*60)
        print("例题2：泥沙输移与冲淤（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        L = 1000      # 河段长度 (m)
        B = 50        # 河宽 (m)
        h = 3.0       # 平均水深 (m)
        S1 = 2.0      # 进口含沙量 (kg/m³)
        S2 = 1.5      # 出口含沙量 (kg/m³)
        u = 0.8       # 平均流速 (m/s)
        dt_day = 1    # 时间 (天)
        dt = dt_day * 86400  # 时间 (秒)
        S_star = 1.8  # 挟沙能力 (kg/m³)
        rho_s = 2650  # 泥沙干密度 (kg/m³)
        
        print(f"\n已知条件：")
        print(f"  河段长度 L = {L} m")
        print(f"  河宽 B = {B} m")
        print(f"  平均水深 h = {h} m")
        print(f"  进口含沙量 S₁ = {S1} kg/m³")
        print(f"  出口含沙量 S₂ = {S2} kg/m³")
        print(f"  平均流速 u = {u} m/s")
        print(f"  时间 Δt = {dt_day} 天 = {dt} s")
        print(f"  挟沙能力 S* = {S_star} kg/m³")
        print(f"  泥沙干密度 ρs = {rho_s} kg/m³")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 输沙率
        print(f"\n(1) 计算进出口输沙率：")
        print(f"    ")
        print(f"    输沙率定义：")
        print(f"    Qs = Q × S = (u × A) × S")
        print(f"       = u × B × h × S")
        print(f"    ")
        print(f"    进口输沙率Qs₁：")
        
        Q = u * B * h
        Qs1 = Q * S1
        
        print(f"    Q = u × B × h")
        print(f"      = {u} × {B} × {h}")
        print(f"      = {Q} m³/s")
        print(f"    ")
        print(f"    Qs₁ = Q × S₁")
        print(f"        = {Q} × {S1}")
        print(f"        = {Qs1} kg/s ✓")
        print(f"    ")
        print(f"    出口输沙率Qs₂：")
        
        Qs2 = Q * S2
        
        print(f"    Qs₂ = Q × S₂")
        print(f"        = {Q} × {S2}")
        print(f"        = {Qs2} kg/s ✓")
        print(f"    ")
        print(f"    输沙率差：")
        
        delta_Qs = Qs1 - Qs2
        
        print(f"    ΔQs = Qs₁ - Qs₂")
        print(f"        = {Qs1} - {Qs2}")
        print(f"        = {delta_Qs} kg/s ✓")
        print(f"    （>0说明有泥沙淤积）")
        
        # (2) 淤积量
        print(f"\n(2) 河段泥沙淤积量ΔW：")
        print(f"    ")
        print(f"    泥沙收支方程：")
        print(f"    ΔW = (Qs₁ - Qs₂) × Δt")
        print(f"    ")
        print(f"    代入数据：")
        
        delta_W = delta_Qs * dt
        
        print(f"    ΔW = {delta_Qs} × {dt}")
        print(f"       = {delta_W:.2e} kg")
        print(f"       = {delta_W/1000:.2e} 吨 ✓")
        print(f"    ")
        print(f"    物理意义：河段内泥沙淤积的总质量")
        
        # (3) 淤积厚度
        print(f"\n(3) 河床平均淤积厚度Δz：")
        print(f"    ")
        print(f"    淤积体积（考虑孔隙率，取γ'=1.6×ρs）：")
        print(f"    V = ΔW / γ'")
        print(f"    ")
        print(f"    河段面积：")
        
        A_bed = L * B
        
        print(f"    A = L × B = {L} × {B}")
        print(f"      = {A_bed} m²")
        print(f"    ")
        print(f"    淤积厚度：")
        print(f"    Δz = V / A = ΔW / (γ' × A)")
        
        gamma_prime = 1.6 * rho_s  # 淤积物容重
        delta_z = delta_W / (gamma_prime * A_bed)
        
        print(f"    ")
        print(f"    γ' = 1.6ρs = 1.6 × {rho_s}")
        print(f"       = {gamma_prime} kg/m³")
        print(f"    ")
        print(f"    Δz = {delta_W:.2e} / ({gamma_prime} × {A_bed})")
        print(f"       = {delta_z:.4f} m")
        print(f"       = {delta_z*100:.2f} cm ✓")
        print(f"    ")
        print(f"    物理意义：{dt_day}天内河床平均抬高{delta_z*100:.2f}cm")
        
        # (4) 挟沙能力分析
        print(f"\n(4) 挟沙能力与冲淤趋势分析：")
        print(f"    ")
        print(f"    挟沙能力：S* = {S_star} kg/m³")
        print(f"    ")
        print(f"    进口断面：")
        print(f"    S₁ = {S1} kg/m³")
        
        if S1 > S_star:
            print(f"    S₁ > S*，饱和超饱和，倾向淤积")
            trend1 = "淤积"
        else:
            print(f"    S₁ < S*，未饱和，可继续挟沙")
            trend1 = "冲刷"
        
        print(f"    ")
        print(f"    出口断面：")
        print(f"    S₂ = {S2} kg/m³")
        
        if S2 > S_star:
            print(f"    S₂ > S*，饱和超饱和")
            trend2 = "淤积"
        else:
            print(f"    S₂ < S*，未饱和")
            trend2 = "冲刷"
        
        print(f"    ")
        print(f"    整体趋势：")
        print(f"    ΔQs = {delta_Qs} kg/s > 0")
        print(f"    结论：河段整体淤积 ✓")
        print(f"    ")
        print(f"    淤积速率：")
        
        rate_per_year = delta_z * 365
        
        print(f"    年淤积速率 = {delta_z:.4f} × 365")
        print(f"                 = {rate_per_year:.3f} m/年")
        print(f"                 = {rate_per_year*100:.1f} cm/年 ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：河段示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 河道
        river_x = [0, L, L, 0, 0]
        river_y = [0, 0, B, B, 0]
        ax1.plot(river_x, river_y, 'k-', linewidth=2)
        ax1.fill(river_x, river_y, color='lightblue', alpha=0.3)
        
        # 进口断面
        ax1.plot([0, 0], [0, B], 'r-', linewidth=3, label='进口断面')
        ax1.text(-50, B/2, f'S₁={S1}kg/m³\nQs₁={Qs1}kg/s',
                fontsize=10, ha='right', color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 出口断面
        ax1.plot([L, L], [0, B], 'b-', linewidth=3, label='出口断面')
        ax1.text(L+50, B/2, f'S₂={S2}kg/m³\nQs₂={Qs2}kg/s',
                fontsize=10, ha='left', color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightcyan'))
        
        # 流向箭头
        arrow_y = B/2
        for x in [L/4, L/2, 3*L/4]:
            ax1.arrow(x, arrow_y, L/8, 0, head_width=3, head_length=30,
                     fc='green', ec='green', linewidth=2, alpha=0.6)
        
        # 淤积示意
        n_deposit = 10
        for i in range(n_deposit):
            x_d = np.random.uniform(100, L-100)
            y_d = np.random.uniform(5, B-5)
            circle = Circle((x_d, y_d), 3, color='brown', alpha=0.5)
            ax1.add_patch(circle)
        
        ax1.text(L/2, B+8, f'淤积量：ΔW={delta_W/1000:.2e}吨\n厚度：Δz={delta_z*100:.2f}cm',
                fontsize=11, ha='center', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='orange', alpha=0.8))
        
        ax1.set_xlabel('河道纵向 (m)', fontsize=12)
        ax1.set_ylabel('河道横向 (m)', fontsize=12)
        ax1.set_title('Day 19 例题2：河段冲淤示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-100, L+100])
        ax1.set_ylim([-5, B+15])
        ax1.set_aspect('equal')
        
        # 子图2：输沙率对比
        ax2 = plt.subplot(2, 2, 2)
        
        locations = ['进口', '出口']
        Qs_values = [Qs1, Qs2]
        S_values = [S1, S2]
        
        x_pos = np.arange(len(locations))
        width = 0.35
        
        bars1 = ax2.bar(x_pos - width/2, Qs_values, width, label='输沙率Qs (kg/s)',
                       color='blue', alpha=0.7)
        bars2 = ax2.bar(x_pos + width/2, [s*100 for s in S_values], width,
                       label='含沙量S×100 (kg/m³)',
                       color='orange', alpha=0.7)
        
        # 标注数值
        for bar in bars1:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 挟沙能力线
        ax2.axhline(y=S_star*100, color='red', linestyle='--', linewidth=2,
                   label=f'挟沙能力S*×100={S_star*100}')
        
        ax2.set_ylabel('数值', fontsize=12)
        ax2.set_title('输沙率与含沙量对比', fontsize=13, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(locations)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 子图3：时间-淤积曲线
        ax3 = plt.subplot(2, 2, 3)
        
        # 模拟一年的淤积过程
        days = np.linspace(0, 365, 100)
        z_accumulation = delta_z * days
        
        ax3.plot(days, z_accumulation*100, 'b-', linewidth=2.5,
                label='淤积厚度累积')
        ax3.plot([dt_day], [delta_z*100], 'ro', markersize=12,
                label=f'{dt_day}天：{delta_z*100:.2f}cm')
        
        # 年淤积
        ax3.plot([365], [rate_per_year*100], 'gs', markersize=12,
                label=f'1年：{rate_per_year*100:.1f}cm')
        
        ax3.set_xlabel('时间 (天)', fontsize=12)
        ax3.set_ylabel('淤积厚度 (cm)', fontsize=12)
        ax3.set_title('淤积厚度时间过程', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          河段：L={L}m, B={B}m, h={h}m
          含沙量：S₁={S1}, S₂={S2} kg/m³
          流速：u = {u} m/s
          时间：Δt = {dt_day} 天
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 输沙率：
            Q = u×B×h = {Q} m³/s
            Qs₁ = Q×S₁ = {Qs1} kg/s ✓
            Qs₂ = Q×S₂ = {Qs2} kg/s ✓
            ΔQs = {delta_Qs} kg/s ✓
        
        (2) 淤积量：
            ΔW = ΔQs×Δt
               = {delta_W:.2e} kg
               = {delta_W/1000:.2e} 吨 ✓
        
        (3) 淤积厚度：
            A = L×B = {A_bed} m²
            γ' = 1.6ρs = {gamma_prime} kg/m³
            Δz = ΔW/(γ'×A)
               = {delta_z:.4f} m
               = {delta_z*100:.2f} cm ✓
        
        (4) 冲淤趋势：
            S* = {S_star} kg/m³
            S₁({S1}) > S*: {trend1}
            S₂({S2}) < S*: {trend2}
            整体：淤积 ✓
            年速率：{rate_per_year*100:.1f} cm/年
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 输沙率：Qs=Q×S
          • 淤积量：ΔW=(Qs₁-Qs₂)×Δt
          • 厚度：Δz=ΔW/(γ'×A)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=7.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day19_river_dynamics/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（20分评分标准）：")
        print("="*60)
        print("✓ (1) 计算流量Q (2分)")
        print("✓ (2) 写出输沙率公式 (2分) ⭐")
        print("✓ (3) 计算Qs₁、Qs₂ (3分) ⭐⭐")
        print("✓ (4) 写出淤积量公式 (2分) ⭐")
        print("✓ (5) 计算ΔW (3分) ⭐⭐")
        print("✓ (6) 计算河床面积A (1分)")
        print("✓ (7) 计算淤积厚度Δz (3分) ⭐⭐")
        print("✓ (8) 挟沙能力分析 (2分)")
        print("✓ (9) 冲淤趋势判断 (2分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 输沙率：Qs=Q×S，不要忘记S")
        print("  ⚠️ 淤积量：ΔW=(Qs₁-Qs₂)×Δt，注意时间单位")
        print("  ⚠️ 淤积厚度：γ'=1.6ρs（考虑孔隙率）")
        print("  ⚠️ 挟沙能力：S>S*淤积，S<S*冲刷")
        
        return {'Qs1': Qs1, 'Qs2': Qs2, 'delta_W': delta_W, 'delta_z': delta_z,
                'rate_per_year': rate_per_year}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 19 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 希尔兹数：")
        print("     θc = τc / [(ρs-ρw)gd]")
        print("     中等粒径：θc ≈ 0.05")
        print("     ")
        print("  2. 起动切应力：")
        print("     τc = θc × (ρs-ρw) × g × d")
        print("     （泥沙起动临界条件）")
        print("     ")
        print("  3. 起动流速：")
        print("     uc = C√(RJ)")
        print("     C = R^(1/6) / n（曼宁）")
        print("     ")
        print("  4. 输沙率：")
        print("     Qs = Q × S")
        print("     Q = u × A（流量）")
        print("     S（含沙量kg/m³）")
        print("     ")
        print("  5. 冲淤计算：")
        print("     ΔW = (Qs₁-Qs₂) × Δt")
        print("     Δz = ΔW / (γ' × A)")
        print("     γ' = 1.6ρs（淤积物容重）")
        
        print("\n✅ 泥沙粒径分类：")
        print("  ┌────────────┬──────────────┬──────────────┐")
        print("  │ 粒径范围   │ 名称         │ θc经验值     │")
        print("  ├────────────┼──────────────┼──────────────┤")
        print("  │ <0.005mm   │ 粘土         │ 特殊         │")
        print("  │ 0.005-0.05 │ 粉砂         │ 0.04-0.06    │")
        print("  │ 0.05-0.25  │ 细砂         │ 0.05         │")
        print("  │ 0.25-0.5   │ 中砂         │ 0.05         │")
        print("  │ 0.5-1.0    │ 粗砂         │ 0.05-0.06    │")
        print("  │ 1.0-2.0    │ 细砾         │ 0.06         │")
        print("  │ >2.0       │ 粗砾、卵石   │ 0.06-0.07    │")
        print("  └────────────┴──────────────┴──────────────┘")
        
        print("\n✅ 冲淤判断标准：")
        print("  ┌────────────────┬──────────┬──────────┐")
        print("  │ 条件           │ 判断     │ 趋势     │")
        print("  ├────────────────┼──────────┼──────────┤")
        print("  │ S > S*         │ 超饱和   │ 淤积     │")
        print("  │ S = S*         │ 饱和     │ 平衡     │")
        print("  │ S < S*         │未饱和    │ 冲刷     │")
        print("  │ Qs₁ > Qs₂      │ 输沙减少 │ 淤积     │")
        print("  │ Qs₁ < Qs₂      │ 输沙增加 │ 冲刷     │")
        print("  └────────────────┴──────────┴──────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【泥沙起动题】")
        print("  Step 1: 确定希尔兹数θc")
        print("  Step 2: 计算起动切应力τc=θc(ρs-ρw)gd")
        print("  Step 3: 计算起动流速uc=C√(RJ)")
        print("  Step 4: 判断u与uc大小")
        print("  ")
        print("  【冲淤计算题】")
        print("  Step 1: 计算输沙率Qs=Q×S")
        print("  Step 2: 计算淤积量ΔW=(Qs₁-Qs₂)×Δt")
        print("  Step 3: 计算淤积厚度Δz=ΔW/(γ'×A)")
        print("  Step 4: 挟沙能力分析")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：希尔兹数公式漏掉ρs-ρw")
        print("  ❌ 错误2：起动流速用平均流速公式（应用底层流速）")
        print("  ❌ 错误3：淤积厚度忘记γ'=1.6ρs（孔隙率修正）")
        print("  ❌ 错误4：时间单位不统一（秒、天、年）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：起动题→希尔兹数→起动切应力→起动流速")
        print("  ✓ 技巧2：冲淤题→输沙率→淤积量→淤积厚度")
        print("  ✓ 技巧3：挟沙能力→S与S*比较→冲淤趋势")
        print("  ✓ 技巧4：单位转换→mm/m、kg/吨、s/天")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能准确计算泥沙起动流速")
        print("  □ 掌握输沙率计算")
        print("  □ 理解冲淤计算方法")
        print("  □ 熟练挟沙能力分析")
        
        print("\n📅 明日预告：Day 20 - 环境水力学")
        print("  • 污染物扩散")
        print("  • 河流自净")
        print("  • 水质模型")
        
        print("\n💪 今日格言：")
        print("  「河流动力学是应用题！掌握泥沙计算=拿到16分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 19: 河流动力学")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day19 = Day19RiverDynamics()
    
    # 例题1：泥沙起动
    result1 = day19.example_1_incipient_motion()
    
    # 例题2：泥沙输移
    result2 = day19.example_2_sediment_transport()
    
    # 每日总结
    day19.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 19 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握泥沙起动")
    print(f"  ✓ 掌握输移冲淤")
    print(f"  ✓ 理解挟沙能力")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n🎊🎊🎊 60%里程碑达成！🎊🎊🎊")
    print(f"下一步：Day 20 - 环境水力学")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
