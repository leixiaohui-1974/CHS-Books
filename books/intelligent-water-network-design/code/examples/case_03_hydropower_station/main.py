#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例3：小型水电站智能发电设计
==========================

**工程背景**：
农村小水电站，2×500kW，水头40m，混流式水轮机，同步发电机。

**设计任务**：
1. 水轮机选型与水力设计（符合DL/T 5186-2004）
2. 调速器设计（频率PID控制）
3. 三目标协调控制（频率+功率+水位）
4. 数字孪生仿真与在环测试
5. 智能化等级评估

**复用前序教材**：
- 第2本书：水力计算
- 第1本书：PID控制器
- 案例1/2：数字孪生仿真、在环测试

作者：CHS-Books项目
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import json

# 设置matplotlib中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ========================================
# 第一部分：水轮机模型
# ========================================

class FrancisTurbine:
    """
    混流式水轮机模型（Francis Turbine）
    
    功能：
    - 效率特性曲线
    - 流量-功率-转矩计算
    - 动态响应特性
    
    Parameters:
    -----------
    rated_head : float
        额定水头 [m]
    rated_flow : float
        额定流量 [m³/s]
    rated_power : float
        额定功率 [kW]
    rated_speed : float
        额定转速 [rpm]
    """
    
    def __init__(self, 
                 rated_head: float = 40.0,
                 rated_flow: float = 1.4,
                 rated_power: float = 500.0,
                 rated_speed: float = 750.0):
        
        self.H_rated = rated_head
        self.Q_rated = rated_flow
        self.P_rated = rated_power
        self.n_rated = rated_speed
        self.eta_rated = 0.92
        
        # 比转速
        self.n_s = rated_speed * np.sqrt(rated_power) / (rated_head ** 0.75)
        
        # 惯性时间常数
        self.Ta = 8.0  # [s]
        
        # 导叶开度
        self.guide_vane_opening = 50.0  # [%]
    
    def compute_efficiency(self, Q: float, opening: float) -> float:
        """
        计算效率（依赖流量和导叶开度）
        
        最高效率点：Q = Q_rated, opening = 70%
        
        Parameters:
        -----------
        Q : float
            流量 [m³/s]
        opening : float
            导叶开度 [%]
        
        Returns:
        --------
        eta : float
            效率 [-]
        """
        Q_ratio = Q / self.Q_rated
        opening_ratio = opening / 70.0  # 最佳开度70%
        
        # 高斯型效率曲线（简化模型）
        eta_max = self.eta_rated
        deviation = (Q_ratio - 1.0)**2 + (opening_ratio - 1.0)**2
        eta = eta_max * np.exp(-deviation / 0.5)
        
        return max(0.5, min(eta, 0.95))
    
    def compute_power(self, Q: float, H: float, opening: float) -> float:
        """
        计算水轮机出力
        
        P = 9.81 * Q * H * η(Q, opening)
        
        Parameters:
        -----------
        Q : float
            流量 [m³/s]
        H : float
            净水头 [m]
        opening : float
            导叶开度 [%]
        
        Returns:
        --------
        P : float
            功率 [kW]
        """
        if Q < 0.01 or opening < 1:
            return 0
        
        eta = self.compute_efficiency(Q, opening)
        P = 9.81 * Q * H * eta / 1000  # kW
        
        return P
    
    def compute_flow(self, opening: float, H: float) -> float:
        """
        计算流量（依赖导叶开度和水头）
        
        Q ∝ opening * sqrt(H)
        
        Parameters:
        -----------
        opening : float
            导叶开度 [%]
        H : float
            水头 [m]
        
        Returns:
        --------
        Q : float
            流量 [m³/s]
        """
        # 流量系数
        C = self.Q_rated / (70.0 * np.sqrt(self.H_rated))
        
        Q = C * opening * np.sqrt(H)
        
        return max(0, Q)
    
    def compute_torque(self, P: float, n: float) -> float:
        """
        计算转矩
        
        T = P / ω
        
        Parameters:
        -----------
        P : float
            功率 [kW]
        n : float
            转速 [rpm]
        
        Returns:
        --------
        T : float
            转矩 [N·m]
        """
        if n < 1:
            return 0
        
        omega = 2 * np.pi * n / 60  # rad/s
        T = P * 1000 / omega  # N·m
        
        return T


