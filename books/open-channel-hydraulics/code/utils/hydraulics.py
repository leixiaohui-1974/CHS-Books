"""
水力学计算工具函数
包含各种水力学基本公式的实现

主要功能：
1. 曼宁公式和谢才公式
2. 弗劳德数和雷诺数
3. 水力要素计算
4. 能量和动量方程
"""

import numpy as np
from typing import Union


# 常量定义
G = 9.81  # 重力加速度 m/s²
NU = 1.0e-6  # 运动粘性系数 m²/s (20°C清水)


def manning_velocity(R: float, S: float, n: float) -> float:
    """
    曼宁公式计算流速

    公式：v = (1/n) * R^(2/3) * S^(1/2)

    参数：
        R: 水力半径 (m)
        S: 水力坡度 (无量纲)
        n: 曼宁糙率系数 (s/m^(1/3))

    返回：
        v: 断面平均流速 (m/s)

    示例：
        >>> manning_velocity(R=1.0, S=0.001, n=0.025)
        1.265
    """
    if R <= 0:
        raise ValueError("水力半径必须大于0")
    if S <= 0:
        raise ValueError("水力坡度必须大于0")
    if n <= 0:
        raise ValueError("糙率系数必须大于0")

    v = (1.0 / n) * (R ** (2.0/3.0)) * (S ** 0.5)
    return v


def chezy_velocity(R: float, S: float, C: float) -> float:
    """
    谢才公式计算流速

    公式：v = C * sqrt(R * S)

    参数：
        R: 水力半径 (m)
        S: 水力坡度 (无量纲)
        C: 谢才系数 (m^(1/2)/s)

    返回：
        v: 断面平均流速 (m/s)

    示例：
        >>> chezy_velocity(R=1.0, S=0.001, C=50)
        1.581
    """
    if R <= 0:
        raise ValueError("水力半径必须大于0")
    if S <= 0:
        raise ValueError("水力坡度必须大于0")
    if C <= 0:
        raise ValueError("谢才系数必须大于0")

    v = C * np.sqrt(R * S)
    return v


def manning_to_chezy(R: float, n: float) -> float:
    """
    曼宁糙率转换为谢才系数

    公式：C = R^(1/6) / n

    参数：
        R: 水力半径 (m)
        n: 曼宁糙率系数 (s/m^(1/3))

    返回：
        C: 谢才系数 (m^(1/2)/s)
    """
    if R <= 0:
        raise ValueError("水力半径必须大于0")
    if n <= 0:
        raise ValueError("糙率系数必须大于0")

    C = (R ** (1.0/6.0)) / n
    return C


def froude_number(v: float, h: float, g: float = G) -> float:
    """
    计算弗劳德数

    公式：Fr = v / sqrt(g * h)

    参数：
        v: 断面平均流速 (m/s)
        h: 水深 (m)
        g: 重力加速度 (m/s²)，默认9.81

    返回：
        Fr: 弗劳德数 (无量纲)

    说明：
        Fr < 1: 缓流（亚临界流）
        Fr = 1: 临界流
        Fr > 1: 急流（超临界流）

    示例：
        >>> froude_number(v=2.0, h=1.0)
        0.639
    """
    if h <= 0:
        raise ValueError("水深必须大于0")

    Fr = v / np.sqrt(g * h)
    return Fr


def reynolds_number(v: float, R: float, nu: float = NU) -> float:
    """
    计算雷诺数

    公式：Re = v * R / nu

    参数：
        v: 断面平均流速 (m/s)
        R: 水力半径 (m)
        nu: 运动粘性系数 (m²/s)，默认1.0e-6 (20°C清水)

    返回：
        Re: 雷诺数 (无量纲)

    说明：
        Re < 500: 层流
        500 < Re < 2000: 过渡流
        Re > 2000: 紊流（明渠流动通常为紊流）

    示例：
        >>> reynolds_number(v=1.0, R=0.5)
        500000.0
    """
    if R <= 0:
        raise ValueError("水力半径必须大于0")
    if nu <= 0:
        raise ValueError("运动粘性系数必须大于0")

    Re = v * R / nu
    return Re


