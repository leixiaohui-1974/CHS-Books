"""
测试新安江模型
============
"""

import sys
sys.path.insert(0, '..')

import numpy as np
import pytest

from code.core.runoff_generation import XinAnJiangModel, create_default_xaj_params


def test_create_default_params():
    """测试默认参数创建"""
    params = create_default_xaj_params('humid')
    
    assert 'K' in params
    assert 'WM' in params
    assert 'B' in params
    assert params['WM'] > 0
    assert 0 < params['B'] < 1


def test_xaj_model_initialization():
    """测试模型初始化"""
    params = create_default_xaj_params('humid')
    model = XinAnJiangModel(params)
    
    assert model.params == params
    assert 'W' in model.state
    assert 'S' in model.state
    assert model.state['W'] >= 0
    assert model.state['S'] >= 0


def test_xaj_model_run():
    """测试模型运行"""
    params = create_default_xaj_params('humid')
    model = XinAnJiangModel(params)
    
    # 创建简单测试数据
    P = np.array([10, 20, 15, 5, 0])
    EM = np.array([5, 5, 5, 5, 5])
    
    results = model.run(P, EM)
    
    # 检查输出
    assert 'Q' in results
    assert 'R' in results
    assert 'E' in results
    assert len(results['Q']) == len(P)
    assert np.all(results['Q'] >= 0)
    assert np.all(results['R'] >= 0)
    assert np.all(results['E'] >= 0)


def test_water_balance():
    """测试水量平衡"""
    params = create_default_xaj_params('humid')
    model = XinAnJiangModel(params)
    
    P = np.array([10, 20, 15, 5, 0, 0, 0])
    EM = np.array([5, 5, 5, 5, 5, 5, 5])
    
    results = model.run(P, EM)
    
    # 水量平衡: P = E + R + ΔW
    P_total = P.sum()
    E_total = results['E'].sum()
    R_total = results['R'].sum()
    W0 = params.get('W0', params['WM'] * 0.6)
    W_final = results['W'][-1]
    dW = W_final - W0
    
    balance_error = P_total - E_total - R_total - dW
    
    # 允许小的数值误差
    assert abs(balance_error) < 1e-6


def test_parameter_sensitivity():
    """测试参数敏感性"""
    params1 = create_default_xaj_params('humid')
    params2 = params1.copy()
    params2['B'] = params1['B'] * 1.5  # 增大B参数
    
    P = np.array([10, 20, 15, 5, 0])
    EM = np.array([5, 5, 5, 5, 5])
    
    model1 = XinAnJiangModel(params1)
    model2 = XinAnJiangModel(params2)
    
    results1 = model1.run(P, EM)
    results2 = model2.run(P, EM)
    
    # B增大应该导致产流增加
    assert results2['R'].sum() > results1['R'].sum()


def test_model_reset():
    """测试模型重置"""
    params = create_default_xaj_params('humid')
    model = XinAnJiangModel(params)
    
    P = np.array([10, 20, 15])
    EM = np.array([5, 5, 5])
    
    # 第一次运行
    results1 = model.run(P, EM)
    state_after = model.get_state()
    
    # 重置
    model.reset()
    state_reset = model.get_state()
    
    # 第二次运行
    results2 = model.run(P, EM)
    
    # 重置后的结果应该与第一次相同
    np.testing.assert_array_almost_equal(results1['R'], results2['R'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
