# -*- coding: utf-8 -*-
"""
第12章 河流动力学 - 题10：泥沙输移计算

问题描述：
    某河段流量Q = 1000 m³/s，河宽B = 200m
    水深h = 5m，河床坡度i = 0.0002
    河床泥沙d₅₀ = 0.2mm，上游含沙量S₀ = 3 kg/m³
    
    求：
    1. 泥沙起动流速
    2. 推移质输沙率
    3. 悬移质输沙率
    4. 总输沙率
    5. 输沙平衡分析

核心公式：
    1. 起动流速：v_c = K·√[(γ_s-γ_w)/γ_w·g·d]
    2. 推移质：Q_b = K_b·(v-v_c)^3
    3. 悬移质：Q_s = α·S·Q
    4. 总输沙率：Q_t = Q_b + Q_s

考试要点：
    - 泥沙起动
    - 推移质计算
    - 悬移质计算
    - 输沙平衡

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SedimentTransport:
    """泥沙输移计算"""
    
    def __init__(self, Q: float, B: float, h: float, i: float,
                 d50: float, S0: float):
        self.Q = Q  # 流量
        self.B = B  # 河宽
        self.h = h  # 水深
        self.i = i  # 河床坡度
        self.d50 = d50  # 中值粒径 mm
        self.S0 = S0  # 上游含沙量
        self.gamma_w = 10.0  # 水重度 kN/m³
        self.gamma_s = 26.5  # 泥沙重度 kN/m³
        self.g = 9.8
        self.rho = 1000  # 水密度 kg/m³
        self.rho_s = 2650  # 泥沙密度 kg/m³
        
    def flow_velocity(self) -> float:
        """流速"""
        return self.Q / (self.B * self.h)
    
    def bed_shear_stress(self) -> float:
        """床面剪切力"""
        tau = self.gamma_w * 1000 * self.h * self.i  # Pa
        return tau
    
    def critical_velocity(self) -> float:
        """
        泥沙起动流速（简化公式）
        v_c = K·√[(γ_s-γ_w)/γ_w·g·d]
        K ≈ 0.8-1.0
        """
        K = 0.9
        d_m = self.d50 / 1000  # 转为m
        
        v_c = K * np.sqrt(((self.gamma_s - self.gamma_w) / self.gamma_w) * self.g * d_m)
        return v_c
    
    def shields_parameter(self) -> float:
        """
        Shields参数
        θ = τ/(γ_s-γ_w)·d
        """
        tau = self.bed_shear_stress()
        d_m = self.d50 / 1000
        
        theta = tau / ((self.gamma_s - self.gamma_w) * 1000 * d_m)
        return theta
    
    def critical_shields(self) -> float:
        """临界Shields参数（约0.05）"""
        return 0.05
    
    def bedload_transport(self) -> float:
        """
        推移质输沙率（Meyer-Peter公式）
        q_b = K·(τ-τ_c)^1.5
        单宽输沙率 kg/(m·s)
        """
        tau = self.bed_shear_stress()
        theta = self.shields_parameter()
        theta_c = self.critical_shields()
        
        if theta > theta_c:
            # Einstein-Brown公式简化
            K = 8.0
            d_m = self.d50 / 1000
            q_b = K * np.sqrt(((self.gamma_s - self.gamma_w)/self.gamma_w) * self.g * (d_m ** 3)) * ((theta - theta_c) ** 1.5)
        else:
            q_b = 0
        
        # 总推移质输沙率
        Q_b = q_b * self.B
        return Q_b
    
    def suspended_load_transport(self) -> float:
        """
        悬移质输沙率
        Q_s = S·Q（假设含沙量均匀）
        """
        Q_s = self.S0 * self.Q
        return Q_s
    
    def total_sediment_transport(self) -> Dict:
        """总输沙率"""
        Q_b = self.bedload_transport()
        Q_s = self.suspended_load_transport()
        Q_t = Q_b + Q_s
        
        # 各部分比例
        ratio_b = Q_b / Q_t * 100 if Q_t > 0 else 0
        ratio_s = Q_s / Q_t * 100 if Q_t > 0 else 0
        
        return {
            'Q_b': Q_b,
            'Q_s': Q_s,
            'Q_t': Q_t,
            'ratio_b': ratio_b,
            'ratio_s': ratio_s
        }
    
    def settling_velocity(self) -> float:
        """
        泥沙沉降速度（Stokes公式）
        ω = (γ_s-γ_w)·d²/(18μ)
        """
        d_m = self.d50 / 1000
        mu = 1e-3  # 动力粘度 Pa·s
        
        omega = ((self.gamma_s - self.gamma_w) * 1000 * (d_m ** 2)) / (18 * mu)
        return omega
    
    def suspension_criterion(self) -> Tuple[float, bool]:
        """
        悬浮判别（Rouse数）
        Z = ω/(κ·u*)
        Z < 1: 易悬浮
        u* = √(τ/ρ)
        """
        tau = self.bed_shear_stress()
        u_star = np.sqrt(tau / self.rho)  # 剪切流速
        omega = self.settling_velocity()
        kappa = 0.4  # 卡门常数
        
        Z = omega / (kappa * u_star)
        is_suspended = Z < 1.0
        
        return Z, is_suspended
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        v = self.flow_velocity()
        v_c = self.critical_velocity()
        tau = self.bed_shear_stress()
        theta = self.shields_parameter()
        theta_c = self.critical_shields()
        transport = self.total_sediment_transport()
        omega = self.settling_velocity()
        Z, is_susp = self.suspension_criterion()
        
        # 1. 泥沙运动示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 河床
        x_bed = np.linspace(0, 10, 100)
        y_bed = np.zeros_like(x_bed)
        
        # 水体
        y_surface = y_bed + self.h
        
        ax1.fill_between(x_bed, y_bed-0.5, y_bed, color='brown', alpha=0.5, label='河床')
        ax1.fill_between(x_bed, y_bed, y_surface, color='lightblue', alpha=0.5, label='水体')
        ax1.plot(x_bed, y_surface, 'b-', linewidth=2)
        ax1.plot(x_bed, y_bed, 'k-', linewidth=2)
        
        # 标注泥沙运动
        ax1.text(5, 0.2, '推移质', ha='center', fontsize=10, color='red', fontweight='bold')
        ax1.text(5, self.h/2, '悬移质', ha='center', fontsize=10, color='blue', fontweight='bold')
        
        # 流速箭头
        ax1.arrow(2, self.h/2, 1, 0, head_width=0.3, head_length=0.2, fc='green', ec='green')
        ax1.text(3.5, self.h/2+0.5, f'v={v:.2f}m/s', fontsize=9, color='green')
        
        ax1.set_xlabel('距离 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('泥沙运动示意图', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.set_xlim(0, 10)
        ax1.set_ylim(-0.8, self.h+1)
        
        # 2. 基本参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '泥沙参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'流量: Q = {self.Q} m³/s', fontsize=10)
        ax2.text(0.1, 0.72, f'流速: v = {v:.2f} m/s', fontsize=10, color='blue')
        ax2.text(0.1, 0.62, f'水深: h = {self.h} m', fontsize=10)
        ax2.text(0.1, 0.52, f'粒径: d₅₀ = {self.d50} mm', fontsize=10, color='brown')
        ax2.text(0.1, 0.42, f'起动流速: v_c = {v_c:.3f} m/s', fontsize=10, color='red')
        ax2.text(0.1, 0.32, f'剪切应力: τ = {tau:.2f} Pa', fontsize=10)
        ax2.text(0.1, 0.22, f'Shields参数: θ = {theta:.4f}', fontsize=10)
        ax2.text(0.1, 0.10, f'含沙量: S₀ = {self.S0} kg/m³', fontsize=10, color='orange')
        
        if v > v_c:
            ax2.text(0.1, 0.00, '✓ 泥沙起动', fontsize=10, color='green', fontweight='bold')
        else:
            ax2.text(0.1, 0.00, '✗ 泥沙未起动', fontsize=10, color='red', fontweight='bold')
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 输沙率组成
        ax3 = plt.subplot(3, 3, 3)
        
        labels = ['推移质', '悬移质']
        sizes = [transport['ratio_b'], transport['ratio_s']]
        colors = ['brown', 'orange']
        
        wedges, texts, autotexts = ax3.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors, startangle=90)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax3.set_title(f'输沙率组成 (总计{transport["Q_t"]:.0f}kg/s)', 
                     fontsize=12, fontweight='bold')
        
        # 4. 流速-输沙率关系
        ax4 = plt.subplot(3, 3, 4)
        
        Q_range = np.linspace(500, 2000, 50)
        Q_b_range = []
        Q_s_range = []
        
        for Q_val in Q_range:
            sed_temp = SedimentTransport(Q_val, self.B, self.h, self.i, self.d50, self.S0)
            Q_b_range.append(sed_temp.bedload_transport())
            Q_s_range.append(sed_temp.suspended_load_transport())
        
        ax4.plot(Q_range, Q_b_range, 'r-', linewidth=2, label='推移质Q_b')
        ax4.plot(Q_range, Q_s_range, 'b-', linewidth=2, label='悬移质Q_s')
        ax4.plot(self.Q, transport['Q_b'], 'ro', markersize=10)
        ax4.plot(self.Q, transport['Q_s'], 'bo', markersize=10)
        
        ax4.set_xlabel('流量 Q (m³/s)', fontsize=10)
        ax4.set_ylabel('输沙率 (kg/s)', fontsize=10)
        ax4.set_title('流量-输沙率关系', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Shields判别图
        ax5 = plt.subplot(3, 3, 5)
        
        # Shields曲线（简化）
        Re_p = np.logspace(-1, 3, 100)
        theta_c_curve = 0.05 * np.ones_like(Re_p)  # 简化为常数
        
        ax5.loglog(Re_p, theta_c_curve, 'k-', linewidth=2, label='临界Shields曲线')
        ax5.axhline(theta_c, color='r', linestyle='--', linewidth=1, label=f'θ_c={theta_c}')
        ax5.plot(10, theta, 'go', markersize=12, label=f'本题θ={theta:.4f}')
        
        # 填充区域
        ax5.fill_between(Re_p, 0, theta_c_curve, alpha=0.2, color='blue', label='静止区')
        ax5.fill_between(Re_p, theta_c_curve, 1, alpha=0.2, color='red', label='运动区')
        
        ax5.set_xlabel('颗粒雷诺数 Re_p', fontsize=10)
        ax5.set_ylabel('Shields参数 θ', fontsize=10)
        ax5.set_title('Shields判别图', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3, which='both')
        ax5.set_ylim(0.01, 1)
        
        # 6. 悬浮判别
        ax6 = plt.subplot(3, 3, 6)
        ax6.axis('off')
        
        ax6.text(0.5, 0.95, '悬浮判别', fontsize=11, ha='center', fontweight='bold')
        ax6.text(0.1, 0.78, f'沉降速度: ω = {omega:.5f} m/s', fontsize=10)
        ax6.text(0.1, 0.68, f'           = {omega*100:.3f} cm/s', fontsize=9, color='gray')
        
        tau_val = self.bed_shear_stress()
        u_star = np.sqrt(tau_val / self.rho)
        ax6.text(0.1, 0.55, f'剪切流速: u* = √(τ/ρ) = {u_star:.3f} m/s', fontsize=10)
        
        ax6.text(0.1, 0.42, f'Rouse数: Z = ω/(κ·u*)', fontsize=10, color='gray')
        ax6.text(0.1, 0.32, f'        = {omega:.5f}/(0.4×{u_star:.3f})', fontsize=9, color='gray')
        ax6.text(0.1, 0.20, f'Z = {Z:.3f}', fontsize=11, 
                color='green' if is_susp else 'red', fontweight='bold')
        
        if is_susp:
            ax6.text(0.1, 0.08, '✓ Z<1，泥沙易悬浮', fontsize=10, color='green', fontweight='bold')
        else:
            ax6.text(0.1, 0.08, '✗ Z≥1，泥沙不易悬浮', fontsize=10, color='red', fontweight='bold')
        
        ax6.set_title('悬浮判别', fontsize=12, fontweight='bold')
        
        # 7. 粒径影响
        ax7 = plt.subplot(3, 3, 7)
        
        d_range = np.linspace(0.1, 1.0, 50)
        v_c_range = []
        Q_b_range_d = []
        
        for d_val in d_range:
            sed_temp = SedimentTransport(self.Q, self.B, self.h, self.i, d_val, self.S0)
            v_c_range.append(sed_temp.critical_velocity())
            Q_b_range_d.append(sed_temp.bedload_transport())
        
        ax7_twin = ax7.twinx()
        
        line1 = ax7.plot(d_range, v_c_range, 'b-', linewidth=2, label='起动流速v_c')
        line2 = ax7_twin.plot(d_range, Q_b_range_d, 'r-', linewidth=2, label='推移质Q_b')
        ax7.plot(self.d50, v_c, 'bo', markersize=10)
        ax7_twin.plot(self.d50, transport['Q_b'], 'ro', markersize=10)
        
        ax7.set_xlabel('粒径 d₅₀ (mm)', fontsize=10)
        ax7.set_ylabel('起动流速 v_c (m/s)', fontsize=10, color='blue')
        ax7_twin.set_ylabel('推移质输沙率 Q_b (kg/s)', fontsize=10, color='red')
        ax7.set_title('粒径影响分析', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, loc='upper left')
        
        # 8. 输沙平衡
        ax8 = plt.subplot(3, 3, 8)
        
        # 输沙平衡条状图
        components = ['上游来沙', '推移质', '悬移质', '总输沙']
        values = [self.S0 * self.Q, transport['Q_b'], transport['Q_s'], transport['Q_t']]
        colors_bar = ['blue', 'brown', 'orange', 'green']
        
        bars = ax8.barh(components, values, color=colors_bar, alpha=0.7, edgecolor='black')
        
        ax8.set_xlabel('输沙率 (kg/s)', fontsize=10)
        ax8.set_title('输沙平衡', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax8.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val:.0f}', ha='left', va='center', fontsize=9, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['流速', f'{v:.2f}', 'm/s'],
            ['起动流速', f'{v_c:.3f}', 'm/s'],
            ['Shields参数', f'{theta:.4f}', '-'],
            ['推移质', f'{transport["Q_b"]:.1f}', 'kg/s'],
            ['悬移质', f'{transport["Q_s"]:.1f}', 'kg/s'],
            ['总输沙率', f'{transport["Q_t"]:.0f}', 'kg/s'],
            ['日输沙量', f'{transport["Q_t"]*86400/1000:.0f}', 't/d']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.45, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [5, 6, 7, 8]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch12_problem10_sediment_transport.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch12_problem10_sediment_transport.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第12章 河流动力学 - 题10：泥沙输移计算")
        print("="*70)
        
        v = self.flow_velocity()
        v_c = self.critical_velocity()
        tau = self.bed_shear_stress()
        theta = self.shields_parameter()
        theta_c = self.critical_shields()
        transport = self.total_sediment_transport()
        omega = self.settling_velocity()
        Z, is_susp = self.suspension_criterion()
        
        print(f"\n【水流参数】")
        print(f"流量: Q = {self.Q} m³/s")
        print(f"河宽: B = {self.B} m")
        print(f"水深: h = {self.h} m")
        print(f"流速: v = Q/(B·h) = {v:.3f} m/s")
        print(f"河床坡度: i = {self.i}")
        
        print(f"\n【泥沙参数】")
        print(f"中值粒径: d₅₀ = {self.d50} mm = {self.d50/1000} m")
        print(f"上游含沙量: S₀ = {self.S0} kg/m³")
        print(f"泥沙重度: γₛ = {self.gamma_s} kN/m³")
        
        print(f"\n【泥沙起动】")
        print(f"床面剪切力: τ = γ·h·i = {self.gamma_w*1000}×{self.h}×{self.i} = {tau:.3f} Pa")
        print(f"起动流速: v_c = {v_c:.4f} m/s")
        if v > v_c:
            print(f"✓ v = {v:.3f} m/s > v_c = {v_c:.4f} m/s，泥沙起动")
        else:
            print(f"✗ v = {v:.3f} m/s < v_c = {v_c:.4f} m/s，泥沙未起动")
        
        print(f"\nShields参数: θ = τ/[(γₛ-γw)·d] = {theta:.5f}")
        print(f"临界Shields参数: θ_c = {theta_c}")
        if theta > theta_c:
            print(f"✓ θ = {theta:.5f} > θ_c = {theta_c}，泥沙运动")
        else:
            print(f"✗ θ = {theta:.5f} < θ_c = {theta_c}，泥沙静止")
        
        print(f"\n【推移质输沙】")
        print(f"推移质输沙率: Q_b = {transport['Q_b']:.2f} kg/s")
        print(f"推移质占比: {transport['ratio_b']:.2f}%")
        
        print(f"\n【悬移质输沙】")
        print(f"悬移质输沙率: Q_s = S₀·Q = {self.S0}×{self.Q} = {transport['Q_s']:.2f} kg/s")
        print(f"悬移质占比: {transport['ratio_s']:.2f}%")
        
        print(f"\n沉降速度: ω = {omega:.5f} m/s = {omega*100:.3f} cm/s")
        u_star = np.sqrt(tau / self.rho)
        print(f"剪切流速: u* = √(τ/ρ) = {u_star:.4f} m/s")
        print(f"Rouse数: Z = ω/(κ·u*) = {Z:.4f}")
        if is_susp:
            print(f"✓ Z = {Z:.4f} < 1，泥沙易悬浮")
        else:
            print(f"✗ Z = {Z:.4f} ≥ 1，泥沙不易悬浮")
        
        print(f"\n【总输沙率】")
        print(f"总输沙率: Q_t = Q_b + Q_s = {transport['Q_t']:.2f} kg/s")
        print(f"日输沙量: {transport['Q_t'] * 86400 / 1000:.2f} t/d")
        print(f"年输沙量: {transport['Q_t'] * 86400 * 365 / 1e6:.2f} 万t/年")
        
        print(f"\n✓ 泥沙输移计算完成")
        print(f"\n{'='*70}\n")


def main():
    Q = 1000
    B = 200
    h = 5
    i = 0.0002
    d50 = 0.2  # mm
    S0 = 3
    
    sediment = SedimentTransport(Q, B, h, i, d50, S0)
    sediment.print_results()
    sediment.plot_analysis()


if __name__ == "__main__":
    main()
