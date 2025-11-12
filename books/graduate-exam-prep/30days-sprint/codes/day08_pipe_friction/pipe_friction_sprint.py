#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 8: 管道阻力
Sprint Day 8: Pipe Friction and Head Loss

⏰ 学习时间：2.5小时
📚 核心考点：
  1. 沿程阻力损失：hf = λ(L/d)(v²/2g)
  2. 达西公式（Darcy-Weisbach）
  3. 雷诺数：Re = vd/ν
  4. 层流：λ = 64/Re
  5. 紊流：λ = f(Re, Δ/d)
  6. 局部阻力损失：hj = ζ(v²/2g)

🎯 学习目标：
  - 掌握沿程阻力损失公式
  - 理解雷诺数与流态判别
  - 熟练计算摩阻系数λ
  - 区分层流与紊流

💪 今日格言：管道阻力是管流核心！掌握λ=拿到20分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
import matplotlib.patches as mpatches

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day8PipeFriction:
    """
    Day 8：管道阻力
    
    包含2个核心例题：
    1. 基础题：层流管道阻力损失
    2. 强化题：紊流管道阻力损失
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000  # 水密度 (kg/m³)
        self.nu = 1.0e-6  # 运动粘度 (m²/s, 20℃水)
        
        # 临界雷诺数
        self.Re_critical_lower = 2000  # 下临界
        self.Re_critical_upper = 4000  # 上临界
        
    def calculate_reynolds(self, v, d):
        """计算雷诺数"""
        Re = v * d / self.nu
        return Re
    
    def calculate_lambda_laminar(self, Re):
        """计算层流摩阻系数"""
        return 64.0 / Re
    
    def calculate_lambda_turbulent_smooth(self, Re):
        """计算紊流光滑管摩阻系数（布拉修斯公式）"""
        # 适用于Re < 10^5
        return 0.3164 / (Re**0.25)
    
    def calculate_lambda_turbulent_rough(self, Re, relative_roughness):
        """计算紊流粗糙管摩阻系数（尼古拉兹公式的近似）"""
        # Colebrook-White公式的显式近似
        # 1/√λ = -2log(Δ/(3.7d) + 2.51/(Re√λ))
        # 使用Swamee-Jain显式近似
        term1 = relative_roughness / 3.7
        term2 = 5.74 / (Re**0.9)
        lambda_turb = 0.25 / (np.log10(term1 + term2))**2
        return lambda_turb
    
    def calculate_head_loss(self, lambda_val, L, d, v):
        """计算沿程阻力损失"""
        hf = lambda_val * (L / d) * (v**2 / (2 * self.g))
        return hf
    
    def example_1_laminar_flow(self):
        """
        例题1：层流管道阻力损失（基础题）⭐⭐⭐⭐⭐
        
        题目：圆形管道，直径d=0.02m，长度L=10m
              水流速度v=0.05m/s，运动粘度ν=1.0×10⁻⁶m²/s
        求：(1) 雷诺数Re
            (2) 判别流态
            (3) 摩阻系数λ
            (4) 沿程阻力损失hf
            (5) 压强降落Δp
        
        考点：雷诺数，层流摩阻系数，达西公式
        难度：基础（必考！）
        时间：15分钟
        分值：12分
        """
        print("\n" + "="*60)
        print("例题1：层流管道阻力损失（基础题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d = 0.02     # 管道直径 (m)
        L = 10.0     # 管道长度 (m)
        v = 0.05     # 流速 (m/s)
        nu = self.nu # 运动粘度 (m²/s)
        
        print(f"\n已知条件：")
        print(f"  管道直径 d = {d} m")
        print(f"  管道长度 L = {L} m")
        print(f"  流速 v = {v} m/s")
        print(f"  运动粘度 ν = {nu:.2e} m²/s")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 雷诺数
        print(f"\n(1) 计算雷诺数Re：")
        print(f"    Re = vd/ν")
        
        Re = self.calculate_reynolds(v, d)
        
        print(f"       = ({v} × {d}) / {nu:.2e}")
        print(f"       = {Re:.0f} ✓")
        
        # (2) 流态判别
        print(f"\n(2) 判别流态：")
        print(f"    Re = {Re:.0f}")
        print(f"    ")
        print(f"    判别标准：")
        print(f"    Re < 2000      → 层流")
        print(f"    2000 < Re < 4000 → 过渡流")
        print(f"    Re > 4000      → 紊流")
        print(f"    ")
        
        if Re < self.Re_critical_lower:
            flow_regime = "层流"
            print(f"    ∵ Re = {Re:.0f} < 2000")
            print(f"    ∴ 流态为：层流 ✓")
        elif Re < self.Re_critical_upper:
            flow_regime = "过渡流"
            print(f"    ∵ 2000 < Re = {Re:.0f} < 4000")
            print(f"    ∴ 流态为：过渡流")
        else:
            flow_regime = "紊流"
            print(f"    ∵ Re = {Re:.0f} > 4000")
            print(f"    ∴ 流态为：紊流")
        
        # (3) 摩阻系数
        print(f"\n(3) 计算摩阻系数λ：")
        
        if Re < self.Re_critical_lower:
            print(f"    层流：λ = 64/Re")
            lambda_val = self.calculate_lambda_laminar(Re)
            print(f"         = 64/{Re:.0f}")
            print(f"         = {lambda_val:.4f} ✓")
        else:
            print(f"    紊流：使用布拉修斯公式")
            lambda_val = self.calculate_lambda_turbulent_smooth(Re)
            print(f"    λ = 0.3164/Re^0.25")
            print(f"      = {lambda_val:.4f} ✓")
        
        # (4) 沿程阻力损失
        print(f"\n(4) 计算沿程阻力损失hf（达西公式）：")
        print(f"    hf = λ × (L/d) × (v²/2g)")
        
        hf = self.calculate_head_loss(lambda_val, L, d, v)
        
        print(f"       = {lambda_val:.4f} × ({L}/{d}) × ({v}²/(2×{self.g}))")
        print(f"       = {lambda_val:.4f} × {L/d:.0f} × {v**2/(2*self.g):.6f}")
        print(f"       = {hf:.6f} m ✓")
        print(f"       = {hf*1000:.3f} mm")
        
        # (5) 压强降落
        print(f"\n(5) 计算压强降落Δp：")
        print(f"    Δp = ρg × hf")
        
        delta_p = self.rho * self.g * hf
        
        print(f"       = {self.rho} × {self.g} × {hf:.6f}")
        print(f"       = {delta_p:.2f} Pa ✓")
        print(f"       = {delta_p/1000:.4f} kPa")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：管道示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 管道
        pipe_length = 4
        pipe_width = 0.3
        ax1.add_patch(Rectangle((0, -pipe_width/2), pipe_length, pipe_width,
                                fill=True, facecolor='lightgray',
                                edgecolor='black', linewidth=2))
        
        # 流速箭头
        num_arrows = 5
        for i in range(num_arrows):
            x_pos = 0.5 + i * 0.7
            ax1.arrow(x_pos, 0, 0.3, 0, head_width=0.08, head_length=0.1,
                     fc='blue', ec='blue', linewidth=2)
        
        ax1.text(pipe_length/2, pipe_width/2+0.2, f'v={v}m/s', 
                ha='center', fontsize=12, color='blue', fontweight='bold')
        
        # 标注
        ax1.plot([0, 0], [-pipe_width/2-0.1, pipe_width/2+0.1], 'k-', linewidth=2)
        ax1.plot([pipe_length, pipe_length], [-pipe_width/2-0.1, pipe_width/2+0.1], 
                'k-', linewidth=2)
        ax1.annotate('', xy=(pipe_length, -pipe_width/2-0.15), 
                    xytext=(0, -pipe_width/2-0.15),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(pipe_length/2, -pipe_width/2-0.25, f'L={L}m',
                ha='center', fontsize=11, color='red', fontweight='bold')
        
        # 直径标注
        ax1.plot([-0.2, -0.2], [-pipe_width/2, pipe_width/2], 'g-', linewidth=2)
        ax1.text(-0.35, 0, f'd={d}m', fontsize=10, color='green',
                rotation=90, va='center', fontweight='bold')
        
        # 能量线
        h1 = 0.5
        h2 = h1 - hf
        ax1.plot([0, pipe_length], [h1, h2], 'r--', linewidth=2, label='能量线（EL）')
        ax1.text(pipe_length/2, (h1+h2)/2+0.1, f'hf={hf*1000:.2f}mm',
                ha='center', fontsize=10, color='red',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.set_xlabel('管道长度方向 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 8 例题1：层流管道阻力示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.6, 4.5])
        ax1.set_ylim([-0.6, 1.0])
        ax1.set_aspect('equal')
        
        # 子图2：雷诺数与流态
        ax2 = plt.subplot(2, 2, 2)
        
        # 雷诺数范围
        Re_range = [0, 2000, 4000, 10000]
        flow_regimes = ['层流', '过渡', '紊流']
        colors_regime = ['#90EE90', '#FFD700', '#FF6B6B']
        
        for i in range(len(flow_regimes)):
            ax2.barh(0, Re_range[i+1]-Re_range[i], left=Re_range[i],
                    height=0.5, color=colors_regime[i], 
                    edgecolor='black', linewidth=2,
                    label=flow_regimes[i])
        
        # 标注本题Re
        ax2.plot([Re, Re], [-0.3, 0.3], 'b-', linewidth=4)
        ax2.plot(Re, 0.4, 'bv', markersize=15)
        ax2.text(Re, 0.6, f'Re={Re:.0f}\n(本题)', 
                ha='center', fontsize=11, color='blue',
                fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        # 临界雷诺数标注
        ax2.axvline(x=2000, color='red', linestyle='--', linewidth=2)
        ax2.text(2000, -0.5, 'Re=2000\n下临界', ha='center',
                fontsize=9, color='red')
        ax2.axvline(x=4000, color='red', linestyle='--', linewidth=2)
        ax2.text(4000, -0.5, 'Re=4000\n上临界', ha='center',
                fontsize=9, color='red')
        
        ax2.set_xlabel('雷诺数 Re', fontsize=12)
        ax2.set_title('雷诺数与流态判别', fontsize=13, fontweight='bold')
        ax2.set_xlim([0, 10000])
        ax2.set_ylim([-0.7, 0.8])
        ax2.set_yticks([])
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 子图3：λ-Re关系（层流区）
        ax3 = plt.subplot(2, 2, 3)
        
        # 层流λ曲线
        Re_laminar = np.linspace(100, 2000, 100)
        lambda_laminar = 64 / Re_laminar
        
        ax3.plot(Re_laminar, lambda_laminar, 'g-', linewidth=3, 
                label='λ=64/Re (层流)')
        
        # 本题的点
        ax3.plot(Re, lambda_val, 'ro', markersize=12, label='本题')
        ax3.text(Re+100, lambda_val+0.002, 
                f'Re={Re:.0f}\nλ={lambda_val:.4f}',
                fontsize=10, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax3.set_xlabel('雷诺数 Re', fontsize=12)
        ax3.set_ylabel('摩阻系数 λ', fontsize=12)
        ax3.set_title('摩阻系数λ与雷诺数Re关系（层流）', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([0, 2200])
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          • 管道直径 d = {d} m
          • 管道长度 L = {L} m
          • 流速 v = {v} m/s
          • 运动粘度 ν = {nu:.2e} m²/s
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 雷诺数：
            Re = vd/ν = {Re:.0f} ✓
        
        (2) 流态判别：
            Re = {Re:.0f} < 2000
            流态：{flow_regime} ✓
        
        (3) 摩阻系数：
            λ = 64/Re = {lambda_val:.4f} ✓
        
        (4) 沿程阻力损失：
            hf = λ(L/d)(v²/2g)
               = {hf:.6f} m
               = {hf*1000:.3f} mm ✓
        
        (5) 压强降落：
            Δp = ρghf = {delta_p:.2f} Pa
               = {delta_p/1000:.4f} kPa ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键公式：
          • 雷诺数：Re = vd/ν
          • 层流：λ = 64/Re
          • 达西公式：hf = λ(L/d)(v²/2g)
          • 压降：Δp = ρghf
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day08_pipe_friction/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（12分评分标准）：")
        print("="*60)
        print("✓ (1) 写出雷诺数公式Re=vd/ν (2分) ⭐")
        print("✓ (2) 计算雷诺数 (1分)")
        print("✓ (3) 判别流态（Re<2000为层流） (2分)")
        print("✓ (4) 应用层流公式λ=64/Re (2分) ⭐")
        print("✓ (5) 写出达西公式hf=λ(L/d)(v²/2g) (2分) ⭐")
        print("✓ (6) 计算沿程阻力损失 (2分)")
        print("✓ (7) 计算压强降落Δp=ρghf (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 雷诺数公式：Re=vd/ν，不要忘记除以ν！")
        print("  ⚠️ 流态判别：Re<2000层流，Re>4000紊流")
        print("  ⚠️ 层流λ：λ=64/Re，64这个常数要记住！")
        print("  ⚠️ 达西公式：hf=λ(L/d)(v²/2g)，括号不要漏")
        
        return {'Re': Re, 'lambda': lambda_val, 'hf': hf, 'delta_p': delta_p}
    
    def example_2_turbulent_flow(self):
        """
        例题2：紊流管道阻力损失（强化题）⭐⭐⭐⭐⭐
        
        题目：圆形管道，直径d=0.10m，长度L=100m
              流量Q=0.02m³/s，绝对粗糙度Δ=0.0001m
              运动粘度ν=1.0×10⁻⁶m²/s
        求：(1) 平均流速v
            (2) 雷诺数Re
            (3) 判别流态
            (4) 相对粗糙度Δ/d
            (5) 摩阻系数λ
            (6) 沿程阻力损失hf
        
        考点：紊流摩阻系数，粗糙度影响
        难度：强化（必考！）
        时间：20分钟
        分值：18分
        """
        print("\n" + "="*60)
        print("例题2：紊流管道阻力损失（强化题）⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        d = 0.10        # 管道直径 (m)
        L = 100.0       # 管道长度 (m)
        Q = 0.02        # 流量 (m³/s)
        Delta = 0.0001  # 绝对粗糙度 (m)
        nu = self.nu    # 运动粘度 (m²/s)
        
        print(f"\n已知条件：")
        print(f"  管道直径 d = {d} m")
        print(f"  管道长度 L = {L} m")
        print(f"  流量 Q = {Q} m³/s")
        print(f"  绝对粗糙度 Δ = {Delta} m = {Delta*1000} mm")
        print(f"  运动粘度 ν = {nu:.2e} m²/s")
        
        # 计算过程
        print(f"\n解题步骤：")
        
        # (1) 平均流速
        print(f"\n(1) 计算平均流速v：")
        print(f"    断面积 A = π(d/2)²")
        
        A = np.pi * (d/2)**2
        
        print(f"            = π×({d}/2)²")
        print(f"            = {A:.6f} m²")
        print(f"    ")
        print(f"    流速 v = Q/A")
        
        v = Q / A
        
        print(f"           = {Q}/{A:.6f}")
        print(f"           = {v:.3f} m/s ✓")
        
        # (2) 雷诺数
        print(f"\n(2) 计算雷诺数Re：")
        print(f"    Re = vd/ν")
        
        Re = self.calculate_reynolds(v, d)
        
        print(f"       = ({v:.3f} × {d}) / {nu:.2e}")
        print(f"       = {Re:.0f} ✓")
        
        # (3) 流态判别
        print(f"\n(3) 判别流态：")
        print(f"    Re = {Re:.0f}")
        print(f"    ")
        print(f"    ∵ Re = {Re:.0f} > 4000")
        print(f"    ∴ 流态为：紊流 ✓")
        
        flow_regime = "紊流"
        
        # (4) 相对粗糙度
        print(f"\n(4) 计算相对粗糙度Δ/d：")
        
        relative_roughness = Delta / d
        
        print(f"    Δ/d = {Delta}/{d}")
        print(f"        = {relative_roughness:.6f}")
        print(f"        = {relative_roughness:.2e} ✓")
        print(f"    ")
        print(f"    说明：相对粗糙度表示管壁粗糙程度")
        
        # (5) 摩阻系数
        print(f"\n(5) 计算摩阻系数λ（紊流）：")
        print(f"    ")
        print(f"    方法1：布拉修斯公式（光滑管，Re<10⁵）")
        
        lambda_smooth = self.calculate_lambda_turbulent_smooth(Re)
        
        print(f"    λ = 0.3164/Re^0.25")
        print(f"      = 0.3164/{Re:.0f}^0.25")
        print(f"      = {lambda_smooth:.6f}")
        print(f"    ")
        print(f"    方法2：粗糙管公式（考虑粗糙度）")
        print(f"    使用Swamee-Jain显式近似：")
        
        lambda_val = self.calculate_lambda_turbulent_rough(Re, relative_roughness)
        
        print(f"    λ = 0.25/[log₁₀(Δ/(3.7d) + 5.74/Re^0.9)]²")
        print(f"      = {lambda_val:.6f} ✓")
        print(f"    ")
        print(f"    说明：粗糙管λ值稍大于光滑管")
        
        # (6) 沿程阻力损失
        print(f"\n(6) 计算沿程阻力损失hf（达西公式）：")
        print(f"    hf = λ × (L/d) × (v²/2g)")
        
        hf = self.calculate_head_loss(lambda_val, L, d, v)
        
        print(f"       = {lambda_val:.6f} × ({L}/{d}) × ({v:.3f}²/(2×{self.g}))")
        print(f"       = {lambda_val:.6f} × {L/d:.0f} × {v**2/(2*self.g):.6f}")
        print(f"       = {hf:.3f} m ✓")
        
        # 压强降落
        delta_p = self.rho * self.g * hf
        print(f"    ")
        print(f"    压强降落：")
        print(f"    Δp = ρghf = {self.rho} × {self.g} × {hf:.3f}")
        print(f"       = {delta_p:.0f} Pa = {delta_p/1000:.2f} kPa")
        
        # 绘图
        fig = plt.figure(figsize=(14, 10))
        
        # 子图1：紊流管道示意图
        ax1 = plt.subplot(2, 2, 1)
        
        # 管道
        pipe_length = 4
        pipe_width = 0.4
        ax1.add_patch(Rectangle((0, -pipe_width/2), pipe_length, pipe_width,
                                fill=True, facecolor='lightgray',
                                edgecolor='black', linewidth=2))
        
        # 管壁粗糙度示意（锯齿状）
        roughness_points_top = []
        roughness_points_bottom = []
        x_rough = np.linspace(0, pipe_length, 20)
        for i, x in enumerate(x_rough):
            y_offset = 0.015 * (1 if i % 2 == 0 else -1)
            roughness_points_top.append([x, pipe_width/2 + y_offset])
            roughness_points_bottom.append([x, -pipe_width/2 - y_offset])
        
        ax1.plot([p[0] for p in roughness_points_top], 
                [p[1] for p in roughness_points_top], 
                'r-', linewidth=1.5, alpha=0.7)
        ax1.plot([p[0] for p in roughness_points_bottom], 
                [p[1] for p in roughness_points_bottom], 
                'r-', linewidth=1.5, alpha=0.7)
        
        # 紊流流速分布（抛物线族表示涡旋）
        for i in range(5):
            x_center = 0.5 + i * 0.7
            # 主流
            ax1.arrow(x_center, 0, 0.25, 0, head_width=0.06, head_length=0.08,
                     fc='blue', ec='blue', linewidth=2)
            # 涡旋
            if i % 2 == 0:
                circle = Circle((x_center+0.15, 0.1), 0.05, 
                              fill=False, edgecolor='cyan', linewidth=1.5, linestyle='--')
                ax1.add_patch(circle)
        
        ax1.text(pipe_length/2, pipe_width/2+0.25, f'v={v:.2f}m/s（紊流）', 
                ha='center', fontsize=12, color='blue', fontweight='bold')
        
        # 标注
        ax1.annotate('', xy=(pipe_length, -pipe_width/2-0.2), 
                    xytext=(0, -pipe_width/2-0.2),
                    arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax1.text(pipe_length/2, -pipe_width/2-0.3, f'L={L}m',
                ha='center', fontsize=11, color='red', fontweight='bold')
        
        # 能量线
        h1 = 0.6
        h2 = h1 - hf/10  # 缩放显示
        ax1.plot([0, pipe_length], [h1, h2], 'r--', linewidth=2, label='能量线（EL）')
        ax1.text(pipe_length/2, (h1+h2)/2+0.05, f'hf={hf:.2f}m',
                ha='center', fontsize=10, color='red',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        ax1.set_xlabel('管道长度方向 (m)', fontsize=12)
        ax1.set_ylabel('高度 (m)', fontsize=12)
        ax1.set_title('Day 8 例题2：紊流管道阻力示意图', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([-0.3, 4.5])
        ax1.set_ylim([-0.6, 1.0])
        
        # 子图2：λ-Re关系（全范围）
        ax2 = plt.subplot(2, 2, 2)
        
        # Re范围
        Re_range = np.logspace(2, 6, 200)
        
        # 层流
        Re_lam = Re_range[Re_range < 2000]
        lambda_lam = 64 / Re_lam
        ax2.loglog(Re_lam, lambda_lam, 'g-', linewidth=3, label='层流 λ=64/Re')
        
        # 紊流光滑管
        Re_turb_smooth = Re_range[(Re_range >= 4000) & (Re_range < 1e5)]
        lambda_turb_smooth = 0.3164 / (Re_turb_smooth**0.25)
        ax2.loglog(Re_turb_smooth, lambda_turb_smooth, 'b-', linewidth=3, 
                  label='紊流光滑管')
        
        # 紊流粗糙管（不同相对粗糙度）
        roughness_values = [1e-5, 1e-4, 1e-3]
        colors_rough = ['cyan', 'orange', 'red']
        for rough, color in zip(roughness_values, colors_rough):
            Re_turb_rough = Re_range[Re_range >= 4000]
            lambda_turb_rough = [self.calculate_lambda_turbulent_rough(r, rough) 
                                for r in Re_turb_rough]
            ax2.loglog(Re_turb_rough, lambda_turb_rough, 
                      color=color, linewidth=2, linestyle='--',
                      label=f'Δ/d={rough:.0e}')
        
        # 本题的点
        ax2.loglog(Re, lambda_val, 'mo', markersize=12, 
                  markeredgewidth=2, markeredgecolor='black',
                  label='本题')
        ax2.text(Re*1.2, lambda_val*1.1, 
                f'Re={Re:.0f}\nλ={lambda_val:.5f}',
                fontsize=9, color='purple', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 临界Re
        ax2.axvline(x=2000, color='gray', linestyle=':', linewidth=2)
        ax2.axvline(x=4000, color='gray', linestyle=':', linewidth=2)
        ax2.text(2000, 0.08, 'Re=2000', fontsize=8, rotation=90)
        ax2.text(4000, 0.08, 'Re=4000', fontsize=8, rotation=90)
        
        ax2.set_xlabel('雷诺数 Re', fontsize=12)
        ax2.set_ylabel('摩阻系数 λ', fontsize=12)
        ax2.set_title('Moody图：λ-Re关系', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3, which='both')
        ax2.set_xlim([100, 1e6])
        ax2.set_ylim([0.01, 0.1])
        
        # 子图3：流速与阻力关系
        ax3 = plt.subplot(2, 2, 3)
        
        # 不同流速下的阻力损失
        v_range = np.linspace(0.5, 4, 20)
        Re_range_v = [self.calculate_reynolds(v_i, d) for v_i in v_range]
        hf_range = []
        
        for v_i, Re_i in zip(v_range, Re_range_v):
            if Re_i < 2000:
                lambda_i = 64 / Re_i
            else:
                lambda_i = self.calculate_lambda_turbulent_rough(Re_i, relative_roughness)
            hf_i = lambda_i * (L / d) * (v_i**2 / (2 * self.g))
            hf_range.append(hf_i)
        
        ax3.plot(v_range, hf_range, 'b-', linewidth=3, label='hf-v关系')
        ax3.plot(v, hf, 'ro', markersize=12, label='本题')
        ax3.text(v+0.2, hf+1, f'v={v:.2f}m/s\nhf={hf:.2f}m',
                fontsize=10, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 二次曲线参考
        ax3.plot(v_range, 2*v_range**2, 'g--', linewidth=2, alpha=0.5,
                label='∝v²（参考）')
        
        ax3.set_xlabel('流速 v (m/s)', fontsize=12)
        ax3.set_ylabel('沿程阻力损失 hf (m)', fontsize=12)
        ax3.set_title('流速与阻力损失关系', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 子图4：计算结果汇总
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        summary_text = f"""
        【计算结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        已知参数：
          • 管道直径 d = {d} m
          • 管道长度 L = {L} m
          • 流量 Q = {Q} m³/s
          • 绝对粗糙度 Δ = {Delta*1000} mm
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        计算结果：
        
        (1) 平均流速：
            A = {A:.6f} m²
            v = Q/A = {v:.3f} m/s ✓
        
        (2) 雷诺数：
            Re = vd/ν = {Re:.0f} ✓
        
        (3) 流态：
            Re > 4000 → 紊流 ✓
        
        (4) 相对粗糙度：
            Δ/d = {relative_roughness:.6f} ✓
        
        (5) 摩阻系数：
            λ = {lambda_val:.6f} ✓
            (考虑粗糙度影响)
        
        (6) 沿程阻力损失：
            hf = λ(L/d)(v²/2g)
               = {hf:.3f} m ✓
            Δp = {delta_p/1000:.2f} kPa
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        关键点：
          • 紊流Re>4000
          • λ考虑粗糙度影响
          • hf ∝ v²（二次关系）
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax4.text(0.1, 0.95, summary_text, fontsize=8.5, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day08_pipe_friction/example_2.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_2.png")
        
        # 答题要点
        print("\n" + "="*60)
        print("📝 答题要点（18分评分标准）：")
        print("="*60)
        print("✓ (1) 计算断面积A (1分)")
        print("✓ (2) 计算平均流速v=Q/A (1分)")
        print("✓ (3) 计算雷诺数Re=vd/ν (2分)")
        print("✓ (4) 判别紊流（Re>4000） (2分)")
        print("✓ (5) 计算相对粗糙度Δ/d (2分)")
        print("✓ (6) 应用紊流λ公式 (4分) ⭐⭐")
        print("✓ (7) 应用达西公式hf=λ(L/d)(v²/2g) (3分) ⭐")
        print("✓ (8) 计算沿程阻力损失 (2分)")
        print("✓ (9) 单位正确 (1分)")
        
        print("\n💡 易错点：")
        print("  ⚠️ 紊流λ计算：不能用λ=64/Re！")
        print("  ⚠️ 相对粗糙度：Δ/d，不是绝对粗糙度Δ")
        print("  ⚠️ 达西公式：hf∝v²，流速影响很大")
        print("  ⚠️ Re判别：Re>4000紊流，Re<2000层流")
        
        return {'Re': Re, 'lambda': lambda_val, 'hf': hf, 'v': v}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 8 知识点总结")
        print("="*60)
        
        print("\n✅ 核心公式（必背！）：")
        print("  1. 雷诺数：")
        print("     Re = vd/ν")
        print("     ")
        print("  2. 流态判别：")
        print("     Re < 2000      → 层流")
        print("     2000 < Re < 4000 → 过渡流")
        print("     Re > 4000      → 紊流")
        print("     ")
        print("  3. 层流摩阻系数：")
        print("     λ = 64/Re")
        print("     ")
        print("  4. 紊流摩阻系数（光滑管）：")
        print("     λ = 0.3164/Re^0.25  (Re < 10⁵)")
        print("     ")
        print("  5. 达西公式（沿程阻力）：")
        print("     hf = λ × (L/d) × (v²/2g)")
        print("     ")
        print("  6. 压强降落：")
        print("     Δp = ρg × hf")
        
        print("\n✅ 流态对比表：")
        print("  ┌────────┬──────────┬──────────────┐")
        print("  │  流态  │ Re范围   │  λ计算公式    │")
        print("  ├────────┼──────────┼──────────────┤")
        print("  │  层流  │ Re<2000  │ λ=64/Re      │")
        print("  │ 过渡流 │2000~4000 │ 不稳定       │")
        print("  │  紊流  │ Re>4000  │ λ=0.3164/Re^0.25│")
        print("  └────────┴──────────┴──────────────┘")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  【管道阻力计算】")
        print("  Step 1: 计算雷诺数Re=vd/ν")
        print("  Step 2: 判别流态（层流/紊流）")
        print("  Step 3: 选择λ公式")
        print("         层流：λ=64/Re")
        print("         紊流：λ=0.3164/Re^0.25或查表")
        print("  Step 4: 应用达西公式hf=λ(L/d)(v²/2g)")
        print("  Step 5: 计算压强降落Δp=ρghf")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：雷诺数公式忘记除以ν")
        print("  ❌ 错误2：层流用紊流公式，紊流用层流公式")
        print("  ❌ 错误3：达西公式括号搞混：λ(L/d)(v²/2g)")
        print("  ❌ 错误4：流速的二次方关系忽略")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：先算Re，判别流态最重要")
        print("  ✓ 技巧2：层流记住「64」，紊流记住「0.3164」")
        print("  ✓ 技巧3：达西公式记住「λ长径速平方」")
        print("  ✓ 技巧4：hf∝v²，流速影响最大")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能熟记雷诺数公式")
        print("  □ 能准确判别流态")
        print("  □ 掌握层流和紊流λ公式")
        print("  □ 熟练应用达西公式")
        
        print("\n📅 明日预告：Day 9 - 有压管流计算")
        print("  预习内容：并联管道，串联管道")
        
        print("\n💪 今日格言：")
        print("  「管道阻力是管流核心！掌握Re和λ=拿到20分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 8: 管道阻力")
    print("="*60)
    print("\n⏰ 学习时间：2.5小时")
    print("📚 今日任务：")
    print("  ✓ 理论复习（30分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day8 = Day8PipeFriction()
    
    # 例题1：层流
    result1 = day8.example_1_laminar_flow()
    
    # 例题2：紊流
    result2 = day8.example_2_turbulent_flow()
    
    # 每日总结
    day8.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 8 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成2道例题")
    print(f"  ✓ 掌握雷诺数计算")
    print(f"  ✓ 理解流态判别")
    print(f"  ✓ 掌握摩阻系数λ")
    print(f"  ✓ 熟练达西公式")
    print(f"  ✓ 生成8张图表")
    
    print(f"\n明日继续：Day 9 - 有压管流计算")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
