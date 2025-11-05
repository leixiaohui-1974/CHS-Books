"""
参数辨识模块单元测试
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from code.models.pv_cell import SingleDiodeModel
from code.models.pv_identification import (ParameterExtractor, ParameterComparator,
                                           OnlineIdentification)


class TestParameterExtractor(unittest.TestCase):
    """参数提取器测试"""
    
    def setUp(self):
        self.extractor = ParameterExtractor()
        
        # 生成测试数据
        cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
        self.V_test, self.I_test = cell.get_iv_curve(50)
        
        # 关键点
        self.Isc = self.I_test[0]
        self.Voc = self.V_test[np.argmin(np.abs(self.I_test))]
        P = self.V_test * self.I_test
        idx_mpp = np.argmax(P)
        self.Vmp = self.V_test[idx_mpp]
        self.Imp = self.I_test[idx_mpp]
    
    def test_extract_from_key_points(self):
        """测试关键点法"""
        params = self.extractor.extract_from_key_points(
            self.Isc, self.Voc, self.Imp, self.Vmp
        )
        
        self.assertIn('Iph', params)
        self.assertIn('I0', params)
        self.assertIn('Rs', params)
        self.assertIn('Rsh', params)
        self.assertIn('n', params)
        
        # 参数应在合理范围
        self.assertGreater(params['Iph'], 0)
        self.assertGreater(params['I0'], 0)
        self.assertGreaterEqual(params['Rs'], 0)
        self.assertGreater(params['Rsh'], 0)
        self.assertGreater(params['n'], 0)
    
    def test_extract_from_curve_least_squares(self):
        """测试最小二乘法"""
        result = self.extractor.extract_from_curve(
            self.V_test, self.I_test,
            method='least_squares'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('rmse', result)
        self.assertIn('r2', result)
        self.assertGreater(result['r2'], 0.9)  # R² should be high
    
    def test_extract_from_curve_minimize(self):
        """测试优化法"""
        result = self.extractor.extract_from_curve(
            self.V_test, self.I_test,
            method='minimize'
        )
        
        self.assertIn('Iph', result)
        self.assertIn('rmse', result)
    
    def test_parameter_ranges(self):
        """测试参数范围合理性"""
        result = self.extractor.extract_from_curve(
            self.V_test, self.I_test
        )
        
        # Iph应接近Isc
        self.assertAlmostEqual(result['Iph'], self.Isc, delta=self.Isc*0.1)
        
        # Rs应较小
        self.assertLess(result['Rs'], 1.0)
        
        # Rsh应较大
        self.assertGreater(result['Rsh'], 10)
        
        # n应在1-2之间
        self.assertGreater(result['n'], 1.0)
        self.assertLess(result['n'], 2.0)


class TestParameterComparator(unittest.TestCase):
    """参数对比器测试"""
    
    def setUp(self):
        self.comparator = ParameterComparator()
        
        # 生成测试数据
        cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
        self.V_test, self.I_test = cell.get_iv_curve(50)
    
    def test_compare_methods(self):
        """测试方法对比"""
        results = self.comparator.compare_methods(
            self.V_test, self.I_test
        )
        
        self.assertIn('key_points', results)
        self.assertIn('least_squares', results)
        
        # 至少有一个方法成功
        success_count = sum(1 for r in results.values() 
                          if r and r.get('success', True))
        self.assertGreater(success_count, 0)
    
    def test_evaluate_accuracy(self):
        """测试精度评估"""
        # 先提取参数
        extractor = ParameterExtractor()
        params = extractor.extract_from_curve(self.V_test, self.I_test)
        
        # 评估精度
        accuracy = self.comparator.evaluate_accuracy(
            params, self.V_test, self.I_test
        )
        
        self.assertIn('mae', accuracy)
        self.assertIn('rmse', accuracy)
        self.assertIn('r2', accuracy)
        
        # R²应较高
        self.assertGreater(accuracy['r2'], 0.85)


class TestOnlineIdentification(unittest.TestCase):
    """在线辨识测试"""
    
    def setUp(self):
        self.initial_params = {
            'Iph': 8.0,
            'I0': 1e-9,
            'Rs': 0.005,
            'Rsh': 1000.0,
            'n': 1.3
        }
        self.identifier = OnlineIdentification(self.initial_params)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(len(self.identifier.history), 0)
        self.assertEqual(self.identifier.params['Iph'], 8.0)
    
    def test_update(self):
        """测试参数更新"""
        params_updated = self.identifier.update(0.5, 7.0)
        
        self.assertIn('Iph', params_updated)
        self.assertEqual(len(self.identifier.history), 1)


def run_tests():
    """运行所有测试"""
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
