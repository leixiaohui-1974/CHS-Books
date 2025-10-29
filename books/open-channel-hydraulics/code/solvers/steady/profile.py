"""
水面曲线求解器

使用标准步长法计算非均匀渐变流水面曲线

作者：CHS-Books项目
日期：2025-10-29
"""

import numpy as np
from typing import List, Tuple, Dict


class WaterSurfaceProfile:
    """
    水面曲线求解器

    使用标准步长法（Standard Step Method）计算非均匀渐变流水面线
    """

    def __init__(self, channel, Q: float, dx: float = 10.0, tol: float = 1e-6):
        """
        初始化水面曲线求解器

        参数：
            channel: 渠道对象（必须有 area, wetted_perimeter, top_width, friction_slope 方法）
            Q: 流量 (m³/s)
            dx: 步长 (m)，默认10m
            tol: 收敛容差，默认1e-6
        """
        self.channel = channel
        self.Q = Q
        self.dx = dx
        self.tol = tol
        self.g = 9.81

    def specific_energy(self, h: float) -> float:
        """
        计算比能

        E = h + v²/(2g) = h + Q²/(2gA²)
        """
        if h <= 0:
            return float('inf')

        A = self.channel.area(h)
        if A <= 0:
            return float('inf')

        E = h + self.Q**2 / (2 * self.g * A**2)
        return E

    def froude_number(self, h: float) -> float:
        """
        计算弗劳德数

        Fr = Q / (A * sqrt(g * hm))
        hm = A / B (平均水深)
        """
        if h <= 0:
            return float('inf')

        A = self.channel.area(h)
        B = self.channel.top_width(h)

        if A <= 0 or B <= 0:
            return float('inf')

        hm = A / B
        Fr = self.Q / (A * np.sqrt(self.g * hm))

        return Fr

    def friction_slope(self, h: float) -> float:
        """
        计算摩阻坡度

        Sf = n²Q² / (A²R^(4/3))
        """
        if h <= 0:
            return float('inf')

        A = self.channel.area(h)
        P = self.channel.wetted_perimeter(h)

        if A <= 0 or P <= 0:
            return float('inf')

        R = A / P
        Sf = (self.channel.n**2 * self.Q**2) / (A**2 * R**(4.0/3.0))

        return Sf

    def compute_upstream_depth(self, h1: float, dx: float) -> float:
        """
        给定下游水深h1和步长dx，计算上游水深h2

        使用能量方程：
        E2 + z2 = E1 + z1 + hf

        其中：
        z2 - z1 = S0 * dx (上游高)
        hf = Sf_avg * dx (摩阻损失)

        参数：
            h1: 下游水深 (m)
            dx: 步长 (m)

        返回：
            h2: 上游水深 (m)
        """
        # 下游断面参数
        E1 = self.specific_energy(h1)
        Sf1 = self.friction_slope(h1)

        # 初始猜测：上游水深略小于下游（壅水曲线）或略大于下游（落水曲线）
        Fr1 = self.froude_number(h1)
        if Fr1 < 1:  # 缓流，可能是壅水曲线，向上游水深减小
            h2 = h1 - 0.01
        else:  # 急流，向上游水深增大
            h2 = h1 + 0.01

        # 牛顿迭代
        for i in range(100):
            E2 = self.specific_energy(h2)
            Sf2 = self.friction_slope(h2)

            # 平均摩阻坡度
            Sf_avg = (Sf1 + Sf2) / 2

            # 能量方程
            # E2 + S0*dx = E1 + Sf_avg*dx
            # f = E2 - E1 + S0*dx - Sf_avg*dx
            f = E2 - E1 + self.channel.S0 * dx - Sf_avg * dx

            if abs(f) < self.tol:
                return h2

            # 数值导数
            dh = 1e-6
            E2_plus = self.specific_energy(h2 + dh)
            Sf2_plus = self.friction_slope(h2 + dh)
            Sf_avg_plus = (Sf1 + Sf2_plus) / 2
            f_plus = E2_plus - E1 + self.channel.S0 * dx - Sf_avg_plus * dx

            df = (f_plus - f) / dh

            if abs(df) < 1e-12:
                # 导数太小，无法迭代
                break

            h2_new = h2 - f / df

            # 限制水深范围
            if h2_new <= 0.01:
                h2_new = h2 / 2
            elif h2_new > 10 * h1:
                h2_new = h2 * 1.1

            if abs(h2_new - h2) < self.tol:
                return h2_new

            h2 = h2_new

        # 如果不收敛，返回近似值
        return h2

    def compute_profile(self, h_start: float, L: float, direction: str = 'upstream') -> Dict:
        """
        计算水面曲线

        参数：
            h_start: 起始断面水深 (m)
            L: 计算长度 (m)
            direction: 推算方向，'upstream' 或 'downstream'

        返回：
            dict: {
                'x': [距离列表],
                'h': [水深列表],
                'E': [比能列表],
                'Fr': [弗劳德数列表],
                'type': 水面曲线类型
            }
        """
        # 初始化
        x_list = [0.0]
        h_list = [h_start]
        E_list = [self.specific_energy(h_start)]
        Fr_list = [self.froude_number(h_start)]

        # 确定步长符号
        if direction == 'upstream':
            dx = self.dx
        else:
            dx = -self.dx

        # 逐步推算
        x = 0.0
        h = h_start

        while abs(x) < L:
            # 计算下一个断面的水深
            try:
                h_next = self.compute_upstream_depth(h, dx)
            except:
                # 计算失败，停止
                break

            # 检查水深合理性
            if h_next <= 0 or h_next > 100:
                break

            # 检查水深变化
            if abs(h_next - h) > 1.0:
                # 水深变化太大，减小步长重算
                dx_small = dx / 2
                try:
                    h_next = self.compute_upstream_depth(h, dx_small)
                    dx = dx_small
                except:
                    break

            # 更新
            x += dx
            h = h_next

            x_list.append(x)
            h_list.append(h)
            E_list.append(self.specific_energy(h))
            Fr_list.append(self.froude_number(h))

            # 检查是否已经接近正常水深（壅水消失）
            hn = self.channel.compute_normal_depth(self.Q)
            if abs(h - hn) < 0.05:
                # 已经恢复正常水深
                break

        # 判断水面曲线类型
        curve_type = self.classify_profile(h_start)

        # 如果是向上游推算，反转列表（使x从小到大）
        if direction == 'upstream':
            x_list = [-x for x in reversed(x_list)]
            h_list = list(reversed(h_list))
            E_list = list(reversed(E_list))
            Fr_list = list(reversed(Fr_list))

        return {
            'x': x_list,
            'h': h_list,
            'E': E_list,
            'Fr': Fr_list,
            'type': curve_type
        }

    def classify_profile(self, h_control: float) -> str:
        """
        判断水面曲线类型

        参数：
            h_control: 控制水深

        返回：
            str: 曲线类型（M1, M2, M3, S1, S2, S3, C1, C3）
        """
        # 计算正常水深和临界水深
        hn = self.channel.compute_normal_depth(self.Q)
        hc = self.channel.compute_critical_depth(self.Q)

        # 计算临界坡度
        # Sc时，hn = hc，即 Sf(hc) = S0
        Sc = self.friction_slope(hc)

        # 判断渠道类型
        if abs(self.channel.S0 - Sc) < 1e-6:
            # 临界坡
            if h_control > hc:
                return "C1 (临界坡壅水)"
            else:
                return "C3 (临界坡急流)"
        elif self.channel.S0 < Sc:
            # 缓坡 (hn > hc)
            if h_control > hn:
                return "M1 (缓坡壅水)"
            elif h_control > hc:
                return "M2 (缓坡过渡)"
            else:
                return "M3 (缓坡急流)"
        else:
            # 陡坡 (hn < hc)
            if h_control > hc:
                return "S1 (陡坡壅水)"
            elif h_control > hn:
                return "S2 (陡坡过渡)"
            else:
                return "S3 (陡坡急流)"

    def compute_backwater_length(self, h_control: float, h_threshold: float = 0.05) -> float:
        """
        计算壅水长度

        从控制断面向上游推算，直到水深接近正常水深

        参数：
            h_control: 控制断面水深 (m)
            h_threshold: 判断壅水消失的阈值 (m)，默认0.05m

        返回：
            L: 壅水长度 (m)
        """
        hn = self.channel.compute_normal_depth(self.Q)

        # 如果控制水深小于正常水深，不存在壅水
        if h_control <= hn:
            return 0.0

        # 向上游推算
        x = 0.0
        h = h_control
        dx = self.dx
        max_distance = 10000  # 最大推算距离 10km

        while x < max_distance:
            h_next = self.compute_upstream_depth(h, dx)

            if h_next <= 0:
                break

            x += dx
            h = h_next

            # 检查是否接近正常水深
            if abs(h - hn) < h_threshold:
                return x

        return x

    def __repr__(self):
        return f"WaterSurfaceProfile(Q={self.Q}m³/s, dx={self.dx}m)"
