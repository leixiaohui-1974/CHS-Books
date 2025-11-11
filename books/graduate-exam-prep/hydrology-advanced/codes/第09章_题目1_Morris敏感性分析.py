"""
第9章 水文不确定性分析
题目1：参数敏感性分析（Morris方法）

知识点：
- Morris筛选法原理
- 轨迹抽样设计
- 基本效应计算
- 敏感性指标μ*和σ
- 参数分类与筛选
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 简化水文模型
def hydro_model(W, alpha, K, C, tau, P=80, E=10, lam=0.5):
    """
    简化水文模型
    R = C * max(0, P - E - λW) * exp(-Kτ/1000)
    """
    R = C * max(0, P - E - lam * W) * np.exp(-K * tau / 1000)
    return R

# 参数范围
param_ranges = {
    'W': [100, 200],
    'alpha': [0.5, 1.2],
    'K': [2, 10],
    'C': [0.1, 0.5],
    'tau': [6, 18]
}
param_names = ['W', 'alpha', 'K', 'C', 'tau']
k = len(param_names)

# Morris抽样
r = 10  # 轨迹数
p = 6   # 水平数
delta = 0.6  # 步长（归一化空间）

print("="*70)
print("题目1：参数敏感性分析（Morris方法）")
print("="*70)
print(f"\nMorris抽样参数：")
print(f"  轨迹数 r = {r}")
print(f"  水平数 p = {p}")
print(f"  参数个数 k = {k}")
print(f"  步长 Δ = {delta}（归一化）")
print(f"  总运行次数 = r×(k+1) = {r*(k+1)}")

# 参数离散化
def discretize_params(p):
    """将参数空间离散化为p个水平"""
    levels = {}
    for name in param_names:
        min_val, max_val = param_ranges[name]
        levels[name] = np.linspace(min_val, max_val, p)
    return levels

levels = discretize_params(p)
print(f"\n参数离散水平：")
for name in param_names:
    print(f"  {name}: {levels[name]}")

# Morris轨迹生成
def generate_morris_trajectory(levels, delta_normalized=0.6):
    """生成一条Morris轨迹"""
    # 随机初始点（从离散水平中选择）
    trajectory = []
    current = {name: np.random.choice(levels[name]) for name in param_names}
    trajectory.append(current.copy())
    
    # 随机参数顺序
    order = np.random.permutation(param_names)
    
    # 依次改变每个参数
    for param in order:
        # 随机选择增加或减少
        direction = np.random.choice([-1, 1])
        current_idx = np.where(levels[param] == current[param])[0][0]
        
        # 计算步长（实际值空间）
        step = int(delta_normalized * (p - 1))
        new_idx = current_idx + direction * step
        new_idx = np.clip(new_idx, 0, p - 1)
        
        current[param] = levels[param][new_idx]
        trajectory.append(current.copy())
    
    return trajectory

# 生成r条轨迹并计算基本效应
np.random.seed(42)  # 保证可重复性
EE_all = {name: [] for name in param_names}

print(f"\n正在生成{r}条Morris轨迹并计算基本效应...")
for i in range(r):
    trajectory = generate_morris_trajectory(levels, delta)
    
    # 计算基本效应
    for j in range(len(trajectory) - 1):
        # 找出改变的参数
        changed_param = None
        for name in param_names:
            if trajectory[j][name] != trajectory[j+1][name]:
                changed_param = name
                break
        
        if changed_param:
            # 计算模型输出
            y1 = hydro_model(**trajectory[j])
            y2 = hydro_model(**trajectory[j+1])
            
            # 基本效应
            delta_param = trajectory[j+1][changed_param] - trajectory[j][changed_param]
            EE = (y2 - y1) / delta_param
            EE_all[changed_param].append(EE)

print(f"完成！共计算{sum(len(v) for v in EE_all.values())}个基本效应")

# 计算Morris指标
morris_stats = {}
for name in param_names:
    EE = np.array(EE_all[name])
    mu = np.mean(EE)
    mu_star = np.mean(np.abs(EE))
    sigma = np.std(EE, ddof=1)
    morris_stats[name] = {'mu': mu, 'mu_star': mu_star, 'sigma': sigma, 'EE': EE}

print(f"\nMorris敏感性指标：")
print(f"{'参数':<8} {'μ':<12} {'μ*':<12} {'σ':<12} {'σ/μ*':<12} {'特征'}")
print("-"*70)
for name in param_names:
    mu = morris_stats[name]['mu']
    mu_star = morris_stats[name]['mu_star']
    sigma = morris_stats[name]['sigma']
    ratio = sigma / mu_star if mu_star > 1e-6 else 0
    
    # 分类
    if mu_star > 0.5 and ratio < 0.3:
        category = "重要-线性"
    elif mu_star > 0.5 and ratio >= 0.3:
        category = "重要-非线性"
    elif mu_star <= 0.5:
        category = "不重要"
    else:
        category = "-"
    
    print(f"{name:<8} {mu:<12.4f} {mu_star:<12.4f} {sigma:<12.4f} {ratio:<12.4f} {category}")

# 敏感性排序
sorted_params = sorted(param_names, key=lambda x: morris_stats[x]['mu_star'], reverse=True)
print(f"\n敏感性排序（按μ*降序）：")
for i, name in enumerate(sorted_params, 1):
    mu_star = morris_stats[name]['mu_star']
    print(f"  {i}. {name:<8} (μ* = {mu_star:.4f})")

# 率定建议
print(f"\n参数率定建议：")
high_sens = [name for name in param_names if morris_stats[name]['mu_star'] > 0.5]
mid_sens = [name for name in param_names if 0.1 < morris_stats[name]['mu_star'] <= 0.5]
low_sens = [name for name in param_names if morris_stats[name]['mu_star'] <= 0.1]

if high_sens:
    print(f"  优先率定：{', '.join(high_sens)}")
if mid_sens:
    print(f"  次要率定：{', '.join(mid_sens)}")
if low_sens:
    print(f"  可固定：{', '.join(low_sens)}")

print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：μ*-σ散点图（Morris图）
ax1 = fig.add_subplot(gs[0, :2])
colors_map = {'C': 'red', 'W': 'orange', 'K': 'blue', 'tau': 'green', 'alpha': 'gray'}
for name in param_names:
    mu_star = morris_stats[name]['mu_star']
    sigma = morris_stats[name]['sigma']
    ax1.scatter(mu_star, sigma, s=300, alpha=0.7, 
                color=colors_map.get(name, 'black'), 
                edgecolors='black', linewidth=2, label=name)
    ax1.text(mu_star, sigma + 0.02, name, ha='center', fontsize=11, fontweight='bold')

# 添加分类线
ax1.axvline(0.5, color='red', linestyle='--', alpha=0.3, label='μ*=0.5（重要性阈值）')
ax1.set_xlabel('μ* (绝对平均基本效应)', fontsize=12, fontweight='bold')
ax1.set_ylabel('σ (基本效应标准差)', fontsize=12, fontweight='bold')
ax1.set_title('题目1-1：Morris敏感性分析（μ*-σ图）', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10, loc='best')

# 子图2：敏感性排序（水平柱状图）
ax2 = fig.add_subplot(gs[0, 2])
mu_stars = [morris_stats[name]['mu_star'] for name in sorted_params]
colors = [colors_map.get(name, 'gray') for name in sorted_params]
bars = ax2.barh(range(len(sorted_params)), mu_stars, color=colors, alpha=0.7, edgecolor='black')
ax2.set_yticks(range(len(sorted_params)))
ax2.set_yticklabels(sorted_params)
ax2.set_xlabel('μ*', fontsize=11, fontweight='bold')
ax2.set_title('题目1-2：参数敏感性排序', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')
for i, (bar, val) in enumerate(zip(bars, mu_stars)):
    ax2.text(val + 0.02, i, f'{val:.3f}', va='center', fontsize=9)

# 子图3：基本效应分布（箱线图）
ax3 = fig.add_subplot(gs[1, :2])
EE_data = [morris_stats[name]['EE'] for name in sorted_params]
bp = ax3.boxplot(EE_data, labels=sorted_params, patch_artist=True)
for patch, name in zip(bp['boxes'], sorted_params):
    patch.set_facecolor(colors_map.get(name, 'gray'))
    patch.set_alpha(0.7)
ax3.axhline(0, color='red', linestyle='--', alpha=0.5, linewidth=2)
ax3.set_ylabel('基本效应 EE', fontsize=12, fontweight='bold')
ax3.set_title('题目1-3：各参数基本效应分布（箱线图）', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 子图4：参数分类与率定建议
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis('off')
classification_text = f"""
参数分类：

