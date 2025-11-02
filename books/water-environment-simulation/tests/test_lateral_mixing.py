"""
测试河流横向混合模型
Test Lateral Mixing Model
"""

import pytest
import numpy as np
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.lateral_mixing import (LateralMixing2D, calculate_mixing_time,
                                    calculate_complete_mixing_distance,
                                    calculate_concentration_at_bank)


class TestLateralMixing2D:
    """测试LateralMixing2D类"""
    
    def test_initialization(self):
        """测试初始化"""
        model = LateralMixing2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ex=0.01, Ey=0.1
        )
        
        assert model.L == 1000
        assert model.B == 100
        assert model.nx == 50
        assert model.ny == 20
        assert model.u == 0.5
        assert len(model.x) == 50
        assert len(model.y) == 20
        assert model.C.shape == (20, 50)
    
    def test_add_source(self):
        """测试添加排放源"""
        model = LateralMixing2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ex=0.01, Ey=0.1
        )
        
        model.add_source(
            x=0, y=0,
            Q_discharge=2.0, C_discharge=100.0,
            Q_river=100.0
        )
        
        assert len(model.sources) == 1
        assert model.sources[0]['x'] == 0
        assert model.sources[0]['y'] == 0
        assert model.sources[0]['Q'] == 2.0
        assert model.sources[0]['C'] == 100.0
    
    def test_solve_steady_state_explicit(self):
        """测试显式求解"""
        model = LateralMixing2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ex=0.01, Ey=0.1
        )
        
        model.add_source(
            x=0, y=0,
            Q_discharge=2.0, C_discharge=100.0,
            Q_river=100.0
        )
        
        x, y, C = model.solve_steady_state(method='explicit')
        
        # 检查结果
        assert C.shape == (20, 50)
        assert np.all(C >= 0)
        assert np.max(C) > 0
    
    def test_solve_steady_state_implicit(self):
        """测试隐式求解"""
        model = LateralMixing2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ex=0.01, Ey=0.1
        )
        
        model.add_source(
            x=0, y=0,
            Q_discharge=2.0, C_discharge=100.0,
            Q_river=100.0
        )
        
        x, y, C = model.solve_steady_state(method='implicit')
        
        # 检查结果
        assert C.shape == (20, 50)
        assert np.all(C >= 0)
        assert np.max(C) > 0
    
    def test_concentration_decay(self):
        """测试浓度衰减"""
        model = LateralMixing2D(
            L=2000, B=100, nx=100, ny=20,
            u=0.5, Ex=0.01, Ey=0.2
        )
        
        model.add_source(
            x=0, y=0,
            Q_discharge=5.0, C_discharge=100.0,
            Q_river=100.0
        )
        
        x, y, C = model.solve_steady_state(method='implicit')
        
        # 检查排放侧浓度在下游逐渐降低（横向扩散）
        C_bank = C[0, :]
        # 排放口处浓度高
        assert C_bank[0] > 10
        # 下游浓度降低（扩散稀释）
        # 注意：由于横向扩散，排放侧浓度会先升高再降低
        assert C_bank[-1] < C_bank[0]
    
    def test_lateral_spreading(self):
        """测试横向扩散"""
        model = LateralMixing2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ex=0.01, Ey=0.2
        )
        
        model.add_source(
            x=0, y=0,
            Q_discharge=2.0, C_discharge=100.0,
            Q_river=100.0
        )
        
        x, y, C = model.solve_steady_state(method='implicit')
        
        # 检查横向浓度分布
        # 在下游某个断面，横向浓度应该更均匀
        C_upstream = C[:, 10]
        C_downstream = C[:, 40]
        
        # 下游断面的浓度变异系数应该小于上游
        cv_upstream = np.std(C_upstream) / np.mean(C_upstream) if np.mean(C_upstream) > 0 else 0
        cv_downstream = np.std(C_downstream) / np.mean(C_downstream) if np.mean(C_downstream) > 0 else 0
        
        # 下游更均匀（变异系数更小）
        assert cv_downstream <= cv_upstream + 0.1  # 允许一定误差
    
    def test_calculate_mixing_length(self):
        """测试混合长度计算"""
        model = LateralMixing2D(
            L=3000, B=100, nx=150, ny=30,
            u=0.5, Ex=0.01, Ey=0.1
        )
        
        model.add_source(
            x=0, y=0,
            Q_discharge=2.0, C_discharge=100.0,
            Q_river=100.0
        )
        
        x, y, C = model.solve_steady_state(method='implicit')
        
        L_mix = model.calculate_mixing_length(threshold=0.90)
        
        # 混合长度应该在合理范围内
        assert L_mix > 0
        assert L_mix <= 3000
    
    def test_calculate_lateral_dispersion_coefficient(self):
        """测试横向扩散系数计算"""
        model = LateralMixing2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ex=0.01, Ey=0.1
        )
        
        # 计算扩散系数
        H = 3.0  # 水深 (m)
        u_star = 0.05  # 摩阻流速 (m/s)
        B = 100  # 河宽 (m)
        
        Ey = model.calculate_lateral_dispersion_coefficient(H, u_star, B)
        
        # 检查结果合理性
        assert Ey > 0
        assert 0.01 < Ey < 1.0  # 典型范围


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_calculate_mixing_time(self):
        """测试混合时间计算"""
        B = 100  # 河宽 (m)
        Ey = 0.1  # 横向扩散系数 (m²/s)
        
        T_mix = calculate_mixing_time(B, Ey)
        
        # 检查结果合理性
        assert T_mix > 0
        # T_mix = B² / (6 * Ey) = 10000 / 0.6 ≈ 16667 s
        assert 10000 < T_mix < 20000
    
    def test_calculate_complete_mixing_distance(self):
        """测试完全混合距离计算"""
        B = 100  # 河宽 (m)
        u = 0.5  # 流速 (m/s)
        Ey = 0.1  # 横向扩散系数 (m²/s)
        
        L_mix = calculate_complete_mixing_distance(B, u, Ey)
        
        # 检查结果合理性
        assert L_mix > 0
        # L_mix = u * B² / (6 * Ey) ≈ 8333 m
        assert 5000 < L_mix < 15000
    
    def test_calculate_concentration_at_bank(self):
        """测试岸边浓度计算"""
        C0 = 100  # 排放浓度 (mg/L)
        y = 0  # 排放位置 (m)
        B = 100  # 河宽 (m)
        x = 1000  # 纵向距离 (m)
        Ey = 0.1  # 横向扩散系数 (m²/s)
        u = 0.5  # 流速 (m/s)
        
        C_bank = calculate_concentration_at_bank(C0, y, B, x, Ey, u)
        
        # 岸边浓度应该低于排放浓度
        assert 0 < C_bank < C0
    
    def test_mixing_time_increases_with_width(self):
        """测试混合时间随河宽增加"""
        Ey = 0.1
        
        T_mix_50 = calculate_mixing_time(50, Ey)
        T_mix_100 = calculate_mixing_time(100, Ey)
        
        # 河宽增加，混合时间增加（B²关系）
        assert T_mix_100 > T_mix_50
        assert abs(T_mix_100 / T_mix_50 - 4.0) < 0.1  # 应该约为4倍
    
    def test_mixing_time_decreases_with_Ey(self):
        """测试混合时间随Ey减小"""
        B = 100
        
        T_mix_low = calculate_mixing_time(B, 0.05)
        T_mix_high = calculate_mixing_time(B, 0.2)
        
        # Ey增加，混合时间减小
        assert T_mix_high < T_mix_low
    
    def test_mixing_distance_proportional_to_velocity(self):
        """测试混合距离与流速成正比"""
        B = 100
        Ey = 0.1
        
        L_mix_slow = calculate_complete_mixing_distance(B, 0.3, Ey)
        L_mix_fast = calculate_complete_mixing_distance(B, 0.6, Ey)
        
        # 流速加倍，混合距离加倍
        assert abs(L_mix_fast / L_mix_slow - 2.0) < 0.1


