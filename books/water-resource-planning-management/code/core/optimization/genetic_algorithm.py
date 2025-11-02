"""
遗传算法 (Genetic Algorithm)

用于求解复杂优化问题
"""

import numpy as np
from typing import Callable, Tuple, Optional, Dict, List


class GeneticAlgorithm:
    """
    遗传算法优化器
    
    基本流程：
    1. 初始化种群
    2. 评估适应度
    3. 选择
    4. 交叉
    5. 变异
    6. 重复2-5直到收敛
    
    Examples
    --------
    >>> # 优化函数 f(x,y) = -(x^2 + y^2)
    >>> def objective(x):
    ...     return -(x[0]**2 + x[1]**2)
    >>> 
    >>> ga = GeneticAlgorithm(
    ...     pop_size=50,
    ...     n_genes=2,
    ...     bounds=[(-5, 5), (-5, 5)]
    ... )
    >>> best_x, best_f = ga.optimize(objective, n_generations=100)
    """
    
    def __init__(
        self,
        pop_size: int,
        n_genes: int,
        bounds: List[Tuple[float, float]],
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elite_size: int = 2,
        tournament_size: int = 3
    ):
        """
        初始化
        
        Parameters
        ----------
        pop_size : int
            种群大小
        n_genes : int
            基因数量（决策变量维度）
        bounds : List[Tuple[float, float]]
            变量边界
        crossover_rate : float
            交叉概率
        mutation_rate : float
            变异概率
        elite_size : int
            精英个体数量
        tournament_size : int
            锦标赛选择大小
        """
        self.pop_size = pop_size
        self.n_genes = n_genes
        self.bounds = np.array(bounds)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        
        self.population = None
        self.fitness = None
        self.best_solution = None
        self.best_fitness = None
        self.history = {'best': [], 'mean': []}
    
    def initialize_population(self):
        """初始化种群"""
        self.population = np.random.uniform(
            low=self.bounds[:, 0],
            high=self.bounds[:, 1],
            size=(self.pop_size, self.n_genes)
        )
    
    def evaluate(self, objective_func: Callable):
        """
        评估种群适应度
        
        Parameters
        ----------
        objective_func : Callable
            目标函数（最大化）
        """
        self.fitness = np.array([objective_func(ind) for ind in self.population])
        
        # 更新最优解
        best_idx = np.argmax(self.fitness)
        if self.best_fitness is None or self.fitness[best_idx] > self.best_fitness:
            self.best_fitness = self.fitness[best_idx]
            self.best_solution = self.population[best_idx].copy()
    
    def selection(self) -> np.ndarray:
        """
        锦标赛选择
        
        Returns
        -------
        np.ndarray
            选中的个体
        """
        indices = np.random.choice(self.pop_size, self.tournament_size, replace=False)
        tournament_fitness = self.fitness[indices]
        winner_idx = indices[np.argmax(tournament_fitness)]
        return self.population[winner_idx].copy()
    
    def crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        单点交叉
        
        Parameters
        ----------
        parent1, parent2 : np.ndarray
            父代个体
        
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            子代个体
        """
        if np.random.rand() < self.crossover_rate:
            point = np.random.randint(1, self.n_genes)
            child1 = np.concatenate([parent1[:point], parent2[point:]])
            child2 = np.concatenate([parent2[:point], parent1[point:]])
            return child1, child2
        else:
            return parent1.copy(), parent2.copy()
    
    def mutation(self, individual: np.ndarray) -> np.ndarray:
        """
        高斯变异
        
        Parameters
        ----------
        individual : np.ndarray
            个体
        
        Returns
        -------
        np.ndarray
            变异后的个体
        """
        for i in range(self.n_genes):
            if np.random.rand() < self.mutation_rate:
                # 高斯变异
                sigma = 0.1 * (self.bounds[i, 1] - self.bounds[i, 0])
                individual[i] += np.random.normal(0, sigma)
                # 边界处理
                individual[i] = np.clip(individual[i], self.bounds[i, 0], self.bounds[i, 1])
        
        return individual
    
    def optimize(
        self,
        objective_func: Callable,
        n_generations: int = 100,
        verbose: bool = False
    ) -> Tuple[np.ndarray, float]:
        """
        运行遗传算法
        
        Parameters
        ----------
        objective_func : Callable
            目标函数（最大化）
        n_generations : int
            进化代数
        verbose : bool
            是否输出进度
        
        Returns
        -------
        Tuple[np.ndarray, float]
            (最优解, 最优值)
        """
        # 初始化
        self.initialize_population()
        self.evaluate(objective_func)
        
        for gen in range(n_generations):
            # 记录历史
            self.history['best'].append(self.best_fitness)
            self.history['mean'].append(np.mean(self.fitness))
            
            if verbose and gen % 10 == 0:
                print(f"代数 {gen}: 最优={self.best_fitness:.4f}, 平均={np.mean(self.fitness):.4f}")
            
            # 新种群
            new_population = []
            
            # 精英保留
            elite_indices = np.argsort(self.fitness)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(self.population[idx].copy())
            
            # 生成子代
            while len(new_population) < self.pop_size:
                # 选择
                parent1 = self.selection()
                parent2 = self.selection()
                
                # 交叉
                child1, child2 = self.crossover(parent1, parent2)
                
                # 变异
                child1 = self.mutation(child1)
                child2 = self.mutation(child2)
                
                new_population.extend([child1, child2])
            
            # 更新种群
            self.population = np.array(new_population[:self.pop_size])
            
            # 评估
            self.evaluate(objective_func)
        
        return self.best_solution, self.best_fitness
    
    def get_history(self) -> Dict:
        """
        获取优化历史
        
        Returns
        -------
        Dict
            历史数据
        """
        return self.history
