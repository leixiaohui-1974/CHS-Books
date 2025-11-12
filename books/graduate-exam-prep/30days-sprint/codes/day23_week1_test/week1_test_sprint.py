#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 23: 第一周测试
Sprint Day 23: Week 1 Comprehensive Test (Day 1-10)

⏰ 考试时间：3小时
📚 测试范围：
  Day 1-3: 静水力学（静水压强、曲面压力、浮力、闸门力）
  Day 4-6: 水动力学基础（伯努利方程、连续性、动量方程）
  Day 8-10: 管流与明渠流（管道阻力、有压管流、明渠均匀流）

🎯 测试目标：
  - 检验第一周学习效果
  - 查漏补缺
  - 巩固核心公式
  - 提高解题速度

💪 考试格言：第一周测试=基础检验！掌握基础=确保80分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon, Wedge
import matplotlib.patches as mpatches
from scipy.optimize import fsolve

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day23Week1Test:
    """
    Day 23：第一周测试
    
    包含3个综合测试题：
    1. 静水力学综合题（30分）
    2. 水动力学综合题（35分）
    3. 明渠流综合题（35分）
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho_w = 1000  # 水的密度 (kg/m³)
        self.gamma_w = self.rho_w * self.g  # 水的重度 (N/m³)
        
    def test_1_hydrostatics_comprehensive(self):
        """
        测试题1：静水力学综合题⭐⭐⭐⭐⭐
        
        题目：水库闸门结构如图：
              矩形闸门AB，宽度b=4m，高度h=5m
              门顶A处水深h1=2m，门底B处水深h2=7m
              闸门绕铰链A转动，后侧有圆柱形浮体辅助启闭
              浮体直径D=1.2m，长度L=4m，材料密度ρ=600kg/m³
        求：(1) 闸门上的静水总压力及作用点
            (2) 浮体的浮力和露出水面高度
            (3) 启闭闸门所需的力矩（浮体协助）
        
        考点：静水总压力、压力中心、浮力、力矩平衡
        难度：综合（第一周核心！）
        时间：35分钟
        分值：30分
        """
        print("\n" + "="*60)
        print("测试题1：静水力学综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 4.0       # 闸门宽度 (m)
        h = 5.0       # 闸门高度 (m)
        h1 = 2.0      # 门顶水深 (m)
        h2 = 7.0      # 门底水深 (m)
        D = 1.2       # 浮体直径 (m)
        L_float = 4.0 # 浮体长度 (m)
        rho_float = 600  # 浮体密度 (kg/m³)
        
        print(f"\n已知条件：")
        print(f"  闸门：宽度b={b}m, 高度h={h}m")
        print(f"  水深：门顶h₁={h1}m, 门底h₂={h2}m")
        print(f"  浮体：直径D={D}m, 长度L={L_float}m, 密度ρ={rho_float}kg/m³")
        
        # (1) 静水总压力及作用点
        print(f"\n解题步骤：")
        print(f"\n(1) 计算闸门上的静水总压力")
        
        # 形心处水深
        hc = (h1 + h2) / 2
        print(f"  形心水深：hc = (h₁+h₂)/2 = ({h1}+{h2})/2 = {hc} m")
        
        # 面积
        A = b * h
        print(f"  闸门面积：A = b×h = {b}×{h} = {A} m²")
        
        # 总压力
        P = self.gamma_w * hc * A
        print(f"  总压力：P = γhcA = {self.gamma_w}×{hc}×{A}")
        print(f"         = {P:.1f} N = {P/1000:.1f} kN ✓")
        
        # 压力中心
        # Ic = bh³/12
        Ic = b * h**3 / 12
        print(f"\n  惯性矩：Ic = bh³/12 = {b}×{h}³/12 = {Ic:.2f} m⁴")
        
        # e = Ic/(hc×A)
        e = Ic / (hc * A)
        print(f"  偏心距：e = Ic/(hcA) = {Ic:.2f}/({hc}×{A})")
        print(f"         = {e:.3f} m")
        
        # 压力中心距形心的距离
        yD = hc + e
        print(f"  压力中心距水面：yD = hc+e = {hc}+{e:.3f} = {yD:.3f} m")
        
        # 压力中心距门顶A的距离
        yD_from_A = yD - h1
        print(f"  压力中心距门顶A：yD-h₁ = {yD:.3f}-{h1} = {yD_from_A:.3f} m ✓")
        
        # (2) 浮体浮力和露出高度
        print(f"\n(2) 计算浮体的浮力")
        
        # 浮体体积
        V_float = np.pi * (D/2)**2 * L_float
        print(f"  浮体体积：V = πD²L/4 = π×{D}²×{L_float}/4 = {V_float:.3f} m³")
        
        # 浮体重量
        G_float = rho_float * self.g * V_float
        print(f"  浮体重量：G = ρgV = {rho_float}×{self.g}×{V_float:.3f}")
        print(f"           = {G_float:.1f} N = {G_float/1000:.1f} kN")
        
        # 浮力等于重量（漂浮）
        F_buoy = G_float
        print(f"  浮力：F浮 = G = {F_buoy:.1f} N = {F_buoy/1000:.1f} kN ✓")
        
        # 浸入水中的体积
        V_sub = G_float / (self.rho_w * self.g)
        print(f"\n  浸入体积：V浸 = G/(ρ水g) = {G_float:.1f}/({self.rho_w}×{self.g})")
        print(f"           = {V_sub:.3f} m³")
        
        # 浸入深度（圆柱体横卧在水面，使用简化计算）
        # 浸入率 = ρ浮体/ρ水
        submersion_ratio = rho_float / self.rho_w
        h_sub = D * submersion_ratio
        print(f"  浸入率：ρ浮/ρ水 = {rho_float}/{self.rho_w} = {submersion_ratio:.3f}")
        print(f"  浸入深度：h浸 = D×浸入率 = {D}×{submersion_ratio:.3f}")
        print(f"           = {h_sub:.3f} m")
        
        # 露出高度
        h_above = D - h_sub
        print(f"  露出高度：h露 = D-h浸 = {D}-{h_sub:.3f} = {h_above:.3f} m ✓")
        
        # (3) 启闭力矩
        print(f"\n(3) 计算启闭闸门所需力矩")
        
        # 水压力对A点的力矩（顺时针，阻力）
        M_water = P * yD_from_A
        print(f"  水压力矩：M水 = P×yD = {P:.1f}×{yD_from_A:.3f}")
        print(f"           = {M_water:.1f} N·m = {M_water/1000:.1f} kN·m")
        
        # 假设浮体通过杆连接在门底B处（简化模型）
        # 浮力对A点的力矩（逆时针，助力）
        arm_float = h  # 力臂为闸门高度
        M_float = F_buoy * arm_float
        print(f"\n  浮体力臂：L臂 = h = {h} m")
        print(f"  浮力力矩：M浮 = F浮×L臂 = {F_buoy:.1f}×{h}")
        print(f"           = {M_float:.1f} N·m = {M_float/1000:.1f} kN·m")
        
        # 所需启闭力矩
        M_required = M_water - M_float
        print(f"\n  所需力矩：M需 = M水-M浮 = {M_water:.1f}-{M_float:.1f}")
        print(f"           = {M_required:.1f} N·m = {M_required/1000:.1f} kN·m ✓")
        
        if M_required > 0:
            print(f"\n  结论：需施加顺时针力矩{M_required/1000:.1f}kN·m以启闭闸门")
        else:
            print(f"\n  结论：浮体助力足够，无需额外力矩")
        
        # 绘图
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：闸门受力示意图
        ax1 = plt.subplot(2, 3, 1)
        
        # 水体
        water_top = h1
        water_bottom = -h + h1
        ax1.fill_between([0, 2], [water_top, water_top], 
                        [water_bottom, water_bottom],
                        color='cyan', alpha=0.3, label='水体')
        ax1.axhline(y=water_top, color='blue', linestyle='--', 
                   linewidth=2, label='水面')
        
        # 闸门
        gate_x = [1, 1.3, 1.3, 1]
        gate_y = [h1, h1, h1-h, h1-h]
        ax1.fill(gate_x, gate_y, color='gray', alpha=0.5, 
                edgecolor='black', linewidth=2, label='闸门')
        
        # 铰链A
        ax1.plot(1, h1, 'ro', markersize=15, label='铰链A')
        ax1.text(0.7, h1, 'A', fontsize=14, fontweight='bold')
        
        # 底部B
        ax1.plot(1, h1-h, 'ko', markersize=10)
        ax1.text(0.7, h1-h, 'B', fontsize=14, fontweight='bold')
        
        # 总压力P
        P_y = h1 - yD_from_A
        ax1.arrow(1.3, P_y, 0.5, 0, head_width=0.2, head_length=0.1,
                 fc='red', ec='red', linewidth=3)
        ax1.text(2.0, P_y, f'P={P/1000:.1f}kN', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 标注水深
        ax1.plot([0.5, 0.5], [water_top, h1], 'k-', linewidth=2)
        ax1.text(0.3, (water_top+h1)/2, f'h₁={h1}m', fontsize=10)
        
        ax1.plot([0.5, 0.5], [water_top, h1-h], 'k-', linewidth=2)
        ax1.text(0.2, (water_top+h1-h)/2, f'h₂={h2}m', fontsize=10)
        
        ax1.set_xlabel('X (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('测试题1：闸门受力示意图', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 子图2：浮体示意图
        ax2 = plt.subplot(2, 3, 2)
        
        # 水面
        ax2.axhline(y=0, color='blue', linestyle='--', linewidth=2, label='水面')
        ax2.fill_between([-1, 1], [0, 0], [-2, -2], 
                        color='cyan', alpha=0.3, label='水体')
        
        # 浮体（圆柱侧视图）
        float_top = h_above
        float_bottom = -h_sub
        float_rect = Rectangle((-L_float/2/2, float_bottom), L_float/2, D,
                              facecolor='orange', alpha=0.6,
                              edgecolor='black', linewidth=2, label='浮体')
        ax2.add_patch(float_rect)
        
        # 重力
        ax2.arrow(0, float_top, 0, -0.3, head_width=0.15, head_length=0.1,
                 fc='green', ec='green', linewidth=3)
        ax2.text(0.3, float_top-0.15, f'G={G_float/1000:.1f}kN',
                fontsize=11, bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        # 浮力
        ax2.arrow(0, float_bottom, 0, 0.3, head_width=0.15, head_length=0.1,
                 fc='red', ec='red', linewidth=3)
        ax2.text(0.3, float_bottom+0.15, f'F浮={F_buoy/1000:.1f}kN',
                fontsize=11, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 标注
        ax2.plot([L_float/4, L_float/4], [0, float_top], 'k-', linewidth=2)
        ax2.text(L_float/4+0.1, float_top/2, f'露出\n{h_above:.2f}m', fontsize=10)
        
        ax2.plot([L_float/4, L_float/4], [0, float_bottom], 'k-', linewidth=2)
        ax2.text(L_float/4+0.1, float_bottom/2, f'浸入\n{h_sub:.2f}m', fontsize=10)
        
        ax2.set_xlabel('长度 (m)', fontsize=12)
        ax2.set_ylabel('高程 (m)', fontsize=12)
        ax2.set_title('浮体浮力分析', fontsize=13, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)
        
        # 子图3：力矩平衡图
        ax3 = plt.subplot(2, 3, 3)
        
        # 力矩数据
        moments = [M_water/1000, -M_float/1000, M_required/1000]
        labels = ['水压力矩', '浮力力矩', '所需力矩']
        colors = ['red', 'green', 'orange']
        
        bars = ax3.bar(labels, moments, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, moment in zip(bars, moments):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{abs(moment):.1f}kN·m',
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=11, fontweight='bold')
        
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax3.set_ylabel('力矩 (kN·m)', fontsize=12)
        ax3.set_title('力矩平衡分析', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：压力分布图
        ax4 = plt.subplot(2, 3, 4)
        
        # 深度数组
        depths = np.linspace(h1, h2, 100)
        pressures = self.gamma_w * depths / 1000  # kPa
        
        ax4.plot(pressures, depths, 'b-', linewidth=3, label='压强分布')
        ax4.fill_betweenx(depths, 0, pressures, alpha=0.3, color='blue')
        
        # 标注压力中心
        p_D = self.gamma_w * yD / 1000
        ax4.plot(p_D, yD, 'ro', markersize=15, label=f'压力中心(yD={yD:.2f}m)')
        
        # 标注形心
        p_c = self.gamma_w * hc / 1000
        ax4.plot(p_c, hc, 'go', markersize=12, label=f'形心(hc={hc:.1f}m)')
        
        ax4.set_xlabel('压强 (kPa)', fontsize=12)
        ax4.set_ylabel('水深 (m)', fontsize=12)
        ax4.set_title('静水压强分布', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.invert_yaxis()
        
        # 子图5：浮体浸入比例
        ax5 = plt.subplot(2, 3, 5)
        
        # 饼图
        sizes = [h_sub, h_above]
        labels_pie = [f'浸入\n{h_sub:.2f}m\n({h_sub/D*100:.1f}%)', 
                     f'露出\n{h_above:.2f}m\n({h_above/D*100:.1f}%)']
        colors_pie = ['cyan', 'orange']
        explode = (0.05, 0.05)
        
        ax5.pie(sizes, explode=explode, labels=labels_pie, colors=colors_pie,
               autopct='', shadow=True, startangle=90)
        ax5.set_title('浮体浸入比例', fontsize=13, fontweight='bold')
        
        # 子图6：结果汇总
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        summary_text = f"""
        【测试题1结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 闸门静水总压力：
        
          形心水深：hc = {hc} m
          总压力：P = {P/1000:.1f} kN ✓
          压力中心：yD = {yD:.3f} m
          距门顶：{yD_from_A:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (2) 浮体浮力分析：
        
          浮体重量：G = {G_float/1000:.1f} kN
          浮力：F浮 = {F_buoy/1000:.1f} kN ✓
          浸入深度：{h_sub:.3f} m
          露出高度：{h_above:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (3) 启闭力矩：
        
          水压力矩：{M_water/1000:.1f} kN·m
          浮力力矩：{M_float/1000:.1f} kN·m
          所需力矩：{M_required/1000:.1f} kN·m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        评分：30分
          (1) 10分  (2) 10分  (3) 10分
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax6.text(0.1, 0.95, summary_text, fontsize=9, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day23_week1_test/test_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_1.png")
        
        return {'P': P, 'yD': yD, 'F_buoy': F_buoy, 'h_above': h_above, 'M_required': M_required}
    
    def test_2_hydrodynamics_comprehensive(self):
        """
        测试题2：水动力学综合题⭐⭐⭐⭐⭐
        
        题目：虹吸管系统：
              水库水位H1=10m，虹吸管顶部高程H2=12m
              出口高程H3=2m，管径d=0.3m，λ=0.025
              管长：进口至顶部L1=5m，顶部至出口L2=15m
              局部损失：进口ξ1=0.5，顶部弯管ξ2=0.3，出口ξ3=1.0
        求：(1) 虹吸管流量
            (2) 顶部压强（判断是否会气蚀）
            (3) 出口射流对挡板的冲击力（挡板垂直射流）
        
        考点：伯努利方程、管道损失、动量方程
        难度：综合（必考！）
        时间：40分钟
        分值：35分
        """
        print("\n" + "="*60)
        print("测试题2：水动力学综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        H1 = 10.0     # 水库水位 (m)
        H2 = 12.0     # 虹吸管顶部高程 (m)
        H3 = 2.0      # 出口高程 (m)
        d = 0.3       # 管径 (m)
        lam = 0.025   # 沿程阻力系数
        L1 = 5.0      # 进口至顶部管长 (m)
        L2 = 15.0     # 顶部至出口管长 (m)
        xi1 = 0.5     # 进口局部损失系数
        xi2 = 0.3     # 顶部弯管损失系数
        xi3 = 1.0     # 出口损失系数
        
        print(f"\n已知条件：")
        print(f"  水位：H₁={H1}m, H₂={H2}m, H₃={H3}m")
        print(f"  管道：d={d}m, λ={lam}")
        print(f"  管长：L₁={L1}m, L₂={L2}m")
        print(f"  局部损失：ξ₁={xi1}, ξ₂={xi2}, ξ₃={xi3}")
        
        # (1) 计算流量
        print(f"\n解题步骤：")
        print(f"\n(1) 计算虹吸管流量")
        
        print(f"\n列伯努利方程（水库水面1-1至出口3-3）：")
        print(f"  H₁ + 0 + 0 = H₃ + v₃²/(2g) + hf")
        print(f"  hf = Σ(λL/d + Σξ)×v²/(2g)")
        
        # 总损失系数
        K_total = lam * (L1 + L2) / d + xi1 + xi2 + xi3
        print(f"\n  总损失系数：K = λ(L₁+L₂)/d + ξ₁ + ξ₂ + ξ₃")
        print(f"              = {lam}×({L1}+{L2})/{d} + {xi1} + {xi2} + {xi3}")
        print(f"              = {K_total:.3f}")
        
        # 流速
        v = np.sqrt(2 * self.g * (H1 - H3) / (1 + K_total))
        print(f"\n  流速：v = √[2g(H₁-H₃)/(1+K)]")
        print(f"       = √[2×{self.g}×({H1}-{H3})/(1+{K_total:.3f})]")
        print(f"       = {v:.3f} m/s ✓")
        
        # 流量
        A = np.pi * d**2 / 4
        Q = v * A
        print(f"\n  管道面积：A = πd²/4 = π×{d}²/4 = {A:.4f} m²")
        print(f"  流量：Q = vA = {v:.3f}×{A:.4f}")
        print(f"       = {Q:.4f} m³/s = {Q*1000:.2f} L/s ✓")
        
        # (2) 顶部压强
        print(f"\n(2) 计算顶部压强")
        
        print(f"\n列伯努利方程（水库1-1至顶部2-2）：")
        print(f"  H₁ = H₂ + v²/(2g) + p₂/(γw) + hf₁₂")
        
        # 进口至顶部的损失
        hf_12 = (lam * L1 / d + xi1) * v**2 / (2 * self.g)
        print(f"\n  进口至顶部损失：hf₁₂ = (λL₁/d + ξ₁)×v²/(2g)")
        print(f"                   = ({lam}×{L1}/{d} + {xi1})×{v:.3f}²/(2×{self.g})")
        print(f"                   = {hf_12:.3f} m")
        
        # 顶部压强水头
        p2_head = H1 - H2 - v**2 / (2 * self.g) - hf_12
        print(f"\n  压强水头：p₂/γ = H₁ - H₂ - v²/(2g) - hf₁₂")
        print(f"           = {H1} - {H2} - {v**2/(2*self.g):.3f} - {hf_12:.3f}")
        print(f"           = {p2_head:.3f} m")
        
        # 绝对压强
        p2_abs = (p2_head + 10.0) * self.gamma_w  # 假设大气压10m水柱
        p2_gauge = p2_head * self.gamma_w
        
        print(f"\n  相对压强：p₂ = {p2_gauge/1000:.2f} kPa ✓")
        print(f"  绝对压强：p₂(abs) = {p2_abs/1000:.2f} kPa")
        
        # 判断气蚀
        p_vapor = 2.34 * 1000  # 20°C水的饱和蒸汽压 ≈ 2.34 kPa
        print(f"\n  饱和蒸汽压：pv ≈ 2.34 kPa")
        if p2_abs > p_vapor:
            print(f"  判断：p₂(abs) = {p2_abs/1000:.2f} kPa > pv = {p_vapor/1000:.2f} kPa")
            print(f"       不会发生气蚀 ✓")
            cavitation = False
        else:
            print(f"  判断：p₂(abs) = {p2_abs/1000:.2f} kPa < pv = {p_vapor/1000:.2f} kPa")
            print(f"       会发生气蚀！⚠️")
            cavitation = True
        
        # (3) 冲击力
        print(f"\n(3) 计算射流对挡板的冲击力")
        
        print(f"\n应用动量方程（挡板垂直射流，水平方向）：")
        print(f"  F = ρQv")
        
        F = self.rho_w * Q * v
        print(f"  冲击力：F = ρQv = {self.rho_w}×{Q:.4f}×{v:.3f}")
        print(f"         = {F:.1f} N = {F/1000:.2f} kN ✓")
        
        # 绘图
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：虹吸管系统示意图
        ax1 = plt.subplot(2, 3, 1)
        
        # 水库
        ax1.fill_between([0, 3], [H1, H1], [0, 0], 
                        color='cyan', alpha=0.3, label='水库')
        ax1.axhline(y=H1, color='blue', linestyle='--', linewidth=2, label='水面')
        
        # 虹吸管
        x_pipe = [1, 1, 2.5, 2.5, 6, 6]
        y_pipe = [H1, H2, H2, H2, H3, H3]
        ax1.plot(x_pipe, y_pipe, 'k-', linewidth=4, label='虹吸管')
        
        # 关键点
        ax1.plot(1, H1, 'ro', markersize=12, label='进口1')
        ax1.plot(2.5, H2, 'go', markersize=12, label='顶部2')
        ax1.plot(6, H3, 'bo', markersize=12, label='出口3')
        
        # 标注
        ax1.text(0.5, H1, f'H₁={H1}m', fontsize=11, 
                bbox=dict(boxstyle='round', facecolor='yellow'))
        ax1.text(3, H2+0.3, f'H₂={H2}m', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        ax1.text(6.5, H3, f'H₃={H3}m', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        # 射流
        ax1.arrow(6, H3, 1, 0, head_width=0.3, head_length=0.2,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(7.5, H3, f'v={v:.2f}m/s', fontsize=10)
        
        # 挡板
        ax1.plot([8, 8], [H3-0.5, H3+0.5], 'k-', linewidth=6, label='挡板')
        
        ax1.set_xlabel('距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('测试题2：虹吸管系统示意图', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-0.5, 9)
        ax1.set_ylim(-0.5, 13)
        
        # 子图2：能量线与水力坡度线
        ax2 = plt.subplot(2, 3, 2)
        
        # 位置
        x_stations = [0, 1, 2.5, 6]
        z_stations = [H1, H1, H2, H3]
        
        # 测压管水头线
        v2_2g = v**2 / (2 * self.g)
        hf_total = K_total * v2_2g
        
        H_total_1 = H1
        H_total_2 = H1 - (lam * L1 / d + xi1) * v2_2g
        H_total_3 = H_total_2 - (lam * L2 / d + xi2 + xi3) * v2_2g
        
        p_heads = [0, 0, p2_head, 0]
        H_totals = [H_total_1, H_total_2, H_total_2, H_total_3]
        H_lines = [h + z for h, z in zip(p_heads, z_stations)]
        
        # 总水头线（能量线）
        ax2.plot(x_stations, H_totals, 'r-o', linewidth=2.5, 
                markersize=10, label='总水头线（能量线）')
        
        # 测压管水头线
        ax2.plot(x_stations, H_lines, 'g-s', linewidth=2.5,
                markersize=10, label='测压管水头线')
        
        # 管道中心线
        ax2.plot(x_pipe, y_pipe, 'b-', linewidth=3, label='管道中心线')
        
        # 标注
        for i, (x, H_t, H_p, z) in enumerate(zip(x_stations, H_totals, H_lines, z_stations)):
            ax2.text(x, H_t+0.3, f'{H_t:.1f}m', fontsize=9, ha='center')
            if i == 2:  # 顶部
                ax2.text(x, H_p-0.5, f'{H_p:.1f}m', fontsize=9, ha='center',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax2.set_xlabel('距离 (m)', fontsize=12)
        ax2.set_ylabel('高程/水头 (m)', fontsize=12)
        ax2.set_title('能量线与水力坡度线', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3：压强分布
        ax3 = plt.subplot(2, 3, 3)
        
        stations = ['水库', '进口', '顶部', '出口']
        pressures = [0, 0, p2_gauge/1000, 0]  # kPa (相对压强)
        colors_p = ['blue' if p >= 0 else 'red' for p in pressures]
        
        bars = ax3.bar(stations, pressures, color=colors_p, alpha=0.7, 
                      edgecolor='black', linewidth=2)
        
        # 标注
        for bar, p in zip(bars, pressures):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{p:.2f}kPa',
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=11, fontweight='bold')
        
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax3.axhline(y=-2.34, color='red', linestyle='--', linewidth=2, 
                   label=f'饱和蒸汽压({-2.34:.2f}kPa)')
        ax3.set_ylabel('相对压强 (kPa)', fontsize=12)
        ax3.set_title('各断面压强分布', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：动量分析
        ax4 = plt.subplot(2, 3, 4)
        
        # 射流与挡板
        # 射流
        ax4.arrow(0, 0, 2, 0, head_width=0.3, head_length=0.2,
                 fc='blue', ec='blue', linewidth=3, label='射流')
        ax4.text(1, -0.5, f'v={v:.2f}m/s\nQ={Q*1000:.1f}L/s', 
                ha='center', fontsize=10)
        
        # 挡板
        ax4.plot([3, 3], [-1, 1], 'k-', linewidth=10, label='挡板')
        
        # 冲击力
        ax4.arrow(3, 0, -0.5, 0, head_width=0.2, head_length=0.15,
                 fc='red', ec='red', linewidth=3)
        ax4.text(2.5, 0.5, f'F={F/1000:.2f}kN', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
                fontweight='bold')
        
        ax4.set_xlabel('X', fontsize=12)
        ax4.set_ylabel('Y', fontsize=12)
        ax4.set_title('射流冲击力分析', fontsize=13, fontweight='bold')
        ax4.legend(loc='upper right', fontsize=10)
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim(-0.5, 4)
        ax4.set_ylim(-1.5, 1.5)
        ax4.set_aspect('equal')
        
        # 子图5：损失分配
        ax5 = plt.subplot(2, 3, 5)
        
        # 各部分损失
        hf_inlet = xi1 * v2_2g
        hf_L1 = lam * L1 / d * v2_2g
        hf_bend = xi2 * v2_2g
        hf_L2 = lam * L2 / d * v2_2g
        hf_outlet = xi3 * v2_2g
        
        losses = [hf_inlet, hf_L1, hf_bend, hf_L2, hf_outlet]
        labels_loss = ['进口', '管段1', '弯管', '管段2', '出口']
        colors_loss = ['red', 'orange', 'yellow', 'green', 'blue']
        
        ax5.pie(losses, labels=labels_loss, colors=colors_loss,
               autopct=lambda p: f'{p:.1f}%\n{p*sum(losses)/100:.2f}m',
               shadow=True, startangle=90)
        ax5.set_title('水头损失分配', fontsize=13, fontweight='bold')
        
        # 子图6：结果汇总
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        cavitation_text = "不会气蚀 ✓" if not cavitation else "会气蚀 ⚠️"
        
        summary_text = f"""
        【测试题2结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 虹吸管流量：
        
          总损失系数：K = {K_total:.3f}
          流速：v = {v:.3f} m/s ✓
          流量：Q = {Q:.4f} m³/s
               = {Q*1000:.2f} L/s ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (2) 顶部压强：
        
          压强水头：{p2_head:.3f} m
          相对压强：{p2_gauge/1000:.2f} kPa ✓
          绝对压强：{p2_abs/1000:.2f} kPa
          
          气蚀判断：{cavitation_text}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (3) 冲击力：
        
          动量方程：F = ρQv
          冲击力：F = {F:.1f} N
                = {F/1000:.2f} kN ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        评分：35分
          (1) 12分  (2) 13分  (3) 10分
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax6.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day23_week1_test/test_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_2.png")
        
        return {'Q': Q, 'v': v, 'p2': p2_gauge, 'cavitation': cavitation, 'F': F}
    
    def test_3_channel_flow_comprehensive(self):
        """
        测试题3：明渠流综合题⭐⭐⭐⭐⭐
        
        题目：梯形渠道：
              底宽b=5m，边坡m=1.5，糙率n=0.025
              底坡i=0.001，流量Q=20m³/s
              下游有跌坎，跌坎高度Δz=1.5m
        求：(1) 正常水深h0和临界水深hc
            (2) 判断流态，计算跌坎上游水深
            (3) 若发生水跃，计算跃后水深和水跃长度
            (4) 单宽能量损失
        
        考点：明渠均匀流、临界水深、水跃
        难度：综合（重点！）
        时间：45分钟
        分值：35分
        """
        print("\n" + "="*60)
        print("测试题3：明渠流综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 5.0       # 底宽 (m)
        m_side = 1.5  # 边坡系数
        n = 0.025     # 糙率
        i = 0.001     # 底坡
        Q = 20.0      # 流量 (m³/s)
        dz = 1.5      # 跌坎高度 (m)
        
        print(f"\n已知条件：")
        print(f"  渠道：底宽b={b}m, 边坡m={m_side}, 糙率n={n}")
        print(f"  底坡：i={i}")
        print(f"  流量：Q={Q}m³/s")
        print(f"  跌坎：Δz={dz}m")
        
        # (1) 正常水深和临界水深
        print(f"\n解题步骤：")
        print(f"\n(1) 计算正常水深h₀和临界水深hc")
        
        # 定义方程
        def normal_depth_eq(h):
            """正常水深方程"""
            A = (b + m_side * h) * h
            chi = b + 2 * h * np.sqrt(1 + m_side**2)
            R = A / chi
            Q_calc = (1/n) * A * R**(2/3) * np.sqrt(i)
            return Q_calc - Q
        
        def critical_depth_eq(h):
            """临界水深方程"""
            A = (b + m_side * h) * h
            B = b + 2 * m_side * h
            Fr2 = Q**2 * B / (self.g * A**3)
            return Fr2 - 1
        
        # 求解正常水深
        h0 = fsolve(normal_depth_eq, 2.0)[0]
        A0 = (b + m_side * h0) * h0
        chi0 = b + 2 * h0 * np.sqrt(1 + m_side**2)
        R0 = A0 / chi0
        v0 = Q / A0
        
        print(f"\n正常水深（谢才公式）：")
        print(f"  Q = (1/n)AR^(2/3)√i")
        print(f"  h₀ = {h0:.3f} m ✓")
        print(f"  A₀ = {A0:.3f} m²")
        print(f"  v₀ = {v0:.3f} m/s")
        print(f"  R₀ = {R0:.3f} m")
        
        # 求解临界水深
        hc = fsolve(critical_depth_eq, 1.0)[0]
        Ac = (b + m_side * hc) * hc
        Bc = b + 2 * m_side * hc
        vc = Q / Ac
        Frc = vc / np.sqrt(self.g * Ac / Bc)
        
        print(f"\n临界水深（弗劳德数Fr=1）：")
        print(f"  Fr = v/√(gA/B) = 1")
        print(f"  hc = {hc:.3f} m ✓")
        print(f"  Ac = {Ac:.3f} m²")
        print(f"  vc = {vc:.3f} m/s")
        print(f"  Fr = {Frc:.3f} ≈ 1")
        
        # (2) 判断流态
        print(f"\n(2) 判断流态")
        
        Fr0 = v0 / np.sqrt(self.g * A0 / (b + 2 * m_side * h0))
        print(f"\n正常流弗劳德数：")
        print(f"  Fr₀ = v₀/√(gA₀/B₀) = {Fr0:.3f}")
        
        if Fr0 < 1:
            flow_type = "缓流"
            print(f"  Fr₀ < 1 → 缓流（h₀ > hc）")
            # 跌坎上游为临界水深
            h_upstream = hc
            print(f"\n跌坎上游水深：")
            print(f"  缓流遇跌坎→临界水深")
            print(f"  h = hc = {h_upstream:.3f} m ✓")
        else:
            flow_type = "急流"
            print(f"  Fr₀ > 1 → 急流（h₀ < hc）")
            h_upstream = h0
            print(f"\n跌坎上游水深：")
            print(f"  急流遇跌坎→保持正常水深")
            print(f"  h = h₀ = {h_upstream:.3f} m ✓")
        
        # (3) 水跃计算
        print(f"\n(3) 水跃计算")
        
        # 假设急流情况，h0为跃前水深
        if Fr0 > 1:
            h1_jump = h0
            v1_jump = v0
            Fr1 = Fr0
        else:
            # 如果是缓流，假设下游有急流段
            h1_jump = hc / 2  # 假设跃前为hc/2
            A1_jump = (b + m_side * h1_jump) * h1_jump
            v1_jump = Q / A1_jump
            B1_jump = b + 2 * m_side * h1_jump
            Fr1 = v1_jump / np.sqrt(self.g * A1_jump / B1_jump)
        
        print(f"\n跃前条件：")
        print(f"  h₁ = {h1_jump:.3f} m")
        print(f"  v₁ = {v1_jump:.3f} m/s")
        print(f"  Fr₁ = {Fr1:.3f}")
        
        if Fr1 > 1:
            # 矩形渠道水跃公式（简化）
            # 对于梯形渠道，使用近似公式
            h2_jump = h1_jump/2 * (-1 + np.sqrt(1 + 8*Fr1**2))
            
            A2_jump = (b + m_side * h2_jump) * h2_jump
            v2_jump = Q / A2_jump
            B2_jump = b + 2 * m_side * h2_jump
            Fr2 = v2_jump / np.sqrt(self.g * A2_jump / B2_jump)
            
            print(f"\n跃后水深（矩形近似公式）：")
            print(f"  h₂/h₁ = 0.5(-1+√(1+8Fr₁²))")
            print(f"  h₂ = {h2_jump:.3f} m ✓")
            print(f"  v₂ = {v2_jump:.3f} m/s")
            print(f"  Fr₂ = {Fr2:.3f} < 1（缓流）")
            
            # 水跃长度（经验公式）
            Lj = 6 * (h2_jump - h1_jump)
            print(f"\n水跃长度（经验公式）：")
            print(f"  Lj = 6(h₂-h₁) = 6×({h2_jump:.3f}-{h1_jump:.3f})")
            print(f"     = {Lj:.3f} m ✓")
        else:
            print(f"\n  Fr₁ < 1，不会发生水跃")
            h2_jump = h1_jump
            Lj = 0
        
        # (4) 能量损失
        print(f"\n(4) 计算单宽能量损失")
        
        if Fr1 > 1 and h2_jump > h1_jump:
            E1 = h1_jump + v1_jump**2 / (2 * self.g)
            E2 = h2_jump + v2_jump**2 / (2 * self.g)
            dE = E1 - E2
            
            # 单宽能量损失
            q = Q / b  # 单宽流量
            dE_per_width = dE
            
            print(f"\n跃前比能：E₁ = h₁ + v₁²/(2g) = {h1_jump:.3f} + {v1_jump**2/(2*self.g):.3f}")
            print(f"         = {E1:.3f} m")
            print(f"跃后比能：E₂ = h₂ + v₂²/(2g) = {h2_jump:.3f} + {v2_jump**2/(2*self.g):.3f}")
            print(f"         = {E2:.3f} m")
            print(f"\n能量损失：ΔE = E₁-E₂ = {E1:.3f}-{E2:.3f}")
            print(f"         = {dE:.3f} m ✓")
            print(f"\n单宽能量损失：ΔE = {dE_per_width:.3f} m ✓")
        else:
            dE = 0
            dE_per_width = 0
            print(f"\n无水跃，能量损失为0")
        
        # 绘图
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：渠道断面
        ax1 = plt.subplot(2, 3, 1)
        
        # 绘制梯形断面
        y_h0 = h0
        x_bottom = [-b/2, b/2]
        x_top_h0 = [-b/2 - m_side*y_h0, b/2 + m_side*y_h0]
        
        # h0断面
        channel_x_h0 = [x_top_h0[0], x_bottom[0], x_bottom[1], x_top_h0[1], x_top_h0[0]]
        channel_y_h0 = [y_h0, 0, 0, y_h0, y_h0]
        ax1.fill(channel_x_h0, channel_y_h0, color='cyan', alpha=0.4, 
                edgecolor='blue', linewidth=2, label=f'h₀={h0:.2f}m')
        
        # hc断面
        y_hc = hc
        x_top_hc = [-b/2 - m_side*y_hc, b/2 + m_side*y_hc]
        channel_x_hc = [x_top_hc[0], x_bottom[0], x_bottom[1], x_top_hc[1], x_top_hc[0]]
        channel_y_hc = [y_hc, 0, 0, y_hc, y_hc]
        ax1.plot(channel_x_hc[:4], channel_y_hc[:4], 'r--', linewidth=2, label=f'hc={hc:.2f}m')
        
        # 标注
        ax1.text(0, h0/2, f'h₀={h0:.2f}m\nFr={Fr0:.2f}\n{flow_type}',
                ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 尺寸标注
        ax1.plot([x_bottom[0], x_bottom[1]], [-0.3, -0.3], 'k-', linewidth=2)
        ax1.text(0, -0.5, f'b={b}m', ha='center', fontsize=10)
        
        ax1.plot([x_bottom[1], x_top_h0[1]], [0, y_h0], 'k--', linewidth=1)
        ax1.text(x_top_h0[1]+0.5, y_h0/2, f'm={m_side}', fontsize=10)
        
        ax1.set_xlabel('宽度 (m)', fontsize=12)
        ax1.set_ylabel('水深 (m)', fontsize=12)
        ax1.set_title('测试题3：梯形渠道断面', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 子图2：纵剖面（含跌坎和水跃）
        ax2 = plt.subplot(2, 3, 2)
        
        # 河底线
        x_profile = [0, 10, 10, 20]
        y_bottom = [0, 0, -dz, -dz]
        ax2.plot(x_profile, y_bottom, 'k-', linewidth=3, label='河底')
        ax2.fill_between(x_profile, y_bottom, [-1]*len(x_profile),
                        color='gray', alpha=0.3)
        
        # 水面线
        if Fr0 < 1:  # 缓流
            # 上游正常水深，跌坎处临界水深
            x_water = [0, 9, 10]
            y_water = [h0, hc, hc-dz]
        else:  # 急流
            # 保持h0
            x_water = [0, 10]
            y_water = [h0, h0-dz]
        
        ax2.plot(x_water, y_water, 'b-', linewidth=2.5, label='水面线')
        
        # 水跃
        if Fr1 > 1 and Lj > 0:
            x_jump_start = 12
            x_jump_end = x_jump_start + Lj
            ax2.plot([x_jump_start, x_jump_end], 
                    [h1_jump-dz, h2_jump-dz],
                    'r-', linewidth=3, label='水跃')
            ax2.fill_between([x_jump_start, x_jump_end],
                            [h1_jump-dz, h2_jump-dz],
                            [y_bottom[3], y_bottom[3]],
                            color='red', alpha=0.2)
        
        # 标注
        ax2.text(5, h0/2, f'h₀={h0:.2f}m', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        ax2.text(9.5, hc, f'hc={hc:.2f}m', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        if Fr1 > 1 and Lj > 0:
            ax2.text(x_jump_start + Lj/2, h2_jump-dz+0.2,
                    f'水跃\nLj={Lj:.1f}m', fontsize=9, ha='center',
                    bbox=dict(boxstyle='round', facecolor='pink', alpha=0.8))
        
        ax2.set_xlabel('距离 (m)', fontsize=12)
        ax2.set_ylabel('高程 (m)', fontsize=12)
        ax2.set_title('纵剖面（含跌坎与水跃）', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3：比能曲线
        ax3 = plt.subplot(2, 3, 3)
        
        # 计算比能曲线
        h_range = np.linspace(0.1, 4, 100)
        E_range = []
        for h in h_range:
            A_temp = (b + m_side * h) * h
            v_temp = Q / A_temp
            E_temp = h + v_temp**2 / (2 * self.g)
            E_range.append(E_temp)
        
        ax3.plot(E_range, h_range, 'b-', linewidth=2.5, label='比能曲线')
        
        # 标注关键点
        E0 = h0 + v0**2 / (2 * self.g)
        Ec = hc + vc**2 / (2 * self.g)
        
        ax3.plot(E0, h0, 'go', markersize=15, label=f'h₀={h0:.2f}m')
        ax3.plot(Ec, hc, 'ro', markersize=15, label=f'hc={hc:.2f}m (最小比能)')
        
        # 水跃点
        if Fr1 > 1 and h2_jump > h1_jump:
            E1_jump = h1_jump + v1_jump**2 / (2 * self.g)
            E2_jump = h2_jump + v2_jump**2 / (2 * self.g)
            ax3.plot(E1_jump, h1_jump, 'ms', markersize=12, label=f'跃前h₁={h1_jump:.2f}m')
            ax3.plot(E2_jump, h2_jump, 'cs', markersize=12, label=f'跃后h₂={h2_jump:.2f}m')
            
            # 能量损失箭头
            ax3.annotate('', xy=(E2_jump, (h1_jump+h2_jump)/2), 
                        xytext=(E1_jump, (h1_jump+h2_jump)/2),
                        arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            ax3.text((E1_jump+E2_jump)/2, (h1_jump+h2_jump)/2+0.2,
                    f'ΔE={dE:.2f}m', ha='center', fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 临界线
        ax3.axvline(x=Ec, color='red', linestyle='--', linewidth=2, alpha=0.5)
        ax3.axhline(y=hc, color='red', linestyle='--', linewidth=2, alpha=0.5)
        
        ax3.set_xlabel('比能 E (m)', fontsize=12)
        ax3.set_ylabel('水深 h (m)', fontsize=12)
        ax3.set_title('比能曲线与关键点', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 子图4：弗劳德数变化
        ax4 = plt.subplot(2, 3, 4)
        
        stations_fr = ['正常流', '跌坎上游', '跃前', '跃后']
        Fr_values = [Fr0, 1.0 if Fr0<1 else Fr0, Fr1 if Fr1>1 else 0, 
                    Fr2 if (Fr1>1 and h2_jump>h1_jump) else 0]
        colors_fr = ['green' if fr < 1 else 'red' for fr in Fr_values]
        
        bars_fr = ax4.bar(stations_fr, Fr_values, color=colors_fr, alpha=0.7,
                         edgecolor='black', linewidth=2)
        
        # 标注
        for bar, fr in zip(bars_fr, Fr_values):
            if fr > 0:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height+0.05,
                        f'{fr:.3f}',
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold')
        
        ax4.axhline(y=1, color='blue', linestyle='--', linewidth=2, label='Fr=1')
        ax4.set_ylabel('弗劳德数 Fr', fontsize=12)
        ax4.set_title('各断面弗劳德数', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 子图5：水跃共轭水深关系
        ax5 = plt.subplot(2, 3, 5)
        
        if Fr1 > 1 and h2_jump > h1_jump:
            # 绘制共轭水深曲线
            Fr_range = np.linspace(1, 10, 100)
            h_ratio = []
            for Fr_temp in Fr_range:
                ratio = 0.5 * (-1 + np.sqrt(1 + 8*Fr_temp**2))
                h_ratio.append(ratio)
            
            ax5.plot(Fr_range, h_ratio, 'b-', linewidth=2.5, label='h₂/h₁理论曲线')
            
            # 当前点
            actual_ratio = h2_jump / h1_jump
            ax5.plot(Fr1, actual_ratio, 'ro', markersize=15,
                    label=f'本题：Fr₁={Fr1:.2f}\nh₂/h₁={actual_ratio:.2f}')
            
            ax5.set_xlabel('跃前弗劳德数 Fr₁', fontsize=12)
            ax5.set_ylabel('共轭水深比 h₂/h₁', fontsize=12)
            ax5.set_title('水跃共轭水深关系', fontsize=13, fontweight='bold')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        else:
            ax5.text(0.5, 0.5, '无水跃', ha='center', va='center',
                    fontsize=20, fontweight='bold')
            ax5.set_xlim(0, 1)
            ax5.set_ylim(0, 1)
        
        # 子图6：结果汇总
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        jump_text = f"""
        跃前：h₁={h1_jump:.3f}m, Fr₁={Fr1:.3f}
        跃后：h₂={h2_jump:.3f}m, Fr₂={Fr2:.3f}
        长度：Lj={Lj:.3f}m
        """ if (Fr1 > 1 and Lj > 0) else "  不发生水跃"
        
        summary_text = f"""
        【测试题3结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 正常水深与临界水深：
        
          正常水深：h₀ = {h0:.3f} m ✓
          临界水深：hc = {hc:.3f} m ✓
          
          比较：h₀ {'>' if h0>hc else '<'} hc
          结论：{flow_type}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (2) 流态与跌坎上游水深：
        
          Fr₀ = {Fr0:.3f} {'<' if Fr0<1 else '>'} 1
          流态：{flow_type}
          
          跌坎上游水深：
            h = {h_upstream:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (3) 水跃计算：
        {jump_text}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (4) 能量损失：
        
          单宽能量损失：
            ΔE = {dE_per_width:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        评分：35分
          (1) 10分  (2) 8分
          (3) 10分  (4) 7分
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax6.text(0.1, 0.95, summary_text, fontsize=8, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day23_week1_test/test_3.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_3.png")
        
        return {'h0': h0, 'hc': hc, 'Fr0': Fr0, 'h2_jump': h2_jump, 'Lj': Lj, 'dE': dE}
    
    def test_summary(self):
        """测试总结"""
        print("\n" + "="*60)
        print("📊 第一周测试总结")
        print("="*60)
        
        print("\n✅ 测试完成情况：")
        print("  ✓ 测试题1：静水力学综合题（30分）")
        print("  ✓ 测试题2：水动力学综合题（35分）")
        print("  ✓ 测试题3：明渠流综合题（35分）")
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  ✓ 总分：100分")
        
        print("\n✅ 知识点覆盖：")
        print("  Day 1-3: 静水力学")
        print("    • 静水总压力与压力中心 ✓")
        print("    • 浮力与浮体平衡 ✓")
        print("    • 闸门力矩平衡 ✓")
        print("  ")
        print("  Day 4-6: 水动力学基础")
        print("    • 伯努利方程应用 ✓")
        print("    • 管道能量损失 ✓")
        print("    • 动量方程与冲击力 ✓")
        print("  ")
        print("  Day 8-10: 管流与明渠流")
        print("    • 明渠均匀流（正常水深）✓")
        print("    • 临界水深与流态判断 ✓")
        print("    • 水跃计算 ✓")
        
        print("\n🎯 重点公式回顾：")
        print("  静水力学：")
        print("    P = γhcA")
        print("    e = Ic/(hcA)")
        print("    F浮 = γV排")
        print("  ")
        print("  水动力学：")
        print("    z + p/(γ) + v²/(2g) = H")
        print("    hf = (λL/d + Σξ)v²/(2g)")
        print("    F = ρQv")
        print("  ")
        print("  明渠流：")
        print("    Q = (1/n)AR^(2/3)√i")
        print("    Fr = v/√(gA/B)")
        print("    h₂/h₁ = 0.5(-1+√(1+8Fr₁²))")
        
        print("\n💡 考试技巧：")
        print("  ✓ 静水力学：先算形心，再算惯性矩")
        print("  ✓ 伯努利方程：选对基准面，注意能量损失")
        print("  ✓ 明渠流：先判断流态（Fr与1比较）")
        print("  ✓ 水跃：Fr₁>1才会发生，注意共轭关系")
        
        print("\n⚠️ 常见错误：")
        print("  ❌ 压力中心≠形心，要加偏心距e")
        print("  ❌ 伯努利方程忘记局部损失")
        print("  ❌ 临界水深公式用错（矩形vs梯形）")
        print("  ❌ 水跃方向搞反（急流→缓流）")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 23: 第一周测试")
    print("="*60)
    print("\n⏰ 考试时间：3小时")
    print("📚 测试范围：Day 1-10")
    print("💯 总分：100分")
    
    # 创建对象
    day23 = Day23Week1Test()
    
    # 测试题1：静水力学
    result1 = day23.test_1_hydrostatics_comprehensive()
    
    # 测试题2：水动力学
    result2 = day23.test_2_hydrodynamics_comprehensive()
    
    # 测试题3：明渠流
    result3 = day23.test_3_channel_flow_comprehensive()
    
    # 测试总结
    day23.test_summary()
    
    print("\n" + "="*60)
    print("✅ 第一周测试完成！")
    print("="*60)
    print(f"\n测试结果：")
    print(f"  测试题1：30分（静水力学）")
    print(f"  测试题2：35分（水动力学）")
    print(f"  测试题3：35分（明渠流）")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  总分：100分")
    
    print(f"\n📊 成绩评估：")
    print(f"  90-100分：优秀！基础扎实")
    print(f"  80-89分：良好，继续保持")
    print(f"  70-79分：合格，需加强")
    print(f"  <70分：需重点复习第一周内容")
    
    print(f"\n下一步：Day 24 - 第二周测试")
    print(f"💪 继续努力，冲刺80%里程碑！")

if __name__ == "__main__":
    main()
    plt.show()
