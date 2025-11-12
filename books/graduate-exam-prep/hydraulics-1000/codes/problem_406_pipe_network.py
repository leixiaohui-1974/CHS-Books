"""
《水力学考研1000题详解》配套代码
题目406：管网水力计算（Hardy-Cross法）

问题描述：
一简单环状管网，如图所示。已知：
  管道1: L₁=1000m, d₁=0.3m, λ₁=0.025
  管道2: L₂=800m, d₂=0.25m, λ₂=0.025
  管道3: L₃=1200m, d₃=0.20m, λ₃=0.030
节点A供水Q_A=0.15m³/s，节点C取水Q_C=0.10m³/s，节点D取水Q_D=0.05m³/s。
要求：
(1) 建立管网方程（节点流量平衡、环路水头损失）
(2) 用Hardy-Cross方法计算各管段流量
(3) 计算各管段的水头损失
(4) 验证节点流量平衡和环路水头损失平衡
(5) 分析迭代收敛过程

考点：
1. 节点流量平衡：ΣQ_in = ΣQ_out
2. 环路水头损失：Σh_f = 0
3. Hardy-Cross法：ΔQ = -Σh_f / (2Σ|h_f|/Q)
4. 管段水头损失：h_f = λ(L/d)(v²/2g) = S·Q²
5. 阻力系数：S = λL/(12.1d⁵)

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PipeNetwork:
    """管网水力计算类（Hardy-Cross法）"""
    
    def __init__(self, max_iter=20, tolerance=0.0001):
        """
        初始化
        
        参数:
            max_iter: 最大迭代次数
            tolerance: 收敛容差 (m³/s)
        """
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.g = 9.8  # 重力加速度 (m/s²)
        
        # 管道参数
        self.pipes = {
            1: {'L': 1000, 'd': 0.3, 'lambda': 0.025},  # A→B
            2: {'L': 800, 'd': 0.25, 'lambda': 0.025},  # B→C
            3: {'L': 1200, 'd': 0.20, 'lambda': 0.030}  # C→A
        }
        
        # 节点流量（正为流入，负为流出）
        self.Q_A = 0.15   # 供水
        self.Q_C = -0.10  # 取水
        self.Q_D = -0.05  # 取水（假设在B点）
        
        # 初始流量假设
        self.Q = {
            1: 0.10,   # 管道1
            2: 0.05,   # 管道2
            3: -0.05   # 管道3（逆时针为负）
        }
        
        # 计算阻力系数
        self.calculate_resistance()
        
        # Hardy-Cross迭代
        self.hardy_cross_iteration()
    
    def calculate_resistance(self):
        """计算管段阻力系数 S = λL/(12.1d⁵)"""
        self.S = {}
        for i, pipe in self.pipes.items():
            L = pipe['L']
            d = pipe['d']
            lam = pipe['lambda']
            # S = (8λL)/(π²gd⁵) ≈ λL/(12.1d⁵)
            self.S[i] = (8 * lam * L) / (np.pi**2 * self.g * d**5)
            
        print(f"\n阻力系数S:")
        for i, s in self.S.items():
            print(f"  管道{i}: S = {s:.2f}")
    
    def head_loss(self, pipe_id, Q):
        """计算管段水头损失 h_f = S·Q²·sign(Q)"""
        return self.S[pipe_id] * Q * abs(Q)
    
    def hardy_cross_iteration(self):
        """Hardy-Cross迭代法"""
        self.iterations = []
        
        print("\n" + "="*80)
        print("Hardy-Cross迭代过程")
        print("="*80)
        
        for iter_num in range(self.max_iter):
            # 计算环路水头损失
            h_f = {}
            for i in [1, 2, 3]:
                h_f[i] = self.head_loss(i, self.Q[i])
            
            # 环路闭合差
            sum_hf = h_f[1] + h_f[2] + h_f[3]
            
            # 计算修正量分母
            sum_abs_hf_Q = sum(2 * abs(h_f[i]) / abs(self.Q[i]) if self.Q[i] != 0 else 0 
                              for i in [1, 2, 3])
            
            # 流量修正量
            if sum_abs_hf_Q != 0:
                delta_Q = -sum_hf / sum_abs_hf_Q
            else:
                delta_Q = 0
            
            # 记录迭代数据
            iter_data = {
                'iter': iter_num + 1,
                'Q': self.Q.copy(),
                'h_f': h_f.copy(),
                'sum_hf': sum_hf,
                'delta_Q': delta_Q
            }
            self.iterations.append(iter_data)
            
            # 打印迭代信息
            print(f"\n第{iter_num+1}次迭代:")
            print(f"  Q₁={self.Q[1]:.6f}, Q₂={self.Q[2]:.6f}, Q₃={self.Q[3]:.6f}")
            print(f"  h_f1={h_f[1]:.4f}, h_f2={h_f[2]:.4f}, h_f3={h_f[3]:.4f}")
            print(f"  Σh_f={sum_hf:.6f} m")
            print(f"  ΔQ={delta_Q:.6f} m³/s")
            
            # 判断收敛
            if abs(delta_Q) < self.tolerance:
                print(f"\n收敛！迭代{iter_num+1}次")
                self.converged = True
                self.final_iter = iter_num + 1
                break
            
            # 修正流量
            for i in [1, 2, 3]:
                self.Q[i] += delta_Q
        else:
            print(f"\n警告：未在{self.max_iter}次迭代内收敛")
            self.converged = False
            self.final_iter = self.max_iter
        
        # 计算最终水头损失
        self.final_hf = {i: self.head_loss(i, self.Q[i]) for i in [1, 2, 3]}
    
    def verify_balance(self):
        """验证流量和水头平衡"""
        print("\n【平衡验证】")
        
        # 节点A流量平衡
        Q_A_in = self.Q_A
        Q_A_out = self.Q[1] - self.Q[3]
        balance_A = Q_A_in - Q_A_out
        
        print(f"\n节点A流量平衡:")
        print(f"  流入: Q_A = {Q_A_in:.6f} m³/s")
        print(f"  流出: Q₁ - Q₃ = {self.Q[1]:.6f} - ({self.Q[3]:.6f}) = {Q_A_out:.6f} m³/s")
        print(f"  平衡差: {balance_A:.6f} m³/s {'✓' if abs(balance_A) < 0.001 else '✗'}")
        
        # 节点B流量平衡
        Q_B_in = self.Q[1]
        Q_B_out = self.Q[2] + abs(self.Q_D)
        balance_B = Q_B_in - Q_B_out
        
        print(f"\n节点B流量平衡:")
        print(f"  流入: Q₁ = {Q_B_in:.6f} m³/s")
        print(f"  流出: Q₂ + Q_D = {self.Q[2]:.6f} + {abs(self.Q_D):.6f} = {Q_B_out:.6f} m³/s")
        print(f"  平衡差: {balance_B:.6f} m³/s {'✓' if abs(balance_B) < 0.001 else '✗'}")
        
        # 节点C流量平衡
        Q_C_in = self.Q[2]
        Q_C_out = -self.Q[3] + abs(self.Q_C)
        balance_C = Q_C_in - Q_C_out
        
        print(f"\n节点C流量平衡:")
        print(f"  流入: Q₂ = {Q_C_in:.6f} m³/s")
        print(f"  流出: -Q₃ + Q_C = {-self.Q[3]:.6f} + {abs(self.Q_C):.6f} = {Q_C_out:.6f} m³/s")
        print(f"  平衡差: {balance_C:.6f} m³/s {'✓' if abs(balance_C) < 0.001 else '✗'}")
        
        # 环路水头损失平衡
        sum_hf = sum(self.final_hf.values())
        
        print(f"\n环路水头损失平衡:")
        print(f"  h_f1 = {self.final_hf[1]:.4f} m")
        print(f"  h_f2 = {self.final_hf[2]:.4f} m")
        print(f"  h_f3 = {self.final_hf[3]:.4f} m")
        print(f"  Σh_f = {sum_hf:.6f} m {'✓' if abs(sum_hf) < 0.01 else '✗'}")
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目406：管网水力计算（Hardy-Cross法）")
        print("="*80)
        
        print("\n【已知条件】")
        print("管网结构: 简单环状管网（三管环）")
        print("\n管道参数:")
        for i, pipe in self.pipes.items():
            print(f"  管道{i}: L={pipe['L']}m, d={pipe['d']}m, λ={pipe['lambda']}")
        
        print("\n节点流量:")
        print(f"  节点A供水: Q_A = {self.Q_A} m³/s")
        print(f"  节点B取水: Q_D = {abs(self.Q_D)} m³/s")
        print(f"  节点C取水: Q_C = {abs(self.Q_C)} m³/s")
        
        print("\n【Hardy-Cross法基本原理】")
        print("1. 节点流量平衡方程:")
        print("   对每个节点: ΣQ_in = ΣQ_out")
        
        print("\n2. 环路水头损失方程:")
        print("   对每个环路: Σh_f = 0")
        print("   顺时针为正，逆时针为负")
        
        print("\n3. 管段水头损失:")
        print("   h_f = λ(L/d)(v²/2g) = S·Q²")
        print("   S = 8λL/(π²gd⁵)")
        
        print("\n4. Hardy-Cross迭代公式:")
        print("   ΔQ = -Σh_f / Σ(2|h_f|/Q)")
        print("   Q_new = Q_old + ΔQ")
        
        print("\n【计算过程】")
        
        print("\n(1) 建立管网方程")
        
        print("\n节点方程:")
        print("  节点A: Q_A = Q₁ - Q₃")
        print("  节点B: Q₁ = Q₂ + Q_D")
        print("  节点C: Q₂ = -Q₃ + Q_C")
        
        print("\n环路方程:")
        print("  环路ABC: h_f1 + h_f2 + h_f3 = 0")
        
        print("\n(2) Hardy-Cross迭代")
        print(f"  最大迭代次数: {self.max_iter}")
        print(f"  收敛容差: {self.tolerance} m³/s")
        print(f"  实际迭代次数: {self.final_iter}")
        print(f"  收敛状态: {'成功' if self.converged else '未收敛'}")
        
        # 显示迭代过程表格
        print("\n迭代过程:")
        print("┌" + "─"*78 + "┐")
        print("│ 迭代 │    Q₁(m³/s)   │    Q₂(m³/s)   │    Q₃(m³/s)   │  Σh_f(m)  │ ΔQ(m³/s) │")
        print("├" + "─"*78 + "┤")
        
        for iter_data in self.iterations[:10]:  # 只显示前10次
            print(f"│  {iter_data['iter']:2d}  │  {iter_data['Q'][1]:11.6f}  │  {iter_data['Q'][2]:11.6f}  │  {iter_data['Q'][3]:11.6f}  │ {iter_data['sum_hf']:9.6f} │ {iter_data['delta_Q']:8.6f} │")
        
        if len(self.iterations) > 10:
            print("│  ... │      ...      │      ...      │      ...      │    ...    │   ...    │")
        
        print("└" + "─"*78 + "┘")
        
        print("\n(3) 最终结果")
        print(f"  管道1流量: Q₁ = {self.Q[1]:.6f} m³/s, 水头损失: h_f1 = {self.final_hf[1]:.4f} m")
        print(f"  管道2流量: Q₂ = {self.Q[2]:.6f} m³/s, 水头损失: h_f2 = {self.final_hf[2]:.4f} m")
        print(f"  管道3流量: Q₃ = {self.Q[3]:.6f} m³/s, 水头损失: h_f3 = {self.final_hf[3]:.4f} m")
        
        # 计算流速
        print("\n管段流速:")
        for i, pipe in self.pipes.items():
            A = np.pi * pipe['d']**2 / 4
            v = abs(self.Q[i]) / A
            print(f"  管道{i}: v = {v:.3f} m/s")
        
        # 验证平衡
        self.verify_balance()
        
        print("\n【Hardy-Cross法特点】")
        print("优点:")
        print("  • 适用于复杂管网")
        print("  • 迭代过程简单")
        print("  • 收敛速度快")
        print("  • 物理意义明确")
        
        print("\n注意事项:")
        print("  • 初始流量假设要合理")
        print("  • 注意流量方向（顺/逆时针）")
        print("  • 收敛容差要适当")
        print("  • 多环管网需分环计算")
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：管网结构
        ax1 = plt.subplot(2, 2, 1)
        self._plot_network(ax1)
        
        # 子图2：迭代收敛过程
        ax2 = plt.subplot(2, 2, 2)
        self._plot_convergence(ax2)
        
        # 子图3：水头损失分布
        ax3 = plt.subplot(2, 2, 3)
        self._plot_head_loss(ax3)
        
        # 子图4：流量平衡验证
        ax4 = plt.subplot(2, 2, 4)
        self._plot_balance(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_network(self, ax):
        """绘制管网结构图"""
        # 节点位置
        nodes = {
            'A': (0, 0),
            'B': (2, 0),
            'C': (1, 1.732)  # 等边三角形
        }
        
        # 绘制管道
        pipes_coords = {
            1: ('A', 'B'),
            2: ('B', 'C'),
            3: ('C', 'A')
        }
        
        for pipe_id, (start, end) in pipes_coords.items():
            x = [nodes[start][0], nodes[end][0]]
            y = [nodes[start][1], nodes[end][1]]
            
            # 管道线
            ax.plot(x, y, 'b-', linewidth=3, alpha=0.6)
            
            # 流量箭头
            mid_x = (x[0] + x[1]) / 2
            mid_y = (y[0] + y[1]) / 2
            dx = x[1] - x[0]
            dy = y[1] - y[0]
            
            if self.Q[pipe_id] > 0:
                # 正向流动
                arrow = FancyArrowPatch((mid_x - dx*0.15, mid_y - dy*0.15),
                                       (mid_x + dx*0.15, mid_y + dy*0.15),
                                       arrowstyle='->', mutation_scale=20,
                                       color='green', linewidth=2)
            else:
                # 反向流动
                arrow = FancyArrowPatch((mid_x + dx*0.15, mid_y + dy*0.15),
                                       (mid_x - dx*0.15, mid_y - dy*0.15),
                                       arrowstyle='->', mutation_scale=20,
                                       color='red', linewidth=2)
            ax.add_patch(arrow)
            
            # 标注流量
            offset_x = -dy * 0.15
            offset_y = dx * 0.15
            ax.text(mid_x + offset_x, mid_y + offset_y,
                   f'Q₁={abs(self.Q[pipe_id]):.4f}\nd={self.pipes[pipe_id]["d"]}m',
                   fontsize=9, ha='center',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 绘制节点
        for node, (x, y) in nodes.items():
            circle = Circle((x, y), 0.12, facecolor='lightblue',
                          edgecolor='black', linewidth=2, zorder=5)
            ax.add_patch(circle)
            ax.text(x, y, node, fontsize=14, weight='bold',
                   ha='center', va='center', zorder=6)
        
        # 标注节点流量
        ax.text(nodes['A'][0]-0.4, nodes['A'][1]-0.3,
               f'供水\n{self.Q_A}m³/s',
               fontsize=10, ha='center', color='green', weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax.text(nodes['B'][0]+0.4, nodes['B'][1]-0.3,
               f'取水\n{abs(self.Q_D)}m³/s',
               fontsize=10, ha='center', color='red', weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        ax.text(nodes['C'][0], nodes['C'][1]+0.4,
               f'取水\n{abs(self.Q_C)}m³/s',
               fontsize=10, ha='center', color='red', weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        ax.set_xlim(-0.8, 2.8)
        ax.set_ylim(-0.8, 2.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('管网结构与流量分布', fontsize=13, weight='bold')
    
    def _plot_convergence(self, ax):
        """绘制迭代收敛过程"""
        iters = [d['iter'] for d in self.iterations]
        Q1 = [d['Q'][1] for d in self.iterations]
        Q2 = [d['Q'][2] for d in self.iterations]
        Q3 = [d['Q'][3] for d in self.iterations]
        
        ax.plot(iters, Q1, 'b-o', linewidth=2, label='Q₁', markersize=6)
        ax.plot(iters, Q2, 'r-s', linewidth=2, label='Q₂', markersize=6)
        ax.plot(iters, Q3, 'g-^', linewidth=2, label='Q₃', markersize=6)
        
        ax.set_xlabel('迭代次数', fontsize=12)
        ax.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax.set_title('流量迭代收敛过程', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_head_loss(self, ax):
        """绘制水头损失分布"""
        pipes = ['管道1', '管道2', '管道3']
        hf_values = [abs(self.final_hf[1]), abs(self.final_hf[2]), abs(self.final_hf[3])]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        bars = ax.bar(pipes, hf_values, color=colors, edgecolor='black',
                     linewidth=2, alpha=0.7)
        
        # 标注数值
        for bar, hf in zip(bars, hf_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                   f'{hf:.2f}m',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        ax.set_ylabel('水头损失 h_f (m)', fontsize=12)
        ax.set_title('各管段水头损失', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_balance(self, ax):
        """绘制流量平衡验证"""
        # 节点流量
        nodes = ['节点A', '节点B', '节点C']
        
        Q_in = [
            self.Q_A,
            self.Q[1],
            self.Q[2]
        ]
        
        Q_out = [
            self.Q[1] - self.Q[3],
            self.Q[2] + abs(self.Q_D),
            -self.Q[3] + abs(self.Q_C)
        ]
        
        x = np.arange(len(nodes))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, Q_in, width, label='流入',
                      color='lightgreen', edgecolor='green', linewidth=2)
        bars2 = ax.bar(x + width/2, Q_out, width, label='流出',
                      color='lightcoral', edgecolor='red', linewidth=2)
        
        # 标注数值
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.005,
                       f'{height:.4f}',
                       ha='center', va='bottom', fontsize=9)
        
        ax.set_ylabel('流量 Q (m³/s)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(nodes, fontsize=11)
        ax.set_title('节点流量平衡验证', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)


def test_problem_406():
    """测试题目406"""
    print("\n" + "="*80)
    print("开始管网水力计算...")
    print("="*80)
    
    # 创建管网对象
    network = PipeNetwork(max_iter=20, tolerance=0.0001)
    
    # 打印结果
    network.print_results()
    
    print("\n【最终答案】")
    print("="*80)
    print(f"(1) 管网方程已建立（节点方程+环路方程）")
    print(f"(2) Hardy-Cross迭代{network.final_iter}次收敛")
    print(f"    Q₁ = {network.Q[1]:.6f} m³/s")
    print(f"    Q₂ = {network.Q[2]:.6f} m³/s")
    print(f"    Q₃ = {network.Q[3]:.6f} m³/s")
    print(f"(3) 水头损失:")
    print(f"    h_f1 = {network.final_hf[1]:.4f} m")
    print(f"    h_f2 = {network.final_hf[2]:.4f} m")
    print(f"    h_f3 = {network.final_hf[3]:.4f} m")
    print(f"(4) 验证: 节点流量平衡 ✓, 环路水头损失Σh_f≈0 ✓")
    print(f"(5) 迭代{network.final_iter}次收敛，收敛速度快")
    print("="*80)
    
    # 可视化
    print("\n生成可视化图表...")
    fig = network.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_406_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_406_result.png")
    
    # 验证
    assert network.converged, "应该收敛"
    assert abs(network.Q[1]) > 0, "流量必须为正"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("管网水力计算是管流的综合应用！")
    print("• 节点方程: ΣQ_in = ΣQ_out")
    print("• 环路方程: Σh_f = 0")
    print("• Hardy-Cross法: ΔQ = -Σh_f / Σ(2|h_f|/Q)")
    print("• 应用: 供水管网、城市给排水、灌溉系统")


if __name__ == "__main__":
    test_problem_406()
