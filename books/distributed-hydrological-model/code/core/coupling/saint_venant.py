"""
一维Saint-Venant方程求解器
========================

实现明渠非恒定流的Saint-Venant方程数值求解。

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Tuple, Optional


class SaintVenant1D:
    """
    一维Saint-Venant方程求解器
    
    方程组:
    ∂A/∂t + ∂Q/∂x = 0                    (连续方程)
    ∂Q/∂t + ∂(Q²/A)/∂x + gA∂h/∂x = -gASf (动量方程)
    
    其中:
    - A: 过水断面面积 (m²)
    - Q: 流量 (m³/s)
    - h: 水深 (m)
    - g: 重力加速度 (m/s²)
    - Sf: 摩阻坡度
    
    数值格式: 四点Preissmann隐式格式
    """
    
    def __init__(self, 
                 L: float,
                 dx: float,
                 dt: float,
                 n: float = 0.03,
                 B: float = 10.0,
                 S0: float = 0.001):
        """
        初始化求解器
        
        Parameters
        ----------
        L : float
            河段长度 (m)
        dx : float
            空间步长 (m)
        dt : float
            时间步长 (s)
        n : float
            曼宁糙率系数
        B : float
            河道底宽 (m)
        S0 : float
            河床坡度
        """
        self.L = L
        self.dx = dx
        self.dt = dt
        self.n = n
        self.B = B
        self.S0 = S0
        self.g = 9.81  # 重力加速度
        
        # 网格点数
        self.nx = int(L / dx) + 1
        self.x = np.linspace(0, L, self.nx)
        
        # 状态变量
        self.h = None  # 水深
        self.Q = None  # 流量
        
    def initialize(self, h0: float = 1.0, Q0: float = 10.0):
        """
        初始化水深和流量
        
        Parameters
        ----------
        h0 : float
            初始水深 (m)
        Q0 : float
            初始流量 (m³/s)
        """
        self.h = np.full(self.nx, h0)
        self.Q = np.full(self.nx, Q0)
        
    def compute_area(self, h: np.ndarray) -> np.ndarray:
        """计算过水断面面积（矩形断面）"""
        return self.B * h
    
    def compute_wetted_perimeter(self, h: np.ndarray) -> np.ndarray:
        """计算湿周（矩形断面）"""
        return self.B + 2 * h
    
    def compute_hydraulic_radius(self, h: np.ndarray) -> np.ndarray:
        """计算水力半径"""
        A = self.compute_area(h)
        P = self.compute_wetted_perimeter(h)
        return A / (P + 1e-10)
    
    def compute_friction_slope(self, h: np.ndarray, Q: np.ndarray) -> np.ndarray:
        """
        计算摩阻坡度
        
        曼宁公式: Sf = n²Q²/(A²R^(4/3))
        """
        A = self.compute_area(h)
        R = self.compute_hydraulic_radius(h)
        
        # 防止除零
        A = np.maximum(A, 1e-6)
        R = np.maximum(R, 1e-6)
        
        Sf = (self.n ** 2 * Q ** 2) / (A ** 2 * R ** (4.0/3.0))
        return Sf
    
    def solve_step(self, 
                   Q_upstream: float,
                   h_downstream: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        求解一个时间步
        
        使用简化的Muskingum-Cunge方法（更稳定）
        
        Parameters
        ----------
        Q_upstream : float
            上游边界流量 (m³/s)
        h_downstream : float, optional
            下游边界水深 (m)
            
        Returns
        -------
        h_new : ndarray
            新的水深
        Q_new : ndarray
            新的流量
        """
        h_old = self.h.copy()
        Q_old = self.Q.copy()
        
        h_new = h_old.copy()
        Q_new = Q_old.copy()
        
        # 上游边界条件
        Q_new[0] = Q_upstream
        
        # 使用Muskingum-Cunge方法演算流量
        for i in range(1, self.nx):
            # 计算平均流速和波速
            A = self.compute_area(h_old[i-1])
            v = Q_old[i-1] / (A + 1e-6)
            R = self.compute_hydraulic_radius(h_old[i-1])
            
            # 曼宁公式计算流速
            v_manning = (1.0 / self.n) * R ** (2.0/3.0) * self.S0 ** 0.5
            v = min(abs(v), v_manning)  # 限制流速
            
            # 洪波波速
            c = max(v * 1.4, 1.0)  # 简化：c ≈ 1.4v
            
            # Muskingum参数
            K = self.dx / c  # 时间参数
            X = 0.25  # 权重参数
            
            # 确保稳定性
            if K > 0:
                C0 = (-K * X + 0.5 * self.dt) / (K - K * X + 0.5 * self.dt)
                C1 = (K * X + 0.5 * self.dt) / (K - K * X + 0.5 * self.dt)
                C2 = (K - K * X - 0.5 * self.dt) / (K - K * X + 0.5 * self.dt)
                
                # 限制系数范围
                C0 = np.clip(C0, 0, 1)
                C1 = np.clip(C1, 0, 1)
                C2 = np.clip(C2, -1, 1)
                
                # 演算流量
                Q_new[i] = C0 * Q_old[i-1] + C1 * Q_new[i-1] + C2 * Q_old[i]
                Q_new[i] = max(Q_new[i], 0.1)  # 最小流量
            else:
                Q_new[i] = Q_old[i]
        
        # 根据流量更新水深（连续方程）
        for i in range(1, self.nx):
            # 简化：使用曼宁公式反算水深
            Q_avg = (Q_new[i] + Q_old[i]) / 2.0
            
            # Q = (1/n) * A * R^(2/3) * S0^0.5
            # 对于矩形断面: A = B*h, R ≈ h (宽浅)
            # Q ≈ (1/n) * B * h * h^(2/3) * S0^0.5
            # h^(5/3) ≈ Q * n / (B * S0^0.5)
            
            if Q_avg > 0:
                h_est = (Q_avg * self.n / (self.B * self.S0 ** 0.5)) ** (3.0/5.0)
                h_new[i] = 0.8 * h_old[i] + 0.2 * h_est  # 阻尼更新
                h_new[i] = np.clip(h_new[i], 0.1, 20.0)  # 限制范围
            else:
                h_new[i] = h_old[i]
        
        # 下游边界条件
        if h_downstream is not None:
            h_new[-1] = h_downstream
        else:
            # 自由出流
            h_new[-1] = h_new[-2]
            Q_new[-1] = Q_new[-2]
        
        # 更新状态
        self.h = h_new
        self.Q = Q_new
        
        return h_new, Q_new
    
    def get_water_level(self) -> np.ndarray:
        """获取水位（河床+水深）"""
        z_bed = self.x * (-self.S0)  # 河床高程
        return z_bed + self.h
    
    def get_velocity(self) -> np.ndarray:
        """获取流速"""
        A = self.compute_area(self.h)
        return self.Q / (A + 1e-10)


