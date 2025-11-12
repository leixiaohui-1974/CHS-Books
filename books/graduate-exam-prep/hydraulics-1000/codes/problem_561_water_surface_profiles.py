"""
《水力学考研1000题详解》配套代码
题目561：水面曲线分类与绘制

问题描述：
矩形明渠，底宽b=3m，糙率n=0.020，底坡i=0.002。
渠道某断面流量Q=10m³/s，水深h=2.0m。
求：(1) 判断底坡类型（缓坡/临界坡/陡坡）
    (2) 判断水面曲线类型（12种之一）
    (3) 确定水深变化趋势
    (4) 绘制水面曲线示意图

考点：
1. 临界水深：h_c = ∛(q²/g)
2. 正常水深：Q = (1/n)AR^(2/3)i^(1/2)
3. 临界坡度：i_c = (nQ/(A_c·R_c^(2/3)))²
4. 底坡分类：i与i_c比较
5. 水面曲线12种分类（M、S、C、H、A）
6. 水深变化规律：dh/dx的正负判断

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
from scipy.optimize import fsolve

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WaterSurfaceProfile:
    """水面曲线分类类"""
    
    def __init__(self, b, n, i, Q, h, g=9.8):
        """
        初始化
        
        参数:
            b: 渠道底宽 (m)
            n: 糙率
            i: 底坡
            Q: 流量 (m³/s)
            h: 某断面水深 (m)
            g: 重力加速度 (m/s²)
        """
        self.b = b
        self.n = n
        self.i = i
        self.Q = Q
        self.h = h
        self.g = g
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算水面曲线类型"""
        # 1. 计算临界水深
        self.q = self.Q / self.b
        self.h_c = (self.q**2 / self.g)**(1/3)
        
        # 2. 计算正常水深（迭代求解）
        self.h_0 = self._solve_normal_depth()
        
        # 3. 计算临界坡度
        A_c = self.b * self.h_c
        P_c = self.b + 2 * self.h_c
        R_c = A_c / P_c
        self.i_c = (self.n * self.Q / (A_c * R_c**(2/3)))**2
        
        # 4. 判断底坡类型
        self._classify_slope()
        
        # 5. 判断水面曲线类型
        self._classify_profile()
        
        # 6. 计算dh/dx（水深变化率）
        self._calculate_slope_derivative()
        
        # 7. 生成水面曲线示意
        self._generate_profile_curve()
    
    def _solve_normal_depth(self):
        """迭代求解正常水深"""
        def f(h):
            if h <= 0:
                return 1e10
            A = self.b * h
            P = self.b + 2 * h
            R = A / P
            Q_calc = (1/self.n) * A * R**(2/3) * np.sqrt(self.i)
            return Q_calc - self.Q
        
        try:
            h0 = fsolve(f, self.h_c)[0]
            if h0 > 0:
                return h0
        except:
            pass
        
        return self.h_c
    
    def _classify_slope(self):
        """底坡分类"""
        if abs(self.i - self.i_c) / self.i_c < 0.01:
            self.slope_type = "临界坡"
            self.slope_symbol = "C"
        elif self.i < self.i_c:
            self.slope_type = "缓坡"
            self.slope_symbol = "M"
        elif self.i > self.i_c:
            self.slope_type = "陡坡"
            self.slope_symbol = "S"
        
        # 特殊情况
        if abs(self.i) < 1e-6:
            self.slope_type = "平坡"
            self.slope_symbol = "H"
        elif self.i < 0:
            self.slope_type = "反坡"
            self.slope_symbol = "A"
    
    def _classify_profile(self):
        """水面曲线分类"""
        # 根据底坡类型和水深位置分类
        if self.slope_symbol == "M":  # 缓坡
            if self.h > self.h_0:
                self.zone = 1
                self.profile_type = "M1"
                self.description = "壅水曲线"
                self.trend = "渐近接近h₀"
            elif self.h_c < self.h < self.h_0:
                self.zone = 2
                self.profile_type = "M2"
                self.description = "降水曲线"
                self.trend = "渐近接近h₀或h_c"
            else:  # h < h_c
                self.zone = 3
                self.profile_type = "M3"
                self.description = "急流曲线"
                self.trend = "渐近接近h_c"
        
        elif self.slope_symbol == "S":  # 陡坡
            if self.h > self.h_c:
                self.zone = 1
                self.profile_type = "S1"
                self.description = "壅水曲线"
                self.trend = "渐近接近h_c"
            elif self.h_0 < self.h < self.h_c:
                self.zone = 2
                self.profile_type = "S2"
                self.description = "降水曲线"
                self.trend = "渐近接近h₀或h_c"
            else:  # h < h_0
                self.zone = 3
                self.profile_type = "S3"
                self.description = "跌水曲线"
                self.trend = "渐近接近h₀"
        
        elif self.slope_symbol == "C":  # 临界坡
            if self.h > self.h_c:
                self.zone = 1
                self.profile_type = "C1"
                self.description = "壅水曲线"
                self.trend = "接近h_c"
            else:  # h < h_c
                self.zone = 3
                self.profile_type = "C3"
                self.description = "跌水曲线"
                self.trend = "离开h_c"
        
        elif self.slope_symbol == "H":  # 平坡
            if self.h > self.h_c:
                self.zone = 2
                self.profile_type = "H2"
                self.description = "平坡降水曲线"
                self.trend = "接近h_c"
            else:  # h < h_c
                self.zone = 3
                self.profile_type = "H3"
                self.description = "平坡跌水曲线"
                self.trend = "离开h_c"
        
        elif self.slope_symbol == "A":  # 反坡
            if self.h > self.h_c:
                self.zone = 2
                self.profile_type = "A2"
                self.description = "反坡壅水曲线"
                self.trend = "接近h_c"
            else:  # h < h_c
                self.zone = 3
                self.profile_type = "A3"
                self.description = "反坡跌水曲线"
                self.trend = "离开h_c"
    
    def _calculate_slope_derivative(self):
        """计算dh/dx"""
        # dh/dx = (i - J) / (1 - Fr²)
        # J = (n²v²) / (R^(4/3))
        A = self.b * self.h
        P = self.b + 2 * self.h
        R = A / P
        v = self.Q / A
        
        J = (self.n * v)**2 / R**(4/3)
        Fr = v / np.sqrt(self.g * self.h)
        
        if abs(1 - Fr**2) < 1e-6:
            self.dh_dx = 0  # 临界流
        else:
            self.dh_dx = (self.i - J) / (1 - Fr**2)
        
        self.J = J
        self.Fr = Fr
    
    def _generate_profile_curve(self):
        """生成水面曲线"""
        # 生成沿程水深变化
        L = 100  # 渠道长度 (m)
        n_points = 100
        
        if abs(self.dh_dx) < 1e-6:
            # 均匀流或临界流
            self.x_profile = np.linspace(0, L, n_points)
            self.h_profile = np.ones(n_points) * self.h
        else:
            # 简化模型：假设dh/dx为常数
            self.x_profile = np.linspace(0, L, n_points)
            self.h_profile = self.h + self.dh_dx * self.x_profile
            
            # 限制水深在合理范围
            self.h_profile = np.clip(self.h_profile, 0.1, max(self.h_0, self.h_c) * 2)
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目561：水面曲线分类与绘制")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"渠道底宽: b = {self.b} m")
        print(f"糙率: n = {self.n}")
        print(f"底坡: i = {self.i} = {self.i*1000:.2f}‰")
        print(f"流量: Q = {self.Q} m³/s")
        print(f"某断面水深: h = {self.h} m")
        
        print("\n【水面曲线基本概念】")
        print("1. 特征水深:")
        print("   • 临界水深h_c: 比能最小的水深")
        print("   • 正常水深h₀: 均匀流的水深")
        print("2. 底坡分类（根据i与i_c）:")
        print("   • 缓坡M: i < i_c，h₀ > h_c")
        print("   • 临界坡C: i = i_c，h₀ = h_c")
        print("   • 陡坡S: i > i_c，h₀ < h_c")
        print("   • 平坡H: i = 0")
        print("   • 反坡A: i < 0")
        print("3. 水面曲线分区:")
        print("   • 区域1: h > max(h₀, h_c)")
        print("   • 区域2: min(h₀, h_c) < h < max(h₀, h_c)")
        print("   • 区域3: h < min(h₀, h_c)")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算临界水深")
        print(f"单宽流量: q = Q/b = {self.Q}/{self.b} = {self.q:.4f} m²/s")
        print(f"临界水深: h_c = ∛(q²/g)")
        print(f"         = ∛({self.q}²/{self.g})")
        print(f"         = {self.h_c:.4f} m")
        
        print("\n步骤2：计算正常水深（迭代求解）")
        print(f"曼宁公式: Q = (1/n)AR^(2/3)√i")
        print(f"迭代求解得: h₀ = {self.h_0:.4f} m")
        
        print("\n步骤3：计算临界坡度")
        A_c = self.b * self.h_c
        P_c = self.b + 2 * self.h_c
        R_c = A_c / P_c
        print(f"临界断面: A_c = {A_c:.4f} m², R_c = {R_c:.4f} m")
        print(f"临界坡度: i_c = (nQ/(A_c·R_c^(2/3)))²")
        print(f"         = ({self.n}×{self.Q}/({A_c:.4f}×{R_c:.4f}^(2/3)))²")
        print(f"         = {self.i_c:.6f} = {self.i_c*1000:.3f}‰")
        
        print("\n步骤4：判断底坡类型")
        print(f"实际底坡: i = {self.i:.6f} = {self.i*1000:.3f}‰")
        print(f"临界坡度: i_c = {self.i_c:.6f} = {self.i_c*1000:.3f}‰")
        if self.slope_symbol == "M":
            print(f"i < i_c  →  {self.slope_type}（{self.slope_symbol}）")
            print(f"特点: h₀ = {self.h_0:.4f} m > h_c = {self.h_c:.4f} m")
        elif self.slope_symbol == "S":
            print(f"i > i_c  →  {self.slope_type}（{self.slope_symbol}）")
            print(f"特点: h₀ = {self.h_0:.4f} m < h_c = {self.h_c:.4f} m")
        else:
            print(f"i ≈ i_c  →  {self.slope_type}（{self.slope_symbol}）")
        
        print("\n步骤5：判断水深所在区域")
        print(f"当前水深: h = {self.h} m")
        print(f"临界水深: h_c = {self.h_c:.4f} m")
        print(f"正常水深: h₀ = {self.h_0:.4f} m")
        
        if self.slope_symbol == "M":
            if self.h > self.h_0:
                print(f"h > h₀ > h_c  →  区域1")
            elif self.h > self.h_c:
                print(f"h₀ > h > h_c  →  区域2")
            else:
                print(f"h₀ > h_c > h  →  区域3")
        elif self.slope_symbol == "S":
            if self.h > self.h_c:
                print(f"h > h_c > h₀  →  区域1")
            elif self.h > self.h_0:
                print(f"h_c > h > h₀  →  区域2")
            else:
                print(f"h_c > h₀ > h  →  区域3")
        
        print("\n步骤6：确定水面曲线类型")
        print(f"水面曲线: {self.profile_type}")
        print(f"类型: {self.description}")
        print(f"变化趋势: {self.trend}")
        
        print("\n步骤7：计算水深变化率dh/dx")
        print(f"当前流速: v = Q/A = {self.Q}/{self.b * self.h:.4f} = {self.Q/(self.b*self.h):.4f} m/s")
        print(f"弗劳德数: Fr = v/√(gh) = {self.Fr:.4f}")
        print(f"能坡: J = n²v²/R^(4/3) = {self.J:.6f}")
        print(f"底坡: i = {self.i:.6f}")
        print(f"dh/dx = (i - J) / (1 - Fr²)")
        print(f"      = ({self.i:.6f} - {self.J:.6f}) / (1 - {self.Fr:.4f}²)")
        print(f"      = {self.dh_dx:.6f}")
        
        if self.dh_dx > 0:
            print(f"dh/dx > 0  →  水深沿程增大（壅水）")
        elif self.dh_dx < 0:
            print(f"dh/dx < 0  →  水深沿程减小（降水）")
        else:
            print(f"dh/dx = 0  →  水深沿程不变（均匀流或临界流）")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 底坡类型: {self.slope_type}（{self.slope_symbol}）")
        print(f"    i = {self.i:.6f}，i_c = {self.i_c:.6f}")
        print(f"(2) 水面曲线: {self.profile_type}型")
        print(f"    {self.description}")
        print(f"(3) 水深变化: dh/dx = {self.dh_dx:.6f}")
        if self.dh_dx > 0:
            print(f"    沿程增大")
        else:
            print(f"    沿程减小")
        print(f"(4) 变化趋势: {self.trend}")
        print("="*80)
        
        print("\n【12种水面曲线总结】")
        print("="*80)
        print("缓坡M（h₀ > h_c）:")
        print("  • M1: h > h₀ > h_c，壅水曲线，dh/dx<0")
        print("  • M2: h₀ > h > h_c，降水曲线，dh/dx<0")
        print("  • M3: h₀ > h_c > h，急流曲线，dh/dx>0")
        print("\n陡坡S（h_c > h₀）:")
        print("  • S1: h > h_c > h₀，壅水曲线，dh/dx<0")
        print("  • S2: h_c > h > h₀，降水曲线，dh/dx>0")
        print("  • S3: h_c > h₀ > h，跌水曲线，dh/dx<0")
        print("\n临界坡C（h₀ = h_c）:")
        print("  • C1: h > h_c，壅水曲线，dh/dx<0")
        print("  • C3: h < h_c，跌水曲线，dh/dx>0")
        print("\n平坡H（i = 0）:")
        print("  • H2: h > h_c，降水曲线，dh/dx<0")
        print("  • H3: h < h_c，跌水曲线，dh/dx<0")
        print("\n反坡A（i < 0）:")
        print("  • A2: h > h_c，壅水曲线，dh/dx<0")
        print("  • A3: h < h_c，跌水曲线，dh/dx<0")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：水深位置示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_depth_zones(ax1)
        
        # 子图2：水面曲线剖面图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_profile(ax2)
        
        # 子图3：12种水面曲线分类图
        ax3 = plt.subplot(2, 2, 3)
        self._plot_classification(ax3)
        
        # 子图4：dh/dx分析图
        ax4 = plt.subplot(2, 2, 4)
        self._plot_dhdx_analysis(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_depth_zones(self, ax):
        """绘制水深分区示意图"""
        # 根据底坡类型确定分区
        if self.slope_symbol == "M":  # 缓坡
            zones = [self.h_0 * 1.5, self.h_0, self.h_c, 0]
            labels = ['区域1\nh>h₀', 'h₀', 'h_c', '区域3\nh<h_c']
            zone_labels_y = [(zones[0] + zones[1])/2, (zones[1] + zones[2])/2, (zones[2] + zones[3])/2]
            zone_labels_text = ['区域1\n(M1)', '区域2\n(M2)', '区域3\n(M3)']
        else:  # 陡坡
            zones = [self.h_c * 1.5, self.h_c, self.h_0, 0]
            labels = ['区域1\nh>h_c', 'h_c', 'h₀', '区域3\nh<h₀']
            zone_labels_y = [(zones[0] + zones[1])/2, (zones[1] + zones[2])/2, (zones[2] + zones[3])/2]
            zone_labels_text = ['区域1\n(S1)', '区域2\n(S2)', '区域3\n(S3)']
        
        # 绘制分区
        colors = ['lightcoral', 'lightyellow', 'lightblue']
        for i in range(len(zones) - 1):
            ax.fill_between([0, 1], [zones[i], zones[i]], [zones[i+1], zones[i+1]],
                           color=colors[i], alpha=0.5, edgecolor='black', linewidth=2)
        
        # 绘制特征水深线
        ax.plot([0, 1], [self.h_0, self.h_0], 'b--', linewidth=2, label=f'正常水深h₀={self.h_0:.3f}m')
        ax.plot([0, 1], [self.h_c, self.h_c], 'r--', linewidth=2, label=f'临界水深h_c={self.h_c:.3f}m')
        
        # 绘制当前水深
        ax.plot([0, 1], [self.h, self.h], 'g-', linewidth=3, label=f'当前水深h={self.h}m')
        ax.plot(0.5, self.h, 'go', markersize=15, zorder=5)
        
        # 标注分区
        for y, text in zip(zone_labels_y, zone_labels_text):
            ax.text(0.5, y, text, fontsize=11, ha='center', va='center',
                   weight='bold', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, zones[0] * 1.1)
        ax.set_ylabel('水深 (m)', fontsize=12)
        ax.set_title(f'水深分区示意图（{self.slope_type}）', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.set_xticks([])
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_profile(self, ax):
        """绘制水面曲线剖面图"""
        # 渠底
        L = 100
        x = np.linspace(0, L, 100)
        z_bottom = -self.i * x
        
        # 水面
        z_water = z_bottom + self.h_profile
        
        # 正常水位线
        z_normal = z_bottom + self.h_0
        
        # 临界水位线
        z_critical = z_bottom + self.h_c
        
        # 绘制
        ax.fill_between(x, z_bottom, z_water, color='lightblue', alpha=0.5, label='水体')
        ax.plot(x, z_water, 'b-', linewidth=2.5, label='水面曲线')
        ax.plot(x, z_normal, 'b--', linewidth=1.5, alpha=0.7, label=f'正常水位（h₀={self.h_0:.3f}m）')
        ax.plot(x, z_critical, 'r--', linewidth=1.5, alpha=0.7, label=f'临界水位（h_c={self.h_c:.3f}m）')
        ax.plot(x, z_bottom, 'k-', linewidth=2, label='渠底')
        
        # 标注曲线类型
        ax.text(L*0.5, z_water[50] + 0.3, f'{self.profile_type}型\n{self.description}',
               fontsize=12, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 标注底坡
        ax.text(L*0.9, z_bottom[-1] - 0.3, f'i={self.i:.4f}',
               fontsize=10, ha='right')
        
        ax.set_xlabel('沿程距离 x (m)', fontsize=12)
        ax.set_ylabel('高程 z (m)', fontsize=12)
        ax.set_title('水面曲线剖面图', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
    
    def _plot_classification(self, ax):
        """绘制12种水面曲线分类图"""
        # 简化示意图
        ax.text(0.5, 0.95, '水面曲线12种分类', fontsize=14, ha='center',
               weight='bold', transform=ax.transAxes)
        
        # 分类表
        classifications = [
            ('缓坡M', ['M1: h>h₀>h_c, 壅水', 'M2: h₀>h>h_c, 降水', 'M3: h₀>h_c>h, 急流']),
            ('陡坡S', ['S1: h>h_c>h₀, 壅水', 'S2: h_c>h>h₀, 降水', 'S3: h_c>h₀>h, 跌水']),
            ('临界坡C', ['C1: h>h_c, 壅水', 'C3: h<h_c, 跌水']),
            ('平坡H', ['H2: h>h_c, 降水', 'H3: h<h_c, 跌水']),
            ('反坡A', ['A2: h>h_c, 壅水', 'A3: h<h_c, 跌水'])
        ]
        
        y_start = 0.85
        y_step = 0.15
        
        for i, (slope_name, profiles) in enumerate(classifications):
            y = y_start - i * y_step
            
            # 底坡名称
            ax.text(0.05, y, slope_name, fontsize=11, weight='bold',
                   transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            
            # 曲线类型
            for j, profile in enumerate(profiles):
                # 检查是否为当前曲线
                is_current = profile.split(':')[0] == self.profile_type
                color = 'yellow' if is_current else 'white'
                linewidth = 2 if is_current else 1
                
                ax.text(0.25 + j * 0.25, y, profile, fontsize=9,
                       transform=ax.transAxes,
                       bbox=dict(boxstyle='round', facecolor=color, alpha=0.7,
                               edgecolor='red' if is_current else 'black',
                               linewidth=linewidth))
        
        # 标注当前曲线
        ax.text(0.5, 0.05, f'当前水面曲线: {self.profile_type}',
               fontsize=12, ha='center', weight='bold', color='red',
               transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def _plot_dhdx_analysis(self, ax):
        """绘制dh/dx分析图"""
        # 参数
        components = ['底坡\ni', '能坡\nJ', 'i-J', '1-Fr²', 'dh/dx']
        values = [self.i, self.J, self.i - self.J, 1 - self.Fr**2, self.dh_dx]
        colors = ['lightblue', 'lightcoral', 'lightgreen', 'lightyellow', 'orange']
        
        # 绘制柱状图
        bars = ax.bar(range(len(components)), values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.6f}',
                   ha='center', va='bottom' if val > 0 else 'top',
                   fontsize=10, weight='bold')
        
        # 零线
        ax.axhline(0, color='red', linestyle='--', linewidth=2, alpha=0.7)
        
        # 公式标注
        ax.text(0.5, 0.95, 'dh/dx = (i-J) / (1-Fr²)',
               fontsize=12, ha='center', weight='bold',
               transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # 结论标注
        if self.dh_dx > 0:
            conclusion = "dh/dx>0 → 水深沿程增大（壅水）"
            color = 'blue'
        elif self.dh_dx < 0:
            conclusion = "dh/dx<0 → 水深沿程减小（降水）"
            color = 'green'
        else:
            conclusion = "dh/dx=0 → 水深沿程不变（均匀流）"
            color = 'orange'
        
        ax.text(0.5, 0.05, conclusion,
               fontsize=11, ha='center', weight='bold', color=color,
               transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9,
                       edgecolor=color, linewidth=2))
        
        ax.set_xticks(range(len(components)))
        ax.set_xticklabels(components, fontsize=10)
        ax.set_ylabel('数值', fontsize=12)
        ax.set_title('水深变化率dh/dx分析', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)


def test_problem_561():
    """测试题目561"""
    # 已知条件
    b = 3.0             # 渠道底宽 (m)
    n = 0.020           # 糙率
    i = 0.002           # 底坡
    Q = 10.0            # 流量 (m³/s)
    h = 2.0             # 某断面水深 (m)
    
    # 创建计算对象
    profile = WaterSurfaceProfile(b, n, i, Q, h)
    
    # 打印结果
    profile.print_results()
    
    # 可视化
    fig = profile.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_561_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_561_result.png")
    
    # 验证答案（合理性检查）
    assert profile.h_c > 0, "临界水深必须为正"
    assert profile.h_0 > 0, "正常水深必须为正"
    assert profile.i_c > 0, "临界坡度必须为正"
    assert profile.profile_type in ['M1', 'M2', 'M3', 'S1', 'S2', 'S3', 
                                     'C1', 'C3', 'H2', 'H3', 'A2', 'A3'], "曲线类型必须合法"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水面曲线是明渠非均匀流的重要内容！")
    print("• 两个特征水深：h_c（临界水深）、h₀（正常水深）")
    print("• 五类底坡：M（缓坡）、S（陡坡）、C（临界坡）、H（平坡）、A（反坡）")
    print("• 十二种曲线：M1-M3、S1-S3、C1/C3、H2/H3、A2/A3")
    print("• dh/dx符号：决定水深沿程变化趋势")
    print("• 应用：渠道设计、水工建筑物布置、水面线计算")


if __name__ == "__main__":
    test_problem_561()
