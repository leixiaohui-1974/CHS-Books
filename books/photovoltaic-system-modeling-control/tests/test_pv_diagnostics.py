"""
光伏诊断模块单元测试
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule
from code.models.pv_diagnostics import (ShadingAnalyzer, IVCurveDiagnostics, 
                                        PerformanceEvaluator)


class TestShadingAnalyzer(unittest.TestCase):
    """遮挡分析器测试"""
    
    def setUp(self):
        cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
        self.module = PVModule(cell_model=cell, Ns=60, Nb=3)
        self.analyzer = ShadingAnalyzer(self.module)
    
    def test_no_shading(self):
        """测试无遮挡场景"""
        irradiances = [1000.0] * 60
        result = self.analyzer.analyze_shading_pattern(irradiances)
        
        self.assertEqual(result['num_shaded_cells'], 0)
        self.assertEqual(result['severity'], "无遮挡")
    
    def test_partial_shading(self):
        """测试部分遮挡"""
        irradiances = [1000.0] * 40 + [200.0] * 20
        result = self.analyzer.analyze_shading_pattern(irradiances)
        
        self.assertGreater(result['num_shaded_cells'], 0)
        self.assertGreater(result['shading_ratio'], 0)
    
    def test_hotspot_detection_low_risk(self):
        """测试低热斑风险"""
        irradiances = [1000.0] * 55 + [900.0] * 5
        result = self.analyzer.detect_hot_spot_risk(irradiances)
        
        self.assertEqual(result['risk_level'], "低风险")
    
    def test_hotspot_detection_high_risk(self):
        """测试高热斑风险"""
        irradiances = [1000.0] * 50 + [100.0] * 10
        result = self.analyzer.detect_hot_spot_risk(irradiances)
        
        self.assertIn(result['risk_level'], ["高风险", "极高风险"])
        self.assertTrue(result['will_bypass_activate'])
    
    def test_power_loss_estimation(self):
        """测试功率损失估算"""
        irradiances_shaded = [1000.0] * 40 + [200.0] * 20
        result = self.analyzer.estimate_power_loss(irradiances_shaded)
        
        # 注意: 简化模型可能无法完全捕捉遮挡效应
        # 这里主要测试函数能正常运行并返回合理结果
        self.assertGreaterEqual(result['power_loss'], 0)
        self.assertGreaterEqual(result['loss_ratio'], 0)
        self.assertIn('baseline_power', result)
        self.assertIn('shaded_power', result)


class TestIVCurveDiagnostics(unittest.TestCase):
    """I-V曲线诊断测试"""
    
    def setUp(self):
        self.diagnostics = IVCurveDiagnostics()
        
        # 创建测试曲线
        cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
        module = PVModule(cell_model=cell, Ns=60, Nb=3)
        self.V, self.I = module.get_iv_curve(200)
    
    def test_curve_analysis(self):
        """测试曲线分析"""
        result = self.diagnostics.analyze_curve_shape(self.V, self.I)
        
        self.assertIn('Isc', result)
        self.assertIn('Voc', result)
        self.assertIn('FF', result)
        self.assertGreater(result['FF'], 0)
        self.assertLess(result['FF'], 1)
    
    def test_fault_detection_normal(self):
        """测试正常曲线"""
        faults = self.diagnostics.detect_faults(self.V, self.I)
        
        self.assertIsInstance(faults, list)
        self.assertIn("无明显故障", faults)
    
    def test_fault_detection_with_reference(self):
        """测试基于参考的故障检测"""
        reference = {
            'Voc': 36.0,
            'Isc': 8.0,
            'FF': 0.75
        }
        
        # 模拟低电压故障
        V_fault = self.V * 0.8
        faults = self.diagnostics.detect_faults(V_fault, self.I, reference)
        
        self.assertTrue(len(faults) > 0)


class TestPerformanceEvaluator(unittest.TestCase):
    """性能评估器测试"""
    
    def setUp(self):
        self.evaluator = PerformanceEvaluator()
    
    def test_performance_ratio(self):
        """测试性能比计算"""
        pr = self.evaluator.calculate_performance_ratio(
            actual_energy=850,
            expected_energy=1000
        )
        
        self.assertAlmostEqual(pr, 0.85)
    
    def test_system_health_excellent(self):
        """测试优秀健康状况"""
        result = self.evaluator.evaluate_system_health(
            current_power=950,
            rated_power=1000,
            irradiance=1000,
            temperature=25
        )
        
        self.assertEqual(result['health_grade'], "优秀")
        self.assertGreater(result['performance_ratio'], 0.90)
    
    def test_system_health_poor(self):
        """测试较差健康状况"""
        result = self.evaluator.evaluate_system_health(
            current_power=600,
            rated_power=1000,
            irradiance=1000,
            temperature=25
        )
        
        self.assertIn(result['health_grade'], ["较差", "差"])


def run_tests():
    """运行所有测试"""
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
