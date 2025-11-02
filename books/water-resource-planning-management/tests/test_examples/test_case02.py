"""
测试案例1.2：城市需水预测
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                "../../code/examples/case02_water_demand_forecasting"))

from src.quota_method import QuotaForecaster
from src.trend_analysis import TrendForecaster
from src.grey_model import GreyForecaster


class TestQuotaMethod:
    """测试定额法预测"""
    
    def test_forecast_domestic(self):
        """测试生活需水预测"""
        forecaster = QuotaForecaster(domestic_quota=260)
        
        # 人口300万人
        demand = forecaster.forecast_domestic(population=300)
        
        # 检查结果范围合理
        assert demand > 0
        assert demand < 100  # 应该在合理范围内
    
    def test_forecast_total(self):
        """测试总需水量预测"""
        forecaster = QuotaForecaster(
            domestic_quota=260,
            industrial_quota=42,
            service_quota=18
        )
        
        result = forecaster.forecast_total(
            population=300,
            industrial_output=1500,
            service_output=2000,
            water_saving_factor=0.9
        )
        
        assert 'domestic' in result
        assert 'industrial' in result
        assert 'service' in result
        assert 'total' in result
        
        # 总需水应该等于各部分之和
        total_calc = result['domestic'] + result['industrial'] + result['service']
        assert abs(result['total'] - total_calc) < 0.01
    
    def test_forecast_series(self):
        """测试序列预测"""
        forecaster = QuotaForecaster()
        
        years = [2020, 2021, 2022]
        population = [300, 305, 310]
        industrial = [1500, 1550, 1600]
        service = [2000, 2050, 2100]
        
        results = forecaster.forecast_series(
            years=years,
            population_series=population,
            industrial_output_series=industrial,
            service_output_series=service
        )
        
        assert len(results) == 3
        assert 'year' in results.columns
        assert 'total' in results.columns


class TestTrendAnalysis:
    """测试趋势分析"""
    
    def test_linear_trend(self):
        """测试线性趋势"""
        years = np.array([2010, 2011, 2012, 2013, 2014])
        values = np.array([100, 105, 110, 115, 120])
        
        forecaster = TrendForecaster(method='linear')
        forecaster.fit(years, values)
        
        # 预测
        pred_years = np.array([2015, 2016])
        predictions = forecaster.predict(pred_years)
        
        assert len(predictions) == 2
        assert all(predictions > 120)  # 应该大于最后一个历史值
    
    def test_model_score(self):
        """测试拟合优度"""
        years = np.array([2010, 2011, 2012, 2013, 2014])
        values = np.array([100, 105, 110, 115, 120])
        
        forecaster = TrendForecaster(method='linear')
        forecaster.fit(years, values)
        
        r2 = forecaster.score()
        
        # 对于完美线性数据，R²应该接近1
        assert r2 > 0.99
    
    def test_get_equation(self):
        """测试方程获取"""
        years = np.array([2010, 2011, 2012])
        values = np.array([100, 105, 110])
        
        forecaster = TrendForecaster(method='linear')
        forecaster.fit(years, values)
        
        equation = forecaster.get_equation()
        
        assert isinstance(equation, str)
        assert 'y' in equation


class TestGreyModel:
    """测试灰色预测模型"""
    
    def test_fit_and_predict(self):
        """测试拟合和预测"""
        data = np.array([100, 105, 110, 115, 120])
        
        model = GreyForecaster()
        model.fit(data)
        
        # 预测3步
        predictions = model.forecast(3)
        
        assert len(predictions) == 3
        assert all(predictions > 120)  # 应该大于最后一个历史值
    
    def test_accuracy_test(self):
        """测试精度检验"""
        data = np.array([100, 105, 110, 115, 120, 125])
        
        model = GreyForecaster()
        model.fit(data)
        
        mre, C, grade = model.accuracy_test()
        
        assert 0 <= mre <= 1  # 相对误差应该在0-1之间
        assert C >= 0  # 后验差比应该非负
        assert isinstance(grade, str)
    
    def test_get_params(self):
        """测试参数获取"""
        data = np.array([100, 105, 110, 115, 120])
        
        model = GreyForecaster()
        model.fit(data)
        
        params = model.get_params()
        
        assert 'a' in params
        assert 'u' in params
        assert 'equation' in params


# 如果直接运行此文件
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