【高敏感性】（μ*>0.5）
  优先率定：{', '.join(high_sens) if high_sens else '无'}
  - 对模型输出影响大
  - 需要精确率定
  
【中等敏感性】（0.1<μ*≤0.5）
  次要率定：{', '.join(mid_sens) if mid_sens else '无'}
  - 中等影响
  - 适度率定
  
【低敏感性】（μ*≤0.1）
  可固定：{', '.join(low_sens) if low_sens else '无'}
  - 影响小
  - 固定为经验值
  
非线性/交互：
  σ/μ*>0.3的参数存在
  非线性效应或参数交互
"""
ax4.text(0.05, 0.95, classification_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# 子图5：敏感参数效应趋势（单因子分析）
ax5 = fig.add_subplot(gs[2, :2])
top3_params = sorted_params[:3]  # 选择前3个敏感参数
for name in top3_params:
    param_range = levels[name]
    outputs = []
    # 固定其他参数为中值
    base_params = {n: np.median(levels[n]) for n in param_names}
    for val in param_range:
        base_params[name] = val
        output = hydro_model(**base_params)
        outputs.append(output)
    ax5.plot(param_range, outputs, 'o-', linewidth=2.5, markersize=8, 
             label=name, color=colors_map.get(name, 'black'))

ax5.set_xlabel('参数值', fontsize=12, fontweight='bold')
ax5.set_ylabel('径流量 R (mm)', fontsize=12, fontweight='bold')
ax5.set_title('题目1-4：敏感参数效应趋势（单因子分析）', fontsize=13, fontweight='bold')
ax5.legend(fontsize=11)
ax5.grid(True, alpha=0.3)

# 子图6：Morris方法原理示意
ax6 = fig.add_subplot(gs[2, 2])
ax6.axis('off')
morris_text = f"""
Morris方法原理：

【基本效应】
  EE = (f(x+Δ) - f(x)) / Δ
  
【敏感性指标】
  μ* = 平均|EE| → 重要性
  σ = std(EE) → 非线性/交互
  
【抽样策略】
  - r = {r}条轨迹
  - 每条轨迹 {k+1}个点
  - 总运行：{r*(k+1)}次
  
【优势】
  ✓ 计算高效
  ✓ 全局敏感性
  ✓ 参数筛选
  ✓ 识别交互作用
  
【应用】
  Step1: Morris筛选
  Step2: Sobol'精确分析
  Step3: 参数率定
"""
ax6.text(0.05, 0.95, morris_text, transform=ax6.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

plt.savefig('题目1_Morris敏感性分析.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_Morris敏感性分析.png")
plt.show()
