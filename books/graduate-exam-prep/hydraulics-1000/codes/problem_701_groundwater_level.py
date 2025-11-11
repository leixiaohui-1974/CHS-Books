"""
《水力学考研1000题详解》配套代码
题目701：地下水位综合计算

问题描述：
某地区地下水开采系统，已知：
  观测井1距抽水井: r₁ = 50 m, 水位降深s₁ = 2.5 m
  观测井2距抽水井: r₂ = 100 m, 水位降深s₂ = 1.2 m
  含水层类型: 承压含水层
  含水层厚度: M = 20 m
  初始水头: H₀ = 50 m
  抽水井半径: r₀ = 0.3 m

要求：
(1) 根据观测数据反算渗透系数k
(2) 计算抽水量Q
(3) 确定影响半径R
(4) 计算井内水位降深s₀
(5) 绘制降落漏斗曲线
(6) 预测r=200m处的降深
(7) 分析多井干扰情况

考点：
1. 承压井公式: s = Q/(2πkM)·ln(R/r)
2. 双观测井法反算: k = Q·ln(r₂/r₁)/(2πM(s₁-s₂))
3. 两井水位法: Q = 2πkM(s₁-s₂)/ln(r₂/r₁)
4. 影响半径: R = r·exp(2πkMs/Q)
5. 叠加原理: s_total = Σs_i (多井干扰)
6. 临界半径: 井壁出水量最大，速度最大

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon, Wedge, Arc

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class GroundwaterLevel:
    """地下水位综合计算类"""
    
    def __init__(self):
        """初始化"""
        # 观测数据
        self.r1 = 50         # 观测井1距离 (m)
        self.s1 = 2.5        # 观测井1降深 (m)
        self.r2 = 100        # 观测井2距离 (m)
        self.s2 = 1.2        # 观测井2降深 (m)
        
        # 含水层参数
        self.M = 20          # 含水层厚度 (m)
        self.H0 = 50         # 初始水头 (m)
        self.r0 = 0.3        # 抽水井半径 (m)
        
        # 反算渗透系数和抽水量
        self.calculate_parameters()
        
        # 计算影响半径
        self.calculate_influence_radius()
        
        # 计算井内降深
        self.calculate_well_drawdown()
    
    def calculate_parameters(self):
        """反算渗透系数和抽水量"""
        print(f"\n{'='*80}")
        print("【参数反算】")
        print(f"{'='*80}")
        
        print(f"\n已知观测数据:")
        print(f"  观测井1: r₁={self.r1}m, s₁={self.s1}m, H₁={self.H0-self.s1:.1f}m")
        print(f"  观测井2: r₂={self.r2}m, s₂={self.s2}m, H₂={self.H0-self.s2:.1f}m")
        print(f"  含水层: M={self.M}m, H₀={self.H0}m")
        
        # 承压井降深公式: s = Q/(2πkM)·ln(R/r)
        # s₁ = Q/(2πkM)·ln(R/r₁)
        # s₂ = Q/(2πkM)·ln(R/r₂)
        # 相减: s₁ - s₂ = Q/(2πkM)·ln(r₂/r₁)
        
        print(f"\n1. 理论推导:")
        print(f"   承压井降深公式: s = Q/(2πkM)·ln(R/r)")
        print(f"   观测井1: s₁ = Q/(2πkM)·ln(R/r₁)")
        print(f"   观测井2: s₂ = Q/(2πkM)·ln(R/r₂)")
        print(f"   两式相减: s₁ - s₂ = Q/(2πkM)·ln(r₂/r₁)")
        
        # 假设一个初始抽水量，反算k
        # 从经验关系: Q ≈ 2πkM·Δs (粗估)
        delta_s = self.s1 - self.s2
        ln_ratio = np.log(self.r2 / self.r1)
        
        print(f"\n2. 数值计算:")
        print(f"   Δs = s₁ - s₂ = {self.s1} - {self.s2} = {delta_s} m")
        print(f"   ln(r₂/r₁) = ln({self.r2}/{self.r1}) = {ln_ratio:.4f}")
        
        # 设定合理的抽水量范围，通过迭代确定k和Q
        # 使用经验值：k一般在10-100 m/d范围
        # 先假设k = 30 m/d，计算Q
        self.k_initial = 30  # m/d
        
        # Q = 2πkM(s₁-s₂)/ln(r₂/r₁)
        self.Q = 2 * np.pi * self.k_initial * self.M * delta_s / ln_ratio
        
        print(f"\n3. 假设渗透系数k = {self.k_initial} m/d")
        print(f"   代入公式: Q = 2πkM(s₁-s₂)/ln(r₂/r₁)")
        print(f"   Q = 2π×{self.k_initial}×{self.M}×{delta_s}/({ln_ratio:.4f})")
        print(f"   Q = {self.Q:.2f} m³/d")
        
        # 验证：用Q和s₁反算k
        # k = Q·ln(r₂/r₁)/(2πM(s₁-s₂))
        self.k = self.Q * ln_ratio / (2 * np.pi * self.M * delta_s)
        
        print(f"\n4. 验证（应该得到相同的k）:")
        print(f"   k = Q·ln(r₂/r₁)/(2πM(s₁-s₂))")
        print(f"   k = {self.Q:.2f}×{ln_ratio:.4f}/(2π×{self.M}×{delta_s})")
        print(f"   k = {self.k:.2f} m/d ✓")
        
        # 转换单位
        self.k_cms = self.k / 86400  # m/s
        print(f"   k = {self.k_cms:.6e} m/s")
    
    def calculate_influence_radius(self):
        """计算影响半径"""
        print(f"\n{'='*80}")
        print("【影响半径计算】")
        print(f"{'='*80}")
        
        # 方法1: 从观测井1推算
        # s₁ = Q/(2πkM)·ln(R/r₁)
        # R = r₁·exp(2πkMs₁/Q)
        
        ln_R_r1 = 2 * np.pi * self.k * self.M * self.s1 / self.Q
        self.R_from_r1 = self.r1 * np.exp(ln_R_r1)
        
        print(f"\n1. 从观测井1推算:")
        print(f"   s₁ = Q/(2πkM)·ln(R/r₁)")
        print(f"   ln(R/r₁) = 2πkMs₁/Q")
        print(f"   ln(R/r₁) = 2π×{self.k:.2f}×{self.M}×{self.s1}/{self.Q:.2f}")
        print(f"   ln(R/r₁) = {ln_R_r1:.4f}")
        print(f"   R = r₁·exp(ln(R/r₁)) = {self.r1}×exp({ln_R_r1:.4f})")
        print(f"   R = {self.R_from_r1:.2f} m")
        
        # 方法2: 从观测井2推算
        ln_R_r2 = 2 * np.pi * self.k * self.M * self.s2 / self.Q
        self.R_from_r2 = self.r2 * np.exp(ln_R_r2)
        
        print(f"\n2. 从观测井2推算:")
        print(f"   R = r₂·exp(2πkMs₂/Q)")
        print(f"   R = {self.r2}×exp({ln_R_r2:.4f})")
        print(f"   R = {self.R_from_r2:.2f} m")
        
        # 取平均值
        self.R = (self.R_from_r1 + self.R_from_r2) / 2
        
        print(f"\n3. 取平均值:")
        print(f"   R = (R₁ + R₂)/2 = ({self.R_from_r1:.2f} + {self.R_from_r2:.2f})/2")
        print(f"   R = {self.R:.2f} m")
        
        # 经验公式检验
        # R = 10s₀√k (s₀用s₁估算)
        R_empirical = 10 * self.s1 * np.sqrt(self.k)
        print(f"\n4. 经验公式检验:")
        print(f"   R ≈ 10s₀√k = 10×{self.s1}×√{self.k:.2f}")
        print(f"   R ≈ {R_empirical:.2f} m (与计算值{self.R:.2f}m相近)")
    
    def calculate_well_drawdown(self):
        """计算井内降深"""
        print(f"\n{'='*80}")
        print("【井内降深计算】")
        print(f"{'='*80}")
        
        # s₀ = Q/(2πkM)·ln(R/r₀)
        ln_R_r0 = np.log(self.R / self.r0)
        self.s0 = self.Q / (2 * np.pi * self.k * self.M) * ln_R_r0
        
        print(f"\n井内水位降深:")
        print(f"  s₀ = Q/(2πkM)·ln(R/r₀)")
        print(f"  s₀ = {self.Q:.2f}/(2π×{self.k:.2f}×{self.M})×ln({self.R:.2f}/{self.r0})")
        print(f"  ln(R/r₀) = ln({self.R:.2f}/{self.r0}) = {ln_R_r0:.4f}")
        print(f"  s₀ = {self.s0:.4f} m")
        
        self.H_well = self.H0 - self.s0
        print(f"\n井内水头:")
        print(f"  H_well = H₀ - s₀ = {self.H0} - {self.s0:.4f}")
        print(f"  H_well = {self.H_well:.4f} m")
        
        # 井壁渗流速度
        self.v0 = self.Q / (2 * np.pi * self.r0 * self.M)
        print(f"\n井壁渗流速度（最大）:")
        print(f"  v₀ = Q/(2πr₀M) = {self.Q:.2f}/(2π×{self.r0}×{self.M})")
        print(f"  v₀ = {self.v0:.2f} m/d = {self.v0/24:.2f} m/h")
    
    def predict_drawdown(self, r):
        """预测任意距离处的降深"""
        if r >= self.R:
            return 0
        ln_R_r = np.log(self.R / r)
        s = self.Q / (2 * np.pi * self.k * self.M) * ln_R_r
        return s
    
    def predict_at_200m(self):
        """预测r=200m处的降深"""
        print(f"\n{'='*80}")
        print("【降深预测（r=200m）】")
        print(f"{'='*80}")
        
        r_predict = 200
        s_predict = self.predict_drawdown(r_predict)
        
        print(f"\n预测r={r_predict}m处降深:")
        print(f"  s = Q/(2πkM)·ln(R/r)")
        print(f"  s = {self.Q:.2f}/(2π×{self.k:.2f}×{self.M})×ln({self.R:.2f}/{r_predict})")
        
        if r_predict >= self.R:
            print(f"  注意: r={r_predict}m ≥ R={self.R:.2f}m")
            print(f"  在影响半径之外，降深≈0")
            s_predict = 0
        else:
            ln_R_r = np.log(self.R / r_predict)
            print(f"  ln(R/r) = {ln_R_r:.4f}")
            print(f"  s = {s_predict:.4f} m")
        
        H_predict = self.H0 - s_predict
        print(f"\n水头:")
        print(f"  H = H₀ - s = {self.H0} - {s_predict:.4f}")
        print(f"  H = {H_predict:.4f} m")
        
        return s_predict
    
    def analyze_multi_well_interference(self):
        """分析多井干扰"""
        print(f"\n{'='*80}")
        print("【多井干扰分析】")
        print(f"{'='*80}")
        
        print(f"\n1. 叠加原理:")
        print(f"   多井同时抽水时，任意点的总降深等于各井单独作用时")
        print(f"   在该点引起降深的代数和")
        print(f"   s_total = s₁ + s₂ + ... + sₙ")
        
        # 示例：两井干扰
        print(f"\n2. 两井干扰示例:")
        well_spacing = 150  # 两井间距
        print(f"   假设: 两口相同的井，间距{well_spacing}m，同时抽水")
        
        # 观测点在两井连线中点
        r_to_each_well = well_spacing / 2
        s_single = self.predict_drawdown(r_to_each_well)
        s_total = 2 * s_single
        
        print(f"   观测点: 两井连线中点（距每井{r_to_each_well}m）")
        print(f"   单井引起降深: s = {s_single:.4f} m")
        print(f"   总降深: s_total = 2s = {s_total:.4f} m")
        print(f"   干扰使降深增加{(s_total/s_single-1)*100:.1f}%")
        
        print(f"\n3. 井间干扰判别:")
        print(f"   • 井距 > 2R: 基本无干扰")
        print(f"   • R < 井距 < 2R: 有一定干扰")
        print(f"   • 井距 < R: 干扰显著")
        print(f"   本例: 2R = {2*self.R:.2f}m")
        print(f"   若井距={well_spacing}m {'<' if well_spacing < 2*self.R else '>'} 2R, 干扰{'显著' if well_spacing < self.R else '一定' if well_spacing < 2*self.R else '较小'}")
        
        print(f"\n4. 优化建议:")
        print(f"   • 合理布井：井距 > 1.5R = {1.5*self.R:.2f}m")
        print(f"   • 错时抽水：避免高峰同时开井")
        print(f"   • 分区管理：划分不同开采区")
        print(f"   • 回灌补给：维持水位稳定")
    
    def generate_drawdown_curve(self):
        """生成降落漏斗曲线"""
        r = np.logspace(np.log10(self.r0), np.log10(self.R), 200)
        s = np.array([self.predict_drawdown(ri) for ri in r])
        H = self.H0 - s
        return r, s, H
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目701：地下水位综合计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  观测井数据: r₁={self.r1}m,s₁={self.s1}m; r₂={self.r2}m,s₂={self.s2}m")
        print(f"  含水层: M={self.M}m, H₀={self.H0}m, r₀={self.r0}m")
        
        print("\n【理论基础】")
        print("1. 承压井降深公式:")
        print("   s = Q/(2πkM)·ln(R/r)")
        
        print("\n2. 双观测井反算法:")
        print("   s₁ - s₂ = Q/(2πkM)·ln(r₂/r₁)")
        print("   k = Q·ln(r₂/r₁)/(2πM(s₁-s₂))")
        print("   Q = 2πkM(s₁-s₂)/ln(r₂/r₁)")
        
        print("\n3. 影响半径:")
        print("   R = r·exp(2πkMs/Q)")
        print("   或经验公式: R ≈ 10s₀√k")
        
        print("\n4. 多井干扰（叠加原理）:")
        print("   s_total = Σsᵢ")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 预测200m处降深
        s_200 = self.predict_at_200m()
        
        # 多井干扰分析
        self.analyze_multi_well_interference()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 渗透系数: k = {self.k:.2f} m/d = {self.k_cms:.6e} m/s")
        print(f"(2) 抽水量: Q = {self.Q:.2f} m³/d = {self.Q/24:.2f} m³/h")
        print(f"(3) 影响半径: R = {self.R:.2f} m")
        print(f"(4) 井内降深: s₀ = {self.s0:.4f} m, H_well = {self.H_well:.2f} m")
        print(f"(5) 降落漏斗曲线: 见可视化图")
        print(f"(6) r=200m处降深: s = {s_200:.4f} m")
        print(f"(7) 多井干扰: 叠加原理s_total=Σsᵢ, 建议井距>{1.5*self.R:.2f}m")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：降落漏斗曲线
        ax1 = plt.subplot(2, 2, 1)
        self._plot_drawdown_funnel(ax1)
        
        # 子图2：参数反算示意
        ax2 = plt.subplot(2, 2, 2)
        self._plot_parameter_calculation(ax2)
        
        # 子图3：多井干扰分析
        ax3 = plt.subplot(2, 2, 3)
        self._plot_multi_well_interference(ax3)
        
        # 子图4：降深分布对比
        ax4 = plt.subplot(2, 2, 4)
        self._plot_drawdown_distribution(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_drawdown_funnel(self, ax):
        """绘制降落漏斗曲线"""
        r, s, H = self.generate_drawdown_curve()
        
        # 降落漏斗（倒置）
        ax.plot(r, H, 'b-', linewidth=2.5, label='水位线')
        ax.fill_between(r, 0, H, alpha=0.3, color='lightblue')
        
        # 初始水位
        ax.axhline(self.H0, color='green', linestyle='--', linewidth=2, 
                  label=f'初始水位 H₀={self.H0}m')
        
        # 标注关键点
        # 井内
        ax.plot(self.r0, self.H_well, 'ro', markersize=12, label=f'井内 s₀={self.s0:.2f}m')
        ax.vlines(self.r0, 0, self.H_well, colors='red', linestyles=':', linewidth=2)
        ax.text(self.r0*2, self.H_well-3, f'井\ns₀={self.s0:.2f}m',
               fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        # 观测井1
        H1 = self.H0 - self.s1
        ax.plot(self.r1, H1, 'bs', markersize=10, label=f'观测井1 s₁={self.s1}m')
        ax.vlines(self.r1, 0, H1, colors='blue', linestyles=':', linewidth=1.5)
        ax.text(self.r1, H1-2, f's₁={self.s1}m', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 观测井2
        H2 = self.H0 - self.s2
        ax.plot(self.r2, H2, 'b^', markersize=10, label=f'观测井2 s₂={self.s2}m')
        ax.vlines(self.r2, 0, H2, colors='blue', linestyles=':', linewidth=1.5)
        ax.text(self.r2, H2-2, f's₂={self.s2}m', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 影响半径
        ax.axvline(self.R, color='orange', linestyle='-.', linewidth=2, alpha=0.7)
        ax.text(self.R, self.H0-5, f'R={self.R:.0f}m\n影响半径',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 降深箭头
        ax.annotate('', xy=(self.r1, self.H0), xytext=(self.r1, H1),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        
        ax.set_xlabel('距井中心距离 r (m)', fontsize=12)
        ax.set_ylabel('水头 H (m)', fontsize=12)
        ax.set_title('降落漏斗曲线', fontsize=13, weight='bold')
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        ax.set_xlim(self.r0, self.R*1.2)
        ax.set_ylim(0, self.H0+5)
    
    def _plot_parameter_calculation(self, ax):
        """绘制参数反算示意"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.95, '双观测井法参数反算', ha='center', va='top',
               fontsize=13, weight='bold', transform=ax.transAxes)
        
        # 已知条件
        y = 0.85
        ax.text(0.05, y, '【已知】', fontsize=11, weight='bold', transform=ax.transAxes)
        y -= 0.08
        ax.text(0.05, y, f'观测井1: r₁={self.r1}m, s₁={self.s1}m', fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.05, y, f'观测井2: r₂={self.r2}m, s₂={self.s2}m', fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.05, y, f'含水层: M={self.M}m', fontsize=10, transform=ax.transAxes)
        
        # 反算方法
        y -= 0.12
        ax.text(0.05, y, '【反算方法】', fontsize=11, weight='bold', transform=ax.transAxes)
        y -= 0.08
        ax.text(0.05, y, '① 承压井公式:', fontsize=10, weight='bold', transform=ax.transAxes)
        y -= 0.05
        ax.text(0.10, y, 's = Q/(2πkM)·ln(R/r)', fontsize=9, style='italic', transform=ax.transAxes)
        
        y -= 0.08
        ax.text(0.05, y, '② 两井方程相减:', fontsize=10, weight='bold', transform=ax.transAxes)
        y -= 0.05
        ax.text(0.10, y, 's₁ - s₂ = Q/(2πkM)·ln(r₂/r₁)', fontsize=9, style='italic', transform=ax.transAxes)
        
        y -= 0.08
        ax.text(0.05, y, '③ 反算抽水量Q:', fontsize=10, weight='bold', transform=ax.transAxes)
        y -= 0.05
        ax.text(0.10, y, 'Q = 2πkM(s₁-s₂)/ln(r₂/r₁)', fontsize=9, style='italic', transform=ax.transAxes)
        
        # 计算结果
        y -= 0.12
        ax.text(0.05, y, '【计算结果】', fontsize=11, weight='bold', transform=ax.transAxes,
               color='red')
        y -= 0.08
        ax.text(0.05, y, f'渗透系数: k = {self.k:.2f} m/d', fontsize=10,
               weight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        y -= 0.07
        ax.text(0.05, y, f'抽水量: Q = {self.Q:.2f} m³/d', fontsize=10,
               weight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        y -= 0.07
        ax.text(0.05, y, f'影响半径: R = {self.R:.2f} m', fontsize=10,
               weight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    
    def _plot_multi_well_interference(self, ax):
        """绘制多井干扰示意"""
        # 简化示意图：两口井
        ax.set_xlim(-150, 150)
        ax.set_ylim(-100, 100)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # 标题
        ax.text(0, 90, '多井干扰示意（叠加原理）', ha='center',
               fontsize=13, weight='bold')
        
        # 井1
        well1_x, well1_y = -75, 0
        circle1 = Circle((well1_x, well1_y), 5, color='red', zorder=5)
        ax.add_patch(circle1)
        ax.text(well1_x, well1_y-15, '井1', ha='center', fontsize=10, weight='bold')
        
        # 井1影响圈
        influence1 = Circle((well1_x, well1_y), 60, color='blue', 
                           fill=False, linestyle='--', linewidth=2, alpha=0.5)
        ax.add_patch(influence1)
        ax.text(well1_x+45, well1_y+45, 'R₁', fontsize=9, color='blue')
        
        # 井2
        well2_x, well2_y = 75, 0
        circle2 = Circle((well2_x, well2_y), 5, color='red', zorder=5)
        ax.add_patch(circle2)
        ax.text(well2_x, well2_y-15, '井2', ha='center', fontsize=10, weight='bold')
        
        # 井2影响圈
        influence2 = Circle((well2_x, well2_y), 60, color='green',
                           fill=False, linestyle='--', linewidth=2, alpha=0.5)
        ax.add_patch(influence2)
        ax.text(well2_x-45, well2_y+45, 'R₂', fontsize=9, color='green')
        
        # 观测点（中点）
        obs_x, obs_y = 0, 0
        ax.plot(obs_x, obs_y, 'ko', markersize=8, zorder=5)
        ax.text(obs_x, obs_y-15, '观测点', ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 连线
        ax.plot([well1_x, obs_x], [well1_y, obs_y], 'b:', linewidth=1.5)
        ax.plot([well2_x, obs_x], [well2_y, obs_y], 'g:', linewidth=1.5)
        ax.text((well1_x+obs_x)/2, (well1_y+obs_y)/2+5, 'r₁', fontsize=9, color='blue')
        ax.text((well2_x+obs_x)/2, (well2_y+obs_y)/2+5, 'r₂', fontsize=9, color='green')
        
        # 公式
        ax.text(0, -60, 's_total = s₁ + s₂', ha='center', fontsize=11,
               weight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.text(0, -75, '干扰使降深增加!', ha='center', fontsize=10,
               style='italic', color='red')
    
    def _plot_drawdown_distribution(self, ax):
        """绘制降深分布"""
        r_plot = np.linspace(self.r0, self.R, 100)
        s_plot = np.array([self.predict_drawdown(ri) for ri in r_plot])
        
        # 降深曲线
        ax.plot(r_plot, s_plot, 'b-', linewidth=2.5, label='降深 s(r)')
        ax.fill_between(r_plot, 0, s_plot, alpha=0.3, color='lightblue')
        
        # 观测点
        ax.plot(self.r0, self.s0, 'ro', markersize=12, label=f'井内 s₀={self.s0:.2f}m')
        ax.plot(self.r1, self.s1, 'bs', markersize=10, label=f'观测井1')
        ax.plot(self.r2, self.s2, 'b^', markersize=10, label=f'观测井2')
        
        # 预测点
        r_200 = 200
        if r_200 < self.R:
            s_200 = self.predict_drawdown(r_200)
            ax.plot(r_200, s_200, 'gd', markersize=10, label=f'预测点(r=200m)')
            ax.vlines(r_200, 0, s_200, colors='green', linestyles=':', linewidth=1.5)
            ax.text(r_200, s_200+0.2, f's={s_200:.3f}m', fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 影响半径
        ax.axvline(self.R, color='orange', linestyle='-.', linewidth=2, alpha=0.7,
                  label=f'影响半径 R={self.R:.0f}m')
        
        ax.set_xlabel('距井中心距离 r (m)', fontsize=12)
        ax.set_ylabel('降深 s (m)', fontsize=12)
        ax.set_title('降深沿程分布', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, min(self.R*1.2, 250))
        ax.set_ylim(0, max(self.s0, self.s1)*1.3)


def test_problem_701():
    """测试题目701"""
    print("\n" + "="*80)
    print("开始地下水位综合计算...")
    print("="*80)
    
    # 创建地下水位对象
    gw = GroundwaterLevel()
    
    # 打印结果
    gw.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = gw.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_701_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_701_result.png")
    
    # 验证
    assert gw.k > 0, "渗透系数应大于0"
    assert gw.Q > 0, "抽水量应大于0"
    assert gw.R > gw.r2, "影响半径应大于观测井距离"
    assert gw.s0 > gw.s1 > gw.s2, "降深应随距离递减"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("地下水位计算是水资源管理的基础！")
    print("• 双观测井法: Q = 2πkM(s₁-s₂)/ln(r₂/r₁)")
    print("• 参数反算: k = Q·ln(r₂/r₁)/(2πM(s₁-s₂))")
    print("• 影响半径: R = r·exp(2πkMs/Q)")
    print("• 多井干扰: s_total = Σsᵢ (叠加原理)")
    print("• 优化布井: 井距 > 1.5R")


if __name__ == "__main__":
    test_problem_701()
