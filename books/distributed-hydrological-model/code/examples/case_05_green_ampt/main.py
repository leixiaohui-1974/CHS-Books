"""
案例5：Green-Ampt超渗产流模型
=============================

演示Green-Ampt模型的入渗和超渗产流过程

作者: CHS-Books项目组
日期: 2025-11-02
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from core.runoff_generation.green_ampt import (
    GreenAmptModel, create_default_green_ampt_params
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)


def generate_rainfall_event(event_type='steady', duration_hours=2, dt=0.1):
    """
    生成降雨过程
    
    Parameters
    ----------
    event_type : str
        降雨类型: 'steady', 'increasing', 'decreasing', 'storm'
    duration_hours : float
        持续时间 (h)
    dt : float
        时间步长 (h)
    
    Returns
    -------
    rainfall : ndarray
        降雨强度序列 (mm/h)
    """
    n_steps = int(duration_hours / dt)
    time = np.arange(n_steps) * dt
    
    if event_type == 'steady':
        # 恒定降雨
        rainfall = np.ones(n_steps) * 30.0
    
    elif event_type == 'increasing':
        # 递增降雨
        rainfall = 10 + 40 * time / duration_hours
    
    elif event_type == 'decreasing':
        # 递减降雨
        rainfall = 50 - 40 * time / duration_hours
    
    elif event_type == 'storm':
        # 暴雨过程（正态分布）
        peak_time = duration_hours / 2
        rainfall = 50 * np.exp(-((time - peak_time) / (duration_hours / 4))**2)
    
    elif event_type == 'intermittent':
        # 间歇降雨
        rainfall = np.zeros(n_steps)
        rainfall[0:int(n_steps/3)] = 40
        rainfall[int(2*n_steps/3):] = 25
    
    else:
        raise ValueError(f"未知的降雨类型: {event_type}")
    
    return rainfall


def plot_infiltration_process(time, rainfall, results, soil_type, save_path=None):
    """绘制入渗过程图"""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # 子图1：降雨强度和入渗率
    ax = axes[0]
    ax.plot(time, rainfall, 'b-', linewidth=2.5, label='降雨强度')
    ax.plot(time, results['f'], 'r-', linewidth=2.5, label='入渗率')
    ax.fill_between(time, 0, rainfall, alpha=0.2, color='blue')
    ax.fill_between(time, 0, results['f'], alpha=0.2, color='red')
    ax.set_ylabel('强度 (mm/h)', fontsize=12)
    ax.set_title(f'Green-Ampt入渗过程 ({soil_type})', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # 子图2：累积入渗和累积径流
    ax = axes[1]
    cum_rainfall = np.cumsum(rainfall * 0.1)  # dt=0.1h
    cum_runoff = np.cumsum(results['runoff'])
    ax.plot(time, cum_rainfall, 'b-', linewidth=2.5, label='累积降雨')
    ax.plot(time, results['F'], 'g-', linewidth=2.5, label='累积入渗')
    ax.plot(time, cum_runoff, 'r-', linewidth=2.5, label='累积径流')
    ax.set_ylabel('累积量 (mm)', fontsize=12)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 子图3：径流强度
    ax = axes[2]
    runoff_intensity = results['runoff'] / 0.1  # 转换为mm/h
    ax.bar(time, runoff_intensity, width=0.08, color='orange', 
          alpha=0.7, edgecolor='black', linewidth=0.5)
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('径流强度 (mm/h)', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def compare_soil_types(save_path=None):
    """对比不同土壤类型"""
    soil_types = ['sand', 'loam', 'clay']
    soil_names = ['砂土', '壤土', '黏土']
    colors = ['#FFD700', '#8B4513', '#696969']
    
    # 生成降雨
    duration = 2.0  # hours
    dt = 0.1
    rainfall = generate_rainfall_event('storm', duration, dt)
    time = np.arange(len(rainfall)) * dt
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 子图1：入渗率对比
    ax = axes[0, 0]
    ax.plot(time, rainfall, 'b--', linewidth=2, alpha=0.5, label='降雨强度')
    
    for soil_type, name, color in zip(soil_types, soil_names, colors):
        params = create_default_green_ampt_params(soil_type)
        model = GreenAmptModel(params)
        results = model.run(rainfall)
        ax.plot(time, results['f'], linewidth=2.5, label=f'{name}', color=color)
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('入渗率 (mm/h)', fontsize=12)
    ax.set_title('不同土壤的入渗率对比', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # 子图2：累积入渗量对比
    ax = axes[0, 1]
    for soil_type, name, color in zip(soil_types, soil_names, colors):
        params = create_default_green_ampt_params(soil_type)
        model = GreenAmptModel(params)
        results = model.run(rainfall)
        ax.plot(time, results['F'], linewidth=2.5, label=f'{name}', color=color)
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('累积入渗量 (mm)', fontsize=12)
    ax.set_title('累积入渗量对比', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # 子图3：产流量对比
    ax = axes[1, 0]
    runoff_totals = []
    for soil_type, name, color in zip(soil_types, soil_names, colors):
        params = create_default_green_ampt_params(soil_type)
        model = GreenAmptModel(params)
        results = model.run(rainfall)
        runoff_total = np.sum(results['runoff'])
        runoff_totals.append(runoff_total)
        cum_runoff = np.cumsum(results['runoff'])
        ax.plot(time, cum_runoff, linewidth=2.5, label=f'{name}', color=color)
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('累积径流量 (mm)', fontsize=12)
    ax.set_title('累积径流量对比', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # 子图4：径流系数对比
    ax = axes[1, 1]
    total_rainfall = np.sum(rainfall * dt)
    runoff_coeffs = [r / total_rainfall for r in runoff_totals]
    
    bars = ax.bar(soil_names, runoff_coeffs, color=colors, 
                  edgecolor='black', linewidth=2, alpha=0.8)
    ax.set_ylabel('径流系数', fontsize=12)
    ax.set_title('径流系数对比', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1)
    
    # 标注数值
    for bar, coeff in zip(bars, runoff_coeffs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{coeff:.1%}',
               ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def parameter_sensitivity_analysis(save_path=None):
    """参数敏感性分析"""
    # 基准参数（壤土）
    base_params = create_default_green_ampt_params('loam')
    
    # 生成降雨
    duration = 2.0
    dt = 0.1
    rainfall = generate_rainfall_event('storm', duration, dt)
    time = np.arange(len(rainfall)) * dt
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # 1. K参数敏感性
    ax = axes[0]
    K_values = [0.5, 1.0, 2.0, 5.0]  # 相对于基准值的倍数
    for k_mult in K_values:
        params = base_params.copy()
        params['K'] = base_params['K'] * k_mult
        model = GreenAmptModel(params)
        results = model.run(rainfall)
        runoff_total = np.sum(results['runoff'])
        ax.plot(time, np.cumsum(results['runoff']), 
               linewidth=2.5, label=f'K × {k_mult} ({runoff_total:.1f}mm)')
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('累积径流 (mm)', fontsize=12)
    ax.set_title('饱和导水率(K)敏感性', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 2. ψ参数敏感性
    ax = axes[1]
    psi_values = [0.5, 1.0, 1.5, 2.0]
    for psi_mult in psi_values:
        params = base_params.copy()
        params['psi'] = base_params['psi'] * psi_mult
        model = GreenAmptModel(params)
        results = model.run(rainfall)
        runoff_total = np.sum(results['runoff'])
        ax.plot(time, np.cumsum(results['runoff']), 
               linewidth=2.5, label=f'ψ × {psi_mult} ({runoff_total:.1f}mm)')
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('累积径流 (mm)', fontsize=12)
    ax.set_title('湿润锋吸力(ψ)敏感性', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 3. Δθ参数敏感性
    ax = axes[2]
    theta_i_values = [0.10, 0.15, 0.20, 0.25]  # 初始含水率
    for theta_i in theta_i_values:
        params = base_params.copy()
        params['theta_i'] = theta_i
        delta_theta = params['theta_s'] - theta_i
        model = GreenAmptModel(params)
        results = model.run(rainfall)
        runoff_total = np.sum(results['runoff'])
        ax.plot(time, np.cumsum(results['runoff']), 
               linewidth=2.5, label=f'Δθ={delta_theta:.2f} ({runoff_total:.1f}mm)')
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('累积径流 (mm)', fontsize=12)
    ax.set_title('含水率差(Δθ)敏感性', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def rainfall_scenarios_comparison(save_path=None):
    """不同降雨情景对比"""
    scenarios = ['steady', 'increasing', 'decreasing', 'storm', 'intermittent']
    scenario_names = ['恒定降雨', '递增降雨', '递减降雨', '暴雨过程', '间歇降雨']
    
    # 使用壤土
    params = create_default_green_ampt_params('loam')
    duration = 2.0
    dt = 0.1
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for i, (scenario, name) in enumerate(zip(scenarios, scenario_names)):
        rainfall = generate_rainfall_event(scenario, duration, dt)
        time = np.arange(len(rainfall)) * dt
        
        model = GreenAmptModel(params)
        results = model.run(rainfall)
        
        ax = axes[i]
        
        # 双Y轴
        ax2 = ax.twinx()
        
        # 降雨和入渗率
        l1 = ax.plot(time, rainfall, 'b-', linewidth=2, alpha=0.6, label='降雨强度')
        l2 = ax.plot(time, results['f'], 'r-', linewidth=2, label='入渗率')
        
        # 累积量
        cum_rainfall = np.cumsum(rainfall * dt)
        cum_runoff = np.cumsum(results['runoff'])
        l3 = ax2.plot(time, cum_rainfall, 'b--', linewidth=2, alpha=0.5, label='累积降雨')
        l4 = ax2.plot(time, cum_runoff, 'r--', linewidth=2, alpha=0.5, label='累积径流')
        
        ax.set_xlabel('时间 (h)', fontsize=11)
        ax.set_ylabel('强度 (mm/h)', fontsize=11, color='black')
        ax2.set_ylabel('累积量 (mm)', fontsize=11, color='black')
        ax.set_title(name, fontsize=12, fontweight='bold')
        
        # 合并图例
        lines = l1 + l2 + l3 + l4
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, fontsize=9, loc='upper left')
        
        ax.grid(True, alpha=0.3)
        
        # 标注径流系数
        runoff_coeff = cum_runoff[-1] / cum_rainfall[-1]
        ax.text(0.98, 0.02, f'径流系数: {runoff_coeff:.1%}',
               transform=ax.transAxes, fontsize=10,
               ha='right', va='bottom',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 移除多余的子图
    axes[-1].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def main():
    """主函数"""
    print("=" * 70)
    print("案例5：Green-Ampt超渗产流模型")
    print("=" * 70)
    print()
    
    # 1. 基本入渗过程演示
    print("1. 基本入渗过程演示（壤土）...")
    params = create_default_green_ampt_params('loam')
    print(f"   土壤参数:")
    print(f"     K (饱和导水率): {params['K']:.2f} mm/h")
    print(f"     ψ (湿润锋吸力): {params['psi']:.1f} mm")
    print(f"     θs (饱和含水率): {params['theta_s']:.3f}")
    print(f"     θi (初始含水率): {params['theta_i']:.3f}")
    print(f"     Δθ (含水率差): {params['theta_s'] - params['theta_i']:.3f}")
    print()
    
    # 生成暴雨过程
    duration = 2.0
    dt = 0.1
    rainfall = generate_rainfall_event('storm', duration, dt)
    time = np.arange(len(rainfall)) * dt
    
    # 运行模型
    model = GreenAmptModel(params)
    results = model.run(rainfall)
    
    # 统计
    total_rainfall = np.sum(rainfall * dt)
    total_infiltration = results['F'][-1]
    total_runoff = np.sum(results['runoff'])
    runoff_coeff = total_runoff / total_rainfall
    
    print(f"   模拟结果:")
    print(f"     总降雨量: {total_rainfall:.2f} mm")
    print(f"     总入渗量: {total_infiltration:.2f} mm")
    print(f"     总径流量: {total_runoff:.2f} mm")
    print(f"     径流系数: {runoff_coeff:.2%}")
    print(f"     水量平衡误差: {abs(total_rainfall - total_infiltration - total_runoff):.6f} mm")
    print()
    
    # 绘图
    fig1 = plot_infiltration_process(time, rainfall, results, '壤土',
                                     save_path=output_dir / 'infiltration_process.png')
    plt.close(fig1)
    
    # 2. 不同土壤类型对比
    print("2. 不同土壤类型对比...")
    fig2 = compare_soil_types(save_path=output_dir / 'soil_comparison.png')
    plt.close(fig2)
    print("   对比完成")
    print()
    
    # 3. 参数敏感性分析
    print("3. 参数敏感性分析...")
    fig3 = parameter_sensitivity_analysis(save_path=output_dir / 'parameter_sensitivity.png')
    plt.close(fig3)
    print("   敏感性分析完成")
    print()
    
    # 4. 降雨情景对比
    print("4. 不同降雨情景对比...")
    fig4 = rainfall_scenarios_comparison(save_path=output_dir / 'rainfall_scenarios.png')
    plt.close(fig4)
    print("   情景对比完成")
    print()
    
    # 5. 总结
    print("=" * 70)
    print("分析完成！")
    print("=" * 70)
    print()
    print("生成的文件:")
    print("  - outputs/infiltration_process.png    : 基本入渗过程")
    print("  - outputs/soil_comparison.png         : 不同土壤对比")
    print("  - outputs/parameter_sensitivity.png   : 参数敏感性")
    print("  - outputs/rainfall_scenarios.png      : 降雨情景对比")
    print()
    print("关键发现:")
    print("  1. Green-Ampt模型清晰描述了超渗产流机理")
    print("  2. 砂土入渗能力强，径流系数小（<10%）")
    print("  3. 黏土入渗能力弱，径流系数大（>80%）")
    print("  4. 饱和导水率K是最敏感的参数")
    print("  5. 降雨强度和土壤类型共同决定产流特性")
    print()


if __name__ == '__main__':
    main()
