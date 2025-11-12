"""
《水力学考研1000题详解》配套代码
题目781：水泵并联与串联运行

问题描述：
某泵站有两台相同的离心泵，其单台特性曲线为：
  H = 50 - 1000Q²  (H: m, Q: m³/s)
  η = -200Q² + 20Q  (效率)
管路特性曲线为：H = 10 + 500Q²

要求：
(1) 计算单泵运行时的工况点（Q、H、η）
(2) 计算两泵并联运行时的工况点
(3) 计算两泵串联运行时的工况点
(4) 比较三种运行方式的效率和经济性
(5) 分析不同运行方式的适用条件

考点：
1. 水泵特性曲线：Q-H, Q-η, Q-P
2. 管路特性曲线：H = H₀ + SQ²
3. 并联运行：Q总 = Q₁ + Q₂, H相同
4. 串联运行：H总 = H₁ + H₂, Q相同
5. 工况点：泵特性曲线与管路特性曲线交点
6. 效率分析与经济性评价

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpSeriesParallel:
    """水泵串并联运行分析类"""
    
    def __init__(self):
        """初始化"""
        # 单泵特性曲线参数
        self.H0 = 50      # 关死扬程 (m)
        self.a = 1000     # H-Q曲线系数
        
        # 效率曲线参数
        self.b1 = -200    # η-Q曲线系数1
        self.b2 = 20      # η-Q曲线系数2
        
        # 管路特性曲线参数
        self.H_static = 10  # 静扬程 (m)
        self.S = 500      # 管路阻力系数
        
        # 计算三种工况
        self.calculate_single_pump()
        self.calculate_parallel()
        self.calculate_series()
    
    def pump_head_curve(self, Q):
        """单泵扬程曲线"""
        return self.H0 - self.a * Q**2
    
    def pump_efficiency_curve(self, Q):
        """单泵效率曲线"""
        eta = self.b1 * Q**2 + self.b2 * Q
        return np.clip(eta, 0, 100)  # 限制在0-100%
    
    def pipe_head_curve(self, Q):
        """管路特性曲线"""
        return self.H_static + self.S * Q**2
    
    def calculate_single_pump(self):
        """计算单泵运行工况"""
        # 工况点：泵特性 = 管路特性
        # H0 - a*Q² = H_static + S*Q²
        # (a + S)*Q² = H0 - H_static
        
        def equation(Q):
            return self.pump_head_curve(Q) - self.pipe_head_curve(Q)
        
        # 求解
        Q_initial = 0.1
        self.Q_single = fsolve(equation, Q_initial)[0]
        self.H_single = self.pump_head_curve(self.Q_single)
        self.eta_single = self.pump_efficiency_curve(self.Q_single)
        
        # 功率（假设水的重度γ=9800 N/m³）
        gamma = 9800
        self.P_single = gamma * self.Q_single * self.H_single / (self.eta_single/100) / 1000  # kW
    
    def calculate_parallel(self):
        """计算并联运行工况"""
        # 并联：Q总 = 2Q单, H相同
        # 并联泵特性：H = H0 - a*(Q/2)² = H0 - a*Q²/4
        # 工况点：H0 - a*Q²/4 = H_static + S*Q²
        # Q²(a/4 + S) = H0 - H_static
        
        def equation(Q):
            H_parallel_pump = self.H0 - self.a * (Q/2)**2
            H_pipe = self.pipe_head_curve(Q)
            return H_parallel_pump - H_pipe
        
        Q_initial = 0.2
        self.Q_parallel = fsolve(equation, Q_initial)[0]
        self.H_parallel = self.pipe_head_curve(self.Q_parallel)
        
        # 每台泵的流量
        self.Q_parallel_each = self.Q_parallel / 2
        
        # 每台泵的效率
        self.eta_parallel_each = self.pump_efficiency_curve(self.Q_parallel_each)
        
        # 总功率
        gamma = 9800
        self.P_parallel = 2 * gamma * self.Q_parallel_each * self.H_parallel / (self.eta_parallel_each/100) / 1000
    
    def calculate_series(self):
        """计算串联运行工况"""
        # 串联：H总 = 2H单, Q相同
        # 串联泵特性：H = 2(H0 - a*Q²) = 2*H0 - 2*a*Q²
        # 工况点：2*H0 - 2*a*Q² = H_static + S*Q²
        # Q²(2*a + S) = 2*H0 - H_static
        
        def equation(Q):
            H_series_pump = 2 * self.pump_head_curve(Q)
            H_pipe = self.pipe_head_curve(Q)
            return H_series_pump - H_pipe
        
        Q_initial = 0.15
        self.Q_series = fsolve(equation, Q_initial)[0]
        self.H_series = self.pipe_head_curve(self.Q_series)
        
        # 每台泵的扬程
        self.H_series_each = self.H_series / 2
        
        # 每台泵的效率
        self.eta_series = self.pump_efficiency_curve(self.Q_series)
        
        # 总功率
        gamma = 9800
        self.P_series = 2 * gamma * self.Q_series * self.H_series_each / (self.eta_series/100) / 1000
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目781：水泵并联与串联运行")
        print("="*80)
        
        print("\n【已知条件】")
        print("单泵特性曲线:")
        print(f"  扬程: H = {self.H0} - {self.a}Q²  (m)")
        print(f"  效率: η = {self.b1}Q² + {self.b2}Q  (%)")
        print("\n管路特性曲线:")
        print(f"  H = {self.H_static} + {self.S}Q²  (m)")
        print(f"  静扬程: H₀ = {self.H_static} m")
        print(f"  阻力系数: S = {self.S}")
        
        print("\n【水泵串并联基本概念】")
        print("1. 工况点:")
        print("   • 泵特性曲线与管路特性曲线的交点")
        print("   • H_泵(Q) = H_管(Q)")
        
        print("\n2. 并联运行:")
        print("   • 特点: Q总 = Q₁ + Q₂, H相同")
        print("   • 优点: 增大流量")
        print("   • 适用: 管路阻力较小，需要大流量")
        
        print("\n3. 串联运行:")
        print("   • 特点: H总 = H₁ + H₂, Q相同")
        print("   • 优点: 增大扬程")
        print("   • 适用: 管路阻力较大，需要高扬程")
        
        print("\n【计算过程】")
        
        # (1) 单泵运行
        print("\n(1) 单泵运行工况点")
        print("    工况方程: H_泵 = H_管")
        print(f"    {self.H0} - {self.a}Q² = {self.H_static} + {self.S}Q²")
        print(f"    {self.a + self.S}Q² = {self.H0 - self.H_static}")
        print(f"    Q² = {(self.H0 - self.H_static)/(self.a + self.S):.6f}")
        print(f"    Q = {self.Q_single:.4f} m³/s")
        print(f"\n    扬程: H = {self.H_single:.2f} m")
        print(f"    效率: η = {self.eta_single:.2f}%")
        print(f"    功率: P = {self.P_single:.2f} kW")
        
        # (2) 并联运行
        print("\n(2) 并联运行工况点")
        print("    并联特性: Q总 = Q₁ + Q₂ = 2Q单, H相同")
        print("    并联泵曲线: H = H₀ - a(Q/2)²")
        print(f"    {self.H0} - {self.a}(Q/2)² = {self.H_static} + {self.S}Q²")
        print(f"    {self.H0} - {self.a/4}Q² = {self.H_static} + {self.S}Q²")
        print(f"    Q = {self.Q_parallel:.4f} m³/s （总流量）")
        print(f"    每台泵流量: Q = {self.Q_parallel_each:.4f} m³/s")
        print(f"\n    扬程: H = {self.H_parallel:.2f} m")
        print(f"    每台泵效率: η = {self.eta_parallel_each:.2f}%")
        print(f"    总功率: P = {self.P_parallel:.2f} kW")
        
        # 与单泵比较
        Q_increase = (self.Q_parallel / self.Q_single - 1) * 100
        print(f"\n    与单泵比较:")
        print(f"    流量增加: {Q_increase:.1f}%")
        print(f"    扬程变化: {self.H_parallel - self.H_single:+.2f} m")
        
        # (3) 串联运行
        print("\n(3) 串联运行工况点")
        print("    串联特性: H总 = H₁ + H₂ = 2H单, Q相同")
        print("    串联泵曲线: H = 2(H₀ - aQ²)")
        print(f"    2({self.H0} - {self.a}Q²) = {self.H_static} + {self.S}Q²")
        print(f"    {2*self.H0} - {2*self.a}Q² = {self.H_static} + {self.S}Q²")
        print(f"    Q = {self.Q_series:.4f} m³/s")
        print(f"\n    总扬程: H = {self.H_series:.2f} m")
        print(f"    每台泵扬程: H = {self.H_series_each:.2f} m")
        print(f"    效率: η = {self.eta_series:.2f}%")
        print(f"    总功率: P = {self.P_series:.2f} kW")
        
        # 与单泵比较
        H_increase = (self.H_series / self.H_single - 1) * 100
        print(f"\n    与单泵比较:")
        print(f"    扬程增加: {H_increase:.1f}%")
        print(f"    流量变化: {self.Q_series - self.Q_single:+.4f} m³/s")
        
        # (4) 综合比较
        print("\n(4) 三种运行方式综合比较")
        print("┌" + "─"*78 + "┐")
        print("│ 运行方式 │  流量(m³/s)  │  扬程(m)  │  效率(%)  │  功率(kW)  │ 单位水量耗能 │")
        print("├" + "─"*78 + "┤")
        
        # 单泵
        e_single = self.P_single / (self.Q_single * 3600) if self.Q_single > 0 else 0
        print(f"│ 单泵运行   │ {self.Q_single:12.4f} │ {self.H_single:9.2f} │ {self.eta_single:9.2f} │ {self.P_single:10.2f} │ {e_single:12.4f} │")
        
        # 并联
        e_parallel = self.P_parallel / (self.Q_parallel * 3600) if self.Q_parallel > 0 else 0
        print(f"│ 并联运行   │ {self.Q_parallel:12.4f} │ {self.H_parallel:9.2f} │ {self.eta_parallel_each:9.2f} │ {self.P_parallel:10.2f} │ {e_parallel:12.4f} │")
        
        # 串联
        e_series = self.P_series / (self.Q_series * 3600) if self.Q_series > 0 else 0
        print(f"│ 串联运行   │ {self.Q_series:12.4f} │ {self.H_series:9.2f} │ {self.eta_series:9.2f} │ {self.P_series:10.2f} │ {e_series:12.4f} │")
        
        print("└" + "─"*78 + "┘")
        print("注: 单位水量耗能 = 功率(kW) / 流量(m³/h), 单位: kW/(m³/h)")
        
        # (5) 适用条件分析
        print("\n(5) 不同运行方式适用条件")
        
        print("\n■ 并联运行适用条件:")
        print("  ① 管路特性: 扁平型（阻力系数S较小）")
        S_ratio = self.S / self.a
        print(f"     本例: S/a = {S_ratio:.3f}")
        if S_ratio < 1:
            print("     ✓ S < a，管路阻力较小，适合并联")
        else:
            print("     ✗ S ≥ a，管路阻力较大，并联效果差")
        
        print("\n  ② 需求特点: 大流量、中等扬程")
        print(f"     并联流量增加: {Q_increase:.1f}%")
        if Q_increase > 50:
            print("     ✓ 流量显著增加，并联有效")
        else:
            print("     ✗ 流量增加有限，并联效果不明显")
        
        print("\n  ③ 效率考虑:")
        if self.eta_parallel_each > 0.9 * self.eta_single:
            print("     ✓ 并联效率保持较好")
        else:
            print("     ✗ 并联效率下降明显")
        
        print("\n■ 串联运行适用条件:")
        print("  ① 管路特性: 陡峭型（阻力系数S较大）")
        print(f"     本例: S/a = {S_ratio:.3f}")
        if S_ratio > 1:
            print("     ✓ S > a，管路阻力较大，适合串联")
        else:
            print("     ✗ S ≤ a，管路阻力较小，串联效果差")
        
        print("\n  ② 需求特点: 高扬程、中等流量")
        print(f"     串联扬程增加: {H_increase:.1f}%")
        if H_increase > 50:
            print("     ✓ 扬程显著增加，串联有效")
        else:
            print("     ✗ 扬程增加有限，串联效果不明显")
        
        print("\n  ③ 效率考虑:")
        if self.eta_series > 0.9 * self.eta_single:
            print("     ✓ 串联效率保持较好")
        else:
            print("     ✗ 串联效率下降明显")
        
        print("\n【经济性评价】")
        print(f"从单位水量耗能看:")
        print(f"  单泵: {e_single:.4f} kW/(m³/h)")
        print(f"  并联: {e_parallel:.4f} kW/(m³/h) ({(e_parallel/e_single-1)*100:+.1f}%)")
        print(f"  串联: {e_series:.4f} kW/(m³/h) ({(e_series/e_single-1)*100:+.1f}%)")
        
        if e_parallel < e_single and e_parallel < e_series:
            print("\n  结论: 并联运行最经济")
        elif e_series < e_single and e_series < e_parallel:
            print("\n  结论: 串联运行最经济")
        else:
            print("\n  结论: 单泵运行最经济")
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：单泵运行
        ax1 = plt.subplot(2, 2, 1)
        self._plot_single_pump(ax1)
        
        # 子图2：并联运行
        ax2 = plt.subplot(2, 2, 2)
        self._plot_parallel(ax2)
        
        # 子图3：串联运行
        ax3 = plt.subplot(2, 2, 3)
        self._plot_series(ax3)
        
        # 子图4：综合比较
        ax4 = plt.subplot(2, 2, 4)
        self._plot_comparison(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_single_pump(self, ax):
        """绘制单泵运行图"""
        Q_array = np.linspace(0, 0.25, 100)
        
        # 泵特性曲线
        H_pump = self.pump_head_curve(Q_array)
        ax.plot(Q_array, H_pump, 'b-', linewidth=2.5, label='单泵特性曲线')
        
        # 管路特性曲线
        H_pipe = self.pipe_head_curve(Q_array)
        ax.plot(Q_array, H_pipe, 'r-', linewidth=2.5, label='管路特性曲线')
        
        # 工况点
        ax.plot(self.Q_single, self.H_single, 'go', markersize=12,
               label=f'工况点: Q={self.Q_single:.3f}m³/s, H={self.H_single:.1f}m')
        
        # 辅助线
        ax.plot([self.Q_single, self.Q_single], [0, self.H_single],
               'g--', linewidth=1.5, alpha=0.5)
        ax.plot([0, self.Q_single], [self.H_single, self.H_single],
               'g--', linewidth=1.5, alpha=0.5)
        
        # 标注
        ax.text(self.Q_single+0.01, self.H_single+2,
               f'η={self.eta_single:.1f}%',
               fontsize=10, color='green', weight='bold')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('单泵运行工况', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.25)
        ax.set_ylim(0, 60)
    
    def _plot_parallel(self, ax):
        """绘制并联运行图"""
        Q_array = np.linspace(0, 0.4, 100)
        
        # 单泵特性
        H_single = self.pump_head_curve(Q_array)
        ax.plot(Q_array, H_single, 'b--', linewidth=1.5, alpha=0.5,
               label='单泵特性')
        
        # 并联泵特性（Q总 = 2Q单）
        H_parallel = self.H0 - self.a * (Q_array/2)**2
        ax.plot(Q_array, H_parallel, 'b-', linewidth=2.5,
               label='并联泵特性')
        
        # 管路特性
        H_pipe = self.pipe_head_curve(Q_array)
        ax.plot(Q_array, H_pipe, 'r-', linewidth=2.5,
               label='管路特性')
        
        # 单泵工况点
        ax.plot(self.Q_single, self.H_single, 'ko', markersize=8,
               alpha=0.5, label=f'单泵: Q={self.Q_single:.3f}m³/s')
        
        # 并联工况点
        ax.plot(self.Q_parallel, self.H_parallel, 'go', markersize=12,
               label=f'并联: Q={self.Q_parallel:.3f}m³/s')
        
        # 辅助线
        ax.plot([self.Q_parallel, self.Q_parallel], [0, self.H_parallel],
               'g--', linewidth=1.5, alpha=0.5)
        
        # 流量增加箭头
        ax.annotate('', xy=(self.Q_parallel, 5), xytext=(self.Q_single, 5),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='orange'))
        ax.text((self.Q_single+self.Q_parallel)/2, 7,
               f'流量↑{(self.Q_parallel/self.Q_single-1)*100:.0f}%',
               ha='center', fontsize=10, color='orange', weight='bold')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('并联运行工况（增大流量）', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.4)
        ax.set_ylim(0, 60)
    
    def _plot_series(self, ax):
        """绘制串联运行图"""
        Q_array = np.linspace(0, 0.25, 100)
        
        # 单泵特性
        H_single = self.pump_head_curve(Q_array)
        ax.plot(Q_array, H_single, 'b--', linewidth=1.5, alpha=0.5,
               label='单泵特性')
        
        # 串联泵特性（H总 = 2H单）
        H_series = 2 * self.pump_head_curve(Q_array)
        ax.plot(Q_array, H_series, 'b-', linewidth=2.5,
               label='串联泵特性')
        
        # 管路特性
        H_pipe = self.pipe_head_curve(Q_array)
        ax.plot(Q_array, H_pipe, 'r-', linewidth=2.5,
               label='管路特性')
        
        # 单泵工况点
        ax.plot(self.Q_single, self.H_single, 'ko', markersize=8,
               alpha=0.5, label=f'单泵: H={self.H_single:.1f}m')
        
        # 串联工况点
        ax.plot(self.Q_series, self.H_series, 'go', markersize=12,
               label=f'串联: H={self.H_series:.1f}m')
        
        # 辅助线
        ax.plot([self.Q_series, self.Q_series], [0, self.H_series],
               'g--', linewidth=1.5, alpha=0.5)
        
        # 扬程增加箭头
        ax.annotate('', xy=(0.05, self.H_series), xytext=(0.05, self.H_single),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='orange'))
        ax.text(0.08, (self.H_single+self.H_series)/2,
               f'扬程↑{(self.H_series/self.H_single-1)*100:.0f}%',
               fontsize=10, color='orange', weight='bold', rotation=90, va='center')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('串联运行工况（增大扬程）', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.25)
        ax.set_ylim(0, 120)
    
    def _plot_comparison(self, ax):
        """绘制综合比较图"""
        # 数据
        labels = ['单泵', '并联', '串联']
        Q_values = [self.Q_single, self.Q_parallel, self.Q_series]
        H_values = [self.H_single, self.H_parallel, self.H_series]
        eta_values = [self.eta_single, self.eta_parallel_each, self.eta_series]
        P_values = [self.P_single, self.P_parallel, self.P_series]
        
        x = np.arange(len(labels))
        width = 0.2
        
        # 流量（归一化到单泵）
        Q_norm = [q/self.Q_single for q in Q_values]
        bars1 = ax.bar(x - 1.5*width, Q_norm, width, label='流量(相对)',
                      color='#4ECDC4', edgecolor='black', linewidth=1.5)
        
        # 扬程（归一化到单泵）
        H_norm = [h/self.H_single for h in H_values]
        bars2 = ax.bar(x - 0.5*width, H_norm, width, label='扬程(相对)',
                      color='#45B7D1', edgecolor='black', linewidth=1.5)
        
        # 效率（归一化到单泵）
        eta_norm = [e/self.eta_single for e in eta_values]
        bars3 = ax.bar(x + 0.5*width, eta_norm, width, label='效率(相对)',
                      color='#96CEB4', edgecolor='black', linewidth=1.5)
        
        # 功率（归一化到单泵）
        P_norm = [p/self.P_single for p in P_values]
        bars4 = ax.bar(x + 1.5*width, P_norm, width, label='功率(相对)',
                      color='#FFEAA7', edgecolor='black', linewidth=1.5)
        
        # 标注数值
        for bars in [bars1, bars2, bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=8)
        
        # 基准线
        ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5,
                  alpha=0.5, label='单泵基准')
        
        ax.set_ylabel('相对值（单泵=1.0）', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_title('三种运行方式综合对比', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=9, ncol=2)
        ax.grid(True, axis='y', alpha=0.3)
        
        # 文字说明
        ax.text(0.5, 0.95, '并联：增大流量\n串联：增大扬程',
               transform=ax.transAxes, fontsize=10,
               ha='center', va='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))


def test_problem_781():
    """测试题目781"""
    print("\n" + "="*80)
    print("开始水泵串并联分析...")
    print("="*80)
    
    # 创建分析对象
    pump = PumpSeriesParallel()
    
    # 打印结果
    pump.print_results()
    
    print("\n【最终答案】")
    print("="*80)
    print(f"(1) 单泵运行: Q={pump.Q_single:.4f}m³/s, H={pump.H_single:.2f}m, η={pump.eta_single:.2f}%")
    print(f"(2) 并联运行: Q={pump.Q_parallel:.4f}m³/s, H={pump.H_parallel:.2f}m, η={pump.eta_parallel_each:.2f}%")
    print(f"    流量增加{(pump.Q_parallel/pump.Q_single-1)*100:.1f}%")
    print(f"(3) 串联运行: Q={pump.Q_series:.4f}m³/s, H={pump.H_series:.2f}m, η={pump.eta_series:.2f}%")
    print(f"    扬程增加{(pump.H_series/pump.H_single-1)*100:.1f}%")
    print("(4) 经济性:")
    e_single = pump.P_single / (pump.Q_single * 3600)
    e_parallel = pump.P_parallel / (pump.Q_parallel * 3600)
    e_series = pump.P_series / (pump.Q_series * 3600)
    if e_parallel < e_single and e_parallel < e_series:
        print("    并联运行最经济")
    elif e_series < e_single and e_series < e_parallel:
        print("    串联运行最经济")
    else:
        print("    单泵运行最经济")
    print("(5) 适用条件:")
    print("    并联：管路阻力小，需大流量")
    print("    串联：管路阻力大，需高扬程")
    print("="*80)
    
    # 可视化
    print("\n生成可视化图表...")
    fig = pump.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_781_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_781_result.png")
    
    # 验证
    assert pump.Q_single > 0, "单泵流量必须为正"
    assert pump.Q_parallel > pump.Q_single, "并联流量应大于单泵"
    assert pump.H_series > pump.H_single, "串联扬程应大于单泵"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水泵串并联是泵站设计的重要内容！")
    print("• 工况点：泵特性 = 管路特性")
    print("• 并联：Q总=Q₁+Q₂, H相同（增大流量）")
    print("• 串联：H总=H₁+H₂, Q相同（增大扬程）")
    print("• 选择原则：根据管路特性和需求")
    print("• 经济性：单位水量耗能最小")


if __name__ == "__main__":
    test_problem_781()
