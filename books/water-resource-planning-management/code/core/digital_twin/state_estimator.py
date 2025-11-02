"""
状态估计器

集成多种状态估计方法
"""

import numpy as np
from typing import Dict, List, Optional
from .kalman_filter import KalmanFilter, ExtendedKalmanFilter


class StateEstimator:
    """
    通用状态估计器
    
    提供多种估计方法的统一接口
    
    Examples
    --------
    >>> estimator = StateEstimator(method='kalman')
    >>> estimator.initialize(dim_x=2, dim_z=1)
    >>> 
    >>> for measurement in data:
    ...     state = estimator.estimate(measurement)
    """
    
    def __init__(self, method: str = 'kalman'):
        """
        初始化状态估计器
        
        Parameters
        ----------
        method : str
            估计方法：'kalman', 'ekf', 'moving_average'
        """
        self.method = method
        self.filter = None
        self.history = []
    
    def initialize(
        self,
        dim_x: int,
        dim_z: int,
        **kwargs
    ):
        """
        初始化滤波器
        
        Parameters
        ----------
        dim_x : int
            状态维度
        dim_z : int
            观测维度
        **kwargs
            其他参数
        """
        if self.method == 'kalman':
            self.filter = KalmanFilter(dim_x, dim_z)
            
            # 设置矩阵
            if 'F' in kwargs:
                self.filter.F = kwargs['F']
            if 'H' in kwargs:
                self.filter.H = kwargs['H']
            if 'Q' in kwargs:
                self.filter.Q = kwargs['Q']
            if 'R' in kwargs:
                self.filter.R = kwargs['R']
            if 'x0' in kwargs:
                self.filter.x = kwargs['x0'].reshape(-1, 1)
            if 'P0' in kwargs:
                self.filter.P = kwargs['P0']
        
        elif self.method == 'ekf':
            self.filter = ExtendedKalmanFilter(dim_x, dim_z)
            
            # 设置函数
            if 'f' in kwargs:
                self.filter.f = kwargs['f']
            if 'h' in kwargs:
                self.filter.h = kwargs['h']
            if 'Q' in kwargs:
                self.filter.Q = kwargs['Q']
            if 'R' in kwargs:
                self.filter.R = kwargs['R']
            if 'x0' in kwargs:
                self.filter.x = kwargs['x0']
            if 'P0' in kwargs:
                self.filter.P = kwargs['P0']
    
    def estimate(
        self,
        measurement: np.ndarray,
        control: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        估计状态
        
        Parameters
        ----------
        measurement : np.ndarray
            观测值
        control : np.ndarray, optional
            控制输入
        
        Returns
        -------
        np.ndarray
            状态估计
        """
        if self.method in ['kalman', 'ekf']:
            # 预测
            self.filter.predict(control)
            
            # 更新
            self.filter.update(measurement)
            
            # 获取估计状态
            state = self.filter.get_state()
            
            # 记录
            self.history.append({
                'state': state.copy(),
                'measurement': measurement.copy(),
                'covariance': self.filter.get_covariance().copy()
            })
            
            return state
        
        elif self.method == 'moving_average':
            # 简单移动平均
            self.history.append(measurement)
            window = 5
            if len(self.history) > window:
                self.history = self.history[-window:]
            
            return np.mean(self.history, axis=0)
    
    def get_history(self) -> List[Dict]:
        """获取历史记录"""
        return self.history
    
    def get_uncertainty(self) -> Optional[np.ndarray]:
        """
        获取不确定性（协方差）
        
        Returns
        -------
        np.ndarray or None
            当前状态的协方差矩阵
        """
        if self.method in ['kalman', 'ekf'] and self.filter is not None:
            return self.filter.get_covariance()
        return None
    
    def reset(self):
        """重置估计器"""
        self.history = []
        if self.filter is not None:
            if hasattr(self.filter, 'history_x'):
                self.filter.history_x = []
                self.filter.history_P = []
