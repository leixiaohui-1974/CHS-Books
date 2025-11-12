"""
《水力学考研1000题详解》配套代码
题目126：伯努利方程基础应用

问题描述：
水平放置的管道，从直径d1=200mm逐渐收缩到d2=100mm。
1断面处的压强p1=150kPa，流速v1=2m/s。
假设理想流体，求2断面处的压强p2和流速v2。

考点：
1. 连续性方程：Q = v1*A1 = v2*A2
2. 伯努利方程：p1/γ + v1²/2g + z1 = p2/γ + v2²/2g + z2
3. 水平管道：z1 = z2

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrow
from matplotlib.patches import Rectangle

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BernoulliPipe:
    """伯努利方程计算类"""
    
    def __init__(self, d1, d2, p1, v1, gamma=9800):
        """
        初始化
        
        参数:
            d1: 断面1直径 (m)
            d2: 断面2直径 (m)
            p1: 断面1压强 (Pa)
            v1: 断面1流速 (m/s)
            gamma: 水的重度 (N/m³)
        """
        self.d1 = d1
        self.d2 = d2
        self.p1 = p1
        self.v1 = v1
        self.gamma = gamma
        self.g = 9.8
        
        # 计算断面面积
        self.A1 = np.pi * d1**2 / 4
        self.A2 = np.pi * d2**2 / 4
        
        # 执行计算
        self.calculate()
    
    def calculate(self):
        """执行流体力学计算"""
        # 1. 连续性方程求v2
        self.Q = self.v1 * self.A1  # 流量 (m³/s)
        self.v2 = self.Q / self.A2   # 断面2流速 (m/s)
        
        # 2. 伯努利方程求p2
        # p1/γ + v1²/2g = p2/γ + v2²/2g
        # p2 = p1 + γ(v1²/2g - v2²/2g)
        h1 = self.v1**2 / (2 * self.g)
        h2 = self.v2**2 / (2 * self.g)
        self.p2 = self.p1 + self.gamma * (h1 - h2)
        
        # 3. 计算水头
        self.pressure_head1 = self.p1 / self.gamma
        self.pressure_head2 = self.p2 / self.gamma
        self.velocity_head1 = h1
        self.velocity_head2 = h2
        self.total_head1 = self.pressure_head1 + self.velocity_head1
        self.total_head2 = self.pressure_head2 + self.velocity_head2
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("题目126：伯努利方程基础应用")
        print("=" * 70)
        
        print("\n【已知条件】")
        print(f"断面1直径: d₁ = {self.d1*1000:.0f} mm")
        print(f"断面2直径: d₂ = {self.d2*1000:.0f} mm")
        print(f"断面1压强: p₁ = {self.p1/1000:.0f} kPa")
        print(f"断面1流速: v₁ = {self.v1:.2f} m/s")
        
        print("\n【计算过程】")
        print("\n步骤1：连续性方程求v₂")
        print(f"A₁ = π×d₁²/4 = π×{self.d1}²/4 = {self.A1:.6f} m²")
        print(f"A₂ = π×d₂²/4 = π×{self.d2}²/4 = {self.A2:.6f} m²")
        print(f"Q = v₁A₁ = {self.v1} × {self.A1:.6f} = {self.Q:.6f} m³/s")
        print(f"v₂ = Q/A₂ = {self.Q:.6f}/{self.A2:.6f} = {self.v2:.3f} m/s")
        
        print("\n步骤2：伯努利方程求p₂")
        print(f"水平管道，z₁ = z₂")
        print(f"p₁/γ + v₁²/2g = p₂/γ + v₂²/2g")
        print(f"p₂ = p₁ + γ(v₁²/2g - v₂²/2g)")
        print(f"   = {self.p1} + {self.gamma} × ({self.v1}²/(2×{self.g}) - {self.v2:.3f}²/(2×{self.g}))")
        print(f"   = {self.p1} + {self.gamma} × ({self.velocity_head1:.4f} - {self.velocity_head2:.4f})")
        print(f"   = {self.p1} + {self.gamma * (self.velocity_head1 - self.velocity_head2):.2f}")
        print(f"   = {self.p2:.2f} Pa = {self.p2/1000:.2f} kPa")
        
        print("\n【最终答案】")
        print(f"断面2流速: v₂ = {self.v2:.3f} m/s")
        print(f"断面2压强: p₂ = {self.p2/1000:.2f} kPa")
        
        print("\n【水头分析】")
        print(f"断面1: 压强水头 = {self.pressure_head1:.3f} m, 速度水头 = {self.velocity_head1:.4f} m, 总水头 = {self.total_head1:.3f} m")
        print(f"断面2: 压强水头 = {self.pressure_head2:.3f} m, 速度水头 = {self.velocity_head2:.4f} m, 总水头 = {self.total_head2:.3f} m")
        print(f"总水头守恒验证: H₁ - H₂ = {abs(self.total_head1 - self.total_head2):.6f} m ≈ 0 ✓")
        
        print("\n【物理意义】")
        print("• 管道收缩，流速增大（v₂ > v₁）")
        print("• 速度水头增加，压强水头减小")
        print("• 总水头不变（理想流体）")
        print("• 这就是文丘里效应！")
        
        print("=" * 70)
    
    def visualize(self):
        """可视化管道流动"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：管道示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_pipe(ax1)
        
        # 子图2：水头线
        ax2 = plt.subplot(2, 2, 2)
        self._plot_heads(ax2)
        
        # 子图3：流速分布
        ax3 = plt.subplot(2, 2, 3)
        self._plot_velocity(ax3)
        
        # 子图4：压强分布
        ax4 = plt.subplot(2, 2, 4)
        self._plot_pressure(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_pipe(self, ax):
        """绘制管道示意图"""
        # 管道长度和高度
        L1, L2, L3 = 3, 2, 3  # 三段长度
        H1, H2 = self.d1, self.d2
        
        # 绘制管道（上壁面）
        x_upper = [0, L1, L1+L2, L1+L2+L3]
        y_upper = [H1/2, H1/2, H2/2, H2/2]
        
        # 绘制管道（下壁面）
        x_lower = x_upper
        y_lower = [-H1/2, -H1/2, -H2/2, -H2/2]
        
        ax.plot(x_upper, y_upper, 'b-', linewidth=2)
        ax.plot(x_lower, y_lower, 'b-', linewidth=2)
        ax.plot([0, 0], [y_lower[0], y_upper[0]], 'b-', linewidth=2)
        ax.plot([L1+L2+L3, L1+L2+L3], [y_lower[-1], y_upper[-1]], 'b-', linewidth=2)
        
        # 渐变段
        ax.fill([L1, L1+L2, L1+L2, L1], 
                [H1/2, H2/2, -H2/2, -H1/2], 
                color='lightblue', alpha=0.3)
        
        # 断面1和断面2
        x1 = L1 / 2
        x2 = L1 + L2 + L3/2
        
        # 绘制断面线
        ax.plot([x1, x1], [-H1/2, H1/2], 'r--', linewidth=2, label='断面1')
        ax.plot([x2, x2], [-H2/2, H2/2], 'g--', linewidth=2, label='断面2')
        
        # 标注
        ax.text(x1, H1/2 + 0.05, '1', fontsize=14, color='red', ha='center', weight='bold')
        ax.text(x2, H2/2 + 0.05, '2', fontsize=14, color='green', ha='center', weight='bold')
        
        # 流速箭头
        arrow_props = dict(arrowstyle='->', lw=2)
        ax.annotate('', xy=(x1+0.5, 0), xytext=(x1-0.5, 0),
                   arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        ax.text(x1, -H1/2-0.08, f'v₁={self.v1:.1f}m/s', fontsize=10, ha='center', color='red')
        
        ax.annotate('', xy=(x2+0.5, 0), xytext=(x2-0.5, 0),
                   arrowprops=dict(arrowstyle='->', lw=2, color='green'))
        ax.text(x2, -H2/2-0.08, f'v₂={self.v2:.1f}m/s', fontsize=10, ha='center', color='green')
        
        # 尺寸标注
        ax.text(x1-0.3, 0, f'd₁={self.d1*1000:.0f}mm', fontsize=9, rotation=90, va='center')
        ax.text(x2+0.3, 0, f'd₂={self.d2*1000:.0f}mm', fontsize=9, rotation=90, va='center')
        
        ax.set_xlim(-0.5, L1+L2+L3+0.5)
        ax.set_ylim(-0.3, 0.3)
        ax.set_aspect('equal')
        ax.set_xlabel('管道轴向 (m)', fontsize=12)
        ax.set_ylabel('管道半径 (m)', fontsize=12)
        ax.set_title('管道几何与流速', fontsize=14, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_heads(self, ax):
        """绘制水头线"""
        x = [1, 2]
        
        # 总水头线（水平）
        total_head = [self.total_head1, self.total_head2]
        ax.plot(x, total_head, 'b-', linewidth=3, marker='o', markersize=10, label='总水头线')
        
        # 测压管水头线（压强水头）
        pressure_head = [self.pressure_head1, self.pressure_head2]
        ax.plot(x, pressure_head, 'r--', linewidth=2, marker='s', markersize=8, label='测压管水头线')
        
        # 速度水头（填充）
        ax.fill_between(x, pressure_head, total_head, alpha=0.3, color='green', label='速度水头')
        
        # 标注数值
        ax.text(1, self.total_head1, f'{self.total_head1:.3f}m', fontsize=10, ha='right', va='bottom')
        ax.text(2, self.total_head2, f'{self.total_head2:.3f}m', fontsize=10, ha='left', va='bottom')
        ax.text(1, self.pressure_head1, f'{self.pressure_head1:.3f}m', fontsize=10, ha='right', va='top')
        ax.text(2, self.pressure_head2, f'{self.pressure_head2:.3f}m', fontsize=10, ha='left', va='top')
        
        # 标注速度水头
        ax.text(1.5, (self.pressure_head1+self.total_head1)/2, 
                f'v²/2g', fontsize=10, ha='center', va='center', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xticks(x)
        ax.set_xticklabels(['断面1', '断面2'], fontsize=11)
        ax.set_ylabel('水头 (m)', fontsize=12)
        ax.set_title('伯努利方程水头线', fontsize=14, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_velocity(self, ax):
        """绘制流速对比"""
        sections = ['断面1', '断面2']
        velocities = [self.v1, self.v2]
        colors = ['red', 'green']
        
        bars = ax.bar(sections, velocities, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, v in zip(bars, velocities):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{v:.3f} m/s',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注比值
        ratio = self.v2 / self.v1
        ax.text(0.5, max(velocities)*0.9, 
                f'v₂/v₁ = {ratio:.2f}\n(流速增加{(ratio-1)*100:.1f}%)',
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        ax.set_ylabel('流速 (m/s)', fontsize=12)
        ax.set_title('流速对比', fontsize=14, weight='bold')
        ax.set_ylim(0, max(velocities)*1.2)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_pressure(self, ax):
        """绘制压强对比"""
        sections = ['断面1', '断面2']
        pressures = [self.p1/1000, self.p2/1000]  # kPa
        colors = ['red', 'green']
        
        bars = ax.bar(sections, pressures, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, p in zip(bars, pressures):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{p:.2f} kPa',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注变化
        delta_p = self.p2 - self.p1
        ax.text(0.5, min(pressures)*1.1, 
                f'Δp = {delta_p/1000:.2f} kPa\n(压强{"增加" if delta_p>0 else "减小"}{abs(delta_p/1000):.2f} kPa)',
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        ax.set_ylabel('压强 (kPa)', fontsize=12)
        ax.set_title('压强对比', fontsize=14, weight='bold')
        ax.set_ylim(0, max(pressures)*1.3)
        ax.grid(True, axis='y', alpha=0.3)


def test_problem_126():
    """测试题目126"""
    # 已知条件
    d1 = 0.2       # 断面1直径 (m)
    d2 = 0.1       # 断面2直径 (m)
    p1 = 150000    # 断面1压强 (Pa)
    v1 = 2.0       # 断面1流速 (m/s)
    
    # 创建计算对象
    pipe = BernoulliPipe(d1, d2, p1, v1)
    
    # 打印结果
    pipe.print_results()
    
    # 可视化
    fig = pipe.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_126_result.png', 
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_126_result.png")
    
    # 验证答案
    assert abs(pipe.v2 - 8.0) < 0.1, "流速计算错误"
    assert abs(pipe.p2/1000 - 120.0) < 5.0, "压强计算错误"
    assert abs(pipe.total_head1 - pipe.total_head2) < 0.001, "总水头不守恒"
    
    print("\n✓ 所有测试通过！")


if __name__ == "__main__":
    test_problem_126()
