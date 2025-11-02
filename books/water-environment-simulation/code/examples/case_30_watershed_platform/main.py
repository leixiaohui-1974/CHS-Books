"""案例30：流域水环境综合管理平台"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.watershed_platform import WatershedPlatform, perform_scenario_analysis
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例30：流域水环境综合管理平台")
    print("="*70)
    
    platform = WatershedPlatform(watershed_name="示范流域", area=1500)
    
    # 情景分析
    scenarios = ['Baseline', 'Scenario1', 'Scenario2', 'Scenario3']
    results_list = []
    for scenario in scenarios:
        results = platform.run_comprehensive_simulation(scenario)
        results_list.append(results)
    
    # 最优情景
    best = perform_scenario_analysis(scenarios)
    
    # 决策支持
    objectives = ['flood_control', 'water_quality', 'ecology']
    recommendations = platform.decision_support(objectives)
    
    # 绘图
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 径流量对比
    runoffs = [r['runoff'] for r in results_list]
    axes[0, 0].bar(scenarios, runoffs, color='steelblue', alpha=0.7)
    axes[0, 0].set_ylabel('Runoff (mm)')
    axes[0, 0].set_title('Runoff Comparison')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # 水质指数对比
    wq = [r['water_quality'] for r in results_list]
    axes[0, 1].bar(scenarios, wq, color='green', alpha=0.7)
    axes[0, 1].set_ylabel('Water Quality Index')
    axes[0, 1].set_title('Water Quality Comparison')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # 生态评分对比
    eco = [r['ecology_score'] for r in results_list]
    axes[1, 0].bar(scenarios, eco, color='forestgreen', alpha=0.7)
    axes[1, 0].set_ylabel('Ecology Score')
    axes[1, 0].set_title('Ecology Comparison')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 综合雷达图
    categories = ['Runoff', 'Water\nQuality', 'Ecology', 'Management']
    values = [results_list[1]['runoff']/100, results_list[1]['water_quality']/50,
              results_list[1]['ecology_score']/10, results_list[1]['management_efficiency']]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    axes[1, 1] = plt.subplot(2, 2, 4, projection='polar')
    axes[1, 1].plot(angles, values, 'o-', linewidth=2)
    axes[1, 1].fill(angles, values, alpha=0.25)
    axes[1, 1].set_xticks(angles[:-1])
    axes[1, 1].set_xticklabels(categories)
    axes[1, 1].set_title('Integrated Assessment')
    
    plt.tight_layout()
    plt.savefig('watershed_platform.png', dpi=150)
    print("  ✓ 已保存: watershed_platform.png")
    print("\n"+"="*70)
    print("🎉🎉🎉 案例30完成！全部30个案例开发完成！🎉🎉🎉")
    print("="*70)

if __name__ == '__main__':
    main()
