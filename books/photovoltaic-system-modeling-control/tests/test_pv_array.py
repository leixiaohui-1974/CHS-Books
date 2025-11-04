"""
光伏阵列模型单元测试
Unit Tests for PV Array Model
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule
from code.models.pv_array import PVArray, CombinerBox


class TestPVArray(unittest.TestCase):
    """光伏阵列测试"""
    
    def setUp(self):
        # 创建标准电池和组件
        cell = SingleDiodeModel(
            Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
            T=298.15, G=1000.0
        )
        self.module = PVModule(cell_model=cell, Ns=60, Nb=3)
        self.vmpp_m, self.impp_m, self.pmpp_m = self.module.find_mpp()
    
    def test_single_string_single_module(self):
        """测试1串1组件配置"""
        array = PVArray(module=self.module, Ns=1, Np=1)
        
        self.assertEqual(array.Ns, 1)
        self.assertEqual(array.Np, 1)
        self.assertEqual(array.total_modules, 1)
        
        # 参数应与单个组件相同
        self.assertAlmostEqual(array.Voc, self.module.Voc, delta=0.1)
        self.assertAlmostEqual(array.Isc, self.module.Isc, delta=0.1)
    
    def test_series_connection(self):
        """测试串联特性"""
        Ns = 10
        array = PVArray(module=self.module, Ns=Ns, Np=1)
        
        # 串联: 电压 × Ns, 电流不变
        self.assertAlmostEqual(array.Voc, self.module.Voc * Ns, delta=1.0)
        self.assertAlmostEqual(array.Isc, self.module.Isc, delta=0.1)
        
        vmpp, impp, pmpp = array.find_mpp()
        self.assertAlmostEqual(vmpp, self.vmpp_m * Ns, delta=vmpp*0.05)
        self.assertAlmostEqual(impp, self.impp_m, delta=0.5)
    
    def test_parallel_connection(self):
        """测试并联特性"""
        Np = 10
        array = PVArray(module=self.module, Ns=1, Np=Np)
        
        # 并联: 电流 × Np, 电压不变
        self.assertAlmostEqual(array.Voc, self.module.Voc, delta=0.1)
        self.assertAlmostEqual(array.Isc, self.module.Isc * Np, delta=1.0)
        
        vmpp, impp, pmpp = array.find_mpp()
        self.assertAlmostEqual(vmpp, self.vmpp_m, delta=1.0)
        self.assertAlmostEqual(impp, self.impp_m * Np, delta=impp*0.05)
    
    def test_series_parallel_combination(self):
        """测试串并联组合"""
        Ns, Np = 20, 5
        array = PVArray(module=self.module, Ns=Ns, Np=Np)
        
        self.assertEqual(array.total_modules, Ns * Np)
        
        # 验证电压电流
        self.assertAlmostEqual(array.Voc, self.module.Voc * Ns, delta=array.Voc*0.02)
        self.assertAlmostEqual(array.Isc, self.module.Isc * Np, delta=array.Isc*0.02)
    
    def test_power_scaling(self):
        """测试功率缩放"""
        configs = [(1, 1), (10, 1), (1, 10), (10, 10)]
        
        for Ns, Np in configs:
            array = PVArray(module=self.module, Ns=Ns, Np=Np)
            _, _, pmpp = array.find_mpp()
            
            expected_power = self.pmpp_m * Ns * Np
            # 允许5%误差
            self.assertAlmostEqual(pmpp, expected_power, delta=expected_power*0.05)
    
    def test_iv_curve_generation(self):
        """测试I-V曲线生成"""
        array = PVArray(module=self.module, Ns=10, Np=5)
        V, I = array.get_iv_curve(100)
        
        self.assertEqual(len(V), 100)
        self.assertEqual(len(I), 100)
        
        # 检查边界
        self.assertGreater(I[0], 0)
        self.assertAlmostEqual(I[-1], 0, delta=1.0)
    
    def test_pv_curve_generation(self):
        """测试P-V曲线生成"""
        array = PVArray(module=self.module, Ns=10, Np=5)
        V, P = array.get_pv_curve(100)
        
        self.assertEqual(len(V), 100)
        self.assertEqual(len(P), 100)
        
        # 功率应非负
        self.assertTrue(np.all(P >= 0))
        
        # 存在最大值
        max_power = np.max(P)
        self.assertGreater(max_power, 0)
    
    def test_mpp_finding(self):
        """测试MPP寻找"""
        array = PVArray(module=self.module, Ns=20, Np=10)
        vmpp, impp, pmpp = array.find_mpp()
        
        # MPP应在合理范围
        self.assertGreater(vmpp, 0)
        self.assertLess(vmpp, array.Voc)
        self.assertGreater(impp, 0)
        self.assertLess(impp, array.Isc)
        self.assertGreater(pmpp, 0)
        
        # 功率一致性
        self.assertAlmostEqual(pmpp, vmpp * impp, delta=1.0)
    
    def test_get_parameters(self):
        """测试参数获取"""
        array = PVArray(module=self.module, Ns=25, Np=10, name="Test Array")
        params = array.get_parameters()
        
        self.assertEqual(params['name'], "Test Array")
        self.assertEqual(params['Ns'], 25)
        self.assertEqual(params['Np'], 10)
        self.assertEqual(params['total_modules'], 250)
        self.assertIn('Vmpp', params)
        self.assertIn('Pmpp_kW', params)
        self.assertIn('FF', params)
    
    def test_calculate_system_size(self):
        """测试系统规模计算"""
        array = PVArray(module=self.module, Ns=25, Np=200)  # ~1MW
        size_info = array.calculate_system_size(module_area=1.6)
        
        self.assertEqual(size_info['module_area'], 1.6)
        self.assertGreater(size_info['total_area'], 0)
        self.assertGreater(size_info['power_kW'], 0)
        self.assertGreater(size_info['efficiency'], 0)
        self.assertLess(size_info['efficiency'], 100)
    
    def test_large_scale_array(self):
        """测试大规模阵列(MW级)"""
        # 1MW阵列
        array = PVArray(module=self.module, Ns=25, Np=200)
        
        self.assertEqual(array.total_modules, 5000)
        
        _, _, pmpp = array.find_mpp()
        pmpp_MW = pmpp / 1e6
        
        # 功率应接近1MW
        self.assertGreater(pmpp_MW, 0.9)
        self.assertLess(pmpp_MW, 1.2)


class TestCombinerBox(unittest.TestCase):
    """汇流箱测试"""
    
    def test_initialization(self):
        """测试初始化"""
        cb = CombinerBox(num_strings=10, name="CB-1")
        
        self.assertEqual(cb.num_strings, 10)
        self.assertEqual(cb.name, "CB-1")
        self.assertTrue(cb.has_fuses)
        self.assertTrue(cb.has_surge_protector)
        self.assertTrue(cb.has_breaker)
    
    def test_get_specifications(self):
        """测试规格获取"""
        cb = CombinerBox(num_strings=16)
        specs = cb.get_specifications()
        
        self.assertEqual(specs['num_strings'], 16)
        self.assertIn('fuses', specs)
        self.assertIn('surge_protector', specs)


def run_tests():
    """运行所有测试"""
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
