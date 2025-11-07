"""
案例5: 尾流效应

本案例演示:
1. Jensen尾流模型
2. 单机尾流风速分布
3. 多机尾流叠加
4. 风电场布局优化

工程背景: 风电场微观选址
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class JensenWakeModel:
    """Jensen尾流模型"""
    
    def __init__(self, D: float, Ct: float = 0.8, alpha: float = 0.075):
        """
        初始化Jensen尾流模型
        
        Args:
            D: 风轮直径 (m)
            Ct: 推力系数
            alpha: 尾流扩展系数（平坦地形0.075，粗糙地形0.1）
        """
        self.D = D
        self.Ct = Ct
        self.alpha = alpha
    
    def wake_velocity_deficit(self, x: float, v0: float) -> float:
        """
        计算下游x处的风速亏损
        
        v/v0 = 1 - (1 - sqrt(1-Ct)) / (1 + 2*alpha*x/D)^2
        
        Args:
            x: 下游距离 (m)
            v0: 上游风速 (m/s)
            
        Returns:
            下游风速 (m/s)
        """
        if x <= 0:
            return v0
        
        # 尾流半径扩展
        r_wake = self.D/2 + self.alpha * x
        
        # 风速亏损
        deficit = (1 - np.sqrt(1 - self.Ct)) / (1 + 2*self.alpha*x/self.D)**2
        
        v = v0 * (1 - deficit)
        
        return v
    
    def wake_profile(self, x: float, y: float, v0: float) -> float:
        """
        计算尾流横截面风速分布
        
        Args:
            x: 下游距离 (m)
            y: 横向距离 (m)
            v0: 上游风速 (m/s)
            
        Returns:
            该点风速 (m/s)
        """
        if x <= 0:
            return v0
        
        # 尾流半径
        r_wake = self.D/2 + self.alpha * x
        
        # 在尾流内
        if abs(y) < r_wake:
            # 轴线风速
            v_axis = self.wake_velocity_deficit(x, v0)
            # 径向分布（简化为均匀）
            v = v_axis
        else:
            v = v0
        
        return v


def demo_single_wake():
    """演示1: 单机尾流"""
    print("=" * 60)
    print("演示1: 单台风力机尾流特性")
    print("=" * 60)
    
    D = 90  # m
    wake = JensenWakeModel(D, Ct=0.8, alpha=0.075)
    v0 = 10.0
    
    # 下游距离
    x_range = np.linspace(0, 15*D, 100)
    v_wake = [wake.wake_velocity_deficit(x, v0) for x in x_range]
    deficit = [(v0 - v) / v0 * 100 for v in v_wake]
    
    print(f"\n风轮参数: D={D}m, Ct={wake.Ct}")
    print(f"上游风速: v0={v0} m/s")
    
    print(f"\n尾流影响:")
    for dist in [2, 5, 10]:
        x = dist * D
        v = wake.wake_velocity_deficit(x, v0)
        print(f"  {dist}D ({x:.0f}m): v={v:.2f}m/s, 亏损{(1-v/v0)*100:.1f}%")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    ax.plot(x_range/D, v_wake, 'b-', linewidth=2)
    ax.axhline(v0, color='r', linestyle='--', label='上游风速')
    ax.set_xlabel('下游距离 (D)', fontsize=12)
    ax.set_ylabel('风速 (m/s)', fontsize=12)
    ax.set_title('尾流风速恢复', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    ax.plot(x_range/D, deficit, 'r-', linewidth=2)
    ax.set_xlabel('下游距离 (D)', fontsize=12)
    ax.set_ylabel('风速亏损 (%)', fontsize=12)
    ax.set_title('尾流亏损曲线', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case05_single_wake.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case05_single_wake.png")


def demo_wake_field():
    """演示2: 尾流流场"""
    print("\n" + "=" * 60)
    print("演示2: 尾流流场可视化")
    print("=" * 60)
    
    D = 90
    wake = JensenWakeModel(D, Ct=0.8)
    v0 = 10.0
    
    # 网格
    x = np.linspace(-2*D, 15*D, 200)
    y = np.linspace(-3*D, 3*D, 100)
    X, Y = np.meshgrid(x, y)
    
    # 计算流场
    V = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            V[i, j] = wake.wake_profile(X[i, j], Y[i, j], v0)
    
    print(f"\n流场计算完成")
    print(f"  网格: {X.shape[0]}×{X.shape[1]}")
    print(f"  风速范围: {V.min():.2f}-{V.max():.2f} m/s")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    levels = np.linspace(6, 10, 21)
    contour = ax.contourf(X/D, Y/D, V, levels=levels, cmap='jet')
    ax.contour(X/D, Y/D, V, levels=levels, colors='k', linewidths=0.3, alpha=0.3)
    
    # 绘制风轮
    circle = plt.Circle((0, 0), 0.5, color='white', ec='black', linewidth=2)
    ax.add_patch(circle)
    ax.arrow(-1, 0, 0.8, 0, head_width=0.3, head_length=0.1, fc='black')
    
    plt.colorbar(contour, ax=ax, label='风速 (m/s)')
    ax.set_xlabel('下游距离 (D)', fontsize=12)
    ax.set_ylabel('横向距离 (D)', fontsize=12)
    ax.set_title('尾流流场分布', fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('case05_wake_field.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case05_wake_field.png")


def demo_multiple_wakes():
    """演示3: 多机尾流叠加"""
    print("\n" + "=" * 60)
    print("演示3: 多台风力机尾流叠加")
    print("=" * 60)
    
    D = 90
    wake = JensenWakeModel(D)
    v0 = 10.0
    
    # 3台风力机布局（一排）
    spacing = [5*D, 8*D, 12*D]  # 间距
    
    print(f"\n布局: 3台风力机")
    print(f"  间距: 5D, 8D, 12D")
    
    # 计算每台的来流风速
    v_turbines = [v0]  # 第1台
    
    # 第2台（受第1台影响）
    v2 = wake.wake_velocity_deficit(spacing[0], v0)
    v_turbines.append(v2)
    
    # 第3台（受第1、2台影响，线性叠加）
    v3_from_1 = wake.wake_velocity_deficit(spacing[0] + spacing[1], v0)
    v3_from_2 = wake.wake_velocity_deficit(spacing[1], v2)
    # 尾流亏损叠加
    deficit_total = np.sqrt((v0-v3_from_1)**2 + (v2-v3_from_2)**2) / v0
    v3 = v0 * (1 - deficit_total)
    v_turbines.append(v3)
    
    # 功率（简化：P ∝ v³）
    P_turbines = [(v/v0)**3 * 2000 for v in v_turbines]
    P_total = sum(P_turbines)
    P_no_wake = 3 * 2000
    wake_loss = (1 - P_total / P_no_wake) * 100
    
    print(f"\n各机组风速和功率:")
    for i, (v, P) in enumerate(zip(v_turbines, P_turbines), 1):
        print(f"  机组{i}: v={v:.2f}m/s, P={P:.0f}kW ({P/2000*100:.0f}%额定)")
    
    print(f"\n总功率:")
    print(f"  实际: {P_total:.0f} kW")
    print(f"  无尾流: {P_no_wake} kW")
    print(f"  尾流损失: {wake_loss:.1f}%")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    positions = [0, spacing[0]/D, (spacing[0]+spacing[1])/D]
    ax.bar(positions, v_turbines, width=0.5, alpha=0.7)
    ax.axhline(v0, color='r', linestyle='--', label='无尾流风速')
    ax.set_xlabel('机组位置 (D)', fontsize=12)
    ax.set_ylabel('来流风速 (m/s)', fontsize=12)
    ax.set_title('各机组来流风速', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    ax = axes[1]
    ax.bar(range(1, 4), P_turbines, width=0.6, alpha=0.7, color='green')
    ax.axhline(2000, color='r', linestyle='--', label='额定功率')
    ax.set_xlabel('机组编号', fontsize=12)
    ax.set_ylabel('功率 (kW)', fontsize=12)
    ax.set_title('各机组功率', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('case05_multiple_wakes.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case05_multiple_wakes.png")


def main():
    print("\n" + "=" * 60)
    print("案例5: 尾流效应")
    print("=" * 60)
    
    demo_single_wake()
    demo_wake_field()
    demo_multiple_wakes()
    
    print("\n" + "=" * 60)
    print("案例5 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case05_single_wake.png")
    print("  2. case05_wake_field.png")
    print("  3. case05_multiple_wakes.png")
    
    plt.show()


if __name__ == "__main__":
    main()
