"""
《水力学考研1000题详解》配套代码
题目751：水泵扬程功率计算

问题描述：
某水泵在转速n=1450r/min时，流量Q=200L/s，扬程H=20m，效率η=75%。
求：(1) 轴功率P
    (2) 电机功率P_m（考虑传动效率η_m=0.95）
    (3) 比转速n_s
    (4) 若转速提高到n'=1750r/min，预测新工况下的Q'、H'、P'

考点：
1. 水泵扬程：单位重量液体获得的能量
2. 轴功率：P = ρgQH/η
3. 电机功率：P_m = P/η_m
4. 比转速：n_s = 3.65n√Q/H^(3/4)
5. 相似定律：
   - 流量：Q'/Q = n'/n
   - 扬程：H'/H = (n'/n)²
   - 功率：P'/P = (n'/n)³

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.patches import Wedge

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpPerformance:
    """水泵性能计算类"""
    
    def __init__(self, n, Q, H, eta, eta_m=0.95, rho=1000, g=9.8):
        """
        初始化
        
        参数:
            n: 转速 (r/min)
            Q: 流量 (L/s)
            H: 扬程 (m)
            eta: 效率 (%)
            eta_m: 传动效率 (%)
            rho: 液体密度 (kg/m³)
            g: 重力加速度 (m/s²)
        """
        self.n = n              # 转速 (r/min)
        self.Q = Q / 1000       # 流量 (m³/s)，从L/s转换
        self.H = H              # 扬程 (m)
        self.eta = eta / 100    # 效率（小数）
        self.eta_m = eta_m      # 传动效率
        self.rho = rho          # 密度 (kg/m³)
        self.g = g              # 重力加速度 (m/s²)
        
        # 计算
        self.calculate()
    
    def calculate(self):
        """计算水泵性能参数"""
        # 1. 有效功率（水功率）
        self.P_e = self.rho * self.g * self.Q * self.H
        
        # 2. 轴功率
        self.P = self.P_e / self.eta
        
        # 3. 电机功率
        self.P_m = self.P / self.eta_m
        
        # 4. 比转速
        self.n_s = 3.65 * self.n * np.sqrt(self.Q) / (self.H ** 0.75)
        
        # 5. 判断泵类型
        if self.n_s < 80:
            self.pump_type = "离心泵"
        elif self.n_s < 150:
            self.pump_type = "混流泵"
        else:
            self.pump_type = "轴流泵"
    
    def predict_new_speed(self, n_new):
        """根据相似定律预测新转速下的性能"""
        # 转速比
        n_ratio = n_new / self.n
        
        # 相似定律
        Q_new = self.Q * n_ratio
        H_new = self.H * (n_ratio ** 2)
        P_new = self.P * (n_ratio ** 3)
        
        # 效率假设不变（在一定范围内）
        eta_new = self.eta
        
        return {
            'n': n_new,
            'Q': Q_new * 1000,  # 转回L/s
            'H': H_new,
            'P': P_new,
            'eta': eta_new * 100,
            'n_s': 3.65 * n_new * np.sqrt(Q_new) / (H_new ** 0.75)
        }
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*80)
        print("题目751：水泵扬程功率计算")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"转速: n = {self.n} r/min")
        print(f"流量: Q = {self.Q*1000} L/s = {self.Q} m³/s")
        print(f"扬程: H = {self.H} m")
        print(f"效率: η = {self.eta*100}%")
        print(f"传动效率: η_m = {self.eta_m*100}%")
        print(f"液体密度: ρ = {self.rho} kg/m³（水）")
        
        print("\n【水泵基本概念】")
        print("1. 扬程H：单位重量液体获得的能量（m）")
        print("   H = (p₂-p₁)/(ρg) + (v₂²-v₁²)/(2g) + (z₂-z₁)")
        print("2. 有效功率P_e：泵实际传递给液体的功率（W）")
        print("   P_e = ρgQH")
        print("3. 轴功率P：电机传递给泵轴的功率（W）")
        print("   P = P_e/η = ρgQH/η")
        print("4. 电机功率P_m：电机输出功率（W）")
        print("   P_m = P/η_m")
        print("5. 效率η：P_e/P，反映能量转换效率")
        
        print("\n【计算过程】")
        
        print("\n步骤1：计算有效功率（水功率）")
        print(f"P_e = ρgQH")
        print(f"    = {self.rho}×{self.g}×{self.Q}×{self.H}")
        print(f"    = {self.P_e:.2f} W")
        print(f"    = {self.P_e/1000:.2f} kW")
        
        print("\n步骤2：计算轴功率")
        print(f"P = P_e/η")
        print(f"  = {self.P_e:.2f}/{self.eta}")
        print(f"  = {self.P:.2f} W")
        print(f"  = {self.P/1000:.2f} kW")
        
        print("\n步骤3：计算电机功率")
        print(f"P_m = P/η_m")
        print(f"    = {self.P:.2f}/{self.eta_m}")
        print(f"    = {self.P_m:.2f} W")
        print(f"    = {self.P_m/1000:.2f} kW")
        print(f"选用电机: {np.ceil(self.P_m/1000)} kW（标准系列）")
        
        print("\n步骤4：计算比转速")
        print(f"n_s = 3.65n√Q/H^(3/4)")
        print(f"    = 3.65×{self.n}×√{self.Q}/{self.H}^(3/4)")
        print(f"    = 3.65×{self.n}×{np.sqrt(self.Q):.4f}/{self.H**0.75:.4f}")
        print(f"    = {self.n_s:.2f}")
        print(f"泵类型: {self.pump_type}（根据比转速判断）")
        print("分类标准:")
        print("  • n_s < 80: 离心泵（低比转速）")
        print("  • 80 ≤ n_s < 150: 混流泵（中比转速）")
        print("  • n_s ≥ 150: 轴流泵（高比转速）")
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 轴功率: P = {self.P/1000:.2f} kW")
        print(f"(2) 电机功率: P_m = {self.P_m/1000:.2f} kW，选用{np.ceil(self.P_m/1000):.0f}kW电机")
        print(f"(3) 比转速: n_s = {self.n_s:.2f}  →  {self.pump_type}")
        print("="*80)
        
        # 相似定律预测
        print("\n【相似定律应用】")
        print("若转速提高到n'=1750r/min，根据相似定律：")
        new_data = self.predict_new_speed(1750)
        n_ratio = 1750 / self.n
        
        print(f"\n转速比: n'/n = {1750}/{self.n} = {n_ratio:.4f}")
        
        print(f"\n流量定律: Q'/Q = n'/n")
        print(f"Q' = Q × (n'/n) = {self.Q*1000} × {n_ratio:.4f}")
        print(f"   = {new_data['Q']:.2f} L/s")
        
        print(f"\n扬程定律: H'/H = (n'/n)²")
        print(f"H' = H × (n'/n)² = {self.H} × {n_ratio:.4f}²")
        print(f"   = {new_data['H']:.2f} m")
        
        print(f"\n功率定律: P'/P = (n'/n)³")
        print(f"P' = P × (n'/n)³ = {self.P/1000:.2f} × {n_ratio:.4f}³")
        print(f"   = {new_data['P']/1000:.2f} kW")
        
        print(f"\n比转速: n_s' = {new_data['n_s']:.2f}")
        print("（比转速不变，因为是同一台泵）")
        
        print("\n【新工况总结】")
        print("="*80)
        print(f"转速: n' = 1750 r/min")
        print(f"流量: Q' = {new_data['Q']:.2f} L/s")
        print(f"扬程: H' = {new_data['H']:.2f} m")
        print(f"功率: P' = {new_data['P']/1000:.2f} kW")
        print("="*80)
        
        print("\n【核心公式】")
        print("轴功率: P = ρgQH/η")
        print("电机功率: P_m = P/η_m")
        print("比转速: n_s = 3.65n√Q/H^(3/4)")
        print("相似定律:")
        print("  • Q'/Q = n'/n")
        print("  • H'/H = (n'/n)²")
        print("  • P'/P = (n'/n)³")
        print("  • η' ≈ η（效率基本不变）")
        print("  • n_s' = n_s（比转速不变）")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：功率分解
        ax1 = plt.subplot(2, 2, 1)
        self._plot_power_breakdown(ax1)
        
        # 子图2：相似定律
        ax2 = plt.subplot(2, 2, 2)
        self._plot_similarity_laws(ax2)
        
        # 子图3：水泵特性曲线
        ax3 = plt.subplot(2, 2, 3)
        self._plot_characteristic_curves(ax3)
        
        # 子图4：比转速分类
        ax4 = plt.subplot(2, 2, 4)
        self._plot_specific_speed(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_power_breakdown(self, ax):
        """绘制功率分解"""
        powers = ['有效功率\nP_e', '轴功率\nP', '电机功率\nP_m']
        values = [self.P_e/1000, self.P/1000, self.P_m/1000]
        colors = ['lightgreen', 'skyblue', 'lightcoral']
        
        bars = ax.barh(powers, values, color=colors, alpha=0.7,
                      edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{val:.2f}kW',
                   ha='left', va='center', fontsize=11, weight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 效率标注
        ax.annotate('', xy=(self.P/1000, 0), xytext=(self.P_e/1000, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text((self.P_e/1000 + self.P/1000)/2, 0.15,
               f'η={self.eta*100}%',
               ha='center', fontsize=10, color='red')
        
        ax.annotate('', xy=(self.P_m/1000, 1), xytext=(self.P/1000, 1),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text((self.P/1000 + self.P_m/1000)/2, 1.15,
               f'η_m={self.eta_m*100}%',
               ha='center', fontsize=10, color='red')
        
        ax.set_xlabel('功率 (kW)', fontsize=12)
        ax.set_title('水泵功率分解', fontsize=13, weight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        ax.set_xlim(0, max(values)*1.3)
        
        # 添加说明
        ax.text(0.5, 2.7, 'P_e = ρgQH\nP = P_e/η\nP_m = P/η_m',
               fontsize=9, transform=ax.transData,
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    def _plot_similarity_laws(self, ax):
        """绘制相似定律"""
        # 转速范围
        n_range = np.linspace(self.n*0.5, self.n*1.5, 100)
        n_ratio = n_range / self.n
        
        # 相似定律
        Q_ratio = n_ratio
        H_ratio = n_ratio ** 2
        P_ratio = n_ratio ** 3
        
        # 绘制曲线
        ax.plot(n_ratio, Q_ratio, 'b-', linewidth=2.5, label='Q\'/Q = n\'/n')
        ax.plot(n_ratio, H_ratio, 'g-', linewidth=2.5, label='H\'/H = (n\'/n)²')
        ax.plot(n_ratio, P_ratio, 'r-', linewidth=2.5, label='P\'/P = (n\'/n)³')
        
        # 标注当前工况
        ax.plot(1.0, 1.0, 'ko', markersize=10, zorder=5)
        ax.text(1.0, 1.05, '原工况\nn=1450r/min',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 标注新工况
        n_new_ratio = 1750 / self.n
        ax.axvline(n_new_ratio, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(n_new_ratio, 2.2, f'n\'=1750r/min\nn\'/n={n_new_ratio:.3f}',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax.set_xlabel('转速比 n\'/n', fontsize=12)
        ax.set_ylabel('参数比值', fontsize=12)
        ax.set_title('水泵相似定律', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0.5, 1.5)
        ax.set_ylim(0, 3.5)
    
    def _plot_characteristic_curves(self, ax):
        """绘制特性曲线"""
        # Q范围（相对于设计流量）
        Q_rel = np.linspace(0, 2, 100)
        
        # 简化的特性曲线模型
        # H-Q曲线（二次函数，开口向下）
        H_rel = 1.2 - 0.4 * Q_rel**2
        
        # η-Q曲线（抛物线，峰值在Q=1）
        eta_rel = -0.6 * (Q_rel - 1)**2 + 1.0
        eta_rel = np.maximum(eta_rel, 0)  # 效率不能为负
        
        # P-Q曲线（三次函数，递增）
        P_rel = 0.3 + 0.4*Q_rel + 0.3*Q_rel**2
        
        # 绘制曲线
        ax_H = ax
        ax_eta = ax.twinx()
        
        line1 = ax_H.plot(Q_rel, H_rel, 'b-', linewidth=2.5, label='H-Q')
        line2 = ax_eta.plot(Q_rel, eta_rel*100, 'g-', linewidth=2.5, label='η-Q')
        line3 = ax_H.plot(Q_rel, P_rel, 'r-', linewidth=2.5, label='P-Q')
        
        # 标注设计工况点
        ax_H.plot(1.0, 1.0, 'ro', markersize=12, zorder=5)
        ax_H.text(1.0, 1.05, '设计工况\nQ=200L/s',
                 fontsize=10, ha='center',
                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax_H.set_xlabel('流量 Q/Q_d', fontsize=12)
        ax_H.set_ylabel('扬程H、功率P (相对值)', fontsize=12, color='black')
        ax_eta.set_ylabel('效率 η (%)', fontsize=12, color='green')
        ax_H.set_title('水泵特性曲线', fontsize=13, weight='bold')
        
        # 合并图例
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax_H.legend(lines, labels, loc='upper right', fontsize=10)
        
        ax_H.grid(True, alpha=0.3)
        ax_H.set_xlim(0, 2)
        ax_H.set_ylim(0, 1.5)
        ax_eta.set_ylim(0, 120)
        
        # 高效区标注
        ax_H.axvspan(0.8, 1.2, alpha=0.2, color='green')
        ax_H.text(1.0, 0.1, '高效区', fontsize=10, ha='center', color='green')
    
    def _plot_specific_speed(self, ax):
        """绘制比转速分类"""
        # 比转速分类
        types = ['离心泵', '混流泵', '轴流泵']
        n_s_ranges = [(30, 80), (80, 150), (150, 300)]
        colors = ['skyblue', 'lightgreen', 'lightcoral']
        
        # 当前泵的比转速
        current_n_s = self.n_s
        
        # 绘制分类区间
        y_pos = 0
        for i, (pump_type, (n_s_min, n_s_max), color) in enumerate(zip(types, n_s_ranges, colors)):
            ax.barh(y_pos, n_s_max - n_s_min, left=n_s_min,
                   height=0.6, color=color, alpha=0.7,
                   edgecolor='black', linewidth=2)
            ax.text((n_s_min + n_s_max)/2, y_pos,
                   f'{pump_type}\nn_s: {n_s_min}-{n_s_max}',
                   ha='center', va='center', fontsize=10, weight='bold')
            y_pos += 1
        
        # 标注当前泵
        current_type_idx = 0 if current_n_s < 80 else (1 if current_n_s < 150 else 2)
        ax.plot(current_n_s, current_type_idx, 'r*', markersize=20, zorder=5)
        ax.text(current_n_s, current_type_idx + 0.3,
               f'本泵\nn_s={current_n_s:.1f}',
               ha='center', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlabel('比转速 n_s', fontsize=12)
        ax.set_yticks([])
        ax.set_title('比转速分类与泵型选择', fontsize=13, weight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        ax.set_xlim(0, 350)
        ax.set_ylim(-0.5, 3)
        
        # 特性说明
        ax.text(320, 2.5, 
               '特性:\n低比转速→高扬程、小流量\n高比转速→低扬程、大流量',
               fontsize=9, ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))


def test_problem_751():
    """测试题目751"""
    # 已知条件
    n = 1450            # 转速 (r/min)
    Q = 200             # 流量 (L/s)
    H = 20              # 扬程 (m)
    eta = 75            # 效率 (%)
    eta_m = 0.95        # 传动效率
    
    # 创建计算对象
    pump = PumpPerformance(n, Q, H, eta, eta_m)
    
    # 打印结果
    pump.print_results()
    
    # 可视化
    fig = pump.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_751_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_751_result.png")
    
    # 验证答案（合理性检查）
    assert pump.P > 0, "轴功率必须为正"
    assert pump.P_m > pump.P, "电机功率必须大于轴功率"
    assert 0 < pump.eta < 1, "效率必须在0-1之间"
    assert pump.n_s > 0, "比转速必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水泵性能是泵站设计的基础！")
    print("• 扬程：单位重量液体获得的能量")
    print("• 功率：P = ρgQH/η")
    print("• 效率：P_e/P，越高越节能")
    print("• 比转速：泵型特征参数，决定泵的形状和性能")
    print("• 相似定律：同一台泵变速运行的规律")
    print("• 应用：泵选型、工况调节、并联串联")


if __name__ == "__main__":
    test_problem_751()
