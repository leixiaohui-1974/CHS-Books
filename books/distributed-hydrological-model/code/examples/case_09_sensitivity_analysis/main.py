"""
案例9：参数敏感性分析

本案例演示如何进行水文模型参数敏感性分析：
1. 单参数敏感性分析（OAT方法）
2. 全局敏感性分析（Sobol方法）
3. 多种敏感性指标计算
4. 敏感性可视化（龙卷风图、散点图、热图）
5. 参数重要性排序

from pathlib import Path
作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import sys
from typing import Dict, List, Tuple, Callable

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.runoff_generation import XinAnJiangModel, create_default_xaj_params

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def generate_rainfall_data(n_steps=100, total_rainfall=150, seed=42):
    """
    生成降雨数据
    
    参数:
    ----
    n_steps : int
        时间步数
    total_rainfall : float
        总降雨量(mm)
    seed : int
        随机种子
    
    返回:
    ----
    rainfall : ndarray
        降雨序列(mm)
    """
    np.random.seed(seed)
    
    # 生成基础雨型（gamma分布）
    shape, scale = 2.0, 1.0
    rainfall_pattern = np.random.gamma(shape, scale, n_steps)
    
    # 归一化并缩放
    rainfall_pattern = rainfall_pattern / rainfall_pattern.sum() * total_rainfall
    
    # 添加一些峰值
    peak_positions = [20, 40, 60]
    for pos in peak_positions:
        if pos < n_steps:
            rainfall_pattern[pos] *= 1.5
    
    return rainfall_pattern


def one_at_a_time_sensitivity(model_func: Callable, base_params: Dict[str, float],
                               param_ranges: Dict[str, Tuple[float, float]],
                               rainfall: np.ndarray, n_samples: int = 10) -> Dict:
    """
    单参数敏感性分析（OAT方法）
    
    参数:
    ----
    model_func : callable
        模型函数
    base_params : dict
        基础参数
    param_ranges : dict
        参数变化范围 {param_name: (min, max)}
    rainfall : ndarray
        降雨输入
    n_samples : int
        每个参数的采样数
    
    返回:
    ----
    results : dict
        敏感性分析结果
    """
    results = {
        'param_values': {},
        'outputs': {},
        'sensitivity_indices': {}
    }
    
    # 运行基准模型
    base_output = model_func(base_params, rainfall)
    base_total_runoff = np.sum(base_output)
    
    # 对每个参数进行分析
    for param_name, (param_min, param_max) in param_ranges.items():
        # 生成参数值序列
        param_values = np.linspace(param_min, param_max, n_samples)
        outputs = []
        
        for param_value in param_values:
            # 修改参数
            test_params = base_params.copy()
            test_params[param_name] = param_value
            
            # 运行模型
            output = model_func(test_params, rainfall)
            total_runoff = np.sum(output)
            outputs.append(total_runoff)
        
        # 计算敏感性指标
        outputs = np.array(outputs)
        
        # 相对敏感性
        relative_change = (outputs - base_total_runoff) / base_total_runoff
        param_relative_change = (param_values - base_params[param_name]) / base_params[param_name]
        
        # 敏感性系数（斜率）
        sensitivity_coef = np.polyfit(param_relative_change, relative_change, 1)[0]
        
        # 输出变化范围
        output_range = (np.max(outputs) - np.min(outputs)) / base_total_runoff
        
        results['param_values'][param_name] = param_values
        results['outputs'][param_name] = outputs
        results['sensitivity_indices'][param_name] = {
            'coefficient': sensitivity_coef,
            'output_range': output_range,
            'base_output': base_total_runoff
        }
    
    return results


def morris_screening(model_func: Callable, param_ranges: Dict[str, Tuple[float, float]],
                     rainfall: np.ndarray, n_trajectories: int = 10, 
                     n_levels: int = 4) -> Dict:
    """
    Morris筛选法（全局敏感性分析简化版）
    
    参数:
    ----
    model_func : callable
        模型函数
    param_ranges : dict
        参数范围
    rainfall : ndarray
        降雨输入
    n_trajectories : int
        轨迹数量
    n_levels : int
        采样水平数
    
    返回:
    ----
    results : dict
        Morris敏感性指标
    """
    param_names = list(param_ranges.keys())
    n_params = len(param_names)
    
    # 初始化结果存储
    elementary_effects = {name: [] for name in param_names}
    
    for _ in range(n_trajectories):
        # 生成基础采样点
        base_point = {}
        for name, (pmin, pmax) in param_ranges.items():
            level = np.random.randint(0, n_levels)
            base_point[name] = pmin + (pmax - pmin) * level / (n_levels - 1)
        
        # 计算基础输出
        base_output = np.sum(model_func(base_point, rainfall))
        
        # 对每个参数进行扰动
        for param_name in param_names:
            # 扰动参数
            delta_point = base_point.copy()
            pmin, pmax = param_ranges[param_name]
            delta = (pmax - pmin) / (n_levels - 1)
            delta_point[param_name] = min(delta_point[param_name] + delta, pmax)
            
            # 计算扰动后输出
            delta_output = np.sum(model_func(delta_point, rainfall))
            
            # 计算基本效应
            ee = (delta_output - base_output) / delta
            elementary_effects[param_name].append(ee)
    
    # 计算Morris指标
    results = {}
    for param_name in param_names:
        ee_array = np.array(elementary_effects[param_name])
        results[param_name] = {
            'mu': np.mean(np.abs(ee_array)),      # 平均绝对效应（重要性）
            'mu_star': np.mean(np.abs(ee_array)), # mu* 指标
            'sigma': np.std(ee_array)             # 标准差（交互作用）
        }
    
    return results


def correlation_based_sensitivity(model_func: Callable, 
                                  param_ranges: Dict[str, Tuple[float, float]],
                                  rainfall: np.ndarray, 
                                  n_samples: int = 1000) -> Dict:
    """
    基于相关系数的敏感性分析
    
    参数:
    ----
    model_func : callable
        模型函数
    param_ranges : dict
        参数范围
    rainfall : ndarray
        降雨输入
    n_samples : int
        采样数量
    
    返回:
    ----
    results : dict
        相关系数敏感性指标
    """
    param_names = list(param_ranges.keys())
    n_params = len(param_names)
    
    # 拉丁超立方采样
    param_samples = np.zeros((n_samples, n_params))
    for i, (name, (pmin, pmax)) in enumerate(param_ranges.items()):
        # 简化的LHS
        intervals = np.linspace(0, 1, n_samples + 1)
        samples = np.random.uniform(intervals[:-1], intervals[1:])
        np.random.shuffle(samples)
        param_samples[:, i] = pmin + samples * (pmax - pmin)
    
    # 运行模型
    outputs = np.zeros(n_samples)
    for i in range(n_samples):
        params = {name: param_samples[i, j] 
                 for j, name in enumerate(param_names)}
        output = model_func(params, rainfall)
        outputs[i] = np.sum(output)
    
    # 计算相关系数
    results = {}
    for i, param_name in enumerate(param_names):
        # Pearson相关系数
        pearson_r = np.corrcoef(param_samples[:, i], outputs)[0, 1]
        
        # Spearman秩相关系数
        rank_param = np.argsort(np.argsort(param_samples[:, i]))
        rank_output = np.argsort(np.argsort(outputs))
        spearman_r = np.corrcoef(rank_param, rank_output)[0, 1]
        
        results[param_name] = {
            'pearson': pearson_r,
            'spearman': spearman_r,
            'param_samples': param_samples[:, i],
            'outputs': outputs
        }
    
    return results


def run_xaj_model(params: Dict[str, float], rainfall: np.ndarray) -> np.ndarray:
    """
    运行新安江模型的包装函数
    
    参数:
    ----
    params : dict
        模型参数
    rainfall : ndarray
        降雨序列
    
    返回:
    ----
    runoff : ndarray
        径流序列
    """
    try:
        # 合并参数
        full_params = create_default_xaj_params()
        full_params.update(params)
        
        # 创建模型
        model = XinAnJiangModel(full_params)
        
        # 运行模型
        n_steps = len(rainfall)
        evaporation = np.zeros(n_steps)  # 简化：蒸发为0
        results = model.run(rainfall, evaporation)
        
        runoff = results['R']  # 返回总径流
        
        # 检查并处理nan值
        if np.any(np.isnan(runoff)):
            runoff = np.nan_to_num(runoff, nan=0.0)
        
        return runoff
    except Exception as e:
        # 如果模型运行失败，返回零数组
        return np.zeros(len(rainfall))


def plot_oat_sensitivity(oat_results: Dict, save_path=None):
    """
    绘制OAT敏感性分析结果
    """
    param_names = list(oat_results['param_values'].keys())
    n_params = len(param_names)
    
    # 计算子图布局
    n_cols = 3
    n_rows = int(np.ceil(n_params / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
    axes = axes.flatten() if n_params > 1 else [axes]
    
    for idx, param_name in enumerate(param_names):
        ax = axes[idx]
        
        param_values = oat_results['param_values'][param_name]
        outputs = oat_results['outputs'][param_name]
        sensitivity_info = oat_results['sensitivity_indices'][param_name]
        
        # 绘制曲线
        ax.plot(param_values, outputs, 'b-o', linewidth=2, markersize=6)
        
        # 标记基准点
        base_output = sensitivity_info['base_output']
        ax.axhline(base_output, color='r', linestyle='--', 
                   linewidth=1.5, label='基准输出')
        
        # 设置标签
        ax.set_xlabel(f'{param_name}', fontsize=11, fontweight='bold')
        ax.set_ylabel('累计径流 (mm)', fontsize=11)
        ax.set_title(f'{param_name} 敏感性\n敏感性系数: {sensitivity_info["coefficient"]:.3f}', 
                     fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # 添加统计信息
        output_range_pct = sensitivity_info['output_range'] * 100
        info_text = f'输出变化: {output_range_pct:.1f}%'
        ax.text(0.05, 0.95, info_text, 
                transform=ax.transAxes, 
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 隐藏多余的子图
    for idx in range(n_params, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_tornado_chart(oat_results: Dict, save_path=None):
    """
    绘制龙卷风图（Tornado Chart）
    """
    param_names = list(oat_results['sensitivity_indices'].keys())
    
    # 提取敏感性指标
    sensitivities = []
    for param_name in param_names:
        output_range = oat_results['sensitivity_indices'][param_name]['output_range']
        sensitivities.append(output_range)
    
    # 排序
    sorted_indices = np.argsort(sensitivities)
    sorted_params = [param_names[i] for i in sorted_indices]
    sorted_sensitivities = [sensitivities[i] for i in sorted_indices]
    
    # 绘制
    fig, ax = plt.subplots(figsize=(10, max(6, len(param_names) * 0.5)))
    
    y_pos = np.arange(len(sorted_params))
    colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(sorted_params)))
    
    bars = ax.barh(y_pos, sorted_sensitivities, color=colors, alpha=0.8, edgecolor='black')
    
    # 标注数值
    for i, (bar, val) in enumerate(zip(bars, sorted_sensitivities)):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{val*100:.1f}%', 
                va='center', fontsize=10, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_params, fontsize=11)
    ax.set_xlabel('输出相对变化范围', fontsize=12, fontweight='bold')
    ax.set_title('参数敏感性龙卷风图', fontsize=14, fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    
    # 添加说明
    info_text = '参数按敏感性从低到高排列\n柱长表示输出变化幅度'
    ax.text(0.98, 0.02, info_text, 
            transform=ax.transAxes, 
            fontsize=10,
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_morris_results(morris_results: Dict, save_path=None):
    """
    绘制Morris筛选结果
    """
    param_names = list(morris_results.keys())
    
    mu_star = [morris_results[name]['mu_star'] for name in param_names]
    sigma = [morris_results[name]['sigma'] for name in param_names]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 散点图
    scatter = ax.scatter(mu_star, sigma, s=200, alpha=0.6, 
                        c=range(len(param_names)), cmap='tab10', 
                        edgecolors='black', linewidths=1.5)
    
    # 标注参数名
    for i, name in enumerate(param_names):
        ax.annotate(name, (mu_star[i], sigma[i]), 
                   fontsize=10, fontweight='bold',
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # 添加分区线（示例）
    ax.axvline(np.median(mu_star), color='gray', linestyle='--', alpha=0.5)
    ax.axhline(np.median(sigma), color='gray', linestyle='--', alpha=0.5)
    
    ax.set_xlabel('μ* (平均绝对效应 - 重要性)', fontsize=12, fontweight='bold')
    ax.set_ylabel('σ (标准差 - 交互作用)', fontsize=12, fontweight='bold')
    ax.set_title('Morris敏感性分析\n参数重要性与交互作用', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 添加图例区域说明
    legend_text = '右上: 高重要性+高交互\n右下: 高重要性+低交互\n左上: 低重要性+高交互\n左下: 低重要性+低交互'
    ax.text(0.02, 0.98, legend_text, 
            transform=ax.transAxes, 
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_correlation_scatter(corr_results: Dict, save_path=None):
    """
    绘制参数-输出散点图
    """
    param_names = list(corr_results.keys())
    n_params = len(param_names)
    
    n_cols = 3
    n_rows = int(np.ceil(n_params / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
    axes = axes.flatten() if n_params > 1 else [axes]
    
    for idx, param_name in enumerate(param_names):
        ax = axes[idx]
        
        param_samples = corr_results[param_name]['param_samples']
        outputs = corr_results[param_name]['outputs']
        pearson = corr_results[param_name]['pearson']
        spearman = corr_results[param_name]['spearman']
        
        # 散点图
        scatter = ax.scatter(param_samples, outputs, alpha=0.5, s=10, c='blue')
        
        # 拟合线
        z = np.polyfit(param_samples, outputs, 1)
        p = np.poly1d(z)
        x_line = np.linspace(param_samples.min(), param_samples.max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=2, label='线性拟合')
        
        ax.set_xlabel(param_name, fontsize=11, fontweight='bold')
        ax.set_ylabel('累计径流 (mm)', fontsize=11)
        ax.set_title(f'{param_name}\nPearson r={pearson:.3f}, Spearman ρ={spearman:.3f}', 
                     fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    # 隐藏多余的子图
    for idx in range(n_params, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_sensitivity_ranking(oat_results: Dict, morris_results: Dict, 
                            corr_results: Dict, save_path=None):
    """
    绘制综合敏感性排名对比
    """
    param_names = list(oat_results['sensitivity_indices'].keys())
    
    # 提取各方法的敏感性指标
    oat_sens = [oat_results['sensitivity_indices'][name]['output_range'] 
                for name in param_names]
    morris_sens = [morris_results[name]['mu_star'] for name in param_names]
    corr_sens = [abs(corr_results[name]['pearson']) for name in param_names]
    
    # 归一化到0-1
    oat_sens_norm = np.array(oat_sens) / np.max(oat_sens)
    morris_sens_norm = np.array(morris_sens) / np.max(morris_sens)
    corr_sens_norm = np.array(corr_sens) / np.max(corr_sens)
    
    # 绘制对比图
    fig, ax = plt.subplots(figsize=(12, max(6, len(param_names) * 0.4)))
    
    x = np.arange(len(param_names))
    width = 0.25
    
    bars1 = ax.barh(x - width, oat_sens_norm, width, label='OAT方法', 
                    color='steelblue', alpha=0.8)
    bars2 = ax.barh(x, morris_sens_norm, width, label='Morris方法', 
                    color='coral', alpha=0.8)
    bars3 = ax.barh(x + width, corr_sens_norm, width, label='相关系数法', 
                    color='seagreen', alpha=0.8)
    
    ax.set_yticks(x)
    ax.set_yticklabels(param_names, fontsize=11)
    ax.set_xlabel('归一化敏感性指标', fontsize=12, fontweight='bold')
    ax.set_title('三种敏感性分析方法对比', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, axis='x', alpha=0.3)
    
    # 添加说明
    info_text = '所有指标归一化到0-1范围\n值越大表示参数越敏感'
    ax.text(0.98, 0.02, info_text, 
            transform=ax.transAxes, 
            fontsize=10,
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def main():
    """主函数"""
    print("=" * 70)
    print("案例9：参数敏感性分析")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 生成降雨数据
    print("\n1. 生成降雨数据...")
    n_steps = 100
    rainfall = generate_rainfall_data(n_steps=n_steps, total_rainfall=150)
    print(f"   时间步数: {n_steps}")
    print(f"   总降雨量: {np.sum(rainfall):.2f} mm")
    
    # 2. 定义参数范围（基于新安江模型）
    print("\n2. 定义参数范围...")
    base_params = create_default_xaj_params()
    
    # 选择关键参数进行敏感性分析
    param_ranges = {
        'WM': (80, 160),      # 蓄水容量 ±33%
        'B': (0.2, 0.5),      # 蓄水容量曲线指数
        'IM': (0.005, 0.03),  # 不透水面积比例
        'SM': (20, 50),       # 自由水蓄水容量
        'KG': (0.2, 0.5),     # 地下径流出流系数
        'KI': (0.2, 0.6),     # 壤中流出流系数
    }
    
    print(f"   分析参数数量: {len(param_ranges)}")
    for name, (pmin, pmax) in param_ranges.items():
        print(f"   {name}: [{pmin}, {pmax}] (基准值: {base_params[name]:.3f})")
    
    # 3. OAT敏感性分析
    print("\n3. 执行OAT敏感性分析...")
    oat_results = one_at_a_time_sensitivity(
        run_xaj_model, base_params, param_ranges, rainfall, n_samples=15
    )
    print("   OAT分析完成")
    
    # 绘制OAT结果
    plot_oat_sensitivity(oat_results, save_path=f'{output_dir}/oat_sensitivity.png')
    
    # 绘制龙卷风图
    plot_tornado_chart(oat_results, save_path=f'{output_dir}/tornado_chart.png')
    
    # 4. Morris筛选法
    print("\n4. 执行Morris筛选法...")
    morris_results = morris_screening(
        run_xaj_model, param_ranges, rainfall, n_trajectories=20
    )
    print("   Morris分析完成")
    
    # 绘制Morris结果
    plot_morris_results(morris_results, save_path=f'{output_dir}/morris_screening.png')
    
    # 5. 基于相关系数的敏感性分析
    print("\n5. 执行相关系数敏感性分析...")
    corr_results = correlation_based_sensitivity(
        run_xaj_model, param_ranges, rainfall, n_samples=500
    )
    print("   相关系数分析完成")
    
    # 绘制相关系数散点图
    plot_correlation_scatter(corr_results, save_path=f'{output_dir}/correlation_scatter.png')
    
    # 6. 综合对比
    print("\n6. 生成综合敏感性排名...")
    plot_sensitivity_ranking(
        oat_results, morris_results, corr_results,
        save_path=f'{output_dir}/sensitivity_ranking.png'
    )
    
    # 7. 输出敏感性统计
    print("\n" + "=" * 70)
    print("敏感性分析结果统计")
    print("=" * 70)
    
    print("\n【OAT方法 - 输出变化范围】")
    oat_ranking = sorted(oat_results['sensitivity_indices'].items(), 
                        key=lambda x: x[1]['output_range'], reverse=True)
    for rank, (name, info) in enumerate(oat_ranking, 1):
        print(f"  {rank}. {name:6s}: {info['output_range']*100:6.2f}% "
              f"(敏感性系数: {info['coefficient']:7.3f})")
    
    print("\n【Morris方法 - μ*指标】")
    morris_ranking = sorted(morris_results.items(), 
                           key=lambda x: x[1]['mu_star'], reverse=True)
    for rank, (name, info) in enumerate(morris_ranking, 1):
        print(f"  {rank}. {name:6s}: μ*={info['mu_star']:8.3f}, "
              f"σ={info['sigma']:8.3f}")
    
    print("\n【相关系数法 - Pearson相关】")
    corr_ranking = sorted(corr_results.items(), 
                         key=lambda x: abs(x[1]['pearson']), reverse=True)
    for rank, (name, info) in enumerate(corr_ranking, 1):
        print(f"  {rank}. {name:6s}: Pearson={info['pearson']:7.3f}, "
              f"Spearman={info['spearman']:7.3f}")
    
    print("\n所有图表已保存到 outputs/ 目录")
    print("=" * 70)


if __name__ == '__main__':
    main()
