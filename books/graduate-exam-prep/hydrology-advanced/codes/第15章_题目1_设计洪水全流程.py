"""
第15章 综合应用与压轴题
题目1：跨章节综合 - 设计洪水全流程计算

知识点：
- P-III型分布（第1章）
- 适线法（第2章）
- 统计参数估计（第3章）
- 特大值处理
- 多方法一致性
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import stats

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 流域特征
F = 3850  # 流域面积（km²）
L = 125  # 主河道长度（km）
i = 0.008  # 平均坡度

# 洪峰统计参数
Q_mean = 3680  # 均值（m³/s）
Cv_Q = 0.75  # 变差系数（初值）
Cs_Cv_Q = 3.5  # 偏态系数比（初值）
n_Q = 50  # 系列长度

# 暴雨统计参数
P_mean = 125  # 均值（mm）
Cv_P = 0.45  # 变差系数（初值）
Cs_Cv_P = 3.2  # 偏态系数比（初值）
n_P = 30  # 系列长度

# 2020年特大值
Q_2020 = 9850  # m³/s
P_2020 = 225  # mm

print("="*80)
print("题目1：跨章节综合 - 设计洪水全流程计算")
print("="*80)

print(f"\n流域特征：")
print(f"  流域面积: F = {F} km²")
print(f"  主河道长度: L = {L} km")
print(f"  平均坡度: i = {i}")

print(f"\n洪峰统计参数（初值）：")
print(f"  Q̄ = {Q_mean} m³/s, Cv = {Cv_Q}, Cs/Cv = {Cs_Cv_Q}")
print(f"  系列长度: n = {n_Q} 年（1970-2019）")

print(f"\n暴雨统计参数（初值）：")
print(f"  P̄ = {P_mean} mm, Cv = {Cv_P}, Cs/Cv = {Cs_Cv_P}")
print(f"  系列长度: n = {n_P} 年（1990-2019）")

# P-III型分布计算函数
def calculate_Phi_PIII(P, Cv, Cs_Cv):
    """计算P-III型离均系数"""
    Cs = Cs_Cv * Cv
    z = stats.norm.ppf(1 - P/100)
    Phi = 2/Cs * ((z - Cs/6)**3 + 1)**(1/3) - 2/Cs + Cs/6
    return Phi

def calculate_QP(mean, Cv, Cs_Cv, P_freq):
    """计算P频率对应的值"""
    Phi = calculate_Phi_PIII(P_freq, Cv, Cs_Cv)
    KP = 1 + Cv * Phi
    QP = mean * KP
    return QP, KP, Phi

# 适线法参数率定（假设调整后）
Cv_Q_adj = 0.72  # 洪峰调整后
Cs_Cv_Q_adj = 3.6
Cv_P_adj = 0.43  # 暴雨调整后
Cs_Cv_P_adj = 3.3

print("\n" + "="*80)
print("适线法参数率定")
print("="*80)

print(f"\n洪峰参数调整：")
print(f"  Cv: {Cv_Q} → {Cv_Q_adj}")
print(f"  Cs/Cv: {Cs_Cv_Q} → {Cs_Cv_Q_adj}")

print(f"\n暴雨参数调整：")
print(f"  Cv: {Cv_P} → {Cv_P_adj}")
print(f"  Cs/Cv: {Cs_Cv_P} → {Cs_Cv_P_adj}")

# 设计值计算
P_design = [1.0, 0.1]  # 设计频率

print("\n" + "="*80)
print("设计值计算")
print("="*80)

# 洪峰设计值
print(f"\n洪峰设计值：")
Q_designs = {}
for p in P_design:
    Q, K, Phi = calculate_QP(Q_mean, Cv_Q_adj, Cs_Cv_Q_adj, p)
    Q_designs[p] = Q
    print(f"  P = {p}%: Φ = {Phi:.3f}, K = {K:.3f}, Q = {Q:.0f} m³/s")

# 暴雨设计值
print(f"\n暴雨设计值：")
P_designs = {}
for p in P_design:
    P, K, Phi = calculate_QP(P_mean, Cv_P_adj, Cs_Cv_P_adj, p)
    P_designs[p] = P
    print(f"  P = {p}%: Φ = {Phi:.3f}, K = {K:.3f}, P = {P:.0f} mm")

# 2020年特大值分析
print("\n" + "="*80)
print("2020年特大值分析")
print("="*80)

print(f"\n2020年实测：")
print(f"  洪峰: {Q_2020} m³/s")
print(f"  暴雨: {P_2020} mm")

# 与设计值对比
Q1 = Q_designs[1.0]
P1 = P_designs[1.0]

print(f"\n与设计值对比：")
print(f"  洪峰: {Q_2020} vs Q₁% = {Q1:.0f} ({'超过' if Q_2020 > Q1 else '未超过'})")
print(f"  暴雨: {P_2020} vs P₁% = {P1:.0f} ({'超过' if P_2020 > P1 else '未超过'})")

# 是否修正参数
print(f"\n参数修正建议：")
if Q_2020 < Q1 and P_2020 < P1:
    print(f"  推荐：不修正")
    print(f"  理由：特大值未超设计标准，属正常波动")
else:
    print(f"  推荐：考虑修正")
    print(f"  理由：特大值超过设计标准")

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：洪峰频率曲线
ax1 = fig.add_subplot(gs[0, :])

# 生成理论曲线
P_range = np.logspace(-1, 2, 100)
Q_theory = [calculate_QP(Q_mean, Cv_Q_adj, Cs_Cv_Q_adj, p)[0] for p in P_range]

ax1.plot(P_range, Q_theory, 'b-', linewidth=2.5, label='P-III型理论线')
ax1.plot(1.0, Q1, 'r^', markersize=15, markeredgewidth=2, label=f'Q₁% = {Q1:.0f} m³/s')
ax1.plot(0.1, Q_designs[0.1], 'm^', markersize=15, markeredgewidth=2, label=f'Q₀.₁% = {Q_designs[0.1]:.0f} m³/s')
ax1.plot(1.0, Q_2020, 'r*', markersize=20, markeredgewidth=2, label=f'2020年 {Q_2020} m³/s')

ax1.set_xlabel('频率 P (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('洪峰流量 (m³/s)', fontsize=12, fontweight='bold')
ax1.set_title('题目1-1：洪峰频率曲线（对数坐标）', fontsize=13, fontweight='bold')
ax1.set_xscale('log')
ax1.set_xlim(0.05, 100)
ax1.legend(fontsize=11, loc='lower left')
ax1.grid(True, alpha=0.3, which='both')

# 子图2：暴雨频率曲线
ax2 = fig.add_subplot(gs[1, 0])

P_theory_rain = [calculate_QP(P_mean, Cv_P_adj, Cs_Cv_P_adj, p)[0] for p in P_range]

ax2.plot(P_range, P_theory_rain, 'b-', linewidth=2.5, label='P-III型理论线')
ax2.plot(1.0, P1, 'r^', markersize=15, markeredgewidth=2, label=f'P₁% = {P1:.0f} mm')
ax2.plot(0.1, P_designs[0.1], 'm^', markersize=15, markeredgewidth=2, label=f'P₀.₁% = {P_designs[0.1]:.0f} mm')
ax2.plot(1.0, P_2020, 'r*', markersize=20, markeredgewidth=2, label=f'2020年 {P_2020} mm')

ax2.set_xlabel('频率 P (%)', fontsize=11, fontweight='bold')
ax2.set_ylabel('24h暴雨 (mm)', fontsize=11, fontweight='bold')
ax2.set_title('题目1-2：暴雨频率曲线（对数坐标）', fontsize=12, fontweight='bold')
ax2.set_xscale('log')
ax2.set_xlim(0.05, 100)
ax2.legend(fontsize=10, loc='lower left')
ax2.grid(True, alpha=0.3, which='both')

# 子图3：洪峰法vs暴雨法对比
ax3 = fig.add_subplot(gs[1, 1])

methods = ['洪峰法', '暴雨法']
Q1_values = [Q1, 7130]  # 暴雨法简化估算
Q01_values = [Q_designs[0.1], 9500]

x = np.arange(len(methods))
width = 0.35

bars1 = ax3.bar(x - width/2, Q1_values, width, label='P=1%', color='red', alpha=0.7)
bars2 = ax3.bar(x + width/2, Q01_values, width, label='P=0.1%', color='blue', alpha=0.7)

ax3.set_ylabel('洪峰流量 (m³/s)', fontsize=11, fontweight='bold')
ax3.set_title('题目1-3：洪峰法vs暴雨法对比', fontsize=12, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(methods)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# 子图4：综合分析
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

summary_text = f"""
设计洪水全流程计算结果：