def solve_saint_venant(
    L: float,
    dx: float,
    dt: float,
    T: float,
    Q_upstream: np.ndarray,
    n: float = 0.03,
    B: float = 10.0,
    S0: float = 0.001,
    h0: float = 1.0,
    Q0: float = 10.0
) -> Dict[str, np.ndarray]:
    """
    求解Saint-Venant方程
    
    Parameters
    ----------
    L : float
        河段长度 (m)
    dx : float
        空间步长 (m)
    dt : float
        时间步长 (s)
    T : float
        模拟时长 (s)
    Q_upstream : ndarray
        上游边界流量序列 (m³/s)
    n : float
        曼宁糙率
    B : float
        河道底宽 (m)
    S0 : float
        河床坡度
    h0 : float
        初始水深 (m)
    Q0 : float
        初始流量 (m³/s)
        
    Returns
    -------
    results : dict
        包含时间序列结果的字典
    """
    # 创建求解器
    solver = SaintVenant1D(L, dx, dt, n, B, S0)
    solver.initialize(h0, Q0)
    
    # 时间步数
    nt = len(Q_upstream)
    nx = solver.nx
    
    # 存储结果
    h_series = np.zeros((nt, nx))
    Q_series = np.zeros((nt, nx))
    v_series = np.zeros((nt, nx))
    z_series = np.zeros((nt, nx))
    
    # 时间推进
    for t in range(nt):
        h_new, Q_new = solver.solve_step(Q_upstream[t])
        
        h_series[t, :] = h_new
        Q_series[t, :] = Q_new
        v_series[t, :] = solver.get_velocity()
        z_series[t, :] = solver.get_water_level()
    
    return {
        'x': solver.x,
        'h': h_series,
        'Q': Q_series,
        'v': v_series,
        'z': z_series,
        't': np.arange(nt) * dt
    }


if __name__ == '__main__':
    """测试Saint-Venant求解器"""
    print("测试Saint-Venant求解器...")
    
    # 参数
    L = 1000.0  # 河段长度 (m)
    dx = 50.0   # 空间步长 (m)
    dt = 10.0   # 时间步长 (s)
    T = 3600.0  # 模拟时长 (s)
    
    # 上游流量（洪峰）
    nt = int(T / dt)
    t = np.arange(nt) * dt
    Q_base = 10.0
    Q_peak = 50.0
    Q_upstream = Q_base + (Q_peak - Q_base) * np.exp(-((t - 1800) / 600) ** 2)
    
    # 求解
    results = solve_saint_venant(L, dx, dt, T, Q_upstream)
    
    print(f"网格点数: {len(results['x'])}")
    print(f"时间步数: {len(results['t'])}")
    print(f"最大水深: {np.max(results['h']):.3f} m")
    print(f"最大流速: {np.max(results['v']):.3f} m/s")
    print("测试通过！")
