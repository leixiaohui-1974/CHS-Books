"""
均匀流求解器

均匀流是明渠水流中最基本的流动状态：
- 水深沿程不变
- 流速沿程不变
- 水面线平行于渠底
- 水力坡度 J = 渠底坡度 S0

基本方程：曼宁公式
Q = A * v = A * (1/n) * R^(2/3) * S0^(1/2)
"""

from typing import Dict, Optional
import numpy as np


class UniformFlowSolver:
    """
    均匀流求解器

    可以求解三类问题：
    1. 已知Q，求正常水深h0
    2. 已知h0，求流量Q
    3. 已知Q和h0，反算糙率n或坡度S0

    参数：
        channel: 渠道对象（TrapezoidalChannel等）
    """

    def __init__(self, channel):
        self.channel = channel

    def compute_normal_depth(self, Q: float) -> Dict[str, float]:
        """
        计算正常水深（已知流量）

        参数：
            Q: 流量 (m³/s)

        返回：
            dict: 包含正常水深和所有水力要素的字典
        """
        h0 = self.channel.compute_normal_depth(Q)

        # 获取所有水力要素
        results = self.channel.get_hydraulic_elements(h0)
        results["正常水深_h0"] = h0
        results["类型"] = "均匀流"

        return results

    def compute_discharge(self, h: float) -> Dict[str, float]:
        """
        计算流量（已知水深）

        参数：
            h: 水深 (m)

        返回：
            dict: 包含流量和所有水力要素的字典
        """
        Q = self.channel.discharge(h)

        results = self.channel.get_hydraulic_elements(h)
        results["类型"] = "均匀流"

        return results

    def compute_roughness(self, Q: float, h: float) -> float:
        """
        反算糙率系数（已知流量和水深）

        从曼宁公式：n = A * R^(2/3) * S0^(1/2) / Q

        参数：
            Q: 流量 (m³/s)
            h: 水深 (m)

        返回：
            n: 曼宁糙率系数
        """
        A = self.channel.area(h)
        R = self.channel.hydraulic_radius(h)
        S0 = self.channel.S0

        n = A * (R ** (2.0/3.0)) * (S0 ** 0.5) / Q
        return n

    def compute_slope(self, Q: float, h: float) -> float:
        """
        反算渠底坡度（已知流量和水深）

        从曼宁公式：S0 = (Q * n / (A * R^(2/3)))²

        参数：
            Q: 流量 (m³/s)
            h: 水深 (m)

        返回：
            S0: 渠底坡度
        """
        A = self.channel.area(h)
        R = self.channel.hydraulic_radius(h)
        n = self.channel.n

        S0 = (Q * n / (A * R ** (2.0/3.0))) ** 2
        return S0

    def analyze_flow_state(self, Q: float) -> Dict[str, any]:
        """
        分析流动状态（给定流量）

        比较正常水深和临界水深，判断流态

        参数：
            Q: 流量 (m³/s)

        返回：
            dict: 包含流态分析结果
        """
        # 计算正常水深和临界水深
        h0 = self.channel.compute_normal_depth(Q)
        hc = self.channel.compute_critical_depth(Q)

        # 计算对应的弗劳德数
        Fr_normal = self.channel.froude_number(h0)
        Fr_critical = self.channel.froude_number(hc)

        # 判断流态
        if h0 > hc:
            flow_type = "缓坡渠道 (S0 < Sc)"
            flow_state = "缓流 (Fr < 1)"
            description = "正常水深大于临界水深，渠道坡度较缓，水流为缓流状态"
        elif h0 < hc:
            flow_type = "陡坡渠道 (S0 > Sc)"
            flow_state = "急流 (Fr > 1)"
            description = "正常水深小于临界水深，渠道坡度较陡，水流为急流状态"
        else:
            flow_type = "临界坡渠道 (S0 = Sc)"
            flow_state = "临界流 (Fr = 1)"
            description = "正常水深等于临界水深，渠道为临界坡度"

        return {
            "流量_Q": Q,
            "正常水深_h0": h0,
            "临界水深_hc": hc,
            "正常流弗劳德数_Fr0": Fr_normal,
            "临界流弗劳德数_Frc": Fr_critical,
            "渠道类型": flow_type,
            "流动状态": flow_state,
            "说明": description
        }

    def plot_discharge_curve(self, h_range: Optional[tuple] = None, n_points: int = 100):
        """
        绘制流量曲线（Q-h关系）

        参数：
            h_range: 水深范围 (h_min, h_max)，默认None自动确定
            n_points: 曲线点数，默认100
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("需要安装matplotlib才能绘图: pip install matplotlib")
            return

        # 确定水深范围
        if h_range is None:
            h_max = 3.0  # 默认最大水深3m
            h_min = 0.01
        else:
            h_min, h_max = h_range

        # 生成水深序列
        h_array = np.linspace(h_min, h_max, n_points)

        # 计算对应的流量
        Q_array = np.array([self.channel.discharge(h) for h in h_array])

        # 绘图
        plt.figure(figsize=(10, 6))
        plt.plot(Q_array, h_array, 'b-', linewidth=2, label='流量曲线')
        plt.xlabel('流量 Q (m³/s)', fontsize=12)
        plt.ylabel('水深 h (m)', fontsize=12)
        plt.title(f'均匀流流量曲线\n{self.channel}', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def __repr__(self):
        return f"UniformFlowSolver(channel={self.channel})"
