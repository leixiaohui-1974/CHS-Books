"""
水工建筑物类
包含堰、闸门、水跃等建筑物的水力计算

主要类：
1. Weir - 堰流计算（薄壁堰、宽顶堰）
2. Gate - 闸门出流计算（自由出流、淹没出流）
3. HydraulicJump - 水跃计算（共轭水深、消能率）
"""

import numpy as np
from typing import Dict, Tuple, Optional


class Weir:
    """
    堰流计算类

    堰是一种常用的量水建筑物，也用于溢流和调节水位。

    堰的分类：
    1. 按堰顶厚度：薄壁堰、宽顶堰、实用堰
    2. 按堰顶形状：矩形堰、三角形堰、梯形堰
    3. 按侧收缩：完全收缩、无侧收缩

    参数：
        b: 堰顶宽度 (m)
        weir_type: 堰的类型 ('thin', 'broad', 'practical')
        m: 流量系数（根据堰型确定）
    """

    def __init__(self, b: float, weir_type: str = 'thin', m: float = None):
        if b <= 0:
            raise ValueError("堰顶宽度必须大于0")

        self.b = b  # 堰顶宽度
        self.weir_type = weir_type

        # 默认流量系数
        if m is None:
            if weir_type == 'thin':
                self.m = 0.40  # 薄壁堰
            elif weir_type == 'broad':
                self.m = 0.385  # 宽顶堰
            elif weir_type == 'practical':
                self.m = 0.35  # 实用堰
            else:
                self.m = 0.40
        else:
            self.m = m

        self.g = 9.81

    def discharge_rectangular(self, H: float, with_contraction: bool = True) -> float:
        """
        矩形堰流量计算

        公式：Q = m * b * sqrt(2g) * H^(3/2)
        有侧收缩时：Q = m * (b - 0.1*n*H) * sqrt(2g) * H^(3/2)

        参数：
            H: 堰顶水头（上游水深-堰顶高程）(m)
            with_contraction: 是否考虑侧收缩，默认True

        返回：
            Q: 流量 (m³/s)
        """
        if H <= 0:
            raise ValueError("堰顶水头必须大于0")

        if with_contraction:
            # 考虑侧收缩（假设两侧收缩，n=2）
            b_eff = self.b - 0.1 * 2 * H
            if b_eff <= 0:
                b_eff = self.b * 0.9  # 确保有效宽度为正
        else:
            b_eff = self.b

        Q = self.m * b_eff * np.sqrt(2 * self.g) * (H ** 1.5)
        return Q

    def discharge_triangular(self, H: float, theta: float = 90.0) -> float:
        """
        三角形堰流量计算

        公式：Q = (8/15) * m * sqrt(2g) * tan(θ/2) * H^(5/2)

        参数：
            H: 堰顶水头 (m)
            theta: 三角形顶角（度），默认90度

        返回：
            Q: 流量 (m³/s)
        """
        if H <= 0:
            raise ValueError("堰顶水头必须大于0")
        if theta <= 0 or theta >= 180:
            raise ValueError("顶角必须在0-180度之间")

        theta_rad = np.radians(theta)
        Q = (8.0/15.0) * self.m * np.sqrt(2*self.g) * np.tan(theta_rad/2) * (H ** 2.5)
        return Q

    def head_from_discharge(self, Q: float, tol: float = 1e-6, max_iter: int = 100) -> float:
        """
        反算堰顶水头（已知流量）

        使用牛顿迭代法求解

        参数：
            Q: 流量 (m³/s)
            tol: 收敛容差
            max_iter: 最大迭代次数

        返回：
            H: 堰顶水头 (m)
        """
        # 初始估计值
        H = (Q / (self.m * self.b * np.sqrt(2*self.g))) ** (2.0/3.0)

        for i in range(max_iter):
            Q_calc = self.discharge_rectangular(H, with_contraction=False)
            f = Q_calc - Q

            if abs(f) < tol:
                return H

            # 数值导数
            dH = 1e-6
            Q_plus = self.discharge_rectangular(H + dH, with_contraction=False)
            df = (Q_plus - Q_calc) / dH

            H_new = H - f / df

            if H_new <= 0:
                H_new = H / 2

            H = H_new

        raise ValueError(f"堰顶水头反算不收敛，迭代{max_iter}次")

    def __repr__(self):
        return f"Weir(b={self.b}m, type={self.weir_type}, m={self.m})"


