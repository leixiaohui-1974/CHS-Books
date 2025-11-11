"""
《水力学考研1000题详解》配套代码
题目766：水泵特性曲线分析

问题描述：
某离心泵在转速n=1450r/min时的特性曲线数据如下：
Q (L/s):  0    50   100   150   200   250   300
H (m):   24   23.5  22    19.5  16    11    4
η (%):    0   45    68    76    75    60    30
P (kW):   5   6.5   8.5   10.5  12    12.5  11

求：(1) 绘制完整的特性曲线（Q-H, Q-η, Q-P）
    (2) 确定高效区范围
    (3) 确定最优工况点
    (4) 分析各参数随Q的变化规律
    (5) 若转速提高到n'=1750r/min，预测新特性曲线

考点：
1. 水泵特性曲线：Q-H, Q-η, Q-P三条曲线
2. 高效区：η ≥ η_max * 0.9的范围
3. 最优工况点：η_max对应的点
4. 曲线拟合：多项式拟合
5. 相似定律：变速后的曲线预测

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpCharacteristics:
    """水泵特性曲线分析类"""
    
    def __init__(self, Q_data, H_data, eta_data, P_data, n=1450):
        """
        初始化
        
        参数:
            Q_data: 流量数据 (L/s)
            H_data: 扬程数据 (m)
            eta_data: 效率数据 (%)
            P_data: 功率数据 (kW)
            n: 转速 (r/min)
        """
        self.Q_data = np.array(Q_data)
        self.H_data = np.array(H_data)
        self.eta_data = np.array(eta_data)
        self.P_data = np.array(P_data)
        self.n = n
        
        # 分析
        self.analyze()
    
    def analyze(self):
        """分析特性曲线"""
        # 1. 曲线拟合
        self._fit_curves()
        
        # 2. 确定最优工况点
        self._find_optimal_point()
        
        # 3. 确定高效区
        self._find_high_efficiency_zone()
        
        # 4. 分析变化规律
        self._analyze_trends()
    
    def _fit_curves(self):
        """曲线拟合"""
        # 生成密集点用于绘图
        self.Q_fit = np.linspace(0, max(self.Q_data), 200)
        
        # H-Q曲线拟合（二次多项式）
        try:
            self.H_coeffs = np.polyfit(self.Q_data, self.H_data, 2)
            self.H_fit = np.polyval(self.H_coeffs, self.Q_fit)
        except:
            # 备用：线性插值
            f_H = interp1d(self.Q_data, self.H_data, kind='quadratic', fill_value='extrapolate')
            self.H_fit = f_H(self.Q_fit)
        
        # η-Q曲线拟合（三次多项式）
        try:
            self.eta_coeffs = np.polyfit(self.Q_data, self.eta_data, 3)
            self.eta_fit = np.polyval(self.eta_coeffs, self.Q_fit)
            # 限制在0-100范围
            self.eta_fit = np.clip(self.eta_fit, 0, 100)
        except:
            f_eta = interp1d(self.Q_data, self.eta_data, kind='cubic', fill_value='extrapolate')
            self.eta_fit = np.clip(f_eta(self.Q_fit), 0, 100)
        
        # P-Q曲线拟合（二次多项式）
        try:
            self.P_coeffs = np.polyfit(self.Q_data, self.P_data, 2)
            self.P_fit = np.polyval(self.P_coeffs, self.Q_fit)
            # 限制为正值
            self.P_fit = np.maximum(self.P_fit, 0)
        except:
            f_P = interp1d(self.Q_data, self.P_data, kind='quadratic', fill_value='extrapolate')
            self.P_fit = np.maximum(f_P(self.Q_fit), 0)
    
    def _find_optimal_point(self):
        """确定最优工况点"""
        # 找到效率最大值点
        idx_max = np.argmax(self.eta_fit)
        self.Q_opt = self.Q_fit[idx_max]
        self.H_opt = self.H_fit[idx_max]
        self.eta_opt = self.eta_fit[idx_max]
        self.P_opt = self.P_fit[idx_max]
    
    def _find_high_efficiency_zone(self):
        """确定高效区"""
        # 高效区定义：η ≥ 0.9 * η_max
        eta_threshold = 0.9 * self.eta_opt
        
        # 找到高效区范围
        high_eff_indices = np.where(self.eta_fit >= eta_threshold)[0]
        if len(high_eff_indices) > 0:
            self.Q_high_eff_min = self.Q_fit[high_eff_indices[0]]
            self.Q_high_eff_max = self.Q_fit[high_eff_indices[-1]]
        else:
            self.Q_high_eff_min = self.Q_opt
            self.Q_high_eff_max = self.Q_opt
    
    def _analyze_trends(self):
        """分析变化规律"""
        # H-Q：递减
        self.H_trend = "递减"
        
        # η-Q：先增后减
        self.eta_trend = "先增后减，峰值在Q=" + f"{self.Q_opt:.1f}L/s"
        
        # P-Q：先增后减（或单调递增）
        if self.P_fit[-1] < self.P_fit[-2]:
            self.P_trend = "先增后减"
        else:
            self.P_trend = "单调递增"
    
    def predict_new_speed(self, n_new):
        """预测新转速下的特性曲线"""
        # 相似定律
        n_ratio = n_new / self.n
        
        # Q' = Q * (n'/n)
        Q_new = self.Q_fit * n_ratio
        
        # H' = H * (n'/n)²
        H_new = self.H_fit * (n_ratio ** 2)
        
        # P' = P * (n'/n)³
        P_new = self.P_fit * (n_ratio ** 3)
        
        # η' ≈ η（效率基本不变）
        eta_new = self.eta_fit.copy()
        
        return {
            'Q': Q_new,
            'H': H_new,
            'eta': eta_new,
            'P': P_new,
            'n': n_new
        }
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目766：水泵特性曲线分析")
        print("="*80)
        
        print("\n【原始数据】")
        print(f"转速: n = {self.n} r/min")
        print("\n数据点:")
        print("Q (L/s):", " ".join([f"{q:6.0f}" for q in self.Q_data]))
        print("H (m):  ", " ".join([f"{h:6.1f}" for h in self.H_data]))
        print("η (%):  ", " ".join([f"{e:6.0f}" for e in self.eta_data]))
        print("P (kW): ", " ".join([f"{p:6.1f}" for p in self.P_data]))
        
        print("\n【水泵特性曲线基本概念】")
        print("1. Q-H曲线（扬程曲线）:")
        print("   • 表示流量Q与扬程H的关系")
        print("   • 一般为递减曲线")
        print("   • Q=0时H最大（闭闸扬程）")
        print("   • 反映泵的输送能力")
        
        print("\n2. Q-η曲线（效率曲线）:")
        print("   • 表示流量Q与效率η的关系")
        print("   • 抛物线形，先增后减")
        print("   • 存在最高效率点")
        print("   • 反映泵的能量利用率")
        
        print("\n3. Q-P曲线（功率曲线）:")
        print("   • 表示流量Q与轴功率P的关系")
        print("   • 一般为递增曲线")
        print("   • Q=0时P最小（启动功率）")
        print("   • 反映泵的能耗")
        
        print("\n【分析过程】")
        
        print("\n步骤1：曲线拟合")
        print("H-Q曲线：二次多项式拟合")
        print(f"  H = {self.H_coeffs[0]:.6f}Q² + {self.H_coeffs[1]:.6f}Q + {self.H_coeffs[2]:.6f}")
        
        print("\nη-Q曲线：三次多项式拟合")
        print(f"  η = {self.eta_coeffs[0]:.8f}Q³ + {self.eta_coeffs[1]:.6f}Q² + {self.eta_coeffs[2]:.6f}Q + {self.eta_coeffs[3]:.6f}")
        
        print("\nP-Q曲线：二次多项式拟合")
        print(f"  P = {self.P_coeffs[0]:.6f}Q² + {self.P_coeffs[1]:.6f}Q + {self.P_coeffs[2]:.6f}")
        
        print("\n步骤2：确定最优工况点")
        print(f"最高效率: η_max = {self.eta_opt:.2f}%")
        print(f"最优流量: Q_opt = {self.Q_opt:.2f} L/s")
        print(f"对应扬程: H_opt = {self.H_opt:.2f} m")
        print(f"对应功率: P_opt = {self.P_opt:.2f} kW")
        print("说明: 这是泵的设计工况点，效率最高，最节能")
        
        print("\n步骤3：确定高效区")
        eta_threshold = 0.9 * self.eta_opt
        print(f"高效区定义: η ≥ 0.9×η_max = {eta_threshold:.2f}%")
        print(f"高效区范围: {self.Q_high_eff_min:.2f} L/s ≤ Q ≤ {self.Q_high_eff_max:.2f} L/s")
        print(f"高效区宽度: ΔQ = {self.Q_high_eff_max - self.Q_high_eff_min:.2f} L/s")
        print("说明: 泵应在高效区内运行，节能且延长寿命")
        
        print("\n步骤4：分析变化规律")
        print(f"H-Q关系: {self.H_trend}")
        print("  • 流量越大，扬程越小")
        print("  • 原因：流速增大，损失增加")
        
        print(f"\nη-Q关系: {self.eta_trend}")
        print("  • 小流量时效率低（回流损失）")
        print("  • 设计点附近效率高")
        print("  • 大流量时效率低（冲击损失）")
        
        print(f"\nP-Q关系: {self.P_trend}")
        print("  • 功率随流量增大而增大")
        print("  • P = ρgQH/η")
        
        print("\n步骤5：关键参数")
        # 闭闸扬程（Q=0）
        H_shutoff = np.polyval(self.H_coeffs, 0)
        print(f"闭闸扬程: H₀ = {H_shutoff:.2f} m（Q=0时）")
        
        # 最大流量（H≈0）
        # 求解H=0的方程
        Q_max_roots = np.roots(self.H_coeffs)
        Q_max = max([r.real for r in Q_max_roots if r.real > 0 and abs(r.imag) < 1e-6])
        print(f"最大流量: Q_max ≈ {Q_max:.2f} L/s（H≈0时）")
        
        print("\n【最终答案】")
        print("="*80)
        print("(1) 特性曲线: 已绘制Q-H、Q-η、Q-P三条曲线")
        print(f"(2) 高效区: {self.Q_high_eff_min:.1f} ~ {self.Q_high_eff_max:.1f} L/s")
        print(f"(3) 最优工况点: Q={self.Q_opt:.1f}L/s, H={self.H_opt:.1f}m, η={self.eta_opt:.1f}%, P={self.P_opt:.1f}kW")
        print("(4) 变化规律:")
        print(f"    • H-Q: {self.H_trend}")
        print(f"    • η-Q: {self.eta_trend}")
        print(f"    • P-Q: {self.P_trend}")
        print("="*80)
        
        print("\n【相似定律应用】")
        print("若转速提高到n'=1750r/min，预测新特性曲线:")
        new_data = self.predict_new_speed(1750)
        n_ratio = 1750 / self.n
        
        print(f"\n转速比: n'/n = {1750}/{self.n} = {n_ratio:.4f}")
        
        print(f"\n最优工况点变化:")
        Q_opt_new = self.Q_opt * n_ratio
        H_opt_new = self.H_opt * (n_ratio ** 2)
        P_opt_new = self.P_opt * (n_ratio ** 3)
        
        print(f"流量: Q' = {self.Q_opt:.1f} × {n_ratio:.3f} = {Q_opt_new:.1f} L/s")
        print(f"扬程: H' = {self.H_opt:.1f} × {n_ratio:.3f}² = {H_opt_new:.1f} m")
        print(f"功率: P' = {self.P_opt:.1f} × {n_ratio:.3f}³ = {P_opt_new:.1f} kW")
        print(f"效率: η' ≈ {self.eta_opt:.1f}% (基本不变)")
        
        print("\n【核心公式】")
        print("特性曲线方程:")
        print("  • H-Q: H = aQ² + bQ + c")
        print("  • η-Q: η = aQ³ + bQ² + cQ + d")
        print("  • P-Q: P = aQ² + bQ + c")
        print("相似定律:")
        print("  • Q'/Q = n'/n")
        print("  • H'/H = (n'/n)²")
        print("  • P'/P = (n'/n)³")
        print("  • η' ≈ η")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：Q-H曲线
        ax1 = plt.subplot(2, 2, 1)
        self._plot_QH_curve(ax1)
        
        # 子图2：Q-η曲线
        ax2 = plt.subplot(2, 2, 2)
        self._plot_Qeta_curve(ax2)
        
        # 子图3：Q-P曲线
        ax3 = plt.subplot(2, 2, 3)
        self._plot_QP_curve(ax3)
        
        # 子图4：综合特性曲线（双y轴）
        ax4 = plt.subplot(2, 2, 4)
        self._plot_combined_curves(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_QH_curve(self, ax):
        """绘制Q-H曲线"""
        # 拟合曲线
        ax.plot(self.Q_fit, self.H_fit, 'b-', linewidth=2.5, label='H-Q曲线（拟合）')
        
        # 原始数据点
        ax.plot(self.Q_data, self.H_data, 'bo', markersize=8, label='实验数据', zorder=5)
        
        # 最优工况点
        ax.plot(self.Q_opt, self.H_opt, 'r*', markersize=20, zorder=6,
               label=f'最优点({self.Q_opt:.0f},{self.H_opt:.1f})')
        
        # 高效区
        ax.axvspan(self.Q_high_eff_min, self.Q_high_eff_max, 
                  alpha=0.2, color='green', label='高效区')
        
        # 闭闸扬程
        H_shutoff = np.polyval(self.H_coeffs, 0)
        ax.plot(0, H_shutoff, 'rs', markersize=10, label=f'闭闸扬程({H_shutoff:.1f}m)')
        
        ax.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('Q-H 扬程特性曲线', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(self.Q_data)*1.1)
        ax.set_ylim(0, max(self.H_data)*1.2)
    
    def _plot_Qeta_curve(self, ax):
        """绘制Q-η曲线"""
        # 拟合曲线
        ax.plot(self.Q_fit, self.eta_fit, 'g-', linewidth=2.5, label='η-Q曲线（拟合）')
        
        # 原始数据点
        ax.plot(self.Q_data, self.eta_data, 'go', markersize=8, label='实验数据', zorder=5)
        
        # 最优工况点
        ax.plot(self.Q_opt, self.eta_opt, 'r*', markersize=20, zorder=6,
               label=f'最高效率({self.Q_opt:.0f},{self.eta_opt:.1f}%)')
        
        # 高效区
        ax.axvspan(self.Q_high_eff_min, self.Q_high_eff_max, 
                  alpha=0.2, color='green', label='高效区')
        
        # 90%效率线
        eta_threshold = 0.9 * self.eta_opt
        ax.axhline(eta_threshold, color='r', linestyle='--', linewidth=1.5,
                  alpha=0.7, label=f'90%η_max({eta_threshold:.1f}%)')
        
        ax.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax.set_ylabel('效率 η (%)', fontsize=12)
        ax.set_title('Q-η 效率特性曲线', fontsize=13, weight='bold')
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(self.Q_data)*1.1)
        ax.set_ylim(0, 100)
    
    def _plot_QP_curve(self, ax):
        """绘制Q-P曲线"""
        # 拟合曲线
        ax.plot(self.Q_fit, self.P_fit, 'r-', linewidth=2.5, label='P-Q曲线（拟合）')
        
        # 原始数据点
        ax.plot(self.Q_data, self.P_data, 'ro', markersize=8, label='实验数据', zorder=5)
        
        # 最优工况点
        ax.plot(self.Q_opt, self.P_opt, 'r*', markersize=20, zorder=6,
               label=f'最优点功率({self.Q_opt:.0f},{self.P_opt:.1f}kW)')
        
        # 高效区
        ax.axvspan(self.Q_high_eff_min, self.Q_high_eff_max, 
                  alpha=0.2, color='green', label='高效区')
        
        # 启动功率
        P_start = np.polyval(self.P_coeffs, 0)
        ax.plot(0, P_start, 'rs', markersize=10, label=f'启动功率({P_start:.1f}kW)')
        
        ax.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax.set_ylabel('功率 P (kW)', fontsize=12)
        ax.set_title('Q-P 功率特性曲线', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(self.Q_data)*1.1)
        ax.set_ylim(0, max(self.P_data)*1.3)
    
    def _plot_combined_curves(self, ax):
        """绘制综合特性曲线（双y轴）"""
        # 主y轴：H和P
        ax.plot(self.Q_fit, self.H_fit, 'b-', linewidth=2, label='扬程H')
        ax.plot(self.Q_fit, self.P_fit, 'r-', linewidth=2, label='功率P')
        
        # 次y轴：η
        ax2 = ax.twinx()
        ax2.plot(self.Q_fit, self.eta_fit, 'g-', linewidth=2, label='效率η')
        
        # 最优工况点
        ax.plot(self.Q_opt, self.H_opt, 'b*', markersize=15, zorder=5)
        ax.plot(self.Q_opt, self.P_opt, 'r*', markersize=15, zorder=5)
        ax2.plot(self.Q_opt, self.eta_opt, 'g*', markersize=15, zorder=5)
        
        # 高效区
        ax.axvspan(self.Q_high_eff_min, self.Q_high_eff_max, 
                  alpha=0.15, color='green')
        
        # 标注最优点
        ax.axvline(self.Q_opt, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.text(self.Q_opt, max(self.H_fit)*0.9, f'最优点\nQ={self.Q_opt:.0f}L/s',
               ha='center', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlabel('流量 Q (L/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m), 功率 P (kW)', fontsize=12)
        ax2.set_ylabel('效率 η (%)', fontsize=12, color='green')
        ax.set_title('水泵综合特性曲线', fontsize=13, weight='bold')
        
        # 合并图例
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(self.Q_data)*1.1)
        ax.set_ylim(0, max(max(self.H_data), max(self.P_data))*1.2)
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='y', labelcolor='green')


def test_problem_766():
    """测试题目766"""
    # 实验数据
    Q_data = [0, 50, 100, 150, 200, 250, 300]  # L/s
    H_data = [24, 23.5, 22, 19.5, 16, 11, 4]   # m
    eta_data = [0, 45, 68, 76, 75, 60, 30]      # %
    P_data = [5, 6.5, 8.5, 10.5, 12, 12.5, 11]  # kW
    n = 1450  # r/min
    
    # 创建分析对象
    pump = PumpCharacteristics(Q_data, H_data, eta_data, P_data, n)
    
    # 打印结果
    pump.print_results()
    
    # 可视化
    fig = pump.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_766_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_766_result.png")
    
    # 验证答案（合理性检查）
    assert pump.Q_opt > 0, "最优流量必须为正"
    assert pump.H_opt > 0, "最优扬程必须为正"
    assert 0 < pump.eta_opt <= 100, "最高效率必须在0-100之间"
    assert pump.Q_high_eff_min < pump.Q_high_eff_max, "高效区范围必须合理"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水泵特性曲线是泵站设计的基础！")
    print("• Q-H曲线：反映输送能力，递减")
    print("• Q-η曲线：反映能量效率，抛物线")
    print("• Q-P曲线：反映能耗，递增")
    print("• 高效区：η ≥ 0.9η_max，节能运行")
    print("• 最优点：效率最高点，设计工况")
    print("• 相似定律：变速调节，Q∝n, H∝n², P∝n³")
    print("• 应用：泵选型、工况调节、系统匹配")


if __name__ == "__main__":
    test_problem_766()
