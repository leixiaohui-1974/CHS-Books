"""案例8：竖缝式鱼道水力设计

工程背景：
某河流拦河坝高度H=3m，需要设计竖缝式鱼道保障鱼类（草鱼、鲤鱼等）洄游。
要求流速适宜、能量消散合理，确保鱼类能够顺利通过。

学习目标：
1. 理解竖缝式鱼道工作原理
2. 掌握池室水力计算方法
3. 学会能量消散控制（体积功率密度）
4. 进行流速场分析和优化

计算内容：
1. 池室尺寸设计
2. 水深与流量关系
3. 体积功率密度验算
4. 流速场分布
5. 回流区分析
6. 设计参数优化
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.fishway import VerticalSlotFishway, create_standard_fishway

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def main():
    """主函数"""
    print("="*70)
    print("案例8：竖缝式鱼道水力设计")
    print("="*70)
    
    # 1. 工程参数
    print("\n【步骤1】工程基本参数")
    print("-"*70)
    
    dam_height = 3.0  # 坝高 (m)
    target_discharge = 1.0  # 设计流量 (m³/s)
    
    print(f"拦河坝高度: {dam_height} m")
    print(f"设计流量: {target_discharge} m³/s")
    print(f"目标鱼类: 草鱼、鲤鱼（持续游速约0.5-0.6 m/s）")
    
    # 2. 创建标准鱼道
    print("\n【步骤2】创建标准竖缝式鱼道")
    print("-"*70)
    
    fishway = create_standard_fishway(dam_height, target_discharge)
    
    print(f"\n标准设计参数：")
    print(f"  池室长度: {fishway.pool_length} m")
    print(f"  池室宽度: {fishway.pool_width} m")
    print(f"  竖缝宽度: {fishway.slot_width} m")
    print(f"  池间落差: {fishway.drop_per_pool} m")
    print(f"  池室数量: {fishway.num_pools} 个")
    
    # 3. 设计水深
    print("\n【步骤3】设计水深计算")
    print("-"*70)
    
    h_design, vpd_ok = fishway.design_water_depth(target_discharge, max_vpd=150.0)
    
    print(f"\n设计水深: {h_design:.3f} m")
    print(f"体积功率密度约束: {'✓ 满足' if vpd_ok else '✗ 不满足'}")
    
    # 计算关键参数
    Q_actual = fishway.slot_discharge(h_design)
    v_slot = fishway.slot_velocity(target_discharge, h_design)
    vpd = fishway.volumetric_power_dissipation(target_discharge, h_design)
    
    print(f"\n水力参数：")
    print(f"  实际流量: {Q_actual:.3f} m³/s")
    print(f"  竖缝流速: {v_slot:.3f} m/s")
    print(f"  体积功率密度: {vpd:.1f} W/m³ (限值: 150 W/m³)")
    
    # 4. 水深-流量关系
    print("\n【步骤4】水深-流量关系分析")
    print("-"*70)
    
    depths = np.linspace(0.5, 2.0, 20)
    discharges = [fishway.slot_discharge(h) for h in depths]
    velocities = [fishway.slot_velocity(Q, h) for Q, h in zip(discharges, depths)]
    vpds = [fishway.volumetric_power_dissipation(Q, h) for Q, h in zip(discharges, depths)]
    
    print(f"\n{'水深(m)':<10} {'流量(m³/s)':<15} {'竖缝流速(m/s)':<18} {'VPD(W/m³)':<15}")
    print("-"*70)
    for h, Q, v, vpd_val in zip(depths[::4], discharges[::4], velocities[::4], vpds[::4]):
        status = "✓" if vpd_val <= 150 else "✗"
        print(f"{h:<10.2f} {Q:<15.3f} {v:<18.3f} {vpd_val:<15.1f} {status}")
    
    # 5. 优化设计
    print("\n【步骤5】设计优化")
    print("-"*70)
    
    optimized = fishway.optimize_design(
        target_discharge=target_discharge,
        dam_height=dam_height,
        max_vpd=150.0,
        max_slot_velocity=1.5
    )
    
    print(f"\n优化后的设计：")
    print(f"  水深: {optimized['water_depth_m']:.3f} m")
    print(f"  竖缝流速: {optimized['slot_velocity_ms']:.3f} m/s")
    print(f"  体积功率密度: {optimized['volumetric_power_density_Wm3']:.1f} W/m³")
    print(f"  回流区面积比: {optimized['recirculation_area_ratio']:.1%}")
    print(f"  鱼道总长: {optimized['fishway_length_m']:.1f} m")
    print(f"  实际坡度: 1:{1/optimized['actual_slope']:.1f}")
    
    opt_result = optimized['optimization_result']
    print(f"\n约束条件检查：")
    print(f"  VPD约束: {'✓ 满足' if opt_result['vpd_constraint_met'] else '✗ 不满足'}")
    print(f"  流速约束: {'✓ 满足' if opt_result['velocity_constraint_met'] else '✗ 不满足'}")
    print(f"  总体评价: {'✓ 合格' if opt_result['all_constraints_met'] else '✗ 需调整'}")
    
    # 6. 流速场分析
    print("\n【步骤6】池室流速场分析")
    print("-"*70)
    
    X, Y, V = fishway.velocity_field(target_discharge, h_design, nx=30, ny=20)
    
    v_max = np.max(V)
    v_avg = np.mean(V)
    low_v_ratio = fishway.recirculation_area_ratio(target_discharge, h_design, 0.3)
    
    print(f"\n流速场统计：")
    print(f"  最大流速: {v_max:.3f} m/s")
    print(f"  平均流速: {v_avg:.3f} m/s")
    print(f"  低流速区(<0.3m/s)面积比: {low_v_ratio:.1%}")
    
    # 7. 绘图
    print("\n【步骤7】生成可视化图表")
    print("-"*70)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 图1: 水深-流量关系
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(depths, discharges, 'b-', linewidth=2)
    ax1.axhline(y=target_discharge, color='r', linestyle='--', 
                label=f'设计流量 {target_discharge} m³/s')
    ax1.axvline(x=h_design, color='g', linestyle='--', 
                label=f'设计水深 {h_design:.2f} m')
    ax1.set_xlabel('水深 (m)', fontsize=11)
    ax1.set_ylabel('流量 (m³/s)', fontsize=11)
    ax1.set_title('水深-流量关系曲线', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: 体积功率密度
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(discharges, vpds, 'r-', linewidth=2)
    ax2.axhline(y=150, color='orange', linestyle='--', linewidth=2,
                label='限值 150 W/m³')
    ax2.axvline(x=target_discharge, color='g', linestyle='--',
                label=f'设计流量 {target_discharge} m³/s')
    ax2.set_xlabel('流量 (m³/s)', fontsize=11)
    ax2.set_ylabel('体积功率密度 (W/m³)', fontsize=11)
    ax2.set_title('体积功率密度验算', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: 竖缝流速
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(discharges, velocities, 'g-', linewidth=2)
    ax3.axhline(y=1.5, color='orange', linestyle='--', linewidth=2,
                label='建议上限 1.5 m/s')
    ax3.axhline(y=0.6, color='blue', linestyle=':', linewidth=1.5,
                label='鱼类持续游速 0.6 m/s')
    ax3.axvline(x=target_discharge, color='g', linestyle='--',
                label=f'设计流量 {target_discharge} m³/s')
    ax3.set_xlabel('流量 (m³/s)', fontsize=11)
    ax3.set_ylabel('竖缝流速 (m/s)', fontsize=11)
    ax3.set_title('竖缝流速分析', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 图4: 池室流速场
    ax4 = plt.subplot(2, 3, 4)
    contour = ax4.contourf(X, Y, V, levels=20, cmap='jet')
    plt.colorbar(contour, ax=ax4, label='流速 (m/s)')
    
    # 绘制竖缝位置
    ax4.add_patch(Rectangle((0, (fishway.pool_width-fishway.slot_width)/2), 
                            0.05, fishway.slot_width, 
                            facecolor='white', edgecolor='black', linewidth=2))
    
    ax4.set_xlabel('长度方向 (m)', fontsize=11)
    ax4.set_ylabel('宽度方向 (m)', fontsize=11)
    ax4.set_title('池室流速场分布', fontsize=12, fontweight='bold')
    ax4.set_aspect('equal')
    
    # 图5: 流速剖面（沿中心线）
    ax5 = plt.subplot(2, 3, 5)
    center_idx = V.shape[0] // 2
    v_centerline = V[center_idx, :]
    x_centerline = X[center_idx, :]
    
    ax5.plot(x_centerline, v_centerline, 'b-', linewidth=2, label='中心线流速')
    ax5.axhline(y=0.3, color='orange', linestyle='--', 
                label='低流速阈值 0.3 m/s')
    ax5.fill_between(x_centerline, 0, v_centerline, alpha=0.3)
    ax5.set_xlabel('距竖缝距离 (m)', fontsize=11)
    ax5.set_ylabel('流速 (m/s)', fontsize=11)
    ax5.set_title('沿中心线流速分布', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 图6: 设计总结
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    summary_text = f"""
    【竖缝式鱼道设计总结】
    
    工程条件：
    ┌─────────────────────────────┐
    │ 大坝高度：{dam_height} m              │
    │ 设计流量：{target_discharge} m³/s            │
    │ 目标鱼类：草鱼、鲤鱼         │
    └─────────────────────────────┘
    
    设计参数：
    ┌─────────────────────────────┐
    │ 池室尺寸：{fishway.pool_length}m × {fishway.pool_width}m        │
    │ 竖缝宽度：{fishway.slot_width} m              │
    │ 池间落差：{fishway.drop_per_pool} m              │
    │ 池室数量：{fishway.num_pools} 个              │
    │ 设计水深：{h_design:.2f} m             │
    └─────────────────────────────┘
    
    水力参数：
    ┌─────────────────────────────┐
    │ 竖缝流速：{v_slot:.2f} m/s         │
    │ VPD：{vpd:.0f} W/m³ {'✓' if vpd<=150 else '✗'}      │
    │ 回流区比：{low_v_ratio:.0%}            │
    └─────────────────────────────┘
    
    总体参数：
    ┌─────────────────────────────┐
    │ 鱼道长度：{optimized['fishway_length_m']:.1f} m           │
    │ 总落差：{optimized['total_head_loss_m']:.1f} m             │
    │ 实际坡度：1:{1/optimized['actual_slope']:.1f}         │
    └─────────────────────────────┘
    
    设计评价：
    ┌─────────────────────────────┐
    │ VPD约束：{'✓ 满足' if vpd<=150 else '✗ 不满足'}        │
    │ 流速约束：{'✓ 满足' if v_slot<=1.5 else '✗ 不满足'}        │
    │ 坡度合理：{'✓ 是' if optimized['slope_reasonable'] else '✗ 否'}          │
    │ 总体评价：{'✓ 合格' if opt_result['all_constraints_met'] else '✗ 需调整'}        │
    └─────────────────────────────┘
    """
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
            family='monospace')
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'fishway_design.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 图表已保存: {output_file}")
    
    # 8. 总结
    print("\n" + "="*70)
    print("【工程结论】")
    print("="*70)
    print(f"""
