#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第01章 静水力学 - 题目10：多层液体压强计算

题目描述：
容器中有三层液体：
- 底层：水银，高度h1=0.2m，密度ρ1=13600 kg/m³
- 中层：水，高度h2=1.0m，密度ρ2=1000 kg/m³  
- 上层：油，高度h3=0.5m，密度ρ3=800 kg/m³
求容器底部的压强。

知识点：
- 多层液体压强叠加
- 界面压强连续性
- 压强传递

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MultilayerFluid:
    """多层液体压强计算类"""
    
    def __init__(self, layers: list, p0: float = 101325.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        layers : list of dict
            液体层列表，每层包含：
            {'name': 名称, 'h': 高度(m), 'rho': 密度(kg/m³), 'color': 颜色}
        p0 : float
            顶部气压 (Pa)
        g : float
            重力加速度 (m/s²)
        """
        self.layers = layers
        self.p0 = p0
        self.g = g
        
        # 计算总高度和界面位置
        self.total_height = sum(layer['h'] for layer in layers)
        self.interface_depths = self._calculate_interface_depths()
        
    def _calculate_interface_depths(self) -> list:
        """计算各界面的深度（从顶部算起）"""
        depths = [0]
        cumulative_h = 0
        for layer in self.layers:
            cumulative_h += layer['h']
            depths.append(cumulative_h)
        return depths
    
    def pressure_at_depth(self, z: float) -> float:
        """
        计算某深度处的压强
        
        Parameters:
        -----------
        z : float
            从顶部向下的深度 (m)
            
        Returns:
        --------
        float : 压强 (Pa)
        """
        p = self.p0
        cumulative_h = 0
        
        for layer in self.layers:
            layer_top = cumulative_h
            layer_bottom = cumulative_h + layer['h']
            
            if z <= layer_top:
                # 在当前层上方
                break
            elif z <= layer_bottom:
                # 在当前层内
                p += layer['rho'] * self.g * (z - layer_top)
                break
            else:
                # 穿过整层
                p += layer['rho'] * self.g * layer['h']
                cumulative_h += layer['h']
        
        return p
    
    def bottom_pressure(self) -> float:
        """计算容器底部压强"""
        return self.pressure_at_depth(self.total_height)
    
    def interface_pressures(self) -> list:
        """计算各界面压强"""
        pressures = []
        for depth in self.interface_depths:
            pressures.append(self.pressure_at_depth(depth))
        return pressures
    
    def plot_multilayer_system(self):
        """绘制多层液体系统示意图"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 8))
        
        # 左图：液体分层示意图
        ax1 = axes[0]
        
        # 从底部向上绘制
        y_bottom = 0
        for i, layer in enumerate(reversed(self.layers)):
            y_top = y_bottom + layer['h']
            
            # 绘制液体层
            rect = patches.Rectangle((0, y_bottom), 2, layer['h'],
                                     linewidth=2, edgecolor='black',
                                     facecolor=layer['color'], alpha=0.6)
            ax1.add_patch(rect)
            
            # 标注层名称和参数
            y_mid = (y_bottom + y_top) / 2
            layer_idx = len(self.layers) - i - 1
            ax1.text(1, y_mid, f"{layer['name']}\n"
                              f"h={layer['h']}m\n"
                              f"ρ={layer['rho']}kg/m³",
                    ha='center', va='center', fontsize=11, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # 标注高度
            ax1.annotate('', xy=(2.3, y_bottom), xytext=(2.3, y_top),
                        arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            ax1.text(2.6, y_mid, f'h{layer_idx+1}={layer["h"]}m',
                    fontsize=10, color='red', fontweight='bold')
            
            y_bottom = y_top
        
        # 标注顶部气压
        ax1.text(1, y_bottom + 0.3, f'p₀={self.p0/101325:.2f}atm',
                ha='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 绘制容器壁
        ax1.plot([0, 0], [0, self.total_height], 'k-', linewidth=4)
        ax1.plot([2, 2], [0, self.total_height], 'k-', linewidth=4)
        ax1.plot([0, 2], [0, 0], 'k-', linewidth=4)  # 底部
        
        ax1.set_xlim(-0.5, 3.5)
        ax1.set_ylim(-0.3, self.total_height + 0.5)
        ax1.set_xlabel('容器宽度 (m)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('高度 (m)', fontsize=12, fontweight='bold')
        ax1.set_title('多层液体分层示意图', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 右图：压强分布曲线
        ax2 = axes[1]
        
        # 计算各点压强
        z_points = []
        p_points = []
        
        for i, layer in enumerate(self.layers):
            if i == 0:
                z_start = 0
            else:
                z_start = self.interface_depths[i]
            
            z_end = self.interface_depths[i+1]
            
            # 在每层内部取多个点
            z_layer = np.linspace(z_start, z_end, 20)
            for z in z_layer:
                z_points.append(z)
                p_points.append(self.pressure_at_depth(z))
        
        z_array = np.array(z_points)
        p_array = np.array(p_points) / 1000  # 转换为kPa
        
        # 绘制压强分布曲线
        ax2.plot(p_array, z_array, 'b-', linewidth=2.5, label='压强分布')
        ax2.fill_betweenx(z_array, 0, p_array, alpha=0.3, color='blue')
        
        # 标注各界面压强
        interface_pressures = self.interface_pressures()
        for i, (depth, pressure) in enumerate(zip(self.interface_depths, interface_pressures)):
            p_kpa = pressure / 1000
            ax2.plot(p_kpa, depth, 'ro', markersize=10)
            
            if i == 0:
                label = f'顶部\np={p_kpa:.2f}kPa'
            elif i == len(self.interface_depths) - 1:
                label = f'底部\np={p_kpa:.2f}kPa'
            else:
                label = f'界面{i}\np={p_kpa:.2f}kPa'
            
            ax2.text(p_kpa + 5, depth, label, fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # 标注各层
        for i, layer in enumerate(self.layers):
            z_mid = (self.interface_depths[i] + self.interface_depths[i+1]) / 2
            ax2.text(5, z_mid, layer['name'], fontsize=11, fontweight='bold',
                    rotation=0, ha='left', va='center',
                    bbox=dict(boxstyle='round', facecolor=layer['color'], alpha=0.5))
        
        ax2.set_xlabel('压强 (kPa)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('深度 z (m)', fontsize=12, fontweight='bold')
        ax2.set_title('压强沿深度分布', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("多层液体压强计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  顶部气压 p0 = {self.p0} Pa = {self.p0/101325:.4f} atm")
        print(f"  重力加速度 g = {self.g} m/s²")
        print(f"  液体层数 = {len(self.layers)}")
        
        print(f"\n液体层参数：")
        for i, layer in enumerate(self.layers, 1):
            print(f"  第{i}层（{layer['name']}）:")
            print(f"    高度 h{i} = {layer['h']} m")
            print(f"    密度 ρ{i} = {layer['rho']} kg/m³")
        
        print(f"  总高度 H = {self.total_height} m")
        
        print(f"\n压强计算：")
        print(f"  基本公式：p = p0 + Σ(ρi·g·hi)")
        
        # 逐层计算
        p_cumulative = self.p0
        print(f"\n  从顶部开始逐层计算：")
        print(f"  顶部（z=0）: p = {self.p0:.2f} Pa = {self.p0/1000:.2f} kPa")
        
        for i, layer in enumerate(self.layers, 1):
            dp = layer['rho'] * self.g * layer['h']
            p_cumulative += dp
            depth = self.interface_depths[i]
            print(f"  第{i}层底部（z={depth}m）:")
            print(f"    增加 Δp{i} = ρ{i}×g×h{i} = {layer['rho']}×{self.g}×{layer['h']}")
            print(f"           = {dp:.2f} Pa = {dp/1000:.2f} kPa")
            print(f"    累计 p = {p_cumulative:.2f} Pa = {p_cumulative/1000:.2f} kPa")
        
        p_bottom = self.bottom_pressure()
        print(f"\n容器底部压强：")
        print(f"  p_底 = {p_bottom:.2f} Pa")
        print(f"       = {p_bottom/1000:.2f} kPa")
        print(f"       = {p_bottom/101325:.4f} atm")
        
        # 与单一液体对比
        print(f"\n对比分析：")
        print(f"  如果全部是水（ρ=1000 kg/m³）:")
        p_water_only = self.p0 + 1000 * self.g * self.total_height
        print(f"    p = {p_water_only:.2f} Pa = {p_water_only/1000:.2f} kPa")
        print(f"    差值 = {abs(p_bottom - p_water_only):.2f} Pa = {abs(p_bottom - p_water_only)/1000:.2f} kPa")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 多层液体压强叠加：p = p0 + Σ(ρi·g·hi)")
        print("2. 界面处压强连续，但密度突变")
        print("3. 压强梯度在不同层不同：dp/dz = ρi·g")
        print("4. 密度大的层（如水银）对底部压强贡献大")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "🌈" * 35)
    print("第01章 静水力学 - 题目10：多层液体压强")
    print("🌈" * 35 + "\n")
    
    # 定义三层液体（从上到下）
    layers = [
        {'name': '油', 'h': 0.5, 'rho': 800, 'color': 'yellow'},
        {'name': '水', 'h': 1.0, 'rho': 1000, 'color': 'cyan'},
        {'name': '水银', 'h': 0.2, 'rho': 13600, 'color': 'silver'}
    ]
    
    # 创建多层液体对象
    fluid = MultilayerFluid(layers=layers)
    
    # 打印结果
    fluid.print_results()
    
    # 绘图
    print("\n正在绘制多层液体系统示意图...")
    fluid.plot_multilayer_system()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
