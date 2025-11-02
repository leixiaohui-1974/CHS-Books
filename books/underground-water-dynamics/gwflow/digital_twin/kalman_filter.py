"""
卡尔曼滤波器模块

实现标准卡尔曼滤波和集合卡尔曼滤波（EnKF）用于数据同化。

理论基础:
-----------
卡尔曼滤波是一种递归估计方法，用于从含噪声的观测中估计系统状态。

**预测步**（Prediction）：
    x̂⁻ = F * x̂ + B * u          状态预测
    P⁻ = F * P * F^T + Q         协方差预测

**更新步**（Update）：
    K = P⁻ * H^T / (H * P⁻ * H^T + R)   卡尔曼增益
    x̂ = x̂⁻ + K * (z - H * x̂⁻)         状态更新
    P = (I - K * H) * P⁻                协方差更新

变量说明:
    x: 状态向量（如地下水头）
    z: 观测向量
    F: 状态转移矩阵
    H: 观测矩阵
    Q: 过程噪声协方差
    R: 观测噪声协方差
    K: 卡尔曼增益

参考文献:
    - Kalman, R. E. (1960). A new approach to linear filtering and prediction problems.
    - Evensen, G. (1994). Sequential data assimilation with a nonlinear 
      quasi-geostrophic model using Monte Carlo methods.
"""

import numpy as np
from typing import Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class KalmanFilterResult:
    """卡尔曼滤波结果"""
    x_pred: np.ndarray      # 预测状态
    P_pred: np.ndarray      # 预测协方差
    x_update: np.ndarray    # 更新后状态
    P_update: np.ndarray    # 更新后协方差
    K: np.ndarray          # 卡尔曼增益
    innovation: np.ndarray  # 创新（观测-预测）
    innovation_cov: np.ndarray  # 创新协方差


