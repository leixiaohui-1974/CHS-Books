"""
水量平衡计算模块

水量平衡方程：ΔS = P + I_in - E - I_out
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Union


def calculate_water_balance(
    precipitation: float,
    inflow: float = 0.0,
    evaporation: float = 0.0,
    outflow: float = 0.0,
    initial_storage: float = 0.0,
) -> Dict[str, float]:
    """
    计算水量平衡
    
    水量平衡方程：ΔS = P + I_in - E - I_out
    
    Parameters
    ----------
    precipitation : float
        降水量 (mm或m³)
    inflow : float, optional
        入流量 (m³)
    evaporation : float, optional
        蒸发量 (mm或m³)
    outflow : float, optional
        出流量 (m³)
    initial_storage : float, optional
        初始蓄水量 (m³)
    
    Returns
    -------
    Dict[str, float]
        水量平衡结果字典：
        - storage_change: 蓄变量
        - final_storage: 最终蓄水量
        - balance_error: 平衡误差（理论上应为0）
    
    Examples
    --------
    >>> result = calculate_water_balance(
    ...     precipitation=100,
    ...     inflow=1000,
    ...     evaporation=50,
    ...     outflow=900,
    ...     initial_storage=5000
    ... )
    >>> print(f"蓄变量: {result['storage_change']:.2f}")
    """
    # 计算蓄变量
    storage_change = precipitation + inflow - evaporation - outflow
    
    # 计算最终蓄水量
    final_storage = initial_storage + storage_change
    
    # 验证水量平衡
    balance = (precipitation + inflow) - (evaporation + outflow + storage_change)
    
    return {
        "storage_change": storage_change,
        "final_storage": final_storage,
        "balance_error": balance,
        "precipitation": precipitation,
        "inflow": inflow,
        "evaporation": evaporation,
        "outflow": outflow,
    }


class WaterBalanceModel:
    """
    水量平衡模型类
    
    用于连续时间序列的水量平衡计算
    
    Attributes
    ----------
    area : float
        流域面积 (km²)
    initial_storage : float
        初始蓄水量 (万m³)
    
    Examples
    --------
    >>> model = WaterBalanceModel(area=1000, initial_storage=5000)
    >>> results = model.simulate(
    ...     precipitation=[100, 120, 80],
    ...     evaporation=[50, 60, 55]
    ... )
    """
    
    def __init__(
        self,
        area: float,
        initial_storage: float = 0.0
    ):
        """
        初始化水量平衡模型
        
        Parameters
        ----------
        area : float
            流域面积 (km²)
        initial_storage : float, optional
            初始蓄水量 (万m³)
        """
        self.area = area
        self.storage = initial_storage
        self.results = []
    
    def step(
        self,
        precipitation: float,
        evaporation: float,
        inflow: float = 0.0,
        outflow: float = 0.0
    ) -> Dict[str, float]:
        """
        单步计算
        
        Parameters
        ----------
        precipitation : float
            降水量 (mm)
        evaporation : float
            蒸发量 (mm)
        inflow : float, optional
            入流量 (m³/s)
        outflow : float, optional
            出流量 (m³/s)
        
        Returns
        -------
        Dict[str, float]
            本时段的水量平衡结果
        """
        # 将降水和蒸发转换为体积 (mm * km² = 1000 m³)
        precip_volume = precipitation * self.area * 1000  # m³
        evap_volume = evaporation * self.area * 1000  # m³
        
        # 计算水量平衡
        result = calculate_water_balance(
            precipitation=precip_volume,
            inflow=inflow,
            evaporation=evap_volume,
            outflow=outflow,
            initial_storage=self.storage
        )
        
        # 更新蓄水量
        self.storage = result["final_storage"]
        
        # 记录结果
        self.results.append(result)
        
        return result
    
    def simulate(
        self,
        precipitation: Union[np.ndarray, list],
        evaporation: Union[np.ndarray, list],
        inflow: Optional[Union[np.ndarray, list]] = None,
        outflow: Optional[Union[np.ndarray, list]] = None
    ) -> pd.DataFrame:
        """
        多时段连续模拟
        
        Parameters
        ----------
        precipitation : array-like
            降水序列 (mm)
        evaporation : array-like
            蒸发序列 (mm)
        inflow : array-like, optional
            入流序列 (m³/s)
        outflow : array-like, optional
            出流序列 (m³/s)
        
        Returns
        -------
        pd.DataFrame
            模拟结果数据框
        
        Examples
        --------
        >>> model = WaterBalanceModel(area=1000, initial_storage=5000)
        >>> results = model.simulate(
        ...     precipitation=[100, 120, 80, 90, 110],
        ...     evaporation=[50, 60, 55, 45, 50]
        ... )
        >>> print(results[['storage_change', 'final_storage']])
        """
        precipitation = np.array(precipitation)
        evaporation = np.array(evaporation)
        n = len(precipitation)
        
        if inflow is None:
            inflow = np.zeros(n)
        else:
            inflow = np.array(inflow)
        
        if outflow is None:
            outflow = np.zeros(n)
        else:
            outflow = np.array(outflow)
        
        # 重置结果
        self.results = []
        
        # 逐时段模拟
        for i in range(n):
            self.step(
                precipitation=precipitation[i],
                evaporation=evaporation[i],
                inflow=inflow[i],
                outflow=outflow[i]
            )
        
        # 转换为DataFrame
        df = pd.DataFrame(self.results)
        df.index.name = "时段"
        
        return df
    
    def get_summary(self) -> Dict[str, float]:
        """
        获取模拟结果摘要
        
        Returns
        -------
        Dict[str, float]
            摘要统计
        """
        if not self.results:
            return {}
        
        df = pd.DataFrame(self.results)
        
        return {
            "total_precipitation": df["precipitation"].sum(),
            "total_evaporation": df["evaporation"].sum(),
            "total_inflow": df["inflow"].sum(),
            "total_outflow": df["outflow"].sum(),
            "net_storage_change": df["storage_change"].sum(),
            "final_storage": self.storage,
            "max_balance_error": df["balance_error"].abs().max(),
        }
