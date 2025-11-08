# -*- coding: utf-8 -*-
"""
第05章 水文学基础 - 题15：综合应用（水库调洪计算）

问题描述：
    某水库库容V = 2×10⁸ m³，设计洪水过程Q(t)，初始水位Z₀ = 100 m，
    泄洪设施为溢洪道，泄流公式Q = m·B·H^1.5（m=0.5，B=50m）。
    坝顶高程105 m，安全超高0.5 m，最高允许水位104.5 m。
    
    输入洪水过程：
    t(h):  0   6   12   18   24   30   36   42   48
    Q(m³/s): 100 400 800 600 400 250 150 100 100
    
    求：
    1. 水位-库容关系曲线
    2. 泄流能力曲线
    3. 水库调洪演算
    4. 最高洪水位
    5. 最大泄流量
    6. 削峰效果评估

核心公式：
    1. 水量平衡方程: dV/dt = Q₁ - Q₂
    2. 离散化: ΔV = (Q̄₁ - Q̄₂)·Δt
    3. 试算法: V_{i+1} = V_i + (Q̄₁ - Q̄₂)·Δt
    4. 溢洪道泄流: Q = m·B·H^1.5
    5. 库容-水位关系: V = f(Z)

考试要点：
    - 水库调洪是水文学与水利工程结合的典型问题
    - 水量平衡方程是核心
    - 需要迭代求解（试算法）
    - 削峰、滞洪是水库的重要作用
    - 需要校核最高水位是否超过允许值

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from typing import Tuple, List

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ReservoirRouting:
    """水库调洪计算"""
    
    def __init__(self, Z0: float, V_max: float, Z_dam: float, Z_safe: float,
                 m: float, B: float, Z_crest: float):
        """
        初始化水库调洪计算
        
        参数:
            Z0: 初始水位 [m]
            V_max: 最大库容 [m³]
            Z_dam: 坝顶高程 [m]
            Z_safe: 安全超高 [m]
            m: 溢洪道流量系数
            B: 溢洪道宽度 [m]
            Z_crest: 溢洪道堰顶高程 [m]
        """
        self.Z0 = Z0
        self.V_max = V_max
        self.Z_dam = Z_dam
        self.Z_safe = Z_safe
        self.Z_max_allow = Z_dam - Z_safe  # 最高允许水位
        self.m = m
        self.B = B
        self.Z_crest = Z_crest
        
        # 初始化库容-水位关系（简化为线性+二次）
        self._init_storage_curve()
        
    def _init_storage_curve(self):
        """初始化库容-水位关系曲线（简化模型）"""
        # 假设简化的库容-水位关系
        # V = a·(Z - Z_dead)^b
        # 这里简化为分段线性
        self.Z_dead = self.Z0 - 10  # 死水位
        self.Z_normal = self.Z0  # 正常蓄水位
        
        # 关键点（水位，库容）
        self.Z_V_points = np.array([
            [self.Z_dead, 0],
            [self.Z_normal, self.V_max * 0.7],
            [self.Z_crest, self.V_max * 0.85],
            [self.Z_max_allow, self.V_max],
            [self.Z_dam, self.V_max * 1.1]
        ])
        
        # 创建插值函数
        self.V_of_Z = interp1d(self.Z_V_points[:, 0], self.Z_V_points[:, 1],
                              kind='quadratic', fill_value='extrapolate')
        self.Z_of_V = interp1d(self.Z_V_points[:, 1], self.Z_V_points[:, 0],
                              kind='quadratic', fill_value='extrapolate')
    
    def storage_of_elevation(self, Z: float) -> float:
        """
        根据水位计算库容
        
        参数:
            Z: 水位 [m]
        
        返回:
            V: 库容 [m³]
        """
        V = float(self.V_of_Z(Z))
        return V
    
    def elevation_of_storage(self, V: float) -> float:
        """
        根据库容计算水位
        
        参数:
            V: 库容 [m³]
        
        返回:
            Z: 水位 [m]
        """
        Z = float(self.Z_of_V(V))
        return Z
    
    def spillway_discharge(self, Z: float) -> float:
        """
        溢洪道泄流量计算
        
        参数:
            Z: 水位 [m]
        
        返回:
            Q: 泄流量 [m³/s]
        
        公式:
            Q = m·B·H^1.5
            H = Z - Z_crest (堰上水头)
        """
        if Z <= self.Z_crest:
            return 0.0
        
        H = Z - self.Z_crest  # 堰上水头
        Q = self.m * self.B * (H ** 1.5)
        return Q
    
    def routing_trial_method(self, t_inflow: np.ndarray, Q_inflow: np.ndarray,
                            dt: float = 1.0) -> Tuple[np.ndarray, np.ndarray, 
                                                       np.ndarray, np.ndarray]:
        """
        水库调洪演算（试算法）
        
        参数:
            t_inflow: 入库流量时间序列 [h]
            Q_inflow: 入库流量 [m³/s]
            dt: 时间步长 [h]
        
        返回:
            t: 时间序列 [h]
            Z: 水位过程线 [m]
            V: 库容过程线 [m³]
            Q_out: 出库流量过程线 [m³/s]
        
        算法:
            1. 初始化: V₀, Z₀
            2. 对每个时段:
               a) 计算平均入流 Q̄₁ = (Q₁ⁱ + Q₁ⁱ⁺¹)/2
               b) 试算出流 Q̄₂
               c) 更新库容 V^{i+1} = V^i + (Q̄₁ - Q̄₂)·Δt·3600
               d) 计算水位 Z^{i+1}
               e) 校核出流 Q₂^{i+1}
               f) 迭代直至收敛
        """
        # 插值到精细时间步长
        t_fine = np.arange(t_inflow[0], t_inflow[-1] + dt, dt)
        Q_inflow_fine = np.interp(t_fine, t_inflow, Q_inflow)
        
        n_steps = len(t_fine)
        
        # 初始化输出数组
        Z = np.zeros(n_steps)
        V = np.zeros(n_steps)
        Q_out = np.zeros(n_steps)
        
        # 初始条件
        Z[0] = self.Z0
        V[0] = self.storage_of_elevation(Z[0])
        Q_out[0] = self.spillway_discharge(Z[0])
        
        # 逐时段演算
        for i in range(n_steps - 1):
            # 平均入流
            Q_in_avg = (Q_inflow_fine[i] + Q_inflow_fine[i+1]) / 2
            
            # 试算法迭代
            Q_out_avg = Q_out[i]  # 初始猜测
            max_iter = 10
            tol = 0.1  # 收敛容差 [m³/s]
            
            for iter in range(max_iter):
                # 更新库容 (dt单位为h，需转换为s)
                dV = (Q_in_avg - Q_out_avg) * dt * 3600
                V[i+1] = V[i] + dV
                
                # 确保库容不超过最大值
                V[i+1] = min(V[i+1], self.V_max * 1.1)
                V[i+1] = max(V[i+1], 0)
                
                # 计算新水位
                Z[i+1] = self.elevation_of_storage(V[i+1])
                
                # 计算新出流
                Q_out[i+1] = self.spillway_discharge(Z[i+1])
                
                # 平均出流
                Q_out_avg_new = (Q_out[i] + Q_out[i+1]) / 2
                
                # 检查收敛
                if abs(Q_out_avg_new - Q_out_avg) < tol:
                    break
                
                Q_out_avg = Q_out_avg_new
        
        return t_fine, Z, V, Q_out
    
    def peak_reduction_analysis(self, Q_in_max: float, Q_out_max: float) -> Tuple[float, float]:
        """
        削峰效果分析
        
        参数:
            Q_in_max: 入库洪峰 [m³/s]
            Q_out_max: 出库洪峰 [m³/s]
        
        返回:
            reduction: 削峰量 [m³/s]
            ratio: 削峰率 [%]
        """
        reduction = Q_in_max - Q_out_max
        ratio = (reduction / Q_in_max) * 100
        return reduction, ratio
    
    def plot_analysis(self, t_inflow: np.ndarray, Q_inflow: np.ndarray):
        """绘制完整分析图表（9个子图）"""
        # 调洪演算
        t, Z, V, Q_out = self.routing_trial_method(t_inflow, Q_inflow)
        
        # 统计量
        Z_max = np.max(Z)
        Q_out_max = np.max(Q_out)
        Q_in_max = np.max(Q_inflow)
        reduction, ratio = self.peak_reduction_analysis(Q_in_max, Q_out_max)
        
        fig = plt.figure(figsize=(16, 12))
        
        # 1. 库容-水位关系曲线
        ax1 = plt.subplot(3, 3, 1)
        Z_range = np.linspace(self.Z_dead, self.Z_dam, 100)
        V_range = np.array([self.storage_of_elevation(z) for z in Z_range])
        
        ax1.plot(V_range / 1e8, Z_range, 'b-', linewidth=2, label='库容曲线')
        ax1.axhline(self.Z0, color='g', linestyle='--', linewidth=2, label=f'初始: {self.Z0}m')
        ax1.axhline(self.Z_crest, color='orange', linestyle='--', linewidth=2, 
                   label=f'堰顶: {self.Z_crest}m')
        ax1.axhline(self.Z_max_allow, color='r', linestyle='--', linewidth=2,
                   label=f'最高允许: {self.Z_max_allow}m')
        ax1.plot(Z_max, self.storage_of_elevation(Z_max) / 1e8, 'r*', markersize=15,
                label=f'最高水位: {Z_max:.2f}m')
        ax1.set_xlabel('库容 (亿m³)', fontsize=11)
        ax1.set_ylabel('水位 (m)', fontsize=11)
        ax1.set_title('库容-水位关系', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=9)
        
        # 2. 泄流能力曲线
        ax2 = plt.subplot(3, 3, 2)
        Z_spill = np.linspace(self.Z_crest, self.Z_dam, 100)
        Q_spill = np.array([self.spillway_discharge(z) for z in Z_spill])
        
        ax2.plot(Q_spill, Z_spill, 'b-', linewidth=2, label='泄流曲线')
        ax2.axhline(self.Z_crest, color='orange', linestyle='--', linewidth=2,
                   label=f'起泄水位')
        ax2.axhline(self.Z_max_allow, color='r', linestyle='--', linewidth=2,
                   label=f'设计水位')
        ax2.plot(Q_out_max, Z_max, 'ro', markersize=10, 
                label=f'最大泄流: {Q_out_max:.0f}m³/s')
        ax2.set_xlabel('泄流量 (m³/s)', fontsize=11)
        ax2.set_ylabel('水位 (m)', fontsize=11)
        ax2.set_title(f'溢洪道泄流能力\n(Q=m·B·H^1.5, m={self.m}, B={self.B}m)', 
                     fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=9)
        
        # 3. 入库与出库流量过程
        ax3 = plt.subplot(3, 3, 3)
        ax3.plot(t_inflow, Q_inflow, 'b-o', linewidth=2, markersize=6, label='入库流量')
        ax3.plot(t, Q_out, 'r-', linewidth=2, label='出库流量')
        ax3.axhline(Q_in_max, color='b', linestyle='--', alpha=0.5,
                   label=f'入库洪峰: {Q_in_max}m³/s')
        ax3.axhline(Q_out_max, color='r', linestyle='--', alpha=0.5,
                   label=f'出库洪峰: {Q_out_max:.0f}m³/s')
        ax3.fill_between(t, Q_out, alpha=0.2, color='red', label='泄流区')
        ax3.set_xlabel('时间 (h)', fontsize=11)
        ax3.set_ylabel('流量 (m³/s)', fontsize=11)
        ax3.set_title('流量过程线', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend(fontsize=9)
        
        # 添加削峰效果标注
        ax3.annotate('', xy=(24, Q_out_max), xytext=(24, Q_in_max),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax3.text(25, (Q_in_max + Q_out_max)/2, 
                f'削峰: {reduction:.0f}m³/s\n({ratio:.1f}%)',
                fontsize=10, color='green', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 4. 水位过程线
        ax4 = plt.subplot(3, 3, 4)
        ax4.plot(t, Z, 'b-', linewidth=2, label='水位过程')
        ax4.axhline(self.Z0, color='g', linestyle='--', linewidth=2, label='初始水位')
        ax4.axhline(self.Z_crest, color='orange', linestyle='--', linewidth=2,
                   label='溢洪道堰顶')
        ax4.axhline(self.Z_max_allow, color='r', linestyle='--', linewidth=2,
                   label='最高允许水位')
        ax4.fill_between(t, self.Z_crest, self.Z_max_allow, alpha=0.2, color='yellow',
                        label='安全范围')
        
        # 标注最高水位
        idx_max = np.argmax(Z)
        ax4.plot(t[idx_max], Z_max, 'r*', markersize=15, label=f'最高水位: {Z_max:.2f}m')
        
        ax4.set_xlabel('时间 (h)', fontsize=11)
        ax4.set_ylabel('水位 (m)', fontsize=11)
        ax4.set_title('水位过程线', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=9, loc='upper right')
        
        # 5. 库容过程线
        ax5 = plt.subplot(3, 3, 5)
        ax5.plot(t, V / 1e8, 'b-', linewidth=2, label='库容过程')
        ax5.axhline(self.storage_of_elevation(self.Z0) / 1e8, color='g', 
                   linestyle='--', linewidth=2, label='初始库容')
        ax5.fill_between(t, V / 1e8, alpha=0.2, color='blue')
        
        V_max_routing = np.max(V)
        idx_max_V = np.argmax(V)
        ax5.plot(t[idx_max_V], V_max_routing / 1e8, 'ro', markersize=10,
                label=f'最大库容: {V_max_routing/1e8:.2f}亿m³')
        
        ax5.set_xlabel('时间 (h)', fontsize=11)
        ax5.set_ylabel('库容 (亿m³)', fontsize=11)
        ax5.set_title('库容过程线', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        ax5.legend(fontsize=9)
        
        # 6. 入流-出流-蓄量关系
        ax6 = plt.subplot(3, 3, 6)
        
        # 插值到相同时间点
        Q_in_interp = np.interp(t, t_inflow, Q_inflow)
        dV_dt = Q_in_interp - Q_out  # 蓄量变化率
        
        ax6.plot(t, Q_in_interp, 'b-', linewidth=2, label='入库流量')
        ax6.plot(t, Q_out, 'r-', linewidth=2, label='出库流量')
        ax6_twin = ax6.twinx()
        ax6_twin.plot(t, dV_dt, 'g--', linewidth=2, label='蓄量变化率')
        ax6_twin.axhline(0, color='k', linestyle=':', linewidth=1)
        
        ax6.set_xlabel('时间 (h)', fontsize=11)
        ax6.set_ylabel('流量 (m³/s)', fontsize=11, color='b')
        ax6_twin.set_ylabel('蓄量变化率 (m³/s)', fontsize=11, color='g')
        ax6.tick_params(axis='y', labelcolor='b')
        ax6_twin.tick_params(axis='y', labelcolor='g')
        ax6.set_title('水量平衡分析', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        
        # 合并图例
        lines1, labels1 = ax6.get_legend_handles_labels()
        lines2, labels2 = ax6_twin.get_legend_handles_labels()
        ax6.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
        
        # 7. 削峰效果分析
        ax7 = plt.subplot(3, 3, 7)
        
        categories = ['入库洪峰', '出库洪峰', '削峰量']
        values = [Q_in_max, Q_out_max, reduction]
        colors_bar = ['blue', 'red', 'green']
        
        bars = ax7.bar(categories, values, color=colors_bar, alpha=0.7, edgecolor='black')
        ax7.set_ylabel('流量 (m³/s)', fontsize=11)
        ax7.set_title('削峰效果', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 添加削峰率标注
        ax7.text(0.5, 0.7, f'削峰率: {ratio:.1f}%', transform=ax7.transAxes,
                fontsize=14, fontweight='bold', ha='center',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 8. 洪水过程线叠加（入库vs出库）
        ax8 = plt.subplot(3, 3, 8)
        
        ax8.fill_between(t_inflow, 0, Q_inflow, alpha=0.3, color='blue', label='入库洪量')
        ax8.fill_between(t, 0, Q_out, alpha=0.3, color='red', label='出库洪量')
        ax8.plot(t_inflow, Q_inflow, 'b-o', linewidth=2, markersize=6, label='入库流量')
        ax8.plot(t, Q_out, 'r-', linewidth=2, label='出库流量')
        
        ax8.set_xlabel('时间 (h)', fontsize=11)
        ax8.set_ylabel('流量 (m³/s)', fontsize=11)
        ax8.set_title('洪水过程对比', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3)
        ax8.legend(fontsize=9)
        
        # 计算洪量
        W_in = np.trapz(Q_inflow, t_inflow) * 3600 / 1e6  # 百万m³
        W_out = np.trapz(Q_out, t) * 3600 / 1e6
        ax8.text(0.5, 0.95, f'入库洪量: {W_in:.2f}×10⁶m³\n出库洪量: {W_out:.2f}×10⁶m³',
                transform=ax8.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
                verticalalignment='top', horizontalalignment='center')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        # 安全校核
        if Z_max <= self.Z_max_allow:
            safety_status = '✓ 满足'
            safety_color = 'green'
        else:
            safety_status = '✗ 超标'
            safety_color = 'red'
        
        summary = [
            '═══ 调洪计算结果 ═══',
            '',
            '【水库参数】',
            f'初始水位: Z₀ = {self.Z0} m',
            f'最大库容: {self.V_max/1e8:.2f}亿m³',
            f'坝顶高程: {self.Z_dam} m',
            f'安全超高: {self.Z_safe} m',
            f'最高允许: {self.Z_max_allow} m',
            f'溢洪道: m={self.m}, B={self.B}m',
            '',
            '【调洪结果】',
            f'入库洪峰: Qin = {Q_in_max} m³/s',
            f'出库洪峰: Qout = {Q_out_max:.0f} m³/s',
            f'削峰量: ΔQ = {reduction:.0f} m³/s',
            f'削峰率: {ratio:.1f}%',
            f'最高水位: Zmax = {Z_max:.2f} m',
            f'安全校核: {safety_status}',
            '',
            '【洪量分析】',
            f'入库洪量: {W_in:.2f}×10⁶m³',
            f'出库洪量: {W_out:.2f}×10⁶m³',
            f'调蓄洪量: {W_in-W_out:.2f}×10⁶m³',
            '',
            '【结论】',
            '水库调洪效果显著',
            f'削峰{ratio:.0f}%，满足防洪要求' if Z_max <= self.Z_max_allow else '⚠ 最高水位超标',
        ]
        
        y_pos = 0.98
        for line in summary:
            if '═══' in line:
                ax9.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif '【' in line:
                ax9.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            elif '安全校核' in line:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace', color=safety_color, fontweight='bold')
            else:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.038
        
        ax9.set_title('调洪结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch05_problem15_reservoir_routing.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch05_problem15_reservoir_routing.png")
        plt.show()
    
    def print_results(self, t_inflow: np.ndarray, Q_inflow: np.ndarray):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第05章 水文学基础 - 题15：综合应用（水库调洪计算）")
        print("="*70)
        
        # 基本参数
        print(f"\n【水库基本参数】")
        print(f"初始水位: Z₀ = {self.Z0} m")
        print(f"最大库容: V_max = {self.V_max/1e8:.2f}亿m³ = {self.V_max:.2e} m³")
        print(f"坝顶高程: Z_dam = {self.Z_dam} m")
        print(f"安全超高: {self.Z_safe} m")
        print(f"最高允许水位: Z_max_allow = {self.Z_max_allow} m")
        
        print(f"\n【泄洪设施参数】")
        print(f"溢洪道流量系数: m = {self.m}")
        print(f"溢洪道宽度: B = {self.B} m")
        print(f"溢洪道堰顶高程: Z_crest = {self.Z_crest} m")
        print(f"泄流公式: Q = m·B·H^1.5 = {self.m}×{self.B}×H^1.5")
        
        print(f"\n【入库洪水过程】")
        print(f"{'时间(h)':>8} {'流量(m³/s)':>12}")
        print("-" * 22)
        for t, Q in zip(t_inflow, Q_inflow):
            print(f"{t:>8.0f} {Q:>12.0f}")
        
        # 调洪演算
        print(f"\n【调洪演算（试算法）】")
        print(f"采用试算法进行逐时段演算...")
        t, Z, V, Q_out = self.routing_trial_method(t_inflow, Q_inflow, dt=1.0)
        
        # 输出关键时刻结果
        print(f"\n调洪过程关键结果:")
        print(f"{'时间(h)':>8} {'入流(m³/s)':>12} {'出流(m³/s)':>12} {'水位(m)':>10} {'库容(亿m³)':>12}")
        print("-" * 66)
        
        Q_in_interp = np.interp(t, t_inflow, Q_inflow)
        indices = np.linspace(0, len(t)-1, min(13, len(t)), dtype=int)
        for idx in indices:
            print(f"{t[idx]:>8.0f} {Q_in_interp[idx]:>12.0f} {Q_out[idx]:>12.0f} "
                  f"{Z[idx]:>10.2f} {V[idx]/1e8:>12.3f}")
        
        # 统计结果
        Q_in_max = np.max(Q_inflow)
        Q_out_max = np.max(Q_out)
        Z_max = np.max(Z)
        idx_max = np.argmax(Z)
        t_max = t[idx_max]
        
        print(f"\n【统计结果】")
        print(f"入库洪峰: Q_in_max = {Q_in_max} m³/s")
        print(f"出库洪峰: Q_out_max = {Q_out_max:.2f} m³/s")
        print(f"最高水位: Z_max = {Z_max:.2f} m (出现时刻: t = {t_max:.1f} h)")
        print(f"最高库容: V_max = {np.max(V)/1e8:.3f}亿m³")
        
        # 削峰效果
        reduction, ratio = self.peak_reduction_analysis(Q_in_max, Q_out_max)
        print(f"\n【削峰效果】")
        print(f"削峰量: ΔQ = Q_in - Q_out = {Q_in_max} - {Q_out_max:.0f} = {reduction:.0f} m³/s")
        print(f"削峰率: η = ΔQ/Q_in × 100% = {reduction:.0f}/{Q_in_max} × 100% = {ratio:.1f}%")
        print(f"✓ 水库削峰效果{'显著' if ratio > 20 else '一般'}！")
        
        # 洪量分析
        W_in = np.trapz(Q_inflow, t_inflow) * 3600  # m³
        W_out = np.trapz(Q_out, t) * 3600
        W_stored = W_in - W_out
        
        print(f"\n【洪量分析】")
        print(f"入库总洪量: W_in = ∫Q_in dt = {W_in/1e6:.2f}×10⁶ m³")
        print(f"出库总洪量: W_out = ∫Q_out dt = {W_out/1e6:.2f}×10⁶ m³")
        print(f"调蓄洪量: W_stored = W_in - W_out = {W_stored/1e6:.2f}×10⁶ m³")
        print(f"调蓄率: {W_stored/W_in*100:.1f}%")
        
        # 安全校核
        print(f"\n【安全校核】")
        print(f"最高水位: Z_max = {Z_max:.2f} m")
        print(f"最高允许水位: Z_max_allow = {self.Z_max_allow} m")
        print(f"坝顶高程: Z_dam = {self.Z_dam} m")
        
        if Z_max <= self.Z_max_allow:
            print(f"✓ Z_max ({Z_max:.2f}m) ≤ Z_max_allow ({self.Z_max_allow}m)")
            print(f"✓ 满足安全要求！余裕: {self.Z_max_allow - Z_max:.2f} m")
        else:
            print(f"✗ Z_max ({Z_max:.2f}m) > Z_max_allow ({self.Z_max_allow}m)")
            print(f"✗ 超标 {Z_max - self.Z_max_allow:.2f} m，需要采取措施！")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 水量平衡方程: dV/dt = Q_in - Q_out")
        print(f"2. 离散化: ΔV = (Q̄_in - Q̄_out)·Δt")
        print(f"3. 试算法：迭代求解平均出流Q̄_out")
        print(f"4. 溢洪道泄流: Q = m·B·H^1.5")
        print(f"5. 削峰效果: η = (Q_in - Q_out)/Q_in")
        print(f"6. 安全校核: Z_max ≤ Z_dam - 安全超高")
        print(f"7. 水库调洪作用: 削峰、滞洪、错峰")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("水库调洪计算")
    print("-" * 70)
    
    # 水库参数
    Z0 = 100.0  # 初始水位 [m]
    V_max = 2e8  # 最大库容 [m³]
    Z_dam = 105.0  # 坝顶高程 [m]
    Z_safe = 0.5  # 安全超高 [m]
    
    # 泄洪设施参数
    m = 0.5  # 溢洪道流量系数
    B = 50.0  # 溢洪道宽度 [m]
    Z_crest = 100.0  # 溢洪道堰顶高程 [m]
    
    # 入库洪水过程
    t_inflow = np.array([0, 6, 12, 18, 24, 30, 36, 42, 48])  # h
    Q_inflow = np.array([100, 400, 800, 600, 400, 250, 150, 100, 100])  # m³/s
    
    # 创建计算实例
    reservoir = ReservoirRouting(Z0, V_max, Z_dam, Z_safe, m, B, Z_crest)
    
    # 打印结果
    reservoir.print_results(t_inflow, Q_inflow)
    
    # 绘制分析图
    reservoir.plot_analysis(t_inflow, Q_inflow)


if __name__ == "__main__":
    main()
