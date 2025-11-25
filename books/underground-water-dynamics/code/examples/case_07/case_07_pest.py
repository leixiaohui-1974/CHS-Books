"""
案例7：PEST方法实现

演示PEST风格的参数率定框架：
1. 参数组管理
2. 观测组管理  
3. SVD辅助参数估计
4. Tikhonov正则化
5. 与标准方法对比
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.solvers.steady_state import solve_2d_steady_gw
from gwflow.calibration.pest import (
    ParameterGroup,
    ObservationGroup,
    pest_calibrate
)

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("案例7：PEST方法实现")
print("=" * 70)


# ============================================================================
# 第1步：定义二维地下水流动模型
# ============================================================================

# 模型参数
Lx, Ly = 1000.0, 800.0  # 区域尺寸 (m)
nx, ny = 50, 40         # 网格数

def forward_model_2d(params_vector: np.ndarray) -> np.ndarray:
    """
    二维稳态地下水流动正演模型
    
    Parameters
    ----------
    params_vector : np.ndarray
        参数向量 [K1, K2, h_left, h_right]
        
    Returns
    -------
    np.ndarray
        观测点的模拟水头
    """
    K1, K2, h_left, h_right = params_vector
    
    # 分区K值（左半部分K1，右半部分K2）
    K = np.ones((ny, nx)) * K1
    K[:, nx//2:] = K2
    
    # 边界条件
    boundary_conditions = {
        'left': {'type': 'dirichlet', 'value': h_left},
        'right': {'type': 'dirichlet', 'value': h_right},
        'top': {'type': 'neumann', 'value': 0.0},
        'bottom': {'type': 'neumann', 'value': 0.0}
    }
    
    # 求解
    h = solve_2d_steady_gw(
        K=K,
        Lx=Lx,
        Ly=Ly,
        nx=nx,
        ny=ny,
        boundary_conditions=boundary_conditions
    )
    
    # 提取观测点值（10个点，均匀分布）
    obs_x = np.array([10, 15, 20, 25, 30, 35, 40, 45])
    obs_y = np.array([20, 20, 20, 20, 20, 20, 20, 20])
    
    h_obs = h[obs_y, obs_x]
    
    return h_obs


print("\n1. 生成合成观测数据")
print("-" * 70)

# 真实参数
K1_true = 10.0      # m/day（左区）
K2_true = 5.0       # m/day（右区）
h_left_true = 25.0  # m
h_right_true = 15.0 # m
params_true = np.array([K1_true, K2_true, h_left_true, h_right_true])

print(f"真实参数:")
print(f"  K1 (左区) = {K1_true:.2f} m/day")
print(f"  K2 (右区) = {K2_true:.2f} m/day")
print(f"  h_left = {h_left_true:.2f} m")
print(f"  h_right = {h_right_true:.2f} m")

# 生成观测数据
np.random.seed(42)
h_observed = forward_model_2d(params_true)
noise = np.random.normal(0, 0.1, len(h_observed))
h_observed_noisy = h_observed + noise

print(f"\n观测点数量: {len(h_observed_noisy)}")
print(f"观测水头范围: [{h_observed_noisy.min():.2f}, {h_observed_noisy.max():.2f}] m")


# ============================================================================
# 第2步：设置PEST参数组和观测组
# ============================================================================

print("\n" + "=" * 70)
print("2. 设置PEST参数组和观测组")
print("=" * 70)

# 参数组1：水力传导度
K_group = ParameterGroup(
    name='hydraulic_conductivity',
    parameters=['K1', 'K2'],
    initial_values=np.array([5.0, 3.0]),  # 初始猜测
    lower_bounds=np.array([1.0, 1.0]),
    upper_bounds=np.array([50.0, 50.0]),
    transform='log',  # 对数变换
    scale_factor=1.0
)

# 参数组2：边界条件
BC_group = ParameterGroup(
    name='boundary_conditions',
    parameters=['h_left', 'h_right'],
    initial_values=np.array([20.0, 18.0]),  # 初始猜测
    lower_bounds=np.array([10.0, 10.0]),
    upper_bounds=np.array([30.0, 25.0]),
    transform='none',  # 无变换
    scale_factor=1.0
)

param_groups = [K_group, BC_group]

print(f"参数组1: {K_group.name}")
print(f"  参数: {K_group.parameters}")
print(f"  初始值: {K_group.initial_values}")
print(f"  变换: {K_group.transform}")

print(f"\n参数组2: {BC_group.name}")
print(f"  参数: {BC_group.parameters}")
print(f"  初始值: {BC_group.initial_values}")
print(f"  变换: {BC_group.transform}")

# 观测组
obs_group = ObservationGroup(
    name='head_observations',
    observations=h_observed_noisy,
    weights=None,  # 均匀权重
    group_weight=1.0
)

obs_groups = [obs_group]

print(f"\n观测组: {obs_group.name}")
print(f"  观测数: {obs_group.n_obs}")
print(f"  权重: 均匀")


# ============================================================================
# 第3步：使用不同方法进行PEST率定
# ============================================================================

print("\n" + "=" * 70)
print("3. 参数率定")
print("=" * 70)

# 方法1：SVD辅助（无正则化）
print("\n" + "-" * 70)
print("方法1：SVD辅助（无正则化）")
print("-" * 70)

result_svd = pest_calibrate(
    forward_model_2d,
    param_groups,
    obs_groups,
    method='svd',
    max_iterations=30,
    tolerance=1e-5,
    svd_components=None,  # 自动确定
    regularization_alpha=0.0,
    verbose=True
)

print(f"\n率定结果:")
for group_name, group_params in result_svd['parameters'].items():
    print(f"  {group_name}:")
    for pname, pvalue in group_params.items():
        print(f"    {pname} = {pvalue:.4f}")

# 方法2：SVD辅助+Tikhonov正则化
print("\n" + "-" * 70)
print("方法2：SVD辅助 + Tikhonov正则化")
print("-" * 70)

result_svd_reg = pest_calibrate(
    forward_model_2d,
    param_groups,
    obs_groups,
    method='svd',
    max_iterations=30,
    tolerance=1e-5,
    svd_components=None,
    regularization_alpha=0.1,  # 正则化参数
    verbose=True
)

print(f"\n率定结果:")
for group_name, group_params in result_svd_reg['parameters'].items():
    print(f"  {group_name}:")
    for pname, pvalue in group_params.items():
        print(f"    {pname} = {pvalue:.4f}")

# 方法3：Levenberg-Marquardt
print("\n" + "-" * 70)
print("方法3：Levenberg-Marquardt")
print("-" * 70)

result_lm = pest_calibrate(
    forward_model_2d,
    param_groups,
    obs_groups,
    method='lm',
    max_iterations=30,
    tolerance=1e-5,
    verbose=True
)

print(f"\n率定结果:")
for group_name, group_params in result_lm['parameters'].items():
    print(f"  {group_name}:")
    for pname, pvalue in group_params.items():
        print(f"    {pname} = {pvalue:.4f}")


# ============================================================================
# 第4步：可视化
# ============================================================================

print("\n" + "=" * 70)
print("4. 生成可视化图表")
print("=" * 70)

# 图1：收敛历史
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 目标函数收敛
ax = axes[0]
ax.semilogy(result_svd['history']['objective'], 'b-', 
           label='SVD', linewidth=2)
ax.semilogy(result_svd_reg['history']['objective'], 'r--', 
           label='SVD + 正则化', linewidth=2)
ax.semilogy(result_lm['history']['objective'], 'g-.', 
           label='L-M', linewidth=2)
ax.set_xlabel('迭代次数')
ax.set_ylabel('目标函数值')
ax.set_title('收敛历史')
ax.legend()
ax.grid(True, alpha=0.3)

# 参数收敛（K1）
ax = axes[1]
svd_K1 = [p[0] for p in result_svd['history']['parameters']]
svd_reg_K1 = [p[0] for p in result_svd_reg['history']['parameters']]
lm_K1 = [p[0] for p in result_lm['history']['parameters']]

ax.plot(svd_K1, 'b-', label='SVD', linewidth=2)
ax.plot(svd_reg_K1, 'r--', label='SVD + 正则化', linewidth=2)
ax.plot(lm_K1, 'g-.', label='L-M', linewidth=2)
ax.axhline(K1_true, color='k', linestyle=':', label='真值', linewidth=2)
ax.set_xlabel('迭代次数')
ax.set_ylabel('K1 (m/day)')
ax.set_title('水力传导度K1率定过程')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_07_convergence.png', dpi=300, bbox_inches='tight')
print("已保存: case_07_convergence.png")
plt.close()

# 图2：SVD奇异值分析
if result_svd['history']['svd_info']:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 奇异值
    ax = axes[0]
    svd_info = result_svd['history']['svd_info'][-1]  # 最后一次迭代
    singular_values = svd_info['singular_values']
    ax.semilogy(range(1, len(singular_values) + 1), singular_values, 
               'bo-', linewidth=2, markersize=8)
    ax.axvline(svd_info['n_components'], color='r', linestyle='--', 
              label=f"保留成分数: {svd_info['n_components']}")
    ax.set_xlabel('奇异值索引')
    ax.set_ylabel('奇异值')
    ax.set_title('奇异值谱')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 条件数演化
    ax = axes[1]
    condition_numbers = [info['condition_number_truncated'] 
                        for info in result_svd['history']['svd_info']]
    ax.semilogy(condition_numbers, 'b-', linewidth=2)
    ax.set_xlabel('迭代次数')
    ax.set_ylabel('条件数')
    ax.set_title('条件数演化')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case_07_svd_analysis.png', dpi=300, bbox_inches='tight')
    print("已保存: case_07_svd_analysis.png")
    plt.close()

# 图3：观测值拟合对比
fig, ax = plt.subplots(figsize=(10, 6))

x_obs = np.arange(len(h_observed_noisy))

# 观测值
ax.scatter(x_obs, h_observed_noisy, color='black', s=100, 
          label='观测值', zorder=5)

# 真实值
ax.plot(x_obs, h_observed, 'k--', linewidth=2, label='真实值', zorder=4)

# 率定结果
h_sim_svd = forward_model_2d(result_svd['parameter_vector'])
h_sim_svd_reg = forward_model_2d(result_svd_reg['parameter_vector'])
h_sim_lm = forward_model_2d(result_lm['parameter_vector'])

ax.plot(x_obs, h_sim_svd, 'b-', linewidth=2, alpha=0.7, label='SVD')
ax.plot(x_obs, h_sim_svd_reg, 'r--', linewidth=2, alpha=0.7, label='SVD + 正则化')
ax.plot(x_obs, h_sim_lm, 'g-.', linewidth=2, alpha=0.7, label='L-M')

ax.set_xlabel('观测点索引')
ax.set_ylabel('水头 (m)')
ax.set_title('观测值与率定结果对比')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_07_fitted_results.png', dpi=300, bbox_inches='tight')
print("已保存: case_07_fitted_results.png")
plt.close()

# 图4：参数对比
fig, ax = plt.subplots(figsize=(10, 6))

param_names = ['K1', 'K2', 'h_left', 'h_right']
true_values = params_true

svd_values = result_svd['parameter_vector']
svd_reg_values = result_svd_reg['parameter_vector']
lm_values = result_lm['parameter_vector']

x = np.arange(len(param_names))
width = 0.2

ax.bar(x - 1.5*width, true_values, width, label='真值', color='black', alpha=0.7)
ax.bar(x - 0.5*width, svd_values, width, label='SVD', color='blue', alpha=0.7)
ax.bar(x + 0.5*width, svd_reg_values, width, label='SVD + 正则化', color='red', alpha=0.7)
ax.bar(x + 1.5*width, lm_values, width, label='L-M', color='green', alpha=0.7)

ax.set_xticks(x)
ax.set_xticklabels(param_names)
ax.set_ylabel('参数值')
ax.set_title('参数率定结果对比')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('case_07_parameter_comparison.png', dpi=300, bbox_inches='tight')
print("已保存: case_07_parameter_comparison.png")
plt.close()


# ============================================================================
# 第5步：性能总结
# ============================================================================

print("\n" + "=" * 70)
print("5. 方法性能总结")
print("=" * 70)

methods = ['SVD', 'SVD + 正则化', 'L-M']
results = [result_svd, result_svd_reg, result_lm]

print(f"\n{'方法':<20} {'迭代次数':<10} {'目标函数':<15} {'K1误差':<10} {'K2误差':<10}")
print("-" * 70)

for method, result in zip(methods, results):
    K1_error = abs(result['parameter_vector'][0] - K1_true) / K1_true * 100
    K2_error = abs(result['parameter_vector'][1] - K2_true) / K2_true * 100
    print(f"{method:<20} {result['iterations']:<10} {result['objective']:<15.6e} "
          f"{K1_error:<10.2f}% {K2_error:<10.2f}%")

print("\nPEST方法特点:")
print("  • 参数组管理：便于组织复杂参数")
print("  • 观测组管理：支持不同类型观测")
print("  • SVD辅助：处理病态问题")
print("  • 正则化：稳定参数估计")

print("\n" + "=" * 70)
print("案例7完成！")
print("=" * 70)
print("\n输出文件:")
print("  1. case_07_convergence.png - 收敛历史")
print("  2. case_07_svd_analysis.png - SVD分析")
print("  3. case_07_fitted_results.png - 拟合结果")
print("  4. case_07_parameter_comparison.png - 参数对比")
