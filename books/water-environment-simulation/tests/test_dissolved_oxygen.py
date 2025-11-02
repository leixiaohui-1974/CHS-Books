"""
测试溶解氧模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.dissolved_oxygen import StreeterPhelps, DOBODCoupled, calculate_reaeration_coefficient


class TestStreeterPhelps:
    """测试Streeter-Phelps模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = StreeterPhelps(L0=30.0, D0=3.0, kd=0.2, ka=0.4, T=10.0, nt=1000)
        
        assert model.L0 == 30.0
        assert model.D0 == 3.0
        assert model.kd == 0.2
        assert model.ka == 0.4
        assert model.T == 10.0
        assert len(model.t) == 1000
    
    def test_analytical_solution(self):
        """测试解析解"""
        model = StreeterPhelps(L0=30.0, D0=3.0, kd=0.2, ka=0.4, T=10.0, nt=1000)
        model.set_saturation_do(9.09)
        
        L, D, DO = model.analytical_solution()
        
        # 检查结果合理性
        assert np.all(L >= 0)  # BOD非负
        assert np.all(D >= 0)  # 亏损非负
        assert np.all(DO >= 0)  # DO非负
        assert np.all(DO <= 9.09 + 0.1)  # DO不超过饱和值（允许小误差）
        
        # BOD应该单调下降
        assert np.all(np.diff(L) <= 0)
        
        # 初始值检查
        assert abs(L[0] - 30.0) < 0.01
        assert abs(D[0] - 3.0) < 0.01
    
    def test_bod_decay(self):
        """测试BOD降解"""
        L0 = 30.0
        kd = 0.2
        model = StreeterPhelps(L0=L0, D0=1.0, kd=kd, ka=0.4, T=10.0, nt=1000)
        
        L, _, _ = model.analytical_solution()
        
        # 半衰期检查
        t_half = np.log(2) / kd
        idx_half = int(t_half / model.dt)
        
        if idx_half < len(L):
            assert L[idx_half] < L0 / 2 + 2  # 允许误差
            assert L[idx_half] > L0 / 2 - 2
    
    def test_critical_point(self):
        """测试临界点计算"""
        model = StreeterPhelps(L0=30.0, D0=3.0, kd=0.2, ka=0.4, T=10.0, nt=1000)
        model.set_saturation_do(9.09)
        
        tc, Dc, DOc = model.calculate_critical_point()
        
        # 临界点应该在合理范围内
        assert tc > 0
        assert tc < model.T
        assert Dc > 0
        assert DOc > 0
        assert DOc < model.DOs
        
        # 临界点是最低DO点
        _, _, DO = model.analytical_solution()
        DO_min = np.min(DO)
        
        assert abs(DOc - DO_min) < 0.5  # 允许一定误差
    
    def test_saturation_do_calculation(self):
        """测试饱和DO计算"""
        model = StreeterPhelps(L0=30.0, D0=3.0, kd=0.2, ka=0.4, T=10.0)
        
        # 20°C时的饱和DO应该接近9.09
        DOs_20 = model.calculate_saturation_do(20)
        assert abs(DOs_20 - 9.09) < 0.5
        
        # 温度升高，饱和DO降低
        DOs_10 = model.calculate_saturation_do(10)
        DOs_30 = model.calculate_saturation_do(30)
        
        assert DOs_10 > DOs_20 > DOs_30
    
    def test_temperature_correction(self):
        """测试温度校正"""
        model = StreeterPhelps(L0=30.0, D0=3.0, kd=0.2, ka=0.4, T=10.0)
        
        kd_20 = 0.2
        ka_20 = 0.4
        
        # 10°C时系数应该减小
        kd_10, ka_10 = model.temperature_correction(kd_20, ka_20, 10)
        assert kd_10 < kd_20
        assert ka_10 < ka_20
        
        # 30°C时系数应该增大
        kd_30, ka_30 = model.temperature_correction(kd_20, ka_20, 30)
        assert kd_30 > kd_20
        assert ka_30 > ka_20
    
    def test_special_case_ka_equals_kd(self):
        """测试特殊情况：ka = kd"""
        L0 = 20.0  # 较小初始BOD
        D0 = 0.5  # 很小的初始亏损
        k = 0.2  # ka = kd
        
        model = StreeterPhelps(L0=L0, D0=D0, kd=k, ka=k, T=3.0, nt=300)  # 短时间
        model.set_saturation_do(9.09)
        
        L, D, DO = model.analytical_solution()
        
        # 主要测试：数值稳定性（不产生NaN或Inf）
        assert np.all(np.isfinite(L))
        assert np.all(np.isfinite(D))
        assert np.all(np.isfinite(DO))
        
        # BOD应该非负且单调递减
        assert np.all(L >= 0)
        assert np.all(np.diff(L) <= 0)


