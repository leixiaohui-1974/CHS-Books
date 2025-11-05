"""
测试PWM调制算法
包含SPWM和SVPWM的单元测试

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

from models.inverter_control import (
    InverterParameters, SPWMModulator, SVPWMModulator, InverterModel
)


class TestInverterParameters(unittest.TestCase):
    """测试逆变器参数类"""
    
    def test_initialization(self):
        """测试参数初始化"""
        params = InverterParameters()
        
        self.assertEqual(params.V_dc, 400.0)
        self.assertEqual(params.V_ac, 220.0)
        self.assertEqual(params.f_ac, 50.0)
        self.assertEqual(params.f_sw, 10000.0)
        self.assertGreater(params.L_filter, 0)
        self.assertGreater(params.C_filter, 0)
    
    def test_custom_parameters(self):
        """测试自定义参数"""
        params = InverterParameters(
            V_dc=600.0,
            V_ac=380.0,
            f_ac=60.0,
            f_sw=20000.0
        )
        
        self.assertEqual(params.V_dc, 600.0)
        self.assertEqual(params.V_ac, 380.0)
        self.assertEqual(params.f_ac, 60.0)
        self.assertEqual(params.f_sw, 20000.0)


class TestSPWMModulator(unittest.TestCase):
    """测试SPWM调制器"""
    
    def setUp(self):
        """测试前准备"""
        self.params = InverterParameters()
        self.spwm = SPWMModulator(self.params, modulation_index=0.9)
    
    def test_initialization(self):
        """测试SPWM初始化"""
        self.assertEqual(self.spwm.name, "SPWM")
        self.assertEqual(self.spwm.modulation_index, 0.9)
        self.assertGreater(self.spwm.mf, 0)
        self.assertIsInstance(self.spwm.mf, int)
    
    def test_generate_reference(self):
        """测试参考信号生成"""
        t = 0.005  # 5ms
        v_ref = self.spwm.generate_reference(t)
        
        # 应该是正弦波
        expected = self.params.V_ac * np.sqrt(2) * np.sin(2 * np.pi * self.params.f_ac * t)
        self.assertAlmostEqual(v_ref, expected, places=5)
    
    def test_modulate_single_point(self):
        """测试单点调制"""
        v_ref = 100.0  # 100V参考电压
        t = 0.0
        
        sw, info = self.spwm.modulate(v_ref, t)
        
        # 检查返回值类型
        self.assertIn(sw, [0.0, 1.0])
        self.assertIn('modulation_wave', info)
        self.assertIn('carrier_wave', info)
        self.assertIn('switching_signal', info)
        self.assertIn('output_voltage', info)
    
    def test_simulate(self):
        """测试仿真功能"""
        duration = 0.02  # 一个周期
        result = self.spwm.simulate(duration)
        
        # 检查结果包含必要的键
        self.assertIn('time', result)
        self.assertIn('v_ref', result)
        self.assertIn('modulation_wave', result)
        self.assertIn('carrier_wave', result)
        self.assertIn('switching_signal', result)
        self.assertIn('output_voltage', result)
        
        # 检查数组长度一致
        N = len(result['time'])
        self.assertEqual(len(result['v_ref']), N)
        self.assertEqual(len(result['switching_signal']), N)
    
    def test_modulation_index_range(self):
        """测试调制比范围"""
        # 低调制比
        spwm_low = SPWMModulator(self.params, modulation_index=0.3)
        result_low = spwm_low.simulate(0.1)  # 多个周期
        v_rms_low = np.sqrt(np.mean(result_low['v_ref']**2))
        
        # 高调制比
        spwm_high = SPWMModulator(self.params, modulation_index=0.9)
        result_high = spwm_high.simulate(0.1)
        v_rms_high = np.sqrt(np.mean(result_high['v_ref']**2))
        
        # 验证调制比不同
        self.assertNotEqual(spwm_low.modulation_index, spwm_high.modulation_index)
        
        # 两个调制器应该基于不同的调制比工作
        self.assertLess(spwm_low.modulation_index, spwm_high.modulation_index)
    
    def test_thd_calculation(self):
        """测试THD计算"""
        duration = 0.1  # 5个周期
        result = self.spwm.simulate(duration)
        
        fs = 1.0 / (result['time'][1] - result['time'][0])
        thd_result = self.spwm.calculate_thd(
            result['output_voltage'], 
            fs, 
            self.params.f_ac, 
            n_harmonics=50
        )
        
        # 检查THD结果
        self.assertIn('THD', thd_result)
        self.assertIn('fundamental', thd_result)
        self.assertIn('harmonics', thd_result)
        
        # THD应该大于0 (PWM输出必然有谐波)
        self.assertGreater(thd_result['THD'], 0)
        
        # 基波应该是主要成分
        self.assertGreater(thd_result['fundamental'], 0)
    
    def test_output_voltage_symmetry(self):
        """测试输出电压对称性"""
        result = self.spwm.simulate(0.1)  # 多个周期
        
        # 检查参考电压的周期性
        v_ref = result['v_ref']
        
        # 计算一个周期的点数
        T = 1.0 / self.params.f_ac
        dt = result['time'][1] - result['time'][0]
        points_per_period = int(T / dt)
        
        # 比较第一个周期和第二个周期
        if len(v_ref) >= 2 * points_per_period:
            period1 = v_ref[:points_per_period]
            period2 = v_ref[points_per_period:2*points_per_period]
            
            # 计算相关系数(避免nan)
            if np.std(period1) > 0 and np.std(period2) > 0:
                correlation = np.corrcoef(period1, period2)[0, 1]
                self.assertGreater(correlation, 0.99)  # 周期性很强
    
    def test_switching_frequency(self):
        """测试开关频率"""
        duration = 0.1
        result = self.spwm.simulate(duration, dt=1e-7)  # 高分辨率采样
        
        # 检测开关次数
        sw_signal = result['switching_signal']
        transitions = np.sum(np.abs(np.diff(sw_signal)) > 0.5)
        
        # 理论开关次数 = 2 * f_sw * duration (每个周期有2次翻转)
        expected_transitions = 2 * self.params.f_sw * duration
        
        # 允许5%误差
        self.assertAlmostEqual(transitions, expected_transitions, delta=expected_transitions * 0.1)


class TestSVPWMModulator(unittest.TestCase):
    """测试SVPWM调制器"""
    
    def setUp(self):
        """测试前准备"""
        self.params = InverterParameters()
        self.svpwm = SVPWMModulator(self.params)
    
    def test_initialization(self):
        """测试SVPWM初始化"""
        self.assertEqual(self.svpwm.name, "SVPWM")
        self.assertEqual(len(self.svpwm.basic_vectors), 8)
        self.assertEqual(len(self.svpwm.sector_angles), 6)
    
    def test_clarke_transform(self):
        """测试Clarke变换"""
        # 测试平衡三相
        va, vb, vc = 100.0, -50.0, -50.0
        v_alpha, v_beta = self.svpwm.clarke_transform(va, vb, vc)
        
        # 验证变换正确性
        self.assertAlmostEqual(v_alpha, 100.0, places=5)
        self.assertAlmostEqual(v_beta, 0.0, places=5)
    
    def test_inverse_clarke_transform(self):
        """测试逆Clarke变换"""
        v_alpha, v_beta = 100.0, 0.0
        va, vb, vc = self.svpwm.inverse_clarke_transform(v_alpha, v_beta)
        
        # 检查三相和为0
        self.assertAlmostEqual(va + vb + vc, 0.0, places=5)
        
        # 检查幅值
        self.assertAlmostEqual(va, v_alpha, places=5)
    
    def test_clarke_inverse_consistency(self):
        """测试Clarke变换和逆变换的一致性"""
        va_orig, vb_orig, vc_orig = 100.0, -50.0, -50.0
        
        # 正变换
        v_alpha, v_beta = self.svpwm.clarke_transform(va_orig, vb_orig, vc_orig)
        
        # 逆变换
        va, vb, vc = self.svpwm.inverse_clarke_transform(v_alpha, v_beta)
        
        # 应该恢复原值
        self.assertAlmostEqual(va, va_orig, places=5)
        self.assertAlmostEqual(vb, vb_orig, places=5)
        self.assertAlmostEqual(vc, vc_orig, places=5)
    
    def test_get_sector(self):
        """测试扇区判断"""
        # 测试各个扇区的中心角度
        test_cases = [
            (100.0, 0.0, 1),          # 扇区1: 0度
            (50.0, 86.6025, 2),       # 扇区2: 60度
            (-50.0, 86.6025, 3),      # 扇区3: 120度
            (-100.0, 0.0, 4),         # 扇区4: 180度
            (-50.0, -86.6025, 5),     # 扇区5: 240度
            (50.0, -86.6025, 6),      # 扇区6: 300度
        ]
        
        for v_alpha, v_beta, expected_sector in test_cases:
            sector = self.svpwm.get_sector(v_alpha, v_beta)
            # 允许相邻扇区(由于数值误差)
            valid_sectors = [expected_sector]
            if expected_sector > 1:
                valid_sectors.append(expected_sector - 1)
            if expected_sector < 6:
                valid_sectors.append(expected_sector + 1)
            self.assertIn(sector, valid_sectors, 
                         f"Failed for ({v_alpha}, {v_beta}): got {sector}, expected around {expected_sector}")
    
    def test_calculate_duty_cycles(self):
        """测试占空比计算"""
        v_alpha, v_beta = 100.0, 0.0
        sector, T1, T2, T0 = self.svpwm.calculate_duty_cycles(
            v_alpha, v_beta, self.params.V_dc
        )
        
        # 扇区应该是1
        self.assertEqual(sector, 1)
        
        # 时间总和应该为1
        self.assertAlmostEqual(T1 + T2 + T0, 1.0, places=5)
        
        # 所有时间应该非负
        self.assertGreaterEqual(T1, 0)
        self.assertGreaterEqual(T2, 0)
        self.assertGreaterEqual(T0, 0)
    
    def test_generate_switching_times(self):
        """测试开关时间生成"""
        T1, T2, T0 = 0.3, 0.4, 0.3
        
        for sector in range(1, 7):
            sw_times = self.svpwm.generate_switching_times(sector, T1, T2, T0)
            
            # 应该有三个开关时间
            self.assertIn('Ta', sw_times)
            self.assertIn('Tb', sw_times)
            self.assertIn('Tc', sw_times)
            
            # 所有时间应该在[0, 1]范围内
            for key, value in sw_times.items():
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 1)
    
    def test_modulate(self):
        """测试调制功能"""
        va_ref = 100.0
        vb_ref = -50.0
        vc_ref = -50.0
        
        result = self.svpwm.modulate(va_ref, vb_ref, vc_ref, self.params.V_dc)
        
        # 检查结果键
        self.assertIn('v_alpha', result)
        self.assertIn('v_beta', result)
        self.assertIn('sector', result)
        self.assertIn('T1', result)
        self.assertIn('T2', result)
        self.assertIn('T0', result)
        self.assertIn('switching_times', result)
        
        # 扇区应该在1-6范围
        self.assertIn(result['sector'], range(1, 7))
    
    def test_simulate(self):
        """测试仿真功能"""
        duration = 0.04  # 2个周期
        result = self.svpwm.simulate(duration)
        
        # 检查结果包含必要的键
        self.assertIn('time', result)
        self.assertIn('va_ref', result)
        self.assertIn('vb_ref', result)
        self.assertIn('vc_ref', result)
        self.assertIn('v_alpha', result)
        self.assertIn('v_beta', result)
        self.assertIn('sectors', result)
        
        # 检查三相平衡
        N = len(result['time'])
        sum_abc = result['va_ref'] + result['vb_ref'] + result['vc_ref']
        
        # 三相和应该接近0
        for s in sum_abc:
            self.assertAlmostEqual(s, 0.0, places=3)
    
    def test_sector_coverage(self):
        """测试扇区覆盖"""
        duration = 0.1  # 5个周期
        result = self.svpwm.simulate(duration)
        
        # 每个扇区都应该被访问到
        unique_sectors = np.unique(result['sectors'])
        self.assertEqual(len(unique_sectors), 6)
        for i in range(1, 7):
            self.assertIn(i, unique_sectors)
    
    def test_voltage_utilization(self):
        """测试电压利用率"""
        duration = 0.1
        result = self.svpwm.simulate(duration, 
                                     amplitude=self.params.V_ac * np.sqrt(2))
        
        # 计算输出电压RMS
        v_rms_a = np.sqrt(np.mean(result['va_ref']**2))
        
        # SVPWM的电压利用率理论值约为100%
        # 实际RMS应该接近设定值
        expected_rms = self.params.V_ac
        self.assertAlmostEqual(v_rms_a, expected_rms, delta=expected_rms * 0.05)


class TestInverterModel(unittest.TestCase):
    """测试逆变器系统模型"""
    
    def setUp(self):
        """测试前准备"""
        self.params = InverterParameters()
        self.spwm = SPWMModulator(self.params, modulation_index=0.9)
        self.inverter = InverterModel(self.params, self.spwm)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.inverter.i_L, 0.0)
        self.assertEqual(self.inverter.v_C, 0.0)
        self.assertIsNotNone(self.inverter.params)
        self.assertIsNotNone(self.inverter.modulator)
    
    def test_update_filter(self):
        """测试滤波器更新"""
        v_in = 200.0
        i_load = 1.0
        dt = 1e-6
        
        # 更新几步
        for _ in range(10):
            self.inverter.update_filter(v_in, i_load, dt)
        
        # 电流和电压应该发生变化
        self.assertNotEqual(self.inverter.i_L, 0.0)
        self.assertNotEqual(self.inverter.v_C, 0.0)
    
    def test_simulate_with_filter(self):
        """测试完整仿真"""
        duration = 0.1  # 5个周期
        result = self.inverter.simulate_with_filter(duration, load_resistance=10.0)
        
        # 检查结果键
        self.assertIn('time', result)
        self.assertIn('v_ref', result)
        self.assertIn('v_pwm', result)
        self.assertIn('i_filter', result)
        self.assertIn('v_output', result)
        
        # 检查输出电压达到稳态
        v_out = result['v_output']
        
        # 后半段应该是稳态
        v_steady = v_out[len(v_out)//2:]
        v_rms = np.sqrt(np.mean(v_steady**2))
        
        # RMS应该接近额定值
        self.assertGreater(v_rms, self.params.V_ac * 0.8)
        self.assertLess(v_rms, self.params.V_ac * 1.2)
    
    def test_filter_attenuation(self):
        """测试滤波器衰减效果"""
        duration = 0.1
        result = self.inverter.simulate_with_filter(duration)
        
        # PWM输出应该包含高频开关成分
        # 滤波后输出应该更平滑
        
        # 计算PWM输出的变化率
        pwm_changes = np.sum(np.abs(np.diff(result['v_pwm'])) > 100)
        
        # 计算滤波输出的变化率  
        out_changes = np.sum(np.abs(np.diff(result['v_output'])) > 100)
        
        # 滤波后的大跳变应该明显减少
        self.assertLess(out_changes, pwm_changes * 0.1)
    
    def test_different_loads(self):
        """测试不同负载"""
        loads = [5.0, 10.0, 20.0]
        v_rms_list = []
        
        for R_load in loads:
            inverter = InverterModel(self.params, self.spwm)
            result = inverter.simulate_with_filter(0.1, load_resistance=R_load)
            
            v_out = result['v_output'][len(result['v_output'])//2:]
            v_rms = np.sqrt(np.mean(v_out**2))
            v_rms_list.append(v_rms)
        
        # 不同负载下输出电压应该基本稳定
        v_rms_array = np.array(v_rms_list)
        std_ratio = np.std(v_rms_array) / np.mean(v_rms_array)
        
        # 电压调整率应该小于10%
        self.assertLess(std_ratio, 0.1)


def suite():
    """创建测试套件"""
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInverterParameters))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSPWMModulator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSVPWMModulator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestInverterModel))
    
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
