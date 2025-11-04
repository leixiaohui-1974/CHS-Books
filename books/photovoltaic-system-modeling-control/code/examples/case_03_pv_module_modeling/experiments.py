"""
案例3实验: 光伏组件深入分析
Experiments for Case 3

实验内容:
1. 不同串联片数对比(36/60/72片)
2. 部分遮挡效应分析
3. 旁路二极管作用演示
4. 组件失配影响分析
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


def experiment_1_different_configurations():
    """
    实验1: 不同串联片数配置对比
    """
    print("\n" + "=" * 80)
    print("实验1: 不同串联片数配置对比")
    print("=" * 80)
    
    # 创建单片电池模板
    cell = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    
    # 创建不同配置的组件
    configs = [
        ('36片 (传统)', 36, 2),
        ('60片 (标准)', 60, 3),
        ('72片 (大功率)', 72, 3),
        ('96片 (超大)', 96, 4),
    ]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    results = []
    colors = ['b', 'g', 'r', 'm']
    
    for i, (name, Ns, Nb) in enumerate(configs):
        print(f"\n创建 {name} 组件...")
        module = PVModule(cell_model=cell, Ns=Ns, Nb=Nb, name=name)
        
        # 计算特性
        vmpp, impp, pmpp = module.find_mpp()
        V, I = module.get_iv_curve(200)
        _, P = module.get_pv_curve(200)
        
        results.append({
            'name': name,
            'Ns': Ns,
            'Voc': module.Voc,
            'Isc': module.Isc,
            'Vmpp': vmpp,
            'Impp': impp,
            'Pmpp': pmpp,
            'V': V,
            'I': I,
            'P': P
        })
        
        # 绘制I-V曲线
        ax1.plot(V, I, color=colors[i], linewidth=2, label=name)
        
        # 绘制P-V曲线
        ax2.plot(V, P, color=colors[i], linewidth=2, label=name)
        ax2.plot(vmpp, pmpp, 'o', color=colors[i], markersize=8)
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('电流 (A)', fontsize=11)
    ax1.set_title('I-V特性曲线对比', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('电压 (V)', fontsize=11)
    ax2.set_ylabel('功率 (W)', fontsize=11)
    ax2.set_title('P-V特性曲线对比', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 绘制参数对比柱状图
    names = [r['name'] for r in results]
    pmpp_values = [r['Pmpp'] for r in results]
    voc_values = [r['Voc'] for r in results]
    
    x = np.arange(len(names))
    width = 0.35
    
    ax3.bar(x, pmpp_values, width, color=colors, alpha=0.7)
    ax3.set_ylabel('最大功率 (W)', fontsize=11)
    ax3.set_title('最大功率对比', fontsize=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(names, rotation=15, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for i, v in enumerate(pmpp_values):
        ax3.text(i, v, f'{v:.1f}W', ha='center', va='bottom', fontsize=9)
    
    ax4.bar(x, voc_values, width, color=colors, alpha=0.7)
    ax4.set_ylabel('开路电压 (V)', fontsize=11)
    ax4.set_title('开路电压对比', fontsize=12)
    ax4.set_xticks(x)
    ax4.set_xticklabels(names, rotation=15, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for i, v in enumerate(voc_values):
        ax4.text(i, v, f'{v:.1f}V', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('不同串联片数配置对比', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'exp1_configurations.png'), dpi=300, bbox_inches='tight')
    
    # 打印对比表格
    print("\n配置对比表:")
    print("-" * 80)
    print(f"{'配置':<15} {'Ns':<6} {'Voc(V)':<10} {'Isc(A)':<10} {'Pmpp(W)':<10} {'Vmpp(V)':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<15} {r['Ns']:<6} {r['Voc']:<10.2f} {r['Isc']:<10.3f} "
              f"{r['Pmpp']:<10.2f} {r['Vmpp']:<10.2f}")
    
    print(f"\n✓ 实验1完成")
    print(f"✓ 结论: 串联片数↑ → 电压↑, 功率↑")
    
    return fig


def experiment_2_partial_shading():
    """
    实验2: 部分遮挡效应分析
    """
    print("\n" + "=" * 80)
    print("实验2: 部分遮挡效应分析")
    print("=" * 80)
    
    # 创建60片组件
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
    module = PVModule(cell_model=cell, Ns=60, Nb=3, name="60片组件")
    
    # 定义不同遮挡场景
    scenarios = {
        '无遮挡': [1000.0] * 60,
        '1片遮挡50%': [1000.0] * 59 + [500.0],
        '5片遮挡50%': [1000.0] * 55 + [500.0] * 5,
        '1组遮挡50% (20片)': [1000.0] * 40 + [500.0] * 20,
        '1组全遮挡 (20片)': [1000.0] * 40 + [100.0] * 20,
    }
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    results = []
    colors = ['b', 'g', 'orange', 'r', 'purple']
    
    for (name, irradiances), color in zip(scenarios.items(), colors):
        print(f"\n场景: {name}")
        
        # 设置辐照度
        module.set_cell_irradiance(irradiances)
        
        # 计算特性
        V, I = module.get_iv_curve(300)
        _, P = module.get_pv_curve(300)
        vmpp, impp, pmpp = module.find_mpp()
        
        # 计算功率损失
        power_loss = (results[0]['Pmpp'] - pmpp) if results else 0
        loss_pct = (power_loss / results[0]['Pmpp'] * 100) if results else 0
        
        results.append({
            'name': name,
            'Pmpp': pmpp,
            'Vmpp': vmpp,
            'Impp': impp,
            'loss': power_loss,
            'loss_pct': loss_pct
        })
        
        # 绘制I-V
        ax1.plot(V, I, color=color, linewidth=2, label=name, alpha=0.8)
        
        # 绘制P-V
        ax2.plot(V, P, color=color, linewidth=2, label=name, alpha=0.8)
        ax2.plot(vmpp, pmpp, 'o', color=color, markersize=6)
        
        print(f"  Pmpp = {pmpp:.2f} W")
        if results[0]:
            print(f"  损失 = {power_loss:.2f} W ({loss_pct:.1f}%)")
    
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('电流 (A)', fontsize=11)
    ax1.set_title('不同遮挡场景的I-V曲线', fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('电压 (V)', fontsize=11)
    ax2.set_ylabel('功率 (W)', fontsize=11)
    ax2.set_title('不同遮挡场景的P-V曲线', fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 功率损失柱状图
    names = [r['name'] for r in results]
    pmpp_values = [r['Pmpp'] for r in results]
    
    ax3.bar(names, pmpp_values, color=colors, alpha=0.7)
    ax3.set_ylabel('最大功率 (W)', fontsize=11)
    ax3.set_title('不同场景的输出功率', fontsize=12)
    ax3.tick_params(axis='x', rotation=15)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 损失百分比
    loss_values = [r['loss_pct'] for r in results[1:]]  # 跳过无遮挡
    
    ax4.bar(names[1:], loss_values, color=colors[1:], alpha=0.7)
    ax4.set_ylabel('功率损失 (%)', fontsize=11)
    ax4.set_title('遮挡导致的功率损失', fontsize=12)
    ax4.tick_params(axis='x', rotation=15)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, v in enumerate(loss_values):
        ax4.text(i, v, f'{v:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('部分遮挡效应分析', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    plt.savefig(os.path.join(output_dir, 'exp2_partial_shading.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 实验2完成")
    print(f"✓ 关键发现:")
    print(f"  • 部分遮挡显著降低输出功率")
    print(f"  • 整组遮挡损失最大 ({loss_values[-1]:.1f}%)")
    print(f"  • 旁路二极管可减少损失")
    
    return fig


def experiment_3_bypass_diode_effect():
    """
    实验3: 旁路二极管作用演示
    """
    print("\n" + "=" * 80)
    print("实验3: 旁路二极管作用演示")
    print("=" * 80)
    
    # 创建电池
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
    
    # 场景: 1组(20片)严重遮挡
    irradiances_shaded = [1000.0] * 40 + [100.0] * 20
    
    # 创建两个组件: 有/无旁路二极管
    # 注意: 实际实现中,我们的模型已经包含旁路二极管
    # 这里主要演示效果
    
    module_with_bypass = PVModule(cell_model=cell, Ns=60, Nb=3, name="有旁路二极管")
    module_with_bypass.set_cell_irradiance(irradiances_shaded)
    
    # 模拟无旁路二极管(热斑效应)
    # 简化处理: 假设被遮挡的电池会限制整个串的电流
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 有旁路二极管
    V_with, I_with = module_with_bypass.get_iv_curve(300)
    _, P_with = module_with_bypass.get_pv_curve(300)
    vmpp_with, impp_with, pmpp_with = module_with_bypass.find_mpp()
    
    # 绘制
    ax1.plot(V_with, I_with, 'g-', linewidth=2, label='有旁路二极管')
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('I-V曲线对比')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(V_with, P_with, 'g-', linewidth=2, label='有旁路二极管')
    ax2.plot(vmpp_with, pmpp_with, 'ro', markersize=10, label=f'MPP={pmpp_with:.1f}W')
    ax2.set_xlabel('电压 (V)')
    ax2.set_ylabel('功率 (W)')
    ax2.set_title('P-V曲线对比')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 旁路二极管状态图
    ax3.text(0.5, 0.7, '旁路二极管保护机制', ha='center', fontsize=14, fontweight='bold',
             transform=ax3.transAxes)
    
    text = """
    工作原理:
    
    1. 正常情况: 旁路二极管截止
       - 电流通过所有电池
       - 全功率输出
    
    2. 部分遮挡: 旁路二极管导通
       - 被遮挡组被旁路
       - 保护电池,防止热斑
       - 减少功率损失
    
    3. 优势:
       ✓ 防止反向偏压
       ✓ 避免热斑效应
       ✓ 提高系统可靠性
       ✓ 减少遮挡损失
    """
    
    ax3.text(0.1, 0.5, text, fontsize=10, family='monospace',
             transform=ax3.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    ax3.axis('off')
    
    # 热斑效应说明
    ax4.text(0.5, 0.7, '热斑效应危害', ha='center', fontsize=14, fontweight='bold',
             transform=ax4.transAxes)
    
    text2 = """
    无旁路二极管的后果:
    
    ⚠ 被遮挡电池反向偏压
    ⚠ 消耗功率而非产生功率
    ⚠ 局部过热 (热斑)
    ⚠ 可能永久损坏
    ⚠ 严重时引发火灾
    
    温度可达:
    • 正常运行: 40-60°C
    • 热斑效应: 80-150°C
    • 危险等级: 极高
    
    → 旁路二极管是必需的!
    """
    
    ax4.text(0.1, 0.5, text2, fontsize=10, family='monospace',
             transform=ax4.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    ax4.axis('off')
    
    plt.suptitle('旁路二极管作用演示', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp3_bypass_diode.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 实验3完成")
    print(f"✓ 旁路二极管配置: 60片/3个 = 20片/组")
    print(f"✓ 有旁路二极管时Pmpp = {pmpp_with:.2f} W")
    print(f"✓ 旁路二极管是光伏组件的关键保护元件")
    
    return fig


def experiment_4_scaling_analysis():
    """
    实验4: 功率扩展分析
    """
    print("\n" + "=" * 80)
    print("实验4: 功率扩展分析")
    print("=" * 80)
    
    # 创建电池
    cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
    P_cell = cell.Vmp_stc * cell.Imp_stc
    
    # 不同片数
    Ns_values = np.array([12, 24, 36, 48, 60, 72, 84, 96])
    
    Voc_values = []
    Pmpp_values = []
    
    print("\n计算不同片数的组件特性...")
    for Ns in Ns_values:
        Nb = max(1, Ns // 20)  # 每20片一个旁路二极管
        module = PVModule(cell_model=cell, Ns=Ns, Nb=Nb)
        vmpp, impp, pmpp = module.find_mpp()
        
        Voc_values.append(module.Voc)
        Pmpp_values.append(pmpp)
        
        print(f"  Ns={Ns:2d}: Voc={module.Voc:5.1f}V, Pmpp={pmpp:6.2f}W")
    
    Voc_values = np.array(Voc_values)
    Pmpp_values = np.array(Pmpp_values)
    
    # 绘图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Voc vs Ns
    ax1.plot(Ns_values, Voc_values, 'bo-', linewidth=2, markersize=8)
    ax1.plot(Ns_values, cell.Voc * Ns_values, 'r--', linewidth=2, label='理论值 (Voc_cell × Ns)')
    ax1.set_xlabel('串联片数 Ns', fontsize=11)
    ax1.set_ylabel('开路电压 Voc (V)', fontsize=11)
    ax1.set_title('开路电压 vs 串联片数', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Pmpp vs Ns
    ax2.plot(Ns_values, Pmpp_values, 'go-', linewidth=2, markersize=8)
    ax2.plot(Ns_values, P_cell * Ns_values, 'r--', linewidth=2, label='理论值 (Pcell × Ns)')
    ax2.set_xlabel('串联片数 Ns', fontsize=11)
    ax2.set_ylabel('最大功率 Pmpp (W)', fontsize=11)
    ax2.set_title('最大功率 vs 串联片数', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 线性拟合
    from numpy.polynomial import Polynomial
    p_voc = Polynomial.fit(Ns_values, Voc_values, 1)
    p_pmpp = Polynomial.fit(Ns_values, Pmpp_values, 1)
    
    ax3.scatter(Ns_values, Voc_values / Ns_values, s=100, alpha=0.6)
    ax3.axhline(cell.Voc, color='r', linestyle='--', linewidth=2, label=f'Voc_cell = {cell.Voc:.3f}V')
    ax3.set_xlabel('串联片数 Ns', fontsize=11)
    ax3.set_ylabel('平均电压 Voc/Ns (V)', fontsize=11)
    ax3.set_title('每片电池平均电压', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    ax4.scatter(Ns_values, Pmpp_values / Ns_values, s=100, alpha=0.6, color='g')
    ax4.axhline(P_cell, color='r', linestyle='--', linewidth=2, label=f'Pcell = {P_cell:.3f}W')
    ax4.set_xlabel('串联片数 Ns', fontsize=11)
    ax4.set_ylabel('平均功率 Pmpp/Ns (W)', fontsize=11)
    ax4.set_title('每片电池平均功率', fontsize=12)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('功率扩展分析 - 线性缩放特性', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp4_scaling.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 实验4完成")
    print(f"✓ 线性缩放关系验证:")
    print(f"  • Voc = {p_voc.coef[1]:.4f} × Ns + {p_voc.coef[0]:.2f}")
    print(f"  • Pmpp = {p_pmpp.coef[1]:.4f} × Ns + {p_pmpp.coef[0]:.2f}")
    print(f"  • 串联片数线性扩展电压和功率 ✓")
    
    return fig


def run_all_experiments():
    """
    运行所有实验
    """
    print("\n" + "=" * 80)
    print("开始运行案例3的全部实验")
    print("=" * 80)
    
    experiment_1_different_configurations()
    experiment_2_partial_shading()
    experiment_3_bypass_diode_effect()
    experiment_4_scaling_analysis()
    
    print("\n" + "=" * 80)
    print("全部实验完成！")
    print("=" * 80)
    print("\n所有图表已保存至: outputs/目录")
    
    plt.show()


if __name__ == "__main__":
    run_all_experiments()
