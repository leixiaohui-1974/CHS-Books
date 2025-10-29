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


class CompoundChannel:
    """
    复式断面河道类

    断面组成：主槽（梯形）+ 左滩地 + 右滩地

    断面示意：
        |<-- bl -->|<----- bm ----->|<-- br -->|
        ___________                 ___________
       /左滩地     \               /     右滩地\
      /             \_____hm_____/             \
                      主槽

    参数：
        bm: 主槽底宽 (m)
        hm: 主槽深度（滩地高度） (m)
        m1: 主槽边坡系数（水平:垂直）
        bl: 左滩地宽度 (m)
        br: 右滩地宽度 (m)
        m2: 滩地边坡系数
        nm: 主槽糙率
        nf: 滩地糙率（左右相同）
        S0: 河床纵坡
    """

    def __init__(self, bm: float, hm: float, m1: float,
                 bl: float, br: float, m2: float,
                 nm: float, nf: float, S0: float):
        """初始化复式断面"""
        # 参数检查
        if bm <= 0:
            raise ValueError("主槽底宽必须大于0")
        if hm <= 0:
            raise ValueError("主槽深度必须大于0")
        if m1 < 0 or m2 < 0:
            raise ValueError("边坡系数不能为负")
        if bl < 0 or br < 0:
            raise ValueError("滩地宽度不能为负")
        if nm <= 0 or nf <= 0:
            raise ValueError("糙率系数必须大于0")
        if S0 <= 0:
            raise ValueError("河床坡度必须大于0")

        # 主槽参数
        self.bm = bm
        self.hm = hm
        self.m1 = m1

        # 滩地参数
        self.bl = bl
        self.br = br
        self.m2 = m2

        # 糙率
        self.nm = nm
        self.nf = nf

        # 坡度
        self.S0 = S0

        # 重力加速度
        self.g = 9.81

    def main_channel_area(self, h: float) -> float:
        """计算主槽过水面积

        当 h <= hm 时：梯形面积
        当 h > hm 时：固定为满槽面积
        """
        if h <= self.hm:
            A = (self.bm + self.m1 * h) * h
        else:
            A = (self.bm + self.m1 * self.hm) * self.hm
        return A

    def main_channel_wetted_perimeter(self, h: float) -> float:
        """计算主槽湿周"""
        if h <= self.hm:
            P = self.bm + 2 * h * np.sqrt(1 + self.m1**2)
        else:
            P = self.bm + 2 * self.hm * np.sqrt(1 + self.m1**2)
        return P

    def main_channel_top_width(self, h: float) -> float:
        """计算主槽水面宽"""
        if h <= self.hm:
            T = self.bm + 2 * self.m1 * h
        else:
            T = self.bm + 2 * self.m1 * self.hm
        return T

    def floodplain_area(self, h: float, side: str = 'left') -> float:
        """计算滩地过水面积

        Args:
            h: 总水深
            side: 'left' 或 'right'
        """
        if h <= self.hm:
            return 0.0

        hf = h - self.hm  # 漫滩深度
        b_flood = self.bl if side == 'left' else self.br

        # 矩形 + 三角形
        A = b_flood * hf + 0.5 * self.m2 * hf**2
        return A

    def floodplain_wetted_perimeter(self, h: float, side: str = 'left') -> float:
        """计算滩地湿周"""
        if h <= self.hm:
            return 0.0

        hf = h - self.hm
        b_flood = self.bl if side == 'left' else self.br

        # 底边 + 斜边（不包括与主槽的分界线）
        P = b_flood + hf * np.sqrt(1 + self.m2**2)
        return P

    def total_area(self, h: float) -> float:
        """计算总过水面积"""
        Am = self.main_channel_area(h)
        Al = self.floodplain_area(h, 'left')
        Ar = self.floodplain_area(h, 'right')
        return Am + Al + Ar

    def total_top_width(self, h: float) -> float:
        """计算总水面宽"""
        if h <= self.hm:
            return self.main_channel_top_width(h)
        else:
            hf = h - self.hm
            # 左滩 + 主槽 + 右滩
            Tl = self.bl + self.m2 * hf
            Tm = self.main_channel_top_width(h)
            Tr = self.br + self.m2 * hf
            return Tl + Tm + Tr

    def discharge_subsection(self, h: float, section: str) -> float:
        """计算各分区流量

        Args:
            h: 总水深
            section: 'main', 'left', 'right'
        """
        if section == 'main':
            A = self.main_channel_area(h)
            P = self.main_channel_wetted_perimeter(h)
            n = self.nm
        elif section == 'left':
            A = self.floodplain_area(h, 'left')
            P = self.floodplain_wetted_perimeter(h, 'left')
            n = self.nf
        elif section == 'right':
            A = self.floodplain_area(h, 'right')
            P = self.floodplain_wetted_perimeter(h, 'right')
            n = self.nf
        else:
            raise ValueError("section 必须是 'main', 'left', 或 'right'")

        if A == 0 or P == 0:
            return 0.0

        R = A / P
        Q = (1.0 / n) * A * (R ** (2.0/3.0)) * (self.S0 ** 0.5)
        return Q

    def discharge(self, h: float) -> Dict[str, float]:
        """计算总流量及各分区流量

        Returns:
            字典包含：
            - 'total': 总流量
            - 'main': 主槽流量
            - 'left': 左滩地流量
            - 'right': 右滩地流量
            - 'alpha_main': 主槽流量比
            - 'alpha_flood': 滩地流量比
        """
        Qm = self.discharge_subsection(h, 'main')
        Ql = self.discharge_subsection(h, 'left')
        Qr = self.discharge_subsection(h, 'right')
        Q_total = Qm + Ql + Qr

        # 流量分配比
        alpha_m = Qm / Q_total if Q_total > 0 else 0
        alpha_f = (Ql + Qr) / Q_total if Q_total > 0 else 0

        return {
            'total': Q_total,
            'main': Qm,
            'left': Ql,
            'right': Qr,
            'alpha_main': alpha_m,
            'alpha_flood': alpha_f
        }

    def bankfull_discharge(self) -> float:
        """计算漫滩流量（主槽满流量）"""
        return self.discharge_subsection(self.hm, 'main')

    def velocity_subsection(self, h: float, section: str) -> float:
        """计算各分区平均流速"""
        Q = self.discharge_subsection(h, section)

        if section == 'main':
            A = self.main_channel_area(h)
        elif section == 'left':
            A = self.floodplain_area(h, 'left')
        elif section == 'right':
            A = self.floodplain_area(h, 'right')
        else:
            raise ValueError("section 必须是 'main', 'left', 或 'right'")

        return Q / A if A > 0 else 0.0

    def froude_number(self, h: float, section: str = 'total') -> float:
        """计算Froude数

        Args:
            h: 水深
            section: 'total' 用总断面，'main' 用主槽
        """
        if section == 'total':
            result = self.discharge(h)
            Q = result['total']
            A = self.total_area(h)
            B = self.total_top_width(h)
        elif section == 'main':
            Q = self.discharge_subsection(h, 'main')
            A = self.main_channel_area(h)
            B = self.main_channel_top_width(h)
        else:
            raise ValueError("section 必须是 'total' 或 'main'")

        if A == 0 or B == 0:
            return 0.0

        v = Q / A
        hm = A / B  # 平均水深
        Fr = v / np.sqrt(self.g * hm)
        return Fr

    def compute_depth_from_discharge(self, Q_target: float,
                                     h_min: float = 0.1,
                                     h_max: float = 10.0,
                                     tol: float = 1e-6) -> float:
        """根据流量反算水深

        使用二分法求解
        """
        for i in range(100):
            h_mid = (h_min + h_max) / 2
            result = self.discharge(h_mid)
            Q_mid = result['total']

            if abs(Q_mid - Q_target) < tol:
                return h_mid

            if Q_mid < Q_target:
                h_min = h_mid
            else:
                h_max = h_mid

            if h_max - h_min < 1e-9:
                break

        return h_mid

    def analyze_flow(self, h: float) -> Dict:
        """全面分析流动状态

        Returns:
            包含几何、水力、流量等所有信息的字典
        """
        result = self.discharge(h)

        # 几何参数
        Am = self.main_channel_area(h)
        Al = self.floodplain_area(h, 'left')
        Ar = self.floodplain_area(h, 'right')
        A_total = self.total_area(h)

        # 流速
        vm = self.velocity_subsection(h, 'main')
        vl = self.velocity_subsection(h, 'left') if h > self.hm else 0
        vr = self.velocity_subsection(h, 'right') if h > self.hm else 0
        v_avg = result['total'] / A_total if A_total > 0 else 0

        # Froude数
        Fr_total = self.froude_number(h, 'total')
        Fr_main = self.froude_number(h, 'main') if h <= self.hm else self.froude_number(self.hm, 'main')

        # 漫滩状态
        is_overbank = h > self.hm
        overbank_depth = h - self.hm if is_overbank else 0

        return {
            'depth': h,
            'is_overbank': is_overbank,
            'overbank_depth': overbank_depth,
            'area_main': Am,
            'area_left': Al,
            'area_right': Ar,
            'area_total': A_total,
            'discharge_main': result['main'],
            'discharge_left': result['left'],
            'discharge_right': result['right'],
            'discharge_total': result['total'],
            'velocity_main': vm,
            'velocity_left': vl,
            'velocity_right': vr,
            'velocity_avg': v_avg,
            'alpha_main': result['alpha_main'],
            'alpha_flood': result['alpha_flood'],
            'froude_total': Fr_total,
            'froude_main': Fr_main,
            'top_width': self.total_top_width(h)
        }

    def __repr__(self):
        return (f"CompoundChannel(bm={self.bm}m, hm={self.hm}m, "
                f"bl={self.bl}m, br={self.br}m, nm={self.nm}, nf={self.nf})")
