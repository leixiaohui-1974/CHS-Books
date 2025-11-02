"""
模型预测控制器（MPC）

基于模型的预测控制算法，用于多变量约束优化控制
"""

import numpy as np
from typing import Optional, Callable, Dict
from scipy.optimize import minimize


class MPCController:
    """
    模型预测控制器
    
    基本思想：
    1. 使用系统模型预测未来状态
    2. 求解优化问题得到最优控制序列
    3. 只执行第一个控制动作
    4. 滚动优化（Receding Horizon）
    
    Examples
    --------
    >>> # 定义系统模型
    >>> def model(x, u):
    ...     # x: 状态, u: 控制
    ...     return A @ x + B @ u
    >>> 
    >>> # 创建MPC控制器
    >>> mpc = MPCController(
    ...     model=model,
    ...     horizon=10,
    ...     n_states=2,
    ...     n_controls=1
    ... )
    >>> 
    >>> # 控制循环
    >>> x = np.array([0.0, 0.0])  # 初始状态
    >>> for t in range(100):
    ...     u = mpc.compute(x, target=[1.0, 0.0])
    ...     x = model(x, u[0])  # 应用第一个控制
    """
    
    def __init__(
        self,
        model: Callable,
        horizon: int,
        n_states: int,
        n_controls: int,
        dt: float = 1.0,
        Q: Optional[np.ndarray] = None,
        R: Optional[np.ndarray] = None,
        control_limits: Optional[tuple] = None,
        state_limits: Optional[tuple] = None
    ):
        """
        初始化MPC控制器
        
        Parameters
        ----------
        model : Callable
            系统模型函数 f(x, u) -> x_next
        horizon : int
            预测时域长度
        n_states : int
            状态维度
        n_controls : int
            控制维度
        dt : float
            采样时间
        Q : np.ndarray, optional
            状态权重矩阵
        R : np.ndarray, optional
            控制权重矩阵
        control_limits : tuple, optional
            控制约束 (u_min, u_max)
        state_limits : tuple, optional
            状态约束 (x_min, x_max)
        """
        self.model = model
        self.horizon = horizon
        self.n_states = n_states
        self.n_controls = n_controls
        self.dt = dt
        
        # 权重矩阵
        if Q is None:
            self.Q = np.eye(n_states)
        else:
            self.Q = Q
        
        if R is None:
            self.R = np.eye(n_controls) * 0.01
        else:
            self.R = R
        
        # 约束
        self.control_limits = control_limits
        self.state_limits = state_limits
        
        # 历史记录
        self.history = {
            'state': [],
            'control': [],
            'cost': []
        }
    
    def predict(
        self,
        x0: np.ndarray,
        u_sequence: np.ndarray
    ) -> np.ndarray:
        """
        预测未来状态轨迹
        
        Parameters
        ----------
        x0 : np.ndarray
            初始状态
        u_sequence : np.ndarray
            控制序列 (horizon, n_controls)
        
        Returns
        -------
        np.ndarray
            预测状态轨迹 (horizon+1, n_states)
        """
        trajectory = [x0]
        x = x0.copy()
        
        for k in range(self.horizon):
            u = u_sequence[k]
            x_next = self.model(x, u)
            trajectory.append(x_next)
            x = x_next
        
        return np.array(trajectory)
    
    def objective(
        self,
        u_flat: np.ndarray,
        x0: np.ndarray,
        target: np.ndarray
    ) -> float:
        """
        优化目标函数
        
        J = Σ(||x-xref||²_Q + ||u||²_R)
        
        Parameters
        ----------
        u_flat : np.ndarray
            扁平化的控制序列
        x0 : np.ndarray
            初始状态
        target : np.ndarray
            目标状态
        
        Returns
        -------
        float
            目标函数值
        """
        # 重塑控制序列
        u_sequence = u_flat.reshape(self.horizon, self.n_controls)
        
        # 预测轨迹
        trajectory = self.predict(x0, u_sequence)
        
        # 计算代价
        cost = 0.0
        for k in range(self.horizon):
            # 状态误差
            x_error = trajectory[k] - target
            cost += x_error.T @ self.Q @ x_error
            
            # 控制代价
            u = u_sequence[k]
            cost += u.T @ self.R @ u
        
        # 终端代价
        x_terminal = trajectory[-1] - target
        cost += x_terminal.T @ self.Q @ x_terminal
        
        return cost
    
    def compute(
        self,
        x0: np.ndarray,
        target: np.ndarray,
        u_init: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        计算最优控制序列
        
        Parameters
        ----------
        x0 : np.ndarray
            当前状态
        target : np.ndarray
            目标状态
        u_init : np.ndarray, optional
            控制初值
        
        Returns
        -------
        np.ndarray
            最优控制序列 (horizon, n_controls)
        """
        # 初始猜测
        if u_init is None:
            u_init = np.zeros((self.horizon, self.n_controls))
        
        u_flat_init = u_init.flatten()
        
        # 约束
        bounds = []
        if self.control_limits is not None:
            u_min, u_max = self.control_limits
            for _ in range(self.horizon * self.n_controls):
                bounds.append((u_min, u_max))
        else:
            bounds = None
        
        # 优化
        result = minimize(
            fun=self.objective,
            x0=u_flat_init,
            args=(x0, target),
            method='SLSQP',
            bounds=bounds
        )
        
        # 提取最优控制序列
        u_optimal = result.x.reshape(self.horizon, self.n_controls)
        
        # 记录
        self.history['state'].append(x0)
        self.history['control'].append(u_optimal[0])
        self.history['cost'].append(result.fun)
        
        return u_optimal
    
    def step(
        self,
        x0: np.ndarray,
        target: np.ndarray
    ) -> np.ndarray:
        """
        执行一步MPC控制
        
        Parameters
        ----------
        x0 : np.ndarray
            当前状态
        target : np.ndarray
            目标状态
        
        Returns
        -------
        np.ndarray
            当前时刻的最优控制
        """
        u_sequence = self.compute(x0, target)
        return u_sequence[0]  # 只返回第一个控制
    
    def get_predicted_trajectory(
        self,
        x0: np.ndarray,
        u_sequence: np.ndarray
    ) -> Dict:
        """
        获取预测轨迹
        
        Parameters
        ----------
        x0 : np.ndarray
            初始状态
        u_sequence : np.ndarray
            控制序列
        
        Returns
        -------
        Dict
            包含状态和控制轨迹
        """
        trajectory = self.predict(x0, u_sequence)
        
        return {
            'states': trajectory,
            'controls': u_sequence,
            'time': np.arange(len(trajectory)) * self.dt
        }


def linear_mpc_matrices(A: np.ndarray, B: np.ndarray) -> Callable:
    """
    创建线性系统模型
    
    x_{k+1} = A*x_k + B*u_k
    
    Parameters
    ----------
    A : np.ndarray
        状态转移矩阵
    B : np.ndarray
        控制输入矩阵
    
    Returns
    -------
    Callable
        模型函数
    
    Examples
    --------
    >>> A = np.array([[1, 0.1], [0, 1]])
    >>> B = np.array([[0], [0.1]])
    >>> model = linear_mpc_matrices(A, B)
    """
    def model(x, u):
        return A @ x + B @ u
    
    return model
