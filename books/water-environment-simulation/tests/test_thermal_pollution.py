"""
测试热污染扩散模型
Test Thermal Pollution Model
"""

import pytest
import numpy as np
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.thermal_pollution import (ThermalPlume2D, calculate_surface_heat_exchange,
                                      calculate_thermal_tolerance, calculate_cooling_efficiency)


class TestThermalPlume2D:
    """测试ThermalPlume2D类"""
    
    def test_initialization(self):
        """测试初始化"""
        model = ThermalPlume2D(
            Lx=1000, Ly=100, nx=50, ny=20,
            u=1.0, Kx=10.0, Ky=2.0,
            lambda_surface=0.1, T_ambient=20.0
        )
        
        assert model.Lx == 1000
        assert model.Ly == 100
        assert model.nx == 50
        assert model.ny == 20
        assert model.u == 1.0
        assert model.T_ambient == 20.0
        assert len(model.x) == 50
        assert len(model.y) == 20
    
    def test_set_discharge(self):
        """测试设置温排水源"""
        model = ThermalPlume2D(
            Lx=1000, Ly=100, nx=50, ny=20,
            u=1.0, Kx=10.0, Ky=2.0,
            lambda_surface=0.1, T_ambient=20.0
        )
        
        model.set_discharge(
            x=0, y=0,
            Q_discharge=10.0, T_discharge=30.0,
            Q_river=100.0
        )
        
        assert model.source_x == 0
        assert model.source_y == 0
        
        # 检查排放温度
        assert model.T_discharge == 30.0
        
        # 检查热排放量计算
        expected_Q = 4.18 * 10.0 * (30.0 - 20.0)
        assert abs(model.Q_thermal - expected_Q) < 0.1
    
    def test_solve_steady_state(self):
        """测试稳态求解"""
        model = ThermalPlume2D(
            Lx=1000, Ly=100, nx=50, ny=20,
            u=1.0, Kx=10.0, Ky=2.0,
            lambda_surface=0.1, T_ambient=20.0
        )
        
        model.set_discharge(
            x=0, y=0,
            Q_discharge=10.0, T_discharge=30.0,
            Q_river=100.0
        )
        
        x, y, T = model.solve_steady_state()
        
        # 检查结果形状
        assert T.shape == (20, 50)
        
        # 检查温度范围
        assert np.all(T >= 20.0)
        
        # 检查最高温度高于环境温度
        T_max = np.max(T)
        assert T_max > 20.0
        assert T_max <= 30.0
    
    def test_temperature_decay(self):
        """测试温度衰减"""
        model = ThermalPlume2D(
            Lx=2000, Ly=100, nx=100, ny=20,
            u=1.0, Kx=10.0, Ky=2.0,
            lambda_surface=0.2, T_ambient=20.0
        )
        
        model.set_discharge(
            x=0, y=0,
            Q_discharge=20.0, T_discharge=35.0,
            Q_river=100.0
        )
        
        x, y, T = model.solve_steady_state()
        
        # 检查中心线温度递减
        T_centerline = T[10, :]
        T_max = np.max(T_centerline)
        T_end = T_centerline[-1]
        
        assert T_max > T_end
        assert T_end > 20.0  # 仍高于环境温度
    
    def test_calculate_mixing_zone(self):
        """测试混合区计算"""
        model = ThermalPlume2D(
            Lx=2000, Ly=100, nx=100, ny=20,
            u=1.0, Kx=10.0, Ky=2.0,
            lambda_surface=0.1, T_ambient=20.0
        )
        
        model.set_discharge(
            x=0, y=0,
            Q_discharge=20.0, T_discharge=30.0,
            Q_river=100.0
        )
        
        x, y, T = model.solve_steady_state()
        
        # 计算混合区
        T_standard = 23.0  # 3°C温升
        area, length, width = model.calculate_mixing_zone(T_standard)
        
        assert area > 0
        assert length > 0
        assert length <= 2000
        assert width > 0
        assert width <= 100
    
    def test_calculate_thermal_impact(self):
        """测试热冲击影响计算"""
        model = ThermalPlume2D(
            Lx=1000, Ly=100, nx=50, ny=20,
            u=1.0, Kx=10.0, Ky=2.0,
            lambda_surface=0.1, T_ambient=20.0
        )
        
        model.set_discharge(
            x=0, y=0,
            Q_discharge=20.0, T_discharge=35.0,
            Q_river=100.0
        )
        
        x, y, T = model.solve_steady_state()
        
        # 计算热冲击区域
        T_threshold = 25.0
        impact_area, max_delta_T = model.calculate_thermal_impact(T_threshold)
        
        assert impact_area >= 0
        assert max_delta_T >= 0