1. 洪峰法（P-III型分布）：
   • 参数：Q̄ = {Q_mean} m³/s, Cv = {Cv_Q_adj}, Cs/Cv = {Cs_Cv_Q_adj}
   • Q₁% = {Q1:.0f} m³/s（100年一遇）
   • Q₀.₁% = {Q_designs[0.1]:.0f} m³/s（1000年一遇）

2. 暴雨法（P-III型分布）：
   • 参数：P̄ = {P_mean} mm, Cv = {Cv_P_adj}, Cs/Cv = {Cs_Cv_P_adj}
   • P₁% = {P1:.0f} mm（100年一遇）
   • P₀.₁% = {P_designs[0.1]:.0f} mm（1000年一遇）

3. 2020年特大值分析：
   • 洪峰：{Q_2020} m³/s（{'低于' if Q_2020 < Q1 else '超过'}Q₁% {abs(Q_2020-Q1):.0f} m³/s）
   • 暴雨：{P_2020} mm（{'低于' if P_2020 < P1 else '超过'}P₁% {abs(P_2020-P1):.0f} mm）
   • 结论：{'特大值未超设计标准，建议不修正参数' if Q_2020 < Q1 else '特大值超设计标准，建议修正参数'}

4. 方法一致性分析：
   • 洪峰法更可靠（实测资料50年 > 暴雨资料30年）
   • 暴雨法需模型推求，不确定性较大
   • 推荐采用洪峰法设计值

5. 综合应用要点：
   ✓ 跨章节综合（第1-3章）
   ✓ P-III型分布理论与适线法
   ✓ 特大值处理的工程判断
   ✓ 多方法一致性检验
"""

ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.savefig('题目1_设计洪水全流程.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_设计洪水全流程.png")
print("="*80)
plt.show()
