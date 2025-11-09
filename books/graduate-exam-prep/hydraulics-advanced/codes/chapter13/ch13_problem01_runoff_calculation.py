# -*- coding: utf-8 -*-
"""
第13章 水资源计算 - 题1：径流计算

问题描述：
    某流域面积A = 1000 km²，年降水量P = 800mm
    年蒸发量E = 400mm，地下水补给量G = 50mm
    地表径流系数α = 0.6
    
    求：
    1. 年径流量计算
    2. 径流模数
    3. 径流深
    4. 水量平衡分析
    5. 径流年内分配

核心公式：
    1. 水量平衡：R = P - E + G - ΔS
    2. 径流深：H = R/A
    3. 径流模数：M = R/(A·T)
    4. 径流系数：α = R/P

考试要点：
    - 水量平衡方程
    - 径流计算
    - 径流模数
    - 径流系数

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RunoffCalculation:
    """径流计算"""
    
    def __init__(self, A: float, P: float, E: float, G: float = 0, alpha: float = 0.6):
        self.A = A  # 流域面积 km²
        self.P = P  # 年降水量 mm
        self.E = E  # 年蒸发量 mm
        self.G = G  # 地下水补给量 mm
        self.alpha = alpha  # 地表径流系数
        
    def water_balance(self) -> Dict:
        """
        水量平衡方程
        R = P - E + G - ΔS
        假设ΔS = 0（多年平均）
        """
        R = self.P - self.E + self.G  # 径流深 mm
        
        # 年径流量
        Q_year = R * self.A * 1000 / 1e6  # 亿m³
        
        return {
            'R': R,
            'Q_year': Q_year
        }
    
    def runoff_coefficient(self) -> float:
        """
        径流系数
        α = R/P
        """
        balance = self.water_balance()
        alpha_calc = balance['R'] / self.P
        return alpha_calc
    
    def runoff_modulus(self) -> float:
        """
        径流模数
        M = Q/(A·T) = R/T (mm/d 或 L/(s·km²))
        """
        balance = self.water_balance()
        # 日径流模数 mm/d
        M_daily = balance['R'] / 365
        
        # 径流模数 L/(s·km²)
        M_liter = balance['R'] / 365 / 86.4  # mm/d → L/(s·km²)
        
        return M_liter
    
    def surface_runoff(self) -> float:
        """地表径流（直接径流）"""
        R_surface = self.alpha * self.P
        return R_surface
    
    def base_flow(self) -> float:
        """基流（地下径流）"""
        balance = self.water_balance()
        R_surface = self.surface_runoff()
        R_base = balance['R'] - R_surface
        return R_base
    
    def monthly_distribution(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        径流年内分配（经验分配）
        汛期（6-9月）：60%
        非汛期：40%
        """
        balance = self.water_balance()
        Q_year = balance['Q_year']
        
        # 月份
        months = np.arange(1, 13)
        
        # 经验分配系数
        # 汛期（6-9月）高，其他月份低
        distribution = np.array([
            0.05, 0.05, 0.06, 0.07, 0.08,  # 1-5月
            0.12, 0.15, 0.18, 0.15,        # 6-9月（汛期）
            0.06, 0.02, 0.01               # 10-12月
        ])
        
        Q_monthly = Q_year * distribution
        
        return months, Q_monthly
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        balance = self.water_balance()
        alpha_calc = self.runoff_coefficient()
        M = self.runoff_modulus()
        R_surface = self.surface_runoff()
        R_base = self.base_flow()
        months, Q_monthly = self.monthly_distribution()
        
        # 1. 流域水量平衡示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 水量平衡组分
        components = ['降水P', '蒸发E', '地下水补给G', '径流R']
        values = [self.P, -self.E, self.G, balance['R']]
        colors_comp = ['blue', 'red', 'green', 'cyan']
        
        y_pos = np.arange(len(components))
        bars = ax1.barh(y_pos, values, color=colors_comp, alpha=0.7, edgecolor='black')
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(components)
        ax1.set_xlabel('水量 (mm)', fontsize=10)
        ax1.set_title('水量平衡组分', fontsize=12, fontweight='bold')
        ax1.axvline(0, color='k', linewidth=1)
        ax1.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2,
                    f'{abs(val):.0f}', ha='left' if width>0 else 'right',
                    va='center', fontsize=9, fontweight='bold')
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '流域参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'流域面积: A = {self.A} km²', fontsize=10)
        ax2.text(0.1, 0.72, f'年降水量: P = {self.P} mm', fontsize=10, color='blue')
        ax2.text(0.1, 0.62, f'年蒸发量: E = {self.E} mm', fontsize=10, color='red')
        ax2.text(0.1, 0.52, f'地下水补给: G = {self.G} mm', fontsize=10, color='green')
        ax2.text(0.1, 0.40, f'径流深: R = {balance["R"]:.1f} mm', fontsize=10, 
                color='cyan', fontweight='bold')
        ax2.text(0.1, 0.28, f'年径流量: Q = {balance["Q_year"]:.2f} 亿m³', fontsize=10,
                color='purple', fontweight='bold')
        ax2.text(0.1, 0.16, f'径流系数: α = {alpha_calc:.3f}', fontsize=10, color='orange')
        ax2.text(0.1, 0.04, f'径流模数: M = {M:.2f} L/(s·km²)', fontsize=10)
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 水量平衡饼图
        ax3 = plt.subplot(3, 3, 3)
        
        # 降水去向
        labels = ['蒸发E', '径流R', '其他损失']
        sizes = [self.E, balance['R'], max(0, self.P - self.E - balance['R'] + self.G)]
        colors_pie = ['red', 'blue', 'gray']
        
        wedges, texts, autotexts = ax3.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors_pie, startangle=90)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax3.set_title(f'降水量分配 (P={self.P}mm)', fontsize=12, fontweight='bold')
        
        # 4. 径流组成
        ax4 = plt.subplot(3, 3, 4)
        
        runoff_components = ['地表径流', '基流']
        runoff_values = [R_surface, R_base]
        colors_runoff = ['lightblue', 'green']
        
        bars = ax4.bar(runoff_components, runoff_values, color=colors_runoff,
                      alpha=0.7, edgecolor='black')
        
        ax4.set_ylabel('径流深 (mm)', fontsize=10)
        ax4.set_title(f'径流组成 (总径流{balance["R"]:.1f}mm)', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, runoff_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}mm\n({val/balance["R"]*100:.1f}%)',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 5. 月径流过程线
        ax5 = plt.subplot(3, 3, 5)
        
        ax5.plot(months, Q_monthly, 'b-o', linewidth=2, markersize=6)
        ax5.fill_between(months, 0, Q_monthly, alpha=0.3, color='lightblue')
        ax5.axhline(balance['Q_year']/12, color='r', linestyle='--', linewidth=1,
                   label=f'平均{balance["Q_year"]/12:.3f}亿m³/月')
        
        # 标注汛期
        ax5.axvspan(6, 9, alpha=0.2, color='red', label='汛期')
        
        ax5.set_xlabel('月份', fontsize=10)
        ax5.set_ylabel('径流量 (亿m³)', fontsize=10)
        ax5.set_title('月径流分配', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_xticks(months)
        
        # 6. 降水-径流关系
        ax6 = plt.subplot(3, 3, 6)
        
        # 不同降水量下的径流
        P_range = np.linspace(400, 1200, 50)
        R_range = []
        
        for P_val in P_range:
            runoff_temp = RunoffCalculation(self.A, P_val, self.E, self.G, self.alpha)
            bal_temp = runoff_temp.water_balance()
            R_range.append(bal_temp['R'])
        
        ax6.plot(P_range, R_range, 'b-', linewidth=2)
        ax6.plot(self.P, balance['R'], 'ro', markersize=12, label=f'实际P={self.P}mm')
        
        ax6.set_xlabel('降水量 P (mm)', fontsize=10)
        ax6.set_ylabel('径流深 R (mm)', fontsize=10)
        ax6.set_title('降水-径流关系', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 径流系数分析
        ax7 = plt.subplot(3, 3, 7)
        
        # 不同降水量下的径流系数
        alpha_range = [R_val / P_val for R_val, P_val in zip(R_range, P_range)]
        
        ax7.plot(P_range, alpha_range, 'g-', linewidth=2)
        ax7.plot(self.P, alpha_calc, 'ro', markersize=12, label=f'α={alpha_calc:.3f}')
        ax7.axhline(alpha_calc, color='r', linestyle='--', linewidth=1, alpha=0.5)
        
        ax7.set_xlabel('降水量 P (mm)', fontsize=10)
        ax7.set_ylabel('径流系数 α', fontsize=10)
        ax7.set_title('径流系数-降水关系', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 累积径流曲线
        ax8 = plt.subplot(3, 3, 8)
        
        Q_cumulative = np.cumsum(Q_monthly)
        
        ax8.plot(months, Q_cumulative, 'b-o', linewidth=2, markersize=6)
        ax8.fill_between(months, 0, Q_cumulative, alpha=0.3, color='lightblue')
        
        # 标注关键点
        ax8.plot(9, Q_cumulative[8], 'ro', markersize=10)
        ax8.text(9, Q_cumulative[8]+0.5, f'汛期末\n{Q_cumulative[8]:.2f}亿m³',
                ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax8.set_xlabel('月份', fontsize=10)
        ax8.set_ylabel('累积径流量 (亿m³)', fontsize=10)
        ax8.set_title('累积径流过程', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3)
        ax8.set_xticks(months)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['流域面积', f'{self.A}', 'km²'],
            ['年降水量', f'{self.P}', 'mm'],
            ['年蒸发量', f'{self.E}', 'mm'],
            ['径流深', f'{balance["R"]:.1f}', 'mm'],
            ['年径流量', f'{balance["Q_year"]:.2f}', '亿m³'],
            ['径流系数', f'{alpha_calc:.3f}', '-'],
            ['径流模数', f'{M:.2f}', 'L/(s·km²)']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.45, 0.3, 0.22])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [5, 6, 7]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch13_problem01_runoff_calculation.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch13_problem01_runoff_calculation.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第13章 水资源计算 - 题1：径流计算")
        print("="*70)
        
        balance = self.water_balance()
        alpha_calc = self.runoff_coefficient()
        M = self.runoff_modulus()
        R_surface = self.surface_runoff()
        R_base = self.base_flow()
        months, Q_monthly = self.monthly_distribution()
        
        print(f"\n【流域基本参数】")
        print(f"流域面积: A = {self.A} km²")
        print(f"年降水量: P = {self.P} mm")
        print(f"年蒸发量: E = {self.E} mm")
        print(f"地下水补给: G = {self.G} mm")
        
        print(f"\n【水量平衡】")
        print(f"水量平衡方程: R = P - E + G - ΔS")
        print(f"假设ΔS = 0（多年平均）")
        print(f"径流深: R = {self.P} - {self.E} + {self.G}")
        print(f"       = {balance['R']:.2f} mm")
        
        print(f"\n年径流量: Q = R × A")
        print(f"         = {balance['R']:.2f} × {self.A}")
        print(f"         = {balance['R'] * self.A} m³")
        print(f"         = {balance['Q_year']:.3f} 亿m³")
        
        print(f"\n【径流系数】")
        print(f"径流系数: α = R/P")
        print(f"         = {balance['R']:.2f}/{self.P}")
        print(f"         = {alpha_calc:.4f}")
        
        print(f"\n【径流模数】")
        print(f"径流模数: M = R/T")
        print(f"日径流模数: {balance['R']/365:.3f} mm/d")
        print(f"径流模数: M = {M:.3f} L/(s·km²)")
        
        print(f"\n【径流组成】")
        print(f"地表径流: R_surface = α × P = {self.alpha}×{self.P} = {R_surface:.2f} mm")
        print(f"基流: R_base = R - R_surface = {balance['R']:.2f} - {R_surface:.2f} = {R_base:.2f} mm")
        print(f"地表径流占比: {R_surface/balance['R']*100:.1f}%")
        print(f"基流占比: {R_base/balance['R']*100:.1f}%")
        
        print(f"\n【月径流分配】")
        print(f"{'月份':<8} {'径流量(亿m³)':<12} {'占比(%)':<10}")
        print(f"-" * 35)
        for m, q in zip(months, Q_monthly):
            print(f"{m:<8} {q:<12.3f} {q/balance['Q_year']*100:<10.1f}")
        
        print(f"\n汛期（6-9月）径流量: {np.sum(Q_monthly[5:9]):.3f} 亿m³")
        print(f"汛期径流占比: {np.sum(Q_monthly[5:9])/balance['Q_year']*100:.1f}%")
        
        print(f"\n✓ 径流计算完成")
        print(f"\n{'='*70}\n")


def main():
    A = 1000  # km²
    P = 800   # mm
    E = 400   # mm
    G = 50    # mm
    alpha = 0.6
    
    runoff = RunoffCalculation(A, P, E, G, alpha)
    runoff.print_results()
    runoff.plot_analysis()


if __name__ == "__main__":
    main()
