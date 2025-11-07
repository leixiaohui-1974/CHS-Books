"""
案例7: P&O扰动观察法
Case 7: Perturb and Observe MPPT

工程背景:
--------
P&O是最经典、应用最广的MPPT算法:
- 不需要PV特性信息
- 实现简单成本低
- 适应性强
- 工业界首选方案

学习目标:
--------
1. 理解P&O算法原理
2. 掌握算法实现要点
3. 分析性能特性
4. 学习参数调优
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
from code.models.mppt_algorithms import PerturbAndObserve, AdaptivePO, MPPTController


def simulate_mppt_tracking(module: PVModule,
                           algorithm,
                           v_init: float,
                           num_steps: int = 100,
                           dt: float = 0.1) -> dict:
    """
    模拟MPPT跟踪过程
    
    Parameters:
    -----------
    module : PVModule
        光伏组件
    algorithm : MPPTAlgorithm
        MPPT算法
    v_init : float
        初始电压(V)
    num_steps : int
        仿真步数
    dt : float
        时间步长(s)
        
    Returns:
    --------
    dict : 跟踪结果
    """
    # 创建控制器
    controller = MPPTController(algorithm, v_min=0, v_max=module.Voc)
    
    # 初始化
    v_pv = v_init
    
    # 仿真循环
    time = []
    voltages = []
    currents = []
    powers = []
    v_refs = []
    
    for step in range(num_steps):
        t = step * dt
        
        # 获取当前工作点
        i_pv = module.calculate_current(v_pv)
        p_pv = v_pv * i_pv
        
        # MPPT更新
        v_ref = controller.step(v_pv, i_pv)
        
        # 简化的电压跟踪(假设理想跟踪)
        v_pv = v_pv + 0.5 * (v_ref - v_pv)  # 一阶滞后
        
        # 记录
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
    """主函数: P&O算法演示"""
    print("=" * 80)
    print("案例7: P&O扰动观察法")
    print("Case 7: Perturb and Observe MPPT")
    print("=" * 80)
    
    # 1. 创建PV组件
    print("\n步骤1: 创建光伏组件")
    print("-" * 80)
    
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
    module = PVModule(cell, Ns=60, Nb=3, name="60片组件")
    module.set_uniform_conditions(T=298.15, G=1000.0)
    
    # 获取真实MPP
    vmpp_true, impp_true, pmpp_true = module.find_mpp()
    
    print(f"组件参数:")
    print(f"  Voc  = {module.Voc:.2f} V")
    print(f"  Isc  = {module.Isc:.2f} A")
    print(f"  Vmpp = {vmpp_true:.2f} V")
    print(f"  Impp = {impp_true:.2f} A")
    print(f"  Pmpp = {pmpp_true:.2f} W")
    
    # 2. 场景1: 标准P&O (不同步长)
    print("\n步骤2: 场景1 - 不同步长对比")
    print("-" * 80)
    
    step_sizes = [0.5, 1.0, 2.0]
    results_step = {}
    
    for step_size in step_sizes:
        print(f"\n测试步长: {step_size} V")
        
        algo = PerturbAndObserve(
            step_size=step_size,
            initial_voltage=vmpp_true * 0.7  # 从70% Vmpp开始
        )
        
        result = simulate_mppt_tracking(
            module, algo,
            v_init=vmpp_true * 0.7,
            num_steps=150,
            dt=0.1
        )
        
        # 评估性能
        perf = result['controller'].evaluate_performance(pmpp_true)
        
        print(f"  平均功率:   {perf['p_avg']:.2f} W")
        print(f"  跟踪效率:   {perf['efficiency']:.2f}%")
        print(f"  稳态振荡:   {perf['oscillation']:.3f} W")
        print(f"  建立时间:   {perf['settling_time']} 步")
        
        results_step[step_size] = result
    
    # 3. 场景2: 自适应P&O vs 标准P&O
    print("\n步骤3: 场景2 - 自适应P&O对比")
    print("-" * 80)
    
    # 标准P&O
    algo_std = PerturbAndObserve(
        step_size=1.0,
        initial_voltage=vmpp_true * 0.7
    )
    result_std = simulate_mppt_tracking(
        module, algo_std,
        v_init=vmpp_true * 0.7,
        num_steps=150,
        dt=0.1
    )
    perf_std = result_std['controller'].evaluate_performance(pmpp_true)
    
    # 自适应P&O
    algo_adp = AdaptivePO(
        step_size_min=0.2,
        step_size_max=3.0,
        initial_voltage=vmpp_true * 0.7
    )
    result_adp = simulate_mppt_tracking(
        module, algo_adp,
        v_init=vmpp_true * 0.7,
        num_steps=150,
        dt=0.1
    )
    perf_adp = result_adp['controller'].evaluate_performance(pmpp_true)
    
    print(f"\n标准P&O:")
    print(f"  跟踪效率:   {perf_std['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_std['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_std['settling_time']} 步")
    
    print(f"\n自适应P&O:")
    print(f"  跟踪效率:   {perf_adp['efficiency']:.2f}%")
    print(f"  稳态振荡:   {perf_adp['oscillation']:.3f} W")
    print(f"  建立时间:   {perf_adp['settling_time']} 步")
    
    # 4. 场景3: 辐照度变化响应
    print("\n步骤4: 场景3 - 辐照度变化响应")
    print("-" * 80)
    
    algo_resp = PerturbAndObserve(step_size=1.0, initial_voltage=vmpp_true)
    controller_resp = MPPTController(algo_resp, v_min=0, v_max=module.Voc)
    
    # 模拟辐照度阶跃变化
    time_resp = []
    voltage_resp = []
    power_resp = []
    irradiance_resp = []
    
    v_pv = vmpp_true
    
    for step in range(200):
        t = step * 0.1
        
        # 辐照度阶跃: t<5s时1000W/m², t>=5s时600W/m²
        if t < 5.0:
            G = 1000.0
        else:
            G = 600.0
        
        module.set_uniform_conditions(T=298.15, G=G)
        
        # 获取当前工作点
        i_pv = module.calculate_current(v_pv)
        p_pv = v_pv * i_pv
        
        # MPPT更新
        v_ref = controller_resp.step(v_pv, i_pv)
        v_pv = v_pv + 0.5 * (v_ref - v_pv)
        
        # 记录
        time_resp.append(t)
        voltage_resp.append(v_pv)
        power_resp.append(p_pv)
        irradiance_resp.append(G)
    
    print(f"辐照度从1000→600 W/m²")
    print(f"功率跟踪: {power_resp[30]:.1f}W → {power_resp[-1]:.1f}W")
    
    # 5. 可视化
    print("\n步骤5: 结果可视化")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 图1: P-V曲线+跟踪轨迹(不同步长)
    ax1 = plt.subplot(3, 3, 1)
    V_curve, P_curve = module.get_pv_curve(300)
    ax1.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    ax1.plot(vmpp_true, pmpp_true, 'r*', markersize=15, label='真实MPP')
    
    colors = ['blue', 'green', 'orange']
    for (step_size, result), color in zip(results_step.items(), colors):
        ax1.plot(result['voltage'], result['power'], 
                alpha=0.6, linewidth=1.5, color=color,
                label=f'步长={step_size}V')
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('功率 (W)', fontsize=11)
    ax1.set_title('场景1: 不同步长的跟踪轨迹', fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 功率时间曲线(不同步长)
    ax2 = plt.subplot(3, 3, 2)
    ax2.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    
    for (step_size, result), color in zip(results_step.items(), colors):
        ax2.plot(result['time'], result['power'], 
                linewidth=2, color=color, alpha=0.7,
                label=f'步长={step_size}V')
    
    ax2.set_xlabel('时间 (s)', fontsize=11)
    ax2.set_ylabel('功率 (W)', fontsize=11)
    ax2.set_title('功率响应曲线', fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 电压时间曲线(不同步长)
    ax3 = plt.subplot(3, 3, 3)
    ax3.axhline(y=vmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    
    for (step_size, result), color in zip(results_step.items(), colors):
        ax3.plot(result['time'], result['voltage'], 
                linewidth=2, color=color, alpha=0.7,
                label=f'步长={step_size}V')
    
    ax3.set_xlabel('时间 (s)', fontsize=11)
    ax3.set_ylabel('电压 (V)', fontsize=11)
    ax3.set_title('电压响应曲线', fontsize=12)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 标准 vs 自适应 (P-V轨迹)
    ax4 = plt.subplot(3, 3, 4)
    ax4.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    ax4.plot(vmpp_true, pmpp_true, 'r*', markersize=15, label='真实MPP')
    ax4.plot(result_std['voltage'], result_std['power'], 
            'b-', alpha=0.6, linewidth=1.5, label='标准P&O')
    ax4.plot(result_adp['voltage'], result_adp['power'], 
            'g-', alpha=0.6, linewidth=1.5, label='自适应P&O')
    
    ax4.set_xlabel('电压 (V)', fontsize=11)
    ax4.set_ylabel('功率 (W)', fontsize=11)
    ax4.set_title('场景2: 标准 vs 自适应 (轨迹)', fontsize=12)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # 图5: 标准 vs 自适应 (功率)
    ax5 = plt.subplot(3, 3, 5)
    ax5.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax5.plot(result_std['time'], result_std['power'], 
            'b-', linewidth=2, alpha=0.7, label='标准P&O')
    ax5.plot(result_adp['time'], result_adp['power'], 
            'g-', linewidth=2, alpha=0.7, label='自适应P&O')
    
    ax5.set_xlabel('时间 (s)', fontsize=11)
    ax5.set_ylabel('功率 (W)', fontsize=11)
    ax5.set_title('功率响应对比', fontsize=12)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 性能对比柱状图
    ax6 = plt.subplot(3, 3, 6)
    metrics = ['跟踪效率(%)', '振荡(W)', '建立时间(步)']
    std_values = [perf_std['efficiency'], perf_std['oscillation'], perf_std['settling_time']]
    adp_values = [perf_adp['efficiency'], perf_adp['oscillation'], perf_adp['settling_time']]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    # 归一化显示
    std_norm = [std_values[0], std_values[1]*10, std_values[2]/10]
    adp_norm = [adp_values[0], adp_values[1]*10, adp_values[2]/10]
    
    ax6.bar(x - width/2, std_norm, width, label='标准P&O', alpha=0.7, color='steelblue')
    ax6.bar(x + width/2, adp_norm, width, label='自适应P&O', alpha=0.7, color='seagreen')
    
    ax6.set_ylabel('归一化值', fontsize=11)
    ax6.set_title('性能指标对比', fontsize=12)
    ax6.set_xticks(x)
    ax6.set_xticklabels(['效率', '振荡×10', '时间/10'], fontsize=9)
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 图7: 辐照度变化响应
    ax7 = plt.subplot(3, 3, 7)
    ax7_twin = ax7.twinx()
    
    ax7.plot(time_resp, power_resp, 'b-', linewidth=2, label='输出功率')
    ax7_twin.plot(time_resp, irradiance_resp, 'r--', linewidth=2, alpha=0.7, label='辐照度')
    
    ax7.set_xlabel('时间 (s)', fontsize=11)
    ax7.set_ylabel('功率 (W)', fontsize=11, color='b')
    ax7_twin.set_ylabel('辐照度 (W/m²)', fontsize=11, color='r')
    ax7.set_title('场景3: 辐照度阶跃响应', fontsize=12)
    ax7.tick_params(axis='y', labelcolor='b')
    ax7_twin.tick_params(axis='y', labelcolor='r')
    ax7.grid(True, alpha=0.3)
    
    # 图8: 稳态振荡分析(放大最后10秒)
    ax8 = plt.subplot(3, 3, 8)
    n_zoom = 100  # 最后100个点
    ax8.plot(result_std['time'][-n_zoom:], result_std['power'][-n_zoom:], 
            'b-', linewidth=2, alpha=0.7, label='标准P&O')
    ax8.plot(result_adp['time'][-n_zoom:], result_adp['power'][-n_zoom:], 
            'g-', linewidth=2, alpha=0.7, label='自适应P&O')
    ax8.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    
    ax8.set_xlabel('时间 (s)', fontsize=11)
    ax8.set_ylabel('功率 (W)', fontsize=11)
    ax8.set_title('稳态振荡分析(放大)', fontsize=12)
    ax8.legend(fontsize=9)
    ax8.grid(True, alpha=0.3)
    
    # 图9: 总结表格
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    summary_data = [
        ['指标', '标准P&O', '自适应P&O', '改进'],
        ['跟踪效率', f'{perf_std["efficiency"]:.2f}%', 
         f'{perf_adp["efficiency"]:.2f}%',
         f'{perf_adp["efficiency"]-perf_std["efficiency"]:+.2f}%'],
        ['稳态振荡', f'{perf_std["oscillation"]:.3f}W',
         f'{perf_adp["oscillation"]:.3f}W',
         f'{(1-perf_adp["oscillation"]/perf_std["oscillation"])*100:.1f}%↓'],
        ['建立时间', f'{perf_std["settling_time"]}步',
         f'{perf_adp["settling_time"]}步',
         f'{perf_std["settling_time"]-perf_adp["settling_time"]:+d}步']
    ]
    
    table = ax9.table(cellText=summary_data, cellLoc='center',
                     loc='center', bbox=[0, 0.3, 1, 0.6])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # 标题行加粗
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax9.set_title('性能总结', fontsize=12, pad=20)
    
    plt.suptitle('P&O扰动观察法MPPT算法', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'perturb_observe_mppt.png'),
                dpi=300, bbox_inches='tight')
    print(f"图表已保存")
    
    # 6. 总结
    print("\n步骤6: 总结")
    print("=" * 80)
    
    print("\nP&O算法特点:")
    print("  优点:")
    print("    ✅ 原理简单易实现")
    print("    ✅ 不需要PV特性")
    print("    ✅ 适应性强")
    print("    ✅ 成本低")
    
    print("\n  缺点:")
    print("    ❌ 稳态振荡")
    print("    ❌ 响应速度慢")
    print("    ❌ 快速变化环境误判")
    
    print("\n参数调优建议:")
    print("  步长小 → 振荡小, 响应慢")
    print("  步长大 → 振荡大, 响应快")
    print("  自适应 → 兼顾响应和稳态")
    
    print(f"\n最佳跟踪效率: {max(perf_std['efficiency'], perf_adp['efficiency']):.2f}%")
    
    print("\n" + "=" * 80)
    print("案例7主程序完成！")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
