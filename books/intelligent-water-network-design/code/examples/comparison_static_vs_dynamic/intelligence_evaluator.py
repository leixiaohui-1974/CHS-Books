#!/usr/bin/env python3
"""
智能化等级评估工具
==================

功能: 独立的智能化等级评估工具，可用于评估任何水利工程项目的智能化等级

使用方法:
    python3 intelligence_evaluator.py
    
    或作为模块导入:
    from intelligence_evaluator import IntelligenceEvaluator
    evaluator = IntelligenceEvaluator()
    result = evaluator.evaluate(your_data)
    
输出:
    - 5大维度评分
    - 综合得分
    - 达成等级(L0-L5)
    - 详细评估报告
    - 改进建议
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np

print("="*80)
print("  智能化等级评估工具 v1.0")
print("="*80)
print()

# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class EvaluationCriteria:
    """评估标准"""
    # 自动化程度维度
    automation_sensors: int = 0           # 传感器数量
    automation_controllers: int = 0       # 控制器数量
    automation_manual_freq: float = 0     # 人工干预频率(次/天)
    automation_24h: bool = False          # 24小时运行能力
    automation_remote: bool = False       # 远程监控能力
    
    # 控制精度维度
    precision_steady_error: float = 100   # 稳态误差(cm)
    precision_max_error: float = 100      # 最大误差(cm)
    precision_target: float = 5.0         # 目标精度(cm)
    
    # 响应速度维度
    speed_response_time: float = 60       # 响应时间(分钟)
    speed_settling_time: float = 60       # 调节时间(分钟)
    speed_control_cycle: float = 600      # 控制周期(秒)
    
    # 鲁棒性维度
    robust_test_scenarios: int = 2        # 测试场景数
    robust_fault_tolerance: bool = False  # 容错能力
    robust_sensor_redundancy: bool = False # 传感器冗余
    robust_disturbance_rejection: float = 0.5  # 扰动抑制(0-1)
    
    # 可维护性维度
    maintain_modular: bool = False        # 模块化设计
    maintain_documentation: bool = False  # 文档完整性
    maintain_diagnosis: bool = False      # 故障诊断能力
    maintain_code_quality: float = 0.5    # 代码质量(0-1)


class IntelligenceEvaluator:
    """智能化等级评估器"""
    
    def __init__(self):
        self.level_thresholds = {
            'L0': (0, 39),
            'L1': (40, 59),
            'L2': (60, 79),
            'L3': (80, 89),
            'L4': (90, 95),
            'L5': (96, 100)
        }
        
    def evaluate_automation(self, criteria: EvaluationCriteria) -> Tuple[float, str]:
        """评估自动化程度 (0-100分)"""
        score = 0
        details = []
        
        # 传感器数量 (0-20分)
        sensor_score = min(criteria.automation_sensors * 3, 20)
        score += sensor_score
        details.append(f"传感器数量: {criteria.automation_sensors}个 → {sensor_score:.0f}分")
        
        # 控制器数量 (0-20分)
        controller_score = min(criteria.automation_controllers * 5, 20)
        score += controller_score
        details.append(f"控制器数量: {criteria.automation_controllers}个 → {controller_score:.0f}分")
        
        # 人工干预频率 (0-30分)
        if criteria.automation_manual_freq == 0:
            manual_score = 30
        elif criteria.automation_manual_freq < 1:
            manual_score = 25
        elif criteria.automation_manual_freq < 3:
            manual_score = 15
        else:
            manual_score = max(0, 30 - criteria.automation_manual_freq * 3)
        score += manual_score
        details.append(f"人工干预: {criteria.automation_manual_freq:.1f}次/天 → {manual_score:.0f}分")
        
        # 24小时运行 (0-15分)
        h24_score = 15 if criteria.automation_24h else 0
        score += h24_score
        details.append(f"24小时运行: {'是' if criteria.automation_24h else '否'} → {h24_score:.0f}分")
        
        # 远程监控 (0-15分)
        remote_score = 15 if criteria.automation_remote else 0
        score += remote_score
        details.append(f"远程监控: {'是' if criteria.automation_remote else '否'} → {remote_score:.0f}分")
        
        return score, "\n".join(details)
    
    def evaluate_precision(self, criteria: EvaluationCriteria) -> Tuple[float, str]:
        """评估控制精度 (0-100分)"""
        score = 0
        details = []
        
        # 稳态误差 (0-50分)
        if criteria.precision_steady_error <= criteria.precision_target:
            steady_score = 50
        else:
            steady_score = max(0, 50 - (criteria.precision_steady_error - criteria.precision_target) * 2)
        score += steady_score
        details.append(f"稳态误差: {criteria.precision_steady_error:.1f}cm (目标{criteria.precision_target:.1f}cm) → {steady_score:.0f}分")
        
        # 最大误差 (0-30分)
        max_allowed = criteria.precision_target * 3
        if criteria.precision_max_error <= max_allowed:
            max_score = 30
        else:
            max_score = max(0, 30 - (criteria.precision_max_error - max_allowed) * 1)
        score += max_score
        details.append(f"最大误差: {criteria.precision_max_error:.1f}cm (允许{max_allowed:.1f}cm) → {max_score:.0f}分")
        
        # 精度稳定性 (0-20分)
        if criteria.precision_max_error <= criteria.precision_steady_error * 2:
            stability_score = 20
        elif criteria.precision_max_error <= criteria.precision_steady_error * 3:
            stability_score = 10
        else:
            stability_score = 0
        score += stability_score
        details.append(f"精度稳定性: 最大/稳态={criteria.precision_max_error/criteria.precision_steady_error:.1f} → {stability_score:.0f}分")
        
        return score, "\n".join(details)
    
    def evaluate_speed(self, criteria: EvaluationCriteria) -> Tuple[float, str]:
        """评估响应速度 (0-100分)"""
        score = 0
        details = []
        
        # 响应时间 (0-40分)
        if criteria.speed_response_time <= 5:
            response_score = 40
        elif criteria.speed_response_time <= 15:
            response_score = 30
        elif criteria.speed_response_time <= 30:
            response_score = 20
        else:
            response_score = max(0, 40 - criteria.speed_response_time)
        score += response_score
        details.append(f"响应时间: {criteria.speed_response_time:.1f}分钟 → {response_score:.0f}分")
        
        # 调节时间 (0-30分)
        if criteria.speed_settling_time <= 5:
            settling_score = 30
        elif criteria.speed_settling_time <= 15:
            settling_score = 20
        else:
            settling_score = max(0, 30 - criteria.speed_settling_time * 0.5)
        score += settling_score
        details.append(f"调节时间: {criteria.speed_settling_time:.1f}分钟 → {settling_score:.0f}分")
        
        # 控制周期 (0-30分)
        if criteria.speed_control_cycle <= 30:
            cycle_score = 30
        elif criteria.speed_control_cycle <= 60:
            cycle_score = 25
        elif criteria.speed_control_cycle <= 300:
            cycle_score = 20
        else:
            cycle_score = max(0, 30 - criteria.speed_control_cycle / 60)
        score += cycle_score
        details.append(f"控制周期: {criteria.speed_control_cycle:.0f}秒 → {cycle_score:.0f}分")
        
        return score, "\n".join(details)
    
    def evaluate_robustness(self, criteria: EvaluationCriteria) -> Tuple[float, str]:
        """评估鲁棒性 (0-100分)"""
        score = 0
        details = []
        
        # 测试场景数 (0-30分)
        scenario_score = min(criteria.robust_test_scenarios * 3, 30)
        score += scenario_score
        details.append(f"测试场景: {criteria.robust_test_scenarios}个 → {scenario_score:.0f}分")
        
        # 容错能力 (0-25分)
        fault_score = 25 if criteria.robust_fault_tolerance else 0
        score += fault_score
        details.append(f"容错能力: {'是' if criteria.robust_fault_tolerance else '否'} → {fault_score:.0f}分")
        
        # 传感器冗余 (0-20分)
        redundancy_score = 20 if criteria.robust_sensor_redundancy else 0
        score += redundancy_score
        details.append(f"传感器冗余: {'是' if criteria.robust_sensor_redundancy else '否'} → {redundancy_score:.0f}分")
        
        # 扰动抑制 (0-25分)
        disturbance_score = criteria.robust_disturbance_rejection * 25
        score += disturbance_score
        details.append(f"扰动抑制: {criteria.robust_disturbance_rejection*100:.0f}% → {disturbance_score:.0f}分")
        
        return score, "\n".join(details)
    
    def evaluate_maintainability(self, criteria: EvaluationCriteria) -> Tuple[float, str]:
        """评估可维护性 (0-100分)"""
        score = 0
        details = []
        
        # 模块化设计 (0-30分)
        modular_score = 30 if criteria.maintain_modular else 0
        score += modular_score
        details.append(f"模块化设计: {'是' if criteria.maintain_modular else '否'} → {modular_score:.0f}分")
        
        # 文档完整性 (0-25分)
        doc_score = 25 if criteria.maintain_documentation else 0
        score += doc_score
        details.append(f"文档完整: {'是' if criteria.maintain_documentation else '否'} → {doc_score:.0f}分")
        
        # 故障诊断 (0-25分)
        diag_score = 25 if criteria.maintain_diagnosis else 0
        score += diag_score
        details.append(f"故障诊断: {'是' if criteria.maintain_diagnosis else '否'} → {diag_score:.0f}分")
        
        # 代码质量 (0-20分)
        code_score = criteria.maintain_code_quality * 20
        score += code_score
        details.append(f"代码质量: {criteria.maintain_code_quality*100:.0f}% → {code_score:.0f}分")
        
        return score, "\n".join(details)
    
    def get_level(self, score: float) -> str:
        """根据得分确定等级"""
        for level, (low, high) in self.level_thresholds.items():
            if low <= score <= high:
                return level
        return 'L0'
    
    def evaluate(self, criteria: EvaluationCriteria) -> Dict:
        """完整评估"""
        # 评估各维度
        auto_score, auto_details = self.evaluate_automation(criteria)
        prec_score, prec_details = self.evaluate_precision(criteria)
        speed_score, speed_details = self.evaluate_speed(criteria)
        robust_score, robust_details = self.evaluate_robustness(criteria)
        maintain_score, maintain_details = self.evaluate_maintainability(criteria)
        
        # 计算综合得分
        total_score = (auto_score + prec_score + speed_score + robust_score + maintain_score) / 5
        
        # 确定等级
        level = self.get_level(total_score)
        
        # 生成改进建议
        suggestions = self.generate_suggestions(
            auto_score, prec_score, speed_score, robust_score, maintain_score, level
        )
        
        return {
            '综合得分': total_score,
            '智能化等级': level,
            '维度得分': {
                '自动化程度': auto_score,
                '控制精度': prec_score,
                '响应速度': speed_score,
                '鲁棒性': robust_score,
                '可维护性': maintain_score
            },
            '详细评分': {
                '自动化程度': auto_details,
                '控制精度': prec_details,
                '响应速度': speed_details,
                '鲁棒性': robust_details,
                '可维护性': maintain_details
            },
            '改进建议': suggestions
        }
    
    def generate_suggestions(self, auto, prec, speed, robust, maintain, level) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 按得分从低到高排序
        scores = [
            (auto, '自动化程度'),
            (prec, '控制精度'),
            (speed, '响应速度'),
            (robust, '鲁棒性'),
            (maintain, '可维护性')
        ]
        scores.sort()
        
        # 针对最薄弱的维度提供建议
        if scores[0][0] < 60:
            dim = scores[0][1]
            if dim == '自动化程度':
                suggestions.append("增加传感器和控制器数量")
                suggestions.append("实现24小时自动运行")
                suggestions.append("减少人工干预频率")
            elif dim == '控制精度':
                suggestions.append("优化PID控制器参数")
                suggestions.append("使用更高精度传感器")
                suggestions.append("改进控制算法")
            elif dim == '响应速度':
                suggestions.append("缩短控制周期")
                suggestions.append("增加前馈控制")
                suggestions.append("优化执行机构")
            elif dim == '鲁棒性':
                suggestions.append("增加测试场景数量")
                suggestions.append("增加传感器冗余")
                suggestions.append("设计容错机制")
            elif dim == '可维护性':
                suggestions.append("采用模块化设计")
                suggestions.append("完善技术文档")
                suggestions.append("增加故障诊断功能")
        
        # 根据当前等级提供升级建议
        if level == 'L0':
            suggestions.append("建议: 先实现L1级(辅助监测),增加基础传感器")
        elif level == 'L1':
            suggestions.append("建议: 升级到L2级(局部控制),增加PID控制器")
        elif level == 'L2':
            suggestions.append("建议: 升级到L3级(协调控制),实现多点协调")
        elif level == 'L3':
            suggestions.append("建议: 升级到L4级(优化调度),增加全局优化")
        elif level == 'L4':
            suggestions.append("建议: 升级到L5级(自主管理),实现数字孪生")
        
        return suggestions
    
    def generate_report(self, result: Dict, output_file: str = 'intelligence_evaluation_report.txt'):
        """生成评估报告"""
        lines = []
        lines.append("="*80)
        lines.append("  智能化等级评估报告")
        lines.append("="*80)
        lines.append("")
        
        lines.append(f"综合得分: {result['综合得分']:.1f}/100")
        lines.append(f"智能化等级: {result['智能化等级']}")
        lines.append("")
        
        lines.append("="*80)
        lines.append("  维度得分详情")
        lines.append("="*80)
        lines.append("")
        
        for dim, score in result['维度得分'].items():
            lines.append(f"【{dim}】: {score:.1f}/100")
            lines.append(result['详细评分'][dim])
            lines.append("")
        
        lines.append("="*80)
        lines.append("  改进建议")
        lines.append("="*80)
        lines.append("")
        
        for i, suggestion in enumerate(result['改进建议'], 1):
            lines.append(f"{i}. {suggestion}")
        
        lines.append("")
        lines.append("="*80)
        lines.append("  等级说明")
        lines.append("="*80)
        lines.append("")
        lines.append("L0 (0-39分):   无智能化,纯人工操作")
        lines.append("L1 (40-59分):  辅助监测,基础传感器+数据采集")
        lines.append("L2 (60-79分):  局部控制,单点PID控制")
        lines.append("L3 (80-89分):  协调控制,多点协调+解耦控制")
        lines.append("L4 (90-95分):  优化调度,全局优化+自适应")
        lines.append("L5 (96-100分): 自主管理,数字孪生+预测性维护")
        lines.append("")
        lines.append("="*80)
        
        report_text = '\n'.join(lines)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return report_text
    
    def plot_radar(self, result: Dict, output_file: str = 'intelligence_radar.png'):
        """绘制雷达图"""
        categories = list(result['维度得分'].keys())
        values = list(result['维度得分'].values())
        
        # 简化标签
        short_labels = ['Automation', 'Precision', 'Speed', 'Robustness', 'Maintain']
        
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#4472C4', label=f"Score: {result['综合得分']:.1f}")
        ax.fill(angles, values, alpha=0.25, color='#4472C4')
        
        # 添加等级阈值圆圈
        thresholds = [40, 60, 80, 90, 96]
        colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
        labels = ['L1', 'L2', 'L3', 'L4', 'L5']
        
        for thresh, color, label in zip(thresholds, colors, labels):
            ax.plot(angles, [thresh]*len(angles), '--', linewidth=1, color=color, alpha=0.3)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(short_labels, fontsize=12, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.title(f'Intelligence Level Assessment\nLevel: {result["智能化等级"]} (Score: {result["综合得分"]:.1f})',
                 fontsize=16, fontweight='bold', pad=20)
        
        # 添加等级说明
        legend_text = 'L1:40-59  L2:60-79  L3:80-89  L4:90-95  L5:96-100'
        ax.text(0.5, -0.15, legend_text, transform=ax.transAxes,
               ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')


# ============================================================================
# 示例用法
# ============================================================================

if __name__ == '__main__':
    print("【示例1】评估L2级系统")
    print("-" * 80)
    
    # 创建评估器
    evaluator = IntelligenceEvaluator()
    
    # L2级系统参数
    l2_criteria = EvaluationCriteria(
        # 自动化
        automation_sensors=3,
        automation_controllers=1,
        automation_manual_freq=0,
        automation_24h=True,
        automation_remote=True,
        # 精度
        precision_steady_error=11.62,
        precision_max_error=56.18,
        precision_target=5.0,
        # 速度
        speed_response_time=4.0,
        speed_settling_time=5.0,
        speed_control_cycle=10,
        # 鲁棒性
        robust_test_scenarios=4,
        robust_fault_tolerance=False,
        robust_sensor_redundancy=True,
        robust_disturbance_rejection=0.7,
        # 可维护性
        maintain_modular=True,
        maintain_documentation=True,
        maintain_diagnosis=False,
        maintain_code_quality=0.85
    )
    
    result_l2 = evaluator.evaluate(l2_criteria)
    
    print(f"\n综合得分: {result_l2['综合得分']:.1f}/100")
    print(f"智能化等级: {result_l2['智能化等级']}")
    print(f"\n维度得分:")
    for dim, score in result_l2['维度得分'].items():
        print(f"  {dim}: {score:.1f}")
    
    # 生成报告
    report = evaluator.generate_report(result_l2, 'intelligence_evaluation_L2.txt')
    print("\n✓ 评估报告已保存: intelligence_evaluation_L2.txt")
    
    # 绘制雷达图
    evaluator.plot_radar(result_l2, 'intelligence_radar_L2.png')
    print("✓ 雷达图已保存: intelligence_radar_L2.png")
    
    print("\n" + "="*80)
    print("【示例2】评估L3级系统")
    print("-" * 80)
    
    # L3级系统参数
    l3_criteria = EvaluationCriteria(
        # 自动化
        automation_sensors=12,
        automation_controllers=4,
        automation_manual_freq=0.2,
        automation_24h=True,
        automation_remote=True,
        # 精度
        precision_steady_error=12.98,
        precision_max_error=33.62,
        precision_target=5.0,
        # 速度
        speed_response_time=3.5,
        speed_settling_time=4.0,
        speed_control_cycle=10,
        # 鲁棒性
        robust_test_scenarios=4,
        robust_fault_tolerance=True,
        robust_sensor_redundancy=True,
        robust_disturbance_rejection=0.8,
        # 可维护性
        maintain_modular=True,
        maintain_documentation=True,
        maintain_diagnosis=True,
        maintain_code_quality=0.9
    )
    
    result_l3 = evaluator.evaluate(l3_criteria)
    
    print(f"\n综合得分: {result_l3['综合得分']:.1f}/100")
    print(f"智能化等级: {result_l3['智能化等级']}")
    print(f"\n维度得分:")
    for dim, score in result_l3['维度得分'].items():
        print(f"  {dim}: {score:.1f}")
    
    # 生成报告
    report = evaluator.generate_report(result_l3, 'intelligence_evaluation_L3.txt')
    print("\n✓ 评估报告已保存: intelligence_evaluation_L3.txt")
    
    # 绘制雷达图
    evaluator.plot_radar(result_l3, 'intelligence_radar_L3.png')
    print("✓ 雷达图已保存: intelligence_radar_L3.png")
    
    print("\n" + "="*80)
    print("  评估完成!")
    print("="*80)
    print()
    print("生成的文件:")
    print("  1. intelligence_evaluation_L2.txt - L2级评估报告")
    print("  2. intelligence_radar_L2.png - L2级雷达图")
    print("  3. intelligence_evaluation_L3.txt - L3级评估报告")
    print("  4. intelligence_radar_L3.png - L3级雷达图")
    print()
    print("使用说明:")
    print("  1. 作为独立工具使用: python3 intelligence_evaluator.py")
    print("  2. 作为模块导入: from intelligence_evaluator import IntelligenceEvaluator")
    print("  3. 自定义评估参数: 修改EvaluationCriteria")
    print()
    print("="*80)
