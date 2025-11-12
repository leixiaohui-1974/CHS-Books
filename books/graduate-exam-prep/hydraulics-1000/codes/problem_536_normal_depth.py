"""
《水力学考研1000题详解》配套代码
题目536：正常水深迭代计算

问题描述：
矩形明渠，底宽b=3m，底坡i=0.001，糙率n=0.025，流量Q=6m³/s。
求：(1) 正常水深h₀（需要迭代）
    (2) 正常流速v₀
    (3) 弗劳德数Fr，判断流态
    (4) 与临界水深比较，判断底坡类型

考点：
1. 曼宁公式：Q = (1/n)AR^(2/3)i^(1/2)
2. 正常水深：使Q满足曼宁公式的水深
3. 迭代求解：h₀出现在A和R中，需要迭代
4. 临界水深：h_c = ∛(q²/g)
5. 底坡分类：i与i_c比较
6. 流态判断：Fr = v/√(gh)

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch
from scipy.optimize import fsolve, brentq

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class NormalDepth:
    """正常水深计算类"""
    
    def __init__(self, b, i, n, Q, shape='rectangular', g=9.8):
        """
        初始化
        
        参数:
            b: 渠道底宽 (m)
            i: 底坡
            n: 糙率
            Q: 流量 (m³/s)
            shape: 断面形状（'rectangular', 'trapezoidal'）
            g: 重力加速度 (m/s²)
        """
        self.b = b
        self.i = i
        self.n = n
        self.Q = Q
        self.shape = shape
        self.g = g
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算正常水深"""
        # 1. 迭代求解正常水深
        self.h0 = self._solve_normal_depth()
        
        # 2. 计算正常流水力要素
        self.A0 = self.b * self.h0  # 矩形断面
        self.P0 = self.b + 2 * self.h0
        self.R0 = self.A0 / self.P0
        self.v0 = self.Q / self.A0
        
        # 3. 弗劳德数
        self.Fr = self.v0 / np.sqrt(self.g * self.h0)
        
        # 4. 临界水深
        self.q = self.Q / self.b
        self.h_c = (self.q**2 / self.g)**(1/3)
        
        # 5. 临界坡度
        A_c = self.b * self.h_c
        P_c = self.b + 2 * self.h_c
        R_c = A_c / P_c
        self.i_c = (self.n * self.Q / (A_c * R_c**(2/3)))**2
        
        # 6. 底坡类型判断
        if abs(self.i - self.i_c) / self.i_c < 0.01:
            self.slope_type = "临界坡"
        elif self.i < self.i_c:
            self.slope_type = "缓坡"
        else:
            self.slope_type = "陡坡"
        
        # 7. 流态判断
        if abs(self.Fr - 1.0) < 0.01:
            self.flow_regime = "临界流"
        elif self.Fr < 1.0:
            self.flow_regime = "缓流"
        else:
            self.flow_regime = "急流"
        
        # 8. 验证曼宁公式
        Q_check = (1/self.n) * self.A0 * self.R0**(2/3) * np.sqrt(self.i)
        self.Q_error = abs(Q_check - self.Q) / self.Q * 100
    
    def _solve_normal_depth(self):
        """迭代求解正常水深"""
        # 目标函数：F(h) = Q - (1/n)AR^(2/3)i^(1/2) = 0
        def f(h):
            if h <= 0:
                return 1e10
            A = self.b * h
            P = self.b + 2 * h
            R = A / P
            Q_calc = (1/self.n) * A * R**(2/3) * np.sqrt(self.i)
            return Q_calc - self.Q
        
        # 初始估计（假设h约为临界水深）
        h_init = (self.Q / self.b)**2 / self.g
        h_init = h_init**(1/3)
        
        # 使用fsolve求解
        try:
            h0 = fsolve(f, h_init)[0]
            if h0 > 0 and abs(f(h0)) < 1e-6:
                return h0
        except:
            pass
        
        # 备用方法：使用brentq（二分法）
        try:
            h0 = brentq(f, 0.01, 10.0)
            return h0
        except:
            # 如果还是失败，使用牛顿迭代
            return self._newton_iteration(f, h_init)
    
    def _newton_iteration(self, f, h_init):
        """牛顿迭代法"""
        h = h_init
        for i in range(100):
            fh = f(h)
            # 数值导数
            dh = 0.0001
            dfh = (f(h + dh) - fh) / dh
            if abs(dfh) < 1e-10:
                break
            h_new = h - fh / dfh
            if h_new <= 0:
                h_new = h / 2
            if abs(h_new - h) < 1e-6:
                return h_new
            h = h_new
        return h
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*80)
        print("题目536：正常水深迭代计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"断面形状: {self.shape} (矩形)")
        print(f"渠道底宽: b = {self.b} m")
        print(f"底坡: i = {self.i} = {self.i*1000:.2f}‰")
        print(f"糙率: n = {self.n}")
        print(f"流量: Q = {self.Q} m³/s")
        
        print("\n【正常水深概念】")
        print("正常水深h₀是均匀流条件下的水深，满足：")
        print("  • 水深沿程不变：dh/dx = 0")
        print("  • 流速沿程不变：dv/dx = 0")
        print("  • 满足曼宁公式：Q = (1/n)AR^(2/3)i^(1/2)")
        print("  • 底坡 = 水力坡度 = 能量坡度：i = J = S₀")
        
        print("\n【求解思路】")
        print("曼宁公式：Q = (1/n)AR^(2/3)i^(1/2)")
        print("矩形断面：A = bh, P = b + 2h, R = A/P")
        print("目标方程：Q = (1/n)·bh·[(bh)/(b+2h)]^(2/3)·√i")
        print("难点：h同时出现在A和R中，无法直接求解")
        print("方法：迭代法（牛顿法、二分法或fsolve）")
        
        print("\n【迭代过程】")
        print(f"目标函数：F(h) = Q_calc(h) - Q = 0")
        print(f"初始估计：h_init ≈ h_c = {(self.Q/self.b)**2/self.g**(1/3):.4f} m")
        print(f"迭代方法：scipy.fsolve（牛顿类方法）")
        print(f"收敛准则：|F(h)| < 10⁻⁶")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算正常水深h₀（迭代求解）")
        print(f"正常水深: h₀ = {self.h0:.4f} m")
        
        print("\n步骤2：计算正常流水力要素")
        print(f"断面面积: A₀ = bh₀ = {self.b}×{self.h0:.4f} = {self.A0:.4f} m²")
        print(f"湿周: P₀ = b + 2h₀ = {self.b} + 2×{self.h0:.4f} = {self.P0:.4f} m")
        print(f"水力半径: R₀ = A₀/P₀ = {self.A0:.4f}/{self.P0:.4f} = {self.R0:.4f} m")
        
        print("\n步骤3：计算正常流速")
        print(f"v₀ = Q/A₀ = {self.Q}/{self.A0:.4f} = {self.v0:.4f} m/s")
        
        print("\n步骤4：验证曼宁公式")
        Q_check = (1/self.n) * self.A0 * self.R0**(2/3) * np.sqrt(self.i)
        print(f"Q_check = (1/n)AR^(2/3)√i")
        print(f"        = (1/{self.n})×{self.A0:.4f}×{self.R0:.4f}^(2/3)×√{self.i}")
        print(f"        = {Q_check:.6f} m³/s")
        print(f"Q_given = {self.Q} m³/s")
        print(f"误差: {self.Q_error:.6f}%  ✓")
        
        print("\n步骤5：计算弗劳德数")
        print(f"Fr = v₀/√(gh₀)")
        print(f"   = {self.v0:.4f}/√({self.g}×{self.h0:.4f})")
        print(f"   = {self.v0:.4f}/{np.sqrt(self.g*self.h0):.4f}")
        print(f"   = {self.Fr:.4f}")
        if abs(self.Fr - 1.0) < 0.01:
            print(f"流态: Fr ≈ 1  →  临界流")
        elif self.Fr < 1.0:
            print(f"流态: Fr < 1  →  缓流")
        else:
            print(f"流态: Fr > 1  →  急流")
        
        print("\n步骤6：计算临界水深")
        print(f"单宽流量: q = Q/b = {self.Q}/{self.b} = {self.q:.4f} m²/s")
        print(f"临界水深: h_c = ∛(q²/g)")
        print(f"         = ∛({self.q:.4f}²/{self.g})")
        print(f"         = {self.h_c:.4f} m")
        
        print("\n步骤7：比较正常水深与临界水深")
        print(f"正常水深: h₀ = {self.h0:.4f} m")
        print(f"临界水深: h_c = {self.h_c:.4f} m")
        if abs(self.h0 - self.h_c) / self.h_c < 0.01:
            print(f"h₀ ≈ h_c  →  临界坡，临界流")
        elif self.h0 > self.h_c:
            print(f"h₀ > h_c  →  缓坡，缓流")
        else:
            print(f"h₀ < h_c  →  陡坡，急流")
        
        print("\n步骤8：计算临界坡度")
        A_c = self.b * self.h_c
        P_c = self.b + 2 * self.h_c
        R_c = A_c / P_c
        print(f"临界坡度: i_c = (nQ/(A_c·R_c^(2/3)))²")
        print(f"         = ({self.n}×{self.Q}/({A_c:.4f}×{R_c:.4f}^(2/3)))²")
        print(f"         = {self.i_c:.6f} = {self.i_c*1000:.3f}‰")
        
        print("\n步骤9：底坡类型判断")
        print(f"实际底坡: i = {self.i:.6f} = {self.i*1000:.3f}‰")
        print(f"临界坡度: i_c = {self.i_c:.6f} = {self.i_c*1000:.3f}‰")
        if abs(self.i - self.i_c) / self.i_c < 0.01:
            print(f"i ≈ i_c  →  临界坡")
        elif self.i < self.i_c:
            print(f"i < i_c  →  缓坡（正常水深>临界水深，缓流）")
        else:
            print(f"i > i_c  →  陡坡（正常水深<临界水深，急流）")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 正常水深: h₀ = {self.h0:.4f} m")
        print(f"(2) 正常流速: v₀ = {self.v0:.4f} m/s")
        print(f"(3) 弗劳德数: Fr = {self.Fr:.4f}  →  {self.flow_regime}")
        print(f"(4) 底坡类型: {self.slope_type}")
        print(f"    临界水深: h_c = {self.h_c:.4f} m")
        print(f"    水深比较: h₀/h_c = {self.h0/self.h_c:.4f}")
        print("="*80)
        
        print("\n【核心公式】")
        print("曼宁公式: Q = (1/n)AR^(2/3)i^(1/2)")
        print("临界水深: h_c = ∛(q²/g)  （矩形）")
        print("临界坡度: i_c = (nQ/(A_c·R_c^(2/3)))²")
        print("弗劳德数: Fr = v/√(gh)")
        print("底坡分类:")
        print("  • i < i_c: 缓坡，h₀ > h_c，缓流")
        print("  • i = i_c: 临界坡，h₀ = h_c，临界流")
        print("  • i > i_c: 陡坡，h₀ < h_c，急流")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：渠道断面
        ax1 = plt.subplot(2, 2, 1)
        self._plot_channel_section(ax1)
        
        # 子图2：Q-h关系曲线
        ax2 = plt.subplot(2, 2, 2)
        self._plot_Q_h_curve(ax2)
        
        # 子图3：水深对比
        ax3 = plt.subplot(2, 2, 3)
        self._plot_depth_comparison(ax3)
        
        # 子图4：底坡分类
        ax4 = plt.subplot(2, 2, 4)
        self._plot_slope_classification(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_channel_section(self, ax):
        """绘制渠道断面"""
        # 渠道底部和侧壁
        channel = Polygon([(0, 0), (self.b, 0), (self.b, self.h0*1.3), 
                          (0, self.h0*1.3)],
                         facecolor='lightgray', edgecolor='black', 
                         linewidth=2, alpha=0.5)
        ax.add_patch(channel)
        
        # 水体（正常水深）
        water = Rectangle((0, 0), self.b, self.h0, facecolor='lightblue',
                         edgecolor='blue', linewidth=2, alpha=0.6)
        ax.add_patch(water)
        
        # 水面线
        ax.plot([0, self.b], [self.h0, self.h0], 'b-', linewidth=2.5)
        
        # 标注
        # 底宽
        ax.annotate('', xy=(self.b, -0.1), xytext=(0, -0.1),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(self.b/2, -0.2, f'b={self.b}m', fontsize=11, ha='center', color='red')
        
        # 正常水深
        ax.annotate('', xy=(self.b+0.2, self.h0), xytext=(self.b+0.2, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax.text(self.b+0.4, self.h0/2, f'h₀={self.h0:.3f}m', fontsize=11,
               rotation=90, va='center', color='blue')
        
        # 临界水深线
        ax.plot([0, self.b], [self.h_c, self.h_c], 'r--', linewidth=2, alpha=0.7)
        ax.text(self.b/2, self.h_c+0.05, f'h_c={self.h_c:.3f}m', 
               fontsize=10, ha='center', color='red',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 流速分布（简化）
        n_arrows = 5
        for i in range(n_arrows):
            x = self.b * (i + 0.5) / n_arrows
            y = self.h0 / 2
            ax.arrow(x-0.15, y, 0.2, 0, head_width=0.06, head_length=0.05,
                    fc='darkblue', ec='darkblue', linewidth=1.5)
        
        ax.text(self.b/2, self.h0 + 0.15, f'v₀={self.v0:.3f}m/s  →',
               fontsize=11, ha='center', color='darkblue', weight='bold')
        
        # 流态和底坡标注
        ax.text(self.b/2, self.h0/2, 
               f'{self.flow_regime}\nFr={self.Fr:.3f}\n{self.slope_type}',
               fontsize=10, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax.set_xlim(-0.5, self.b+0.8)
        ax.set_ylim(-0.3, self.h0*1.5)
        ax.set_aspect('equal')
        ax.set_xlabel('宽度 (m)', fontsize=12)
        ax.set_ylabel('高度 (m)', fontsize=12)
        ax.set_title('矩形渠道断面（正常水深）', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_Q_h_curve(self, ax):
        """绘制Q-h关系曲线"""
        # 水深范围
        h_range = np.linspace(0.1, self.h0*2, 100)
        Q_range = []
        
        for h in h_range:
            A = self.b * h
            P = self.b + 2 * h
            R = A / P
            Q = (1/self.n) * A * R**(2/3) * np.sqrt(self.i)
            Q_range.append(Q)
        
        # 绘制曲线
        ax.plot(Q_range, h_range, 'b-', linewidth=2.5, label='Q-h关系')
        
        # 标注正常水深
        ax.plot(self.Q, self.h0, 'ro', markersize=12, zorder=5)
        ax.text(self.Q*1.05, self.h0, 
               f'正常水深\nh₀={self.h0:.3f}m\nQ={self.Q}m³/s',
               fontsize=10, va='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 标注临界水深
        ax.axhline(self.h_c, color='red', linestyle='--', linewidth=2,
                  label=f'临界水深h_c={self.h_c:.3f}m')
        
        # 给定流量线
        ax.axvline(self.Q, color='green', linestyle='--', linewidth=1.5,
                  alpha=0.7, label=f'给定流量Q={self.Q}m³/s')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('水深 h (m)', fontsize=12)
        ax.set_title('流量-水深关系曲线', fontsize=13, weight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_depth_comparison(self, ax):
        """绘制水深对比"""
        depths = ['正常水深\nh₀', '临界水深\nh_c']
        values = [self.h0, self.h_c]
        colors = ['skyblue', 'lightcoral']
        
        bars = ax.bar(depths, values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.4f}m',
                   ha='center', va='bottom', fontsize=12, weight='bold')
        
        # 比值标注
        ratio = self.h0 / self.h_c
        ax.text(0.5, max(values)*0.5, f'h₀/h_c = {ratio:.3f}',
               fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 流态判断
        if ratio > 1.05:
            flow_type = "缓流（h₀>h_c）"
            color = 'blue'
        elif ratio < 0.95:
            flow_type = "急流（h₀<h_c）"
            color = 'red'
        else:
            flow_type = "临界流（h₀≈h_c）"
            color = 'orange'
        
        ax.text(0.5, max(values)*0.8, flow_type,
               fontsize=11, ha='center', color=color, weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.set_ylabel('水深 (m)', fontsize=12)
        ax.set_title('正常水深与临界水深对比', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, max(values)*1.3)
    
    def _plot_slope_classification(self, ax):
        """绘制底坡分类"""
        slopes = ['实际底坡\ni', '临界坡度\ni_c']
        values = [self.i*1000, self.i_c*1000]  # 转换为‰
        colors = ['lightgreen' if self.i < self.i_c else 'lightcoral', 'yellow']
        
        bars = ax.bar(slopes, values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.3f}‰',
                   ha='center', va='bottom', fontsize=12, weight='bold')
        
        # 坡度比
        ratio = self.i / self.i_c
        ax.text(0.5, max(values)*0.5, f'i/i_c = {ratio:.3f}',
               fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 底坡类型
        ax.text(0.5, max(values)*0.8, self.slope_type,
               fontsize=12, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 说明
        if self.slope_type == "缓坡":
            explanation = "i<i_c → h₀>h_c → 缓流"
        elif self.slope_type == "陡坡":
            explanation = "i>i_c → h₀<h_c → 急流"
        else:
            explanation = "i≈i_c → h₀≈h_c → 临界流"
        
        ax.text(0.5, max(values)*1.15, explanation,
               fontsize=10, ha='center', style='italic')
        
        ax.set_ylabel('坡度 (‰)', fontsize=12)
        ax.set_title('底坡分类判断', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, max(values)*1.3)


def test_problem_536():
    """测试题目536"""
    # 已知条件
    b = 3.0             # 渠道底宽 (m)
    i = 0.001           # 底坡
    n = 0.025           # 糙率
    Q = 6.0             # 流量 (m³/s)
    
    # 创建计算对象
    normal = NormalDepth(b, i, n, Q)
    
    # 打印结果
    normal.print_results()
    
    # 可视化
    fig = normal.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_536_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_536_result.png")
    
    # 验证答案（合理性检查）
    assert 0.1 < normal.h0 < 10.0, "正常水深不合理"
    assert 0.1 < normal.v0 < 10.0, "流速不合理"
    assert 0 < normal.Fr < 5.0, "弗劳德数不合理"
    assert normal.Q_error < 1.0, "曼宁公式验证误差过大"
    assert normal.h_c > 0, "临界水深必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("正常水深是均匀流的核心概念！")
    print("• 定义：满足曼宁公式的水深")
    print("• 特点：水深、流速沿程不变")
    print("• 求解：迭代法（牛顿、二分法）")
    print("• 判断：与临界水深比较 → 流态和底坡类型")
    print("• 应用：渠道设计、水面线分析")


if __name__ == "__main__":
    test_problem_536()
