"""
明渠断面类
包含各种常见断面类型的水力要素计算

主要类：
1. TrapezoidalChannel - 梯形断面
2. RectangularChannel - 矩形断面
3. CircularChannel - 圆形断面
"""

import numpy as np
from typing import Dict, Tuple


class TrapezoidalChannel:
    """
    梯形断面明渠类

    断面几何：
         <--- B = b + 2*m*h --->
         ╱‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾╲
        ╱ |                 | ╲
       ╱  |                 |  ╲
      ╱   |<---- b ---->|   ╲
     ╱ m  |       h         m ╲
    ╱_____|___________________|_╲

    其中：
    - b: 渠底宽度 (m)
    - h: 水深 (m)
    - m: 边坡系数（水平:垂直 = m:1）
    - B: 水面宽度 = b + 2*m*h (m)

    参数：
        b: 渠底宽度 (m)
        m: 边坡系数 (无量纲)
        n: 曼宁糙率系数 (s/m^(1/3))
        S0: 渠底坡度 (无量纲)
        length: 渠段长度 (m)，可选
    """

    def __init__(self, b: float, m: float, n: float, S0: float, length: float = None):
        """初始化梯形断面"""
        if b <= 0:
            raise ValueError("渠底宽度必须大于0")
        if m < 0:
            raise ValueError("边坡系数不能为负")
        if n <= 0:
            raise ValueError("糙率系数必须大于0")
        if S0 <= 0:
            raise ValueError("渠底坡度必须大于0")

        self.b = b  # 渠底宽度
        self.m = m  # 边坡系数
        self.n = n  # 曼宁糙率系数
        self.S0 = S0  # 渠底坡度
        self.length = length  # 渠段长度

    def area(self, h: float) -> float:
        """
        计算过水断面面积

        公式：A = (b + m*h) * h

        参数：
            h: 水深 (m)

        返回：
            A: 过水断面面积 (m²)
        """
        if h < 0:
            raise ValueError("水深不能为负")
        return (self.b + self.m * h) * h

    def wetted_perimeter(self, h: float) -> float:
        """
        计算湿周

        公式：χ = b + 2*h*sqrt(1 + m²)

        参数：
            h: 水深 (m)

        返回：
            chi: 湿周 (m)
        """
        if h < 0:
            raise ValueError("水深不能为负")
        return self.b + 2 * h * np.sqrt(1 + self.m**2)

    def hydraulic_radius(self, h: float) -> float:
        """
        计算水力半径

        公式：R = A / χ

        参数：
            h: 水深 (m)

        返回：
            R: 水力半径 (m)
        """
        A = self.area(h)
        chi = self.wetted_perimeter(h)
        return A / chi if chi > 0 else 0

    def top_width(self, h: float) -> float:
        """
        计算水面宽度

        公式：B = b + 2*m*h

        参数：
            h: 水深 (m)

        返回：
            B: 水面宽度 (m)
        """
        if h < 0:
            raise ValueError("水深不能为负")
        return self.b + 2 * self.m * h

    def hydraulic_depth(self, h: float) -> float:
        """
        计算水力深度

        公式：hm = A / B

        参数：
            h: 水深 (m)

        返回：
            hm: 水力深度 (m)
        """
        A = self.area(h)
        B = self.top_width(h)
        return A / B if B > 0 else 0

    def velocity(self, h: float) -> float:
        """
        用曼宁公式计算流速

        公式：v = (1/n) * R^(2/3) * S0^(1/2)

        参数：
            h: 水深 (m)

        返回：
            v: 断面平均流速 (m/s)
        """
        R = self.hydraulic_radius(h)
        v = (1.0 / self.n) * (R ** (2.0/3.0)) * (self.S0 ** 0.5)
        return v

    def discharge(self, h: float) -> float:
        """
        计算流量

        公式：Q = A * v

        参数：
            h: 水深 (m)

        返回：
            Q: 流量 (m³/s)
        """
        A = self.area(h)
        v = self.velocity(h)
        return A * v

    def froude_number(self, h: float, g: float = 9.81) -> float:
        """
        计算弗劳德数

        公式：Fr = v / sqrt(g * hm)
        其中 hm = A/B 是水力深度（hydraulic depth）

        对于矩形断面，hm = h（水深）
        对于其他断面，必须使用水力深度

        参数：
            h: 水深 (m)
            g: 重力加速度 (m/s²)，默认9.81

        返回：
            Fr: 弗劳德数 (无量纲)
        """
        v = self.velocity(h)
        hm = self.hydraulic_depth(h)
        return v / np.sqrt(g * hm) if hm > 0 else 0

    def compute_normal_depth(self, Q: float, tol: float = 1e-6, max_iter: int = 100) -> float:
        """
        计算正常水深（给定流量）

        使用牛顿迭代法求解：Q = A * v = A * (1/n) * R^(2/3) * S0^(1/2)

        参数：
            Q: 流量 (m³/s)
            tol: 收敛容差，默认1e-6
            max_iter: 最大迭代次数，默认100

        返回：
            h0: 正常水深 (m)

        异常：
            ValueError: 如果迭代不收敛
        """
        if Q <= 0:
            raise ValueError("流量必须大于0")

        # 初始估计值（根据宽浅渠道近似）
        h = (Q * self.n / (self.b * self.S0**0.5)) ** 0.6

        for i in range(max_iter):
            # 计算当前水深对应的流量
            Q_calc = self.discharge(h)

            # 目标函数
            f = Q_calc - Q

            # 检查收敛
            if abs(f) < tol:
                return h

            # 数值导数
            dh = 1e-6
            Q_plus = self.discharge(h + dh)
            df = (Q_plus - Q_calc) / dh

            # 牛顿迭代
            h_new = h - f / df

            # 确保水深为正
            if h_new <= 0:
                h_new = h / 2

            h = h_new

        raise ValueError(f"正常水深计算不收敛，迭代{max_iter}次后未达到容差{tol}")

    def compute_critical_depth(self, Q: float, tol: float = 1e-6, max_iter: int = 100) -> float:
        """
        计算临界水深（给定流量）

        临界条件：Fr = 1，即 Q²*B/(g*A³) = 1

        参数：
            Q: 流量 (m³/s)
            tol: 收敛容差，默认1e-6
            max_iter: 最大迭代次数，默认100

        返回：
            hc: 临界水深 (m)

        异常：
            ValueError: 如果迭代不收敛
        """
        if Q <= 0:
            raise ValueError("流量必须大于0")

        g = 9.81

        # 初始估计值（矩形断面近似）
        h = (Q**2 / (g * self.b**2)) ** (1.0/3.0)

        for i in range(max_iter):
            A = self.area(h)
            B = self.top_width(h)

            # 目标函数：f(h) = Q²*B/(g*A³) - 1 = 0
            f = Q**2 * B / (g * A**3) - 1.0

            # 检查收敛
            if abs(f) < tol:
                return h

            # 数值导数
            dh = 1e-6
            A_plus = self.area(h + dh)
            B_plus = self.top_width(h + dh)
            f_plus = Q**2 * B_plus / (g * A_plus**3) - 1.0
            df = (f_plus - f) / dh

            # 牛顿迭代
            if abs(df) < 1e-10:
                # 导数太小，使用二分法
                h_new = h * 1.01 if f > 0 else h * 0.99
            else:
                h_new = h - f / df

            # 确保水深为正
            if h_new <= 0:
                h_new = h / 2

            h = h_new

        raise ValueError(f"临界水深计算不收敛，迭代{max_iter}次后未达到容差{tol}")

    def get_hydraulic_elements(self, h: float) -> Dict[str, float]:
        """
        获取所有水力要素

        参数：
            h: 水深 (m)

        返回：
            dict: 包含所有水力要素的字典
        """
        A = self.area(h)
        chi = self.wetted_perimeter(h)
        R = self.hydraulic_radius(h)
        B = self.top_width(h)
        hm = self.hydraulic_depth(h)
        v = self.velocity(h)
        Q = self.discharge(h)
        Fr = self.froude_number(h)

        return {
            "水深_h": h,
            "面积_A": A,
            "湿周_chi": chi,
            "水力半径_R": R,
            "水面宽_B": B,
            "水力深_hm": hm,
            "流速_v": v,
            "流量_Q": Q,
            "弗劳德数_Fr": Fr,
            "流态": "急流" if Fr > 1 else ("临界流" if abs(Fr - 1) < 0.01 else "缓流")
        }

    def __repr__(self):
        return (f"TrapezoidalChannel(b={self.b}m, m={self.m}, "
                f"n={self.n}, S0={self.S0})")


