"""
gwflow.coupling.solver - 耦合求解器

本模块提供地表地下水耦合系统的求解方法，包括：
- 弱耦合（松散耦合）求解器
- 顺序耦合求解器

耦合方法分类：
-----------
1. 弱耦合（Loosely Coupled / Iterative）：
   - 交替求解地表水和地下水
   - 在每个时间步内迭代直到收敛
   - 计算效率高，但可能不稳定

2. 强耦合（Tightly Coupled / Fully Coupled）：
   - 同时求解地表水和地下水
   - 构建联合矩阵系统
   - 稳定性好，但计算量大

3. 顺序耦合（Sequential Coupling）：
   - 按顺序求解，不迭代
   - 适用于交互较弱的情况
   - 最快但精度较低

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Callable, Any, Optional
from .exchange import compute_exchange_flux


def solve_coupled_weak(
    gw_solver: Callable,
    sw_solver: Callable,
    initial_h_gw: np.ndarray,
    initial_h_sw: np.ndarray,
    conductance: float,
    dt: float,
    n_steps: int,
    coupling_points: Optional[np.ndarray] = None,
    max_iter: int = 20,
    tol: float = 1e-4,
    relaxation: float = 1.0,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    弱耦合（迭代）求解器
    
    算法流程（每个时间步）：
    ----------------------
    1. 初始化：h_gw^(0) = h_gw^(n-1), h_sw^(0) = h_sw^(n-1)
    2. 迭代k = 1, 2, ..., max_iter:
       a. 计算交换通量：Q^(k) = C * (h_sw^(k-1) - h_gw^(k-1))
       b. 求解地下水：h_gw^(k) = GW_Solver(h_gw^(k-1), Q^(k))
       c. 更新交换通量：Q^(k) = C * (h_sw^(k-1) - h_gw^(k))
       d. 求解地表水：h_sw^(k) = SW_Solver(h_sw^(k-1), -Q^(k))
       e. 检查收敛：|h^(k) - h^(k-1)| < tol
    3. 若收敛，进入下一时间步；否则继续迭代
    
    Parameters
    ----------
    gw_solver : callable
        地下水求解器函数
        签名：h_new = gw_solver(h_old, source_term, dt)
    sw_solver : callable
        地表水求解器函数
        签名：h_new = sw_solver(h_old, source_term, dt)
    initial_h_gw : array, shape (n_gw,)
        地下水初始水头 (m)
    initial_h_sw : array, shape (n_sw,)
        地表水初始水头/水深 (m)
    conductance : float
        水力传导度 (m²/day)
    dt : float
        时间步长 (day)
    n_steps : int
        时间步数
    coupling_points : array, optional
        耦合点索引，shape (n_coupling, 2)
        每行为 [gw_idx, sw_idx]
        如果为None，假设一一对应
    max_iter : int, default=20
        每个时间步最大迭代次数
    tol : float, default=1e-4
        收敛容差 (m)
    relaxation : float, default=1.0
        松弛因子（0 < relaxation <= 1）
        用于稳定迭代：h^(k) = relaxation * h_new + (1-relaxation) * h^(k-1)
    verbose : bool, default=True
        是否输出详细信息
    
    Returns
    -------
    results : dict
        求解结果，包含：
        - h_gw_history : array, shape (n_steps+1, n_gw)
            地下水水头历史
        - h_sw_history : array, shape (n_steps+1, n_sw)
            地表水水头历史
        - exchange_history : array, shape (n_steps, n_coupling)
            交换通量历史
        - convergence_history : list of dict
            每个时间步的收敛信息
        - success : bool
            是否成功完成
    
    Examples
    --------
    >>> # 定义简单的求解器
    >>> def simple_gw_solver(h_old, source, dt):
    ...     return h_old + source * dt
    >>> 
    >>> def simple_sw_solver(h_old, source, dt):
    ...     return h_old + source * dt
    >>> 
    >>> # 初始条件
    >>> h_gw_init = np.ones(10) * 25.0
    >>> h_sw_init = np.ones(10) * 30.0
    >>> 
    >>> # 弱耦合求解
    >>> result = solve_coupled_weak(
    ...     gw_solver=simple_gw_solver,
    ...     sw_solver=simple_sw_solver,
    ...     initial_h_gw=h_gw_init,
    ...     initial_h_sw=h_sw_init,
    ...     conductance=1000.0,
    ...     dt=1.0,
    ...     n_steps=10
    ... )
    
    Notes
    -----
    1. 松弛因子（relaxation）：
       - 1.0: 无松弛（可能不稳定）
       - 0.5-0.8: 适度松弛（推荐）
       - < 0.5: 强松弛（收敛慢）
    
    2. 收敛性：
       - 强交互：可能需要更多迭代或更小的松弛因子
       - 弱交互：通常快速收敛
    
    3. 稳定性：
       - 小时间步：更稳定
       - 大传导度：可能需要更多迭代
    """
    # 验证输入
    if not 0 < relaxation <= 1:
        raise ValueError(f"relaxation must be in (0, 1], got {relaxation}")
    
    n_gw = len(initial_h_gw)
    n_sw = len(initial_h_sw)
    
    # 设置耦合点
    if coupling_points is None:
        # 假设一一对应
        if n_gw != n_sw:
            raise ValueError(
                "If coupling_points is None, n_gw must equal n_sw. "
                f"Got n_gw={n_gw}, n_sw={n_sw}"
            )
        coupling_points = np.column_stack([np.arange(n_gw), np.arange(n_sw)])
    
    n_coupling = len(coupling_points)
    
    # 初始化
    h_gw = initial_h_gw.copy()
    h_sw = initial_h_sw.copy()
    
    # 存储历史
    h_gw_history = np.zeros((n_steps + 1, n_gw))
    h_sw_history = np.zeros((n_steps + 1, n_sw))
    exchange_history = np.zeros((n_steps, n_coupling))
    convergence_history = []
    
    h_gw_history[0] = h_gw
    h_sw_history[0] = h_sw
    
    if verbose:
        print("="*60)
        print("弱耦合求解器")
        print("="*60)
        print(f"地下水节点数: {n_gw}")
        print(f"地表水节点数: {n_sw}")
        print(f"耦合点数: {n_coupling}")
        print(f"时间步数: {n_steps}")
        print(f"时间步长: {dt} day")
        print(f"松弛因子: {relaxation}")
        print()
    
    # 时间步进
    for step in range(n_steps):
        if verbose and (step % max(1, n_steps // 10) == 0):
            print(f"时间步 {step+1}/{n_steps}")
        
        # 弱耦合迭代
        converged = False
        for iter_count in range(max_iter):
            h_gw_old = h_gw.copy()
            h_sw_old = h_sw.copy()
            
            # 1. 计算耦合点的交换通量
            exchange_flux = np.zeros(n_coupling)
            for i, (gw_idx, sw_idx) in enumerate(coupling_points):
                exchange_flux[i] = compute_exchange_flux(
                    h_gw[gw_idx], h_sw[sw_idx], conductance
                )
            
            # 2. 将交换通量分配到源汇项
            gw_source = np.zeros(n_gw)
            sw_source = np.zeros(n_sw)
            
            for i, (gw_idx, sw_idx) in enumerate(coupling_points):
                gw_source[gw_idx] += exchange_flux[i]
                sw_source[sw_idx] -= exchange_flux[i]
            
            # 3. 求解地下水
            h_gw_new = gw_solver(h_gw, gw_source, dt)
            
            # 应用松弛
            h_gw = relaxation * h_gw_new + (1 - relaxation) * h_gw
            
            # 4. 重新计算交换通量（使用新的h_gw）
            for i, (gw_idx, sw_idx) in enumerate(coupling_points):
                exchange_flux[i] = compute_exchange_flux(
                    h_gw[gw_idx], h_sw[sw_idx], conductance
                )
            
            # 更新源汇项
            gw_source = np.zeros(n_gw)
            sw_source = np.zeros(n_sw)
            
            for i, (gw_idx, sw_idx) in enumerate(coupling_points):
                gw_source[gw_idx] += exchange_flux[i]
                sw_source[sw_idx] -= exchange_flux[i]
            
            # 5. 求解地表水
            h_sw_new = sw_solver(h_sw, sw_source, dt)
            
            # 应用松弛
            h_sw = relaxation * h_sw_new + (1 - relaxation) * h_sw
            
            # 6. 检查收敛
            error_gw = np.max(np.abs(h_gw - h_gw_old))
            error_sw = np.max(np.abs(h_sw - h_sw_old))
            max_error = max(error_gw, error_sw)
            
            if max_error < tol:
                converged = True
                convergence_history.append({
                    'step': step,
                    'iterations': iter_count + 1,
                    'error': max_error,
                    'converged': True
                })
                if verbose and (step % max(1, n_steps // 10) == 0):
                    print(f"  收敛于第 {iter_count+1} 次迭代, 误差: {max_error:.2e}")
                break
        
        if not converged:
            convergence_history.append({
                'step': step,
                'iterations': max_iter,
                'error': max_error,
                'converged': False
            })
            if verbose:
                print(f"  警告: 时间步 {step+1} 未收敛, 误差: {max_error:.2e}")
        
        # 记录结果
        h_gw_history[step + 1] = h_gw
        h_sw_history[step + 1] = h_sw
        
        # 最终交换通量
        for i, (gw_idx, sw_idx) in enumerate(coupling_points):
            exchange_history[step, i] = compute_exchange_flux(
                h_gw[gw_idx], h_sw[sw_idx], conductance
            )
    
    if verbose:
        n_converged = sum(1 for c in convergence_history if c['converged'])
        print(f"\n完成! {n_converged}/{n_steps} 个时间步收敛")
    
    return {
        'h_gw_history': h_gw_history,
        'h_sw_history': h_sw_history,
        'exchange_history': exchange_history,
        'convergence_history': convergence_history,
        'success': True
    }


def solve_sequential(
    gw_solver: Callable,
    sw_solver: Callable,
    initial_h_gw: np.ndarray,
    initial_h_sw: np.ndarray,
    conductance: float,
    dt: float,
    n_steps: int,
    coupling_points: Optional[np.ndarray] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    顺序耦合求解器
    
    算法流程（每个时间步）：
    ----------------------
    1. 使用上一时间步的h_sw计算交换通量
    2. 求解地下水
    3. 使用新的h_gw更新交换通量
    4. 求解地表水
    5. 进入下一时间步（不迭代）
    
    特点：
    - 最快的耦合方法
    - 不保证耦合条件的强满足
    - 适用于弱交互系统
    
    Parameters
    ----------
    参数与 solve_coupled_weak 相同，但没有 max_iter, tol, relaxation
    
    Returns
    -------
    results : dict
        与 solve_coupled_weak 相同
    
    Notes
    -----
    顺序耦合不进行迭代，因此：
    - 计算速度最快
    - 精度较低
    - 可能出现质量不守恒
    
    建议用于：
    - 耦合强度弱的情况
    - 需要快速估算的场景
    - 初步探索性分析
    """
    n_gw = len(initial_h_gw)
    n_sw = len(initial_h_sw)
    
    # 设置耦合点
    if coupling_points is None:
        if n_gw != n_sw:
            raise ValueError(
                "If coupling_points is None, n_gw must equal n_sw"
            )
        coupling_points = np.column_stack([np.arange(n_gw), np.arange(n_sw)])
    
    n_coupling = len(coupling_points)
    
    # 初始化
    h_gw = initial_h_gw.copy()
    h_sw = initial_h_sw.copy()
    
    # 存储历史
    h_gw_history = np.zeros((n_steps + 1, n_gw))
    h_sw_history = np.zeros((n_steps + 1, n_sw))
    exchange_history = np.zeros((n_steps, n_coupling))
    
    h_gw_history[0] = h_gw
    h_sw_history[0] = h_sw
    
    if verbose:
        print("="*60)
        print("顺序耦合求解器")
        print("="*60)
        print(f"时间步数: {n_steps}")
        print(f"时间步长: {dt} day")
        print()
    
    # 时间步进
    for step in range(n_steps):
        if verbose and (step % max(1, n_steps // 10) == 0):
            print(f"时间步 {step+1}/{n_steps}")
        
        # 1. 计算交换通量（使用当前状态）
        exchange_flux = np.zeros(n_coupling)
        for i, (gw_idx, sw_idx) in enumerate(coupling_points):
            exchange_flux[i] = compute_exchange_flux(
                h_gw[gw_idx], h_sw[sw_idx], conductance
            )
        
        # 2. 分配源汇项并求解地下水
        gw_source = np.zeros(n_gw)
        for i, (gw_idx, _) in enumerate(coupling_points):
            gw_source[gw_idx] += exchange_flux[i]
        
        h_gw = gw_solver(h_gw, gw_source, dt)
        
        # 3. 重新计算交换通量（使用新的h_gw）
        for i, (gw_idx, sw_idx) in enumerate(coupling_points):
            exchange_flux[i] = compute_exchange_flux(
                h_gw[gw_idx], h_sw[sw_idx], conductance
            )
        
        # 4. 求解地表水
        sw_source = np.zeros(n_sw)
        for i, (_, sw_idx) in enumerate(coupling_points):
            sw_source[sw_idx] -= exchange_flux[i]
        
        h_sw = sw_solver(h_sw, sw_source, dt)
        
        # 记录结果
        h_gw_history[step + 1] = h_gw
        h_sw_history[step + 1] = h_sw
        exchange_history[step] = exchange_flux
    
    if verbose:
        print("\n完成!")
    
    return {
        'h_gw_history': h_gw_history,
        'h_sw_history': h_sw_history,
        'exchange_history': exchange_history,
        'convergence_history': [],  # 顺序耦合无迭代信息
        'success': True
    }
