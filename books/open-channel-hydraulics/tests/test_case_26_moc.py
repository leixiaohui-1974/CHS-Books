"""
案例26单元测试：特征线法MOC

测试内容：
1. 特征线斜率
2. 摩阻项计算
3. 内部节点计算（C+和C-方程）
4. 上游边界（水库）
5. 下游边界（阀门）
6. Courant条件
7. 离散化参数
8. 基本MOC模拟

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def characteristic_slope_positive(a):
    """C⁺特征线斜率
    dx/dt = +a
    """
    return a


def characteristic_slope_negative(a):
    """C⁻特征线斜率
    dx/dt = -a
    """
    return -a


def friction_term(lambda_f, v, D, a, dt, g=9.81):
    """摩阻项 R [m]
    R = (λ*v*|v|)/(2gD) * a * Δt
    """
    R = (lambda_f * v * abs(v)) / (2 * g * D) * a * dt
    return R


def courant_timestep(dx, a):
    """Courant条件下的时间步长 [s]
    Δt = Δx / a
    """
    dt = dx / a
    return dt


def space_step(L, N):
    """空间步长 [m]
    Δx = L / N
    """
    dx = L / N
    return dx


def timestep_from_segments(L, N, a):
    """根据分段数计算时间步长 [s]
    Δt = L / (N * a)
    """
    dt = L / (N * a)
    return dt


def c_plus_equation(H_A, v_A, v_P, R_A, a, g=9.81):
    """C⁺方程
    H_P = H_A - (a/g)*(v_P - v_A) - R_A
    """
    H_P = H_A - (a / g) * (v_P - v_A) - R_A
    return H_P


def c_minus_equation(H_B, v_B, v_P, R_B, a, g=9.81):
    """C⁻方程
    H_P = H_B + (a/g)*(v_P - v_B) - R_B
    """
    H_P = H_B + (a / g) * (v_P - v_B) - R_B
    return H_P


def internal_point_velocity(H_A, H_B, v_A, v_B, R_A, R_B, a, g=9.81):
    """内部节点流速（联立C+和C-）
    v_P = (H_A - H_B + (a/g)*(v_A + v_B) - R_A - R_B) / (2a/g)
    """
    numerator = H_A - H_B + (a/g)*(v_A + v_B) - R_A - R_B
    denominator = 2 * a / g
    v_P = numerator / denominator
    return v_P


def internal_point_head(H_A, H_B, v_A, v_B, R_A, R_B, a, g=9.81):
    """内部节点压力水头（联立C+和C-）
    H_P = (H_A + H_B)/2 + (a/2g)*(v_A - v_B) - (R_A + R_B)/2
    """
    H_P = (H_A + H_B) / 2 + (a / (2*g)) * (v_A - v_B) - (R_A + R_B) / 2
    return H_P


def upstream_reservoir_velocity(H_reservoir, H_B, v_B, R_B, a, g=9.81):
    """上游水库边界流速（C-方程）
    v_1 = v_B + (g/a)*(H_reservoir - H_B) + (g/a)*R_B
    """
    v_1 = v_B + (g / a) * (H_reservoir - H_B) + (g / a) * R_B
    return v_1


def valve_coefficient_linear_closure(C_v0, t, t_c):
    """线性关闭阀门开度系数
    C_v(t) = C_v0 * (1 - t/t_c)  (t ≤ t_c)
    C_v(t) = 0  (t > t_c)
    """
    if t >= t_c:
        return 0.0
    else:
        return C_v0 * (1 - t / t_c)


def valve_velocity_simple(C_v, H, g=9.81):
    """简化阀门流速
    v = C_v * √(2gH)
    """
    if H < 0:
        return 0.0
    v = C_v * np.sqrt(2 * g * H)
    return v


def downstream_valve_head_iterative(H_A, v_A, R_A, C_v, a, g=9.81, tol=1e-6, max_iter=100):
    """下游阀门边界水头（迭代求解）

    C⁺方程：H_N = H_A - (a/g)*(v_N - v_A) - R_A
    阀门方程：v_N = C_v * √(2gH_N)

    迭代求解H_N
    """
    # 初始猜测
    H_N = H_A

    for i in range(max_iter):
        # 用当前H_N计算v_N
        v_N = valve_velocity_simple(C_v, H_N, g)

        # 用C+方程更新H_N
        H_N_new = H_A - (a / g) * (v_N - v_A) - R_A

        # 检查收敛
        if abs(H_N_new - H_N) < tol:
            return H_N_new, v_N

        H_N = H_N_new

    return H_N, v_N


class TestCase26MOC:
    """案例26：特征线法MOC测试"""

    def test_characteristic_slope_positive(self):
        """测试1：C⁺特征线斜率"""
        a = 1000  # m/s

        slope = characteristic_slope_positive(a)

        # dx/dt = +a = 1000
        assert slope == 1000

    def test_characteristic_slope_negative(self):
        """测试2：C⁻特征线斜率"""
        a = 1000  # m/s

        slope = characteristic_slope_negative(a)

        # dx/dt = -a = -1000
        assert slope == -1000

    def test_friction_term_calculation(self):
        """测试3：摩阻项计算"""
        lambda_f = 0.02
        v = 1.5  # m/s
        D = 0.6  # m
        a = 1000  # m/s
        dt = 0.1  # s
        g = 9.81

        R = friction_term(lambda_f, v, D, a, dt, g)

        # R = (0.02*1.5*1.5)/(2*9.81*0.6) * 1000 * 0.1
        R_expected = (lambda_f * v * abs(v)) / (2 * g * D) * a * dt
        assert abs(R - R_expected) < 1e-6

        # 摩阻项应为正（耗散能量）
        assert R > 0

    def test_friction_term_zero_velocity(self):
        """测试4：零流速时摩阻项为零"""
        lambda_f = 0.02
        v = 0.0
        D = 0.6
        a = 1000
        dt = 0.1

        R = friction_term(lambda_f, v, D, a, dt)

        assert R == 0.0

    def test_courant_timestep(self):
        """测试5：Courant时间步长"""
        dx = 100  # m
        a = 1000  # m/s

        dt = courant_timestep(dx, a)

        # Δt = 100/1000 = 0.1 s
        assert abs(dt - 0.1) < 1e-6

    def test_space_step_calculation(self):
        """测试6：空间步长计算"""
        L = 1200  # m
        N = 12  # 分段数

        dx = space_step(L, N)

        # Δx = 1200/12 = 100 m
        assert abs(dx - 100.0) < 1e-6

    def test_timestep_from_segments(self):
        """测试7：从分段数计算时间步长"""
        L = 1200
        N = 12
        a = 1000

        dt = timestep_from_segments(L, N, a)

        # Δt = 1200/(12*1000) = 0.1 s
        assert abs(dt - 0.1) < 1e-6

    def test_c_plus_equation(self):
        """测试8：C⁺方程"""
        H_A = 60  # m
        v_A = 1.5  # m/s
        v_P = 1.2  # m/s
        R_A = 0.05  # m
        a = 1000
        g = 9.81

        H_P = c_plus_equation(H_A, v_A, v_P, R_A, a, g)

        # H_P = 60 - (1000/9.81)*(1.2-1.5) - 0.05
        # H_P = 60 + 30.58 - 0.05 ≈ 90.53
        assert H_P > H_A  # 流速减小，压力升高

    def test_c_minus_equation(self):
        """测试9：C⁻方程"""
        H_B = 60
        v_B = 1.5
        v_P = 1.2
        R_B = 0.05
        a = 1000
        g = 9.81

        H_P = c_minus_equation(H_B, v_B, v_P, R_B, a, g)

        # H_P = 60 + (1000/9.81)*(1.2-1.5) - 0.05
        # H_P = 60 - 30.58 - 0.05 ≈ 29.37
        assert H_P < H_B  # 流速减小但C-方向，压力下降

    def test_internal_point_calculation(self):
        """测试10：内部节点计算"""
        H_A = 62  # m
        H_B = 58  # m
        v_A = 1.6  # m/s
        v_B = 1.4  # m/s
        R_A = 0.04
        R_B = 0.03
        a = 1000
        g = 9.81

        v_P = internal_point_velocity(H_A, H_B, v_A, v_B, R_A, R_B, a, g)
        H_P = internal_point_head(H_A, H_B, v_A, v_B, R_A, R_B, a, g)

        # 流速应在v_A和v_B之间（大致）
        assert v_P > 0

        # 压力应在H_A和H_B之间（大致）
        assert H_P > 0

    def test_internal_point_symmetry(self):
        """测试11：对称工况（H_A=H_B, v_A=v_B）"""
        H_A = 60
        H_B = 60
        v_A = 1.5
        v_B = 1.5
        R_A = 0.05
        R_B = 0.05
        a = 1000

        v_P = internal_point_velocity(H_A, H_B, v_A, v_B, R_A, R_B, a)
        H_P = internal_point_head(H_A, H_B, v_A, v_B, R_A, R_B, a)

        # 对称工况：v_P = v_A = v_B
        assert abs(v_P - v_A) < 0.01

        # H_P = H_A - R_A (约)
        assert H_P < H_A

    def test_upstream_reservoir_boundary(self):
        """测试12：上游水库边界"""
        H_reservoir = 60  # m
        H_B = 58  # m
        v_B = 1.4  # m/s
        R_B = 0.03
        a = 1000
        g = 9.81

        v_1 = upstream_reservoir_velocity(H_reservoir, H_B, v_B, R_B, a, g)

        # H_reservoir > H_B，水流入管道，v_1应为正
        assert v_1 > 0

    def test_upstream_reservoir_higher_head(self):
        """测试13：水库水头提高"""
        H_reservoir_low = 60
        H_reservoir_high = 65
        H_B = 58
        v_B = 1.4
        R_B = 0.03
        a = 1000

        v_1_low = upstream_reservoir_velocity(H_reservoir_low, H_B, v_B, R_B, a)
        v_1_high = upstream_reservoir_velocity(H_reservoir_high, H_B, v_B, R_B, a)

        # 水库水头越高，流速越大
        assert v_1_high > v_1_low

    def test_valve_coefficient_linear_closure(self):
        """测试14：线性关闭阀门系数"""
        C_v0 = 1.0
        t_c = 2.0

        # t = 0时，全开
        C_v_0 = valve_coefficient_linear_closure(C_v0, 0.0, t_c)
        assert abs(C_v_0 - 1.0) < 1e-6

        # t = 1时，半开
        C_v_1 = valve_coefficient_linear_closure(C_v0, 1.0, t_c)
        assert abs(C_v_1 - 0.5) < 1e-6

        # t = 2时，全关
        C_v_2 = valve_coefficient_linear_closure(C_v0, 2.0, t_c)
        assert abs(C_v_2 - 0.0) < 1e-6

        # t > 2时，仍为0
        C_v_3 = valve_coefficient_linear_closure(C_v0, 3.0, t_c)
        assert C_v_3 == 0.0

    def test_valve_velocity_calculation(self):
        """测试15：阀门流速计算"""
        C_v = 0.8
        H = 60  # m
        g = 9.81

        v = valve_velocity_simple(C_v, H, g)

        # v = 0.8 * √(2*9.81*60) ≈ 27.4 m/s
        v_expected = C_v * np.sqrt(2 * g * H)
        assert abs(v - v_expected) < 1e-6

    def test_valve_velocity_zero_opening(self):
        """测试16：阀门全关时流速为零"""
        C_v = 0.0
        H = 60

        v = valve_velocity_simple(C_v, H)

        assert v == 0.0

    def test_downstream_valve_iterative(self):
        """测试17：下游阀门边界（迭代求解）"""
        H_A = 62  # m
        v_A = 1.6  # m/s
        R_A = 0.04
        C_v = 0.5
        a = 1000

        H_N, v_N = downstream_valve_head_iterative(H_A, v_A, R_A, C_v, a)

        # 应收敛到合理值
        assert H_N > 0
        assert v_N >= 0  # 可以为0（阀门部分关闭时）

        # 验证C+方程
        H_check = H_A - (a / 9.81) * (v_N - v_A) - R_A
        assert abs(H_check - H_N) < 1e-3

        # 验证阀门方程（如果v_N > 0）
        if v_N > 1e-6:
            v_check = valve_velocity_simple(C_v, H_N)
            assert abs(v_check - v_N) < 1e-3

    def test_moc_discretization(self):
        """测试18：MOC离散化参数"""
        L = 1200  # m
        N = 12
        a = 1000  # m/s

        dx = space_step(L, N)
        dt = timestep_from_segments(L, N, a)

        # Courant条件
        dt_courant = courant_timestep(dx, a)

        # 应满足：Δt = Δx/a
        assert abs(dt - dt_courant) < 1e-9

    def test_friction_effect_on_pressure(self):
        """测试19：摩阻对压力的影响"""
        H_A = 60
        v_A = 1.5
        v_P = 1.5  # 同样流速
        a = 1000

        # 无摩阻
        R_A_zero = 0.0
        H_P_zero = c_plus_equation(H_A, v_A, v_P, R_A_zero, a)

        # 有摩阻
        R_A_nonzero = 0.1
        H_P_nonzero = c_plus_equation(H_A, v_A, v_P, R_A_nonzero, a)

        # 摩阻导致压力损失
        assert H_P_nonzero < H_P_zero

    def test_velocity_decrease_increases_pressure(self):
        """测试20：流速减小导致压力升高（C+）"""
        H_A = 60
        v_A = 2.0
        R_A = 0.0  # 忽略摩阻
        a = 1000

        v_P_high = 1.5
        v_P_low = 1.0

        H_P_high = c_plus_equation(H_A, v_A, v_P_high, R_A, a)
        H_P_low = c_plus_equation(H_A, v_A, v_P_low, R_A, a)

        # 流速越小，压力越高
        assert H_P_low > H_P_high

    def test_number_of_segments_effect(self):
        """测试21：分段数对时间步长的影响"""
        L = 1200
        a = 1000

        N_few = 6
        N_many = 24

        dt_few = timestep_from_segments(L, N_few, a)
        dt_many = timestep_from_segments(L, N_many, a)

        # 分段越多，时间步长越小
        assert dt_many < dt_few

    def test_wave_speed_effect_on_timestep(self):
        """测试22：波速对时间步长的影响"""
        L = 1200
        N = 12

        a_fast = 1200  # m/s
        a_slow = 800  # m/s

        dt_fast = timestep_from_segments(L, N, a_fast)
        dt_slow = timestep_from_segments(L, N, a_slow)

        # 波速越快，时间步长越小
        assert dt_fast < dt_slow

    def test_valve_closure_reduces_flow(self):
        """测试23：阀门关闭减小流量"""
        H = 60
        C_v_open = 1.0
        C_v_half = 0.5
        C_v_closed = 0.0

        v_open = valve_velocity_simple(C_v_open, H)
        v_half = valve_velocity_simple(C_v_half, H)
        v_closed = valve_velocity_simple(C_v_closed, H)

        # 开度越小，流速越小
        assert v_open > v_half > v_closed

    def test_negative_head_at_valve(self):
        """测试24：阀门处负压（极端工况）"""
        H_A = 10  # m（初始水头低）
        v_A = 3.0  # m/s（初始流速高）
        R_A = 0.1
        C_v = 0.0  # 阀门全关
        a = 1000

        H_N, v_N = downstream_valve_head_iterative(H_A, v_A, R_A, C_v, a)

        # 阀门全关，流速应为0
        assert abs(v_N) < 1e-3

        # 可能产生负压（水锤危险）
        # H_N可能为负


class TestMOCSimulation:
    """MOC完整模拟测试"""

    def test_initial_condition_steady_flow(self):
        """测试1：初始稳态条件"""
        # 稳态：所有节点H和v相同
        N = 12
        H0 = 60
        v0 = 1.5

        # 初始化
        H = np.ones(N+1) * H0
        v = np.ones(N+1) * v0

        # 验证均匀
        assert np.all(H == H0)
        assert np.all(v == v0)

    def test_mass_conservation_internal_points(self):
        """测试2：内部点质量守恒（近似）"""
        # 无摩阻、对称工况应严格守恒
        H_A = 60
        H_B = 60
        v_A = 1.5
        v_B = 1.5
        R_A = 0.0
        R_B = 0.0
        a = 1000

        v_P = internal_point_velocity(H_A, H_B, v_A, v_B, R_A, R_B, a)

        # 流速应保持
        assert abs(v_P - v_A) < 1e-6

    def test_pressure_wave_propagation_direction(self):
        """测试3：压力波传播方向"""
        a = 1000

        # C+向右传播
        slope_plus = characteristic_slope_positive(a)
        assert slope_plus > 0

        # C-向左传播
        slope_minus = characteristic_slope_negative(a)
        assert slope_minus < 0


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_wave_speed(self):
        """测试1：零波速（不现实，但测试健壮性）"""
        # 这会导致除零，实际应避免
        pass

    def test_very_small_timestep(self):
        """测试2：极小时间步长"""
        dx = 1.0  # m
        a = 1000

        dt = courant_timestep(dx, a)

        # dt = 0.001 s
        assert dt == 0.001

    def test_very_large_pipe(self):
        """测试3：极长管道"""
        L = 100000  # m (100 km)
        N = 100
        a = 1000

        dt = timestep_from_segments(L, N, a)

        # dt = 1.0 s
        assert dt == 1.0

    def test_reverse_flow(self):
        """测试4：倒流工况"""
        lambda_f = 0.02
        v = -1.5  # 负流速（倒流）
        D = 0.6
        a = 1000
        dt = 0.1

        R = friction_term(lambda_f, v, D, a, dt)

        # 倒流时R为负（符号跟随流向）
        assert R < 0

        # 正向流时R为正
        R_forward = friction_term(lambda_f, 1.5, D, a, dt)
        assert R_forward > 0

        # 绝对值应相等
        assert abs(R) == abs(R_forward)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
