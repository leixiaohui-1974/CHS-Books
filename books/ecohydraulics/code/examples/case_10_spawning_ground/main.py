"""案例10：鱼卵漂流与孵化场水力条件

工程背景：
长江四大家鱼（青鱼、草鱼、鲢鱼、鳙鱼）产卵场需要特定的水力条件。
本案例分析产卵场的水力特征，评估其适宜性。

学习目标：
1. 理解鱼类繁殖生态需求
2. 掌握鱼卵水力学特性
3. 学会产卵场水文过程分析
4. 设计人工产卵场修复方案

计算内容：
1. 鱼卵沉降速度和悬浮条件
2. 漂流距离估算
3. 最优产卵流量范围
4. 底质适宜性评价
5. 综合条件评估
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.spawning_ground import (
    FishEgg, SpawningGround,
    create_chinese_carp_egg,
    create_standard_spawning_ground
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def main():
    """主函数"""
    print("="*70)
    print("案例10：鱼卵漂流与孵化场水力条件")
    print("="*70)
    
    # 1. 鱼卵特性分析
    print("\n【步骤1】鱼卵水力学特性")
    print("-"*70)
    
    egg = create_chinese_carp_egg("四大家鱼")
    
    print(f"鱼卵参数：")
    print(f"  直径: {egg.diameter} mm")
    print(f"  密度: {egg.density} kg/m³")
    
    w_s = egg.settling_velocity()
    Re = egg.reynolds_number()
    v_susp = egg.suspension_velocity_threshold()
    
    print(f"\n水力学特性：")
    print(f"  沉降速度: {w_s*1000:.2f} mm/s ({w_s:.4f} m/s)")
    print(f"  雷诺数: {Re:.2f}")
    print(f"  悬浮流速阈值: {v_susp:.3f} m/s")
    
    # 2. 创建产卵场模型
    print("\n【步骤2】产卵场基本参数")
    print("-"*70)
    
    spawning_ground = create_standard_spawning_ground(
        reach_length=50000.0,  # 50 km
        d50=30.0  # 30 mm
    )
    
    print(f"产卵场参数：")
    print(f"  河段长度: {spawning_ground.reach_length/1000:.1f} km")
    print(f"  河床坡度: {spawning_ground.slope}")
    print(f"  底质粒径d50: {spawning_ground.d50} mm")
    
    # 3. 最优流速范围
    print("\n【步骤3】最优产卵流速范围")
    print("-"*70)
    
    v_min, v_max = spawning_ground.optimal_flow_velocity_range()
    
    print(f"\n最优流速范围:")
    print(f"  最小流速: {v_min:.2f} m/s（维持鱼卵悬浮）")
    print(f"  最大流速: {v_max:.2f} m/s（不冲走亲鱼）")
    print(f"  推荐范围: {v_min:.2f} - {v_max:.2f} m/s")
    
    # 4. 漂流距离分析
    print("\n【步骤4】鱼卵漂流距离分析")
    print("-"*70)
    
    velocities = [0.8, 1.0, 1.2, 1.5]
    water_depth = 3.0
    
    print(f"\n漂流距离（水深{water_depth}m，孵化时间24小时）:")
    print(f"{'流速(m/s)':<12} {'漂流距离(km)':<15}")
    print("-"*70)
    
    for v in velocities:
        dist = spawning_ground.drift_distance(v, water_depth, 24.0)
        print(f"{v:<12.1f} {dist/1000:.1f}")
    
    # 5. 底质适宜性
    print("\n【步骤5】底质适宜性评价")
    print("-"*70)
    
    substrate_result = spawning_ground.substrate_suitability()
    
    print(f"\n底质评价：")
    print(f"  实际粒径d50: {substrate_result['d50_mm']} mm")
    print(f"  最优范围: {substrate_result['optimal_range'][0]}-{substrate_result['optimal_range'][1]} mm")
    print(f"  适宜性: {substrate_result['suitability']}")
    print(f"  评分: {substrate_result['score']:.2f}")
    
    # 6. 综合评估
    print("\n【步骤6】产卵场综合评估")
    print("-"*70)
    
    # 评估几种典型条件
    scenarios = [
        {"name": "自然产卵场", "v": 1.2, "h": 3.5, "rise": 0.8},
        {"name": "受损产卵场", "v": 0.6, "h": 2.0, "rise": 0.3},
        {"name": "理想修复后", "v": 1.0, "h": 3.0, "rise": 0.7},
    ]
    
    results = []
    for scenario in scenarios:
        assessment = spawning_ground.spawning_condition_assessment(
            flow_velocity=scenario["v"],
            water_depth=scenario["h"],
            water_level_rise=scenario["rise"]
        )
        results.append(assessment)
        
        print(f"\n{scenario['name']}:")
        print(f"  流速: {scenario['v']} m/s - {assessment['velocity']['suitable'] and '✓' or '✗'}")
        print(f"  水深: {scenario['h']} m - {assessment['depth']['suitable'] and '✓' or '✗'}")
        print(f"  涨水: {scenario['rise']} m/day - {assessment['water_level_rise']['suitable'] and '✓' or '✗'}")
        print(f"  底质: {assessment['substrate']['suitability']}")
        print(f"  综合评分: {assessment['overall_score']:.2f}")
        print(f"  评级: {assessment['grade']}")
    
    # 7. 绘图
    print("\n【步骤7】生成可视化图表")
    print("-"*70)
    
    fig = plt.figure(figsize=(16, 10))
    
    # 图1: 流速-漂流距离关系
    ax1 = plt.subplot(2, 3, 1)
    v_range = np.linspace(0.5, 2.0, 30)
    drift_dists = [spawning_ground.drift_distance(v, 3.0, 24.0)/1000 for v in v_range]
    
    ax1.plot(v_range, drift_dists, 'b-', linewidth=2)
    ax1.axhspan(50, 150, alpha=0.2, color='green', label='适宜范围')
    ax1.axvline(x=v_min, color='r', linestyle='--', label=f'最小流速 {v_min:.2f} m/s')
    ax1.axvline(x=v_max, color='r', linestyle='--', label=f'最大流速 {v_max:.2f} m/s')
    ax1.set_xlabel('流速 (m/s)', fontsize=11)
    ax1.set_ylabel('漂流距离 (km)', fontsize=11)
    ax1.set_title('流速与鱼卵漂流距离关系', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: 底质适宜性
    ax2 = plt.subplot(2, 3, 2)
    d50_range = np.array([5, 10, 20, 30, 50, 80, 100])
    suitabilities = []
    for d in d50_range:
        sg_temp = SpawningGround(50000, 0.0005, d, egg)
        result = sg_temp.substrate_suitability()
        suitabilities.append(result['score'])
    
    colors = ['red' if s < 0.5 else 'orange' if s < 0.8 else 'green' for s in suitabilities]
    ax2.bar(range(len(d50_range)), suitabilities, color=colors)
    ax2.set_xticks(range(len(d50_range)))
    ax2.set_xticklabels([f'{d}mm' for d in d50_range])
    ax2.set_ylabel('适宜性评分', fontsize=11)
    ax2.set_title('底质粒径适宜性评价', fontsize=12, fontweight='bold')
    ax2.axhline(y=0.7, color='orange', linestyle='--', alpha=0.5)
    ax2.grid(axis='y', alpha=0.3)
    
    # 图3: 综合评估对比
    ax3 = plt.subplot(2, 3, 3)
    scenario_names = [s['name'] for s in scenarios]
    overall_scores = [r['overall_score'] for r in results]
    
    bars = ax3.barh(scenario_names, overall_scores)
    colors_bar = ['green' if s >= 0.85 else 'yellow' if s >= 0.7 else 'orange' if s >= 0.55 else 'red' 
                  for s in overall_scores]
    for bar, color in zip(bars, colors_bar):
        bar.set_color(color)
    
    ax3.set_xlabel('综合评分', fontsize=11)
    ax3.set_title('不同情景产卵场评估对比', fontsize=12, fontweight='bold')
    ax3.set_xlim([0, 1.0])
    ax3.grid(axis='x', alpha=0.3)
    
    # 图4: 涨水过程示意
    ax4 = plt.subplot(2, 3, 4)
    days = np.arange(0, 10, 0.1)
    # 模拟涨水过程
    base_level = 10.0
    rise_pattern = base_level + 0.8 * np.sin(days * 0.8) * np.exp(-days/8)
    
    ax4.plot(days, rise_pattern, 'b-', linewidth=2)
    ax4.axhspan(base_level + 0.5, base_level + 1.0, alpha=0.2, color='green', label='理想涨幅')
    ax4.set_xlabel('时间 (天)', fontsize=11)
    ax4.set_ylabel('水位 (m)', fontsize=11)
    ax4.set_title('产卵期涨水过程示意', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 图5: 各指标雷达图
    ax5 = plt.subplot(2, 3, 5, projection='polar')
    
    # 取第一个场景做雷达图
    assessment = results[0]
    categories = ['流速', '水深', '涨水', '底质', '漂流距离']
    scores = [
        assessment['velocity']['score'],
        assessment['depth']['score'],
        assessment['water_level_rise']['score'],
        assessment['substrate']['score'],
        assessment['drift_distance']['score']
    ]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    scores += scores[:1]
    angles += angles[:1]
    
    ax5.plot(angles, scores, 'o-', linewidth=2, color='blue')
    ax5.fill(angles, scores, alpha=0.25, color='blue')
    ax5.set_xticks(angles[:-1])
    ax5.set_xticklabels(categories)
    ax5.set_ylim(0, 1)
    ax5.set_title(f'{scenarios[0]["name"]}各指标评分', fontsize=12, fontweight='bold', pad=20)
    ax5.grid(True)
    
    # 图6: 设计建议
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    summary_text = f"""
    【产卵场设计建议】
    
    水力条件：
    ┌─────────────────────────────┐
    │ 流速: {v_min:.2f}-{v_max:.2f} m/s    │
    │ 水深: ≥ 2.0 m                │
    │ 涨水幅度: 0.5-1.0 m/day      │
    └─────────────────────────────┘
    
    底质条件：
    ┌─────────────────────────────┐
    │ 粒径d50: 20-50 mm           │
    │ 类型: 卵石、砾石            │
    │ 要求: 稳定、不淤积          │
    └─────────────────────────────┘
    
    漂流条件：
    ┌─────────────────────────────┐
    │ 漂流距离: 50-150 km         │
    │ 河段要求: 无闸坝阻隔        │
    │ 水流条件: 连续性好          │
    └─────────────────────────────┘
    
    修复建议：
    1. 保障生态流量和涨水过程
    2. 清除淤积，恢复卵石底床
    3. 保持河段连通性
    4. 控制采砂等人为干扰
    5. 在适当时期进行人工增殖放流
    
    评估结果：
    - 自然产卵场: {results[0]['grade']}
    - 受损产卵场: {results[1]['grade']}
    - 修复后: {results[2]['grade']}
    """
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
            family='monospace')
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'spawning_ground_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 图表已保存: {output_file}")
    
    # 8. 总结
    print("\n" + "="*70)
    print("【工程结论】")
    print("="*70)
    print(f"""
