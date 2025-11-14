"""
案例12：河口盐水入侵与水质模拟
Estuary Saltwater Intrusion and Water Quality Simulation

演示：
1. 盐度场时间演化
2. 盐水入侵长度计算
3. 取水口风险评估
4. 不同流量情景对比
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.estuary import (EstuarySaltIntrusion1D, calculate_stratification_parameter,
                             calculate_salt_wedge_length, estimate_intake_risk)


def main():
    """主函数"""
    print("=" * 70)
    print("案例12：河口盐水入侵与水质模拟")
    print("=" * 70)
    print()
    
    # 参数设置
    L = 30000       # 河口长度 (m)
    nx = 150        # 节点数
    H = 5           # 水深 (m)
    tidal_range = 3 # 潮差 (m)
    tidal_period = 12.4 * 3600  # 潮汐周期 (s)
    
    # 不同流量情景
    Q_scenarios = {
        '丰水期': 200,
        '平水期': 100,
        '枯水期': 50
    }
    
    print("河口参数:")
    print(f"  长度: {L/1000} km")
    print(f"  水深: {H} m")
    print(f"  潮差: {tidal_range} m")
    print(f"  潮汐周期: {tidal_period/3600:.1f} hour")
    print()
    
    # 任务1-3：不同流量情景模拟
    results = {}
    
    for scenario_name, Q in Q_scenarios.items():
        print(f"\n{'='*70}")
        print(f"情景：{scenario_name}（Q = {Q} m³/s）")
        print('='*70)
        
        # 创建模型
        model = EstuarySaltIntrusion1D(L, nx, H, Q, tidal_range, tidal_period)
        
        # 设置初始盐度
        model.set_initial_salinity(S_sea=30, S_river=0)
        
        # 时间演化（模拟1个潮周期）
        # 稳定性条件: dt ≤ dx²/(2*K_x) ≈ 201²/(2*100) ≈ 202s
        dt = 150  # 时间步长 2.5分钟（满足稳定性条件）
        n_steps = int(tidal_period / dt)
        
        # 记录不同潮时的盐度
        S_high_tide = None
        S_low_tide = None
        
        for step in range(n_steps):
            t = step * dt
            model.solve_salinity_transport(t, dt)
            
            # 记录涨潮高潮位（1/4周期）
            if step == n_steps // 4:
                S_high_tide = model.S.copy()
            
            # 记录退潮低潮位（3/4周期）
            if step == 3 * n_steps // 4:
                S_low_tide = model.S.copy()
        
        # 计算入侵长度
        L_intrusion = model.calculate_intrusion_length(S_threshold=2.0)
        
        # 取水口位置（20 km）
        x_intake = 20000
        ix_intake = int(x_intake / L * nx)
        
        # 评估风险
        risk_level, is_safe = estimate_intake_risk(model.S, ix_intake, S_max=0.5)
        
        # 保存结果
        results[scenario_name] = {
            'x': model.x,
            'S': model.S,
            'S_high': S_high_tide,
            'S_low': S_low_tide,
            'L_intrusion': L_intrusion,
            'risk': risk_level,
            'safe': is_safe
        }
    
    # 任务4：盐水楔长度估算
    print(f"\n{'='*70}")
    print("盐水楔长度理论估算")
    print('='*70)
    
    for scenario_name, Q in Q_scenarios.items():
        L_wedge = calculate_salt_wedge_length(Q, 500, H, 1000, 1025)
        print(f"{scenario_name}: L_wedge ≈ {L_wedge/1000:.2f} km")
    
    # 绘图
    print(f"\n生成图表...")
    
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 图1：不同流量下的盐度分布
    fig1, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['blue', 'green', 'red']
    for (scenario_name, result), color in zip(results.items(), colors):
        ax.plot(result['x']/1000, result['S'], linewidth=2.5, 
                label=scenario_name, color=color)
    
    # 标注取水口和标准
    ax.axvline(x=20, color='purple', linestyle='--', linewidth=2, label='取水口位置')
    ax.axhline(y=0.5, color='orange', linestyle=':', linewidth=2, label='盐度标准（0.5 ppt）')
    ax.axhline(y=2.0, color='gray', linestyle=':', linewidth=1.5, alpha=0.5, label='入侵阈值（2 ppt）')
    
    ax.set_xlabel('距河口距离 (km)', fontsize=11)
    ax.set_ylabel('盐度 (ppt)', fontsize=11)
    ax.set_title('不同流量情景下的盐度分布', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 30])
    
    plt.tight_layout()
    plt.savefig('salinity_scenarios.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: salinity_scenarios.png")
    
    # 图2：枯水期潮汐影响
    fig2, ax = plt.subplots(figsize=(12, 6))
    
    result_dry = results['枯水期']
    ax.plot(result_dry['x']/1000, result_dry['S_high'], 'r-', linewidth=2.5, label='涨潮高潮位')
    ax.plot(result_dry['x']/1000, result_dry['S_low'], 'b-', linewidth=2.5, label='退潮低潮位')
    ax.plot(result_dry['x']/1000, result_dry['S'], 'g--', linewidth=2, label='平均盐度')
    
    ax.axvline(x=20, color='purple', linestyle='--', linewidth=2, label='取水口位置')
    ax.axhline(y=0.5, color='orange', linestyle=':', linewidth=2, label='盐度标准')
    
    ax.set_xlabel('距河口距离 (km)', fontsize=11)
    ax.set_ylabel('盐度 (ppt)', fontsize=11)
    ax.set_title('枯水期潮汐对盐度的影响', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('tidal_effect.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: tidal_effect.png")
    
    # 图3：入侵长度对比
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = list(results.keys())
    intrusion_lengths = [results[s]['L_intrusion']/1000 for s in scenarios]
    colors_bar = ['blue', 'green', 'red']
    
    bars = ax.bar(scenarios, intrusion_lengths, color=colors_bar, alpha=0.7, edgecolor='black', linewidth=2)
    
    # 标注数值
    for bar, val in zip(bars, intrusion_lengths):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{val:.1f} km',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 标注取水口位置
    ax.axhline(y=20, color='purple', linestyle='--', linewidth=2, label='取水口距离（20 km）')
    
    ax.set_ylabel('入侵长度 (km)', fontsize=11)
    ax.set_title('盐水入侵长度对比', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('intrusion_comparison.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: intrusion_comparison.png")
    
    # 图4：取水口风险评估
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    risk_levels = [results[s]['risk'] * 100 for s in scenarios]
    safe_status = ['安全' if results[s]['safe'] else '超标' for s in scenarios]
    bar_colors = ['green' if results[s]['safe'] else 'red' for s in scenarios]
    
    bars = ax.bar(scenarios, risk_levels, color=bar_colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # 标注
    for bar, val, status in zip(bars, risk_levels, safe_status):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{val:.0f}%\n{status}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.axhline(y=100, color='orange', linestyle='--', linewidth=2, label='风险阈值（100%）')
    
    ax.set_ylabel('风险等级 (%)', fontsize=11)
    ax.set_title('取水口盐度风险评估', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('intake_risk.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: intake_risk.png")
    
    # 总结
    print()
    print("=" * 70)
    print("案例12完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print(f"1. 丰水期：入侵{results['丰水期']['L_intrusion']/1000:.1f} km，取水安全")
    print(f"2. 平水期：入侵{results['平水期']['L_intrusion']/1000:.1f} km，取水{'安全' if results['平水期']['safe'] else '有风险'}")
    print(f"3. 枯水期：入侵{results['枯水期']['L_intrusion']/1000:.1f} km，取水{'安全' if results['枯水期']['safe'] else '超标'}")
    print()
    print("工程建议:")
    print("  1. 枯水期盐水入侵严重，需加强监测")
    print("  2. 取水口位置偏近，建议上移至25-30 km")
    print("  3. 建立上游水库调度方案，枯水期补水")
    print("  4. 配置实时盐度监测和预警系统")
    print("  5. 开发深层取水或备用水源")
    print()
    
    plt.show()


if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Agg')
    main()
