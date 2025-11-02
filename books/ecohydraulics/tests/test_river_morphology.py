"""测试河流形态多样性模型"""

import pytest
import numpy as np
from code.models.river_morphology import (
    PoolRiffleSequence,
    MeanderChannel,
    BedStability,
    design_naturalized_channel
)


class TestPoolRiffleSequence:
    """测试深潭-浅滩序列"""
    
    def test_initialization(self):
        """测试初始化"""
        pr = PoolRiffleSequence(20.0, 1.5, 0.001, 30.0)
        assert pr.width == 20.0
        assert pr.h_avg == 1.5
        assert pr.slope == 0.001
        assert pr.Q == 30.0
    
    def test_pool_spacing(self):
        """测试深潭间距"""
        pr = PoolRiffleSequence(20.0, 1.5, 0.001, 30.0)
        spacing = pr.pool_spacing()
        
        # 应该是5-7倍河宽
        assert 5 * 20 <= spacing <= 7 * 20
    
    def test_pool_depth(self):
        """测试深潭深度"""
        pr = PoolRiffleSequence(20.0, 1.5, 0.001, 30.0)
        h_pool = pr.pool_depth()
        
        # 应该是1.5-2倍平均水深
        assert 1.5 * 1.5 <= h_pool <= 2.0 * 1.5
    
    def test_riffle_depth(self):
        """测试浅滩深度"""
        pr = PoolRiffleSequence(20.0, 1.5, 0.001, 30.0)
        h_riffle = pr.riffle_depth()
        
        # 应该小于平均水深
        assert h_riffle < 1.5
        assert h_riffle > 0
    
    def test_design_profile(self):
        """测试纵剖面设计"""
        pr = PoolRiffleSequence(20.0, 1.5, 0.001, 30.0)
        x, h = pr.design_profile(500.0)
        
        assert len(x) == len(h)
        assert len(x) > 0
        assert np.all(h > 0)
        assert x[0] == 0
        assert x[-1] <= 500.0
    
    def test_velocity_distribution(self):
        """测试流速分布"""
        pr = PoolRiffleSequence(20.0, 1.5, 0.001, 30.0)
        x, h = pr.design_profile(500.0)
        v = pr.velocity_distribution(x, h)
        
        assert len(v) == len(h)
        assert np.all(v > 0)
        
        # 浅滩流速应该大于深潭
        assert v.max() > v.min()
    
    def test_hydraulic_diversity(self):
        """测试水力多样性"""
        pr = PoolRiffleSequence(20.0, 1.5, 0.001, 30.0)
        x, h = pr.design_profile(500.0)
        v = pr.velocity_distribution(x, h)
        diversity = pr.hydraulic_diversity(v)
        
        assert 'shannon_index' in diversity
        assert 'simpson_index' in diversity
        assert diversity['shannon_index'] > 0
        assert 0 <= diversity['simpson_index'] <= 1


class TestMeanderChannel:
    """测试弯道模型"""
    
    def test_initialization(self):
        """测试初始化"""
        meander = MeanderChannel(20.0, 50.0, 2.0, 0.001)
        assert meander.B == 20.0
        assert meander.R == 50.0
        assert meander.h == 2.0
    
    def test_velocity_ratio(self):
        """测试流速比"""
        meander = MeanderChannel(20.0, 50.0, 2.0, 0.001)
        ratio = meander.velocity_ratio()
        
        # 外岸流速应该大于内岸
        assert ratio > 1.0
        assert ratio < 2.0  # 合理范围
    
    def test_secondary_flow(self):
        """测试环流强度"""
        meander = MeanderChannel(20.0, 50.0, 2.0, 0.001)
        circulation = meander.secondary_flow_strength()
        
        assert 0 <= circulation <= 1.0
    
    def test_bend_scour_depth(self):
        """测试冲刷深度"""
        meander = MeanderChannel(20.0, 50.0, 2.0, 0.001)
        scour = meander.bend_scour_depth()
        
        # 冲刷深度应该大于平均水深
        assert scour > 2.0
        assert scour < 10.0  # 合理上限


class TestBedStability:
    """测试河床稳定性"""
    
    def test_initialization(self):
        """测试初始化"""
        stab = BedStability(15.0, 1.5, 0.001, 0.8)
        assert stab.d50 == 0.015  # 转换为m
        assert stab.h == 1.5
    
    def test_shields_stress(self):
        """测试Shields应力"""
        stab = BedStability(15.0, 1.5, 0.001, 0.8)
        theta = stab.shields_stress()
        
        assert theta > 0
        assert theta < 1.0  # 合理范围
    
    def test_critical_velocity(self):
        """测试起动流速"""
        stab = BedStability(15.0, 1.5, 0.001, 0.8)
        v_c = stab.critical_velocity()
        
        assert v_c > 0
        assert v_c < 2.0  # 对于15mm粗砂
    
    def test_stability_assessment(self):
        """测试稳定性评价"""
        stab = BedStability(15.0, 1.5, 0.001, 0.8)
        result = stab.stability_assessment()
        
        assert 'shields_stress' in result
        assert 'critical_velocity' in result
        assert 'stability' in result
        assert 'erosion_risk' in result
        assert result['stability'] in ['稳定', '基本稳定', '不稳定']


class TestDesignFunction:
    """测试综合设计函数"""
    
    def test_design_naturalized_channel(self):
        """测试近自然河道设计"""
        result = design_naturalized_channel(20.0, 500.0, 0.001, 30.0, 15.0)
        
        # 检查所有输出字段
        assert 'pool_spacing' in result
        assert 'pool_depth' in result
        assert 'riffle_depth' in result
        assert 'profile' in result
        assert 'hydraulic_diversity' in result
        assert 'meander_radius' in result
        assert 'stability' in result
        
        # 检查合理性
        assert result['pool_depth'] > result['riffle_depth']
        assert result['meander_radius'] > 0
