"""
风力机控制模块

包含:
1. MPPT控制算法
   - TSR (Tip Speed Ratio) 控制
   - PSF (Power Signal Feedback) 控制
   - HCS (Hill Climb Search) 控制
2. 变桨距控制
3. 转矩控制
4. PID控制器

作者: CHS Books
"""

import numpy as np
from typing import Dict, Tuple, Callable


class PIDController:
    """PID控制器"""
    
    def __init__(
        self,
        Kp: float = 1.0,
        Ki: float = 0.1,
        Kd: float = 0.01,
        output_limits: Tuple[float, float] = None,
        name: str = "PID"
    ):
        """
        初始化PID控制器
        
        Args:
            Kp: 比例增益
            Ki: 积分增益
            Kd: 微分增益
            output_limits: 输出限幅 (min, max)
        """
        self.name = name
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.output_limits = output_limits
        
        # 内部状态
        self.integral = 0
        self.prev_error = 0
    
    def compute(self, setpoint: float, measurement: float, dt: float) -> float:
        """
        计算控制输出
        
        Args:
            setpoint: 设定值
            measurement: 测量值
            dt: 时间步长
            
        Returns:
            控制输出
        """
        error = setpoint - measurement
        
        # 比例项
        P = self.Kp * error
        
        # 积分项
        self.integral += error * dt
        I = self.Ki * self.integral
        
        # 微分项
        D = self.Kd * (error - self.prev_error) / dt if dt > 0 else 0
        
        # 总输出
        output = P + I + D
        
        # 限幅
        if self.output_limits is not None:
            output = np.clip(output, self.output_limits[0], self.output_limits[1])
            
            # 抗积分饱和
            if output == self.output_limits[0] or output == self.output_limits[1]:
                self.integral -= error * dt
        
        self.prev_error = error
        
        return output
    
    def reset(self):
        """重置控制器"""
        self.integral = 0
        self.prev_error = 0


class TSRController:
    """
    TSR (Tip Speed Ratio) 控制
    
    通过维持最优叶尖速比来实现MPPT
    """
    
    def __init__(
        self,
        lambda_opt: float = 8.0,
        R: float = 40.0,
        Kp: float = 1e5,
        Ki: float = 1e3,
        name: str = "TSR_Control"
    ):
        """
        初始化TSR控制器
        
        Args:
            lambda_opt: 最优叶尖速比
            R: 风轮半径 (m)
            Kp, Ki: PI控制器参数
        """
        self.name = name
        self.lambda_opt = lambda_opt
        self.R = R
        
        # 转速PI控制器
        self.speed_controller = PIDController(
            Kp=Kp, Ki=Ki, Kd=0,
            output_limits=(0, 1e7)
        )
    
    def compute_reference_speed(self, v_wind: float) -> float:
        """
        根据风速计算参考转速
        
        omega_ref = lambda_opt * v_wind / R
        
        Args:
            v_wind: 风速 (m/s)
            
        Returns:
            参考转速 (rad/s)
        """
        omega_ref = self.lambda_opt * v_wind / self.R
        return omega_ref
    
    def compute_torque(
        self,
        v_wind: float,
        omega_actual: float,
        dt: float
    ) -> Dict:
        """
        计算控制转矩
        
        Args:
            v_wind: 风速 (m/s)
            omega_actual: 实际转速 (rad/s)
            dt: 时间步长
            
        Returns:
            控制结果字典
        """
        # 计算参考转速
        omega_ref = self.compute_reference_speed(v_wind)
        
        # PI控制计算转矩
        T_ref = self.speed_controller.compute(omega_ref, omega_actual, dt)
        
        # 实际叶尖速比
        lambda_actual = omega_actual * self.R / v_wind if v_wind > 0 else 0
        
        return {
            'T_ref': T_ref,
            'omega_ref': omega_ref,
            'lambda_actual': lambda_actual,
            'lambda_opt': self.lambda_opt,
        }


class PSFController:
    """
    PSF (Power Signal Feedback) 控制
    
    基于测量功率反馈的MPPT控制
    """
    
    def __init__(
        self,
        Kopt: float = 0.5,
        R: float = 40.0,
        rho: float = 1.225,
        Cp_max: float = 0.48,
        name: str = "PSF_Control"
    ):
        """
        初始化PSF控制器
        
        Kopt = 0.5 * rho * pi * R^5 * Cp_max / lambda_opt^3
        
        Args:
            Kopt: 最优增益系数
            R: 风轮半径
            rho: 空气密度
            Cp_max: 最大功率系数
        """
        self.name = name
        self.Kopt = Kopt
        self.R = R
        self.rho = rho
        self.Cp_max = Cp_max
    
    @staticmethod
    def compute_Kopt(R: float, rho: float, Cp_max: float, lambda_opt: float) -> float:
        """计算最优增益Kopt"""
        Kopt = 0.5 * rho * np.pi * R**5 * Cp_max / lambda_opt**3
        return Kopt
    
    def compute_torque(self, omega: float) -> Dict:
        """
        计算最优转矩
        
        T_opt = Kopt * omega^2
        
        Args:
            omega: 转速 (rad/s)
            
        Returns:
            控制结果
        """
        T_opt = self.Kopt * omega**2
        
        return {
            'T_opt': T_opt,
            'omega': omega,
        }


