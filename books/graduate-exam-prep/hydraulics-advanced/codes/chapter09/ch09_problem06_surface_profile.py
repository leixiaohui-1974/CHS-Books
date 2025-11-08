# -*- coding: utf-8 -*-
"""
第09章 渠系水力计算 - 题6：非均匀流水面曲线

问题描述：
    矩形断面渠道，b = 5m，n = 0.025，Q = 20 m³/s
    底坡从i1 = 0.001变化到i2 = 0.0005（变坡段）
    
    求：
    1. 正常水深h0（上下游）
    2. 临界水深hc
    3. 水面曲线类型判别
    4. 水面曲线计算（逐段求和法）
    5. 壅水分析
    
核心公式：
    1. 正常水深：Q = A·(1/n)R^(2/3)i^(1/2)
    2. 临界水深：Fr = 1, hc = (Q²/(gb²))^(1/3)
    3. 水面曲线方程：dh/dx = (i - J)/(1 - Fr²)
    4. 壅水高度：Δh = h - h0

考试要点：
    - 水面曲线分类（12种）
    - 临界水深与正常水深比较
    - 逐段求和法应用
    - 壅水现象分析

作者: CHS-Books Team  
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from typing import Tuple, List

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SurfaceProfile:
    """非均匀流水面曲线"""
    
    def __init__(self, b: float, n: float, Q: float, i1: float, i2: float):
        self.b = b
        self.n = n
        self.Q = Q
        self.i1 = i1  # 上游底坡
        self.i2 = i2  # 下游底坡
        self.g = 9.8
        
    def normal_depth(self, i: float) -> float:
        """正常水深"""
        def equation(h):
            A = self.b * h
            chi = self.b + 2 * h
            R = A / chi
            v = (1 / self.n) * (R ** (2/3)) * (i ** 0.5)
            return A * v - self.Q
        
        h0 = fsolve(equation, 1.0)[0]
        return h0
    
    def critical_depth(self) -> float:
        """临界水深"""
        hc = (self.Q**2 / (self.g * self.b**2)) ** (1/3)
        return hc
    
    def froude_number(self, h: float) -> float:
        """Froude数"""
        A = self.b * h
        v = self.Q / A
        hm = A / self.b  # 平均水深
        Fr = v / np.sqrt(self.g * hm)
        return Fr
    
    def energy_slope(self, h: float) -> float:
        """能坡J"""
        A = self.b * h
        chi = self.b + 2 * h
        R = A / chi
        v = self.Q / A
        J = (self.n * v)**2 / (R ** (4/3))
        return J
    
    def profile_type(self, h: float, h0: float, hc: float) -> str:
        """水面曲线类型判别"""
        if h > h0 and h > hc:
            return "M1-壅水曲线"
        elif h0 > h > hc:
            return "M2-降水曲线"
        elif h < hc and h < h0:
            return "M3-降水曲线"
        elif h > hc > h0:
            return "S1-壅水曲线"
        elif hc > h > h0:
            return "S2-降水曲线"
        elif h < h0 and h < hc:
            return "S3-降水曲线"
        else:
            return "临界流"
    
    def compute_profile(self, h_start: float, L: float, dx: float, i: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        水面曲线计算（逐段求和法）
        dh/dx = (i - J) / (1 - Fr²)
        """
        n_steps = int(L / dx)
        x = np.zeros(n_steps)
        h = np.zeros(n_steps)
        
        h[0] = h_start
        x[0] = 0
        
        for j in range(1, n_steps):
            h_current = h[j-1]
            
            # 计算能坡和Fr数
            J = self.energy_slope(h_current)
            Fr = self.froude_number(h_current)
            
            # 水面曲线微分方程
            if abs(1 - Fr**2) < 0.01:  # 接近临界流
                dh_dx = 0
            else:
                dh_dx = (i - J) / (1 - Fr**2)
            
            # 更新
            h[j] = h_current + dh_dx * dx
            x[j] = x[j-1] + dx
            
            # 检查物理合理性
            if h[j] < 0.1 or h[j] > 10:
                h = h[:j]
                x = x[:j]
                break
        
        return x, h
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算关键水深
        h01 = self.normal_depth(self.i1)
        h02 = self.normal_depth(self.i2)
        hc = self.critical_depth()
        
        # 1. 断面示意图
        ax1 = plt.subplot(3, 3, 1)
        
        # 绘制矩形断面
        x_rect = np.array([0, self.b, self.b, 0, 0])
        y_rect = np.array([0, 0, h01, h01, 0])
        
        ax1.fill(x_rect, y_rect, color='lightblue', alpha=0.5, label='水体')
        ax1.plot(x_rect, y_rect, 'k-', linewidth=2)
        
        ax1.text(self.b/2, -0.2, f'b={self.b}m', ha='center', fontsize=10, color='red', fontweight='bold')
        ax1.text(self.b+0.3, h01/2, f'h₀={h01:.2f}m', fontsize=10, color='red', fontweight='bold')
        ax1.axhline(hc, color='green', linestyle='--', linewidth=2, label=f'hc={hc:.2f}m')
        
        ax1.set_xlim(-0.5, self.b+1)
        ax1.set_ylim(-0.5, h01+0.5)
        ax1.set_aspect('equal')
        ax1.set_title('断面示意图', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 关键水深比较
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.9, '关键水深计算', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.75, f'上游正常水深: h₀₁ = {h01:.3f} m', fontsize=10)
        ax2.text(0.1, 0.65, f'下游正常水深: h₀₂ = {h02:.3f} m', fontsize=10)
        ax2.text(0.1, 0.55, f'临界水深: hc = {hc:.3f} m', fontsize=10, color='green', fontweight='bold')
        ax2.text(0.1, 0.40, f'上游Fr: {self.froude_number(h01):.3f} ({"缓流" if self.froude_number(h01)<1 else "急流"})', fontsize=10)
        ax2.text(0.1, 0.30, f'下游Fr: {self.froude_number(h02):.3f} ({"缓流" if self.froude_number(h02)<1 else "急流"})', fontsize=10)
        
        # 坡度类型判别
        if h01 > hc:
            slope_type1 = "缓坡"
        elif h01 < hc:
            slope_type1 = "陡坡"
        else:
            slope_type1 = "临界坡"
        
        ax2.text(0.1, 0.15, f'上游坡度类型: {slope_type1}', fontsize=10, color='blue', fontweight='bold')
        ax2.text(0.1, 0.05, f'i₁={self.i1}, i₂={self.i2}', fontsize=9)
        
        ax2.set_title('水深分析', fontsize=12, fontweight='bold')
        
        # 3. 水面曲线（上游段）
        ax3 = plt.subplot(3, 3, 3)
        
        L1 = 500  # 上游段长度
        h_start1 = h01 + 0.5  # 起始水深（壅水）
        x1, h1 = self.compute_profile(h_start1, L1, dx=5, i=self.i1)
        
        ax3.plot(x1, h1, 'b-', linewidth=2, label='实际水面')
        ax3.axhline(h01, color='red', linestyle='--', linewidth=1.5, label=f'正常水深={h01:.2f}m')
        ax3.axhline(hc, color='green', linestyle='--', linewidth=1.5, label=f'临界水深={hc:.2f}m')
        ax3.fill_between(x1, 0, h1, alpha=0.2, color='lightblue')
        
        ax3.set_xlabel('距离 x (m)', fontsize=10)
        ax3.set_ylabel('水深 h (m)', fontsize=10)
        ax3.set_title('上游水面曲线', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 底坡变化示意
        ax4 = plt.subplot(3, 3, 4)
        
        x_profile = np.array([0, 500, 500, 1000])
        z_profile = np.array([10, 10-500*self.i1, 10-500*self.i1, 10-500*self.i1-500*self.i2])
        
        ax4.plot(x_profile, z_profile, 'k-', linewidth=2, label='渠底')
        ax4.fill_between(x_profile, z_profile, z_profile.min()-1, alpha=0.2, color='brown')
        
        # 标注坡度
        ax4.text(250, z_profile[0]-0.3, f'i₁={self.i1}', fontsize=10, ha='center', color='red', fontweight='bold')
        ax4.text(750, z_profile[2]-0.3, f'i₂={self.i2}', fontsize=10, ha='center', color='blue', fontweight='bold')
        
        ax4.set_xlabel('距离 (m)', fontsize=10)
        ax4.set_ylabel('高程 (m)', fontsize=10)
        ax4.set_title('底坡变化示意', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Fr数沿程变化
        ax5 = plt.subplot(3, 3, 5)
        
        Fr_profile = [self.froude_number(h) for h in h1]
        
        ax5.plot(x1, Fr_profile, 'b-', linewidth=2)
        ax5.axhline(1, color='red', linestyle='--', linewidth=1.5, label='Fr=1(临界流)')
        ax5.fill_between(x1, 0, Fr_profile, where=np.array(Fr_profile)<1, alpha=0.3, color='blue', label='缓流区')
        ax5.fill_between(x1, 0, Fr_profile, where=np.array(Fr_profile)>=1, alpha=0.3, color='orange', label='急流区')
        
        ax5.set_xlabel('距离 x (m)', fontsize=10)
        ax5.set_ylabel('Froude数 Fr', fontsize=10)
        ax5.set_title('Fr数沿程分布', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 能坡与底坡比较
        ax6 = plt.subplot(3, 3, 6)
        
        J_profile = [self.energy_slope(h) for h in h1]
        
        ax6.plot(x1, J_profile, 'b-', linewidth=2, label='能坡J')
        ax6.axhline(self.i1, color='red', linestyle='--', linewidth=1.5, label=f'底坡i={self.i1}')
        
        ax6.set_xlabel('距离 x (m)', fontsize=10)
        ax6.set_ylabel('坡度', fontsize=10)
        ax6.set_title('能坡与底坡比较', fontsize=12, fontweight='bold')
        ax6.set_yscale('log')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 壅水高度分布
        ax7 = plt.subplot(3, 3, 7)
        
        backwater = h1 - h01
        
        ax7.plot(x1, backwater, 'r-', linewidth=2)
        ax7.fill_between(x1, 0, backwater, alpha=0.3, color='red')
        ax7.axhline(0, color='k', linestyle='-', linewidth=0.5)
        
        ax7.set_xlabel('距离 x (m)', fontsize=10)
        ax7.set_ylabel('壅水高度 Δh (m)', fontsize=10)
        ax7.set_title('壅水高度分布', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        
        max_backwater = backwater.max()
        ax7.text(x1[np.argmax(backwater)], max_backwater, 
                f'最大壅水\n{max_backwater:.2f}m', 
                ha='center', va='bottom', fontsize=9, color='red', fontweight='bold')
        
        # 8. 水面曲线分类图
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '水面曲线分类', fontsize=11, ha='center', fontweight='bold')
        ax8.text(0.1, 0.85, '缓坡(M):', fontsize=10, color='blue', fontweight='bold')
        ax8.text(0.15, 0.77, 'M1: h>h₀>hc (壅水)', fontsize=9)
        ax8.text(0.15, 0.70, 'M2: h₀>h>hc (降水)', fontsize=9)
        ax8.text(0.15, 0.63, 'M3: h₀>hc>h (降水)', fontsize=9)
        
        ax8.text(0.1, 0.52, '陡坡(S):', fontsize=10, color='red', fontweight='bold')
        ax8.text(0.15, 0.44, 'S1: h>hc>h₀ (壅水)', fontsize=9)
        ax8.text(0.15, 0.37, 'S2: hc>h>h₀ (降水)', fontsize=9)
        ax8.text(0.15, 0.30, 'S3: hc>h₀>h (降水)', fontsize=9)
        
        ax8.text(0.1, 0.19, f'当前情况: {self.profile_type(h_start1, h01, hc)}', 
                fontsize=10, color='green', fontweight='bold')
        
        ax8.set_title('曲线类型', fontsize=12, fontweight='bold')
        
        # 9. 综合结果表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['参数', '上游', '下游'],
            ['底坡', f'{self.i1}', f'{self.i2}'],
            ['正常水深(m)', f'{h01:.3f}', f'{h02:.3f}'],
            ['临界水深(m)', f'{hc:.3f}', f'{hc:.3f}'],
            ['Froude数', f'{self.froude_number(h01):.3f}', f'{self.froude_number(h02):.3f}'],
            ['流态', '缓流' if self.froude_number(h01)<1 else '急流', '缓流' if self.froude_number(h02)<1 else '急流'],
            ['最大壅水(m)', f'{max_backwater:.3f}', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.35, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch09_problem06_surface_profile.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch09_problem06_surface_profile.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第09章 渠系水力计算 - 题6：非均匀流水面曲线")
        print("="*70)
        
        h01 = self.normal_depth(self.i1)
        h02 = self.normal_depth(self.i2)
        hc = self.critical_depth()
        
        print(f"\n【渠道参数】")
        print(f"矩形断面宽度: b = {self.b} m")
        print(f"糙率: n = {self.n}")
        print(f"流量: Q = {self.Q} m³/s")
        print(f"上游底坡: i₁ = {self.i1}")
        print(f"下游底坡: i₂ = {self.i2}")
        
        print(f"\n【关键水深】")
        print(f"上游正常水深: h₀₁ = {h01:.3f} m")
        print(f"下游正常水深: h₀₂ = {h02:.3f} m")
        print(f"临界水深: hc = {hc:.3f} m")
        
        print(f"\n【流态判别】")
        Fr1 = self.froude_number(h01)
        Fr2 = self.froude_number(h02)
        print(f"上游Froude数: Fr₁ = {Fr1:.3f} ({'缓流' if Fr1<1 else '急流'})")
        print(f"下游Froude数: Fr₂ = {Fr2:.3f} ({'缓流' if Fr2<1 else '急流'})")
        
        print(f"\n【水面曲线】")
        h_start = h01 + 0.5
        print(f"起始水深: h = {h_start:.3f} m")
        print(f"曲线类型: {self.profile_type(h_start, h01, hc)}")
        
        print(f"\n✓ 水面曲线分析完成")
        print(f"\n{'='*70}\n")


def main():
    b = 5
    n = 0.025
    Q = 20
    i1 = 0.001
    i2 = 0.0005
    
    sp = SurfaceProfile(b, n, Q, i1, i2)
    sp.print_results()
    sp.plot_analysis()


if __name__ == "__main__":
    main()
