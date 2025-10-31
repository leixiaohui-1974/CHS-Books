"""
水力学考研核心100题 - 第一章题目4
矩形闸门总压力计算与可视化

功能：
1. 计算闸门所受总压力
2. 计算压力中心位置
3. 绘制压力分布图和压力中心示意图

考频：⭐⭐⭐⭐⭐ 必考！
难度：基础

作者：CHS-Books考研系列
更新：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RectangularGate:
    """矩形闸门总压力计算类"""

    def __init__(self, h, b, d, rho=1000, g=9.81):
        """
        初始化闸门参数

        Parameters:
        -----------
        h : float
            闸门高度 (m)
        b : float
            闸门宽度 (m)
        d : float
            闸门顶部距水面距离 (m)
        rho : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.h = h
        self.b = b
        self.d = d
        self.rho = rho
        self.g = g

    def calculate_total_pressure(self):
        """
        计算总压力

        Returns:
        --------
        dict : 包含计算结果的字典
        """
        # 闸门面积
        A = self.b * self.h

        # 形心水深
        hc = self.d + self.h / 2

        # 总压力
        P = self.rho * self.g * hc * A

        # 对形心轴的惯性矩
        Ic = self.b * self.h**3 / 12

        # 压力中心距形心的距离
        e = Ic / (hc * A)

        # 压力中心距水面的深度
        hD = hc + e

        # 压力中心距闸门顶部的距离
        yD = hD - self.d

        return {
            'A': A,
            'hc': hc,
            'P': P,
            'Ic': Ic,
            'e': e,
            'hD': hD,
            'yD': yD
        }

    def print_results(self):
        """打印计算结果"""
        results = self.calculate_total_pressure()

        print("=" * 70)
        print("矩形闸门总压力计算")
        print("=" * 70)

        print("\n【已知条件】")
        print(f"  闸门高度 h = {self.h} m")
        print(f"  闸门宽度 b = {self.b} m")
        print(f"  顶部距水面 d = {self.d} m")
        print(f"  水密度 ρ = {self.rho} kg/m³")
        print(f"  重力加速度 g = {self.g} m/s²")

        print("\n【计算步骤】")
        print(f"\n(1) 闸门面积：")
        print(f"    A = b × h = {self.b} × {self.h} = {results['A']:.2f} m²")

        print(f"\n(2) 形心水深：")
        print(f"    hc = d + h/2 = {self.d} + {self.h}/2 = {results['hc']:.2f} m")

        print(f"\n(3) 总压力：")
        print(f"    P = ρ·g·hc·A")
        print(f"      = {self.rho} × {self.g} × {results['hc']:.2f} × {results['A']:.2f}")
        print(f"      = {results['P']:.2f} N")
        print(f"      = {results['P']/1000:.2f} kN")

        print(f"\n(4) 惯性矩：")
        print(f"    Ic = b·h³/12 = {self.b} × {self.h}³/12 = {results['Ic']:.2f} m⁴")

        print(f"\n(5) 压力中心：")
        print(f"    e = Ic/(hc·A) = {results['Ic']:.2f}/({results['hc']:.2f}×{results['A']:.2f})")
        print(f"      = {results['e']:.3f} m")
        print(f"    hD = hc + e = {results['hc']:.2f} + {results['e']:.3f}")
        print(f"       = {results['hD']:.3f} m（距水面）")
        print(f"    yD = hD - d = {results['hD']:.3f} - {self.d}")
        print(f"       = {results['yD']:.3f} m（距闸门顶部）")

        print("\n【重要结论】")
        print(f"  ✅ 总压力 P = {results['P']/1000:.2f} kN")
        print(f"  ✅ 压力中心在形心下方 {results['e']*100:.1f} cm")
        print(f"  ✅ 压力中心距闸门顶部 {results['yD']:.3f} m")
        print(f"  ⚠️  总压力与闸门倾斜角无关！")

        print("\n" + "=" * 70)

        return results

    def plot_diagram(self, save_fig=True):
        """绘制闸门示意图和压力分布"""
        results = self.calculate_total_pressure()

        fig, axes = plt.subplots(1, 3, figsize=(18, 8))

        # ========== 子图1：闸门几何示意图 ==========
        ax1 = axes[0]

        # 水面
        water_level = 0
        ax1.axhline(y=water_level, color='blue', linestyle='--',
                   linewidth=2, alpha=0.7, label='水面')

        # 水体
        ax1.fill_between([0, 0.5], water_level, -4,
                        alpha=0.2, color='cyan', label='水体')

        # 闸门
        gate_top = -self.d
        gate_bottom = -self.d - self.h
        gate = patches.Rectangle((0.5, gate_bottom), 0.1, self.h,
                                linewidth=3, edgecolor='black',
                                facecolor='gray', alpha=0.7,
                                label='闸门')
        ax1.add_patch(gate)

        # 标注
        # 形心
        yc = gate_top - self.h/2
        ax1.plot(0.55, yc, 'ro', markersize=12, label='形心C', zorder=10)
        ax1.text(0.7, yc, 'C (形心)', fontsize=12, fontweight='bold')

        # 压力中心
        yD = gate_top - results['yD']
        ax1.plot(0.55, yD, 'go', markersize=12, label='压力中心D', zorder=10)
        ax1.text(0.7, yD, 'D (压力中心)', fontsize=12, fontweight='bold', color='green')

        # 尺寸标注
        # h
        ax1.annotate('', xy=(0.35, gate_top), xytext=(0.35, gate_bottom),
                    arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax1.text(0.25, (gate_top + gate_bottom)/2, f'h={self.h}m',
                fontsize=11, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # d
        ax1.annotate('', xy=(0.35, water_level), xytext=(0.35, gate_top),
                    arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax1.text(0.25, (water_level + gate_top)/2, f'd={self.d}m',
                fontsize=11, color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # e
        ax1.annotate('', xy=(0.75, yc), xytext=(0.75, yD),
                    arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
        ax1.text(0.8, (yc + yD)/2, f'e={results["e"]*100:.1f}cm',
                fontsize=10, color='purple', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax1.set_xlim(0, 1.2)
        ax1.set_ylim(-4.5, 0.5)
        ax1.set_xlabel('水平距离 (m)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('竖直坐标 (m)', fontsize=12, fontweight='bold')
        ax1.set_title('闸门几何示意图', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='lower right', fontsize=10)
        ax1.set_aspect('equal')

        # ========== 子图2：压强分布 ==========
        ax2 = axes[1]

        # 沿闸门高度的压强分布
        y_gate = np.linspace(0, self.h, 100)  # 闸门上的坐标
        depth_gate = self.d + y_gate  # 距水面的深度
        p_gate = self.rho * self.g * depth_gate / 1000  # kPa

        # 压强分布（三角形）
        ax2.fill_betweenx(y_gate, 0, p_gate, alpha=0.3, color='blue', label='压强分布')
        ax2.plot(p_gate, y_gate, 'b-', linewidth=3, label='压强线性分布')

        # 标注形心和压力中心
        p_c = self.rho * self.g * results['hc'] / 1000
        ax2.plot(p_c, self.h/2, 'ro', markersize=12, label='形心压强', zorder=10)
        ax2.axhline(y=self.h/2, color='r', linestyle='--', alpha=0.5)

        p_D = self.rho * self.g * results['hD'] / 1000
        ax2.plot(p_D, results['yD'], 'go', markersize=12, label='压力中心', zorder=10)
        ax2.axhline(y=results['yD'], color='g', linestyle='--', alpha=0.5)

        ax2.set_xlabel('压强 (kPa)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('距闸门顶部距离 (m)', fontsize=12, fontweight='bold')
        ax2.set_title('闸门压强分布', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        ax2.invert_yaxis()  # 顶部在上

        # ========== 子图3：总压力矢量图 ==========
        ax3 = axes[2]

        # 闸门
        gate3 = patches.Rectangle((0.5, 0), 0.1, self.h,
                                 linewidth=3, edgecolor='black',
                                 facecolor='lightgray', alpha=0.7)
        ax3.add_patch(gate3)

        # 压力矢量（箭头）
        arrow_scale = 0.003  # 缩放因子
        arrow_length = results['P'] * arrow_scale
        ax3.arrow(0.4, results['yD'], -arrow_length, 0,
                 head_width=0.1, head_length=0.1,
                 fc='red', ec='red', linewidth=3,
                 label=f'总压力 P={results["P"]/1000:.1f}kN')

        # 标注
        ax3.plot(0.55, results['yD'], 'go', markersize=15, zorder=10)
        ax3.text(0.7, results['yD'],
                f'压力中心D\n({results["yD"]:.2f}m)',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

        # 形心对比
        ax3.plot(0.55, self.h/2, 'ro', markersize=12, alpha=0.5, zorder=9)
        ax3.text(0.7, self.h/2,
                f'形心C\n({self.h/2:.2f}m)',
                fontsize=10, color='red',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

        ax3.set_xlim(0, 1.2)
        ax3.set_ylim(-0.2, self.h + 0.2)
        ax3.set_xlabel('水平距离 (m)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('距闸门顶部距离 (m)', fontsize=12, fontweight='bold')
        ax3.set_title('总压力作用点', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper right', fontsize=11)
        ax3.invert_yaxis()
        ax3.set_aspect('equal')

        plt.tight_layout()

        if save_fig:
            plt.savefig('gate_total_pressure.png',
                       dpi=300, bbox_inches='tight', facecolor='white')
            print("\n✅ 图表已保存为 'gate_total_pressure.png'")

        plt.show()


def main():
    """主函数"""

    print("\n")
    print("*" * 70)
    print("水力学考研核心100题 - 第一章题目4")
    print("矩形闸门总压力计算（基础题 ⭐⭐⭐⭐⭐）")
    print("*" * 70)
    print("\n")

    # 创建闸门对象
    gate = RectangularGate(
        h=3.0,      # 闸门高度 (m)
        b=2.0,      # 闸门宽度 (m)
        d=1.0,      # 顶部距水面 (m)
        rho=1000,   # 水密度 (kg/m³)
        g=9.81      # 重力加速度 (m/s²)
    )

    # 计算并打印结果
    results = gate.print_results()

    # 绘制示意图
    print("\n正在生成可视化图表...")
    gate.plot_diagram()

    # 重要提示
    print("\n" + "=" * 70)
    print("【考点总结】")
    print("=" * 70)
    print("1. 总压力公式：P = ρ·g·hc·A （hc为形心水深）")
    print("2. 压力中心公式：yD = yc + Ic/(hc·A)")
    print("3. 压力中心总是在形心下方（∵ Ic > 0）")
    print("4. 总压力与倾斜角无关，只与hc和A有关")
    print("5. 惯性矩 Ic = b·h³/12 （矩形对形心轴）")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("【易错点】")
    print("=" * 70)
    print("⚠️  压力中心 ≠ 形心")
    print("⚠️  总压力与倾斜角无关（但压力中心位置会变）")
    print("⚠️  要用对形心轴的惯性矩Ic，不是对底边")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("【参数调整练习】")
    print("=" * 70)
    print("1. 修改 d=0（闸门顶部在水面），观察总压力")
    print("2. 修改 h=4m，观察压力中心距形心的距离e")
    print("3. 思考：当d很大时（深水），e/h的值趋向多少？")
    print("\n在代码中修改RectangularGate的参数，重新运行！")
    print("=" * 70)


if __name__ == "__main__":
    main()
