"""
观测系统模块

定义地下水监测井和观测系统，用于生成模拟观测数据。

在实际应用中，观测系统包括：
- 监测井位置
- 观测频率
- 观测误差（仪器精度、人为误差等）
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ObservationWell:
    """
    监测井
    
    Attributes
    ----------
    x : float
        井位x坐标
    y : float
        井位y坐标
    noise_std : float
        观测噪声标准差（m）
    name : str
        井名
    """
    x: float
    y: float
    noise_std: float = 0.1
    name: Optional[str] = None
    
    def __post_init__(self):
        if self.name is None:
            self.name = f"Well({self.x:.1f}, {self.y:.1f})"


class ObservationSystem:
    """
    观测系统
    
    管理多个监测井，生成观测数据。
    
    Parameters
    ----------
    nx : int
        网格x方向节点数
    ny : int
        网格y方向节点数
    dx : float
        网格x方向间距
    dy : float
        网格y方向间距
    
    Attributes
    ----------
    wells : List[ObservationWell]
        监测井列表
    n_wells : int
        监测井数量
    
    Examples
    --------
    >>> obs_sys = ObservationSystem(nx=50, ny=50, dx=100, dy=100)
    >>> obs_sys.add_well(2500, 2500, noise_std=0.05, name="MW-1")
    >>> obs_sys.add_well(3500, 3500, noise_std=0.08, name="MW-2")
    >>> true_state = np.ones((50, 50)) * 10.0
    >>> observations = obs_sys.generate_observations(true_state)
    """
    
    def __init__(
        self,
        nx: int,
        ny: int,
        dx: float,
        dy: float
    ):
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.dy = dy
        self.wells: List[ObservationWell] = []
    
    @property
    def n_wells(self) -> int:
        """监测井数量"""
        return len(self.wells)
    
    def add_well(
        self,
        x: float,
        y: float,
        noise_std: float = 0.1,
        name: Optional[str] = None
    ) -> None:
        """
        添加监测井
        
        Parameters
        ----------
        x : float
            井位x坐标
        y : float
            井位y坐标
        noise_std : float
            观测噪声标准差
        name : str, optional
            井名
        """
        well = ObservationWell(x=x, y=y, noise_std=noise_std, name=name)
        self.wells.append(well)
    
    def get_well_indices(self) -> List[Tuple[int, int]]:
        """
        获取监测井在网格中的索引
        
        Returns
        -------
        indices : List[Tuple[int, int]]
            井位索引列表 [(i1, j1), (i2, j2), ...]
        """
        indices = []
        for well in self.wells:
            i = int(well.y / self.dy)
            j = int(well.x / self.dx)
            # 确保索引在有效范围内
            i = max(0, min(i, self.ny - 1))
            j = max(0, min(j, self.nx - 1))
            indices.append((i, j))
        return indices
    
    def generate_observations(
        self,
        true_state: np.ndarray,
        add_noise: bool = True
    ) -> np.ndarray:
        """
        生成观测数据
        
        Parameters
        ----------
        true_state : np.ndarray
            真实状态场 (ny × nx)
        add_noise : bool
            是否添加观测噪声
        
        Returns
        -------
        observations : np.ndarray
            观测数据 (n_wells,)
        """
        indices = self.get_well_indices()
        observations = np.zeros(self.n_wells)
        
        for idx, (i, j) in enumerate(indices):
            obs = true_state[i, j]
            if add_noise:
                obs += np.random.normal(0, self.wells[idx].noise_std)
            observations[idx] = obs
        
        return observations
    
    def get_observation_matrix(self) -> np.ndarray:
        """
        构建观测矩阵H
        
        H将状态向量（展平的二维场）映射到观测向量。
        
        Returns
        -------
        H : np.ndarray
            观测矩阵 (n_wells × (nx*ny))
        """
        indices = self.get_well_indices()
        n_states = self.nx * self.ny
        H = np.zeros((self.n_wells, n_states))
        
        for idx, (i, j) in enumerate(indices):
            # 将2D索引转换为1D索引（行优先）
            state_idx = i * self.nx + j
            H[idx, state_idx] = 1.0
        
        return H
    
    def get_observation_covariance(self) -> np.ndarray:
        """
        获取观测噪声协方差矩阵R
        
        假设各井观测误差独立。
        
        Returns
        -------
        R : np.ndarray
            观测噪声协方差矩阵 (n_wells × n_wells)
        """
        variances = np.array([well.noise_std ** 2 for well in self.wells])
        R = np.diag(variances)
        return R
    
    def plot_well_locations(self, ax=None):
        """
        绘制监测井位置
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            绘图坐标轴
        
        Returns
        -------
        ax : matplotlib.axes.Axes
            坐标轴对象
        """
        import matplotlib.pyplot as plt
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        # 绘制网格边界
        Lx = self.nx * self.dx
        Ly = self.ny * self.dy
        ax.add_patch(plt.Rectangle((0, 0), Lx, Ly, 
                                   fill=False, edgecolor='gray', linewidth=2))
        
        # 绘制监测井
        for well in self.wells:
            ax.plot(well.x, well.y, 'ro', markersize=10, 
                   markeredgecolor='darkred', markeredgewidth=2)
            ax.text(well.x, well.y + 200, well.name, 
                   ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_title('监测井布置')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        return ax


def state_to_observations(
    state: np.ndarray,
    H: np.ndarray
) -> np.ndarray:
    """
    将状态场映射到观测值
    
    Parameters
    ----------
    state : np.ndarray
        状态向量 (展平的场)
    H : np.ndarray
        观测矩阵
    
    Returns
    -------
    observations : np.ndarray
        观测值
    """
    return H @ state


def compute_innovation(
    observations: np.ndarray,
    predicted_observations: np.ndarray
) -> np.ndarray:
    """
    计算创新（观测残差）
    
    Parameters
    ----------
    observations : np.ndarray
        实际观测值
    predicted_observations : np.ndarray
        模型预测的观测值
    
    Returns
    -------
    innovation : np.ndarray
        创新 = 观测 - 预测
    """
    return observations - predicted_observations


def compute_observation_likelihood(
    innovation: np.ndarray,
    R: np.ndarray
) -> float:
    """
    计算观测似然（对数似然）
    
    假设观测误差服从高斯分布。
    
    Parameters
    ----------
    innovation : np.ndarray
        创新向量
    R : np.ndarray
        观测噪声协方差
    
    Returns
    -------
    log_likelihood : float
        对数似然值
    """
    n = len(innovation)
    R_inv = np.linalg.inv(R)
    det_R = np.linalg.det(R)
    
    # 对数似然 = -0.5 * [n*log(2π) + log|R| + ν^T R^{-1} ν]
    log_likelihood = -0.5 * (
        n * np.log(2 * np.pi) +
        np.log(det_R) +
        innovation.T @ R_inv @ innovation
    )
    
    return log_likelihood
