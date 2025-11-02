"""
测试坡面汇流模块
==============
"""

import sys
sys.path.insert(0, '..')

import numpy as np
import pytest

from code.core.slope_routing import (
    KinematicWaveSlope, LinearReservoirSlope, NashCascade
)
from code.core.slope_routing.kinematic_wave import estimate_time_of_concentration
from code.core.slope_routing.linear_reservoir import estimate_K_from_tc


def test_kinematic_wave_initialization():
    """测试运动波模型初始化"""
    params = {
        'length': 100,
        'width': 50,
        'slope': 0.01,
        'manning_n': 0.15,
        'dx': 10,
        'dt': 60
    }
    
    model = KinematicWaveSlope(params)
    
    assert model.L == 100
    assert model.W == 50
    assert model.S == 0.01
    assert model.n == 0.15
    assert model.dx == 10
    assert model.dt == 60
    assert model.nx > 0
    assert model.alpha > 0
    assert model.m == 5.0/3.0


def test_kinematic_wave_run():
    """测试运动波模型运行"""
    params = {
        'length': 100,
        'width': 50,
        'slope': 0.01,
        'manning_n': 0.15,
        'dx': 10,
        'dt': 60
    }
    
    model = KinematicWaveSlope(params)
    
    # 简单净雨过程
    runoff = np.zeros(20)
    runoff[5:15] = 30.0  # mm/h
    
    results = model.run(runoff)
    
    # 检查结果
    assert 'outlet_discharge' in results
    assert 'water_depth' in results
    assert 'x' in results
    
    assert len(results['outlet_discharge']) == 20
    assert results['water_depth'].shape[0] == 20
    
    # 检查出流量非负
    assert np.all(results['outlet_discharge'] >= 0)
    
    # 检查有峰值
    assert np.max(results['outlet_discharge']) > 0


def test_kinematic_wave_mass_balance():
    """测试运动波水量平衡"""
    params = {
        'length': 100,
        'width': 50,
        'slope': 0.01,
        'manning_n': 0.15,
        'dx': 10,
        'dt': 60
    }
    
    model = KinematicWaveSlope(params)
    
    runoff = np.zeros(30)
    runoff[5:15] = 30.0  # mm/h
    
    results = model.run(runoff)
    
    # 计算总输入
    total_input = np.sum(runoff / 1000 / 3600) * model.L * model.W * model.dt  # m³
    
    # 计算总输出
    total_output = np.sum(results['outlet_discharge']) * model.dt  # m³
    
    # 计算存储（最后时刻的水深）
    storage = np.sum(results['water_depth'][-1]) * model.dx * model.W  # m³
    
    # 水量平衡检查（误差<5%）
    balance_error = abs(total_input - total_output - storage) / total_input
    assert balance_error < 0.05


def test_linear_reservoir_initialization():
    """测试线性水库初始化"""
    params = {
        'area': 5000,
        'K': 300,
        'dt': 60
    }
    
    model = LinearReservoirSlope(params)
    
    assert model.area == 5000
    assert model.K == 300
    assert model.dt == 60
    assert model.C1 > 0
    assert model.C2 >= 0
    assert abs(model.C1 + model.C2 - 1.0) < 1e-10


def test_linear_reservoir_run():
    """测试线性水库运行"""
    params = {
        'area': 5000,
        'K': 300,
        'dt': 60
    }
    
    model = LinearReservoirSlope(params)
    
    # 简单净雨
    runoff = np.zeros(30)
    runoff[5:15] = 30.0
    
    results = model.run(runoff)
    
    assert 'discharge' in results
    assert 'storage' in results
    
    assert len(results['discharge']) == 30
    assert len(results['storage']) == 30
    
    # 出流非负
    assert np.all(results['discharge'] >= 0)
    # 存储非负
    assert np.all(results['storage'] >= 0)
    
    # 有峰值
    assert np.max(results['discharge']) > 0


def test_linear_reservoir_steady_state():
    """测试线性水库稳态"""
    params = {
        'area': 5000,
        'K': 300,
        'dt': 60
    }
    
    model = LinearReservoirSlope(params)
    
    # 恒定净雨
    runoff = np.ones(100) * 20.0  # mm/h
    
    results = model.run(runoff)
    
    # 检查最后是否接近稳态
    # 稳态时 Q = I
    steady_inflow = 20.0 / 1000 / 3600 * 5000  # m³/s
    
    # 最后几个值应该接近稳态
    assert abs(results['discharge'][-1] - steady_inflow) / steady_inflow < 0.1