def specific_energy(h: float, v: float, g: float = G) -> float:
    """
    计算比能（单位重量水流的总机械能）

    公式：E = h + v²/(2g)

    参数：
        h: 水深 (m)
        v: 断面平均流速 (m/s)
        g: 重力加速度 (m/s²)，默认9.81

    返回：
        E: 比能 (m)

    示例：
        >>> specific_energy(h=1.0, v=2.0)
        1.204
    """
    E = h + (v ** 2) / (2 * g)
    return E


def critical_depth_rectangular(q: float, g: float = G) -> float:
    """
    矩形断面临界水深

    公式：hc = (q²/g)^(1/3)

    参数：
        q: 单宽流量 (m²/s)
        g: 重力加速度 (m/s²)，默认9.81

    返回：
        hc: 临界水深 (m)

    示例：
        >>> critical_depth_rectangular(q=2.0)
        0.742
    """
    if q <= 0:
        raise ValueError("单宽流量必须大于0")

    hc = (q ** 2 / g) ** (1.0/3.0)
    return hc


def normal_depth_rectangular_manning(Q: float, b: float, S: float, n: float) -> float:
    """
    矩形断面正常水深（曼宁公式）

    使用迭代法求解：Q = (1/n) * A * R^(2/3) * S^(1/2)

    参数：
        Q: 流量 (m³/s)
        b: 渠底宽度 (m)
        S: 渠底坡度 (无量纲)
        n: 曼宁糙率系数 (s/m^(1/3))

    返回：
        h0: 正常水深 (m)

    示例：
        >>> normal_depth_rectangular_manning(Q=10.0, b=5.0, S=0.001, n=0.025)
        1.456
    """
    if Q <= 0 or b <= 0 or S <= 0 or n <= 0:
        raise ValueError("所有参数必须大于0")

    # 使用牛顿迭代法求解
    h = (Q * n / (b * S**0.5)) ** 0.6  # 初始估计值

    for _ in range(100):  # 最多迭代100次
        A = b * h
        chi = b + 2 * h
        R = A / chi

        # 目标函数：f(h) = Q - (1/n) * A * R^(2/3) * S^(1/2)
        f = Q - (1.0/n) * A * (R**(2.0/3.0)) * (S**0.5)

        # 导数（数值导数）
        dh = 1e-6
        A_plus = b * (h + dh)
        chi_plus = b + 2 * (h + dh)
        R_plus = A_plus / chi_plus
        Q_plus = (1.0/n) * A_plus * (R_plus**(2.0/3.0)) * (S**0.5)
        df = (Q_plus - (Q - f)) / dh

        # 牛顿迭代
        h_new = h - f / df

        # 检查收敛
        if abs(h_new - h) < 1e-6:
            return h_new

        h = h_new

        if h <= 0:
            h = 0.1  # 防止负值

    return h


def hydraulic_radius(A: float, chi: float) -> float:
    """
    计算水力半径

    公式：R = A / χ

    参数：
        A: 过水断面面积 (m²)
        chi: 湿周 (m)

    返回：
        R: 水力半径 (m)
    """
    if A <= 0:
        raise ValueError("过水断面面积必须大于0")
    if chi <= 0:
        raise ValueError("湿周必须大于0")

    return A / chi


def hydraulic_depth(A: float, B: float) -> float:
    """
    计算水力深度

    公式：hm = A / B

    参数：
        A: 过水断面面积 (m²)
        B: 水面宽度 (m)

    返回：
        hm: 水力深度 (m)
    """
    if A <= 0:
        raise ValueError("过水断面面积必须大于0")
    if B <= 0:
        raise ValueError("水面宽度必须大于0")

    return A / B
