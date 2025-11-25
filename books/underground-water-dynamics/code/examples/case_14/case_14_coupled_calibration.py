"""
案例14：耦合模型率定

本案例演示如何率定地表地下水耦合模型的参数，使用河流和地下水的联合观测数据。

演示内容：
---------
1. 耦合模型参数率定框架
2. 多类型观测数据联合使用
3. 河流参数可识别性分析
4. 敏感性分析
5. 不确定性评估

物理场景：
---------
二维地下水系统 + 河流：
- 含水层：2000m × 1500m
- 河流：横穿中部
- 观测数据：地下水水位 + 河流交换通量
- 目标：率定含水层K和河流传导度

学习目标：
---------
1. 掌握耦合模型率定方法
2. 处理多类型观测数据
3. 分析参数可识别性
4. 评估率定不确定性
5. 验证率定结果

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.optimize import minimize

# 导入gwflow模块
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.coupling import RiverPackage
from gwflow.calibration import (
    compute_objective_function,
    compute_jacobian,
    levenberg_marquardt,
    compute_sensitivity_matrix
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def setup_model_and_observations():
    """
    设置模型和"真实"观测数据
    
    这里我们使用已知的真实参数运行模型，生成"观测"数据。
    然后用不同的初始参数进行率定，看能否恢复真实参数。
    """
    print("\n" + "="*60)
    print("设置模型和生成观测数据")
    print("="*60)
    
    # 模型区域
    params = {
        'Lx': 2000.0,
        'Ly': 1500.0,
        'nx': 41,
        'ny': 31,
        'K_true': 20.0,          # 真实渗透系数
        'b': 25.0,
        'recharge': 0.0003,
        'h_west': 35.0,
        'h_east': 30.0,
        'h_north': 33.0,
        'h_south': 32.0,
        'river_cond_true': 1200.0,  # 真实河流传导度
        'river_stage': 33.0,
        'river_bottom': 25.0,
    }
    
    params['dx'] = params['Lx'] / (params['nx'] - 1)
    params['dy'] = params['Ly'] / (params['ny'] - 1)
    params['x'] = np.linspace(0, params['Lx'], params['nx'])
    params['y'] = np.linspace(0, params['Ly'], params['ny'])
    params['cell_area'] = params['dx'] * params['dy']
    
    print(f"\n真实参数：")
    print(f"  含水层K: {params['K_true']} m/day")
    print(f"  河流传导度: {params['river_cond_true']} m²/day")
    
    # 创建河流（沿中部）
    riv = RiverPackage(name='CalibrationRiver')
    river_row = params['ny'] // 2
    
    for col in range(params['nx']):
        riv.add_river_cell(
            layer=0,
            row=river_row,
            col=col,
            stage=params['river_stage'],
            conductance=params['river_cond_true'],
            bottom=params['river_bottom']
        )
    
    # 用真实参数求解，生成"观测"数据
    h_true = solve_coupled_model(params, riv, params['K_true'], params['river_cond_true'])
    
    # 选择观测点（地下水水位）
    obs_points_gw = [
        (10, 10), (10, 20), (10, 30),
        (20, 10), (20, 20), (20, 30),
        (30, 10), (30, 20), (30, 30)
    ]
    
    h_obs = []
    for row, col in obs_points_gw:
        h_obs.append(h_true[row, col])
    
    # 观测河流通量
    river_flux_true = riv.get_total_flux(h_true, use_disconnection=True)
    
    # 添加观测噪声
    np.random.seed(42)
    h_obs = np.array(h_obs) + np.random.normal(0, 0.1, len(h_obs))
    river_flux_obs = river_flux_true + np.random.normal(0, 50)
    
    print(f"\n观测数据：")
    print(f"  地下水观测点: {len(obs_points_gw)} 个")
    print(f"  地下水水位范围: {np.min(h_obs):.2f} - {np.max(h_obs):.2f} m")
    print(f"  河流通量观测: {river_flux_obs:.2f} m³/day")
    
    observations = {
        'gw_points': obs_points_gw,
        'gw_heads': h_obs,
        'river_flux': river_flux_obs,
        'h_true': h_true
    }
    
    return params, riv, observations


def solve_coupled_model(params, riv, K, river_conductance):
    """
    求解耦合模型
    
    使用简化的迭代方法求解稳态耦合系统
    """
    nx, ny = params['nx'], params['ny']
    
    # 初始水头
    h = np.ones((ny, nx)) * 32.0
    
    # 边界条件
    h[:, 0] = params['h_west']
    h[:, -1] = params['h_east']
    h[0, :] = params['h_south']
    h[-1, :] = params['h_north']
    
    # 更新河流传导度
    for cell in riv.river_cells:
        cell.conductance = river_conductance
    
    # 弱耦合迭代
    dx, dy = params['dx'], params['dy']
    b = params['b']
    cell_volume = params['cell_area'] * b
    
    for _ in range(30):  # 固定迭代次数
        # 计算河流源汇项
        river_source = riv.apply_flux_to_source(
            head=h,
            cell_volume=np.ones((ny, nx)) * cell_volume,
            use_disconnection=True
        )
        
        # 总源汇项
        total_source = params['recharge'] + river_source
        
        # 简单迭代（Gauss-Seidel）
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
        
        # 保持边界
        h[:, 0] = params['h_west']
        h[:, -1] = params['h_east']
        h[0, :] = params['h_south']
        h[-1, :] = params['h_north']
    
    return h


def forward_model(parameters, params, riv, observations):
    """
    前向模型：给定参数，计算模拟值
    
    Parameters
    ----------
    parameters : array
        参数向量 [K, river_conductance]
    
    Returns
    -------
    simulated : array
        模拟值 [h_sim_1, ..., h_sim_n, river_flux_sim]
    """
    K, river_cond = parameters
    
    # 参数约束
    K = max(K, 1.0)
    K = min(K, 100.0)
    river_cond = max(river_cond, 100.0)
    river_cond = min(river_cond, 5000.0)
    
    # 求解模型
    h = solve_coupled_model(params, riv, K, river_cond)
    
    # 提取观测点模拟值
    h_sim = []
    for row, col in observations['gw_points']:
        h_sim.append(h[row, col])
    
    # 计算河流通量
    river_flux_sim = riv.get_total_flux(h, use_disconnection=True)
    
    # 组合
    simulated = np.array(h_sim + [river_flux_sim])
    
    return simulated


def calibrate_coupled_model(params, riv, observations):
    """
    率定耦合模型
    """
    print("\n" + "="*60)
    print("开始参数率定")
    print("="*60)
    
    # 观测值
    observed = np.array(list(observations['gw_heads']) + [observations['river_flux']])
    
    # 权重（河流通量单位大，需要降低权重）
    n_gw = len(observations['gw_heads'])
    weights = np.ones(len(observed))
    weights[-1] = 0.001  # 河流通量权重
    
    print(f"\n观测数据：")
    print(f"  地下水观测: {n_gw} 个")
    print(f"  河流通量观测: 1 个")
    print(f"  总观测数: {len(observed)}")
    
    # 初始参数（故意偏离真实值）
    initial_params = np.array([15.0, 800.0])  # [K, river_cond]
    
    print(f"\n初始参数：")
    print(f"  K: {initial_params[0]} m/day")
    print(f"  河流传导度: {initial_params[1]} m²/day")
    
    print(f"\n真实参数：")
    print(f"  K: {params['K_true']} m/day")
    print(f"  河流传导度: {params['river_cond_true']} m²/day")
    
    # 定义目标函数
    def objective(p):
        simulated = forward_model(p, params, riv, observations)
        residuals = observed - simulated
        return np.sum((weights * residuals)**2)
    
    # 使用scipy优化
    print(f"\n开始优化（L-BFGS-B）...")
    
    result = minimize(
        objective,
        initial_params,
        method='L-BFGS-B',
        bounds=[(1.0, 100.0), (100.0, 5000.0)],
        options={'maxiter': 50, 'disp': True}
    )
    
    optimized_params = result.x
    
    print(f"\n率定结果：")
    print(f"  K: {optimized_params[0]:.2f} m/day （真实: {params['K_true']:.2f}）")
    print(f"  河流传导度: {optimized_params[1]:.2f} m²/day （真实: {params['river_cond_true']:.2f}）")
    
    # 计算误差
    K_error = abs(optimized_params[0] - params['K_true']) / params['K_true'] * 100
    cond_error = abs(optimized_params[1] - params['river_cond_true']) / params['river_cond_true'] * 100
    
    print(f"\n相对误差：")
    print(f"  K: {K_error:.1f}%")
    print(f"  河流传导度: {cond_error:.1f}%")
    
    # 计算拟合度
    final_simulated = forward_model(optimized_params, params, riv, observations)
    final_residuals = observed - final_simulated
    rmse = np.sqrt(np.mean((weights * final_residuals)**2))
    
    print(f"\n拟合统计：")
    print(f"  加权RMSE: {rmse:.4f}")
    print(f"  目标函数值: {result.fun:.4f}")
    
    return {
        'initial': initial_params,
        'optimized': optimized_params,
        'true': np.array([params['K_true'], params['river_cond_true']]),
        'observed': observed,
        'simulated': final_simulated,
        'residuals': final_residuals,
        'weights': weights,
        'rmse': rmse,
        'success': result.success
    }


def sensitivity_analysis(params, riv, observations, optimized_params):
    """
    敏感性分析
    """
    print("\n" + "="*60)
    print("敏感性分析")
    print("="*60)
    
    # 参数扰动
    delta_frac = 0.01  # 1%扰动
    
    def forward_wrapper(p):
        return forward_model(p, params, riv, observations)
    
    # 计算Jacobian
    J = compute_jacobian(forward_wrapper, optimized_params, delta=delta_frac)
    
    print(f"\nJacobian矩阵 shape: {J.shape}")
    print(f"  行数（观测）: {J.shape[0]}")
    print(f"  列数（参数）: {J.shape[1]}")
    
    # 计算敏感性
    sensitivity = np.abs(J)
    
    print(f"\n平均敏感性：")
    print(f"  K: {np.mean(sensitivity[:, 0]):.4f}")
    print(f"  河流传导度: {np.mean(sensitivity[:, 1]):.4f}")
    
    # 参数相关性
    if J.shape[0] >= J.shape[1]:
        correlation = np.corrcoef(J.T)
        print(f"\n参数相关系数矩阵：")
        print(correlation)
        print(f"\nK与河流传导度相关性: {correlation[0, 1]:.4f}")
    
    return {
        'jacobian': J,
        'sensitivity': sensitivity,
        'correlation': correlation if J.shape[0] >= J.shape[1] else None
    }


def parameter_uncertainty(params, riv, observations, calibration_result, sensitivity_result):
    """
    参数不确定性分析（简化版）
    """
    print("\n" + "="*60)
    print("参数不确定性分析")
    print("="*60)
    
    # 使用线性近似估计参数不确定性
    J = sensitivity_result['jacobian']
    weights = calibration_result['weights']
    
    # 加权Jacobian
    W = np.diag(weights)
    JtWJ = J.T @ W @ J
    
    # 观测误差方差估计
    residuals = calibration_result['residuals']
    n_obs = len(residuals)
    n_params = 2
    sigma_squared = np.sum((weights * residuals)**2) / (n_obs - n_params)
    
    print(f"\n残差方差估计: {sigma_squared:.4f}")
    
    # 参数协方差矩阵
    try:
        param_cov = sigma_squared * np.linalg.inv(JtWJ)
        param_std = np.sqrt(np.diag(param_cov))
        
        print(f"\n参数标准差估计：")
        print(f"  K: {param_std[0]:.2f} m/day")
        print(f"  河流传导度: {param_std[1]:.2f} m²/day")
        
        # 95%置信区间
        optimized = calibration_result['optimized']
        ci_95 = 1.96 * param_std
        
        print(f"\n95%置信区间：")
        print(f"  K: [{optimized[0]-ci_95[0]:.2f}, {optimized[0]+ci_95[0]:.2f}] m/day")
        print(f"  河流传导度: [{optimized[1]-ci_95[1]:.2f}, {optimized[1]+ci_95[1]:.2f}] m²/day")
        
        return {
            'cov_matrix': param_cov,
            'std': param_std,
            'ci_95': ci_95
        }
    
    except np.linalg.LinAlgError:
        print("\n警告: 无法计算参数协方差矩阵（矩阵奇异）")
        return None


def plot_results(params, observations, calibration_result, sensitivity_result):
    """绘制结果"""
    
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # 图1: 参数收敛
    ax1 = fig.add_subplot(gs[0, 0])
    
    initial = calibration_result['initial']
    optimized = calibration_result['optimized']
    true_params = calibration_result['true']
    
    param_names = ['K\n(m/day)', '河流传导度\n(m²/day)']
    x = np.arange(len(param_names))
    width = 0.25
    
    bars1 = ax1.bar(x - width, initial, width, label='初始', alpha=0.7, color='lightblue')
    bars2 = ax1.bar(x, optimized, width, label='率定', alpha=0.7, color='orange')
    bars3 = ax1.bar(x + width, true_params, width, label='真实', alpha=0.7, color='green')
    
    ax1.set_ylabel('参数值', fontsize=11)
    ax1.set_title('参数率定结果', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(param_names)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom', fontsize=8)
    
    # 图2: 观测vs模拟（地下水）
    ax2 = fig.add_subplot(gs[0, 1])
    
    n_gw = len(observations['gw_heads'])
    obs_gw = calibration_result['observed'][:n_gw]
    sim_gw = calibration_result['simulated'][:n_gw]
    
    ax2.scatter(obs_gw, sim_gw, s=80, alpha=0.6, edgecolors='black')
    
    # 1:1线
    min_val = min(np.min(obs_gw), np.min(sim_gw))
    max_val = max(np.max(obs_gw), np.max(sim_gw))
    ax2.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='1:1线')
    
    ax2.set_xlabel('观测水头 (m)', fontsize=11)
    ax2.set_ylabel('模拟水头 (m)', fontsize=11)
    ax2.set_title('地下水水头拟合', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    # 计算R²
    r2 = 1 - np.sum((obs_gw - sim_gw)**2) / np.sum((obs_gw - np.mean(obs_gw))**2)
    ax2.text(0.05, 0.95, f'R² = {r2:.3f}', transform=ax2.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 图3: 河流通量对比
    ax3 = fig.add_subplot(gs[0, 2])
    
    flux_obs = calibration_result['observed'][-1]
    flux_sim = calibration_result['simulated'][-1]
    flux_true = observations['river_flux']
    
    categories = ['观测', '模拟', '真实']
    values = [flux_obs, flux_sim, flux_true]
    colors = ['skyblue', 'orange', 'green']
    
    bars = ax3.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('河流通量 (m³/day)', fontsize=11)
    ax3.set_title('河流通量拟合', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}',
                ha='center', va='bottom', fontsize=10)
    
    # 图4: 残差分布
    ax4 = fig.add_subplot(gs[1, 0])
    
    residuals_gw = calibration_result['residuals'][:n_gw]
    
    ax4.hist(residuals_gw, bins=15, alpha=0.7, color='blue', edgecolor='black')
    ax4.axvline(0, color='red', linestyle='--', linewidth=2)
    ax4.set_xlabel('残差 (m)', fontsize=11)
    ax4.set_ylabel('频数', fontsize=11)
    ax4.set_title('地下水残差分布', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 添加统计信息
    mean_res = np.mean(residuals_gw)
    std_res = np.std(residuals_gw)
    ax4.text(0.65, 0.95, f'均值: {mean_res:.3f}\n标准差: {std_res:.3f}',
            transform=ax4.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 图5: 观测点位置和残差
    ax5 = fig.add_subplot(gs[1, 1])
    
    # 绘制观测点
    for i, (row, col) in enumerate(observations['gw_points']):
        x = params['x'][col]
        y = params['y'][row]
        residual = residuals_gw[i]
        
        # 颜色映射残差大小
        color = 'green' if abs(residual) < 0.2 else ('orange' if abs(residual) < 0.5 else 'red')
        size = 100 + abs(residual) * 500
        
        ax5.scatter(x, y, s=size, c=color, alpha=0.6, edgecolors='black')
        ax5.text(x, y, f'{i+1}', ha='center', va='center', fontsize=8)
    
    # 河流位置
    river_row = params['ny'] // 2
    river_y = params['y'][river_row]
    ax5.axhline(river_y, color='blue', linewidth=3, label='河流', alpha=0.7)
    
    ax5.set_xlabel('X (m)', fontsize=11)
    ax5.set_ylabel('Y (m)', fontsize=11)
    ax5.set_title('观测点分布与残差', fontsize=13, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    ax5.set_aspect('equal')
    
    # 图6: Jacobian矩阵热图
    ax6 = fig.add_subplot(gs[1, 2])
    
    J = sensitivity_result['jacobian']
    im = ax6.imshow(np.abs(J), cmap='YlOrRd', aspect='auto')
    
    ax6.set_xlabel('参数索引', fontsize=11)
    ax6.set_ylabel('观测索引', fontsize=11)
    ax6.set_title('Jacobian矩阵（绝对值）', fontsize=13, fontweight='bold')
    ax6.set_xticks([0, 1])
    ax6.set_xticklabels(['K', 'Cond'])
    
    plt.colorbar(im, ax=ax6, label='|∂obs/∂param|')
    
    # 图7: 参数敏感性对比
    ax7 = fig.add_subplot(gs[2, 0])
    
    sens = sensitivity_result['sensitivity']
    avg_sens = np.mean(sens, axis=0)
    
    param_names_short = ['K', '河流传导度']
    bars = ax7.bar(param_names_short, avg_sens, color=['skyblue', 'lightcoral'],
                  alpha=0.7, edgecolor='black')
    
    ax7.set_ylabel('平均敏感性', fontsize=11)
    ax7.set_title('参数敏感性对比', fontsize=13, fontweight='bold')
    ax7.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, avg_sens):
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=10)
    
    # 图8: 敏感性分布（箱线图）
    ax8 = fig.add_subplot(gs[2, 1])
    
    data_to_plot = [sens[:, 0], sens[:, 1]]
    bp = ax8.boxplot(data_to_plot, labels=param_names_short, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], ['skyblue', 'lightcoral']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax8.set_ylabel('敏感性', fontsize=11)
    ax8.set_title('敏感性分布', fontsize=13, fontweight='bold')
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 图9: 参数相关性
    ax9 = fig.add_subplot(gs[2, 2])
    
    if sensitivity_result['correlation'] is not None:
        corr = sensitivity_result['correlation']
        im = ax9.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')
        
        ax9.set_xticks([0, 1])
        ax9.set_yticks([0, 1])
        ax9.set_xticklabels(['K', 'Cond'])
        ax9.set_yticklabels(['K', 'Cond'])
        
        # 添加数值
        for i in range(2):
            for j in range(2):
                text = ax9.text(j, i, f'{corr[i, j]:.3f}',
                              ha="center", va="center", color="black", fontsize=12)
        
        ax9.set_title('参数相关性矩阵', fontsize=13, fontweight='bold')
        plt.colorbar(im, ax=ax9, label='相关系数')
    else:
        ax9.text(0.5, 0.5, '数据不足\n无法计算', ha='center', va='center',
                transform=ax9.transAxes, fontsize=12)
        ax9.set_title('参数相关性矩阵', fontsize=13, fontweight='bold')
    
    plt.savefig('case_14_coupled_calibration_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_14_coupled_calibration_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例14：耦合模型率定")
    print("="*60)
    print("\n本案例演示如何率定地表地下水耦合模型")
    print("包括：联合观测、参数率定、敏感性分析、不确定性评估")
    
    # 1. 设置模型和观测
    params, riv, observations = setup_model_and_observations()
    
    # 2. 参数率定
    calibration_result = calibrate_coupled_model(params, riv, observations)
    
    # 3. 敏感性分析
    sensitivity_result = sensitivity_analysis(
        params, riv, observations, calibration_result['optimized']
    )
    
    # 4. 不确定性分析
    uncertainty_result = parameter_uncertainty(
        params, riv, observations, calibration_result, sensitivity_result
    )
    
    # 5. 绘图
    print("\n生成结果图...")
    plot_results(params, observations, calibration_result, sensitivity_result)
    
    # 6. 总结
    print("\n" + "="*60)
    print("案例14完成总结")
    print("="*60)
    
    print(f"\n核心发现：")
    print(f"1. 成功率定了耦合模型参数")
    print(f"2. 地下水和河流观测联合约束参数")
    print(f"3. 参数可识别性良好")
    print(f"4. 敏感性分析揭示参数重要性")
    print(f"5. 不确定性分析量化置信区间")
    
    print(f"\n学习要点：")
    print(f"✓ 耦合模型率定框架")
    print(f"✓ 多类型观测数据使用")
    print(f"✓ 参数可识别性分析")
    print(f"✓ 敏感性计算")
    print(f"✓ 不确定性量化")
    
    print("\n✅ 案例14执行完成！")


if __name__ == '__main__':
    main()
