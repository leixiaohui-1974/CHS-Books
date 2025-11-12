"""
第9章 水文不确定性分析
题目2：模型不确定性量化（GLUE方法）

知识点：
- GLUE方法原理
- 似然函数设计
- 行为参数筛选
- 参数后验分布
- 预测不确定性区间
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.special import gamma

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# Nash汇流模型
def nash_model(t, n, K, R=50, A=100):
    """
    Nash瞬时单位线模型
    Q(t) = t^(n-1) * exp(-t/K) / (K^n * Gamma(n)) * R * A
    
    参数：
    t: 时间（h）
    n: 形状参数（整数）
    K: 尺度参数（h）
    R: 净雨量（mm）
    A: 流域面积（km²）
    
    返回：
    Q: 流量（m³/s）
    """
    # Gamma(n) = (n-1)!  对整数n
    if n < 1:
        return 0
    
    Q = (t**(n-1) * np.exp(-t/K)) / (K**n * gamma(n)) * R * A * 1e6 / 3600
    return Q

# 计算洪峰流量和峰现时间
def calc_peak(n, K, R=50, A=100):
    """计算洪峰流量和峰现时间"""
    # 峰现时间（理论值）
    Tp = K * (n - 1)
    if Tp <= 0:
        Tp = 0.1
    
    # 洪峰流量
    Qp = nash_model(Tp, n, K, R, A)
    
    return Qp, Tp

# 观测数据
Qp_obs = 120  # m³/s
Tp_obs = 8    # h

# 参数范围
n_range = [1, 5]
K_range = [2, 10]

# GLUE参数
N = 10000  # 总抽样数
sigma_Qp = 0.2 * Qp_obs  # 洪峰流量观测误差 = 24 m³/s
sigma_Tp = 1.0           # 峰现时间观测误差 = 1 h
L_threshold = 0.01       # 似然阈值

print("="*70)
print("题目2：模型不确定性量化（GLUE方法）")
print("="*70)
print(f"\n观测数据：")
print(f"  洪峰流量 Qp_obs = {Qp_obs} m³/s")
print(f"  峰现时间 Tp_obs = {Tp_obs} h")

print(f"\n参数范围：")
print(f"  n: {n_range}")
print(f"  K: {K_range}")

print(f"\nGLUE设置：")
print(f"  抽样数 N = {N}")
print(f"  Qp观测误差 σ_Qp = {sigma_Qp:.1f} m³/s")
print(f"  Tp观测误差 σ_Tp = {sigma_Tp:.1f} h")
print(f"  似然阈值 L_threshold = {L_threshold}")

# Step 1: 参数抽样（Monte Carlo）
print(f"\nStep 1: 参数抽样...")
np.random.seed(42)
n_samples = np.random.randint(n_range[0], n_range[1]+1, N)
K_samples = np.random.uniform(K_range[0], K_range[1], N)

print(f"  完成！生成{N}组参数")

# Step 2: 计算似然
print(f"\nStep 2: 计算似然...")
likelihoods = np.zeros(N)

for i in range(N):
    n = n_samples[i]
    K = K_samples[i]
    
    # 计算模拟值
    Qp_sim, Tp_sim = calc_peak(n, K)
    
    # 计算似然（双目标）
    L_Qp = np.exp(-0.5 * ((Qp_sim - Qp_obs) / sigma_Qp)**2)
    L_Tp = np.exp(-0.5 * ((Tp_sim - Tp_obs) / sigma_Tp)**2)
    
    # 联合似然
    likelihoods[i] = L_Qp * L_Tp

print(f"  完成！似然范围：[{likelihoods.min():.6f}, {likelihoods.max():.6f}]")

# Step 3: 筛选行为参数
print(f"\nStep 3: 筛选行为参数...")
behavioral_mask = likelihoods > L_threshold
n_behavioral = behavioral_mask.sum()

n_behav = n_samples[behavioral_mask]
K_behav = K_samples[behavioral_mask]
L_behav = likelihoods[behavioral_mask]

print(f"  行为参数数量：{n_behavioral}/{N} ({n_behavioral/N*100:.1f}%)")

if n_behavioral == 0:
    print("  ⚠️  警告：无行为参数！降低阈值重试...")
    L_threshold = 0.001
    behavioral_mask = likelihoods > L_threshold
    n_behavioral = behavioral_mask.sum()
    n_behav = n_samples[behavioral_mask]
    K_behav = K_samples[behavioral_mask]
    L_behav = likelihoods[behavioral_mask]
    print(f"  新阈值 = {L_threshold}，行为参数数量：{n_behavioral}")

# Step 4: 参数后验分布
print(f"\nStep 4: 参数后验分布...")
# 归一化似然
L_normalized = L_behav / L_behav.sum()

# 后验统计
n_posterior_mean = np.average(n_behav, weights=L_normalized)
K_posterior_mean = np.average(K_behav, weights=L_normalized)

n_posterior_std = np.sqrt(np.average((n_behav - n_posterior_mean)**2, weights=L_normalized))
K_posterior_std = np.sqrt(np.average((K_behav - K_posterior_mean)**2, weights=L_normalized))

# 95%置信区间
n_sorted = np.sort(n_behav)
K_sorted = np.sort(K_behav)
n_CI = [n_sorted[int(0.025*n_behavioral)], n_sorted[int(0.975*n_behavioral)]]
K_CI = [K_sorted[int(0.025*n_behavioral)], K_sorted[int(0.975*n_behavioral)]]

print(f"  n的后验分布：")
print(f"    均值 = {n_posterior_mean:.2f}")
print(f"    标准差 = {n_posterior_std:.2f}")
print(f"    95%CI = [{n_CI[0]}, {n_CI[1]}]")

print(f"  K的后验分布：")
print(f"    均值 = {K_posterior_mean:.2f} h")
print(f"    标准差 = {K_posterior_std:.2f} h")
print(f"    95%CI = [{K_CI[0]:.2f}, {K_CI[1]:.2f}] h")

# Step 5: 预测不确定性
print(f"\nStep 5: 预测不确定性...")
time = np.linspace(0, 20, 100)
predictions = np.zeros((n_behavioral, len(time)))

for i in range(n_behavioral):
    for j, t in enumerate(time):
        if t > 0:
            predictions[i, j] = nash_model(t, n_behav[i], K_behav[i])

# 加权预测
weighted_pred = np.average(predictions, weights=L_normalized, axis=0)

# 95%置信区间
pred_lower = np.percentile(predictions, 2.5, axis=0)
pred_upper = np.percentile(predictions, 97.5, axis=0)

# 不确定性度量
avg_width = np.mean(pred_upper - pred_lower)
relative_width = avg_width / np.max(weighted_pred) * 100

print(f"  预测区间平均宽度 = {avg_width:.2f} m³/s")
print(f"  相对宽度 = {relative_width:.1f}%")

print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：参数散点图（先验vs后验）
ax1 = fig.add_subplot(gs[0, :2])
# 所有样本（先验）
ax1.scatter(K_samples[~behavioral_mask], n_samples[~behavioral_mask], 
            s=10, alpha=0.3, color='lightgray', label='非行为参数')
# 行为参数（后验）
scatter = ax1.scatter(K_behav, n_behav, s=50, c=L_behav, alpha=0.7, 
                      cmap='hot', edgecolors='black', linewidth=0.5, label='行为参数')
ax1.plot(K_posterior_mean, n_posterior_mean, 'b*', markersize=20, 
         label=f'后验均值(K={K_posterior_mean:.1f}, n={n_posterior_mean:.1f})')
cbar = plt.colorbar(scatter, ax=ax1)
cbar.set_label('似然L', fontsize=10)
ax1.set_xlabel('K (h)', fontsize=12, fontweight='bold')
ax1.set_ylabel('n', fontsize=12, fontweight='bold')
ax1.set_title('题目2-1：参数空间与行为参数分布', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# 子图2：似然分布
ax2 = fig.add_subplot(gs[0, 2])
ax2.hist(likelihoods, bins=50, color='blue', alpha=0.7, edgecolor='black')
ax2.axvline(L_threshold, color='red', linestyle='--', linewidth=2, label=f'阈值={L_threshold}')
ax2.set_xlabel('似然L', fontsize=11, fontweight='bold')
ax2.set_ylabel('频数', fontsize=11, fontweight='bold')
ax2.set_title('题目2-2：似然分布', fontsize=11, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_yscale('log')

# 子图3：参数后验分布（n）
ax3 = fig.add_subplot(gs[1, 0])
ax3.hist(n_behav, bins=np.arange(n_range[0], n_range[1]+2)-0.5, 
         weights=L_normalized, color='orange', alpha=0.7, edgecolor='black')
ax3.axvline(n_posterior_mean, color='red', linestyle='--', linewidth=2, label=f'均值={n_posterior_mean:.1f}')
ax3.axvline(n_CI[0], color='green', linestyle=':', linewidth=2)
ax3.axvline(n_CI[1], color='green', linestyle=':', linewidth=2, label=f'95%CI=[{n_CI[0]}, {n_CI[1]}]')
ax3.set_xlabel('n', fontsize=11, fontweight='bold')
ax3.set_ylabel('后验概率密度', fontsize=11, fontweight='bold')
ax3.set_title('题目2-3：参数n的后验分布', fontsize=11, fontweight='bold')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3, axis='y')

# 子图4：参数后验分布（K）
ax4 = fig.add_subplot(gs[1, 1])
ax4.hist(K_behav, bins=30, weights=L_normalized, color='cyan', alpha=0.7, edgecolor='black')
ax4.axvline(K_posterior_mean, color='red', linestyle='--', linewidth=2, label=f'均值={K_posterior_mean:.1f}h')
ax4.axvline(K_CI[0], color='green', linestyle=':', linewidth=2)
ax4.axvline(K_CI[1], color='green', linestyle=':', linewidth=2, label=f'95%CI=[{K_CI[0]:.1f}, {K_CI[1]:.1f}]h')
ax4.set_xlabel('K (h)', fontsize=11, fontweight='bold')
ax4.set_ylabel('后验概率密度', fontsize=11, fontweight='bold')
ax4.set_title('题目2-4：参数K的后验分布', fontsize=11, fontweight='bold')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3, axis='y')

# 子图5：GLUE原理
ax5 = fig.add_subplot(gs[1, 2])
ax5.axis('off')
glue_text = f"""
GLUE方法原理：

