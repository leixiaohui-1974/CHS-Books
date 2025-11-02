"""
SCE-UA参数率定算法
=================

Shuffled Complex Evolution - University of Arizona

SCE-UA是一种全局优化算法，特别适合水文模型参数率定。

算法特点：
- 结合随机搜索和确定性搜索
- 适合高维非凸优化问题
- 鲁棒性强

参考文献：
Duan, Q., Sorooshian, S., & Gupta, V. (1992). 
"Effective and efficient global optimization for conceptual 
rainfall-runoff models." Water Resources Research, 28(4), 1015-1031.

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Callable, List, Tuple, Dict, Optional
import warnings


class SCEUA:
    """
    SCE-UA优化算法
    
    Parameters
    ----------
    objective_func : callable
        目标函数，接受参数数组，返回标量（最大化）
    bounds : list of tuple
        参数边界列表 [(lower, upper), ...]
    n_complexes : int
        复合体数量（默认：2-5）
    n_points_per_complex : int
        每个复合体的点数（默认：2*n_params+1）
    n_evolution_steps : int
        进化步数（默认：n_params+1）
    alpha : int
        Simplex反射系数（默认：1）
    beta : float
        Simplex收缩系数（默认：0.5）
    """
    
    def __init__(self,
                 objective_func: Callable,
                 bounds: List[Tuple[float, float]],
                 n_complexes: int = None,
                 n_points_per_complex: int = None,
                 n_evolution_steps: int = None,
                 alpha: int = 1,
                 beta: float = 0.5):
        
        self.objective_func = objective_func
        self.bounds = np.array(bounds)
        self.n_params = len(bounds)
        
        # 算法参数
        self.n_complexes = n_complexes or max(2, min(5, self.n_params // 2))
        self.n_points_per_complex = n_points_per_complex or (2 * self.n_params + 1)
        self.n_evolution_steps = n_evolution_steps or (self.n_params + 1)
        self.alpha = alpha
        self.beta = beta
        
        # 计算种群大小
        self.n_points = self.n_complexes * self.n_points_per_complex
        
        # 历史记录
        self.history = {
            'best_params': [],
            'best_scores': [],
            'iterations': []
        }
        
        # 验证参数
        self._validate_parameters()
    
    def _validate_parameters(self):
        """验证参数"""
        if self.n_params <= 0:
            raise ValueError("参数数量必须为正")
        
        if self.n_complexes < 1:
            raise ValueError("复合体数量必须至少为1")
        
        if self.n_points_per_complex < self.n_params + 1:
            warnings.warn(
                f"每个复合体的点数({self.n_points_per_complex})"
                f"小于推荐值({self.n_params + 1})"
            )
    
    def _initialize_population(self) -> np.ndarray:
        """
        初始化种群（拉丁超立方采样）
        
        Returns
        -------
        population : ndarray (n_points, n_params)
            初始种群
        """
        population = np.zeros((self.n_points, self.n_params))
        
        for j in range(self.n_params):
            # 拉丁超立方采样
            segments = np.linspace(0, 1, self.n_points + 1)
            samples = np.random.uniform(segments[:-1], segments[1:])
            np.random.shuffle(samples)
            
            # 映射到参数范围
            lower, upper = self.bounds[j]
            population[:, j] = lower + samples * (upper - lower)
        
        return population
    
    def _evaluate_population(self, population: np.ndarray) -> np.ndarray:
        """
        评估种群
        
        Parameters
        ----------
        population : ndarray (n_points, n_params)
            种群
        
        Returns
        -------
        scores : ndarray (n_points,)
            目标函数值
        """
        scores = np.array([self.objective_func(ind) for ind in population])
        return scores
    
    def _sort_population(self, population: np.ndarray, 
                        scores: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        按得分降序排序种群
        
        Returns
        -------
        sorted_pop : ndarray
            排序后的种群
        sorted_scores : ndarray
            排序后的得分
        """
        indices = np.argsort(scores)[::-1]  # 降序
        return population[indices], scores[indices]
    
    def _partition_into_complexes(self, population: np.ndarray,
                                  scores: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        将种群划分为复合体
        
        Returns
        -------
        complexes : list of (pop, scores)
            复合体列表
        """
        complexes = []
        
        for k in range(self.n_complexes):
            # 按序号k, k+m, k+2m, ... 提取点
            indices = np.arange(k, self.n_points, self.n_complexes)
            complex_pop = population[indices]
            complex_scores = scores[indices]
            complexes.append((complex_pop, complex_scores))
        
        return complexes
    
    def _evolve_complex(self, complex_pop: np.ndarray,
                       complex_scores: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        进化一个复合体
        
        使用Competitive Complex Evolution (CCE)
        """
        n_points = len(complex_pop)
        
        for _ in range(self.n_evolution_steps):
            # 1. 选择子复合体（三角分布采样）
            weights = np.arange(n_points, 0, -1)
            weights = weights / np.sum(weights)
            
            # 选择q+1个点组成simplex（q为参数维度）
            n_simplex = self.n_params + 1
            selected_indices = np.random.choice(
                n_points, size=n_simplex, replace=False, p=weights
            )
            
            simplex = complex_pop[selected_indices]
            simplex_scores = complex_scores[selected_indices]
            
            # 2. 对simplex进行Nelder-Mead演化
            new_point = self._evolve_simplex(simplex, simplex_scores)
            
            # 3. 替换最差点
            worst_idx_in_simplex = np.argmin(simplex_scores)
            worst_idx_in_complex = selected_indices[worst_idx_in_simplex]
            
            new_score = self.objective_func(new_point)
            
            if new_score > complex_scores[worst_idx_in_complex]:
                complex_pop[worst_idx_in_complex] = new_point
                complex_scores[worst_idx_in_complex] = new_score
        
        return complex_pop, complex_scores
    
    def _evolve_simplex(self, simplex: np.ndarray,
                       scores: np.ndarray) -> np.ndarray:
        """
        使用Nelder-Mead方法进化simplex
        
        Returns
        -------
        new_point : ndarray
            新生成的点
        """
        # 排序
        indices = np.argsort(scores)[::-1]
        simplex = simplex[indices]
        scores = scores[indices]
        
        # 计算质心（排除最差点）
        centroid = np.mean(simplex[:-1], axis=0)
        
        # 反射
        worst = simplex[-1]
        reflected = centroid + self.alpha * (centroid - worst)
        reflected = self._enforce_bounds(reflected)
        
        reflected_score = self.objective_func(reflected)
        
        # 如果反射点比最差点好，接受
        if reflected_score > scores[-1]:
            return reflected
        
        # 否则，收缩
        contracted = centroid + self.beta * (worst - centroid)
        contracted = self._enforce_bounds(contracted)
        
        contracted_score = self.objective_func(contracted)
        
        # 选择更好的点
        if contracted_score > scores[-1]:
            return contracted
        else:
            # 随机生成新点
            return self._random_point_in_bounds()
    
    def _enforce_bounds(self, point: np.ndarray) -> np.ndarray:
        """强制参数在边界内"""
        point = np.maximum(point, self.bounds[:, 0])
        point = np.minimum(point, self.bounds[:, 1])
        return point
    
    def _random_point_in_bounds(self) -> np.ndarray:
        """在边界内生成随机点"""
        point = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1])
        return point
    
    def optimize(self, max_iterations: int = 50,
                tolerance: float = 1e-6,
                verbose: bool = True) -> Dict:
        """
        执行优化
        
        Parameters
        ----------
        max_iterations : int
            最大迭代次数
        tolerance : float
            收敛容差
        verbose : bool
            是否打印过程
        
        Returns
        -------
        result : dict
            优化结果，包含：
            - best_params : 最优参数
            - best_score : 最优得分
            - n_iterations : 迭代次数
            - converged : 是否收敛
            - history : 历史记录
        """
        # 初始化
        population = self._initialize_population()
        scores = self._evaluate_population(population)
        population, scores = self._sort_population(population, scores)
        
        best_score_prev = -np.inf
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"SCE-UA优化开始")
            print(f"{'='*70}")
            print(f"参数维度: {self.n_params}")
            print(f"种群大小: {self.n_points}")
            print(f"复合体数: {self.n_complexes}")
            print(f"最大迭代: {max_iterations}\n")
        
        # 迭代
        for iteration in range(max_iterations):
            # 划分复合体
            complexes = self._partition_into_complexes(population, scores)
            
            # 进化各复合体
            evolved_complexes = []
            for complex_pop, complex_scores in complexes:
                evolved_pop, evolved_scores = self._evolve_complex(
                    complex_pop.copy(), complex_scores.copy()
                )
                evolved_complexes.append((evolved_pop, evolved_scores))
            
            # 合并复合体
            population = np.vstack([pop for pop, _ in evolved_complexes])
            scores = np.hstack([scr for _, scr in evolved_complexes])
            
            # 重新排序
            population, scores = self._sort_population(population, scores)
            
            # 记录历史
            best_score = scores[0]
            best_params = population[0]
            
            self.history['best_params'].append(best_params.copy())
            self.history['best_scores'].append(best_score)
            self.history['iterations'].append(iteration + 1)
            
            # 打印进度
            if verbose and (iteration % 10 == 0 or iteration == max_iterations - 1):
                print(f"迭代 {iteration+1:3d}: 最优得分 = {best_score:.6f}")
            
            # 检查收敛
            if abs(best_score - best_score_prev) < tolerance:
                if verbose:
                    print(f"\n在第{iteration+1}次迭代达到收敛（容差={tolerance}）")
                converged = True
                break
            
            best_score_prev = best_score
        else:
            converged = False
            if verbose:
                print(f"\n达到最大迭代次数{max_iterations}")
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"优化完成")
            print(f"{'='*70}")
            print(f"最优得分: {scores[0]:.6f}")
            print(f"最优参数:")
            for i, param in enumerate(population[0]):
                print(f"  参数{i+1}: {param:.6f} (范围: {self.bounds[i]})")
            print(f"{'='*70}\n")
        
        return {
            'best_params': population[0],
            'best_score': scores[0],
            'n_iterations': iteration + 1,
            'converged': converged,
            'history': self.history
        }


