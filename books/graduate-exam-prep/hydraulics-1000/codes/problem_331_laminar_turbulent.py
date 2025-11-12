"""
《水力学考研1000题详解》配套代码
题目331：层流与紊流流动特性分析

问题描述：
圆管流动，已知：
  管径 d = 0.10 m
  流速 v = 1.5 m/s
  运动粘度 ν = 1.0×10⁻⁶ m²/s（水，20℃）
  管壁粗糙度 Δ = 0.2 mm
要求：
(1) 计算Reynolds数，判断流态
(2) 分析层流和紊流的流速分布规律
(3) 计算沿程阻力系数λ
(4) 计算管壁切应力和断面平均切应力
(5) 对比层流和紊流的水力特性

考点：
1. Reynolds数：Re = vd/ν
2. 临界Reynolds数：Re_c = 2000（下临界），Re_c = 4000（上临界）
3. 层流流速分布：u(r) = u_max[1-(r/R)²]（抛物线）
4. 紊流流速分布：u(r) = u_max(1-r/R)^(1/n)（指数律，n≈7）
5. 层流阻力系数：λ = 64/Re
6. 紊流阻力系数：1/√λ = 2lg(d/Δ) + 1.74（尼古拉兹公式）
7. 切应力分布：τ(r) = τ₀(r/R)

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class LaminarTurbulent:
    """层流与紊流分析类"""
    
    def __init__(self, d=0.10, v=1.5, nu=1e-6, delta=0.0002, rho=1000):
        """
        初始化
        
        参数:
            d: 管径 (m)
            v: 平均流速 (m/s)
            nu: 运动粘度 (m²/s)
            delta: 管壁粗糙度 (m)
            rho: 密度 (kg/m³)
        """
        self.d = d
        self.R = d / 2  # 半径
        self.v = v
        self.nu = nu
        self.delta = delta
        self.rho = rho
        self.g = 9.8
        
        # 计算Reynolds数
        self.Re = self.v * self.d / self.nu
        
        # 判断流态
        self.classify_flow()
        
        # 计算阻力系数
        self.calculate_friction_factor()
        
        # 计算切应力
        self.calculate_shear_stress()
    
    def classify_flow(self):
        """判断流态"""
        if self.Re < 2000:
            self.flow_type = "层流"
            self.regime = "laminar"
        elif self.Re < 4000:
            self.flow_type = "过渡流"
            self.regime = "transition"
        else:
            self.flow_type = "紊流"
            self.regime = "turbulent"
        
        print(f"\nReynolds数: Re = vd/ν = {self.v}×{self.d}/{self.nu:.2e} = {self.Re:.0f}")
        print(f"流态判别: {self.flow_type}")
        print(f"  Re < 2000: 层流")
        print(f"  2000 ≤ Re < 4000: 过渡流")
        print(f"  Re ≥ 4000: 紊流")
    
    def velocity_profile_laminar(self, r):
        """
        层流流速分布（抛物线）
        u(r) = u_max[1-(r/R)²]
        u_max = 2v（断面平均流速的2倍）
        """
        u_max = 2 * self.v
        u = u_max * (1 - (r / self.R)**2)
        return u
    
    def velocity_profile_turbulent(self, r, n=7):
        """
        紊流流速分布（指数律）
        u(r) = u_max(1-r/R)^(1/n)
        n ≈ 7（经验值）
        u_max ≈ 1.22v（断面平均流速的1.22倍）
        """
        u_max = 1.22 * self.v
        # 避免中心线处的奇异性
        r_normalized = np.clip(r / self.R, 0, 0.999)
        u = u_max * (1 - r_normalized)**(1/n)
        return u
    
    def calculate_friction_factor(self):
        """计算沿程阻力系数λ"""
        if self.regime == "laminar":
            # 层流: λ = 64/Re
            self.lambda_laminar = 64 / self.Re
            self.lambda_actual = self.lambda_laminar
            print(f"\n层流阻力系数: λ = 64/Re = 64/{self.Re:.0f} = {self.lambda_laminar:.6f}")
        
        elif self.regime == "turbulent":
            # 紊流: 使用Colebrook-White公式迭代求解
            # 或使用尼古拉兹公式（粗糙管）
            relative_roughness = self.delta / self.d
            
            # 尼古拉兹公式（适用于完全粗糙区）
            # 1/√λ = 2lg(d/Δ) + 1.74
            temp = 2 * np.log10(self.d / self.delta) + 1.74
            self.lambda_nikuradse = 1 / temp**2
            
            # Colebrook-White公式（迭代求解）
            self.lambda_colebrook = self._solve_colebrook()
            
            self.lambda_actual = self.lambda_colebrook
            
            print(f"\n紊流阻力系数:")
            print(f"  相对粗糙度: Δ/d = {self.delta}/{self.d} = {relative_roughness:.4f}")
            print(f"  尼古拉兹公式: λ = {self.lambda_nikuradse:.6f}")
            print(f"  Colebrook-White公式: λ = {self.lambda_colebrook:.6f}")
        
        else:  # 过渡流
            # 简化处理，取层流和紊流的插值
            lambda_lam = 64 / self.Re
            self.lambda_colebrook = self._solve_colebrook()
            weight = (self.Re - 2000) / 2000
            self.lambda_actual = lambda_lam * (1 - weight) + self.lambda_colebrook * weight
            print(f"\n过渡流阻力系数: λ = {self.lambda_actual:.6f}（插值估算）")
    
    def _solve_colebrook(self, max_iter=20, tol=1e-6):
        """
        Colebrook-White公式迭代求解
        1/√λ = -2lg(Δ/3.7d + 2.51/(Re√λ))
        """
        # 初始值（使用Swamee-Jain显式公式估算）
        A = self.delta / (3.7 * self.d)
        B = 2.51 / self.Re
        lambda_old = 0.25 / (np.log10(A + B / np.sqrt(0.02)))**2
        
        for i in range(max_iter):
            sqrt_lambda = np.sqrt(lambda_old)
            f_val = -2 * np.log10(A + B / sqrt_lambda)
            lambda_new = 1 / f_val**2
            
            if abs(lambda_new - lambda_old) < tol:
                return lambda_new
            
            lambda_old = lambda_new
        
        return lambda_new
    
    def calculate_shear_stress(self):
        """计算切应力"""
        # 管壁切应力: τ₀ = λρv²/8
        self.tau_0 = self.lambda_actual * self.rho * self.v**2 / 8
        
        # 断面平均切应力: τ_avg = τ₀/2（对于圆管）
        self.tau_avg = self.tau_0 / 2
        
        print(f"\n切应力:")
        print(f"  管壁切应力: τ₀ = λρv²/8 = {self.tau_0:.3f} Pa")
        print(f"  断面平均切应力: τ_avg = τ₀/2 = {self.tau_avg:.3f} Pa")
    
    def shear_stress_distribution(self, r):
        """
        切应力分布（层流和紊流均适用）
        τ(r) = τ₀(r/R)
        """
        tau = self.tau_0 * r / self.R
        return tau
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目331：层流与紊流流动特性分析")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  管径: d = {self.d} m")
        print(f"  流速: v = {self.v} m/s")
        print(f"  运动粘度: ν = {self.nu:.2e} m²/s")
        print(f"  管壁粗糙度: Δ = {self.delta*1000} mm")
        print(f"  密度: ρ = {self.rho} kg/m³")
        
        print("\n【层流与紊流基本理论】")
        print("1. Reynolds数（流态判别准则）:")
        print("   Re = vd/ν = 惯性力/粘性力")
        
        print("\n2. 临界Reynolds数:")
        print("   Re_c(下) = 2000（层流→过渡流）")
        print("   Re_c(上) = 4000（过渡流→紊流）")
        
        print("\n3. 层流特性:")
        print("   • 流体质点有规则运动")
        print("   • 流速分布为抛物线: u(r) = u_max[1-(r/R)²]")
        print("   • u_max = 2v（最大流速为平均流速的2倍）")
        print("   • λ = 64/Re（阻力系数仅与Re有关）")
        
        print("\n4. 紊流特性:")
        print("   • 流体质点不规则脉动")
        print("   • 流速分布较均匀: u(r) = u_max(1-r/R)^(1/n)")
        print("   • u_max ≈ 1.22v（最大流速约为平均流速的1.22倍）")
        print("   • λ = f(Re, Δ/d)（阻力系数与Re和相对粗糙度有关）")
        
        print("\n【计算过程】")
        
        print("\n(1) Reynolds数计算与流态判别")
        print(f"  Re = vd/ν = {self.v}×{self.d}/{self.nu:.2e} = {self.Re:.0f}")
        print(f"  流态: {self.flow_type}")
        
        print("\n(2) 流速分布规律")
        
        # 层流流速分布
        print("\n  层流流速分布（抛物线）:")
        r_sample = np.array([0, self.R/2, self.R])
        for r in r_sample:
            u = self.velocity_profile_laminar(r)
            print(f"    r = {r:.3f} m: u = {u:.3f} m/s")
        u_max_lam = self.velocity_profile_laminar(0)
        print(f"    最大流速: u_max = {u_max_lam:.3f} m/s = {u_max_lam/self.v:.2f}v")
        
        # 紊流流速分布
        print("\n  紊流流速分布（指数律）:")
        for r in r_sample:
            u = self.velocity_profile_turbulent(r)
            print(f"    r = {r:.3f} m: u = {u:.3f} m/s")
        u_max_turb = self.velocity_profile_turbulent(0)
        print(f"    最大流速: u_max = {u_max_turb:.3f} m/s = {u_max_turb/self.v:.2f}v")
        
        print("\n(3) 沿程阻力系数λ")
        print(f"  实际流态({self.flow_type}): λ = {self.lambda_actual:.6f}")
        
        # 对比不同流态
        lambda_lam_calc = 64 / self.Re
        print(f"\n  对比:")
        print(f"    若为层流: λ = 64/Re = {lambda_lam_calc:.6f}")
        print(f"    若为紊流: λ = {self.lambda_colebrook if hasattr(self, 'lambda_colebrook') else 'N/A':.6f}")
        
        print("\n(4) 切应力分布")
        print(f"  管壁切应力: τ₀ = {self.tau_0:.3f} Pa")
        print(f"  管中心切应力: τ(0) = 0 Pa")
        print(f"  r = R/2处切应力: τ(R/2) = {self.shear_stress_distribution(self.R/2):.3f} Pa")
        
        print("\n(5) 层流与紊流水力特性对比")
        print("┌" + "─"*78 + "┐")
        print("│ 特性         │ 层流                    │ 紊流                     │")
        print("├" + "─"*78 + "┤")
        print("│ 流态         │ 规则、分层              │ 不规则、脉动             │")
        print("│ 流速分布     │ 抛物线（尖峰）          │ 指数律（较平坦）         │")
        print("│ u_max/v      │ 2.0                     │ 1.2~1.3                  │")
        print("│ λ的影响因素  │ 仅与Re有关              │ 与Re和Δ/d有关           │")
        print("│ λ的公式      │ λ=64/Re                 │ Colebrook-White公式      │")
        print("│ 能量损失     │ 较小                    │ 较大                     │")
        print("│ 工程意义     │ 小管径、高粘度流体      │ 大管径、低粘度流体       │")
        print("└" + "─"*78 + "┘")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) Re = {self.Re:.0f}，流态为{self.flow_type}")
        print(f"(2) 层流: 抛物线分布，u_max=2v；紊流: 指数律，u_max≈1.22v")
        print(f"(3) λ = {self.lambda_actual:.6f}")
        print(f"(4) τ₀ = {self.tau_0:.3f} Pa, τ_avg = {self.tau_avg:.3f} Pa")
        print(f"(5) 紊流流速分布更均匀，能量损失更大")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：流速分布对比
        ax1 = plt.subplot(2, 2, 1)
        self._plot_velocity_profile(ax1)
        
        # 子图2：切应力分布
        ax2 = plt.subplot(2, 2, 2)
        self._plot_shear_stress(ax2)
        
        # 子图3：流态判别（Moody图简化版）
        ax3 = plt.subplot(2, 2, 3)
        self._plot_flow_regime(ax3)
        
        # 子图4：层流与紊流对比示意图
        ax4 = plt.subplot(2, 2, 4)
        self._plot_flow_comparison(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_velocity_profile(self, ax):
        """绘制流速分布"""
        r = np.linspace(0, self.R, 100)
        
        # 层流流速分布
        u_lam = self.velocity_profile_laminar(r)
        
        # 紊流流速分布
        u_turb = self.velocity_profile_turbulent(r)
        
        # 绘制（使用径向坐标）
        # 上半管
        ax.plot(u_lam, r, 'b-', linewidth=2.5, label='层流（抛物线）')
        ax.plot(u_turb, r, 'r-', linewidth=2.5, label='紊流（指数律）')
        
        # 下半管（镜像）
        ax.plot(u_lam, -r, 'b-', linewidth=2.5)
        ax.plot(u_turb, -r, 'r-', linewidth=2.5)
        
        # 平均流速线
        ax.axvline(self.v, color='green', linestyle='--', linewidth=2, label=f'平均流速 v={self.v}m/s')
        
        # 管壁
        ax.axhline(self.R, color='gray', linestyle='-', linewidth=3, alpha=0.5)
        ax.axhline(-self.R, color='gray', linestyle='-', linewidth=3, alpha=0.5)
        
        # 标注
        ax.text(self.velocity_profile_laminar(0), 0, f'  {self.velocity_profile_laminar(0):.2f}m/s',
               fontsize=10, color='blue', weight='bold')
        ax.text(self.velocity_profile_turbulent(0), 0.02, f'  {self.velocity_profile_turbulent(0):.2f}m/s',
               fontsize=10, color='red', weight='bold')
        
        ax.set_xlabel('流速 u (m/s)', fontsize=12)
        ax.set_ylabel('径向位置 r (m)', fontsize=12)
        ax.set_title('层流与紊流流速分布对比', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(u_lam[0], u_turb[0]) * 1.1)
    
    def _plot_shear_stress(self, ax):
        """绘制切应力分布"""
        r = np.linspace(0, self.R, 100)
        tau = self.shear_stress_distribution(r)
        
        # 上半管
        ax.plot(tau, r, 'purple', linewidth=3, label='τ(r) = τ₀(r/R)')
        # 下半管
        ax.plot(tau, -r, 'purple', linewidth=3)
        
        # 管壁
        ax.axhline(self.R, color='gray', linestyle='-', linewidth=3, alpha=0.5)
        ax.axhline(-self.R, color='gray', linestyle='-', linewidth=3, alpha=0.5)
        
        # 标注关键点
        ax.plot(self.tau_0, self.R, 'ro', markersize=10)
        ax.plot(self.tau_0, -self.R, 'ro', markersize=10)
        ax.plot(0, 0, 'go', markersize=10)
        
        ax.text(self.tau_0, self.R + 0.005, f'τ₀={self.tau_0:.2f}Pa',
               ha='center', fontsize=10, weight='bold')
        ax.text(0, 0.005, 'τ=0', ha='center', fontsize=10, weight='bold')
        
        ax.set_xlabel('切应力 τ (Pa)', fontsize=12)
        ax.set_ylabel('径向位置 r (m)', fontsize=12)
        ax.set_title('切应力沿径向分布', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.tau_0 * 1.2)
    
    def _plot_flow_regime(self, ax):
        """绘制流态判别图"""
        Re_range = [1, 10, 100, 1000, 2000, 4000, 10000, 100000, 1000000]
        
        # 区域划分
        ax.axvspan(0, 2000, alpha=0.3, color='blue', label='层流区')
        ax.axvspan(2000, 4000, alpha=0.3, color='yellow', label='过渡区')
        ax.axvspan(4000, 1e6, alpha=0.3, color='red', label='紊流区')
        
        # 当前Re位置
        ax.axvline(self.Re, color='black', linestyle='--', linewidth=3, label=f'当前Re={self.Re:.0f}')
        ax.plot(self.Re, 0.5, 'ko', markersize=15)
        
        # 临界Re
        ax.axvline(2000, color='green', linestyle='-', linewidth=2, alpha=0.7)
        ax.axvline(4000, color='green', linestyle='-', linewidth=2, alpha=0.7)
        
        ax.text(1000, 0.8, '层流\nRe<2000', ha='center', fontsize=12, weight='bold')
        ax.text(3000, 0.8, '过渡\n2000≤Re<4000', ha='center', fontsize=11, weight='bold')
        ax.text(50000, 0.8, '紊流\nRe≥4000', ha='center', fontsize=12, weight='bold')
        
        ax.set_xscale('log')
        ax.set_xlim(1, 1e6)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Reynolds数 Re', fontsize=12)
        ax.set_title('流态判别（Reynolds数准则）', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.set_yticks([])
    
    def _plot_flow_comparison(self, ax):
        """绘制层流与紊流对比示意图"""
        ax.axis('off')
        
        # 层流示意图
        y_lam = 0.7
        ax.text(0.5, y_lam + 0.15, '层流（Laminar Flow）', ha='center', fontsize=13, weight='bold')
        
        # 绘制平行流线
        for i in range(5):
            y = y_lam - 0.05 * i
            ax.plot([0.1, 0.9], [y, y], 'b-', linewidth=2, alpha=0.7)
            # 箭头
            ax.annotate('', xy=(0.9, y), xytext=(0.8, y),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        
        ax.text(0.5, y_lam - 0.25, '• 流线平行\n• 质点有序运动\n• 能量损失小',
               ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 紊流示意图
        y_turb = 0.15
        ax.text(0.5, y_turb + 0.15, '紊流（Turbulent Flow）', ha='center', fontsize=13, weight='bold')
        
        # 绘制混乱流线
        np.random.seed(42)
        for i in range(5):
            y_base = y_turb - 0.05 * i
            x = np.linspace(0.1, 0.9, 20)
            y = y_base + 0.01 * np.sin(10 * x + i) + 0.005 * np.random.randn(20)
            ax.plot(x, y, 'r-', linewidth=2, alpha=0.7)
            # 箭头
            ax.annotate('', xy=(0.9, y[-1]), xytext=(0.85, y[-2]),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        ax.text(0.5, y_turb - 0.25, '• 流线交织\n• 质点脉动\n• 能量损失大',
               ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.2, 1)
        ax.set_title('层流与紊流流动形态对比', fontsize=13, weight='bold')


def test_problem_331():
    """测试题目331"""
    print("\n" + "="*80)
    print("开始层流与紊流流动特性分析...")
    print("="*80)
    
    # 创建分析对象
    flow = LaminarTurbulent(d=0.10, v=1.5, nu=1e-6, delta=0.0002)
    
    # 打印结果
    flow.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = flow.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_331_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_331_result.png")
    
    # 验证
    assert flow.Re > 0, "Reynolds数必须为正"
    assert flow.lambda_actual > 0, "阻力系数必须为正"
    assert flow.tau_0 > 0, "切应力必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("层流与紊流是管流的两种基本流态！")
    print("• Re = vd/ν（流态判别准则）")
    print("• 层流: λ=64/Re，流速抛物线分布")
    print("• 紊流: λ=f(Re,Δ/d)，流速分布较均匀")
    print("• 应用: 管道设计、流体输送、流量测量")


if __name__ == "__main__":
    test_problem_331()
