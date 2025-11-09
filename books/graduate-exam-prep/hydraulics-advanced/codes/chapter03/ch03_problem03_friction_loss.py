#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第03章 管流与明渠流 - 题目3：沿程损失计算

题目描述：
水平管道输水，已知：
- 管长L=1000m
- 管径d=0.3m
- 流量Q=0.1m³/s
- 粗糙系数n=0.012（混凝土管）

求：
(1) 沿程阻力系数λ
(2) 沿程水头损失h_f
(3) 压力降低值Δp
(4) 不同粗糙度的影响

知识点：
- 达西-魏斯巴赫公式
- 谢才公式
- 曼宁公式
- 摩阻系数计算

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FrictionLossAnalysis:
    """沿程损失计算类"""
    
    def __init__(self, L: float, d: float, Q: float, n: float = 0.012,
                 rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        L : float
            管长 (m)
        d : float
            管径 (m)
        Q : float
            流量 (m³/s)
        n : float
            曼宁粗糙系数
        rho : float
            水密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.L = L
        self.d = d
        self.Q = Q
        self.n = n
        self.rho = rho
        self.g = g
    
    def velocity(self) -> float:
        """
        计算平均流速
        
        v = Q / A
        
        Returns:
        --------
        float : 流速 (m/s)
        """
        A = np.pi * self.d**2 / 4
        return self.Q / A
    
    def reynolds_number(self) -> float:
        """
        计算雷诺数
        
        Re = vd/ν
        
        Returns:
        --------
        float : 雷诺数
        """
        v = self.velocity()
        nu = 1.0e-6  # 20°C水的运动粘度
        return v * self.d / nu
    
    def friction_factor_manning(self) -> float:
        """
        根据曼宁公式计算沿程阻力系数
        
        曼宁公式：v = (1/n) * R^(2/3) * J^(1/2)
        达西公式：h_f = λ * (L/d) * (v²/2g)
        
        推导：λ = 8g * n² / R^(1/3)
        圆管：R = d/4
        
        Returns:
        --------
        float : 沿程阻力系数λ
        """
        R = self.d / 4  # 水力半径（圆管）
        lambda_f = 8 * self.g * self.n**2 / R**(1/3)
        return lambda_f
    
    def friction_factor_colebrook(self, epsilon: float = 0.0003) -> float:
        """
        根据Colebrook-White公式计算沿程阻力系数
        
        1/√λ = -2log₁₀(ε/3.7d + 2.51/(Re√λ))
        
        使用迭代法求解
        
        Parameters:
        -----------
        epsilon : float
            绝对粗糙度 (m)
            
        Returns:
        --------
        float : 沿程阻力系数λ
        """
        Re = self.reynolds_number()
        
        # 初始值（Swamee-Jain近似）
        lambda_f = 0.25 / (np.log10(epsilon/(3.7*self.d) + 5.74/Re**0.9))**2
        
        # 迭代求解
        for _ in range(20):
            f_old = lambda_f
            lambda_f = 1 / (-2 * np.log10(epsilon/(3.7*self.d) + 
                                          2.51/(Re*np.sqrt(lambda_f))))**2
            if abs(lambda_f - f_old) < 1e-6:
                break
        
        return lambda_f
    
    def head_loss(self) -> float:
        """
        计算沿程水头损失
        
        达西-魏斯巴赫公式：
        h_f = λ * (L/d) * (v²/2g)
        
        Returns:
        --------
        float : 沿程水头损失 (m)
        """
        lambda_f = self.friction_factor_manning()
        v = self.velocity()
        
        h_f = lambda_f * (self.L / self.d) * (v**2 / (2 * self.g))
        return h_f
    
    def pressure_drop(self) -> float:
        """
        计算压力降低值
        
        Δp = ρg * h_f
        
        Returns:
        --------
        float : 压力降低 (Pa)
        """
        h_f = self.head_loss()
        return self.rho * self.g * h_f
    
    def roughness_analysis(self, n_range: tuple = (0.008, 0.020), 
                          n_points: int = 50) -> tuple:
        """
        不同粗糙度的影响分析
        
        Parameters:
        -----------
        n_range : tuple
            粗糙系数范围
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (n_array, lambda_array, hf_array, dp_array)
        """
        n_array = np.linspace(n_range[0], n_range[1], n_points)
        
        lambda_array = np.zeros(n_points)
        hf_array = np.zeros(n_points)
        dp_array = np.zeros(n_points)
        
        v = self.velocity()
        R = self.d / 4
        
        for i, n in enumerate(n_array):
            # 阻力系数
            lambda_f = 8 * self.g * n**2 / R**(1/3)
            lambda_array[i] = lambda_f
            
            # 水头损失
            h_f = lambda_f * (self.L / self.d) * (v**2 / (2 * self.g))
            hf_array[i] = h_f
            
            # 压力降
            dp = self.rho * self.g * h_f
            dp_array[i] = dp
        
        return n_array, lambda_array, hf_array, dp_array
    
    def diameter_analysis(self, d_range: tuple = (0.1, 0.5), 
                         n_points: int = 50) -> tuple:
        """
        不同管径的影响分析
        
        Parameters:
        -----------
        d_range : tuple
            管径范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (d_array, v_array, lambda_array, hf_array)
        """
        d_array = np.linspace(d_range[0], d_range[1], n_points)
        
        v_array = np.zeros(n_points)
        lambda_array = np.zeros(n_points)
        hf_array = np.zeros(n_points)
        
        for i, d in enumerate(d_array):
            # 流速
            A = np.pi * d**2 / 4
            v = self.Q / A
            v_array[i] = v
            
            # 阻力系数
            R = d / 4
            lambda_f = 8 * self.g * self.n**2 / R**(1/3)
            lambda_array[i] = lambda_f
            
            # 水头损失
            h_f = lambda_f * (self.L / d) * (v**2 / (2 * self.g))
            hf_array[i] = h_f
        
        return d_array, v_array, lambda_array, hf_array
    
    def length_analysis(self, L_range: tuple = (100, 2000), 
                       n_points: int = 50) -> tuple:
        """
        不同管长的影响分析
        
        Parameters:
        -----------
        L_range : tuple
            管长范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (L_array, hf_array, dp_array)
        """
        L_array = np.linspace(L_range[0], L_range[1], n_points)
        
        lambda_f = self.friction_factor_manning()
        v = self.velocity()
        
        # 水头损失正比于管长
        hf_array = lambda_f * (L_array / self.d) * (v**2 / (2 * self.g))
        
        # 压力降
        dp_array = self.rho * self.g * hf_array
        
        return L_array, hf_array, dp_array
    
    def plot_analysis(self):
        """绘制沿程损失分析图"""
        fig = plt.figure(figsize=(15, 10))
        
        # 图1：水头损失沿程分布
        ax1 = plt.subplot(2, 3, 1)
        
        lambda_f = self.friction_factor_manning()
        v = self.velocity()
        
        # 沿程位置
        x = np.linspace(0, self.L, 100)
        # 水头损失分布（线性）
        h_f_x = lambda_f * (x / self.d) * (v**2 / (2 * self.g))
        
        ax1.plot(x, h_f_x, 'b-', linewidth=2.5, label='水头损失线')
        ax1.fill_between(x, 0, h_f_x, color='lightblue', alpha=0.5)
        
        # 标注关键点
        h_f_total = self.head_loss()
        ax1.plot([0, self.L], [0, h_f_total], 'ro', markersize=10)
        ax1.text(self.L/2, h_f_total/2, 
                f'h_f = {h_f_total:.2f}m\nλ = {lambda_f:.4f}',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax1.set_xlabel('沿程距离 x (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('水头损失 h_f (m)', fontsize=11, fontweight='bold')
        ax1.set_title('沿程水头损失分布', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 图2：粗糙度影响
        ax2 = plt.subplot(2, 3, 2)
        
        n_array, lambda_array, hf_array, dp_array = self.roughness_analysis()
        
        ax2_twin = ax2.twinx()
        
        line1 = ax2.plot(n_array*1000, lambda_array, 'b-', linewidth=2.5, 
                        label='阻力系数λ', marker='o', markersize=4, 
                        markevery=5)
        line2 = ax2_twin.plot(n_array*1000, hf_array, 'r-', linewidth=2.5,
                             label='水头损失h_f', marker='s', markersize=4,
                             markevery=5)
        
        # 标注当前点
        idx = np.argmin(np.abs(n_array - self.n))
        ax2.plot([self.n*1000], [lambda_array[idx]], 'go', markersize=12,
                label='当前状态')
        
        ax2.set_xlabel('粗糙系数 n (×10⁻³)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('阻力系数 λ', fontsize=11, fontweight='bold', color='b')
        ax2_twin.set_ylabel('水头损失 h_f (m)', fontsize=11, fontweight='bold', color='r')
        ax2.set_title('粗糙度对沿程损失的影响', fontsize=13, fontweight='bold')
        
        ax2.tick_params(axis='y', labelcolor='b')
        ax2_twin.tick_params(axis='y', labelcolor='r')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, fontsize=9, loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # 图3：管径影响
        ax3 = plt.subplot(2, 3, 3)
        
        d_array, v_array, lambda_d, hf_d = self.diameter_analysis()
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(d_array*1000, hf_d, 'b-', linewidth=2.5,
                        label='水头损失h_f')
        line2 = ax3_twin.plot(d_array*1000, v_array, 'r-', linewidth=2.5,
                             label='流速v')
        
        # 标注当前点
        idx = np.argmin(np.abs(d_array - self.d))
        ax3.plot([self.d*1000], [hf_d[idx]], 'go', markersize=12,
                label='当前状态')
        
        ax3.set_xlabel('管径 d (mm)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('水头损失 h_f (m)', fontsize=11, fontweight='bold', color='b')
        ax3_twin.set_ylabel('流速 v (m/s)', fontsize=11, fontweight='bold', color='r')
        ax3.set_title('管径对沿程损失的影响', fontsize=13, fontweight='bold')
        
        ax3.tick_params(axis='y', labelcolor='b')
        ax3_twin.tick_params(axis='y', labelcolor='r')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, fontsize=9, loc='upper right')
        ax3.grid(True, alpha=0.3)
        
        # 标注趋势
        ax3.text(350, max(hf_d)*0.5,
                '管径↑\n→ v↓\n→ h_f↓',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图4：管长影响
        ax4 = plt.subplot(2, 3, 4)
        
        L_array, hf_L, dp_L = self.length_analysis()
        
        ax4.plot(L_array/1000, hf_L, 'b-', linewidth=2.5, label='水头损失')
        ax4.plot([self.L/1000], [self.head_loss()], 'ro', markersize=12,
                label='当前状态')
        
        ax4.set_xlabel('管长 L (km)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('水头损失 h_f (m)', fontsize=11, fontweight='bold')
        ax4.set_title('管长对沿程损失的影响', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        # 标注线性关系
        ax4.text(1.2, max(hf_L)*0.7,
                'h_f ∝ L\n（线性关系）',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图5：压力分布
        ax5 = plt.subplot(2, 3, 5)
        
        # 假设初始压力
        p0 = 500000  # Pa (5个大气压)
        
        x_pressure = np.linspace(0, self.L, 100)
        h_f_x_pressure = lambda_f * (x_pressure / self.d) * (v**2 / (2 * self.g))
        p_x = p0 - self.rho * self.g * h_f_x_pressure
        
        ax5.plot(x_pressure, p_x/1000, 'b-', linewidth=2.5, label='压力分布')
        ax5.axhline(y=p0/1000, color='g', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'初始压力={p0/1000:.0f}kPa')
        
        # 标注压降
        dp = self.pressure_drop()
        ax5.annotate('', xy=(self.L, (p0-dp)/1000), xytext=(self.L, p0/1000),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax5.text(self.L*0.85, p0/1000 - dp/2000,
                f'Δp = {dp/1000:.1f}kPa',
                fontsize=11, fontweight='bold', color='red')
        
        ax5.set_xlabel('沿程距离 x (m)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('压力 p (kPa)', fontsize=11, fontweight='bold')
        ax5.set_title('沿程压力分布', fontsize=13, fontweight='bold')
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)
        
        # 图6：能量线与水力坡度
        ax6 = plt.subplot(2, 3, 6)
        
        x_energy = np.linspace(0, self.L, 100)
        
        # 能量线（以管道为基准）
        E_x = h_f_total - h_f_x
        
        # 水力坡度
        J = h_f_total / self.L
        
        ax6.plot(x_energy, E_x, 'b-', linewidth=2.5, label='能量线')
        ax6.fill_between(x_energy, 0, E_x, color='lightblue', alpha=0.3)
        
        # 标注水力坡度
        ax6.plot([0, self.L], [h_f_total, 0], 'r--', linewidth=2,
                label=f'水力坡度J={J:.5f}')
        
        # 标注坡度角
        angle_deg = np.arctan(J) * 180 / np.pi
        ax6.text(self.L/2, h_f_total/2,
                f'J = {J:.5f}\n= 1/{1/J:.0f}\n角度={angle_deg:.3f}°',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax6.set_xlabel('沿程距离 x (m)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('水头 (m)', fontsize=11, fontweight='bold')
        ax6.set_title('能量线与水力坡度', fontsize=13, fontweight='bold')
        ax6.legend(fontsize=10)
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("沿程损失计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  管长：L = {self.L}m = {self.L/1000}km")
        print(f"  管径：d = {self.d}m = {self.d*1000}mm")
        print(f"  流量：Q = {self.Q}m³/s")
        print(f"  粗糙系数：n = {self.n}（混凝土管）")
        
        # 基本参数
        A = np.pi * self.d**2 / 4
        v = self.velocity()
        Re = self.reynolds_number()
        R = self.d / 4
        
        print(f"\n基本参数：")
        print(f"  过流断面积：A = πd²/4 = {A:.4f} m²")
        print(f"  平均流速：v = Q/A = {v:.3f} m/s")
        print(f"  雷诺数：Re = vd/ν = {Re:.0f}")
        
        if Re > 4000:
            print(f"  流态：紊流（Re > 4000）")
        elif Re > 2000:
            print(f"  流态：过渡流（2000 < Re < 4000）")
        else:
            print(f"  流态：层流（Re < 2000）")
        
        print(f"  水力半径：R = d/4 = {R:.4f} m")
        
        # (1) 沿程阻力系数
        lambda_f = self.friction_factor_manning()
        
        print(f"\n(1) 沿程阻力系数：")
        print(f"  使用曼宁公式推导：")
        print(f"    λ = 8gn²/R^(1/3)")
        print(f"      = 8 × {self.g} × {self.n}² / {R}^(1/3)")
        print(f"      = {lambda_f:.6f}")
        
        # 对比Colebrook公式
        lambda_c = self.friction_factor_colebrook()
        print(f"\n  对比Colebrook公式：")
        print(f"    λ = {lambda_c:.6f}")
        print(f"    差异：{abs(lambda_f - lambda_c)/lambda_c*100:.2f}%")
        
        # (2) 沿程水头损失
        h_f = self.head_loss()
        
        print(f"\n(2) 沿程水头损失：")
        print(f"  达西-魏斯巴赫公式：")
        print(f"    h_f = λ × (L/d) × (v²/2g)")
        print(f"        = {lambda_f:.6f} × ({self.L}/{self.d}) × ({v}²/(2×{self.g}))")
        print(f"        = {lambda_f:.6f} × {self.L/self.d:.2f} × {v**2/(2*self.g):.4f}")
        print(f"        = {h_f:.3f} m")
        
        # 水力坡度
        J = h_f / self.L
        print(f"\n  水力坡度：")
        print(f"    J = h_f/L = {h_f:.3f}/{self.L} = {J:.6f}")
        print(f"    即 1/{1/J:.0f}（每米降低{J*1000:.3f}mm）")
        
        # (3) 压力降低值
        dp = self.pressure_drop()
        
        print(f"\n(3) 压力降低值：")
        print(f"  Δp = ρg × h_f")
        print(f"      = {self.rho} × {self.g} × {h_f:.3f}")
        print(f"      = {dp:.0f} Pa")
        print(f"      = {dp/1000:.2f} kPa")
        print(f"      = {dp/100000:.3f} bar")
        print(f"      ≈ {dp/101325:.2f} atm")
        
        # (4) 粗糙度影响
        print(f"\n(4) 粗糙度影响分析：")
        
        # 常见管道类型
        pipe_types = {
            '玻璃管/铜管': 0.008,
            '钢管/铸铁管': 0.012,
            '混凝土管': 0.013,
            '旧铸铁管': 0.017,
            '粗糙混凝土管': 0.020
        }
        
        print(f"\n  常见管道类型对比：")
        print(f"  {'类型':<15} {'n':<8} {'λ':<10} {'h_f(m)':<10} {'Δp(kPa)':<10}")
        print(f"  {'-'*55}")
        
        for pipe_type, n_value in pipe_types.items():
            lambda_temp = 8 * self.g * n_value**2 / R**(1/3)
            hf_temp = lambda_temp * (self.L / self.d) * (v**2 / (2 * self.g))
            dp_temp = self.rho * self.g * hf_temp / 1000
            
            marker = " ✓" if abs(n_value - self.n) < 0.001 else ""
            print(f"  {pipe_type:<15} {n_value:<8.3f} {lambda_temp:<10.6f} "
                  f"{hf_temp:<10.2f} {dp_temp:<10.2f}{marker}")
        
        print(f"\n  结论：粗糙度↑ → λ↑ → h_f↑ → Δp↑")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 达西公式：h_f = λ(L/d)(v²/2g)")
        print("2. 曼宁公式：v = (1/n)R^(2/3)J^(1/2)")
        print("3. 水力坡度：J = h_f/L")
        print("4. 压力降：Δp = ρgh_f")
        print("5. 影响因素：管长、管径、流速、粗糙度")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第03章 管流与明渠流 - 题目3：沿程损失计算")
    print("💧" * 35 + "\n")
    
    # 题目参数
    L = 1000.0      # 管长1000m
    d = 0.3         # 管径0.3m
    Q = 0.1         # 流量0.1m³/s
    n = 0.012       # 粗糙系数0.012（混凝土管）
    
    # 创建沿程损失分析对象
    friction = FrictionLossAnalysis(L=L, d=d, Q=Q, n=n)
    
    # 打印结果
    friction.print_results()
    
    # 绘图
    print("\n正在绘制沿程损失分析图...")
    friction.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
