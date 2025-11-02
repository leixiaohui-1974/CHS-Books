"""
测试湖泊完全混合反应器模型
Test Lake Complete Mixed Flow Reactor Model
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.lake_cmfr import (LakeCMFR, calculate_critical_load, calculate_flushing_efficiency)


class TestLakeCMFR:
    """测试LakeCMFR类"""
    
    def test_initialization(self):
        """测试初始化"""
        A = 1e6  # 1 km²
        H = 5    # 5 m
        Q_in = 1000
        k = 0.1
        C_in = 10
        C0 = 5
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in, C0=C0)
        
        assert lake.A == A
        assert lake.H == H
        assert lake.V == A * H
        assert lake.Q_in == Q_in
        assert lake.Q_out == Q_in
        assert lake.k == k
        assert lake.C == C0
    
    def test_calculate_hydraulic_residence_time(self):
        """测试水力停留时间计算"""
        A = 1e6
        H = 5
        Q_out = 1000
        
        lake = LakeCMFR(A, H, Q_in=Q_out, Q_out=Q_out)
        HRT = lake.calculate_hydraulic_residence_time()
        
        expected_HRT = lake.V / Q_out
        assert abs(HRT - expected_HRT) < 1e-6
    
    def test_calculate_flushing_rate(self):
        """测试换水率计算"""
        A = 1e6
        H = 5
        Q_out = 1000
        
        lake = LakeCMFR(A, H, Q_in=Q_out, Q_out=Q_out)
        r = lake.calculate_flushing_rate()
        
        expected_r = Q_out / lake.V
        assert abs(r - expected_r) < 1e-9
    
    def test_set_internal_source(self):
        """测试内源设置"""
        lake = LakeCMFR(1e6, 5, 1000)
        
        # 设置内源
        S = 500
        lake.set_internal_source(S)
        assert lake.S == S
    
    def test_calculate_steady_state(self):
        """测试稳态浓度计算"""
        A = 1e6
        H = 5
        Q_in = 1000
        Q_out = 1000
        k = 0.1
        C_in = 10
        V = A * H
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_out, k=k, C_in=C_in)
        
        # 无内源
        C_ss = lake.calculate_steady_state()
        
        # 手算验证
        expected_C_ss = (Q_in * C_in) / (Q_out + k * V)
        assert abs(C_ss - expected_C_ss) < 0.01
    
    def test_calculate_steady_state_with_source(self):
        """测试有内源的稳态浓度"""
        A = 1e6
        H = 5
        Q_in = 1000
        Q_out = 1000
        k = 0.1
        C_in = 10
        S = 500
        V = A * H
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_out, k=k, C_in=C_in)
        lake.set_internal_source(S)
        
        C_ss = lake.calculate_steady_state()
        
        # 手算验证
        expected_C_ss = (Q_in * C_in + S) / (Q_out + k * V)
        assert abs(C_ss - expected_C_ss) < 0.01
    
    def test_calculate_response_time(self):
        """测试响应时间计算"""
        A = 1e6
        H = 5
        Q_out = 1000
        k = 0.1
        V = A * H
        
        lake = LakeCMFR(A, H, Q_in=Q_out, Q_out=Q_out, k=k)
        tau, t_95 = lake.calculate_response_time()
        
        # 验证
        expected_tau = V / (Q_out + k * V)
        expected_t_95 = 3 * expected_tau
        
        assert abs(tau - expected_tau) < 1e-6
        assert abs(t_95 - expected_t_95) < 1e-6
    
    def test_solve_transient(self):
        """测试瞬态求解"""
        A = 1e6
        H = 5
        Q_in = 1000
        k = 0.1
        C_in = 10
        C0 = 0
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in, C0=C0)
        
        # 求解
        t = np.linspace(0, 100, 100)
        t_out, C_out = lake.solve_transient(t)
        
        # 验证
        assert len(t_out) == len(t)
        assert len(C_out) == len(t)
        assert C_out[0] == C0  # 初始浓度
        assert C_out[-1] > C0  # 浓度增加
    
    def test_evaluate_water_exchange(self):
        """测试换水措施评估"""
        A = 1e6
        H = 5
        Q_in = 1000
        k = 0.1
        C_in = 10
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in)
        
        # 评估
        Q_new = 2000
        C_old, C_new, improvement = lake.evaluate_water_exchange(Q_new)
        
        # 验证
        assert C_new < C_old  # 新浓度应更低
        assert improvement > 0  # 有改善


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_calculate_critical_load(self):
        """测试临界负荷计算"""
        V = 5e6
        Q_out = 1000
        k = 0.1
        C_standard = 5
        
        L_crit = calculate_critical_load(V, Q_out, k, C_standard)
        
        # 验证
        expected_L_crit = C_standard * (Q_out + k * V)
        assert abs(L_crit - expected_L_crit) < 0.01
    
    def test_calculate_flushing_efficiency(self):
        """测试冲刷效率计算"""
        Q_out = 1000
        V = 5e6
        k = 0.1
        
        E = calculate_flushing_efficiency(Q_out, V, k)
        
        # 验证
        expected_E = (Q_out + k * V) / (2 * Q_out + k * V)
        assert abs(E - expected_E) < 1e-9
        
        # 效率应在0-1之间
        assert 0 <= E <= 1


class TestPhysicalBehavior:
    """测试物理行为"""
    
    def test_mass_balance(self):
        """测试质量平衡"""
        A = 1e6
        H = 5
        Q_in = 1000
        k = 0
        C_in = 10
        C0 = 5
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in, C0=C0)
        
        # 无反应时，稳态浓度应等于入流浓度
        C_ss = lake.calculate_steady_state()
        assert abs(C_ss - C_in) < 0.01
    
    def test_reaction_effect(self):
        """测试反应效应"""
        A = 1e6
        H = 5
        Q_in = 1000
        C_in = 10
        
        # 无反应
        lake1 = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=0, C_in=C_in)
        C_ss1 = lake1.calculate_steady_state()
        
        # 有反应
        lake2 = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=0.2, C_in=C_in)
        C_ss2 = lake2.calculate_steady_state()
        
        # 有反应时浓度应更低
        assert C_ss2 < C_ss1
    
    def test_flushing_effect(self):
        """测试换水效应"""
        A = 1e6
        H = 5
        k = 0
        C_in = 10
        
        # 低换水率（长HRT）
        lake1 = LakeCMFR(A, H, Q_in=500, Q_out=500, k=k, C_in=C_in)
        C_ss1 = lake1.calculate_steady_state()
        
        # 高换水率（短HRT）
        lake2 = LakeCMFR(A, H, Q_in=2000, Q_out=2000, k=k, C_in=C_in)
        C_ss2 = lake2.calculate_steady_state()
        
        # 无反应时，稳态浓度都等于入流浓度
        assert abs(C_ss1 - C_in) < 0.01
        assert abs(C_ss2 - C_in) < 0.01
    
    def test_internal_source_effect(self):
        """测试内源效应"""
        A = 1e6
        H = 5
        Q_in = 1000
        k = 0.1
        C_in = 10
        
        # 无内源
        lake1 = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in)
        C_ss1 = lake1.calculate_steady_state()
        
        # 有内源（产生）
        lake2 = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in)
        lake2.set_internal_source(1000)  # 正值：产生
        C_ss2 = lake2.calculate_steady_state()
        
        # 内源产生时浓度应更高
        assert C_ss2 > C_ss1
    
    def test_transient_to_steady(self):
        """测试瞬态到稳态"""
        A = 1e6
        H = 5
        Q_in = 1000
        k = 0.1
        C_in = 10
        C0 = 0
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in, C0=C0)
        
        # 计算稳态
        C_ss = lake.calculate_steady_state()
        
        # 长时间瞬态求解
        t = np.linspace(0, 10000, 1000)
        t_out, C_out = lake.solve_transient(t)
        
        # 长时间后应接近稳态
        assert abs(C_out[-1] - C_ss) < 0.1
    
    def test_hrt_effect_on_response(self):
        """测试HRT对响应时间的影响"""
        A = 1e6
        H = 5
        k = 0.1
        
        # 短HRT
        lake1 = LakeCMFR(A, H, Q_in=2000, Q_out=2000, k=k)
        tau1, _ = lake1.calculate_response_time()
        
        # 长HRT
        lake2 = LakeCMFR(A, H, Q_in=500, Q_out=500, k=k)
        tau2, _ = lake2.calculate_response_time()
        
        # HRT越长，响应时间越长
        assert tau2 > tau1
    
    def test_zero_outflow(self):
        """测试零出流情况"""
        A = 1e6
        H = 5
        Q_in = 1000
        Q_out = 0
        k = 0.1
        C_in = 10
        
        lake = LakeCMFR(A, H, Q_in, Q_out=Q_out, k=k, C_in=C_in)
        
        # HRT应为无穷大
        assert lake.HRT == np.inf
        
        # 稳态浓度应仅依赖反应
        C_ss = lake.calculate_steady_state()
        expected_C_ss = Q_in * C_in / (k * lake.V)
        assert abs(C_ss - expected_C_ss) < 0.01


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
