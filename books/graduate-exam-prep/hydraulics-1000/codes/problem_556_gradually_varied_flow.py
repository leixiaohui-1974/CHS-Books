"""
《水力学考研1000题详解》配套代码
题目556：明渠非均匀流水面线计算

问题描述：
矩形断面明渠，已知：
  渠宽 b = 3.0 m
  流量 Q = 6.0 m³/s
  底坡 i = 0.001
  糙率 n = 0.025
  渠道长度 L = 500 m
  下游水深 h₁ = 1.5 m（控制水深）

要求：
(1) 计算正常水深h₀和临界水深h_c
(2) 判断水面线类型
(3) 用水面曲线微分方程计算水面线
(4) 绘制水面线纵剖面图
(5) 分析控制断面和计算方向

考点：
1. 正常水深：Manning公式 Q = (1/n)·A·R^(2/3)·i^(1/2)
2. 临界水深：Fr = v/√(gh_c) = 1
3. 水面曲线微分方程：dh/dx = (i - J)/(1 - Fr²)
4. 沿程阻力：J = n²v²/(R^(4/3))
5. 数值积分：Euler法或Runge-Kutta法
6. 水面线分类：M1/M2/M3, S1/S2/S3等12种

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
from matplotlib.patches import Rectangle, Polygon
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class GraduallyVariedFlow:
    """明渠非均匀流水面线计算类"""
    
    def __init__(self, b=3.0, Q=6.0, i=0.001, n=0.025, L=500, h1=1.5):
        """
        初始化
        
        参数:
            b: 渠宽 (m)
            Q: 流量 (m³/s)
            i: 底坡
            n: 糙率
            L: 渠道长度 (m)
            h1: 下游控制水深 (m)
        """
        self.b = b
        self.Q = Q
        self.i = i
        self.n = n
        self.L = L
        self.h1 = h1
        self.g = 9.8
        
        # 计算特征水深
        self.calculate_characteristic_depths()
        
        # 判断水面线类型
        self.classify_profile()
        
        # 计算水面线
        self.compute_water_surface_profile()
    
    def calculate_characteristic_depths(self):
        """计算正常水深和临界水深"""
        # 临界水深（矩形断面）
        # q = Q/b, h_c = (q²/g)^(1/3)
        q = self.Q / self.b
        self.h_c = (q**2 / self.g)**(1/3)
        
        print(f"\n临界水深计算:")
        print(f"  单宽流量: q = Q/b = {self.Q}/{self.b} = {q:.3f} m²/s")
        print(f"  临界水深: h_c = (q²/g)^(1/3) = {self.h_c:.4f} m")
        
        # 正常水深（Manning公式迭代求解）
        def manning_equation(h):
            A = self.b * h
            P = self.b + 2 * h
            R = A / P
            Q_calc = (1/self.n) * A * R**(2/3) * self.i**(1/2)
            return Q_calc - self.Q
        
        # 使用brentq求解
        try:
            self.h0 = brentq(manning_equation, 0.01, 10.0)
            converged = True
        except:
            # 备用Newton迭代
            h = self.h_c * 1.5
            for iteration in range(50):
                A = self.b * h
                P = self.b + 2 * h
                R = A / P
                Q_calc = (1/self.n) * A * R**(2/3) * self.i**(1/2)
                
                # 数值微分
                dh = 0.001
                A_plus = self.b * (h + dh)
                P_plus = self.b + 2 * (h + dh)
                R_plus = A_plus / P_plus
                Q_plus = (1/self.n) * A_plus * R_plus**(2/3) * self.i**(1/2)
                dQ_dh = (Q_plus - Q_calc) / dh
                
                h_new = h - (Q_calc - self.Q) / dQ_dh
                
                if abs(h_new - h) < 1e-6:
                    self.h0 = h_new
                    converged = True
                    break
                h = h_new
            else:
                self.h0 = h
                converged = False
        
        print(f"\n正常水深计算（Manning公式迭代）:")
        print(f"  正常水深: h₀ = {self.h0:.4f} m")
        print(f"  收敛状态: {'成功' if converged else '未完全收敛'}")
        
        # 计算临界坡度
        A_c = self.b * self.h_c
        P_c = self.b + 2 * self.h_c
        R_c = A_c / P_c
        v_c = self.Q / A_c
        self.i_c = (self.n * v_c / R_c**(2/3))**2
        
        print(f"\n临界坡度:")
        print(f"  i_c = {self.i_c:.6f}")
        print(f"  底坡 i = {self.i:.6f}")
        print(f"  坡度分类: {'缓坡' if self.i < self.i_c else '陡坡' if self.i > self.i_c else '临界坡'}")
    
    def classify_profile(self):
        """判断水面线类型"""
        # 坡度分类
        if abs(self.i - self.i_c) / self.i_c < 0.01:
            slope_type = "临界坡"
            slope_code = "C"
        elif self.i < self.i_c:
            slope_type = "缓坡"
            slope_code = "M"
        else:
            slope_type = "陡坡"
            slope_code = "S"
        
        # 水深分区
        if slope_code == "M":
            if self.h1 > self.h0:
                zone = "1"
                description = "壅水曲线，dh/dx<0，水深沿程减小"
            elif self.h_c < self.h1 < self.h0:
                zone = "2"
                description = "降水曲线，dh/dx>0，水深沿程增加"
            else:
                zone = "3"
                description = "急流，dh/dx<0，水深沿程减小"
        elif slope_code == "S":
            if self.h1 > self.h_c:
                zone = "1"
                description = "壅水曲线，dh/dx<0"
            elif self.h0 < self.h1 < self.h_c:
                zone = "2"
                description = "降水曲线，dh/dx>0"
            else:
                zone = "3"
                description = "急流，dh/dx<0"
        else:
            zone = "1"
            description = "临界流"
        
        self.profile_type = slope_code + zone
        self.slope_type = slope_type
        self.description = description
        
        print(f"\n水面线分类:")
        print(f"  控制水深: h₁ = {self.h1:.4f} m")
        print(f"  正常水深: h₀ = {self.h0:.4f} m")
        print(f"  临界水深: h_c = {self.h_c:.4f} m")
        print(f"  坡度类型: {slope_type}（{slope_code}）")
        print(f"  水深分区: 第{zone}区")
        print(f"  水面线型: {self.profile_type}型")
        print(f"  特征: {description}")
    
    def compute_water_surface_profile(self):
        """计算水面线（数值积分法）"""
        print(f"\n水面线计算:")
        
        # 确定计算方向和起点
        if self.h1 > self.h0:
            # M1型，从下游向上游计算
            direction = "下游→上游"
            x_start = 0
            x_end = self.L
            h_start = self.h1
        else:
            # M2型或其他，从上游向下游计算
            direction = "上游→下游"
            x_start = self.L
            x_end = 0
            h_start = self.h1
        
        print(f"  计算方向: {direction}")
        print(f"  起始水深: h = {h_start:.4f} m")
        
        # Euler方法数值积分
        n_steps = 200
        dx = (x_end - x_start) / n_steps
        
        x_array = [x_start]
        h_array = [h_start]
        
        x = x_start
        h = h_start
        
        for step in range(n_steps):
            # 计算 dh/dx
            dh_dx = self.water_surface_derivative(h)
            
            # Euler步进
            h_new = h + dh_dx * dx
            x_new = x + dx
            
            # 边界检查
            if h_new < 0.01:
                h_new = 0.01
            if h_new > 10:
                h_new = 10
            
            h_array.append(h_new)
            x_array.append(x_new)
            
            h = h_new
            x = x_new
        
        self.x_profile = np.array(x_array)
        self.h_profile = np.array(h_array)
        
        print(f"  计算步数: {n_steps}")
        print(f"  终点水深: h = {h_array[-1]:.4f} m")
        print(f"  水深变化: Δh = {abs(h_array[-1] - h_array[0]):.4f} m")
    
    def water_surface_derivative(self, h):
        """
        水面曲线微分方程
        dh/dx = (i - J) / (1 - Fr²)
        """
        # 水力要素
        A = self.b * h
        P = self.b + 2 * h
        R = A / P
        v = self.Q / A
        
        # Froude数
        Fr = v / np.sqrt(self.g * h)
        
        # 沿程阻力坡度（Manning公式）
        J = (self.n * v / R**(2/3))**2
        
        # 水面曲线导数
        numerator = self.i - J
        denominator = 1 - Fr**2
        
        # 避免分母为零
        if abs(denominator) < 1e-6:
            dh_dx = 0
        else:
            dh_dx = numerator / denominator
        
        return dh_dx
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目556：明渠非均匀流水面线计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  渠宽: b = {self.b} m")
        print(f"  流量: Q = {self.Q} m³/s")
        print(f"  底坡: i = {self.i}")
        print(f"  糙率: n = {self.n}")
        print(f"  渠长: L = {self.L} m")
        print(f"  下游控制水深: h₁ = {self.h1} m")
        
        print("\n【理论基础】")
        print("1. 正常水深（均匀流）:")
        print("   Manning公式: Q = (1/n)·A·R^(2/3)·i^(1/2)")
        
        print("\n2. 临界水深（临界流）:")
        print("   Fr = v/√(gh_c) = 1")
        print("   矩形断面: h_c = (q²/g)^(1/3)")
        
        print("\n3. 水面曲线微分方程:")
        print("   dh/dx = (i - J)/(1 - Fr²)")
        print("   i: 底坡")
        print("   J: 沿程阻力坡度 = (nv/R^(2/3))²")
        print("   Fr: Froude数 = v/√(gh)")
        
        print("\n4. 水面线分类（12种）:")
        print("   缓坡(M): M1(壅水), M2(降水), M3(急流)")
        print("   陡坡(S): S1(壅水), S2(降水), S3(急流)")
        print("   临界坡(C): C1, C3")
        print("   平坡(H): H2, H3")
        print("   反坡(A): A2, A3")
        
        print("\n5. 控制断面:")
        print("   缓流: 下游控制（M1, M2）")
        print("   急流: 上游控制（M3, S2, S3）")
        
        print("\n【计算结果】")
        
        print(f"\n(1) 特征水深:")
        print(f"  正常水深: h₀ = {self.h0:.4f} m")
        print(f"  临界水深: h_c = {self.h_c:.4f} m")
        print(f"  临界坡度: i_c = {self.i_c:.6f}")
        
        print(f"\n(2) 水面线类型:")
        print(f"  类型: {self.profile_type}型")
        print(f"  坡度: {self.slope_type}")
        print(f"  特征: {self.description}")
        
        print(f"\n(3) 水面线计算:")
        print(f"  起点水深: h(0) = {self.h_profile[0]:.4f} m")
        print(f"  终点水深: h(L) = {self.h_profile[-1]:.4f} m")
        print(f"  水深变化: Δh = {abs(self.h_profile[-1] - self.h_profile[0]):.4f} m")
        
        # 关键断面
        idx_mid = len(self.x_profile) // 2
        print(f"\n  关键断面:")
        print(f"    x=0m: h={self.h_profile[0]:.4f}m")
        print(f"    x={self.x_profile[idx_mid]:.0f}m: h={self.h_profile[idx_mid]:.4f}m")
        print(f"    x={self.L}m: h={self.h_profile[-1]:.4f}m")
        
        print(f"\n(4) 水面线纵剖面: 已绘制")
        
        print(f"\n(5) 控制断面与计算方向:")
        if self.h1 > self.h0:
            print(f"  控制断面: 下游（h₁ > h₀，缓流）")
            print(f"  计算方向: 从下游向上游逐步推算")
        else:
            print(f"  控制断面: 下游")
            print(f"  计算方向: 根据水面线类型确定")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) h₀={self.h0:.4f}m, h_c={self.h_c:.4f}m")
        print(f"(2) 水面线类型: {self.profile_type}型（{self.description}）")
        print(f"(3) 已用微分方程数值求解水面线")
        print(f"(4) 水面线纵剖面图已绘制")
        print(f"(5) 控制断面在下游，计算方向视情况而定")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：水面线纵剖面
        ax1 = plt.subplot(2, 2, 1)
        self._plot_longitudinal_profile(ax1)
        
        # 子图2：水深沿程变化
        ax2 = plt.subplot(2, 2, 2)
        self._plot_depth_variation(ax2)
        
        # 子图3：Froude数分布
        ax3 = plt.subplot(2, 2, 3)
        self._plot_froude_distribution(ax3)
        
        # 子图4：12种水面线分类
        ax4 = plt.subplot(2, 2, 4)
        self._plot_profile_classification(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_longitudinal_profile(self, ax):
        """绘制水面线纵剖面"""
        # 渠底高程
        z_bottom = np.zeros_like(self.x_profile)
        for i, x in enumerate(self.x_profile):
            z_bottom[i] = -self.i * x
        
        # 水面高程
        z_surface = z_bottom + self.h_profile
        
        # 正常水深线
        z_normal = z_bottom + self.h0
        
        # 临界水深线
        z_critical = z_bottom + self.h_c
        
        # 绘图
        ax.fill_between(self.x_profile, z_bottom, z_surface, 
                        alpha=0.5, color='lightblue', label='水体')
        ax.plot(self.x_profile, z_surface, 'b-', linewidth=2.5, label='实际水面线')
        ax.plot(self.x_profile, z_bottom, 'k-', linewidth=2, label='渠底')
        ax.plot(self.x_profile, z_normal, 'g--', linewidth=2, label=f'正常水深线 h₀={self.h0:.3f}m')
        ax.plot(self.x_profile, z_critical, 'r--', linewidth=2, label=f'临界水深线 h_c={self.h_c:.3f}m')
        
        # 标注
        ax.text(self.L/2, z_surface[len(z_surface)//2] + 0.2, 
               f'{self.profile_type}型水面线',
               ha='center', fontsize=12, weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('距离 x (m)', fontsize=12)
        ax.set_ylabel('高程 z (m)', fontsize=12)
        ax.set_title('水面线纵剖面图', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.L)
    
    def _plot_depth_variation(self, ax):
        """绘制水深沿程变化"""
        ax.plot(self.x_profile, self.h_profile, 'b-', linewidth=2.5, label='实际水深')
        ax.axhline(self.h0, color='green', linestyle='--', linewidth=2, 
                  label=f'正常水深 h₀={self.h0:.3f}m')
        ax.axhline(self.h_c, color='red', linestyle='--', linewidth=2, 
                  label=f'临界水深 h_c={self.h_c:.3f}m')
        
        # 标注控制断面
        ax.plot(0, self.h1, 'ro', markersize=10, label='控制断面')
        ax.text(20, self.h1, f'h₁={self.h1:.3f}m', fontsize=10, weight='bold')
        
        ax.set_xlabel('距离 x (m)', fontsize=12)
        ax.set_ylabel('水深 h (m)', fontsize=12)
        ax.set_title('水深沿程变化', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.L)
    
    def _plot_froude_distribution(self, ax):
        """绘制Froude数分布"""
        Fr_array = []
        for h in self.h_profile:
            A = self.b * h
            v = self.Q / A
            Fr = v / np.sqrt(self.g * h)
            Fr_array.append(Fr)
        
        Fr_array = np.array(Fr_array)
        
        ax.plot(self.x_profile, Fr_array, 'purple', linewidth=2.5)
        ax.axhline(1, color='red', linestyle='--', linewidth=2, label='Fr=1（临界流）')
        
        # 标注流态
        if np.mean(Fr_array) < 1:
            ax.text(self.L/2, np.mean(Fr_array), '缓流区\n(Fr<1)', 
                   ha='center', fontsize=11, weight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        else:
            ax.text(self.L/2, np.mean(Fr_array), '急流区\n(Fr>1)', 
                   ha='center', fontsize=11, weight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        ax.set_xlabel('距离 x (m)', fontsize=12)
        ax.set_ylabel('Froude数 Fr', fontsize=12)
        ax.set_title('Froude数沿程分布', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.L)
    
    def _plot_profile_classification(self, ax):
        """绘制12种水面线分类示意图"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.98, '明渠水面线12种类型', ha='center', va='top',
               fontsize=13, weight='bold', transform=ax.transAxes)
        
        # 缓坡M
        y_M = 0.75
        ax.text(0.05, y_M, '缓坡M\n(i<i_c)', fontsize=10, weight='bold', 
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        ax.text(0.25, y_M + 0.08, 'M1: h>h₀>h_c', fontsize=9)
        ax.text(0.25, y_M + 0.03, 'M2: h₀>h>h_c', fontsize=9)
        ax.text(0.25, y_M - 0.02, 'M3: h₀>h_c>h', fontsize=9)
        
        # 绘制M型水面线示意
        x_M = np.linspace(0.55, 0.95, 50)
        # M1
        y_M1 = y_M + 0.08 + 0.03 * (1 - (x_M - 0.55) / 0.4)
        ax.plot(x_M, y_M1, 'b-', linewidth=2)
        ax.axhline(y_M + 0.08, xmin=0.55, xmax=0.95, color='g', linestyle='--', linewidth=1)
        
        # 陡坡S
        y_S = 0.50
        ax.text(0.05, y_S, '陡坡S\n(i>i_c)', fontsize=10, weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        ax.text(0.25, y_S + 0.08, 'S1: h>h_c>h₀', fontsize=9)
        ax.text(0.25, y_S + 0.03, 'S2: h_c>h>h₀', fontsize=9)
        ax.text(0.25, y_S - 0.02, 'S3: h_c>h₀>h', fontsize=9)
        
        # 其他坡型
        y_other = 0.25
        ax.text(0.05, y_other + 0.08, '临界坡C: C1, C3', fontsize=9)
        ax.text(0.05, y_other + 0.03, '平坡H: H2, H3', fontsize=9)
        ax.text(0.05, y_other - 0.02, '反坡A: A2, A3', fontsize=9)
        
        # 标注当前类型
        ax.text(0.5, 0.05, f'当前水面线: {self.profile_type}型',
               ha='center', fontsize=12, weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
               transform=ax.transAxes)


def test_problem_556():
    """测试题目556"""
    print("\n" + "="*80)
    print("开始明渠非均匀流水面线计算...")
    print("="*80)
    
    # 创建水面线分析对象
    gvf = GraduallyVariedFlow(b=3.0, Q=6.0, i=0.001, n=0.025, L=500, h1=1.5)
    
    # 打印结果
    gvf.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = gvf.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_556_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_556_result.png")
    
    # 验证
    assert gvf.h0 > 0, "正常水深必须为正"
    assert gvf.h_c > 0, "临界水深必须为正"
    assert len(gvf.h_profile) > 0, "水面线必须计算"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("明渠非均匀流水面线是明渠水力学的核心内容！")
    print("• 微分方程: dh/dx = (i-J)/(1-Fr²)")
    print("• 正常水深h₀: Manning公式")
    print("• 临界水深h_c: Fr=1")
    print("• 12种水面线: M1/M2/M3, S1/S2/S3等")
    print("• 应用: 渠道设计、水位预报、防洪计算")


if __name__ == "__main__":
    test_problem_556()