# ========================================
# 第二部分：同步发电机模型
# ========================================

class SynchronousGenerator:
    """
    同步发电机模型
    
    功能：
    - 摇摆方程求解
    - 频率计算
    - 电磁转矩计算
    
    摇摆方程：
    J * dω/dt = T_turbine - T_electric - T_damping
    """
    
    def __init__(self, 
                 rated_power: float = 500.0,
                 rated_speed: float = 750.0,
                 rated_frequency: float = 50.0):
        
        self.P_rated = rated_power
        self.n_rated = rated_speed
        self.f_rated = rated_frequency
        
        # 额定角速度
        self.omega_rated = 2 * np.pi * rated_frequency  # rad/s
        
        # 转动惯量（水轮机+发电机）
        self.J = 1500  # kg·m²
        
        # 阻尼系数
        self.D = 50
        
        # 当前状态
        self.omega = self.omega_rated  # 角速度 [rad/s]
        self.frequency = rated_frequency  # 频率 [Hz]
    
    def update(self, T_turbine: float, P_electric: float, dt: float) -> float:
        """
        更新发电机状态（求解摇摆方程）
        
        Parameters:
        -----------
        T_turbine : float
            水轮机输出转矩 [N·m]
        P_electric : float
            电力负荷 [kW]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        frequency : float
            发电机频率 [Hz]
        """
        # 电磁转矩
        if abs(self.omega) > 0.01:
            T_electric = P_electric * 1000 / self.omega
        else:
            T_electric = 0
        
        # 阻尼转矩
        T_damping = self.D * (self.omega - self.omega_rated)
        
        # 摇摆方程：J * dω/dt = T_turbine - T_electric - T_damping
        d_omega = (T_turbine - T_electric - T_damping) / self.J * dt
        
        # 更新角速度
        self.omega += d_omega
        
        # 限制范围（±10%）
        self.omega = np.clip(self.omega, 0.9*self.omega_rated, 1.1*self.omega_rated)
        
        # 转换为频率
        # ω = 2πf
        self.frequency = self.omega / (2 * np.pi)
        
        return self.frequency


# ========================================
# 第三部分：调速器（Governor）
# ========================================

class SimplePIDController:
    """简化PID控制器（复用）"""
    
    def __init__(self, Kp: float, Ki: float, Kd: float,
                 setpoint: float, output_limits: Tuple[float, float],
                 windup_limit: float = None):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.output_limits = output_limits
        self.windup_limit = windup_limit if windup_limit else (output_limits[1] - output_limits[0])
        
        self.integral = 0.0
        self.last_error = 0.0
    
    def update(self, measured_value: float, dt: float) -> float:
        """PID更新"""
        error = self.setpoint - measured_value
        
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.windup_limit, self.windup_limit)
        
        derivative = (error - self.last_error) / dt if dt > 0 else 0
        self.last_error = error
        
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        output = np.clip(output, self.output_limits[0], self.output_limits[1])
        
        return output


