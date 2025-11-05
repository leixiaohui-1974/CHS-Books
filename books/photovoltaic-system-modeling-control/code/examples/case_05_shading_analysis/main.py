"""
案例5: 遮挡分析与诊断
Case 5: Shading Analysis and Diagnostics

工程背景:
--------
光伏系统运行中常遇到遮挡问题:
- 建筑物/树木遮挡
- 灰尘/鸟粪污染
- 组件老化不均
导致功率损失、热斑风险、系统故障

学习目标:
--------
1. 掌握遮挡模式识别方法
2. 学习热斑风险评估
3. 理解I-V曲线诊断技术
4. 掌握故障定位方法
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule
from code.models.pv_diagnostics import ShadingAnalyzer, IVCurveDiagnostics


def main():
    """主函数: 遮挡分析与诊断演示"""
    print("=" * 80)
    print("案例5: 遮挡分析与诊断")
    print("Case 5: Shading Analysis and Diagnostics")
    print("=" * 80)
    
    # 1. 创建标准组件
    print("\n步骤1: 创建60片标准组件")
    print("-" * 80)
    
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
    module = PVModule(cell_model=cell, Ns=60, Nb=3, name="60片组件")
    
    # 2. 定义不同遮挡场景
    print("\n步骤2: 定义遮挡场景")
    print("-" * 80)
    
    scenarios = {
        '场景1-无遮挡': [1000.0] * 60,
        '场景2-轻度遮挡(5片)': [1000.0] * 55 + [400.0] * 5,
        '场景3-中度遮挡(15片)': [1000.0] * 45 + [300.0] * 15,
        '场景4-严重遮挡(1组)': [1000.0] * 40 + [100.0] * 20,
        '场景5-极端遮挡(2组)': [1000.0] * 20 + [50.0] * 40,
    }
    
    # 3. 遮挡分析
    print("\n步骤3: 遮挡模式分析")
    print("-" * 80)
    
    analyzer = ShadingAnalyzer(module)
    
    results = {}
    for name, irradiances in scenarios.items():
        print(f"\n{name}:")
        
        # 遮挡分析
        shading_info = analyzer.analyze_shading_pattern(irradiances)
        print(f"  遮挡电池数: {shading_info['num_shaded_cells']}/{module.Ns}")
        print(f"  遮挡比例: {shading_info['shading_ratio']*100:.1f}%")
        print(f"  严重程度: {shading_info['severity']}")
        print(f"  受影响组数: {shading_info['num_affected_groups']}/{module.Nb}")
        
        # 热斑风险
        hotspot_info = analyzer.detect_hot_spot_risk(irradiances)
        print(f"  热斑风险: {hotspot_info['risk_level']}")
        print(f"  预估温升: {hotspot_info['estimated_temp_rise']:.1f}°C")
        print(f"  旁路导通: {'是' if hotspot_info['will_bypass_activate'] else '否'}")
        
        # 功率损失
        loss_info = analyzer.estimate_power_loss(irradiances)
        print(f"  基准功率: {loss_info['baseline_power']:.2f} W")
        print(f"  实际功率: {loss_info['shaded_power']:.2f} W")
        print(f"  功率损失: {loss_info['power_loss']:.2f} W ({loss_info['loss_percentage']:.1f}%)")
        
        results[name] = {
            'irradiances': irradiances,
            'shading': shading_info,
            'hotspot': hotspot_info,
            'loss': loss_info,
        }
    
    # 4. I-V曲线对比
    print("\n步骤4: I-V曲线诊断")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    diagnostics = IVCurveDiagnostics()
    
    for idx, (name, data) in enumerate(results.items(), 1):
        # 设置辐照度
        module.set_cell_irradiance(data['irradiances'])
        
        # 获取I-V曲线
        V, I = module.get_iv_curve(300)
        _, P = module.get_pv_curve(300)
        
        # 曲线分析
        curve_analysis = diagnostics.analyze_curve_shape(V, I)
        
        # 故障检测
        if idx == 1:
            reference = curve_analysis
        else:
            faults = diagnostics.detect_faults(V, I, reference)
        
        # 绘制I-V曲线
        ax_iv = plt.subplot(3, 5, idx)
        ax_iv.plot(V, I, 'b-', linewidth=2)
        ax_iv.plot(curve_analysis['Vmpp'], curve_analysis['Impp'], 
                  'ro', markersize=8)
        ax_iv.set_xlabel('电压 (V)', fontsize=9)
        ax_iv.set_ylabel('电流 (A)', fontsize=9)
        title = name.split('-')[0]
        ax_iv.set_title(f'{title}\nFF={curve_analysis["FF"]:.3f}', fontsize=10)
        ax_iv.grid(True, alpha=0.3)
        
        # 绘制P-V曲线
        ax_pv = plt.subplot(3, 5, idx + 5)
        ax_pv.plot(V, P, 'g-', linewidth=2)
        ax_pv.plot(curve_analysis['Vmpp'], curve_analysis['Pmpp'], 
                  'ro', markersize=8)
        ax_pv.set_xlabel('电压 (V)', fontsize=9)
        ax_pv.set_ylabel('功率 (W)', fontsize=9)
        pmpp = curve_analysis['Pmpp']
        ax_pv.set_title(f'Pmpp={pmpp:.1f}W', fontsize=10)
        ax_pv.grid(True, alpha=0.3)
        
        # 打印诊断信息
        if idx > 1:
            print(f"\n{name} 诊断:")
            for fault in faults:
                print(f"  • {fault}")
    
    # 第11-15个子图: 统计对比
    ax11 = plt.subplot(3, 5, 11)
    names = [n.split('-')[0] for n in results.keys()]
    powers = [r['loss']['shaded_power'] for r in results.values()]
    colors = ['green', 'yellowgreen', 'orange', 'orangered', 'red']
    
    bars = ax11.bar(range(len(names)), powers, color=colors, alpha=0.7)
    ax11.set_ylabel('功率 (W)', fontsize=10)
    ax11.set_title('输出功率对比', fontsize=11)
    ax11.set_xticks(range(len(names)))
    ax11.set_xticklabels(names, rotation=20, fontsize=8)
    ax11.grid(True, alpha=0.3, axis='y')
    
    for bar, p in zip(bars, powers):
        ax11.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f'{p:.0f}W', ha='center', va='bottom', fontsize=8)
    
    # 功率损失
    ax12 = plt.subplot(3, 5, 12)
    losses = [r['loss']['loss_percentage'] for r in results.values()]
    bars = ax12.bar(range(len(names)), losses, color=colors, alpha=0.7)
    ax12.set_ylabel('损失 (%)', fontsize=10)
    ax12.set_title('功率损失比例', fontsize=11)
    ax12.set_xticks(range(len(names)))
    ax12.set_xticklabels(names, rotation=20, fontsize=8)
    ax12.grid(True, alpha=0.3, axis='y')
    
    for bar, l in zip(bars, losses):
        ax12.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f'{l:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # 热斑风险
    ax13 = plt.subplot(3, 5, 13)
    risk_scores = [r['hotspot']['risk_score'] for r in results.values()]
    bars = ax13.bar(range(len(names)), risk_scores, color=colors, alpha=0.7)
    ax13.set_ylabel('风险等级', fontsize=10)
    ax13.set_title('热斑风险评估', fontsize=11)
    ax13.set_xticks(range(len(names)))
    ax13.set_xticklabels(names, rotation=20, fontsize=8)
    ax13.set_ylim([0, 5])
    ax13.grid(True, alpha=0.3, axis='y')
    
    risk_labels = ['', '低', '中', '高', '极高']
    for bar, s in zip(bars, risk_scores):
        if s < len(risk_labels):
            ax13.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                     risk_labels[s], ha='center', va='bottom', fontsize=8)
    
    # 遮挡比例
    ax14 = plt.subplot(3, 5, 14)
    shading_ratios = [r['shading']['shading_ratio']*100 for r in results.values()]
    bars = ax14.bar(range(len(names)), shading_ratios, color=colors, alpha=0.7)
    ax14.set_ylabel('遮挡比例 (%)', fontsize=10)
    ax14.set_title('遮挡电池比例', fontsize=11)
    ax14.set_xticks(range(len(names)))
    ax14.set_xticklabels(names, rotation=20, fontsize=8)
    ax14.grid(True, alpha=0.3, axis='y')
    
    for bar, r in zip(bars, shading_ratios):
        ax14.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f'{r:.0f}%', ha='center', va='bottom', fontsize=8)
    
    # FF对比
    ax15 = plt.subplot(3, 5, 15)
    module.set_uniform_conditions(T=298.15, G=1000.0)
    V_ref, I_ref = module.get_iv_curve(300)
    ff_values = []
    for data in results.values():
        module.set_cell_irradiance(data['irradiances'])
        V, I = module.get_iv_curve(300)
        analysis = diagnostics.analyze_curve_shape(V, I)
        ff_values.append(analysis['FF'])
    
    bars = ax15.bar(range(len(names)), ff_values, color=colors, alpha=0.7)
    ax15.set_ylabel('填充因子', fontsize=10)
    ax15.set_title('填充因子对比', fontsize=11)
    ax15.set_xticks(range(len(names)))
    ax15.set_xticklabels(names, rotation=20, fontsize=8)
    ax15.set_ylim([0, 1])
    ax15.grid(True, alpha=0.3, axis='y')
    ax15.axhline(y=0.75, color='r', linestyle='--', alpha=0.5, label='正常值')
    ax15.legend(fontsize=8)
    
    for bar, ff in zip(bars, ff_values):
        ax15.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                 f'{ff:.2f}', ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('光伏组件遮挡分析与诊断', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'shading_analysis.png'), 
                dpi=300, bbox_inches='tight')
    print(f"\n图表已保存")
    
    # 5. 总结
    print("\n步骤5: 分析总结")
    print("=" * 80)
    print("\n遮挡影响总结:")
    print(f"  轻度遮挡(8%):   功率损失 ~{results['场景2-轻度遮挡(5片)']['loss']['loss_percentage']:.1f}%")
    print(f"  中度遮挡(25%):  功率损失 ~{results['场景3-中度遮挡(15片)']['loss']['loss_percentage']:.1f}%")
    print(f"  严重遮挡(33%):  功率损失 ~{results['场景4-严重遮挡(1组)']['loss']['loss_percentage']:.1f}%")
    print(f"  极端遮挡(67%):  功率损失 ~{results['场景5-极端遮挡(2组)']['loss']['loss_percentage']:.1f}%")
    
    print("\n关键发现:")
    print("  ✓ 遮挡导致功率损失非线性增加")
    print("  ✓ 整组遮挡比分散遮挡影响更大")
    print("  ✓ 旁路二极管可降低但无法消除损失")
    print("  ✓ 严重遮挡存在热斑风险")
    
    print("\n" + "=" * 80)
    print("案例5主程序完成！")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
