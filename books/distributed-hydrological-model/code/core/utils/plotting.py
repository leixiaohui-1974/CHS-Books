"""
绘图工具模块
===========

提供常用的水文图表绘制函数
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure


def plot_hydrograph(time, observed=None, simulated=None, 
                   xlabel='Time', ylabel='Discharge (m³/s)',
                   title='Hydrograph', figsize=(12, 6),
                   save_path=None):
    """
    绘制水文过程线
    
    Parameters
    ----------
    time : array_like
        时间序列
    observed : array_like, optional
        观测流量
    simulated : array_like, optional
        模拟流量
    xlabel : str
        x轴标签
    ylabel : str
        y轴标签
    title : str
        图表标题
    figsize : tuple
        图表大小
    save_path : str, optional
        保存路径
        
    Returns
    -------
    fig : Figure
        matplotlib图表对象
        
    Examples
    --------
    >>> import numpy as np
    >>> t = np.arange(100)
    >>> obs = np.random.rand(100) * 10
    >>> sim = obs + np.random.randn(100) * 0.5
    >>> fig = plot_hydrograph(t, obs, sim, title='Test Hydrograph')
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if observed is not None:
        ax.plot(time, observed, 'k-', linewidth=2, label='Observed', zorder=2)
    
    if simulated is not None:
        ax.plot(time, simulated, 'r--', linewidth=1.5, label='Simulated', zorder=1)
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='best')
    
    # 自动格式化x轴（如果是日期类型）
    try:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    except:
        pass
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {save_path}")
    
    return fig


def plot_scatter(observed, simulated, 
                xlabel='Observed', ylabel='Simulated',
                title='Scatter Plot', figsize=(8, 8),
                show_1to1=True, show_stats=True,
                save_path=None):
    """
    绘制散点图（观测值 vs 模拟值）
    
    Parameters
    ----------
    observed : array_like
        观测值
    simulated : array_like
        模拟值
    xlabel : str
        x轴标签
    ylabel : str
        y轴标签
    title : str
        图表标题
    figsize : tuple
        图表大小
    show_1to1 : bool
        是否显示1:1线
    show_stats : bool
        是否显示统计指标
    save_path : str, optional
        保存路径
        
    Returns
    -------
    fig : Figure
        matplotlib图表对象
    """
    from .metrics import nash_sutcliffe, correlation_coefficient
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 移除NaN值
    mask = ~(np.isnan(observed) | np.isnan(simulated))
    obs_clean = observed[mask]
    sim_clean = simulated[mask]
    
    # 绘制散点
    ax.scatter(obs_clean, sim_clean, alpha=0.5, s=30, color='blue', edgecolors='black', linewidths=0.5)
    
    # 1:1线
    if show_1to1:
        min_val = min(obs_clean.min(), sim_clean.min())
        max_val = max(obs_clean.max(), sim_clean.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='1:1 Line')
    
    # 显示统计指标
    if show_stats:
        nse = nash_sutcliffe(obs_clean, sim_clean)
        r = correlation_coefficient(obs_clean, sim_clean)
        
        stats_text = f'NSE = {nse:.4f}\nR = {r:.4f}'
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
               fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    if show_1to1:
        ax.legend(fontsize=10)
    
    # 设置坐标轴范围相等
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {save_path}")
    
    return fig


def plot_rainfall_runoff(time, rainfall, runoff, 
                         title='Rainfall-Runoff Process',
                         figsize=(12, 8), save_path=None):
    """
    绘制降雨径流双轴图
    
    Parameters
    ----------
    time : array_like
        时间序列
    rainfall : array_like
        降雨过程 (mm)
    runoff : array_like
        径流过程 (m³/s or mm)
    title : str
        图表标题
    figsize : tuple
        图表大小
    save_path : str, optional
        保存路径
        
    Returns
    -------
    fig : Figure
        matplotlib图表对象
    """
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # 降雨柱状图（倒置）
    ax1.bar(time, rainfall, width=0.8, color='skyblue', alpha=0.7, label='Rainfall')
    ax1.set_ylabel('Rainfall (mm)', fontsize=12, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.invert_yaxis()  # 倒置y轴
    ax1.set_ylim(max(rainfall) * 1.2, 0)  # 留出空间
    
    # 径流过程线
    ax2 = ax1.twinx()
    ax2.plot(time, runoff, 'r-', linewidth=2, label='Runoff')
    ax2.set_ylabel('Runoff (m³/s)', fontsize=12, color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(0, max(runoff) * 1.2)
    
    ax1.set_xlabel('Time', fontsize=12)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {save_path}")
    
    return fig
