"""
多目标优化算法

NSGA-II (Non-dominated Sorting Genetic Algorithm II)
"""

import numpy as np
from typing import Callable, List, Tuple, Dict, Optional


class NSGAII:
    """
    NSGA-II多目标遗传算法
    
    特点：
    - 快速非支配排序
    - 拥挤度计算
    - 精英策略
    
    Examples
    --------
    >>> # 双目标优化：最小化f1(x)和f2(x)
    >>> def objectives(x):
    ...     f1 = x[0]**2 + x[1]**2
    ...     f2 = (x[0]-1)**2 + (x[1]-1)**2
    ...     return [f1, f2]
    >>> 
    >>> nsga2 = NSGAII(
    ...     pop_size=50,
    ...     n_vars=2,
    ...     n_objs=2,
    ...     bounds=[(-5, 5), (-5, 5)]
    ... )
    >>> pareto_front = nsga2.optimize(objectives, n_generations=100)
    """
    
    def __init__(
        self,
        pop_size: int,
        n_vars: int,
        n_objs: int,
        bounds: List[Tuple[float, float]],
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1
    ):
        """
        初始化
        
        Parameters
        ----------
        pop_size : int
            种群大小（必须为偶数）
        n_vars : int
            决策变量数量
        n_objs : int
            目标函数数量
        bounds : List[Tuple[float, float]]
            变量边界
        crossover_rate : float
            交叉概率
        mutation_rate : float
            变异概率
        """
        if pop_size % 2 != 0:
            pop_size += 1
        
        self.pop_size = pop_size
        self.n_vars = n_vars
        self.n_objs = n_objs
        self.bounds = np.array(bounds)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.population = None
        self.objectives = None
    
    def initialize_population(self):
        """初始化种群"""
        self.population = np.random.uniform(
            low=self.bounds[:, 0],
            high=self.bounds[:, 1],
            size=(self.pop_size, self.n_vars)
        )
    
    def evaluate(self, objective_funcs: Callable):
        """
        评估目标函数
        
        Parameters
        ----------
        objective_funcs : Callable
            目标函数（返回列表）
        """
        self.objectives = np.array([objective_funcs(ind) for ind in self.population])
    
    def fast_non_dominated_sort(self) -> List[List[int]]:
        """
        快速非支配排序
        
        Returns
        -------
        List[List[int]]
            各层级的个体索引
        """
        n = len(self.population)
        
        # 支配关系
        domination_count = np.zeros(n, dtype=int)  # 被支配次数
        dominated_solutions = [[] for _ in range(n)]  # 支配的解
        
        fronts = [[]]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                # 判断i是否支配j
                if self._dominates(i, j):
                    dominated_solutions[i].append(j)
                elif self._dominates(j, i):
                    domination_count[i] += 1
            
            if domination_count[i] == 0:
                fronts[0].append(i)
        
        # 后续层级
        i = 0
        while fronts[i]:
            next_front = []
            for p in fronts[i]:
                for q in dominated_solutions[p]:
                    domination_count[q] -= 1
                    if domination_count[q] == 0:
                        next_front.append(q)
            i += 1
            if next_front:
                fronts.append(next_front)
        
        return fronts[:-1]  # 去掉最后的空列表
    
    def _dominates(self, i: int, j: int) -> bool:
        """
        判断i是否支配j（最小化问题）
        
        Parameters
        ----------
        i, j : int
            个体索引
        
        Returns
        -------
        bool
            是否支配
        """
        better_in_all = True
        strictly_better_in_one = False
        
        for k in range(self.n_objs):
            if self.objectives[i, k] > self.objectives[j, k]:
                better_in_all = False
                break
            if self.objectives[i, k] < self.objectives[j, k]:
                strictly_better_in_one = True
        
        return better_in_all and strictly_better_in_one
    
    def crowding_distance(self, front: List[int]) -> np.ndarray:
        """
        计算拥挤度距离
        
        Parameters
        ----------
        front : List[int]
            层级中的个体索引
        
        Returns
        -------
        np.ndarray
            拥挤度距离
        """
        n = len(front)
        if n == 0:
            return np.array([])
        
        distances = np.zeros(n)
        
        for m in range(self.n_objs):
            # 按第m个目标排序
            sorted_indices = np.argsort(self.objectives[front, m])
            
            # 边界点设为无穷大
            distances[sorted_indices[0]] = np.inf
            distances[sorted_indices[-1]] = np.inf
            
            # 归一化范围
            obj_range = self.objectives[front[sorted_indices[-1]], m] - \
                       self.objectives[front[sorted_indices[0]], m]
            
            if obj_range == 0:
                continue
            
            # 中间点的拥挤度
            for i in range(1, n - 1):
                distances[sorted_indices[i]] += \
                    (self.objectives[front[sorted_indices[i+1]], m] - \
                     self.objectives[front[sorted_indices[i-1]], m]) / obj_range
        
        return distances
    
    def selection(self, fronts: List[List[int]]) -> np.ndarray:
        """
        选择下一代种群
        
        Parameters
        ----------
        fronts : List[List[int]]
            非支配层级
        
        Returns
        -------
        np.ndarray
            选中的个体索引
        """
        selected = []
        
        for front in fronts:
            if len(selected) + len(front) <= self.pop_size:
                selected.extend(front)
            else:
                # 计算拥挤度
                distances = self.crowding_distance(front)
                # 按拥挤度降序排序
                sorted_indices = np.argsort(-distances)
                remaining = self.pop_size - len(selected)
                selected.extend([front[i] for i in sorted_indices[:remaining]])
                break
        
        return np.array(selected)
    
    def crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """模拟二进制交叉（SBX）"""
        if np.random.rand() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1 = np.zeros(self.n_vars)
        child2 = np.zeros(self.n_vars)
        
        eta = 20  # 分布指数
        
        for i in range(self.n_vars):
            if np.random.rand() <= 0.5:
                if abs(parent1[i] - parent2[i]) > 1e-10:
                    beta = 1.0 + (2.0 * (parent1[i] - self.bounds[i, 0]) / (parent2[i] - parent1[i]))
                    alpha = 2.0 - beta ** (-(eta + 1.0))
                    
                    u = np.random.rand()
                    if u <= 1.0 / alpha:
                        betaq = (u * alpha) ** (1.0 / (eta + 1.0))
                    else:
                        betaq = (1.0 / (2.0 - u * alpha)) ** (1.0 / (eta + 1.0))
                    
                    child1[i] = 0.5 * ((parent1[i] + parent2[i]) - betaq * (parent2[i] - parent1[i]))
                    child2[i] = 0.5 * ((parent1[i] + parent2[i]) + betaq * (parent2[i] - parent1[i]))
                else:
                    child1[i] = parent1[i]
                    child2[i] = parent2[i]
                
                # 边界处理
                child1[i] = np.clip(child1[i], self.bounds[i, 0], self.bounds[i, 1])
                child2[i] = np.clip(child2[i], self.bounds[i, 0], self.bounds[i, 1])
            else:
                child1[i] = parent1[i]
                child2[i] = parent2[i]
        
        return child1, child2
    
    def mutation(self, individual: np.ndarray) -> np.ndarray:
        """多项式变异"""
        eta = 20
        
        for i in range(self.n_vars):
            if np.random.rand() < self.mutation_rate:
                delta = (self.bounds[i, 1] - self.bounds[i, 0])
                u = np.random.rand()
                
                if u < 0.5:
                    deltaq = (2.0 * u) ** (1.0 / (eta + 1.0)) - 1.0
                else:
                    deltaq = 1.0 - (2.0 * (1.0 - u)) ** (1.0 / (eta + 1.0))
                
                individual[i] = individual[i] + deltaq * delta
                individual[i] = np.clip(individual[i], self.bounds[i, 0], self.bounds[i, 1])
        
        return individual
    
    def optimize(
        self,
        objective_funcs: Callable,
        n_generations: int = 100,
        verbose: bool = False
    ) -> Dict:
        """
        运行NSGA-II
        
        Parameters
        ----------
        objective_funcs : Callable
            目标函数（返回列表）
        n_generations : int
            进化代数
        verbose : bool
            是否输出进度
        
        Returns
        -------
        Dict
            优化结果，包含Pareto前沿
        """
        # 初始化
        self.initialize_population()
        self.evaluate(objective_funcs)
        
        for gen in range(n_generations):
            if verbose and gen % 10 == 0:
                print(f"代数 {gen}")
            
            # 生成子代
            offspring = []
            for _ in range(self.pop_size // 2):
                # 随机选择父代
                parent1 = self.population[np.random.randint(self.pop_size)]
                parent2 = self.population[np.random.randint(self.pop_size)]
                
                # 交叉
                child1, child2 = self.crossover(parent1, parent2)
                
                # 变异
                child1 = self.mutation(child1)
                child2 = self.mutation(child2)
                
                offspring.extend([child1, child2])
            
            offspring = np.array(offspring)
            
            # 合并父代和子代
            combined_pop = np.vstack([self.population, offspring])
            self.population = combined_pop
            self.evaluate(objective_funcs)
            
            # 非支配排序
            fronts = self.fast_non_dominated_sort()
            
            # 选择
            selected_indices = self.selection(fronts)
            self.population = self.population[selected_indices]
            self.objectives = self.objectives[selected_indices]
        
        # 最终非支配排序
        fronts = self.fast_non_dominated_sort()
        pareto_front_indices = fronts[0]
        
        return {
            'pareto_solutions': self.population[pareto_front_indices],
            'pareto_objectives': self.objectives[pareto_front_indices],
            'all_solutions': self.population,
            'all_objectives': self.objectives
        }
