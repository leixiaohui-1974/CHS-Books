# -*- coding: utf-8 -*-
"""
第10章 堰闸水力计算 - 题13：堰闸综合应用

问题描述：
    水利枢纽包含：
    - 宽顶堰：b_weir = 10m，P_weir = 3m
    - 闸门：b_gate = 8m，e = 1.2m，P_gate = 3m
    - 上游水位：Z_up = 8m
    - 下游水位：Z_down = 4m
    
    求：
    1. 堰流流量与闸孔流量
    2. 总流量与分配比例
    3. 不同运行工况分析
    4. 优化调度方案
    5. 消能设计（水跃）

核心公式：
    - 堰流：Q_weir = m·b·H^(3/2)·√(2g)
    - 闸流：Q_gate = μ·b·e·√(2gH)
    - 总流量：Q_total = Q_weir + Q_gate
    - 水跃共轭深：h2 = (h1/2)(√(1+8Fr²)-1)

考试要点：
    - 堰闸联合运行
    - 流量分配
    - 工况分析
    - 优化调度

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ComprehensiveSystem:
    """堰闸综合系统"""
    
    def __init__(self, b_weir: float, P_weir: float, b_gate: float, e: float, 
                 P_gate: float, Z_up: float, Z_down: float):
        self.b_weir = b_weir  # 堰宽
        self.P_weir = P_weir  # 堰高
        self.b_gate = b_gate  # 闸宽
        self.e = e  # 闸门开度
        self.P_gate = P_gate  # 闸底高程
        self.Z_up = Z_up  # 上游水位
        self.Z_down = Z_down  # 下游水位
        self.g = 9.8
        
        # 流量系数
        self.m_weir = 0.385  # 宽顶堰
        self.mu_gate = 0.60  # 自由出流闸门
        self.mu_s_gate = 0.85  # 淹没出流闸门
        
    def weir_head(self) -> float:
        """堰上水头"""
        H_weir = self.Z_up - self.P_weir
        return H_weir
    
    def weir_discharge(self) -> float:
        """堰流流量"""
        H = self.weir_head()
        if H > 0:
            Q_weir = self.m_weir * self.b_weir * (H ** 1.5) * np.sqrt(2 * self.g)
        else:
            Q_weir = 0
        return Q_weir
    
    def gate_head(self) -> float:
        """闸前水头"""
        H_gate = self.Z_up - self.P_gate
        return H_gate
    
    def gate_discharge(self) -> float:
        """闸孔流量"""
        H = self.gate_head()
        h_tail = self.Z_down - self.P_gate
        
        # 判别自由/淹没
        epsilon = 0.62
        hc = epsilon * self.e
        
        if hc / h_tail < 0.7:  # 自由出流
            Q_gate = self.mu_gate * self.b_gate * self.e * np.sqrt(2 * self.g * H)
        else:  # 淹没出流
            H_down = self.Z_down - self.P_gate
            Q_gate = self.mu_s_gate * self.b_gate * self.e * np.sqrt(2 * self.g * (H - H_down))
        
        return Q_gate
    
    def total_discharge(self) -> Dict:
        """总流量及分配"""
        Q_weir = self.weir_discharge()
        Q_gate = self.gate_discharge()
        Q_total = Q_weir + Q_gate
        
        ratio_weir = Q_weir / Q_total if Q_total > 0 else 0
        ratio_gate = Q_gate / Q_total if Q_total > 0 else 0
        
        return {
            'Q_weir': Q_weir,
            'Q_gate': Q_gate,
            'Q_total': Q_total,
            'ratio_weir': ratio_weir,
            'ratio_gate': ratio_gate
        }
    
    def operating_scenarios(self) -> List[Dict]:
        """不同运行工况"""
        scenarios = []
        
        # 工况1：当前状态
        scenarios.append({
            'name': '工况1-当前',
            'Z_up': self.Z_up,
            'e': self.e,
            'Q': self.total_discharge()
        })
        
        # 工况2：增大开度
        sys_temp = ComprehensiveSystem(self.b_weir, self.P_weir, self.b_gate, 
                                       self.e*1.5, self.P_gate, self.Z_up, self.Z_down)
        scenarios.append({
            'name': '工况2-大开度',
            'Z_up': self.Z_up,
            'e': self.e*1.5,
            'Q': sys_temp.total_discharge()
        })
        
        # 工况3：高水位
        sys_temp = ComprehensiveSystem(self.b_weir, self.P_weir, self.b_gate, 
                                       self.e, self.P_gate, self.Z_up+1, self.Z_down)
        scenarios.append({
            'name': '工况3-高水位',
            'Z_up': self.Z_up+1,
            'e': self.e,
            'Q': sys_temp.total_discharge()
        })
        
        # 工况4：只开闸门
        sys_temp = ComprehensiveSystem(0, self.P_weir, self.b_gate, 
                                       self.e, self.P_gate, self.Z_up, self.Z_down)
        scenarios.append({
            'name': '工况4-仅闸门',
            'Z_up': self.Z_up,
            'e': self.e,
            'Q': sys_temp.total_discharge()
        })
        
        return scenarios
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        Q_info = self.total_discharge()
        
        # 1. 堰闸布置示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 堰体
        x_weir = [0, 0, 3, 3, 5]
        y_weir = [0, self.P_weir, self.P_weir, self.P_weir, 0]
        ax1.fill(x_weir, y_weir, color='gray', alpha=0.5, label='堰')
        
        # 闸门
        x_gate = [6, 6, 6, 6+self.b_gate/3, 6+self.b_gate/3]
        y_gate = [0, self.P_gate, self.P_gate+self.e, self.P_gate+self.e, 0]
        ax1.fill(x_gate, y_gate, color='brown', alpha=0.5, label='闸')
        ax1.plot([6, 6], [self.P_gate, self.P_gate+self.e], 'k-', linewidth=4)
        
        # 水位线
        ax1.axhline(self.Z_up, color='blue', linestyle='--', linewidth=2, label=f'上游Z={self.Z_up}m')
        ax1.axhline(self.Z_down, color='green', linestyle='--', linewidth=2, label=f'下游Z={self.Z_down}m')
        
        # 标注
        ax1.text(1.5, self.P_weir-0.5, f'堰宽\n{self.b_weir}m', ha='center', fontsize=9)
        ax1.text(6+self.b_gate/6, self.P_gate-0.5, f'闸宽\n{self.b_gate}m', ha='center', fontsize=9)
        ax1.text(-0.5, self.Z_up+0.3, f'H_堰={self.weir_head():.1f}m', fontsize=9, color='red', fontweight='bold')
        ax1.text(5.3, self.Z_up+0.3, f'H_闸={self.gate_head():.1f}m', fontsize=9, color='red', fontweight='bold')
        
        ax1.set_xlim(-1, 9)
        ax1.set_ylim(-1, self.Z_up+1.5)
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('堰闸布置示意', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. 流量分配
        ax2 = plt.subplot(3, 3, 2)
        
        labels = ['堰流', '闸流']
        sizes = [Q_info['Q_weir'], Q_info['Q_gate']]
        colors = ['skyblue', 'lightcoral']
        explode = (0.05, 0.05)
        
        ax2.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
        
        ax2.text(0, -1.5, f'总流量: {Q_info["Q_total"]:.2f} m³/s', 
                ha='center', fontsize=11, color='red', fontweight='bold')
        ax2.set_title('流量分配', fontsize=12, fontweight='bold')
        
        # 3. 上游水位-流量关系
        ax3 = plt.subplot(3, 3, 3)
        
        Z_up_range = np.linspace(self.P_weir+0.5, self.Z_up+2, 50)
        Q_total_range = []
        Q_weir_range = []
        Q_gate_range = []
        
        for Z in Z_up_range:
            sys_temp = ComprehensiveSystem(self.b_weir, self.P_weir, self.b_gate,
                                          self.e, self.P_gate, Z, self.Z_down)
            Q = sys_temp.total_discharge()
            Q_total_range.append(Q['Q_total'])
            Q_weir_range.append(Q['Q_weir'])
            Q_gate_range.append(Q['Q_gate'])
        
        ax3.plot(Z_up_range, Q_total_range, 'b-', linewidth=2, label='总流量')
        ax3.plot(Z_up_range, Q_weir_range, 'g--', linewidth=2, label='堰流')
        ax3.plot(Z_up_range, Q_gate_range, 'r--', linewidth=2, label='闸流')
        ax3.plot(self.Z_up, Q_info['Q_total'], 'ko', markersize=10, label='当前工况')
        
        ax3.set_xlabel('上游水位 Z_up (m)', fontsize=10)
        ax3.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_title('水位-流量关系', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 闸门开度-流量关系
        ax4 = plt.subplot(3, 3, 4)
        
        e_range = np.linspace(0.3, 3, 50)
        Q_e_range = []
        
        for e_val in e_range:
            sys_temp = ComprehensiveSystem(self.b_weir, self.P_weir, self.b_gate,
                                          e_val, self.P_gate, self.Z_up, self.Z_down)
            Q_e_range.append(sys_temp.total_discharge()['Q_total'])
        
        ax4.plot(e_range, Q_e_range, 'b-', linewidth=2)
        ax4.plot(self.e, Q_info['Q_total'], 'ro', markersize=10, label=f'e={self.e}m')
        
        ax4.set_xlabel('闸门开度 e (m)', fontsize=10)
        ax4.set_ylabel('总流量 Q_total (m³/s)', fontsize=10)
        ax4.set_title('开度-流量关系', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 运行工况对比
        ax5 = plt.subplot(3, 3, 5)
        
        scenarios = self.operating_scenarios()
        scenario_names = [s['name'].split('-')[1] for s in scenarios]
        Q_totals = [s['Q']['Q_total'] for s in scenarios]
        
        bars = ax5.bar(scenario_names, Q_totals, color=['skyblue', 'lightgreen', 'lightcoral', 'gold'],
                      alpha=0.7, edgecolor='black')
        ax5.set_ylabel('总流量 (m³/s)', fontsize=10)
        ax5.set_title('运行工况对比', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, Q in zip(bars, Q_totals):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{Q:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 6. 堰闸流量比随水位变化
        ax6 = plt.subplot(3, 3, 6)
        
        ratio_weir = [Q_w / (Q_w + Q_g) if (Q_w+Q_g) > 0 else 0 
                     for Q_w, Q_g in zip(Q_weir_range, Q_gate_range)]
        
        ax6.plot(Z_up_range, ratio_weir, 'b-', linewidth=2, label='堰流占比')
        ax6.plot(Z_up_range, 1 - np.array(ratio_weir), 'r-', linewidth=2, label='闸流占比')
        ax6.plot(self.Z_up, Q_info['ratio_weir'], 'go', markersize=10, label='当前')
        
        ax6.set_xlabel('上游水位 Z_up (m)', fontsize=10)
        ax6.set_ylabel('流量占比', fontsize=10)
        ax6.set_title('流量分配比随水位变化', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        ax6.set_ylim(0, 1)
        
        # 7. 消能设计（水跃）
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        # 闸后水跃计算
        Q_gate = Q_info['Q_gate']
        epsilon = 0.62
        hc = epsilon * self.e
        vc = Q_gate / (self.b_gate * hc)
        Fr_gate = vc / np.sqrt(self.g * hc)
        
        if Fr_gate > 1:
            hc2 = (hc / 2) * (np.sqrt(1 + 8 * Fr_gate**2) - 1)
            Lj = 6 * hc2
            has_jump = True
        else:
            hc2 = hc
            Lj = 0
            has_jump = False
        
        ax7.text(0.5, 0.95, '消能设计', fontsize=11, ha='center', fontweight='bold')
        ax7.text(0.1, 0.80, f'闸后收缩水深: hc = {hc:.3f} m', fontsize=10)
        ax7.text(0.1, 0.70, f'收缩流速: vc = {vc:.3f} m/s', fontsize=10)
        ax7.text(0.1, 0.60, f'Froude数: Fr = {Fr_gate:.3f}', fontsize=10, color='red')
        
        if has_jump:
            ax7.text(0.1, 0.45, f'✓ 发生水跃', fontsize=11, color='green', fontweight='bold')
            ax7.text(0.1, 0.35, f'跃后水深: h₂ = {hc2:.3f} m', fontsize=10)
            ax7.text(0.1, 0.25, f'水跃长度: Lj = {Lj:.2f} m', fontsize=10)
            ax7.text(0.1, 0.10, f'建议消力池长度: {Lj*1.2:.1f} m', fontsize=10, color='blue', fontweight='bold')
        else:
            ax7.text(0.1, 0.45, '✗ 无水跃（Fr<1）', fontsize=11, color='orange', fontweight='bold')
            ax7.text(0.1, 0.30, '无需消力池', fontsize=10)
        
        ax7.set_title('水跃消能', fontsize=12, fontweight='bold')
        
        # 8. 优化调度建议
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '优化调度建议', fontsize=11, ha='center', fontweight='bold')
        
        ax8.text(0.1, 0.80, '1. 泄流优先级:', fontsize=10, color='blue', fontweight='bold')
        ax8.text(0.15, 0.70, '• 高水位：优先开闸（调节灵活）', fontsize=9)
        ax8.text(0.15, 0.62, '• 常水位：堰闸联合（分担流量）', fontsize=9)
        
        ax8.text(0.1, 0.50, '2. 防洪调度:', fontsize=10, color='green', fontweight='bold')
        ax8.text(0.15, 0.40, '• 来流大时全开闸门', fontsize=9)
        ax8.text(0.15, 0.32, f'• 当前余量: {100*(1-Q_info["Q_total"]/150):.1f}%', fontsize=9, color='red')
        
        ax8.text(0.1, 0.20, '3. 经济运行:', fontsize=10, color='orange', fontweight='bold')
        ax8.text(0.15, 0.10, '• 堰流：无动力消耗', fontsize=9)
        ax8.text(0.15, 0.02, '• 闸门：需启闭设备', fontsize=9)
        
        ax8.set_title('运行建议', fontsize=12, fontweight='bold')
        
        # 9. 综合参数表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '堰', '闸'],
            ['宽度(m)', f'{self.b_weir:.1f}', f'{self.b_gate:.1f}'],
            ['高程(m)', f'{self.P_weir:.1f}', f'{self.P_gate:.1f}'],
            ['水头(m)', f'{self.weir_head():.2f}', f'{self.gate_head():.2f}'],
            ['流量(m³/s)', f'{Q_info["Q_weir"]:.2f}', f'{Q_info["Q_gate"]:.2f}'],
            ['占比(%)', f'{Q_info["ratio_weir"]*100:.1f}', f'{Q_info["ratio_gate"]*100:.1f}'],
            ['', '', ''],
            ['总流量', f'{Q_info["Q_total"]:.2f} m³/s', ''],
            ['水跃长度', f'{Lj:.2f} m' if has_jump else '无', '']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.35, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.4)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        table[(7, 1)].set_facecolor('#90EE90')
        table[(7, 1)].set_text_props(weight='bold')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch10_problem13_comprehensive.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch10_problem13_comprehensive.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第10章 堰闸水力计算 - 题13：堰闸综合应用")
        print("="*70)
        
        Q_info = self.total_discharge()
        
        print(f"\n【工程布置】")
        print(f"宽顶堰: b = {self.b_weir} m, P = {self.P_weir} m")
        print(f"闸门: b = {self.b_gate} m, e = {self.e} m, P = {self.P_gate} m")
        print(f"上游水位: Z_up = {self.Z_up} m")
        print(f"下游水位: Z_down = {self.Z_down} m")
        
        print(f"\n【流量计算】")
        print(f"堰上水头: H_weir = {self.weir_head():.2f} m")
        print(f"堰流流量: Q_weir = {Q_info['Q_weir']:.2f} m³/s ({Q_info['ratio_weir']*100:.1f}%)")
        
        print(f"\n闸前水头: H_gate = {self.gate_head():.2f} m")
        print(f"闸流流量: Q_gate = {Q_info['Q_gate']:.2f} m³/s ({Q_info['ratio_gate']*100:.1f}%)")
        
        print(f"\n总流量: Q_total = {Q_info['Q_total']:.2f} m³/s")
        
        print(f"\n【运行工况】")
        scenarios = self.operating_scenarios()
        for s in scenarios:
            print(f"{s['name']}: Q = {s['Q']['Q_total']:.2f} m³/s")
        
        print(f"\n✓ 堰闸综合计算完成")
        print(f"\n{'='*70}\n")


def main():
    b_weir = 10
    P_weir = 3
    b_gate = 8
    e = 1.2
    P_gate = 3
    Z_up = 8
    Z_down = 4
    
    system = ComprehensiveSystem(b_weir, P_weir, b_gate, e, P_gate, Z_up, Z_down)
    system.print_results()
    system.plot_analysis()


if __name__ == "__main__":
    main()
