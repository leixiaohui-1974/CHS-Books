"""
物理水库模型

模拟真实水库的物理行为
"""

import numpy as np
from typing import Tuple


class PhysicalReservoir:
    """
    物理水库模型（真实系统模拟）
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
        初始化物理水库
        
        Parameters
        ----------
        min_storage : float
            死库容（万m³）
        max_storage : float
            最大库容
        min_level : float
            死水位（m）
        max_level : float
            最高水位
        dt : float
            时间步长（小时）
        """
        self.min_storage = min_storage
        self.max_storage = max_storage
        self.min_level = min_level
        self.max_level = max_level
        self.dt = dt
        
        # 当前状态（真实值）
        self.storage = (min_storage + max_storage) / 2
        self.inflow = 200.0  # m³/s
        self.outflow = 200.0
        
        # 历史
        self.history = {
            'storage': [self.storage],
            'level': [self.storage_to_level(self.storage)],
            'inflow': [self.inflow],
            'outflow': [self.outflow]
        }
    
    def storage_to_level(self, storage: float) -> float:
        """
        库容转水位（非线性关系）
        
        Parameters
        ----------
        storage : float
            库容（万m³）
        
        Returns
        -------
        float
            水位（m）
        """
        # 非线性关系（简化：二次多项式）
        ratio = (storage - self.min_storage) / (self.max_storage - self.min_storage)
        ratio = np.clip(ratio, 0, 1)
        
        # 非线性插值
        level = self.min_level + (self.max_level - self.min_level) * (ratio ** 0.8)
        
        return level
    
    def level_to_storage(self, level: float) -> float:
        """
        水位转库容
        
        Parameters
        ----------
        level : float
            水位（m）
        
        Returns
        -------
        float
            库容（万m³）
        """
        ratio = (level - self.min_level) / (self.max_level - self.min_level)
        ratio = np.clip(ratio, 0, 1)
        
        # 非线性逆变换
        storage = self.min_storage + (self.max_storage - self.min_storage) * (ratio ** 1.25)
        
        return storage
    
    def step(self, inflow: float, outflow: float) -> Tuple[float, float]:
        """
        模拟一个时间步
        
        Parameters
        ----------
        inflow : float
            入流（m³/s）
        outflow : float
            出流（m³/s）
        
        Returns
        -------
        Tuple[float, float]
            (库容, 水位)
        """
        # 水量平衡（单位转换：m³/s -> 万m³/h）
        delta_storage = (inflow - outflow) * self.dt * 3.6 / 10000
        
        # 更新库容
        self.storage += delta_storage
        self.storage = np.clip(self.storage, self.min_storage, self.max_storage)
        
        # 更新入流（带随机波动）
        self.inflow = inflow + np.random.randn() * 5
        self.outflow = outflow
        
        # 计算水位
        level = self.storage_to_level(self.storage)
        
        # 记录
        self.history['storage'].append(self.storage)
        self.history['level'].append(level)
        self.history['inflow'].append(self.inflow)
        self.history['outflow'].append(self.outflow)
        
        return self.storage, level
    
    def get_measurements(
        self,
        level_noise_std: float = 0.05,
        flow_noise_std: float = 5.0
    ) -> dict:
        """
        获取带噪声的测量值（模拟真实传感器）
        
        Parameters
        ----------
        level_noise_std : float
            水位测量噪声标准差（m）
        flow_noise_std : float
            流量测量噪声标准差（m³/s）
        
        Returns
        -------
        dict
            测量值
        """
        level = self.storage_to_level(self.storage)
        
        # 添加测量噪声
        level_measured = level + np.random.randn() * level_noise_std
        inflow_measured = self.inflow + np.random.randn() * flow_noise_std
        outflow_measured = self.outflow + np.random.randn() * flow_noise_std
        
        return {
            'level': level_measured,
            'inflow': inflow_measured,
            'outflow': outflow_measured,
            'storage_true': self.storage,  # 真实值（用于对比）
            'level_true': level
        }
