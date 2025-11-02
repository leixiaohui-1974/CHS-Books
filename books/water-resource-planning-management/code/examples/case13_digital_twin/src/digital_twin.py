"""
数字孪生水库

虚拟水库模型，与物理水库实时同步
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../"))

from core.digital_twin import KalmanFilter, VirtualSensor


class DigitalTwinReservoir:
    """
    数字孪生水库
    """
    
    def __init__(
        self,
        min_storage: float = 50,
        max_storage: float = 500,
        min_level: float = 180,
        max_level: float = 200,
        dt: float = 1.0
    ):
        """
        初始化数字孪生
        
        Parameters
        ----------
        min_storage, max_storage : float
            库容范围
        min_level, max_level : float
            水位范围
        dt : float
            时间步长
        """
        self.min_storage = min_storage
        self.max_storage = max_storage
        self.min_level = min_level
        self.max_level = max_level
        self.dt = dt
        
        # 卡尔曼滤波器
        self.kf = self._initialize_kalman_filter()
        
        # 虚拟传感器
        self.virtual_storage_sensor = self._create_storage_sensor()
        
        # 估计历史
        self.history = {
            'storage_est': [],
            'level_est': [],
            'storage_var': []
        }
    
    def _initialize_kalman_filter(self) -> KalmanFilter:
        """初始化卡尔曼滤波器"""
        # 状态：[库容]
        # 观测：[水位]
        
        kf = KalmanFilter(dim_x=1, dim_z=1)
        
        # 状态转移矩阵（简化：一阶积分）
        kf.F = np.array([[1.0]])
        
        # 观测矩阵（水位 = f(库容)，线性化）
        # 实际是非线性，这里用雅可比近似
        kf.H = np.array([[1.0 / (self.max_storage - self.min_storage) * (self.max_level - self.min_level)]])
        
        # 过程噪声协方差
        kf.Q = np.array([[1.0]])  # 库容变化不确定性
        
        # 观测噪声协方差
        kf.R = np.array([[0.05 ** 2]])  # 水位测量噪声
        
        # 初始状态
        kf.x = np.array([[(self.min_storage + self.max_storage) / 2]])
        kf.P = np.array([[100.0]])
        
        return kf
    
    def _create_storage_sensor(self) -> VirtualSensor:
        """创建库容虚拟传感器"""
        def storage_model(inputs):
            level = inputs.get('level', self.min_level)
            
            # 水位转库容（非线性）
            ratio = (level - self.min_level) / (self.max_level - self.min_level)
            ratio = np.clip(ratio, 0, 1)
            
            storage = self.min_storage + (self.max_storage - self.min_storage) * (ratio ** 1.25)
            
            return storage
        
        sensor = VirtualSensor(model=storage_model, name="StorageSensor")
        return sensor
    
    def storage_to_level(self, storage: float) -> float:
        """库容转水位"""
        ratio = (storage - self.min_storage) / (self.max_storage - self.min_storage)
        ratio = np.clip(ratio, 0, 1)
        
        level = self.min_level + (self.max_level - self.min_level) * (ratio ** 0.8)
        
        return level
    
    def update(
        self,
        measurements: dict,
        control: dict
    ) -> dict:
        """
        更新数字孪生状态
        
        Parameters
        ----------
        measurements : dict
            传感器测量值
        control : dict
            控制输入
        
        Returns
        -------
        dict
            估计状态
        """
        level_measured = measurements['level']
        inflow = measurements['inflow']
        outflow = measurements['outflow']
        
        # 1. 预测步骤（基于水量平衡）
        delta_storage = (inflow - outflow) * self.dt * 3.6 / 10000
        self.kf.x[0, 0] += delta_storage
        
        # 预测协方差
        self.kf.P = self.kf.F @ self.kf.P @ self.kf.F.T + self.kf.Q
        
        # 2. 更新步骤（基于水位观测）
        # 将水位转换为库容观测
        storage_from_level = self.virtual_storage_sensor.measure({'level': level_measured})
        
        # 卡尔曼更新
        z = np.array([[storage_from_level]])
        
        # 计算卡尔曼增益
        S = self.kf.H @ self.kf.P @ self.kf.H.T + self.kf.R
        K = self.kf.P @ self.kf.H.T / S[0, 0]
        
        # 更新状态
        innovation = z[0, 0] - self.kf.H @ self.kf.x
        self.kf.x += K * innovation
        
        # 更新协方差
        self.kf.P = (np.eye(1) - K @ self.kf.H) @ self.kf.P
        
        # 提取估计值
        storage_est = self.kf.x[0, 0]
        storage_est = np.clip(storage_est, self.min_storage, self.max_storage)
        
        level_est = self.storage_to_level(storage_est)
        storage_var = self.kf.P[0, 0]
        
        # 记录
        self.history['storage_est'].append(storage_est)
        self.history['level_est'].append(level_est)
        self.history['storage_var'].append(storage_var)
        
        return {
            'storage_est': storage_est,
            'level_est': level_est,
            'storage_std': np.sqrt(storage_var)
        }
    
    def predict_future(
        self,
        inflow_forecast: list,
        outflow_plan: list,
        steps: int
    ) -> list:
        """
        预测未来状态
        
        Parameters
        ----------
        inflow_forecast : list
            入流预测序列
        outflow_plan : list
            出流计划序列
        steps : int
            预测步数
        
        Returns
        -------
        list
            预测状态序列
        """
        predictions = []
        storage = self.kf.x[0, 0]
        
        for i in range(min(steps, len(inflow_forecast), len(outflow_plan))):
            # 水量平衡预测
            delta_storage = (inflow_forecast[i] - outflow_plan[i]) * self.dt * 3.6 / 10000
            storage += delta_storage
            storage = np.clip(storage, self.min_storage, self.max_storage)
            
            level = self.storage_to_level(storage)
            
            predictions.append({
                'storage': storage,
                'level': level
            })
        
        return predictions
