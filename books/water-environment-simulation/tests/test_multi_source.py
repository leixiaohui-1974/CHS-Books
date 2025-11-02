"""
测试多点源污染叠加模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.multi_source import MultiSourceRiver1D, PointSource, calculate_superposition_factor


class TestPointSource:
    """测试点源类"""
    
    def test_initialization(self):
        """测试点源初始化"""
        source = PointSource(x=1000, Q_waste=0.5, C_waste=100, name="Test Source")
        
        assert source.x == 1000
        assert source.Q_waste == 0.5
        assert source.C_waste == 100
        assert source.name == "Test Source"


class TestMultiSourceRiver1D:
    """测试多点源河流模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
            Q_river=50.0, C0=5.0
        )
        
        assert model.L == 10000
        assert model.nx == 100
        assert model.u == 0.5
        assert model.D == 2.0
        assert model.Q_river == 50.0
        assert model.C0 == 5.0
        assert len(model.sources) == 0
    
    def test_add_source(self):
        """测试添加点源"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
            Q_river=50.0, C0=5.0
        )
        
        source = model.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
        
        assert len(model.sources) == 1
        assert source.x == 2000
        assert source.Q_waste == 1.0
        assert source.C_waste == 100
    
    def test_mixed_concentration(self):
        """测试混合浓度计算"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
            Q_river=50.0, C0=5.0
        )
        
        source = PointSource(x=2000, Q_waste=1.0, C_waste=100, name="Test")
        
        C_mixed, Q_mixed = model.calculate_mixed_concentration(
            C_upstream=10.0, Q_upstream=50.0, source=source
        )
        
        # 验证质量守恒
        expected_C = (50.0 * 10.0 + 1.0 * 100.0) / (50.0 + 1.0)
        assert abs(C_mixed - expected_C) < 0.01
        assert Q_mixed == 51.0
    
    def test_solve_single_source(self):
        """测试单点源求解"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
            Q_river=50.0, C0=5.0
        )
        
        model.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
        
        x, C = model.solve()
        
        # 验证解
        assert len(x) == 100
        assert len(C) == 100
        assert np.all(np.isfinite(C))
        assert np.all(C >= 0)
        
        # 验证点源下游浓度升高
        idx_source = np.argmin(np.abs(x - 2000))
        assert C[idx_source] > model.C0
    
    def test_solve_multi_source(self):
        """测试多点源求解"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
            Q_river=50.0, C0=5.0
        )
        
        model.add_source(x=2000, Q_waste=0.5, C_waste=150, name="Source1")
        model.add_source(x=5000, Q_waste=0.3, C_waste=120, name="Source2")
        model.add_source(x=8000, Q_waste=0.4, C_waste=100, name="Source3")
        
        x, C = model.solve()
        
        # 验证解
        assert len(x) == 100
        assert len(C) == 100
        assert np.all(np.isfinite(C))
        assert np.all(C >= 0)
    
    def test_concentration_decay(self):
        """测试浓度衰减"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.2/86400,  # 较大降解系数
            Q_river=50.0, C0=0
        )
        
        model.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
        
        x, C = model.solve()
        
        # 找到点源下游浓度
        idx_source = np.argmin(np.abs(x - 2000))
        C_source = C[idx_source]
        C_downstream = C[idx_source + 10]  # 下游一段距离
        
        # 验证浓度衰减
        assert C_downstream < C_source
    
    def test_compliance_distance(self):
        """测试达标距离计算"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.15/86400, 
            Q_river=50.0, C0=5.0
        )
        
        model.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
        
        model.solve()
        
        # 计算达标距离
        dist = model.calculate_compliance_distance(C_standard=20.0, source_idx=0)
        
        # 应该找到达标距离
        assert dist is not None
        assert dist > 0
    
    def test_max_concentration(self):
        """测试最大浓度计算"""
        model = MultiSourceRiver1D(
            L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
            Q_river=50.0, C0=5.0
        )
        
        model.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
        
        model.solve()
        
        C_max, x_max = model.calculate_max_concentration()
        
        # 验证最大浓度
        assert C_max > model.C0
        assert 0 <= x_max <= model.L


def test_multiple_sources_increase_concentration():
    """测试多点源增加浓度"""
    # 单点源
    model_single = MultiSourceRiver1D(
        L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
        Q_river=50.0, C0=5.0
    )
    model_single.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
    _, C_single = model_single.solve()
    
    # 双点源
    model_double = MultiSourceRiver1D(
        L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
        Q_river=50.0, C0=5.0
    )
    model_double.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
    model_double.add_source(x=5000, Q_waste=1.0, C_waste=100, name="Source2")
    _, C_double = model_double.solve()
    
    # 双点源下游浓度应该更高
    idx_downstream = 70  # 第二个点源之后
    assert C_double[idx_downstream] > C_single[idx_downstream]


def test_higher_flow_dilutes_concentration():
    """测试高流量稀释浓度"""
    # 低流量
    model_low = MultiSourceRiver1D(
        L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
        Q_river=30.0, C0=5.0
    )
    model_low.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
    _, C_low = model_low.solve()
    
    # 高流量
    model_high = MultiSourceRiver1D(
        L=10000, nx=100, u=0.5, D=2.0, k=0.1/86400, 
        Q_river=70.0, C0=5.0
    )
    model_high.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
    _, C_high = model_high.solve()
    
    # 高流量应导致更低的浓度
    C_max_low = np.max(C_low)
    C_max_high = np.max(C_high)
    assert C_max_high < C_max_low


def test_higher_decay_reduces_concentration():
    """测试高降解系数降低浓度"""
    # 低降解
    model_low_k = MultiSourceRiver1D(
        L=10000, nx=100, u=0.5, D=2.0, k=0.05/86400, 
        Q_river=50.0, C0=5.0
    )
    model_low_k.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
    _, C_low_k = model_low_k.solve()
    
    # 高降解
    model_high_k = MultiSourceRiver1D(
        L=10000, nx=100, u=0.5, D=2.0, k=0.3/86400, 
        Q_river=50.0, C0=5.0
    )
    model_high_k.add_source(x=2000, Q_waste=1.0, C_waste=100, name="Source1")
    _, C_high_k = model_high_k.solve()
    
    # 高降解应导致下游更低的浓度
    idx_downstream = 70
    assert C_high_k[idx_downstream] < C_low_k[idx_downstream]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
