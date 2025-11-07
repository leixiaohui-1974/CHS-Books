"""
案例7：风光互补特性分析

展示内容：
1. 风电和光伏日内出力特性
2. 相关系数分析
3. 互补系数计算
4. 季节性互补特性
5. 联合出力平滑度分析

作者: CHS Books
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
from models.multi_energy_system import ComplementarityAnalysis

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_wind_solar_profiles(season='summer', n_days=7, T_per_day=96):
    """
    生成风电和光伏出力曲线
    
    Args:
        season: 季节 ('spring', 'summer', 'autumn', 'winter')
        n_days: 天数
        T_per_day: 每天的时间点数（96 = 24h × 4点/h）
        
    Returns:
        wind, solar: 风电和光伏功率序列
    """
    T = n_days * T_per_day
    t = np.linspace(0, 24*n_days, T)
    
    # 季节参数
    season_params = {
        'spring': {'wind_base': 0.6, 'wind_amp': 0.3, 'solar_max': 0.85},
        'summer': {'wind_base': 0.4, 'wind_amp': 0.25, 'solar_max': 1.0},
        'autumn': {'wind_base': 0.65, 'wind_amp': 0.35, 'solar_max': 0.75},
        'winter': {'wind_base': 0.75, 'wind_amp': 0.4, 'solar_max': 0.65},
    }
    
    params = season_params[season]
    
    # 风电出力（夜间和早晨较大，有随机波动）
    wind = np.zeros(T)
    for i in range(T):
        t_local = t[i] % 24
        # 基础日变化模式
        wind_pattern = params['wind_base'] + params['wind_amp'] * np.sin(2*np.pi*t_local/24 + np.pi)
        # 添加随机波动
        wind_fluctuation = 0.15 * np.random.randn()
        wind[i] = wind_pattern + wind_fluctuation
    
    wind = np.clip(wind, 0, 1)
    wind = wind * 200  # 200MW装机
    
    # 光伏出力（白天有出力，晴天和阴天交替）
    solar = np.zeros(T)
    for i in range(T):
        t_local = t[i] % 24
        day = int(t[i] / 24)
        
        # 基础光照模式（6:00-18:00）
        if 6 <= t_local <= 18:
            solar_pattern = params['solar_max'] * np.sin(np.pi * (t_local - 6) / 12) ** 2
            
            # 模拟云层遮挡（部分天阴天）
            if day % 3 == 1:  # 每3天有1天多云
                cloud_factor = 0.4 + 0.3 * np.random.rand()
            else:
                cloud_factor = 0.9 + 0.1 * np.random.rand()
            
            solar[i] = solar_pattern * cloud_factor
        else:
            solar[i] = 0
    
    solar = solar * 150  # 150MW装机
    
    return wind, solar, t


def main():
    """主函数"""
    
    print("=" * 80)
    print("案例7：风光互补特性分析")
    print("=" * 80)
    
    # 创建分析器
    analyzer = ComplementarityAnalysis()
    
    # ========================================================================
    # 第1部分：单日分析
    # ========================================================================
    
    print("\n【第1部分：典型日风光互补特性】")
    print("-" * 80)
    
    # 生成夏季典型日数据
    wind_summer, solar_summer, t = generate_wind_solar_profiles(
        season='summer', n_days=1, T_per_day=96
    )
    
    t_hours = t[:96]
    
    print(f"\n夏季典型日：")
    print(f"  风电: {wind_summer.min():.1f} - {wind_summer.max():.1f} MW")
    print(f"  光伏: {solar_summer.min():.1f} - {solar_summer.max():.1f} MW")
    print(f"  平均: 风电 {wind_summer.mean():.1f} MW, 光伏 {solar_summer.mean():.1f} MW")
    
    # 计算相关系数
    corr = analyzer.correlation_coefficient(wind_summer, solar_summer)
    print(f"\n✓ 相关系数: {corr:.3f}")
    if corr < -0.3:
        print(f"  → 负相关明显，互补性强")
    elif corr < 0.3:
        print(f"  → 相关性弱，具有一定互补性")
    else:
        print(f"  → 正相关，互补性较弱")
    
    # 计算互补系数
    C = analyzer.complementarity_coefficient(wind_summer, solar_summer)
    print(f"\n✓ 互补系数: {C:.3f}")
    print(f"  → 互补系数越大，互补性越好（>0表示有互补效果）")
    
    # 波动分析
    wind_std = np.std(wind_summer)
    solar_std = np.std(solar_summer)
    combined_std = np.std(wind_summer + solar_summer)
    
    smoothing_effect = 1 - combined_std / (wind_std + solar_std)
    
    print(f"\n✓ 波动平抑效果：")
    print(f"  风电标准差: {wind_std:.2f} MW")
    print(f"  光伏标准差: {solar_std:.2f} MW")
    print(f"  联合标准差: {combined_std:.2f} MW")
    print(f"  平抑效果: {smoothing_effect:.1%}")
    
    # ========================================================================
    # 第2部分：多日分析
    # ========================================================================
    
    print("\n\n【第2部分：一周风光互补特性】")
    print("-" * 80)
    
    wind_week, solar_week, t_week = generate_wind_solar_profiles(
        season='summer', n_days=7, T_per_day=96
    )
    
    # 日平均出力
    daily_wind = []
    daily_solar = []
    for day in range(7):
        start = day * 96
        end = (day + 1) * 96
        daily_wind.append(np.mean(wind_week[start:end]))
        daily_solar.append(np.mean(solar_week[start:end]))
    
    print(f"\n日平均出力（MW）：")
    print(f"  {'日期':<10} {'风电':<10} {'光伏':<10} {'合计':<10}")
    print(f"  {'-'*40}")
    for i in range(7):
        total = daily_wind[i] + daily_solar[i]
        print(f"  第{i+1}天{'':<6} {daily_wind[i]:>6.1f}     {daily_solar[i]:>6.1f}     {total:>6.1f}")
    
    # 周总发电量
    energy_wind_week = np.sum(wind_week) * 0.25  # 15min = 0.25h
    energy_solar_week = np.sum(solar_week) * 0.25
    
    print(f"\n✓ 周发电量：")
    print(f"  风电: {energy_wind_week:,.0f} MWh")
    print(f"  光伏: {energy_solar_week:,.0f} MWh")
    print(f"  总计: {energy_wind_week + energy_solar_week:,.0f} MWh")
    
    # ========================================================================
    # 第3部分：季节互补分析
    # ========================================================================
    
    print("\n\n【第3部分：季节互补特性】")
    print("-" * 80)
    
    seasons = ['spring', 'summer', 'autumn', 'winter']
    season_names = ['春季', '夏季', '秋季', '冬季']
    
    monthly_wind = []
    monthly_solar = []
    
    print(f"\n季节平均出力（MW）：")
    print(f"  {'季节':<10} {'风电':<10} {'光伏':<10} {'互补系数':<10}")
    print(f"  {'-'*45}")
    
    for season, name in zip(seasons, season_names):
        wind, solar, _ = generate_wind_solar_profiles(season=season, n_days=3, T_per_day=96)
        
        wind_mean = np.mean(wind)
        solar_mean = np.mean(solar)
        
        monthly_wind.append(wind_mean)
        monthly_solar.append(solar_mean)
        
        # 季节互补系数
        C_season = analyzer.complementarity_coefficient(wind, solar)
        
        print(f"  {name:<10} {wind_mean:>6.1f}     {solar_mean:>6.1f}     {C_season:>6.3f}")
    
    # 季节相关性
    monthly_wind_array = np.array(monthly_wind)
    monthly_solar_array = np.array(monthly_solar)
    
    season_corr = analyzer.correlation_coefficient(monthly_wind_array, monthly_solar_array)
    
    print(f"\n✓ 季节相关系数: {season_corr:.3f}")
    if season_corr < 0:
        print(f"  → 季节互补明显（冬季风大，夏季光强）")
    else:
        print(f"  → 季节互补较弱")
    
    # ========================================================================
    # 第4部分：可视化
    # ========================================================================
    
    print("\n\n【第4部分：可视化分析】")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 4.1 典型日出力曲线
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(t_hours, wind_summer, 'g-', label='风电', linewidth=2)
    ax1.plot(t_hours, solar_summer, 'orange', label='光伏', linewidth=2)
    ax1.fill_between(t_hours, 0, wind_summer, alpha=0.3, color='green')
    ax1.fill_between(t_hours, 0, solar_summer, alpha=0.3, color='orange')
    ax1.set_xlabel('时间 (小时)')
    ax1.set_ylabel('功率 (MW)')
    ax1.set_title('典型日风光出力曲线（夏季）')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 24)
    
    # 4.2 联合出力
    ax2 = plt.subplot(3, 2, 2)
    combined = wind_summer + solar_summer
    ax2.plot(t_hours, wind_summer, 'g--', label='风电', linewidth=1.5, alpha=0.7)
    ax2.plot(t_hours, solar_summer, '--', color='orange', label='光伏', linewidth=1.5, alpha=0.7)
    ax2.plot(t_hours, combined, 'b-', label='联合出力', linewidth=2.5)
    ax2.set_xlabel('时间 (小时)')
    ax2.set_ylabel('功率 (MW)')
    ax2.set_title('风光联合出力（平滑效果）')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 24)
    
    # 4.3 一周出力
    ax3 = plt.subplot(3, 2, 3)
    t_week_hours = t_week / 24
    ax3.plot(t_week_hours, wind_week, 'g-', label='风电', linewidth=1, alpha=0.8)
    ax3.plot(t_week_hours, solar_week, 'orange', label='光伏', linewidth=1, alpha=0.8)
    ax3.fill_between(t_week_hours, 0, wind_week, alpha=0.2, color='green')
    ax3.fill_between(t_week_hours, 0, solar_week, alpha=0.2, color='orange')
    ax3.set_xlabel('时间 (天)')
    ax3.set_ylabel('功率 (MW)')
    ax3.set_title('一周风光出力变化')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 7)
    
    # 4.4 散点图（相关性）
    ax4 = plt.subplot(3, 2, 4)
    ax4.scatter(wind_summer, solar_summer, alpha=0.5, s=20)
    ax4.set_xlabel('风电出力 (MW)')
    ax4.set_ylabel('光伏出力 (MW)')
    ax4.set_title(f'风光出力相关性（r={corr:.3f}）')
    ax4.grid(True, alpha=0.3)
    
    # 添加趋势线
    z = np.polyfit(wind_summer, solar_summer, 1)
    p = np.poly1d(z)
    ax4.plot(wind_summer, p(wind_summer), "r--", alpha=0.8, linewidth=2)
    
    # 4.5 季节对比
    ax5 = plt.subplot(3, 2, 5)
    x_pos = np.arange(len(season_names))
    width = 0.35
    
    ax5.bar(x_pos - width/2, monthly_wind, width, label='风电', color='green', alpha=0.7)
    ax5.bar(x_pos + width/2, monthly_solar, width, label='光伏', color='orange', alpha=0.7)
    ax5.set_xlabel('季节')
    ax5.set_ylabel('平均出力 (MW)')
    ax5.set_title('季节平均出力对比')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(season_names)
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 4.6 关键指标
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    
    metrics_text = f"""
    【风光互补特性关键指标】
    
    ■ 典型日分析（夏季）：
      相关系数: {corr:.3f}
      互补系数: {C:.3f}
      波动平抑: {smoothing_effect:.1%}
    
    ■ 一周发电量：
      风电: {energy_wind_week:,.0f} MWh
      光伏: {energy_solar_week:,.0f} MWh
      总计: {energy_wind_week + energy_solar_week:,.0f} MWh
    
    ■ 季节互补：
      春季: 风电 {monthly_wind[0]:.1f} MW, 光伏 {monthly_solar[0]:.1f} MW
      夏季: 风电 {monthly_wind[1]:.1f} MW, 光伏 {monthly_solar[1]:.1f} MW
      秋季: 风电 {monthly_wind[2]:.1f} MW, 光伏 {monthly_solar[2]:.1f} MW
      冬季: 风电 {monthly_wind[3]:.1f} MW, 光伏 {monthly_solar[3]:.1f} MW
      
      季节相关系数: {season_corr:.3f}
    
    ■ 互补效益：
      ✓ 日内互补：白天光伏，夜间风电
      ✓ 季节互补：冬季风大，夏季光强
      ✓ 波动平抑：联合出力更平滑
      ✓ 容量利用：提高整体利用率
    """
    
    ax6.text(0.05, 0.95, metrics_text, transform=ax6.transAxes,
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('example_07_complementarity_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ 图表已保存: example_07_complementarity_analysis.png")
    plt.show()
    
    # ========================================================================
    # 总结
    # ========================================================================
    
    print("\n\n" + "=" * 80)
    print("【案例7总结】")
    print("=" * 80)
    
    print(f"""
    
    本案例系统分析了风光互补特性：
    
    1️⃣ 日内互补：
       - 光伏白天（6:00-18:00）有出力，夜间为0
       - 风电全天波动，夜间和早晨通常较大
       - 相关系数：{corr:.3f}（负相关表示互补）
       - 互补系数：{C:.3f}（>0表示有互补效果）
    
    2️⃣ 波动平抑：
       - 风电单独标准差：{wind_std:.2f} MW
       - 光伏单独标准差：{solar_std:.2f} MW
       - 联合标准差：{combined_std:.2f} MW
       - 平抑效果：{smoothing_effect:.1%}（联合出力更平滑）
    
    3️⃣ 季节互补：
       - 冬季风力资源丰富（平均{monthly_wind[3]:.1f} MW）
       - 夏季太阳辐射强（平均{monthly_solar[1]:.1f} MW）
       - 季节相关系数：{season_corr:.3f}
    
    4️⃣ 工程意义：
       ✓ 提高新能源整体利用率
       ✓ 降低出力波动，减少对电网冲击
       ✓ 减少储能配置需求
       ✓ 优化系统经济性
    
    5️⃣ 规划建议：
       ✓ 风光合理配比（本案例200MW:150MW）
       ✓ 考虑当地资源特性
       ✓ 配合水电/储能进一步平抑
       ✓ 季节性调度策略优化
    
    """)
    
    print("=" * 80)
    print("🎉 案例7完成！风光互补是多能互补的基础！")
    print("=" * 80)


if __name__ == "__main__":
    main()
