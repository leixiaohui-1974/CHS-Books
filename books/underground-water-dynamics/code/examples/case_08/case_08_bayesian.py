"""
案例8：贝叶斯推断与MCMC

演示贝叶斯参数推断和不确定性量化：
1. 贝叶斯推断基本原理
2. Metropolis-Hastings MCMC采样
3. 后验分布估计
4. 预测不确定性
5. 与频率学派方法对比
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.solvers.steady_state import solve_1d_steady_gw
from gwflow.calibration.bayesian import (
    metropolis_hastings,
    compute_dic,
    predictive_distribution,
    log_posterior
)
from gwflow.calibration.optimization import levenberg_marquardt

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("案例8：贝叶斯推断与MCMC")
print("=" * 70)


# ============================================================================
# 第1步：定义问题和生成数据
# ============================================================================

def forward_model_1d(params: np.ndarray) -> np.ndarray:
    """一维稳态地下水流动正演模型"""
    K, h_left, h_right = params
    
    L = 1000.0
    nx = 100
    
    h = solve_1d_steady_gw(K=K, L=L, nx=nx, h_left=h_left, h_right=h_right)
    
    # 10个观测点
    obs_indices = np.linspace(10, 90, 10, dtype=int)
    return h[obs_indices]


print("\n1. 生成观测数据")
print("-" * 70)

# 真实参数
K_true = 10.0
h_left_true = 20.0
h_right_true = 10.0
params_true = np.array([K_true, h_left_true, h_right_true])

print(f"真实参数:")
print(f"  K = {K_true:.2f} m/day")
print(f"  h_left = {h_left_true:.2f} m")
print(f"  h_right = {h_right_true:.2f} m")

# 生成观测数据
np.random.seed(42)
h_true = forward_model_1d(params_true)
sigma_obs = 0.1  # 观测误差标准差
noise = np.random.normal(0, sigma_obs, len(h_true))
h_observed = h_true + noise

print(f"\n观测点数量: {len(h_observed)}")
print(f"观测误差标准差: {sigma_obs:.2f} m")


# ============================================================================
# 第2步：贝叶斯推断 - MCMC采样
# ============================================================================

print("\n" + "=" * 70)
print("2. 贝叶斯推断 - MCMC采样")
print("=" * 70)

# 设置先验分布（均匀先验）
prior_params = {
    'bounds': [
        (1.0, 50.0),   # K
        (15.0, 30.0),  # h_left
        (5.0, 15.0)    # h_right
    ]
}

# 初始参数（随机选择）
initial_params = np.array([15.0, 22.0, 12.0])

print(f"\n先验分布: 均匀分布")
print(f"  K ∈ [1, 50] m/day")
print(f"  h_left ∈ [15, 30] m")
print(f"  h_right ∈ [5, 15] m")

print(f"\n初始参数:")
print(f"  K = {initial_params[0]:.2f} m/day")
print(f"  h_left = {initial_params[1]:.2f} m")
print(f"  h_right = {initial_params[2]:.2f} m")

# 运行MCMC
print("\n开始MCMC采样...")
mcmc_result = metropolis_hastings(
    forward_model=forward_model_1d,
    initial_params=initial_params,
    observations=h_observed,
    sigma=sigma_obs,
    prior_type='uniform',
    prior_params=prior_params,
    n_iterations=20000,
    proposal_std=np.array([0.5, 0.2, 0.2]),
    burn_in=5000,
    thin=10,
    verbose=True
)


# ============================================================================
# 第3步：频率学派方法对比
# ============================================================================

print("\n" + "=" * 70)
print("3. 频率学派方法对比（Levenberg-Marquardt）")
print("=" * 70)

# 使用L-M方法
result_lm = levenberg_marquardt(
    forward_model=forward_model_1d,
    initial_params=initial_params,
    observed=h_observed,
    max_iterations=30,
    tolerance=1e-6,
    bounds=prior_params['bounds'],
    verbose=False
)

print(f"\n点估计结果:")
print(f"  K = {result_lm['parameters'][0]:.4f} m/day")
print(f"  h_left = {result_lm['parameters'][1]:.4f} m")
print(f"  h_right = {result_lm['parameters'][2]:.4f} m")


# ============================================================================
# 第4步：后验分析
# ============================================================================

print("\n" + "=" * 70)
print("4. 后验分析")
print("=" * 70)

# 计算DIC
print("\n计算DIC（偏差信息准则）...")
dic_result = compute_dic(
    chain=mcmc_result['chain_burned'],
    forward_model=forward_model_1d,
    observations=h_observed,
    sigma=sigma_obs
)

print(f"  DIC = {dic_result['DIC']:.2f}")
print(f"  D_bar = {dic_result['D_bar']:.2f}")
print(f"  p_D = {dic_result['p_D']:.2f} (有效参数数)")

# 预测分布
print("\n计算预测分布...")
predictions = predictive_distribution(
    chain=mcmc_result['chain_burned'],
    forward_model=forward_model_1d,
    sigma=sigma_obs,
    n_samples=1000
)

pred_mean = np.mean(predictions, axis=0)
pred_std = np.std(predictions, axis=0)
pred_ci_lower = np.percentile(predictions, 2.5, axis=0)
pred_ci_upper = np.percentile(predictions, 97.5, axis=0)

print(f"  生成了 {len(predictions)} 个预测样本")


# ============================================================================
# 第5步：可视化
# ============================================================================

print("\n" + "=" * 70)
print("5. 生成可视化图表")
print("=" * 70)

# 图1：MCMC链迹图
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

param_names = ['K (m/day)', 'h_left (m)', 'h_right (m)']
true_values = params_true

for i, (ax, name, true_val) in enumerate(zip(axes, param_names, true_values)):
    # 绘制完整链
    ax.plot(mcmc_result['chain'][:, i], 'b-', alpha=0.5, linewidth=0.5)
    # 标记燃烧期
    ax.axvline(mcmc_result['burn_in'], color='r', linestyle='--', 
              label='燃烧期结束', linewidth=2)
    # 真值
    ax.axhline(true_val, color='g', linestyle=':', label='真值', linewidth=2)
    # 后验均值
    ax.axhline(mcmc_result['posterior_mean'][i], color='k', linestyle='--',
              label='后验均值', linewidth=2)
    
    ax.set_ylabel(name)
    ax.set_xlabel('迭代次数')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

axes[0].set_title('MCMC链迹图（Trace Plot）')
plt.tight_layout()
plt.savefig('case_08_trace_plots.png', dpi=300, bbox_inches='tight')
print("已保存: case_08_trace_plots.png")
plt.close()

# 图2：后验分布直方图
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for i, (ax, name, true_val) in enumerate(zip(axes, param_names, true_values)):
    # 后验样本直方图
    ax.hist(mcmc_result['chain_burned'][:, i], bins=50, density=True,
           alpha=0.7, color='steelblue', edgecolor='black')
    
    # 真值
    ax.axvline(true_val, color='green', linestyle=':', linewidth=3, label='真值')
    
    # 后验均值
    ax.axvline(mcmc_result['posterior_mean'][i], color='red', linestyle='--',
              linewidth=2, label='后验均值')
    
    # L-M估计
    ax.axvline(result_lm['parameters'][i], color='orange', linestyle='-.',
              linewidth=2, label='L-M估计')
    
    # 95% 置信区间
    ax.axvline(mcmc_result['posterior_ci_lower'][i], color='gray', 
              linestyle=':', linewidth=1.5)
    ax.axvline(mcmc_result['posterior_ci_upper'][i], color='gray', 
              linestyle=':', linewidth=1.5, label='95% CI')
    
    ax.set_xlabel(name)
    ax.set_ylabel('概率密度')
    ax.legend()
    ax.grid(True, alpha=0.3)

axes[0].set_title('后验分布')
plt.tight_layout()
plt.savefig('case_08_posterior_distributions.png', dpi=300, bbox_inches='tight')
print("已保存: case_08_posterior_distributions.png")
plt.close()

# 图3：参数相关性（散点图矩阵）
fig, axes = plt.subplots(3, 3, figsize=(12, 12))

samples = mcmc_result['chain_burned']
labels = ['K', 'h_left', 'h_right']

for i in range(3):
    for j in range(3):
        ax = axes[i, j]
        
        if i == j:
            # 对角线：直方图
            ax.hist(samples[:, i], bins=30, alpha=0.7, color='steelblue',
                   edgecolor='black')
            ax.set_ylabel('频数')
        else:
            # 非对角线：散点图
            ax.scatter(samples[:, j], samples[:, i], alpha=0.3, s=1, color='steelblue')
            # 真值
            ax.plot(true_values[j], true_values[i], 'r*', markersize=15, label='真值')
            # 后验均值
            ax.plot(mcmc_result['posterior_mean'][j], mcmc_result['posterior_mean'][i],
                   'go', markersize=10, label='后验均值')
            ax.legend()
        
        if i == 2:
            ax.set_xlabel(labels[j])
        if j == 0:
            ax.set_ylabel(labels[i])
        
        ax.grid(True, alpha=0.3)

plt.suptitle('参数后验相关性')
plt.tight_layout()
plt.savefig('case_08_parameter_correlations.png', dpi=300, bbox_inches='tight')
print("已保存: case_08_parameter_correlations.png")
plt.close()

# 图4：预测不确定性
fig, ax = plt.subplots(figsize=(10, 6))

x_obs = np.arange(len(h_observed))

# 观测值
ax.scatter(x_obs, h_observed, color='black', s=100, zorder=5,
          label='观测值', marker='o')

# 真实值
ax.plot(x_obs, h_true, 'g--', linewidth=2, label='真实值', zorder=4)

# 预测均值
ax.plot(x_obs, pred_mean, 'b-', linewidth=2, label='预测均值（贝叶斯）', zorder=3)

# 95% 预测区间
ax.fill_between(x_obs, pred_ci_lower, pred_ci_upper, alpha=0.3, color='blue',
                label='95% 预测区间')

# L-M拟合
h_lm = forward_model_1d(result_lm['parameters'])
ax.plot(x_obs, h_lm, 'r-.', linewidth=2, label='L-M拟合', zorder=3)

ax.set_xlabel('观测点索引')
ax.set_ylabel('水头 (m)')
ax.set_title('预测不确定性量化')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_08_prediction_uncertainty.png', dpi=300, bbox_inches='tight')
print("已保存: case_08_prediction_uncertainty.png")
plt.close()

# 图5：对数后验历史
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(mcmc_result['log_posterior'], 'b-', linewidth=0.5, alpha=0.7)
ax.axvline(mcmc_result['burn_in'], color='r', linestyle='--',
          label='燃烧期结束', linewidth=2)
ax.set_xlabel('迭代次数')
ax.set_ylabel('对数后验概率')
ax.set_title('对数后验历史')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_08_log_posterior_history.png', dpi=300, bbox_inches='tight')
print("已保存: case_08_log_posterior_history.png")
plt.close()


# ============================================================================
# 第6步：方法对比总结
# ============================================================================

print("\n" + "=" * 70)
print("6. 贝叶斯 vs 频率学派方法对比")
print("=" * 70)

print(f"\n{'参数':<15} {'真值':<10} {'贝叶斯均值':<15} {'贝叶斯95%CI':<25} {'L-M估计':<10}")
print("-" * 85)

for i, name in enumerate(['K', 'h_left', 'h_right']):
    ci_str = f"[{mcmc_result['posterior_ci_lower'][i]:.4f}, {mcmc_result['posterior_ci_upper'][i]:.4f}]"
    print(f"{name:<15} {true_values[i]:<10.4f} {mcmc_result['posterior_mean'][i]:<15.4f} "
          f"{ci_str:<25} {result_lm['parameters'][i]:<10.4f}")

print("\n方法特点:")
print("\n贝叶斯推断（MCMC）:")
print("  ✅ 完整的后验分布")
print("  ✅ 自然的不确定性量化")
print("  ✅ 置信区间直观")
print("  ✅ 可融合先验信息")
print("  ❌ 计算成本高")
print("  ❌ 需要调节MCMC参数")

print("\n频率学派（L-M）:")
print("  ✅ 计算快速")
print("  ✅ 点估计精确")
print("  ✅ 易于实现")
print("  ❌ 不确定性量化复杂")
print("  ❌ 需要额外计算置信区间")
print("  ❌ 依赖渐近理论")

print(f"\nMCMC诊断:")
print(f"  接受率: {mcmc_result['acceptance_rate']:.3f}")
print(f"  （推荐：0.2-0.5为最优）")
print(f"  有效样本数: {mcmc_result['n_effective_samples']}")

print("\n" + "=" * 70)
print("案例8完成！")
print("=" * 70)
print("\n输出文件:")
print("  1. case_08_trace_plots.png - MCMC链迹图")
print("  2. case_08_posterior_distributions.png - 后验分布")
print("  3. case_08_parameter_correlations.png - 参数相关性")
print("  4. case_08_prediction_uncertainty.png - 预测不确定性")
print("  5. case_08_log_posterior_history.png - 对数后验历史")
