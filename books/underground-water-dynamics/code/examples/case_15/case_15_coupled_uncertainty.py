"""
案例15：耦合系统不确定性分析

本案例演示如何量化和分析地表地下水耦合系统的预测不确定性。

演示内容：
---------
1. 耦合系统不确定性来源分析
2. Monte Carlo不确定性传播
3. GLUE方法（行为参数集）
4. 预测区间估计
5. 不同方法对比

物理场景：
---------
二维地下水系统 + 河流：
- 含水层参数不确定性
- 河流参数不确定性  
- 预测地下水水位和河流交换通量
- 量化预测不确定性

学习目标：
---------
1. 理解耦合系统不确定性来源
2. 应用Monte Carlo方法
3. 实现GLUE方法
4. 估计预测区间
5. 对比不同不确定性方法
6. 评估预测可靠性

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats

# 导入gwflow模块
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.coupling import RiverPackage
from gwflow.calibration import monte_carlo_uncertainty, glue_analysis

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def setup_model():
    """设置耦合模型"""
    print("\n" + "="*60)
    print("设置耦合模型")
    print("="*60)
    
    params = {
        'Lx': 2000.0,
        'Ly': 1500.0,
        'nx': 41,
        'ny': 31,
        'b': 25.0,
        'recharge': 0.0003,
        'h_west': 35.0,
        'h_east': 30.0,
        'h_north': 33.0,
        'h_south': 32.0,
    }
    
    params['dx'] = params['Lx'] / (params['nx'] - 1)
    params['dy'] = params['Ly'] / (params['ny'] - 1)
    params['x'] = np.linspace(0, params['Lx'], params['nx'])
    params['y'] = np.linspace(0, params['Ly'], params['ny'])
    params['cell_area'] = params['dx'] * params['dy']
    
    print(f"\n模型设置：")
    print(f"  区域: {params['Lx']}m × {params['Ly']}m")
    print(f"  网格: {params['nx']} × {params['ny']}")
    
    return params


def solve_coupled_model(params, K, river_conductance):
    """求解耦合模型（简化版）"""
    nx, ny = params['nx'], params['ny']
    
    # 创建河流
    riv = RiverPackage()
    river_row = ny // 2
    
    for col in range(nx):
        riv.add_river_cell(
            layer=0, row=river_row, col=col,
            stage=33.0,
            conductance=river_conductance,
            bottom=25.0
        )
    
    # 初始水头
    h = np.ones((ny, nx)) * 32.0
    
    # 边界条件
    h[:, 0] = params['h_west']
    h[:, -1] = params['h_east']
    h[0, :] = params['h_south']
    h[-1, :] = params['h_north']
    
    # 弱耦合迭代（简化）
    dx, dy = params['dx'], params['dy']
    b = params['b']
    cell_volume = params['cell_area'] * b
    
    for _ in range(20):
        river_source = riv.apply_flux_to_source(
            head=h,
            cell_volume=np.ones((ny, nx)) * cell_volume,
            use_disconnection=True
        )
        
        total_source = params['recharge'] + river_source
        
        h_new = h.copy()
        for _ in range(5):
            for i in range(1, ny-1):
                for j in range(1, nx-1):
                    h_new[i, j] = (
                        (h_new[i+1, j] + h_new[i-1, j]) / dy**2 +
                        (h_new[i, j+1] + h_new[i, j-1]) / dx**2 +
                        total_source[i, j] / (K * b)
                    ) / (2/dx**2 + 2/dy**2)
        
        h = h_new
        h[:, 0] = params['h_west']
        h[:, -1] = params['h_east']
        h[0, :] = params['h_south']
        h[-1, :] = params['h_north']
    
    # 计算河流通量
    river_flux = riv.get_total_flux(h, use_disconnection=True)
    
    return h, river_flux


def monte_carlo_analysis(params, n_samples=1000):
    """
    Monte Carlo不确定性分析
    """
    print("\n" + "="*60)
    print("Monte Carlo不确定性分析")
    print("="*60)
    
    print(f"\n采样数: {n_samples}")
    
    # 参数不确定性定义（正态分布）
    K_mean, K_std = 20.0, 3.0
    C_mean, C_std = 1200.0, 200.0
    
    print(f"\n参数分布：")
    print(f"  K ~ N({K_mean}, {K_std}²) m/day")
    print(f"  河流传导度 ~ N({C_mean}, {C_std}²) m²/day")
    
    # Monte Carlo采样
    np.random.seed(42)
    K_samples = np.random.normal(K_mean, K_std, n_samples)
    C_samples = np.random.normal(C_mean, C_std, n_samples)
    
    # 参数约束（物理合理范围）
    K_samples = np.clip(K_samples, 5.0, 50.0)
    C_samples = np.clip(C_samples, 300.0, 3000.0)
    
    # 预测点
    predict_points = [
        (15, 20, '点A'),
        (20, 15, '点B'),
        (10, 25, '点C')
    ]
    
    # 存储结果
    h_predictions = {name: [] for _, _, name in predict_points}
    flux_predictions = []
    
    print(f"\n开始Monte Carlo模拟...")
    
    for i in range(n_samples):
        if i % 200 == 0:
            print(f"  进度: {i}/{n_samples}")
        
        K = K_samples[i]
        C = C_samples[i]
        
        try:
            h, flux = solve_coupled_model(params, K, C)
            
            # 提取预测点水头
            for row, col, name in predict_points:
                h_predictions[name].append(h[row, col])
            
            flux_predictions.append(flux)
        
        except:
            # 如果求解失败，跳过
            continue
    
    print(f"\n完成! 成功模拟: {len(flux_predictions)}/{n_samples}")
    
    # 转换为数组
    for name in h_predictions:
        h_predictions[name] = np.array(h_predictions[name])
    flux_predictions = np.array(flux_predictions)
    
    # 统计分析
    print(f"\n预测统计：")
    for row, col, name in predict_points:
        h_pred = h_predictions[name]
        print(f"\n{name} ({row}, {col}):")
        print(f"  均值: {np.mean(h_pred):.2f} m")
        print(f"  标准差: {np.std(h_pred):.2f} m")
        print(f"  95%CI: [{np.percentile(h_pred, 2.5):.2f}, {np.percentile(h_pred, 97.5):.2f}] m")
    
    print(f"\n河流通量:")
    print(f"  均值: {np.mean(flux_predictions):.2f} m³/day")
    print(f"  标准差: {np.std(flux_predictions):.2f} m³/day")
    print(f"  95%CI: [{np.percentile(flux_predictions, 2.5):.2f}, {np.percentile(flux_predictions, 97.5):.2f}] m³/day")
    
    return {
        'K_samples': K_samples,
        'C_samples': C_samples,
        'h_predictions': h_predictions,
        'flux_predictions': flux_predictions,
        'predict_points': predict_points
    }


def glue_analysis_method(params, mc_result, observations_synthetic):
    """
    GLUE（Generalized Likelihood Uncertainty Estimation）分析
    """
    print("\n" + "="*60)
    print("GLUE方法分析")
    print("="*60)
    
    # 从Monte Carlo结果中识别行为参数集
    K_samples = mc_result['K_samples']
    C_samples = mc_result['C_samples']
    flux_predictions = mc_result['flux_predictions']
    
    # 合成观测值（假设真实）
    flux_obs = observations_synthetic['flux']
    
    print(f"\n观测河流通量: {flux_obs:.2f} m³/day")
    print(f"\n定义似然函数...")
    
    # 似然函数（基于河流通量）
    residuals = flux_predictions - flux_obs
    sigma = 100.0  # 观测误差标准差
    likelihoods = np.exp(-0.5 * (residuals / sigma)**2)
    
    # 归一化
    likelihoods = likelihoods / np.sum(likelihoods)
    
    # 定义阈值（前10%为行为参数集）
    threshold = np.percentile(likelihoods, 90)
    behavioral_mask = likelihoods >= threshold
    
    n_behavioral = np.sum(behavioral_mask)
    
    print(f"\n似然阈值: {threshold:.6f}")
    print(f"行为参数集数量: {n_behavioral}/{len(K_samples)}")
    print(f"行为参数集比例: {n_behavioral/len(K_samples)*100:.1f}%")
    
    # 行为参数集统计
    K_behavioral = K_samples[behavioral_mask]
    C_behavioral = C_samples[behavioral_mask]
    
    print(f"\n行为参数集范围：")
    print(f"  K: [{np.min(K_behavioral):.2f}, {np.max(K_behavioral):.2f}] m/day")
    print(f"  河流传导度: [{np.min(C_behavioral):.2f}, {np.max(C_behavioral):.2f}] m²/day")
    
    # GLUE预测区间（行为参数集）
    flux_behavioral = flux_predictions[behavioral_mask]
    
    print(f"\nGLUE预测区间（河流通量）：")
    print(f"  5%-95%: [{np.percentile(flux_behavioral, 5):.2f}, {np.percentile(flux_behavioral, 95):.2f}] m³/day")
    
    return {
        'likelihoods': likelihoods,
        'behavioral_mask': behavioral_mask,
        'K_behavioral': K_behavioral,
        'C_behavioral': C_behavioral,
        'flux_behavioral': flux_behavioral,
        'threshold': threshold
    }


def prediction_interval_analysis(mc_result):
    """
    预测区间分析
    """
    print("\n" + "="*60)
    print("预测区间分析")
    print("="*60)
    
    flux_predictions = mc_result['flux_predictions']
    
    # 不同置信水平
    confidence_levels = [50, 68, 90, 95, 99]
    
    print(f"\n河流通量预测区间：")
    print(f"{'置信水平':<10} {'下界':<15} {'上界':<15} {'区间宽度':<15}")
    print("-" * 60)
    
    intervals = {}
    
    for cl in confidence_levels:
        alpha = (100 - cl) / 2
        lower = np.percentile(flux_predictions, alpha)
        upper = np.percentile(flux_predictions, 100 - alpha)
        width = upper - lower
        
        intervals[cl] = (lower, upper, width)
        
        print(f"{cl}%{'':<7} {lower:<15.2f} {upper:<15.2f} {width:<15.2f}")
    
    return intervals


def uncertainty_decomposition(params, mc_result):
    """
    不确定性分解
    
    将总不确定性分解为：
    1. K参数不确定性
    2. 河流传导度不确定性
    """
    print("\n" + "="*60)
    print("不确定性分解")
    print("="*60)
    
    K_mean = np.mean(mc_result['K_samples'])
    C_mean = np.mean(mc_result['C_samples'])
    
    # 1. 仅K变化
    print(f"\n计算仅K参数不确定性...")
    flux_K_only = []
    K_samples_subset = np.random.choice(mc_result['K_samples'], 200)
    
    for K in K_samples_subset:
        try:
            _, flux = solve_coupled_model(params, K, C_mean)
            flux_K_only.append(flux)
        except:
            pass
    
    flux_K_only = np.array(flux_K_only)
    var_K = np.var(flux_K_only)
    
    # 2. 仅C变化
    print(f"计算仅河流参数不确定性...")
    flux_C_only = []
    C_samples_subset = np.random.choice(mc_result['C_samples'], 200)
    
    for C in C_samples_subset:
        try:
            _, flux = solve_coupled_model(params, K_mean, C)
            flux_C_only.append(flux)
        except:
            pass
    
    flux_C_only = np.array(flux_C_only)
    var_C = np.var(flux_C_only)
    
    # 总方差
    var_total = np.var(mc_result['flux_predictions'])
    
    # 交互方差
    var_interaction = var_total - var_K - var_C
    
    print(f"\n方差分解：")
    print(f"  K贡献: {var_K:.2f} ({var_K/var_total*100:.1f}%)")
    print(f"  河流传导度贡献: {var_C:.2f} ({var_C/var_total*100:.1f}%)")
    print(f"  交互作用: {var_interaction:.2f} ({var_interaction/var_total*100:.1f}%)")
    print(f"  总方差: {var_total:.2f}")
    
    return {
        'var_K': var_K,
        'var_C': var_C,
        'var_interaction': var_interaction,
        'var_total': var_total,
        'flux_K_only': flux_K_only,
        'flux_C_only': flux_C_only
    }


def plot_results(params, mc_result, glue_result, intervals, decomp_result):
    """绘制结果"""
    
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # 图1: 参数采样分布
    ax1 = fig.add_subplot(gs[0, 0])
    
    K_samples = mc_result['K_samples']
    C_samples = mc_result['C_samples']
    
    ax1.scatter(K_samples, C_samples, alpha=0.3, s=20, c='blue', label='全部')
    
    # 标记行为参数集
    behavioral_mask = glue_result['behavioral_mask']
    ax1.scatter(K_samples[behavioral_mask], C_samples[behavioral_mask],
               alpha=0.6, s=40, c='red', label='行为参数集')
    
    ax1.set_xlabel('K (m/day)', fontsize=11)
    ax1.set_ylabel('河流传导度 (m²/day)', fontsize=11)
    ax1.set_title('参数空间采样', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 河流通量预测分布
    ax2 = fig.add_subplot(gs[0, 1])
    
    flux_pred = mc_result['flux_predictions']
    
    ax2.hist(flux_pred, bins=50, alpha=0.6, color='skyblue', edgecolor='black',
            label='Monte Carlo')
    ax2.hist(glue_result['flux_behavioral'], bins=30, alpha=0.6, color='orange',
            edgecolor='black', label='GLUE行为集')
    
    # 均值线
    ax2.axvline(np.mean(flux_pred), color='blue', linestyle='--', linewidth=2,
               label=f'MC均值: {np.mean(flux_pred):.0f}')
    ax2.axvline(np.mean(glue_result['flux_behavioral']), color='red',
               linestyle='--', linewidth=2,
               label=f'GLUE均值: {np.mean(glue_result["flux_behavioral"]):.0f}')
    
    ax2.set_xlabel('河流通量 (m³/day)', fontsize=11)
    ax2.set_ylabel('频数', fontsize=11)
    ax2.set_title('河流通量预测分布', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 图3: 预测区间对比
    ax3 = fig.add_subplot(gs[0, 2])
    
    cl_levels = list(intervals.keys())
    widths_mc = [intervals[cl][2] for cl in cl_levels]
    
    ax3.plot(cl_levels, widths_mc, 'o-', linewidth=2, markersize=8,
            color='blue', label='Monte Carlo')
    
    ax3.set_xlabel('置信水平 (%)', fontsize=11)
    ax3.set_ylabel('预测区间宽度 (m³/day)', fontsize=11)
    ax3.set_title('预测区间宽度 vs 置信水平', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 地下水水头预测（点A）
    ax4 = fig.add_subplot(gs[1, 0])
    
    point_name = mc_result['predict_points'][0][2]
    h_pred = mc_result['h_predictions'][point_name]
    
    ax4.hist(h_pred, bins=40, alpha=0.7, color='lightgreen', edgecolor='black')
    ax4.axvline(np.mean(h_pred), color='red', linestyle='--', linewidth=2,
               label=f'均值: {np.mean(h_pred):.2f}m')
    
    # 95%CI
    ci_lower = np.percentile(h_pred, 2.5)
    ci_upper = np.percentile(h_pred, 97.5)
    ax4.axvline(ci_lower, color='orange', linestyle=':', linewidth=2)
    ax4.axvline(ci_upper, color='orange', linestyle=':', linewidth=2, 
               label=f'95%CI: [{ci_lower:.2f}, {ci_upper:.2f}]')
    
    ax4.set_xlabel('水头 (m)', fontsize=11)
    ax4.set_ylabel('频数', fontsize=11)
    ax4.set_title(f'{point_name}水头预测分布', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 图5: 不同预测点的不确定性
    ax5 = fig.add_subplot(gs[1, 1])
    
    point_names = [name for _, _, name in mc_result['predict_points']]
    means = [np.mean(mc_result['h_predictions'][name]) for name in point_names]
    stds = [np.std(mc_result['h_predictions'][name]) for name in point_names]
    
    x_pos = np.arange(len(point_names))
    ax5.bar(x_pos, means, yerr=stds, alpha=0.7, color='lightblue',
           edgecolor='black', capsize=5, error_kw={'linewidth': 2})
    
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(point_names)
    ax5.set_ylabel('水头 (m)', fontsize=11)
    ax5.set_title('不同预测点的水头（均值±标准差）', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 图6: GLUE似然分布
    ax6 = fig.add_subplot(gs[1, 2])
    
    likelihoods = glue_result['likelihoods']
    threshold = glue_result['threshold']
    
    ax6.hist(likelihoods, bins=50, alpha=0.7, color='purple', edgecolor='black')
    ax6.axvline(threshold, color='red', linestyle='--', linewidth=2,
               label=f'阈值: {threshold:.4e}')
    
    ax6.set_xlabel('似然值', fontsize=11)
    ax6.set_ylabel('频数', fontsize=11)
    ax6.set_title('GLUE似然分布', fontsize=13, fontweight='bold')
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3, axis='y')
    ax6.set_yscale('log')
    
    # 图7: 不确定性分解（饼图）
    ax7 = fig.add_subplot(gs[2, 0])
    
    var_K = decomp_result['var_K']
    var_C = decomp_result['var_C']
    var_interaction = max(decomp_result['var_interaction'], 0)  # 确保非负
    
    sizes = [var_K, var_C, var_interaction]
    labels = ['K参数', '河流传导度', '交互作用']
    colors = ['skyblue', 'lightcoral', 'lightgreen']
    explode = (0.05, 0.05, 0.05)
    
    ax7.pie(sizes, explode=explode, labels=labels, colors=colors,
           autopct='%1.1f%%', shadow=True, startangle=90)
    ax7.set_title('不确定性来源分解', fontsize=13, fontweight='bold')
    
    # 图8: 分别仅变化一个参数的通量分布
    ax8 = fig.add_subplot(gs[2, 1])
    
    flux_K_only = decomp_result['flux_K_only']
    flux_C_only = decomp_result['flux_C_only']
    
    ax8.hist(flux_K_only, bins=30, alpha=0.6, color='skyblue',
            edgecolor='black', label='仅K变化')
    ax8.hist(flux_C_only, bins=30, alpha=0.6, color='lightcoral',
            edgecolor='black', label='仅C变化')
    
    ax8.set_xlabel('河流通量 (m³/day)', fontsize=11)
    ax8.set_ylabel('频数', fontsize=11)
    ax8.set_title('单参数不确定性贡献', fontsize=13, fontweight='bold')
    ax8.legend(fontsize=10)
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 图9: 累积分布函数（CDF）
    ax9 = fig.add_subplot(gs[2, 2])
    
    # Monte Carlo CDF
    flux_sorted_mc = np.sort(flux_pred)
    cdf_mc = np.arange(1, len(flux_sorted_mc)+1) / len(flux_sorted_mc)
    
    ax9.plot(flux_sorted_mc, cdf_mc, linewidth=2, label='Monte Carlo', color='blue')
    
    # GLUE CDF
    flux_sorted_glue = np.sort(glue_result['flux_behavioral'])
    cdf_glue = np.arange(1, len(flux_sorted_glue)+1) / len(flux_sorted_glue)
    
    ax9.plot(flux_sorted_glue, cdf_glue, linewidth=2, label='GLUE', color='red',
            linestyle='--')
    
    # 标记关键百分位数
    for p in [5, 50, 95]:
        val = np.percentile(flux_pred, p)
        ax9.axvline(val, color='gray', linestyle=':', alpha=0.5)
        ax9.text(val, 0.5, f'P{p}', rotation=90, va='center', fontsize=8)
    
    ax9.set_xlabel('河流通量 (m³/day)', fontsize=11)
    ax9.set_ylabel('累积概率', fontsize=11)
    ax9.set_title('累积分布函数（CDF）', fontsize=13, fontweight='bold')
    ax9.legend(fontsize=10)
    ax9.grid(True, alpha=0.3)
    
    plt.savefig('case_15_coupled_uncertainty_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_15_coupled_uncertainty_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例15：耦合系统不确定性分析")
    print("="*60)
    print("\n本案例演示耦合系统的不确定性量化方法")
    print("包括：Monte Carlo、GLUE、预测区间、不确定性分解")
    
    # 1. 设置模型
    params = setup_model()
    
    # 2. Monte Carlo分析
    mc_result = monte_carlo_analysis(params, n_samples=200)
    
    # 3. GLUE分析
    observations_synthetic = {
        'flux': 8500.0  # 合成观测值
    }
    glue_result = glue_analysis_method(params, mc_result, observations_synthetic)
    
    # 4. 预测区间
    intervals = prediction_interval_analysis(mc_result)
    
    # 5. 不确定性分解
    decomp_result = uncertainty_decomposition(params, mc_result)
    
    # 6. 绘图
    print("\n生成结果图...")
    plot_results(params, mc_result, glue_result, intervals, decomp_result)
    
    # 7. 总结
    print("\n" + "="*60)
    print("案例15完成总结")
    print("="*60)
    
    print(f"\n核心发现：")
    print(f"1. Monte Carlo有效量化参数不确定性")
    print(f"2. GLUE识别了{np.sum(glue_result['behavioral_mask'])}个行为参数集")
    print(f"3. 95%预测区间宽度约{intervals[95][2]:.0f} m³/day")
    print(f"4. K参数贡献{decomp_result['var_K']/decomp_result['var_total']*100:.1f}%不确定性")
    print(f"5. 河流参数贡献{decomp_result['var_C']/decomp_result['var_total']*100:.1f}%不确定性")
    
    print(f"\n学习要点：")
    print(f"✓ 不确定性来源识别")
    print(f"✓ Monte Carlo方法应用")
    print(f"✓ GLUE方法实现")
    print(f"✓ 预测区间估计")
    print(f"✓ 不确定性分解")
    print(f"✓ 方法对比分析")
    
    print("\n✅ 案例15执行完成！")
    print("\n🎉🎉🎉 第三篇全部完成！🎉🎉🎉")


if __name__ == '__main__':
    main()
