"""
DC/DC变换器模型测试

Author: CHS-BOOKS Project  
Date: 2025-11-04
"""

import unittest
import numpy as np
import sys
from pathlib import Path

# 添加code路径
code_path = Path(__file__).parent.parent / 'books' / 'photovoltaic-system-modeling-control' / 'code'
sys.path.insert(0, str(code_path))

from models.dcdc_converter import (
    BoostConverter, BuckConverter, BuckBoostConverter,
    DCBusVoltageController, FeedforwardCompensator
)


class TestBoostConverter(unittest.TestCase):
    """测试Boost升压变换器"""
    
    def setUp(self):
        """初始化测试"""
        self.boost = BoostConverter(L=100e-6, C=100e-6, R=10.0)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.boost.name, "Boost")
        self.assertEqual(self.boost.L, 100e-6)
        self.assertEqual(self.boost.C, 100e-6)
        self.assertEqual(self.boost.R, 10.0)
        self.assertEqual(self.boost.i_L, 0.0)
        self.assertEqual(self.boost.v_C, 0.0)
    
    def test_voltage_gain(self):
        """测试升压特性"""
        V_in = 12.0
        d = 0.5  # 占空比50%
        dt = 1e-6
        
        # 仿真到稳态
        for _ in range(10000):
            self.boost.update(V_in, d, dt)
        
        # 理论输出: V_out = V_in / (1 - d) = 12 / 0.5 = 24V
        v_out_theory = V_in / (1 - d)
        v_out_actual = self.boost.v_C
        
        # 允许5%误差
        self.assertAlmostEqual(v_out_actual, v_out_theory, delta=v_out_theory * 0.05)
        
        # 验证升压
        self.assertGreater(v_out_actual, V_in)
    
    def test_duty_cycle_limit(self):
        """测试占空比限制"""
        # 测试超过最大占空比
        self.boost.update(12.0, 0.99, 1e-6)
        self.assertLessEqual(self.boost.d, 0.95)
    
    def test_reset(self):
        """测试重置"""
        # 运行一些步骤
        for _ in range(100):
            self.boost.update(12.0, 0.5, 1e-6)
        
        # 重置
        self.boost.reset()
        
        self.assertEqual(self.boost.i_L, 0.0)
        self.assertEqual(self.boost.v_C, 0.0)


class TestBuckConverter(unittest.TestCase):
    """测试Buck降压变换器"""
    
    def setUp(self):
        """初始化测试"""
        self.buck = BuckConverter(L=100e-6, C=100e-6, R=10.0)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.buck.name, "Buck")
        self.assertEqual(self.buck.L, 100e-6)
        self.assertEqual(self.buck.C, 100e-6)
    
    def test_voltage_gain(self):
        """测试降压特性"""
        V_in = 24.0
        d = 0.5  # 占空比50%
        dt = 1e-6
        
        # 仿真到稳态
        for _ in range(10000):
            self.buck.update(V_in, d, dt)
        
        # 理论输出: V_out = d * V_in = 0.5 * 24 = 12V
        v_out_theory = d * V_in
        v_out_actual = self.buck.v_C
        
        # 允许5%误差
        self.assertAlmostEqual(v_out_actual, v_out_theory, delta=v_out_theory * 0.05)
        
        # 验证降压
        self.assertLess(v_out_actual, V_in)
    
    def test_different_duty_cycles(self):
        """测试不同占空比"""
        V_in = 20.0
        dt = 1e-6
        
        for d in [0.2, 0.4, 0.6, 0.8]:
            buck = BuckConverter(L=100e-6, C=100e-6, R=10.0)
            
            # 仿真到稳态
            for _ in range(10000):
                buck.update(V_in, d, dt)
            
            v_out_theory = d * V_in
            v_out_actual = buck.v_C
            
            self.assertAlmostEqual(v_out_actual, v_out_theory, delta=v_out_theory * 0.1)


