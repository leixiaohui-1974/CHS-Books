"""
《水力学1000题详解》- 题目033: 漂浮物体浮力
=================================================

知识点：阿基米德原理、漂浮平衡、吃水深度
难度：⭐ 基础题

功能：
1. 计算漂浮物体的浮力和吃水深度
2. 可视化物体漂浮状态
3. 分析加载能力
4. 动态展示不同密度物体的漂浮状态
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib as mpl

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False


class FloatingBody:
    """漂浮物体类"""
    
    def __init__(self, length, width, height, rho_body, rho_fluid=1000, g=9.8):
        """
        初始化漂浮物体参数
        
        参数:
            length: 长度 (m)
            width: 宽度 (m)
            height: 高度 (m)
            rho_body: 物体密度 (kg/m³)
            rho_fluid: 液体密度 (kg/m³)，默认为水
            g: 重力加速度 (m/s²)
        """
        self.a = length
        self.b = width
        self.h = height
        self.rho_body = rho_body
        self.rho_fluid = rho_fluid
        self.g = g
        
        # 计算物体总体积和质量
        self.V_total = self.a * self.b * self.h
        self.m = self.rho_body * self.V_total
        self.G = self.m * self.g
        
        # 判断浮沉状态
        self._check_floating_status()
        
        # 计算浮力和吃水深度
        if self.status == "漂浮":
            self._calculate_floating()
        elif self.status == "悬浮":
            self._calculate_suspending()
        else:  # 下沉
            self._calculate_sinking()
    
    def _check_floating_status(self):
        """判断物体浮沉状态"""
        if self.rho_body < self.rho_fluid:
            self.status = "漂浮"
        elif self.rho_body == self.rho_fluid:
            self.status = "悬浮"
        else:
            self.status = "下沉"
    
    def _calculate_floating(self):
        """计算漂浮状态参数"""
        # 漂浮：F_浮 = G
        self.F_buoy = self.G
        
        # 吃水深度：d = h * (rho_body / rho_fluid)
        self.draft = self.h * (self.rho_body / self.rho_fluid)
        
        # 浸没体积
        self.V_submerged = self.a * self.b * self.draft
        
        # 露出高度
        self.h_above = self.h - self.draft
        
        # 露出比例
        self.ratio_above = self.h_above / self.h * 100
        
        # 最大加载能力（使物体刚好完全浸没）
        self.F_buoy_max = self.rho_fluid * self.g * self.V_total
        self.delta_F = self.F_buoy_max - self.F_buoy
        self.max_load = self.delta_F / self.g  # kg
    
    def _calculate_suspending(self):
        """计算悬浮状态参数"""
        self.F_buoy = self.G
        self.draft = self.h  # 完全浸没
        self.V_submerged = self.V_total
        self.h_above = 0
        self.ratio_above = 0
        self.max_load = 0
    
    def _calculate_sinking(self):
        """计算下沉状态参数"""
        # 完全浸没时的浮力
        self.F_buoy = self.rho_fluid * self.g * self.V_total
        self.draft = self.h
        self.V_submerged = self.V_total
        self.h_above = 0
        self.ratio_above = 0
        
        # 净下沉力
        self.net_weight = self.G - self.F_buoy
        self.max_load = 0
    
    def plot_floating_analysis(self, save_path=None):
        """绘制漂浮分析图"""
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2)
        
        ax1 = fig.add_subplot(gs[0, 0])  # 左上：漂浮状态示意图
        ax2 = fig.add_subplot(gs[0, 1])  # 右上：受力分析
        ax3 = fig.add_subplot(gs[1, :])  # 下方：密度影响分析
        
        # ===== 左上图：漂浮状态示意图 =====
        ax1.set_xlim(-0.5, self.a + 1)
        ax1.set_ylim(-1, self.h + 1.5)
        ax1.set_aspect('equal')
        
        if self.status == "漂浮":
            # 水面
            water_level = 0
            ax1.fill_between([-0.5, self.a + 1], -1, water_level, 
                            alpha=0.3, color='lightblue', label='水')
            ax1.plot([-0.5, self.a + 1], [water_level, water_level], 
                    'b--', linewidth=2, label='水面')
            
            # 物体（分为浸没部分和露出部分）
            # 浸没部分（深色）
            submerged_rect = Rectangle((0, water_level - self.draft), 
                                      self.a, self.draft,
                                      facecolor='tan', edgecolor='brown',
                                      linewidth=3, alpha=0.8, label='浸没部分')
            ax1.add_patch(submerged_rect)
            
            # 露出部分（浅色）
            if self.h_above > 0:
                above_rect = Rectangle((0, water_level), 
                                      self.a, self.h_above,
                                      facecolor='wheat', edgecolor='brown',
                                      linewidth=3, alpha=0.6, label='露出部分')
                ax1.add_patch(above_rect)
            
            # 标注尺寸
            # 吃水深度
            ax1.plot([self.a + 0.3, self.a + 0.6], 
                    [water_level - self.draft, water_level - self.draft], 'r-', linewidth=1.5)
            ax1.plot([self.a + 0.3, self.a + 0.6], 
                    [water_level, water_level], 'r-', linewidth=1.5)
            ax1.annotate('', xy=(self.a + 0.45, water_level), 
                        xytext=(self.a + 0.45, water_level - self.draft),
                        arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            ax1.text(self.a + 0.8, water_level - self.draft/2, 
                    f'd={self.draft:.2f}m', fontsize=11, fontweight='bold', color='red')
            
            # 露出高度
            if self.h_above > 0:
                ax1.plot([-0.3, -0.6], [water_level, water_level], 'g-', linewidth=1.5)
                ax1.plot([-0.3, -0.6], 
                        [water_level + self.h_above, water_level + self.h_above], 'g-', linewidth=1.5)
                ax1.annotate('', xy=(-0.45, water_level + self.h_above), 
                            xytext=(-0.45, water_level),
                            arrowprops=dict(arrowstyle='<->', color='green', lw=2))
                ax1.text(-1.1, water_level + self.h_above/2, 
                        f'{self.h_above:.2f}m\n({self.ratio_above:.1f}%)', 
                        fontsize=10, fontweight='bold', color='green')
            
            # 重心（物体中心）
            cg_y = water_level - self.draft + self.h/2
            ax1.plot(self.a/2, cg_y, 'r*', markersize=20, label='重心G')
            ax1.text(self.a/2 + 0.2, cg_y, 'G', fontsize=14, fontweight='bold')
            
            # 浮心（浸没部分中心）
            cb_y = water_level - self.draft/2
            ax1.plot(self.a/2, cb_y, 'b^', markersize=15, label='浮心B')
            ax1.text(self.a/2 + 0.2, cb_y, 'B', fontsize=14, fontweight='bold')
        
        ax1.set_xlabel('长度 (m)', fontsize=11)
        ax1.set_ylabel('高度 (m)', fontsize=11)
        ax1.set_title(f'漂浮状态示意图 - {self.status}', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # ===== 右上图：受力分析 =====
        ax2.set_xlim(-2, 2)
        ax2.set_ylim(-2, 3)
        ax2.set_aspect('equal')
        
        # 物体简图（小方块）
        body_rect = Rectangle((-0.3, 0), 0.6, 0.4,
                             facecolor='tan', edgecolor='brown', linewidth=2)
        ax2.add_patch(body_rect)
        
        # 重力箭头（向下）
        G_scale = self.G / 10000  # 缩放
        ax2.arrow(0, 0, 0, -G_scale, 
                 head_width=0.15, head_length=0.15, fc='red', ec='red', 
                 linewidth=3, label=f'重力G={self.G/1000:.2f} kN')
        ax2.text(0.3, -G_scale/2, f'G={self.G/1000:.2f} kN', 
                fontsize=11, fontweight='bold', color='red')
        
        # 浮力箭头（向上）
        F_scale = self.F_buoy / 10000
        ax2.arrow(0, 0.4, 0, F_scale, 
                 head_width=0.15, head_length=0.15, fc='blue', ec='blue', 
                 linewidth=3, label=f'浮力F={self.F_buoy/1000:.2f} kN')
        ax2.text(0.3, 0.4 + F_scale/2, f'F={self.F_buoy/1000:.2f} kN', 
                fontsize=11, fontweight='bold', color='blue')
        
        # 平衡标注
        if abs(self.G - self.F_buoy) < 0.1:
            ax2.text(0, -1.5, '✓ 平衡状态：F = G', 
                    ha='center', fontsize=13, fontweight='bold', color='green',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax2.set_xlabel('')
        ax2.set_ylabel('')
        ax2.set_title('受力分析', fontsize=13, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.axis('off')
        
        # ===== 下方图：密度影响分析 =====
        rho_range = np.linspace(100, 1500, 50)
        draft_list = []
        ratio_above_list = []
        
        for rho in rho_range:
            if rho < self.rho_fluid:
                d = self.h * (rho / self.rho_fluid)
                draft_list.append(d)
                ratio_above_list.append((self.h - d) / self.h * 100)
            else:
                draft_list.append(self.h)
                ratio_above_list.append(0)
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(rho_range, draft_list, 'b-', linewidth=2.5, 
                        label='吃水深度 d', marker='o', markersize=4)
        line2 = ax3_twin.plot(rho_range, ratio_above_list, 'g--', linewidth=2.5, 
                             label='露出比例', marker='s', markersize=4)
        
        # 水的密度线
        ax3.axvline(x=self.rho_fluid, color='cyan', linestyle=':', 
                   linewidth=2, alpha=0.7, label='水的密度')
        
        # 当前物体标记
        ax3.plot(self.rho_body, self.draft, 'ro', markersize=15, 
                markeredgewidth=3, markerfacecolor='none')
        ax3.text(self.rho_body, self.draft + 0.05, 
                f'当前物体\nρ={self.rho_body} kg/m³', 
                ha='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax3.set_xlabel('物体密度 ρ (kg/m³)', fontsize=12)
        ax3.set_ylabel('吃水深度 d (m)', fontsize=12, color='b')
        ax3_twin.set_ylabel('露出比例 (%)', fontsize=12, color='g')
        ax3.set_title('物体密度对漂浮状态的影响', fontsize=14, fontweight='bold')
        
        ax3.tick_params(axis='y', labelcolor='b')
        ax3_twin.tick_params(axis='y', labelcolor='g')
        
        # 组合图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper left', fontsize=10)
        
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存至: {save_path}")
        
        plt.show()
    
    def print_results(self):
        """打印详细计算结果"""
        print("=" * 70)
        print("题目033: 漂浮物体浮力 - 计算结果")
        print("=" * 70)
        
        print(f"\n【物体参数】")
        print(f"  尺寸: {self.a}m × {self.b}m × {self.h}m")
        print(f"  体积: V = {self.V_total} m³")
        print(f"  密度: ρ_物 = {self.rho_body} kg/m³")
        print(f"  质量: m = {self.m} kg")
        print(f"  重力: G = {self.G} N = {self.G/1000:.2f} kN")
        
        print(f"\n【液体参数】")
        print(f"  密度: ρ_液 = {self.rho_fluid} kg/m³")
        
        print(f"\n【浮沉判断】")
        print(f"  ρ_物 = {self.rho_body} kg/m³")
        print(f"  ρ_液 = {self.rho_fluid} kg/m³")
        print(f"  比较: ρ_物 {'<' if self.rho_body < self.rho_fluid else '=' if self.rho_body == self.rho_fluid else '>'} ρ_液")
        print(f"  结论: {self.status}")
        
        if self.status == "漂浮":
            print(f"\n【漂浮状态计算】")
            print(f"  (1) 浮力:")
            print(f"      漂浮平衡: F_浮 = G")
            print(f"      F_浮 = {self.F_buoy} N = {self.F_buoy/1000:.2f} kN")
            
            print(f"\n  (2) 吃水深度:")
            print(f"      公式: d = h × (ρ_物/ρ_液)")
            print(f"      d = {self.h} × ({self.rho_body}/{self.rho_fluid})")
            print(f"      d = {self.draft:.3f} m")
            
            print(f"\n  (3) 浸没体积:")
            print(f"      V_浸 = a × b × d")
            print(f"      V_浸 = {self.a} × {self.b} × {self.draft:.3f}")
            print(f"      V_浸 = {self.V_submerged:.3f} m³")
            print(f"      浸没比例: {self.V_submerged/self.V_total*100:.1f}%")
            
            print(f"\n  (4) 露出部分:")
            print(f"      露出高度: {self.h_above:.3f} m")
            print(f"      露出比例: {self.ratio_above:.1f}%")
            
            print(f"\n  (5) 加载能力:")
            print(f"      完全浸没时浮力: F_max = ρ_液 × g × V")
            print(f"                     = {self.F_buoy_max:.0f} N")
            print(f"      浮力增量: ΔF = F_max - F_浮 = {self.delta_F:.0f} N")
            print(f"      最大加载: {self.max_load:.1f} kg（约{self.max_load/1000:.2f}吨）")
            print(f"      【解释】: 可再加载{self.max_load:.1f}kg重物使物体刚好完全浸没")
        
        elif self.status == "下沉":
            print(f"\n【下沉状态】")
            print(f"  浮力: F_浮 = {self.F_buoy:.0f} N（完全浸没）")
            print(f"  重力: G = {self.G:.0f} N")
            print(f"  净下沉力: F_净 = G - F_浮 = {self.net_weight:.0f} N")
            print(f"  物体将沉入水底")
        
        print("\n" + "=" * 70)


def main():
    """主程序"""
    
    print("\n" + "="*70)
    print("《水力学1000题详解》- 题目033")
    print("漂浮物体浮力计算")
    print("="*70 + "\n")
    
    # 创建漂浮木块实例
    wood = FloatingBody(
        length=2.0,
        width=1.0,
        height=0.5,
        rho_body=700,  # 木块密度
        rho_fluid=1000,  # 水密度
        g=9.8
    )
    
    # 打印计算结果
    wood.print_results()
    
    # 绘制分析图
    print("\n正在生成漂浮分析图...")
    wood.plot_floating_analysis()
    
    print("\n✅ 题目033 计算完成！\n")


def test_floating_body():
    """单元测试"""
    print("\n【单元测试】漂浮物体计算验证")
    print("-" * 50)
    
    wood = FloatingBody(2.0, 1.0, 0.5, 700, 1000, 9.8)
    
    # 测试1：浮沉判断
    assert wood.status == "漂浮", "密度700应该漂浮"
    print(f"✓ 测试1通过: 浮沉判断 = {wood.status}")
    
    # 测试2：吃水深度
    expected_draft = 0.5 * (700/1000)
    assert abs(wood.draft - expected_draft) < 0.01, "吃水深度计算错误"
    print(f"✓ 测试2通过: 吃水深度 = {wood.draft:.3f} m")
    
    # 测试3：漂浮平衡
    assert abs(wood.F_buoy - wood.G) < 1, "漂浮时浮力应等于重力"
    print(f"✓ 测试3通过: F_浮 = G = {wood.F_buoy:.0f} N")
    
    # 测试4：浸没体积
    expected_V_sub = 2.0 * 1.0 * expected_draft
    assert abs(wood.V_submerged - expected_V_sub) < 0.01, "浸没体积计算错误"
    print(f"✓ 测试4通过: 浸没体积 = {wood.V_submerged:.3f} m³")
    
    # 测试5：露出比例
    expected_ratio = (0.5 - expected_draft) / 0.5 * 100
    assert abs(wood.ratio_above - expected_ratio) < 0.1, "露出比例计算错误"
    print(f"✓ 测试5通过: 露出比例 = {wood.ratio_above:.1f}%")
    
    # 测试6：下沉物体
    iron = FloatingBody(1.0, 1.0, 1.0, 7800, 1000, 9.8)
    assert iron.status == "下沉", "密度7800应该下沉"
    print(f"✓ 测试6通过: 铁块下沉判断正确")
    
    print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    # 运行单元测试
    test_floating_body()
    
    # 运行主程序
    main()
