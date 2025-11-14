#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例1: 灌区智能闸站优化设计 (L2智能化等级)
=============================================

本案例演示灌溉闸门的自动控制和数字孪生技术。
复用前序教材成果，实现1条干渠+10条支渠的智能调配。

核心功能:
1. PID控制器实现水位自动调节
2. 梯形渠道水力学模型
3. 数字孪生实时仿真
4. 智能化等级L2评估

作者: CHS-Books项目
日期: 2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict
import sys
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SimplePIDController:
    """简单PID控制器

    实现比例-积分-微分控制算法，用于闸门开度调节。
    """

    def __init__(self, Kp: float, Ki: float, Kd: float,
                 setpoint: float, output_limits: Tuple[float, float] = (0, 1)):
        """初始化PID控制器

        Args:
            Kp: 比例增益
            Ki: 积分增益
            Kd: 微分增益
            setpoint: 目标设定值
            output_limits: 输出限幅范围 (min, max)
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.output_limits = output_limits

        # 状态变量
        self.integral = 0.0
        self.previous_error = 0.0
        self.windup_limit = 10.0  # 积分饱和限制

    def update(self, measured_value: float, dt: float) -> float:
        """更新控制器输出

        Args:
            measured_value: 当前测量值
            dt: 时间步长

        Returns:
            控制输出（闸门开度）
        """
        # 计算误差
        error = self.setpoint - measured_value

        # 比例项
        P = self.Kp * error

        # 积分项（带抗饱和）
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.windup_limit, self.windup_limit)
        I = self.Ki * self.integral

        # 微分项
        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0
        D = self.Kd * derivative

        # 计算输出
        output = P + I + D

        # 限幅
        output = np.clip(output, self.output_limits[0], self.output_limits[1])

        # 更新状态
        self.previous_error = error

        return output

    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.previous_error = 0.0


class TrapezoidalChannel:
    """梯形渠道水力学模型

    使用Manning公式计算明渠非恒定流。
    """

    def __init__(self, bottom_width: float, side_slope: float,
                 slope: float, roughness: float, length: float):
        """初始化渠道参数

        Args:
            bottom_width: 底宽 (m)
            side_slope: 边坡系数 (m=1表示1:1)
            slope: 纵坡 (i)
            roughness: 糙率 (n)
            length: 渠道长度 (m)
        """
        self.b = bottom_width
        self.m = side_slope
        self.i = slope
        self.n = roughness
        self.L = length

    def compute_flow_area(self, h: float) -> float:
        """计算过流面积

        Args:
            h: 水深 (m)

        Returns:
            过流面积 (m²)
        """
        return (self.b + self.m * h) * h

    def compute_wetted_perimeter(self, h: float) -> float:
        """计算湿周

        Args:
            h: 水深 (m)

        Returns:
            湿周 (m)
        """
        return self.b + 2 * h * np.sqrt(1 + self.m**2)

    def compute_hydraulic_radius(self, h: float) -> float:
        """计算水力半径

        Args:
            h: 水深 (m)

        Returns:
            水力半径 (m)
        """
        A = self.compute_flow_area(h)
        P = self.compute_wetted_perimeter(h)
        return A / P if P > 0 else 0.0

    def compute_velocity(self, h: float) -> float:
        """使用Manning公式计算流速

        Args:
            h: 水深 (m)

        Returns:
            流速 (m/s)
        """
        if h <= 0.01:  # 最小水深限制
            return 0.0

        R = self.compute_hydraulic_radius(h)
        v = (1.0 / self.n) * (R ** (2.0/3.0)) * (self.i ** 0.5)
        return v

    def compute_discharge(self, h: float) -> float:
        """计算流量

        Args:
            h: 水深 (m)

        Returns:
            流量 (m³/s)
        """
        A = self.compute_flow_area(h)
        v = self.compute_velocity(h)
        return A * v


class IrrigationGateDigitalTwin:
    """灌溉闸站数字孪生

    实现1条干渠+10条支渠的水力学耦合和闸门控制。
    """

    def __init__(self, main_channel_params: Dict, branch_params: Dict):
        """初始化数字孪生

        Args:
            main_channel_params: 干渠参数字典
            branch_params: 支渠参数字典
        """
        # 创建干渠模型
        self.main_channel = TrapezoidalChannel(**main_channel_params)

        # 创建支渠模型（10条）
        self.branches = []
        for i in range(10):
            self.branches.append(TrapezoidalChannel(**branch_params))

        # 闸门状态（开度: 0-1）
        self.gate_openings = np.ones(10) * 0.5

        # 水位状态
        self.main_water_level = 2.5  # m
        self.branch_water_levels = np.ones(10) * 2.0  # m

        # PID控制器
        self.controllers = []
        for i in range(10):
            self.controllers.append(
                SimplePIDController(
                    Kp=0.5, Ki=0.1, Kd=0.05,
                    setpoint=2.0,  # 目标水位2m
                    output_limits=(0.2, 1.0)
                )
            )

    def step(self, dt: float, inflow: float, demands: np.ndarray):
        """单步仿真

        Args:
            dt: 时间步长 (s)
            inflow: 干渠入流 (m³/s)
            demands: 各支渠需水量 (m³/s), shape=(10,)
        """
        # 1. 更新干渠水位
        Q_main = self.main_channel.compute_discharge(self.main_water_level)
        Q_out = np.sum([self.branches[i].compute_discharge(self.branch_water_levels[i]) *
                        self.gate_openings[i] for i in range(10)])

        dh_main = (inflow - Q_out) * dt / (self.main_channel.L * self.main_channel.b)
        self.main_water_level += dh_main
        self.main_water_level = np.clip(self.main_water_level, 0.5, 4.0)

        # 2. 更新各支渠水位和闸门开度
        for i in range(10):
            # PID控制闸门开度
            self.gate_openings[i] = self.controllers[i].update(
                measured_value=self.branch_water_levels[i],
                dt=dt
            )

            # 计算支渠流量
            Q_in_branch = self.branches[i].compute_discharge(self.main_water_level) * \
                         self.gate_openings[i]
            Q_out_branch = demands[i]

            # 更新支渠水位
            dh_branch = (Q_in_branch - Q_out_branch) * dt / \
                       (self.branches[i].L * self.branches[i].b)
            self.branch_water_levels[i] += dh_branch
            self.branch_water_levels[i] = np.clip(self.branch_water_levels[i], 0.2, 3.0)

    def compute_performance_metrics(self, target_levels: np.ndarray) -> Dict:
        """计算性能指标

        Args:
            target_levels: 目标水位数组 (m), shape=(10,)

        Returns:
            性能指标字典
        """
        errors = self.branch_water_levels - target_levels

        mae = np.mean(np.abs(errors))  # 平均绝对误差
        rmse = np.sqrt(np.mean(errors**2))  # 均方根误差
        max_error = np.max(np.abs(errors))  # 最大误差

        # 配水均匀度 (Christiansen均匀系数)
        mean_level = np.mean(self.branch_water_levels)
        cu = 100 * (1 - np.sum(np.abs(self.branch_water_levels - mean_level)) /
                    (10 * mean_level))

        return {
            'MAE': mae,
            'RMSE': rmse,
            'Max_Error': max_error,
            'Uniformity': cu
        }


def evaluate_intelligence_level(performance: Dict) -> Tuple[str, int]:
    """评估智能化等级

    根据性能指标判断系统智能化水平。
    参考自动驾驶分级标准(L0-L5)。

    Args:
        performance: 性能指标字典

    Returns:
        (等级名称, 等级数值)
    """
    uniformity = performance['Uniformity']
    mae = performance['MAE']

    if uniformity > 95 and mae < 0.05:
        return "L5-完全自主", 5
    elif uniformity > 90 and mae < 0.10:
        return "L4-高度自动化", 4
    elif uniformity > 85 and mae < 0.15:
        return "L3-有条件自动化", 3
    elif uniformity > 80 and mae < 0.20:
        return "L2-部分自动化", 2
    elif uniformity > 70 and mae < 0.30:
        return "L1-辅助驾驶", 1
    else:
        return "L0-无自动化", 0


def demonstrate_irrigation_gate():
    """演示灌溉闸站控制"""
    print("=" * 70)
    print("案例1: 灌区智能闸站优化设计")
    print("=" * 70)

    # 参数设置
    main_params = {
        'bottom_width': 5.0,
        'side_slope': 1.5,
        'slope': 0.0002,
        'roughness': 0.025,
        'length': 1000.0
    }

    branch_params = {
        'bottom_width': 2.0,
        'side_slope': 1.0,
        'slope': 0.0003,
        'roughness': 0.025,
        'length': 500.0
    }

    # 创建数字孪生
    twin = IrrigationGateDigitalTwin(main_params, branch_params)

    # 仿真参数
    dt = 60.0  # 时间步长60秒
    total_time = 3600.0 * 24  # 仿真24小时
    steps = int(total_time / dt)

    # 记录数据
    time_history = []
    main_level_history = []
    branch_level_history = [[] for _ in range(10)]
    gate_opening_history = [[] for _ in range(10)]

    # 目标水位
    target_levels = np.ones(10) * 2.0

    # 仿真循环
    print(f"\n开始仿真 (时长={total_time/3600:.1f}小时, 步长={dt}秒)")

    for step in range(steps):
        t = step * dt

        # 干渠入流（模拟日变化）
        inflow = 10.0 + 3.0 * np.sin(2 * np.pi * t / 86400.0)

        # 各支渠需水量（模拟灌溉需求变化）
        demands = np.ones(10) * 0.8 + 0.2 * np.random.randn(10)
        demands = np.clip(demands, 0.3, 1.5)

        # 执行仿真步
        twin.step(dt, inflow, demands)

        # 记录数据
        if step % 10 == 0:  # 每10步记录一次
            time_history.append(t / 3600.0)  # 转换为小时
            main_level_history.append(twin.main_water_level)
            for i in range(10):
                branch_level_history[i].append(twin.branch_water_levels[i])
                gate_opening_history[i].append(twin.gate_openings[i])

    # 计算性能指标
    performance = twin.compute_performance_metrics(target_levels)

    print("\n性能指标:")
    print(f"  平均绝对误差(MAE): {performance['MAE']:.4f} m")
    print(f"  均方根误差(RMSE): {performance['RMSE']:.4f} m")
    print(f"  最大误差: {performance['Max_Error']:.4f} m")
    print(f"  配水均匀度: {performance['Uniformity']:.2f}%")

    # 智能化等级评估
    level_name, level_value = evaluate_intelligence_level(performance)
    print(f"\n智能化等级: {level_name} (L{level_value})")

    # 可视化结果
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # 子图1: 干渠水位
    axes[0].plot(time_history, main_level_history, 'b-', linewidth=2)
    axes[0].set_xlabel('时间 (小时)')
    axes[0].set_ylabel('干渠水位 (m)')
    axes[0].set_title('干渠水位变化')
    axes[0].grid(True, alpha=0.3)

    # 子图2: 支渠水位
    for i in range(10):
        axes[1].plot(time_history, branch_level_history[i],
                    alpha=0.6, label=f'支渠{i+1}')
    axes[1].axhline(y=2.0, color='r', linestyle='--', linewidth=2, label='目标水位')
    axes[1].set_xlabel('时间 (小时)')
    axes[1].set_ylabel('支渠水位 (m)')
    axes[1].set_title('支渠水位控制效果')
    axes[1].legend(ncol=6, fontsize=8)
    axes[1].grid(True, alpha=0.3)

    # 子图3: 闸门开度
    for i in range(10):
        axes[2].plot(time_history, gate_opening_history[i],
                    alpha=0.6, label=f'闸门{i+1}')
    axes[2].set_xlabel('时间 (小时)')
    axes[2].set_ylabel('闸门开度')
    axes[2].set_title('闸门开度调节')
    axes[2].legend(ncol=6, fontsize=8)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存图片
    output_dir = Path(__file__).parent
    plt.savefig(output_dir / 'irrigation_gate_control.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存: {output_dir / 'irrigation_gate_control.png'}")

    plt.show()

    print("\n" + "=" * 70)
    print("仿真完成!")
    print("=" * 70)

    return twin, performance


if __name__ == "__main__":
    # 运行演示
    twin, performance = demonstrate_irrigation_gate()
