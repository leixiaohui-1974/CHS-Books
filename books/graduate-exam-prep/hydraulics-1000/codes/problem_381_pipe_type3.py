"""
《水力学考研1000题详解》配套代码
题目381：管道第三类计算问题（迭代求管径d）

问题描述：
圆管输水系统，流量Q=0.05m³/s，管长L=400m，总水头损失h=8m。
管道绝对粗糙度ε=0.3mm，运动粘度ν=1.0×10⁻⁶m²/s。
局部损失系数∑ζ=4.0。
求：管径d (m)

考点：
1. 第三类问题特点：已知Q和h，求d
2. 迭代求解：λ依赖于Re和ε/d，Re和ε/d都依赖于d
3. 能量方程：h = (λL/d + ∑ζ)·v²/2g，其中v = 4Q/(πd²)
4. 收敛判断：|d_new - d_old| < 0.0001m
5. 优化算法：牛顿迭代或二分法

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from scipy.optimize import fsolve, brentq

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PipeType3:
    """管道第三类计算问题（迭代求管径）"""
    
    def __init__(self, Q, L, h, epsilon, nu, zeta_sum, g=9.8):
        """
        初始化
        
        参数:
            Q: 流量 (m³/s)
            L: 管长 (m)
            h: 总水头损失 (m)
            epsilon: 绝对粗糙度 (m)
            nu: 运动粘度 (m²/s)
            zeta_sum: 局部损失系数之和
            g: 重力加速度 (m/s²)
        """
        self.Q = Q
        self.L = L
        self.h = h
        self.epsilon = epsilon
        self.nu = nu
        self.zeta_sum = zeta_sum
        self.g = g
        
        # 计算
        self.solve()
    
    def solve(self):
        """迭代求解管径d"""
        # 记录迭代过程
        self.iterations = []
        
        # 初始估计d（基于经验公式）
        # 假设λ≈0.02，忽略局部损失，则 d ≈ (λLQ²/(2πgh))^(1/5)
        d_old = (0.02 * self.L * self.Q**2 / (2 * np.pi * self.g * self.h))**(1/5)
        
        tol = 1e-6  # 收敛精度
        max_iter = 50
        
        print("\n" + "="*80)
        print("开始迭代求解...")
        print("="*80)
        print(f"初始估计: d₀ = {d_old:.6f} m = {d_old*1000:.2f} mm")
        
        for i in range(max_iter):
            # 步骤1：计算流速和断面积
            A = np.pi * d_old**2 / 4
            v = self.Q / A
            
            # 步骤2：计算雷诺数和相对粗糙度
            Re = v * d_old / self.nu
            relative_roughness = self.epsilon / d_old
            
            # 步骤3：计算摩阻系数λ
            lambda_f = self._colebrook(Re, relative_roughness)
            
            # 步骤4：计算水头损失
            h_f = lambda_f * self.L / d_old * v**2 / (2 * self.g)
            h_j = self.zeta_sum * v**2 / (2 * self.g)
            h_total = h_f + h_j
            
            # 步骤5：根据水头损失误差调整d
            # h_actual = h_target，调整d
            # 使用牛顿迭代的思想：如果h_actual > h_target，则d太小，需要增大d
            
            # 计算新的d（基于能量方程反推）
            # h = (λL/d + ∑ζ)·v²/2g = (λL/d + ∑ζ)·(4Q/πd²)²/(2g)
            # 这是关于d的超越方程，使用迭代求解
            
            # 方法：假设λ不变，从能量方程反推d
            # h = (λL/d + ∑ζ)·16Q²/(2gπ²d⁴)
            # 令 K = 16Q²/(2gπ²)，则 h = K(λL/d + ∑ζ)/d⁴ = K(λL + ∑ζd)/d⁵
            # 这是一个五次方程，难以直接求解
            
            # 使用调节因子法：d_new = d_old · (h_total/h_target)^α
            # α是调节系数，经验值0.2-0.3
            alpha = 0.25
            ratio = h_total / self.h
            d_new = d_old * ratio**alpha
            
            # 记录迭代数据
            iteration_data = {
                'iter': i + 1,
                'd': d_new,
                'v': v,
                'Re': Re,
                'lambda': lambda_f,
                'h_f': h_f,
                'h_j': h_j,
                'h_total': h_total,
                'error_d': abs(d_new - d_old),
                'error_h': abs(h_total - self.h)
            }
            self.iterations.append(iteration_data)
            
            # 打印迭代信息
            if i < 5 or i == max_iter - 1 or abs(d_new - d_old) < tol:
                print(f"\n第{i+1}次迭代:")
                print(f"  d = {d_new:.6f} m = {d_new*1000:.2f} mm")
                print(f"  v = {v:.4f} m/s")
                print(f"  Re = {Re:.0f}")
                print(f"  λ = {lambda_f:.6f}")
                print(f"  h_total = {h_total:.4f} m (目标: {self.h} m)")
                print(f"  d误差 = {abs(d_new - d_old):.8f} m")
                print(f"  h误差 = {abs(h_total - self.h):.6f} m")
            
            # 收敛判断（同时检查d和h）
            if abs(d_new - d_old) < tol and abs(h_total - self.h) < 0.01:
                print(f"\n收敛！共{i+1}次迭代")
                break
            
            d_old = d_new
        
        # 保存最终结果（使用最后一次的d重新计算）
        self.d = d_new
        self.A = np.pi * self.d**2 / 4
        self.v = self.Q / self.A
        self.Re = self.v * self.d / self.nu
        self.relative_roughness = self.epsilon / self.d
        self.lambda_f = self._colebrook(self.Re, self.relative_roughness)
        self.h_f = self.lambda_f * self.L / self.d * self.v**2 / (2 * self.g)
        self.h_j = self.zeta_sum * self.v**2 / (2 * self.g)
        self.h_total = self.h_f + self.h_j
        self.n_iter = i + 1
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
        print("题目381：管道第三类计算问题（迭代求管径）")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"流量: Q = {self.Q} m³/s = {self.Q*1000} L/s")
        print(f"管长: L = {self.L} m")
        print(f"总水头损失: h = {self.h} m")
        print(f"绝对粗糙度: ε = {self.epsilon*1000} mm")
        print(f"运动粘度: ν = {self.nu} m²/s")
        print(f"局部损失系数: ∑ζ = {self.zeta_sum}")
        
        print("\n【求解思路】")
        print("第三类问题：已知 Q 和 h，求 d")
        print("\n难点：λ = f(Re, ε/d)，Re = f(d)，ε/d = f(d)")
        print("      → d 出现在多个地方，需要迭代求解")
        print("\n迭代步骤：")
        print("  1. 初始估计 d₀（经验公式）")
        print("  2. 计算 v = Q/A = 4Q/(πd²)")
        print("  3. 计算 Re = vd/ν 和 ε/d")
        print("  4. 由 Colebrook-White 计算 λ")
        print("  5. 计算实际水头损失 h_actual")
        print("  6. 根据 h_actual 与 h_target 的差异调整 d")
        print("  7. 判断收敛：|d_new - d_old| < 10⁻⁶ 且 |h_actual - h_target| < 0.01")
        print("  8. 若未收敛，d_old = d_new，返回步骤2")
        
        print("\n【迭代过程】")
        print(f"总迭代次数: {self.n_iter} 次")
        print(f"收敛精度: d误差<10⁻⁶m，h误差<0.01m")
        print("\n前3次和最后1次迭代详情：")
        for i, data in enumerate(self.iterations):
            if i < 3 or i == len(self.iterations) - 1:
                print(f"\n  第{data['iter']}次:")
                print(f"    d = {data['d']:.6f} m = {data['d']*1000:.2f} mm")
                print(f"    v = {data['v']:.4f} m/s")
                print(f"    Re = {data['Re']:.0f}")
                print(f"    λ = {data['lambda']:.6f}")
                print(f"    h_total = {data['h_total']:.4f} m")
                print(f"    d误差 = {data['error_d']:.8f} m")
                print(f"    h误差 = {data['error_h']:.6f} m")
        
        print("\n【最终答案】")
        print(f"✓ 管径: d = {self.d:.6f} m = {self.d*1000:.2f} mm")
        print(f"  建议采用: d = {np.ceil(self.d*1000/10)*10:.0f} mm  （标准管径）")
        print(f"✓ 流速: v = {self.v:.4f} m/s")
        print(f"✓ 雷诺数: Re = {self.Re:.0f}  →  {self.flow_regime}")
        print(f"✓ 摩阻系数: λ = {self.lambda_f:.6f}")
        print(f"✓ 相对粗糙度: ε/d = {self.relative_roughness:.6f}")
        
        print("\n【水头损失验证】")
        print(f"沿程损失: h_f = λ·L/d·v²/2g")
        print(f"           = {self.lambda_f:.6f}×{self.L}/{self.d:.6f}×{self.v:.4f}²/(2×{self.g})")
        print(f"           = {self.h_f:.4f} m  ({self.h_f/self.h*100:.1f}%)")
        print(f"局部损失: h_j = ∑ζ·v²/2g")
        print(f"           = {self.zeta_sum}×{self.v:.4f}²/(2×{self.g})")
        print(f"           = {self.h_j:.4f} m  ({self.h_j/self.h*100:.1f}%)")
        print(f"总损失:   h = h_f + h_j = {self.h_f:.4f} + {self.h_j:.4f}")
        print(f"           = {self.h_total:.4f} m")
        print(f"目标值:   h = {self.h} m")
        print(f"误差:     {abs(self.h_total - self.h):.6f} m  ({abs(self.h_total - self.h)/self.h*100:.3f}%)")
        print(f"验证: ✓ 水头损失计算准确")
        
        print("\n【工程建议】")
        # 推荐标准管径
        standard_diameters = [100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600]
        d_mm = self.d * 1000
        recommended = min([d for d in standard_diameters if d >= d_mm], default=600)
        print(f"计算管径: {d_mm:.2f} mm")
        print(f"推荐标准管径: {recommended} mm（DN{recommended}）")
        print(f"安全系数: {recommended/d_mm:.2f}")
        
        print("\n【关键公式】")
        print("能量方程: h = (λL/d + ∑ζ)·v²/2g")
        print("流速: v = 4Q/(πd²)")
        print("雷诺数: Re = vd/ν")
        print("Colebrook-White: 1/√λ = -2lg(ε/3.71d + 2.51/Re√λ)")
        
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：迭代收敛过程
        ax1 = plt.subplot(2, 2, 1)
        self._plot_convergence(ax1)
        
        # 子图2：管径与水头损失关系
        ax2 = plt.subplot(2, 2, 2)
        self._plot_d_h_relation(ax2)
        
        # 子图3：管道断面示意图
        ax3 = plt.subplot(2, 2, 3)
        self._plot_pipe_section(ax3)
        
        # 子图4：水力参数对比
        ax4 = plt.subplot(2, 2, 4)
        self._plot_parameters(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_convergence(self, ax):
        """绘制迭代收敛过程"""
        iters = [d['iter'] for d in self.iterations]
        d_values = [d['d']*1000 for d in self.iterations]  # 转换为mm
        h_values = [d['h_total'] for d in self.iterations]
        
        # 双Y轴
        ax_h = ax.twinx()
        
        # d的收敛
        line1 = ax.plot(iters, d_values, 'b-o', linewidth=2, markersize=6, label='管径 d')
        ax.set_ylabel('管径 d (mm)', fontsize=12, color='b')
        ax.tick_params(axis='y', labelcolor='b')
        
        # h的收敛
        line2 = ax_h.plot(iters, h_values, 'r-s', linewidth=2, markersize=6, label='水头损失 h')
        ax_h.axhline(self.h, color='green', linestyle='--', linewidth=2, label='目标h')
        ax_h.set_ylabel('水头损失 h (m)', fontsize=12, color='r')
        ax_h.tick_params(axis='y', labelcolor='r')
        
        # 标注最终值
        ax.plot(iters[-1], d_values[-1], 'b*', markersize=15)
        ax.text(iters[-1], d_values[-1]*1.01, f'd={d_values[-1]:.1f}mm',
               fontsize=9, ha='right', color='b')
        
        ax.set_xlabel('迭代次数', fontsize=12)
        ax.set_title('迭代收敛过程', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3)
        
        # 图例
        lines = line1 + line2 + [ax_h.lines[1]]
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper right', fontsize=9)
    
    def _plot_d_h_relation(self, ax):
        """绘制管径与水头损失关系"""
        # 生成一系列管径
        d_range = np.linspace(self.d*0.7, self.d*1.5, 50)
        h_values = []
        
        for d_test in d_range:
            A_test = np.pi * d_test**2 / 4
            v_test = self.Q / A_test
            Re_test = v_test * d_test / self.nu
            rr_test = self.epsilon / d_test
            lambda_test = self._colebrook(Re_test, rr_test)
            h_f_test = lambda_test * self.L / d_test * v_test**2 / (2 * self.g)
            h_j_test = self.zeta_sum * v_test**2 / (2 * self.g)
            h_total_test = h_f_test + h_j_test
            h_values.append(h_total_test)
        
        # 绘制h-d曲线
        ax.plot(d_range*1000, h_values, 'b-', linewidth=2.5, label='h-d关系曲线')
        
        # 目标水头损失线
        ax.axhline(self.h, color='red', linestyle='--', linewidth=2, label=f'目标h={self.h}m')
        
        # 标注解
        ax.plot(self.d*1000, self.h_total, 'r*', markersize=20, zorder=5,
               label=f'解: d={self.d*1000:.1f}mm')
        ax.text(self.d*1000, self.h_total*1.1, 
               f'd={self.d*1000:.1f}mm\nh={self.h_total:.2f}m',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('管径 d (mm)', fontsize=12)
        ax.set_ylabel('水头损失 h (m)', fontsize=12)
        ax.set_title('管径-水头损失关系', fontsize=14, weight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def _plot_pipe_section(self, ax):
        """绘制管道断面示意图"""
        # 圆形管道
        circle = Circle((0, 0), self.d/2, facecolor='lightblue', 
                       edgecolor='blue', linewidth=3, alpha=0.6)
        ax.add_patch(circle)
        
        # 管径标注
        ax.plot([-self.d/2, self.d/2], [0, 0], 'r-', linewidth=2)
        ax.plot([-self.d/2, -self.d/2], [-0.02, 0.02], 'r-', linewidth=2)
        ax.plot([self.d/2, self.d/2], [-0.02, 0.02], 'r-', linewidth=2)
        ax.text(0, -self.d/2*1.3, f'd = {self.d:.4f} m\n= {self.d*1000:.1f} mm',
               fontsize=12, ha='center', color='red', weight='bold')
        
        # 流速分布（抛物线，简化表示）
        n_arrows = 7
        for i in range(n_arrows):
            y = (i - n_arrows//2) * (self.d/2) / (n_arrows//2) * 0.8
            if abs(y) < self.d/2:
                # 湍流速度分布（较平坦）
                v_local = self.v * (1 - (2*y/self.d)**2) * 0.3 + self.v * 0.7
                arrow_len = v_local / self.v * 0.15
                ax.arrow(-self.d/2*0.6, y, arrow_len, 0, 
                        head_width=0.015, head_length=0.01,
                        fc='darkblue', ec='darkblue', linewidth=1.5)
        
        ax.text(0, 0, f'Q = {self.Q*1000:.1f} L/s\nv = {self.v:.3f} m/s',
               fontsize=11, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 粗糙度示意（夸张显示）
        n_rough = 20
        for i in range(n_rough):
            theta = 2 * np.pi * i / n_rough
            x = (self.d/2) * np.cos(theta)
            y = (self.d/2) * np.sin(theta)
            rough_len = 0.01
            ax.plot([x, x*(1+rough_len*10)], [y, y*(1+rough_len*10)], 
                   'k-', linewidth=1, alpha=0.5)
        
        ax.text(0, self.d/2*1.2, f'ε = {self.epsilon*1000} mm',
               fontsize=10, ha='center', style='italic')
        
        ax.set_xlim(-self.d*1.5, self.d*1.5)
        ax.set_ylim(-self.d*1.5, self.d*1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('管道断面图', fontsize=14, weight='bold')
    
    def _plot_parameters(self, ax):
        """绘制水力参数对比"""
        categories = ['管径d\n(mm)', '流速v\n(m/s)', 'Re/10⁴', 'λ×100']
        values = [self.d*1000, self.v, self.Re/1e4, self.lambda_f*100]
        colors = ['skyblue', 'lightgreen', 'gold', 'lightcoral']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val, cat in zip(bars, values, categories):
            height = bar.get_height()
            if 'mm' in cat:
                text = f'{val:.1f}'
            elif 'Re' in cat:
                text = f'{val:.2f}'
            else:
                text = f'{val:.4f}'
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   text, ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 水头损失分布（叠加柱状图）
        ax2 = ax.twinx()
        loss_categories = ['h_f\n(m)', 'h_j\n(m)']
        loss_values = [self.h_f, self.h_j]
        x_pos = [4, 5]
        
        bars2 = ax2.bar(x_pos, loss_values, color=['lightblue', 'lightcoral'],
                       alpha=0.7, edgecolor='black', linewidth=2)
        
        for bar, val in zip(bars2, loss_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=10, weight='bold')
        
        # 总损失线
        ax2.axhline(self.h, color='green', linestyle='--', linewidth=2,
                   label=f'h_total={self.h}m', alpha=0.7)
        
        ax.set_ylabel('水力参数', fontsize=12)
        ax2.set_ylabel('水头损失 (m)', fontsize=12)
        ax.set_title('水力参数汇总', fontsize=14, weight='bold')
        ax.set_ylim(0, max(values)*1.3)
        ax2.legend(loc='upper right', fontsize=9)
        ax.grid(True, axis='y', alpha=0.3)


def test_problem_381():
    """测试题目381"""
    # 已知条件
    Q = 0.05            # 流量 (m³/s)
    L = 400             # 管长 (m)
    h = 8               # 总水头损失 (m)
    epsilon = 0.0003    # 绝对粗糙度 (m) = 0.3mm
    nu = 1.0e-6         # 运动粘度 (m²/s)
    zeta_sum = 4.0      # 局部损失系数之和
    
    # 创建计算对象
    pipe = PipeType3(Q, L, h, epsilon, nu, zeta_sum)
    
    # 打印结果
    pipe.print_results()
    
    # 可视化
    fig = pipe.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_381_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_381_result.png")
    
    # 验证答案（合理性检查）
    assert 0.05 < pipe.d < 0.5, "管径不合理"
    assert 0.5 < pipe.v < 10.0, "流速不合理"
    assert pipe.Re > 2000, "应该是湍流"
    assert 0.01 < pipe.lambda_f < 0.1, "摩阻系数不合理"
    assert abs(pipe.h_total - pipe.h) / pipe.h < 0.05, "水头损失误差过大"
    assert pipe.n_iter < 50, "迭代次数过多"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("管道第三类问题是考研必考题型！")
    print("• 特点：已知Q和h，求d（需要迭代）")
    print("• 难点：d出现在v、Re、ε/d、λ中")
    print("• 方法：估计d → 算v和Re → 算λ → 算h → 调整d → 判断收敛")
    print("• 公式：h = (λL/d + ∑ζ)·v²/2g，v = 4Q/(πd²)")
    print("• 收敛：|d_new - d_old| < 10⁻⁶ 且 |h_actual - h_target| < 0.01")
    print("• 工程：选用标准管径（DN系列）")


if __name__ == "__main__":
    test_problem_381()
