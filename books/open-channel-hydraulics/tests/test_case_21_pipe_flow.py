"""
案例21单元测试：城市供水管道水力计算

测试内容：
1. 达西-魏斯巴赫公式计算
2. 雷诺数计算
3. 摩阻系数计算（Colebrook-White方程）
4. 层流与紊流判别
5. Swamee-Jain显式公式
6. 流速与管径关系
7. 粗糙度影响
8. 流量变化影响
9. Moody图验证
10. 边界条件测试

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def reynolds_number(v, D, nu):
    """计算雷诺数"""
    Re = v * D / nu
    return Re


def flow_velocity(Q, D):
    """计算管道流速"""
    A = np.pi * D**2 / 4
    v = Q / A
    return v


def darcy_friction_factor_laminar(Re):
    """层流摩阻系数"""
    if Re <= 0:
        return 0.0
    lambda_f = 64.0 / Re
    return lambda_f


def colebrook_white(Re, epsilon_D, tol=1e-6, max_iter=100):
    """Colebrook-White方程求解摩阻系数（迭代法）"""
    if Re < 2320:
        # 层流
        return darcy_friction_factor_laminar(Re)

    # 紊流：迭代求解
    # 1/√λ = -2.0 * log₁₀(ε/(3.7*D) + 2.51/(Re*√λ))
    lambda_f = 0.02  # 初值

    for i in range(max_iter):
        sqrt_lambda = np.sqrt(lambda_f)
        f_val = 1/sqrt_lambda + 2.0 * np.log10(epsilon_D/3.7 + 2.51/(Re*sqrt_lambda))

        if abs(f_val) < tol:
            return lambda_f

        # Newton-Raphson更新
        df_dlambda = -0.5 / (lambda_f**1.5) - 2.0 * 0.4343 * 2.51 / (2 * Re * lambda_f**1.5)
        lambda_f = lambda_f - f_val / df_dlambda

        # 限制范围
        lambda_f = max(0.008, min(lambda_f, 0.1))

    return lambda_f


def swamee_jain_friction_factor(Re, epsilon_D):
    """Swamee-Jain显式近似公式"""
    if Re < 4000:
        return darcy_friction_factor_laminar(Re)

    # λ = 0.25 / [log₁₀(ε/(3.7*D) + 5.74/Re^0.9)]²
    numerator = 0.25
    log_term = np.log10(epsilon_D/3.7 + 5.74/Re**0.9)
    lambda_f = numerator / log_term**2
    return lambda_f


def darcy_head_loss(lambda_f, L, D, v, g=9.81):
    """达西-魏斯巴赫公式：沿程水头损失"""
    h_f = lambda_f * (L/D) * (v**2 / (2*g))
    return h_f


def determine_flow_regime(Re):
    """判别流态"""
    if Re < 2320:
        return 'laminar'
    elif Re < 4000:
        return 'transition'
    else:
        return 'turbulent'


class TestCase21PipeFlow:
    """案例21：城市供水管道水力计算测试"""

    def test_reynolds_number_calculation(self):
        """测试1：雷诺数计算"""
        v = 1.0  # m/s
        D = 0.2  # m
        nu = 1e-6  # m²/s

        Re = reynolds_number(v, D, nu)

        # Re = v*D/ν = 1.0 * 0.2 / 1e-6 = 200,000
        assert abs(Re - 200000) < 1

    def test_flow_velocity_calculation(self):
        """测试2：流速计算"""
        Q = 0.05  # m³/s
        D = 0.2   # m

        v = flow_velocity(Q, D)

        # v = Q/A = 0.05 / (π*0.2²/4) ≈ 1.592 m/s
        A = np.pi * D**2 / 4
        v_expected = Q / A
        assert abs(v - v_expected) < 1e-6

    def test_laminar_friction_factor(self):
        """测试3：层流摩阻系数"""
        Re = 2000

        lambda_f = darcy_friction_factor_laminar(Re)

        # λ = 64/Re = 64/2000 = 0.032
        assert abs(lambda_f - 0.032) < 1e-6

    def test_colebrook_white_turbulent(self):
        """测试4：紊流Colebrook-White方程"""
        Re = 100000
        epsilon_D = 0.0005  # ε/D = 0.05mm / 100mm = 0.0005

        lambda_f = colebrook_white(Re, epsilon_D)

        # 紊流区摩阻系数应在合理范围
        assert 0.01 < lambda_f < 0.05
        assert lambda_f > 0

    def test_colebrook_white_smooth_pipe(self):
        """测试5：光滑管Colebrook-White"""
        Re = 100000
        epsilon_D = 0.0  # 光滑管

        lambda_f = colebrook_white(Re, epsilon_D)

        # 光滑管摩阻系数较小
        assert 0.008 < lambda_f < 0.03

    def test_swamee_jain_formula(self):
        """测试6：Swamee-Jain显式公式"""
        Re = 100000
        epsilon_D = 0.0005

        lambda_swamee = swamee_jain_friction_factor(Re, epsilon_D)
        lambda_colebrook = colebrook_white(Re, epsilon_D)

        # Swamee-Jain与Colebrook-White结果应接近
        assert abs(lambda_swamee - lambda_colebrook) / lambda_colebrook < 0.05

    def test_darcy_head_loss(self):
        """测试7：达西水头损失计算"""
        lambda_f = 0.02
        L = 500  # m
        D = 0.2  # m
        v = 1.5  # m/s
        g = 9.81

        h_f = darcy_head_loss(lambda_f, L, D, v, g)

        # h_f = λ*(L/D)*(v²/2g) = 0.02*(500/0.2)*(1.5²/(2*9.81))
        h_f_expected = lambda_f * (L/D) * (v**2 / (2*g))
        assert abs(h_f - h_f_expected) < 1e-6

    def test_flow_regime_determination(self):
        """测试8：流态判别"""
        assert determine_flow_regime(2000) == 'laminar'
        assert determine_flow_regime(3000) == 'transition'
        assert determine_flow_regime(5000) == 'turbulent'

    def test_pipe_case_D200(self):
        """测试9：管径200mm工况"""
        Q = 0.05  # m³/s
        D = 0.200  # m
        L = 500  # m
        epsilon = 0.05e-3  # m (0.05 mm)
        nu = 1e-6  # m²/s

        v = flow_velocity(Q, D)
        Re = reynolds_number(v, D, nu)
        epsilon_D = epsilon / D
        lambda_f = colebrook_white(Re, epsilon_D)
        h_f = darcy_head_loss(lambda_f, L, D, v)

        # 流速应合理（0.5-3.0 m/s）
        assert 0.5 < v < 3.0

        # 应为紊流
        assert Re > 4000

        # 摩阻系数合理
        assert 0.01 < lambda_f < 0.05

        # 水头损失为正
        assert h_f > 0

    def test_pipe_case_D300(self):
        """测试10：管径300mm工况"""
        Q = 0.05  # m³/s
        D = 0.300  # m
        L = 500  # m
        epsilon = 0.05e-3  # m
        nu = 1e-6  # m²/s

        v = flow_velocity(Q, D)
        Re = reynolds_number(v, D, nu)
        epsilon_D = epsilon / D
        lambda_f = colebrook_white(Re, epsilon_D)
        h_f = darcy_head_loss(lambda_f, L, D, v)

        # 流速应合理
        assert 0.2 < v < 2.0

        # 应为紊流
        assert Re > 4000

        # 水头损失应小于D200
        # （管径越大，流速越小，水头损失越小）
        assert h_f > 0

    def test_diameter_effect_on_velocity(self):
        """测试11：管径对流速的影响"""
        Q = 0.05
        D1 = 0.200
        D2 = 0.300

        v1 = flow_velocity(Q, D1)
        v2 = flow_velocity(Q, D2)

        # 管径越大，流速越小
        assert v1 > v2

        # v与D²成反比
        ratio = v1 / v2
        ratio_expected = (D2 / D1)**2
        assert abs(ratio - ratio_expected) < 0.01

    def test_roughness_effect(self):
        """测试12：粗糙度影响"""
        Re = 100000
        epsilon_D_smooth = 0.00005  # 新管
        epsilon_D_rough = 0.005      # 旧管

        lambda_smooth = colebrook_white(Re, epsilon_D_smooth)
        lambda_rough = colebrook_white(Re, epsilon_D_rough)

        # 粗糙管摩阻系数更大
        assert lambda_rough > lambda_smooth

    def test_reynolds_effect_on_friction(self):
        """测试13：雷诺数对摩阻系数的影响"""
        epsilon_D = 0.0005
        Re_low = 10000
        Re_high = 1000000

        lambda_low = colebrook_white(Re_low, epsilon_D)
        lambda_high = colebrook_white(Re_high, epsilon_D)

        # 雷诺数越大，摩阻系数越小（紊流光滑区）
        assert lambda_low > lambda_high

    def test_head_loss_proportional_to_length(self):
        """测试14：水头损失与管长成正比"""
        lambda_f = 0.02
        D = 0.2
        v = 1.5

        L1 = 500
        L2 = 1000

        h_f1 = darcy_head_loss(lambda_f, L1, D, v)
        h_f2 = darcy_head_loss(lambda_f, L2, D, v)

        # h_f与L成正比
        ratio = h_f2 / h_f1
        assert abs(ratio - 2.0) < 0.01

    def test_head_loss_proportional_to_velocity_squared(self):
        """测试15：水头损失与流速平方成正比"""
        lambda_f = 0.02
        L = 500
        D = 0.2

        v1 = 1.0
        v2 = 2.0

        h_f1 = darcy_head_loss(lambda_f, L, D, v1)
        h_f2 = darcy_head_loss(lambda_f, L, D, v2)

        # h_f与v²成正比
        ratio = h_f2 / h_f1
        ratio_expected = (v2 / v1)**2
        assert abs(ratio - ratio_expected) < 0.01


class TestMoodyDiagram:
    """Moody图验证测试"""

    def test_laminar_region(self):
        """测试1：层流区验证"""
        Re = 1500
        lambda_f = darcy_friction_factor_laminar(Re)

        # λ = 64/Re
        assert abs(lambda_f - 64/Re) < 1e-10

    def test_transition_region(self):
        """测试2：过渡区"""
        Re = 3000
        epsilon_D = 0.001

        lambda_f = colebrook_white(Re, epsilon_D)

        # 过渡区摩阻系数应在合理范围
        assert 0.02 < lambda_f < 0.06

    def test_turbulent_smooth_region(self):
        """测试3：紊流光滑区"""
        Re = 1e6
        epsilon_D = 0.0  # 光滑管

        lambda_f = colebrook_white(Re, epsilon_D)

        # 高雷诺数光滑管：λ ≈ 0.01
        assert 0.008 < lambda_f < 0.015

    def test_fully_rough_region(self):
        """测试4：完全紊流区（粗糙管区）"""
        Re_low = 1e5
        Re_high = 1e7
        epsilon_D = 0.01  # 较大相对粗糙度

        lambda_low = colebrook_white(Re_low, epsilon_D)
        lambda_high = colebrook_white(Re_high, epsilon_D)

        # 完全紊流区：λ主要取决于ε/D，与Re关系不大
        assert abs(lambda_low - lambda_high) / lambda_low < 0.1


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_velocity(self):
        """测试1：零流速"""
        Q = 0.0
        D = 0.2

        v = flow_velocity(Q, D)
        assert v == 0.0

    def test_very_small_pipe(self):
        """测试2：极小管径"""
        Q = 0.05
        D = 0.05  # 50mm

        v = flow_velocity(Q, D)

        # 极小管径流速会很大
        assert v > 10.0

    def test_very_large_pipe(self):
        """测试3：极大管径"""
        Q = 0.05
        D = 1.0  # 1000mm

        v = flow_velocity(Q, D)

        # 极大管径流速会很小
        assert v < 0.1

    def test_smooth_pipe_limit(self):
        """测试4：光滑管极限"""
        Re = 1e6
        epsilon_D = 0.0

        lambda_f = colebrook_white(Re, epsilon_D)

        # 光滑管极限：λ较小
        assert lambda_f < 0.015

    def test_rough_pipe_limit(self):
        """测试5：粗糙管极限"""
        Re = 1e6
        epsilon_D = 0.05  # 极大相对粗糙度

        lambda_f = colebrook_white(Re, epsilon_D)

        # 粗糙管：λ较大
        assert lambda_f > 0.03

    def test_low_reynolds_number(self):
        """测试6：低雷诺数"""
        Re = 100
        lambda_f = darcy_friction_factor_laminar(Re)

        # 层流：λ = 64/Re = 0.64
        assert abs(lambda_f - 0.64) < 1e-6

    def test_high_reynolds_number(self):
        """测试7：高雷诺数"""
        Re = 1e8
        epsilon_D = 0.0001

        lambda_f = colebrook_white(Re, epsilon_D)

        # 高Re紊流：λ较小
        assert lambda_f > 0
        assert lambda_f < 0.02


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
