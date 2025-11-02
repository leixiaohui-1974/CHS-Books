"""
线性规划求解器

支持标准形式线性规划问题：
    min  c^T x
    s.t. A_ub x <= b_ub
         A_eq x = b_eq
         lb <= x <= ub
"""

import numpy as np
from typing import Optional, Tuple, Dict
from scipy.optimize import linprog


class LinearProgramming:
    """
    线性规划求解器
    
    封装scipy.optimize.linprog，提供更友好的接口
    
    Examples
    --------
    >>> # 最小化: 2x1 + 3x2
    >>> # 约束: x1 + x2 <= 10
    >>> #       x1 >= 2, x2 >= 1
    >>> lp = LinearProgramming()
    >>> result = lp.solve(
    ...     c=[2, 3],
    ...     A_ub=[[1, 1]],
    ...     b_ub=[10],
    ...     bounds=[(2, None), (1, None)]
    ... )
    >>> print(f"最优解: {result['x']}")
    >>> print(f"最优值: {result['fun']:.2f}")
    """
    
    def __init__(self):
        """初始化"""
        self.result = None
    
    def solve(
        self,
        c: np.ndarray,
        A_ub: Optional[np.ndarray] = None,
        b_ub: Optional[np.ndarray] = None,
        A_eq: Optional[np.ndarray] = None,
        b_eq: Optional[np.ndarray] = None,
        bounds: Optional[list] = None,
        method: str = 'highs',
        maximize: bool = False
    ) -> Dict:
        """
        求解线性规划问题
        
        Parameters
        ----------
        c : np.ndarray
            目标函数系数向量
        A_ub : np.ndarray, optional
            不等式约束系数矩阵
        b_ub : np.ndarray, optional
            不等式约束右端项
        A_eq : np.ndarray, optional
            等式约束系数矩阵
        b_eq : np.ndarray, optional
            等式约束右端项
        bounds : list, optional
            变量边界，格式[(lb1, ub1), (lb2, ub2), ...]
        method : str, optional
            求解方法：'highs'（默认）, 'simplex', 'interior-point'
        maximize : bool, optional
            是否为最大化问题，默认False（最小化）
        
        Returns
        -------
        Dict
            求解结果字典，包含：
            - x: 最优解
            - fun: 最优值
            - success: 是否成功
            - message: 求解信息
            - nit: 迭代次数
        """
        # 转换为数组
        c = np.array(c, dtype=float)
        
        # 如果是最大化问题，转换为最小化
        if maximize:
            c = -c
        
        # 求解
        self.result = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method=method
        )
        
        # 整理结果
        result_dict = {
            'x': self.result.x,
            'fun': -self.result.fun if maximize else self.result.fun,
            'success': self.result.success,
            'message': self.result.message,
            'nit': self.result.nit if hasattr(self.result, 'nit') else None,
            'slack': self.result.slack if hasattr(self.result, 'slack') else None
        }
        
        return result_dict
    
    def get_dual_values(self) -> Optional[np.ndarray]:
        """
        获取对偶值（影子价格）
        
        Returns
        -------
        np.ndarray or None
            对偶值
        """
        if self.result is None:
            return None
        
        if hasattr(self.result, 'ineqlin') and self.result.ineqlin is not None:
            return self.result.ineqlin.marginals
        
        return None
    
    def get_sensitivity_ranges(self) -> Optional[Dict]:
        """
        灵敏度分析（需要单纯形法）
        
        Returns
        -------
        Dict or None
            灵敏度范围
        """
        if self.result is None:
            return None
        
        # 单纯形法才有灵敏度信息
        if hasattr(self.result, 'slack'):
            return {
                'slack': self.result.slack,
                'con': self.result.con if hasattr(self.result, 'con') else None
            }
        
        return None


def solve_lp(
    c: np.ndarray,
    A_ub: Optional[np.ndarray] = None,
    b_ub: Optional[np.ndarray] = None,
    A_eq: Optional[np.ndarray] = None,
    b_eq: Optional[np.ndarray] = None,
    bounds: Optional[list] = None,
    maximize: bool = False
) -> Tuple[np.ndarray, float]:
    """
    求解线性规划的便捷函数
    
    Parameters
    ----------
    c : np.ndarray
        目标函数系数
    A_ub, b_ub : np.ndarray, optional
        不等式约束
    A_eq, b_eq : np.ndarray, optional
        等式约束
    bounds : list, optional
        变量边界
    maximize : bool, optional
        是否最大化
    
    Returns
    -------
    Tuple[np.ndarray, float]
        (最优解, 最优值)
    
    Examples
    --------
    >>> c = [2, 3, 4]
    >>> A_ub = [[1, 1, 1]]
    >>> b_ub = [10]
    >>> x, obj = solve_lp(c, A_ub, b_ub, bounds=[(0, None)]*3)
    """
    lp = LinearProgramming()
    result = lp.solve(c, A_ub, b_ub, A_eq, b_eq, bounds, maximize=maximize)
    
    if not result['success']:
        raise ValueError(f"线性规划求解失败: {result['message']}")
    
    return result['x'], result['fun']


