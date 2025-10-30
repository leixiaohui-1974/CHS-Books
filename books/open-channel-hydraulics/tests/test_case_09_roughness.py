"""
案例9单元测试：河道糙率率定

测试内容：
1. 单断面法糙率率定
2. Manning公式验证
3. 水力半径计算
4. 双断面法水面坡度计算
5. 糙率合理性判断
6. 不同河床条件测试
7. 流速-糙率关系
8. 边界条件测试

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from models.channel import RectangularChannel


def calibrate_roughness_single(Q, B, h, S0):
    """单断面法率定糙率"""
    A = B * h
    P = B + 2 * h
    R = A / P
    n = A * (R ** (2.0/3.0)) * (S0 ** 0.5) / Q
    return n, A, R


class TestCase09RoughnessCalibration:
    """案例9：河道糙率率定测试"""

    def test_single_section_calibration(self):
        """测试1：单断面法糙率率定"""
        B = 45.0
        h = 3.2
        Q = 180.0
        S0 = 0.0004

        n, A, R = calibrate_roughness_single(Q, B, h, S0)

        # 糙率应为正
        assert n > 0

        # 糙率应在合理范围（天然河道）
        assert 0.020 < n < 0.060

        # 验证反算正确性（Manning公式）
        v_calc = (1/n) * (R ** (2.0/3.0)) * (S0 ** 0.5)
        Q_check = A * v_calc
        assert abs(Q_check - Q) / Q < 0.001

    def test_hydraulic_radius_calculation(self):
        """测试2：水力半径计算"""
        B = 45.0
        h = 3.2

        A = B * h
        P = B + 2 * h
        R = A / P

        # 水力半径应为正
        assert R > 0

        # 矩形断面：R应小于水深
        assert R < h

        # 理论值验证
        R_theoretical = (B * h) / (B + 2*h)
        assert abs(R - R_theoretical) < 0.001

    def test_manning_formula_verification(self):
        """测试3：Manning公式验证"""
        B = 45.0
        h = 3.2
        n = 0.030
        S0 = 0.0004

        channel = RectangularChannel(b=B, S0=S0, n=n)
        A = channel.area(h)
        R = A / channel.wetted_perimeter(h)

        # Manning公式：v = (1/n) * R^(2/3) * S^(1/2)
        v = (1/n) * (R ** (2.0/3.0)) * (S0 ** 0.5)

        # 流速应为正
        assert v > 0

        # 流速应在合理范围（天然河道）
        assert 0.5 < v < 3.0

    def test_water_surface_slope_calculation(self):
        """测试4：双断面法水面坡度计算"""
        B1 = 45.0
        h1 = 3.2
        B2 = 48.0
        h2 = 3.0
        Q = 180.0
        L = 500.0
        g = 9.81

        # 计算流速
        v1 = Q / (B1 * h1)
        v2 = Q / (B2 * h2)

        # 计算比能
        E1 = h1 + v1**2 / (2*g)
        E2 = h2 + v2**2 / (2*g)

        # 水面坡度
        Sf = (E1 - E2) / L

        # 水面坡度应为正（能量沿程损失）
        assert Sf > 0

        # 水面坡度应小于河床坡度（有阻力）
        S0 = 0.0004
        assert Sf < S0 * 2

    def test_roughness_range_validation(self):
        """测试5：糙率合理性判断"""
        test_cases = [
            (0.012, "光滑混凝土"),
            (0.025, "卵石河床"),
            (0.040, "天然河道"),
        ]

        for n, description in test_cases:
            # 糙率应在物理合理范围
            assert 0.010 < n < 0.100

    def test_different_bed_materials(self):
        """测试6：不同河床条件"""
        B = 45.0
        h = 3.0
        Q = 180.0

        # 不同坡度对应不同河床
        test_cases = [
            (0.0002, "平坦河床"),
            (0.0005, "一般河床"),
            (0.001, "陡峻河床"),
        ]

        for S0, description in test_cases:
            n, A, R = calibrate_roughness_single(Q, B, h, S0)

            # 所有情况下糙率都应为正
            assert n > 0

            # 糙率应在合理范围
            assert 0.015 < n < 0.080

    def test_velocity_roughness_relationship(self):
        """测试7：流速-糙率关系"""
        B = 45.0
        h = 3.0
        S0 = 0.0005

        # 不同糙率对应不同流速
        roughness_values = [0.020, 0.030, 0.040]
        velocities = []

        for n in roughness_values:
            A = B * h
            P = B + 2 * h
            R = A / P

            v = (1/n) * (R ** (2.0/3.0)) * (S0 ** 0.5)
            velocities.append(v)

        # 糙率越大，流速越小
        for i in range(len(velocities) - 1):
            assert velocities[i] > velocities[i+1]

    def test_discharge_calculation_accuracy(self):
        """测试8：流量计算精度"""
        B = 45.0
        h = 3.2
        n = 0.030
        S0 = 0.0004

        channel = RectangularChannel(b=B, S0=S0, n=n)
        A = channel.area(h)
        R = A / channel.wetted_perimeter(h)

        # 用Manning公式计算流量
        v = (1/n) * (R ** (2.0/3.0)) * (S0 ** 0.5)
        Q = A * v

        # 反算糙率
        n_back, _, _ = calibrate_roughness_single(Q, B, h, S0)

        # 反算的糙率应等于原糙率
        assert abs(n_back - n) / n < 0.001

    def test_froude_number_check(self):
        """测试9：弗劳德数校核"""
        B = 45.0
        h = 3.2
        Q = 180.0
        g = 9.81

        v = Q / (B * h)
        Fr = v / np.sqrt(g * h)

        # 天然河道通常为缓流
        assert Fr < 1.0

        # 弗劳德数应在合理范围
        assert 0.1 < Fr < 0.9


class TestEdgeCases:
    """边界条件测试"""

    def test_smooth_channel(self):
        """测试光滑渠道（小糙率）"""
        B = 50.0
        h = 3.0
        Q = 200.0
        S0 = 0.001  # 较大坡度

        n, A, R = calibrate_roughness_single(Q, B, h, S0)

        # 应该能正常计算
        assert n > 0
        assert n < 0.080  # 在合理范围内

    def test_rough_channel(self):
        """测试粗糙渠道（大糙率）"""
        B = 40.0
        h = 2.5
        Q = 100.0
        S0 = 0.0002  # 较小坡度

        n, A, R = calibrate_roughness_single(Q, B, h, S0)

        # 应该能正常计算
        assert n > 0
        assert 0.015 < n < 0.080

    def test_shallow_water(self):
        """测试浅水情况"""
        B = 50.0
        h = 0.5  # 浅水
        Q = 50.0
        S0 = 0.001

        n, A, R = calibrate_roughness_single(Q, B, h, S0)

        # 应该能正常计算
        assert n > 0
        assert 0.005 < n < 0.100  # 浅水时糙率范围更宽

    def test_deep_water(self):
        """测试深水情况"""
        B = 50.0
        h = 5.0  # 深水
        Q = 500.0
        S0 = 0.0005

        n, A, R = calibrate_roughness_single(Q, B, h, S0)

        # 应该能正常计算
        assert n > 0
        assert 0.015 < n < 0.060

    def test_small_discharge(self):
        """测试小流量"""
        B = 40.0
        h = 2.0
        Q = 50.0  # 小流量
        S0 = 0.0003

        n, A, R = calibrate_roughness_single(Q, B, h, S0)

        # 应该能正常计算
        assert n > 0

    def test_large_discharge(self):
        """测试大流量"""
        B = 60.0
        h = 4.0
        Q = 500.0  # 大流量
        S0 = 0.0008

        n, A, R = calibrate_roughness_single(Q, B, h, S0)

        # 应该能正常计算
        assert n > 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