def optimize_sce_ua(objective_func: Callable,
                   bounds: List[Tuple[float, float]],
                   max_iterations: int = 50,
                   **kwargs) -> Dict:
    """
    SCE-UA优化的便捷函数
    
    Parameters
    ----------
    objective_func : callable
        目标函数
    bounds : list of tuple
        参数边界
    max_iterations : int
        最大迭代次数
    **kwargs : dict
        传递给SCEUA的其他参数
    
    Returns
    -------
    result : dict
        优化结果
    """
    optimizer = SCEUA(objective_func, bounds, **kwargs)
    return optimizer.optimize(max_iterations=max_iterations)


if __name__ == '__main__':
    # 简单测试：优化Rosenbrock函数
    print("SCE-UA算法测试")
    print("=" * 50)
    print("测试函数: Rosenbrock (最优解: x=[1,1], f=0)")
    print()
    
    def rosenbrock(x):
        """Rosenbrock函数（最小化问题，转为最大化）"""
        return -(100 * (x[1] - x[0]**2)**2 + (1 - x[0])**2)
    
    bounds = [(-5, 5), (-5, 5)]
    
    result = optimize_sce_ua(
        rosenbrock,
        bounds,
        max_iterations=30,
        n_complexes=2
    )
    
    print("测试通过！")
