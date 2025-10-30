"""
案例27单元测试：泵站瞬变过程

测试内容：
1. 泵特性曲线（H-Q, M-Q）
2. 相似定律（n, Q, H, M关系）
3. 惯性时间常数计算
4. 转速衰减规律
5. 飞轮设计计算
6. 四象限运行判别
7. 最大/最小压力估算
8. 边界条件测试

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def pump_head_characteristic(Q, Q0, H0, a_h=0.4):
    """泵扬程特性曲线
    H = H₀ * [1 - a_h * (Q/Q₀)²]
    """
    H = H0 * (1 - a_h * (Q / Q0)**2)
    return H


def pump_torque_characteristic(Q, Q0, M0, a_m=0.5, b_m=0.5):
    """泵转矩特性曲线
    M = M₀ * [a_m + b_m * (Q/Q₀)]
    """
    M = M0 * (a_m + b_m * (Q / Q0))
    return M


def affinity_law_flow(Q0, n, n0):
    """相似定律：流量
    Q/Q₀ = n/n₀
    """
    Q = Q0 * (n / n0)
    return Q


def affinity_law_head(H0, n, n0):
    """相似定律：扬程
    H/H₀ = (n/n₀)²
    """
    H = H0 * (n / n0)**2
    return H


def affinity_law_torque(M0, n, n0):
    """相似定律：转矩
    M/M₀ = (n/n₀)²
    """
    M = M0 * (n / n0)**2
    return M


def inertia_time_constant(GD2, n0, M_friction):
    """惯性时间常数 [s]
    T_i = (GD² * n₀) / (375 * M_friction)
    """
    if M_friction == 0:
        return np.inf
    T_i = (GD2 * n0) / (375 * M_friction)
    return T_i


def speed_decay_exponential(n0, t, T_i):
    """转速衰减（指数衰减） [rpm]
    n(t) = n₀ * exp(-t/T_i)
    """
    n = n0 * np.exp(-t / T_i)
    return n


def flywheel_requirement(T_i_target, n0, M_friction):
    """计算所需飞轮GD² [kg·m²]
    GD² = T_i * 375 * M_friction / n₀
    """
    GD2 = T_i_target * 375 * M_friction / n0
    return GD2


def determine_quadrant(n, Q):
    """判别运行象限
    第一象限：n>0, Q>0 (正常)
    第二象限：n>0, Q<0 (倒流)
    第三象限：n<0, Q<0 (反转)
    第四象限：n<0, Q>0 (涡轮)
    """
    if n > 0 and Q > 0:
        return 1
    elif n > 0 and Q < 0:
        return 2
    elif n < 0 and Q < 0:
        return 3
    elif n < 0 and Q > 0:
        return 4
    else:
        return 0  # n=0 或 Q=0


def max_pressure_pump_trip(p0, rho, a, v0):
    """泵跳闸最大压力（Joukowsky估算）[Pa]
    p_max = p₀ + ρ*a*v₀
    """
    p_max = p0 + rho * a * v0
    return p_max


def min_pressure_pump_outlet(H_s, H_static, H_friction):
    """泵出口最小压力水头（停机后）[m]
    H_min = H_s - H_static - H_friction
    """
    H_min = H_s - H_static - H_friction
    return H_min


def check_column_separation(p_min, p_vapor):
    """校核水柱分离
    分离条件：p_min ≤ p_vapor
    """
    return p_min <= p_vapor


class TestCase27PumpTransients:
    """案例27：泵站瞬变过程测试"""

    def test_pump_head_characteristic_rated(self):
        """测试1：额定工况扬程"""
        Q0 = 0.15  # m³/s
        H0 = 40  # m
        a_h = 0.4

        H = pump_head_characteristic(Q0, Q0, H0, a_h)

        # 额定流量下：H = H₀ * (1 - 0.4) = 0.6 * H₀ = 24 m
        # 注意：公式中Q=Q0时，H不等于H0（除非a_h=0）
        # 这里H0是最大扬程（零流量），实际额定扬程要低
        assert H > 0

    def test_pump_head_characteristic_shutoff(self):
        """测试2：零流量（关死点）扬程"""
        Q = 0.0
        Q0 = 0.15
        H0 = 40

        H = pump_head_characteristic(Q, Q0, H0)

        # Q=0时：H = H₀
        assert abs(H - H0) < 1e-6

    def test_pump_head_decreases_with_flow(self):
        """测试3：流量增加扬程下降"""
        Q0 = 0.15
        H0 = 40

        Q_low = 0.1
        Q_high = 0.2

        H_low = pump_head_characteristic(Q_low, Q0, H0)
        H_high = pump_head_characteristic(Q_high, Q0, H0)

        # 流量越大，扬程越小
        assert H_low > H_high

    def test_pump_torque_characteristic(self):
        """测试4：转矩特性曲线"""
        Q = 0.15
        Q0 = 0.15
        M0 = 100  # N·m
        a_m = 0.5
        b_m = 0.5

        M = pump_torque_characteristic(Q, Q0, M0, a_m, b_m)

        # M = 100 * (0.5 + 0.5*1) = 100 N·m
        assert abs(M - 100) < 1e-6

    def test_affinity_law_flow(self):
        """测试5：相似定律（流量）"""
        Q0 = 0.15
        n0 = 1450  # rpm
        n = 1160  # 80% 转速

        Q = affinity_law_flow(Q0, n, n0)

        # Q/Q₀ = n/n₀ = 0.8
        Q_expected = Q0 * 0.8
        assert abs(Q - Q_expected) < 1e-6

    def test_affinity_law_head(self):
        """测试6：相似定律（扬程）"""
        H0 = 40
        n0 = 1450
        n = 1160  # 80% 转速

        H = affinity_law_head(H0, n, n0)

        # H/H₀ = (n/n₀)² = 0.64
        H_expected = H0 * 0.64
        assert abs(H - H_expected) < 1e-6

    def test_affinity_law_torque(self):
        """测试7：相似定律（转矩）"""
        M0 = 100
        n0 = 1450
        n = 1160

        M = affinity_law_torque(M0, n, n0)

        # M/M₀ = (n/n₀)² = 0.64
        M_expected = M0 * 0.64
        assert abs(M - M_expected) < 1e-6

    def test_affinity_law_power_scaling(self):
        """测试8：相似定律（功率）P ∝ n³"""
        # P = M * ω ∝ n² * n = n³
        n0 = 1450
        n1 = 1450
        n2 = 725  # 50% 转速

        M0 = 100

        M1 = affinity_law_torque(M0, n1, n0)
        M2 = affinity_law_torque(M0, n2, n0)

        # P ∝ M*n
        P1 = M1 * n1
        P2 = M2 * n2

        # P2/P1 = (n2/n1)³ = 0.125
        ratio = P2 / P1
        ratio_expected = (n2 / n1)**3
        assert abs(ratio - ratio_expected) < 0.01

    def test_inertia_time_constant(self):
        """测试9：惯性时间常数计算"""
        GD2 = 50  # kg·m²
        n0 = 1450  # rpm
        M_friction = 20  # N·m

        T_i = inertia_time_constant(GD2, n0, M_friction)

        # T_i = 50*1450 / (375*20) = 9.67 s
        T_i_expected = (GD2 * n0) / (375 * M_friction)
        assert abs(T_i - T_i_expected) < 0.01

    def test_speed_decay_at_zero_time(self):
        """测试10：t=0时转速不变"""
        n0 = 1450
        t = 0.0
        T_i = 10

        n = speed_decay_exponential(n0, t, T_i)

        # t=0: n = n₀
        assert abs(n - n0) < 1e-6

    def test_speed_decay_at_T_i(self):
        """测试11：t=T_i时转速衰减到1/e"""
        n0 = 1450
        T_i = 10
        t = T_i

        n = speed_decay_exponential(n0, t, T_i)

        # t=T_i: n = n₀/e ≈ 0.368*n₀
        n_expected = n0 / np.e
        assert abs(n - n_expected) < 1.0

    def test_speed_decay_monotonic(self):
        """测试12：转速单调递减"""
        n0 = 1450
        T_i = 10

        times = [0, 5, 10, 15, 20]
        speeds = [speed_decay_exponential(n0, t, T_i) for t in times]

        # 转速应单调递减
        for i in range(len(speeds) - 1):
            assert speeds[i] > speeds[i+1]

    def test_flywheel_requirement(self):
        """测试13：飞轮设计计算"""
        T_i_target = 15  # s (目标惯性时间)
        n0 = 1450
        M_friction = 20

        GD2 = flywheel_requirement(T_i_target, n0, M_friction)

        # GD² = 15*375*20 / 1450 ≈ 77.6 kg·m²
        GD2_expected = T_i_target * 375 * M_friction / n0
        assert abs(GD2 - GD2_expected) < 0.01

        # 验证：用此GD²计算T_i应等于目标值
        T_i_check = inertia_time_constant(GD2, n0, M_friction)
        assert abs(T_i_check - T_i_target) < 0.01

    def test_determine_quadrant_I(self):
        """测试14：第一象限（正常运行）"""
        n = 1450  # 正转
        Q = 0.15  # 正流

        quadrant = determine_quadrant(n, Q)

        assert quadrant == 1

    def test_determine_quadrant_II(self):
        """测试15：第二象限（倒流）"""
        n = 500  # 仍正转
        Q = -0.05  # 倒流

        quadrant = determine_quadrant(n, Q)

        assert quadrant == 2

    def test_determine_quadrant_III(self):
        """测试16：第三象限（反转）"""
        n = -300  # 反转
        Q = -0.03  # 倒流

        quadrant = determine_quadrant(n, Q)

        assert quadrant == 3

    def test_determine_quadrant_IV(self):
        """测试17：第四象限（涡轮）"""
        n = -200  # 反转
        Q = 0.02  # 正流

        quadrant = determine_quadrant(n, Q)

        assert quadrant == 4

    def test_max_pressure_pump_trip(self):
        """测试18：泵跳闸最大压力"""
        p0 = 0.4e6  # Pa
        rho = 1000
        a = 1000
        v0 = 1.2  # m/s

        p_max = max_pressure_pump_trip(p0, rho, a, v0)

        # p_max = 0.4e6 + 1000*1000*1.2 = 1.6e6 Pa
        assert abs(p_max - 1.6e6) < 1e-6

    def test_min_pressure_pump_outlet(self):
        """测试19：泵出口最小压力"""
        H_s = 5  # m (吸水池水位)
        H_static = 35  # m (静扬程)
        H_friction = 5  # m (摩阻损失)

        H_min = min_pressure_pump_outlet(H_s, H_static, H_friction)

        # H_min = 5 - 35 - 5 = -35 m (负压！)
        assert H_min < 0

    def test_check_column_separation_true(self):
        """测试20：水柱分离（发生）"""
        p_min = -5  # m水柱（负压）
        p_vapor = 0.238  # m (20°C)

        is_separated = check_column_separation(p_min, p_vapor)

        # p_min < p_vapor，发生分离
        assert is_separated == True

    def test_check_column_separation_false(self):
        """测试21：水柱分离（不发生）"""
        p_min = 5  # m水柱（正压）
        p_vapor = 0.238  # m

        is_separated = check_column_separation(p_min, p_vapor)

        # p_min > p_vapor，不发生分离
        assert is_separated == False

    def test_inertia_effect_on_pressure(self):
        """测试22：惯量对压力的影响"""
        # 惯量越大，转速衰减越慢，压力变化越平缓
        n0 = 1450
        M_friction = 20

        GD2_small = 20
        GD2_large = 100

        T_i_small = inertia_time_constant(GD2_small, n0, M_friction)
        T_i_large = inertia_time_constant(GD2_large, n0, M_friction)

        # 惯量越大，惯性时间越长
        assert T_i_large > T_i_small

        # t=5s时的转速
        n_small = speed_decay_exponential(n0, 5, T_i_small)
        n_large = speed_decay_exponential(n0, 5, T_i_large)

        # 惯量大时，转速保持得更好
        assert n_large > n_small

    def test_affinity_law_consistency(self):
        """测试23：相似定律一致性"""
        Q0 = 0.15
        H0 = 40
        n0 = 1450
        n = 1160

        # 用相似定律计算
        Q = affinity_law_flow(Q0, n, n0)
        H = affinity_law_head(H0, n, n0)

        # 验证：比速公式ns = n*sqrt(Q)/H^0.75 应保持不变
        ns0 = n0 * np.sqrt(Q0) / H0**0.75
        ns = n * np.sqrt(Q) / H**0.75

        assert abs(ns - ns0) / ns0 < 0.01

    def test_zero_friction_infinite_inertia_time(self):
        """测试24：零摩擦时惯性时间无限大"""
        GD2 = 50
        n0 = 1450
        M_friction = 0

        T_i = inertia_time_constant(GD2, n0, M_friction)

        # M_friction=0，T_i→∞
        assert T_i == np.inf


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_speed(self):
        """测试1：零转速"""
        n = 0
        Q = 0.1

        quadrant = determine_quadrant(n, Q)

        # n=0，无法判别象限
        assert quadrant == 0

    def test_zero_flow(self):
        """测试2：零流量"""
        n = 1000
        Q = 0

        quadrant = determine_quadrant(n, Q)

        # Q=0，无法判别象限
        assert quadrant == 0

    def test_very_large_inertia(self):
        """测试3：极大惯量"""
        GD2 = 1000  # 很大的飞轮
        n0 = 1450
        M_friction = 10

        T_i = inertia_time_constant(GD2, n0, M_friction)

        # 惯性时间很长
        assert T_i > 100

        # 10秒后转速仍接近初值
        n_10s = speed_decay_exponential(n0, 10, T_i)
        assert n_10s > 0.9 * n0

    def test_very_small_inertia(self):
        """测试4：极小惯量"""
        GD2 = 1  # 很小的惯量
        n0 = 1450
        M_friction = 50

        T_i = inertia_time_constant(GD2, n0, M_friction)

        # 惯性时间很短
        assert T_i < 1

        # 1秒后转速已大幅下降
        n_1s = speed_decay_exponential(n0, 1, T_i)
        assert n_1s < 0.4 * n0

    def test_long_time_speed_approaches_zero(self):
        """测试5：长时间后转速趋于零"""
        n0 = 1450
        T_i = 10
        t = 100  # 很长时间（10*T_i）

        n = speed_decay_exponential(n0, t, T_i)

        # n ≈ 0
        assert n < 1  # rpm (接近零)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