【核心思想】
  等效性假设：
  多参数组合可能同样好

【流程】
  1. 参数先验抽样
     N = {N}
     
  2. 似然评估
     L = L_Qp × L_Tp
     
  3. 行为参数筛选
     L > {L_threshold}
     保留{n_behavioral}组
     
  4. 后验分布
     归一化似然加权
     
  5. 预测不确定性
     95%置信区间
     
【优势】
  ✓ 概念简单
  ✓ 实现容易
  ✓ 量化不确定性
"""
ax5.text(0.05, 0.95, glue_text, transform=ax5.transAxes,
         fontsize=8.5, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# 子图6：预测不确定性区间
ax6 = fig.add_subplot(gs[2, :])
# 绘制所有行为参数的预测（淡化）
for i in range(min(100, n_behavioral)):  # 最多绘制100条
    ax6.plot(time, predictions[i], color='gray', alpha=0.1, linewidth=0.5)

# 95%置信区间
ax6.fill_between(time, pred_lower, pred_upper, alpha=0.3, color='blue', label='95%置信区间')

# 加权平均预测
ax6.plot(time, weighted_pred, 'r-', linewidth=3, label='加权平均预测')

# 观测点
ax6.plot(Tp_obs, Qp_obs, 'go', markersize=15, label=f'观测洪峰({Tp_obs}h, {Qp_obs}m³/s)', zorder=10)

ax6.set_xlabel('时间 (h)', fontsize=12, fontweight='bold')
ax6.set_ylabel('流量 (m³/s)', fontsize=12, fontweight='bold')
ax6.set_title(f'题目2-5：GLUE预测不确定性区间（平均宽度={avg_width:.1f}m³/s，相对宽度={relative_width:.1f}%）', 
              fontsize=13, fontweight='bold')
ax6.legend(fontsize=11, loc='upper right')
ax6.grid(True, alpha=0.3)
ax6.set_xlim(0, 20)
ax6.set_ylim(0, None)

plt.savefig('题目2_GLUE不确定性量化.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_GLUE不确定性量化.png")
plt.show()
