"""
《水力学考研1000题详解》配套代码
题目681：井流计算（承压井与无压井）

问题描述：
某地下含水层厚度H=20m，渗透系数k=10m/d。
在该含水层中钻一口抽水井，井半径r₀=0.2m，影响半径R=100m。
求：(1) 承压井流量Q（水位降深s=5m）
    (2) 无压井流量Q（水位降深s=8m）
    (3) 井壁处渗流速度
    (4) 绘制水位降落漏斗

考点：
1. 达西定律：v = k·i
2. 承压井公式：Q = 2πkH(H-s)/ln(R/r₀)
3. 无压井公式：Q = πk(H²-(H-s)²)/ln(R/r₀)
4. 渗流速度：v = Q/(2πrh)
5. 水位降落曲线：s(r) = s·ln(R/r)/ln(R/r₀)

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch, Wedge
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WellFlow:
    """井流计算类"""
    
    def __init__(self, H, k, r0, R, s_confined, s_unconfined, g=9.8):
        """
        初始化
        
        参数:
            H: 含水层厚度 (m)
            k: 渗透系数 (m/d)
            r0: 井半径 (m)
            R: 影响半径 (m)
            s_confined: 承压井水位降深 (m)
            s_unconfined: 无压井水位降深 (m)
            g: 重力加速度 (m/s²)
        """
        self.H = H          # 含水层厚度 (m)
        self.k = k          # 渗透系数 (m/d)
        self.r0 = r0        # 井半径 (m)
        self.R = R          # 影响半径 (m)
        self.s_c = s_confined    # 承压井降深 (m)
        self.s_u = s_unconfined  # 无压井降深 (m)
        self.g = g          # 重力加速度 (m/s²)
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算井流"""
        # 1. 承压井流量
        self.Q_confined = (2 * np.pi * self.k * self.H * self.s_c) / np.log(self.R / self.r0)
        
        # 2. 无压井流量
        self.Q_unconfined = (np.pi * self.k * (self.H**2 - (self.H - self.s_u)**2)) / np.log(self.R / self.r0)
        
        # 3. 承压井井壁渗流速度
        self.v_confined_wall = self.Q_confined / (2 * np.pi * self.r0 * self.H)
        
        # 4. 无压井井壁渗流速度
        h_wall_unconfined = self.H - self.s_u
        self.v_unconfined_wall = self.Q_unconfined / (2 * np.pi * self.r0 * h_wall_unconfined)
        
        # 5. 计算水位降落曲线（承压井）
        self.r_array = np.linspace(self.r0, self.R, 100)
        self.s_confined_curve = self.s_c * np.log(self.R / self.r_array) / np.log(self.R / self.r0)
        
        # 6. 计算水位降落曲线（无压井）
        self.s_unconfined_curve = []
        for r in self.r_array:
            # 对于无压井，水头h(r)满足：h² = h_w² + [H² - h_w²]·ln(R/r)/ln(R/r₀)
            h_w = self.H - self.s_u  # 井壁水头
            h_r_sq = h_w**2 + (self.H**2 - h_w**2) * np.log(self.R / r) / np.log(self.R / self.r0)
            h_r = np.sqrt(h_r_sq)
            s_r = self.H - h_r
            self.s_unconfined_curve.append(s_r)
        self.s_unconfined_curve = np.array(self.s_unconfined_curve)
        
        # 7. 达西流速（平均）
        self.v_darcy_confined = self.Q_confined / (2 * np.pi * self.R * self.H)
        self.v_darcy_unconfined = self.Q_unconfined / (2 * np.pi * self.R * (self.H - self.s_u/2))
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*80)
        print("题目681：井流计算（承压井与无压井）")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"含水层厚度: H = {self.H} m")
        print(f"渗透系数: k = {self.k} m/d = {self.k/86400:.6f} m/s")
        print(f"井半径: r₀ = {self.r0} m")
        print(f"影响半径: R = {self.R} m")
        print(f"承压井水位降深: s = {self.s_c} m")
        print(f"无压井水位降深: s = {self.s_u} m")
        
        print("\n【井流基本概念】")
        print("1. 达西定律: v = k·i")
        print("   - v: 渗流速度（m/s）")
        print("   - k: 渗透系数（m/s）")
        print("   - i: 水力坡度（无量纲）")
        print("2. 承压井: 含水层上下有不透水层，水头降低但饱和厚度不变")
        print("3. 无压井: 含水层上部为自由水面，水头降低且饱和厚度减小")
        print("4. 影响半径R: 抽水影响范围的半径")
        print("5. 水位降深s: 抽水前后水位差")
        
        print("\n【计算过程】")
        
        print("\n一、承压井流量计算")
        print("\n步骤1：承压井基本方程推导")
        print("达西定律: v = k·i")
        print("水力坡度: i = dh/dr")
        print("流量连续: Q = 2πrh·v = 2πrh·k·(dh/dr)")
        print("承压井特点: h = H - s，饱和厚度不变")
        print("积分: Q∫(dr/r) = 2πkH∫ds")
        print("边界条件: r=r₀时s=s，r=R时s=0")
        print("得到: Q·ln(R/r₀) = 2πkH·s")
        
        print("\n步骤2：承压井流量公式")
        print("Q = 2πkHs / ln(R/r₀)")
        print(f"  = 2π×{self.k}×{self.H}×{self.s_c} / ln({self.R}/{self.r0})")
        print(f"  = 2π×{self.k}×{self.H}×{self.s_c} / {np.log(self.R/self.r0):.4f}")
        print(f"  = {self.Q_confined:.4f} m³/d")
        print(f"  = {self.Q_confined/86400:.6f} m³/s")
        
        print("\n步骤3：承压井井壁渗流速度")
        print("v = Q / (2πr₀H)")
        print(f"  = {self.Q_confined:.4f} / (2π×{self.r0}×{self.H})")
        print(f"  = {self.v_confined_wall:.4f} m/d")
        print(f"  = {self.v_confined_wall/86400:.6f} m/s")
        
        print("\n步骤4：承压井水位降落曲线")
        print("s(r) = s · ln(R/r) / ln(R/r₀)")
        print(f"例如，r=10m时:")
        s_10m = self.s_c * np.log(self.R / 10) / np.log(self.R / self.r0)
        print(f"s(10) = {self.s_c} × ln({self.R}/10) / ln({self.R}/{self.r0})")
        print(f"      = {s_10m:.4f} m")
        
        print("\n二、无压井流量计算")
        print("\n步骤1：无压井基本方程推导")
        print("达西定律: v = k·i")
        print("水力坡度: i = dh/dr")
        print("流量连续: Q = 2πrh·v = 2πrh·k·(dh/dr)")
        print("无压井特点: 饱和厚度h随r变化")
        print("积分: Q∫(dr/r) = 2πk∫h·dh")
        print("边界条件: r=r₀时h=h₀，r=R时h=H")
        print("得到: Q·ln(R/r₀) = πk(H² - h₀²)")
        
        print("\n步骤2：无压井流量公式")
        h0 = self.H - self.s_u
        print(f"井壁水头: h₀ = H - s = {self.H} - {self.s_u} = {h0} m")
        print("Q = πk(H² - h₀²) / ln(R/r₀)")
        print(f"  = π×{self.k}×({self.H}² - {h0}²) / ln({self.R}/{self.r0})")
        print(f"  = π×{self.k}×({self.H**2} - {h0**2}) / {np.log(self.R/self.r0):.4f}")
        print(f"  = π×{self.k}×{self.H**2 - h0**2} / {np.log(self.R/self.r0):.4f}")
        print(f"  = {self.Q_unconfined:.4f} m³/d")
        print(f"  = {self.Q_unconfined/86400:.6f} m³/s")
        
        print("\n步骤3：无压井井壁渗流速度")
        print("v = Q / (2πr₀h₀)")
        print(f"  = {self.Q_unconfined:.4f} / (2π×{self.r0}×{h0})")
        print(f"  = {self.v_unconfined_wall:.4f} m/d")
        print(f"  = {self.v_unconfined_wall/86400:.6f} m/s")
        
        print("\n步骤4：无压井水位降落曲线")
        print("h²(r) = h₀² + (H² - h₀²)·ln(R/r)/ln(R/r₀)")
        print("s(r) = H - h(r)")
        print(f"例如，r=10m时:")
        h_10m_sq = h0**2 + (self.H**2 - h0**2) * np.log(self.R / 10) / np.log(self.R / self.r0)
        h_10m = np.sqrt(h_10m_sq)
        s_10m_u = self.H - h_10m
        print(f"h²(10) = {h0}² + ({self.H}² - {h0}²)×ln({self.R}/10)/ln({self.R}/{self.r0})")
        print(f"       = {h_10m_sq:.4f}")
        print(f"h(10) = {h_10m:.4f} m")
        print(f"s(10) = {self.H} - {h_10m:.4f} = {s_10m_u:.4f} m")
        
        print("\n【最终答案】")
        print("="*80)
        print("\n(1) 承压井:")
        print(f"    流量: Q = {self.Q_confined:.4f} m³/d = {self.Q_confined/86400:.6f} m³/s")
        print(f"    井壁渗流速度: v = {self.v_confined_wall:.4f} m/d = {self.v_confined_wall/86400:.6f} m/s")
        
        print("\n(2) 无压井:")
        print(f"    流量: Q = {self.Q_unconfined:.4f} m³/d = {self.Q_unconfined/86400:.6f} m³/s")
        print(f"    井壁渗流速度: v = {self.v_unconfined_wall:.4f} m/d = {self.v_unconfined_wall/86400:.6f} m/s")
        
        print("\n(3) 对比分析:")
        print(f"    流量比: Q_无压/Q_承压 = {self.Q_unconfined/self.Q_confined:.4f}")
        print(f"    速度比: v_无压/v_承压 = {self.v_unconfined_wall/self.v_confined_wall:.4f}")
        print("    结论: 在相同降深下，承压井流量通常大于无压井")
        print("          （因为承压井饱和厚度保持为H，而无压井减小）")
        print("="*80)
        
        print("\n【核心公式】")
        print("承压井: Q = 2πkHs / ln(R/r₀)")
        print("无压井: Q = πk(H² - h₀²) / ln(R/r₀)")
        print("渗流速度: v = Q / (2πrh)")
        print("水位降落（承压）: s(r) = s · ln(R/r) / ln(R/r₀)")
        print("水位降落（无压）: h²(r) = h₀² + (H² - h₀²)·ln(R/r)/ln(R/r₀)")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：承压井剖面图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_confined_well(ax1)
        
        # 子图2：无压井剖面图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_unconfined_well(ax2)
        
        # 子图3：水位降落曲线对比
        ax3 = plt.subplot(2, 2, 3)
        self._plot_drawdown_curves(ax3)
        
        # 子图4：流量与参数关系
        ax4 = plt.subplot(2, 2, 4)
        self._plot_Q_vs_parameters(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_confined_well(self, ax):
        """绘制承压井剖面图"""
        # 不透水层（上）
        ax.fill_between([0, self.R*1.2], [self.H+5, self.H+5], [self.H, self.H],
                       color='gray', alpha=0.5, label='不透水层')
        
        # 含水层
        ax.fill_between([0, self.R*1.2], [self.H, self.H], [0, 0],
                       color='lightblue', alpha=0.4, label='含水层')
        
        # 不透水层（下）
        ax.fill_between([0, self.R*1.2], [0, 0], [-5, -5],
                       color='gray', alpha=0.5)
        
        # 原始水位
        ax.plot([0, self.R*1.2], [self.H, self.H], 'b--', linewidth=2, label='原始水位')
        
        # 抽水后水位（降落漏斗）
        water_level = self.H - self.s_confined_curve
        ax.plot(self.r_array, water_level, 'b-', linewidth=2.5, label='抽水后水位')
        ax.fill_between(self.r_array, water_level, 0, color='cyan', alpha=0.3)
        
        # 井筒
        well_bottom = 0
        ax.plot([self.r0, self.r0], [well_bottom, self.H-self.s_c], 'k-', linewidth=3)
        ax.plot([0, self.r0], [self.H-self.s_c, self.H-self.s_c], 'b-', linewidth=2)
        
        # 标注
        # 含水层厚度
        ax.annotate('', xy=(self.R*1.15, self.H), xytext=(self.R*1.15, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(self.R*1.18, self.H/2, f'H={self.H}m', fontsize=11, color='red',
               rotation=90, va='center')
        
        # 降深
        ax.annotate('', xy=(self.r0*3, self.H), xytext=(self.r0*3, self.H-self.s_c),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(self.r0*3.5, self.H-self.s_c/2, f's={self.s_c}m', fontsize=10, color='green')
        
        # 影响半径
        ax.plot([self.R, self.R], [0, self.H], 'r--', linewidth=1.5, alpha=0.7)
        ax.text(self.R, -1, f'R={self.R}m', fontsize=10, ha='center', color='red')
        
        # 井半径
        ax.text(self.r0/2, self.H-self.s_c-2, f'r₀={self.r0}m', fontsize=9, color='black')
        
        # 流量标注
        ax.text(self.R*0.5, self.H+2, f'承压井\nQ={self.Q_confined:.2f}m³/d',
               fontsize=11, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlim(0, self.R*1.3)
        ax.set_ylim(-6, self.H+7)
        ax.set_xlabel('径向距离 r (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('承压井剖面图', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_unconfined_well(self, ax):
        """绘制无压井剖面图"""
        # 不透水层（下）
        ax.fill_between([0, self.R*1.2], [0, 0], [-5, -5],
                       color='gray', alpha=0.5, label='不透水层')
        
        # 含水层（饱和区）
        water_level = self.H - self.s_unconfined_curve
        ax.fill_between(self.r_array, water_level, 0, color='lightblue', alpha=0.4, label='饱和区')
        
        # 含水层（非饱和区）
        ax.fill_between([0, self.R*1.2], [self.H, self.H], [0, 0],
                       color='lightyellow', alpha=0.3, label='原含水层范围')
        
        # 原始水位
        ax.plot([0, self.R*1.2], [self.H, self.H], 'b--', linewidth=2, label='原始水位')
        
        # 抽水后水位（自由水面）
        ax.plot(self.r_array, water_level, 'b-', linewidth=2.5, label='抽水后水位')
        
        # 井筒
        well_bottom = 0
        h_well = self.H - self.s_u
        ax.plot([self.r0, self.r0], [well_bottom, h_well], 'k-', linewidth=3)
        ax.plot([0, self.r0], [h_well, h_well], 'b-', linewidth=2)
        
        # 标注
        # 原含水层厚度
        ax.annotate('', xy=(self.R*1.15, self.H), xytext=(self.R*1.15, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(self.R*1.18, self.H/2, f'H={self.H}m', fontsize=11, color='red',
               rotation=90, va='center')
        
        # 降深
        ax.annotate('', xy=(self.r0*3, self.H), xytext=(self.r0*3, h_well),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(self.r0*3.5, self.H-self.s_u/2, f's={self.s_u}m', fontsize=10, color='green')
        
        # 井壁水头
        ax.annotate('', xy=(self.r0*5, h_well), xytext=(self.r0*5, 0),
                   arrowprops=dict(arrowstyle='<->', lw=1.5, color='blue'))
        ax.text(self.r0*5.5, h_well/2, f'h₀={h_well}m', fontsize=9, color='blue',
               rotation=90, va='center')
        
        # 影响半径
        ax.plot([self.R, self.R], [0, self.H], 'r--', linewidth=1.5, alpha=0.7)
        ax.text(self.R, -1, f'R={self.R}m', fontsize=10, ha='center', color='red')
        
        # 流量标注
        ax.text(self.R*0.5, self.H+2, f'无压井\nQ={self.Q_unconfined:.2f}m³/d',
               fontsize=11, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlim(0, self.R*1.3)
        ax.set_ylim(-6, self.H+7)
        ax.set_xlabel('径向距离 r (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('无压井剖面图', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_drawdown_curves(self, ax):
        """绘制水位降落曲线对比"""
        # 承压井降深曲线
        ax.plot(self.r_array, self.s_confined_curve, 'b-', linewidth=2.5,
               label=f'承压井 (s={self.s_c}m)', marker='o', markersize=3, markevery=10)
        
        # 无压井降深曲线
        ax.plot(self.r_array, self.s_unconfined_curve, 'r-', linewidth=2.5,
               label=f'无压井 (s={self.s_u}m)', marker='s', markersize=3, markevery=10)
        
        # 井壁位置
        ax.axvline(self.r0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(self.r0*1.1, max(self.s_c, self.s_u)*0.9, f'井壁\nr₀={self.r0}m',
               fontsize=9, color='gray')
        
        # 影响半径
        ax.axvline(self.R, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(self.R*0.95, max(self.s_c, self.s_u)*0.1, f'影响半径\nR={self.R}m',
               fontsize=9, ha='right', color='gray')
        
        # 标注几个关键点
        r_marks = [1, 10, 50]
        for r_mark in r_marks:
            if r_mark < self.R and r_mark > self.r0:
                s_c_mark = self.s_c * np.log(self.R / r_mark) / np.log(self.R / self.r0)
                ax.plot(r_mark, s_c_mark, 'bo', markersize=6)
                
        ax.set_xlabel('径向距离 r (m)', fontsize=12)
        ax.set_ylabel('水位降深 s (m)', fontsize=12)
        ax.set_title('水位降落曲线对比', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        
        # 添加说明
        ax.text(0.5, 0.05, '降深随距离对数增长\n影响半径处降深为0',
               transform=ax.transAxes, fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    def _plot_Q_vs_parameters(self, ax):
        """绘制流量与参数关系"""
        # 不同降深下的流量
        s_range = np.linspace(1, self.H*0.8, 50)
        Q_confined_range = []
        Q_unconfined_range = []
        
        for s in s_range:
            Q_c = (2 * np.pi * self.k * self.H * s) / np.log(self.R / self.r0)
            Q_confined_range.append(Q_c)
            
            if s < self.H:
                h0 = self.H - s
                Q_u = (np.pi * self.k * (self.H**2 - h0**2)) / np.log(self.R / self.r0)
                Q_unconfined_range.append(Q_u)
            else:
                Q_unconfined_range.append(0)
        
        # 绘制曲线
        ax.plot(s_range, Q_confined_range, 'b-', linewidth=2.5, label='承压井')
        ax.plot(s_range, Q_unconfined_range, 'r-', linewidth=2.5, label='无压井')
        
        # 标注当前点
        ax.plot(self.s_c, self.Q_confined, 'bo', markersize=10, zorder=5)
        ax.text(self.s_c*1.05, self.Q_confined, 
               f'({self.s_c}, {self.Q_confined:.1f})',
               fontsize=9, color='blue')
        
        ax.plot(self.s_u, self.Q_unconfined, 'rs', markersize=10, zorder=5)
        ax.text(self.s_u*0.95, self.Q_unconfined*1.05,
               f'({self.s_u}, {self.Q_unconfined:.1f})',
               fontsize=9, ha='right', color='red')
        
        ax.set_xlabel('水位降深 s (m)', fontsize=12)
        ax.set_ylabel('流量 Q (m³/d)', fontsize=12)
        ax.set_title('流量与降深关系', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 添加说明
        ax.text(0.5, 0.95, 
               '承压井：Q ∝ s（线性）\n无压井：Q ∝ (H²-h₀²)（非线性）',
               transform=ax.transAxes, fontsize=9, ha='center', va='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))


def test_problem_681():
    """测试题目681"""
    # 已知条件
    H = 20.0            # 含水层厚度 (m)
    k = 10.0            # 渗透系数 (m/d)
    r0 = 0.2            # 井半径 (m)
    R = 100.0           # 影响半径 (m)
    s_confined = 5.0    # 承压井降深 (m)
    s_unconfined = 8.0  # 无压井降深 (m)
    
    # 创建计算对象
    well = WellFlow(H, k, r0, R, s_confined, s_unconfined)
    
    # 打印结果
    well.print_results()
    
    # 可视化
    fig = well.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_681_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_681_result.png")
    
    # 验证答案（合理性检查）
    assert well.Q_confined > 0, "承压井流量必须为正"
    assert well.Q_unconfined > 0, "无压井流量必须为正"
    assert well.v_confined_wall > 0, "渗流速度必须为正"
    assert well.v_unconfined_wall > 0, "渗流速度必须为正"
    assert len(well.s_confined_curve) > 0, "降深曲线必须有数据"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("井流是地下水渗流的重要应用！")
    print("• 达西定律：v = k·i")
    print("• 承压井：饱和厚度不变，Q与s成正比")
    print("• 无压井：饱和厚度减小，Q与(H²-h₀²)成正比")
    print("• 水位降落漏斗：s(r)与ln(r)成反比")
    print("• 应用：供水井设计、降水工程、水资源评价")


if __name__ == "__main__":
    test_problem_681()
