"""
案例17：地面沉降模拟

本案例演示地下水开采导致的地面沉降预测。

演示内容：
---------
1. Terzaghi有效应力原理
2. 线性vs对数压缩模型
3. 正常固结vs超固结
4. 固结时间过程
5. 多层系统总沉降
6. 沉降空间分布

物理场景：
---------
某城市地下水过度开采：
- 地下水位下降30m
- 多层土层系统
- 预测地面沉降
- 评估风险

学习目标：
---------
1. 理解有效应力原理
2. 掌握压缩计算方法
3. 分析固结时间过程
4. 预测地面沉降
5. 评估沉降风险

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# 导入gwflow模块
import sys
sys.path.insert(0, '/workspace/books/underground-water-dynamics')

from gwflow.subsidence import (
    SoilLayer,
    SubsidenceModel,
    terzaghi_consolidation_1d,
    consolidation_degree,
    consolidation_settlement,
    compute_effective_stress_change,
    compute_settlement_time
)

from gwflow.pumping import theis_solution

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_effective_stress():
    """
    实验1：有效应力原理
    """
    print("\n" + "="*60)
    print("实验1：Terzaghi有效应力原理")
    print("="*60)
    
    # 场景：水位下降
    head_changes = np.array([0, -5, -10, -15, -20, -30])  # m
    
    print(f"\n有效应力变化计算：")
    print(f"{'水位变化(m)':<15} {'有效应力增量(kPa)':<20}")
    print("-" * 35)
    
    delta_sigmas = []
    for dh in head_changes:
        delta_sigma = compute_effective_stress_change(dh)
        delta_sigmas.append(delta_sigma)
        print(f"{dh:<15.1f} {delta_sigma:<20.1f}")
    
    print(f"\n物理解释：")
    print(f"  水位下降 → 孔隙水压力降低")
    print(f"  总应力不变 → 有效应力增加")
    print(f"  有效应力增加 → 土层压缩")
    
    print(f"\n关系：Δσ' = -γw * Δh")
    print(f"  γw = 9.81 kN/m³")
    print(f"  水位降30m → 有效应力增加294.3 kPa")
    
    return head_changes, np.array(delta_sigmas)


def experiment_2_compression_models():
    """
    实验2：压缩模型对比
    """
    print("\n" + "="*60)
    print("实验2：线性vs对数压缩模型")
    print("="*60)
    
    # 创建土层
    layer_linear = SoilLayer(
        name="粘土层（线性）",
        top=0,
        bottom=-10,
        av=0.0005,  # 1/kPa
        gamma_sat=19.0
    )
    
    layer_log = SoilLayer(
        name="粘土层（对数）",
        top=0,
        bottom=-10,
        Cc=0.3,
        e0=0.8,
        gamma_sat=19.0
    )
    
    # 有效应力范围
    sigma_0 = 100  # kPa
    delta_sigma_range = np.linspace(0, 300, 50)
    
    # 线性模型
    compression_linear = []
    for ds in delta_sigma_range:
        comp = layer_linear.compute_compression_linear(ds)
        compression_linear.append(comp)
    
    # 对数模型
    compression_log = []
    for ds in delta_sigma_range:
        sigma_f = sigma_0 + ds
        comp = layer_log.compute_compression_logarithmic(sigma_0, sigma_f)
        compression_log.append(comp)
    
    compression_linear = np.array(compression_linear)
    compression_log = np.array(compression_log)
    
    print(f"\n线性模型：")
    print(f"  ΔH = av * Δσ' * H")
    print(f"  av = {layer_linear.av} 1/kPa")
    print(f"  Δσ'=100kPa → ΔH={compression_linear[16]:.3f}m")
    
    print(f"\n对数模型：")
    print(f"  ΔH/H = Cc/(1+e0) * log10(σ'f/σ'0)")
    print(f"  Cc = {layer_log.Cc}, e0 = {layer_log.e0}")
    print(f"  σ'0=100kPa, σ'f=200kPa → ΔH={compression_log[16]:.3f}m")
    
    print(f"\n对比：")
    print(f"  线性：适用于小应力增量")
    print(f"  对数：更符合实际，应力范围大")
    
    return delta_sigma_range, compression_linear, compression_log


def experiment_3_preconsolidation():
    """
    实验3：正常固结vs超固结
    """
    print("\n" + "="*60)
    print("实验3：正常固结 vs 超固结")
    print("="*60)
    
    # 土层参数
    layer = SoilLayer(
        name="粘土层",
        top=0,
        bottom=-10,
        Cc=0.3,
        e0=0.8,
        sigma_c=200,  # 先期固结压力 kPa
        gamma_sat=19.0
    )
    
    sigma_0 = 100  # kPa（现有应力）
    sigma_range = np.linspace(100, 400, 50)
    
    # 正常固结（假设sigma_c = sigma_0）
    layer_nc = SoilLayer(
        name="正常固结",
        top=0, bottom=-10,
        Cc=0.3, e0=0.8,
        sigma_c=100,  # 正常固结
        gamma_sat=19.0
    )
    
    compression_nc = []
    compression_oc = []  # 超固结
    
    for sigma_f in sigma_range:
        # 正常固结
        comp_nc = layer_nc.compute_compression_with_preconsolidation(
            sigma_0, sigma_f
        )
        compression_nc.append(comp_nc)
        
        # 超固结
        comp_oc = layer.compute_compression_with_preconsolidation(
            sigma_0, sigma_f
        )
        compression_oc.append(comp_oc)
    
    compression_nc = np.array(compression_nc)
    compression_oc = np.array(compression_oc)
    
    print(f"\n正常固结（NC）：")
    print(f"  σ'0 = σ'c = 100 kPa")
    print(f"  一直处于正常压缩状态")
    print(f"  σ'f=300kPa → ΔH={compression_nc[-1]:.3f}m")
    
    print(f"\n超固结（OC）：")
    print(f"  σ'0 = 100 kPa < σ'c = 200 kPa")
    print(f"  历史上经历过更大应力")
    print(f"  σ'f<σ'c：再压缩（小压缩）")
    print(f"  σ'f>σ'c：正常压缩（大压缩）")
    print(f"  σ'f=300kPa → ΔH={compression_oc[-1]:.3f}m")
    
    print(f"\n超固结比 OCR = σ'c / σ'0 = {layer.sigma_c / sigma_0:.1f}")
    print(f"  OCR=1: 正常固结")
    print(f"  OCR>1: 超固结（压缩小）")
    
    return sigma_range, compression_nc, compression_oc


def experiment_4_consolidation_process():
    """
    实验4：固结时间过程
    """
    print("\n" + "="*60)
    print("实验4：固结时间过程")
    print("="*60)
    
    # 土层参数
    H = 5  # 排水距离 m（土层厚10m，双面排水）
    Cv = 1.0  # 固结系数 m²/day
    S_ultimate = 0.5  # 最终沉降 m
    
    # 时间数组
    t = np.linspace(0, 500, 100)  # days
    
    # 固结度
    Tv = Cv * t / H**2
    U = consolidation_degree(Tv)
    
    # 沉降
    S = U * S_ultimate
    
    print(f"\n参数：")
    print(f"  土层厚度: 10 m（双面排水）")
    print(f"  排水距离 H: {H} m")
    print(f"  固结系数 Cv: {Cv} m²/day")
    print(f"  最终沉降: {S_ultimate} m")
    
    print(f"\n关键时间点：")
    for U_target in [0.5, 0.9, 0.95]:
        t_target = compute_settlement_time(U_target, S_ultimate, Cv, H)
        S_target = U_target * S_ultimate
        print(f"  U={U_target*100:.0f}% (S={S_target:.2f}m): t={t_target:.1f} day ({t_target/365:.2f} year)")
    
    print(f"\n固结特性：")
    print(f"  早期：固结快")
    print(f"  后期：固结慢（渐近线）")
    print(f"  U=90%以后进展缓慢")
    
    return t, U, S


def experiment_5_multi_layer_subsidence():
    """
    实验5：多层系统总沉降
    """
    print("\n" + "="*60)
    print("实验5：多层系统总沉降")
    print("="*60)
    
    # 创建沉降模型
    model = SubsidenceModel(name="多层系统")
    
    # 添加土层（从上到下）
    layers_config = [
        {"name": "填土", "top": 0, "bottom": -3, "av": 0.0002, "Cv": 5.0},
        {"name": "粉质粘土", "top": -3, "bottom": -10, "av": 0.0003, "Cv": 2.0},
        {"name": "淤泥质粘土", "top": -10, "bottom": -20, "av": 0.0008, "Cv": 0.5},
        {"name": "粘土", "top": -20, "bottom": -35, "av": 0.0004, "Cv": 1.0},
        {"name": "砂层", "top": -35, "bottom": -50, "av": 0.00005, "Cv": 50.0},
    ]
    
    for config in layers_config:
        layer = SoilLayer(**config, gamma_sat=19.0)
        model.add_layer(layer)
    
    print(f"\n土层结构：")
    print(f"{'层名':<12} {'厚度(m)':<10} {'av(1/kPa)':<12} {'Cv(m²/day)':<12}")
    print("-" * 50)
    for layer in model.layers:
        print(f"{layer.name:<12} {layer.thickness:<10.1f} {layer.av:<12.6f} {layer.Cv:<12.2f}")
    
    print(f"\n总厚度: {model.get_total_thickness():.1f} m")
    
    # 水位下降情景
    head_change = -30  # m
    head_changes = {layer.name: head_change for layer in model.layers}
    
    # 计算沉降
    layer_compressions, total_subsidence = model.compute_subsidence(
        head_changes, method='linear'
    )
    
    print(f"\n水位下降: {-head_change} m")
    print(f"\n各层压缩量：")
    print(f"{'层名':<12} {'压缩量(m)':<12} {'贡献率(%)':<12}")
    print("-" * 40)
    for name, comp in layer_compressions.items():
        contrib = comp / total_subsidence * 100
        print(f"{name:<12} {comp:<12.4f} {contrib:<12.1f}")
    
    print(f"\n总沉降: {total_subsidence:.3f} m = {total_subsidence*100:.1f} cm")
    
    print(f"\n分析：")
    print(f"  淤泥质粘土贡献最大（高压缩性）")
    print(f"  砂层几乎不压缩（低压缩性）")
    print(f"  总沉降是各层叠加")
    
    return model, layer_compressions, total_subsidence


def experiment_6_spatial_distribution():
    """
    实验6：沉降空间分布
    """
    print("\n" + "="*60)
    print("实验6：沉降空间分布")
    print("="*60)
    
    # 含水层参数
    Q = 3000  # m³/day
    T = 500   # m²/day
    S = 0.0002
    t = 100   # days
    
    # 网格
    x = np.linspace(-1000, 1000, 51)
    y = np.linspace(-1000, 1000, 51)
    X, Y = np.meshgrid(x, y)
    
    # 抽水井在(0,0)
    r = np.sqrt(X**2 + Y**2)
    r = np.maximum(r, 0.1)
    
    # 水头降深
    drawdown = theis_solution(r, t, Q, T, S)
    
    # 沉降系数（经验：cm/m）
    subsidence_coef = 2.0  # cm沉降/m降深
    
    # 沉降
    subsidence = drawdown * subsidence_coef / 100  # m
    
    print(f"\n抽水井参数：")
    print(f"  Q = {Q} m³/day")
    print(f"  t = {t} day")
    
    print(f"\n沉降系数: {subsidence_coef} cm/m")
    print(f"  （每米水位降深产生{subsidence_coef}cm沉降）")
    
    print(f"\n沉降统计：")
    print(f"  最大沉降（井筒）: {np.max(subsidence)*100:.1f} cm")
    print(f"  平均沉降: {np.mean(subsidence)*100:.1f} cm")
    print(f"  影响范围（>1cm）: {np.max(r[subsidence > 0.01]):.0f} m")
    
    print(f"\n特征：")
    print(f"  沉降漏斗类似降深漏斗")
    print(f"  井附近沉降最大")
    print(f"  沉降范围与降深范围一致")
    
    return X, Y, drawdown, subsidence


def plot_results(exp1, exp2, exp3, exp4, exp5, exp6):
    """绘制所有结果"""
    
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.35)
    
    # 图1: 有效应力原理
    ax1 = fig.add_subplot(gs[0, 0])
    head_changes, delta_sigmas = exp1
    ax1.plot(-head_changes, delta_sigmas, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('水位下降 (m)', fontsize=11)
    ax1.set_ylabel('有效应力增量 (kPa)', fontsize=11)
    ax1.set_title('Terzaghi有效应力原理', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 添加关系线
    ax1.text(15, 150, "Δσ' = 9.81·Δh", fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 图2: 压缩模型对比
    ax2 = fig.add_subplot(gs[0, 1])
    delta_sigma_range, comp_linear, comp_log = exp2
    ax2.plot(delta_sigma_range, comp_linear*100, 'b-', linewidth=2, label='线性模型')
    ax2.plot(delta_sigma_range, comp_log*100, 'r--', linewidth=2, label='对数模型')
    ax2.set_xlabel('有效应力增量 (kPa)', fontsize=11)
    ax2.set_ylabel('压缩量 (cm)', fontsize=11)
    ax2.set_title('压缩模型对比', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 正常固结vs超固结
    ax3 = fig.add_subplot(gs[0, 2])
    sigma_range, comp_nc, comp_oc = exp3
    ax3.plot(sigma_range, comp_nc*100, 'b-', linewidth=2, label='正常固结')
    ax3.plot(sigma_range, comp_oc*100, 'r--', linewidth=2, label='超固结(OCR=2)')
    ax3.axvline(200, color='gray', linestyle=':', alpha=0.5, label='σ\'c')
    ax3.set_xlabel('最终有效应力 (kPa)', fontsize=11)
    ax3.set_ylabel('压缩量 (cm)', fontsize=11)
    ax3.set_title('正常固结 vs 超固结', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 固结度vs时间
    ax4 = fig.add_subplot(gs[1, 0])
    t, U, S = exp4
    ax4.plot(t, U, 'b-', linewidth=2)
    ax4.axhline(0.5, color='red', linestyle='--', alpha=0.5, label='U=50%')
    ax4.axhline(0.9, color='orange', linestyle='--', alpha=0.5, label='U=90%')
    ax4.set_xlabel('时间 (day)', fontsize=11)
    ax4.set_ylabel('固结度 U', fontsize=11)
    ax4.set_title('固结度 vs 时间', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # 图5: 沉降vs时间
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(t, S*100, 'b-', linewidth=2)
    ax5.axhline(0.5*100, color='gray', linestyle='--', alpha=0.5, label='最终沉降')
    ax5.set_xlabel('时间 (day)', fontsize=11)
    ax5.set_ylabel('沉降 (cm)', fontsize=11)
    ax5.set_title('沉降时间曲线', fontsize=13, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 各层压缩量
    ax6 = fig.add_subplot(gs[1, 2])
    model, layer_compressions, total_subsidence = exp5
    layer_names = list(layer_compressions.keys())
    compressions = [layer_compressions[name]*100 for name in layer_names]
    
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightgray']
    bars = ax6.barh(layer_names, compressions, color=colors[:len(layer_names)], 
                    edgecolor='black', alpha=0.7)
    ax6.set_xlabel('压缩量 (cm)', fontsize=11)
    ax6.set_title('各层压缩量', fontsize=13, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='x')
    
    # 标注数值
    for i, (bar, comp) in enumerate(zip(bars, compressions)):
        ax6.text(comp, i, f' {comp:.1f}', va='center', fontsize=9)
    
    # 图7: 层序剖面
    ax7 = fig.add_subplot(gs[2, 0])
    
    y_positions = []
    thicknesses = []
    colors_profile = []
    
    for i, layer in enumerate(model.layers):
        y_positions.append(layer.z_mid)
        thicknesses.append(layer.thickness)
        colors_profile.append(colors[i])
    
    for i, layer in enumerate(model.layers):
        ax7.barh(layer.z_mid, 1, height=layer.thickness, 
                color=colors_profile[i], edgecolor='black', alpha=0.7)
        ax7.text(0.5, layer.z_mid, layer.name, ha='center', va='center', fontsize=9)
    
    ax7.set_xlabel('', fontsize=11)
    ax7.set_ylabel('标高 (m)', fontsize=11)
    ax7.set_title('土层剖面', fontsize=13, fontweight='bold')
    ax7.set_xlim(0, 1)
    ax7.set_xticks([])
    ax7.axhline(0, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='地表')
    ax7.legend(fontsize=10)
    ax7.grid(True, alpha=0.3, axis='y')
    
    # 图8: 沉降空间分布2D
    ax8 = fig.add_subplot(gs[2, 1])
    X, Y, drawdown, subsidence = exp6
    
    levels = [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    cs = ax8.contourf(X, Y, subsidence, levels=levels, cmap='YlOrRd')
    ax8.contour(X, Y, subsidence, levels=levels, colors='black', 
               linewidths=0.5, alpha=0.3)
    ax8.plot(0, 0, 'k*', markersize=15, label='抽水井')
    ax8.set_xlabel('x (m)', fontsize=11)
    ax8.set_ylabel('y (m)', fontsize=11)
    ax8.set_title('沉降漏斗 (m)', fontsize=13, fontweight='bold')
    ax8.legend(fontsize=10)
    ax8.axis('equal')
    plt.colorbar(cs, ax=ax8, label='沉降 (m)')
    
    # 图9: 降深vs沉降关系
    ax9 = fig.add_subplot(gs[2, 2])
    
    # 中心线剖面
    center_line_idx = subsidence.shape[0] // 2
    r_profile = X[center_line_idx, :]
    drawdown_profile = drawdown[center_line_idx, :]
    subsidence_profile = subsidence[center_line_idx, :]
    
    ax9_twin = ax9.twinx()
    
    line1 = ax9.plot(r_profile, drawdown_profile, 'b-', linewidth=2, label='水头降深')
    line2 = ax9_twin.plot(r_profile, subsidence_profile*100, 'r-', linewidth=2, 
                          label='沉降')
    
    ax9.set_xlabel('距离 (m)', fontsize=11)
    ax9.set_ylabel('水头降深 (m)', fontsize=11, color='b')
    ax9_twin.set_ylabel('沉降 (cm)', fontsize=11, color='r')
    ax9.set_title('降深与沉降剖面', fontsize=13, fontweight='bold')
    ax9.tick_params(axis='y', labelcolor='b')
    ax9_twin.tick_params(axis='y', labelcolor='r')
    ax9.grid(True, alpha=0.3)
    
    # 合并图例
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax9.legend(lines, labels, fontsize=10)
    
    plt.savefig('case_17_subsidence_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_17_subsidence_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例17：地面沉降模拟")
    print("="*60)
    print("\n本案例演示地下水开采导致的地面沉降预测")
    
    # 运行所有实验
    exp1 = experiment_1_effective_stress()
    exp2 = experiment_2_compression_models()
    exp3 = experiment_3_preconsolidation()
    exp4 = experiment_4_consolidation_process()
    exp5 = experiment_5_multi_layer_subsidence()
    exp6 = experiment_6_spatial_distribution()
    
    # 绘图
    print("\n生成结果图...")
    plot_results(exp1, exp2, exp3, exp4, exp5, exp6)
    
    # 总结
    print("\n" + "="*60)
    print("案例17完成总结")
    print("="*60)
    
    print(f"\n核心发现：")
    print(f"1. 水位下降导致有效应力增加（Δσ'≈9.81·Δh）")
    print(f"2. 对数模型更适合大应力增量")
    print(f"3. 超固结土压缩性小于正常固结土")
    print(f"4. 固结是时间过程，U=90%需要较长时间")
    print(f"5. 淤泥质粘土是沉降主要来源")
    print(f"6. 沉降漏斗类似降深漏斗")
    
    print(f"\n学习要点：")
    print(f"✓ Terzaghi有效应力原理")
    print(f"✓ 线性和对数压缩模型")
    print(f"✓ 先期固结概念")
    print(f"✓ 固结时间过程")
    print(f"✓ 多层系统沉降计算")
    print(f"✓ 空间分布预测")
    
    print(f"\n工程意义：")
    print(f"✓ 地面沉降预测")
    print(f"✓ 风险评估")
    print(f"✓ 开采方案优化")
    print(f"✓ 监测网设计")
    
    print("\n✅ 案例17执行完成！")


if __name__ == '__main__':
    main()
