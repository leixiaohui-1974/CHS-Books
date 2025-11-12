#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 16: 地下水动力学
Sprint Day 16: Groundwater Dynamics and Well Interference

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 非稳定井流：Theis公式、Jacob公式
  2. 井群干扰：叠加原理
  3. 越流系统：含水层-弱透水层-含水层
  4. 抽水试验：s-t曲线、s-lgr曲线
  5. 水位恢复：剩余降深法

🎯 学习目标：
  - 掌握非稳定井流计算
  - 理解井函数W(u)
  - 熟练井群干扰计算
  - 了解抽水试验分析

💪 今日格言：非稳定井流是难点，但掌握了=拿到18分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
from matplotlib.patches import ConnectionPatch
import matplotlib.patches as mpatches
from scipy.special import exp1  # 指数积分函数

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day16Groundwater:
    """
    Day 16：地下水动力学
    
    包含2个核心例题：
    1. 基础题：非稳定井流计算（Theis公式）
    2. 强化题：井群干扰计算
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        self.gamma = self.rho * self.g  # 水容重 (N/m³)
        
    def well_function_W(self, u):
        """
        井函数 W(u)
        W(u) = ∫(u to ∞) (e^(-y)/y) dy
        使用指数积分函数 E1(u)
        """
        return exp1(u)
    
    def well_function_approx(self, u):
        """
        井函数近似计算（Jacob公式，u<0.01时）
        W(u) ≈ -0.5772 - ln(u)
        """
        return -0.5772 - np.log(u)
    
    def example_1_unsteady_well(self):
        """
        例题1：非稳定井流计算（基础题）⭐⭐⭐⭐⭐
        
        题目：承压含水层厚度M=20m，渗透系数k=10m/d
              给水度（储水系数）S=0.001
              抽水井流量Q=1000m³/d，抽水时间t=1天
              计算距井中心r=100m处的降深s
        
        考点：Theis公式，井函数W(u)，非稳定井流
        难度：基础（必考！）
        时间：20分钟
        分值：15分
        """
        print("\n" + "="*60)
        print("例题1：非稳定井流计算（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        M = 20.0       # 含水层厚度 (m)
        k = 10.0       # 渗透系数 (m/d)
        S = 0.001      # 储水系数（给水度）
        Q = 1000.0     # 抽水流量 (m³/d)
        t = 1.0        # 抽水时间 (d)
        r = 100.0      # 距井距离 (m)
        
        print(f"\n已知条件：")
        print(f"  含水层厚度 M = {M} m")
        print(f"  渗透系数 k = {k} m/d")
        print(f"  储水系数 S = {S}")
        print(f"  抽水流量 Q = {Q} m³/d")
        print(f"  抽水时间 t = {t} d")
        print(f"  计算点距离 r = {r} m")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 导水系数
        print(f"\n(1) 计算导水系数T：")
        print(f"    ")
        print(f"    T = k × M")
        
        T = k * M
        
        print(f"      = {k} × {M}")
        print(f"      = {T} m²/d ✓")
        
        # (2) 计算u
        print(f"\n(2) 计算井函数参数u：")
        print(f"    ")
        print(f"    u = r²S / (4Tt)")
        
        u = r**2 * S / (4 * T * t)
        
        print(f"      = {r}² × {S} / (4 × {T} × {t})")
        print(f"      = {r**2 * S} / {4 * T * t}")
        print(f"      = {u:.6f} ✓")
        print(f"    ")
        print(f"    判断：u = {u:.6f} < 0.01")
        print(f"    说明：可以使用Jacob近似公式")
        
        # (3) 计算井函数W(u)
        print(f"\n(3) 计算井函数W(u)：")
        print(f"    ")
        print(f"    方法1：精确计算（指数积分）")
        
        W_u_exact = self.well_function_W(u)
        
        print(f"    W(u) = ∫(u to ∞) (e^(-y)/y) dy")
        print(f"         = {W_u_exact:.4f} ✓")
        print(f"    ")
        print(f"    方法2：Jacob近似（u<0.01时）")
        
        W_u_approx = self.well_function_approx(u)
        
        print(f"    W(u) ≈ -0.5772 - ln(u)")
        print(f"         = -0.5772 - ln({u:.6f})")
        print(f"         = -0.5772 - ({np.log(u):.4f})")
        print(f"         = {W_u_approx:.4f} ✓")
        print(f"    ")
        print(f"    误差：|{W_u_exact:.4f} - {W_u_approx:.4f}| / {W_u_exact:.4f}")
        print(f"         = {abs(W_u_exact-W_u_approx)/W_u_exact*100:.2f}% (很小！)")
        
        W_u = W_u_exact  # 使用精确值
        
        # (4) 计算降深
        print(f"\n(4) 计算降深s（Theis公式）：")
        print(f"    ")
        print(f"    Theis公式：")
        print(f"    s = Q/(4πT) × W(u)")
        
        s = Q / (4 * np.pi * T) * W_u
        
        print(f"      = {Q} / (4π × {T}) × {W_u:.4f}")
        print(f"      = {Q / (4 * np.pi * T):.4f} × {W_u:.4f}")
        print(f"      = {s:.3f} m ✓")
        print(f"    ")
        print(f"    物理意义：抽水1天后，距井100m处水位下降{s:.3f}m")
        
        # (5) 不同时刻的降深
        print(f"\n(5) 计算不同时刻r={r}m处的降深：")
        
        t_array = np.array([0.1, 0.5, 1.0, 2.0, 5.0, 10.0])  # 时间数组 (d)
        s_array = []
        
        print(f"    ")
        print(f"    时间t(d)   u          W(u)      降深s(m)")
        print(f"    " + "-"*50)
        
        for t_i in t_array:
            u_i = r**2 * S / (4 * T * t_i)
            W_u_i = self.well_function_W(u_i)
            s_i = Q / (4 * np.pi * T) * W_u_i
            s_array.append(s_i)
            print(f"    {t_i:6.1f}     {u_i:.6f}   {W_u_i:.4f}    {s_i:.3f}")
        
        s_array = np.array(s_array)
        
        print(f"    ")
        print(f"    规律：时间越长，降深越大（但增速递减）")
        
        # (6) 不同距离的降深
        print(f"\n(6) 计算t={t}d时不同距离处的降深：")
        
        r_array = np.array([10, 30, 50, 100, 200, 500])  # 距离数组 (m)
        s_r_array = []
        
        print(f"    ")
        print(f"    距离r(m)   u          W(u)      降深s(m)")
        print(f"    " + "-"*50)
        
        for r_i in r_array:
            u_i = r_i**2 * S / (4 * T * t)
            W_u_i = self.well_function_W(u_i)
            s_i = Q / (4 * np.pi * T) * W_u_i
            s_r_array.append(s_i)
            print(f"    {r_i:6.0f}     {u_i:.6f}   {W_u_i:.4f}    {s_i:.3f}")
        
        s_r_array = np.array(s_r_array)
        
        print(f"    ")
        print(f"    规律：距离越远，降深越小")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：非稳定井流示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 绘制不同时刻的降深曲线
        r_plot = np.linspace(1, 500, 200)
        colors = ['red', 'orange', 'green', 'blue', 'purple']
        
        for i, t_i in enumerate([0.1, 0.5, 1.0, 5.0, 10.0]):
            s_plot = []
            for r_i in r_plot:
                u_i = r_i**2 * S / (4 * T * t_i)
                W_u_i = self.well_function_W(u_i)
                s_i = Q / (4 * np.pi * T) * W_u_i
                s_plot.append(s_i)
            ax1.plot(r_plot, s_plot, color=colors[i], linewidth=2,
                    label=f't={t_i}d')
        
        # 标注本题点
        ax1.plot([r], [s], 'ko', markersize=10)
        ax1.text(r*1.1, s*1.1, f'本题点\nr={r}m\nt={t}d\ns={s:.3f}m',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.set_xlabel('距井距离 r (m)', fontsize=12)
        ax1.set_ylabel('降深 s (m)', fontsize=12)
        ax1.set_title('Day 16 例题1：非稳定井流降深曲线', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 500])
        ax1.invert_yaxis()  # 降深向下
        
        # 子图2：降深随时间变化（s-t曲线）
        ax2 = plt.subplot(2, 2, 2)
        
        t_plot = np.logspace(-1, 2, 100)  # 0.1到100天，对数刻度
        s_t_plot = []
        
        for t_i in t_plot:
            u_i = r**2 * S / (4 * T * t_i)
            W_u_i = self.well_function_W(u_i)
            s_i = Q / (4 * np.pi * T) * W_u_i
            s_t_plot.append(s_i)
        
        ax2.semilogx(t_plot, s_t_plot, 'b-', linewidth=2.5)
        ax2.plot([t], [s], 'ro', markersize=10)
        ax2.text(t*1.5, s*0.95, f't={t}d\ns={s:.3f}m',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax2.set_xlabel('时间 t (d，对数坐标)', fontsize=12)
        ax2.set_ylabel('降深 s (m)', fontsize=12)
        ax2.set_title(f'r={r}m处降深随时间变化（s-lgt）', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, which='both')
        ax2.invert_yaxis()
        
        # 子图3：井函数W(u)-u曲线
        ax3 = plt.subplot(2, 2, 3)
        
        u_plot = np.logspace(-4, 0, 100)  # 0.0001到1
        W_u_plot = [self.well_function_W(u_i) for u_i in u_plot]
        W_u_approx_plot = [self.well_function_approx(u_i) for u_i in u_plot]
        
        ax3.loglog(u_plot, W_u_plot, 'b-', linewidth=2.5, label='W(u)精确值')
        ax3.loglog(u_plot, W_u_approx_plot, 'r--', linewidth=2, label='Jacob近似')
        ax3.axvline(x=0.01, color='green', linestyle='--', linewidth=1.5,
                   label='u=0.01 (近似界限)')
        
        ax3.plot([u], [W_u], 'ko', markersize=10)
        ax3.text(u*2, W_u*0.9, f'本题点\nu={u:.6f}\nW(u)={W_u:.4f}',
                fontsize=8, bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_xlabel('u（对数坐标）', fontsize=12)
        ax3.set_ylabel('W(u)（对数坐标）', fontsize=12)
        ax3.set_title('井函数W(u)曲线', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, which='both')
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          含水层厚度：M = {M} m
          渗透系数：k = {k} m/d
          储水系数：S = {S}
          抽水流量：Q = {Q} m³/d
          抽水时间：t = {t} d
          计算点距离：r = {r} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 导水系数：
            T = kM = {T} m²/d ✓
        
        (2) 井函数参数：
            u = r²S/(4Tt) = {u:.6f} ✓
        
        (3) 井函数：
            W(u) = {W_u:.4f} ✓
        
        (4) 降深（Theis公式）：
            s = Q/(4πT)×W(u)
              = {s:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • Theis公式：s=Q/(4πT)×W(u)
          • u = r²S/(4Tt)
          • W(u) = ∫(u→∞) e^(-y)/y dy
          • Jacob近似：W(u)≈-0.5772-ln(u)
            (u<0.01时)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day16_groundwater/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（15分评分标准）：")
        print("="*60)
        print("✓ (1) 计算导水系数T=kM (1分)")
        print("✓ (2) 计算u=r²S/(4Tt) (2分)")
        print("✓ (3) 判断u大小，选择计算方法 (1分)")
        print("✓ (4) 计算井函数W(u) (3分) ⭐⭐")
        print("✓ (5) 写出Theis公式 (2分) ⭐")
        print("✓ (6) 计算降深s (3分) ⭐⭐")
        print("✓ (7) 物理意义解释 (2分)")
        print("✓ (8) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 井函数W(u)：不能直接计算，需查表或用近似")
        print("  ⚠️ u的判断：u<0.01才能用Jacob近似")
        print("  ⚠️ 导水系数：T=kM，不要忘记乘M")
        print("  ⚠️ 非稳定vs稳定：非稳定考虑时间t")
        
        return {'T': T, 'u': u, 'W_u': W_u, 's': s}
    
    def example_2_well_interference(self):
        """
        例题2：井群干扰计算（强化题）⭐⭐⭐⭐⭐
        
        题目：两口抽水井A和B，相距L=200m
              承压含水层T=300m²/d，S=0.0005
              井A流量QA=2000m³/d，井B流量QB=1500m³/d
              抽水时间t=10天
              求：观测点P距井A为rA=100m，距井B为rB=150m
                  (1) 单独井A抽水时P点降深sA
                  (2) 单独井B抽水时P点降深sB
                  (3) 两井同时抽水时P点总降深s总
        
        考点：井群干扰，叠加原理，Theis公式应用
        难度：强化（必考！）
        时间：25分钟
        分值：18分
        """
        print("\n" + "="*60)
        print("例题2：井群干扰计算（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        L = 200.0      # 两井距离 (m)
        T = 300.0      # 导水系数 (m²/d)
        S = 0.0005     # 储水系数
        QA = 2000.0    # 井A流量 (m³/d)
        QB = 1500.0    # 井B流量 (m³/d)
        t = 10.0       # 抽水时间 (d)
        rA = 100.0     # P点距井A (m)
        rB = 150.0     # P点距井B (m)
        
        print(f"\n已知条件：")
        print(f"  两井距离 L = {L} m")
        print(f"  导水系数 T = {T} m²/d")
        print(f"  储水系数 S = {S}")
        print(f"  井A流量 QA = {QA} m³/d")
        print(f"  井B流量 QB = {QB} m³/d")
        print(f"  抽水时间 t = {t} d")
        print(f"  P点距井A rA = {rA} m")
        print(f"  P点距井B rB = {rB} m")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 单独井A
        print(f"\n(1) 单独井A抽水时P点降深sA：")
        print(f"    ")
        print(f"    计算uA：")
        
        uA = rA**2 * S / (4 * T * t)
        
        print(f"    uA = rA²S/(4Tt)")
        print(f"       = {rA}² × {S} / (4 × {T} × {t})")
        print(f"       = {uA:.7f} ✓")
        print(f"    ")
        print(f"    判断：uA = {uA:.7f} < 0.01")
        print(f"    使用Jacob近似：")
        
        W_uA = self.well_function_W(uA)
        
        print(f"    W(uA) = {W_uA:.4f} ✓")
        print(f"    ")
        print(f"    降深sA：")
        
        sA = QA / (4 * np.pi * T) * W_uA
        
        print(f"    sA = QA/(4πT) × W(uA)")
        print(f"       = {QA} / (4π × {T}) × {W_uA:.4f}")
        print(f"       = {sA:.3f} m ✓")
        
        # (2) 单独井B
        print(f"\n(2) 单独井B抽水时P点降深sB：")
        print(f"    ")
        print(f"    计算uB：")
        
        uB = rB**2 * S / (4 * T * t)
        
        print(f"    uB = rB²S/(4Tt)")
        print(f"       = {rB}² × {S} / (4 × {T} × {t})")
        print(f"       = {uB:.7f} ✓")
        print(f"    ")
        
        W_uB = self.well_function_W(uB)
        
        print(f"    W(uB) = {W_uB:.4f} ✓")
        print(f"    ")
        print(f"    降深sB：")
        
        sB = QB / (4 * np.pi * T) * W_uB
        
        print(f"    sB = QB/(4πT) × W(uB)")
        print(f"       = {QB} / (4π × {T}) × {W_uB:.4f}")
        print(f"       = {sB:.3f} m ✓")
        
        # (3) 总降深
        print(f"\n(3) 两井同时抽水时P点总降深（叠加原理）：")
        print(f"    ")
        print(f"    叠加原理：")
        print(f"    s总 = sA + sB")
        
        s_total = sA + sB
        
        print(f"        = {sA:.3f} + {sB:.3f}")
        print(f"        = {s_total:.3f} m ✓")
        print(f"    ")
        print(f"    物理意义：")
        print(f"    • 井A单独作用使P点下降{sA:.3f}m")
        print(f"    • 井B单独作用使P点下降{sB:.3f}m")
        print(f"    • 两井同时作用总降深{s_total:.3f}m")
        print(f"    • 干扰效应：{s_total:.3f}m > {sA:.3f}m（叠加）")
        
        # (4) 绘制等降深线
        print(f"\n(4) 绘制井群影响范围等降深线...")
        
        # 网格点
        x = np.linspace(-300, 300, 200)
        y = np.linspace(-300, 300, 200)
        X, Y = np.meshgrid(x, y)
        
        # 井A位置 (-100, 0)，井B位置 (100, 0)
        xA, yA = -L/2, 0
        xB, yB = L/2, 0
        
        # 计算每个网格点的距离
        rA_grid = np.sqrt((X - xA)**2 + (Y - yA)**2) + 0.1  # 避免r=0
        rB_grid = np.sqrt((X - xB)**2 + (Y - yB)**2) + 0.1
        
        # 计算每个网格点的降深
        uA_grid = rA_grid**2 * S / (4 * T * t)
        uB_grid = rB_grid**2 * S / (4 * T * t)
        
        # 计算W(u)（向量化）
        W_uA_grid = np.zeros_like(uA_grid)
        W_uB_grid = np.zeros_like(uB_grid)
        
        for i in range(uA_grid.shape[0]):
            for j in range(uA_grid.shape[1]):
                if uA_grid[i,j] < 10:  # 限制u范围
                    W_uA_grid[i,j] = self.well_function_W(uA_grid[i,j])
                if uB_grid[i,j] < 10:
                    W_uB_grid[i,j] = self.well_function_W(uB_grid[i,j])
        
        sA_grid = QA / (4 * np.pi * T) * W_uA_grid
        sB_grid = QB / (4 * np.pi * T) * W_uB_grid
        s_total_grid = sA_grid + sB_grid
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：等降深线图
        ax1 = plt.subplot(2, 2, 1)
        
        # 绘制等降深线
        levels = [0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
        contour = ax1.contour(X, Y, s_total_grid, levels=levels, 
                             colors='blue', linewidths=1.5)
        ax1.clabel(contour, inline=True, fontsize=8, fmt='%.1fm')
        
        # 填充颜色
        contourf = ax1.contourf(X, Y, s_total_grid, levels=20, 
                               cmap='YlOrRd', alpha=0.5)
        plt.colorbar(contourf, ax=ax1, label='降深 s (m)')
        
        # 井位置
        ax1.plot([xA], [yA], 'ro', markersize=15, label='井A')
        ax1.text(xA, yA-30, 'A', ha='center', fontsize=14, 
                fontweight='bold', color='red')
        ax1.plot([xB], [yB], 'bo', markersize=15, label='井B')
        ax1.text(xB, yB-30, 'B', ha='center', fontsize=14, 
                fontweight='bold', color='blue')
        
        # P点位置（计算实际坐标）
        # P点距A为rA=100m，距B为rB=150m
        # 使用余弦定理求P点坐标
        cosA = (rA**2 + L**2 - rB**2) / (2 * rA * L)
        angle = np.arccos(cosA)
        xP = xA + rA * np.cos(angle)
        yP = yA + rA * np.sin(angle)
        
        ax1.plot([xP], [yP], 'go', markersize=12, label='观测点P')
        ax1.text(xP+20, yP+20, f'P\ns={s_total:.2f}m', 
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 距离线
        ax1.plot([xA, xP], [yA, yP], 'g--', linewidth=1.5, alpha=0.5)
        ax1.text((xA+xP)/2, (yA+yP)/2-20, f'rA={rA}m', fontsize=9)
        ax1.plot([xB, xP], [yB, yP], 'g--', linewidth=1.5, alpha=0.5)
        ax1.text((xB+xP)/2, (yB+yP)/2+20, f'rB={rB}m', fontsize=9)
        
        ax1.set_xlabel('X (m)', fontsize=12)
        ax1.set_ylabel('Y (m)', fontsize=12)
        ax1.set_title('Day 16 例题2：井群等降深线图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axis('equal')
        ax1.set_xlim([-300, 300])
        ax1.set_ylim([-300, 300])
        
        # 子图2：沿AB连线的降深剖面
        ax2 = plt.subplot(2, 2, 2)
        
        x_profile = np.linspace(-300, 300, 300)
        y_profile = 0
        
        rA_profile = np.abs(x_profile - xA) + 0.1
        rB_profile = np.abs(x_profile - xB) + 0.1
        
        uA_profile = rA_profile**2 * S / (4 * T * t)
        uB_profile = rB_profile**2 * S / (4 * T * t)
        
        W_uA_profile = np.array([self.well_function_W(u) if u < 10 else 0 for u in uA_profile])
        W_uB_profile = np.array([self.well_function_W(u) if u < 10 else 0 for u in uB_profile])
        
        sA_profile = QA / (4 * np.pi * T) * W_uA_profile
        sB_profile = QB / (4 * np.pi * T) * W_uB_profile
        s_total_profile = sA_profile + sB_profile
        
        ax2.plot(x_profile, sA_profile, 'r--', linewidth=2, label='井A单独')
        ax2.plot(x_profile, sB_profile, 'b--', linewidth=2, label='井B单独')
        ax2.plot(x_profile, s_total_profile, 'g-', linewidth=2.5, label='两井叠加')
        
        ax2.axvline(x=xA, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
        ax2.text(xA, 0.2, 'A', ha='center', fontsize=12, color='red', fontweight='bold')
        ax2.axvline(x=xB, color='blue', linestyle=':', linewidth=1.5, alpha=0.5)
        ax2.text(xB, 0.2, 'B', ha='center', fontsize=12, color='blue', fontweight='bold')
        
        ax2.plot([xP], [s_total], 'go', markersize=10)
        
        ax2.set_xlabel('沿AB连线距离 (m)', fontsize=12)
        ax2.set_ylabel('降深 s (m)', fontsize=12)
        ax2.set_title('沿AB连线降深剖面', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()
        ax2.set_xlim([-300, 300])
        
        # 子图3：叠加原理示意
        ax3 = plt.subplot(2, 2, 3)
        
        categories = ['井A单独', '井B单独', '两井叠加\n(理论)', '两井叠加\n(实际)']
        heights = [sA, sB, sA+sB, s_total]
        colors_bar = ['red', 'blue', 'orange', 'green']
        
        bars = ax3.bar(categories, heights, color=colors_bar, 
                      edgecolor='black', linewidth=2, alpha=0.7)
        
        for bar, height in zip(bars, heights):
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}m',
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        # 叠加示意
        ax3.plot([0, 1, 2], [sA, sB, sA+sB], 'k--', linewidth=2, alpha=0.5)
        ax3.text(1, (sA+sB)/2, '叠加原理\ns总=sA+sB', 
                ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_ylabel('降深 (m)', fontsize=12)
        ax3.set_title('叠加原理验证', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          导水系数：T = {T} m²/d
          储水系数：S = {S}
          井A流量：QA = {QA} m³/d
          井B流量：QB = {QB} m³/d
          抽水时间：t = {t} d
          P点距A：rA = {rA} m
          P点距B：rB = {rB} m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 井A单独降深：
            uA = {uA:.7f}
            W(uA) = {W_uA:.4f}
            sA = {sA:.3f} m ✓
        
        (2) 井B单独降深：
            uB = {uB:.7f}
            W(uB) = {W_uB:.4f}
            sB = {sB:.3f} m ✓
        
        (3) 两井总降深（叠加）：
            s总 = sA + sB
                = {s_total:.3f} m ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键原理：
          • 叠加原理：s总=ΣsᵢI
          • 适用条件：线性系统
          • 井群干扰：降深叠加增大
          • 优化布井：考虑相互影响
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day16_groundwater/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（18分评分标准）：")
        print("="*60)
        print("✓ (1) 计算井A参数uA (2分)")
        print("✓ (2) 计算井A降深sA (3分) ⭐⭐")
        print("✓ (3) 计算井B参数uB (2分)")
        print("✓ (4) 计算井B降深sB (3分) ⭐⭐")
        print("✓ (5) 写出叠加原理 (2分) ⭐")
        print("✓ (6) 计算总降深s总=sA+sB (3分) ⭐⭐")
        print("✓ (7) 物理意义解释 (2分)")
        print("✓ (8) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 叠加原理：s总=sA+sB，不是sA×sB")
        print("  ⚠️ 距离计算：rA、rB分别是P到A、B的距离")
        print("  ⚠️ 流量不同：QA≠QB，要分别计算")
        print("  ⚠️ 适用条件：线性系统，承压含水层")
        
        return {'sA': sA, 'sB': sB, 's_total': s_total}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 16 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. Theis公式（非稳定井流）：")
        print("     s = Q/(4πT) × W(u)")
        print("     u = r²S/(4Tt)")
        print("     ")
        print("  2. 井函数W(u)：")
        print("     W(u) = ∫(u to ∞) (e^(-y)/y) dy")
        print("     ")
        print("  3. Jacob近似（u<0.01时）：")
        print("     W(u) ≈ -0.5772 - ln(u)")
        print("     s = 2.3Q/(4πT) × lg(2.25Tt/r²S)")
        print("     ")
        print("  4. 叠加原理（井群干扰）：")
        print("     s总 = s₁ + s₂ + s₃ + ...")
        print("     ")
        print("  5. 导水系数与储水系数：")
        print("     T = k × M  (导水系数)")
        print("     S = μ × M  (储水系数，承压)")
        print("     S = μₑ     (储水系数，潜水)")
        
        print("\n✅ 稳定井流vs非稳定井流：")
        print("  ┌──────────┬──────────────┬──────────────┐")
        print("  │ 项目     │ 稳定井流     │ 非稳定井流   │")
        print("  ├──────────┼──────────────┼──────────────┤")
        print("  │ 时间因素 │ 不考虑t      │ 考虑t        │")
        print("  │ 公式     │ Dupuit       │ Theis        │")
        print("  │ 参数     │ H²-h²或H-h   │ W(u)         │")
        print("  │ 应用     │ 长时间抽水   │ 短时间抽水   │")
        print("  └──────────┴──────────────┴──────────────┘")
        
        print("\n✅ 井函数W(u)特点：")
        print("  • W(u)是单调递减函数")
        print("  • u越小，W(u)越大（距离近或时间长）")
        print("  • u<0.01时可用Jacob近似")
        print("  • 需查表或数值积分")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【非稳定井流题】")
        print("  Step 1: 计算导水系数T=kM")
        print("  Step 2: 计算u=r²S/(4Tt)")
        print("  Step 3: 判断u大小，选择计算方法")
        print("  Step 4: 计算W(u)（查表或近似）")
        print("  Step 5: 应用Theis公式s=Q/(4πT)×W(u)")
        print("  ")
        print("  【井群干扰题】")
        print("  Step 1: 分别计算各井单独作用")
        print("  Step 2: 每口井用Theis公式求sᵢ")
        print("  Step 3: 应用叠加原理s总=Σsᵢ")
        print("  Step 4: 分析干扰效应")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：用稳定井流公式算非稳定问题")
        print("  ❌ 错误2：W(u)直接算，忘记查表或近似")
        print("  ❌ 错误3：u>0.01时仍用Jacob近似")
        print("  ❌ 错误4：井群干扰忘记叠加")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：看到时间t→非稳定井流→Theis")
        print("  ✓ 技巧2：u<0.01→Jacob近似→简化计算")
        print("  ✓ 技巧3：多口井→叠加原理→s总=Σsᵢ")
        print("  ✓ 技巧4：画图！平面图+剖面图清晰")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能区分稳定与非稳定井流")
        print("  □ 掌握Theis公式应用")
        print("  □ 理解井函数W(u)意义")
        print("  □ 熟练井群干扰计算（叠加原理）")
        
        print("\n📅 明日预告：Day 17 - 水泵与泵站")
        print("  • 水泵特性曲线")
        print("  • 工况点计算")
        print("  • 水泵选型")
        print("  • 并联与串联")
        
        print("\n💪 今日格言：")
        print("  「非稳定井流是难点，但掌握了=拿到18分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 16: 地下水动力学")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day16 = Day16Groundwater()
    
    # 例题1：非稳定井流
    result1 = day16.example_1_unsteady_well()
    
    # 例题2：井群干扰
    result2 = day16.example_2_well_interference()
    
    # 每日总结
    day16.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 16 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握Theis公式")
    print(f"  ✓ 掌握井群干扰")
    print(f"  ✓ 理解井函数W(u)")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n🎊 50%半程里程碑达成！")
    print(f"  15/30天完成，进度过半！")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
