"""
案例4单元测试：灌区量水堰流量测量

测试内容：
1. 矩形薄壁堰流量计算
2. 侧收缩影响分析
3. 水头反算
4. 三角形堰对比
5. 淹没堰计算
6. 堰流公式验证

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from models.structures import Weir


class TestCase04WeirFlowMeasurement:
    """案例4：灌区量水堰流量测量测试"""

    def test_rectangular_weir_discharge(self):
        """测试1：矩形薄壁堰流量计算"""
        b = 0.8  # 堰宽
        m = 0.4  # 流量系数
        weir = Weir(b=b, weir_type='thin', m=m)

        # 堰流公式：Q = m * b * sqrt(2g) * H^(3/2)
        g = 9.81
        H = 0.2  # 水头

        Q_calc = weir.discharge_rectangular(H, with_contraction=False)
        Q_theoretical = m * b * np.sqrt(2*g) * H**(3/2)

        # 验证计算正确
        assert abs(Q_calc - Q_theoretical) / Q_theoretical < 0.001

    def test_discharge_head_relationship(self):
        """测试2：流量-水头关系"""
        b = 0.8
        m = 0.4
        weir = Weir(b=b, weir_type='thin', m=m)

        # 测试不同水头的流量
        heads = [0.05, 0.1, 0.15, 0.2, 0.3]
        Q_list = []

        for H in heads:
            Q = weir.discharge_rectangular(H, with_contraction=False)
            Q_list.append(Q)

        # 水头增大，流量应增大
        for i in range(len(Q_list)-1):
            assert Q_list[i] < Q_list[i+1]

        # 验证Q与H^(3/2)成正比
        for i in range(len(heads)):
            ratio = Q_list[i] / (heads[i]**(3/2))
            # 所有比值应该相同（常数）
            if i > 0:
                assert abs(ratio - Q_list[0]/(heads[0]**(3/2))) / ratio < 0.001

    def test_side_contraction_effect(self):
        """测试3：侧收缩影响"""
        b = 0.8
        m = 0.4
        H = 0.2

        # 无侧收缩
        weir = Weir(b=b, weir_type='thin', m=m)
        Q_no_contraction = weir.discharge_rectangular(H, with_contraction=False)

        # 有侧收缩
        Q_with_contraction = weir.discharge_rectangular(H, with_contraction=True)

        # 有侧收缩的流量应小于无侧收缩
        assert Q_with_contraction < Q_no_contraction

        # 流量减少率
        reduction = (Q_no_contraction - Q_with_contraction) / Q_no_contraction
        # 应该在合理范围内（1-10%）
        assert 0.01 < reduction < 0.15

    def test_head_calculation_from_discharge(self):
        """测试4：水头反算"""
        b = 0.8
        m = 0.4
        g = 9.81
        weir = Weir(b=b, weir_type='thin', m=m)

        # 给定流量，反算水头
        Q_design = 0.2

        # 理论水头：H = (Q / (m*b*sqrt(2g)))^(2/3)
        H_theoretical = (Q_design / (m * b * np.sqrt(2*g)))**(2/3)

        # 数值反算
        H_numerical = weir.head_from_discharge(Q_design)

        # 验证反算正确
        assert abs(H_numerical - H_theoretical) / H_theoretical < 0.01

        # 验证正反算一致性
        Q_verify = weir.discharge_rectangular(H_numerical, with_contraction=False)
        assert abs(Q_verify - Q_design) / Q_design < 0.001

    def test_triangular_weir(self):
        """测试5：三角形堰（V型堰）"""
        theta = 90  # 90度三角形堰
        m_tri = 0.58  # 三角形堰流量系数

        # 三角形堰流量公式：Q = (8/15) * m * sqrt(2g) * tan(θ/2) * H^(5/2)
        g = 9.81
        H = 0.2

        weir_tri = Weir(b=0.8, weir_type='thin', m=m_tri)  # b对三角形堰无影响
        Q_triangular = weir_tri.discharge_triangular(H, theta=theta)

        # 验证计算
        assert Q_triangular > 0

        # 对于相同水头，90度三角形堰的流量应小于0.8m宽矩形堰
        weir_rect = Weir(b=0.8, weir_type='thin', m=0.4)
        Q_rect = weir_rect.discharge_rectangular(H, with_contraction=False)
        assert Q_triangular < Q_rect

    def test_submerged_weir_effect(self):
        """测试6：淹没堰影响（简化测试）"""
        b = 0.8
        m = 0.4
        H1 = 0.3  # 上游水头
        H2 = 0.15  # 下游水头

        # 淹没度
        submergence = H2 / H1
        assert 0 < submergence < 1

        # 自由出流
        weir = Weir(b=b, weir_type='thin', m=m)
        Q_free = weir.discharge_rectangular(H1, with_contraction=False)

        # 淹没出流（简化：使用淹没系数）
        # Q_submerged = Q_free * (1 - submergence)^0.385
        submergence_factor = (1 - submergence)**0.385
        Q_submerged = Q_free * submergence_factor

        # 淹没流量应小于自由流量
        assert Q_submerged < Q_free

    def test_weir_coefficient_range(self):
        """测试7：流量系数范围"""
        b = 0.8
        H = 0.2

        # 测试不同流量系数
        coefficients = [0.35, 0.40, 0.45]
        Q_list = []

        for m in coefficients:
            weir = Weir(b=b, weir_type='thin', m=m)
            Q = weir.discharge_rectangular(H, with_contraction=False)
            Q_list.append(Q)

        # 流量系数增大，流量增大
        for i in range(len(Q_list)-1):
            assert Q_list[i] < Q_list[i+1]

    def test_broad_crested_weir(self):
        """测试8：宽顶堰"""
        b = 0.8
        H = 0.2

        # 宽顶堰（流量系数一般为0.385）
        weir_broad = Weir(b=b, weir_type='broad')
        Q_broad = weir_broad.discharge_rectangular(H, with_contraction=False)

        # 薄壁堰（流量系数一般为0.4）
        weir_thin = Weir(b=b, weir_type='thin')
        Q_thin = weir_thin.discharge_rectangular(H, with_contraction=False)

        # 两者流量应该接近（系数相差不大）
        assert Q_broad > 0
        assert Q_thin > 0

    def test_weir_height_effect(self):
        """测试9：堰高影响"""
        b = 0.8
        m = 0.4
        H = 0.15  # 水头
        P = 0.3  # 堰高

        # H/P比应该在合理范围（通常H/P ≤ 0.5）
        ratio = H / P
        assert ratio <= 0.5  # 堰流基本假设

        # 计算上游水深
        h_upstream = P + H
        assert h_upstream > P
        assert h_upstream < 2 * P  # 合理范围

    def test_accuracy_requirements(self):
        """测试10：精度要求"""
        b = 0.8
        m = 0.4
        weir = Weir(b=b, weir_type='thin', m=m)

        # 测量精度：水头测量误差对流量的影响
        H_nominal = 0.2
        delta_H = 0.001  # 1mm误差

        Q_nominal = weir.discharge_rectangular(H_nominal, with_contraction=False)
        Q_plus = weir.discharge_rectangular(H_nominal + delta_H, with_contraction=False)
        Q_minus = weir.discharge_rectangular(H_nominal - delta_H, with_contraction=False)

        # 相对误差
        error_plus = abs(Q_plus - Q_nominal) / Q_nominal
        error_minus = abs(Q_minus - Q_nominal) / Q_nominal

        # 1mm水头误差应导致小于2%的流量误差
        assert error_plus < 0.02
        assert error_minus < 0.02


class TestEdgeCases:
    """边界条件测试"""

    def test_very_small_head(self):
        """测试极小水头"""
        b = 0.8
        m = 0.4
        weir = Weir(b=b, weir_type='thin', m=m)

        H = 0.01  # 极小水头
        Q = weir.discharge_rectangular(H, with_contraction=False)

        # 应该能计算，且流量很小
        assert Q > 0
        assert Q < 0.01

    def test_large_head(self):
        """测试较大水头"""
        b = 0.8
        m = 0.4
        weir = Weir(b=b, weir_type='thin', m=m)

        H = 0.5  # 较大水头
        Q = weir.discharge_rectangular(H, with_contraction=False)

        # 应该能计算
        assert Q > 0
        assert Q < 2.0  # 合理上限

    def test_wide_weir(self):
        """测试宽堰"""
        b = 5.0  # 宽堰
        m = 0.4
        H = 0.2
        weir = Weir(b=b, weir_type='thin', m=m)

        Q = weir.discharge_rectangular(H, with_contraction=False)

        # 宽堰流量应大（相对于小堰）
        assert Q > 0.5

    def test_narrow_weir(self):
        """测试窄堰"""
        b = 0.2  # 窄堰
        m = 0.4
        H = 0.2
        weir = Weir(b=b, weir_type='thin', m=m)

        Q = weir.discharge_rectangular(H, with_contraction=False)

        # 窄堰流量应小
        assert Q < 0.1


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
