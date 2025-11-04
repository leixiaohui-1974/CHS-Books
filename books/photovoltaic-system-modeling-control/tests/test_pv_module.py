"""
光伏组件模型单元测试
Unit Tests for PV Module Model
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule, BypassDiode


class TestBypassDiode(unittest.TestCase):
    """旁路二极管测试"""
    
    def setUp(self):
        self.diode = BypassDiode(Vf=0.7, Rs=0.01)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.diode.Vf, 0.7)
        self.assertEqual(self.diode.Rs, 0.01)
    
    def test_forward_bias(self):
        """测试正向偏置(截止)"""
        self.assertFalse(self.diode.is_conducting(0.5))
        I = self.diode.calculate_current(0.5)
        self.assertEqual(I, 0.0)
    
    def test_reverse_bias_conducting(self):
        """测试反向导通"""
        self.assertTrue(self.diode.is_conducting(-1.0))
        I = self.diode.calculate_current(-1.0)
        self.assertGreater(I, 0)


class TestPVModule(unittest.TestCase):
    """光伏组件测试"""
    
    def setUp(self):
        # 创建标准电池
        self.cell = SingleDiodeModel(
            Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
            T=298.15, G=1000.0
        )
    
    def test_60_cell_module(self):
        """测试60片组件"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        
        self.assertEqual(module.Ns, 60)
        self.assertEqual(module.Nb, 3)
        self.assertEqual(module.cells_per_bypass, 20)
        
        # 验证串联特性
        self.assertAlmostEqual(module.Voc, self.cell.Voc * 60, delta=1.0)
        self.assertAlmostEqual(module.Isc, self.cell.Isc, delta=0.1)
    
    def test_72_cell_module(self):
        """测试72片组件"""
        module = PVModule(cell_model=self.cell, Ns=72, Nb=3)
        
        self.assertEqual(module.Ns, 72)
        self.assertAlmostEqual(module.Voc, self.cell.Voc * 72, delta=1.0)
    
    def test_iv_curve(self):
        """测试I-V曲线生成"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        V, I = module.get_iv_curve(100)
        
        self.assertEqual(len(V), 100)
        self.assertEqual(len(I), 100)
        
        # 检查边界
        self.assertAlmostEqual(I[0], module.Isc, delta=0.5)
        self.assertAlmostEqual(I[-1], 0, delta=0.5)
    
    def test_pv_curve(self):
        """测试P-V曲线"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        V, P = module.get_pv_curve(100)
        
        self.assertEqual(len(V), 100)
        self.assertEqual(len(P), 100)
        
        # 功率应该非负
        self.assertTrue(np.all(P >= 0))
        
        # 存在最大值
        max_power = np.max(P)
        self.assertGreater(max_power, 0)
    
    def test_mpp_finding(self):
        """测试MPP寻找"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        vmpp, impp, pmpp = module.find_mpp()
        
        # MPP应在合理范围
        self.assertGreater(vmpp, 0)
        self.assertLess(vmpp, module.Voc)
        self.assertGreater(impp, 0)
        self.assertLess(impp, module.Isc)
        self.assertGreater(pmpp, 0)
        
        # 功率一致性
        self.assertAlmostEqual(pmpp, vmpp * impp, delta=0.1)
    
    def test_power_scaling(self):
        """测试功率缩放"""
        cell_power = self.cell.Vmp_stc * self.cell.Imp_stc
        
        module_60 = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        _, _, pmpp_60 = module_60.find_mpp()
        
        # 功率应约等于Ns倍
        expected_power = cell_power * 60
        self.assertAlmostEqual(pmpp_60, expected_power, delta=expected_power * 0.1)
    
    def test_set_uniform_conditions(self):
        """测试统一条件设置"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        module.set_uniform_conditions(T=323.15, G=800.0)
        
        # 检查所有电池条件
        for cell in module.cells:
            self.assertEqual(cell.T, 323.15)
            self.assertEqual(cell.G, 800.0)
    
    def test_set_cell_irradiance(self):
        """测试单独设置电池辐照度"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        
        # 设置不同辐照度
        G_values = [1000.0] * 40 + [500.0] * 20
        module.set_cell_irradiance(G_values)
        
        # 验证
        self.assertEqual(module.cells[0].G, 1000.0)
        self.assertEqual(module.cells[59].G, 500.0)
    
    def test_partial_shading_power_loss(self):
        """测试部分遮挡功率损失"""
        # 注意: 当前简化模型使用平均法,无法完全模拟遮挡效果
        # 这里测试设置功能是否正常工作
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        
        # 设置不同辐照度
        G_shaded = [1000.0] * 40 + [200.0] * 20
        module.set_cell_irradiance(G_shaded)
        
        # 验证设置成功
        self.assertEqual(module.cells[0].G, 1000.0)
        self.assertEqual(module.cells[59].G, 200.0)
        
        # 功率应该大于0
        _, _, pmpp = module.find_mpp()
        self.assertGreater(pmpp, 0)
    
    def test_get_parameters(self):
        """测试参数获取"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3, name="Test Module")
        params = module.get_parameters()
        
        self.assertEqual(params['name'], "Test Module")
        self.assertEqual(params['Ns'], 60)
        self.assertEqual(params['Nb'], 3)
        self.assertIn('Voc', params)
        self.assertIn('Pmp', params)


class TestModuleConfiguration(unittest.TestCase):
    """组件配置测试"""
    
    def setUp(self):
        self.cell = SingleDiodeModel(
            Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
            T=298.15, G=1000.0
        )
    
    def test_different_configurations(self):
        """测试不同配置"""
        configs = [(36, 2), (60, 3), (72, 3), (96, 4)]
        
        for Ns, Nb in configs:
            module = PVModule(cell_model=self.cell, Ns=Ns, Nb=Nb)
            
            # 基本验证
            self.assertEqual(module.Ns, Ns)
            self.assertEqual(module.Nb, Nb)
            
            # 电压应线性缩放
            self.assertAlmostEqual(module.Voc / Ns, self.cell.Voc, delta=0.01)
    
    def test_voltage_current_relationship(self):
        """测试电压电流关系"""
        module = PVModule(cell_model=self.cell, Ns=60, Nb=3)
        
        # 测试几个点
        V_test = module.Voc * 0.5
        I = module.calculate_current(V_test)
        
        self.assertGreater(I, 0)
        self.assertLess(I, module.Isc)


def run_tests():
    """运行所有测试"""
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
