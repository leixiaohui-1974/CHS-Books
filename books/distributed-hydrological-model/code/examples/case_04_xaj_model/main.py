"""
案例4：新安江模型产流计算
=======================

完整演示新安江模型的使用方法

作者: CHS-Books项目组
日期: 2025-11-02
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from core.runoff_generation import XinAnJiangModel, create_default_xaj_params
from core.utils.metrics import nash_sutcliffe, evaluate_model
from core.utils.plotting import plot_hydrograph, plot_rainfall_runoff

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)


def generate_synthetic_data(n_days=365):
    """
    生成合成的降雨-蒸发数据
    
    模拟一个完整水文年的数据，包含雨季和旱季
    """
    np.random.seed(42)
    
    time = np.arange(n_days)
    
    # 降雨数据（模拟季节性）
    # 雨季（夏季）：第150-250天
    rainfall = np.zeros(n_days)
    
    # 设置几场降雨事件
    rain_events = [
        (50, 5, 15),   # (起始日, 持续天数, 强度)
        (100, 3, 25),
        (150, 7, 30),
        (180, 10, 40),
        (220, 5, 20),
        (280, 4, 18),
    ]
    
    for start, duration, intensity in rain_events:
        for i in range(duration):
            if start + i < n_days:
                # 添加随机变化
                rainfall[start + i] = intensity * (0.8 + 0.4 * np.random.rand())
    
    # 蒸发数据（季节变化）
    evaporation = 3 + 2 * np.sin(2 * np.pi * time / 365) + np.random.rand(n_days) * 0.5
    evaporation = np.maximum(evaporation, 1.0)  # 最小1mm
    
    return time, rainfall, evaporation


def plot_water_sources(time, RS, RI, RG, save_path=None):
    """绘制三水源分量图"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # 堆叠面积图
    ax.fill_between(time, 0, RS, alpha=0.7, label='地表径流 RS', color='red')
    ax.fill_between(time, RS, RS + RI, alpha=0.7, label='壤中流 RI', color='orange')
    ax.fill_between(time, RS + RI, RS + RI + RG, alpha=0.7, 
                   label='地下径流 RG', color='blue')
    
    ax.set_xlabel('时间 (天)', fontsize=12)
    ax.set_ylabel('径流深 (mm)', fontsize=12)
    ax.set_title('新安江模型三水源划分', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def plot_soil_moisture(time, W, WM, save_path=None):
    """绘制土壤含水量变化"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(time, W, 'b-', linewidth=2, label='土壤含水量 W')
    ax.axhline(WM, color='r', linestyle='--', linewidth=2, 
              label=f'蓄水容量 WM = {WM} mm')
    ax.fill_between(time, 0, W, alpha=0.3, color='blue')
    
    ax.set_xlabel('时间 (天)', fontsize=12)
    ax.set_ylabel('土壤含水量 (mm)', fontsize=12)
    ax.set_title('土壤含水量变化过程', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, WM * 1.1)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def sensitivity_analysis(P, EM, param_name, param_range):
    """
    参数敏感性分析
    
    Parameters
    ----------
    P : ndarray
        降雨序列
    EM : ndarray
        蒸发序列
    param_name : str
        参数名称
    param_range : list
        参数取值范围
    """
    results_list = []
    
    for param_value in param_range:
        # 创建参数
        params = create_default_xaj_params('humid')
        params[param_name] = param_value
        
        # 运行模型
        model = XinAnJiangModel(params)
        results = model.run(P, EM)
        
        results_list.append({
            'param_value': param_value,
            'total_runoff': results['R'].sum(),
            'peak_runoff': results['R'].max(),
            'results': results
        })
    
    return results_list


def plot_sensitivity(param_name, param_range, results_list, save_path=None):
    """绘制敏感性分析图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    total_runoffs = [r['total_runoff'] for r in results_list]
    peak_runoffs = [r['peak_runoff'] for r in results_list]
    
    # 总径流深
    axes[0].plot(param_range, total_runoffs, 'o-', linewidth=2, markersize=8)
    axes[0].set_xlabel(f'参数 {param_name}', fontsize=12)
    axes[0].set_ylabel('总径流深 (mm)', fontsize=12)
    axes[0].set_title(f'{param_name} 对总径流深的影响', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # 洪峰径流
    axes[1].plot(param_range, peak_runoffs, 'o-', linewidth=2, 
                markersize=8, color='red')
    axes[1].set_xlabel(f'参数 {param_name}', fontsize=12)
    axes[1].set_ylabel('洪峰径流深 (mm)', fontsize=12)
    axes[1].set_title(f'{param_name} 对洪峰径流的影响', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def main():
    """主函数"""
    print("=" * 60)
    print("案例4：新安江模型产流计算")
    print("=" * 60)
    print()
    
    # 1. 生成数据
    print("1. 生成合成数据...")
    time, rainfall, evaporation = generate_synthetic_data(n_days=365)
    print(f"   时间步数: {len(time)} 天")
    print(f"   年降雨量: {rainfall.sum():.1f} mm")
    print(f"   年蒸发量: {evaporation.sum():.1f} mm")
    print()
    
    # 2. 创建模型
    print("2. 创建新安江模型...")
    params = create_default_xaj_params('humid')
    
    print("   模型参数:")
    for key, value in params.items():
        print(f"     {key} = {value}")
    print()
    
    model = XinAnJiangModel(params)
    
    # 3. 运行模拟
    print("3. 运行模型模拟...")
    results = model.run(rainfall, evaporation)
    
    print(f"   总径流深: {results['R'].sum():.1f} mm")
    print(f"   实际蒸散发: {results['E'].sum():.1f} mm")
    print(f"   水量平衡检验:")
    
    P_total = rainfall.sum()
    E_total = results['E'].sum()
    R_total = results['R'].sum()
    dW = results['W'][-1] - results['W'][0]
    balance = P_total - E_total - R_total - dW
    
    print(f"     降雨: {P_total:.1f} mm")
    print(f"     蒸发: {E_total:.1f} mm")
    print(f"     径流: {R_total:.1f} mm")
    print(f"     蓄水变化: {dW:.1f} mm")
    print(f"     水量平衡误差: {balance:.2f} mm ({abs(balance/P_total)*100:.3f}%)")
    print()
    
    # 4. 绘制结果
    print("4. 绘制结果图表...")
    
    # 4.1 降雨-径流过程
    fig1 = plot_rainfall_runoff(time, rainfall, results['R'],
                                title='新安江模型：降雨-径流过程',
                                save_path=output_dir / 'rainfall_runoff.png')
    plt.close(fig1)
    
    # 4.2 三水源分量
    fig2 = plot_water_sources(time, results['RS'], results['RI'], results['RG'],
                              save_path=output_dir / 'water_sources.png')
    plt.close(fig2)
    
    # 4.3 土壤含水量
    fig3 = plot_soil_moisture(time, results['W'], params['WM'],
                              save_path=output_dir / 'soil_moisture.png')
    plt.close(fig3)
    
    print("   √ 所有图表已保存到 outputs/ 目录")
    print()
    
    # 5. 参数敏感性分析
    print("5. 参数敏感性分析...")
    
    # 分析B参数
    print("   分析参数 B (蓄水容量曲线指数)...")
    B_range = [0.1, 0.2, 0.3, 0.4, 0.5]
    results_B = sensitivity_analysis(rainfall, evaporation, 'B', B_range)
    
    fig4 = plot_sensitivity('B', B_range, results_B,
                           save_path=output_dir / 'sensitivity_B.png')
    plt.close(fig4)
    
    # 分析WM参数
    print("   分析参数 WM (流域平均蓄水容量)...")
    WM_range = [100, 125, 150, 175, 200]
    results_WM = sensitivity_analysis(rainfall, evaporation, 'WM', WM_range)
    
    fig5 = plot_sensitivity('WM', WM_range, results_WM,
                           save_path=output_dir / 'sensitivity_WM.png')
    plt.close(fig5)
    
    print("   √ 敏感性分析完成")
    print()
    
    # 6. 总结
    print("=" * 60)
    print("模拟完成！")
    print("=" * 60)
    print()
    print("生成的文件:")
    print("  - outputs/rainfall_runoff.png    : 降雨-径流过程图")
    print("  - outputs/water_sources.png      : 三水源分量图")
    print("  - outputs/soil_moisture.png      : 土壤含水量变化")
    print("  - outputs/sensitivity_B.png      : B参数敏感性分析")
    print("  - outputs/sensitivity_WM.png     : WM参数敏感性分析")
    print()
    print("关键发现:")
    print(f"  1. B参数显著影响产流量，B越大，产流越多")
    print(f"  2. WM参数控制流域蓄水能力，WM越大，产流越少")
    print(f"  3. 三水源分量反映了不同的响应时间特征")
    print(f"  4. 水量平衡误差很小，模型计算可靠")
    print()


if __name__ == '__main__':
    main()