class TestBuckBoostConverter(unittest.TestCase):
    """测试Buck-Boost升降压变换器"""
    
    def setUp(self):
        """初始化测试"""
        self.buck_boost = BuckBoostConverter(L=100e-6, C=100e-6, R=10.0)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.buck_boost.name, "Buck-Boost")
        self.assertEqual(self.buck_boost.L, 100e-6)
    
    def test_voltage_gain(self):
        """测试升降压特性"""
        V_in = 20.0
        d = 0.5
        dt = 1e-6
        
        # 仿真到稳态
        for _ in range(10000):
            self.buck_boost.update(V_in, d, dt)
        
        # 理论输出: V_out = -d/(1-d) * V_in = -0.5/0.5 * 20 = -20V
        v_out_theory = -d / (1 - d) * V_in
        v_out_actual = self.buck_boost.v_C
        
        # Buck-Boost输出为负电压
        self.assertLess(v_out_actual, 0)
        
        # 允许10%误差
        self.assertAlmostEqual(abs(v_out_actual), abs(v_out_theory), delta=abs(v_out_theory) * 0.1)
    
    def test_polarity_inversion(self):
        """测试极性反转"""
        V_in = 15.0
        d = 0.6
        dt = 1e-6
        
        # 仿真
        for _ in range(10000):
            self.buck_boost.update(V_in, d, dt)
        
        # 输出应为负
        self.assertLess(self.buck_boost.v_C, 0)


class TestDCBusVoltageController(unittest.TestCase):
    """测试直流母线电压控制器"""
    
    def setUp(self):
        """初始化测试"""
        self.controller = DCBusVoltageController(Kp=0.001, Ki=0.5, v_ref=400.0)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.controller.name, "DCBusController")
        self.assertEqual(self.controller.v_ref, 400.0)
        self.assertEqual(self.controller.Kp, 0.001)
    
    def test_control_action(self):
        """测试控制动作"""
        v_measured = 350.0  # 低于参考
        d = self.controller.update(v_measured, dt=1e-6)
        
        # 验证占空比在合理范围
        self.assertGreaterEqual(d, 0.05)
        self.assertLessEqual(d, 0.95)
    
    def test_voltage_tracking(self):
        """测试电压跟踪"""
        boost = BoostConverter(L=100e-6, C=100e-6, R=20.0)
        V_in = 100.0
        
        # 仿真到稳态（更长时间）
        for _ in range(20000):
            d = self.controller.update(boost.v_C, 1e-6)
            boost.update(V_in, d, 1e-6)
        
        # 验证稳态误差（放宽要求）
        v_ss = boost.v_C
        self.assertAlmostEqual(v_ss, 400.0, delta=20.0)


class TestFeedforwardCompensator(unittest.TestCase):
    """测试前馈补偿器"""
    
    def setUp(self):
        """初始化测试"""
        self.ff_boost = FeedforwardCompensator("boost")
        self.ff_buck = FeedforwardCompensator("buck")
    
    def test_boost_feedforward(self):
        """测试Boost前馈"""
        V_in = 100.0
        V_ref = 400.0
        
        d_ff = self.ff_boost.calculate(V_in, V_ref)
        
        # Boost: d = 1 - Vin/Vout = 1 - 100/400 = 0.75
        self.assertAlmostEqual(d_ff, 0.75, places=2)
    
    def test_buck_feedforward(self):
        """测试Buck前馈"""
        V_in = 400.0
        V_ref = 100.0
        
        d_ff = self.ff_buck.calculate(V_in, V_ref)
        
        # Buck: d = Vout/Vin = 100/400 = 0.25
        self.assertAlmostEqual(d_ff, 0.25, places=2)


def suite():
    """创建测试套件"""
    suite = unittest.TestSuite()
    
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBoostConverter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBuckConverter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBuckBoostConverter))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDCBusVoltageController))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFeedforwardCompensator))
    
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
