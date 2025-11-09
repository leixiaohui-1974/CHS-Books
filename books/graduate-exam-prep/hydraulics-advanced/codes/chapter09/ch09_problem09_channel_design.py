# -*- coding: utf-8 -*-
"""
第09章 渠系水力计算 - 题9：渠道综合设计

问题描述：
    设计一条灌溉渠道，要求：
    - 设计流量Q = 15 m³/s
    - 底坡i = 0.0008
    - 允许流速范围：0.6 ~ 2.5 m/s（防冲防淤）
    - 边坡系数m = 2.0（土质渠道）
    - 糙率n = 0.025
    
    求：
    1. 水力最优断面设计
    2. 多方案比较（不同b/h比）
    3. 防冲防淤验证
    4. 土方量与造价估算
    5. 最优方案推荐

核心公式：
    1. Manning: Q = A·(1/n)R^(2/3)i^(1/2)
    2. 最优条件: b = 2h(√(1+m²)-m)
    3. 不冲流速: v_max = 2.5 m/s（土渠）
    4. 不淤流速: v_min = 0.6 m/s

考试要点：
    - 渠道断面设计方法
    - 防冲防淤要求
    - 多方案比选
    - 工程经济分析

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ChannelDesign:
    """渠道综合设计"""
    
    def __init__(self, Q: float, i: float, n: float, m: float = 2.0,
                 v_min: float = 0.6, v_max: float = 2.5):
        self.Q = Q
        self.i = i
        self.n = n
        self.m = m
        self.v_min = v_min
        self.v_max = v_max
        self.g = 9.8
        
    def trapezoid_area(self, b: float, h: float) -> float:
        """梯形断面面积"""
        return (b + self.m * h) * h
    
    def wetted_perimeter(self, b: float, h: float) -> float:
        """湿周"""
        return b + 2 * h * np.sqrt(1 + self.m**2)
    
    def hydraulic_radius(self, b: float, h: float) -> float:
        """水力半径"""
        A = self.trapezoid_area(b, h)
        chi = self.wetted_perimeter(b, h)
        return A / chi
    
    def velocity(self, b: float, h: float) -> float:
        """流速"""
        R = self.hydraulic_radius(b, h)
        return (1 / self.n) * (R ** (2/3)) * (self.i ** 0.5)
    
    def discharge(self, b: float, h: float) -> float:
        """流量"""
        A = self.trapezoid_area(b, h)
        v = self.velocity(b, h)
        return A * v
    
    def optimal_section(self) -> Tuple[float, float]:
        """水力最优断面"""
        def equation(h):
            b = 2 * h * (np.sqrt(1 + self.m**2) - self.m)
            return self.discharge(b, h) - self.Q
        
        h_opt = fsolve(equation, 1.5)[0]
        b_opt = 2 * h_opt * (np.sqrt(1 + self.m**2) - self.m)
        return b_opt, h_opt
    
    def design_schemes(self) -> List[Dict]:
        """多方案设计"""
        schemes = []
        
        # 方案1：水力最优
        b_opt, h_opt = self.optimal_section()
        v_opt = self.velocity(b_opt, h_opt)
        schemes.append({
            'name': '方案1-水力最优',
            'b': b_opt,
            'h': h_opt,
            'v': v_opt,
            'type': 'optimal'
        })
        
        # 方案2-4：不同b/h比
        for ratio in [1.5, 2.0, 2.5]:
            def eq(h):
                b = ratio * h
                return self.discharge(b, h) - self.Q
            
            h = fsolve(eq, 1.5)[0]
            b = ratio * h
            v = self.velocity(b, h)
            
            schemes.append({
                'name': f'方案{len(schemes)+1}-b/h={ratio}',
                'b': b,
                'h': h,
                'v': v,
                'type': f'ratio_{ratio}'
            })
        
        return schemes
    
    def excavation_volume(self, b: float, h: float, L: float = 1000) -> float:
        """土方量（单位长度）"""
        H_dig = h + 0.5  # 加保护层
        # 梯形台体积
        V = ((b + (b + 2 * self.m * H_dig)) / 2) * H_dig * L
        return V / L  # 返回单位长度
    
    def cost_estimate(self, b: float, h: float, L: float = 1000) -> Dict:
        """造价估算"""
        V_earth = self.excavation_volume(b, h, L)
        
        # 单价（元/m³）
        price_excavation = 15  # 土方开挖
        price_lining = 80  # 衬砌（可选）
        
        # 开挖费用
        cost_excavation = V_earth * L * price_excavation
        
        # 衬砌费用（假设衬砌厚0.1m）
        A_lining = self.wetted_perimeter(b, h) * L
        cost_lining = A_lining * 0.1 * price_lining
        
        total = cost_excavation + cost_lining
        
        return {
            'excavation': cost_excavation,
            'lining': cost_lining,
            'total': total,
            'unit': total / L
        }
    
    def check_velocity(self, v: float) -> Tuple[bool, str]:
        """流速检查"""
        if v < self.v_min:
            return False, f"流速过小({v:.3f}<{self.v_min})，易淤积"
        elif v > self.v_max:
            return False, f"流速过大({v:.3f}>{self.v_max})，易冲刷"
        else:
            return True, f"流速合格({v:.3f} m/s)"
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        schemes = self.design_schemes()
        
        # 1. 方案1断面图
        ax1 = plt.subplot(3, 3, 1)
        
        s1 = schemes[0]
        b, h = s1['b'], s1['h']
        
        x_trap = np.array([0, b, b+self.m*h, -self.m*h, 0])
        y_trap = np.array([0, 0, h, h, 0])
        
        ax1.fill(x_trap, y_trap, color='lightblue', alpha=0.5, label='水体')
        ax1.plot(x_trap, y_trap, 'k-', linewidth=2)
        
        ax1.text(b/2, -0.3, f'b={b:.2f}m', ha='center', fontsize=10, color='red', fontweight='bold')
        ax1.text(b+0.5, h/2, f'h={h:.2f}m', fontsize=10, color='red', fontweight='bold')
        ax1.text(-0.5, h/2, f'm={self.m}', fontsize=10, color='blue')
        
        ax1.set_aspect('equal')
        ax1.set_title(f'{s1["name"]}断面', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 设计参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.9, '设计条件', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.75, f'流量: Q = {self.Q} m³/s', fontsize=10)
        ax2.text(0.1, 0.65, f'底坡: i = {self.i}', fontsize=10)
        ax2.text(0.1, 0.55, f'糙率: n = {self.n}', fontsize=10)
        ax2.text(0.1, 0.45, f'边坡: m = {self.m}', fontsize=10)
        ax2.text(0.1, 0.30, f'允许流速: {self.v_min}~{self.v_max} m/s', fontsize=10, color='red')
        ax2.text(0.1, 0.20, f'不冲：v < {self.v_max} m/s', fontsize=9, color='orange')
        ax2.text(0.1, 0.10, f'不淤：v > {self.v_min} m/s', fontsize=9, color='blue')
        
        ax2.set_title('设计要求', fontsize=12, fontweight='bold')
        
        # 3. 方案对比（b-h）
        ax3 = plt.subplot(3, 3, 3)
        
        for i, s in enumerate(schemes):
            ax3.scatter(s['b'], s['h'], s=200, label=f"{s['name']}", marker='o')
        
        ax3.set_xlabel('底宽 b (m)', fontsize=10)
        ax3.set_ylabel('水深 h (m)', fontsize=10)
        ax3.set_title('方案断面尺寸对比', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 4. 流速对比
        ax4 = plt.subplot(3, 3, 4)
        
        names = [s['name'].split('-')[0] for s in schemes]
        velocities = [s['v'] for s in schemes]
        colors = []
        
        for v in velocities:
            if v < self.v_min:
                colors.append('blue')
            elif v > self.v_max:
                colors.append('red')
            else:
                colors.append('green')
        
        bars = ax4.bar(names, velocities, color=colors, alpha=0.7, edgecolor='black')
        ax4.axhline(self.v_min, color='blue', linestyle='--', linewidth=1.5, label=f'v_min={self.v_min}')
        ax4.axhline(self.v_max, color='red', linestyle='--', linewidth=1.5, label=f'v_max={self.v_max}')
        
        ax4.set_ylabel('流速 v (m/s)', fontsize=10)
        ax4.set_title('流速对比（防冲防淤）', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for bar, v in zip(bars, velocities):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{v:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 5. 断面参数对比
        ax5 = plt.subplot(3, 3, 5)
        
        params = ['面积\n(m²)', '湿周\n(m)', '水力半径\n(m)']
        x_pos = np.arange(len(params))
        width = 0.2
        
        for i, s in enumerate(schemes):
            A = self.trapezoid_area(s['b'], s['h'])
            chi = self.wetted_perimeter(s['b'], s['h'])
            R = self.hydraulic_radius(s['b'], s['h'])
            values = [A, chi, R]
            
            ax5.bar(x_pos + i*width, values, width, label=f"方案{i+1}", alpha=0.7)
        
        ax5.set_xticks(x_pos + width*1.5)
        ax5.set_xticklabels(params, fontsize=9)
        ax5.set_title('断面参数对比', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. 土方量对比
        ax6 = plt.subplot(3, 3, 6)
        
        earth_vols = [self.excavation_volume(s['b'], s['h']) for s in schemes]
        
        bars = ax6.bar(names, earth_vols, color='brown', alpha=0.6, edgecolor='black')
        ax6.set_ylabel('单位土方量 (m³/m)', fontsize=10)
        ax6.set_title('土方量对比', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, vol in zip(bars, earth_vols):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{vol:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 7. 造价对比
        ax7 = plt.subplot(3, 3, 7)
        
        costs = [self.cost_estimate(s['b'], s['h'])['unit'] for s in schemes]
        
        bars = ax7.bar(names, costs, color='gold', alpha=0.7, edgecolor='black')
        ax7.set_ylabel('单位造价 (元/m)', fontsize=10)
        ax7.set_title('工程造价对比', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='y')
        
        for bar, cost in zip(bars, costs):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height,
                    f'{cost:.0f}', ha='center', va='bottom', fontsize=9)
        
        # 8. 综合评价雷达图
        ax8 = plt.subplot(3, 3, 8, projection='polar')
        
        # 评价指标：流速合理性、水力效率、土方量、造价（归一化）
        categories = ['流速\n合理性', '水力\n效率', '土方\n经济', '造价\n经济']
        N = len(categories)
        
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        # 计算方案1的指标
        s = schemes[0]
        v_score = 1 - abs(s['v'] - (self.v_min+self.v_max)/2) / ((self.v_max-self.v_min)/2)
        R = self.hydraulic_radius(s['b'], s['h'])
        R_score = R / 2  # 假设理想R=2m
        earth_score = 1 - (earth_vols[0] - min(earth_vols)) / (max(earth_vols) - min(earth_vols) + 0.01)
        cost_score = 1 - (costs[0] - min(costs)) / (max(costs) - min(costs) + 0.01)
        
        values = [v_score, R_score, earth_score, cost_score]
        values += values[:1]
        
        ax8.plot(angles, values, 'o-', linewidth=2, label='方案1', color='blue')
        ax8.fill(angles, values, alpha=0.25, color='blue')
        ax8.set_xticks(angles[:-1])
        ax8.set_xticklabels(categories, fontsize=9)
        ax8.set_ylim(0, 1)
        ax8.set_title('综合评价（方案1）', fontsize=12, fontweight='bold', pad=20)
        ax8.legend(loc='upper right')
        ax8.grid(True)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [['方案', 'b(m)', 'h(m)', 'v(m/s)', '检查']]
        
        for i, s in enumerate(schemes):
            check_ok, check_msg = self.check_velocity(s['v'])
            status = '✓' if check_ok else '✗'
            table_data.append([
                s['name'].split('-')[0],
                f"{s['b']:.2f}",
                f"{s['h']:.2f}",
                f"{s['v']:.2f}",
                status
            ])
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.25, 0.18, 0.18, 0.18, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        # 设置表头样式
        for i in range(5):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮推荐方案
        table[(1, 0)].set_facecolor('#90EE90')
        
        ax9.set_title('方案汇总（推荐方案1）', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch09_problem09_channel_design.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch09_problem09_channel_design.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第09章 渠系水力计算 - 题9：渠道综合设计")
        print("="*70)
        
        print(f"\n【设计条件】")
        print(f"流量: Q = {self.Q} m³/s")
        print(f"底坡: i = {self.i}")
        print(f"糙率: n = {self.n}")
        print(f"边坡: m = {self.m}")
        print(f"允许流速: {self.v_min} ~ {self.v_max} m/s")
        
        schemes = self.design_schemes()
        
        print(f"\n【设计方案】")
        for i, s in enumerate(schemes, 1):
            print(f"\n{s['name']}:")
            print(f"  底宽: b = {s['b']:.3f} m")
            print(f"  水深: h = {s['h']:.3f} m")
            print(f"  流速: v = {s['v']:.3f} m/s")
            
            check_ok, check_msg = self.check_velocity(s['v'])
            print(f"  检查: {check_msg} {'✓' if check_ok else '✗'}")
            
            cost = self.cost_estimate(s['b'], s['h'])
            earth = self.excavation_volume(s['b'], s['h'])
            print(f"  土方: {earth:.2f} m³/m")
            print(f"  造价: {cost['unit']:.0f} 元/m")
        
        print(f"\n【推荐方案】")
        print(f"✓ 方案1（水力最优）：综合性能最佳")
        
        print(f"\n✓ 渠道设计完成")
        print(f"\n{'='*70}\n")


def main():
    Q = 15
    i = 0.0008
    n = 0.025
    m = 2.0
    
    design = ChannelDesign(Q, i, n, m)
    design.print_results()
    design.plot_analysis()


if __name__ == "__main__":
    main()
