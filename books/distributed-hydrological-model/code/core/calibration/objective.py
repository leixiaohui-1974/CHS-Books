"""
目标函数模块
===========

定义各种率定目标函数。

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Callable, List, Dict, Tuple


class ObjectiveFunction:
    """
    目标函数基类
    
    Parameters
    ----------
    observed : ndarray
        观测值
    metric : str or callable
        评价指标名称或函数
    maximize : bool
        是否最大化（True）或最小化（False）
    """
    
    def __init__(self, observed: np.ndarray, 
                 metric: str = 'nse',
                 maximize: bool = True):
        self.observed = observed
        self.metric_name = metric if isinstance(metric, str) else 'custom'
        self.maximize = maximize
        
        # 选择评价指标
        if isinstance(metric, str):
            self.metric_func = self._get_metric_function(metric)
        else:
            self.metric_func = metric
    
    def _get_metric_function(self, metric: str) -> Callable:
        """获取评价指标函数"""
        metrics = {
            'nse': self._nash_sutcliffe,
            'rmse': self._rmse,
            'mae': self._mae,
            'r2': self._r_squared,
            'pbias': self._pbias
        }
        
        if metric not in metrics:
            raise ValueError(f"未知指标: {metric}")
        
        return metrics[metric]
    
    def _nash_sutcliffe(self, simulated: np.ndarray) -> float:
        """Nash-Sutcliffe效率系数"""
        obs_mean = np.mean(self.observed)
        numerator = np.sum((self.observed - simulated) ** 2)
        denominator = np.sum((self.observed - obs_mean) ** 2)
        
        if denominator == 0:
            return 0.0
        
        nse = 1 - numerator / denominator
        return nse
    
    def _rmse(self, simulated: np.ndarray) -> float:
        """均方根误差"""
        return np.sqrt(np.mean((self.observed - simulated) ** 2))
    
    def _mae(self, simulated: np.ndarray) -> float:
        """平均绝对误差"""
        return np.mean(np.abs(self.observed - simulated))
    
    def _r_squared(self, simulated: np.ndarray) -> float:
        """决定系数"""
        obs_mean = np.mean(self.observed)
        sim_mean = np.mean(simulated)
        
        numerator = np.sum((self.observed - obs_mean) * (simulated - sim_mean))
        denominator = np.sqrt(
            np.sum((self.observed - obs_mean) ** 2) *
            np.sum((simulated - sim_mean) ** 2)
        )
        
        if denominator == 0:
            return 0.0
        
        r = numerator / denominator
        return r ** 2
    
    def _pbias(self, simulated: np.ndarray) -> float:
        """百分比偏差"""
        numerator = np.sum(self.observed - simulated)
        denominator = np.sum(self.observed)
        
        if denominator == 0:
            return 0.0
        
        return 100 * numerator / denominator
    
    def evaluate(self, simulated: np.ndarray) -> float:
        """
        评估模拟结果
        
        Parameters
        ----------
        simulated : ndarray
            模拟值
        
        Returns
        -------
        score : float
            目标函数值（根据maximize决定符号）
        """
        # 数据验证
        if len(simulated) != len(self.observed):
            raise ValueError("模拟值和观测值长度不一致")
        
        # 计算指标
        score = self.metric_func(simulated)
        
        # 根据优化方向调整符号
        if not self.maximize:
            score = -score
        
        return score


def nash_sutcliffe_objective(observed: np.ndarray) -> ObjectiveFunction:
    """创建Nash-Sutcliffe目标函数（最大化）"""
    return ObjectiveFunction(observed, metric='nse', maximize=True)


def rmse_objective(observed: np.ndarray) -> ObjectiveFunction:
    """创建RMSE目标函数（最小化）"""
    return ObjectiveFunction(observed, metric='rmse', maximize=False)


def multi_objective(observed: np.ndarray, 
                   weights: Dict[str, float]) -> Callable:
    """
    创建多目标函数
    
    Parameters
    ----------
    observed : ndarray
        观测值
    weights : dict
        各指标权重，如 {'nse': 0.6, 'rmse': 0.4}
    
    Returns
    -------
    objective_func : callable
        多目标函数
    """
    objectives = {}
    for metric, weight in weights.items():
        if metric == 'rmse':
            objectives[metric] = ObjectiveFunction(observed, metric, maximize=False)
        else:
            objectives[metric] = ObjectiveFunction(observed, metric, maximize=True)
    
    def evaluate(simulated: np.ndarray) -> float:
        """评估多目标"""
        total_score = 0.0
        total_weight = sum(weights.values())
        
        for metric, weight in weights.items():
            score = objectives[metric].evaluate(simulated)
            # 归一化权重
            total_score += score * (weight / total_weight)
        
        return total_score
    
    return evaluate


if __name__ == '__main__':
    # 简单测试
    print("目标函数模块测试")
    print("=" * 50)
    
    # 生成测试数据
    observed = np.array([10, 20, 30, 25, 15])
    simulated = np.array([12, 19, 28, 26, 14])
    
    # NSE
    obj_nse = nash_sutcliffe_objective(observed)
    nse_score = obj_nse.evaluate(simulated)
    print(f"NSE: {nse_score:.4f}")
    
    # RMSE
    obj_rmse = rmse_objective(observed)
    rmse_score = obj_rmse.evaluate(simulated)
    print(f"RMSE (负值): {rmse_score:.4f}")
    
    print("\n测试通过！")