class TestSurfaceHeatExchange:
    """测试表面热交换函数"""
    
    def test_basic_calculation(self):
        """测试基本计算"""
        lambda_s, Q_net = calculate_surface_heat_exchange(
            T_water=25, T_air=20,
            wind_speed=3, solar_radiation=500
        )
        
        assert lambda_s > 0
        assert isinstance(Q_net, float)
    
    def test_temperature_effect(self):
        """测试温度影响"""
        lambda1, Q1 = calculate_surface_heat_exchange(
            T_water=20, T_air=20, wind_speed=3, solar_radiation=500
        )
        
        lambda2, Q2 = calculate_surface_heat_exchange(
            T_water=30, T_air=20, wind_speed=3, solar_radiation=500
        )
        
        # 温差大时，热交换系数应更大
        assert lambda2 > lambda1
    
    def test_wind_effect(self):
        """测试风速影响"""
        lambda1, Q1 = calculate_surface_heat_exchange(
            T_water=25, T_air=20, wind_speed=1, solar_radiation=500
        )
        
        lambda2, Q2 = calculate_surface_heat_exchange(
            T_water=25, T_air=20, wind_speed=5, solar_radiation=500
        )
        
        # 风速大时，散热增加，净热通量减小（绝对值）
        # 因此热交换系数可能减小（因为Q_net减小）
        # 实际上应该检查散热量增加
        assert Q2 < Q1  # 净热通量减小（因为散热多）
    
    def test_solar_radiation_effect(self):
        """测试太阳辐射影响"""
        lambda1, Q1 = calculate_surface_heat_exchange(
            T_water=25, T_air=20, wind_speed=3, solar_radiation=0
        )
        
        lambda2, Q2 = calculate_surface_heat_exchange(
            T_water=25, T_air=20, wind_speed=3, solar_radiation=800
        )
        
        # 太阳辐射影响净热通量
        assert Q2 > Q1


class TestThermalTolerance:
    """测试生物热耐受性函数"""
    
    def test_cold_water_fish(self):
        """测试冷水鱼"""
        T_lethal, T_stress = calculate_thermal_tolerance(
            'cold_water_fish', T_base=15, duration=24
        )
        
        assert T_lethal > T_stress
        assert T_stress > 15
        assert T_lethal < 30  # 冷水鱼致死温度较低
    
    def test_warm_water_fish(self):
        """测试温水鱼"""
        T_lethal, T_stress = calculate_thermal_tolerance(
            'warm_water_fish', T_base=20, duration=24
        )
        
        assert T_lethal > T_stress
        assert T_stress > 20
        assert T_lethal > 30  # 温水鱼耐受性更强
    
    def test_invertebrates(self):
        """测试无脊椎动物"""
        T_lethal, T_stress = calculate_thermal_tolerance(
            'invertebrates', T_base=18, duration=24
        )
        
        assert T_lethal > T_stress
        assert T_stress > 18
    
    def test_algae(self):
        """测试藻类"""
        T_lethal, T_stress = calculate_thermal_tolerance(
            'algae', T_base=20, duration=24
        )
        
        assert T_lethal > T_stress
        assert T_stress > 20
    
    def test_duration_effect(self):
        """测试暴露时间影响"""
        T_l1, T_s1 = calculate_thermal_tolerance(
            'warm_water_fish', T_base=20, duration=1
        )
        
        T_l2, T_s2 = calculate_thermal_tolerance(
            'warm_water_fish', T_base=20, duration=48
        )
        
        # 暴露时间长，耐受温度应降低
        assert T_l2 <= T_l1
        assert T_s2 <= T_s1


class TestCoolingEfficiency:
    """测试冷却效率函数"""
    
    def test_basic_calculation(self):
        """测试基本计算"""
        efficiency, Q_removed = calculate_cooling_efficiency(
            T_in=35, T_out=28, T_ambient=20, Q_cooling=100
        )
        
        assert 0 < efficiency <= 1
        assert Q_removed > 0
    
    def test_perfect_cooling(self):
        """测试完全冷却"""
        efficiency, Q_removed = calculate_cooling_efficiency(
            T_in=35, T_out=20, T_ambient=20, Q_cooling=100
        )
        
        # 完全冷却到环境温度
        assert abs(efficiency - 1.0) < 0.01
    
    def test_no_cooling(self):
        """测试无冷却"""
        efficiency, Q_removed = calculate_cooling_efficiency(
            T_in=35, T_out=35, T_ambient=20, Q_cooling=100
        )
        
        # 无冷却
        assert abs(efficiency) < 0.01
        assert abs(Q_removed) < 0.01
    
    def test_partial_cooling(self):
        """测试部分冷却"""
        efficiency1, Q1 = calculate_cooling_efficiency(
            T_in=35, T_out=30, T_ambient=20, Q_cooling=100
        )
        
        efficiency2, Q2 = calculate_cooling_efficiency(
            T_in=35, T_out=25, T_ambient=20, Q_cooling=100
        )
        
        # 冷却更多，效率更高
        assert efficiency2 > efficiency1
        assert Q2 > Q1
    
    def test_flow_rate_effect(self):
        """测试流量影响"""
        efficiency1, Q1 = calculate_cooling_efficiency(
            T_in=35, T_out=28, T_ambient=20, Q_cooling=50
        )
        
        efficiency2, Q2 = calculate_cooling_efficiency(
            T_in=35, T_out=28, T_ambient=20, Q_cooling=100
        )
        
        # 流量加倍，热移除量也应加倍
        assert abs(Q2 / Q1 - 2.0) < 0.1
        # 但效率相同
        assert abs(efficiency2 - efficiency1) < 0.01


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
