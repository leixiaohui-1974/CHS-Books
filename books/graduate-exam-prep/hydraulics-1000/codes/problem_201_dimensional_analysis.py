"""
《水力学考研1000题详解》配套代码
题目201：量纲分析与相似理论

问题描述：
水流绕圆柱的阻力F与流速v、圆柱直径d、流体密度ρ、动力粘度μ有关。
即 F = f(v, d, ρ, μ)
要求：
(1) 用Buckingham π定理进行量纲分析，确定π项数量
(2) 推导无量纲关系式
(3) 识别相似准则（雷诺数）
(4) 若模型与原型的长度比例为1:10，流速比为1:5，求阻力比
(5) 分析常见相似准则（Re, Fr, Eu, We, Ma）的物理意义

考点：
1. Buckingham π定理：n个物理量，m个基本量纲 → (n-m)个π项
2. 量纲矩阵法
3. 相似准则（Re, Fr, Eu, We, Ma）
4. 模型试验相似律
5. 无量纲化处理

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, FancyBboxPatch
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DimensionalAnalysis:
    """量纲分析类"""
    
    def __init__(self):
        """初始化"""
        # 物理量及其量纲
        self.variables = {
            'F': {'name': '阻力', 'dimension': [1, 1, -2], 'unit': 'N'},  # [M L T⁻²]
            'v': {'name': '流速', 'dimension': [0, 1, -1], 'unit': 'm/s'},  # [L T⁻¹]
            'd': {'name': '直径', 'dimension': [0, 1, 0], 'unit': 'm'},  # [L]
            'ρ': {'name': '密度', 'dimension': [1, -3, 0], 'unit': 'kg/m³'},  # [M L⁻³]
            'μ': {'name': '动力粘度', 'dimension': [1, -1, -1], 'unit': 'Pa·s'}  # [M L⁻¹ T⁻¹]
        }
        
        # 基本量纲
        self.basic_dimensions = ['M', 'L', 'T']  # 质量、长度、时间
        
        # 相似准则
        self.similarity_criteria = {
            'Re': {
                'name': '雷诺数',
                'formula': 'ρvd/μ',
                'meaning': '惯性力/粘性力',
                'application': '管流、边界层、阻力'
            },
            'Fr': {
                'name': '弗劳德数',
                'formula': 'v/√(gL)',
                'meaning': '惯性力/重力',
                'application': '明渠流、自由液面流动'
            },
            'Eu': {
                'name': '欧拉数',
                'formula': 'Δp/(ρv²)',
                'meaning': '压力/惯性力',
                'application': '压力分布、空化'
            },
            'We': {
                'name': '韦伯数',
                'formula': 'ρv²L/σ',
                'meaning': '惯性力/表面张力',
                'application': '液滴、气泡、波浪'
            },
            'Ma': {
                'name': '马赫数',
                'formula': 'v/c',
                'meaning': '流速/声速',
                'application': '可压缩流、高速气体'
            }
        }
        
        # 执行量纲分析
        self.buckingham_analysis()
    
    def buckingham_analysis(self):
        """Buckingham π定理分析"""
        # 统计
        self.n = len(self.variables)  # 物理量个数
        self.m = len(self.basic_dimensions)  # 基本量纲个数
        self.k = self.n - self.m  # π项个数
        
        print("\n" + "="*80)
        print("题目201：量纲分析与相似理论")
        print("="*80)
        
        print("\n【问题描述】")
        print("水流绕圆柱的阻力F与以下因素有关：")
        print("  v - 流速 (m/s)")
        print("  d - 圆柱直径 (m)")
        print("  ρ - 流体密度 (kg/m³)")
        print("  μ - 动力粘度 (Pa·s)")
        print("\n函数关系：F = f(v, d, ρ, μ)")
        
        print("\n【Buckingham π定理】")
        print(f"物理量个数：n = {self.n}")
        print(f"基本量纲个数：m = {self.m}")
        print(f"π项个数：k = n - m = {self.n} - {self.m} = {self.k}")
        
        print("\n【量纲分析步骤】")
        
        # 步骤1：列出量纲
        print("\n步骤1：确定各物理量的量纲")
        print("┌" + "─"*76 + "┐")
        print("│ 物理量 │   符号   │      量纲      │     单位     │")
        print("├" + "─"*76 + "┤")
        for symbol, info in self.variables.items():
            dim_str = self._dimension_to_string(info['dimension'])
            print(f"│ {info['name']:6s} │ {symbol:8s} │ {dim_str:14s} │ {info['unit']:12s} │")
        print("└" + "─"*76 + "┘")
        
        # 步骤2：选择重复变量
        print("\n步骤2：选择重复变量")
        print("选择准则：")
        print("  ① 包含所有基本量纲（M, L, T）")
        print("  ② 不能组成无量纲量")
        print("  ③ 通常选择：密度ρ、速度v、特征长度d")
        print("\n本题选择：ρ, v, d")
        
        # 步骤3：构造π项
        print("\n步骤3：构造π项")
        print("根据Buckingham定理，需要构造2个π项：")
        
        print("\n■ π₁项（包含F）")
        print("  设 π₁ = F · ρᵃ · vᵇ · dᶜ")
        print("  要求：[π₁] = M⁰L⁰T⁰（无量纲）")
        print("\n  量纲方程：")
        print("  [M¹L¹T⁻²] · [M¹L⁻³T⁰]ᵃ · [M⁰L¹T⁻¹]ᵇ · [M⁰L¹T⁰]ᶜ = M⁰L⁰T⁰")
        print("\n  分别对M, L, T列方程：")
        print("  M: 1 + a = 0       → a = -1")
        print("  L: 1 - 3a + b + c = 0")
        print("  T: -2 - b = 0      → b = -2")
        print("\n  代入a=-1, b=-2：")
        print("  L: 1 - 3(-1) + (-2) + c = 0")
        print("     1 + 3 - 2 + c = 0")
        print("     c = -2")
        print("\n  因此：π₁ = F · ρ⁻¹ · v⁻² · d⁻²")
        print("           = F / (ρv²d²)")
        
        print("\n■ π₂项（包含μ）")
        print("  设 π₂ = μ · ρᵃ · vᵇ · dᶜ")
        print("  量纲方程：")
        print("  [M¹L⁻¹T⁻¹] · [M¹L⁻³T⁰]ᵃ · [M⁰L¹T⁻¹]ᵇ · [M⁰L¹T⁰]ᶜ = M⁰L⁰T⁰")
        print("\n  分别对M, L, T列方程：")
        print("  M: 1 + a = 0       → a = -1")
        print("  L: -1 - 3a + b + c = 0")
        print("  T: -1 - b = 0      → b = -1")
        print("\n  代入a=-1, b=-1：")
        print("  L: -1 - 3(-1) + (-1) + c = 0")
        print("     -1 + 3 - 1 + c = 0")
        print("     c = -1")
        print("\n  因此：π₂ = μ · ρ⁻¹ · v⁻¹ · d⁻¹")
        print("           = μ / (ρvd)")
        print("           = 1 / Re  （雷诺数的倒数）")
        
        # 步骤4：建立无量纲关系
        print("\n步骤4：建立无量纲关系")
        print("根据Buckingham定理：")
        print("  π₁ = φ(π₂)")
        print("\n即：")
        print("  F/(ρv²d²) = φ(μ/(ρvd))")
        print("  F/(ρv²d²) = φ(1/Re)")
        print("\n也可写成：")
        print("  F = ρv²d² · φ(Re)")
        print("\n引入阻力系数CD：")
        print("  CD = F / (½ρv²A)")
        print("     = F / (½ρv²·πd²/4)")
        print("     = 8F / (πρv²d²)")
        print("\n则：CD = f(Re)")
        print("  这就是著名的阻力系数与雷诺数的关系！")
        
        # 步骤5：相似准则
        print("\n【相似准则识别】")
        print("从π₂项可以看出：")
        print("  Re = ρvd/μ = vd/ν")
        print("  这是雷诺数（Reynolds Number）")
        print("\n物理意义：")
        print("  Re = 惯性力/粘性力")
        print("  Re < 2300  → 层流")
        print("  Re > 4000  → 紊流")
        print("  2300 < Re < 4000 → 过渡流")
    
    def _dimension_to_string(self, dim):
        """将量纲列表转为字符串"""
        parts = []
        labels = ['M', 'L', 'T']
        for i, exp in enumerate(dim):
            if exp == 0:
                continue
            elif exp == 1:
                parts.append(labels[i])
            else:
                parts.append(f"{labels[i]}^{exp}")
        return ' '.join(parts) if parts else '1'
    
    def model_similarity(self, L_ratio=10, v_ratio=5):
        """模型相似分析"""
        print("\n【模型试验相似律】")
        print(f"已知：长度比 λL = {L_ratio}:1，流速比 λv = {v_ratio}:1")
        
        # 几何相似
        print("\n1. 几何相似（长度比）")
        print(f"  λL = Lp/Lm = {L_ratio}")
        print(f"  所有线性尺寸按相同比例缩放")
        
        # 运动相似
        print("\n2. 运动相似（流速比）")
        print(f"  λv = vp/vm = {v_ratio}")
        print(f"  时间比：λt = λL/λv = {L_ratio}/{v_ratio} = {L_ratio/v_ratio}")
        
        # 动力相似（雷诺数相似）
        print("\n3. 动力相似（雷诺数相似）")
        print("  要求：Rep = Rem")
        print("  即：(ρvd/μ)p = (ρvd/μ)m")
        print("\n  如果使用同种流体（ρp=ρm, μp=μm）：")
        print("  则：(vd)p = (vd)m")
        print(f"  λv·λd = 1")
        print(f"  但实际：λv·λL = {v_ratio} × {L_ratio} = {v_ratio*L_ratio} ≠ 1")
        print("  说明：雷诺数相似无法满足！")
        
        print("\n  实际操作：")
        print("  • 如果Re足够大（自模化区），Re相似不重要")
        print("  • 或者改变流体（如用水模拟空气）")
        print("  • 或者调整流速使λv = 1/λL")
        
        # 阻力比
        print("\n4. 阻力比计算")
        print("  根据量纲分析：F = ρv²d² · φ(Re)")
        print("  如果忽略Re影响（自模化）：")
        print("  λF = λρ · λv² · λL²")
        
        # 假设同种流体
        rho_ratio = 1  # 同种流体
        F_ratio = rho_ratio * v_ratio**2 * L_ratio**2
        
        print(f"\n  假设同种流体（λρ = 1）：")
        print(f"  λF = 1 × {v_ratio}² × {L_ratio}²")
        print(f"     = 1 × {v_ratio**2} × {L_ratio**2}")
        print(f"     = {F_ratio}")
        print(f"\n  即：Fp = {F_ratio} × Fm")
        print(f"  原型阻力是模型阻力的{F_ratio}倍")
        
        return F_ratio
    
    def similarity_criteria_summary(self):
        """相似准则总结"""
        print("\n【常见相似准则总结】")
        print("┌" + "─"*78 + "┐")
        print("│ 准则 │   名称   │      公式      │   物理意义   │      应用      │")
        print("├" + "─"*78 + "┤")
        
        criteria_order = ['Re', 'Fr', 'Eu', 'We', 'Ma']
        for symbol in criteria_order:
            info = self.similarity_criteria[symbol]
            print(f"│ {symbol:4s} │ {info['name']:8s} │ {info['formula']:14s} │ {info['meaning']:12s} │ {info['application']:14s} │")
        
        print("└" + "─"*78 + "┘")
        
        print("\n【详细说明】")
        
        print("\n1. 雷诺数 Re = ρvL/μ = vL/ν")
        print("   物理意义：惯性力/粘性力")
        print("   临界值：")
        print("     • 圆管：Re < 2300 层流，Re > 4000 紊流")
        print("     • 平板：Re_c ≈ 5×10⁵")
        print("   应用：流态判别、阻力计算、边界层分析")
        
        print("\n2. 弗劳德数 Fr = v/√(gL)")
        print("   物理意义：惯性力/重力")
        print("   临界值：")
        print("     • Fr < 1: 缓流（亚临界流）")
        print("     • Fr = 1: 临界流")
        print("     • Fr > 1: 急流（超临界流）")
        print("   应用：明渠流、波浪、船舶、溃坝")
        
        print("\n3. 欧拉数 Eu = Δp/(ρv²)")
        print("   物理意义：压力/惯性力")
        print("   相关：阻力系数 CD、升力系数 CL")
        print("   应用：压力分布、空化、流量测量")
        
        print("\n4. 韦伯数 We = ρv²L/σ")
        print("   物理意义：惯性力/表面张力")
        print("   临界值：We < 1 表面张力主导")
        print("   应用：液滴、气泡、喷雾、毛细现象")
        
        print("\n5. 马赫数 Ma = v/c")
        print("   物理意义：流速/声速")
        print("   临界值：")
        print("     • Ma < 0.3: 不可压缩流")
        print("     • 0.3 < Ma < 0.8: 亚音速")
        print("     • 0.8 < Ma < 1.2: 跨音速")
        print("     • Ma > 1.2: 超音速")
        print("   应用：高速气体流动、航空航天")
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：量纲分析流程
        ax1 = plt.subplot(2, 2, 1)
        self._plot_buckingham_process(ax1)
        
        # 子图2：相似准则图解
        ax2 = plt.subplot(2, 2, 2)
        self._plot_similarity_criteria(ax2)
        
        # 子图3：雷诺数与流态
        ax3 = plt.subplot(2, 2, 3)
        self._plot_reynolds_regime(ax3)
        
        # 子图4：模型试验示意
        ax4 = plt.subplot(2, 2, 4)
        self._plot_model_test(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_buckingham_process(self, ax):
        """绘制Buckingham定理流程图"""
        # 流程框
        steps = [
            '确定物理量\nn=5个',
            '确定基本量纲\nm=3个(M,L,T)',
            '计算π项数\nk=n-m=2个',
            '选择重复变量\nρ, v, d',
            '构造π项\nπ₁, π₂',
            '建立关系\nπ₁=φ(π₂)'
        ]
        
        y_positions = [0.9, 0.75, 0.6, 0.45, 0.3, 0.15]
        
        for i, (step, y) in enumerate(zip(steps, y_positions)):
            # 绘制框
            box = FancyBboxPatch((0.15, y-0.05), 0.7, 0.08,
                                boxstyle="round,pad=0.01",
                                facecolor='lightblue' if i % 2 == 0 else 'lightgreen',
                                edgecolor='black', linewidth=2)
            ax.add_patch(box)
            
            # 添加文字
            ax.text(0.5, y, step, ha='center', va='center',
                   fontsize=10, weight='bold')
            
            # 添加箭头
            if i < len(steps) - 1:
                ax.annotate('', xy=(0.5, y_positions[i+1]+0.03),
                           xytext=(0.5, y-0.05),
                           arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Buckingham π定理分析流程', fontsize=13, weight='bold', pad=10)
    
    def _plot_similarity_criteria(self, ax):
        """绘制相似准则示意图"""
        # 5个相似准则的图示
        criteria = ['Re', 'Fr', 'Eu', 'We', 'Ma']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        # 绘制5个圆圈
        theta = np.linspace(0, 2*np.pi, 6)
        radius = 0.35
        center_x, center_y = 0.5, 0.5
        
        for i, (criterion, color) in enumerate(zip(criteria, colors)):
            angle = theta[i]
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
            # 绘制圆圈
            circle = Circle((x, y), 0.12, facecolor=color, edgecolor='black',
                          linewidth=2, alpha=0.7)
            ax.add_patch(circle)
            
            # 添加文字
            info = self.similarity_criteria[criterion]
            ax.text(x, y, f'{criterion}\n{info["name"]}',
                   ha='center', va='center', fontsize=9, weight='bold')
        
        # 中心标题
        center_circle = Circle((center_x, center_y), 0.15,
                             facecolor='yellow', edgecolor='black',
                             linewidth=2, alpha=0.8)
        ax.add_patch(center_circle)
        ax.text(center_x, center_y, '相似\n准则',
               ha='center', va='center', fontsize=11, weight='bold')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('五大相似准则', fontsize=13, weight='bold', pad=10)
    
    def _plot_reynolds_regime(self, ax):
        """绘制雷诺数与流态关系"""
        # Re范围
        Re_ranges = [
            (0, 2300, '层流', 'green'),
            (2300, 4000, '过渡流', 'orange'),
            (4000, 10000, '紊流', 'red')
        ]
        
        y_base = 0.5
        height = 0.2
        
        # 绘制Re区间
        for Re_min, Re_max, label, color in Re_ranges:
            # 对数尺度映射到[0,1]
            x_min = np.log10(Re_min + 1) / np.log10(10001)
            x_max = np.log10(Re_max + 1) / np.log10(10001)
            width = x_max - x_min
            
            rect = Rectangle((x_min, y_base), width, height,
                           facecolor=color, edgecolor='black',
                           linewidth=2, alpha=0.6)
            ax.add_patch(rect)
            
            # 标签
            ax.text(x_min + width/2, y_base + height/2, label,
                   ha='center', va='center', fontsize=11, weight='bold',
                   color='white')
            
            # Re值标注
            if Re_min == 0:
                Re_text = '0'
            else:
                Re_text = f'{Re_min}'
            ax.text(x_min, y_base - 0.05, Re_text,
                   ha='center', va='top', fontsize=9)
        
        # 最后的Re值
        ax.text(1, y_base - 0.05, '10000+',
               ha='center', va='top', fontsize=9)
        
        # 临界Re标注
        ax.plot([np.log10(2301)/np.log10(10001)]*2, [y_base, y_base+height],
               'k--', linewidth=2)
        ax.text(np.log10(2301)/np.log10(10001), y_base+height+0.05,
               'Re_c1=2300', ha='center', fontsize=9, color='blue')
        
        ax.plot([np.log10(4001)/np.log10(10001)]*2, [y_base, y_base+height],
               'k--', linewidth=2)
        ax.text(np.log10(4001)/np.log10(10001), y_base+height+0.05,
               'Re_c2=4000', ha='center', fontsize=9, color='blue')
        
        # 标题
        ax.text(0.5, 0.85, '圆管流动的流态判别',
               ha='center', fontsize=11, weight='bold')
        
        # 公式
        ax.text(0.5, 0.2, 'Re = ρvd/μ = vd/ν',
               ha='center', fontsize=12,
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('雷诺数与流态', fontsize=13, weight='bold', pad=10)
    
    def _plot_model_test(self, ax):
        """绘制模型试验示意图"""
        # 原型（大）
        x1, y1 = 0.15, 0.6
        r1 = 0.12
        circle1 = Circle((x1, y1), r1, facecolor='lightblue',
                        edgecolor='black', linewidth=2)
        ax.add_patch(circle1)
        ax.text(x1, y1-r1-0.08, '原型\nd_p=1m',
               ha='center', fontsize=10, weight='bold')
        
        # 速度箭头
        ax.arrow(x1-0.25, y1, 0.08, 0, head_width=0.03, head_length=0.02,
                fc='red', ec='red', linewidth=2)
        ax.text(x1-0.25, y1+0.05, 'v_p=5m/s', fontsize=9, color='red')
        
        # 模型（小）
        x2, y2 = 0.15, 0.25
        r2 = 0.012 * 10  # 缩小10倍，但显示时放大以便可见
        circle2 = Circle((x2, y2), r2, facecolor='lightgreen',
                        edgecolor='black', linewidth=2)
        ax.add_patch(circle2)
        ax.text(x2, y2-r2-0.08, '模型\nd_m=0.1m',
               ha='center', fontsize=10, weight='bold')
        
        # 速度箭头
        ax.arrow(x2-0.25, y2, 0.08, 0, head_width=0.03, head_length=0.02,
                fc='blue', ec='blue', linewidth=2)
        ax.text(x2-0.25, y2+0.05, 'v_m=1m/s', fontsize=9, color='blue')
        
        # 相似关系
        ax.annotate('', xy=(x2+0.15, y2+0.1), xytext=(x1+0.15, y1-0.1),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
        
        ax.text(0.35, 0.43, '相似律\nλ_L=10:1\nλ_v=5:1\nλ_F=2500:1',
               ha='center', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 右侧公式
        formulas = [
            '几何相似: λ_L=L_p/L_m',
            '运动相似: λ_v=v_p/v_m',
            '动力相似: λ_F=λ_ρ·λ_v²·λ_L²'
        ]
        
        for i, formula in enumerate(formulas):
            ax.text(0.65, 0.75-i*0.12, formula, fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.7))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('模型试验相似律', fontsize=13, weight='bold', pad=10)


def test_problem_201():
    """测试题目201"""
    print("\n" + "="*80)
    print("开始量纲分析...")
    print("="*80)
    
    # 创建分析对象
    analysis = DimensionalAnalysis()
    
    # 模型相似分析
    F_ratio = analysis.model_similarity(L_ratio=10, v_ratio=5)
    
    # 相似准则总结
    analysis.similarity_criteria_summary()
    
    print("\n【最终答案】")
    print("="*80)
    print("(1) π项数量: k = n - m = 5 - 3 = 2个")
    print("(2) 无量纲关系式:")
    print("    π₁ = F/(ρv²d²)")
    print("    π₂ = μ/(ρvd) = 1/Re")
    print("    关系: π₁ = φ(π₂)")
    print("    即: F/(ρv²d²) = φ(1/Re)")
    print("(3) 相似准则: 雷诺数 Re = ρvd/μ")
    print("    物理意义: 惯性力/粘性力")
    print(f"(4) 阻力比: λ_F = {F_ratio}")
    print(f"    原型阻力是模型阻力的{F_ratio}倍")
    print("(5) 常见相似准则:")
    print("    Re - 惯性力/粘性力 - 管流、阻力")
    print("    Fr - 惯性力/重力 - 明渠流、波浪")
    print("    Eu - 压力/惯性力 - 压力分布")
    print("    We - 惯性力/表面张力 - 液滴、气泡")
    print("    Ma - 流速/声速 - 高速气体")
    print("="*80)
    
    # 可视化
    print("\n生成可视化图表...")
    fig = analysis.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_201_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_201_result.png")
    
    # 验证
    assert analysis.n == 5, "物理量个数应为5"
    assert analysis.m == 3, "基本量纲个数应为3"
    assert analysis.k == 2, "π项个数应为2"
    assert F_ratio == 2500, "阻力比应为2500"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("量纲分析是水力学的重要方法论！")
    print("• Buckingham π定理: k = n - m")
    print("• 量纲矩阵法构造π项")
    print("• 雷诺数Re：惯性力/粘性力")
    print("• 弗劳德数Fr：惯性力/重力")
    print("• 模型试验相似律：几何、运动、动力相似")
    print("• 应用：阻力预测、模型试验、公式推导")


if __name__ == "__main__":
    test_problem_201()
