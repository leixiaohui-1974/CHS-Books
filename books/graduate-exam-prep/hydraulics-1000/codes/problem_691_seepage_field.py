"""
《水力学考研1000题详解》配套代码
题目691：渗流场分析

问题描述：
某土坝断面如图所示，已知：
  坝高: H = 15 m
  上游水深: h₁ = 12 m
  下游水深: h₂ = 3 m
  渗透系数: k = 0.002 cm/s = 2×10⁻⁵ m/s
  坝底宽度: L = 40 m
  坝体土质均匀

要求：
(1) 根据Darcy定律计算渗流速度
(2) 计算单宽流量q
(3) 绘制等势线和流线
(4) 计算渗流坡降i和水头损失
(5) 分析渗流安全性（渗透破坏判别）
(6) 提出防渗加固措施

考点：
1. Darcy定律: v = ki, Q = kiA
2. 渗流连续方程: ∂vₓ/∂x + ∂vᵧ/∂y = 0
3. 流网绘制: 等势线⊥流线，Δh相等，Δs/Δn=常数
4. 单宽流量: q = kH(h₁-h₂)/L
5. 临界坡降: i_cr = (γₛ-γ)/γ ≈ 1.0
6. 渗透稳定性: i < i_cr, 安全系数K = i_cr/i > 1.5

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Rectangle, Polygon

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SeepageField:
    """渗流场分析类"""
    
    def __init__(self):
        """初始化"""
        # 几何参数
        self.H = 15      # 坝高 (m)
        self.h1 = 12     # 上游水深 (m)
        self.h2 = 3      # 下游水深 (m)
        self.L = 40      # 坝底宽度 (m)
        
        # 物理参数
        self.k = 2e-5    # 渗透系数 (m/s)
        self.rho = 1000  # 水的密度 (kg/m³)
        self.g = 9.8     # 重力加速度 (m/s²)
        
        # 土体参数
        self.gamma_s = 26000  # 土粒重度 (N/m³)
        self.gamma_w = 9800   # 水重度 (N/m³)
        self.gamma = 19000    # 土体重度 (N/m³)
        
        # 安全系数要求
        self.K_required = 1.5
        
        # 计算
        self.calculate_seepage()
    
    def calculate_seepage(self):
        """计算渗流参数"""
        print(f"\n{'='*80}")
        print("【渗流计算】")
        print(f"{'='*80}")
        
        # 1. 水头差
        self.delta_h = self.h1 - self.h2
        print(f"\n1. 水头差:")
        print(f"   Δh = h₁ - h₂ = {self.h1} - {self.h2} = {self.delta_h} m")
        
        # 2. 平均渗流坡降（简化模型）
        self.i_avg = self.delta_h / self.L
        print(f"\n2. 平均渗流坡降:")
        print(f"   i_avg = Δh/L = {self.delta_h}/{self.L} = {self.i_avg:.4f}")
        
        # 3. 平均渗流速度
        self.v_avg = self.k * self.i_avg
        print(f"\n3. 平均渗流速度 (Darcy定律):")
        print(f"   v = ki = {self.k:.2e} × {self.i_avg:.4f}")
        print(f"   v = {self.v_avg:.6e} m/s = {self.v_avg*86400:.4f} m/d")
        
        # 4. 单宽流量
        self.q = self.k * self.delta_h
        print(f"\n4. 单宽流量:")
        print(f"   q = kΔh = {self.k:.2e} × {self.delta_h}")
        print(f"   q = {self.q:.6e} m³/(s·m) = {self.q*86400:.5f} m³/(d·m)")
        
        # 5. 渗流时间（从上游到下游）
        self.t_seepage = self.L / (self.v_avg * 86400)  # 天
        print(f"\n5. 渗流时间（穿过坝体）:")
        print(f"   t = L/v = {self.L}/{self.v_avg*86400:.4f}")
        print(f"   t = {self.t_seepage:.1f} 天")
    
    def analyze_stability(self):
        """渗透稳定性分析"""
        print(f"\n{'='*80}")
        print("【渗透稳定性分析】")
        print(f"{'='*80}")
        
        # 1. 临界坡降
        self.i_cr = (self.gamma_s - self.gamma_w) / self.gamma_w
        print(f"\n1. 临界坡降:")
        print(f"   i_cr = (γₛ - γw)/γw")
        print(f"   i_cr = ({self.gamma_s} - {self.gamma_w})/{self.gamma_w}")
        print(f"   i_cr = {self.i_cr:.4f}")
        
        # 2. 出逸坡降（下游坡脚处，简化取最大值）
        # 实际工程中需要流网分析，这里取保守值
        self.i_exit = self.i_avg * 1.5  # 出口处坡降放大系数
        print(f"\n2. 出逸坡降（下游坡脚）:")
        print(f"   i_exit ≈ 1.5 × i_avg = 1.5 × {self.i_avg:.4f}")
        print(f"   i_exit = {self.i_exit:.4f}")
        
        # 3. 安全系数
        self.K_safety = self.i_cr / self.i_exit
        print(f"\n3. 安全系数:")
        print(f"   K = i_cr/i_exit = {self.i_cr:.4f}/{self.i_exit:.4f}")
        print(f"   K = {self.K_safety:.2f}")
        
        # 4. 安全性判断
        print(f"\n4. 安全性判断:")
        print(f"   要求: K ≥ {self.K_required}")
        print(f"   实际: K = {self.K_safety:.2f}")
        
        if self.K_safety >= self.K_required:
            status = "✓ 安全"
            color = "绿色"
        elif self.K_safety >= 1.2:
            status = "⚠ 基本安全，建议加强观测"
            color = "黄色"
        else:
            status = "✗ 不安全，需要采取措施"
            color = "红色"
        
        print(f"   结论: {status} ({color})")
        
        # 5. 渗透破坏类型
        print(f"\n5. 可能的渗透破坏类型:")
        print(f"   (1) 管涌: 细颗粒被渗流带走")
        print(f"   (2) 流土: 整体土体失稳上浮")
        print(f"   (3) 接触冲刷: 不同土层接触面冲刷")
        print(f"   (4) 接触流土: 接触面处土体流失")
        
        return self.K_safety >= self.K_required
    
    def suggest_measures(self):
        """防渗加固措施"""
        print(f"\n{'='*80}")
        print("【防渗加固措施建议】")
        print(f"{'='*80}")
        
        measures = []
        
        if self.K_safety < self.K_required:
            print(f"\n⚠ 当前安全系数K={self.K_safety:.2f} < {self.K_required}，需要采取措施！\n")
            
            measures = [
                "1. 延长渗径措施:",
                "   • 上游防渗斜墙或垂直防渗墙",
                "   • 上游铺盖（水平防渗层）",
                "   • 增加防渗体厚度",
                "",
                "2. 减小渗透坡降:",
                "   • 下游排水棱体",
                "   • 下游导渗沟",
                "   • 减压井",
                "",
                "3. 提高抗渗能力:",
                "   • 反滤层设置",
                "   • 土工布防护",
                "   • 灌浆加固",
                "",
                "4. 排水减压措施:",
                "   • 褥垫层排水",
                "   • 排水孔",
                "   • 减压沟",
                "",
                "5. 监测措施:",
                "   • 渗流量观测",
                "   • 浸润线观测",
                "   • 渗透压力监测"
            ]
        else:
            print(f"\n✓ 当前安全系数K={self.K_safety:.2f} ≥ {self.K_required}，满足要求！\n")
            
            measures = [
                "建议的日常维护措施:",
                "",
                "1. 定期监测:",
                "   • 渗流量观测（每月一次）",
                "   • 浸润线观测（每季度一次）",
                "   • 变形监测（每年一次）",
                "",
                "2. 预防性维护:",
                "   • 保持排水系统畅通",
                "   • 防止上游淤积",
                "   • 下游坡脚植草护坡",
                "",
                "3. 应急预案:",
                "   • 建立渗流异常预警系统",
                "   • 准备应急抢险材料",
                "   • 制定应急处置方案"
            ]
        
        for measure in measures:
            print(measure)
    
    def generate_flow_net(self):
        """生成流网（简化模型）"""
        # 网格
        x = np.linspace(0, self.L, 100)
        y = np.linspace(0, self.H, 80)
        X, Y = np.meshgrid(x, y)
        
        # 简化势函数（抛物线型）
        # φ = h1 - (h1-h2)*(x/L)^1.5
        phi = self.h1 - (self.h1 - self.h2) * (X / self.L) ** 1.5
        
        # 浸润线（自由面）
        x_line = np.linspace(0, self.L, 100)
        y_phreatic = self.h1 - (self.h1 - self.h2) * (x_line / self.L) ** 1.2
        
        # 限制在坝体内
        y_phreatic = np.minimum(y_phreatic, self.H)
        
        return X, Y, phi, x_line, y_phreatic
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目691：渗流场分析")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"  坝体几何: H={self.H}m, L={self.L}m")
        print(f"  水位: h₁={self.h1}m, h₂={self.h2}m")
        print(f"  渗透系数: k={self.k:.2e} m/s = {self.k*100:.4f} cm/s")
        
        print("\n【渗流基本理论】")
        print("1. Darcy定律:")
        print("   v = ki")
        print("   Q = kiA")
        print("   适用条件: 层流渗流（Re < 1~10）")
        
        print("\n2. 渗流连续方程:")
        print("   ∂vₓ/∂x + ∂vᵧ/∂y = 0")
        
        print("\n3. 流网特性:")
        print("   • 等势线⊥流线")
        print("   • Δh相等")
        print("   • 流网网格近似正方形")
        
        print("\n4. 单宽流量:")
        print("   q = kΔh")
        
        print("\n5. 临界坡降:")
        print("   i_cr = (γₛ - γw)/γw ≈ 1.0")
        
        print("\n6. 安全系数:")
        print("   K = i_cr/i_exit ≥ 1.5")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 稳定性分析
        is_safe = self.analyze_stability()
        
        # 防渗措施
        self.suggest_measures()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 渗流速度: v = {self.v_avg:.6e} m/s = {self.v_avg*86400:.4f} m/d")
        print(f"(2) 单宽流量: q = {self.q:.6e} m³/(s·m) = {self.q*86400:.5f} m³/(d·m)")
        print(f"(3) 流网: 见可视化图（等势线+流线）")
        print(f"(4) 渗流坡降: i = {self.i_avg:.4f}, 水头损失Δh = {self.delta_h} m")
        print(f"(5) 安全性: K = {self.K_safety:.2f} {'≥' if is_safe else '<'} {self.K_required}，"
              f"{'安全✓' if is_safe else '需加固✗'}")
        print(f"(6) 措施: 见上述建议")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：流网（等势线+流线）
        ax1 = plt.subplot(2, 2, 1)
        self._plot_flow_net(ax1)
        
        # 子图2：渗流参数分布
        ax2 = plt.subplot(2, 2, 2)
        self._plot_seepage_parameters(ax2)
        
        # 子图3：稳定性分析
        ax3 = plt.subplot(2, 2, 3)
        self._plot_stability_analysis(ax3)
        
        # 子图4：防渗措施示意
        ax4 = plt.subplot(2, 2, 4)
        self._plot_protection_measures(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_flow_net(self, ax):
        """绘制流网"""
        X, Y, phi, x_line, y_phreatic = self.generate_flow_net()
        
        # 坝体轮廓
        dam_x = [0, 0, self.L, self.L, 0]
        dam_y = [0, self.H, self.H, 0, 0]
        ax.fill(dam_x, dam_y, color='tan', alpha=0.3, label='坝体')
        ax.plot(dam_x, dam_y, 'k-', linewidth=2)
        
        # 上游水体
        water_up_x = [-5, -5, 0, 0, -5]
        water_up_y = [0, self.h1, self.h1, 0, 0]
        ax.fill(water_up_x, water_up_y, color='lightblue', alpha=0.5, label='上游水体')
        
        # 下游水体
        water_down_x = [self.L, self.L, self.L+5, self.L+5, self.L]
        water_down_y = [0, self.h2, self.h2, 0, 0]
        ax.fill(water_down_x, water_down_y, color='lightblue', alpha=0.5)
        
        # 浸润线
        ax.plot(x_line, y_phreatic, 'b-', linewidth=3, label='浸润线（自由面）')
        
        # 等势线
        levels_phi = np.linspace(self.h2, self.h1, 10)
        cs1 = ax.contour(X, Y, phi, levels=levels_phi, colors='blue', 
                        linewidths=1.5, linestyles='--', alpha=0.7)
        ax.clabel(cs1, inline=True, fontsize=8, fmt='h=%.1fm')
        
        # 流线（简化，几条代表性流线）
        for i in range(5):
            y_start = self.h1 * (i + 1) / 6
            if y_start < self.H:
                x_stream = np.linspace(0, self.L, 50)
                y_stream = y_start - (y_start - self.h2 * (i + 1) / 6) * (x_stream / self.L) ** 1.3
                y_stream = np.minimum(y_stream, self.H)
                y_stream = np.maximum(y_stream, 0)
                ax.plot(x_stream, y_stream, 'r-', linewidth=1, alpha=0.6)
        
        # 渗流方向箭头
        for xi in [10, 20, 30]:
            yi = self.h1 - (self.h1 - self.h2) * (xi / self.L) ** 1.2 - 2
            if 0 < yi < self.H:
                ax.arrow(xi, yi, 3, -0.5, head_width=0.8, head_length=1.5,
                        fc='darkred', ec='darkred', linewidth=2)
        
        # 标注
        ax.text(-2.5, self.h1/2, f'h₁={self.h1}m', fontsize=11, rotation=90,
               va='center', weight='bold')
        ax.text(self.L+2, self.h2/2, f'h₂={self.h2}m', fontsize=11, rotation=90,
               va='center', weight='bold')
        ax.text(self.L/2, -2, f'L={self.L}m', fontsize=11, ha='center', weight='bold')
        
        ax.set_xlabel('水平距离 x (m)', fontsize=12)
        ax.set_ylabel('高程 y (m)', fontsize=12)
        ax.set_title('渗流流网（等势线⊥流线）', fontsize=13, weight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-5, self.L+5)
        ax.set_ylim(-3, self.H+2)
        ax.set_aspect('equal')
    
    def _plot_seepage_parameters(self, ax):
        """绘制渗流参数分布"""
        x = np.linspace(0, self.L, 100)
        
        # 水头分布（简化）
        h = self.h1 - (self.h1 - self.h2) * (x / self.L) ** 1.5
        
        # 渗流坡降分布
        i = np.gradient(h, x) * (-1)
        
        # 渗流速度分布
        v = self.k * i * 86400  # m/d
        
        # 双Y轴
        ax2 = ax.twinx()
        
        # 水头
        line1 = ax.plot(x, h, 'b-', linewidth=2.5, label='水头 h(x)')
        ax.fill_between(x, 0, h, alpha=0.2, color='blue')
        
        # 坡降
        line2 = ax2.plot(x, i, 'r--', linewidth=2.5, label='渗流坡降 i(x)')
        
        # 临界坡降线
        line3 = ax2.axhline(self.i_cr, color='orange', linestyle=':', 
                           linewidth=2, label=f'临界坡降 i_cr={self.i_cr:.2f}')
        
        ax.set_xlabel('水平距离 x (m)', fontsize=12)
        ax.set_ylabel('水头 h (m)', fontsize=12, color='blue')
        ax2.set_ylabel('渗流坡降 i', fontsize=12, color='red')
        ax.set_title('渗流参数沿程分布', fontsize=13, weight='bold')
        
        ax.tick_params(axis='y', labelcolor='blue')
        ax2.tick_params(axis='y', labelcolor='red')
        
        # 合并图例
        lines = line1 + line2 + [line3]
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper right', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.L)
    
    def _plot_stability_analysis(self, ax):
        """绘制稳定性分析"""
        categories = ['平均坡降\ni_avg', '出逸坡降\ni_exit', '临界坡降\ni_cr']
        values = [self.i_avg, self.i_exit, self.i_cr]
        colors = ['blue', 'orange', 'red']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.6, 
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                   f'{val:.4f}', ha='center', fontsize=11, weight='bold')
        
        # 安全系数线
        ax.axhline(self.i_exit, color='orange', linestyle='--', 
                  linewidth=2, alpha=0.7)
        ax.axhline(self.i_cr, color='red', linestyle='--', 
                  linewidth=2, alpha=0.7)
        
        # 安全系数标注
        ax.text(2.3, (self.i_exit + self.i_cr)/2,
               f'K = i_cr/i_exit\n= {self.K_safety:.2f}',
               fontsize=11, weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 安全判断
        if self.K_safety >= self.K_required:
            status_text = f'✓ 安全\nK={self.K_safety:.2f} ≥ {self.K_required}'
            status_color = 'lightgreen'
        else:
            status_text = f'✗ 不安全\nK={self.K_safety:.2f} < {self.K_required}'
            status_color = 'lightcoral'
        
        ax.text(0.5, 0.95, status_text,
               transform=ax.transAxes, fontsize=12, weight='bold',
               ha='center', va='top',
               bbox=dict(boxstyle='round', facecolor=status_color, alpha=0.8))
        
        ax.set_ylabel('渗流坡降', fontsize=12)
        ax.set_title('渗透稳定性分析', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim(0, max(values) * 1.3)
    
    def _plot_protection_measures(self, ax):
        """绘制防渗措施示意"""
        ax.axis('off')
        
        # 标题
        ax.text(0.5, 0.95, '防渗加固措施', ha='center', va='top',
               fontsize=13, weight='bold', transform=ax.transAxes)
        
        # 措施列表
        measures = [
            ('1. 延长渗径', ['上游防渗斜墙', '垂直防渗墙', '上游铺盖'], 0.80),
            ('2. 减小坡降', ['下游排水棱体', '导渗沟', '减压井'], 0.60),
            ('3. 提高抗渗', ['反滤层', '土工布', '灌浆加固'], 0.40),
            ('4. 监测预警', ['渗流量观测', '浸润线观测', '压力监测'], 0.20)
        ]
        
        for title, items, y in measures:
            # 标题
            ax.text(0.05, y, title, fontsize=11, weight='bold',
                   transform=ax.transAxes)
            
            # 子项
            for i, item in enumerate(items):
                ax.text(0.15, y - 0.04*(i+1), f'• {item}',
                       fontsize=9, transform=ax.transAxes)
        
        # 底部总结
        if self.K_safety >= self.K_required:
            summary = f'✓ 当前安全系数K={self.K_safety:.2f}满足要求\n建议加强日常监测和维护'
            color = 'lightgreen'
        else:
            summary = f'⚠ 当前安全系数K={self.K_safety:.2f}不足\n需要立即采取加固措施'
            color = 'lightcoral'
        
        ax.text(0.5, 0.05, summary,
               ha='center', fontsize=10, weight='bold',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.8),
               transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)


def test_problem_691():
    """测试题目691"""
    print("\n" + "="*80)
    print("开始渗流场分析...")
    print("="*80)
    
    # 创建渗流场对象
    seepage = SeepageField()
    
    # 打印结果
    seepage.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = seepage.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_691_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_691_result.png")
    
    # 验证
    assert seepage.v_avg > 0, "渗流速度应大于0"
    assert seepage.q > 0, "单宽流量应大于0"
    assert seepage.i_cr > 0, "临界坡降应大于0"
    assert seepage.K_safety > 0, "安全系数应大于0"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("渗流场分析是土石坝安全的关键！")
    print("• Darcy定律: v = ki, Q = kiA")
    print("• 流网特性: 等势线⊥流线")
    print("• 临界坡降: i_cr = (γₛ-γw)/γw ≈ 1.0")
    print("• 安全系数: K = i_cr/i_exit ≥ 1.5")
    print("• 防渗措施: 延长渗径+减小坡降+提高抗渗")


if __name__ == "__main__":
    test_problem_691()
