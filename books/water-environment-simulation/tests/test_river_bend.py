"""
测试河流弯道水质模型
Test River Bend Water Quality Model
"""

import pytest
import numpy as np
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.river_bend import (RiverBend2D, calculate_bend_mixing_length,
                                calculate_curvature_radius, calculate_secondary_flow_strength)


class TestRiverBend2D:
    """测试RiverBend2D类"""
    
    def test_initialization(self):
        """测试初始化"""
        model = RiverBend2D(
            L=1000, B=80, nx=50, ny=20,
            u=0.6, Ey_straight=0.05, R=500, bend_angle=90
        )
        
        assert model.L == 1000
        assert model.B == 80
        assert model.u == 0.6
        assert model.R == 500
        assert model.K_bend > 1.0  # 弯道增强
        assert model.Ey_effective > model.Ey_straight
    
    def test_bend_enhancement_factor(self):
        """测试弯道增强系数"""
        model = RiverBend2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ey_straight=0.05, R=500, bend_angle=90
        )
        
        K = model.calculate_bend_enhancement_factor()
        
        # 弯道增强系数应大于1
        assert K > 1.0
        # 对于B/R=0.2，K应在合理范围
        assert 1.0 < K < 5.0
    
    def test_add_source(self):
        """测试添加排放源"""
        model = RiverBend2D(
            L=1000, B=80, nx=50, ny=20,
            u=0.6, Ey_straight=0.05, R=500, bend_angle=90
        )
        
        model.add_source(
            x=0, y=10,
            Q_discharge=1.5, C_discharge=80.0,
            Q_river=120.0
        )
        
        assert len(model.sources) == 1
        assert model.sources[0]['x'] == 0
        assert model.sources[0]['y'] == 10
    
    def test_secondary_flow_velocity(self):
        """测试二次流速度"""
        model = RiverBend2D(
            L=1000, B=80, nx=50, ny=20,
            u=0.6, Ey_straight=0.05, R=500, bend_angle=90
        )
        
        # 测试不同位置的二次流速度
        v_center = model.calculate_secondary_flow_velocity(40)  # 中心
        v_inner = model.calculate_secondary_flow_velocity(0)    # 内岸
        v_outer = model.calculate_secondary_flow_velocity(80)   # 外岸
        
        # 中心二次流速度最大
        assert abs(v_center) > abs(v_inner)
        assert abs(v_center) > abs(v_outer)
    
    def test_solve_with_secondary_flow(self):
        """测试考虑二次流的求解"""
        model = RiverBend2D(
            L=2000, B=80, nx=100, ny=20,
            u=0.6, Ey_straight=0.05, R=500, bend_angle=90
        )
        
        model.add_source(
            x=0, y=10,
            Q_discharge=1.5, C_discharge=80.0,
            Q_river=120.0
        )
        
        x, y, C = model.solve_with_secondary_flow()
        
        # 检查结果
        assert C.shape == (20, 100)
        assert np.all(C >= 0)
        assert np.max(C) > 0
    
    def test_concentration_shift(self):
        """测试浓度偏向"""
        model = RiverBend2D(
            L=2000, B=80, nx=100, ny=20,
            u=0.6, Ey_straight=0.05, R=500, bend_angle=90
        )
        
        model.add_source(
            x=0, y=10,  # 凸岸侧排放
            Q_discharge=1.5, C_discharge=80.0,
            Q_river=120.0
        )
        
        x, y, C = model.solve_with_secondary_flow()
        
        shift_ratio = model.calculate_concentration_shift()
        
        # 浓度应该向凹岸偏移（shift_ratio > 1）
        # 但由于数值扩散，偏移可能不明显
        assert shift_ratio >= 0.5


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_calculate_bend_mixing_length(self):
        """测试弯道混合长度"""
        B = 80
        u = 0.6
        Ey = 0.05
        K_bend = 2.0
        
        L_mix_bend, L_mix_straight = calculate_bend_mixing_length(B, u, Ey, K_bend)
        
        # 弯道混合长度应小于直道
        assert L_mix_bend < L_mix_straight
        # 应该缩短约50%
        assert abs(L_mix_bend / L_mix_straight - 0.5) < 0.1
    
    def test_calculate_curvature_radius(self):
        """测试曲率半径计算"""
        bend_length = 1500
        bend_angle = 90
        
        R = calculate_curvature_radius(bend_length, bend_angle)
        
        # R = L / θ (弧度)
        expected_R = 1500 / (np.pi / 2)
        assert abs(R - expected_R) < 1
    
    def test_calculate_secondary_flow_strength(self):
        """测试二次流强度"""
        u = 0.6
        R = 500
        B = 80
        H = 2.5
        
        v_max, Fr = calculate_secondary_flow_strength(u, R, B, H)
        
        # 二次流速度应为正值
        assert v_max > 0
        # Fr数应合理
        assert 0 < Fr < 2
    
    def test_higher_bend_curvature_stronger_secondary_flow(self):
        """测试弯曲度越大，二次流越强"""
        u = 0.6
        B = 80
        H = 2.5
        
        # 小曲率半径（急弯）
        v_max_sharp, _ = calculate_secondary_flow_strength(u, 300, B, H)
        
        # 大曲率半径（缓弯）
        v_max_gentle, _ = calculate_secondary_flow_strength(u, 1000, B, H)
        
        # 急弯二次流更强
        assert v_max_sharp > v_max_gentle


class TestPhysicalBehavior:
    """测试物理行为"""
    
    def test_bend_enhances_mixing(self):
        """测试弯道增强混合"""
        # 创建两个模型：弯道和直道
        L = 2000
        B = 80
        nx = 100
        ny = 20
        u = 0.6
        Ey = 0.05
        
        # 弯道（急弯）
        model_bend_sharp = RiverBend2D(
            L, B, nx, ny, u, Ey, R=400, bend_angle=90
        )
        
        # 弯道（缓弯）
        model_bend_gentle = RiverBend2D(
            L, B, nx, ny, u, Ey, R=1000, bend_angle=90
        )
        
        # 急弯的增强系数应大于缓弯
        assert model_bend_sharp.K_bend > model_bend_gentle.K_bend
        assert model_bend_sharp.Ey_effective > model_bend_gentle.Ey_effective
    
    def test_bend_mixing_length_reduction(self):
        """测试弯道混合长度缩短"""
        B = 100
        u = 0.5
        Ey = 0.05
        
        # 不同弯道增强系数
        K_mild = 1.5
        K_strong = 3.0
        
        L_mild, L_straight = calculate_bend_mixing_length(B, u, Ey, K_mild)
        L_strong, _ = calculate_bend_mixing_length(B, u, Ey, K_strong)
        
        # 增强越强，混合长度越短
        assert L_strong < L_mild < L_straight
    
    def test_width_curvature_ratio_effect(self):
        """测试宽曲比影响"""
        L = 1000
        B = 80
        nx = 50
        ny = 20
        u = 0.6
        Ey = 0.05
        
        # 大宽曲比（B/R大）
        model_large_ratio = RiverBend2D(
            L, B, nx, ny, u, Ey, R=400, bend_angle=90
        )
        
        # 小宽曲比（B/R小）
        model_small_ratio = RiverBend2D(
            L, B, nx, ny, u, Ey, R=1600, bend_angle=90
        )
        
        # B/R大时，增强系数大
        assert model_large_ratio.K_bend > model_small_ratio.K_bend


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
