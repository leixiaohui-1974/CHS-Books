"""
第13章 985高校真题精讲
题目1：清华大学2021年 - 设计洪水计算

知识点：
- P-III型分布
- 适线法参数复核
- 设计洪峰计算
- 特大值处理
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import stats

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 水文资料
n_years = 61  # 61年资料（1960-2020）
Q_mean = 2680  # 平均洪峰流量（m³/s）
Cv = 0.85  # 变差系数（初值）
Cs_Cv = 3.5  # 偏态系数与变差系数比值（初值）

# 历史特大洪水
Q_max = 8650  # 1998年
Q_2nd = 7820  # 2016年
Q_3rd = 6950  # 1975年
Q_median = 2340  # 中位数

# 2021年新增洪水
Q_2021 = 9200  # m³/s

print("="*80)
print("题目1：清华大学2021年 - 设计洪水计算")
print("="*80)

print(f"\n水文资料：")
print(f"  系列长度: {n_years} 年（1960-2020）")
print(f"  平均洪峰: Q̄ = {Q_mean} m³/s")
print(f"  变差系数: Cv = {Cv}")
print(f"  偏态系数比: Cs/Cv = {Cs_Cv}")
print(f"  历史最大: {Q_max} m³/s（1998年）")
print(f"  历史次大: {Q_2nd} m³/s（2016年）")

# 生成模拟洪峰序列（简化，用P-III型生成）
np.random.seed(42)
# 使用Gamma分布模拟P-III型
alpha = 4 / Cv**2  # 形状参数
scale = Q_mean * Cv**2 / 4  # 尺度参数
Q_series = stats.gamma.rvs(alpha, scale=scale, size=n_years-3)
Q_series = np.sort(Q_series)[::-1]  # 降序排列

# 插入已知的前3大值
Q_series = np.concatenate([[Q_max, Q_2nd, Q_3rd], Q_series[:-3]])

# 计算经验频率（Weibull公式）
m = np.arange(1, n_years+1)  # 序号
P_empirical = m / (n_years + 1) * 100  # 经验频率（%）

print(f"\n经验频率计算（Weibull公式）：")
print(f"  P = m / (n+1) × 100%")
print(f"  最大值频率: P₁ = 1/62 = {P_empirical[0]:.2f}%")
print(f"  次大值频率: P₂ = 2/62 = {P_empirical[1]:.2f}%")

# P-III型分布理论频率计算
def calculate_Phi_PIII(P, Cv, Cs_Cv):
    """
    计算P-III型分布的离均系数Φ
    使用威尔逊-希尔费蒂法近似
    """
    Cs = Cs_Cv * Cv
    z = stats.norm.ppf(1 - P/100)  # 标准正态分位数
    
    # 威尔逊-希尔费蒂近似公式
    Phi = 2/Cs * ((z - Cs/6)**3 + 1)**(1/3) - 2/Cs + Cs/6
    
    return Phi

def calculate_QP(Q_mean, Cv, Cs_Cv, P):
    """计算P频率对应的流量"""
    Phi = calculate_Phi_PIII(P, Cv, Cs_Cv)
    KP = 1 + Cv * Phi
    QP = Q_mean * KP
    return QP, KP, Phi

# 参数率定（适线法）
print("\n" + "="*80)
print("适线法参数率定")
print("="*80)

# 尝试不同的Cv和Cs/Cv组合
Cv_trials = [0.80, 0.82, 0.85, 0.88]
Cs_Cv_trials = [3.2, 3.4, 3.5, 3.6]

best_Cv = Cv
best_Cs_Cv = Cs_Cv
min_error = float('inf')

print(f"\n试验不同参数组合：")
print(f"{'Cv':<8} {'Cs/Cv':<8} {'Q1%(m³/s)':<12} {'误差平方和':<12}")
print("-" * 50)

for Cv_trial in Cv_trials:
    for Cs_Cv_trial in Cs_Cv_trials:
        # 计算理论流量
        Q_theory = np.array([calculate_QP(Q_mean, Cv_trial, Cs_Cv_trial, p)[0] 
                             for p in P_empirical])
        
        # 计算误差（重点关注大值段，P<10%）
        mask = P_empirical < 10
        error = np.sum((Q_series[mask] - Q_theory[mask])**2)
        
        # 仅打印部分组合
        if Cv_trial in [0.82, 0.85] and Cs_Cv_trial in [3.5, 3.6]:
            Q1_pct = calculate_QP(Q_mean, Cv_trial, Cs_Cv_trial, 1.0)[0]
            print(f"{Cv_trial:<8.2f} {Cs_Cv_trial:<8.1f} {Q1_pct:<12.0f} {error:<12.0f}")
        
        if error < min_error:
            min_error = error
            best_Cv = Cv_trial
            best_Cs_Cv = Cs_Cv_trial

print(f"\n最优参数：")
print(f"  Cv = {best_Cv}")
print(f"  Cs/Cv = {best_Cs_Cv}")
print(f"  Cs = {best_Cv * best_Cs_Cv:.3f}")

# 设计洪峰计算
print("\n" + "="*80)
print("设计洪峰计算")
print("="*80)

# 设计标准
P_design = 1.0  # 100年一遇
P_check = 0.1   # 1000年一遇

# 计算设计值
Q1, K1, Phi1 = calculate_QP(Q_mean, best_Cv, best_Cs_Cv, P_design)
Q01, K01, Phi01 = calculate_QP(Q_mean, best_Cv, best_Cs_Cv, P_check)

print(f"\n采用参数：Cv = {best_Cv}, Cs/Cv = {best_Cs_Cv}")

print(f"\n设计洪峰（100年一遇，P=1%）：")
print(f"  Φ₁% = {Phi1:.3f}")
print(f"  K₁% = 1 + Cv·Φ = 1 + {best_Cv}×{Phi1:.3f} = {K1:.3f}")
print(f"  Q₁% = Q̄·K₁% = {Q_mean}×{K1:.3f} = {Q1:.0f} m³/s")

print(f"\n校核洪峰（1000年一遇，P=0.1%）：")
print(f"  Φ₀.₁% = {Phi01:.3f}")
print(f"  K₀.₁% = 1 + Cv·Φ = 1 + {best_Cv}×{Phi01:.3f} = {K01:.3f}")
print(f"  Q₀.₁% = Q̄·K₀.₁% = {Q_mean}×{K01:.3f} = {Q01:.0f} m³/s")

# 2021年特大洪水分析
print("\n" + "="*80)
print("2021年特大洪水分析")
print("="*80)

print(f"\n2021年实测洪峰: {Q_2021} m³/s")
print(f"  超过历史最大值（{Q_max}）: {(Q_2021-Q_max)/Q_max*100:+.1f}%")
print(f"  超过设计值Q₁%（{Q1:.0f}）: {(Q_2021-Q1)/Q1*100:+.1f}%")

# 估算重现期
P_2021_pct = 100 - 100 * stats.gamma.cdf(Q_2021, 4/best_Cv**2, scale=Q_mean*best_Cv**2/4)
T_2021 = 100 / P_2021_pct
print(f"  估算重现期: 约{T_2021:.0f}年一遇")

# 是否修正参数
Q_mean_new = (Q_mean * n_years + Q_2021) / (n_years + 1)
print(f"\n是否修正参数讨论：")
print(f"  若加入2021年数据：")
print(f"    新系列长度: {n_years+1} 年")
print(f"    新平均值: Q̄_new = {Q_mean_new:.0f} m³/s（+{Q_mean_new-Q_mean:.0f}，+{(Q_mean_new-Q_mean)/Q_mean*100:.1f}%）")
print(f"    新Q₁%估计: 约{Q_mean_new*K1:.0f} m³/s")
print(f"\n  推荐：不修正")
print(f"    理由1: {Q_2021} < {Q01:.0f}（校核标准内）")
print(f"    理由2: 增加1年对参数影响小（<5%）")
print(f"    理由3: 工程经济性考虑")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：频率曲线（对数频率格纸）
ax1 = fig.add_subplot(gs[0, :])

# 理论频率曲线
P_theory = np.logspace(-1, 2, 100)  # 0.1% 到 99.9%
Q_theory = np.array([calculate_QP(Q_mean, best_Cv, best_Cs_Cv, p)[0] for p in P_theory])

# 绘制理论线
ax1.plot(P_theory, Q_theory, 'b-', linewidth=2.5, label=f'P-III型理论线\n(Cv={best_Cv}, Cs/Cv={best_Cs_Cv})')

# 绘制经验点
ax1.plot(P_empirical, Q_series, 'ro', markersize=6, alpha=0.6, label='实测点（1960-2020）')

# 标注关键点
ax1.plot(P_design, Q1, 'g^', markersize=15, markeredgewidth=2, 
         label=f'设计洪峰 Q₁%={Q1:.0f} m³/s')
ax1.plot(P_check, Q01, 'm^', markersize=15, markeredgewidth=2,
         label=f'校核洪峰 Q₀.₁%={Q01:.0f} m³/s')

# 标注2021年洪水
ax1.plot(P_2021_pct, Q_2021, 'r*', markersize=20, markeredgewidth=2,
         label=f'2021年洪水 {Q_2021} m³/s')

ax1.set_xlabel('频率 P (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('洪峰流量 (m³/s)', fontsize=12, fontweight='bold')
ax1.set_title('题目1-1：P-III型频率曲线（对数坐标）', fontsize=13, fontweight='bold')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlim(0.05, 100)
ax1.set_ylim(500, 15000)
ax1.legend(fontsize=10, loc='lower left')
ax1.grid(True, alpha=0.3, which='both')

# 子图2：参数敏感性分析
ax2 = fig.add_subplot(gs[1, 0])

Cv_range = np.linspace(0.75, 0.95, 20)
Q1_vs_Cv = [calculate_QP(Q_mean, cv, best_Cs_Cv, P_design)[0] for cv in Cv_range]

ax2.plot(Cv_range, Q1_vs_Cv, 'b-', linewidth=2.5)
ax2.plot(best_Cv, Q1, 'ro', markersize=12, label=f'最优Cv={best_Cv}')
ax2.axhline(y=Q_max, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='历史最大值')

ax2.set_xlabel('变差系数 Cv', fontsize=11, fontweight='bold')
ax2.set_ylabel('设计洪峰 Q₁% (m³/s)', fontsize=11, fontweight='bold')
ax2.set_title('题目1-2：Cv参数敏感性', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

# 子图3：Cs/Cv参数敏感性
ax3 = fig.add_subplot(gs[1, 1])

Cs_Cv_range = np.linspace(3.0, 4.0, 20)
Q1_vs_Cs_Cv = [calculate_QP(Q_mean, best_Cv, cs_cv, P_design)[0] for cs_cv in Cs_Cv_range]

ax3.plot(Cs_Cv_range, Q1_vs_Cs_Cv, 'g-', linewidth=2.5)
ax3.plot(best_Cs_Cv, Q1, 'ro', markersize=12, label=f'最优Cs/Cv={best_Cs_Cv}')
ax3.axhline(y=Q_max, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='历史最大值')

ax3.set_xlabel('偏态系数比 Cs/Cv', fontsize=11, fontweight='bold')
ax3.set_ylabel('设计洪峰 Q₁% (m³/s)', fontsize=11, fontweight='bold')
ax3.set_title('题目1-3：Cs/Cv参数敏感性', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# 子图4：P-III型分布原理
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

piii_text = f"""
P-III型分布计算原理：

