# -*- coding: utf-8 -*-
"""
第05章 水文学基础 - 题6：推理公式法（设计洪水计算）

问题描述：
    某小流域，面积F = 50 km²，主河道长度L = 12 km，平均坡度J = 0.005。
    该流域为农田（α₁ = 0.4）和林地（α₂ = 0.2）混合，面积比为6:4。
    设计暴雨：重现期P = 2%（50年一遇），1小时暴雨量P₁ = 60 mm。
    
    求：
    1. 流域综合径流系数α
    2. 汇流时间τ（用经验公式τ = 0.278 L^0.6/J^0.3）
    3. 设计流量Qp（用推理公式法）
    4. 如果流域面积增大到100 km²，流量如何变化？

核心公式：
    1. 推理公式：Qp = 0.278·α·Pτ·F/τ
    2. 汇流时间（克里奇公式）：τ = 0.278·L^0.6/J^0.3
    3. 暴雨强度递减：Pt = P₁·t^0.5
    4. 综合径流系数：α = Σ(αi·Fi)/ΣFi

考试要点：
    - 推理公式法是小流域设计洪水计算的常用方法
    - 综合径流系数需要面积加权
    - 暴雨量随历时增大而递减（强度降低）
    - 面积增大时，汇流时间也增大，流量增幅小于面积增幅
    - 适用条件：F < 200 km²，τ < 24 h

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RationalMethod:
    """推理公式法（设计洪水计算）"""
    
    def __init__(self, F: float, L: float, J: float, 
                 land_types: list, alpha_values: list, area_ratios: list,
                 P1: float, return_period: float):
        """
        初始化推理公式法计算
        
        参数:
            F: 流域面积 [km²]
            L: 主河道长度 [km]
            J: 平均坡度 [无量纲]
            land_types: 土地类型列表
            alpha_values: 各类型径流系数 [无量纲]
            area_ratios: 各类型面积比例 [无量纲]
            P1: 1小时暴雨量 [mm]
            return_period: 重现期 [年]
        """
        self.F = F
        self.L = L
        self.J = J
        self.land_types = land_types
        self.alpha_values = np.array(alpha_values)
        self.area_ratios = np.array(area_ratios)
        self.P1 = P1
        self.T = return_period
        
    def composite_runoff_coefficient(self) -> float:
        """
        计算综合径流系数（面积加权）
        
        返回:
            α: 综合径流系数 [无量纲]
        
        公式:
            α = Σ(αi·Fi) / ΣFi
        """
        alpha = np.sum(self.alpha_values * self.area_ratios)
        return alpha
    
    def concentration_time_kraven(self) -> float:
        """
        计算汇流时间（克里奇公式）
        
        返回:
            τ: 汇流时间 [h]
        
        公式:
            τ = 0.278 · L^0.6 / J^0.3
        """
        tau = 0.278 * (self.L ** 0.6) / (self.J ** 0.3)
        return tau
    
    def concentration_time_kirpich(self, v: float = None) -> float:
        """
        计算汇流时间（其他经验公式）
        
        参数:
            v: 平均流速 [m/s]，如果提供则用简化公式
        
        返回:
            τ: 汇流时间 [h]
        """
        if v is not None:
            # 简化公式: τ = L/(3.6v)
            tau = self.L / (3.6 * v)
        else:
            # 福柯维奇公式: τ = 0.021·L^0.76/J^0.19
            tau = 0.021 * (self.L ** 0.76) / (self.J ** 0.19)
        return tau
    
    def rainfall_duration_scaling(self, t: float, method: str = 'root') -> float:
        """
        暴雨量随历时的递减关系
        
        参数:
            t: 历时 [h]
            method: 'root'（平方根法）或'power'（指数法）
        
        返回:
            Pt: t小时暴雨量 [mm]
        
        公式:
            平方根法: Pt = P₁ · t^0.5
            指数法: Pt = P₁ · t^0.7
        """
        if method == 'root':
            # 平方根法（常用）
            Pt = self.P1 * (t ** 0.5)
        else:
            # 指数法
            Pt = self.P1 * (t ** 0.7)
        return Pt
    
    def design_discharge_rational(self, alpha: float = None, tau: float = None) -> Tuple[float, float]:
        """
        推理公式计算设计流量
        
        参数:
            alpha: 径流系数（如不提供则自动计算）
            tau: 汇流时间（如不提供则自动计算）
        
        返回:
            Qp: 设计洪峰流量 [m³/s]
            Ptau: 汇流时间内降雨量 [mm]
        
        公式:
            Qp = 0.278 · α · Pτ · F / τ
        """
        if alpha is None:
            alpha = self.composite_runoff_coefficient()
        if tau is None:
            tau = self.concentration_time_kraven()
        
        # 计算τ时间内的降雨量
        Ptau = self.rainfall_duration_scaling(tau)
        
        # 推理公式
        Qp = 0.278 * alpha * Ptau * self.F / tau
        
        return Qp, Ptau
    
    def basin_area_effect(self, F_new: float) -> Tuple[float, float, float, float]:
        """
        流域面积变化的影响分析
        
        参数:
            F_new: 新的流域面积 [km²]
        
        返回:
            L_new: 新的河道长度 [km]
            tau_new: 新的汇流时间 [h]
            Qp_new: 新的设计流量 [m³/s]
            ratio: 流量增幅比
        """
        # 假设河道长度与流域面积的平方根成正比
        L_new = self.L * np.sqrt(F_new / self.F)
        
        # 新的汇流时间
        tau_new = 0.278 * (L_new ** 0.6) / (self.J ** 0.3)
        
        # 新的降雨量
        Ptau_new = self.rainfall_duration_scaling(tau_new)
        
        # 新的流量
        alpha = self.composite_runoff_coefficient()
        Qp_new = 0.278 * alpha * Ptau_new * F_new / tau_new
        
        # 原流量
        Qp_old, _ = self.design_discharge_rational()
        
        ratio = Qp_new / Qp_old
        
        return L_new, tau_new, Qp_new, ratio
    
    def runoff_coefficient_analysis(self, alpha_range: tuple = (0.1, 0.8), 
                                    n_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        径流系数影响分析
        
        参数:
            alpha_range: 径流系数范围
            n_points: 计算点数
        
        返回:
            alphas: 径流系数数组
            Qps: 对应的流量数组
        """
        alphas = np.linspace(alpha_range[0], alpha_range[1], n_points)
        tau = self.concentration_time_kraven()
        Ptau = self.rainfall_duration_scaling(tau)
        
        Qps = 0.278 * alphas * Ptau * self.F / tau
        
        return alphas, Qps
    
    def concentration_time_analysis(self, L_range: tuple = (5, 20), 
                                   n_points: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        汇流时间（河道长度）影响分析
        
        参数:
            L_range: 河道长度范围 [km]
            n_points: 计算点数
        
        返回:
            Ls: 长度数组
            taus: 汇流时间数组
            Qps: 流量数组
        """
        Ls = np.linspace(L_range[0], L_range[1], n_points)
        taus = 0.278 * (Ls ** 0.6) / (self.J ** 0.3)
        
        alpha = self.composite_runoff_coefficient()
        Qps = np.zeros_like(Ls)
        
        for i, tau in enumerate(taus):
            Ptau = self.rainfall_duration_scaling(tau)
            Qps[i] = 0.278 * alpha * Ptau * self.F / tau
        
        return Ls, taus, Qps
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算基本参数
        alpha = self.composite_runoff_coefficient()
        tau = self.concentration_time_kraven()
        Qp, Ptau = self.design_discharge_rational()
        
        # 1. 流域组成与径流系数
        ax1 = plt.subplot(3, 3, 1)
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.land_types)))
        ax1.pie(self.area_ratios, labels=self.land_types, autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax1.set_title('流域土地利用组成', fontsize=12, fontweight='bold')
        
        # 添加径流系数信息
        text = '\n'.join([f'{self.land_types[i]}: α={self.alpha_values[i]:.2f}'
                         for i in range(len(self.land_types))])
        ax1.text(1.5, 0, text, fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 2. 综合径流系数计算
        ax2 = plt.subplot(3, 3, 2)
        areas = self.area_ratios * self.F
        x = np.arange(len(self.land_types))
        bars = ax2.bar(x, self.alpha_values, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_xticks(x)
        ax2.set_xticklabels(self.land_types)
        ax2.set_ylabel('径流系数 α', fontsize=11)
        ax2.set_title('各类型径流系数', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(alpha, color='r', linestyle='--', linewidth=2, 
                   label=f'综合: α={alpha:.3f}')
        ax2.legend()
        
        # 添加面积标注
        for i, (bar, area) in enumerate(zip(bars, areas)):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{area:.1f} km²', ha='center', va='bottom', fontsize=9)
        
        # 3. 汇流时间与河道特性
        ax3 = plt.subplot(3, 3, 3)
        params = ['河长L\n(km)', '坡度J\n×1000', '汇流时间τ\n(h)']
        values = [self.L, self.J*1000, tau]
        bars = ax3.bar(params, values, color=['skyblue', 'lightcoral', 'lightgreen'],
                      alpha=0.7, edgecolor='black')
        ax3.set_ylabel('参数值', fontsize=11)
        ax3.set_title('流域特性参数', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 4. 暴雨量随历时变化
        ax4 = plt.subplot(3, 3, 4)
        t_range = np.linspace(1, 24, 100)
        P_root = np.array([self.rainfall_duration_scaling(t, 'root') for t in t_range])
        P_power = np.array([self.rainfall_duration_scaling(t, 'power') for t in t_range])
        
        ax4.plot(t_range, P_root, 'b-', linewidth=2, label='平方根法: $P_t=P_1·t^{0.5}$')
        ax4.plot(t_range, P_power, 'r--', linewidth=2, label='指数法: $P_t=P_1·t^{0.7}$')
        ax4.plot(1, self.P1, 'ro', markersize=10, label=f'已知: $P_1$={self.P1} mm')
        ax4.plot(tau, Ptau, 'gs', markersize=10, label=f'设计: $P_τ$={Ptau:.1f} mm')
        ax4.set_xlabel('历时 t (h)', fontsize=11)
        ax4.set_ylabel('降雨量 P (mm)', fontsize=11)
        ax4.set_title('暴雨量随历时递减关系', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=9)
        
        # 5. 推理公式计算流程
        ax5 = plt.subplot(3, 3, 5)
        ax5.axis('off')
        
        # 计算流程
        steps = [
            f'【步骤1】综合径流系数',
            f'α = Σ(αi·Fi)/ΣFi = {alpha:.3f}',
            '',
            f'【步骤2】汇流时间（克里奇公式）',
            f'τ = 0.278·L^0.6/J^0.3',
            f'τ = 0.278×{self.L**0.6:.2f}/{self.J**0.3:.3f} = {tau:.2f} h',
            '',
            f'【步骤3】暴雨量换算',
            f'Pτ = P₁·τ^0.5 = {self.P1}×{tau**0.5:.2f} = {Ptau:.1f} mm',
            '',
            f'【步骤4】推理公式',
            f'Qp = 0.278·α·Pτ·F/τ',
            f'Qp = 0.278×{alpha:.3f}×{Ptau:.1f}×{self.F}/{tau:.2f}',
            f'Qp = {Qp:.2f} m³/s'
        ]
        
        y_pos = 0.95
        for step in steps:
            if '【' in step:
                ax5.text(0.1, y_pos, step, fontsize=11, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif step == '':
                y_pos -= 0.02
                continue
            else:
                ax5.text(0.15, y_pos, step, fontsize=10, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.065
        
        ax5.set_title('推理公式计算流程', fontsize=12, fontweight='bold')
        
        # 6. 径流系数影响分析
        ax6 = plt.subplot(3, 3, 6)
        alphas, Qps_alpha = self.runoff_coefficient_analysis()
        ax6.plot(alphas, Qps_alpha, 'b-', linewidth=2)
        ax6.plot(alpha, Qp, 'ro', markersize=10, label=f'设计工况: α={alpha:.3f}')
        ax6.set_xlabel('径流系数 α', fontsize=11)
        ax6.set_ylabel('设计流量 Qp (m³/s)', fontsize=11)
        ax6.set_title('径流系数对流量的影响', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        ax6.legend()
        
        # 添加线性关系说明
        ax6.text(0.5, 0.95, 'Qp ∝ α（线性关系）', transform=ax6.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        # 7. 河道长度与汇流时间影响
        ax7 = plt.subplot(3, 3, 7)
        Ls, taus, Qps_L = self.concentration_time_analysis()
        
        ax7_twin = ax7.twinx()
        line1 = ax7.plot(Ls, taus, 'b-', linewidth=2, label='汇流时间 τ')
        line2 = ax7_twin.plot(Ls, Qps_L, 'r-', linewidth=2, label='设计流量 Qp')
        
        ax7.plot(self.L, tau, 'bo', markersize=10)
        ax7_twin.plot(self.L, Qp, 'ro', markersize=10)
        
        ax7.set_xlabel('河道长度 L (km)', fontsize=11)
        ax7.set_ylabel('汇流时间 τ (h)', fontsize=11, color='b')
        ax7_twin.set_ylabel('设计流量 Qp (m³/s)', fontsize=11, color='r')
        ax7.tick_params(axis='y', labelcolor='b')
        ax7_twin.tick_params(axis='y', labelcolor='r')
        ax7.set_title('河道长度的综合影响', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, loc='upper left')
        
        # 8. 流域面积增大的影响
        ax8 = plt.subplot(3, 3, 8)
        F_range = np.linspace(self.F, 200, 50)
        results = [self.basin_area_effect(F) for F in F_range]
        Qps_F = np.array([r[2] for r in results])
        ratios = np.array([r[3] for r in results])
        
        ax8_twin = ax8.twinx()
        line1 = ax8.plot(F_range, Qps_F, 'b-', linewidth=2, label='设计流量 Qp')
        line2 = ax8_twin.plot(F_range, ratios, 'r--', linewidth=2, label='流量比 Qp\'/Qp')
        
        # 标注关键点
        L_new, tau_new, Qp_new, ratio = self.basin_area_effect(100)
        ax8.plot(100, Qp_new, 'bs', markersize=10, 
                label=f'F=100 km²: Qp={Qp_new:.1f} m³/s')
        ax8_twin.plot(100, ratio, 'rs', markersize=10)
        
        ax8.set_xlabel('流域面积 F (km²)', fontsize=11)
        ax8.set_ylabel('设计流量 Qp (m³/s)', fontsize=11, color='b')
        ax8_twin.set_ylabel('流量比', fontsize=11, color='r')
        ax8.tick_params(axis='y', labelcolor='b')
        ax8_twin.tick_params(axis='y', labelcolor='r')
        ax8.set_title('流域面积变化的影响', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3)
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax8.legend(lines, labels, loc='upper left', fontsize=9)
        
        # 添加说明
        ax8.text(0.5, 0.25, f'面积增大1倍\n流量增大{(ratio-1)*100:.1f}%\n（不是2倍）',
                transform=ax8.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                verticalalignment='top', horizontalalignment='center')
        
        # 9. 设计结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        # 汇总结果
        summary = [
            '═══ 设计结果汇总 ═══',
            '',
            f'【基本参数】',
            f'流域面积: F = {self.F} km²',
            f'河道长度: L = {self.L} km',
            f'平均坡度: J = {self.J}',
            f'重现期: T = {self.T} 年 (P={100/self.T:.1f}%)',
            f'1h暴雨量: P₁ = {self.P1} mm',
            '',
            f'【计算结果】',
            f'综合径流系数: α = {alpha:.3f}',
            f'汇流时间: τ = {tau:.2f} h',
            f'{tau:.1f}h暴雨量: Pτ = {Ptau:.1f} mm',
            f'设计流量: Qp = {Qp:.2f} m³/s',
            '',
            f'【面积增大影响(F=100 km²)】',
            f'新河长: L\' = {L_new:.1f} km',
            f'新汇流时间: τ\' = {tau_new:.1f} h',
            f'新设计流量: Qp\' = {Qp_new:.1f} m³/s',
            f'流量增幅: {(ratio-1)*100:.1f}%',
        ]
        
        y_pos = 0.98
        for line in summary:
            if '═══' in line:
                ax9.text(0.5, y_pos, line, fontsize=12, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif '【' in line:
                ax9.text(0.1, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax9.text(0.15, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.045
        
        ax9.set_title('计算结果与分析', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch05_problem06_rational_method.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch05_problem06_rational_method.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第05章 水文学基础 - 题6：推理公式法（设计洪水计算）")
        print("="*70)
        
        # 基本参数
        print(f"\n【基本参数】")
        print(f"流域面积: F = {self.F} km²")
        print(f"河道长度: L = {self.L} km")
        print(f"平均坡度: J = {self.J}")
        print(f"重现期: T = {self.T} 年 (P = {100/self.T:.1f}%)")
        print(f"1小时暴雨量: P₁ = {self.P1} mm")
        print(f"\n流域组成:")
        for i, land_type in enumerate(self.land_types):
            area = self.area_ratios[i] * self.F
            print(f"  {land_type}: 面积 {area:.1f} km² ({self.area_ratios[i]*100:.0f}%), "
                  f"径流系数 α = {self.alpha_values[i]:.2f}")
        
        # (1) 综合径流系数
        print(f"\n【问题1】综合径流系数")
        alpha = self.composite_runoff_coefficient()
        print(f"面积加权平均: α = Σ(αi·Fi) / ΣFi")
        print(f"α = {alpha:.4f}")
        print(f"✓ 综合径流系数: α = {alpha:.3f}")
        
        # (2) 汇流时间
        print(f"\n【问题2】汇流时间（克里奇公式）")
        tau = self.concentration_time_kraven()
        print(f"τ = 0.278 · L^0.6 / J^0.3")
        print(f"τ = 0.278 × {self.L}^0.6 / {self.J}^0.3")
        print(f"τ = 0.278 × {self.L**0.6:.3f} / {self.J**0.3:.3f}")
        print(f"τ = {tau:.3f} h")
        print(f"✓ 汇流时间: τ = {tau:.2f} h")
        
        # 其他公式对比
        tau_kirpich = self.concentration_time_kirpich()
        print(f"\n对比：福柯维奇公式: τ = {tau_kirpich:.2f} h")
        
        # (3) 设计流量
        print(f"\n【问题3】设计流量（推理公式法）")
        Qp, Ptau = self.design_discharge_rational()
        
        print(f"\n步骤1：计算τ={tau:.1f}h内的降雨量")
        print(f"暴雨强度递减: Pt = P₁ · t^0.5")
        print(f"P{tau:.1f} = {self.P1} × {tau}^0.5")
        print(f"P{tau:.1f} = {self.P1} × {tau**0.5:.3f} = {Ptau:.2f} mm")
        
        print(f"\n步骤2：推理公式计算流量")
        print(f"Qp = 0.278 · α · Pτ · F / τ")
        print(f"Qp = 0.278 × {alpha:.3f} × {Ptau:.1f} × {self.F} / {tau:.2f}")
        print(f"Qp = {Qp:.3f} m³/s")
        print(f"✓ 设计流量: Qp = {Qp:.2f} m³/s")
        
        # (4) 流域面积影响
        print(f"\n【问题4】流域面积增大到100 km²的影响")
        L_new, tau_new, Qp_new, ratio = self.basin_area_effect(100)
        
        print(f"\n假设河道长度与流域面积的平方根成正比:")
        print(f"L' = L × √(F'/F) = {self.L} × √(100/{self.F})")
        print(f"L' = {L_new:.2f} km")
        
        print(f"\n新的汇流时间:")
        print(f"τ' = 0.278 × {L_new:.2f}^0.6 / {self.J}^0.3")
        print(f"τ' = {tau_new:.2f} h")
        
        Ptau_new = self.rainfall_duration_scaling(tau_new)
        print(f"\n新的降雨量:")
        print(f"P{tau_new:.1f} = {self.P1} × {tau_new}^0.5 = {Ptau_new:.2f} mm")
        
        print(f"\n新的设计流量:")
        print(f"Qp' = 0.278 × {alpha:.3f} × {Ptau_new:.1f} × 100 / {tau_new:.2f}")
        print(f"Qp' = {Qp_new:.2f} m³/s")
        
        print(f"\n流量比:")
        print(f"Qp'/Qp = {Qp_new:.1f}/{Qp:.1f} = {ratio:.2f}")
        print(f"✓ 流量增幅: {(ratio-1)*100:.1f}% (面积增大1倍，流量增幅小于1倍)")
        
        print(f"\n结论:")
        print(f"  - 面积增大1倍: {self.F} → 100 km²")
        print(f"  - 流量增大: {Qp:.1f} → {Qp_new:.1f} m³/s (增幅{(ratio-1)*100:.1f}%)")
        print(f"  - 原因: 汇流时间也增大({tau:.1f}→{tau_new:.1f}h)，暴雨强度递减")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 推理公式: Qp = 0.278·α·Pτ·F/τ (必须记住!)")
        print(f"2. 综合径流系数需要面积加权")
        print(f"3. 汇流时间常用克里奇公式: τ = 0.278·L^0.6/J^0.3")
        print(f"4. 暴雨强度随历时递减: Pt = P₁·t^0.5 (常用)")
        print(f"5. 适用条件: F < 200 km², τ < 24 h")
        print(f"6. 面积增大时，流量增幅小于面积增幅（因τ也增大）")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("推理公式法（设计洪水计算）")
    print("-" * 70)
    
    # 基本参数
    F = 50.0  # 流域面积 [km²]
    L = 12.0  # 主河道长度 [km]
    J = 0.005  # 平均坡度
    
    # 土地类型与径流系数
    land_types = ['农田', '林地']
    alpha_values = [0.4, 0.2]
    area_ratios = [0.6, 0.4]
    
    # 设计暴雨
    P1 = 60.0  # 1小时暴雨量 [mm]
    return_period = 50.0  # 重现期 [年]
    
    # 创建计算实例
    rational = RationalMethod(F, L, J, land_types, alpha_values, area_ratios, 
                             P1, return_period)
    
    # 打印结果
    rational.print_results()
    
    # 绘制分析图
    rational.plot_analysis()


if __name__ == "__main__":
    main()
