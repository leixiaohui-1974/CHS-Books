"""
DoubleTank模型单元测试

测试内容：
1. 初始化参数验证
2. 基本功能测试
3. 物理约束测试
4. 二阶系统特性测试
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.models.water_tank.double_tank import DoubleTank, simulate_double_tank


class TestDoubleTankInitialization:
    """测试初始化"""
    
    def test_default_initialization(self):
        """测试默认参数"""
        tank = DoubleTank()
        assert tank.A1 == 1.0
        assert tank.A2 == 2.0
        assert tank.R1 == 1.0
        assert tank.R2 == 2.0
        assert tank.K == 1.0
    
    def test_custom_initialization(self):
        """测试自定义参数"""
        tank = DoubleTank(A1=2.0, A2=3.0, R1=1.5, R2=2.5, K=2.0)
        assert tank.A1 == 2.0
        assert tank.A2 == 3.0
        assert tank.R1 == 1.5
        assert tank.R2 == 2.5
        assert tank.K == 2.0
    
    def test_invalid_parameters(self):
        """测试无效参数"""
        with pytest.raises(ValueError):
            DoubleTank(A1=0)
        with pytest.raises(ValueError):
            DoubleTank(A2=-1)
        with pytest.raises(ValueError):
            DoubleTank(R1=-1)
        with pytest.raises(ValueError):
            DoubleTank(K=-1)
    
    def test_system_characteristics(self):
        """测试系统特性计算"""
        tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0)
        
        # 时间常数
        assert tank.tau1 == 1.0
        assert tank.tau2 == 4.0
        
        # 自然频率和阻尼比
        assert abs(tank.omega_n - 0.5) < 1e-6
        assert abs(tank.zeta - 1.25) < 1e-6


class TestDoubleTankBasicFunctions:
    """测试基本功能"""
    
    def test_compute_flows(self):
        """测试流量计算"""
        tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0, K=1.0)
        
        # 正常情况
        Q_in, Q_12, Q_out = tank.compute_flows(h1=2.0, h2=1.0, u=1.0)
        assert Q_in == 1.0  # K * u
        assert Q_12 == 2.0  # h1 / R1
        assert Q_out == 0.5 # h2 / R2
    
    def test_compute_derivatives(self):
        """测试导数计算"""
        tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0, K=1.0)
        
        dh1_dt, dh2_dt = tank.compute_derivatives(h1=2.0, h2=1.0, u=1.0)
        
        # dh1/dt = (Q_in - Q_12) / A1 = (1.0 - 2.0) / 1.0 = -1.0
        assert abs(dh1_dt - (-1.0)) < 1e-6
        
        # dh2/dt = (Q_12 - Q_out) / A2 = (2.0 - 0.5) / 2.0 = 0.75
        assert abs(dh2_dt - 0.75) < 1e-6
    
    def test_step_function(self):
        """测试单步仿真"""
        tank = DoubleTank()
        tank.reset(h1_0=1.0, h2_0=1.0)
        
        h1_new, h2_new = tank.step(u=1.0, dt=0.1)
        
        # 水位应该变化
        assert h1_new != 1.0 or h2_new != 1.0
        # 时间应该更新
        assert tank.t == 0.1
    
    def test_reset_function(self):
        """测试重置功能"""
        tank = DoubleTank()
        tank.h1 = 5.0
        tank.h2 = 3.0
        tank.t = 10.0
        
        tank.reset(h1_0=2.0, h2_0=1.5)
        assert tank.h1 == 2.0
        assert tank.h2 == 1.5
        assert tank.t == 0.0


class TestDoubleTankPhysicalConstraints:
    """测试物理约束"""
    
    def test_water_levels_non_negative(self):
        """测试水位不能为负"""
        tank = DoubleTank()
        tank.reset(h1_0=0.1, h2_0=0.1)
        
        # 大量流出
        for _ in range(100):
            tank.step(u=0.0, dt=0.1)
        
        assert tank.h1 >= 0.0
        assert tank.h2 >= 0.0
    
    def test_flow_non_negative(self):
        """测试流量不能为负"""
        tank = DoubleTank()
        
        # 负水位情况
        Q_in, Q_12, Q_out = tank.compute_flows(h1=-1.0, h2=-1.0, u=1.0)
        
        assert Q_in >= 0
        assert Q_12 >= 0
        assert Q_out >= 0


class TestDoubleTankSystemProperties:
    """测试二阶系统特性"""
    
    def test_state_space_dimensions(self):
        """测试状态空间矩阵维度"""
        tank = DoubleTank()
        A, B, C, D = tank.get_state_space_matrices()
        
        assert A.shape == (2, 2)
        assert B.shape == (2, 1)
        assert C.shape == (1, 2)
        assert D.shape == (1, 1)
    
    def test_state_space_values(self):
        """测试状态空间矩阵值"""
        tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0, K=1.0)
        A, B, C, D = tank.get_state_space_matrices()
        
        # A矩阵
        assert abs(A[0, 0] - (-1.0)) < 1e-6  # -1/tau1
        assert abs(A[0, 1] - 0) < 1e-6
        assert abs(A[1, 0] - 0.5) < 1e-6     # 1/(A2*R1)
        assert abs(A[1, 1] - (-0.25)) < 1e-6 # -1/tau2
        
        # B矩阵
        assert abs(B[0, 0] - 1.0) < 1e-6     # K/A1
        assert abs(B[1, 0] - 0) < 1e-6
        
        # C矩阵（测量h2）
        assert C[0, 0] == 0
        assert C[0, 1] == 1
        
        # D矩阵
        assert D[0, 0] == 0
    
    def test_poles_calculation(self):
        """测试极点计算"""
        tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0)
        poles = tank.get_poles()
        
        # 应该有2个极点
        assert len(poles) == 2
        
        # 所有极点应该在左半平面（稳定系统）
        assert all(np.real(p) < 0 for p in poles)
    
    def test_damping_ratio(self):
        """测试阻尼比分类"""
        # 过阻尼系统
        tank1 = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0)
        assert tank1.zeta > 1.0
        
        # 欠阻尼系统（调整参数使阻尼比<1）
        tank2 = DoubleTank(A1=1.0, A2=1.0, R1=2.0, R2=2.0)
        # tau1=2, tau2=2, zeta = (2+2)/(2*2) = 1.0 (临界阻尼)
        assert abs(tank2.zeta - 1.0) < 0.1
    
    def test_transfer_function(self):
        """测试传递函数"""
        tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0, K=1.0)
        tf = tank.get_transfer_function()
        
        # 应该有必要的字段
        assert 'num' in tf
        assert 'den' in tf
        assert 'omega_n' in tf
        assert 'zeta' in tf
        
        # 分母应该是二阶（3个系数）
        assert len(tf['den']) == 3


class TestDoubleTankSimulation:
    """测试仿真功能"""
    
    def test_simulate_double_tank(self):
        """测试仿真辅助函数"""
        tank = DoubleTank()
        tank.reset(h1_0=0, h2_0=0)
        
        u_sequence = np.ones(100)
        t, h1, h2, Q_in, Q_12, Q_out = simulate_double_tank(tank, u_sequence, dt=0.1)
        
        # 检查返回数组长度
        assert len(t) == 100
        assert len(h1) == 100
        assert len(h2) == 100
        
        # 阶跃输入下，h1和h2应该上升
        assert h1[-1] > h1[0]
        assert h2[-1] > h2[0]
    
    def test_response_order(self):
        """测试响应顺序（上水箱先响应）"""
        tank = DoubleTank()
        tank.reset(h1_0=0, h2_0=0)
        
        u_sequence = np.ones(50)
        t, h1, h2, _, _, _ = simulate_double_tank(tank, u_sequence, dt=0.1)
        
        # 找到h1和h2达到10%最终值的时间
        h1_10_idx = np.where(h1 >= 0.1 * h1[-1])[0]
        h2_10_idx = np.where(h2 >= 0.1 * h2[-1])[0]
        
        if len(h1_10_idx) > 0 and len(h2_10_idx) > 0:
            # 上水箱应该先响应
            assert h1_10_idx[0] < h2_10_idx[0]


if __name__ == "__main__":
    """运行所有测试"""
    pytest.main([__file__, "-v", "-s"])
