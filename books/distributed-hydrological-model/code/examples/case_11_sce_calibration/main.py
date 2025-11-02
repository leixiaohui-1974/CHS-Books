"""
案例11：SCE-UA参数率定算法
===========================

使用SCE-UA算法自动率定新安江模型参数。

核心内容：
1. SCE-UA算法原理
2. 目标函数设计
3. 参数约束处理
4. 率定过程可视化
5. 率定结果验证

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel
from core.calibration.sce_ua import SCEUA
from core.calibration.objective import ObjectiveFunction

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def generate_synthetic_data(true_params: dict, n_days: int = 365) -> tuple:
    """
    生成合成观测数据
    
    参数:
    ----
    true_params : dict
        真实参数
    n_days : int
        天数
    
    返回:
    ----
    rainfall : ndarray
        降雨序列
    EM : ndarray
        蒸散发序列
    observed_runoff : ndarray
        "观测"径流
    """
    # 生成降雨（随机 + 几场洪水）
    np.random.seed(42)
    rainfall = np.random.exponential(2.0, n_days)
    
    # 添加几场大洪水
    flood_days = [50, 120, 200, 280]
    for day in flood_days:
        duration = np.random.randint(3, 8)
        peak = np.random.uniform(40, 80)
        for i in range(duration):
            if day + i < n_days:
                rainfall[day + i] += peak * np.exp(-0.3 * i)
    
    # 生成蒸散发数据（简单季节性模式）
    day_of_year = np.arange(n_days)
    EM = 3.0 + 2.0 * np.sin(2 * np.pi * day_of_year / 365)  # 1-5mm/day
    
    # 使用真实参数运行模型
    model = XinAnJiangModel(true_params)
    results = model.run(rainfall, EM)
    
    # 添加观测误差
    noise = np.random.normal(0, 2.0, n_days)
    observed_runoff = results['R'] + noise
    observed_runoff = np.maximum(observed_runoff, 0)  # 确保非负
    
    return rainfall, EM, observed_runoff


def create_calibration_objective(rainfall: np.ndarray,
                                 EM: np.ndarray,
                                 observed: np.ndarray,
                                 param_names: list,
                                 fixed_params: dict):
    """
    创建率定目标函数
    
    参数:
    ----
    rainfall : ndarray
        降雨数据
    EM : ndarray
        蒸散发数据
    observed : ndarray
        观测径流
    param_names : list
        待率定参数名称
    fixed_params : dict
        固定参数
    
    返回:
    ----
    objective_func : callable
        目标函数
    """
    def objective(params_array):
        """目标函数：返回NSE（最大化）"""
        # 组装参数字典
        params = fixed_params.copy()
        for i, name in enumerate(param_names):
            params[name] = params_array[i]
        
        try:
            # 运行模型
            model = XinAnJiangModel(params)
            results = model.run(rainfall, EM)
            simulated = results['R']
            
            # 计算NSE
            obs_mean = np.mean(observed)
            numerator = np.sum((observed - simulated) ** 2)
            denominator = np.sum((observed - obs_mean) ** 2)
            
            if denominator == 0:
                return -999
            
            nse = 1 - numerator / denominator
            
            # 惩罚不合理结果
            if np.any(np.isnan(simulated)) or np.any(np.isinf(simulated)):
                return -999
            
            return nse
        
        except Exception as e:
            # 模型运行失败
            return -999
    
    return objective


def plot_calibration_progress(history: dict, save_path: str = None):
    """绘制率定进度"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    iterations = history['iterations']
    scores = history['best_scores']
    
    ax.plot(iterations, scores, 'b-', linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('迭代次数', fontsize=12)
    ax.set_ylabel('目标函数值 (NSE)', fontsize=12)
    ax.set_title('SCE-UA率定收敛过程', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 标注最终值
    final_score = scores[-1]
    ax.axhline(y=final_score, color='r', linestyle='--', alpha=0.5)
    ax.text(0.02, 0.98, f'最终NSE = {final_score:.4f}',
            transform=ax.transAxes, fontsize=12, 
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_parameter_evolution(history: dict, param_names: list,
                             true_params: dict = None,
                             save_path: str = None):
    """绘制参数演变"""
    n_params = len(param_names)
    fig, axes = plt.subplots(n_params, 1, figsize=(10, 3*n_params))
    
    if n_params == 1:
        axes = [axes]
    
    iterations = history['iterations']
    
    for i, (ax, param_name) in enumerate(zip(axes, param_names)):
        param_values = [params[i] for params in history['best_params']]
        
        ax.plot(iterations, param_values, 'b-', linewidth=2, 
                marker='o', markersize=4, label='率定值')
        
        # 如果有真值，绘制
        if true_params and param_name in true_params:
            true_value = true_params[param_name]
            ax.axhline(y=true_value, color='r', linestyle='--', 
                      linewidth=2, label='真实值')
            
            # 标注最终误差
            final_value = param_values[-1]
            error = abs(final_value - true_value) / true_value * 100
            ax.text(0.98, 0.98, f'误差: {error:.1f}%',
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        ax.set_ylabel(param_name, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc='upper left')
        
        if i == n_params - 1:
            ax.set_xlabel('迭代次数', fontsize=12)
    
    plt.suptitle('参数演变过程', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_simulation_comparison(rainfall: np.ndarray,
                               observed: np.ndarray,
                               simulated_initial: np.ndarray,
                               simulated_calibrated: np.ndarray,
                               save_path: str = None):
    """绘制模拟对比"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    time = np.arange(len(rainfall))
    
    # 上图：降雨和径流过程
    ax1 = axes[0]
    ax1_rain = ax1.twinx()
    
    # 降雨（倒置）
    ax1_rain.bar(time, rainfall, color='lightblue', alpha=0.5, label='降雨')
    ax1_rain.set_ylim([max(rainfall)*2, 0])  # 倒置
    ax1_rain.set_ylabel('降雨 (mm)', fontsize=12)
    ax1_rain.legend(loc='upper right', fontsize=10)
    
    # 径流
    ax1.plot(time, observed, 'k-', linewidth=2, label='观测径流', alpha=0.8)
    ax1.plot(time, simulated_initial, 'b--', linewidth=1.5, 
            label='初始参数模拟', alpha=0.7)
    ax1.plot(time, simulated_calibrated, 'r-', linewidth=2,
            label='率定参数模拟', alpha=0.8)
    
    ax1.set_ylabel('径流 (mm)', fontsize=12)
    ax1.set_title('降雨-径流过程对比', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 下图：散点对比
    ax2 = axes[1]
    
    ax2.scatter(observed, simulated_initial, c='blue', alpha=0.5, 
               s=30, label='初始参数')
    ax2.scatter(observed, simulated_calibrated, c='red', alpha=0.5,
               s=30, label='率定参数')
    
    # 1:1线
    max_val = max(np.max(observed), np.max(simulated_calibrated))
    ax2.plot([0, max_val], [0, max_val], 'k--', linewidth=2, label='1:1线')
    
    # 计算NSE
    def calc_nse(obs, sim):
        return 1 - np.sum((obs - sim)**2) / np.sum((obs - np.mean(obs))**2)
    
    nse_initial = calc_nse(observed, simulated_initial)
    nse_calibrated = calc_nse(observed, simulated_calibrated)
    
    ax2.text(0.05, 0.95, 
            f'初始NSE = {nse_initial:.4f}\n率定NSE = {nse_calibrated:.4f}',
            transform=ax2.transAxes, fontsize=11,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax2.set_xlabel('观测径流 (mm)', fontsize=12)
    ax2.set_ylabel('模拟径流 (mm)', fontsize=12)
    ax2.set_title('观测-模拟散点图', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10, loc='lower right')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_parameter_comparison(param_names: list,
                              initial_params: dict,
                              calibrated_params: dict,
                              true_params: dict = None,
                              save_path: str = None):
    """绘制参数对比柱状图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(param_names))
    width = 0.25
    
    initial_values = [initial_params[name] for name in param_names]
    calibrated_values = [calibrated_params[name] for name in param_names]
    
    bars1 = ax.bar(x - width, initial_values, width, label='初始值',
                   color='lightblue', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x, calibrated_values, width, label='率定值',
                   color='lightcoral', edgecolor='black', linewidth=1.5)
    
    if true_params:
        true_values = [true_params[name] for name in param_names]
        bars3 = ax.bar(x + width, true_values, width, label='真实值',
                      color='lightgreen', edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('参数', fontsize=12)
    ax.set_ylabel('参数值', fontsize=12)
    ax.set_title('参数率定结果对比', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(param_names, fontsize=11, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)
    
    # 添加数值标签
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)
    
    add_value_labels(bars1)
    add_value_labels(bars2)
    if true_params:
        add_value_labels(bars3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def main():
    """主函数"""
    print("\n" + "="*70)
    print("案例11：SCE-UA参数率定算法")
    print("="*70 + "\n")
    
    # 创建输出目录
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # ========== 1. 生成合成数据 ==========
    print("1. 生成合成观测数据")
    print("-" * 70)
    
    # 真实参数（新安江模型全部参数）
    true_params = {
        # 蒸散发参数
        'K': 0.8,
        'UM': 20.0,
        'LM': 80.0,
        'C': 0.15,
        # 产流参数
        'WM': 120.0,
        'B': 0.35,
        'IM': 0.02,
        # 水源划分参数
        'SM': 30.0,
        'EX': 1.5,
        'KG': 0.4,
        'KI': 0.3,
        # 汇流参数
        'CG': 0.98,
        'CI': 0.6,
        'CS': 0.8
    }
    
    n_days = 365
    rainfall, EM, observed_runoff = generate_synthetic_data(true_params, n_days)
    
    print(f"数据长度: {n_days} 天")
    print(f"总降雨: {np.sum(rainfall):.1f} mm")
    print(f"总径流: {np.sum(observed_runoff):.1f} mm")
    print(f"径流系数: {np.sum(observed_runoff)/np.sum(rainfall):.3f}\n")
    
    # ========== 2. 设置率定参数 ==========
    print("2. 设置率定参数")
    print("-" * 70)
    
    # 待率定参数（选择最敏感的几个）
    param_names = ['WM', 'B', 'KI', 'KG']
    
    # 参数边界
    bounds = [
        (80, 200),   # WM
        (0.1, 0.5),  # B
        (0.1, 0.5),  # KI
        (0.2, 0.6)   # KG
    ]
    
    # 固定其他参数
    fixed_params = {k: v for k, v in true_params.items() 
                   if k not in param_names}
    
    print(f"待率定参数: {param_names}")
    print(f"参数边界:")
    for name, (lower, upper) in zip(param_names, bounds):
        print(f"  {name}: [{lower}, {upper}]")
    print()
    
    # ========== 3. 初始模拟 ==========
    print("3. 初始参数模拟")
    print("-" * 70)
    
    # 使用边界中点作为初始参数
    initial_params = fixed_params.copy()
    for name, (lower, upper) in zip(param_names, bounds):
        initial_params[name] = (lower + upper) / 2
    
    model_initial = XinAnJiangModel(initial_params)
    results_initial = model_initial.run(rainfall, EM)
    simulated_initial = results_initial['R']
    
    # 计算初始NSE
    obs_mean = np.mean(observed_runoff)
    nse_initial = 1 - np.sum((observed_runoff - simulated_initial)**2) / \
                      np.sum((observed_runoff - obs_mean)**2)
    
    print(f"初始参数:")
    for name in param_names:
        print(f"  {name} = {initial_params[name]:.2f}")
    print(f"\n初始NSE: {nse_initial:.4f}\n")
    
    # ========== 4. SCE-UA率定 ==========
    print("4. SCE-UA参数率定")
    print("-" * 70)
    
    # 创建目标函数
    objective_func = create_calibration_objective(
        rainfall, EM, observed_runoff, param_names, fixed_params
    )
    
    # 创建优化器
    optimizer = SCEUA(
        objective_func=objective_func,
        bounds=bounds,
        n_complexes=3,
        n_points_per_complex=10
    )
    
    # 执行优化
    result = optimizer.optimize(
        max_iterations=30,
        tolerance=1e-4,
        verbose=True
    )
    
    # ========== 5. 率定后模拟 ==========
    print("\n5. 率定参数模拟")
    print("-" * 70)
    
    calibrated_params = fixed_params.copy()
    for i, name in enumerate(param_names):
        calibrated_params[name] = result['best_params'][i]
    
    model_calibrated = XinAnJiangModel(calibrated_params)
    results_calibrated = model_calibrated.run(rainfall, EM)
    simulated_calibrated = results_calibrated['R']
    
    nse_calibrated = result['best_score']
    
    print(f"率定参数:")
    for name in param_names:
        print(f"  {name} = {calibrated_params[name]:.2f} "
              f"(真值: {true_params[name]:.2f})")
    print(f"\n率定NSE: {nse_calibrated:.4f}")
    print(f"NSE提升: {nse_calibrated - nse_initial:.4f}\n")
    
    # ========== 6. 可视化 ==========
    print("6. 生成可视化图表")
    print("-" * 70)
    
    plot_calibration_progress(
        result['history'],
        save_path=f'{output_dir}/calibration_progress.png'
    )
    
    plot_parameter_evolution(
        result['history'],
        param_names,
        true_params=true_params,
        save_path=f'{output_dir}/parameter_evolution.png'
    )
    
    plot_simulation_comparison(
        rainfall,
        observed_runoff,
        simulated_initial,
        simulated_calibrated,
        save_path=f'{output_dir}/simulation_comparison.png'
    )
    
    plot_parameter_comparison(
        param_names,
        initial_params,
        calibrated_params,
        true_params=true_params,
        save_path=f'{output_dir}/parameter_comparison.png'
    )
    
    # ========== 7. 结果统计 ==========
    print("\n" + "="*70)
    print("SCE-UA率定结果统计")
    print("="*70)
    
    print(f"\n【率定设置】")
    print(f"  数据长度: {n_days} 天")
    print(f"  待率定参数数: {len(param_names)}")
    print(f"  迭代次数: {result['n_iterations']}")
    print(f"  收敛状态: {'是' if result['converged'] else '否'}")
    
    print(f"\n【模拟精度】")
    print(f"  初始NSE: {nse_initial:.4f}")
    print(f"  率定NSE: {nse_calibrated:.4f}")
    print(f"  NSE提升: {nse_calibrated - nse_initial:.4f}")
    
    print(f"\n【参数恢复精度】")
    for name in param_names:
        true_val = true_params[name]
        calib_val = calibrated_params[name]
        error = abs(calib_val - true_val) / true_val * 100
        print(f"  {name}: 真值={true_val:.2f}, 率定值={calib_val:.2f}, "
              f"误差={error:.1f}%")
    
    print(f"\n所有图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
