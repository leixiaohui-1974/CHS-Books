"""
《水力学1000题详解》- 题目001: 矩形水箱压强分布
===============================================

知识点：静水压强分布、相对压强与绝对压强
难度：⭐ 基础题

功能：
1. 计算水箱底部和任意点的压强
2. 绘制压强分布图
3. 可视化压强沿水深的变化规律
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib as mpl

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False

# ====================
# 1. 题目参数
# ====================

class WaterTank:
    """水箱类"""
    def __init__(self, height, width, length, water_depth, gamma=9800):
        """
        初始化水箱参数
        
        参数:
            height: 水箱高度 (m)
            width: 水箱宽度 (m)
            length: 水箱长度 (m)
            water_depth: 水深 (m)
            gamma: 水的容重 (N/m³), 默认9800
        """
        self.height = height
        self.width = width
        self.length = length
        self.water_depth = water_depth
        self.gamma = gamma
        self.p_atm = 101.325  # 标准大气压 (kPa)
    
    def pressure_at_depth(self, depth, absolute=False):
        """
        计算指定水深处的压强
        
        参数:
            depth: 水深 (m)
            absolute: 是否返回绝对压强
        
        返回:
            压强 (kPa)
        """
        if depth < 0 or depth > self.water_depth:
            raise ValueError(f"水深必须在0到{self.water_depth}m之间")
        
        # 相对压强
        p_relative = self.gamma * depth / 1000  # 转换为kPa
        
        if absolute:
            return self.p_atm + p_relative
        else:
            return p_relative
    
    def pressure_distribution(self, num_points=100):
        """
        获取压强分布数据
        
        参数:
            num_points: 采样点数
        
        返回:
            depths: 水深数组 (m)
            pressures: 相对压强数组 (kPa)
        """
        depths = np.linspace(0, self.water_depth, num_points)
        pressures = self.gamma * depths / 1000
        return depths, pressures
    
    def plot_pressure_distribution(self, save_path=None):
        """
        绘制压强分布图
        
        参数:
            save_path: 保存路径（可选）
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # ===== 左图：水箱剖面与压强分布 =====
        ax1.set_xlim(-0.5, 2)
        ax1.set_ylim(-0.5, self.height + 0.5)
        ax1.set_aspect('equal')
        
        # 绘制水箱
        tank_rect = Rectangle((0, 0), 1, self.height, 
                               linewidth=3, edgecolor='black', 
                               facecolor='none', label='水箱壁')
        ax1.add_patch(tank_rect)
        
        # 绘制水体
        water_rect = Rectangle((0, self.height - self.water_depth), 
                                1, self.water_depth,
                                facecolor='lightblue', alpha=0.5, 
                                label='水体')
        ax1.add_patch(water_rect)
        
        # 水面线
        ax1.plot([0, 1], [self.height - self.water_depth] * 2, 
                 'b--', linewidth=2, label='水面')
        
        # 压强分布箭头
        num_arrows = 10
        depths = np.linspace(0, self.water_depth, num_arrows)
        
        for depth in depths:
            y_pos = self.height - depth
            pressure = self.pressure_at_depth(depth)
            # 箭头长度与压强成正比
            arrow_length = pressure / (self.gamma * self.water_depth / 1000) * 0.5
            
            ax1.arrow(1, y_pos, arrow_length, 0, 
                      head_width=0.1, head_length=0.05,
                      fc='red', ec='red', alpha=0.6)
        
        # 标注关键点
        # A点（底部中心）
        ax1.plot(0.5, 0, 'ro', markersize=10, label='A点（底部）')
        ax1.text(0.5, -0.3, 'A点', ha='center', fontsize=12, fontweight='bold')
        
        # B点（水面下1.5m）
        b_depth = 1.5
        b_y = self.height - b_depth
        ax1.plot(0.5, b_y, 'go', markersize=10, label='B点（1.5m深）')
        ax1.text(0.5, b_y - 0.3, 'B点', ha='center', fontsize=12, fontweight='bold')
        
        ax1.set_xlabel('水平位置', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('水箱剖面与压强分布示意图', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # ===== 右图：压强-水深曲线 =====
        depths, pressures = self.pressure_distribution()
        
        ax2.plot(pressures, depths, 'b-', linewidth=2.5, label='压强分布曲线')
        ax2.fill_betweenx(depths, 0, pressures, alpha=0.3, color='blue')
        
        # 标注关键点
        # A点
        p_A = self.pressure_at_depth(self.water_depth)
        ax2.plot(p_A, self.water_depth, 'ro', markersize=12, label=f'A点: {p_A:.2f} kPa')
        ax2.text(p_A + 1, self.water_depth, f'{p_A:.2f} kPa', 
                 fontsize=11, va='center', fontweight='bold')
        
        # B点
        p_B = self.pressure_at_depth(1.5)
        ax2.plot(p_B, 1.5, 'go', markersize=12, label=f'B点: {p_B:.2f} kPa')
        ax2.text(p_B + 1, 1.5, f'{p_B:.2f} kPa', 
                 fontsize=11, va='center', fontweight='bold')
        
        # 水面
        ax2.axhline(y=0, color='cyan', linestyle='--', linewidth=2, label='水面')
        
        ax2.set_xlabel('相对压强 (kPa)', fontsize=12)
        ax2.set_ylabel('水深 (m)', fontsize=12)
        ax2.set_title('静水压强分布曲线', fontsize=14, fontweight='bold')
        ax2.legend(loc='lower right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()  # 反转y轴，使水深向下增加
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 60)
        print("题目001: 矩形水箱压强分布 - 计算结果")
        print("=" * 60)
        print(f"\n【题目参数】")
        print(f"  水箱尺寸: {self.length}m × {self.width}m × {self.height}m")
        print(f"  水深: {self.water_depth} m")
        print(f"  水的容重: {self.gamma} N/m³")
        print(f"  标准大气压: {self.p_atm} kPa")
        
        print(f"\n【计算结果】")
        
        # （1）A点（底部中心）压强
        p_A_relative = self.pressure_at_depth(self.water_depth, absolute=False)
        p_A_absolute = self.pressure_at_depth(self.water_depth, absolute=True)
        
        print(f"\n（1）A点（水箱底部中心）:")
        print(f"     相对压强: {p_A_relative:.3f} kPa")
        print(f"     绝对压强: {p_A_absolute:.3f} kPa")
        print(f"     计算过程: p = γh = {self.gamma} × {self.water_depth} = {p_A_relative * 1000:.0f} Pa")
        
        # （2）B点（水面下1.5m）压强
        b_depth = 1.5
        p_B = self.pressure_at_depth(b_depth, absolute=False)
        
        print(f"\n（2）B点（水面下1.5m处）:")
        print(f"     相对压强: {p_B:.3f} kPa")
        print(f"     计算过程: p = γh = {self.gamma} × {b_depth} = {p_B * 1000:.0f} Pa")
        
        # （3）压强分布规律
        print(f"\n（3）压强分布规律:")
        print(f"     线性分布: p(z) = γz")
        print(f"     水面处: p = 0 kPa (相对压强)")
        print(f"     水底处: p = {p_A_relative:.2f} kPa")
        print(f"     梯度: dp/dz = γ = {self.gamma / 1000:.2f} kPa/m")
        
        print("\n" + "=" * 60)


# ====================
# 2. 主程序
# ====================

def main():
    """主程序"""
    
    print("\n" + "="*60)
    print("《水力学1000题详解》- 题目001")
    print("矩形水箱压强分布")
    print("="*60 + "\n")
    
    # 创建水箱实例
    tank = WaterTank(
        height=3.0,      # 水箱高度 (m)
        width=2.0,       # 水箱宽度 (m)
        length=4.0,      # 水箱长度 (m)
        water_depth=2.5, # 水深 (m)
        gamma=9800       # 水的容重 (N/m³)
    )
    
    # 打印计算结果
    tank.print_results()
    
    # 绘制压强分布图
    print("\n正在生成压强分布图...")
    tank.plot_pressure_distribution()
    
    # 额外计算：不同水深的压强
    print("\n【补充计算】不同水深处的压强:")
    print(f"{'水深(m)':<10} {'相对压强(kPa)':<15} {'绝对压强(kPa)':<15}")
    print("-" * 40)
    
    for depth in np.linspace(0, tank.water_depth, 6):
        p_rel = tank.pressure_at_depth(depth, absolute=False)
        p_abs = tank.pressure_at_depth(depth, absolute=True)
        print(f"{depth:<10.2f} {p_rel:<15.3f} {p_abs:<15.3f}")
    
    print("\n✅ 题目001 计算完成！\n")


# ====================
# 3. 单元测试
# ====================

def test_pressure_calculation():
    """测试压强计算"""
    print("\n【单元测试】压强计算验证")
    print("-" * 40)
    
    tank = WaterTank(3.0, 2.0, 4.0, 2.5, 9800)
    
    # 测试1：底部压强
    p_bottom = tank.pressure_at_depth(2.5, absolute=False)
    expected = 24.5
    assert abs(p_bottom - expected) < 0.01, f"底部压强计算错误: {p_bottom} != {expected}"
    print(f"✓ 测试1通过: 底部相对压强 = {p_bottom:.2f} kPa")
    
    # 测试2：绝对压强
    p_absolute = tank.pressure_at_depth(2.5, absolute=True)
    expected_abs = 125.825
    assert abs(p_absolute - expected_abs) < 0.01, f"绝对压强计算错误: {p_absolute} != {expected_abs}"
    print(f"✓ 测试2通过: 底部绝对压强 = {p_absolute:.3f} kPa")
    
    # 测试3：B点压强
    p_B = tank.pressure_at_depth(1.5, absolute=False)
    expected_B = 14.7
    assert abs(p_B - expected_B) < 0.01, f"B点压强计算错误: {p_B} != {expected_B}"
    print(f"✓ 测试3通过: B点相对压强 = {p_B:.2f} kPa")
    
    # 测试4：水面压强
    p_surface = tank.pressure_at_depth(0, absolute=False)
    assert abs(p_surface) < 0.01, f"水面压强应为0: {p_surface}"
    print(f"✓ 测试4通过: 水面相对压强 = {p_surface:.2f} kPa")
    
    print("\n✅ 所有测试通过！\n")


# ====================
# 4. 运行程序
# ====================

if __name__ == "__main__":
    # 运行单元测试
    test_pressure_calculation()
    
    # 运行主程序
    main()
