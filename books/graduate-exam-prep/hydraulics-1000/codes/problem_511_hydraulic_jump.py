"""
《水力学考研1000题详解》配套代码
题目511：水跃计算

问题描述：
矩形明渠，宽度b=3m，跃前水深h1=0.5m，跃前流速v1=6m/s。
求：(1) 跃前弗劳德数Fr1
    (2) 跃后水深h2
    (3) 跃后流速v2
    (4) 水跃长度Lj
    (5) 水跃水头损失Δh
    (6) 能量损失率η

考点：
1. 跃前弗劳德数：Fr1 = v1/√(gh1) > 1（急流）
2. 共轭水深：h2 = (h1/2)·(√(1+8Fr1²) - 1)
3. 跃后流速：v2 = v1h1/h2（连续性）
4. 水跃长度：Lj = (6~7)h2
5. 水跃损失：Δh = (h2-h1)³/(4h1h2)

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch, Circle
from scipy.optimize import fsolve

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class HydraulicJump:
    """水跃计算类"""
    
    def __init__(self, b, h1, v1, g=9.8):
        """
        初始化
        
        参数:
            b: 渠道底宽 (m)
            h1: 跃前水深 (m)
            v1: 跃前流速 (m/s)
            g: 重力加速度 (m/s²)
        """
        self.b = b
        self.h1 = h1
        self.v1 = v1
        self.g = g
        
        # 执行计算
        self.calculate()
    
    def calculate(self):
        """执行水力计算"""
        # 1. 跃前弗劳德数
        self.Fr1 = self.v1 / np.sqrt(self.g * self.h1)
        
        # 判断流态
        if self.Fr1 <= 1.0:
            raise ValueError(f"跃前必须是急流！Fr1={self.Fr1:.3f} <= 1")
        
        # 2. 跃前断面参数
        self.A1 = self.b * self.h1
        self.Q = self.A1 * self.v1
        self.q = self.Q / self.b  # 单宽流量
        
        # 3. 跃后水深（共轭水深公式）
        # h2 = (h1/2) * (√(1 + 8Fr1²) - 1)
        self.h2 = (self.h1 / 2) * (np.sqrt(1 + 8 * self.Fr1**2) - 1)
        
        # 4. 跃后流速（连续性方程）
        self.A2 = self.b * self.h2
        self.v2 = self.Q / self.A2
        
        # 验证：v2 = v1·h1/h2
        self.v2_check = self.v1 * self.h1 / self.h2
        
        # 5. 跃后弗劳德数（应该<1，缓流）
        self.Fr2 = self.v2 / np.sqrt(self.g * self.h2)
        
        # 6. 水跃长度（经验公式）
        # Lj = (6~7)h2，取中值6.5
        self.Lj = 6.5 * self.h2
        
        # 7. 跃前后比能
        self.E1 = self.h1 + self.v1**2 / (2 * self.g)
        self.E2 = self.h2 + self.v2**2 / (2 * self.g)
        
        # 8. 水跃水头损失
        # 公式1：Δh = (h2-h1)³/(4h1h2)
        self.delta_h = (self.h2 - self.h1)**3 / (4 * self.h1 * self.h2)
        
        # 验证：Δh = E1 - E2
        self.delta_h_check = self.E1 - self.E2
        
        # 9. 能量损失率
        self.eta = (self.delta_h / self.E1) * 100  # 百分比
        
        # 10. 动量方程验证
        # M1 = M2: Q²/A1 + gA1ȳ1 = Q²/A2 + gA2ȳ2
        # 对于矩形：ȳ = h/2
        y_bar1 = self.h1 / 2
        y_bar2 = self.h2 / 2
        self.M1 = self.Q**2 / self.A1 + self.g * self.A1 * y_bar1
        self.M2 = self.Q**2 / self.A2 + self.g * self.A2 * y_bar2
        
        # 11. 水跃类型判别
        self.jump_type = self._classify_jump()
    
    def _classify_jump(self):
        """根据Fr1判别水跃类型"""
        if 1.0 < self.Fr1 <= 1.7:
            return "波状水跃"
        elif 1.7 < self.Fr1 <= 2.5:
            return "弱水跃"
        elif 2.5 < self.Fr1 <= 4.5:
            return "稳定水跃"
        elif 4.5 < self.Fr1 <= 9.0:
            return "强水跃"
        else:
            return "激烈水跃"
    
    def print_results(self):
        """打印计算结果"""
        print("=" * 80)
        print("题目511：水跃计算")
        print("=" * 80)
        
        print("\n【已知条件】")
        print(f"渠道底宽: b = {self.b:.2f} m")
        print(f"跃前水深: h1 = {self.h1:.2f} m")
        print(f"跃前流速: v1 = {self.v1:.2f} m/s")
        
        print("\n【计算过程】")
        
        print("\n步骤1：判断跃前流态（计算Fr1）")
        print(f"Fr1 = v1/√(gh1)")
        print(f"    = {self.v1:.2f}/√({self.g}×{self.h1:.2f})")
        print(f"    = {self.v1:.2f}/√{self.g*self.h1:.3f}")
        print(f"    = {self.v1:.2f}/{np.sqrt(self.g*self.h1):.3f}")
        print(f"    = {self.Fr1:.4f}")
        print(f"Fr1 = {self.Fr1:.4f} > 1  →  急流（可发生水跃） ✓")
        
        print("\n步骤2：计算跃前断面参数")
        print(f"A1 = bh1 = {self.b} × {self.h1} = {self.A1:.3f} m²")
        print(f"Q = A1v1 = {self.A1:.3f} × {self.v1} = {self.Q:.3f} m³/s")
        print(f"q = Q/b = {self.Q:.3f}/{self.b} = {self.q:.3f} m²/s")
        
        print("\n步骤3：计算跃后水深（共轭水深公式）")
        print(f"h2 = (h1/2) · (√(1 + 8Fr1²) - 1)")
        print(f"   = ({self.h1}/2) · (√(1 + 8×{self.Fr1:.4f}²) - 1)")
        print(f"   = {self.h1/2:.3f} · (√(1 + {8*self.Fr1**2:.3f}) - 1)")
        print(f"   = {self.h1/2:.3f} · (√{1 + 8*self.Fr1**2:.3f} - 1)")
        print(f"   = {self.h1/2:.3f} · ({np.sqrt(1 + 8*self.Fr1**2):.3f} - 1)")
        print(f"   = {self.h1/2:.3f} × {np.sqrt(1 + 8*self.Fr1**2) - 1:.3f}")
        print(f"   = {self.h2:.4f} m")
        
        print("\n步骤4：计算跃后流速")
        print(f"方法1（连续性）：")
        print(f"  A2 = bh2 = {self.b} × {self.h2:.4f} = {self.A2:.4f} m²")
        print(f"  v2 = Q/A2 = {self.Q:.3f}/{self.A2:.4f} = {self.v2:.4f} m/s")
        print(f"方法2（验证公式）：")
        print(f"  v2 = v1·h1/h2 = {self.v1} × {self.h1}/{self.h2:.4f} = {self.v2_check:.4f} m/s")
        print(f"验证: 两种方法结果一致 ✓")
        
        print("\n步骤5：验证跃后流态（计算Fr2）")
        print(f"Fr2 = v2/√(gh2)")
        print(f"    = {self.v2:.4f}/√({self.g}×{self.h2:.4f})")
        print(f"    = {self.v2:.4f}/{np.sqrt(self.g*self.h2):.4f}")
        print(f"    = {self.Fr2:.4f}")
        print(f"Fr2 = {self.Fr2:.4f} < 1  →  缓流（跃后状态正确） ✓")
        
        print("\n步骤6：计算水跃长度（经验公式）")
        print(f"Lj = 6.5·h2  （经验系数6~7，取6.5）")
        print(f"   = 6.5 × {self.h2:.4f}")
        print(f"   = {self.Lj:.4f} m")
        
        print("\n步骤7：计算断面比能")
        print(f"跃前：E1 = h1 + v1²/2g")
        print(f"       = {self.h1} + {self.v1}²/(2×{self.g})")
        print(f"       = {self.h1} + {self.v1**2/(2*self.g):.4f}")
        print(f"       = {self.E1:.4f} m")
        print(f"跃后：E2 = h2 + v2²/2g")
        print(f"       = {self.h2:.4f} + {self.v2:.4f}²/(2×{self.g})")
        print(f"       = {self.h2:.4f} + {self.v2**2/(2*self.g):.4f}")
        print(f"       = {self.E2:.4f} m")
        
        print("\n步骤8：计算水跃水头损失")
        print(f"方法1（水跃公式）：")
        print(f"  Δh = (h2-h1)³/(4h1h2)")
        print(f"     = ({self.h2:.4f}-{self.h1})³/(4×{self.h1}×{self.h2:.4f})")
        print(f"     = {(self.h2-self.h1):.4f}³/({4*self.h1*self.h2:.4f})")
        print(f"     = {(self.h2-self.h1)**3:.6f}/{4*self.h1*self.h2:.4f}")
        print(f"     = {self.delta_h:.4f} m")
        print(f"方法2（能量守恒）：")
        print(f"  Δh = E1 - E2 = {self.E1:.4f} - {self.E2:.4f} = {self.delta_h_check:.4f} m")
        print(f"验证: 两种方法结果一致 ✓")
        
        print("\n步骤9：计算能量损失率")
        print(f"η = (Δh/E1) × 100%")
        print(f"  = ({self.delta_h:.4f}/{self.E1:.4f}) × 100%")
        print(f"  = {self.eta:.2f}%")
        
        print("\n步骤10：动量方程验证")
        print(f"动量守恒：M1 = M2")
        print(f"M1 = Q²/A1 + gA1ȳ1")
        print(f"   = {self.Q:.3f}²/{self.A1:.3f} + {self.g}×{self.A1:.3f}×{self.h1/2:.3f}")
        print(f"   = {self.Q**2/self.A1:.3f} + {self.g*self.A1*self.h1/2:.3f}")
        print(f"   = {self.M1:.3f} N/m")
        print(f"M2 = Q²/A2 + gA2ȳ2")
        print(f"   = {self.Q:.3f}²/{self.A2:.4f} + {self.g}×{self.A2:.4f}×{self.h2/2:.4f}")
        print(f"   = {self.Q**2/self.A2:.3f} + {self.g*self.A2*self.h2/2:.3f}")
        print(f"   = {self.M2:.3f} N/m")
        print(f"误差: {abs(self.M1-self.M2)/self.M1*100:.2f}% < 1%  →  动量守恒验证通过 ✓")
        
        print("\n【最终答案】")
        print(f"(1) 跃前弗劳德数: Fr1 = {self.Fr1:.4f}  （急流）")
        print(f"(2) 跃后水深: h2 = {self.h2:.4f} m  （是h1的{self.h2/self.h1:.2f}倍）")
        print(f"(3) 跃后流速: v2 = {self.v2:.4f} m/s  （是v1的{self.v2/self.v1:.2f}倍）")
        print(f"(4) 水跃长度: Lj = {self.Lj:.4f} m  （约{self.Lj/self.h2:.1f}倍h2）")
        print(f"(5) 水跃损失: Δh = {self.delta_h:.4f} m  （损失{self.eta:.1f}%能量）")
        print(f"(6) 能量损失率: η = {self.eta:.2f}%")
        
        print("\n【水跃类型判别】")
        print(f"根据Fr1 = {self.Fr1:.2f}:")
        print(f"  1.0 < Fr1 ≤ 1.7: 波状水跃")
        print(f"  1.7 < Fr1 ≤ 2.5: 弱水跃")
        print(f"  2.5 < Fr1 ≤ 4.5: 稳定水跃")
        print(f"  4.5 < Fr1 ≤ 9.0: 强水跃")
        print(f"  Fr1 > 9.0: 激烈水跃")
        print(f"→ 本题为: {self.jump_type}")
        
        print("=" * 80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：水跃剖面
        ax1 = plt.subplot(2, 2, 1)
        self._plot_jump_profile(ax1)
        
        # 子图2：弗劳德数变化
        ax2 = plt.subplot(2, 2, 2)
        self._plot_froude_number(ax2)
        
        # 子图3：能量损失分析
        ax3 = plt.subplot(2, 2, 3)
        self._plot_energy_loss(ax3)
        
        # 子图4：水深流速对比
        ax4 = plt.subplot(2, 2, 4)
        self._plot_comparison(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_jump_profile(self, ax):
        """绘制水跃剖面"""
        # 渠道底部
        ax.plot([0, self.Lj*1.5], [0, 0], 'k-', linewidth=3)
        
        # 跃前水面
        x_before = np.linspace(0, self.Lj*0.2, 20)
        y_before = np.ones_like(x_before) * self.h1
        ax.plot(x_before, y_before, 'b-', linewidth=2)
        
        # 水跃段（抛物线过渡）
        x_jump = np.linspace(self.Lj*0.2, self.Lj*0.2 + self.Lj, 50)
        # 使用三次多项式平滑过渡
        t = (x_jump - self.Lj*0.2) / self.Lj
        y_jump = self.h1 + (self.h2 - self.h1) * (3*t**2 - 2*t**3)
        # 添加波动效果
        wave = 0.05 * self.h2 * np.sin(10*t) * np.exp(-3*t)
        y_jump += wave
        ax.plot(x_jump, y_jump, 'b-', linewidth=2.5, label='水面线')
        
        # 跃后水面
        x_after = np.linspace(self.Lj*0.2 + self.Lj, self.Lj*1.5, 20)
        y_after = np.ones_like(x_after) * self.h2
        ax.plot(x_after, y_after, 'b-', linewidth=2)
        
        # 填充水体
        x_water = np.concatenate([x_before, x_jump, x_after])
        y_water = np.concatenate([y_before, y_jump, y_after])
        ax.fill_between(x_water, 0, y_water, alpha=0.3, color='cyan')
        
        # 标注跃前水深
        ax.plot([self.Lj*0.1, self.Lj*0.1], [0, self.h1], 'r--', linewidth=1.5)
        ax.annotate('', xy=(self.Lj*0.08, self.h1), xytext=(self.Lj*0.08, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(self.Lj*0.05, self.h1/2, f'h₁={self.h1}m', 
               fontsize=10, color='red', rotation=90, va='center')
        
        # 标注跃后水深
        x_pos = self.Lj*0.2 + self.Lj + self.Lj*0.1
        ax.plot([x_pos, x_pos], [0, self.h2], 'r--', linewidth=1.5)
        ax.annotate('', xy=(x_pos+self.Lj*0.02, self.h2), xytext=(x_pos+self.Lj*0.02, 0),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
        ax.text(x_pos+self.Lj*0.05, self.h2/2, f'h₂={self.h2:.2f}m', 
               fontsize=10, color='red', rotation=90, va='center')
        
        # 标注水跃长度
        y_label = -self.h2*0.15
        ax.annotate('', xy=(self.Lj*0.2 + self.Lj, y_label), xytext=(self.Lj*0.2, y_label),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='green'))
        ax.text(self.Lj*0.2 + self.Lj/2, y_label-self.h2*0.1, 
               f'Lⱼ={self.Lj:.2f}m', fontsize=11, ha='center', color='green')
        
        # 流速箭头（跃前）
        for i in range(3):
            x = self.Lj*0.05 + i*self.Lj*0.05
            y = self.h1 * (0.3 + i*0.2)
            arrow_len = 0.3
            ax.arrow(x, y, arrow_len, 0, head_width=0.08, head_length=0.1,
                    fc='darkblue', ec='darkblue', linewidth=1.5)
        ax.text(self.Lj*0.1, self.h1 + 0.15, f'v₁={self.v1}m/s  →', 
               fontsize=10, color='darkblue', weight='bold')
        
        # 流速箭头（跃后）
        for i in range(3):
            x = x_pos + self.Lj*0.15 + i*self.Lj*0.05
            y = self.h2 * (0.3 + i*0.2)
            arrow_len = 0.15
            ax.arrow(x, y, arrow_len, 0, head_width=0.08, head_length=0.08,
                    fc='darkgreen', ec='darkgreen', linewidth=1.5)
        ax.text(x_pos + self.Lj*0.2, self.h2 + 0.15, f'v₂={self.v2:.2f}m/s  →', 
               fontsize=10, color='darkgreen', weight='bold')
        
        # 标注水跃类型
        ax.text(self.Lj*0.2 + self.Lj/2, self.h2*0.8, 
               f'{self.jump_type}\nFr₁={self.Fr1:.2f}',
               fontsize=11, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlim(-self.Lj*0.05, self.Lj*1.5)
        ax.set_ylim(-self.h2*0.3, self.h2*1.4)
        ax.set_aspect('equal')
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel('高度 (m)', fontsize=12)
        ax.set_title('水跃剖面图', fontsize=14, weight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    def _plot_froude_number(self, ax):
        """绘制弗劳德数变化"""
        positions = ['跃前', '跃后']
        Fr_values = [self.Fr1, self.Fr2]
        colors = ['red', 'blue']
        
        bars = ax.bar(positions, Fr_values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2, width=0.5)
        
        # 标注数值
        for bar, Fr, color in zip(bars, Fr_values, colors):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'Fr={Fr:.3f}',
                   ha='center', va='bottom', fontsize=12, weight='bold', color=color)
        
        # Fr=1临界线
        ax.axhline(1.0, color='green', linestyle='--', linewidth=2.5, label='Fr=1 (临界)')
        
        # 流态标注
        ax.text(0, self.Fr1*0.5, '急流\n(Fr>1)', fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        ax.text(1, self.Fr2*0.5, '缓流\n(Fr<1)', fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        # 变化箭头
        ax.annotate('', xy=(1, self.Fr2), xytext=(0, self.Fr1),
                   arrowprops=dict(arrowstyle='->', lw=3, color='purple'))
        ax.text(0.5, (self.Fr1+self.Fr2)/2, '急流→缓流', 
               fontsize=10, ha='center', rotation=-60, color='purple')
        
        ax.set_ylabel('弗劳德数 Fr', fontsize=12)
        ax.set_title('水跃前后弗劳德数变化', fontsize=14, weight='bold')
        ax.set_ylim(0, max(Fr_values)*1.3)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_energy_loss(self, ax):
        """绘制能量损失分析"""
        labels = ['E₁\n(跃前)', 'Δh\n(损失)', 'E₂\n(跃后)']
        values = [self.E1, self.delta_h, self.E2]
        colors = ['green', 'red', 'blue']
        
        bars = ax.bar(labels, values, color=colors, alpha=0.7,
                     edgecolor='black', linewidth=2)
        
        # 标注数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.3f}m',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        # 能量守恒关系
        ax.plot([0, 2], [self.E1, self.E2], 'k--', linewidth=2, alpha=0.5)
        
        # 损失率标注
        ax.text(1, self.delta_h/2, f'损失率\nη={self.eta:.1f}%',
               fontsize=10, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        # 守恒关系标注
        ax.text(1, self.E1*1.05, 'E₁ = Δh + E₂', 
               fontsize=11, ha='center', style='italic',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))
        
        ax.set_ylabel('比能 E (m)', fontsize=12)
        ax.set_title('水跃能量损失分析', fontsize=14, weight='bold')
        ax.set_ylim(0, max(values)*1.2)
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_comparison(self, ax):
        """绘制水深流速对比"""
        x = np.arange(2)
        width = 0.35
        
        # 水深对比
        bars1 = ax.bar(x - width/2, [self.h1, self.h2], width, 
                      label='水深 (m)', color='skyblue', 
                      edgecolor='black', linewidth=1.5)
        
        # 流速对比（缩放到同一数量级）
        scale = 1.0  # 流速和水深数量级相近，不需缩放
        bars2 = ax.bar(x + width/2, [self.v1*scale, self.v2*scale], width,
                      label=f'流速 (m/s)', color='lightcoral',
                      edgecolor='black', linewidth=1.5)
        
        # 标注数值
        for bar, val in zip(bars1, [self.h1, self.h2]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.3f}',
                   ha='center', va='bottom', fontsize=10, weight='bold')
        
        for bar, val in zip(bars2, [self.v1, self.v2]):
            height = bar.get_height() * scale
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{val:.3f}',
                   ha='center', va='bottom', fontsize=10, weight='bold')
        
        # 变化比例标注
        h_ratio = self.h2 / self.h1
        v_ratio = self.v2 / self.v1
        
        # 水深增加
        ax.annotate('', xy=(0-width/2, self.h2), xytext=(0-width/2, self.h1),
                   arrowprops=dict(arrowstyle='<-', lw=2, color='blue'))
        ax.text(-0.5, (self.h1+self.h2)/2, f'×{h_ratio:.2f}',
               fontsize=9, ha='right', color='blue')
        
        # 流速减小
        ax.annotate('', xy=(1+width/2, self.v2*scale), xytext=(1+width/2, self.v1*scale),
                   arrowprops=dict(arrowstyle='<-', lw=2, color='red'))
        ax.text(1.5, (self.v1*scale+self.v2*scale)/2, f'×{v_ratio:.2f}',
               fontsize=9, ha='left', color='red')
        
        # 连续性方程验证
        Q1 = self.h1 * self.v1
        Q2 = self.h2 * self.v2
        ax.text(0.5, max(self.h1, self.h2, self.v1*scale, self.v2*scale)*1.05,
               f'连续性验证:\nh₁v₁={Q1:.3f}\nh₂v₂={Q2:.3f}',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        
        ax.set_ylabel('数值', fontsize=12)
        ax.set_title('水深与流速对比', fontsize=14, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['跃前', '跃后'])
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)


def test_problem_511():
    """测试题目511"""
    # 已知条件
    b = 3.0         # 渠道底宽 (m)
    h1 = 0.5        # 跃前水深 (m)
    v1 = 6.0        # 跃前流速 (m/s)
    
    # 创建计算对象
    jump = HydraulicJump(b, h1, v1)
    
    # 打印结果
    jump.print_results()
    
    # 可视化
    fig = jump.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_511_result.png',
                dpi=150, bbox_inches='tight')
    print("\n图片已保存: problem_511_result.png")
    
    # 验证答案（合理性检查）
    assert jump.Fr1 > 1.0, "跃前必须是急流"
    assert jump.Fr2 < 1.0, "跃后必须是缓流"
    assert jump.h2 > jump.h1, "跃后水深必须大于跃前"
    assert jump.v2 < jump.v1, "跃后流速必须小于跃前"
    assert jump.delta_h > 0, "水跃损失必须大于0"
    assert abs(jump.M1 - jump.M2) / jump.M1 < 0.01, "动量守恒误差过大"
    assert abs(jump.delta_h - jump.delta_h_check) / jump.delta_h < 0.01, "能量损失计算误差过大"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("水跃是明渠流重要的局部水力现象！")
    print("• 水跃条件：Fr1 > 1（跃前急流）")
    print("• 共轭水深：h2 = (h1/2)·(√(1+8Fr1²) - 1)")
    print("• 能量损失：Δh = (h2-h1)³/(4h1h2)")
    print("• 流态转换：急流 → 缓流")
    print("• 实际应用：消能、混合、充氧")


if __name__ == "__main__":
    test_problem_511()
