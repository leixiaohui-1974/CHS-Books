#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
案例19: 渠道-管道耦合系统（Coupled Canal-Pipeline System）

本案例演示明渠与压力管道的耦合建模、仿真与协调控制，涵盖：
1. 渠道Saint-Venant方程 + Preissmann隐式格式
2. 管道水锤方程 + MOC特征线法
3. 耦合边界条件处理（流量连续性、水头关系）
4. 分层协调控制策略

Author: AI Assistant
Date: 2025-10-30
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from scipy.linalg import solve_banded
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ==================== 第一部分：渠道模型（Preissmann格式） ====================

class CanalParameters:
    """渠道参数类"""
    def __init__(self, L=5000, B=10.0, S0=0.0001, n=0.025, h0=2.0, Q0=20.0):
        """
        Args:
            L: 渠道长度 [m]
            B: 渠道底宽 [m]
            S0: 底坡 [-]
            n: Manning糙率系数 [-]
            h0: 初始水深 [m]
            Q0: 初始流量 [m³/s]
        """
        self.L = L
        self.B = B
        self.S0 = S0
        self.n = n
        self.h0 = h0
        self.Q0 = Q0
        self.g = 9.81  # 重力加速度 [m/s²]

    def compute_area(self, h):
        """计算过水断面面积（矩形断面）"""
        return self.B * h

    def compute_perimeter(self, h):
        """计算湿周"""
        return self.B + 2 * h

    def compute_hydraulic_radius(self, h):
        """计算水力半径"""
        A = self.compute_area(h)
        P = self.compute_perimeter(h)
        return A / P if P > 0 else 0

    def compute_friction_slope(self, h, Q):
        """计算摩阻坡度（Manning公式）"""
        A = self.compute_area(h)
        R = self.compute_hydraulic_radius(h)
        if A < 1e-6 or R < 1e-6:
            return 0
        V = Q / A
        Sf = (self.n * V)**2 / R**(4/3)
        return Sf


class CanalSimulator:
    """渠道显式仿真器（简化Lax-Wendroff格式）

    求解Saint-Venant方程组：
    ∂A/∂t + ∂Q/∂x = 0  (连续性方程)
    ∂Q/∂t + ∂(Q²/A)/∂x + gA∂h/∂x = gA(S0 - Sf)  (动量方程)
    """
    def __init__(self, params, dx=200, dt=10):
        """
        Args:
            params: 渠道参数对象
            dx: 空间步长 [m]
            dt: 时间步长 [s]
        """
        self.params = params
        self.dx = dx
        self.dt = dt

        # 空间离散
        self.N = int(params.L / dx) + 1
        self.x = np.linspace(0, params.L, self.N)

        # 初始化状态变量
        self.h = np.ones(self.N) * params.h0  # 水深 [m]
        self.Q = np.ones(self.N) * params.Q0  # 流量 [m³/s]

        # 边界条件
        self.upstream_Q = params.Q0  # 上游流量
        self.downstream_h = params.h0  # 下游水深

    def step(self):
        """单步仿真（显式差分格式）"""
        N = self.N
        dt = self.dt
        dx = self.dx
        params = self.params

        h_new = np.zeros(N)
        Q_new = np.zeros(N)

        # 内部节点（简化的Lax-Wendroff格式）
        for i in range(1, N-1):
            # 计算当前节点的通量
            A_i = params.compute_area(self.h[i])
            Sf_i = params.compute_friction_slope(self.h[i], self.Q[i])

            # 连续性方程：dh/dt = -(1/B) * dQ/dx
            dQ_dx = (self.Q[i+1] - self.Q[i-1]) / (2 * dx)
            dh_dt = -dQ_dx / params.B

            # 动量方程：dQ/dt = -d(Q²/A)/dx - gA*dh/dx + gA(S0 - Sf)
            if A_i > 1e-6:
                A_ip1 = params.compute_area(self.h[i+1])
                A_im1 = params.compute_area(self.h[i-1])
                dQQ_A_dx = (self.Q[i+1]**2/A_ip1 - self.Q[i-1]**2/A_im1) / (2 * dx)
            else:
                dQQ_A_dx = 0

            dh_dx = (self.h[i+1] - self.h[i-1]) / (2 * dx)
            dQ_dt = -dQQ_A_dx - params.g * A_i * dh_dx + params.g * A_i * (params.S0 - Sf_i)

            # 显式更新
            h_new[i] = self.h[i] + dt * dh_dt
            Q_new[i] = self.Q[i] + dt * dQ_dt

            # 物理约束
            h_new[i] = max(0.1, min(h_new[i], 10.0))
            Q_new[i] = max(-100, min(Q_new[i], 100.0))

        # 上游边界条件（给定流量）
        Q_new[0] = self.upstream_Q
        # 从连续性方程推算上游水深
        dQ_dx_0 = (self.Q[1] - self.Q[0]) / dx
        h_new[0] = self.h[0] - dt * dQ_dx_0 / params.B
        h_new[0] = max(0.1, min(h_new[0], 10.0))

        # 下游边界条件（给定水深）
        h_new[-1] = self.downstream_h
        # 从动量方程推算下游流量
        A_nm1 = params.compute_area(self.h[-2])
        Sf_nm1 = params.compute_friction_slope(self.h[-2], self.Q[-2])
        if A_nm1 > 1e-6:
            dQQ_A_dx_nm1 = (self.Q[-1]**2/params.compute_area(self.h[-1]) -
                           self.Q[-2]**2/A_nm1) / dx
        else:
            dQQ_A_dx_nm1 = 0
        dh_dx_nm1 = (self.h[-1] - self.h[-2]) / dx
        dQ_dt_nm1 = -dQQ_A_dx_nm1 - params.g * A_nm1 * dh_dx_nm1 + \
                    params.g * A_nm1 * (params.S0 - Sf_nm1)
        Q_new[-1] = self.Q[-1] + dt * dQ_dt_nm1
        Q_new[-1] = max(-100, min(Q_new[-1], 100.0))

        self.h = h_new
        self.Q = Q_new

    def set_upstream_flow(self, Q):
        """设置上游流量边界条件"""
        self.upstream_Q = Q

    def set_downstream_depth(self, h):
        """设置下游水深边界条件"""
        self.downstream_h = h


