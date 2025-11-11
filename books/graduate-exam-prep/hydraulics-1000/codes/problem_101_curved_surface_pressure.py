"""
《水力学考研1000题详解》配套代码
题目101：曲面总压力计算

问题描述：
一圆柱形闸门，半径R=2m，宽度b=3m（垂直纸面），左侧水深h=3m。
求：(1) 作用在曲面AB上的水平分力Px
    (2) 作用在曲面AB上的垂直分力Pz
    (3) 总压力P的大小和方向
    (4) 压力作用点位置
    (5) 绘制压力体示意图

考点：
1. 曲面总压力的水平分力：Px = γhcAx（相当于垂直投影面上的平面总压力）
2. 曲面总压力的垂直分力：Pz = γV（压力体体积乘以重度）
3. 压力体：实际液体体积（向上）或虚拟液体体积（向下）
4. 总压力：P = √(Px² + Pz²)
5. 作用方向：tanθ = Pz/Px
6. 压力作用点：通过曲面曲率中心

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc, Polygon, FancyArrowPatch, Wedge

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CurvedSurfacePressure:
    """曲面总压力计算类"""
    
    def __init__(self, R, b, h, gamma=9800):
        """
        初始化
        
        参数:
            R: 圆柱半径 (m)
            b: 宽度（垂直纸面）(m)
            h: 水深 (m)
            gamma: 水的重度 (N/m³)
        """
        self.R = R          # 半径 (m)
        self.b = b          # 宽度 (m)
        self.h = h          # 水深 (m)
        self.gamma = gamma  # 重度 (N/m³)
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算曲面总压力"""
        # 1. 水平分力Px（相当于垂直投影面上的平面总压力）
        # 垂直投影面：矩形，高度为R（假设曲面从水面到底部）
        # 如果h > R，投影高度为R；如果h < R，投影高度为h
        if self.h >= self.R:
            # 完全淹没
            h_proj = self.R
            # 投影面积
            self.Ax = h_proj * self.b
            # 形心水深（投影面中心）
            self.hc = self.h - self.R / 2
        else:
            # 部分淹没
            h_proj = self.h
            self.Ax = h_proj * self.b
            self.hc = self.h / 2
        
        # 水平分力
        self.Px = self.gamma * self.hc * self.Ax
        
        # 水平分力作用点（压力中心）
        # yD = yc + Ic/(yc*A)
        # 对于矩形，Ic = b*h³/12
        Ic = self.b * h_proj**3 / 12
        self.yD_from_surface = self.hc + Ic / (self.hc * self.Ax)
        
        # 2. 垂直分力Pz（压力体重量）
        # 压力体：曲面上方到自由液面的实际液体体积
        # 对于圆柱曲面（假设是1/4圆弧）
        # 压力体 = 矩形体积 - 扇形体积
        
        # 假设曲面是圆心在水面处，向下的1/4圆弧
        # 压力体体积（单位宽度）
        V_rectangle = self.R * self.R  # 矩形OABO'
        V_sector = np.pi * self.R**2 / 4  # 扇形面积
        V_pressure_body_per_width = V_rectangle - V_sector
        
        # 总压力体体积
        self.V_pressure_body = V_pressure_body_per_width * self.b
        
        # 垂直分力
        self.Pz = self.gamma * self.V_pressure_body
        
        # 3. 总压力
        self.P = np.sqrt(self.Px**2 + self.Pz**2)
        
        # 4. 作用方向（与水平方向夹角）
        self.theta = np.arctan(self.Pz / self.Px)
        self.theta_deg = np.degrees(self.theta)
        
        # 5. 压力作用点
        # 对于圆柱曲面，总压力通过曲率中心（圆心）
        self.pressure_center = "通过曲率中心（圆心）"
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目101：曲面总压力计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"圆柱半径: R = {self.R} m")
        print(f"闸门宽度: b = {self.b} m（垂直纸面）")
        print(f"水深: h = {self.h} m")
        print(f"水的重度: γ = {self.gamma} N/m³")
        
        print("\n【曲面总压力基本概念】")
        print("1. 水平分力Px:")
        print("   • 等于作用在曲面垂直投影面上的平面总压力")
        print("   • Px = γ·hc·Ax")
        print("   • hc: 投影面形心水深")
        print("   • Ax: 垂直投影面面积")
        
        print("\n2. 垂直分力Pz:")
        print("   • 等于压力体的重量")
        print("   • Pz = γ·V")
        print("   • V: 压力体体积")
        
        print("\n3. 压力体:")
        print("   • 曲面、垂直投影面、自由液面（或其延长面）围成的体积")
        print("   • 实际液体体积：Pz向下")
        print("   • 虚拟液体体积：Pz向上")
        
        print("\n4. 总压力:")
        print("   • P = √(Px² + Pz²)")
        print("   • tanθ = Pz/Px")
        print("   • 通过曲率中心")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算水平分力Px")
        print("确定垂直投影面:")
        if self.h >= self.R:
            h_proj = self.R
            print(f"  水深h={self.h}m ≥ R={self.R}m，曲面完全淹没")
            print(f"  投影面高度: h_proj = R = {h_proj} m")
        else:
            h_proj = self.h
            print(f"  水深h={self.h}m < R={self.R}m，曲面部分淹没")
            print(f"  投影面高度: h_proj = h = {h_proj} m")
        
        print(f"\n投影面面积:")
        print(f"  Ax = h_proj × b = {h_proj} × {self.b} = {self.Ax} m²")
        
        print(f"\n投影面形心水深:")
        print(f"  hc = h - R/2 = {self.h} - {self.R}/2 = {self.hc} m")
        
        print(f"\n水平分力:")
        print(f"  Px = γ·hc·Ax")
        print(f"     = {self.gamma} × {self.hc} × {self.Ax}")
        print(f"     = {self.Px:.2f} N")
        print(f"     = {self.Px/1000:.2f} kN")
        
        print(f"\n水平分力作用点（压力中心）:")
        print(f"  yD = hc + Ic/(hc·Ax)")
        Ic = self.b * h_proj**3 / 12
        print(f"  Ic = b·h³/12 = {self.b} × {h_proj}³/12 = {Ic:.4f} m⁴")
        print(f"  yD = {self.hc} + {Ic:.4f}/({self.hc} × {self.Ax})")
        print(f"     = {self.yD_from_surface:.4f} m（从自由液面算起）")
        
        print("\n步骤2：计算垂直分力Pz")
        print("确定压力体:")
        print(f"  假设曲面为圆心在水面处的1/4圆弧（向下凸）")
        print(f"  压力体 = 矩形OABO' - 扇形OAB")
        
        V_rectangle = self.R * self.R
        V_sector = np.pi * self.R**2 / 4
        V_per_width = V_rectangle - V_sector
        
        print(f"\n单位宽度压力体面积:")
        print(f"  矩形面积: A_rect = R × R = {self.R} × {self.R} = {V_rectangle} m²")
        print(f"  扇形面积: A_sector = πR²/4 = π × {self.R}²/4 = {V_sector:.4f} m²")
        print(f"  压力体面积: A_pb = A_rect - A_sector = {V_rectangle} - {V_sector:.4f}")
        print(f"             = {V_per_width:.4f} m²")
        
        print(f"\n总压力体体积:")
        print(f"  V = A_pb × b = {V_per_width:.4f} × {self.b} = {self.V_pressure_body:.4f} m³")
        
        print(f"\n垂直分力:")
        print(f"  Pz = γ·V")
        print(f"     = {self.gamma} × {self.V_pressure_body:.4f}")
        print(f"     = {self.Pz:.2f} N")
        print(f"     = {self.Pz/1000:.2f} kN")
        
        print("\n步骤3：计算总压力")
        print(f"总压力大小:")
        print(f"  P = √(Px² + Pz²)")
        print(f"    = √({self.Px:.2f}² + {self.Pz:.2f}²)")
        print(f"    = √({self.Px**2:.2f} + {self.Pz**2:.2f})")
        print(f"    = {self.P:.2f} N")
        print(f"    = {self.P/1000:.2f} kN")
        
        print(f"\n作用方向:")
        print(f"  tanθ = Pz/Px = {self.Pz:.2f}/{self.Px:.2f} = {self.Pz/self.Px:.4f}")
        print(f"  θ = arctan({self.Pz/self.Px:.4f})")
        print(f"    = {self.theta:.4f} rad")
        print(f"    = {self.theta_deg:.2f}°")
        print(f"  说明: 总压力与水平方向成{self.theta_deg:.2f}°角")
        
        print("\n步骤4：确定压力作用点")
        print(f"  对于圆柱曲面，总压力通过曲率中心（圆心）")
        print(f"  作用线：从圆心出发，与水平方向成θ={self.theta_deg:.2f}°")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 水平分力: Px = {self.Px/1000:.2f} kN")
        print(f"    作用点: 距液面{self.yD_from_surface:.3f}m")
        print(f"(2) 垂直分力: Pz = {self.Pz/1000:.2f} kN")
        print(f"    方向: 向下")
        print(f"(3) 总压力: P = {self.P/1000:.2f} kN")
        print(f"    方向: 与水平方向成{self.theta_deg:.2f}°角")
        print(f"(4) 作用点: {self.pressure_center}")
        print("="*80)
        
        print("\n【核心公式】")
        print("水平分力: Px = γ·hc·Ax")
        print("垂直分力: Pz = γ·V（压力体重量）")
        print("总压力: P = √(Px² + Pz²)")
        print("方向: tanθ = Pz/Px")
        print("作用点: 通过曲率中心")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：曲面示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_curved_surface(ax1)
        
        # 子图2：压力体示意图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_pressure_body(ax2)
        
        # 子图3：力的分解
        ax3 = plt.subplot(2, 2, 3)
        self._plot_force_decomposition(ax3)
        
        # 子图4：力的合成
        ax4 = plt.subplot(2, 2, 4)
        self._plot_force_composition(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_curved_surface(self, ax):
        """绘制曲面示意图"""
        # 水面
        ax.plot([-1, self.R+1], [0, 0], 'b-', linewidth=2, label='自由液面')
        
        # 水体
        theta_start = -90
        theta_end = 0
        theta_array = np.linspace(np.radians(theta_start), np.radians(theta_end), 100)
        x_curve = self.R * np.cos(theta_array)
        y_curve = self.R * np.sin(theta_array)
        
        # 填充水体
        x_water = np.concatenate([[0], x_curve, [self.R, 0]])
        y_water = np.concatenate([[0], y_curve, [-self.R, 0]])
        ax.fill(x_water, y_water, color='lightblue', alpha=0.5, label='水体')
        
        # 曲面AB
        ax.plot(x_curve, y_curve, 'r-', linewidth=3, label='曲面AB')
        
        # 圆心O
        ax.plot(0, 0, 'ko', markersize=8)
        ax.text(-0.2, 0.2, 'O（圆心）', fontsize=10)
        
        # 点A和B
        ax.plot(0, -self.R, 'ro', markersize=8)
        ax.text(-0.3, -self.R, 'A', fontsize=11, weight='bold')
        
        ax.plot(self.R, 0, 'ro', markersize=8)
        ax.text(self.R+0.2, 0, 'B', fontsize=11, weight='bold')
        
        # 半径R
        ax.plot([0, self.R], [0, 0], 'k--', linewidth=1, alpha=0.5)
        ax.text(self.R/2, 0.15, f'R={self.R}m', fontsize=10)
        
        ax.plot([0, 0], [0, -self.R], 'k--', linewidth=1, alpha=0.5)
        ax.text(-0.4, -self.R/2, f'R={self.R}m', fontsize=10, rotation=90, va='center')
        
        # 水深
        ax.annotate('', xy=(-0.5, 0), xytext=(-0.5, -self.h),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax.text(-0.8, -self.h/2, f'h={self.h}m', fontsize=10, color='blue',
               rotation=90, va='center')
        
        # 宽度（用箭头表示垂直纸面）
        ax.text(self.R*0.5, -self.R*1.3, f'⊗ b={self.b}m（垂直纸面向里）',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlim(-1.5, self.R+1)
        ax.set_ylim(-self.R-1, 1)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('圆柱形曲面示意图', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_pressure_body(self, ax):
        """绘制压力体示意图"""
        # 压力体（矩形 - 扇形）
        # 矩形
        rect = Rectangle((0, -self.R), self.R, self.R, 
                        facecolor='lightyellow', edgecolor='black', 
                        linewidth=2, alpha=0.7, label='压力体')
        ax.add_patch(rect)
        
        # 扇形（要减去的部分）
        theta_start = -90
        theta_end = 0
        theta_array = np.linspace(np.radians(theta_start), np.radians(theta_end), 100)
        x_sector = np.concatenate([[0], self.R * np.cos(theta_array), [0]])
        y_sector = np.concatenate([[0], self.R * np.sin(theta_array), [0]])
        sector = Polygon(np.column_stack([x_sector, y_sector]), 
                        facecolor='white', edgecolor='red', 
                        linewidth=2, alpha=0.9, label='扇形（减去）')
        ax.add_patch(sector)
        
        # 自由液面
        ax.plot([-0.5, self.R+0.5], [0, 0], 'b-', linewidth=2, label='自由液面')
        
        # 曲面
        ax.plot(self.R * np.cos(theta_array), self.R * np.sin(theta_array), 
               'r-', linewidth=3, label='曲面AB')
        
        # 标注
        ax.plot(0, 0, 'ko', markersize=8)
        ax.text(-0.2, 0.2, 'O', fontsize=10)
        
        ax.plot(0, -self.R, 'ro', markersize=8)
        ax.text(-0.3, -self.R, 'A', fontsize=11, weight='bold')
        
        ax.plot(self.R, 0, 'ro', markersize=8)
        ax.text(self.R+0.2, 0, 'B', fontsize=11, weight='bold')
        
        # 压力体体积
        V_per_width = self.R**2 - np.pi * self.R**2 / 4
        ax.text(self.R*0.4, -self.R*0.5, 
               f'压力体面积\n{V_per_width:.3f}m²',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlim(-0.8, self.R+0.8)
        ax.set_ylim(-self.R-0.5, 0.8)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title('压力体示意图', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_force_decomposition(self, ax):
        """绘制力的分解"""
        # 简化示意，只画曲面和力
        # 曲面
        theta_array = np.linspace(-np.pi/2, 0, 100)
        x_curve = self.R * np.cos(theta_array)
        y_curve = self.R * np.sin(theta_array)
        ax.plot(x_curve, y_curve, 'r-', linewidth=3, label='曲面AB')
        
        # 圆心
        ax.plot(0, 0, 'ko', markersize=10, zorder=5)
        ax.text(-0.3, 0.2, 'O', fontsize=11, weight='bold')
        
        # 水平分力Px（红色箭头，向左）
        scale = 0.00015  # 比例因子
        Px_arrow_length = self.Px * scale
        ax.arrow(0, -self.R/2, -Px_arrow_length, 0, 
                head_width=0.15, head_length=0.2, fc='red', ec='red', 
                linewidth=2, zorder=4)
        ax.text(-Px_arrow_length/2, -self.R/2-0.3, 
               f'Px={self.Px/1000:.1f}kN',
               fontsize=10, ha='center', color='red', weight='bold')
        
        # 垂直分力Pz（蓝色箭头，向下）
        Pz_arrow_length = self.Pz * scale
        ax.arrow(self.R/2, 0, 0, -Pz_arrow_length,
                head_width=0.15, head_length=0.2, fc='blue', ec='blue',
                linewidth=2, zorder=4)
        ax.text(self.R/2+0.3, -Pz_arrow_length/2,
               f'Pz={self.Pz/1000:.1f}kN',
               fontsize=10, va='center', color='blue', weight='bold')
        
        # 坐标轴
        ax.axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.axvline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_xlim(-Px_arrow_length-0.5, self.R+0.5)
        ax.set_ylim(-max(Pz_arrow_length, self.R)-0.5, 0.8)
        ax.set_aspect('equal')
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_title('总压力分解（Px, Pz）', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_force_composition(self, ax):
        """绘制力的合成（矢量图）"""
        # 以原点为起点，绘制力的矢量三角形
        scale = 0.00015
        
        # Px（水平向左）
        Px_length = self.Px * scale
        ax.arrow(0, 0, -Px_length, 0,
                head_width=0.15, head_length=0.2, fc='red', ec='red',
                linewidth=2.5, label=f'Px={self.Px/1000:.1f}kN', zorder=3)
        
        # Pz（垂直向下，从Px终点开始）
        Pz_length = self.Pz * scale
        ax.arrow(-Px_length, 0, 0, -Pz_length,
                head_width=0.15, head_length=0.2, fc='blue', ec='blue',
                linewidth=2.5, label=f'Pz={self.Pz/1000:.1f}kN', zorder=3)
        
        # P（总压力，从原点到Pz终点）
        P_length = self.P * scale
        P_x = -Px_length
        P_y = -Pz_length
        ax.arrow(0, 0, P_x, P_y,
                head_width=0.2, head_length=0.25, fc='green', ec='green',
                linewidth=3, label=f'P={self.P/1000:.1f}kN', zorder=4)
        
        # 角度标注
        arc = Arc((0, 0), 1.0, 1.0, angle=0, theta1=180, theta2=180+self.theta_deg,
                 color='orange', linewidth=2, linestyle='--')
        ax.add_patch(arc)
        ax.text(-0.7, -0.3, f'θ={self.theta_deg:.1f}°',
               fontsize=10, color='orange', weight='bold')
        
        # 标注各力的数值
        ax.text(-Px_length/2, 0.3, f'Px', fontsize=11, ha='center', color='red', weight='bold')
        ax.text(-Px_length-0.3, -Pz_length/2, f'Pz', fontsize=11, va='center', color='blue', weight='bold')
        ax.text(P_x/2-0.2, P_y/2-0.2, f'P', fontsize=11, color='green', weight='bold')
        
        # 原点
        ax.plot(0, 0, 'ko', markersize=10, zorder=5)
        
        # 公式标注
        ax.text(0.5, -Pz_length-0.8,
               f'P = √(Px² + Pz²) = {self.P/1000:.1f}kN\ntanθ = Pz/Px = {self.Pz/self.Px:.3f}\nθ = {self.theta_deg:.1f}°',
               fontsize=10, ha='left',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
        
        ax.set_xlim(-Px_length-1, 1)
        ax.set_ylim(-Pz_length-1, 1)
        ax.set_aspect('equal')
        ax.set_xlabel('水平方向', fontsize=12)
        ax.set_ylabel('垂直方向', fontsize=12)
        ax.set_title('力的矢量合成', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)


def test_problem_101():
    """测试题目101"""
    # 已知条件
    R = 2.0     # 圆柱半径 (m)
    b = 3.0     # 宽度 (m)
    h = 3.0     # 水深 (m)
    gamma = 9800  # 水的重度 (N/m³)
    
    # 创建计算对象
    pressure = CurvedSurfacePressure(R, b, h, gamma)
    
    # 打印结果
    pressure.print_results()
    
    # 可视化
    fig = pressure.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_101_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_101_result.png")
    
    # 验证答案（合理性检查）
    assert pressure.Px > 0, "水平分力必须为正"
    assert pressure.Pz > 0, "垂直分力必须为正"
    assert pressure.P > 0, "总压力必须为正"
    assert pressure.P >= pressure.Px, "总压力必须大于等于水平分力"
    assert pressure.P >= pressure.Pz, "总压力必须大于等于垂直分力"
    assert 0 < pressure.theta < np.pi/2, "角度必须在0-90度之间"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("曲面总压力是静水力学的重要内容！")
    print("• 水平分力：Px = γ·hc·Ax（投影面平面总压力）")
    print("• 垂直分力：Pz = γ·V（压力体重量）")
    print("• 压力体：曲面、投影面、自由液面围成的体积")
    print("• 总压力：P = √(Px² + Pz²)")
    print("• 方向：tanθ = Pz/Px")
    print("• 作用点：通过曲率中心")
    print("• 应用：闸门设计、水工建筑物、容器设计")


if __name__ == "__main__":
    test_problem_101()
