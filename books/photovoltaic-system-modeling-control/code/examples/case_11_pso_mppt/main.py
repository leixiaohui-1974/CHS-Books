"""
案例11: 粒子群优化MPPT
Case 11: Particle Swarm Optimization MPPT

工程背景:
--------
PSO是群智能优化算法:
- 全局搜索能力强
- 适合多峰优化
- 收敛速度快
- 无需梯度信息

学习目标:
--------
1. 理解群智能算法原理
2. 掌握PSO算法设计
3. 学习参数调优方法
4. 对比智能优化算法性能
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.animation import FuncAnimation

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule
from code.models.mppt_algorithms import (ParticleSwarmMPPT, PerturbAndObserve,
                                          FuzzyLogicMPPT, MPPTController)


def simulate_pso_mppt(module: PVModule, pso_algo, n_iterations: int = 30) -> dict:
    """模拟PSO MPPT寻优过程"""
    # 设置PV组件引用
    pso_algo.set_pv_module(module)
    
    history = {
        'iteration': [],
        'gbest_position': [],
        'gbest_fitness': [],
        'all_positions': [],
        'all_fitness': [],
        'converged': []
    }
    
    # 迭代寻优
    for step in range(n_iterations):
        # 获取当前电压和电流（这里使用模型）
        v_current = pso_algo.v_ref
        i_current = module.calculate_current(v_current)
        
        # 更新PSO
        v_ref = pso_algo.update(v_current, i_current)
        
        # 获取粒子群状态
        state = pso_algo.get_swarm_state()
        
        # 记录历史
        history['iteration'].append(step)
        history['gbest_position'].append(state['gbest_position'])
        history['gbest_fitness'].append(state['gbest_fitness'])
        history['all_positions'].append(state['positions'].copy())
        
        # 计算所有粒子的适应度
        fitness_list = []
        for pos in state['positions']:
            i = module.calculate_current(pos)
            fitness_list.append(pos * i)
        history['all_fitness'].append(fitness_list)
        history['converged'].append(state['converged'])
        
        if state['converged']:
            print(f"PSO收敛于第{step}步")
            break
    
    return history


def main():
    """主函数: PSO MPPT演示"""
    print("=" * 80)
    print("案例11: 粒子群优化MPPT")
    print("Case 11: Particle Swarm Optimization MPPT")
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
    print(f"  Voc = {module.Voc:.2f} V")
    
    # 2. 场景1: PSO寻优过程可视化
    print("\n步骤2: 场景1 - PSO寻优过程")
    print("-" * 80)
    
    pso_algo = ParticleSwarmMPPT(
        n_particles=10,
        v_min=0,
        v_max=module.Voc,
        w=0.7,
        c1=1.5,
        c2=1.5,
        max_iterations=30
    )
    
    print(f"PSO参数:")
    print(f"  粒子数: {pso_algo.n_particles}")
    print(f"  惯性权重w: {pso_algo.w}")
    print(f"  学习因子c1: {pso_algo.c1}, c2: {pso_algo.c2}")
    
    history = simulate_pso_mppt(module, pso_algo, n_iterations=30)
    
    final_v = history['gbest_position'][-1]
    final_p = history['gbest_fitness'][-1]
    efficiency = (final_p / pmpp_true) * 100
    
    print(f"\nPSO寻优结果:")
    print(f"  找到电压: {final_v:.2f} V")
    print(f"  找到功率: {final_p:.2f} W")
    print(f"  跟踪效率: {efficiency:.2f}%")
    print(f"  迭代次数: {len(history['iteration'])}")
    
    # 3. 场景2: PSO vs 传统算法
    print("\n步骤3: 场景2 - PSO vs 传统算法")
    print("-" * 80)
    
    # PSO (重置)
    pso_algo.reset()
    pso_algo.set_pv_module(module)
    
    # P&O
    po_algo = PerturbAndObserve(step_size=1.0, initial_voltage=vmpp_true * 0.7)
    
    # Fuzzy
    fuzzy_algo = FuzzyLogicMPPT(step_size_max=3.0, initial_voltage=vmpp_true * 0.7)
    
    # 模拟对比
    results = {}
    
    for name, algo in [('PSO', pso_algo), ('P&O', po_algo), ('Fuzzy', fuzzy_algo)]:
        if name == 'PSO':
            algo.set_pv_module(module)
        
        controller = MPPTController(algo, v_min=0, v_max=module.Voc)
        
        v_pv = vmpp_true * 0.7
        powers = []
        voltages = []
        
        steps = 30 if name == 'PSO' else 100
        
        for _ in range(steps):
            i_pv = module.calculate_current(v_pv)
            v_ref = controller.step(v_pv, i_pv)
            v_pv = v_pv + 0.5 * (v_ref - v_pv)
            powers.append(v_pv * i_pv)
            voltages.append(v_pv)
        
        perf = controller.evaluate_performance(pmpp_true)
        results[name] = {
            'powers': powers,
            'voltages': voltages,
            'perf': perf
        }
        
        print(f"\n{name}:")
        print(f"  跟踪效率: {perf['efficiency']:.2f}%")
        print(f"  建立时间: {perf['settling_time']} 步")
        print(f"  稳态振荡: {perf['oscillation']:.3f} W")
    
    # 4. 场景3: 部分遮挡（多峰）测试
    print("\n步骤4: 场景3 - 部分遮挡多峰测试")
    print("-" * 80)
    
    # 创建部分遮挡条件
    shading_pattern = [1000, 1000, 800, 800, 600]  # W/m²
    module_shaded = PVModule(cell, Ns=60, Nb=3, name="遮挡组件")
    
    # 为简化，使用平均光照
    avg_G = np.mean(shading_pattern)
    module_shaded.set_uniform_conditions(T=298.15, G=avg_G)
    
    vmpp_shaded, _, pmpp_shaded = module_shaded.find_mpp()
    
    print(f"遮挡条件:")
    print(f"  遮挡模式: {shading_pattern}")
    print(f"  平均光照: {avg_G:.1f} W/m²")
    print(f"  Pmpp(遮挡): {pmpp_shaded:.2f} W")
    
    # PSO在多峰条件下
    pso_shaded = ParticleSwarmMPPT(
        n_particles=15,  # 增加粒子数
        v_min=0,
        v_max=module_shaded.Voc,
        w=0.7,
        c1=1.5,
        c2=1.5,
        max_iterations=40
    )
    
    pso_shaded.set_pv_module(module_shaded)
    
    for _ in range(40):
        v = pso_shaded.v_ref
        i = module_shaded.calculate_current(v)
        pso_shaded.update(v, i)
        
        if pso_shaded.converged:
            break
    
    final_p_shaded = pso_shaded.gbest_fitness
    eff_shaded = (final_p_shaded / pmpp_shaded) * 100
    
    print(f"\nPSO在遮挡条件下:")
    print(f"  找到功率: {final_p_shaded:.2f} W")
    print(f"  跟踪效率: {eff_shaded:.2f}%")
    
    # 5. 可视化
    print("\n步骤5: 结果可视化")
    print("-" * 80)
    
    fig = plt.figure(figsize=(18, 12))
    
    # 图1: 粒子搜索过程动画（选取几个关键帧）
    ax1 = plt.subplot(3, 3, 1)
    V_curve, P_curve = module.get_pv_curve(300)
    ax1.plot(V_curve, P_curve, 'k-', linewidth=2, alpha=0.5, label='P-V曲线')
    ax1.plot(vmpp_true, pmpp_true, 'r*', markersize=15, label='真实MPP')
    
    # 绘制初始、中间、最终粒子位置
    key_frames = [0, len(history['iteration'])//2, -1]
    colors = ['blue', 'green', 'red']
    labels = ['初始', '中间', '最终']
    
    for idx, (frame, color, label) in enumerate(zip(key_frames, colors, labels)):
        positions = history['all_positions'][frame]
        fitness = history['all_fitness'][frame]
        ax1.scatter(positions, fitness, c=color, s=100, alpha=0.6,
                   label=f'{label}粒子', edgecolors='black', linewidth=1)
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('功率 (W)', fontsize=11)
    ax1.set_title('PSO粒子搜索过程', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 全局最优收敛曲线
    ax2 = plt.subplot(3, 3, 2)
    ax2.plot(history['iteration'], history['gbest_fitness'],
            'b-', linewidth=2, marker='o', markersize=4)
    ax2.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax2.set_xlabel('迭代次数', fontsize=11)
    ax2.set_ylabel('全局最优功率 (W)', fontsize=11)
    ax2.set_title('PSO收敛过程', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 电压收敛曲线
    ax3 = plt.subplot(3, 3, 3)
    ax3.plot(history['iteration'], history['gbest_position'],
            'g-', linewidth=2, marker='s', markersize=4)
    ax3.axhline(y=vmpp_true, color='r', linestyle='--', alpha=0.5, label='真实Vmpp')
    ax3.set_xlabel('迭代次数', fontsize=11)
    ax3.set_ylabel('全局最优电压 (V)', fontsize=11)
    ax3.set_title('电压收敛曲线', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 功率对比（PSO vs P&O vs Fuzzy）
    ax4 = plt.subplot(3, 3, 4)
    
    # 归一化时间轴（PSO 30步，其他100步）
    pso_steps = np.linspace(0, 100, len(results['PSO']['powers']))
    po_steps = np.arange(len(results['P&O']['powers']))
    fuzzy_steps = np.arange(len(results['Fuzzy']['powers']))
    
    ax4.axhline(y=pmpp_true, color='r', linestyle='--', alpha=0.5, label='真实MPP')
    ax4.plot(pso_steps, results['PSO']['powers'],
            'b-', linewidth=2, label='PSO', alpha=0.8)
    ax4.plot(po_steps, results['P&O']['powers'],
            'g-', linewidth=2, label='P&O', alpha=0.8)
    ax4.plot(fuzzy_steps, results['Fuzzy']['powers'],
            'm-', linewidth=2, label='Fuzzy', alpha=0.8)
    
    ax4.set_xlabel('归一化步数', fontsize=11)
    ax4.set_ylabel('功率 (W)', fontsize=11)
    ax4.set_title('算法功率响应对比', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # 图5: 效率对比柱状图
    ax5 = plt.subplot(3, 3, 5)
    algorithms = ['PSO', 'P&O', 'Fuzzy']
    efficiencies = [results[alg]['perf']['efficiency'] for alg in algorithms]
    
    bars = ax5.bar(algorithms, efficiencies,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax5.axhline(y=100, color='r', linestyle='--', alpha=0.5)
    ax5.set_ylabel('跟踪效率 (%)', fontsize=11)
    ax5.set_title('跟踪效率对比', fontsize=12, fontweight='bold')
    ax5.set_ylim([95, 101])
    ax5.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, efficiencies):
        ax5.text(bar.get_x() + bar.get_width()/2, val,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 图6: 建立时间对比
    ax6 = plt.subplot(3, 3, 6)
    settling_times = [results[alg]['perf']['settling_time'] for alg in algorithms]
    
    bars = ax6.bar(algorithms, settling_times,
                   color=['steelblue', 'seagreen', 'coral'], alpha=0.7)
    ax6.set_ylabel('建立时间 (步)', fontsize=11)
    ax6.set_title('建立时间对比', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, settling_times):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{val}', ha='center', va='bottom', fontsize=9)
    
    # 图7: 粒子分布直方图（最终状态）
    ax7 = plt.subplot(3, 3, 7)
    final_positions = history['all_positions'][-1]
    ax7.hist(final_positions, bins=10, color='steelblue', alpha=0.7, edgecolor='black')
    ax7.axvline(x=vmpp_true, color='r', linestyle='--', linewidth=2, label='真实Vmpp')
    ax7.axvline(x=history['gbest_position'][-1], color='g',
               linestyle='--', linewidth=2, label='全局最优')
    ax7.set_xlabel('电压 (V)', fontsize=11)
    ax7.set_ylabel('粒子数量', fontsize=11)
    ax7.set_title('最终粒子分布', fontsize=12, fontweight='bold')
    ax7.legend(fontsize=9)
    ax7.grid(True, alpha=0.3, axis='y')
    
    # 图8: 参数敏感性分析（惯性权重w）
    ax8 = plt.subplot(3, 3, 8)
    w_values = [0.3, 0.5, 0.7, 0.9]
    convergence_speeds = []
    
    for w_test in w_values:
        pso_test = ParticleSwarmMPPT(
            n_particles=10, v_min=0, v_max=module.Voc,
            w=w_test, c1=1.5, c2=1.5, max_iterations=30
        )
        pso_test.set_pv_module(module)
        
        for step in range(30):
            v = pso_test.v_ref
            i = module.calculate_current(v)
            pso_test.update(v, i)
            
            if pso_test.converged:
                convergence_speeds.append(step)
                break
        else:
            convergence_speeds.append(30)
    
    ax8.plot(w_values, convergence_speeds, 'o-',
            linewidth=2, markersize=8, color='steelblue')
    ax8.set_xlabel('惯性权重 w', fontsize=11)
    ax8.set_ylabel('收敛步数', fontsize=11)
    ax8.set_title('参数w敏感性分析', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    # 图9: 性能总结表格
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    summary_data = [
        ['指标', 'PSO', 'P&O', 'Fuzzy'],
        ['跟踪效率', f'{results["PSO"]["perf"]["efficiency"]:.1f}%',
         f'{results["P&O"]["perf"]["efficiency"]:.1f}%',
         f'{results["Fuzzy"]["perf"]["efficiency"]:.1f}%'],
        ['建立时间', f'{results["PSO"]["perf"]["settling_time"]}步',
         f'{results["P&O"]["perf"]["settling_time"]}步',
         f'{results["Fuzzy"]["perf"]["settling_time"]}步'],
        ['稳态振荡', f'{results["PSO"]["perf"]["oscillation"]:.2f}W',
         f'{results["P&O"]["perf"]["oscillation"]:.2f}W',
         f'{results["Fuzzy"]["perf"]["oscillation"]:.2f}W'],
        ['全局搜索', '优秀', '弱', '良好'],
        ['计算复杂度', '高', '低', '中']
    ]
    
    table = ax9.table(cellText=summary_data, cellLoc='center',
                     loc='center', bbox=[0, 0.1, 1, 0.8])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax9.set_title('性能总结对比', fontsize=12, fontweight='bold', pad=20)
    
    plt.suptitle('粒子群优化MPPT - 综合分析', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'pso_mppt_analysis.png'),
                dpi=300, bbox_inches='tight')
    print(f"图表已保存")
    
    # 6. 总结
    print("\n步骤6: 总结")
    print("=" * 80)
    
    print("\nPSO MPPT特点:")
    print("  优点:")
    print("    ✅ 全局搜索能力强")
    print("    ✅ 收敛速度快")
    print("    ✅ 适合多峰优化")
    print("    ✅ 无需梯度信息")
    
    print("\n  缺点:")
    print("    ❌ 计算量较大")
    print("    ❌ 参数敏感")
    print("    ❌ 需要多次功率测量")
    
    print("\n最佳应用场景:")
    print("  ✓ 部分遮挡（多峰）")
    print("  ✓ 快速启动")
    print("  ✓ 精确跟踪")
    
    print("\n" + "=" * 80)
    print("案例11主程序完成！")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
