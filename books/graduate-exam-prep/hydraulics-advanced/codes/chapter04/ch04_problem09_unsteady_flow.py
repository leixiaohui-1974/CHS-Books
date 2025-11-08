#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第04章 地下水与渗流 - 题目9：非稳定井流（Theis公式）

题目描述：
某承压含水层，已知：
- 厚度M=12m
- 导水系数T=kM=600m²/d
- 贮水系数S=0.0005
- 抽水流量Q=1000m³/d

求：
(1) 抽水t=1h后，r=100m处的降深（Theis公式）
(2) 抽水t=10h后的降深
(3) 停抽后水位恢复情况
(4) 降深随时间变化曲线

知识点：
- Theis公式
- 井函数W(u)
- 非稳定井流
- 水位恢复

作者：CHS-Books Team
日期：2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import exp1

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class UnsteadyWellFlow:
    """非稳定井流分析类（Theis公式）"""
    
    def __init__(self, M: float, T: float, S: float, Q: float):
        """
        初始化参数
        
        Parameters:
        -----------
        M : float
            含水层厚度 (m)
        T : float
            导水系数 (m²/d)
        S : float
            贮水系数
        Q : float
            抽水流量 (m³/d)
        """
        self.M = M
        self.T = T
        self.S = S
        self.Q = Q
    
    def well_function(self, u: float) -> float:
        """
        计算Theis井函数W(u)
        
        W(u) = ∫[u,∞] e^(-y)/y dy = E1(u)
        
        Parameters:
        -----------
        u : float
            无量纲参数 u = r²S/(4Tt)
            
        Returns:
        --------
        float : 井函数值
        """
        if u <= 0:
            return 0
        return exp1(u)  # scipy的指数积分函数
    
    def calculate_u(self, r: float, t: float) -> float:
        """
        计算无量纲参数u
        
        u = r²S/(4Tt)
        
        Parameters:
        -----------
        r : float
            距井轴距离 (m)
        t : float
            时间 (d)
            
        Returns:
        --------
        float : u值
        """
        if t <= 0:
            return np.inf
        return r**2 * self.S / (4 * self.T * t)
    
    def drawdown_theis(self, r: float, t: float) -> float:
        """
        用Theis公式计算降深
        
        s = Q/(4πT) * W(u)
        
        Parameters:
        -----------
        r : float
            距井轴距离 (m)
        t : float
            时间 (d)
            
        Returns:
        --------
        float : 降深 (m)
        """
        u = self.calculate_u(r, t)
        Wu = self.well_function(u)
        return self.Q / (4 * np.pi * self.T) * Wu
    
    def drawdown_jacob(self, r: float, t: float) -> float:
        """
        用Jacob近似公式计算降深（大时间）
        
        s ≈ Q/(4πT) * [ln(2.25Tt/(r²S))]
        
        适用条件：u < 0.01
        
        Parameters:
        -----------
        r : float
            距井轴距离 (m)
        t : float
            时间 (d)
            
        Returns:
        --------
        float : 降深 (m)
        """
        if t <= 0:
            return 0
        return self.Q / (4 * np.pi * self.T) * np.log(2.25 * self.T * t / (r**2 * self.S))
    
    def recovery(self, r: float, t_pump: float, t_rest: float) -> float:
        """
        计算停抽后的水位恢复（叠加原理）
        
        s_残 = s_抽水(t_总) - s_回灌(t_停)
        
        Parameters:
        -----------
        r : float
            距井轴距离 (m)
        t_pump : float
            抽水时间 (d)
        t_rest : float
            停抽后休止时间 (d)
            
        Returns:
        --------
        float : 剩余降深 (m)
        """
        # 总时间
        t_total = t_pump + t_rest
        
        # 抽水作用
        s_pump = self.drawdown_theis(r, t_total)
        
        # 回灌作用（等效于负的抽水）
        s_inject = self.drawdown_theis(r, t_rest)
        
        # 剩余降深
        return s_pump - s_inject
    
    def time_drawdown_curve(self, r: float, t_range: tuple = (0.01, 10), 
                           n_points: int = 100) -> tuple:
        """
        计算某点降深随时间变化
        
        Parameters:
        -----------
        r : float
            距井轴距离 (m)
        t_range : tuple
            时间范围 (d)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (t_array, s_array, u_array)
        """
        t_array = np.logspace(np.log10(t_range[0]), np.log10(t_range[1]), n_points)
        s_array = np.array([self.drawdown_theis(r, t) for t in t_array])
        u_array = np.array([self.calculate_u(r, t) for t in t_array])
        
        return t_array, s_array, u_array
    
    def distance_drawdown_curve(self, t: float, r_range: tuple = (1, 1000), 
                                n_points: int = 100) -> tuple:
        """
        计算某时刻降深随距离变化
        
        Parameters:
        -----------
        t : float
            时间 (d)
        r_range : tuple
            距离范围 (m)
        n_points : int
            计算点数
            
        Returns:
        --------
        tuple : (r_array, s_array)
        """
        r_array = np.logspace(np.log10(r_range[0]), np.log10(r_range[1]), n_points)
        s_array = np.array([self.drawdown_theis(r, t) for r in r_array])
        
        return r_array, s_array
    
    def plot_analysis(self):
        """绘制非稳定井流分析图"""
        fig = plt.figure(figsize=(16, 12))
        
        # 图1：Theis井函数曲线
        ax1 = plt.subplot(3, 3, 1)
        
        u_values = np.logspace(-4, 2, 100)
        Wu_values = np.array([self.well_function(u) for u in u_values])
        
        ax1.loglog(u_values, Wu_values, 'b-', linewidth=2.5, label='W(u)')
        
        # 标注特殊点
        u_special = [0.01, 0.05, 0.1, 1, 10]
        for u in u_special:
            Wu = self.well_function(u)
            ax1.plot([u], [Wu], 'ro', markersize=8)
            ax1.text(u * 1.2, Wu, f'u={u}\nW(u)={Wu:.2f}',
                    fontsize=8)
        
        ax1.set_xlabel('u = r²S/(4Tt)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('W(u)井函数', fontsize=11, fontweight='bold')
        ax1.set_title('Theis井函数曲线', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3, which='both')
        
        # 图2：降深随时间变化（r=100m）
        ax2 = plt.subplot(3, 3, 2)
        
        r_fixed = 100  # m
        t_array, s_theis, u_array = self.time_drawdown_curve(r_fixed, t_range=(0.01/24, 10))
        
        # Theis公式
        ax2.semilogx(t_array * 24, s_theis, 'b-', linewidth=2.5, label='Theis公式')
        
        # Jacob近似（u<0.01时）
        s_jacob = np.array([self.drawdown_jacob(r_fixed, t) if self.calculate_u(r_fixed, t) < 0.01 
                           else np.nan for t in t_array])
        ax2.semilogx(t_array * 24, s_jacob, 'r--', linewidth=2, label='Jacob近似')
        
        # 标注t=1h和t=10h
        t_1h = 1/24
        t_10h = 10/24
        s_1h = self.drawdown_theis(r_fixed, t_1h)
        s_10h = self.drawdown_theis(r_fixed, t_10h)
        
        ax2.plot([1], [s_1h], 'go', markersize=12, label=f't=1h, s={s_1h:.3f}m')
        ax2.plot([10], [s_10h], 'mo', markersize=12, label=f't=10h, s={s_10h:.3f}m')
        
        ax2.set_xlabel('时间 t (h)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('降深 s (m)', fontsize=11, fontweight='bold')
        ax2.set_title(f'降深随时间变化（r={r_fixed}m）', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, which='both')
        
        # 图3：降深随距离变化
        ax3 = plt.subplot(3, 3, 3)
        
        t_values = [0.1/24, 1/24, 10/24, 1, 10]  # d
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        for t, color in zip(t_values, colors):
            r_array, s_array = self.distance_drawdown_curve(t, r_range=(1, 500))
            label = f't={t*24:.1f}h' if t < 1 else f't={t:.1f}d'
            ax3.semilogx(r_array, s_array, linewidth=2, color=color, label=label)
        
        ax3.set_xlabel('距井轴距离 r (m)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('降深 s (m)', fontsize=11, fontweight='bold')
        ax3.set_title('降深随距离变化', fontsize=13, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, which='both')
        
        # 图4：u值随时间变化
        ax4 = plt.subplot(3, 3, 4)
        
        ax4.loglog(t_array * 24, u_array, 'b-', linewidth=2.5, label='u(t)')
        ax4.axhline(y=0.01, color='r', linestyle='--', linewidth=2,
                   label='u=0.01（Jacob近似界限）')
        
        # 标注
        ax4.fill_between([min(t_array)*24, max(t_array)*24], 0, 0.01,
                        color='lightgreen', alpha=0.3, label='Jacob近似适用区')
        
        ax4.set_xlabel('时间 t (h)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('u = r²S/(4Tt)', fontsize=11, fontweight='bold')
        ax4.set_title('u值随时间变化', fontsize=13, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, which='both')
        
        # 图5：水位恢复曲线
        ax5 = plt.subplot(3, 3, 5)
        
        t_pump = 10/24  # 抽水10h
        t_rest_array = np.linspace(0, t_pump * 3, 50)
        s_recovery = np.array([self.recovery(r_fixed, t_pump, t_rest) for t_rest in t_rest_array])
        
        ax5.plot(t_rest_array * 24, s_recovery, 'b-', linewidth=2.5, label='剩余降深')
        ax5.axhline(y=s_10h, color='r', linestyle='--', linewidth=1.5,
                   label=f'停抽前降深={s_10h:.3f}m')
        
        # 标注停抽10h后
        s_after_10h = self.recovery(r_fixed, t_pump, t_pump)
        ax5.plot([10], [s_after_10h], 'go', markersize=12,
                label=f'停抽10h后: s={s_after_10h:.3f}m')
        
        ax5.set_xlabel('停抽后时间 (h)', fontsize=11, fontweight='bold')
        ax5.set_ylabel('剩余降深 s (m)', fontsize=11, fontweight='bold')
        ax5.set_title(f'水位恢复曲线（r={r_fixed}m）', fontsize=13, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 图6：Theis vs Jacob对比
        ax6 = plt.subplot(3, 3, 6)
        
        r_compare = [10, 50, 100, 200]
        t_compare = np.logspace(-2, 1, 50)
        
        for r in r_compare:
            s_theis_comp = np.array([self.drawdown_theis(r, t) for t in t_compare])
            s_jacob_comp = np.array([self.drawdown_jacob(r, t) if self.calculate_u(r, t) < 0.01 
                                    else np.nan for t in t_compare])
            
            ax6.semilogx(t_compare * 24, s_theis_comp, '-', linewidth=2, label=f'r={r}m (Theis)')
            ax6.semilogx(t_compare * 24, s_jacob_comp, '--', linewidth=1.5, alpha=0.7)
        
        ax6.set_xlabel('时间 t (h)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('降深 s (m)', fontsize=11, fontweight='bold')
        ax6.set_title('Theis公式 vs Jacob近似', fontsize=13, fontweight='bold')
        ax6.legend(fontsize=8, ncol=2)
        ax6.grid(True, alpha=0.3, which='both')
        
        # 图7：参数影响分析
        ax7 = plt.subplot(3, 3, 7)
        
        # 贮水系数影响
        S_values = [0.0001, 0.0005, 0.001, 0.005]
        t_param = 1/24  # 1小时
        
        for S_val in S_values:
            original_S = self.S
            self.S = S_val
            r_param = np.logspace(0, 2.5, 50)
            s_param = np.array([self.drawdown_theis(r, t_param) for r in r_param])
            ax7.semilogx(r_param, s_param, linewidth=2, label=f'S={S_val}')
            self.S = original_S
        
        ax7.set_xlabel('距离 r (m)', fontsize=11, fontweight='bold')
        ax7.set_ylabel('降深 s (m)', fontsize=11, fontweight='bold')
        ax7.set_title('贮水系数的影响（t=1h）', fontsize=13, fontweight='bold')
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3, which='both')
        
        # 图8：参数汇总
        ax8 = plt.subplot(3, 3, 8)
        
        params_text = f"""
非稳定井流计算结果

【基本参数】
厚度 M = {self.M} m
导水系数 T = {self.T} m²/d
贮水系数 S = {self.S}
抽水流量 Q = {self.Q} m³/d

【计算点】r = {r_fixed} m

【结果】
t = 1h:
  u = {self.calculate_u(r_fixed, t_1h):.4f}
  s = {s_1h:.4f} m

t = 10h:
  u = {self.calculate_u(r_fixed, t_10h):.4f}
  s = {s_10h:.4f} m

停抽10h后:
  剩余降深 = {s_after_10h:.4f} m
  恢复率 = {(1-s_after_10h/s_10h)*100:.1f}%
"""
        
        ax8.text(0.1, 0.5, params_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax8.axis('off')
        ax8.set_title('计算结果汇总', fontsize=13, fontweight='bold')
        
        # 图9：公式总结
        ax9 = plt.subplot(3, 3, 9)
        
        formula_text = """
Theis公式

【基本公式】
s = Q/(4πT) · W(u)

u = r²S/(4Tt)

【井函数】
W(u) = -0.5772 - ln(u) + u - u²/(2·2!) + ...

【Jacob近似】（u < 0.01）
s ≈ Q/(4πT) · ln(2.25Tt/(r²S))

【水位恢复】
s_残 = s_抽(t_总) - s_回(t_停)

【适用条件】
• 承压含水层
• 完整井
• 无限含水层
• 各向同性
"""
        
        ax9.text(0.1, 0.5, formula_text, fontsize=9, fontfamily='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax9.axis('off')
        ax9.set_title('公式总结', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 70)
        print("非稳定井流计算（Theis公式）")
        print("=" * 70)
        
        print(f"\n输入参数：")
        print(f"  含水层厚度：M = {self.M} m")
        print(f"  导水系数：T = kM = {self.T} m²/d")
        print(f"  贮水系数：S = {self.S}")
        print(f"  抽水流量：Q = {self.Q} m³/d = {self.Q/86.4:.2f} L/s")
        
        # 计算点
        r = 100  # m
        t_1h = 1/24  # d
        t_10h = 10/24  # d
        
        print(f"\n计算点：r = {r} m")
        
        # (1) t=1h
        u_1h = self.calculate_u(r, t_1h)
        Wu_1h = self.well_function(u_1h)
        s_1h = self.drawdown_theis(r, t_1h)
        
        print(f"\n(1) t = 1 h时的降深：")
        print(f"  Theis公式：")
        print(f"    s = Q/(4πT) · W(u)")
        
        print(f"\n  计算u：")
        print(f"    u = r²S/(4Tt)")
        print(f"      = {r}² × {self.S} / (4 × {self.T} × {t_1h:.6f})")
        print(f"      = {r**2 * self.S:.2f} / {4 * self.T * t_1h:.2f}")
        print(f"      = {u_1h:.6f}")
        
        print(f"\n  计算W(u)：")
        print(f"    使用scipy.special.exp1函数")
        print(f"    W({u_1h:.6f}) = {Wu_1h:.4f}")
        
        print(f"\n  计算降深：")
        print(f"    s = {self.Q}/(4π×{self.T}) × {Wu_1h:.4f}")
        print(f"      = {self.Q/(4*np.pi*self.T):.4f} × {Wu_1h:.4f}")
        print(f"      = {s_1h:.4f} m")
        
        # (2) t=10h
        u_10h = self.calculate_u(r, t_10h)
        Wu_10h = self.well_function(u_10h)
        s_10h = self.drawdown_theis(r, t_10h)
        
        print(f"\n(2) t = 10 h时的降深：")
        print(f"  u = {r}² × {self.S} / (4 × {self.T} × {t_10h:.6f})")
        print(f"    = {u_10h:.6f}")
        print(f"  W(u) = {Wu_10h:.4f}")
        print(f"  s = {s_10h:.4f} m")
        
        print(f"\n  与t=1h对比：")
        print(f"    降深增加：Δs = {s_10h - s_1h:.4f} m")
        print(f"    增加率：{(s_10h/s_1h - 1)*100:.1f}%")
        
        # Jacob近似
        if u_10h < 0.01:
            s_jacob = self.drawdown_jacob(r, t_10h)
            print(f"\n  Jacob近似（u < 0.01）：")
            print(f"    s ≈ Q/(4πT) · ln(2.25Tt/(r²S))")
            print(f"      = {s_jacob:.4f} m")
            print(f"    误差：{abs(s_jacob - s_10h)/s_10h*100:.2f}%")
        
        # (3) 停抽后恢复
        t_rest = 10/24  # 停抽10h
        s_remain = self.recovery(r, t_10h, t_rest)
        recovery_rate = (1 - s_remain/s_10h) * 100
        
        print(f"\n(3) 停抽后水位恢复：")
        print(f"  抽水时间：t_抽 = 10 h")
        print(f"  停抽时间：t_停 = 10 h")
        
        print(f"\n  叠加原理：")
        print(f"    s_残 = s_抽(t_总) - s_回(t_停)")
        
        print(f"\n  总时间效应（持续抽水）：")
        t_total = t_10h + t_rest
        s_total = self.drawdown_theis(r, t_total)
        print(f"    t_总 = 20 h")
        print(f"    s_抽(20h) = {s_total:.4f} m")
        
        print(f"\n  回灌效应（停抽10h）：")
        s_inject = self.drawdown_theis(r, t_rest)
        print(f"    s_回(10h) = {s_inject:.4f} m")
        
        print(f"\n  剩余降深：")
        print(f"    s_残 = {s_total:.4f} - {s_inject:.4f}")
        print(f"        = {s_remain:.4f} m")
        
        print(f"\n  恢复情况：")
        print(f"    停抽前降深：{s_10h:.4f} m")
        print(f"    停抽10h后：{s_remain:.4f} m")
        print(f"    恢复了：{s_10h - s_remain:.4f} m")
        print(f"    恢复率：{recovery_rate:.1f}%")
        
        # (4) 时间变化
        print(f"\n(4) 降深随时间变化特征：")
        
        times = [0.1, 0.5, 1, 2, 5, 10, 24, 48]  # h
        print(f"\n  {'时间(h)':<10} {'u':<15} {'W(u)':<15} {'降深s(m)':<15}")
        print(f"  {'-'*55}")
        
        for t_h in times:
            t_d = t_h / 24
            u = self.calculate_u(r, t_d)
            Wu = self.well_function(u)
            s = self.drawdown_theis(r, t_d)
            print(f"  {t_h:<10.1f} {u:<15.6f} {Wu:<15.4f} {s:<15.4f}")
        
        print(f"\n  特征：")
        print(f"    • 初期降深快")
        print(f"    • 后期趋缓")
        print(f"    • 对数关系")
        print(f"    • 无稳定值")
        
        print("\n" + "=" * 70)
        print("考试要点：")
        print("=" * 70)
        print("1. Theis公式：s = Q/(4πT)·W(u)")
        print("2. 无量纲参数：u = r²S/(4Tt)")
        print("3. Jacob近似：u<0.01时可用")
        print("4. 叠加原理：用于水位恢复计算")
        print("5. 非稳定特征：随时间持续增长")
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "💧" * 35)
    print("第04章 地下水与渗流 - 题目9：非稳定井流（Theis公式）")
    print("💧" * 35 + "\n")
    
    # 题目参数
    M = 12.0          # 含水层厚度12m
    T = 600.0         # 导水系数600m²/d
    S = 0.0005        # 贮水系数0.0005
    Q = 1000.0        # 抽水流量1000m³/d
    
    # 创建非稳定井流对象
    unsteady = UnsteadyWellFlow(M=M, T=T, S=S, Q=Q)
    
    # 打印结果
    unsteady.print_results()
    
    # 绘图
    print("\n正在绘制非稳定井流分析图...")
    unsteady.plot_analysis()
    
    print("\n✅ 计算完成！")


if __name__ == "__main__":
    main()