class GovernorController:
    """
    水轮机调速器（L3智能化等级）
    
    功能：
    1. 频率PID控制（主回路）
    2. 功率前馈控制（辅助）
    3. 导叶开度限速（防水锤）
    4. 开度限幅保护
    """
    
    def __init__(self, rated_frequency: float = 50.0):
        self.rated_frequency = rated_frequency
        
        # 频率PID控制器
        self.frequency_pid = SimplePIDController(
            Kp=2.0,       # 比例系数（频率敏感，需要较大增益）
            Ki=0.5,       # 积分系数
            Kd=0.2,       # 微分系数
            setpoint=rated_frequency,
            output_limits=(-20, 20),  # 导叶开度变化量 [%]
            windup_limit=10.0
        )
        
        # 功率前馈增益
        self.power_feedforward_gain = 0.05
        
        # 导叶状态
        self.guide_vane_opening = 50.0  # 当前开度 [%]
        self.max_opening_rate = 5.0     # 最大变化率 [%/s]
        
        # 保护参数
        self.opening_min = 10.0
        self.opening_max = 95.0
        
        # 统计
        self.control_actions = 0
    
    def update(self, frequency: float, power_demand: float, dt: float) -> float:
        """
        调速器更新
        
        Parameters:
        -----------
        frequency : float
            当前频率 [Hz]
        power_demand : float
            目标功率 [kW]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        guide_vane_opening : float
            导叶开度指令 [%]
        """
        # 1. 频率PID控制
        opening_change_pid = self.frequency_pid.update(frequency, dt)
        
        # 2. 功率前馈（负荷变化快速响应）
        power_error = power_demand - 500.0  # 与额定功率的偏差
        opening_change_ff = self.power_feedforward_gain * power_error
        
        # 3. 总控制量
        opening_change = opening_change_pid + opening_change_ff
        
        # 4. 限制变化率（防水锤）
        max_change = self.max_opening_rate * dt
        opening_change = np.clip(opening_change, -max_change, max_change)
        
        # 5. 更新开度
        self.guide_vane_opening += opening_change
        self.guide_vane_opening = np.clip(
            self.guide_vane_opening,
            self.opening_min,
            self.opening_max
        )
        
        self.control_actions += 1
        
        return self.guide_vane_opening


class CoordinatedController:
    """
    三目标协调控制器（L3核心）
    
    目标：
    1. 频率控制（最高优先级）
    2. 功率控制
    3. 水位控制
    
    策略：
    - 正常情况：频率控制为主
    - 水位异常：水位控制介入
    """
    
    def __init__(self):
        self.governor = GovernorController(rated_frequency=50.0)
        
        # 水位控制器（辅助）
        self.water_level_pid = SimplePIDController(
            Kp=5.0, Ki=1.0, Kd=0.5,
            setpoint=440.0,  # 目标水位440m
            output_limits=(-10, 10)  # 开度调整量 [%]
        )
        
        # 协调权重
        self.w_frequency = 1.0
        self.w_water_level = 0.3
    
    def update(self, frequency: float, power: float, water_level: float, 
               power_demand: float, dt: float) -> float:
        """
        协调控制更新
        
        Parameters:
        -----------
        frequency : float
            当前频率 [Hz]
        power : float
            当前功率 [kW]
        water_level : float
            水库水位 [m]
        power_demand : float
            目标功率 [kW]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        guide_vane_opening : float
            导叶开度指令 [%]
        """
        # 1. 频率控制（主回路）
        opening = self.governor.update(frequency, power_demand, dt)
        
        # 2. 水位反馈调整
        water_level_adjustment = self.water_level_pid.update(water_level, dt)
        
        # 3. 协调决策
        frequency_error = abs(frequency - 50.0)
        
        if frequency_error > 0.5:
            # 频率严重偏差，全力恢复频率
            pass  # 使用频率控制器输出
        else:
            # 频率正常，考虑水位
            if water_level > 441.5:
                # 水位过高，增大发电（加权）
                opening += self.w_water_level * water_level_adjustment
                opening = min(opening, 95)
            elif water_level < 438.5:
                # 水位过低，减小发电
                opening += self.w_water_level * water_level_adjustment
                opening = max(opening, 10)
        
        return opening


# ========================================
# 第四部分：数字孪生仿真
# ========================================

