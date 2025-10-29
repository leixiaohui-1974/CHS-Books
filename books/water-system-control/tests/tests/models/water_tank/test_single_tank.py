"""
SingleTank模型单元测试

测试内容：
1. 初始化参数验证
2. 基本功能测试
3. 物理约束测试
4. 数学特性测试
"""

import pytest
import numpy as np
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.models.water_tank.single_tank import SingleTank, simulate_open_loop, calculate_step_response_metrics


class TestSingleTankInitialization:
    """测试初始化"""
    
    def test_default_initialization(self):
        """测试默认参数初始化"""
        tank = SingleTank()
        assert tank.A == 2.0
        assert tank.R == 2.0
        assert tank.K == 1.0
        assert tank.h == 2.0
        assert tank.t == 0.0
    
    def test_custom_initialization(self):
        """测试自定义参数初始化"""
        tank = SingleTank(A=3.0, R=1.5, K=2.0)
        assert tank.A == 3.0
        assert tank.R == 1.5
        assert tank.K == 2.0
    
    def test_invalid_parameters(self):
        """测试无效参数应该抛出异常"""
        with pytest.raises(ValueError):
            SingleTank(A=0)  # 零面积
        
        with pytest.raises(ValueError):
            SingleTank(A=-1)  # 负面积
        
        with pytest.raises(ValueError):
            SingleTank(R=-1)  # 负阻力
        
        with pytest.raises(ValueError):
            SingleTank(K=-1)  # 负增益
    
    def test_derived_parameters(self):
        """测试派生参数计算"""
        tank = SingleTank(A=2.0, R=3.0, K=1.5)
        assert tank.tau == 2.0 * 3.0  # τ = A×R
        assert tank.steady_state_gain == 1.5 * 3.0  # K×R


class TestSingleTankBasicFunctions:
    """测试基本功能"""
    
    def test_compute_flow_out(self):
        """测试出水流量计算"""
        tank = SingleTank(R=2.0)
        
        # 正常情况
        assert tank.compute_flow_out(4.0) == 2.0
        assert tank.compute_flow_out(2.0) == 1.0
        
        # 零水位
        assert tank.compute_flow_out(0.0) == 0.0
        
        # 负水位（边界情况）
        assert tank.compute_flow_out(-1.0) == 0.0
    
    def test_compute_level_change_rate(self):
        """测试水位变化速度计算"""
        tank = SingleTank(A=2.0, R=2.0)
        
        # Q_in = 2.0, h = 2.0 → Q_out = 1.0
        # dh/dt = (2.0 - 1.0) / 2.0 = 0.5
        dh_dt = tank.compute_level_change_rate(h=2.0, Q_in=2.0)
        assert abs(dh_dt - 0.5) < 1e-10
        
        # 稳态：Q_in = Q_out
        dh_dt = tank.compute_level_change_rate(h=2.0, Q_in=1.0)
        assert abs(dh_dt) < 1e-10
    
    def test_step_function(self):
        """测试单步仿真"""
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=1.0)  # 从较低水位开始
        
        # 全速抽水（从1.0m开始，应该上升）
        h_new = tank.step(u=1.0, dt=0.1)
        assert h_new > 1.0  # 水位应该上升
        assert tank.t == 0.1  # 时间应该更新
        
        # 关闭泵
        tank.reset(h0=2.0)
        h_new = tank.step(u=0.0, dt=0.1)
        assert h_new < 2.0  # 水位应该下降（自然流出）
    
    def test_reset_function(self):
        """测试重置功能"""
        tank = SingleTank()
        tank.h = 5.0
        tank.t = 10.0
        
        tank.reset(h0=3.0)
        assert tank.h == 3.0
        assert tank.t == 0.0


class TestSingleTankPhysicalConstraints:
    """测试物理约束"""
    
    def test_water_level_non_negative(self):
        """测试水位不能为负"""
        tank = SingleTank()
        tank.reset(h0=0.1)
        
        # 大量流出，水位应该停在0而不是负数
        for _ in range(100):
            tank.step(u=0.0, dt=0.1)
        
        assert tank.h >= 0.0
    
    def test_control_input_clamping(self):
        """测试控制输入限幅"""
        tank = SingleTank()
        
        # 超过1.0应该被限制
        h1 = tank.step(u=2.0, dt=0.1)
        tank.reset()
        h2 = tank.step(u=1.0, dt=0.1)
        assert abs(h1 - h2) < 1e-10
        
        # 负值应该被限制为0
        tank.reset(h0=2.0)
        h1 = tank.step(u=-1.0, dt=0.1)
        tank.reset(h0=2.0)
        h2 = tank.step(u=0.0, dt=0.1)
        assert abs(h1 - h2) < 1e-10


class TestSingleTankMathematicalProperties:
    """测试数学特性"""
    
    def test_linearity(self):
        """测试系统线性性"""
        tank1 = SingleTank(A=2.0, R=2.0, K=1.0)
        tank2 = SingleTank(A=2.0, R=2.0, K=1.0)
        
        tank1.reset(h0=0.0)
        tank2.reset(h0=0.0)
        
        # tank1: u=0.5, tank2: u=1.0
        for _ in range(100):
            tank1.step(u=0.5, dt=0.1)
            tank2.step(u=1.0, dt=0.1)
        
        # tank2的水位应该约为tank1的2倍
        ratio = tank2.h / tank1.h if tank1.h > 0 else 0
        assert abs(ratio - 2.0) < 0.01
    
    def test_state_space_matrices(self):
        """测试状态空间矩阵"""
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        A, B, C, D = tank.get_state_space_matrices()
        
        # 检查形状
        assert A.shape == (1, 1)
        assert B.shape == (1, 1)
        assert C.shape == (1, 1)
        assert D.shape == (1, 1)
        
        # 检查值
        assert abs(A[0,0] + 1/tank.tau) < 1e-10
        assert abs(B[0,0] - tank.K/tank.A) < 1e-10
        assert C[0,0] == 1.0
        assert D[0,0] == 0.0
    
    def test_transfer_function(self):
        """测试传递函数"""
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tf = tank.get_transfer_function()
        
        assert tf['gain'] == tank.steady_state_gain
        assert tf['tau'] == tank.tau
        assert len(tf['num']) == 1
        assert len(tf['den']) == 2


class TestSimulationHelpers:
    """测试仿真辅助函数"""
    
    def test_simulate_open_loop(self):
        """测试开环仿真"""
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=0.0)
        
        u_sequence = np.ones(100)
        t, h, Q_in, Q_out = simulate_open_loop(tank, u_sequence, dt=0.1)
        
        # 检查返回数组长度
        assert len(t) == 100
        assert len(h) == 100
        assert len(Q_in) == 100
        assert len(Q_out) == 100
        
        # 检查单调性（对于阶跃输入，水位应该单调上升）
        assert all(h[i+1] >= h[i] for i in range(len(h)-1))
    
    def test_calculate_step_response_metrics(self):
        """测试性能指标计算"""
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=0.0)
        
        u_sequence = np.ones(200)
        t, h, _, _ = simulate_open_loop(tank, u_sequence, dt=0.1)
        
        metrics = calculate_step_response_metrics(t, h, tank.steady_state_gain, 0.1)
        
        # 检查指标存在
        assert 'rise_time' in metrics
        assert 'settling_time' in metrics
        assert 'overshoot' in metrics
        assert 'steady_state_error' in metrics
        
        # 一阶系统不应该有超调
        assert metrics['overshoot'] == 0.0


if __name__ == "__main__":
    """运行所有测试"""
    pytest.main([__file__, "-v", "-s"])
