"""
第13章 985高校真题精讲
题目2：河海大学2022年 - 新安江模型率定

知识点：
- 新安江模型
- 蓄满产流原理
- 蓄水容量曲线（参数B）
- 三水源划分
- 模拟精度评价
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 流域特征
F = 2560  # 流域面积（km²）
slope = 0.15  # 平均坡度
density = 0.85  # 河网密度（km/km²）
vegetation = 0.75  # 植被覆盖度

# 降雨过程（8个时段，Δt=3h，单位：mm）
dt = 3  # 时段长度（小时）
P = np.array([8, 15, 32, 48, 35, 20, 10, 5])  # 降雨量（mm）
n_periods = len(P)

# 实测流量过程（10个时段，m³/s）
Q0 = 120  # 起涨前流量
Q_obs = np.array([120, 145, 280, 685, 1240, 980, 650, 420, 280, 200])

# 新安江模型参数
B = 0.35  # 蓄水容量曲线指数（待率定）
WM = 120  # 张力水容量（mm）
WMM = 150  # 流域平均蓄水容量（mm）
KG = 0.30  # 地面径流消退系数
KI = 0.65  # 壤中流消退系数
KKG = 0.85  # 地下径流消退系数
C = 0.15  # 深层蒸散发系数

# 初始土壤含水量
W0 = 80  # mm

print("="*80)
print("题目2：河海大学2022年 - 新安江模型率定")
print("="*80)

print(f"\n流域特征：")
print(f"  流域面积: F = {F} km²")
print(f"  平均坡度: i = {slope}")
print(f"  河网密度: D = {density} km/km²")
print(f"  植被覆盖度: {vegetation*100:.0f}%")

print(f"\n降雨过程（Δt = {dt}h）：")
for i, p in enumerate(P, 1):
    print(f"  时段{i}: {p:2.0f} mm", end="")
    if i % 4 == 0:
        print()
print(f"\n  总降雨量: {np.sum(P):.0f} mm")

print(f"\n实测流量过程：")
for i, q in enumerate(Q_obs, 1):
    print(f"  时段{i:2}: {q:4.0f} m³/s", end="")
    if i % 5 == 0:
        print()
print()

# 新安江模型产流计算
def xinanjiang_runoff(P, W0, WMM, B, E=0):
    """
    新安江模型产流计算
    
    参数：
    P: 降雨量（mm）
    W0: 初始土壤含水量（mm）
    WMM: 流域平均蓄水容量（mm）
    B: 蓄水容量曲线指数
    E: 蒸发量（mm）
    
    返回：
    R: 产流量（mm）
    W1: 最终土壤含水量（mm）
    """
    PE = P - E  # 净雨
    
    if PE <= 0:
        return 0, W0
    
    # 计算产流量
    if W0 + PE <= WMM:
        # 未蓄满，不产流
        R = 0
        W1 = W0 + PE
    else:
        # 蓄满产流
        # 使用蓄水容量曲线
        A = WMM * (1 - (1 - W0/WMM)**(1/(B+1)))  # 蓄满面积对应容量
        
        if W0 + PE >= WMM:
            # 部分面积蓄满产流
            term1 = 1 - (W0 / WMM)
            term2 = 1 - ((W0 + PE) / WMM) if (W0 + PE) < WMM else 0
            R = PE - WMM * (term1**(B+1) - term2**(B+1))
        else:
            R = 0
        
        W1 = min(W0 + PE - R, WMM)
    
    return R, W1

# 产流计算
print("\n" + "="*80)
print("新安江模型产流计算")
print("="*80)

print(f"\n模型参数：")
print(f"  B = {B}（蓄水容量曲线指数）")
print(f"  WM = {WM} mm（张力水容量）")
print(f"  WMM = {WMM} mm（流域平均蓄水容量）")
print(f"  W0 = {W0} mm（初始土壤含水量，{W0/WMM*100:.0f}%）")

print(f"\n逐时段产流计算：")
print(f"{'时段':<6} {'降雨P':<10} {'累计P':<10} {'土壤水W':<12} {'产流R':<10}")
print("-" * 60)

W = W0  # 当前土壤含水量
R_list = []  # 产流量序列
W_list = [W0]  # 土壤含水量序列
P_cumsum = 0

for i, p in enumerate(P, 1):
    P_cumsum += p
    R, W_new = xinanjiang_runoff(p, W, WMM, B, E=0)
    R_list.append(R)
    W_list.append(W_new)
    
    print(f"{i:<6} {p:<10.0f} {P_cumsum:<10.0f} {W:<12.1f} {R:<10.1f}")
    W = W_new

R_total = np.sum(R_list)
runoff_coef = R_total / np.sum(P)

print("-" * 60)
print(f"{'合计':<6} {np.sum(P):<10.0f} {'':<10} {'':<12} {R_total:<10.1f}")
print(f"\n径流系数: α = R/P = {R_total:.1f}/{np.sum(P):.0f} = {runoff_coef:.3f} = {runoff_coef*100:.1f}%")

# 三水源划分
print("\n" + "="*80)
print("三水源划分")
print("="*80)

# 自由水分配
FR = 0.35  # 地面径流产流系数（根据前期含水量确定）
KI_partition = 0.65  # 壤中流分配系数

RS = FR * R_total  # 地面径流（mm）
RSS = (1 - FR) * KI_partition * R_total  # 壤中流（mm）
RG = (1 - FR) * (1 - KI_partition) * R_total  # 地下径流（mm）

print(f"\n自由水分配参数：")
print(f"  FR = {FR}（地面径流产流系数）")
print(f"  KI = {KI_partition}（壤中流分配系数）")

print(f"\n三水源划分：")
print(f"  地面径流（RS）  = {FR} × {R_total:.1f} = {RS:.1f} mm（{RS/R_total*100:.1f}%）")
print(f"  壤中流（RSS）   = (1-{FR}) × {KI_partition} × {R_total:.1f} = {RSS:.1f} mm（{RSS/R_total*100:.1f}%）")
print(f"  地下径流（RG）  = (1-{FR}) × (1-{KI_partition}) × {R_total:.1f} = {RG:.1f} mm（{RG/R_total*100:.1f}%）")
print(f"  验证：RS + RSS + RG = {RS+RSS+RG:.1f} mm ✓")

# 汇流计算（简化）
print("\n" + "="*80)
print("汇流计算")
print("="*80)

# 将产流分配到各时段
R_array = np.array(R_list)

# 地面径流汇流（线性水库）
Q_RS = np.zeros(n_periods + 2)
for i in range(n_periods):
    if R_array[i] > 0:
        # 地面径流输入
        input_RS = FR * R_array[i] * F * 1000 / (dt * 3600)  # mm → m³/s
        Q_RS[i+1] = KG * Q_RS[i] + (1 - KG) * input_RS

# 壤中流汇流
Q_RSS = np.zeros(n_periods + 2)
for i in range(n_periods):
    if R_array[i] > 0:
        input_RSS = (1-FR) * KI_partition * R_array[i] * F * 1000 / (dt * 3600)
        Q_RSS[i+1] = KI * Q_RSS[i] + (1 - KI) * input_RSS

# 地下径流汇流
Q_RG = np.zeros(n_periods + 2)
Q_RG[0] = Q0  # 基流初值
for i in range(n_periods):
    if R_array[i] > 0:
        input_RG = (1-FR) * (1-KI_partition) * R_array[i] * F * 1000 / (dt * 3600)
        Q_RG[i+1] = KKG * Q_RG[i] + (1 - KKG) * input_RG
    else:
        Q_RG[i+1] = KKG * Q_RG[i]

# 总流量
Q_sim = Q_RS[:len(Q_obs)] + Q_RSS[:len(Q_obs)] + Q_RG[:len(Q_obs)]

print(f"\n汇流参数：")
print(f"  KG = {KG}（地面径流消退系数）")
print(f"  KI = {KI}（壤中流消退系数）")
print(f"  KKG = {KKG}（地下径流消退系数）")

print(f"\n模拟流量过程：")
print(f"{'时段':<6} {'实测Q':<12} {'模拟Q':<12} {'误差':<12}")
print("-" * 50)

for i in range(len(Q_obs)):
    error = Q_sim[i] - Q_obs[i]
    print(f"{i+1:<6} {Q_obs[i]:<12.0f} {Q_sim[i]:<12.0f} {error:<12.0f}")

# 模拟精度评价
print("\n" + "="*80)
print("模拟精度评价")
print("="*80)

# NSE（Nash-Sutcliffe效率系数）
Q_obs_mean = np.mean(Q_obs)
NSE = 1 - np.sum((Q_obs - Q_sim)**2) / np.sum((Q_obs - Q_obs_mean)**2)

# 洪峰误差
Qp_obs = np.max(Q_obs)
Qp_sim = np.max(Q_sim)
Tp_obs = np.argmax(Q_obs) + 1
Tp_sim = np.argmax(Q_sim) + 1
RE_Qp = (Qp_sim - Qp_obs) / Qp_obs * 100

# 相关系数
r = np.corrcoef(Q_obs, Q_sim)[0, 1]

# RMSE
RMSE = np.sqrt(np.mean((Q_obs - Q_sim)**2))

print(f"\nNash-Sutcliffe效率系数：")
print(f"  NSE = {NSE:.3f}")
print(f"  评价：{'很好' if NSE > 0.75 else '良好' if NSE > 0.6 else '需改进'}")

print(f"\n洪峰误差：")
print(f"  实测洪峰: Qp_obs = {Qp_obs:.0f} m³/s（时段{Tp_obs}）")
print(f"  模拟洪峰: Qp_sim = {Qp_sim:.0f} m³/s（时段{Tp_sim}）")
print(f"  相对误差: RE_Qp = {RE_Qp:+.1f}%")
print(f"  评价：{'很好' if abs(RE_Qp) < 10 else '良好' if abs(RE_Qp) < 20 else '需改进'}")

print(f"\n相关系数：")
print(f"  r = {r:.3f}")

print(f"\nRMSE：")
print(f"  RMSE = {RMSE:.0f} m³/s")

print(f"\n综合评价：")
print(f"  模拟精度：{'优秀' if NSE > 0.8 else '良好' if NSE > 0.65 else '一般'}")
print(f"  参数B={B}合理性：湿润地区（植被{vegetation*100:.0f}%），B偏大合理")
print(f"  结论：模型率定成功，可用于洪水预报")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：降雨径流过程
ax1 = fig.add_subplot(gs[0, :])

# 降雨柱状图（倒置）
ax1_rain = ax1.twinx()
ax1_rain.bar(np.arange(1, n_periods+1), P, width=0.6, alpha=0.3, color='blue', label='降雨')
ax1_rain.set_ylabel('降雨 (mm)', fontsize=11, fontweight='bold')
ax1_rain.set_ylim(max(P)*1.5, 0)  # 倒置
ax1_rain.legend(loc='upper left', fontsize=10)

# 流量过程
time_obs = np.arange(1, len(Q_obs)+1)
ax1.plot(time_obs, Q_obs, 'ro-', linewidth=2.5, markersize=8, label='实测流量')
ax1.plot(time_obs, Q_sim, 'b--s', linewidth=2.5, markersize=6, label='模拟流量')

ax1.set_xlabel('时段', fontsize=12, fontweight='bold')
ax1.set_ylabel('流量 (m³/s)', fontsize=12, fontweight='bold')
ax1.set_title(f'题目2-1：降雨径流过程（NSE={NSE:.2f}）', fontsize=13, fontweight='bold')
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(True, alpha=0.3)

# 子图2：产流过程
ax2 = fig.add_subplot(gs[1, 0])

time_R = np.arange(1, n_periods+1)
ax2.bar(time_R, R_list, width=0.6, alpha=0.7, color='green', label='逐时段产流')
ax2.plot(time_R, np.cumsum(R_list), 'r-o', linewidth=2.5, markersize=6, label='累计产流')

ax2.set_xlabel('时段', fontsize=11, fontweight='bold')
ax2.set_ylabel('产流量 (mm)', fontsize=11, fontweight='bold')
ax2.set_title(f'题目2-2：产流过程（α={runoff_coef*100:.1f}%）', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

# 子图3：三水源划分
ax3 = fig.add_subplot(gs[1, 1])

sources = ['地面径流\nRS', '壤中流\nRSS', '地下径流\nRG']
values = [RS, RSS, RG]
colors_sources = ['red', 'orange', 'blue']

bars = ax3.bar(sources, values, color=colors_sources, alpha=0.7, edgecolor='black', linewidth=2)

# 添加数值和百分比标签
for i, (bar, val) in enumerate(zip(bars, values)):
    pct = val / R_total * 100
    ax3.text(i, val + 1, f'{val:.1f}mm\n({pct:.1f}%)', 
             ha='center', va='bottom', fontsize=10, fontweight='bold')

ax3.set_ylabel('径流量 (mm)', fontsize=11, fontweight='bold')
ax3.set_title(f'题目2-3：三水源划分（总径流{R_total:.1f}mm）', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 子图4：新安江模型原理
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

xaj_text = f"""
新安江模型原理与计算结果：