class TestPhysicalBehavior:
    """测试物理行为"""
    
    def test_mass_conservation(self):
        """测试质量守恒（简化检查）"""
        model = LateralMixing2D(
            L=1000, B=100, nx=50, ny=20,
            u=0.5, Ex=0.01, Ey=0.2
        )
        
        Q_discharge = 2.0
        C_discharge = 100.0
        Q_river = 100.0
        
        model.add_source(
            x=0, y=0,
            Q_discharge=Q_discharge,
            C_discharge=C_discharge,
            Q_river=Q_river
        )
        
        x, y, C = model.solve_steady_state(method='implicit')
        
        # 完全混合后的理论浓度
        C_theory = Q_discharge * C_discharge / Q_river
        
        # 检查下游远处断面平均浓度接近理论值
        C_downstream = C[:, -1]
        C_avg = np.mean(C_downstream)
        
        # 允许较大误差（由于数值扩散和边界效应）
        assert abs(C_avg - C_theory) < C_theory * 0.5
    
    def test_higher_Ey_faster_mixing(self):
        """测试更大的Ey导致更快混合"""
        # 低Ey
        model_low = LateralMixing2D(
            L=2000, B=100, nx=100, ny=20,
            u=0.5, Ex=0.01, Ey=0.05
        )
        model_low.add_source(0, 0, 2.0, 100.0, 100.0)
        x, y, C_low = model_low.solve_steady_state(method='implicit')
        
        # 高Ey
        model_high = LateralMixing2D(
            L=2000, B=100, nx=100, ny=20,
            u=0.5, Ex=0.01, Ey=0.2
        )
        model_high.add_source(0, 0, 2.0, 100.0, 100.0)
        x, y, C_high = model_high.solve_steady_state(method='implicit')
        
        # 在中游断面，高Ey情况下横向更均匀
        ix_mid = 50
        cv_low = np.std(C_low[:, ix_mid]) / np.mean(C_low[:, ix_mid]) if np.mean(C_low[:, ix_mid]) > 0 else 999
        cv_high = np.std(C_high[:, ix_mid]) / np.mean(C_high[:, ix_mid]) if np.mean(C_high[:, ix_mid]) > 0 else 999
        
        # 高Ey更均匀（变异系数更小）
        assert cv_high < cv_low + 0.2


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
