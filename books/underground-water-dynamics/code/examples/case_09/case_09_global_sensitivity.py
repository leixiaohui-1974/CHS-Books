"""
案例9：敏感性分析深入

演示全局敏感性分析方法：
1. Sobol敏感性指数
2. Morris筛选法
3. 参数交互作用分析
4. 与局部敏感性对比
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.solvers.steady_state import solve_1d_steady_gw
from gwflow.calibration.global_sensitivity import (
    compute_sobol_indices,
    morris_screening,
    interaction_analysis
)
from gwflow.calibration.sensitivity import (
    compute_sensitivity_matrix,
    compute_composite_sensitivity
)

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("案例9：敏感性分析深入")
print("=" * 70)


# ============================================================================
# 第1步：定义测试模型
# ============================================================================

def forward_model_1d(params: np.ndarray) -> float:
    """
    一维稳态地下水流动正演模型（返回单一输出）
    
    Parameters
    ----------
    params : np.ndarray
        参数数组 [K, h_left, h_right]
        
    Returns
    -------
    float
        目标输出（中点水头值）
    """
    K, h_left, h_right = params
    
    L = 1000.0
    nx = 100
    
    h = solve_1d_steady_gw(K=K, L=L, nx=nx, h_left=h_left, h_right=h_right)
    
    # 返回中点水头
    return h[nx // 2]


print("\n1. 定义测试模型")
print("-" * 70)
print("模型: 一维稳态地下水流动")
print("输出: 中点水头值")
print("参数: K (水力传导度), h_left, h_right")


# ============================================================================
# 第2步：Sobol敏感性分析
# ============================================================================

print("\n" + "=" * 70)
print("2. Sobol敏感性分析")
print("=" * 70)

# 参数范围
bounds = [
    (5.0, 20.0),   # K: 5-20 m/day
    (15.0, 25.0),  # h_left: 15-25 m
    (8.0, 15.0)    # h_right: 8-15 m
]

print("\n参数范围:")
print(f"  K ∈ [5, 20] m/day")
print(f"  h_left ∈ [15, 25] m")
print(f"  h_right ∈ [8, 15] m")

# 计算Sobol指数
print("\n计算Sobol敏感性指数...")
sobol_result = compute_sobol_indices(
    forward_model=forward_model_1d,
    bounds=bounds,
    n_samples=500,  # 使用较小样本数以加快演示
    calc_second_order=True,
    verbose=True
)


# ============================================================================
# 第3步：Morris筛选法
# ============================================================================

print("\n" + "=" * 70)
print("3. Morris筛选法")
print("=" * 70)

morris_result = morris_screening(
    forward_model=forward_model_1d,
    bounds=bounds,
    n_trajectories=20,
    n_levels=4,
    delta=0.5,
    verbose=True
)


# ============================================================================
# 第4步：参数交互作用分析
# ============================================================================

print("\n" + "=" * 70)
print("4. 参数交互作用分析")
print("=" * 70)

interaction_result = interaction_analysis(
    forward_model=forward_model_1d,
    bounds=bounds,
    n_samples=10,
    param_pairs=[(0, 1), (0, 2), (1, 2)]  # K-h_left, K-h_right, h_left-h_right
)

print("\n交互作用强度:")
for pair, strength in interaction_result['interaction_strength'].items():
    param_names = ['K', 'h_left', 'h_right']
    print(f"  {param_names[pair[0]]} × {param_names[pair[1]]}: {strength:.4f}")


# ============================================================================
# 第5步：局部敏感性对比
# ============================================================================

print("\n" + "=" * 70)
print("5. 局部敏感性对比")
print("=" * 70)

# 在参数空间中点计算局部敏感性
params_center = np.array([(lower + upper) / 2 for lower, upper in bounds])

print(f"\n参考点:")
print(f"  K = {params_center[0]:.2f} m/day")
print(f"  h_left = {params_center[1]:.2f} m")
print(f"  h_right = {params_center[2]:.2f} m")

# 定义局部敏感性的正演模型（返回向量）
def forward_model_local(params):
    K, h_left, h_right = params
    L = 1000.0
    nx = 100
    h = solve_1d_steady_gw(K=K, L=L, nx=nx, h_left=h_left, h_right=h_right)
    # 返回10个观测点
    obs_indices = np.linspace(10, 90, 10, dtype=int)
    return h[obs_indices]

# 计算局部敏感性
sensitivity_matrix = compute_sensitivity_matrix(
    forward_model=forward_model_local,
    parameters=params_center,
    method='forward'
)

composite_sens_local = compute_composite_sensitivity(sensitivity_matrix)

print(f"\n局部复合敏感性:")
for i, name in enumerate(['K', 'h_left', 'h_right']):
    print(f"  {name}: {composite_sens_local[i]:.4f}")


# ============================================================================
# 第6步：可视化
# ============================================================================

print("\n" + "=" * 70)
print("6. 生成可视化图表")
print("=" * 70)

# 图1：Sobol指数对比
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

param_names = ['K', 'h_left', 'h_right']
x = np.arange(len(param_names))
width = 0.35

# 一阶和总效应指数
ax = axes[0]
ax.bar(x - width/2, sobol_result['S_first'], width, label='一阶指数 (S_i)',
       color='steelblue', edgecolor='black')
ax.bar(x + width/2, sobol_result['S_total'], width, label='总效应指数 (ST_i)',
       color='coral', edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels(param_names)
ax.set_ylabel('敏感性指数')
ax.set_title('Sobol敏感性指数')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# 交互效应指数
ax = axes[1]
interaction_indices = sobol_result['S_total'] - sobol_result['S_first']
colors = ['green' if i > 0.05 else 'lightgray' for i in interaction_indices]
ax.bar(x, interaction_indices, color=colors, edgecolor='black')
ax.set_xticks(x)
ax.set_xticklabels(param_names)
ax.set_ylabel('交互效应指数 (ST_i - S_i)')
ax.set_title('参数交互作用')
ax.axhline(0.05, color='r', linestyle='--', label='显著性阈值')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('case_09_sobol_indices.png', dpi=300, bbox_inches='tight')
print("已保存: case_09_sobol_indices.png")
plt.close()

# 图2：Morris筛选图
fig, ax = plt.subplots(figsize=(8, 8))

ax.scatter(morris_result['mu_star'], morris_result['sigma'],
          s=200, alpha=0.6, color='steelblue', edgecolors='black', linewidth=2)

# 标注参数名称
for i, name in enumerate(param_names):
    ax.annotate(name, (morris_result['mu_star'][i], morris_result['sigma'][i]),
               xytext=(5, 5), textcoords='offset points', fontsize=14, fontweight='bold')

# 分区线
mu_star_median = np.median(morris_result['mu_star'])
sigma_median = np.median(morris_result['sigma'])

ax.axvline(mu_star_median, color='red', linestyle='--', alpha=0.7, linewidth=2,
          label=f'μ*中位数: {mu_star_median:.3f}')
ax.axhline(sigma_median, color='green', linestyle='--', alpha=0.7, linewidth=2,
          label=f'σ中位数: {sigma_median:.3f}')

# 添加区域标签
ax.text(mu_star_median * 1.5, sigma_median * 1.5, '重要\n非线性/交互',
       ha='center', va='center', fontsize=12, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
ax.text(mu_star_median * 0.5, sigma_median * 0.5, '不重要',
       ha='center', va='center', fontsize=12, bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))

ax.set_xlabel('μ* (绝对均值)', fontsize=14)
ax.set_ylabel('σ (标准差)', fontsize=14)
ax.set_title('Morris筛选图', fontsize=16, fontweight='bold')
ax.legend(loc='upper left', fontsize=12)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_09_morris_screening.png', dpi=300, bbox_inches='tight')
print("已保存: case_09_morris_screening.png")
plt.close()

# 图3：二阶交互指数热图
if 'S_second' in sobol_result:
    fig, ax = plt.subplots(figsize=(8, 6))
    
    im = ax.imshow(sobol_result['S_second'], cmap='RdYlBu_r', vmin=-0.1, vmax=0.1)
    
    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(param_names)
    ax.set_yticklabels(param_names)
    
    # 添加数值标注
    for i in range(3):
        for j in range(3):
            if i != j:
                text = ax.text(j, i, f'{sobol_result["S_second"][i, j]:.4f}',
                              ha="center", va="center", color="black", fontsize=12)
    
    plt.colorbar(im, ax=ax, label='二阶Sobol指数')
    ax.set_title('参数二阶交互效应')
    
    plt.tight_layout()
    plt.savefig('case_09_second_order_indices.png', dpi=300, bbox_inches='tight')
    print("已保存: case_09_second_order_indices.png")
    plt.close()

# 图4：全局vs局部敏感性对比
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(param_names))
width = 0.25

# 归一化以便比较
sobol_first_norm = sobol_result['S_first'] / np.sum(sobol_result['S_first'])
morris_norm = morris_result['mu_star'] / np.sum(morris_result['mu_star'])
local_norm = composite_sens_local / np.sum(composite_sens_local)

ax.bar(x - width, sobol_first_norm, width, label='Sobol一阶',
       color='steelblue', edgecolor='black')
ax.bar(x, morris_norm, width, label='Morris μ*',
       color='coral', edgecolor='black')
ax.bar(x + width, local_norm, width, label='局部敏感性',
       color='lightgreen', edgecolor='black')

ax.set_xticks(x)
ax.set_xticklabels(param_names)
ax.set_ylabel('归一化敏感性')
ax.set_title('全局 vs 局部敏感性对比')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('case_09_global_vs_local.png', dpi=300, bbox_inches='tight')
print("已保存: case_09_global_vs_local.png")
plt.close()


# ============================================================================
# 第7步：方法总结
# ============================================================================

print("\n" + "=" * 70)
print("7. 方法总结与对比")
print("=" * 70)

print("\n方法特点:")

print("\nSobol方法:")
print("  ✅ 完整的方差分解")
print("  ✅ 一阶和总效应指数")
print("  ✅ 量化参数交互")
print("  ❌ 计算成本高")
print(f"  模型运行次数: {sobol_result['n_samples'] * (2 + len(param_names))}")

print("\nMorris方法:")
print("  ✅ 计算效率高")
print("  ✅ 参数筛选")
print("  ✅ 检测非线性")
print("  ❌ 精度相对较低")
print(f"  模型运行次数: {morris_result['n_trajectories'] * (len(param_names) + 1)}")

print("\n局部敏感性:")
print("  ✅ 计算最快")
print("  ✅ 精确（局部）")
print("  ❌ 仅在一个点")
print("  ❌ 不考虑非线性")
print(f"  模型运行次数: {len(param_names) + 1}")

print("\n参数排序:")
print("\nSobol一阶指数:")
sobol_order = np.argsort(sobol_result['S_first'])[::-1]
for i, idx in enumerate(sobol_order):
    print(f"  {i+1}. {param_names[idx]}: {sobol_result['S_first'][idx]:.4f}")

print("\nMorris μ*:")
morris_order = np.argsort(morris_result['mu_star'])[::-1]
for i, idx in enumerate(morris_order):
    print(f"  {i+1}. {param_names[idx]}: {morris_result['mu_star'][idx]:.4f}")

print("\n" + "=" * 70)
print("案例9完成！")
print("=" * 70)
print("\n输出文件:")
print("  1. case_09_sobol_indices.png - Sobol敏感性指数")
print("  2. case_09_morris_screening.png - Morris筛选图")
print("  3. case_09_second_order_indices.png - 二阶交互指数")
print("  4. case_09_global_vs_local.png - 全局vs局部对比")
