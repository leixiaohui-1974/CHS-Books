"""
光伏组件模型
PV Module Models

组件由多个电池串并联构成
"""

import numpy as np
from typing import Tuple
from .pv_cell import SingleDiodeModel


class PVModule:
    """
    光伏组件模型
    由Ns个电池串联, Np个串并联
    """
    
    def __init__(self,
                 cell_model: SingleDiodeModel,
                 Ns: int = 60,  # 串联电池数
                 Np: int = 1,   # 并联串数
                 name: str = "PV Module"):
        """
        初始化光伏组件
        
        Parameters:
        -----------
        cell_model : SingleDiodeModel
            单个电池模型
        Ns : int
            串联电池数量
        Np : int
            并联串数量
        """
        self.cell = cell_model
        self.Ns = Ns
        self.Np = Np
        self.name = name
        
        # 组件特性
        self.Voc = Ns * cell_model.Voc
        self.Isc = Np * cell_model.Isc
        
    def calculate_current(self, voltage: float) -> float:
        """
        计算组件电流
        """
        v_cell = voltage / self.Ns
        i_cell = self.cell.calculate_current(v_cell)
        return self.Np * i_cell
        
    def calculate_power(self, voltage: float) -> float:
        """
        计算组件功率
        """
        return voltage * self.calculate_current(voltage)
