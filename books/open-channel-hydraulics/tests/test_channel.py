"""
渠道类单元测试

测试 TrapezoidalChannel、RectangularChannel 和 CircularChannel 类
"""

import sys
import os
import unittest
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.channel import TrapezoidalChannel, RectangularChannel, CircularChannel


class TestTrapezoidalChannel(unittest.TestCase):
    """测试梯形断面类"""

    def setUp(self):
        """设置测试数据"""
        self.channel = TrapezoidalChannel(b=1.0, m=1.5, n=0.025, S0=0.0002)

    def test_area(self):
        """测试断面积计算"""
        h = 1.0
        A = self.channel.area(h)
        # 手算：A = (b + m*h)*h = (1.0 + 1.5*1.0)*1.0 = 2.5
        self.assertAlmostEqual(A, 2.5, places=5)

    def test_wetted_perimeter(self):
        """测试湿周计算"""
        h = 1.0
        chi = self.channel.wetted_perimeter(h)
        # 手算：χ = b + 2*h*sqrt(1+m²) = 1.0 + 2*1.0*sqrt(1+1.5²) = 1.0 + 2*1.803 = 4.606
        self.assertAlmostEqual(chi, 4.606, places=2)

    def test_hydraulic_radius(self):
        """测试水力半径计算"""
        h = 1.0
        R = self.channel.hydraulic_radius(h)
        A = self.channel.area(h)
        chi = self.channel.wetted_perimeter(h)
        self.assertAlmostEqual(R, A/chi, places=5)

    def test_top_width(self):
        """测试水面宽度计算"""
        h = 1.0
        B = self.channel.top_width(h)
        # 手算：B = b + 2*m*h = 1.0 + 2*1.5*1.0 = 4.0
        self.assertAlmostEqual(B, 4.0, places=5)

    def test_normal_depth(self):
        """测试正常水深计算"""
        Q = 0.5
        h0 = self.channel.compute_normal_depth(Q)

        # 验证：计算的水深应该满足Q方程
        Q_calc = self.channel.discharge(h0)
        self.assertAlmostEqual(Q_calc, Q, places=4)

        # 水深应该为正
        self.assertGreater(h0, 0)

    def test_critical_depth(self):
        """测试临界水深计算"""
        Q = 0.5
        hc = self.channel.compute_critical_depth(Q)

        # 验证：临界条件 Q²*B/(g*A³) = 1
        A = self.channel.area(hc)
        B = self.channel.top_width(hc)
        g = 9.81
        criterion = Q**2 * B / (g * A**3)
        self.assertAlmostEqual(criterion, 1.0, places=4)

        # 验证：Fr应该接近1（使用临界流速v=Q/A，而不是曼宁公式）
        v = Q / A
        hm = self.channel.hydraulic_depth(hc)
        Fr = v / np.sqrt(g * hm)
        self.assertAlmostEqual(Fr, 1.0, places=2)

        # 水深应该为正
        self.assertGreater(hc, 0)

    def test_froude_number(self):
        """测试弗劳德数计算"""
        h = 0.74
        Fr = self.channel.froude_number(h)

        # Fr应该在合理范围内
        self.assertGreater(Fr, 0)
        self.assertLess(Fr, 3)  # 一般明渠流Fr不会超过3

    def test_invalid_parameters(self):
        """测试无效参数"""
        # 负的渠底宽度
        with self.assertRaises(ValueError):
            TrapezoidalChannel(b=-1.0, m=1.5, n=0.025, S0=0.0002)

        # 负的糙率系数
        with self.assertRaises(ValueError):
            TrapezoidalChannel(b=1.0, m=1.5, n=-0.025, S0=0.0002)

        # 负的坡度
        with self.assertRaises(ValueError):
            TrapezoidalChannel(b=1.0, m=1.5, n=0.025, S0=-0.0002)


class TestRectangularChannel(unittest.TestCase):
    """测试矩形断面类"""

    def setUp(self):
        """设置测试数据"""
        self.channel = RectangularChannel(b=2.0, n=0.020, S0=0.001)

    def test_area(self):
        """测试断面积计算"""
        h = 1.0
        A = self.channel.area(h)
        # 矩形：A = b*h = 2.0*1.0 = 2.0
        self.assertAlmostEqual(A, 2.0, places=5)

    def test_wetted_perimeter(self):
        """测试湿周计算"""
        h = 1.0
        chi = self.channel.wetted_perimeter(h)
        # 矩形：χ = b + 2*h = 2.0 + 2*1.0 = 4.0
        self.assertAlmostEqual(chi, 4.0, places=5)

    def test_top_width(self):
        """测试水面宽度计算"""
        h = 1.0
        B = self.channel.top_width(h)
        # 矩形：B = b = 2.0
        self.assertAlmostEqual(B, 2.0, places=5)


class TestCircularChannel(unittest.TestCase):
    """测试圆形断面类"""

    def setUp(self):
        """设置测试数据"""
        self.channel = CircularChannel(D=1.0, n=0.015, S0=0.001)

    def test_area_half_full(self):
        """测试半满时的断面积"""
        h = 0.5  # 半满
        A = self.channel.area(h)
        # 半满：A = π*R²/2 = π*0.5²/2 = 0.3927
        self.assertAlmostEqual(A, np.pi * 0.25 / 2, places=3)

    def test_area_full(self):
        """测试满管时的断面积"""
        h = 1.0  # 满管
        A = self.channel.area(h)
        # 满管：A = π*R² = π*0.5² = 0.7854
        self.assertAlmostEqual(A, np.pi * 0.25, places=3)

    def test_invalid_depth(self):
        """测试无效水深"""
        # 水深超过管径
        with self.assertRaises(ValueError):
            self.channel.area(1.5)

        # 负水深
        with self.assertRaises(ValueError):
            self.channel.area(-0.1)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
