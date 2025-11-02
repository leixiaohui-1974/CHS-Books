"""
测试营养盐循环模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.nutrients import (NitrogenCycle, PhosphorusCycle, 
                               EutrophicationIndex, calculate_oxygen_consumption)


class TestNitrogenCycle:
    """测试氮循环模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = NitrogenCycle(NH4_0=1.0, NO3_0=0.5, OrgN_0=0.3,
                              k_n=0.2, k_dn=0.1, k_am=0.15, T=30.0, nt=1000)
        
        assert model.NH4_0 == 1.0
        assert model.NO3_0 == 0.5
        assert model.OrgN_0 == 0.3
        assert model.k_n == 0.2
        assert model.k_dn == 0.1
        assert model.k_am == 0.15
        assert len(model.t) == 1000
    
    def test_solve(self):
        """测试氮循环求解"""
        model = NitrogenCycle(NH4_0=1.0, NO3_0=0.5, OrgN_0=0.5,
                              k_n=0.2, k_dn=0.1, k_am=0.15, T=30.0, nt=1000)
        model.set_do(6.0)
        
        NH4, NO3, OrgN, TN = model.solve()
        
        # 检查结果合理性
        assert np.all(NH4 >= -0.01)  # 允许小量负值
        assert np.all(NO3 >= -0.01)
        assert np.all(OrgN >= -0.01)
        assert np.all(TN >= 0)
        assert np.all(np.isfinite(NH4))
        assert np.all(np.isfinite(NO3))
        assert np.all(np.isfinite(OrgN))
    
    def test_organic_nitrogen_decrease(self):
        """测试有机氮应该递减"""
        model = NitrogenCycle(NH4_0=0.5, NO3_0=0.5, OrgN_0=1.0,
                              k_n=0.1, k_dn=0.05, k_am=0.2, T=20.0, nt=500)
        
        _, _, OrgN, _ = model.solve()
        
        # 有机氮应该单调递减（氨化作用）
        assert np.all(np.diff(OrgN) <= 0.001)  # 允许小误差
    
    def test_nitrification(self):
        """测试硝化作用（NH4 → NO3）"""
        # 高DO，硝化主导
        model = NitrogenCycle(NH4_0=2.0, NO3_0=0.1, OrgN_0=0.1,
                              k_n=0.3, k_dn=0.05, k_am=0.1, T=20.0, nt=500)
        model.set_do(8.0)  # 高DO
        
        NH4, NO3, _, _ = model.solve()
        
        # NH4应该减少，NO3应该增加
        assert NH4[-1] < NH4[0]
        assert NO3[-1] > NO3[0]
    
    def test_temperature_correction(self):
        """测试温度校正"""
        model = NitrogenCycle(NH4_0=1.0, NO3_0=1.0, OrgN_0=0.5,
                              k_n=0.2, k_dn=0.1, k_am=0.15, T=10.0)
        
        k_20 = 0.2
        
        # 10°C时速率应该减小
        k_10 = model.temperature_correction(k_20, 10, 'nitrification')
        assert k_10 < k_20
        
        # 30°C时速率应该增大
        k_30 = model.temperature_correction(k_20, 30, 'nitrification')
        assert k_30 > k_20
    
    def test_total_nitrogen_conservation(self):
        """测试总氮守恒（无反硝化时）"""
        # k_dn = 0，没有反硝化损失
        model = NitrogenCycle(NH4_0=1.0, NO3_0=0.5, OrgN_0=0.5,
                              k_n=0.2, k_dn=0.0, k_am=0.15, T=10.0, nt=200)
        model.set_do(6.0)
        
        _, _, _, TN = model.solve()
        
        # 总氮应该基本守恒（误差<5%）
        TN_loss = abs(TN[-1] - TN[0]) / TN[0]
        assert TN_loss < 0.05


