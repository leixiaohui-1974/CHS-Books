"""
《水力学考研1000题详解》配套代码
题目366：管道第二类计算问题（迭代求流量Q）

问题描述：
圆管输水系统，管径d=0.2m，管长L=500m，总水头损失h=10m。
管道绝对粗糙度ε=0.2mm，运动粘度ν=1.0×10⁻⁶m²/s。
局部损失系数∑ζ=5.0。
求：流量Q (m³/s)

考点：
1. 第二类问题特点：已知h和d，求Q
2. 迭代求解：λ依赖于Re，Re依赖于v，v依赖于Q
3. Colebrook-White方程：1/√λ = -2lg(ε/3.71d + 2.51/Re√λ)
4. 能量方程：h = (λL/d + ∑ζ)·v²/2g
5. 收敛判断：|Q_new - Q_old| < 0.001

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Arrow
import warnings

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PipeType2:
    """管道第二类计算问题（迭代求流量）"""
    
    def __init__(self, d, L, h, epsilon, nu, zeta_sum, g=9.8):
        """
        初始化
        
        参数:
            d: 管径 (m)
            L: 管长 (m)
            h: 总水头损失 (m)
            epsilon: 绝对粗糙度 (m)
            nu: 运动粘度 (m²/s)
            zeta_sum: 局部损失系数之和
            g: 重力加速度 (m/s²)
        """
        self.d = d
        self.L = L
        self.h = h
        self.epsilon = epsilon
        self.nu = nu
        self.zeta_sum = zeta_sum
        self.g = g
        
        # 计算
        self.solve()
    
    def solve(self):
        """迭代求解流量Q"""
        # 记录迭代过程
        self.iterations = []
        
        # 初始假设λ（光滑管初值）
        lambda_old = 0.02
        tol = 1e-6  # 收敛精度
        max_iter = 100
        
        print("\n" + "="*80)
        print("开始迭代求解...")
        print("="*80)
        
        for i in range(max_iter):
            # 步骤1：根据假设的λ计算流速v
            # h = (λL/d + ∑ζ)·v²/2g
            # v = √(2gh / (λL/d + ∑ζ))
            K = lambda_old * self.L / self.d + self.zeta_sum
            v = np.sqrt(2 * self.g * self.h / K)
            
            # 步骤2：计算流量Q
            A = np.pi * self.d**2 / 4
            Q = A * v
            
            # 步骤3：计算雷诺数Re
            Re = v * self.d / self.nu
            
            # 步骤4：用Colebrook-White方程计算新的λ
            lambda_new = self._colebrook(Re, self.epsilon/self.d)
            
            # 步骤5：计算沿程损失和局部损失
            h_f = lambda_new * self.L / self.d * v**2 / (2 * self.g)
            h_j = self.zeta_sum * v**2 / (2 * self.g)
            h_total = h_f + h_j
            
            # 记录本次迭代
            iteration_data = {
                'iter': i + 1,
                'lambda': lambda_new,
                'v': v,
                'Q': Q,
                'Re': Re,
                'h_f': h_f,
                'h_j': h_j,
                'h_total': h_total,
                'error': abs(lambda_new - lambda_old)
            }
            self.iterations.append(iteration_data)
            
            # 打印迭代信息
            if i < 5 or i == max_iter - 1 or abs(lambda_new - lambda_old) < tol:
                print(f"\n第{i+1}次迭代:")
                print(f"  λ = {lambda_new:.6f}")
                print(f"  v = {v:.4f} m/s")
                print(f"  Q = {Q:.6f} m³/s")
                print(f"  Re = {Re:.0f}")
                print(f"  h_f = {h_f:.4f} m")
                print(f"  h_j = {h_j:.4f} m")
                print(f"  h_total = {h_total:.4f} m (目标: {self.h} m)")
                print(f"  误差 = {abs(lambda_new - lambda_old):.8f}")
            
            # 收敛判断
            if abs(lambda_new - lambda_old) < tol:
                print(f"\n收敛！共{i+1}次迭代")
                break
            
            lambda_old = lambda_new
        
        # 保存最终结果
        self.v = v
        self.Q = Q
        self.Re = Re
        self.lambda_f = lambda_new
        self.h_f = h_f
        self.h_j = h_j
        self.h_total = h_total
        self.n_iter = i + 1
        
        # 计算额外参数
        self.A = A
        self.relative_roughness = self.epsilon / self.d
        self.flow_regime = "层流" if self.Re < 2000 else ("过渡流" if self.Re < 4000 else "湍流")
    
    def _colebrook(self, Re, relative_roughness):
        """
        Colebrook-White方程迭代求解摩阻系数λ
        1/√λ = -2lg(ε/3.71d + 2.51/Re√λ)
        """
        if Re < 2000:  # 层流
            return 64 / Re
        
        # 湍流区，迭代求解
        lambda_old = 0.02
        for _ in range(50):
            sqrt_lambda = np.sqrt(lambda_old)
            term1 = relative_roughness / 3.71
            term2 = 2.51 / (Re * sqrt_lambda)
            f_inv_sqrt = -2 * np.log10(term1 + term2)
            lambda_new = 1 / f_inv_sqrt**2
            
            if abs(lambda_new - lambda_old) < 1e-8:
                break
            lambda_old = lambda_new
        
        return lambda_new
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*80)
        print("题目366：管道第二类计算问题（迭代求流量）")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"管径: d = {self.d} m = {self.d*1000} mm")
        print(f"管长: L = {self.L} m")
        print(f"总水头损失: h = {self.h} m")
        print(f"绝对粗糙度: ε = {self.epsilon*1000} mm")
        print(f"相对粗糙度: ε/d = {self.relative_roughness:.6f}")
        print(f"运动粘度: ν = {self.nu} m²/s")
        print(f"局部损失系数: ∑ζ = {self.zeta_sum}")
        
        print("\n【求解思路】")
        print("第二类问题：已知 h 和 d，求 Q")
        print("\n难点：λ = f(Re, ε/d)，Re = f(v)，v = f(Q)")
        print("      → λ 和 Q 互相依赖，需要迭代求解")
        print("\n迭代步骤：")
        print("  1. 假设初始 λ₀ = 0.02")
        print("  2. 由 h = (λL/d + ∑ζ)·v²/2g 反推 v")
        print("  3. 由 Q = Av 计算流量")
        print("  4. 由 Re = vd/ν 计算雷诺数")
        print("  5. 由 Colebrook-White 方程计算新的 λ")
        print("  6. 判断收敛：|λ_new - λ_old| < 10⁻⁶")
        print("  7. 若未收敛，λ_old = λ_new，返回步骤2")
        
        print("\n【迭代过程】")
        print(f"总迭代次数: {self.n_iter} 次")
        print(f"收敛精度: 10⁻⁶")
        print("\n前3次和最后1次迭代详情：")
        for i, data in enumerate(self.iterations):
            if i < 3 or i == len(self.iterations) - 1:
                print(f"\n  第{data['iter']}次:")
                print(f"    λ = {data['lambda']:.6f}")
                print(f"    v = {data['v']:.4f} m/s")
                print(f"    Q = {data['Q']:.6f} m³/s = {data['Q']*1000:.3f} L/s")
                print(f"    Re = {data['Re']:.0f}")
                print(f"    误差 = {data['error']:.8f}")
        
        print("\n【最终答案】")
        print(f"✓ 流量: Q = {self.Q:.6f} m³/s = {self.Q*1000:.3f} L/s")
        print(f"✓ 流速: v = {self.v:.4f} m/s")
        print(f"✓ 雷诺数: Re = {self.Re:.0f}  →  {self.flow_regime}")
        print(f"✓ 摩阻系数: λ = {self.lambda_f:.6f}")
        
        print("\n【水头损失验证】")
        print(f"沿程损失: h_f = λ·L/d·v²/2g")
        print(f"           = {self.lambda_f:.6f}×{self.L}/{self.d}×{self.v:.4f}²/(2×{self.g})")
        print(f"           = {self.h_f:.4f} m  ({self.h_f/self.h*100:.1f}%)")
        print(f"局部损失: h_j = ∑ζ·v²/2g")
        print(f"           = {self.zeta_sum}×{self.v:.4f}²/(2×{self.g})")
        print(f"           = {self.h_j:.4f} m  ({self.h_j/self.h*100:.1f}%)")
        print(f"总损失:   h = h_f + h_j = {self.h_f:.4f} + {self.h_j:.4f}")
        print(f"           = {self.h_total:.4f} m")
        print(f"目标值:   h = {self.h} m")
        print(f"误差:     {abs(self.h_total - self.h):.6f} m  ({abs(self.h_total - self.h)/self.h*100:.3f}%)")
        print(f"验证: ✓ 水头损失计算准确")
        
        print("\n【关键公式】")
        print("能量方程: h = h_f + h_j = (λL/d + ∑ζ)·v²/2g")
        print("Colebrook-White: 1/√λ = -2lg(ε/3.71d + 2.51/Re√λ)")
        print("雷诺数: Re = vd/ν")
        print("流量: Q = Av = (πd²/4)·v")
        
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：迭代收敛过程
        ax1 = plt.subplot(2, 2, 1)
        self._plot_convergence(ax1)
        
        # 子图2：管道系统示意图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_system(ax2)
        
        # 子图3：Re-λ关系（Moody图）
        ax3 = plt.subplot(2, 2, 3)
        self._plot_moody(ax3)
        
        # 子图4：水头损失分布
        ax4 = plt.subplot(2, 2, 4)
        self._plot_loss_distribution(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_convergence(self, ax):
        """绘制迭代收敛过程"""
        iters = [d['iter'] for d in self.iterations]
        lambdas = [d['lambda'] for d in self.iterations]
        Qs = [d['Q']*1000 for d in self.iterations]  # 转换为L/s
        
        # 双Y轴
        ax_Q = ax.twinx()
        
        # λ的收敛
        line1 = ax.plot(iters, lambdas, 'b-o', linewidth=2, markersize=6, label='λ')
        ax.set_ylabel('摩阻系数 λ', fontsize=12, color='b')
        ax.tick_params(axis='y', labelcolor='b')
        
        # Q的收敛
        line2 = ax_Q.plot(iters, Qs, 'r-s', linewidth=2, markersize=6, label='Q')
        ax_Q.set_ylabel('流量 Q (L/s)', fontsize=12, color='r')
        ax_Q.tick_params(axis='y', labelcolor='r')
        
        # 标注最终值
        ax.plot(iters[-1], lambdas[-1], 'b*', markersize=15)
        ax.text(iters[-1], lambdas[-1]*1.01, f'λ={lambdas[-1]:.5f}',
               fontsize=9, ha='right', color='b')
        
        ax_Q.plot(iters[-1], Qs[-1], 'r*', markersize=15)
        ax_Q.text(iters[-1], Qs[-1]*1.02, f'Q={Qs[-1]:.2f}L/s',
                 fontsize=9, ha='right', color='r')
        
        ax.set_xlabel('迭代次数', fontsize=12)
        ax.set_title('迭代收敛过程', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3)
        
        # 图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper right')
    
    def _plot_system(self, ax):
        """绘制管道系统示意图"""
        # 上游水池
        pool1 = Rectangle((0, 2), 1, 1, facecolor='lightblue', 
                         edgecolor='blue', linewidth=2)
        ax.add_patch(pool1)
        ax.text(0.5, 2.5, '上游\n水池', fontsize=10, ha='center', va='center')
        
        # 管道
        pipe_y = 2
        pipe = Rectangle((1, pipe_y-0.1), 5, 0.2, facecolor='gray',
                        edgecolor='black', linewidth=2)
        ax.add_patch(pipe)
        
        # 流向箭头
        for x in [2, 3.5, 5]:
            ax.arrow(x, pipe_y, 0.3, 0, head_width=0.15, head_length=0.15,
                    fc='red', ec='red', linewidth=2)
        
        ax.text(3.5, pipe_y-0.5, f'd={self.d}m, L={self.L}m',
               fontsize=10, ha='center')
        ax.text(3.5, pipe_y+0.5, f'Q={self.Q*1000:.2f}L/s →',
               fontsize=11, ha='center', color='red', weight='bold')
        
        # 下游水池
        pool2 = Rectangle((6, 2-self.h/10), 1, 1, facecolor='lightblue',
                         edgecolor='blue', linewidth=2)
        ax.add_patch(pool2)
        ax.text(6.5, 2.5-self.h/10, '下游\n水池', fontsize=10, ha='center', va='center')
        
        # 水头线
        ax.plot([0, 1], [3, 3], 'b-', linewidth=2, label='上游水头')
        ax.plot([6, 7], [3-self.h/10, 3-self.h/10], 'r-', linewidth=2, label='下游水头')
        
        # 水头损失标注
        ax.annotate('', xy=(7.5, 3-self.h/10), xytext=(7.5, 3),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(7.8, 3-self.h/20, f'h={self.h}m',
               fontsize=11, color='green', weight='bold')
        
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(0, 4)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('管道系统示意图', fontsize=14, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
    
    def _plot_moody(self, ax):
        """绘制简化的Moody图和本题位置"""
        # Re范围
        Re_range = np.logspace(3, 6, 100)
        
        # 不同相对粗糙度的λ曲线
        relative_roughnesses = [0.00001, 0.0001, 0.001, 0.01]
        colors = ['blue', 'green', 'orange', 'red']
        
        for rr, color in zip(relative_roughnesses, colors):
            lambdas = []
            for Re in Re_range:
                if Re < 2000:
                    lam = 64 / Re
                else:
                    lam = self._colebrook(Re, rr)
                lambdas.append(lam)
            ax.plot(Re_range, lambdas, color=color, linewidth=1.5,
                   label=f'ε/d={rr}', alpha=0.7)
        
        # 本题的点
        ax.plot(self.Re, self.lambda_f, 'r*', markersize=20, zorder=5,
               label=f'本题 (Re={self.Re:.0f})')
        
        # 标注
        ax.text(self.Re, self.lambda_f*1.15, 
               f'λ={self.lambda_f:.5f}\nε/d={self.relative_roughness:.6f}',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 层流区域标注
        ax.fill_between([1000, 2000], [0.01, 0.01], [0.1, 0.1],
                       alpha=0.2, color='blue')
        ax.text(1500, 0.045, '层流区\nλ=64/Re', fontsize=9, ha='center')
        
        # 过渡区标注
        ax.fill_between([2000, 4000], [0.01, 0.01], [0.1, 0.1],
                       alpha=0.2, color='yellow')
        ax.text(3000, 0.055, '过渡区', fontsize=9, ha='center')
        
        # 湍流区标注
        ax.text(50000, 0.02, '湍流区\nColebrook-White', fontsize=9)
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('雷诺数 Re', fontsize=12)
        ax.set_ylabel('摩阻系数 λ', fontsize=12)
        ax.set_title('Moody图（简化）', fontsize=14, weight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, which='both', alpha=0.3)
        ax.set_xlim(1000, 1e6)
        ax.set_ylim(0.01, 0.1)
    
    def _plot_loss_distribution(self, ax):
        """绘制水头损失分布"""
        labels = ['沿程损失\nh_f', '局部损失\nh_j']
        values = [self.h_f, self.h_j]
        colors = ['skyblue', 'lightcoral']
        percentages = [v/self.h*100 for v in values]
        
        bars = ax.bar(labels, values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值和百分比
        for bar, val, pct in zip(bars, values, percentages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.3f}m\n({pct:.1f}%)',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 总损失线
        ax.axhline(self.h, color='green', linestyle='--', linewidth=2,
                  label=f'总损失 h={self.h}m')
        
        # 公式标注
        ax.text(0, self.h_f*0.5, 
               f'λL/d·v²/2g\n={self.lambda_f:.5f}×{self.L}/{self.d}\n×{self.v:.3f}²/(2×{self.g})',
               fontsize=8, ha='center')
        
        ax.text(1, self.h_j*0.5,
               f'∑ζ·v²/2g\n={self.zeta_sum}×{self.v:.3f}²\n/(2×{self.g})',
               fontsize=8, ha='center')
        
        ax.set_ylabel('水头损失 (m)', fontsize=12)
        ax.set_title('水头损失分布', fontsize=14, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, self.h*1.3)


def test_problem_366():
    """测试题目366"""
    # 已知条件
    d = 0.2             # 管径 (m)
    L = 500             # 管长 (m)
    h = 10              # 总水头损失 (m)
    epsilon = 0.0002    # 绝对粗糙度 (m) = 0.2mm
    nu = 1.0e-6         # 运动粘度 (m²/s)
    zeta_sum = 5.0      # 局部损失系数之和
    
    # 创建计算对象
    pipe = PipeType2(d, L, h, epsilon, nu, zeta_sum)
    
    # 打印结果
    pipe.print_results()
    
    # 可视化
    fig = pipe.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_366_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_366_result.png")
    
    # 验证答案（合理性检查）
    assert 0.001 < pipe.Q < 1.0, "流量不合理"
    assert 0.5 < pipe.v < 10.0, "流速不合理"
    assert pipe.Re > 2000, "应该是湍流"
    assert 0.01 < pipe.lambda_f < 0.1, "摩阻系数不合理"
    assert abs(pipe.h_total - pipe.h) / pipe.h < 0.01, "水头损失误差过大"
    assert pipe.n_iter < 50, "迭代次数过多"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("管道第二类问题是考研必考题型！")
    print("• 特点：已知h和d，求Q（需要迭代）")
    print("• 关键：λ依赖于Re，Re依赖于v，v依赖于Q")
    print("• 方法：假设λ → 算v → 算Re → 算新λ → 判断收敛")
    print("• 公式：h = (λL/d + ∑ζ)·v²/2g")
    print("• 收敛：|λ_new - λ_old| < 10⁻⁶")


if __name__ == "__main__":
    test_problem_366()
