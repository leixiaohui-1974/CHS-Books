"""案例7：鱼类游泳能力与水流关系

工程背景：
某河流拟建设低坝过鱼设施，需要分析目标鱼类（草鱼、青鱼、鲤鱼等）的
游泳能力，确定鱼道设计流速和休息区布置。

学习目标：
1. 理解鱼类游泳生物力学基础
2. 掌握持续游速、爆发游速、临界游速的计算
3. 学会不同体长鱼类的游泳能力差异
4. 为鱼道设计提供流速建议

计算内容：
1. 不同体长鱼类的游泳能力对比
2. 游泳速度与耐力时间关系
3. 鱼道设计流速确定
4. 通道通过能力评估
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.fish_swimming import (
    FishSwimmingModel, 
    create_grass_carp, 
    create_black_carp,
    create_common_carp,
    create_silver_carp
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def main():
    """主函数"""
    print("="*70)
    print("案例7：鱼类游泳能力与水流关系")
    print("="*70)
    
    # 1. 创建不同鱼类模型（体长30cm）
    print("\n【步骤1】创建目标鱼类模型（体长30cm）")
    print("-"*70)
    
    grass_carp = create_grass_carp(body_length=30.0, temperature=20.0)
    black_carp = create_black_carp(body_length=30.0, temperature=20.0)
    common_carp = create_common_carp(body_length=30.0, temperature=20.0)
    silver_carp = create_silver_carp(body_length=30.0, temperature=20.0)
    
    fishes = [grass_carp, black_carp, common_carp, silver_carp]
    
    for fish in fishes:
        summary = fish.swimming_performance_summary()
        print(f"\n{summary['species']}:")
        print(f"  体长: {summary['body_length_cm']:.1f} cm")
        print(f"  体重: {summary['body_weight_g']:.1f} g")
        print(f"  持续游速: {summary['sustained_speed_ms']:.2f} m/s ({summary['sustained_speed_BLs']:.1f} BL/s)")
        print(f"  爆发游速: {summary['burst_speed_ms']:.2f} m/s ({summary['burst_speed_BLs']:.1f} BL/s)")
        print(f"  临界游速: {summary['critical_speed_ms']:.2f} m/s ({summary['critical_speed_BLs']:.1f} BL/s)")
    
    # 2. 分析不同体长草鱼的游泳能力
    print("\n【步骤2】草鱼体长对游泳能力的影响")
    print("-"*70)
    
    body_lengths = np.array([10, 20, 30, 40, 50, 60])  # cm
    
    print(f"\n{'体长(cm)':<10} {'体重(g)':<12} {'持续游速(m/s)':<15} {'爆发游速(m/s)':<15} {'临界游速(m/s)':<15}")
    print("-"*70)
    
    for length in body_lengths:
        fish = create_grass_carp(body_length=length)
        summary = fish.swimming_performance_summary()
        print(f"{length:<10.0f} {summary['body_weight_g']:<12.1f} {summary['sustained_speed_ms']:<15.2f} "
              f"{summary['burst_speed_ms']:<15.2f} {summary['critical_speed_ms']:<15.2f}")
    
    # 3. 鱼道设计流速建议
    print("\n【步骤3】鱼道设计流速建议")
    print("-"*70)
    
    # 选择最弱游泳能力的鱼类作为设计标准
    target_fish = common_carp  # 鲤鱼游泳能力相对较弱
    
    design_v, recommendation = target_fish.design_flow_velocity(safety_factor=0.8)
    print(recommendation)
    
    # 4. 通道通过能力评估
    print("\n【步骤4】通道通过能力评估")
    print("-"*70)
    
    passage_length = 20.0  # 鱼道池室间距 (m)
    test_velocities = [0.6, 0.8, 1.0, 1.2, 1.5]  # m/s
    
    print(f"\n通道长度: {passage_length} m")
    print(f"{'流速(m/s)':<12} {'草鱼':<15} {'青鱼':<15} {'鲤鱼':<15} {'鲢鱼':<15}")
    print("-"*70)
    
    for v in test_velocities:
        results = []
        for fish in fishes:
            can_pass, time_needed, msg = fish.can_pass_velocity(v, passage_length)
            status = "✓" if can_pass else "✗"
            results.append(f"{status} {time_needed:.1f}s")
        
        print(f"{v:<12.1f} {results[0]:<15} {results[1]:<15} {results[2]:<15} {results[3]:<15}")
    
    # 5. 绘图
    print("\n【步骤5】生成可视化图表")
    print("-"*70)
    
    fig = plt.figure(figsize=(16, 10))
    
    # 图1: 不同鱼类游泳能力对比
    ax1 = plt.subplot(2, 3, 1)
    species_names = [f.species for f in fishes]
    sustained_speeds = [f.sustained_speed() for f in fishes]
    burst_speeds = [f.burst_speed() for f in fishes]
    critical_speeds = [f.critical_speed() for f in fishes]
    
    x = np.arange(len(species_names))
    width = 0.25
    
    ax1.bar(x - width, sustained_speeds, width, label='持续游速', color='#2ecc71')
    ax1.bar(x, critical_speeds, width, label='临界游速', color='#3498db')
    ax1.bar(x + width, burst_speeds, width, label='爆发游速', color='#e74c3c')
    
    ax1.set_xlabel('鱼类种类', fontsize=11)
    ax1.set_ylabel('游泳速度 (m/s)', fontsize=11)
    ax1.set_title('不同鱼类游泳能力对比（体长30cm）', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(species_names)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # 图2: 体长对草鱼游泳能力的影响
    ax2 = plt.subplot(2, 3, 2)
    body_lengths_plot = np.linspace(10, 60, 50)
    sustained_vs_length = []
    burst_vs_length = []
    critical_vs_length = []
    
    for length in body_lengths_plot:
        fish = create_grass_carp(body_length=length)
        sustained_vs_length.append(fish.sustained_speed())
        burst_vs_length.append(fish.burst_speed())
        critical_vs_length.append(fish.critical_speed())
    
    ax2.plot(body_lengths_plot, sustained_vs_length, 'g-', linewidth=2, label='持续游速')
    ax2.plot(body_lengths_plot, critical_vs_length, 'b--', linewidth=2, label='临界游速')
    ax2.plot(body_lengths_plot, burst_vs_length, 'r:', linewidth=2, label='爆发游速')
    ax2.axhline(y=1.2, color='orange', linestyle='-.', linewidth=1.5, label='建议设计流速')
    
    ax2.set_xlabel('体长 (cm)', fontsize=11)
    ax2.set_ylabel('游泳速度 (m/s)', fontsize=11)
    ax2.set_title('体长对草鱼游泳能力的影响', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: 游泳速度与耐力时间关系
    ax3 = plt.subplot(2, 3, 3)
    
    target_fish = create_grass_carp(body_length=30.0)
    sustained = target_fish.sustained_speed()
    burst = target_fish.burst_speed()
    
    speeds = np.linspace(sustained, burst * 0.95, 50)
    endurances = [target_fish.endurance_time(v) for v in speeds]
    
    # 转换为分钟
    endurances_min = [min(e/60.0, 1000) for e in endurances]
    
    ax3.semilogy(speeds, endurances_min, 'b-', linewidth=2)
    ax3.axvline(x=sustained, color='g', linestyle='--', label=f'持续游速 {sustained:.2f} m/s')
    ax3.axvline(x=burst, color='r', linestyle='--', label=f'爆发游速 {burst:.2f} m/s')
    
    ax3.set_xlabel('游泳速度 (m/s)', fontsize=11)
    ax3.set_ylabel('耐力时间 (分钟, 对数坐标)', fontsize=11)
    ax3.set_title('草鱼游泳速度与耐力时间关系（30cm）', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 图4: 不同流速下的通过能力
    ax4 = plt.subplot(2, 3, 4)
    
    velocities_test = np.linspace(0.3, 2.0, 30)
    passage_success = {f.species: [] for f in fishes}
    
    for v in velocities_test:
        for fish in fishes:
            can_pass, _, _ = fish.can_pass_velocity(v, passage_length=20.0)
            passage_success[fish.species].append(1 if can_pass else 0)
    
    for fish in fishes:
        ax4.plot(velocities_test, passage_success[fish.species], 
                linewidth=2, label=fish.species, marker='o', markersize=3)
    
    ax4.set_xlabel('通道流速 (m/s)', fontsize=11)
    ax4.set_ylabel('能否通过 (1=能, 0=否)', fontsize=11)
    ax4.set_title('不同流速下鱼类通过能力（通道长度20m）', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim([-0.1, 1.1])
    
    # 图5: 能量消耗与速度关系
    ax5 = plt.subplot(2, 3, 5)
    
    speeds_energy = np.linspace(0.3, burst, 30)
    duration = 300.0  # 5分钟
    
    for fish in fishes:
        energies = [fish.energy_expenditure(v, duration) / 1000.0 for v in speeds_energy]  # kJ
        ax5.plot(speeds_energy, energies, linewidth=2, label=fish.species)
    
    ax5.set_xlabel('游泳速度 (m/s)', fontsize=11)
    ax5.set_ylabel('能量消耗 (kJ/5分钟)', fontsize=11)
    ax5.set_title('不同鱼类的能量消耗（体长30cm）', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 图6: 鱼道设计参数建议
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    text_content = f"""
    【鱼道设计参数建议】
    
    目标鱼类：草鱼、青鱼、鲤鱼、鲢鱼
    设计体长：20-40 cm
    
    设计流速：
    ┌─────────────────────────────┐
    │ 推荐流速：< 1.0 m/s        │
    │ 最大流速：< 1.2 m/s        │
    │ 依据：鲤鱼持续游速的80%    │
    └─────────────────────────────┘
    
    休息区设置：
    ┌─────────────────────────────┐
    │ 间距：每15-20 m设置一处    │
    │ 面积：≥ 2 m²              │
    │ 流速：< 0.3 m/s            │
    └─────────────────────────────┘
    
    通道长度：
    ┌─────────────────────────────┐
    │ 单段长度：≤ 20 m          │
    │ 总长度：视坝高而定         │
    │ 坡度：1:10 ~ 1:20         │
    └─────────────────────────────┘
    
    【工程应用说明】
    1. 设计流速应以最弱游泳能力的
       目标鱼类为准
    2. 应考虑幼鱼和成鱼的差异
    3. 休息区是长距离洄游的关键
    4. 水温影响游泳能力，需考虑
       季节变化
    """
    
    ax6.text(0.1, 0.95, text_content, transform=ax6.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
            family='monospace')
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'fish_swimming_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 图表已保存: {output_file}")
    
    # 6. 总结
    print("\n" + "="*70)
    print("【工程结论】")
    print("="*70)
    print(f"""
1. 游泳能力分析（体长30cm）：
   - 青鱼游泳能力最强：持续游速 {black_carp.sustained_speed():.2f} m/s
   - 鲤鱼游泳能力最弱：持续游速 {common_carp.sustained_speed():.2f} m/s
   - 能力差异约 {(black_carp.sustained_speed()/common_carp.sustained_speed()-1)*100:.0f}%

2. 鱼道设计建议：
   - 推荐设计流速: ≤ 1.0 m/s（以鲤鱼为准）
   - 最大允许流速: ≤ 1.2 m/s
   - 休息区间距: 15-20 m

3. 体长影响：
   - 体长每增加10cm，游泳速度提高约0.2 m/s
   - 小体长鱼类(<20cm)需要特别保护

4. 工程应用：
   - 本分析可用于鱼道设计、河流生态修复
   - 应根据实际目标鱼类调整参数
   - 需要现场观测验证设计效果
    """)
    
    print("="*70)
    print("案例7计算完成！")
    print("="*70)


if __name__ == "__main__":
    main()