# ==================== 第二部分：管道模型（MOC特征线法） ====================

class PipelineParameters:
    """管道参数类"""
    def __init__(self, L=1000, D=0.8, e=0.01, E=2e11, K=2.2e9,
                 rho=1000, f=0.02, H_inlet=20.0, Q0=1.0):
        """
        Args:
            L: 管道长度 [m]
            D: 管道内径 [m]
            e: 管壁厚度 [m]
            E: 管壁弹性模量 [Pa]
            K: 水的体积弹性模量 [Pa]
            rho: 水密度 [kg/m³]
            f: Darcy-Weisbach摩阻系数 [-]
            H_inlet: 入口水头 [m]
            Q0: 初始流量 [m³/s]
        """
        self.L = L
        self.D = D
        self.e = e
        self.E = E
        self.K = K
        self.rho = rho
        self.f = f
        self.H_inlet = H_inlet
        self.Q0 = Q0
        self.g = 9.81

        # 计算导出参数
        self.A = np.pi * D**2 / 4  # 管道面积
        self.V0 = Q0 / self.A  # 初始流速
        self.a = self._compute_wave_speed()  # 水锤波速
        self.phase = 2 * L / self.a  # 相位周期

    def _compute_wave_speed(self):
        """计算水锤波速"""
        a = np.sqrt(self.K / self.rho) / \
            np.sqrt(1 + (self.K * self.D) / (self.E * self.e))
        return a


