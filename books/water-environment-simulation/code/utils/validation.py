"""
验证工具
Validation Utilities
"""

import numpy as np


def calculate_error(C_numerical, C_analytical, error_type='L2'):
    """
    计算数值解误差
    
    参数:
        C_numerical: 数值解
        C_analytical: 解析解或参考解
        error_type: 误差类型 ('L1', 'L2', 'Linf', 'relative')
    
    返回:
        error: 误差值
    """
    diff = C_numerical - C_analytical
    
    if error_type == 'L1':
        # L1范数（平均绝对误差）
        error = np.mean(np.abs(diff))
    elif error_type == 'L2':
        # L2范数（均方根误差）
        error = np.sqrt(np.mean(diff**2))
    elif error_type == 'Linf':
        # L∞范数（最大误差）
        error = np.max(np.abs(diff))
    elif error_type == 'relative':
        # 相对误差
        error = np.mean(np.abs(diff) / (np.abs(C_analytical) + 1e-10))
    else:
        raise ValueError(f"未知的误差类型: {error_type}")
    
    return error


def check_stability(method, Cr=None, Fo=None, Pe=None):
    """
    检查数值格式的稳定性
    
    参数:
        method: 数值格式名称
        Cr: Courant数 (u*dt/dx)
        Fo: Fourier数 (D*dt/dx²)
        Pe: Peclet数 (u*L/D)
    
    返回:
        is_stable: 是否稳定
        message: 稳定性信息
    """
    is_stable = True
    messages = []
    
    if method == 'explicit_diffusion':
        if Fo is not None:
            if Fo > 0.5:
                is_stable = False
                messages.append(f"⚠️ Fo = {Fo:.3f} > 0.5，显式扩散格式不稳定！")
            else:
                messages.append(f"✓ Fo = {Fo:.3f} ≤ 0.5，稳定")
    
    elif method == 'upwind':
        if Cr is not None:
            if Cr > 1:
                is_stable = False
                messages.append(f"⚠️ Cr = {Cr:.3f} > 1，迎风格式不稳定！")
            else:
                messages.append(f"✓ Cr = {Cr:.3f} ≤ 1，稳定")
        
        if Fo is not None and Cr is not None:
            if 2*Fo + Cr > 1:
                is_stable = False
                messages.append(f"⚠️ 2*Fo + Cr = {2*Fo + Cr:.3f} > 1，不稳定！")
    
    elif method == 'central':
        if Cr is not None and Fo is not None:
            if Cr > 2*Fo:
                is_stable = False
                messages.append(f"⚠️ Cr = {Cr:.3f} > 2*Fo = {2*Fo:.3f}，中心差分不稳定！")
        
        if Pe is not None:
            if Pe > 2:
                messages.append(f"⚠️ Pe = {Pe:.2f} > 2，可能产生振荡！")
    
    elif method == 'lax_wendroff':
        if Cr is not None and Fo is not None:
            if Cr**2 > 2*Fo:
                is_stable = False
                messages.append(f"⚠️ Cr² = {Cr**2:.3f} > 2*Fo = {2*Fo:.3f}，Lax-Wendroff不稳定！")
    
    return is_stable, '\n'.join(messages)


def calculate_conservation_error(C, dx, dt=None):
    """
    计算质量守恒误差
    
    参数:
        C: 浓度场 (nt, nx) 或 (nx,)
        dx: 空间步长
        dt: 时间步长（可选）
    
    返回:
        mass_error: 质量守恒误差
    """
    if C.ndim == 1:
        # 单一时刻
        total_mass = np.sum(C) * dx
        return total_mass
    else:
        # 多个时刻
        initial_mass = np.sum(C[0, :]) * dx
        final_mass = np.sum(C[-1, :]) * dx
        mass_error = np.abs(final_mass - initial_mass) / initial_mass
        
        return mass_error


def check_convergence(errors, grid_sizes):
    """
    检查网格收敛性
    
    参数:
        errors: 不同网格的误差
        grid_sizes: 网格尺寸 (dx)
    
    返回:
        order: 收敛阶数
    """
    # 使用对数拟合计算收敛阶
    log_dx = np.log(grid_sizes)
    log_error = np.log(errors)
    
    # 线性拟合 log(error) = order * log(dx) + const
    coeffs = np.polyfit(log_dx, log_error, 1)
    order = coeffs[0]
    
    return order


def calculate_peclet_number(u, L, D):
    """
    计算Peclet数
    
    Pe = u*L/D （对流与扩散的比值）
    
    Pe << 1: 扩散主导
    Pe >> 1: 对流主导
    Pe ~ 1: 对流和扩散同等重要
    """
    Pe = u * L / D
    
    if Pe < 0.1:
        regime = "扩散主导"
    elif Pe > 10:
        regime = "对流主导"
    else:
        regime = "对流-扩散平衡"
    
    return Pe, regime


def calculate_courant_number(u, dt, dx):
    """
    计算Courant数
    
    Cr = u*dt/dx （CFL条件）
    
    Cr ≤ 1: 满足CFL条件
    """
    Cr = u * dt / dx
    is_cfl_satisfied = Cr <= 1.0
    
    return Cr, is_cfl_satisfied


def calculate_fourier_number(D, dt, dx):
    """
    计算Fourier数
    
    Fo = D*dt/dx²
    
    对于显式格式: Fo ≤ 0.5
    """
    Fo = D * dt / dx**2
    is_stable = Fo <= 0.5
    
    return Fo, is_stable
