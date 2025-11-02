"""测试丹尼尔式鱼道模型"""

import pytest
import numpy as np
from code.models.denil_fishway import DenilFishway, create_denil_design


class TestDenilFishway:
    """测试丹尼尔鱼道基本功能"""
    
    def test_initialization(self):
        """测试初始化"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        assert fishway.B == 1.0
        assert fishway.L == 50.0
        assert fishway.slope == 10.0
    
    def test_water_depth(self):
        """测试水深计算"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        h = fishway.water_depth(0.5)
        assert h > 0
        assert h < 2.0  # 合理范围
    
    def test_flow_velocity(self):
        """测试流速计算"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        v = fishway.flow_velocity(0.5)
        assert v > 0
        assert v < 5.0  # 合理范围
    
    def test_energy_dissipation(self):
        """测试能量耗散"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        epsilon = fishway.energy_dissipation_rate()
        assert epsilon > 0
        assert epsilon < 1.0
    
    def test_hydraulic_conditions(self):
        """测试水力条件计算"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        conditions = fishway.hydraulic_conditions(0.5)
        
        assert 'discharge' in conditions
        assert 'water_depth' in conditions
        assert 'velocity' in conditions
        assert 'froude_number' in conditions
        assert 'unit_power' in conditions
        
        assert conditions['velocity'] > 0
        assert conditions['water_depth'] > 0
    
    def test_fish_passage_capacity(self):
        """测试鱼类通过能力"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        passage = fishway.fish_passage_capacity(0.5, 'cyprinid')
        
        assert 'suitability' in passage
        assert 'score' in passage
        assert 0 <= passage['score'] <= 1.0
        assert passage['suitability'] in ['优秀', '良好', '可接受', '不适宜']
    
    def test_different_fish_species(self):
        """测试不同鱼类"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        
        cyprinid = fishway.fish_passage_capacity(0.5, 'cyprinid')
        salmonid = fishway.fish_passage_capacity(0.5, 'salmonid')
        
        # 鲑科鱼类游泳能力更强，临界值更高
        assert cyprinid['critical_velocity'] < salmonid['critical_velocity']
    
    def test_design_optimization(self):
        """测试设计优化"""
        fishway = DenilFishway(1.0, 50.0, 10.0)
        result = fishway.design_optimization(0.5, 'cyprinid')
        
        assert 'optimal_slope' in result
        assert 'all_results' in result
        assert len(result['all_results']) > 0
    
    def test_baffle_configuration(self):
        """测试挡板配置"""
        fishway = DenilFishway(1.0, 50.0, 10.0, baffle_spacing=0.4)
        config = fishway.baffle_configuration()
        
        assert 'number_of_baffles' in config
        assert config['number_of_baffles'] > 0
        assert config['baffle_spacing'] == 0.4


class TestDenilDesign:
    """测试完整设计功能"""
    
    def test_create_denil_design(self):
        """测试创建设计方案"""
        design = create_denil_design(5.0, 0.5, 'cyprinid')
        
        assert 'dam_height' in design
        assert 'channel_width' in design
        assert 'channel_length' in design
        assert 'hydraulic_conditions' in design
        assert 'fish_passage' in design
        
        assert design['dam_height'] == 5.0
        assert design['channel_width'] > 0
    
    def test_design_feasibility(self):
        """测试设计可行性"""
        design = create_denil_design(5.0, 0.5, 'cyprinid')
        
        # 检查流速在合理范围
        v = design['hydraulic_conditions']['velocity']
        assert 0.5 < v < 3.0
        
        # 检查水深合理
        h = design['hydraulic_conditions']['water_depth']
        assert 0.1 < h < 1.5
        
        # 检查鱼类通过评分
        score = design['fish_passage']['score']
        assert score > 0.5  # 至少可接受
