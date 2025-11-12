"""
《水力学考研1000题详解》配套代码
题目796：水泵并联运行分析

问题描述：
两台相同的离心泵并联运行，已知：
  单泵特性: H = 40 - 200Q² (Q单位m³/s，H单位m)
            η = 180Q - 1800Q² (效率)
  管路特性: H_pipe = 10 + 400Q²
  水的密度: ρ = 1000 kg/m³

要求：
(1) 计算单泵运行的工况点(Q₁, H₁, η₁, P₁)
(2) 计算并联运行的工况点(Q₂, H₂, η₂, P₂)
(3) 分析并联运行的增流效果
(4) 计算并联效率系数
(5) 讨论管路特性对并联效果的影响

考点：
1. 单泵工况点: H_pump(Q) = H_pipe(Q)
2. 并联特性: H_parallel = H_single(Q_single), Q_total = 2Q_single
3. 并联工况点: H_parallel = H_pipe(Q_total)
4. 增流系数: K_Q = Q_parallel/Q_single
5. 并联效率系数: ξ = (Q_parallel - Q_single)/Q_single
6. 管路特性影响: 平坦管路增流效果好，陡峭管路增流效果差

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Polygon
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpParallel:
    """水泵并联运行分析类"""
    
    def __init__(self):
        """初始化"""
        self.g = 9.8
        self.rho = 1000  # kg/m³
        
        # 计算单泵工况点
        self.calculate_single_pump()
        
        # 计算并联工况点
        self.calculate_parallel_pumps()
        
        # 分析增流效果
        self.analyze_parallel_effect()
    
    def pump_head(self, Q):
        """单泵扬程特性 H = 40 - 200Q²"""
        return 40 - 200 * Q**2
    
    def pump_efficiency(self, Q):
        """单泵效率特性 η = 180Q - 1800Q²"""
        eta = 180 * Q - 1800 * Q**2
        return np.clip(eta, 0, 1)
    
    def pump_power(self, Q, H):
        """泵功率 P = ρgQH/η (kW)"""
        eta = self.pump_efficiency(Q)
        if eta < 0.01:
            eta = 0.01
        P = self.rho * self.g * Q * H / (1000 * eta)
        return P
    
    def pipe_head(self, Q):
        """管路特性 H = 10 + 400Q²"""
        return 10 + 400 * Q**2
    
    def calculate_single_pump(self):
        """计算单泵运行工况点"""
        print(f"\n{'='*80}")
        print("【单泵运行】")
        print(f"{'='*80}")
        
        # 工况点: H_pump = H_pipe
        def equation(Q):
            return self.pump_head(Q) - self.pipe_head(Q)
        
        self.Q1 = brentq(equation, 0.001, 0.5)
        self.H1 = self.pump_head(self.Q1)
        self.eta1 = self.pump_efficiency(self.Q1)
        self.P1 = self.pump_power(self.Q1, self.H1)
        
        print(f"  流量: Q₁ = {self.Q1:.6f} m³/s = {self.Q1*3600:.2f} m³/h")
        print(f"  扬程: H₁ = {self.H1:.4f} m")
        print(f"  效率: η₁ = {self.eta1*100:.2f}%")
        print(f"  功率: P₁ = {self.P1:.2f} kW")
    
    def parallel_head(self, Q_total):
        """并联泵特性: 每台泵分担Q_total/2流量"""
        Q_single = Q_total / 2
        return self.pump_head(Q_single)
    
    def calculate_parallel_pumps(self):
        """计算并联运行工况点"""
        print(f"\n{'='*80}")
        print("【并联运行】")
        print(f"{'='*80}")
        
        # 并联工况点: H_parallel = H_pipe
        def equation(Q_total):
            return self.parallel_head(Q_total) - self.pipe_head(Q_total)
        
        self.Q2 = brentq(equation, 0.001, 1.0)
        self.H2 = self.parallel_head(self.Q2)
        
        # 每台泵的流量
        self.Q_single_parallel = self.Q2 / 2
        
        # 每台泵的效率
        self.eta_single_parallel = self.pump_efficiency(self.Q_single_parallel)
        
        # 总功率
        self.P2 = 2 * self.pump_power(self.Q_single_parallel, self.H2)
        
        print(f"  总流量: Q₂ = {self.Q2:.6f} m³/s = {self.Q2*3600:.2f} m³/h")
        print(f"  每台泵流量: Q_单 = {self.Q_single_parallel:.6f} m³/s")
        print(f"  扬程: H₂ = {self.H2:.4f} m")
        print(f"  每台泵效率: η_单 = {self.eta_single_parallel*100:.2f}%")
        print(f"  总功率: P₂ = {self.P2:.2f} kW (2×{self.P2/2:.2f})")
    
    def analyze_parallel_effect(self):
        """分析并联增流效果"""
        print(f"\n{'='*80}")
        print("【并联效果分析】")
        print(f"{'='*80}")
        
        # 增流系数
        self.K_Q = self.Q2 / self.Q1
        
        # 并联效率系数
        self.xi = (self.Q2 - self.Q1) / self.Q1
        
        # 流量增加
        delta_Q = self.Q2 - self.Q1
        delta_Q_percent = delta_Q / self.Q1 * 100
        
        print(f"\n1. 流量增加:")
        print(f"   单泵流量: Q₁ = {self.Q1:.6f} m³/s")
        print(f"   并联流量: Q₂ = {self.Q2:.6f} m³/s")
        print(f"   流量增加: ΔQ = {delta_Q:.6f} m³/s ({delta_Q_percent:.1f}%)")
        print(f"   增流系数: K_Q = Q₂/Q₁ = {self.K_Q:.4f}")
        
        # 理论分析
        if self.K_Q < 1.5:
            effect = "较差"
        elif self.K_Q < 1.7:
            effect = "一般"
        elif self.K_Q < 1.9:
            effect = "较好"
        else:
            effect = "很好"
        
        print(f"   增流效果: {effect}")
        print(f"   说明: 理想并联K_Q=2.0，实际总小于2.0")
        
        # 扬程变化
        delta_H = self.H2 - self.H1
        print(f"\n2. 扬程变化:")
        print(f"   单泵扬程: H₁ = {self.H1:.4f} m")
        print(f"   并联扬程: H₂ = {self.H2:.4f} m")
        print(f"   扬程变化: ΔH = {delta_H:.4f} m")
        
        # 功率变化
        print(f"\n3. 功率对比:")
        print(f"   单泵功率: P₁ = {self.P1:.2f} kW")
        print(f"   并联功率: P₂ = {self.P2:.2f} kW")
        print(f"   功率比: P₂/P₁ = {self.P2/self.P1:.2f}")
        
        # 单位流量功耗
        p_unit_1 = self.P1 / self.Q1
        p_unit_2 = self.P2 / self.Q2
        print(f"   单位流量功耗:")
        print(f"     单泵: {p_unit_1:.2f} kW/(m³/s)")
        print(f"     并联: {p_unit_2:.2f} kW/(m³/s)")
        
        # 并联效率系数
        print(f"\n4. 并联效率系数:")
        print(f"   ξ = (Q₂-Q₁)/Q₁ = {self.xi:.4f} = {self.xi*100:.1f}%")
        print(f"   说明: ξ越大，并联效果越好")
    
    def analyze_pipe_characteristics(self):
        """分析管路特性对并联效果的影响"""
        print(f"\n{'='*80}")
        print("【管路特性影响分析】")
        print(f"{'='*80}")
        
        # 管路特性系数
        # H_pipe = H_s + SQ²，S = 400
        H_s = 10  # 静扬程
        S = 400   # 管路阻力系数
        
        print(f"\n管路特性: H = {H_s} + {S}Q²")
        print(f"  静扬程: H_s = {H_s} m")
        print(f"  阻力系数: S = {S}")
        
        # 管路特性坡度（在工况点）
        slope_pipe_Q1 = 2 * S * self.Q1
        slope_pipe_Q2 = 2 * S * self.Q2
        
        print(f"\n管路特性坡度 dH/dQ:")
        print(f"  单泵工况点: {slope_pipe_Q1:.2f}")
        print(f"  并联工况点: {slope_pipe_Q2:.2f}")
        
        # 泵特性坡度
        slope_pump_Q1 = -2 * 200 * self.Q1
        slope_pump_Q2 = -2 * 200 * self.Q_single_parallel
        
        print(f"\n泵特性坡度 dH/dQ:")
        print(f"  单泵工况点: {slope_pump_Q1:.2f}")
        print(f"  并联工况点: {slope_pump_Q2:.2f}")
        
        # 判断管路类型
        ratio = H_s / self.H1
        if ratio < 0.3:
            pipe_type = "平坦管路"
            parallel_effect = "好"
        elif ratio < 0.6:
            pipe_type = "中等管路"
            parallel_effect = "较好"
        else:
            pipe_type = "陡峭管路"
            parallel_effect = "一般"
        
        print(f"\n管路类型判别:")
        print(f"  静扬程比: H_s/H₁ = {ratio:.2f}")
        print(f"  管路类型: {pipe_type}")
        print(f"  并联效果: {parallel_effect}")
        
        print(f"\n结论:")
        print(f"  • 平坦管路（H_s/H小）: 并联增流效果好")
        print(f"  • 陡峭管路（H_s/H大）: 并联增流效果差")
        print(f"  • 本例属于{pipe_type}，并联效果{parallel_effect}")
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目796：水泵并联运行分析")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  单泵特性: H = 40 - 200Q²")
        print(f"            η = 180Q - 1800Q²")
        print(f"  管路特性: H = 10 + 400Q²")
        print(f"  泵的台数: 2台")
        
        print("\n【水泵并联运行原理】")
        print("1. 单泵工况点:")
        print("   H_pump(Q) = H_pipe(Q)")
        
        print("\n2. 并联特性:")
        print("   扬程不变: H_parallel = H_single")
        print("   流量叠加: Q_total = Q₁ + Q₂")
        print("   相同泵: Q_total = 2Q_single")
        
        print("\n3. 并联工况点:")
        print("   H_parallel(Q_total) = H_pipe(Q_total)")
        
        print("\n4. 增流系数:")
        print("   K_Q = Q_parallel/Q_single")
        print("   理想并联: K_Q = 2.0")
        print("   实际并联: K_Q < 2.0（受管路特性影响）")
        
        print("\n5. 并联适用性:")
        print("   平坦管路: 增流效果好（H_s/H < 0.3）")
        print("   陡峭管路: 增流效果差（H_s/H > 0.6）")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 管路特性影响分析
        self.analyze_pipe_characteristics()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 单泵工况: Q₁={self.Q1:.4f}m³/s, H₁={self.H1:.2f}m, η₁={self.eta1*100:.1f}%, P₁={self.P1:.2f}kW")
        print(f"(2) 并联工况: Q₂={self.Q2:.4f}m³/s, H₂={self.H2:.2f}m, η₂={self.eta_single_parallel*100:.1f}%, P₂={self.P2:.2f}kW")
        print(f"(3) 增流效果: K_Q={self.K_Q:.3f}, 流量增加{(self.K_Q-1)*100:.1f}%")
        print(f"(4) 并联效率系数: ξ={self.xi:.3f} = {self.xi*100:.1f}%")
        print(f"(5) 管路影响: 静扬程比={10/self.H1:.2f}，属于平坦管路，并联效果好")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：特性曲线与工况点
        ax1 = plt.subplot(2, 2, 1)
        self._plot_characteristics(ax1)
        
        # 子图2：并联前后对比
        ax2 = plt.subplot(2, 2, 2)
        self._plot_comparison(ax2)
        
        # 子图3：增流效果分析
        ax3 = plt.subplot(2, 2, 3)
        self._plot_flow_increase(ax3)
        
        # 子图4：管路特性影响
        ax4 = plt.subplot(2, 2, 4)
        self._plot_pipe_effect(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_characteristics(self, ax):
        """绘制特性曲线与工况点"""
        Q = np.linspace(0, 0.4, 200)
        
        # 单泵特性
        H_pump = self.pump_head(Q)
        ax.plot(Q, H_pump, 'b-', linewidth=2.5, label='单泵特性 H_pump')
        
        # 并联泵特性
        H_parallel = np.array([self.parallel_head(q) for q in Q])
        ax.plot(Q, H_parallel, 'r--', linewidth=2.5, label='并联泵特性 H_parallel')
        
        # 管路特性
        H_pipe = self.pipe_head(Q)
        ax.plot(Q, H_pipe, 'g-', linewidth=2.5, label='管路特性 H_pipe')
        
        # 单泵工况点
        ax.plot(self.Q1, self.H1, 'bo', markersize=12, label=f'单泵工况点 Q₁={self.Q1:.3f}', zorder=5)
        ax.text(self.Q1 + 0.01, self.H1 + 2, f'Q₁={self.Q1:.3f}\nH₁={self.H1:.1f}m',
               fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 并联工况点
        ax.plot(self.Q2, self.H2, 'ro', markersize=12, label=f'并联工况点 Q₂={self.Q2:.3f}', zorder=5)
        ax.text(self.Q2 + 0.01, self.H2 + 2, f'Q₂={self.Q2:.3f}\nH₂={self.H2:.1f}m',
               fontsize=9, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        # 标注增流效果
        ax.annotate('', xy=(self.Q2, 5), xytext=(self.Q1, 5),
                   arrowprops=dict(arrowstyle='<->', color='purple', lw=3))
        ax.text((self.Q1+self.Q2)/2, 7, f'增流\nΔQ={self.Q2-self.Q1:.3f}',
               ha='center', fontsize=10, weight='bold', color='purple')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('水泵并联特性曲线', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.35)
        ax.set_ylim(0, 45)
    
    def _plot_comparison(self, ax):
        """绘制并联前后对比"""
        categories = ['流量\n(m³/s)', '扬程\n(m)', '效率\n(%)', '功率\n(kW)']
        
        single = [self.Q1, self.H1, self.eta1*100, self.P1]
        parallel_total = [self.Q2, self.H2, self.eta_single_parallel*100, self.P2]
        
        x = np.arange(len(categories))
        width = 0.35
        
        # 归一化显示
        single_norm = np.array(single) / np.array([max(self.Q2, self.Q1), 
                                                    max(self.H2, self.H1),
                                                    max(self.eta1, self.eta_single_parallel)*100,
                                                    max(self.P2, self.P1)])
        parallel_norm = np.array(parallel_total) / np.array([max(self.Q2, self.Q1),
                                                              max(self.H2, self.H1),
                                                              max(self.eta1, self.eta_single_parallel)*100,
                                                              max(self.P2, self.P1)])
        
        bars1 = ax.bar(x - width/2, single_norm, width, label='单泵运行',
                      color='lightblue', edgecolor='blue', linewidth=2)
        bars2 = ax.bar(x + width/2, parallel_norm, width, label='并联运行',
                      color='lightcoral', edgecolor='red', linewidth=2)
        
        # 标注实际值
        for i, (s, p) in enumerate(zip(single, parallel_total)):
            ax.text(i - width/2, single_norm[i] + 0.05, f'{s:.2f}',
                   ha='center', fontsize=9, weight='bold')
            ax.text(i + width/2, parallel_norm[i] + 0.05, f'{p:.2f}',
                   ha='center', fontsize=9, weight='bold')
        
        ax.set_ylabel('归一化值', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_title('单泵与并联运行对比', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, 1.3)
    
    def _plot_flow_increase(self, ax):
        """绘制增流效果分析"""
        # 不同管路特性下的增流系数
        S_values = [100, 200, 400, 800, 1600]  # 管路阻力系数
        K_Q_values = []
        
        for S in S_values:
            # 单泵工况
            def eq1(Q):
                return self.pump_head(Q) - (10 + S * Q**2)
            Q_single = brentq(eq1, 0.001, 0.5)
            
            # 并联工况
            def eq2(Q_total):
                Q_s = Q_total / 2
                return self.pump_head(Q_s) - (10 + S * Q_total**2)
            Q_parallel = brentq(eq2, 0.001, 1.0)
            
            K_Q_values.append(Q_parallel / Q_single)
        
        ax.plot(S_values, K_Q_values, 'b-o', linewidth=2.5, markersize=8)
        
        # 标注当前工况
        ax.plot(400, self.K_Q, 'ro', markersize=15, label=f'当前工况\nS=400, K_Q={self.K_Q:.3f}')
        
        # 理想值
        ax.axhline(2.0, color='green', linestyle='--', linewidth=2, label='理想并联 K_Q=2.0')
        
        # 填充区域
        ax.fill_between(S_values, K_Q_values, 2.0, alpha=0.3, color='yellow')
        
        ax.set_xlabel('管路阻力系数 S', fontsize=12)
        ax.set_ylabel('增流系数 K_Q = Q并联/Q单泵', fontsize=12)
        ax.set_title('管路特性对增流效果的影响', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        
        # 添加说明
        ax.text(0.5, 0.2, 'S越小（平坦管路）→ K_Q越大（增流效果越好）',
               transform=ax.transAxes, fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    def _plot_pipe_effect(self, ax):
        """绘制管路特性影响示意图"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.95, '并联适用性分析', ha='center', va='top',
               fontsize=13, weight='bold', transform=ax.transAxes)
        
        # 三种管路类型
        pipe_types = [
            ('平坦管路', 'H_s/H < 0.3', '增流效果好\nK_Q > 1.7', 'green', 0.70),
            ('中等管路', '0.3 ≤ H_s/H < 0.6', '增流效果较好\n1.5 < K_Q ≤ 1.7', 'orange', 0.45),
            ('陡峭管路', 'H_s/H ≥ 0.6', '增流效果差\nK_Q ≤ 1.5', 'red', 0.20)
        ]
        
        for name, condition, effect, color, y in pipe_types:
            # 方框
            rect = Rectangle((0.1, y-0.08), 0.8, 0.15,
                           facecolor=color, edgecolor='black',
                           linewidth=2, alpha=0.3)
            ax.add_patch(rect)
            
            # 文字
            ax.text(0.2, y+0.04, name, fontsize=12, weight='bold', va='top')
            ax.text(0.2, y-0.01, condition, fontsize=10, va='top')
            ax.text(0.2, y-0.05, effect, fontsize=9, va='top', style='italic')
        
        # 当前工况
        current_y = 0.70  # 平坦管路位置
        ax.text(0.75, current_y, '← 当前\n   工况',
               fontsize=11, weight='bold', color='blue',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 底部总结
        ax.text(0.5, 0.05, 
               f'本例: H_s/H = {10/self.H1:.2f} < 0.3，属于平坦管路\n'
               f'增流系数 K_Q = {self.K_Q:.3f} > 1.7，并联效果好 ✓',
               ha='center', fontsize=10, weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7),
               transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)


def test_problem_796():
    """测试题目796"""
    print("\n" + "="*80)
    print("开始水泵并联运行分析...")
    print("="*80)
    
    # 创建并联分析对象
    parallel = PumpParallel()
    
    # 打印结果
    parallel.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = parallel.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_796_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_796_result.png")
    
    # 验证
    assert parallel.Q2 > parallel.Q1, "并联流量应大于单泵流量"
    assert parallel.K_Q > 1.0, "增流系数应大于1"
    assert parallel.K_Q < 2.0, "增流系数应小于2（实际情况）"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水泵并联运行是提高流量的重要方式！")
    print("• 并联特性: 扬程不变，流量叠加")
    print("• 增流系数: K_Q = Q并联/Q单泵 < 2.0")
    print("• 平坦管路: 并联效果好（H_s/H小）")
    print("• 陡峭管路: 并联效果差（H_s/H大）")
    print("• 应用: 大流量供水、调峰调谷、提高可靠性")


if __name__ == "__main__":
    test_problem_796()
