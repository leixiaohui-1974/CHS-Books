"""
水力学考研核心100题 - 第一章题目6
浮体平衡计算与可视化

功能：
1. 计算木块浸入水中的深度
2. 计算浮力
3. 分析放置重物后的新平衡状态
4. 绘制浮力平衡示意图

考频：⭐⭐⭐⭐⭐ 高频！
难度：基础

作者：CHS-Books考研系列
更新：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FloatingBody:
    """浮体平衡计算类"""

    def __init__(self, L, B, H, rho_body, rho_fluid=1000, g=9.81):
        """
        初始化浮体参数

        Parameters:
        -----------
        L : float
            长度 (m)
        B : float
            宽度 (m)
        H : float
            高度 (m)
        rho_body : float
            浮体密度 (kg/m³)
        rho_fluid : float
            液体密度 (kg/m³), 默认1000(水)
        g : float
            重力加速度 (m/s²)
        """
        self.L = L
        self.B = B
        self.H = H
        self.rho_body = rho_body
        self.rho_fluid = rho_fluid
        self.g = g

    def calculate_draft(self, added_mass=0):
        """
        计算浸深（吃水）

        Parameters:
        -----------
        added_mass : float
            附加质量 (kg), 如重物

        Returns:
        --------
        dict : 计算结果
        """
        # 浮体体积
        V_body = self.L * self.B * self.H

        # 浮体质量
        M_body = self.rho_body * V_body

        # 浮体重量
        G_body = M_body * self.g

        # 总重量
        G_total = G_body + added_mass * self.g

        # 底面积
        A_bottom = self.L * self.B

        # 漂浮平衡：G = F_buoy = rho_fluid * g * V_displaced
        # V_displaced = G / (rho_fluid * g)
        V_displaced = G_total / (self.rho_fluid * self.g)

        # 浸深 draft = V_displaced / A_bottom
        draft = V_displaced / A_bottom

        # 浮力
        F_buoy = self.rho_fluid * self.g * V_displaced

        # 检查是否仍然漂浮
        is_floating = draft < self.H

        return {
            'V_body': V_body,
            'M_body': M_body,
            'G_body': G_body,
            'G_total': G_total,
            'V_displaced': V_displaced,
            'draft': draft,
            'F_buoy': F_buoy,
            'is_floating': is_floating,
            'added_mass': added_mass
        }

    def print_results(self, added_mass=0):
        """打印计算结果"""
        results = self.calculate_draft(added_mass)

        print("=" * 75)
        print("浮体平衡计算")
        print("=" * 75)

        print("\n【已知条件】")
        print(f"  浮体尺寸：L×B×H = {self.L}m × {self.B}m × {self.H}m")
        print(f"  浮体密度：ρ_body = {self.rho_body} kg/m³")
        print(f"  液体密度：ρ_fluid = {self.rho_fluid} kg/m³")
        if added_mass > 0:
            print(f"  附加质量：m = {added_mass} kg")

        print("\n【计算步骤】")

        print(f"\n(1) 浮体体积和质量：")
        print(f"    V = L × B × H = {self.L} × {self.B} × {self.H}")
        print(f"      = {results['V_body']:.3f} m³")
        print(f"    M = ρ_body × V = {self.rho_body} × {results['V_body']:.3f}")
        print(f"      = {results['M_body']:.2f} kg")

        print(f"\n(2) 重力：")
        print(f"    G_body = M × g = {results['M_body']:.2f} × {self.g}")
        print(f"           = {results['G_body']:.2f} N")
        if added_mass > 0:
            print(f"    G_added = m × g = {added_mass} × {self.g}")
            print(f"            = {added_mass * self.g:.2f} N")
            print(f"    G_total = {results['G_body']:.2f} + {added_mass * self.g:.2f}")
            print(f"            = {results['G_total']:.2f} N")

        print(f"\n(3) 漂浮平衡（G = F_buoy）：")
        print(f"    F_buoy = G = {results['G_total']:.2f} N")
        print(f"    F_buoy = ρ_fluid × g × V_displaced")
        print(f"    V_displaced = F_buoy / (ρ_fluid × g)")
        print(f"                = {results['G_total']:.2f} / ({self.rho_fluid} × {self.g})")
        print(f"                = {results['V_displaced']:.4f} m³")

        print(f"\n(4) 浸深（吃水）：")
        print(f"    A_bottom = L × B = {self.L} × {self.B} = {self.L * self.B} m²")
        print(f"    draft = V_displaced / A_bottom")
        print(f"          = {results['V_displaced']:.4f} / {self.L * self.B}")
        print(f"          = {results['draft']:.4f} m = {results['draft']*100:.2f} cm")

        print(f"\n(5) 状态判断：")
        if results['is_floating']:
            print(f"    draft = {results['draft']:.4f} m < H = {self.H} m")
            print(f"    ✅ 仍然漂浮")
        else:
            print(f"    draft = {results['draft']:.4f} m >= H = {self.H} m")
            print(f"    ⚠️  完全浸没或沉底")

        print("\n【最终答案】")
        print(f"  • 浸深：h = {results['draft']:.4f} m = {results['draft']*100:.2f} cm")
        print(f"  • 浮力：F = {results['F_buoy']:.2f} N = {results['F_buoy']/1000:.3f} kN")
        print(f"  • 状态：{'漂浮' if results['is_floating'] else '沉没'}")

        print("\n" + "=" * 75)

        return results

    def plot_diagram(self, added_mass=0, save_fig=True):
        """绘制浮力平衡示意图"""
        results = self.calculate_draft(added_mass)

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # ========== 子图1：初始状态 ==========
        ax1 = axes[0]
        results_init = self.calculate_draft(0)
        draft_init = results_init['draft']

        # 水面
        ax1.axhline(y=0, color='blue', linestyle='--', linewidth=2, label='水面')

        # 水体
        ax1.fill_between([-0.2, self.L+0.2], -2, 0, alpha=0.2, color='cyan', label='水')

        # 浮体（木块）
        body1 = patches.Rectangle((0, -draft_init), self.L, self.H,
                                 linewidth=3, edgecolor='brown',
                                 facecolor='burlywood', alpha=0.8,
                                 label='浮体（木块）')
        ax1.add_patch(body1)

        # 水线（浸没部分）
        water_line1 = patches.Rectangle((0, -draft_init), self.L, draft_init,
                                       linewidth=0, facecolor='lightblue',
                                       alpha=0.5, label='浸没部分')
        ax1.add_patch(water_line1)

        # 力矢量
        # 重力
        G_center = self.L / 2
        ax1.arrow(G_center, self.H - draft_init + 0.3, 0, -0.25,
                 head_width=0.05, head_length=0.05, fc='red', ec='red', linewidth=3)
        ax1.text(G_center + 0.15, self.H - draft_init + 0.2,
                f'G={results_init["G_body"]/1000:.2f}kN',
                fontsize=11, color='red', fontweight='bold')

        # 浮力
        ax1.arrow(G_center, -draft_init/2 - 0.3, 0, 0.25,
                 head_width=0.05, head_length=0.05, fc='blue', ec='blue', linewidth=3)
        ax1.text(G_center + 0.15, -draft_init/2 - 0.2,
                f'F={results_init["F_buoy"]/1000:.2f}kN',
                fontsize=11, color='blue', fontweight='bold')

        # 标注浸深
        ax1.annotate('', xy=(-0.1, 0), xytext=(-0.1, -draft_init),
                    arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
        ax1.text(-0.25, -draft_init/2, f'h={draft_init*100:.1f}cm',
                fontsize=11, color='purple', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax1.set_xlim(-0.4, self.L + 0.4)
        ax1.set_ylim(-2, self.H + 0.5)
        ax1.set_xlabel('水平距离 (m)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('竖直坐标 (m)', fontsize=12, fontweight='bold')
        ax1.set_title('初始状态（无附加质量）', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right', fontsize=10)
        ax1.set_aspect('equal')

        # ========== 子图2：放置重物后 ==========
        if added_mass > 0:
            ax2 = axes[1]
            draft_new = results['draft']

            # 水面
            ax2.axhline(y=0, color='blue', linestyle='--', linewidth=2, label='水面')

            # 水体
            ax2.fill_between([-0.2, self.L+0.2], -2, 0, alpha=0.2, color='cyan')

            # 浮体
            body2 = patches.Rectangle((0, -draft_new), self.L, self.H,
                                     linewidth=3, edgecolor='brown',
                                     facecolor='burlywood', alpha=0.8)
            ax2.add_patch(body2)

            # 浸没部分
            water_line2 = patches.Rectangle((0, -draft_new), self.L, draft_new,
                                           linewidth=0, facecolor='lightblue',
                                           alpha=0.5)
            ax2.add_patch(water_line2)

            # 重物
            weight_height = 0.15
            weight = patches.Rectangle((self.L/2 - 0.1, self.H - draft_new),
                                      0.2, weight_height,
                                      linewidth=2, edgecolor='black',
                                      facecolor='darkgray', label=f'重物({added_mass}kg)')
            ax2.add_patch(weight)

            # 力矢量
            # 总重力
            ax2.arrow(G_center, self.H - draft_new + weight_height + 0.3, 0, -0.25,
                     head_width=0.05, head_length=0.05, fc='red', ec='red', linewidth=3)
            ax2.text(G_center + 0.15, self.H - draft_new + weight_height + 0.2,
                    f'G={results["G_total"]/1000:.2f}kN',
                    fontsize=11, color='red', fontweight='bold')

            # 浮力
            ax2.arrow(G_center, -draft_new/2 - 0.3, 0, 0.25,
                     head_width=0.05, head_length=0.05, fc='blue', ec='blue', linewidth=3)
            ax2.text(G_center + 0.15, -draft_new/2 - 0.2,
                    f'F={results["F_buoy"]/1000:.2f}kN',
                    fontsize=11, color='blue', fontweight='bold')

            # 标注新浸深
            ax2.annotate('', xy=(-0.1, 0), xytext=(-0.1, -draft_new),
                        arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
            ax2.text(-0.3, -draft_new/2, f'h′={draft_new*100:.1f}cm',
                    fontsize=11, color='purple', fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            ax2.set_xlim(-0.4, self.L + 0.4)
            ax2.set_ylim(-2, self.H + weight_height + 0.5)
            ax2.set_xlabel('水平距离 (m)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('竖直坐标 (m)', fontsize=12, fontweight='bold')
            ax2.set_title(f'放置{added_mass}kg重物后', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='upper right', fontsize=10)
            ax2.set_aspect('equal')

        # ========== 子图3：浸深对比 ==========
        ax3 = axes[2]

        states = ['初始', f'+{added_mass}kg']
        drafts = [draft_init * 100, results['draft'] * 100]  # cm
        colors = ['lightblue', 'blue']

        bars = ax3.bar(states, drafts, color=colors, alpha=0.7,
                      edgecolor='black', linewidth=2)

        # 标注数值
        for bar, draft in zip(bars, drafts):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{draft:.2f} cm',
                    ha='center', va='bottom', fontsize=13, fontweight='bold')

        # 最大高度线
        ax3.axhline(y=self.H*100, color='red', linestyle='--', linewidth=2,
                   label=f'浮体高度H={self.H*100}cm')

        ax3.set_ylabel('浸深 (cm)', fontsize=12, fontweight='bold')
        ax3.set_title('浸深对比', fontsize=14, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        ax3.legend(fontsize=11)

        plt.tight_layout()

        if save_fig:
            plt.savefig('buoyancy_calculation.png',
                       dpi=300, bbox_inches='tight', facecolor='white')
            print("\n✅ 图表已保存为 'buoyancy_calculation.png'")

        plt.show()


def main():
    """主函数"""

    print("\n")
    print("*" * 75)
    print("水力学考研核心100题 - 第一章题目6")
    print("浮体平衡计算（基础题 ⭐⭐⭐⭐⭐）")
    print("*" * 75)
    print("\n")

    # 创建浮体对象（木块）
    wood = FloatingBody(
        L=1.0,          # 长度 (m)
        B=0.5,          # 宽度 (m)
        H=0.4,          # 高度 (m)
        rho_body=600,   # 木块密度 (kg/m³)
        rho_fluid=1000, # 水密度 (kg/m³)
        g=9.81          # 重力加速度 (m/s²)
    )

    # (1) 初始状态
    print("【情况1：初始状态】")
    results1 = wood.print_results(added_mass=0)

    # (2) 放置重物后
    print("\n\n【情况2：放置50kg重物后】")
    results2 = wood.print_results(added_mass=50)

    # 绘制对比图
    print("\n正在生成可视化对比图...")
    wood.plot_diagram(added_mass=50)

    # 知识点总结
    print("\n" + "=" * 75)
    print("【考点总结】")
    print("=" * 75)
    print("1. 漂浮平衡条件：G = F_buoy")
    print("2. 浮力公式：F_buoy = ρ_fluid × g × V_displaced")
    print("3. 浸深计算：draft = V_displaced / A_bottom")
    print("4. 漂浮判据：draft < H（否则为悬浮或沉底）")
    print("5. 密度关系：")
    print("   - ρ_body < ρ_fluid → 漂浮")
    print("   - ρ_body = ρ_fluid → 悬浮")
    print("   - ρ_body > ρ_fluid → 沉底")
    print("=" * 75)

    print("\n" + "=" * 75)
    print("【易错点】")
    print("=" * 75)
    print("⚠️  浮力 = 排开液体的重量（不是物体体积！）")
    print("⚠️  必须验证 draft < H（漂浮条件）")
    print("⚠️  单位统一：密度kg/m³，体积m³")
    print("=" * 75)

    print("\n" + "=" * 75)
    print("【参数调整练习】")
    print("=" * 75)
    print("1. 修改 rho_body=800，观察浸深变化")
    print("2. 修改 added_mass=100kg，检查是否仍漂浮")
    print("3. 思考：最多能放多重的物体而不沉没？")
    print("\n计算：当draft = H时，m_max = ?")
    print(f"    m_max = ρ_fluid × A × H - M_body")
    print(f"          = {wood.rho_fluid} × {wood.L * wood.B} × {wood.H} - {results1['M_body']:.2f}")
    print(f"          = {wood.rho_fluid * wood.L * wood.B * wood.H - results1['M_body']:.2f} kg")
    print("=" * 75)


if __name__ == "__main__":
    main()
