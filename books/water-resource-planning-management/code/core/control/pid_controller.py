"""
PID控制器

比例-积分-微分控制器，用于水位、流量等参数的反馈控制
"""

import numpy as np
from typing import Optional, Dict


class PIDController:
    """
    PID控制器
    
    实现标准PID控制算法：
    u(t) = Kp*e(t) + Ki*∫e(τ)dτ + Kd*de(t)/dt
    
    Examples
    --------
    >>> # 水位控制
    >>> controller = PIDController(Kp=1.0, Ki=0.1, Kd=0.05)
    >>> 
    >>> # 控制循环
    >>> target = 10.0  # 目标水位
    >>> for t in range(100):
    ...     current = measure_water_level()
    ...     control = controller.compute(target, current, dt=1.0)
    ...     apply_control(control)
    """
    
    def __init__(
        self,
        Kp: float = 1.0,
        Ki: float = 0.0,
        Kd: float = 0.0,
        setpoint: float = 0.0,
        output_limits: Optional[tuple] = None,
        sample_time: Optional[float] = None
    ):
        """
        初始化PID控制器
        
        Parameters
        ----------
        Kp : float
            比例增益
        Ki : float
            积分增益
        Kd : float
            微分增益
        setpoint : float
            目标设定值
        output_limits : tuple, optional
            输出限制 (min, max)
        sample_time : float, optional
            采样时间（秒）
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        
        # 输出限制
        if output_limits is not None:
            self.output_min, self.output_max = output_limits
        else:
            self.output_min, self.output_max = None, None
        
        self.sample_time = sample_time
        
        # 内部状态
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = None
        self._output = 0.0
        
        # 历史记录
        self.history = {
            'time': [],
            'setpoint': [],
            'measurement': [],
            'error': [],
            'output': [],
            'p_term': [],
            'i_term': [],
            'd_term': []
        }
    
    def compute(
        self,
        measurement: float,
        dt: Optional[float] = None
    ) -> float:
        """
        计算控制输出
        
        Parameters
        ----------
        measurement : float
            当前测量值
        dt : float, optional
            时间步长（秒），如果为None则使用sample_time
        
        Returns
        -------
        float
            控制输出
        """
        # 误差
        error = self.setpoint - measurement
        
        # 时间步长
        if dt is None:
            dt = self.sample_time if self.sample_time is not None else 1.0
        
        # 比例项
        p_term = self.Kp * error
        
        # 积分项（梯形积分）
        self._integral += error * dt
        i_term = self.Ki * self._integral
        
        # 微分项（一阶差分）
        if dt > 0:
            derivative = (error - self._prev_error) / dt
        else:
            derivative = 0.0
        d_term = self.Kd * derivative
        
        # 控制输出
        output = p_term + i_term + d_term
        
        # 输出限制
        if self.output_min is not None and output < self.output_min:
            output = self.output_min
            # 抗积分饱和（Anti-windup）
            self._integral -= error * dt
        elif self.output_max is not None and output > self.output_max:
            output = self.output_max
            # 抗积分饱和
            self._integral -= error * dt
        
        # 更新状态
        self._prev_error = error
        self._output = output
        
        # 记录历史
        self.history['setpoint'].append(self.setpoint)
        self.history['measurement'].append(measurement)
        self.history['error'].append(error)
        self.history['output'].append(output)
        self.history['p_term'].append(p_term)
        self.history['i_term'].append(i_term)
        self.history['d_term'].append(d_term)
        
        return output
    
    def set_setpoint(self, setpoint: float):
        """设置目标值"""
        self.setpoint = setpoint
    
    def set_tunings(self, Kp: float, Ki: float, Kd: float):
        """
        设置PID参数
        
        Parameters
        ----------
        Kp, Ki, Kd : float
            PID增益
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
    
    def reset(self):
        """重置控制器状态"""
        self._integral = 0.0
        self._prev_error = 0.0
        self._output = 0.0
        self.history = {
            'time': [],
            'setpoint': [],
            'measurement': [],
            'error': [],
            'output': [],
            'p_term': [],
            'i_term': [],
            'd_term': []
        }
    
    def get_components(self) -> Dict[str, float]:
        """
        获取PID各分量
        
        Returns
        -------
        Dict[str, float]
            包含P、I、D各分量的字典
        """
        if len(self.history['p_term']) > 0:
            return {
                'p_term': self.history['p_term'][-1],
                'i_term': self.history['i_term'][-1],
                'd_term': self.history['d_term'][-1],
                'output': self.history['output'][-1]
            }
        else:
            return {
                'p_term': 0.0,
                'i_term': 0.0,
                'd_term': 0.0,
                'output': 0.0
            }
    
    def auto_tune(
        self,
        measurement_func: callable,
        control_func: callable,
        duration: float = 100.0,
        dt: float = 1.0
    ) -> tuple:
        """
        自动整定PID参数（Ziegler-Nichols方法）
        
        Parameters
        ----------
        measurement_func : callable
            测量函数
        control_func : callable
            控制执行函数
        duration : float
            测试持续时间
        dt : float
            采样时间
        
        Returns
        -------
        tuple
            (Kp, Ki, Kd)
        """
        # 简化实现：使用经验公式
        # 实际应用中需要更复杂的自动整定算法
        
        # 这里返回一组保守的参数
        Kp = 0.6 * self.Kp if self.Kp > 0 else 1.0
        Ki = 2.0 * Kp / duration
        Kd = Kp * duration / 8.0
        
        return Kp, Ki, Kd


def tune_pid_ziegler_nichols(Ku: float, Tu: float, control_type: str = 'PID') -> tuple:
    """
    使用Ziegler-Nichols方法整定PID参数
    
    Parameters
    ----------
    Ku : float
        临界增益
    Tu : float
        临界周期
    control_type : str
        控制器类型：'P', 'PI', 'PID'
    
    Returns
    -------
    tuple
        (Kp, Ki, Kd)
    
    Examples
    --------
    >>> Kp, Ki, Kd = tune_pid_ziegler_nichols(Ku=2.0, Tu=10.0, control_type='PID')
    """
    if control_type == 'P':
        Kp = 0.5 * Ku
        Ki = 0.0
        Kd = 0.0
    elif control_type == 'PI':
        Kp = 0.45 * Ku
        Ki = 1.2 * Kp / Tu
        Kd = 0.0
    elif control_type == 'PID':
        Kp = 0.6 * Ku
        Ki = 2.0 * Kp / Tu
        Kd = Kp * Tu / 8.0
    else:
        raise ValueError(f"Unknown control type: {control_type}")
    
    return Kp, Ki, Kd
