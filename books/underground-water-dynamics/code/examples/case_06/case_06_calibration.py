"""
案例6：参数率定基础（优化方法）

演示如何使用不同的优化算法进行地下水模型参数率定：
1. 生成合成观测数据
2. 使用梯度下降法率定
3. 使用Gauss-Newton法率定
4. 使用Levenberg-Marquardt法率定
5. 比较不同方法的性能
6. 敏感性分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys
import os

# 添加gwflow包路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.solvers.steady_state import solve_1d_steady_gw
from gwflow.calibration.optimization import (
    calibrate_parameters,
    compute_objective_function
)
from gwflow.calibration.sensitivity import (
    compute_sensitivity_matrix,
    compute_composite_sensitivity,
    compute_parameter_correlation
)

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("案例6：参数率定基础（优化方法）")
print("=" * 70)


# ============================================================================
# 第1步：定义正演模型和生成观测数据
# ============================================================================

def forward_model_1d(params: np.ndarray) -> np.ndarray:
    """
    一维稳态地下水流动正演模型
    
    Parameters
    ----------
    params : np.ndarray
        参数数组 [K, h_left, h_right]
        
    Returns
    -------
    np.ndarray
        模拟的水头值（在观测点位置）
    """
    K, h_left, h_right = params
    
    # 求解1D稳态问题
    L = 1000.0  # 区域长度 (m)
    nx = 100    # 网格数
    
    h = solve_1d_steady_gw(
        K=K,
        L=L,
        h0=h_left,
        hL=h_right,
        nx=nx
    )
    
    # 在观测点位置提取模拟值
    # 假设在10个均匀分布的观测点
    obs_indices = np.linspace(10, 90, 10, dtype=int)
    h_obs_locations = h[obs_indices]
    
    return h_obs_locations


print("\n1. 生成合成观测数据")
print("-" * 70)

# 真实参数（我们要反演得到的）
K_true = 10.0      # m/day
h_left_true = 20.0  # m
h_right_true = 10.0 # m
params_true = np.array([K_true, h_left_true, h_right_true])

print(f"真实参数:")
print(f"  K = {K_true:.2f} m/day")
print(f"  h_left = {h_left_true:.2f} m")
print(f"  h_right = {h_right_true:.2f} m")

# 生成合成观测数据（添加噪声）
np.random.seed(42)
h_observed = forward_model_1d(params_true)
noise_level = 0.05  # 5%噪声
noise = np.random.normal(0, noise_level * np.mean(h_observed), len(h_observed))
h_observed_noisy = h_observed + noise

print(f"\n生成了 {len(h_observed_noisy)} 个观测点")
print(f"噪声水平: {noise_level*100:.1f}%")
print(f"观测水头范围: [{h_observed_noisy.min():.2f}, {h_observed_noisy.max():.2f}] m")


# ============================================================================
# 第2步：使用不同方法进行参数率定
# ============================================================================

print("\n" + "=" * 70)
print("2. 参数率定")
print("=" * 70)

# 初始猜测（故意偏离真值）
K_init = 5.0
h_left_init = 25.0
h_right_init = 8.0
params_init = np.array([K_init, h_left_init, h_right_init])

print(f"\n初始参数:")
print(f"  K = {K_init:.2f} m/day")
print(f"  h_left = {h_left_init:.2f} m")
print(f"  h_right = {h_right_init:.2f} m")

# 参数边界
bounds = [
    (1.0, 50.0),   # K: 1-50 m/day
    (15.0, 30.0),  # h_left: 15-30 m
    (5.0, 15.0)    # h_right: 5-15 m
]

# 方法1：梯度下降法
print("\n" + "-" * 70)
print("方法1：梯度下降法")
print("-" * 70)

result_gd = calibrate_parameters(
    forward_model_1d,
    params_init.copy(),
    h_observed_noisy,
    method='gradient-descent',
    learning_rate=0.005,
    max_iterations=200,
    tolerance=1e-6,
    bounds=bounds,
    verbose=False
)

print(f"迭代次数: {result_gd['iterations']}")
print(f"收敛: {'是' if result_gd['success'] else '否'}")
print(f"最终目标函数: {result_gd['objective']:.6e}")
print(f"率定结果:")
print(f"  K = {result_gd['parameters'][0]:.2f} m/day (真值: {K_true:.2f})")
print(f"  h_left = {result_gd['parameters'][1]:.2f} m (真值: {h_left_true:.2f})")
print(f"  h_right = {result_gd['parameters'][2]:.2f} m (真值: {h_right_true:.2f})")

# 方法2：Gauss-Newton法
print("\n" + "-" * 70)
print("方法2：Gauss-Newton法")
print("-" * 70)

result_gn = calibrate_parameters(
    forward_model_1d,
    params_init.copy(),
    h_observed_noisy,
    method='gauss-newton',
    max_iterations=50,
    tolerance=1e-6,
    bounds=bounds,
    verbose=False
)

print(f"迭代次数: {result_gn['iterations']}")
print(f"收敛: {'是' if result_gn['success'] else '否'}")
print(f"最终目标函数: {result_gn['objective']:.6e}")
print(f"率定结果:")
print(f"  K = {result_gn['parameters'][0]:.2f} m/day (真值: {K_true:.2f})")
print(f"  h_left = {result_gn['parameters'][1]:.2f} m (真值: {h_left_true:.2f})")
print(f"  h_right = {result_gn['parameters'][2]:.2f} m (真值: {h_right_true:.2f})")

# 方法3：Levenberg-Marquardt法
print("\n" + "-" * 70)
print("方法3：Levenberg-Marquardt法")
print("-" * 70)

result_lm = calibrate_parameters(
    forward_model_1d,
    params_init.copy(),
    h_observed_noisy,
    method='levenberg-marquardt',
    max_iterations=50,
    tolerance=1e-6,
    lambda_init=0.01,
    bounds=bounds,
    verbose=False
)

print(f"迭代次数: {result_lm['iterations']}")
print(f"收敛: {'是' if result_lm['success'] else '否'}")
print(f"最终目标函数: {result_lm['objective']:.6e}")
print(f"率定结果:")
print(f"  K = {result_lm['parameters'][0]:.2f} m/day (真值: {K_true:.2f})")
print(f"  h_left = {result_lm['parameters'][1]:.2f} m (真值: {h_left_true:.2f})")
print(f"  h_right = {result_lm['parameters'][2]:.2f} m (真值: {h_right_true:.2f})")


# ============================================================================
# 第3步：敏感性分析
# ============================================================================

print("\n" + "=" * 70)
print("3. 敏感性分析")
print("=" * 70)

# 使用率定后的参数计算敏感性
params_calibrated = result_lm['parameters']

sensitivity_matrix = compute_sensitivity_matrix(
    forward_model_1d,
    params_calibrated,
    method='forward'
)

print(f"\n敏感性矩阵形状: {sensitivity_matrix.shape}")
print(f"(观测点数 × 参数数)")

# 复合敏感性
composite_sens = compute_composite_sensitivity(sensitivity_matrix)
print(f"\n复合敏感性:")
print(f"  K: {composite_sens[0]:.6f}")
print(f"  h_left: {composite_sens[1]:.6f}")
print(f"  h_right: {composite_sens[2]:.6f}")

# 参数相关性
correlation_matrix = compute_parameter_correlation(sensitivity_matrix)
print(f"\n参数相关性矩阵:")
print(correlation_matrix)


# ============================================================================
# 第4步：可视化
# ============================================================================

print("\n" + "=" * 70)
print("4. 生成可视化图表")
print("=" * 70)

# 图1：收敛历史对比
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# 目标函数历史
ax = axes[0]
ax.semilogy(result_gd['history']['objective'], 'b-', label='Gradient Descent', linewidth=2)
ax.semilogy(result_gn['history']['objective'], 'r--', label='Gauss-Newton', linewidth=2)
ax.semilogy(result_lm['history']['objective'], 'g-.', label='Levenberg-Marquardt', linewidth=2)
ax.set_xlabel('迭代次数')
ax.set_ylabel('目标函数值')
ax.set_title('收敛历史对比')
ax.legend()
ax.grid(True, alpha=0.3)

# 参数收敛 - K
ax = axes[1]
gd_K = [p[0] for p in result_gd['history']['parameters']]
gn_K = [p[0] for p in result_gn['history']['parameters']]
lm_K = [p[0] for p in result_lm['history']['parameters']]
ax.plot(gd_K, 'b-', label='Gradient Descent', linewidth=2)
ax.plot(gn_K, 'r--', label='Gauss-Newton', linewidth=2)
ax.plot(lm_K, 'g-.', label='Levenberg-Marquardt', linewidth=2)
ax.axhline(K_true, color='k', linestyle=':', label='真值')
ax.set_xlabel('迭代次数')
ax.set_ylabel('K (m/day)')
ax.set_title('水力传导度率定过程')
ax.legend()
ax.grid(True, alpha=0.3)

# 参数收敛 - 边界
ax = axes[2]
gd_h_left = [p[1] for p in result_gd['history']['parameters']]
lm_h_left = [p[1] for p in result_lm['history']['parameters']]
ax.plot(gd_h_left, 'b-', label='GD: h_left', linewidth=2)
ax.plot(lm_h_left, 'g-.', label='L-M: h_left', linewidth=2)
ax.axhline(h_left_true, color='k', linestyle=':', label='真值')
ax.set_xlabel('迭代次数')
ax.set_ylabel('水头 (m)')
ax.set_title('边界条件率定过程')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_06_convergence_comparison.png', dpi=300, bbox_inches='tight')
print("已保存: case_06_convergence_comparison.png")
plt.close()

# 图2：观测值与拟合结果
fig, ax = plt.subplots(figsize=(10, 6))

x_obs = np.linspace(100, 900, len(h_observed_noisy))

# 观测值
ax.scatter(x_obs, h_observed_noisy, color='black', s=100, 
          label='观测值（含噪声）', zorder=5, marker='o')

# 真实值
ax.plot(x_obs, h_observed, 'k--', linewidth=2, label='真实值', zorder=4)

# 率定结果
h_sim_gd = forward_model_1d(result_gd['parameters'])
h_sim_gn = forward_model_1d(result_gn['parameters'])
h_sim_lm = forward_model_1d(result_lm['parameters'])

ax.plot(x_obs, h_sim_gd, 'b-', linewidth=2, alpha=0.7, label='梯度下降')
ax.plot(x_obs, h_sim_gn, 'r--', linewidth=2, alpha=0.7, label='Gauss-Newton')
ax.plot(x_obs, h_sim_lm, 'g-.', linewidth=2, alpha=0.7, label='Levenberg-Marquardt')

ax.set_xlabel('位置 (m)')
ax.set_ylabel('水头 (m)')
ax.set_title('观测值与率定结果对比')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_06_fitted_results.png', dpi=300, bbox_inches='tight')
print("已保存: case_06_fitted_results.png")
plt.close()

# 图3：残差分析
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

residuals_gd = h_observed_noisy - h_sim_gd
residuals_gn = h_observed_noisy - h_sim_gn
residuals_lm = h_observed_noisy - h_sim_lm

# 残差分布
ax = axes[0]
ax.scatter(x_obs, residuals_gd, color='blue', label='梯度下降', alpha=0.6)
ax.scatter(x_obs, residuals_gn, color='red', label='Gauss-Newton', alpha=0.6)
ax.scatter(x_obs, residuals_lm, color='green', label='L-M', alpha=0.6)
ax.axhline(0, color='k', linestyle='--', alpha=0.5)
ax.set_xlabel('位置 (m)')
ax.set_ylabel('残差 (m)')
ax.set_title('残差空间分布')
ax.legend()
ax.grid(True, alpha=0.3)

# 残差直方图
ax = axes[1]
ax.hist(residuals_lm, bins=10, alpha=0.7, color='green', edgecolor='black')
ax.set_xlabel('残差 (m)')
ax.set_ylabel('频数')
ax.set_title('残差分布（L-M法）')
ax.axvline(0, color='k', linestyle='--', alpha=0.5)
ax.grid(True, alpha=0.3)

# 敏感性分析
ax = axes[2]
param_names = ['K', 'h_left', 'h_right']
ax.bar(param_names, composite_sens, color=['steelblue', 'coral', 'lightgreen'],
       edgecolor='black')
ax.set_ylabel('复合敏感性')
ax.set_title('参数敏感性分析')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('case_06_residuals_and_sensitivity.png', dpi=300, bbox_inches='tight')
print("已保存: case_06_residuals_and_sensitivity.png")
plt.close()

# 图4：参数相关性热图
fig, ax = plt.subplots(figsize=(8, 6))

im = ax.imshow(np.abs(correlation_matrix), cmap='RdYlBu_r', vmin=0, vmax=1)
ax.set_xticks(range(3))
ax.set_yticks(range(3))
ax.set_xticklabels(param_names)
ax.set_yticklabels(param_names)

# 添加数值标注
for i in range(3):
    for j in range(3):
        text = ax.text(j, i, f'{correlation_matrix[i, j]:.3f}',
                      ha="center", va="center", color="black", fontsize=12)

plt.colorbar(im, ax=ax, label='相关性系数')
ax.set_title('参数相关性矩阵')

plt.tight_layout()
plt.savefig('case_06_parameter_correlation.png', dpi=300, bbox_inches='tight')
print("已保存: case_06_parameter_correlation.png")
plt.close()


# ============================================================================
# 第5步：性能比较
# ============================================================================

print("\n" + "=" * 70)
print("5. 方法性能总结")
print("=" * 70)

methods = ['梯度下降', 'Gauss-Newton', 'Levenberg-Marquardt']
results = [result_gd, result_gn, result_lm]

print(f"\n{'方法':<20} {'迭代次数':<10} {'最终目标函数':<15} {'K误差':<10} {'收敛':<10}")
print("-" * 70)

for method, result in zip(methods, results):
    K_error = abs(result['parameters'][0] - K_true) / K_true * 100
    print(f"{method:<20} {result['iterations']:<10} {result['objective']:<15.6e} "
          f"{K_error:<10.2f}% {'是' if result['success'] else '否':<10}")

print("\n推荐:")
print("  • Levenberg-Marquardt法综合性能最优")
print("  • Gauss-Newton法收敛快但可能不稳定")
print("  • 梯度下降法稳定但收敛慢")

print("\n" + "=" * 70)
print("案例6完成！")
print("=" * 70)
print("\n输出文件:")
print("  1. case_06_convergence_comparison.png - 收敛历史对比")
print("  2. case_06_fitted_results.png - 观测值与拟合结果")
print("  3. case_06_residuals_and_sensitivity.png - 残差和敏感性分析")
print("  4. case_06_parameter_correlation.png - 参数相关性")
