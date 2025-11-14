"""
案例16：人类活动对产汇流影响评估
===============================

评估土地利用变化、城镇化等人类活动
对流域产汇流过程的影响。

核心内容：
1. 土地利用变化情景设计
2. 参数修正方法
from pathlib import Path
3. 产汇流过程模拟
4. 多情景对比分析
5. 影响量化评估

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


class LandUseScenario:
    """土地利用情景类"""
    
    def __init__(self, name: str, description: str):
        """
        初始化土地利用情景
        
        Parameters
        ----------
        name : str
            情景名称
        description : str
            情景描述
        """
        self.name = name
        self.description = description
        self.land_use = {}
        
    def set_land_use(self, forest: float, urban: float, 
                     agriculture: float, water: float):
        """
        设置土地利用比例
        
        Parameters
        ----------
        forest : float
            森林比例 (0-1)
        urban : float
            城镇比例 (0-1)
        agriculture : float
            农田比例 (0-1)
        water : float
            水体比例 (0-1)
        """
        total = forest + urban + agriculture + water
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"土地利用比例之和应为1.0，当前为{total}")
        
        self.land_use = {
            'forest': forest,
            'urban': urban,
            'agriculture': agriculture,
            'water': water
        }
    
    def adjust_parameters(self, base_params: dict) -> dict:
        """
        根据土地利用调整水文模型参数
        
        Parameters
        ----------
        base_params : dict
            基准参数（自然状态）
            
        Returns
        -------
        adjusted_params : dict
            调整后的参数
        """
        params = base_params.copy()
        
        # 获取土地利用比例
        urban = self.land_use['urban']
        forest = self.land_use['forest']
        
        # 1. 城镇化影响：增加不透水面积
        # 蓄水容量减小
        impervious_factor = 1.0 - 0.6 * urban
        params['WM'] = base_params['WM'] * impervious_factor
        params['UM'] = base_params['UM'] * impervious_factor
        params['LM'] = base_params['LM'] * impervious_factor
        
        # 蒸散发能力减弱
        params['C'] = base_params['C'] * (1.0 - 0.3 * urban)
        
        # 产流更快（B参数减小）
        params['B'] = base_params['B'] * (1.0 - 0.4 * urban)
        
        # 2. 森林覆盖影响：增强蓄水和蒸散发
        forest_factor = 0.8 + 0.4 * forest
        params['C'] = params['C'] * forest_factor
        
        # 地下水补给增加
        params['KG'] = base_params['KG'] * (1.0 + 0.2 * forest)
        
        # 3. 汇流参数调整
        # 城镇化加快汇流
        params['CS'] = base_params['CS'] * (1.0 + 0.3 * urban)
        params['CI'] = base_params['CI'] * (1.0 + 0.2 * urban)
        
        return params


def generate_scenarios():
    """生成多个土地利用情景"""
    scenarios = []
    
    # 情景1：自然状态（基准）
    s1 = LandUseScenario("自然状态", "原始森林为主，无城镇化")
    s1.set_land_use(forest=0.70, urban=0.05, agriculture=0.20, water=0.05)
    scenarios.append(s1)
    
    # 情景2：轻度城镇化
    s2 = LandUseScenario("轻度城镇化", "15%城镇化，森林减少")
    s2.set_land_use(forest=0.55, urban=0.15, agriculture=0.25, water=0.05)
    scenarios.append(s2)
    
    # 情景3：中度城镇化
    s3 = LandUseScenario("中度城镇化", "30%城镇化，森林进一步减少")
    s3.set_land_use(forest=0.40, urban=0.30, agriculture=0.25, water=0.05)
    scenarios.append(s3)
    
    # 情景4：高度城镇化
    s4 = LandUseScenario("高度城镇化", "50%城镇化，森林大幅减少")
    s4.set_land_use(forest=0.20, urban=0.50, agriculture=0.25, water=0.05)
    scenarios.append(s4)
    
    return scenarios


def run_human_impact_assessment():
    """运行人类活动影响评估"""
    print("\n" + "="*70)
    print("案例16：人类活动对产汇流影响评估")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 生成情景
    print("1. 生成土地利用情景...")
    scenarios = generate_scenarios()
    
    for i, s in enumerate(scenarios, 1):
        print(f"   情景{i}: {s.name}")
        print(f"      森林: {s.land_use['forest']*100:.0f}%, "
              f"城镇: {s.land_use['urban']*100:.0f}%, "
              f"农田: {s.land_use['agriculture']*100:.0f}%")
    print()
    
    # 2. 设置基准参数
    print("2. 设置基准水文参数...")
    base_params = {
        'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.15,
        'WM': 120.0, 'B': 0.35, 'IM': 0.02,
        'SM': 30.0, 'EX': 1.5, 'KG': 0.4, 'KI': 0.3,
        'CG': 0.98, 'CI': 0.6, 'CS': 0.8
    }
    print("   使用新安江模型\n")
    
    # 3. 生成降雨数据
    print("3. 生成降雨过程...")
    n_days = 90
    rainfall = np.zeros(n_days)
    
    # 3次洪峰
    flood_days = [20, 50, 75]
    for day in flood_days:
        for i in range(5):
            if day + i < n_days:
                rainfall[day + i] = 30 * np.exp(-0.3 * i) * (0.8 + 0.4 * np.random.rand())
    
    # 蒸发
    evaporation = 3.0 + 2.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    
    print(f"   时间步数: {n_days} 天")
    print(f"   总降雨: {np.sum(rainfall):.1f} mm\n")
    
    # 4. 运行多情景模拟
    print("4. 运行多情景模拟...")
    results = {}
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"   情景{i}: {scenario.name}...")
        
        # 调整参数
        params = scenario.adjust_parameters(base_params)
        
        # 运行模型
        model = XinAnJiangModel(params)
        output = model.run(rainfall, evaporation)
        
        # 处理NaN
        runoff = np.nan_to_num(output['R'], nan=0.0)
        runoff = np.maximum(runoff, 0.0)
        
        results[scenario.name] = {
            'runoff': runoff,
            'params': params,
            'scenario': scenario
        }
    
    print("\n5. 模拟完成\n")
    
    # 5. 统计分析
    print("="*70)
    print("多情景产汇流影响评估结果")
    print("="*70)
    
    base_name = "自然状态"
    base_runoff = results[base_name]['runoff']
    base_total = np.sum(base_runoff)
    
    print(f"\n【基准情景】{base_name}")
    print(f"  总降雨: {np.sum(rainfall):.1f} mm")
    print(f"  总径流: {base_total:.1f} mm")
    print(f"  径流系数: {base_total / np.sum(rainfall):.3f}")
    print(f"  峰值径流: {np.max(base_runoff):.2f} mm/d")
    
    print(f"\n【情景对比】")
    print(f"{'情景名称':<15} {'总径流(mm)':<12} {'变化率':<10} "
          f"{'峰值(mm/d)':<12} {'变化率':<10}")
    print("-" * 70)
    
    for name, data in results.items():
        runoff = data['runoff']
        total = np.sum(runoff)
        peak = np.max(runoff)
        
        change_total = (total - base_total) / base_total * 100
        change_peak = (peak - np.max(base_runoff)) / np.max(base_runoff) * 100
        
        print(f"{name:<15} {total:<12.1f} {change_total:>+8.1f}% "
              f"{peak:<12.2f} {change_peak:>+8.1f}%")
    
    # 6. 参数变化分析
    print(f"\n【关键参数变化】")
    print(f"{'情景':<15} {'WM':<8} {'B':<8} {'C':<8} {'CS':<8}")
    print("-" * 50)
    
    for name, data in results.items():
        params = data['params']
        print(f"{name:<15} {params['WM']:<8.1f} {params['B']:<8.3f} "
              f"{params['C']:<8.3f} {params['CS']:<8.2f}")
    
    # 7. 可视化
    print(f"\n6. 生成可视化...")
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 图1：土地利用情景
    ax1 = fig.add_subplot(gs[0, 0])
    land_types = ['森林', '城镇', '农田', '水体']
    x = np.arange(len(scenarios))
    width = 0.2
    
    for i, land_type in enumerate(['forest', 'urban', 'agriculture', 'water']):
        values = [s.land_use[land_type] * 100 for s in scenarios]
        ax1.bar(x + i * width, values, width, label=land_types[i])
    
    ax1.set_xlabel('情景', fontsize=11)
    ax1.set_ylabel('比例 (%)', fontsize=10)
    ax1.set_title('土地利用变化情景', fontsize=12, fontweight='bold')
    ax1.set_xticks(x + width * 1.5)
    ax1.set_xticklabels([s.name for s in scenarios], rotation=15, ha='right')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 图2：径流过程对比
    ax2 = fig.add_subplot(gs[0, 1])
    time = np.arange(n_days)
    colors = ['green', 'blue', 'orange', 'red']
    
    for (name, data), color in zip(results.items(), colors):
        ax2.plot(time, data['runoff'], linewidth=2, label=name, color=color)
    
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('径流 (mm/d)', fontsize=10)
    ax2.set_title('径流过程对比', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3：总径流量对比
    ax3 = fig.add_subplot(gs[1, 0])
    names = list(results.keys())
    totals = [np.sum(data['runoff']) for data in results.values()]
    colors_bar = ['green', 'blue', 'orange', 'red']
    
    bars = ax3.bar(names, totals, color=colors_bar, alpha=0.7)
    ax3.axhline(y=base_total, color='green', linestyle='--', 
                linewidth=2, label='基准值')
    ax3.set_ylabel('总径流 (mm)', fontsize=10)
    ax3.set_title('总径流量对比', fontsize=12, fontweight='bold')
    ax3.set_xticklabels(names, rotation=15, ha='right')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    # 图4：峰值径流对比
    ax4 = fig.add_subplot(gs[1, 1])
    peaks = [np.max(data['runoff']) for data in results.values()]
    
    bars = ax4.bar(names, peaks, color=colors_bar, alpha=0.7)
    ax4.axhline(y=np.max(base_runoff), color='green', linestyle='--', 
                linewidth=2, label='基准值')
    ax4.set_ylabel('峰值径流 (mm/d)', fontsize=10)
    ax4.set_title('峰值径流对比', fontsize=12, fontweight='bold')
    ax4.set_xticklabels(names, rotation=15, ha='right')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    # 图5：径流系数变化
    ax5 = fig.add_subplot(gs[2, 0])
    coeffs = [np.sum(data['runoff']) / np.sum(rainfall) for data in results.values()]
    
    bars = ax5.bar(names, coeffs, color=colors_bar, alpha=0.7)
    ax5.set_ylabel('径流系数', fontsize=10)
    ax5.set_title('径流系数变化', fontsize=12, fontweight='bold')
    ax5.set_xticklabels(names, rotation=15, ha='right')
    ax5.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 图6：关键参数变化
    ax6 = fig.add_subplot(gs[2, 1])
    param_names = ['WM', 'B', 'C']
    x_param = np.arange(len(scenarios))
    width_param = 0.25
    
    for i, pname in enumerate(param_names):
        # 归一化到0-1
        base_val = base_params[pname]
        values = [data['params'][pname] / base_val for data in results.values()]
        ax6.bar(x_param + i * width_param, values, width_param, label=pname)
    
    ax6.axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax6.set_xlabel('情景', fontsize=11)
    ax6.set_ylabel('参数相对变化', fontsize=10)
    ax6.set_title('关键参数变化（相对基准）', fontsize=12, fontweight='bold')
    ax6.set_xticks(x_param + width_param)
    ax6.set_xticklabels([s.name for s in scenarios], rotation=15, ha='right')
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.savefig(f'{output_dir}/human_impact_assessment.png', 
                dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/human_impact_assessment.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_human_impact_assessment()
