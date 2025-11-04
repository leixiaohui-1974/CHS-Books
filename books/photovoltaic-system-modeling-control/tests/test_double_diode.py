"""
测试双二极管模型
Test Double Diode Model
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from code.models.pv_cell import SingleDiodeModel, DoubleDiodeModel


class TestDoubleDiodeModel(unittest.TestCase):
    """测试双二极管模型"""
    
    def setUp(self):
        """设置测试"""
        self.pv = DoubleDiodeModel(
            Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
            T=298.15, G=1000.0
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.pv)
        self.assertEqual(self.pv.n1, 1.0)
        self.assertEqual(self.pv.n2, 2.0)
        self.assertIsNotNone(self.pv.I01)
        self.assertIsNotNone(self.pv.I02)
    
    def test_two_saturation_currents(self):
        """测试两个饱和电流"""
        self.assertGreater(self.pv.I01, 0)
        self.assertGreater(self.pv.I02, 0)
        # I01应该大于I02 (扩散电流主导)
        self.assertGreater(self.pv.I01, self.pv.I02)
    
    def test_basic_characteristics(self):
        """测试基本特性"""
        # 短路电流
        I_sc = self.pv.calculate_current(0.0)
        self.assertGreater(I_sc, 0)
        
        # 开路电压
        I_oc = self.pv.calculate_current(self.pv.Voc)
        self.assertLess(I_oc, 0.01)
    
    def test_mpp(self):
        """测试最大功率点"""
        vmpp, impp, pmpp = self.pv.find_mpp()
        
        self.assertGreater(vmpp, 0)
        self.assertLess(vmpp, self.pv.Voc)
        self.assertGreater(impp, 0)
        self.assertGreater(pmpp, 0)
    
    def test_comparison_with_single_diode(self):
        """测试与单二极管模型对比"""
        # 创建单二极管模型
        pv1 = SingleDiodeModel(
            Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
            T=298.15, G=1000.0
        )
        
        # 获取特性曲线
        V1, I1 = pv1.get_iv_curve(200)
        V2, I2 = self.pv.get_iv_curve(200)
        
        # 曲线应该相似但不完全相同
        correlation = np.corrcoef(I1, I2)[0, 1]
        self.assertGreater(correlation, 0.95)  # 高度相关
        
        # 应该有差异
        max_diff = np.max(np.abs(I1 - I2))
        self.assertGreater(max_diff, 0.001)  # 有明显差异
    
    def test_temperature_effect(self):
        """测试温度影响"""
        pv_25 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        pv_50 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=323.15, G=1000.0)
        
        # Voc应该下降
        self.assertLess(pv_50.Voc, pv_25.Voc)
    
    def test_irradiance_effect(self):
        """测试辐照度影响"""
        pv_1000 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        pv_200 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=200.0)
        
        # Isc应该显著下降
        self.assertLess(pv_200.Isc, pv_1000.Isc * 0.3)
        
        # Voc应该下降
        self.assertLess(pv_200.Voc, pv_1000.Voc)
    
    def test_update_conditions(self):
        """测试更新条件"""
        original_Isc = self.pv.Isc
        
        self.pv.update_conditions(G=500.0)
        self.assertEqual(self.pv.G, 500.0)
        self.assertNotEqual(self.pv.Isc, original_Isc)
    
    def test_get_parameters(self):
        """测试获取参数"""
        params = self.pv.get_parameters()
        
        self.assertIn('n1', params)
        self.assertIn('n2', params)
        self.assertIn('I01', params)
        self.assertIn('I02', params)
    
    def test_physical_constraints(self):
        """测试物理约束"""
        test_voltages = np.linspace(0, self.pv.Voc, 50)
        
        for v in test_voltages:
            i = self.pv.calculate_current(v)
            self.assertGreaterEqual(i, 0)


class TestModelAccuracy(unittest.TestCase):
    """测试模型精度"""
    
    def test_low_irradiance_accuracy(self):
        """测试低辐照度精度"""
        # 在低辐照度下,双二极管应该更准确
        pv1 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=100.0)
        pv2 = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=100.0)
        
        # 两个模型都应该能正常工作
        vmpp1, _, pmpp1 = pv1.find_mpp()
        vmpp2, _, pmpp2 = pv2.find_mpp()
        
        self.assertGreater(pmpp1, 0)
        self.assertGreater(pmpp2, 0)
    
    def test_consistency(self):
        """测试一致性"""
        # 同样参数,结果应该可重现
        pv_a = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        pv_b = DoubleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        
        vmpp_a, _, pmpp_a = pv_a.find_mpp()
        vmpp_b, _, pmpp_b = pv_b.find_mpp()
        
        self.assertAlmostEqual(vmpp_a, vmpp_b, places=5)
        self.assertAlmostEqual(pmpp_a, pmpp_b, places=5)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDoubleDiodeModel))
    suite.addTests(loader.loadTestsFromTestCase(TestModelAccuracy))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
