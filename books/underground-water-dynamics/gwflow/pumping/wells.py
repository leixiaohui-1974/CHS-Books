"""
抽水井类定义
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from .analytical import (
    theis_solution,
    cooper_jacob_solution,
    thiem_solution
)


@dataclass
class PumpingWell:
    """
    抽水井类
    
    Attributes
    ----------
    x : float
        井的x坐标 [m]
    y : float
        井的y坐标 [m]
    Q : float
        抽水流量 [m³/day]，正值表示抽水
    r_well : float, optional
        井半径 [m]，默认0.1m
    name : str, optional
        井的名称
    """
    x: float
    y: float
    Q: float
    r_well: float = 0.1
    name: Optional[str] = None
    
    def __post_init__(self):
        if self.name is None:
            self.name = f"Well_{id(self)}"
    
    def compute_drawdown(
        self,
        x_obs: np.ndarray,
        y_obs: np.ndarray,
        t: float,
        T: float,
        S: float,
        method: str = 'theis'
    ) -> np.ndarray:
        """
        计算观测点处的降深
        
        Parameters
        ----------
        x_obs, y_obs : array
            观测点坐标
        t : float
            时间 [day]
        T, S : float
            含水层参数
        method : str
            'theis', 'cooper_jacob', or 'thiem'
        
        Returns
        -------
        s : array
            降深 [m]
        """
        # 计算距离
        r = np.sqrt((x_obs - self.x)**2 + (y_obs - self.y)**2)
        r = np.maximum(r, self.r_well)  # 最小为井半径
        
        if method == 'theis':
            s = theis_solution(r, t, self.Q, T, S)
        elif method == 'cooper_jacob':
            s = cooper_jacob_solution(r, t, self.Q, T, S)
        elif method == 'thiem':
            R = 2000  # 假设影响半径
            s = thiem_solution(r, self.Q, T, R)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return s


class WellField:
    """
    井群管理类
    
    管理多个抽水井，计算总的水位影响
    """
    
    def __init__(self, name: str = "WellField"):
        """
        Parameters
        ----------
        name : str
            井群名称
        """
        self.name = name
        self.wells: List[PumpingWell] = []
    
    def add_well(self, well: PumpingWell):
        """添加一口井"""
        self.wells.append(well)
    
    def remove_well(self, well: PumpingWell):
        """移除一口井"""
        self.wells.remove(well)
    
    def get_total_pumping(self) -> float:
        """获取总抽水量"""
        return sum(w.Q for w in self.wells)
    
    def get_well_locations(self) -> np.ndarray:
        """获取所有井的坐标"""
        return np.array([[w.x, w.y] for w in self.wells])
    
    def get_well_rates(self) -> np.ndarray:
        """获取所有井的流量"""
        return np.array([w.Q for w in self.wells])
    
    def compute_total_drawdown(
        self,
        x_obs: np.ndarray,
        y_obs: np.ndarray,
        t: float,
        T: float,
        S: float,
        method: str = 'theis'
    ) -> np.ndarray:
        """
        计算所有井叠加后的总降深
        
        Parameters
        ----------
        x_obs, y_obs : array
            观测点坐标
        t : float
            时间 [day]
        T, S : float
            含水层参数
        method : str
            计算方法
        
        Returns
        -------
        s_total : array
            总降深 [m]
        """
        s_total = np.zeros_like(x_obs, dtype=float)
        
        for well in self.wells:
            s = well.compute_drawdown(x_obs, y_obs, t, T, S, method)
            s_total += s
        
        return s_total
    
    def get_statistics(self) -> Dict:
        """获取井群统计信息"""
        return {
            'n_wells': len(self.wells),
            'total_Q': self.get_total_pumping(),
            'mean_Q': np.mean(self.get_well_rates()) if self.wells else 0,
            'max_Q': np.max(self.get_well_rates()) if self.wells else 0,
            'min_Q': np.min(self.get_well_rates()) if self.wells else 0,
        }
    
    def __len__(self):
        return len(self.wells)
    
    def __repr__(self):
        return f"WellField('{self.name}', n_wells={len(self.wells)}, total_Q={self.get_total_pumping():.0f})"
