#!/usr/bin/env python3
"""案例18：河流生态修复效果评估"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.sediment_gravel import RestorationAssessment

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例18：河流生态修复效果评估")
    print("=" * 70)
    
    assessment = RestorationAssessment()
    
    # 水力多样性变化
    before = np.array([0.5, 0.3, 0.15, 0.05])  # 修复前（单一）
    after = np.array([0.3, 0.3, 0.25, 0.15])   # 修复后（多样）
    
    diversity_change = assessment.hydraulic_diversity_change(before, after)
    print(f"\n水力多样性变化:")
    print(f"  修复前Shannon指数: {diversity_change['shannon_before']:.3f}")
    print(f"  修复后Shannon指数: {diversity_change['shannon_after']:.3f}")
    print(f"  变化率: {diversity_change['change_rate']:+.1f}%")
    
    # 栖息地质量
    print(f"\n栖息地质量评分:")
    conditions = [
        (0.5, 1.0, '砾石', '修复后-深潭'),
        (0.8, 0.6, '粗砂', '修复后-浅滩'),
        (0.2, 2.5, '淤泥', '修复前')
    ]
    scores = []
    for v, h, s, name in conditions:
        score = assessment.habitat_quality_score(v, h, s)
        scores.append(score)
        print(f"  {name}: {score:.2f}")
    
    # 综合评价
    print(f"\n综合效果评价:")
    result = assessment.comprehensive_evaluation(
        hydraulic_improvement=diversity_change['change_rate'],
        habitat_improvement=(np.mean(scores[:2]) - scores[2]) * 100,
        biodiversity_improvement=25.0  # 假设值
    )
    print(f"  综合得分: {result['overall_score']:.1f}")
    print(f"  评价等级: {result['grade']}")
    print(f"  水力贡献: {result['hydraulic_contribution']:.1f}")
    print(f"  生境贡献: {result['habitat_contribution']:.1f}")
    print(f"  生物贡献: {result['biodiversity_contribution']:.1f}")
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 多样性对比
    ax1 = axes[0]
    categories = ['低速', '中低速', '中高速', '高速']
    x = np.arange(len(categories))
    width = 0.35
    ax1.bar(x - width/2, before, width, label='修复前', alpha=0.7, color='gray')
    ax1.bar(x + width/2, after, width, label='修复后', alpha=0.7, color='green')
    ax1.set_ylabel('比例', fontsize=10)
    ax1.set_title('流速分布多样性对比', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=9)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 综合评分
    ax2 = axes[1]
    contributions = [
        result['hydraulic_contribution'],
        result['habitat_contribution'],
        result['biodiversity_contribution']
    ]
    labels = ['水力改善', '生境改善', '生物改善']
    colors = ['steelblue', 'green', 'orange']
    ax2.bar(labels, contributions, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('贡献得分', fontsize=10)
    ax2.set_title(f'修复效果综合评价 ({result["grade"]})', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    for i, (label, val) in enumerate(zip(labels, contributions)):
        ax2.text(i, val, f'{val:.1f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'restoration_assessment.png', dpi=300)
    print(f"\n图表已保存")
    print("=" * 70)

if __name__ == '__main__':
    main()
