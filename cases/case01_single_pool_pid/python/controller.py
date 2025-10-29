"""
PID控制器实现

实现了标准PID控制器及其变体，包括抗积分饱和等功能。
"""

import numpy as np


class PIDController:
    """
    PID控制器

    控制律:
        u(t) = K_p * e(t) + K_i * ∫e(τ)dτ + K_d * de(t)/dt

    特性:
        - 抗积分饱和 (Anti-windup)
        - 微分项滤波
        - 输出限幅
    """

    def __init__(self, Kp, Ki, Kd, dt,
                 u_min=0.0, u_max=2.0,
                 anti_windup=True,
                 derivative_filter=True,
                 tau_f=10.0):
        """
        初始化PID控制器

        Args:
            Kp: 比例增益
            Ki: 积分增益
            Kd: 微分增益
            dt: 采样时间 (s)
            u_min: 输出最小值
            u_max: 输出最大值
            anti_windup: 是否启用抗积分饱和
            derivative_filter: 是否对微分项滤波
            tau_f: 微分滤波时间常数 (s)
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt

        self.u_min = u_min
        self.u_max = u_max

        self.anti_windup = anti_windup
        self.derivative_filter = derivative_filter
        self.tau_f = tau_f

        # 内部状态
        self.integral = 0.0
        self.error_prev = 0.0
        self.derivative_filtered = 0.0

        # 用于记录
        self.u_p = 0.0
        self.u_i = 0.0
        self.u_d = 0.0

    def compute(self, setpoint, measurement):
        """
        计算控制输出

        Args:
            setpoint: 设定值
            measurement: 测量值

        Returns:
            u: 控制输出
        """
        # 计算误差
        error = setpoint - measurement

        # 比例项
        self.u_p = self.Kp * error

        # 积分项
        self.integral += error * self.dt
        self.u_i = self.Ki * self.integral

        # 微分项
        derivative = (error - self.error_prev) / self.dt

        if self.derivative_filter:
            # 一阶低通滤波
            alpha = self.dt / (self.tau_f + self.dt)
            self.derivative_filtered = (alpha * derivative +
                                       (1 - alpha) * self.derivative_filtered)
            self.u_d = self.Kd * self.derivative_filtered
        else:
            self.u_d = self.Kd * derivative

        # 总控制输出
        u = self.u_p + self.u_i + self.u_d

        # 输出限幅
        u_sat = np.clip(u, self.u_min, self.u_max)

        # 抗积分饱和：如果输出饱和，停止积分累积
        if self.anti_windup and (u != u_sat):
            # 反算积分项，使总输出等于饱和值
            self.integral -= (u - u_sat) / self.Ki if self.Ki != 0 else 0

        # 更新状态
        self.error_prev = error

        return u_sat

    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.error_prev = 0.0
        self.derivative_filtered = 0.0
        self.u_p = 0.0
        self.u_i = 0.0
        self.u_d = 0.0

    def set_gains(self, Kp, Ki, Kd):
        """
        设置PID参数

        Args:
            Kp: 比例增益
            Ki: 积分增益
            Kd: 微分增益
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def get_components(self):
        """
        获取各控制分量

        Returns:
            tuple: (u_p, u_i, u_d)
        """
        return self.u_p, self.u_i, self.u_d


class PIController(PIDController):
    """PI控制器（PID的简化版本）"""

    def __init__(self, Kp, Ki, dt, u_min=0.0, u_max=2.0, anti_windup=True):
        super().__init__(Kp, Ki, 0.0, dt, u_min, u_max, anti_windup, False)


class PController(PIDController):
    """P控制器（仅比例）"""

    def __init__(self, Kp, dt, u_min=0.0, u_max=2.0):
        super().__init__(Kp, 0.0, 0.0, dt, u_min, u_max, False, False)


def ziegler_nichols_tuning(Ku, Tu, controller_type='PID'):
    """
    Ziegler-Nichols参数整定

    Args:
        Ku: 临界增益
        Tu: 临界周期 (s)
        controller_type: 控制器类型 ('P', 'PI', 'PID')

    Returns:
        tuple: (Kp, Ki, Kd)
    """
    if controller_type == 'P':
        Kp = 0.5 * Ku
        Ki = 0.0
        Kd = 0.0
    elif controller_type == 'PI':
        Kp = 0.45 * Ku
        Ki = 1.2 * Kp / Tu
        Kd = 0.0
    elif controller_type == 'PID':
        Kp = 0.6 * Ku
        Ki = 2 * Kp / Tu
        Kd = Kp * Tu / 8
    else:
        raise ValueError(f"Unknown controller type: {controller_type}")

    return Kp, Ki, Kd


def cohen_coon_tuning(K, tau, theta, controller_type='PID'):
    """
    Cohen-Coon参数整定（针对一阶加纯滞后系统）

    Args:
        K: 系统增益
        tau: 时间常数 (s)
        theta: 纯滞后 (s)
        controller_type: 控制器类型

    Returns:
        tuple: (Kp, Ki, Kd)
    """
    r = theta / tau

    if controller_type == 'P':
        Kp = (1/K) * (1/r) * (1 + r/3)
        Ki = 0.0
        Kd = 0.0
    elif controller_type == 'PI':
        Kp = (1/K) * (1/r) * (0.9 + r/12)
        Ki = Kp / (theta * (30 + 3*r) / (9 + 20*r))
        Kd = 0.0
    elif controller_type == 'PID':
        Kp = (1/K) * (1/r) * (4/3 + r/4)
        Ki = Kp / (theta * (32 + 6*r) / (13 + 8*r))
        Kd = Kp * theta * 4 / (11 + 2*r)
    else:
        raise ValueError(f"Unknown controller type: {controller_type}")

    return Kp, Ki, Kd


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("PID控制器测试")
    print("=" * 60)

    # 创建控制器
    dt = 1.0
    pid = PIDController(Kp=0.5, Ki=0.01, Kd=5.0, dt=dt)

    print(f"\nPID参数:")
    print(f"  Kp = {pid.Kp}")
    print(f"  Ki = {pid.Ki}")
    print(f"  Kd = {pid.Kd}")
    print(f"  采样时间 dt = {pid.dt} s")

    # 测试阶跃响应
    print(f"\n测试: 阶跃响应")
    print(f"  设定值 = 2.5, 测量值从 2.0 开始")
    print(f"\n  时间   误差    u_p     u_i     u_d     输出")
    print(f"  " + "-" * 60)

    setpoint = 2.5
    measurement = 2.0

    for i in range(10):
        t = i * dt
        u = pid.compute(setpoint, measurement)
        error = setpoint - measurement
        u_p, u_i, u_d = pid.get_components()

        print(f"  {t:5.0f}  {error:6.3f}  {u_p:6.3f}  {u_i:6.3f}  "
              f"{u_d:6.3f}  {u:6.3f}")

        # 简单模拟：测量值逐渐接近设定值
        measurement += (u - 1.0) * 0.01

    # 测试Ziegler-Nichols整定
    print(f"\n\nZiegler-Nichols参数整定测试:")
    Ku = 2.0
    Tu = 100.0
    print(f"  临界增益 Ku = {Ku}")
    print(f"  临界周期 Tu = {Tu} s")

    for ctrl_type in ['P', 'PI', 'PID']:
        Kp, Ki, Kd = ziegler_nichols_tuning(Ku, Tu, ctrl_type)
        print(f"\n  {ctrl_type}控制器:")
        print(f"    Kp = {Kp:.3f}, Ki = {Ki:.4f}, Kd = {Kd:.3f}")

    print("\n测试完成!")