def test_nash_cascade_initialization():
    """测试纳什瀑布初始化"""
    params = {
        'area': 5000,
        'K': 100,
        'n': 3,
        'dt': 60
    }
    
    model = NashCascade(params)
    
    assert model.area == 5000
    assert model.K == 100
    assert model.n == 3
    assert len(model.reservoirs) == 3


def test_nash_cascade_run():
    """测试纳什瀑布运行"""
    params = {
        'area': 5000,
        'K': 100,
        'n': 3,
        'dt': 60
    }
    
    model = NashCascade(params)
    
    runoff = np.zeros(30)
    runoff[5:15] = 30.0
    
    results = model.run(runoff)
    
    assert 'discharge' in results
    assert 'intermediate_discharge' in results
    
    # 有n级出流
    assert len(results['intermediate_discharge']) == 3
    
    # 最终出流非负
    assert np.all(results['discharge'] >= 0)
    
    # 峰值递减（调蓄效果）
    peaks = [np.max(q) for q in results['intermediate_discharge']]
    # 后级峰值应该小于前级
    for i in range(len(peaks)-1):
        assert peaks[i+1] <= peaks[i]


def test_nash_cascade_vs_single_reservoir():
    """测试纳什瀑布与单个水库的差异"""
    area = 5000
    K_total = 300
    dt = 60
    
    runoff = np.zeros(30)
    runoff[5:15] = 30.0
    
    # 单个水库
    params_single = {'area': area, 'K': K_total, 'dt': dt}
    model_single = LinearReservoirSlope(params_single)
    results_single = model_single.run(runoff)
    
    # 纳什瀑布 (n=3)
    params_nash = {'area': area, 'K': K_total/3, 'n': 3, 'dt': dt}
    model_nash = NashCascade(params_nash)
    results_nash = model_nash.run(runoff)
    
    # 纳什瀑布峰值应该小于单水库
    peak_single = np.max(results_single['discharge'])
    peak_nash = np.max(results_nash['discharge'])
    assert peak_nash < peak_single
    
    # 纳什瀑布峰现时间应该晚于单水库
    time_single = np.argmax(results_single['discharge'])
    time_nash = np.argmax(results_nash['discharge'])
    assert time_nash >= time_single


def test_estimate_time_of_concentration():
    """测试汇流时间估算"""
    length = 100
    slope = 0.01
    manning_n = 0.15
    
    tc = estimate_time_of_concentration(length, slope, manning_n)
    
    # 汇流时间应该为正
    assert tc > 0
    
    # 合理范围（经验）
    assert tc > 60  # 大于1分钟
    assert tc < 3600  # 小于1小时


def test_estimate_K_from_tc():
    """测试从汇流时间估算K"""
    tc = 600  # 10分钟
    n = 3
    
    K = estimate_K_from_tc(tc, n)
    
    assert K > 0
    assert abs(K * n - tc) < 1e-10


def test_kinematic_wave_reset():
    """测试运动波重置"""
    params = {
        'length': 100,
        'width': 50,
        'slope': 0.01,
        'manning_n': 0.15,
        'dx': 10,
        'dt': 60
    }
    
    model = KinematicWaveSlope(params)
    
    # 运行一次
    runoff = np.zeros(20)
    runoff[5:15] = 30.0
    model.run(runoff)
    
    # 重置
    model.reset()
    
    # 检查状态
    state = model.get_state()
    assert np.all(state['h'] == 0)


def test_linear_reservoir_state():
    """测试线性水库状态管理"""
    params = {
        'area': 5000,
        'K': 300,
        'dt': 60
    }
    
    model = LinearReservoirSlope(params)
    
    # 获取初始状态
    initial_state = model.get_state()
    assert initial_state['Q'] == 0
    assert initial_state['S'] == 0
    
    # 设置状态
    new_state = {'Q': 0.1, 'S': 30}
    model.set_state(new_state)
    
    # 验证
    state = model.get_state()
    assert state['Q'] == 0.1
    assert state['S'] == 30


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
