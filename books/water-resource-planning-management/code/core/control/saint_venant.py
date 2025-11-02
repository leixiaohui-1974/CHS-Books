"""
Saint-Venant方程求解器

明渠非恒定流水力学方程的数值求解
"""

import numpy as np
from typing import Tuple, Optional


class SaintVenantSolver:
    """
    Saint-Venant方程求解器
    
    求解一维明渠非恒定流方程：
    连续方程：∂A/∂t + ∂Q/∂x = 0
    动量方程：∂Q/∂t + ∂(Q²/A)/∂x + gA(∂h/∂x + S_f - S_0) = 0
    
    其中：
    - A: 断面面积
    - Q: 流量
    - h: 水深
    - S_f: 摩阻坡度
    - S_0: 底坡
    
    Examples
    --------
    >>> solver = SaintVenantSolver(
    ...     length=1000,  # 渠道长度(m)
    ...     n_sections=50,  # 断面数
    ...     width=10,  # 渠道宽度(m)
    ...     slope=0.001  # 底坡
    ... )
    >>> 
    >>> # 初始条件
    >>> h_init = np.ones(50) * 2.0  # 初始水深2m
    >>> Q_init = np.ones(50) * 20.0  # 初始流量20m³/s
    >>> 
    >>> # 求解
    >>> h, Q = solver.solve(h_init, Q_init, dt=10, n_steps=100)
    """
    
    def __init__(
        self,
        length: float,
        n_sections: int,
        width: float,
        slope: float,
        manning_n: float = 0.025
    ):
        """
        初始化
        
        Parameters
        ----------
        length : float
            渠道长度 (m)
        n_sections : int
            断面数量
        width : float
            渠道宽度 (m)
        slope : float
            底坡
        manning_n : float
            曼宁粗糙系数
        """
        self.length = length
        self.n_sections = n_sections
        self.width = width
        self.slope = slope
        self.manning_n = manning_n
        
        # 空间离散
        self.dx = length / (n_sections - 1)
        self.x = np.linspace(0, length, n_sections)
    
    def compute_area(self, h: np.ndarray) -> np.ndarray:
        """计算断面面积"""
        return self.width * h
    
    def compute_friction_slope(
        self,
        h: np.ndarray,
        Q: np.ndarray
    ) -> np.ndarray:
        """
        计算摩阻坡度 S_f
        
        曼宁公式：S_f = n²Q²/(A²R^(4/3))
        """
        A = self.compute_area(h)
        R = h  # 矩形断面：水力半径 ≈ 水深
        
        # 避免除零
        A = np.where(A < 1e-6, 1e-6, A)
        R = np.where(R < 1e-6, 1e-6, R)
        
        S_f = (self.manning_n ** 2) * (Q ** 2) / (A ** 2 * R ** (4/3))
        
        return S_f
    
    def solve_step(
        self,
        h: np.ndarray,
        Q: np.ndarray,
        dt: float,
        Q_upstream: Optional[float] = None,
        h_downstream: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        求解一个时间步
        
        使用Lax-Wendroff格式
        
        Parameters
        ----------
        h : np.ndarray
            当前水深
        Q : np.ndarray
            当前流量
        dt : float
            时间步长
        Q_upstream : float, optional
            上游边界流量
        h_downstream : float, optional
            下游边界水深
        
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            (新水深, 新流量)
        """
        n = len(h)
        h_new = h.copy()
        Q_new = Q.copy()
        
        A = self.compute_area(h)
        S_f = self.compute_friction_slope(h, Q)
        
        # 内部断面（Lax-Wendroff）
        for i in range(1, n-1):
            # 连续方程
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)
            h_new[i] = h[i] - dt * dQ_dx / self.width
            
            # 动量方程（简化）
            v = Q[i] / (A[i] + 1e-6)  # 流速
            dv_dx = (Q[i+1]/A[i+1] - Q[i-1]/A[i-1]) / (2 * self.dx)
            dh_dx = (h[i+1] - h[i-1]) / (2 * self.dx)
            
            # 加速度
            dQ_dt = -A[i] * (v * dv_dx + 9.81 * (dh_dx + S_f[i] - self.slope))
            Q_new[i] = Q[i] + dt * dQ_dt
        
        # 上游边界
        if Q_upstream is not None:
            Q_new[0] = Q_upstream
            # 根据连续方程推算水深
            dQ_dx = (Q[1] - Q[0]) / self.dx
            h_new[0] = h[0] - dt * dQ_dx / self.width
        
        # 下游边界
        if h_downstream is not None:
            h_new[-1] = h_downstream
            # 根据动量方程推算流量
            v = Q[-1] / (A[-1] + 1e-6)
            dh_dx = (h[-1] - h[-2]) / self.dx
            Q_new[-1] = Q[-1] - dt * A[-1] * 9.81 * (dh_dx + S_f[-1] - self.slope)
        
        return h_new, Q_new
    
    def solve(
        self,
        h_init: np.ndarray,
        Q_init: np.ndarray,
        dt: float,
        n_steps: int,
        Q_upstream_series: Optional[np.ndarray] = None,
        h_downstream: Optional[float] = None
    ) -> Dict:
        """
        求解Saint-Venant方程
        
        Parameters
        ----------
        h_init : np.ndarray
            初始水深
        Q_init : np.ndarray
            初始流量
        dt : float
            时间步长
        n_steps : int
            时间步数
        Q_upstream_series : np.ndarray, optional
            上游边界流量时间序列
        h_downstream : float, optional
            下游边界水深
        
        Returns
        -------
        Dict
            求解结果
        """
        h = h_init.copy()
        Q = Q_init.copy()
        
        # 历史记录
        h_history = [h.copy()]
        Q_history = [Q.copy()]
        
        for step in range(n_steps):
            # 上游边界
            Q_upstream = None
            if Q_upstream_series is not None:
                Q_upstream = Q_upstream_series[step]
            
            # 求解一步
            h, Q = self.solve_step(h, Q, dt, Q_upstream, h_downstream)
            
            # 记录
            h_history.append(h.copy())
            Q_history.append(Q.copy())
        
        return {
            'h': np.array(h_history),  # (n_steps+1, n_sections)
            'Q': np.array(Q_history),
            'x': self.x,
            't': np.arange(n_steps + 1) * dt
        }
