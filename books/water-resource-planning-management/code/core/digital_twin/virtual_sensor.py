"""
虚拟传感器

使用物理模型和数据融合实现软测量
"""

import numpy as np
from typing import Dict, Callable, Optional


class VirtualSensor:
    """
    虚拟传感器
    
    通过物理模型和其他传感器数据推算难以直接测量的变量
    
    Examples
    --------
    >>> # 虚拟水位传感器
    >>> def level_model(storage):
    ...     return storage_to_level(storage)
    >>> 
    >>> sensor = VirtualSensor(model=level_model)
    >>> level = sensor.measure({'storage': 450})
    """
    
    def __init__(
        self,
        model: Optional[Callable] = None,
        name: str = "VirtualSensor"
    ):
        """
        初始化虚拟传感器
        
        Parameters
        ----------
        model : Callable, optional
            物理模型函数
        name : str
            传感器名称
        """
        self.model = model
        self.name = name
        
        # 历史记录
        self.history = []
        
        # 校准参数
        self.calibration = {
            'bias': 0.0,
            'scale': 1.0
        }
    
    def measure(
        self,
        inputs: Dict[str, float],
        use_calibration: bool = True
    ) -> float:
        """
        进行测量
        
        Parameters
        ----------
        inputs : Dict[str, float]
            输入变量
        use_calibration : bool
            是否使用校准参数
        
        Returns
        -------
        float
            测量值
        """
        if self.model is None:
            raise ValueError("未设置物理模型")
        
        # 计算原始值
        raw_value = self.model(inputs)
        
        # 应用校准
        if use_calibration:
            value = raw_value * self.calibration['scale'] + self.calibration['bias']
        else:
            value = raw_value
        
        # 记录
        self.history.append({
            'inputs': inputs.copy(),
            'raw_value': raw_value,
            'value': value
        })
        
        return value
    
    def calibrate(
        self,
        reference_data: np.ndarray,
        estimated_data: np.ndarray
    ):
        """
        校准虚拟传感器
        
        使用线性回归拟合偏差和尺度因子
        
        Parameters
        ----------
        reference_data : np.ndarray
            参考数据（真实值）
        estimated_data : np.ndarray
            估计数据（模型值）
        """
        # 线性回归：y = scale*x + bias
        n = len(reference_data)
        
        # 最小二乘法
        x_mean = np.mean(estimated_data)
        y_mean = np.mean(reference_data)
        
        numerator = np.sum((estimated_data - x_mean) * (reference_data - y_mean))
        denominator = np.sum((estimated_data - x_mean) ** 2)
        
        if denominator > 1e-10:
            self.calibration['scale'] = numerator / denominator
            self.calibration['bias'] = y_mean - self.calibration['scale'] * x_mean
        
        # 计算校准精度
        calibrated = estimated_data * self.calibration['scale'] + self.calibration['bias']
        rmse = np.sqrt(np.mean((reference_data - calibrated) ** 2))
        
        return {
            'scale': self.calibration['scale'],
            'bias': self.calibration['bias'],
            'rmse': rmse
        }
    
    def get_history(self) -> list:
        """获取历史记录"""
        return self.history
    
    def set_model(self, model: Callable):
        """设置物理模型"""
        self.model = model
    
    def reset(self):
        """重置传感器"""
        self.history = []


def create_reservoir_level_sensor(
    min_storage: float,
    max_storage: float,
    min_level: float,
    max_level: float
) -> VirtualSensor:
    """
    创建水库水位虚拟传感器
    
    Parameters
    ----------
    min_storage : float
        最小库容
    max_storage : float
        最大库容
    min_level : float
        死水位
    max_level : float
        最高水位
    
    Returns
    -------
    VirtualSensor
        水位虚拟传感器
    """
    def level_model(inputs: Dict) -> float:
        storage = inputs.get('storage', min_storage)
        
        # 线性插值（简化）
        ratio = (storage - min_storage) / (max_storage - min_storage)
        ratio = np.clip(ratio, 0, 1)
        
        level = min_level + ratio * (max_level - min_level)
        
        return level
    
    sensor = VirtualSensor(model=level_model, name="ReservoirLevelSensor")
    return sensor


def create_flow_sensor(coefficient: float = 1.0) -> VirtualSensor:
    """
    创建流量虚拟传感器
    
    基于水位和闸门开度估算流量
    
    Parameters
    ----------
    coefficient : float
        流量系数
    
    Returns
    -------
    VirtualSensor
        流量虚拟传感器
    """
    def flow_model(inputs: Dict) -> float:
        head = inputs.get('head', 0)
        gate_opening = inputs.get('gate_opening', 0)
        
        # Q = C * A * sqrt(2*g*H)
        # 简化：Q = coefficient * opening * sqrt(head)
        flow = coefficient * gate_opening * np.sqrt(max(0, head))
        
        return flow
    
    sensor = VirtualSensor(model=flow_model, name="FlowSensor")
    return sensor
