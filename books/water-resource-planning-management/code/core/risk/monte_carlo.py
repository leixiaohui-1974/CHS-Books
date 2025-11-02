"""
蒙特卡洛模拟

用于不确定性分析和风险评估
"""

import numpy as np
from typing import Callable, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class SimulationResult:
    """模拟结果"""
    samples: np.ndarray
    mean: float
    std: float
    percentiles: Dict[float, float]
    
    def summary(self) -> str:
        """生成摘要"""
        lines = [
            f"样本数: {len(self.samples)}",
            f"均值: {self.mean:.4f}",
            f"标准差: {self.std:.4f}",
            "分位数:"
        ]
        for p, val in sorted(self.percentiles.items()):
            lines.append(f"  {p*100:.0f}%: {val:.4f}")
        
        return "\n".join(lines)


class MonteCarloSimulator:
    """
    蒙特卡洛模拟器
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        初始化模拟器
        
        Parameters
        ----------
        seed : int, optional
            随机种子
        """
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
        
        self.results = {}
    
    def simulate(
        self,
        model: Callable,
        parameters: Dict[str, Dict],
        n_simulations: int = 10000,
        percentiles: List[float] = [0.05, 0.25, 0.5, 0.75, 0.95]
    ) -> SimulationResult:
        """
        运行蒙特卡洛模拟
        
        Parameters
        ----------
        model : Callable
            模型函数，接受参数字典，返回结果
        parameters : Dict[str, Dict]
            参数分布字典，格式:
            {
                'param1': {'dist': 'normal', 'mean': 0, 'std': 1},
                'param2': {'dist': 'uniform', 'low': 0, 'high': 1}
            }
        n_simulations : int
            模拟次数
        percentiles : List[float]
            要计算的分位数
        
        Returns
        -------
        SimulationResult
            模拟结果
        """
        samples = np.zeros(n_simulations)
        
        for i in range(n_simulations):
            # 生成随机参数
            params = self._generate_parameters(parameters)
            
            # 运行模型
            result = model(**params)
            samples[i] = result
        
        # 计算统计量
        mean = np.mean(samples)
        std = np.std(samples)
        
        percentile_values = {}
        for p in percentiles:
            percentile_values[p] = np.percentile(samples, p * 100)
        
        return SimulationResult(
            samples=samples,
            mean=mean,
            std=std,
            percentiles=percentile_values
        )
    
    def _generate_parameters(self, parameters: Dict[str, Dict]) -> Dict:
        """生成随机参数"""
        params = {}
        
        for name, config in parameters.items():
            dist = config['dist']
            
            if dist == 'normal':
                value = np.random.normal(config['mean'], config['std'])
            
            elif dist == 'uniform':
                value = np.random.uniform(config['low'], config['high'])
            
            elif dist == 'lognormal':
                value = np.random.lognormal(config['mean'], config['std'])
            
            elif dist == 'exponential':
                value = np.random.exponential(config['scale'])
            
            elif dist == 'triangular':
                value = np.random.triangular(
                    config['left'],
                    config['mode'],
                    config['right']
                )
            
            elif dist == 'beta':
                value = np.random.beta(config['a'], config['b'])
                if 'scale' in config:
                    value *= config['scale']
            
            else:
                raise ValueError(f"Unknown distribution: {dist}")
            
            params[name] = value
        
        return params
    
    def simulate_scenarios(
        self,
        model: Callable,
        scenarios: List[Dict],
        n_simulations_per_scenario: int = 1000
    ) -> Dict[str, SimulationResult]:
        """
        模拟多个情景
        
        Parameters
        ----------
        model : Callable
            模型函数
        scenarios : List[Dict]
            情景列表
        n_simulations_per_scenario : int
            每个情景的模拟次数
        
        Returns
        -------
        Dict[str, SimulationResult]
            情景模拟结果
        """
        results = {}
        
        for i, scenario in enumerate(scenarios):
            name = scenario.get('name', f'Scenario_{i+1}')
            parameters = scenario['parameters']
            
            result = self.simulate(model, parameters, n_simulations_per_scenario)
            results[name] = result
        
        return results
    
    def latin_hypercube_sampling(
        self,
        parameters: Dict[str, Dict],
        n_samples: int
    ) -> np.ndarray:
        """
        拉丁超立方抽样（LHS）
        
        更均匀地覆盖参数空间
        
        Parameters
        ----------
        parameters : Dict[str, Dict]
            参数分布
        n_samples : int
            样本数
        
        Returns
        -------
        np.ndarray
            样本矩阵 (n_samples, n_parameters)
        """
        n_params = len(parameters)
        
        # 生成LHS样本（[0, 1]均匀分布）
        lhs_samples = np.zeros((n_samples, n_params))
        
        for i in range(n_params):
            # 分层抽样
            intervals = np.arange(n_samples) / n_samples
            lhs_samples[:, i] = intervals + np.random.uniform(0, 1/n_samples, n_samples)
            
            # 随机打乱
            np.random.shuffle(lhs_samples[:, i])
        
        # 转换到目标分布
        samples = np.zeros_like(lhs_samples)
        
        for i, (name, config) in enumerate(parameters.items()):
            uniform_samples = lhs_samples[:, i]
            
            dist = config['dist']
            
            if dist == 'normal':
                from scipy.stats import norm
                samples[:, i] = norm.ppf(uniform_samples, config['mean'], config['std'])
            
            elif dist == 'uniform':
                samples[:, i] = config['low'] + uniform_samples * (config['high'] - config['low'])
            
            elif dist == 'lognormal':
                from scipy.stats import lognorm
                samples[:, i] = lognorm.ppf(uniform_samples, config['std'], scale=np.exp(config['mean']))
            
            else:
                # 默认使用逆变换
                samples[:, i] = uniform_samples
        
        return samples
