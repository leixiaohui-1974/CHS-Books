"""
案例8: 增量电导法
Case 8: Incremental Conductance MPPT

工程背景:
--------
INC是精度更高的MPPT算法:
- 基于理论推导
- 无稳态振荡
- 响应快速
- 适合高精度场合

学习目标:
--------
1. 理解INC算法原理
2. 掌握dI/dV=-I/V条件
3. 对比INC与P&O性能
4. 学习改进策略
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
                                          ModifiedINC, MPPTController)


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
    """主函数: INC算法演示"""
    print("=" * 80)
    print("案例8: 增量电导法")
    print("Case 8: Incremental Conductance MPPT")
    print("=" * 80)
    
    # 1. 创建PV组件
    print("\n步骤1: 创建光伏组件")
    print("-" * 80)
    
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
    module = PVModule(cell, Ns=60, Nb=3, name="60片组件")
    module.set_uniform_conditions(T=298.15, G=1000.0)
    
    vmpp_true, impp_true, pmpp_true = module.find_mpp()
    
    print(f"组件参数:")
    print(f"  Vmpp = {vmpp_true:.2f} V")
    print(f"  Impp = {impp_true:.2f} A")
    print(f"  Pmpp = {pmpp_true:.2f} W")
    
    # 2. 场景1: INC vs P&O 对比
    print("\n步骤2: 场景1 - INC vs P&O 对比")
    print("-" * 80)
    
    v_init = vmpp_true * 0.7
    
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
    algo_inc = IncrementalConductance(step_size=1.0, initial_voltage=v_init,
                                     threshold=0.01)
    result_inc = simulate_mppt(module, algo_inc, v_init, num_steps=150, dt=0.1)
    perf_inc = result_inc['controller'].evaluate_performance(pmpp_true)
    
    print(f"  跟踪效率:   {perf_inc['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_inc['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_inc['settling_time']} 步")
    
    print(f"\n性能提升:")
    print(f"  效率提升:   {perf_inc['efficiency'] - perf_po['efficiency']:+.2f}%")
    print(f"  振荡减小:   {(1-perf_inc['oscillation']/perf_po['oscillation'])*100:.1f}%")
    
    # 3. 场景2: 改进型INC
    print("\n步骤3: 场景2 - 改进型INC")
    print("-" * 80)
    
    algo_mod = ModifiedINC(step_size_min=0.2, step_size_max=3.0,
                          initial_voltage=v_init, threshold=0.01, deadband=0.01)
    result_mod = simulate_mppt(module, algo_mod, v_init, num_steps=150, dt=0.1)
    perf_mod = result_mod['controller'].evaluate_performance(pmpp_true)
    
    print(f"改进型INC:")
    print(f"  跟踪效率:   {perf_mod['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_mod['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_mod['settling_time']} 步")
    
    # 4. 场景3: 噪声环境测试
    print("\n步骤4: 场景3 - 噪声环境测试")
    print("-" * 80)
    
    # 添加噪声的仿真
    print("添加5%测量噪声...")
    
    algo_po_noise = PerturbAndObserve(step_size=1.0, initial_voltage=v_init)
    algo_inc_noise = IncrementalConductance(step_size=1.0, initial_voltage=v_init)
    algo_mod_noise = ModifiedINC(step_size_min=0.2, step_size_max=3.0,
                                 initial_voltage=v_init)
    
    controllers = [
        MPPTController(algo_po_noise, v_min=0, v_max=module.Voc),
        MPPTController(algo_inc_noise, v_min=0, v_max=module.Voc),
        MPPTController(algo_mod_noise, v_min=0, v_max=module.Voc)
    ]
    
    results_noise = []
    for ctrl in controllers:
        v_pv = v_init
        powers = []
        
        for step in range(150):
            i_pv = module.calculate_current(v_pv)
            
            # 添加噪声
            i_noisy = i_pv * (1 + np.random.normal(0, 0.05))
            v_noisy = v_pv * (1 + np.random.normal(0, 0.05))
            
            v_ref = ctrl.step(v_noisy, i_noisy)
            v_pv = v_pv + 0.5 * (v_ref - v_pv)
            powers.append(v_pv * i_pv)
        
        perf_noise = ctrl.evaluate_performance(pmpp_true)
        results_noise.append(perf_noise)
        
    print(f"\nP&O (噪声):       效率={results_noise[0]['efficiency']:.2f}%")
    print(f"INC (噪声):       效率={results_noise[1]['efficiency']:.2f}%")
    print(f"改进INC (噪声):   效率={results_noise[2]['efficiency']:.2f}%")
    
    # 5. 可视化
    print("\n步骤5: 结果可视化")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 图1: P-V曲线+跟踪轨迹
    ax1 = plt.subplot(3, 3, 1)
    V_curve, P_curve = module.get_pv_curve(300)
    ax1.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    ax1.plot(vmpp_true, pmpp_true, 'r*', markersize=15, label='真实MPP')
    ax1.plot(result_po['voltage'], result_po['power'], 
            'b-', alpha=0.6, linewidth=1.5, label='P&O')
    ax1.plot(result_inc['voltage'], result_inc['power'],
            'g-', alpha=0.6, linewidth=1.5, label='INC')
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('功率 (W)', fontsize=11)
    ax1.set_title('场景1: P&O vs INC (跟踪轨迹)', fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 功率时间曲线
    ax2 = plt.subplot(3, 3, 2)
    ax2.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax2.plot(result_po['time'], result_po['power'], 
            'b-', linewidth=2, alpha=0.7, label='P&O')
    ax2.plot(result_inc['time'], result_inc['power'],
            'g-', linewidth=2, alpha=0.7, label='INC')
    
    ax2.set_xlabel('时间 (s)', fontsize=11)
    ax2.set_ylabel('功率 (W)', fontsize=11)
    ax2.set_title('功率响应对比', fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 电压时间曲线
    ax3 = plt.subplot(3, 3, 3)
    ax3.axhline(y=vmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax3.plot(result_po['time'], result_po['voltage'],
            'b-', linewidth=2, alpha=0.7, label='P&O')
    ax3.plot(result_inc['time'], result_inc['voltage'],
            'g-', linewidth=2, alpha=0.7, label='INC')
    
    ax3.set_xlabel('时间 (s)', fontsize=11)
    ax3.set_ylabel('电压 (V)', fontsize=11)
    ax3.set_title('电压响应对比', fontsize=12)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 稳态振荡分析(放大)
    ax4 = plt.subplot(3, 3, 4)
    n_zoom = 100
    ax4.plot(result_po['time'][-n_zoom:], result_po['power'][-n_zoom:],
            'b-', linewidth=2, alpha=0.7, label='P&O')
    ax4.plot(result_inc['time'][-n_zoom:], result_inc['power'][-n_zoom:],
            'g-', linewidth=2, alpha=0.7, label='INC')
    ax4.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    
    ax4.set_xlabel('时间 (s)', fontsize=11)
    ax4.set_ylabel('功率 (W)', fontsize=11)
    ax4.set_title('稳态振荡分析(放大)', fontsize=12)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # 图5: 三种算法对比
    ax5 = plt.subplot(3, 3, 5)
    ax5.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax5.plot(result_po['time'], result_po['power'],
            'b-', linewidth=2, alpha=0.7, label='P&O')
    ax5.plot(result_inc['time'], result_inc['power'],
            'g-', linewidth=2, alpha=0.7, label='INC')
    ax5.plot(result_mod['time'], result_mod['power'],
            'm-', linewidth=2, alpha=0.7, label='改进INC')
    
    ax5.set_xlabel('时间 (s)', fontsize=11)
    ax5.set_ylabel('功率 (W)', fontsize=11)
    ax5.set_title('场景2: 三种算法对比', fontsize=12)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 性能指标对比
    ax6 = plt.subplot(3, 3, 6)
    algorithms = ['P&O', 'INC', '改进INC']
    efficiencies = [perf_po['efficiency'], perf_inc['efficiency'], perf_mod['efficiency']]
    
    bars = ax6.bar(algorithms, efficiencies, color=['steelblue', 'seagreen', 'coral'],
                   alpha=0.7)
    ax6.axhline(y=100, color='r', linestyle='--', alpha=0.5)
    ax6.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax6.set_title('跟踪效率对比', fontsize=12)
    ax6.set_ylim([95, 100])
    ax6.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, efficiencies):
        ax6.text(bar.get_x() + bar.get_width()/2, val,
                f'{val:.2f}%', ha='center', va='bottom', fontsize=9)
    
    # 图7: 振荡对比
    ax7 = plt.subplot(3, 3, 7)
    oscillations = [perf_po['oscillation'], perf_inc['oscillation'],
                   perf_mod['oscillation']]
    
    bars = ax7.bar(algorithms, oscillations,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax7.set_ylabel('稳态振荡 (W)', fontsize=11)
    ax7.set_title('稳态振荡对比', fontsize=12)
    ax7.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, oscillations):
        ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 图8: 噪声环境性能
    ax8 = plt.subplot(3, 3, 8)
    eff_noise = [r['efficiency'] for r in results_noise]
    
    x = np.arange(len(algorithms))
    width = 0.35
    
    bars1 = ax8.bar(x - width/2, efficiencies, width, label='无噪声',
                    alpha=0.7, color='steelblue')
    bars2 = ax8.bar(x + width/2, eff_noise, width, label='5%噪声',
                    alpha=0.7, color='coral')
    
    ax8.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax8.set_title('场景3: 噪声环境测试', fontsize=12)
    ax8.set_xticks(x)
    ax8.set_xticklabels(algorithms, fontsize=9)
    ax8.legend(fontsize=9)
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 图9: 总结表格
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    summary_data = [
        ['算法', 'P&O', 'INC', '改进INC'],
        ['跟踪效率', f'{perf_po["efficiency"]:.2f}%',
         f'{perf_inc["efficiency"]:.2f}%',
         f'{perf_mod["efficiency"]:.2f}%'],
        ['稳态振荡', f'{perf_po["oscillation"]:.3f}W',
         f'{perf_inc["oscillation"]:.3f}W',
         f'{perf_mod["oscillation"]:.3f}W'],
        ['建立时间', f'{perf_po["settling_time"]}步',
         f'{perf_inc["settling_time"]}步',
         f'{perf_mod["settling_time"]}步'],
        ['噪声鲁棒性', '中', '较差', '好']
    ]
    
    table = ax9.table(cellText=summary_data, cellLoc='center',
                     loc='center', bbox=[0, 0.2, 1, 0.7])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax9.set_title('性能总结', fontsize=12, pad=20)
    
    plt.suptitle('增量电导法MPPT算法', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'incremental_conductance_mppt.png'),
                dpi=300, bbox_inches='tight')
    print(f"图表已保存")
    
    # 6. 总结
    print("\n步骤6: 总结")
    print("=" * 80)
    
    print("\nINC vs P&O 对比:")
    print("  跟踪效率:   INC优于P&O")
    print("  稳态振荡:   INC显著优于P&O")
    print("  响应速度:   INC略快于P&O")
    print("  噪声敏感:   INC更敏感,需要滤波")
    
    print("\n适用场景:")
    print("  P&O:     通用场合,成本敏感")
    print("  INC:     精度要求高,环境稳定")
    print("  改进INC: 兼顾性能与鲁棒性")
    
    print(f"\n最佳效率: {max(perf_po['efficiency'], perf_inc['efficiency'], perf_mod['efficiency']):.2f}%")
    
    print("\n" + "=" * 80)
    print("案例8主程序完成！")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
