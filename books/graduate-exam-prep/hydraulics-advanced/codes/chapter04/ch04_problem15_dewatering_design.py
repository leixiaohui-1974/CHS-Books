#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第04章 地下水与渗流 - 题目15：基坑降水设计（综合应用）

题目描述：
某基坑开挖工程，已知：
- 基坑尺寸：L×B=50m×30m
- 开挖深度：d=5m
- 地下水位：3m
- 需降深：s=7m
- 潜水含水层厚度：H=15m
- 渗透系数：k=5m/d
- 影响半径：R=100m
- 井径：r₀=0.15m
- 井间距：10m

求：
(1) 所需降深计算
(2) 等效半径计算（大井法）
(3) 单井出水量
(4) 井数确定
(5) 总抽水量
(6) 降水井布置方案

知识点：
- 大井法
- 裘布依公式
- 井群干扰
- 基坑降水设计

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DewateringDesign:
    """基坑降水设计类"""
    
    def __init__(self, L: float, B: float, d: float, water_table: float,
                 H: float, k: float, R: float, r0: float, d_well: float = 10.0):
        """
        初始化参数
        
        Parameters:
        -----------
        L : float
            基坑长度 (m)
        B : float
            基坑宽度 (m)
        d : float
            开挖深度 (m)
        water_table : float
            地下水位深度 (m)
        H : float
            含水层厚度 (m)
        k : float
            渗透系数 (m/d)
        R : float
            影响半径 (m)
        r0 : float
            井半径 (m)
        d_well : float
            井间距 (m)
        """
        self.L = L
        self.B = B
        self.d = d
        self.water_table = water_table
        self.H = H
        self.k = k
        self.R = R
        self.r0 = r0
        self.d_well = d_well
    
    def required_drawdown(self, safety_margin: float = 1.0) -> float:
        """
        计算所需降深
        
        s = (开挖深度 - 地下水位) + 安全余量
        
        Parameters:
        -----------
        safety_margin : float
            安全余量 (m)
            
        Returns:
        --------
        float : 所需降深 (m)
        """
        return (self.d - self.water_table) + safety_margin
    
    def equivalent_radius(self) -> float:
        """
        计算等效半径（大井法）
        
        矩形基坑：r_e = 0.29(L + B)
        
        Returns:
        --------
        float : 等效半径 (m)
        """
        return 0.29 * (self.L + self.B)
    
    def single_well_discharge(self, s: float, r_e: float) -> float:
        """
        计算单井出水量（裘布依公式）
        
        Q = π·k·(H² - h²) / ln(R/r₀)
        
        其中 h = H - s
        
        Parameters:
        -----------
        s : float
            降深 (m)
        r_e : float
            等效半径 (m)
            
        Returns:
        --------
        float : 出水量 (m³/d)
        """
        h = self.H - s  # 降深后的水位
        
        # 裘布依公式（潜水井）
        Q = np.pi * self.k * (self.H**2 - h**2) / np.log(self.R / r_e)
        
        return Q
    
    def number_of_wells(self) -> int:
        """
        计算井数
        
        环形布井：n = 周长 / 井间距
        
        Returns:
        --------
        int : 井数
        """
        perimeter = 2 * (self.L + self.B)
        n = int(np.ceil(perimeter / self.d_well))
        return n
    
    def total_discharge(self, s: float, eta: float = 1.2) -> float:
        """
        计算总抽水量（考虑群井干扰）
        
        Q_total = η × Q₀
        
        Parameters:
        -----------
        s : float
            降深 (m)
        eta : float
            干扰系数
            
        Returns:
        --------
        float : 总抽水量 (m³/d)
        """
        r_e = self.equivalent_radius()
        Q0 = self.single_well_discharge(s, r_e)
        return eta * Q0
    
    def well_positions(self, n: int, offset: float = 5.0) -> tuple:
        """
        计算降水井位置（环形布置）
        
        Parameters:
        -----------
        n : int
            井数
        offset : float
            距基坑边线距离 (m)
            
        Returns:
        --------
        tuple : (x_coords, y_coords)
        """
        # 基坑外围（含偏移）
        L_outer = self.L + 2 * offset
        B_outer = self.B + 2 * offset
        
        # 周长
        perimeter = 2 * (L_outer + B_outer)
        
        # 沿周长均匀分布
        positions = []
        
        # 底边
        n_bottom = int(n * L_outer / perimeter)
        for i in range(n_bottom):
            x = -offset + (i + 0.5) * L_outer / n_bottom
            y = -offset
            positions.append((x, y))
        
        # 右边
        n_right = int(n * B_outer / perimeter)
        for i in range(n_right):
            x = self.L + offset
            y = -offset + (i + 0.5) * B_outer / n_right
            positions.append((x, y))
        
        # 上边
        n_top = int(n * L_outer / perimeter)
        for i in range(n_top):
            x = self.L + offset - (i + 0.5) * L_outer / n_top
            y = self.B + offset
            positions.append((x, y))
        
        # 左边
        n_left = n - n_bottom - n_right - n_top
        for i in range(n_left):
            x = -offset
            y = self.B + offset - (i + 0.5) * B_outer / n_left
            positions.append((x, y))
        
        # 调整为实际井数
        while len(positions) < n:
            positions.append(positions[-1])
        positions = positions[:n]
        
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        return np.array(x_coords), np.array(y_coords)
    
    def drawdown_analysis(self, s_range: tuple = (3, 12), n_points: int = 50) -> tuple:
        """
        降深影响分析
        
        Parameters:
        -----------
        s_range : tuple
            降深范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (s_array, Q_array, n_wells_array)
        """
        s_array = np.linspace(s_range[0], s_range[1], n_points)
        Q_array = np.array([self.total_discharge(s) for s in s_array])
        
        # 井数保持不变
        n_wells = self.number_of_wells()
        n_wells_array = np.ones_like(s_array) * n_wells
        
        return s_array, Q_array, n_wells_array
    
    def permeability_analysis(self, k_range: tuple = (1, 10), n_points: int = 50) -> tuple:
        """
        渗透系数影响分析
        
        Parameters:
        -----------
        k_range : tuple
            渗透系数范围 (m/d)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (k_array, Q_array)
        """
        k_array = np.linspace(k_range[0], k_range[1], n_points)
        
        s = self.required_drawdown()
        r_e = self.equivalent_radius()
        h = self.H - s
        
        Q_array = np.pi * k_array * (self.H**2 - h**2) / np.log(self.R / r_e)
        Q_total_array = Q_array * 1.2  # 考虑干扰
        
        return k_array, Q_total_array
    
    def plot_layout(self, ax):
        """绘制降水井布置图"""
        # 基坑轮廓
        pit = Rectangle((0, 0), self.L, self.B, 
                       linewidth=3, edgecolor='black', facecolor='lightgray', alpha=0.3)
        ax.add_patch(pit)
        
        # 井位置
        n = self.number_of_wells()
        x_wells, y_wells = self.well_positions(n, offset=5)
        
        # 绘制井
        for x, y in zip(x_wells, y_wells):
            well = Circle((x, y), radius=0.5, color='steelblue', 
                         edgecolor='black', linewidth=2)
            ax.add_patch(well)
            
        # 影响半径示意（只画几个典型的）
        indices = [0, n//4, n//2, 3*n//4]
        for idx in indices:
            if idx < len(x_wells):
                circle = Circle((x_wells[idx], y_wells[idx]), radius=self.R/5, 
                              color='cyan', alpha=0.1, linestyle='--', linewidth=1)
                ax.add_patch(circle)
        
        # 标注
        ax.text(self.L/2, self.B/2, f'基坑\n{self.L}m×{self.B}m\n开挖深度{self.d}m',
               fontsize=12, ha='center', va='center', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 尺寸标注
        ax.plot([0, self.L], [-3, -3], 'k-', linewidth=2)
        ax.text(self.L/2, -4, f'{self.L}m', fontsize=11, ha='center', fontweight='bold')
        
        ax.plot([-3, -3], [0, self.B], 'k-', linewidth=2)
        ax.text(-5, self.B/2, f'{self.B}m', fontsize=11, ha='center', 
               rotation=90, fontweight='bold')
        
        # 图例
        well_legend = Circle((0, 0), radius=0.5, color='steelblue', 
                           edgecolor='black', linewidth=2)
        ax.legend([well_legend], [f'降水井（共{n}口）'], fontsize=10, loc='upper right')
        
        ax.set_xlim(-10, self.L+10)
        ax.set_ylim(-10, self.B+10)
        ax.set_aspect('equal')
        ax.set_xlabel('X (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Y (m)', fontsize=11, fontweight='bold')
        ax.set_title('降水井布置平面图', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    def plot_analysis(self):
        """绘制基坑降水设计分析图"""
        fig = plt.figure(figsize=(16, 12))
        
        # 图1：降水井布置
        ax1 = plt.subplot(3, 3, 1)
        self.plot_layout(ax1)
        
        # 图2：剖面示意
        ax2 = plt.subplot(3, 3, 2)
        
        s = self.required_drawdown()
        
        # 原地下水位
        ax2.fill_between([0, self.L+20], [self.H-self.water_table]*2, 
                        [self.H]*2, color='lightblue', alpha=0.5, label='原地下水位')
        
        # 降水后水位
        ax2.fill_between([0, self.L+20], [self.H-self.water_table-s]*2,
                        [self.H-self.water_table]*2, color='skyblue', alpha=0.5, 
                        label=f'降深{s}m')
        
        # 基坑
        ax2.add_patch(Rectangle((5, self.H-self.d), self.L, self.d,
                               linewidth=2, edgecolor='black', facecolor='white'))
        
        # 含水层底板
        ax2.axhline(y=0, color='brown', linewidth=3, label='含水层底板')
        
        # 标注
        ax2.text(self.L/2+5, self.H-self.d/2, '基坑开挖区',
                fontsize=11, ha='center', fontweight='bold')
        
        # 尺寸标注
        ax2.plot([1, 1], [self.H-self.water_table, self.H-self.water_table-s], 'r-', linewidth=2)
        ax2.text(0, self.H-self.water_table-s/2, f's={s}m', fontsize=10, 
                ha='right', color='red', fontweight='bold')
        
        ax2.set_xlim(0, self.L+20)
        ax2.set_ylim(-1, self.H+2)
        ax2.set_xlabel('水平距离 (m)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('高程 (m)', fontsize=11, fontweight='bold')
        ax2.set_title('基坑降水剖面示意图', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # 图3：设计参数
        ax3 = plt.subplot(3, 3, 3)
        
        s = self.required_drawdown()
        r_e = self.equivalent_radius()
        Q0 = self.single_well_discharge(s, r_e)
        n = self.number_of_wells()
        Q_total = self.total_discharge(s)
        
        params = ['所需降深', '等效半径', '大井流量', '井数', '总抽水量']
        values = [s, r_e, Q0, n, Q_total]
        units = ['m', 'm', 'm³/d', '口', 'm³/d']
        
        y_pos = np.arange(len(params))
        
        ax3.barh(y_pos, values, color='skyblue', edgecolor='black', linewidth=2)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(params, fontsize=10)
        ax3.set_xlabel('数值', fontsize=11, fontweight='bold')
        ax3.set_title('设计参数汇总', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # 标注数值和单位
        for i, (val, unit) in enumerate(zip(values, units)):
            if val < 100:
                ax3.text(val+max(values)*0.02, i, f'{val:.1f} {unit}',
                        va='center', fontsize=9, fontweight='bold')
            else:
                ax3.text(val/2, i, f'{val:.0f} {unit}',
                        va='center', ha='center', fontsize=9, fontweight='bold', color='white')
        
        # 图4：降深影响
        ax4 = plt.subplot(3, 3, 4)
        
        s_array, Q_array, n_wells_array = self.drawdown_analysis()
        
        ax4.plot(s_array, Q_array, 'b-', linewidth=2.5, label='总抽水量')
        
        # 标注当前设计点
        ax4.plot([s], [Q_total], 'ro', markersize=12, 
                label=f'设计点: s={s}m, Q={Q_total:.0f}m³/d')
        
        ax4.set_xlabel('降深 s (m)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('总抽水量 Q (m³/d)', fontsize=11, fontweight='bold')
        ax4.set_title('降深对抽水量的影响', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)
        
        # 图5：渗透系数影响
        ax5 = plt.subplot(3, 3, 5)
        
        k_array, Q_k_array = self.permeability_analysis()
        
        ax5.plot(k_array, Q_k_array, 'g-', linewidth=2.5)
        
        # 标注当前值
        ax5.plot([self.k], [Q_total], 'ro', markersize=12,
                label=f'k={self.k}m/d, Q={Q_total:.0f}m³/d')
        
        ax5.set_xlabel('渗透系数 k (m/d)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('总抽水量 Q (m³/d)', fontsize=11, fontweight='bold')
        ax5.set_title('渗透系数的影响', fontsize=13, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 图6：流量分配
        ax6 = plt.subplot(3, 3, 6)
        
        q_single = Q_total / n  # 单井平均流量
        
        # 饼图
        sizes = [q_single] * min(n, 8)  # 最多显示8口井
        if n > 8:
            sizes.append(q_single * (n - 8))
            labels = [f'井{i+1}' for i in range(8)] + [f'其余{n-8}口井']
        else:
            labels = [f'井{i+1}' for i in range(n)]
        
        colors = plt.cm.tab20(np.linspace(0, 1, len(sizes)))
        
        ax6.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 9})
        ax6.set_title(f'流量分配（共{n}口井）', fontsize=13, fontweight='bold')
        
        # 图7：井间距影响
        ax7 = plt.subplot(3, 3, 7)
        
        d_well_array = np.linspace(5, 20, 50)
        perimeter = 2 * (self.L + self.B)
        n_array = np.ceil(perimeter / d_well_array).astype(int)
        q_single_array = Q_total / n_array
        
        ax7_twin = ax7.twinx()
        
        line1 = ax7.plot(d_well_array, n_array, 'b-', linewidth=2.5, label='井数')
        line2 = ax7_twin.plot(d_well_array, q_single_array, 'r--', linewidth=2.5, 
                             label='单井流量')
        
        # 标注当前设计
        ax7.plot([self.d_well], [n], 'bo', markersize=10)
        ax7_twin.plot([self.d_well], [q_single], 'ro', markersize=10)
        
        ax7.set_xlabel('井间距 (m)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('井数（口）', fontsize=11, fontweight='bold', color='b')
        ax7_twin.set_ylabel('单井流量 (m³/d)', fontsize=11, fontweight='bold', color='r')
        ax7.set_title('井间距的影响', fontsize=13, fontweight='bold')
        
        lines = line1 + line2
        labels_leg = [l.get_label() for l in lines]
        ax7.legend(lines, labels_leg, fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        # 图8：计算结果汇总
        ax8 = plt.subplot(3, 3, 8)
        
        results_text = f"""
基坑降水设计结果

【基坑参数】
尺寸：{self.L}m × {self.B}m
开挖深度：{self.d}m
地下水位：{self.water_table}m

【水文地质】
含水层厚度：{self.H}m
渗透系数：{self.k}m/d
影响半径：{self.R}m

【设计结果】
所需降深：{s:.1f}m
等效半径：{r_e:.2f}m
大井流量：{Q0:.1f}m³/d

【井群设计】
井数：{n}口
井间距：{self.d_well}m
井径：{self.r0}m
单井流量：{q_single:.1f}m³/d

【总抽水量】
设计流量：{Q_total:.1f}m³/d
         = {Q_total/24:.1f}m³/h
         = {Q_total/86.4:.1f}L/s

【干扰系数】η = 1.2
"""
        
        ax8.text(0.1, 0.5, results_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax8.axis('off')
        ax8.set_title('计算结果汇总', fontsize=13, fontweight='bold')
        
        # 图9：公式总结
        ax9 = plt.subplot(3, 3, 9)
        
        formula_text = """
基坑降水设计公式

【大井法】
等效半径（矩形）：
r_e = 0.29(L + B)

【裘布依公式】（潜水井）
Q = π·k·(H² - h²) / ln(R/r₀)
h = H - s

【井群设计】
井数：n = 周长 / 井间距
单井流量：q = Q_总 / n

【干扰系数】
Q_总 = η·Q₀
η = 1.2~1.5（经验值）

【降深要求】
s = (d - 水位) + 安全余量
安全余量 ≥ 0.5m
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
        print("基坑降水设计（综合应用）")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  基坑尺寸：L × B = {self.L} m × {self.B} m")
        print(f"  开挖深度：d = {self.d} m")
        print(f"  地下水位：{self.water_table} m（地表以下）")
        print(f"  含水层厚度：H = {self.H} m")
        print(f"  渗透系数：k = {self.k} m/d")
        print(f"  影响半径：R = {self.R} m")
        print(f"  井径：r₀ = {self.r0} m")
        print(f"  设计井间距：{self.d_well} m")
        
        print(f"\n(1) 所需降深计算：")
        print(f"  基坑底面需要在地下水位以下干燥作业")
        print(f"  开挖深度：d = {self.d} m")
        print(f"  地下水位：{self.water_table} m")
        print(f"  需降至：d + 安全余量 = {self.d} + 1.0 = {self.d + 1.0} m")
        
        s = self.required_drawdown()
        print(f"\n  所需降深：")
        print(f"    s = (d - 水位) + 安全余量")
        print(f"      = ({self.d} - {self.water_table}) + 1.0")
        print(f"      = {s} m")
        
        print(f"\n(2) 等效半径计算（大井法）：")
        print(f"  将基坑等效为一口大口径井")
        
        r_e = self.equivalent_radius()
        print(f"\n  矩形基坑等效半径：")
        print(f"    r_e = 0.29(L + B)")
        print(f"        = 0.29 × ({self.L} + {self.B})")
        print(f"        = 0.29 × {self.L + self.B}")
        print(f"        = {r_e:.2f} m")
        
        print(f"\n(3) 大井出水量（裘布依公式）：")
        print(f"  潜水井公式：")
        print(f"    Q = π·k·(H² - h²) / ln(R/r_e)")
        
        h = self.H - s
        print(f"\n  降深后水位：")
        print(f"    h = H - s = {self.H} - {s} = {h} m")
        
        Q0 = self.single_well_discharge(s, r_e)
        print(f"\n  大井流量：")
        print(f"    Q₀ = π × {self.k} × ({self.H}² - {h}²) / ln({self.R}/{r_e:.2f})")
        print(f"       = π × {self.k} × ({self.H**2} - {h**2}) / ln({self.R/r_e:.2f})")
        print(f"       = {np.pi * self.k:.2f} × {self.H**2 - h**2} / {np.log(self.R/r_e):.3f}")
        print(f"       = {Q0:.1f} m³/d")
        
        print(f"\n(4) 井数确定：")
        print(f"  环形布井，沿基坑外侧布置")
        
        perimeter = 2 * (self.L + self.B)
        print(f"\n  基坑周长：")
        print(f"    P = 2(L + B) = 2 × ({self.L} + {self.B}) = {perimeter} m")
        
        n = self.number_of_wells()
        print(f"\n  井数：")
        print(f"    n = P / d_井间距")
        print(f"      = {perimeter} / {self.d_well}")
        print(f"      = {perimeter/self.d_well:.1f}")
        print(f"      ≈ {n} 口（向上取整）")
        
        actual_spacing = perimeter / n
        print(f"\n  实际井间距：{actual_spacing:.2f} m")
        
        print(f"\n(5) 总抽水量：")
        print(f"  考虑群井干扰，需乘以干扰系数η")
        
        eta = 1.2
        Q_total = self.total_discharge(s, eta=eta)
        print(f"\n  干扰系数：η = {eta}")
        print(f"  （经验值：环形布井η=1.2~1.5）")
        
        print(f"\n  总抽水量：")
        print(f"    Q_总 = η × Q₀")
        print(f"        = {eta} × {Q0:.1f}")
        print(f"        = {Q_total:.1f} m³/d")
        
        print(f"\n  单位换算：")
        print(f"    Q_总 = {Q_total/24:.1f} m³/h")
        print(f"        = {Q_total/86.4:.1f} L/s")
        
        q_single = Q_total / n
        print(f"\n  单井平均流量：")
        print(f"    q = Q_总 / n")
        print(f"      = {Q_total:.1f} / {n}")
        print(f"      = {q_single:.1f} m³/d = {q_single/24:.1f} m³/h")
        
        print(f"\n(6) 降水井布置方案：")
        print(f"\n  【布置原则】")
        print(f"    • 环形布井，沿基坑外侧")
        print(f"    • 距基坑边线约5m")
        print(f"    • 均匀分布，井间距{self.d_well}m")
        print(f"    • 共{n}口井")
        
        print(f"\n  【井参数】")
        print(f"    • 井径：{self.r0*2}m（滤管直径）")
        print(f"    • 井深：{self.H+2}m（至含水层底板+2m）")
        print(f"    • 滤管长度：约{self.H-5}m")
        print(f"    • 单井流量：{q_single:.1f}m³/d")
        
        print(f"\n  【降水方案】")
        print(f"    1. 分级降水：")
        print(f"       - 第一级：降深{s/2:.1f}m（7天）")
        print(f"       - 第二级：降深{s:.1f}m（14天）")
        print(f"    2. 边抽水边开挖")
        print(f"    3. 配备备用泵（20%富余量）")
        print(f"    4. 水位监测点：4-6个")
        
        print(f"\n  【设备选型】")
        pump_capacity = q_single / 24 * 1.2  # m³/h，含20%余量
        print(f"    潜水泵流量：≥{pump_capacity:.1f} m³/h")
        print(f"    扬程：≥{s + 5} m（降深+5m余量）")
        print(f"    台数：{n}台（每井1台）+ {int(n*0.2)}台备用")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 大井法：r_e = 0.29(L+B)")
        print("2. 裘布依公式：Q = π·k·(H²-h²)/ln(R/r₀)")
        print("3. 干扰系数：η = 1.2~1.5")
        print("4. 井数：n = 周长/井间距")
        print("5. 分级降水：逐步降深，避免突然降水")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第04章 地下水与渗流 - 题目15：基坑降水设计（综合应用）")
    print("💧" * 35 + "\n")
    
    # 题目参数
    L = 50.0           # 基坑长度50m
    B = 30.0           # 基坑宽度30m
    d = 5.0            # 开挖深度5m
    water_table = 3.0  # 地下水位3m
    H = 15.0           # 含水层厚度15m
    k = 5.0            # 渗透系数5m/d
    R = 100.0          # 影响半径100m
    r0 = 0.15          # 井径0.15m
    d_well = 10.0      # 井间距10m
    
    # 创建基坑降水设计对象
    dewatering = DewateringDesign(L=L, B=B, d=d, water_table=water_table,
                                  H=H, k=k, R=R, r0=r0, d_well=d_well)
    
    # 打印结果
    dewatering.print_results()
    
    # 绘图
    print("\n正在绘制基坑降水设计图...")
    dewatering.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
