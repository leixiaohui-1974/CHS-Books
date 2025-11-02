"""
案例3：IDW与Kriging空间插值对比
===============================

对比分析IDW和Kriging两种高级插值方法

作者: CHS-Books项目组
日期: 2025-11-02
"""

import sys
sys.path.insert(0, '../../..')

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import time

from code.core.interpolation import (
    inverse_distance_weighting, ordinary_kriging,
    experimental_variogram, cross_validation_idw
)
from code.core.interpolation.idw import idw_grid
from code.core.utils.metrics import rmse, correlation_coefficient

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)


def generate_rainfall_field(n_stations=20, basin_size=30):
    """
    生成模拟的降雨场数据
    
    Parameters
    ----------
    n_stations : int
        站点数量
    basin_size : float
        流域大小 (km)
        
    Returns
    -------
    stations_xy : ndarray
        站点坐标
    rainfall : ndarray
        各站点降雨量
    true_function : function
        真实降雨场函数（用于验证）
    """
    np.random.seed(42)
    
    # 生成站点坐标（随机分布）
    stations_xy = np.random.rand(n_stations, 2) * basin_size
    
    # 定义真实降雨场（高斯+线性趋势）
    def true_function(x, y):
        # 降雨中心
        center1 = np.array([10, 15])
        center2 = np.array([20, 10])
        
        # 高斯成分
        r1 = np.sqrt((x - center1[0])**2 + (y - center1[1])**2)
        r2 = np.sqrt((x - center2[0])**2 + (y - center2[1])**2)
        gaussian = 50 * np.exp(-r1**2 / 50) + 30 * np.exp(-r2**2 / 80)
        
        # 线性趋势
        trend = 20 + 0.3 * x - 0.2 * y
        
        return gaussian + trend
    
    # 生成观测值（加入观测误差）
    rainfall = np.array([
        true_function(xy[0], xy[1]) + np.random.normal(0, 2)
        for xy in stations_xy
    ])
    rainfall = np.maximum(rainfall, 10)  # 最小10mm
    
    return stations_xy, rainfall, true_function