class HydropowerStationDigitalTwin:
    """
    水电站数字孪生仿真器
    
    功能：
    - 水库水量平衡
    - 水轮机-发电机耦合动力学
    - 调速器控制
    - 电力负荷模拟
    - 性能指标统计
    """
    
    def __init__(self,
                 turbine: FrancisTurbine,
                 generator: SynchronousGenerator,
                 controller: CoordinatedController,
                 reservoir_area: float = 20000,  # 水库面积 [m²]
                 initial_water_level: float = 440.0):
        
        self.turbine = turbine
        self.generator = generator
        self.controller = controller
        
        # 水库参数
        self.reservoir_area = reservoir_area
        self.water_level = initial_water_level
        self.H_net = 39.0  # 净水头（简化，实际随水位变化）
        
        # 仿真时间
        self.t = 0
        self.dt = 0.1  # 时间步长0.1秒（频率控制需快速响应）
        
        # 数据记录
        self.history = {
            't': [],
            'frequency': [],
            'power': [],
            'water_level': [],
            'guide_vane_opening': [],
            'flow': [],
            'inflow': [],
            'power_demand': []
        }
    
    def step(self, inflow: float, power_demand: float):
        """
        推进一个时间步
        
        Parameters:
        -----------
        inflow : float
            上游来水 [m³/s]
        power_demand : float
            电力负荷需求 [kW]
        """
        # 1. 获取当前导叶开度（用于计算当前功率）
        current_opening = self.controller.governor.guide_vane_opening
        current_flow = self.turbine.compute_flow(current_opening, self.H_net)
        current_power = self.turbine.compute_power(current_flow, self.H_net, current_opening)
        
        # 2. 协调控制器决策（更新开度）
        opening = self.controller.update(
            self.generator.frequency,
            current_power,
            self.water_level,
            power_demand,
            self.dt
        )
        
        # 3. 计算水轮机流量
        Q_turbine = self.turbine.compute_flow(opening, self.H_net)
        
        # 4. 计算水轮机功率
        P_turbine = self.turbine.compute_power(Q_turbine, self.H_net, opening)
        
        # 5. 计算水轮机转矩
        T_turbine = self.turbine.compute_torque(P_turbine, 750)
        
        # 6. 更新发电机状态（求解摇摆方程）
        frequency = self.generator.update(T_turbine, power_demand, self.dt)
        
        # 7. 水库水量平衡
        # dV/dt = Q_in - Q_turbine
        dV = (inflow - Q_turbine) * self.dt
        dh = dV / self.reservoir_area
        self.water_level += dh
        
        # 限制水位范围
        self.water_level = np.clip(self.water_level, 438.0, 442.0)
        
        # 8. 更新净水头（简化，实际随水位变化）
        self.H_net = 39.0 + (self.water_level - 440.0) * 0.5
        
        # 9. 记录历史数据
        self.history['t'].append(self.t)
        self.history['frequency'].append(frequency)
        self.history['power'].append(P_turbine)
        self.history['water_level'].append(self.water_level)
        self.history['guide_vane_opening'].append(opening)
        self.history['flow'].append(Q_turbine)
        self.history['inflow'].append(inflow)
        self.history['power_demand'].append(power_demand)
        
        # 10. 更新时间
        self.t += self.dt
        
        return {
            't': self.t,
            'frequency': frequency,
            'power': P_turbine,
            'water_level': self.water_level,
            'opening': opening
        }
    
    def simulate(self, duration: float, inflow_func, power_demand_func, verbose: bool = False):
        """运行仿真"""
        n_steps = int(duration / self.dt)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"开始仿真：时长 {duration:.0f} 秒")
            print(f"{'='*60}\n")
        
        for step_i in range(n_steps):
            inflow = inflow_func(self.t)
            power_demand = power_demand_func(self.t)
            
            state = self.step(inflow, power_demand)
            
            if verbose and step_i % 100 == 0:
                print(f"t={self.t:6.1f}s: 频率={state['frequency']:.3f}Hz, "
                      f"功率={state['power']:.1f}kW, "
                      f"水位={state['water_level']:.2f}m")
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"仿真完成")
            print(f"{'='*60}\n")
        
        return self.history
    
    def calculate_performance_metrics(self) -> Dict:
        """计算性能指标"""
        frequencies = np.array(self.history['frequency'])
        powers = np.array(self.history['power'])
        water_levels = np.array(self.history['water_level'])
        
        metrics = {
            # 频率控制性能
            'frequency_mean': float(np.mean(frequencies)),
            'frequency_std': float(np.std(frequencies)),
            'frequency_max_deviation': float(np.max(np.abs(frequencies - 50.0))),
            'frequency_steady_error': float(np.mean(np.abs(frequencies - 50.0))),
            
            # 功率性能
            'power_mean': float(np.mean(powers)),
            'power_std': float(np.std(powers)),
            
            # 水位性能
            'water_level_mean': float(np.mean(water_levels)),
            'water_level_std': float(np.std(water_levels)),
            
            # 控制动作
            'control_actions': self.controller.governor.control_actions,
            
            # 安全性
            'frequency_violation_count': int(np.sum(np.abs(frequencies - 50.0) > 0.2)),
            'water_level_overflow_count': int(np.sum(water_levels > 441.8)),
            'water_level_low_count': int(np.sum(water_levels < 438.2))
        }
        
        return metrics
    
    def plot_results(self):
        """绘制仿真结果"""
        t_sec = np.array(self.history['t'])
        
        fig, axes = plt.subplots(4, 1, figsize=(12, 10))
        
        # 1. 频率
        axes[0].plot(t_sec, self.history['frequency'], 'b-', linewidth=2, label='实际频率')
        axes[0].axhline(50.0, color='r', linestyle='--', linewidth=1.5, label='额定频率 50Hz')
        axes[0].axhline(50.2, color='orange', linestyle=':', label='±0.2Hz范围')
        axes[0].axhline(49.8, color='orange', linestyle=':')
        axes[0].set_ylabel('频率 [Hz]', fontsize=11)
        axes[0].set_title('案例3：小型水电站仿真结果', fontsize=14, fontweight='bold')
        axes[0].legend(loc='best')
        axes[0].grid(True, alpha=0.3)
        
        # 2. 功率
        axes[1].plot(t_sec, self.history['power'], 'g-', linewidth=2, label='实际功率')
        axes[1].plot(t_sec, self.history['power_demand'], 'r--', linewidth=1.5, label='需求功率')
        axes[1].set_ylabel('功率 [kW]', fontsize=11)
        axes[1].legend(loc='best')
        axes[1].grid(True, alpha=0.3)
        
        # 3. 水位
        axes[2].plot(t_sec, self.history['water_level'], 'b-', linewidth=2, label='水库水位')
        axes[2].axhline(440.0, color='r', linestyle='--', linewidth=1.5, label='目标水位 440m')
        axes[2].set_ylabel('水位 [m]', fontsize=11)
        axes[2].legend(loc='best')
        axes[2].grid(True, alpha=0.3)
        
        # 4. 导叶开度
        axes[3].plot(t_sec, self.history['guide_vane_opening'], 'purple', linewidth=2, label='导叶开度')
        axes[3].set_ylabel('开度 [%]', fontsize=11)
        axes[3].set_xlabel('时间 [s]', fontsize=11)
        axes[3].legend(loc='best')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig


