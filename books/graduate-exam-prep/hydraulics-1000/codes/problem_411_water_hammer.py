"""
《水力学考研1000题详解》配套代码
题目411：水击（水锤）计算

问题描述：
水平输水管道，已知：
  管长 L = 1000 m
  管径 d = 0.5 m
  壁厚 δ = 10 mm
  初始流速 v₀ = 2.0 m/s
  管道材料：钢管，弹性模量 E_steel = 2.0×10¹¹ Pa
  水的体积弹性模量 K = 2.0×10⁹ Pa
  水的密度 ρ = 1000 kg/m³
  阀门关闭时间 t_c = 3.0 s

要求：
(1) 计算水击波传播速度c
(2) 判断水击类型（直接水击或间接水击）
(3) 计算水击压强增量ΔH
(4) 计算阀门处最大压强
(5) 分析水击过程的四个阶段
(6) 讨论水击防护措施

考点：
1. 水击波速公式：c = √(K/ρ) / √(1 + (K/E)(d/δ))
2. 相位时间：T = 2L/c
3. 直接水击：t_c ≤ T（最危险）
4. 间接水击：t_c > T（较缓和）
5. Joukowsky公式：ΔH = (c·Δv)/g
6. 最大压强：H_max = H₀ + ΔH

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WaterHammer:
    """水击计算类"""
    
    def __init__(self, L=1000, d=0.5, delta=0.01, v0=2.0, 
                 E_steel=2e11, K=2e9, rho=1000, t_c=3.0, H0=50):
        """
        初始化
        
        参数:
            L: 管长 (m)
            d: 管径 (m)
            delta: 壁厚 (m)
            v0: 初始流速 (m/s)
            E_steel: 钢管弹性模量 (Pa)
            K: 水的体积弹性模量 (Pa)
            rho: 水的密度 (kg/m³)
            t_c: 阀门关闭时间 (s)
            H0: 初始水头 (m)
        """
        self.L = L
        self.d = d
        self.delta = delta
        self.v0 = v0
        self.E = E_steel
        self.K = K
        self.rho = rho
        self.t_c = t_c
        self.H0 = H0
        self.g = 9.8
        
        # 计算水击参数
        self.calculate_wave_speed()
        self.classify_water_hammer()
        self.calculate_pressure_rise()
    
    def calculate_wave_speed(self):
        """
        计算水击波传播速度
        考虑管壁弹性的影响
        """
        # 刚性管中的波速（理论最大值）
        c_rigid = np.sqrt(self.K / self.rho)
        
        # 考虑管壁弹性的修正系数
        correction = 1 + (self.K / self.E) * (self.d / self.delta)
        
        # 实际波速
        self.c = c_rigid / np.sqrt(correction)
        
        print(f"\n水击波速计算:")
        print(f"  刚性管波速: c₀ = √(K/ρ) = √({self.K:.2e}/{self.rho}) = {c_rigid:.2f} m/s")
        print(f"  修正系数: 1 + (K/E)(d/δ) = 1 + ({self.K:.2e}/{self.E:.2e})×({self.d}/{self.delta}) = {correction:.6f}")
        print(f"  实际波速: c = {self.c:.2f} m/s")
    
    def classify_water_hammer(self):
        """判断水击类型"""
        # 相位时间（波的往返时间）
        self.T = 2 * self.L / self.c
        
        if self.t_c <= self.T:
            self.hammer_type = "直接水击"
            self.severity = "最危险"
        else:
            self.hammer_type = "间接水击"
            self.severity = "较缓和"
        
        print(f"\n水击类型判别:")
        print(f"  相位时间: T = 2L/c = 2×{self.L}/{self.c:.2f} = {self.T:.3f} s")
        print(f"  关闭时间: t_c = {self.t_c} s")
        print(f"  判别: t_c {'≤' if self.t_c <= self.T else '>'} T")
        print(f"  水击类型: {self.hammer_type}（{self.severity}）")
    
    def calculate_pressure_rise(self):
        """计算水击压强增量"""
        # 流速变化
        delta_v = self.v0  # 完全关闭，Δv = v₀
        
        if self.hammer_type == "直接水击":
            # Joukowsky公式（完整水击）
            self.delta_H = (self.c * delta_v) / self.g
        else:
            # 间接水击（部分水击）
            # 简化计算：ΔH = (c·Δv/g) × (T/t_c)
            self.delta_H = (self.c * delta_v / self.g) * (self.T / self.t_c)
        
        # 最大压强
        self.H_max = self.H0 + self.delta_H
        
        # 最大压力（Pa）
        self.p_max = self.rho * self.g * self.delta_H
        
        print(f"\n水击压强计算:")
        print(f"  流速变化: Δv = v₀ = {delta_v} m/s")
        
        if self.hammer_type == "直接水击":
            print(f"  Joukowsky公式: ΔH = (c·Δv)/g")
            print(f"  水击压强增量: ΔH = ({self.c:.2f}×{delta_v})/{self.g} = {self.delta_H:.2f} m")
        else:
            print(f"  间接水击公式: ΔH = (c·Δv/g)×(T/t_c)")
            print(f"  水击压强增量: ΔH = ({self.c:.2f}×{delta_v}/{self.g})×({self.T:.3f}/{self.t_c}) = {self.delta_H:.2f} m")
        
        print(f"  最大压力: Δp = ρgΔH = {self.p_max/1e6:.3f} MPa")
        print(f"  最大水头: H_max = H₀ + ΔH = {self.H0} + {self.delta_H:.2f} = {self.H_max:.2f} m")
    
    def analyze_phases(self):
        """分析水击过程的四个阶段"""
        print(f"\n水击过程四个阶段:")
        
        print(f"\n第一阶段（0 ~ T/4 = {self.T/4:.3f}s）:")
        print(f"  • 阀门关闭，水击波从阀门向水库传播")
        print(f"  • 阀门处压强增加ΔH，流速降为0")
        print(f"  • 波前：v=v₀, H=H₀；波后：v=0, H=H₀+ΔH")
        
        print(f"\n第二阶段（T/4 ~ T/2 = {self.T/2:.3f}s）:")
        print(f"  • 水击波到达水库并反射")
        print(f"  • 全管压强增加ΔH，流速为0")
        print(f"  • 水库开始向管道倒灌")
        
        print(f"\n第三阶段（T/2 ~ 3T/4 = {3*self.T/4:.3f}s）:")
        print(f"  • 负压波从水库向阀门传播")
        print(f"  • 管内压强降低，流速反向为-v₀")
        print(f"  • 波前：v=0, H=H₀+ΔH；波后：v=-v₀, H=H₀")
        
        print(f"\n第四阶段（3T/4 ~ T = {self.T:.3f}s）:")
        print(f"  • 负压波到达阀门并反射")
        print(f"  • 全管压强恢复H₀，流速降为0")
        print(f"  • 一个周期结束，循环往复")
    
    def protection_measures(self):
        """水击防护措施"""
        print(f"\n水击防护措施:")
        
        print(f"\n1. 延长关闭时间:")
        print(f"   • 使 t_c > T，变直接水击为间接水击")
        print(f"   • 本例需 t_c > {self.T:.3f}s")
        print(f"   • 缺点: 可能不满足操作要求")
        
        print(f"\n2. 设置调压塔（水塔）:")
        print(f"   • 在管道适当位置设置调压塔")
        print(f"   • 吸收压力波动，保护管道")
        print(f"   • 适用于长距离输水")
        
        print(f"\n3. 设置空气罐:")
        print(f"   • 利用空气可压缩性缓冲")
        print(f"   • 适用于泵站出口")
        
        print(f"\n4. 设置安全阀:")
        print(f"   • 压强超过限值时自动开启")
        print(f"   • 释放多余压力")
        
        print(f"\n5. 采用柔性管材:")
        print(f"   • 减小波速c，降低ΔH")
        print(f"   • 如塑料管、橡胶管")
        
        print(f"\n6. 多级关闭:")
        print(f"   • 先快后慢，或先慢后快")
        print(f"   • 减小压力冲击")
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目411：水击（水锤）计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  管长: L = {self.L} m")
        print(f"  管径: d = {self.d} m")
        print(f"  壁厚: δ = {self.delta*1000} mm")
        print(f"  初始流速: v₀ = {self.v0} m/s")
        print(f"  管材弹性模量: E = {self.E:.2e} Pa（钢）")
        print(f"  水的体积弹性模量: K = {self.K:.2e} Pa")
        print(f"  水的密度: ρ = {self.rho} kg/m³")
        print(f"  阀门关闭时间: t_c = {self.t_c} s")
        print(f"  初始水头: H₀ = {self.H0} m")
        
        print("\n【水击基本原理】")
        print("1. 水击现象:")
        print("   管道中流速突然变化引起压强急剧波动")
        
        print("\n2. 水击波速:")
        print("   刚性管: c₀ = √(K/ρ)")
        print("   弹性管: c = c₀/√(1 + (K/E)(d/δ))")
        
        print("\n3. 相位时间:")
        print("   T = 2L/c（水击波往返一次的时间）")
        
        print("\n4. 水击分类:")
        print("   直接水击: t_c ≤ T（完全水击，最危险）")
        print("   间接水击: t_c > T（部分水击，较缓和）")
        
        print("\n5. Joukowsky公式:")
        print("   ΔH = (c·Δv)/g")
        
        print("\n【计算过程】")
        
        # 显示计算结果（已在各方法中打印）
        
        # 分析水击过程
        self.analyze_phases()
        
        # 防护措施
        self.protection_measures()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 水击波速: c = {self.c:.2f} m/s")
        print(f"(2) 水击类型: {self.hammer_type}（t_c {'≤' if self.t_c <= self.T else '>'} T = {self.T:.3f}s）")
        print(f"(3) 水击压强增量: ΔH = {self.delta_H:.2f} m, Δp = {self.p_max/1e6:.3f} MPa")
        print(f"(4) 最大压强: H_max = {self.H_max:.2f} m")
        print(f"(5) 水击过程: 四个阶段，周期T = {self.T:.3f}s，反复波动")
        print(f"(6) 防护措施: 延长关闭时间、设置调压塔、空气罐等")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：水击过程示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_hammer_process(ax1)
        
        # 子图2：压强时程曲线
        ax2 = plt.subplot(2, 2, 2)
        self._plot_pressure_history(ax2)
        
        # 子图3：水击波传播过程
        ax3 = plt.subplot(2, 2, 3)
        self._plot_wave_propagation(ax3)
        
        # 子图4：水击影响因素分析
        ax4 = plt.subplot(2, 2, 4)
        self._plot_parameter_sensitivity(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_hammer_process(self, ax):
        """绘制水击过程示意图"""
        # 绘制管道
        ax.plot([0, self.L], [0, 0], 'b-', linewidth=8, label='管道')
        
        # 水库
        reservoir = Rectangle((-100, -50), 100, 100, 
                             facecolor='lightblue', edgecolor='blue', linewidth=2)
        ax.add_patch(reservoir)
        ax.text(-50, 0, '水库', ha='center', va='center', fontsize=12, weight='bold')
        
        # 阀门
        valve_x = self.L
        valve_y = 0
        ax.plot([valve_x, valve_x], [-30, 30], 'r-', linewidth=5)
        ax.plot([valve_x-10, valve_x], [0, 30], 'r-', linewidth=3)
        ax.plot([valve_x-10, valve_x], [0, -30], 'r-', linewidth=3)
        ax.text(valve_x, -50, '阀门', ha='center', fontsize=12, weight='bold', color='red')
        
        # 标注管长
        ax.annotate('', xy=(self.L, 30), xytext=(0, 30),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        ax.text(self.L/2, 40, f'L = {self.L}m', ha='center', fontsize=11)
        
        # 标注初始流速
        arrow = FancyArrowPatch((self.L/4, 0), (self.L/4 + 100, 0),
                               arrowstyle='->', mutation_scale=30, 
                               color='green', linewidth=3)
        ax.add_patch(arrow)
        ax.text(self.L/4 + 50, 15, f'v₀={self.v0}m/s', fontsize=11, color='green', weight='bold')
        
        # 标注水击波
        wave_x = self.L - 300
        for i in range(3):
            circle = Circle((wave_x - i*80, 0), 20, facecolor='red', 
                          edgecolor='darkred', linewidth=2, alpha=0.7)
            ax.add_patch(circle)
        ax.text(wave_x, -70, f'水击波\nc={self.c:.0f}m/s', 
               ha='center', fontsize=10, weight='bold', color='red')
        
        ax.set_xlim(-150, self.L + 100)
        ax.set_ylim(-100, 80)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('水击过程示意图', fontsize=13, weight='bold')
    
    def _plot_pressure_history(self, ax):
        """绘制压强时程曲线"""
        # 模拟多个周期
        n_cycles = 3
        t = np.linspace(0, n_cycles * self.T, 1000)
        
        # 阀门处压强变化（简化为方波）
        H = np.zeros_like(t)
        for i, ti in enumerate(t):
            cycle_time = ti % self.T
            if cycle_time < self.T/2:
                H[i] = self.H0 + self.delta_H
            else:
                H[i] = self.H0
        
        ax.plot(t, H, 'b-', linewidth=2.5, label='阀门处压强')
        
        # 标注关键值
        ax.axhline(self.H0, color='green', linestyle='--', linewidth=2, 
                  label=f'初始水头 H₀={self.H0}m')
        ax.axhline(self.H_max, color='red', linestyle='--', linewidth=2, 
                  label=f'最大水头 H_max={self.H_max:.1f}m')
        
        # 标注周期
        for i in range(n_cycles + 1):
            ax.axvline(i * self.T, color='gray', linestyle=':', alpha=0.5)
            if i < n_cycles:
                ax.text(i * self.T + self.T/2, self.H0 - 5, f'T={self.T:.2f}s',
                       ha='center', fontsize=9, bbox=dict(boxstyle='round', 
                       facecolor='yellow', alpha=0.5))
        
        ax.set_xlabel('时间 t (s)', fontsize=12)
        ax.set_ylabel('水头 H (m)', fontsize=12)
        ax.set_title('阀门处压强时程曲线', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_wave_propagation(self, ax):
        """绘制水击波传播过程"""
        # 四个关键时刻
        times = [0, self.T/4, self.T/2, 3*self.T/4]
        labels = ['t=0\n阀门关闭', f't=T/4\n波到水库', f't=T/2\n反射波', f't=3T/4\n波到阀门']
        colors = ['red', 'orange', 'blue', 'purple']
        
        for i, (t, label, color) in enumerate(zip(times, labels, colors)):
            y = -i * 0.25
            
            # 管道
            ax.plot([0, 1], [y, y], 'k-', linewidth=3)
            
            # 水库和阀门
            ax.plot([0, 0], [y-0.02, y+0.02], 'b-', linewidth=6)
            ax.plot([1, 1], [y-0.02, y+0.02], 'r-', linewidth=6)
            
            # 波的位置
            if i == 0:
                wave_pos = 1.0  # 阀门处
            elif i == 1:
                wave_pos = 0.0  # 到达水库
            elif i == 2:
                wave_pos = 0.0  # 开始反射
            else:
                wave_pos = 1.0  # 返回阀门
            
            # 绘制压强分布
            if i == 0:
                ax.fill_between([0.8, 1], [y, y], [y+0.05, y+0.05], 
                              alpha=0.5, color=color)
            elif i == 1:
                ax.fill_between([0, 1], [y, y], [y+0.05, y+0.05], 
                              alpha=0.5, color=color)
            elif i == 2:
                ax.fill_between([0, 1], [y, y], [y+0.05, y+0.05], 
                              alpha=0.5, color=color)
            else:
                ax.fill_between([0, 0.2], [y, y], [y+0.05, y+0.05], 
                              alpha=0.5, color=color)
            
            # 标签
            ax.text(1.05, y, label, fontsize=9, va='center')
        
        ax.set_xlim(-0.1, 1.3)
        ax.set_ylim(-0.9, 0.15)
        ax.axis('off')
        ax.set_title('水击波传播四阶段', fontsize=13, weight='bold')
    
    def _plot_parameter_sensitivity(self, ax):
        """绘制参数敏感性分析"""
        # 分析不同流速下的水击压强
        v_range = np.linspace(0.5, 4, 20)
        delta_H_array = (self.c * v_range) / self.g
        
        ax.plot(v_range, delta_H_array, 'b-o', linewidth=2.5, markersize=6)
        
        # 标注当前工况
        ax.plot(self.v0, self.delta_H, 'ro', markersize=12, 
               label=f'当前工况\nv₀={self.v0}m/s\nΔH={self.delta_H:.1f}m')
        
        ax.set_xlabel('流速 v (m/s)', fontsize=12)
        ax.set_ylabel('水击压强增量 ΔH (m)', fontsize=12)
        ax.set_title('水击压强与流速关系（ΔH = cv/g）', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 添加说明文本
        ax.text(0.95, 0.3, f'水击波速: c={self.c:.0f}m/s\n'
                            f'相位时间: T={self.T:.2f}s\n'
                            f'关闭时间: t_c={self.t_c}s\n'
                            f'水击类型: {self.hammer_type}',
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))


def test_problem_411():
    """测试题目411"""
    print("\n" + "="*80)
    print("开始水击（水锤）计算...")
    print("="*80)
    
    # 创建水击分析对象
    hammer = WaterHammer(L=1000, d=0.5, delta=0.01, v0=2.0,
                        E_steel=2e11, K=2e9, rho=1000, t_c=3.0, H0=50)
    
    # 打印结果
    hammer.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = hammer.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_411_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_411_result.png")
    
    # 验证
    assert hammer.c > 0, "波速必须为正"
    assert hammer.delta_H > 0, "水击压强增量必须为正"
    assert hammer.T > 0, "相位时间必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水击是管道瞬变流的重要现象！")
    print("• 水击波速: c = c₀/√(1+(K/E)(d/δ))")
    print("• Joukowsky公式: ΔH = c·Δv/g")
    print("• 直接水击(t_c≤T): 最危险")
    print("• 防护: 延长关闭时间、调压塔、安全阀")
    print("• 应用: 长距离输水、泵站设计、管道安全")


if __name__ == "__main__":
    test_problem_411()
