"""
案例19：气候变化对水文过程影响评估
=================================

评估气候变化情景下的水文响应变化，
包括降雨、蒸发、径流、极端事件等。

核心内容：
1. 气候变化情景设计
2. 水文要素变化模拟
from pathlib import Path
3. 水文响应评估
4. 极端事件分析
5. 适应性对策建议

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ClimateScenario:
    """气候变化情景类"""
    
    def __init__(self, name: str, description: str):
        """
        初始化气候情景
        
        Parameters
        ----------
        name : str
            情景名称
        description : str
            情景描述
        """
        self.name = name
        self.description = description
        self.changes = {}
    
    def set_changes(self, 
                   temp_change: float,
                   precip_change: float,
                   evap_change: float):
        """
        设置气候变化幅度
        
        Parameters
        ----------
        temp_change : float
            温度变化 (°C)
        precip_change : float
            降雨变化率 (%)
        evap_change : float
            蒸发变化率 (%)
        """
        self.changes = {
            'temperature': temp_change,
            'precipitation': precip_change,
            'evaporation': evap_change
        }
    
    def apply_to_data(self, 
                     rainfall: np.ndarray,
                     evaporation: np.ndarray) -> tuple:
        """
        应用气候变化到数据
        
        Parameters
        ----------
        rainfall : ndarray
            基准降雨
        evaporation : ndarray
            基准蒸发
            
        Returns
        -------
        modified_rainfall : ndarray
            修正后的降雨
        modified_evap : ndarray
            修正后的蒸发
        """
        # 降雨变化
        precip_factor = 1.0 + self.changes['precipitation'] / 100.0
        modified_rainfall = rainfall * precip_factor
        
        # 蒸发变化（受温度影响）
        # 简化：温度每升高1°C，蒸发增加约3-5%
        temp_effect = 1.0 + self.changes['temperature'] * 0.04
        evap_factor = 1.0 + self.changes['evaporation'] / 100.0
        modified_evap = evaporation * evap_factor * temp_effect
        
        return modified_rainfall, modified_evap


def generate_scenarios():
    """生成气候变化情景"""
    scenarios = []
    
    # 情景0：基准情景（当前气候）
    s0 = ClimateScenario("基准情景", "当前气候条件")
    s0.set_changes(temp_change=0.0, precip_change=0.0, evap_change=0.0)
    scenarios.append(s0)
    
    # 情景1：温和变化（RCP2.6）
    s1 = ClimateScenario("温和变化", "温度+1°C，降雨+5%")
    s1.set_changes(temp_change=1.0, precip_change=5.0, evap_change=3.0)
    scenarios.append(s1)
    
    # 情景2：中度变化（RCP4.5）
    s2 = ClimateScenario("中度变化", "温度+2°C，降雨+10%")
    s2.set_changes(temp_change=2.0, precip_change=10.0, evap_change=5.0)
    scenarios.append(s2)
    
    # 情景3：高度变化（RCP8.5）
    s3 = ClimateScenario("高度变化", "温度+3°C，降雨+15%")
    s3.set_changes(temp_change=3.0, precip_change=15.0, evap_change=8.0)
    scenarios.append(s3)
    
    # 情景4：极端干旱情景
    s4 = ClimateScenario("极端干旱", "温度+2°C，降雨-10%")
    s4.set_changes(temp_change=2.0, precip_change=-10.0, evap_change=10.0)
    scenarios.append(s4)
    
    return scenarios


def analyze_extreme_events(runoff: np.ndarray, threshold: float = 20.0) -> dict:
    """
    分析极端事件
    
    Parameters
    ----------
    runoff : ndarray
        径流序列
    threshold : float
        极端事件阈值
        
    Returns
    -------
    stats : dict
        极端事件统计
    """
    # 识别极端事件
    extreme_events = runoff > threshold
    n_events = np.sum(extreme_events)
    
    # 极端值统计
    if n_events > 0:
        extreme_values = runoff[extreme_events]
        max_extreme = np.max(extreme_values)
        mean_extreme = np.mean(extreme_values)
    else:
        max_extreme = 0
        mean_extreme = 0
    
    return {
        'n_events': n_events,
        'max_value': max_extreme,
        'mean_value': mean_extreme,
        'frequency': n_events / len(runoff) * 100  # 百分比
    }


def run_climate_change_assessment():
    """运行气候变化影响评估"""
    print("\n" + "="*70)
    print("案例19：气候变化对水文过程影响评估")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 生成气候情景
    print("1. 生成气候变化情景...")
    scenarios = generate_scenarios()
    
    for i, s in enumerate(scenarios):
        print(f"   情景{i}: {s.name}")
        if s.changes['temperature'] != 0:
            print(f"      温度变化: {s.changes['temperature']:+.1f}°C")
            print(f"      降雨变化: {s.changes['precipitation']:+.0f}%")
            print(f"      蒸发变化: {s.changes['evaporation']:+.0f}%")
    print()
    
    # 2. 设置水文模型
    print("2. 设置水文模型参数...")
    hydro_params = {
        'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.15,
        'WM': 120.0, 'B': 0.35, 'IM': 0.02,
        'SM': 30.0, 'EX': 1.5, 'KG': 0.4, 'KI': 0.3,
        'CG': 0.98, 'CI': 0.6, 'CS': 0.8
    }
    print("   使用新安江模型\n")
    
    # 3. 生成基准气象数据
    print("3. 生成基准气象数据...")
    n_years = 30  # 30年
    n_days = n_years * 365
    
    # 基准降雨（带季节性和随机性）
    base_rainfall = np.zeros(n_days)
    for year in range(n_years):
        for day in range(365):
            idx = year * 365 + day
            # 季节性（夏季多雨）
            seasonal = 5.0 + 10.0 * np.sin(2 * np.pi * day / 365)
            # 随机性
            random_factor = np.random.gamma(2, 0.5)
            base_rainfall[idx] = seasonal * random_factor
    
    # 基准蒸发
    base_evap = 3.0 + 2.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    
    print(f"   时间跨度: {n_years} 年")
    print(f"   平均降雨: {np.mean(base_rainfall):.1f} mm/d")
    print(f"   平均蒸发: {np.mean(base_evap):.1f} mm/d\n")
    
    # 4. 运行多情景模拟
    print("4. 运行多情景模拟...")
    results = {}
    
    for i, scenario in enumerate(scenarios):
        print(f"   情景{i}: {scenario.name}...")
        
        # 应用气候变化
        rainfall, evap = scenario.apply_to_data(base_rainfall, base_evap)
        
        # 运行水文模型
        model = XinAnJiangModel(hydro_params)
        output = model.run(rainfall, evap)
        
        # 处理NaN
        runoff = np.nan_to_num(output['R'], nan=0.0)
        runoff = np.maximum(runoff, 0.0)
        
        # 分析极端事件
        extreme_stats = analyze_extreme_events(runoff, threshold=20.0)
        
        results[scenario.name] = {
            'rainfall': rainfall,
            'evap': evap,
            'runoff': runoff,
            'extreme_stats': extreme_stats,
            'scenario': scenario
        }
    
    print("\n5. 模拟完成\n")
    
    # 5. 对比分析
    print("="*70)
    print("气候变化影响评估结果")
    print("="*70)
    
    base_name = "基准情景"
    base_result = results[base_name]
    
    print(f"\n【基准情景】")
    print(f"  年均降雨: {np.mean(base_result['rainfall']) * 365:.0f} mm/年")
    print(f"  年均径流: {np.sum(base_result['runoff']) / n_years:.0f} mm/年")
    print(f"  径流系数: {np.sum(base_result['runoff']) / np.sum(base_result['rainfall']):.3f}")
    print(f"  极端事件: {base_result['extreme_stats']['n_events']} 次")
    
    print(f"\n【情景对比】")
    print(f"{'情景':<12} {'年均降雨':<12} {'年均径流':<12} {'径流系数':<10} {'极端事件':<10}")
    print("-" * 70)
    
    for name, data in results.items():
        annual_precip = np.mean(data['rainfall']) * 365
        annual_runoff = np.sum(data['runoff']) / n_years
        runoff_coef = np.sum(data['runoff']) / np.sum(data['rainfall'])
        n_extreme = data['extreme_stats']['n_events']
        
        print(f"{name:<12} {annual_precip:<12.0f} {annual_runoff:<12.0f} "
              f"{runoff_coef:<10.3f} {n_extreme:<10d}")
    
    # 相对变化
    print(f"\n【相对基准情景变化率】")
    print(f"{'情景':<12} {'降雨变化':<12} {'径流变化':<12} {'极端事件变化':<15}")
    print("-" * 60)
    
    base_annual_runoff = np.sum(base_result['runoff']) / n_years
    base_n_extreme = base_result['extreme_stats']['n_events']
    
    for name, data in results.items():
        if name == base_name:
            continue
        
        annual_precip = np.mean(data['rainfall']) * 365
        base_annual_precip = np.mean(base_result['rainfall']) * 365
        precip_change = (annual_precip - base_annual_precip) / base_annual_precip * 100
        
        annual_runoff = np.sum(data['runoff']) / n_years
        runoff_change = (annual_runoff - base_annual_runoff) / base_annual_runoff * 100
        
        n_extreme = data['extreme_stats']['n_events']
        extreme_change = (n_extreme - base_n_extreme) / max(base_n_extreme, 1) * 100
        
        print(f"{name:<12} {precip_change:>+10.1f}% {runoff_change:>+10.1f}% "
              f"{extreme_change:>+13.1f}%")
    
    # 6. 可视化
    print(f"\n6. 生成可视化...")
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 图1：年均降雨对比
    ax1 = fig.add_subplot(gs[0, 0])
    names = list(results.keys())
    annual_precips = [np.mean(data['rainfall']) * 365 for data in results.values()]
    colors = ['green', 'blue', 'orange', 'red', 'brown']
    
    bars = ax1.bar(names, annual_precips, color=colors, alpha=0.7)
    ax1.set_ylabel('年均降雨 (mm)', fontsize=10)
    ax1.set_title('年均降雨对比', fontsize=12, fontweight='bold')
    ax1.set_xticklabels(names, rotation=15, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 图2：年均径流对比
    ax2 = fig.add_subplot(gs[0, 1])
    annual_runoffs = [np.sum(data['runoff']) / n_years for data in results.values()]
    
    bars = ax2.bar(names, annual_runoffs, color=colors, alpha=0.7)
    ax2.set_ylabel('年均径流 (mm)', fontsize=10)
    ax2.set_title('年均径流对比', fontsize=12, fontweight='bold')
    ax2.set_xticklabels(names, rotation=15, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 图3：径流系数对比
    ax3 = fig.add_subplot(gs[1, 0])
    runoff_coefs = [np.sum(data['runoff']) / np.sum(data['rainfall']) 
                   for data in results.values()]
    
    bars = ax3.bar(names, runoff_coefs, color=colors, alpha=0.7)
    ax3.set_ylabel('径流系数', fontsize=10)
    ax3.set_title('径流系数对比', fontsize=12, fontweight='bold')
    ax3.set_xticklabels(names, rotation=15, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 图4：极端事件频次
    ax4 = fig.add_subplot(gs[1, 1])
    n_extremes = [data['extreme_stats']['n_events'] for data in results.values()]
    
    bars = ax4.bar(names, n_extremes, color=colors, alpha=0.7)
    ax4.set_ylabel('极端事件次数', fontsize=10)
    ax4.set_title('极端事件频次对比', fontsize=12, fontweight='bold')
    ax4.set_xticklabels(names, rotation=15, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # 图5：径流年际变化（选几个情景）
    ax5 = fig.add_subplot(gs[2, :])
    selected_scenarios = ['基准情景', '中度变化', '高度变化', '极端干旱']
    colors_line = ['green', 'orange', 'red', 'brown']
    
    for name, color in zip(selected_scenarios, colors_line):
        if name in results:
            runoff = results[name]['runoff']
            # 计算年径流
            annual_runoff_series = []
            for year in range(n_years):
                start_idx = year * 365
                end_idx = (year + 1) * 365
                annual_runoff_series.append(np.sum(runoff[start_idx:end_idx]))
            
            ax5.plot(range(n_years), annual_runoff_series, 
                    color=color, linewidth=2, label=name, marker='o', markersize=4)
    
    ax5.set_xlabel('年份', fontsize=11)
    ax5.set_ylabel('年径流 (mm)', fontsize=10)
    ax5.set_title('径流年际变化', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    plt.savefig(f'{output_dir}/climate_change_assessment.png', 
                dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/climate_change_assessment.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_climate_change_assessment()