class HCSController:
    """
    HCS (Hill Climb Search) 控制
    
    爬山搜索算法，无需风速测量
    """
    
    def __init__(
        self,
        delta_T: float = 1e4,
        delta_P_threshold: float = 1e3,
        update_interval: float = 5.0,
        name: str = "HCS_Control"
    ):
        """
        初始化HCS控制器
        
        Args:
            delta_T: 转矩扰动步长 (N*m)
            delta_P_threshold: 功率变化阈值 (W)
            update_interval: 更新间隔 (s)
        """
        self.name = name
        self.delta_T = delta_T
        self.delta_P_threshold = delta_P_threshold
        self.update_interval = update_interval
        
        # 状态变量
        self.T_ref = 1e5  # 初始转矩
        self.P_prev = 0
        self.time_since_update = 0
    
    def compute_torque(self, P_actual: float, dt: float) -> Dict:
        """
        计算控制转矩
        
        Args:
            P_actual: 实际功率 (W)
            dt: 时间步长
            
        Returns:
            控制结果
        """
        self.time_since_update += dt
        
        # 检查是否到更新时刻
        if self.time_since_update >= self.update_interval:
            delta_P = P_actual - self.P_prev
            
            # 爬山逻辑
            if abs(delta_P) > self.delta_P_threshold:
                if delta_P > 0:
                    # 功率增加，继续当前方向
                    pass
                else:
                    # 功率减小，反向
                    self.delta_T = -self.delta_T
            
            # 更新转矩
            self.T_ref += self.delta_T
            self.T_ref = max(0, self.T_ref)  # 非负
            
            # 更新状态
            self.P_prev = P_actual
            self.time_since_update = 0
        
        return {
            'T_ref': self.T_ref,
            'P_actual': P_actual,
            'delta_P': P_actual - self.P_prev,
        }


class OptimalTorqueController:
    """
    最优转矩控制
    
    基于功率曲线的查表法
    """
    
    def __init__(
        self,
        omega_table: np.ndarray,
        T_table: np.ndarray,
        name: str = "OptimalTorque"
    ):
        """
        初始化最优转矩控制器
        
        Args:
            omega_table: 转速查找表 (rad/s)
            T_table: 对应的最优转矩 (N*m)
        """
        self.name = name
        self.omega_table = omega_table
        self.T_table = T_table
    
    def compute_torque(self, omega: float) -> float:
        """
        查表计算最优转矩
        
        Args:
            omega: 转速
            
        Returns:
            最优转矩
        """
        T_opt = np.interp(omega, self.omega_table, self.T_table)
        return T_opt


