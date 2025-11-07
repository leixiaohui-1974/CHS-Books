"""
案例11：日前调度优化（单目标）

展示内容：
1. 构建日前优化模型
2. 考虑水火风光储多种电源
3. 最小化总成本
4. 满足功率平衡约束

作者: CHS Books
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
from models.optimization import DayAheadOptimization, PowerSource
from models.multi_energy_system import LoadModel

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_renewable_forecast(T=96):
    """
    生成新能源预测曲线
    
    Args:
        T: 时间步数
        
    Returns:
        wind, solar: 风电和光伏预测
    """
    t = np.linspace(0, 24, T)
    
    # 风电：夜间和早晨较大
    wind = 150 * (
        0.8 + 0.3 * np.sin(2 * np.pi * t / 24 + np.pi) +
        0.1 * np.random.randn(T)
    )
    wind = np.clip(wind, 0, 200)
    
    # 光伏：白天有出力
    solar = 120 * np.maximum(0, np.sin(np.pi * (t - 6) / 12)) ** 2
    solar = np.clip(solar, 0, 150)
    
    return wind, solar


def main():
    """主函数"""
    
    print("=" * 70)
    print("案例11：日前调度优化（单目标 - 最小化成本）")
    print("=" * 70)
    
    # 1. 定义电源
    sources = [
        PowerSource(
            name="水电1",
            type="hydro",
            P_rated=300,
            P_min=100,
            P_max=300,
            ramp_rate=50,  # MW/min
            cost_coef=(0, 30, 0),  # 成本较低
            emission_coef=0  # 零排放
        ),
        PowerSource(
            name="火电1",
            type="thermal",
            P_rated=600,
            P_min=200,
            P_max=600,
            ramp_rate=10,
            cost_coef=(1000, 50, 0.01),  # 成本较高
            emission_coef=0.8  # tCO2/MWh
        ),
        PowerSource(
            name="火电2",
            type="thermal",
            P_rated=400,
            P_min=150,
            P_max=400,
            ramp_rate=8,
            cost_coef=(800, 55, 0.015),  # 成本更高
            emission_coef=0.85
        ),
    ]
    
    print("\n电源配置：")
    for source in sources:
        print(f"  {source.name}:")
        print(f"    类型: {source.type}, 容量: {source.P_rated} MW")
        print(f"    成本系数: a={source.cost_coef[0]}, b={source.cost_coef[1]}, c={source.cost_coef[2]}")
    
    # 2. 生成负荷和新能源预测
    T = 96  # 24小时，15分钟间隔
    
    load_model = LoadModel()
    load_forecast = load_model.generate_daily_load(
        P_base=1000,
        peak_ratio=1.3,
        valley_ratio=0.7,
        n_points=T
    )
    
    wind_forecast, solar_forecast = generate_renewable_forecast(T)
    
    print(f"\n负荷与新能源预测：")
    print(f"  负荷范围: {load_forecast.min():.0f} - {load_forecast.max():.0f} MW")
    print(f"  风电预测: {wind_forecast.min():.0f} - {wind_forecast.max():.0f} MW")
    print(f"  光伏预测: {solar_forecast.min():.0f} - {solar_forecast.max():.0f} MW")
    
    # 3. 创建优化模型
    optimizer = DayAheadOptimization(
        sources=sources,
        time_horizon=T,
        dt=0.25  # 15分钟 = 0.25小时
    )
    
    # 4. 构建优化问题
    renewable_forecast = {
        'wind': wind_forecast,
        'solar': solar_forecast
    }
    
    problem = optimizer.formulate_problem(
        load_forecast=load_forecast,
        renewable_forecast=renewable_forecast
    )
    
    net_load = problem['net_load']
    print(f"\n净负荷（负荷-新能源）：")
    print(f"  范围: {net_load.min():.0f} - {net_load.max():.0f} MW")
    print(f"  平均: {net_load.mean():.0f} MW")
    
    # 5. 求解优化问题
    print(f"\n开始优化求解...")
    solution = optimizer.solve_single_objective(net_load=net_load)
    
    P_schedule = solution['P_schedule']
    total_cost = solution['total_cost']
    
    print(f"优化完成！")
    print(f"\n优化结果：")
    print(f"  总成本: {total_cost:,.0f} 元")
    print(f"  日均成本: {total_cost/24:,.0f} 元/小时")
    
    # 6. 分析各电源出力
    print(f"\n各电源出力统计：")
    for i, source in enumerate(sources):
        P_i = P_schedule[:, i]
        energy_i = np.sum(P_i) * optimizer.dt
        print(f"  {source.name}:")
        print(f"    出力范围: {P_i.min():.1f} - {P_i.max():.1f} MW")
        print(f"    平均出力: {P_i.mean():.1f} MW")
        print(f"    日发电量: {energy_i:.0f} MWh")
    
    # 7. 计算总排放
    total_emission = 0
    for i, source in enumerate(sources):
        P_i = P_schedule[:, i]
        energy_i = np.sum(P_i) * optimizer.dt
        emission_i = energy_i * source.emission_coef
        total_emission += emission_i
    
    print(f"\n环境指标：")
    print(f"  总CO2排放: {total_emission:.0f} tCO2")
    print(f"  单位电量排放: {total_emission / np.sum(load_forecast) / optimizer.dt:.3f} tCO2/MWh")
    
    # 8. 绘图
    t_hours = np.linspace(0, 24, T)
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # 8.1 负荷与新能源
    ax = axes[0]
    ax.plot(t_hours, load_forecast, 'k-', label='负荷', linewidth=2)
    ax.plot(t_hours, wind_forecast, 'g--', label='风电预测', linewidth=1.5)
    ax.plot(t_hours, solar_forecast, 'orange', linestyle='--', label='光伏预测', linewidth=1.5)
    ax.plot(t_hours, net_load, 'r-', label='净负荷', linewidth=2, alpha=0.7)
    ax.set_ylabel('功率 (MW)')
    ax.set_title('负荷与新能源预测')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    
    # 8.2 电源调度方案（堆叠图）
    ax = axes[1]
    
    # 堆叠绘制
    bottom = np.zeros(T)
    colors = ['royalblue', 'tomato', 'orange']
    
    for i, source in enumerate(sources):
        P_i = P_schedule[:, i]
        ax.fill_between(t_hours, bottom, bottom + P_i, 
                        label=source.name, alpha=0.7, color=colors[i])
        bottom += P_i
    
    # 叠加净负荷曲线对比
    ax.plot(t_hours, net_load, 'k--', label='净负荷', linewidth=2)
    
    ax.set_ylabel('功率 (MW)')
    ax.set_title('常规电源调度方案（堆叠图）')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    
    # 8.3 各电源出力分解
    ax = axes[2]
    for i, source in enumerate(sources):
        P_i = P_schedule[:, i]
        ax.plot(t_hours, P_i, label=source.name, linewidth=2)
    
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('功率 (MW)')
    ax.set_title('各电源出力曲线')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 24)
    
    plt.tight_layout()
    plt.savefig('example_11_day_ahead_optimization.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存: example_11_day_ahead_optimization.png")
    plt.show()
    
    # 9. 经济性分析
    print(f"\n经济性分析：")
    
    # 新能源消纳
    renewable_total = np.sum(wind_forecast + solar_forecast) * optimizer.dt
    load_total = np.sum(load_forecast) * optimizer.dt
    renewable_ratio = renewable_total / load_total
    
    print(f"  日总负荷: {load_total:.0f} MWh")
    print(f"  新能源发电: {renewable_total:.0f} MWh")
    print(f"  新能源占比: {renewable_ratio:.1%}")
    
    # 各电源成本分解
    print(f"\n各电源成本分解：")
    for i, source in enumerate(sources):
        P_i = P_schedule[:, i]
        a, b, c = source.cost_coef
        cost_i = 0
        for t in range(T):
            P = P_i[t]
            cost_i += (a + b * P + c * P**2) * optimizer.dt
        
        print(f"  {source.name}: {cost_i:,.0f} 元 ({cost_i/total_cost:.1%})")
    
    print("\n" + "=" * 70)
    print("案例11完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
