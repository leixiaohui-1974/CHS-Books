#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 21: 第三周测试
Sprint Day 21: Week 3 Test

⏰ 测试时间：3小时
📚 测试范围：
  Day 11-20（第11-20天内容）
  - 明渠流（Day 10-13）
  - 渗流+泵站（Day 15-17）
  - 水工建筑物（Day 18）
  - 河流动力学（Day 19）
  - 环境水力学（Day 20）

🎯 测试目标：
  - 检验第三周学习效果
  - 查漏补缺重点知识
  - 综合应用能力提升
  - 考前模拟训练

💪 今日格言：第三周测试！检验学习成果，冲刺70%里程碑！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day21Week3Test:
    """
    Day 21：第三周测试
    
    包含3个综合测试题：
    1. 综合题1：明渠水面线+临界水深（Day 11-12）
    2. 综合题2：泵站+渗流+水工建筑物（Day 15-18）
    3. 综合题3：河流泥沙+污染扩散（Day 19-20）
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        
    def test_1_channel_profile(self):
        """
        测试题1：明渠水面线综合题⭐⭐⭐⭐⭐
        
        题目：某梯形断面渠道，底宽b=4m，边坡系数m=1.5
              糙率n=0.025，底坡i=0.0004
              流量Q=15m³/s
        求：(1) 正常水深h0和临界水深hc
            (2) 判断水流流态
            (3) 若下游有闸门控制，闸前水深h=3.5m，
                判断水面线类型并计算水面线长度（至h=3.0m）
        
        考点：正常水深、临界水深、水面线分析
        时间：30分钟
        分值：25分
        """
        print("\n" + "="*60)
        print("测试题1：明渠水面线综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 4.0       # 底宽 (m)
        m = 1.5       # 边坡系数
        n = 0.025     # 糙率
        i = 0.0004    # 底坡
        Q = 15.0      # 流量 (m³/s)
        h_gate = 3.5  # 闸前水深 (m)
        h_end = 3.0   # 计算终点水深 (m)
        
        print(f"\n已知条件：")
        print(f"  底宽 b = {b} m")
        print(f"  边坡系数 m = {m}")
        print(f"  糙率 n = {n}")
        print(f"  底坡 i = {i}")
        print(f"  流量 Q = {Q} m³/s")
        print(f"  闸前水深 = {h_gate} m")
        
        # (1) 正常水深
        print(f"\n(1) 计算正常水深h₀：")
        print(f"    ")
        print(f"    正常水深满足：Q = (1/n)AR^(2/3)√i")
        print(f"    ")
        print(f"    梯形断面：")
        print(f"    A = (b+mh)h")
        print(f"    χ = b + 2h√(1+m²)")
        print(f"    R = A/χ")
        print(f"    ")
        print(f"    迭代求解h₀：")
        
        def normal_depth_eq(h):
            A = (b + m * h) * h
            chi = b + 2 * h * np.sqrt(1 + m**2)
            R = A / chi
            return (1/n) * A * R**(2/3) * np.sqrt(i) - Q
        
        # 二分法求解
        h_min, h_max = 0.1, 10.0
        for _ in range(50):
            h0 = (h_min + h_max) / 2
            if normal_depth_eq(h0) > 0:
                h_max = h0
            else:
                h_min = h0
        
        A0 = (b + m * h0) * h0
        chi0 = b + 2 * h0 * np.sqrt(1 + m**2)
        R0 = A0 / chi0
        v0 = Q / A0
        
        print(f"    h₀ = {h0:.3f} m ✓")
        print(f"    A₀ = {A0:.3f} m²")
        print(f"    R₀ = {R0:.3f} m")
        print(f"    v₀ = {v0:.3f} m/s")
        
        # 临界水深
        print(f"\n    计算临界水深hc：")
        print(f"    ")
        print(f"    临界条件：Fr = v/√(gA/B) = 1")
        print(f"    即：Q²B/(gA³) = 1")
        print(f"    ")
        print(f"    梯形断面水面宽：B = b + 2mh")
        print(f"    ")
        print(f"    迭代求解hc：")
        
        def critical_depth_eq(h):
            A = (b + m * h) * h
            B = b + 2 * m * h
            return Q**2 * B / (self.g * A**3) - 1
        
        h_min, h_max = 0.1, 10.0
        for _ in range(50):
            hc = (h_min + h_max) / 2
            if critical_depth_eq(hc) > 0:
                h_max = hc
            else:
                h_min = hc
        
        Ac = (b + m * hc) * hc
        Bc = b + 2 * m * hc
        vc = Q / Ac
        Frc = vc / np.sqrt(self.g * Ac / Bc)
        
        print(f"    hc = {hc:.3f} m ✓")
        print(f"    Ac = {Ac:.3f} m²")
        print(f"    vc = {vc:.3f} m/s")
        print(f"    Frc = {Frc:.3f} (验证≈1)")
        
        # (2) 流态判断
        print(f"\n(2) 流态判断：")
        print(f"    ")
        print(f"    比较h₀与hc：")
        print(f"    h₀ = {h0:.3f} m")
        print(f"    hc = {hc:.3f} m")
        
        if h0 > hc:
            flow_type = "缓流"
            print(f"    h₀ > hc → 缓流 ✓")
            print(f"    Fr₀ = v₀/√(gA₀/B₀) < 1")
        else:
            flow_type = "急流"
            print(f"    h₀ < hc → 急流 ✓")
            print(f"    Fr₀ = v₀/√(gA₀/B₀) > 1")
        
        # (3) 水面线类型
        print(f"\n(3) 水面线分析：")
        print(f"    ")
        print(f"    闸前水深：h = {h_gate} m")
        print(f"    正常水深：h₀ = {h0:.3f} m")
        print(f"    临界水深：hc = {hc:.3f} m")
        print(f"    ")
        print(f"    判断：")
        
        if h_gate > h0 > hc:
            profile_type = "壅水曲线M1型"
            print(f"    h > h₀ > hc → {profile_type} ✓")
            print(f"    特点：水深大于正常水深，向上游壅水")
        elif h0 > h_gate > hc:
            profile_type = "落水曲线M2型"
            print(f"    h₀ > h > hc → {profile_type} ✓")
        else:
            profile_type = "其他类型"
            print(f"    其他类型")
        
        print(f"    ")
        print(f"    水面线长度计算（h={h_gate}m → {h_end}m）：")
        print(f"    ")
        print(f"    标准步长法：")
        print(f"    ΔL = (E₂-E₁)/(i-J̄)")
        print(f"    E = h + v²/(2g)")
        print(f"    J̄ = (J₁+J₂)/2")
        
        # 计算两个断面
        h1 = h_gate
        A1 = (b + m * h1) * h1
        chi1 = b + 2 * h1 * np.sqrt(1 + m**2)
        R1 = A1 / chi1
        v1 = Q / A1
        E1 = h1 + v1**2 / (2 * self.g)
        J1 = (n * v1 / R1**(2/3))**2
        
        h2 = h_end
        A2 = (b + m * h2) * h2
        chi2 = b + 2 * h2 * np.sqrt(1 + m**2)
        R2 = A2 / chi2
        v2 = Q / A2
        E2 = h2 + v2**2 / (2 * self.g)
        J2 = (n * v2 / R2**(2/3))**2
        
        J_avg = (J1 + J2) / 2
        delta_L = (E2 - E1) / (i - J_avg)
        
        print(f"    ")
        print(f"    断面1（h={h1}m）：")
        print(f"      E₁ = {E1:.3f} m")
        print(f"      J₁ = {J1:.6f}")
        print(f"    ")
        print(f"    断面2（h={h2}m）：")
        print(f"      E₂ = {E2:.3f} m")
        print(f"      J₂ = {J2:.6f}")
        print(f"    ")
        print(f"    J̄ = {J_avg:.6f}")
        print(f"    ΔL = ({E2:.3f}-{E1:.3f})/({i}-{J_avg:.6f})")
        print(f"       = {delta_L:.2f} m ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：断面示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 绘制梯形断面
        h_plot = 4.0
        x_bottom = [-m*h_plot, -m*h_plot, b+m*h_plot, b+m*h_plot]
        y_bottom = [-0.5, 0, 0, -0.5]
        x_top = [-m*h_plot, 0, b, b+m*h_plot]
        y_top = [0, h_plot, h_plot, 0]
        
        ax1.fill(x_bottom + x_top[::-1], y_bottom + y_top[::-1],
                color='lightblue', alpha=0.3, edgecolor='black', linewidth=2)
        ax1.plot(x_top, y_top, 'b-', linewidth=2, label='水面')
        
        # 标注
        ax1.text(b/2, -0.3, f'b={b}m', ha='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='yellow'))
        ax1.text(-1, h_plot/2, f'm={m}', fontsize=10, rotation=60)
        ax1.text(b/2, h_plot+0.2, f'B=b+2mh', ha='center', fontsize=10)
        
        # 水深线
        ax1.plot([0, b], [h0, h0], 'g--', linewidth=2, label=f'h₀={h0:.2f}m')
        ax1.plot([0, b], [hc, hc], 'r--', linewidth=2, label=f'hc={hc:.2f}m')
        
        ax1.set_xlabel('宽度 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 21 测试1：梯形断面示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-8, b+8])
        ax1.set_ylim([-1, h_plot+1])
        ax1.set_aspect('equal')
        
        # 子图2：水深对比
        ax2 = plt.subplot(2, 2, 2)
        
        depths = ['正常水深h₀', '临界水深hc', '闸前水深h']
        values = [h0, hc, h_gate]
        colors = ['green', 'red', 'blue']
        
        bars = ax2.bar(depths, values, color=colors, alpha=0.7,
                      edgecolor='black', linewidth=2)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}m',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('水深 (m)', fontsize=12)
        ax2.set_title('水深对比', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 子图3：水面线示意
        ax3 = plt.subplot(2, 2, 3)
        
        # 渠底线
        x_channel = np.linspace(0, 1000, 100)
        y_bottom_line = -i * x_channel
        ax3.plot(x_channel, y_bottom_line, 'k-', linewidth=2, label='渠底')
        
        # 正常水深线
        ax3.plot(x_channel, y_bottom_line + h0, 'g--', linewidth=2,
                label=f'正常水深线（h₀={h0:.2f}m）')
        
        # 水面线（M1型壅水曲线）
        x_profile = np.linspace(0, abs(delta_L), 50)
        # 简化模型：指数型过渡
        h_profile = h_gate - (h_gate - h_end) * (x_profile / abs(delta_L))
        y_profile = -i * x_profile + h_profile
        ax3.plot(x_profile, y_profile, 'b-', linewidth=2.5,
                label=f'实际水面线（{profile_type}）')
        
        # 闸门
        ax3.plot([0, 0], [y_bottom_line[0], y_bottom_line[0]+h_gate],
                'r-', linewidth=4, label='闸门')
        
        ax3.set_xlabel('距离 (m)', fontsize=12)
        ax3.set_ylabel('高程 (m)', fontsize=12)
        ax3.set_title('水面线示意图', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
        
        # 子图4：结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【测试题1结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 水深计算：
            正常水深：h₀ = {h0:.3f} m ✓
            临界水深：hc = {hc:.3f} m ✓
        
        (2) 流态判断：
            h₀ {'>' if h0>hc else '<'} hc
            流态：{flow_type} ✓
        
        (3) 水面线分析：
            类型：{profile_type} ✓
            长度：ΔL = {abs(delta_L):.2f} m ✓
            （从h={h_gate}m到h={h_end}m）
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 正常水深：Q=(1/n)AR^(2/3)√i
          • 临界水深：Q²B/(gA³)=1
          • 水面线：ΔL=(E₂-E₁)/(i-J̄)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        得分：25/25分 ✓
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day21_week3_test/test_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_1.png")
        
        print("\n" + "="*60)
        print("📝 测试题1评分（25分）：")
        print("="*60)
        print("✓ 正常水深计算 (8分)")
        print("✓ 临界水深计算 (7分)")
        print("✓ 流态判断 (3分)")
        print("✓ 水面线类型判断 (4分)")
        print("✓ 水面线长度计算 (3分)")
        
        return {'h0': h0, 'hc': hc, 'flow_type': flow_type,
                'profile_type': profile_type, 'delta_L': delta_L}
    
    def test_2_integrated_problem(self):
        """
        测试题2：泵站+渗流综合题⭐⭐⭐⭐⭐
        
        题目：某水库坝高H=25m，上游水位h1=23m
              坝基透水层渗透系数k=0.8cm/s
              需要设计排水系统和抽水泵站
        求：(1) 若采用排水棱体，计算出逸点高度y0
            (2) 单宽渗流量q
            (3) 需安装水泵，扬程H_pump=30m，流量Q_pump=0.5m³/s
                效率η=75%，计算所需功率N
        
        考点：渗流、排水、泵站
        时间：25分钟
        分值：25分
        """
        print("\n" + "="*60)
        print("测试题2：泵站+渗流综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        H_dam = 25.0    # 坝高 (m)
        h1 = 23.0       # 上游水位 (m)
        k_cm = 0.8      # 渗透系数 (cm/s)
        k = k_cm * 0.01 # 转换为 m/s
        H_pump = 30.0   # 水泵扬程 (m)
        Q_pump = 0.5    # 水泵流量 (m³/s)
        eta = 0.75      # 效率
        
        print(f"\n已知条件：")
        print(f"  坝高 H = {H_dam} m")
        print(f"  上游水位 h₁ = {h1} m")
        print(f"  渗透系数 k = {k_cm} cm/s = {k} m/s")
        print(f"  水泵扬程 H_pump = {H_pump} m")
        print(f"  水泵流量 Q_pump = {Q_pump} m³/s")
        print(f"  水泵效率 η = {eta}")
        
        # (1) 出逸点高度
        print(f"\n(1) 排水棱体出逸点高度：")
        print(f"    ")
        print(f"    经验公式：y₀ ≈ 0.4√(h₁L)")
        print(f"    ")
        print(f"    渗流长度（简化）：")
        print(f"    L ≈ 2H = 2×{H_dam}")
        
        L = 2 * H_dam
        
        print(f"      = {L} m")
        print(f"    ")
        print(f"    无排水设施出逸点：")
        
        y0_no_drain = 0.4 * np.sqrt(h1 * L)
        
        print(f"    y₀ = 0.4√({h1}×{L})")
        print(f"       = {y0_no_drain:.2f} m")
        print(f"    ")
        print(f"    采用排水棱体后：")
        print(f"    y₀' ≈ y₀/2")
        
        y0 = y0_no_drain / 2
        
        print(f"        ≈ {y0_no_drain:.2f}/2")
        print(f"        ≈ {y0:.2f} m ✓")
        
        # (2) 渗流量
        print(f"\n(2) 单宽渗流量：")
        print(f"    ")
        print(f"    渗流量公式：")
        print(f"    q = k(h₁²-y₀²)/(2L)")
        print(f"    ")
        print(f"    代入数据：")
        
        q = k * (h1**2 - y0**2) / (2 * L)
        
        print(f"    q = {k}×({h1}²-{y0:.2f}²)/(2×{L})")
        print(f"      = {k}×({h1**2}-{y0**2:.2f})/{2*L}")
        print(f"      = {q:.6f} m³/(s·m)")
        print(f"      = {q*86400:.4f} m³/(d·m) ✓")
        
        # (3) 泵站功率
        print(f"\n(3) 水泵所需功率：")
        print(f"    ")
        print(f"    水力功率公式：")
        print(f"    N_water = ρgQH = 9.81QH (kW)")
        print(f"    ")
        print(f"    水力功率：")
        
        N_water = 9.81 * Q_pump * H_pump
        
        print(f"    N_water = 9.81×{Q_pump}×{H_pump}")
        print(f"            = {N_water:.2f} kW")
        print(f"    ")
        print(f"    轴功率（考虑效率）：")
        print(f"    N = N_water/η")
        
        N = N_water / eta
        
        print(f"      = {N_water:.2f}/{eta}")
        print(f"      = {N:.2f} kW ✓")
        print(f"      = {N/0.735:.2f} 马力")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：坝体+渗流示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 坝体
        dam_x = [0, 0, 30, 0]
        dam_y = [0, H_dam, 0, 0]
        ax1.fill(dam_x, dam_y, color='gray', alpha=0.5,
                edgecolor='black', linewidth=2, label='坝体')
        
        # 上游水体
        ax1.fill_between([-20, 0], [0, 0], [h1, h1],
                        color='lightblue', alpha=0.5)
        ax1.plot([0, 0], [0, h1], 'b-', linewidth=2, label='上游水位')
        
        # 浸润线（简化）
        x_seep = np.linspace(0, 30, 50)
        y_seep = h1 - (h1 - y0) * (x_seep / 30)**1.5
        ax1.plot(x_seep, y_seep, 'r--', linewidth=2.5, label='浸润线')
        
        # 出逸点
        ax1.plot([30], [y0], 'ro', markersize=12, label=f'出逸点y₀={y0:.1f}m')
        
        # 排水棱体
        ax1.plot([25, 30, 30], [y0, y0, 0], 'g--', linewidth=2,
                label='排水棱体')
        
        ax1.set_xlabel('距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 21 测试2：渗流与排水示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-25, 35])
        ax1.set_ylim([-2, H_dam+3])
        
        # 子图2：水泵特性曲线
        ax2 = plt.subplot(2, 2, 2)
        
        Q_range = np.linspace(0, 1.0, 50)
        # 简化水泵曲线：H = H0 - aQ²
        H0 = 35.0
        a = 20.0
        H_curve = H0 - a * Q_range**2
        
        ax2.plot(Q_range, H_curve, 'b-', linewidth=2.5, label='水泵特性曲线')
        ax2.plot([Q_pump], [H_pump], 'ro', markersize=12,
                label=f'工作点(Q={Q_pump}m³/s, H={H_pump}m)')
        ax2.axhline(y=H_pump, color='red', linestyle='--', linewidth=1.5)
        ax2.axvline(x=Q_pump, color='red', linestyle='--', linewidth=1.5)
        
        ax2.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax2.set_ylabel('扬程 H (m)', fontsize=12)
        ax2.set_title('水泵特性曲线', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3：功率分解
        ax3 = plt.subplot(2, 2, 3)
        
        powers = ['水力功率\nN_water', '轴功率\nN', '损失功率\nΔN']
        values = [N_water, N, N - N_water]
        colors = ['blue', 'green', 'red']
        
        bars = ax3.bar(powers, values, color=colors, alpha=0.7,
                      edgecolor='black', linewidth=2)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}kW',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax3.set_ylabel('功率 (kW)', fontsize=12)
        ax3.set_title('功率分解', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【测试题2结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 排水棱体出逸点：
            无排水：y₀={y0_no_drain:.2f}m
            有排水：y₀'={y0:.2f}m ✓
            降低：{(1-y0/y0_no_drain)*100:.1f}%
        
        (2) 单宽渗流量：
            q = {q:.6f} m³/(s·m)
              = {q*86400:.4f} m³/(d·m) ✓
        
        (3) 水泵功率：
            水力功率：{N_water:.2f} kW
            轴功率：N = {N:.2f} kW ✓
            效率：η = {eta*100}%
            损失：{N-N_water:.2f} kW
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 出逸点：y₀=0.4√(h₁L)
          • 渗流量：q=k(h₁²-y₀²)/(2L)
          • 泵功率：N=ρgQH/η
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        得分：25/25分 ✓
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day21_week3_test/test_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_2.png")
        
        print("\n" + "="*60)
        print("📝 测试题2评分（25分）：")
        print("="*60)
        print("✓ 出逸点高度计算 (10分)")
        print("✓ 渗流量计算 (8分)")
        print("✓ 水泵功率计算 (7分)")
        
        return {'y0': y0, 'q': q, 'N': N}
    
    def test_3_river_pollution(self):
        """
        测试题3：河流泥沙+污染综合题⭐⭐⭐⭐⭐
        
        题目：某河段泥沙粒径d=0.3mm，流速u=0.6m/s，水深h=2.5m
              同时接纳污水排放，排放速率M=5g/s
              河流流量Q=20m³/s，纵向扩散系数Ex=15m²/s
        求：(1) 判断泥沙是否起动（希尔兹数θc=0.05）
            (2) 污染物浓度在下游500m处的数值
            (3) 综合评价河流环境状况
        
        考点：泥沙起动、污染扩散、综合评价
        时间：25分钟
        分值：30分
        """
        print("\n" + "="*60)
        print("测试题3：河流泥沙+污染综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d = 0.3e-3      # 粒径 (m)
        u = 0.6         # 流速 (m/s)
        h = 2.5         # 水深 (m)
        M = 5.0         # 排放速率 (g/s)
        Q = 20.0        # 流量 (m³/s)
        Ex = 15.0       # 扩散系数 (m²/s)
        x_calc = 500.0  # 计算距离 (m)
        theta_c = 0.05  # 希尔兹数
        rho_s = 2650    # 泥沙密度 (kg/m³)
        rho_w = 1000    # 水密度 (kg/m³)
        g = 9.81        # 重力加速度 (m/s²)
        
        print(f"\n已知条件：")
        print(f"  泥沙粒径 d = {d*1000} mm")
        print(f"  流速 u = {u} m/s")
        print(f"  水深 h = {h} m")
        print(f"  排放速率 M = {M} g/s")
        print(f"  流量 Q = {Q} m³/s")
        print(f"  扩散系数 Ex = {Ex} m²/s")
        print(f"  希尔兹数 θc = {theta_c}")
        
        # (1) 泥沙起动
        print(f"\n(1) 泥沙起动判断：")
        print(f"    ")
        print(f"    起动切应力：")
        print(f"    τc = θc(ρs-ρw)gd")
        
        tau_c = theta_c * (rho_s - rho_w) * g * d
        
        print(f"       = {theta_c}×({rho_s}-{rho_w})×{g}×{d}")
        print(f"       = {tau_c:.4f} N/m² ✓")
        print(f"    ")
        print(f"    实际底床切应力：")
        print(f"    假设底坡J≈0.0001（典型值）")
        
        J = 0.0001
        tau = rho_w * g * h * J
        
        print(f"    τ = ρwghJ = {rho_w}×{g}×{h}×{J}")
        print(f"      = {tau:.4f} N/m²")
        print(f"    ")
        print(f"    判断：")
        
        if tau > tau_c:
            sediment_status = "起动"
            print(f"    τ ({tau:.4f}) > τc ({tau_c:.4f})")
            print(f"    泥沙起动，发生输移 ✓")
        else:
            sediment_status = "不起动"
            print(f"    τ ({tau:.4f}) ≤ τc ({tau_c:.4f})")
            print(f"    泥沙不起动 ✓")
        
        # (2) 污染物浓度
        print(f"\n(2) 污染物浓度计算：")
        print(f"    ")
        print(f"    点源扩散公式：")
        print(f"    C(x) = (M/Q)×exp(-ux/(2Ex))")
        print(f"    ")
        print(f"    排放口浓度：")
        
        C0 = (M / Q) * 1000  # 转换为mg/L
        
        print(f"    C(0⁺) = M/Q = {M}/{Q}")
        print(f"          = {M/Q:.3f} g/m³")
        print(f"          = {C0:.2f} mg/L ✓")
        print(f"    ")
        print(f"    下游x={x_calc}m处：")
        print(f"    ")
        print(f"    指数项：")
        
        exponent = -u * x_calc / (2 * Ex)
        
        print(f"    -ux/(2Ex) = -{u}×{x_calc}/(2×{Ex})")
        print(f"              = {exponent:.4f}")
        print(f"    ")
        print(f"    浓度：")
        
        C_x = C0 * np.exp(exponent)
        
        print(f"    C({x_calc}) = {C0:.2f}×exp({exponent:.4f})")
        print(f"             = {C0:.2f}×{np.exp(exponent):.4f}")
        print(f"             = {C_x:.3f} mg/L ✓")
        
        # (3) 综合评价
        print(f"\n(3) 河流环境综合评价：")
        print(f"    ")
        print(f"    泥沙方面：")
        print(f"    • 泥沙状态：{sediment_status}")
        
        if sediment_status == "起动":
            print(f"    • 影响：可能发生河床冲刷，需关注")
            sediment_impact = "中等"
        else:
            print(f"    • 影响：河床相对稳定")
            sediment_impact = "轻微"
        
        print(f"    ")
        print(f"    污染方面：")
        print(f"    • 排放口浓度：{C0:.2f} mg/L")
        print(f"    • 下游500m处：{C_x:.2f} mg/L")
        
        if C_x < 1.0:
            pollution_level = "轻度"
            print(f"    • 污染程度：轻度（C<1mg/L）")
        elif C_x < 5.0:
            pollution_level = "中度"
            print(f"    • 污染程度：中度（1≤C<5mg/L）")
        else:
            pollution_level = "重度"
            print(f"    • 污染程度：重度（C≥5mg/L）")
        
        print(f"    ")
        print(f"    综合评价：")
        print(f"    • 泥沙影响：{sediment_impact}")
        print(f"    • 污染程度：{pollution_level}")
        
        if sediment_impact == "轻微" and pollution_level == "轻度":
            overall = "良好"
            print(f"    • 总体评价：{overall} ✓")
        elif sediment_impact == "中等" or pollution_level == "中度":
            overall = "一般"
            print(f"    • 总体评价：{overall}，需要监测 ✓")
        else:
            overall = "较差"
            print(f"    • 总体评价：{overall}，需要治理 ✓")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：综合示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 河流
        ax1.fill_between([0, 1000], [-0.5, -0.5], [0.5, 0.5],
                        color='lightblue', alpha=0.3)
        ax1.plot([0, 1000], [0, 0], 'b-', linewidth=2)
        
        # 排污口
        ax1.plot([0], [0], 'r*', markersize=20, label='排污口')
        ax1.arrow(0, -0.3, 0, 0.2, head_width=20, head_length=0.05,
                 fc='red', ec='red', linewidth=2)
        
        # 泥沙
        for x in [100, 300, 500, 700, 900]:
            circle = Circle((x, 0), 10, color='brown', alpha=0.6)
            ax1.add_patch(circle)
        
        # 流向
        for x in [200, 500, 800]:
            ax1.arrow(x, 0, 80, 0, head_width=0.08, head_length=30,
                     fc='blue', ec='blue', linewidth=2, alpha=0.6)
        
        ax1.text(500, 0.35, f'u={u}m/s', fontsize=11,
                ha='center', color='blue', fontweight='bold')
        
        # 标注
        ax1.plot([x_calc], [0], 'go', markersize=12)
        ax1.text(x_calc, -0.35, f'x={x_calc}m\nC={C_x:.2f}mg/L',
                fontsize=10, ha='center', color='green',
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        ax1.set_xlabel('距离 (m)', fontsize=12)
        ax1.set_ylabel('横向 (m)', fontsize=12)
        ax1.set_title('Day 21 测试3：河流泥沙+污染示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-50, 1050])
        ax1.set_ylim([-0.6, 0.6])
        
        # 子图2：浓度分布
        ax2 = plt.subplot(2, 2, 2)
        
        x_range = np.linspace(0.1, 2000, 200)
        C_range = C0 * np.exp(-u * x_range / (2 * Ex))
        
        ax2.plot(x_range, C_range, 'b-', linewidth=2.5, label='浓度分布')
        ax2.plot([x_calc], [C_x], 'ro', markersize=12,
                label=f'x={x_calc}m: C={C_x:.2f}mg/L')
        
        # 污染等级线
        ax2.axhline(y=1.0, color='green', linestyle='--', linewidth=2,
                   label='轻度/中度分界线')
        ax2.axhline(y=5.0, color='orange', linestyle='--', linewidth=2,
                   label='中度/重度分界线')
        
        ax2.set_xlabel('距离 (m)', fontsize=12)
        ax2.set_ylabel('浓度 (mg/L)', fontsize=12)
        ax2.set_title('污染物浓度分布', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 2000])
        
        # 子图3：综合评价雷达图
        ax3 = plt.subplot(2, 2, 3, projection='polar')
        
        categories = ['泥沙影响', '污染程度', '扩散能力', '自净能力', '生态影响']
        N_cats = len(categories)
        
        # 评分（0-10分）
        scores = [3 if sediment_status=="起动" else 1,
                 1 if C_x<1 else (3 if C_x<5 else 7),
                 7,  # 扩散能力较好
                 6,  # 自净能力一般
                 2 if overall=="良好" else 5]
        
        angles = np.linspace(0, 2 * np.pi, N_cats, endpoint=False).tolist()
        scores += scores[:1]
        angles += angles[:1]
        
        ax3.plot(angles, scores, 'b-', linewidth=2, label='实际状态')
        ax3.fill(angles, scores, 'b', alpha=0.25)
        ax3.set_xticks(angles[:-1])
        ax3.set_xticklabels(categories, fontsize=9)
        ax3.set_ylim(0, 10)
        ax3.set_title('河流环境综合评价', fontsize=13, fontweight='bold', pad=20)
        ax3.legend(loc='upper right')
        ax3.grid(True)
        
        # 子图4：结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【测试题3结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 泥沙起动判断：
            τc = {tau_c:.4f} N/m²
            τ = {tau:.4f} N/m²
            判断：{sediment_status} ✓
        
        (2) 污染物浓度：
            C(0⁺) = {C0:.2f} mg/L
            C({x_calc}m) = {C_x:.3f} mg/L ✓
        
        (3) 综合评价：
            泥沙影响：{sediment_impact}
            污染程度：{pollution_level}
            总体评价：{overall} ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 起动：τc=θc(ρs-ρw)gd
          • 扩散：C(x)=(M/Q)×exp(-ux/(2Ex))
          • 评价：综合多因素分析
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        得分：30/30分 ✓
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day21_week3_test/test_3.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_3.png")
        
        print("\n" + "="*60)
        print("📝 测试题3评分（30分）：")
        print("="*60)
        print("✓ 泥沙起动判断 (12分)")
        print("✓ 污染物浓度计算 (10分)")
        print("✓ 综合评价分析 (8分)")
        
        return {'sediment_status': sediment_status, 'C_x': C_x, 'overall': overall}
    
    def summary_and_tips(self):
        """测试总结"""
        print("\n" + "="*60)
        print("📚 第三周测试总结")
        print("="*60)
        
        print("\n✅ 测试统计：")
        print("  测试题1（明渠水面线）：25分")
        print("  测试题2（泵站+渗流）：25分")
        print("  测试题3（河流+污染）：30分")
        print("  ━━━━━━━━━━━━━━━━━━━━━━")
        print("  总分：80分")
        
        print("\n✅ 知识点覆盖：")
        print("  ✓ 明渠流：正常水深、临界水深、水面线")
        print("  ✓ 渗流：出逸点、渗流量、排水设施")
        print("  ✓ 泵站：水泵特性、功率计算")
        print("  ✓ 河流：泥沙起动、输沙")
        print("  ✓ 环境：污染扩散、水质评价")
        
        print("\n✅ 第三周核心公式回顾：")
        print("  1. 正常水深：Q = (1/n)AR^(2/3)√i")
        print("  2. 临界水深：Q²B/(gA³) = 1")
        print("  3. 渗流：q = k(h₁²-y₀²)/(2L)")
        print("  4. 泵功率：N = ρgQH/η")
        print("  5. 泥沙起动：τc = θc(ρs-ρw)gd")
        print("  6. 污染扩散：C(x) = (M/Q)×exp(-ux/(2Ex))")
        
        print("\n⚠️ 常见易错点：")
        print("  ❌ 正常水深vs临界水深：别搞混计算方法")
        print("  ❌ 渗流出逸点：y₀=0.4√(h₁L)，别忘根号")
        print("  ❌ 泵功率：N=ρgQH/η，注意除以η")
        print("  ❌ 污染扩散：注意2Ex，不是Ex")
        
        print("\n🎯 学习建议：")
        print("  ✓ 复习第11-20天笔记")
        print("  ✓ 重做典型例题")
        print("  ✓ 总结公式卡片")
        print("  ✓ 查漏补缺薄弱点")
        
        print("\n💪 今日格言：")
        print("  「第三周测试完成！检验学习成果，冲刺70%里程碑！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 21: 第三周测试")
    print("="*60)
    print("\n⏰ 测试时间：3小时")
    print("📚 测试范围：Day 11-20")
    print("💯 总分：80分")
    
    # 创建对象
    day21 = Day21Week3Test()
    
    # 测试题1
    result1 = day21.test_1_channel_profile()
    
    # 测试题2
    result2 = day21.test_2_integrated_problem()
    
    # 测试题3
    result3 = day21.test_3_river_pollution()
    
    # 测试总结
    day21.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ 第三周测试完成！")
    print("="*60)
    print(f"\n测试成果：")
    print(f"  ✓ 完成3道综合测试题")
    print(f"  ✓ 覆盖5个知识模块")
    print(f"  ✓ 检验学习效果")
    print(f"  ✓ 生成12张图表")
    
    print(f"\n🎊🎊🎊 70%里程碑达成！🎊🎊🎊")
    print(f"下一步：Day 22 - 继续冲刺")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
