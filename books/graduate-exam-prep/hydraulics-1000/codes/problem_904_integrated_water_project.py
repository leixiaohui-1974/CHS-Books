"""
《水力学考研1000题详解》配套代码
题目904：综合水利工程系统分析（终极跨章节综合题）

问题描述：
某山区综合水利工程，包含多个子系统：

【系统1：引水隧洞】
  上游水库: 水位H₁ = 200 m
  隧洞: 长度L₁ = 5000 m，直径d₁ = 4 m，λ₁ = 0.018
  调压井: 位于隧洞出口

【系统2：压力钢管】
  钢管: 长度L₂ = 1000 m，直径d₂ = 3 m，λ₂ = 0.015
  下游厂房: 高程H₂ = 50 m

【系统3：尾水渠道】
  矩形断面: 宽度B = 10 m，坡度i = 0.001，糙率n = 0.02
  下游河流: 水位H₃ = 45 m

【系统4：厂房水轮机】
  设计流量: Q_design = 50 m³/s
  水轮机效率: η_t = 0.90
  发电机效率: η_g = 0.95

要求：
(1) 计算各段水头损失（隧洞、钢管、尾水）
(2) 计算水轮机有效水头H_net
(3) 计算装机容量（发电功率）
(4) 分析水击保护（关闭时间、压力上升）
(5) 计算尾水渠道正常水深
(6) 综合优化建议（提高效率、降低成本）

涉及知识点：
1. 长管水力计算（Darcy-Weisbach）
2. 水头损失分配（沿程+局部）
3. 水击计算（Joukowsky公式）
4. 明渠均匀流（Manning公式）
5. 水轮机与发电（能量转换）
6. 系统优化（技术经济分析）

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon, FancyBboxPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class IntegratedWaterProject:
    """综合水利工程系统分析类"""
    
    def __init__(self):
        """初始化"""
        self.g = 9.8          # 重力加速度 (m/s²)
        self.rho = 1000       # 水密度 (kg/m³)
        
        # 系统1：引水隧洞
        self.H1 = 200         # 上游水库水位 (m)
        self.L1 = 5000        # 隧洞长度 (m)
        self.d1 = 4           # 隧洞直径 (m)
        self.lambda1 = 0.018  # 沿程阻力系数
        
        # 系统2：压力钢管
        self.L2 = 1000        # 钢管长度 (m)
        self.d2 = 3           # 钢管直径 (m)
        self.lambda2 = 0.015  # 沿程阻力系数
        self.H2 = 50          # 厂房高程 (m)
        
        # 系统3：尾水渠道
        self.B = 10           # 渠道宽度 (m)
        self.i = 0.001        # 渠道坡度
        self.n = 0.02         # 糙率
        self.H3 = 45          # 下游河流水位 (m)
        
        # 系统4：水轮发电机组
        self.Q_design = 50    # 设计流量 (m³/s)
        self.eta_t = 0.90     # 水轮机效率
        self.eta_g = 0.95     # 发电机效率
        
        # 钢管参数（水击计算用）
        self.E_steel = 2.1e11  # 钢的弹性模量 (Pa)
        self.K_water = 2.1e9   # 水的体积弹性模量 (Pa)
        self.delta = 0.02      # 钢管壁厚 (m)
        
        # 计算
        self.calculate_head_losses()
        self.calculate_net_head()
        self.calculate_power()
        self.analyze_water_hammer()
        self.calculate_tailrace_depth()
        self.comprehensive_optimization()
    
    def calculate_head_losses(self):
        """计算各段水头损失"""
        print(f"\n{'='*80}")
        print("【水头损失计算】")
        print(f"{'='*80}")
        
        # 隧洞流速
        A1 = np.pi * (self.d1 / 2)**2
        self.v1 = self.Q_design / A1
        
        print(f"\n1. 引水隧洞:")
        print(f"   直径: d₁ = {self.d1} m")
        print(f"   流速: v₁ = Q/A = {self.Q_design}/{A1:.4f}")
        print(f"   v₁ = {self.v1:.4f} m/s")
        
        # 隧洞损失
        self.h_f1 = self.lambda1 * self.L1 / self.d1 * self.v1**2 / (2 * self.g)
        
        print(f"   沿程损失: h_f1 = λ(L/d)(v²/2g)")
        print(f"   h_f1 = {self.lambda1}×({self.L1}/{self.d1})×({self.v1:.4f}²/(2×{self.g}))")
        print(f"   h_f1 = {self.h_f1:.4f} m")
        
        # 钢管流速
        A2 = np.pi * (self.d2 / 2)**2
        self.v2 = self.Q_design / A2
        
        print(f"\n2. 压力钢管:")
        print(f"   直径: d₂ = {self.d2} m")
        print(f"   流速: v₂ = Q/A = {self.Q_design}/{A2:.4f}")
        print(f"   v₂ = {self.v2:.4f} m/s")
        
        # 钢管损失
        self.h_f2 = self.lambda2 * self.L2 / self.d2 * self.v2**2 / (2 * self.g)
        
        print(f"   沿程损失: h_f2 = λ(L/d)(v²/2g)")
        print(f"   h_f2 = {self.lambda2}×({self.L2}/{self.d2})×({self.v2:.4f}²/(2×{self.g}))")
        print(f"   h_f2 = {self.h_f2:.4f} m")
        
        # 总沿程损失
        self.h_f_total = self.h_f1 + self.h_f2
        
        print(f"\n3. 总沿程损失:")
        print(f"   h_f = h_f1 + h_f2")
        print(f"   h_f = {self.h_f1:.4f} + {self.h_f2:.4f}")
        print(f"   h_f = {self.h_f_total:.4f} m")
        
        # 局部损失（简化估算为沿程损失的10%）
        self.h_j_total = 0.1 * self.h_f_total
        
        print(f"\n4. 局部损失（估算为沿程损失10%）:")
        print(f"   h_j ≈ 0.1×h_f = {self.h_j_total:.4f} m")
    
    def calculate_net_head(self):
        """计算水轮机有效水头"""
        print(f"\n{'='*80}")
        print("【水轮机有效水头】")
        print(f"{'='*80}")
        
        # 毛水头
        self.H_gross = self.H1 - self.H2
        
        print(f"\n1. 毛水头（总水头）:")
        print(f"   H_总 = H₁ - H₂")
        print(f"   H_总 = {self.H1} - {self.H2}")
        print(f"   H_总 = {self.H_gross} m")
        
        # 净水头
        self.H_net = self.H_gross - self.h_f_total - self.h_j_total
        
        print(f"\n2. 净水头（有效水头）:")
        print(f"   H_净 = H_总 - h_f - h_j")
        print(f"   H_净 = {self.H_gross} - {self.h_f_total:.4f} - {self.h_j_total:.4f}")
        print(f"   H_净 = {self.H_net:.4f} m")
        
        # 水头利用率
        self.eta_head = self.H_net / self.H_gross
        
        print(f"\n3. 水头利用率:")
        print(f"   η_H = H_净/H_总 = {self.H_net:.4f}/{self.H_gross}")
        print(f"   η_H = {self.eta_head*100:.2f}%")
        
        if self.eta_head >= 0.95:
            print(f"   ✓ 水头利用率高（≥95%）")
        elif self.eta_head >= 0.90:
            print(f"   ✓ 水头利用率良好（90-95%）")
        else:
            print(f"   ⚠ 水头利用率偏低（<90%），建议优化管道")
    
    def calculate_power(self):
        """计算装机容量"""
        print(f"\n{'='*80}")
        print("【装机容量计算】")
        print(f"{'='*80}")
        
        # 水功率
        self.P_water = self.rho * self.g * self.Q_design * self.H_net / 1000  # kW
        
        print(f"\n1. 水功率:")
        print(f"   P_水 = ρgQH_净")
        print(f"   P_水 = {self.rho}×{self.g}×{self.Q_design}×{self.H_net:.4f}/1000")
        print(f"   P_水 = {self.P_water:.2f} kW = {self.P_water/1000:.2f} MW")
        
        # 水轮机输出功率
        self.P_turbine = self.P_water * self.eta_t
        
        print(f"\n2. 水轮机输出:")
        print(f"   P_轮 = P_水 × η_t")
        print(f"   P_轮 = {self.P_water:.2f} × {self.eta_t}")
        print(f"   P_轮 = {self.P_turbine:.2f} kW = {self.P_turbine/1000:.2f} MW")
        
        # 发电机输出功率（装机容量）
        self.P_generator = self.P_turbine * self.eta_g
        
        print(f"\n3. 发电机输出（装机容量）:")
        print(f"   P_发 = P_轮 × η_g")
        print(f"   P_发 = {self.P_turbine:.2f} × {self.eta_g}")
        print(f"   P_发 = {self.P_generator:.2f} kW = {self.P_generator/1000:.3f} MW")
        
        # 总效率
        self.eta_total = self.eta_head * self.eta_t * self.eta_g
        
        print(f"\n4. 总效率:")
        print(f"   η_总 = η_H × η_t × η_g")
        print(f"   η_总 = {self.eta_head:.4f} × {self.eta_t} × {self.eta_g}")
        print(f"   η_总 = {self.eta_total*100:.2f}%")
        
        # 年发电量（假设年利用小时数）
        hours_per_year = 5000  # 小时
        self.annual_energy = self.P_generator * hours_per_year / 1000  # MWh
        
        print(f"\n5. 年发电量（假设年利用{hours_per_year}h）:")
        print(f"   E_年 = P × t = {self.P_generator/1000:.3f} × {hours_per_year}")
        print(f"   E_年 = {self.annual_energy:.2f} MWh = {self.annual_energy/10000:.3f} 亿kWh")
    
    def analyze_water_hammer(self):
        """分析水击保护"""
        print(f"\n{'='*80}")
        print("【水击分析与保护】")
        print(f"{'='*80}")
        
        # 水击波速（钢管）
        c_denominator = 1 + (self.K_water / self.E_steel) * (self.d2 / self.delta)
        self.c = np.sqrt(self.K_water / self.rho) / np.sqrt(c_denominator)
        
        print(f"\n1. 水击波速:")
        print(f"   c = √(K/ρ) / √(1 + (K/E)(d/δ))")
        print(f"   c = √({self.K_water:.2e}/{self.rho}) / √(1 + ({self.K_water:.2e}/{self.E_steel:.2e})×({self.d2}/{self.delta}))")
        print(f"   c = {self.c:.2f} m/s")
        
        # 相位时间
        self.T = 2 * self.L2 / self.c
        
        print(f"\n2. 相位时间:")
        print(f"   T = 2L/c = 2×{self.L2}/{self.c:.2f}")
        print(f"   T = {self.T:.2f} s")
        
        # 直接水击临界关闭时间
        t_cr = self.T
        
        print(f"\n3. 直接水击临界关闭时间:")
        print(f"   t_cr = T = {t_cr:.2f} s")
        
        # 关闭时间选择
        self.t_close = 15  # 秒
        
        print(f"\n4. 导叶关闭时间选择:")
        print(f"   建议: t_close ≥ 2T = {2*self.T:.2f} s")
        print(f"   选择: t_close = {self.t_close} s")
        
        if self.t_close > 2 * self.T:
            print(f"   ✓ t_close > 2T，间接水击，压力上升较小")
            self.hammer_type = "间接水击"
        elif self.t_close > self.T:
            print(f"   ⚠ T < t_close < 2T，过渡水击")
            self.hammer_type = "过渡水击"
        else:
            print(f"   ⚠ t_close < T，直接水击，压力上升大")
            self.hammer_type = "直接水击"
        
        # Joukowsky压力上升（最大瞬时）
        delta_v = self.v2  # 假设完全关闭
        self.delta_H = self.c * delta_v / self.g
        
        print(f"\n5. Joukowsky压力上升:")
        print(f"   ΔH = c·Δv/g")
        print(f"   Δv = v₂ = {delta_v:.4f} m/s（完全关闭）")
        print(f"   ΔH = {self.c:.2f}×{delta_v:.4f}/{self.g}")
        print(f"   ΔH = {self.delta_H:.4f} m")
        
        # 最大压力
        self.H_max = self.H1 + self.delta_H
        
        print(f"\n6. 最大压力:")
        print(f"   H_max = H₁ + ΔH")
        print(f"   H_max = {self.H1} + {self.delta_H:.4f}")
        print(f"   H_max = {self.H_max:.4f} m")
        print(f"   p_max = ρgH_max = {self.rho*self.g*self.H_max/1e6:.2f} MPa")
        
        # 保护措施
        print(f"\n7. 水击保护措施:")
        print(f"   • 调压井（已设置）✓")
        print(f"   • 延长关闭时间（t > 2T = {2*self.T:.1f}s）")
        print(f"   • 安全阀设置")
        print(f"   • 单向阀防倒流")
    
    def calculate_tailrace_depth(self):
        """计算尾水渠道水深"""
        print(f"\n{'='*80}")
        print("【尾水渠道分析】")
        print(f"{'='*80}")
        
        print(f"\n1. 渠道参数:")
        print(f"   宽度: B = {self.B} m")
        print(f"   坡度: i = {self.i}")
        print(f"   糙率: n = {self.n}")
        print(f"   流量: Q = {self.Q_design} m³/s")
        
        # Manning公式求正常水深
        def manning_eq(h):
            A = self.B * h
            R = A / (self.B + 2 * h)
            Q_calc = (1 / self.n) * A * R**(2/3) * self.i**(1/2)
            return Q_calc - self.Q_design
        
        self.h_tailrace = brentq(manning_eq, 0.1, 10)
        
        print(f"\n2. 正常水深h₀（Manning公式）:")
        A_tail = self.B * self.h_tailrace
        R_tail = A_tail / (self.B + 2 * self.h_tailrace)
        v_tail = self.Q_design / A_tail
        
        print(f"   h₀ = {self.h_tailrace:.4f} m")
        print(f"   A = {A_tail:.4f} m²")
        print(f"   R = {R_tail:.4f} m")
        print(f"   v = {v_tail:.4f} m/s")
        
        # 尾水水头损失
        self.h_tail = self.h_tailrace - (self.H3 - self.H2)
        
        print(f"\n3. 尾水水头损失:")
        print(f"   h_尾 = h₀ - (H₃ - H₂)")
        print(f"   h_尾 = {self.h_tailrace:.4f} - ({self.H3} - {self.H2})")
        print(f"   h_尾 = {self.h_tail:.4f} m")
    
    def comprehensive_optimization(self):
        """综合优化建议"""
        print(f"\n{'='*80}")
        print("【综合优化建议】")
        print(f"{'='*80}")
        
        suggestions = []
        
        # 1. 水头损失优化
        loss_ratio = (self.h_f_total + self.h_j_total) / self.H_gross
        if loss_ratio > 0.05:
            suggestions.append(f"• 水头损失占比{loss_ratio*100:.1f}%较大")
            suggestions.append(f"  - 建议增大管道直径（隧洞{self.d1}m→{self.d1*1.2:.1f}m, 钢管{self.d2}m→{self.d2*1.2:.1f}m）")
            suggestions.append(f"  - 定期清洗维护，降低λ值")
        
        # 2. 效率优化
        if self.eta_total < 0.85:
            suggestions.append(f"• 总效率{self.eta_total*100:.1f}%有提升空间")
            suggestions.append(f"  - 提高水头利用率（目前{self.eta_head*100:.1f}%）")
            suggestions.append(f"  - 选择高效水轮机（目前{self.eta_t*100:.1f}%）")
        
        # 3. 水击保护
        if self.delta_H / self.H_gross > 0.3:
            suggestions.append(f"• 水击压力上升{self.delta_H:.1f}m较大")
            suggestions.append(f"  - 确保调压井正常工作")
            suggestions.append(f"  - 延长关闭时间至>{2*self.T:.1f}s")
        
        # 4. 尾水设计
        if self.h_tailrace > 5:
            suggestions.append(f"• 尾水渠道水深{self.h_tailrace:.2f}m较深")
            suggestions.append(f"  - 建议加宽渠道或增大坡度")
        
        # 5. 发电效益
        annual_revenue = self.annual_energy * 400  # 假设电价0.4元/kWh
        suggestions.append(f"• 年发电量{self.annual_energy:.0f}MWh")
        suggestions.append(f"  - 预估年收益约{annual_revenue/10000:.1f}万元（按0.4元/kWh）")
        
        # 6. 综合建议
        suggestions.append("• 运行管理建议:")
        suggestions.append("  - 优化调度降低弃水")
        suggestions.append("  - 定期检修维持高效")
        suggestions.append("  - 水情监测预警系统")
        
        print(f"\n优化建议:")
        for suggestion in suggestions:
            print(suggestion)
        
        return suggestions
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目904：综合水利工程系统分析（终极跨章节综合题）")
        print("="*80)
        
        print("\n【工程概况】")
        print(f"  上游水库: H₁ = {self.H1} m")
        print(f"  引水隧洞: L₁={self.L1}m, d₁={self.d1}m")
        print(f"  压力钢管: L₂={self.L2}m, d₂={self.d2}m")
        print(f"  水轮机组: Q={self.Q_design}m³/s, η_t={self.eta_t}, η_g={self.eta_g}")
        print(f"  尾水渠道: B={self.B}m, i={self.i}")
        
        print("\n【涉及知识点】")
        print("1. 长管水力计算（Darcy-Weisbach）")
        print("2. 水头损失分配（沿程+局部）")
        print("3. 水击计算（Joukowsky公式）")
        print("4. 明渠均匀流（Manning公式）")
        print("5. 水轮机发电（能量转换）")
        print("6. 系统优化（技术经济分析）")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 水头损失: 隧洞{self.h_f1:.2f}m + 钢管{self.h_f2:.2f}m + 局部{self.h_j_total:.2f}m = {self.h_f_total + self.h_j_total:.2f}m")
        print(f"(2) 有效水头: H_净 = {self.H_net:.2f} m (利用率{self.eta_head*100:.1f}%)")
        print(f"(3) 装机容量: P = {self.P_generator/1000:.3f} MW, 年发电{self.annual_energy:.0f} MWh")
        print(f"(4) 水击保护: {self.hammer_type}, ΔH={self.delta_H:.1f}m, t_close>{2*self.T:.1f}s")
        print(f"(5) 尾水水深: h₀ = {self.h_tailrace:.2f} m")
        print(f"(6) 优化建议: 见上述分析（水头利用+效率提升+水击防护）")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(16, 10))
        
        # 子图1：系统纵剖面
        ax1 = plt.subplot(2, 3, 1)
        self._plot_longitudinal_section(ax1)
        
        # 子图2：水头损失分布
        ax2 = plt.subplot(2, 3, 2)
        self._plot_head_loss_distribution(ax2)
        
        # 子图3：能量转换流程
        ax3 = plt.subplot(2, 3, 3)
        self._plot_energy_conversion(ax3)
        
        # 子图4：水击过程
        ax4 = plt.subplot(2, 3, 4)
        self._plot_water_hammer(ax4)
        
        # 子图5：效率分析
        ax5 = plt.subplot(2, 3, 5)
        self._plot_efficiency_analysis(ax5)
        
        # 子图6：经济效益
        ax6 = plt.subplot(2, 3, 6)
        self._plot_economic_benefit(ax6)
        
        plt.tight_layout()
        return fig
    
    def _plot_longitudinal_section(self, ax):
        """绘制系统纵剖面"""
        # 分段
        x_reservoir = 0
        x_tunnel_end = self.L1
        x_surge = x_tunnel_end
        x_pipe_end = x_surge + self.L2
        x_tailrace_end = x_pipe_end + 200
        
        # 高程
        z = [self.H1, self.H1 - self.h_f1, self.H1 - self.h_f1,
             self.H2, self.H3]
        x = [x_reservoir, x_tunnel_end, x_surge, x_pipe_end, x_tailrace_end]
        
        # 水面/压力线
        ax.plot(x, z, 'b-', linewidth=2.5, label='水面/压力线')
        ax.fill_between(x, 0, z, alpha=0.2, color='lightblue')
        
        # 能量线
        E = [self.H1, self.H1 - self.h_f1, self.H1 - self.h_f1,
             self.H2 + self.H_net - self.H_gross + self.h_f1,
             self.H3 + self.h_tailrace]
        ax.plot(x, E, 'r--', linewidth=2, label='能量线', alpha=0.7)
        
        # 标注各段
        ax.text(x_tunnel_end/2, self.H1+5, '引水隧洞', ha='center', fontsize=10, weight='bold')
        ax.text(x_surge + self.L2/2, (self.H1+self.H2)/2, '压力钢管', ha='center', fontsize=10, weight='bold')
        ax.text(x_pipe_end + 100, self.H3+2, '尾水渠', ha='center', fontsize=10, weight='bold')
        
        # 水轮机
        ax.plot(x_pipe_end, self.H2, 'ro', markersize=15)
        ax.text(x_pipe_end, self.H2-10, '水轮机\n发电厂房', ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('水电站系统纵剖面图', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_head_loss_distribution(self, ax):
        """绘制水头损失分布"""
        labels = ['隧洞\n沿程', '钢管\n沿程', '局部\n损失']
        sizes = [self.h_f1, self.h_f2, self.h_j_total]
        colors = ['lightblue', 'lightcoral', 'lightyellow']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90,
                                          textprops={'fontsize': 10})
        
        for text in texts:
            text.set_weight('bold')
        
        for autotext in autotexts:
            autotext.set_weight('bold')
            autotext.set_fontsize(10)
        
        ax.set_title(f'水头损失分布\n(总计={self.h_f_total + self.h_j_total:.2f}m, {(self.h_f_total + self.h_j_total)/self.H_gross*100:.1f}%)',
                    fontsize=12, weight='bold')
    
    def _plot_energy_conversion(self, ax):
        """绘制能量转换流程"""
        # 能量流
        E_input = self.H_gross
        E_loss = self.h_f_total + self.h_j_total
        E_net = self.H_net
        E_turbine = E_net * self.eta_t
        E_generator = E_turbine * self.eta_g
        
        stages = ['毛水头', '损失', '净水头', '水轮机', '发电机']
        values = [E_input, -E_loss, E_net, E_turbine, E_generator]
        
        # 使用条形图展示能量转换
        y_pos = np.arange(len(stages))
        colors = ['skyblue', 'red', 'lightgreen', 'yellow', 'orange']
        
        for i, (stage, value, color) in enumerate(zip(stages, values, colors)):
            if value > 0:
                ax.barh(i, value, color=color, edgecolor='black', linewidth=2)
                ax.text(value/2, i, f'{stage}\n{value:.1f}m', ha='center', va='center',
                       fontsize=9, weight='bold')
            else:
                ax.barh(i, -value, color=color, edgecolor='black', linewidth=2, alpha=0.5)
                ax.text(-value/2, i, f'{stage}\n{-value:.1f}m', ha='center', va='center',
                       fontsize=9, weight='bold')
        
        ax.set_xlabel('能量/水头 (m)', fontsize=12)
        ax.set_title('能量转换流程', fontsize=13, weight='bold')
        ax.set_yticks([])
        ax.grid(True, axis='x', alpha=0.3)
        ax.set_xlim(0, E_input * 1.1)
    
    def _plot_water_hammer(self, ax):
        """绘制水击过程"""
        # 模拟关闭过程压力变化
        t = np.linspace(0, self.t_close * 2, 200)
        
        # 简化模型：线性关闭
        v_t = self.v2 * np.maximum(1 - t / self.t_close, 0)
        
        # 压力上升（间接水击简化）
        if self.t_close > 2 * self.T:
            # 间接水击，压力逐渐上升
            H_t = self.H1 + self.delta_H * (t / self.t_close) * np.exp(-t / self.t_close)
        else:
            # 直接水击，振荡
            H_t = self.H1 + self.delta_H * np.sin(np.pi * t / self.T) * np.exp(-t / (3*self.T))
        
        H_t = np.maximum(H_t, self.H2)
        
        ax.plot(t, H_t, 'b-', linewidth=2.5, label='压力水头')
        ax.axhline(self.H1, color='green', linestyle='--', linewidth=2,
                  label=f'正常压力 H₁={self.H1}m')
        ax.axhline(self.H_max, color='red', linestyle='--', linewidth=2,
                  label=f'最大压力 H_max={self.H_max:.0f}m')
        
        ax.set_xlabel('时间 (s)', fontsize=12)
        ax.set_ylabel('压力水头 (m)', fontsize=12)
        ax.set_title(f'水击过程（{self.hammer_type}）', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.t_close * 1.5)
    
    def _plot_efficiency_analysis(self, ax):
        """绘制效率分析"""
        stages = ['水头\n利用率', '水轮机\n效率', '发电机\n效率', '总\n效率']
        efficiencies = [self.eta_head, self.eta_t, self.eta_g, self.eta_total]
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']
        
        bars = ax.bar(stages, np.array(efficiencies)*100, color=colors,
                     edgecolor='black', linewidth=2)
        
        for bar, eff in zip(bars, efficiencies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                   f'{eff*100:.1f}%', ha='center', fontsize=11, weight='bold')
        
        ax.axhline(90, color='green', linestyle='--', linewidth=2, alpha=0.5,
                  label='优秀线90%')
        
        ax.set_ylabel('效率 (%)', fontsize=12)
        ax.set_title('系统效率分析', fontsize=13, weight='bold')
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, 105)
    
    def _plot_economic_benefit(self, ax):
        """绘制经济效益"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.95, '经济效益分析', ha='center', fontsize=13, weight='bold',
               transform=ax.transAxes)
        
        # 发电参数
        y = 0.80
        ax.text(0.1, y, '【发电参数】', fontsize=11, weight='bold',
               transform=ax.transAxes, color='blue')
        y -= 0.08
        ax.text(0.1, y, f'装机容量: {self.P_generator/1000:.3f} MW',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.1, y, f'年发电量: {self.annual_energy:.0f} MWh',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.1, y, f'年利用: 5000 小时',
               fontsize=10, transform=ax.transAxes)
        
        # 经济效益（假设）
        y -= 0.12
        ax.text(0.1, y, '【经济效益】', fontsize=11, weight='bold',
               transform=ax.transAxes, color='green')
        
        electricity_price = 0.4  # 元/kWh
        annual_revenue = self.annual_energy * electricity_price * 1000
        
        y -= 0.08
        ax.text(0.1, y, f'电价: {electricity_price} 元/kWh',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.1, y, f'年收益: {annual_revenue/10000:.1f} 万元',
               fontsize=10, weight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 投资回收（假设）
        investment = 50000  # 万元（假设）
        payback = investment / (annual_revenue / 10000)
        
        y -= 0.12
        ax.text(0.1, y, '【投资回收】', fontsize=11, weight='bold',
               transform=ax.transAxes, color='red')
        y -= 0.08
        ax.text(0.1, y, f'总投资: {investment} 万元（假设）',
               fontsize=10, transform=ax.transAxes)
        y -= 0.06
        ax.text(0.1, y, f'回收期: {payback:.1f} 年',
               fontsize=10, weight='bold', transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        
        # 总结
        y -= 0.12
        ax.text(0.5, y, f'✓ 综合效益显著\n总效率{self.eta_total*100:.1f}%，年收益{annual_revenue/10000:.0f}万元',
               ha='center', fontsize=10, weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8),
               transform=ax.transAxes)


def test_problem_904():
    """测试题目904"""
    print("\n" + "="*80)
    print("开始综合水利工程系统分析...")
    print("="*80)
    
    # 创建系统对象
    system = IntegratedWaterProject()
    
    # 打印结果
    system.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = system.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_904_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_904_result.png")
    
    # 验证
    assert system.H_net > 0, "净水头应大于0"
    assert system.H_net < system.H_gross, "净水头应小于毛水头"
    assert system.P_generator > 0, "发电功率应大于0"
    assert 0 < system.eta_total < 1, "总效率应在0-1之间"
    assert system.h_tailrace > 0, "尾水深应大于0"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("综合水利工程系统分析整合全部水力学知识！")
    print("• 长管计算: Darcy-Weisbach公式")
    print("• 水头分配: 沿程+局部损失")
    print("• 水击防护: Joukowsky公式 + 调压井")
    print("• 明渠流: Manning公式")
    print("• 能量转换: P = ηρgQH")
    print("• 系统优化: 技术经济综合分析")
    print("\n🎉 这是《水力学1000题详解》代码体系的完美收官之作！")


if __name__ == "__main__":
    test_problem_904()
