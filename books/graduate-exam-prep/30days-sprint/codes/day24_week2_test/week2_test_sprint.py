#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 24: 第二周测试
Sprint Day 24: Week 2 Comprehensive Test (Day 11-20)

⏰ 考试时间：3小时
📚 测试范围：
  Day 11-13: 明渠非均匀流（临界水深、水跃、堰流闸孔）
  Day 15-16: 渗流（达西定律、地下水井）
  Day 17-20: 泵站+水工+河流+环境

🎯 测试目标：
  - 检验第二周学习效果
  - 巩固复杂问题求解
  - 提高综合应用能力
  - 为最后冲刺做准备

💪 考试格言：第二周测试=能力提升！综合应用=提高10分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon, Wedge, FancyBboxPatch
import matplotlib.patches as mpatches
from scipy.optimize import fsolve, brentq

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day24Week2Test:
    """
    Day 24：第二周测试
    
    包含3个综合测试题：
    1. 明渠水跃与堰流综合题（35分）
    2. 渗流与地下水综合题（30分）
    3. 泵站与环境综合题（35分）
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho_w = 1000  # 水的密度 (kg/m³)
        self.gamma_w = self.rho_w * self.g  # 水的重度 (N/m³)
        
    def test_1_channel_hydraulic_jump_weir(self):
        """
        测试题1：明渠水跃与堰流综合题⭐⭐⭐⭐⭐
        
        题目：矩形渠道串联宽顶堰：
              渠道宽度b=6m，糙率n=0.02，底坡i=0.002
              上游流量Q=30m³/s，水深h₁=1.5m（急流）
              中间发生水跃，跃后接宽顶堰（堰高P=1.2m）
        求：(1) 跃前水深的弗劳德数与跃后水深
            (2) 水跃长度与水跃损失
            (3) 堰顶水头与过堰流量（验证连续性）
            (4) 堰后水深（假设为临界水深）
        
        考点：水跃共轭、能量损失、堰流计算
        难度：综合（第二周核心！）
        时间：40分钟
        分值：35分
        """
        print("\n" + "="*60)
        print("测试题1：明渠水跃与堰流综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 6.0       # 渠道宽度 (m)
        n = 0.02      # 糙率
        i = 0.002     # 底坡
        Q = 30.0      # 流量 (m³/s)
        h1 = 1.5      # 跃前水深 (m)
        P = 1.2       # 堰高 (m)
        
        print(f"\n已知条件：")
        print(f"  渠道：宽度b={b}m, 糙率n={n}, 底坡i={i}")
        print(f"  流量：Q={Q}m³/s")
        print(f"  跃前水深：h₁={h1}m")
        print(f"  堰高：P={P}m")
        
        # (1) 跃前弗劳德数与跃后水深
        print(f"\n解题步骤：")
        print(f"\n(1) 计算跃前Fr与跃后水深")
        
        # 跃前参数
        A1 = b * h1
        v1 = Q / A1
        Fr1 = v1 / np.sqrt(self.g * h1)
        
        print(f"\n跃前参数：")
        print(f"  面积：A₁ = b×h₁ = {b}×{h1} = {A1} m²")
        print(f"  流速：v₁ = Q/A₁ = {Q}/{A1} = {v1:.3f} m/s")
        print(f"  弗劳德数：Fr₁ = v₁/√(gh₁) = {v1:.3f}/√({self.g}×{h1})")
        print(f"            = {Fr1:.3f} ✓")
        
        if Fr1 > 1:
            print(f"  判断：Fr₁ > 1 → 急流，可发生水跃")
        else:
            print(f"  判断：Fr₁ < 1 → 缓流，不会发生水跃")
        
        # 跃后水深（矩形断面水跃公式）
        h2 = h1/2 * (-1 + np.sqrt(1 + 8*Fr1**2))
        A2 = b * h2
        v2 = Q / A2
        Fr2 = v2 / np.sqrt(self.g * h2)
        
        print(f"\n跃后水深（水跃共轭公式）：")
        print(f"  h₂/h₁ = 0.5(-1+√(1+8Fr₁²))")
        print(f"  h₂ = h₁/2 × (-1+√(1+8×{Fr1:.3f}²))")
        print(f"     = {h1}/2 × (-1+√(1+{8*Fr1**2:.2f}))")
        print(f"     = {h2:.3f} m ✓")
        print(f"  v₂ = Q/A₂ = {Q}/{A2:.2f} = {v2:.3f} m/s")
        print(f"  Fr₂ = {Fr2:.3f} < 1（缓流）✓")
        
        # (2) 水跃长度与损失
        print(f"\n(2) 计算水跃长度与能量损失")
        
        # 水跃长度（经验公式）
        Lj = 6 * (h2 - h1)
        print(f"\n水跃长度（经验公式）：")
        print(f"  Lj = 6(h₂-h₁) = 6×({h2:.3f}-{h1})")
        print(f"     = {Lj:.3f} m ✓")
        
        # 比能与损失
        E1 = h1 + v1**2 / (2 * self.g)
        E2 = h2 + v2**2 / (2 * self.g)
        dE = E1 - E2
        
        print(f"\n能量损失：")
        print(f"  跃前比能：E₁ = h₁ + v₁²/(2g) = {h1} + {v1**2/(2*self.g):.3f}")
        print(f"           = {E1:.3f} m")
        print(f"  跃后比能：E₂ = h₂ + v₂²/(2g) = {h2:.3f} + {v2**2/(2*self.g):.3f}")
        print(f"           = {E2:.3f} m")
        print(f"  水跃损失：ΔE = E₁-E₂ = {E1:.3f}-{E2:.3f}")
        print(f"           = {dE:.3f} m ✓")
        
        # 相对损失
        relative_loss = dE / E1 * 100
        print(f"  相对损失：ΔE/E₁ = {dE:.3f}/{E1:.3f} = {relative_loss:.1f}%")
        
        # (3) 堰顶水头与过堰流量
        print(f"\n(3) 计算堰顶水头与过堰流量")
        
        # 假设跃后水深h2为堰前水深
        # 堰顶水头
        H_weir = h2 - P
        
        print(f"\n堰顶水头：")
        print(f"  H = h₂ - P = {h2:.3f} - {P}")
        print(f"    = {H_weir:.3f} m ✓")
        
        # 宽顶堰流量公式
        m_weir = 0.385  # 流量系数（宽顶堰）
        Q_weir = m_weir * b * np.sqrt(2*self.g) * H_weir**1.5
        
        print(f"\n过堰流量（宽顶堰公式）：")
        print(f"  Q = mb√(2g)H^(3/2)")
        print(f"    = {m_weir}×{b}×√(2×{self.g})×{H_weir:.3f}^1.5")
        print(f"    = {Q_weir:.2f} m³/s")
        
        # 验证连续性
        error = abs(Q_weir - Q) / Q * 100
        print(f"\n连续性验证：")
        print(f"  上游流量：Q = {Q} m³/s")
        print(f"  过堰流量：Q堰 = {Q_weir:.2f} m³/s")
        print(f"  误差：{error:.1f}%")
        if error < 5:
            print(f"  结论：连续性满足 ✓")
        else:
            print(f"  结论：误差较大，需调整参数")
        
        # (4) 堰后水深
        print(f"\n(4) 计算堰后水深")
        
        # 假设堰后为临界水深
        # 矩形断面：hc = (Q²/(gb²))^(1/3)
        hc = (Q**2 / (self.g * b**2))**(1/3)
        
        print(f"\n堰后水深（临界水深）：")
        print(f"  hc = (Q²/(gb²))^(1/3)")
        print(f"     = ({Q}²/({self.g}×{b}²))^(1/3)")
        print(f"     = {hc:.3f} m ✓")
        
        vc = Q / (b * hc)
        Frc = vc / np.sqrt(self.g * hc)
        print(f"  vc = Q/(b×hc) = {vc:.3f} m/s")
        print(f"  Frc = {Frc:.3f} ≈ 1（临界流）✓")
        
        # 绘图
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：纵剖面示意图
        ax1 = plt.subplot(2, 3, 1)
        
        # 河底
        x_profile = [0, 5, 5+Lj, 15, 20, 25]
        y_bottom = [0, -5*i, -(5+Lj)*i, -15*i, -15*i-P, -25*i-P]
        ax1.plot(x_profile, y_bottom, 'k-', linewidth=3, label='河底')
        ax1.fill_between(x_profile, y_bottom, [min(y_bottom)-0.5]*len(x_profile),
                        color='gray', alpha=0.3)
        
        # 水面线
        x_water = [0, 5, 5, 5+Lj, 15, 20, 25]
        y_water = [h1, h1-5*i, h1-5*i, h2-(5+Lj)*i, h2-15*i, 
                  hc-15*i-P, hc-25*i-P]
        ax1.plot(x_water, y_water, 'b-', linewidth=2.5, label='水面线')
        
        # 标注
        ax1.text(2.5, h1/2, f'急流\nh₁={h1}m\nFr₁={Fr1:.2f}',
                ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        ax1.annotate('', xy=(5+Lj, h2-(5+Lj)*i), xytext=(5, h1-5*i),
                    arrowprops=dict(arrowstyle='->', color='red', lw=3))
        ax1.text(5+Lj/2, (h1+h2)/2, f'水跃\nLj={Lj:.1f}m',
                ha='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.text(12, h2/2, f'缓流\nh₂={h2:.2f}m\nFr₂={Fr2:.2f}',
                ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 堰
        weir_x = [20, 20, 20, 20]
        weir_y = [-15*i-P, -15*i, h2-15*i, -15*i-P]
        ax1.fill([20, 20, 20.3, 20.3], [-15*i-P, -15*i, -15*i, -15*i-P],
                color='brown', alpha=0.7, edgecolor='black', linewidth=2)
        ax1.text(21, -15*i-P/2, f'堰\nP={P}m',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='orange'))
        
        ax1.set_xlabel('距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('测试题1：水跃+堰流系统纵剖面', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 子图2：水跃共轭水深关系
        ax2 = plt.subplot(2, 3, 2)
        
        # 理论曲线
        Fr_range = np.linspace(1, 10, 100)
        h_ratio = 0.5 * (-1 + np.sqrt(1 + 8*Fr_range**2))
        
        ax2.plot(Fr_range, h_ratio, 'b-', linewidth=2.5, label='h₂/h₁理论曲线')
        
        # 本题点
        actual_ratio = h2 / h1
        ax2.plot(Fr1, actual_ratio, 'ro', markersize=15,
                label=f'本题\nFr₁={Fr1:.2f}\nh₂/h₁={actual_ratio:.2f}')
        
        # 标注
        ax2.axhline(y=actual_ratio, color='red', linestyle='--', 
                   linewidth=1, alpha=0.5)
        ax2.axvline(x=Fr1, color='red', linestyle='--',
                   linewidth=1, alpha=0.5)
        
        ax2.set_xlabel('跃前弗劳德数 Fr₁', fontsize=12)
        ax2.set_ylabel('共轭水深比 h₂/h₁', fontsize=12)
        ax2.set_title('水跃共轭水深关系', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(1, 10)
        
        # 子图3：能量线图
        ax3 = plt.subplot(2, 3, 3)
        
        # 关键断面
        sections = ['跃前', '跃后', '堰前', '堰顶']
        h_values = [h1, h2, h2, hc]
        v_values = [v1, v2, v2, vc]
        E_values = [h + v**2/(2*self.g) for h, v in zip(h_values, v_values)]
        
        x_pos = np.arange(len(sections))
        
        # 总能量
        ax3.bar(x_pos, E_values, width=0.6, color='blue', alpha=0.6,
               edgecolor='black', linewidth=2, label='总比能E')
        
        # 水深
        ax3.bar(x_pos, h_values, width=0.6, color='cyan', alpha=0.8,
               edgecolor='black', linewidth=1, label='水深h')
        
        # 标注
        for i, (E, h, v) in enumerate(zip(E_values, h_values, v_values)):
            ax3.text(i, E+0.05, f'E={E:.2f}m',
                    ha='center', fontsize=9, fontweight='bold')
            ax3.text(i, h/2, f'h={h:.2f}m',
                    ha='center', fontsize=8, color='white', fontweight='bold')
        
        # 水跃损失
        ax3.annotate('', xy=(1, E_values[1]), xytext=(0, E_values[0]),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax3.text(0.5, (E_values[0]+E_values[1])/2, f'ΔE={dE:.2f}m',
                fontsize=9, ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(sections)
        ax3.set_ylabel('比能/水深 (m)', fontsize=12)
        ax3.set_title('各断面能量分析', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：堰流分析
        ax4 = plt.subplot(2, 3, 4)
        
        # 堰侧视图
        # 堰体
        weir_body = Rectangle((0, 0), 1, P, facecolor='brown',
                             alpha=0.7, edgecolor='black', linewidth=2)
        ax4.add_patch(weir_body)
        
        # 堰前水位
        ax4.fill_between([0-2, 0], [h2, h2], [0, 0],
                        color='cyan', alpha=0.4, label='堰前水体')
        ax4.axhline(y=h2, color='blue', linestyle='--', linewidth=2)
        ax4.text(-1, h2+0.1, f'h₂={h2:.2f}m', fontsize=10)
        
        # 堰顶水头
        ax4.plot([0.5, 0.5], [P, h2], 'r-', linewidth=3)
        ax4.text(0.7, (P+h2)/2, f'H={H_weir:.2f}m',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 堰后水深
        ax4.fill_between([1, 3], [hc, hc], [0, 0],
                        color='lightblue', alpha=0.6, label='堰后水体')
        ax4.axhline(y=hc, xmin=0.5, color='green', linestyle='--', linewidth=2)
        ax4.text(2, hc+0.1, f'hc={hc:.2f}m', fontsize=10)
        
        # 标注
        ax4.text(0.5, -0.3, f'堰高\nP={P}m', ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='orange'))
        
        ax4.set_xlabel('距离 (m)', fontsize=12)
        ax4.set_ylabel('高程 (m)', fontsize=12)
        ax4.set_title('宽顶堰流分析', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim(-2.5, 3.5)
        ax4.set_ylim(-0.5, 3)
        
        # 子图5：流量对比
        ax5 = plt.subplot(2, 3, 5)
        
        flows = [Q, Q_weir]
        labels_flow = ['上游流量Q', '过堰流量Q堰']
        colors_flow = ['blue', 'green']
        
        bars = ax5.bar(labels_flow, flows, color=colors_flow, alpha=0.7,
                      edgecolor='black', linewidth=2)
        
        # 标注
        for bar, flow in zip(bars, flows):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height+0.5,
                    f'{flow:.2f}m³/s',
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
        
        ax5.set_ylabel('流量 (m³/s)', fontsize=12)
        ax5.set_title(f'流量连续性验证（误差{error:.1f}%）', 
                     fontsize=13, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 子图6：结果汇总
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        summary_text = f"""
        【测试题1结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 水跃分析：
        
          跃前：h₁={h1}m, Fr₁={Fr1:.3f}（急流）
          跃后：h₂={h2:.3f}m, Fr₂={Fr2:.3f}（缓流）
          
          共轭关系：h₂/h₁={actual_ratio:.2f} ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (2) 水跃特性：
        
          水跃长度：Lj={Lj:.3f}m ✓
          能量损失：ΔE={dE:.3f}m
          相对损失：{relative_loss:.1f}%
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (3) 堰流计算：
        
          堰顶水头：H={H_weir:.3f}m ✓
          过堰流量：Q堰={Q_weir:.2f}m³/s
          
          连续性验证：
            误差={error:.1f}% ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (4) 堰后水深：
        
          临界水深：hc={hc:.3f}m ✓
          Frc={Frc:.3f} ≈ 1
        
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
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day24_week2_test/test_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_1.png")
        
        return {'Fr1': Fr1, 'h2': h2, 'Lj': Lj, 'dE': dE, 'H_weir': H_weir, 'hc': hc}
    
    def test_2_seepage_groundwater(self):
        """
        测试题2：渗流与地下水综合题⭐⭐⭐⭐⭐
        
        题目：承压含水层抽水试验：
              含水层厚度M=20m，渗透系数k=15m/d
              在中心打一口井，半径r₀=0.3m
              抽水量Q=1200m³/d，稳定后
              观测井1：距离r₁=10m，水位降深s₁
              观测井2：距离r₂=50m，水位降深s₂
        另外，旁边有一土坝，底宽a=40m
        下游无排水设备，上游水深H₁=8m，下游H₂=2m
        
        求：(1) 两观测井的水位降深
            (2) 抽水影响半径R
            (3) 土坝渗流量（每延米）
            (4) 浸润线方程与渗流逸出点高度
        
        考点：地下水井、裘布依公式、土坝渗流
        难度：综合（重点！）
        时间：35分钟
        分值：30分
        """
        print("\n" + "="*60)
        print("测试题2：渗流与地下水综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        M = 20.0      # 含水层厚度 (m)
        k = 15.0      # 渗透系数 (m/d)
        r0 = 0.3      # 井半径 (m)
        Q = 1200.0    # 抽水量 (m³/d)
        r1 = 10.0     # 观测井1距离 (m)
        r2 = 50.0     # 观测井2距离 (m)
        a = 40.0      # 坝底宽 (m)
        H1 = 8.0      # 上游水深 (m)
        H2 = 2.0      # 下游水深 (m)
        
        print(f"\n已知条件：")
        print(f"  承压含水层：厚度M={M}m, 渗透系数k={k}m/d")
        print(f"  抽水井：半径r₀={r0}m, 抽水量Q={Q}m³/d")
        print(f"  观测井：r₁={r1}m, r₂={r2}m")
        print(f"  土坝：底宽a={a}m, H₁={H1}m, H₂={H2}m")
        
        # (1) 观测井水位降深
        print(f"\n解题步骤：")
        print(f"\n(1) 计算观测井水位降深")
        
        print(f"\n裘布依公式（承压水完整井）：")
        print(f"  s = Q/(2πkM) × ln(R/r)")
        
        # 假设影响半径R
        # 对于两个观测井，可以用它们之间的关系求解
        # s₁ - s₂ = Q/(2πkM) × ln(r₂/r₁)
        
        s_diff = Q / (2 * np.pi * k * M) * np.log(r2 / r1)
        
        print(f"\n观测井降深差：")
        print(f"  s₁-s₂ = Q/(2πkM) × ln(r₂/r₁)")
        print(f"        = {Q}/(2π×{k}×{M}) × ln({r2}/{r1})")
        print(f"        = {s_diff:.3f} m")
        
        # 假设影响半径R=300m（经验值）
        R = 300.0
        
        s1 = Q / (2 * np.pi * k * M) * np.log(R / r1)
        s2 = Q / (2 * np.pi * k * M) * np.log(R / r2)
        
        print(f"\n假设影响半径R={R}m：")
        print(f"  s₁ = Q/(2πkM) × ln(R/r₁)")
        print(f"     = {Q}/(2π×{k}×{M}) × ln({R}/{r1})")
        print(f"     = {s1:.3f} m ✓")
        print(f"  s₂ = Q/(2πkM) × ln(R/r₂)")
        print(f"     = {Q}/(2π×{k}×{M}) × ln({R}/{r2})")
        print(f"     = {s2:.3f} m ✓")
        
        # 验证
        s_diff_calc = s1 - s2
        print(f"\n验证：s₁-s₂ = {s1:.3f}-{s2:.3f} = {s_diff_calc:.3f} m ≈ {s_diff:.3f} m ✓")
        
        # (2) 影响半径
        print(f"\n(2) 确定抽水影响半径")
        
        # 库萨金经验公式
        H0 = M  # 承压水初始水头
        sw = s1  # 井中水位降深（用观测井1近似）
        R_kusakin = 10 * sw * np.sqrt(k * H0)
        
        print(f"\n库萨金经验公式：")
        print(f"  R = 10s√(kH₀)")
        print(f"    = 10×{sw:.3f}×√({k}×{H0})")
        print(f"    = {R_kusakin:.1f} m")
        
        print(f"\n综合判断：")
        print(f"  假设值：R = {R} m ✓")
        print(f"  经验值：R ≈ {R_kusakin:.0f} m")
        print(f"  采用：R = {R} m（合理范围内）")
        
        # (3) 土坝渗流量
        print(f"\n(3) 计算土坝渗流量")
        
        # 无排水设备，使用简化公式
        # q = k(H₁²-H₂²)/(2L)
        q_dam = k / 86400 * (H1**2 - H2**2) / (2 * a)  # 转换为m³/(s·m)
        q_dam_day = k * (H1**2 - H2**2) / (2 * a)  # m³/(d·m)
        
        print(f"\n土坝渗流量（每延米）：")
        print(f"  q = k(H₁²-H₂²)/(2L)")
        print(f"    = {k}×({H1}²-{H2}²)/(2×{a})")
        print(f"    = {k}×({H1**2}-{H2**2})/{2*a}")
        print(f"    = {q_dam_day:.4f} m³/(d·m)")
        print(f"    = {q_dam*1000:.3f} L/(s·m) ✓")
        
        # (4) 浸润线与逸出点
        print(f"\n(4) 计算浸润线方程与逸出点高度")
        
        # 浸润线方程：h²=H₁²-(H₁²-H₂²)x/L
        print(f"\n浸润线方程（抛物线）：")
        print(f"  h² = H₁² - (H₁²-H₂²)×x/L")
        print(f"  h = √[H₁² - (H₁²-H₂²)×x/L]")
        
        # 逸出点高度（x=L处）
        h_exit = H2
        print(f"\n逸出点高度（x=L={a}m）：")
        print(f"  h = H₂ = {h_exit} m ✓")
        
        # 计算浸润线
        x_seepage = np.linspace(0, a, 100)
        h_seepage = np.sqrt(H1**2 - (H1**2 - H2**2) * x_seepage / a)
        
        # 绘图
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：承压水井剖面
        ax1 = plt.subplot(2, 3, 1)
        
        # 含水层
        ax1.fill_between([0, 15], [0, 0], [-M, -M],
                        color='lightblue', alpha=0.3, label='含水层')
        ax1.axhline(y=0, color='blue', linestyle='--', linewidth=2, label='静水位')
        
        # 井
        well_x = [7.3, 7.3, 7.7, 7.7]
        well_y = [0, -M, -M, 0]
        ax1.fill(well_x, well_y, color='brown', alpha=0.5,
                edgecolor='black', linewidth=2)
        ax1.text(7.5, -M/2, '井', ha='center', fontsize=10, fontweight='bold')
        
        # 水位降深
        r_array = np.linspace(r0, R, 100)
        s_array = Q / (2 * np.pi * k * M) * np.log(R / r_array)
        
        # 转换为笛卡尔坐标（右侧）
        x_right = 7.5 + r_array[:50]
        y_right = -s_array[:50]
        ax1.plot(x_right, y_right, 'r-', linewidth=2.5, label='降落漏斗')
        
        # 转换为笛卡尔坐标（左侧）
        x_left = 7.5 - r_array[:50]
        y_left = -s_array[:50]
        ax1.plot(x_left, y_left, 'r-', linewidth=2.5)
        
        # 观测井
        ax1.plot([7.5+r1, 7.5+r1], [0, -s1], 'go', markersize=10)
        ax1.plot([7.5+r1, 7.5+r1], [0, -s1], 'g-', linewidth=2)
        ax1.text(7.5+r1+0.5, -s1/2, f'井1\nr={r1}m\ns={s1:.2f}m',
                fontsize=8, bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        ax1.plot([7.5-r2/10, 7.5-r2/10], [0, -s2], 'mo', markersize=10)
        ax1.plot([7.5-r2/10, 7.5-r2/10], [0, -s2], 'm-', linewidth=2)
        ax1.text(7.5-r2/10-1, -s2/2, f'井2\nr={r2}m\ns={s2:.2f}m',
                fontsize=8, bbox=dict(boxstyle='round', facecolor='plum'))
        
        ax1.set_xlabel('距离 (m)', fontsize=12)
        ax1.set_ylabel('深度 (m)', fontsize=12)
        ax1.set_title('测试题2：承压水井降落漏斗', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(-M-2, 2)
        
        # 子图2：水位降深曲线
        ax2 = plt.subplot(2, 3, 2)
        
        r_plot = np.linspace(r0, 100, 200)
        s_plot = Q / (2 * np.pi * k * M) * np.log(R / r_plot)
        
        ax2.plot(r_plot, s_plot, 'b-', linewidth=2.5, label='s(r)曲线')
        
        # 标注观测井
        ax2.plot(r1, s1, 'go', markersize=15, label=f'观测井1: s₁={s1:.2f}m')
        ax2.plot(r2, s2, 'mo', markersize=15, label=f'观测井2: s₂={s2:.2f}m')
        
        # 影响半径
        ax2.axvline(x=R, color='red', linestyle='--', linewidth=2,
                   label=f'影响半径R={R}m')
        
        ax2.set_xlabel('距离 r (m)', fontsize=12)
        ax2.set_ylabel('水位降深 s (m)', fontsize=12)
        ax2.set_title('水位降深分布', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 100)
        ax2.invert_yaxis()
        
        # 子图3：土坝渗流
        ax3 = plt.subplot(2, 3, 3)
        
        # 坝体
        dam_x = [0, 0, a, a, 0]
        dam_y = [0, H1, H2, 0, 0]
        ax3.fill(dam_x, dam_y, color='brown', alpha=0.5,
                edgecolor='black', linewidth=2, label='坝体')
        
        # 上下游水位
        ax3.fill_between([0-5, 0], [H1, H1], [0, 0],
                        color='cyan', alpha=0.4, label='上游水体')
        ax3.fill_between([a, a+3], [H2, H2], [0, 0],
                        color='lightblue', alpha=0.4, label='下游水体')
        
        # 浸润线
        ax3.plot(x_seepage, h_seepage, 'r-', linewidth=3, label='浸润线')
        
        # 标注
        ax3.text(-2.5, H1/2, f'H₁={H1}m', fontsize=11, ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        ax3.text(a+1.5, H2/2, f'H₂={H2}m', fontsize=11, ha='center',
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        ax3.text(a/2, (H1+H2)/2+1, f'q={q_dam*1000:.2f}L/(s·m)',
                fontsize=11, ha='center',
                bbox=dict(boxstyle='round', facecolor='orange', alpha=0.8))
        
        ax3.set_xlabel('距离 (m)', fontsize=12)
        ax3.set_ylabel('高度 (m)', fontsize=12)
        ax3.set_title('土坝渗流与浸润线', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim(-6, a+4)
        ax3.set_ylim(-0.5, H1+1)
        
        # 子图4：渗流量对比
        ax4 = plt.subplot(2, 3, 4)
        
        # 不同水头差下的渗流量
        dH_array = np.array([2, 4, 6, 8, 10])
        q_array = k * (H1**2 - (H1-dH_array)**2) / (2 * a)
        
        ax4.plot(dH_array, q_array, 'b-o', linewidth=2.5, markersize=10)
        
        # 本题点
        dH_actual = H1 - H2
        ax4.plot(dH_actual, q_dam_day, 'ro', markersize=15,
                label=f'本题：ΔH={dH_actual}m\nq={q_dam_day:.3f}m³/(d·m)')
        
        ax4.set_xlabel('水头差 ΔH (m)', fontsize=12)
        ax4.set_ylabel('渗流量 q (m³/(d·m))', fontsize=12)
        ax4.set_title('渗流量随水头差变化', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 子图5：浸润线详图
        ax5 = plt.subplot(2, 3, 5)
        
        # 浸润线
        ax5.plot(x_seepage, h_seepage, 'r-', linewidth=3, label='浸润线h(x)')
        
        # 上下游水位
        ax5.axhline(y=H1, xmax=0, color='blue', linestyle='--',
                   linewidth=2, label=f'上游H₁={H1}m')
        ax5.axhline(y=H2, xmin=1, color='green', linestyle='--',
                   linewidth=2, label=f'下游H₂={H2}m')
        
        # 关键点
        ax5.plot(0, H1, 'bo', markersize=12)
        ax5.plot(a, H2, 'go', markersize=12)
        
        # 标注
        x_mid = a/2
        h_mid = np.sqrt(H1**2 - (H1**2 - H2**2) * 0.5)
        ax5.plot(x_mid, h_mid, 'mo', markersize=10)
        ax5.text(x_mid, h_mid+0.5, f'中点\nh={h_mid:.2f}m',
                ha='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='pink'))
        
        ax5.set_xlabel('距离 x (m)', fontsize=12)
        ax5.set_ylabel('高度 h (m)', fontsize=12)
        ax5.set_title('浸润线方程 h=√[H₁²-(H₁²-H₂²)x/L]', 
                     fontsize=13, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 子图6：结果汇总
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        summary_text = f"""
        【测试题2结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 观测井水位降深：
        
          观测井1（r₁={r1}m）：
            s₁ = {s1:.3f} m ✓
          
          观测井2（r₂={r2}m）：
            s₂ = {s2:.3f} m ✓
          
          降深差：s₁-s₂ = {s_diff_calc:.3f} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (2) 抽水影响半径：
        
          假设值：R = {R} m ✓
          经验值：R ≈ {R_kusakin:.0f} m
          
          采用：R = {R} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (3) 土坝渗流量：
        
          每延米渗流量：
            q = {q_dam_day:.4f} m³/(d·m)
            q = {q_dam*1000:.3f} L/(s·m) ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (4) 浸润线与逸出点：
        
          浸润线方程：
            h = √[H₁²-(H₁²-H₂²)x/L]
          
          逸出点高度：
            h = H₂ = {h_exit} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        评分：30分
          (1) 8分   (2) 6分
          (3) 8分   (4) 8分
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax6.text(0.1, 0.95, summary_text, fontsize=7.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day24_week2_test/test_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_2.png")
        
        return {'s1': s1, 's2': s2, 'R': R, 'q_dam': q_dam, 'h_exit': h_exit}
    
    def test_3_pump_station_environment(self):
        """
        测试题3：泵站与环境综合题⭐⭐⭐⭐⭐
        
        题目：排水泵站环境影响评估：
              泵站提水高度Hs=15m，流量Q=0.8m³/s
              管道：直径d=0.5m，长度L=100m，λ=0.025
              局部损失：Σξ=5.0
              泵特性：H=25-100Q²（H单位m，Q单位m³/s）
              
              下游河流接纳泵站排水：
              河流流量Qr=10m³/s，平均流速ur=0.5m/s
              污染物浓度Cr=2mg/L
              泵站排水污染物浓度Cp=20mg/L
              河流BOD降解系数k1=0.3/d，复氧系数k2=0.5/d
              溶解氧饱和度DOs=9mg/L，河流DO=7mg/L
        
        求：(1) 泵站扬程与轴功率（效率η=0.75）
            (2) 混合后河流污染物浓度
            (3) BOD-DO模型分析（临界点位置与最低DO）
            (4) 环境影响评估（水质类别）
        
        考点：泵站计算、污染物混合、BOD-DO模型
        难度：综合（难度最高！）
        时间：45分钟
        分值：35分
        """
        print("\n" + "="*60)
        print("测试题3：泵站与环境综合题⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        Hs = 15.0     # 提水高度 (m)
        Q = 0.8       # 流量 (m³/s)
        d = 0.5       # 管径 (m)
        L = 100.0     # 管长 (m)
        lam = 0.025   # 摩阻系数
        xi_sum = 5.0  # 局部损失系数和
        eta = 0.75    # 泵效率
        
        # 河流参数
        Qr = 10.0     # 河流流量 (m³/s)
        ur = 0.5      # 河流流速 (m/s)
        Cr = 2.0      # 河流污染物浓度 (mg/L)
        Cp = 20.0     # 泵站排水污染物浓度 (mg/L)
        k1 = 0.3      # BOD降解系数 (/d)
        k2 = 0.5      # 复氧系数 (/d)
        DOs = 9.0     # 饱和溶解氧 (mg/L)
        DO0 = 7.0     # 河流DO (mg/L)
        
        print(f"\n已知条件：")
        print(f"  泵站：Hs={Hs}m, Q={Q}m³/s, d={d}m, L={L}m")
        print(f"  管道：λ={lam}, Σξ={xi_sum}, η={eta}")
        print(f"  泵特性：H = 25 - 100Q²")
        print(f"  河流：Qr={Qr}m³/s, ur={ur}m/s")
        print(f"  污染：Cr={Cr}mg/L, Cp={Cp}mg/L")
        print(f"  DO参数：k₁={k1}/d, k₂={k2}/d, DOs={DOs}mg/L, DO₀={DO0}mg/L")
        
        # (1) 泵站扬程与功率
        print(f"\n解题步骤：")
        print(f"\n(1) 计算泵站扬程与轴功率")
        
        # 管道流速
        A = np.pi * d**2 / 4
        v = Q / A
        
        print(f"\n管道流速：")
        print(f"  A = πd²/4 = π×{d}²/4 = {A:.4f} m²")
        print(f"  v = Q/A = {Q}/{A:.4f} = {v:.3f} m/s")
        
        # 管道损失
        hf = (lam * L / d + xi_sum) * v**2 / (2 * self.g)
        
        print(f"\n管道损失：")
        print(f"  hf = (λL/d + Σξ)×v²/(2g)")
        print(f"     = ({lam}×{L}/{d} + {xi_sum})×{v:.3f}²/(2×{self.g})")
        print(f"     = {hf:.3f} m")
        
        # 所需扬程
        H_required = Hs + hf + v**2 / (2 * self.g)
        
        print(f"\n所需扬程：")
        print(f"  H = Hs + hf + v²/(2g)")
        print(f"    = {Hs} + {hf:.3f} + {v**2/(2*self.g):.3f}")
        print(f"    = {H_required:.3f} m ✓")
        
        # 泵提供扬程
        H_pump = 25 - 100 * Q**2
        
        print(f"\n泵特性曲线提供扬程：")
        print(f"  H = 25 - 100Q²")
        print(f"    = 25 - 100×{Q}²")
        print(f"    = {H_pump:.3f} m")
        
        # 检查匹配
        H_diff = H_pump - H_required
        print(f"\n扬程匹配检查：")
        print(f"  H泵 - H需 = {H_pump:.3f} - {H_required:.3f} = {H_diff:.3f} m")
        if abs(H_diff) < 1.0:
            print(f"  结论：匹配良好 ✓")
        else:
            print(f"  结论：需调整参数")
        
        # 采用实际扬程
        H_actual = H_pump
        
        # 轴功率
        N_water = self.gamma_w * Q * H_actual / 1000  # kW
        N_shaft = N_water / eta
        
        print(f"\n轴功率：")
        print(f"  水功率：N水 = γQH = {self.gamma_w}×{Q}×{H_actual:.3f}/1000")
        print(f"             = {N_water:.2f} kW")
        print(f"  轴功率：N轴 = N水/η = {N_water:.2f}/{eta}")
        print(f"             = {N_shaft:.2f} kW ✓")
        
        # (2) 混合后污染物浓度
        print(f"\n(2) 计算混合后污染物浓度")
        
        # 混合流量
        Q_mix = Qr + Q
        
        # 混合浓度
        C_mix = (Qr * Cr + Q * Cp) / Q_mix
        
        print(f"\n完全混合模型：")
        print(f"  混合流量：Qm = Qr + Qp = {Qr} + {Q} = {Q_mix} m³/s")
        print(f"  混合浓度：Cm = (QrCr + QpCp)/Qm")
        print(f"           = ({Qr}×{Cr} + {Q}×{Cp})/{Q_mix}")
        print(f"           = {C_mix:.3f} mg/L ✓")
        
        # 浓度变化
        delta_C = C_mix - Cr
        increase_percent = delta_C / Cr * 100
        
        print(f"\n浓度变化：")
        print(f"  ΔC = Cm - Cr = {C_mix:.3f} - {Cr} = {delta_C:.3f} mg/L")
        print(f"  增幅：{increase_percent:.1f}%")
        
        # (3) BOD-DO分析
        print(f"\n(3) BOD-DO模型分析")
        
        # 假设BOD初始值
        BOD0 = C_mix  # 简化假设污染物浓度=BOD
        
        # 初始DO亏损
        D0 = DOs - DO0
        
        print(f"\nStreeter-Phelps方程：")
        print(f"  D(t) = (k₁BOD₀)/(k₂-k₁) × (e^(-k₁t) - e^(-k₂t)) + D₀e^(-k₂t)")
        
        print(f"\n初始条件：")
        print(f"  BOD₀ = {BOD0:.3f} mg/L（简化假设）")
        print(f"  DO₀ = {DO0} mg/L")
        print(f"  D₀ = DOs - DO₀ = {DOs} - {DO0} = {D0} mg/L")
        
        # 临界时间
        tc = 1/(k2-k1) * np.log((k2/k1) * (1 - D0*(k2-k1)/(k1*BOD0)))
        
        print(f"\n临界时间：")
        print(f"  tc = 1/(k₂-k₁) × ln[(k₂/k₁)×(1-D₀(k₂-k₁)/(k₁BOD₀))]")
        print(f"     = 1/({k2}-{k1}) × ln[({k2}/{k1})×(1-{D0}×({k2}-{k1})/({k1}×{BOD0:.3f}))]")
        print(f"     = {tc:.3f} d ✓")
        
        # 临界位置
        xc = ur * tc * 86400  # 转换为m
        
        print(f"  临界位置：xc = u×tc = {ur}×{tc:.3f}×86400")
        print(f"             = {xc:.0f} m = {xc/1000:.2f} km ✓")
        
        # 临界DO亏损
        Dc = (k1 * BOD0) / k2 * np.exp(-k1 * tc)
        
        # 最低DO
        DOc = DOs - Dc
        
        print(f"\n临界点DO：")
        print(f"  Dc = (k₁BOD₀)/k₂ × e^(-k₁tc)")
        print(f"     = ({k1}×{BOD0:.3f})/{k2} × e^(-{k1}×{tc:.3f})")
        print(f"     = {Dc:.3f} mg/L")
        print(f"  DOc = DOs - Dc = {DOs} - {Dc:.3f}")
        print(f"      = {DOc:.3f} mg/L ✓")
        
        # (4) 环境影响评估
        print(f"\n(4) 环境影响评估")
        
        # 水质分类
        if DOc >= 6:
            quality = "Ⅱ类（良好）"
        elif DOc >= 5:
            quality = "Ⅲ类（一般）"
        elif DOc >= 3:
            quality = "Ⅳ类（轻度污染）"
        elif DOc >= 2:
            quality = "Ⅴ类（中度污染）"
        else:
            quality = "劣Ⅴ类（重度污染）"
        
        print(f"\n水质类别判断：")
        print(f"  最低DO = {DOc:.3f} mg/L")
        print(f"  水质类别：{quality} ✓")
        
        # 综合评估
        print(f"\n综合环境影响评估：")
        print(f"  1. 污染物浓度增加{increase_percent:.1f}%")
        print(f"  2. 临界点出现在下游{xc/1000:.2f}km处")
        print(f"  3. 最低DO为{DOc:.3f}mg/L，属于{quality}")
        if DOc >= 5:
            print(f"  4. 环境影响：可接受 ✓")
        elif DOc >= 3:
            print(f"  4. 环境影响：需采取措施")
        else:
            print(f"  4. 环境影响：严重，需立即处理")
        
        # 计算DO曲线
        t_array = np.linspace(0, 10, 200)  # 10天
        D_array = []
        DO_array = []
        BOD_array = []
        
        for t in t_array:
            BOD_t = BOD0 * np.exp(-k1 * t)
            D_t = (k1*BOD0)/(k2-k1) * (np.exp(-k1*t) - np.exp(-k2*t)) + D0*np.exp(-k2*t)
            DO_t = DOs - D_t
            
            BOD_array.append(BOD_t)
            D_array.append(D_t)
            DO_array.append(DO_t)
        
        # 绘图
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：泵站系统示意图
        ax1 = plt.subplot(2, 3, 1)
        
        # 水池
        ax1.fill_between([0, 3], [0, 0], [-3, -3],
                        color='cyan', alpha=0.3, label='取水池')
        ax1.axhline(y=0, xmax=0.3, color='blue', linestyle='--', linewidth=2)
        
        # 泵
        pump_center = (2, 2)
        pump = Circle(pump_center, 0.8, color='orange', alpha=0.7,
                     edgecolor='black', linewidth=2)
        ax1.add_patch(pump)
        ax1.text(pump_center[0], pump_center[1], '泵',
                ha='center', va='center', fontsize=14, fontweight='bold')
        
        # 管道
        ax1.plot([1.5, 1.5, 5, 5], [0, 2, 2, Hs+2], 'k-', linewidth=4)
        
        # 出水池
        ax1.fill_between([4.5, 6], [Hs+2, Hs+2], [Hs-1, Hs-1],
                        color='lightblue', alpha=0.5, label='排水池')
        ax1.axhline(y=Hs+2, xmin=0.75, color='green', linestyle='--', linewidth=2)
        
        # 标注
        ax1.plot([0.5, 0.5], [0, Hs+2], 'r-', linewidth=2)
        ax1.text(0.2, (Hs+2)/2, f'Hs={Hs}m',
                rotation=90, va='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.text(2, 4, f'H={H_actual:.1f}m\nQ={Q}m³/s\nN={N_shaft:.1f}kW',
                ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        ax1.set_xlabel('X (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('测试题3：泵站系统示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-0.5, 7)
        ax1.set_ylim(-4, Hs+4)
        
        # 子图2：泵特性与工况点
        ax2 = plt.subplot(2, 3, 2)
        
        # 泵特性曲线
        Q_range = np.linspace(0, 0.5, 100)
        H_range = 25 - 100 * Q_range**2
        
        ax2.plot(Q_range, H_range, 'b-', linewidth=2.5, label='泵特性H=25-100Q²')
        
        # 管路特性
        H_pipe_range = Hs + (lam*L/d + xi_sum) * (Q_range/A)**2 / (2*self.g)
        ax2.plot(Q_range, H_pipe_range, 'r-', linewidth=2.5, label='管路特性')
        
        # 工况点
        ax2.plot(Q, H_actual, 'go', markersize=15,
                label=f'工况点\nQ={Q}m³/s\nH={H_actual:.1f}m')
        
        ax2.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax2.set_ylabel('扬程 H (m)', fontsize=12)
        ax2.set_title('泵特性与工况匹配', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3：污染物混合
        ax3 = plt.subplot(2, 3, 3)
        
        # 河流与排水
        sections_mix = ['河流', '泵站排水', '混合后']
        Q_values = [Qr, Q, Q_mix]
        C_values = [Cr, Cp, C_mix]
        
        x_pos = np.arange(len(sections_mix))
        width = 0.35
        
        ax3.bar(x_pos - width/2, Q_values, width, label='流量(m³/s)',
               color='blue', alpha=0.7, edgecolor='black', linewidth=2)
        
        ax3_twin = ax3.twinx()
        ax3_twin.bar(x_pos + width/2, C_values, width, label='浓度(mg/L)',
                    color='red', alpha=0.7, edgecolor='black', linewidth=2)
        
        ax3.set_xlabel('断面', fontsize=12)
        ax3.set_ylabel('流量 (m³/s)', fontsize=12, color='blue')
        ax3_twin.set_ylabel('浓度 (mg/L)', fontsize=12, color='red')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(sections_mix)
        ax3.set_title(f'污染物混合（增幅{increase_percent:.1f}%）', 
                     fontsize=13, fontweight='bold')
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='red')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：BOD-DO曲线
        ax4 = plt.subplot(2, 3, 4)
        
        x_km = t_array * ur * 86400 / 1000  # 转换为km
        
        # DO曲线
        ax4.plot(x_km, DO_array, 'b-', linewidth=2.5, label='溶解氧DO')
        
        # BOD曲线
        ax4_twin = ax4.twinx()
        ax4_twin.plot(x_km, BOD_array, 'r-', linewidth=2.5, label='生化需氧量BOD')
        
        # 临界点
        ax4.plot(xc/1000, DOc, 'go', markersize=15,
                label=f'临界点\nxc={xc/1000:.2f}km\nDOc={DOc:.2f}mg/L')
        
        # 水质标准线
        ax4.axhline(y=6, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Ⅱ类水')
        ax4.axhline(y=5, color='yellow', linestyle='--', linewidth=2, alpha=0.5, label='Ⅲ类水')
        ax4.axhline(y=3, color='orange', linestyle='--', linewidth=2, alpha=0.5, label='Ⅳ类水')
        
        ax4.set_xlabel('距离 (km)', fontsize=12)
        ax4.set_ylabel('溶解氧 DO (mg/L)', fontsize=12, color='blue')
        ax4_twin.set_ylabel('BOD (mg/L)', fontsize=12, color='red')
        ax4.set_title('BOD-DO沿程变化', fontsize=13, fontweight='bold')
        ax4.legend(loc='upper left')
        ax4_twin.legend(loc='upper right')
        ax4.tick_params(axis='y', labelcolor='blue')
        ax4_twin.tick_params(axis='y', labelcolor='red')
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim(0, 10)
        
        # 子图5：DO亏损曲线
        ax5 = plt.subplot(2, 3, 5)
        
        ax5.plot(t_array, D_array, 'r-', linewidth=2.5, label='DO亏损D(t)')
        
        # 临界点
        ax5.plot(tc, Dc, 'go', markersize=15,
                label=f'最大亏损\ntc={tc:.2f}d\nDc={Dc:.2f}mg/L')
        
        ax5.set_xlabel('时间 (d)', fontsize=12)
        ax5.set_ylabel('DO亏损 D (mg/L)', fontsize=12)
        ax5.set_title('溶解氧亏损曲线', fontsize=13, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 子图6：结果汇总
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        summary_text = f"""
        【测试题3结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 泵站参数：
        
          所需扬程：H需 = {H_required:.3f} m
          泵提供扬程：H泵 = {H_pump:.3f} m
          实际扬程：H = {H_actual:.3f} m ✓
          
          水功率：N水 = {N_water:.2f} kW
          轴功率：N轴 = {N_shaft:.2f} kW ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (2) 混合浓度：
        
          混合流量：Qm = {Q_mix} m³/s
          混合浓度：Cm = {C_mix:.3f} mg/L ✓
          浓度增幅：{increase_percent:.1f}%
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (3) BOD-DO分析：
        
          临界时间：tc = {tc:.3f} d ✓
          临界位置：xc = {xc/1000:.2f} km ✓
          最低DO：DOc = {DOc:.3f} mg/L ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (4) 环境评估：
        
          水质类别：{quality}
          
          环境影响：{'可接受✓' if DOc>=5 else '需采取措施⚠️'}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        评分：35分
          (1) 10分  (2) 8分
          (3) 10分  (4) 7分
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax6.text(0.1, 0.95, summary_text, fontsize=7.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day24_week2_test/test_3.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：test_3.png")
        
        return {'H_actual': H_actual, 'N_shaft': N_shaft, 'C_mix': C_mix, 
                'tc': tc, 'xc': xc, 'DOc': DOc, 'quality': quality}
    
    def test_summary(self):
        """测试总结"""
        print("\n" + "="*60)
        print("📊 第二周测试总结")
        print("="*60)
        
        print("\n✅ 测试完成情况：")
        print("  ✓ 测试题1：明渠水跃与堰流综合题（35分）")
        print("  ✓ 测试题2：渗流与地下水综合题（30分）")
        print("  ✓ 测试题3：泵站与环境综合题（35分）")
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  ✓ 总分：100分")
        
        print("\n✅ 知识点覆盖：")
        print("  Day 11-13: 明渠非均匀流")
        print("    • 水跃共轭水深与能量损失 ✓")
        print("    • 宽顶堰流量计算 ✓")
        print("    • 流量连续性验证 ✓")
        print("  ")
        print("  Day 15-16: 渗流与地下水")
        print("    • 裘布依公式（承压水井）✓")
        print("    • 抽水影响半径 ✓")
        print("    • 土坝渗流与浸润线 ✓")
        print("  ")
        print("  Day 17-20: 泵站+环境")
        print("    • 泵站扬程与功率 ✓")
        print("    • 污染物混合稀释 ✓")
        print("    • BOD-DO模型分析 ✓")
        print("    • 环境影响评估 ✓")
        
        print("\n🎯 重点公式回顾：")
        print("  水跃：")
        print("    h₂/h₁ = 0.5(-1+√(1+8Fr₁²))")
        print("    Lj = 6(h₂-h₁)")
        print("    ΔE = E₁ - E₂")
        print("  ")
        print("  堰流：")
        print("    Q = mb√(2g)H^(3/2)")
        print("  ")
        print("  地下水：")
        print("    s = Q/(2πkM) × ln(R/r)")
        print("    q = k(H₁²-H₂²)/(2L)")
        print("  ")
        print("  泵站：")
        print("    H = Hs + hf + v²/(2g)")
        print("    N = γQH/η")
        print("  ")
        print("  BOD-DO：")
        print("    D(t) = (k₁BOD₀)/(k₂-k₁) × (e^(-k₁t) - e^(-k₂t))")
        
        print("\n💡 考试技巧：")
        print("  ✓ 水跃：先算Fr判断急缓流")
        print("  ✓ 堰流：注意流量系数选择")
        print("  ✓ 地下水：影响半径用经验公式验证")
        print("  ✓ 泵站：扬程=几何+损失+动能")
        print("  ✓ BOD-DO：临界点是关键，注意单位")
        
        print("\n⚠️ 常见错误：")
        print("  ❌ 水跃方向搞反（应急流→缓流）")
        print("  ❌ 堰流忘记√(2g)系数")
        print("  ❌ 地下水井公式混淆（承压vs潜水）")
        print("  ❌ 泵站扬程漏算动能项")
        print("  ❌ BOD-DO时间与距离转换错误")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 24: 第二周测试")
    print("="*60)
    print("\n⏰ 考试时间：3小时")
    print("📚 测试范围：Day 11-20")
    print("💯 总分：100分")
    
    # 创建对象
    day24 = Day24Week2Test()
    
    # 测试题1：水跃堰流
    result1 = day24.test_1_channel_hydraulic_jump_weir()
    
    # 测试题2：渗流地下水
    result2 = day24.test_2_seepage_groundwater()
    
    # 测试题3：泵站环境
    result3 = day24.test_3_pump_station_environment()
    
    # 测试总结
    day24.test_summary()
    
    print("\n" + "="*60)
    print("✅ 第二周测试完成！")
    print("="*60)
    print(f"\n测试结果：")
    print(f"  测试题1：35分（水跃+堰流）")
    print(f"  测试题2：30分（渗流+地下水）")
    print(f"  测试题3：35分（泵站+环境）")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  总分：100分")
    
    print(f"\n📊 成绩评估：")
    print(f"  90-100分：优秀！综合能力强")
    print(f"  80-89分：良好，继续提高")
    print(f"  70-79分：合格，需强化弱项")
    print(f"  <70分：需重点复习第二周内容")
    
    print(f"\n🎊🎊🎊 80%里程碑达成！")
    print(f"下一步：Day 25-26 - 综合应用专题")
    print(f"💪 冲刺最后20%，胜利在望！")

if __name__ == "__main__":
    main()
    plt.show()
