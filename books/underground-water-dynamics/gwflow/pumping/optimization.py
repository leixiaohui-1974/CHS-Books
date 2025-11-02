"""
抽水井优化模块
"""

import numpy as np
from scipy.optimize import linprog, minimize
from typing import List, Tuple, Optional, Dict, Callable

from .analytical import superposition_principle


def optimize_pumping_rates(
    well_locations: np.ndarray,
    T: float,
    S: float,
    h0: float,
    h_min: float,
    Q_max: np.ndarray,
    constraint_points: np.ndarray,
    t: float = 100.0,
    method: str = 'linear'
) -> Dict:
    """
    优化多口井的抽水量
    
    目标：最大化总抽水量
    约束：满足最小水位要求
    
    Parameters
    ----------
    well_locations : ndarray, shape (n_wells, 2)
        井的坐标 [[x1,y1], [x2,y2], ...]
    T, S : float
        含水层参数
    h0 : float
        初始水头 [m]
    h_min : float
        最小允许水头 [m]
    Q_max : ndarray, shape (n_wells,)
        每口井的最大抽水量 [m³/day]
    constraint_points : ndarray, shape (n_points, 2)
        需要满足约束的点
    t : float
        预测时间 [day]
    method : str
        'linear' 使用线性规划（Cooper-Jacob）
        'nonlinear' 使用非线性优化（Theis）
    
    Returns
    -------
    result : dict
        优化结果，包含：
        - Q_opt: 最优抽水量
        - total_Q: 总抽水量
        - h_constraint: 约束点的水头
        - success: 是否成功
    """
    n_wells = len(well_locations)
    n_points = len(constraint_points)
    
    if method == 'linear':
        # 使用Cooper-Jacob线性近似
        # 降深 s = (Q / 4πT) * ln(2.25Tt / r²S)
        # 水头 h = h0 - s = h0 - Σ(Q_i * coef_i)
        
        # 计算系数矩阵
        A_ub = np.zeros((n_points, n_wells))
        
        for i, (xp, yp) in enumerate(constraint_points):
            for j, (xw, yw) in enumerate(well_locations):
                r = np.sqrt((xp - xw)**2 + (yp - yw)**2)
                r = max(r, 0.1)  # 避免r=0
                
                # Cooper-Jacob系数
                coef = np.log(2.25 * T * t / (r**2 * S)) / (4 * np.pi * T)
                A_ub[i, j] = coef  # 降深对Q的系数
        
        # 约束：h0 - Σ(coef * Q) >= h_min
        # 即：Σ(coef * Q) <= h0 - h_min
        b_ub = np.full(n_points, h0 - h_min)
        
        # 目标：最大化 Σ Q_i，即最小化 -Σ Q_i
        c = -np.ones(n_wells)
        
        # 边界：0 <= Q_i <= Q_max_i
        bounds = [(0, q_max) for q_max in Q_max]
        
        # 求解
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if res.success:
            Q_opt = res.x
            total_Q = np.sum(Q_opt)
            
            # 计算约束点水头
            wells_list = [(well_locations[i, 0], well_locations[i, 1], Q_opt[i]) 
                          for i in range(n_wells)]
            s = superposition_principle(
                wells_list,
                constraint_points[:, 0],
                constraint_points[:, 1],
                t, T, S, method='cooper_jacob'
            )
            h_constraint = h0 - s
            
            return {
                'Q_opt': Q_opt,
                'total_Q': total_Q,
                'h_constraint': h_constraint,
                'success': True,
                'message': 'Optimization successful'
            }
        else:
            return {
                'Q_opt': None,
                'total_Q': 0,
                'h_constraint': None,
                'success': False,
                'message': res.message
            }
    
    elif method == 'nonlinear':
        # 使用Theis完整解，非线性优化
        def objective(Q):
            """目标函数：-Σ Q_i（最大化总抽水量）"""
            return -np.sum(Q)
        
        def constraint_func(Q):
            """约束函数：h >= h_min，返回 h - h_min >= 0"""
            wells_list = [(well_locations[i, 0], well_locations[i, 1], Q[i]) 
                          for i in range(n_wells)]
            s = superposition_principle(
                wells_list,
                constraint_points[:, 0],
                constraint_points[:, 1],
                t, T, S, method='theis'
            )
            h = h0 - s
            return h - h_min  # 所有点 >= 0
        
        # 约束
        constraints = {'type': 'ineq', 'fun': constraint_func}
        
        # 边界
        bounds = [(0, q_max) for q_max in Q_max]
        
        # 初始猜测（均匀分配）
        Q0 = Q_max * 0.5
        
        # 求解
        res = minimize(objective, Q0, method='SLSQP', 
                       bounds=bounds, constraints=constraints)
        
        if res.success:
            Q_opt = res.x
            total_Q = np.sum(Q_opt)
            
            wells_list = [(well_locations[i, 0], well_locations[i, 1], Q_opt[i]) 
                          for i in range(n_wells)]
            s = superposition_principle(
                wells_list,
                constraint_points[:, 0],
                constraint_points[:, 1],
                t, T, S, method='theis'
            )
            h_constraint = h0 - s
            
            return {
                'Q_opt': Q_opt,
                'total_Q': total_Q,
                'h_constraint': h_constraint,
                'success': True,
                'message': 'Optimization successful'
            }
        else:
            return {
                'Q_opt': None,
                'total_Q': 0,
                'h_constraint': None,
                'success': False,
                'message': res.message
            }
    
    else:
        raise ValueError(f"Unknown method: {method}")


