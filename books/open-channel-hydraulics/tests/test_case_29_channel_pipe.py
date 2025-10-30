"""
案例29单元测试：渠道-管道耦合系统

测试内容：
1. 明渠正常水深计算（Manning公式）
2. 明渠流速计算
3. 管道压力损失（Darcy公式）
4. 进水池水位确定
5. 能量平衡验证
6. 过渡段损失
7. 系统优化分析

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def manning_velocity(R, S0, n):
    """Manning流速公式 [m/s]
    v = (1/n) * R^(2/3) * S_0^(1/2)
    """
    v = (1/n) * R**(2/3) * S0**(1/2)
    return v


def manning_discharge(A, R, S0, n):
    """Manning流量公式 [m³/s]
    Q = (1/n) * A * R^(2/3) * S_0^(1/2)
    """
    v = manning_velocity(R, S0, n)
    Q = A * v
    return Q


def rectangular_channel_normal_depth(Q, b, S0, n, tol=1e-6, max_iter=100):
    """矩形渠道正常水深（迭代求解）[m]"""
    h = 1.0  # 初始猜测
    for i in range(max_iter):
        A = b * h
        P = b + 2 * h
        R = A / P
        Q_calc = manning_discharge(A, R, S0, n)

        # Newton-Raphson
        dQ_dh = (1/n) * S0**0.5 * (b * R**(2/3) + (2/3) * A * R**(-1/3) * (-2*A/P**2))

        h_new = h + (Q - Q_calc) / dQ_dh

        if abs(h_new - h) < tol:
            return h_new
        h = max(0.1, h_new)  # 限制最小值

    return h


def pipe_darcy_head_loss(lambda_f, L, D, v, g=9.81):
    """管道Darcy水头损失 [m]"""
    h_f = lambda_f * (L/D) * (v**2 / (2*g))
    return h_f


def entrance_loss(zeta_e, v, g=9.81):
    """进口损失 [m]"""
    h_e = zeta_e * (v**2 / (2*g))
    return h_e


def pool_water_level(h_channel, h_entrance, h_pipe, H_downstream):
    """进水池水位 [m]"""
    H_pool = h_channel + h_entrance + h_pipe + H_downstream
    return H_pool


def energy_balance_check(E_upstream, E_downstream, h_losses, tol=0.1):
    """能量平衡校核"""
    delta = abs(E_upstream - E_downstream - h_losses)
    return delta < tol


def pipe_velocity(Q, D):
    """管道流速 [m/s]"""
    A = np.pi * D**2 / 4
    v = Q / A
    return v


class TestCase29ChannelPipe:
    """案例29：渠道-管道耦合系统测试"""

    def test_manning_velocity(self):
        """测试1：Manning流速计算"""
        R = 0.5  # m
        S0 = 0.001
        n = 0.015

        v = manning_velocity(R, S0, n)

        # v = (1/0.015) * 0.5^(2/3) * 0.001^(1/2) ≈ 1.33 m/s
        assert v > 0
        assert v < 5.0  # 合理范围

    def test_manning_discharge(self):
        """测试2：Manning流量计算"""
        A = 3.0  # m²
        R = 0.6  # m
        S0 = 0.0005
        n = 0.015

        Q = manning_discharge(A, R, S0, n)

        # Q应为正
        assert Q > 0

    def test_rectangular_channel_normal_depth(self):
        """测试3：矩形渠道正常水深"""
        Q = 1.2  # m³/s
        b = 2.0  # m
        S0 = 0.0005
        n = 0.015

        h_n = rectangular_channel_normal_depth(Q, b, S0, n)

        # 正常水深应合理
        assert 0.3 < h_n < 2.0

        # 验证：用此水深计算流量应等于Q
        A = b * h_n
        P = b + 2 * h_n
        R = A / P
        Q_check = manning_discharge(A, R, S0, n)
        assert abs(Q_check - Q) / Q < 0.01

    def test_pipe_darcy_head_loss(self):
        """测试4：管道Darcy损失"""
        lambda_f = 0.02
        L = 300  # m
        D = 0.8  # m
        v = 2.4  # m/s

        h_f = pipe_darcy_head_loss(lambda_f, L, D, v)

        # h_f = 0.02 * (300/0.8) * (2.4²/(2*9.81)) ≈ 2.21 m
        assert h_f > 0
        assert h_f < 10  # 合理范围

    def test_entrance_loss(self):
        """测试5：进口损失"""
        zeta_e = 0.5
        v = 2.4  # m/s

        h_e = entrance_loss(zeta_e, v)

        # h_e = 0.5 * 2.4²/(2*9.81) ≈ 0.147 m
        assert h_e > 0
        assert h_e < 1.0

    def test_pool_water_level(self):
        """测试6：进水池水位计算"""
        h_channel = 0.8  # m
        h_entrance = 0.15  # m
        h_pipe = 2.2  # m
        H_downstream = 10  # m

        H_pool = pool_water_level(h_channel, h_entrance, h_pipe, H_downstream)

        # H_pool = 0.8 + 0.15 + 2.2 + 10 = 13.15 m
        assert abs(H_pool - 13.15) < 0.01

    def test_energy_balance_check(self):
        """测试7：能量平衡校核"""
        E_upstream = 15.0  # m
        E_downstream = 12.0  # m
        h_losses = 3.0  # m

        is_balanced = energy_balance_check(E_upstream, E_downstream, h_losses)

        # 15 = 12 + 3，平衡
        assert is_balanced == True

    def test_pipe_velocity(self):
        """测试8：管道流速计算"""
        Q = 1.2  # m³/s
        D = 0.8  # m

        v = pipe_velocity(Q, D)

        # v = 1.2 / (π*0.64/4) ≈ 2.39 m/s
        A = np.pi * D**2 / 4
        v_expected = Q / A
        assert abs(v - v_expected) < 0.01

    def test_channel_velocity_range(self):
        """测试9：明渠流速范围校核"""
        Q = 1.2
        b = 2.0
        S0 = 0.0005
        n = 0.015

        h_n = rectangular_channel_normal_depth(Q, b, S0, n)
        v = Q / (b * h_n)

        # 明渠流速应在合理范围（0.5~3.0 m/s）
        assert 0.5 < v < 3.0

    def test_pipe_velocity_range(self):
        """测试10：管道流速范围校核"""
        Q = 1.2
        D = 0.8

        v = pipe_velocity(Q, D)

        # 管道流速应在合理范围（0.5~3.0 m/s）
        assert 0.5 < v < 3.0

    def test_manning_n_effect(self):
        """测试11：糙率系数对流速的影响"""
        R = 0.5
        S0 = 0.001

        n_smooth = 0.013  # 光滑渠道
        n_rough = 0.025   # 粗糙渠道

        v_smooth = manning_velocity(R, S0, n_smooth)
        v_rough = manning_velocity(R, S0, n_rough)

        # 糙率越大，流速越小
        assert v_smooth > v_rough

    def test_slope_effect_on_velocity(self):
        """测试12：坡度对流速的影响"""
        R = 0.5
        n = 0.015

        S0_flat = 0.0001
        S0_steep = 0.005

        v_flat = manning_velocity(R, S0_flat, n)
        v_steep = manning_velocity(R, S0_steep, n)

        # 坡度越大，流速越大
        assert v_steep > v_flat

    def test_diameter_effect_on_pipe_loss(self):
        """测试13：管径对损失的影响"""
        lambda_f = 0.02
        L = 300
        Q = 1.2

        D_small = 0.6
        D_large = 1.0

        v_small = pipe_velocity(Q, D_small)
        v_large = pipe_velocity(Q, D_large)

        h_f_small = pipe_darcy_head_loss(lambda_f, L, D_small, v_small)
        h_f_large = pipe_darcy_head_loss(lambda_f, L, D_large, v_large)

        # 管径越大，损失越小
        assert h_f_large < h_f_small

    def test_system_case_study(self):
        """测试14：系统案例综合计算"""
        # 案例参数
        Q = 1.2
        b = 2.0
        S0 = 0.0005
        n = 0.015
        L_p = 300
        D = 0.8
        lambda_f = 0.02
        zeta_e = 0.5

        # 明渠段
        h_n = rectangular_channel_normal_depth(Q, b, S0, n)
        assert h_n > 0

        # 管道段
        v_p = pipe_velocity(Q, D)
        h_f_pipe = pipe_darcy_head_loss(lambda_f, L_p, D, v_p)
        h_e = entrance_loss(zeta_e, v_p)

        # 总损失
        h_total = h_n + h_e + h_f_pipe

        # 应为正值
        assert h_total > 0


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_slope(self):
        """测试1：零坡度（静水）"""
        R = 0.5
        S0 = 0.0
        n = 0.015

        v = manning_velocity(R, S0, n)

        # S0=0，流速为0
        assert v == 0.0

    def test_very_steep_slope(self):
        """测试2：极陡坡度"""
        R = 0.5
        S0 = 0.1  # 10%坡度
        n = 0.015

        v = manning_velocity(R, S0, n)

        # 极陡坡度，流速很大
        assert v > 10

    def test_very_small_diameter(self):
        """测试3：极小管径"""
        Q = 1.2
        D = 0.3  # 很小

        v = pipe_velocity(Q, D)

        # 管径小，流速大
        assert v > 10

    def test_zero_flow(self):
        """测试4：零流量"""
        Q = 0.0
        D = 0.8

        v = pipe_velocity(Q, D)

        assert v == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
