"""
测试空间插值模块
==============
"""

import sys
sys.path.insert(0, '..')

import numpy as np
import pytest

from code.core.interpolation import (
    thiessen_polygon, thiessen_weights,
    inverse_distance_weighting, ordinary_kriging,
    experimental_variogram
)


def test_thiessen_weights():
    """测试Thiessen权重计算"""
    stations = np.array([[0, 0], [1, 0], [0, 1]])
    target = np.array([0.2, 0.1])
    
    weights, nearest_idx = thiessen_weights(stations, target)
    
    # 权重和应该为1
    assert np.sum(weights) == 1.0
    # 只有一个站点权重为1
    assert np.sum(weights == 1.0) == 1
    # 最近站点应该是第一个
    assert nearest_idx == 0


def test_idw_basic():
    """测试IDW基本功能"""
    stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    values = np.array([10, 20, 15, 25])
    target = np.array([[0.5, 0.5]])
    
    result = inverse_distance_weighting(stations, values, target, power=2)
    
    # 结果应该在观测值范围内
    assert result[0] >= values.min()
    assert result[0] <= values.max()
    # 中心点结果应该接近平均值
    assert abs(result[0] - np.mean(values)) < 5


def test_idw_exact_at_stations():
    """测试IDW在站点处精确"""
    stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    values = np.array([10, 20, 15, 25])
    
    # 在第一个站点处插值
    target = stations[0:1]
    result = inverse_distance_weighting(stations, values, target, power=2)
    
    # 应该精确等于该站点的值
    assert abs(result[0] - values[0]) < 1e-6


def test_idw_power_effect():
    """测试IDW power参数影响"""
    stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    values = np.array([10, 20, 15, 25])
    target = np.array([[0.5, 0.5]])
    
    result_p1 = inverse_distance_weighting(stations, values, target, power=1)
    result_p2 = inverse_distance_weighting(stations, values, target, power=2)
    result_p3 = inverse_distance_weighting(stations, values, target, power=3)
    
    # power越大，距离衰减越快
    # 结果应该不同
    assert not np.allclose(result_p1, result_p2)
    assert not np.allclose(result_p2, result_p3)


def test_kriging_basic():
    """测试Kriging基本功能"""
    stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    values = np.array([10, 20, 15, 25])
    target = np.array([[0.5, 0.5]])
    
    result, variance = ordinary_kriging(stations, values, target)
    
    # 结果应该在合理范围内
    assert result[0] >= values.min() - 5
    assert result[0] <= values.max() + 5
    # 方差应该非负
    assert variance[0] >= 0


def test_experimental_variogram():
    """测试实验变异函数计算"""
    stations = np.array([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]])
    values = np.array([10, 12, 15, 18, 20])
    
    lag_distances, semivariances = experimental_variogram(stations, values, n_lags=3)
    
    # 应该有滞后距离和半方差
    assert len(lag_distances) > 0
    assert len(semivariances) > 0
    assert len(lag_distances) == len(semivariances)
    # 半方差应该非负
    assert np.all(semivariances >= 0)


def test_idw_multiple_targets():
    """测试IDW批量插值"""
    stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    values = np.array([10, 20, 15, 25])
    targets = np.array([[0.25, 0.25], [0.75, 0.75], [0.5, 0.5]])
    
    results = inverse_distance_weighting(stations, values, targets, power=2)
    
    # 应该返回3个结果
    assert len(results) == 3
    # 所有结果都应该在合理范围内
    assert np.all(results >= values.min() - 1)
    assert np.all(results <= values.max() + 1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
