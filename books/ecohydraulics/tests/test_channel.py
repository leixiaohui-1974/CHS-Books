"""
测试河道模型
===========
"""

import pytest
import numpy as np
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.channel import River, RiverReach


class TestRiverReach:
    """测试RiverReach类"""
    
    def setup_method(self):
        """设置测试用例"""
        self.reach = RiverReach(
            length=1000.0,
            width=10.0,
            slope=0.001,
            roughness=0.030,
            side_slope=2.0
        )
    
    def test_initialization(self):
        """测试初始化"""
        assert self.reach.length == 1000.0
        assert self.reach.b == 10.0
        assert self.reach.S0 == 0.001
        assert self.reach.n == 0.030
        assert self.reach.m == 2.0
    
    def test_area(self):
        """测试断面面积计算"""
        h = 2.0
        A = self.reach.area(h)
        A_expected = (10.0 + 2.0 * 2.0) * 2.0  # (b + m*h)*h
        assert abs(A - A_expected) < 1e-6
        
    def test_wetted_perimeter(self):
        """测试湿周计算"""
        h = 2.0
        chi = self.reach.wetted_perimeter(h)
        chi_expected = 10.0 + 2 * 2.0 * np.sqrt(1 + 2.0**2)
        assert abs(chi - chi_expected) < 1e-6
    
    def test_hydraulic_radius(self):
        """测试水力半径计算"""
        h = 2.0
        R = self.reach.hydraulic_radius(h)
        A = self.reach.area(h)
        chi = self.reach.wetted_perimeter(h)
        R_expected = A / chi
        assert abs(R - R_expected) < 1e-6
    
    def test_top_width(self):
        """测试水面宽度计算"""
        h = 2.0
        B = self.reach.top_width(h)
        B_expected = 10.0 + 2 * 2.0 * 2.0  # b + 2*m*h
        assert abs(B - B_expected) < 1e-6
    
    def test_velocity_manning(self):
        """测试Manning流速计算"""
        h = 2.0
        v = self.reach.velocity_manning(h)
        # v应该为正值且在合理范围内
        assert v > 0
        assert v < 10.0  # 明渠流速一般不超过10 m/s
    
    def test_discharge_manning(self):
        """测试流量计算"""
        h = 2.0
        Q = self.reach.discharge_manning(h)
        A = self.reach.area(h)
        v = self.reach.velocity_manning(h)
        Q_expected = A * v
        assert abs(Q - Q_expected) < 1e-6
    
    def test_solve_depth(self):
        """测试水深求解"""
        Q = 5.0
        h = self.reach.solve_depth(Q)
        
        # 验证：用求得的水深计算流量应该等于输入流量
        Q_check = self.reach.discharge_manning(h)
        assert abs(Q_check - Q) / Q < 0.001  # 相对误差小于0.1%
        
        # 水深应该为正值
        assert h > 0
    
    def test_get_hydraulic_properties(self):
        """测试获取全部水力要素"""
        h = 2.0
        props = self.reach.get_hydraulic_properties(h)
        
        # 检查所有键是否存在
        required_keys = ['depth', 'area', 'wetted_perimeter', 
                        'hydraulic_radius', 'top_width', 'velocity', 'discharge']
        for key in required_keys:
            assert key in props
        
        # 检查值的一致性
        assert props['depth'] == h
        assert props['area'] == self.reach.area(h)


class TestRiver:
    """测试River类"""
    
    def setup_method(self):
        """设置测试用例"""
        self.river = River(name="Test River", mean_annual_flow=10.0)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.river.name == "Test River"
        assert self.river.Q_maf == 10.0
        assert len(self.river.reaches) == 0
    
    def test_add_reach(self):
        """测试添加河段"""
        reach1 = RiverReach(1000, 10, 0.001, 0.03, 2.0)
        reach2 = RiverReach(2000, 12, 0.0015, 0.035, 2.5)
        
        self.river.add_reach(reach1)
        self.river.add_reach(reach2)
        
        assert len(self.river.reaches) == 2
        assert self.river.reaches[0] == reach1
        assert self.river.reaches[1] == reach2
    
    def test_total_length(self):
        """测试总长度计算"""
        reach1 = RiverReach(1000, 10, 0.001, 0.03, 2.0)
        reach2 = RiverReach(2000, 12, 0.0015, 0.035, 2.5)
        
        self.river.add_reach(reach1)
        self.river.add_reach(reach2)
        
        total_length = self.river.total_length()
        assert total_length == 3000.0
    
    def test_average_wetted_perimeter(self):
        """测试平均湿周计算"""
        reach1 = RiverReach(1000, 10, 0.001, 0.03, 2.0)
        reach2 = RiverReach(1000, 10, 0.001, 0.03, 2.0)
        
        self.river.add_reach(reach1)
        self.river.add_reach(reach2)
        
        wp_avg = self.river.average_wetted_perimeter(5.0)
        
        # 平均湿周应该为正值
        assert wp_avg > 0
        
        # 两个相同河段的平均湿周应该等于单个河段的湿周
        h = reach1.solve_depth(5.0)
        wp_single = reach1.wetted_perimeter(h)
        assert abs(wp_avg - wp_single) < 1e-6


class TestEdgeCases:
    """测试边界情况"""
    
    def test_zero_depth(self):
        """测试零水深情况"""
        reach = RiverReach(1000, 10, 0.001, 0.03, 2.0)
        
        A = reach.area(0.0)
        assert A == 0.0
        
        chi = reach.wetted_perimeter(0.0)
        assert chi == reach.b
    
    def test_large_depth(self):
        """测试大水深情况"""
        reach = RiverReach(1000, 10, 0.001, 0.03, 2.0)
        
        h = 100.0
        A = reach.area(h)
        # 大水深时断面积应该接近 m*h^2
        A_approx = reach.m * h**2
        assert abs(A - A_approx) / A_approx < 0.2  # 相对误差小于20%
    
    def test_steep_slope(self):
        """测试陡坡情况"""
        reach = RiverReach(1000, 10, 0.01, 0.03, 2.0)  # 坡度1%
        
        Q = 5.0
        h = reach.solve_depth(Q)
        
        # 陡坡情况下水深应该较小
        assert h > 0
        assert h < 10.0
    
    def test_gentle_slope(self):
        """测试缓坡情况"""
        reach = RiverReach(1000, 10, 0.0001, 0.03, 2.0)  # 坡度0.01%
        
        Q = 5.0
        h = reach.solve_depth(Q)
        
        # 缓坡情况下水深应该较大
        assert h > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
