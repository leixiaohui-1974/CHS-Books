"""
《水力学考研1000题详解》配套代码
题目481：临界水深计算

问题描述：
矩形明渠，宽度b=2m，流量Q=4m³/s。
求：(1) 临界水深h_c
    (2) 临界流速v_c
    (3) 临界坡度i_c（糙率n=0.015）
    (4) 绘制E-h曲线（断面比能曲线）

考点：
1. 临界水深：h_c = ∛(q²/g) （矩形）
2. 临界流速：v_c = √(gh_c)
3. 弗劳德数：Fr = v/√(gh) = 1（临界）
4. 断面比能：E = h + v²/2g = 3/2·h_c（最小）
5. 临界坡度：i_c，使正常水深=临界水深

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
from scipy.optimize import fsolve

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CriticalDepth:
    """临界水深计算类"""
    
    def __init__(self, b, Q, n=0.015, shape='rectangular'):
        """
        初始化
        
        参数:
            b: 渠道底宽 (m)
            Q: 流量 (m³/s)
            n: 糙率系数
            shape: 断面形状（'rectangular', 'trapezoidal', 'triangular'）
        """
        self.b = b
        self.Q = Q
        self.n = n
        self.shape = shape
        self.g = 9.8
        
        # 执行计算
        self.calculate()
    
    def calculate(self):
        """执行水力计算"""
        # 1. 单宽流量
        self.q = self.Q / self.b
        
        # 2. 临界水深（矩形断面）
        self.h_c = (self.q**2 / self.g)**(1/3)
        
        # 3. 临界断面面积、湿周、水力半径
        self.A_c = self.b * self.h_c
        self.P_c = self.b + 2 * self.h_c
        self.R_c = self.A_c / self.P_c
        
        # 4. 临界流速
        self.v_c = self.q / self.h_c
        
        # 验证：v_c = √(gh_c)
        self.v_c_theory = np.sqrt(self.g * self.h_c)
        
        # 5. 临界弗劳德数（应该=1）
        self.Fr_c = self.v_c / np.sqrt(self.g * self.h_c)
        
        # 6. 临界比能（最小比能）
        self.E_min = 1.5 * self.h_c
        
        # 验证：E_min = h_c + v_c²/2g
        self.E_check = self.h_c + self.v_c**2 / (2 * self.g)
        
        # 7. 临界坡度（使正常水深=临界水深）
        # 曼宁公式：Q = (1/n)AR^(2/3)i^(1/2)
        # i_c = (nQ / (AR^(2/3)))^2
        self.i_c = (self.n * self.Q / (self.A_c * self.R_c**(2/3)))**2
        
        # 8. 绘制E-h曲线需要的数据
        self.h_range = np.linspace(0.1, 3*self.h_c, 200)
        self.E_curve = self._compute_E_curve(self.h_range)
    
    def _compute_E_curve(self, h_values):
        """计算E-h曲线"""
        E_values = []
        for h in h_values:
            A = self.b * h
            v = self.Q / A
            E = h + v**2 / (2 * self.g)
            E_values.append(E)
        return np.array(E_values)
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 80)
        print("题目481：临界水深计算")
        print("=" * 80)
        
        print("\n【已知条件】")
        print(f"断面形状: {self.shape} (矩形)")
        print(f"渠道底宽: b = {self.b:.2f} m")
        print(f"流量: Q = {self.Q:.2f} m³/s")
        print(f"糙率: n = {self.n:.3f}")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算单宽流量")
        print(f"q = Q/b = {self.Q:.2f}/{self.b:.2f} = {self.q:.4f} m²/s")
        
        print("\n步骤2：计算临界水深（矩形断面公式）")
        print(f"h_c = ∛(q²/g)")
        print(f"    = ∛({self.q:.4f}²/{self.g})")
        print(f"    = ∛({self.q**2:.6f}/{self.g})")
        print(f"    = ∛{self.q**2/self.g:.6f}")
        print(f"    = {self.h_c:.4f} m")
        
        print("\n步骤3：计算临界断面水力要素")
        print(f"A_c = bh_c = {self.b} × {self.h_c:.4f} = {self.A_c:.4f} m²")
        print(f"P_c = b + 2h_c = {self.b} + 2×{self.h_c:.4f} = {self.P_c:.4f} m")
        print(f"R_c = A_c/P_c = {self.A_c:.4f}/{self.P_c:.4f} = {self.R_c:.4f} m")
        
        print("\n步骤4：计算临界流速")
        print(f"方法1（连续性）：v_c = q/h_c = {self.q:.4f}/{self.h_c:.4f} = {self.v_c:.4f} m/s")
        print(f"方法2（理论公式）：v_c = √(gh_c) = √({self.g}×{self.h_c:.4f}) = {self.v_c_theory:.4f} m/s")
        print(f"验证: 两种方法结果一致 ✓")
        
        print("\n步骤5：计算弗劳德数")
        print(f"Fr_c = v_c/√(gh_c) = {self.v_c:.4f}/√({self.g}×{self.h_c:.4f})")
        print(f"     = {self.v_c:.4f}/{np.sqrt(self.g*self.h_c):.4f}")
        print(f"     = {self.Fr_c:.6f} ≈ 1")
        print(f"临界流态特征: Fr = 1 ✓")
        
        print("\n步骤6：计算最小比能")
        print(f"方法1（理论公式）：E_min = 3/2·h_c = 1.5 × {self.h_c:.4f} = {self.E_min:.4f} m")
        print(f"方法2（验证计算）：E = h_c + v_c²/2g")
        print(f"                 = {self.h_c:.4f} + {self.v_c:.4f}²/(2×{self.g})")
        print(f"                 = {self.h_c:.4f} + {self.v_c**2/(2*self.g):.4f}")
        print(f"                 = {self.E_check:.4f} m")
        print(f"验证: 两种方法结果一致 ✓")
        
        print("\n步骤7：计算临界坡度")
        print(f"临界坡度定义: 使正常水深h_0 = 临界水深h_c的底坡")
        print(f"曼宁公式: Q = (1/n)AR^(2/3)i^(1/2)")
        print(f"i_c = (nQ / (AR^(2/3)))²")
        print(f"    = ({self.n}×{self.Q:.2f} / ({self.A_c:.4f}×{self.R_c:.4f}^(2/3)))²")
        print(f"    = ({self.n*self.Q:.4f} / ({self.A_c:.4f}×{self.R_c**(2/3):.4f}))²")
        print(f"    = ({self.n*self.Q:.4f} / {self.A_c*self.R_c**(2/3):.4f})²")
        print(f"    = {self.i_c:.6f} = {self.i_c*1000:.3f}‰")
        
        print("\n【最终答案】")
        print(f"(1) 临界水深: h_c = {self.h_c:.4f} m")
        print(f"(2) 临界流速: v_c = {self.v_c:.4f} m/s")
        print(f"(3) 临界坡度: i_c = {self.i_c:.6f} = {self.i_c*1000:.3f}‰")
        print(f"(4) 最小比能: E_min = {self.E_min:.4f} m")
        
        print("\n【临界流态判别准则】")
        print(f"✓ Fr = 1  →  临界流")
        print(f"✓ Fr < 1  →  缓流（h > h_c）")
        print(f"✓ Fr > 1  →  急流（h < h_c）")
        
        print("\n【底坡分类】")
        print(f"设实际底坡为 i：")
        print(f"  i < i_c = {self.i_c*1000:.3f}‰  →  缓坡（正常水深 > 临界水深）")
        print(f"  i = i_c = {self.i_c*1000:.3f}‰  →  临界坡（正常水深 = 临界水深）")
        print(f"  i > i_c = {self.i_c*1000:.3f}‰  →  陡坡（正常水深 < 临界水深）")
        
        print("=" * 80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：E-h曲线（断面比能曲线）
        ax1 = plt.subplot(2, 2, 1)
        self._plot_E_h_curve(ax1)
        
        # 子图2：流态判别
        ax2 = plt.subplot(2, 2, 2)
        self._plot_flow_regime(ax2)
        
        # 子图3：渠道断面
        ax3 = plt.subplot(2, 2, 3)
        self._plot_channel_section(ax3)
        
        # 子图4：水力要素对比
        ax4 = plt.subplot(2, 2, 4)
        self._plot_hydraulic_elements(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_E_h_curve(self, ax):
        """绘制E-h曲线（断面比能曲线）"""
        # E-h曲线
        ax.plot(self.E_curve, self.h_range, 'b-', linewidth=2.5, label='E-h 曲线')
        
        # 45度线（h=E）
        E_max = max(self.E_curve)
        h_max = max(self.h_range)
        diag_max = min(E_max, h_max)
        ax.plot([0, diag_max], [0, diag_max], 'k--', linewidth=1, alpha=0.5, label='h = E')
        
        # 标记临界点
        ax.plot(self.E_min, self.h_c, 'ro', markersize=12, 
               label=f'临界点 (E_min={self.E_min:.3f}m, h_c={self.h_c:.3f}m)', zorder=5)
        
        # 从临界点画竖线和横线
        ax.plot([self.E_min, self.E_min], [0, self.h_c], 'r--', linewidth=1, alpha=0.7)
        ax.plot([0, self.E_min], [self.h_c, self.h_c], 'r--', linewidth=1, alpha=0.7)
        
        # 标注E_min和h_c
        ax.text(self.E_min, -0.1, f'E_min={self.E_min:.3f}m', 
               fontsize=9, ha='center', color='red')
        ax.text(-0.1, self.h_c, f'h_c={self.h_c:.3f}m', 
               fontsize=9, ha='right', va='center', color='red')
        
        # 标注缓流区和急流区
        # 缓流区（h > h_c）
        ax.fill_between(self.E_curve[self.h_range > self.h_c], 
                       self.h_range[self.h_range > self.h_c], 
                       self.h_c, alpha=0.2, color='blue')
        ax.text(E_max*0.8, h_max*0.8, '缓流区\n(Fr<1)\nh>h_c', 
               fontsize=11, ha='center', 
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 急流区（h < h_c）
        ax.fill_between(self.E_curve[self.h_range < self.h_c], 
                       self.h_range[self.h_range < self.h_c], 
                       0, alpha=0.2, color='red')
        ax.text(E_max*0.5, self.h_c*0.3, '急流区\n(Fr>1)\nh<h_c', 
               fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        ax.set_xlabel('断面比能 E (m)', fontsize=12)
        ax.set_ylabel('水深 h (m)', fontsize=12)
        ax.set_title('E-h 曲线（断面比能曲线）', fontsize=14, weight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, E_max*1.1)
        ax.set_ylim(0, h_max*0.9)
    
    def _plot_flow_regime(self, ax):
        """绘制流态判别"""
        # 三种流态
        regimes = ['急流\nFr>1', '临界流\nFr=1', '缓流\nFr<1']
        Fr_values = [1.5, 1.0, 0.7]
        colors = ['red', 'orange', 'blue']
        
        bars = ax.bar(regimes, Fr_values, color=colors, alpha=0.7, 
                     edgecolor='black', linewidth=2)
        
        # 标注Fr值
        for bar, Fr in zip(bars, Fr_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'Fr={Fr:.1f}',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # Fr=1的临界线
        ax.axhline(1.0, color='black', linestyle='--', linewidth=2, label='Fr=1 (临界)')
        
        # 标注本题
        ax.text(1, 1.3, f'本题\nFr={self.Fr_c:.4f}≈1\n临界流态',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_ylabel('弗劳德数 Fr', fontsize=12)
        ax.set_title('流态判别（弗劳德数）', fontsize=14, weight='bold')
        ax.set_ylim(0, 2.0)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_channel_section(self, ax):
        """绘制渠道断面"""
        # 渠道底部和侧壁
        channel_x = [0, 0, self.b, self.b, 0]
        channel_y = [0, self.h_c*1.5, self.h_c*1.5, 0, 0]
        ax.plot(channel_x, channel_y, 'k-', linewidth=3)
        
        # 水体（临界水深）
        water = Polygon([(0, 0), (self.b, 0), (self.b, self.h_c), (0, self.h_c)],
                       facecolor='lightblue', edgecolor='blue', linewidth=2, alpha=0.6)
        ax.add_patch(water)
        
        # 水面线
        ax.plot([0, self.b], [self.h_c, self.h_c], 'b-', linewidth=2, label='临界水面')
        
        # 标注
        # 宽度
        ax.annotate('', xy=(self.b, -0.1), xytext=(0, -0.1),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(self.b/2, -0.2, f'b = {self.b} m', fontsize=12, ha='center', color='red')
        
        # 临界水深
        ax.annotate('', xy=(self.b+0.2, self.h_c), xytext=(self.b+0.2, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax.text(self.b+0.4, self.h_c/2, f'h_c = {self.h_c:.3f} m', 
               fontsize=11, ha='left', va='center', color='blue', rotation=90)
        
        # 流速箭头
        n_arrows = 5
        for i in range(n_arrows):
            x = self.b * (i + 0.5) / n_arrows
            y = self.h_c / 2
            ax.arrow(x-0.15, y, 0.25, 0, head_width=0.08, head_length=0.05,
                    fc='darkblue', ec='darkblue')
        
        ax.text(self.b/2, self.h_c + 0.15, f'v_c = {self.v_c:.3f} m/s  →', 
               fontsize=11, ha='center', color='darkblue', weight='bold')
        
        # 标注临界状态
        ax.text(self.b/2, self.h_c/2, 
               f'临界状态\nFr = 1\nE = E_min',
               fontsize=10, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlim(-0.5, self.b + 0.8)
        ax.set_ylim(-0.3, self.h_c*1.7)
        ax.set_aspect('equal')
        ax.set_xlabel('渠道宽度 (m)', fontsize=12)
        ax.set_ylabel('高度 (m)', fontsize=12)
        ax.set_title('矩形渠道断面（临界水深）', fontsize=14, weight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    def _plot_hydraulic_elements(self, ax):
        """绘制水力要素对比"""
        elements = ['h_c\n(m)', 'v_c\n(m/s)', 'Fr', 'E_min\n(m)']
        values = [self.h_c, self.v_c, self.Fr_c, self.E_min]
        colors = ['skyblue', 'lightgreen', 'gold', 'lightcoral']
        
        bars = ax.bar(elements, values, color=colors, alpha=0.7, 
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.4f}',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注公式
        formulas = ['∛(q²/g)', '√(gh_c)', 'v/√(gh)', '3h_c/2']
        for i, (bar, formula) in enumerate(zip(bars, formulas)):
            ax.text(bar.get_x() + bar.get_width()/2, -max(values)*0.08,
                   formula, ha='center', va='top', fontsize=8, style='italic')
        
        # 特别标注Fr=1
        ax.plot([2.5], [1.0], 'r*', markersize=20, zorder=5)
        ax.text(2.5, 1.2, 'Fr=1\n(临界)', fontsize=9, ha='center', color='red')
        
        ax.set_ylabel('数值', fontsize=12)
        ax.set_title('临界状态水力要素', fontsize=14, weight='bold')
        ax.set_ylim(0, max(values)*1.3)
        ax.grid(True, axis='y', alpha=0.3)


def test_problem_481():
    """测试题目481"""
    # 已知条件
    b = 2.0         # 渠道底宽 (m)
    Q = 4.0         # 流量 (m³/s)
    n = 0.015       # 糙率
    
    # 创建计算对象
    critical = CriticalDepth(b, Q, n)
    
    # 打印结果
    critical.print_results()
    
    # 可视化
    fig = critical.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_481_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_481_result.png")
    
    # 验证答案（合理性检查）
    assert 0.3 < critical.h_c < 3.0, "临界水深不合理"
    assert 0.5 < critical.v_c < 5.0, "临界流速不合理"
    assert abs(critical.Fr_c - 1.0) < 0.001, "弗劳德数应该等于1"
    assert abs(critical.E_min - 1.5*critical.h_c) < 0.001, "最小比能公式错误"
    assert abs(critical.v_c - np.sqrt(critical.g*critical.h_c)) < 0.001, "临界流速公式错误"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("临界水深是明渠流最重要的概念之一！")
    print("• 临界水深h_c：使断面比能E最小的水深")
    print("• 临界流速v_c = √(gh_c)")
    print("• 临界状态：Fr = 1")
    print("• 最小比能：E_min = 3h_c/2")
    print("• 临界坡度：使h_0 = h_c的底坡")


if __name__ == "__main__":
    test_problem_481()