class PitchController:
    """
    变桨距控制器
    
    用于超额定风速区域的功率限制
    """
    
    def __init__(
        self,
        P_rated: float = 2e6,
        omega_rated: float = 2.0,
        Kp_pitch: float = 5.0,
        Ki_pitch: float = 0.5,
        beta_min: float = 0,
        beta_max: float = 30,
        name: str = "PitchControl"
    ):
        """
        初始化变桨距控制器
        
        Args:
            P_rated: 额定功率 (W)
            omega_rated: 额定转速 (rad/s)
            Kp_pitch, Ki_pitch: PI参数
            beta_min, beta_max: 桨距角范围 (度)
        """
        self.name = name
        self.P_rated = P_rated
        self.omega_rated = omega_rated
        self.beta_min = beta_min
        self.beta_max = beta_max
        
        # PI控制器（基于转速）
        self.speed_controller = PIDController(
            Kp=Kp_pitch,
            Ki=Ki_pitch,
            Kd=0,
            output_limits=(beta_min, beta_max)
        )
    
    def compute_pitch_angle(
        self,
        omega_actual: float,
        dt: float
    ) -> Dict:
        """
        计算桨距角
        
        Args:
            omega_actual: 实际转速
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # PI控制计算桨距角
        beta = self.speed_controller.compute(
            self.omega_rated,
            omega_actual,
            dt
        )
        
        return {
            'beta': beta,
            'omega_ref': self.omega_rated,
            'omega_actual': omega_actual,
        }


class RegionController:
    """
    分区控制器
    
    综合MPPT和变桨控制
    """
    
    def __init__(
        self,
        mppt_controller,
        pitch_controller,
        v_rated: float = 12.0,
        omega_rated: float = 2.0,
        P_rated: float = 2e6,
        name: str = "RegionControl"
    ):
        """
        初始化分区控制器
        
        Args:
            mppt_controller: MPPT控制器（TSR/PSF/HCS）
            pitch_controller: 变桨距控制器
            v_rated: 额定风速
            omega_rated: 额定转速
            P_rated: 额定功率
        """
        self.name = name
        self.mppt_controller = mppt_controller
        self.pitch_controller = pitch_controller
        self.v_rated = v_rated
        self.omega_rated = omega_rated
        self.P_rated = P_rated
    
    def compute_control(
        self,
        v_wind: float,
        omega_actual: float,
        P_actual: float,
        dt: float
    ) -> Dict:
        """
        分区控制逻辑
        
        Args:
            v_wind: 风速
            omega_actual: 实际转速
            P_actual: 实际功率
            dt: 时间步长
            
        Returns:
            控制结果
        """
        if v_wind < self.v_rated:
            # Region II: MPPT控制
            if hasattr(self.mppt_controller, 'compute_reference_speed'):
                # TSR控制
                result = self.mppt_controller.compute_torque(v_wind, omega_actual, dt)
            else:
                # PSF控制
                result = self.mppt_controller.compute_torque(omega_actual)
            
            result['region'] = 'II_MPPT'
            result['beta'] = 0  # 最小桨距角
            
        else:
            # Region III: 变桨距功率限制
            pitch_result = self.pitch_controller.compute_pitch_angle(omega_actual, dt)
            
            result = {
                'region': 'III_Pitch',
                'beta': pitch_result['beta'],
                'T_ref': self.P_rated / omega_actual if omega_actual > 0 else 0,
                'omega_ref': self.omega_rated,
            }
        
        return result


def estimate_wind_speed(P: float, omega: float, R: float, rho: float = 1.225, Cp: float = 0.4) -> float:
    """
    风速估计（简化方法）
    
    从功率和转速估计风速
    
    Args:
        P: 功率 (W)
        omega: 转速 (rad/s)
        R: 风轮半径 (m)
        rho: 空气密度
        Cp: 假设的功率系数
        
    Returns:
        估计风速 (m/s)
    """
    if P <= 0:
        return 0
    
    # P = 0.5 * rho * A * Cp * v^3
    A = np.pi * R**2
    v_est = (P / (0.5 * rho * A * Cp)) ** (1/3)
    
    return v_est


def simulate_wind_turbine_mppt(
    wind_speed_func: Callable,
    power_curve_func: Callable,
    controller,
    t_span: Tuple[float, float],
    dt: float = 0.1
) -> Dict:
    """
    风力机MPPT仿真
    
    Args:
        wind_speed_func: 风速函数 v(t)
        power_curve_func: 功率曲线函数 P(v, omega, beta)
        controller: 控制器对象
        t_span: 时间范围 (t0, tf)
        dt: 时间步长
        
    Returns:
        仿真结果
    """
    t0, tf = t_span
    N = int((tf - t0) / dt)
    
    # 初始化数组
    t = np.linspace(t0, tf, N)
    v_wind = np.zeros(N)
    omega = np.zeros(N)
    T_ref = np.zeros(N)
    P_actual = np.zeros(N)
    beta = np.zeros(N)
    
    # 初始条件
    omega[0] = 1.0
    
    # 仿真循环
    for i in range(1, N):
        # 风速
        v_wind[i] = wind_speed_func(t[i])
        
        # 控制器计算
        if hasattr(controller, 'compute_control'):
            # 分区控制器
            ctrl = controller.compute_control(v_wind[i], omega[i-1], P_actual[i-1], dt)
            T_ref[i] = ctrl.get('T_ref', 0)
            beta[i] = ctrl.get('beta', 0)
        elif hasattr(controller, 'compute_pitch_angle'):
            # 变桨控制器
            ctrl = controller.compute_pitch_angle(omega[i-1], dt)
            beta[i] = ctrl['beta']
            T_ref[i] = 0
        else:
            # MPPT控制器
            if hasattr(controller, 'compute_reference_speed'):
                ctrl = controller.compute_torque(v_wind[i], omega[i-1], dt)
            else:
                ctrl = controller.compute_torque(omega[i-1])
            T_ref[i] = ctrl.get('T_ref', ctrl.get('T_opt', 0))
            beta[i] = 0
        
        # 功率曲线
        P_actual[i] = power_curve_func(v_wind[i], omega[i-1], beta[i])
        
        # 转速动态（简化）
        J = 1e7  # 转动惯量
        T_aero = P_actual[i] / omega[i-1] if omega[i-1] > 0 else 0
        domega = (T_aero - T_ref[i]) / J
        omega[i] = omega[i-1] + domega * dt
        omega[i] = max(0.1, omega[i])  # 避免负转速
    
    return {
        't': t,
        'v_wind': v_wind,
        'omega': omega,
        'T_ref': T_ref,
        'P_actual': P_actual,
        'beta': beta,
    }