class PipelineMOCSimulator:
    """管道MOC特征线仿真器

    求解水锤方程：
    ∂H/∂t + (a²/gA)∂Q/∂x + (f/2DA)|Q|Q = 0  (连续性)
    ∂Q/∂t + gA∂H/∂x + (f/2D)|Q|Q = 0  (动量)
    """
    def __init__(self, params, dx=None, dt=None):
        """
        Args:
            params: 管道参数对象
            dx: 空间步长 [m]，若None则自动选择
            dt: 时间步长 [s]，若None则根据Courant条件确定
        """
        self.params = params

        # 自动选择空间步长（保证整数分段）
        if dx is None:
            self.N = 20  # 默认分段数
            self.dx = params.L / self.N
        else:
            self.N = int(params.L / dx)
            self.dx = params.L / self.N

        # Courant条件：dt = dx / a
        if dt is None:
            self.dt = self.dx / params.a
        else:
            self.dt = dt

        self.x = np.linspace(0, params.L, self.N + 1)

        # 初始化状态变量
        self.H = np.ones(self.N + 1) * params.H_inlet  # 测压管水头 [m]
        self.Q = np.ones(self.N + 1) * params.Q0  # 流量 [m³/s]

        # MOC系数
        self.B = params.a / (params.g * params.A)
        self.R = params.f * self.dt / (2 * params.D * params.A)

        # 边界条件
        self.inlet_H = params.H_inlet  # 入口恒定水头
        self.outlet_valve_opening = 1.0  # 出口阀门开度

    def step(self):
        """单步仿真（MOC特征线法）"""
        H_new = np.zeros_like(self.H)
        Q_new = np.zeros_like(self.Q)

        # 1. 内部节点（特征线交点）
        for i in range(1, self.N):
            # C+特征线（来自上游i-1）
            C_p = self.H[i-1] + self.B * self.Q[i-1] - \
                  self.R * self.Q[i-1] * abs(self.Q[i-1])

            # C-特征线（来自下游i+1）
            C_m = self.H[i+1] - self.B * self.Q[i+1] + \
                  self.R * self.Q[i+1] * abs(self.Q[i+1])

            # 求解
            H_new[i] = (C_p + C_m) / 2
            Q_new[i] = (C_p - C_m) / (2 * self.B)

        # 2. 上游边界（恒定水头）
        H_new[0] = self.inlet_H
        C_m = self.H[1] - self.B * self.Q[1] + self.R * self.Q[1] * abs(self.Q[1])
        Q_new[0] = (self.inlet_H - C_m) / self.B

        # 3. 下游边界（阀门）
        C_p = self.H[-2] + self.B * self.Q[-2] - self.R * self.Q[-2] * abs(self.Q[-2])

        # 阀门方程：Q = τ * Q0 * sqrt(H / H0)
        tau = self.outlet_valve_opening
        H0 = self.params.H_inlet
        Q0 = self.params.Q0

        def valve_equation(Q):
            if Q < 0:
                return Q + 1e6  # 惩罚负流量
            H = C_p - self.B * Q + self.R * Q * abs(Q)
            if H < 0:
                return Q + 1e6
            return Q - tau * Q0 * np.sqrt(H / H0)

        from scipy.optimize import brentq
        try:
            Q_new[-1] = brentq(valve_equation, 0, 2*Q0, xtol=1e-6)
            H_new[-1] = C_p - self.B * Q_new[-1] + self.R * Q_new[-1] * abs(Q_new[-1])
        except:
            Q_new[-1] = self.Q[-1]
            H_new[-1] = self.H[-1]

        self.H = H_new
        self.Q = Q_new

    def set_inlet_head(self, H):
        """设置入口水头"""
        self.inlet_H = H

    def set_outlet_valve(self, opening):
        """设置出口阀门开度 [0-1]"""
        self.outlet_valve_opening = np.clip(opening, 0, 1)


# ==================== 第三部分：耦合系统 ====================

class CoupledSystem:
    """渠道-管道耦合系统

    耦合方式：渠道末端出水 → 管道入口进水
    耦合边界条件：
    1. 流量连续性：Q_canal_end = Q_pipe_inlet
    2. 水头关系：H_pipe_inlet = h_canal_end + Z_canal - h_loss
    """
    def __init__(self, canal_params, pipe_params, Z_canal=50.0):
        """
        Args:
            canal_params: 渠道参数
            pipe_params: 管道参数
            Z_canal: 渠道末端底高程 [m]
        """
        self.canal = CanalSimulator(canal_params, dx=200, dt=20)
        self.pipe = PipelineMOCSimulator(pipe_params)
        self.Z_canal = Z_canal

        # 耦合迭代参数
        self.coupling_tol = 1e-3
        self.max_coupling_iter = 10

    def step(self):
        """耦合系统单步仿真"""
        # 迭代求解耦合边界条件
        for iter in range(self.max_coupling_iter):
            # 1. 从渠道获取末端状态
            h_canal_end = self.canal.h[-1]
            Q_canal_end = self.canal.Q[-1]

            # 2. 计算管道入口水头
            # 简化水头损失（进水口局部损失）
            V_inlet = Q_canal_end / self.pipe.params.A
            h_loss = 0.5 * V_inlet**2 / (2 * 9.81)  # 局部损失系数0.5
            H_pipe_inlet = self.Z_canal + h_canal_end - h_loss

            # 3. 更新管道入口边界
            self.pipe.set_inlet_head(H_pipe_inlet)

            # 4. 从管道获取入口流量
            Q_pipe_inlet = self.pipe.Q[0]

            # 5. 检查流量连续性
            residual = abs(Q_canal_end - Q_pipe_inlet)
            if residual < self.coupling_tol:
                break

            # 6. 更新渠道下游边界（使用管道需求流量）
            # 这里简化处理：调整渠道下游水深以匹配流量
            # 实际应用中可能需要更复杂的迭代算法
            if Q_canal_end > Q_pipe_inlet:
                self.canal.downstream_h *= 1.01
            else:
                self.canal.downstream_h *= 0.99

        # 推进时间步
        self.canal.step()
        self.pipe.step()

    def set_upstream_flow(self, Q):
        """设置渠道上游流量"""
        self.canal.set_upstream_flow(Q)

    def set_pipe_outlet_valve(self, opening):
        """设置管道出口阀门开度"""
        self.pipe.set_outlet_valve(opening)


