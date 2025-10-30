"""
集成测试：明渠水力学综合系统测试

本测试文件包含跨案例的集成测试，验证：
1. 明渠系统完整计算流程
2. 有压流系统完整计算流程
3. 数据一致性验证

注意：本版本为简化版，仅包含可直接运行的集成测试。
更多集成测试将在后续版本中添加。

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加tests目录到路径，以便直接导入其他测试模块
tests_dir = os.path.dirname(os.path.abspath(__file__))
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)


class TestIntegrationOpenChannel:
    """明渠系统集成测试"""

    def test_irrigation_channel_complete_design(self):
        """测试1：灌溉渠道完整设计流程"""
        # 导入案例1的函数
        from test_case_01_irrigation import (
            trapezoidal_area, trapezoidal_wetted_perimeter as wetted_perimeter,
            hydraulic_radius, manning_velocity, discharge as compute_discharge,
            froude_number
        )

        # 设计参数
        Q_design = 5.0  # m³/s
        b = 3.0  # m
        m = 1.5
        S0 = 0.0003
        n = 0.02
        g = 9.81

        # 迭代计算正常水深
        h = 1.0
        for _ in range(20):
            A = trapezoidal_area(b, h, m)
            P = wetted_perimeter(b, h, m)
            R = hydraulic_radius(A, P)
            v = manning_velocity(R, S0, n)
            Q = compute_discharge(A, v)

            if abs(Q - Q_design) < 1e-6:
                break

            # 简单更新
            h = h * (Q_design / Q) ** 0.4

        # 验证结果
        assert 1.0 < h < 2.0  # 水深合理
        A_final = trapezoidal_area(b, h, m)
        P_final = wetted_perimeter(b, h, m)
        R_final = hydraulic_radius(A_final, P_final)
        v_final = manning_velocity(R_final, S0, n)
        Q_final = compute_discharge(A_final, v_final)

        # 流量误差小于1%
        assert abs(Q_final - Q_design) / Q_design < 0.01

        # 流速在合理范围
        assert 0.5 < v_final < 2.0

        # 流态为缓流
        Fr = froude_number(v_final, h, g)
        assert Fr < 1.0


class TestIntegrationPressurizedFlow:
    """有压流系统集成测试"""

    def test_pipe_network_complete_analysis(self):
        """测试2：管网完整分析"""
        from test_case_21_pipe_flow import (
            reynolds_number, colebrook_white, darcy_head_loss
        )
        from test_case_22_pipe_network import (
            pipe_head_loss, hardy_cross_correction
        )

        # 管道参数
        D = 0.3  # m
        L = 500  # m
        Q = 0.15  # m³/s
        epsilon_D = 0.0005
        nu = 1.0e-6

        # 计算Reynolds数
        v = Q / (np.pi * D**2 / 4)
        Re = reynolds_number(v, D, nu)

        # 计算摩阻系数
        lambda_f = colebrook_white(Re, epsilon_D)

        # 计算水头损失
        h_f = darcy_head_loss(lambda_f, L, D, v)

        # 验证水头损失合理性
        assert 0 < h_f < 20  # 500m管道损失应在合理范围

        # 管网分析（简化单环）
        K = lambda_f * L / (2 * 9.81 * D**5 / (np.pi**2))
        pipe_K = [K, K, K, K]  # 4根管道
        Q_init = [Q, -Q/2, -Q/2, 0]  # 初始流量分配

        # Hardy-Cross校正
        delta_Q = hardy_cross_correction(Q_init, pipe_K, n=2.0)

        # 校正量应合理
        assert abs(delta_Q) < Q  # 校正量不会超过流量本身

    def test_economic_pipe_design(self):
        """测试3：管道经济设计"""
        from test_case_23_long_distance import (
            economic_diameter_formula, construction_cost_pipe,
            annual_operation_cost, pump_power, total_cost_npv
        )

        # 设计参数
        Q = 2.0  # m³/s
        L = 50000  # m (50 km)
        n_years = 50
        r = 0.07

        # 经济管径
        D_econ = economic_diameter_formula(Q)

        # 经济管径应在合理范围
        assert 0.5 < D_econ < 3.0

        # 建设费用
        k = 1500  # 单位成本系数
        a = 1.0   # 管径指数
        C_constr = construction_cost_pipe(k, D_econ, a, L)

        # 运行费用
        lambda_f = 0.02
        g = 9.81
        A = np.pi * D_econ**2 / 4
        v = Q / A
        h_f = lambda_f * (L/D_econ) * (v**2 / (2*g))
        H_total = h_f + 10  # 假设静扬程10m
        P_pump = pump_power(1000, g, Q, H_total, eta=0.75)  # W

        C_elec = 0.6  # 电价 元/kWh
        T = 7000      # 年运行小时数
        C_annual = annual_operation_cost(C_elec, P_pump, T)

        # 总费用NPV
        NPV = total_cost_npv(C_constr, C_annual, n_years, r)

        # NPV应为正值
        assert NPV > 0


class TestIntegrationTransientFlow:
    """瞬变流系统集成测试"""

    def test_water_hammer_moc_simulation(self):
        """测试4：水锤-MOC完整模拟"""
        from test_case_25_water_hammer import (
            wave_speed_elastic_pipe, joukowsky_head_rise, critical_time
        )
        from test_case_26_moc import (
            space_step, timestep_from_segments, c_plus_equation, c_minus_equation
        )

        # 管道参数
        L = 1200  # m
        D = 0.6  # m
        e = 0.012  # m
        v0 = 1.5  # m/s
        H0 = 60  # m

        K = 2.1e9  # Pa
        rho = 1000
        E = 200e9

        # 计算波速
        a = wave_speed_elastic_pipe(K, rho, E, D, e)

        # 估算水锤压力升高
        delta_H = joukowsky_head_rise(a, v0)

        # 水锤压力应显著但合理
        assert 10 < delta_H < 500

        # MOC离散化
        N = 12
        dx = space_step(L, N)
        dt = timestep_from_segments(L, N, a)

        # Courant条件
        assert abs(dt - dx/a) < 1e-9

        # 特征线计算（简化测试）
        H_A = H0
        v_A = v0
        R_A = 0.01  # 摩阻项

        H_B = H0
        v_B = v0
        R_B = 0.01

        # 假设流速减小到v0/2
        v_P = v0 / 2

        # C+方程
        H_P_plus = c_plus_equation(H_A, v_A, v_P, R_A, a)

        # C-方程
        H_P_minus = c_minus_equation(H_B, v_B, v_P, R_B, a)

        # 两个方程计算的压力应在合理范围（允许负压）
        assert -100 < H_P_plus < 300
        assert -100 < H_P_minus < 300
        # 压力值应该是数值类型
        assert isinstance(H_P_plus, (int, float, np.number))
        assert isinstance(H_P_minus, (int, float, np.number))

    def test_pump_surge_tank_protection(self):
        """测试5：泵站-调压井联合防护"""
        from test_case_27_pump_transients import (
            speed_decay_exponential, inertia_time_constant
        )
        from test_case_28_surge_tank import (
            thoma_critical_area, max_surge_simple
        )

        # 泵站参数
        GD2 = 50  # kg·m²
        n0 = 1450  # rpm
        M_friction = 20  # N·m

        # 惯性时间
        T_i = inertia_time_constant(GD2, n0, M_friction)

        # 5秒后转速
        n_5s = speed_decay_exponential(n0, 5, T_i)

        # 转速应下降但仍为正
        assert 0 < n_5s < n0

        # 调压井参数
        L = 2000  # m
        A = 15  # m²
        H_r = 100  # m

        # 临界面积
        A_t_crit = thoma_critical_area(L, A, H_r, F_s=1.5)

        # 设计面积（略大于临界）
        A_t = A_t_crit * 1.2

        # 最高涌浪
        v0 = 2.0  # m/s
        Z_max = max_surge_simple(v0, L, A_t)

        # 涌浪应在合理范围
        assert 0 < Z_max < H_r


class TestIntegrationHybridSystem:
    """混合系统集成测试"""

    def test_channel_to_pipe_transition(self):
        """测试6：渠道-管道过渡"""
        from test_case_29_channel_pipe import (
            manning_velocity, pipe_velocity, pipe_darcy_head_loss
        )

        # 明渠段
        Q = 1.2  # m³/s
        b = 2.0  # m
        h = 0.8  # m
        m = 1.0
        S0 = 0.0005
        n = 0.015

        A_channel = (b + m*h) * h
        P_channel = b + 2*h*np.sqrt(1 + m**2)
        R = A_channel / P_channel  # 水力半径 = 面积/湿周
        v_channel = manning_velocity(R, S0, n)
        Q_channel = A_channel * v_channel

        # 管道段（使用渠道计算出的流量以保证连续性）
        D = 0.8  # m
        L_pipe = 300  # m
        lambda_f = 0.02

        v_pipe = pipe_velocity(Q_channel, D)  # 使用渠道流量
        h_f_pipe = pipe_darcy_head_loss(lambda_f, L_pipe, D, v_pipe)

        # 验证：渠道流量应为正值且合理
        assert 0.5 < Q_channel < 10.0

        # 管道流速应合理（允许较高流速）
        assert 0.5 < v_pipe < 6.0

        # 水头损失应合理
        assert h_f_pipe > 0

        # 验证连续性方程
        A_pipe = np.pi * D**2 / 4
        assert abs(v_pipe * A_pipe - Q_channel) < 0.01  # 流量守恒

    def test_comprehensive_pump_channel_pipe_system(self):
        """测试7：泵站-渠道-管道综合系统"""
        from test_case_30_comprehensive import (
            static_head, system_total_head, pump_power, system_efficiency
        )

        # 水位差
        H_reservoir = 10  # m
        H_target = 35  # m

        # 静扬程
        H_static = static_head(H_target, H_reservoir)
        assert H_static == 25

        # 各段损失
        h_f_suction = 0.5  # m
        h_f_channel = 0.3  # m
        h_f_pipe = 2.0  # m
        h_f_local = 0.8  # m

        # 总扬程
        H_total = system_total_head(H_static, h_f_suction, h_f_channel,
                                    h_f_pipe, h_f_local)

        # 总扬程应包含所有损失
        assert H_total > H_static

        # 泵功率
        Q = 1.5  # m³/s
        eta = 0.75
        P = pump_power(1000, 9.81, Q, H_total, eta)

        # 功率应合理
        assert P > 0

        # 系统效率
        eta_sys = system_efficiency(H_static, H_total)

        # 系统效率应在合理范围
        assert 0.7 < eta_sys < 0.95


class TestDataConsistency:
    """数据一致性测试"""

    def test_unit_conversions(self):
        """测试8：单位换算一致性"""
        # 流量单位
        Q_m3s = 1.0  # m³/s
        Q_Ls = Q_m3s * 1000  # L/s
        assert Q_Ls == 1000.0

        # 压力单位
        p_Pa = 100000  # Pa
        p_kPa = p_Pa / 1000
        p_bar = p_Pa / 1e5
        assert p_kPa == 100.0
        assert p_bar == 1.0

        # 功率单位
        P_W = 1000  # W
        P_kW = P_W / 1000
        assert P_kW == 1.0

    def test_manning_chezy_equivalence(self):
        """测试9：Manning-Chézy公式等价性"""
        # Manning系数
        n = 0.02
        R = 1.0  # m

        # Manning流速
        v_manning = (1/n) * R**(2/3) * 0.001**0.5

        # Chézy系数
        C = R**(1/6) / n

        # Chézy流速
        v_chezy = C * np.sqrt(R * 0.001)

        # 两者应相等
        assert abs(v_manning - v_chezy) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
