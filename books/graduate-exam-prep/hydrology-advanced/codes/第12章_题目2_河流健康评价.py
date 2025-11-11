"""
第12章 生态水文
题目2：河流健康评价

知识点：
- 河流健康评价概念
- 水文改变度（Hydrologic Alteration）
- IHA指标体系
- 生态影响评价
- 生态修复建议
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 筑坝前后水文指标
indicators = ['年均流量', '最大流量', '最小流量', '洪峰频率', '枯水历时']
before_dam = np.array([500, 2500, 100, 3.5, 45])  # 筑坝前
after_dam = np.array([480, 1200, 150, 1.2, 20])   # 筑坝后
units = ['m³/s', 'm³/s', 'm³/s', '次/年', '天/年']

# 生态指标
eco_indicators = ['鱼类种类数', 'Shannon指数', '底栖动物密度', '水质等级']
eco_before = [32, 2.85, 1250, 1]  # 水质1=I类
eco_after = [18, 1.92, 680, 2]    # 水质2=II类
eco_units = ['种', '', 'ind/m²', '类']

print("="*80)
print("题目2：河流健康评价")
print("="*80)

print("\n筑坝前后水文指标对比：")
print(f"{'指标':<12} {'筑坝前':<15} {'筑坝后':<15} {'变化量':<15} {'变化率':<10}")
print("-" * 80)

changes = after_dam - before_dam
change_rates = (changes / before_dam) * 100

for i, (ind, bf, af, chg, rate, unit) in enumerate(zip(indicators, before_dam, after_dam, changes, change_rates, units)):
    print(f"{ind:<12} {bf:<15.1f} {af:<15.1f} {chg:<15.1f} {rate:>9.1f}%")

print("\n筑坝前后生态指标对比：")
print(f"{'指标':<15} {'筑坝前':<15} {'筑坝后':<15} {'变化率':<10}")
print("-" * 80)
eco_change_rates = [(eco_after[i] - eco_before[i]) / eco_before[i] * 100 if eco_before[i] != 0 else 0 
                    for i in range(len(eco_before))]

for ind, bf, af, rate in zip(eco_indicators, eco_before, eco_after, eco_change_rates):
    if ind == '水质等级':
        print(f"{ind:<15} {'I类':<15} {'II类':<15} {'下降1级':<10}")
    else:
        print(f"{ind:<15} {bf:<15.2f} {af:<15.2f} {rate:>9.1f}%")

# 计算水文改变度（Hydrologic Alteration, HA）
print("\n" + "="*80)
print("水文改变度计算（Hydrologic Alteration）")
print("="*80)

ha_values = np.abs(changes / before_dam) * 100

print(f"\n{'指标':<15} {'改变度(%)':<12} {'等级':<10}")
print("-" * 80)

def classify_ha(ha):
    """分类水文改变度"""
    if ha < 33:
        return '低'
    elif ha < 67:
        return '中等'
    else:
        return '高'

for ind, ha in zip(indicators, ha_values):
    level = classify_ha(ha)
    print(f"{ind:<15} {ha:<12.1f} {level:<10}")

# 综合水文改变度
ha_avg = np.mean(ha_values)
ha_weighted = np.average(ha_values, weights=[0.1, 0.3, 0.3, 0.2, 0.1])

print(f"\n综合水文改变度：")
print(f"  算术平均: {ha_avg:.1f}% ({classify_ha(ha_avg)})")
print(f"  加权平均: {ha_weighted:.1f}% ({classify_ha(ha_weighted)})")

# 生态影响评估
print("\n" + "="*80)
print("生态影响评估")
print("="*80)

fish_loss = (eco_before[0] - eco_after[0]) / eco_before[0] * 100
diversity_loss = (eco_before[1] - eco_after[1]) / eco_before[1] * 100
benthos_loss = (eco_before[2] - eco_after[2]) / eco_before[2] * 100

print(f"\n生物多样性损失：")
print(f"  鱼类种类数减少: {fish_loss:.1f}% ({eco_before[0]:.0f} → {eco_after[0]:.0f}种)")
print(f"  Shannon指数下降: {diversity_loss:.1f}% ({eco_before[1]:.2f} → {eco_after[1]:.2f})")
print(f"  底栖动物密度降低: {benthos_loss:.1f}% ({eco_before[2]:.0f} → {eco_after[2]:.0f} ind/m²)")
print(f"  水质等级: I类 → II类（下降1级）")

# 综合评价
print(f"\n综合评价：")
print(f"  水文改变: {classify_ha(ha_weighted)} ({ha_weighted:.1f}%)")
print(f"  生态影响: 中度-重度（种类数-{fish_loss:.0f}%，多样性-{diversity_loss:.0f}%）")
print(f"  河流健康: 中度受损")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：水文指标对比
ax1 = fig.add_subplot(gs[0, :])
x = np.arange(len(indicators))
width = 0.35

bars1 = ax1.bar(x - width/2, before_dam/np.max(before_dam), width, label='筑坝前', color='blue', alpha=0.7)
bars2 = ax1.bar(x + width/2, after_dam/np.max(before_dam), width, label='筑坝后', color='red', alpha=0.7)

# 添加变化率标签
for i, (bf, af, rate) in enumerate(zip(before_dam, after_dam, change_rates)):
    ax1.text(i, max(bf, af)/np.max(before_dam) + 0.05, f'{rate:+.0f}%', 
             ha='center', fontsize=10, fontweight='bold')

ax1.set_xlabel('水文指标', fontsize=12, fontweight='bold')
ax1.set_ylabel('归一化值', fontsize=12, fontweight='bold')
ax1.set_title('题目2-1：筑坝前后水文指标对比', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(indicators, rotation=15, ha='right')
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3, axis='y')

# 子图2：水文改变度
ax2 = fig.add_subplot(gs[1, 0])
colors = ['green' if ha < 33 else 'orange' if ha < 67 else 'red' for ha in ha_values]
bars = ax2.barh(indicators, ha_values, color=colors, alpha=0.7)

# 添加等级区分线
ax2.axvline(x=33, color='orange', linestyle='--', linewidth=2, alpha=0.5, label='低/中等界限')
ax2.axvline(x=67, color='red', linestyle='--', linewidth=2, alpha=0.5, label='中等/高界限')

# 添加数值标签
for i, (ind, ha) in enumerate(zip(indicators, ha_values)):
    ax2.text(ha + 2, i, f'{ha:.1f}%', va='center', fontsize=10, fontweight='bold')

ax2.set_xlabel('水文改变度 (%)', fontsize=11, fontweight='bold')
ax2.set_title(f'题目2-2：水文改变度（综合：{ha_weighted:.1f}%）', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9, loc='lower right')
ax2.grid(True, alpha=0.3, axis='x')

# 子图3：生态指标损失
ax3 = fig.add_subplot(gs[1, 1])
eco_loss_rates = [-fish_loss, -diversity_loss, -benthos_loss]
eco_names = ['鱼类种类', 'Shannon指数', '底栖动物']

bars = ax3.bar(eco_names, eco_loss_rates, color=['red', 'orange', 'darkred'], alpha=0.7)

for i, (name, loss) in enumerate(zip(eco_names, eco_loss_rates)):
    ax3.text(i, loss - 3, f'{loss:.1f}%', ha='center', va='top', fontsize=10, fontweight='bold', color='white')

ax3.set_ylabel('变化率 (%)', fontsize=11, fontweight='bold')
ax3.set_title('题目2-3：生态指标损失', fontsize=12, fontweight='bold')
ax3.axhline(y=0, color='black', linewidth=1.5)
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_xticklabels(eco_names, rotation=15, ha='right')

# 子图4：河流健康评价框架
ax4 = fig.add_subplot(gs[2, 0])
ax4.axis('off')

health_text = f"""
河流健康评价框架：

