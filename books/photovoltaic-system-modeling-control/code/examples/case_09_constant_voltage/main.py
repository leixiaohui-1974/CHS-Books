"""
案例9: 恒电压法
Case 9: Constant Voltage MPPT

工程背景:
--------
CV是最简单的MPPT算法:
- 基于0.76-0.8×Voc经验
- 极快响应
- 成本极低
- 适合简单应用

学习目标:
--------
1. 理解CV算法原理
2. 掌握电压比例选择
3. 对比CV与其他算法
4. 了解适用场景
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
from code.models.mppt_algorithms import (PerturbAndObserve, IncrementalConductance,
                                          ConstantVoltage, ImprovedCV, MPPTController)


def simulate_mppt(module: PVModule, algorithm, v_init: float,
                 num_steps: int = 100, dt: float = 0.1) -> dict:
    """模拟MPPT跟踪"""
    controller = MPPTController(algorithm, v_min=0, v_max=module.Voc)
    
    v_pv = v_init
    time, voltages, currents, powers, v_refs = [], [], [], [], []
    
    for step in range(num_steps):
        t = step * dt
        i_pv = module.calculate_current(v_pv)
        p_pv = v_pv * i_pv
        
        v_ref = controller.step(v_pv, i_pv)
        v_pv = v_pv + 0.5 * (v_ref - v_pv)
        
        time.append(t)
        voltages.append(v_pv)
        currents.append(i_pv)
        powers.append(p_pv)
        v_refs.append(v_ref)
    
    return {
        'time': np.array(time),
        'voltage': np.array(voltages),
        'current': np.array(currents),
        'power': np.array(powers),
        'v_ref': np.array(v_refs),
        'controller': controller
    }


def main():
    """主函数: CV算法演示"""
    print("=" * 80)
    print("案例9: 恒电压法")
    print("Case 9: Constant Voltage MPPT")
    print("=" * 80)
    
    # 1. 创建PV组件
    print("\n步骤1: 创建光伏组件")
    print("-" * 80)
    
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
    module = PVModule(cell, Ns=60, Nb=3, name="60片组件")
    module.set_uniform_conditions(T=298.15, G=1000.0)
    
    vmpp_true, impp_true, pmpp_true = module.find_mpp()
    voc_module = module.Voc
    
    print(f"组件参数:")
    print(f"  Voc  = {voc_module:.2f} V")
    print(f"  Vmpp = {vmpp_true:.2f} V")
    print(f"  Vmpp/Voc = {vmpp_true/voc_module:.3f}")
    print(f"  Pmpp = {pmpp_true:.2f} W")
    
    # 2. 场景1: 不同电压比例
    print("\n步骤2: 场景1 - 不同电压比例对比")
    print("-" * 80)
    
    ratios = [0.70, 0.76, 0.80]
    results_ratio = {}
    
    for ratio in ratios:
        print(f"\n测试比例: {ratio}")
        
        algo = ConstantVoltage(voltage_ratio=ratio, voc=voc_module)
        result = simulate_mppt(module, algo, v_init=vmpp_true*0.8,
                              num_steps=100, dt=0.1)
        
        perf = result['controller'].evaluate_performance(pmpp_true)
        
        print(f"  参考电压:   {ratio*voc_module:.2f} V")
        print(f"  跟踪效率:   {perf['efficiency']:.2f}%")
        print(f"  平均功率:   {perf['p_avg']:.2f} W")
        
        results_ratio[ratio] = result
    
    # 3. 场景2: CV vs P&O vs INC
    print("\n步骤3: 场景2 - 三种算法对比")
    print("-" * 80)
    
    v_init = vmpp_true * 0.7
    
    # CV (最优比例0.76)
    print("\n测试CV...")
    algo_cv = ConstantVoltage(voltage_ratio=0.76, voc=voc_module)
    result_cv = simulate_mppt(module, algo_cv, v_init, num_steps=150, dt=0.1)
    perf_cv = result_cv['controller'].evaluate_performance(pmpp_true)
    
    print(f"  跟踪效率:   {perf_cv['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_cv['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_cv['settling_time']} 步")
    
    # P&O
    print("\n测试P&O...")
    algo_po = PerturbAndObserve(step_size=1.0, initial_voltage=v_init)
    result_po = simulate_mppt(module, algo_po, v_init, num_steps=150, dt=0.1)
    perf_po = result_po['controller'].evaluate_performance(pmpp_true)
    
    print(f"  跟踪效率:   {perf_po['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_po['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_po['settling_time']} 步")
    
    # INC
    print("\n测试INC...")
    algo_inc = IncrementalConductance(step_size=1.0, initial_voltage=v_init)
    result_inc = simulate_mppt(module, algo_inc, v_init, num_steps=150, dt=0.1)
    perf_inc = result_inc['controller'].evaluate_performance(pmpp_true)
    
    print(f"  跟踪效率:   {perf_inc['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_inc['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_inc['settling_time']} 步")
    
    # 4. 场景3: 辐照度变化响应
    print("\n步骤4: 场景3 - 辐照度变化响应")
    print("-" * 80)
    
    algos_irr = {
        'CV': ConstantVoltage(voltage_ratio=0.76, voc=voc_module),
        'P&O': PerturbAndObserve(step_size=1.0, initial_voltage=vmpp_true),
        'INC': IncrementalConductance(step_size=1.0, initial_voltage=vmpp_true)
    }
    
    results_irr = {}
    
    for name, algo in algos_irr.items():
        controller = MPPTController(algo, v_min=0, v_max=module.Voc)
        
        v_pv = vmpp_true
        time_list, power_list, irr_list = [], [], []
        
        for step in range(200):
            t = step * 0.1
            
            # 辐照度阶跃: t<5s时1000, t>=5s时600
            if t < 5.0:
                G = 1000.0
            else:
                G = 600.0
            
            module.set_uniform_conditions(T=298.15, G=G)
            
            i_pv = module.calculate_current(v_pv)
            p_pv = v_pv * i_pv
            
            v_ref = controller.step(v_pv, i_pv)
            v_pv = v_pv + 0.5 * (v_ref - v_pv)
            
            time_list.append(t)
            power_list.append(p_pv)
            irr_list.append(G)
        
        results_irr[name] = {
            'time': np.array(time_list),
            'power': np.array(power_list),
            'irradiance': np.array(irr_list)
        }
    
    print(f"辐照度从1000→600 W/m²")
    for name, data in results_irr.items():
        p_before = data['power'][30]
        p_after = data['power'][-1]
        print(f"  {name}: {p_before:.1f}W → {p_after:.1f}W")
    
    # 5. 可视化
    print("\n步骤5: 结果可视化")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 图1: P-V曲线+不同比例的CV点
    ax1 = plt.subplot(3, 3, 1)
    V_curve, P_curve = module.get_pv_curve(300)
    ax1.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    ax1.plot(vmpp_true, pmpp_true, 'r*', markersize=15, label='真实MPP')
    
    colors = ['blue', 'green', 'orange']
    for ratio, color in zip(ratios, colors):
        v_cv = ratio * voc_module
        i_cv = module.calculate_current(v_cv)
        p_cv = v_cv * i_cv
        ax1.plot(v_cv, p_cv, 'o', markersize=10, color=color,
                label=f'CV k={ratio}')
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('功率 (W)', fontsize=11)
    ax1.set_title('场景1: 不同电压比例', fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 不同比例的效率
    ax2 = plt.subplot(3, 3, 2)
    efficiencies = []
    for ratio in ratios:
        perf = results_ratio[ratio]['controller'].evaluate_performance(pmpp_true)
        efficiencies.append(perf['efficiency'])
    
    bars = ax2.bar([str(r) for r in ratios], efficiencies,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax2.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax2.set_xlabel('电压比例 k', fontsize=11)
    ax2.set_title('不同比例的跟踪效率', fontsize=12)
    ax2.set_ylim([85, 100])
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, efficiencies):
        ax2.text(bar.get_x() + bar.get_width()/2, val,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 图3: 三种算法P-V轨迹
    ax3 = plt.subplot(3, 3, 3)
    ax3.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    ax3.plot(vmpp_true, pmpp_true, 'r*', markersize=15, label='真实MPP')
    ax3.plot(result_cv['voltage'], result_cv['power'],
            'b-', alpha=0.6, linewidth=1.5, label='CV')
    ax3.plot(result_po['voltage'], result_po['power'],
            'g-', alpha=0.6, linewidth=1.5, label='P&O')
    ax3.plot(result_inc['voltage'], result_inc['power'],
            'm-', alpha=0.6, linewidth=1.5, label='INC')
    
    ax3.set_xlabel('电压 (V)', fontsize=11)
    ax3.set_ylabel('功率 (W)', fontsize=11)
    ax3.set_title('场景2: 跟踪轨迹对比', fontsize=12)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 功率时间曲线
    ax4 = plt.subplot(3, 3, 4)
    ax4.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax4.plot(result_cv['time'], result_cv['power'],
            'b-', linewidth=2, alpha=0.7, label='CV')
    ax4.plot(result_po['time'], result_po['power'],
            'g-', linewidth=2, alpha=0.7, label='P&O')
    ax4.plot(result_inc['time'], result_inc['power'],
            'm-', linewidth=2, alpha=0.7, label='INC')
    
    ax4.set_xlabel('时间 (s)', fontsize=11)
    ax4.set_ylabel('功率 (W)', fontsize=11)
    ax4.set_title('功率响应对比', fontsize=12)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # 图5: 电压时间曲线
    ax5 = plt.subplot(3, 3, 5)
    ax5.axhline(y=vmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax5.plot(result_cv['time'], result_cv['voltage'],
            'b-', linewidth=2, alpha=0.7, label='CV')
    ax5.plot(result_po['time'], result_po['voltage'],
            'g-', linewidth=2, alpha=0.7, label='P&O')
    ax5.plot(result_inc['time'], result_inc['voltage'],
            'm-', linewidth=2, alpha=0.7, label='INC')
    
    ax5.set_xlabel('时间 (s)', fontsize=11)
    ax5.set_ylabel('电压 (V)', fontsize=11)
    ax5.set_title('电压响应对比', fontsize=12)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 三种算法性能对比
    ax6 = plt.subplot(3, 3, 6)
    algorithms = ['CV', 'P&O', 'INC']
    effs = [perf_cv['efficiency'], perf_po['efficiency'], perf_inc['efficiency']]
    
    bars = ax6.bar(algorithms, effs,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax6.axhline(y=100, color='r', linestyle='--', alpha=0.5)
    ax6.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax6.set_title('跟踪效率对比', fontsize=12)
    ax6.set_ylim([85, 100])
    ax6.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, effs):
        ax6.text(bar.get_x() + bar.get_width()/2, val,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 图7: 辐照度变化响应
    ax7 = plt.subplot(3, 3, 7)
    ax7_twin = ax7.twinx()
    
    for name, data in results_irr.items():
        ax7.plot(data['time'], data['power'], linewidth=2, label=name, alpha=0.7)
    
    ax7_twin.plot(results_irr['CV']['time'], results_irr['CV']['irradiance'],
                 'r--', linewidth=2, alpha=0.5, label='辐照度')
    
    ax7.set_xlabel('时间 (s)', fontsize=11)
    ax7.set_ylabel('功率 (W)', fontsize=11)
    ax7_twin.set_ylabel('辐照度 (W/m²)', fontsize=11, color='r')
    ax7.set_title('场景3: 辐照度阶跃响应', fontsize=12)
    ax7.legend(loc='upper right', fontsize=9)
    ax7_twin.tick_params(axis='y', labelcolor='r')
    ax7.grid(True, alpha=0.3)
    
    # 图8: 建立时间对比
    ax8 = plt.subplot(3, 3, 8)
    settling_times = [perf_cv['settling_time'], perf_po['settling_time'],
                     perf_inc['settling_time']]
    
    bars = ax8.bar(algorithms, settling_times,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax8.set_ylabel('建立时间 (步)', fontsize=11)
    ax8.set_title('建立时间对比', fontsize=12)
    ax8.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, settling_times):
        ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{val}', ha='center', va='bottom', fontsize=9)
    
    # 图9: 总结表格
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    summary_data = [
        ['指标', 'CV', 'P&O', 'INC'],
        ['跟踪效率', f'{perf_cv["efficiency"]:.1f}%',
         f'{perf_po["efficiency"]:.1f}%',
         f'{perf_inc["efficiency"]:.1f}%'],
        ['稳态振荡', f'{perf_cv["oscillation"]:.2f}W',
         f'{perf_po["oscillation"]:.2f}W',
         f'{perf_inc["oscillation"]:.2f}W'],
        ['建立时间', f'{perf_cv["settling_time"]}步',
         f'{perf_po["settling_time"]}步',
         f'{perf_inc["settling_time"]}步'],
        ['计算复杂度', '极低', '低', '中'],
        ['精度等级', '中', '高', '极高']
    ]
    
    table = ax9.table(cellText=summary_data, cellLoc='center',
                     loc='center', bbox=[0, 0.15, 1, 0.75])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax9.set_title('性能总结', fontsize=12, pad=20)
    
    plt.suptitle('恒电压法MPPT算法', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'constant_voltage_mppt.png'),
                dpi=300, bbox_inches='tight')
    print(f"图表已保存")
    
    # 6. 总结
    print("\n步骤6: 总结")
    print("=" * 80)
    
    print("\nCV算法特点:")
    print("  优点:")
    print("    ✅ 极简单(1行代码)")
    print("    ✅ 极快速(瞬时响应)")
    print("    ✅ 成本极低")
    print("    ✅ 无振荡")
    
    print("\n  缺点:")
    print("    ❌ 精度低(90-95%)")
    print("    ❌ 不能跟踪变化")
    print("    ❌ 依赖Voc测量")
    
    print("\n三种算法对比:")
    print(f"  CV:   {perf_cv['efficiency']:.1f}%效率, {perf_cv['settling_time']}步, 极简单")
    print(f"  P&O:  {perf_po['efficiency']:.1f}%效率, {perf_po['settling_time']}步, 简单")
    print(f"  INC:  {perf_inc['efficiency']:.1f}%效率, {perf_inc['settling_time']}步, 复杂")
    
    print("\n应用建议:")
    print("  CV:   简单系统、成本敏感、快速启动")
    print("  P&O:  通用场合、性价比高")
    print("  INC:  高精度要求、高端系统")
    
    print("\n" + "=" * 80)
    print("案例9主程序完成！")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
