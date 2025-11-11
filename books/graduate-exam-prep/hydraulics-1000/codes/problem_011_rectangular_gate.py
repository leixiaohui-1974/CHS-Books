"""
《水力学1000题详解》- 题目011: 矩形竖直闸门总压力
========================================================

知识点：平面总压力、压力中心、力矩分析
难度：⭐ 基础题

功能：
1. 计算矩形平板受到的水压总力
2. 计算压力中心位置
3. 可视化压强分布和压力作用点
4. 分析不同尺寸和水深的影响
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import matplotlib as mpl

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False


class RectangularGate:
    """矩形闸门类"""
    
    def __init__(self, width, height, gamma=9800):
        """
        初始化矩形闸门参数
        
        参数:
            width: 闸门宽度 (m)
            height: 闸门高度 (m)
            gamma: 水的容重 (N/m³)
        """
        self.b = width
        self.h = height
        self.gamma = gamma
        self.A = self.b * self.h  # 面积
        self.h_c = self.h / 2  # 形心深度
        self.I_c = self.b * self.h**3 / 12  # 对形心轴的惯性矩
        
        # 计算总压力和压力中心
        self._calculate_pressure()
    
    def _calculate_pressure(self):
        """计算总压力和压力中心"""
        # 总压力
        self.P = self.gamma * self.h_c * self.A
        
        # 压力中心深度
        self.y_p = self.h_c + self.I_c / (self.h_c * self.A)
        
        # 压力中心距底部的距离
        self.e_bottom = self.h - self.y_p
    
    def plot_pressure_analysis(self, save_path=None):
        """绘制压力分析图"""
        
        fig = plt.figure(figsize=(16, 6))
        gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        
        # ===== 左图：闸门与压强分布示意图 =====
        ax1.set_xlim(-1, 3)
        ax1.set_ylim(-0.5, self.h + 0.5)
        ax1.set_aspect('equal')
        
        # 绘制闸门
        gate = Rectangle((0, 0), 0.2, self.h,
                         facecolor='gray', edgecolor='black',
                         linewidth=3, label='闸门')
        ax1.add_patch(gate)
        
        # 绘制水体
        water = Rectangle((0.2, 0), 1.5, self.h,
                         facecolor='lightblue', alpha=0.5,
                         label='水体')
        ax1.add_patch(water)
        
        # 水面线
        ax1.plot([0, 1.7], [self.h, self.h], 'b--', linewidth=2, label='水面')
        
        # 压强分布箭头（三角形分布）
        num_arrows = 10
        depths = np.linspace(0, self.h, num_arrows)
        
        for depth in depths:
            y_pos = self.h - depth
            pressure = self.gamma * depth / 1000  # kPa
            # 箭头长度与压强成正比
            max_pressure = self.gamma * self.h / 1000
            arrow_length = (pressure / max_pressure) * 1.0
            
            if arrow_length > 0:
                arrow = FancyArrowPatch((0, y_pos), (-arrow_length, y_pos),
                                       arrowstyle='->', mutation_scale=15,
                                       color='red', linewidth=2, alpha=0.6)
                ax1.add_patch(arrow)
        
        # 标注形心位置
        ax1.plot(-0.3, self.h - self.h_c, 'go', markersize=12, label='形心')
        ax1.text(-0.5, self.h - self.h_c, f'形心\nh={self.h_c:.2f}m',
                ha='right', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 标注压力中心
        ax1.plot(-0.3, self.h - self.y_p, 'rs', markersize=12, label='压力中心')
        ax1.text(-0.5, self.h - self.y_p, f'压力中心\ny_p={self.y_p:.3f}m',
                ha='right', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='salmon', alpha=0.7))
        
        # 总压力箭头
        arrow_P = FancyArrowPatch((-0.3, self.h - self.y_p), 
                                  (-1.2, self.h - self.y_p),
                                  arrowstyle='->', mutation_scale=30,
                                  color='red', linewidth=4)
        ax1.add_patch(arrow_P)
        ax1.text(-1.5, self.h - self.y_p + 0.3, f'P={self.P/1000:.1f} kN',
                fontsize=12, fontweight='bold', color='red')
        
        # 标注尺寸
        ax1.text(0.1, -0.3, f'宽度b={self.b}m', ha='center', fontsize=10)
        ax1.plot([-0.7, -0.7], [0, self.h], 'k-', linewidth=1.5)
        ax1.text(-0.9, self.h/2, f'h={self.h}m', rotation=90,
                va='center', fontsize=11, fontweight='bold')
        
        ax1.set_xlabel('水平位置 (m)', fontsize=11)
        ax1.set_ylabel('高度 (m)', fontsize=11)
        ax1.set_title('闸门与压强分布', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # ===== 中图：压强分布曲线 =====
        depths = np.linspace(0, self.h, 100)
        pressures = self.gamma * depths / 1000  # kPa
        
        ax2.plot(pressures, depths, 'b-', linewidth=2.5, label='压强p(y)')
        ax2.fill_betweenx(depths, 0, pressures, alpha=0.3, color='blue')
        
        # 标注特殊点
        ax2.plot(0, 0, 'co', markersize=10, label='顶部(p=0)')
        ax2.plot(pressures[-1], self.h, 'mo', markersize=10,
                label=f'底部(p={pressures[-1]:.1f} kPa)')
        
        # 形心和压力中心
        p_c = self.gamma * self.h_c / 1000
        ax2.plot(p_c, self.h_c, 'go', markersize=12, label='形心')
        ax2.axhline(y=self.h_c, color='green', linestyle='--', alpha=0.5)
        
        p_cp = self.gamma * self.y_p / 1000
        ax2.plot(p_cp, self.y_p, 'rs', markersize=12, label='压力中心')
        ax2.axhline(y=self.y_p, color='red', linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('压强 (kPa)', fontsize=11)
        ax2.set_ylabel('深度 (m)', fontsize=11)
        ax2.set_title('压强-深度曲线', fontsize=13, fontweight='bold')
        ax2.legend(loc='lower right', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()
        
        # ===== 右图：参数分析（总压力vs水深） =====
        heights = np.linspace(1, 10, 50)
        pressures_total = []
        y_ps = []
        
        for h_temp in heights:
            gate_temp = RectangularGate(self.b, h_temp, self.gamma)
            pressures_total.append(gate_temp.P / 1000)  # kN
            y_ps.append(gate_temp.y_p)
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(heights, pressures_total, 'b-', linewidth=2.5,
                        label='总压力P', marker='o', markersize=4)
        line2 = ax3_twin.plot(heights, y_ps, 'r--', linewidth=2.5,
                             label='压力中心y_p', marker='s', markersize=4)
        
        # 当前闸门标记
        ax3.plot(self.h, self.P/1000, 'bo', markersize=15,
                markeredgewidth=3, markerfacecolor='none')
        ax3_twin.plot(self.h, self.y_p, 'rs', markersize=15,
                     markeredgewidth=3, markerfacecolor='none')
        
        ax3.set_xlabel('闸门高度 h (m)', fontsize=11)
        ax3.set_ylabel('总压力 P (kN)', fontsize=11, color='b')
        ax3_twin.set_ylabel('压力中心深度 y_p (m)', fontsize=11, color='r')
        ax3.set_title('参数影响分析', fontsize=13, fontweight='bold')
        
        ax3.tick_params(axis='y', labelcolor='b')
        ax3_twin.tick_params(axis='y', labelcolor='r')
        
        # 组合图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper left', fontsize=9)
        
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        
        plt.show()
    
    def print_results(self):
        """打印详细计算结果"""
        print("=" * 70)
        print("题目011: 矩形竖直闸门总压力 - 计算结果")
        print("=" * 70)
        
        print(f"\n【闸门参数】")
        print(f"  宽度: b = {self.b} m")
        print(f"  高度: h = {self.h} m")
        print(f"  面积: A = {self.A} m²")
        print(f"  水的容重: γ = {self.gamma} N/m³")
        
        print(f"\n【几何参数】")
        print(f"  形心深度: h_c = h/2 = {self.h_c} m")
        print(f"  惯性矩: I_c = bh³/12 = {self.b} × {self.h}³/12 = {self.I_c:.3f} m⁴")
        
        print(f"\n【总压力计算】")
        print(f"  公式: P = γ × h_c × A")
        print(f"  P = {self.gamma} × {self.h_c} × {self.A}")
        print(f"  P = {self.P:.0f} N = {self.P/1000:.1f} kN")
        print(f"  【等效力】: 约 {self.P/9800:.1f} 吨力")
        
        print(f"\n【压力中心计算】")
        print(f"  公式: y_p = h_c + I_c/(h_c × A)")
        print(f"  y_p = {self.h_c} + {self.I_c:.3f}/({self.h_c} × {self.A})")
        print(f"  y_p = {self.h_c} + {self.I_c/(self.h_c * self.A):.3f}")
        print(f"  y_p = {self.y_p:.3f} m （从水面算起）")
        print(f"  y_p = {self.y_p:.3f} m （从闸门顶部算起）")
        print(f"  距底部: {self.e_bottom:.3f} m")
        
        print(f"\n【压强分布】")
        print(f"  顶部（水面）: p = 0 kPa")
        print(f"  形心处: p = γh_c = {self.gamma * self.h_c / 1000:.1f} kPa")
        print(f"  底部（水深{self.h}m）: p = γh = {self.gamma * self.h / 1000:.1f} kPa")
        print(f"  分布形式: 线性三角形分布")
        
        print(f"\n【理论验证】")
        print(f"  压力中心与形心关系: y_p - h_c = {self.y_p - self.h_c:.3f} m > 0 ✓")
        print(f"  压力中心位置比: y_p/h = {self.y_p/self.h:.3f}")
        print(f"  理论值（三角形）: 2/3 = 0.667")
        print(f"  【结论】: 压力中心总在形心下方 ✓")
        
        print("\n" + "=" * 70)
    
    def calculate_opening_force(self, hinge_position='bottom'):
        """
        计算闸门开启力（假设底部铰接）
        
        参数:
            hinge_position: 铰链位置 ('bottom' 或 'top')
        
        返回:
            required_force: 所需作用力 (N)
        """
        if hinge_position == 'bottom':
            # 底部铰接，顶部施力
            moment_arm_pressure = self.e_bottom  # 压力作用点到铰链的距离
            moment_arm_force = self.h  # 顶部力到铰链的距离
            
            # 力矩平衡: F × h = P × (h - y_p)
            required_force = self.P * moment_arm_pressure / moment_arm_force
            
            print(f"\n【闸门开启力计算】")
            print(f"  铰链位置: 底部")
            print(f"  施力位置: 顶部")
            print(f"  压力力臂: l_P = {moment_arm_pressure:.3f} m")
            print(f"  作用力力臂: l_F = {moment_arm_force:.3f} m")
            print(f"  力矩平衡: F × {moment_arm_force} = P × {moment_arm_pressure:.3f}")
            print(f"  F = {self.P:.0f} × {moment_arm_pressure:.3f} / {moment_arm_force}")
            print(f"  F = {required_force:.0f} N = {required_force/1000:.1f} kN")
            print(f"  【结论】: 需要 {required_force/1000:.1f} kN 的向上作用力")
            
            return required_force
        else:
            raise NotImplementedError("仅实现底部铰接情况")


def main():
    """主程序"""
    
    print("\n" + "="*70)
    print("《水力学1000题详解》- 题目011")
    print("矩形竖直闸门总压力计算")
    print("="*70 + "\n")
    
    # 创建闸门实例
    gate = RectangularGate(width=3.0, height=4.0, gamma=9800)
    
    # 打印计算结果
    gate.print_results()
    
    # 计算开启力
    gate.calculate_opening_force(hinge_position='bottom')
    
    # 绘制分析图
    print("\n正在生成压力分析图...")
    gate.plot_pressure_analysis()
    
    print("\n✅ 题目011 计算完成！\n")


def test_rectangular_gate():
    """单元测试"""
    print("\n【单元测试】矩形闸门总压力计算验证")
    print("-" * 50)
    
    gate = RectangularGate(3.0, 4.0, 9800)
    
    # 测试1：面积
    assert gate.A == 12.0, "面积计算错误"
    print(f"✓ 测试1通过: 面积 = {gate.A} m²")
    
    # 测试2：形心深度
    assert gate.h_c == 2.0, "形心深度计算错误"
    print(f"✓ 测试2通过: 形心深度 = {gate.h_c} m")
    
    # 测试3：惯性矩
    I_c_expected = 3 * 4**3 / 12
    assert abs(gate.I_c - I_c_expected) < 0.01, "惯性矩计算错误"
    print(f"✓ 测试3通过: 惯性矩 = {gate.I_c:.3f} m⁴")
    
    # 测试4：总压力
    P_expected = 9800 * 2.0 * 12
    assert abs(gate.P - P_expected) < 1, "总压力计算错误"
    print(f"✓ 测试4通过: 总压力 = {gate.P/1000:.1f} kN")
    
    # 测试5：压力中心
    y_p_expected = 2.0 + 16 / (2.0 * 12)
    assert abs(gate.y_p - y_p_expected) < 0.01, "压力中心计算错误"
    print(f"✓ 测试5通过: 压力中心 = {gate.y_p:.3f} m")
    
    # 测试6：压力中心在形心下方
    assert gate.y_p > gate.h_c, "压力中心应在形心下方"
    print(f"✓ 测试6通过: 压力中心在形心下方（y_p={gate.y_p:.3f} > h_c={gate.h_c}）")
    
    print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    # 运行单元测试
    test_rectangular_gate()
    
    # 运行主程序
    main()
