#!/usr/bin/env python3
"""
智能化等级评估工具 (Intelligence Level Grader)

功能：
1. 评估水网系统的智能化等级（L1-L5）
2. 提供详细的评分报告
3. 给出改进建议

评估标准：
- L1（辅助监测）：基本的数据采集和报警
- L2（局部控制）：单点PID控制
- L3（协调控制）：多点协调、MPC
- L4（优化调度）：全局优化、自适应
- L5（自主管理）：数字孪生、预测性维护

作者：CHS-Books项目
日期：2025-10-31
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class IntelligenceLevel(Enum):
    """智能化等级枚举"""
    L1 = 1  # 辅助监测
    L2 = 2  # 局部控制  
    L3 = 3  # 协调控制
    L4 = 4  # 优化调度
    L5 = 5  # 自主管理


@dataclass
class EvaluationScore:
    """评估分数数据类"""
    level: IntelligenceLevel
    overall_score: float  # 总分（0-100）
    dimension_scores: Dict[str, float]  # 各维度得分
    passed: bool  # 是否达标
    recommendations: List[str]  # 改进建议


class IntelligenceGrader:
    """
    智能化等级评估器
    
    评估维度：
    1. 自动化程度（Automation）
    2. 控制精度（Accuracy）
    3. 响应速度（Response）
    4. 鲁棒性（Robustness）
    5. 可维护性（Maintainability）
    """
    
    def __init__(self):
        """初始化评估标准"""
        # 各等级的评分阈值
        self.criteria = {
            IntelligenceLevel.L1: {
                '自动化程度': 40,
                '控制精度': 50,
                '响应速度': 40,
                '鲁棒性': 50,
                '可维护性': 60
            },
            IntelligenceLevel.L2: {
                '自动化程度': 70,
                '控制精度': 75,
                '响应速度': 70,
                '鲁棒性': 70,
                '可维护性': 75
            },
            IntelligenceLevel.L3: {
                '自动化程度': 85,
                '控制精度': 85,
                '响应速度': 80,
                '鲁棒性': 80,
                '可维护性': 85
            },
            IntelligenceLevel.L4: {
                '自动化程度': 92,
                '控制精度': 90,
                '响应速度': 85,
                '鲁棒性': 88,
                '可维护性': 90
            },
            IntelligenceLevel.L5: {
                '自动化程度': 95,
                '控制精度': 95,
                '响应速度': 92,
                '鲁棒性': 93,
                '可维护性': 95
            }
        }
    
    def evaluate_automation(self, 
                           n_sensors: int,
                           n_controllers: int,
                           n_manual_operations: int,
                           has_remote_control: bool = True,
                           has_decision_support: bool = False) -> float:
        """
        评估自动化程度
        
        Parameters:
        -----------
        n_sensors : int
            传感器数量
        n_controllers : int
            控制器数量
        n_manual_operations : int
            需要人工干预的操作数量
        has_remote_control : bool
            是否有远程控制
        has_decision_support : bool
            是否有决策支持系统
            
        Returns:
        --------
        score : float
            自动化程度得分（0-100）
        """
        # 基础分：传感器和控制器覆盖率
        total_devices = n_sensors + n_controllers
        if total_devices == 0:
            base_score = 0
        else:
            automation_rate = 1 - min(n_manual_operations / total_devices, 1.0)
            base_score = automation_rate * 70  # 最高70分
        
        # 加分项
        bonus = 0
        if has_remote_control:
            bonus += 15
        if has_decision_support:
            bonus += 15
        
        score = min(base_score + bonus, 100)
        return score
    
    def evaluate_accuracy(self,
                         steady_state_errors: List[float],
                         setpoints: List[float]) -> float:
        """
        评估控制精度
        
        Parameters:
        -----------
        steady_state_errors : List[float]
            各控制点的稳态误差
        setpoints : List[float]
            各控制点的设定值
            
        Returns:
        --------
        score : float
            控制精度得分（0-100）
        """
        if len(steady_state_errors) == 0 or len(setpoints) == 0:
            return 0
        
        # 计算相对误差
        relative_errors = []
        for error, sp in zip(steady_state_errors, setpoints):
            if sp != 0:
                rel_err = abs(error / sp)
                relative_errors.append(rel_err)
        
        if len(relative_errors) == 0:
            return 0
        
        # 平均相对误差
        mean_rel_error = np.mean(relative_errors)
        
        # 评分：误差越小，分数越高
        # 0% 误差 → 100分
        # 5% 误差 → 75分
        # 10% 误差 → 50分
        # >20% 误差 → 0分
        if mean_rel_error <= 0.01:  # ≤1%
            score = 100
        elif mean_rel_error <= 0.05:  # 1-5%
            score = 100 - (mean_rel_error - 0.01) * 625  # 线性递减
        elif mean_rel_error <= 0.10:  # 5-10%
            score = 75 - (mean_rel_error - 0.05) * 500
        elif mean_rel_error <= 0.20:  # 10-20%
            score = 50 - (mean_rel_error - 0.10) * 500
        else:
            score = 0
        
        return max(score, 0)
    
    def evaluate_response(self,
                         rise_times: List[float],
                         target_rise_time: float = 5.0) -> float:
        """
        评估响应速度
        
        Parameters:
        -----------
        rise_times : List[float]
            各控制回路的上升时间（分钟）
        target_rise_time : float
            目标上升时间（分钟）
            
        Returns:
        --------
        score : float
            响应速度得分（0-100）
        """
        if len(rise_times) == 0:
            return 0
        
        mean_rise_time = np.mean(rise_times)
        
        # 评分：响应越快，分数越高
        # ≤目标时间 → 100分
        # 2倍目标时间 → 50分
        # ≥4倍目标时间 → 0分
        if mean_rise_time <= target_rise_time:
            score = 100
        elif mean_rise_time <= 2 * target_rise_time:
            score = 100 - (mean_rise_time - target_rise_time) * 50 / target_rise_time
        elif mean_rise_time <= 4 * target_rise_time:
            score = 50 - (mean_rise_time - 2*target_rise_time) * 25 / target_rise_time
        else:
            score = 0
        
        return max(score, 0)
    
    def evaluate_robustness(self,
                           disturbance_rejection_ratios: List[float],
                           fault_recovery_success_rate: float = 1.0) -> float:
        """
        评估鲁棒性
        
        Parameters:
        -----------
        disturbance_rejection_ratios : List[float]
            扰动抑制比（0-1，越大越好）
        fault_recovery_success_rate : float
            故障恢复成功率（0-1）
            
        Returns:
        --------
        score : float
            鲁棒性得分（0-100）
        """
        if len(disturbance_rejection_ratios) == 0:
            return 0
        
        # 扰动抑制能力（60%权重）
        mean_rejection = np.mean(disturbance_rejection_ratios)
        disturbance_score = mean_rejection * 60
        
        # 故障恢复能力（40%权重）
        recovery_score = fault_recovery_success_rate * 40
        
        score = disturbance_score + recovery_score
        return score
    
    def evaluate_maintainability(self,
                                code_modularity: float = 0.8,
                                documentation_completeness: float = 0.9,
                                diagnostic_capability: float = 0.7) -> float:
        """
        评估可维护性
        
        Parameters:
        -----------
        code_modularity : float
            代码模块化程度（0-1）
        documentation_completeness : float
            文档完整性（0-1）
        diagnostic_capability : float
            故障诊断能力（0-1）
            
        Returns:
        --------
        score : float
            可维护性得分（0-100）
        """
        # 加权平均
        weights = [0.3, 0.4, 0.3]  # 代码、文档、诊断
        factors = [code_modularity, documentation_completeness, diagnostic_capability]
        
        score = sum(w * f for w, f in zip(weights, factors)) * 100
        return score
    
    def determine_level(self, dimension_scores: Dict[str, float]) -> IntelligenceLevel:
        """
        根据各维度得分确定智能化等级
        
        Parameters:
        -----------
        dimension_scores : Dict[str, float]
            各维度得分
            
        Returns:
        --------
        level : IntelligenceLevel
            智能化等级
        """
        # 从高到低检查各等级
        for level in [IntelligenceLevel.L5, IntelligenceLevel.L4, 
                     IntelligenceLevel.L3, IntelligenceLevel.L2, 
                     IntelligenceLevel.L1]:
            criteria = self.criteria[level]
            
            # 检查是否所有维度都达标
            all_passed = all(
                dimension_scores.get(dim, 0) >= threshold
                for dim, threshold in criteria.items()
            )
            
            if all_passed:
                return level
        
        # 如果都不达标，返回L1
        return IntelligenceLevel.L1
    
    def generate_recommendations(self,
                                dimension_scores: Dict[str, float],
                                target_level: IntelligenceLevel) -> List[str]:
        """
        生成改进建议
        
        Parameters:
        -----------
        dimension_scores : Dict[str, float]
            当前各维度得分
        target_level : IntelligenceLevel
            目标等级
            
        Returns:
        --------
        recommendations : List[str]
            改进建议列表
        """
        recommendations = []
        target_criteria = self.criteria[target_level]
        
        for dimension, threshold in target_criteria.items():
            current_score = dimension_scores.get(dimension, 0)
            gap = threshold - current_score
            
            if gap > 0:
                if dimension == '自动化程度':
                    recommendations.append(
                        f"提升{dimension}：当前{current_score:.1f}分，需达到{threshold}分。"
                        f"建议增加传感器和控制器数量，减少人工干预。"
                    )
                elif dimension == '控制精度':
                    recommendations.append(
                        f"提升{dimension}：当前{current_score:.1f}分，需达到{threshold}分。"
                        f"建议优化控制器参数，或升级到更先进的控制算法（如MPC）。"
                    )
                elif dimension == '响应速度':
                    recommendations.append(
                        f"提升{dimension}：当前{current_score:.1f}分，需达到{threshold}分。"
                        f"建议缩短数据采集周期，优化控制器计算效率。"
                    )
                elif dimension == '鲁棒性':
                    recommendations.append(
                        f"提升{dimension}：当前{current_score:.1f}分，需达到{threshold}分。"
                        f"建议加强扰动补偿设计，增加冗余备份。"
                    )
                elif dimension == '可维护性':
                    recommendations.append(
                        f"提升{dimension}：当前{current_score:.1f}分，需达到{threshold}分。"
                        f"建议完善系统文档，增强故障诊断功能。"
                    )
        
        if len(recommendations) == 0:
            recommendations.append(f"✓ 当前系统已达到{target_level.name}等级标准！")
        
        return recommendations
    
    def evaluate(self,
                # 自动化参数
                n_sensors: int,
                n_controllers: int,
                n_manual_operations: int = 0,
                has_remote_control: bool = True,
                has_decision_support: bool = False,
                # 精度参数
                steady_state_errors: List[float] = None,
                setpoints: List[float] = None,
                # 响应参数
                rise_times: List[float] = None,
                target_rise_time: float = 5.0,
                # 鲁棒性参数
                disturbance_rejection_ratios: List[float] = None,
                fault_recovery_success_rate: float = 0.95,
                # 可维护性参数
                code_modularity: float = 0.8,
                documentation_completeness: float = 0.9,
                diagnostic_capability: float = 0.7,
                # 目标等级
                target_level: IntelligenceLevel = IntelligenceLevel.L2
                ) -> EvaluationScore:
        """
        综合评估系统智能化等级
        
        Returns:
        --------
        result : EvaluationScore
            评估结果
        """
        # 计算各维度得分
        dimension_scores = {}
        
        # 1. 自动化程度
        dimension_scores['自动化程度'] = self.evaluate_automation(
            n_sensors, n_controllers, n_manual_operations,
            has_remote_control, has_decision_support
        )
        
        # 2. 控制精度
        if steady_state_errors and setpoints:
            dimension_scores['控制精度'] = self.evaluate_accuracy(
                steady_state_errors, setpoints
            )
        else:
            dimension_scores['控制精度'] = 70  # 默认值
        
        # 3. 响应速度
        if rise_times:
            dimension_scores['响应速度'] = self.evaluate_response(
                rise_times, target_rise_time
            )
        else:
            dimension_scores['响应速度'] = 75  # 默认值
        
        # 4. 鲁棒性
        if disturbance_rejection_ratios:
            dimension_scores['鲁棒性'] = self.evaluate_robustness(
                disturbance_rejection_ratios, fault_recovery_success_rate
            )
        else:
            dimension_scores['鲁棒性'] = 70  # 默认值
        
        # 5. 可维护性
        dimension_scores['可维护性'] = self.evaluate_maintainability(
            code_modularity, documentation_completeness, diagnostic_capability
        )
        
        # 计算总分
        overall_score = np.mean(list(dimension_scores.values()))
        
        # 确定等级
        achieved_level = self.determine_level(dimension_scores)
        
        # 检查是否达到目标等级
        passed = achieved_level.value >= target_level.value
        
        # 生成改进建议
        recommendations = self.generate_recommendations(dimension_scores, target_level)
        
        return EvaluationScore(
            level=achieved_level,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            passed=passed,
            recommendations=recommendations
        )
    
    def print_report(self, result: EvaluationScore):
        """打印评估报告"""
        print("="*70)
        print("  智能化等级评估报告")
        print("="*70)
        
        print(f"\n评估结果：")
        print(f"  智能化等级：{result.level.name} ({result.level.value}级)")
        print(f"  综合得分：{result.overall_score:.1f}/100")
        print(f"  是否达标：{'✓ 通过' if result.passed else '✗ 未通过'}")
        
        print(f"\n各维度得分：")
        for dimension, score in result.dimension_scores.items():
            bar = '█' * int(score/5) + '░' * (20 - int(score/5))
            print(f"  {dimension:.<20} {score:>5.1f}/100  [{bar}]")
        
        print(f"\n改进建议：")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*70)


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='智能化等级评估工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 基本评估
  python intelligence_grader.py --sensors 30 --controllers 10
  
  # 指定目标等级
  python intelligence_grader.py --sensors 50 --controllers 20 --target L3
  
  # 详细评估
  python intelligence_grader.py --sensors 30 --controllers 10 \\
      --errors 0.05 0.06 0.04 --setpoints 1.8 2.0 1.5 \\
      --rise-times 4 5 6 --target L2
        """
    )
    
    # 基本参数
    parser.add_argument('--sensors', type=int, required=True,
                       help='传感器数量')
    parser.add_argument('--controllers', type=int, required=True,
                       help='控制器数量')
    parser.add_argument('--manual-ops', type=int, default=0,
                       help='人工操作数量')
    parser.add_argument('--target', choices=['L1', 'L2', 'L3', 'L4', 'L5'],
                       default='L2', help='目标智能化等级')
    
    # 精度参数（可选）
    parser.add_argument('--errors', nargs='+', type=float,
                       help='稳态误差列表')
    parser.add_argument('--setpoints', nargs='+', type=float,
                       help='设定值列表')
    
    # 响应参数（可选）
    parser.add_argument('--rise-times', nargs='+', type=float,
                       help='上升时间列表（分钟）')
    
    args = parser.parse_args()
    
    # 创建评估器
    grader = IntelligenceGrader()
    
    # 目标等级
    target_level = IntelligenceLevel[args.target]
    
    # 执行评估
    result = grader.evaluate(
        n_sensors=args.sensors,
        n_controllers=args.controllers,
        n_manual_operations=args.manual_ops,
        steady_state_errors=args.errors,
        setpoints=args.setpoints,
        rise_times=args.rise_times,
        target_level=target_level
    )
    
    # 打印报告
    grader.print_report(result)


if __name__ == '__main__':
    main()