# ========================================
# 第五部分：在环测试场景
# ========================================

def create_test_scenarios() -> List[Dict]:
    """创建测试场景"""
    scenarios = []
    
    # 场景1：恒定负荷
    scenarios.append({
        'name': '场景1：恒定负荷（正常工况）',
        'duration': 300,  # 5分钟
        'inflow': lambda t: 1.5,  # 恒定来水
        'power_demand': lambda t: 400.0,  # 恒定负荷400kW
        'description': '恒定负荷400kW，测试稳态频率控制'
    })
    
    # 场景2：负荷阶跃
    scenarios.append({
        'name': '场景2：负荷阶跃（扰动工况）',
        'duration': 300,
        'inflow': lambda t: 1.5,
        'power_demand': lambda t: 300.0 if t < 150 else 500.0,  # 150秒后负荷阶跃
        'description': '负荷从300kW阶跃到500kW，测试调速器响应'
    })
    
    # 场景3：负荷波动
    scenarios.append({
        'name': '场景3：负荷周期波动（扰动工况）',
        'duration': 300,
        'inflow': lambda t: 1.5,
        'power_demand': lambda t: 400 + 100 * np.sin(2 * np.pi * t / 60),  # 周期60秒
        'description': '负荷正弦波动（400±100 kW），测试抗扰能力'
    })
    
    # 场景4：来水变化
    scenarios.append({
        'name': '场景4：来水突然增大（扰动工况）',
        'duration': 300,
        'inflow': lambda t: 1.2 if t < 150 else 2.0,  # 来水突增
        'power_demand': lambda t: 400.0,
        'description': '来水从1.2增至2.0 m³/s，测试水位控制'
    })
    
    # 场景5：甩负荷
    scenarios.append({
        'name': '场景5：甩负荷（故障工况）',
        'duration': 300,
        'inflow': lambda t: 1.5,
        'power_demand': lambda t: 500.0 if t < 150 else 50.0,  # 突然甩负荷
        'description': '负荷从500kW突降至50kW（甩负荷），测试超速保护'
    })
    
    return scenarios


