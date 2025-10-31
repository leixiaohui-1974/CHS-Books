#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例2单元测试
Test Case 02: Pump Station Intelligent Design

测试内容：
1. 泵模型功能测试
2. PID控制器测试
3. 多泵协调控制器测试
4. 数字孪生仿真测试
5. 在环测试场景验证
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code/examples/case_02_pump_station'))

import pytest
import numpy as np

from main import (
    Pump,
    SimplePIDController,
    MultiPumpController,
    PumpStationDigitalTwin,
    create_test_scenarios,
    run_hil_test
)


class TestPump:
    """泵模型测试"""
    
    def test_pump_initialization(self):
        """测试泵初始化"""
        pump = Pump(Q_rated=1.2, H_rated=15.0, P_rated=80.0, pump_id=1)
        
        assert pump.Q_rated == 1.2
        assert pump.H_rated == 15.0
        assert pump.P_rated == 80.0
        assert pump.pump_id == 1
        assert 0.75 < pump.eta_rated < 0.80
    
    def test_pump_operating_point(self):
        """测试工况点计算"""
        pump = Pump()
        
        # 额定工况
        H, eta, P = pump.compute_operating_point(Q=1.2)
        assert 14.5 < H < 15.5  # 扬程应接近15m
        assert eta > 0.75       # 效率应>75%
        assert 75 < P < 85      # 功率应接近80kW
        
        # 小流量工况（扬程应增加）
        H_small, eta_small, P_small = pump.compute_operating_point(Q=0.6)
        assert H_small > H
        
        # 大流量工况（扬程应减小）
        H_large, eta_large, P_large = pump.compute_operating_point(Q=1.5)
        assert H_large < H
    
    def test_pump_statistics(self):
        """测试运行统计"""
        pump = Pump()
        
        # 运行1小时
        for _ in range(60):
            pump.update_statistics(is_running=True, dt=60)
        
        assert pump.total_run_time > 0.9  # 接近1小时
        assert pump.total_energy > 70     # 接近80kWh


class TestPIDController:
    """PID控制器测试"""
    
    def test_pid_initialization(self):
        """测试PID初始化"""
        pid = SimplePIDController(
            Kp=1.5, Ki=0.3, Kd=0.05,
            setpoint=3.5,
            output_limits=(0, 3)
        )
        
        assert pid.Kp == 1.5
        assert pid.Ki == 0.3
        assert pid.Kd == 0.05
        assert pid.setpoint == 3.5
    
    def test_pid_proportional_control(self):
        """测试比例控制"""
        pid = SimplePIDController(
            Kp=1.0, Ki=0, Kd=0,
            setpoint=3.5,
            output_limits=(0, 3)
        )
        
        # 水位低于目标，应输出正值
        output = pid.update(measured_value=3.0, dt=1.0)
        assert output > 0
        
        # 水位高于目标，应输出0（限幅）
        output = pid.update(measured_value=4.0, dt=1.0)
        assert output == 0
    
    def test_pid_integral_windup(self):
        """测试积分抗饱和"""
        pid = SimplePIDController(
            Kp=1.0, Ki=1.0, Kd=0,
            setpoint=3.5,
            output_limits=(0, 3),
            windup_limit=2.0
        )
        
        # 持续大误差
        for _ in range(10):
            pid.update(measured_value=1.0, dt=1.0)
        
        # 积分项应被限制
        assert abs(pid.integral) <= 2.0


class TestMultiPumpController:
    """多泵控制器测试"""
    
    def test_controller_initialization(self):
        """测试控制器初始化"""
        controller = MultiPumpController(n_pumps=3)
        
        assert controller.n_pumps == 3
        assert len(controller.pump_status) == 3
        assert sum(controller.pump_status) == 0  # 初始全停
    
    def test_pump_start_logic(self):
        """测试启泵逻辑"""
        controller = MultiPumpController(
            n_pumps=3,
            Kp=2.0, Ki=0, Kd=0,  # 只用比例控制
            setpoint=3.5,
            min_run_time=0,     # 关闭保护，方便测试
            min_stop_time=0
        )
        
        # 水位很低，应启泵
        status = controller.update(water_level=2.5, dt=1.0)
        assert sum(status) > 0
    
    def test_pump_rotation(self):
        """测试轮换运行"""
        controller = MultiPumpController(
            n_pumps=3,
            min_run_time=0,
            min_stop_time=0
        )
        
        # 手动设置不同运行时间
        controller.pump_run_time = [100, 50, 10]  # 泵#1最多，泵#3最少
        controller.pump_status = [0, 0, 0]
        
        # 需要启动1台泵，应选择运行时间最短的泵#3
        controller._start_pumps(1)
        assert controller.pump_status[2] == 1  # 泵#3启动
    
    def test_minimum_run_time_protection(self):
        """测试最小运行时间保护"""
        controller = MultiPumpController(
            n_pumps=3,
            min_run_time=300  # 5分钟
        )
        
        # 启动泵#1
        controller.pump_status = [1, 0, 0]
        controller.last_switch_time[0] = 0
        controller.current_time = 0
        
        # 尝试立即停止（应被阻止）
        controller.current_time = 60  # 只过了1分钟
        controller._stop_pumps(1)
        assert controller.pump_status[0] == 1  # 仍在运行
        
        # 5分钟后停止（应成功）
        controller.current_time = 360
        controller._stop_pumps(1)
        assert controller.pump_status[0] == 0  # 已停止


