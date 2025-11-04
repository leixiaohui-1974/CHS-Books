"""
测试光伏电池模型
Test PV Cell Models
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from code.models.pv_cell import SingleDiodeModel


class TestSingleDiodeModel(unittest.TestCase):
    """测试单二极管模型"""
    
    def setUp(self):
        """设置测试"""
        self.pv = SingleDiodeModel(
            Isc=8.0,
            Voc=0.6,
            Imp=7.5,
            Vmp=0.48,
            T=298.15,
            G=1000.0
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.pv)
        self.assertEqual(self.pv.Isc_stc, 8.0)
        self.assertEqual(self.pv.Voc_stc, 0.6)
        self.assertEqual(self.pv.T, 298.15)
        self.assertEqual(self.pv.G, 1000.0)
    
    def test_short_circuit_current(self):
        """测试短路电流"""
        I_sc = self.pv.calculate_current(0.0)
        self.assertGreater(I_sc, 0)
        self.assertAlmostEqual(I_sc, self.pv.Isc_stc, delta=0.5)
    
    def test_open_circuit_voltage(self):
        """测试开路电压"""
        I_oc = self.pv.calculate_current(self.pv.Voc)
        self.assertLess(I_oc, 0.01)  # 开路时电流应接近0
    
    def test_current_voltage_relationship(self):
        """测试电流电压关系"""
        # 电压增加,电流应该减少
        I1 = self.pv.calculate_current(0.1)
        I2 = self.pv.calculate_current(0.3)
        I3 = self.pv.calculate_current(0.5)
        
        self.assertGreater(I1, I2)
        self.assertGreater(I2, I3)
    
    def test_power_calculation(self):
        """测试功率计算"""
        P = self.pv.calculate_power(0.48)
        self.assertGreater(P, 0)
        self.assertLess(P, self.pv.Isc * self.pv.Voc)  # 功率应小于Isc*Voc
    
    def test_mpp_finding(self):
        """测试最大功率点寻找"""
        vmpp, impp, pmpp = self.pv.find_mpp()
        
        # MPP应该在合理范围内
        self.assertGreater(vmpp, 0)
        self.assertLess(vmpp, self.pv.Voc)
        self.assertGreater(impp, 0)
        self.assertLess(impp, self.pv.Isc)
        self.assertGreater(pmpp, 0)
        
        # MPP功率应该是最大的
        P_before = self.pv.calculate_power(vmpp - 0.05)
        P_after = self.pv.calculate_power(vmpp + 0.05)
        self.assertLess(P_before, pmpp)
        self.assertLess(P_after, pmpp)
    
    def test_fill_factor(self):
        """测试填充因子"""
        vmpp, impp, pmpp = self.pv.find_mpp()
        FF = pmpp / (self.pv.Voc * self.pv.Isc)
        
        # 填充因子应该在合理范围 (0.7-0.85)
        self.assertGreater(FF, 0.65)
        self.assertLess(FF, 0.90)
    
    def test_temperature_effect(self):
        """测试温度影响"""
        # 创建不同温度的电池
        pv_25 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        pv_50 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=323.15, G=1000.0)
        
        # 温度升高,Voc应该下降
        self.assertLess(pv_50.Voc, pv_25.Voc)
        
        # 温度升高,Isc应该略微增加
        self.assertGreaterEqual(pv_50.Isc, pv_25.Isc * 0.99)  # 允许小幅下降
    
    def test_irradiance_effect(self):
        """测试辐照度影响"""
        # 创建不同辐照度的电池
        pv_1000 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=1000.0)
        pv_500 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=500.0)
        pv_200 = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=200.0)
        
        # 辐照度减半,Isc应该大约减半
        self.assertAlmostEqual(pv_500.Isc, pv_1000.Isc / 2, delta=0.5)
        
        # 辐照度减小,Voc应该下降(对数关系,变化较小)
        # 使用更明显的对比(1000 vs 200)
        self.assertLess(pv_200.Voc, pv_1000.Voc)
        self.assertGreater(pv_200.Voc, pv_1000.Voc * 0.85)  # Voc变化约10-15%
    
    def test_iv_curve_generation(self):
        """测试I-V曲线生成"""
        V, I = self.pv.get_iv_curve(100)
        
        # 应该返回正确长度的数组
        self.assertEqual(len(V), 100)
        self.assertEqual(len(I), 100)
        
        # 电压应该从0到Voc
        self.assertAlmostEqual(V[0], 0, delta=0.01)
        self.assertAlmostEqual(V[-1], self.pv.Voc, delta=0.01)
        
        # 电流应该从Isc下降到0
        self.assertGreater(I[0], 0)
        self.assertLess(I[-1], 0.1)
    
    def test_pv_curve_generation(self):
        """测试P-V曲线生成"""
        V, P = self.pv.get_pv_curve(100)
        
        # 应该返回正确长度的数组
        self.assertEqual(len(V), 100)
        self.assertEqual(len(P), 100)
        
        # 功率应该大于等于0
        self.assertTrue(np.all(P >= 0))
        
        # 应该存在最大功率点
        max_power = np.max(P)
        self.assertGreater(max_power, 0)
    
    def test_update_conditions(self):
        """测试更新工作条件"""
        original_Isc = self.pv.Isc
        original_Voc = self.pv.Voc
        
        # 更新温度
        self.pv.update_conditions(T=323.15)
        self.assertEqual(self.pv.T, 323.15)
        self.assertNotEqual(self.pv.Isc, original_Isc)
        
        # 更新辐照度
        self.pv.update_conditions(G=500.0)
        self.assertEqual(self.pv.G, 500.0)
        
        # 同时更新
        self.pv.update_conditions(T=298.15, G=1000.0)
        self.assertEqual(self.pv.T, 298.15)
        self.assertEqual(self.pv.G, 1000.0)
    
    def test_get_parameters(self):
        """测试获取参数"""
        params = self.pv.get_parameters()
        
        # 应该返回字典
        self.assertIsInstance(params, dict)
        
        # 应该包含关键参数
        required_keys = ['T', 'G', 'n', 'Rs', 'Rsh', 'Iph', 'I0', 'Isc', 'Voc']
        for key in required_keys:
            self.assertIn(key, params)
    
    def test_physical_constraints(self):
        """测试物理约束"""
        # 测试多个电压点
        test_voltages = np.linspace(0, self.pv.Voc, 50)
        
        for v in test_voltages:
            i = self.pv.calculate_current(v)
            
            # 电流应该非负
            self.assertGreaterEqual(i, 0, f"Negative current at V={v}")
            
            # 电流应该小于等于Isc
            self.assertLessEqual(i, self.pv.Isc * 1.1, f"Current exceeds Isc at V={v}")


class TestPVCellEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        """设置测试"""
        self.pv = SingleDiodeModel(
            Isc=8.0,
            Voc=0.6,
            Imp=7.5,
            Vmp=0.48,
            T=298.15,
            G=1000.0
        )
    
    def test_extreme_temperature(self):
        """测试极端温度"""
        # 低温
        pv_cold = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=233.15, G=1000.0)  # -40°C
        self.assertIsNotNone(pv_cold.Isc)
        self.assertIsNotNone(pv_cold.Voc)
        
        # 高温
        pv_hot = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=353.15, G=1000.0)  # 80°C
        self.assertIsNotNone(pv_hot.Isc)
        self.assertIsNotNone(pv_hot.Voc)
    
    def test_low_irradiance(self):
        """测试低辐照度"""
        pv_low = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48, T=298.15, G=100.0)
        
        # 低辐照度下仍应有合理输出
        self.assertGreater(pv_low.Isc, 0)
        self.assertGreater(pv_low.Voc, 0)
        
        vmpp, impp, pmpp = pv_low.find_mpp()
        self.assertGreater(pmpp, 0)
    
    def test_zero_voltage(self):
        """测试零电压"""
        I = self.pv.calculate_current(0.0)
        self.assertAlmostEqual(I, self.pv.Isc, delta=0.1)
    
    def test_high_voltage(self):
        """测试高电压(超过Voc)"""
        I = self.pv.calculate_current(self.pv.Voc * 1.5)
        # 超过Voc后电流应该为0或很小
        self.assertLess(I, 0.1)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestSingleDiodeModel))
    suite.addTests(loader.loadTestsFromTestCase(TestPVCellEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
