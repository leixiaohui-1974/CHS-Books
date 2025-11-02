"""案例29：城市黑臭水体治理方案评估"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.urban_blackwater import UrbanBlackwaterModel, optimize_treatment_plan
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例29：城市黑臭水体治理方案评估")
    print("="*70)
    
    model = UrbanBlackwaterModel(river_length=2000, width=15, depth=2)
    
    # 现状评估
    status, score = model.assess_current_status(DO=1.5, NH3_N=10, transparency=0.15)
    
    # 治理措施
    measures = {
        'source_control': True,
        'dredging': True,
        'aeration': True,
        'ecological_restoration': True
    }
    DO_improvement, NH3_reduction = model.simulate_treatment_effects(measures)
    
    # 方案优化
    optimal_plan = optimize_treatment_plan(budget=800, target_quality='Class III')
    
    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 治理前后对比
    indicators = ['DO', 'NH3-N', 'Transparency']
    before = [1.5, 10, 0.15]
    after = [1.5 + DO_improvement, 10 - NH3_reduction, 0.4]
    x = np.arange(len(indicators))
    width = 0.35
    ax1.bar(x - width/2, before, width, label='Before', color='red', alpha=0.7)
    ax1.bar(x + width/2, after, width, label='After', color='green', alpha=0.7)
    ax1.set_ylabel('Value')
    ax1.set_title('Treatment Effect')
    ax1.set_xticks(x)
    ax1.set_xticklabels(indicators)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 措施效果
    measure_names = ['Source\nControl', 'Dredging', 'Aeration', 'Ecological\nRestoration']
    effects = [6, 3, 3, 3]
    ax2.barh(measure_names, effects, color=['blue', 'orange', 'purple', 'green'], alpha=0.7)
    ax2.set_xlabel('Improvement Score')
    ax2.set_title('Measure Effectiveness')
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('urban_blackwater.png', dpi=150)
    print("  ✓ 已保存: urban_blackwater.png")
    print("\n"+"="*70)
    print("案例29完成！")
    print("="*70)

if __name__ == '__main__':
    main()
