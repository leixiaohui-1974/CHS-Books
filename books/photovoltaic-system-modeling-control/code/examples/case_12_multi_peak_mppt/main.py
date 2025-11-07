"""
案例12: 多峰MPPT算法
Case 12: Multi-Peak MPPT Algorithms

工程背景:
--------
部分遮挡导致P-V曲线出现多个功率峰值:
- 传统MPPT易陷入局部最优
- 需要全局搜索能力
- 混合策略平衡速度与精度

学习目标:
--------
1. 理解多峰问题的本质
2. 掌握多峰检测方法
3. 学习全局搜索策略
4. 掌握混合算法设计
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
from code.models.mppt_algorithms import (MultiPeakDetector, GlobalScanMPPT,
                                          HybridMPPT, PerturbAndObserve,
                                          ParticleSwarmMPPT, MPPTController)


def create_partial_shading_module():
    """创建部分遮挡条件下的组件（简化模拟）"""
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
    
    # 使用降低的光照模拟部分遮挡效果
    module = PVModule(cell, Ns=60, Nb=3, name="遮挡组件")
    module.set_uniform_conditions(T=298.15, G=700.0)  # 平均光照
    
    return module


def main():
    """主函数: 多峰MPPT演示"""
    print("=" * 80)
    print("案例12: 多峰MPPT算法")
    print("Case 12: Multi-Peak MPPT Algorithms")
    print("=" * 80)
    
    # 1. 创建PV组件
    print("\n步骤1: 创建光伏组件")
    print("-" * 80)
    
    # 标准组件
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
    module = PVModule(cell, Ns=60, Nb=3, name="标准组件")
    module.set_uniform_conditions(T=298.15, G=1000.0)
    
    vmpp_std, impp_std, pmpp_std = module.find_mpp()
    
    print(f"标准组件:")
    print(f"  Vmpp = {vmpp_std:.2f} V")
    print(f"  Pmpp = {pmpp_std:.2f} W")
    
    # 遮挡组件（简化）
    module_shaded = create_partial_shading_module()
    vmpp_sh, impp_sh, pmpp_sh = module_shaded.find_mpp()
    
    print(f"\n遮挡组件(平均G=700 W/m²):")
    print(f"  Vmpp = {vmpp_sh:.2f} V")
    print(f"  Pmpp = {pmpp_sh:.2f} W")
    
    # 2. 场景1: 多峰检测
    print("\n步骤2: 场景1 - 多峰检测")
    print("-" * 80)
    
    detector = MultiPeakDetector(module_shaded, n_scan_points=50)
    voltages, powers = detector.scan_pv_curve()
    peaks = detector.detect_peaks(voltages, powers, min_prominence=1.0)
    
    print(f"扫描点数: {len(voltages)}")
    print(f"检测到{len(peaks)}个峰值:")
    for i, peak in enumerate(peaks):
        print(f"  峰{i+1}: V={peak['voltage']:.2f}V, P={peak['power']:.2f}W, "
              f"突出度={peak['prominence']:.2f}W")
    
    # 3. 场景2: P&O陷入局部最优
    print("\n步骤3: 场景2 - P&O在部分遮挡下的表现")
    print("-" * 80)
    
    # 从不同起始点测试P&O
    start_voltages = [vmpp_sh * 0.5, vmpp_sh * 0.7, vmpp_sh * 1.2]
    po_results = []
    
    for v_start in start_voltages:
        po = PerturbAndObserve(step_size=1.0, initial_voltage=v_start)
        controller = MPPTController(po, v_min=0, v_max=module_shaded.Voc)
        
        v_pv = v_start
        for _ in range(50):
            i_pv = module_shaded.calculate_current(v_pv)
            v_ref = controller.step(v_pv, i_pv)
            v_pv = v_pv + 0.5 * (v_ref - v_pv)
        
        final_p = v_pv * module_shaded.calculate_current(v_pv)
        po_results.append({
            'start_v': v_start,
            'final_v': v_pv,
            'final_p': final_p,
            'efficiency': (final_p / pmpp_sh) * 100
        })
        
        print(f"  起始V={v_start:.1f}V → 最终V={v_pv:.1f}V, P={final_p:.1f}W, "
              f"效率={po_results[-1]['efficiency']:.1f}%")
    
    # 4. 场景3: PSO全局搜索
    print("\n步骤4: 场景3 - PSO全局搜索")
    print("-" * 80)
    
    pso = ParticleSwarmMPPT(
        n_particles=10,
        v_min=0,
        v_max=module_shaded.Voc,
        w=0.7,
        c1=1.5,
        c2=1.5,
        max_iterations=30
    )
    pso.set_pv_module(module_shaded)
    
    for step in range(30):
        v = pso.v_ref
        i = module_shaded.calculate_current(v)
        pso.update(v, i)
        
        if pso.converged:
            print(f"  PSO收敛于第{step}步")
            break
    
    pso_final_p = pso.gbest_fitness
    pso_eff = (pso_final_p / pmpp_sh) * 100
    
    print(f"  找到V={pso.gbest_position:.2f}V, P={pso_final_p:.2f}W")
    print(f"  跟踪效率: {pso_eff:.1f}%")
    
    # 5. 场景4: 混合MPPT
    print("\n步骤5: 场景4 - 混合MPPT（PSO+P&O）")
    print("-" * 80)
    
    hybrid = HybridMPPT(
        pv_module=module,
        pso_params={'n_particles': 10, 'max_iterations': 20},
        po_params={'step_size': 1.0},
        switch_threshold=0.95
    )
    
    v_pv = vmpp_std * 0.7
    mode_switches = []
    
    for step in range(100):
        i_pv = module.calculate_current(v_pv)
        v_ref = hybrid.update(v_pv, i_pv)
        v_pv = v_pv + 0.5 * (v_ref - v_pv)
        
        status = hybrid.get_status()
        if step > 0 and status['switch_count'] != mode_switches[-1] if mode_switches else 0:
            mode_switches.append(status['switch_count'])
            print(f"  第{step}步: 切换到{status['mode']}模式")
    
    final_status = hybrid.get_status()
    print(f"\n混合MPPT最终状态:")
    print(f"  当前模式: {final_status['mode']}")
    print(f"  找到V={final_status['v_ref']:.2f}V")
    print(f"  最佳功率: {final_status['best_power']:.2f}W")
    print(f"  切换次数: {final_status['switch_count']}")
    
    # 6. 可视化
    print("\n步骤6: 结果可视化")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 10))
    
    # 图1: 多峰P-V曲线与峰值检测
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(voltages, powers, 'b-', linewidth=2, label='P-V曲线(遮挡)')
    for i, peak in enumerate(peaks):
        ax1.plot(peak['voltage'], peak['power'], 'r*', markersize=15,
                label=f'峰{i+1}' if i < 3 else '')
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('功率 (W)', fontsize=11)
    ax1.set_title('多峰P-V曲线与峰值检测', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 图2: P&O从不同起点的结果
    ax2 = plt.subplot(2, 3, 2)
    V_curve, P_curve = module_shaded.get_pv_curve(200)
    ax2.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    
    colors = ['red', 'blue', 'green']
    for result, color in zip(po_results, colors):
        ax2.scatter(result['start_v'], 5, marker='o', s=100, c=color, 
                   label=f"起点{result['start_v']:.1f}V", alpha=0.7)
        ax2.scatter(result['final_v'], result['final_p'], marker='x', 
                   s=150, c=color, linewidths=3)
        ax2.annotate(f"{result['efficiency']:.0f}%",
                    xy=(result['final_v'], result['final_p']),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=9, color=color)
    
    ax2.set_xlabel('电压 (V)', fontsize=11)
    ax2.set_ylabel('功率 (W)', fontsize=11)
    ax2.set_title('P&O从不同起点的收敛', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 算法效率对比
    ax3 = plt.subplot(2, 3, 3)
    algorithms = ['P&O\n(最好)', 'P&O\n(最差)', 'PSO', 'Global\nMPP']
    efficiencies = [
        max([r['efficiency'] for r in po_results]),
        min([r['efficiency'] for r in po_results]),
        pso_eff,
        100.0
    ]
    
    bars = ax3.bar(algorithms, efficiencies,
                   color=['coral', 'lightcoral', 'steelblue', 'green'], alpha=0.7)
    ax3.axhline(y=100, color='r', linestyle='--', alpha=0.5)
    ax3.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax3.set_title('多峰条件下算法效率对比', fontsize=12, fontweight='bold')
    ax3.set_ylim([70, 105])
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, efficiencies):
        ax3.text(bar.get_x() + bar.get_width()/2, val,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 图4: 混合MPPT模式切换
    ax4 = plt.subplot(2, 3, 4)
    
    # 绘制模式时间线
    modes = [h['mode'] for h in hybrid.history]
    steps = list(range(len(modes)))
    mode_numeric = [1 if m == 'PSO' else 0 for m in modes]
    
    ax4.fill_between(steps, 0, mode_numeric, where=[m == 1 for m in mode_numeric],
                     color='steelblue', alpha=0.5, label='PSO模式')
    ax4.fill_between(steps, 0, [1-m for m in mode_numeric],
                     where=[m == 0 for m in mode_numeric],
                     color='coral', alpha=0.5, label='P&O模式')
    
    ax4.set_xlabel('步数', fontsize=11)
    ax4.set_ylabel('模式', fontsize=11)
    ax4.set_yticks([0, 1])
    ax4.set_yticklabels(['P&O', 'PSO'])
    ax4.set_title('混合MPPT模式切换', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis='x')
    
    # 图5: 混合MPPT功率曲线
    ax5 = plt.subplot(2, 3, 5)
    powers_hybrid = [h['p'] for h in hybrid.history]
    ax5.plot(powers_hybrid, 'b-', linewidth=2, alpha=0.7)
    ax5.axhline(y=pmpp_std, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax5.set_xlabel('步数', fontsize=11)
    ax5.set_ylabel('功率 (W)', fontsize=11)
    ax5.set_title('混合MPPT功率响应', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 总结表格
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    summary_data = [
        ['算法', '全局搜索', '局部精度', '计算量', '推荐度'],
        ['P&O', '❌', '⭐⭐⭐', '⭐', '⭐⭐'],
        ['PSO', '⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐'],
        ['GlobalScan', '⭐⭐⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐'],
        ['Hybrid', '⭐⭐⭐⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐⭐'],
    ]
    
    table = ax6.table(cellText=summary_data, cellLoc='center',
                     loc='center', bbox=[0, 0.2, 1, 0.7])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    for i in range(5):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax6.set_title('多峰MPPT算法总结', fontsize=12, fontweight='bold', pad=20)
    
    plt.suptitle('多峰MPPT算法 - 综合分析', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'multi_peak_mppt.png'),
                dpi=300, bbox_inches='tight')
    print(f"图表已保存")
    
    # 7. 总结
    print("\n步骤7: 总结")
    print("=" * 80)
    
    print("\n多峰MPPT关键技术:")
    print("  1. 多峰检测: 扫描P-V曲线，识别所有峰值")
    print("  2. 全局搜索: PSO、全局扫描等方法")
    print("  3. 混合策略: 全局+局部，平衡速度与精度")
    print("  4. 智能切换: 根据环境变化动态调整")
    
    print("\n算法选择建议:")
    print("  部分遮挡严重 → PSO或Hybrid")
    print("  偶尔遮挡     → GlobalScan")
    print("  无遮挡       → P&O/INC")
    print("  高精度要求   → Hybrid")
    
    print("\n" + "=" * 80)
    print("案例12主程序完成！")
    print("MPPT算法系列完结 🎉")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
