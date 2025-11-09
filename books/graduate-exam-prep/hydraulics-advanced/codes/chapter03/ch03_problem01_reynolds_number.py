#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第03章 管流与明渠流 - 题目1：雷诺数与流态判别

题目描述：
圆形管道输水，已知：
- 管径d=0.1m
- 流速v=2m/s
- 水温20°C，运动粘度ν=1.0×10⁻⁶ m²/s

求：
(1) 雷诺数Re
(2) 判别流态
(3) 不同流速下的流态转换
(4) 温度对流态的影响

知识点：
- 雷诺数计算
- 流态判别（层流/紊流）
- 临界雷诺数
- 影响因素分析

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ReynoldsNumberAnalysis:
    """雷诺数与流态分析类"""
    
    def __init__(self, d: float, v: float, nu: float = 1.0e-6,
                 Re_lower: float = 2000, Re_upper: float = 4000):
        """
        初始化参数
        
        Parameters:
        -----------
        d : float
            管径 (m)
        v : float
            流速 (m/s)
        nu : float
            运动粘度 (m²/s)
        Re_lower : float
            临界雷诺数下限
        Re_upper : float
            临界雷诺数上限
        """
        self.d = d
        self.v = v
        self.nu = nu
        self.Re_lower = Re_lower
        self.Re_upper = Re_upper
    
    def reynolds_number(self) -> float:
        """
        计算雷诺数
        
        Re = vd/ν
        
        Returns:
        --------
        float : 雷诺数
        """
        return self.v * self.d / self.nu
    
    def flow_regime(self) -> str:
        """
        判别流态
        
        Returns:
        --------
        str : 流态（层流/过渡流/紊流）
        """
        Re = self.reynolds_number()
        
        if Re < self.Re_lower:
            return "层流"
        elif Re > self.Re_upper:
            return "紊流"
        else:
            return "过渡流"
    
    def critical_velocity(self) -> tuple:
        """
        计算临界流速
        
        Returns:
        --------
        tuple : (v_lower, v_upper)
            v_lower : 层流→过渡流临界流速 (m/s)
            v_upper : 过渡流→紊流临界流速 (m/s)
        """
        v_lower = self.Re_lower * self.nu / self.d
        v_upper = self.Re_upper * self.nu / self.d
        return v_lower, v_upper
    
    def velocity_analysis(self, v_range: tuple = (0, 5), n_points: int = 100) -> tuple:
        """
        不同流速下的雷诺数分析
        
        Parameters:
        -----------
        v_range : tuple
            流速范围 (m/s)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (v_array, Re_array)
        """
        v_array = np.linspace(v_range[0], v_range[1], n_points)
        Re_array = v_array * self.d / self.nu
        return v_array, Re_array
    
    def temperature_effect(self, T_range: tuple = (0, 40), n_points: int = 20) -> tuple:
        """
        温度对雷诺数的影响
        
        运动粘度与温度关系（经验公式）：
        ν(T) = ν₂₀ × (293/(273+T))^1.5
        
        Parameters:
        -----------
        T_range : tuple
            温度范围 (°C)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (T_array, nu_array, Re_array)
        """
        T_array = np.linspace(T_range[0], T_range[1], n_points)
        nu_20 = 1.0e-6  # 20°C时的运动粘度
        
        # 计算不同温度下的运动粘度
        nu_array = nu_20 * (293 / (273 + T_array))**1.5
        
        # 计算雷诺数
        Re_array = self.v * self.d / nu_array
        
        return T_array, nu_array, Re_array
    
    def diameter_effect(self, d_range: tuple = (0.02, 0.5), n_points: int = 50) -> tuple:
        """
        管径对雷诺数的影响
        
        Parameters:
        -----------
        d_range : tuple
            管径范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (d_array, Re_array)
        """
        d_array = np.linspace(d_range[0], d_range[1], n_points)
        Re_array = self.v * d_array / self.nu
        return d_array, Re_array
    
    def plot_analysis(self):
        """绘制雷诺数分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：雷诺数与流态判别
        ax1 = axes[0, 0]
        
        Re = self.reynolds_number()
        regime = self.flow_regime()
        v_lower, v_upper = self.critical_velocity()
        
        # 绘制流态区域
        ax1.axhspan(0, self.Re_lower, color='lightblue', alpha=0.3, label='层流区')
        ax1.axhspan(self.Re_lower, self.Re_upper, color='lightyellow', 
                   alpha=0.3, label='过渡流区')
        ax1.axhspan(self.Re_upper, 300000, color='lightcoral', alpha=0.3, label='紊流区')
        
        # 标注临界雷诺数
        ax1.axhline(y=self.Re_lower, color='blue', linestyle='--', 
                   linewidth=2, label=f'Re_下限={self.Re_lower}')
        ax1.axhline(y=self.Re_upper, color='red', linestyle='--',
                   linewidth=2, label=f'Re_上限={self.Re_upper}')
        
        # 标注当前雷诺数
        ax1.plot([0, 1], [Re, Re], 'g-', linewidth=3, marker='o', 
                markersize=12, label=f'当前Re={Re:.0f}')
        
        # 流态标注
        regime_color = {'层流': 'blue', '过渡流': 'orange', '紊流': 'red'}
        ax1.text(0.5, Re, f'  {regime}', fontsize=14, fontweight='bold',
                color=regime_color.get(regime, 'black'), va='center')
        
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 300000)
        ax1.set_ylabel('雷诺数 Re', fontsize=11, fontweight='bold')
        ax1.set_title('雷诺数与流态判别', fontsize=13, fontweight='bold')
        ax1.set_xticks([])
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 图2：流速对雷诺数的影响
        ax2 = axes[0, 1]
        
        v_array, Re_array = self.velocity_analysis()
        
        ax2.plot(v_array, Re_array, 'b-', linewidth=2.5, label='Re vs v')
        
        # 标注临界流速
        ax2.axhline(y=self.Re_lower, color='blue', linestyle='--', 
                   linewidth=1.5, alpha=0.7)
        ax2.axhline(y=self.Re_upper, color='red', linestyle='--',
                   linewidth=1.5, alpha=0.7)
        ax2.axvline(x=v_lower, color='blue', linestyle=':', linewidth=1.5, alpha=0.7)
        ax2.axvline(x=v_upper, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
        
        # 填充流态区域
        ax2.fill_between(v_array, 0, Re_array, where=(Re_array<self.Re_lower),
                        color='lightblue', alpha=0.3, label='层流')
        ax2.fill_between(v_array, 0, Re_array, 
                        where=((Re_array>=self.Re_lower) & (Re_array<=self.Re_upper)),
                        color='lightyellow', alpha=0.3, label='过渡流')
        ax2.fill_between(v_array, 0, Re_array, where=(Re_array>self.Re_upper),
                        color='lightcoral', alpha=0.3, label='紊流')
        
        # 标注当前点
        ax2.plot([self.v], [Re], 'ro', markersize=12, label=f'当前状态')
        
        ax2.set_xlabel('流速 v (m/s)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('雷诺数 Re', fontsize=11, fontweight='bold')
        ax2.set_title('流速对雷诺数的影响', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        # 标注临界流速
        ax2.text(v_lower, self.Re_lower + 5000, f'v_下={v_lower:.3f}m/s',
                fontsize=9, fontweight='bold', color='blue')
        ax2.text(v_upper, self.Re_upper + 5000, f'v_上={v_upper:.3f}m/s',
                fontsize=9, fontweight='bold', color='red')
        
        # 图3：温度对雷诺数的影响
        ax3 = axes[1, 0]
        
        T_array, nu_array, Re_T = self.temperature_effect()
        
        ax3.plot(T_array, Re_T, 'r-', linewidth=2.5, label='Re vs T')
        ax3.axhline(y=self.Re_lower, color='blue', linestyle='--', 
                   linewidth=1.5, alpha=0.7, label=f'Re={self.Re_lower}')
        ax3.axhline(y=self.Re_upper, color='red', linestyle='--',
                   linewidth=1.5, alpha=0.7, label=f'Re={self.Re_upper}')
        
        # 标注20°C
        Re_20 = self.v * self.d / 1.0e-6
        ax3.plot([20], [Re_20], 'go', markersize=12, label='20°C（当前）')
        
        ax3.set_xlabel('温度 T (°C)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('雷诺数 Re', fontsize=11, fontweight='bold')
        ax3.set_title('温度对雷诺数的影响', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
        
        # 标注趋势
        ax3.text(25, max(Re_T) * 0.8,
                '温度↑ → ν↓ → Re↑\n（水温升高，流态更易紊流）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：管径对雷诺数的影响
        ax4 = axes[1, 1]
        
        d_array, Re_d = self.diameter_effect()
        
        ax4.plot(d_array * 1000, Re_d, 'g-', linewidth=2.5, label='Re vs d')
        ax4.axhline(y=self.Re_lower, color='blue', linestyle='--',
                   linewidth=1.5, alpha=0.7, label=f'Re={self.Re_lower}')
        ax4.axhline(y=self.Re_upper, color='red', linestyle='--',
                   linewidth=1.5, alpha=0.7, label=f'Re={self.Re_upper}')
        
        # 标注当前管径
        ax4.plot([self.d * 1000], [Re], 'ro', markersize=12, label=f'd={self.d}m')
        
        ax4.set_xlabel('管径 d (mm)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('雷诺数 Re', fontsize=11, fontweight='bold')
        ax4.set_title('管径对雷诺数的影响', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)
        
        # 标注趋势
        ax4.text(250, max(Re_d) * 0.7,
                '管径↑ → Re↑\n（管径越大，流态更易紊流）',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("雷诺数与流态判别")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  管径：d = {self.d}m = {self.d*1000}mm")
        print(f"  流速：v = {self.v}m/s")
        print(f"  运动粘度：ν = {self.nu:.2e} m²/s（20°C水）")
        
        # (1) 雷诺数
        Re = self.reynolds_number()
        
        print(f"\n(1) 雷诺数计算：")
        print(f"  Re = vd/ν")
        print(f"     = {self.v} × {self.d} / {self.nu:.2e}")
        print(f"     = {Re:.0f}")
        
        # (2) 流态判别
        regime = self.flow_regime()
        
        print(f"\n(2) 流态判别：")
        print(f"  判别标准：")
        print(f"    Re < {self.Re_lower}：层流")
        print(f"    {self.Re_lower} < Re < {self.Re_upper}：过渡流")
        print(f"    Re > {self.Re_upper}：紊流")
        
        print(f"\n  当前流态：Re = {Re:.0f}")
        
        if regime == "层流":
            print(f"  ✓ {regime}（Re < {self.Re_lower}）")
            print(f"  特点：流体质点作有规则的层状运动")
        elif regime == "过渡流":
            print(f"  ⚠ {regime}（{self.Re_lower} < Re < {self.Re_upper}）")
            print(f"  特点：流态不稳定，可能在层流和紊流间转换")
        else:
            print(f"  ✓ {regime}（Re > {self.Re_upper}）")
            print(f"  特点：流体质点作无规则的脉动运动")
        
        # (3) 临界流速
        v_lower, v_upper = self.critical_velocity()
        
        print(f"\n(3) 临界流速分析：")
        print(f"  层流→过渡流临界流速：")
        print(f"    v_下 = Re_下 × ν / d")
        print(f"        = {self.Re_lower} × {self.nu:.2e} / {self.d}")
        print(f"        = {v_lower:.4f} m/s")
        
        print(f"\n  过渡流→紊流临界流速：")
        print(f"    v_上 = Re_上 × ν / d")
        print(f"        = {self.Re_upper} × {self.nu:.2e} / {self.d}")
        print(f"        = {v_upper:.4f} m/s")
        
        print(f"\n  当前流速：v = {self.v} m/s")
        if self.v < v_lower:
            print(f"  → 低于临界流速，为层流")
        elif self.v > v_upper:
            print(f"  → 高于临界流速，为紊流")
            print(f"  → 超出{(self.v - v_upper)/v_upper*100:.1f}%")
        else:
            print(f"  → 处于临界区间，为过渡流")
        
        # (4) 影响因素
        print(f"\n(4) 影响因素分析：")
        
        print(f"\n  【流速影响】")
        print(f"    Re ∝ v（正比关系）")
        print(f"    流速增大 → 雷诺数增大 → 趋向紊流")
        
        print(f"\n  【管径影响】")
        print(f"    Re ∝ d（正比关系）")
        print(f"    管径增大 → 雷诺数增大 → 趋向紊流")
        
        print(f"\n  【粘度影响】")
        print(f"    Re ∝ 1/ν（反比关系）")
        print(f"    粘度增大 → 雷诺数减小 → 趋向层流")
        
        print(f"\n  【温度影响（水）】")
        T_array, nu_array, Re_T = self.temperature_effect()
        Re_0 = Re_T[0]
        Re_40 = Re_T[-1]
        print(f"    0°C：ν={nu_array[0]:.2e} m²/s，Re={Re_0:.0f}")
        print(f"    20°C：ν={1.0e-6:.2e} m²/s，Re={Re:.0f}")
        print(f"    40°C：ν={nu_array[-1]:.2e} m²/s，Re={Re_40:.0f}")
        print(f"    温度升高 → 粘度降低 → 雷诺数增大 → 趋向紊流")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 雷诺数公式：Re = vd/ν")
        print("2. 流态判别：Re<2000层流，2000<Re<4000过渡流，Re>4000紊流")
        print("3. 物理意义：Re表示惯性力与粘性力的比值")
        print("4. 影响因素：流速、管径、粘度（温度）")
        print("5. 临界雷诺数：2300（通常取2000-4000）")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第03章 管流与明渠流 - 题目1：雷诺数判别")
    print("💧" * 35 + "\n")
    
    # 题目参数
    d = 0.1         # 管径0.1m
    v = 2.0         # 流速2m/s
    nu = 1.0e-6     # 运动粘度1.0×10⁻⁶ m²/s（20°C水）
    
    # 创建雷诺数分析对象
    reynolds = ReynoldsNumberAnalysis(d=d, v=v, nu=nu)
    
    # 打印结果
    reynolds.print_results()
    
    # 绘图
    print("\n正在绘制雷诺数分析图...")
    reynolds.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