class TestDOBODCoupled:
    """测试DO-BOD耦合模型"""
    
    def test_initialization(self):
        """测试耦合模型初始化"""
        model = DOBODCoupled(L=50000, T=5.0, nx=100, nt=500,
                             u=0.3, D_coef=10.0, kd=0.2, ka=0.4, DOs=9.09)
        
        assert model.L_length == 50000
        assert model.nx == 100
        assert model.nt == 500
        assert model.BOD.shape == (500, 100)
        assert model.DO.shape == (500, 100)
    
    def test_initial_conditions(self):
        """测试初始条件设置"""
        model = DOBODCoupled(L=50000, T=5.0, nx=100, nt=500,
                             u=0.3, D_coef=10.0, kd=0.2, ka=0.4, DOs=9.09)
        
        # 常数初始条件
        model.set_initial_conditions(30.0, 6.0)
        assert np.all(model.BOD[0, :] == 30.0)
        assert np.all(model.DO[0, :] == 6.0)
        
        # 函数初始条件
        BOD0 = lambda x: 20.0 + 10.0 * np.exp(-x/10000)
        DO0 = lambda x: 5.0 + x/50000
        
        model.set_initial_conditions(BOD0, DO0)
        assert model.BOD[0, 0] > model.BOD[0, -1]  # BOD递减
        assert model.DO[0, 0] < model.DO[0, -1]    # DO递增
    
    def test_coupled_solve(self):
        """测试耦合求解"""
        model = DOBODCoupled(L=50000, T=2.0, nx=100, nt=200,
                             u=0.3, D_coef=10.0, kd=0.2, ka=0.4, DOs=9.09)
        
        model.set_initial_conditions(30.0, 6.0)
        model.set_boundary_conditions(30.0, 6.0)
        
        BOD, DO = model.solve(method='upwind')
        
        # 检查结果合理性
        assert np.all(BOD >= -0.1)  # 允许小量负值
        assert np.all(DO >= -0.1)
        assert np.all(np.isfinite(BOD))
        assert np.all(np.isfinite(DO))
        
        # BOD应该沿程衰减
        assert BOD[-1, -1] < BOD[-1, 0]


def test_reaeration_coefficient():
    """测试复氧系数计算"""
    u = 0.3  # m/s
    H = 1.5  # m
    
    # Owens公式
    ka_owens = calculate_reaeration_coefficient(u, H, 'Owens')
    assert ka_owens > 0
    assert ka_owens < 5.0  # 合理范围
    
    # Churchill公式
    ka_churchill = calculate_reaeration_coefficient(u, H, 'Churchill')
    assert ka_churchill > 0
    assert ka_churchill < 5.0
    
    # O'Connor-Dobbins公式
    ka_oconnor = calculate_reaeration_coefficient(u, H, 'OConnor-Dobbins')
    assert ka_oconnor > 0
    assert ka_oconnor < 5.0
    
    # 流速增大，ka应该增大
    ka_slow = calculate_reaeration_coefficient(0.1, H, 'Owens')
    ka_fast = calculate_reaeration_coefficient(0.5, H, 'Owens')
    assert ka_fast > ka_slow
    
    # 水深增大，ka应该减小
    ka_shallow = calculate_reaeration_coefficient(u, 0.5, 'Owens')
    ka_deep = calculate_reaeration_coefficient(u, 2.0, 'Owens')
    assert ka_shallow > ka_deep


def test_oxygen_recovery():
    """测试DO恢复"""
    model = StreeterPhelps(L0=30.0, D0=5.0, kd=0.2, ka=0.8, T=20.0, nt=2000)
    model.set_saturation_do(9.09)
    
    _, _, DO = model.solve()
    
    # 高ka/kd比值（4.0）应该使DO快速恢复
    # 最终DO应该接近饱和值
    assert DO[-1] > 8.0  # 接近饱和


def test_low_ka_high_depletion():
    """测试低ka情况（差自净能力）"""
    model = StreeterPhelps(L0=40.0, D0=2.0, kd=0.3, ka=0.15, T=20.0, nt=2000)
    model.set_saturation_do(9.09)
    
    tc, Dc, DOc = model.calculate_critical_point()
    
    # 低ka/kd比值（0.5 < 1）应该导致严重亏损
    # 注意：ka < kd时，DO会持续下降
    assert DOc < 6.0  # 水质较差


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
