"""
《水力学考研1000题详解》配套代码
题目146：毕托管测速

问题描述：
用毕托管测量管道中心流速。水银压差计读数Δh=15cm。
水的密度ρ=1000kg/m³，水银密度ρ_Hg=13600kg/m³。
求：(1) 管道中心流速v
    (2) 若为空气流动（ρ_air=1.2kg/m³），求流速
    (3) 绘制毕托管原理图和压强分布

考点：
1. 伯努利方程：p₁ + ½ρv₁² = p₂ + ½ρv₂²
2. 毕托管原理：滞止点v₂=0，p₂为总压
3. 静压和动压：p_total = p_static + p_dynamic
4. 压差计：Δp = (ρ_Hg - ρ)gΔh
5. 流速公式：v = √(2Δp/ρ)

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow, Polygon, FancyBboxPatch, Arc
from matplotlib.patches import FancyArrowPatch
import matplotlib.lines as mlines

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PitotTube:
    """毕托管测速计算类"""
    
    def __init__(self, delta_h, rho_fluid=1000, rho_Hg=13600, g=9.8):
        """
        初始化
        
        参数:
            delta_h: 压差计读数 (m)
            rho_fluid: 流体密度 (kg/m³)
            rho_Hg: 水银密度 (kg/m³)
            g: 重力加速度 (m/s²)
        """
        self.delta_h = delta_h
        self.rho_fluid = rho_fluid
        self.rho_Hg = rho_Hg
        self.g = g
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算流速"""
        # 1. 压差计算
        self.delta_p = (self.rho_Hg - self.rho_fluid) * self.g * self.delta_h
        
        # 2. 流速计算（伯努利方程）
        # p₁ + ½ρv₁² = p₂ + ½ρv₂²
        # 其中v₂=0（滞止点），p₂-p₁=Δp
        # Δp = ½ρv₁²
        # v₁ = √(2Δp/ρ)
        self.v = np.sqrt(2 * self.delta_p / self.rho_fluid)
        
        # 3. 动压和静压
        self.p_dynamic = 0.5 * self.rho_fluid * self.v**2
        self.p_static = 0  # 参考点
        self.p_total = self.p_static + self.p_dynamic
        
        # 4. 雷诺数（假设管径d=0.1m，运动粘度ν=1e-6）
        d_assumed = 0.1
        nu = 1e-6
        self.Re = self.v * d_assumed / nu
        
        # 5. 对于空气的计算
        rho_air = 1.2
        delta_p_air = (self.rho_Hg - rho_air) * self.g * self.delta_h
        self.v_air = np.sqrt(2 * delta_p_air / rho_air)
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*80)
        print("题目146：毕托管测速")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"压差计读数: Δh = {self.delta_h} m = {self.delta_h*100} cm")
        print(f"流体密度: ρ = {self.rho_fluid} kg/m³ (水)")
        print(f"水银密度: ρ_Hg = {self.rho_Hg} kg/m³")
        print(f"重力加速度: g = {self.g} m/s²")
        
        print("\n【毕托管原理】")
        print("毕托管是测量流速的经典仪器，由两个测压孔组成：")
        print("  • 静压孔：测量静压p_s（与流速方向平行）")
        print("  • 总压孔：测量总压p_t（正对流速方向，滞止点）")
        print("\n在滞止点：流速v₂=0，动能完全转化为压能")
        print("伯努利方程：p_s + ½ρv² = p_t")
        print("动压：p_d = p_t - p_s = ½ρv²")
        print("流速：v = √(2·p_d/ρ)")
        
        print("\n【计算过程】")
        
        print("\n步骤1：根据压差计读数计算压差")
        print("压差计平衡方程：")
        print(f"Δp = (ρ_Hg - ρ)g·Δh")
        print(f"   = ({self.rho_Hg} - {self.rho_fluid}) × {self.g} × {self.delta_h}")
        print(f"   = {self.rho_Hg - self.rho_fluid} × {self.g} × {self.delta_h}")
        print(f"   = {self.delta_p:.2f} Pa")
        print(f"   = {self.delta_p/1000:.3f} kPa")
        
        print("\n步骤2：应用伯努利方程计算流速")
        print("从静压孔到总压孔（滞止点）：")
        print("p_s + ½ρv² = p_t + 0")
        print("Δp = p_t - p_s = ½ρv²")
        print(f"v = √(2Δp/ρ)")
        print(f"  = √(2 × {self.delta_p:.2f} / {self.rho_fluid})")
        print(f"  = √({2*self.delta_p:.2f} / {self.rho_fluid})")
        print(f"  = √{2*self.delta_p/self.rho_fluid:.4f}")
        print(f"  = {self.v:.4f} m/s")
        
        print("\n步骤3：压强组成分析")
        print(f"静压: p_s = {self.p_static:.2f} Pa (参考点)")
        print(f"动压: p_d = ½ρv² = 0.5×{self.rho_fluid}×{self.v:.4f}²")
        print(f"         = {self.p_dynamic:.2f} Pa = {self.p_dynamic/1000:.3f} kPa")
        print(f"总压: p_t = p_s + p_d = {self.p_total:.2f} Pa")
        print(f"验证: Δp = p_d = {self.p_dynamic:.2f} Pa ✓")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 水流速度: v = {self.v:.4f} m/s = {self.v*3.6:.2f} km/h")
        print(f"    动压: p_d = {self.p_dynamic:.2f} Pa = {self.p_dynamic/1000:.3f} kPa")
        print("="*80)
        
        print("\n【空气流速计算】")
        print(f"若为空气流动（ρ_air = 1.2 kg/m³）：")
        delta_p_air = (self.rho_Hg - 1.2) * self.g * self.delta_h
        print(f"Δp_air = (ρ_Hg - ρ_air)g·Δh")
        print(f"       = ({self.rho_Hg} - 1.2) × {self.g} × {self.delta_h}")
        print(f"       = {delta_p_air:.2f} Pa")
        print(f"v_air = √(2Δp_air/ρ_air)")
        print(f"      = √(2 × {delta_p_air:.2f} / 1.2)")
        print(f"      = {self.v_air:.4f} m/s = {self.v_air*3.6:.2f} km/h")
        print(f"\n(2) 空气流速: v_air = {self.v_air:.4f} m/s = {self.v_air*3.6:.2f} km/h")
        
        print("\n【对比分析】")
        print(f"水流速度: v_water = {self.v:.4f} m/s")
        print(f"空气流速: v_air = {self.v_air:.4f} m/s")
        print(f"速度比: v_air/v_water = {self.v_air/self.v:.2f}")
        print(f"说明: 相同压差下，密度越小，流速越大")
        
        print("\n【核心公式】")
        print("压差计: Δp = (ρ_Hg - ρ)g·Δh")
        print("伯努利: p + ½ρv² = 常数")
        print("毕托管: v = √(2Δp/ρ)")
        print("总压: p_t = p_s + ½ρv² (滞止压强)")
        
        print("\n【应用范围】")
        print("✓ 管道流速测量")
        print("✓ 飞机空速测量")
        print("✓ 风速测量")
        print("✓ 实验室流速标定")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：毕托管原理
        ax1 = plt.subplot(2, 2, 1)
        self._plot_pitot_principle(ax1)
        
        # 子图2：压差计示意图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_manometer(ax2)
        
        # 子图3：压强分布
        ax3 = plt.subplot(2, 2, 3)
        self._plot_pressure_distribution(ax3)
        
        # 子图4：流速-压差关系
        ax4 = plt.subplot(2, 2, 4)
        self._plot_velocity_pressure(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_pitot_principle(self, ax):
        """绘制毕托管原理图"""
        # 管道
        pipe = Rectangle((0, 0.3), 2, 0.4, facecolor='lightgray',
                        edgecolor='black', linewidth=2, alpha=0.5)
        ax.add_patch(pipe)
        
        # 流动方向
        for i in range(5):
            x = 0.2 + i*0.3
            ax.arrow(x, 0.5, 0.15, 0, head_width=0.06, head_length=0.05,
                    fc='blue', ec='blue', linewidth=1.5)
        ax.text(1, 0.85, f'v={self.v:.2f}m/s  →', fontsize=11, 
               color='blue', weight='bold')
        
        # 毕托管
        # 静压孔（侧面）
        static_x, static_y = 1.5, 0.3
        ax.plot([static_x, static_x], [static_y, static_y-0.3], 'k-', linewidth=2)
        ax.plot([static_x], [static_y], 'ko', markersize=6)
        ax.text(static_x-0.1, static_y-0.4, '静压孔\np_s', fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 总压孔（正对）
        total_x, total_y = 1.3, 0.5
        # L型管
        ax.plot([total_x-0.2, total_x], [total_y, total_y], 'k-', linewidth=2)
        ax.plot([total_x, total_x], [total_y, total_y+0.3], 'k-', linewidth=2)
        # 滞止点
        ax.plot([total_x], [total_y], 'ro', markersize=8)
        ax.text(total_x, total_y+0.4, '总压孔\np_t', fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        # 滞止区示意
        circle = Circle((total_x, total_y), 0.08, facecolor='red', 
                       edgecolor='red', alpha=0.3)
        ax.add_patch(circle)
        ax.text(total_x-0.25, total_y, 'v=0', fontsize=8, color='red')
        
        # 压强标注
        ax.annotate('', xy=(static_x, static_y-0.15), xytext=(total_x, total_y+0.15),
                   arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax.text(1.4, 0.25, f'Δp={self.delta_p/1000:.2f}kPa',
               fontsize=10, color='green', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlim(0, 2)
        ax.set_ylim(-0.5, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('毕托管原理图', fontsize=13, weight='bold')
    
    def _plot_manometer(self, ax):
        """绘制压差计示意图"""
        # U型管
        u_tube_x = [0.5, 0.5, 1.5, 1.5]
        u_tube_y = [1.0, 0, 0, 1.0]
        ax.plot(u_tube_x, u_tube_y, 'k-', linewidth=3)
        
        # 水（上部）
        water_left = Rectangle((0.5, 0.5), 0.03, 0.5, facecolor='lightblue',
                              edgecolor='blue', linewidth=1)
        water_right = Rectangle((1.47, 0.5+self.delta_h), 0.03, 0.5-self.delta_h,
                               facecolor='lightblue', edgecolor='blue', linewidth=1)
        ax.add_patch(water_left)
        ax.add_patch(water_right)
        
        # 水银（下部）
        hg_height = 0.3
        mercury = Polygon([(0.5, 0), (0.5, hg_height), (1.5, hg_height+self.delta_h), 
                          (1.5, 0)], facecolor='gray', edgecolor='black', linewidth=2)
        ax.add_patch(mercury)
        
        # 水银液面
        ax.plot([0.5, 0.7], [hg_height, hg_height], 'r-', linewidth=2)
        ax.plot([1.3, 1.5], [hg_height+self.delta_h, hg_height+self.delta_h], 
               'r-', linewidth=2)
        
        # 标注
        ax.text(0.3, 0.75, '水', fontsize=10, color='blue')
        ax.text(1, 0.1, '水银', fontsize=10, color='gray')
        
        # Δh标注
        ax.annotate('', xy=(1.7, hg_height+self.delta_h), xytext=(1.7, hg_height),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(1.85, hg_height+self.delta_h/2, f'Δh={self.delta_h*100:.0f}cm',
               fontsize=11, color='red', weight='bold', rotation=90, va='center')
        
        # 连接管道
        ax.plot([0.5, 0.5], [1.0, 1.3], 'k--', linewidth=1)
        ax.plot([1.5, 1.5], [1.0, 1.3], 'k--', linewidth=1)
        ax.text(0.5, 1.35, '→p_s', fontsize=9, ha='center')
        ax.text(1.5, 1.35, '→p_t', fontsize=9, ha='center')
        
        # 公式
        ax.text(1, -0.2, f'Δp=(ρ_Hg-ρ)g·Δh\n={self.delta_p:.0f}Pa',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax.set_xlim(0, 2.2)
        ax.set_ylim(-0.3, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('U型水银压差计', fontsize=13, weight='bold')
    
    def _plot_pressure_distribution(self, ax):
        """绘制压强分布"""
        categories = ['静压\np_s', '动压\np_d', '总压\np_t']
        values = [0, self.p_dynamic/1000, self.p_total/1000]  # 转换为kPa
        colors = ['lightblue', 'lightcoral', 'lightgreen']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2, height,
                       f'{val:.3f}\nkPa',
                       ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 压强关系
        ax.plot([0.5, 2.5], [self.p_total/1000, self.p_total/1000],
               'g--', linewidth=2, label='p_t = p_s + p_d')
        
        # 公式标注
        ax.text(1, self.p_dynamic/2000, 
               f'½ρv²\n=½×{self.rho_fluid}×{self.v:.2f}²',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        ax.set_ylabel('压强 (kPa)', fontsize=12)
        ax.set_title('压强组成分析', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, max(values)*1.3)
    
    def _plot_velocity_pressure(self, ax):
        """绘制流速-压差关系"""
        # 压差范围
        delta_h_range = np.linspace(0.01, 0.5, 100)
        delta_p_range = (self.rho_Hg - self.rho_fluid) * self.g * delta_h_range
        v_range = np.sqrt(2 * delta_p_range / self.rho_fluid)
        
        # 绘制曲线
        ax.plot(delta_h_range*100, v_range, 'b-', linewidth=2.5,
               label=f'水 (ρ={self.rho_fluid}kg/m³)')
        
        # 空气的曲线
        delta_p_air_range = (self.rho_Hg - 1.2) * self.g * delta_h_range
        v_air_range = np.sqrt(2 * delta_p_air_range / 1.2)
        ax.plot(delta_h_range*100, v_air_range, 'r--', linewidth=2,
               label='空气 (ρ=1.2kg/m³)')
        
        # 标注本题的点
        ax.plot(self.delta_h*100, self.v, 'bo', markersize=12, zorder=5)
        ax.text(self.delta_h*100, self.v*1.1,
               f'水\nΔh={self.delta_h*100:.0f}cm\nv={self.v:.2f}m/s',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax.plot(self.delta_h*100, self.v_air, 'ro', markersize=12, zorder=5)
        ax.text(self.delta_h*100*1.3, self.v_air,
               f'空气\nv={self.v_air:.2f}m/s',
               fontsize=10, ha='left',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        # 公式
        ax.text(25, 1, r'$v = \sqrt{\frac{2(\rho_{Hg}-\rho)g\Delta h}{\rho}}$',
               fontsize=12, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('压差计读数 Δh (cm)', fontsize=12)
        ax.set_ylabel('流速 v (m/s)', fontsize=12)
        ax.set_title('流速-压差关系曲线', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 50)


def test_problem_146():
    """测试题目146"""
    # 已知条件
    delta_h = 0.15      # 压差计读数 (m) = 15cm
    rho_fluid = 1000    # 水的密度 (kg/m³)
    rho_Hg = 13600      # 水银密度 (kg/m³)
    
    # 创建计算对象
    pitot = PitotTube(delta_h, rho_fluid, rho_Hg)
    
    # 打印结果
    pitot.print_results()
    
    # 可视化
    fig = pitot.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_146_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_146_result.png")
    
    # 验证答案（合理性检查）
    assert 1 < pitot.v < 20, "水流速度不合理"
    assert 10 < pitot.v_air < 200, "空气流速不合理"
    assert pitot.delta_p > 0, "压差必须为正"
    assert pitot.p_dynamic > 0, "动压必须为正"
    assert abs(pitot.p_dynamic - pitot.delta_p) < 1, "动压应等于压差"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("毕托管是测速的经典仪器！")
    print("• 原理：伯努利方程")
    print("• 静压孔：测p_s（侧面）")
    print("• 总压孔：测p_t（正对流速，滞止点）")
    print("• 动压：p_d = p_t - p_s = ½ρv²")
    print("• 流速：v = √(2Δp/ρ)")
    print("• 应用：管道、飞机、风洞测速")


if __name__ == "__main__":
    test_problem_146()
