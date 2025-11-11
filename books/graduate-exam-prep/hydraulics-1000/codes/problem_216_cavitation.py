"""
《水力学考研1000题详解》配套代码
题目216：空化（气蚀）现象分析

问题描述：
一离心泵装置，已知：
  吸水高度 h_s = 3.5 m
  吸水管直径 d = 0.15 m
  流量 Q = 0.05 m³/s
  吸水管总损失系数 ζ = 5.0
  大气压强 p_a = 101.3 kPa
  水的饱和蒸汽压 p_v = 2.3 kPa（20℃）
  水的密度 ρ = 1000 kg/m³

要求：
(1) 计算泵入口处的压强
(2) 判断是否会发生空化
(3) 计算空化数σ
(4) 计算允许吸上真空度和允许安装高度
(5) 分析空化的危害及防护措施

考点：
1. Bernoulli方程：p/ρg + v²/2g + z = 常数
2. 空化判据：p ≤ p_v（发生空化）
3. 空化数：σ = (p - p_v)/(ρv²/2)
4. 允许吸上真空度：[H_s] = p_a/ρg - p_v/ρg - Δh
5. 允许安装高度：[h_s] = [H_s] - h_loss
6. 空化余量：NPSH = (p - p_v)/ρg

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch, Polygon
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Cavitation:
    """空化现象分析类"""
    
    def __init__(self, h_s=3.5, d=0.15, Q=0.05, zeta=5.0, 
                 p_a=101.3e3, p_v=2.3e3, rho=1000):
        """
        初始化
        
        参数:
            h_s: 吸水高度 (m)
            d: 管径 (m)
            Q: 流量 (m³/s)
            zeta: 总损失系数
            p_a: 大气压强 (Pa)
            p_v: 饱和蒸汽压 (Pa)
            rho: 密度 (kg/m³)
        """
        self.h_s = h_s
        self.d = d
        self.Q = Q
        self.zeta = zeta
        self.p_a = p_a
        self.p_v = p_v
        self.rho = rho
        self.g = 9.8
        
        # 计算流速
        self.A = np.pi * self.d**2 / 4
        self.v = self.Q / self.A
        
        # 计算泵入口压强
        self.calculate_inlet_pressure()
        
        # 判断空化
        self.check_cavitation()
        
        # 计算空化数
        self.calculate_cavitation_number()
        
        # 计算允许安装高度
        self.calculate_allowable_height()
    
    def calculate_inlet_pressure(self):
        """计算泵入口处的压强"""
        # Bernoulli方程（从水面到泵入口）
        # 水面: p_a/ρg + 0 + 0 = 基准
        # 泵入口: p_1/ρg + v²/2g + (-h_s) + 损失
        
        # 损失水头
        h_loss = self.zeta * self.v**2 / (2 * self.g)
        
        # 泵入口压强水头
        H_1 = self.p_a / (self.rho * self.g) - self.v**2 / (2 * self.g) - self.h_s - h_loss
        
        # 泵入口绝对压强
        self.p_1 = H_1 * self.rho * self.g
        
        # 真空度
        self.vacuum = self.p_a - self.p_1
        self.H_vacuum = self.vacuum / (self.rho * self.g)
        
        print(f"\n泵入口压强计算:")
        print(f"  流速: v = Q/A = {self.Q}/{self.A:.6f} = {self.v:.3f} m/s")
        print(f"  速度水头: v²/2g = {self.v**2/(2*self.g):.4f} m")
        print(f"  损失水头: h_loss = ζ×v²/2g = {self.zeta}×{self.v**2/(2*self.g):.4f} = {h_loss:.4f} m")
        print(f"  压强水头: H₁ = p_a/ρg - v²/2g - h_s - h_loss")
        print(f"          = {self.p_a/(self.rho*self.g):.3f} - {self.v**2/(2*self.g):.4f} - {self.h_s} - {h_loss:.4f}")
        print(f"          = {H_1:.4f} m")
        print(f"  绝对压强: p₁ = {self.p_1/1000:.2f} kPa")
        print(f"  真空度: H_v = {self.H_vacuum:.4f} m = {self.vacuum/1000:.2f} kPa")
    
    def check_cavitation(self):
        """判断是否发生空化"""
        self.cavitation_occurred = self.p_1 <= self.p_v
        
        print(f"\n空化判别:")
        print(f"  泵入口压强: p₁ = {self.p_1/1000:.2f} kPa")
        print(f"  饱和蒸汽压: p_v = {self.p_v/1000:.2f} kPa")
        print(f"  判据: p₁ {'≤' if self.cavitation_occurred else '>'} p_v")
        
        if self.cavitation_occurred:
            print(f"  结论: ⚠️ 会发生空化！")
            print(f"  危险程度: 严重")
        else:
            # 计算安全裕度
            safety_margin = (self.p_1 - self.p_v) / self.p_v * 100
            print(f"  结论: ✓ 不会发生空化")
            print(f"  安全裕度: {safety_margin:.1f}%")
    
    def calculate_cavitation_number(self):
        """计算空化数"""
        # 空化数: σ = (p - p_v) / (ρv²/2)
        self.sigma = (self.p_1 - self.p_v) / (0.5 * self.rho * self.v**2)
        
        # Thoma空化系数
        self.thoma = (self.p_1 - self.p_v) / (self.rho * self.g * (self.v**2 / (2 * self.g)))
        
        print(f"\n空化数计算:")
        print(f"  空化数: σ = (p₁-p_v)/(ρv²/2)")
        print(f"         = ({self.p_1/1000:.2f}-{self.p_v/1000:.2f})×1000 / ({self.rho}×{self.v:.3f}²/2)")
        print(f"         = {self.sigma:.4f}")
        
        print(f"\n  Thoma空化系数: σ_T = (p₁-p_v)/(ρg×v²/2g)")
        print(f"                 = {self.thoma:.4f}")
        
        # 判断空化风险
        if self.sigma < 0:
            risk = "极高风险 - 已空化"
        elif self.sigma < 0.5:
            risk = "高风险"
        elif self.sigma < 1.0:
            risk = "中等风险"
        else:
            risk = "低风险"
        
        print(f"  空化风险: {risk}")
    
    def calculate_allowable_height(self):
        """计算允许吸上真空度和允许安装高度"""
        # 允许吸上真空度（取安全系数0.75）
        safety_factor = 0.75
        
        # 理论允许真空度
        H_s_theory = self.p_a / (self.rho * self.g) - self.p_v / (self.rho * self.g)
        
        # 实际允许真空度（考虑安全系数）
        self.H_s_allow = safety_factor * H_s_theory
        
        # 损失水头
        h_loss = self.zeta * self.v**2 / (2 * self.g)
        
        # 允许安装高度
        self.h_s_allow = self.H_s_allow - self.v**2 / (2 * self.g) - h_loss
        
        print(f"\n允许安装高度计算:")
        print(f"  大气压水头: p_a/ρg = {self.p_a/(self.rho*self.g):.3f} m")
        print(f"  蒸汽压水头: p_v/ρg = {self.p_v/(self.rho*self.g):.3f} m")
        print(f"  理论允许真空度: H_s(理论) = {H_s_theory:.3f} m")
        print(f"  安全系数: k = {safety_factor}")
        print(f"  允许真空度: [H_s] = {self.H_s_allow:.3f} m")
        print(f"  允许安装高度: [h_s] = [H_s] - v²/2g - h_loss")
        print(f"               = {self.H_s_allow:.3f} - {self.v**2/(2*self.g):.4f} - {h_loss:.4f}")
        print(f"               = {self.h_s_allow:.3f} m")
        
        # 与实际安装高度对比
        print(f"\n  实际安装高度: h_s = {self.h_s} m")
        print(f"  允许安装高度: [h_s] = {self.h_s_allow:.3f} m")
        
        if self.h_s > self.h_s_allow:
            print(f"  结论: ⚠️ h_s > [h_s]，安装高度过高，易发生空化！")
            print(f"  超出量: Δh = {self.h_s - self.h_s_allow:.3f} m")
        else:
            print(f"  结论: ✓ h_s ≤ [h_s]，安装高度合适")
            print(f"  安全余量: Δh = {self.h_s_allow - self.h_s:.3f} m")
    
    def analyze_cavitation_damage(self):
        """分析空化危害"""
        print(f"\n空化危害分析:")
        
        print(f"\n1. 材料破坏:")
        print(f"   • 气泡溃灭产生高压冲击（可达数百MPa）")
        print(f"   • 金属表面产生麻点、蜂窝状损坏")
        print(f"   • 严重时导致叶轮穿孔")
        
        print(f"\n2. 性能下降:")
        print(f"   • 流量减小、扬程降低")
        print(f"   • 效率大幅下降")
        print(f"   • 无法达到设计工况")
        
        print(f"\n3. 振动与噪声:")
        print(f"   • 气泡溃灭产生强烈振动")
        print(f"   • 噪声增大（类似砂石撞击声）")
        print(f"   • 影响设备寿命和运行稳定性")
        
        print(f"\n4. 化学腐蚀:")
        print(f"   • 新鲜金属表面暴露")
        print(f"   • 氧化腐蚀加速")
        print(f"   • 机械作用与化学腐蚀协同")
    
    def suggest_prevention_measures(self):
        """提出防空化措施"""
        print(f"\n防空化措施:")
        
        print(f"\n1. 降低安装高度 ⭐⭐⭐⭐⭐")
        print(f"   • 现状: h_s = {self.h_s} m")
        print(f"   • 建议: h_s ≤ {self.h_s_allow:.2f} m")
        print(f"   • 需降低: Δh ≥ {max(0, self.h_s - self.h_s_allow):.2f} m")
        
        print(f"\n2. 减小吸水管阻力 ⭐⭐⭐⭐")
        print(f"   • 增大管径（减小流速）")
        print(f"   • 减少弯头、阀门等局部阻力")
        print(f"   • 缩短管道长度")
        print(f"   • 现状损失系数: ζ = {self.zeta}")
        
        print(f"\n3. 改善吸水条件 ⭐⭐⭐")
        print(f"   • 增加水源压力")
        print(f"   • 降低水温（降低p_v）")
        print(f"   • 避免吸入空气")
        
        print(f"\n4. 选用抗空化性能好的泵 ⭐⭐⭐⭐")
        print(f"   • 选择必需空化余量NPSH_r较小的泵")
        print(f"   • 采用双吸泵（减小入口流速）")
        print(f"   • 采用诱导轮")
        
        print(f"\n5. 材料与结构改进 ⭐⭐⭐")
        print(f"   • 选用抗空化材料（不锈钢、铜合金）")
        print(f"   • 表面涂层保护")
        print(f"   • 优化叶轮设计")
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目216：空化（气蚀）现象分析")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  吸水高度: h_s = {self.h_s} m")
        print(f"  管径: d = {self.d} m")
        print(f"  流量: Q = {self.Q} m³/s")
        print(f"  总损失系数: ζ = {self.zeta}")
        print(f"  大气压强: p_a = {self.p_a/1000} kPa")
        print(f"  饱和蒸汽压: p_v = {self.p_v/1000} kPa")
        print(f"  水的密度: ρ = {self.rho} kg/m³")
        
        print("\n【空化基本原理】")
        print("1. 空化现象:")
        print("   液体中局部压强降至饱和蒸汽压以下时，")
        print("   液体汽化形成气泡，气泡在高压区溃灭产生冲击")
        
        print("\n2. 空化条件:")
        print("   p ≤ p_v（局部压强 ≤ 饱和蒸汽压）")
        
        print("\n3. 空化数:")
        print("   σ = (p - p_v)/(ρv²/2)")
        print("   σ < 0: 已空化；σ > 1: 相对安全")
        
        print("\n4. 允许吸上真空度:")
        print("   [H_s] = p_a/ρg - p_v/ρg - Δh（含安全系数）")
        
        print("\n5. 允许安装高度:")
        print("   [h_s] = [H_s] - v²/2g - h_loss")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 危害分析
        self.analyze_cavitation_damage()
        
        # 防护措施
        self.suggest_prevention_measures()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 泵入口压强: p₁ = {self.p_1/1000:.2f} kPa，真空度 = {self.H_vacuum:.3f} m")
        print(f"(2) 空化判别: {'会发生空化 ⚠️' if self.cavitation_occurred else '不会空化 ✓'}")
        print(f"(3) 空化数: σ = {self.sigma:.4f}")
        print(f"(4) 允许吸上真空度: [H_s] = {self.H_s_allow:.3f} m")
        print(f"    允许安装高度: [h_s] = {self.h_s_allow:.3f} m")
        print(f"(5) 危害: 材料破坏、性能下降、振动噪声、化学腐蚀")
        print(f"    措施: 降低安装高度、减小阻力、改善吸水条件、优化设计")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：泵装置示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_pump_system(ax1)
        
        # 子图2：压强分布
        ax2 = plt.subplot(2, 2, 2)
        self._plot_pressure_distribution(ax2)
        
        # 子图3：空化过程
        ax3 = plt.subplot(2, 2, 3)
        self._plot_cavitation_process(ax3)
        
        # 子图4：安装高度影响
        ax4 = plt.subplot(2, 2, 4)
        self._plot_height_effect(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_pump_system(self, ax):
        """绘制泵装置示意图"""
        # 水池
        pool = Rectangle((0, -4), 3, 3.5, 
                        facecolor='lightblue', edgecolor='blue', linewidth=2)
        ax.add_patch(pool)
        ax.plot([0, 3], [-0.5, -0.5], 'b-', linewidth=3)  # 水面
        ax.text(1.5, -0.8, '水面', ha='center', fontsize=11, weight='bold')
        
        # 吸水管
        ax.plot([2.5, 2.5, 4], [-0.5, 3.5, 3.5], 'gray', linewidth=8)
        ax.text(3.2, 1.5, f'吸水管\nd={self.d}m', ha='center', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 泵
        pump_center = (5, 3.5)
        pump = Circle(pump_center, 0.8, facecolor='lightgreen', 
                     edgecolor='green', linewidth=2)
        ax.add_patch(pump)
        ax.text(pump_center[0], pump_center[1], '离心泵', 
               ha='center', va='center', fontsize=12, weight='bold')
        
        # 标注安装高度
        ax.annotate('', xy=(7, -0.5), xytext=(7, 3.5),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax.text(7.5, 1.5, f'h_s={self.h_s}m', fontsize=11, weight='bold', color='red')
        
        # 标注流速
        arrow = FancyArrowPatch((3, 3.5), (4, 3.5),
                               arrowstyle='->', mutation_scale=20, 
                               color='blue', linewidth=3)
        ax.add_patch(arrow)
        ax.text(3.5, 4, f'v={self.v:.2f}m/s', fontsize=10, color='blue', weight='bold')
        
        # 空化警告
        if self.cavitation_occurred:
            ax.text(5, 1, '⚠️ 空化风险区', ha='center', fontsize=12, weight='bold',
                   color='red', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(-4.5, 5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('离心泵吸水装置示意图', fontsize=13, weight='bold')
    
    def _plot_pressure_distribution(self, ax):
        """绘制压强分布"""
        # 压强值（kPa）
        pressures = [
            self.p_a/1000,           # 水面
            self.p_1/1000,           # 泵入口
            self.p_v/1000            # 饱和蒸汽压
        ]
        
        labels = ['大气压\np_a', '泵入口\np₁', '饱和蒸汽压\np_v']
        colors = ['green', 'blue' if not self.cavitation_occurred else 'red', 'orange']
        
        bars = ax.bar(labels, pressures, color=colors, edgecolor='black', 
                     linewidth=2, alpha=0.7)
        
        # 标注数值
        for bar, p in zip(bars, pressures):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 2,
                   f'{p:.1f}kPa',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 标注空化判据线
        ax.axhline(self.p_v/1000, color='red', linestyle='--', linewidth=2, 
                  label='空化临界压强')
        
        # 标注区域
        if self.cavitation_occurred:
            ax.text(0.5, 0.85, '⚠️ 已空化\np₁ < p_v', transform=ax.transAxes,
                   fontsize=12, weight='bold', color='red',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        else:
            ax.text(0.5, 0.85, '✓ 未空化\np₁ > p_v', transform=ax.transAxes,
                   fontsize=12, weight='bold', color='green',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        ax.set_ylabel('压强 p (kPa)', fontsize=12)
        ax.set_title('各点压强对比', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_cavitation_process(self, ax):
        """绘制空化过程示意图"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.98, '空化过程（四个阶段）', ha='center', va='top',
               fontsize=13, weight='bold', transform=ax.transAxes)
        
        stages = [
            ('1. 气核生长', '压强降低\np < p_v', 0.75),
            ('2. 气泡形成', '液体汽化\n气泡膨胀', 0.55),
            ('3. 气泡迁移', '随流动进入\n高压区', 0.35),
            ('4. 气泡溃灭', '压强升高\n强烈冲击', 0.15)
        ]
        
        for i, (title, desc, y) in enumerate(stages):
            # 气泡示意
            if i < 3:
                radius = 0.05 + i * 0.02
                circle = Circle((0.2, y), radius, facecolor='lightblue', 
                              edgecolor='blue', linewidth=2)
                ax.add_patch(circle)
            else:
                # 溃灭效果
                ax.plot([0.15, 0.25], [y-0.03, y+0.03], 'r-', linewidth=3)
                ax.plot([0.15, 0.25], [y+0.03, y-0.03], 'r-', linewidth=3)
                ax.text(0.2, y, '💥', ha='center', fontsize=20)
            
            # 文字说明
            ax.text(0.35, y+0.02, title, fontsize=11, weight='bold')
            ax.text(0.35, y-0.03, desc, fontsize=9)
            
            # 箭头
            if i < 3:
                ax.annotate('', xy=(0.2, stages[i+1][2]+0.05), xytext=(0.2, y-0.05),
                           arrowprops=dict(arrowstyle='->', color='gray', lw=2))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    
    def _plot_height_effect(self, ax):
        """绘制安装高度影响"""
        # 不同安装高度下的入口压强
        h_range = np.linspace(0, 8, 50)
        p_1_array = []
        
        for h in h_range:
            h_loss = self.zeta * self.v**2 / (2 * self.g)
            H_1 = self.p_a/(self.rho*self.g) - self.v**2/(2*self.g) - h - h_loss
            p_1 = H_1 * self.rho * self.g
            p_1_array.append(p_1/1000)
        
        p_1_array = np.array(p_1_array)
        
        # 绘图
        ax.plot(h_range, p_1_array, 'b-', linewidth=2.5, label='泵入口压强 p₁')
        ax.axhline(self.p_v/1000, color='red', linestyle='--', linewidth=2, 
                  label=f'饱和蒸汽压 p_v={self.p_v/1000}kPa')
        ax.axhline(0, color='gray', linestyle=':', linewidth=1)
        
        # 标注当前工况
        ax.plot(self.h_s, self.p_1/1000, 'ro', markersize=10, 
               label=f'当前工况\nh_s={self.h_s}m')
        
        # 标注允许安装高度
        ax.axvline(self.h_s_allow, color='green', linestyle='--', linewidth=2,
                  label=f'允许安装高度\n[h_s]={self.h_s_allow:.2f}m')
        
        # 填充区域
        ax.fill_between(h_range, p_1_array, self.p_v/1000, 
                        where=(p_1_array >= self.p_v/1000),
                        alpha=0.3, color='green', label='安全区')
        ax.fill_between(h_range, p_1_array, self.p_v/1000, 
                        where=(p_1_array < self.p_v/1000),
                        alpha=0.3, color='red', label='空化区')
        
        ax.set_xlabel('安装高度 h_s (m)', fontsize=12)
        ax.set_ylabel('压强 p (kPa)', fontsize=12)
        ax.set_title('安装高度对入口压强的影响', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 8)


def test_problem_216():
    """测试题目216"""
    print("\n" + "="*80)
    print("开始空化（气蚀）现象分析...")
    print("="*80)
    
    # 创建空化分析对象
    cav = Cavitation(h_s=3.5, d=0.15, Q=0.05, zeta=5.0,
                    p_a=101.3e3, p_v=2.3e3, rho=1000)
    
    # 打印结果
    cav.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = cav.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_216_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_216_result.png")
    
    # 验证
    assert cav.p_1 > 0, "压强必须计算"
    assert cav.sigma is not None, "空化数必须计算"
    assert cav.h_s_allow > 0, "允许安装高度必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("空化是流体机械的重大危害！")
    print("• 空化条件: p ≤ p_v")
    print("• 空化数: σ = (p-p_v)/(ρv²/2)")
    print("• 允许安装高度: [h_s] = [H_s] - v²/2g - h_loss")
    print("• 防护: 降低安装高度、减小阻力、优化设计")
    print("• 应用: 泵站设计、水轮机、螺旋桨、水力空化")


if __name__ == "__main__":
    test_problem_216()
