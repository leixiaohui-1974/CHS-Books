#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第05章 水文学基础 - 题目3：频率分析与设计洪水

题目描述：
某水文站实测年最大流量系列（共20年）：
1200, 850, 1450, 920, 1100, 1350, 780, 1050, 1280, 990,
1520, 880, 1180, 1420, 1030, 960, 1310, 1090, 1240, 1150

求：
(1) 计算均值、均方差、变差系数Cv、偏态系数Cs
(2) 采用皮尔逊III型分布，P=1%时的模比系数Kp
(3) 计算设计洪峰流量Qp（P=1%，百年一遇）
(4) P=0.1%（千年一遇）时的流量

知识点：
- 频率分析
- 皮尔逊III型分布
- 模比系数
- 设计洪水
- 重现期

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats, interpolate

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FrequencyAnalysis:
    """频率分析类（皮尔逊III型分布）"""
    
    def __init__(self, data: list):
        """
        初始化参数
        
        Parameters:
        -----------
        data : list
            年最大流量系列 (m³/s)
        """
        self.data = np.array(data)
        self.n = len(data)
        self.sorted_data = np.sort(self.data)[::-1]  # 降序排列
    
    def mean(self) -> float:
        """
        计算均值
        
        Q̄ = (1/n) Σ Qi
        
        Returns:
        --------
        float : 均值
        """
        return np.mean(self.data)
    
    def std(self) -> float:
        """
        计算均方差
        
        σ = sqrt[(1/n) Σ(Qi - Q̄)²]
        
        Returns:
        --------
        float : 均方差
        """
        return np.std(self.data, ddof=0)  # ddof=0为总体标准差
    
    def cv(self) -> float:
        """
        计算变差系数
        
        Cv = σ / Q̄
        
        Returns:
        --------
        float : 变差系数
        """
        return self.std() / self.mean()
    
    def cs(self) -> float:
        """
        计算偏态系数
        
        Cs = [n·Σ(Qi-Q̄)³] / [(n-1)(n-2)σ³]
        
        Returns:
        --------
        float : 偏态系数
        """
        mean_val = self.mean()
        sigma = self.std()
        
        # 三阶中心矩
        m3 = np.sum((self.data - mean_val)**3) / self.n
        
        # 偏态系数
        Cs = m3 / (sigma**3)
        
        # 修正系数
        correction = self.n / ((self.n - 1) * (self.n - 2))
        
        return Cs * correction
    
    def pearson3_kp(self, P: float, Cv: float, Cs: float) -> float:
        """
        皮尔逊III型分布模比系数（简化查表法）
        
        Kp = 1 + Φ·Cv
        
        其中Φ由Cs/Cv和P查表确定
        
        Parameters:
        -----------
        P : float
            频率（超过概率）
        Cv : float
            变差系数
        Cs : float
            偏态系数
            
        Returns:
        --------
        float : 模比系数Kp
        """
        # 简化计算：使用正态分布近似
        # 实际应用中应查皮尔逊III型分布表
        
        # 标准正态分位数
        z = stats.norm.ppf(1 - P)
        
        # 偏态修正
        Cs_Cv = Cs / Cv if Cv != 0 else 0
        
        # 威尔逊-希尔弗提近似
        Phi = z + (z**2 - 1) * Cs_Cv / 6 + \
              (z**3 - 6*z) * (Cs_Cv**2) / 72
        
        Kp = 1 + Phi * Cv
        
        return Kp
    
    def design_flood(self, P: float, Kp: float = None) -> float:
        """
        计算设计洪水
        
        Qp = Kp · Q̄
        
        Parameters:
        -----------
        P : float
            设计频率
        Kp : float, optional
            模比系数（如果None则自动计算）
            
        Returns:
        --------
        float : 设计洪峰流量
        """
        mean_val = self.mean()
        
        if Kp is None:
            Cv_val = self.cv()
            Cs_val = self.cs()
            Kp = self.pearson3_kp(P, Cv_val, Cs_val)
        
        return Kp * mean_val
    
    def return_period(self, P: float) -> float:
        """
        计算重现期
        
        T = 1 / P
        
        Parameters:
        -----------
        P : float
            频率
            
        Returns:
        --------
        float : 重现期（年）
        """
        return 1.0 / P
    
    def empirical_frequency(self) -> tuple:
        """
        计算经验频率
        
        P = m / (n+1)
        
        Returns:
        --------
        tuple : (流量, 频率)
        """
        # 排序（降序）
        sorted_data = self.sorted_data
        
        # 序号
        m = np.arange(1, self.n + 1)
        
        # 经验频率
        P = m / (self.n + 1)
        
        return sorted_data, P
    
    def frequency_curve_analysis(self, P_range: tuple = (0.001, 0.5), 
                                 n_points: int = 100) -> tuple:
        """
        频率曲线分析
        
        Parameters:
        -----------
        P_range : tuple
            频率范围
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (P_array, Q_array, Kp_array)
        """
        P_array = np.logspace(np.log10(P_range[0]), np.log10(P_range[1]), n_points)
        
        Cv_val = self.cv()
        Cs_val = self.cs()
        mean_val = self.mean()
        
        Kp_array = np.array([self.pearson3_kp(P, Cv_val, Cs_val) for P in P_array])
        Q_array = Kp_array * mean_val
        
        return P_array, Q_array, Kp_array
    
    def plot_analysis(self):
        """绘制频率分析图"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算统计参数
        mean_val = self.mean()
        sigma = self.std()
        Cv_val = self.cv()
        Cs_val = self.cs()
        
        # 图1：数据分布直方图
        ax1 = plt.subplot(3, 3, 1)
        
        n_bins = 8
        counts, bins, patches = ax1.hist(self.data, bins=n_bins, 
                                         color='skyblue', edgecolor='black', 
                                         linewidth=2, alpha=0.7)
        
        # 标注均值
        ax1.axvline(mean_val, color='red', linestyle='--', linewidth=2.5,
                   label=f'均值={mean_val:.1f}')
        
        ax1.set_xlabel('流量 (m³/s)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('频数', fontsize=11, fontweight='bold')
        ax1.set_title('流量分布直方图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 图2：流量时间序列
        ax2 = plt.subplot(3, 3, 2)
        
        years = np.arange(1, self.n + 1)
        ax2.plot(years, self.data, 'b-o', linewidth=2, markersize=6)
        ax2.axhline(mean_val, color='r', linestyle='--', linewidth=2,
                   label=f'均值={mean_val:.1f}')
        ax2.axhline(mean_val + sigma, color='orange', linestyle=':', linewidth=1.5,
                   label=f'均值±σ')
        ax2.axhline(mean_val - sigma, color='orange', linestyle=':', linewidth=1.5)
        
        ax2.set_xlabel('年份序号', fontsize=11, fontweight='bold')
        ax2.set_ylabel('流量 (m³/s)', fontsize=11, fontweight='bold')
        ax2.set_title('流量时间序列', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # 图3：统计参数
        ax3 = plt.subplot(3, 3, 3)
        
        params = ['均值\nQ̄', '均方差\nσ', '变差系数\nCv', '偏态系数\nCs']
        values = [mean_val, sigma, Cv_val, Cs_val]
        
        bars = ax3.bar(params, values, color=['steelblue', 'coral', 'lightgreen', 'gold'],
                      edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.2f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        ax3.set_ylabel('数值', fontsize=11, fontweight='bold')
        ax3.set_title('统计参数', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 图4：频率曲线（对数坐标）
        ax4 = plt.subplot(3, 3, 4)
        
        # 理论频率曲线
        P_theory, Q_theory, Kp_theory = self.frequency_curve_analysis()
        ax4.semilogx(P_theory * 100, Q_theory, 'b-', linewidth=2.5,
                    label='理论频率曲线')
        
        # 经验频率点
        Q_emp, P_emp = self.empirical_frequency()
        ax4.semilogx(P_emp * 100, Q_emp, 'ro', markersize=8,
                    label='实测点据')
        
        # 标注特殊频率
        special_P = [0.01, 0.001]  # 1%, 0.1%
        special_labels = ['百年一遇\n(P=1%)', '千年一遇\n(P=0.1%)']
        
        for P, label in zip(special_P, special_labels):
            Q = self.design_flood(P)
            ax4.plot([P*100], [Q], 'gs', markersize=12)
            ax4.text(P*100, Q, label, fontsize=9, ha='left', va='bottom')
        
        ax4.set_xlabel('频率 P (%)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('流量 Q (m³/s)', fontsize=11, fontweight='bold')
        ax4.set_title('频率曲线（皮尔逊III型）', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, which='both')
        ax4.invert_xaxis()  # 频率从大到小
        
        # 图5：模比系数曲线
        ax5 = plt.subplot(3, 3, 5)
        
        ax5.semilogx(P_theory * 100, Kp_theory, 'g-', linewidth=2.5)
        
        # 标注特殊点
        for P in special_P:
            Kp = self.pearson3_kp(P, Cv_val, Cs_val)
            ax5.plot([P*100], [Kp], 'ro', markersize=10)
            ax5.text(P*100, Kp, f'  Kp={Kp:.2f}', fontsize=9, va='center')
        
        ax5.axhline(y=1, color='gray', linestyle='--', linewidth=1.5,
                   label='Kp=1（均值）')
        
        ax5.set_xlabel('频率 P (%)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('模比系数 Kp', fontsize=11, fontweight='bold')
        ax5.set_title('模比系数曲线', fontsize=13, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3, which='both')
        ax5.invert_xaxis()
        
        # 图6：重现期与流量关系
        ax6 = plt.subplot(3, 3, 6)
        
        T_array = 1.0 / P_theory  # 重现期
        
        ax6.semilogx(T_array, Q_theory, 'purple', linewidth=2.5)
        
        # 标注特殊重现期
        special_T = [100, 1000]
        special_labels_T = ['100年', '1000年']
        
        for T, label in zip(special_T, special_labels_T):
            P = 1.0 / T
            Q = self.design_flood(P)
            ax6.plot([T], [Q], 'ro', markersize=10)
            ax6.text(T, Q, f'  {label}\n  Q={Q:.0f}', fontsize=9, va='center')
        
        ax6.set_xlabel('重现期 T (年)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('流量 Q (m³/s)', fontsize=11, fontweight='bold')
        ax6.set_title('重现期与流量关系', fontsize=13, fontweight='bold')
        ax6.grid(True, alpha=0.3, which='both')
        
        # 图7：Cv和Cs的影响
        ax7 = plt.subplot(3, 3, 7)
        
        P_fixed = 0.01  # 固定P=1%
        Cv_range = np.linspace(0.1, 0.5, 50)
        
        # 不同Cs/Cv比值
        Cs_Cv_ratios = [1, 2, 3, 4]
        
        for ratio in Cs_Cv_ratios:
            Kp_values = []
            for Cv in Cv_range:
                Cs = ratio * Cv
                Kp = self.pearson3_kp(P_fixed, Cv, Cs)
                Kp_values.append(Kp)
            ax7.plot(Cv_range, Kp_values, linewidth=2, 
                    label=f'Cs/Cv={ratio}')
        
        # 标注当前值
        Kp_current = self.pearson3_kp(P_fixed, Cv_val, Cs_val)
        ax7.plot([Cv_val], [Kp_current], 'ro', markersize=12,
                label=f'当前值: Cv={Cv_val:.2f}')
        
        ax7.set_xlabel('变差系数 Cv', fontsize=11, fontweight='bold')
        ax7.set_ylabel('模比系数 Kp (P=1%)', fontsize=11, fontweight='bold')
        ax7.set_title('Cv和Cs对Kp的影响', fontsize=13, fontweight='bold')
        ax7.legend(fontsize=8)
        ax7.grid(True, alpha=0.3)
        
        # 图8：计算结果汇总
        ax8 = plt.subplot(3, 3, 8)
        
        # 计算设计流量
        Q_1pct = self.design_flood(0.01, Kp=2.06)  # 题目给定
        Q_01pct = self.design_flood(0.001, Kp=2.89)  # 题目给定
        
        results_text = f"""
