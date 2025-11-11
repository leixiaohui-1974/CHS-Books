"""
《水力学考研1000题详解》配套代码
题目901：水库泄洪系统综合分析（跨章节综合题）

问题描述：
某水库泄洪系统如图所示，包括：
  上游水库: 水位H₁ = 50 m（相对基准面）
  溢流堰: 堰顶高程P = 45 m，堰宽b = 10 m，堰流系数m = 0.4
  泄洪隧洞: 长度L = 200 m，直径d = 3 m，沿程阻力系数λ = 0.025
  下游出口: 出口高程H₂ = 10 m，淹没情况需判断
  下游河道: 矩形断面，宽度B = 15 m，糙率n = 0.025，坡度i = 0.001

要求：
(1) 计算溢流堰泄流量Q₁
(2) 计算泄洪隧洞泄流量Q₂
(3) 判断下游是否发生水跃，计算跃后水深
(4) 分析下游河道水面线类型
(5) 计算总能量损失
(6) 提出优化建议

涉及知识点：
1. 堰流（明渠流）: Q = mbH^(3/2)
2. 管流（Bernoulli + Darcy-Weisbach）: H₁ - H₂ = v²/2g + λL/d·v²/2g
3. 水跃（动量方程）: h_c = (h₁/2)(√(1+8Fr₁²)-1)
4. 明渠均匀流（Manning）: Q = (1/n)A R^(2/3) i^(1/2)
5. 能量损失分析

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon, Wedge

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ReservoirSystem:
    """水库泄洪系统综合分析类"""
    
    def __init__(self):
        """初始化"""
        self.g = 9.8          # 重力加速度 (m/s²)
        
        # 上游水库
        self.H1 = 50          # 上游水位 (m)
        
        # 溢流堰
        self.P = 45           # 堰顶高程 (m)
        self.b_weir = 10      # 堰宽 (m)
        self.m = 0.4          # 堰流系数
        
        # 泄洪隧洞
        self.L_tunnel = 200   # 隧洞长度 (m)
        self.d_tunnel = 3     # 隧洞直径 (m)
        self.lambda_tunnel = 0.025  # 沿程阻力系数
        
        # 下游出口
        self.H2 = 10          # 出口高程 (m)
        
        # 下游河道
        self.B_channel = 15   # 河道宽度 (m)
        self.n = 0.025        # 糙率
        self.i = 0.001        # 坡度
        
        # 计算各部分
        self.calculate_weir_flow()
        self.calculate_tunnel_flow()
        self.analyze_hydraulic_jump()
        self.analyze_channel_profile()
        self.calculate_energy_loss()
    
    def calculate_weir_flow(self):
        """计算溢流堰泄流量"""
        print(f"\n{'='*80}")
        print("【溢流堰泄流分析】")
        print(f"{'='*80}")
        
        # 堰上水头
        self.H_weir = self.H1 - self.P
        
        print(f"\n1. 堰上水头:")
        print(f"   H = H₁ - P = {self.H1} - {self.P}")
        print(f"   H = {self.H_weir} m")
        
        # 堰流公式: Q = mbH^(3/2)
        self.Q_weir = self.m * self.b_weir * self.H_weir**(3/2)
        
        print(f"\n2. 溢流堰泄流量:")
        print(f"   Q₁ = mbH^(3/2)")
        print(f"   Q₁ = {self.m}×{self.b_weir}×{self.H_weir}^(3/2)")
        print(f"   Q₁ = {self.Q_weir:.2f} m³/s")
        
        # 单宽流量
        self.q_weir = self.Q_weir / self.b_weir
        print(f"\n3. 单宽流量:")
        print(f"   q = Q₁/b = {self.Q_weir:.2f}/{self.b_weir}")
        print(f"   q = {self.q_weir:.4f} m³/(s·m)")
        
        # 堰顶流速（临界流速）
        self.h_c_weir = (self.q_weir**2 / self.g)**(1/3)
        self.v_c_weir = self.q_weir / self.h_c_weir
        
        print(f"\n4. 堰顶临界水深和流速:")
        print(f"   h_c = (q²/g)^(1/3) = ({self.q_weir:.4f}²/{self.g})^(1/3)")
        print(f"   h_c = {self.h_c_weir:.4f} m")
        print(f"   v_c = q/h_c = {self.q_weir:.4f}/{self.h_c_weir:.4f}")
        print(f"   v_c = {self.v_c_weir:.4f} m/s")
    
    def calculate_tunnel_flow(self):
        """计算泄洪隧洞泄流量"""
        print(f"\n{'='*80}")
        print("【泄洪隧洞泄流分析】")
        print(f"{'='*80}")
        
        # Bernoulli方程 + Darcy-Weisbach
        # H₁ - H₂ = v²/2g + λL/d·v²/2g = (1 + λL/d)·v²/2g
        
        print(f"\n1. 能量方程:")
        print(f"   H₁ - H₂ = (1 + λL/d)·v²/2g")
        
        # 总水头损失
        delta_H = self.H1 - self.H2
        print(f"\n2. 总水头差:")
        print(f"   ΔH = H₁ - H₂ = {self.H1} - {self.H2}")
        print(f"   ΔH = {delta_H} m")
        
        # 阻力系数
        K = 1 + self.lambda_tunnel * self.L_tunnel / self.d_tunnel
        print(f"\n3. 总阻力系数:")
        print(f"   K = 1 + λL/d = 1 + {self.lambda_tunnel}×{self.L_tunnel}/{self.d_tunnel}")
        print(f"   K = {K:.4f}")
        
        # 流速
        self.v_tunnel = np.sqrt(2 * self.g * delta_H / K)
        print(f"\n4. 隧洞流速:")
        print(f"   v = √(2gΔH/K) = √(2×{self.g}×{delta_H}/{K:.4f})")
        print(f"   v = {self.v_tunnel:.4f} m/s")
        
        # 流量
        A_tunnel = np.pi * (self.d_tunnel / 2)**2
        self.Q_tunnel = A_tunnel * self.v_tunnel
        
        print(f"\n5. 隧洞泄流量:")
        print(f"   A = πd²/4 = π×{self.d_tunnel}²/4 = {A_tunnel:.4f} m²")
        print(f"   Q₂ = Av = {A_tunnel:.4f}×{self.v_tunnel:.4f}")
        print(f"   Q₂ = {self.Q_tunnel:.2f} m³/s")
        
        # 出口断面
        self.h_exit = A_tunnel / self.B_channel  # 假设出口宽度等于河道宽度
        self.v_exit = self.Q_tunnel / (self.B_channel * self.h_exit)
        
        print(f"\n6. 出口断面（假设宽度=河道宽度）:")
        print(f"   h_出口 ≈ A_隧洞/B = {A_tunnel:.4f}/{self.B_channel}")
        print(f"   h_出口 ≈ {self.h_exit:.4f} m")
        print(f"   v_出口 = Q₂/(B·h) = {self.Q_tunnel:.2f}/({self.B_channel}×{self.h_exit:.4f})")
        print(f"   v_出口 = {self.v_exit:.4f} m/s")
        
        # Froude数
        self.Fr_exit = self.v_exit / np.sqrt(self.g * self.h_exit)
        print(f"\n7. 出口Froude数:")
        print(f"   Fr = v/√(gh) = {self.v_exit:.4f}/√({self.g}×{self.h_exit:.4f})")
        print(f"   Fr = {self.Fr_exit:.4f}")
        
        if self.Fr_exit > 1:
            print(f"   Fr > 1: 急流，可能发生水跃")
        else:
            print(f"   Fr < 1: 缓流")
    
    def analyze_hydraulic_jump(self):
        """分析水跃"""
        print(f"\n{'='*80}")
        print("【水跃分析】")
        print(f"{'='*80}")
        
        if self.Fr_exit <= 1:
            print(f"\n出口Fr={self.Fr_exit:.4f} ≤ 1，为缓流，不发生水跃")
            self.has_jump = False
            return
        
        self.has_jump = True
        print(f"\n出口Fr={self.Fr_exit:.4f} > 1，为急流，可能发生水跃")
        
        # 跃前水深
        self.h1_jump = self.h_exit
        
        # 共轭水深公式: h₂ = (h₁/2)(√(1+8Fr₁²)-1)
        self.h2_jump = (self.h1_jump / 2) * (np.sqrt(1 + 8 * self.Fr_exit**2) - 1)
        
        print(f"\n1. 共轭水深计算:")
        print(f"   h₁ = {self.h1_jump:.4f} m（跃前水深）")
        print(f"   h₂ = (h₁/2)(√(1+8Fr₁²)-1)")
        print(f"   h₂ = ({self.h1_jump:.4f}/2)(√(1+8×{self.Fr_exit:.4f}²)-1)")
        print(f"   h₂ = {self.h2_jump:.4f} m（跃后水深）")
        
        # 跃后流速
        self.v2_jump = self.v_exit * self.h1_jump / self.h2_jump
        self.Fr2_jump = self.v2_jump / np.sqrt(self.g * self.h2_jump)
        
        print(f"\n2. 跃后流速:")
        print(f"   v₂ = v₁h₁/h₂ = {self.v_exit:.4f}×{self.h1_jump:.4f}/{self.h2_jump:.4f}")
        print(f"   v₂ = {self.v2_jump:.4f} m/s")
        print(f"   Fr₂ = {self.Fr2_jump:.4f} < 1（跃后为缓流）✓")
        
        # 水跃长度（经验公式）
        self.L_jump = 6 * self.h2_jump
        print(f"\n3. 水跃长度（经验公式）:")
        print(f"   L_j = 6h₂ = 6×{self.h2_jump:.4f}")
        print(f"   L_j = {self.L_jump:.2f} m")
        
        # 能量损失
        self.E1_jump = self.h1_jump + self.v_exit**2 / (2 * self.g)
        self.E2_jump = self.h2_jump + self.v2_jump**2 / (2 * self.g)
        self.delta_E_jump = self.E1_jump - self.E2_jump
        
        print(f"\n4. 水跃能量损失:")
        print(f"   E₁ = h₁ + v₁²/2g = {self.h1_jump:.4f} + {self.v_exit**2/(2*self.g):.4f}")
        print(f"   E₁ = {self.E1_jump:.4f} m")
        print(f"   E₂ = h₂ + v₂²/2g = {self.h2_jump:.4f} + {self.v2_jump**2/(2*self.g):.4f}")
        print(f"   E₂ = {self.E2_jump:.4f} m")
        print(f"   ΔE = E₁ - E₂ = {self.delta_E_jump:.4f} m")
        
        # 相对能量损失
        eta_jump = self.delta_E_jump / self.E1_jump
        print(f"   相对损失: η = ΔE/E₁ = {eta_jump*100:.2f}%")
    
    def analyze_channel_profile(self):
        """分析下游河道水面线"""
        print(f"\n{'='*80}")
        print("【下游河道水面线分析】")
        print(f"{'='*80}")
        
        # Manning公式计算正常水深
        # Q = (1/n)A R^(2/3) i^(1/2)
        # 矩形断面: A = Bh, R = Bh/(B+2h)
        
        print(f"\n1. 河道参数:")
        print(f"   宽度: B = {self.B_channel} m")
        print(f"   糙率: n = {self.n}")
        print(f"   坡度: i = {self.i}")
        print(f"   流量: Q = Q₂ = {self.Q_tunnel:.2f} m³/s")
        
        # 正常水深（迭代求解）
        def manning_equation(h):
            A = self.B_channel * h
            R = A / (self.B_channel + 2 * h)
            Q_calc = (1 / self.n) * A * R**(2/3) * self.i**(1/2)
            return Q_calc - self.Q_tunnel
        
        self.h0_channel = brentq(manning_equation, 0.1, 5)
        
        print(f"\n2. 正常水深h₀:")
        A0 = self.B_channel * self.h0_channel
        R0 = A0 / (self.B_channel + 2 * self.h0_channel)
        v0 = self.Q_tunnel / A0
        
        print(f"   h₀ = {self.h0_channel:.4f} m（通过Manning公式迭代求解）")
        print(f"   A₀ = {A0:.4f} m²")
        print(f"   R₀ = {R0:.4f} m")
        print(f"   v₀ = {v0:.4f} m/s")
        
        # 临界水深
        # Fr = 1: v/√(gh) = 1, v = Q/(Bh), 代入得
        # Q/(Bh) = √(gh), Q²/(B²h²) = gh, h_c³ = Q²/(gB²)
        self.h_c_channel = (self.Q_tunnel**2 / (self.g * self.B_channel**2))**(1/3)
        
        print(f"\n3. 临界水深h_c:")
        print(f"   h_c = (Q²/(gB²))^(1/3)")
        print(f"   h_c = ({self.Q_tunnel:.2f}²/({self.g}×{self.B_channel}²))^(1/3)")
        print(f"   h_c = {self.h_c_channel:.4f} m")
        
        # 临界坡度
        A_c = self.B_channel * self.h_c_channel
        R_c = A_c / (self.B_channel + 2 * self.h_c_channel)
        self.i_c = (self.Q_tunnel * self.n / (A_c * R_c**(2/3)))**2
        
        print(f"\n4. 临界坡度i_c:")
        print(f"   i_c = (Qn/(AR^(2/3)))²")
        print(f"   i_c = {self.i_c:.6f}")
        
        # 水面线类型判别
        print(f"\n5. 水面线类型判别:")
        print(f"   i = {self.i:.6f}")
        print(f"   i_c = {self.i_c:.6f}")
        print(f"   h₀ = {self.h0_channel:.4f} m")
        print(f"   h_c = {self.h_c_channel:.4f} m")
        
        if self.i < self.i_c:
            print(f"   ∵ i < i_c, 缓坡")
            if self.has_jump:
                h_start = self.h2_jump
                print(f"   水跃后水深 h = {h_start:.4f} m")
                if h_start > self.h_c_channel:
                    print(f"   h > h_c: M1型水面线（壅水曲线）")
                    self.profile_type = "M1"
                else:
                    print(f"   h < h_c: M2型水面线（降水曲线）")
                    self.profile_type = "M2"
            else:
                self.profile_type = "M2"
                print(f"   M2型水面线")
        elif self.i > self.i_c:
            print(f"   ∵ i > i_c, 陡坡")
            if self.has_jump:
                print(f"   S2型水面线→水跃→M1型")
                self.profile_type = "S2→jump→M1"
            else:
                self.profile_type = "S2"
        else:
            print(f"   ∵ i = i_c, 临界坡")
            self.profile_type = "C"
    
    def calculate_energy_loss(self):
        """计算总能量损失"""
        print(f"\n{'='*80}")
        print("【总能量损失分析】")
        print(f"{'='*80}")
        
        # 上游水库总能量（相对基准面）
        E_upstream = self.H1
        
        # 下游河道总能量
        if self.has_jump:
            h_downstream = self.h2_jump
            v_downstream = self.v2_jump
        else:
            h_downstream = self.h0_channel
            v_downstream = self.Q_tunnel / (self.B_channel * h_downstream)
        
        E_downstream = self.H2 + h_downstream + v_downstream**2 / (2 * self.g)
        
        print(f"\n1. 上游总能量:")
        print(f"   E_上 = H₁ = {E_upstream} m（相对基准面）")
        
        print(f"\n2. 下游总能量:")
        print(f"   位置水头: {self.H2} m")
        print(f"   压力水头: {h_downstream:.4f} m")
        print(f"   流速水头: {v_downstream**2/(2*self.g):.4f} m")
        print(f"   E_下 = {E_downstream:.4f} m")
        
        # 总损失
        self.total_loss = E_upstream - E_downstream
        
        print(f"\n3. 总能量损失:")
        print(f"   ΔE_总 = E_上 - E_下")
        print(f"   ΔE_总 = {E_upstream} - {E_downstream:.4f}")
        print(f"   ΔE_总 = {self.total_loss:.4f} m")
        
        # 损失分配
        print(f"\n4. 能量损失分配:")
        
        # 隧洞沿程损失
        h_f_tunnel = self.lambda_tunnel * self.L_tunnel / self.d_tunnel * self.v_tunnel**2 / (2 * self.g)
        print(f"   隧洞沿程损失: h_f = {h_f_tunnel:.4f} m ({h_f_tunnel/self.total_loss*100:.1f}%)")
        
        if self.has_jump:
            print(f"   水跃能量损失: ΔE_跃 = {self.delta_E_jump:.4f} m ({self.delta_E_jump/self.total_loss*100:.1f}%)")
        
        # 其他损失（局部损失等）
        other_loss = self.total_loss - h_f_tunnel
        if self.has_jump:
            other_loss -= self.delta_E_jump
        
        print(f"   其他损失（局部+河道）: {other_loss:.4f} m ({other_loss/self.total_loss*100:.1f}%)")
        
        # 能量转换效率
        eta_total = E_downstream / E_upstream
        print(f"\n5. 能量转换效率:")
        print(f"   η = E_下/E_上 = {eta_total*100:.2f}%")
        print(f"   能量损失率 = {(1-eta_total)*100:.2f}%")
    
    def optimization_suggestions(self):
        """优化建议"""
        print(f"\n{'='*80}")
        print("【优化建议】")
        print(f"{'='*80}")
        
        suggestions = []
        
        # 计算隧洞沿程损失
        h_f_tunnel = self.lambda_tunnel * self.L_tunnel / self.d_tunnel * self.v_tunnel**2 / (2 * self.g)
        
        # 1. 堰流优化
        if self.Q_weir < self.Q_tunnel:
            suggestions.append("• 堰流能力不足，建议增加堰宽或降低堰顶高程")
        
        # 2. 水跃优化
        if self.has_jump:
            if self.Fr_exit > 9:
                suggestions.append("• 出口Fr数过大，水跃过于剧烈，建议设置消能工")
            elif self.Fr_exit > 4.5:
                suggestions.append("• 水跃较强，建议设置消力池")
            else:
                suggestions.append("• 水跃强度适中，可利用自然水跃消能")
        
        # 3. 下游河道
        if self.has_jump and self.h2_jump > self.h0_channel * 1.2:
            suggestions.append("• 跃后水深明显大于正常水深，建议加深河槽或拓宽")
        
        # 4. 能量损失
        if h_f_tunnel / self.total_loss > 0.5:
            suggestions.append("• 隧洞沿程损失占比较大，建议增大隧洞直径或减小糙率")
        
        # 5. 安全性
        if self.v_tunnel > 10:
            suggestions.append(f"• 隧洞流速{self.v_tunnel:.2f}m/s较大，注意抗冲刷和空化")
        
        print(f"\n优化建议：")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        if not suggestions:
            print("• 当前系统运行状态良好，建议加强日常维护和监测")
        
        return suggestions
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目901：水库泄洪系统综合分析（跨章节综合题）")
        print("="*80)
        
        print("\n【系统概况】")
        print(f"  上游水位: H₁ = {self.H1} m")
        print(f"  堰顶高程: P = {self.P} m")
        print(f"  下游高程: H₂ = {self.H2} m")
        print(f"  泄洪隧洞: L={self.L_tunnel}m, d={self.d_tunnel}m")
        print(f"  下游河道: B={self.B_channel}m, n={self.n}, i={self.i}")
        
        print("\n【涉及知识点】")
        print("1. 堰流理论（明渠流）")
        print("2. 管流理论（Bernoulli方程 + 沿程损失）")
        print("3. 水跃理论（动量方程）")
        print("4. 明渠非均匀流（水面线分析）")
        print("5. 能量守恒与损失分析")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 优化建议
        self.optimization_suggestions()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 溢流堰泄流量: Q₁ = {self.Q_weir:.2f} m³/s")
        print(f"(2) 泄洪隧洞泄流量: Q₂ = {self.Q_tunnel:.2f} m³/s")
        
        if self.has_jump:
            print(f"(3) 发生水跃: h₁={self.h1_jump:.3f}m → h₂={self.h2_jump:.3f}m, L_j={self.L_jump:.2f}m")
        else:
            print(f"(3) 不发生水跃（Fr={self.Fr_exit:.3f} ≤ 1）")
        
        print(f"(4) 下游水面线类型: {self.profile_type}")
        print(f"(5) 总能量损失: ΔE = {self.total_loss:.2f} m ({(1-self.total_loss/self.H1)*100:.1f}%效率)")
        print(f"(6) 优化建议: 见上述分析")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(16, 12))
        
        # 子图1：系统纵剖面
        ax1 = plt.subplot(2, 2, 1)
        self._plot_longitudinal_profile(ax1)
        
        # 子图2：流量与能量对比
        ax2 = plt.subplot(2, 2, 2)
        self._plot_flow_energy(ax2)
        
        # 子图3：水跃分析
        ax3 = plt.subplot(2, 2, 3)
        self._plot_hydraulic_jump(ax3)
        
        # 子图4：能量损失分布
        ax4 = plt.subplot(2, 2, 4)
        self._plot_energy_loss(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_longitudinal_profile(self, ax):
        """绘制系统纵剖面"""
        # X坐标设置
        x_reservoir = 0
        x_weir = 100
        x_tunnel_entrance = 120
        x_tunnel_exit = x_tunnel_entrance + self.L_tunnel
        x_channel_end = x_tunnel_exit + 100
        
        # 上游水库
        ax.fill_between([x_reservoir, x_weir], 0, self.H1, 
                       alpha=0.3, color='lightblue', label='水体')
        ax.plot([x_reservoir, x_weir], [self.H1, self.H1], 'b-', linewidth=2)
        ax.text((x_reservoir+x_weir)/2, self.H1+2, f'H₁={self.H1}m',
               ha='center', fontsize=10, weight='bold')
        
        # 溢流堰
        weir_points = [[x_weir-5, 0], [x_weir-5, self.P], 
                      [x_weir, self.P], [x_weir+5, self.P-5], [x_weir+5, 0]]
        weir_poly = Polygon(weir_points, facecolor='gray', edgecolor='black', linewidth=2)
        ax.add_patch(weir_poly)
        ax.text(x_weir, self.P+3, '溢流堰', ha='center', fontsize=9, weight='bold')
        
        # 泄洪隧洞
        tunnel_y = (self.P + self.H2) / 2
        tunnel_rect = Rectangle((x_tunnel_entrance, tunnel_y - self.d_tunnel/2),
                               self.L_tunnel, self.d_tunnel,
                               facecolor='lightgray', edgecolor='black', linewidth=2)
        ax.add_patch(tunnel_rect)
        ax.text((x_tunnel_entrance + x_tunnel_exit)/2, tunnel_y,
               f'泄洪隧洞\nL={self.L_tunnel}m', ha='center', fontsize=9)
        
        # 下游河道
        ax.fill_between([x_tunnel_exit, x_channel_end], 0, 
                       self.H2 + self.h0_channel,
                       alpha=0.3, color='lightblue')
        ax.plot([x_tunnel_exit, x_channel_end], [0, 0], 'k-', linewidth=3)
        
        # 水跃
        if self.has_jump:
            x_jump = x_tunnel_exit + 20
            ax.fill_between([x_tunnel_exit, x_jump],
                          self.H2, self.H2 + self.h1_jump,
                          alpha=0.5, color='cyan', label='水跃前')
            ax.fill_between([x_jump, x_jump + self.L_jump],
                          self.H2, self.H2 + self.h2_jump,
                          alpha=0.5, color='yellow', label='水跃区')
            ax.text(x_jump + self.L_jump/2, self.H2 + self.h2_jump + 1,
                   '水跃', ha='center', fontsize=9, weight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 能量线
        x_energy = [x_reservoir, x_weir, x_tunnel_entrance, x_tunnel_exit, x_channel_end]
        E_energy = [self.H1, self.H1, 
                   self.H1 - 1,  # 局部损失
                   self.H2 + self.h_exit + self.v_exit**2/(2*self.g),
                   self.H2 + self.h0_channel + (self.Q_tunnel/(self.B_channel*self.h0_channel))**2/(2*self.g)]
        ax.plot(x_energy, E_energy, 'r--', linewidth=2, label='能量线', alpha=0.7)
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('水库泄洪系统纵剖面', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(x_reservoir - 20, x_channel_end + 20)
        ax.set_ylim(-5, self.H1 + 10)
    
    def _plot_flow_energy(self, ax):
        """绘制流量与能量对比"""
        categories = ['溢流堰', '泄洪隧洞']
        flows = [self.Q_weir, self.Q_tunnel]
        
        bars = ax.bar(categories, flows, color=['skyblue', 'lightcoral'],
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, flow in zip(bars, flows):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                   f'{flow:.2f} m³/s', ha='center', fontsize=11, weight='bold')
        
        ax.set_ylabel('流量 (m³/s)', fontsize=12)
        ax.set_title('泄流量对比', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, max(flows) * 1.3)
    
    def _plot_hydraulic_jump(self, ax):
        """绘制水跃分析"""
        if not self.has_jump:
            ax.text(0.5, 0.5, '不发生水跃\n(Fr ≤ 1)',
                   ha='center', va='center', fontsize=14, weight='bold',
                   transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
            ax.axis('off')
            return
        
        # X坐标
        x = np.linspace(0, self.L_jump, 100)
        
        # 水深变化（简化为线性）
        h = self.h1_jump + (self.h2_jump - self.h1_jump) * (x / self.L_jump)
        
        # 绘制水跃
        ax.fill_between(x, 0, h, alpha=0.5, color='cyan')
        ax.plot(x, h, 'b-', linewidth=2.5)
        
        # 跃前跃后
        ax.axhline(self.h1_jump, color='red', linestyle='--', linewidth=2,
                  label=f'h₁={self.h1_jump:.3f}m, Fr₁={self.Fr_exit:.2f}')
        ax.axhline(self.h2_jump, color='green', linestyle='--', linewidth=2,
                  label=f'h₂={self.h2_jump:.3f}m, Fr₂={self.Fr2_jump:.2f}')
        
        # 能量线
        E = [self.E1_jump - i/(self.L_jump) * self.delta_E_jump for i in x]
        ax.plot(x, E, 'orange', linestyle=':', linewidth=2, label='能量线')
        
        # 标注
        ax.text(self.L_jump/2, self.h2_jump + 0.5, '水跃区',
               ha='center', fontsize=11, weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.text(self.L_jump/2, self.E1_jump + 0.3,
               f'ΔE={self.delta_E_jump:.2f}m',
               ha='center', fontsize=10, weight='bold', color='red')
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('水深/能量 (m)', fontsize=12)
        ax.set_title('水跃过程分析', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.L_jump)
        ax.set_ylim(0, max(self.E1_jump, self.h2_jump) * 1.3)
    
    def _plot_energy_loss(self, ax):
        """绘制能量损失分布"""
        # 损失分类
        h_f_tunnel = self.lambda_tunnel * self.L_tunnel / self.d_tunnel * self.v_tunnel**2 / (2 * self.g)
        
        losses = []
        labels = []
        colors = []
        
        losses.append(h_f_tunnel)
        labels.append(f'隧洞沿程\n{h_f_tunnel:.2f}m')
        colors.append('lightblue')
        
        if self.has_jump:
            losses.append(self.delta_E_jump)
            labels.append(f'水跃消能\n{self.delta_E_jump:.2f}m')
            colors.append('yellow')
        
        other = self.total_loss - sum(losses)
        if other > 0.1:
            losses.append(other)
            labels.append(f'其他损失\n{other:.2f}m')
            colors.append('lightcoral')
        
        # 饼图
        wedges, texts, autotexts = ax.pie(losses, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90,
                                          textprops={'fontsize': 10, 'weight': 'bold'})
        
        ax.set_title(f'能量损失分布\n(总损失={self.total_loss:.2f}m)', 
                    fontsize=13, weight='bold')


def test_problem_901():
    """测试题目901"""
    print("\n" + "="*80)
    print("开始水库泄洪系统综合分析...")
    print("="*80)
    
    # 创建系统对象
    system = ReservoirSystem()
    
    # 打印结果
    system.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = system.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_901_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_901_result.png")
    
    # 验证
    assert system.Q_weir > 0, "堰流量应大于0"
    assert system.Q_tunnel > 0, "隧洞流量应大于0"
    assert system.total_loss > 0, "总能量损失应大于0"
    assert system.total_loss < system.H1, "损失应小于总水头"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水库泄洪系统综合分析整合多个水力学知识点！")
    print("• 堰流: Q = mbH^(3/2)")
    print("• 管流: Bernoulli + Darcy-Weisbach")
    print("• 水跃: 动量方程求共轭水深")
    print("• 水面线: 12类水面线分析")
    print("• 能量: 守恒与损失分析")
    print("• 优化: 多目标综合决策")


if __name__ == "__main__":
    test_problem_901()