# ==================== 第四部分：控制策略 ====================

class FeedforwardFeedbackController:
    """前馈-反馈控制器

    用于渠道上游流量控制，目标：维持渠道末端水深
    """
    def __init__(self, h_target, Kp=0.5, Ki=0.01, Kd=0.1, Q_base=20.0):
        """
        Args:
            h_target: 目标水深 [m]
            Kp, Ki, Kd: PID参数
            Q_base: 基准流量 [m³/s]
        """
        self.h_target = h_target
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Q_base = Q_base

        self.integral = 0
        self.last_error = 0

    def compute(self, h_current, disturbance=0, dt=1.0):
        """计算控制输出

        Args:
            h_current: 当前水深 [m]
            disturbance: 下游扰动（管道需水量变化） [m³/s]
            dt: 时间步长 [s]

        Returns:
            Q_control: 控制流量 [m³/s]
        """
        # 反馈控制（PID）
        error = self.h_target - h_current
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        Q_feedback = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.last_error = error

        # 前馈控制（补偿下游扰动）
        Q_feedforward = disturbance

        # 总控制量
        Q_control = self.Q_base + Q_feedback + Q_feedforward

        return max(0, Q_control)  # 流量非负


class MPCCoordinator:
    """MPC协调控制器（简化版）

    优化目标：
    1. 维持渠道水深在目标值
    2. 减小流量变化率
    3. 防止管道水锤压力超限
    """
    def __init__(self, h_target, Q_base, H_pipe_max, N_pred=10):
        """
        Args:
            h_target: 渠道目标水深 [m]
            Q_base: 基准流量 [m³/s]
            H_pipe_max: 管道最大允许压力 [m]
            N_pred: 预测时域
        """
        self.h_target = h_target
        self.Q_base = Q_base
        self.H_pipe_max = H_pipe_max
        self.N_pred = N_pred

    def compute(self, h_current, H_pipe_current, Q_current):
        """计算MPC控制输出（简化为启发式规则）

        Args:
            h_current: 当前渠道水深 [m]
            H_pipe_current: 当前管道压力 [m]
            Q_current: 当前流量 [m³/s]

        Returns:
            Q_control: 控制流量 [m³/s]
        """
        # 简化MPC：基于当前状态的启发式决策
        h_error = self.h_target - h_current
        H_margin = self.H_pipe_max - H_pipe_current

        # 权衡渠道水深控制和管道压力约束
        if H_margin < 5:  # 管道压力接近上限
            # 优先降低流量以减小管道压力
            Q_control = Q_current * 0.95
        elif abs(h_error) > 0.5:  # 渠道水深偏差较大
            # 调整流量以纠正水深
            Q_control = Q_current + 2.0 * h_error
        else:
            # 维持当前流量
            Q_control = Q_current

        # 流量变化率限制（避免激烈调整）
        dQ_max = 2.0  # m³/s per step
        Q_control = np.clip(Q_control, Q_current - dQ_max, Q_current + dQ_max)

        return max(0, Q_control)


# ==================== 第五部分：演示案例 ====================

