#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第02章 流体动力学基础 - 题目15：综合应用（供水系统设计）

题目描述：
某城市供水系统，从水库（标高H0=50m）向用户（标高H1=10m）供水。
输水管道d=0.4m，长度L=2000m，粗糙度n=0.012。
要求供水流量Q=0.15m³/s，用户处压强不低于p_min=150kPa。
求：
(1) 自流供水是否可行？
(2) 若需加压泵站，泵站应提供的扬程H_pump
(3) 泵站功率P（泵效率η=0.75）
(4) 优化建议（改变管径）

知识点：
- 能量方程综合应用
- 水泵扬程计算
- 功率计算
- 管道优化设计

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class WaterSupplySystem:
    """供水系统综合分析类"""
    
    def __init__(self, H0: float, H1: float, d: float, L: float, Q: float,
                 p_min: float, n: float = 0.012, rho: float = 1000.0, g: float = 9.81):
        """
        初始化参数
        
        Parameters:
        -----------
        H0 : float
            水库水位 (m)
        H1 : float
            用户标高 (m)
        d : float
            管道直径 (m)
        L : float
            管道长度 (m)
        Q : float
            设计流量 (m³/s)
        p_min : float
            用户最小压强 (Pa)
        n : float
            粗糙度系数
        rho : float
            密度 (kg/m³)
        g : float
            重力加速度 (m/s²)
        """
        self.H0 = H0
        self.H1 = H1
        self.d = d
        self.L = L
        self.Q = Q
        self.p_min = p_min
        self.n = n
        self.rho = rho
        self.g = g
        
        # 计算断面面积
        self.A = np.pi * d**2 / 4
    
    def velocity(self) -> float:
        """计算流速"""
        return self.Q / self.A
    
    def friction_factor(self) -> float:
        """计算摩擦系数"""
        R = self.d / 4
        lamb = 8 * self.g * self.n**2 / R**(1/3)
        return lamb
    
    def head_loss(self) -> float:
        """
        计算水头损失
        
        Returns:
        --------
        float : 总水头损失 (m)
        """
        v = self.velocity()
        lamb = self.friction_factor()
        
        # 沿程损失
        hf = lamb * (self.L / self.d) * v**2 / (2 * self.g)
        
        # 局部损失（假设为沿程损失的10%）
        hm = 0.1 * hf
        
        return hf + hm
    
    def required_pressure_head(self) -> float:
        """
        计算用户处所需压强水头
        
        Returns:
        --------
        float : 压强水头 (m)
        """
        return self.p_min / (self.rho * self.g)
    
    def check_gravity_flow(self) -> tuple:
        """
        检查自流供水是否可行
        
        Returns:
        --------
        tuple : (is_feasible, H_available, H_required)
        """
        h_loss = self.head_loss()
        p_head = self.required_pressure_head()
        
        # 可用水头
        H_available = self.H0 - self.H1
        
        # 所需水头
        H_required = h_loss + p_head
        
        is_feasible = H_available >= H_required
        
        return is_feasible, H_available, H_required
    
    def pump_head(self) -> float:
        """
        计算所需泵扬程
        
        Returns:
        --------
        float : 泵扬程 (m)
        """
        _, H_available, H_required = self.check_gravity_flow()
        
        if H_available >= H_required:
            return 0
        else:
            return H_required - H_available
    
    def pump_power(self, eta: float = 0.75) -> tuple:
        """
        计算泵功率
        
        Parameters:
        -----------
        eta : float
            泵效率
            
        Returns:
        --------
        tuple : (P_water, P_shaft)
            P_water : 水功率 (W)
            P_shaft : 轴功率 (W)
        """
        H_pump = self.pump_head()
        
        # 水功率
        P_water = self.rho * self.g * self.Q * H_pump
        
        # 轴功率
        P_shaft = P_water / eta
        
        return P_water, P_shaft
    
    def optimize_diameter(self, d_range: tuple = (0.3, 0.6), n_points: int = 20) -> tuple:
        """
        优化管径
        
        Parameters:
        -----------
        d_range : tuple
            管径范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (d_opt, H_pump_min, diameters, pump_heads)
        """
        diameters = np.linspace(d_range[0], d_range[1], n_points)
        pump_heads = []
        
        original_d = self.d
        original_A = self.A
        
        for d in diameters:
            self.d = d
            self.A = np.pi * d**2 / 4
            
            H_pump = self.pump_head()
            pump_heads.append(H_pump)
        
        # 恢复原值
        self.d = original_d
        self.A = original_A
        
        # 找到最优管径
        idx_min = np.argmin(pump_heads)
        d_opt = diameters[idx_min]
        H_pump_min = pump_heads[idx_min]
        
        return d_opt, H_pump_min, diameters, pump_heads
    
    def plot_system_analysis(self):
        """绘制供水系统分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 图1：系统示意图和能量线
        ax1 = axes[0, 0]
        
        # 水库
        ax1.add_patch(plt.Rectangle((-50, 0), 40, self.H0,
                                    facecolor='lightblue', edgecolor='black',
                                    linewidth=2, alpha=0.7))
        ax1.plot([-50, -10], [self.H0, self.H0], 'b-', linewidth=2)
        ax1.text(-30, self.H0 + 2, f'水库\nH0={self.H0}m', ha='center',
                fontsize=11, fontweight='bold')
        
        # 管道
        y_pipe = self.H1 + 5
        ax1.plot([0, self.L/10], [self.H0 - 5, y_pipe], 'k-', linewidth=4,
                label=f'管道: d={self.d}m, L={self.L}m')
        
        # 用户
        ax1.add_patch(plt.Rectangle((self.L/10, self.H1 - 5), 20, 10,
                                    facecolor='lightgray', edgecolor='black',
                                    linewidth=2))
        ax1.text(self.L/10 + 10, self.H1, '用户', ha='center',
                fontsize=11, fontweight='bold')
        ax1.plot([self.L/10, self.L/10 + 20], [self.H1, self.H1], 'r--', linewidth=2)
        ax1.text(self.L/10 + 30, self.H1, f'H1={self.H1}m', fontsize=10, fontweight='bold')
        
        # 能量线
        h_loss = self.head_loss()
        p_head = self.required_pressure_head()
        
        x_energy = [0, self.L/10]
        H_energy = [self.H0, self.H1 + p_head]
        ax1.plot(x_energy, H_energy, 'g-', linewidth=3, marker='o',
                markersize=8, label='能量线（自流）')
        
        # 检查是否需要泵
        is_feasible, H_available, H_required = self.check_gravity_flow()
        
        if not is_feasible:
            H_pump = self.pump_head()
            # 加泵后的能量线
            H_energy_pump = [self.H0 + H_pump, self.H1 + p_head]
            ax1.plot(x_energy, H_energy_pump, 'r--', linewidth=3, marker='s',
                    markersize=8, label=f'能量线（加泵，H_pump={H_pump:.1f}m）')
            
            # 泵站位置
            ax1.plot([0], [self.H0], 'r^', markersize=15, label='泵站')
            ax1.annotate('', xy=(0, self.H0 + H_pump), xytext=(0, self.H0),
                        arrowprops=dict(arrowstyle='->', color='red', lw=3))
            ax1.text(5, self.H0 + H_pump/2, f'H_pump={H_pump:.1f}m',
                    fontsize=10, color='red', fontweight='bold')
        
        # 标注水头损失
        ax1.annotate('', xy=(self.L/10, self.H1 + p_head), xytext=(self.L/10, self.H0),
                    arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
        ax1.text(self.L/10 - 20, (self.H0 + self.H1 + p_head)/2,
                f'水头损失\n{h_loss:.1f}m', ha='center',
                fontsize=9, color='blue', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        ax1.set_xlim(-60, self.L/10 + 50)
        ax1.set_ylim(-5, self.H0 + 10 if is_feasible else self.H0 + H_pump + 10)
        ax1.set_xlabel('水平距离 (m)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('高程 (m)', fontsize=11, fontweight='bold')
        ax1.set_title('供水系统示意图', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # 图2：水头平衡分析
        ax2 = axes[0, 1]
        
        items = ['地形高差', '压强水头', '水头损失', '可用水头\n/所需水头']
        values = [self.H0 - self.H1, p_head, h_loss, H_available if is_feasible else H_required]
        colors = ['lightblue', 'lightcoral', 'lightyellow', 'lightgreen']
        
        bars = ax2.bar(items, values, color=colors, edgecolor='black',
                      linewidth=2, alpha=0.8)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.03,
                    f'{val:.1f}m', ha='center', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('水头 (m)', fontsize=11, fontweight='bold')
        ax2.set_title('水头平衡分析', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 标注结论
        if is_feasible:
            conclusion = f'自流可行！\n可用水头 > 所需水头'
            color = 'green'
        else:
            conclusion = f'需加压泵站！\n缺少水头 {H_pump:.1f}m'
            color = 'red'
        
        ax2.text(1.5, max(values) * 0.7, conclusion,
                ha='center', fontsize=11, fontweight='bold', color=color,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 图3：泵功率分析
        ax3 = axes[1, 0]
        
        if not is_feasible:
            eta_range = [0.6, 0.7, 0.75, 0.8, 0.85]
            P_water, _ = self.pump_power(eta=0.75)
            P_shafts = [P_water / eta / 1000 for eta in eta_range]
            
            bars = ax3.bar(range(len(eta_range)), P_shafts, color='lightblue',
                          edgecolor='blue', linewidth=2, alpha=0.8)
            
            # 标注数值
            for i, (bar, P, eta) in enumerate(zip(bars, P_shafts, eta_range)):
                height = bar.get_height()
                ax3.text(i, height + max(P_shafts)*0.03,
                        f'{P:.1f}kW', ha='center', fontsize=10, fontweight='bold')
            
            ax3.set_xticks(range(len(eta_range)))
            ax3.set_xticklabels([f'η={eta:.0%}' for eta in eta_range], fontsize=10)
            ax3.set_ylabel('轴功率 (kW)', fontsize=11, fontweight='bold')
            ax3.set_title('泵功率与效率关系', fontsize=13, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')
            
            # 标注推荐
            ax3.text(2, max(P_shafts) * 0.7,
                    f'推荐效率：η=0.75\n轴功率：{P_shafts[2]:.1f}kW',
                    ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        else:
            ax3.text(0.5, 0.5, '自流供水\n无需泵站',
                    ha='center', va='center', fontsize=16, fontweight='bold',
                    transform=ax3.transAxes,
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
            ax3.set_xlim(0, 1)
            ax3.set_ylim(0, 1)
        
        # 图4：管径优化分析
        ax4 = axes[1, 1]
        
        d_opt, H_pump_min, diameters, pump_heads = self.optimize_diameter()
        
        ax4.plot(diameters * 1000, pump_heads, 'b-', linewidth=2.5, label='泵扬程')
        ax4.plot([self.d * 1000], [self.pump_head()], 'ro', markersize=10,
                label=f'当前设计: d={self.d}m')
        
        if not is_feasible:
            ax4.plot([d_opt * 1000], [H_pump_min], 'g^', markersize=12,
                    label=f'最优设计: d={d_opt:.3f}m')
        
        ax4.set_xlabel('管径 (mm)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('泵扬程 (m)', fontsize=11, fontweight='bold')
        ax4.set_title('管径优化分析', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        # 标注优化建议
        if not is_feasible and d_opt != self.d:
            saving = self.pump_head() - H_pump_min
            ax4.text(450, max(pump_heads) * 0.7,
                    f'优化建议：\n管径从{self.d}m增至{d_opt:.3f}m\n可降低扬程{saving:.1f}m',
                    ha='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("供水系统综合设计")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  水库水位：H0 = {self.H0}m")
        print(f"  用户标高：H1 = {self.H1}m")
        print(f"  管道：d = {self.d}m, L = {self.L}m, n = {self.n}")
        print(f"  设计流量：Q = {self.Q}m³/s = {self.Q*1000:.0f}L/s")
        print(f"  最小压强：p_min = {self.p_min/1000:.0f}kPa")
        
        # 基本计算
        v = self.velocity()
        lamb = self.friction_factor()
        h_loss = self.head_loss()
        p_head = self.required_pressure_head()
        
        print(f"\n基本计算：")
        print(f"  流速：v = Q/A = {self.Q} / {self.A:.5f} = {v:.3f} m/s")
        print(f"  摩擦系数：λ = {lamb:.4f}")
        print(f"  水头损失：h_loss = {h_loss:.2f} m")
        print(f"  所需压强水头：p_head = {p_head:.2f} m")
        
        # (1) 自流可行性
        is_feasible, H_available, H_required = self.check_gravity_flow()
        
        print(f"\n(1) 自流供水可行性分析：")
        print(f"  可用水头：H_available = H0 - H1 = {self.H0} - {self.H1} = {H_available:.1f} m")
        print(f"  所需水头：H_required = h_loss + p_head")
        print(f"                        = {h_loss:.2f} + {p_head:.2f}")
        print(f"                        = {H_required:.2f} m")
        
        if is_feasible:
            print(f"\n  结论：H_available > H_required，自流供水可行！✓")
            print(f"       安全裕度：{H_available - H_required:.2f} m")
        else:
            print(f"\n  结论：H_available < H_required，自流供水不可行！✗")
            print(f"       缺少水头：{H_required - H_available:.2f} m")
        
        # (2) 泵扬程
        H_pump = self.pump_head()
        
        if not is_feasible:
            print(f"\n(2) 所需泵扬程：")
            print(f"  H_pump = H_required - H_available")
            print(f"         = {H_required:.2f} - {H_available:.1f}")
            print(f"         = {H_pump:.2f} m")
            
            # (3) 泵功率
            P_water, P_shaft = self.pump_power(eta=0.75)
            
            print(f"\n(3) 泵站功率（η=0.75）：")
            print(f"  水功率：P_water = ρgQH_pump")
            print(f"                  = {self.rho} × {self.g} × {self.Q} × {H_pump:.2f}")
            print(f"                  = {P_water:.0f} W = {P_water/1000:.2f} kW")
            
            print(f"\n  轴功率：P_shaft = P_water / η")
            print(f"                  = {P_water:.0f} / 0.75")
            print(f"                  = {P_shaft:.0f} W = {P_shaft/1000:.2f} kW")
            
            print(f"\n  选泵建议：选用 {P_shaft/1000*1.1:.1f} kW 的水泵（考虑10%裕度）")
        else:
            print(f"\n(2) 泵扬程：")
            print(f"  不需要泵站，自流即可满足要求")
        
        # (4) 优化建议
        print(f"\n(4) 优化建议：")
        
        d_opt, H_pump_min, _, _ = self.optimize_diameter()
        
        if abs(d_opt - self.d) > 0.01:
            print(f"  当前管径：d = {self.d}m，泵扬程 = {H_pump:.2f}m")
            print(f"  最优管径：d_opt = {d_opt:.3f}m，泵扬程 = {H_pump_min:.2f}m")
            
            if H_pump_min < H_pump:
                print(f"  优化效果：可降低泵扬程 {H_pump - H_pump_min:.2f}m")
                print(f"           年节约电费约 {(H_pump - H_pump_min) * self.Q * self.rho * self.g * 8760 * 0.6 / 1000000:.0f} 元")
                print(f"           （假设年运行8760h，电价0.6元/kWh）")
            
            print(f"\n  建议：增大管径至 {d_opt:.3f}m，可显著降低能耗")
        else:
            print(f"  当前管径 d = {self.d}m 已接近最优值")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. 能量方程：H0 + H_pump = H1 + p/(ρg) + h_loss")
        print("2. 水头损失：h_loss = hf + hm = λ(L/d)v²/(2g) + ζv²/(2g)")
        print("3. 泵功率：P = ρgQH_pump/η")
        print("4. 优化设计：增大管径→降低流速→减少损失→节约能耗")
        print("5. 经济分析：投资成本 vs 运行成本，寻找最优平衡点")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第02章 流体动力学基础 - 题目15：综合应用")
    print("💧" * 35 + "\n")
    
    # 题目参数
    H0 = 50.0       # 水库水位50m
    H1 = 10.0       # 用户标高10m
    d = 0.4         # 管径0.4m
    L = 2000.0      # 长度2000m
    Q = 0.15        # 流量0.15m³/s
    p_min = 150000  # 最小压强150kPa
    n = 0.012       # 粗糙度
    
    # 创建供水系统对象
    system = WaterSupplySystem(H0=H0, H1=H1, d=d, L=L, Q=Q, p_min=p_min, n=n)
    
    # 打印结果
    system.print_results()
    
    # 绘图
    print("\n正在绘制供水系统分析图...")
    system.plot_system_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
