"""
案例3实验: 光伏组件深入分析
Experiments for Case 3

实验内容:
1. 不同组件配置对比 (36/60/72片)
2. 部分遮挡效应仿真
3. 旁路二极管作用分析
4. 温度梯度影响
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule


def experiment_1_module_configurations():
    """
    实验1: 不同组件配置对比
    """
    print("\n" + "=" * 80)
    print("实验1: 不同组件配置对比")
    print("=" * 80)
    
    # 创建标准电池
    cell = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    
    # 创建不同配置的组件
    configs = [
        (36, 2, "36片组件 (小型)"),
        (60, 3, "60片组件 (标准)"),
        (72, 3, "72片组件 (大型)"),
        (96, 4, "96片组件 (超大)")
    ]
    
    results = {
        'Ns': [],
        'Voc': [],
        'Isc': [],
        'Vmpp': [],
        'Impp': [],
        'Pmpp': [],
        'FF': []
    }
    
    modules = []
    
    for Ns, Nb, name in configs:
        print(f"\n创建 {name}...")
        module = PVModule(
            cell_model=cell,
            Ns=Ns,
            Nb=Nb,
            name=name
        )
        modules.append(module)
        
        vmpp, impp, pmpp = module.find_mpp()
        FF = pmpp / (module.Voc * module.Isc)
        
        results['Ns'].append(Ns)
        results['Voc'].append(module.Voc)
        results['Isc'].append(module.Isc)
        results['Vmpp'].append(vmpp)
        results['Impp'].append(impp)
        results['Pmpp'].append(pmpp)
        results['FF'].append(FF)
        
        print(f"  Voc={module.Voc:.2f}V, Isc={module.Isc:.3f}A, Pmpp={pmpp:.2f}W, FF={FF:.4f}")
    
    # 创建图表
    fig = plt.figure(figsize=(16, 12))
    
    # 图1: I-V曲线对比
    ax1 = plt.subplot(2, 3, 1)
    colors = ['b', 'g', 'r', 'm']
    for i, module in enumerate(modules):
        V, I = module.get_iv_curve(200)
        ax1.plot(V, I, color=colors[i], linewidth=2, label=configs[i][2])
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('I-V曲线对比')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: P-V曲线对比
    ax2 = plt.subplot(2, 3, 2)
    for i, module in enumerate(modules):
        V, P = module.get_pv_curve(200)
        ax2.plot(V, P, color=colors[i], linewidth=2, label=configs[i][2])
    ax2.set_xlabel('电压 (V)')
    ax2.set_ylabel('功率 (W)')
    ax2.set_title('P-V曲线对比')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: Voc vs Ns
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(results['Ns'], results['Voc'], 'bo-', linewidth=2, markersize=8)
    ax3.set_xlabel('串联电池数 Ns')
    ax3.set_ylabel('开路电压 Voc (V)')
    ax3.set_title('Voc vs Ns (线性关系)')
    ax3.grid(True, alpha=0.3)
    
    # 图4: Pmpp vs Ns
    ax4 = plt.subplot(2, 3, 4)
    ax4.plot(results['Ns'], results['Pmpp'], 'ro-', linewidth=2, markersize=8)
    ax4.set_xlabel('串联电池数 Ns')
    ax4.set_ylabel('最大功率 Pmpp (W)')
    ax4.set_title('Pmpp vs Ns (线性关系)')
    ax4.grid(True, alpha=0.3)
    
    # 图5: FF vs Ns
    ax5 = plt.subplot(2, 3, 5)
    ax5.plot(results['Ns'], results['FF'], 'go-', linewidth=2, markersize=8)
    ax5.set_xlabel('串联电池数 Ns')
    ax5.set_ylabel('填充因子 FF')
    ax5.set_title('FF vs Ns (基本不变)')
    ax5.set_ylim([0.7, 0.85])
    ax5.grid(True, alpha=0.3)
    
    # 图6: 参数表格
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    table_data = [['配置', 'Voc(V)', 'Isc(A)', 'Pmpp(W)', 'FF']]
    for i in range(len(configs)):
        table_data.append([
            f"{results['Ns'][i]}片",
            f"{results['Voc'][i]:.1f}",
            f"{results['Isc'][i]:.2f}",
            f"{results['Pmpp'][i]:.1f}",
            f"{results['FF'][i]:.3f}"
        ])
    
    table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                      colWidths=[0.15, 0.2, 0.2, 0.2, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # 设置表头样式
    for i in range(5):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.suptitle('实验1: 不同组件配置对比', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'exp1_configurations.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 实验1完成")
    print(f"  关键发现: Voc和Pmpp与Ns成正比, FF保持不变")
    
    return fig


def experiment_2_partial_shading():
    """
    实验2: 部分遮挡效应仿真
    """
    print("\n" + "=" * 80)
    print("实验2: 部分遮挡效应仿真")
    print("=" * 80)
    
    # 创建标准电池
    cell = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    
    # 创建60片组件 (3个旁路二极管)
    module = PVModule(
        cell_model=cell,
        Ns=60,
        Nb=3,
        name="60片组件"
    )
    
    # 定义遮挡场景
    scenarios = [
        ("无遮挡", [1000.0] * 60),
        ("1组遮挡50%", [1000.0]*20 + [500.0]*20 + [1000.0]*20),
        ("1组遮挡75%", [1000.0]*20 + [250.0]*20 + [1000.0]*20),
        ("2组遮挡50%", [500.0]*20 + [1000.0]*20 + [500.0]*20),
        ("全部遮挡50%", [500.0] * 60),
    ]
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = ['b', 'g', 'orange', 'r', 'm']
    results = []
    
    for i, (name, irradiances) in enumerate(scenarios):
        print(f"\n测试场景: {name}")
        
        # 设置辐照度
        module.set_cell_irradiance(irradiances)
        
        # 计算曲线
        V, I = module.get_iv_curve(300)
        _, P = module.get_pv_curve(300)
        
        # 找MPP
        vmpp, impp, pmpp = module.find_mpp()
        
        # 计算损失
        P_nominal = 215.0  # 无遮挡额定功率
        loss = (P_nominal - pmpp) / P_nominal * 100
        
        results.append({
            'name': name,
            'pmpp': pmpp,
            'loss': loss
        })
        
        print(f"  Pmpp = {pmpp:.2f} W")
        print(f"  损失 = {loss:.1f}%")
        
        # 绘制曲线
        ax1.plot(V, I, color=colors[i], linewidth=2, label=name)
        ax2.plot(V, P, color=colors[i], linewidth=2, label=name)
    
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('部分遮挡 - I-V曲线')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('电压 (V)')
    ax2.set_ylabel('功率 (W)')
    ax2.set_title('部分遮挡 - P-V曲线')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 功率损失对比
    ax3.bar(range(len(results)), [r['pmpp'] for r in results], 
            color=colors, alpha=0.7)
    ax3.set_xticks(range(len(results)))
    ax3.set_xticklabels([r['name'] for r in results], rotation=15, ha='right')
    ax3.set_ylabel('最大功率 (W)')
    ax3.set_title('不同遮挡场景的功率输出')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 损失百分比
    ax4.bar(range(len(results)), [r['loss'] for r in results],
            color=colors, alpha=0.7)
    ax4.set_xticks(range(len(results)))
    ax4.set_xticklabels([r['name'] for r in results], rotation=15, ha='right')
    ax4.set_ylabel('功率损失 (%)')
    ax4.set_title('遮挡导致的功率损失')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('实验2: 部分遮挡效应分析', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp2_partial_shading.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 实验2完成")
    print(f"  关键发现: 部分遮挡导致功率显著下降, 旁路二极管可减少损失")
    
    return fig


def experiment_3_bypass_diode_effect():
    """
    实验3: 旁路二极管作用分析
    """
    print("\n" + "=" * 80)
    print("实验3: 旁路二极管作用分析")
    print("=" * 80)
    
    # 创建标准电池
    cell = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    
    # 对比不同旁路二极管数量
    configs = [
        (60, 1, "1个旁路二极管"),
        (60, 2, "2个旁路二极管"),
        (60, 3, "3个旁路二极管"),
        (60, 6, "6个旁路二极管"),
    ]
    
    # 遮挡场景: 第1组遮挡75%
    irradiances_shaded = [250.0]*20 + [1000.0]*40
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = ['b', 'g', 'r', 'm']
    results = []
    
    for i, (Ns, Nb, name) in enumerate(configs):
        print(f"\n测试配置: {name}")
        
        module = PVModule(
            cell_model=cell,
            Ns=Ns,
            Nb=Nb,
            name=name
        )
        
        # 无遮挡
        module.set_uniform_conditions(T=298.15, G=1000.0)
        _, P_no_shade = module.get_pv_curve(200)
        pmpp_no_shade = np.max(P_no_shade)
        
        # 有遮挡
        module.set_cell_irradiance(irradiances_shaded)
        V, I = module.get_iv_curve(200)
        _, P = module.get_pv_curve(200)
        vmpp, impp, pmpp = module.find_mpp()
        
        loss = (pmpp_no_shade - pmpp) / pmpp_no_shade * 100
        
        results.append({
            'name': name,
            'Nb': Nb,
            'pmpp': pmpp,
            'loss': loss
        })
        
        print(f"  无遮挡: {pmpp_no_shade:.2f} W")
        print(f"  有遮挡: {pmpp:.2f} W")
        print(f"  损失: {loss:.1f}%")
        
        # 绘制曲线
        ax1.plot(V, I, color=colors[i], linewidth=2, label=name)
        ax2.plot(V, P, color=colors[i], linewidth=2, label=name)
    
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('不同旁路二极管配置 - I-V曲线')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('电压 (V)')
    ax2.set_ylabel('功率 (W)')
    ax2.set_title('不同旁路二极管配置 - P-V曲线')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 旁路二极管数量 vs 功率
    ax3.plot([r['Nb'] for r in results], [r['pmpp'] for r in results],
             'bo-', linewidth=2, markersize=10)
    ax3.set_xlabel('旁路二极管数量')
    ax3.set_ylabel('最大功率 (W)')
    ax3.set_title('旁路二极管数量对功率的影响')
    ax3.grid(True, alpha=0.3)
    
    # 旁路二极管数量 vs 损失
    ax4.plot([r['Nb'] for r in results], [r['loss'] for r in results],
             'ro-', linewidth=2, markersize=10)
    ax4.set_xlabel('旁路二极管数量')
    ax4.set_ylabel('功率损失 (%)')
    ax4.set_title('旁路二极管数量对损失的影响')
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('实验3: 旁路二极管作用分析', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp3_bypass_diode.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 实验3完成")
    print(f"  关键发现: 旁路二极管数量增加可减少遮挡损失, 但成本也增加")
    
    return fig


def experiment_4_temperature_gradient():
    """
    实验4: 温度梯度影响
    """
    print("\n" + "=" * 80)
    print("实验4: 温度梯度影响")
    print("=" * 80)
    
    # 创建标准电池
    cell = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    
    # 创建60片组件
    module = PVModule(
        cell_model=cell,
        Ns=60,
        Nb=3,
        name="60片组件"
    )
    
    # 定义温度场景
    scenarios = [
        ("均温25°C", [298.15] * 60),
        ("均温50°C", [323.15] * 60),
        ("温度梯度10°C", np.linspace(298.15, 308.15, 60)),
        ("温度梯度25°C", np.linspace(298.15, 323.15, 60)),
        ("局部热斑", [298.15]*20 + [348.15]*20 + [298.15]*20),  # 中间20片75°C
    ]
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = ['b', 'orange', 'g', 'r', 'm']
    results = []
    
    for i, (name, temperatures) in enumerate(scenarios):
        print(f"\n测试场景: {name}")
        
        # 设置温度
        module.set_cell_temperature(list(temperatures))
        
        # 计算曲线
        V, I = module.get_iv_curve(200)
        _, P = module.get_pv_curve(200)
        
        # 找MPP
        vmpp, impp, pmpp = module.find_mpp()
        
        results.append({
            'name': name,
            'pmpp': pmpp,
            'T_avg': np.mean(temperatures) - 273.15
        })
        
        print(f"  平均温度 = {np.mean(temperatures)-273.15:.1f}°C")
        print(f"  Pmpp = {pmpp:.2f} W")
        
        # 绘制曲线
        ax1.plot(V, I, color=colors[i], linewidth=2, label=name)
        ax2.plot(V, P, color=colors[i], linewidth=2, label=name)
    
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('温度影响 - I-V曲线')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('电压 (V)')
    ax2.set_ylabel('功率 (W)')
    ax2.set_title('温度影响 - P-V曲线')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 温度 vs 功率
    ax3.plot([r['T_avg'] for r in results], [r['pmpp'] for r in results],
             'ro-', linewidth=2, markersize=10)
    ax3.set_xlabel('平均温度 (°C)')
    ax3.set_ylabel('最大功率 (W)')
    ax3.set_title('平均温度对功率的影响')
    ax3.grid(True, alpha=0.3)
    
    # 结果表格
    ax4.axis('off')
    table_data = [['场景', '平均温度(°C)', 'Pmpp(W)']]
    for r in results:
        table_data.append([
            r['name'],
            f"{r['T_avg']:.1f}",
            f"{r['pmpp']:.1f}"
        ])
    
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                      colWidths=[0.4, 0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    for i in range(3):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.suptitle('实验4: 温度梯度影响分析', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp4_temperature.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 实验4完成")
    print(f"  关键发现: 温度升高导致功率下降, 局部热斑影响显著")
    
    return fig


def run_all_experiments():
    """
    运行所有实验
    """
    print("\n" + "=" * 80)
    print("开始运行案例3的全部实验")
    print("=" * 80)
    
    experiment_1_module_configurations()
    experiment_2_partial_shading()
    experiment_3_bypass_diode_effect()
    experiment_4_temperature_gradient()
    
    print("\n" + "=" * 80)
    print("全部实验完成！")
    print("=" * 80)
    print("\n所有图表已保存至: outputs/目录")
    
    plt.show()


if __name__ == "__main__":
    run_all_experiments()
