#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 20: 环境水力学
Sprint Day 20: Environmental Hydraulics

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 污染物扩散：点源扩散、纵向扩散
  2. 河流自净：BOD-DO模型、Streeter-Phelps方程
  3. 扩散系数：纵向、横向、垂向
  4. 污染负荷：污染物通量、浓度分布
  5. 自净能力：复氧系数、降解系数

🎯 学习目标：
  - 掌握污染物扩散规律
  - 理解河流自净机理
  - 熟练BOD-DO计算
  - 了解水质模型应用

💪 今日格言：环境水力学是热点！掌握污染扩散=拿到14分！
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

class Day20Environmental:
    """
    Day 20：环境水力学
    
    包含2个核心例题：
    1. 基础题：点源污染物扩散
    2. 强化题：河流BOD-DO模型
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        
    def example_1_pollutant_dispersion(self):
        """
        例题1：点源污染物扩散（基础题）⭐⭐⭐⭐⭐
        
        题目：某河流平均流速u=0.5m/s，纵向扩散系数Ex=20m²/s
              某排污口持续排放污染物，排放速率M=10g/s
              河流断面面积A=30m²，背景浓度C0=0
        求：(1) 排污口下游x=1000m处的稳态浓度C
            (2) 浓度降至排放口浓度10%的距离x10
            (3) 若要求浓度不超过2mg/L，计算最小允许距离xmin
        
        考点：点源扩散，纵向扩散系数，浓度分布
        难度：基础（必考！）
        时间：18分钟
        分值：14分
        """
        print("\n" + "="*60)
        print("例题1：点源污染物扩散（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        u = 0.5       # 平均流速 (m/s)
        Ex = 20.0     # 纵向扩散系数 (m²/s)
        M = 10.0      # 排放速率 (g/s)
        A = 30.0      # 断面面积 (m²)
        C0 = 0.0      # 背景浓度 (mg/L)
        x1 = 1000.0   # 计算距离 (m)
        C_limit = 2.0 # 浓度限值 (mg/L)
        
        print(f"\n已知条件：")
        print(f"  平均流速 u = {u} m/s")
        print(f"  纵向扩散系数 Ex = {Ex} m²/s")
        print(f"  排放速率 M = {M} g/s")
        print(f"  断面面积 A = {A} m²")
        print(f"  背景浓度 C₀ = {C0} mg/L")
        print(f"  计算距离 x = {x1} m")
        print(f"  浓度限值 = {C_limit} mg/L")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 下游浓度
        print(f"\n(1) 排污口下游x={x1}m处浓度：")
        print(f"    ")
        print(f"    点源连续排放稳态浓度公式：")
        print(f"    C(x) = (M/Q) × exp(-ux/(2Ex))")
        print(f"    ")
        print(f"    其中Q为河流流量：")
        
        Q = u * A
        
        print(f"    Q = u × A = {u} × {A}")
        print(f"      = {Q} m³/s")
        print(f"    ")
        print(f"    排放口处浓度（x=0⁺）：")
        
        C_source = (M / Q) * 1000  # 转换为mg/L
        
        print(f"    C(0⁺) = M/Q")
        print(f"          = {M} / {Q}")
        print(f"          = {M/Q:.4f} g/m³")
        print(f"          = {C_source:.2f} mg/L ✓")
        print(f"    ")
        print(f"    下游x={x1}m处浓度：")
        print(f"    ")
        print(f"    指数项：")
        
        exponent = -u * x1 / (2 * Ex)
        
        print(f"    -ux/(2Ex) = -{u}×{x1}/(2×{Ex})")
        print(f"              = {exponent:.4f}")
        print(f"    ")
        print(f"    C({x1}) = C(0⁺) × exp({exponent:.4f})")
        
        C_x1 = C_source * np.exp(exponent)
        
        print(f"            = {C_source:.2f} × {np.exp(exponent):.4f}")
        print(f"            = {C_x1:.3f} mg/L ✓")
        
        # (2) 降至10%的距离
        print(f"\n(2) 浓度降至排放口10%的距离：")
        print(f"    ")
        print(f"    目标浓度：")
        
        C_target = 0.1 * C_source
        
        print(f"    C_target = 0.1 × C(0⁺)")
        print(f"             = 0.1 × {C_source:.2f}")
        print(f"             = {C_target:.2f} mg/L")
        print(f"    ")
        print(f"    从浓度公式：")
        print(f"    C(x)/C(0⁺) = exp(-ux/(2Ex)) = 0.1")
        print(f"    ")
        print(f"    取对数：")
        print(f"    -ux/(2Ex) = ln(0.1) = {np.log(0.1):.4f}")
        print(f"    ")
        print(f"    解出x₁₀：")
        
        x10 = -2 * Ex * np.log(0.1) / u
        
        print(f"    x₁₀ = -2Ex×ln(0.1)/u")
        print(f"        = -2×{Ex}×{np.log(0.1):.4f}/{u}")
        print(f"        = {x10:.2f} m ✓")
        print(f"    ")
        print(f"    物理意义：下游{x10:.0f}m处浓度降至排放口的10%")
        
        # (3) 满足限值的最小距离
        print(f"\n(3) 浓度不超过{C_limit}mg/L的最小距离：")
        print(f"    ")
        print(f"    要求：C(xmin) ≤ {C_limit} mg/L")
        print(f"    ")
        print(f"    从公式：")
        print(f"    C(xmin) = C(0⁺) × exp(-u×xmin/(2Ex)) = {C_limit}")
        print(f"    ")
        print(f"    浓度比：")
        
        ratio = C_limit / C_source
        
        print(f"    C(xmin)/C(0⁺) = {C_limit}/{C_source:.2f}")
        print(f"                  = {ratio:.4f}")
        print(f"    ")
        print(f"    取对数：")
        print(f"    -u×xmin/(2Ex) = ln({ratio:.4f})")
        print(f"                  = {np.log(ratio):.4f}")
        print(f"    ")
        print(f"    解出xmin：")
        
        xmin = -2 * Ex * np.log(ratio) / u
        
        print(f"    xmin = -2Ex×ln({ratio:.4f})/u")
        print(f"         = -2×{Ex}×{np.log(ratio):.4f}/{u}")
        print(f"         = {xmin:.2f} m ✓")
        print(f"    ")
        print(f"    结论：排污口下游至少{xmin:.0f}m处，浓度才降至{C_limit}mg/L")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：污染物扩散示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 河流
        river_y = [0, 0]
        river_x = [0, 3000]
        ax1.fill_between(river_x, [-1, -1], [1, 1], color='lightblue', alpha=0.3)
        ax1.plot(river_x, [0, 0], 'b-', linewidth=2, label='河流中心线')
        
        # 排污口
        ax1.plot([0], [0], 'r*', markersize=20, label='排污口')
        ax1.arrow(0, -0.8, 0, 0.6, head_width=50, head_length=0.1,
                 fc='red', ec='red', linewidth=3)
        ax1.text(0, -1.2, f'M={M}g/s', fontsize=10, ha='center',
                color='red', fontweight='bold')
        
        # 流向
        for x in [500, 1500, 2500]:
            ax1.arrow(x, 0, 200, 0, head_width=0.15, head_length=80,
                     fc='blue', ec='blue', linewidth=2, alpha=0.6)
        
        ax1.text(1500, 0.5, f'u={u}m/s', fontsize=11, ha='center',
                color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 标注关键距离
        ax1.plot([x1], [0], 'go', markersize=10)
        ax1.text(x1, -0.4, f'x={x1}m\nC={C_x1:.2f}mg/L',
                fontsize=9, ha='center', color='green',
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        ax1.plot([xmin], [0], 'mo', markersize=10)
        ax1.text(xmin, 0.6, f'xmin={xmin:.0f}m\nC={C_limit}mg/L',
                fontsize=9, ha='center', color='magenta',
                bbox=dict(boxstyle='round', facecolor='pink'))
        
        ax1.set_xlabel('纵向距离 x (m)', fontsize=12)
        ax1.set_ylabel('横向距离 y (m)', fontsize=12)
        ax1.set_title('Day 20 例题1：点源污染物扩散示意图', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-200, 3200])
        ax1.set_ylim([-1.5, 1.5])
        
        # 子图2：浓度分布曲线
        ax2 = plt.subplot(2, 2, 2)
        
        x_range = np.linspace(0.1, 5000, 500)
        C_range = C_source * np.exp(-u * x_range / (2 * Ex))
        
        ax2.plot(x_range, C_range, 'b-', linewidth=2.5, label='浓度分布C(x)')
        ax2.plot([x1], [C_x1], 'go', markersize=12,
                label=f'x={x1}m: C={C_x1:.2f}mg/L')
        ax2.plot([x10], [C_target], 'ro', markersize=12,
                label=f'x={x10:.0f}m: C={C_target:.2f}mg/L (10%)')
        ax2.plot([xmin], [C_limit], 'mo', markersize=12,
                label=f'xmin={xmin:.0f}m: C={C_limit}mg/L')
        
        # 浓度限值线
        ax2.axhline(y=C_limit, color='magenta', linestyle='--', linewidth=2,
                   label=f'浓度限值={C_limit}mg/L')
        
        ax2.set_xlabel('距离 x (m)', fontsize=12)
        ax2.set_ylabel('浓度 C (mg/L)', fontsize=12)
        ax2.set_title('纵向浓度分布', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 5000])
        
        # 子图3：对数坐标浓度分布
        ax3 = plt.subplot(2, 2, 3)
        
        ax3.semilogy(x_range, C_range, 'b-', linewidth=2.5, label='浓度分布(对数)')
        ax3.semilogy([x1], [C_x1], 'go', markersize=12)
        ax3.semilogy([x10], [C_target], 'ro', markersize=12)
        ax3.semilogy([xmin], [C_limit], 'mo', markersize=12)
        ax3.axhline(y=C_limit, color='magenta', linestyle='--', linewidth=2)
        
        ax3.set_xlabel('距离 x (m)', fontsize=12)
        ax3.set_ylabel('浓度 C (mg/L, 对数)', fontsize=12)
        ax3.set_title('浓度分布（对数坐标）', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, which='both')
        ax3.set_xlim([0, 5000])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          流速：u = {u} m/s
          扩散系数：Ex = {Ex} m²/s
          排放速率：M = {M} g/s
          断面积：A = {A} m²
          流量：Q = {Q} m³/s
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 排放口浓度：
            C(0⁺) = M/Q
                  = {C_source:.2f} mg/L ✓
        
        (2) 下游x={x1}m处：
            指数：{exponent:.4f}
            C({x1}) = {C_x1:.3f} mg/L ✓
        
        (3) 降至10%距离：
            x₁₀ = -2Ex×ln(0.1)/u
                = {x10:.2f} m ✓
        
        (4) 满足限值距离：
            要求：C ≤ {C_limit} mg/L
            xmin = {xmin:.2f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 浓度：C(x)=(M/Q)×exp(-ux/(2Ex))
          • 距离：x=-2Ex×ln(C/C₀)/u
          • 衰减：指数衰减规律
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day20_environmental/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（14分评分标准）：")
        print("="*60)
        print("✓ (1) 写出点源扩散公式 (2分) ⭐")
        print("✓ (2) 计算流量Q (1分)")
        print("✓ (3) 计算排放口浓度 (2分) ⭐")
        print("✓ (4) 计算下游浓度C(x) (3分) ⭐⭐")
        print("✓ (5) 写出距离反算公式 (2分) ⭐")
        print("✓ (6) 计算x₁₀ (2分)")
        print("✓ (7) 计算xmin (2分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 点源公式：C=(M/Q)×exp(-ux/(2Ex))，注意2Ex")
        print("  ⚠️ 单位转换：M(g/s)→C(mg/L)，注意×1000")
        print("  ⚠️ 距离公式：x=-2Ex×ln(C/C₀)/u，负号不要丢")
        print("  ⚠️ 排放口：x=0⁺，浓度C(0⁺)=M/Q")
        
        return {'C_source': C_source, 'C_x1': C_x1, 'x10': x10, 'xmin': xmin}
    
    def example_2_bod_do_model(self):
        """
        例题2：河流BOD-DO模型（强化题）⭐⭐⭐⭐⭐
        
        题目：某河流接纳污水后，初始溶解氧DO0=6.0mg/L
              初始生化需氧量BOD0=15.0mg/L，饱和溶解氧DOs=9.0mg/L
              脱氧系数k1=0.2/d，复氧系数k2=0.3/d
              河流流速u=0.4m/s
        求：(1) 临界点位置xc和临界溶解氧DOc
            (2) 下游x=10km处的DO和BOD
            (3) 溶解氧赤字最大值Dmax
        
        考点：Streeter-Phelps方程，BOD-DO模型，河流自净
        难度：强化（必考！）
        时间：25分钟
        分值：18分
        """
        print("\n" + "="*60)
        print("例题2：河流BOD-DO模型（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        DO0 = 6.0     # 初始溶解氧 (mg/L)
        BOD0 = 15.0   # 初始BOD (mg/L)
        DOs = 9.0     # 饱和溶解氧 (mg/L)
        k1 = 0.2      # 脱氧系数 (/d)
        k2 = 0.3      # 复氧系数 (/d)
        u = 0.4       # 流速 (m/s)
        x_calc = 10000  # 计算点距离 (m)
        
        print(f"\n已知条件：")
        print(f"  初始溶解氧 DO₀ = {DO0} mg/L")
        print(f"  初始BOD BOD₀ = {BOD0} mg/L")
        print(f"  饱和溶解氧 DOs = {DOs} mg/L")
        print(f"  脱氧系数 k₁ = {k1} /d")
        print(f"  复氧系数 k₂ = {k2} /d")
        print(f"  流速 u = {u} m/s")
        print(f"  计算点 x = {x_calc} m = {x_calc/1000} km")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # 初始溶解氧赤字
        D0 = DOs - DO0
        
        print(f"\n前置计算：")
        print(f"  初始溶解氧赤字：")
        print(f"  D₀ = DOs - DO₀ = {DOs} - {DO0}")
        print(f"     = {D0} mg/L")
        
        # (1) 临界点
        print(f"\n(1) 临界点位置xc和临界溶解氧DOc：")
        print(f"    ")
        print(f"    Streeter-Phelps方程：")
        print(f"    D(t) = (k₁×BOD₀)/(k₂-k₁) × [exp(-k₁t) - exp(-k₂t)]")
        print(f"           + D₀×exp(-k₂t)")
        print(f"    ")
        print(f"    临界点：dD/dt = 0")
        print(f"    临界时间：")
        print(f"    tc = ln[(k₂/k₁)×(1-D₀×(k₂-k₁)/(k₁×BOD₀))]/(k₂-k₁)")
        print(f"    ")
        print(f"    计算中间量：")
        
        ratio = D0 * (k2 - k1) / (k1 * BOD0)
        
        print(f"    D₀×(k₂-k₁)/(k₁×BOD₀) = {D0}×({k2}-{k1})/({k1}×{BOD0})")
        print(f"                          = {ratio:.4f}")
        print(f"    ")
        print(f"    ln项参数：")
        
        ln_param = (k2/k1) * (1 - ratio)
        
        print(f"    (k₂/k₁)×(1-{ratio:.4f}) = ({k2}/{k1})×{1-ratio:.4f}")
        print(f"                             = {ln_param:.4f}")
        print(f"    ")
        print(f"    临界时间：")
        
        tc = np.log(ln_param) / (k2 - k1)
        
        print(f"    tc = ln({ln_param:.4f})/(k₂-k₁)")
        print(f"       = {np.log(ln_param):.4f}/({k2}-{k1})")
        print(f"       = {tc:.3f} d ✓")
        print(f"    ")
        print(f"    临界位置：")
        
        xc = u * tc * 86400  # 转换为米
        
        print(f"    xc = u×tc = {u}×{tc:.3f}×86400")
        print(f"       = {xc:.2f} m")
        print(f"       = {xc/1000:.2f} km ✓")
        print(f"    ")
        print(f"    临界溶解氧赤字：")
        
        Dc = (k1 * BOD0 / (k2 - k1)) * (np.exp(-k1 * tc) - np.exp(-k2 * tc)) + D0 * np.exp(-k2 * tc)
        
        print(f"    Dc = (k₁×BOD₀)/(k₂-k₁) × [exp(-k₁tc) - exp(-k₂tc)]")
        print(f"         + D₀×exp(-k₂tc)")
        print(f"       = ({k1}×{BOD0})/({k2}-{k1}) × [exp(-{k1}×{tc:.3f}) - exp(-{k2}×{tc:.3f})]")
        print(f"         + {D0}×exp(-{k2}×{tc:.3f})")
        print(f"       = {Dc:.3f} mg/L ✓")
        print(f"    ")
        print(f"    临界溶解氧：")
        
        DOc = DOs - Dc
        
        print(f"    DOc = DOs - Dc = {DOs} - {Dc:.3f}")
        print(f"        = {DOc:.3f} mg/L ✓")
        print(f"    ")
        print(f"    物理意义：下游{xc/1000:.2f}km处溶解氧最低，为{DOc:.2f}mg/L")
        
        # (2) 下游x=10km处
        print(f"\n(2) 下游x={x_calc/1000}km处的DO和BOD：")
        print(f"    ")
        print(f"    时间计算：")
        
        t_calc = x_calc / (u * 86400)
        
        print(f"    t = x/u = {x_calc}/{u}/86400")
        print(f"      = {t_calc:.3f} d")
        print(f"    ")
        print(f"    BOD衰减：")
        print(f"    BOD(t) = BOD₀ × exp(-k₁t)")
        
        BOD_calc = BOD0 * np.exp(-k1 * t_calc)
        
        print(f"           = {BOD0} × exp(-{k1}×{t_calc:.3f})")
        print(f"           = {BOD0} × {np.exp(-k1*t_calc):.4f}")
        print(f"           = {BOD_calc:.3f} mg/L ✓")
        print(f"    ")
        print(f"    溶解氧赤字：")
        
        D_calc = (k1 * BOD0 / (k2 - k1)) * (np.exp(-k1 * t_calc) - np.exp(-k2 * t_calc)) + D0 * np.exp(-k2 * t_calc)
        
        print(f"    D(t) = (k₁×BOD₀)/(k₂-k₁) × [exp(-k₁t) - exp(-k₂t)]")
        print(f"           + D₀×exp(-k₂t)")
        print(f"         = {D_calc:.3f} mg/L")
        print(f"    ")
        print(f"    溶解氧：")
        
        DO_calc = DOs - D_calc
        
        print(f"    DO(t) = DOs - D(t)")
        print(f"          = {DOs} - {D_calc:.3f}")
        print(f"          = {DO_calc:.3f} mg/L ✓")
        
        # (3) 最大赤字
        print(f"\n(3) 溶解氧赤字最大值：")
        print(f"    ")
        print(f"    最大赤字即临界赤字：")
        
        Dmax = Dc
        
        print(f"    Dmax = Dc = {Dmax:.3f} mg/L ✓")
        print(f"    ")
        print(f"    对应最小溶解氧：")
        
        DOmin = DOc
        
        print(f"    DOmin = DOc = {DOmin:.3f} mg/L ✓")
        print(f"    ")
        print(f"    判断水质：")
        
        if DOmin >= 5.0:
            print(f"    DOmin ({DOmin:.2f}) ≥ 5.0 mg/L")
            print(f"    水质良好，鱼类可生存 ✓")
            status = "良好"
        elif DOmin >= 3.0:
            print(f"    3.0 ≤ DOmin ({DOmin:.2f}) < 5.0 mg/L")
            print(f"    水质一般，部分鱼类可生存")
            status = "一般"
        else:
            print(f"    DOmin ({DOmin:.2f}) < 3.0 mg/L")
            print(f"    水质较差，鱼类难以生存")
            status = "较差"
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：河流BOD-DO示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 河流
        ax1.fill_between([0, 50], [-0.5, -0.5], [0.5, 0.5], color='lightblue', alpha=0.3)
        ax1.plot([0, 50], [0, 0], 'b-', linewidth=2)
        
        # 排污口
        ax1.plot([0], [0], 'r*', markersize=20, label='排污口')
        ax1.arrow(0, -0.3, 0, 0.2, head_width=1, head_length=0.05,
                 fc='red', ec='red', linewidth=2)
        
        # 临界点
        xc_plot = xc / 1000  # 转为km
        ax1.plot([xc_plot], [0], 'mo', markersize=12, label=f'临界点(xc={xc_plot:.1f}km)')
        
        # 流向
        for x in [10, 25, 40]:
            ax1.arrow(x, 0, 3, 0, head_width=0.08, head_length=1.5,
                     fc='blue', ec='blue', linewidth=2, alpha=0.6)
        
        ax1.set_xlabel('距离 (km)', fontsize=12)
        ax1.set_ylabel('横向 (km)', fontsize=12)
        ax1.set_title('Day 20 例题2：河流BOD-DO示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-2, 52])
        ax1.set_ylim([-0.6, 0.6])
        
        # 子图2：BOD-DO曲线
        ax2 = plt.subplot(2, 2, 2)
        
        x_range_km = np.linspace(0, 50, 500)
        t_range = x_range_km * 1000 / (u * 86400)
        
        BOD_range = BOD0 * np.exp(-k1 * t_range)
        D_range = (k1 * BOD0 / (k2 - k1)) * (np.exp(-k1 * t_range) - np.exp(-k2 * t_range)) + D0 * np.exp(-k2 * t_range)
        DO_range = DOs - D_range
        
        ax2.plot(x_range_km, BOD_range, 'r-', linewidth=2.5, label='BOD(t)')
        ax2.plot(x_range_km, DO_range, 'b-', linewidth=2.5, label='DO(t)')
        ax2.axhline(y=DOs, color='green', linestyle='--', linewidth=2,
                   label=f'饱和DO={DOs}mg/L')
        
        # 临界点标注
        ax2.plot([xc_plot], [DOc], 'mo', markersize=12,
                label=f'临界点: DOmin={DOc:.2f}mg/L')
        
        # 安全线
        ax2.axhline(y=5.0, color='orange', linestyle='--', linewidth=1.5,
                   label='DO安全线(5mg/L)')
        
        ax2.set_xlabel('距离 (km)', fontsize=12)
        ax2.set_ylabel('浓度 (mg/L)', fontsize=12)
        ax2.set_title('BOD与DO沿程变化', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 50])
        
        # 子图3：溶解氧赤字曲线
        ax3 = plt.subplot(2, 2, 3)
        
        ax3.plot(x_range_km, D_range, 'r-', linewidth=2.5, label='溶解氧赤字D(t)')
        ax3.plot([xc_plot], [Dc], 'mo', markersize=12,
                label=f'最大赤字: Dmax={Dc:.2f}mg/L')
        ax3.axhline(y=D0, color='blue', linestyle='--', linewidth=2,
                   label=f'初始赤字D₀={D0}mg/L')
        
        ax3.set_xlabel('距离 (km)', fontsize=12)
        ax3.set_ylabel('溶解氧赤字 D (mg/L)', fontsize=12)
        ax3.set_title('溶解氧赤字曲线', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([0, 50])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          DO₀={DO0}mg/L, BOD₀={BOD0}mg/L
          DOs={DOs}mg/L
          k₁={k1}/d, k₂={k2}/d
          u={u}m/s
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 临界点：
            tc = {tc:.3f} d
            xc = {xc/1000:.2f} km ✓
            Dc = {Dc:.3f} mg/L
            DOc = {DOc:.3f} mg/L ✓
        
        (2) 下游x={x_calc/1000}km：
            t = {t_calc:.3f} d
            BOD = {BOD_calc:.3f} mg/L ✓
            DO = {DO_calc:.3f} mg/L ✓
        
        (3) 最大赤字：
            Dmax = {Dmax:.3f} mg/L ✓
            DOmin = {DOmin:.3f} mg/L ✓
            水质：{status}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式（Streeter-Phelps）：
          • BOD: BOD(t)=BOD₀×exp(-k₁t)
          • D(t): 脱氧-复氧平衡
          • DO: DO(t)=DOs-D(t)
          • tc: ln[(k₂/k₁)×(...)]/(k₂-k₁)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=7.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day20_environmental/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（18分评分标准）：")
        print("="*60)
        print("✓ (1) 写出Streeter-Phelps方程 (2分) ⭐")
        print("✓ (2) 计算初始赤字D₀ (1分)")
        print("✓ (3) 写出临界时间公式 (2分) ⭐")
        print("✓ (4) 计算tc和xc (3分) ⭐⭐")
        print("✓ (5) 计算临界DO (2分)")
        print("✓ (6) 写出BOD衰减公式 (1分)")
        print("✓ (7) 计算下游BOD和DO (3分) ⭐⭐")
        print("✓ (8) 求最大赤字Dmax (2分)")
        print("✓ (9) 水质判断 (2分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 赤字定义：D=DOs-DO，不要搞反")
        print("  ⚠️ S-P方程：D(t)包含两项，脱氧项+初始赤字项")
        print("  ⚠️ 临界时间：tc公式复杂，注意ln项参数")
        print("  ⚠️ 单位：时间(d)，距离(km)，浓度(mg/L)")
        
        return {'tc': tc, 'xc': xc/1000, 'DOc': DOc, 'Dc': Dc,
                'BOD_calc': BOD_calc, 'DO_calc': DO_calc, 'status': status}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 20 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 点源污染物扩散：")
        print("     C(x) = (M/Q) × exp(-ux/(2Ex))")
        print("     M - 排放速率")
        print("     Q - 河流流量")
        print("     Ex - 纵向扩散系数")
        print("     ")
        print("  2. 距离反算：")
        print("     x = -2Ex × ln(C/C₀) / u")
        print("     （已知浓度求距离）")
        print("     ")
        print("  3. BOD衰减：")
        print("     BOD(t) = BOD₀ × exp(-k₁t)")
        print("     k₁ - 脱氧系数(/d)")
        print("     ")
        print("  4. Streeter-Phelps方程：")
        print("     D(t) = (k₁BOD₀)/(k₂-k₁) × [e^(-k₁t) - e^(-k₂t)]")
        print("            + D₀ × e^(-k₂t)")
        print("     D - 溶解氧赤字 = DOs - DO")
        print("     ")
        print("  5. 临界时间：")
        print("     tc = ln[(k₂/k₁)(1-D₀(k₂-k₁)/(k₁BOD₀))]/(k₂-k₁)")
        print("     （溶解氧最低点时间）")
        
        print("\n✅ 扩散系数典型值：")
        print("  ┌────────────┬──────────────────┐")
        print("  │ 方向       │ 扩散系数范围     │")
        print("  ├────────────┼──────────────────┤")
        print("  │ 纵向Ex     │ 10-100 m²/s      │")
        print("  │ 横向Ey     │ 0.1-1 m²/s       │")
        print("  │ 垂向Ez     │ 0.001-0.01 m²/s  │")
        print("  └────────────┴──────────────────┘")
        
        print("\n✅ 水质标准：")
        print("  ┌────────────┬──────────┬──────────┐")
        print("  │ DO (mg/L)  │ 水质等级 │ 鱼类生存 │")
        print("  ├────────────┼──────────┼──────────┤")
        print("  │ ≥ 7.5      │ I类      │ 优良     │")
        print("  │ 6-7.5      │ II类     │ 良好     │")
        print("  │ 5-6        │ III类    │ 一般     │")
        print("  │ 3-5        │ IV类     │ 较差     │")
        print("  │ < 3        │ V类      │ 很差     │")
        print("  └────────────┴──────────┴──────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【污染物扩散题】")
        print("  Step 1: 计算流量Q=u×A")
        print("  Step 2: 计算排放口浓度C₀=M/Q")
        print("  Step 3: 用公式C(x)=C₀×exp(-ux/(2Ex))")
        print("  Step 4: 或反算x=-2Ex×ln(C/C₀)/u")
        print("  ")
        print("  【BOD-DO模型题】")
        print("  Step 1: 计算初始赤字D₀=DOs-DO₀")
        print("  Step 2: 计算临界时间tc")
        print("  Step 3: 计算临界赤字Dc")
        print("  Step 4: 计算临界DO=DOs-Dc")
        print("  Step 5: 任意点BOD、DO计算")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：点源公式漏掉2（应是2Ex）")
        print("  ❌ 错误2：赤字定义搞反（D=DOs-DO）")
        print("  ❌ 错误3：S-P方程只写一项（应有两项）")
        print("  ❌ 错误4：临界时间公式记错")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：污染扩散→指数衰减规律")
        print("  ✓ 技巧2：BOD-DO→临界点是关键")
        print("  ✓ 技巧3：单位换算→时间(d)，距离(km)")
        print("  ✓ 技巧4：水质判断→DO≥5mg/L为良好")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能准确计算污染物浓度")
        print("  □ 掌握BOD-DO模型")
        print("  □ 理解临界点计算")
        print("  □ 熟练水质判断")
        
        print("\n📅 明日预告：Day 21 - 第三周测试")
        print("  • 综合测试")
        print("  • Day 11-20复习")
        print("  • 查漏补缺")
        
        print("\n💪 今日格言：")
        print("  「环境水力学是热点！掌握污染扩散=拿到14分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 20: 环境水力学")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day20 = Day20Environmental()
    
    # 例题1：污染物扩散
    result1 = day20.example_1_pollutant_dispersion()
    
    # 例题2：BOD-DO模型
    result2 = day20.example_2_bod_do_model()
    
    # 每日总结
    day20.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 20 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握污染扩散")
    print(f"  ✓ 掌握BOD-DO模型")
    print(f"  ✓ 理解河流自净")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n下一步：Day 21 - 第三周测试 → 70%里程碑！")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
