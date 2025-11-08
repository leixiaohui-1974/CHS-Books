# -*- coding: utf-8 -*-
"""
第11章 水工建筑物 - 题4：溢洪道水力设计

问题描述：
    某水库需设计溢洪道，设计流量Q = 2000 m³/s
    堰顶高程P = 80m，上游水位H = 85m
    溢流堰采用WES型实用堰，堰顶宽b = 50m
    下游消能采用挑流方式
    
    求：
    1. 堰顶水头与流量关系
    2. 溢流堰流量系数
    3. 溢流面曲线方程
    4. 挑流鼻坎设计
    5. 下游冲刷坑深度

核心公式：
    1. 溢流堰流量：Q = m·b·H^(3/2)·√(2g)
    2. WES堰流量系数：m = 0.502
    3. 溢流面曲线：y = -0.5·(x/H)^1.85·H
    4. 挑流射程：L = v₀²·sin(2θ)/g
    5. 冲刷坑深度：t = q^0.5·H_0^0.25

考试要点：
    - 溢流堰设计
    - WES堰剖面
    - 挑流消能
    - 冲刷计算

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SpillwayDesign:
    """溢洪道水力设计"""
    
    def __init__(self, Q: float, P: float, H_up: float, b: float, 
                 m: float = 0.502, theta: float = 30):
        self.Q = Q  # 设计流量
        self.P = P  # 堰顶高程
        self.H_up = H_up  # 上游水位
        self.b = b  # 堰顶宽度
        self.m = m  # 流量系数
        self.theta = theta  # 挑角
        self.g = 9.8
        
    def head(self) -> float:
        """堰顶水头"""
        return self.H_up - self.P
    
    def discharge(self, H: float = None) -> float:
        """
        溢流堰流量
        Q = m·b·H^(3/2)·√(2g)
        """
        if H is None:
            H = self.head()
        
        Q = self.m * self.b * (H ** 1.5) * np.sqrt(2 * self.g)
        return Q
    
    def flow_coefficient(self, Q_actual: float = None) -> float:
        """
        反算流量系数
        m = Q / [b·H^(3/2)·√(2g)]
        """
        if Q_actual is None:
            Q_actual = self.Q
        
        H = self.head()
        m_calc = Q_actual / (self.b * (H ** 1.5) * np.sqrt(2 * self.g))
        return m_calc
    
    def unit_discharge(self) -> float:
        """单宽流量"""
        return self.Q / self.b
    
    def spillway_profile(self, n_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        WES溢流面曲线
        y = -0.5·(x/Hd)^1.85·Hd
        Hd为设计水头
        """
        Hd = self.head()
        
        # x坐标（从堰顶向下游）
        x = np.linspace(0, 3*Hd, n_points)
        
        # y坐标（堰顶为0，向下为负）
        y = -0.5 * ((x / Hd) ** 1.85) * Hd
        
        return x, y
    
    def crest_velocity(self) -> float:
        """堰顶流速"""
        H = self.head()
        # v = √(2g·H)
        v = np.sqrt(2 * self.g * H)
        return v
    
    def flip_bucket_design(self) -> Dict:
        """
        挑流鼻坎设计
        假设鼻坎高程Zb，鼻坎处水深hb
        """
        q = self.unit_discharge()
        H = self.head()
        
        # 鼻坎处水深（估算）
        hb = (q ** 2 / self.g) ** (1/3)
        
        # 鼻坎处流速
        vb = q / hb
        
        # 挑距（水平射程）
        theta_rad = np.deg2rad(self.theta)
        
        # 假设鼻坎高程与下游河床高差ΔZ
        delta_Z = H + self.P - 60  # 假设下游河床高程60m
        
        # 考虑高差的挑距
        # L = (v²·sin(2θ))/(2g) + v·cos(θ)·√[v²·sin²(θ)/(2g²) + 2ΔZ/g]
        term1 = (vb ** 2 * np.sin(2 * theta_rad)) / (2 * self.g)
        term2 = vb * np.cos(theta_rad) * np.sqrt(
            (vb ** 2 * np.sin(theta_rad) ** 2) / (2 * self.g ** 2) + 
            2 * delta_Z / self.g
        )
        L = term1 + term2
        
        # 冲击动能
        E_impact = 0.5 * (q * vb) * (vb ** 2)
        
        return {
            'hb': hb,
            'vb': vb,
            'L': L,
            'delta_Z': delta_Z,
            'E_impact': E_impact
        }
    
    def scour_depth(self) -> float:
        """
        冲刷坑深度（经验公式）
        t = K·q^0.5·H_0^0.25
        K取1.9（岩基）
        """
        q = self.unit_discharge()
        H0 = self.head() + self.P  # 总水头
        
        K = 1.9  # 经验系数（岩基）
        t = K * (q ** 0.5) * (H0 ** 0.25)
        
        return t
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        H = self.head()
        Q_design = self.discharge()
        q = self.unit_discharge()
        v_crest = self.crest_velocity()
        bucket = self.flip_bucket_design()
        t_scour = self.scour_depth()
        
        # 1. 溢洪道纵剖面
        ax1 = plt.subplot(3, 3, 1)
        
        # 溢流面曲线
        x_profile, y_profile = self.spillway_profile()
        
        # 坐标转换（以堰顶为原点）
        ax1.plot(x_profile, y_profile, 'b-', linewidth=3, label='WES溢流面')
        
        # 堰体
        ax1.plot([0, 0], [0, -self.P/2], 'k-', linewidth=4)
        ax1.fill([-5, -5, 0, 0], [-self.P/2, 0, 0, -self.P/2], 
                color='gray', alpha=0.4, label='堰体')
        
        # 上游水位
        ax1.axhline(H, color='lightblue', linewidth=3, alpha=0.7, label=f'上游水位 H={H}m')
        ax1.fill_between([-10, 0], 0, H, color='lightblue', alpha=0.3)
        
        # 挑流轨迹
        theta_rad = np.deg2rad(self.theta)
        x_flip = x_profile[-1]
        y_flip = y_profile[-1]
        
        # 从鼻坎点开始的抛物线
        t_flight = np.linspace(0, 5, 100)
        x_traj = x_flip + bucket['vb'] * np.cos(theta_rad) * t_flight
        y_traj = y_flip + bucket['vb'] * np.sin(theta_rad) * t_flight - 0.5 * self.g * (t_flight ** 2)
        
        # 只绘制y>下游河床的部分
        y_bed = -bucket['delta_Z']
        mask = y_traj > y_bed
        ax1.plot(x_traj[mask], y_traj[mask], 'r--', linewidth=2, label='挑流轨迹')
        
        # 下游河床
        ax1.axhline(y_bed, color='brown', linewidth=2, linestyle='-', label='下游河床')
        ax1.fill_between([x_profile[-1], x_traj[-1]], y_bed, y_bed-t_scour, 
                        color='orange', alpha=0.3, label='冲刷坑')
        
        # 标注
        ax1.text(0, H+1, f'H={H:.1f}m', ha='center', fontsize=9, color='blue', fontweight='bold')
        ax1.text(x_flip, y_flip-2, f'θ={self.theta}°', ha='center', fontsize=9, color='red', fontweight='bold')
        
        ax1.set_xlabel('水平距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('溢洪道纵剖面', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-10, x_traj[mask][-1]+5)
        
        # 2. 设计参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '设计参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'设计流量: Q = {self.Q:.0f} m³/s', fontsize=10, color='blue')
        ax2.text(0.1, 0.72, f'堰顶宽度: b = {self.b:.0f} m', fontsize=10)
        ax2.text(0.1, 0.62, f'堰顶高程: P = {self.P:.0f} m', fontsize=10)
        ax2.text(0.1, 0.52, f'上游水位: {self.H_up:.0f} m', fontsize=10)
        ax2.text(0.1, 0.42, f'堰顶水头: H = {H:.1f} m', fontsize=10, color='red')
        ax2.text(0.1, 0.32, f'单宽流量: q = {q:.1f} m²/s', fontsize=10, color='green')
        ax2.text(0.1, 0.22, f'流量系数: m = {self.m}', fontsize=10)
        ax2.text(0.1, 0.12, f'挑角: θ = {self.theta}°', fontsize=10)
        ax2.text(0.1, 0.02, f'堰顶流速: v = {v_crest:.2f} m/s', fontsize=10, color='purple')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. H-Q关系曲线
        ax3 = plt.subplot(3, 3, 3)
        
        H_range = np.linspace(1, 10, 100)
        Q_range = [self.discharge(H_val) for H_val in H_range]
        
        ax3.plot(H_range, Q_range, 'b-', linewidth=2)
        ax3.plot(H, Q_design, 'ro', markersize=10, label=f'设计点(H={H:.1f}m)')
        
        ax3.set_xlabel('堰顶水头 H (m)', fontsize=10)
        ax3.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax3.set_title('H-Q关系曲线', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. WES剖面验证
        ax4 = plt.subplot(3, 3, 4)
        
        x_wes, y_wes = self.spillway_profile()
        ax4.plot(x_wes/H, y_wes/H, 'b-', linewidth=3, label='WES标准曲线')
        
        # 理论公式 y/Hd = -0.5(x/Hd)^1.85
        x_theory = x_wes / H
        y_theory = -0.5 * (x_theory ** 1.85)
        ax4.plot(x_theory, y_theory, 'r--', linewidth=2, alpha=0.7, label='理论公式')
        
        ax4.set_xlabel('x/Hd', fontsize=10)
        ax4.set_ylabel('y/Hd', fontsize=10)
        ax4.set_title('WES剖面无量纲化', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 流量系数影响
        ax5 = plt.subplot(3, 3, 5)
        
        m_range = np.linspace(0.45, 0.55, 50)
        Q_m = [m_val * self.b * (H ** 1.5) * np.sqrt(2 * self.g) for m_val in m_range]
        
        ax5.plot(m_range, Q_m, 'g-', linewidth=2)
        ax5.plot(self.m, Q_design, 'ro', markersize=10, label=f'm={self.m}')
        ax5.axhline(self.Q, color='red', linestyle='--', linewidth=1, alpha=0.7, label=f'设计Q={self.Q}m³/s')
        
        ax5.set_xlabel('流量系数 m', fontsize=10)
        ax5.set_ylabel('流量 Q (m³/s)', fontsize=10)
        ax5.set_title('流量系数影响', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 挑流轨迹详图
        ax6 = plt.subplot(3, 3, 6)
        
        # 不同挑角的轨迹
        theta_list = [20, 25, 30, 35, 40]
        colors_theta = plt.cm.rainbow(np.linspace(0, 1, len(theta_list)))
        
        for theta_val, color in zip(theta_list, colors_theta):
            theta_rad_val = np.deg2rad(theta_val)
            t_flight_val = np.linspace(0, 5, 100)
            x_traj_val = bucket['vb'] * np.cos(theta_rad_val) * t_flight_val
            y_traj_val = bucket['vb'] * np.sin(theta_rad_val) * t_flight_val - 0.5 * self.g * (t_flight_val ** 2)
            
            mask_val = y_traj_val > -bucket['delta_Z']
            ax6.plot(x_traj_val[mask_val], y_traj_val[mask_val], color=color, 
                    linewidth=2, label=f'θ={theta_val}°')
        
        ax6.axhline(0, color='k', linestyle='-', linewidth=1)
        ax6.axhline(-bucket['delta_Z'], color='brown', linestyle='--', linewidth=2, label='河床')
        
        ax6.set_xlabel('水平距离 (m)', fontsize=10)
        ax6.set_ylabel('相对高程 (m)', fontsize=10)
        ax6.set_title('不同挑角的挑流轨迹', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=7, loc='upper right')
        ax6.grid(True, alpha=0.3)
        
        # 7. 挑距与挑角关系
        ax7 = plt.subplot(3, 3, 7)
        
        theta_range = np.linspace(10, 50, 50)
        L_range = []
        
        for theta_val in theta_range:
            theta_rad_val = np.deg2rad(theta_val)
            vb = bucket['vb']
            delta_Z = bucket['delta_Z']
            
            term1 = (vb ** 2 * np.sin(2 * theta_rad_val)) / (2 * self.g)
            term2 = vb * np.cos(theta_rad_val) * np.sqrt(
                (vb ** 2 * np.sin(theta_rad_val) ** 2) / (2 * self.g ** 2) + 
                2 * delta_Z / self.g
            )
            L_val = term1 + term2
            L_range.append(L_val)
        
        ax7.plot(theta_range, L_range, 'b-', linewidth=2)
        ax7.plot(self.theta, bucket['L'], 'ro', markersize=10, label=f'设计θ={self.theta}°')
        
        # 标注最大挑距
        idx_max = np.argmax(L_range)
        ax7.plot(theta_range[idx_max], L_range[idx_max], 'g^', markersize=12, label=f'最优θ≈{theta_range[idx_max]:.0f}°')
        
        ax7.set_xlabel('挑角 θ (°)', fontsize=10)
        ax7.set_ylabel('挑距 L (m)', fontsize=10)
        ax7.set_title('挑距-挑角关系', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 冲刷深度计算
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '冲刷坑计算', fontsize=11, ha='center', fontweight='bold')
        ax8.text(0.1, 0.80, f'单宽流量: q = {q:.1f} m²/s', fontsize=10)
        ax8.text(0.1, 0.70, f'总水头: H₀ = {H + self.P:.1f} m', fontsize=10)
        ax8.text(0.1, 0.60, f'经验系数: K = 1.9', fontsize=10)
        ax8.text(0.1, 0.48, f't = K·q^0.5·H₀^0.25', fontsize=9, color='gray')
        ax8.text(0.1, 0.38, f'  = 1.9×{q:.1f}^0.5×{H+self.P:.1f}^0.25', fontsize=9, color='gray')
        ax8.text(0.1, 0.25, f'冲刷深度: t = {t_scour:.2f} m', fontsize=11, 
                color='red', fontweight='bold')
        
        ax8.text(0.1, 0.12, f'挑距: L = {bucket["L"]:.1f} m', fontsize=10, color='blue')
        ax8.text(0.1, 0.02, f'落差: ΔZ = {bucket["delta_Z"]:.1f} m', fontsize=10, color='green')
        
        ax8.set_title('消能计算', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        m_calc = self.flow_coefficient()
        
        table_data = [
            ['项目', '数值', '单位'],
            ['设计流量', f'{self.Q:.0f}', 'm³/s'],
            ['堰顶水头', f'{H:.2f}', 'm'],
            ['单宽流量', f'{q:.1f}', 'm²/s'],
            ['流量系数', f'{m_calc:.3f}', '-'],
            ['堰顶流速', f'{v_crest:.2f}', 'm/s'],
            ['挑角', f'{self.theta}', '°'],
            ['挑距', f'{bucket["L"]:.1f}', 'm'],
            ['冲刷深度', f'{t_scour:.2f}', 'm']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.45, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键参数
        for i in [1, 3, 8]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('设计结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch11_problem04_spillway_design.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch11_problem04_spillway_design.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第11章 水工建筑物 - 题4：溢洪道水力设计")
        print("="*70)
        
        H = self.head()
        Q_design = self.discharge()
        m_calc = self.flow_coefficient()
        q = self.unit_discharge()
        v_crest = self.crest_velocity()
        bucket = self.flip_bucket_design()
        t_scour = self.scour_depth()
        
        print(f"\n【设计参数】")
        print(f"设计流量: Q = {self.Q} m³/s")
        print(f"堰顶宽度: b = {self.b} m")
        print(f"堰顶高程: P = {self.P} m")
        print(f"上游水位: {self.H_up} m")
        print(f"挑角: θ = {self.theta}°")
        
        print(f"\n【溢流堰计算】")
        print(f"堰顶水头: H = {H:.2f} m")
        print(f"单宽流量: q = Q/b = {self.Q}/{self.b} = {q:.2f} m²/s")
        print(f"理论流量: Q = m·b·H^1.5·√(2g)")
        print(f"         = {self.m}×{self.b}×{H:.2f}^1.5×√(2×{self.g})")
        print(f"         = {Q_design:.2f} m³/s")
        print(f"反算流量系数: m = {m_calc:.4f}")
        print(f"堰顶流速: v = √(2gH) = {v_crest:.2f} m/s")
        
        print(f"\n【挑流消能】")
        print(f"鼻坎处水深: hb = {bucket['hb']:.2f} m")
        print(f"鼻坎处流速: vb = {bucket['vb']:.2f} m/s")
        print(f"落差: ΔZ = {bucket['delta_Z']:.2f} m")
        print(f"挑距: L = {bucket['L']:.2f} m")
        print(f"冲击动能: E = {bucket['E_impact']:.2f} kW")
        
        print(f"\n【冲刷计算】")
        print(f"冲刷深度: t = K·q^0.5·H₀^0.25")
        print(f"         = 1.9×{q:.2f}^0.5×{H+self.P:.2f}^0.25")
        print(f"         = {t_scour:.2f} m")
        
        print(f"\n✓ 溢洪道水力设计完成")
        print(f"\n{'='*70}\n")


def main():
    Q = 2000
    P = 80
    H_up = 85
    b = 50
    m = 0.502
    theta = 30
    
    spillway = SpillwayDesign(Q, P, H_up, b, m, theta)
    spillway.print_results()
    spillway.plot_analysis()


if __name__ == "__main__":
    main()
