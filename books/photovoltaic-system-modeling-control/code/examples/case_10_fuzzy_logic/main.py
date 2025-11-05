"""
案例10: 模糊逻辑MPPT
Case 10: Fuzzy Logic MPPT

工程背景:
--------
模糊逻辑MPPT是高级智能算法:
- 不需要精确数学模型
- 鲁棒性强、抗噪声
- 响应快速
- 适合复杂工况

学习目标:
--------
1. 理解模糊逻辑原理
2. 掌握FIS系统设计
3. 学习规则库构建
4. 对比智能与传统算法
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
                                          FuzzyLogicMPPT, MPPTController)


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
    """主函数: Fuzzy MPPT演示"""
    print("=" * 80)
    print("案例10: 模糊逻辑MPPT")
    print("Case 10: Fuzzy Logic MPPT")
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
    print(f"  Pmpp = {pmpp_true:.2f} W")
    
    # 2. 场景1: Fuzzy vs P&O vs INC
    print("\n步骤2: 场景1 - 四种算法对比")
    print("-" * 80)
    
    v_init = vmpp_true * 0.7
    
    # Fuzzy
    print("\n测试Fuzzy...")
    algo_fuzzy = FuzzyLogicMPPT(step_size_max=3.0, initial_voltage=v_init)
    result_fuzzy = simulate_mppt(module, algo_fuzzy, v_init, num_steps=150, dt=0.1)
    perf_fuzzy = result_fuzzy['controller'].evaluate_performance(pmpp_true)
    
    print(f"  跟踪效率:   {perf_fuzzy['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_fuzzy['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_fuzzy['settling_time']} 步")
    
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
    
    # 3. 场景2: 噪声环境测试
    print("\n步骤3: 场景2 - 噪声环境鲁棒性")
    print("-" * 80)
    
    algos_noise = {
        'Fuzzy': FuzzyLogicMPPT(step_size_max=3.0, initial_voltage=v_init),
        'P&O': PerturbAndObserve(step_size=1.0, initial_voltage=v_init),
        'INC': IncrementalConductance(step_size=1.0, initial_voltage=v_init)
    }
    
    results_noise = {}
    
    for name, algo in algos_noise.items():
        controller = MPPTController(algo, v_min=0, v_max=module.Voc)
        
        v_pv = v_init
        powers = []
        
        for step in range(150):
            i_pv = module.calculate_current(v_pv)
            
            # 添加10%噪声
            i_noisy = i_pv * (1 + np.random.normal(0, 0.1))
            v_noisy = v_pv * (1 + np.random.normal(0, 0.1))
            
            v_ref = controller.step(v_noisy, i_noisy)
            v_pv = v_pv + 0.5 * (v_ref - v_pv)
            powers.append(v_pv * i_pv)
        
        perf = controller.evaluate_performance(pmpp_true)
        results_noise[name] = perf
    
    print(f"\nFuzzy (10%噪声):  效率={results_noise['Fuzzy']['efficiency']:.2f}%")
    print(f"P&O (10%噪声):    效率={results_noise['P&O']['efficiency']:.2f}%")
    print(f"INC (10%噪声):    效率={results_noise['INC']['efficiency']:.2f}%")
    
    # 4. 可视化
    print("\n步骤4: 结果可视化")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 10))
    
    # 图1: P-V曲线+跟踪轨迹
    ax1 = plt.subplot(2, 3, 1)
    V_curve, P_curve = module.get_pv_curve(300)
    ax1.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    ax1.plot(vmpp_true, pmpp_true, 'r*', markersize=15, label='真实MPP')
    ax1.plot(result_fuzzy['voltage'], result_fuzzy['power'],
            'b-', alpha=0.6, linewidth=1.5, label='Fuzzy')
    ax1.plot(result_po['voltage'], result_po['power'],
            'g-', alpha=0.6, linewidth=1.5, label='P&O')
    ax1.plot(result_inc['voltage'], result_inc['power'],
            'm-', alpha=0.6, linewidth=1.5, label='INC')
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('功率 (W)', fontsize=11)
    ax1.set_title('跟踪轨迹对比', fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 功率时间曲线
    ax2 = plt.subplot(2, 3, 2)
    ax2.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax2.plot(result_fuzzy['time'], result_fuzzy['power'],
            'b-', linewidth=2, alpha=0.7, label='Fuzzy')
    ax2.plot(result_po['time'], result_po['power'],
            'g-', linewidth=2, alpha=0.7, label='P&O')
    ax2.plot(result_inc['time'], result_inc['power'],
            'm-', linewidth=2, alpha=0.7, label='INC')
    
    ax2.set_xlabel('时间 (s)', fontsize=11)
    ax2.set_ylabel('功率 (W)', fontsize=11)
    ax2.set_title('功率响应对比', fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 跟踪效率对比
    ax3 = plt.subplot(2, 3, 3)
    algorithms = ['Fuzzy', 'P&O', 'INC']
    effs = [perf_fuzzy['efficiency'], perf_po['efficiency'], perf_inc['efficiency']]
    
    bars = ax3.bar(algorithms, effs,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax3.axhline(y=100, color='r', linestyle='--', alpha=0.5)
    ax3.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax3.set_title('跟踪效率对比', fontsize=12)
    ax3.set_ylim([95, 100])
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, effs):
        ax3.text(bar.get_x() + bar.get_width()/2, val,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 图4: 噪声环境性能
    ax4 = plt.subplot(2, 3, 4)
    effs_noise = [results_noise[alg]['efficiency'] for alg in algorithms]
    
    x = np.arange(len(algorithms))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, effs, width, label='无噪声',
                    alpha=0.7, color='steelblue')
    bars2 = ax4.bar(x + width/2, effs_noise, width, label='10%噪声',
                    alpha=0.7, color='coral')
    
    ax4.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax4.set_title('噪声环境测试', fontsize=12)
    ax4.set_xticks(x)
    ax4.set_xticklabels(algorithms, fontsize=9)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 图5: 建立时间对比
    ax5 = plt.subplot(2, 3, 5)
    settling_times = [perf_fuzzy['settling_time'], perf_po['settling_time'],
                     perf_inc['settling_time']]
    
    bars = ax5.bar(algorithms, settling_times,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax5.set_ylabel('建立时间 (步)', fontsize=11)
    ax5.set_title('建立时间对比', fontsize=12)
    ax5.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, settling_times):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{val}', ha='center', va='bottom', fontsize=9)
    
    # 图6: 总结表格
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    summary_data = [
        ['指标', 'Fuzzy', 'P&O', 'INC'],
        ['跟踪效率', f'{perf_fuzzy["efficiency"]:.1f}%',
         f'{perf_po["efficiency"]:.1f}%',
         f'{perf_inc["efficiency"]:.1f}%'],
        ['稳态振荡', f'{perf_fuzzy["oscillation"]:.2f}W',
         f'{perf_po["oscillation"]:.2f}W',
         f'{perf_inc["oscillation"]:.2f}W'],
        ['建立时间', f'{perf_fuzzy["settling_time"]}步',
         f'{perf_po["settling_time"]}步',
         f'{perf_inc["settling_time"]}步'],
        ['噪声鲁棒性', '优秀', '良好', '中等']
    ]
    
    table = ax6.table(cellText=summary_data, cellLoc='center',
                     loc='center', bbox=[0, 0.2, 1, 0.7])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax6.set_title('性能总结', fontsize=12, pad=20)
    
    plt.suptitle('模糊逻辑MPPT算法', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'fuzzy_logic_mppt.png'),
                dpi=300, bbox_inches='tight')
    print(f"图表已保存")
    
    # 5. 总结
    print("\n步骤5: 总结")
    print("=" * 80)
    
    print("\nFuzzy MPPT特点:")
    print("  优点:")
    print("    ✅ 鲁棒性强")
    print("    ✅ 响应快速")
    print("    ✅ 抗噪声能力强")
    print("    ✅ 不需要精确模型")
    
    print("\n  缺点:")
    print("    ❌ 规则设计复杂")
    print("    ❌ 计算量较大")
    print("    ❌ 需要专家知识")
    
    print("\n算法对比:")
    print(f"  Fuzzy: {perf_fuzzy['efficiency']:.1f}%效率, 鲁棒性优秀")
    print(f"  INC:   {perf_inc['efficiency']:.1f}%效率, 精度最高")
    print(f"  P&O:   {perf_po['efficiency']:.1f}%效率, 最简单")
    
    print("\n" + "=" * 80)
    print("案例10主程序完成！")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
