# -*- coding: utf-8 -*-
"""
第12章 河流动力学 - 题1：河床演变计算

问题描述：
    某河段长度L = 10km，河道平均宽度B = 200m
    上游来水流量Q = 1000 m³/s，含沙量S₀ = 5 kg/m³
    河床泥沙中值粒径d₅₀ = 0.25mm，河床坡度i = 0.0002
    河道糙率n = 0.025，泥沙干容重γₛ = 16 kN/m³
    
    求：
    1. 河床冲淤量计算
    2. 河床演变过程分析
    3. 挟沙能力计算
    4. 冲淤平衡分析
    5. 河床形态预测

核心公式：
    1. 挟沙能力：S* = K·V^m·h^n
    2. 冲淤量：ΔV = (S₀-S*)·Q·T/γₛ
    3. 床面剪切力：τ₀ = γ·R·i
    4. 输沙率：Qs = S·Q

考试要点：
    - 河床演变机理
    - 挟沙能力计算
    - 冲淤量估算
    - 河床形态分析

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RiverBedEvolution:
    """河床演变计算"""
    
    def __init__(self, L: float, B: float, Q: float, S0: float,
                 d50: float, i: float, n: float, gamma_s: float):
        self.L = L * 1000  # 转为m
        self.B = B  # 河道宽度
        self.Q = Q  # 流量
        self.S0 = S0  # 上游含沙量
        self.d50 = d50  # 中值粒径 mm
        self.i = i  # 河床坡度
        self.n = n  # 糙率
        self.gamma_s = gamma_s  # 泥沙干容重
        self.gamma_w = 10.0  # 水的重度 kN/m³
        self.g = 9.8
        
    def flow_parameters(self) -> Dict:
        """水流参数"""
        # 平均水深（曼宁公式反算）
        # Q = (1/n)·A·R^(2/3)·i^(1/2)
        # 假设宽浅河道：R ≈ h
        # Q = (1/n)·B·h·h^(2/3)·i^(1/2)
        # h = [Q·n/(B·i^(1/2))]^(3/5)
        
        h = (self.Q * self.n / (self.B * np.sqrt(self.i))) ** (3/5)
        
        # 流速
        v = self.Q / (self.B * h)
        
        # 水力半径
        R = self.B * h / (self.B + 2 * h)
        
        # 佛汝德数
        Fr = v / np.sqrt(self.g * h)
        
        return {
            'h': h,
            'v': v,
            'R': R,
            'Fr': Fr
        }
    
    def bed_shear_stress(self) -> float:
        """
        床面剪切力
        τ₀ = γ·R·i
        """
        flow = self.flow_parameters()
        tau0 = self.gamma_w * 1000 * flow['R'] * self.i  # Pa
        return tau0
    
    def critical_shear_stress(self) -> float:
        """
        起动剪切力（Shields公式）
        τc = θc·(γs-γw)·d50
        θc ≈ 0.05（经验值）
        """
        theta_c = 0.05
        gamma_s_Pa = self.gamma_s * 1000  # 转为Pa/m³
        gamma_w_Pa = self.gamma_w * 1000
        d50_m = self.d50 / 1000  # 转为m
        
        tau_c = theta_c * (gamma_s_Pa - gamma_w_Pa) * d50_m
        return tau_c
    
    def sediment_carrying_capacity(self) -> float:
        """
        挟沙能力（张瑞瑾公式）
        S* = K·(V/ω)^m·(h/d)^n
        简化：S* = K·V^m
        K=0.05, m=2.5（经验值）
        """
        flow = self.flow_parameters()
        K = 0.05
        m = 2.5
        
        S_star = K * (flow['v'] ** m)
        return S_star
    
    def sediment_transport_rate(self, S: float) -> float:
        """
        输沙率
        Qs = S·Q（kg/s）
        """
        return S * self.Q
    
    def scour_fill_volume(self, T: float = 86400) -> Dict:
        """
        冲淤量计算
        ΔV = (S₀-S*)·Q·T/γₛ
        
        参数：
        T - 时间段（秒），默认1天
        """
        S_star = self.sediment_carrying_capacity()
        
        # 输沙不平衡量
        delta_S = self.S0 - S_star
        
        # 冲淤体积（m³）
        gamma_s_kg = self.gamma_s * 1000 / self.g  # 转为kg/m³
        delta_V = (delta_S * self.Q * T) / gamma_s_kg
        
        # 冲淤厚度（m）
        delta_h = delta_V / (self.L * self.B)
        
        # 判断冲淤类型
        if delta_S > 0:
            scour_type = "淤积"
        elif delta_S < 0:
            scour_type = "冲刷"
        else:
            scour_type = "平衡"
        
        return {
            'S_star': S_star,
            'delta_S': delta_S,
            'delta_V': delta_V,
            'delta_h': delta_h,
            'scour_type': scour_type,
            'T': T
        }
    
    def evolution_process(self, T_total: float = 30*86400, dt: float = 86400) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        河床演变过程（时间序列）
        
        参数：
        T_total - 总时间（秒），默认30天
        dt - 时间步长（秒），默认1天
        """
        n_steps = int(T_total / dt)
        t_array = np.linspace(0, T_total/86400, n_steps)  # 转为天
        
        V_accum = np.zeros(n_steps)  # 累计冲淤量
        h_bed = np.zeros(n_steps)  # 河床高程变化
        
        h_current = 0  # 初始河床高程
        
        for i in range(n_steps):
            result = self.scour_fill_volume(dt)
            V_accum[i] = result['delta_V'] * (i + 1)  # 累计
            h_bed[i] = h_current + result['delta_h'] * (i + 1)
        
        return t_array, V_accum, h_bed
    
    def bed_form_classification(self) -> str:
        """
        河床形态分类（基于佛汝德数）
        """
        flow = self.flow_parameters()
        Fr = flow['Fr']
        
        if Fr < 0.3:
            return "平坦床面"
        elif 0.3 <= Fr < 0.5:
            return "沙波（ripple）"
        elif 0.5 <= Fr < 0.8:
            return "沙垄（dune）"
        elif 0.8 <= Fr < 1.0:
            return "过渡区"
        elif 1.0 <= Fr < 1.5:
            return "平坦床面（上游）"
        else:
            return "逆行沙波"
    
    def equilibrium_slope(self) -> float:
        """
        平衡坡度（当S=S*时）
        i_eq = τc/(γ·R)
        """
        tau_c = self.critical_shear_stress()
        flow = self.flow_parameters()
        
        i_eq = tau_c / (self.gamma_w * 1000 * flow['R'])
        return i_eq
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        flow = self.flow_parameters()
        tau0 = self.bed_shear_stress()
        tau_c = self.critical_shear_stress()
        S_star = self.sediment_carrying_capacity()
        scour_result = self.scour_fill_volume()
        t_array, V_accum, h_bed = self.evolution_process()
        bed_form = self.bed_form_classification()
        i_eq = self.equilibrium_slope()
        
        # 1. 河道纵剖面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        x_profile = np.linspace(0, self.L/1000, 100)  # km
        z_bed = -self.i * x_profile * 1000  # 河床高程
        z_water = z_bed + flow['h']  # 水面高程
        
        ax1.fill_between(x_profile, z_bed-2, z_bed, color='brown', alpha=0.5, label='河床')
        ax1.fill_between(x_profile, z_bed, z_water, color='lightblue', alpha=0.5, label='水体')
        ax1.plot(x_profile, z_water, 'b-', linewidth=2, label='水面线')
        ax1.plot(x_profile, z_bed, 'k-', linewidth=2, label='河床线')
        
        # 标注
        ax1.text(self.L/2000, flow['h']/2, f'h={flow["h"]:.2f}m\nv={flow["v"]:.2f}m/s', 
                ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax1.set_xlabel('距离 (km)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('河道纵剖面', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 水流参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '水流参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'流量: Q = {self.Q} m³/s', fontsize=10, color='blue')
        ax2.text(0.1, 0.72, f'河宽: B = {self.B} m', fontsize=10)
        ax2.text(0.1, 0.62, f'水深: h = {flow["h"]:.2f} m', fontsize=10, color='green')
        ax2.text(0.1, 0.52, f'流速: v = {flow["v"]:.2f} m/s', fontsize=10, color='red')
        ax2.text(0.1, 0.42, f'水力半径: R = {flow["R"]:.2f} m', fontsize=10)
        ax2.text(0.1, 0.32, f'佛汝德数: Fr = {flow["Fr"]:.3f}', fontsize=10)
        ax2.text(0.1, 0.20, f'河床形态: {bed_form}', fontsize=10, 
                color='purple', fontweight='bold')
        ax2.text(0.1, 0.08, f'坡度: i = {self.i}', fontsize=10)
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 泥沙参数
        ax3 = plt.subplot(3, 3, 3)
        ax3.axis('off')
        
        ax3.text(0.5, 0.95, '泥沙参数', fontsize=11, ha='center', fontweight='bold')
        ax3.text(0.1, 0.80, f'上游含沙量: S₀ = {self.S0} kg/m³', fontsize=10, color='brown')
        ax3.text(0.1, 0.70, f'挟沙能力: S* = {S_star:.3f} kg/m³', fontsize=10, color='orange')
        ax3.text(0.1, 0.60, f'含沙差: ΔS = {scour_result["delta_S"]:.3f} kg/m³', fontsize=10, color='red')
        ax3.text(0.1, 0.48, f'中值粒径: d₅₀ = {self.d50} mm', fontsize=10)
        ax3.text(0.1, 0.38, f'床面剪切力: τ₀ = {tau0:.2f} Pa', fontsize=10)
        ax3.text(0.1, 0.28, f'起动剪切力: τc = {tau_c:.2f} Pa', fontsize=10)
        
        if tau0 > tau_c:
            ax3.text(0.1, 0.15, '✓ 泥沙处于运动状态', fontsize=10, color='green', fontweight='bold')
        else:
            ax3.text(0.1, 0.15, '✗ 泥沙处于静止状态', fontsize=10, color='red', fontweight='bold')
        
        ax3.text(0.1, 0.03, f'冲淤类型: {scour_result["scour_type"]}', fontsize=11,
                color='blue', fontweight='bold')
        
        ax3.set_title('泥沙特性', fontsize=12, fontweight='bold')
        
        # 4. 冲淤量计算
        ax4 = plt.subplot(3, 3, 4)
        
        # 不同时间段的冲淤量
        T_range = np.array([1, 7, 15, 30, 60, 90])  # 天
        V_range = []
        h_range = []
        
        for T_days in T_range:
            result = self.scour_fill_volume(T_days * 86400)
            V_range.append(result['delta_V'])
            h_range.append(result['delta_h'])
        
        ax4.bar(T_range, np.array(V_range)/10000, color='orange', alpha=0.7, edgecolor='black')
        
        ax4.set_xlabel('时间 (天)', fontsize=10)
        ax4.set_ylabel('冲淤量 (万m³)', fontsize=10)
        ax4.set_title('不同时段冲淤量', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        for i, (T, V) in enumerate(zip(T_range, V_range)):
            ax4.text(T, V/10000, f'{V/10000:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 5. 河床演变过程
        ax5 = plt.subplot(3, 3, 5)
        
        ax5.plot(t_array, h_bed*100, 'b-', linewidth=2)
        ax5.fill_between(t_array, 0, h_bed*100, alpha=0.3, color='orange')
        ax5.axhline(0, color='k', linestyle='--', linewidth=1)
        
        ax5.set_xlabel('时间 (天)', fontsize=10)
        ax5.set_ylabel('河床高程变化 (cm)', fontsize=10)
        ax5.set_title('河床演变过程', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # 标注类型
        if scour_result['scour_type'] == "淤积":
            ax5.text(t_array[-1]/2, h_bed[-1]*100/2, '淤积', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='red')
        elif scour_result['scour_type'] == "冲刷":
            ax5.text(t_array[-1]/2, h_bed[-1]*100/2, '冲刷', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='blue')
        
        # 6. 挟沙能力与流速关系
        ax6 = plt.subplot(3, 3, 6)
        
        v_range = np.linspace(0.5, 3.0, 100)
        S_capacity = 0.05 * (v_range ** 2.5)
        
        ax6.plot(v_range, S_capacity, 'b-', linewidth=2)
        ax6.plot(flow['v'], S_star, 'ro', markersize=12, label=f'实际v={flow["v"]:.2f}m/s')
        ax6.axhline(self.S0, color='green', linestyle='--', linewidth=2, label=f'上游S₀={self.S0}kg/m³')
        
        ax6.set_xlabel('流速 v (m/s)', fontsize=10)
        ax6.set_ylabel('挟沙能力 S* (kg/m³)', fontsize=10)
        ax6.set_title('挟沙能力-流速关系', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 床面剪切力分布
        ax7 = plt.subplot(3, 3, 7)
        
        # 不同流量下的剪切力
        Q_range = np.linspace(500, 2000, 50)
        tau_range = []
        
        for Q_val in Q_range:
            river_temp = RiverBedEvolution(self.L/1000, self.B, Q_val, self.S0,
                                          self.d50, self.i, self.n, self.gamma_s)
            tau_range.append(river_temp.bed_shear_stress())
        
        ax7.plot(Q_range, tau_range, 'b-', linewidth=2)
        ax7.plot(self.Q, tau0, 'ro', markersize=12, label=f'Q={self.Q}m³/s')
        ax7.axhline(tau_c, color='red', linestyle='--', linewidth=2, label=f'τc={tau_c:.2f}Pa')
        
        ax7.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax7.set_ylabel('床面剪切力 τ₀ (Pa)', fontsize=10)
        ax7.set_title('流量-剪切力关系', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. 冲淤平衡分析
        ax8 = plt.subplot(3, 3, 8)
        
        # S-Q关系（保持平衡）
        Q_balance = np.linspace(500, 2000, 50)
        S_balance = []
        
        for Q_val in Q_balance:
            river_temp = RiverBedEvolution(self.L/1000, self.B, Q_val, self.S0,
                                          self.d50, self.i, self.n, self.gamma_s)
            S_balance.append(river_temp.sediment_carrying_capacity())
        
        ax8.plot(Q_balance, S_balance, 'b-', linewidth=2, label='挟沙能力S*')
        ax8.axhline(self.S0, color='green', linestyle='--', linewidth=2, label=f'上游S₀={self.S0}')
        ax8.plot(self.Q, S_star, 'ro', markersize=12, label='实际状态')
        
        # 填充冲淤区域
        ax8.fill_between(Q_balance, S_balance, self.S0, 
                        where=(np.array(S_balance) < self.S0), 
                        color='red', alpha=0.2, label='淤积区')
        ax8.fill_between(Q_balance, S_balance, self.S0, 
                        where=(np.array(S_balance) >= self.S0), 
                        color='blue', alpha=0.2, label='冲刷区')
        
        ax8.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax8.set_ylabel('含沙量 S (kg/m³)', fontsize=10)
        ax8.set_title('冲淤平衡分析', fontsize=12, fontweight='bold')
        ax8.legend(fontsize=8)
        ax8.grid(True, alpha=0.3)
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        result_30d = self.scour_fill_volume(30*86400)
        
        table_data = [
            ['项目', '数值', '单位'],
            ['流量', f'{self.Q:.0f}', 'm³/s'],
            ['水深', f'{flow["h"]:.2f}', 'm'],
            ['流速', f'{flow["v"]:.2f}', 'm/s'],
            ['上游含沙量', f'{self.S0}', 'kg/m³'],
            ['挟沙能力', f'{S_star:.3f}', 'kg/m³'],
            ['冲淤类型', scour_result['scour_type'], '-'],
            ['30天冲淤量', f'{result_30d["delta_V"]/10000:.2f}', '万m³']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.45, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮冲淤类型
        table[(7, 0)].set_facecolor('#FFF9E6')
        table[(7, 1)].set_facecolor('#FFF9E6')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch12_problem01_river_bed_evolution.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch12_problem01_river_bed_evolution.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第12章 河流动力学 - 题1：河床演变计算")
        print("="*70)
        
        flow = self.flow_parameters()
        tau0 = self.bed_shear_stress()
        tau_c = self.critical_shear_stress()
        S_star = self.sediment_carrying_capacity()
        scour_result = self.scour_fill_volume()
        bed_form = self.bed_form_classification()
        i_eq = self.equilibrium_slope()
        
        print(f"\n【河道参数】")
        print(f"河段长度: L = {self.L/1000} km")
        print(f"河道宽度: B = {self.B} m")
        print(f"河床坡度: i = {self.i}")
        print(f"糙率: n = {self.n}")
        
        print(f"\n【水流参数】")
        print(f"流量: Q = {self.Q} m³/s")
        print(f"水深: h = {flow['h']:.3f} m")
        print(f"流速: v = Q/(B·h) = {self.Q}/({self.B}×{flow['h']:.3f}) = {flow['v']:.3f} m/s")
        print(f"水力半径: R = {flow['R']:.3f} m")
        print(f"佛汝德数: Fr = v/√(g·h) = {flow['Fr']:.3f}")
        print(f"河床形态: {bed_form}")
        
        print(f"\n【泥沙参数】")
        print(f"中值粒径: d₅₀ = {self.d50} mm")
        print(f"泥沙干容重: γₛ = {self.gamma_s} kN/m³")
        print(f"上游含沙量: S₀ = {self.S0} kg/m³")
        
        print(f"\n【床面剪切力】")
        print(f"床面剪切力: τ₀ = γ·R·i = {self.gamma_w*1000}×{flow['R']:.3f}×{self.i} = {tau0:.3f} Pa")
        print(f"起动剪切力: τc = {tau_c:.3f} Pa")
        if tau0 > tau_c:
            print(f"✓ τ₀ = {tau0:.3f} Pa > τc = {tau_c:.3f} Pa，泥沙处于运动状态")
        else:
            print(f"✗ τ₀ = {tau0:.3f} Pa < τc = {tau_c:.3f} Pa，泥沙处于静止状态")
        
        print(f"\n【挟沙能力】")
        print(f"挟沙能力公式: S* = K·V^m（张瑞瑾公式简化）")
        print(f"  K = 0.05, m = 2.5")
        print(f"挟沙能力: S* = 0.05×{flow['v']:.3f}^2.5 = {S_star:.4f} kg/m³")
        print(f"上游含沙量: S₀ = {self.S0} kg/m³")
        print(f"含沙量差: ΔS = S₀ - S* = {scour_result['delta_S']:.4f} kg/m³")
        
        print(f"\n【冲淤计算】（1天）")
        print(f"输沙不平衡量: ΔS = {scour_result['delta_S']:.4f} kg/m³")
        print(f"冲淤体积: ΔV = ΔS·Q·T/γₛ")
        print(f"         = {scour_result['delta_S']:.4f}×{self.Q}×86400/{self.gamma_s*1000/self.g:.0f}")
        print(f"         = {scour_result['delta_V']:.2f} m³")
        print(f"冲淤厚度: Δh = ΔV/(L·B)")
        print(f"         = {scour_result['delta_V']:.2f}/({self.L}×{self.B})")
        print(f"         = {scour_result['delta_h']*100:.4f} cm")
        print(f"冲淤类型: {scour_result['scour_type']}")
        
        # 30天冲淤量
        result_30d = self.scour_fill_volume(30*86400)
        print(f"\n【30天累计冲淤】")
        print(f"冲淤体积: ΔV = {result_30d['delta_V']:.2f} m³ = {result_30d['delta_V']/10000:.2f} 万m³")
        print(f"冲淤厚度: Δh = {result_30d['delta_h']*100:.2f} cm")
        
        print(f"\n【平衡坡度】")
        print(f"平衡坡度: i_eq = τc/(γ·R) = {tau_c:.3f}/({self.gamma_w*1000}×{flow['R']:.3f}) = {i_eq:.6f}")
        print(f"实际坡度: i = {self.i}")
        if self.i > i_eq:
            print(f"i > i_eq，河床趋于冲刷")
        else:
            print(f"i < i_eq，河床趋于淤积")
        
        print(f"\n✓ 河床演变计算完成")
        print(f"\n{'='*70}\n")


def main():
    L = 10  # km
    B = 200
    Q = 1000
    S0 = 5
    d50 = 0.25  # mm
    i = 0.0002
    n = 0.025
    gamma_s = 16
    
    river = RiverBedEvolution(L, B, Q, S0, d50, i, n, gamma_s)
    river.print_results()
    river.plot_analysis()


if __name__ == "__main__":
    main()