class RectangularChannel:
    """
    矩形断面明渠类（梯形断面的特例，m=0）

    断面几何：
         <--- b --->
         ┌─────────┐
         │         │
         │    h    │
         │         │
         └─────────┘

    参数：
        b: 渠底宽度 (m)
        n: 曼宁糙率系数 (s/m^(1/3))
        S0: 渠底坡度 (无量纲)
        length: 渠段长度 (m)，可选
    """

    def __init__(self, b: float, n: float, S0: float, length: float = None):
        """使用梯形断面类，边坡系数m=0"""
        self._trap = TrapezoidalChannel(b=b, m=0, n=n, S0=S0, length=length)
        self.b = b
        self.n = n
        self.S0 = S0
        self.length = length

    def __getattr__(self, name):
        """委托给内部的梯形断面对象"""
        return getattr(self._trap, name)

    def __repr__(self):
        return f"RectangularChannel(b={self.b}m, n={self.n}, S0={self.S0})"


class CircularChannel:
    """
    圆形断面明渠类（用于管道、涵洞等）

    断面几何：
           ╱‾‾‾╲
         ╱       ╲
        │    D    │
         ╲       ╱
           ╲___╱
        <--- D --->

    参数：
        D: 圆管直径 (m)
        n: 曼宁糙率系数 (s/m^(1/3))
        S0: 管底坡度 (无量纲)
        length: 管段长度 (m)，可选
    """

    def __init__(self, D: float, n: float, S0: float, length: float = None):
        if D <= 0:
            raise ValueError("圆管直径必须大于0")
        if n <= 0:
            raise ValueError("糙率系数必须大于0")
        if S0 <= 0:
            raise ValueError("管底坡度必须大于0")

        self.D = D  # 圆管直径
        self.R_pipe = D / 2  # 圆管半径
        self.n = n
        self.S0 = S0
        self.length = length

    def area(self, h: float) -> float:
        """
        计算过水断面面积

        参数：
            h: 水深 (m)

        返回：
            A: 过水断面面积 (m²)
        """
        if h < 0 or h > self.D:
            raise ValueError(f"水深必须在0到{self.D}m之间")

        # 圆心角
        theta = 2 * np.arccos(1 - 2*h/self.D)
        # 面积
        A = (self.R_pipe**2 / 2) * (theta - np.sin(theta))
        return A

    def wetted_perimeter(self, h: float) -> float:
        """计算湿周"""
        if h < 0 or h > self.D:
            raise ValueError(f"水深必须在0到{self.D}m之间")

        theta = 2 * np.arccos(1 - 2*h/self.D)
        chi = self.R_pipe * theta
        return chi

    def hydraulic_radius(self, h: float) -> float:
        """计算水力半径"""
        A = self.area(h)
        chi = self.wetted_perimeter(h)
        return A / chi if chi > 0 else 0

    def velocity(self, h: float) -> float:
        """用曼宁公式计算流速"""
        R = self.hydraulic_radius(h)
        v = (1.0 / self.n) * (R ** (2.0/3.0)) * (self.S0 ** 0.5)
        return v

    def discharge(self, h: float) -> float:
        """计算流量"""
        A = self.area(h)
        v = self.velocity(h)
        return A * v

    def __repr__(self):
        return f"CircularChannel(D={self.D}m, n={self.n}, S0={self.S0})"
