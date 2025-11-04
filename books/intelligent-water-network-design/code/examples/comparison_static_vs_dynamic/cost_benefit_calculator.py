#!/usr/bin/env python3
"""
成本效益计算器
==============

功能: 计算静态设计与动态设计的全生命周期成本效益

使用方法:
    python3 cost_benefit_calculator.py
    
    或作为模块导入:
    from cost_benefit_calculator import CostBenefitCalculator
    calculator = CostBenefitCalculator()
    result = calculator.calculate(project_params)
    
输出:
    - 初始投资对比
    - 年运行成本对比
    - 投资回收期
    - 20年全生命周期成本
    - 敏感性分析
    - 决策建议
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

print("="*80)
print("  成本效益计算器 v1.0")
print("="*80)
print()

# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class ProjectParams:
    """项目参数"""
    # 基本信息
    project_name: str = "示例工程"
    project_scale: float = 500  # 工程规模(万元)
    control_points: int = 1     # 控制点数量
    
    # 静态设计成本
    static_initial_cost: float = 30       # 初始投资(万元)
    static_annual_staff: int = 13         # 年运行人员数
    static_staff_salary: float = 12       # 人员年薪(万元)
    static_annual_power: float = 20       # 年电费(万元)
    static_annual_maintain: float = 4     # 年维护费(万元)
    
    # L2级动态设计增量成本
    l2_sensor_cost: float = 1.5           # 传感器成本(万元)
    l2_controller_cost: float = 3.5       # 控制系统成本(万元)
    l2_annual_staff: int = 3              # 年运行人员数
    l2_power_saving: float = 0.4          # 电费节省率(0-1)
    l2_maintain_cost: float = 12          # 年维护费(万元,含系统维护)
    
    # L3级协调控制增量成本
    l3_sensor_multiplier: float = 4       # 传感器倍数
    l3_controller_multiplier: float = 4   # 控制器倍数
    l3_coord_cost: float = 50             # 协调系统额外成本(万元)
    l3_annual_staff: int = 8              # 年运行人员数
    l3_power_saving: float = 0.3          # 电费节省率
    l3_maintain_cost: float = 44          # 年维护费(万元)
    
    # 效益参数
    precision_improvement_value: float = 10  # 精度提升带来的年效益(万元)
    automation_value: float = 20             # 自动化带来的年效益(万元)
    
    # 其他参数
    discount_rate: float = 0.05           # 贴现率
    analysis_years: int = 20              # 分析年限


class CostBenefitCalculator:
    """成本效益计算器"""
    
    def __init__(self):
        pass
    
    def calculate_static_costs(self, params: ProjectParams) -> Dict:
        """计算静态设计成本"""
        # 初始投资
        initial = params.static_initial_cost
        
        # 年运行成本
        annual_staff = params.static_annual_staff * params.static_staff_salary
        annual_power = params.static_annual_power
        annual_maintain = params.static_annual_maintain
        annual_total = annual_staff + annual_power + annual_maintain
        
        # 全生命周期成本
        lifecycle = initial + annual_total * params.analysis_years
        
        # NPV
        npv = initial + sum([annual_total / (1 + params.discount_rate)**year 
                            for year in range(1, params.analysis_years+1)])
        
        return {
            '初始投资': initial,
            '年运行成本': annual_total,
            '年人工成本': annual_staff,
            '年电费': annual_power,
            '年维护费': annual_maintain,
            '20年总成本': lifecycle,
            'NPV': npv
        }
    
    def calculate_l2_costs(self, params: ProjectParams) -> Dict:
        """计算L2级动态设计成本"""
        # 初始投资 = 静态 + 传感器 + 控制系统
        initial = (params.static_initial_cost + 
                  params.l2_sensor_cost + 
                  params.l2_controller_cost)
        
        # 年运行成本
        annual_staff = params.l2_annual_staff * params.static_staff_salary
        annual_power = params.static_annual_power * (1 - params.l2_power_saving)
        annual_maintain = params.l2_maintain_cost
        annual_total = annual_staff + annual_power + annual_maintain
        
        # 全生命周期成本
        lifecycle = initial + annual_total * params.analysis_years
        
        # NPV
        npv = initial + sum([annual_total / (1 + params.discount_rate)**year 
                            for year in range(1, params.analysis_years+1)])
        
        return {
            '初始投资': initial,
            '年运行成本': annual_total,
            '年人工成本': annual_staff,
            '年电费': annual_power,
            '年维护费': annual_maintain,
            '20年总成本': lifecycle,
            'NPV': npv,
            '增量投资': initial - params.static_initial_cost
        }
    
    def calculate_l3_costs(self, params: ProjectParams) -> Dict:
        """计算L3级协调控制成本"""
        # 初始投资 = 静态 + 传感器×倍数 + 控制系统×倍数 + 协调系统
        initial = (params.static_initial_cost * params.control_points +
                  params.l2_sensor_cost * params.l3_sensor_multiplier +
                  params.l2_controller_cost * params.l3_controller_multiplier +
                  params.l3_coord_cost)
        
        # 年运行成本
        annual_staff = params.l3_annual_staff * params.static_staff_salary
        annual_power = params.static_annual_power * params.control_points * (1 - params.l3_power_saving)
        annual_maintain = params.l3_maintain_cost
        annual_total = annual_staff + annual_power + annual_maintain
        
        # 全生命周期成本
        lifecycle = initial + annual_total * params.analysis_years
        
        # NPV
        npv = initial + sum([annual_total / (1 + params.discount_rate)**year 
                            for year in range(1, params.analysis_years+1)])
        
        static_baseline = params.static_initial_cost * params.control_points
        
        return {
            '初始投资': initial,
            '年运行成本': annual_total,
            '年人工成本': annual_staff,
            '年电费': annual_power,
            '年维护费': annual_maintain,
            '20年总成本': lifecycle,
            'NPV': npv,
            '增量投资': initial - static_baseline
        }
    
    def calculate_payback(self, increment_invest: float, annual_saving: float) -> float:
        """计算投资回收期(年)"""
        if annual_saving <= 0:
            return float('inf')
        return increment_invest / annual_saving
    
    def sensitivity_analysis(self, params: ProjectParams, 
                           param_name: str, 
                           variation_range: List[float]) -> Dict:
        """敏感性分析"""
        results = {
            'static': [],
            'l2': [],
            'l3': []
        }
        
        original_value = getattr(params, param_name)
        
        for variation in variation_range:
            # 修改参数
            setattr(params, param_name, original_value * variation)
            
            # 重新计算
            static = self.calculate_static_costs(params)
            l2 = self.calculate_l2_costs(params)
            l3 = self.calculate_l3_costs(params)
            
            results['static'].append(static['20年总成本'])
            results['l2'].append(l2['20年总成本'])
            results['l3'].append(l3['20年总成本'])
        
        # 恢复原始值
        setattr(params, param_name, original_value)
        
        return results
    
    def generate_report(self, params: ProjectParams, 
                       output_file: str = 'cost_benefit_report.txt') -> str:
        """生成成本效益报告"""
        static = self.calculate_static_costs(params)
        l2 = self.calculate_l2_costs(params)
        l3 = self.calculate_l3_costs(params)
        
        # 计算对比
        l2_saving = static['年运行成本'] - l2['年运行成本']
        l2_payback = self.calculate_payback(l2['增量投资'], l2_saving)
        l2_lifecycle_saving = static['20年总成本'] - l2['20年总成本']
        
        static_multi = static['初始投资'] * params.control_points
        l3_saving_vs_static_multi = (static['年运行成本'] * params.control_points - 
                                     l3['年运行成本'])
        l3_payback = self.calculate_payback(l3['增量投资'], l3_saving_vs_static_multi)
        
        lines = []
        lines.append("="*80)
        lines.append("  成本效益分析报告")
        lines.append("="*80)
        lines.append(f"\n项目名称: {params.project_name}")
        lines.append(f"工程规模: {params.project_scale}万元")
        lines.append(f"控制点数: {params.control_points}个")
        lines.append(f"分析年限: {params.analysis_years}年")
        lines.append(f"贴现率: {params.discount_rate*100}%\n")
        
        lines.append("="*80)
        lines.append("  一、初始投资对比")
        lines.append("="*80)
        lines.append("")
        lines.append(f"{'方案':<15} {'初始投资(万元)':<15} {'增量投资':<15} {'增量比例'}")
        lines.append("-"*80)
        lines.append(f"{'静态设计':<15} {static['初始投资']:<15.1f} {'-':<15} {'-'}")
        lines.append(f"{'L2级动态':<15} {l2['初始投资']:<15.1f} {l2['增量投资']:<15.1f} {(l2['增量投资']/static['初始投资']*100):.1f}%")
        
        static_multi_val = static['初始投资'] * params.control_points
        lines.append(f"{'静态设计×'+str(params.control_points):<15} {static_multi_val:<15.1f} {'-':<15} {'-'}")
        lines.append(f"{'L3级协调':<15} {l3['初始投资']:<15.1f} {l3['增量投资']:<15.1f} {(l3['增量投资']/static_multi_val*100):.1f}%")
        
        lines.append("\n" + "="*80)
        lines.append("  二、年运行成本对比")
        lines.append("="*80)
        lines.append("")
        lines.append(f"{'方案':<15} {'人工成本':<12} {'电费':<10} {'维护费':<10} {'合计':<10} {'节省'}")
        lines.append("-"*80)
        lines.append(f"{'静态设计':<15} {static['年人工成本']:<12.1f} {static['年电费']:<10.1f} {static['年维护费']:<10.1f} {static['年运行成本']:<10.1f} {'-'}")
        lines.append(f"{'L2级动态':<15} {l2['年人工成本']:<12.1f} {l2['年电费']:<10.1f} {l2['年维护费']:<10.1f} {l2['年运行成本']:<10.1f} {l2_saving:.1f}({l2_saving/static['年运行成本']*100:.0f}%)")
        
        static_annual_multi = static['年运行成本'] * params.control_points
        lines.append(f"{'静态设计×'+str(params.control_points):<15} {static['年人工成本']*params.control_points:<12.1f} {static['年电费']*params.control_points:<10.1f} {static['年维护费']*params.control_points:<10.1f} {static_annual_multi:<10.1f} {'-'}")
        lines.append(f"{'L3级协调':<15} {l3['年人工成本']:<12.1f} {l3['年电费']:<10.1f} {l3['年维护费']:<10.1f} {l3['年运行成本']:<10.1f} {l3_saving_vs_static_multi:.1f}({l3_saving_vs_static_multi/static_annual_multi*100:.0f}%)")
        
        lines.append("\n" + "="*80)
        lines.append("  三、投资回收期分析")
        lines.append("="*80)
        lines.append("")
        lines.append("【L2级 vs 静态设计】")
        lines.append(f"  增量投资: {l2['增量投资']:.1f}万元")
        lines.append(f"  年节省: {l2_saving:.1f}万元")
        lines.append(f"  投资回收期: {l2_payback:.2f}年 (约{l2_payback*12:.0f}个月)")
        
        lines.append("")
        lines.append("【L3级 vs 静态设计×{0}】".format(params.control_points))
        lines.append(f"  增量投资: {l3['增量投资']:.1f}万元")
        lines.append(f"  年节省: {l3_saving_vs_static_multi:.1f}万元")
        if l3_payback < 100:
            lines.append(f"  投资回收期: {l3_payback:.2f}年 (约{l3_payback*12:.0f}个月)")
        else:
            lines.append(f"  投资回收期: 无法回收(运行成本未降低)")
        
        lines.append("\n" + "="*80)
        lines.append("  四、全生命周期成本({0}年)".format(params.analysis_years))
        lines.append("="*80)
        lines.append("")
        lines.append(f"{'方案':<20} {'总成本(万元)':<15} {'相对静态节省'}")
        lines.append("-"*80)
        lines.append(f"{'静态设计':<20} {static['20年总成本']:<15.1f} {'-'}")
        lines.append(f"{'L2级动态':<20} {l2['20年总成本']:<15.1f} {l2_lifecycle_saving:.1f} ({l2_lifecycle_saving/static['20年总成本']*100:.1f}%)")
        
        static_lifecycle_multi = static['20年总成本'] * params.control_points
        l3_lifecycle_saving = static_lifecycle_multi - l3['20年总成本']
        lines.append(f"{'静态设计×'+str(params.control_points):<20} {static_lifecycle_multi:<15.1f} {'-'}")
        lines.append(f"{'L3级协调':<20} {l3['20年总成本']:<15.1f} {l3_lifecycle_saving:.1f} ({l3_lifecycle_saving/static_lifecycle_multi*100:.1f}%)")
        
        lines.append("\n" + "="*80)
        lines.append("  五、决策建议")
        lines.append("="*80)
        lines.append("")
        
        # 基于分析给出建议
        if params.project_scale < 100:
            lines.append("【工程规模较小(<100万)】")
            lines.append("  建议: 采用静态设计或L1级(辅助监测)")
            lines.append("  理由: 智能化投资占比过高,不够经济")
        elif params.project_scale < 1000:
            lines.append("【工程规模中等(100-1000万)】")
            lines.append("  ⭐ 强烈推荐: L2级动态设计")
            lines.append(f"  理由: 投资增量仅{l2['增量投资']/static['初始投资']*100:.0f}%, 回收期{l2_payback:.1f}年")
            lines.append(f"        20年节省{l2_lifecycle_saving:.0f}万元({l2_lifecycle_saving/static['20年总成本']*100:.0f}%)")
        else:
            lines.append("【工程规模较大(>1000万)】")
            if params.control_points > 2:
                lines.append("  ⭐ 推荐: L3级或更高")
                lines.append("  理由: 多点耦合系统,需要协调控制")
            else:
                lines.append("  ⭐ 推荐: L2-L3级")
                lines.append("  理由: 单点建议L2,多点建议L3")
        
        lines.append("")
        lines.append("【关键指标】")
        if l2_payback < 3:
            lines.append(f"  ✓ L2级投资回收期很短({l2_payback:.1f}年), 强烈推荐")
        elif l2_payback < 5:
            lines.append(f"  ✓ L2级投资回收期可接受({l2_payback:.1f}年), 推荐")
        else:
            lines.append(f"  ⚠ L2级投资回收期较长({l2_payback:.1f}年), 需慎重")
        
        if l2_lifecycle_saving > 0:
            lines.append(f"  ✓ L2级全生命周期节省{l2_lifecycle_saving:.0f}万元, 经济效益显著")
        
        lines.append("\n" + "="*80)
        lines.append("报告完成")
        lines.append("="*80)
        
        report_text = '\n'.join(lines)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return report_text
    
    def plot_comparison(self, params: ProjectParams, 
                       output_file: str = 'cost_benefit_comparison.png'):
        """绘制成本对比图"""
        static = self.calculate_static_costs(params)
        l2 = self.calculate_l2_costs(params)
        l3 = self.calculate_l3_costs(params)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 子图1: 初始投资对比
        ax = axes[0, 0]
        categories = ['Static', 'L2', f'Static×{params.control_points}', 'L3']
        values = [
            static['初始投资'],
            l2['初始投资'],
            static['初始投资'] * params.control_points,
            l3['初始投资']
        ]
        colors = ['gray', 'blue', 'lightgray', 'green']
        bars = ax.bar(range(4), values, color=colors, alpha=0.7)
        ax.set_ylabel('Investment (10K CNY)', fontweight='bold')
        ax.set_title('(a) Initial Investment Comparison', fontweight='bold')
        ax.set_xticks(range(4))
        ax.set_xticklabels(categories)
        ax.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x()+bar.get_width()/2, val, f'{val:.0f}', 
                   ha='center', va='bottom', fontweight='bold')
        
        # 子图2: 年运行成本对比
        ax = axes[0, 1]
        values = [
            static['年运行成本'],
            l2['年运行成本'],
            static['年运行成本'] * params.control_points,
            l3['年运行成本']
        ]
        bars = ax.bar(range(4), values, color=colors, alpha=0.7)
        ax.set_ylabel('Annual Cost (10K CNY)', fontweight='bold')
        ax.set_title('(b) Annual Operating Cost', fontweight='bold')
        ax.set_xticks(range(4))
        ax.set_xticklabels(categories)
        ax.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x()+bar.get_width()/2, val, f'{val:.0f}', 
                   ha='center', va='bottom', fontweight='bold')
        
        # 子图3: 20年累计成本
        ax = axes[1, 0]
        years = np.arange(0, params.analysis_years+1)
        
        static_cum = [static['初始投资'] + static['年运行成本']*y for y in years]
        l2_cum = [l2['初始投资'] + l2['年运行成本']*y for y in years]
        l3_cum = [l3['初始投资'] + l3['年运行成本']*y for y in years]
        
        ax.plot(years, static_cum, 'o-', linewidth=2, color='gray', label='Static', markersize=3)
        ax.plot(years, l2_cum, 's-', linewidth=2, color='blue', label='L2', markersize=3)
        ax.plot(years, l3_cum, '^-', linewidth=2, color='green', label=f'L3({params.control_points} gates)', markersize=3)
        
        ax.set_xlabel('Years', fontweight='bold')
        ax.set_ylabel('Cumulative Cost (10K CNY)', fontweight='bold')
        ax.set_title('(c) Lifecycle Cost (20 Years)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 标注投资回收期
        l2_saving = static['年运行成本'] - l2['年运行成本']
        if l2_saving > 0:
            payback = l2['增量投资'] / l2_saving
            if payback < params.analysis_years:
                ax.axvline(x=payback, color='blue', linestyle='--', alpha=0.5)
                ax.text(payback+1, static_cum[-1]*0.5, f'L2 Payback\n{payback:.1f}y',
                       fontsize=9, color='blue')
        
        # 子图4: 成本构成
        ax = axes[1, 1]
        
        categories = ['Static', 'L2']
        staff_costs = [static['年人工成本'], l2['年人工成本']]
        power_costs = [static['年电费'], l2['年电费']]
        maintain_costs = [static['年维护费'], l2['年维护费']]
        
        x = np.arange(len(categories))
        width = 0.6
        
        p1 = ax.bar(x, staff_costs, width, label='Staff', color='#FF9999')
        p2 = ax.bar(x, power_costs, width, bottom=staff_costs, label='Power', color='#66B2FF')
        p3 = ax.bar(x, maintain_costs, width, 
                   bottom=np.array(staff_costs)+np.array(power_costs),
                   label='Maintenance', color='#99FF99')
        
        ax.set_ylabel('Annual Cost (10K CNY)', fontweight='bold')
        ax.set_title('(d) Annual Cost Breakdown', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # 添加总数标签
        for i, (s, p, m) in enumerate(zip(staff_costs, power_costs, maintain_costs)):
            total = s + p + m
            ax.text(i, total, f'{total:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle(f'Cost-Benefit Analysis: {params.project_name}',
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == '__main__':
    print("【示例】单控制点中型工程")
    print("-" * 80)
    
    # 创建计算器
    calculator = CostBenefitCalculator()
    
    # 定义项目参数
    params = ProjectParams(
        project_name="灌溉渠道闸门控制",
        project_scale=500,
        control_points=1
    )
    
    # 生成报告
    report = calculator.generate_report(params, 'cost_benefit_report.txt')
    print(report)
    print("\n✓ 成本效益报告已保存: cost_benefit_report.txt")
    
    # 绘制对比图
    calculator.plot_comparison(params, 'cost_benefit_comparison.png')
    print("✓ 成本对比图已保存: cost_benefit_comparison.png")
    
    print("\n" + "="*80)
    print("  计算完成!")
    print("="*80)
    print()
    print("生成的文件:")
    print("  1. cost_benefit_report.txt - 成本效益分析报告")
    print("  2. cost_benefit_comparison.png - 成本对比图(4子图)")
    print()
    print("使用说明:")
    print("  1. 修改ProjectParams参数适配你的工程")
    print("  2. 运行: python3 cost_benefit_calculator.py")
    print("  3. 或导入: from cost_benefit_calculator import CostBenefitCalculator")
    print()
    print("="*80)
