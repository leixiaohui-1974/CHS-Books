#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例1单元测试：灌区智能闸站
===========================

测试内容：
1. PID控制器功能测试
2. 数字孪生仿真测试
3. 性能指标测试
4. 智能化等级评估测试

作者：CHS-Books项目
日期：2025-10-31
"""

import unittest
import numpy as np
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

from main import (
    SimplePIDController,
    TrapezoidalChannel,
    IrrigationGateDigitalTwin,
    evaluate_intelligence_level
)


class TestSimplePIDController(unittest.TestCase):
    """测试PID控制器"""
    
    def setUp(self):
        """初始化"""
        self.pid = SimplePIDController(
            Kp=0.5, Ki=0.1, Kd=0.05,
            setpoint=3.0,
            output_limits=(0.2, 2.0)
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.pid.setpoint, 3.0)
        self.assertEqual(self.pid.Kp, 0.5)
        self.assertEqual(self.pid.Ki, 0.1)
        self.assertEqual(self.pid.Kd, 0.05)
    
    def test_proportional_response(self):
        """测试比例响应"""
        # 误差=1.0（目标3.0-实际2.0）
        output = self.pid.update(measured_value=2.0, dt=1.0)
        # 比例项 = 0.5 * 1.0 = 0.5
        self.assertGreater(output, 0.0)
        self.assertLess(output, 2.0)  # 在限幅范围内
    
    def test_integral_windup(self):
        """测试积分饱和"""
        # 连续大误差
        for _ in range(100):
            self.pid.update(measured_value=1.0, dt=1.0)  # 误差=2.0
        
        # 积分项应该被限幅
        self.assertLessEqual(self.pid.integral, self.pid.windup_limit)
        self.assertGreaterEqual(self.pid.integral, -self.pid.windup_limit)
    
    def test_output_limits(self):
        """测试输出限幅"""
        # 极大误差
        output = self.pid.update(measured_value=0.0, dt=1.0)
        self.assertGreaterEqual(output, 0.2)
        self.assertLessEqual(output, 2.0)
    
    def test_zero_error_steady_state(self):
        """测试零误差稳态"""
        # 多次更新在设定值
        for _ in range(10):
            self.pid.update(measured_value=3.0, dt=1.0)
        
        # 再次更新应该保持稳定
        output = self.pid.update(measured_value=3.0, dt=1.0)
        self.assertIsNotNone(output)


class TestTrapezoidalChannel(unittest.TestCase):
    """测试梯形渠道模型"""
    
    def setUp(self):
        """初始化"""
        self.channel = TrapezoidalChannel(
            b=3.0, m=1.5, n=0.025, S0=0.0005, L=1000.0
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.channel.b, 3.0)
        self.assertEqual(self.channel.m, 1.5)
        self.assertEqual(self.channel.n, 0.025)
        self.assertEqual(self.channel.S0, 0.0005)
        self.assertEqual(self.channel.L, 1000.0)
    
    def test_flow_area(self):
        """测试过水面积计算"""
        h = 2.0
        A_expected = (3.0 + 1.5 * 2.0) * 2.0  # (b + m*h)*h
        A_actual = (self.channel.b + self.channel.m * h) * h
        self.assertAlmostEqual(A_expected, A_actual, places=6)
    
    def test_compute_normal_depth(self):
        """测试正常水深计算"""
        Q = 5.0
        h_n = self.channel.compute_normal_depth(Q)
        
        # 正常水深应该为正
        self.assertGreater(h_n, 0.0)
        # 应该在合理范围内（0-10m）
        self.assertLess(h_n, 10.0)
    
    def test_compute_velocity(self):
        """测试流速计算"""
        Q = 5.0
        h = 2.0
        v = self.channel.compute_velocity(Q, h)
        
        # 流速应该为正
        self.assertGreater(v, 0.0)
        # 流速应该在合理范围内（0-5 m/s）
        self.assertLess(v, 5.0)
    
    def test_water_balance(self):
        """测试水量平衡"""
        # 初始水深
        h0 = 2.0
        Q_in = 5.0
        Q_out = 4.8
        dt = 1.0
        
        # 简化水量平衡（dh/dt ≈ (Q_in - Q_out) / A）
        A = (self.channel.b + self.channel.m * h0) * h0
        dh_dt = (Q_in - Q_out) / A
        h1 = h0 + dh_dt * dt
        
        # 水位应该上升（因为Q_in > Q_out）
        self.assertGreater(h1, h0)


class TestDigitalTwin(unittest.TestCase):
    """测试数字孪生仿真"""
    
    def setUp(self):
        """初始化"""
        self.twin = IrrigationGateDigitalTwin()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.twin.h_upstream, 3.0)
        self.assertEqual(self.twin.h_downstream, 2.0)
        self.assertEqual(self.twin.gate_opening, 1.0)
        self.assertEqual(self.twin.t, 0.0)
    
    def test_step_execution(self):
        """测试单步执行"""
        initial_time = self.twin.t
        self.twin.step()
        
        # 时间应该推进
        self.assertGreater(self.twin.t, initial_time)
        
        # 历史记录应该更新
        self.assertGreater(len(self.twin.time_history), 0)
        self.assertGreater(len(self.twin.h_upstream_history), 0)
    
    def test_simulate(self):
        """测试完整仿真"""
        duration = 10.0  # 10秒
        self.twin.simulate(duration=duration, verbose=False)
        
        # 仿真时间应该达到目标
        self.assertGreaterEqual(self.twin.t, duration)
        
        # 历史记录数量应该合理
        expected_steps = int(duration / self.twin.dt)
        self.assertGreaterEqual(len(self.twin.time_history), expected_steps * 0.9)
    
    def test_performance_metrics(self):
        """测试性能指标计算"""
        self.twin.simulate(duration=3600, verbose=False)
        metrics = self.twin.calculate_performance_metrics()
        
        # 检查指标完整性
        self.assertIn('水位波动', metrics)
        self.assertIn('超调量', metrics)
        self.assertIn('稳态误差', metrics)
        self.assertIn('响应时间', metrics)
        
        # 检查指标合理性
        self.assertGreaterEqual(metrics['水位波动'], 0.0)
        self.assertGreaterEqual(metrics['超调量'], 0.0)
        self.assertLessEqual(metrics['稳态误差'], 1.0)


class TestIntelligenceLevel(unittest.TestCase):
    """测试智能化等级评估"""
    
    def test_L3_pass(self):
        """测试L3通过"""
        metrics = {
            '水位波动': 0.05,
            '超调量': 8.0,
            '稳态误差': 0.02,
            '响应时间': 180
        }
        level, passed = evaluate_intelligence_level(metrics)
        self.assertEqual(level, 'L3')
        self.assertTrue(passed)
    
    def test_L2_fail(self):
        """测试L2未通过"""
        metrics = {
            '水位波动': 0.15,  # 超标
            '超调量': 12.0,
            '稳态误差': 0.06,
            '响应时间': 250
        }
        level, passed = evaluate_intelligence_level(metrics)
        self.assertEqual(level, 'L2')
        self.assertFalse(passed)
    
    def test_L1_fail(self):
        """测试L1未通过"""
        metrics = {
            '水位波动': 0.25,
            '超调量': 20.0,
            '稳态误差': 0.15,
            '响应时间': 400
        }
        level, passed = evaluate_intelligence_level(metrics)
        self.assertEqual(level, 'L1')
        self.assertFalse(passed)


def run_tests():
    """运行所有测试"""
    print("="*60)
    print("案例1单元测试")
    print("="*60)
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestSimplePIDController))
    suite.addTests(loader.loadTestsFromTestCase(TestTrapezoidalChannel))
    suite.addTests(loader.loadTestsFromTestCase(TestDigitalTwin))
    suite.addTests(loader.loadTestsFromTestCase(TestIntelligenceLevel))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print()
    print("="*60)
    print("测试总结")
    print("="*60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