def part1_coupling_simulation():
    """演示1：耦合系统基本仿真（开环）

    场景：渠道-管道耦合系统，管道末端阀门快速关闭，观察系统响应
    """
    print("\n" + "="*60)
    print("演示1：渠道-管道耦合系统仿真")
    print("="*60)

    # 参数设置
    canal_params = CanalParameters(L=5000, B=10, S0=0.0001, n=0.025, h0=2.0, Q0=20.0)
    pipe_params = PipelineParameters(L=1000, D=0.8, e=0.01, H_inlet=52.0, Q0=20.0)
    coupled_system = CoupledSystem(canal_params, pipe_params, Z_canal=50.0)

    # 仿真参数
    t_total = 300  # 总时长 [s]
    dt_canal = 20  # 渠道时间步长
    dt_pipe = coupled_system.pipe.dt
    t_valve_close_start = 100  # 阀门开始关闭时刻
    t_valve_close_end = 110  # 阀门关闭完成时刻

    # 同步时间步长（取最小值）
    dt = min(dt_canal, dt_pipe)
    N_steps = int(t_total / dt)

    # 记录数据
    time_history = []
    h_canal_end_history = []
    Q_canal_end_history = []
    H_pipe_inlet_history = []
    Q_pipe_inlet_history = []
    H_pipe_outlet_history = []
    valve_opening_history = []

    # 仿真循环
    for step in range(N_steps):
        t = step * dt

        # 阀门关闭策略（线性关闭）
        if t < t_valve_close_start:
            valve_opening = 1.0
        elif t < t_valve_close_end:
            valve_opening = 1.0 - (t - t_valve_close_start) / (t_valve_close_end - t_valve_close_start)
        else:
            valve_opening = 0.0

        coupled_system.set_pipe_outlet_valve(valve_opening)

        # 推进仿真
        coupled_system.step()

        # 记录数据
        if step % 10 == 0:  # 降采样
            time_history.append(t)
            h_canal_end_history.append(coupled_system.canal.h[-1])
            Q_canal_end_history.append(coupled_system.canal.Q[-1])
            H_pipe_inlet_history.append(coupled_system.pipe.H[0])
            Q_pipe_inlet_history.append(coupled_system.pipe.Q[0])
            H_pipe_outlet_history.append(coupled_system.pipe.H[-1])
            valve_opening_history.append(valve_opening)

    # 性能评估
    h_max = max(h_canal_end_history)
    h_min = min(h_canal_end_history)
    H_pipe_max = max(H_pipe_outlet_history)
    H_pipe_min = min(H_pipe_outlet_history)

    print(f"渠道末端水深变化范围: {h_min:.3f} - {h_max:.3f} m")
    print(f"管道出口压力变化范围: {H_pipe_min:.2f} - {H_pipe_max:.2f} m")
    print(f"管道最大压力上升: {H_pipe_max - pipe_params.H_inlet:.2f} m")

    # 可视化
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    fig.suptitle('渠道-管道耦合系统仿真（开环）', fontsize=14, fontweight='bold')

    # 渠道末端水深
    ax = axes[0, 0]
    ax.plot(time_history, h_canal_end_history, 'b-', linewidth=2)
    ax.axhline(canal_params.h0, color='k', linestyle='--', label='初始水深')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('水深 [m]')
    ax.set_title('(a) 渠道末端水深')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 渠道末端流量
    ax = axes[0, 1]
    ax.plot(time_history, Q_canal_end_history, 'g-', linewidth=2)
    ax.axhline(canal_params.Q0, color='k', linestyle='--', label='初始流量')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('流量 [m³/s]')
    ax.set_title('(b) 渠道末端流量')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 管道入口压力
    ax = axes[1, 0]
    ax.plot(time_history, H_pipe_inlet_history, 'r-', linewidth=2)
    ax.axhline(pipe_params.H_inlet, color='k', linestyle='--', label='初始压力')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('测压管水头 [m]')
    ax.set_title('(c) 管道入口压力')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 管道入口流量
    ax = axes[1, 1]
    ax.plot(time_history, Q_pipe_inlet_history, 'm-', linewidth=2)
    ax.axhline(pipe_params.Q0, color='k', linestyle='--', label='初始流量')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('流量 [m³/s]')
    ax.set_title('(d) 管道入口流量')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 管道出口压力（水锤效应）
    ax = axes[2, 0]
    ax.plot(time_history, H_pipe_outlet_history, 'c-', linewidth=2)
    ax.axhline(pipe_params.H_inlet, color='k', linestyle='--', label='初始压力')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('测压管水头 [m]')
    ax.set_title('(e) 管道出口压力（水锤）')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 阀门开度
    ax = axes[2, 1]
    ax.plot(time_history, valve_opening_history, 'orange', linewidth=2)
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('阀门开度 [-]')
    ax.set_title('(f) 管道出口阀门开度')
    ax.set_ylim([-0.1, 1.1])
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_coupling_simulation.png', dpi=150, bbox_inches='tight')
    print("图形已保存: part1_coupling_simulation.png")
    plt.close()