def plot_interpolation_result(grid_x, grid_y, grid_z, stations_xy, rainfall,
                              title, save_path=None):
    """绘制插值结果"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 等值线填充图
    contour = ax.contourf(grid_x, grid_y, grid_z, levels=20, cmap='RdYlBu_r')
    
    # 等值线
    cs = ax.contour(grid_x, grid_y, grid_z, levels=10, colors='black',
                   linewidths=0.5, alpha=0.4)
    ax.clabel(cs, inline=True, fontsize=8)
    
    # 观测站点
    scatter = ax.scatter(stations_xy[:, 0], stations_xy[:, 1],
                        c=rainfall, s=200, cmap='RdYlBu_r',
                        edgecolors='black', linewidths=2, zorder=5,
                        vmin=grid_z.min(), vmax=grid_z.max())
    
    # 颜色条
    cbar = plt.colorbar(contour, ax=ax, label='降雨量 (mm)')
    cbar.ax.tick_params(labelsize=11)
    
    ax.set_xlabel('X坐标 (km)', fontsize=13)
    ax.set_ylabel('Y坐标 (km)', fontsize=13)
    ax.set_title(title, fontsize=15, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def plot_comparison(grid_x, grid_y, idw_result, kriging_result,
                   stations_xy, rainfall, save_path=None):
    """对比两种方法"""
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # IDW结果
    im1 = axes[0].contourf(grid_x, grid_y, idw_result, levels=20, cmap='RdYlBu_r')
    axes[0].scatter(stations_xy[:, 0], stations_xy[:, 1], c='black', 
                   s=50, edgecolors='white', linewidths=1, zorder=5)
    axes[0].set_title('IDW插值 (power=2)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('X (km)', fontsize=12)
    axes[0].set_ylabel('Y (km)', fontsize=12)
    axes[0].set_aspect('equal')
    plt.colorbar(im1, ax=axes[0], label='降雨量 (mm)')
    
    # Kriging结果
    im2 = axes[1].contourf(grid_x, grid_y, kriging_result, levels=20, cmap='RdYlBu_r')
    axes[1].scatter(stations_xy[:, 0], stations_xy[:, 1], c='black',
                   s=50, edgecolors='white', linewidths=1, zorder=5)
    axes[1].set_title('Kriging插值 (球状模型)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('X (km)', fontsize=12)
    axes[1].set_aspect('equal')
    plt.colorbar(im2, ax=axes[1], label='降雨量 (mm)')
    
    # 差异图
    diff = idw_result - kriging_result
    im3 = axes[2].contourf(grid_x, grid_y, diff, levels=20, cmap='RdBu_r',
                          vmin=-np.max(np.abs(diff)), vmax=np.max(np.abs(diff)))
    axes[2].scatter(stations_xy[:, 0], stations_xy[:, 1], c='black',
                   s=50, edgecolors='white', linewidths=1, zorder=5)
    axes[2].set_title('差异 (IDW - Kriging)', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('X (km)', fontsize=12)
    axes[2].set_aspect('equal')
    cbar = plt.colorbar(im3, ax=axes[2], label='差异 (mm)')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def plot_variogram(stations_xy, rainfall, save_path=None):
    """绘制变异函数图"""
    # 计算实验变异函数
    lag_distances, semivariances = experimental_variogram(stations_xy, rainfall, n_lags=15)
    
    # 拟合理论模型（简化：直接使用参数）
    max_dist = np.max(lag_distances)
    semivar_max = np.max(semivariances)
    
    # 球状模型参数
    nugget = semivar_max * 0.05
    sill = semivar_max * 1.1
    range_param = max_dist * 0.4
    
    # 理论模型
    h_theory = np.linspace(0, max_dist, 100)
    from code.core.interpolation.kriging import spherical_variogram
    gamma_theory = spherical_variogram(h_theory, nugget, sill, range_param)
    
    # 绘图
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 实验变异函数
    ax.scatter(lag_distances, semivariances, s=100, c='blue', 
              edgecolors='black', linewidths=2, label='实验变异函数', zorder=5)
    
    # 理论模型
    ax.plot(h_theory, gamma_theory, 'r-', linewidth=3, 
           label=f'球状模型\n(nugget={nugget:.1f}, sill={sill:.1f}, range={range_param:.1f})')
    
    # 标注关键点
    ax.axhline(sill, color='green', linestyle='--', linewidth=2, alpha=0.7, label='基台值 (Sill)')
    ax.axvline(range_param, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='变程 (Range)')
    ax.axhline(nugget, color='purple', linestyle='--', linewidth=2, alpha=0.7, label='块金效应 (Nugget)')
    
    ax.set_xlabel('滞后距离 (km)', fontsize=13)
    ax.set_ylabel('半方差', fontsize=13)
    ax.set_title('变异函数分析', fontsize=15, fontweight='bold')
    ax.legend(fontsize=11, loc='lower right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def cross_validation_comparison(stations_xy, rainfall):
    """交叉验证对比"""
    n = len(stations_xy)
    
    # IDW交叉验证
    idw_predictions = []
    idw_observed = []
    
    for i in range(n):
        # 留一法
        train_xy = np.delete(stations_xy, i, axis=0)
        train_values = np.delete(rainfall, i)
        test_xy = stations_xy[i:i+1]
        test_value = rainfall[i]
        
        # IDW预测
        pred = inverse_distance_weighting(train_xy, train_values, test_xy, power=2)
        idw_predictions.append(pred[0])
        idw_observed.append(test_value)
    
    idw_predictions = np.array(idw_predictions)
    idw_observed = np.array(idw_observed)
    
    # Kriging交叉验证
    kriging_predictions = []
    kriging_observed = []
    
    for i in range(n):
        train_xy = np.delete(stations_xy, i, axis=0)
        train_values = np.delete(rainfall, i)
        test_xy = stations_xy[i:i+1]
        test_value = rainfall[i]
        
        # Kriging预测
        pred, _ = ordinary_kriging(train_xy, train_values, test_xy)
        kriging_predictions.append(pred[0])
        kriging_observed.append(test_value)
    
    kriging_predictions = np.array(kriging_predictions)
    kriging_observed = np.array(kriging_observed)
    
    return {
        'idw': {'observed': idw_observed, 'predicted': idw_predictions},
        'kriging': {'observed': kriging_observed, 'predicted': kriging_predictions}
    }


def plot_cross_validation(cv_results, save_path=None):
    """绘制交叉验证结果"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # IDW
    idw_obs = cv_results['idw']['observed']
    idw_pred = cv_results['idw']['predicted']
    idw_rmse = rmse(idw_obs, idw_pred)
    idw_r = correlation_coefficient(idw_obs, idw_pred)
    
    axes[0].scatter(idw_obs, idw_pred, s=100, alpha=0.6, edgecolors='black', linewidths=1.5)
    min_val = min(idw_obs.min(), idw_pred.min())
    max_val = max(idw_obs.max(), idw_pred.max())
    axes[0].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='1:1线')
    axes[0].set_xlabel('观测值 (mm)', fontsize=13)
    axes[0].set_ylabel('预测值 (mm)', fontsize=13)
    axes[0].set_title(f'IDW交叉验证\nRMSE={idw_rmse:.2f} mm, R={idw_r:.3f}',
                     fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_aspect('equal')
    
    # Kriging
    kriging_obs = cv_results['kriging']['observed']
    kriging_pred = cv_results['kriging']['predicted']
    kriging_rmse = rmse(kriging_obs, kriging_pred)
    kriging_r = correlation_coefficient(kriging_obs, kriging_pred)
    
    axes[1].scatter(kriging_obs, kriging_pred, s=100, alpha=0.6, edgecolors='black', linewidths=1.5)
    min_val = min(kriging_obs.min(), kriging_pred.min())
    max_val = max(kriging_obs.max(), kriging_pred.max())
    axes[1].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='1:1线')
    axes[1].set_xlabel('观测值 (mm)', fontsize=13)
    axes[1].set_ylabel('预测值 (mm)', fontsize=13)
    axes[1].set_title(f'Kriging交叉验证\nRMSE={kriging_rmse:.2f} mm, R={kriging_r:.3f}',
                     fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_aspect('equal')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig, {'idw_rmse': idw_rmse, 'idw_r': idw_r,
                'kriging_rmse': kriging_rmse, 'kriging_r': kriging_r}


def main():
    """主函数"""
    print("=" * 70)
    print("案例3：IDW与Kriging空间插值对比")
    print("=" * 70)
    print()
    
    basin_size = 30  # km
    n_stations = 20
    
    # 1. 生成数据
    print("1. 生成模拟降雨场数据...")
    stations_xy, rainfall, true_function = generate_rainfall_field(n_stations, basin_size)
    print(f"   站点数量: {n_stations}")
    print(f"   流域大小: {basin_size} × {basin_size} km²")
    print(f"   降雨范围: {rainfall.min():.1f} - {rainfall.max():.1f} mm")
    print()
    
    # 2. 创建插值网格
    print("2. 创建插值网格...")
    grid_resolution = 100
    x = np.linspace(0, basin_size, grid_resolution)
    y = np.linspace(0, basin_size, grid_resolution)
    grid_x, grid_y = np.meshgrid(x, y)
    print(f"   网格分辨率: {grid_resolution} × {grid_resolution}")
    print()
    
    # 3. IDW插值
    print("3. 执行IDW插值...")
    start_time = time.time()
    idw_result = idw_grid(stations_xy, rainfall, grid_x, grid_y, power=2)
    idw_time = time.time() - start_time
    print(f"   计算时间: {idw_time:.3f} 秒")
    print(f"   结果范围: {idw_result.min():.1f} - {idw_result.max():.1f} mm")
    
    # 绘制IDW结果
    fig1 = plot_interpolation_result(grid_x, grid_y, idw_result, stations_xy, rainfall,
                                     'IDW插值结果 (power=2)',
                                     save_path=output_dir / 'idw_interpolation.png')
    plt.close(fig1)
    print()
    
    # 4. Kriging插值
    print("4. 执行Kriging插值...")
    start_time = time.time()
    target_points = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    kriging_result_flat, kriging_var = ordinary_kriging(stations_xy, rainfall, target_points)
    kriging_result = kriging_result_flat.reshape(grid_x.shape)
    kriging_time = time.time() - start_time
    print(f"   计算时间: {kriging_time:.3f} 秒")
    print(f"   结果范围: {kriging_result.min():.1f} - {kriging_result.max():.1f} mm")
    
    # 绘制Kriging结果
    fig2 = plot_interpolation_result(grid_x, grid_y, kriging_result, stations_xy, rainfall,
                                     'Kriging插值结果 (球状模型)',
                                     save_path=output_dir / 'kriging_interpolation.png')
    plt.close(fig2)
    print()
    
    # 5. 方法对比
    print("5. 对比两种方法...")
    fig3 = plot_comparison(grid_x, grid_y, idw_result, kriging_result,
                          stations_xy, rainfall,
                          save_path=output_dir / 'comparison.png')
    plt.close(fig3)
    
    mean_diff = np.mean(np.abs(idw_result - kriging_result))
    print(f"   平均绝对差异: {mean_diff:.2f} mm")
    print()
    
    # 6. 变异函数分析
    print("6. 变异函数分析...")
    fig4 = plot_variogram(stations_xy, rainfall,
                         save_path=output_dir / 'variogram.png')
    plt.close(fig4)
    print("   变异函数图已生成")
    print()
    
    # 7. 交叉验证
    print("7. 交叉验证（留一法）...")
    cv_results = cross_validation_comparison(stations_xy, rainfall)
    fig5, cv_metrics = plot_cross_validation(cv_results,
                                             save_path=output_dir / 'cross_validation.png')
    plt.close(fig5)
    
    print(f"   IDW - RMSE: {cv_metrics['idw_rmse']:.2f} mm, R: {cv_metrics['idw_r']:.3f}")
    print(f"   Kriging - RMSE: {cv_metrics['kriging_rmse']:.2f} mm, R: {cv_metrics['kriging_r']:.3f}")
    print()
    
    # 8. 总结
    print("=" * 70)
    print("分析完成！")
    print("=" * 70)
    print()
    print("生成的文件:")
    print("  - outputs/idw_interpolation.png     : IDW插值结果")
    print("  - outputs/kriging_interpolation.png : Kriging插值结果")
    print("  - outputs/comparison.png            : 方法对比")
    print("  - outputs/variogram.png             : 变异函数分析")
    print("  - outputs/cross_validation.png      : 交叉验证")
    print()
    print("性能对比:")
    print(f"  计算时间: IDW {idw_time:.3f}s vs Kriging {kriging_time:.3f}s")
    print(f"            (Kriging慢{kriging_time/idw_time:.1f}倍)")
    print()
    print(f"  插值精度: IDW RMSE={cv_metrics['idw_rmse']:.2f} mm")
    print(f"            Kriging RMSE={cv_metrics['kriging_rmse']:.2f} mm")
    print(f"            (Kriging提升{(1-cv_metrics['kriging_rmse']/cv_metrics['idw_rmse'])*100:.1f}%)")
    print()
    print("结论:")
    print("  1. Kriging插值精度更高，但计算时间较长")
    print("  2. IDW计算快速，适合实时应用")
    print("  3. Kriging提供不确定性估计，更适合科研")
    print("  4. 实际应用中需根据需求选择合适方法")
    print()


if __name__ == '__main__':
    main()