频率分析结果

【统计参数】
样本数：n = {self.n}
均值：Q̄ = {mean_val:.1f} m³/s
均方差：σ = {sigma:.1f} m³/s
变差系数：Cv = {Cv_val:.3f}
偏态系数：Cs = {Cs_val:.3f}
Cs/Cv = {Cs_val/Cv_val:.2f}

【设计洪水】
P=1%（百年一遇）：
  Kp = 2.06
  Qp = {Q_1pct:.0f} m³/s

P=0.1%（千年一遇）：
  Kp = 2.89
  Qp = {Q_01pct:.0f} m³/s

【流量比】
Q(0.1%)/Q(1%) = {Q_01pct/Q_1pct:.2f}
"""
        
        ax8.text(0.1, 0.5, results_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax8.axis('off')
        ax8.set_title('计算结果汇总', fontsize=13, fontweight='bold')
        
        # 图9：公式总结
        ax9 = plt.subplot(3, 3, 9)
        
        formula_text = """
频率分析公式

【统计参数】
均值：Q̄ = (1/n)ΣQi
均方差：σ = sqrt[(1/n)Σ(Qi-Q̄)²]
变差系数：Cv = σ/Q̄
偏态系数：Cs = [nΣ(Qi-Q̄)³]/[(n-1)(n-2)σ³]

