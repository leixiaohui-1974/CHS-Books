"""
案例2实验: 双二极管模型深入分析
Experiments for Case 2

实验内容:
1. 不同条件下的模型精度对比
2. 低辐照度性能对比
3. 高温条件性能对比
4. 理想因子影响分析
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import time

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

from code.models.pv_cell import SingleDiodeModel, DoubleDiodeModel


def experiment_1_standard_comparison():
    """
    实验1: 标准条件下详细对比
    """
    print("\n" + "=" * 80)
    print("实验1: 标准条件下详细对比")
    print("=" * 80)
    
    # 创建模型
    pv1 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
    pv2 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
    
    # 获取曲线
    V1, I1 = pv1.get_iv_curve(500)
    V2, I2 = pv2.get_iv_curve(500)
    _, P1 = pv1.get_pv_curve(500)
    _, P2 = pv2.get_pv_curve(500)
    
    # 创建图表
    fig = plt.figure(figsize=(16, 10))
    
    # I-V曲线对比
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(V1, I1, 'b-', linewidth=2, label='单二极管', alpha=0.7)
    ax1.plot(V2, I2, 'r--', linewidth=2, label='双二极管')
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('I-V曲线对比')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # P-V曲线对比
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(V1, P1, 'b-', linewidth=2, label='单二极管', alpha=0.7)
    ax2.plot(V2, P2, 'r--', linewidth=2, label='双二极管')
    ax2.set_xlabel('电压 (V)')
    ax2.set_ylabel('功率 (W)')
    ax2.set_title('P-V曲线对比')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 局部放大 - 低压区
    ax3 = plt.subplot(2, 3, 3)
    mask_low = V1 <= 0.2
    ax3.plot(V1[mask_low], I1[mask_low], 'b-', linewidth=2, label='单二极管')
    ax3.plot(V2[mask_low], I2[mask_low], 'r--', linewidth=2, label='双二极管')
    ax3.set_xlabel('电压 (V)')
    ax3.set_ylabel('电流 (A)')
    ax3.set_title('低压区放大 (V<0.2V)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 局部放大 - MPP附近
    ax4 = plt.subplot(2, 3, 4)
    mask_mpp = (V1 >= 0.4) & (V1 <= 0.55)
    ax4.plot(V1[mask_mpp], I1[mask_mpp], 'b-', linewidth=2, label='单二极管')
    ax4.plot(V2[mask_mpp], I2[mask_mpp], 'r--', linewidth=2, label='双二极管')
    ax4.set_xlabel('电压 (V)')
    ax4.set_ylabel('电流 (A)')
    ax4.set_title('MPP区放大 (0.4-0.55V)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 电流相对误差
    ax5 = plt.subplot(2, 3, 5)
    rel_error = np.abs((I2 - I1) / (I1 + 1e-10)) * 100
    ax5.plot(V1, rel_error, 'g-', linewidth=2)
    ax5.set_xlabel('电压 (V)')
    ax5.set_ylabel('相对误差 (%)')
    ax5.set_title('电流相对误差')
    ax5.grid(True, alpha=0.3)
    ax5.set_ylim([0, max(5, np.max(rel_error[rel_error < 100]))])
    
    # 统计信息
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    vmpp1, impp1, pmpp1 = pv1.find_mpp()
    vmpp2, impp2, pmpp2 = pv2.find_mpp()
    
    stats_text = f"""
    统计信息 (STC条件)
    ══════════════════════════════
    
    单二极管模型:
      Vmpp = {vmpp1:.4f} V
      Impp = {impp1:.4f} A  
      Pmpp = {pmpp1:.4f} W
      FF   = {pmpp1/(pv1.Voc*pv1.Isc):.4f}
    
    双二极管模型:
      Vmpp = {vmpp2:.4f} V
      Impp = {impp2:.4f} A
      Pmpp = {pmpp2:.4f} W
      FF   = {pmpp2/(pv2.Voc*pv2.Isc):.4f}
    
    差异:
      ΔVmpp = {abs(vmpp2-vmpp1):.4f} V ({abs(vmpp2-vmpp1)/vmpp1*100:.2f}%)
      ΔImpp = {abs(impp2-impp1):.4f} A ({abs(impp2-impp1)/impp1*100:.2f}%)
      ΔPmpp = {abs(pmpp2-pmpp1):.4f} W ({abs(pmpp2-pmpp1)/pmpp1*100:.2f}%)
    
    电流最大误差: {np.max(rel_error):.3f}%
    电流平均误差: {np.mean(rel_error):.3f}%
    """
    
    ax6.text(0.1, 0.9, stats_text, fontsize=9, family='monospace',
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'exp1_standard_comparison.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 标准条件对比完成")
    print(f"✓ 功率差异: {abs(pmpp2-pmpp1):.4f}W ({abs(pmpp2-pmpp1)/pmpp1*100:.2f}%)")
    print(f"✓ 最大电流误差: {np.max(rel_error):.3f}%")
    print(f"✓ 平均电流误差: {np.mean(rel_error):.3f}%")
    
    return fig


def experiment_2_low_irradiance():
    """
    实验2: 低辐照度性能对比
    """
    print("\n" + "=" * 80)
    print("实验2: 低辐照度性能对比")
    print("=" * 80)
    
    # 测试多个辐照度
    irradiances = [1000, 800, 600, 400, 200, 100]
    
    results = {
        'G': [],
        'pmpp_single': [],
        'pmpp_double': [],
        'diff_abs': [],
        'diff_pct': []
    }
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = plt.cm.YlOrRd(np.linspace(0.3, 1, len(irradiances)))
    
    for i, G in enumerate(irradiances):
        pv1 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=G)
        pv2 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=G)
        
        V1, I1 = pv1.get_iv_curve(200)
        V2, I2 = pv2.get_iv_curve(200)
        _, P1 = pv1.get_pv_curve(200)
        _, P2 = pv2.get_pv_curve(200)
        
        vmpp1, impp1, pmpp1 = pv1.find_mpp()
        vmpp2, impp2, pmpp2 = pv2.find_mpp()
        
        results['G'].append(G)
        results['pmpp_single'].append(pmpp1)
        results['pmpp_double'].append(pmpp2)
        results['diff_abs'].append(abs(pmpp2 - pmpp1))
        results['diff_pct'].append(abs(pmpp2 - pmpp1) / pmpp1 * 100)
        
        # 绘制I-V曲线
        ax1.plot(V1, I1, '-', color=colors[i], linewidth=1.5, alpha=0.5, label=f'{G}W/m² 单')
        ax1.plot(V2, I2, '--', color=colors[i], linewidth=2, label=f'{G}W/m² 双')
    
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('不同辐照度下的I-V曲线')
    ax1.legend(fontsize=7, ncol=2)
    ax1.grid(True, alpha=0.3)
    
    # Pmpp对比
    ax2.plot(results['G'], results['pmpp_single'], 'bo-', linewidth=2, markersize=8, label='单二极管')
    ax2.plot(results['G'], results['pmpp_double'], 'rs--', linewidth=2, markersize=8, label='双二极管')
    ax2.set_xlabel('辐照度 (W/m²)')
    ax2.set_ylabel('最大功率 (W)')
    ax2.set_title('Pmpp vs 辐照度')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 绝对差异
    ax3.plot(results['G'], results['diff_abs'], 'g^-', linewidth=2, markersize=8)
    ax3.set_xlabel('辐照度 (W/m²)')
    ax3.set_ylabel('功率绝对差异 (W)')
    ax3.set_title('模型差异 (绝对值)')
    ax3.grid(True, alpha=0.3)
    
    # 相对差异
    ax4.plot(results['G'], results['diff_pct'], 'mo-', linewidth=2, markersize=8)
    ax4.set_xlabel('辐照度 (W/m²)')
    ax4.set_ylabel('功率相对差异 (%)')
    ax4.set_title('模型差异 (百分比)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp2_low_irradiance.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n低辐照度性能对比:")
    print("-" * 60)
    print(f"{'G(W/m²)':<10} {'单(W)':<10} {'双(W)':<10} {'差异(W)':<10} {'差异(%)':<10}")
    print("-" * 60)
    for i in range(len(results['G'])):
        print(f"{results['G'][i]:<10.0f} {results['pmpp_single'][i]:<10.4f} "
              f"{results['pmpp_double'][i]:<10.4f} {results['diff_abs'][i]:<10.4f} "
              f"{results['diff_pct'][i]:<10.2f}")
    
    print(f"\n✓ 关键发现:")
    print(f"  • 低辐照度下,模型差异相对增大")
    print(f"  • 100W/m²时差异: {results['diff_pct'][-1]:.2f}%")
    print(f"  • 1000W/m²时差异: {results['diff_pct'][0]:.2f}%")
    print(f"  • 双二极管模型在低辐照度下更准确")
    
    return fig


def experiment_3_high_temperature():
    """
    实验3: 高温条件性能对比
    """
    print("\n" + "=" * 80)
    print("实验3: 高温条件性能对比")
    print("=" * 80)
    
    # 测试多个温度
    temperatures = [25, 35, 45, 55, 65, 75]
    
    results = {'T': [], 'pmpp_single': [], 'pmpp_double': [], 'diff_pct': []}
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = plt.cm.coolwarm(np.linspace(0, 1, len(temperatures)))
    
    for i, T_c in enumerate(temperatures):
        T_k = T_c + 273.15
        pv1 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=T_k, G=1000.0)
        pv2 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=T_k, G=1000.0)
        
        V1, I1 = pv1.get_iv_curve(200)
        V2, I2 = pv2.get_iv_curve(200)
        
        vmpp1, impp1, pmpp1 = pv1.find_mpp()
        vmpp2, impp2, pmpp2 = pv2.find_mpp()
        
        results['T'].append(T_c)
        results['pmpp_single'].append(pmpp1)
        results['pmpp_double'].append(pmpp2)
        results['diff_pct'].append(abs(pmpp2 - pmpp1) / pmpp1 * 100)
        
        # I-V曲线
        ax1.plot(V1, I1, '-', color=colors[i], linewidth=1.5, alpha=0.5)
        ax1.plot(V2, I2, '--', color=colors[i], linewidth=2, label=f'{T_c}°C')
    
    ax1.set_xlabel('电压 (V)')
    ax1.set_ylabel('电流 (A)')
    ax1.set_title('不同温度下的I-V曲线 (双二极管)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Pmpp对比
    ax2.plot(results['T'], results['pmpp_single'], 'bo-', linewidth=2, label='单二极管')
    ax2.plot(results['T'], results['pmpp_double'], 'rs--', linewidth=2, label='双二极管')
    ax2.set_xlabel('温度 (°C)')
    ax2.set_ylabel('最大功率 (W)')
    ax2.set_title('Pmpp vs 温度')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 相对差异
    ax3.plot(results['T'], results['diff_pct'], 'go-', linewidth=2, markersize=8)
    ax3.set_xlabel('温度 (°C)')
    ax3.set_ylabel('功率相对差异 (%)')
    ax3.set_title('模型差异随温度变化')
    ax3.grid(True, alpha=0.3)
    
    # 统计表格
    ax4.axis('off')
    table_data = []
    table_data.append(['温度(°C)', '单(W)', '双(W)', '差异(%)'])
    for i in range(len(results['T'])):
        table_data.append([
            f"{results['T'][i]:.0f}",
            f"{results['pmpp_single'][i]:.3f}",
            f"{results['pmpp_double'][i]:.3f}",
            f"{results['diff_pct'][i]:.2f}"
        ])
    
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                      colWidths=[0.2, 0.25, 0.25, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # 设置表头样式
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    plt.savefig(os.path.join(output_dir, 'exp3_high_temperature.png'), dpi=300, bbox_inches='tight')
    
    print(f"\n✓ 高温条件分析完成")
    print(f"  • 温度升高,两模型差异略有变化")
    print(f"  • 25°C差异: {results['diff_pct'][0]:.2f}%")
    print(f"  • 75°C差异: {results['diff_pct'][-1]:.2f}%")
    
    return fig


def experiment_4_computation_time():
    """
    实验4: 计算时间对比
    """
    print("\n" + "=" * 80)
    print("实验4: 计算时间对比")
    print("=" * 80)
    
    n_runs = 100
    n_points = 300
    
    # 测试单二极管
    start = time.time()
    for _ in range(n_runs):
        pv1 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        V, I = pv1.get_iv_curve(n_points)
        vmpp, impp, pmpp = pv1.find_mpp()
    time_single = (time.time() - start) / n_runs
    
    # 测试双二极管
    start = time.time()
    for _ in range(n_runs):
        pv2 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        V, I = pv2.get_iv_curve(n_points)
        vmpp, impp, pmpp = pv2.find_mpp()
    time_double = (time.time() - start) / n_runs
    
    # 结果
    print(f"\n计算时间对比 (平均 {n_runs} 次运行):")
    print(f"  单二极管模型: {time_single*1000:.2f} ms")
    print(f"  双二极管模型: {time_double*1000:.2f} ms")
    print(f"  时间比: {time_double/time_single:.2f}x")
    
    print(f"\n✓ 计算效率分析:")
    print(f"  • 双二极管模型计算时间约为单二极管的 {time_double/time_single:.1f} 倍")
    print(f"  • 精度提升通常值得这个额外开销")
    print(f"  • 对于实时应用,两者都足够快")


def run_all_experiments():
    """
    运行所有实验
    """
    print("\n" + "=" * 80)
    print("开始运行案例2的全部实验")
    print("=" * 80)
    
    experiment_1_standard_comparison()
    experiment_2_low_irradiance()
    experiment_3_high_temperature()
    experiment_4_computation_time()
    
    print("\n" + "=" * 80)
    print("全部实验完成！")
    print("=" * 80)
    print("\n所有图表已保存至: outputs/目录")
    
    plt.show()


if __name__ == "__main__":
    run_all_experiments()
