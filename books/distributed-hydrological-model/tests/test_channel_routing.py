"""
测试河道汇流模块
==============
"""

import sys
sys.path.insert(0, '..')

import numpy as np
import pytest

from code.core.channel_routing import (
    UnitHydrograph, create_snyder_uh, create_scs_uh,
    create_triangular_uh, MuskingumChannel
)


def test_unit_hydrograph_initialization():
    """测试单元线初始化"""
    uh = np.array([0, 0.5, 1.0, 0.5, 0])
    dt = 1.0
    
    model = UnitHydrograph(uh, dt)
    
    assert len(model.uh) == 5
    assert model.dt == 1.0
    assert model.n == 5


def test_unit_hydrograph_run():
    """测试单元线运行"""
    uh = np.array([0, 0.5, 1.0, 0.5, 0])
    dt = 1.0
    model = UnitHydrograph(uh, dt)
    
    runoff = np.array([10, 20, 10])  # mm
    results = model.run(runoff)
    
    assert 'discharge' in results
    assert 'time' in results
    assert len(results['discharge']) == len(runoff) + len(uh) - 1
    assert np.all(results['discharge'] >= 0)


def test_triangular_uh():
    """测试三角形单元线"""
    basin_area = 100
    tp = 5
    tb = 15
    dt = 1.0
    
    uh = create_triangular_uh(basin_area, tp, tb, dt)
    
    assert len(uh) > 0
    assert np.all(uh >= 0)
    
    # 检查峰值位置
    peak_idx = np.argmax(uh)
    peak_time = peak_idx * dt
    assert abs(peak_time - tp) <= dt


def test_snyder_uh():
    """测试Snyder单元线"""
    basin_area = 100
    L = 20
    Lc = 10
    dt = 1.0
    
    uh, tp = create_snyder_uh(basin_area, L, Lc, dt=dt)
    
    assert len(uh) > 0
    assert tp > 0
    assert np.all(uh >= 0)
    
    # 检查峰现时间合理性
    peak_time = np.argmax(uh) * dt
    assert abs(peak_time - tp) < 2  # 允许2小时误差


def test_scs_uh():
    """测试SCS单元线"""
    basin_area = 100
    tc = 8
    dt = 1.0
    
    uh = create_scs_uh(basin_area, tc, dt)
    
    assert len(uh) > 0
    assert np.all(uh >= 0)
    
    # 峰现时间应该约为0.6*tc
    peak_time = np.argmax(uh) * dt
    expected_tp = 0.6 * tc
    assert abs(peak_time - expected_tp) < 2


def test_muskingum_initialization():
    """测试Muskingum初始化"""
    params = {
        'K': 6.0,
        'X': 0.25,
        'dt': 1.0
    }
    
    model = MuskingumChannel(params)
    
    assert model.K == 6.0
    assert model.X == 0.25
    assert model.dt == 1.0
    
    # 检查系数和为1
    coef_sum = model.C0 + model.C1 + model.C2
    assert abs(coef_sum - 1.0) < 1e-6


def test_muskingum_run():
    """测试Muskingum运行"""
    params = {'K': 6.0, 'X': 0.25, 'dt': 1.0}
    model = MuskingumChannel(params)
    
    # 简单入流
    inflow = np.array([100, 200, 300, 200, 100, 50, 0, 0, 0, 0])
    
    results = model.run(inflow)
    
    assert 'outflow' in results
    assert 'storage' in results
    assert 'attenuation' in results
    assert 'lag' in results
    
    assert len(results['outflow']) == len(inflow)
    assert np.all(results['outflow'] >= 0)


def test_muskingum_attenuation():
    """测试Muskingum削峰效果"""
    params = {'K': 6.0, 'X': 0.25, 'dt': 1.0}
    model = MuskingumChannel(params)
    
    # 三角形入流
    inflow = np.zeros(20)
    inflow[5:10] = [100, 200, 300, 200, 100]
    
    results = model.run(inflow)
    
    # 出流峰值应小于入流峰值
    peak_in = np.max(inflow)
    peak_out = np.max(results['outflow'])
    assert peak_out < peak_in
    
    # 削峰率应该为正
    assert results['attenuation'] > 0


def test_muskingum_lag():
    """测试Muskingum滞时效果"""
    params = {'K': 6.0, 'X': 0.25, 'dt': 1.0}
    model = MuskingumChannel(params)
    
    inflow = np.zeros(20)
    inflow[5:10] = [100, 200, 300, 200, 100]
    
    results = model.run(inflow)
    
    # 出流峰现时间应晚于入流
    time_peak_in = np.argmax(inflow)
    time_peak_out = np.argmax(results['outflow'])
    assert time_peak_out >= time_peak_in
    
    # 滞时应该为正或零
    assert results['lag'] >= 0


def test_muskingum_mass_balance():
    """测试Muskingum水量平衡"""
    params = {'K': 6.0, 'X': 0.25, 'dt': 1.0}
    model = MuskingumChannel(params)
    
    inflow = np.zeros(30)
    inflow[5:15] = 200  # 恒定入流
    
    results = model.run(inflow)
    
    # 计算总入流和总出流
    total_in = np.sum(inflow) * params['dt'] * 3600  # m³
    total_out = np.sum(results['outflow']) * params['dt'] * 3600  # m³
    final_storage = results['storage'][-1]  # m³
    
    # 水量平衡检查（误差<1%）
    balance_error = abs(total_in - total_out - final_storage) / total_in
    assert balance_error < 0.01


def test_muskingum_stability_warning():
    """测试Muskingum稳定性警告"""
    # 不稳定的参数组合
    params = {
        'K': 6.0,
        'X': 0.3,
        'dt': 10.0  # 太大
    }
    
    # 应该产生警告但不报错
    with pytest.warns(UserWarning):
        model = MuskingumChannel(params)


def test_unit_hydrograph_convolution():
    """测试单元线卷积的正确性"""
    # 简单情况：单位净雨应该得到原始单元线
    uh = np.array([0, 1, 2, 1, 0])
    dt = 1.0
    model = UnitHydrograph(uh, dt)
    
    # 单位净雨
    runoff = np.array([1])
    results = model.run(runoff)
    
    # 结果应该与单元线相同
    assert len(results['discharge']) >= len(uh)
    np.testing.assert_array_almost_equal(
        results['discharge'][:len(uh)], uh * 1
    )


def test_muskingum_steady_state():
    """测试Muskingum稳态"""
    params = {'K': 6.0, 'X': 0.25, 'dt': 1.0}
    model = MuskingumChannel(params)
    
    # 恒定入流
    inflow = np.ones(50) * 200
    
    results = model.run(inflow)
    
    # 最终应该接近稳态（出流≈入流）
    assert abs(results['outflow'][-1] - inflow[-1]) / inflow[-1] < 0.05


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
