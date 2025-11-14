"""
案例10：Muskingum-Cunge河道洪水演进方法
=========================================

Muskingum-Cunge方法是Muskingum方法的物理基础改进版，
参数K和X根据河道物理特性动态计算。

核心内容：
1. 物理参数估算K和X
2. 动态波速计算
from pathlib import Path
3. 河段演进模拟
4. 多河段串联
5. 与经验Muskingum方法对比

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def manning_velocity(Q: float, B: float, n: float, S0: float) -> float:
    """
    根据曼宁公式计算流速
    
    参数:
    ----
    Q : float
        流量 (m³/s)
    B : float
        河宽 (m)
    n : float
        糙率系数
    S0 : float
        河床坡度
    
    返回:
    ----
    v : float
        流速 (m/s)
    """
    # 假设矩形断面，水深h = (Q*n / (B*sqrt(S0)))^0.6
    # v = Q / (B*h)
    
    if Q <= 0 or B <= 0 or S0 <= 0:
        return 0.1  # 最小流速
    
    # 简化：v ≈ (Q*S0^0.5 / (B*n))^0.6
    v = np.power(Q * np.sqrt(S0) / (B * n), 0.6)
    
    return max(v, 0.1)


def compute_wave_celerity(Q: float, B: float, n: float, S0: float) -> float:
    """
    计算洪波波速（动力波传播速度）
    
    参数:
    ----
    Q : float
        流量 (m³/s)
    B : float
        河宽 (m)
    n : float
        糙率系数
    S0 : float
        河床坡度
    
    返回:
    ----
    c : float
        波速 (m/s)
    """
    # 根据曼宁公式推导，动力波波速 c ≈ (5/3) * v
    v = manning_velocity(Q, B, n, S0)
    c = (5.0 / 3.0) * v
    
    return max(c, 0.5)


def compute_muskingum_cunge_params(Q: float, B: float, n: float, 
                                    S0: float, dx: float, 
                                    dt: float) -> Dict[str, float]:
    """
    计算Muskingum-Cunge参数
    
    参数:
    ----
    Q : float
        参考流量 (m³/s)
    B : float
        河宽 (m)
    n : float
        糙率系数
    S0 : float
        河床坡度
    dx : float
        河段长度 (m)
    dt : float
        时间步长 (h)
    
    返回:
    ----
    params : dict
        包含K, X, C0, C1, C2
    """
    # 计算波速
    c = compute_wave_celerity(Q, B, n, S0)
    
    # K = dx / c (小时)
    K = dx / (c * 3600)  # 转换为小时
    
    # X = 0.5 * (1 - Q / (B * S0 * c * dx))
    # 简化形式：X ≈ 0.5 * (1 - v/c)
    v = manning_velocity(Q, B, n, S0)
    X = 0.5 * (1 - v / c)
    X = np.clip(X, 0, 0.5)  # 限制在合理范围
    
    # 计算演算系数
    denominator = K - K * X + 0.5 * dt
    if abs(denominator) < 1e-6:
        denominator = 1e-6
    
    C0 = (-K * X + 0.5 * dt) / denominator
    C1 = (K * X + 0.5 * dt) / denominator
    C2 = (K - K * X - 0.5 * dt) / denominator
    
    return {
        'K': K,
        'X': X,
        'C0': C0,
        'C1': C1,
        'C2': C2,
        'c': c,
        'v': v
    }


def muskingum_cunge_routing(inflow: np.ndarray, B: float, n: float, 
                            S0: float, dx: float, 
                            dt: float) -> Dict[str, np.ndarray]:
    """
    Muskingum-Cunge河道演进
    
    参数:
    ----
    inflow : ndarray
        入流过程 (m³/s)
    B : float
        河宽 (m)
    n : float
        糙率系数
    S0 : float
        河床坡度
    dx : float
        河段长度 (m)
    dt : float
        时间步长 (h)
    
    返回:
    ----
    results : dict
        包含outflow, K_series, X_series等
    """
    n_steps = len(inflow)
    
    # 初始化
    outflow = np.zeros(n_steps)
    K_series = np.zeros(n_steps)
    X_series = np.zeros(n_steps)
    c_series = np.zeros(n_steps)
    
    Q_prev = inflow[0]
    I_prev = inflow[0]
    
    for t in range(n_steps):
        I = inflow[t]
        
        # 使用平均流量计算参数
        Q_ref = (I + Q_prev) / 2
        Q_ref = max(Q_ref, 0.1)  # 避免零流量
        
        # 动态计算参数
        params = compute_muskingum_cunge_params(Q_ref, B, n, S0, dx, dt)
        
        # Muskingum演算
        Q_new = params['C0'] * I + params['C1'] * I_prev + params['C2'] * Q_prev
        Q_new = max(Q_new, 0)
        
        # 保存结果
        outflow[t] = Q_new
        K_series[t] = params['K']
        X_series[t] = params['X']
        c_series[t] = params['c']
        
        # 更新状态
        I_prev = I
        Q_prev = Q_new
    
    # 统计
    peak_in = np.max(inflow)
    peak_out = np.max(outflow)
    attenuation = (peak_in - peak_out) / peak_in if peak_in > 0 else 0
    
    peak_in_time = np.argmax(inflow)
    peak_out_time = np.argmax(outflow)
    lag = (peak_out_time - peak_in_time) * dt
    
    return {
        'outflow': outflow,
        'K_series': K_series,
        'X_series': X_series,
        'c_series': c_series,
        'attenuation': attenuation,
        'lag': lag,
        'peak_in': peak_in,
        'peak_out': peak_out
    }


def cascade_routing(inflow: np.ndarray, reach_params: list, 
                    dt: float) -> Dict[str, list]:
    """
    多河段串联演进
    
    参数:
    ----
    inflow : ndarray
        初始入流 (m³/s)
    reach_params : list of dict
        每个河段的参数 [{'B':..., 'n':..., 'S0':..., 'dx':...}, ...]
    dt : float
        时间步长 (h)
    
    返回:
    ----
    results : dict
        包含每个河段的出流过程
    """
    n_reaches = len(reach_params)
    outflows = []
    
    current_inflow = inflow.copy()
    
    for i, params in enumerate(reach_params):
        print(f"  河段{i+1}: L={params['dx']/1000:.1f}km, "
              f"B={params['B']:.0f}m, S0={params['S0']:.5f}")
        
        result = muskingum_cunge_routing(
            current_inflow,
            B=params['B'],
            n=params['n'],
            S0=params['S0'],
            dx=params['dx'],
            dt=dt
        )
        
        outflows.append(result['outflow'])
        current_inflow = result['outflow'].copy()
    
    return {
        'outflows': outflows,
        'final_outflow': outflows[-1] if outflows else inflow
    }


def generate_flood_hydrograph(duration: int = 48, peak_time: int = 12,
                              peak_flow: float = 1000, 
                              base_flow: float = 50) -> np.ndarray:
    """
    生成洪水过程线
    
    参数:
    ----
    duration : int
        总时段数
    peak_time : int
        峰值时刻
    peak_flow : float
        峰值流量 (m³/s)
    base_flow : float
        基流 (m³/s)
    
    返回:
    ----
    hydrograph : ndarray
        洪水过程
    """
    t = np.arange(duration)
    
    # 使用Gamma分布形状
    alpha = 3.0
    beta = peak_time / alpha
    
    # 归一化Gamma分布
    gamma_curve = np.power(t / beta, alpha - 1) * np.exp(-t / beta)
    gamma_curve = gamma_curve / np.max(gamma_curve)
    
    # 缩放到峰值
    hydrograph = base_flow + (peak_flow - base_flow) * gamma_curve
    
    return hydrograph


def plot_routing_comparison(time: np.ndarray, inflow: np.ndarray,
                            outflow_mc: np.ndarray,
                            title: str = "Muskingum-Cunge演进结果",
                            save_path: str = None):
    """绘制演进对比图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(time, inflow, 'b-', linewidth=2, label='入流', marker='o', markersize=4)
    ax.plot(time, outflow_mc, 'r-', linewidth=2, label='出流', marker='s', markersize=4)
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('流量 (m³/s)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 标注峰值
    peak_in_idx = np.argmax(inflow)
    peak_out_idx = np.argmax(outflow_mc)
    
    ax.plot(time[peak_in_idx], inflow[peak_in_idx], 'bo', markersize=10)
    ax.plot(time[peak_out_idx], outflow_mc[peak_out_idx], 'rs', markersize=10)
    
    ax.annotate(f'峰值: {inflow[peak_in_idx]:.0f}', 
                xy=(time[peak_in_idx], inflow[peak_in_idx]),
                xytext=(10, 10), textcoords='offset points',
                fontsize=10, color='blue')
    
    ax.annotate(f'峰值: {outflow_mc[peak_out_idx]:.0f}', 
                xy=(time[peak_out_idx], outflow_mc[peak_out_idx]),
                xytext=(10, -20), textcoords='offset points',
                fontsize=10, color='red')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_parameters_evolution(time: np.ndarray, K_series: np.ndarray,
                              X_series: np.ndarray, c_series: np.ndarray,
                              save_path: str = None):
    """绘制参数演变图"""
    fig, axes = plt.subplots(3, 1, figsize=(10, 10))
    
    # K演变
    axes[0].plot(time, K_series, 'b-', linewidth=2, marker='o', markersize=4)
    axes[0].set_ylabel('K (h)', fontsize=12)
    axes[0].set_title('传播时间常数K的演变', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # X演变
    axes[1].plot(time, X_series, 'g-', linewidth=2, marker='s', markersize=4)
    axes[1].set_ylabel('X', fontsize=12)
    axes[1].set_title('蓄量比重系数X的演变', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0.25, color='r', linestyle='--', alpha=0.5, label='典型值0.25')
    axes[1].legend(fontsize=10)
    
    # 波速演变
    axes[2].plot(time, c_series, 'r-', linewidth=2, marker='^', markersize=4)
    axes[2].set_xlabel('时间 (h)', fontsize=12)
    axes[2].set_ylabel('波速 (m/s)', fontsize=12)
    axes[2].set_title('洪波波速的演变', fontsize=12, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_cascade_routing(time: np.ndarray, inflow: np.ndarray,
                         outflows: list, save_path: str = None):
    """绘制多河段串联演进图"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 入流
    ax.plot(time, inflow, 'k-', linewidth=2.5, label='初始入流', marker='o', markersize=5)
    
    # 各河段出流
    colors = ['blue', 'green', 'red', 'orange', 'purple']
    markers = ['s', '^', 'D', 'v', '<']
    
    for i, outflow in enumerate(outflows):
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]
        ax.plot(time, outflow, color=color, linewidth=2, 
                label=f'河段{i+1}出流', marker=marker, markersize=4, alpha=0.8)
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('流量 (m³/s)', fontsize=12)
    ax.set_title('多河段串联洪水演进', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def plot_attenuation_comparison(reach_lengths: list, attenuations: list,
                                save_path: str = None):
    """绘制削峰率对比图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(reach_lengths))
    width = 0.6
    
    bars = ax.bar(x, np.array(attenuations) * 100, width, 
                   color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E'],
                   alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('河段长度 (km)', fontsize=12)
    ax.set_ylabel('削峰率 (%)', fontsize=12)
    ax.set_title('不同河段长度的削峰效果', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{L/1000:.0f}' for L in reach_lengths])
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for bar, att in zip(bars, attenuations):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{att*100:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.close()


def main():
    """主函数"""
    print("\n" + "="*70)
    print("案例10：Muskingum-Cunge河道洪水演进方法")
    print("="*70 + "\n")
    
    # 创建输出目录
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # ========== 实验1：单河段演进 ==========
    print("实验1：单河段Muskingum-Cunge演进")
    print("-" * 70)
    
    # 河道参数
    B = 80.0      # 河宽 (m)
    n = 0.035     # 糙率
    S0 = 0.0005   # 坡度
    dx = 10000    # 河段长度 (m, 10km)
    dt = 1.0      # 时间步长 (h)
    
    print(f"河道参数:")
    print(f"  河宽: {B} m")
    print(f"  糙率: {n}")
    print(f"  坡度: {S0}")
    print(f"  河段长度: {dx/1000} km")
    print(f"  时间步长: {dt} h\n")
    
    # 生成洪水过程
    duration = 48
    inflow = generate_flood_hydrograph(duration=duration, peak_time=12, 
                                       peak_flow=1000, base_flow=50)
    
    # Muskingum-Cunge演进
    result = muskingum_cunge_routing(inflow, B, n, S0, dx, dt)
    
    print(f"演进结果:")
    print(f"  入流峰值: {result['peak_in']:.1f} m³/s")
    print(f"  出流峰值: {result['peak_out']:.1f} m³/s")
    print(f"  削峰率: {result['attenuation']:.2%}")
    print(f"  滞时: {result['lag']:.1f} h")
    print(f"  平均K: {np.mean(result['K_series']):.2f} h")
    print(f"  平均X: {np.mean(result['X_series']):.3f}")
    print(f"  平均波速: {np.mean(result['c_series']):.2f} m/s\n")
    
    # 可视化
    time = np.arange(duration) * dt
    plot_routing_comparison(time, inflow, result['outflow'],
                           title="Muskingum-Cunge演进结果",
                           save_path=f'{output_dir}/routing_comparison.png')
    
    plot_parameters_evolution(time, result['K_series'], result['X_series'],
                             result['c_series'],
                             save_path=f'{output_dir}/parameters_evolution.png')
    
    # ========== 实验2：多河段串联演进 ==========
    print("\n实验2：多河段串联演进")
    print("-" * 70)
    
    # 定义3个河段
    reach_params = [
        {'B': 100, 'n': 0.030, 'S0': 0.0008, 'dx': 8000},   # 河段1：上游
        {'B': 120, 'n': 0.035, 'S0': 0.0005, 'dx': 12000},  # 河段2：中游
        {'B': 150, 'n': 0.040, 'S0': 0.0003, 'dx': 15000},  # 河段3：下游
    ]
    
    cascade_result = cascade_routing(inflow, reach_params, dt)
    
    print(f"\n串联演进结果:")
    for i, outflow in enumerate(cascade_result['outflows']):
        peak = np.max(outflow)
        peak_idx = np.argmax(outflow)
        att = (result['peak_in'] - peak) / result['peak_in']
        print(f"  河段{i+1}出流: 峰值={peak:.1f} m³/s, "
              f"峰现时刻={peak_idx*dt:.0f}h, 削峰率={att:.2%}")
    
    plot_cascade_routing(time, inflow, cascade_result['outflows'],
                        save_path=f'{output_dir}/cascade_routing.png')
    
    # ========== 实验3：河段长度影响分析 ==========
    print("\n实验3：河段长度影响分析")
    print("-" * 70)
    
    lengths = [5000, 10000, 15000, 20000, 25000]  # m
    attenuations = []
    
    print(f"{'河段长度(km)':<15} {'削峰率':<10} {'滞时(h)':<10}")
    print("-" * 40)
    
    for dx_test in lengths:
        result_test = muskingum_cunge_routing(inflow, B, n, S0, dx_test, dt)
        attenuations.append(result_test['attenuation'])
        print(f"{dx_test/1000:<15.0f} {result_test['attenuation']:<10.2%} "
              f"{result_test['lag']:<10.1f}")
    
    plot_attenuation_comparison(lengths, attenuations,
                               save_path=f'{output_dir}/attenuation_comparison.png')
    
    # ========== 总结 ==========
    print("\n" + "="*70)
    print("Muskingum-Cunge演进结果统计")
    print("="*70)
    
    print(f"\n【单河段演进】")
    print(f"  河段长度: {dx/1000} km")
    print(f"  入流峰值: {result['peak_in']:.1f} m³/s")
    print(f"  出流峰值: {result['peak_out']:.1f} m³/s")
    print(f"  削峰率: {result['attenuation']:.2%}")
    print(f"  滞时: {result['lag']:.1f} h")
    
    print(f"\n【多河段串联】")
    total_length = sum(p['dx'] for p in reach_params) / 1000
    final_peak = np.max(cascade_result['final_outflow'])
    total_att = (result['peak_in'] - final_peak) / result['peak_in']
    print(f"  总长度: {total_length:.1f} km")
    print(f"  入流峰值: {result['peak_in']:.1f} m³/s")
    print(f"  最终峰值: {final_peak:.1f} m³/s")
    print(f"  总削峰率: {total_att:.2%}")
    
    print(f"\n所有图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