1. 鱼道几何设计：
   - 池室尺寸: {fishway.pool_length}m × {fishway.pool_width}m × {h_design:.2f}m（长×宽×深）
   - 竖缝宽度: {fishway.slot_width} m
   - 池间落差: {fishway.drop_per_pool} m
   - 池室数量: {fishway.num_pools} 个

2. 水力性能评估：
   - 设计流量: {target_discharge} m³/s
   - 竖缝流速: {v_slot:.2f} m/s（低于鱼类爆发游速3.0 m/s）
   - 体积功率密度: {vpd:.0f} W/m³（{'满足' if vpd<=150 else '超过'}限值150 W/m³）
   - 回流区面积: {low_v_ratio:.0%}（提供休息空间）

3. 鱼类通过性分析：
   - 目标鱼类持续游速约0.5-0.6 m/s
   - 竖缝流速{v_slot:.2f} m/s，鱼类可短时间通过
   - 池室内有{low_v_ratio:.0%}低流速区供休息
   - 预计通过成功率: 高

4. 设计建议：
   - 本设计{'满足' if opt_result['all_constraints_met'] else '不满足'}所有约束条件
   - 鱼道总长{optimized['fishway_length_m']:.1f}m，实际坡度1:{1/optimized['actual_slope']:.1f}
   - 建议在鱼道入口设置诱鱼流
   - 建议定期监测鱼类通过情况

5. 工程应用：
   - 本设计可用于低坝（<5m）过鱼工程
   - 适用于鲤科鱼类洄游
   - 施工简单，维护方便
   - 可根据实际监测结果调整竖缝宽度
    """)
    
    print("="*70)
    print("案例8计算完成！")
    print("="*70)


if __name__ == "__main__":
    main()