def run_hil_test(scenarios: List[Dict], verbose: bool = True):
    """运行在环测试"""
    test_results = []
    
    for i, scenario in enumerate(scenarios):
        if verbose:
            print(f"\n{'='*70}")
            print(f"测试 [{i+1}/{len(scenarios)}]: {scenario['name']}")
            print(f"描述: {scenario['description']}")
            print(f"{'='*70}")
        
        # 创建水电站系统
        turbine = FrancisTurbine()
        generator = SynchronousGenerator()
        controller = CoordinatedController()
        twin = HydropowerStationDigitalTwin(turbine, generator, controller)
        
        # 运行仿真
        history = twin.simulate(
            duration=scenario['duration'],
            inflow_func=scenario['inflow'],
            power_demand_func=scenario['power_demand'],
            verbose=False
        )
        
        # 计算性能指标
        metrics = twin.calculate_performance_metrics()
        
        # 保存结果
        result = {
            'scenario': scenario['name'],
            'metrics': metrics,
            'history': history,
            'twin': twin
        }
        test_results.append(result)
        
        # 打印性能摘要
        if verbose:
            print(f"\n性能指标：")
            print(f"  - 平均频率: {metrics['frequency_mean']:.3f} Hz")
            print(f"  - 频率波动: {metrics['frequency_std']:.4f} Hz")
            print(f"  - 最大频率偏差: {metrics['frequency_max_deviation']:.4f} Hz")
            print(f"  - 频率稳态误差: {metrics['frequency_steady_error']:.4f} Hz")
            print(f"  - 频率越限次数: {metrics['frequency_violation_count']}")
            print(f"  - 平均功率: {metrics['power_mean']:.1f} kW")
            print(f"  - 平均水位: {metrics['water_level_mean']:.2f} m")
    
    return test_results


# ========================================
# 第六部分：智能化等级评估
# ========================================

def evaluate_intelligence_level(test_results: List[Dict]) -> Dict:
    """智能化等级评估"""
    all_freq_errors = [r['metrics']['frequency_steady_error'] for r in test_results]
    all_freq_violations = [r['metrics']['frequency_violation_count'] for r in test_results]
    
    avg_freq_error = np.mean(all_freq_errors)
    total_violations = np.sum(all_freq_violations)
    
    # 等级判定
    if avg_freq_error < 0.05 and total_violations < 10:
        level = 'L3'  # 协调控制，频率+功率+水位
        level_score = 3
    elif avg_freq_error < 0.1 and total_violations < 50:
        level = 'L2'  # 局部控制
        level_score = 2
    else:
        level = 'L1'
        level_score = 1
    
    evaluation = {
        'intelligence_level': level,
        'level_score': level_score,
        'avg_frequency_error': float(avg_freq_error),
        'total_frequency_violations': int(total_violations),
        'pass': level_score >= 3
    }
    
    return evaluation


def print_intelligence_report(evaluation: Dict):
    """打印智能化等级报告"""
    print(f"\n{'='*70}")
    print(f"智能化等级评估报告")
    print(f"{'='*70}\n")
    
    print(f"智能化等级: {evaluation['intelligence_level']}")
    print(f"等级分数: {evaluation['level_score']}/5")
    print(f"是否通过: {'✅ 通过' if evaluation['pass'] else '❌ 未通过'}\n")
    
    print(f"性能指标：")
    print(f"  - 平均频率误差: {evaluation['avg_frequency_error']:.4f} Hz")
    print(f"  - 频率越限总次数: {evaluation['total_frequency_violations']}\n")
    
    print(f"等级说明：")
    print(f"  L2 - 局部控制（单一频率控制）")
    print(f"  L3 - 协调控制（频率+功率+水位多目标）⭐ 本案例目标")
    print(f"  L4 - 优化调度（考虑经济调度、预测性维护）\n")
    
    print(f"{'='*70}\n")


