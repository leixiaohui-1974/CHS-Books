"""
案例1实验: 光伏电池特性分析实验
Experiments for Case 1

实验内容:
1. I-V曲线仿真
2. 温度影响分析 (25-75°C)
3. 辐照度影响分析 (200-1000 W/m²)
4. 参数敏感性分析
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


def experiment_1_basic_iv_curve():
    """
    实验1: 基础I-V曲线仿真
    """
    print("\n" + "=" * 80)
    print("实验1: 基础I-V曲线仿真")
    print("=" * 80)
    
    # 创建光伏电池
    pv = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0, name="标准电池"
    )
    
    # 获取曲线
    V, I = pv.get_iv_curve(300)
    _, P = pv.get_pv_curve(300)
    
    # 绘图
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. I-V曲线
    ax1.plot(V, I, 'b-', linewidth=2)
    ax1.plot(0, pv.Isc, 'ro', markersize=10, label=f'Isc={pv.Isc:.3f}A')
    ax1.plot(pv.Voc, 0, 'go', markersize=10, label=f'Voc={pv.Voc:.3f}V')
    vmpp, impp, pmpp = pv.find_mpp()
    ax1.plot(vmpp, impp, 'r*', markersize=15, label='MPP')
    ax1.set_xlabel('电压 V (V)')
    ax1.set_ylabel('电流 I (A)')
    ax1.set_title('I-V特性曲线')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. P-V曲线
    ax2.plot(V, P, 'r-', linewidth=2)
    ax2.plot(vmpp, pmpp, 'r*', markersize=15, label=f'Pmpp={pmpp:.3f}W')
    ax2.set_xlabel('电压 V (V)')
    ax2.set_ylabel('功率 P (W)')
    ax2.set_title('P-V特性曲线')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. I-P曲线
    ax3.plot(I, P, 'g-', linewidth=2)
    ax3.plot(impp, pmpp, 'r*', markersize=15, label='MPP')
    ax3.set_xlabel('电流 I (A)')
    ax3.set_ylabel('功率 P (W)')
    ax3.set_title('I-P特性曲线')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. 功率-电压导数 (dP/dV)
    dPdV = np.gradient(P, V)
    ax4.plot(V, dPdV, 'm-', linewidth=2)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax4.plot(vmpp, 0, 'r*', markersize=15, label='dP/dV=0 (MPP)')
    ax4.set_xlabel('电压 V (V)')
    ax4.set_ylabel('dP/dV (W/V)')
    ax4.set_title('功率-电压导数曲线')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'exp1_basic_curves.png'), dpi=300, bbox_inches='tight')
    
    print("✓ I-V, P-V, I-P曲线绘制完成")
    print(f"✓ 最大功率点: Vmpp={vmpp:.4f}V, Impp={impp:.4f}A, Pmpp={pmpp:.4f}W")
    print(f"✓ 图表保存至: outputs/exp1_basic_curves.png")
    
    return fig


def experiment_2_temperature_effect():
    """
    实验2: 温度影响分析 (25-75°C)
    """
    print("\n" + "=" * 80)
    print("实验2: 温度影响分析")
    print("=" * 80)
    
    # 测试温度范围
    temperatures = [25, 35, 45, 55, 65, 75]  # °C
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 存储结果
    results = {'T': [], 'Voc': [], 'Isc': [], 'Pmpp': [], 'Vmpp': [], 'Impp': [], 'FF': []}
    
    # 颜色映射
    colors = plt.cm.coolwarm(np.linspace(0, 1, len(temperatures)))
    
    for i, T_celsius in enumerate(temperatures):
        T_kelvin = T_celsius + 273.15
        
        # 创建电池
        pv = SingleDiodeModel(
            Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
            T=T_kelvin, G=1000.0
        )
        
        # 获取曲线
        V, I = pv.get_iv_curve(200)
        _, P = pv.get_pv_curve(200)
        
        # 找MPP
        vmpp, impp, pmpp = pv.find_mpp()
        FF = pmpp / (pv.Voc * pv.Isc)
        
        # 存储结果
        results['T'].append(T_celsius)
        results['Voc'].append(pv.Voc)
        results['Isc'].append(pv.Isc)
        results['Pmpp'].append(pmpp)
        results['Vmpp'].append(vmpp)
        results['Impp'].append(impp)
        results['FF'].append(FF)
        
        # 绘制I-V曲线
        ax1.plot(V, I, color=colors[i], linewidth=2, label=f'{T_celsius}°C')
        
        # 绘制P-V曲线
        ax2.plot(V, P, color=colors[i], linewidth=2, label=f'{T_celsius}°C')
    
    ax1.set_xlabel('电压 V (V)')
    ax1.set_ylabel('电流 I (A)')
    ax1.set_title('不同温度下的I-V特性')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax2.set_xlabel('电压 V (V)')
    ax2.set_ylabel('功率 P (W)')
    ax2.set_title('不同温度下的P-V特性')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 绘制参数随温度变化
    ax3.plot(results['T'], results['Voc'], 'b-o', label='Voc', linewidth=2)
    ax3_twin = ax3.twinx()
    ax3_twin.plot(results['T'], results['Isc'], 'r-s', label='Isc', linewidth=2)
    ax3.set_xlabel('温度 (°C)')
    ax3.set_ylabel('开路电压 Voc (V)', color='b')
    ax3_twin.set_ylabel('短路电流 Isc (A)', color='r')
    ax3.set_title('Voc和Isc随温度变化')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='y', labelcolor='b')
    ax3_twin.tick_params(axis='y', labelcolor='r')
    
    # 绘制Pmpp和FF随温度变化
    ax4.plot(results['T'], results['Pmpp'], 'g-o', label='Pmpp', linewidth=2)
    ax4_twin = ax4.twinx()
    ax4_twin.plot(results['T'], results['FF'], 'm-s', label='FF', linewidth=2)
    ax4.set_xlabel('温度 (°C)')
    ax4.set_ylabel('最大功率 Pmpp (W)', color='g')
    ax4_twin.set_ylabel('填充因子 FF', color='m')
    ax4.set_title('Pmpp和FF随温度变化')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='y', labelcolor='g')
    ax4_twin.tick_params(axis='y', labelcolor='m')
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp2_temperature_effect.png'), dpi=300, bbox_inches='tight')
    
    # 打印分析
    print("\n温度影响分析结果:")
    print("-" * 60)
    print(f"{'温度(°C)':<10} {'Voc(V)':<10} {'Isc(A)':<10} {'Pmpp(W)':<10} {'FF':<10}")
    print("-" * 60)
    for i in range(len(results['T'])):
        print(f"{results['T'][i]:<10.0f} {results['Voc'][i]:<10.4f} {results['Isc'][i]:<10.4f} "
              f"{results['Pmpp'][i]:<10.4f} {results['FF'][i]:<10.4f}")
    
    # 计算温度系数
    dVoc_dT = (results['Voc'][-1] - results['Voc'][0]) / (results['T'][-1] - results['T'][0])
    dIsc_dT = (results['Isc'][-1] - results['Isc'][0]) / (results['T'][-1] - results['T'][0])
    dPmpp_dT = (results['Pmpp'][-1] - results['Pmpp'][0]) / (results['T'][-1] - results['T'][0])
    
    print(f"\n温度系数:")
    print(f"  dVoc/dT  = {dVoc_dT:.6f} V/°C ({dVoc_dT/results['Voc'][0]*100:.3f}%/°C)")
    print(f"  dIsc/dT  = {dIsc_dT:.6f} A/°C ({dIsc_dT/results['Isc'][0]*100:.3f}%/°C)")
    print(f"  dPmpp/dT = {dPmpp_dT:.6f} W/°C ({dPmpp_dT/results['Pmpp'][0]*100:.3f}%/°C)")
    
    print(f"\n关键发现:")
    print(f"  • 开路电压Voc随温度升高而下降 (负温度系数)")
    print(f"  • 短路电流Isc随温度升高而略微增加 (正温度系数)")
    print(f"  • 最大功率Pmpp随温度升高而下降")
    print(f"  • 温度每升高10°C, 功率下降约{-dPmpp_dT*10/results['Pmpp'][0]*100:.1f}%")
    
    print(f"\n✓ 图表保存至: outputs/exp2_temperature_effect.png")
    
    return fig


def experiment_3_irradiance_effect():
    """
    实验3: 辐照度影响分析 (200-1000 W/m²)
    """
    print("\n" + "=" * 80)
    print("实验3: 辐照度影响分析")
    print("=" * 80)
    
    # 测试辐照度范围
    irradiances = [200, 400, 600, 800, 1000]  # W/m²
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 存储结果
    results = {'G': [], 'Voc': [], 'Isc': [], 'Pmpp': [], 'Vmpp': [], 'Impp': [], 'FF': []}
    
    # 颜色映射
    colors = plt.cm.YlOrRd(np.linspace(0.3, 1, len(irradiances)))
    
    for i, G in enumerate(irradiances):
        # 创建电池
        pv = SingleDiodeModel(
            Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
            T=298.15, G=G
        )
        
        # 获取曲线
        V, I = pv.get_iv_curve(200)
        _, P = pv.get_pv_curve(200)
        
        # 找MPP
        vmpp, impp, pmpp = pv.find_mpp()
        FF = pmpp / (pv.Voc * pv.Isc) if pv.Voc * pv.Isc > 0 else 0
        
        # 存储结果
        results['G'].append(G)
        results['Voc'].append(pv.Voc)
        results['Isc'].append(pv.Isc)
        results['Pmpp'].append(pmpp)
        results['Vmpp'].append(vmpp)
        results['Impp'].append(impp)
        results['FF'].append(FF)
        
        # 绘制I-V曲线
        ax1.plot(V, I, color=colors[i], linewidth=2, label=f'{G}W/m²')
        
        # 绘制P-V曲线
        ax2.plot(V, P, color=colors[i], linewidth=2, label=f'{G}W/m²')
    
    ax1.set_xlabel('电压 V (V)')
    ax1.set_ylabel('电流 I (A)')
    ax1.set_title('不同辐照度下的I-V特性')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax2.set_xlabel('电压 V (V)')
    ax2.set_ylabel('功率 P (W)')
    ax2.set_title('不同辐照度下的P-V特性')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 绘制Isc和Voc随辐照度变化
    ax3.plot(results['G'], results['Isc'], 'b-o', label='Isc', linewidth=2, markersize=8)
    ax3_twin = ax3.twinx()
    ax3_twin.plot(results['G'], results['Voc'], 'r-s', label='Voc', linewidth=2, markersize=8)
    ax3.set_xlabel('辐照度 G (W/m²)')
    ax3.set_ylabel('短路电流 Isc (A)', color='b')
    ax3_twin.set_ylabel('开路电压 Voc (V)', color='r')
    ax3.set_title('Isc和Voc随辐照度变化')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='y', labelcolor='b')
    ax3_twin.tick_params(axis='y', labelcolor='r')
    
    # 绘制Pmpp随辐照度变化
    ax4.plot(results['G'], results['Pmpp'], 'g-o', linewidth=2, markersize=8)
    ax4.set_xlabel('辐照度 G (W/m²)')
    ax4.set_ylabel('最大功率 Pmpp (W)')
    ax4.set_title('Pmpp随辐照度变化')
    ax4.grid(True, alpha=0.3)
    
    # 添加线性拟合
    coeffs = np.polyfit(results['G'], results['Pmpp'], 1)
    fit_line = np.polyval(coeffs, results['G'])
    ax4.plot(results['G'], fit_line, 'r--', label=f'线性拟合: y={coeffs[0]:.4f}x+{coeffs[1]:.3f}')
    ax4.legend()
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp3_irradiance_effect.png'), dpi=300, bbox_inches='tight')
    
    # 打印分析
    print("\n辐照度影响分析结果:")
    print("-" * 60)
    print(f"{'G(W/m²)':<12} {'Voc(V)':<10} {'Isc(A)':<10} {'Pmpp(W)':<10} {'FF':<10}")
    print("-" * 60)
    for i in range(len(results['G'])):
        print(f"{results['G'][i]:<12.0f} {results['Voc'][i]:<10.4f} {results['Isc'][i]:<10.4f} "
              f"{results['Pmpp'][i]:<10.4f} {results['FF'][i]:<10.4f}")
    
    print(f"\n关键发现:")
    print(f"  • 短路电流Isc与辐照度近似线性关系: Isc ∝ G")
    print(f"  • 开路电压Voc随辐照度增加而缓慢增加 (对数关系)")
    print(f"  • 最大功率Pmpp与辐照度近似线性关系")
    print(f"  • 辐照度每降低100W/m², 功率下降约{(results['Pmpp'][0]-results['Pmpp'][-1])/8:.2f}W")
    
    print(f"\n✓ 图表保存至: outputs/exp3_irradiance_effect.png")
    
    return fig


def experiment_4_parameter_sensitivity():
    """
    实验4: 参数敏感性分析
    分析Rs, Rsh, n对性能的影响
    """
    print("\n" + "=" * 80)
    print("实验4: 参数敏感性分析")
    print("=" * 80)
    
    # 创建图表
    fig = plt.figure(figsize=(18, 12))
    
    # 基准参数
    base_params = {'Isc': 8.0, 'Voc': 0.6, 'Imp': 7.5, 'Vmp': 0.48, 'T': 298.15, 'G': 1000.0}
    
    # === 子图1-2: Rs的影响 ===
    ax1 = plt.subplot(3, 3, 1)
    ax2 = plt.subplot(3, 3, 2)
    
    Rs_values = [0.001, 0.005, 0.01, 0.02, 0.05]
    colors = plt.cm.Blues(np.linspace(0.4, 1, len(Rs_values)))
    
    pmpp_rs = []
    for i, Rs in enumerate(Rs_values):
        pv = SingleDiodeModel(**base_params, Rs=Rs, Rsh=1000.0, n=1.2)
        V, I = pv.get_iv_curve(200)
        _, P = pv.get_pv_curve(200)
        vmpp, impp, pmpp = pv.find_mpp()
        pmpp_rs.append(pmpp)
        
        ax1.plot(V, I, color=colors[i], linewidth=2, label=f'Rs={Rs*1000:.0f}mΩ')
        ax2.plot(V, P, color=colors[i], linewidth=2, label=f'Rs={Rs*1000:.0f}mΩ')
    
    ax1.set_xlabel('电压 V (V)')
    ax1.set_ylabel('电流 I (A)')
    ax1.set_title('串联电阻Rs对I-V的影响')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)
    
    ax2.set_xlabel('电压 V (V)')
    ax2.set_ylabel('功率 P (W)')
    ax2.set_title('串联电阻Rs对P-V的影响')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)
    
    ax3 = plt.subplot(3, 3, 3)
    ax3.plot([r*1000 for r in Rs_values], pmpp_rs, 'bo-', linewidth=2, markersize=8)
    ax3.set_xlabel('串联电阻 Rs (mΩ)')
    ax3.set_ylabel('最大功率 Pmpp (W)')
    ax3.set_title('Pmpp随Rs变化')
    ax3.grid(True, alpha=0.3)
    
    # === 子图4-5: Rsh的影响 ===
    ax4 = plt.subplot(3, 3, 4)
    ax5 = plt.subplot(3, 3, 5)
    
    Rsh_values = [100, 500, 1000, 5000, 10000]
    colors = plt.cm.Greens(np.linspace(0.4, 1, len(Rsh_values)))
    
    pmpp_rsh = []
    for i, Rsh in enumerate(Rsh_values):
        pv = SingleDiodeModel(**base_params, Rs=0.005, Rsh=Rsh, n=1.2)
        V, I = pv.get_iv_curve(200)
        _, P = pv.get_pv_curve(200)
        vmpp, impp, pmpp = pv.find_mpp()
        pmpp_rsh.append(pmpp)
        
        ax4.plot(V, I, color=colors[i], linewidth=2, label=f'Rsh={Rsh}Ω')
        ax5.plot(V, P, color=colors[i], linewidth=2, label=f'Rsh={Rsh}Ω')
    
    ax4.set_xlabel('电压 V (V)')
    ax4.set_ylabel('电流 I (A)')
    ax4.set_title('并联电阻Rsh对I-V的影响')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=8)
    
    ax5.set_xlabel('电压 V (V)')
    ax5.set_ylabel('功率 P (W)')
    ax5.set_title('并联电阻Rsh对P-V的影响')
    ax5.grid(True, alpha=0.3)
    ax5.legend(fontsize=8)
    
    ax6 = plt.subplot(3, 3, 6)
    ax6.semilogx(Rsh_values, pmpp_rsh, 'go-', linewidth=2, markersize=8)
    ax6.set_xlabel('并联电阻 Rsh (Ω)')
    ax6.set_ylabel('最大功率 Pmpp (W)')
    ax6.set_title('Pmpp随Rsh变化')
    ax6.grid(True, alpha=0.3)
    
    # === 子图7-8: n的影响 ===
    ax7 = plt.subplot(3, 3, 7)
    ax8 = plt.subplot(3, 3, 8)
    
    n_values = [1.0, 1.1, 1.2, 1.3, 1.5]
    colors = plt.cm.Reds(np.linspace(0.4, 1, len(n_values)))
    
    pmpp_n = []
    for i, n in enumerate(n_values):
        pv = SingleDiodeModel(**base_params, Rs=0.005, Rsh=1000.0, n=n)
        V, I = pv.get_iv_curve(200)
        _, P = pv.get_pv_curve(200)
        vmpp, impp, pmpp = pv.find_mpp()
        pmpp_n.append(pmpp)
        
        ax7.plot(V, I, color=colors[i], linewidth=2, label=f'n={n:.1f}')
        ax8.plot(V, P, color=colors[i], linewidth=2, label=f'n={n:.1f}')
    
    ax7.set_xlabel('电压 V (V)')
    ax7.set_ylabel('电流 I (A)')
    ax7.set_title('理想因子n对I-V的影响')
    ax7.grid(True, alpha=0.3)
    ax7.legend(fontsize=8)
    
    ax8.set_xlabel('电压 V (V)')
    ax8.set_ylabel('功率 P (W)')
    ax8.set_title('理想因子n对P-V的影响')
    ax8.grid(True, alpha=0.3)
    ax8.legend(fontsize=8)
    
    ax9 = plt.subplot(3, 3, 9)
    ax9.plot(n_values, pmpp_n, 'ro-', linewidth=2, markersize=8)
    ax9.set_xlabel('理想因子 n')
    ax9.set_ylabel('最大功率 Pmpp (W)')
    ax9.set_title('Pmpp随n变化')
    ax9.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp4_parameter_sensitivity.png'), dpi=300, bbox_inches='tight')
    
    print("\n参数敏感性分析结果:")
    print("\n1. 串联电阻Rs的影响:")
    print("   • Rs增加 → Vmpp下降, Impp下降, Pmpp显著下降")
    print("   • Rs对填充因子FF影响很大")
    print("   • 实际电池应保持Rs尽可能小 (<10mΩ)")
    
    print("\n2. 并联电阻Rsh的影响:")
    print("   • Rsh减小 → 低压区电流下降更快")
    print("   • Rsh<1000Ω时对Pmpp有明显影响")
    print("   • Rsh应尽可能大 (>1000Ω)")
    
    print("\n3. 理想因子n的影响:")
    print("   • n增加 → 曲线"膝部"变圆润")
    print("   • n增加 → Pmpp下降")
    print("   • 单晶硅n≈1.0-1.2, 多晶硅n≈1.2-1.3")
    
    print(f"\n✓ 图表保存至: outputs/exp4_parameter_sensitivity.png")
    
    return fig


def run_all_experiments():
    """
    运行所有实验
    """
    print("\n" + "=" * 80)
    print("开始运行案例1的全部实验")
    print("=" * 80)
    
    # 运行各实验
    experiment_1_basic_iv_curve()
    experiment_2_temperature_effect()
    experiment_3_irradiance_effect()
    experiment_4_parameter_sensitivity()
    
    print("\n" + "=" * 80)
    print("全部实验完成！")
    print("=" * 80)
    print("\n所有图表已保存至: outputs/目录")
    
    # 显示所有图表
    plt.show()


if __name__ == "__main__":
    run_all_experiments()
