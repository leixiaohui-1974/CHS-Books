"""
plots.py - 绘图功能
===================

提供各种地下水模拟结果的绘图功能。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from typing import Optional, List, Tuple


def plot_1d_head(
    x: np.ndarray,
    h: np.ndarray,
    title: str = "一维地下水水头分布",
    xlabel: str = "距离 (m)",
    ylabel: str = "水头 (m)",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    绘制一维水头分布
    
    参数：
        x: 位置坐标
        h: 水头值
        title: 图标题
        xlabel: x轴标签
        ylabel: y轴标签
        save_path: 保存路径（如果提供）
    
    返回：
        fig: matplotlib图形对象
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x, h, 'b-', linewidth=2, label='水头分布')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_2d_head(
    X: np.ndarray,
    Y: np.ndarray,
    h: np.ndarray,
    title: str = "二维地下水水头分布",
    xlabel: str = "x (m)",
    ylabel: str = "y (m)",
    contour_levels: int = 20,
    cmap: str = 'viridis',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    绘制二维水头等值线图
    
    参数：
        X: x坐标网格
        Y: y坐标网格
        h: 水头分布
        title: 图标题
        xlabel: x轴标签
        ylabel: y轴标签
        contour_levels: 等值线数量
        cmap: 颜色映射
        save_path: 保存路径
    
    返回：
        fig: matplotlib图形对象
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 填充等值线
    contourf = ax.contourf(X, Y, h, levels=contour_levels, cmap=cmap)
    # 等值线
    contour = ax.contour(X, Y, h, levels=contour_levels, colors='black',
                         linewidths=0.5, alpha=0.4)
    ax.clabel(contour, inline=True, fontsize=8, fmt='%.1f')
    
    # 颜色条
    cbar = plt.colorbar(contourf, ax=ax, label='水头 (m)')
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_2d_velocity(
    X: np.ndarray,
    Y: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    h: Optional[np.ndarray] = None,
    title: str = "地下水流速场",
    skip: int = 5,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    绘制二维流速场（矢量图）
    
    参数：
        X: x坐标网格
        Y: y坐标网格
        vx: x方向速度
        vy: y方向速度
        h: 水头分布（可选，作为背景）
        title: 图标题
        skip: 矢量间隔
        save_path: 保存路径
    
    返回：
        fig: matplotlib图形对象
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 如果提供了水头，绘制为背景
    if h is not None:
        contourf = ax.contourf(X, Y, h, levels=20, cmap='Blues', alpha=0.5)
        plt.colorbar(contourf, ax=ax, label='水头 (m)')
    
    # 计算速度大小
    # 注意vx和vy的尺寸可能与X, Y不同
    # 需要插值到单元中心
    ny, nx = X.shape
    
    # 创建速度场用于绘制（插值到网格中心）
    vx_plot = np.zeros((ny, nx))
    vy_plot = np.zeros((ny, nx))
    
    # 简单平均插值
    vx_plot[:, :-1] = vx
    vx_plot[:, -1] = vx[:, -1]
    
    vy_plot[:-1, :] = vy
    vy_plot[-1, :] = vy[-1, :]
    
    # 绘制矢量场
    quiver = ax.quiver(
        X[::skip, ::skip], Y[::skip, ::skip],
        vx_plot[::skip, ::skip], vy_plot[::skip, ::skip],
        scale=None, scale_units='xy', angles='xy',
        color='red', width=0.003
    )
    
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('y (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_transient_animation(
    X: np.ndarray,
    Y: np.ndarray,
    h_history: List[np.ndarray],
    dt: float,
    title: str = "瞬态地下水流动",
    save_path: Optional[str] = None,
    fps: int = 10
) -> animation.FuncAnimation:
    """
    创建瞬态模拟的动画
    
    参数：
        X: x坐标网格
        Y: y坐标网格
        h_history: 各时间步的水头分布列表
        dt: 时间步长
        title: 图标题
        save_path: 保存路径（.gif或.mp4）
        fps: 帧率
    
    返回：
        anim: matplotlib动画对象
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 确定颜色范围
    vmin = min(h.min() for h in h_history)
    vmax = max(h.max() for h in h_history)
    
    # 初始化
    contourf = ax.contourf(X, Y, h_history[0], levels=20,
                           cmap='viridis', vmin=vmin, vmax=vmax)
    cbar = plt.colorbar(contourf, ax=ax, label='水头 (m)')
    
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes,
                        fontsize=12, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('y (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    
    def animate(frame):
        ax.clear()
        contourf = ax.contourf(X, Y, h_history[frame], levels=20,
                               cmap='viridis', vmin=vmin, vmax=vmax)
        
        time = frame * dt
        time_text = ax.text(0.02, 0.95, f'时间: {time:.1f} day',
                           transform=ax.transAxes, fontsize=12,
                           verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('x (m)', fontsize=12)
        ax.set_ylabel('y (m)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_aspect('equal')
        
        return contourf,
    
    anim = animation.FuncAnimation(
        fig, animate, frames=len(h_history),
        interval=1000/fps, blit=False
    )
    
    if save_path:
        if save_path.endswith('.gif'):
            anim.save(save_path, writer='pillow', fps=fps)
        elif save_path.endswith('.mp4'):
            anim.save(save_path, writer='ffmpeg', fps=fps)
    
    return anim


def plot_comparison(
    x: np.ndarray,
    h_numerical: np.ndarray,
    h_analytical: Optional[np.ndarray] = None,
    title: str = "数值解与解析解对比",
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    绘制数值解与解析解的对比
    
    参数：
        x: 位置坐标
        h_numerical: 数值解
        h_analytical: 解析解（可选）
        title: 图标题
        save_path: 保存路径
    
    返回：
        fig: matplotlib图形对象
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x, h_numerical, 'b-', linewidth=2, label='数值解', marker='o',
            markersize=4, markevery=5)
    
    if h_analytical is not None:
        ax.plot(x, h_analytical, 'r--', linewidth=2, label='解析解')
        
        # 计算误差
        error = np.abs(h_numerical - h_analytical)
        rmse = np.sqrt(np.mean(error**2))
        max_error = np.max(error)
        
        # 在图上显示误差信息
        error_text = f'RMSE: {rmse:.4f} m\nMax Error: {max_error:.4f} m'
        ax.text(0.02, 0.98, error_text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('距离 (m)', fontsize=12)
    ax.set_ylabel('水头 (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