def part2_feedforward_feedback_control():
    """演示2：前馈-反馈控制

    场景：使用PID+前馈控制维持渠道末端水深，应对管道需水量变化
    """
    print("\n" + "="*60)
    print("演示2：前馈-反馈协调控制")
    print("="*60)

    # 参数设置
    canal_params = CanalParameters(L=5000, B=10, S0=0.0001, n=0.025, h0=2.0, Q0=20.0)
    pipe_params = PipelineParameters(L=1000, D=0.8, e=0.01, H_inlet=52.0, Q0=20.0)
    coupled_system = CoupledSystem(canal_params, pipe_params, Z_canal=50.0)

    # 控制器
    h_target = 2.0
    controller = FeedforwardFeedbackController(h_target=h_target, Kp=5.0, Ki=0.1, Kd=1.0, Q_base=20.0)

    # 仿真参数
    t_total = 500
    dt = 20
    N_steps = int(t_total / dt)

    # 记录数据
    time_history = []
    h_canal_end_history = []
    Q_upstream_history = []
    Q_downstream_history = []
    valve_opening_history = []

    # 仿真循环
    for step in range(N_steps):
        t = step * dt

        # 扰动场景：管道阀门开度变化（模拟需水量变化）
        if t < 100:
            valve_opening = 1.0
        elif t < 200:
            valve_opening = 0.5  # 需水量减半
        elif t < 300:
            valve_opening = 1.2  # 需水量增加20%
        else:
            valve_opening = 1.0

        coupled_system.set_pipe_outlet_valve(valve_opening)

        # 估计下游扰动（管道需水量变化）
        disturbance = (valve_opening - 1.0) * pipe_params.Q0

        # 控制器计算
        h_current = coupled_system.canal.h[-1]
        Q_control = controller.compute(h_current, disturbance, dt)

        # 应用控制
        coupled_system.set_upstream_flow(Q_control)

        # 推进仿真
        coupled_system.step()

        # 记录数据
        time_history.append(t)
        h_canal_end_history.append(coupled_system.canal.h[-1])
        Q_upstream_history.append(coupled_system.canal.Q[0])
        Q_downstream_history.append(coupled_system.canal.Q[-1])
        valve_opening_history.append(valve_opening)

    # 性能评估
    h_error = np.array(h_canal_end_history) - h_target
    IAE = np.sum(np.abs(h_error)) * dt
    ISE = np.sum(h_error**2) * dt
    max_error = np.max(np.abs(h_error))

    print(f"控制性能指标:")
    print(f"  最大误差: {max_error:.4f} m")
    print(f"  IAE: {IAE:.2f}")
    print(f"  ISE: {ISE:.4f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle('前馈-反馈协调控制', fontsize=14, fontweight='bold')

    # 渠道末端水深
    ax = axes[0, 0]
    ax.plot(time_history, h_canal_end_history, 'b-', linewidth=2, label='实际水深')
    ax.axhline(h_target, color='r', linestyle='--', linewidth=2, label='目标水深')
    ax.fill_between(time_history, h_target-0.1, h_target+0.1, alpha=0.2, color='green', label='±0.1m容差')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('水深 [m]')
    ax.set_title('(a) 渠道末端水深控制')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 上游控制流量
    ax = axes[0, 1]
    ax.plot(time_history, Q_upstream_history, 'g-', linewidth=2)
    ax.axhline(canal_params.Q0, color='k', linestyle='--', label='基准流量')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('流量 [m³/s]')
    ax.set_title('(b) 渠道上游控制流量')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 下游流量（耦合点）
    ax = axes[1, 0]
    ax.plot(time_history, Q_downstream_history, 'm-', linewidth=2)
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('流量 [m³/s]')
    ax.set_title('(c) 渠道下游流量（耦合点）')
    ax.grid(True, alpha=0.3)

    # 管道阀门开度（扰动）
    ax = axes[1, 1]
    ax.plot(time_history, valve_opening_history, 'orange', linewidth=2)
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('阀门开度 [-]')
    ax.set_title('(d) 管道阀门开度（扰动）')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part2_feedforward_feedback_control.png', dpi=150, bbox_inches='tight')
    print("图形已保存: part2_feedforward_feedback_control.png")
    plt.close()


def part3_mpc_coordination():
    """演示3：MPC协调控制

    场景：MPC协调控制器同时考虑渠道水深和管道压力约束
    """
    print("\n" + "="*60)
    print("演示3：MPC协调控制")
    print("="*60)

    # 参数设置
    canal_params = CanalParameters(L=5000, B=10, S0=0.0001, n=0.025, h0=2.0, Q0=20.0)
    pipe_params = PipelineParameters(L=1000, D=0.8, e=0.01, H_inlet=52.0, Q0=20.0)
    coupled_system = CoupledSystem(canal_params, pipe_params, Z_canal=50.0)

    # MPC控制器
    h_target = 2.0
    H_pipe_max = 80.0  # 管道最大允许压力
    mpc = MPCCoordinator(h_target=h_target, Q_base=20.0, H_pipe_max=H_pipe_max)

    # 仿真参数
    t_total = 400
    dt = 20
    N_steps = int(t_total / dt)

    # 记录数据
    time_history = []
    h_canal_history = []
    Q_control_history = []
    H_pipe_outlet_history = []
    valve_opening_history = []

    # 仿真循环
    for step in range(N_steps):
        t = step * dt

        # 扰动场景：阀门快速变化
        if t < 100:
            valve_opening = 1.0
        elif t < 120:
            valve_opening = 0.3  # 快速关闭（大扰动）
        elif t < 250:
            valve_opening = 0.3
        elif t < 270:
            valve_opening = 1.0  # 快速开启
        else:
            valve_opening = 1.0

        coupled_system.set_pipe_outlet_valve(valve_opening)

        # MPC控制
        h_current = coupled_system.canal.h[-1]
        H_pipe_current = coupled_system.pipe.H[-1]
        Q_current = coupled_system.canal.Q[0]
        Q_control = mpc.compute(h_current, H_pipe_current, Q_current)

        # 应用控制
        coupled_system.set_upstream_flow(Q_control)

        # 推进仿真
        coupled_system.step()

        # 记录数据
        time_history.append(t)
        h_canal_history.append(coupled_system.canal.h[-1])
        Q_control_history.append(Q_control)
        H_pipe_outlet_history.append(coupled_system.pipe.H[-1])
        valve_opening_history.append(valve_opening)

    # 性能评估
    h_error = np.array(h_canal_history) - h_target
    max_error = np.max(np.abs(h_error))
    H_pipe_max_actual = np.max(H_pipe_outlet_history)
    constraint_violation = max(0, H_pipe_max_actual - H_pipe_max)

    print(f"MPC控制性能:")
    print(f"  水深最大误差: {max_error:.4f} m")
    print(f"  管道最大压力: {H_pipe_max_actual:.2f} m")
    print(f"  压力约束违反: {constraint_violation:.2f} m")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle('MPC协调控制（考虑多目标与约束）', fontsize=14, fontweight='bold')

    # 渠道水深
    ax = axes[0, 0]
    ax.plot(time_history, h_canal_history, 'b-', linewidth=2, label='实际水深')
    ax.axhline(h_target, color='r', linestyle='--', linewidth=2, label='目标水深')
    ax.fill_between(time_history, h_target-0.1, h_target+0.1, alpha=0.2, color='green')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('水深 [m]')
    ax.set_title('(a) 渠道末端水深')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 控制流量
    ax = axes[0, 1]
    ax.plot(time_history, Q_control_history, 'g-', linewidth=2)
    ax.axhline(canal_params.Q0, color='k', linestyle='--', label='基准流量')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('流量 [m³/s]')
    ax.set_title('(b) MPC控制流量')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 管道压力（含约束）
    ax = axes[1, 0]
    ax.plot(time_history, H_pipe_outlet_history, 'r-', linewidth=2, label='实际压力')
    ax.axhline(H_pipe_max, color='orange', linestyle='--', linewidth=2, label=f'压力上限 {H_pipe_max}m')
    ax.fill_between(time_history, 0, H_pipe_max, alpha=0.1, color='green', label='安全区域')
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('测压管水头 [m]')
    ax.set_title('(c) 管道出口压力（约束管理）')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # 阀门开度
    ax = axes[1, 1]
    ax.plot(time_history, valve_opening_history, 'orange', linewidth=2)
    ax.set_xlabel('时间 [s]')
    ax.set_ylabel('阀门开度 [-]')
    ax.set_title('(d) 管道阀门开度（大扰动）')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_mpc_coordination.png', dpi=150, bbox_inches='tight')
    print("图形已保存: part3_mpc_coordination.png")
    plt.close()


def part4_spatial_profiles():
    """演示4：空间分布可视化

    展示耦合系统在不同时刻的空间分布（渠道水深剖面+管道压力剖面）
    """
    print("\n" + "="*60)
    print("演示4：耦合系统空间分布可视化")
    print("="*60)

    # 参数设置
    canal_params = CanalParameters(L=5000, B=10, S0=0.0001, n=0.025, h0=2.0, Q0=20.0)
    pipe_params = PipelineParameters(L=1000, D=0.8, e=0.01, H_inlet=52.0, Q0=20.0)
    coupled_system = CoupledSystem(canal_params, pipe_params, Z_canal=50.0)

    # 仿真参数
    t_total = 200
    dt = 20
    N_steps = int(t_total / dt)

    # 记录特定时刻的空间分布（选择与时间步长对齐的时刻）
    snapshot_steps = [0, 3, 5, 8]  # 对应t = 0, 60, 100, 160秒
    snapshot_times = [s * dt for s in snapshot_steps]
    snapshots = []

    # 仿真循环
    for step in range(N_steps + 1):  # +1以包含最后一步
        t = step * dt

        # 阀门关闭
        if t < 80:
            valve_opening = 1.0
        elif t < 100:
            valve_opening = 1.0 - (t - 80) / 20
        else:
            valve_opening = 0.0

        coupled_system.set_pipe_outlet_valve(valve_opening)

        # 记录快照（在推进之前）
        if step in snapshot_steps:
            snapshot = {
                't': t,
                'canal_h': coupled_system.canal.h.copy(),
                'canal_x': coupled_system.canal.x.copy(),
                'pipe_H': coupled_system.pipe.H.copy(),
                'pipe_x': coupled_system.pipe.x.copy()
            }
            snapshots.append(snapshot)

        # 推进仿真
        if step < N_steps:  # 最后一步只记录不推进
            coupled_system.step()

    # 可视化
    fig, axes = plt.subplots(len(snapshots), 2, figsize=(14, 10))
    fig.suptitle('耦合系统空间分布演化', fontsize=14, fontweight='bold')

    for i, snapshot in enumerate(snapshots):
        t = snapshot['t']

        # 渠道水深剖面
        ax = axes[i, 0]
        ax.plot(snapshot['canal_x'], snapshot['canal_h'], 'b-', linewidth=2)
        ax.axhline(canal_params.h0, color='k', linestyle='--', alpha=0.5, label='初始水深')
        ax.set_ylabel('水深 [m]')
        ax.set_title(f'渠道水深剖面 (t={t:.0f}s)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([1.5, 2.5])
        if i == 0:
            ax.legend()

        # 管道压力剖面
        ax = axes[i, 1]
        ax.plot(snapshot['pipe_x'], snapshot['pipe_H'], 'r-', linewidth=2)
        ax.axhline(pipe_params.H_inlet, color='k', linestyle='--', alpha=0.5, label='初始压力')
        ax.set_ylabel('测压管水头 [m]')
        ax.set_title(f'管道压力剖面 (t={t:.0f}s)')
        ax.grid(True, alpha=0.3)
        if i == 0:
            ax.legend()

        if i == len(snapshots) - 1:
            axes[i, 0].set_xlabel('距离 [m]')
            axes[i, 1].set_xlabel('距离 [m]')

    plt.tight_layout()
    plt.savefig('part4_spatial_profiles.png', dpi=150, bbox_inches='tight')
    print("图形已保存: part4_spatial_profiles.png")
    plt.close()

    print("\n耦合系统特征:")
    print(f"  渠道长度: {canal_params.L} m")
    print(f"  管道长度: {pipe_params.L} m")
    print(f"  水锤波速: {pipe_params.a:.1f} m/s")
    print(f"  水锤相位周期: {pipe_params.phase:.2f} s")


# ==================== 主程序 ====================

def main():
    """主程序：运行所有演示案例"""
    print("\n" + "="*60)
    print("案例19: 渠道-管道耦合系统")
    print("Coupled Canal-Pipeline System Simulation and Control")
    print("="*60)

    # 运行四个演示案例
    part1_coupling_simulation()
    part2_feedforward_feedback_control()
    part3_mpc_coordination()
    part4_spatial_profiles()

    print("\n" + "="*60)
    print("所有演示完成！")
    print("="*60)
    print("\n生成的图形文件:")
    print("  1. part1_coupling_simulation.png - 耦合系统基本仿真")
    print("  2. part2_feedforward_feedback_control.png - 前馈-反馈控制")
    print("  3. part3_mpc_coordination.png - MPC协调控制")
    print("  4. part4_spatial_profiles.png - 空间分布可视化")

    print("\n工程意义:")
    print("  ✓ 耦合建模：准确描述渠道-管道系统的水力耦合特性")
    print("  ✓ 数值方法：Preissmann隐式（渠道）+ MOC显式（管道）+ 迭代耦合")
    print("  ✓ 协调控制：前馈-反馈与MPC策略，平衡多目标与约束")
    print("  ✓ 工程应用：跨流域调水、灌区取水、泵站输水等复杂系统")


if __name__ == "__main__":
    main()
