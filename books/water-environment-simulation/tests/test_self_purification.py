"""
测试自净能力评估模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.self_purification import (SelfPurificationCapacity, WaterQualityIndex,
                                      calculate_assimilative_capacity,
                                      functional_zone_classification)


class TestSelfPurificationCapacity:
    """测试自净能力评估"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = SelfPurificationCapacity(Q=20.0, u=0.5, A=40.0, P=20.0, ka=0.6, kd=0.2)
        
        assert model.Q == 20.0
        assert model.u == 0.5
        assert model.A == 40.0
        assert model.P == 20.0
        assert model.ka == 0.6
        assert model.kd == 0.2
        assert model.R == 40.0 / 20.0
    
    def test_self_purification_coefficient(self):
        """测试自净系数计算"""
        # 强自净能力
        model_strong = SelfPurificationCapacity(Q=20, u=0.5, A=40, P=20, ka=1.0, kd=0.2)
        f_strong, grade_strong, _ = model_strong.calculate_self_purification_coefficient()
        assert f_strong == 5.0
        assert "强" in grade_strong
        
        # 弱自净能力
        model_weak = SelfPurificationCapacity(Q=20, u=0.5, A=40, P=20, ka=0.15, kd=0.2)
        f_weak, grade_weak, _ = model_weak.calculate_self_purification_coefficient()
        assert abs(f_weak - 0.75) < 0.01
        assert "弱" in grade_weak
    
    def test_dilution_capacity(self):
        """测试稀释容量计算"""
        model = SelfPurificationCapacity(Q=20.0, u=0.5, A=40, P=20, ka=0.6, kd=0.2)
        
        # 正常情况
        W = model.calculate_dilution_capacity(C_river=5.0, C_standard=10.0)
        assert W > 0
        
        # 理论值：Q * (C_std - C_bg) * 86.4
        W_expected = 20.0 * (10.0 - 5.0) * 86.4
        assert abs(W - W_expected) < 1.0
        
        # 本底超标情况
        W_zero = model.calculate_dilution_capacity(C_river=15.0, C_standard=10.0)
        assert W_zero == 0
    
    def test_environmental_capacity(self):
        """测试环境容量计算"""
        model = SelfPurificationCapacity(Q=20.0, u=0.5, A=40, P=20, ka=0.6, kd=0.2)
        
        # 考虑降解
        W_decay = model.calculate_environmental_capacity(
            C0=5.0, C_standard=10.0, L=50, decay=True
        )
        
        # 不考虑降解
        W_no_decay = model.calculate_environmental_capacity(
            C0=5.0, C_standard=10.0, L=50, decay=False
        )
        
        # 考虑降解应该比不考虑降解的容量大
        assert W_decay > W_no_decay
    
    def test_mixing_length(self):
        """测试混合长度计算"""
        model = SelfPurificationCapacity(Q=20.0, u=0.5, A=40, P=20, ka=0.6, kd=0.2)
        
        L_mix = model.calculate_mixing_length(B=15.0, Q_waste=1.0, Q_river=20.0)
        
        # 混合长度应该为正且合理
        assert L_mix > 0
        assert L_mix < 5000  # 一般不超过5km


class TestWaterQualityIndex:
    """测试水质评价指数"""
    
    def test_single_factor_index(self):
        """测试单因子指数"""
        # 达标
        P_ok = WaterQualityIndex.single_factor_index(3.0, 5.0)
        assert P_ok < 1
        
        # 超标
        P_exceed = WaterQualityIndex.single_factor_index(8.0, 5.0)
        assert P_exceed > 1
        
        # 临界
        P_critical = WaterQualityIndex.single_factor_index(5.0, 5.0)
        assert abs(P_critical - 1.0) < 0.01
    
    def test_comprehensive_pollution_index(self):
        """测试综合污染指数"""
        C_measured = [3.0, 4.0, 5.0]
        C_standard = [5.0, 5.0, 5.0]
        
        # 无权重
        P_unweighted = WaterQualityIndex.comprehensive_pollution_index(
            C_measured, C_standard
        )
        assert 0 < P_unweighted < 1
        
        # 有权重
        weights = [1.0, 1.5, 0.5]
        P_weighted = WaterQualityIndex.comprehensive_pollution_index(
            C_measured, C_standard, weights
        )
        assert 0 < P_weighted < 1


def test_assimilative_capacity():
    """测试同化容量计算"""
    L0_max, W = calculate_assimilative_capacity(
        Q=20.0, ka=0.6, kd=0.2, DOs=9.0, DO_standard=5.0, L0_bg=5.0
    )
    
    # 应该返回合理值
    assert L0_max >= 0
    assert W >= 0


def test_functional_zone_classification():
    """测试功能区划分"""
    # 优良水质
    params_good = {
        'DO': 7.0,
        'BOD5': 3.0,
        'NH3-N': 0.3,
    }
    category_good, uses_good = functional_zone_classification(params_good)
    assert category_good <= 3
    assert 'drinking' in uses_good or 'fishery' in uses_good
    
    # 较差水质
    params_poor = {
        'DO': 3.5,
        'BOD5': 7.0,
        'NH3-N': 1.6,
    }
    category_poor, uses_poor = functional_zone_classification(params_poor)
    assert category_poor >= 4


def test_high_ka_strong_purification():
    """测试高ka意味着强自净能力"""
    model_high_ka = SelfPurificationCapacity(Q=20, u=0.5, A=40, P=20, ka=2.0, kd=0.2)
    f_high, grade_high, _ = model_high_ka.calculate_self_purification_coefficient()
    
    model_low_ka = SelfPurificationCapacity(Q=20, u=0.5, A=40, P=20, ka=0.3, kd=0.2)
    f_low, grade_low, _ = model_low_ka.calculate_self_purification_coefficient()
    
    # 高ka应该有更强的自净能力
    assert f_high > f_low


def test_degradation_increases_capacity():
    """测试降解作用增加环境容量"""
    model = SelfPurificationCapacity(Q=20.0, u=0.5, A=40, P=20, ka=0.6, kd=0.3)
    
    # 不考虑降解
    W_no_decay = model.calculate_environmental_capacity(
        C0=5.0, C_standard=10.0, L=100, decay=False
    )
    
    # 考虑降解
    W_with_decay = model.calculate_environmental_capacity(
        C0=5.0, C_standard=10.0, L=100, decay=True
    )
    
    # 考虑降解应该增加容量
    assert W_with_decay > W_no_decay


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
