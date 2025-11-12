"""
《水力学考研1000题详解》配套代码
题目351：管道计算第一类问题

问题描述：
已知：管径d=200mm，长度L=500m，流量Q=40L/s，
      绝对粗糙度Δ=0.3mm，局部损失系数Σζ=5.0
求：总水头损失h

管道计算三类问题：
- 第一类：已知Q、d，求h（直接计算）✓ 本题
- 第二类：已知h、d，求Q（迭代计算）
- 第三类：已知Q、h，求d（迭代计算）

考点：
1. 雷诺数Re判断流态
2. 阻力系数λ确定（莫迪图或科尔布鲁克公式）
3. 达西公式：h_f = λ(L/d)(v²/2g)
4. 局部损失：h_m = Σζ(v²/2g)
5. 总损失：h = h_f + h_m

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PipeType1:
    """管道第一类问题求解类"""
    
    def __init__(self, d, L, Q, delta, sum_zeta, nu=1.0e-6, rho=1000):
        """
        初始化
        
        参数:
            d: 管径 (m)
            L: 管长 (m)
            Q: 流量 (m³/s)
            delta: 绝对粗糙度 (m)
            sum_zeta: 局部损失系数之和
            nu: 运动粘度 (m²/s)
            rho: 密度 (kg/m³)
        """
        self.d = d
        self.L = L
        self.Q = Q
        self.delta = delta
        self.sum_zeta = sum_zeta
        self.nu = nu
        self.rho = rho
        self.g = 9.8
        
        # 执行计算
        self.calculate()
    
    def calculate(self):
        """执行水力计算"""
        # 步骤1：流速
        self.A = np.pi * self.d**2 / 4
        self.v = self.Q / self.A
        
        # 步骤2：雷诺数
        self.Re = self.v * self.d / self.nu
        
        # 步骤3：相对粗糙度
        self.rel_roughness = self.delta / self.d
        
        # 步骤4：阻力系数λ
        if self.Re < 2000:
            self.flow_regime = "层流"
            self.lambda_f = 64 / self.Re
        elif self.Re < 4000:
            self.flow_regime = "过渡流"
            self.lambda_f = self._colebrook()
        else:
            self.flow_regime = "湍流"
            self.lambda_f = self._colebrook()
        
        # 步骤5：沿程损失
        self.h_f = self.lambda_f * (self.L / self.d) * (self.v**2 / (2 * self.g))
        
        # 步骤6：局部损失
        self.h_m = self.sum_zeta * (self.v**2 / (2 * self.g))
        
        # 步骤7：总损失
        self.h = self.h_f + self.h_m
        
        # 步骤8：损失占比
        self.ratio_f = self.h_f / self.h * 100
        self.ratio_m = self.h_m / self.h * 100
        
        # 步骤9：等效长度
        self.L_eq = self.sum_zeta * self.d / self.lambda_f
    
    def _colebrook(self):
        """科尔布鲁克公式迭代求解λ"""
        # 初值
        lambda_0 = 0.25 / (np.log10(self.rel_roughness/3.7 + 5.74/(self.Re**0.9)))**2
        
        # 迭代
        for _ in range(20):
            f_lambda = 1/np.sqrt(lambda_0) + 2*np.log10(self.rel_roughness/3.7 + 
                                                        2.51/(self.Re*np.sqrt(lambda_0)))
            df_lambda = -0.5 * lambda_0**(-1.5) - \
                       2 * 2.51 / (self.Re * np.log(10)) * (-0.5) * lambda_0**(-1.5)
            lambda_new = lambda_0 - f_lambda / df_lambda
            
            if abs(lambda_new - lambda_0) < 1e-8:
                break
            lambda_0 = lambda_new
        
        return lambda_0
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 85)
        print("题目351：管道计算第一类问题（已知Q、d，求h）")
        print("=" * 85)
        
        print("\n【已知条件】")
        print(f"管径: d = {self.d*1000:.0f} mm = {self.d:.3f} m")
        print(f"管长: L = {self.L:.0f} m")
        print(f"流量: Q = {self.Q*1000:.0f} L/s = {self.Q:.3f} m³/s")
        print(f"绝对粗糙度: Δ = {self.delta*1000:.1f} mm")
        print(f"局部损失系数: Σζ = {self.sum_zeta:.1f}")
        
        print("\n【计算步骤】")
        
        print("\n步骤1：计算流速")
        print(f"A = πd²/4 = π×{self.d}²/4 = {self.A:.6f} m²")
        print(f"v = Q/A = {self.Q:.3f}/{self.A:.6f} = {self.v:.4f} m/s")
        
        print("\n步骤2：计算雷诺数，判断流态")
        print(f"Re = vd/ν = ({self.v:.4f}×{self.d:.3f})/{self.nu:.2e}")
        print(f"   = {self.Re:.0f}")
        print(f"判断: Re = {self.Re:.0f} > 4000，流态为{self.flow_regime}")
        
        print("\n步骤3：计算相对粗糙度")
        print(f"Δ/d = {self.delta:.4f}/{self.d:.3f} = {self.rel_roughness:.6f}")
        
        print("\n步骤4：确定阻力系数λ（科尔布鲁克公式）")
        print(f"1/√λ = -2log₁₀(Δ/3.7d + 2.51/(Re√λ))")
        print(f"迭代求解得: λ = {self.lambda_f:.6f}")
        
        print("\n步骤5：计算沿程损失（达西公式）")
        print(f"h_f = λ(L/d)(v²/2g)")
        print(f"    = {self.lambda_f:.6f} × ({self.L}/{self.d:.3f}) × ({self.v:.4f}²/(2×{self.g}))")
        print(f"    = {self.lambda_f:.6f} × {self.L/self.d:.2f} × {self.v**2/(2*self.g):.6f}")
        print(f"    = {self.h_f:.4f} m")
        
        print("\n步骤6：计算局部损失")
        print(f"h_m = Σζ(v²/2g) = {self.sum_zeta} × {self.v**2/(2*self.g):.6f}")
        print(f"    = {self.h_m:.4f} m")
        
        print("\n步骤7：计算总损失")
        print(f"h = h_f + h_m = {self.h_f:.4f} + {self.h_m:.4f}")
        print(f"  = {self.h:.4f} m")
        
        print("\n【最终答案】")
        print(f"总水头损失: h = {self.h:.4f} m")
        print(f"  其中：沿程损失 h_f = {self.h_f:.4f} m ({self.ratio_f:.1f}%)")
        print(f"        局部损失 h_m = {self.h_m:.4f} m ({self.ratio_m:.1f}%)")
        
        print("\n【附加信息】")
        print(f"平均比降: i = h_f/L = {self.h_f/self.L:.6f} = {self.h_f/self.L*1000:.3f}‰")
        print(f"等效长度: L_eq = Σζ(d/λ) = {self.L_eq:.2f} m")
        print(f"  (局部损失相当于{self.L_eq:.1f}m管道的沿程损失)")
        print(f"总等效长度: L_total = L + L_eq = {self.L + self.L_eq:.2f} m")
        
        print("\n【解题要点】")
        print("✓ 第一类问题：直接计算，无需迭代")
        print("✓ 关键步骤：Re → λ → h_f → h_m → h")
        print("✓ 注意单位：d用m，Q用m³/s")
        print(f"✓ 本题λ={self.lambda_f:.4f}，可用莫迪图验证")
        
        print("=" * 85)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：管道示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_pipe(ax1)
        
        # 子图2：水头损失分布
        ax2 = plt.subplot(2, 2, 2)
        self._plot_head_loss(ax2)
        
        # 子图3：损失占比
        ax3 = plt.subplot(2, 2, 3)
        self._plot_loss_ratio(ax3)
        
        # 子图4：能量线
        ax4 = plt.subplot(2, 2, 4)
        self._plot_energy_line(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_pipe(self, ax):
        """绘制管道示意图"""
        pipe_height = 0.2
        
        # 管道
        pipe = Rectangle((0, -pipe_height/2), self.L/10, pipe_height,
                        facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(pipe)
        
        # 局部阻力（阀门、弯头等）
        n_local = int(self.sum_zeta)
        for i in range(n_local):
            x = self.L/10 * (i+1) / (n_local+1)
            valve = Rectangle((x-0.5, -pipe_height/2-0.05), 1, pipe_height+0.1,
                             facecolor='red', edgecolor='darkred', linewidth=1.5, alpha=0.5)
            ax.add_patch(valve)
            ax.text(x, pipe_height/2+0.15, '⊗', fontsize=16, ha='center', color='red')
        
        # 标注
        ax.text(self.L/20, pipe_height/2+0.08, f'L={self.L:.0f}m, d={self.d*1000:.0f}mm',
               fontsize=10, ha='center')
        ax.text(self.L/20, -pipe_height/2-0.15, f'Q={self.Q*1000:.0f}L/s, v={self.v:.2f}m/s',
               fontsize=10, ha='center', color='blue')
        
        # 流向箭头
        ax.arrow(self.L/10+1, 0, 1, 0, head_width=0.1, head_length=0.3,
                fc='darkblue', ec='darkblue', linewidth=2)
        ax.text(self.L/10+2.5, 0, '流向', fontsize=11, va='center', color='darkblue')
        
        ax.set_xlim(-2, self.L/10+4)
        ax.set_ylim(-0.4, 0.4)
        ax.set_aspect('equal')
        ax.set_title('管道系统示意图', fontsize=13, weight='bold')
        ax.axis('off')
    
    def _plot_head_loss(self, ax):
        """绘制水头损失分布"""
        categories = ['沿程损失\nh_f', '局部损失\nh_m', '总损失\nh']
        values = [self.h_f, self.h_m, self.h]
        colors = ['steelblue', 'coral', 'green']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.3f} m',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注公式
        formulas = ['λ(L/d)(v²/2g)', 'Σζ(v²/2g)', 'h_f + h_m']
        for i, (bar, formula) in enumerate(zip(bars, formulas)):
            ax.text(bar.get_x() + bar.get_width()/2, -max(values)*0.08,
                   formula, ha='center', va='top', fontsize=8, style='italic')
        
        ax.set_ylabel('水头损失 (m)', fontsize=11)
        ax.set_title('水头损失分析', fontsize=13, weight='bold')
        ax.set_ylim(0, max(values)*1.25)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_loss_ratio(self, ax):
        """绘制损失占比饼图"""
        sizes = [self.ratio_f, self.ratio_m]
        labels = [f'沿程损失\n{self.ratio_f:.1f}%', f'局部损失\n{self.ratio_m:.1f}%']
        colors = ['steelblue', 'coral']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels,
                                           colors=colors, autopct='%1.1f%%',
                                           startangle=90, textprops={'fontsize': 11})
        
        # 美化
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            autotext.set_fontsize(12)
        
        ax.set_title('损失占比分析', fontsize=13, weight='bold')
    
    def _plot_energy_line(self, ax):
        """绘制能量线和水力坡度线"""
        # 沿程位置
        x = np.linspace(0, self.L, 100)
        
        # 总水头线（直线下降）
        H_total = self.h * (1 - x/self.L)
        
        # 假设局部损失均匀分布
        h_f_dist = self.h_f * x / self.L
        h_m_dist = self.h_m * x / self.L
        
        # 测压管水头线（有突降）
        H_piezometric = H_total.copy()
        
        # 绘制总水头线
        ax.plot(x, H_total, 'b-', linewidth=2.5, label='总水头线（能量线）')
        
        # 绘制测压管水头线
        ax.plot(x, H_piezometric, 'r--', linewidth=2, label='测压管水头线')
        
        # 填充区域
        ax.fill_between(x, 0, H_total, alpha=0.2, color='lightblue')
        
        # 标注
        ax.text(self.L/2, self.h/2, f'总损失 h={self.h:.2f}m',
               fontsize=11, ha='center', rotation=-np.degrees(np.arctan(self.h/self.L)),
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 局部损失点（示意）
        n_local = int(self.sum_zeta)
        for i in range(n_local):
            x_local = self.L * (i+1) / (n_local+1)
            H_before = self.h * (1 - x_local/self.L)
            H_after = H_before - self.h_m / n_local
            ax.plot([x_local, x_local], [H_after, H_before], 'r-', linewidth=3)
            ax.plot(x_local, H_before, 'ro', markersize=6)
        
        ax.set_xlabel('管道轴向 (m)', fontsize=11)
        ax.set_ylabel('水头 (m)', fontsize=11)
        ax.set_title('能量线与水力坡度线', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.L)
        ax.set_ylim(0, self.h*1.1)


def test_problem_351():
    """测试题目351"""
    # 已知条件
    d = 0.2         # 管径 (m)
    L = 500         # 管长 (m)
    Q = 0.040       # 流量 (m³/s) = 40 L/s
    delta = 0.0003  # 粗糙度 (m) = 0.3 mm
    sum_zeta = 5.0  # 局部损失系数之和
    
    # 创建计算对象
    pipe = PipeType1(d, L, Q, delta, sum_zeta)
    
    # 打印结果
    pipe.print_results()
    
    # 可视化
    fig = pipe.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_351_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_351_result.png")
    
    # 验证答案（合理性检查）
    assert 0.5 < pipe.v < 5.0, "流速不合理"
    assert pipe.Re > 4000, "应该是湍流"
    assert 0 < pipe.h < 100, "水头损失不合理"
    assert pipe.h_f > 0 and pipe.h_m > 0, "各项损失必须为正"
    assert abs(pipe.h - pipe.h_f - pipe.h_m) < 0.001, "总损失不等于各项之和"
    
    print("\n✓ 所有测试通过！")
    print("\n【题型特点】")
    print("第一类问题（最简单）：")
    print("• 已知：Q、d（还有L、Δ、ζ）")
    print("• 求：h（水头损失）")
    print("• 方法：直接计算，v→Re→λ→h")
    print("• 难点：确定λ（莫迪图或科尔布鲁克）")


if __name__ == "__main__":
    test_problem_351()
