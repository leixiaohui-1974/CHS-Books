"""
卡尔曼滤波器

实现标准卡尔曼滤波（KF）和扩展卡尔曼滤波（EKF）
"""

import numpy as np
from typing import Callable, Optional, Tuple


class KalmanFilter:
    """
    标准卡尔曼滤波器
    
    适用于线性系统：
    - 状态方程：x_k = A*x_{k-1} + B*u_k + w_k
    - 观测方程：z_k = H*x_k + v_k
    
    Examples
    --------
    >>> kf = KalmanFilter(dim_x=2, dim_z=1)
    >>> kf.F = np.array([[1, 1], [0, 1]])  # 状态转移矩阵
    >>> kf.H = np.array([[1, 0]])          # 观测矩阵
    >>> 
    >>> for z in measurements:
    ...     kf.predict()
    ...     kf.update(z)
    ...     print(kf.x)  # 估计状态
    """
    
    def __init__(
        self,
        dim_x: int,
        dim_z: int,
        dim_u: int = 0
    ):
        """
        初始化卡尔曼滤波器
        
        Parameters
        ----------
        dim_x : int
            状态维度
        dim_z : int
            观测维度
        dim_u : int
            控制输入维度
        """
        self.dim_x = dim_x
        self.dim_z = dim_z
        self.dim_u = dim_u
        
        # 状态
        self.x = np.zeros((dim_x, 1))  # 状态估计
        self.P = np.eye(dim_x)         # 状态协方差
        
        # 系统矩阵
        self.F = np.eye(dim_x)         # 状态转移矩阵
        self.B = None                  # 控制矩阵
        self.H = np.zeros((dim_z, dim_x))  # 观测矩阵
        
        # 噪声协方差
        self.Q = np.eye(dim_x)         # 过程噪声
        self.R = np.eye(dim_z)         # 观测噪声
        
        # 预测与更新
        self.x_prior = self.x.copy()
        self.P_prior = self.P.copy()
        
        # 历史记录
        self.history_x = []
        self.history_P = []
    
    def predict(self, u: Optional[np.ndarray] = None):
        """
        预测步骤
        
        x_k|k-1 = F*x_{k-1} + B*u_k
        P_k|k-1 = F*P_{k-1}*F^T + Q
        
        Parameters
        ----------
        u : np.ndarray, optional
            控制输入
        """
        # 状态预测
        if u is not None and self.B is not None:
            self.x = self.F @ self.x + self.B @ u
        else:
            self.x = self.F @ self.x
        
        # 协方差预测
        self.P = self.F @ self.P @ self.F.T + self.Q
        
        # 保存先验估计
        self.x_prior = self.x.copy()
        self.P_prior = self.P.copy()
    
    def update(self, z: np.ndarray):
        """
        更新步骤
        
        K_k = P_k|k-1 * H^T * (H*P_k|k-1*H^T + R)^{-1}
        x_k = x_k|k-1 + K_k*(z_k - H*x_k|k-1)
        P_k = (I - K_k*H)*P_k|k-1
        
        Parameters
        ----------
        z : np.ndarray
            观测值
        """
        # 确保z是列向量
        if z.ndim == 1:
            z = z.reshape(-1, 1)
        
        # 计算卡尔曼增益
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # 更新状态
        y = z - self.H @ self.x  # 新息（innovation）
        self.x = self.x + K @ y
        
        # 更新协方差（Joseph形式，数值稳定）
        I_KH = np.eye(self.dim_x) - K @ self.H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R @ K.T
        
        # 记录历史
        self.history_x.append(self.x.copy())
        self.history_P.append(self.P.copy())
    
    def get_state(self) -> np.ndarray:
        """获取当前状态估计"""
        return self.x.flatten()
    
    def get_covariance(self) -> np.ndarray:
        """获取当前协方差"""
        return self.P


