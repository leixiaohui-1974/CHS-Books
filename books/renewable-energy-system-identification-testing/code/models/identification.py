"""
系统辨识基础模块

包含:
1. 最小二乘法 (LS/RLS/WLS)
2. 卡尔曼滤波器 (KF/EKF/UKF)
3. 粒子滤波
4. 模型结构选择

作者: CHS Books
"""

import numpy as np
from typing import Dict, Tuple, Callable
from scipy.optimize import least_squares, minimize


class LeastSquaresIdentification:
    """
    最小二乘参数辨识
    
    适用于线性回归模型: y = X @ theta + noise
    """
    
    def __init__(self, name: str = "LS"):
        self.name = name
        self.theta_est = None
        self.covariance = None
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        批处理最小二乘估计
        
        Args:
            X: 回归矩阵 [n_samples, n_features]
            y: 观测向量 [n_samples]
            
        Returns:
            参数估计 theta
        """
        # theta = (X^T X)^{-1} X^T y
        self.theta_est = np.linalg.lstsq(X, y, rcond=None)[0]
        
        # 计算协方差矩阵
        residuals = y - X @ self.theta_est
        mse = np.mean(residuals**2)
        self.covariance = mse * np.linalg.inv(X.T @ X)
        
        return self.theta_est
    
    def fit_nonlinear(
        self,
        model_func: Callable,
        x_data: np.ndarray,
        y_data: np.ndarray,
        theta_init: np.ndarray
    ) -> np.ndarray:
        """
        非线性最小二乘
        
        Args:
            model_func: 模型函数 y = f(x, theta)
            x_data: 输入数据
            y_data: 输出数据
            theta_init: 初始参数
            
        Returns:
            参数估计
        """
        def residual(theta):
            return y_data - model_func(x_data, theta)
        
        result = least_squares(residual, theta_init)
        self.theta_est = result.x
        
        return self.theta_est


class RecursiveLeastSquares:
    """
    递推最小二乘 (RLS)
    
    在线参数更新
    """
    
    def __init__(
        self,
        n_params: int,
        forgetting_factor: float = 0.99,
        initial_covariance: float = 1000.0,
        name: str = "RLS"
    ):
        """
        初始化RLS
        
        Args:
            n_params: 参数数量
            forgetting_factor: 遗忘因子 (0.95-1.0)
            initial_covariance: 初始协方差
        """
        self.name = name
        self.n_params = n_params
        self.lambda_forget = forgetting_factor
        
        # 初始化
        self.theta = np.zeros(n_params)
        self.P = np.eye(n_params) * initial_covariance
    
    def update(self, phi: np.ndarray, y: float) -> np.ndarray:
        """
        递推更新
        
        Args:
            phi: 回归向量 [n_params]
            y: 观测值
            
        Returns:
            更新后的参数估计
        """
        # 预测误差
        y_pred = phi @ self.theta
        error = y - y_pred
        
        # 增益向量
        K = self.P @ phi / (self.lambda_forget + phi @ self.P @ phi)
        
        # 参数更新
        self.theta = self.theta + K * error
        
        # 协方差更新
        self.P = (self.P - np.outer(K, phi) @ self.P) / self.lambda_forget
        
        return self.theta


class KalmanFilter:
    """
    卡尔曼滤波器
    
    线性系统状态估计
    """
    
    def __init__(
        self,
        A: np.ndarray,  # 状态转移矩阵
        B: np.ndarray,  # 控制矩阵
        C: np.ndarray,  # 观测矩阵
        Q: np.ndarray,  # 过程噪声协方差
        R: np.ndarray,  # 测量噪声协方差
        x0: np.ndarray = None,
        P0: np.ndarray = None,
        name: str = "KF"
    ):
        """
        初始化卡尔曼滤波器
        
        Args:
            A: 状态转移矩阵
            B: 控制矩阵
            C: 观测矩阵
            Q: 过程噪声协方差
            R: 测量噪声协方差
            x0: 初始状态
            P0: 初始协方差
        """
        self.name = name
        self.A = A
        self.B = B
        self.C = C
        self.Q = Q
        self.R = R
        
        n_states = A.shape[0]
        self.x = x0 if x0 is not None else np.zeros(n_states)
        self.P = P0 if P0 is not None else np.eye(n_states)
    
    def predict(self, u: np.ndarray = None) -> np.ndarray:
        """
        预测步骤
        
        Args:
            u: 控制输入
            
        Returns:
            预测状态
        """
        if u is not None:
            self.x = self.A @ self.x + self.B @ u
        else:
            self.x = self.A @ self.x
        
        self.P = self.A @ self.P @ self.A.T + self.Q
        
        return self.x
    
    def update(self, z: np.ndarray) -> np.ndarray:
        """
        更新步骤
        
        Args:
            z: 测量值
            
        Returns:
            更新后的状态估计
        """
        # 创新（innovation）
        y = z - self.C @ self.x
        
        # 创新协方差
        S = self.C @ self.P @ self.C.T + self.R
        
        # 卡尔曼增益
        K = self.P @ self.C.T @ np.linalg.inv(S)
        
        # 状态更新
        self.x = self.x + K @ y
        
        # 协方差更新
        I = np.eye(len(self.x))
        self.P = (I - K @ self.C) @ self.P
        
        return self.x


class ExtendedKalmanFilter:
    """
    扩展卡尔曼滤波 (EKF)
    
    非线性系统状态估计
    """
    
    def __init__(
        self,
        f: Callable,  # 状态转移函数
        h: Callable,  # 观测函数
        F_jacobian: Callable,  # f的雅可比矩阵
        H_jacobian: Callable,  # h的雅可比矩阵
        Q: np.ndarray,
        R: np.ndarray,
        x0: np.ndarray,
        P0: np.ndarray,
        name: str = "EKF"
    ):
        """
        初始化EKF
        
        Args:
            f: 状态转移函数 x(k+1) = f(x(k), u(k))
            h: 观测函数 z(k) = h(x(k))
            F_jacobian: f的雅可比矩阵函数
            H_jacobian: h的雅可比矩阵函数
            Q, R: 噪声协方差
            x0, P0: 初始状态和协方差
        """
        self.name = name
        self.f = f
        self.h = h
        self.F_jacobian = F_jacobian
        self.H_jacobian = H_jacobian
        self.Q = Q
        self.R = R
        self.x = x0
        self.P = P0
    
    def predict(self, u: np.ndarray = None) -> np.ndarray:
        """预测步骤"""
        # 状态预测
        self.x = self.f(self.x, u)
        
        # 雅可比矩阵
        F = self.F_jacobian(self.x, u)
        
        # 协方差预测
        self.P = F @ self.P @ F.T + self.Q
        
        return self.x
    
    def update(self, z: np.ndarray) -> np.ndarray:
        """更新步骤"""
        # 观测预测
        z_pred = self.h(self.x)
        
        # 雅可比矩阵
        H = self.H_jacobian(self.x)
        
        # 创新
        y = z - z_pred
        S = H @ self.P @ H.T + self.R
        
        # 卡尔曼增益
        K = self.P @ H.T @ np.linalg.inv(S)
        
        # 状态更新
        self.x = self.x + K @ y
        
        # 协方差更新
        I = np.eye(len(self.x))
        self.P = (I - K @ H) @ self.P
        
        return self.x


class UnscentedKalmanFilter:
    """
    无迹卡尔曼滤波 (UKF)
    
    使用UT变换处理非线性
    """
    
    def __init__(
        self,
        f: Callable,
        h: Callable,
        Q: np.ndarray,
        R: np.ndarray,
        x0: np.ndarray,
        P0: np.ndarray,
        alpha: float = 1e-3,
        beta: float = 2.0,
        kappa: float = 0.0,
        name: str = "UKF"
    ):
        """
        初始化UKF
        
        Args:
            f: 状态转移函数
            h: 观测函数
            Q, R: 噪声协方差
            x0, P0: 初始状态和协方差
            alpha, beta, kappa: UT变换参数
        """
        self.name = name
        self.f = f
        self.h = h
        self.Q = Q
        self.R = R
        self.x = x0
        self.P = P0
        
        # UT参数
        self.alpha = alpha
        self.beta = beta
        self.kappa = kappa
        
        n = len(x0)
        self.lambda_param = alpha**2 * (n + kappa) - n
    
    def _generate_sigma_points(self) -> np.ndarray:
        """生成sigma点"""
        n = len(self.x)
        lambda_param = self.lambda_param
        
        # Cholesky分解
        L = np.linalg.cholesky((n + lambda_param) * self.P)
        
        # Sigma点
        sigma_points = np.zeros((2*n + 1, n))
        sigma_points[0] = self.x
        for i in range(n):
            sigma_points[i+1] = self.x + L[:, i]
            sigma_points[n+i+1] = self.x - L[:, i]
        
        return sigma_points
    
    def _compute_weights(self) -> Tuple[np.ndarray, np.ndarray]:
        """计算权重"""
        n = len(self.x)
        lambda_param = self.lambda_param
        
        # 均值权重
        Wm = np.full(2*n + 1, 1 / (2*(n + lambda_param)))
        Wm[0] = lambda_param / (n + lambda_param)
        
        # 协方差权重
        Wc = Wm.copy()
        Wc[0] += (1 - self.alpha**2 + self.beta)
        
        return Wm, Wc
    
    def predict(self, u: np.ndarray = None) -> np.ndarray:
        """预测步骤"""
        # 生成sigma点
        sigma_points = self._generate_sigma_points()
        
        # 传播sigma点
        sigma_points_pred = np.array([self.f(sp, u) for sp in sigma_points])
        
        # 权重
        Wm, Wc = self._compute_weights()
        
        # 预测均值
        self.x = np.sum(Wm[:, None] * sigma_points_pred, axis=0)
        
        # 预测协方差
        diff = sigma_points_pred - self.x
        self.P = np.sum(Wc[:, None, None] * (diff[:, :, None] * diff[:, None, :]), axis=0) + self.Q
        
        return self.x
    
    def update(self, z: np.ndarray) -> np.ndarray:
        """更新步骤"""
        # 生成sigma点
        sigma_points = self._generate_sigma_points()
        
        # 观测预测
        z_sigma = np.array([self.h(sp) for sp in sigma_points])
        
        # 权重
        Wm, Wc = self._compute_weights()
        
        # 预测观测
        z_pred = np.sum(Wm[:, None] * z_sigma, axis=0)
        
        # 创新协方差
        diff_z = z_sigma - z_pred
        Pzz = np.sum(Wc[:, None, None] * (diff_z[:, :, None] * diff_z[:, None, :]), axis=0) + self.R
        
        # 交叉协方差
        diff_x = sigma_points - self.x
        Pxz = np.sum(Wc[:, None, None] * (diff_x[:, :, None] * diff_z[:, None, :]), axis=0)
        
        # 卡尔曼增益
        K = Pxz @ np.linalg.inv(Pzz)
        
        # 状态更新
        self.x = self.x + K @ (z - z_pred)
        self.P = self.P - K @ Pzz @ K.T
        
        return self.x


class ParticleFilter:
    """
    粒子滤波
    
    适用于非线性非高斯系统
    """
    
    def __init__(
        self,
        f: Callable,
        h: Callable,
        n_particles: int,
        x_range: Tuple[np.ndarray, np.ndarray],
        process_noise_std: float,
        measurement_noise_std: float,
        name: str = "PF"
    ):
        """
        初始化粒子滤波器
        
        Args:
            f: 状态转移函数
            h: 观测函数
            n_particles: 粒子数量
            x_range: 状态范围 (min, max)
            process_noise_std: 过程噪声标准差
            measurement_noise_std: 测量噪声标准差
        """
        self.name = name
        self.f = f
        self.h = h
        self.n_particles = n_particles
        self.process_noise_std = process_noise_std
        self.measurement_noise_std = measurement_noise_std
        
        # 初始化粒子
        x_min, x_max = x_range
        n_states = len(x_min)
        self.particles = np.random.uniform(x_min, x_max, (n_particles, n_states))
        self.weights = np.ones(n_particles) / n_particles
        
        self.x_est = np.mean(self.particles, axis=0)
    
    def predict(self, u: np.ndarray = None):
        """预测步骤"""
        # 传播粒子
        for i in range(self.n_particles):
            noise = np.random.normal(0, self.process_noise_std, len(self.particles[i]))
            self.particles[i] = self.f(self.particles[i], u) + noise
    
    def update(self, z: np.ndarray):
        """更新步骤"""
        # 计算权重
        for i in range(self.n_particles):
            z_pred = self.h(self.particles[i])
            # 似然函数（假设高斯）
            diff = z - z_pred
            likelihood = np.exp(-0.5 * np.sum((diff / self.measurement_noise_std)**2))
            self.weights[i] *= likelihood
        
        # 归一化权重
        self.weights += 1e-300  # 避免除零
        self.weights /= np.sum(self.weights)
        
        # 状态估计
        self.x_est = np.sum(self.weights[:, None] * self.particles, axis=0)
        
        # 重采样（避免粒子退化）
        if 1.0 / np.sum(self.weights**2) < self.n_particles / 2:
            self._resample()
    
    def _resample(self):
        """重采样"""
        indices = np.random.choice(
            self.n_particles,
            size=self.n_particles,
            p=self.weights
        )
        self.particles = self.particles[indices]
        self.weights = np.ones(self.n_particles) / self.n_particles


class ModelSelection:
    """
    模型结构选择
    
    AIC/BIC准则
    """
    
    @staticmethod
    def aic(n_samples: int, rss: float, n_params: int) -> float:
        """
        赤池信息准则 (AIC)
        
        Args:
            n_samples: 样本数量
            rss: 残差平方和
            n_params: 参数数量
            
        Returns:
            AIC值（越小越好）
        """
        return n_samples * np.log(rss / n_samples) + 2 * n_params
    
    @staticmethod
    def bic(n_samples: int, rss: float, n_params: int) -> float:
        """
        贝叶斯信息准则 (BIC)
        
        Args:
            n_samples: 样本数量
            rss: 残差平方和
            n_params: 参数数量
            
        Returns:
            BIC值（越小越好）
        """
        return n_samples * np.log(rss / n_samples) + n_params * np.log(n_samples)
    
    @staticmethod
    def select_best_model(
        models_results: Dict[str, Dict]
    ) -> str:
        """
        选择最优模型
        
        Args:
            models_results: 模型结果字典
                {'model_name': {'n_samples': n, 'rss': rss, 'n_params': p}}
                
        Returns:
            最优模型名称
        """
        best_model = None
        best_bic = np.inf
        
        for model_name, results in models_results.items():
            bic = ModelSelection.bic(
                results['n_samples'],
                results['rss'],
                results['n_params']
            )
            if bic < best_bic:
                best_bic = bic
                best_model = model_name
        
        return best_model
