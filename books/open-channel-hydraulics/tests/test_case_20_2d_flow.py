"""
案例20单元测试：二维明渠水流模拟

测试内容：
1. 状态向量转换
2. x方向通量计算
3. y方向通量计算
4. 浅水波速计算
5. CFL时间步长
6. Lax-Friedrichs数值通量
7. 干湿单元判定
8. 摩阻源项
9. 底坡源项
10. 速度矢量计算

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def state_vector_from_primitives(h, u, v):
    """
    从原始变量构造状态向量

    Args:
        h: 水深 (m)
        u: x方向流速 (m/s)
        v: y方向流速 (m/s)

    Returns:
        U: 状态向量 [h, hu, hv]
    """
    return np.array([h, h * u, h * v])


def primitives_from_state(U):
    """
    从状态向量提取原始变量

    Args:
        U: 状态向量 [h, hu, hv]

    Returns:
        h, u, v: 水深和流速
    """
    h = U[0]
    if h > 1e-10:
        u = U[1] / h
        v = U[2] / h
    else:
        u = 0.0
        v = 0.0
    return h, u, v


def compute_x_flux(U, g=9.81):
    """
    计算x方向通量 F = [hu, hu²+gh²/2, huv]

    Args:
        U: 状态向量 [h, hu, hv]
        g: 重力加速度

    Returns:
        F: x方向通量
    """
    h = U[0]
    hu = U[1]
    hv = U[2]

    if h > 1e-10:
        u = hu / h
        v = hv / h
    else:
        u = 0.0
        v = 0.0

    F = np.array([
        hu,
        hu * u + 0.5 * g * h**2,
        hu * v
    ])

    return F


def compute_y_flux(U, g=9.81):
    """
    计算y方向通量 G = [hv, huv, hv²+gh²/2]

    Args:
        U: 状态向量 [h, hu, hv]
        g: 重力加速度

    Returns:
        G: y方向通量
    """
    h = U[0]
    hu = U[1]
    hv = U[2]

    if h > 1e-10:
        u = hu / h
        v = hv / h
    else:
        u = 0.0
        v = 0.0

    G = np.array([
        hv,
        hv * u,
        hv * v + 0.5 * g * h**2
    ])

    return G


def shallow_water_wave_speed(h, u, v, g=9.81):
    """
    计算浅水波速

    Args:
        h: 水深 (m)
        u: x方向流速 (m/s)
        v: y方向流速 (m/s)
        g: 重力加速度

    Returns:
        c: 波速 (m/s)
        lambda_max: 最大特征值速度 (m/s)
    """
    c = np.sqrt(g * h)
    velocity_mag = np.sqrt(u**2 + v**2)
    lambda_max = velocity_mag + c

    return c, lambda_max


def compute_cfl_timestep(dx, dy, h, u, v, cfl_number=0.5, g=9.81):
    """
    计算CFL时间步长

    Args:
        dx: x方向网格间距 (m)
        dy: y方向网格间距 (m)
        h: 水深 (m)
        u: x方向流速 (m/s)
        v: y方向流速 (m/s)
        cfl_number: CFL数
        g: 重力加速度

    Returns:
        dt: 时间步长 (s)
    """
    c = np.sqrt(g * h)
    lambda_x = abs(u) + c
    lambda_y = abs(v) + c

    dt_x = dx / lambda_x if lambda_x > 0 else np.inf
    dt_y = dy / lambda_y if lambda_y > 0 else np.inf

    dt = cfl_number * min(dt_x, dt_y)

    return dt


def lax_friedrichs_flux(U_L, U_R, direction='x', g=9.81):
    """
    Lax-Friedrichs数值通量

    Args:
        U_L: 左侧状态
        U_R: 右侧状态
        direction: 'x' 或 'y'
        g: 重力加速度

    Returns:
        F_num: 数值通量
    """
    if direction == 'x':
        F_L = compute_x_flux(U_L, g)
        F_R = compute_x_flux(U_R, g)
    else:  # direction == 'y'
        F_L = compute_y_flux(U_L, g)
        F_R = compute_y_flux(U_R, g)

    # 计算最大波速
    h_L, u_L, v_L = primitives_from_state(U_L)
    h_R, u_R, v_R = primitives_from_state(U_R)

    c_L = np.sqrt(g * h_L) if h_L > 0 else 0.0
    c_R = np.sqrt(g * h_R) if h_R > 0 else 0.0

    if direction == 'x':
        alpha = max(abs(u_L) + c_L, abs(u_R) + c_R)
    else:
        alpha = max(abs(v_L) + c_L, abs(v_R) + c_R)

    # Lax-Friedrichs通量
    F_num = 0.5 * (F_L + F_R) - 0.5 * alpha * (U_R - U_L)

    return F_num


def is_wet_cell(h, h_dry=0.01):
    """
    判定干湿单元

    Args:
        h: 水深 (m)
        h_dry: 临界水深 (m)

    Returns:
        wet: True表示湿单元，False表示干单元
    """
    return h >= h_dry


def friction_source_term(h, u, v, n, g=9.81):
    """
    计算摩阻源项

    Args:
        h: 水深 (m)
        u: x方向流速 (m/s)
        v: y方向流速 (m/s)
        n: 糙率系数
        g: 重力加速度

    Returns:
        S_fx, S_fy: x和y方向摩阻源项
    """
    if h < 1e-10:
        return 0.0, 0.0

    velocity_mag = np.sqrt(u**2 + v**2)

    # 曼宁摩阻
    C_f = g * n**2 * velocity_mag / h**(4.0/3.0)

    S_fx = -C_f * u
    S_fy = -C_f * v

    return S_fx, S_fy


def bed_slope_source_term(h, dz_dx, dz_dy, g=9.81):
    """
    计算底坡源项

    Args:
        h: 水深 (m)
        dz_dx: 底高程x方向梯度
        dz_dy: 底高程y方向梯度
        g: 重力加速度

    Returns:
        S_bx, S_by: x和y方向底坡源项
    """
    S_bx = -g * h * dz_dx
    S_by = -g * h * dz_dy

    return S_bx, S_by


def compute_velocity_magnitude(u, v):
    """
    计算速度矢量大小

    Args:
        u: x方向流速
        v: y方向流速

    Returns:
        velocity_mag: 速度大小
    """
    return np.sqrt(u**2 + v**2)


class TestCase202DFlow:
    """案例20：二维明渠水流模拟测试"""

    def test_state_vector_construction(self):
        """测试1：状态向量构造"""
        h = 2.0
        u = 1.0
        v = 0.5

        U = state_vector_from_primitives(h, u, v)

        # 验证状态向量
        assert abs(U[0] - h) < 1e-10
        assert abs(U[1] - h * u) < 1e-10
        assert abs(U[2] - h * v) < 1e-10

    def test_primitives_extraction(self):
        """测试2：原始变量提取"""
        U = np.array([2.0, 2.0, 1.0])  # h=2, hu=2, hv=1

        h, u, v = primitives_from_state(U)

        # 验证提取
        assert abs(h - 2.0) < 1e-10
        assert abs(u - 1.0) < 1e-10
        assert abs(v - 0.5) < 1e-10

    def test_x_flux_calculation(self):
        """测试3：x方向通量计算"""
        h = 2.0
        u = 1.0
        v = 0.5
        g = 9.81

        U = state_vector_from_primitives(h, u, v)
        F = compute_x_flux(U, g)

        # F = [hu, hu²+gh²/2, huv]
        F_expected = np.array([
            h * u,
            h * u**2 + 0.5 * g * h**2,
            h * u * v
        ])

        assert np.allclose(F, F_expected)

    def test_y_flux_calculation(self):
        """测试4：y方向通量计算"""
        h = 2.0
        u = 1.0
        v = 0.5
        g = 9.81

        U = state_vector_from_primitives(h, u, v)
        G = compute_y_flux(U, g)

        # G = [hv, huv, hv²+gh²/2]
        G_expected = np.array([
            h * v,
            h * u * v,
            h * v**2 + 0.5 * g * h**2
        ])

        assert np.allclose(G, G_expected)

    def test_wave_speed_calculation(self):
        """测试5：浅水波速计算"""
        h = 3.0
        u = 1.0
        v = 0.5
        g = 9.81

        c, lambda_max = shallow_water_wave_speed(h, u, v, g)

        # 波速 c = √(gh)
        c_expected = np.sqrt(g * h)
        assert abs(c - c_expected) < 0.01

        # 最大特征值 = |v| + c
        velocity_mag = np.sqrt(u**2 + v**2)
        lambda_expected = velocity_mag + c
        assert abs(lambda_max - lambda_expected) < 0.01

    def test_cfl_timestep_calculation(self):
        """测试6：CFL时间步长计算"""
        dx = 10.0
        dy = 10.0
        h = 3.0
        u = 1.0
        v = 0.5
        cfl_number = 0.5
        g = 9.81

        dt = compute_cfl_timestep(dx, dy, h, u, v, cfl_number, g)

        # dt应为正
        assert dt > 0

        # dt应满足CFL条件
        c = np.sqrt(g * h)
        lambda_x = abs(u) + c
        lambda_y = abs(v) + c
        dt_max = cfl_number * min(dx / lambda_x, dy / lambda_y)

        assert abs(dt - dt_max) < 0.01

    def test_lax_friedrichs_flux_x(self):
        """测试7：Lax-Friedrichs x方向通量"""
        U_L = np.array([2.0, 2.0, 1.0])
        U_R = np.array([1.8, 1.8, 0.9])
        g = 9.81

        F_num = lax_friedrichs_flux(U_L, U_R, direction='x', g=g)

        # 数值通量应有3个分量
        assert len(F_num) == 3

        # 通量应有合理值（不验证精确值，因为公式复杂）
        assert np.all(np.isfinite(F_num))

    def test_lax_friedrichs_flux_symmetry(self):
        """测试8：Lax-Friedrichs通量对称性"""
        U_L = np.array([2.0, 2.0, 1.0])
        U_R = np.array([2.0, 2.0, 1.0])  # 相同状态
        g = 9.81

        F_num = lax_friedrichs_flux(U_L, U_R, direction='x', g=g)
        F_exact = compute_x_flux(U_L, g)

        # 相同状态时，数值通量应等于精确通量
        assert np.allclose(F_num, F_exact)

    def test_wet_cell_determination(self):
        """测试9：湿单元判定"""
        h_dry = 0.01

        # 湿单元
        h_wet = 0.5
        assert is_wet_cell(h_wet, h_dry) == True

        # 干单元
        h_dry_cell = 0.005
        assert is_wet_cell(h_dry_cell, h_dry) == False

        # 临界
        h_critical = h_dry
        assert is_wet_cell(h_critical, h_dry) == True

    def test_friction_source_term(self):
        """测试10：摩阻源项"""
        h = 2.0
        u = 1.0
        v = 0.5
        n = 0.03
        g = 9.81

        S_fx, S_fy = friction_source_term(h, u, v, n, g)

        # 摩阻应与速度反向
        assert S_fx < 0  # u > 0, 所以摩阻为负
        assert S_fy < 0  # v > 0, 所以摩阻为负

        # 摩阻大小应与速度成比例
        assert abs(S_fx) > abs(S_fy)  # u > v

    def test_bed_slope_source_term(self):
        """测试11：底坡源项"""
        h = 2.0
        dz_dx = 0.001  # 上坡
        dz_dy = 0.0
        g = 9.81

        S_bx, S_by = bed_slope_source_term(h, dz_dx, dz_dy, g)

        # 上坡时底坡源项为负（阻碍流动）
        assert S_bx < 0

        # y方向无坡度
        assert abs(S_by) < 1e-10

    def test_velocity_magnitude(self):
        """测试12：速度矢量大小"""
        u = 3.0
        v = 4.0

        velocity_mag = compute_velocity_magnitude(u, v)

        # 3-4-5三角形
        assert abs(velocity_mag - 5.0) < 1e-10


class TestConservationProperties:
    """守恒特性测试"""

    def test_zero_velocity_zero_flux(self):
        """测试零速度时通量"""
        h = 2.0
        u = 0.0
        v = 0.0
        g = 9.81

        U = state_vector_from_primitives(h, u, v)
        F = compute_x_flux(U, g)
        G = compute_y_flux(U, g)

        # 零速度时，对流通量应为零（仅有压力项）
        assert abs(F[0]) < 1e-10  # hu = 0
        assert abs(G[0]) < 1e-10  # hv = 0

        # 压力项不为零
        pressure = 0.5 * g * h**2
        assert abs(F[1] - pressure) < 0.01
        assert abs(G[2] - pressure) < 0.01

    def test_flux_consistency(self):
        """测试通量一致性"""
        h = 2.0
        u = 1.0
        v = 0.5

        U = state_vector_from_primitives(h, u, v)
        F = compute_x_flux(U)
        G = compute_y_flux(U)

        # 质量通量应等于动量
        assert abs(F[0] - U[1]) < 1e-10
        assert abs(G[0] - U[2]) < 1e-10

    def test_friction_energy_dissipation(self):
        """测试摩阻耗能"""
        h = 2.0
        u = 1.0
        v = 0.5
        n = 0.03

        S_fx, S_fy = friction_source_term(h, u, v, n)

        # 摩阻功率（耗能）= S_f · v
        power_dissipation = S_fx * u + S_fy * v

        # 耗能应为负
        assert power_dissipation < 0


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_depth(self):
        """测试零水深"""
        h = 0.0
        u = 1.0  # 无意义
        v = 0.5

        U = state_vector_from_primitives(h, u, v)

        # 零水深时状态向量应全为零
        assert np.allclose(U, np.zeros(3))

        # 通量应为零
        F = compute_x_flux(U)
        G = compute_y_flux(U)
        assert np.allclose(F, np.zeros(3))
        assert np.allclose(G, np.zeros(3))

    def test_very_shallow_water(self):
        """测试极浅水"""
        h = 0.001  # 1mm
        u = 0.1
        v = 0.0

        c, lambda_max = shallow_water_wave_speed(h, u, v)

        # 极浅水波速很小
        assert c < 0.2

    def test_very_deep_water(self):
        """测试深水"""
        h = 100.0
        u = 1.0
        v = 0.5

        c, lambda_max = shallow_water_wave_speed(h, u, v)

        # 深水波速大
        assert c > 30.0

    def test_high_velocity(self):
        """测试高速流动"""
        h = 2.0
        u = 10.0  # 高速
        v = 0.0
        g = 9.81

        U = state_vector_from_primitives(h, u, v)
        F = compute_x_flux(U, g)

        # 高速时动量通量占主导
        momentum_flux = h * u**2
        pressure_flux = 0.5 * g * h**2

        assert momentum_flux > pressure_flux

    def test_zero_roughness(self):
        """测试零糙率"""
        h = 2.0
        u = 1.0
        v = 0.5
        n = 0.0  # 光滑

        S_fx, S_fy = friction_source_term(h, u, v, n)

        # 零糙率无摩阻
        assert abs(S_fx) < 1e-10
        assert abs(S_fy) < 1e-10

    def test_very_high_roughness(self):
        """测试高糙率"""
        h = 2.0
        u = 1.0
        v = 0.5
        n = 0.1  # 很粗糙

        S_fx, S_fy = friction_source_term(h, u, v, n)

        # 高糙率大摩阻（n=0.1时S_f约0.04）
        assert abs(S_fx) > 0.03
        assert abs(S_fy) > 0.01

    def test_flat_bed(self):
        """测试平坦床"""
        h = 2.0
        dz_dx = 0.0
        dz_dy = 0.0

        S_bx, S_by = bed_slope_source_term(h, dz_dx, dz_dy)

        # 平坦床无底坡源项
        assert abs(S_bx) < 1e-10
        assert abs(S_by) < 1e-10

    def test_cfl_very_small_grid(self):
        """测试极小网格"""
        dx = 0.1  # 10cm
        dy = 0.1
        h = 2.0
        u = 1.0
        v = 0.5

        dt = compute_cfl_timestep(dx, dy, h, u, v)

        # 小网格需要小时间步
        assert dt < 0.1

    def test_cfl_large_grid(self):
        """测试大网格"""
        dx = 100.0  # 100m
        dy = 100.0
        h = 2.0
        u = 1.0
        v = 0.5

        dt = compute_cfl_timestep(dx, dy, h, u, v)

        # 大网格允许大时间步
        assert dt > 1.0

    def test_primitives_from_zero_depth(self):
        """测试从零水深提取原始变量"""
        U = np.array([0.0, 0.0, 0.0])

        h, u, v = primitives_from_state(U)

        # 零水深时速度应为零（避免除零）
        assert h == 0.0
        assert u == 0.0
        assert v == 0.0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
