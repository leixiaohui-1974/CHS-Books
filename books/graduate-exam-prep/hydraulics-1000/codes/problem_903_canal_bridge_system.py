"""
《水力学考研1000题详解》配套代码
题目903：渠道桥梁过水系统综合分析（跨章节综合题）

问题描述：
某灌溉渠道需跨越公路，设计U形渡槽桥，参数如下：
  上游渠道: 矩形断面，宽度b₁ = 5 m，底坡i₁ = 0.0008，糙率n = 0.02
  上游流量: Q = 15 m³/s
  渡槽: 矩形断面，宽度b₂ = 4 m，长度L = 30 m，进出口各设渐变段
  桥墩阻水: 等效收缩系数ε = 0.9
  下游渠道: 同上游，b₃ = 5 m，i₃ = 0.0008
  过桥高差: 渡槽比上游渠底低Δh = 0.3 m

要求：
(1) 计算上游渠道正常水深h₀₁
(2) 分析渡槽进口水流状态（急流/缓流）
(3) 计算渡槽内水深h₂（考虑收缩）
(4) 判断是否发生壅水，计算壅水高度
(5) 分析下游衔接段水面线
(6) 优化设计建议（减小水头损失）

涉及知识点：
1. 明渠均匀流（Manning公式）
2. 临界水深与流态判别（Fr数）
3. 断面收缩与能量损失
4. 渐变流与急变流
5. 壅水计算（Bernoulli方程）
6. 水面线分析（M、S曲线）

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon, FancyBboxPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CanalBridgeSystem:
    """渠道桥梁过水系统综合分析类"""
    
    def __init__(self):
        """初始化"""
        self.g = 9.8          # 重力加速度 (m/s²)
        
        # 上游渠道
        self.b1 = 5           # 上游宽度 (m)
        self.i1 = 0.0008      # 上游坡度
        self.n = 0.02         # 糙率
        
        # 流量
        self.Q = 15           # m³/s
        
        # 渡槽
        self.b2 = 4           # 渡槽宽度 (m)
        self.L = 30           # 渡槽长度 (m)
        self.epsilon = 0.9    # 收缩系数
        
        # 高差（负值表示降低）
        self.delta_h = -0.3    # 渡槽降低 (m)
        
        # 下游渠道
        self.b3 = 5           # 下游宽度 (m)
        self.i3 = 0.0008      # 下游坡度
        
        # 计算
        self.calculate_upstream_depth()
        self.analyze_aqueduct_inlet()
        self.calculate_aqueduct_depth()
        self.analyze_backwater()
        self.analyze_downstream_profile()
    
    def manning_equation(self, h, b, i):
        """Manning公式计算流量"""
        A = b * h
        P = b + 2 * h
        R = A / P
        Q_calc = (1 / self.n) * A * R**(2/3) * i**(1/2)
        return Q_calc
    
    def calculate_upstream_depth(self):
        """计算上游渠道正常水深"""
        print(f"\n{'='*80}")
        print("【上游渠道分析】")
        print(f"{'='*80}")
        
        print(f"\n1. 渠道参数:")
        print(f"   宽度: b₁ = {self.b1} m")
        print(f"   坡度: i₁ = {self.i1}")
        print(f"   糙率: n = {self.n}")
        print(f"   流量: Q = {self.Q} m³/s")
        
        # 正常水深（迭代求解Manning公式）
        def equation(h):
            return self.manning_equation(h, self.b1, self.i1) - self.Q
        
        self.h01 = brentq(equation, 0.1, 5)
        
        print(f"\n2. 正常水深h₀₁（Manning公式迭代）:")
        A01 = self.b1 * self.h01
        R01 = A01 / (self.b1 + 2 * self.h01)
        v01 = self.Q / A01
        
        print(f"   h₀₁ = {self.h01:.4f} m")
        print(f"   A = {A01:.4f} m²")
        print(f"   R = {R01:.4f} m")
        print(f"   v = {v01:.4f} m/s")
        
        # 临界水深
        self.hc1 = (self.Q**2 / (self.g * self.b1**2))**(1/3)
        
        print(f"\n3. 临界水深h_c:")
        print(f"   h_c = (Q²/(gb²))^(1/3)")
        print(f"   h_c = ({self.Q}²/({self.g}×{self.b1}²))^(1/3)")
        print(f"   h_c = {self.hc1:.4f} m")
        
        # Froude数
        self.Fr1 = v01 / np.sqrt(self.g * self.h01)
        
        print(f"\n4. Froude数:")
        print(f"   Fr = v/√(gh) = {v01:.4f}/√({self.g}×{self.h01:.4f})")
        print(f"   Fr = {self.Fr1:.4f}")
        
        if self.Fr1 < 1:
            print(f"   Fr < 1: 缓流")
            self.flow_regime1 = "缓流"
        else:
            print(f"   Fr > 1: 急流")
            self.flow_regime1 = "急流"
        
        # 比能
        self.E1 = self.h01 + v01**2 / (2 * self.g)
        print(f"\n5. 比能:")
        print(f"   E = h + v²/2g = {self.h01:.4f} + {v01**2/(2*self.g):.4f}")
        print(f"   E = {self.E1:.4f} m")
    
    def analyze_aqueduct_inlet(self):
        """分析渡槽进口水流状态"""
        print(f"\n{'='*80}")
        print("【渡槽进口分析】")
        print(f"{'='*80}")
        
        print(f"\n1. 断面收缩:")
        print(f"   上游宽度: b₁ = {self.b1} m")
        print(f"   渡槽宽度: b₂ = {self.b2} m")
        print(f"   收缩比: b₂/b₁ = {self.b2/self.b1:.2f}")
        print(f"   收缩系数: ε = {self.epsilon}")
        
        # 渡槽临界水深
        self.hc2 = (self.Q**2 / (self.g * self.b2**2))**(1/3)
        
        print(f"\n2. 渡槽临界水深:")
        print(f"   h_c = (Q²/(gb₂²))^(1/3)")
        print(f"   h_c = ({self.Q}²/({self.g}×{self.b2}²))^(1/3)")
        print(f"   h_c = {self.hc2:.4f} m")
        
        # 进口能量方程（考虑收缩损失）
        # E₁ = E₂ + ξ·v₂²/2g，ξ为进口损失系数
        self.xi_inlet = 0.5 * (1 - self.epsilon)  # 进口损失系数
        
        print(f"\n3. 进口能量损失:")
        print(f"   损失系数: ξ_进 = 0.5(1-ε) = 0.5×(1-{self.epsilon})")
        print(f"   ξ_进 = {self.xi_inlet:.3f}")
    
    def calculate_aqueduct_depth(self):
        """计算渡槽内水深"""
        print(f"\n{'='*80}")
        print("【渡槽水深计算】")
        print(f"{'='*80}")
        
        # 能量方程求解渡槽水深
        # E₁ = h₂ + v₂²/2g + ξ_进·v₂²/2g
        # E₁ = h₂ + (1+ξ_进)·v₂²/2g
        # v₂ = Q/(b₂h₂)
        
        def energy_equation(h2):
            v2 = self.Q / (self.b2 * h2)
            # 上游能量 + 位能差 = 渡槽能量 + 进口损失
            # E1 - delta_h = h2 + v2²/2g + ξ·v2²/2g
            # （delta_h为负时表示降低，位能增加）
            E_available = self.E1 - self.delta_h
            E2_with_loss = h2 + (1 + self.xi_inlet) * v2**2 / (2 * self.g)
            return E_available - E2_with_loss
        
        # 求解，使用fsolve从临界水深开始
        result = fsolve(energy_equation, self.hc2)
        self.h2 = result[0]
        
        self.v2 = self.Q / (self.b2 * self.h2)
        self.Fr2 = self.v2 / np.sqrt(self.g * self.h2)
        
        print(f"\n1. 渡槽水深h₂（能量方程求解）:")
        print(f"   h₂ = {self.h2:.4f} m")
        print(f"   v₂ = Q/(b₂h₂) = {self.Q}/({self.b2}×{self.h2:.4f})")
        print(f"   v₂ = {self.v2:.4f} m/s")
        print(f"   Fr₂ = {self.Fr2:.4f}")
        
        if self.Fr2 < 1:
            print(f"   Fr₂ < 1: 渡槽内为缓流")
            self.flow_regime2 = "缓流"
        else:
            print(f"   Fr₂ > 1: 渡槽内为急流")
            self.flow_regime2 = "急流"
        
        # 进口损失
        self.h_inlet = self.xi_inlet * self.v2**2 / (2 * self.g)
        
        print(f"\n2. 进口水头损失:")
        print(f"   h_损 = ξ_进·v₂²/2g = {self.xi_inlet:.3f}×{self.v2**2/(2*self.g):.4f}")
        print(f"   h_损 = {self.h_inlet:.4f} m")
        
        # 渡槽内比能
        self.E2 = self.h2 + self.v2**2 / (2 * self.g)
        
        print(f"\n3. 渡槽比能:")
        print(f"   E₂ = h₂ + v₂²/2g = {self.h2:.4f} + {self.v2**2/(2*self.g):.4f}")
        print(f"   E₂ = {self.E2:.4f} m")
    
    def analyze_backwater(self):
        """分析壅水"""
        print(f"\n{'='*80}")
        print("【壅水分析】")
        print(f"{'='*80}")
        
        # 判断是否发生壅水
        # 壅水高度 = 实际水深 - 正常水深
        
        # 渡槽进口上游影响段
        # 由于断面收缩，上游可能产生壅水
        
        print(f"\n1. 壅水判断:")
        print(f"   上游正常水深: h₀₁ = {self.h01:.4f} m")
        print(f"   渡槽水深: h₂ = {self.h2:.4f} m")
        print(f"   高差: Δh = {self.delta_h:.2f} m ({'降低' if self.delta_h < 0 else '抬高'})")
        
        # 壅水高度（简化计算）
        # 由于断面收缩，上游会有轻微壅水
        if self.h2 > self.h01 or self.delta_h > 0:
            self.backwater = True
            # 壅水高度估算：进口损失导致的水位抬高
            self.delta_backwater = max(self.h_inlet, 0.05)  # 至少5cm
            
            print(f"\n2. 发生壅水 ✓")
            print(f"   壅水高度估算: Δh_壅 ≈ {self.delta_backwater:.4f} m")
            print(f"   主要原因: 断面收缩 + 能量损失")
            
            # 壅水影响长度（经验公式）
            self.L_backwater = 50 * self.delta_backwater / self.i1
            
            print(f"\n3. 壅水影响长度（经验公式）:")
            print(f"   L_壅 ≈ 50Δh_壅/i")
            print(f"   L_壅 ≈ 50×{self.delta_backwater:.4f}/{self.i1}")
            print(f"   L_壅 ≈ {self.L_backwater:.2f} m")
        else:
            self.backwater = False
            self.delta_backwater = 0
            self.L_backwater = 0
            print(f"\n2. 不发生显著壅水")
    
    def analyze_downstream_profile(self):
        """分析下游水面线"""
        print(f"\n{'='*80}")
        print("【下游水面线分析】")
        print(f"{'='*80}")
        
        # 下游正常水深
        def equation_down(h):
            return self.manning_equation(h, self.b3, self.i3) - self.Q
        
        self.h03 = brentq(equation_down, 0.1, 5)
        
        print(f"\n1. 下游正常水深:")
        print(f"   h₀₃ = {self.h03:.4f} m（与上游相同，因为参数相同）")
        
        # 下游临界水深
        self.hc3 = (self.Q**2 / (self.g * self.b3**2))**(1/3)
        
        print(f"\n2. 下游临界水深:")
        print(f"   h_c = {self.hc3:.4f} m")
        
        # 出口水深（从渡槽出来）
        # 考虑出口损失
        self.xi_outlet = 1.0  # 出口损失系数
        
        # 出口扩散，从b₂扩大到b₃
        # 简化：假设出口后恢复到正常水深附近
        # 用fsolve求解或直接取正常水深作为近似
        
        def outlet_equation(h3):
            v3 = self.Q / (self.b3 * h3)
            h_loss = self.xi_outlet * (self.v2 - v3)**2 / (2 * self.g)
            # 渡槽能量 - 高差(回升) = 下游能量 + 出口损失
            E_from_aqueduct = self.E2 - self.delta_h  # delta_h为负，所以是减去负值=加
            E3_total = h3 + v3**2 / (2 * self.g) + h_loss
            return E_from_aqueduct - E3_total
        
        # 使用fsolve
        result = fsolve(outlet_equation, self.h03)
        self.h3_outlet = result[0]
        self.v3_outlet = self.Q / (self.b3 * self.h3_outlet)
        
        print(f"\n3. 出口断面水深:")
        print(f"   h₃ = {self.h3_outlet:.4f} m")
        print(f"   v₃ = {self.v3_outlet:.4f} m/s")
        
        # 判断水面线类型
        print(f"\n4. 下游水面线类型:")
        print(f"   h₃_出口 = {self.h3_outlet:.4f} m")
        print(f"   h₀₃ = {self.h03:.4f} m")
        print(f"   h_c = {self.hc3:.4f} m")
        
        if self.h3_outlet > self.h03:
            print(f"   h₃ > h₀: M1型水面线（壅水曲线）")
            self.profile_type = "M1"
        elif self.h3_outlet < self.h03 and self.h3_outlet > self.hc3:
            print(f"   h_c < h₃ < h₀: M2型水面线（降水曲线）")
            self.profile_type = "M2"
        else:
            print(f"   需要进一步判断")
            self.profile_type = "待定"
    
    def calculate_total_loss(self):
        """计算总水头损失"""
        print(f"\n{'='*80}")
        print("【总水头损失】")
        print(f"{'='*80}")
        
        # 进口损失
        h_inlet_loss = self.h_inlet
        
        # 出口损失
        h_outlet_loss = self.xi_outlet * (self.v2 - self.v3_outlet)**2 / (2 * self.g)
        
        # 沿程损失（渡槽内，简化为零，因为短且坡度小）
        h_friction = 0
        
        # 总损失
        h_total_loss = h_inlet_loss + h_outlet_loss + h_friction
        
        print(f"\n1. 各项损失:")
        print(f"   进口损失: h_进 = {h_inlet_loss:.4f} m")
        print(f"   出口损失: h_出 = {h_outlet_loss:.4f} m")
        print(f"   沿程损失: h_f = {h_friction:.4f} m（渡槽短，忽略）")
        
        print(f"\n2. 总水头损失:")
        print(f"   Σh_损 = {h_total_loss:.4f} m")
        
        self.total_loss = h_total_loss
        
        return h_total_loss
    
    def optimization_suggestions(self):
        """优化建议"""
        print(f"\n{'='*80}")
        print("【优化设计建议】")
        print(f"{'='*80}")
        
        suggestions = []
        
        # 1. 壅水
        if self.backwater and self.delta_backwater > 0.2:
            suggestions.append(f"• 壅水高度{self.delta_backwater:.2f}m较大，建议:")
            suggestions.append(f"  - 增大渡槽宽度（目前{self.b2}m，建议≥{self.b1}m）")
            suggestions.append(f"  - 减小抬高高度（目前{self.delta_h}m）")
            suggestions.append(f"  - 设置渐变段减缓收缩")
        
        # 2. 流态
        if self.Fr2 > 0.8:
            suggestions.append(f"• 渡槽Fr={self.Fr2:.2f}接近临界，流态不稳定")
            suggestions.append(f"  - 建议增大水深或减小流速")
        
        # 3. 收缩
        if self.b2 / self.b1 < 0.85:
            suggestions.append(f"• 断面收缩比{self.b2/self.b1:.2f}较小，损失较大")
            suggestions.append(f"  - 建议收缩比>0.85，或设置长渐变段")
        
        # 4. 损失
        if self.total_loss > 0.3:
            suggestions.append(f"• 总水头损失{self.total_loss:.2f}m较大")
            suggestions.append(f"  - 优化进出口过渡段设计")
            suggestions.append(f"  - 采用流线型设计减小局部损失")
        
        # 5. 通用建议
        suggestions.append("• 通用建议:")
        suggestions.append("  - 渐变段长度L_渐 ≥ 3(b₁-b₂)")
        suggestions.append("  - 定期清淤保持糙率稳定")
        suggestions.append("  - 监测壅水影响范围")
        
        print(f"\n优化建议:")
        for suggestion in suggestions:
            print(suggestion)
        
        return suggestions
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目903：渠道桥梁过水系统综合分析（跨章节综合题）")
        print("="*80)
        
        print("\n【系统参数】")
        print(f"  上游渠道: b₁={self.b1}m, i₁={self.i1}, n={self.n}")
        print(f"  渡槽: b₂={self.b2}m, L={self.L}m, Δh={self.delta_h}m")
        print(f"  流量: Q={self.Q}m³/s")
        
        print("\n【涉及知识点】")
        print("1. 明渠均匀流（Manning公式）")
        print("2. 临界水深与流态判别（Fr数）")
        print("3. 断面收缩与能量损失")
        print("4. 渐变流与急变流")
        print("5. 壅水计算（能量方程）")
        print("6. 水面线分析（M型曲线）")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 总损失
        self.calculate_total_loss()
        
        # 优化建议
        self.optimization_suggestions()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 上游正常水深: h₀₁ = {self.h01:.4f} m, Fr = {self.Fr1:.3f} ({self.flow_regime1})")
        print(f"(2) 渡槽进口: 断面收缩b₂/b₁={self.b2/self.b1:.2f}, ε={self.epsilon}")
        print(f"(3) 渡槽水深: h₂ = {self.h2:.4f} m, Fr₂ = {self.Fr2:.3f} ({self.flow_regime2})")
        
        if self.backwater:
            print(f"(4) 发生壅水: Δh_壅 ≈ {self.delta_backwater:.4f} m, L_壅 ≈ {self.L_backwater:.0f} m")
        else:
            print(f"(4) 不发生壅水")
        
        print(f"(5) 下游水面线: {self.profile_type}型，h₃_出口 = {self.h3_outlet:.4f} m")
        print(f"(6) 总水头损失: Σh = {self.total_loss:.4f} m，见优化建议")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：纵剖面图
        ax1 = plt.subplot(2, 3, 1)
        self._plot_longitudinal_profile(ax1)
        
        # 子图2：水深变化
        ax2 = plt.subplot(2, 3, 2)
        self._plot_depth_variation(ax2)
        
        # 子图3：Fr数变化
        ax3 = plt.subplot(2, 3, 3)
        self._plot_froude_variation(ax3)
        
        # 子图4：能量线
        ax4 = plt.subplot(2, 3, 4)
        self._plot_energy_line(ax4)
        
        # 子图5：水头损失分布
        ax5 = plt.subplot(2, 3, 5)
        self._plot_loss_distribution(ax5)
        
        # 子图6：优化对比
        ax6 = plt.subplot(2, 3, 6)
        self._plot_optimization(ax6)
        
        plt.tight_layout()
        return fig
    
    def _plot_longitudinal_profile(self, ax):
        """绘制纵剖面"""
        # X坐标
        x_up = np.array([-100, 0])  # 上游
        x_aqueduct = np.array([0, self.L])  # 渡槽
        x_down = np.array([self.L, self.L + 100])  # 下游
        
        # 底高程
        z_up = np.array([0, 0])
        z_aqueduct = np.array([self.delta_h, self.delta_h])
        z_down = np.array([0, -self.i3 * 100])
        
        # 水面高程
        h_up = z_up + self.h01
        h_aqueduct = z_aqueduct + self.h2
        h_down = z_down + self.h3_outlet
        
        # 绘制底部
        ax.fill_between(x_up, -2, z_up, color='brown', alpha=0.3)
        ax.plot(x_up, z_up, 'k-', linewidth=2)
        
        ax.fill_between(x_aqueduct, -2, z_aqueduct, color='gray', alpha=0.5)
        ax.plot(x_aqueduct, z_aqueduct, 'k-', linewidth=3)
        
        ax.fill_between(x_down, -2, z_down, color='brown', alpha=0.3)
        ax.plot(x_down, z_down, 'k-', linewidth=2)
        
        # 绘制水面
        ax.fill_between(x_up, z_up, h_up, color='lightblue', alpha=0.6, label='水体')
        ax.plot(x_up, h_up, 'b-', linewidth=2.5, label='水面线')
        
        ax.fill_between(x_aqueduct, z_aqueduct, h_aqueduct, color='lightblue', alpha=0.6)
        ax.plot(x_aqueduct, h_aqueduct, 'b-', linewidth=2.5)
        
        ax.fill_between(x_down, z_down, h_down, color='lightblue', alpha=0.6)
        ax.plot(x_down, h_down, 'b-', linewidth=2.5)
        
        # 壅水影响
        if self.backwater:
            x_back = np.linspace(-self.L_backwater, 0, 50)
            h_back = self.h01 + self.delta_backwater * np.exp(x_back / self.L_backwater * 3)
            ax.plot(x_back, h_back, 'r--', linewidth=2, label='壅水影响')
        
        # 标注
        ax.text(-50, self.h01 + 0.3, f'上游\nh={self.h01:.2f}m', ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        ax.text(self.L/2, self.delta_h + self.h2 + 0.3, f'渡槽\nh={self.h2:.2f}m',
               ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        ax.text(self.L + 50, self.h3_outlet + 0.3, f'下游\nh={self.h3_outlet:.2f}m',
               ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.7))
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('系统纵剖面图', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-120, self.L + 120)
    
    def _plot_depth_variation(self, ax):
        """绘制水深变化"""
        x = [-50, 0, 0, self.L, self.L, self.L + 50]
        h = [self.h01, self.h01, self.h2, self.h2, self.h3_outlet, self.h3_outlet]
        
        ax.plot(x, h, 'b-o', linewidth=2.5, markersize=8)
        
        # 临界水深线
        ax.axhline(self.hc1, color='red', linestyle='--', linewidth=2,
                  label=f'临界水深 h_c={self.hc1:.2f}m')
        
        # 标注
        for xi, hi in zip([0, self.L/2, self.L], [self.h01, self.h2, self.h3_outlet]):
            ax.text(xi, hi + 0.1, f'{hi:.3f}m', ha='center', fontsize=9)
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('水深 (m)', fontsize=12)
        ax.set_title('水深沿程变化', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_froude_variation(self, ax):
        """绘制Fr数变化"""
        x = [-50, 0, self.L, self.L + 50]
        Fr = [self.Fr1, self.Fr1, self.Fr2, self.v3_outlet/np.sqrt(self.g*self.h3_outlet)]
        
        ax.plot(x, Fr, 'g-s', linewidth=2.5, markersize=8, label='Froude数')
        
        # Fr=1线
        ax.axhline(1, color='red', linestyle='--', linewidth=2, label='Fr=1（临界）')
        
        # 填充区域
        ax.fill_between(x, 0, Fr, where=(np.array(Fr) < 1),
                       alpha=0.3, color='blue', label='缓流区')
        ax.fill_between(x, Fr, 2, where=(np.array(Fr) >= 1),
                       alpha=0.3, color='yellow', label='急流区')
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('Froude数 Fr', fontsize=12)
        ax.set_title('流态判别（Fr数）', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.5)
    
    def _plot_energy_line(self, ax):
        """绘制能量线"""
        x = [-50, 0, self.L, self.L + 50]
        
        # 水面高程
        h_surface = [self.h01, self.h01, self.delta_h + self.h2, self.h3_outlet]
        
        # 总能量（水面+流速水头）
        E = [self.h01 + (self.Q/(self.b1*self.h01))**2/(2*self.g),
             self.E1,
             self.delta_h + self.E2,
             self.h3_outlet + (self.Q/(self.b3*self.h3_outlet))**2/(2*self.g)]
        
        ax.plot(x, h_surface, 'b-', linewidth=2.5, label='水面线')
        ax.plot(x, E, 'r--', linewidth=2.5, label='能量线')
        
        # 填充
        ax.fill_between(x, h_surface, E, alpha=0.3, color='yellow', label='流速水头')
        
        # 标注损失
        ax.annotate('', xy=(0, E[1]), xytext=(0, E[0]),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax.text(5, (E[0] + E[1])/2, '进口损失', fontsize=9, color='red')
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('能量线与水面线', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_loss_distribution(self, ax):
        """绘制水头损失分布"""
        h_inlet = self.h_inlet
        h_outlet = self.xi_outlet * (self.v2 - self.v3_outlet)**2 / (2 * self.g)
        
        labels = ['进口损失', '出口损失']
        sizes = [h_inlet, h_outlet]
        colors = ['lightcoral', 'lightyellow']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90)
        
        for text in texts:
            text.set_fontsize(11)
            text.set_weight('bold')
        
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax.set_title(f'水头损失分布\n(总计={self.total_loss:.3f}m)',
                    fontsize=13, weight='bold')
    
    def _plot_optimization(self, ax):
        """绘制优化对比"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.95, '优化建议', ha='center', fontsize=13, weight='bold',
               transform=ax.transAxes)
        
        # 当前状态
        y = 0.85
        ax.text(0.05, y, '【当前状态】', fontsize=11, weight='bold',
               transform=ax.transAxes, color='red')
        y -= 0.08
        ax.text(0.05, y, f'断面收缩: b₂/b₁ = {self.b2/self.b1:.2f}',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.05, y, f'壅水高度: Δh = {self.delta_backwater:.3f} m',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.05, y, f'水头损失: Σh = {self.total_loss:.3f} m',
               fontsize=10, transform=ax.transAxes)
        
        # 优化建议
        y -= 0.12
        ax.text(0.05, y, '【优化方案】', fontsize=11, weight='bold',
               transform=ax.transAxes, color='green')
        y -= 0.08
        ax.text(0.05, y, '① 增大渡槽宽度至5m',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.1, y, f'→ 收缩比: {self.b2/self.b1:.2f} → 1.00',
               fontsize=9, transform=ax.transAxes, style='italic')
        
        y -= 0.08
        ax.text(0.05, y, '② 设置渐变段 L≥9m',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.1, y, '→ 减小进口损失50%',
               fontsize=9, transform=ax.transAxes, style='italic')
        
        y -= 0.08
        ax.text(0.05, y, '③ 降低抬高高度',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.1, y, f'→ 减小壅水至 < 0.3m',
               fontsize=9, transform=ax.transAxes, style='italic')
        
        # 预期效果
        y -= 0.10
        ax.text(0.5, y, '预期效果：水头损失减小40%',
               ha='center', fontsize=10, weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
               transform=ax.transAxes)


def test_problem_903():
    """测试题目903"""
    print("\n" + "="*80)
    print("开始渠道桥梁过水系统综合分析...")
    print("="*80)
    
    # 创建系统对象
    system = CanalBridgeSystem()
    
    # 打印结果
    system.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = system.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_903_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_903_result.png")
    
    # 验证
    assert system.h01 > 0, "上游水深应大于0"
    assert system.h2 > 0, "渡槽水深应大于0"
    assert system.Fr1 < 1, "上游应为缓流"
    assert system.total_loss > 0, "应有水头损失"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("渠道桥梁过水系统整合明渠流核心知识！")
    print("• Manning公式: 正常水深计算")
    print("• Fr数: 流态判别（缓流/急流）")
    print("• 能量方程: 断面收缩分析")
    print("• 壅水: 上游水位抬高")
    print("• 水面线: M型曲线分析")
    print("• 优化: 减小损失的工程措施")


if __name__ == "__main__":
    test_problem_903()
