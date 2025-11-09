#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第02章 流体动力学基础 - 题目12：管道流量计算

题目描述：
串联管道系统，由d1=0.3m，L1=200m和d2=0.2m，L2=150m两段组成。
上游水箱水位H1=10m，下游水箱水位H2=2m。
粗糙度n=0.012，局部损失系数Σζ=3.5。
求：
(1) 通过管道的流量Q
(2) 两管段连接处的压强p
(3) 各管段的雷诺数

知识点：
- 串联管道计算
- 能量方程
- 水头损失
- 流量分配

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SeriesPipeFlow:
    """串联管道流量计算类"""
    
    def __init__(self, d1: float, L1: float, d2: float, L2: float,
                 H1: float, H2: float, n: float = 0.012, zeta_sum: float = 3.5,
                 rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        d1 : float
            管段1直径 (m)
        L1 : float
            管段1长度 (m)
        d2 : float
            管段2直径 (m)
        L2 : float
            管段2长度 (m)
        H1 : float
            上游水位 (m)
        H2 : float
            下游水位 (m)
        n : float
            粗糙度系数
        zeta_sum : float
            局部损失系数总和
        rho : float
            密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.d1 = d1
        self.L1 = L1
        self.d2 = d2
        self.L2 = L2
        self.H1 = H1
        self.H2 = H2
        self.n = n
        self.zeta_sum = zeta_sum
        self.rho = rho
        self.g = g
        
        # 计算断面面积
        self.A1 = np.pi * d1**2 / 4
        self.A2 = np.pi * d2**2 / 4
    
    def friction_factor(self, d: float) -> float:
        """
        计算摩擦系数
        
        Parameters:
        -----------
        d : float
            管道直径 (m)
            
        Returns:
        --------
        float : 摩擦系数
        """
        R = d / 4
        lamb = 8 * self.g * self.n**2 / R**(1/3)
        return lamb
    
    def head_loss_pipe(self, Q: float, d: float, L: float) -> float:
        """
        计算单段管道的水头损失
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
        d : float
            管道直径 (m)
        L : float
            管道长度 (m)
            
        Returns:
        --------
        float : 水头损失 (m)
        """
        A = np.pi * d**2 / 4
        v = Q / A
        lamb = self.friction_factor(d)
        hf = lamb * (L / d) * v**2 / (2 * self.g)
        return hf
    
    def head_loss_local(self, Q: float) -> float:
        """
        计算局部水头损失（基于管段1的流速）
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        float : 局部水头损失 (m)
        """
        v1 = Q / self.A1
        hm = self.zeta_sum * v1**2 / (2 * self.g)
        return hm
    
    def energy_equation(self, Q: float) -> float:
        """
        能量方程残差
        
        H1 = H2 + hf1 + hf2 + hm
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        float : 残差
        """
        hf1 = self.head_loss_pipe(Q, self.d1, self.L1)
        hf2 = self.head_loss_pipe(Q, self.d2, self.L2)
        hm = self.head_loss_local(Q)
        
        residual = self.H1 - self.H2 - hf1 - hf2 - hm
        return residual
    
    def calculate_discharge(self) -> float:
        """
        计算流量（迭代求解）
        
        Returns:
        --------
        float : 流量 (m³/s)
        """
        # 初始猜测值
        Q0 = 0.05
        
        # 求解能量方程
        Q = fsolve(self.energy_equation, Q0)[0]
        
        return Q
    
    def pressure_at_connection(self, Q: float) -> tuple:
        """
        计算连接处压强
        
        从上游水箱到连接处：
        H1 = z_conn + p_conn/(ρg) + v1²/(2g) + hf1 + hm1
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
            
        Returns:
        --------
        tuple : (p_conn, z_conn, v1)
            p_conn : 连接处压强 (Pa)
            z_conn : 连接处高程 (m)，假设为0
            v1 : 管段1流速 (m/s)
        """
        z_conn = 0  # 假设连接处在基准面
        v1 = Q / self.A1
        
        # 计算从入口到连接处的水头损失
        hf1 = self.head_loss_pipe(Q, self.d1, self.L1)
        hm1 = self.zeta_sum * 0.5 * v1**2 / (2 * self.g)  # 假设一半局部损失在管段1
        
        # 能量方程
        p_conn = self.rho * self.g * (self.H1 - z_conn - v1**2/(2*self.g) - hf1 - hm1)
        
        return p_conn, z_conn, v1
    
    def reynolds_number(self, Q: float, d: float) -> float:
        """
        计算雷诺数
        
        Parameters:
        -----------
        Q : float
            流量 (m³/s)
        d : float
            管道直径 (m)
            
        Returns:
        --------
        float : 雷诺数
        """
        A = np.pi * d**2 / 4
        v = Q / A
        nu = 1e-6  # 运动粘度
        Re = v * d / nu
        return Re
    
    def plot_system_diagram(self):
        """绘制管道系统分析图"""
        Q = self.calculate_discharge()
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：管道系统示意图
        ax1 = axes[0, 0]
        
        # 上游水箱
        ax1.add_patch(plt.Rectangle((-5, 0), 3, self.H1, 
                                    facecolor='lightblue', edgecolor='black', linewidth=2))
        ax1.text(-3.5, self.H1 + 0.5, f'H1={self.H1}m', ha='center', 
                fontsize=11, fontweight='bold')
        ax1.plot([-5, -2], [self.H1, self.H1], 'b-', linewidth=2)
        
        # 下游水箱
        total_length = self.L1 + self.L2
        ax1.add_patch(plt.Rectangle((total_length, 0), 3, self.H2,
                                    facecolor='lightblue', edgecolor='black', linewidth=2))
        ax1.text(total_length + 1.5, self.H2 + 0.5, f'H2={self.H2}m',
                ha='center', fontsize=11, fontweight='bold')
        ax1.plot([total_length, total_length + 3], [self.H2, self.H2], 'b-', linewidth=2)
        
        # 管段1
        y1 = self.H1 - 2
        ax1.add_patch(plt.Rectangle((0, y1 - self.d1/2), self.L1, self.d1,
                                    facecolor='gray', edgecolor='black', linewidth=2,
                                    label=f'管段1: d={self.d1}m, L={self.L1}m'))
        ax1.text(self.L1/2, y1 + 0.5, f'管段1\nd1={self.d1}m',
                ha='center', fontsize=10, fontweight='bold')
        
        # 管段2
        y2 = self.H2 + 1
        ax1.add_patch(plt.Rectangle((self.L1, y2 - self.d2/2), self.L2, self.d2,
                                    facecolor='darkgray', edgecolor='black', linewidth=2,
                                    label=f'管段2: d={self.d2}m, L={self.L2}m'))
        ax1.text(self.L1 + self.L2/2, y2 + 0.4, f'管段2\nd2={self.d2}m',
                ha='center', fontsize=10, fontweight='bold')
        
        # 连接管段
        ax1.plot([-2, 0], [self.H1 - 1, y1], 'k-', linewidth=3)
        ax1.plot([self.L1, self.L1], [y1, y2], 'k-', linewidth=3)
        ax1.plot([self.L1 + self.L2, total_length], [y2, self.H2 + 0.5], 'k-', linewidth=3)
        
        # 流量标注
        ax1.arrow(self.L1/2, y1 - 1, 20, 0, head_width=0.3, head_length=5,
                 fc='blue', ec='blue', linewidth=2)
        ax1.text(self.L1/2, y1 - 1.5, f'Q={Q:.4f}m³/s', ha='center',
                fontsize=11, fontweight='bold', color='blue')
        
        # 能量线
        hf1 = self.head_loss_pipe(Q, self.d1, self.L1)
        hf2 = self.head_loss_pipe(Q, self.d2, self.L2)
        hm = self.head_loss_local(Q)
        
        x_energy = [0, self.L1, self.L1 + self.L2]
        H_energy = [self.H1, self.H1 - hf1 - hm*0.5, self.H2]
        ax1.plot(x_energy, H_energy, 'g-', linewidth=3, marker='o',
                markersize=8, label='能量线')
        
        ax1.set_xlim(-10, total_length + 5)
        ax1.set_ylim(-1, self.H1 + 2)
        ax1.set_xlabel('水平距离 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('高程 (m)', fontsize=11, fontweight='bold')
        ax1.set_title('串联管道系统示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # 图2：水头损失分布
        ax2 = axes[0, 1]
        
        losses = ['管段1\n沿程损失', '管段2\n沿程损失', '局部损失', '总损失']
        values = [hf1, hf2, hm, hf1 + hf2 + hm]
        colors = ['lightblue', 'lightcoral', 'lightyellow', 'lightgreen']
        
        bars = ax2.bar(losses, values, color=colors, edgecolor='black',
                      linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.03,
                    f'{val:.2f}m', ha='center', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('水头损失 (m)', fontsize=11, fontweight='bold')
        ax2.set_title('水头损失分布', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 标注比例
        total_loss = hf1 + hf2 + hm
        ax2.text(1.5, max(values) * 0.6,
                f'管段1：{hf1/total_loss*100:.1f}%\n管段2：{hf2/total_loss*100:.1f}%\n局部：{hm/total_loss*100:.1f}%',
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图3：流速和雷诺数
        ax3 = axes[1, 0]
        
        v1 = Q / self.A1
        v2 = Q / self.A2
        Re1 = self.reynolds_number(Q, self.d1)
        Re2 = self.reynolds_number(Q, self.d2)
        
        sections = ['管段1', '管段2']
        velocities = [v1, v2]
        reynolds = [Re1/1000, Re2/1000]  # 以千为单位
        
        x_pos = np.arange(len(sections))
        width = 0.35
        
        bars1 = ax3.bar(x_pos - width/2, velocities, width, label='流速 (m/s)',
                       color='lightblue', edgecolor='blue', linewidth=2)
        ax3_twin = ax3.twinx()
        bars2 = ax3_twin.bar(x_pos + width/2, reynolds, width, label='雷诺数 (×10³)',
                            color='lightcoral', edgecolor='red', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars1, velocities):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{val:.2f}m/s', ha='center', fontsize=10, fontweight='bold')
        
        for bar, val, Re in zip(bars2, reynolds, [Re1, Re2]):
            ax3_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(reynolds)*0.05,
                         f'{Re:.0f}', ha='center', fontsize=10, fontweight='bold')
        
        ax3.set_xlabel('管段', fontsize=11, fontweight='bold')
        ax3.set_ylabel('流速 (m/s)', fontsize=11, fontweight='bold', color='blue')
        ax3_twin.set_ylabel('雷诺数', fontsize=11, fontweight='bold', color='red')
        ax3.set_title('流速与雷诺数', fontsize=13, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(sections, fontsize=10)
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='red')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 图4：连接处压强
        ax4 = axes[1, 1]
        
        p_conn, z_conn, _ = self.pressure_at_connection(Q)
        
        # 大气压和连接处压强
        p_atm = 101325
        pressures = ['大气压', '连接处压强']
        values = [p_atm/1000, p_conn/1000]
        colors = ['lightblue', 'lightgreen']
        
        bars = ax4.bar(pressures, values, color=colors, edgecolor='black',
                      linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.03,
                    f'{val:.1f}kPa', ha='center', fontsize=11, fontweight='bold')
        
        ax4.set_ylabel('压强 (kPa)', fontsize=11, fontweight='bold')
        ax4.set_title('连接处压强', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 标注压强性质
        if p_conn > p_atm:
            status = '正压'
            color = 'green'
        else:
            status = '负压'
            color = 'red'
        
        ax4.text(0.5, max(values) * 0.6,
                f'连接处：{status}\np_conn={p_conn/1000:.1f}kPa',
                ha='center', fontsize=11, fontweight='bold', color=color,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("串联管道流量计算")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  管段1：d1={self.d1}m, L1={self.L1}m")
        print(f"  管段2：d2={self.d2}m, L2={self.L2}m")
        print(f"  上游水位：H1={self.H1}m")
        print(f"  下游水位：H2={self.H2}m")
        print(f"  粗糙度：n={self.n}")
        print(f"  局部损失系数：Σζ={self.zeta_sum}")
        
        # (1) 流量
        Q = self.calculate_discharge()
        print(f"\n(1) 通过管道的流量：")
        print(f"  能量方程：H1 = H2 + hf1 + hf2 + hm")
        print(f"  其中：hf = λ(L/d)v²/(2g), hm = Σζv²/(2g)")
        print(f"\n  通过迭代求解，得：")
        print(f"    Q = {Q:.6f} m³/s = {Q*1000:.2f} L/s")
        
        # 各段流速
        v1 = Q / self.A1
        v2 = Q / self.A2
        print(f"\n  各管段流速：")
        print(f"    v1 = Q/A1 = {Q:.6f} / {self.A1:.6f} = {v1:.3f} m/s")
        print(f"    v2 = Q/A2 = {Q:.6f} / {self.A2:.6f} = {v2:.3f} m/s")
        
        # 各段水头损失
        hf1 = self.head_loss_pipe(Q, self.d1, self.L1)
        hf2 = self.head_loss_pipe(Q, self.d2, self.L2)
        hm = self.head_loss_local(Q)
        
        lamb1 = self.friction_factor(self.d1)
        lamb2 = self.friction_factor(self.d2)
        
        print(f"\n  管段1水头损失：")
        print(f"    λ1 = {lamb1:.4f}")
        print(f"    hf1 = {lamb1:.4f} × ({self.L1}/{self.d1}) × {v1:.3f}²/(2×{self.g})")
        print(f"        = {hf1:.3f} m")
        
        print(f"\n  管段2水头损失：")
        print(f"    λ2 = {lamb2:.4f}")
        print(f"    hf2 = {lamb2:.4f} × ({self.L2}/{self.d2}) × {v2:.3f}²/(2×{self.g})")
        print(f"        = {hf2:.3f} m")
        
        print(f"\n  局部水头损失：")
        print(f"    hm = {self.zeta_sum} × {v1:.3f}²/(2×{self.g})")
        print(f"       = {hm:.3f} m")
        
        total_loss = hf1 + hf2 + hm
        print(f"\n  总水头损失：")
        print(f"    h_total = {hf1:.3f} + {hf2:.3f} + {hm:.3f} = {total_loss:.3f} m")
        
        # 验证
        H_diff = self.H1 - self.H2
        print(f"\n  验证：H1 - H2 = {self.H1} - {self.H2} = {H_diff:.1f} m")
        print(f"        h_total = {total_loss:.3f} m")
        print(f"        误差：{abs(H_diff - total_loss):.4f} m ✓")
        
        # (2) 连接处压强
        p_conn, z_conn, _ = self.pressure_at_connection(Q)
        print(f"\n(2) 连接处压强：")
        print(f"  从上游到连接处能量方程：")
        print(f"    H1 = z_conn + p_conn/(ρg) + v1²/(2g) + hf1 + hm1")
        print(f"  p_conn = ρg × [H1 - z_conn - v1²/(2g) - hf1 - hm1]")
        print(f"         = {self.rho} × {self.g} × [...] ")
        print(f"         = {p_conn:.0f} Pa = {p_conn/1000:.1f} kPa")
        
        if p_conn > 101325:
            print(f"  判断：p_conn > p_atm，为正压")
        else:
            print(f"  判断：p_conn < p_atm，为负压（真空）")
        
        # (3) 雷诺数
        Re1 = self.reynolds_number(Q, self.d1)
        Re2 = self.reynolds_number(Q, self.d2)
        
        print(f"\n(3) 各管段雷诺数：")
        print(f"  Re1 = v1·d1/ν = {v1:.3f} × {self.d1} / 1e-6 = {Re1:.0f}")
        print(f"  Re2 = v2·d2/ν = {v2:.3f} × {self.d2} / 1e-6 = {Re2:.0f}")
        
        for i, Re in enumerate([Re1, Re2], 1):
            if Re > 4000:
                status = "紊流"
            elif Re < 2000:
                status = "层流"
            else:
                status = "过渡流"
            print(f"  管段{i}：{status}")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 串联管道：流量相同，水头损失相加")
        print("2. 能量方程：H1 = H2 + Σhf + Σhm")
        print("3. 流速关系：v1/v2 = (d2/d1)²")
        print("4. 连接处压强：用能量方程从上游推导")
        print("5. 雷诺数判别：Re>4000紊流，Re<2000层流")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第02章 流体动力学基础 - 题目12：管道流量计算")
    print("💧" * 35 + "\n")
    
    # 题目参数
    d1 = 0.3        # 管段1直径0.3m
    L1 = 200.0      # 管段1长度200m
    d2 = 0.2        # 管段2直径0.2m
    L2 = 150.0      # 管段2长度150m
    H1 = 10.0       # 上游水位10m
    H2 = 2.0        # 下游水位2m
    n = 0.012       # 粗糙度
    zeta_sum = 3.5  # 局部损失系数
    
    # 创建串联管道对象
    pipe_system = SeriesPipeFlow(d1=d1, L1=L1, d2=d2, L2=L2,
                                 H1=H1, H2=H2, n=n, zeta_sum=zeta_sum)
    
    # 打印结果
    pipe_system.print_results()
    
    # 绘图
    print("\n正在绘制管道系统分析图...")
    pipe_system.plot_system_diagram()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
