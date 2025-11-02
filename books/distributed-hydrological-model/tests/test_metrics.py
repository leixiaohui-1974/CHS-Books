"""
测试评估指标模块
==============
"""

import sys
sys.path.insert(0, '..')

import numpy as np
import pytest

from code.core.utils.metrics import (
    nash_sutcliffe, rmse, relative_error, 
    peak_error, correlation_coefficient, evaluate_model
)


def test_nash_sutcliffe():
    """测试NSE"""
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sim = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    nse = nash_sutcliffe(obs, sim)
    assert nse == 1.0  # 完美匹配
    
    # 测试较差的匹配
    sim2 = np.array([2.0, 3.0, 4.0, 5.0, 6.0])
    nse2 = nash_sutcliffe(obs, sim2)
    assert nse2 < 1.0


def test_rmse():
    """测试RMSE"""
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sim = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    error = rmse(obs, sim)
    assert error == 0.0  # 完美匹配
    
    # 测试有误差的情况
    sim2 = np.array([1.1, 2.1, 3.1, 4.1, 5.1])
    error2 = rmse(obs, sim2)
    assert error2 > 0


def test_relative_error():
    """测试相对误差"""
    obs = np.array([10.0, 20.0, 30.0])
    sim = np.array([11.0, 22.0, 33.0])
    
    re = relative_error(obs, sim)
    expected_re = (66.0 - 60.0) / 60.0 * 100
    assert abs(re - expected_re) < 1e-6


def test_peak_error():
    """测试洪峰误差"""
    obs = np.array([1.0, 5.0, 3.0, 2.0])
    sim = np.array([1.1, 5.5, 3.1, 2.1])
    
    pe = peak_error(obs, sim)
    expected_pe = (5.5 - 5.0) / 5.0 * 100
    assert abs(pe - expected_pe) < 1e-6


def test_correlation_coefficient():
    """测试相关系数"""
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sim = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    r = correlation_coefficient(obs, sim)
    assert abs(r - 1.0) < 1e-6  # 完美相关


def test_evaluate_model():
    """测试综合评估"""
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    sim = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    
    results = evaluate_model(obs, sim)
    
    assert 'NSE' in results
    assert 'RMSE' in results
    assert 'RE' in results
    assert 'PE' in results
    assert 'R' in results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
