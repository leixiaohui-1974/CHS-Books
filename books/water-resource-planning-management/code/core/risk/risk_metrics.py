"""
风险度量指标

实现VaR、CVaR等风险度量
"""

import numpy as np
from typing import Union, Callable, Optional


class VaRCalculator:
    """
    风险价值（Value at Risk）计算器
    
    VaR表示在给定置信水平下，投资组合可能遭受的最大损失
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        初始化VaR计算器
        
        Parameters
        ----------
        confidence_level : float
            置信水平，默认0.95（95%）
        """
        if not 0 < confidence_level < 1:
            raise ValueError("confidence_level must be in (0, 1)")
        
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def calculate_historical(self, returns: np.ndarray) -> float:
        """
        历史模拟法计算VaR
        
        Parameters
        ----------
        returns : np.ndarray
            历史收益/损失序列（损失为负值）
        
        Returns
        -------
        float
            VaR值（正值表示损失）
        """
        if len(returns) == 0:
            raise ValueError("returns array is empty")
        
        # 计算分位数（损失，负值）
        quantile = np.quantile(returns, self.alpha)
        
        # VaR为正值表示损失
        var = -quantile
        
        return var
    
    def calculate_parametric(
        self,
        mean: float,
        std: float,
        distribution: str = 'normal'
    ) -> float:
        """
        参数法计算VaR
        
        Parameters
        ----------
        mean : float
            收益均值
        std : float
            收益标准差
        distribution : str
            分布类型，'normal'或't'
        
        Returns
        -------
        float
            VaR值
        """
        if distribution == 'normal':
            # 正态分布
            from scipy.stats import norm
            z = norm.ppf(self.alpha)
            var = -(mean + z * std)
        
        elif distribution == 't':
            # t分布（更保守）
            from scipy.stats import t
            df = 10  # 自由度
            t_value = t.ppf(self.alpha, df)
            var = -(mean + t_value * std)
        
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
        
        return var
    
    def calculate_monte_carlo(
        self,
        simulation_func: Callable,
        n_simulations: int = 10000,
        **kwargs
    ) -> float:
        """
        蒙特卡洛模拟法计算VaR
        
        Parameters
        ----------
        simulation_func : Callable
            模拟函数，返回一个样本
        n_simulations : int
            模拟次数
        **kwargs
            传递给模拟函数的参数
        
        Returns
        -------
        float
            VaR值
        """
        # 生成模拟样本
        samples = np.array([simulation_func(**kwargs) for _ in range(n_simulations)])
        
        # 使用历史模拟法计算
        var = self.calculate_historical(samples)
        
        return var


class CVaRCalculator:
    """
    条件风险价值（Conditional VaR / Expected Shortfall）计算器
    
    CVaR是超过VaR的损失的期望值
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        初始化CVaR计算器
        
        Parameters
        ----------
        confidence_level : float
            置信水平
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
        self.var_calculator = VaRCalculator(confidence_level)
    
    def calculate(self, returns: np.ndarray) -> tuple:
        """
        计算CVaR
        
        Parameters
        ----------
        returns : np.ndarray
            历史收益/损失序列
        
        Returns
        -------
        tuple
            (VaR, CVaR)
        """
        if len(returns) == 0:
            raise ValueError("returns array is empty")
        
        # 先计算VaR
        var = self.var_calculator.calculate_historical(returns)
        
        # CVaR：超过VaR的损失的平均值
        threshold = -var  # 转换为收益空间
        tail_losses = returns[returns <= threshold]
        
        if len(tail_losses) == 0:
            cvar = var
        else:
            cvar = -np.mean(tail_losses)
        
        return var, cvar
    
    def calculate_parametric(self, mean: float, std: float) -> tuple:
        """
        参数法计算CVaR（正态分布）
        
        Parameters
        ----------
        mean : float
            收益均值
        std : float
            收益标准差
        
        Returns
        -------
        tuple
            (VaR, CVaR)
        """
        from scipy.stats import norm
        
        z_alpha = norm.ppf(self.alpha)
        phi_z = norm.pdf(z_alpha)
        
        var = -(mean + z_alpha * std)
        cvar = -(mean + std * phi_z / self.alpha)
        
        return var, cvar


def calculate_downside_risk(
    returns: np.ndarray,
    target: float = 0.0
) -> float:
    """
    计算下行风险（Downside Risk）
    
    只考虑低于目标收益的风险
    
    Parameters
    ----------
    returns : np.ndarray
        收益序列
    target : float
        目标收益
    
    Returns
    -------
    float
        下行标准差
    """
    shortfall = returns - target
    downside_returns = shortfall[shortfall < 0]
    
    if len(downside_returns) == 0:
        return 0.0
    
    downside_variance = np.mean(downside_returns ** 2)
    downside_risk = np.sqrt(downside_variance)
    
    return downside_risk


def calculate_probability_of_failure(
    samples: np.ndarray,
    threshold: float
) -> float:
    """
    计算失效概率
    
    Parameters
    ----------
    samples : np.ndarray
        样本数据
    threshold : float
        失效阈值
    
    Returns
    -------
    float
        失效概率
    """
    n_failures = np.sum(samples < threshold)
    probability = n_failures / len(samples)
    
    return probability


def calculate_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.0
) -> float:
    """
    计算夏普比率（Sharpe Ratio）
    
    衡量单位风险的超额收益
    
    Parameters
    ----------
    returns : np.ndarray
        收益序列
    risk_free_rate : float
        无风险收益率
    
    Returns
    -------
    float
        夏普比率
    """
    excess_returns = returns - risk_free_rate
    mean_return = np.mean(excess_returns)
    std_return = np.std(excess_returns)
    
    if std_return == 0:
        return 0.0
    
    sharpe = mean_return / std_return
    
    return sharpe


def calculate_sortino_ratio(
    returns: np.ndarray,
    target: float = 0.0
) -> float:
    """
    计算索提诺比率（Sortino Ratio）
    
    使用下行风险代替标准差
    
    Parameters
    ----------
    returns : np.ndarray
        收益序列
    target : float
        目标收益
    
    Returns
    -------
    float
        索提诺比率
    """
    excess_returns = returns - target
    mean_return = np.mean(excess_returns)
    downside_risk = calculate_downside_risk(returns, target)
    
    if downside_risk == 0:
        return 0.0
    
    sortino = mean_return / downside_risk
    
    return sortino
