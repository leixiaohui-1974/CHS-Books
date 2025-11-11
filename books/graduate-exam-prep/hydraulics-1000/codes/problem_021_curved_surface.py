"""
《水力学1000题详解》- 题目021: 圆柱面曲面总压力
=======================================================

知识点：曲面总压力、压力体法、水平/垂直分力
难度：⭐⭐ 中等题

功能：
1. 计算圆柱面的水平和垂直分力
2. 计算总压力的大小和方向
3. 可视化压力体和压力分布
4. 分析不同曲面形状的影响
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle, Polygon, Wedge
import matplotlib as mpl

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False


class CurvedSurfacePressure:
    """曲面总压力类"""
    
    def __init__(self, radius, width, gamma=9800):
        """
        初始化圆柱面参数
        
        参数:
            radius: 圆弧半径 (m)
            width: 闸门宽度（垂直纸面）(m)
            gamma: 水的容重 (N/m³)
        """
        self.R = radius
        self.b = width
        self.gamma = gamma
        
        # 计算压力
        self._calculate_pressure()
    
    def _calculate_pressure(self):
        """计算水平和垂直分力"""
        
        # 水平分力（投影面积法）
        # 投影面：矩形，宽度b，高度R
        self.A_x = self.b * self.R  # 投影面积
        self.h_c = self.R / 2  # 形心深度
        self.P_x = self.gamma * self.h_c * self.A_x  # 水平分力
        
        # 水平分力作用点（从水面算起）
        self.y_px = 2 * self.R / 3  # 三角形分布，2h/3
        
        # 垂直分力（压力体法）
        # 压力体：半圆柱体（凸面向上，实体）
        self.V = (np.pi * self.R**2 / 2) * self.b  # 半圆柱体积
        self.P_z = self.gamma * self.V  # 垂直分力
        
        # 垂直分力作用点（半圆形心）
        self.x_pz = 4 * self.R / (3 * np.pi)  # 从圆心水平距离
        
        # 总压力
        self.P = np.sqrt(self.P_x**2 + self.P_z**2)
        
        # 方向角（与水平面夹角）
        self.alpha = np.arctan(self.P_z / self.P_x) * 180 / np.pi
    
    def plot_pressure_analysis(self, save_path=None):
        """绘制压力分析图"""
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 1])
        
        ax1 = fig.add_subplot(gs[0, 0])  # 左上：曲面与压力体
        ax2 = fig.add_subplot(gs[0, 1])  # 右上：压力分解
        ax3 = fig.add_subplot(gs[1, :])  # 下方：参数分析
        
        # ===== 左上图：曲面与压力体示意图 =====
        ax1.set_xlim(-1, 4)
        ax1.set_ylim(-0.5, 3)
        ax1.set_aspect('equal')
        
        # 绘制水面
        ax1.plot([-0.5, 3.5], [self.R, self.R], 'b--', linewidth=2, label='水面')
        ax1.fill_between([-0.5, 3.5], self.R, 3, alpha=0.3, color='lightblue')
        
        # 绘制圆弧（半圆，圆心在原点，凸面向上）
        theta = np.linspace(0, np.pi, 100)
        x_arc = self.R * np.cos(theta)
        y_arc = self.R * np.sin(theta) + self.R
        ax1.plot(x_arc, y_arc, 'k-', linewidth=3, label='曲面AB')
        
        # A点和B点
        ax1.plot(-self.R, self.R, 'ro', markersize=12, label='A点')
        ax1.plot(self.R, self.R, 'go', markersize=12, label='B点')
        ax1.text(-self.R - 0.3, self.R, 'A', fontsize=14, fontweight='bold')
        ax1.text(self.R + 0.2, self.R, 'B', fontsize=14, fontweight='bold')
        
        # 圆心O
        ax1.plot(0, self.R, 'ko', markersize=10, label='圆心O')
        ax1.text(0, self.R + 0.3, 'O', fontsize=14, fontweight='bold')
        
        # 压力体（半圆形，填充）
        ax1.fill(x_arc, y_arc, alpha=0.4, color='yellow', label='压力体（实）')
        
        # 投影面（竖直矩形）
        projection_x = [self.R, self.R, self.R + 0.3, self.R + 0.3]
        projection_y = [self.R, 0, 0, self.R]
        ax1.fill(projection_x, projection_y, alpha=0.5, color='lightgreen', 
                edgecolor='green', linewidth=2, label='投影面')
        
        # 标注尺寸
        ax1.plot([0, self.R], [self.R, self.R], 'r--', linewidth=1.5)
        ax1.text(self.R/2, self.R - 0.2, f'R={self.R}m', 
                ha='center', fontsize=11, fontweight='bold', color='red')
        
        # 标注形心（压力体）
        x_c = self.x_pz
        y_c = self.R + 4*self.R/(3*np.pi)
        ax1.plot(x_c, y_c, 'r*', markersize=15, label='压力体形心')
        
        ax1.set_xlabel('水平位置 (m)', fontsize=11)
        ax1.set_ylabel('高度 (m)', fontsize=11)
        ax1.set_title('圆柱面曲面与压力体', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # ===== 右上图：压力分解与合成 =====
        ax2.set_xlim(-50, 250)
        ax2.set_ylim(-50, 250)
        ax2.set_aspect('equal')
        
        # 原点（曲面中心）
        ax2.plot(0, 0, 'ko', markersize=10)
        
        # 水平分力箭头
        scale = 0.5  # 缩放比例
        P_x_scaled = self.P_x / 1000 * scale
        P_z_scaled = self.P_z / 1000 * scale
        
        ax2.arrow(0, 0, P_x_scaled, 0, 
                 head_width=8, head_length=10, fc='blue', ec='blue', 
                 linewidth=3, label=f'P_x={self.P_x/1000:.1f} kN')
        ax2.text(P_x_scaled/2, -15, f'P_x={self.P_x/1000:.1f} kN', 
                ha='center', fontsize=11, fontweight='bold', color='blue')
        
        # 垂直分力箭头
        ax2.arrow(0, 0, 0, P_z_scaled, 
                 head_width=8, head_length=10, fc='red', ec='red', 
                 linewidth=3, label=f'P_z={self.P_z/1000:.1f} kN')
        ax2.text(-15, P_z_scaled/2, f'P_z={self.P_z/1000:.1f} kN', 
                rotation=90, va='center', fontsize=11, fontweight='bold', color='red')
        
        # 总压力箭头（矢量和）
        P_scaled = self.P / 1000 * scale
        ax2.arrow(0, 0, P_x_scaled, P_z_scaled, 
                 head_width=10, head_length=12, fc='green', ec='green', 
                 linewidth=4, alpha=0.7, label=f'P={self.P/1000:.1f} kN')
        
        # 角度标注
        angle_arc = Arc((0, 0), 40, 40, angle=0, theta1=0, theta2=self.alpha, 
                       color='purple', linewidth=2)
        ax2.add_patch(angle_arc)
        ax2.text(25, 15, f'α={self.alpha:.1f}°', 
                fontsize=12, fontweight='bold', color='purple')
        
        # 虚线（平行四边形）
        ax2.plot([P_x_scaled, P_x_scaled], [0, P_z_scaled], 'k--', alpha=0.4)
        ax2.plot([0, P_x_scaled], [P_z_scaled, P_z_scaled], 'k--', alpha=0.4)
        
        ax2.set_xlabel('水平方向 (kN)', fontsize=11)
        ax2.set_ylabel('垂直方向 (kN)', fontsize=11)
        ax2.set_title('曲面总压力的分解与合成', fontsize=13, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # ===== 下方图：参数影响分析 =====
        radii = np.linspace(0.5, 5, 30)
        P_x_list = []
        P_z_list = []
        P_list = []
        alpha_list = []
        
        for r in radii:
            temp_surf = CurvedSurfacePressure(r, self.b, self.gamma)
            P_x_list.append(temp_surf.P_x / 1000)
            P_z_list.append(temp_surf.P_z / 1000)
            P_list.append(temp_surf.P / 1000)
            alpha_list.append(temp_surf.alpha)
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(radii, P_x_list, 'b-', linewidth=2.5, 
                        label='水平分力 P_x', marker='o', markersize=4)
        line2 = ax3.plot(radii, P_z_list, 'r-', linewidth=2.5, 
                        label='垂直分力 P_z', marker='s', markersize=4)
        line3 = ax3.plot(radii, P_list, 'g-', linewidth=2.5, 
                        label='总压力 P', marker='^', markersize=4)
        line4 = ax3_twin.plot(radii, alpha_list, 'm--', linewidth=2.5, 
                             label='方向角 α', marker='d', markersize=4)
        
        # 当前半径标记
        ax3.axvline(x=self.R, color='gray', linestyle=':', linewidth=2, alpha=0.7)
        ax3.plot(self.R, self.P_x/1000, 'bo', markersize=12, 
                markeredgewidth=3, markerfacecolor='none')
        ax3.plot(self.R, self.P_z/1000, 'rs', markersize=12, 
                markeredgewidth=3, markerfacecolor='none')
        ax3.plot(self.R, self.P/1000, 'g^', markersize=12, 
                markeredgewidth=3, markerfacecolor='none')
        
        ax3.set_xlabel('圆弧半径 R (m)', fontsize=12)
        ax3.set_ylabel('压力 (kN)', fontsize=12)
        ax3_twin.set_ylabel('方向角 α (度)', fontsize=12, color='m')
        ax3.set_title('曲面半径对压力的影响分析', fontsize=14, fontweight='bold')
        
        ax3.tick_params(axis='y', labelcolor='k')
        ax3_twin.tick_params(axis='y', labelcolor='m')
        
        # 组合图例
        lines = line1 + line2 + line3 + line4
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper left', fontsize=10)
        
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        
        plt.show()
    
    def print_results(self):
        """打印详细计算结果"""
        print("=" * 70)
        print("题目021: 圆柱面曲面总压力 - 计算结果")
        print("=" * 70)
        
        print(f"\n【曲面参数】")
        print(f"  圆弧半径: R = {self.R} m")
        print(f"  闸门宽度: b = {self.b} m（垂直纸面）")
        print(f"  水的容重: γ = {self.gamma} N/m³")
        print(f"  曲面形式: 半圆柱形，凸面向上")
        
        print(f"\n【水平分力计算】")
        print(f"  原理: 曲面水平分力 = 投影面上的压力")
        print(f"  投影面: 矩形，宽度b={self.b}m，高度R={self.R}m")
        print(f"  投影面积: A_x = b × R = {self.b} × {self.R} = {self.A_x} m²")
        print(f"  形心深度: h_c = R/2 = {self.h_c} m")
        print(f"  水平分力: P_x = γ × h_c × A_x")
        print(f"           = {self.gamma} × {self.h_c} × {self.A_x}")
        print(f"           = {self.P_x:.0f} N = {self.P_x/1000:.1f} kN")
        print(f"  作用点高度: y_px = 2R/3 = {self.y_px:.3f} m（从水面算起）")
        
        print(f"\n【垂直分力计算】")
        print(f"  原理: 曲面垂直分力 = 压力体重量")
        print(f"  压力体: 半圆柱体（凸面向上，实体）")
        print(f"  体积: V = (πR²/2) × b")
        print(f"       = (π × {self.R}²/2) × {self.b}")
        print(f"       = {self.V:.3f} m³")
        print(f"  垂直分力: P_z = γ × V")
        print(f"           = {self.gamma} × {self.V:.3f}")
        print(f"           = {self.P_z:.0f} N = {self.P_z/1000:.1f} kN")
        print(f"  方向: 竖直向下")
        print(f"  作用点: 距圆心水平距离 x_pz = 4R/(3π) = {self.x_pz:.3f} m")
        
        print(f"\n【总压力计算】")
        print(f"  大小: P = √(P_x² + P_z²)")
        print(f"       = √({self.P_x/1000:.1f}² + {self.P_z/1000:.1f}²)")
        print(f"       = {self.P/1000:.1f} kN")
        print(f"  方向角: α = arctan(P_z/P_x)")
        print(f"         = arctan({self.P_z/1000:.1f}/{self.P_x/1000:.1f})")
        print(f"         = {self.alpha:.1f}°（与水平面夹角）")
        print(f"  方向: 向右下方")
        
        print(f"\n【工程意义】")
        print(f"  等效吨力: {self.P/9800:.1f} 吨")
        print(f"  P_z/P_x比值: {self.P_z/self.P_x:.2f}")
        print(f"  说明: 垂直分力 {'>' if self.P_z > self.P_x else '<'} 水平分力")
        
        print("\n" + "=" * 70)


def main():
    """主程序"""
    
    print("\n" + "="*70)
    print("《水力学1000题详解》- 题目021")
    print("圆柱面曲面总压力计算")
    print("="*70 + "\n")
    
    # 创建曲面实例
    surf = CurvedSurfacePressure(radius=2.0, width=3.0, gamma=9800)
    
    # 打印计算结果
    surf.print_results()
    
    # 绘制分析图
    print("\n正在生成曲面压力分析图...")
    surf.plot_pressure_analysis()
    
    print("\n✅ 题目021 计算完成！\n")


def test_curved_surface():
    """单元测试"""
    print("\n【单元测试】曲面总压力计算验证")
    print("-" * 50)
    
    surf = CurvedSurfacePressure(2.0, 3.0, 9800)
    
    # 测试1：投影面积
    expected_A_x = 2.0 * 3.0
    assert abs(surf.A_x - expected_A_x) < 0.01, "投影面积计算错误"
    print(f"✓ 测试1通过: 投影面积 = {surf.A_x} m²")
    
    # 测试2：形心深度
    expected_h_c = 1.0
    assert abs(surf.h_c - expected_h_c) < 0.01, "形心深度计算错误"
    print(f"✓ 测试2通过: 形心深度 = {surf.h_c} m")
    
    # 测试3：水平分力
    expected_P_x = 9800 * 1.0 * 6.0
    assert abs(surf.P_x - expected_P_x) < 1, "水平分力计算错误"
    print(f"✓ 测试3通过: 水平分力 = {surf.P_x/1000:.1f} kN")
    
    # 测试4：压力体体积
    expected_V = (np.pi * 2.0**2 / 2) * 3.0
    assert abs(surf.V - expected_V) < 0.01, "压力体体积计算错误"
    print(f"✓ 测试4通过: 压力体体积 = {surf.V:.3f} m³")
    
    # 测试5：垂直分力
    expected_P_z = 9800 * expected_V
    assert abs(surf.P_z - expected_P_z) < 1, "垂直分力计算错误"
    print(f"✓ 测试5通过: 垂直分力 = {surf.P_z/1000:.1f} kN")
    
    # 测试6：总压力
    expected_P = np.sqrt(surf.P_x**2 + surf.P_z**2)
    assert abs(surf.P - expected_P) < 1, "总压力计算错误"
    print(f"✓ 测试6通过: 总压力 = {surf.P/1000:.1f} kN")
    
    # 测试7：P_z > P_x（对于半圆）
    assert surf.P_z > surf.P_x, "半圆柱面应该垂直分力大于水平分力"
    print(f"✓ 测试7通过: P_z > P_x（半圆特性）")
    
    print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    # 运行单元测试
    test_curved_surface()
    
    # 运行主程序
    main()
