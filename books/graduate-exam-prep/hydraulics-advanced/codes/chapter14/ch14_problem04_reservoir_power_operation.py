# -*- coding: utf-8 -*-
"""
第14章 压轴大题专项训练 - 题4：水库-电站联合调度

问题描述：
    某水库总库容V = 10亿m³，死库容Vd = 2亿m³
    坝前正常蓄水位Hnorm = 150m，死水位Hdead = 130m
    电站装机容量N = 300MW，台数n = 3台×100MW
    设计水头Hd = 85m，最小工作水头Hmin = 70m
    年平均入流量Q_avg = 120 m³/s
    
    径流过程（月平均流量，m³/s）：
    1月:60, 2月:55, 3月:65, 4月:80, 5月:130,6月:220
    7月:280, 8月:250, 9月:180, 10月:110, 11月:80, 12月:65
    
    电力需求（月，MW·h）：
    1-3月:高峰2.5亿，4-5月:平段2.0亿，6-9月:低谷1.5亿，10-12月:高峰2.3亿
    
    求：
    1. 水库特征水位与库容关系（V-Z曲线）
    2. 电站出力计算与保证出力
    3. 年调节计算（逐月平衡）
    4. 优化调度方案（最大发电量目标）
    5. 弃水量与缺电量分析
    6. 经济效益评估

核心公式：
    1. N = 9.81·η·Q·H/1000 (MW)
    2. E = N·T (MW·h)
    3. V(t+1) = V(t) + (Q_in - Q_out)·Δt
    4. H = Z_上 - Z_下 - h_损

考试要点：
    - 水库调节计算
    - 水电站出力计算
    - 联合优化调度
    - 经济效益分析

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from scipy.optimize import minimize

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ReservoirPowerOperation:
    """水库-电站联合调度"""
    
    def __init__(self, V_total: float, V_dead: float, H_norm: float,
                 H_dead: float, N_installed: float, H_design: float,
                 H_min: float, Q_avg: float):
        self.V_total = V_total  # 总库容 亿m³
        self.V_dead = V_dead  # 死库容 亿m³
        self.H_norm = H_norm  # 正常蓄水位 m
        self.H_dead = H_dead  # 死水位 m
        self.N_installed = N_installed  # 装机容量 MW
        self.H_design = H_design  # 设计水头 m
        self.H_min = H_min  # 最小水头 m
        self.Q_avg = Q_avg  # 年平均入流 m³/s
        
        # 月入流量（m³/s）
        self.Q_inflow = np.array([60, 55, 65, 80, 130, 220,
                                  280, 250, 180, 110, 80, 65])
        
        # 月电力需求（亿kW·h）
        self.E_demand = np.array([2.5, 2.5, 2.5, 2.0, 2.0, 1.5,
                                  1.5, 1.5, 1.5, 2.3, 2.3, 2.3])
        
    def V_Z_relationship(self) -> Dict:
        """库容-水位关系"""
        # 简化为线性关系
        Z_range = np.linspace(self.H_dead, self.H_norm, 50)
        
        # V = V_dead + k·(Z - H_dead)²
        V_benefit = self.V_total - self.V_dead
        k = V_benefit / (self.H_norm - self.H_dead)**2
        
        V_range = self.V_dead + k * (Z_range - self.H_dead)**2
        
        return {
            'Z': Z_range,
            'V': V_range,
            'k': k
        }
    
    def Z_from_V(self, V: float, k: float) -> float:
        """根据库容计算水位"""
        if V <= self.V_dead:
            return self.H_dead
        elif V >= self.V_total:
            return self.H_norm
        else:
            return self.H_dead + np.sqrt((V - self.V_dead) / k)
    
    def power_output(self, Q: float, H: float, eta: float = 0.85) -> float:
        """电站出力计算"""
        # N = 9.81·η·Q·H/1000 (MW)
        N = 9.81 * eta * Q * H / 1000
        
        # 限制在装机容量内
        N = min(N, self.N_installed)
        
        return N
    
    def guaranteed_output(self, Q_series: np.ndarray, H_avg: float,
                         guarantee_rate: float = 0.95) -> float:
        """保证出力"""
        # 按流量排序
        Q_sorted = np.sort(Q_series)
        
        # 保证率对应的流量
        idx = int(len(Q_sorted) * (1 - guarantee_rate))
        Q_guarantee = Q_sorted[idx]
        
        # 保证出力
        N_guarantee = self.power_output(Q_guarantee, H_avg)
        
        return N_guarantee
    
    def monthly_regulation(self, k: float) -> Dict:
        """逐月调节计算"""
        months = 12
        V = np.zeros(months + 1)
        Z = np.zeros(months + 1)
        Q_out = np.zeros(months)
        N_out = np.zeros(months)
        E_gen = np.zeros(months)
        H_net = np.zeros(months)
        
        # 初始库容（汛前蓄满）
        V[0] = self.V_total * 0.9
        Z[0] = self.Z_from_V(V[0], k)
        
        # 尾水位（简化）
        Z_tail = 50.0  # m
        
        # 逐月计算
        days_in_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        
        for i in range(months):
            # 月入流量（亿m³）
            W_in = self.Q_inflow[i] * days_in_month[i] * 86400 / 1e8
            
            # 平均水位
            Z_avg = Z[i]
            H_net[i] = Z_avg - Z_tail - 2.0  # 减去损失
            
            # 根据电力需求确定发电流量
            E_demand_month = self.E_demand[i]  # 亿kW·h
            hours_in_month = days_in_month[i] * 24
            
            # 所需平均出力
            N_required = E_demand_month * 1e8 / (hours_in_month * 1e3)  # MW
            
            # 根据出力反推流量
            if H_net[i] > self.H_min:
                Q_required = N_required * 1000 / (9.81 * 0.85 * H_net[i])
            else:
                Q_required = 0
            
            # 限制在入流量和库容范围内
            Q_out[i] = min(Q_required, self.Q_inflow[i] * 1.2)
            Q_out[i] = max(Q_out[i], self.Q_inflow[i] * 0.5)
            
            # 实际出力和发电量
            N_out[i] = self.power_output(Q_out[i], H_net[i])
            E_gen[i] = N_out[i] * hours_in_month / 1e8  # 亿kW·h
            
            # 月末库容
            W_out = Q_out[i] * days_in_month[i] * 86400 / 1e8
            V[i+1] = V[i] + W_in - W_out
            
            # 库容约束
            V[i+1] = max(self.V_dead, min(self.V_total, V[i+1]))
            
            # 月末水位
            Z[i+1] = self.Z_from_V(V[i+1], k)
        
        # 弃水和缺电
        spill = np.maximum(0, V[1:] - self.V_total) * 1e8  # m³
        shortage = np.maximum(0, self.E_demand - E_gen)
        
        return {
            'V': V,
            'Z': Z,
            'Q_out': Q_out,
            'N_out': N_out,
            'E_gen': E_gen,
            'H_net': H_net,
            'spill': spill,
            'shortage': shortage
        }
    
    def optimal_operation(self, k: float) -> Dict:
        """优化调度方案"""
        # 目标：最大化年发电量
        # 约束：库容、出力、水头
        
        # 简化优化：使用贪心策略
        # 丰水期多蓄水，枯水期多发电
        
        months = 12
        V_opt = np.zeros(months + 1)
        Q_opt = np.zeros(months)
        
        V_opt[0] = self.V_total * 0.85
        
        days_in_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        
        # 判断丰枯
        Q_median = np.median(self.Q_inflow)
        
        for i in range(months):
            W_in = self.Q_inflow[i] * days_in_month[i] * 86400 / 1e8
            
            if self.Q_inflow[i] > Q_median * 1.2:
                # 丰水期：适当蓄水
                Q_opt[i] = self.Q_inflow[i] * 0.7
            elif self.Q_inflow[i] < Q_median * 0.8:
                # 枯水期：多发电
                Q_opt[i] = self.Q_inflow[i] * 1.3
            else:
                # 平水期：平衡
                Q_opt[i] = self.Q_inflow[i]
            
            W_out = Q_opt[i] * days_in_month[i] * 86400 / 1e8
            V_opt[i+1] = V_opt[i] + W_in - W_out
            V_opt[i+1] = max(self.V_dead, min(self.V_total, V_opt[i+1]))
        
        return {
            'V_opt': V_opt,
            'Q_opt': Q_opt
        }
    
    def economic_analysis(self, regulation: Dict) -> Dict:
        """经济效益分析"""
        # 年发电量
        E_annual = np.sum(regulation['E_gen'])  # 亿kW·h
        
        # 电价（元/kW·h）
        price_peak = 0.8
        price_normal = 0.5
        price_valley = 0.3
        
        # 各月电价（简化）
        prices = np.array([price_peak] * 3 + [price_normal] * 2 + 
                         [price_valley] * 4 + [price_peak] * 3)
        
        # 发电收入
        revenue = np.sum(regulation['E_gen'] * 1e8 * prices) / 1e8  # 亿元
        
        # 运行成本（发电量的5%）
        cost = revenue * 0.05
        
        # 净收益
        net_benefit = revenue - cost
        
        # 缺电损失（按最高电价计算）
        shortage_loss = np.sum(regulation['shortage']) * 1e8 * price_peak / 1e8
        
        # 综合效益
        total_benefit = net_benefit - shortage_loss
        
        # 装机利用小时数
        utilization_hours = E_annual * 1e8 / (self.N_installed * 1e3)
        
        return {
            'E_annual': E_annual,
            'revenue': revenue,
            'cost': cost,
            'net_benefit': net_benefit,
            'shortage_loss': shortage_loss,
            'total_benefit': total_benefit,
            'utilization_hours': utilization_hours
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        VZ = self.V_Z_relationship()
        regulation = self.monthly_regulation(VZ['k'])
        optimal = self.optimal_operation(VZ['k'])
        economic = self.economic_analysis(regulation)
        
        months = np.arange(1, 13)
        days_in_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        
        # 1. 库容-水位关系曲线
        ax1 = plt.subplot(3, 3, 1)
        
        ax1.plot(VZ['V'], VZ['Z'], 'b-', linewidth=2, label='V-Z曲线')
        ax1.axhline(self.H_norm, color='r', linestyle='--', linewidth=1, label='正常蓄水位')
        ax1.axhline(self.H_dead, color='orange', linestyle='--', linewidth=1, label='死水位')
        ax1.axvline(self.V_dead, color='orange', linestyle='--', linewidth=1, alpha=0.5)
        ax1.axvline(self.V_total, color='r', linestyle='--', linewidth=1, alpha=0.5)
        
        ax1.fill_between(VZ['V'], self.H_dead, VZ['Z'], alpha=0.2, color='blue')
        
        ax1.set_xlabel('库容 V (亿m³)', fontsize=10)
        ax1.set_ylabel('水位 Z (m)', fontsize=10)
        ax1.set_title('库容-水位关系', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '水库与电站参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'总库容: {self.V_total} 亿m³', fontsize=10)
        ax2.text(0.1, 0.74, f'兴利库容: {self.V_total-self.V_dead} 亿m³', fontsize=10)
        ax2.text(0.1, 0.66, f'正常蓄水位: {self.H_norm} m', fontsize=10)
        ax2.text(0.1, 0.58, f'死水位: {self.H_dead} m', fontsize=10)
        
        ax2.text(0.1, 0.45, f'装机容量: {self.N_installed} MW', fontsize=10, color='blue')
        ax2.text(0.1, 0.37, f'设计水头: {self.H_design} m', fontsize=10)
        ax2.text(0.1, 0.29, f'最小水头: {self.H_min} m', fontsize=10)
        
        ax2.text(0.1, 0.16, f'年均入流: {self.Q_avg} m³/s', fontsize=10)
        ax2.text(0.1, 0.08, f'年发电量: {economic["E_annual"]:.2f} 亿kW·h', 
                fontsize=10, color='green', fontweight='bold')
        
        ax2.set_title('参数汇总', fontsize=12, fontweight='bold')
        
        # 3. 月入流过程
        ax3 = plt.subplot(3, 3, 3)
        
        ax3.plot(months, self.Q_inflow, 'b-o', linewidth=2, markersize=6)
        ax3.axhline(self.Q_avg, color='r', linestyle='--', linewidth=1, 
                   label=f'年均{self.Q_avg}m³/s')
        ax3.fill_between(months, 0, self.Q_inflow, alpha=0.3, color='lightblue')
        
        ax3.set_xlabel('月份', fontsize=10)
        ax3.set_ylabel('入流量 (m³/s)', fontsize=10)
        ax3.set_title('月入流过程', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xticks(months)
        
        # 4. 库容调节过程
        ax4 = plt.subplot(3, 3, 4)
        
        months_extended = np.arange(0, 13)
        ax4.plot(months_extended, regulation['V'], 'b-o', linewidth=2, label='实际运行')
        ax4.plot(months_extended, optimal['V_opt'], 'g--s', linewidth=2, label='优化方案')
        ax4.axhline(self.V_total, color='r', linestyle='--', linewidth=1, alpha=0.5)
        ax4.axhline(self.V_dead, color='orange', linestyle='--', linewidth=1, alpha=0.5)
        
        ax4.fill_between(months_extended, self.V_dead, regulation['V'], 
                        alpha=0.2, color='blue')
        
        ax4.set_xlabel('月份', fontsize=10)
        ax4.set_ylabel('库容 (亿m³)', fontsize=10)
        ax4.set_title('库容调节过程', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xticks(months_extended)
        
        # 5. 水位变化过程
        ax5 = plt.subplot(3, 3, 5)
        
        ax5.plot(months_extended, regulation['Z'], 'b-o', linewidth=2)
        ax5.axhline(self.H_norm, color='r', linestyle='--', linewidth=1, 
                   label='正常蓄水位')
        ax5.axhline(self.H_dead, color='orange', linestyle='--', linewidth=1,
                   label='死水位')
        ax5.fill_between(months_extended, self.H_dead, regulation['Z'],
                        alpha=0.2, color='lightblue')
        
        ax5.set_xlabel('月份', fontsize=10)
        ax5.set_ylabel('水位 (m)', fontsize=10)
        ax5.set_title('水位变化过程', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_xticks(months_extended)
        
        # 6. 发电出力过程
        ax6 = plt.subplot(3, 3, 6)
        
        ax6.plot(months, regulation['N_out'], 'g-o', linewidth=2, markersize=6)
        ax6.axhline(self.N_installed, color='r', linestyle='--', linewidth=1,
                   label=f'装机{self.N_installed}MW')
        ax6.fill_between(months, 0, regulation['N_out'], alpha=0.3, color='lightgreen')
        
        ax6.set_xlabel('月份', fontsize=10)
        ax6.set_ylabel('出力 (MW)', fontsize=10)
        ax6.set_title('发电出力过程', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        ax6.set_xticks(months)
        
        # 7. 发电量与需求对比
        ax7 = plt.subplot(3, 3, 7)
        
        x = np.arange(len(months))
        width = 0.35
        
        bars1 = ax7.bar(x - width/2, self.E_demand, width, label='需求',
                       color='red', alpha=0.7, edgecolor='black')
        bars2 = ax7.bar(x + width/2, regulation['E_gen'], width, label='发电',
                       color='green', alpha=0.7, edgecolor='black')
        
        ax7.set_xlabel('月份', fontsize=10)
        ax7.set_ylabel('电量 (亿kW·h)', fontsize=10)
        ax7.set_title('发电量与需求对比', fontsize=12, fontweight='bold')
        ax7.set_xticks(x)
        ax7.set_xticklabels(months)
        ax7.legend()
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 8. 经济效益分析
        ax8 = plt.subplot(3, 3, 8)
        
        benefit_items = ['发电收入', '运行成本', '缺电损失', '净效益']
        benefit_values = [economic['revenue'], -economic['cost'],
                         -economic['shortage_loss'], economic['total_benefit']]
        colors_benefit = ['green', 'red', 'orange', 'blue']
        
        bars = ax8.barh(benefit_items, benefit_values, color=colors_benefit,
                       alpha=0.7, edgecolor='black')
        ax8.axvline(0, color='k', linewidth=1)
        
        for bar, val in zip(bars, benefit_values):
            width = bar.get_width()
            ax8.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.2f}', ha='left' if width>0 else 'right',
                    va='center', fontsize=9, fontweight='bold')
        
        ax8.set_xlabel('金额 (亿元)', fontsize=10)
        ax8.set_title('经济效益分析', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        # 9. 综合评价表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['年发电量', f'{economic["E_annual"]:.2f}', '亿kW·h'],
            ['装机利用', f'{economic["utilization_hours"]:.0f}', '小时'],
            ['发电收入', f'{economic["revenue"]:.2f}', '亿元'],
            ['运行成本', f'{economic["cost"]:.2f}', '亿元'],
            ['缺电损失', f'{economic["shortage_loss"]:.2f}', '亿元'],
            ['净效益', f'{economic["total_benefit"]:.2f}', '亿元'],
            ['年均流量', f'{self.Q_avg}', 'm³/s'],
            ['年均水头', f'{np.mean(regulation["H_net"]):.1f}', 'm']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.40, 0.30, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2.0)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [1, 4, 6]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('综合评价汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch14_problem04_reservoir_power_operation.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch14_problem04_reservoir_power_operation.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第14章 压轴大题 - 题4：水库-电站联合调度")
        print("="*70)
        
        VZ = self.V_Z_relationship()
        regulation = self.monthly_regulation(VZ['k'])
        economic = self.economic_analysis(regulation)
        N_guarantee = self.guaranteed_output(self.Q_inflow, self.H_design)
        
        print(f"\n【1. 水库特征参数】")
        print(f"总库容: V = {self.V_total} 亿m³")
        print(f"死库容: Vd = {self.V_dead} 亿m³")
        print(f"兴利库容: Vb = {self.V_total - self.V_dead} 亿m³")
        print(f"正常蓄水位: {self.H_norm} m")
        print(f"死水位: {self.H_dead} m")
        
        print(f"\n【2. 电站出力】")
        print(f"装机容量: N = {self.N_installed} MW")
        print(f"设计水头: Hd = {self.H_design} m")
        print(f"保证出力: Ng = {N_guarantee:.2f} MW")
        print(f"装机利用小时数: {economic['utilization_hours']:.0f} 小时/年")
        
        print(f"\n【3. 年调节计算】")
        print(f"{'月份':<6} {'入流':<10} {'出流':<10} {'库容':<10} {'水位':<10} {'出力':<10} {'发电量':<10}")
        print(f"{'':6} {'(m³/s)':<10} {'(m³/s)':<10} {'(亿m³)':<10} {'(m)':<10} {'(MW)':<10} {'(亿kW·h)':<10}")
        print("-" * 70)
        
        for i in range(12):
            print(f"{i+1:<6} {self.Q_inflow[i]:<10.1f} {regulation['Q_out'][i]:<10.1f} "
                  f"{regulation['V'][i]:<10.2f} {regulation['Z'][i]:<10.1f} "
                  f"{regulation['N_out'][i]:<10.1f} {regulation['E_gen'][i]:<10.2f}")
        
        print(f"\n【4. 弃水与缺电】")
        total_spill = np.sum(regulation['spill']) / 1e8
        total_shortage = np.sum(regulation['shortage'])
        print(f"年弃水量: {total_spill:.2f} 亿m³")
        print(f"年缺电量: {total_shortage:.2f} 亿kW·h")
        
        if total_spill < 1.0 and total_shortage < 0.5:
            print(f"✓ 调节性能良好")
        else:
            print(f"△ 需优化调度方案")
        
        print(f"\n【5. 经济效益】")
        print(f"年发电量: {economic['E_annual']:.2f} 亿kW·h")
        print(f"发电收入: {economic['revenue']:.2f} 亿元")
        print(f"运行成本: {economic['cost']:.2f} 亿元")
        print(f"缺电损失: {economic['shortage_loss']:.2f} 亿元")
        print(f"综合效益: {economic['total_benefit']:.2f} 亿元")
        
        print(f"\n✓ 水库-电站联合调度完成")
        print(f"\n{'='*70}\n")


def main():
    V_total = 10.0  # 亿m³
    V_dead = 2.0
    H_norm = 150  # m
    H_dead = 130
    N_installed = 300  # MW
    H_design = 85  # m
    H_min = 70
    Q_avg = 120  # m³/s
    
    operation = ReservoirPowerOperation(V_total, V_dead, H_norm, H_dead,
                                        N_installed, H_design, H_min, Q_avg)
    operation.print_results()
    operation.plot_analysis()


if __name__ == "__main__":
    main()
