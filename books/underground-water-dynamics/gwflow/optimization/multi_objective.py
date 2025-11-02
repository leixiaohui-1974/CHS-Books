"""
多目标优化模块

实现多种多目标优化方法，包括：
- 加权和法 (Weighted Sum Method)
- ε-约束法 (Epsilon-Constraint Method)
- 帕累托前沿分析 (Pareto Front Analysis)
- NSGA-II简化版 (Non-dominated Sorting Genetic Algorithm II)

多目标优化问题形式:
----------------
minimize/maximize [f1(x), f2(x), ..., fm(x)]
subject to:
    gi(x) ≤ 0,  i = 1,...,p
    hj(x) = 0,  j = 1,...,q
    x_min ≤ x ≤ x_max

关键概念:
-------
1. 帕累托最优 (Pareto Optimality):
   解x*是帕累托最优的，当且仅当不存在其他解x，使得：
   - fi(x) ≤ fi(x*) 对所有i成立
   - 至少存在一个j使得 fj(x) < fj(x*)

2. 帕累托前沿 (Pareto Front):
   所有帕累托最优解在目标空间的集合
"""

import numpy as np
from typing import List, Tuple, Callable, Optional, Dict
from scipy.optimize import minimize, differential_evolution


def weighted_sum_method(
    objectives: List[Callable],
    weights: np.ndarray,
    x0: np.ndarray,
    bounds: List[Tuple[float, float]],
    constraints: Optional[List] = None,
    method: str = 'SLSQP'
) -> Dict:
    """
    加权和法
    
    将多目标问题转化为单目标问题：
    minimize Σ wi·fi(x)
    
    Parameters
    ----------
    objectives : List[Callable]
        目标函数列表，每个函数接受x返回标量
    weights : np.ndarray
        权重向量 (Σ wi = 1, wi ≥ 0)
    x0 : np.ndarray
        初始解
    bounds : List[Tuple]
        变量边界
    constraints : List, optional
        约束条件（scipy格式）
    method : str
        优化方法
    
    Returns
    -------
    result : Dict
        优化结果
        - x: 最优解
        - objectives: 各目标函数值
        - weighted_sum: 加权和
        - success: 是否成功
    """
    # 归一化权重
    weights = np.array(weights)
    weights = weights / np.sum(weights)
    
    def weighted_objective(x):
        """加权目标函数"""
        obj_values = np.array([f(x) for f in objectives])
        return np.dot(weights, obj_values)
    
    # 优化
    res = minimize(
        weighted_objective,
        x0,
        method=method,
        bounds=bounds,
        constraints=constraints if constraints else ()
    )
    
    # 计算各目标值
    obj_values = np.array([f(res.x) for f in objectives])
    
    result = {
        'x': res.x,
        'objectives': obj_values,
        'weighted_sum': res.fun,
        'success': res.success,
        'message': res.message,
        'weights': weights
    }
    
    return result


def epsilon_constraint_method(
    primary_objective: Callable,
    secondary_objectives: List[Callable],
    epsilons: np.ndarray,
    x0: np.ndarray,
    bounds: List[Tuple[float, float]],
    base_constraints: Optional[List] = None,
    method: str = 'SLSQP'
) -> Dict:
    """
    ε-约束法
    
    优化一个主目标，将其他目标转化为约束：
    minimize f1(x)
    subject to: fi(x) ≤ εi, i = 2,...,m
    
    Parameters
    ----------
    primary_objective : Callable
        主目标函数
    secondary_objectives : List[Callable]
        次要目标函数列表
    epsilons : np.ndarray
        ε约束值
    x0 : np.ndarray
        初始解
    bounds : List[Tuple]
        变量边界
    base_constraints : List, optional
        基础约束
    method : str
        优化方法
    
    Returns
    -------
    result : Dict
        优化结果
    """
    from scipy.optimize import NonlinearConstraint
    
    # 构建约束
    constraints = [] if base_constraints is None else list(base_constraints)
    
    for i, (f, eps) in enumerate(zip(secondary_objectives, epsilons)):
        # fi(x) ≤ εi  =>  εi - fi(x) ≥ 0
        constraint = NonlinearConstraint(
            lambda x, f=f, eps=eps: eps - f(x),
            lb=0,
            ub=np.inf
        )
        constraints.append(constraint)
    
    # 优化
    res = minimize(
        primary_objective,
        x0,
        method=method,
        bounds=bounds,
        constraints=constraints
    )
    
    # 计算所有目标值
    all_objectives = [primary_objective] + secondary_objectives
    obj_values = np.array([f(res.x) for f in all_objectives])
    
    result = {
        'x': res.x,
        'objectives': obj_values,
        'primary_value': res.fun,
        'success': res.success,
        'epsilons': epsilons
    }
    
    return result


