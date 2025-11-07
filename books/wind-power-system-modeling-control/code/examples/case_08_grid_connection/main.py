"""
案例8: 并网动态特性

本案例演示:
1. 电网电压跌落响应
2. 频率波动响应
3. 有功/无功功率动态
4. 低电压穿越（LVRT）

工程背景: 风电并网要求
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_voltage_dip():
    """演示1: 电压跌落响应"""
    print("=" * 60)
    print("演示1: 电网电压跌落响应")
    print("=" * 60)
    
    # 仿真参数
    t = np.linspace(0, 5, 1000)
    dt = t[1] - t[0]
    
    # 电压跌落：1s跌落到50%，持续1s，然后恢复
    V_grid = np.ones_like(t)
    V_grid[(t >= 1) & (t < 2)] = 0.5
    
    # 简化功率响应（实际需要详细的发电机和变流器模型）
    P = np.ones_like(t) * 1.0  # pu
    Q = np.zeros_like(t)
    
    # 电压跌落时功率响应
    for i in range(len(t)):
        if 1 <= t[i] < 2:
            # 有功功率下降
            P[i] = V_grid[i]**2
            # 无功功率支撑（LVRT要求）
            Q[i] = 0.3
        elif 2 <= t[i] < 3:
            # 恢复阶段
            P[i] = 0.5 + (t[i] - 2) * 0.5
            Q[i] = 0.3 * (1 - (t[i] - 2))
    
    print(f"\n电压跌落场景:")
    print(f"  跌落时间: 1.0s")
    print(f"  跌落幅度: 50%")
    print(f"  持续时间: 1.0s")
    print(f"  恢复时间: ~1.0s")
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # 电压
    ax = axes[0]
    ax.plot(t, V_grid, 'b-', linewidth=2)
    ax.axhline(0.9, color='g', linestyle='--', alpha=0.5, label='正常范围')
    ax.axhline(0.5, color='r', linestyle='--', alpha=0.5, label='LVRT阈值')
    ax.fill_between(t, 0, V_grid, alpha=0.2)
    ax.set_ylabel('电网电压 (pu)', fontsize=12)
    ax.set_title('电压跌落波形', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 5)
    
    # 有功功率
    ax = axes[1]
    ax.plot(t, P, 'g-', linewidth=2)
    ax.axhline(1.0, color='r', linestyle='--', alpha=0.5)
    ax.set_ylabel('有功功率 (pu)', fontsize=12)
    ax.set_title('有功功率响应', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 5)
    
    # 无功功率
    ax = axes[2]
    ax.plot(t, Q, 'r-', linewidth=2)
    ax.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('无功功率 (pu)', fontsize=12)
    ax.set_title('无功功率支撑', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 5)
    
    plt.tight_layout()
    plt.savefig('case08_voltage_dip.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case08_voltage_dip.png")


def demo_frequency_response():
    """演示2: 频率响应"""
    print("\n" + "=" * 60)
    print("演示2: 电网频率波动响应")
    print("=" * 60)
    
    t = np.linspace(0, 10, 1000)
    
    # 频率波动：50Hz → 49.5Hz → 50Hz
    f_grid = np.ones_like(t) * 50
    f_grid[(t >= 2) & (t < 6)] = 49.5
    
    # 频率下降时增加功率（下垂特性）
    P = np.ones_like(t) * 1.0
    droop = 0.05  # 5%下垂系数
    
    for i in range(len(t)):
        df = f_grid[i] - 50
        P[i] = 1.0 - droop * df / 50  # 频率下降，功率增加
        P[i] = np.clip(P[i], 0, 1.1)
    
    print(f"\n频率响应特性:")
    print(f"  额定频率: 50 Hz")
    print(f"  频率偏差: -0.5 Hz")
    print(f"  下垂系数: {droop*100}%")
    print(f"  功率响应: {(P[(t >= 2) & (t < 6)].mean() - 1.0)*100:+.1f}%")
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 频率
    ax = axes[0]
    ax.plot(t, f_grid, 'b-', linewidth=2)
    ax.axhline(50, color='g', linestyle='--', alpha=0.5, label='额定频率')
    ax.axhline(49.5, color='r', linestyle='--', alpha=0.5, label='偏差')
    ax.set_ylabel('电网频率 (Hz)', fontsize=12)
    ax.set_title('频率波动', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 10)
    
    # 功率
    ax = axes[1]
    ax.plot(t, P, 'g-', linewidth=2)
    ax.axhline(1.0, color='r', linestyle='--', alpha=0.5, label='额定功率')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('有功功率 (pu)', fontsize=12)
    ax.set_title('功率响应（下垂控制）', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 10)
    
    plt.tight_layout()
    plt.savefig('case08_frequency_response.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case08_frequency_response.png")


def demo_lvrt_curve():
    """演示3: LVRT曲线"""
    print("\n" + "=" * 60)
    print("演示3: 低电压穿越（LVRT）要求")
    print("=" * 60)
    
    # 中国国标GB/T 19963.1-2011
    t_lvrt = np.array([0, 0.15, 0.625, 2.0, 3.0])
    V_lvrt = np.array([0, 0.2, 0.9, 0.9, 1.0])
    
    # 不同严重程度的电压跌落
    scenarios = [
        ("轻微跌落", 0.7, 1.0),
        ("中度跌落", 0.4, 1.5),
        ("严重跌落", 0.2, 2.0),
    ]
    
    print(f"\nLVRT标准（GB/T 19963.1-2011）:")
    print(f"  0s: 0%电压（最严重）")
    print(f"  0.15s: 20%电压")
    print(f"  0.625s: 90%电压")
    print(f"  3.0s: 100%电压（完全恢复）")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # LVRT曲线
    ax = axes[0]
    ax.plot(t_lvrt, V_lvrt, 'r-', linewidth=3, marker='o', markersize=8, label='LVRT边界')
    ax.fill_between(t_lvrt, V_lvrt, 1.0, alpha=0.2, color='green', label='必须保持并网')
    ax.fill_between(t_lvrt, 0, V_lvrt, alpha=0.2, color='red', label='允许脱网')
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('电压 (pu)', fontsize=12)
    ax.set_title('LVRT边界曲线', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 3.5)
    ax.set_ylim(0, 1.1)
    
    # 不同场景
    ax = axes[1]
    for name, V_dip, t_recover in scenarios:
        t_scenario = np.linspace(0, 4, 100)
        V_scenario = np.ones_like(t_scenario)
        
        # 跌落阶段
        V_scenario[(t_scenario >= 0.5) & (t_scenario < 0.5 + t_recover)] = V_dip
        
        # 恢复阶段
        for i in range(len(t_scenario)):
            if 0.5 + t_recover <= t_scenario[i] < 0.5 + t_recover + 1:
                V_scenario[i] = V_dip + (1 - V_dip) * (t_scenario[i] - 0.5 - t_recover)
        
        ax.plot(t_scenario, V_scenario, linewidth=2, label=name)
    
    ax.axhline(0.9, color='g', linestyle='--', alpha=0.5)
    ax.set_xlabel('时间 (s)', fontsize=12)
    ax.set_ylabel('电压 (pu)', fontsize=12)
    ax.set_title('典型电压跌落场景', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 4)
    
    plt.tight_layout()
    plt.savefig('case08_lvrt_curve.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case08_lvrt_curve.png")


def main():
    print("\n" + "=" * 60)
    print("案例8: 并网动态特性")
    print("=" * 60)
    
    demo_voltage_dip()
    demo_frequency_response()
    demo_lvrt_curve()
    
    print("\n" + "=" * 60)
    print("案例8 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case08_voltage_dip.png")
    print("  2. case08_frequency_response.png")
    print("  3. case08_lvrt_curve.png")
    
    print("\n核心知识点:")
    print("  ✓ 电压跌落响应")
    print("  ✓ 频率响应与下垂控制")
    print("  ✓ LVRT要求与标准")
    print("  ✓ 无功支撑策略")
    
    plt.show()


if __name__ == "__main__":
    main()
