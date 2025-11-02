"""
定额法预测模块
"""

import numpy as np
import pandas as pd
from typing import Dict, List


class QuotaForecaster:
    """
    定额法需水预测器
    
    根据用水定额和社会经济指标预测未来需水量
    """
    
    def __init__(
        self,
        domestic_quota: float = 260,  # L/人·日
        industrial_quota: float = 42,  # m³/万元
        service_quota: float = 18,     # m³/万元
    ):
        """
        初始化
        
        Parameters
        ----------
        domestic_quota : float
            人均综合生活用水定额 (L/人·日)
        industrial_quota : float
            万元工业增加值用水量 (m³/万元)
        service_quota : float
            万元服务业增加值用水量 (m³/万元)
        """
        self.domestic_quota = domestic_quota
        self.industrial_quota = industrial_quota
        self.service_quota = service_quota
    
    def forecast_domestic(
        self,
        population: float
    ) -> float:
        """
        预测生活需水量
        
        Q_生活 = P × q × 365 / 10000
        
        Parameters
        ----------
        population : float
            人口 (万人)
        
        Returns
        -------
        float
            生活需水量 (万m³/d)
        """
        # L/人·日 × 万人 / 10000 = 万m³/d
        return self.domestic_quota * population / 10000
    
    def forecast_industrial(
        self,
        industrial_output: float
    ) -> float:
        """
        预测工业需水量
        
        Q_工业 = 工业增加值 × 万元产值用水量
        
        Parameters
        ----------
        industrial_output : float
            工业增加值 (亿元)
        
        Returns
        -------
        float
            工业需水量 (万m³/d)
        """
        # 亿元 × 10000万元/亿元 × m³/万元 / 365天 = 万m³/d
        return industrial_output * 10000 * self.industrial_quota / 365 / 10000
    
    def forecast_service(
        self,
        service_output: float
    ) -> float:
        """
        预测服务业需水量
        
        Parameters
        ----------
        service_output : float
            服务业增加值 (亿元)
        
        Returns
        -------
        float
            服务业需水量 (万m³/d)
        """
        return service_output * 10000 * self.service_quota / 365 / 10000
    
    def forecast_total(
        self,
        population: float,
        industrial_output: float,
        service_output: float,
        water_saving_factor: float = 1.0
    ) -> Dict[str, float]:
        """
        预测总需水量
        
        Parameters
        ----------
        population : float
            人口 (万人)
        industrial_output : float
            工业增加值 (亿元)
        service_output : float
            服务业增加值 (亿元)
        water_saving_factor : float, optional
            节水系数，默认1.0（无节水措施）
        
        Returns
        -------
        Dict[str, float]
            各类需水量和总需水量
        """
        domestic = self.forecast_domestic(population)
        industrial = self.forecast_industrial(industrial_output)
        service = self.forecast_service(service_output)
        
        # 应用节水系数
        domestic_adj = domestic * water_saving_factor
        industrial_adj = industrial * water_saving_factor
        service_adj = service * water_saving_factor
        
        total = domestic_adj + industrial_adj + service_adj
        
        return {
            "domestic": domestic_adj,
            "industrial": industrial_adj,
            "service": service_adj,
            "total": total
        }
    
    def forecast_series(
        self,
        years: List[int],
        population_series: List[float],
        industrial_output_series: List[float],
        service_output_series: List[float],
        water_saving_factor: float = 1.0
    ) -> pd.DataFrame:
        """
        预测多年序列
        
        Parameters
        ----------
        years : List[int]
            年份列表
        population_series : List[float]
            人口序列 (万人)
        industrial_output_series : List[float]
            工业增加值序列 (亿元)
        service_output_series : List[float]
            服务业增加值序列 (亿元)
        water_saving_factor : float, optional
            节水系数
        
        Returns
        -------
        pd.DataFrame
            预测结果数据框
        """
        results = []
        
        for i, year in enumerate(years):
            forecast = self.forecast_total(
                population=population_series[i],
                industrial_output=industrial_output_series[i],
                service_output=service_output_series[i],
                water_saving_factor=water_saving_factor
            )
            forecast["year"] = year
            results.append(forecast)
        
        df = pd.DataFrame(results)
        # 重新排列列顺序
        df = df[["year", "domestic", "industrial", "service", "total"]]
        
        return df
