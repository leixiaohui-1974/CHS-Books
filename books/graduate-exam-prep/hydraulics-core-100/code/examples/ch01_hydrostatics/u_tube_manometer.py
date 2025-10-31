"""
水力学考研核心100题 - 第一章题目11
U型管压差计计算与可视化

功能：
1. 使用等压面法计算压差
2. 绘制U型管示意图
3. 可视化压强传递过程

难度：强化
考频：⭐⭐⭐⭐⭐

作者：CHS-Books考研系列
更新：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class UTubeManometer:
    """U型管压差计类"""

    def __init__(self, h1, h2, dh, rho1=1000, rho2=13600, g=9.81):
        """
        初始化U型管压差计

        Parameters:
        -----------
        h1 : float
            A点上方水柱高度 (m)
        h2 : float
            B点上方水柱高度 (m)
        dh : float
            水银面高差 (m)
        rho1 : float
            水密度 (kg/m³)
        rho2 : float
            水银密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.h1 = h1
        self.h2 = h2
        self.dh = dh
        self.rho1 = rho1
        self.rho2 = rho2
        self.g = g

    def calculate_pressure_difference(self):
        """
        使用等压面法计算压差

        Returns:
        --------
        float : 压差 pA - pB (Pa)
        """
        # 等压面法：
        # 左侧：p0 = pA + rho1*g*h1
        # 右侧：p0 = pB + rho1*g*h2 + rho2*g*dh
        # 因此：pA - pB = rho1*g*(h2 - h1) + rho2*g*dh

        dp = self.g * (self.rho1 * (self.h2 - self.h1) + self.rho2 * self.dh)
        return dp

    def print_solution_steps(self):
        """打印详细求解步骤"""
        dp = self.calculate_pressure_difference()

        print("=" * 75)
        print("U型管压差计 - 等压面法求解")
        print("=" * 75)

        print("\n【已知条件】")
        print(f"  h₁ (A点上方水柱高度) = {self.h1} m")
        print(f"  h₂ (B点上方水柱高度) = {self.h2} m")
        print(f"  Δh (水银面高差) = {self.dh} m")
        print(f"  ρ₁ (水) = {self.rho1} kg/m³")
        print(f"  ρ₂ (水银) = {self.rho2} kg/m³")
        print(f"  g (重力加速度) = {self.g} m/s²")

        print("\n【求解步骤】")
        print("\n步骤1：选择等压面")
        print("  选择U型管左侧水银面为等压面0-0")
        print("  （关键：等压面必须在同种液体的同一水平面）")

        print("\n步骤2：从A点向下列压强方程")
        print("  在0-0面（左侧水银面）：")
        print("  p₀ = pₐ + ρ₁g·h₁  ......(1)")

        print("\n步骤3：从B点向下列压强方程")
        print("  在0-0面同一水平（右侧）：")
        print("  p₀ = pᵦ + ρ₁g·h₂ + ρ₂g·Δh  ......(2)")
        print("  （注意：右侧要考虑水银高差Δh的压强）")

        print("\n步骤4：利用等压面条件")
        print("  因为0-0面是等压面，所以：p₀(左) = p₀(右)")
        print("  即：pₐ + ρ₁g·h₁ = pᵦ + ρ₁g·h₂ + ρ₂g·Δh")

        print("\n步骤5：求解压差")
        print("  pₐ - pᵦ = ρ₁g·h₂ - ρ₁g·h₁ + ρ₂g·Δh")
        print("         = ρ₁g(h₂ - h₁) + ρ₂g·Δh")
        print("         = g[ρ₁(h₂ - h₁) + ρ₂·Δh]")

        print("\n步骤6：代入数值计算")
        term1 = self.rho1 * (self.h2 - self.h1)
        term2 = self.rho2 * self.dh
        print(f"  pₐ - pᵦ = {self.g} × [{self.rho1}×({self.h2} - {self.h1}) + {self.rho2}×{self.dh}]")
        print(f"         = {self.g} × [{term1:.0f} + {term2:.0f}]")
        print(f"         = {self.g} × {term1 + term2:.0f}")
        print(f"         = {dp:.1f} Pa")
        print(f"         = {dp/1000:.2f} kPa")

        print("\n【结论】")
        if dp > 0:
            print(f"  pₐ - pᵦ = {dp/1000:.2f} kPa > 0")
            print("  说明：A点压强大于B点压强")
        elif dp < 0:
            print(f"  pₐ - pᵦ = {dp/1000:.2f} kPa < 0")
            print("  说明：B点压强大于A点压强")
        else:
            print("  pₐ = pᵦ，两点压强相等")

        print("\n【评分要点】（12分）")
        print("  ✓ 选择等压面正确 (2分)")
        print("  ✓ A侧压强方程 (3分)")
        print("  ✓ B侧压强方程 (3分)")
        print("  ✓ 等压面条件 (2分)")
        print("  ✓ 最终结果 (2分)")

        print("\n" + "=" * 75)

        return dp

    def plot_diagram(self, save_fig=True):
        """
        绘制U型管示意图

        Parameters:
        -----------
        save_fig : bool
            是否保存图片
        """
        dp = self.calculate_pressure_difference()

        fig = plt.figure(figsize=(14, 10))
        ax = plt.subplot(111)

        # ===== 几何参数 =====
        tube_width = 0.08
        tube_spacing = 0.9
        hg_base = 1.0        # 水银基准高度
        water_base = hg_base + 0.15  # 水柱起始高度

        left_center = -tube_spacing / 2
        right_center = tube_spacing / 2

        # ===== 绘制U型管道 =====
        # 底部连接管
        bottom = patches.Rectangle(
            (left_center - tube_width/2, hg_base - 0.25),
            tube_spacing + tube_width, 0.25,
            linewidth=3, edgecolor='black', facecolor='lightgray',
            zorder=5
        )
        ax.add_patch(bottom)

        # 左侧管道
        left_height = water_base + self.h1 + 0.2
        left_tube = patches.Rectangle(
            (left_center - tube_width/2, hg_base - 0.25),
            tube_width, left_height,
            linewidth=3, edgecolor='black', facecolor='none',
            zorder=10
        )
        ax.add_patch(left_tube)

        # 右侧管道
        right_height = water_base + self.dh + self.h2 + 0.2
        right_tube = patches.Rectangle(
            (right_center - tube_width/2, hg_base - 0.25),
            tube_width, right_height,
            linewidth=3, edgecolor='black', facecolor='none',
            zorder=10
        )
        ax.add_patch(right_tube)

        # ===== 绘制液体 =====
        # 左侧水银
        hg_left_height = 0.15
        hg_left = patches.Rectangle(
            (left_center - tube_width/2, hg_base),
            tube_width, hg_left_height,
            facecolor='silver', edgecolor='darkgray', linewidth=1.5,
            alpha=0.9, zorder=8, label='水银'
        )
        ax.add_patch(hg_left)

        # 右侧水银（高出dh）
        hg_right_height = hg_left_height + self.dh
        hg_right = patches.Rectangle(
            (right_center - tube_width/2, hg_base),
            tube_width, hg_right_height,
            facecolor='silver', edgecolor='darkgray', linewidth=1.5,
            alpha=0.9, zorder=8
        )
        ax.add_patch(hg_right)

        # 左侧水柱
        water_left = patches.Rectangle(
            (left_center - tube_width/2, water_base),
            tube_width, self.h1,
            facecolor='lightblue', edgecolor='blue', linewidth=1.5,
            alpha=0.7, zorder=7, label='水'
        )
        ax.add_patch(water_left)

        # 右侧水柱
        water_right = patches.Rectangle(
            (right_center - tube_width/2, water_base + self.dh),
            tube_width, self.h2,
            facecolor='lightblue', edgecolor='blue', linewidth=1.5,
            alpha=0.7, zorder=7
        )
        ax.add_patch(water_right)

        # ===== 标注测点A和B =====
        # A点
        yA = water_base
        ax.plot(left_center, yA, 'ro', markersize=14, zorder=15, label='A点')
        ax.text(left_center - 0.22, yA, 'A', fontsize=16,
               fontweight='bold', color='red', zorder=20)

        # B点
        yB = water_base + self.dh
        ax.plot(right_center, yB, 'bo', markersize=14, zorder=15, label='B点')
        ax.text(right_center + 0.15, yB, 'B', fontsize=16,
               fontweight='bold', color='blue', zorder=20)

        # ===== 等压面0-0 =====
        ax.plot([left_center - 0.25, right_center + 0.25],
               [hg_base, hg_base],
               'g--', linewidth=2.5, zorder=12, label='等压面0-0')
        ax.text(-0.65, hg_base - 0.06, '等压面0-0',
               fontsize=12, color='green', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

        # ===== 尺寸标注 =====
        arrow_props = dict(arrowstyle='<->', lw=2.5)

        # h1标注
        x_h1 = left_center + 0.16
        ax.annotate('', xy=(x_h1, yA), xytext=(x_h1, yA + self.h1),
                   arrowprops={**arrow_props, 'color': 'red'})
        ax.text(x_h1 + 0.03, yA + self.h1/2, f'h₁={self.h1}m',
               fontsize=12, color='red', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # h2标注
        x_h2 = right_center + 0.16
        ax.annotate('', xy=(x_h2, yB), xytext=(x_h2, yB + self.h2),
                   arrowprops={**arrow_props, 'color': 'blue'})
        ax.text(x_h2 + 0.03, yB + self.h2/2, f'h₂={self.h2}m',
               fontsize=12, color='blue', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Δh标注
        x_dh = 0
        ax.annotate('', xy=(x_dh, hg_base + hg_left_height),
                   xytext=(x_dh, hg_base + hg_right_height),
                   arrowprops={**arrow_props, 'color': 'purple'})
        ax.text(x_dh + 0.03, hg_base + hg_left_height + self.dh/2,
               f'Δh={self.dh}m',
               fontsize=12, color='purple', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # ===== 图表设置 =====
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(0.6, max(left_height, right_height) + 0.1)
        ax.set_aspect('equal')
        ax.axis('off')

        title_text = (
            f'U型管压差计示意图\n'
            f'pₐ - pᵦ = {dp/1000:.2f} kPa '
            f'{"(A点压强较大)" if dp > 0 else "(B点压强较大)" if dp < 0 else ""}'
        )
        ax.set_title(title_text, fontsize=16, fontweight='bold', pad=20)

        # 添加图例
        ax.legend(loc='upper left', fontsize=11,
                 bbox_to_anchor=(0.02, 0.98),
                 framealpha=0.9)

        # ===== 添加计算公式框 =====
        formula_text = (
            "【等压面法求解】\n\n"
            f"左侧: p₀ = pₐ + ρ₁gh₁\n"
            f"右侧: p₀ = pᵦ + ρ₁gh₂ + ρ₂gΔh\n\n"
            f"∴ pₐ - pᵦ = ρ₁g(h₂ - h₁) + ρ₂gΔh\n"
            f"  = g[ρ₁(h₂ - h₁) + ρ₂·Δh]\n"
            f"  = {self.g}×[{self.rho1}×{self.h2 - self.h1:.1f}\n"
            f"     + {self.rho2}×{self.dh}]\n"
            f"  = {dp/1000:.2f} kPa"
        )
        ax.text(0.02, 0.28, formula_text,
               transform=ax.transAxes,
               fontsize=10,
               verticalalignment='top',
               family='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat',
                        alpha=0.85, pad=0.8))

        plt.tight_layout()

        if save_fig:
            plt.savefig('u_tube_manometer.png',
                       dpi=300, bbox_inches='tight', facecolor='white')
            print("\n✅ 图表已保存为 'u_tube_manometer.png'")

        plt.show()


def main():
    """主函数"""

    print("\n")
    print("*" * 75)
    print("水力学考研核心100题 - 第一章题目11")
    print("U型管压差计（强化题）")
    print("*" * 75)
    print("\n")

    # ===== 创建U型管对象 =====
    utube = UTubeManometer(
        h1=0.5,      # A点上方水柱高度 (m)
        h2=0.3,      # B点上方水柱高度 (m)
        dh=0.15,     # 水银面高差 (m)
        rho1=1000,   # 水密度 (kg/m³)
        rho2=13600,  # 水银密度 (kg/m³)
        g=9.81       # 重力加速度 (m/s²)
    )

    # ===== 打印求解步骤 =====
    dp = utube.print_solution_steps()

    # ===== 绘制示意图 =====
    print("\n正在生成U型管示意图...")
    utube.plot_diagram()

    # ===== 练习提示 =====
    print("\n" + "=" * 75)
    print("【易错点总结】")
    print("=" * 75)
    print("⚠️  易错1：等压面选择错误")
    print("   → 必须在同种液体（水银）的同一水平面")
    print("\n⚠️  易错2：压强传递方向搞反")
    print("   → 向下传递：压强增大（+ρgh）")
    print("   → 向上传递：压强减小（-ρgh）")
    print("\n⚠️  易错3：忘记水柱高度差")
    print("   → 不仅要考虑水银高差Δh，还要考虑水柱差(h₂ - h₁)")
    print("=" * 75)

    print("\n" + "=" * 75)
    print("【参数调整练习】")
    print("=" * 75)
    print("1. 修改 h1=0.4, h2=0.6，观察压差变化")
    print("2. 修改 dh=0（水银面等高），此时压差只与水柱高差有关")
    print("3. 修改 h1=h2=0.5，dh=0.1，此时压差只与水银高差有关")
    print("\n在代码中修改UTubeManometer的参数，重新运行观察！")
    print("=" * 75)


if __name__ == "__main__":
    main()