class TestPhosphorusCycle:
    """测试磷循环模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = PhosphorusCycle(PO4_0=0.1, OrgP_0=0.05,
                                k_mp=0.3, k_s=0.05, T=30.0, nt=1000)
        
        assert model.PO4_0 == 0.1
        assert model.OrgP_0 == 0.05
        assert model.k_mp == 0.3
        assert model.k_s == 0.05
        assert len(model.t) == 1000
    
    def test_solve(self):
        """测试磷循环求解"""
        model = PhosphorusCycle(PO4_0=0.08, OrgP_0=0.07,
                                k_mp=0.3, k_s=0.05, T=30.0, nt=1000)
        
        PO4, OrgP, TP = model.solve()
        
        # 检查结果合理性
        assert np.all(PO4 >= -0.01)
        assert np.all(OrgP >= -0.01)
        assert np.all(TP >= -0.01)
        assert np.all(np.isfinite(PO4))
        assert np.all(np.isfinite(OrgP))
        assert np.all(np.isfinite(TP))
    
    def test_organic_phosphorus_decrease(self):
        """测试有机磷应该递减"""
        model = PhosphorusCycle(PO4_0=0.05, OrgP_0=0.1,
                                k_mp=0.3, k_s=0.05, T=20.0, nt=500)
        
        _, OrgP, _ = model.solve()
        
        # 有机磷应该单调递减
        assert np.all(np.diff(OrgP) <= 0.001)
    
    def test_mineralization(self):
        """测试矿化作用（OrgP → PO4）"""
        model = PhosphorusCycle(PO4_0=0.01, OrgP_0=0.1,
                                k_mp=0.5, k_s=0.0, T=20.0, nt=500)
        
        PO4, OrgP, _ = model.solve()
        
        # PO4应该增加，OrgP应该减少
        assert PO4[-1] > PO4[0]
        assert OrgP[-1] < OrgP[0]
    
    def test_settling(self):
        """测试沉降导致总磷减少"""
        model = PhosphorusCycle(PO4_0=0.05, OrgP_0=0.1,
                                k_mp=0.1, k_s=0.1, T=30.0, nt=500)
        
        _, _, TP = model.solve()
        
        # 总磷应该减少（沉降损失）
        assert TP[-1] < TP[0]


class TestEutrophicationIndex:
    """测试富营养化指数"""
    
    def test_carlson_tsi_chl(self):
        """测试基于叶绿素a的TSI"""
        # 低叶绿素a → 低TSI
        tsi_low = EutrophicationIndex.carlson_tsi_chl(2.0)
        assert tsi_low < 45
        
        # 高叶绿素a → 高TSI
        tsi_high = EutrophicationIndex.carlson_tsi_chl(50.0)
        assert tsi_high > 65
    
    def test_carlson_tsi_tp(self):
        """测试基于总磷的TSI"""
        # 低总磷 → 低TSI
        tsi_low = EutrophicationIndex.carlson_tsi_tp(10.0)
        assert tsi_low < 40
        
        # 高总磷 → 高TSI
        tsi_high = EutrophicationIndex.carlson_tsi_tp(100.0)
        assert tsi_high > 50
    
    def test_carlson_tsi_sd(self):
        """测试基于透明度的TSI"""
        # 高透明度 → 低TSI
        tsi_low = EutrophicationIndex.carlson_tsi_sd(3.0)
        assert tsi_low < 50
        
        # 低透明度 → 高TSI
        tsi_high = EutrophicationIndex.carlson_tsi_sd(0.5)
        assert tsi_high > 60
    
    def test_carlson_tsi_comprehensive(self):
        """测试综合TSI"""
        # 贫营养湖泊
        TSI_low, status_low = EutrophicationIndex.carlson_tsi_综合(3.0, 10.0, 4.0)
        assert TSI_low < 40
        assert "贫营养" in status_low or "中营养" in status_low
        
        # 富营养湖泊
        TSI_high, status_high = EutrophicationIndex.carlson_tsi_综合(40.0, 100.0, 0.5)
        assert TSI_high > 50
        assert "富营养" in status_high
    
    def test_china_tli(self):
        """测试中国湖泊TLI"""
        # 贫营养-中营养湖泊
        TLI_low, status_low = EutrophicationIndex.china_tli(3.0, 0.01, 0.2, 3.0, 2.0)
        assert TLI_low < 50
        
        # 富营养湖泊
        TLI_high, status_high = EutrophicationIndex.china_tli(50.0, 0.15, 2.5, 0.8, 8.0)
        assert TLI_high > 60
        assert "富营养" in status_high
    
    def test_limiting_nutrient(self):
        """测试限制性营养元素判断"""
        # 低N/P → 氮限制
        limiting_n = EutrophicationIndex.limiting_nutrient(0.5, 0.2, 7.2)
        assert limiting_n == 'N'
        
        # 高N/P → 磷限制
        limiting_p = EutrophicationIndex.limiting_nutrient(2.0, 0.1, 7.2)
        assert limiting_p == 'P'
        
        # 中等N/P → 共同限制
        limiting_co = EutrophicationIndex.limiting_nutrient(1.0, 0.14, 7.2)
        assert limiting_co == 'Co-limitation'


def test_oxygen_consumption():
    """测试硝化耗氧量计算"""
    NH4 = 1.0
    k_n = 0.2
    
    O2 = calculate_oxygen_consumption(NH4, k_n)
    
    # 理论耗氧量：1 mg NH4-N 需要 4.57 mg O2
    # 耗氧速率 = 4.57 * k_n * NH4
    expected = 4.57 * k_n * NH4
    
    assert abs(O2 - expected) < 0.01


def test_nitrogen_loss_by_denitrification():
    """测试反硝化导致氮损失"""
    # 有反硝化
    model_with_dn = NitrogenCycle(NH4_0=0.5, NO3_0=1.0, OrgN_0=0.5,
                                  k_n=0.1, k_dn=0.15, k_am=0.1, T=20.0, nt=500)
    model_with_dn.set_do(2.0)  # 低DO，有利于反硝化
    _, _, _, TN_with_dn = model_with_dn.solve()
    
    # 无反硝化
    model_no_dn = NitrogenCycle(NH4_0=0.5, NO3_0=1.0, OrgN_0=0.5,
                                k_n=0.1, k_dn=0.0, k_am=0.1, T=20.0, nt=500)
    model_no_dn.set_do(2.0)
    _, _, _, TN_no_dn = model_no_dn.solve()
    
    # 有反硝化时氮损失应该更多
    loss_with_dn = TN_with_dn[0] - TN_with_dn[-1]
    loss_no_dn = TN_no_dn[0] - TN_no_dn[-1]
    
    assert loss_with_dn > loss_no_dn


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
