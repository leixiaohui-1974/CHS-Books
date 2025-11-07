"""
案例1：水电站建模与日运行仿真

展示内容：
1. 水电站模型建立
2. 入库流量曲线
3. 日运行优化仿真
4. 库容、水头、功率变化分析

作者: CHS Books
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
from models.multi_energy_system import HydropowerPlant

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_inflow_profile(base_flow=500, amplitude=200, T=96):
    """
    生成日入库流量曲线
    
    模拟日内变化：白天径流量大，夜间小
    """
    t = np.linspace(0, 24, T)
    # 白天（6:00-18:00）流量大
    inflow = base_flow + amplitude * (
        np.exp(-((t - 12)**2) / 20) - 0.3 * np.exp(-((t - 0)**2) / 10)
    )
    inflow = np.maximum(inflow, 200)  # 最小流量
    return inflow


def generate_power_target(peak_power=250, valley_power=150, T=96):
    """
    生成目标功率曲线
    
    典型双峰负荷曲线
    """
    t = np.linspace(0, 24, T)
    power_target = valley_power + (peak_power - valley_power) * (
        0.8 * np.exp(-((t - 10)**2) / 8) +  # 早高峰
        1.0 * np.exp(-((t - 19)**2) / 8) +  # 晚高峰
        0.3 * np.sin(np.pi * t / 12)  # 日变化
    )
    return power_target


def main():
    """主函数"""
    
    print("=" * 60)
    print("案例1：水电站建模与日运行仿真")
    print("=" * 60)
    
    # 1. 创建水电站
    hydro = HydropowerPlant(
        reservoir_capacity=1000e6,  # 10亿m³
        H_rated=100,  # 100m水头
        Q_max=1000,  # 1000 m³/s
        efficiency=0.90,
        P_rated=300,  # 300 MW
        name="示范水电站"
    )
    
    print(f"\n水电站参数：")
    print(f"  水库容量: {hydro.V_capacity/1e6:.0f} 百万m³")
    print(f"  额定水头: {hydro.H_rated:.0f} m")
    print(f"  最大流量: {hydro.Q_max:.0f} m³/s")
    print(f"  水轮机效率: {hydro.efficiency:.2%}")
    print(f"  额定功率: {hydro.P_rated:.0f} MW")
    
    # 2. 生成日运行场景
    T = 96  # 24小时，15分钟间隔
    dt = 900  # 15分钟 = 900秒
    
    inflow_profile = generate_inflow_profile(T=T)
    power_target = generate_power_target(T=T)
    
    print(f"\n运行场景：")
    print(f"  时间范围: 24小时")
    print(f"  时间步长: 15分钟")
    print(f"  入库流量: {inflow_profile.min():.0f} - {inflow_profile.max():.0f} m³/s")
    print(f"  目标功率: {power_target.min():.0f} - {power_target.max():.0f} MW")
    
    # 3. 运行仿真
    print(f"\n开始仿真...")
    
    hydro.V = hydro.V_capacity * 0.6  # 初始库容60%
    V_init = hydro.V
    
    results = hydro.simulate_daily_operation(
        inflow_profile=inflow_profile,
        power_target=power_target,
        dt=dt
    )
    
    print(f"仿真完成！")
    
    # 4. 结果分析
    P_actual = results['P']
    Q_out = results['Q_out']
    V_trajectory = results['V']
    H_trajectory = results['H']
    
    print(f"\n结果统计：")
    print(f"  实际出力: {P_actual.min():.1f} - {P_actual.max():.1f} MW")
    print(f"  平均出力: {P_actual.mean():.1f} MW")
    print(f"  出库流量: {Q_out.min():.1f} - {Q_out.max():.1f} m³/s")
    print(f"  初始库容: {V_init/1e6:.1f} 百万m³ ({V_init/hydro.V_capacity:.1%})")
    print(f"  结束库容: {V_trajectory[-1]/1e6:.1f} 百万m³ ({V_trajectory[-1]/hydro.V_capacity:.1%})")
    print(f"  库容变化: {(V_trajectory[-1] - V_init)/1e6:.1f} 百万m³")
    
    # 计算跟踪误差
    tracking_error = np.mean(np.abs(P_actual - power_target))
    print(f"  平均跟踪误差: {tracking_error:.2f} MW")
    
    # 5. 绘图
    t_hours = np.linspace(0, 24, T)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 5.1 功率曲线
    ax = axes[0, 0]
    ax.plot(t_hours, power_target, 'b--', label='目标功率', linewidth=2)
    ax.plot(t_hours, P_actual, 'r-', label='实际出力', linewidth=1.5)
    ax.fill_between(t_hours, power_target, P_actual, alpha=0.3)
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('功率 (MW)')
    ax.set_title('水电站出力曲线')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    
    # 5.2 流量曲线
    ax = axes[0, 1]
    ax.plot(t_hours, inflow_profile, 'g-', label='入库流量', linewidth=2)
    ax.plot(t_hours, Q_out, 'orange', label='出库流量', linewidth=2)
    ax.fill_between(t_hours, inflow_profile, Q_out, alpha=0.3,
                     where=(inflow_profile >= Q_out), color='green', label='蓄水')
    ax.fill_between(t_hours, inflow_profile, Q_out, alpha=0.3,
                     where=(inflow_profile < Q_out), color='red', label='放水')
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('流量 (m³/s)')
    ax.set_title('入库/出库流量')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    
    # 5.3 库容变化
    ax = axes[1, 0]
    V_percent = V_trajectory / hydro.V_capacity * 100
    ax.plot(t_hours, V_percent, 'b-', linewidth=2)
    ax.axhline(y=50, color='r', linestyle='--', label='50%库容')
    ax.fill_between(t_hours, V_percent, 50, alpha=0.3)
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('库容 (%)')
    ax.set_title('水库库容变化')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 100)
    
    # 5.4 水头变化
    ax = axes[1, 1]
    ax.plot(t_hours, H_trajectory, 'm-', linewidth=2)
    ax.axhline(y=hydro.H_rated, color='k', linestyle='--', label='额定水头')
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('水头 (m)')
    ax.set_title('水头变化')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    
    plt.tight_layout()
    plt.savefig('example_01_hydro_modeling.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存: example_01_hydro_modeling.png")
    plt.show()
    
    # 6. 性能评估
    print(f"\n性能评估：")
    
    # 发电量
    energy_generated = np.sum(P_actual) * (dt / 3600)  # MWh
    print(f"  日发电量: {energy_generated:.0f} MWh")
    
    # 水能利用率
    total_inflow = np.sum(inflow_profile) * dt  # m³
    potential_energy = total_inflow * hydro.rho * hydro.g * hydro.H_rated / 1e6  # MJ
    potential_energy_MWh = potential_energy / 3.6  # MWh
    utilization = energy_generated / potential_energy_MWh
    print(f"  水能利用率: {utilization:.1%}")
    
    # 跟踪性能
    tracking_quality = 1 - tracking_error / power_target.mean()
    print(f"  跟踪性能: {tracking_quality:.1%}")
    
    print("\n" + "=" * 60)
    print("案例1完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