class ExtendedKalmanFilter:
    """
    扩展卡尔曼滤波器（EKF）
    
    适用于非线性系统：
    - 状态方程：x_k = f(x_{k-1}, u_k) + w_k
    - 观测方程：z_k = h(x_k) + v_k
    
    Examples
    --------
    >>> def f(x, u):
    ...     # 非线性状态转移函数
    ...     return np.array([x[0] + x[1]*dt, x[1]])
    >>> 
    >>> def h(x):
    ...     # 非线性观测函数
    ...     return np.array([x[0]])
    >>> 
    >>> ekf = ExtendedKalmanFilter(dim_x=2, dim_z=1)
    >>> ekf.f = f
    >>> ekf.h = h
    """
    
    def __init__(
        self,
        dim_x: int,
        dim_z: int,
        f: Optional[Callable] = None,
        h: Optional[Callable] = None
    ):
        """
        初始化扩展卡尔曼滤波器
        
        Parameters
        ----------
        dim_x : int
            状态维度
        dim_z : int
            观测维度
        f : Callable, optional
            状态转移函数
        h : Callable, optional
            观测函数
        """
        self.dim_x = dim_x
        self.dim_z = dim_z
        
        # 状态
        self.x = np.zeros(dim_x)
        self.P = np.eye(dim_x)
        
        # 非线性函数
        self.f = f  # f(x, u) -> x_next
        self.h = h  # h(x) -> z
        
        # 雅可比矩阵函数（可选）
        self.F_jacobian = None  # df/dx
        self.H_jacobian = None  # dh/dx
        
        # 噪声协方差
        self.Q = np.eye(dim_x)
        self.R = np.eye(dim_z)
        
        # 历史
        self.history_x = []
        self.history_P = []
    
    def predict(self, u: Optional[np.ndarray] = None, dt: float = 1.0):
        """
        预测步骤（非线性）
        
        Parameters
        ----------
        u : np.ndarray, optional
            控制输入
        dt : float
            时间步长
        """
        # 状态预测（非线性）
        if self.f is not None:
            self.x = self.f(self.x, u, dt)
        
        # 计算雅可比矩阵
        if self.F_jacobian is not None:
            F = self.F_jacobian(self.x, u, dt)
        else:
            # 数值微分
            F = self._numerical_jacobian(lambda x: self.f(x, u, dt), self.x)
        
        # 协方差预测
        self.P = F @ self.P @ F.T + self.Q
    
    def update(self, z: np.ndarray):
        """
        更新步骤（非线性）
        
        Parameters
        ----------
        z : np.ndarray
            观测值
        """
        # 预测观测
        z_pred = self.h(self.x) if self.h is not None else self.x
        
        # 计算观测雅可比矩阵
        if self.H_jacobian is not None:
            H = self.H_jacobian(self.x)
        else:
            # 数值微分
            H = self._numerical_jacobian(self.h, self.x)
        
        # 计算卡尔曼增益
        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)
        
        # 更新状态
        y = z - z_pred  # 新息
        self.x = self.x + K @ y
        
        # 更新协方差
        I_KH = np.eye(self.dim_x) - K @ H
        self.P = I_KH @ self.P
        
        # 记录
        self.history_x.append(self.x.copy())
        self.history_P.append(self.P.copy())
    
    def _numerical_jacobian(
        self,
        func: Callable,
        x: np.ndarray,
        epsilon: float = 1e-5
    ) -> np.ndarray:
        """
        数值计算雅可比矩阵
        
        Parameters
        ----------
        func : Callable
            函数 f: R^n -> R^m
        x : np.ndarray
            当前点
        epsilon : float
            微小扰动
        
        Returns
        -------
        np.ndarray
            雅可比矩阵 (m, n)
        """
        f0 = func(x)
        n = len(x)
        m = len(f0) if isinstance(f0, np.ndarray) else 1
        
        J = np.zeros((m, n))
        
        for i in range(n):
            x_plus = x.copy()
            x_plus[i] += epsilon
            f_plus = func(x_plus)
            
            J[:, i] = (f_plus - f0) / epsilon
        
        return J
    
    def get_state(self) -> np.ndarray:
        """获取当前状态估计"""
        return self.x
    
    def get_covariance(self) -> np.ndarray:
        """获取当前协方差"""
        return self.P
