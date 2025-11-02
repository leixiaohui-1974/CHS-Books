"""
GLUE不确定性分析
================

Generalized Likelihood Uncertainty Estimation

GLUE是一种基于贝叶斯框架的不确定性分析方法，
通过蒙特卡洛采样估计参数和预测的不确定性。

核心思想：
- 所有参数集都是可能的
- 根据性能划分"行为"和"非行为"参数集
- 使用似然函数加权
- 估计预测不确定性区间

参考文献：
Beven, K., & Binley, A. (1992). "The future of distributed models: 
model calibration and uncertainty prediction." Hydrological Processes, 
6(3), 279-298.

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Callable, List, Tuple, Dict, Optional
import warnings


class GLUE:
    """
    GLUE不确定性分析
    
    Parameters
    ----------
    model_func : callable
        模型函数，接受参数数组，返回模拟序列
    objective_func : callable
        目标函数，接受模拟值，返回性能指标
    bounds : list of tuple
        参数边界 [(lower, upper), ...]
    behavioral_threshold : float
        行为参数集阈值
    n_samples : int
        蒙特卡洛采样数量
    """
    
    def __init__(self,
                 model_func: Callable,
                 objective_func: Callable,
                 bounds: List[Tuple[float, float]],
                 behavioral_threshold: float = 0.5,
                 n_samples: int = 10000):
        
        self.model_func = model_func
        self.objective_func = objective_func
        self.bounds = np.array(bounds)
        self.n_params = len(bounds)
        self.behavioral_threshold = behavioral_threshold
        self.n_samples = n_samples
        
        # 结果存储
        self.param_samples = None
        self.performance = None
        self.behavioral_mask = None
        self.behavioral_params = None
        self.behavioral_performance = None
        self.simulations = None
        self.behavioral_simulations = None
    
    def _random_sample(self) -> np.ndarray:
        """生成随机参数样本（均匀分布）"""
        samples = np.random.uniform(
            self.bounds[:, 0],
            self.bounds[:, 1],
            size=(self.n_samples, self.n_params)
        )
        return samples
    
    def _latin_hypercube_sample(self) -> np.ndarray:
        """拉丁超立方采样"""
        samples = np.zeros((self.n_samples, self.n_params))
        
        for j in range(self.n_params):
            segments = np.linspace(0, 1, self.n_samples + 1)
            sample_pts = np.random.uniform(segments[:-1], segments[1:])
            np.random.shuffle(sample_pts)
            
            lower, upper = self.bounds[j]
            samples[:, j] = lower + sample_pts * (upper - lower)
        
        return samples
    
    def run(self, sampling_method: str = 'uniform',
            verbose: bool = True) -> Dict:
        """
        执行GLUE分析
        
        Parameters
        ----------
        sampling_method : str
            采样方法：'uniform' 或 'lhs'
        verbose : bool
            是否打印进度
        
        Returns
        -------
        results : dict
            分析结果
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"GLUE不确定性分析")
            print(f"{'='*70}")
            print(f"参数维度: {self.n_params}")
            print(f"采样数量: {self.n_samples}")
            print(f"采样方法: {sampling_method}")
            print(f"行为阈值: {self.behavioral_threshold}\n")
        
        # 1. 生成参数样本
        if verbose:
            print("1. 生成参数样本...")
        
        if sampling_method == 'lhs':
            self.param_samples = self._latin_hypercube_sample()
        else:
            self.param_samples = self._random_sample()
        
        # 2. 运行模型并评估
        if verbose:
            print("2. 运行模型并评估...")
        
        self.performance = np.zeros(self.n_samples)
        self.simulations = []
        
        for i in range(self.n_samples):
            try:
                # 运行模型
                sim = self.model_func(self.param_samples[i])
                self.simulations.append(sim)
                
                # 评估性能
                perf = self.objective_func(sim)
                self.performance[i] = perf
                
            except Exception as e:
                # 模型失败
                self.simulations.append(None)
                self.performance[i] = -999
            
            if verbose and (i + 1) % (self.n_samples // 10) == 0:
                progress = (i + 1) / self.n_samples * 100
                print(f"   进度: {progress:.0f}%")
        
        self.simulations = np.array(self.simulations, dtype=object)
        
        # 3. 识别行为参数集
        if verbose:
            print("\n3. 识别行为参数集...")
        
        self.behavioral_mask = self.performance >= self.behavioral_threshold
        self.behavioral_params = self.param_samples[self.behavioral_mask]
        self.behavioral_performance = self.performance[self.behavioral_mask]
        self.behavioral_simulations = [
            self.simulations[i] for i in range(self.n_samples)
            if self.behavioral_mask[i] and self.simulations[i] is not None
        ]
        
        n_behavioral = len(self.behavioral_params)
        behavioral_ratio = n_behavioral / self.n_samples * 100
        
        if verbose:
            print(f"   行为参数集: {n_behavioral} / {self.n_samples} ({behavioral_ratio:.1f}%)")
            print(f"   最佳性能: {np.max(self.performance):.4f}")
            print(f"   行为集性能范围: [{np.min(self.behavioral_performance):.4f}, "
                  f"{np.max(self.behavioral_performance):.4f}]")
        
        # 4. 计算似然权重
        if verbose:
            print("\n4. 计算似然权重...")
        
        likelihood = self._compute_likelihood(self.behavioral_performance)
        
        # 5. 估计不确定性区间
        if verbose:
            print("5. 估计不确定性区间...\n")
        
        uncertainty_bands = self._compute_uncertainty_bands(
            self.behavioral_simulations,
            likelihood
        )
        
        if verbose:
            print(f"{'='*70}")
            print(f"GLUE分析完成")
            print(f"{'='*70}\n")
        
        return {
            'param_samples': self.param_samples,
            'performance': self.performance,
            'behavioral_mask': self.behavioral_mask,
            'behavioral_params': self.behavioral_params,
            'behavioral_performance': self.behavioral_performance,
            'behavioral_simulations': self.behavioral_simulations,
            'likelihood': likelihood,
            'uncertainty_bands': uncertainty_bands,
            'n_behavioral': n_behavioral,
            'behavioral_ratio': behavioral_ratio
        }
    
    def _compute_likelihood(self, performance: np.ndarray) -> np.ndarray:
        """
        计算似然权重
        
        使用归一化的性能指标作为似然
        """
        # 简单方法：归一化到[0,1]
        likelihood = (performance - self.behavioral_threshold) / \
                    (np.max(performance) - self.behavioral_threshold + 1e-10)
        
        # 归一化为概率分布
        likelihood = likelihood / np.sum(likelihood)
        
        return likelihood
    
    def _compute_uncertainty_bands(self,
                                   simulations: List[np.ndarray],
                                   likelihood: np.ndarray,
                                   percentiles: List[float] = [5, 25, 50, 75, 95]
                                   ) -> Dict:
        """
        计算不确定性区间
        
        Parameters
        ----------
        simulations : list
            行为参数集的模拟结果
        likelihood : ndarray
            似然权重
        percentiles : list
            百分位数
        
        Returns
        -------
        bands : dict
            不确定性区间
        """
        if len(simulations) == 0:
            return {}
        
        # 转换为数组
        sim_array = np.array([s for s in simulations if s is not None])
        
        if len(sim_array) == 0:
            return {}
        
        n_steps = len(sim_array[0])
        bands = {}
        
        # 对每个时间步计算加权百分位数
        for p in percentiles:
            band = np.zeros(n_steps)
            for t in range(n_steps):
                values = sim_array[:, t]
                # 加权百分位数
                band[t] = self._weighted_percentile(values, likelihood, p)
            bands[f'P{p}'] = band
        
        return bands
    
    def _weighted_percentile(self, values: np.ndarray,
                            weights: np.ndarray,
                            percentile: float) -> float:
        """计算加权百分位数"""
        # 排序
        sorted_indices = np.argsort(values)
        sorted_values = values[sorted_indices]
        sorted_weights = weights[sorted_indices]
        
        # 累积权重
        cumsum = np.cumsum(sorted_weights)
        cumsum = cumsum / cumsum[-1]  # 归一化
        
        # 找到百分位数对应的值
        idx = np.searchsorted(cumsum, percentile / 100.0)
        
        if idx >= len(sorted_values):
            idx = len(sorted_values) - 1
        
        return sorted_values[idx]


def glue_analysis(model_func: Callable,
                 objective_func: Callable,
                 bounds: List[Tuple[float, float]],
                 behavioral_threshold: float = 0.5,
                 n_samples: int = 10000,
                 **kwargs) -> Dict:
    """
    GLUE分析的便捷函数
    
    Parameters
    ----------
    model_func : callable
        模型函数
    objective_func : callable
        目标函数
    bounds : list of tuple
        参数边界
    behavioral_threshold : float
        行为阈值
    n_samples : int
        采样数量
    **kwargs : dict
        传递给GLUE的其他参数
    
    Returns
    -------
    results : dict
        分析结果
    """
    glue = GLUE(
        model_func=model_func,
        objective_func=objective_func,
        bounds=bounds,
        behavioral_threshold=behavioral_threshold,
        n_samples=n_samples
    )
    
    return glue.run(**kwargs)


if __name__ == '__main__':
    # 简单测试
    print("GLUE算法测试")
    print("=" * 50)
    
    # 简单的线性模型
    def simple_model(params):
        """y = a*x + b"""
        a, b = params
        x = np.linspace(0, 10, 50)
        return a * x + b
    
    # 真实数据（a=2, b=1加噪声）
    x_true = np.linspace(0, 10, 50)
    y_true = 2 * x_true + 1 + np.random.normal(0, 2, 50)
    
    def objective(simulated):
        """NSE"""
        obs_mean = np.mean(y_true)
        nse = 1 - np.sum((y_true - simulated)**2) / np.sum((y_true - obs_mean)**2)
        return nse
    
    bounds = [(0, 5), (-5, 5)]  # a, b的范围
    
    result = glue_analysis(
        model_func=simple_model,
        objective_func=objective,
        bounds=bounds,
        behavioral_threshold=0.5,
        n_samples=1000
    )
    
    print(f"\n行为参数集: {result['n_behavioral']}")
    print(f"行为比例: {result['behavioral_ratio']:.1f}%")
    print(f"最佳性能: {np.max(result['performance']):.4f}")
    print("\n测试通过！")
