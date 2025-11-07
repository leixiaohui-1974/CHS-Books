"""
案例13: PWM调制技术
演示SPWM和SVPWM调制算法，分析谐波特性

实验内容:
1. SPWM调制原理与实现
2. SVPWM调制原理与实现
3. 调制比对输出的影响
4. THD谐波分析
5. SPWM vs SVPWM性能对比

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# 添加models路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.inverter_control import (
    InverterParameters, SPWMModulator, SVPWMModulator, InverterModel
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_spwm_principle():
    """
    实验1: SPWM调制原理
    展示正弦调制波与三角载波的比较过程
    """
    print("=" * 60)
    print("实验1: SPWM调制原理")
    print("=" * 60)
    
    # 初始化参数
    params = InverterParameters(
        V_dc=400.0,
        V_ac=220.0,
        f_ac=50.0,
        f_sw=2000.0  # 较低的开关频率便于观察
    )
    
    # 创建SPWM调制器
    spwm = SPWMModulator(params, modulation_index=0.9)
    
    # 仿真一个基波周期
    duration = 1.0 / params.f_ac  # 20ms
    result = spwm.simulate(duration)
    
    # 提取结果
    time_ms = result['time'] * 1000  # 转换为ms
    
    # 创建图形
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    
    # 子图1: 参考正弦波
    axes[0].plot(time_ms, result['v_ref'], 'b-', linewidth=2, label='参考电压')
    axes[0].set_ylabel('电压 (V)', fontsize=11)
    axes[0].set_title('SPWM调制原理', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=10)
    
    # 子图2: 调制波与载波
    axes[1].plot(time_ms, result['modulation_wave'], 'b-', linewidth=1.5, label='调制波')
    axes[1].plot(time_ms, result['carrier_wave'], 'r-', linewidth=0.8, alpha=0.6, label='载波')
    axes[1].set_ylabel('归一化幅值', fontsize=11)
    axes[1].set_ylim([-1.2, 1.2])
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=10, loc='upper right')
    
    # 子图3: 开关信号
    axes[2].plot(time_ms, result['switching_signal'], 'g-', linewidth=1)
    axes[2].set_ylabel('开关状态', fontsize=11)
    axes[2].set_ylim([-0.1, 1.1])
    axes[2].set_yticks([0, 1])
    axes[2].set_yticklabels(['OFF', 'ON'])
    axes[2].grid(True, alpha=0.3)
    
    # 子图4: 输出电压
    axes[3].plot(time_ms, result['output_voltage'], 'r-', linewidth=1, label='PWM输出')
    axes[3].plot(time_ms, result['v_ref'], 'b--', linewidth=1.5, alpha=0.6, label='参考电压')
    axes[3].set_xlabel('时间 (ms)', fontsize=11)
    axes[3].set_ylabel('电压 (V)', fontsize=11)
    axes[3].grid(True, alpha=0.3)
    axes[3].legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('case_13_exp1_spwm_principle.png', dpi=300, bbox_inches='tight')
    print("✓ 图1已保存: case_13_exp1_spwm_principle.png")
    plt.show()
    
    # 输出关键参数
    print(f"\n关键参数:")
    print(f"  调制比 ma = {spwm.modulation_index:.2f}")
    print(f"  频率比 mf = {spwm.mf}")
    print(f"  直流电压 Vdc = {params.V_dc} V")
    print(f"  输出电压峰值 = {params.V_ac * np.sqrt(2):.1f} V")
    print(f"  开关频率 = {params.f_sw} Hz")


def experiment_2_modulation_index_effect():
    """
    实验2: 调制比对输出的影响
    对比不同调制比下的输出特性
    """
    print("\n" + "=" * 60)
    print("实验2: 调制比对输出的影响")
    print("=" * 60)
    
    params = InverterParameters()
    modulation_indices = [0.5, 0.7, 0.9]
    
    fig, axes = plt.subplots(len(modulation_indices), 2, figsize=(14, 10))
    
    for idx, ma in enumerate(modulation_indices):
        print(f"\n测试调制比 ma = {ma}")
        
        # 创建调制器
        spwm = SPWMModulator(params, modulation_index=ma)
        
        # 仿真
        duration = 0.04  # 2个周期
        result = spwm.simulate(duration)
        
        time_ms = result['time'] * 1000
        
        # 左图: 时域波形
        axes[idx, 0].plot(time_ms, result['v_ref'], 'b--', linewidth=1, 
                          alpha=0.6, label='参考')
        axes[idx, 0].plot(time_ms, result['output_voltage'], 'r-', 
                          linewidth=0.8, label=f'PWM输出 (ma={ma})')
        axes[idx, 0].set_ylabel('电压 (V)', fontsize=10)
        axes[idx, 0].grid(True, alpha=0.3)
        axes[idx, 0].legend(fontsize=9)
        axes[idx, 0].set_title(f'调制比 ma = {ma}', fontsize=11)
        
        # THD分析
        fs = 1.0 / (result['time'][1] - result['time'][0])
        thd_result = spwm.calculate_thd(result['output_voltage'], fs, params.f_ac, n_harmonics=50)
        
        # 右图: 频谱
        freqs = thd_result['frequencies']
        magnitude = thd_result['magnitude']
        
        # 只显示到2kHz
        freq_limit = 2000
        mask = freqs <= freq_limit
        
        axes[idx, 1].stem(freqs[mask], magnitude[mask], linefmt='b-', 
                          markerfmt='bo', basefmt='k-', label='谐波')
        axes[idx, 1].set_ylabel('幅值 (V)', fontsize=10)
        axes[idx, 1].grid(True, alpha=0.3)
        axes[idx, 1].set_xlim([0, freq_limit])
        axes[idx, 1].set_title(f'频谱 (THD = {thd_result["THD"]:.2f}%)', fontsize=11)
        
        # 标注基波
        axes[idx, 1].axvline(params.f_ac, color='r', linestyle='--', 
                             linewidth=1, alpha=0.5, label='基波')
        axes[idx, 1].legend(fontsize=9)
        
        print(f"  基波幅值: {thd_result['fundamental']:.2f} V")
        print(f"  THD: {thd_result['THD']:.2f} %")
    
    axes[-1, 0].set_xlabel('时间 (ms)', fontsize=10)
    axes[-1, 1].set_xlabel('频率 (Hz)', fontsize=10)
    
    fig.suptitle('调制比对SPWM输出的影响', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('case_13_exp2_modulation_index.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图2已保存: case_13_exp2_modulation_index.png")
    plt.show()


def experiment_3_svpwm_principle():
    """
    实验3: SVPWM调制原理
    展示空间矢量调制的扇区切换和矢量合成
    """
    print("\n" + "=" * 60)
    print("实验3: SVPWM调制原理")
    print("=" * 60)
    
    params = InverterParameters()
    svpwm = SVPWMModulator(params)
    
    # 仿真
    duration = 0.04  # 2个周期
    result = svpwm.simulate(duration)
    
    time_ms = result['time'] * 1000
    
    # 创建图形
    fig = plt.figure(figsize=(14, 10))
    
    # 子图1: 三相参考电压
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(time_ms, result['va_ref'], 'r-', linewidth=1.5, label='Va')
    ax1.plot(time_ms, result['vb_ref'], 'g-', linewidth=1.5, label='Vb')
    ax1.plot(time_ms, result['vc_ref'], 'b-', linewidth=1.5, label='Vc')
    ax1.set_ylabel('电压 (V)', fontsize=10)
    ax1.set_title('三相参考电压', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9, ncol=3)
    
    # 子图2: αβ坐标系
    ax2 = plt.subplot(3, 2, 2)
    ax2.plot(result['v_alpha'], result['v_beta'], 'b-', linewidth=1.5, alpha=0.7)
    ax2.plot(result['v_alpha'][0], result['v_beta'][0], 'go', markersize=8, label='起点')
    ax2.plot(result['v_alpha'][-1], result['v_beta'][-1], 'ro', markersize=8, label='终点')
    
    # 绘制基本矢量
    for i in range(6):
        angle = i * np.pi / 3
        v_x = np.cos(angle) * params.V_ac * np.sqrt(2) * 0.8
        v_y = np.sin(angle) * params.V_ac * np.sqrt(2) * 0.8
        ax2.arrow(0, 0, v_x, v_y, head_width=15, head_length=10, 
                  fc='gray', ec='gray', alpha=0.3)
        ax2.text(v_x*1.15, v_y*1.15, f'V{i+1}', fontsize=9, ha='center')
    
    ax2.set_xlabel('Vα (V)', fontsize=10)
    ax2.set_ylabel('Vβ (V)', fontsize=10)
    ax2.set_title('αβ坐标系轨迹', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    ax2.legend(fontsize=9)
    
    # 子图3: 扇区切换
    ax3 = plt.subplot(3, 2, 3)
    ax3.plot(time_ms, result['sectors'], 'k-', linewidth=2, marker='o', 
             markersize=3, markevery=20)
    ax3.set_ylabel('扇区号', fontsize=10)
    ax3.set_title('扇区切换', fontsize=11, fontweight='bold')
    ax3.set_ylim([0.5, 6.5])
    ax3.set_yticks([1, 2, 3, 4, 5, 6])
    ax3.grid(True, alpha=0.3)
    
    # 子图4: 矢量作用时间
    ax4 = plt.subplot(3, 2, 4)
    ax4.plot(time_ms, result['T1'], 'r-', linewidth=1.5, label='T1', alpha=0.7)
    ax4.plot(time_ms, result['T2'], 'g-', linewidth=1.5, label='T2', alpha=0.7)
    ax4.plot(time_ms, result['T0'], 'b-', linewidth=1.5, label='T0', alpha=0.7)
    ax4.set_ylabel('归一化时间', fontsize=10)
    ax4.set_title('矢量作用时间', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=9, ncol=3)
    ax4.set_ylim([0, 1.05])
    
    # 子图5: 矢量轨迹详图 (一个周期)
    ax5 = plt.subplot(3, 2, 5)
    n_samples = len(result['v_alpha'])
    n_per_period = n_samples // 2
    alpha_one = result['v_alpha'][:n_per_period]
    beta_one = result['v_beta'][:n_per_period]
    
    # 用颜色表示时间
    scatter = ax5.scatter(alpha_one, beta_one, c=np.linspace(0, 1, len(alpha_one)), 
                          cmap='rainbow', s=10, alpha=0.6)
    ax5.set_xlabel('Vα (V)', fontsize=10)
    ax5.set_ylabel('Vβ (V)', fontsize=10)
    ax5.set_title('矢量轨迹 (单周期)', fontsize=11, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.axis('equal')
    cbar = plt.colorbar(scatter, ax=ax5)
    cbar.set_label('时间', fontsize=9)
    
    # 子图6: 统计信息
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    
    # 计算统计信息
    V_alpha_rms = np.sqrt(np.mean(result['v_alpha']**2))
    V_beta_rms = np.sqrt(np.mean(result['v_beta']**2))
    V_ref_mag = np.sqrt(np.mean(result['v_alpha']**2 + result['v_beta']**2))
    
    # 扇区占用统计
    sector_counts = np.bincount(result['sectors'], minlength=7)[1:]  # 排除索引0
    sector_percentages = sector_counts / np.sum(sector_counts) * 100
    
    info_text = f"""
    SVPWM调制参数
    
    直流母线电压: {params.V_dc} V
    交流频率: {params.f_ac} Hz
    开关频率: {params.f_sw} Hz
    
    矢量信息:
      Vα RMS: {V_alpha_rms:.2f} V
      Vβ RMS: {V_beta_rms:.2f} V
      |Vref|: {V_ref_mag:.2f} V
    
    扇区占用率:
    """
    
    for i, pct in enumerate(sector_percentages, 1):
        info_text += f"  扇区{i}: {pct:.1f}%\n"
    
    ax6.text(0.1, 0.95, info_text, transform=ax6.transAxes,
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.suptitle('SVPWM空间矢量调制原理', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('case_13_exp3_svpwm_principle.png', dpi=300, bbox_inches='tight')
    print("✓ 图3已保存: case_13_exp3_svpwm_principle.png")
    plt.show()
    
    print(f"\n关键参数:")
    print(f"  参考矢量幅值: {V_ref_mag:.2f} V")
    print(f"  直流电压利用率: {V_ref_mag / params.V_dc * 100:.1f}%")


def experiment_4_spwm_vs_svpwm():
    """
    实验4: SPWM vs SVPWM 性能对比
    """
    print("\n" + "=" * 60)
    print("实验4: SPWM vs SVPWM 性能对比")
    print("=" * 60)
    
    params = InverterParameters(f_sw=10000.0)
    
    # SPWM仿真
    print("\n运行SPWM仿真...")
    spwm = SPWMModulator(params, modulation_index=0.9)
    spwm_model = InverterModel(params, spwm)
    spwm_result = spwm_model.simulate_with_filter(duration=0.1, load_resistance=10.0)
    
    # SVPWM仿真 (简化: 使用单相等效)
    print("运行SVPWM仿真...")
    svpwm = SVPWMModulator(params)
    svpwm_result = svpwm.simulate(duration=0.1)
    
    # THD分析
    fs_spwm = 1.0 / (spwm_result['time'][1] - spwm_result['time'][0])
    thd_spwm_pwm = spwm.calculate_thd(spwm_result['v_pwm'], fs_spwm, params.f_ac)
    thd_spwm_out = spwm.calculate_thd(spwm_result['v_output'], fs_spwm, params.f_ac)
    
    # 创建对比图
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    time_ms = spwm_result['time'] * 1000
    
    # SPWM时域波形
    axes[0, 0].plot(time_ms, spwm_result['v_pwm'], 'b-', linewidth=0.5, 
                    alpha=0.6, label='PWM输出')
    axes[0, 0].plot(time_ms, spwm_result['v_output'], 'r-', linewidth=2, 
                    label='滤波后输出')
    axes[0, 0].set_ylabel('电压 (V)', fontsize=11)
    axes[0, 0].set_title('SPWM - 时域波形', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend(fontsize=10)
    axes[0, 0].set_xlim([0, 40])  # 只显示2个周期
    
    # SPWM频谱
    axes[0, 1].stem(thd_spwm_out['frequencies'][:200], 
                    thd_spwm_out['magnitude'][:200],
                    linefmt='b-', markerfmt='bo', basefmt='k-')
    axes[0, 1].set_ylabel('幅值 (V)', fontsize=11)
    axes[0, 1].set_title(f'SPWM - 频谱 (THD={thd_spwm_out["THD"]:.2f}%)', 
                        fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].axvline(params.f_ac, color='r', linestyle='--', 
                      linewidth=2, alpha=0.5)
    
    # SVPWM三相波形
    time_ms_sv = svpwm_result['time'] * 1000
    axes[1, 0].plot(time_ms_sv, svpwm_result['va_ref'], 'r-', 
                    linewidth=1.5, alpha=0.7, label='Va')
    axes[1, 0].plot(time_ms_sv, svpwm_result['vb_ref'], 'g-', 
                    linewidth=1.5, alpha=0.7, label='Vb')
    axes[1, 0].plot(time_ms_sv, svpwm_result['vc_ref'], 'b-', 
                    linewidth=1.5, alpha=0.7, label='Vc')
    axes[1, 0].set_xlabel('时间 (ms)', fontsize=11)
    axes[1, 0].set_ylabel('电压 (V)', fontsize=11)
    axes[1, 0].set_title('SVPWM - 三相输出', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend(fontsize=10, ncol=3)
    axes[1, 0].set_xlim([0, 40])
    
    # 性能对比表
    axes[1, 1].axis('off')
    
    # 计算关键指标
    V_out_spwm = np.sqrt(np.mean(spwm_result['v_output']**2))
    V_out_svpwm = np.sqrt(np.mean(svpwm_result['va_ref']**2))
    
    util_spwm = V_out_spwm / (params.V_dc / np.sqrt(2)) * 100
    util_svpwm = V_out_svpwm / (params.V_dc / np.sqrt(2)) * 100
    
    comparison_text = f"""
    性能对比
    
    指标                SPWM        SVPWM
    {'='*45}
    输出电压(RMS)      {V_out_spwm:.1f}V      {V_out_svpwm:.1f}V
    
    直流电压利用率     {util_spwm:.1f}%       {util_svpwm:.1f}%
    
    THD (滤波前)       {thd_spwm_pwm['THD']:.2f}%       -
    
    THD (滤波后)       {thd_spwm_out['THD']:.2f}%       -
    
    基波幅值          {thd_spwm_out['fundamental']:.1f}V      {V_out_svpwm*np.sqrt(2):.1f}V
    
    实现复杂度         简单        较复杂
    
    适用场合          单相        三相
    """
    
    axes[1, 1].text(0.05, 0.95, comparison_text, transform=axes[1, 1].transAxes,
                   fontsize=11, verticalalignment='top', family='monospace',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    axes[1, 0].set_xlabel('时间 (ms)', fontsize=11)
    
    plt.suptitle('SPWM vs SVPWM 性能对比', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('case_13_exp4_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✓ 图4已保存: case_13_exp4_comparison.png")
    plt.show()
    
    # 打印详细对比
    print(f"\n详细对比:")
    print(f"  SPWM:")
    print(f"    输出电压(RMS): {V_out_spwm:.2f} V")
    print(f"    直流电压利用率: {util_spwm:.1f}%")
    print(f"    THD (滤波后): {thd_spwm_out['THD']:.2f}%")
    print(f"  SVPWM:")
    print(f"    输出电压(RMS): {V_out_svpwm:.2f} V")
    print(f"    直流电压利用率: {util_svpwm:.1f}%")
    print(f"    理论优势: 直流电压利用率提高约15%")


def main():
    """主函数"""
    print("=" * 60)
    print("案例13: PWM调制技术")
    print("从单相SPWM到三相SVPWM的完整实现")
    print("=" * 60)
    
    # 运行所有实验
    experiment_1_spwm_principle()
    experiment_2_modulation_index_effect()
    experiment_3_svpwm_principle()
    experiment_4_spwm_vs_svpwm()
    
    print("\n" + "=" * 60)
    print("✅ 所有实验完成!")
    print("=" * 60)
    print("\n总结:")
    print("  1. SPWM通过正弦调制波与三角载波比较产生PWM信号")
    print("  2. 调制比影响输出电压幅值,调制比越大输出越大")
    print("  3. SVPWM通过空间矢量合成,直流电压利用率更高")
    print("  4. SVPWM适用于三相系统,SPWM更适合单相系统")
    print("  5. 适当的滤波可以显著降低THD")


if __name__ == "__main__":
    main()
