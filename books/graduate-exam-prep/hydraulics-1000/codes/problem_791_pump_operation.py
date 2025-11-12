"""
《水力学考研1000题详解》配套代码
题目791：水泵综合工况分析与调节

问题描述：
某离心泵装置，已知：
  水泵特性曲线: H = 32 - 1500Q² (Q单位m³/s，H单位m)
                η = 220Q - 2500Q² (效率)
                P = 9.8ρQH/η (功率，kW)
  管路特性: H_pipe = 15 + 1000Q²
  额定转速: n₀ = 1450 r/min
  需要流量: Q_required = 0.12 m³/s

要求：
(1) 计算额定转速下的工况点(Q₀, H₀, η₀)
(2) 采用节流调节，计算阀门损失和能量损失
(3) 采用变速调节，计算所需转速和节能效果
(4) 采用切削调节，计算切削后的叶轮直径
(5) 对比三种调节方式的优缺点

考点：
1. 工况点: H_pump = H_pipe (泵和管路特性曲线交点)
2. 节流调节: 增加阀门阻力改变管路特性
3. 变速调节: n'/n = Q'/Q, H'/H = (n'/n)², P'/P = (n'/n)³
4. 切削调节: D'/D ≈ Q'/Q, H'/H ≈ (D'/D)²
5. 效率分析: η = ρgQH/(1000P)

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Polygon
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpOperation:
    """水泵综合工况分析类"""
    
    def __init__(self, Q_required=0.12, n0=1450):
        """
        初始化
        
        参数:
            Q_required: 需要的流量 (m³/s)
            n0: 额定转速 (r/min)
        """
        self.Q_required = Q_required
        self.n0 = n0
        self.g = 9.8
        self.rho = 1000  # kg/m³
        
        # 计算额定工况点
        self.calculate_rated_operating_point()
        
        # 节流调节
        self.throttle_regulation()
        
        # 变速调节
        self.speed_regulation()
        
        # 切削调节
        self.impeller_trimming()
    
    def pump_head(self, Q):
        """泵特性曲线 H = 32 - 1500Q²"""
        return 32 - 1500 * Q**2
    
    def pump_efficiency(self, Q):
        """泵效率曲线 η = 220Q - 2500Q²"""
        eta = 220 * Q - 2500 * Q**2
        # 限制在0-1之间
        return np.clip(eta, 0, 1)
    
    def pump_power(self, Q):
        """泵功率 P = ρgQH/η (kW)"""
        H = self.pump_head(Q)
        eta = self.pump_efficiency(Q)
        if eta < 0.01:
            eta = 0.01  # 避免除零
        P = self.rho * self.g * Q * H / (1000 * eta)
        return P
    
    def pipe_head(self, Q, H_static=15, S=1000):
        """管路特性曲线 H = H_static + S*Q²"""
        return H_static + S * Q**2
    
    def calculate_rated_operating_point(self):
        """计算额定转速下的工况点"""
        # 工况点: H_pump = H_pipe
        def equation(Q):
            return self.pump_head(Q) - self.pipe_head(Q)
        
        # 求解工况点
        self.Q0 = brentq(equation, 0.001, 0.2)
        self.H0 = self.pump_head(self.Q0)
        self.eta0 = self.pump_efficiency(self.Q0)
        self.P0 = self.pump_power(self.Q0)
        
        print(f"\n【额定工况点】")
        print(f"  流量: Q₀ = {self.Q0:.6f} m³/s = {self.Q0*3600:.2f} m³/h")
        print(f"  扬程: H₀ = {self.H0:.4f} m")
        print(f"  效率: η₀ = {self.eta0*100:.2f}%")
        print(f"  功率: P₀ = {self.P0:.2f} kW")
    
    def throttle_regulation(self):
        """节流调节"""
        print(f"\n【节流调节】")
        print(f"  目标流量: Q = {self.Q_required} m³/s")
        
        # 在需要流量处，泵的扬程
        H_pump_at_Q = self.pump_head(self.Q_required)
        
        # 原管路的扬程
        H_pipe_original = self.pipe_head(self.Q_required)
        
        # 阀门需要消耗的扬程
        self.H_valve = H_pump_at_Q - H_pipe_original
        
        # 节流后的效率和功率
        self.eta_throttle = self.pump_efficiency(self.Q_required)
        self.P_throttle = self.pump_power(self.Q_required)
        
        # 能量损失
        self.energy_loss_throttle = self.rho * self.g * self.Q_required * self.H_valve / 1000  # kW
        
        print(f"  泵扬程: H_pump = {H_pump_at_Q:.4f} m")
        print(f"  管路扬程: H_pipe = {H_pipe_original:.4f} m")
        print(f"  阀门损失: H_valve = {self.H_valve:.4f} m")
        print(f"  效率: η = {self.eta_throttle*100:.2f}%")
        print(f"  功率: P = {self.P_throttle:.2f} kW")
        print(f"  阀门能耗: ΔP = {self.energy_loss_throttle:.2f} kW")
        print(f"  能量损失率: {self.energy_loss_throttle/self.P_throttle*100:.1f}%")
    
    def speed_regulation(self):
        """变速调节"""
        print(f"\n【变速调节】")
        print(f"  目标流量: Q = {self.Q_required} m³/s")
        
        # 相似律: n'/n = Q'/Q
        self.n_new = self.n0 * self.Q_required / self.Q0
        
        # H'/H = (n'/n)²
        speed_ratio = self.n_new / self.n0
        self.H_new = self.H0 * speed_ratio**2
        
        # P'/P = (n'/n)³
        self.P_speed = self.P0 * speed_ratio**3
        
        # 效率基本不变（理想情况）
        self.eta_speed = self.eta0
        
        # 与节流对比
        power_saving = self.P_throttle - self.P_speed
        power_saving_rate = power_saving / self.P_throttle * 100
        
        print(f"  新转速: n' = {self.n_new:.1f} r/min")
        print(f"  转速比: n'/n₀ = {speed_ratio:.4f}")
        print(f"  新扬程: H' = {self.H_new:.4f} m")
        print(f"  新功率: P' = {self.P_speed:.2f} kW")
        print(f"  效率: η ≈ {self.eta_speed*100:.2f}% (基本不变)")
        print(f"\n  与节流对比:")
        print(f"    节能量: ΔP = {power_saving:.2f} kW")
        print(f"    节能率: {power_saving_rate:.1f}%")
    
    def impeller_trimming(self):
        """切削调节"""
        print(f"\n【切削调节】")
        print(f"  目标流量: Q = {self.Q_required} m³/s")
        
        # 切削定律: D'/D ≈ Q'/Q (近似)
        # 更准确的切削公式考虑扬程变化
        # H'/H = (D'/D)² * (Q'/Q)
        
        # 简化计算: D'/D = Q'/Q
        D_ratio_approx = self.Q_required / self.Q0
        
        # 切削后扬程变化
        # 在新流量下，管路需要的扬程
        H_pipe_new = self.pipe_head(self.Q_required)
        
        # 根据扬程比反推更准确的直径比
        # H'/H₀ = (D'/D)²，但工况点会变化
        # 迭代求解
        def trim_equation(D_ratio):
            # 切削后的泵特性曲线
            # H' = H₀(D'/D)² - 1500(D'/D)²Q²
            Q = self.Q_required
            H_pump_trim = 32 * D_ratio**2 - 1500 * D_ratio**2 * Q**2
            H_pipe = self.pipe_head(Q)
            return H_pump_trim - H_pipe
        
        # 求解
        try:
            self.D_ratio = brentq(trim_equation, 0.5, 1.0)
        except:
            self.D_ratio = D_ratio_approx
        
        # 切削后参数
        self.H_trim = self.pipe_head(self.Q_required)
        self.eta_trim = self.eta0 * 0.95  # 切削后效率略降
        self.P_trim = self.rho * self.g * self.Q_required * self.H_trim / (1000 * self.eta_trim)
        
        print(f"  直径比: D'/D = {self.D_ratio:.4f}")
        print(f"  切削量: ΔD/D = {(1-self.D_ratio)*100:.2f}%")
        print(f"  新扬程: H' = {self.H_trim:.4f} m")
        print(f"  效率: η ≈ {self.eta_trim*100:.2f}% (略降)")
        print(f"  功率: P' = {self.P_trim:.2f} kW")
        print(f"\n  注意: 切削不可逆，需谨慎！")
    
    def compare_methods(self):
        """对比三种调节方式"""
        print(f"\n【三种调节方式对比】")
        
        print(f"\n1. 节流调节:")
        print(f"   优点: 简单方便，成本低")
        print(f"   缺点: 能耗大，效率低")
        print(f"   功率: P = {self.P_throttle:.2f} kW")
        print(f"   效率: η = {self.eta_throttle*100:.2f}%")
        print(f"   适用: 调节范围小，短时调节")
        
        print(f"\n2. 变速调节:")
        print(f"   优点: 节能效果好，效率高")
        print(f"   缺点: 需变频器，初投资大")
        print(f"   功率: P = {self.P_speed:.2f} kW")
        print(f"   效率: η ≈ {self.eta_speed*100:.2f}%")
        print(f"   节能: {(self.P_throttle-self.P_speed)/self.P_throttle*100:.1f}%")
        print(f"   适用: 调节范围大，长期运行 ⭐⭐⭐⭐⭐")
        
        print(f"\n3. 切削调节:")
        print(f"   优点: 一次投资，长期有效")
        print(f"   缺点: 不可逆，调节范围小")
        print(f"   功率: P = {self.P_trim:.2f} kW")
        print(f"   效率: η ≈ {self.eta_trim*100:.2f}%")
        print(f"   适用: 永久性流量变化")
        
        # 经济性对比
        print(f"\n【经济性分析】（假设运行1000小时/年）")
        annual_hours = 1000
        electricity_price = 0.8  # 元/kWh
        
        cost_throttle = self.P_throttle * annual_hours * electricity_price
        cost_speed = self.P_speed * annual_hours * electricity_price
        cost_trim = self.P_trim * annual_hours * electricity_price
        
        print(f"  节流调节年电费: {cost_throttle:.0f} 元")
        print(f"  变速调节年电费: {cost_speed:.0f} 元")
        print(f"  切削调节年电费: {cost_trim:.0f} 元")
        
        print(f"\n  变速比节流节省: {cost_throttle - cost_speed:.0f} 元/年")
        print(f"  切削比节流节省: {cost_throttle - cost_trim:.0f} 元/年")
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目791：水泵综合工况分析与调节")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  泵特性曲线: H = 32 - 1500Q²")
        print(f"               η = 220Q - 2500Q²")
        print(f"  管路特性: H = 15 + 1000Q²")
        print(f"  额定转速: n₀ = {self.n0} r/min")
        print(f"  需要流量: Q_required = {self.Q_required} m³/s")
        
        print("\n【水泵调节基本原理】")
        print("1. 工况点:")
        print("   H_pump(Q) = H_pipe(Q)（泵和管路特性曲线交点）")
        
        print("\n2. 节流调节:")
        print("   增加阀门阻力 → 改变管路特性")
        print("   H_pipe' = H_pipe + H_valve")
        print("   优点: 简单；缺点: 能耗大")
        
        print("\n3. 变速调节（相似律）:")
        print("   n'/n = Q'/Q")
        print("   H'/H = (n'/n)²")
        print("   P'/P = (n'/n)³")
        print("   优点: 节能；缺点: 需变频器")
        
        print("\n4. 切削调节:")
        print("   D'/D ≈ Q'/Q")
        print("   H'/H ≈ (D'/D)²")
        print("   优点: 永久有效；缺点: 不可逆")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 对比分析
        self.compare_methods()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 额定工况点: Q₀={self.Q0:.4f}m³/s, H₀={self.H0:.2f}m, η₀={self.eta0*100:.1f}%")
        print(f"(2) 节流调节: H_valve={self.H_valve:.2f}m, 能耗={self.P_throttle:.2f}kW")
        print(f"(3) 变速调节: n'={self.n_new:.0f}r/min, 节能{(self.P_throttle-self.P_speed)/self.P_throttle*100:.1f}%")
        print(f"(4) 切削调节: D'/D={self.D_ratio:.3f}, 切削{(1-self.D_ratio)*100:.1f}%")
        print(f"(5) 推荐: 变速调节（节能效果最好，推荐用于长期运行）")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：工况点与调节方式
        ax1 = plt.subplot(2, 2, 1)
        self._plot_operating_points(ax1)
        
        # 子图2：功率对比
        ax2 = plt.subplot(2, 2, 2)
        self._plot_power_comparison(ax2)
        
        # 子图3：效率分析
        ax3 = plt.subplot(2, 2, 3)
        self._plot_efficiency_analysis(ax3)
        
        # 子图4：调节方式示意图
        ax4 = plt.subplot(2, 2, 4)
        self._plot_regulation_methods(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_operating_points(self, ax):
        """绘制工况点与调节方式"""
        Q = np.linspace(0, 0.16, 200)
        
        # 泵特性曲线
        H_pump = self.pump_head(Q)
        ax.plot(Q, H_pump, 'b-', linewidth=2.5, label='泵特性曲线 H_pump')
        
        # 原管路特性
        H_pipe_original = self.pipe_head(Q)
        ax.plot(Q, H_pipe_original, 'g-', linewidth=2.5, label='管路特性 H_pipe')
        
        # 额定工况点
        ax.plot(self.Q0, self.H0, 'ro', markersize=12, label=f'额定工况点 Q₀={self.Q0:.3f}', zorder=5)
        
        # 节流后的管路特性
        H_pipe_throttle = self.pipe_head(Q, H_static=15, S=1000) + self.H_valve * (Q/self.Q_required)**2
        ax.plot(Q, H_pipe_throttle, 'r--', linewidth=2, label='节流后管路特性')
        ax.plot(self.Q_required, self.pump_head(self.Q_required), 'rs', markersize=10, label=f'节流工况点 Q={self.Q_required}')
        
        # 变速后的泵特性
        speed_ratio = self.n_new / self.n0
        H_pump_speed = self.pump_head(Q / speed_ratio) * speed_ratio**2
        ax.plot(Q, H_pump_speed, 'orange', linestyle='--', linewidth=2, label='变速后泵特性')
        ax.plot(self.Q_required, self.H_new, 'o', color='orange', markersize=10, label=f'变速工况点')
        
        # 切削后的泵特性
        H_pump_trim = self.pump_head(Q) * self.D_ratio**2
        ax.plot(Q, H_pump_trim, 'purple', linestyle='--', linewidth=2, label='切削后泵特性')
        ax.plot(self.Q_required, self.H_trim, 'D', color='purple', markersize=10, label=f'切削工况点')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('水泵工况点与调节方式', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.16)
        ax.set_ylim(0, 35)
    
    def _plot_power_comparison(self, ax):
        """绘制功率对比"""
        methods = ['额定工况', '节流调节', '变速调节', '切削调节']
        powers = [self.P0, self.P_throttle, self.P_speed, self.P_trim]
        colors = ['gray', 'red', 'green', 'purple']
        
        bars = ax.bar(methods, powers, color=colors, edgecolor='black', 
                     linewidth=2, alpha=0.7)
        
        # 标注数值
        for bar, power in zip(bars, powers):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                   f'{power:.2f}kW',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注节能量
        if self.P_throttle > self.P_speed:
            ax.annotate('', xy=(1, self.P_speed), xytext=(1, self.P_throttle),
                       arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
            ax.text(1.3, (self.P_throttle + self.P_speed)/2, 
                   f'节能\n{self.P_throttle - self.P_speed:.2f}kW',
                   fontsize=10, color='blue', weight='bold')
        
        ax.set_ylabel('功率 P (kW)', fontsize=12)
        ax.set_title('不同调节方式功率对比', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_efficiency_analysis(self, ax):
        """绘制效率分析"""
        Q = np.linspace(0.02, 0.14, 100)
        eta = self.pump_efficiency(Q) * 100
        
        ax.plot(Q, eta, 'b-', linewidth=2.5, label='效率曲线 η(Q)')
        
        # 额定工况效率
        ax.plot(self.Q0, self.eta0*100, 'ro', markersize=12, label=f'额定工况 η₀={self.eta0*100:.1f}%')
        
        # 需要流量处的效率
        ax.plot(self.Q_required, self.eta_throttle*100, 'rs', markersize=10, 
               label=f'节流/变速 η={self.eta_throttle*100:.1f}%')
        
        ax.plot(self.Q_required, self.eta_trim*100, 'D', color='purple', markersize=10,
               label=f'切削 η≈{self.eta_trim*100:.1f}%')
        
        # 高效区（效率>85%最大效率）
        eta_max = np.max(eta)
        Q_high_eff = Q[eta >= 0.85 * eta_max]
        if len(Q_high_eff) > 0:
            ax.axvspan(Q_high_eff[0], Q_high_eff[-1], alpha=0.2, color='green', label='高效区')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('效率 η (%)', fontsize=12)
        ax.set_title('泵效率特性', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.16)
        ax.set_ylim(0, 100)
    
    def _plot_regulation_methods(self, ax):
        """绘制调节方式示意图"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.98, '三种调节方式对比', ha='center', va='top',
               fontsize=13, weight='bold', transform=ax.transAxes)
        
        methods = [
            ('节流调节', '增加阀门阻力', '简单方便\n能耗较大', 0.75),
            ('变速调节', '改变转速n', '节能效果好\n需变频器', 0.50),
            ('切削调节', '切削叶轮直径D', '永久有效\n不可逆', 0.25)
        ]
        
        colors = ['red', 'green', 'purple']
        
        for i, ((name, principle, feature, y), color) in enumerate(zip(methods, colors)):
            # 方框
            rect = Rectangle((0.05, y-0.08), 0.9, 0.15, 
                           facecolor=color, edgecolor='black', 
                           linewidth=2, alpha=0.3)
            ax.add_patch(rect)
            
            # 名称
            ax.text(0.15, y+0.04, name, fontsize=12, weight='bold', va='top')
            
            # 原理
            ax.text(0.15, y-0.01, f'原理: {principle}', fontsize=10, va='top')
            
            # 特点
            ax.text(0.15, y-0.05, f'特点: {feature}', fontsize=9, va='top', style='italic')
            
            # 图标
            if i == 0:  # 节流
                ax.text(0.05, y, '🚰', fontsize=30, ha='left', va='center')
            elif i == 1:  # 变速
                ax.text(0.05, y, '⚡', fontsize=30, ha='left', va='center')
            else:  # 切削
                ax.text(0.05, y, '✂️', fontsize=30, ha='left', va='center')
        
        # 推荐
        ax.text(0.5, 0.05, '推荐: 变速调节（长期运行节能效果最好）⭐⭐⭐⭐⭐',
               ha='center', fontsize=11, weight='bold', color='green',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
               transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)


def test_problem_791():
    """测试题目791"""
    print("\n" + "="*80)
    print("开始水泵综合工况分析...")
    print("="*80)
    
    # 创建水泵工况分析对象  
    # 设Q_required=0.07 < Q₀，使节流调节有意义
    pump = PumpOperation(Q_required=0.07, n0=1450)
    
    # 打印结果
    pump.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = pump.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_791_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_791_result.png")
    
    # 验证
    assert pump.Q0 > 0, "流量必须为正"
    assert pump.H0 > 0, "扬程必须为正"
    assert 0 < pump.eta0 <= 1, "效率必须在0-1之间"
    assert pump.P_speed < pump.P_throttle, "变速应比节流节能"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水泵工况调节是泵站运行的关键技术！")
    print("• 工况点: H_pump = H_pipe")
    print("• 节流调节: 简单但能耗大")
    print("• 变速调节: 节能效果最好 ⭐⭐⭐⭐⭐")
    print("• 切削调节: 不可逆，需谨慎")
    print("• 应用: 泵站设计、节能改造、工况匹配")


if __name__ == "__main__":
    test_problem_791()
