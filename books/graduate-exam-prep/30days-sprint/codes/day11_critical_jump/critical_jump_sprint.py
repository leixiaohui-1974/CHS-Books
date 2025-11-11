#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 11: 临界水深与水跃
Sprint Day 11: Critical Depth and Hydraulic Jump

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 临界水深：hc = (q²/g)^(1/3) 或 hc = (Q²/(gb²))^(1/3)
  2. 水跃共轭水深：h₂ = (h₁/2)(-1 + √(1 + 8Fr₁²))
  3. 水跃消能：ΔE = (h₂ - h₁)³/(4h₁h₂)

🎯 学习目标：
  - 掌握临界水深计算
  - 熟练计算水跃共轭水深
  - 理解水跃消能原理

💪 今日格言：水跃是考研必考题！掌握共轭水深公式=拿到15分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.optimize import fsolve

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day11CriticalJump:
    """
    Day 11：临界水深与水跃
    
    包含3个核心例题：
    1. 基础题：矩形明渠临界水深
    2. 强化题：水跃共轭水深与消能
    3. 综合题：淹没水跃分析
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        
    def example_1_critical_depth(self):
        """
        例题1：矩形明渠临界水深计算（基础题）⭐⭐⭐⭐⭐
        
        题目：矩形明渠，宽b=3m，流量Q=15m³/s
        求：(1) 临界水深hc
            (2) 临界流速vc
            (3) 判断h₀=2m时的流态
        
        考点：临界水深公式，Froude数，流态判断
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题1：矩形明渠临界水深计算（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 3.0   # 渠宽 (m)
        Q = 15.0  # 流量 (m³/s)
        h0 = 2.0  # 给定水深 (m)
        
        print(f"\n已知条件：")
        print(f"  矩形明渠宽度 b = {b:.1f} m")
        print(f"  流量 Q = {Q:.1f} m³/s")
        print(f"  给定水深 h₀ = {h0:.1f} m")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 计算临界水深
        print(f"\n(1) 计算临界水深：")
        print(f"    单宽流量 q = Q/b = {Q}/{b} = {Q/b:.3f} m²/s")
        print(f"    ")
        print(f"    临界水深公式（矩形断面）：")
        print(f"    hc = (q²/g)^(1/3)")
        
        q = Q / b
        hc = (q**2 / self.g)**(1/3)
        
        print(f"       = ({q:.3f}²/{self.g:.2f})^(1/3)")
        print(f"       = {hc:.4f} m ✓")
        
        # (2) 计算临界流速
        Ac = b * hc
        vc = Q / Ac
        
        print(f"\n(2) 计算临界流速：")
        print(f"    Ac = bhc = {b} × {hc:.4f} = {Ac:.4f} m²")
        print(f"    vc = Q/Ac = {Q}/{Ac:.4f} = {vc:.3f} m/s ✓")
        
        # 验证：vc = √(ghc)
        vc_check = np.sqrt(self.g * hc)
        print(f"    ")
        print(f"    验证（临界流条件）：")
        print(f"    vc = √(ghc) = √({self.g:.2f} × {hc:.4f}) = {vc_check:.3f} m/s")
        print(f"    误差 = |{vc:.3f} - {vc_check:.3f}| = {abs(vc-vc_check):.6f} m/s ✓")
        
        # (3) 判断h₀=2m时的流态
        print(f"\n(3) 判断h₀={h0}m时的流态：")
        A0 = b * h0
        v0 = Q / A0
        Fr0 = v0 / np.sqrt(self.g * h0)
        
        print(f"    A₀ = bh₀ = {b} × {h0} = {A0:.1f} m²")
        print(f"    v₀ = Q/A₀ = {Q}/{A0:.1f} = {v0:.3f} m/s")
        print(f"    Fr₀ = v₀/√(gh₀) = {v0:.3f}/√({self.g:.2f}×{h0})")
        print(f"        = {Fr0:.4f}")
        print(f"    ")
        
        if h0 > hc:
            print(f"    ∵ h₀ > hc ({h0:.1f} > {hc:.4f})")
            print(f"      Fr₀ < 1 ({Fr0:.4f} < 1)")
            print(f"    ∴ 流态：缓流（亚临界流） ✓")
            flow_type = "缓流"
        elif h0 < hc:
            print(f"    ∵ h₀ < hc ({h0:.1f} < {hc:.4f})")
            print(f"      Fr₀ > 1 ({Fr0:.4f} > 1)")
            print(f"    ∴ 流态：急流（超临界流）")
            flow_type = "急流"
        else:
            print(f"    ∵ h₀ = hc ({h0:.1f} = {hc:.4f})")
            print(f"      Fr₀ = 1")
            print(f"    ∴ 流态：临界流")
            flow_type = "临界流"
        
        # 绘图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 子图1：断面比较（临界水深 vs 给定水深）
        ax1.fill([0, b, b, 0], [0, 0, hc, hc], alpha=0.3, color='yellow', 
                edgecolor='orange', linewidth=2, label=f'临界水深 hc={hc:.3f}m')
        ax1.fill([0, b, b, 0], [0, 0, h0, h0], alpha=0.3, color='lightblue', 
                edgecolor='blue', linewidth=2, label=f'给定水深 h₀={h0}m')
        
        # 标注
        ax1.plot([b/2, b/2], [0, hc], 'r--', linewidth=2)
        ax1.text(b/2+0.15, hc/2, f'hc={hc:.3f}m', fontsize=11, color='red')
        ax1.plot([b/2-0.3, b/2-0.3], [0, h0], 'b--', linewidth=2)
        ax1.text(b/2-0.6, h0/2, f'h₀={h0}m', fontsize=11, color='blue')
        
        # 流速箭头
        if h0 > hc:
            ax1.arrow(0.5, h0/2, 0.4, 0, head_width=0.1, head_length=0.08, 
                     fc='blue', ec='blue', linewidth=2)
            ax1.text(1.0, h0/2+0.15, f'缓流\nFr={Fr0:.3f}<1', fontsize=10, color='blue')
        
        ax1.set_xlabel('宽度 (m)', fontsize=12)
        ax1.set_ylabel('水深 (m)', fontsize=12)
        ax1.set_title('Day 11 例题1：临界水深与给定水深对比', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.2, b+0.5])
        ax1.set_ylim([0, h0*1.2])
        ax1.set_aspect('equal')
        
        # 子图2：比能曲线
        h_range = np.linspace(0.2, 3, 100)
        E_range = []
        for h in h_range:
            A = b * h
            v = Q / A
            E = h + v**2 / (2*self.g)
            E_range.append(E)
        
        Ec = hc + vc**2/(2*self.g)
        E0 = h0 + v0**2/(2*self.g)
        
        ax2.plot(E_range, h_range, 'b-', linewidth=2, label='比能曲线 E(h)')
        ax2.axhline(y=hc, color='red', linestyle='--', linewidth=2, label=f'临界水深 hc={hc:.3f}m')
        ax2.plot(Ec, hc, 'ro', markersize=12, label=f'临界点 (Ec={Ec:.3f}m)')
        ax2.plot(E0, h0, 'bs', markersize=12, label=f'工作点 (E₀={E0:.3f}m, h₀={h0}m)')
        
        # 标注临界点
        ax2.plot([Ec, Ec], [0, hc], 'r:', linewidth=1)
        ax2.text(Ec+0.05, 0.3, f'Emin={Ec:.3f}m', fontsize=10, color='red', rotation=90)
        
        ax2.set_xlabel('比能 E (m)', fontsize=12)
        ax2.set_ylabel('水深 h (m)', fontsize=12)
        ax2.set_title('比能曲线（E = h + v²/(2g)）', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([1.0, 4])
        ax2.set_ylim([0, 3])
        
        # 子图3：Froude数与水深关系
        Fr_range = []
        for h in h_range:
            A = b * h
            v = Q / A
            Fr = v / np.sqrt(self.g * h)
            Fr_range.append(Fr)
        
        ax3.plot(h_range, Fr_range, 'purple', linewidth=2, label='Fr(h)曲线')
        ax3.axhline(y=1, color='red', linestyle='--', linewidth=2, label='Fr=1（临界）')
        ax3.axvline(x=hc, color='red', linestyle='--', linewidth=1)
        ax3.plot(hc, 1, 'ro', markersize=12, label=f'临界点 (hc={hc:.3f}m)')
        ax3.plot(h0, Fr0, 'bs', markersize=12, label=f'工作点 (h₀={h0}m, Fr={Fr0:.3f})')
        
        # 标注区域
        ax3.fill_between([0.2, hc], 5, 0, alpha=0.2, color='orange', label='急流区 (Fr>1)')
        ax3.fill_between([hc, 3], 5, 0, alpha=0.2, color='lightblue', label='缓流区 (Fr<1)')
        
        ax3.set_xlabel('水深 h (m)', fontsize=12)
        ax3.set_ylabel('Froude数 Fr', fontsize=12)
        ax3.set_title('Froude数变化规律', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([0.2, 3])
        ax3.set_ylim([0, 5])
        
        # 子图4：流速与水深关系
        v_range = []
        for h in h_range:
            A = b * h
            v = Q / A
            v_range.append(v)
        
        ax4.plot(h_range, v_range, 'green', linewidth=2, label='v(h)曲线')
        ax4.axvline(x=hc, color='red', linestyle='--', linewidth=2, label=f'hc={hc:.3f}m')
        ax4.plot(hc, vc, 'ro', markersize=12, label=f'vc={vc:.3f}m/s')
        ax4.plot(h0, v0, 'bs', markersize=12, label=f'v₀={v0:.3f}m/s')
        
        ax4.set_xlabel('水深 h (m)', fontsize=12)
        ax4.set_ylabel('流速 v (m/s)', fontsize=12)
        ax4.set_title('流速变化规律', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim([0.2, 3])
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day11_critical_jump/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 计算单宽流量 q = Q/b (1分)")
        print("✓ (2) 应用公式 hc = (q²/g)^(1/3) (3分) ⭐")
        print("✓ (3) 计算临界流速 vc = Q/(bhc) (2分)")
        print("✓ (4) 验证 vc = √(ghc) (1分)")
        print("✓ (5) 计算Fr₀ = v₀/√(gh₀) (2分)")
        print("✓ (6) 比较h₀与hc，判断流态 (2分) ⭐")
        print("✓ (7) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 临界水深公式：hc = (q²/g)^(1/3)，注意是q²不是Q²")
        print("  ⚠️ 流态判断：h > hc → 缓流；h < hc → 急流")
        print("  ⚠️ 临界流条件：Fr = 1，v = √(gh)")
        
        return {'hc': hc, 'vc': vc, 'Fr0': Fr0, 'flow_type': flow_type}
    
    def example_2_hydraulic_jump(self):
        """
        例题2：水跃共轭水深与消能（强化题）⭐⭐⭐⭐⭐
        
        题目：矩形明渠，宽b=4m，跃前水深h₁=0.5m，流量Q=20m³/s
        求：(1) 跃前Froude数Fr₁
            (2) 跃后水深h₂（共轭水深）
            (3) 水跃损失ΔE
            (4) 相对损失ΔE/E₁
        
        考点：水跃共轭水深公式，水跃消能计算
        难度：强化（必考！）
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题2：水跃共轭水深与消能（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 4.0    # 渠宽 (m)
        h1 = 0.5   # 跃前水深 (m)
        Q = 20.0   # 流量 (m³/s)
        
        print(f"\n已知条件：")
        print(f"  矩形明渠宽度 b = {b:.1f} m")
        print(f"  跃前水深 h₁ = {h1:.1f} m")
        print(f"  流量 Q = {Q:.1f} m³/s")
        
        # 计算
        print(f"\n解题步骤：")
        
        # (1) 计算跃前参数
        A1 = b * h1
        v1 = Q / A1
        Fr1 = v1 / np.sqrt(self.g * h1)
        
        print(f"\n(1) 计算跃前参数：")
        print(f"    A₁ = bh₁ = {b} × {h1} = {A1:.1f} m²")
        print(f"    v₁ = Q/A₁ = {Q}/{A1:.1f} = {v1:.2f} m/s")
        print(f"    Fr₁ = v₁/√(gh₁)")
        print(f"        = {v1:.2f}/√({self.g:.2f}×{h1})")
        print(f"        = {Fr1:.4f} ✓")
        
        if Fr1 > 1:
            print(f"    ∵ Fr₁ > 1，跃前为急流，满足水跃条件 ✓")
        else:
            print(f"    ⚠️ Fr₁ < 1，跃前为缓流，不会发生水跃！")
        
        # (2) 计算共轭水深
        print(f"\n(2) 计算共轭水深（水跃方程）：")
        print(f"    h₂ = (h₁/2) × [-1 + √(1 + 8Fr₁²)]")
        
        h2 = (h1/2) * (-1 + np.sqrt(1 + 8*Fr1**2))
        
        print(f"       = ({h1}/2) × [-1 + √(1 + 8×{Fr1:.4f}²)]")
        print(f"       = {h1/2:.2f} × [-1 + √(1 + {8*Fr1**2:.2f})]")
        print(f"       = {h1/2:.2f} × [-1 + {np.sqrt(1 + 8*Fr1**2):.4f}]")
        print(f"       = {h2:.4f} m ✓")
        
        # 跃后参数
        A2 = b * h2
        v2 = Q / A2
        Fr2 = v2 / np.sqrt(self.g * h2)
        
        print(f"\n(3) 计算跃后参数：")
        print(f"    A₂ = bh₂ = {b} × {h2:.4f} = {A2:.4f} m²")
        print(f"    v₂ = Q/A₂ = {Q}/{A2:.4f} = {v2:.3f} m/s")
        print(f"    Fr₂ = v₂/√(gh₂) = {v2:.3f}/√({self.g:.2f}×{h2:.4f})")
        print(f"        = {Fr2:.4f}")
        print(f"    ∵ Fr₂ < 1 ({Fr2:.4f} < 1)")
        print(f"    ∴ 跃后为缓流 ✓")
        
        # (4) 水跃损失
        E1 = h1 + v1**2/(2*self.g)
        E2 = h2 + v2**2/(2*self.g)
        delta_E = E1 - E2
        delta_E_formula = (h2 - h1)**3 / (4*h1*h2)
        
        print(f"\n(4) 计算水跃损失：")
        print(f"    跃前比能 E₁ = h₁ + v₁²/(2g)")
        print(f"              = {h1} + {v1:.2f}²/(2×{self.g:.2f})")
        print(f"              = {E1:.4f} m")
        print(f"    ")
        print(f"    跃后比能 E₂ = h₂ + v₂²/(2g)")
        print(f"              = {h2:.4f} + {v2:.3f}²/(2×{self.g:.2f})")
        print(f"              = {E2:.4f} m")
        print(f"    ")
        print(f"    水跃损失 ΔE = E₁ - E₂")
        print(f"              = {E1:.4f} - {E2:.4f}")
        print(f"              = {delta_E:.4f} m ✓")
        print(f"    ")
        print(f"    验证公式：ΔE = (h₂ - h₁)³/(4h₁h₂)")
        print(f"              = ({h2:.4f} - {h1})³/(4×{h1}×{h2:.4f})")
        print(f"              = {delta_E_formula:.4f} m")
        print(f"    误差 = |{delta_E:.4f} - {delta_E_formula:.4f}| = {abs(delta_E-delta_E_formula):.6f} m ✓")
        
        # (5) 相对损失
        rel_loss = delta_E / E1 * 100
        
        print(f"\n(5) 相对损失：")
        print(f"    ΔE/E₁ = {delta_E:.4f}/{E1:.4f}")
        print(f"          = {delta_E/E1:.4f}")
        print(f"          = {rel_loss:.2f}% ✓")
        print(f"    ")
        print(f"    消能效率很高！")
        
        # 绘图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 子图1：水跃示意图
        # 跃前段
        x1 = np.linspace(0, 2, 50)
        y1_bottom = np.zeros_like(x1)
        y1_top = np.ones_like(x1) * h1
        
        ax1.fill_between(x1, y1_bottom, y1_top, alpha=0.5, color='lightblue', 
                        edgecolor='blue', linewidth=2)
        
        # 水跃过渡段
        x_jump = np.linspace(2, 3, 30)
        y_jump = h1 + (h2 - h1) * (x_jump - 2)**2  # 二次曲线模拟水跃
        ax1.plot(x_jump, y_jump, 'b-', linewidth=3)
        ax1.fill_between(x_jump, 0, y_jump, alpha=0.5, color='lightgreen')
        
        # 跃后段
        x2 = np.linspace(3, 5, 50)
        y2_top = np.ones_like(x2) * h2
        ax1.fill_between(x2, 0, y2_top, alpha=0.5, color='lightblue', 
                        edgecolor='blue', linewidth=2)
        
        # 标注
        ax1.text(1, h1/2, f'跃前\nh₁={h1}m\nv₁={v1:.2f}m/s\nFr₁={Fr1:.2f}\n(急流)', 
                fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='yellow'))
        ax1.text(4, h2/2, f'跃后\nh₂={h2:.2f}m\nv₂={v2:.2f}m/s\nFr₂={Fr2:.2f}\n(缓流)', 
                fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        # 能量线
        E1_line = np.ones_like(x1) * E1
        E2_line = np.ones_like(x2) * E2
        ax1.plot(x1, E1_line, 'r--', linewidth=2, label=f'E₁={E1:.2f}m')
        ax1.plot(x2, E2_line, 'g--', linewidth=2, label=f'E₂={E2:.2f}m')
        
        # 标注损失
        ax1.annotate('', xy=(4.5, E2), xytext=(4.5, E1),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(4.7, (E1+E2)/2, f'ΔE={delta_E:.2f}m\n({rel_loss:.1f}%)', 
                fontsize=11, color='red', fontweight='bold')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 11 例题2：水跃过程示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 5])
        ax1.set_ylim([0, max(E1, h2)*1.2])
        
        # 子图2：能量分析
        labels = ['跃前E₁', '跃后E₂', '损失ΔE']
        values = [E1, E2, delta_E]
        colors = ['#FF6B6B', '#4ECDC4', '#FFA07A']
        
        bars = ax2.bar(labels, values, color=colors, edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.3f}m', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 百分比标注
        ax2.text(2, delta_E/2, f'{rel_loss:.1f}%\n消能', ha='center', fontsize=14, 
                color='white', fontweight='bold')
        
        ax2.set_ylabel('能量 (m)', fontsize=12)
        ax2.set_title('水跃能量分析', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 添加公式
        formula_text = (
            "共轭水深公式：\n"
            f"h₂ = (h₁/2)[-1 + √(1 + 8Fr₁²)]\n"
            f"   = {h2:.3f} m\n\n"
            "水跃损失公式：\n"
            f"ΔE = (h₂-h₁)³/(4h₁h₂)\n"
            f"   = {delta_E:.3f} m"
        )
        ax2.text(0.5, max(values)*0.7, formula_text, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
                verticalalignment='top')
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day11_critical_jump/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 计算跃前流速和Fr₁ (2分)")
        print("✓ (2) 判断Fr₁>1，满足水跃条件 (1分)")
        print("✓ (3) 应用共轭水深公式 h₂=(h₁/2)[-1+√(1+8Fr₁²)] (5分) ⭐⭐⭐")
        print("✓ (4) 计算E₁和E₂ (2分)")
        print("✓ (5) 计算ΔE = E₁ - E₂ (2分)")
        print("✓ (6) 计算相对损失ΔE/E₁ (2分)")
        print("✓ (7) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 共轭水深公式要背熟！这是必考公式！")
        print("  ⚠️ 注意是[-1 + √...]，不是[1 + √...]")
        print("  ⚠️ Fr₁必须>1才能发生水跃")
        print("  ⚠️ 水跃是能量损失，ΔE>0")
        
        return {'h2': h2, 'delta_E': delta_E, 'Fr1': Fr1, 'rel_loss': rel_loss}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 11 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 临界水深（矩形断面）：")
        print("     hc = (q²/g)^(1/3) = (Q²/(gb²))^(1/3)")
        print("     ")
        print("  2. 临界流条件：")
        print("     Fr = 1,  v = √(gh),  E = Emin")
        print("     ")
        print("  3. 水跃共轭水深（必考！）：")
        print("     h₂ = (h₁/2) × [-1 + √(1 + 8Fr₁²)]")
        print("     ")
        print("  4. 水跃损失：")
        print("     ΔE = E₁ - E₂ = (h₂ - h₁)³/(4h₁h₂)")
        print("     ")
        print("  5. 流态判断：")
        print("     h > hc: 缓流（Fr<1）")
        print("     h < hc: 急流（Fr>1）")
        print("     h = hc: 临界流（Fr=1）")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【临界水深题】")
        print("  Step 1: 计算单宽流量q = Q/b")
        print("  Step 2: 应用公式hc = (q²/g)^(1/3)")
        print("  Step 3: 计算临界流速vc = √(ghc)")
        print("  Step 4: 判断流态（比较h与hc）")
        print("  ")
        print("  【水跃题】")
        print("  Step 1: 计算跃前Fr₁，判断Fr₁>1")
        print("  Step 2: 应用公式h₂ = (h₁/2)[-1+√(1+8Fr₁²)]")
        print("  Step 3: 计算E₁和E₂")
        print("  Step 4: 计算ΔE = E₁ - E₂")
        print("  Step 5: 验算或计算相对损失")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：临界水深用Q²代替q²")
        print("  ❌ 错误2：共轭水深公式记成[1+√...]")
        print("  ❌ 错误3：忘记判断Fr₁>1的水跃条件")
        print("  ❌ 错误4：水跃损失算成E₂-E₁（应该是E₁-E₂）")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：共轭水深公式必须背熟！")
        print("  ✓ 技巧2：水跃题一定要画示意图")
        print("  ✓ 技巧3：注意判断Fr₁>1才有水跃")
        print("  ✓ 技巧4：损失公式可以验算")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能默写临界水深公式")
        print("  □ 能默写共轭水深公式（重要！）")
        print("  □ 能独立计算水跃消能")
        print("  □ 理解临界流、缓流、急流的区别")
        
        print("\n📅 明日预告：Day 12 - 明渠非均匀流")
        print("  预习内容：水面线分类（12种）、水面线计算")
        
        print("\n💪 今日格言：")
        print("  「水跃共轭水深公式=考研15分！一定要背熟！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 11: 临界水深与水跃")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day11 = Day11CriticalJump()
    
    # 例题1：临界水深
    result1 = day11.example_1_critical_depth()
    
    # 例题2：水跃
    result2 = day11.example_2_hydraulic_jump()
    
    # 每日总结
    day11.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 11 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握临界水深公式")
    print(f"  ✓ 掌握共轭水深公式（必考！）")
    print(f"  ✓ 理解水跃消能原理")
    print(f"  ✓ 生成2张图表")
    
    print(f"\n明日继续：Day 12 - 明渠非均匀流")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
