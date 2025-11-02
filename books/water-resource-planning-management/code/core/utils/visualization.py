"""
可视化工具
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def plot_series(
    data: pd.Series,
    title: str = "时间序列图",
    xlabel: str = "时间",
    ylabel: str = "值",
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> None:
    """
    绘制时间序列图
    
    Parameters
    ----------
    data : pd.Series
        时间序列数据
    title : str, optional
        图标题
    xlabel : str, optional
        X轴标签
    ylabel : str, optional
        Y轴标签
    figsize : Tuple[int, int], optional
        图形大小
    save_path : str, optional
        保存路径，如果指定则保存图片
    
    Examples
    --------
    >>> dates = pd.date_range('2020-01-01', periods=365, freq='D')
    >>> data = pd.Series(np.random.randn(365).cumsum(), index=dates)
    >>> plot_series(data, title='年径流过程', ylabel='径流量 (m³/s)')
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.plot(data.index, data.values, linewidth=1.5)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存到: {save_path}")
    
    plt.show()


def plot_frequency_curve(
    empirical_data: np.ndarray,
    empirical_probs: np.ndarray,
    theoretical_probs: Optional[np.ndarray] = None,
    theoretical_values: Optional[np.ndarray] = None,
    title: str = "频率曲线",
    xlabel: str = "超过概率 (%)",
    ylabel: str = "设计值",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> None:
    """
    绘制频率曲线
    
    Parameters
    ----------
    empirical_data : np.ndarray
        经验数据点
    empirical_probs : np.ndarray
        经验超过概率
    theoretical_probs : np.ndarray, optional
        理论分布的概率点
    theoretical_values : np.ndarray, optional
        理论分布的设计值
    title : str, optional
        图标题
    xlabel : str, optional
        X轴标签
    ylabel : str, optional
        Y轴标签
    figsize : Tuple[int, int], optional
        图形大小
    save_path : str, optional
        保存路径
    
    Examples
    --------
    >>> # 经验点
    >>> data = np.array([100, 120, 90, 110, 95])
    >>> from core.utils.statistics import calculate_exceedance_probability
    >>> emp_data, emp_probs = calculate_exceedance_probability(data)
    >>> 
    >>> # 理论曲线
    >>> from core.utils.statistics import frequency_analysis
    >>> theo_probs, theo_values = frequency_analysis(data)
    >>> 
    >>> plot_frequency_curve(emp_data, emp_probs, theo_probs, theo_values)
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制经验点
    ax.scatter(empirical_probs * 100, empirical_data, 
               s=50, c='red', marker='o', label='经验点', zorder=3)
    
    # 绘制理论曲线
    if theoretical_probs is not None and theoretical_values is not None:
        ax.plot(theoretical_probs * 100, theoretical_values,
                linewidth=2, c='blue', label='理论曲线', zorder=2)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # 设置X轴为对数刻度（常用于频率曲线）
    ax.set_xscale('log')
    ax.set_xlim([0.1, 99.9])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存到: {save_path}")
    
    plt.show()


def plot_comparison(
    data_dict: dict,
    title: str = "对比图",
    xlabel: str = "X轴",
    ylabel: str = "Y轴",
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> None:
    """
    绘制多条曲线对比图
    
    Parameters
    ----------
    data_dict : dict
        数据字典，格式为 {标签: Series或array}
    title : str, optional
        图标题
    xlabel : str, optional
        X轴标签
    ylabel : str, optional
        Y轴标签
    figsize : Tuple[int, int], optional
        图形大小
    save_path : str, optional
        保存路径
    
    Examples
    --------
    >>> data1 = pd.Series(np.random.randn(100).cumsum())
    >>> data2 = pd.Series(np.random.randn(100).cumsum())
    >>> plot_comparison({'方案1': data1, '方案2': data2}, title='方案对比')
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    for label, data in data_dict.items():
        if isinstance(data, pd.Series):
            ax.plot(data.index, data.values, label=label, linewidth=1.5)
        else:
            ax.plot(data, label=label, linewidth=1.5)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存到: {save_path}")
    
    plt.show()


def plot_bar_chart(
    categories: List[str],
    values: List[float],
    title: str = "柱状图",
    xlabel: str = "类别",
    ylabel: str = "值",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> None:
    """
    绘制柱状图
    
    Parameters
    ----------
    categories : List[str]
        类别标签
    values : List[float]
        对应的值
    title : str, optional
        图标题
    xlabel : str, optional
        X轴标签
    ylabel : str, optional
        Y轴标签
    figsize : Tuple[int, int], optional
        图形大小
    save_path : str, optional
        保存路径
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.bar(categories, values, color='steelblue', alpha=0.7)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存到: {save_path}")
    
    plt.show()
