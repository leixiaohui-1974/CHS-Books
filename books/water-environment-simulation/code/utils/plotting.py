"""
绘图工具
Plotting Utilities
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


def plot_1d_evolution(x, t, C, title='浓度演化', xlabel='位置 x (m)', 
                      ylabel='时间 t (s)', zlabel='浓度 C (mg/L)',
                      time_indices=None, figsize=(12, 5)):
    """
    绘制1D浓度随时间演化图
    
    参数:
        x: 空间坐标
        t: 时间坐标
        C: 浓度场 (nt, nx)
        title: 图标题
        time_indices: 要绘制的时间索引列表
        figsize: 图尺寸
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # 左图：选定时刻的浓度分布
    if time_indices is None:
        # 自动选择几个时刻
        nt = len(t)
        time_indices = [0, nt//4, nt//2, 3*nt//4, nt-1]
    
    for idx in time_indices:
        ax1.plot(x, C[idx, :], label=f't = {t[idx]:.1f} s')
    
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(zlabel)
    ax1.set_title(f'{title} - 不同时刻')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 右图：时空演化图
    T, X = np.meshgrid(t, x)
    contour = ax2.contourf(X, T, C.T, levels=20, cmap='viridis')
    ax2.set_xlabel(xlabel)
    ax2.set_ylabel(ylabel)
    ax2.set_title(f'{title} - 时空演化')
    plt.colorbar(contour, ax=ax2, label=zlabel)
    
    plt.tight_layout()
    return fig


def plot_2d_contour(X, Y, C, title='浓度分布', xlabel='x (m)', ylabel='y (m)',
                   figsize=(10, 8), time_indices=None, t=None):
    """
    绘制2D浓度分布等值线图
    
    参数:
        X, Y: 空间网格
        C: 浓度场 (nt, ny, nx) 或 (ny, nx)
        title: 图标题
        time_indices: 时间索引
        t: 时间坐标
        figsize: 图尺寸
    """
    if C.ndim == 3:
        # 3D数据，绘制多个时刻
        if time_indices is None:
            nt = C.shape[0]
            time_indices = [0, nt//2, nt-1]
        
        n_plots = len(time_indices)
        fig, axes = plt.subplots(1, n_plots, figsize=figsize)
        
        if n_plots == 1:
            axes = [axes]
        
        for i, idx in enumerate(time_indices):
            contour = axes[i].contourf(X, Y, C[idx, :, :], levels=20, cmap='viridis')
            axes[i].set_xlabel(xlabel)
            axes[i].set_ylabel(ylabel)
            time_str = f't = {t[idx]:.1f} s' if t is not None else f'step {idx}'
            axes[i].set_title(f'{title}\n{time_str}')
            plt.colorbar(contour, ax=axes[i])
    else:
        # 2D数据，绘制单个时刻
        fig, ax = plt.subplots(figsize=(8, 6))
        contour = ax.contourf(X, Y, C, levels=20, cmap='viridis')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        plt.colorbar(contour, ax=ax, label='浓度 C (mg/L)')
    
    plt.tight_layout()
    return fig


def plot_3d_surface(X, Y, C, title='浓度分布 3D', xlabel='x (m)', 
                   ylabel='y (m)', zlabel='C (mg/L)', figsize=(10, 8)):
    """
    绘制3D表面图
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, C, cmap='viridis', edgecolor='none', alpha=0.9)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    ax.set_title(title)
    
    fig.colorbar(surf, ax=ax, shrink=0.5)
    
    return fig


def compare_solutions(x, C_numerical, C_analytical, t=None, 
                     title='数值解与解析解对比', figsize=(10, 5)):
    """
    对比数值解和解析解
    
    参数:
        x: 空间坐标
        C_numerical: 数值解
        C_analytical: 解析解
        t: 时间（可选）
        title: 图标题
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # 左图：两种解的对比
    ax1.plot(x, C_numerical, 'b-', linewidth=2, label='数值解')
    ax1.plot(x, C_analytical, 'r--', linewidth=2, label='解析解')
    ax1.set_xlabel('位置 x (m)')
    ax1.set_ylabel('浓度 C (mg/L)')
    time_str = f' (t = {t:.1f} s)' if t is not None else ''
    ax1.set_title(f'{title}{time_str}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 右图：误差分布
    error = np.abs(C_numerical - C_analytical)
    ax2.plot(x, error, 'g-', linewidth=2)
    ax2.set_xlabel('位置 x (m)')
    ax2.set_ylabel('绝对误差 (mg/L)')
    ax2.set_title('误差分布')
    ax2.grid(True, alpha=0.3)
    
    # 显示统计信息
    max_error = np.max(error)
    mean_error = np.mean(error)
    ax2.text(0.05, 0.95, f'最大误差: {max_error:.2e}\n平均误差: {mean_error:.2e}',
             transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig


def plot_scheme_comparison(x, t, solutions, labels, title='数值格式对比',
                          figsize=(12, 8)):
    """
    对比不同数值格式的结果
    
    参数:
        x: 空间坐标
        t: 时间坐标
        solutions: 解的字典 {label: C}
        labels: 标签列表
        title: 图标题
    """
    n_schemes = len(solutions)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()
    
    # 选择几个时刻
    nt = len(t)
    time_indices = [nt//4, nt//2, 3*nt//4, nt-1]
    
    for i, idx in enumerate(time_indices):
        if i < len(axes):
            for label, C in solutions.items():
                axes[i].plot(x, C[idx, :], linewidth=2, label=label)
            
            axes[i].set_xlabel('位置 x (m)')
            axes[i].set_ylabel('浓度 C (mg/L)')
            axes[i].set_title(f't = {t[idx]:.1f} s')
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig


def plot_parameter_sensitivity(x, results, param_name, param_values,
                               title='参数敏感性分析', figsize=(10, 6)):
    """
    绘制参数敏感性分析结果
    
    参数:
        x: 空间坐标
        results: 结果列表
        param_name: 参数名称
        param_values: 参数值列表
        title: 图标题
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    for i, (result, value) in enumerate(zip(results, param_values)):
        ax.plot(x, result, linewidth=2, label=f'{param_name} = {value}')
    
    ax.set_xlabel('位置 x (m)')
    ax.set_ylabel('浓度 C (mg/L)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig
