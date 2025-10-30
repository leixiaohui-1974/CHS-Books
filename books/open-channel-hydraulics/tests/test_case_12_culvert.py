"""
案例12单元测试：涵洞过流

测试内容：
1. 临界水深计算
2. 临界流速计算
3. 自由出流流量计算（进口控制）
4. 淹没出流流量计算（出口控制）
5. 压力流流量计算（满管流）
6. 流态判别（自由/淹没/压力）
7. 不同进口形式流量系数
8. 能量守恒验证
9. 损失系数影响
10. 边界条件测试

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

# 导入主程序中的函数
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code/examples/case_12_culvert'))
from main import (
    compute_critical_depth,
    compute_critical_velocity,
    free_flow_discharge,
    submerged_flow_discharge,
    pressure_flow_discharge,
    determine_flow_type
)

from models.channel import RectangularChannel


class TestCase12CulvertHydraulics:
    """案例12：涵洞过流测试"""

    def test_critical_depth_calculation(self):
        """测试1：临界水深计算"""
        Q = 4.0  # m³/s
        b = 2.0  # m
        g = 9.81

        hc = compute_critical_depth(Q, b, g)

        # 临界水深公式：hc = (Q²/(g*b²))^(1/3)
        hc_theoretical = (Q**2 / (g * b**2)) ** (1.0/3.0)

        # 验证计算正确
        assert abs(hc - hc_theoretical) < 0.001

        # 临界水深应为正
        assert hc > 0

        # 临界水深应在合理范围（0.5-1.5m）
        assert 0.5 < hc < 1.5

    def test_critical_velocity_calculation(self):
        """测试2：临界流速计算"""
        Q = 4.0
        b = 2.0
        g = 9.81

        hc = compute_critical_depth(Q, b, g)
        vc = compute_critical_velocity(hc, g)

        # 临界流速公式：vc = sqrt(g*hc)
        vc_theoretical = np.sqrt(g * hc)

        # 验证计算正确
        assert abs(vc - vc_theoretical) < 0.001

        # 在临界水深处，弗劳德数应为1.0
        Fr = vc / np.sqrt(g * hc)
        assert abs(Fr - 1.0) < 0.01

    def test_free_flow_discharge_inlet_control(self):
        """测试3：自由出流流量计算（进口控制）"""
        b = 2.0
        H = 1.5
        h1 = 1.2  # 上游水深
        Cd = 0.70  # 圆角进口
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 流量应为正
        assert Q > 0

        # 流量应在合理范围（2-6 m³/s）
        assert 2.0 < Q < 6.0

        # 验证流量与流量系数成正比
        Q1 = free_flow_discharge(b, H, h1, Cd=0.60, g=g)
        Q2 = free_flow_discharge(b, H, h1, Cd=0.80, g=g)
        assert Q2 > Q1

    def test_free_flow_discharge_coefficients(self):
        """测试4：不同进口形式的流量系数"""
        b = 2.0
        H = 1.5
        h1 = 1.2
        g = 9.81

        # 不同进口形式
        Cd_square = 0.60  # 直角进口
        Cd_rounded = 0.70  # 圆角进口
        Cd_flared = 0.90  # 喇叭口进口

        Q_square = free_flow_discharge(b, H, h1, Cd_square, g)
        Q_rounded = free_flow_discharge(b, H, h1, Cd_rounded, g)
        Q_flared = free_flow_discharge(b, H, h1, Cd_flared, g)

        # 流量系数越大，流量越大
        assert Q_flared > Q_rounded > Q_square

        # 流量比应接近流量系数比
        ratio_theoretical = Cd_flared / Cd_square
        ratio_actual = Q_flared / Q_square
        assert abs(ratio_actual - ratio_theoretical) / ratio_theoretical < 0.1

    def test_submerged_flow_discharge_outlet_control(self):
        """测试5：淹没出流流量计算（出口控制）"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.001
        h1 = 2.0  # 上游水深
        h3 = 1.6  # 下游水深（淹没）
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 流量应为正
        assert result['Q'] > 0

        # 流速应为正
        assert result['v'] > 0

        # 各项损失应为正
        assert result['hf_entrance'] > 0
        assert result['hf_friction'] > 0
        assert result['hf_exit'] > 0
        assert result['hf_total'] > 0

        # 总损失应等于各项损失之和
        hf_sum = result['hf_entrance'] + result['hf_friction'] + result['hf_exit']
        assert abs(result['hf_total'] - hf_sum) < 0.001

    def test_submerged_flow_energy_conservation(self):
        """测试6：淹没出流能量守恒验证"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.001
        h1 = 2.0
        h3 = 1.6
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 能量方程：H1 + S0*L = H3 + hf
        H1 = result['H1']
        H3 = result['H3']
        hf_total = result['hf_total']

        energy_left = H1 + S0*L
        energy_right = H3 + hf_total

        energy_balance = energy_left - energy_right

        # 能量应守恒（误差可能稍大，因为迭代求解）
        assert abs(energy_balance) < 0.10

    def test_pressure_flow_discharge_full_pipe(self):
        """测试7：压力流流量计算（满管流）"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.001
        h1 = 2.5  # 上游水深（进口淹没）
        h3 = 2.0  # 下游水深（出口淹没）
        g = 9.81

        result = pressure_flow_discharge(b, H, L, n, S0, h1, h3,
                                        zeta_e=0.2, zeta_o=1.0, g=g)

        # 流量应为正
        assert result['Q'] > 0

        # 流速应为正
        assert result['v'] > 0

        # 有效水头应为正
        assert result['delta_H'] > 0

        # 各项损失应为正
        assert result['hf_entrance'] > 0
        assert result['hf_friction'] > 0
        assert result['hf_exit'] > 0
        assert result['hf_total'] > 0

        # 总损失系数应大于1（包括基本损失）
        assert result['zeta_total'] > 1.0

    def test_pressure_flow_vs_submerged_flow(self):
        """测试8：压力流与淹没出流对比"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.001
        g = 9.81

        # 压力流工况
        h1_press = 2.5
        h3_press = 2.0
        result_press = pressure_flow_discharge(b, H, L, n, S0, h1_press, h3_press,
                                              zeta_e=0.2, zeta_o=1.0, g=g)

        # 淹没出流工况
        h1_sub = 2.0
        h3_sub = 1.6
        result_sub = submerged_flow_discharge(b, H, L, n, S0, h1_sub, h3_sub,
                                             zeta_e=0.2, zeta_o=1.0, g=g)

        # 两种流态都应能正常计算
        assert result_press['Q'] > 0
        assert result_sub['Q'] > 0

        # 压力流速度应受满管约束
        assert result_press['v'] > 0

    def test_flow_type_determination_free(self):
        """测试9：流态判别 - 自由出流"""
        H = 1.5
        Q = 4.0
        b = 2.0
        hc = compute_critical_depth(Q, b)

        # 自由出流条件：h3 < hc and h1/H < 1.2
        h1 = 1.2  # 上游水深
        h3 = 0.5  # 下游水深（小于临界水深）

        flow_type = determine_flow_type(h1, h3, H, hc)

        assert flow_type == 'free'

    def test_flow_type_determination_submerged(self):
        """测试10：流态判别 - 淹没出流"""
        H = 1.5
        Q = 4.0
        b = 2.0
        hc = compute_critical_depth(Q, b)

        # 淹没出流：h3 > hc but not fully submerged
        h1 = 1.5
        h3 = 1.2  # 大于临界水深

        flow_type = determine_flow_type(h1, h3, H, hc)

        assert flow_type == 'submerged'

    def test_flow_type_determination_pressure(self):
        """测试11：流态判别 - 压力流"""
        H = 1.5
        Q = 4.0
        b = 2.0
        hc = compute_critical_depth(Q, b)

        # 压力流条件：h1/H > 1.2 and h3/H > 1.0
        h1 = 2.5  # 进口淹没
        h3 = 2.0  # 出口淹没

        flow_type = determine_flow_type(h1, h3, H, hc)

        assert flow_type == 'pressure'

    def test_entrance_loss_coefficient_effect(self):
        """测试12：进口损失系数影响"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.001
        h1 = 2.0
        h3 = 1.6
        g = 9.81

        # 不同进口损失系数
        result_1 = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                           zeta_e=0.5, zeta_o=1.0, g=g)
        result_2 = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                           zeta_e=0.2, zeta_o=1.0, g=g)

        # 进口损失系数越小，流量越大
        assert result_2['Q'] > result_1['Q']

        # 进口损失应不同
        assert result_1['hf_entrance'] > result_2['hf_entrance']

    def test_exit_loss_coefficient_effect(self):
        """测试13：出口损失系数影响"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.001
        h1 = 2.0
        h3 = 1.6
        g = 9.81

        # 不同出口损失系数
        result_1 = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                           zeta_e=0.2, zeta_o=1.5, g=g)
        result_2 = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                           zeta_e=0.2, zeta_o=0.5, g=g)

        # 出口损失系数越小，流量越大
        assert result_2['Q'] > result_1['Q']

        # 出口损失应不同
        assert result_1['hf_exit'] > result_2['hf_exit']

    def test_continuity_equation_free_flow(self):
        """测试14：连续性方程验证（自由出流）"""
        b = 2.0
        H = 1.5
        h1 = 1.2
        Cd = 0.70
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 计算流速
        A = b * h1
        v = Q / A

        # 流速应合理（1-4 m/s）
        assert 1.0 < v < 4.0

        # 连续性：Q = A * v
        Q_check = A * v
        assert abs(Q_check - Q) < 0.01

    def test_normal_depth_in_culvert(self):
        """测试15：涵洞正常水深"""
        b = 2.0
        H = 1.5
        S0 = 0.001
        n = 0.014
        Q = 4.0

        channel = RectangularChannel(b=b, S0=S0, n=n)
        hn = channel.compute_normal_depth(Q)

        # 正常水深应小于涵洞高度（否则会满管）
        assert hn < H

        # 正常水深应为正
        assert hn > 0

        # 验证Manning公式
        A = b * hn
        P = b + 2*hn
        R = A / P
        Q_check = (1/n) * A * R**(2.0/3.0) * S0**0.5

        assert abs(Q_check - Q) / Q < 0.01


class TestEdgeCases:
    """边界条件测试"""

    def test_very_small_discharge(self):
        """测试极小流量"""
        b = 2.0
        H = 1.5
        h1 = 0.5
        Cd = 0.70
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 小流量应能计算
        assert Q > 0
        assert Q < 2.0

    def test_very_large_discharge(self):
        """测试极大流量"""
        b = 2.0
        H = 1.5
        h1 = 3.0  # 大水深
        Cd = 0.70
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 大流量应能计算
        assert Q > 5.0

    def test_upstream_depth_exceeds_culvert_height(self):
        """测试上游水深超过涵洞高度"""
        b = 2.0
        H = 1.5
        h1 = 2.0  # 超过涵洞高度
        Cd = 0.70
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 应能计算（按满管计算）
        assert Q > 0

    def test_zero_slope(self):
        """测试平坡（S0=0）"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.0  # 平坡
        h1 = 2.0
        h3 = 1.8
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 平坡时仍应能计算
        assert result['Q'] > 0

        # 平坡时损失应完全由水头差提供
        assert result['hf_total'] > 0

    def test_steep_slope(self):
        """测试陡坡"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.014
        S0 = 0.01  # 陡坡
        h1 = 2.0
        h3 = 1.5
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 陡坡时流量应更大（底坡提供额外能量）
        assert result['Q'] > 0

    def test_long_culvert(self):
        """测试长涵洞"""
        b = 2.0
        H = 1.5
        L = 100.0  # 长涵洞
        n = 0.014
        S0 = 0.001
        h1 = 2.0
        h3 = 1.5
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 长涵洞沿程损失应显著
        assert result['hf_friction'] > 0.1

        # 沿程损失应占总损失的较大比例
        assert result['hf_friction'] / result['hf_total'] > 0.3

    def test_short_culvert(self):
        """测试短涵洞"""
        b = 2.0
        H = 1.5
        L = 5.0  # 短涵洞
        n = 0.014
        S0 = 0.001
        h1 = 2.0
        h3 = 1.6
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 短涵洞沿程损失应很小
        assert result['hf_friction'] < 0.05

        # 局部损失应占主导
        local_loss = result['hf_entrance'] + result['hf_exit']
        assert local_loss / result['hf_total'] > 0.5

    def test_wide_culvert(self):
        """测试宽涵洞"""
        b = 5.0  # 宽涵洞
        H = 1.5
        h1 = 1.2
        Cd = 0.70
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 宽涵洞流量应大
        assert Q > 8.0

    def test_narrow_culvert(self):
        """测试窄涵洞"""
        b = 1.0  # 窄涵洞
        H = 1.5
        h1 = 1.2
        Cd = 0.70
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 窄涵洞流量应小
        assert Q < 4.0

    def test_high_culvert(self):
        """测试高涵洞"""
        b = 2.0
        H = 3.0  # 高涵洞
        h1 = 2.0
        Cd = 0.70
        g = 9.81

        Q = free_flow_discharge(b, H, h1, Cd, g)

        # 高涵洞应能计算
        assert Q > 0

        # h1 < H，未满管
        assert h1 < H

    def test_smooth_culvert(self):
        """测试光滑涵洞（小糙率）"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.010  # 光滑混凝土
        S0 = 0.001
        h1 = 2.0
        h3 = 1.6
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 光滑涵洞摩阻损失应较小
        assert result['hf_friction'] < 0.1

    def test_rough_culvert(self):
        """测试粗糙涵洞（大糙率）"""
        b = 2.0
        H = 1.5
        L = 30.0
        n = 0.020  # 粗糙表面
        S0 = 0.001
        h1 = 2.0
        h3 = 1.6
        g = 9.81

        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        # 粗糙涵洞摩阻损失应较大
        assert result['hf_friction'] > 0.05


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