class Gate:
    """
    闸门出流计算类

    闸门是控制流量和调节水位的重要建筑物。

    出流类型：
    1. 自由出流：下游水深不影响出流，临界水深在闸孔
    2. 淹没出流：下游水深较高，影响出流能力

    参数：
        b: 闸门宽度 (m)
        mu: 流量系数（自由出流），默认0.60
        mu_s: 流量系数（淹没出流），默认0.85
    """

    def __init__(self, b: float, mu: float = 0.60, mu_s: float = 0.85):
        if b <= 0:
            raise ValueError("闸门宽度必须大于0")

        self.b = b
        self.mu = mu  # 自由出流流量系数
        self.mu_s = mu_s  # 淹没出流流量系数
        self.g = 9.81

    def discharge_free(self, e: float, H: float) -> float:
        """
        闸门自由出流流量计算

        公式：Q = μ * b * e * sqrt(2g * H)

        参数：
            e: 闸门开度（闸底至闸门底的距离）(m)
            H: 上游水头（上游水深）(m)

        返回：
            Q: 流量 (m³/s)
        """
        if e <= 0:
            raise ValueError("闸门开度必须大于0")
        if H <= 0:
            raise ValueError("上游水头必须大于0")

        Q = self.mu * self.b * e * np.sqrt(2 * self.g * H)
        return Q

    def discharge_submerged(self, e: float, H1: float, H2: float) -> float:
        """
        闸门淹没出流流量计算

        公式：Q = μs * b * e * sqrt(2g * (H1 - H2))

        参数：
            e: 闸门开度 (m)
            H1: 上游水深 (m)
            H2: 下游水深 (m)

        返回：
            Q: 流量 (m³/s)
        """
        if e <= 0:
            raise ValueError("闸门开度必须大于0")
        if H1 <= H2:
            raise ValueError("上游水深必须大于下游水深")

        dH = H1 - H2
        Q = self.mu_s * self.b * e * np.sqrt(2 * self.g * dH)
        return Q

    def check_submergence(self, e: float, H1: float, H2: float) -> bool:
        """
        判断出流状态（自由或淹没）

        判据：淹没度 σ = H2/H1 < 0.6 为自由出流

        参数：
            e: 闸门开度 (m)
            H1: 上游水深 (m)
            H2: 下游水深 (m)

        返回：
            bool: True表示淹没出流，False表示自由出流
        """
        sigma = H2 / H1
        return sigma > 0.6

    def opening_from_discharge(self, Q: float, H: float) -> float:
        """
        反算闸门开度（已知流量，假设自由出流）

        从 Q = μ * b * e * sqrt(2g * H) 解出 e

        参数：
            Q: 设计流量 (m³/s)
            H: 上游水深 (m)

        返回：
            e: 所需开度 (m)
        """
        if Q <= 0:
            raise ValueError("流量必须大于0")
        if H <= 0:
            raise ValueError("上游水深必须大于0")

        e = Q / (self.mu * self.b * np.sqrt(2 * self.g * H))
        return e

    def __repr__(self):
        return f"Gate(b={self.b}m, μ={self.mu}, μs={self.mu_s})"


