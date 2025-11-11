"""
《水力学考研1000题详解》配套代码
题目136：文丘里管流量测量

问题描述：
水平文丘里管，喉部直径d2=50mm，入口直径d1=100mm。
水银差压计读数Δh=200mm。
求：(1) 管道流量Q
    (2) 喉部流速v2
    (3) 入口流速v1

考点：
1. 连续性方程：v1A1 = v2A2
2. 伯努利方程：p1/γ + v1²/2g = p2/γ + v2²/2g
3. 压差计：Δp = (ρ_Hg - ρ_水)gΔh
4. 文丘里系数μ（考虑损失，取0.98）

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyBboxPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class VenturiMeter:
    """文丘里管流量计算类"""
    
    def __init__(self, d1, d2, delta_h, mu=0.98, rho_Hg=13600, rho=1000):
        """
        初始化
        
        参数:
            d1: 入口直径 (m)
            d2: 喉部直径 (m)
            delta_h: 水银差压计读数 (m)
            mu: 文丘里系数（流量系数）
            rho_Hg: 水银密度 (kg/m³)
            rho: 水的密度 (kg/m³)
        """
        self.d1 = d1
        self.d2 = d2
        self.delta_h = delta_h
        self.mu = mu
        self.rho_Hg = rho_Hg
        self.rho = rho
        self.g = 9.8
        self.gamma = rho * self.g
        
        # 执行计算
        self.calculate()
    
    def calculate(self):
        """执行流量计算"""
        # 1. 断面面积
        self.A1 = np.pi * self.d1**2 / 4
        self.A2 = np.pi * self.d2**2 / 4
        
        # 2. 面积比
        self.m = self.A2 / self.A1  # m < 1
        
        # 3. 压差计算
        self.delta_p = (self.rho_Hg - self.rho) * self.g * self.delta_h
        
        # 4. 理论流速（伯努利方程+连续性方程）
        # v2 = √[2Δp/(ρ(1-m²))]
        self.v2_theory = np.sqrt(2 * self.delta_p / (self.rho * (1 - self.m**2)))
        
        # 5. 实际流速（考虑系数μ）
        self.v2 = self.mu * self.v2_theory
        
        # 6. 入口流速（连续性方程）
        self.v1 = self.v2 * self.m
        
        # 7. 流量
        self.Q = self.v2 * self.A2
        
        # 8. 压强差（通过伯努利验证）
        self.p1_minus_p2 = self.rho * (self.v2**2 - self.v1**2) / 2
        
        # 9. 雷诺数（在喉部）
        self.nu = 1.0e-6  # 20°C水的运动粘度
        self.Re2 = self.v2 * self.d2 / self.nu
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 80)
        print("题目136：文丘里管流量测量")
        print("=" * 80)
        
        print("\n【已知条件】")
        print(f"入口直径: d₁ = {self.d1*1000:.0f} mm = {self.d1:.3f} m")
        print(f"喉部直径: d₂ = {self.d2*1000:.0f} mm = {self.d2:.3f} m")
        print(f"水银差压计读数: Δh = {self.delta_h*1000:.0f} mm = {self.delta_h:.3f} m")
        print(f"文丘里系数: μ = {self.mu:.2f}")
        print(f"水银密度: ρ_Hg = {self.rho_Hg} kg/m³")
        print(f"水的密度: ρ = {self.rho} kg/m³")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算断面面积")
        print(f"A₁ = πd₁²/4 = π×{self.d1}²/4 = {self.A1:.6f} m²")
        print(f"A₂ = πd₂²/4 = π×{self.d2}²/4 = {self.A2:.6f} m²")
        print(f"面积比: m = A₂/A₁ = {self.m:.4f}")
        
        print("\n步骤2：计算压差")
        print(f"Δp = (ρ_Hg - ρ)gΔh")
        print(f"   = ({self.rho_Hg} - {self.rho}) × {self.g} × {self.delta_h}")
        print(f"   = {self.rho_Hg - self.rho} × {self.g} × {self.delta_h}")
        print(f"   = {self.delta_p:.2f} Pa = {self.delta_p/1000:.2f} kPa")
        
        print("\n步骤3：伯努利方程+连续性方程推导")
        print("伯努利: p₁/ρ + v₁²/2 = p₂/ρ + v₂²/2")
        print("连续性: v₁A₁ = v₂A₂  →  v₁ = v₂(A₂/A₁) = v₂m")
        print("联立得: Δp = p₁ - p₂ = ρ(v₂² - v₁²)/2 = ρv₂²(1 - m²)/2")
        print(f"理论流速: v₂ = √[2Δp/(ρ(1-m²))]")
        print(f"        = √[2×{self.delta_p}/(${self.rho}×(1-{self.m:.4f}²))]")
        print(f"        = √[{2*self.delta_p}/{self.rho*(1-self.m**2):.2f}]")
        print(f"        = {self.v2_theory:.4f} m/s")
        
        print("\n步骤4：考虑文丘里系数")
        print(f"实际流速: v₂ = μ × v₂_理论 = {self.mu} × {self.v2_theory:.4f}")
        print(f"        = {self.v2:.4f} m/s")
        
        print("\n步骤5：计算入口流速")
        print(f"v₁ = v₂ × m = {self.v2:.4f} × {self.m:.4f}")
        print(f"   = {self.v1:.4f} m/s")
        
        print("\n步骤6：计算流量")
        print(f"Q = v₂A₂ = {self.v2:.4f} × {self.A2:.6f}")
        print(f"  = {self.Q:.6f} m³/s = {self.Q*1000:.3f} L/s")
        
        print("\n【最终答案】")
        print(f"(1) 流量: Q = {self.Q:.6f} m³/s = {self.Q*1000:.3f} L/s")
        print(f"(2) 喉部流速: v₂ = {self.v2:.4f} m/s")
        print(f"(3) 入口流速: v₁ = {self.v1:.4f} m/s")
        
        print("\n【附加信息】")
        print(f"流速比: v₂/v₁ = {self.v2/self.v1:.2f}")
        print(f"压差: Δp = {self.delta_p/1000:.2f} kPa")
        print(f"喉部雷诺数: Re₂ = {self.Re2:.0f} (湍流)")
        print(f"理论误差: (v₂_实际/v₂_理论 - 1) = {(self.v2/self.v2_theory - 1)*100:.1f}%")
        
        print("\n【文丘里管特点】")
        print("✓ 收缩段：流速增大，压强降低")
        print("✓ 喉部：流速最大，压强最小")
        print("✓ 扩散段：压强恢复，损失小")
        print("✓ 优点：测量精度高，损失小（μ≈0.98）")
        
        print("=" * 80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：文丘里管结构
        ax1 = plt.subplot(2, 2, 1)
        self._plot_venturi(ax1)
        
        # 子图2：压强分布
        ax2 = plt.subplot(2, 2, 2)
        self._plot_pressure(ax2)
        
        # 子图3：流速分布
        ax3 = plt.subplot(2, 2, 3)
        self._plot_velocity(ax3)
        
        # 子图4：差压计原理
        ax4 = plt.subplot(2, 2, 4)
        self._plot_manometer(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_venturi(self, ax):
        """绘制文丘里管结构"""
        # 文丘里管轮廓
        L_in = 3      # 入口段
        L_con = 2     # 收缩段
        L_throat = 1  # 喉部
        L_exp = 4     # 扩散段
        
        r1 = self.d1 / 2
        r2 = self.d2 / 2
        
        # 上轮廓
        x_upper = [0, L_in, L_in+L_con, L_in+L_con+L_throat, L_in+L_con+L_throat+L_exp]
        y_upper = [r1, r1, r2, r2, r1]
        
        # 下轮廓
        y_lower = [-y for y in y_upper]
        
        # 绘制管壁
        ax.plot(x_upper, y_upper, 'b-', linewidth=2.5)
        ax.plot(x_upper, y_lower, 'b-', linewidth=2.5)
        ax.plot([0, 0], [y_lower[0], y_upper[0]], 'b-', linewidth=2.5)
        ax.plot([x_upper[-1], x_upper[-1]], [y_lower[-1], y_upper[-1]], 'b-', linewidth=2.5)
        
        # 填充水流
        vertices = [(x, y_upper[i]) for i, x in enumerate(x_upper)] + \
                   [(x, y_lower[i]) for i, x in enumerate(reversed(x_upper))]
        poly = Polygon(vertices, facecolor='lightblue', edgecolor='none', alpha=0.5)
        ax.add_patch(poly)
        
        # 标注断面1（入口）
        x1 = L_in / 2
        ax.plot([x1, x1], [-r1, r1], 'r--', linewidth=2, label='断面1')
        ax.text(x1, r1+0.03, '①', fontsize=14, color='red', ha='center', weight='bold')
        ax.text(x1, -r1-0.05, f'd₁={self.d1*1000:.0f}mm', fontsize=9, ha='center')
        
        # 标注断面2（喉部）
        x2 = L_in + L_con + L_throat/2
        ax.plot([x2, x2], [-r2, r2], 'g--', linewidth=2, label='断面2 (喉部)')
        ax.text(x2, r2+0.03, '②', fontsize=14, color='green', ha='center', weight='bold')
        ax.text(x2, -r2-0.05, f'd₂={self.d2*1000:.0f}mm', fontsize=9, ha='center')
        
        # 流向箭头
        n_arrows = 8
        for i in range(n_arrows):
            x_arr = x_upper[-1] * (i + 0.5) / n_arrows
            # 根据位置插值半径
            if x_arr < L_in:
                r = r1
            elif x_arr < L_in + L_con:
                r = r1 - (r1-r2)*(x_arr-L_in)/L_con
            elif x_arr < L_in + L_con + L_throat:
                r = r2
            else:
                r = r2 + (r1-r2)*(x_arr-L_in-L_con-L_throat)/L_exp
            
            ax.arrow(x_arr-0.15, 0, 0.3, 0, head_width=r*0.3, head_length=0.08,
                    fc='darkblue', ec='darkblue', alpha=0.6)
        
        # 测压孔
        ax.plot([x1, x1], [r1, r1+0.15], 'k-', linewidth=1.5)
        ax.plot(x1, r1+0.15, 'ko', markersize=4)
        ax.text(x1, r1+0.2, 'p₁', fontsize=10, ha='center')
        
        ax.plot([x2, x2], [r2, r2+0.15], 'k-', linewidth=1.5)
        ax.plot(x2, r2+0.15, 'ko', markersize=4)
        ax.text(x2, r2+0.2, 'p₂', fontsize=10, ha='center')
        
        # 标注段落
        ax.text(L_in/2, r1+0.12, '入口段', fontsize=9, ha='center', style='italic')
        ax.text(L_in+L_con/2, 0.12, '收缩段', fontsize=9, ha='center', style='italic')
        ax.text(L_in+L_con+L_throat/2, 0, '喉部', fontsize=8, ha='center', 
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        ax.text(L_in+L_con+L_throat+L_exp/2, 0.12, '扩散段', fontsize=9, ha='center', style='italic')
        
        ax.set_xlim(-0.5, x_upper[-1]+0.5)
        ax.set_ylim(-0.15, 0.3)
        ax.set_aspect('equal')
        ax.set_xlabel('管道轴向', fontsize=11)
        ax.set_title('文丘里管结构', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_pressure(self, ax):
        """绘制压强分布"""
        positions = ['入口①', '喉部②']
        # 假设入口压强为100 kPa（相对值）
        p1 = 100
        p2 = p1 - self.delta_p/1000
        pressures = [p1, p2]
        colors = ['red', 'green']
        
        bars = ax.bar(positions, pressures, color=colors, alpha=0.7, 
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, p in zip(bars, pressures):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{p:.1f} kPa',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注压差
        ax.annotate('', xy=(0.5, p2), xytext=(0.5, p1),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax.text(0.7, (p1+p2)/2, f'Δp={self.delta_p/1000:.1f}kPa',
               fontsize=10, color='blue', weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax.set_ylabel('压强 (kPa)', fontsize=11)
        ax.set_title('压强对比', fontsize=13, weight='bold')
        ax.set_ylim(0, max(pressures)*1.2)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_velocity(self, ax):
        """绘制流速分布"""
        positions = ['入口①', '喉部②']
        velocities = [self.v1, self.v2]
        colors = ['red', 'green']
        
        bars = ax.bar(positions, velocities, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, v in zip(bars, velocities):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{v:.3f} m/s',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注比值
        ax.text(0.5, max(velocities)*0.85,
               f'v₂/v₁ = {self.v2/self.v1:.2f}\n(流速增加{(self.v2/self.v1-1)*100:.0f}%)',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_ylabel('流速 (m/s)', fontsize=11)
        ax.set_title('流速对比', fontsize=13, weight='bold')
        ax.set_ylim(0, max(velocities)*1.2)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_manometer(self, ax):
        """绘制差压计原理"""
        # U型管
        tube_width = 0.3
        tube_height = 2.5
        
        # 左管
        ax.plot([1, 1, 1.5], [tube_height, 0.5, 0.5], 'k-', linewidth=2.5)
        # 右管
        ax.plot([2.5, 2.5, 2], [tube_height, 0.5, 0.5], 'k-', linewidth=2.5)
        # 底部连接
        ax.plot([1.5, 2], [0.5, 0.5], 'k-', linewidth=2.5)
        
        # 水银液面
        h_Hg = 0.8
        h_water_left = h_Hg + self.delta_h * 5  # 放大显示
        h_water_right = h_Hg
        
        # 水银（红色）
        ax.fill([1, 1.5, 2, 2.5, 2.5, 1], 
               [0.5, 0.5, 0.5, 0.5, h_Hg, h_Hg],
               color='red', alpha=0.6, label='水银')
        
        # 水（蓝色）
        ax.fill([1, 1, 1, 1], [h_Hg, h_water_left, h_water_left, h_Hg],
               color='lightblue', alpha=0.6)
        ax.fill([2.5, 2.5, 2.5, 2.5], [h_Hg, h_water_right, h_water_right, h_Hg],
               color='lightblue', alpha=0.6, label='水')
        
        # 标注
        ax.text(0.7, h_water_left, 'p₁', fontsize=12, ha='right', weight='bold')
        ax.text(2.8, h_water_right, 'p₂', fontsize=12, ha='left', weight='bold')
        
        # 水银高度差
        ax.plot([3, 3], [h_Hg, h_water_left], 'g-', linewidth=2)
        ax.plot([2.9, 3.1], [h_Hg, h_Hg], 'g-', linewidth=1.5)
        ax.plot([2.9, 3.1], [h_water_left, h_water_left], 'g-', linewidth=1.5)
        ax.text(3.3, (h_Hg+h_water_left)/2, f'Δh={self.delta_h*1000:.0f}mm',
               fontsize=10, color='green', weight='bold', rotation=90, va='center')
        
        # 公式
        ax.text(2, 2.2, 'Δp = (ρ_Hg - ρ_水)gΔh',
               fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.set_xlim(0.5, 4)
        ax.set_ylim(0, 2.5)
        ax.set_aspect('equal')
        ax.set_title('水银差压计原理', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.axis('off')


def test_problem_136():
    """测试题目136"""
    # 已知条件
    d1 = 0.1        # 入口直径 (m)
    d2 = 0.05       # 喉部直径 (m)
    delta_h = 0.2   # 水银差压计读数 (m)
    
    # 创建计算对象
    venturi = VenturiMeter(d1, d2, delta_h)
    
    # 打印结果
    venturi.print_results()
    
    # 可视化
    fig = venturi.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_136_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_136_result.png")
    
    # 验证答案（合理性检查）
    assert 0.5 < venturi.v2 < 10.0, "喉部流速不合理"
    assert venturi.v2 > venturi.v1, "喉部流速应大于入口流速"
    assert venturi.Q > 0, "流量必须为正"
    assert venturi.delta_p > 0, "压差必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【物理原理】")
    print("文丘里管利用伯努利方程测流量：")
    print("• 收缩段：A↓ → v↑ → p↓")
    print("• 测量Δp即可计算流量")
    print("• 优点：精度高、损失小")


if __name__ == "__main__":
    test_problem_136()