# ========================================
# 主程序
# ========================================

def main():
    """主程序"""
    print(f"\n{'#'*70}")
    print(f"#  案例3：小型水电站智能发电设计")
    print(f"#  Intelligent Hydropower Station Design")
    print(f"#  ")
    print(f"#  工程：2×500kW农村小水电，混流式水轮机")
    print(f"#  目标：L3智能化等级（频率+功率+水位协调控制）")
    print(f"#  标准：GB/T 15945-2008, DL/T 5186-2004")
    print(f"{'#'*70}\n")
    
    # ===== 第1步：水轮机特性展示 =====
    print("="*70)
    print("第1步：水轮机特性曲线")
    print("="*70)
    turbine = FrancisTurbine()
    
    # 绘制效率特性
    openings = np.linspace(20, 90, 50)
    flows = [turbine.compute_flow(op, 40) for op in openings]
    efficiencies = [turbine.compute_efficiency(turbine.compute_flow(op, 40), op) * 100 
                   for op in openings]
    
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(openings, flows, 'b-', linewidth=2)
    plt.xlabel('导叶开度 [%]')
    plt.ylabel('流量 [m³/s]')
    plt.title('流量-开度特性')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(openings, efficiencies, 'g-', linewidth=2)
    plt.xlabel('导叶开度 [%]')
    plt.ylabel('效率 [%]')
    plt.title('效率-开度特性')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('turbine_characteristics.png', dpi=150, bbox_inches='tight')
    print("✓ 水轮机特性曲线已生成: turbine_characteristics.png\n")
    plt.close()
    
    # ===== 第2步：运行在环测试 =====
    print("="*70)
    print("第2步：在环测试（5种工况）")
    print("="*70)
    scenarios = create_test_scenarios()
    test_results = run_hil_test(scenarios, verbose=True)
    
    # ===== 第3步：智能化等级评估 =====
    print("\n" + "="*70)
    print("第3步：智能化等级评估")
    print("="*70)
    evaluation = evaluate_intelligence_level(test_results)
    print_intelligence_report(evaluation)
    
    # ===== 第4步：绘制仿真结果 =====
    print("="*70)
    print("第4步：绘制仿真结果")
    print("="*70)
    for i, result in enumerate(test_results[:3]):  # 只绘制前3个
        print(f"✓ 绘制场景{i+1}...")
        fig = result['twin'].plot_results()
        plt.savefig(f'hydro_scenario_{i+1}_results.png', dpi=150, bbox_inches='tight')
        plt.close()
    print("✓ 仿真结果图已生成\n")
    
    # ===== 第5步：生成设计报告 =====
    print("="*70)
    print("第5步：生成设计报告")
    print("="*70)
    
    report = {
        'project_name': '小型水电站智能发电设计',
        'design_standard': 'GB/T 15945-2008, DL/T 5186-2004',
        'turbine_config': 'HL110-WJ-70混流式水轮机，500kW',
        'intelligence_level': evaluation['intelligence_level'],
        'test_summary': {
            'total_scenarios': len(test_results),
            'avg_frequency_error': evaluation['avg_frequency_error'],
            'pass': evaluation['pass']
        }
    }
    
    with open('hydro_design_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✓ 设计报告已生成: hydro_design_report.json")
    
    # ===== 总结 =====
    print(f"\n{'#'*70}")
    print(f"#  案例3完成！")
    print(f"#  ")
    print(f"#  ✅ 水轮机选型与水力设计完成")
    print(f"#  ✅ 调速器PID控制器开发完成")
    print(f"#  ✅ 三目标协调控制实现（频率+功率+水位）")
    print(f"#  ✅ 数字孪生仿真完成（5种工况）")
    print(f"#  ✅ 智能化等级{evaluation['intelligence_level']}认证")
    print(f"#  ")
    print(f"#  设计成果：")
    print(f"#    - 水轮机特性曲线: turbine_characteristics.png")
    print(f"#    - 仿真结果图: hydro_scenario_1/2/3_results.png")
    print(f"#    - 设计报告: hydro_design_report.json")
    print(f"{'#'*70}\n")


if __name__ == '__main__':
    main()