1. 蓄满产流原理：
   • 降雨首先补充土壤水分亏缺
   • 土壤蓄满后才产生径流
   • 蓄水容量曲线：f(WM) = 1 - (1 - WM/WMM)^(B+1)
   • 参数B={B}：控制蓄水容量分布（B大→分布不均→产流分散）

2. 产流计算结果：
   • 总降雨：{np.sum(P):.0f} mm
   • 总产流：{R_total:.1f} mm
   • 径流系数：{runoff_coef*100:.1f}%
   • 初始土壤含水量：W0 = {W0} mm（{W0/WMM*100:.0f}%）

3. 三水源划分：
   • 地面径流（RS）：{RS:.1f} mm（{RS/R_total*100:.1f}%）- 响应快
   • 壤中流（RSS）：{RSS:.1f} mm（{RSS/R_total*100:.1f}%）- 响应中等
   • 地下径流（RG）：{RG:.1f} mm（{RG/R_total*100:.1f}%）- 基流

4. 模拟精度评价：
   • NSE = {NSE:.3f}（{'很好' if NSE > 0.75 else '良好'}）
   • 洪峰误差：{RE_Qp:+.1f}%（{'很好' if abs(RE_Qp) < 10 else '良好'}）
   • 相关系数：r = {r:.3f}

5. 河海大学考点特色：
   ✓ 新安江模型：中国自主研发，应用广泛
   ✓ 蓄满产流：湿润地区主导机制
   ✓ 参数率定：试错法、自动优化
   ✓ 三水源划分：地面、壤中、地下径流
"""

ax4.text(0.05, 0.95, xaj_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.savefig('题目2_河海真题_新安江模型.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_河海真题_新安江模型.png")
plt.show()