class KalmanFilter:
    """
    标准卡尔曼滤波器
    
    用于线性系统的状态估计和数据同化。
    
    Parameters
    ----------
    F : np.ndarray
        状态转移矩阵 (n_states × n_states)
    H : np.ndarray
        观测矩阵 (n_obs × n_states)
    Q : np.ndarray
        过程噪声协方差矩阵 (n_states × n_states)
    R : np.ndarray
        观测噪声协方差矩阵 (n_obs × n_obs)
    B : np.ndarray, optional
        控制输入矩阵 (n_states × n_controls)
    
    Attributes
    ----------
    n_states : int
        状态向量维度
    n_obs : int
        观测向量维度
    
    Examples
    --------
    >>> F = np.eye(10)  # 状态转移
    >>> H = np.eye(10)[:3]  # 观测3个状态
    >>> Q = 0.01 * np.eye(10)  # 过程噪声
    >>> R = 0.1 * np.eye(3)  # 观测噪声
    >>> kf = KalmanFilter(F, H, Q, R)
    >>> x = np.zeros(10)
    >>> P = np.eye(10)
    >>> z = np.array([1.0, 2.0, 3.0])
    >>> result = kf.filter_step(x, P, z)
    """
    
    def __init__(
        self,
        F: np.ndarray,
        H: np.ndarray,
        Q: np.ndarray,
        R: np.ndarray,
        B: Optional[np.ndarray] = None
    ):
        self.F = F
        self.H = H
        self.Q = Q
        self.R = R
        self.B = B
        
        self.n_states = F.shape[0]
        self.n_obs = H.shape[0]
        
        # 验证矩阵维度
        assert F.shape == (self.n_states, self.n_states), "F must be square"
        assert H.shape[1] == self.n_states, "H must have n_states columns"
        assert Q.shape == (self.n_states, self.n_states), "Q must match F"
        assert R.shape == (self.n_obs, self.n_obs), "R must match H rows"
    
    def predict(
        self,
        x: np.ndarray,
        P: np.ndarray,
        u: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        预测步：根据系统模型预测下一状态
        
        Parameters
        ----------
        x : np.ndarray
            当前状态估计 (n_states,)
        P : np.ndarray
            当前状态协方差 (n_states, n_states)
        u : np.ndarray, optional
            控制输入 (n_controls,)
        
        Returns
        -------
        x_pred : np.ndarray
            预测状态
        P_pred : np.ndarray
            预测协方差
        """
        # 状态预测
        x_pred = self.F @ x
        if u is not None and self.B is not None:
            x_pred += self.B @ u
        
        # 协方差预测
        P_pred = self.F @ P @ self.F.T + self.Q
        
        return x_pred, P_pred
    
    def update(
        self,
        x_pred: np.ndarray,
        P_pred: np.ndarray,
        z: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        更新步：利用观测数据修正状态估计
        
        Parameters
        ----------
        x_pred : np.ndarray
            预测状态 (n_states,)
        P_pred : np.ndarray
            预测协方差 (n_states, n_states)
        z : np.ndarray
            观测数据 (n_obs,)
        
        Returns
        -------
        x_update : np.ndarray
            更新后状态
        P_update : np.ndarray
            更新后协方差
        K : np.ndarray
            卡尔曼增益
        innovation : np.ndarray
            创新（观测残差）
        innovation_cov : np.ndarray
            创新协方差
        """
        # 创新（观测残差）
        innovation = z - self.H @ x_pred
        
        # 创新协方差
        innovation_cov = self.H @ P_pred @ self.H.T + self.R
        
        # 卡尔曼增益
        K = P_pred @ self.H.T @ np.linalg.inv(innovation_cov)
        
        # 状态更新
        x_update = x_pred + K @ innovation
        
        # 协方差更新（Joseph形式，数值稳定）
        I_KH = np.eye(self.n_states) - K @ self.H
        P_update = I_KH @ P_pred @ I_KH.T + K @ self.R @ K.T
        
        return x_update, P_update, K, innovation, innovation_cov
    
    def filter_step(
        self,
        x: np.ndarray,
        P: np.ndarray,
        z: np.ndarray,
        u: Optional[np.ndarray] = None
    ) -> KalmanFilterResult:
        """
        完整的滤波步骤（预测+更新）
        
        Parameters
        ----------
        x : np.ndarray
            当前状态
        P : np.ndarray
            当前协方差
        z : np.ndarray
            观测数据
        u : np.ndarray, optional
            控制输入
        
        Returns
        -------
        result : KalmanFilterResult
            包含预测和更新结果的数据类
        """
        # 预测
        x_pred, P_pred = self.predict(x, P, u)
        
        # 更新
        x_update, P_update, K, innovation, innovation_cov = self.update(
            x_pred, P_pred, z
        )
        
        return KalmanFilterResult(
            x_pred=x_pred,
            P_pred=P_pred,
            x_update=x_update,
            P_update=P_update,
            K=K,
            innovation=innovation,
            innovation_cov=innovation_cov
        )


class EnsembleKalmanFilter:
    """
    集合卡尔曼滤波器（EnKF）
    
    使用蒙特卡洛样本估计协方差，适用于高维非线性系统。
    
    Parameters
    ----------
    n_ensemble : int
        集合成员数量
    H : np.ndarray
        观测矩阵 (n_obs × n_states)
    R : np.ndarray
        观测噪声协方差 (n_obs × n_obs)
    inflation : float, optional
        协方差膨胀因子（防止集合退化），默认1.0
    
    Notes
    -----
    EnKF不需要显式的状态转移矩阵F和过程噪声Q，
    而是通过运行模型集合来隐式传播不确定性。
    
    References
    ----------
    Evensen, G. (1994). Sequential data assimilation with a nonlinear 
    quasi-geostrophic model using Monte Carlo methods to forecast error statistics.
    
    Examples
    --------
    >>> enkf = EnsembleKalmanFilter(n_ensemble=50, H=H, R=R)
    >>> ensemble = np.random.randn(50, 10)  # 50个样本，10个状态
    >>> z = np.array([1.0, 2.0, 3.0])
    >>> ensemble_updated = enkf.assimilate(ensemble, z)
    """
    
    def __init__(
        self,
        n_ensemble: int,
        H: np.ndarray,
        R: np.ndarray,
        inflation: float = 1.0
    ):
        self.n_ensemble = n_ensemble
        self.H = H
        self.R = R
        self.inflation = inflation
        
        self.n_obs = H.shape[0]
        self.n_states = H.shape[1]
    
    def assimilate(
        self,
        ensemble: np.ndarray,
        z: np.ndarray
    ) -> np.ndarray:
        """
        同化观测数据到集合
        
        Parameters
        ----------
        ensemble : np.ndarray
            状态集合 (n_ensemble × n_states)
        z : np.ndarray
            观测数据 (n_obs,)
        
        Returns
        -------
        ensemble_updated : np.ndarray
            同化后的状态集合
        """
        n_ens = ensemble.shape[0]
        
        # 计算集合均值
        x_mean = np.mean(ensemble, axis=0)
        
        # 计算集合偏差矩阵
        A = ensemble - x_mean  # (n_ens × n_states)
        
        # 协方差膨胀
        if self.inflation != 1.0:
            A *= np.sqrt(self.inflation)
        
        # 预测观测集合
        Y = (self.H @ A.T).T  # (n_ens × n_obs)
        y_mean = np.mean(Y, axis=0)
        
        # 创新协方差（集合估计）
        S = Y - y_mean  # (n_ens × n_obs)
        C_yy = (S.T @ S) / (n_ens - 1) + self.R
        
        # 状态-观测协方差
        C_xy = (A.T @ S) / (n_ens - 1)  # (n_states × n_obs)
        
        # 卡尔曼增益
        K = C_xy @ np.linalg.inv(C_yy)  # (n_states × n_obs)
        
        # 为每个集合成员生成扰动观测
        z_perturbed = z + np.random.multivariate_normal(
            np.zeros(self.n_obs),
            self.R,
            size=n_ens
        )
        
        # 更新集合
        ensemble_updated = np.zeros_like(ensemble)
        for i in range(n_ens):
            y_i = self.H @ ensemble[i]
            innovation_i = z_perturbed[i] - y_i
            ensemble_updated[i] = ensemble[i] + K @ innovation_i
        
        return ensemble_updated
    
    def get_mean_and_cov(
        self,
        ensemble: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        从集合计算均值和协方差
        
        Parameters
        ----------
        ensemble : np.ndarray
            状态集合 (n_ensemble × n_states)
        
        Returns
        -------
        mean : np.ndarray
            集合均值
        cov : np.ndarray
            集合协方差
        """
        mean = np.mean(ensemble, axis=0)
        A = ensemble - mean
        cov = (A.T @ A) / (ensemble.shape[0] - 1)
        return mean, cov


def compute_rmse(
    estimated: np.ndarray,
    truth: np.ndarray
) -> float:
    """
    计算均方根误差（RMSE）
    
    Parameters
    ----------
    estimated : np.ndarray
        估计值
    truth : np.ndarray
        真实值
    
    Returns
    -------
    rmse : float
        均方根误差
    """
    return np.sqrt(np.mean((estimated - truth) ** 2))


def compute_mae(
    estimated: np.ndarray,
    truth: np.ndarray
) -> float:
    """
    计算平均绝对误差（MAE）
    
    Parameters
    ----------
    estimated : np.ndarray
        估计值
    truth : np.ndarray
        真实值
    
    Returns
    -------
    mae : float
        平均绝对误差
    """
    return np.mean(np.abs(estimated - truth))
