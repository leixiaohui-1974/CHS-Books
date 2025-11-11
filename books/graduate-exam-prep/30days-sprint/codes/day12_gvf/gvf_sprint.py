#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 12: 明渠非均匀流（水面线）
Sprint Day 12: Gradually Varied Flow (GVF)

⏰ 学习时间：3小时
📚 核心考点：
  1. 水面线微分方程：dh/dx = (i - J)/(1 - Fr²)
  2. 水面线类型判断：12种水面线
  3. 水面线定性绘制

🎯 学习目标：
  - 掌握水面线微分方程
  - 熟练判断水面线类型
  - 理解水深变化规律

💪 今日格言：水面线是考研难点！掌握12种类型=拿到10分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.integrate import odeint

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day12GVF:
    """
    Day 12：明渠非均匀流（水面线）
    
    包含2个核心例题：
    1. 基础题：水面线类型判断
    2. 强化题：水面线数值计算
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        
    def manning_friction_slope(self, h, b, n, Q, m=0):
        """
        计算Manning摩阻坡度
        
        参数:
            h: 水深 (m)
            b: 渠底宽度 (m)
            n: Manning糙率
            Q: 流量 (m³/s)
            m: 边坡系数（梯形断面，矩形为0）
        
        返回:
            J: 摩阻坡度
        """
        A = b * h + m * h**2
        P = b + 2 * h * np.sqrt(1 + m**2)
        R = A / P
        v = Q / A
        
        # Manning公式：v = (1/n)R^(2/3)√J
        # 因此：J = (nv/R^(2/3))²
        J = (n * v / R**(2/3))**2
        
        return J
    
    def gvf_equation(self, h, x, b, n, Q, i, m=0):
        """
        水面线微分方程 dh/dx = (i - J)/(1 - Fr²)
        
        参数:
            h: 水深 (m)
            x: 水平距离 (m)
            b: 渠底宽度 (m)
            n: Manning糙率
            Q: 流量 (m³/s)
            i: 渠底坡度
            m: 边坡系数
        
        返回:
            dh/dx: 水深梯度
        """
        if h <= 0.01:  # 防止水深过小
            return 0
        
        # 计算水力要素
        A = b * h + m * h**2
        v = Q / A
        Fr = v / np.sqrt(self.g * h)
        
        # 摩阻坡度
        J = self.manning_friction_slope(h, b, n, Q, m)
        
        # 水面线微分方程
        dh_dx = (i - J) / (1 - Fr**2)
        
        return dh_dx
    
    def example_1_water_profile_classification(self):
        """
        例题1：水面线类型判断（基础题）⭐⭐⭐⭐⭐
        
        题目：矩形明渠，b=3m，n=0.020，i=0.001，Q=12m³/s
        求：(1) 正常水深h₀
            (2) 临界水深hc
            (3) 判断并绘制3种典型水面线
        
        考点：水面线分类（12种），定性分析
        难度：基础（必考！）
        时间：20分钟
        分值：10分
        """
        print("\n" + "="*60)
        print("例题1：水面线类型判断（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        b = 3.0      # 渠宽 (m)
        n = 0.020    # Manning糙率
        i = 0.001    # 渠底坡度
        Q = 12.0     # 流量 (m³/s)
        
        print(f"\n已知条件：")
        print(f"  矩形明渠宽度 b = {b:.1f} m")
        print(f"  Manning糙率 n = {n:.3f}")
        print(f"  渠底坡度 i = {i:.4f}")
        print(f"  流量 Q = {Q:.1f} m³/s")
        
        # (1) 计算正常水深h₀（通过迭代求解）
        print(f"\n解题步骤：")
        print(f"\n(1) 计算正常水深h₀：")
        print(f"    Manning公式：Q = (1/n)AR^(2/3)√i")
        print(f"    ")
        
        # 使用迭代法求正常水深
        from scipy.optimize import fsolve
        
        def manning_eq(h):
            A = b * h
            P = b + 2 * h
            R = A / P
            Q_calc = (1/n) * A * R**(2/3) * np.sqrt(i)
            return Q_calc - Q
        
        h0 = fsolve(manning_eq, 1.5)[0]
        
        A0 = b * h0
        P0 = b + 2 * h0
        R0 = A0 / P0
        v0 = Q / A0
        Fr0 = v0 / np.sqrt(self.g * h0)
        
        print(f"    迭代求解得：h₀ = {h0:.4f} m ✓")
        print(f"    ")
        print(f"    验证：")
        print(f"    A₀ = bh₀ = {b} × {h0:.4f} = {A0:.4f} m²")
        print(f"    P₀ = b + 2h₀ = {b} + 2×{h0:.4f} = {P0:.4f} m")
        print(f"    R₀ = A₀/P₀ = {R0:.4f} m")
        print(f"    Q = (1/{n})×{A0:.4f}×{R0:.4f}^(2/3)×√{i}")
        Q_check = (1/n) * A0 * R0**(2/3) * np.sqrt(i)
        print(f"      = {Q_check:.3f} m³/s ≈ {Q:.1f} m³/s ✓")
        print(f"    ")
        print(f"    Fr₀ = v₀/√(gh₀) = {v0:.3f}/√({self.g:.2f}×{h0:.4f})")
        print(f"        = {Fr0:.4f} < 1")
        print(f"    ∴ 正常水深对应缓流 ✓")
        
        # (2) 计算临界水深
        print(f"\n(2) 计算临界水深hc：")
        q = Q / b
        hc = (q**2 / self.g)**(1/3)
        vc = Q / (b * hc)
        
        print(f"    单宽流量 q = Q/b = {Q}/{b} = {q:.3f} m²/s")
        print(f"    hc = (q²/g)^(1/3)")
        print(f"       = ({q:.3f}²/{self.g:.2f})^(1/3)")
        print(f"       = {hc:.4f} m ✓")
        print(f"    ")
        print(f"    vc = q/hc = {q:.3f}/{hc:.4f} = {vc:.3f} m/s")
        
        # (3) 比较h₀和hc，确定渠道类型
        print(f"\n(3) 渠道类型判断：")
        print(f"    h₀ = {h0:.4f} m")
        print(f"    hc = {hc:.4f} m")
        print(f"    ")
        
        if h0 > hc:
            print(f"    ∵ h₀ > hc ({h0:.4f} > {hc:.4f})")
            print(f"    ∴ 渠道类型：缓坡渠道（Mild slope, M型）✓")
            channel_type = "M"
        elif h0 < hc:
            print(f"    ∵ h₀ < hc ({h0:.4f} < {hc:.4f})")
            print(f"    ∴ 渠道类型：陡坡渠道（Steep slope, S型）")
            channel_type = "S"
        else:
            print(f"    ∵ h₀ = hc")
            print(f"    ∴ 渠道类型：临界坡渠道（Critical slope, C型）")
            channel_type = "C"
        
        # (4) 水面线分类
        print(f"\n(4) 水面线分类（{channel_type}型渠道）：")
        print(f"    ")
        print(f"    水深分区：")
        print(f"    Zone 1: h > h₀ (h > {h0:.4f}m)")
        print(f"    Zone 2: hc < h < h₀ ({hc:.4f}m < h < {h0:.4f}m)")
        print(f"    Zone 3: h < hc (h < {hc:.4f}m)")
        print(f"    ")
        print(f"    可能的水面线类型：")
        print(f"    M1型：h > h₀，水深递减（壅水曲线）")
        print(f"    M2型：hc < h < h₀，水深递增（降水曲线）")
        print(f"    M3型：h < hc，水深递增（急流段）")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：渠道纵剖面与水深分区
        ax1 = plt.subplot(3, 2, (1, 2))
        
        x_range = np.linspace(0, 100, 500)
        
        # 渠底线
        z_bottom = -i * x_range
        ax1.plot(x_range, z_bottom, 'k-', linewidth=2, label='渠底')
        
        # 正常水深线
        z_h0 = z_bottom + h0
        ax1.plot(x_range, z_h0, 'b--', linewidth=2, label=f'正常水深线 h₀={h0:.3f}m')
        
        # 临界水深线
        z_hc = z_bottom + hc
        ax1.plot(x_range, z_hc, 'r--', linewidth=2, label=f'临界水深线 hc={hc:.3f}m')
        
        # 标注分区
        y_mid = z_bottom[50]
        ax1.fill_between([0, 100], z_h0[0], z_h0[0]+0.5, alpha=0.2, color='blue', label='Zone 1 (h>h₀)')
        ax1.fill_between([0, 100], z_hc[0], z_h0[0], alpha=0.2, color='green', label='Zone 2 (hc<h<h₀)')
        ax1.fill_between([0, 100], z_hc[0]-0.5, z_hc[0], alpha=0.2, color='orange', label='Zone 3 (h<hc)')
        
        ax1.text(50, z_h0[50]+0.25, 'Zone 1\n(M1型)', ha='center', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        ax1.text(50, (z_hc[50]+z_h0[50])/2, 'Zone 2\n(M2型)', ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        ax1.text(50, z_hc[50]-0.25, 'Zone 3\n(M3型)', ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow'))
        
        ax1.set_xlabel('水平距离 x (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('Day 12 例题1：渠道纵剖面与水深分区', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 100])
        
        # 子图2：M1型水面线（壅水曲线）
        ax2 = plt.subplot(3, 2, 3)
        
        # M1: h从h₀+0.5递减到h₀
        h_M1 = np.linspace(h0+0.5, h0, 100)
        x_M1 = np.linspace(0, 50, 100)
        z_bottom_M1 = -i * x_M1
        z_M1 = z_bottom_M1 + h_M1
        
        ax2.plot(x_M1, z_bottom_M1, 'k-', linewidth=2)
        ax2.plot(x_M1, z_M1, 'b-', linewidth=3, label='M1水面线')
        ax2.axhline(y=h0, color='b', linestyle='--', linewidth=1, label=f'h₀={h0:.3f}m')
        ax2.axhline(y=hc, color='r', linestyle='--', linewidth=1, label=f'hc={hc:.3f}m')
        
        # 标注特征
        ax2.annotate('h>h₀\n壅水段', xy=(25, z_M1[50]), xytext=(30, z_M1[50]+0.3),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=2),
                    fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow'))
        ax2.arrow(40, z_M1[80], -5, 0, head_width=0.05, head_length=2, 
                 fc='blue', ec='blue', linewidth=2)
        ax2.text(42, z_M1[80], '水深递减', fontsize=9, color='blue')
        
        ax2.set_xlabel('x (m)', fontsize=11)
        ax2.set_ylabel('高程 (m)', fontsize=11)
        ax2.set_title('M1型水面线（壅水曲线）', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 子图3：M2型水面线（降水曲线）
        ax3 = plt.subplot(3, 2, 4)
        
        # M2: h从h₀递增到h₀-0.3
        h_M2_start = h0 - 0.3
        h_M2 = h_M2_start + (h0 - h_M2_start) * (1 - np.exp(-x_M1/20))
        z_M2 = z_bottom_M1 + h_M2
        
        ax3.plot(x_M1, z_bottom_M1, 'k-', linewidth=2)
        ax3.plot(x_M1, z_M2, 'g-', linewidth=3, label='M2水面线')
        ax3.axhline(y=h0, color='b', linestyle='--', linewidth=1, label=f'h₀={h0:.3f}m')
        ax3.axhline(y=hc, color='r', linestyle='--', linewidth=1, label=f'hc={hc:.3f}m')
        
        ax3.annotate('hc<h<h₀\n降水段', xy=(25, z_M2[50]), xytext=(30, z_M2[50]-0.3),
                    arrowprops=dict(arrowstyle='->', color='green', lw=2),
                    fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow'))
        ax3.arrow(10, z_M2[20], 5, 0.05, head_width=0.05, head_length=2,
                 fc='green', ec='green', linewidth=2)
        ax3.text(12, z_M2[20]+0.1, '水深递增', fontsize=9, color='green')
        
        ax3.set_xlabel('x (m)', fontsize=11)
        ax3.set_ylabel('高程 (m)', fontsize=11)
        ax3.set_title('M2型水面线（降水曲线）', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 子图4：M3型水面线（急流段）
        ax4 = plt.subplot(3, 2, 5)
        
        # M3: h从0.3递增到hc
        h_M3 = 0.3 + (hc - 0.3) * (1 - np.exp(-x_M1/15))
        z_M3 = z_bottom_M1 + h_M3
        
        ax4.plot(x_M1, z_bottom_M1, 'k-', linewidth=2)
        ax4.plot(x_M1, z_M3, 'orange', linewidth=3, label='M3水面线')
        ax4.axhline(y=h0, color='b', linestyle='--', linewidth=1, label=f'h₀={h0:.3f}m')
        ax4.axhline(y=hc, color='r', linestyle='--', linewidth=1, label=f'hc={hc:.3f}m')
        
        ax4.annotate('h<hc\n急流段', xy=(25, z_M3[50]), xytext=(30, z_M3[50]-0.2),
                    arrowprops=dict(arrowstyle='->', color='orange', lw=2),
                    fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow'))
        ax4.arrow(10, z_M3[20], 5, 0.08, head_width=0.05, head_length=2,
                 fc='orange', ec='orange', linewidth=2)
        ax4.text(12, z_M3[20]+0.1, '水深递增', fontsize=9, color='orange')
        
        ax4.set_xlabel('x (m)', fontsize=11)
        ax4.set_ylabel('高程 (m)', fontsize=11)
        ax4.set_title('M3型水面线（急流段）', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        # 子图5：水面线分类表（12种）
        ax5 = plt.subplot(3, 2, 6)
        ax5.axis('off')
        
        table_data = [
            ['渠道类型', 'Zone 1', 'Zone 2', 'Zone 3'],
            ['M型(缓坡)', 'M1(壅水↓)', 'M2(降水↑)', 'M3(急流↑)'],
            ['S型(陡坡)', 'S1(壅水↓)', 'S2(降水↑)', 'S3(急流↑)'],
            ['C型(临界)', 'C1(壅水↓)', '-', 'C3(急流↑)'],
            ['H型(平坡)', 'H2(降水↑)', '-', 'H3(急流↑)'],
            ['A型(反坡)', 'A2(降水↑)', '-', 'A3(急流↑)']
        ]
        
        table = ax5.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.25, 0.25, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        # 设置表头样式
        for i in range(4):
            table[(0, i)].set_facecolor('#4ECDC4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮M型
        for i in range(1, 4):
            table[(1, i)].set_facecolor('#FFE66D')
        
        ax5.set_title('水面线12种类型分类表', fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day12_gvf/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（10分评分标准）：")
        print("="*60)
        print("✓ (1) 计算正常水深h₀（Manning公式）(3分) ⭐")
        print("✓ (2) 计算临界水深hc (2分)")
        print("✓ (3) 比较h₀与hc，确定渠道类型 (2分)")
        print("✓ (4) 划分水深分区（Zone 1, 2, 3）(1分)")
        print("✓ (5) 判断水面线类型（M1/M2/M3）(2分) ⭐")
        
        print("\n💡 易错点：")
        print("  ⚠️ 正常水深h₀要用Manning公式迭代求解")
        print("  ⚠️ 渠道类型：h₀>hc→缓坡(M)；h₀<hc→陡坡(S)")
        print("  ⚠️ 水面线类型：M1降，M2升，M3升")
        print("  ⚠️ 12种水面线要熟记！")
        
        return {'h0': h0, 'hc': hc, 'channel_type': channel_type}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 12 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 水面线微分方程：")
        print("     dh/dx = (i - J)/(1 - Fr²)")
        print("     ")
        print("  2. 判断依据：")
        print("     • 分子(i-J)：决定凹凸性")
        print("     • 分母(1-Fr²)：决定升降")
        print("     ")
        print("  3. 渠道类型判断：")
        print("     • h₀ > hc → 缓坡(M型)")
        print("     • h₀ < hc → 陡坡(S型)")
        print("     • h₀ = hc → 临界坡(C型)")
        print("     • i = 0 → 平坡(H型)")
        print("     • i < 0 → 反坡(A型)")
        
        print("\n✅ 12种水面线速记：")
        print("  ")
        print("  【M型（缓坡）】h₀ > hc")
        print("  • M1: h > h₀，壅水，水深↓")
        print("  • M2: hc < h < h₀，降水，水深↑")
        print("  • M3: h < hc，急流，水深↑")
        print("  ")
        print("  【S型（陡坡）】h₀ < hc")
        print("  • S1: h > hc，壅水，水深↓")
        print("  • S2: h₀ < h < hc，降水，水深↑")
        print("  • S3: h < h₀，急流，水深↑")
        print("  ")
        print("  【C型（临界坡）】h₀ = hc")
        print("  • C1: h > hc，壅水，水深↓")
        print("  • C3: h < hc，急流，水深↑")
        print("  ")
        print("  【H型（平坡）】i = 0")
        print("  • H2: h > hc，水深↑")
        print("  • H3: h < hc，水深↑")
        print("  ")
        print("  【A型（反坡）】i < 0")
        print("  • A2: h > hc，水深↑")
        print("  • A3: h < hc，水深↑")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【水面线判断题】")
        print("  Step 1: 计算h₀（Manning公式迭代）")
        print("  Step 2: 计算hc（临界水深公式）")
        print("  Step 3: 比较h₀与hc，确定渠道类型")
        print("  Step 4: 确定水深所在分区")
        print("  Step 5: 查表确定水面线类型")
        print("  Step 6: 判断水深升降趋势")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：把h₀当成已知量，忘记计算")
        print("  ❌ 错误2：渠道类型判断错误（h₀与hc比较）")
        print("  ❌ 错误3：水深分区搞混")
        print("  ❌ 错误4：水面线类型记错")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：12种水面线要制表背熟！")
        print("  ✓ 技巧2：先判断渠道类型(M/S/C/H/A)")
        print("  ✓ 技巧3：再确定水深分区(1/2/3)")
        print("  ✓ 技巧4：画草图辅助判断")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能计算正常水深h₀")
        print("  □ 能判断渠道类型")
        print("  □ 能熟记12种水面线")
        print("  □ 能判断水深升降趋势")
        
        print("\n📅 明日预告：Day 13 - 堰流与闸孔出流")
        print("  预习内容：薄壁堰、实用堰、闸孔出流")
        
        print("\n💪 今日格言：")
        print("  「12种水面线=考研10分！制表背熟，稳拿高分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 12: 明渠非均匀流（水面线）")
    print("="*60)
    print("\n⏰ 学习时间：3小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（45分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（45分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day12 = Day12GVF()
    
    # 例题1：水面线类型判断
    result1 = day12.example_1_water_profile_classification()
    
    # 每日总结
    day12.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 12 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成1道例题")
    print(f"  ✓ 掌握水面线微分方程")
    print(f"  ✓ 熟记12种水面线类型")
    print(f"  ✓ 理解水深变化规律")
    print(f"  ✓ 生成5张图表")
    
    print(f"\n明日继续：Day 13 - 堰流与闸孔出流")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
