# -*- coding: utf-8 -*-
"""
第06章 水泵与水泵站 - 题6：水泵并联和串联运行

问题描述：
    某水泵站有两台相同型号的离心泵，单泵性能曲线为：
    H = 60 - 1000Q²（H单位m，Q单位m³/s）
    管路特性曲线为：H_管 = 20 + 500Q²
    
    求：
    1. 单泵运行工况点
    2. 两泵并联运行工况点
    3. 两泵串联运行工况点
    4. 对比分析
    5. 适用场合
    6. 功率计算（η = 0.75）

核心公式：
    1. 并联：Q并 = Q1 + Q2（相同扬程）
    2. 串联：H串 = H1 + H2（相同流量）
    3. 并联特性：H = H0 - k(Q/n)²
    4. 串联特性：H = n(H0 - kQ²)

考试要点：
    - 并联增加流量，串联增加扬程
    - 并联适用于低扬程大流量场合
    - 串联适用于高扬程小流量场合
    - 并联/串联效果不是简单的倍数关系

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SeriesParallelPumps:
    """水泵并联和串联运行分析"""
    
    def __init__(self, H0: float, k_pump: float, Hst: float, r_pipe: float, eta: float = 0.75):
        """
        初始化参数
        
        参数:
            H0: 单泵零流量扬程 [m]
            k_pump: 单泵特性系数
            Hst: 静扬程 [m]
            r_pipe: 管路阻力系数
            eta: 水泵效率
        """
        self.H0 = H0
        self.k_pump = k_pump
        self.Hst = Hst
        self.r_pipe = r_pipe
        self.eta = eta
        self.rho = 1000  # 水密度 [kg/m³]
        self.g = 9.8  # 重力加速度 [m/s²]
        
    def pump_curve(self, Q: np.ndarray) -> np.ndarray:
        """单泵特性曲线：H = H0 - kQ²"""
        H = self.H0 - self.k_pump * (Q ** 2)
        return H
    
    def pipe_curve(self, Q: np.ndarray) -> np.ndarray:
        """管路特性曲线：H = Hst + rQ²"""
        H = self.Hst + self.r_pipe * (Q ** 2)
        return H
    
    def find_single_pump_point(self) -> Tuple[float, float]:
        """单泵工况点"""
        Q = np.sqrt((self.H0 - self.Hst) / (self.k_pump + self.r_pipe))
        H = self.pump_curve(Q)
        return Q, H
    
    def parallel_pump_curve(self, Q: np.ndarray, n: int = 2) -> np.ndarray:
        """
        并联水泵特性曲线
        
        并联：相同扬程，流量相加
        Q总 = n·Q单
        H = H0 - k(Q/n)²
        """
        Q_single = Q / n
        H = self.pump_curve(Q_single)
        return H
    
    def find_parallel_point(self, n: int = 2) -> Tuple[float, float, float]:
        """
        并联工况点
        
        返回:
            Q_total: 总流量
            H: 扬程
            Q_single: 单泵流量
        """
        Q_total = np.sqrt((self.H0 - self.Hst) / (self.k_pump / (n**2) + self.r_pipe))
        H = self.pipe_curve(Q_total)
        Q_single = Q_total / n
        return Q_total, H, Q_single
    
    def series_pump_curve(self, Q: np.ndarray, n: int = 2) -> np.ndarray:
        """
        串联水泵特性曲线
        
        串联：相同流量，扬程相加
        H总 = n·H单
        H = n(H0 - kQ²)
        """
        H_single = self.pump_curve(Q)
        H_total = n * H_single
        return H_total
    
    def find_series_point(self, n: int = 2) -> Tuple[float, float]:
        """
        串联工况点
        
        返回:
            Q: 流量
            H: 总扬程
        """
        Q = np.sqrt((n * self.H0 - self.Hst) / (n * self.k_pump + self.r_pipe))
        H = self.pipe_curve(Q)
        return Q, H
    
    def calculate_power(self, Q: float, H: float, n_pumps: int = 1) -> Tuple[float, float]:
        """
        计算功率
        
        参数:
            Q: 流量 [m³/s]
            H: 扬程 [m]
            n_pumps: 水泵台数
        
        返回:
            Ne: 有效功率 [kW]
            N: 轴功率 [kW]
        """
        Ne = self.rho * self.g * Q * H / 1000  # kW
        N = Ne / self.eta * n_pumps  # 总轴功率
        return Ne, N
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算工况点
        Q_s, H_s = self.find_single_pump_point()
        Q_p, H_p, Q_ps = self.find_parallel_point()
        Q_ser, H_ser = self.find_series_point()
        
        # 流量范围
        Q_range = np.linspace(0, 0.3, 200)
        
        # 1. 单泵工况点
        ax1 = plt.subplot(3, 3, 1)
        H_pump = self.pump_curve(Q_range)
        H_pipe = self.pipe_curve(Q_range)
        
        ax1.plot(Q_range*1000, H_pump, 'b-', linewidth=2, label='单泵特性')
        ax1.plot(Q_range*1000, H_pipe, 'r-', linewidth=2, label='管路特性')
        ax1.plot(Q_s*1000, H_s, 'go', markersize=12, 
                label=f'工况点({Q_s*1000:.1f}L/s, {H_s:.1f}m)')
        
        ax1.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax1.set_ylabel('扬程 H (m)', fontsize=11)
        ax1.set_title('单泵运行工况点', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=9)
        ax1.set_xlim(0, 300)
        ax1.set_ylim(0, 80)
        
        # 2. 并联工况点
        ax2 = plt.subplot(3, 3, 2)
        H_parallel = self.parallel_pump_curve(Q_range, n=2)
        
        ax2.plot(Q_range*1000, H_pump, 'b-', linewidth=2, label='单泵特性')
        ax2.plot(Q_range*1000, H_parallel, 'b--', linewidth=2, label='并联特性')
        ax2.plot(Q_range*1000, H_pipe, 'r-', linewidth=2, label='管路特性')
        ax2.plot(Q_s*1000, H_s, 'go', markersize=10, label='单泵工况')
        ax2.plot(Q_p*1000, H_p, 'mo', markersize=12, label=f'并联工况')
        
        # 标注单泵分担
        ax2.axvline(Q_ps*1000, color='purple', linestyle=':', alpha=0.5)
        ax2.text(Q_ps*1000, 5, f'单泵分担\n{Q_ps*1000:.0f}L/s', 
                ha='center', fontsize=9, color='purple',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        ax2.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax2.set_ylabel('扬程 H (m)', fontsize=11)
        ax2.set_title('并联运行工况点', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=9)
        ax2.set_xlim(0, 300)
        ax2.set_ylim(0, 80)
        
        # 3. 串联工况点
        ax3 = plt.subplot(3, 3, 3)
        H_series = self.series_pump_curve(Q_range, n=2)
        
        ax3.plot(Q_range*1000, H_pump, 'b-', linewidth=2, label='单泵特性')
        ax3.plot(Q_range*1000, H_series, 'b:', linewidth=2, label='串联特性')
        ax3.plot(Q_range*1000, H_pipe, 'r-', linewidth=2, label='管路特性')
        ax3.plot(Q_s*1000, H_s, 'go', markersize=10, label='单泵工况')
        ax3.plot(Q_ser*1000, H_ser, 'co', markersize=12, label=f'串联工况')
        
        ax3.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax3.set_ylabel('扬程 H (m)', fontsize=11)
        ax3.set_title('串联运行工况点', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend(fontsize=9)
        ax3.set_xlim(0, 300)
        ax3.set_ylim(0, 140)
        
        # 4. 三种工况对比
        ax4 = plt.subplot(3, 3, 4)
        ax4.plot(Q_range*1000, H_pump, 'b-', linewidth=2, label='单泵特性')
        ax4.plot(Q_range*1000, H_parallel, 'b--', linewidth=2, label='并联特性')
        ax4.plot(Q_range*1000, H_series, 'b:', linewidth=3, label='串联特性')
        ax4.plot(Q_range*1000, H_pipe, 'r-', linewidth=2, label='管路特性')
        
        ax4.plot(Q_s*1000, H_s, 'go', markersize=12, label='单泵')
        ax4.plot(Q_p*1000, H_p, 'mo', markersize=12, label='并联')
        ax4.plot(Q_ser*1000, H_ser, 'co', markersize=12, label='串联')
        
        ax4.set_xlabel('流量 Q (L/s)', fontsize=11)
        ax4.set_ylabel('扬程 H (m)', fontsize=11)
        ax4.set_title('三种工况综合对比', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=9, ncol=2)
        ax4.set_xlim(0, 300)
        ax4.set_ylim(0, 140)
        
        # 5. 流量对比
        ax5 = plt.subplot(3, 3, 5)
        cases = ['单泵', '并联', '串联']
        flows = [Q_s*1000, Q_p*1000, Q_ser*1000]
        colors = ['green', 'magenta', 'cyan']
        
        bars = ax5.bar(cases, flows, color=colors, alpha=0.7, edgecolor='black')
        ax5.set_ylabel('流量 (L/s)', fontsize=11)
        ax5.set_title('流量对比', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, flows):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
            # 标注增幅
            if val != Q_s*1000:
                ratio = (val / (Q_s*1000) - 1) * 100
                ax5.text(bar.get_x() + bar.get_width()/2, height/2,
                        f'{ratio:+.0f}%', ha='center', va='center',
                        fontsize=9, color='red', fontweight='bold')
        
        # 6. 扬程对比
        ax6 = plt.subplot(3, 3, 6)
        heads = [H_s, H_p, H_ser]
        bars = ax6.bar(cases, heads, color=colors, alpha=0.7, edgecolor='black')
        ax6.set_ylabel('扬程 (m)', fontsize=11)
        ax6.set_title('扬程对比', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, heads):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
            # 标注增幅
            if val != H_s:
                ratio = (val / H_s - 1) * 100
                ax6.text(bar.get_x() + bar.get_width()/2, height/2,
                        f'{ratio:+.0f}%', ha='center', va='center',
                        fontsize=9, color='red', fontweight='bold')
        
        # 7. 功率对比
        ax7 = plt.subplot(3, 3, 7)
        
        Ne_s, N_s = self.calculate_power(Q_s, H_s, 1)
        Ne_p, N_p = self.calculate_power(Q_p, H_p, 2)
        Ne_ser, N_ser = self.calculate_power(Q_ser, H_ser, 2)
        
        x = np.arange(3)
        width = 0.35
        
        Ne_vals = [Ne_s, Ne_p, Ne_ser]
        N_vals = [N_s, N_p, N_ser]
        
        bars1 = ax7.bar(x - width/2, Ne_vals, width, label='有效功率Ne',
                       color='lightgreen', alpha=0.7, edgecolor='black')
        bars2 = ax7.bar(x + width/2, N_vals, width, label='轴功率N',
                       color='lightcoral', alpha=0.7, edgecolor='black')
        
        ax7.set_ylabel('功率 (kW)', fontsize=11)
        ax7.set_title('功率对比', fontsize=12, fontweight='bold')
        ax7.set_xticks(x)
        ax7.set_xticklabels(cases)
        ax7.legend()
        ax7.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax7.text(bar.get_x() + bar.get_width()/2, height,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 8. 对比表
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        data = [
            ['项目', '单泵', '并联(×2)', '串联(×2)'],
            ['流量(L/s)', f'{Q_s*1000:.1f}', f'{Q_p*1000:.1f}', f'{Q_ser*1000:.1f}'],
            ['增幅', '-', f'+{(Q_p/Q_s-1)*100:.0f}%', f'+{(Q_ser/Q_s-1)*100:.0f}%'],
            ['扬程(m)', f'{H_s:.1f}', f'{H_p:.1f}', f'{H_ser:.1f}'],
            ['增幅', '-', f'+{(H_p/H_s-1)*100:.0f}%', f'+{(H_ser/H_s-1)*100:.0f}%'],
            ['单泵Q(L/s)', f'{Q_s*1000:.1f}', f'{Q_ps*1000:.1f}', f'{Q_ser*1000:.1f}'],
            ['轴功率(kW)', f'{N_s:.1f}', f'{N_p:.1f}', f'{N_ser:.1f}'],
        ]
        
        table = ax8.table(cellText=data, loc='center', cellLoc='center',
                         colWidths=[0.3, 0.23, 0.23, 0.23])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # 设置表头样式
        for i in range(4):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax8.set_title('性能对比表', fontsize=12, fontweight='bold', pad=20)
        
        # 9. 结果汇总与适用场合
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 运行方式对比 ═══',
            '',
            '【单泵运行】',
            f'Q = {Q_s*1000:.1f} L/s, H = {H_s:.1f} m',
            f'N = {N_s:.1f} kW',
            '',
            '【并联运行(2台)】',
            f'Q = {Q_p*1000:.1f} L/s (+{(Q_p/Q_s-1)*100:.0f}%)',
            f'H = {H_p:.1f} m (+{(H_p/H_s-1)*100:.0f}%)',
            f'单泵: {Q_ps*1000:.0f} L/s',
            f'N = {N_p:.1f} kW',
            '适用：增大流量，低扬程',
            '',
            '【串联运行(2台)】',
            f'Q = {Q_ser*1000:.1f} L/s (+{(Q_ser/Q_s-1)*100:.0f}%)',
            f'H = {H_ser:.1f} m (+{(H_ser/H_s-1)*100:.0f}%)',
            f'N = {N_ser:.1f} kW',
            '适用：增大扬程，小流量',
            '',
            '【选择原则】',
            '• 并联：扁平管路（阻力大）',
            '• 串联：陡峭管路（扬程高）',
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
            elif '适用' in line or '选择' in line:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        color='darkgreen', fontweight='bold')
            else:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.042
        
        ax9.set_title('结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch06_problem06_series_parallel.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch06_problem06_series_parallel.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第06章 水泵与水泵站 - 题6：水泵并联和串联运行")
        print("="*70)
        
        # 基本参数
        print(f"\n【系统参数】")
        print(f"单泵特性: H = {self.H0} - {self.k_pump}Q²")
        print(f"管路特性: H = {self.Hst} + {self.r_pipe}Q²")
        print(f"水泵效率: η = {self.eta}")
        
        # (1) 单泵工况点
        print(f"\n【问题1】单泵运行工况点")
        Q_s, H_s = self.find_single_pump_point()
        
        print(f"\n工况点方程:")
        print(f"{self.H0} - {self.k_pump}Q² = {self.Hst} + {self.r_pipe}Q²")
        print(f"Q² = {(self.H0-self.Hst)/(self.k_pump+self.r_pipe):.6f}")
        print(f"Q = {Q_s:.4f} m³/s = {Q_s*1000:.1f} L/s")
        print(f"H = {H_s:.2f} m")
        
        print(f"\n✓ 单泵工况点: Q = {Q_s*1000:.1f} L/s, H = {H_s:.1f} m")
        
        # (2) 并联工况点
        print(f"\n【问题2】两泵并联运行工况点")
        Q_p, H_p, Q_ps = self.find_parallel_point()
        
        print(f"\n并联特性（相同扬程，流量相加）:")
        print(f"Q总 = 2Q单")
        print(f"H = {self.H0} - {self.k_pump}(Q/2)²")
        print(f"H = {self.H0} - {self.k_pump/4}Q²")
        
        print(f"\n并联工况点:")
        print(f"{self.H0} - {self.k_pump/4}Q² = {self.Hst} + {self.r_pipe}Q²")
        print(f"Q = {Q_p:.4f} m³/s = {Q_p*1000:.1f} L/s")
        print(f"H = {H_p:.2f} m")
        print(f"单泵分担: {Q_ps:.4f} m³/s = {Q_ps*1000:.1f} L/s")
        
        print(f"\n✓ 并联工况点: Q = {Q_p*1000:.1f} L/s, H = {H_p:.1f} m")
        print(f"✓ 单泵流量: {Q_ps*1000:.1f} L/s")
        
        # (3) 串联工况点
        print(f"\n【问题3】两泵串联运行工况点")
        Q_ser, H_ser = self.find_series_point()
        
        print(f"\n串联特性（相同流量，扬程相加）:")
        print(f"H总 = 2H单")
        print(f"H = 2({self.H0} - {self.k_pump}Q²)")
        print(f"H = {2*self.H0} - {2*self.k_pump}Q²")
        
        print(f"\n串联工况点:")
        print(f"{2*self.H0} - {2*self.k_pump}Q² = {self.Hst} + {self.r_pipe}Q²")
        print(f"Q = {Q_ser:.4f} m³/s = {Q_ser*1000:.1f} L/s")
        print(f"H = {H_ser:.2f} m")
        
        print(f"\n✓ 串联工况点: Q = {Q_ser*1000:.1f} L/s, H = {H_ser:.1f} m")
        
        # (4) 对比分析
        print(f"\n【问题4】对比分析")
        
        print(f"\n流量对比:")
        print(f"单泵: {Q_s*1000:.1f} L/s (基准)")
        print(f"并联: {Q_p*1000:.1f} L/s (增幅{(Q_p/Q_s-1)*100:+.1f}%)")
        print(f"串联: {Q_ser*1000:.1f} L/s (增幅{(Q_ser/Q_s-1)*100:+.1f}%)")
        
        print(f"\n扬程对比:")
        print(f"单泵: {H_s:.1f} m (基准)")
        print(f"并联: {H_p:.1f} m (增幅{(H_p/H_s-1)*100:+.1f}%)")
        print(f"串联: {H_ser:.1f} m (增幅{(H_ser/H_s-1)*100:+.1f}%)")
        
        print(f"\n关键结论:")
        print(f"• 并联：流量增大{(Q_p/Q_s-1)*100:.0f}%，扬程增大{(H_p/H_s-1)*100:.0f}%")
        print(f"• 串联：流量增大{(Q_ser/Q_s-1)*100:.0f}%，扬程增大{(H_ser/H_s-1)*100:.0f}%")
        print(f"• 并联主要增流量，串联主要增扬程")
        
        # (5) 适用场合
        print(f"\n【问题5】适用场合")
        
        print(f"\n并联运行适用场合:")
        print(f"1. 低扬程、大流量场合（如平原灌溉）")
        print(f"2. 管路阻力系数大（扁平特性）")
        print(f"3. 需要灵活调节流量")
        print(f"4. 需要备用或检修")
        
        print(f"\n串联运行适用场合:")
        print(f"1. 高扬程、小流量场合（如高层供水）")
        print(f"2. 管路阻力系数小（陡峭特性）")
        print(f"3. 单泵扬程不足")
        print(f"4. 多级泵站")
        
        # (6) 功率计算
        print(f"\n【问题6】功率计算（η = {self.eta}）")
        
        Ne_s, N_s = self.calculate_power(Q_s, H_s, 1)
        Ne_p, N_p = self.calculate_power(Q_p, H_p, 2)
        Ne_ser, N_ser = self.calculate_power(Q_ser, H_ser, 2)
        
        print(f"\n单泵运行:")
        print(f"有效功率: Ne = ρgQH = {self.rho}×{self.g}×{Q_s:.4f}×{H_s:.1f}/1000 = {Ne_s:.2f} kW")
        print(f"轴功率: N = Ne/η = {Ne_s:.2f}/{self.eta} = {N_s:.2f} kW")
        
        print(f"\n并联运行:")
        print(f"有效功率: Ne = {Ne_p:.2f} kW")
        print(f"总轴功率: N = 2×Ne/η = {N_p:.2f} kW")
        print(f"单泵功率: {N_p/2:.2f} kW")
        
        print(f"\n串联运行:")
        print(f"有效功率: Ne = {Ne_ser:.2f} kW")
        print(f"总轴功率: N = 2×Ne/η = {N_ser:.2f} kW")
        print(f"单泵功率: {N_ser/2:.2f} kW")
        
        # 对比表
        print(f"\n【性能对比表】")
        print(f"{'项目':<12} {'单泵':>12} {'并联':>12} {'串联':>12}")
        print(f"{'-'*52}")
        print(f"{'流量(L/s)':<12} {Q_s*1000:>12.1f} {Q_p*1000:>12.1f} {Q_ser*1000:>12.1f}")
        print(f"{'扬程(m)':<12} {H_s:>12.1f} {H_p:>12.1f} {H_ser:>12.1f}")
        print(f"{'单泵Q(L/s)':<12} {Q_s*1000:>12.1f} {Q_ps*1000:>12.1f} {Q_ser*1000:>12.1f}")
        print(f"{'有效功率(kW)':<12} {Ne_s:>12.1f} {Ne_p:>12.1f} {Ne_ser:>12.1f}")
        print(f"{'轴功率(kW)':<12} {N_s:>12.1f} {N_p:>12.1f} {N_ser:>12.1f}")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 并联：Q并 = Q1 + Q2（相同H）")
        print(f"2. 串联：H串 = H1 + H2（相同Q）")
        print(f"3. 并联特性：H = H0 - k(Q/n)²")
        print(f"4. 串联特性：H = n(H0 - kQ²)")
        print(f"5. 并联增流量，串联增扬程")
        print(f"6. 效果不是台数倍（受管路影响）")
        print(f"7. 选择依据：管路特性、需求")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("水泵并联和串联运行分析")
    print("-" * 70)
    
    # 系统参数
    H0 = 60  # 单泵零流量扬程 [m]
    k_pump = 1000  # 单泵特性系数
    Hst = 20  # 静扬程 [m]
    r_pipe = 500  # 管路阻力系数
    eta = 0.75  # 水泵效率
    
    # 创建分析实例
    sp = SeriesParallelPumps(H0, k_pump, Hst, r_pipe, eta)
    
    # 打印结果
    sp.print_results()
    
    # 绘制分析图
    sp.plot_analysis()


if __name__ == "__main__":
    main()