1. 水文改变度评价：
   • 综合改变度: {ha_weighted:.1f}% (中等)
   • 主要问题: 洪峰削减(-52%)、频率降低(-66%)、水文均质化
   • 等级: ⚠️ 中度改变

2. 生态影响评价：
   • 鱼类种类减少 44% (32 → 18种)
   • Shannon指数下降 33% (2.85 → 1.92)
   • 底栖动物降低 46% (1250 → 680 ind/m²)
   • 等级: ⚠️ 中度-重度受损

3. 综合健康评价：
   • 河流健康: 中度受损
   • 主要原因: 水文过程改变、生境退化、连续性中断
"""

ax4.text(0.05, 0.95, health_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# 子图5：生态修复建议
ax5 = fig.add_subplot(gs[2, 1])
ax5.axis('off')

restoration_text = f"""
生态修复建议：

1. 生态调度（优先）：
   • 最小生态流量: ≥150 m³/s (30% Q̄)
   • 人造洪峰: 汛期1-2次，1000-1500 m³/s，持续3-5天
   • 流量脉冲: 模拟自然流量变化

2. 过鱼设施：
   • 建设鱼道: 恢复洄游通道
   • 增殖放流: 补充种群
   • 栖息地修复: 产卵场、索饵场

3. 生境修复：
   • 河道整治: 恢复深潭-浅滩结构
   • 岸带修复: 种植本地植被
   • 湿地恢复: 河漫滩湿地

4. 监测与管理：
   • 建立监测体系: 水文、水质、生物
   • 适应性管理: 根据监测结果调整
"""

ax5.text(0.05, 0.95, restoration_text, transform=ax5.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.savefig('题目2_河流健康评价.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_河流健康评价.png")
plt.show()