1. 鱼卵水力学特性：
   - 沉降速度: {w_s*1000:.2f} mm/s
   - 悬浮流速阈值: {v_susp:.2f} m/s
   - 最优产卵流速: {v_min:.2f}-{v_max:.2f} m/s

2. 产卵场水力要求：
   - 流速: 0.8-1.5 m/s（维持鱼卵悬浮）
   - 水深: ≥ 2.0 m（提供足够空间）
   - 涨水: 0.5-1.0 m/day（刺激产卵）
   - 底质: d50 = 20-50 mm（卵石、砾石）

3. 漂流距离：
   - 在流速1.0 m/s时，漂流约60 km
   - 需要50-150 km无闸坝河段
   - 保证鱼卵有足够孵化时间

4. 产卵场保护建议：
   - 保障生态流量和涨水过程
   - 禁止过度采砂
   - 保持河段连通性
   - 控制污染和人为干扰

5. 修复效果评估：
   - 自然产卵场: {results[0]['grade']}（评分{results[0]['overall_score']:.2f}）
   - 受损产卵场: {results[1]['grade']}（评分{results[1]['overall_score']:.2f}）
   - 修复后预期: {results[2]['grade']}（评分{results[2]['overall_score']:.2f}）
    """)
    
    print("="*70)
    print("案例10计算完成！")
    print("="*70)


if __name__ == "__main__":
    main()
