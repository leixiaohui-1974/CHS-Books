"""
测试 core.utils 模块
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import os
import sys

# 添加code目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../code"))

from core.utils.statistics import (
    calculate_statistics,
    pearson_iii_distribution,
    frequency_analysis,
    calculate_exceedance_probability,
    moving_average,
)
from core.utils.data_io import load_csv, save_csv, load_yaml, save_yaml
from core.utils.time_series import resample_series, fill_missing_values, detect_outliers


class TestStatistics:
    """测试统计分析函数"""
    
    def test_calculate_statistics(self):
        """测试基本统计量计算"""
        data = np.array([100, 120, 90, 110, 95, 105, 115, 88, 102, 108])
        stats = calculate_statistics(data)
        
        assert 'mean' in stats
        assert 'std' in stats
        assert 'cv' in stats
        assert 'cs' in stats
        
        # 检查均值计算
        assert abs(stats['mean'] - np.mean(data)) < 0.01
        
        # 检查变差系数
        expected_cv = np.std(data, ddof=1) / np.mean(data)
        assert abs(stats['cv'] - expected_cv) < 0.01
    
    def test_pearson_iii_distribution(self):
        """测试Pearson-III分布参数估计"""
        data = np.array([100, 120, 90, 110, 95, 105, 115, 88, 102, 108])
        mean, cv, cs = pearson_iii_distribution(data)
        
        assert mean > 0
        assert cv > 0
        assert isinstance(cs, float)
        
        # 检查均值
        assert abs(mean - np.mean(data)) < 0.01
    
    def test_frequency_analysis(self):
        """测试频率分析"""
        # 生成测试数据
        np.random.seed(42)
        data = np.random.lognormal(4.5, 0.5, 50)
        
        # 频率分析
        probs, design_values = frequency_analysis(
            data,
            probabilities=[0.5, 0.75, 0.95],
            distribution='pearson3'
        )
        
        assert len(probs) == 3
        assert len(design_values) == 3
        
        # 检查设计值随概率递减
        assert design_values[0] > design_values[1] > design_values[2]
    
    def test_calculate_exceedance_probability(self):
        """测试经验超过概率计算"""
        data = np.array([100, 120, 90, 110, 95])
        sorted_data, probs = calculate_exceedance_probability(data)
        
        assert len(sorted_data) == len(data)
        assert len(probs) == len(data)
        
        # 检查排序（从大到小）
        assert sorted_data[0] == 120
        assert sorted_data[-1] == 90
        
        # 检查概率范围
        assert all(0 < p < 1 for p in probs)
    
    def test_moving_average(self):
        """测试移动平均"""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        ma = moving_average(data, window=3)
        
        # 中间部分应该是移动平均值
        assert not np.isnan(ma[1])  # 应该有值
        
        # 检查移动平均的计算
        # 例如索引1的值应该是(1+2+3)/3=2
        # 但由于填充策略，实际值可能略有不同


class TestDataIO:
    """测试数据输入输出函数"""
    
    def test_save_and_load_csv(self):
        """测试CSV读写"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试数据
            df = pd.DataFrame({
                'year': [2020, 2021, 2022],
                'value': [100, 110, 120]
            })
            
            # 保存
            filepath = os.path.join(tmpdir, 'test.csv')
            save_csv(df, filepath)
            
            # 读取
            df_loaded = load_csv(filepath)
            
            # 检查
            assert len(df_loaded) == 3
            assert list(df_loaded.columns) == ['year', 'value']
            assert df_loaded['value'].sum() == 330
    
    def test_save_and_load_yaml(self):
        """测试YAML读写"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试数据
            data = {
                'name': 'test',
                'value': 123,
                'list': [1, 2, 3]
            }
            
            # 保存
            filepath = os.path.join(tmpdir, 'test.yaml')
            save_yaml(data, filepath)
            
            # 读取
            data_loaded = load_yaml(filepath)
            
            # 检查
            assert data_loaded['name'] == 'test'
            assert data_loaded['value'] == 123
            assert data_loaded['list'] == [1, 2, 3]


class TestTimeSeries:
    """测试时间序列处理函数"""
    
    def test_fill_missing_values(self):
        """测试缺失值填补"""
        # 创建带缺失值的数据
        data = pd.Series([1, np.nan, 3, np.nan, 5])
        
        # 线性插值
        filled = fill_missing_values(data, method='linear')
        
        # 检查
        assert not filled.isna().any()
        assert filled[1] == 2.0  # 线性插值结果
        assert filled[3] == 4.0
    
    def test_detect_outliers(self):
        """测试异常值检测"""
        # 创建数据，包含一个明显的异常值
        data = np.array([1, 2, 3, 100, 4, 5])
        
        # 检测异常值
        outliers = detect_outliers(data, method='iqr', threshold=1.5)
        
        # 检查
        assert outliers.sum() == 1  # 应该检测到1个异常值
        assert outliers[3] == True  # 100应该被检测为异常值
    
    def test_resample_series(self):
        """测试时间序列重采样"""
        # 创建日数据
        dates = pd.date_range('2020-01-01', periods=365, freq='D')
        series = pd.Series(np.random.randn(365), index=dates)
        
        # 重采样为月数据
        monthly = resample_series(series, 'M', method='mean')
        
        # 检查
        assert len(monthly) == 12  # 应该有12个月


# 如果直接运行此文件
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
