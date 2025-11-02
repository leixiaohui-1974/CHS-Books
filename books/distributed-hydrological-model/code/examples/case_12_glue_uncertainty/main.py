"""
案例12：GLUE不确定性分析
========================

使用GLUE（Generalized Likelihood Uncertainty Estimation）方法
进行参数和预测不确定性分析。

核心内容：
1. GLUE方法原理
2. 蒙特卡洛参数采样
3. 行为参数集识别
4. 不确定性区间估计
5. 参数后验分布分析

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
from core.calibration.glue import GLUE

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def generate_observed_data(n_days: int = 365):
    """生成观测数据"""
    np.random.seed(42)
    
    # 真实参数
    true_params = {
        'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.15,
        'WM': 120.0, 'B': 0.35, 'IM': 0.02,
        'SM': 30.0, 'EX': 1.5, 'KG': 0.4, 'KI': 0.3,
        'CG': 0.98, 'CI': 0.6, 'CS': 0.8
    }
    
    # 生成降雨
    rainfall = np.zeros(n_days)
    flood_days = [50, 120, 200, 280]
    for day in flood_days:
        for i in range(5):
            if day + i < n_days:
                rainfall[day + i] = 50.0 * np.exp(-0.5 * i)
    
    # 生成蒸散发
    day_of_year = np.arange(n_days)
    EM = 3.0 + 2.0 * np.sin(2 * np.pi * day_of_year / 365)
    
    # 运行模型
    model = XinAnJiangModel(true_params)
    results = model.run(rainfall, EM)
    
    # 添加误差
    observed = results['R'] + np.random.normal(0, 0.5, n_days)
    observed = np.maximum(observed, 0)
    observed = np.nan_to_num(observed, nan=0.0)
    
    return rainfall, EM, observed, true_params


def plot_parameter_distributions(result, param_names, true_params=None,
                                 save_path=None):
    """绘制参数后验分布"""
    n_params = len(param_names)
    fig, axes = plt.subplots(n_params, 2, figsize=(14, 4*n_params))
    
    if n_params == 1:
        axes = axes.reshape(1, -1)
    
    behavioral_params = result['behavioral_params']
    all_params = result['param_samples']
    
    for i, param_name in enumerate(param_names):
        # 左图：散点图
        ax_scatter = axes[i, 0]
        
        # 非行为参数
        non_behavioral = all_params[~result['behavioral_mask']]
        ax_scatter.scatter(non_behavioral[:, i],
                          result['performance'][~result['behavioral_mask']],
                          c='lightgray', alpha=0.3, s=10, label='非行为')
        
        # 行为参数
        ax_scatter.scatter(behavioral_params[:, i],
                          result['behavioral_performance'],
                          c=result['behavioral_performance'],
                          cmap='viridis', alpha=0.6, s=20, label='行为')
        
        if true_params and param_name in true_params:
            ax_scatter.axvline(true_params[param_name], color='r',
                              linestyle='--', linewidth=2, label='真值')
        
        ax_scatter.set_xlabel(param_name, fontsize=12, fontweight='bold')
        ax_scatter.set_ylabel('NSE', fontsize=11)
        ax_scatter.legend(fontsize=9)
        ax_scatter.grid(True, alpha=0.3)
        
        # 右图：直方图
        ax_hist = axes[i, 1]
        
        ax_hist.hist(all_params[:, i], bins=50, alpha=0.3,
                    color='gray', label='所有样本', density=True)
        ax_hist.hist(behavioral_params[:, i], bins=30, alpha=0.7,
                    color='blue', label='行为样本', density=True)
        
        if true_params and param_name in true_params:
            ax_hist.axvline(true_params[param_name], color='r',
                           linestyle='--', linewidth=2, label='真值')
        
        ax_hist.set_xlabel(param_name, fontsize=12, fontweight='bold')
        ax_hist.set_ylabel('概率密度', fontsize=11)
        ax_hist.legend(fontsize=9)
        ax_hist.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('参数后验分布分析', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_uncertainty_bands(time, observed, uncertainty_bands,
                          rainfall=None, save_path=None):
    """绘制不确定性区间"""
    fig, axes = plt.subplots(2 if rainfall is not None else 1, 1,
                            figsize=(14, 10 if rainfall is not None else 7))
    
    if rainfall is None:
        axes = [axes]
    else:
        # 降雨图
        ax_rain = axes[0].twinx()
        ax_rain.bar(time, rainfall, color='lightblue', alpha=0.5, label='降雨')
        ax_rain.set_ylim([max(rainfall)*2, 0])
        ax_rain.set_ylabel('降雨 (mm)', fontsize=11)
        ax_rain.legend(loc='upper right', fontsize=9)
        axes = [axes[1]]
    
    ax = axes[0]
    
    # 不确定性区间
    if 'P5' in uncertainty_bands and 'P95' in uncertainty_bands:
        ax.fill_between(time, uncertainty_bands['P5'], uncertainty_bands['P95'],
                        color='lightblue', alpha=0.3, label='90%置信区间')
    
    if 'P25' in uncertainty_bands and 'P75' in uncertainty_bands:
        ax.fill_between(time, uncertainty_bands['P25'], uncertainty_bands['P75'],
                        color='blue', alpha=0.3, label='50%置信区间')
    
    # 中位数
    if 'P50' in uncertainty_bands:
        ax.plot(time, uncertainty_bands['P50'], 'b-', linewidth=2,
               label='中位数模拟', alpha=0.8)
    
    # 观测值
    ax.plot(time, observed, 'k-', linewidth=2, label='观测径流', alpha=0.8)
    
    ax.set_xlabel('时间 (天)', fontsize=12)
    ax.set_ylabel('径流 (mm)', fontsize=12)
    ax.set_title('GLUE不确定性区间', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_behavioral_ratio(result, save_path=None):
    """绘制行为参数集比例"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    categories = ['非行为', '行为']
    counts = [
        len(result['param_samples']) - result['n_behavioral'],
        result['n_behavioral']
    ]
    colors = ['lightgray', 'green']
    
    wedges, texts, autotexts = ax.pie(counts, labels=categories,
                                       autopct='%1.1f%%', colors=colors,
                                       startangle=90, textprops={'fontsize': 12})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    ax.set_title(f'行为参数集比例\n(总样本: {len(result["param_samples"])})',
                fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def main():
    """主函数"""
    print("\n" + "="*70)
    print("案例12：GLUE不确定性分析")
    print("="*70 + "\n")
    
    # 创建输出目录
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # ========== 1. 生成观测数据 ==========
    print("1. 生成观测数据")
    print("-" * 70)
    
    n_days = 365
    rainfall, EM, observed, true_params = generate_observed_data(n_days)
    
    print(f"数据长度: {n_days} 天")
    print(f"总降雨: {np.sum(rainfall):.1f} mm")
    print(f"总径流: {np.sum(observed):.1f} mm\n")
    
    # ========== 2. 设置GLUE分析 ==========
    print("2. 设置GLUE分析")
    print("-" * 70)
    
    # 待分析参数
    param_names = ['WM', 'B']
    bounds = [(80, 200), (0.1, 0.5)]
    
    # 固定其他参数
    fixed_params = {k: v for k, v in true_params.items()
                   if k not in param_names}
    
    print(f"分析参数: {param_names}")
    print(f"参数边界:")
    for name, (lower, upper) in zip(param_names, bounds):
        print(f"  {name}: [{lower}, {upper}]")
    print()
    
    # ========== 3. 定义模型和目标函数 ==========
    def model_func(params_array):
        """模型包装"""
        params = fixed_params.copy()
        for i, name in enumerate(param_names):
            params[name] = params_array[i]
        
        try:
            model = XinAnJiangModel(params)
            results = model.run(rainfall, EM)
            simulated = results['R']
            
            if np.any(np.isnan(simulated)):
                return np.zeros(len(observed))
            
            return simulated
        except:
            return np.zeros(len(observed))
    
    def objective_func(simulated):
        """NSE目标函数"""
        obs_mean = np.mean(observed)
        if obs_mean == 0:
            return -999
        
        numerator = np.sum((observed - simulated) ** 2)
        denominator = np.sum((observed - obs_mean) ** 2)
        
        if denominator < 1e-10:
            return -999
        
        nse = 1.0 - numerator / denominator
        return max(nse, -10.0)
    
    # ========== 4. 执行GLUE分析 ==========
    print("3. 执行GLUE分析")
    print("-" * 70)
    
    glue = GLUE(
        model_func=model_func,
        objective_func=objective_func,
        bounds=bounds,
        behavioral_threshold=0.6,  # NSE > 0.6为行为参数集
        n_samples=2000  # 2000个样本
    )
    
    result = glue.run(sampling_method='lhs', verbose=True)
    
    # ========== 5. 结果分析 ==========
    print("\n4. 结果统计")
    print("-" * 70)
    
    print(f"总采样数: {len(result['param_samples'])}")
    print(f"行为参数集: {result['n_behavioral']}")
    print(f"行为比例: {result['behavioral_ratio']:.1f}%")
    print(f"最佳NSE: {np.max(result['performance']):.4f}")
    print(f"行为集NSE范围: [{np.min(result['behavioral_performance']):.4f}, "
          f"{np.max(result['behavioral_performance']):.4f}]")
    
    # 参数统计
    print(f"\n参数后验统计:")
    for i, name in enumerate(param_names):
        behavioral_vals = result['behavioral_params'][:, i]
        print(f"  {name}:")
        print(f"    真值: {true_params[name]:.2f}")
        print(f"    后验均值: {np.mean(behavioral_vals):.2f} ± {np.std(behavioral_vals):.2f}")
        print(f"    后验中位数: {np.median(behavioral_vals):.2f}")
        print(f"    90%置信区间: [{np.percentile(behavioral_vals, 5):.2f}, "
              f"{np.percentile(behavioral_vals, 95):.2f}]")
    
    # ========== 6. 可视化 ==========
    print(f"\n5. 生成可视化图表")
    print("-" * 70)
    
    time = np.arange(n_days)
    
    plot_parameter_distributions(
        result, param_names, true_params,
        save_path=f'{output_dir}/parameter_distributions.png'
    )
    
    plot_uncertainty_bands(
        time, observed, result['uncertainty_bands'], rainfall,
        save_path=f'{output_dir}/uncertainty_bands.png'
    )
    
    plot_behavioral_ratio(
        result,
        save_path=f'{output_dir}/behavioral_ratio.png'
    )
    
    # ========== 7. 总结 ==========
    print("\n" + "="*70)
    print("GLUE不确定性分析结果")
    print("="*70)
    
    print(f"\n【分析设置】")
    print(f"  采样方法: 拉丁超立方")
    print(f"  采样数量: {len(result['param_samples'])}")
    print(f"  行为阈值: NSE > 0.6")
    print(f"  分析参数: {', '.join(param_names)}")
    
    print(f"\n【不确定性】")
    print(f"  行为参数集: {result['n_behavioral']} ({result['behavioral_ratio']:.1f}%)")
    print(f"  最佳NSE: {np.max(result['performance']):.4f}")
    
    print(f"\n所有图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