class WaterAllocationLP:
    """
    水资源配置线性规划模型
    
    用于求解区域水资源优化配置问题
    
    Examples
    --------
    >>> model = WaterAllocationLP(n_users=3, n_sources=2)
    >>> model.set_objective([10, 12, 15])  # 各用户效益
    >>> model.set_capacity([100, 80])      # 各水源供水能力
    >>> model.set_demand([50, 60, 40])     # 各用户需求
    >>> result = model.solve()
    """
    
    def __init__(self, n_users: int, n_sources: int):
        """
        初始化
        
        Parameters
        ----------
        n_users : int
            用水户数量
        n_sources : int
            水源数量
        """
        self.n_users = n_users
        self.n_sources = n_sources
        self.n_vars = n_users * n_sources
        
        self.benefits = None
        self.capacities = None
        self.demands = None
        self.costs = None
    
    def set_objective(
        self,
        benefits: np.ndarray,
        costs: Optional[np.ndarray] = None
    ):
        """
        设置目标函数：最大化净效益
        
        Parameters
        ----------
        benefits : np.ndarray
            各用户的用水效益 (n_users,)
        costs : np.ndarray, optional
            水源到用户的输水成本 (n_sources, n_users)
        """
        self.benefits = np.array(benefits)
        
        if costs is not None:
            self.costs = np.array(costs)
        else:
            self.costs = np.zeros((self.n_sources, self.n_users))
    
    def set_capacity(self, capacities: np.ndarray):
        """
        设置水源供水能力约束
        
        Parameters
        ----------
        capacities : np.ndarray
            各水源的供水能力 (n_sources,)
        """
        self.capacities = np.array(capacities)
    
    def set_demand(self, demands: np.ndarray):
        """
        设置用水需求约束
        
        Parameters
        ----------
        demands : np.ndarray
            各用户的用水需求 (n_users,)
        """
        self.demands = np.array(demands)
    
    def solve(self, maximize: bool = True) -> Dict:
        """
        求解优化模型
        
        Parameters
        ----------
        maximize : bool
            是否最大化效益
        
        Returns
        -------
        Dict
            求解结果
        """
        if self.benefits is None or self.capacities is None or self.demands is None:
            raise ValueError("请先设置目标函数和约束条件")
        
        # 构造目标函数
        # 变量顺序：x[i,j] 表示水源i到用户j的配水量
        c = []
        for i in range(self.n_sources):
            for j in range(self.n_users):
                # 效益 - 成本
                c.append(self.benefits[j] - self.costs[i, j])
        c = np.array(c)
        
        # 构造约束
        # 1. 水源供水能力约束：sum_j x[i,j] <= capacity[i]
        A_ub_capacity = np.zeros((self.n_sources, self.n_vars))
        for i in range(self.n_sources):
            for j in range(self.n_users):
                idx = i * self.n_users + j
                A_ub_capacity[i, idx] = 1
        b_ub_capacity = self.capacities
        
        # 2. 用户需水约束：sum_i x[i,j] >= demand[j]
        # 转换为 <= 形式：-sum_i x[i,j] <= -demand[j]
        A_ub_demand = np.zeros((self.n_users, self.n_vars))
        for j in range(self.n_users):
            for i in range(self.n_sources):
                idx = i * self.n_users + j
                A_ub_demand[j, idx] = -1
        b_ub_demand = -self.demands
        
        # 合并约束
        A_ub = np.vstack([A_ub_capacity, A_ub_demand])
        b_ub = np.concatenate([b_ub_capacity, b_ub_demand])
        
        # 变量边界：x >= 0
        bounds = [(0, None)] * self.n_vars
        
        # 求解
        lp = LinearProgramming()
        result = lp.solve(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            maximize=maximize
        )
        
        # 整理结果
        if result['success']:
            # 转换为矩阵形式
            x_matrix = result['x'].reshape(self.n_sources, self.n_users)
            result['allocation'] = x_matrix
            result['total_benefit'] = result['fun']
        
        return result
