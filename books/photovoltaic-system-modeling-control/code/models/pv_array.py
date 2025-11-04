"""
光伏阵列模型
PV Array Models

阵列由多个组件串并联构成
"""

from .pv_module import PVModule


class PVArray:
    """
    光伏阵列模型
    """
    
    def __init__(self,
                 module: PVModule,
                 Ns: int = 1,  # 串联组件数
                 Np: int = 1,  # 并联串数
                 name: str = "PV Array"):
        """
        初始化光伏阵列
        """
        self.module = module
        self.Ns = Ns
        self.Np = Np
        self.name = name
        
        # 阵列特性
        self.Voc = Ns * module.Voc
        self.Isc = Np * module.Isc
        
    def calculate_current(self, voltage: float) -> float:
        """
        计算阵列电流
        """
        v_module = voltage / self.Ns
        i_module = self.module.calculate_current(v_module)
        return self.Np * i_module
        
    def calculate_power(self, voltage: float) -> float:
        """
        计算阵列功率
        """
        return voltage * self.calculate_current(voltage)
