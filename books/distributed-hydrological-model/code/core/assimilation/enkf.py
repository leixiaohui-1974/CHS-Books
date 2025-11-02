"""
集合卡尔曼滤波（EnKF）
=====================

Ensemble Kalman Filter

EnKF是一种基于蒙特卡洛方法的数据同化技术，
通过集合预报估计背景误差协方差，
利用观测数据更新模型状态。

核心思想：
- 使用集合（ensemble）表示状态不确定性
- 预报步：运行集合成员获得预报
- 分析步：利用观测更新状态
- 适用于非线性模型

参考文献：
Evensen, G. (1994). "Sequential data assimilation with a 
nonlinear quasi-geostrophic model using Monte Carlo methods 
to forecast error statistics." Journal of Geophysical Research, 
99(C5), 10143-10162.

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Callable, List, Tuple, Dict, Optional
import warnings


class EnKF:
    """
    集合卡尔曼滤波
    
    Parameters
    ----------
    model_func : callable
        模型函数，接受状态和输入，返回新状态
    n_ensemble : int
        集合成员数量
    state_dim : int
        状态维度
    obs_dim : int
        观测维度
    inflation_factor : float
        膨胀因子（防止滤波发散）
    """
    
    def __init__(self,
                 model_func: Callable,
                 n_ensemble: int = 50,
                 state_dim: int = None,
                 obs_dim: int = 1,
                 inflation_factor: float = 1.0):
        
        self.model_func = model_func
        self.n_ensemble = n_ensemble
        self.state_dim = state_dim
        self.obs_dim = obs_dim
        self.inflation_factor = inflation_factor
        
        # 集合状态
        self.ensemble = None
        
        # 历史记录
        self.history = {
            'ensemble_mean': [],
            'ensemble_std': [],
            'analysis': [],
            'observations': []
        }
    
    def initialize_ensemble(self, mean_state: np.ndarray,
                          std_state: np.ndarray) -> np.ndarray:
        """
        初始化集合
        
        Parameters
        ----------
        mean_state : ndarray (state_dim,)
            初始状态均值
        std_state : ndarray (state_dim,)
            初始状态标准差
        
        Returns
        -------
        ensemble : ndarray (n_ensemble, state_dim)
            初始集合
        """
        if self.state_dim is None:
            self.state_dim = len(mean_state)
        
        self.ensemble = np.zeros((self.n_ensemble, self.state_dim))
        
        for i in range(self.n_ensemble):
            self.ensemble[i] = mean_state + std_state * np.random.randn(self.state_dim)
        
        return self.ensemble
    
    def forecast(self, inputs: np.ndarray,
                process_noise_std: float = 0.0) -> np.ndarray:
        """
        预报步：运行模型获得预报集合
        
        Parameters
        ----------
        inputs : ndarray
            模型输入
        process_noise_std : float
            过程噪声标准差
        
        Returns
        -------
        forecast_ensemble : ndarray (n_ensemble, state_dim)
            预报集合
        """
        forecast_ensemble = np.zeros_like(self.ensemble)
        
        for i in range(self.n_ensemble):
            # 运行模型
            forecast_state = self.model_func(self.ensemble[i], inputs)
            
            # 添加过程噪声
            if process_noise_std > 0:
                forecast_state += process_noise_std * np.random.randn(self.state_dim)
            
            forecast_ensemble[i] = forecast_state
        
        # 膨胀（防止滤波发散）
        if self.inflation_factor != 1.0:
            mean = np.mean(forecast_ensemble, axis=0)
            forecast_ensemble = mean + self.inflation_factor * (forecast_ensemble - mean)
        
        self.ensemble = forecast_ensemble
        return forecast_ensemble
    
    def analysis(self, observation: np.ndarray,
                obs_operator: Callable,
                obs_error_std: float) -> np.ndarray:
        """
        分析步：利用观测更新状态
        
        Parameters
        ----------
        observation : ndarray (obs_dim,)
            观测值
        obs_operator : callable
            观测算子，将状态映射到观测空间
        obs_error_std : float
            观测误差标准差
        
        Returns
        -------
        analysis_ensemble : ndarray (n_ensemble, state_dim)
            分析集合
        """
        # 1. 计算预报观测
        forecast_obs = np.zeros((self.n_ensemble, self.obs_dim))
        for i in range(self.n_ensemble):
            forecast_obs[i] = obs_operator(self.ensemble[i])
        
        # 2. 计算预报观测的均值和偏差
        mean_forecast_obs = np.mean(forecast_obs, axis=0)
        D = forecast_obs - mean_forecast_obs  # (n_ensemble, obs_dim)
        
        # 3. 计算预报状态的均值和偏差
        mean_forecast = np.mean(self.ensemble, axis=0)
        A = self.ensemble - mean_forecast  # (n_ensemble, state_dim)
        
        # 4. 计算卡尔曼增益
        # P_f H^T
        PHT = (1.0 / (self.n_ensemble - 1)) * A.T @ D  # (state_dim, obs_dim)
        
        # H P_f H^T + R
        HPHT_R = (1.0 / (self.n_ensemble - 1)) * D.T @ D + obs_error_std**2 * np.eye(self.obs_dim)
        
        # K = P_f H^T (H P_f H^T + R)^{-1}
        K = PHT @ np.linalg.inv(HPHT_R)  # (state_dim, obs_dim)
        
        # 5. 更新集合
        analysis_ensemble = np.zeros_like(self.ensemble)
        
        for i in range(self.n_ensemble):
            # 扰动观测
            perturbed_obs = observation + obs_error_std * np.random.randn(self.obs_dim)
            
            # 计算创新（innovation）
            innovation = perturbed_obs - forecast_obs[i]
            
            # 更新状态
            analysis_ensemble[i] = self.ensemble[i] + K @ innovation
        
        self.ensemble = analysis_ensemble
        return analysis_ensemble
    
    def get_mean_state(self) -> np.ndarray:
        """获取集合均值状态"""
        return np.mean(self.ensemble, axis=0)
    
    def get_std_state(self) -> np.ndarray:
        """获取集合标准差"""
        return np.std(self.ensemble, axis=0)
    
    def run(self, 
            observations: np.ndarray,
            inputs: np.ndarray,
            obs_operator: Callable,
            obs_error_std: float,
            process_noise_std: float = 0.0,
            initial_state_mean: np.ndarray = None,
            initial_state_std: np.ndarray = None,
            verbose: bool = True) -> Dict:
        """
        运行EnKF数据同化
        
        Parameters
        ----------
        observations : ndarray (n_steps, obs_dim)
            观测序列
        inputs : ndarray (n_steps, input_dim)
            输入序列
        obs_operator : callable
            观测算子
        obs_error_std : float
            观测误差标准差
        process_noise_std : float
            过程噪声标准差
        initial_state_mean : ndarray
            初始状态均值
        initial_state_std : ndarray
            初始状态标准差
        verbose : bool
            是否打印进度
        
        Returns
        -------
        results : dict
            同化结果
        """
        n_steps = len(observations)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"EnKF数据同化")
            print(f"{'='*70}")
            print(f"集合成员数: {self.n_ensemble}")
            print(f"状态维度: {self.state_dim}")
            print(f"观测维度: {self.obs_dim}")
            print(f"时间步数: {n_steps}\n")
        
        # 初始化集合
        if initial_state_mean is not None and initial_state_std is not None:
            self.initialize_ensemble(initial_state_mean, initial_state_std)
        
        # 初始化历史记录
        self.history = {
            'ensemble_mean': [],
            'ensemble_std': [],
            'forecast_mean': [],
            'analysis_mean': [],
            'observations': []
        }
        
        # 时间循环
        for t in range(n_steps):
            # 预报步
            self.forecast(inputs[t], process_noise_std)
            forecast_mean = self.get_mean_state()
            
            # 如果有观测，进行分析
            if not np.isnan(observations[t]).any():
                self.analysis(observations[t], obs_operator, obs_error_std)
                analysis_mean = self.get_mean_state()
            else:
                analysis_mean = forecast_mean
            
            # 记录
            self.history['forecast_mean'].append(forecast_mean)
            self.history['analysis_mean'].append(analysis_mean)
            self.history['ensemble_mean'].append(self.get_mean_state())
            self.history['ensemble_std'].append(self.get_std_state())
            self.history['observations'].append(observations[t])
            
            if verbose and (t + 1) % max(1, n_steps // 10) == 0:
                progress = (t + 1) / n_steps * 100
                print(f"   进度: {progress:.0f}%")
        
        # 转换为数组
        for key in self.history:
            self.history[key] = np.array(self.history[key])
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"EnKF同化完成")
            print(f"{'='*70}\n")
        
        return self.history


def enkf_assimilation(model_func: Callable,
                     observations: np.ndarray,
                     inputs: np.ndarray,
                     obs_operator: Callable,
                     obs_error_std: float,
                     n_ensemble: int = 50,
                     **kwargs) -> Dict:
    """
    EnKF数据同化的便捷函数
    
    Parameters
    ----------
    model_func : callable
        模型函数
    observations : ndarray
        观测序列
    inputs : ndarray
        输入序列
    obs_operator : callable
        观测算子
    obs_error_std : float
        观测误差标准差
    n_ensemble : int
        集合成员数量
    **kwargs : dict
        传递给EnKF的其他参数
    
    Returns
    -------
    results : dict
        同化结果
    """
    enkf = EnKF(
        model_func=model_func,
        n_ensemble=n_ensemble
    )
    
    return enkf.run(
        observations=observations,
        inputs=inputs,
        obs_operator=obs_operator,
        obs_error_std=obs_error_std,
        **kwargs
    )


if __name__ == '__main__':
    # 简单测试
    print("EnKF算法测试")
    print("=" * 50)
    
    # 简单的线性模型: x(t+1) = 0.9*x(t) + u(t)
    def simple_model(state, inputs):
        return 0.9 * state + inputs
    
    # 观测算子：直接观测状态
    def obs_operator(state):
        return state
    
    # 生成真实轨迹
    n_steps = 50
    true_state = np.zeros(n_steps)
    inputs = np.random.randn(n_steps) * 0.1
    
    for t in range(1, n_steps):
        true_state[t] = 0.9 * true_state[t-1] + inputs[t] + 0.1 * np.random.randn()
    
    # 生成观测
    observations = true_state + 0.5 * np.random.randn(n_steps)
    
    # EnKF同化
    enkf = EnKF(model_func=simple_model, n_ensemble=30, state_dim=1, obs_dim=1)
    
    results = enkf.run(
        observations=observations.reshape(-1, 1),
        inputs=inputs.reshape(-1, 1),
        obs_operator=obs_operator,
        obs_error_std=0.5,
        process_noise_std=0.1,
        initial_state_mean=np.array([0.0]),
        initial_state_std=np.array([1.0]),
        verbose=True
    )
    
    # 计算RMSE
    analysis_mean = results['analysis_mean'].flatten()
    rmse = np.sqrt(np.mean((analysis_mean - true_state)**2))
    
    print(f"\nRMSE: {rmse:.4f}")
    print("\n测试通过！")
