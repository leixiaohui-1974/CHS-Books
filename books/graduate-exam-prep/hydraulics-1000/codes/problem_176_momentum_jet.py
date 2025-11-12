"""
《水力学考研1000题详解》配套代码
题目176：动量方程-射流冲击平板

问题描述：
水平射流冲击垂直固定平板。射流直径d=0.05m，流速v=10m/s。
水的密度ρ=1000kg/m³。
求：(1) 射流对平板的冲击力F
    (2) 若平板倾斜30°，求冲击力F和分离流量比
    (3) 若平板为移动平板（速度u=3m/s），求冲击力
    (4) 绘制力-速度关系图

考点：
1. 动量方程：∑F = ρQ(v₂ - v₁)
2. 垂直平板：v₂ = 0，F = ρQv
3. 倾斜平板：流量分配，力的分解
4. 移动平板：相对速度
5. 射流功率和效率

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Circle, Polygon, FancyBboxPatch
from matplotlib.patches import FancyArrowPatch
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MomentumJet:
    """动量方程-射流冲击计算类"""
    
    def __init__(self, d, v, rho=1000, g=9.8):
        """
        初始化
        
        参数:
            d: 射流直径 (m)
            v: 射流速度 (m/s)
            rho: 水的密度 (kg/m³)
            g: 重力加速度 (m/s²)
        """
        self.d = d
        self.v = v
        self.rho = rho
        self.g = g
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算射流冲击力"""
        # 1. 射流流量
        self.A = np.pi * self.d**2 / 4
        self.Q = self.A * self.v
        
        # 2. 情况1：垂直固定平板
        self.F_perpendicular = self.rho * self.Q * self.v
        
        # 3. 情况2：倾斜平板（30°）
        self.theta = 30  # 度
        theta_rad = np.radians(self.theta)
        
        # 法向速度分量
        v_n = self.v * np.sin(theta_rad)
        # 切向速度分量
        v_t = self.v * np.cos(theta_rad)
        
        # 法向冲击力
        self.F_inclined = self.rho * self.Q * v_n
        
        # 分离流量（上下分流，速度相等）
        # 根据动量守恒，沿板面两侧流量相等
        self.Q1 = self.Q / 2  # 上侧流量
        self.Q2 = self.Q / 2  # 下侧流量
        
        # 4. 情况3：移动平板
        self.u = 3.0  # 平板速度 (m/s)
        v_rel = self.v - self.u  # 相对速度
        Q_rel = self.A * v_rel  # 相对流量
        self.F_moving = self.rho * Q_rel * v_rel
        
        # 5. 射流功率
        self.P_jet = 0.5 * self.rho * self.Q * self.v**2
        
        # 6. 移动平板的有效功率
        self.P_effective = self.F_moving * self.u
        
        # 7. 效率
        if self.P_jet > 0:
            self.eta = self.P_effective / self.P_jet * 100
        else:
            self.eta = 0
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*80)
        print("题目176：动量方程-射流冲击平板")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"射流直径: d = {self.d} m = {self.d*1000} mm")
        print(f"射流速度: v = {self.v} m/s")
        print(f"水的密度: ρ = {self.rho} kg/m³")
        
        print("\n【基本参数】")
        print(f"射流断面积: A = πd²/4 = π×{self.d}²/4 = {self.A:.6f} m²")
        print(f"射流流量: Q = Av = {self.A:.6f}×{self.v} = {self.Q:.6f} m³/s = {self.Q*1000:.3f} L/s")
        print(f"射流功率: P = ½ρQv² = 0.5×{self.rho}×{self.Q:.6f}×{self.v}²")
        print(f"          = {self.P_jet:.2f} W = {self.P_jet/1000:.3f} kW")
        
        print("\n" + "="*80)
        print("情况1：垂直固定平板")
        print("="*80)
        
        print("\n【物理模型】")
        print("射流水平冲击垂直固定平板，冲击后分成两股，沿板面上下流动")
        print("入口速度: v₁ = v（水平方向）")
        print("出口速度: v₂ = 0（水平方向，沿板面流动）")
        
        print("\n【动量方程】")
        print("X方向动量方程：F = ρQ(v₁ - v₂)")
        print("因为 v₂ = 0，所以：")
        print(f"F = ρQv₁")
        print(f"  = {self.rho}×{self.Q:.6f}×{self.v}")
        print(f"  = {self.F_perpendicular:.3f} N")
        print(f"  = {self.F_perpendicular/1000:.3f} kN")
        
        print("\n【物理意义】")
        print(f"冲击力等于射流动量的变化率")
        print(f"力的方向: 垂直于平板，指向平板")
        
        print("\n" + "="*80)
        print(f"情况2：倾斜平板（倾角θ = {self.theta}°）")
        print("="*80)
        
        print("\n【物理模型】")
        print("射流水平冲击倾斜平板，冲击后沿板面上下分流")
        print(f"倾角: θ = {self.theta}°")
        print(f"法向速度: vₙ = v·sin(θ) = {self.v}×sin({self.theta}°) = {self.v*np.sin(np.radians(self.theta)):.4f} m/s")
        print(f"切向速度: vₜ = v·cos(θ) = {self.v}×cos({self.theta}°) = {self.v*np.cos(np.radians(self.theta)):.4f} m/s")
        
        print("\n【动量方程】")
        print("法向方向：F = ρQ·vₙ")
        print(f"         = {self.rho}×{self.Q:.6f}×{self.v*np.sin(np.radians(self.theta)):.4f}")
        print(f"         = {self.F_inclined:.3f} N")
        print(f"         = {self.F_inclined/1000:.3f} kN")
        
        print("\n【流量分配】")
        print("假设沿板面上下对称分流（忽略重力）：")
        print(f"上侧流量: Q₁ = Q/2 = {self.Q1:.6f} m³/s = {self.Q1*1000:.3f} L/s")
        print(f"下侧流量: Q₂ = Q/2 = {self.Q2:.6f} m³/s = {self.Q2*1000:.3f} L/s")
        print(f"分流比: Q₁/Q₂ = 1:1")
        
        print("\n【与垂直平板对比】")
        print(f"垂直平板冲击力: F₀ = {self.F_perpendicular:.3f} N")
        print(f"倾斜平板冲击力: F = {self.F_inclined:.3f} N")
        print(f"比值: F/F₀ = sin({self.theta}°) = {self.F_inclined/self.F_perpendicular:.4f}")
        
        print("\n" + "="*80)
        print(f"情况3：移动平板（平板速度u = {self.u} m/s）")
        print("="*80)
        
        print("\n【物理模型】")
        print(f"平板以速度 u = {self.u} m/s 沿射流方向移动")
        print(f"相对速度: v_rel = v - u = {self.v} - {self.u} = {self.v - self.u} m/s")
        
        print("\n【动量方程（相对运动）】")
        print("对于移动坐标系，使用相对速度：")
        print(f"相对流量: Q_rel = A·v_rel = {self.A:.6f}×{self.v - self.u} = {self.A*(self.v - self.u):.6f} m³/s")
        print(f"冲击力: F = ρQ_rel·v_rel")
        print(f"      = {self.rho}×{self.A*(self.v - self.u):.6f}×{self.v - self.u}")
        print(f"      = {self.F_moving:.3f} N")
        print(f"      = {self.F_moving/1000:.3f} kN")
        
        print("\n【功率分析】")
        print(f"射流功率: P_jet = ½ρQv² = {self.P_jet:.2f} W")
        print(f"有效功率: P_eff = F·u = {self.F_moving:.3f}×{self.u} = {self.P_effective:.2f} W")
        print(f"效率: η = P_eff/P_jet × 100% = {self.eta:.2f}%")
        
        print("\n【与固定平板对比】")
        print(f"固定平板冲击力: F₀ = {self.F_perpendicular:.3f} N")
        print(f"移动平板冲击力: F = {self.F_moving:.3f} N")
        print(f"比值: F/F₀ = (v-u)²/v² = ({self.v}-{self.u})²/{self.v}² = {self.F_moving/self.F_perpendicular:.4f}")
        
        print("\n【最终答案汇总】")
        print("="*80)
        print(f"(1) 垂直固定平板冲击力: F = {self.F_perpendicular:.3f} N = {self.F_perpendicular/1000:.3f} kN")
        print(f"(2) 倾斜平板（30°）冲击力: F = {self.F_inclined:.3f} N = {self.F_inclined/1000:.3f} kN")
        print(f"    分离流量比: Q₁:Q₂ = 1:1")
        print(f"(3) 移动平板冲击力: F = {self.F_moving:.3f} N = {self.F_moving/1000:.3f} kN")
        print(f"    效率: η = {self.eta:.2f}%")
        print("="*80)
        
        print("\n【核心公式】")
        print("动量方程: F = ρQ(v₂ - v₁)")
        print("垂直平板: F = ρQv")
        print("倾斜平板: F = ρQ·v·sin(θ)")
        print("移动平板: F = ρQ_rel·v_rel = ρA(v-u)²")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：垂直平板冲击
        ax1 = plt.subplot(2, 2, 1)
        self._plot_perpendicular(ax1)
        
        # 子图2：倾斜平板冲击
        ax2 = plt.subplot(2, 2, 2)
        self._plot_inclined(ax2)
        
        # 子图3：移动平板冲击
        ax3 = plt.subplot(2, 2, 3)
        self._plot_moving(ax3)
        
        # 子图4：力-速度关系
        ax4 = plt.subplot(2, 2, 4)
        self._plot_force_velocity(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_perpendicular(self, ax):
        """绘制垂直平板冲击示意图"""
        # 平板
        plate = Rectangle((0.5, -0.4), 0.05, 0.8, 
                         facecolor='gray', edgecolor='black', linewidth=3)
        ax.add_patch(plate)
        
        # 射流
        jet = Rectangle((-0.3, -0.05), 0.8, 0.1,
                       facecolor='lightblue', edgecolor='blue', linewidth=2, alpha=0.7)
        ax.add_patch(jet)
        
        # 射流速度箭头
        ax.arrow(-0.4, 0, 0.3, 0, head_width=0.08, head_length=0.08,
                fc='blue', ec='blue', linewidth=2)
        ax.text(-0.5, 0.15, f'v={self.v}m/s', fontsize=11, color='blue', weight='bold')
        
        # 冲击点
        ax.plot(0.5, 0, 'ro', markersize=10)
        
        # 上下分流
        # 上侧
        arrow_up = FancyArrowPatch((0.5, 0), (0.5, 0.35),
                                  arrowstyle='->', mutation_scale=20,
                                  linewidth=2, color='cyan')
        ax.add_patch(arrow_up)
        ax.text(0.6, 0.25, f'Q₁={self.Q1*1000:.1f}L/s', fontsize=9, color='cyan')
        
        # 下侧
        arrow_down = FancyArrowPatch((0.5, 0), (0.5, -0.35),
                                    arrowstyle='->', mutation_scale=20,
                                    linewidth=2, color='cyan')
        ax.add_patch(arrow_down)
        ax.text(0.6, -0.25, f'Q₂={self.Q2*1000:.1f}L/s', fontsize=9, color='cyan')
        
        # 冲击力
        ax.arrow(0.5, 0, -0.25, 0, head_width=0.06, head_length=0.06,
                fc='red', ec='red', linewidth=3)
        ax.text(0.2, -0.15, f'F={self.F_perpendicular/1000:.2f}kN',
               fontsize=11, color='red', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlim(-0.6, 0.8)
        ax.set_ylim(-0.5, 0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('情况1：垂直固定平板', fontsize=13, weight='bold')
    
    def _plot_inclined(self, ax):
        """绘制倾斜平板冲击示意图"""
        # 倾斜平板
        theta_rad = np.radians(self.theta)
        plate_len = 0.8
        x1, y1 = 0.5, -0.4
        x2 = x1 + plate_len * np.cos(theta_rad)
        y2 = y1 + plate_len * np.sin(theta_rad)
        
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=8, color='gray')
        
        # 射流
        jet = Rectangle((-0.3, -0.05), 0.8, 0.1,
                       facecolor='lightblue', edgecolor='blue', linewidth=2, alpha=0.7)
        ax.add_patch(jet)
        
        # 射流速度
        ax.arrow(-0.4, 0, 0.3, 0, head_width=0.08, head_length=0.08,
                fc='blue', ec='blue', linewidth=2)
        ax.text(-0.5, 0.15, f'v={self.v}m/s', fontsize=11, color='blue', weight='bold')
        
        # 冲击点
        ax.plot(0.5, 0, 'ro', markersize=10)
        
        # 速度分解
        v_n = self.v * np.sin(theta_rad)
        v_t = self.v * np.cos(theta_rad)
        
        # 法向速度（垂直于板）
        nx = -np.sin(theta_rad)
        ny = np.cos(theta_rad)
        scale = 0.04
        ax.arrow(0.5, 0, nx*v_n*scale, ny*v_n*scale,
                head_width=0.05, head_length=0.04,
                fc='red', ec='red', linewidth=2)
        ax.text(0.3, 0.15, f'vₙ={v_n:.2f}m/s', fontsize=9, color='red')
        
        # 切向速度（沿板）
        tx = np.cos(theta_rad)
        ty = np.sin(theta_rad)
        ax.arrow(0.5, 0, tx*v_t*scale, ty*v_t*scale,
                head_width=0.05, head_length=0.04,
                fc='green', ec='green', linewidth=2)
        ax.text(0.65, 0.05, f'vₜ={v_t:.2f}m/s', fontsize=9, color='green')
        
        # 分流（沿板面）
        ax.arrow(0.5, 0, 0.25*np.cos(theta_rad), 0.25*np.sin(theta_rad),
                head_width=0.04, head_length=0.04,
                fc='cyan', ec='cyan', linewidth=2, alpha=0.7)
        ax.arrow(0.5, 0, -0.15*np.cos(theta_rad), -0.15*np.sin(theta_rad),
                head_width=0.04, head_length=0.04,
                fc='cyan', ec='cyan', linewidth=2, alpha=0.7)
        
        # 冲击力（法向）
        ax.arrow(0.5, 0, -0.2*np.sin(theta_rad), 0.2*np.cos(theta_rad),
                head_width=0.06, head_length=0.05,
                fc='red', ec='red', linewidth=3)
        ax.text(0.25, 0.25, f'F={self.F_inclined/1000:.2f}kN',
               fontsize=11, color='red', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 角度标注
        arc = mpatches.Arc((0.5, 0), 0.2, 0.2, angle=0, theta1=0, theta2=self.theta,
                          color='black', linewidth=1.5)
        ax.add_patch(arc)
        ax.text(0.65, -0.08, f'θ={self.theta}°', fontsize=10)
        
        ax.set_xlim(-0.6, 1.2)
        ax.set_ylim(-0.5, 0.6)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'情况2：倾斜平板（{self.theta}°）', fontsize=13, weight='bold')
    
    def _plot_moving(self, ax):
        """绘制移动平板冲击示意图"""
        # 移动平板
        plate = Rectangle((0.5, -0.4), 0.05, 0.8,
                         facecolor='lightgray', edgecolor='black', linewidth=3)
        ax.add_patch(plate)
        
        # 平板移动方向
        ax.arrow(0.525, -0.5, 0.2, 0, head_width=0.06, head_length=0.06,
                fc='green', ec='green', linewidth=2, linestyle='--')
        ax.text(0.6, -0.6, f'u={self.u}m/s', fontsize=11, color='green', weight='bold')
        
        # 射流（相对静止坐标系）
        jet = Rectangle((-0.3, -0.05), 0.8, 0.1,
                       facecolor='lightblue', edgecolor='blue', linewidth=2, alpha=0.7)
        ax.add_patch(jet)
        
        # 射流速度
        ax.arrow(-0.4, 0, 0.3, 0, head_width=0.08, head_length=0.08,
                fc='blue', ec='blue', linewidth=2)
        ax.text(-0.5, 0.15, f'v={self.v}m/s', fontsize=11, color='blue', weight='bold')
        
        # 相对速度
        v_rel = self.v - self.u
        ax.arrow(-0.1, 0.25, 0.15, 0, head_width=0.05, head_length=0.04,
                fc='purple', ec='purple', linewidth=2, linestyle='--')
        ax.text(-0.15, 0.35, f'v_rel={v_rel}m/s', fontsize=10, color='purple')
        
        # 冲击点
        ax.plot(0.5, 0, 'ro', markersize=10)
        
        # 分流
        ax.arrow(0.5, 0, 0, 0.3, head_width=0.04, head_length=0.04,
                fc='cyan', ec='cyan', linewidth=2, alpha=0.7)
        ax.arrow(0.5, 0, 0, -0.3, head_width=0.04, head_length=0.04,
                fc='cyan', ec='cyan', linewidth=2, alpha=0.7)
        
        # 冲击力
        ax.arrow(0.5, 0, -0.2, 0, head_width=0.06, head_length=0.05,
                fc='red', ec='red', linewidth=3)
        ax.text(0.15, -0.15, f'F={self.F_moving/1000:.2f}kN',
               fontsize=11, color='red', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 功率标注
        ax.text(0, -0.4, f'P_eff={self.P_effective:.0f}W\nη={self.eta:.1f}%',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.set_xlim(-0.6, 0.8)
        ax.set_ylim(-0.7, 0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'情况3：移动平板（u={self.u}m/s）', fontsize=13, weight='bold')
    
    def _plot_force_velocity(self, ax):
        """绘制力-速度关系图"""
        # 平板速度范围
        u_range = np.linspace(0, self.v, 100)
        
        # 固定平板力（常数）
        F_fixed = np.ones_like(u_range) * self.F_perpendicular
        
        # 移动平板力
        F_moving = self.rho * self.A * (self.v - u_range)**2
        
        # 功率
        P_effective = F_moving * u_range
        
        # 绘制力曲线
        ax.plot([0, self.v], [self.F_perpendicular, self.F_perpendicular],
               'b--', linewidth=2, label='固定平板F=ρQv')
        ax.plot(u_range, F_moving, 'r-', linewidth=2.5,
               label='移动平板F=ρA(v-u)²')
        
        # 标注本题的点
        ax.plot(self.u, self.F_moving, 'ro', markersize=12, zorder=5)
        ax.text(self.u, self.F_moving*1.1, 
               f'u={self.u}m/s\nF={self.F_moving:.1f}N',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 双Y轴：右侧为功率
        ax2 = ax.twinx()
        ax2.plot(u_range, P_effective/1000, 'g-', linewidth=2,
                label='有效功率P=F·u', alpha=0.7)
        
        # 标注最大功率点
        max_P_idx = np.argmax(P_effective)
        u_max_P = u_range[max_P_idx]
        P_max = P_effective[max_P_idx]
        ax2.plot(u_max_P, P_max/1000, 'g*', markersize=15, zorder=5)
        ax2.text(u_max_P, P_max/1000*1.1,
                f'P_max={P_max:.0f}W\n(u={u_max_P:.2f}m/s)',
                fontsize=9, ha='center', color='green',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.set_xlabel('平板速度 u (m/s)', fontsize=12)
        ax.set_ylabel('冲击力 F (N)', fontsize=12, color='r')
        ax2.set_ylabel('有效功率 P (kW)', fontsize=12, color='g')
        ax.tick_params(axis='y', labelcolor='r')
        ax2.tick_params(axis='y', labelcolor='g')
        ax.set_title('力-速度-功率关系', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax2.legend(loc='center right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.v)
        ax.set_ylim(0, self.F_perpendicular*1.2)


def test_problem_176():
    """测试题目176"""
    # 已知条件
    d = 0.05            # 射流直径 (m)
    v = 10.0            # 射流速度 (m/s)
    rho = 1000          # 水的密度 (kg/m³)
    
    # 创建计算对象
    jet = MomentumJet(d, v, rho)
    
    # 打印结果
    jet.print_results()
    
    # 可视化
    fig = jet.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_176_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_176_result.png")
    
    # 验证答案（合理性检查）
    assert 10 < jet.F_perpendicular < 1000, "垂直平板冲击力不合理"
    assert 0 < jet.F_inclined < jet.F_perpendicular, "倾斜平板冲击力不合理"
    assert 0 < jet.F_moving < jet.F_perpendicular, "移动平板冲击力不合理"
    assert abs(jet.F_inclined/jet.F_perpendicular - np.sin(np.radians(jet.theta))) < 0.01, "倾斜板力比不符"
    assert 0 < jet.eta < 100, "效率不合理"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("动量方程是水动力学的核心！")
    print("• 基本形式：∑F = ρQ(v₂ - v₁)")
    print("• 垂直平板：F = ρQv（v₂=0）")
    print("• 倾斜平板：F = ρQ·v·sin(θ)")
    print("• 移动平板：F = ρA(v-u)²")
    print("• 最大功率：u = v/3时，P_max = 4ρAv³/27")
    print("• 应用：射流推力、水轮机、喷水推进")


if __name__ == "__main__":
    test_problem_176()