class TestDigitalTwin:
    """数字孪生测试"""
    
    def test_twin_initialization(self):
        """测试数字孪生初始化"""
        pumps = [Pump(pump_id=i+1) for i in range(3)]
        controller = MultiPumpController(n_pumps=3)
        twin = PumpStationDigitalTwin(pumps, controller)
        
        assert twin.inlet_level == 3.5
        assert twin.outlet_level == 2.0
        assert twin.t == 0
    
    def test_water_balance(self):
        """测试水量平衡"""
        pumps = [Pump(pump_id=i+1) for i in range(3)]
        controller = MultiPumpController(n_pumps=3, Kp=0, Ki=0, Kd=0)  # 关闭控制
        twin = PumpStationDigitalTwin(pumps, controller)
        
        initial_level = twin.inlet_level
        
        # 只进水，不抽水
        twin.step(inflow=2.0, demand=0)
        assert twin.inlet_level > initial_level  # 水位应上升
        
        # 只抽水，不进水（需要手动开泵）
        controller.pump_status = [1, 1, 0]
        twin.step(inflow=0, demand=3.0)
        # 注：这里水位变化取决于控制器
    
    def test_simulation_run(self):
        """测试仿真运行"""
        pumps = [Pump(pump_id=i+1) for i in range(3)]
        controller = MultiPumpController(n_pumps=3)
        twin = PumpStationDigitalTwin(pumps, controller)
        
        # 运行1小时仿真
        history = twin.simulate(
            duration=3600,
            inflow_func=lambda t: 2.0,
            demand_func=lambda t: 3.0,
            verbose=False
        )
        
        assert len(history['t']) == 60  # 60个时间步（每步60秒）
        assert 't' in history
        assert 'inlet_level' in history
        assert 'pump_status' in history


class TestHILScenarios:
    """在环测试场景测试"""
    
    def test_scenario_generation(self):
        """测试场景生成"""
        scenarios = create_test_scenarios()
        
        assert len(scenarios) >= 5
        for scenario in scenarios:
            assert 'name' in scenario
            assert 'duration' in scenario
            assert 'inflow' in scenario
            assert 'demand' in scenario
    
    def test_run_single_scenario(self):
        """测试单个场景运行"""
        scenarios = create_test_scenarios()
        results = run_hil_test([scenarios[0]], verbose=False)
        
        assert len(results) == 1
        result = results[0]
        assert 'scenario' in result
        assert 'metrics' in result
        assert 'history' in result
    
    @pytest.mark.slow
    def test_run_all_scenarios(self):
        """测试全部场景运行（标记为慢测试）"""
        scenarios = create_test_scenarios()
        results = run_hil_test(scenarios, verbose=False)
        
        assert len(results) == len(scenarios)
        
        # 检查所有场景都有性能指标
        for result in results:
            metrics = result['metrics']
            assert 'inlet_level_mean' in metrics
            assert 'steady_state_error' in metrics
            assert 'total_switches' in metrics


class TestPerformanceMetrics:
    """性能指标测试"""
    
    def test_metrics_calculation(self):
        """测试性能指标计算"""
        pumps = [Pump(pump_id=i+1) for i in range(3)]
        controller = MultiPumpController(n_pumps=3)
        twin = PumpStationDigitalTwin(pumps, controller)
        
        # 运行短时间仿真
        twin.simulate(
            duration=600,  # 10分钟
            inflow_func=lambda t: 2.0,
            demand_func=lambda t: 3.0,
            verbose=False
        )
        
        # 计算性能指标
        metrics = twin.calculate_performance_metrics()
        
        # 检查所有指标都存在
        expected_keys = [
            'inlet_level_mean', 'inlet_level_std',
            'inlet_level_max', 'inlet_level_min',
            'steady_state_error', 'total_switches',
            'total_energy_kwh', 'overflow_count', 'dryout_count'
        ]
        for key in expected_keys:
            assert key in metrics
        
        # 检查数值合理性
        assert 0 < metrics['inlet_level_mean'] < 6
        assert metrics['inlet_level_std'] >= 0
        assert metrics['total_switches'] >= 0
        assert metrics['total_energy_kwh'] >= 0


# ========================================
# Pytest配置
# ========================================

@pytest.fixture
def sample_pump():
    """创建示例泵"""
    return Pump(Q_rated=1.2, H_rated=15.0, P_rated=80.0, pump_id=1)


@pytest.fixture
def sample_controller():
    """创建示例控制器"""
    return MultiPumpController(n_pumps=3)


@pytest.fixture
def sample_twin():
    """创建示例数字孪生"""
    pumps = [Pump(pump_id=i+1) for i in range(3)]
    controller = MultiPumpController(n_pumps=3)
    return PumpStationDigitalTwin(pumps, controller)


# ========================================
# 运行测试
# ========================================

if __name__ == '__main__':
    # 运行所有测试
    pytest.main([__file__, '-v', '--tb=short'])
