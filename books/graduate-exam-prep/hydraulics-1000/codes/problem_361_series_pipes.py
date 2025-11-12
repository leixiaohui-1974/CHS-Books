"""
《水力学考研1000题详解》配套代码
题目361：串联管道水力计算

问题描述：
三根管道串联，已知：
  管道1: L₁=500m, d₁=0.3m, λ₁=0.025
  管道2: L₂=800m, d₂=0.25m, λ₂=0.030
  管道3: L₃=600m, d₃=0.20m, λ₃=0.028
  总水头损失: ΔH = 15 m
  局部损失忽略不计

要求：
(1) 建立串联管道水力方程
(2) 计算通过管道的流量Q
(3) 计算各管段的流速和水头损失
(4) 绘制测压管水头线和总水头线
(5) 分析串联管道的特点

考点：
1. 串联管道连续性方程: Q₁ = Q₂ = Q₃ = Q
2. 能量方程: ΔH = Σh_f = h_f1 + h_f2 + h_f3
3. 沿程损失: h_f = λ(L/d)(v²/2g)
4. 等效管长: L_e = L₁(d_e/d₁)⁵ + L₂(d_e/d₂)⁵ + L₃(d_e/d₃)⁵
5. 串联管道特点: 流量相同，水头损失叠加

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SeriesPipes:
    """串联管道水力计算类"""
    
    def __init__(self, L1=500, d1=0.3, lambda1=0.025,
                 L2=800, d2=0.25, lambda2=0.030,
                 L3=600, d3=0.20, lambda3=0.028,
                 delta_H=15):
        """
        初始化
        
        参数:
            L1, L2, L3: 管长 (m)
            d1, d2, d3: 管径 (m)
            lambda1, lambda2, lambda3: 沿程阻力系数
            delta_H: 总水头损失 (m)
        """
        # 管道参数
        self.pipes = {
            1: {'L': L1, 'd': d1, 'lambda': lambda1},
            2: {'L': L2, 'd': d2, 'lambda': lambda2},
            3: {'L': L3, 'd': d3, 'lambda': lambda3}
        }
        
        self.delta_H = delta_H
        self.g = 9.8
        
        # 计算阻力系数
        self.calculate_resistance_coefficients()
        
        # 计算流量
        self.calculate_flow_rate()
        
        # 计算各管段参数
        self.calculate_pipe_parameters()
        
        # 计算等效管长
        self.calculate_equivalent_length()
    
    def calculate_resistance_coefficients(self):
        """计算管段阻力系数 S = 8λL/(π²gd⁵)"""
        self.S = {}
        
        print(f"\n管段阻力系数计算:")
        print(f"公式: S = 8λL/(π²gd⁵)")
        
        for i, pipe in self.pipes.items():
            L = pipe['L']
            d = pipe['d']
            lam = pipe['lambda']
            S = (8 * lam * L) / (np.pi**2 * self.g * d**5)
            self.S[i] = S
            
            print(f"  管道{i}: S{i} = 8×{lam}×{L}/(π²×{self.g}×{d}⁵) = {S:.2f}")
    
    def calculate_flow_rate(self):
        """计算流量（迭代求解）"""
        # 串联管道水头损失方程
        # ΔH = S₁Q² + S₂Q² + S₃Q² = (S₁+S₂+S₃)Q²
        
        S_total = sum(self.S.values())
        
        # 直接求解
        self.Q = np.sqrt(self.delta_H / S_total)
        
        print(f"\n流量计算:")
        print(f"  串联管道方程: ΔH = (S₁+S₂+S₃)Q²")
        print(f"  总阻力系数: S_total = {self.S[1]:.2f} + {self.S[2]:.2f} + {self.S[3]:.2f}")
        print(f"               = {S_total:.2f}")
        print(f"  流量: Q = √(ΔH/S_total) = √({self.delta_H}/{S_total:.2f})")
        print(f"        = {self.Q:.6f} m³/s")
    
    def calculate_pipe_parameters(self):
        """计算各管段流速和水头损失"""
        self.velocities = {}
        self.head_losses = {}
        self.Re = {}
        
        print(f"\n各管段水力参数:")
        print("─" * 70)
        print(f"{'管段':<6} {'流速v(m/s)':<12} {'水头损失h_f(m)':<15} {'雷诺数Re':<12}")
        print("─" * 70)
        
        for i, pipe in self.pipes.items():
            # 流速
            d = pipe['d']
            A = np.pi * d**2 / 4
            v = self.Q / A
            self.velocities[i] = v
            
            # 水头损失
            h_f = self.S[i] * self.Q**2
            self.head_losses[i] = h_f
            
            # 雷诺数（假设运动粘度 ν = 1.0×10⁻⁶ m²/s）
            nu = 1.0e-6
            Re = v * d / nu
            self.Re[i] = Re
            
            print(f"管道{i}   {v:10.4f}      {h_f:12.4f}         {Re:10.0f}")
        
        print("─" * 70)
        print(f"合计                   {sum(self.head_losses.values()):12.4f}")
        print("─" * 70)
        
        # 验证
        total_loss = sum(self.head_losses.values())
        error = abs(total_loss - self.delta_H)
        
        print(f"\n验证:")
        print(f"  各管段损失之和: Σh_f = {total_loss:.4f} m")
        print(f"  给定总损失: ΔH = {self.delta_H:.4f} m")
        print(f"  误差: {error:.6f} m {'✓' if error < 0.01 else '✗'}")
    
    def calculate_equivalent_length(self):
        """计算等效管长"""
        # 选择管道1的直径作为等效直径
        d_e = self.pipes[1]['d']
        lambda_e = self.pipes[1]['lambda']
        
        # 等效管长: L_e = Σ[L_i × (d_e/d_i)⁵ × (λ_i/λ_e)]
        L_e = 0
        
        print(f"\n等效管长计算:")
        print(f"  基准管径: d_e = {d_e} m")
        print(f"  基准阻力系数: λ_e = {lambda_e}")
        
        for i, pipe in self.pipes.items():
            L_i = pipe['L']
            d_i = pipe['d']
            lambda_i = pipe['lambda']
            
            # 等效管长分量
            L_ei = L_i * (d_e / d_i)**5 * (lambda_i / lambda_e)
            L_e += L_ei
            
            print(f"  管道{i}: L_e{i} = {L_i}×({d_e}/{d_i})⁵×({lambda_i}/{lambda_e}) = {L_ei:.2f} m")
        
        self.L_equivalent = L_e
        
        print(f"  等效总长: L_e = {L_e:.2f} m")
        
        # 验证（用等效管道计算流量）
        A_e = np.pi * d_e**2 / 4
        S_e = (8 * lambda_e * L_e) / (np.pi**2 * self.g * d_e**5)
        Q_e = np.sqrt(self.delta_H / S_e)
        
        print(f"\n  验证（用等效管道计算）:")
        print(f"    等效流量: Q_e = {Q_e:.6f} m³/s")
        print(f"    实际流量: Q = {self.Q:.6f} m³/s")
        print(f"    误差: {abs(Q_e - self.Q):.6f} m³/s {'✓' if abs(Q_e-self.Q) < 0.0001 else '✗'}")
    
    def analyze_characteristics(self):
        """分析串联管道特点"""
        print(f"\n串联管道特点分析:")
        
        print(f"\n1. 流量关系:")
        print(f"   Q₁ = Q₂ = Q₃ = Q = {self.Q:.6f} m³/s")
        print(f"   特点: 各管段流量相同（连续性方程）")
        
        print(f"\n2. 流速关系:")
        v1, v2, v3 = self.velocities[1], self.velocities[2], self.velocities[3]
        print(f"   v₁ = {v1:.4f} m/s")
        print(f"   v₂ = {v2:.4f} m/s")
        print(f"   v₃ = {v3:.4f} m/s")
        print(f"   特点: 管径越小，流速越大（v ∝ 1/d²）")
        
        print(f"\n3. 水头损失分配:")
        total_loss = sum(self.head_losses.values())
        for i in [1, 2, 3]:
            percentage = self.head_losses[i] / total_loss * 100
            print(f"   管道{i}: h_f{i} = {self.head_losses[i]:.4f} m ({percentage:.1f}%)")
        print(f"   特点: 小管径、长管段损失大")
        
        print(f"\n4. 主控管段:")
        max_loss_pipe = max(self.head_losses, key=self.head_losses.get)
        max_loss = self.head_losses[max_loss_pipe]
        print(f"   主控管段: 管道{max_loss_pipe}")
        print(f"   最大损失: h_f{max_loss_pipe} = {max_loss:.4f} m ({max_loss/total_loss*100:.1f}%)")
        print(f"   改进建议: 优先增大管道{max_loss_pipe}的直径")
        
        print(f"\n5. 雷诺数分析:")
        for i in [1, 2, 3]:
            Re = self.Re[i]
            regime = "紊流" if Re > 4000 else "层流" if Re < 2000 else "过渡流"
            print(f"   管道{i}: Re{i} = {Re:.0f} ({regime})")
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目361：串联管道水力计算")
        print("="*80)
        
        print("\n【已知条件】")
        for i, pipe in self.pipes.items():
            print(f"  管道{i}: L{i}={pipe['L']}m, d{i}={pipe['d']}m, λ{i}={pipe['lambda']}")
        print(f"  总水头损失: ΔH = {self.delta_H} m")
        
        print("\n【串联管道基本原理】")
        print("1. 连续性方程:")
        print("   Q₁ = Q₂ = Q₃ = Q（流量相同）")
        
        print("\n2. 能量方程:")
        print("   ΔH = h_f1 + h_f2 + h_f3（水头损失叠加）")
        
        print("\n3. 沿程损失公式:")
        print("   h_f = λ(L/d)(v²/2g) = S·Q²")
        print("   其中 S = 8λL/(π²gd⁵)")
        
        print("\n4. 串联管道方程:")
        print("   ΔH = (S₁+S₂+S₃)Q²")
        print("   Q = √[ΔH/(S₁+S₂+S₃)]")
        
        print("\n5. 等效管长法:")
        print("   将串联管道等效为单根管道")
        print("   L_e = Σ[L_i(d_e/d_i)⁵(λ_i/λ_e)]")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 特点分析
        self.analyze_characteristics()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 串联管道方程: ΔH = (S₁+S₂+S₃)Q²")
        print(f"    Q = √[ΔH/(S₁+S₂+S₃)] = {self.Q:.6f} m³/s")
        print(f"(2) 流量: Q = {self.Q:.6f} m³/s = {self.Q*1000:.3f} L/s")
        print(f"(3) 各管段参数:")
        for i in [1, 2, 3]:
            print(f"    管道{i}: v{i}={self.velocities[i]:.4f}m/s, h_f{i}={self.head_losses[i]:.4f}m")
        print(f"(4) 测压管水头线和总水头线已绘制")
        print(f"(5) 特点: 流量相同、损失叠加、小管径控制")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：管道布置与水头线
        ax1 = plt.subplot(2, 2, 1)
        self._plot_hydraulic_grade_line(ax1)
        
        # 子图2：各管段参数对比
        ax2 = plt.subplot(2, 2, 2)
        self._plot_parameter_comparison(ax2)
        
        # 子图3：水头损失分配
        ax3 = plt.subplot(2, 2, 3)
        self._plot_head_loss_distribution(ax3)
        
        # 子图4：流速与管径关系
        ax4 = plt.subplot(2, 2, 4)
        self._plot_velocity_diameter_relation(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_hydraulic_grade_line(self, ax):
        """绘制测压管水头线和总水头线"""
        # 累计管长
        x_positions = [0]
        for i in [1, 2, 3]:
            x_positions.append(x_positions[-1] + self.pipes[i]['L'])
        
        # 累计水头损失（从上游到下游）
        H_total = [0]  # 初始水头设为0（相对值）
        H_pressure = [0]
        
        for i in [1, 2, 3]:
            # 总水头线（逐渐下降）
            H_total.append(H_total[-1] - self.head_losses[i])
            
            # 测压管水头线（考虑速度水头变化）
            v_prev = self.velocities[i-1] if i > 1 else 0
            v_curr = self.velocities[i]
            delta_velocity_head = (v_curr**2 - v_prev**2) / (2 * self.g)
            H_pressure.append(H_total[-1] - v_curr**2/(2*self.g))
        
        # 管底高程（水平管道）
        z_bottom = [min(H_total) - 5] * len(x_positions)
        
        # 绘制管道
        for i in range(len(x_positions)-1):
            pipe_idx = i + 1
            d = self.pipes[pipe_idx]['d']
            
            # 管道轮廓
            x = [x_positions[i], x_positions[i+1]]
            y_bottom = [z_bottom[i], z_bottom[i+1]]
            y_top = [y_bottom[0] + d, y_bottom[1] + d]
            
            ax.fill_between(x, y_bottom, y_top, alpha=0.3, color='gray')
            ax.plot(x, y_bottom, 'k-', linewidth=2)
            ax.plot(x, y_top, 'k-', linewidth=2)
            
            # 标注管径
            ax.text((x[0]+x[1])/2, y_bottom[0] - 1.5, 
                   f'd{pipe_idx}={d}m\nL{pipe_idx}={self.pipes[pipe_idx]["L"]}m',
                   ha='center', fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 总水头线
        ax.plot(x_positions, H_total, 'b-', linewidth=2.5, marker='o', 
               markersize=8, label='总水头线（能量线）')
        
        # 测压管水头线
        ax.plot(x_positions, H_pressure, 'r--', linewidth=2.5, marker='s', 
               markersize=8, label='测压管水头线')
        
        # 标注水头损失
        for i in [1, 2, 3]:
            x_mid = (x_positions[i-1] + x_positions[i]) / 2
            y_mid = (H_total[i-1] + H_total[i]) / 2
            ax.annotate(f'h_f{i}={self.head_losses[i]:.2f}m',
                       xy=(x_mid, y_mid), fontsize=9,
                       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 标注总水头损失
        ax.annotate('', xy=(x_positions[-1]+50, H_total[0]), 
                   xytext=(x_positions[-1]+50, H_total[-1]),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax.text(x_positions[-1]+100, (H_total[0]+H_total[-1])/2, 
               f'ΔH={self.delta_H}m',
               fontsize=11, weight='bold', color='red')
        
        ax.set_xlabel('距离 x (m)', fontsize=12)
        ax.set_ylabel('水头 H (m)', fontsize=12)
        ax.set_title('串联管道水头线图', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-100, x_positions[-1] + 200)
    
    def _plot_parameter_comparison(self, ax):
        """绘制各管段参数对比"""
        pipes = ['管道1', '管道2', '管道3']
        
        # 多组柱状图
        x = np.arange(len(pipes))
        width = 0.25
        
        # 流速（归一化）
        velocities_norm = [self.velocities[i]/max(self.velocities.values()) for i in [1,2,3]]
        bars1 = ax.bar(x - width, velocities_norm, width, label='流速（归一化）',
                      color='lightblue', edgecolor='blue', linewidth=2)
        
        # 水头损失（归一化）
        head_losses_norm = [self.head_losses[i]/max(self.head_losses.values()) for i in [1,2,3]]
        bars2 = ax.bar(x, head_losses_norm, width, label='水头损失（归一化）',
                      color='lightcoral', edgecolor='red', linewidth=2)
        
        # 管径（归一化）
        diameters_norm = [self.pipes[i]['d']/max([self.pipes[j]['d'] for j in [1,2,3]]) for i in [1,2,3]]
        bars3 = ax.bar(x + width, diameters_norm, width, label='管径（归一化）',
                      color='lightgreen', edgecolor='green', linewidth=2)
        
        # 标注实际值
        for i, (v, h, d) in enumerate(zip(velocities_norm, head_losses_norm, diameters_norm)):
            ax.text(x[i] - width, v + 0.05, f'{self.velocities[i+1]:.2f}m/s', 
                   ha='center', fontsize=8)
            ax.text(x[i], h + 0.05, f'{self.head_losses[i+1]:.2f}m', 
                   ha='center', fontsize=8)
            ax.text(x[i] + width, d + 0.05, f'{self.pipes[i+1]["d"]}m', 
                   ha='center', fontsize=8)
        
        ax.set_ylabel('归一化值', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(pipes, fontsize=11)
        ax.set_title('各管段参数对比', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, 1.3)
    
    def _plot_head_loss_distribution(self, ax):
        """绘制水头损失分配饼图"""
        labels = [f'管道{i}\n{self.head_losses[i]:.2f}m' for i in [1, 2, 3]]
        sizes = [self.head_losses[i] for i in [1, 2, 3]]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        explode = [0.1 if self.head_losses[i] == max(sizes) else 0 for i in [1, 2, 3]]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                          autopct='%1.1f%%', startangle=90,
                                          explode=explode,
                                          textprops={'fontsize': 11, 'weight': 'bold'})
        
        # 美化百分比文字
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')
        
        ax.set_title(f'水头损失分配（总计{self.delta_H}m）', 
                    fontsize=13, weight='bold', pad=20)
    
    def _plot_velocity_diameter_relation(self, ax):
        """绘制流速与管径关系"""
        pipes = ['管道1', '管道2', '管道3']
        diameters = [self.pipes[i]['d'] for i in [1, 2, 3]]
        velocities = [self.velocities[i] for i in [1, 2, 3]]
        
        # 散点图
        ax.scatter(diameters, velocities, s=200, c=['red', 'blue', 'green'],
                  alpha=0.7, edgecolors='black', linewidth=2, zorder=3)
        
        # 标注
        for i, (d, v, name) in enumerate(zip(diameters, velocities, pipes)):
            ax.annotate(f'{name}\nd={d}m\nv={v:.3f}m/s',
                       xy=(d, v), xytext=(d, v + 0.3),
                       ha='center', fontsize=9, weight='bold',
                       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 理论曲线 v ∝ 1/d²
        d_theory = np.linspace(min(diameters)*0.8, max(diameters)*1.2, 100)
        # 使用第一个管道作为参考点
        v_theory = velocities[0] * (diameters[0] / d_theory)**2
        ax.plot(d_theory, v_theory, 'k--', linewidth=2, alpha=0.5, 
               label='理论曲线 v∝1/d²')
        
        ax.set_xlabel('管径 d (m)', fontsize=12)
        ax.set_ylabel('流速 v (m/s)', fontsize=12)
        ax.set_title('流速与管径关系', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 添加说明
        ax.text(0.05, 0.95, f'Q = {self.Q:.6f} m³/s = 常数\nv = Q/A = 4Q/(πd²)',
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))


def test_problem_361():
    """测试题目361"""
    print("\n" + "="*80)
    print("开始串联管道水力计算...")
    print("="*80)
    
    # 创建串联管道分析对象
    pipes = SeriesPipes(L1=500, d1=0.3, lambda1=0.025,
                       L2=800, d2=0.25, lambda2=0.030,
                       L3=600, d3=0.20, lambda3=0.028,
                       delta_H=15)
    
    # 打印结果
    pipes.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = pipes.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_361_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_361_result.png")
    
    # 验证
    assert pipes.Q > 0, "流量必须为正"
    assert all(v > 0 for v in pipes.velocities.values()), "流速必须为正"
    assert abs(sum(pipes.head_losses.values()) - pipes.delta_H) < 0.01, "水头损失应相等"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("串联管道是管流的经典问题！")
    print("• 连续性: Q₁ = Q₂ = Q₃")
    print("• 能量方程: ΔH = Σh_f")
    print("• 串联方程: ΔH = (S₁+S₂+S₃)Q²")
    print("• 等效管长: 将串联管等效为单管")
    print("• 应用: 长距离输水、城市供水、管网设计")


if __name__ == "__main__":
    test_problem_361()
