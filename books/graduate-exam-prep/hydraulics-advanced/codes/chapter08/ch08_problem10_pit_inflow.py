# -*- coding: utf-8 -*-
"""
第08章 渗流计算 - 题10：基坑涌水量计算

问题描述：
    矩形基坑开挖，长L = 60m，宽B = 40m，深度H = 8m
    承压含水层：厚度M = 12m，顶板埋深H0 = 5m
    渗透系数K = 0.0008 m/s
    影响半径R = 150m，降至坑底
    
    求：
    1. 基坑涌水量Q（等效圆法、经验公式）
    2. 单井抽水量（承压井）
    3. 所需井数与布置
    4. 抽水周期与总水量
    5. 抽水费用估算

核心公式：
    1. 等效圆法：r0 = √(LB/π)
    2. 承压井：Q = 2πKM·s/ln(R/r0)
    3. 涌水量修正：Q' = α·Q（形状系数）
    4. 抽水周期：T = V_pit/(Q-Q_补给)

考试要点：
    - 基坑涌水量计算方法
    - 等效圆法应用
    - 井数确定
    - 工程实践经验

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PitInflow:
    """基坑涌水量计算"""
    
    def __init__(self, L: float, B: float, H: float, M: float, 
                 H0: float, K: float, R: float):
        self.L = L  # 基坑长度
        self.B = B  # 基坑宽度
        self.H = H  # 开挖深度
        self.M = M  # 含水层厚度
        self.H0 = H0  # 承压水顶板埋深
        self.K = K  # 渗透系数
        self.R = R  # 影响半径
        self.g = 9.8
        
    def equivalent_radius(self) -> float:
        """等效圆半径"""
        A = self.L * self.B
        r0 = np.sqrt(A / np.pi)
        return r0
    
    def drawdown(self) -> float:
        """降深"""
        # 从承压水顶板到坑底的降深
        s = self.H - self.H0
        return s
    
    def inflow_confined(self) -> float:
        """
        承压水基坑涌水量（等效圆法）
        Q = 2πKM·s/ln(R/r0)
        """
        r0 = self.equivalent_radius()
        s = self.drawdown()
        Q = 2 * np.pi * self.K * self.M * s / np.log(self.R / r0)
        return Q
    
    def shape_factor(self) -> float:
        """
        形状系数α
        矩形基坑修正
        α = 1.1~1.3（经验值）
        """
        ratio = self.L / self.B
        if ratio <= 2:
            alpha = 1.1
        elif ratio <= 4:
            alpha = 1.2
        else:
            alpha = 1.3
        return alpha
    
    def inflow_corrected(self) -> float:
        """修正后涌水量"""
        Q = self.inflow_confined()
        alpha = self.shape_factor()
        Q_corrected = alpha * Q
        return Q_corrected
    
    def single_well_discharge(self, r_well: float = 0.2) -> float:
        """单井抽水量"""
        s = self.drawdown()
        Q_well = 2 * np.pi * self.K * self.M * s / np.log(self.R / r_well)
        return Q_well
    
    def well_count(self, safety_factor: float = 1.3) -> int:
        """抽水井数量"""
        Q_pit = self.inflow_corrected()
        Q_well = self.single_well_discharge()
        
        # 考虑安全系数
        Q_required = Q_pit * safety_factor
        n = int(np.ceil(Q_required / Q_well))
        
        return n
    
    def well_layout(self, n: int) -> Dict:
        """抽水井布置"""
        perimeter = 2 * (self.L + self.B)
        spacing = perimeter / n
        
        # 沿基坑周边布置
        positions = []
        
        # 长边（两侧）
        n_long = max(int(n * self.L / perimeter), 1)
        for i in range(n_long):
            x = i * self.L / max(n_long-1, 1) if n_long > 1 else self.L/2
            positions.append({'x': x, 'y': 0, 'side': '南'})
            positions.append({'x': x, 'y': self.B, 'side': '北'})
        
        # 短边（两侧）
        remaining = n - 2 * n_long
        if remaining > 0:
            n_short = max(remaining // 2, 1)
            for i in range(n_short):
                y = i * self.B / max(n_short-1, 1) if n_short > 1 else self.B/2
                positions.append({'x': 0, 'y': y, 'side': '西'})
                if len(positions) < n:
                    positions.append({'x': self.L, 'y': y, 'side': '东'})
        
        return {
            'count': min(n, len(positions)),
            'spacing': spacing,
            'positions': positions[:n]
        }
    
    def pumping_period(self, porosity: float = 0.25) -> float:
        """抽水周期（天）"""
        # 基坑体积
        V_pit = self.L * self.B * self.H
        
        # 需排水体积（考虑孔隙率）
        V_water = V_pit * porosity
        
        # 抽水量
        Q_pump = self.inflow_corrected()
        
        # 补给量（假设为涌水量的30%）
        Q_recharge = Q_pump * 0.3
        
        # 净抽水量
        Q_net = Q_pump - Q_recharge
        
        # 抽水周期（秒）
        if Q_net > 0:
            T_sec = V_water / Q_net
            T_days = T_sec / (24 * 3600)
        else:
            T_days = float('inf')
        
        return T_days
    
    def cost_estimate(self, n: int, T_days: float) -> Dict:
        """费用估算"""
        # 单价
        price_well = 8000  # 井施工费（元/口）
        price_pump = 5000  # 水泵费用（元/台）
        price_power = 0.6  # 电价（元/kWh）
        power_per_well = 7.5  # 单井功率（kW）
        
        # 施工费
        cost_construction = n * (price_well + price_pump)
        
        # 运行费（假设抽水30天）
        T_operation = min(T_days, 30)
        hours = T_operation * 24
        energy = n * power_per_well * hours
        cost_operation = energy * price_power
        
        # 维护费（10%）
        cost_maintenance = cost_operation * 0.1
        
        # 总费用
        total = cost_construction + cost_operation + cost_maintenance
        
        return {
            'construction': cost_construction,
            'operation': cost_operation,
            'maintenance': cost_maintenance,
            'total': total,
            'per_day': cost_operation / T_operation
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        r0 = self.equivalent_radius()
        s = self.drawdown()
        Q_conf = self.inflow_confined()
        Q_corr = self.inflow_corrected()
        alpha = self.shape_factor()
        Q_well = self.single_well_discharge()
        n = self.well_count()
        layout = self.well_layout(n)
        T = self.pumping_period()
        cost = self.cost_estimate(n, T)
        
        # 1. 基坑平面与抽水井布置
        ax1 = plt.subplot(3, 3, 1)
        
        # 基坑轮廓
        ax1.plot([0, self.L, self.L, 0, 0], [0, 0, self.B, self.B, 0], 
                'k-', linewidth=3, label='基坑')
        ax1.fill([0, self.L, self.L, 0], [0, 0, self.B, self.B], 
                color='lightgray', alpha=0.3)
        
        # 等效圆
        circle = plt.Circle((self.L/2, self.B/2), r0, 
                           color='blue', fill=False, linestyle='--', 
                           linewidth=2, label=f'等效圆r₀={r0:.1f}m')
        ax1.add_patch(circle)
        
        # 抽水井
        for pos in layout['positions']:
            ax1.plot(pos['x'], pos['y'], 'bo', markersize=10)
            ax1.text(pos['x'], pos['y']+2, f"{layout['positions'].index(pos)+1}", 
                    fontsize=8, ha='center', fontweight='bold')
        
        # 影响范围（示意）
        if len(layout['positions']) > 0:
            pos0 = layout['positions'][0]
            influence = plt.Circle((pos0['x'], pos0['y']), self.R*0.15, 
                                  color='red', alpha=0.1, label='影响范围')
            ax1.add_patch(influence)
        
        ax1.set_xlabel('长度 (m)', fontsize=10)
        ax1.set_ylabel('宽度 (m)', fontsize=10)
        ax1.set_title(f'抽水井布置（共{n}口井）', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        ax1.set_xlim(-10, self.L+10)
        ax1.set_ylim(-10, self.B+10)
        
        # 2. 计算参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '涌水量参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'基坑尺寸: {self.L}×{self.B}×{self.H} m', fontsize=10)
        ax2.text(0.1, 0.72, f'等效半径: r₀ = {r0:.2f} m', fontsize=10)
        ax2.text(0.1, 0.62, f'含水层厚: M = {self.M} m', fontsize=10)
        ax2.text(0.1, 0.52, f'降深: s = {s:.2f} m', fontsize=10)
        ax2.text(0.1, 0.42, f'渗透系数: K = {self.K} m/s', fontsize=10)
        ax2.text(0.1, 0.30, f'理论涌水量: {Q_conf*1000:.2f} L/s', fontsize=10, color='blue')
        ax2.text(0.1, 0.20, f'形状系数: α = {alpha:.2f}', fontsize=10, color='green')
        ax2.text(0.1, 0.10, f'修正涌水量: {Q_corr*1000:.2f} L/s', fontsize=11, color='red', fontweight='bold')
        ax2.text(0.1, 0.00, f'单井流量: {Q_well*1000:.2f} L/s', fontsize=10)
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 涌水量计算对比
        ax3 = plt.subplot(3, 3, 3)
        
        methods = ['理论值\n(等效圆)', '修正值\n(×α)', f'总需求\n(×{1.3})']
        flows = [Q_conf*1000, Q_corr*1000, Q_corr*1000*1.3]
        colors = ['skyblue', 'lightgreen', 'lightcoral']
        
        bars = ax3.bar(methods, flows, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_ylabel('涌水量 (L/s)', fontsize=10)
        ax3.set_title('涌水量计算对比', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        for bar, flow in zip(bars, flows):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{flow:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 4. 降深-涌水量关系
        ax4 = plt.subplot(3, 3, 4)
        
        s_range = np.linspace(1, self.M*0.8, 50)
        Q_s = [2*np.pi*self.K*self.M*s_val/np.log(self.R/r0)*1000 for s_val in s_range]
        
        ax4.plot(s_range, Q_s, 'b-', linewidth=2, label='Q(s)')
        ax4.plot(s, Q_conf*1000, 'ro', markersize=10, label=f's={s:.1f}m')
        
        ax4.set_xlabel('降深 s (m)', fontsize=10)
        ax4.set_ylabel('涌水量 Q (L/s)', fontsize=10)
        ax4.set_title('降深-涌水量关系', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 渗透系数影响
        ax5 = plt.subplot(3, 3, 5)
        
        K_range = np.logspace(-4, -2, 50)
        Q_K = [2*np.pi*K_val*self.M*s/np.log(self.R/r0)*1000 for K_val in K_range]
        
        ax5.plot(K_range, Q_K, 'g-', linewidth=2)
        ax5.plot(self.K, Q_conf*1000, 'ro', markersize=10, label=f'K={self.K}m/s')
        
        ax5.set_xlabel('渗透系数 K (m/s)', fontsize=10)
        ax5.set_ylabel('涌水量 Q (L/s)', fontsize=10)
        ax5.set_title('渗透系数影响', fontsize=12, fontweight='bold')
        ax5.set_xscale('log')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 井数-总流量关系
        ax6 = plt.subplot(3, 3, 6)
        
        n_range = np.arange(1, 20)
        Q_total_range = [n_val * Q_well * 1000 for n_val in n_range]
        
        ax6.plot(n_range, Q_total_range, 'b-o', linewidth=2, markersize=4)
        ax6.axhline(Q_corr*1000*1.3, color='r', linestyle='--', linewidth=2, 
                   label=f'需求量={Q_corr*1000*1.3:.1f}L/s')
        ax6.plot(n, n*Q_well*1000, 'go', markersize=10, label=f'n={n}口井')
        
        ax6.set_xlabel('抽水井数 n', fontsize=10)
        ax6.set_ylabel('总抽水量 (L/s)', fontsize=10)
        ax6.set_title('井数-总流量关系', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 抽水周期分析
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        V_pit = self.L * self.B * self.H
        V_water = V_pit * 0.25
        
        ax7.text(0.5, 0.95, '抽水周期', fontsize=11, ha='center', fontweight='bold')
        ax7.text(0.1, 0.80, f'基坑体积: {V_pit:.1f} m³', fontsize=10)
        ax7.text(0.1, 0.70, f'排水体积: {V_water:.1f} m³', fontsize=10)
        ax7.text(0.1, 0.60, f'孔隙率: 25%', fontsize=9, color='gray')
        ax7.text(0.1, 0.48, f'涌水量: {Q_corr*1000:.1f} L/s', fontsize=10, color='blue')
        ax7.text(0.1, 0.38, f'补给量: {Q_corr*1000*0.3:.1f} L/s (30%)', fontsize=9, color='orange')
        ax7.text(0.1, 0.28, f'净抽水量: {Q_corr*1000*0.7:.1f} L/s', fontsize=10, color='green')
        ax7.text(0.1, 0.15, f'抽水周期: {T:.1f} 天', fontsize=11, color='red', fontweight='bold')
        ax7.text(0.1, 0.03, '（理论值，实际需更长）', fontsize=9, color='gray')
        
        ax7.set_title('时间估算', fontsize=12, fontweight='bold')
        
        # 8. 费用估算
        ax8 = plt.subplot(3, 3, 8)
        
        labels = ['施工费', '运行费', '维护费']
        sizes = [cost['construction'], cost['operation'], cost['maintenance']]
        colors = ['gold', 'lightblue', 'lightgreen']
        explode = (0.05, 0.05, 0.05)
        
        ax8.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9, 'fontweight': 'bold'})
        
        ax8.text(0, -1.5, f'总费用: {cost["total"]/10000:.1f} 万元', 
                ha='center', fontsize=11, color='red', fontweight='bold')
        ax8.text(0, -1.7, f'日运行费: {cost["per_day"]:.0f} 元', 
                ha='center', fontsize=9, color='blue')
        ax8.set_title('费用分析', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '数值', '单位'],
            ['基坑尺寸', f'{self.L}×{self.B}', 'm'],
            ['开挖深度', f'{self.H:.1f}', 'm'],
            ['等效半径', f'{r0:.2f}', 'm'],
            ['降深', f'{s:.2f}', 'm'],
            ['修正涌水量', f'{Q_corr*1000:.2f}', 'L/s'],
            ['抽水井数', f'{n}', '口'],
            ['井距', f'{layout["spacing"]:.1f}', 'm'],
            ['抽水周期', f'{T:.1f}', '天'],
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
        plt.savefig('/tmp/ch08_problem10_pit_inflow.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch08_problem10_pit_inflow.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第08章 渗流计算 - 题10：基坑涌水量计算")
        print("="*70)
        
        r0 = self.equivalent_radius()
        s = self.drawdown()
        Q_conf = self.inflow_confined()
        Q_corr = self.inflow_corrected()
        alpha = self.shape_factor()
        Q_well = self.single_well_discharge()
        n = self.well_count()
        layout = self.well_layout(n)
        T = self.pumping_period()
        cost = self.cost_estimate(n, T)
        
        print(f"\n【基坑参数】")
        print(f"基坑尺寸: {self.L}m × {self.B}m × {self.H}m")
        print(f"含水层厚度: M = {self.M} m")
        print(f"顶板埋深: H₀ = {self.H0} m")
        print(f"渗透系数: K = {self.K} m/s = {self.K*86400:.2f} m/d")
        print(f"影响半径: R = {self.R} m")
        
        print(f"\n【等效圆法】")
        print(f"基坑面积: A = {self.L}×{self.B} = {self.L*self.B} m²")
        print(f"等效半径: r₀ = √(A/π) = {r0:.2f} m")
        print(f"降深: s = {s:.2f} m")
        
        print(f"\n【涌水量计算】")
        print(f"理论涌水量（承压井公式）：")
        print(f"Q = 2πKM·s/ln(R/r₀)")
        print(f"  = 2π×{self.K}×{self.M}×{s}/ln({self.R}/{r0:.2f})")
        print(f"  = {Q_conf:.6f} m³/s = {Q_conf*1000:.2f} L/s")
        
        print(f"\n形状修正（矩形基坑）：")
        print(f"形状系数: α = {alpha:.2f}")
        print(f"修正涌水量: Q' = α×Q = {Q_corr:.6f} m³/s = {Q_corr*1000:.2f} L/s")
        
        print(f"\n【抽水井设计】")
        print(f"单井流量: {Q_well*1000:.2f} L/s")
        print(f"所需井数: n = {n} 口（含1.3安全系数）")
        print(f"井距: {layout['spacing']:.1f} m")
        print(f"总抽水量: {n*Q_well*1000:.2f} L/s")
        
        print(f"\n【抽水周期】")
        print(f"抽水周期: {T:.1f} 天（理论值）")
        print(f"建议: {T*1.5:.1f}~{T*2:.1f} 天（考虑补给和安全）")
        
        print(f"\n【费用估算】")
        print(f"施工费: {cost['construction']/10000:.1f} 万元")
        print(f"运行费: {cost['operation']/10000:.1f} 万元")
        print(f"维护费: {cost['maintenance']/10000:.1f} 万元")
        print(f"总费用: {cost['total']/10000:.1f} 万元")
        
        print(f"\n✓ 基坑涌水量计算完成")
        print(f"\n{'='*70}\n")


def main():
    L = 60
    B = 40
    H = 8
    M = 12
    H0 = 5
    K = 0.0008
    R = 150
    
    pit = PitInflow(L, B, H, M, H0, K, R)
    pit.print_results()
    pit.plot_analysis()


if __name__ == "__main__":
    main()