class HydraulicJump:
    """
    水跃计算类

    水跃是从急流转为缓流的局部水力现象，伴随大量能量消耗。

    应用：
    1. 消能工设计（溢洪道、泄水建筑物）
    2. 掺气增氧（改善水质）
    3. 混合搅拌（污水处理）

    参数：
        b: 渠道宽度 (m)
        g: 重力加速度 (m/s²)，默认9.81
    """

    def __init__(self, b: float, g: float = 9.81):
        if b <= 0:
            raise ValueError("渠道宽度必须大于0")

        self.b = b
        self.g = g

    def conjugate_depth(self, h1: float, Fr1: float) -> float:
        """
        计算共轭水深（矩形断面）

        公式：h2 = h1/2 * (sqrt(1 + 8*Fr1²) - 1)

        参数：
            h1: 跃前水深（急流）(m)
            Fr1: 跃前弗劳德数

        返回：
            h2: 跃后水深（缓流）(m)
        """
        if h1 <= 0:
            raise ValueError("跃前水深必须大于0")
        if Fr1 <= 1:
            raise ValueError("水跃只能发生在急流（Fr > 1）")

        h2 = h1 / 2 * (np.sqrt(1 + 8 * Fr1**2) - 1)
        return h2

    def energy_loss(self, h1: float, h2: float) -> float:
        """
        计算水跃能量损失

        公式：ΔE = (h2 - h1)³ / (4 * h1 * h2)

        参数：
            h1: 跃前水深 (m)
            h2: 跃后水深 (m)

        返回：
            dE: 能量损失 (m)
        """
        if h1 <= 0 or h2 <= 0:
            raise ValueError("水深必须大于0")
        if h2 <= h1:
            raise ValueError("跃后水深必须大于跃前水深")

        dE = (h2 - h1)**3 / (4 * h1 * h2)
        return dE

    def energy_dissipation_ratio(self, h1: float, h2: float, Q: float) -> float:
        """
        计算消能率

        η = ΔE / E1

        参数：
            h1: 跃前水深 (m)
            h2: 跃后水深 (m)
            Q: 流量 (m³/s)

        返回：
            eta: 消能率（百分比）
        """
        # 跃前比能
        A1 = self.b * h1
        v1 = Q / A1
        E1 = h1 + v1**2 / (2*self.g)

        # 能量损失
        dE = self.energy_loss(h1, h2)

        eta = (dE / E1) * 100
        return eta

    def jump_length(self, h1: float, h2: float) -> float:
        """
        估算水跃长度

        经验公式：Lj = 6.0 * (h2 - h1)

        参数：
            h1: 跃前水深 (m)
            h2: 跃后水深 (m)

        返回：
            Lj: 水跃长度 (m)
        """
        Lj = 6.0 * (h2 - h1)
        return Lj

    def jump_type(self, Fr1: float) -> str:
        """
        根据Fr1判断水跃类型

        Fr1 < 1.7: 波状水跃
        1.7 < Fr1 < 2.5: 弱水跃
        2.5 < Fr1 < 4.5: 稳定水跃
        4.5 < Fr1 < 9.0: 强水跃
        Fr1 > 9.0: 剧烈水跃

        参数：
            Fr1: 跃前弗劳德数

        返回：
            str: 水跃类型描述
        """
        if Fr1 < 1.7:
            return "波状水跃（几乎无跃）"
        elif Fr1 < 2.5:
            return "弱水跃（水面波动小）"
        elif Fr1 < 4.5:
            return "稳定水跃（消能效果好）"
        elif Fr1 < 9.0:
            return "强水跃（水面翻滚剧烈）"
        else:
            return "剧烈水跃（严重翻滚，需防护）"

    def analyze_jump(self, Q: float, h1: float) -> Dict[str, float]:
        """
        完整的水跃分析

        参数：
            Q: 流量 (m³/s)
            h1: 跃前水深 (m)

        返回：
            dict: 包含所有水跃特征参数
        """
        # 跃前参数
        A1 = self.b * h1
        v1 = Q / A1
        Fr1 = v1 / np.sqrt(self.g * h1)
        E1 = h1 + v1**2 / (2*self.g)

        # 共轭水深
        h2 = self.conjugate_depth(h1, Fr1)

        # 跃后参数
        A2 = self.b * h2
        v2 = Q / A2
        Fr2 = v2 / np.sqrt(self.g * h2)
        E2 = h2 + v2**2 / (2*self.g)

        # 能量损失
        dE = self.energy_loss(h1, h2)
        eta = self.energy_dissipation_ratio(h1, h2, Q)

        # 水跃长度
        Lj = self.jump_length(h1, h2)

        # 水跃类型
        jump_type = self.jump_type(Fr1)

        return {
            "跃前水深_h1": h1,
            "跃前流速_v1": v1,
            "跃前Fr_Fr1": Fr1,
            "跃前比能_E1": E1,
            "跃后水深_h2": h2,
            "跃后流速_v2": v2,
            "跃后Fr_Fr2": Fr2,
            "跃后比能_E2": E2,
            "能量损失_dE": dE,
            "消能率_%": eta,
            "水跃长度_Lj": Lj,
            "水跃类型": jump_type
        }

    def __repr__(self):
        return f"HydraulicJump(b={self.b}m)"
