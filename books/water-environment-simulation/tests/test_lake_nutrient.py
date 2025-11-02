"""
测试湖泊营养盐输入响应模型
Test Lake Nutrient Input-Response Model
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.lake_nutrient import (VollenweiderModel, calculate_trophic_state,
                                   calculate_vollenweider_loading, calculate_phosphorus_budget,
                                   predict_response_time)


class TestVollenweiderModel:
    """测试VollenweiderModel类"""
    
    def test_initialization(self):
        """测试初始化"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        
        assert model.A == 10e6
        assert model.H == 10
        assert model.V == 10e6 * 10
        assert model.Q == 100000
        assert model.L == 10e6
        assert model.sigma == 0.01
    
    def test_calculate_steady_state(self):
        """测试稳态浓度计算"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        
        P_ss = model.calculate_steady_state()
        
        # 手算验证: P_ss = L / (Q + σ*A)
        expected_P_ss = 10e6 / (100000 + 0.01 * 10e6)
        assert abs(P_ss - expected_P_ss) < 0.1
    
    def test_calculate_retention_coefficient(self):
        """测试滞留系数计算"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        
        R = model.calculate_retention_coefficient()
        
        # R应在0-1之间
        assert 0 <= R <= 1
    
    def test_calculate_critical_load(self):
        """测试临界负荷计算"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        
        P_standard = 30
        L_crit = model.calculate_critical_load(P_standard)
        
        # 验证: L_crit = P_standard * (Q + σ*A)
        expected_L_crit = P_standard * (100000 + 0.01 * 10e6)
        assert abs(L_crit - expected_L_crit) < 100
    
    def test_evaluate_load_reduction(self):
        """测试负荷削减评估"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        
        P_old, P_new, improvement = model.evaluate_load_reduction(50)
        
        # 削减50%后浓度应降低
        assert P_new < P_old
        assert improvement > 0
    
    def test_calibrate_settling_velocity(self):
        """测试沉降速率率定"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        
        P_observed = 50
        sigma_cal = model.calibrate_settling_velocity(P_observed, 10e6, 100000)
        
        # 率定的沉降速率应非负
        assert sigma_cal >= 0
    
    def test_solve_transient(self):
        """测试瞬态求解"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01, P0=10)
        
        t = np.linspace(0, 100, 50)
        t_out, P_out = model.solve_transient(t)
        
        assert len(t_out) == len(t)
        assert len(P_out) == len(t)
        assert P_out[0] == 10


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_calculate_trophic_state(self):
        """测试营养状态判断"""
        state1, idx1 = calculate_trophic_state(5)
        assert "Oligotrophic" in state1
        assert idx1 == 0
        
        state2, idx2 = calculate_trophic_state(20)
        assert "Mesotrophic" in state2
        assert idx2 == 1
        
        state3, idx3 = calculate_trophic_state(60)
        assert "Eutrophic" in state3
        assert idx3 == 2
        
        state4, idx4 = calculate_trophic_state(150)
        assert "Hypertrophic" in state4
        assert idx4 == 3
    
    def test_calculate_vollenweider_loading(self):
        """测试Vollenweider容许负荷"""
        A = 10e6
        H = 10
        tau = 365 * 100  # 100 days in years
        P_target = 30
        
        L_perm, L_dang = calculate_vollenweider_loading(A, H, tau, P_target)
        
        assert L_perm > 0
        assert L_dang > 0
    
    def test_calculate_phosphorus_budget(self):
        """测试磷收支平衡"""
        L_in = 10e6
        L_out = 5e6
        L_settling = 4e6
        V = 100e6
        
        balance, retention = calculate_phosphorus_budget(L_in, L_out, L_settling, V)
        
        expected_balance = (L_in - L_out - L_settling) / V
        assert abs(balance - expected_balance) < 1e-6
        
        expected_retention = (L_out + L_settling) / L_in * 100
        assert abs(retention - expected_retention) < 0.1
    
    def test_predict_response_time(self):
        """测试响应时间预测"""
        tau = 365
        sigma = 0.01
        H = 10
        
        tau_resp, t_95 = predict_response_time(tau, sigma, H)
        
        assert tau_resp > 0
        assert t_95 == 3 * tau_resp


class TestPhysicalBehavior:
    """测试物理行为"""
    
    def test_load_reduction_effect(self):
        """测试负荷削减效应"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        
        P_base = model.calculate_steady_state()
        
        # 削减50%
        P_old, P_new, _ = model.evaluate_load_reduction(50)
        
        # 削减50%负荷，浓度应接近减半
        assert abs(P_new / P_old - 0.5) < 0.1
    
    def test_settling_effect(self):
        """测试沉降效应"""
        # 无沉降
        model1 = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0)
        P1 = model1.calculate_steady_state()
        
        # 有沉降
        model2 = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.02)
        P2 = model2.calculate_steady_state()
        
        # 有沉降时浓度应更低
        assert P2 < P1
    
    def test_retention_coefficient_range(self):
        """测试滞留系数范围"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01)
        R = model.calculate_retention_coefficient()
        
        # R应在0-1之间
        assert 0 <= R <= 1
    
    def test_transient_to_steady(self):
        """测试瞬态到稳态"""
        model = VollenweiderModel(A=10e6, H=10, Q=100000, L=10e6, sigma=0.01, P0=10)
        
        P_ss = model.calculate_steady_state()
        
        # 长时间瞬态
        t = np.linspace(0, 10000, 100)
        t_out, P_out = model.solve_transient(t)
        
        # 最终应接近稳态
        assert abs(P_out[-1] - P_ss) < 1


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
