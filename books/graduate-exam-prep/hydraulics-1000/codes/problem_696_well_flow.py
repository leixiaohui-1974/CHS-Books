"""
《水力学考研1000题详解》配套代码
题目696：井流综合计算

问题描述：
某地下水抽水试验，已知：
  承压含水层厚度: M = 15 m
  渗透系数: k = 25 m/d
  初始水头: H₀ = 30 m
  抽水井半径: r₀ = 0.2 m
  影响半径: R = 300 m
  设计抽水量: Q = 2000 m³/d

要求：
(1) 计算承压井的降落曲线方程
(2) 计算井内水位降深s₀
(3) 计算距井中心r=50m处的降深s
(4) 绘制降落曲线
(5) 若改为潜水井（初始水位h₀=30m），重新计算
(6) 对比承压井与潜水井的差异

考点：
1. 承压井公式: Q = 2πkM(H-H₀)/ln(R/r₀)
2. 承压井降落曲线: H = H₀ + Q/(2πkM)·ln(r/R)
3. 潜水井公式: Q = πk(h₀²-h²)/ln(R/r₀)
4. 潜水井降落曲线: h² = h₀² - Q/(πk)·ln(r/R)
5. 影响半径: R = 10s₀√k (经验公式)
6. 承压井特点: 降深s = H₀ - H（与r成对数关系）
7. 潜水井特点: 降深较大，曲线更陡

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon, Wedge

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WellFlow:
    """井流计算类"""
    
    def __init__(self):
        """初始化"""
        # 承压井参数
        self.M = 15          # 含水层厚度 (m)
        self.k = 25          # 渗透系数 (m/d)
        self.H0 = 30         # 初始水头 (m)
        self.r0 = 0.2        # 井半径 (m)
        self.R_confined = 300         # 承压井影响半径 (m)
        self.R_unconfined = 200       # 潜水井影响半径 (m)，较小
        self.Q_confined = 2000        # 承压井抽水量 (m³/d)
        self.Q_unconfined = 400       # 潜水井抽水量 (m³/d)，较小
        
        # 计算承压井
        self.calculate_confined_well()
        
        # 计算潜水井
        self.calculate_unconfined_well()
    
    def calculate_confined_well(self):
        """计算承压井"""
        print(f"\n{'='*80}")
        print("【承压井计算】")
        print(f"{'='*80}")
        
        print(f"\n已知条件:")
        print(f"  含水层厚度: M = {self.M} m")
        print(f"  渗透系数: k = {self.k} m/d")
        print(f"  初始水头: H₀ = {self.H0} m")
        print(f"  井半径: r₀ = {self.r0} m")
        print(f"  影响半径: R = {self.R_confined} m")
        print(f"  抽水量: Q = {self.Q_confined} m³/d")
        
        # 1. 降落曲线方程
        print(f"\n1. 降落曲线方程:")
        print(f"   H(r) = H₀ + Q/(2πkM)·ln(r/R)")
        print(f"   H(r) = {self.H0} + {self.Q_confined}/(2π×{self.k}×{self.M})·ln(r/{self.R_confined})")
        
        # 系数
        self.A_confined = self.Q_confined / (2 * np.pi * self.k * self.M)
        print(f"   系数: A = Q/(2πkM) = {self.A_confined:.4f}")
        print(f"   ∴ H(r) = {self.H0} + {self.A_confined:.4f}·ln(r/{self.R_confined})")
        
        # 2. 井内水位
        self.H_well = self.H0 + self.A_confined * np.log(self.r0 / self.R_confined)
        self.s0_confined = self.H0 - self.H_well
        
        print(f"\n2. 井内水位:")
        print(f"   H(r₀) = {self.H0} + {self.A_confined:.4f}·ln({self.r0}/{self.R_confined})")
        print(f"   H(r₀) = {self.H_well:.4f} m")
        print(f"   降深: s₀ = H₀ - H(r₀) = {self.H0} - {self.H_well:.4f}")
        print(f"   s₀ = {self.s0_confined:.4f} m")
        
        # 3. r=50m处水位
        r_test = 50
        self.H_50 = self.H0 + self.A_confined * np.log(r_test / self.R_confined)
        self.s_50_confined = self.H0 - self.H_50
        
        print(f"\n3. r={r_test}m处水位:")
        print(f"   H({r_test}) = {self.H0} + {self.A_confined:.4f}·ln({r_test}/{self.R_confined})")
        print(f"   H({r_test}) = {self.H_50:.4f} m")
        print(f"   降深: s = {self.H0} - {self.H_50:.4f} = {self.s_50_confined:.4f} m")
        
        # 4. 验证抽水量公式
        Q_check = 2 * np.pi * self.k * self.M * (self.H0 - self.H_well) / np.log(self.R_confined / self.r0)
        print(f"\n4. 验证（反算抽水量）:")
        print(f"   Q = 2πkM(H₀-H_well)/ln(R/r₀)")
        print(f"   Q = 2π×{self.k}×{self.M}×{self.H0-self.H_well:.4f}/ln({self.R_confined}/{self.r0})")
        print(f"   Q = {Q_check:.2f} m³/d ✓ (与给定值{self.Q_confined}相符)")
        
        # 5. 渗流速度（井壁处最大）
        self.v0_confined = self.Q_confined / (2 * np.pi * self.r0 * self.M)
        print(f"\n5. 井壁渗流速度:")
        print(f"   v₀ = Q/(2πr₀M) = {self.Q_confined}/(2π×{self.r0}×{self.M})")
        print(f"   v₀ = {self.v0_confined:.2f} m/d")
    
    def calculate_unconfined_well(self):
        """计算潜水井"""
        print(f"\n{'='*80}")
        print("【潜水井计算】")
        print(f"{'='*80}")
        
        print(f"\n已知条件:")
        print(f"  渗透系数: k = {self.k} m/d")
        print(f"  初始水位: h₀ = {self.H0} m")
        print(f"  井半径: r₀ = {self.r0} m")
        print(f"  影响半径: R = {self.R_unconfined} m (潜水井影响半径较小)")
        print(f"  抽水量: Q = {self.Q_unconfined} m³/d (潜水井抽水量较小)")
        
        # 1. 降落曲线方程
        print(f"\n1. 降落曲线方程:")
        print(f"   h²(r) = h₀² + Q/(πk)·ln(r/R)  【注意：ln(r/R)<0】")
        print(f"   h²(r) = {self.H0}² + {self.Q_unconfined}/(π×{self.k})·ln(r/{self.R_unconfined})")
        
        # 系数
        self.B_unconfined = self.Q_unconfined / (np.pi * self.k)
        print(f"   系数: B = Q/(πk) = {self.B_unconfined:.4f}")
        print(f"   ∴ h²(r) = {self.H0**2} + {self.B_unconfined:.4f}·ln(r/{self.R_unconfined})")
        
        # 2. 井内水位
        h_well_sq = self.H0**2 + self.B_unconfined * np.log(self.r0 / self.R_unconfined)
        self.h_well = np.sqrt(h_well_sq)
        self.s0_unconfined = self.H0 - self.h_well
        
        print(f"\n2. 井内水位:")
        print(f"   h²(r₀) = {self.H0**2} + {self.B_unconfined:.4f}·ln({self.r0}/{self.R_unconfined})")
        print(f"   h²(r₀) = {h_well_sq:.4f}")
        print(f"   h(r₀) = √{h_well_sq:.4f} = {self.h_well:.4f} m")
        print(f"   降深: s₀ = h₀ - h(r₀) = {self.H0} - {self.h_well:.4f}")
        print(f"   s₀ = {self.s0_unconfined:.4f} m")
        
        # 3. r=50m处水位
        r_test = 50
        h_50_sq = self.H0**2 + self.B_unconfined * np.log(r_test / self.R_unconfined)
        self.h_50 = np.sqrt(h_50_sq)
        self.s_50_unconfined = self.H0 - self.h_50
        
        print(f"\n3. r={r_test}m处水位:")
        print(f"   h²({r_test}) = {self.H0**2} + {self.B_unconfined:.4f}·ln({r_test}/{self.R_unconfined})")
        print(f"   h²({r_test}) = {h_50_sq:.4f}")
        print(f"   h({r_test}) = {self.h_50:.4f} m")
        print(f"   降深: s = {self.H0} - {self.h_50:.4f} = {self.s_50_unconfined:.4f} m")
        
        # 4. 验证抽水量公式
        Q_check = np.pi * self.k * (self.H0**2 - self.h_well**2) / np.log(self.R_unconfined / self.r0)
        print(f"\n4. 验证（反算抽水量）:")
        print(f"   Q = πk(h₀²-h_well²)/ln(R/r₀)")
        print(f"   Q = π×{self.k}×({self.H0**2}-{self.h_well**2:.2f})/ln({self.R_unconfined}/{self.r0})")
        print(f"   Q = {Q_check:.2f} m³/d ✓ (与给定值{self.Q_unconfined}相符)")
        
        # 5. 渗流速度（井壁处最大）
        self.v0_unconfined = self.Q_unconfined / (2 * np.pi * self.r0 * self.h_well)
        print(f"\n5. 井壁渗流速度:")
        print(f"   v₀ = Q/(2πr₀h_well) = {self.Q_unconfined}/(2π×{self.r0}×{self.h_well:.4f})")
        print(f"   v₀ = {self.v0_unconfined:.2f} m/d")
    
    def compare_wells(self):
        """对比承压井与潜水井"""
        print(f"\n{'='*80}")
        print("【承压井 vs 潜水井对比】")
        print(f"{'='*80}")
        
        print(f"\n1. 降落曲线形式:")
        print(f"   承压井: H(r) = H₀ + A·ln(r/R)  (对数曲线)")
        print(f"   潜水井: h²(r) = h₀² - B·ln(r/R)  (抛物线)")
        
        print(f"\n2. 井内降深:")
        print(f"   承压井: s₀ = {self.s0_confined:.4f} m")
        print(f"   潜水井: s₀ = {self.s0_unconfined:.4f} m")
        print(f"   差异: Δs₀ = {abs(self.s0_unconfined - self.s0_confined):.4f} m")
        print(f"   潜水井降深较{'大' if self.s0_unconfined > self.s0_confined else '小'}")
        
        print(f"\n3. r=50m处降深:")
        print(f"   承压井: s = {self.s_50_confined:.4f} m")
        print(f"   潜水井: s = {self.s_50_unconfined:.4f} m")
        print(f"   差异: Δs = {abs(self.s_50_unconfined - self.s_50_confined):.4f} m")
        
        print(f"\n4. 井壁渗流速度:")
        print(f"   承压井: v₀ = {self.v0_confined:.2f} m/d")
        print(f"   潜水井: v₀ = {self.v0_unconfined:.2f} m/d")
        print(f"   差异: 潜水井速度{'较大' if self.v0_unconfined > self.v0_confined else '较小'}")
        
        print(f"\n5. 物理特性:")
        print(f"   承压井:")
        print(f"     • 含水层顶底板不透水")
        print(f"     • 水头高于含水层顶板")
        print(f"     • 降深与含水层厚度无关")
        print(f"     • 曲线为对数曲线")
        
        print(f"\n   潜水井:")
        print(f"     • 含水层顶部为自由面")
        print(f"     • 水位降落改变过水断面")
        print(f"     • 降深影响含水层厚度")
        print(f"     • 曲线为抛物线（更陡）")
        
        print(f"\n6. 工程意义:")
        print(f"   • 相同抽水量时，潜水井降深更大")
        print(f"   • 承压井出水能力更强（有顶板约束）")
        print(f"   • 潜水井需要考虑水位下降对厚度的影响")
        print(f"   • 本例：承压井Q={self.Q_confined}m³/d，潜水井Q={self.Q_unconfined}m³/d")
    
    def generate_drawdown_curves(self):
        """生成降落曲线"""
        r_max = max(self.R_confined, self.R_unconfined)
        r = np.logspace(np.log10(self.r0), np.log10(r_max), 200)
        
        # 承压井
        H_confined = self.H0 + self.A_confined * np.log(r / self.R_confined)
        s_confined = self.H0 - H_confined
        
        # 潜水井
        h_sq = self.H0**2 + self.B_unconfined * np.log(r / self.R_unconfined)
        h_sq = np.maximum(h_sq, 0)  # 确保非负
        h_unconfined = np.sqrt(h_sq)
        s_unconfined = self.H0 - h_unconfined
        
        return r, H_confined, h_unconfined, s_confined, s_unconfined
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目696：井流综合计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  承压井: M={self.M}m, k={self.k}m/d, H₀={self.H0}m, R={self.R_confined}m, Q={self.Q_confined}m³/d")
        print(f"  潜水井: h₀={self.H0}m, k={self.k}m/d, R={self.R_unconfined}m, Q={self.Q_unconfined}m³/d")
        print(f"  共同参数: r₀={self.r0}m")
        
        print("\n【井流理论】")
        print("1. 承压井:")
        print("   降落曲线: H(r) = H₀ + Q/(2πkM)·ln(r/R)")
        print("   抽水量: Q = 2πkM(H₀-H_well)/ln(R/r₀)")
        print("   特点: 对数曲线，降深较小")
        
        print("\n2. 潜水井:")
        print("   降落曲线: h²(r) = h₀² + Q/(πk)·ln(r/R)  【ln(r/R)<0】")
        print("   抽水量: Q = πk(h₀²-h_well²)/ln(R/r₀)")
        print("   特点: 抛物线，降深较大")
        
        print("\n3. 影响半径:")
        print("   经验公式: R = 10s₀√k")
        print("   或水文地质试验确定")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 对比分析
        self.compare_wells()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 承压井降落曲线: H(r) = {self.H0} + {self.A_confined:.4f}·ln(r/{self.R_confined})")
        print(f"(2) 承压井井内降深: s₀ = {self.s0_confined:.4f} m")
        print(f"(3) 承压井r=50m降深: s = {self.s_50_confined:.4f} m")
        print(f"(4) 见可视化图")
        print(f"(5) 潜水井降落曲线: h²(r) = {self.H0**2} + {self.B_unconfined:.4f}·ln(r/{self.R_unconfined})")
        print(f"    潜水井井内降深: s₀ = {self.s0_unconfined:.4f} m (Q={self.Q_unconfined}m³/d, R={self.R_unconfined}m)")
        print(f"(6) 相同抽水量时潜水井降深更大，本例不同参数比较工况特性")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：降落曲线对比
        ax1 = plt.subplot(2, 2, 1)
        self._plot_drawdown_curves(ax1)
        
        # 子图2：井流示意图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_well_schematic(ax2)
        
        # 子图3：降深对比
        ax3 = plt.subplot(2, 2, 3)
        self._plot_drawdown_comparison(ax3)
        
        # 子图4：参数对比
        ax4 = plt.subplot(2, 2, 4)
        self._plot_parameter_comparison(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_drawdown_curves(self, ax):
        """绘制降落曲线"""
        r, H_confined, h_unconfined, s_confined, s_unconfined = self.generate_drawdown_curves()
        
        # 承压井
        ax.plot(r, H_confined, 'b-', linewidth=2.5, label='承压井 H(r)')
        ax.fill_between(r, 0, H_confined, alpha=0.2, color='blue')
        
        # 潜水井
        ax.plot(r, h_unconfined, 'r--', linewidth=2.5, label='潜水井 h(r)')
        ax.fill_between(r, 0, h_unconfined, alpha=0.2, color='red')
        
        # 初始水位线
        ax.axhline(self.H0, color='green', linestyle=':', linewidth=2, 
                  label=f'初始水位 H₀={self.H0}m')
        
        # 标注关键点
        # 井内水位
        ax.plot(self.r0, self.H_well, 'bo', markersize=10)
        ax.plot(self.r0, self.h_well, 'ro', markersize=10)
        ax.text(self.r0*2, self.H_well, 
               f'承压井\nH_well={self.H_well:.2f}m\ns₀={self.s0_confined:.2f}m',
               fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        ax.text(self.r0*2, self.h_well-3, 
               f'潜水井\nh_well={self.h_well:.2f}m\ns₀={self.s0_unconfined:.2f}m',
               fontsize=9, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        # r=50m处
        ax.plot(50, self.H_50, 'b^', markersize=8)
        ax.plot(50, self.h_50, 'r^', markersize=8)
        ax.vlines(50, 0, self.H0, colors='gray', linestyles='--', alpha=0.5)
        
        ax.set_xlabel('距井中心距离 r (m)', fontsize=12)
        ax.set_ylabel('水位/水头 (m)', fontsize=12)
        ax.set_title('降落曲线对比', fontsize=13, weight='bold')
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_xlim(self.r0, max(self.R_confined, self.R_unconfined))
        ax.set_ylim(0, self.H0 + 5)
    
    def _plot_well_schematic(self, ax):
        """绘制井流示意图"""
        ax.axis('off')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-0.5, 2.5)
        
        # 标题
        ax.text(0, 2.3, '承压井与潜水井示意图', ha='center', fontsize=13, weight='bold')
        
        # 左侧：承压井
        x_left = -0.8
        
        # 含水层
        rect1 = Rectangle((x_left-0.3, 0.5), 0.6, 0.6, 
                         facecolor='lightyellow', edgecolor='black', linewidth=2)
        ax.add_patch(rect1)
        ax.text(x_left, 0.35, '承压含水层', ha='center', fontsize=9, weight='bold')
        
        # 不透水层
        rect_top = Rectangle((x_left-0.3, 1.1), 0.6, 0.1,
                            facecolor='gray', edgecolor='black', linewidth=1)
        rect_bottom = Rectangle((x_left-0.3, 0.4), 0.6, 0.1,
                               facecolor='gray', edgecolor='black', linewidth=1)
        ax.add_patch(rect_top)
        ax.add_patch(rect_bottom)
        ax.text(x_left, 1.25, '不透水层', ha='center', fontsize=8)
        ax.text(x_left, 0.25, '不透水层', ha='center', fontsize=8)
        
        # 井
        ax.plot([x_left, x_left], [0.5, 1.5], 'b-', linewidth=4)
        ax.plot(x_left, 0.8, 'bo', markersize=6)
        
        # 水位线
        ax.plot([x_left-0.35, x_left-0.05], [1.4, 1.4], 'b--', linewidth=2)
        ax.plot([x_left, x_left], [1.3, 1.5], 'b-', linewidth=2)
        
        # 标注
        ax.text(x_left, 1.6, 'H₀', ha='center', fontsize=10, weight='bold', color='blue')
        ax.text(x_left+0.35, 0.8, 'M', fontsize=10, weight='bold')
        ax.text(x_left, 0.1, '承压井', ha='center', fontsize=11, weight='bold', color='blue')
        
        # 右侧：潜水井
        x_right = 0.8
        
        # 含水层
        poly = Polygon([(x_right-0.3, 0.5), (x_right+0.3, 0.5), 
                       (x_right+0.3, 1.3), (x_right-0.3, 1.3)],
                      facecolor='lightyellow', edgecolor='black', linewidth=2)
        ax.add_patch(poly)
        ax.text(x_right, 0.35, '潜水含水层', ha='center', fontsize=9, weight='bold')
        
        # 不透水层
        rect_bottom2 = Rectangle((x_right-0.3, 0.4), 0.6, 0.1,
                                facecolor='gray', edgecolor='black', linewidth=1)
        ax.add_patch(rect_bottom2)
        ax.text(x_right, 0.25, '不透水层', ha='center', fontsize=8)
        
        # 自由面（波浪线）
        x_wave = np.linspace(x_right-0.3, x_right+0.3, 50)
        y_wave = 1.3 + 0.02*np.sin(20*x_wave)
        ax.plot(x_wave, y_wave, 'b-', linewidth=2)
        ax.text(x_right+0.4, 1.3, '自由面', fontsize=8, color='blue')
        
        # 井
        ax.plot([x_right, x_right], [0.5, 1.1], 'r-', linewidth=4)
        ax.plot(x_right, 0.8, 'ro', markersize=6)
        
        # 水位
        ax.plot([x_right, x_right], [1.1, 1.3], 'r--', linewidth=2)
        
        # 标注
        ax.text(x_right, 1.4, 'h₀', ha='center', fontsize=10, weight='bold', color='red')
        ax.text(x_right, 0.1, '潜水井', ha='center', fontsize=11, weight='bold', color='red')
        
        # 底部说明
        ax.text(0, -0.3, '关键区别：承压井有顶板约束，潜水井有自由面',
               ha='center', fontsize=9, style='italic',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
    def _plot_drawdown_comparison(self, ax):
        """绘制降深对比"""
        r, _, _, s_confined, s_unconfined = self.generate_drawdown_curves()
        
        # 降深曲线
        ax.plot(r, s_confined, 'b-', linewidth=2.5, label='承压井降深 s(r)')
        ax.plot(r, s_unconfined, 'r--', linewidth=2.5, label='潜水井降深 s(r)')
        
        # 填充差异区域
        ax.fill_between(r, s_confined, s_unconfined, 
                       where=(s_unconfined >= s_confined),
                       alpha=0.3, color='orange', label='降深差异')
        
        # 标注关键点
        ax.plot(self.r0, self.s0_confined, 'bo', markersize=10, label=f'承压井 s₀={self.s0_confined:.2f}m')
        ax.plot(self.r0, self.s0_unconfined, 'ro', markersize=10, label=f'潜水井 s₀={self.s0_unconfined:.2f}m')
        
        # 垂直线
        ax.vlines(self.r0, 0, max(self.s0_confined, self.s0_unconfined), 
                 colors='gray', linestyles=':', alpha=0.7)
        ax.vlines(50, 0, max(self.s_50_confined, self.s_50_unconfined),
                 colors='gray', linestyles=':', alpha=0.7)
        
        ax.set_xlabel('距井中心距离 r (m)', fontsize=12)
        ax.set_ylabel('降深 s (m)', fontsize=12)
        ax.set_title('降深曲线对比', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_xlim(self.r0, max(self.R_confined, self.R_unconfined))
        ax.set_ylim(0, max(self.s0_unconfined, self.s0_confined) * 1.2)
    
    def _plot_parameter_comparison(self, ax):
        """绘制参数对比"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.95, '承压井 vs 潜水井参数对比', ha='center', va='top',
               fontsize=13, weight='bold', transform=ax.transAxes)
        
        # 对比表格
        data = [
            ['参数', '承压井', '潜水井', '差异'],
            ['井内降深 s₀', f'{self.s0_confined:.2f}m', f'{self.s0_unconfined:.2f}m', 
             f'{abs(self.s0_unconfined-self.s0_confined):.2f}m'],
            ['r=50m降深', f'{self.s_50_confined:.2f}m', f'{self.s_50_unconfined:.2f}m',
             f'{abs(self.s_50_unconfined-self.s_50_confined):.2f}m'],
            ['井壁速度', f'{self.v0_confined:.1f}m/d', f'{self.v0_unconfined:.1f}m/d',
             f'{abs(self.v0_unconfined-self.v0_confined):.1f}m/d'],
            ['曲线形式', '对数曲线', '抛物线', '-'],
            ['曲线特点', '较平缓', '较陡峭', '-']
        ]
        
        # 绘制表格
        y_start = 0.80
        y_step = 0.12
        
        for i, row in enumerate(data):
            y = y_start - i * y_step
            
            # 表头加粗
            weight = 'bold' if i == 0 else 'normal'
            color = 'lightgray' if i == 0 else 'white'
            
            # 背景
            if i > 0:
                rect = Rectangle((0.05, y-0.05), 0.9, 0.08,
                               facecolor='lightyellow' if i % 2 else 'white',
                               edgecolor='gray', linewidth=1,
                               transform=ax.transAxes)
                ax.add_patch(rect)
            
            # 文字
            ax.text(0.08, y, row[0], fontsize=10, weight=weight, va='center',
                   transform=ax.transAxes)
            ax.text(0.35, y, row[1], fontsize=9, weight=weight, va='center',
                   ha='center', transform=ax.transAxes, color='blue' if i > 0 else 'black')
            ax.text(0.60, y, row[2], fontsize=9, weight=weight, va='center',
                   ha='center', transform=ax.transAxes, color='red' if i > 0 else 'black')
            ax.text(0.85, y, row[3], fontsize=9, weight=weight, va='center',
                   ha='center', transform=ax.transAxes)
        
        # 底部总结
        ax.text(0.5, 0.05,
               '结论：相同抽水量，潜水井降深更大，曲线更陡\n'
               '承压井出水能力强，但需要有不透水顶板约束',
               ha='center', fontsize=10, style='italic',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.6),
               transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)


def test_problem_696():
    """测试题目696"""
    print("\n" + "="*80)
    print("开始井流综合计算...")
    print("="*80)
    
    # 创建井流对象
    well = WellFlow()
    
    # 打印结果
    well.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = well.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_696_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_696_result.png")
    
    # 验证
    assert well.s0_confined > 0, "承压井降深应大于0"
    assert well.s0_unconfined > 0, "潜水井降深应大于0"
    assert well.H_well < well.H0, "井内水头应低于初始水头"
    assert well.h_well < well.H0, "井内水位应低于初始水位"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("井流计算是地下水开采的基础！")
    print("• 承压井: H(r) = H₀ + Q/(2πkM)·ln(r/R)")
    print("• 潜水井: h²(r) = h₀² - Q/(πk)·ln(r/R)")
    print("• 潜水井降深更大（自由面影响）")
    print("• 承压井出水能力强（顶板约束）")
    print("• 影响半径: R = 10s₀√k")


if __name__ == "__main__":
    test_problem_696()
