#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第05章 水文学基础 - 题目1：降雨资料分析

题目描述：
某流域面积F=100km²，某次暴雨过程实测雨量站资料：
时段：0-1h, 1-2h, 2-3h, 3-4h, 4-5h, 5-6h
雨量(mm)：5, 15, 30, 25, 10, 5

求：
(1) 总降雨量P和平均降雨强度i
(2) 最大1小时、2小时、3小时降雨量
(3) 绘制降雨过程线和累积降雨量曲线
(4) 径流系数α=0.6时，计算产流总量和产流深

知识点：
- 降雨资料分析
- 降雨强度计算
- 最大连续降雨量
- 径流系数法
- 产流计算

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RainfallAnalysis:
    """降雨资料分析类"""
    
    def __init__(self, rainfall_data: list, basin_area: float):
        """
        初始化参数
        
        Parameters:
        -----------
        rainfall_data : list
            时段降雨量数据 (mm)
        basin_area : float
            流域面积 (km²)
        """
        self.rainfall = np.array(rainfall_data)
        self.basin_area = basin_area
        self.n_periods = len(rainfall_data)
        self.time = np.arange(self.n_periods + 1)  # 时间节点
    
    def total_rainfall(self) -> float:
        """
        计算总降雨量
        
        P = Σ P_i
        
        Returns:
        --------
        float : 总降雨量 (mm)
        """
        return np.sum(self.rainfall)
    
    def average_intensity(self) -> float:
        """
        计算平均降雨强度
        
        i = P / t
        
        Returns:
        --------
        float : 平均降雨强度 (mm/h)
        """
        return self.total_rainfall() / self.n_periods
    
    def max_consecutive_rainfall(self, duration: int) -> tuple:
        """
        计算最大连续n小时降雨量
        
        Parameters:
        -----------
        duration : int
            持续时间 (h)
            
        Returns:
        --------
        tuple : (最大降雨量, 起始时刻, 结束时刻)
        """
        if duration > self.n_periods:
            return self.total_rainfall(), 0, self.n_periods
        
        max_rainfall = 0
        start_idx = 0
        
        for i in range(self.n_periods - duration + 1):
            consecutive_sum = np.sum(self.rainfall[i:i+duration])
            if consecutive_sum > max_rainfall:
                max_rainfall = consecutive_sum
                start_idx = i
        
        return max_rainfall, start_idx, start_idx + duration
    
    def cumulative_rainfall(self) -> np.ndarray:
        """
        计算累积降雨量
        
        Returns:
        --------
        np.ndarray : 累积降雨量数组
        """
        return np.concatenate(([0], np.cumsum(self.rainfall)))
    
    def runoff_calculation(self, runoff_coefficient: float) -> tuple:
        """
        产流计算（径流系数法）
        
        R = α * P
        W = R * F
        
        Parameters:
        -----------
        runoff_coefficient : float
            径流系数
            
        Returns:
        --------
        tuple : (产流深, 产流总量)
        """
        P = self.total_rainfall()
        R = runoff_coefficient * P  # 产流深 (mm)
        W = R * self.basin_area  # 产流总量 (mm·km²)
        W_m3 = W * 1000  # 转换为m³
        
        return R, W_m3
    
    def rainfall_distribution(self) -> dict:
        """
        降雨分布特征分析
        
        Returns:
        --------
        dict : 降雨分布特征
        """
        P_total = self.total_rainfall()
        
        # 各时段降雨占比
        percentages = (self.rainfall / P_total * 100) if P_total > 0 else np.zeros_like(self.rainfall)
        
        # 最大雨强时段
        max_intensity_idx = np.argmax(self.rainfall)
        max_intensity = self.rainfall[max_intensity_idx]
        
        # 峰现时间（最大雨强出现时刻）
        peak_time = max_intensity_idx + 0.5  # 时段中点
        
        return {
            'percentages': percentages,
            'max_intensity': max_intensity,
            'max_intensity_time': max_intensity_idx,
            'peak_time': peak_time
        }
    
    def runoff_coefficient_analysis(self, alpha_range: tuple = (0.3, 0.9), 
                                   n_points: int = 50) -> tuple:
        """
        径流系数影响分析
        
        Parameters:
        -----------
        alpha_range : tuple
            径流系数范围
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (alpha_array, R_array, W_array)
        """
        alpha_array = np.linspace(alpha_range[0], alpha_range[1], n_points)
        P = self.total_rainfall()
        
        R_array = alpha_array * P
        W_array = R_array * self.basin_area * 1000  # m³
        
        return alpha_array, R_array, W_array
    
    def basin_area_analysis(self, F_range: tuple = (50, 200), 
                           n_points: int = 50, alpha: float = 0.6) -> tuple:
        """
        流域面积影响分析
        
        Parameters:
        -----------
        F_range : tuple
            流域面积范围 (km²)
        n_points : int
            计算点数
        alpha : float
            径流系数
            
        Returns:
        --------
        tuple : (F_array, W_array)
        """
        F_array = np.linspace(F_range[0], F_range[1], n_points)
        P = self.total_rainfall()
        R = alpha * P
        
        W_array = R * F_array * 1000  # m³
        
        return F_array, W_array
    
    def plot_analysis(self, alpha: float = 0.6):
        """绘制降雨分析图"""
        fig = plt.figure(figsize=(16, 12))
        
        # 图1：降雨过程线（柱状图）
        ax1 = plt.subplot(3, 3, 1)
        
        time_centers = np.arange(self.n_periods) + 0.5
        bars = ax1.bar(time_centers, self.rainfall, width=0.8, 
                      color='steelblue', edgecolor='black', linewidth=2,
                      label='时段降雨量')
        
        # 标注数值
        for i, (t, r) in enumerate(zip(time_centers, self.rainfall)):
            ax1.text(t, r + 1, f'{r}', ha='center', fontsize=10, fontweight='bold')
        
        # 标注最大雨强
        max_idx = np.argmax(self.rainfall)
        ax1.bar([time_centers[max_idx]], [self.rainfall[max_idx]], width=0.8,
               color='red', alpha=0.5, label='最大雨强')
        
        ax1.set_xlabel('时间 (h)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('降雨量 (mm/h)', fontsize=11, fontweight='bold')
        ax1.set_title('降雨过程线', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_xlim(0, self.n_periods)
        
        # 图2：累积降雨量曲线
        ax2 = plt.subplot(3, 3, 2)
        
        cumulative = self.cumulative_rainfall()
        ax2.plot(self.time, cumulative, 'b-o', linewidth=2.5, markersize=8,
                label='累积降雨量')
        ax2.fill_between(self.time, 0, cumulative, alpha=0.3, color='skyblue')
        
        # 标注总降雨量
        P_total = self.total_rainfall()
        ax2.text(self.n_periods, P_total, f'P={P_total}mm',
                fontsize=11, fontweight='bold', ha='right', va='bottom')
        
        ax2.set_xlabel('时间 (h)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('累积降雨量 (mm)', fontsize=11, fontweight='bold')
        ax2.set_title('累积降雨量曲线', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # 图3：降雨分布饼图
        ax3 = plt.subplot(3, 3, 3)
        
        dist = self.rainfall_distribution()
        labels = [f'{i}~{i+1}h\n{r}mm\n({p:.1f}%)' 
                 for i, (r, p) in enumerate(zip(self.rainfall, dist['percentages']))]
        
        colors = plt.cm.Blues(np.linspace(0.3, 0.9, self.n_periods))
        
        wedges, texts = ax3.pie(self.rainfall, labels=labels, colors=colors,
                               startangle=90, textprops={'fontsize': 9})
        
        # 高亮最大值
        wedges[dist['max_intensity_time']].set_edgecolor('red')
        wedges[dist['max_intensity_time']].set_linewidth(3)
        
        ax3.set_title('降雨时段分布', fontsize=13, fontweight='bold')
        
        # 图4：最大连续降雨量
        ax4 = plt.subplot(3, 3, 4)
        
        durations = [1, 2, 3, 4, 5, 6]
        max_rainfalls = []
        
        for d in durations:
            max_r, _, _ = self.max_consecutive_rainfall(d)
            max_rainfalls.append(max_r)
        
        bars = ax4.bar(durations, max_rainfalls, color='coral', 
                      edgecolor='black', linewidth=2)
        
        # 标注数值
        for d, r in zip(durations, max_rainfalls):
            ax4.text(d, r + 2, f'{r:.0f}', ha='center', fontsize=10, fontweight='bold')
        
        ax4.set_xlabel('持续时间 (h)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('最大降雨量 (mm)', fontsize=11, fontweight='bold')
        ax4.set_title('最大连续降雨量', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 图5：产流计算
        ax5 = plt.subplot(3, 3, 5)
        
        R, W = self.runoff_calculation(alpha)
        P_total = self.total_rainfall()
        loss = P_total - R
        
        categories = ['总降雨\nP', '产流深\nR', '损失\n(P-R)']
        values = [P_total, R, loss]
        colors_bar = ['steelblue', 'green', 'orange']
        
        bars = ax5.bar(categories, values, color=colors_bar, 
                      edgecolor='black', linewidth=2)
        
        # 标注
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}mm', ha='center', va='bottom', 
                    fontsize=11, fontweight='bold')
        
        ax5.set_ylabel('降雨/产流深 (mm)', fontsize=11, fontweight='bold')
        ax5.set_title(f'产流计算（α={alpha}）', fontsize=13, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 图6：径流系数影响
        ax6 = plt.subplot(3, 3, 6)
        
        alpha_array, R_array, W_array = self.runoff_coefficient_analysis()
        
        ax6_twin = ax6.twinx()
        
        line1 = ax6.plot(alpha_array, R_array, 'b-', linewidth=2.5, label='产流深R')
        line2 = ax6_twin.plot(alpha_array, W_array/1e6, 'r--', linewidth=2.5, 
                             label='产流总量W')
        
        # 标注当前设计值
        ax6.plot([alpha], [R], 'bo', markersize=10)
        ax6_twin.plot([alpha], [W/1e6], 'ro', markersize=10)
        
        ax6.set_xlabel('径流系数 α', fontsize=11, fontweight='bold')
        ax6.set_ylabel('产流深 R (mm)', fontsize=11, fontweight='bold', color='b')
        ax6_twin.set_ylabel('产流总量 W (万m³)', fontsize=11, fontweight='bold', color='r')
        ax6.set_title('径流系数的影响', fontsize=13, fontweight='bold')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax6.legend(lines, labels, fontsize=9)
        ax6.grid(True, alpha=0.3)
        
        # 图7：流域面积影响
        ax7 = plt.subplot(3, 3, 7)
        
        F_array, W_F_array = self.basin_area_analysis(alpha=alpha)
        
        ax7.plot(F_array, W_F_array/1e6, 'g-', linewidth=2.5)
        
        # 标注当前设计值
        ax7.plot([self.basin_area], [W/1e6], 'go', markersize=12,
                label=f'F={self.basin_area}km², W={W/1e6:.1f}万m³')
        
        ax7.set_xlabel('流域面积 F (km²)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('产流总量 W (万m³)', fontsize=11, fontweight='bold')
        ax7.set_title('流域面积的影响', fontsize=13, fontweight='bold')
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        # 图8：计算结果汇总
        ax8 = plt.subplot(3, 3, 8)
        
        i_avg = self.average_intensity()
        max_1h, start_1, end_1 = self.max_consecutive_rainfall(1)
        max_2h, start_2, end_2 = self.max_consecutive_rainfall(2)
        max_3h, start_3, end_3 = self.max_consecutive_rainfall(3)
        
        results_text = f"""
降雨资料分析结果

【基本参数】
流域面积：F = {self.basin_area} km²
降雨历时：t = {self.n_periods} h

【降雨特征】
总降雨量：P = {P_total} mm
平均雨强：i = {i_avg:.2f} mm/h

【最大降雨量】
最大1h：{max_1h} mm (第{start_1+1}h)
最大2h：{max_2h} mm (第{start_2+1}~{end_2}h)
最大3h：{max_3h} mm (第{start_3+1}~{end_3}h)

【产流计算】（α={alpha}）
产流深：R = {R:.1f} mm
产流总量：W = {W/1e6:.1f} 万m³
          = {W/1e4:.2f} 万m³

【径流系数意义】
降雨形成径流：{alpha*100:.0f}%
损失（蒸发+下渗）：{(1-alpha)*100:.0f}%
"""
        
        ax8.text(0.1, 0.5, results_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax8.axis('off')
        ax8.set_title('计算结果汇总', fontsize=13, fontweight='bold')
        
        # 图9：公式总结
        ax9 = plt.subplot(3, 3, 9)
        
        formula_text = """
降雨资料分析公式

【基本计算】
总降雨量：P = Σ P_i

平均雨强：i = P / t

累积降雨：P_累(t) = Σ P_i

【最大连续降雨】
P_n = max{P_i + P_i+1 + ... + P_i+n-1}

【产流计算】
径流系数法：
R = α · P
W = R · F

单位换算：
W (m³) = R (mm) × F (km²) × 1000

【径流系数α】
城市：0.7~0.9
山区：0.4~0.6
平原：0.3~0.5
"""
        
        ax9.text(0.1, 0.5, formula_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax9.axis('off')
        ax9.set_title('公式总结', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self, alpha: float = 0.6):
        """打印计算结果"""
        print("=" * 70)
        print("降雨资料分析")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  流域面积：F = {self.basin_area} km²")
        print(f"  降雨历时：t = {self.n_periods} h")
        print(f"  时段降雨量：{self.rainfall} mm")
        
        print(f"\n(1) 总降雨量和平均降雨强度：")
        
        P_total = self.total_rainfall()
        print(f"\n  总降雨量：")
        print(f"    P = Σ P_i")
        print(f"      = {' + '.join(map(str, self.rainfall))}")
        print(f"      = {P_total} mm")
        
        i_avg = self.average_intensity()
        print(f"\n  平均降雨强度：")
        print(f"    i = P / t")
        print(f"      = {P_total} / {self.n_periods}")
        print(f"      = {i_avg:.2f} mm/h")
        
        print(f"\n(2) 最大连续降雨量：")
        
        # 最大1小时
        max_1h, start_1, end_1 = self.max_consecutive_rainfall(1)
        print(f"\n  最大1小时降雨量：")
        print(f"    检查各时段：")
        for i, r in enumerate(self.rainfall):
            marker = ' ✓✓ 最大' if r == max_1h else ''
            print(f"      第{i+1}h: {r} mm{marker}")
        print(f"    P_1h,max = {max_1h} mm （第{start_1+1}小时）")
        
        # 最大2小时
        max_2h, start_2, end_2 = self.max_consecutive_rainfall(2)
        print(f"\n  最大2小时降雨量：")
        print(f"    检查所有连续2小时：")
        for i in range(self.n_periods - 1):
            consecutive_sum = np.sum(self.rainfall[i:i+2])
            marker = ' ✓✓ 最大' if consecutive_sum == max_2h else ''
            print(f"      第{i+1}~{i+2}h: {' + '.join(map(str, self.rainfall[i:i+2]))} = {consecutive_sum} mm{marker}")
        print(f"    P_2h,max = {max_2h} mm （第{start_2+1}~{end_2}小时）")
        
        # 最大3小时
        max_3h, start_3, end_3 = self.max_consecutive_rainfall(3)
        print(f"\n  最大3小时降雨量：")
        print(f"    检查所有连续3小时：")
        for i in range(self.n_periods - 2):
            consecutive_sum = np.sum(self.rainfall[i:i+3])
            marker = ' ✓✓ 最大' if consecutive_sum == max_3h else ''
            print(f"      第{i+1}~{i+3}h: {' + '.join(map(str, self.rainfall[i:i+3]))} = {consecutive_sum} mm{marker}")
        print(f"    P_3h,max = {max_3h} mm （第{start_3+1}~{end_3}小时）")
        
        print(f"\n(3) 降雨过程线和累积降雨量：")
        
        cumulative = self.cumulative_rainfall()
        print(f"\n  数据表：")
        print(f"  {'时间(h)':<10} {'时段雨量(mm)':<15} {'累积雨量(mm)':<15}")
        print(f"  {'-'*40}")
        for i, (t, cum) in enumerate(zip(self.time, cumulative)):
            if i < self.n_periods:
                period_rain = self.rainfall[i]
                print(f"  {t:<10} {period_rain:<15} {cum:<15.1f}")
            else:
                print(f"  {t:<10} {'-':<15} {cum:<15.1f}")
        
        dist = self.rainfall_distribution()
        print(f"\n  降雨特征：")
        print(f"    • 最大雨强：{dist['max_intensity']} mm/h（第{dist['max_intensity_time']+1}小时）")
        print(f"    • 峰现时间：第{dist['peak_time']:.1f}小时")
        print(f"    • 降雨类型：单峰型暴雨")
        
        print(f"\n(4) 产流计算：")
        
        R, W = self.runoff_calculation(alpha)
        
        print(f"\n  径流系数法：")
        print(f"    R = α · P")
        print(f"\n  其中：")
        print(f"    α = {alpha}：径流系数")
        print(f"    P = {P_total} mm：降雨量")
        
        print(f"\n  产流深：")
        print(f"    R = {alpha} × {P_total}")
        print(f"      = {R:.1f} mm")
        
        print(f"\n  产流总量：")
        print(f"    W = R · F")
        print(f"      = {R:.1f} mm × {self.basin_area} km²")
        print(f"      = {R * self.basin_area:.1f} mm·km²")
        
        print(f"\n  单位换算：")
        print(f"    W = {R * self.basin_area:.1f} × 1000 m³")
        print(f"      = {W:.0f} m³")
        print(f"      = {W/1e4:.2f} 万m³")
        print(f"      = {W/1e6:.1f} 百万m³")
        
        loss = P_total - R
        print(f"\n  物理意义：")
        print(f"    • 降雨{P_total}mm中，{alpha*100:.0f}%形成径流")
        print(f"    • {(1-alpha)*100:.0f}%通过蒸发、下渗等损失")
        print(f"    • 产流深{R:.1f}mm，损失{loss:.1f}mm")
        print(f"    • 产流{W/1e4:.2f}万m³可供利用")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 总降雨量：P = Σ P_i")
        print("2. 平均雨强：i = P/t")
        print("3. 最大连续降雨：逐段检查求和")
        print("4. 径流系数法：R = α·P，W = R·F")
        print("5. 单位换算：mm·km² × 1000 = m³")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第05章 水文学基础 - 题目1：降雨资料分析")
    print("💧" * 35 + "\n")
    
    # 题目参数
    rainfall_data = [5, 15, 30, 25, 10, 5]  # mm
    basin_area = 100.0  # km²
    alpha = 0.6  # 径流系数
    
    # 创建降雨分析对象
    rainfall = RainfallAnalysis(rainfall_data=rainfall_data, 
                               basin_area=basin_area)
    
    # 打印结果
    rainfall.print_results(alpha=alpha)
    
    # 绘图
    print("\n正在绘制降雨分析图...")
    rainfall.plot_analysis(alpha=alpha)
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