1. 基本公式：
   QP = Q̄ × KP
   KP = 1 + Cv × ΦP
   ΦP = f(P, Cv, Cs/Cv)  # 查P-III型表或用近似公式

2. 参数意义：
   • Q̄ = {Q_mean} m³/s  # 多年平均洪峰
   • Cv = {best_Cv}  # 变差系数，反映离散程度
   • Cs = {best_Cv*best_Cs_Cv:.2f}  # 偏态系数，反映不对称性
   • Cs/Cv = {best_Cs_Cv}  # 偏态系数比

3. 设计值计算结果：
   • 设计洪峰（P=1%）：Q₁% = {Q1:.0f} m³/s（100年一遇）
   • 校核洪峰（P=0.1%）：Q₀.₁% = {Q01:.0f} m³/s（1000年一遇）
   
4. 2021年特大洪水：
   • 实测：{Q_2021} m³/s
   • 超过设计值：{(Q_2021-Q1)/Q1*100:+.1f}%
   • 估算重现期：约{T_2021:.0f}年一遇
   • 建议：不修正参数（理由见解答）

5. 清华大学考点特色：
   ✓ 理论深度：P-III型分布原理、适线法
   ✓ 工程实践：设计标准选择、特大值处理
   ✓ 综合判断：参数修正与否的权衡
"""

ax4.text(0.05, 0.95, piii_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.savefig('题目1_清华真题_设计洪水.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_清华真题_设计洪水.png")
plt.show()
