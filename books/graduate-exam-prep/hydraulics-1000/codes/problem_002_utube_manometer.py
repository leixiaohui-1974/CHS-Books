"""
《水力学1000题详解》- 题目002: U型测压管读数
===============================================

知识点：U型测压管原理、测压管高度、正压与负压
难度：⭐ 基础题

功能：
1. 计算不同类型测压管的读数
2. 对比U型管与倒U型管
3. 可视化测压管工作原理
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
import matplotlib as mpl

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False


class UtubeManometer:
    """U型测压管类"""
    
    def __init__(self, h1, z_A, gamma=9800):
        """
        初始化测压管参数
        
        参数:
            h1: 测压管水柱高度 (m)
            z_A: A点高程 (m)
            gamma: 水的容重 (N/m³)
        """
        self.h1 = h1
        self.z_A = z_A
        self.gamma = gamma
        self.p_atm = 101.325  # 标准大气压 (kPa)
    
    def pressure_at_A(self, absolute=False):
        """
        计算A点压强（正压，普通U型管）
        
        参数:
            absolute: 是否返回绝对压强
        
        返回:
            压强 (kPa)
        """
        # 相对压强
        p_relative = self.gamma * self.h1 / 1000
        
        if absolute:
            return self.p_atm + p_relative
        else:
            return p_relative
    
    def pressure_inverted_utube(self, h2):
        """
        计算倒U型管的压强（负压）
        
        参数:
            h2: 气柱高度 (m)
        
        返回:
            绝对压强 (kPa)
        """
        # 倒U型管测量负压
        p_absolute = self.p_atm - self.gamma * h2 / 1000
        return p_absolute
    
    def plot_utube_comparison(self, h2=0.5, save_path=None):
        """
        绘制U型管与倒U型管对比图
        
        参数:
            h2: 倒U型管气柱高度 (m)
            save_path: 保存路径
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
        
        # ===== 左图：普通U型管（正压） =====
        ax1.set_xlim(-1, 3)
        ax1.set_ylim(-0.5, 3)
        ax1.set_aspect('equal')
        
        # 管道（水平管）
        pipe_y = self.z_A
        ax1.plot([-0.5, 1], [pipe_y, pipe_y], 'k-', linewidth=8, label='管道')
        ax1.plot(0.5, pipe_y, 'ro', markersize=15, label='A点')
        
        # U型管（垂直管）
        utube_x = 1
        utube_bottom = pipe_y - 0.3
        utube_top = pipe_y + self.h1
        
        # U型管管壁
        ax1.plot([utube_x - 0.1, utube_x - 0.1], [utube_bottom, utube_top], 
                 'k-', linewidth=3)
        ax1.plot([utube_x + 0.1, utube_x + 0.1], [utube_bottom, utube_top], 
                 'k-', linewidth=3)
        ax1.plot([utube_x - 0.1, utube_x + 0.1], [utube_bottom, utube_bottom], 
                 'k-', linewidth=3)
        
        # U型管内水柱
        water_rect = Rectangle((utube_x - 0.08, pipe_y), 0.16, self.h1,
                                facecolor='lightblue', edgecolor='blue', 
                                linewidth=2, label='水柱')
        ax1.add_patch(water_rect)
        
        # 水柱高度标注
        ax1.plot([utube_x + 0.3, utube_x + 0.6], 
                 [pipe_y, pipe_y], 'r--', linewidth=1.5)
        ax1.plot([utube_x + 0.3, utube_x + 0.6], 
                 [utube_top, utube_top], 'r--', linewidth=1.5)
        ax1.annotate('', xy=(utube_x + 0.5, utube_top), 
                     xytext=(utube_x + 0.5, pipe_y),
                     arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(utube_x + 0.8, (pipe_y + utube_top) / 2, 
                 f'h₁ = {self.h1} m', fontsize=12, 
                 fontweight='bold', color='red')
        
        # 基准线
        ax1.axhline(y=0, color='brown', linestyle='--', 
                    linewidth=1.5, alpha=0.5, label='基准面')
        
        # A点高程标注
        ax1.plot([utube_x - 0.5, utube_x - 0.8], [0, 0], 'g--', linewidth=1.5)
        ax1.plot([utube_x - 0.5, utube_x - 0.8], [pipe_y, pipe_y], 'g--', linewidth=1.5)
        ax1.annotate('', xy=(utube_x - 0.65, pipe_y), 
                     xytext=(utube_x - 0.65, 0),
                     arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax1.text(utube_x - 1.1, pipe_y / 2, f'z_A = {self.z_A} m', 
                 fontsize=11, fontweight='bold', color='green')
        
        # 压强值标注
        p_A = self.pressure_at_A(absolute=False)
        p_A_abs = self.pressure_at_A(absolute=True)
        
        textstr = f'A点压强:\n相对: {p_A:.2f} kPa\n绝对: {p_A_abs:.2f} kPa'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax1.text(1.5, 2.3, textstr, fontsize=11, 
                 verticalalignment='top', bbox=props, fontweight='bold')
        
        ax1.set_xlabel('水平位置 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('普通U型测压管（测正压）', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # ===== 右图：倒U型管（负压） =====
        ax2.set_xlim(-1, 3)
        ax2.set_ylim(-0.5, 3)
        ax2.set_aspect('equal')
        
        # 管道
        ax2.plot([-0.5, 1], [pipe_y, pipe_y], 'k-', linewidth=8, label='管道')
        ax2.plot(0.5, pipe_y, 'ro', markersize=15, label='A点')
        
        # 倒U型管
        utube_top_inv = pipe_y + 1.2
        utube_water_top = utube_top_inv - h2
        
        # 倒U型管管壁
        ax2.plot([utube_x - 0.1, utube_x - 0.1], [pipe_y, utube_top_inv], 
                 'k-', linewidth=3)
        ax2.plot([utube_x + 0.1, utube_x + 0.1], [pipe_y, utube_top_inv], 
                 'k-', linewidth=3)
        ax2.plot([utube_x - 0.1, utube_x + 0.1], [utube_top_inv, utube_top_inv], 
                 'k-', linewidth=3)
        
        # 倒U型管内水柱（顶部有气体）
        water_rect_inv = Rectangle((utube_x - 0.08, pipe_y), 
                                    0.16, utube_water_top - pipe_y,
                                    facecolor='lightblue', edgecolor='blue', 
                                    linewidth=2, label='水柱')
        ax2.add_patch(water_rect_inv)
        
        # 气柱
        air_rect = Rectangle((utube_x - 0.08, utube_water_top), 
                              0.16, h2,
                              facecolor='lightyellow', edgecolor='orange', 
                              linewidth=2, label='气柱')
        ax2.add_patch(air_rect)
        
        # 气柱高度标注
        ax2.plot([utube_x + 0.3, utube_x + 0.6], 
                 [utube_water_top, utube_water_top], 'r--', linewidth=1.5)
        ax2.plot([utube_x + 0.3, utube_x + 0.6], 
                 [utube_top_inv, utube_top_inv], 'r--', linewidth=1.5)
        ax2.annotate('', xy=(utube_x + 0.5, utube_top_inv), 
                     xytext=(utube_x + 0.5, utube_water_top),
                     arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax2.text(utube_x + 0.8, (utube_water_top + utube_top_inv) / 2, 
                 f'h₂ = {h2} m', fontsize=12, 
                 fontweight='bold', color='red')
        
        # 基准线
        ax2.axhline(y=0, color='brown', linestyle='--', 
                    linewidth=1.5, alpha=0.5, label='基准面')
        
        # 压强值标注
        p_A_inv = self.pressure_inverted_utube(h2)
        vacuum_degree = self.p_atm - p_A_inv
        
        textstr_inv = f'A点压强:\n绝对: {p_A_inv:.2f} kPa\n真空度: {vacuum_degree:.2f} kPa'
        props_inv = dict(boxstyle='round', facecolor='lightcyan', alpha=0.8)
        ax2.text(1.5, 2.3, textstr_inv, fontsize=11, 
                 verticalalignment='top', bbox=props_inv, fontweight='bold')
        
        ax2.set_xlabel('水平位置 (m)', fontsize=12)
        ax2.set_ylabel('高程 (m)', fontsize=12)
        ax2.set_title('倒U型测压管（测负压）', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper left', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        
        plt.show()
    
    def print_results(self, h2=0.5):
        """打印计算结果"""
        print("=" * 60)
        print("题目002: U型测压管读数 - 计算结果")
        print("=" * 60)
        
        print(f"\n【题目参数】")
        print(f"  测压管水柱高度: h₁ = {self.h1} m")
        print(f"  A点高程: z_A = {self.z_A} m")
        print(f"  水的容重: γ = {self.gamma} N/m³")
        print(f"  标准大气压: p_atm = {self.p_atm} kPa")
        
        print(f"\n【计算结果】")
        
        # （1）普通U型管：A点相对压强
        p_A_rel = self.pressure_at_A(absolute=False)
        print(f"\n（1）A点的相对压强（普通U型管）:")
        print(f"     p_A = γh₁ = {self.gamma} × {self.h1}")
        print(f"         = {p_A_rel * 1000:.0f} Pa = {p_A_rel:.2f} kPa")
        
        # （2）A点绝对压强
        p_A_abs = self.pressure_at_A(absolute=True)
        print(f"\n（2）A点的绝对压强:")
        print(f"     p_A(绝对) = p_atm + p_A(相对)")
        print(f"               = {self.p_atm} + {p_A_rel:.2f}")
        print(f"               = {p_A_abs:.3f} kPa")
        
        # （3）倒U型管：负压
        p_A_inv = self.pressure_inverted_utube(h2)
        vacuum = self.p_atm - p_A_inv
        
        print(f"\n（3）倒U型管测量（气柱高度h₂ = {h2} m）:")
        print(f"     p_A = p_atm - γh₂")
        print(f"         = {self.p_atm} - {self.gamma * h2 / 1000:.2f}")
        print(f"         = {p_A_inv:.3f} kPa")
        print(f"     真空度 = {vacuum:.2f} kPa")
        print(f"     注：p_A < p_atm，为负压（真空）")
        
        print("\n" + "=" * 60)


def main():
    """主程序"""
    
    print("\n" + "="*60)
    print("《水力学1000题详解》- 题目002")
    print("U型测压管读数")
    print("="*60 + "\n")
    
    # 创建测压管实例
    manometer = UtubeManometer(
        h1=1.2,    # 测压管水柱高度 (m)
        z_A=0.8,   # A点高程 (m)
        gamma=9800 # 水的容重 (N/m³)
    )
    
    # 打印计算结果
    manometer.print_results(h2=0.5)
    
    # 绘制对比图
    print("\n正在生成U型测压管对比图...")
    manometer.plot_utube_comparison(h2=0.5)
    
    print("\n✅ 题目002 计算完成！\n")


def test_utube_calculation():
    """单元测试"""
    print("\n【单元测试】U型测压管计算验证")
    print("-" * 40)
    
    manometer = UtubeManometer(1.2, 0.8, 9800)
    
    # 测试1：相对压强
    p_rel = manometer.pressure_at_A(absolute=False)
    expected = 11.76
    assert abs(p_rel - expected) < 0.01, f"相对压强计算错误"
    print(f"✓ 测试1通过: 相对压强 = {p_rel:.2f} kPa")
    
    # 测试2：绝对压强
    p_abs = manometer.pressure_at_A(absolute=True)
    expected_abs = 113.085
    assert abs(p_abs - expected_abs) < 0.01, f"绝对压强计算错误"
    print(f"✓ 测试2通过: 绝对压强 = {p_abs:.3f} kPa")
    
    # 测试3：倒U型管
    p_inv = manometer.pressure_inverted_utube(0.5)
    expected_inv = 96.425
    assert abs(p_inv - expected_inv) < 0.01, f"倒U型管压强计算错误"
    print(f"✓ 测试3通过: 倒U型管压强 = {p_inv:.3f} kPa")
    
    print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    # 运行单元测试
    test_utube_calculation()
    
    # 运行主程序
    main()
