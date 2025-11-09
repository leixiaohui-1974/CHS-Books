# -*- coding: utf-8 -*-
"""
第08章 渗流计算 - 题1：裘布依公式应用

问题描述：
    基坑降水工程，基坑长L=50m，宽B=30m
    含水层：M=10m（承压）或H0=10m（无压）
    渗透系数K=0.001 m/s
    影响半径R=100m，降深s0=5m
    
    求：
    1. 承压水井流量（裘布依公式）
    2. 无压水井流量
    3. 所需降水井数量
    4. 井距布置
    5. 降水成本估算

核心公式：
    1. 承压水：Q = 2πKM(H0-hw)/ln(R/r0)
    2. 无压水：Q = πK(H0²-hw²)/ln(R/r0)
    3. 井数：n ≥ Q_total / Q_单井
    4. 降水周期：T = V / Q_total

考试要点：
    - 裘布依公式应用
    - 承压与无压区别
    - 降水井数量计算
    - 工程成本估算

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class DupuitDewatering:
    """裘布依公式降水计算"""
    
    def __init__(self, L: float, B: float, M: float, K: float, 
                 R: float, s0: float, r0: float = 0.2):
        self.L = L  # 基坑长度
        self.B = B  # 基坑宽度
        self.M = M  # 承压含水层厚度
        self.K = K  # 渗透系数
        self.R = R  # 影响半径
        self.s0 = s0  # 降深
        self.r0 = r0  # 井半径
        self.g = 9.8
        
    def confined_well_discharge(self, H0: float = None, hw: float = None) -> float:
        """
        承压水井流量（裘布依公式）
        Q = 2πKM(H0-hw) / ln(R/r0)
        """
        if H0 is None:
            H0 = self.M
        if hw is None:
            hw = H0 - self.s0
            
        Q = 2 * np.pi * self.K * self.M * (H0 - hw) / np.log(self.R / self.r0)
        return Q
    
    def unconfined_well_discharge(self, H0: float = None, hw: float = None) -> float:
        """
        无压水井流量（裘布依公式）
        Q = πK(H0²-hw²) / ln(R/r0)
        """
        if H0 is None:
            H0 = self.M
        if hw is None:
            hw = H0 - self.s0
            
        Q = np.pi * self.K * (H0**2 - hw**2) / np.log(self.R / self.r0)
        return Q
    
    def pit_volume(self) -> float:
        """基坑涌水量估算"""
        # 简化：按等效圆形基坑
        A = self.L * self.B
        r_equiv = np.sqrt(A / np.pi)
        
        # 承压水
        Q = self.confined_well_discharge()
        
        return Q
    
    def well_count(self, Q_single: float, safety_factor: float = 1.3) -> int:
        """降水井数量"""
        Q_pit = self.pit_volume()
        Q_required = Q_pit * safety_factor
        n = int(np.ceil(Q_required / Q_single))
        return n
    
    def well_layout(self, n: int) -> Dict:
        """降水井布置"""
        # 基坑周长
        perimeter = 2 * (self.L + self.B)
        
        # 井距
        spacing = perimeter / n
        
        # 布置位置（简化为矩形周边均布）
        positions = []
        
        # 长边
        n_long = int(n * self.L / perimeter)
        for i in range(n_long):
            x = i * self.L / n_long
            positions.append({'x': x, 'y': 0, 'side': '南'})
            positions.append({'x': x, 'y': self.B, 'side': '北'})
        
        # 短边
        n_short = n - 2 * n_long
        for i in range(n_short):
            y = i * self.B / n_short
            positions.append({'x': 0, 'y': y, 'side': '西'})
            positions.append({'x': self.L, 'y': y, 'side': '东'})
        
        return {
            'count': n,
            'spacing': spacing,
            'positions': positions[:n]
        }
    
    def dewatering_time(self, Q_total: float, porosity: float = 0.3) -> float:
        """降水周期"""
        V = self.L * self.B * self.s0 * porosity  # 需排水体积
        T = V / Q_total  # 时间（秒）
        return T / (24 * 3600)  # 转换为天
    
    def cost_estimate(self, n: int, T_days: float) -> Dict:
        """成本估算"""
        # 单价（示例）
        price_well = 5000  # 单井施工费（元）
        price_pump = 3000  # 水泵费用（元）
        price_power = 0.6  # 电价（元/kWh）
        power_per_well = 5.5  # 单井功率（kW）
        
        # 施工费
        cost_construction = n * (price_well + price_pump)
        
        # 运行费
        hours = T_days * 24
        energy = n * power_per_well * hours
        cost_operation = energy * price_power
        
        # 总费用
        total = cost_construction + cost_operation
        
        return {
            'construction': cost_construction,
            'operation': cost_operation,
            'total': total,
            'per_day': cost_operation / T_days
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        Q_conf = self.confined_well_discharge()
        Q_unconf = self.unconfined_well_discharge()
        n_wells = self.well_count(Q_conf)
        layout = self.well_layout(n_wells)
        
        # 1. 基坑与降水井布置
        ax1 = plt.subplot(3, 3, 1)
        
        # 基坑轮廓
        ax1.plot([0, self.L, self.L, 0, 0], [0, 0, self.B, self.B, 0], 
                'k-', linewidth=2, label='基坑')
        ax1.fill([0, self.L, self.L, 0], [0, 0, self.B, self.B], 
                color='lightgray', alpha=0.3)
        
        # 降水井
        for pos in layout['positions']:
            ax1.plot(pos['x'], pos['y'], 'bo', markersize=8)
            ax1.text(pos['x'], pos['y']+1, f"井{layout['positions'].index(pos)+1}", 
                    fontsize=7, ha='center')
        
        # 影响范围（示意）
        if len(layout['positions']) > 0:
            pos0 = layout['positions'][0]
            circle = plt.Circle((pos0['x'], pos0['y']), self.R*0.3, 
                               color='blue', alpha=0.1, label=f'影响半径R={self.R}m')
            ax1.add_patch(circle)
        
        ax1.set_xlabel('长度 (m)', fontsize=10)
        ax1.set_ylabel('宽度 (m)', fontsize=10)
        ax1.set_title(f'降水井布置（共{n_wells}口井）', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        ax1.set_xlim(-10, self.L+10)
        ax1.set_ylim(-10, self.B+10)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '降水参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'基坑尺寸: {self.L}m × {self.B}m', fontsize=10)
        ax2.text(0.1, 0.72, f'含水层厚度: M = {self.M} m', fontsize=10)
        ax2.text(0.1, 0.62, f'渗透系数: K = {self.K} m/s', fontsize=10)
        ax2.text(0.1, 0.52, f'影响半径: R = {self.R} m', fontsize=10)
        ax2.text(0.1, 0.42, f'降深: s₀ = {self.s0} m', fontsize=10)
        ax2.text(0.1, 0.30, f'承压井流量: Q = {Q_conf*1000:.2f} L/s', fontsize=10, color='blue')
        ax2.text(0.1, 0.20, f'无压井流量: Q = {Q_unconf*1000:.2f} L/s', fontsize=10, color='green')
        ax2.text(0.1, 0.10, f'降水井数: n = {n_wells} 口', fontsize=11, color='red', fontweight='bold')
        ax2.text(0.1, 0.00, f'井距: {layout["spacing"]:.1f} m', fontsize=10)
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 降深-流量关系
        ax3 = plt.subplot(3, 3, 3)
        
        s_range = np.linspace(1, self.M*0.9, 50)
        Q_conf_range = []
        Q_unconf_range = []
        
        for s in s_range:
            hw = self.M - s
            Q_conf_range.append(self.confined_well_discharge(self.M, hw) * 1000)
            Q_unconf_range.append(self.unconfined_well_discharge(self.M, hw) * 1000)
        
        ax3.plot(s_range, Q_conf_range, 'b-', linewidth=2, label='承压水')
        ax3.plot(s_range, Q_unconf_range, 'g-', linewidth=2, label='无压水')
        ax3.plot(self.s0, Q_conf*1000, 'ro', markersize=10, label=f's₀={self.s0}m')
        
        ax3.set_xlabel('降深 s (m)', fontsize=10)
        ax3.set_ylabel('单井流量 Q (L/s)', fontsize=10)
        ax3.set_title('降深-流量关系', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 承压vs无压流量对比
        ax4 = plt.subplot(3, 3, 4)
        
        bars = ax4.bar(['承压水', '无压水'], [Q_conf*1000, Q_unconf*1000],
                      color=['skyblue', 'lightgreen'], alpha=0.7, edgecolor='black')
        
        ax4.set_ylabel('单井流量 (L/s)', fontsize=10)
        ax4.set_title('承压vs无压流量对比', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for bar, Q in zip(bars, [Q_conf*1000, Q_unconf*1000]):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{Q:.2f}\nL/s', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 5. 渗透系数影响
        ax5 = plt.subplot(3, 3, 5)
        
        K_range = np.logspace(-4, -2, 50)  # 0.0001~0.01 m/s
        Q_K_range = [2*np.pi*K*self.M*self.s0/np.log(self.R/self.r0)*1000 for K in K_range]
        
        ax5.plot(K_range, Q_K_range, 'b-', linewidth=2)
        ax5.plot(self.K, Q_conf*1000, 'ro', markersize=10, label=f'K={self.K}m/s')
        
        ax5.set_xlabel('渗透系数 K (m/s)', fontsize=10)
        ax5.set_ylabel('单井流量 Q (L/s)', fontsize=10)
        ax5.set_title('渗透系数影响', fontsize=12, fontweight='bold')
        ax5.set_xscale('log')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 影响半径影响
        ax6 = plt.subplot(3, 3, 6)
        
        R_range = np.linspace(50, 200, 50)
        Q_R_range = [2*np.pi*self.K*self.M*self.s0/np.log(R/self.r0)*1000 for R in R_range]
        
        ax6.plot(R_range, Q_R_range, 'g-', linewidth=2)
        ax6.plot(self.R, Q_conf*1000, 'ro', markersize=10, label=f'R={self.R}m')
        
        ax6.set_xlabel('影响半径 R (m)', fontsize=10)
        ax6.set_ylabel('单井流量 Q (L/s)', fontsize=10)
        ax6.set_title('影响半径影响', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 降水时间估算
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        Q_total = Q_conf * n_wells
        T_days = self.dewatering_time(Q_total)
        
        ax7.text(0.5, 0.95, '降水周期分析', fontsize=11, ha='center', fontweight='bold')
        ax7.text(0.1, 0.80, f'单井流量: {Q_conf*1000:.2f} L/s', fontsize=10)
        ax7.text(0.1, 0.70, f'井数: {n_wells} 口', fontsize=10)
        ax7.text(0.1, 0.60, f'总流量: {Q_total*1000:.2f} L/s', fontsize=10, color='blue')
        ax7.text(0.1, 0.45, f'需排水量: {self.L*self.B*self.s0:.1f} m³', fontsize=10)
        ax7.text(0.1, 0.35, f'孔隙率: 30%', fontsize=9, color='gray')
        ax7.text(0.1, 0.20, f'降水周期: {T_days:.1f} 天', fontsize=11, color='red', fontweight='bold')
        ax7.text(0.1, 0.05, '（含补给，实际需更长）', fontsize=9, color='orange')
        
        ax7.set_title('时间估算', fontsize=12, fontweight='bold')
        
        # 8. 成本估算
        ax8 = plt.subplot(3, 3, 8)
        
        cost = self.cost_estimate(n_wells, T_days)
        
        labels = ['施工费', '运行费']
        sizes = [cost['construction'], cost['operation']]
        colors = ['gold', 'lightcoral']
        explode = (0.05, 0.05)
        
        ax8.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
        
        ax8.text(0, -1.5, f'总费用: {cost["total"]/10000:.1f} 万元', 
                ha='center', fontsize=11, color='red', fontweight='bold')
        ax8.text(0, -1.7, f'日运行费: {cost["per_day"]:.0f} 元', 
                ha='center', fontsize=9, color='blue')
        ax8.set_title('费用估算', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['基坑尺寸', f'{self.L}×{self.B}', 'm'],
            ['降深', f'{self.s0:.1f}', 'm'],
            ['单井流量(承压)', f'{Q_conf*1000:.2f}', 'L/s'],
            ['单井流量(无压)', f'{Q_unconf*1000:.2f}', 'L/s'],
            ['降水井数', f'{n_wells}', '口'],
            ['井距', f'{layout["spacing"]:.1f}', 'm'],
            ['降水周期', f'{T_days:.1f}', '天'],
            ['总费用', f'{cost["total"]/10000:.1f}', '万元']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        table[(5, 1)].set_facecolor('#90EE90')
        table[(5, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch08_problem01_dupuit_formula.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch08_problem01_dupuit_formula.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第08章 渗流计算 - 题1：裘布依公式应用")
        print("="*70)
        
        Q_conf = self.confined_well_discharge()
        Q_unconf = self.unconfined_well_discharge()
        
        print(f"\n【工程参数】")
        print(f"基坑尺寸: {self.L}m × {self.B}m")
        print(f"含水层厚度: M = {self.M} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400:.2f} m/d")
        print(f"影响半径: R = {self.R} m")
        print(f"降深要求: s₀ = {self.s0} m")
        print(f"井半径: r₀ = {self.r0} m")
        
        print(f"\n【承压水井流量】")
        print(f"Q = 2πKM(H₀-hw) / ln(R/r₀)")
        print(f"  = 2π×{self.K}×{self.M}×{self.s0} / ln({self.R}/{self.r0})")
        print(f"  = {Q_conf:.6f} m³/s = {Q_conf*1000:.2f} L/s")
        
        print(f"\n【无压水井流量】")
        hw = self.M - self.s0
        print(f"Q = πK(H₀²-hw²) / ln(R/r₀)")
        print(f"  = π×{self.K}×({self.M}²-{hw}²) / ln({self.R}/{self.r0})")
        print(f"  = {Q_unconf:.6f} m³/s = {Q_unconf*1000:.2f} L/s")
        
        n_wells = self.well_count(Q_conf)
        layout = self.well_layout(n_wells)
        
        print(f"\n【降水井设计】")
        print(f"所需井数: n = {n_wells} 口")
        print(f"井距: {layout['spacing']:.1f} m")
        print(f"总流量: {Q_conf*n_wells*1000:.2f} L/s")
        
        Q_total = Q_conf * n_wells
        T_days = self.dewatering_time(Q_total)
        
        print(f"\n【降水周期】")
        print(f"降水周期: {T_days:.1f} 天（理论值）")
        print(f"建议: {T_days*1.5:.1f}~{T_days*2:.1f} 天（考虑补给）")
        
        cost = self.cost_estimate(n_wells, T_days)
        
        print(f"\n【费用估算】")
        print(f"施工费: {cost['construction']/10000:.1f} 万元")
        print(f"运行费: {cost['operation']/10000:.1f} 万元")
        print(f"总费用: {cost['total']/10000:.1f} 万元")
        
        print(f"\n✓ 裘布依公式降水计算完成")
        print(f"\n{'='*70}\n")


def main():
    L = 50
    B = 30
    M = 10
    K = 0.001
    R = 100
    s0 = 5
    
    dew = DupuitDewatering(L, B, M, K, R, s0)
    dew.print_results()
    dew.plot_analysis()


if __name__ == "__main__":
    main()
