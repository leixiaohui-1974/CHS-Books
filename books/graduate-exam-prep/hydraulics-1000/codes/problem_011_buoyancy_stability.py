"""
《水力学考研1000题详解》配套代码
题目011：浮力与浮体稳定性

问题描述：
一矩形浮箱，长L=4m，宽B=2m，高H=1.5m，重量W=80kN。
水的重度γ=10kN/m³。
要求：
(1) 计算浮箱漂浮时的吃水深度h
(2) 计算浮心C的位置
(3) 计算定倾中心M的位置（假设重心G在几何中心）
(4) 判断浮箱的稳定性
(5) 分析不同吃水深度下的稳定性变化

考点：
1. 阿基米德原理：F_b = γV_排 = W
2. 浮心：排水体积的几何中心
3. 重心：物体质量中心
4. 定倾中心：M = C + Ic/(V_排)
5. 稳定性判据：GM > 0（稳定），GM = 0（临界），GM < 0（不稳定）
6. 稳心半径：r = Ic/V_排

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Arc, Polygon
from matplotlib.patches import FancyBboxPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BuoyancyStability:
    """浮力与浮体稳定性分析类"""
    
    def __init__(self, L, B, H, W, gamma=10):
        """
        初始化
        
        参数:
            L: 浮箱长度 (m)
            B: 浮箱宽度 (m)
            H: 浮箱高度 (m)
            W: 浮箱重量 (kN)
            gamma: 水的重度 (kN/m³)
        """
        self.L = L          # 长度 (m)
        self.B = B          # 宽度 (m)
        self.H = H          # 高度 (m)
        self.W = W          # 重量 (kN)
        self.gamma = gamma  # 重度 (kN/m³)
        
        # 计算浮力平衡
        self.calculate_equilibrium()
        
        # 计算稳定性
        self.calculate_stability()
    
    def calculate_equilibrium(self):
        """计算浮力平衡（吃水深度）"""
        # 阿基米德原理：F_b = γ·V_排 = W
        # γ·L·B·h = W
        # h = W / (γ·L·B)
        
        self.h = self.W / (self.gamma * self.L * self.B)
        
        # 排水体积
        self.V_displaced = self.L * self.B * self.h
        
        # 浮力
        self.F_b = self.gamma * self.V_displaced
        
        # 吃水比
        self.draft_ratio = self.h / self.H
    
    def calculate_stability(self):
        """计算稳定性参数"""
        # 1. 浮心C（排水体积的几何中心）
        # 从底面算起
        self.z_C = self.h / 2
        
        # 2. 重心G（假设在几何中心）
        self.z_G = self.H / 2
        
        # 3. 定倾中心M
        # 水线面对纵倾轴的惯性矩
        # Ic = L·B³/12（对横倾）或 Ic = B·L³/12（对纵倾）
        
        # 横倾（绕纵轴，长度方向）
        self.Ic_transverse = self.L * self.B**3 / 12
        
        # 纵倾（绕横轴，宽度方向）
        self.Ic_longitudinal = self.B * self.L**3 / 12
        
        # 稳心半径
        self.r_transverse = self.Ic_transverse / self.V_displaced
        self.r_longitudinal = self.Ic_longitudinal / self.V_displaced
        
        # 定倾中心M的位置（从底面算起）
        self.z_M_transverse = self.z_C + self.r_transverse
        self.z_M_longitudinal = self.z_C + self.r_longitudinal
        
        # 4. 稳心高（GM）
        self.GM_transverse = self.z_M_transverse - self.z_G
        self.GM_longitudinal = self.z_M_longitudinal - self.z_G
        
        # 5. 稳定性判别
        if self.GM_transverse > 0:
            self.stability_transverse = "稳定"
        elif self.GM_transverse == 0:
            self.stability_transverse = "临界"
        else:
            self.stability_transverse = "不稳定"
        
        if self.GM_longitudinal > 0:
            self.stability_longitudinal = "稳定"
        elif self.GM_longitudinal == 0:
            self.stability_longitudinal = "临界"
        else:
            self.stability_longitudinal = "不稳定"
    
    def analyze_stability_variation(self, h_array):
        """分析不同吃水深度下的稳定性变化"""
        GM_transverse_array = []
        GM_longitudinal_array = []
        
        for h in h_array:
            # 排水体积
            V = self.L * self.B * h
            
            # 浮心
            z_C = h / 2
            
            # 稳心半径
            r_trans = (self.L * self.B**3 / 12) / V
            r_long = (self.B * self.L**3 / 12) / V
            
            # 定倾中心
            z_M_trans = z_C + r_trans
            z_M_long = z_C + r_long
            
            # 稳心高
            GM_trans = z_M_trans - self.z_G
            GM_long = z_M_long - self.z_G
            
            GM_transverse_array.append(GM_trans)
            GM_longitudinal_array.append(GM_long)
        
        return np.array(GM_transverse_array), np.array(GM_longitudinal_array)
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目011：浮力与浮体稳定性")
        print("="*80)
        
        print("\n【已知条件】")
        print(f"浮箱尺寸: L={self.L}m, B={self.B}m, H={self.H}m")
        print(f"浮箱重量: W={self.W}kN")
        print(f"水的重度: γ={self.gamma}kN/m³")
        
        print("\n【浮力与稳定性基本概念】")
        print("1. 阿基米德原理:")
        print("   • 浮力 = 排水体积的重量")
        print("   • F_b = γ·V_排")
        print("   • 平衡条件: F_b = W")
        
        print("\n2. 浮心C (Center of Buoyancy):")
        print("   • 排水体积的几何中心")
        print("   • 浮力的作用点")
        print("   • z_C = h/2（从底面算起）")
        
        print("\n3. 重心G (Center of Gravity):")
        print("   • 物体重量的作用点")
        print("   • 由质量分布决定")
        print("   • 本例假设在几何中心")
        
        print("\n4. 定倾中心M (Metacenter):")
        print("   • 浮体微倾时浮力作用线与对称面交点")
        print("   • z_M = z_C + r（r为稳心半径）")
        print("   • r = Ic/V_排（Ic为水线面惯性矩）")
        
        print("\n5. 稳定性判据:")
        print("   • GM > 0: 稳定（扶正力矩）")
        print("   • GM = 0: 临界（中性平衡）")
        print("   • GM < 0: 不稳定（倾覆力矩）")
        
        print("\n【计算过程】")
        
        # (1) 吃水深度
        print("\n(1) 吃水深度计算")
        print("    平衡条件: F_b = W")
        print(f"    γ·L·B·h = W")
        print(f"    {self.gamma} × {self.L} × {self.B} × h = {self.W}")
        print(f"    h = {self.W} / ({self.gamma} × {self.L} × {self.B})")
        print(f"    h = {self.h:.3f} m")
        print(f"\n    吃水比: h/H = {self.h}/{self.H} = {self.draft_ratio:.1%}")
        print(f"    排水体积: V = {self.V_displaced:.3f} m³")
        print(f"    浮力验证: F_b = {self.F_b:.1f} kN = W ✓")
        
        # (2) 浮心位置
        print("\n(2) 浮心C的位置")
        print("    浮心是排水体积的几何中心")
        print(f"    z_C = h/2 = {self.h}/2 = {self.z_C:.3f} m（从底面算起）")
        
        # (3) 定倾中心位置
        print("\n(3) 定倾中心M的位置")
        
        print("\n    ■ 横倾（绕纵轴，L方向）:")
        print(f"    水线面惯性矩: Ic = L·B³/12")
        print(f"                  = {self.L} × {self.B}³/12")
        print(f"                  = {self.Ic_transverse:.4f} m⁴")
        
        print(f"\n    稳心半径: r = Ic/V_排")
        print(f"             = {self.Ic_transverse:.4f} / {self.V_displaced:.3f}")
        print(f"             = {self.r_transverse:.4f} m")
        
        print(f"\n    定倾中心: z_M = z_C + r")
        print(f"             = {self.z_C:.3f} + {self.r_transverse:.4f}")
        print(f"             = {self.z_M_transverse:.4f} m")
        
        print("\n    ■ 纵倾（绕横轴，B方向）:")
        print(f"    水线面惯性矩: Ic = B·L³/12")
        print(f"                  = {self.B} × {self.L}³/12")
        print(f"                  = {self.Ic_longitudinal:.4f} m⁴")
        
        print(f"\n    稳心半径: r = Ic/V_排")
        print(f"             = {self.Ic_longitudinal:.4f} / {self.V_displaced:.3f}")
        print(f"             = {self.r_longitudinal:.4f} m")
        
        print(f"\n    定倾中心: z_M = z_C + r")
        print(f"             = {self.z_C:.3f} + {self.r_longitudinal:.4f}")
        print(f"             = {self.z_M_longitudinal:.4f} m")
        
        # (4) 稳定性判别
        print("\n(4) 稳定性判别")
        
        print(f"\n    重心位置: z_G = H/2 = {self.H}/2 = {self.z_G:.3f} m")
        
        print("\n    ■ 横倾稳定性:")
        print(f"    稳心高: GM = z_M - z_G")
        print(f"           = {self.z_M_transverse:.4f} - {self.z_G:.3f}")
        print(f"           = {self.GM_transverse:.4f} m")
        
        if self.GM_transverse > 0:
            print(f"    判断: GM > 0，浮箱横倾稳定 ✓")
        elif self.GM_transverse == 0:
            print(f"    判断: GM = 0，浮箱横倾临界")
        else:
            print(f"    判断: GM < 0，浮箱横倾不稳定 ✗")
        
        print("\n    ■ 纵倾稳定性:")
        print(f"    稳心高: GM = z_M - z_G")
        print(f"           = {self.z_M_longitudinal:.4f} - {self.z_G:.3f}")
        print(f"           = {self.GM_longitudinal:.4f} m")
        
        if self.GM_longitudinal > 0:
            print(f"    判断: GM > 0，浮箱纵倾稳定 ✓")
        elif self.GM_longitudinal == 0:
            print(f"    判断: GM = 0，浮箱纵倾临界")
        else:
            print(f"    判断: GM < 0，浮箱纵倾不稳定 ✗")
        
        # (5) 稳定性分析
        print("\n(5) 稳定性分析")
        
        print("\n    ■ 影响因素:")
        print("    ① 吃水深度h:")
        print("       • h↑ → V_排↑ → r↓ → z_M可能↓")
        print("       • 吃水过深可能导致失稳")
        
        print("\n    ② 重心位置G:")
        print("       • G↑ → GM↓ → 稳定性↓")
        print("       • 重心越高越危险")
        
        print("\n    ③ 水线面形状:")
        print("       • B↑ → Ic↑ → r↑ → GM↑")
        print("       • 宽而扁的浮体更稳定")
        
        print(f"\n    ④ 长宽比影响:")
        print(f"       L/B = {self.L/self.B:.2f}")
        print(f"       GM_横倾/GM_纵倾 = {self.GM_transverse/self.GM_longitudinal:.2f}")
        print("       横倾稳定性较弱（宽度方向）")
        
        print("\n    ■ 临界吃水深度:")
        # 计算临界吃水（GM=0）
        # z_M = z_G
        # h/2 + (L·B³/12)/(L·B·h) = H/2
        # h/2 + B²/(12h) = H/2
        # 6h² - 6H·h + B² = 0
        a_coef = 6
        b_coef = -6 * self.H
        c_coef = self.B**2
        discriminant = b_coef**2 - 4*a_coef*c_coef
        
        if discriminant >= 0:
            h_crit1 = (-b_coef + np.sqrt(discriminant)) / (2*a_coef)
            h_crit2 = (-b_coef - np.sqrt(discriminant)) / (2*a_coef)
            h_crit = max(h_crit1, h_crit2)  # 取较大值
            
            if h_crit <= self.H:
                print(f"    横倾临界吃水: h_crit = {h_crit:.3f} m")
                print(f"    当前吃水: h = {self.h:.3f} m")
                if self.h < h_crit:
                    print(f"    安全裕度: Δh = {h_crit - self.h:.3f} m ✓")
                else:
                    print(f"    警告: 吃水超过临界值 ✗")
        
        print("\n【稳定性物理解释】")
        print("\n浮体倾斜时的力矩分析:")
        print("  • 重力W作用于G点，方向向下")
        print("  • 浮力F_b作用于C点，方向向上")
        print("  • 倾斜后浮力作用线通过M点")
        print("\n若M在G上方（GM>0）:")
        print("  → 浮力与重力形成扶正力矩")
        print("  → 浮体恢复到平衡位置")
        print("  → 稳定 ✓")
        print("\n若M在G下方（GM<0）:")
        print("  → 浮力与重力形成倾覆力矩")
        print("  → 浮体继续倾斜")
        print("  → 不稳定 ✗")
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(14, 11))
        
        # 子图1：浮力平衡示意图
        ax1 = plt.subplot(2, 2, 1)
        self._plot_equilibrium(ax1)
        
        # 子图2：稳定性分析图
        ax2 = plt.subplot(2, 2, 2)
        self._plot_stability(ax2)
        
        # 子图3：GM随吃水变化
        ax3 = plt.subplot(2, 2, 3)
        self._plot_GM_variation(ax3)
        
        # 子图4：倾斜状态示意
        ax4 = plt.subplot(2, 2, 4)
        self._plot_tilted_state(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_equilibrium(self, ax):
        """绘制浮力平衡示意图"""
        # 水面
        ax.plot([-0.5, self.B+0.5], [self.h, self.h], 'b-', linewidth=3, label='水面')
        ax.fill_between([-0.5, self.B+0.5], 0, self.h, color='lightblue', alpha=0.4)
        
        # 浮箱
        box = Rectangle((0, 0), self.B, self.H, facecolor='lightyellow',
                       edgecolor='black', linewidth=2.5)
        ax.add_patch(box)
        
        # 排水部分（深色）
        water_box = Rectangle((0, 0), self.B, self.h, facecolor='lightblue',
                             edgecolor='blue', linewidth=2, alpha=0.7)
        ax.add_patch(water_box)
        
        # 重心G
        G_x = self.B / 2
        G_y = self.z_G
        ax.plot(G_x, G_y, 'ro', markersize=12, label='重心G', zorder=5)
        ax.text(G_x+0.15, G_y, 'G', fontsize=12, weight='bold', color='red')
        
        # 浮心C
        C_x = self.B / 2
        C_y = self.z_C
        ax.plot(C_x, C_y, 'go', markersize=12, label='浮心C', zorder=5)
        ax.text(C_x+0.15, C_y, 'C', fontsize=12, weight='bold', color='green')
        
        # 重力
        ax.annotate('', xy=(G_x, G_y-0.2), xytext=(G_x, G_y),
                   arrowprops=dict(arrowstyle='->', lw=3, color='red'))
        ax.text(G_x+0.3, G_y-0.15, f'W={self.W}kN', fontsize=10, color='red')
        
        # 浮力
        ax.annotate('', xy=(C_x, C_y+0.2), xytext=(C_x, C_y),
                   arrowprops=dict(arrowstyle='->', lw=3, color='blue'))
        ax.text(C_x+0.3, C_y+0.15, f'F_b={self.F_b:.1f}kN', fontsize=10, color='blue')
        
        # 标注尺寸
        # 吃水深度h
        ax.annotate('', xy=(self.B+0.3, 0), xytext=(self.B+0.3, self.h),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
        ax.text(self.B+0.4, self.h/2, f'h={self.h:.2f}m', fontsize=10,
               rotation=90, va='center', color='purple')
        
        # 高度H
        ax.annotate('', xy=(-0.3, 0), xytext=(-0.3, self.H),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='brown'))
        ax.text(-0.4, self.H/2, f'H={self.H}m', fontsize=10,
               rotation=90, va='center', color='brown')
        
        # 宽度B
        ax.annotate('', xy=(0, -0.2), xytext=(self.B, -0.2),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='brown'))
        ax.text(self.B/2, -0.35, f'B={self.B}m', fontsize=10, ha='center', color='brown')
        
        ax.set_xlim(-0.6, self.B+0.6)
        ax.set_ylim(-0.5, self.H+0.3)
        ax.set_aspect('equal')
        ax.set_xlabel('宽度 (m)', fontsize=12)
        ax.set_ylabel('高度 (m)', fontsize=12)
        ax.set_title('浮力平衡状态', fontsize=13, weight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_stability(self, ax):
        """绘制稳定性分析图"""
        # 浮箱轮廓
        box = Rectangle((0, 0), self.B, self.H, fill=False,
                       edgecolor='black', linewidth=2.5)
        ax.add_patch(box)
        
        # 水面
        ax.plot([-0.2, self.B+0.2], [self.h, self.h], 'b-', linewidth=2.5)
        
        # 排水部分
        water_box = Rectangle((0, 0), self.B, self.h, facecolor='lightblue',
                             edgecolor='blue', linewidth=1.5, alpha=0.5)
        ax.add_patch(water_box)
        
        # 中心线
        center_x = self.B / 2
        ax.plot([center_x, center_x], [0, self.H+0.3], 'k--',
               linewidth=1.5, alpha=0.5)
        
        # C, G, M位置
        ax.plot(center_x, self.z_C, 'go', markersize=14, zorder=5)
        ax.text(center_x+0.15, self.z_C, 'C（浮心）', fontsize=11, weight='bold', color='green')
        
        ax.plot(center_x, self.z_G, 'ro', markersize=14, zorder=5)
        ax.text(center_x+0.15, self.z_G, 'G（重心）', fontsize=11, weight='bold', color='red')
        
        ax.plot(center_x, self.z_M_transverse, 'bo', markersize=14, zorder=5)
        ax.text(center_x+0.15, self.z_M_transverse, 'M（定倾中心）', fontsize=11, weight='bold', color='blue')
        
        # GM连线
        ax.plot([center_x, center_x], [self.z_G, self.z_M_transverse],
               'purple', linewidth=4, alpha=0.6, zorder=3)
        
        # GM标注
        ax.annotate('', xy=(center_x-0.15, self.z_G), xytext=(center_x-0.15, self.z_M_transverse),
                   arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
        ax.text(center_x-0.25, (self.z_G+self.z_M_transverse)/2,
               f'GM={self.GM_transverse:.3f}m', fontsize=11,
               rotation=90, va='center', ha='right', color='purple', weight='bold')
        
        # 稳定性判断
        if self.GM_transverse > 0:
            status = "稳定 ✓"
            color = 'green'
        else:
            status = "不稳定 ✗"
            color = 'red'
        
        ax.text(self.B/2, self.H+0.15, f'稳定性: {status}',
               fontsize=12, ha='center', weight='bold', color=color,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlim(-0.3, self.B+0.5)
        ax.set_ylim(-0.1, self.H+0.4)
        ax.set_aspect('equal')
        ax.set_xlabel('宽度 (m)', fontsize=12)
        ax.set_ylabel('高度 (m)', fontsize=12)
        ax.set_title('稳定性参数（C-G-M）', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_GM_variation(self, ax):
        """绘制GM随吃水变化曲线"""
        # 吃水范围
        h_array = np.linspace(0.1, self.H, 100)
        
        # 计算GM变化
        GM_trans, GM_long = self.analyze_stability_variation(h_array)
        
        # 绘制曲线
        ax.plot(h_array, GM_trans, 'b-', linewidth=2.5, label='横倾GM')
        ax.plot(h_array, GM_long, 'r-', linewidth=2.5, label='纵倾GM')
        
        # 当前工况点
        ax.plot(self.h, self.GM_transverse, 'bo', markersize=10,
               label=f'当前横倾: h={self.h:.2f}m', zorder=5)
        ax.plot(self.h, self.GM_longitudinal, 'ro', markersize=10,
               label=f'当前纵倾: h={self.h:.2f}m', zorder=5)
        
        # GM=0线
        ax.axhline(0, color='black', linestyle='--', linewidth=2, alpha=0.5,
                  label='临界线 GM=0')
        
        # 稳定区域
        ax.fill_between(h_array, 0, 0.5, color='green', alpha=0.1,
                       label='稳定区（GM>0）')
        ax.fill_between(h_array, -0.5, 0, color='red', alpha=0.1,
                       label='不稳定区（GM<0）')
        
        ax.set_xlabel('吃水深度 h (m)', fontsize=12)
        ax.set_ylabel('稳心高 GM (m)', fontsize=12)
        ax.set_title('稳心高随吃水变化', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.H)
    
    def _plot_tilted_state(self, ax):
        """绘制倾斜状态示意图"""
        # 倾斜角度
        theta = 10  # 度
        theta_rad = np.radians(theta)
        
        # 浮箱中心
        cx = 0
        cy = self.z_G
        
        # 倾斜后的浮箱顶点（绕重心旋转）
        corners = np.array([
            [-self.B/2, -self.z_G],
            [self.B/2, -self.z_G],
            [self.B/2, self.H-self.z_G],
            [-self.B/2, self.H-self.z_G]
        ])
        
        # 旋转矩阵
        rotation = np.array([
            [np.cos(theta_rad), -np.sin(theta_rad)],
            [np.sin(theta_rad), np.cos(theta_rad)]
        ])
        
        rotated_corners = corners @ rotation.T
        rotated_corners[:, 0] += cx
        rotated_corners[:, 1] += cy
        
        # 绘制倾斜浮箱
        tilted_box = Polygon(rotated_corners, facecolor='lightyellow',
                           edgecolor='black', linewidth=2.5, alpha=0.7)
        ax.add_patch(tilted_box)
        
        # 水面
        ax.plot([-1.5, 1.5], [self.h, self.h], 'b-', linewidth=3)
        ax.fill_between([-1.5, 1.5], 0, self.h, color='lightblue', alpha=0.3)
        
        # 重心G（相对位置不变）
        G_pos = np.array([0, 0]) @ rotation.T
        G_x = cx + G_pos[0]
        G_y = cy + G_pos[1]
        ax.plot(G_x, G_y, 'ro', markersize=12, zorder=5)
        ax.text(G_x+0.15, G_y, 'G', fontsize=12, weight='bold', color='red')
        
        # 新浮心C'（考虑排水体积变化）
        C_offset = np.array([0, self.z_C - self.z_G]) @ rotation.T
        C_new_x = cx + C_offset[0]
        C_new_y = cy + C_offset[1]
        ax.plot(C_new_x, C_new_y, 'go', markersize=12, zorder=5)
        ax.text(C_new_x+0.15, C_new_y, "C'", fontsize=12, weight='bold', color='green')
        
        # 定倾中心M（在垂直线上）
        M_x = cx
        M_y = self.z_M_transverse
        ax.plot(M_x, M_y, 'bo', markersize=12, zorder=5)
        ax.text(M_x+0.15, M_y, 'M', fontsize=12, weight='bold', color='blue')
        
        # 浮力作用线（通过C'和M）
        ax.plot([C_new_x, M_x], [C_new_y, M_y], 'g--', linewidth=2, alpha=0.7)
        
        # 重力
        ax.annotate('', xy=(G_x, G_y-0.3), xytext=(G_x, G_y),
                   arrowprops=dict(arrowstyle='->', lw=3, color='red'))
        ax.text(G_x-0.3, G_y-0.2, 'W', fontsize=11, color='red', weight='bold')
        
        # 浮力
        ax.annotate('', xy=(C_new_x, C_new_y+0.3), xytext=(C_new_x, C_new_y),
                   arrowprops=dict(arrowstyle='->', lw=3, color='blue'))
        ax.text(C_new_x-0.3, C_new_y+0.2, 'F_b', fontsize=11, color='blue', weight='bold')
        
        # 力臂
        if self.GM_transverse > 0:
            # 扶正力矩
            ax.text(0.5, 1.3, f'倾斜角θ={theta}°', fontsize=11)
            ax.text(0.5, 1.1, f'扶正力矩 = W·GM·sinθ', fontsize=10,
                   color='green', weight='bold')
            ax.text(0.5, 0.9, f'浮体将恢复平衡 ✓', fontsize=10, color='green')
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.2, 1.6)
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title(f'倾斜状态分析（θ={theta}°）', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)


def test_problem_011():
    """测试题目011"""
    # 已知条件
    L = 4.0      # 长度 (m)
    B = 2.0      # 宽度 (m)
    H = 1.5      # 高度 (m)
    W = 80.0     # 重量 (kN)
    gamma = 10.0 # 水的重度 (kN/m³)
    
    # 创建分析对象
    buoyancy = BuoyancyStability(L, B, H, W, gamma)
    
    # 打印结果
    buoyancy.print_results()
    
    print("\n【最终答案】")
    print("="*80)
    print(f"(1) 吃水深度: h = {buoyancy.h:.3f} m")
    print(f"    吃水比: h/H = {buoyancy.draft_ratio:.1%}")
    print(f"(2) 浮心位置: z_C = {buoyancy.z_C:.3f} m（从底面算起）")
    print(f"(3) 定倾中心位置:")
    print(f"    横倾: z_M = {buoyancy.z_M_transverse:.4f} m")
    print(f"    纵倾: z_M = {buoyancy.z_M_longitudinal:.4f} m")
    print(f"(4) 稳定性判别:")
    print(f"    横倾GM = {buoyancy.GM_transverse:.4f} m → {buoyancy.stability_transverse}")
    print(f"    纵倾GM = {buoyancy.GM_longitudinal:.4f} m → {buoyancy.stability_longitudinal}")
    print("(5) 稳定性影响因素:")
    print("    • 吃水深度h：过深可能失稳")
    print("    • 重心位置G：越高越危险")
    print("    • 水线面形状：宽而扁更稳定")
    print("="*80)
    
    # 可视化
    print("\n生成可视化图表...")
    fig = buoyancy.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_011_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_011_result.png")
    
    # 验证
    assert buoyancy.h > 0, "吃水深度必须为正"
    assert buoyancy.h < buoyancy.H, "吃水深度不能超过高度"
    assert abs(buoyancy.F_b - buoyancy.W) < 0.1, "浮力必须等于重量"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("浮力与稳定性是静水力学的重要内容！")
    print("• 阿基米德原理: F_b = γV_排 = W")
    print("• 浮心C: 排水体积的几何中心")
    print("• 定倾中心M: M = C + Ic/V_排")
    print("• 稳定性判据: GM > 0（稳定）")
    print("• 应用: 船舶设计、浮式结构、水上运输")


if __name__ == "__main__":
    test_problem_011()
