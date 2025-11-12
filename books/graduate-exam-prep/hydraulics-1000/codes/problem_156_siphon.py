"""
《水力学考研1000题详解》配套代码
题目156：虹吸管流量和真空度计算

问题描述：
虹吸管从上游水池抽水到下游水池。管径d=0.1m，管长L=50m，
上游水面高程H1=10m，下游水面高程H2=0m，最高点高程H_max=12m。
沿程阻力系数λ=0.025，局部损失系数∑ζ=5.0。
大气压p_a=101325Pa，水的密度ρ=1000kg/m³。
求：(1) 虹吸管流量Q
    (2) 最高点绝对压强p_max和真空度
    (3) 判断是否会发生汽蚀（水的饱和蒸汽压p_v=2340Pa）
    (4) 绘制虹吸管水力学特性图

考点：
1. 伯努利方程：z₁ + p₁/ρg + v₁²/2g = z₂ + p₂/ρg + v₂²/2g + h_loss
2. 虹吸管流量：Q = A√(2gΔH/(1+λL/d+∑ζ))
3. 最高点压强：p_max/ρg + v²/2g = H1 - h_loss
4. 真空度：p_vac = p_a - p_max
5. 汽蚀判断：p_max < p_v时发生汽蚀

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch, Arc, FancyArrow
from matplotlib.patches import FancyArrowPatch
import matplotlib.lines as mlines

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Siphon:
    """虹吸管计算类"""
    
    def __init__(self, d, L, H1, H2, H_max, lam, zeta_sum, 
                 p_a=101325, rho=1000, p_v=2340, g=9.8):
        """
        初始化
        
        参数:
            d: 管径 (m)
            L: 管长 (m)
            H1: 上游水面高程 (m)
            H2: 下游水面高程 (m)
            H_max: 最高点高程 (m)
            lam: 沿程阻力系数
            zeta_sum: 局部损失系数之和
            p_a: 大气压 (Pa)
            rho: 水的密度 (kg/m³)
            p_v: 水的饱和蒸汽压 (Pa)
            g: 重力加速度 (m/s²)
        """
        self.d = d
        self.L = L
        self.H1 = H1
        self.H2 = H2
        self.H_max = H_max
        self.lam = lam
        self.zeta_sum = zeta_sum
        self.p_a = p_a
        self.rho = rho
        self.p_v = p_v
        self.g = g
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算虹吸管参数"""
        # 1. 有效水头
        self.delta_H = self.H1 - self.H2
        
        # 2. 断面积
        self.A = np.pi * self.d**2 / 4
        
        # 3. 流速计算（伯努利方程）
        # H1 = H2 + (λL/d + ∑ζ)v²/2g
        # v = √(2gΔH / (1 + λL/d + ∑ζ))
        K = 1 + self.lam * self.L / self.d + self.zeta_sum
        self.v = np.sqrt(2 * self.g * self.delta_H / K)
        
        # 4. 流量
        self.Q = self.A * self.v
        
        # 5. 水头损失
        self.h_f = self.lam * self.L / self.d * self.v**2 / (2 * self.g)  # 沿程损失
        self.h_j = self.zeta_sum * self.v**2 / (2 * self.g)  # 局部损失
        self.h_loss = self.h_f + self.h_j  # 总损失
        
        # 6. 最高点压强（伯努利方程：从上游水面到最高点）
        # H1 + p_a/ρg = H_max + p_max/ρg + v²/2g + h_loss_to_max
        # 假设到最高点的损失占总损失的比例（按长度比）
        L_to_max = (self.H_max - self.H2) / (self.H1 - self.H2) * self.L  # 估算
        h_loss_to_max = self.h_loss * L_to_max / self.L
        
        # p_max/ρg = H1 + p_a/ρg - H_max - v²/2g - h_loss_to_max
        p_max_over_rhog = (self.H1 + self.p_a/(self.rho*self.g) 
                           - self.H_max - self.v**2/(2*self.g) - h_loss_to_max)
        self.p_max = p_max_over_rhog * self.rho * self.g
        
        # 7. 真空度
        self.p_vac = self.p_a - self.p_max  # 真空压强
        self.h_vac = self.p_vac / (self.rho * self.g)  # 真空高度
        
        # 8. 汽蚀判断
        self.cavitation = self.p_max < self.p_v
        self.safety_margin = (self.p_max - self.p_v) / self.p_v * 100 if self.p_max > self.p_v else 0
        
        # 9. 雷诺数
        nu = 1e-6  # 运动粘度
        self.Re = self.v * self.d / nu
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*80)
        print("题目156：虹吸管流量和真空度计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"管径: d = {self.d} m = {self.d*1000} mm")
        print(f"管长: L = {self.L} m")
        print(f"上游水面高程: H1 = {self.H1} m")
        print(f"下游水面高程: H2 = {self.H2} m")
        print(f"最高点高程: H_max = {self.H_max} m")
        print(f"沿程阻力系数: λ = {self.lam}")
        print(f"局部损失系数: ∑ζ = {self.zeta_sum}")
        print(f"大气压: p_a = {self.p_a} Pa = {self.p_a/1000:.2f} kPa")
        print(f"水的饱和蒸汽压: p_v = {self.p_v} Pa = {self.p_v/1000:.3f} kPa")
        
        print("\n【虹吸管原理】")
        print("虹吸管利用大气压和位能差实现跨越高点的自流输水")
        print("特点：")
        print("  1. 管道需要充满水，排空空气")
        print("  2. 出口必须低于上游水面")
        print("  3. 最高点会产生负压（真空）")
        print("  4. 真空度不能过大，否则会发生汽蚀")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算有效水头")
        print(f"ΔH = H1 - H2 = {self.H1} - {self.H2} = {self.delta_H} m")
        
        print("\n步骤2：应用伯努利方程计算流速")
        print("从上游水面(1)到下游水面(2)：")
        print("z1 + p1/ρg + v1²/2g = z2 + p2/ρg + v2²/2g + h_loss")
        print("其中：z1=H1, z2=H2, p1=p2=p_a, v1≈0, v2≈0")
        print("简化为：H1 = H2 + h_loss")
        print("h_loss = (λL/d + ∑ζ)v²/2g")
        print(f"\nΔH = (λL/d + ∑ζ)v²/2g")
        print(f"v = √(2gΔH / (λL/d + ∑ζ))")
        K = self.lam * self.L / self.d + self.zeta_sum
        print(f"  = √(2×{self.g}×{self.delta_H} / ({self.lam}×{self.L}/{self.d} + {self.zeta_sum}))")
        print(f"  = √({2*self.g*self.delta_H} / ({K:.2f}))")
        print(f"  = √{2*self.g*self.delta_H/K:.4f}")
        print(f"  = {self.v:.4f} m/s")
        
        print("\n步骤3：计算流量")
        print(f"A = πd²/4 = π×{self.d}²/4 = {self.A:.6f} m²")
        print(f"Q = Av = {self.A:.6f}×{self.v:.4f} = {self.Q:.6f} m³/s")
        print(f"  = {self.Q*1000:.3f} L/s = {self.Q*3600:.2f} m³/h")
        
        print("\n步骤4：计算水头损失")
        print(f"沿程损失: h_f = λL/d·v²/2g")
        print(f"            = {self.lam}×{self.L}/{self.d}×{self.v:.4f}²/(2×{self.g})")
        print(f"            = {self.h_f:.4f} m ({self.h_f/self.h_loss*100:.1f}%)")
        print(f"局部损失: h_j = ∑ζ·v²/2g")
        print(f"            = {self.zeta_sum}×{self.v:.4f}²/(2×{self.g})")
        print(f"            = {self.h_j:.4f} m ({self.h_j/self.h_loss*100:.1f}%)")
        print(f"总损失:   h = h_f + h_j = {self.h_loss:.4f} m")
        print(f"验证: ΔH = {self.delta_H} m ✓")
        
        print("\n步骤5：计算最高点压强")
        print("从上游水面到最高点的伯努利方程：")
        print("H1 + p_a/ρg = H_max + p_max/ρg + v²/2g + h_loss_to_max")
        print(f"p_max/ρg = H1 + p_a/ρg - H_max - v²/2g - h_loss_to_max")
        print(f"         = {self.H1} + {self.p_a/(self.rho*self.g):.2f} - {self.H_max} - {self.v**2/(2*self.g):.4f} - (估算损失)")
        print(f"p_max = {self.p_max:.2f} Pa = {self.p_max/1000:.3f} kPa")
        print(f"      = {self.p_max/(self.rho*self.g):.3f} m水柱")
        
        print("\n步骤6：计算真空度")
        print(f"真空压强: p_vac = p_a - p_max")
        print(f"              = {self.p_a} - {self.p_max:.2f}")
        print(f"              = {self.p_vac:.2f} Pa = {self.p_vac/1000:.3f} kPa")
        print(f"真空高度: h_vac = p_vac/ρg")
        print(f"              = {self.p_vac:.2f}/({self.rho}×{self.g})")
        print(f"              = {self.h_vac:.3f} m水柱")
        
        print("\n步骤7：汽蚀判断")
        print(f"水的饱和蒸汽压: p_v = {self.p_v} Pa = {self.p_v/1000:.3f} kPa")
        print(f"最高点压强: p_max = {self.p_max:.2f} Pa = {self.p_max/1000:.3f} kPa")
        if self.cavitation:
            print(f"结论: p_max < p_v  →  ⚠️ 会发生汽蚀！")
            print(f"      需要降低最高点高程或增大管径")
        else:
            print(f"结论: p_max > p_v  →  ✓ 不会发生汽蚀")
            print(f"安全系数: {self.safety_margin:.1f}%")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 虹吸管流量: Q = {self.Q:.6f} m³/s = {self.Q*1000:.3f} L/s")
        print(f"    管内流速: v = {self.v:.4f} m/s")
        print(f"(2) 最高点压强: p_max = {self.p_max:.2f} Pa = {self.p_max/1000:.3f} kPa")
        print(f"    真空度: h_vac = {self.h_vac:.3f} m水柱 = {self.p_vac/1000:.3f} kPa")
        print(f"(3) 汽蚀判断: {'⚠️ 会发生汽蚀' if self.cavitation else '✓ 不会发生汽蚀'}")
        if not self.cavitation:
            print(f"    安全系数: {self.safety_margin:.1f}%")
        print("="*80)
        
        print("\n【核心公式】")
        print("流量: Q = A√(2gΔH / (1 + λL/d + ∑ζ))")
        print("最高点压强: p_max/ρg = H1 + p_a/ρg - H_max - v²/2g - h_loss_to_max")
        print("真空度: p_vac = p_a - p_max")
        print("汽蚀条件: p_max < p_v")
        
        print("\n【工程要点】")
        print("1. 虹吸管最高点不宜过高，真空度一般不超过7-8m水柱")
        print("2. 启动时需要灌水排气，可用真空泵抽气")
        print("3. 运行中要防止空气渗入")
        print("4. 最高点应设置排气阀")
        print("5. 出口高程必须低于上游水面")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：虹吸管示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_siphon_schematic(ax1)
        
        # 子图2：能量线和水力坡度
        ax2 = plt.subplot(2, 2, 2)
        self._plot_energy_line(ax2)
        
        # 子图3：压强分布
        ax3 = plt.subplot(2, 2, 3)
        self._plot_pressure_distribution(ax3)
        
        # 子图4：流量-最高点高程关系
        ax4 = plt.subplot(2, 2, 4)
        self._plot_Q_H_relation(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_siphon_schematic(self, ax):
        """绘制虹吸管示意图"""
        # 上游水池
        pool1 = Rectangle((0, 0), 1.5, self.H1, facecolor='lightblue',
                         edgecolor='blue', linewidth=2, alpha=0.6)
        ax.add_patch(pool1)
        ax.text(0.75, self.H1+0.3, '上游水池', fontsize=11, ha='center', weight='bold')
        
        # 下游水池
        pool2 = Rectangle((4.5, 0), 1.5, self.H2 if self.H2 > 0 else 0.5,
                         facecolor='lightblue', edgecolor='blue', linewidth=2, alpha=0.6)
        ax.add_patch(pool2)
        ax.text(5.25, (self.H2 if self.H2 > 0 else 0.5)+0.3, 
               '下游水池', fontsize=11, ha='center', weight='bold')
        
        # 虹吸管（简化为折线）
        pipe_x = [1.5, 2, 3, 4, 4.5]
        pipe_y = [self.H1, self.H_max, self.H_max, self.H2 if self.H2 > 0 else 0, 
                 self.H2 if self.H2 > 0 else 0]
        ax.plot(pipe_x, pipe_y, 'k-', linewidth=4, label='虹吸管')
        
        # 流动方向箭头
        arrow_x = [1.7, 2.5, 3.5, 4.2]
        arrow_y = [self.H1*0.9 + self.H_max*0.1, self.H_max, self.H_max*0.3 + self.H2*0.7,
                  self.H2 if self.H2 > 0 else 0.2]
        for x, y in zip(arrow_x, arrow_y):
            ax.arrow(x, y, 0.15, 0, head_width=0.15, head_length=0.1,
                    fc='red', ec='red', linewidth=1.5)
        
        # 标注水面高程
        ax.plot([0, 1.5], [self.H1, self.H1], 'b-', linewidth=2)
        ax.text(-0.3, self.H1, f'H1={self.H1}m', fontsize=10, ha='right', color='blue')
        
        if self.H2 > 0:
            ax.plot([4.5, 6], [self.H2, self.H2], 'b-', linewidth=2)
            ax.text(6.3, self.H2, f'H2={self.H2}m', fontsize=10, ha='left', color='blue')
        
        # 标注最高点
        ax.plot([2.5, 3.5], [self.H_max, self.H_max], 'r--', linewidth=1.5)
        ax.plot(3, self.H_max, 'ro', markersize=10)
        ax.text(3, self.H_max+0.5, f'最高点\nH_max={self.H_max}m\np={self.p_max/1000:.1f}kPa',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 标注流量
        ax.text(3, self.H2-1 if self.H2 > 1 else -0.5, 
               f'Q={self.Q*1000:.2f}L/s\nv={self.v:.2f}m/s',
               fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 基准线
        ax.axhline(0, color='brown', linestyle='--', linewidth=1, alpha=0.5)
        ax.text(3, -0.3, '基准面', fontsize=9, ha='center', color='brown')
        
        ax.set_xlim(-0.5, 6.5)
        ax.set_ylim(-1, self.H_max+1)
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('高程 (m)', fontsize=12)
        ax.set_title('虹吸管系统示意图', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
    
    def _plot_energy_line(self, ax):
        """绘制能量线"""
        # 简化：假设沿程均匀损失
        x = np.array([0, 1.5, 2, 3, 4, 4.5, 6])
        
        # 管道高程
        z = np.array([self.H1, self.H1, self.H_max, self.H_max,
                     self.H2 if self.H2 > 0 else 0,
                     self.H2 if self.H2 > 0 else 0,
                     self.H2 if self.H2 > 0 else 0])
        
        # 能量线（线性下降）
        E = np.linspace(self.H1 + self.p_a/(self.rho*self.g),
                       self.H2 + self.p_a/(self.rho*self.g),
                       len(x))
        
        # 测压管水头线
        H_p = E - self.v**2/(2*self.g)
        
        # 绘制
        ax.plot(x, E, 'g-', linewidth=2.5, label='能量线', marker='o')
        ax.plot(x, H_p, 'b--', linewidth=2, label='测压管水头线', marker='s')
        ax.plot(x, z, 'k-', linewidth=3, label='管道轴线', marker='^')
        
        # 填充
        ax.fill_between(x, z, H_p, alpha=0.2, color='blue')
        
        # 标注最高点
        idx_max = 2
        ax.plot(x[idx_max], z[idx_max], 'ro', markersize=12)
        ax.text(x[idx_max]+0.2, z[idx_max], 
               f'最高点\n真空{self.h_vac:.2f}m',
               fontsize=9, color='red',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 标注
        ax.text(1, self.H1+1, f'ΔH={self.delta_H}m', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('高程/水头 (m)', fontsize=12)
        ax.set_title('能量线和水力坡度', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-0.5, 6.5)
    
    def _plot_pressure_distribution(self, ax):
        """绘制压强分布"""
        # 沿程各点压强（简化）
        positions = ['进口', '上升段', '最高点', '下降段', '出口']
        # 估算各点压强
        p_values = [
            self.p_a,  # 进口（接近大气压）
            self.p_a - self.rho*self.g*(self.H_max - self.H1)/2,  # 上升段
            self.p_max,  # 最高点
            self.p_a - self.rho*self.g*(self.H_max - self.H2)/2,  # 下降段
            self.p_a  # 出口（接近大气压）
        ]
        p_values_kPa = [p/1000 for p in p_values]
        
        # 大气压线
        ax.axhline(self.p_a/1000, color='green', linestyle='--', 
                  linewidth=2, label=f'大气压{self.p_a/1000:.1f}kPa')
        
        # 饱和蒸汽压线
        ax.axhline(self.p_v/1000, color='red', linestyle='--',
                  linewidth=2, label=f'饱和蒸汽压{self.p_v/1000:.2f}kPa')
        
        # 压强分布
        colors = ['lightblue', 'skyblue', 'red' if self.cavitation else 'yellow',
                 'skyblue', 'lightblue']
        bars = ax.bar(positions, p_values_kPa, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, p_values_kPa):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.2f}\nkPa',
                   ha='center', va='bottom', fontsize=10, weight='bold')
        
        # 特别标注最高点
        ax.plot(2, p_values_kPa[2], 'ro', markersize=15, zorder=5)
        if self.cavitation:
            ax.text(2, p_values_kPa[2]*1.2, '⚠️汽蚀！',
                   fontsize=11, ha='center', color='red', weight='bold')
        
        ax.set_ylabel('压强 (kPa)', fontsize=12)
        ax.set_title('沿程压强分布', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, self.p_a/1000*1.2)
    
    def _plot_Q_H_relation(self, ax):
        """绘制流量-最高点高程关系"""
        # 最高点高程范围
        H_max_range = np.linspace(self.H1, self.H1+5, 100)
        Q_range = []
        p_max_range = []
        
        for H_test in H_max_range:
            # 创建临时虹吸管对象
            temp_siphon = Siphon(self.d, self.L, self.H1, self.H2, H_test,
                                self.lam, self.zeta_sum, self.p_a, self.rho, self.p_v)
            Q_range.append(temp_siphon.Q * 1000)  # L/s
            p_max_range.append(temp_siphon.p_max / 1000)  # kPa
        
        # 双Y轴
        ax2 = ax.twinx()
        
        # 流量曲线
        line1 = ax.plot(H_max_range, Q_range, 'b-', linewidth=2.5, label='流量Q')
        ax.set_ylabel('流量 Q (L/s)', fontsize=12, color='b')
        ax.tick_params(axis='y', labelcolor='b')
        
        # 最高点压强曲线
        line2 = ax2.plot(H_max_range, p_max_range, 'r-', linewidth=2.5, label='最高点压强p_max')
        ax2.axhline(self.p_v/1000, color='red', linestyle='--', linewidth=2,
                   label='饱和蒸汽压')
        ax2.axhline(0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
        ax2.set_ylabel('最高点压强 p_max (kPa)', fontsize=12, color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        
        # 标注本题的点
        ax.plot(self.H_max, self.Q*1000, 'bo', markersize=12, zorder=5)
        ax.text(self.H_max, self.Q*1000*1.05,
               f'H_max={self.H_max}m\nQ={self.Q*1000:.2f}L/s',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax2.plot(self.H_max, self.p_max/1000, 'ro', markersize=12, zorder=5)
        
        # 汽蚀区域标注
        cavitation_zone = np.where(np.array(p_max_range) < self.p_v/1000)[0]
        if len(cavitation_zone) > 0:
            ax2.fill_between(H_max_range[cavitation_zone],
                           np.array(p_max_range)[cavitation_zone],
                           self.p_v/1000,
                           alpha=0.3, color='red')
            ax2.text(H_max_range[cavitation_zone[-1]], self.p_v/1000*1.5,
                    '汽蚀区', fontsize=10, color='red', weight='bold')
        
        ax.set_xlabel('最高点高程 H_max (m)', fontsize=12)
        ax.set_title('流量和压强随最高点高程变化', fontsize=13, weight='bold')
        
        # 图例
        lines = line1 + line2 + [ax2.lines[1]]
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        ax.set_xlim(self.H1, self.H1+5)


def test_problem_156():
    """测试题目156"""
    # 已知条件
    d = 0.1             # 管径 (m)
    L = 50              # 管长 (m)
    H1 = 10             # 上游水面高程 (m)
    H2 = 0              # 下游水面高程 (m)
    H_max = 12          # 最高点高程 (m)
    lam = 0.025         # 沿程阻力系数
    zeta_sum = 5.0      # 局部损失系数之和
    
    # 创建计算对象
    siphon = Siphon(d, L, H1, H2, H_max, lam, zeta_sum)
    
    # 打印结果
    siphon.print_results()
    
    # 可视化
    fig = siphon.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_156_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_156_result.png")
    
    # 验证答案（合理性检查）
    assert 0.001 < siphon.Q < 1.0, "流量不合理"
    assert 0.5 < siphon.v < 10.0, "流速不合理"
    assert siphon.p_max < siphon.p_a, "最高点压强应小于大气压"
    assert siphon.p_vac > 0, "真空度必须为正"
    assert siphon.h_loss > 0, "水头损失必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("虹吸管是利用大气压和位差输水的经典装置！")
    print("• 原理：伯努利方程")
    print("• 条件：出口低于上游水面")
    print("• 特点：最高点产生真空")
    print("• 限制：真空度不能过大（7-8m水柱）")
    print("• 汽蚀：p_max < p_v时发生")
    print("• 应用：取水、排水、输油")


if __name__ == "__main__":
    test_problem_156()
