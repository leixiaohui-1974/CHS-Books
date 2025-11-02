"""
粒子群优化算法 (Particle Swarm Optimization)

受鸟群觅食行为启发的群智能优化算法
"""

import numpy as np
from typing import Callable, Tuple, List, Dict, Optional


class ParticleSwarmOptimization:
    """
    粒子群优化算法
    
    基本思想：
    - 每个粒子代表一个解
    - 粒子根据自身经验和群体经验调整速度和位置
    - 全局最优解由所有粒子共享
    
    Examples
    --------
    >>> # 最小化函数 f(x,y) = x^2 + y^2
    >>> def objective(x):
    ...     return x[0]**2 + x[1]**2
    >>> 
    >>> pso = ParticleSwarmOptimization(
    ...     n_particles=30,
    ...     n_dims=2,
    ...     bounds=[(-5, 5), (-5, 5)]
    ... )
    >>> best_x, best_f = pso.optimize(objective, n_iterations=100, minimize=True)
    """
    
    def __init__(
        self,
        n_particles: int,
        n_dims: int,
        bounds: List[Tuple[float, float]],
        w: float = 0.7,
        c1: float = 1.5,
        c2: float = 1.5,
        v_max: Optional[float] = None
    ):
        """
        初始化
        
        Parameters
        ----------
        n_particles : int
            粒子数量
        n_dims : int
            问题维度
        bounds : List[Tuple[float, float]]
            变量边界
        w : float
            惯性权重
        c1 : float
            个体学习因子
        c2 : float
            社会学习因子
        v_max : float, optional
            最大速度限制
        """
        self.n_particles = n_particles
        self.n_dims = n_dims
        self.bounds = np.array(bounds)
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        # 最大速度
        if v_max is None:
            self.v_max = 0.2 * (self.bounds[:, 1] - self.bounds[:, 0])
        else:
            self.v_max = v_max
        
        # 粒子状态
        self.positions = None
        self.velocities = None
        self.pbest_positions = None  # 个体最优位置
        self.pbest_values = None     # 个体最优值
        self.gbest_position = None   # 全局最优位置
        self.gbest_value = None      # 全局最优值
        
        self.history = {'best': [], 'mean': []}
    
    def initialize(self):
        """初始化粒子群"""
        # 随机初始化位置
        self.positions = np.random.uniform(
            low=self.bounds[:, 0],
            high=self.bounds[:, 1],
            size=(self.n_particles, self.n_dims)
        )
        
        # 随机初始化速度
        self.velocities = np.random.uniform(
            low=-self.v_max,
            high=self.v_max,
            size=(self.n_particles, self.n_dims)
        )
        
        # 初始化个体最优
        self.pbest_positions = self.positions.copy()
        self.pbest_values = np.full(self.n_particles, np.inf)
        
        # 初始化全局最优
        self.gbest_position = None
        self.gbest_value = np.inf
    
    def evaluate(self, objective_func: Callable, minimize: bool = True):
        """
        评估粒子适应度
        
        Parameters
        ----------
        objective_func : Callable
            目标函数
        minimize : bool
            是否为最小化问题
        """
        for i in range(self.n_particles):
            # 计算目标函数值
            value = objective_func(self.positions[i])
            
            # 更新个体最优
            if minimize:
                if value < self.pbest_values[i]:
                    self.pbest_values[i] = value
                    self.pbest_positions[i] = self.positions[i].copy()
                
                # 更新全局最优
                if value < self.gbest_value:
                    self.gbest_value = value
                    self.gbest_position = self.positions[i].copy()
            else:
                if value > self.pbest_values[i]:
                    self.pbest_values[i] = value
                    self.pbest_positions[i] = self.positions[i].copy()
                
                if value > self.gbest_value:
                    self.gbest_value = value
                    self.gbest_position = self.positions[i].copy()
    
    def update(self):
        """更新粒子位置和速度"""
        r1 = np.random.rand(self.n_particles, self.n_dims)
        r2 = np.random.rand(self.n_particles, self.n_dims)
        
        # 更新速度
        self.velocities = (
            self.w * self.velocities +
            self.c1 * r1 * (self.pbest_positions - self.positions) +
            self.c2 * r2 * (self.gbest_position - self.positions)
        )
        
        # 速度限制
        self.velocities = np.clip(self.velocities, -self.v_max, self.v_max)
        
        # 更新位置
        self.positions = self.positions + self.velocities
        
        # 边界处理
        for d in range(self.n_dims):
            self.positions[:, d] = np.clip(
                self.positions[:, d],
                self.bounds[d, 0],
                self.bounds[d, 1]
            )
    
    def optimize(
        self,
        objective_func: Callable,
        n_iterations: int = 100,
        minimize: bool = True,
        verbose: bool = False
    ) -> Tuple[np.ndarray, float]:
        """
        运行PSO优化
        
        Parameters
        ----------
        objective_func : Callable
            目标函数
        n_iterations : int
            迭代次数
        minimize : bool
            是否为最小化问题
        verbose : bool
            是否输出进度
        
        Returns
        -------
        Tuple[np.ndarray, float]
            (最优解, 最优值)
        """
        # 初始化
        self.initialize()
        self.evaluate(objective_func, minimize)
        
        for iter in range(n_iterations):
            # 记录历史
            self.history['best'].append(self.gbest_value)
            self.history['mean'].append(np.mean(self.pbest_values))
            
            if verbose and iter % 10 == 0:
                print(f"迭代 {iter}: 最优={self.gbest_value:.4f}, 平均={np.mean(self.pbest_values):.4f}")
            
            # 更新
            self.update()
            
            # 评估
            self.evaluate(objective_func, minimize)
        
        return self.gbest_position, self.gbest_value
    
    def get_history(self) -> Dict:
        """
        获取优化历史
        
        Returns
        -------
        Dict
            历史数据
        """
        return self.history


# 便捷别名
PSO = ParticleSwarmOptimization