def is_pareto_dominated(solution1: np.ndarray, solution2: np.ndarray) -> bool:
    """
    判断solution1是否被solution2支配
    
    假设最小化所有目标。
    
    Parameters
    ----------
    solution1 : np.ndarray
        解1的目标值
    solution2 : np.ndarray
        解2的目标值
    
    Returns
    -------
    dominated : bool
        True如果solution1被solution2支配
    """
    # solution2至少在一个目标上更好，且在所有目标上不更差
    better = np.any(solution2 < solution1)
    not_worse = np.all(solution2 <= solution1)
    return better and not_worse


def identify_pareto_front(
    solutions: np.ndarray,
    objectives: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    识别帕累托前沿
    
    Parameters
    ----------
    solutions : np.ndarray
        解集合 (n_solutions × n_vars)
    objectives : np.ndarray
        目标值 (n_solutions × n_objectives)
    
    Returns
    -------
    pareto_solutions : np.ndarray
        帕累托最优解
    pareto_objectives : np.ndarray
        帕累托前沿点
    """
    n_solutions = objectives.shape[0]
    is_pareto = np.ones(n_solutions, dtype=bool)
    
    for i in range(n_solutions):
        for j in range(n_solutions):
            if i != j and is_pareto[i]:
                if is_pareto_dominated(objectives[i], objectives[j]):
                    is_pareto[i] = False
                    break
    
    return solutions[is_pareto], objectives[is_pareto]


def generate_pareto_front_weighted_sum(
    objectives: List[Callable],
    bounds: List[Tuple[float, float]],
    n_points: int = 20,
    constraints: Optional[List] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    使用加权和法生成帕累托前沿
    
    通过改变权重向量，生成多个帕累托最优解。
    
    Parameters
    ----------
    objectives : List[Callable]
        目标函数列表
    bounds : List[Tuple]
        变量边界
    n_points : int
        生成点数
    constraints : List, optional
        约束条件
    
    Returns
    -------
    pareto_solutions : np.ndarray
        帕累托最优解集
    pareto_objectives : np.ndarray
        帕累托前沿点
    """
    n_objectives = len(objectives)
    solutions = []
    obj_values = []
    
    # 生成权重向量
    if n_objectives == 2:
        # 2目标：权重从(1,0)到(0,1)
        weights_list = []
        for i in range(n_points):
            w1 = i / (n_points - 1)
            w2 = 1 - w1
            weights_list.append([w1, w2])
    else:
        # 多目标：随机生成权重
        weights_list = np.random.dirichlet(np.ones(n_objectives), n_points)
    
    # 初始解
    x0 = np.array([(b[0] + b[1]) / 2 for b in bounds])
    
    for weights in weights_list:
        result = weighted_sum_method(
            objectives,
            weights,
            x0,
            bounds,
            constraints
        )
        if result['success']:
            solutions.append(result['x'])
            obj_values.append(result['objectives'])
    
    if len(solutions) == 0:
        raise RuntimeError("未找到任何可行解")
    
    solutions = np.array(solutions)
    obj_values = np.array(obj_values)
    
    # 识别帕累托前沿
    pareto_solutions, pareto_objectives = identify_pareto_front(
        solutions, obj_values
    )
    
    return pareto_solutions, pareto_objectives


class SimpleNSGAII:
    """
    简化的NSGA-II算法
    
    NSGA-II (Non-dominated Sorting Genetic Algorithm II) 是一种
    经典的多目标进化算法。
    
    本实现是教学简化版，适用于小规模问题。
    
    Parameters
    ----------
    objectives : List[Callable]
        目标函数列表
    bounds : List[Tuple]
        变量边界
    population_size : int
        种群大小
    n_generations : int
        迭代代数
    crossover_rate : float
        交叉概率
    mutation_rate : float
        变异概率
    
    Examples
    --------
    >>> def f1(x): return x[0]**2 + x[1]**2
    >>> def f2(x): return (x[0]-1)**2 + (x[1]-1)**2
    >>> nsga = SimpleNSGAII([f1, f2], [(-5, 5), (-5, 5)])
    >>> solutions, objectives = nsga.run()
    """
    
    def __init__(
        self,
        objectives: List[Callable],
        bounds: List[Tuple[float, float]],
        population_size: int = 50,
        n_generations: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        seed: int = 42
    ):
        self.objectives = objectives
        self.bounds = np.array(bounds)
        self.n_vars = len(bounds)
        self.n_objectives = len(objectives)
        self.population_size = population_size
        self.n_generations = n_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.seed = seed
        
        np.random.seed(seed)
        
        self.population = None
        self.history = []
    
    def initialize_population(self):
        """初始化种群"""
        lower = self.bounds[:, 0]
        upper = self.bounds[:, 1]
        self.population = np.random.uniform(
            low=lower,
            high=upper,
            size=(self.population_size, self.n_vars)
        )
    
    def evaluate_population(self, population):
        """评估种群"""
        obj_values = np.zeros((len(population), self.n_objectives))
        for i, individual in enumerate(population):
            for j, obj_func in enumerate(self.objectives):
                obj_values[i, j] = obj_func(individual)
        return obj_values
    
    def non_dominated_sort(self, obj_values):
        """非支配排序"""
        n = len(obj_values)
        fronts = [[]]
        domination_count = np.zeros(n, dtype=int)
        dominated_solutions = [[] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    if is_pareto_dominated(obj_values[j], obj_values[i]):
                        dominated_solutions[i].append(j)
                    elif is_pareto_dominated(obj_values[i], obj_values[j]):
                        domination_count[i] += 1
            
            if domination_count[i] == 0:
                fronts[0].append(i)
        
        # 构建后续前沿
        i = 0
        while len(fronts[i]) > 0:
            next_front = []
            for p in fronts[i]:
                for q in dominated_solutions[p]:
                    domination_count[q] -= 1
                    if domination_count[q] == 0:
                        next_front.append(q)
            i += 1
            fronts.append(next_front)
        
        return fronts[:-1]  # 移除最后的空前沿
    
    def crowding_distance(self, obj_values, front):
        """计算拥挤距离"""
        n = len(front)
        if n <= 2:
            return np.full(n, np.inf)
        
        distances = np.zeros(n)
        
        for m in range(self.n_objectives):
            sorted_indices = np.argsort(obj_values[front, m])
            distances[sorted_indices[0]] = np.inf
            distances[sorted_indices[-1]] = np.inf
            
            obj_range = obj_values[front[sorted_indices[-1]], m] - \
                       obj_values[front[sorted_indices[0]], m]
            
            if obj_range > 0:
                for i in range(1, n-1):
                    distances[sorted_indices[i]] += \
                        (obj_values[front[sorted_indices[i+1]], m] -
                         obj_values[front[sorted_indices[i-1]], m]) / obj_range
        
        return distances
    
    def selection(self, population, obj_values):
        """选择操作"""
        fronts = self.non_dominated_sort(obj_values)
        next_population = []
        
        for front in fronts:
            if len(next_population) + len(front) <= self.population_size:
                next_population.extend(front)
            else:
                # 根据拥挤距离选择
                distances = self.crowding_distance(obj_values, front)
                sorted_indices = np.argsort(distances)[::-1]
                remaining = self.population_size - len(next_population)
                next_population.extend([front[i] for i in sorted_indices[:remaining]])
                break
        
        return population[next_population]
    
    def crossover(self, parent1, parent2):
        """交叉操作（模拟二进制交叉）"""
        if np.random.random() < self.crossover_rate:
            alpha = np.random.random(self.n_vars)
            child1 = alpha * parent1 + (1 - alpha) * parent2
            child2 = (1 - alpha) * parent1 + alpha * parent2
            # 确保在边界内
            child1 = np.clip(child1, self.bounds[:, 0], self.bounds[:, 1])
            child2 = np.clip(child2, self.bounds[:, 0], self.bounds[:, 1])
            return child1, child2
        else:
            return parent1.copy(), parent2.copy()
    
    def mutation(self, individual):
        """变异操作"""
        if np.random.random() < self.mutation_rate:
            mutation_strength = 0.1 * (self.bounds[:, 1] - self.bounds[:, 0])
            mutated = individual + np.random.normal(0, mutation_strength)
            mutated = np.clip(mutated, self.bounds[:, 0], self.bounds[:, 1])
            return mutated
        return individual
    
    def run(self, verbose: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        运行NSGA-II
        
        Parameters
        ----------
        verbose : bool
            是否打印进度
        
        Returns
        -------
        pareto_solutions : np.ndarray
            帕累托最优解
        pareto_objectives : np.ndarray
            帕累托前沿
        """
        # 初始化
        self.initialize_population()
        
        if verbose:
            print(f"\n运行NSGA-II...")
            print(f"  种群大小: {self.population_size}")
            print(f"  迭代代数: {self.n_generations}")
            print(f"  变量数: {self.n_vars}")
            print(f"  目标数: {self.n_objectives}")
        
        for gen in range(self.n_generations):
            # 评估
            obj_values = self.evaluate_population(self.population)
            
            # 选择
            selected = self.selection(self.population, obj_values)
            
            # 生成后代
            offspring = []
            for i in range(0, self.population_size, 2):
                parent1 = selected[i]
                parent2 = selected[min(i+1, len(selected)-1)]
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutation(child1)
                child2 = self.mutation(child2)
                offspring.extend([child1, child2])
            
            offspring = np.array(offspring[:self.population_size])
            
            # 合并父代和子代
            combined = np.vstack([self.population, offspring])
            combined_obj = self.evaluate_population(combined)
            
            # 选择下一代
            self.population = self.selection(combined, combined_obj)
            
            if verbose and (gen % 20 == 0 or gen == self.n_generations - 1):
                # 当前第一前沿大小
                fronts = self.non_dominated_sort(
                    self.evaluate_population(self.population)
                )
                print(f"  代数 {gen}: 第一前沿规模 = {len(fronts[0])}")
        
        # 最终结果
        final_obj = self.evaluate_population(self.population)
        pareto_solutions, pareto_objectives = identify_pareto_front(
            self.population, final_obj
        )
        
        if verbose:
            print(f"\n完成！帕累托前沿包含 {len(pareto_solutions)} 个解")
        
        return pareto_solutions, pareto_objectives


def plot_pareto_front_2d(
    pareto_objectives: np.ndarray,
    obj_names: List[str] = None,
    title: str = "帕累托前沿"
):
    """
    绘制2D帕累托前沿
    
    Parameters
    ----------
    pareto_objectives : np.ndarray
        帕累托前沿点 (n_points × 2)
    obj_names : List[str], optional
        目标名称
    title : str
        标题
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        图形对象
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 排序以便连线
    sorted_indices = np.argsort(pareto_objectives[:, 0])
    sorted_front = pareto_objectives[sorted_indices]
    
    ax.plot(sorted_front[:, 0], sorted_front[:, 1], 'b-o', 
           markersize=8, linewidth=2, markeredgecolor='k', markeredgewidth=1)
    
    if obj_names:
        ax.set_xlabel(obj_names[0], fontsize=12)
        ax.set_ylabel(obj_names[1], fontsize=12)
    else:
        ax.set_xlabel('目标 1', fontsize=12)
        ax.set_ylabel('目标 2', fontsize=12)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig
