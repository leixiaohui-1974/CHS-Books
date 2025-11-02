"""
测试反应动力学模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.reaction import ReactionKinetics, ReactionTransport1D


class TestReactionKinetics:
    """测试反应动力学模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = ReactionKinetics(T=100.0, nt=1000, k=0.1, n=1)
        
        assert model.T == 100.0
        assert model.nt == 1000
        assert model.k == 0.1
        assert model.n == 1
        
        assert len(model.t) == 1000
        assert len(model.C) == 1000
    
    def test_zero_order(self):
        """测试零阶反应"""
        C0 = 50.0
        k = 1.0
        T = 30.0
        
        model = ReactionKinetics(T=T, nt=300, k=k, n=0)
        model.set_initial_condition(C0)
        C = model.solve_zero_order()
        
        # 检查浓度非负
        assert np.all(C >= -1e-10)
        
        # 零阶反应应该线性下降
        # 理论：C(t) = C0 - k*t
        t_half = C0 / (2 * k)
        idx_half = int(t_half / model.dt)
        if idx_half < len(C):
            assert C[idx_half] < C0 / 2 + 5  # 允许误差
    
    def test_first_order(self):
        """测试一阶反应"""
        C0 = 50.0
        k = 0.1
        T = 50.0
        
        model = ReactionKinetics(T=T, nt=500, k=k, n=1)
        model.set_initial_condition(C0)
        C = model.solve_first_order()
        
        # 检查浓度非负
        assert np.all(C >= -1e-10)
        
        # 一阶反应应该指数下降
        # 理论：C(t) = C0 * exp(-k*t)
        C_theory = model.analytical_first_order(model.t)
        
        # 数值解应该接近解析解
        error = np.abs(C - C_theory)
        assert np.max(error) < 1.0  # 最大误差 < 1 mg/L
    
    def test_second_order(self):
        """测试二阶反应"""
        C0 = 50.0
        k = 0.001
        T = 50.0
        
        model = ReactionKinetics(T=T, nt=500, k=k, n=2)
        model.set_initial_condition(C0)
        C = model.solve_second_order()
        
        # 检查浓度非负
        assert np.all(C >= -1e-10)
        
        # 二阶反应应该满足：C(t) = C0 / (1 + k*C0*t)
        C_theory = model.analytical_second_order(model.t)
        
        # 数值解应该接近解析解
        error = np.abs(C - C_theory)
        assert np.max(error) < 1.0
    
    def test_monod_kinetics(self):
        """测试Monod动力学"""
        C0 = 50.0
        k_max = 2.0
        K_s = 10.0
        T = 10.0
        
        model = ReactionKinetics(T=T, nt=100, k=k_max, n=1)
        model.set_initial_condition(C0)
        C = model.solve_monod(K_s=K_s)
        
        # 检查浓度非负
        assert np.all(C >= -1e-10)
        
        # 浓度应该下降
        assert C[-1] < C[0]
        
        # 当C << K_s时，应该接近一阶反应
        # 当C >> K_s时，应该接近零阶反应
    
    def test_half_life(self):
        """测试半衰期"""
        C0 = 100.0
        k = 0.1
        T = 50.0
        
        model = ReactionKinetics(T=T, nt=500, k=k, n=1)
        model.set_initial_condition(C0)
        C = model.solve_first_order()
        
        # 理论半衰期
        t_half_theory = np.log(2) / k
        
        # 找到浓度降至C0/2的时间
        idx_half = np.argmin(np.abs(C - C0/2))
        t_half_numerical = model.t[idx_half]
        
        # 数值半衰期应该接近理论值
        assert abs(t_half_numerical - t_half_theory) < 1.0
    
    def test_temperature_correction(self):
        """测试温度校正"""
        k_20 = 0.1
        theta = 1.047
        
        model = ReactionKinetics(T=10.0, nt=100, k=k_20, n=1)
        
        # 10°C时的速率常数
        k_10 = model.temperature_correction(k_20, 10, theta)
        assert k_10 < k_20  # 温度降低，速率减小
        
        # 30°C时的速率常数
        k_30 = model.temperature_correction(k_20, 30, theta)
        assert k_30 > k_20  # 温度升高，速率增大
        
        # 理论值
        k_10_theory = k_20 * theta**(10 - 20)
        k_30_theory = k_20 * theta**(30 - 20)
        
        assert abs(k_10 - k_10_theory) < 1e-6
        assert abs(k_30 - k_30_theory) < 1e-6
    
    def test_fit_first_order(self):
        """测试参数拟合"""
        # 生成"实验数据"
        true_k = 0.08
        C0 = 50.0
        t_data = np.array([0, 5, 10, 15, 20])
        C_data = C0 * np.exp(-true_k * t_data)
        
        model = ReactionKinetics(T=20.0, nt=100, k=0.1, n=1)
        model.set_initial_condition(C0)
        
        k_fitted, C0_fitted, R2 = model.fit_first_order(t_data, C_data)
        
        # 拟合值应该接近真实值
        assert abs(k_fitted - true_k) < 0.01
        assert R2 > 0.99  # 完美拟合


class TestReactionTransport1D:
    """测试反应-迁移耦合模型"""
    
    def test_initialization(self):
        """测试耦合模型初始化"""
        model = ReactionTransport1D(L=100.0, T=200.0, nx=100, nt=1000,
                                    u=0.5, D=0.1, k=0.01, n=1)
        
        assert model.L == 100.0
        assert model.u == 0.5
        assert model.D == 0.1
        assert model.k == 0.01
        assert model.n == 1
        
        assert model.C.shape == (1000, 100)
    
    def test_coupled_solve(self):
        """测试耦合求解"""
        model = ReactionTransport1D(L=100.0, T=200.0, nx=100, nt=1000,
                                    u=0.5, D=0.1, k=0.01, n=1)
        
        # 初始条件：高斯分布
        x0 = 20.0
        sigma = 2.0
        C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        
        C = model.solve(method='upwind')
        
        # 检查结果合理性
        assert np.all(C >= -1e-10)
        assert np.all(np.isfinite(C))
        
        # 峰值应该下降（反应）且向下游移动（对流）
        peak_initial = np.max(C[0, :])
        peak_final = np.max(C[-1, :])
        
        assert peak_final < peak_initial  # 反应导致峰值下降
        
        pos_initial = np.argmax(C[0, :])
        pos_final = np.argmax(C[-1, :])
        
        assert pos_final > pos_initial  # 对流导致向下游移动


def test_decay_reduces_concentration():
    """测试降解使浓度降低"""
    C0 = 100.0
    k = 0.1
    T = 20.0
    
    model = ReactionKinetics(T=T, nt=200, k=k, n=1)
    model.set_initial_condition(C0)
    C = model.solve_first_order()
    
    # 浓度应该单调下降
    for i in range(len(C) - 1):
        assert C[i+1] <= C[i] + 1e-6  # 允许小量数值误差


def test_no_reaction_no_change():
    """测试无反应时浓度不变"""
    C0 = 50.0
    k = 0.0  # 无反应
    T = 100.0
    
    model = ReactionKinetics(T=T, nt=1000, k=k, n=1)
    model.set_initial_condition(C0)
    C = model.solve_first_order()
    
    # 浓度应该保持不变
    assert np.all(np.abs(C - C0) < 1e-6)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
