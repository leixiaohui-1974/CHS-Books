"""
案例7：坡面运动波汇流
==================

演示不同坡面汇流方法的原理和应用

作者: CHS-Books项目组
日期: 2025-11-02
"""

import sys
sys.path.insert(0, '../../..')

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from code.core.slope_routing import (
    KinematicWaveSlope, LinearReservoirSlope, NashCascade
)
from code.core.slope_routing.kinematic_wave import estimate_time_of_concentration
from code.core.slope_routing.linear_reservoir import estimate_K_from_tc

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)


def generate_net_rainfall(pattern='triangular', duration_min=30, dt_s=60):
    """
    生成净雨过程
    
    Parameters
    ----------
    pattern : str
        降雨模式: 'uniform', 'triangular', 'bimodal'
    duration_min : int
        持续时间(分钟)
    dt_s : int
        时间步长(秒)
    
    Returns
    -------
    runoff : ndarray
        净雨强度 (mm/h)
    time_min : ndarray
        时间序列 (分钟)
    """
    n_steps = duration_min
    time_min = np.arange(n_steps)
    
    if pattern == 'uniform':
        # 均匀净雨
        runoff = np.zeros(n_steps)
        runoff[5:25] = 30.0  # mm/h
    
    elif pattern == 'triangular':
        # 三角形净雨
        runoff = np.zeros(n_steps)
        peak_idx = 15
        runoff[5:peak_idx] = np.linspace(0, 40, peak_idx-5)
        runoff[peak_idx:25] = np.linspace(40, 0, 25-peak_idx)
    
    elif pattern == 'bimodal':
        # 双峰净雨
        runoff = np.zeros(n_steps)
        # 第一个峰
        runoff[5:10] = np.linspace(0, 30, 5)
        runoff[10:15] = np.linspace(30, 5, 5)
        # 第二个峰
        runoff[18:23] = np.linspace(5, 35, 5)
        runoff[23:28] = np.linspace(35, 0, 5)
    
    else:
        raise ValueError(f"未知的降雨模式: {pattern}")
    
    return runoff, time_min


def plot_kinematic_wave_process(model, runoff, time_min, save_path=None):
    """绘制运动波汇流过程"""
    # 运行模型
    results = model.run(runoff)
    
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 子图1：水深空间分布演进（选取几个时刻）
    ax1 = fig.add_subplot(gs[0, :])
    time_snapshots = [5, 10, 15, 20, 25]
    for t in time_snapshots:
        if t < len(results['water_depth']):
            ax1.plot(results['x'], results['water_depth'][t] * 1000,  # 转为mm
                    linewidth=2, label=f't={t}分钟')
    ax1.set_xlabel('沿程距离 (m)', fontsize=12)
    ax1.set_ylabel('水深 (mm)', fontsize=12)
    ax1.set_title('水深空间分布演进', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, ncol=5)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：净雨过程
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.bar(time_min, runoff, width=0.8, color='skyblue', 
           edgecolor='black', linewidth=0.5, alpha=0.7)
    ax2.set_xlabel('时间 (分钟)', fontsize=12)
    ax2.set_ylabel('净雨强度 (mm/h)', fontsize=12)
    ax2.set_title('净雨过程', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 子图3：出口流量过程
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(time_min[:len(results['outlet_discharge'])], 
            results['outlet_discharge'], 
            linewidth=2.5, color='red', label='出口流量')
    ax3.fill_between(time_min[:len(results['outlet_discharge'])], 
                     0, results['outlet_discharge'], 
                     alpha=0.3, color='red')
    ax3.set_xlabel('时间 (分钟)', fontsize=12)
    ax3.set_ylabel('流量 (m³/s)', fontsize=12)
    ax3.set_title('出口流量过程', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3)
    
    # 子图4：统计信息
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
    
    # 计算统计量
    peak_discharge = np.max(results['outlet_discharge'])
    peak_time = np.argmax(results['outlet_discharge'])
    total_runoff_volume = np.sum(runoff / 60) * model.L * model.W / 1000  # m³
    total_discharge_volume = np.sum(results['outlet_discharge']) * 60  # m³
    
    stats_text = f"""
    运动波汇流统计:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    坡面参数:
      • 长度: {model.L:.1f} m
      • 宽度: {model.W:.1f} m
      • 坡度: {model.S*100:.2f}%
      • 曼宁糙率: {model.n:.3f}
      • 空间步长: {model.dx:.1f} m
    
    汇流结果:
      • 峰值流量: {peak_discharge:.4f} m³/s
      • 峰现时间: {peak_time} 分钟
      • 总净雨量: {total_runoff_volume:.2f} m³
      • 总出流量: {total_discharge_volume:.2f} m³
      • 水量平衡误差: {abs(total_runoff_volume - total_discharge_volume):.3f} m³
    """
    
    ax4.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
            verticalalignment='center')
    
    plt.suptitle('运动波坡面汇流过程', fontsize=16, fontweight='bold', y=0.98)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig, results


