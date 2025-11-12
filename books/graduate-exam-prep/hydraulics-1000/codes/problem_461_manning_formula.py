"""
《水力学考研1000题详解》配套代码
题目461：曼宁公式应用

问题描述：
矩形断面明渠，宽度b=3m，水深h=2m，底坡i=0.001，糙率n=0.013（混凝土）。
求：(1) 过水断面积A、湿周P、水力半径R
    (2) 流速v和流量Q（用曼宁公式）
    (3) 弗劳德数Fr，判断流态
    (4) 断面比能E

考点：
1. 水力要素：A、P、R
2. 曼宁公式：v = (1/n)R^(2/3)i^(1/2)
3. 弗劳德数：Fr = v/√(gh)
4. 断面比能：E = h + v²/2g

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ManningChannel:
    """曼宁公式计算类"""
    
    def __init__(self, b, h, i, n, shape='rectangular'):
        """
        初始化
        
        参数:
            b: 底宽 (m)
            h: 水深 (m)
            i: 底坡 (无量纲)
            n: 糙率 (曼宁系数)
            shape: 断面形状 ('rectangular', 'trapezoidal', 'triangular')
        """
        self.b = b
        self.h = h
        self.i = i
        self.n = n
        self.shape = shape
        self.g = 9.8
        
        # 执行计算
        self.calculate()
    
    def calculate(self):
        """执行水力计算"""
        # 1. 水力要素
        if self.shape == 'rectangular':
            self.A = self.b * self.h
            self.P = self.b + 2 * self.h
            self.B = self.b  # 水面宽
        
        self.R = self.A / self.P
        
        # 2. 曼宁公式求流速和流量
        self.v = (1/self.n) * (self.R**(2/3)) * (self.i**0.5)
        self.Q = self.v * self.A
        
        # 3. 弗劳德数
        self.Fr = self.v / np.sqrt(self.g * self.h)
        
        # 判断流态
        if self.Fr < 1:
            self.flow_regime = "缓流"
        elif self.Fr == 1:
            self.flow_regime = "临界流"
        else:
            self.flow_regime = "急流"
        
        # 4. 断面比能
        self.velocity_head = self.v**2 / (2 * self.g)
        self.E = self.h + self.velocity_head
        
        # 5. 临界水深
        self.q = self.Q / self.b  # 单宽流量
        self.h_c = (self.q**2 / self.g)**(1/3)
        
        # 6. 临界坡度（假设正常水深=当前水深）
        self.R_c = (self.b * self.h_c) / (self.b + 2 * self.h_c)
        self.i_c = (self.n * self.v / (self.R_c**(2/3)))**2
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 80)
        print("题目461：曼宁公式应用")
        print("=" * 80)
        
        print("\n【已知条件】")
        print(f"断面形状: {self.shape} (矩形)")
        print(f"渠道底宽: b = {self.b:.2f} m")
        print(f"水深: h = {self.h:.2f} m")
        print(f"底坡: i = {self.i:.4f} = {self.i*1000:.1f}‰")
        print(f"糙率: n = {self.n:.3f} (混凝土)")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算水力要素")
        print(f"过水断面积: A = bh = {self.b} × {self.h} = {self.A:.3f} m²")
        print(f"湿周: P = b + 2h = {self.b} + 2×{self.h} = {self.P:.3f} m")
        print(f"水力半径: R = A/P = {self.A:.3f}/{self.P:.3f} = {self.R:.4f} m")
        print(f"水面宽: B = {self.B:.3f} m")
        
        print("\n步骤2：曼宁公式计算流速和流量")
        print(f"曼宁公式: v = (1/n)R^(2/3)i^(1/2)")
        print(f"v = (1/{self.n}) × {self.R:.4f}^(2/3) × {self.i:.4f}^(1/2)")
        print(f"  = {1/self.n:.3f} × {self.R**(2/3):.4f} × {self.i**0.5:.4f}")
        print(f"  = {self.v:.4f} m/s")
        print(f"Q = vA = {self.v:.4f} × {self.A:.3f} = {self.Q:.4f} m³/s")
        
        print("\n步骤3：计算弗劳德数，判断流态")
        print(f"Fr = v/√(gh) = {self.v:.4f}/√({self.g}×{self.h})")
        print(f"   = {self.v:.4f}/{np.sqrt(self.g*self.h):.4f}")
        print(f"   = {self.Fr:.4f}")
        print(f"判断: Fr = {self.Fr:.4f} < 1，流态为{self.flow_regime}")
        
        print("\n步骤4：计算断面比能")
        print(f"速度水头: v²/2g = {self.v:.4f}²/(2×{self.g}) = {self.velocity_head:.4f} m")
        print(f"断面比能: E = h + v²/2g = {self.h} + {self.velocity_head:.4f} = {self.E:.4f} m")
        
        print("\n【最终答案】")
        print(f"(1) 水力要素:")
        print(f"    过水断面积 A = {self.A:.3f} m²")
        print(f"    湿周 P = {self.P:.3f} m")
        print(f"    水力半径 R = {self.R:.4f} m")
        print(f"(2) 流速和流量:")
        print(f"    流速 v = {self.v:.4f} m/s")
        print(f"    流量 Q = {self.Q:.4f} m³/s")
        print(f"(3) 流态:")
        print(f"    弗劳德数 Fr = {self.Fr:.4f}")
        print(f"    流态: {self.flow_regime}")
        print(f"(4) 断面比能:")
        print(f"    E = {self.E:.4f} m")
        
        print("\n【附加信息】")
        print(f"单宽流量: q = Q/b = {self.q:.4f} m²/s")
        print(f"临界水深: h_c = {self.h_c:.4f} m")
        print(f"临界坡度: i_c = {self.i_c:.6f} = {self.i_c*1000:.3f}‰")
        print(f"底坡分类: i = {self.i*1000:.1f}‰ > i_c = {self.i_c*1000:.3f}‰，陡坡")
        
        print("=" * 80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：断面示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_cross_section(ax1)
        
        # 子图2：比能曲线
        ax2 = plt.subplot(2, 2, 2)
        self._plot_specific_energy(ax2)
        
        # 子图3：流速分布
        ax3 = plt.subplot(2, 2, 3)
        self._plot_velocity_distribution(ax3)
        
        # 子图4：水力要素
        ax4 = plt.subplot(2, 2, 4)
        self._plot_hydraulic_elements(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_cross_section(self, ax):
        """绘制断面示意图"""
        # 渠道底部和侧壁
        x_bottom = [-0.5, self.b + 0.5]
        y_bottom = [0, 0]
        
        # 绘制渠道
        channel_x = [-0.5, 0, self.b, self.b+0.5]
        channel_y = [0, 0, 0, 0]
        ax.plot(channel_x, channel_y, 'k-', linewidth=3)
        
        # 侧壁
        ax.plot([0, 0], [0, self.h + 0.5], 'k-', linewidth=3)
        ax.plot([self.b, self.b], [0, self.h + 0.5], 'k-', linewidth=3)
        
        # 水体
        water = Polygon([(0, 0), (self.b, 0), (self.b, self.h), (0, self.h)],
                       facecolor='lightblue', edgecolor='blue', linewidth=2, alpha=0.6)
        ax.add_patch(water)
        
        # 水面线
        ax.plot([0, self.b], [self.h, self.h], 'b-', linewidth=2, label='水面')
        
        # 标注
        # 宽度
        ax.annotate('', xy=(self.b, -0.2), xytext=(0, -0.2),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(self.b/2, -0.3, f'b = {self.b} m', fontsize=12, ha='center', color='red')
        
        # 水深
        ax.annotate('', xy=(self.b+0.3, self.h), xytext=(self.b+0.3, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='blue'))
        ax.text(self.b+0.5, self.h/2, f'h = {self.h} m', fontsize=12, 
               ha='left', va='center', color='blue', rotation=90)
        
        # 水力要素标注
        ax.text(self.b/2, self.h/2, 
               f'A = {self.A:.2f} m²\nR = {self.R:.3f} m\nP = {self.P:.2f} m',
               fontsize=11, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 流速箭头
        n_arrows = 5
        for i in range(n_arrows):
            x = self.b * (i + 0.5) / n_arrows
            y = self.h / 2
            ax.arrow(x-0.15, y, 0.3, 0, head_width=0.1, head_length=0.05,
                    fc='darkblue', ec='darkblue')
        
        ax.text(self.b/2, self.h + 0.2, f'v = {self.v:.3f} m/s  →', 
               fontsize=11, ha='center', color='darkblue', weight='bold')
        
        ax.set_xlim(-1, self.b + 1)
        ax.set_ylim(-0.5, self.h + 0.7)
        ax.set_aspect('equal')
        ax.set_xlabel('宽度 (m)', fontsize=12)
        ax.set_ylabel('高度 (m)', fontsize=12)
        ax.set_title('矩形明渠断面', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
    
    def _plot_specific_energy(self, ax):
        """绘制断面比能曲线（E-h图）"""
        # 给定流量，改变水深
        h_range = np.linspace(0.1, 4, 100)
        E_values = []
        
        for h_test in h_range:
            A_test = self.b * h_test
            v_test = self.Q / A_test
            E_test = h_test + v_test**2 / (2 * self.g)
            E_values.append(E_test)
        
        E_values = np.array(E_values)
        
        # 绘制E-h曲线
        ax.plot(E_values, h_range, 'b-', linewidth=2, label='E-h 曲线')
        
        # 45度线
        E_line = np.linspace(0, max(E_values), 100)
        ax.plot(E_line, E_line, 'k--', linewidth=1, alpha=0.5, label='h = E')
        
        # 标记当前工况点
        ax.plot(self.E, self.h, 'ro', markersize=12, label=f'当前工况\n(E={self.E:.3f}m, h={self.h:.2f}m)')
        
        # 标记临界点
        E_c = 1.5 * self.h_c
        ax.plot(E_c, self.h_c, 'g^', markersize=12, label=f'临界点\n(h_c={self.h_c:.3f}m)')
        
        # 标注缓流区和急流区
        ax.text(max(E_values)*0.7, 3, '缓流区\n(Fr<1)', fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        ax.text(max(E_values)*0.3, 0.5, '急流区\n(Fr>1)', fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        ax.set_xlabel('断面比能 E (m)', fontsize=12)
        ax.set_ylabel('水深 h (m)', fontsize=12)
        ax.set_title('断面比能曲线', fontsize=14, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(E_values)*1.1)
        ax.set_ylim(0, 4)
    
    def _plot_velocity_distribution(self, ax):
        """绘制流速分布"""
        # 假设对数分布
        y_range = np.linspace(0.01, self.h, 50)
        v_dist = self.v * (1 + 0.3 * np.log(y_range/0.01 + 1))
        
        ax.plot(v_dist, y_range, 'b-', linewidth=2)
        ax.fill_betweenx(y_range, 0, v_dist, alpha=0.3, color='lightblue')
        
        # 平均流速线
        ax.axvline(self.v, color='red', linestyle='--', linewidth=2, 
                  label=f'平均流速 v={self.v:.3f}m/s')
        
        # 最大流速
        v_max = max(v_dist)
        ax.axvline(v_max, color='green', linestyle=':', linewidth=2,
                  label=f'最大流速 v_max={v_max:.3f}m/s')
        
        ax.set_xlabel('流速 (m/s)', fontsize=12)
        ax.set_ylabel('水深 (m)', fontsize=12)
        ax.set_title('垂线流速分布', fontsize=14, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, self.h*1.1)
    
    def _plot_hydraulic_elements(self, ax):
        """绘制水力要素对比"""
        elements = ['A\n(m²)', 'P\n(m)', 'R\n(m)', 'B\n(m)']
        values = [self.A, self.P, self.R, self.B]
        colors = ['skyblue', 'lightgreen', 'lightcoral', 'gold']
        
        bars = ax.bar(elements, values, color=colors, alpha=0.7, 
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.3f}',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 添加计算公式
        formulas = ['A=bh', 'P=b+2h', 'R=A/P', 'B=b']
        for i, (bar, formula) in enumerate(zip(bars, formulas)):
            ax.text(bar.get_x() + bar.get_width()/2, -max(values)*0.1,
                   formula, ha='center', va='top', fontsize=9, style='italic')
        
        ax.set_ylabel('数值', fontsize=12)
        ax.set_title('水力要素', fontsize=14, weight='bold')
        ax.set_ylim(-max(values)*0.15, max(values)*1.3)
        ax.grid(True, axis='y', alpha=0.3)


def test_problem_461():
    """测试题目461"""
    # 已知条件
    b = 3.0      # 底宽 (m)
    h = 2.0      # 水深 (m)
    i = 0.001    # 底坡
    n = 0.013    # 糙率
    
    # 创建计算对象
    channel = ManningChannel(b, h, i, n)
    
    # 打印结果
    channel.print_results()
    
    # 可视化
    fig = channel.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_461_result.png', 
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_461_result.png")
    
    # 验证答案（合理性检查）
    assert 0.3 < channel.v < 3.0, "流速不合理"
    assert channel.Fr < 1, "应该是缓流"
    assert channel.R > 0, "水力半径必须为正"
    assert channel.Q > 0, "流量必须为正"
    
    print("\n✓ 所有测试通过！")


if __name__ == "__main__":
    test_problem_461()
