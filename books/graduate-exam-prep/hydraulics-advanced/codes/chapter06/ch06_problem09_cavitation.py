# -*- coding: utf-8 -*-
"""
第06章 水泵与水泵站 - 题9：水泵汽蚀分析与防护

问题描述：
    某离心泵从敞口水池抽水，水温20°C，泵轴中心线高出水面Hs = 4.5m
    水泵性能参数：Q = 0.2 m³/s, n = 1450 r/min
    吸水管：d = 300mm, L = 15m, λ = 0.025, 局部损失系数ζ = 5.0
    
    已知：20°C水的饱和蒸汽压 pv = 2.34 kPa
          大气压 pa = 101.3 kPa
          水泵必需汽蚀余量 (NPSH)r = 3.5 m
    
    求：
    1. 吸水管水头损失
    2. 有效汽蚀余量NPSHa
    3. 汽蚀校核
    4. 允许安装高度[Hs]
    5. 防止汽蚀措施
    6. 温度影响分析

核心公式：
    1. 有效汽蚀余量：NPSHa = pa/(ρg) - Hs - hws - pv/(ρg)
    2. 必需汽蚀余量：(NPSH)r（由泵性能决定）
    3. 汽蚀安全裕度：K = NPSHa/(NPSH)r ≥ 1.3
    4. 允许安装高度：[Hs] = pa/(ρg) - (NPSH)r - hws - pv/(ρg)

考试要点：
    - NPSHa是系统特性（装置决定）
    - (NPSH)r是水泵特性（产品决定）
    - 必须NPSHa ≥ (NPSH)r
    - 建议安全系数K = 1.3~1.5
    - 降低安装高度、减少吸水损失

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CavitationAnalysis:
    """水泵汽蚀分析"""
    
    def __init__(self, Hs: float, Q: float, d: float, L: float, 
                 lambd: float, zeta: float, n: float,
                 pa: float, pv: float, NPSH_r: float):
        """
        初始化参数
        
        参数:
            Hs: 安装高度（泵轴高出水面）[m]
            Q: 流量 [m³/s]
            d: 吸水管直径 [m]
            L: 吸水管长度 [m]
            lambd: 沿程阻力系数
            zeta: 局部阻力系数之和
            n: 转速 [r/min]
            pa: 大气压 [kPa]
            pv: 饱和蒸汽压 [kPa]
            NPSH_r: 必需汽蚀余量 [m]
        """
        self.Hs = Hs
        self.Q = Q
        self.d = d
        self.L = L
        self.lambd = lambd
        self.zeta = zeta
        self.n = n
        self.pa = pa
        self.pv = pv
        self.NPSH_r = NPSH_r
        
        self.rho = 1000  # 水密度 [kg/m³]
        self.g = 9.8  # 重力加速度 [m/s²]
        
    def pipe_velocity(self) -> float:
        """吸水管流速"""
        A = np.pi * (self.d ** 2) / 4
        v = self.Q / A
        return v
    
    def head_loss_suction(self) -> Tuple[float, float, float]:
        """
        吸水管水头损失
        
        返回:
            hf: 沿程损失 [m]
            hm: 局部损失 [m]
            hws: 总损失 [m]
        """
        v = self.pipe_velocity()
        
        # 沿程损失
        hf = self.lambd * (self.L / self.d) * (v ** 2) / (2 * self.g)
        
        # 局部损失
        hm = self.zeta * (v ** 2) / (2 * self.g)
        
        # 总损失
        hws = hf + hm
        
        return hf, hm, hws
    
    def available_NPSH(self) -> float:
        """
        有效汽蚀余量 NPSHa
        
        NPSHa = pa/(ρg) - Hs - hws - pv/(ρg)
        """
        _, _, hws = self.head_loss_suction()
        
        ha = self.pa * 1000 / (self.rho * self.g)  # 大气压水头
        hv = self.pv * 1000 / (self.rho * self.g)  # 蒸汽压水头
        
        NPSHa = ha - self.Hs - hws - hv
        
        return NPSHa
    
    def cavitation_check(self) -> Tuple[bool, float]:
        """
        汽蚀校核
        
        返回:
            is_safe: 是否安全
            K: 安全系数
        """
        NPSHa = self.available_NPSH()
        K = NPSHa / self.NPSH_r
        is_safe = K >= 1.3  # 建议安全系数
        
        return is_safe, K
    
    def allowable_installation_height(self) -> float:
        """
        允许安装高度 [Hs]
        
        [Hs] = pa/(ρg) - (NPSH)r - hws - pv/(ρg)
        """
        _, _, hws = self.head_loss_suction()
        
        ha = self.pa * 1000 / (self.rho * self.g)
        hv = self.pv * 1000 / (self.rho * self.g)
        
        Hs_allow = ha - self.NPSH_r - hws - hv
        
        return Hs_allow
    
    def allowable_height_with_safety(self, K_design: float = 1.3) -> float:
        """
        考虑安全系数的允许安装高度
        
        [Hs] = pa/(ρg) - K×(NPSH)r - hws - pv/(ρg)
        """
        _, _, hws = self.head_loss_suction()
        
        ha = self.pa * 1000 / (self.rho * self.g)
        hv = self.pv * 1000 / (self.rho * self.g)
        
        Hs_allow = ha - K_design * self.NPSH_r - hws - hv
        
        return Hs_allow
    
    def temperature_effect(self, T_range: tuple = (0, 100)) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        温度对汽蚀的影响
        
        参数:
            T_range: 温度范围 [°C]
        
        返回:
            T: 温度数组
            pv_array: 饱和蒸汽压数组
            NPSHa_array: 有效汽蚀余量数组
        """
        T = np.linspace(T_range[0], T_range[1], 50)
        
        # 饱和蒸汽压经验公式（安托万方程简化）
        # log10(pv) = A - B/(T+C)，pv单位mmHg
        # 水的参数：A=8.07131, B=1730.63, C=233.426
        # 转换为kPa：1mmHg = 0.133322kPa
        
        pv_mmHg = 10 ** (8.07131 - 1730.63 / (T + 233.426))
        pv_array = pv_mmHg * 0.133322
        
        # 计算不同温度下的NPSHa
        _, _, hws = self.head_loss_suction()
        ha = self.pa * 1000 / (self.rho * self.g)
        hv_array = pv_array * 1000 / (self.rho * self.g)
        
        NPSHa_array = ha - self.Hs - hws - hv_array
        
        return T, pv_array, NPSHa_array
    
    def installation_height_analysis(self, Hs_range: tuple = (-2, 8)) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        安装高度影响分析
        
        参数:
            Hs_range: 安装高度范围 [m]
        
        返回:
            Hs_array: 安装高度数组
            NPSHa_array: 有效汽蚀余量数组
            K_array: 安全系数数组
        """
        Hs_array = np.linspace(Hs_range[0], Hs_range[1], 50)
        
        _, _, hws = self.head_loss_suction()
        ha = self.pa * 1000 / (self.rho * self.g)
        hv = self.pv * 1000 / (self.rho * self.g)
        
        NPSHa_array = ha - Hs_array - hws - hv
        K_array = NPSHa_array / self.NPSH_r
        
        return Hs_array, NPSHa_array, K_array
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算关键参数
        v = self.pipe_velocity()
        hf, hm, hws = self.head_loss_suction()
        NPSHa = self.available_NPSH()
        is_safe, K = self.cavitation_check()
        Hs_allow = self.allowable_installation_height()
        Hs_allow_safe = self.allowable_height_with_safety()
        
        ha = self.pa * 1000 / (self.rho * self.g)
        hv = self.pv * 1000 / (self.rho * self.g)
        
        # 1. 系统示意图
        ax1 = plt.subplot(3, 3, 1)
        ax1.axis('off')
        
        # 水池
        ax1.fill_between([0, 3], [-2, -2], [-4, -4], color='lightblue', alpha=0.5)
        ax1.plot([0, 3], [-2, -2], 'b-', linewidth=2)
        
        # 泵
        pump_x, pump_y = 3.5, self.Hs
        circle = plt.Circle((pump_x, pump_y), 0.4, color='gray', fill=True, alpha=0.7)
        ax1.add_patch(circle)
        ax1.text(pump_x, pump_y, '泵', ha='center', va='center', 
                fontsize=12, fontweight='bold', color='white')
        
        # 吸水管
        ax1.plot([1.5, 1.5, pump_x-0.4], [-2, pump_y, pump_y], 'k-', linewidth=3)
        ax1.arrow(1.5, -1, 0, 0.5, head_width=0.15, head_length=0.2, fc='red', ec='red')
        
        # 尺寸标注
        ax1.plot([0.5, 0.5], [-2, pump_y], 'k--', linewidth=1)
        ax1.annotate('', xy=(0.5, pump_y), xytext=(0.5, -2),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
        ax1.text(0.2, pump_y/2-1, f'Hs={self.Hs}m', fontsize=10, 
                color='red', fontweight='bold', rotation=90, va='center')
        
        # 水位线
        ax1.axhline(-2, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax1.text(0.1, -2.3, '水面', fontsize=9, color='blue')
        
        # 基准线
        ax1.axhline(0, color='black', linestyle=':', linewidth=1, alpha=0.3)
        
        ax1.set_xlim(-0.5, 5)
        ax1.set_ylim(-5, self.Hs+2)
        ax1.set_aspect('equal')
        ax1.set_title('系统示意图', fontsize=12, fontweight='bold')
        
        # 2. 吸水管损失分解
        ax2 = plt.subplot(3, 3, 2)
        
        losses = [hf, hm, hws]
        labels = ['沿程损失\nhf', '局部损失\nhm', '总损失\nhws']
        colors = ['lightcoral', 'lightsalmon', 'indianred']
        
        bars = ax2.bar(labels, losses, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('水头损失 (m)', fontsize=11)
        ax2.set_title('吸水管损失分解', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, losses):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.3f}m', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        
        # 3. 汽蚀余量计算
        ax3 = plt.subplot(3, 3, 3)
        
        # 构造计算流程
        components = ['大气压\n水头', '安装\n高度', '吸水\n损失', '蒸汽压\n水头', 'NPSHa']
        values = [ha, -self.Hs, -hws, -hv, NPSHa]
        colors_flow = ['lightgreen', 'lightcoral', 'lightsalmon', 'lightblue', 'gold']
        
        cumsum = np.cumsum([ha, -self.Hs, -hws, -hv])
        
        # 绘制瀑布图
        for i, (comp, val, col) in enumerate(zip(components[:-1], values[:-1], colors_flow[:-1])):
            if i == 0:
                ax3.bar(i, val, color=col, alpha=0.7, edgecolor='black')
                ax3.text(i, val/2, f'{val:.2f}m', ha='center', va='center',
                        fontsize=9, fontweight='bold')
            else:
                start = cumsum[i-1]
                ax3.bar(i, val, bottom=start, color=col, alpha=0.7, edgecolor='black')
                mid = start + val/2
                ax3.text(i, mid, f'{val:.2f}m', ha='center', va='center',
                        fontsize=9, fontweight='bold')
        
        # 最终NPSHa
        ax3.bar(len(components)-1, NPSHa, color=colors_flow[-1], 
               alpha=0.7, edgecolor='black', linewidth=2)
        ax3.text(len(components)-1, NPSHa/2, f'{NPSHa:.2f}m', 
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        ax3.set_xticks(range(len(components)))
        ax3.set_xticklabels(components, fontsize=9)
        ax3.set_ylabel('水头 (m)', fontsize=11)
        ax3.set_title('NPSHa计算流程', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.axhline(0, color='black', linewidth=1)
        
        # 4. 汽蚀校核
        ax4 = plt.subplot(3, 3, 4)
        
        x = [0, 1]
        y_npsha = [NPSHa, NPSHa]
        y_npshr = [self.NPSH_r, self.NPSH_r]
        
        ax4.fill_between(x, 0, y_npsha, alpha=0.3, color='green' if is_safe else 'red',
                        label=f'NPSHa={NPSHa:.2f}m')
        ax4.plot(x, y_npsha, 'g-', linewidth=3, label='有效汽蚀余量')
        ax4.plot(x, y_npshr, 'r--', linewidth=3, label=f'(NPSH)r={self.NPSH_r}m')
        
        # 安全余量
        if NPSHa > self.NPSH_r:
            ax4.fill_between(x, y_npshr, y_npsha, alpha=0.2, color='blue',
                           label=f'安全余量={NPSHa-self.NPSH_r:.2f}m')
        
        ax4.set_xlim(-0.2, 1.2)
        ax4.set_ylim(0, max(NPSHa, self.NPSH_r) * 1.3)
        ax4.set_ylabel('NPSH (m)', fontsize=11)
        ax4.set_title(f'汽蚀校核 (K={K:.2f}, {"✓安全" if is_safe else "✗不安全"})', 
                     fontsize=12, fontweight='bold',
                     color='green' if is_safe else 'red')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_xticks([])
        
        # 5. 安装高度影响
        ax5 = plt.subplot(3, 3, 5)
        
        Hs_arr, NPSHa_arr, K_arr = self.installation_height_analysis()
        
        ax5.plot(Hs_arr, NPSHa_arr, 'b-', linewidth=2, label='NPSHa')
        ax5.axhline(self.NPSH_r, color='r', linestyle='--', linewidth=2, label='(NPSH)r')
        ax5.axhline(1.3*self.NPSH_r, color='orange', linestyle=':', linewidth=2, label='1.3×(NPSH)r')
        
        # 当前点
        ax5.plot(self.Hs, NPSHa, 'go', markersize=12, label='当前工况')
        
        # 允许高度
        ax5.axvline(Hs_allow, color='green', linestyle='-.', linewidth=1.5, alpha=0.7)
        ax5.text(Hs_allow, ax5.get_ylim()[1]*0.9, f'[Hs]={Hs_allow:.2f}m', 
                ha='center', fontsize=9, color='green',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 安全高度
        ax5.axvline(Hs_allow_safe, color='orange', linestyle='-.', linewidth=1.5, alpha=0.7)
        ax5.text(Hs_allow_safe, ax5.get_ylim()[1]*0.8, f'[Hs](K=1.3)={Hs_allow_safe:.2f}m', 
                ha='center', fontsize=9, color='orange',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 安全区域
        safe_region = Hs_arr[NPSHa_arr >= 1.3*self.NPSH_r]
        if len(safe_region) > 0:
            ax5.axvspan(safe_region[0], safe_region[-1], alpha=0.1, color='green')
        
        ax5.set_xlabel('安装高度 Hs (m)', fontsize=11)
        ax5.set_ylabel('NPSH (m)', fontsize=11)
        ax5.set_title('安装高度影响分析', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 6. 安全系数变化
        ax6 = plt.subplot(3, 3, 6)
        
        ax6.plot(Hs_arr, K_arr, 'b-', linewidth=2, label='安全系数K')
        ax6.axhline(1.0, color='r', linestyle='--', linewidth=2, label='K=1.0 (临界)')
        ax6.axhline(1.3, color='orange', linestyle='--', linewidth=2, label='K=1.3 (推荐)')
        
        # 当前点
        ax6.plot(self.Hs, K, 'go', markersize=12, label=f'当前K={K:.2f}')
        
        # 安全区域
        safe_K = Hs_arr[K_arr >= 1.3]
        if len(safe_K) > 0:
            ax6.axvspan(safe_K[0], safe_K[-1], alpha=0.1, color='green', label='安全区')
        
        ax6.set_xlabel('安装高度 Hs (m)', fontsize=11)
        ax6.set_ylabel('安全系数 K', fontsize=11)
        ax6.set_title('安全系数变化', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=9)
        ax6.grid(True, alpha=0.3)
        ax6.set_ylim(0, max(K_arr)*1.1)
        
        # 7. 温度影响
        ax7 = plt.subplot(3, 3, 7)
        
        T, pv_arr, NPSHa_T = self.temperature_effect()
        
        ax7_twin = ax7.twinx()
        
        line1 = ax7.plot(T, pv_arr, 'r-', linewidth=2, label='饱和蒸汽压pv')
        line2 = ax7_twin.plot(T, NPSHa_T, 'b-', linewidth=2, label='NPSHa')
        ax7_twin.axhline(self.NPSH_r, color='orange', linestyle='--', linewidth=2, label='(NPSH)r')
        
        # 当前温度点（20°C）
        idx_20 = np.argmin(np.abs(T - 20))
        ax7.plot(20, pv_arr[idx_20], 'ro', markersize=10)
        ax7_twin.plot(20, NPSHa_T[idx_20], 'bo', markersize=10)
        
        ax7.set_xlabel('温度 T (°C)', fontsize=11)
        ax7.set_ylabel('饱和蒸汽压 pv (kPa)', fontsize=11, color='r')
        ax7_twin.set_ylabel('NPSHa (m)', fontsize=11, color='b')
        ax7.set_title('温度影响分析', fontsize=12, fontweight='bold')
        ax7.tick_params(axis='y', labelcolor='r')
        ax7_twin.tick_params(axis='y', labelcolor='b')
        ax7.grid(True, alpha=0.3)
        
        lines = line1 + line2 + [plt.Line2D([0], [0], color='orange', linestyle='--', linewidth=2)]
        labels = ['饱和蒸汽压pv', 'NPSHa', '(NPSH)r']
        ax7.legend(lines, labels, fontsize=9, loc='upper left')
        
        # 8. 防汽蚀措施
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        measures = [
            '【防止汽蚀的措施】',
            '',
            '1. 降低安装高度Hs',
            f'   当前: {self.Hs:.1f}m',
            f'   允许: {Hs_allow_safe:.1f}m (K=1.3)',
            f'   建议: ≤{Hs_allow_safe:.1f}m',
            '',
            '2. 减小吸水管损失hws',
            f'   当前: {hws:.3f}m',
            '   措施: 增大管径、缩短长度',
            '        减少弯头、阀门',
            '',
            '3. 改善水泵吸水条件',
            '   • 采用双吸泵（降低(NPSH)r）',
            '   • 前置诱导轮',
            '   • 提高泵性能',
            '',
            '4. 降低水温',
            '   • 避免高温抽水',
            '   • 采用冷却措施',
            '',
            '5. 提高吸水池水位',
        ]
        
        y_pos = 0.98
        for line in measures:
            if '【' in line:
                ax8.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                ax8.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax8.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.042
        
        ax8.set_title('防汽蚀措施', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 汽蚀分析结果 ═══',
            '',
            '【系统参数】',
            f'流量: Q = {self.Q:.2f} m³/s',
            f'转速: n = {self.n} r/min',
            f'安装高度: Hs = {self.Hs:.2f} m',
            f'管径: d = {self.d*1000:.0f} mm',
            '',
            '【吸水管损失】',
            f'流速: v = {v:.2f} m/s',
            f'沿程损失: hf = {hf:.3f} m',
            f'局部损失: hm = {hm:.3f} m',
            f'总损失: hws = {hws:.3f} m',
            '',
            '【汽蚀余量】',
            f'有效: NPSHa = {NPSHa:.2f} m',
            f'必需: (NPSH)r = {self.NPSH_r:.2f} m',
            f'安全系数: K = {K:.2f}',
            f'校核结果: {"✓安全" if is_safe else "✗不安全"}',
            '',
            '【允许高度】',
            f'理论: [Hs] = {Hs_allow:.2f} m',
            f'安全(K=1.3): {Hs_allow_safe:.2f} m',
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
            elif '✓' in line or '✗' in line:
                color = 'green' if '✓' in line else 'red'
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace', color=color, fontweight='bold')
            else:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.038
        
        ax9.set_title('结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch06_problem09_cavitation.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch06_problem09_cavitation.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第06章 水泵与水泵站 - 题9：水泵汽蚀分析与防护")
        print("="*70)
        
        # 基本参数
        print(f"\n【已知条件】")
        print(f"安装高度: Hs = {self.Hs} m")
        print(f"流量: Q = {self.Q} m³/s")
        print(f"转速: n = {self.n} r/min")
        print(f"吸水管直径: d = {self.d} m = {self.d*1000} mm")
        print(f"吸水管长度: L = {self.L} m")
        print(f"沿程阻力系数: λ = {self.lambd}")
        print(f"局部阻力系数: Σζ = {self.zeta}")
        print(f"大气压: pa = {self.pa} kPa")
        print(f"饱和蒸汽压: pv = {self.pv} kPa (20°C)")
        print(f"必需汽蚀余量: (NPSH)r = {self.NPSH_r} m")
        
        # (1) 吸水管水头损失
        print(f"\n【问题1】吸水管水头损失")
        
        v = self.pipe_velocity()
        hf, hm, hws = self.head_loss_suction()
        
        print(f"\n管道流速:")
        print(f"A = πd²/4 = π×{self.d}²/4 = {np.pi*(self.d**2)/4:.4f} m²")
        print(f"v = Q/A = {self.Q}/{np.pi*(self.d**2)/4:.4f} = {v:.3f} m/s")
        
        print(f"\n沿程损失:")
        print(f"hf = λ(L/d)(v²/2g)")
        print(f"   = {self.lambd}×({self.L}/{self.d})×({v:.3f}²/(2×{self.g}))")
        print(f"   = {hf:.4f} m")
        
        print(f"\n局部损失:")
        print(f"hm = Σζ(v²/2g)")
        print(f"   = {self.zeta}×({v:.3f}²/(2×{self.g}))")
        print(f"   = {hm:.4f} m")
        
        print(f"\n总损失:")
        print(f"hws = hf + hm = {hf:.4f} + {hm:.4f} = {hws:.4f} m")
        
        print(f"\n✓ 吸水管总损失: hws = {hws:.3f} m")
        
        # (2) 有效汽蚀余量
        print(f"\n【问题2】有效汽蚀余量NPSHa")
        
        ha = self.pa * 1000 / (self.rho * self.g)
        hv = self.pv * 1000 / (self.rho * self.g)
        NPSHa = self.available_NPSH()
        
        print(f"\n大气压水头:")
        print(f"ha = pa/(ρg) = {self.pa*1000}/({self.rho}×{self.g}) = {ha:.2f} m")
        
        print(f"\n蒸汽压水头:")
        print(f"hv = pv/(ρg) = {self.pv*1000}/({self.rho}×{self.g}) = {hv:.2f} m")
        
        print(f"\n有效汽蚀余量:")
        print(f"NPSHa = ha - Hs - hws - hv")
        print(f"      = {ha:.2f} - {self.Hs} - {hws:.3f} - {hv:.2f}")
        print(f"      = {NPSHa:.2f} m")
        
        print(f"\n✓ 有效汽蚀余量: NPSHa = {NPSHa:.2f} m")
        
        # (3) 汽蚀校核
        print(f"\n【问题3】汽蚀校核")
        
        is_safe, K = self.cavitation_check()
        
        print(f"\n安全系数:")
        print(f"K = NPSHa/(NPSH)r = {NPSHa:.2f}/{self.NPSH_r} = {K:.2f}")
        
        print(f"\n校核标准:")
        print(f"• K ≥ 1.0：不发生汽蚀（临界）")
        print(f"• K ≥ 1.3：安全运行（推荐）")
        
        print(f"\n校核结果:")
        print(f"NPSHa = {NPSHa:.2f} m {'>' if NPSHa > self.NPSH_r else '<'} (NPSH)r = {self.NPSH_r} m")
        print(f"K = {K:.2f} {'≥' if K >= 1.3 else '<'} 1.3")
        
        if is_safe:
            print(f"\n✓ 校核结论: 满足要求，安全系数充足")
        elif K >= 1.0:
            print(f"\n△ 校核结论: 不发生汽蚀，但安全裕度不足")
        else:
            print(f"\n✗ 校核结论: 会发生汽蚀，不满足要求")
        
        # (4) 允许安装高度
        print(f"\n【问题4】允许安装高度[Hs]")
        
        Hs_allow = self.allowable_installation_height()
        Hs_allow_safe = self.allowable_height_with_safety()
        
        print(f"\n理论允许高度:")
        print(f"[Hs] = ha - (NPSH)r - hws - hv")
        print(f"     = {ha:.2f} - {self.NPSH_r} - {hws:.3f} - {hv:.2f}")
        print(f"     = {Hs_allow:.2f} m")
        
        print(f"\n考虑安全系数(K=1.3):")
        print(f"[Hs] = ha - 1.3×(NPSH)r - hws - hv")
        print(f"     = {ha:.2f} - 1.3×{self.NPSH_r} - {hws:.3f} - {hv:.2f}")
        print(f"     = {Hs_allow_safe:.2f} m")
        
        print(f"\n✓ 理论允许高度: [Hs] = {Hs_allow:.2f} m")
        print(f"✓ 安全允许高度: [Hs] = {Hs_allow_safe:.2f} m (K=1.3)")
        
        print(f"\n当前安装:")
        if self.Hs <= Hs_allow_safe:
            print(f"Hs = {self.Hs} m ≤ {Hs_allow_safe:.2f} m，满足要求")
        elif self.Hs <= Hs_allow:
            print(f"{Hs_allow_safe:.2f} m < Hs = {self.Hs} m ≤ {Hs_allow:.2f} m，")
            print(f"理论满足，但安全裕度不足")
        else:
            print(f"Hs = {self.Hs} m > {Hs_allow:.2f} m，不满足要求")
        
        # (5) 防止汽蚀措施
        print(f"\n【问题5】防止汽蚀的措施")
        
        print(f"\n1. 降低安装高度Hs")
        print(f"   • 将泵安装在较低位置")
        print(f"   • 当前{self.Hs}m → 建议≤{Hs_allow_safe:.2f}m")
        print(f"   • 降低{self.Hs-Hs_allow_safe:.2f}m可提高安全性")
        
        print(f"\n2. 减小吸水管路损失hws")
        print(f"   • 增大管径（当前{self.d*1000:.0f}mm）")
        print(f"   • 缩短管长（当前{self.L}m）")
        print(f"   • 减少弯头、阀门等局部阻力")
        print(f"   • 采用流线型进口")
        
        print(f"\n3. 改善水泵吸水性能")
        print(f"   • 选用汽蚀性能好的泵（低(NPSH)r）")
        print(f"   • 采用双吸泵")
        print(f"   • 加装前置诱导轮")
        
        print(f"\n4. 改善吸水条件")
        print(f"   • 提高吸水池水位")
        print(f"   • 降低水温（降低pv）")
        print(f"   • 避免高温季节运行")
        
        print(f"\n5. 运行维护")
        print(f"   • 及时排除吸水管内空气")
        print(f"   • 保持叶轮光洁")
        print(f"   • 避免流量过大")
        
        # (6) 温度影响
        print(f"\n【问题6】温度影响分析")
        
        print(f"\n温度对汽蚀的影响:")
        print(f"• 温度↑ → 饱和蒸汽压pv↑ → 蒸汽压水头hv↑")
        print(f"• NPSHa = ha - Hs - hws - hv")
        print(f"• 温度↑ → hv↑ → NPSHa↓ → 更易汽蚀")
        
        T_arr = [0, 10, 20, 30, 40, 50, 60, 80, 100]
        print(f"\n不同温度下的饱和蒸汽压:")
        print(f"{'温度(°C)':<10} {'pv(kPa)':<12} {'hv(m)':<12} {'NPSHa(m)':<12}")
        print(f"{'-'*50}")
        for T in T_arr:
            pv_mmHg = 10 ** (8.07131 - 1730.63 / (T + 233.426))
            pv_kPa = pv_mmHg * 0.133322
            hv_calc = pv_kPa * 1000 / (self.rho * self.g)
            NPSHa_calc = ha - self.Hs - hws - hv_calc
            print(f"{T:<10} {pv_kPa:<12.2f} {hv_calc:<12.2f} {NPSHa_calc:<12.2f}")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. NPSHa = pa/(ρg) - Hs - hws - pv/(ρg)（系统特性）")
        print(f"2. (NPSH)r 由水泵性能决定（产品特性）")
        print(f"3. 汽蚀条件: NPSHa ≥ (NPSH)r")
        print(f"4. 安全系数: K = NPSHa/(NPSH)r ≥ 1.3")
        print(f"5. [Hs] = pa/(ρg) - (NPSH)r - hws - pv/(ρg)")
        print(f"6. 温度↑、Hs↑、hws↑ → 易汽蚀")
        print(f"7. 防汽蚀: 降Hs、减hws、降T、选好泵")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("水泵汽蚀分析与防护")
    print("-" * 70)
    
    # 系统参数
    Hs = 4.5  # 安装高度 [m]
    Q = 0.2  # 流量 [m³/s]
    d = 0.3  # 吸水管直径 [m]
    L = 15  # 吸水管长度 [m]
    lambd = 0.025  # 沿程阻力系数
    zeta = 5.0  # 局部阻力系数
    n = 1450  # 转速 [r/min]
    pa = 101.3  # 大气压 [kPa]
    pv = 2.34  # 饱和蒸汽压(20°C) [kPa]
    NPSH_r = 3.5  # 必需汽蚀余量 [m]
    
    # 创建分析实例
    cav = CavitationAnalysis(Hs, Q, d, L, lambd, zeta, n, pa, pv, NPSH_r)
    
    # 打印结果
    cav.print_results()
    
    # 绘制分析图
    cav.plot_analysis()


if __name__ == "__main__":
    main()
