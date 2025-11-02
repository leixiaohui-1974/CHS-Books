"""
情景分析

生成和分析不同情景
"""

import numpy as np
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass


@dataclass
class Scenario:
    """情景定义"""
    name: str
    probability: float
    parameters: Dict[str, float]
    description: str = ""
    
    def __repr__(self):
        return f"Scenario('{self.name}', p={self.probability:.2f})"


class ScenarioGenerator:
    """
    情景生成器
    """
    
    def __init__(self):
        self.scenarios = []
    
    def generate_quantile_scenarios(
        self,
        parameter_name: str,
        base_value: float,
        std: float,
        quantiles: List[float] = [0.1, 0.5, 0.9]
    ) -> List[Scenario]:
        """
        生成分位数情景
        
        Parameters
        ----------
        parameter_name : str
            参数名称
        base_value : float
            基准值
        std : float
            标准差
        quantiles : List[float]
            分位数列表
        
        Returns
        -------
        List[Scenario]
            情景列表
        """
        from scipy.stats import norm
        
        scenarios = []
        
        labels = {
            0.1: '悲观',
            0.5: '基准',
            0.9: '乐观'
        }
        
        for q in quantiles:
            z = norm.ppf(q)
            value = base_value + z * std
            
            scenario = Scenario(
                name=labels.get(q, f'P{int(q*100)}'),
                probability=1.0 / len(quantiles),
                parameters={parameter_name: value},
                description=f"{parameter_name}={value:.2f}"
            )
            scenarios.append(scenario)
        
        self.scenarios = scenarios
        return scenarios
    
    def generate_combination_scenarios(
        self,
        parameters: Dict[str, Dict[str, float]],
        labels: Optional[List[str]] = None
    ) -> List[Scenario]:
        """
        生成组合情景
        
        Parameters
        ----------
        parameters : Dict[str, Dict[str, float]]
            参数组合，格式:
            {
                'scenario1': {'param1': value1, 'param2': value2},
                'scenario2': {...}
            }
        labels : List[str], optional
            情景标签
        
        Returns
        -------
        List[Scenario]
            情景列表
        """
        scenarios = []
        n_scenarios = len(parameters)
        
        for i, (name, params) in enumerate(parameters.items()):
            label = labels[i] if labels and i < len(labels) else name
            
            scenario = Scenario(
                name=label,
                probability=1.0 / n_scenarios,
                parameters=params
            )
            scenarios.append(scenario)
        
        self.scenarios = scenarios
        return scenarios
    
    def generate_tree_scenarios(
        self,
        branches: Dict[str, List[float]],
        probabilities: Optional[Dict[str, List[float]]] = None
    ) -> List[Scenario]:
        """
        生成树形情景
        
        Parameters
        ----------
        branches : Dict[str, List[float]]
            分支定义
        probabilities : Dict[str, List[float]], optional
            概率定义
        
        Returns
        -------
        List[Scenario]
            情景列表
        """
        # 递归生成所有组合
        param_names = list(branches.keys())
        param_values = list(branches.values())
        
        if probabilities is None:
            probabilities = {name: [1.0/len(vals)] * len(vals) 
                           for name, vals in branches.items()}
        
        scenarios = []
        
        def _generate_recursive(level, current_params, current_prob):
            if level == len(param_names):
                scenario = Scenario(
                    name=f"S{len(scenarios)+1}",
                    probability=current_prob,
                    parameters=current_params.copy()
                )
                scenarios.append(scenario)
                return
            
            param_name = param_names[level]
            for val, prob in zip(branches[param_name], probabilities[param_name]):
                current_params[param_name] = val
                _generate_recursive(level + 1, current_params, current_prob * prob)
        
        _generate_recursive(0, {}, 1.0)
        
        self.scenarios = scenarios
        return scenarios


class ScenarioAnalyzer:
    """
    情景分析器
    """
    
    def __init__(self, scenarios: List[Scenario]):
        """
        初始化分析器
        
        Parameters
        ----------
        scenarios : List[Scenario]
            情景列表
        """
        self.scenarios = scenarios
        self.results = {}
    
    def evaluate(
        self,
        model: Callable,
        objective: Optional[Callable] = None
    ) -> Dict:
        """
        评估所有情景
        
        Parameters
        ----------
        model : Callable
            模型函数
        objective : Callable, optional
            目标函数（从模型输出提取目标值）
        
        Returns
        -------
        Dict
            评估结果
        """
        results = {}
        
        for scenario in self.scenarios:
            # 运行模型
            output = model(**scenario.parameters)
            
            # 提取目标值
            if objective is not None:
                value = objective(output)
            else:
                value = output
            
            results[scenario.name] = {
                'probability': scenario.probability,
                'value': value,
                'parameters': scenario.parameters
            }
        
        self.results = results
        return results
    
    def calculate_expected_value(self) -> float:
        """计算期望值"""
        if not self.results:
            raise ValueError("No results to analyze. Run evaluate() first.")
        
        expected_value = sum(
            result['probability'] * result['value']
            for result in self.results.values()
        )
        
        return expected_value
    
    def calculate_variance(self) -> float:
        """计算方差"""
        expected_value = self.calculate_expected_value()
        
        variance = sum(
            result['probability'] * (result['value'] - expected_value) ** 2
            for result in self.results.values()
        )
        
        return variance
    
    def get_worst_case(self) -> Dict:
        """获取最坏情景"""
        worst = min(self.results.items(), key=lambda x: x[1]['value'])
        return {
            'scenario': worst[0],
            **worst[1]
        }
    
    def get_best_case(self) -> Dict:
        """获取最好情景"""
        best = max(self.results.items(), key=lambda x: x[1]['value'])
        return {
            'scenario': best[0],
            **best[1]
        }
    
    def summary(self) -> str:
        """生成摘要"""
        if not self.results:
            return "No results available."
        
        ev = self.calculate_expected_value()
        var = self.calculate_variance()
        worst = self.get_worst_case()
        best = self.get_best_case()
        
        lines = [
            "情景分析摘要",
            "=" * 50,
            f"情景数: {len(self.scenarios)}",
            f"期望值: {ev:.4f}",
            f"标准差: {np.sqrt(var):.4f}",
            f"最优情景: {best['scenario']} (值={best['value']:.4f})",
            f"最差情景: {worst['scenario']} (值={worst['value']:.4f})",
        ]
        
        return "\n".join(lines)
