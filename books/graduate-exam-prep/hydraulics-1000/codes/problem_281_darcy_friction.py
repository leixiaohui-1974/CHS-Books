"""
《水力学考研1000题详解》配套代码
题目281：达西-魏斯巴赫公式应用

问题描述：
水平圆管，直径d=150mm，长度L=100m，流量Q=20L/s。
管壁绝对粗糙度Δ=0.2mm，水温20°C（ν=1.0×10⁻⁶ m²/s）。
求：(1) 流速v和雷诺数Re
    (2) 相对粗糙度Δ/d和阻力系数λ
    (3) 沿程水头损失h_f
    (4) 压强降Δp

考点：
1. 连续性方程：v = Q/A
2. 雷诺数：Re = vd/ν
3. 相对粗糙度：Δ/d
4. 阻力系数：λ（查莫迪图或用公式）
5. 达西公式：h_f = λ(L/d)(v²/2g)
6. 压强降：Δp = ρgh_f

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DarcyFriction:
    """达西阻力计算类"""
    
    def __init__(self, d, L, Q, delta, nu=1.0e-6, rho=1000):
        """
        初始化
        
        参数:
            d: 管径 (m)
            L: 管长 (m)
            Q: 流量 (m³/s)
            delta: 绝对粗糙度 (m)
            nu: 运动粘度 (m²/s)
            rho: 密度 (kg/m³)
        """
        self.d = d
        self.L = L
        self.Q = Q
        self.delta = delta
        self.nu = nu
        self.rho = rho
        self.g = 9.8
        self.gamma = rho * self.g
        
        # 执行计算
        self.calculate()
    
    def calculate(self):
        """执行水力计算"""
        # 1. 流速
        self.A = np.pi * self.d**2 / 4
        self.v = self.Q / self.A
        
        # 2. 雷诺数
        self.Re = self.v * self.d / self.nu
        
        # 3. 相对粗糙度
        self.rel_roughness = self.delta / self.d
        
        # 4. 判断流态
        if self.Re < 2000:
            self.flow_regime = "层流"
            self.lambda_f = 64 / self.Re
        elif self.Re < 4000:
            self.flow_regime = "过渡流"
            self.lambda_f = self._colebrook()
        else:
            self.flow_regime = "湍流"
            if self.Re < 1e5:
                # 布拉修斯公式（光滑管）
                lambda_smooth = 0.3164 / (self.Re**0.25)
                # 科尔布鲁克公式（粗糙管）
                lambda_rough = self._colebrook()
                self.lambda_f = max(lambda_smooth, lambda_rough)
            else:
                self.lambda_f = self._colebrook()
        
        # 5. 达西公式求水头损失
        self.h_f = self.lambda_f * (self.L / self.d) * (self.v**2 / (2 * self.g))
        
        # 6. 压强降
        self.delta_p = self.rho * self.g * self.h_f
        
        # 7. 功率损失
        self.power_loss = self.gamma * self.Q * self.h_f
    
    def _colebrook(self):
        """
        科尔布鲁克-怀特公式（隐式，迭代求解）
        1/√λ = -2log₁₀(Δ/3.7d + 2.51/(Re√λ))
        """
        # 初值（斯万-杰恩公式）
        lambda_0 = 0.25 / (np.log10(self.rel_roughness/3.7 + 5.74/(self.Re**0.9)))**2
        
        # 迭代求解
        for _ in range(20):
            f_lambda = 1/np.sqrt(lambda_0) + 2*np.log10(self.rel_roughness/3.7 + 2.51/(self.Re*np.sqrt(lambda_0)))
            df_lambda = -0.5 * lambda_0**(-1.5) - 2 * 2.51 / (self.Re * np.log(10)) * (-0.5) * lambda_0**(-1.5)
            lambda_new = lambda_0 - f_lambda / df_lambda
            
            if abs(lambda_new - lambda_0) < 1e-8:
                break
            lambda_0 = lambda_new
        
        return lambda_0
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 80)
        print("题目281：达西-魏斯巴赫公式应用")
        print("=" * 80)
        
        print("\n【已知条件】")
        print(f"管径: d = {self.d*1000:.0f} mm = {self.d:.3f} m")
        print(f"管长: L = {self.L:.0f} m")
        print(f"流量: Q = {self.Q*1000:.0f} L/s = {self.Q:.4f} m³/s")
        print(f"绝对粗糙度: Δ = {self.delta*1000:.1f} mm = {self.delta:.4f} m")
        print(f"运动粘度: ν = {self.nu:.2e} m²/s (20°C水)")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算流速")
        print(f"A = πd²/4 = π×{self.d}²/4 = {self.A:.6f} m²")
        print(f"v = Q/A = {self.Q:.4f}/{self.A:.6f} = {self.v:.4f} m/s")
        
        print("\n步骤2：计算雷诺数")
        print(f"Re = vd/ν = ({self.v:.4f}×{self.d:.3f})/{self.nu:.2e}")
        print(f"   = {self.Re:.0f}")
        print(f"判断: Re = {self.Re:.0f} > 4000，流态为{self.flow_regime}")
        
        print("\n步骤3：计算相对粗糙度")
        print(f"Δ/d = {self.delta:.4f}/{self.d:.3f} = {self.rel_roughness:.6f}")
        
        print("\n步骤4：确定阻力系数λ")
        if self.Re < 2000:
            print(f"层流: λ = 64/Re = 64/{self.Re:.0f} = {self.lambda_f:.6f}")
        elif self.Re < 1e5:
            lambda_smooth = 0.3164 / (self.Re**0.25)
            print(f"布拉修斯公式（光滑管）: λ_smooth = 0.3164/Re^0.25 = {lambda_smooth:.6f}")
            print(f"科尔布鲁克公式（粗糙管）: λ_rough = {self.lambda_f:.6f}")
            print(f"取较大值: λ = {self.lambda_f:.6f}")
        else:
            print(f"科尔布鲁克公式: 1/√λ = -2log₁₀(Δ/3.7d + 2.51/(Re√λ))")
            print(f"迭代求解得: λ = {self.lambda_f:.6f}")
        
        print("\n步骤5：达西公式计算水头损失")
        print(f"h_f = λ(L/d)(v²/2g)")
        print(f"    = {self.lambda_f:.6f} × ({self.L}/{self.d:.3f}) × ({self.v:.4f}²/(2×{self.g}))")
        print(f"    = {self.lambda_f:.6f} × {self.L/self.d:.2f} × {self.v**2/(2*self.g):.6f}")
        print(f"    = {self.h_f:.4f} m")
        
        print("\n步骤6：计算压强降")
        print(f"Δp = ρgh_f = {self.rho} × {self.g} × {self.h_f:.4f}")
        print(f"   = {self.delta_p:.2f} Pa = {self.delta_p/1000:.2f} kPa")
        
        print("\n【最终答案】")
        print(f"(1) 流速: v = {self.v:.4f} m/s")
        print(f"    雷诺数: Re = {self.Re:.0f} ({self.flow_regime})")
        print(f"(2) 相对粗糙度: Δ/d = {self.rel_roughness:.6f}")
        print(f"    阻力系数: λ = {self.lambda_f:.6f}")
        print(f"(3) 水头损失: h_f = {self.h_f:.4f} m")
        print(f"(4) 压强降: Δp = {self.delta_p/1000:.2f} kPa")
        
        print("\n【附加信息】")
        print(f"功率损失: P = γQh_f = {self.power_loss:.2f} W = {self.power_loss/1000:.3f} kW")
        print(f"平均比降: i = h_f/L = {self.h_f/self.L:.6f} = {self.h_f/self.L*1000:.3f}‰")
        
        print("=" * 80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：管道示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_pipe(ax1)
        
        # 子图2：雷诺数与流态
        ax2 = plt.subplot(2, 2, 2)
        self._plot_reynolds(ax2)
        
        # 子图3：阻力系数曲线
        ax3 = plt.subplot(2, 2, 3)
        self._plot_moody(ax3)
        
        # 子图4：沿程压强分布
        ax4 = plt.subplot(2, 2, 4)
        self._plot_pressure_drop(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_pipe(self, ax):
        """绘制管道示意图"""
        # 管道
        pipe_height = 0.15
        pipe = Rectangle((0, -pipe_height/2), self.L, pipe_height, 
                         facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(pipe)
        
        # 流向箭头
        n_arrows = 5
        for i in range(n_arrows):
            x = self.L * (i + 0.5) / n_arrows
            ax.arrow(x-2, 0, 4, 0, head_width=0.05, head_length=1, 
                    fc='red', ec='red', linewidth=2)
        
        # 标注
        ax.text(self.L/2, pipe_height/2 + 0.05, f'L = {self.L:.0f} m', 
               fontsize=11, ha='center', va='bottom')
        ax.text(-5, 0, f'd = {self.d*1000:.0f} mm', 
               fontsize=10, ha='right', va='center')
        ax.text(self.L/2, -pipe_height/2 - 0.1, 
               f'Q = {self.Q*1000:.0f} L/s,  v = {self.v:.3f} m/s', 
               fontsize=10, ha='center', va='top', 
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 测压管
        n_tubes = 6
        for i in range(n_tubes):
            x = self.L * i / (n_tubes - 1)
            h_loss = self.h_f * i / (n_tubes - 1)
            h_tube = (self.h_f - h_loss) * 2  # 放大显示
            
            # 测压管
            ax.plot([x, x], [pipe_height/2, pipe_height/2 + h_tube], 
                   'b-', linewidth=1.5)
            ax.plot(x, pipe_height/2 + h_tube, 'bo', markersize=4)
        
        # 测压管水头线
        x_line = np.linspace(0, self.L, 100)
        h_line = self.h_f * (1 - x_line/self.L) * 2
        ax.plot(x_line, pipe_height/2 + h_line, 'b--', linewidth=2, 
               label='测压管水头线')
        
        ax.set_xlim(-10, self.L + 10)
        ax.set_ylim(-0.3, max(h_line) + 0.3)
        ax.set_xlabel('管道轴向 (m)', fontsize=12)
        ax.set_title('管道流动与水头损失', fontsize=14, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')
    
    def _plot_reynolds(self, ax):
        """绘制雷诺数与流态"""
        Re_values = [1000, 2000, 3000, 4000, self.Re]
        labels = ['1000\n(层流)', '2000\n(临界)', '3000\n(过渡)', 
                 '4000\n(湍流)', f'{self.Re:.0f}\n(本题)']
        colors = ['blue', 'orange', 'yellow', 'red', 'green']
        
        bars = ax.bar(range(len(Re_values)), Re_values, color=colors, 
                     alpha=0.7, edgecolor='black', linewidth=2)
        
        # 分界线
        ax.axhline(2000, color='orange', linestyle='--', linewidth=2, label='Re=2000 (临界)')
        ax.axhline(4000, color='red', linestyle='--', linewidth=2, label='Re=4000 (湍流)')
        
        ax.set_xticks(range(len(Re_values)))
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_ylabel('雷诺数 Re', fontsize=12)
        ax.set_title('雷诺数与流态判别', fontsize=14, weight='bold')
        ax.set_yscale('log')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3, which='both')
    
    def _plot_moody(self, ax):
        """绘制莫迪图（简化版）"""
        Re_range = np.logspace(3, 6, 100)
        
        # 层流线
        Re_laminar = Re_range[Re_range < 2000]
        lambda_laminar = 64 / Re_laminar
        ax.loglog(Re_laminar, lambda_laminar, 'b-', linewidth=2, label='层流: λ=64/Re')
        
        # 几条不同粗糙度的曲线
        roughness_values = [0, 0.00001, 0.0001, 0.001, self.rel_roughness]
        roughness_labels = ['光滑', 'Δ/d=10⁻⁵', 'Δ/d=10⁻⁴', 'Δ/d=10⁻³', f'本题: Δ/d={self.rel_roughness:.6f}']
        colors_m = ['green', 'cyan', 'orange', 'red', 'purple']
        
        for rough, label, color in zip(roughness_values, roughness_labels, colors_m):
            Re_turbulent = Re_range[Re_range >= 4000]
            lambda_vals = []
            for Re in Re_turbulent:
                if rough == 0:
                    # 布拉修斯
                    lam = 0.3164 / (Re**0.25)
                else:
                    # 科尔布鲁克（简化）
                    lam = 0.25 / (np.log10(rough/3.7 + 5.74/(Re**0.9)))**2
                lambda_vals.append(lam)
            ax.loglog(Re_turbulent, lambda_vals, color=color, linewidth=2, label=label)
        
        # 标记本题工况点
        ax.plot(self.Re, self.lambda_f, 'r*', markersize=20, 
               label=f'本题工况点\nRe={self.Re:.0f}, λ={self.lambda_f:.4f}')
        
        ax.set_xlabel('雷诺数 Re', fontsize=12)
        ax.set_ylabel('阻力系数 λ', fontsize=12)
        ax.set_title('莫迪图（Moody Diagram）', fontsize=14, weight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3, which='both')
        ax.set_xlim(1e3, 1e6)
        ax.set_ylim(0.01, 0.1)
    
    def _plot_pressure_drop(self, ax):
        """绘制沿程压强分布"""
        x = np.linspace(0, self.L, 100)
        p = self.delta_p * (1 - x/self.L) / 1000  # kPa (相对于出口)
        
        ax.plot(x, p, 'b-', linewidth=3)
        ax.fill_between(x, 0, p, alpha=0.3, color='lightblue')
        
        # 标注
        ax.text(0, p[0], f'{p[0]:.2f} kPa', fontsize=11, ha='right', va='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        ax.text(self.L, p[-1], f'{p[-1]:.2f} kPa', fontsize=11, ha='left', va='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        ax.text(self.L/2, p[50]/2, f'Δp = {self.delta_p/1000:.2f} kPa', 
               fontsize=12, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
        
        ax.set_xlabel('管道轴向 (m)', fontsize=12)
        ax.set_ylabel('压强 (相对出口, kPa)', fontsize=12)
        ax.set_title('沿程压强分布', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3)


def test_problem_281():
    """测试题目281"""
    # 已知条件
    d = 0.15        # 管径 (m)
    L = 100         # 管长 (m)
    Q = 0.020       # 流量 (m³/s) = 20 L/s
    delta = 0.0002  # 粗糙度 (m) = 0.2 mm
    
    # 创建计算对象
    darcy = DarcyFriction(d, L, Q, delta)
    
    # 打印结果
    darcy.print_results()
    
    # 可视化
    fig = darcy.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_281_result.png', 
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_281_result.png")
    
    # 验证答案（合理性检查）
    assert 0.5 < darcy.v < 5.0, "流速不合理"
    assert darcy.Re > 4000, "应该是湍流"
    assert 0.01 < darcy.lambda_f < 0.1, "阻力系数不合理"
    assert 0 < darcy.h_f < 50, "水头损失不合理"
    
    print("\n✓ 所有测试通过！")


if __name__ == "__main__":
    test_problem_281()
