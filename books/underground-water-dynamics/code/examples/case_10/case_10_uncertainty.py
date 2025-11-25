"""
案例10：不确定性量化

演示不确定性量化的各种方法：
1. Monte Carlo不确定性分析
2. GLUE方法
3. Bootstrap方法
4. 不确定性分解
5. 方法对比
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.solvers.steady_state import solve_1d_steady_gw
from gwflow.calibration.uncertainty import (
    monte_carlo_uncertainty,
    glue_analysis,
    bootstrap_uncertainty,
    propagate_uncertainty
)
from gwflow.calibration.optimization import levenberg_marquardt

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("案例10：不确定性量化")
print("=" * 70)


# ============================================================================
# 第1步：生成数据
# ============================================================================

def forward_model_vector(params: np.ndarray) -> np.ndarray:
    """一维稳态地下水流动（返回观测点水头）"""
    K, h_left, h_right = params
    
    L = 1000.0
    nx = 100
    
    h = solve_1d_steady_gw(K=K, L=L, h0=h_left, hL=h_right, nx=nx)
    
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
h_true = forward_model_vector(params_true)
sigma_obs = 0.15  # 观测误差
noise = np.random.normal(0, sigma_obs, len(h_true))
h_observed = h_true + noise

print(f"\n观测点数量: {len(h_observed)}")
print(f"观测误差标准差: {sigma_obs:.2f} m")


# ============================================================================
# 第2步：参数率定（获得校准参数）
# ============================================================================

print("\n" + "=" * 70)
print("2. 参数率定")
print("=" * 70)

initial_params = np.array([15.0, 22.0, 12.0])
bounds = [(5.0, 20.0), (15.0, 25.0), (8.0, 15.0)]

result_calib = levenberg_marquardt(
    forward_model=forward_model_vector,
    initial_params=initial_params,
    observed=h_observed,
    bounds=bounds,
    verbose=False
)

params_calibrated = result_calib['parameters']

print(f"率定结果:")
print(f"  K = {params_calibrated[0]:.4f} m/day")
print(f"  h_left = {params_calibrated[1]:.4f} m")
print(f"  h_right = {params_calibrated[2]:.4f} m")


# ============================================================================
# 第3步：Monte Carlo不确定性分析
# ============================================================================

print("\n" + "=" * 70)
print("3. Monte Carlo不确定性分析")
print("=" * 70)

# 定义参数不确定性（基于率定结果的假设）
param_distributions = [
    ('normal', (params_calibrated[0], 0.5)),    # K
    ('normal', (params_calibrated[1], 0.3)),    # h_left
    ('normal', (params_calibrated[2], 0.3))     # h_right
]

mc_result = monte_carlo_uncertainty(
    forward_model=forward_model_vector,
    param_distributions=param_distributions,
    n_samples=2000,
    verbose=True
)

print(f"\n输出不确定性:")
print(f"  均值标准差: {np.mean(mc_result['output_std']):.4f} m")


# ============================================================================
# 第4步：GLUE分析
# ============================================================================

print("\n" + "=" * 70)
print("4. GLUE分析")
print("=" * 70)

glue_result = glue_analysis(
    forward_model=forward_model_vector,
    observations=h_observed,
    param_bounds=bounds,
    n_samples=5000,
    likelihood_threshold=0.7,
    verbose=True
)


# ============================================================================
# 第5步：Bootstrap不确定性
# ============================================================================

print("\n" + "=" * 70)
print("5. Bootstrap不确定性分析")
print("=" * 70)

bootstrap_result = bootstrap_uncertainty(
    forward_model=forward_model_vector,
    observations=h_observed,
    calibrated_params=params_calibrated,
    n_bootstrap=1000,
    noise_std=sigma_obs,
    verbose=True
)


# ============================================================================
# 第6步：可视化
# ============================================================================

print("\n" + "=" * 70)
print("6. 生成可视化图表")
print("=" * 70)

x_obs = np.arange(len(h_observed))

# 图1：Monte Carlo不确定性
fig, ax = plt.subplots(figsize=(10, 6))

# 真实值
ax.plot(x_obs, h_true, 'g--', linewidth=2, label='真实值', zorder=4)

# 观测值
ax.scatter(x_obs, h_observed, color='black', s=100, zorder=5,
          label='观测值', marker='o')

# Monte Carlo预测均值
ax.plot(x_obs, mc_result['output_mean'], 'b-', linewidth=2,
       label='Monte Carlo均值', zorder=3)

# 95%置信区间
ax.fill_between(x_obs, mc_result['output_ci_lower'], mc_result['output_ci_upper'],
                alpha=0.3, color='blue', label='95% Monte Carlo区间')

# 率定值
h_calibrated = forward_model_vector(params_calibrated)
ax.plot(x_obs, h_calibrated, 'r-.', linewidth=2,
       label='率定值', zorder=3)

ax.set_xlabel('观测点索引')
ax.set_ylabel('水头 (m)')
ax.set_title('Monte Carlo不确定性分析')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_10_monte_carlo.png', dpi=300, bbox_inches='tight')
print("已保存: case_10_monte_carlo.png")
plt.close()

# 图2：GLUE不确定性
fig, ax = plt.subplots(figsize=(10, 6))

# 观测值
ax.scatter(x_obs, h_observed, color='black', s=100, zorder=5,
          label='观测值', marker='o')

# 真实值
ax.plot(x_obs, h_true, 'g--', linewidth=2, label='真实值', zorder=4)

# GLUE预测（绘制行为参数集的模拟）
for i in range(min(100, glue_result['n_behavioral'])):
    ax.plot(x_obs, glue_result['behavioral_simulations'][i],
           'gray', alpha=0.1, linewidth=0.5)

# GLUE加权均值
ax.plot(x_obs, glue_result['weighted_mean'], 'r-', linewidth=2,
       label='GLUE加权均值', zorder=3)

# 95%置信区间
ax.fill_between(x_obs, glue_result['ci_lower'], glue_result['ci_upper'],
                alpha=0.3, color='red', label='95% GLUE区间')

ax.set_xlabel('观测点索引')
ax.set_ylabel('水头 (m)')
ax.set_title(f'GLUE分析 (行为参数集: {glue_result["n_behavioral"]}/{glue_result["n_total"]})')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_10_glue.png', dpi=300, bbox_inches='tight')
print("已保存: case_10_glue.png")
plt.close()

# 图3：方法对比
fig, ax = plt.subplots(figsize=(10, 6))

# 观测值
ax.scatter(x_obs, h_observed, color='black', s=100, zorder=5,
          label='观测值', marker='o')

# 真实值
ax.plot(x_obs, h_true, 'g--', linewidth=3, label='真实值', zorder=4)

# Monte Carlo
ax.plot(x_obs, mc_result['output_mean'], 'b-', linewidth=2,
       label='Monte Carlo', alpha=0.7)
ax.fill_between(x_obs, mc_result['output_ci_lower'], mc_result['output_ci_upper'],
                alpha=0.2, color='blue')

# GLUE
ax.plot(x_obs, glue_result['weighted_mean'], 'r-', linewidth=2,
       label='GLUE', alpha=0.7)
ax.fill_between(x_obs, glue_result['ci_lower'], glue_result['ci_upper'],
                alpha=0.2, color='red')

# Bootstrap
ax.plot(x_obs, bootstrap_result['output_mean'], 'm-.', linewidth=2,
       label='Bootstrap', alpha=0.7)
ax.fill_between(x_obs, bootstrap_result['ci_lower'], bootstrap_result['ci_upper'],
                alpha=0.2, color='magenta')

ax.set_xlabel('观测点索引')
ax.set_ylabel('水头 (m)')
ax.set_title('不确定性量化方法对比')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case_10_methods_comparison.png', dpi=300, bbox_inches='tight')
print("已保存: case_10_methods_comparison.png")
plt.close()

# 图4：行为参数集分布（GLUE）
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

param_names = ['K (m/day)', 'h_left (m)', 'h_right (m)']
true_values = params_true

for i, (ax, name, true_val) in enumerate(zip(axes, param_names, true_values)):
    # 所有样本的直方图（浅色）
    ax.hist(glue_result['behavioral_params'][:, i], bins=30, alpha=0.5,
           color='lightgray', edgecolor='black', density=True,
           label='行为参数集')
    
    # 真值
    ax.axvline(true_val, color='green', linestyle=':', linewidth=3,
              label='真值')
    
    # 率定值
    ax.axvline(params_calibrated[i], color='red', linestyle='--',
              linewidth=2, label='率定值')
    
    ax.set_xlabel(name)
    ax.set_ylabel('概率密度')
    ax.legend()
    ax.grid(True, alpha=0.3)

axes[0].set_title('GLUE行为参数集分布')
plt.tight_layout()
plt.savefig('case_10_behavioral_params.png', dpi=300, bbox_inches='tight')
print("已保存: case_10_behavioral_params.png")
plt.close()

# 图5：不确定性区间宽度对比
fig, ax = plt.subplots(figsize=(10, 6))

mc_width = mc_result['output_ci_upper'] - mc_result['output_ci_lower']
glue_width = glue_result['ci_upper'] - glue_result['ci_lower']
bootstrap_width = bootstrap_result['ci_upper'] - bootstrap_result['ci_lower']

width_data = 0.25
positions = np.arange(len(x_obs))

ax.bar(positions - width_data, mc_width, width_data,
      label='Monte Carlo', color='steelblue', edgecolor='black')
ax.bar(positions, glue_width, width_data,
      label='GLUE', color='coral', edgecolor='black')
ax.bar(positions + width_data, bootstrap_width, width_data,
      label='Bootstrap', color='lightgreen', edgecolor='black')

ax.set_xlabel('观测点索引')
ax.set_ylabel('95% CI宽度 (m)')
ax.set_title('不确定性区间宽度对比')
ax.set_xticks(positions)
ax.set_xticklabels(x_obs)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('case_10_uncertainty_width.png', dpi=300, bbox_inches='tight')
print("已保存: case_10_uncertainty_width.png")
plt.close()


# ============================================================================
# 第7步：方法总结
# ============================================================================

print("\n" + "=" * 70)
print("7. 方法总结与对比")
print("=" * 70)

print("\nMonte Carlo方法:")
print("  ✅ 参数不确定性传播")
print("  ✅ 适合已知参数分布")
print("  ✅ 理论清晰")
print(f"  计算成本: {mc_result['n_samples']} 次模型运行")

print("\nGLUE方法:")
print("  ✅ 非正式贝叶斯")
print("  ✅ 识别行为参数集")
print("  ✅ 适合模型结构不确定性")
print(f"  计算成本: {glue_result['n_total']} 次模型运行")
print(f"  接受率: {glue_result['acceptance_rate']*100:.1f}%")

print("\nBootstrap方法:")
print("  ✅ 残差重采样")
print("  ✅ 观测误差量化")
print("  ✅ 不需要参数分布假设")
print(f"  计算成本: {bootstrap_result['n_bootstrap']} 次（简化版）")

print("\n平均不确定性（标准差）:")
print(f"  Monte Carlo: {np.mean(mc_result['output_std']):.4f} m")
print(f"  GLUE: {np.mean(glue_result['ci_upper'] - glue_result['weighted_mean']):.4f} m")
print(f"  Bootstrap: {np.mean(bootstrap_result['output_std']):.4f} m")

print("\n覆盖率分析（真值被置信区间覆盖的比例）:")
mc_coverage = np.mean((h_true >= mc_result['output_ci_lower']) & 
                      (h_true <= mc_result['output_ci_upper']))
glue_coverage = np.mean((h_true >= glue_result['ci_lower']) & 
                        (h_true <= glue_result['ci_upper']))
bootstrap_coverage = np.mean((h_true >= bootstrap_result['ci_lower']) & 
                             (h_true <= bootstrap_result['ci_upper']))

print(f"  Monte Carlo: {mc_coverage*100:.1f}%")
print(f"  GLUE: {glue_coverage*100:.1f}%")
print(f"  Bootstrap: {bootstrap_coverage*100:.1f}%")

print("\n" + "=" * 70)
print("案例10完成！")
print("=" * 70)
print("\n输出文件:")
print("  1. case_10_monte_carlo.png - Monte Carlo不确定性")
print("  2. case_10_glue.png - GLUE分析")
print("  3. case_10_methods_comparison.png - 方法对比")
print("  4. case_10_behavioral_params.png - 行为参数集分布")
print("  5. case_10_uncertainty_width.png - 不确定性区间宽度")

print("\n" + "=" * 70)
print("🎉 参数率定篇全部完成！")
print("=" * 70)