def optimize_well_locations(
    n_wells: int,
    feasible_region: Tuple[float, float, float, float],
    total_demand: float,
    T: float,
    S: float,
    h0: float,
    h_min: float,
    constraint_points: np.ndarray,
    t: float = 100.0,
    max_iter: int = 100
) -> Dict:
    """
    优化井的位置
    
    使用遗传算法或随机搜索
    
    Parameters
    ----------
    n_wells : int
        井的数量
    feasible_region : tuple
        可行域 (x_min, x_max, y_min, y_max)
    total_demand : float
        总需水量 [m³/day]
    T, S : float
        含水层参数
    h0, h_min : float
        初始水头和最小水头 [m]
    constraint_points : ndarray
        约束点
    t : float
        预测时间
    max_iter : int
        最大迭代次数
    
    Returns
    -------
    result : dict
        优化结果
    """
    x_min, x_max, y_min, y_max = feasible_region
    Q_per_well = total_demand / n_wells
    
    best_objective = -np.inf
    best_locations = None
    best_violation = np.inf
    
    for iteration in range(max_iter):
        # 随机生成井位
        x_wells = np.random.uniform(x_min, x_max, n_wells)
        y_wells = np.random.uniform(y_min, y_max, n_wells)
        locations = np.column_stack([x_wells, y_wells])
        
        # 计算约束点水头
        wells_list = [(locations[i, 0], locations[i, 1], Q_per_well) 
                      for i in range(n_wells)]
        s = superposition_principle(
            wells_list,
            constraint_points[:, 0],
            constraint_points[:, 1],
            t, T, S, method='cooper_jacob'
        )
        h = h0 - s
        
        # 检查约束
        violation = np.sum(np.maximum(0, h_min - h))
        
        if violation < best_violation:
            best_violation = violation
            best_locations = locations
            best_objective = -violation  # 尽量减少违反量
    
    return {
        'locations': best_locations,
        'violation': best_violation,
        'feasible': best_violation < 1e-6,
        'message': f'Best violation: {best_violation:.2e}'
    }


def compute_feasible_region(
    well_location: Tuple[float, float],
    Q: float,
    T: float,
    S: float,
    h0: float,
    h_min: float,
    t: float,
    grid_x: np.ndarray,
    grid_y: np.ndarray
) -> np.ndarray:
    """
    计算给定井位和流量下的可行域
    
    返回满足h >= h_min的区域
    
    Parameters
    ----------
    well_location : tuple
        井的坐标 (x, y)
    Q : float
        抽水量
    T, S : float
        含水层参数
    h0, h_min : float
        初始和最小水头
    t : float
        时间
    grid_x, grid_y : ndarray
        网格坐标
    
    Returns
    -------
    feasible : ndarray (bool)
        可行域掩码
    """
    wells_list = [(well_location[0], well_location[1], Q)]
    s = superposition_principle(
        wells_list,
        grid_x,
        grid_y,
        t, T, S, method='cooper_jacob'
    )
    h = h0 - s
    feasible = h >= h_min
    
    return feasible