def compare_linear_reservoir_K(area, runoff, time_min, save_path=None):
    """对比不同K值的线性水库"""
    K_values = [300, 600, 900, 1200]  # 秒
    dt = 60  # 秒
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    
    colors = ['blue', 'red', 'green', 'purple']
    
    for idx, K in enumerate(K_values):
        params = {
            'area': area,
            'K': K,
            'dt': dt
        }
        model = LinearReservoirSlope(params)
        results = model.run(runoff)
        
        ax = axes[idx]
        
        # 双Y轴
        ax2 = ax.twinx()
        
        # 净雨
        l1 = ax.bar(time_min, runoff, width=0.8, alpha=0.3, 
                   color='skyblue', edgecolor='black', linewidth=0.5,
                   label='净雨强度')
        
        # 出流
        l2 = ax2.plot(time_min, results['discharge'], 
                     linewidth=2.5, color=colors[idx], label='出流量')
        ax2.fill_between(time_min, 0, results['discharge'], 
                        alpha=0.2, color=colors[idx])
        
        ax.set_xlabel('时间 (分钟)', fontsize=11)
        ax.set_ylabel('净雨强度 (mm/h)', fontsize=11, color='black')
        ax2.set_ylabel('流量 (m³/s)', fontsize=11, color=colors[idx])
        ax.set_title(f'K = {K}s ({K/60:.1f}分钟)', fontsize=13, fontweight='bold')
        
        # 统计
        peak_Q = np.max(results['discharge'])
        peak_t = np.argmax(results['discharge'])
        ax.text(0.02, 0.98, f'峰值: {peak_Q:.4f} m³/s\n峰现: {peak_t}分钟',
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # 图例
        lines = [l1] + l2
        labels = ['净雨强度', '出流量']
        ax.legend(lines, labels, loc='upper right', fontsize=9)
        
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('线性水库调蓄系数K的影响', fontsize=15, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def compare_nash_cascade_n(area, runoff, time_min, K_base, save_path=None):
    """对比不同n值的纳什瀑布"""
    n_values = [1, 2, 3, 5]
    dt = 60
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = ['blue', 'red', 'green', 'purple']
    
    # 净雨（背景）
    ax2 = ax.twinx()
    ax2.bar(time_min, runoff, width=0.8, alpha=0.2, 
           color='lightgray', edgecolor='black', linewidth=0.5,
           label='净雨强度')
    ax2.set_ylabel('净雨强度 (mm/h)', fontsize=12, color='gray')
    ax2.tick_params(axis='y', labelcolor='gray')
    
    # 各种n值
    for n, color in zip(n_values, colors):
        K = K_base / n if n > 1 else K_base
        
        if n == 1:
            # 单个线性水库
            params = {'area': area, 'K': K, 'dt': dt}
            model = LinearReservoirSlope(params)
            results = model.run(runoff)
            discharge = results['discharge']
        else:
            # 纳什瀑布
            params = {'area': area, 'K': K, 'n': n, 'dt': dt}
            model = NashCascade(params)
            results = model.run(runoff)
            discharge = results['discharge']
        
        peak_Q = np.max(discharge)
        peak_t = np.argmax(discharge)
        
        ax.plot(time_min, discharge, linewidth=2.5, color=color,
               label=f'n={n} (峰值={peak_Q:.4f} m³/s, 峰现={peak_t}min)')
    
    ax.set_xlabel('时间 (分钟)', fontsize=13)
    ax.set_ylabel('流量 (m³/s)', fontsize=13)
    ax.set_title(f'纳什瀑布水库数量(n)的影响 (K_total={K_base}s)', 
                fontsize=15, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def compare_all_methods(save_path=None):
    """对比三种汇流方法"""
    # 统一参数
    length = 100  # m
    width = 50    # m
    slope = 0.02  # 2%
    manning_n = 0.15
    area = length * width  # m²
    dt = 60  # s
    
    # 生成净雨
    runoff, time_min = generate_net_rainfall('triangular', 30, dt)
    
    # 1. 运动波
    kw_params = {
        'length': length,
        'width': width,
        'slope': slope,
        'manning_n': manning_n,
        'dx': 10,
        'dt': dt
    }
    kw_model = KinematicWaveSlope(kw_params)
    kw_results = kw_model.run(runoff)
    
    # 2. 线性水库
    tc = estimate_time_of_concentration(length, slope, manning_n)
    K = tc / 2
    lr_params = {'area': area, 'K': K, 'dt': dt}
    lr_model = LinearReservoirSlope(lr_params)
    lr_results = lr_model.run(runoff)
    
    # 3. 纳什瀑布
    n = 3
    K_nash = estimate_K_from_tc(tc, n)
    nash_params = {'area': area, 'K': K_nash, 'n': n, 'dt': dt}
    nash_model = NashCascade(nash_params)
    nash_results = nash_model.run(runoff)
    
    # 绘图
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 子图1-3: 各方法详细
    methods = [
        ('运动波', kw_results['outlet_discharge'], 'blue'),
        ('线性水库', lr_results['discharge'], 'red'),
        ('纳什瀑布', nash_results['discharge'], 'green')
    ]
    
    for idx, (name, discharge, color) in enumerate(methods):
        if idx < 3:
            row = idx // 2
            col = idx % 2
            ax = axes[row, col]
            
            # 净雨背景
            ax2 = ax.twinx()
            ax2.bar(time_min, runoff, width=0.8, alpha=0.2,
                   color='lightgray', edgecolor='black', linewidth=0.5)
            ax2.set_ylabel('净雨 (mm/h)', fontsize=10, color='gray')
            
            # 流量
            ax.plot(time_min[:len(discharge)], discharge, 
                   linewidth=2.5, color=color)
            ax.fill_between(time_min[:len(discharge)], 0, discharge,
                           alpha=0.3, color=color)
            
            peak_Q = np.max(discharge)
            peak_t = np.argmax(discharge)
            
            ax.set_xlabel('时间 (分钟)', fontsize=11)
            ax.set_ylabel('流量 (m³/s)', fontsize=11)
            ax.set_title(f'{name}\n峰值={peak_Q:.4f} m³/s, 峰现={peak_t}min',
                        fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
    
    # 子图4: 综合对比
    ax = axes[1, 1]
    
    for name, discharge, color in methods:
        ax.plot(time_min[:len(discharge)], discharge,
               linewidth=2.5, color=color, label=name)
    
    ax.set_xlabel('时间 (分钟)', fontsize=12)
    ax.set_ylabel('流量 (m³/s)', fontsize=12)
    ax.set_title('三种方法对比', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('坡面汇流方法综合对比', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    # 返回统计
    stats = {
        '运动波': {
            'peak': np.max(kw_results['outlet_discharge']),
            'time': np.argmax(kw_results['outlet_discharge'])
        },
        '线性水库': {
            'peak': np.max(lr_results['discharge']),
            'time': np.argmax(lr_results['discharge'])
        },
        '纳什瀑布': {
            'peak': np.max(nash_results['discharge']),
            'time': np.argmax(nash_results['discharge'])
        }
    }
    
    return fig, stats


def main():
    """主函数"""
    print("=" * 70)
    print("案例7：坡面运动波汇流")
    print("=" * 70)
    print()
    
    # 1. 运动波汇流过程
    print("1. 运动波汇流过程演示...")
    kw_params = {
        'length': 100,      # m
        'width': 50,        # m
        'slope': 0.02,      # 2%
        'manning_n': 0.15,
        'dx': 10,           # m
        'dt': 60            # s
    }
    
    print(f"   坡面参数:")
    print(f"     长度: {kw_params['length']} m")
    print(f"     宽度: {kw_params['width']} m")
    print(f"     坡度: {kw_params['slope']*100:.1f}%")
    print(f"     糙率: {kw_params['manning_n']}")
    print()
    
    # 估算汇流时间
    tc = estimate_time_of_concentration(
        kw_params['length'], kw_params['slope'], kw_params['manning_n']
    )
    print(f"   估算汇流时间: {tc/60:.2f} 分钟")
    print()
    
    kw_model = KinematicWaveSlope(kw_params)
    runoff, time_min = generate_net_rainfall('triangular', 30, 60)
    
    fig1, kw_results = plot_kinematic_wave_process(
        kw_model, runoff, time_min,
        save_path=output_dir / 'kinematic_wave_process.png'
    )
    plt.close(fig1)
    
    # 2. 线性水库K值对比
    print("2. 线性水库调蓄系数K的影响...")
    area = kw_params['length'] * kw_params['width']
    fig2 = compare_linear_reservoir_K(
        area, runoff, time_min,
        save_path=output_dir / 'linear_reservoir_comparison.png'
    )
    plt.close(fig2)
    print("   对比完成")
    print()
    
    # 3. 纳什瀑布n值对比
    print("3. 纳什瀑布水库数量n的影响...")
    K_base = 900  # 秒
    fig3 = compare_nash_cascade_n(
        area, runoff, time_min, K_base,
        save_path=output_dir / 'nash_cascade_effect.png'
    )
    plt.close(fig3)
    print("   对比完成")
    print()
    
    # 4. 三种方法综合对比
    print("4. 三种汇流方法综合对比...")
    fig4, stats = compare_all_methods(
        save_path=output_dir / 'method_comparison.png'
    )
    plt.close(fig4)
    
    print()
    print("   对比结果:")
    for method, data in stats.items():
        print(f"     {method:8s}: 峰值={data['peak']:.4f} m³/s, 峰现={data['time']}分钟")
    print()
    
    # 5. 总结
    print("=" * 70)
    print("分析完成！")
    print("=" * 70)
    print()
    print("生成的文件:")
    print("  - outputs/kinematic_wave_process.png      : 运动波汇流过程")
    print("  - outputs/linear_reservoir_comparison.png : 线性水库对比")
    print("  - outputs/nash_cascade_effect.png         : 纳什瀑布效果")
    print("  - outputs/method_comparison.png           : 方法综合对比")
    print()
    print("关键发现:")
    print("  1. 运动波法峰值最大、峰现最早（物理过程真实）")
    print("  2. 线性水库法调蓄效果明显（参数K控制）")
    print("  3. 纳什瀑布调蓄效果最强（多级串联）")
    print("  4. 方法选择需平衡精度与效率")
    print("  5. 参数率定对结果影响显著")
    print()


if __name__ == '__main__':
    main()
