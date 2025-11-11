"""
《水力学1000题详解》- 题目003: 多层液体压强
===============================================

知识点：多层不混溶液体压强计算、分层累加法
难度：⭐⭐ 中等题

功能：
1. 计算多层液体容器的压强分布
2. 可视化分层液体和压强变化
3. 分析密度差异对压强的影响
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib as mpl

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False


class MultilayerFluid:
    """多层液体容器类"""
    
    def __init__(self, layers, p0=120):
        """
        初始化多层液体参数
        
        参数:
            layers: 液层列表，每层为字典 {'name': 名称, 'rho': 密度(kg/m³), 'h': 厚度(m)}
            p0: 液面上方气压 (kPa，绝对压强)
        """
        self.layers = layers
        self.p0 = p0  # kPa
        self.g = 9.8  # m/s²
        self.p_atm = 101.325  # kPa
        
        # 计算各层界面的位置和压强
        self._calculate_interfaces()
    
    def _calculate_interfaces(self):
        """计算各层界面的高度和压强"""
        self.interface_heights = [0]  # 从顶部开始
        self.interface_pressures = [self.p0]  # 顶部气压
        
        current_height = 0
        current_pressure = self.p0
        
        for layer in self.layers:
            # 累加高度
            current_height += layer['h']
            self.interface_heights.append(current_height)
            
            # 计算该层底部压强
            dp = layer['rho'] * self.g * layer['h'] / 1000  # 转换为kPa
            current_pressure += dp
            self.interface_pressures.append(current_pressure)
    
    def pressure_at_depth(self, depth):
        """
        计算指定深度处的压强
        
        参数:
            depth: 从液面算起的深度 (m)
        
        返回:
            压强 (kPa)
        """
        if depth < 0 or depth > self.interface_heights[-1]:
            raise ValueError(f"深度必须在0到{self.interface_heights[-1]}m之间")
        
        # 找到对应的液层
        for i, layer in enumerate(self.layers):
            if depth <= self.interface_heights[i + 1]:
                # 在第i层内
                depth_in_layer = depth - self.interface_heights[i]
                p = self.interface_pressures[i] + \
                    layer['rho'] * self.g * depth_in_layer / 1000
                return p
        
        return self.interface_pressures[-1]
    
    def plot_multilayer_system(self, save_path=None):
        """绘制多层液体系统及压强分布"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
        
        # ===== 左图：多层液体容器示意图 =====
        ax1.set_xlim(-0.5, 2)
        total_height = self.interface_heights[-1]
        ax1.set_ylim(-0.5, total_height + 1)
        ax1.set_aspect('equal')
        
        # 容器外壁
        container_rect = Rectangle((0, 0), 1, total_height + 0.5,
                                   linewidth=3, edgecolor='black',
                                   facecolor='none')
        ax1.add_patch(container_rect)
        
        # 定义颜色
        colors = ['lightyellow', 'lightblue', 'lightgray']
        
        # 绘制各液层
        for i, layer in enumerate(self.layers):
            y_bottom = total_height - self.interface_heights[i + 1]
            height = layer['h']
            
            layer_rect = Rectangle((0, y_bottom), 1, height,
                                    facecolor=colors[i % len(colors)],
                                    edgecolor='blue', linewidth=1.5,
                                    alpha=0.7)
            ax1.add_patch(layer_rect)
            
            # 标注液层名称和密度
            y_center = y_bottom + height / 2
            ax1.text(0.5, y_center, 
                     f"{layer['name']}\nρ={layer['rho']} kg/m³\nh={layer['h']} m",
                     ha='center', va='center', fontsize=10,
                     fontweight='bold', 
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # 界面线
            if i < len(self.layers) - 1:
                ax1.axhline(y=y_bottom + height, color='darkblue',
                           linestyle='--', linewidth=2)
        
        # 顶部气压标注
        ax1.text(0.5, total_height + 0.7,
                 f'气压: p₀ = {self.p0} kPa',
                 ha='center', fontsize=11, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6))
        
        # 压强箭头
        num_arrows = 8
        for depth in np.linspace(0, total_height, num_arrows):
            y_pos = total_height - depth
            p = self.pressure_at_depth(depth)
            # 箭头长度与压强成正比
            arrow_length = (p - self.p0) / (self.interface_pressures[-1] - self.p0) * 0.5
            
            if arrow_length > 0:
                ax1.arrow(1, y_pos, arrow_length, 0,
                         head_width=0.15, head_length=0.05,
                         fc='red', ec='red', alpha=0.6)
        
        ax1.set_xlabel('容器宽度', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('多层液体容器示意图', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # ===== 右图：压强-深度曲线 =====
        depths = np.linspace(0, total_height, 200)
        pressures = [self.pressure_at_depth(d) for d in depths]
        
        ax2.plot(pressures, depths, 'b-', linewidth=2.5, label='压强分布')
        ax2.fill_betweenx(depths, self.p0, pressures, alpha=0.3, color='blue')
        
        # 标注各层界面
        for i, (h, p) in enumerate(zip(self.interface_heights, self.interface_pressures)):
            ax2.plot(p, h, 'ro', markersize=10)
            
            label = '液面' if i == 0 else f'{self.layers[i-1]["name"]}底部'
            ax2.text(p + 2, h, f'{label}\n{p:.2f} kPa',
                    fontsize=10, va='center', fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 分层线
        for h in self.interface_heights[1:]:
            ax2.axhline(y=h, color='gray', linestyle='--',
                       linewidth=1.5, alpha=0.5)
        
        ax2.set_xlabel('压强 (kPa)', fontsize=12)
        ax2.set_ylabel('深度 (m)', fontsize=12)
        ax2.set_title('多层液体压强分布曲线', fontsize=14, fontweight='bold')
        ax2.legend(loc='lower right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("题目003: 多层液体压强 - 计算结果")
        print("=" * 70)
        
        print(f"\n【题目参数】")
        print(f"  液面上方气压: p₀ = {self.p0} kPa (绝对压强)")
        print(f"  液层数: {len(self.layers)} 层")
        print(f"\n  液层详情:")
        
        for i, layer in enumerate(self.layers, 1):
            print(f"    第{i}层 - {layer['name']}:")
            print(f"      密度: ρ = {layer['rho']} kg/m³")
            print(f"      厚度: h = {layer['h']} m")
        
        print(f"\n【逐层压强计算】")
        
        for i, layer in enumerate(self.layers):
            p_top = self.interface_pressures[i]
            p_bottom = self.interface_pressures[i + 1]
            dp = p_bottom - p_top
            
            print(f"\n  第{i+1}层（{layer['name']}）:")
            print(f"    顶部压强: p_{i} = {p_top:.3f} kPa")
            print(f"    压强增量: Δp = ρgh = {layer['rho']} × {self.g} × {layer['h']}")
            print(f"            = {dp:.3f} kPa")
            print(f"    底部压强: p_{i+1} = {p_bottom:.3f} kPa")
        
        print(f"\n【最终结果】")
        print(f"  容器底部总压强: p_bottom = {self.interface_pressures[-1]:.3f} kPa")
        print(f"  液面到底部压强增量: Δp_total = {self.interface_pressures[-1] - self.p0:.3f} kPa")
        print(f"  等效水深: h_eq = {(self.interface_pressures[-1] - self.p0) * 1000 / (1000 * self.g):.3f} m")
        
        print("\n" + "=" * 70)


def main():
    """主程序"""
    
    print("\n" + "="*70)
    print("《水力学1000题详解》- 题目003")
    print("多层液体压强计算")
    print("="*70 + "\n")
    
    # 定义三层液体系统
    layers = [
        {'name': '油（Oil）', 'rho': 800, 'h': 0.5},    # 第1层
        {'name': '水（Water）', 'rho': 1000, 'h': 1.0},  # 第2层
        {'name': '水银（Mercury）', 'rho': 13600, 'h': 0.3}  # 第3层
    ]
    
    # 创建多层液体实例
    fluid_system = MultilayerFluid(layers=layers, p0=120)
    
    # 打印计算结果
    fluid_system.print_results()
    
    # 绘制可视化图表
    print("\n正在生成多层液体系统可视化图...")
    fluid_system.plot_multilayer_system()
    
    # 额外分析
    print("\n【额外分析】不同液层对总压强的贡献:")
    print(f"{'液层':<15} {'密度(kg/m³)':<12} {'厚度(m)':<10} {'压强贡献(kPa)':<15} {'占比(%)':<10}")
    print("-" * 70)
    
    total_dp = fluid_system.interface_pressures[-1] - fluid_system.p0
    
    for i, layer in enumerate(layers):
        dp = fluid_system.interface_pressures[i + 1] - fluid_system.interface_pressures[i]
        contribution = (dp / total_dp) * 100
        print(f"{layer['name']:<15} {layer['rho']:<12} {layer['h']:<10.2f} "
              f"{dp:<15.3f} {contribution:<10.2f}")
    
    print(f"\n气压贡献: {fluid_system.p0} kPa")
    print(f"液体总贡献: {total_dp:.3f} kPa")
    print(f"容器底部总压强: {fluid_system.interface_pressures[-1]:.3f} kPa")
    
    print("\n✅ 题目003 计算完成！\n")


def test_multilayer_calculation():
    """单元测试"""
    print("\n【单元测试】多层液体压强计算验证")
    print("-" * 50)
    
    layers = [
        {'name': '油', 'rho': 800, 'h': 0.5},
        {'name': '水', 'rho': 1000, 'h': 1.0},
        {'name': '水银', 'rho': 13600, 'h': 0.3}
    ]
    
    system = MultilayerFluid(layers=layers, p0=120)
    
    # 测试1：油层底部压强
    p1_expected = 120 + 800 * 9.8 * 0.5 / 1000
    p1_actual = system.interface_pressures[1]
    assert abs(p1_actual - p1_expected) < 0.01, "油层底部压强计算错误"
    print(f"✓ 测试1通过: 油层底部压强 = {p1_actual:.3f} kPa")
    
    # 测试2：水层底部压强
    p2_expected = p1_expected + 1000 * 9.8 * 1.0 / 1000
    p2_actual = system.interface_pressures[2]
    assert abs(p2_actual - p2_expected) < 0.01, "水层底部压强计算错误"
    print(f"✓ 测试2通过: 水层底部压强 = {p2_actual:.3f} kPa")
    
    # 测试3：容器底部压强
    p3_expected = p2_expected + 13600 * 9.8 * 0.3 / 1000
    p3_actual = system.interface_pressures[3]
    assert abs(p3_actual - p3_expected) < 0.1, "容器底部压强计算错误"
    print(f"✓ 测试3通过: 容器底部压强 = {p3_actual:.3f} kPa")
    
    # 测试4：任意深度压强
    p_mid = system.pressure_at_depth(0.75)  # 水层中部
    expected_mid = system.interface_pressures[1] + 1000 * 9.8 * 0.25 / 1000
    assert abs(p_mid - expected_mid) < 0.01, "任意深度压强计算错误"
    print(f"✓ 测试4通过: 水层中部压强 = {p_mid:.3f} kPa")
    
    print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    # 运行单元测试
    test_multilayer_calculation()
    
    # 运行主程序
    main()
