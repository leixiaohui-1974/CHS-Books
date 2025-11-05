"""
案例2: 风切变与湍流

本案例演示:
1. 风切变模型（指数律、对数律）
2. 湍流强度计算与分类
3. 风廓线分析
4. 风轮等效风速

工程背景: 风力机选址高度优化
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加models路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from models.wind_resource import (
    WindShear,
    TurbulenceIntensity,
    WindProfile
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def demo_wind_shear_models():
    """演示1: 风切变模型对比"""
    print("=" * 60)
    print("演示1: 风切变模型（指数律 vs 对数律）")
    print("=" * 60)
    
    # 参考条件
    v_ref = 8.0  # 10m高度风速
    h_ref = 10.0  # 参考高度
    
    # 高度范围
    heights = np.linspace(10, 150, 100)
    
    # 创建风切变模型
    shear_power = WindShear(model="power_law")
    shear_log = WindShear(model="log_law")
    
    # 不同地形的指数律
    alphas = {
        '平坦地形': 0.14,
        '粗糙地形': 0.20,
        '城市': 0.30
    }
    
    print(f"\n参考条件: v_ref = {v_ref} m/s @ h_ref = {h_ref} m")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 不同α值的指数律
    ax = axes[0]
    for terrain, alpha in alphas.items():
        v = shear_power.power_law(v_ref, h_ref, heights, alpha)
        ax.plot(v, heights, label=f'{terrain} (α={alpha})', linewidth=2)
        
        # 打印典型高度风速
        v_80 = shear_power.power_law(v_ref, h_ref, np.array([80]), alpha)[0]
        v_120 = shear_power.power_law(v_ref, h_ref, np.array([120]), alpha)[0]
        print(f"\n{terrain}:")
        print(f"  80m:  {v_80:.2f} m/s (+{(v_80/v_ref-1)*100:.1f}%)")
        print(f"  120m: {v_120:.2f} m/s (+{(v_120/v_ref-1)*100:.1f}%)")
    
    ax.axhline(h_ref, color='gray', linestyle='--', alpha=0.5, label='参考高度')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('指数律风切变（不同地形）', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 图2: 对数律（不同粗糙度）
    ax = axes[1]
    z0_values = {
        '海面': 0.0002,
        '草地': 0.03,
        '农田': 0.10,
        '森林': 0.50
    }
    
    for terrain, z0 in z0_values.items():
        v = shear_log.log_law(v_ref, h_ref, heights, z0)
        ax.plot(v, heights, label=f'{terrain} (z₀={z0}m)', linewidth=2)
    
    ax.axhline(h_ref, color='gray', linestyle='--', alpha=0.5, label='参考高度')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('对数律风切变（不同粗糙度）', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case02_wind_shear_models.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case02_wind_shear_models.png")


def demo_model_comparison():
    """演示2: 指数律与对数律对比"""
    print("\n" + "=" * 60)
    print("演示2: 指数律与对数律模型对比")
    print("=" * 60)
    
    # 参考条件
    v_ref = 7.5
    h_ref = 10.0
    heights = np.linspace(10, 150, 100)
    
    # 模型
    shear_power = WindShear(model="power_law")
    shear_log = WindShear(model="log_law")
    
    # 计算
    v_power = shear_power.power_law(v_ref, h_ref, heights, alpha=0.14)
    v_log = shear_log.log_law(v_ref, h_ref, heights, z0=0.03)
    
    # 相对差异
    diff_percent = (v_power - v_log) / v_log * 100
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 风速廓线对比
    ax = axes[0]
    ax.plot(v_power, heights, 'b-', linewidth=2, label='指数律 (α=0.14)')
    ax.plot(v_log, heights, 'r--', linewidth=2, label='对数律 (z₀=0.03m)')
    ax.axhline(h_ref, color='gray', linestyle=':', alpha=0.5, label='参考高度')
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('两种模型对比', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 图2: 相对差异
    ax = axes[1]
    ax.plot(diff_percent, heights, 'g-', linewidth=2)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.axhline(80, color='orange', linestyle='--', alpha=0.7, label='典型轮毂高度')
    ax.set_xlabel('相对差异 (%)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('模型间差异', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    print(f"\n典型高度的差异:")
    for h in [50, 80, 100, 120]:
        idx = np.argmin(np.abs(heights - h))
        print(f"  {h}m: {diff_percent[idx]:+.2f}%")
    
    plt.tight_layout()
    plt.savefig('case02_model_comparison.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case02_model_comparison.png")


def demo_turbulence_intensity():
    """演示3: 湍流强度"""
    print("\n" + "=" * 60)
    print("演示3: 湍流强度分析")
    print("=" * 60)
    
    # 创建湍流模型
    turb = TurbulenceIntensity()
    
    # IEC标准湍流等级
    categories = ['A', 'B', 'C']
    v_range = np.linspace(4, 25, 100)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 图1: IEC标准湍流强度
    ax = axes[0, 0]
    for cat in categories:
        TI_values = [turb.iec_category(v, cat) for v in v_range]
        ax.plot(v_range, TI_values, linewidth=2, label=f'类别 {cat}')
    
    ax.set_xlabel('平均风速 (m/s)', fontsize=11)
    ax.set_ylabel('湍流强度', fontsize=11)
    ax.set_title('IEC 61400-1 湍流等级', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 打印典型值
    print("\nIEC标准湍流强度 (v=10 m/s):")
    for cat in categories:
        TI = turb.iec_category(10.0, cat)
        terrain = turb.classify_terrain(TI)
        print(f"  类别 {cat}: TI = {TI:.3f} - {terrain}")
    
    # 图2: 湍流风速时间序列
    ax = axes[0, 1]
    v_mean = 10.0
    TI = 0.15
    duration = 300  # 5分钟
    dt = 0.1
    
    t = np.arange(0, duration, dt)
    v_turb = turb.generate_turbulent_wind(v_mean, TI, duration, dt)
    
    ax.plot(t, v_turb, 'b-', linewidth=0.5, alpha=0.7)
    ax.axhline(v_mean, color='r', linestyle='--', linewidth=2, 
               label=f'平均: {v_mean} m/s')
    ax.axhline(v_mean + TI*v_mean, color='g', linestyle=':', 
               label=f'±1σ')
    ax.axhline(v_mean - TI*v_mean, color='g', linestyle=':')
    ax.set_xlabel('时间 (s)', fontsize=11)
    ax.set_ylabel('风速 (m/s)', fontsize=11)
    ax.set_title(f'湍流风速时间序列 (TI={TI})', fontsize=12, fontweight='bold')
    ax.set_xlim([0, 60])  # 只显示前60秒
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 计算实际湍流强度
    TI_actual = turb.calculate(v_turb)
    print(f"\n生成的湍流风速:")
    print(f"  设定TI: {TI:.3f}")
    print(f"  实际TI: {TI_actual:.3f}")
    print(f"  平均值: {np.mean(v_turb):.2f} m/s")
    print(f"  标准差: {np.std(v_turb):.2f} m/s")
    
    # 图3: Kaimal功率谱
    ax = axes[1, 0]
    freq = np.logspace(-3, 1, 200)  # 0.001 to 10 Hz
    sigma_v = TI * v_mean
    S = turb.kaimal_spectrum(freq, v_mean, sigma_v)
    
    ax.loglog(freq, S, 'b-', linewidth=2)
    ax.set_xlabel('频率 (Hz)', fontsize=11)
    ax.set_ylabel('功率谱密度 (m²/s²/Hz)', fontsize=11)
    ax.set_title('Kaimal湍流功率谱', fontsize=12, fontweight='bold')
    ax.grid(True, which='both', alpha=0.3)
    
    # 图4: 不同TI的影响
    ax = axes[1, 1]
    TI_levels = [0.10, 0.15, 0.20]
    colors = ['green', 'orange', 'red']
    
    for TI_level, color in zip(TI_levels, colors):
        v_turb_temp = turb.generate_turbulent_wind(v_mean, TI_level, 60, dt)
        t_temp = np.arange(0, 60, dt)
        ax.plot(t_temp, v_turb_temp, color=color, linewidth=0.5, 
                alpha=0.6, label=f'TI={TI_level}')
    
    ax.axhline(v_mean, color='black', linestyle='--', linewidth=2)
    ax.set_xlabel('时间 (s)', fontsize=11)
    ax.set_ylabel('风速 (m/s)', fontsize=11)
    ax.set_title('不同湍流强度对比', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case02_turbulence_intensity.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case02_turbulence_intensity.png")


def demo_wind_profile_application():
    """演示4: 风廓线工程应用"""
    print("\n" + "=" * 60)
    print("演示4: 风廓线在风力机中的应用")
    print("=" * 60)
    
    # 参考条件
    v_ref = 8.0
    h_ref = 10.0
    
    # 创建风廓线模型
    profile = WindProfile(v_ref, h_ref, shear_model="power_law")
    
    # 风力机参数
    turbines = {
        '小型机组': {'h_hub': 50, 'D': 40},
        '中型机组': {'h_hub': 80, 'D': 90},
        '大型机组': {'h_hub': 120, 'D': 150}
    }
    
    print(f"\n参考条件: v_ref = {v_ref} m/s @ h_ref = {h_ref} m")
    print("\n风力机轮毂高度风速:")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1: 风廓线与风力机
    ax = axes[0]
    heights = np.linspace(0, 200, 200)
    v_profile = profile.get_profile(heights, alpha=0.14)
    ax.plot(v_profile, heights, 'b-', linewidth=2, label='风速廓线')
    
    colors = ['green', 'orange', 'red']
    for (name, params), color in zip(turbines.items(), colors):
        h_hub = params['h_hub']
        D = params['D']
        R = D / 2
        
        # 轮毂高度风速
        v_hub = profile.hub_height_wind(h_hub, alpha=0.14)
        
        # 风轮等效风速
        v_eq = profile.rotor_equivalent_wind(h_hub, D, alpha=0.14)
        
        print(f"\n{name}:")
        print(f"  轮毂高度: {h_hub}m, 直径: {D}m")
        print(f"  轮毂风速: {v_hub:.2f} m/s")
        print(f"  等效风速: {v_eq:.2f} m/s")
        print(f"  风切变影响: {(v_eq/v_hub-1)*100:.2f}%")
        
        # 绘制风轮
        ax.plot(v_hub, h_hub, 'o', color=color, markersize=8)
        ax.plot([v_hub]*2, [h_hub-R, h_hub+R], color=color, 
                linewidth=4, alpha=0.5, label=name)
    
    ax.set_xlabel('风速 (m/s)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('风廓线与风力机尺寸', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 图2: 不同α值对轮毂风速的影响
    ax = axes[1]
    alpha_range = np.linspace(0.10, 0.35, 50)
    
    for name, params in turbines.items():
        h_hub = params['h_hub']
        v_hub_values = []
        
        for alpha in alpha_range:
            v_hub = profile.hub_height_wind(h_hub, alpha=alpha)
            v_hub_values.append(v_hub)
        
        ax.plot(alpha_range, v_hub_values, linewidth=2, label=name)
    
    ax.set_xlabel('风切变指数 α', fontsize=12)
    ax.set_ylabel('轮毂高度风速 (m/s)', fontsize=12)
    ax.set_title('风切变对不同机组的影响', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('case02_wind_profile_application.png', dpi=300, bbox_inches='tight')
    print("\n图表已保存: case02_wind_profile_application.png")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("案例2: 风切变与湍流")
    print("=" * 60)
    
    # 演示1: 风切变模型
    demo_wind_shear_models()
    
    # 演示2: 模型对比
    demo_model_comparison()
    
    # 演示3: 湍流强度
    demo_turbulence_intensity()
    
    # 演示4: 工程应用
    demo_wind_profile_application()
    
    print("\n" + "=" * 60)
    print("案例2 运行完成！")
    print("=" * 60)
    print("\n生成的图表:")
    print("  1. case02_wind_shear_models.png")
    print("  2. case02_model_comparison.png")
    print("  3. case02_turbulence_intensity.png")
    print("  4. case02_wind_profile_application.png")
    
    plt.show()


if __name__ == "__main__":
    main()
