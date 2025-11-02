"""
测试非点源污染模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.nonpoint_source import (SCSCurveNumber, EventMeanConcentration,
                                    NonPointSourceRiver1D,
                                    calculate_first_flush_factor,
                                    calculate_buildup_washoff)


class TestSCSCurveNumber:
    """测试SCS-CN模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        scs = SCSCurveNumber(CN=75, area=10)
        
        assert scs.CN == 75
        assert scs.area == 10
        assert scs.S > 0
        assert scs.Ia > 0
    
    def test_runoff_calculation(self):
        """测试径流计算"""
        scs = SCSCurveNumber(CN=80, area=10)
        
        # 降雨大于初损
        Q, alpha = scs.calculate_runoff(50)
        assert Q > 0
        assert 0 < alpha < 1
        
        # 降雨小于初损
        Q_small, alpha_small = scs.calculate_runoff(5)
        assert Q_small == 0
        assert alpha_small == 0
    
    def test_higher_CN_more_runoff(self):
        """测试高CN产生更多径流"""
        scs_low = SCSCurveNumber(CN=60, area=10)
        scs_high = SCSCurveNumber(CN=90, area=10)
        
        Q_low, _ = scs_low.calculate_runoff(50)
        Q_high, _ = scs_high.calculate_runoff(50)
        
        assert Q_high > Q_low
    
    def test_runoff_volume(self):
        """测试径流量计算"""
        scs = SCSCurveNumber(CN=75, area=10)
        
        V = scs.calculate_runoff_volume(50)
        
        assert V > 0
        # 体积单位转换正确
        Q, _ = scs.calculate_runoff(50)
        expected_V = Q * 10 * 1000  # mm * km² = 1000 m³
        assert abs(V - expected_V) < 1


class TestEventMeanConcentration:
    """测试EMC模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        emc = EventMeanConcentration({'COD': 80, 'TN': 3.0})
        
        assert emc.EMC_dict['COD'] == 80
        assert emc.EMC_dict['TN'] == 3.0
    
    def test_load_calculation(self):
        """测试污染负荷计算"""
        emc = EventMeanConcentration({'COD': 100})
        
        V = 10000  # m³
        loads = emc.calculate_load(V)
        
        # L = C * V * 10^-6
        expected_load = 100 * 10000 * 1e-6
        assert abs(loads['COD'] - expected_load) < 0.01
    
    def test_multiple_pollutants(self):
        """测试多污染物"""
        emc = EventMeanConcentration({
            'COD': 100,
            'TN': 5.0,
            'TP': 0.8
        })
        
        V = 5000
        loads = emc.calculate_load(V)
        
        assert 'COD' in loads
        assert 'TN' in loads
        assert 'TP' in loads
        assert all(L > 0 for L in loads.values())


class TestNonPointSourceRiver1D:
    """测试非点源河流模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = NonPointSourceRiver1D(
            L=10000, nx=100, u=0.5, D=3.0, k=0.1/86400,
            Q_river=20.0, C0=5.0
        )
        
        assert model.L == 10000
        assert model.nx == 100
        assert model.Q_river == 20.0
        assert len(model.S_nps) == 100
        assert np.all(model.S_nps == 0)
    
    def test_add_distributed_source(self):
        """测试添加分布式源项"""
        model = NonPointSourceRiver1D(
            L=10000, nx=100, u=0.5, D=3.0, k=0.1/86400,
            Q_river=20.0, C0=5.0
        )
        
        model.add_distributed_source(x_start=2000, x_end=5000, load_rate=10.0)
        
        # 检查源项非零
        assert np.any(model.S_nps > 0)
        
        # 源项仅在指定范围内
        mask = (model.x >= 2000) & (model.x <= 5000)
        assert np.all(model.S_nps[~mask] == 0)
    
    def test_solve_with_source(self):
        """测试求解（有源项）"""
        model = NonPointSourceRiver1D(
            L=10000, nx=100, u=0.5, D=3.0, k=0.1/86400,
            Q_river=20.0, C0=5.0
        )
        
        model.add_distributed_source(x_start=2000, x_end=5000, load_rate=10.0)
        
        x, C = model.solve()
        
        assert len(x) == 100
        assert len(C) == 100
        assert np.all(np.isfinite(C))
        assert np.all(C >= 0)
        
        # 下游浓度应高于上游
        assert np.max(C) > model.C0
    
    def test_solve_no_source(self):
        """测试求解（无源项）"""
        model = NonPointSourceRiver1D(
            L=10000, nx=100, u=0.5, D=3.0, k=0.2/86400,
            Q_river=20.0, C0=10.0
        )
        
        x, C = model.solve()
        
        # 无源项，浓度应逐渐衰减
        assert C[0] == model.C0
        assert C[-1] < C[0]


def test_first_flush_factor():
    """测试初期冲刷系数"""
    # 短时降雨
    ff_short = calculate_first_flush_factor(rainfall_duration=1.5)
    assert ff_short > 2.0
    
    # 长时降雨
    ff_long = calculate_first_flush_factor(rainfall_duration=8)
    assert ff_long < 2.0
    
    # 短时应大于长时
    assert ff_short > ff_long


def test_buildup_washoff():
    """测试累积-冲刷系数"""
    # 长期无雨，高强度降雨
    factor_high = calculate_buildup_washoff(days_since_last_rain=10, rainfall_intensity=25)
    
    # 短期无雨，低强度降雨
    factor_low = calculate_buildup_washoff(days_since_last_rain=2, rainfall_intensity=3)
    
    # 高累积+高强度应产生更大冲刷
    assert factor_high > factor_low


def test_distributed_source_increases_concentration():
    """测试分布式源项增加浓度"""
    # 无源项
    model_no_source = NonPointSourceRiver1D(
        L=10000, nx=100, u=0.5, D=3.0, k=0.1/86400,
        Q_river=20.0, C0=5.0
    )
    _, C_no_source = model_no_source.solve()
    
    # 有源项
    model_with_source = NonPointSourceRiver1D(
        L=10000, nx=100, u=0.5, D=3.0, k=0.1/86400,
        Q_river=20.0, C0=5.0
    )
    model_with_source.add_distributed_source(2000, 5000, 20.0)
    _, C_with_source = model_with_source.solve()
    
    # 有源项应产生更高浓度
    assert np.max(C_with_source) > np.max(C_no_source)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