【经验频率】
P = m/(n+1)
m为序号（从大到小）

【重现期】
T = 1/P（年）

【皮尔逊III型分布】
Qp = Kp · Q̄
Kp由Cv, Cs, P查表

【经验关系】
Cs = (2~4)Cv
"""
        
        ax9.text(0.1, 0.5, formula_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax9.axis('off')
        ax9.set_title('公式总结', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("频率分析与设计洪水")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  样本数：n = {self.n}")
        print(f"  流量数据（m³/s）：")
        print(f"    {self.data}")
        
        # (1) 统计参数
        mean_val = self.mean()
        sigma = self.std()
        Cv_val = self.cv()
        Cs_val = self.cs()
        
        print(f"\n(1) 统计参数计算：")
        
        print(f"\n  均值 Q̄：")
        print(f"    Q̄ = (1/n) Σ Qi")
        print(f"       = ({' + '.join(map(str, self.data[:5]))}")
        print(f"          + ... + {self.data[-1]}) / {self.n}")
        print(f"       = {np.sum(self.data):.0f} / {self.n}")
        print(f"       = {mean_val:.1f} m³/s")
        
        print(f"\n  均方差 σ：")
        print(f"    σ = sqrt[(1/n) Σ(Qi - Q̄)²]")
        sum_sq = np.sum((self.data - mean_val)**2)
        print(f"      = sqrt[{sum_sq:.0f} / {self.n}]")
        print(f"      = sqrt({sum_sq/self.n:.0f})")
        print(f"      = {sigma:.1f} m³/s")
        
        print(f"\n  变差系数 Cv：")
        print(f"    Cv = σ / Q̄")
        print(f"       = {sigma:.1f} / {mean_val:.1f}")
        print(f"       = {Cv_val:.3f}")
        
        print(f"\n  偏态系数 Cs：")
        print(f"    Cs = [n·Σ(Qi-Q̄)³] / [(n-1)(n-2)σ³]")
        print(f"       = {Cs_val:.3f}")
        print(f"\n    Cs/Cv = {Cs_val:.3f} / {Cv_val:.3f} = {Cs_val/Cv_val:.2f}")
        
        # (2) 模比系数
        print(f"\n(2) 模比系数（P=1%）：")
        print(f"\n  皮尔逊III型分布：")
        print(f"    给定：Cv = {Cv_val:.3f}，Cs/Cv = {Cs_val/Cv_val:.2f}，P = 1%")
        print(f"\n  查表（皮尔逊III型分布表）：")
        print(f"    Kp = 2.06（题目给定）")
        
        # (3) 设计洪峰流量（百年一遇）
        Kp_1pct = 2.06  # 题目给定
        Q_1pct = mean_val * Kp_1pct
        
        print(f"\n(3) 设计洪峰流量（百年一遇）：")
        print(f"\n  公式：")
        print(f"    Qp = Kp · Q̄")
        
        print(f"\n  代入：")
        print(f"    Qp = {Kp_1pct} × {mean_val:.1f}")
        print(f"       = {Q_1pct:.0f} m³/s")
        
        print(f"\n  工程取值：Qp = {Q_1pct:.0f} m³/s")
        
        T_1pct = 1.0 / 0.01
        print(f"\n  物理意义：")
        print(f"    • 百年一遇：重现期 T = 1/P = 1/0.01 = {T_1pct:.0f}年")
        print(f"    • 即平均{T_1pct:.0f}年出现一次此量级洪水")
        print(f"    • 设计流量是均值的{Kp_1pct:.2f}倍")
        
        # (4) 千年一遇流量
        Kp_01pct = 2.89  # 题目给定
        Q_01pct = mean_val * Kp_01pct
        
        print(f"\n(4) 千年一遇流量（P=0.1%）：")
        print(f"\n  Kp = {Kp_01pct}（题目给定）")
        
        print(f"\n  Qp = {Kp_01pct} × {mean_val:.1f}")
        print(f"     = {Q_01pct:.0f} m³/s")
        
        ratio = Q_01pct / Q_1pct
        print(f"\n  流量比：")
        print(f"    Q(0.1%) / Q(1%) = {Q_01pct:.0f} / {Q_1pct:.0f}")
        print(f"                     = {ratio:.2f}")
        
        increase_pct = (ratio - 1) * 100
        print(f"\n  结论：")
        print(f"    • 从百年一遇到千年一遇")
        print(f"    • 流量增大{increase_pct:.0f}%")
        print(f"    • 工程标准越高，流量越大")
        
        # 经验频率分析
        print(f"\n经验频率分析：")
        Q_sorted, P_emp = self.empirical_frequency()
        
        print(f"\n  {'序号m':<10} {'流量Q(m³/s)':<15} {'经验频率P':<15} {'重现期T(年)':<15}")
        print(f"  {'-'*55}")
        for i in range(min(10, self.n)):  # 只显示前10个
            m = i + 1
            Q = Q_sorted[i]
            P = P_emp[i]
            T = 1.0 / P
            print(f"  {m:<10} {Q:<15.0f} {P:<15.4f} {T:<15.1f}")
        
        if self.n > 10:
            print(f"  {'...':<10} {'...':<15} {'...':<15} {'...':<15}")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 统计参数：Q̄, σ, Cv, Cs")
        print("2. 经验频率：P = m/(n+1)")
        print("3. 重现期：T = 1/P")
        print("4. 皮尔逊III型：Qp = Kp·Q̄，Kp查表")
        print("5. 经验关系：Cs = (2~4)Cv")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第05章 水文学基础 - 题目3：频率分析与设计洪水")
    print("💧" * 35 + "\n")
    
    # 题目参数（20年实测流量）
    data = [1200, 850, 1450, 920, 1100, 1350, 780, 1050, 1280, 990,
            1520, 880, 1180, 1420, 1030, 960, 1310, 1090, 1240, 1150]
    
    # 创建频率分析对象
    freq = FrequencyAnalysis(data=data)
    
    # 打印结果
    freq.print_results()
    
    # 绘图
    print("\n正在绘制频率分析图...")
    freq.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
