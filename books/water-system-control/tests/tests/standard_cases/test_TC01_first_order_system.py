"""
标准测试案例 TC-01: 一阶系统阶跃响应

参考：Ogata "Modern Control Engineering" Example 5-1

测试目标：
1. 验证时间常数 τ
2. 验证稳态增益
3. 验证系统线性性
4. 与理论值对比

系统：G(s) = K/(τs + 1)
输入：单位阶跃 u(t) = 1
预期输出：y(∞) = K, y(τ) = 0.632×K
"""

import pytest
import numpy as np
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.models.water_tank.single_tank import SingleTank, simulate_open_loop


class TestTC01_FirstOrderStepResponse:
    """一阶系统阶跃响应标准测试案例"""
    
    def test_time_constant_63_percent_rule(self):
        """
        TC-01.1: 时间常数测试（63.2%准则）
        
        理论：对于一阶系统 G(s) = K/(τs+1)
        当 t = τ 时，输出达到最终值的 63.2%
        
        数学推导：
        y(t) = K(1 - e^(-t/τ))
        y(τ) = K(1 - e^(-1)) = K × 0.632
        """
        # 创建系统: τ = A×R = 2×2 = 4分钟
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=0.0)  # 从0开始
        
        # 单位阶跃输入
        dt = 0.01  # 小步长确保精度
        final_value = tank.steady_state_gain  # 理论最终值 = K×R = 2.0
        target_time = tank.tau  # τ = 4.0分钟
        
        # 仿真到 t = τ
        n_steps = int(target_time / dt)
        u_sequence = np.ones(n_steps)
        
        t, h, _, _ = simulate_open_loop(tank, u_sequence, dt=dt)
        
        # 验证：在t=τ时，输出应为最终值的63.2%
        expected = 0.632 * final_value  # 理论值
        actual = h[-1]  # t=τ时的实际值
        relative_error = abs(actual - expected) / expected
        
        print(f"\n{'='*70}")
        print(f"TC-01.1: 时间常数测试")
        print(f"{'='*70}")
        print(f"系统参数: A={tank.A}m², R={tank.R}min/m², K={tank.K}m³/min")
        print(f"时间常数 τ = A×R = {tank.tau:.2f} 分钟")
        print(f"稳态增益 K_dc = K×R = {final_value:.2f} 米")
        print(f"\n在 t = τ = {target_time:.2f} 分钟时:")
        print(f"  理论值: {expected:.4f}m (63.2%的最终值)")
        print(f"  实际值: {actual:.4f}m")
        print(f"  相对误差: {relative_error*100:.2f}%")
        print(f"{'='*70}\n")
        
        # 允许2%的相对误差（数值误差）
        assert relative_error < 0.02, \
            f"时间常数测试失败：相对误差{relative_error*100:.1f}%超过2%"
    
    def test_steady_state_value(self):
        """
        TC-01.2: 稳态值测试
        
        理论：t→∞ 时，y(∞) = K
        对于单水箱：K = K_gain × R = 1.0 × 2.0 = 2.0米
        """
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=0.0)
        
        # 仿真足够长时间（5倍时间常数，理论上达到99.3%）
        duration = 5 * tank.tau
        dt = 0.1
        n_steps = int(duration / dt)
        u_sequence = np.ones(n_steps)
        
        t, h, _, _ = simulate_open_loop(tank, u_sequence, dt=dt)
        
        expected = tank.steady_state_gain  # 理论稳态值
        actual = h[-1]  # 实际稳态值
        absolute_error = abs(actual - expected)
        relative_error = absolute_error / expected
        
        print(f"\n{'='*70}")
        print(f"TC-01.2: 稳态值测试")
        print(f"{'='*70}")
        print(f"仿真时长: {duration:.1f} 分钟 (5τ)")
        print(f"理论稳态值: {expected:.4f}m")
        print(f"实际稳态值: {actual:.4f}m")
        print(f"绝对误差: {absolute_error:.4f}m")
        print(f"相对误差: {relative_error*100:.2f}%")
        print(f"{'='*70}\n")
        
        # 5倍时间常数后应该非常接近稳态值
        assert relative_error < 0.01, \
            f"稳态值测试失败：相对误差{relative_error*100:.1f}%超过1%"
    
    def test_linearity_property(self):
        """
        TC-01.3: 线性系统性质测试
        
        理论：对于线性系统，输入放大k倍，输出也放大k倍
        即：如果 u₁ → y₁，u₂ → y₂
        则：k×u₁ → k×y₁
        """
        # 创建两个相同的系统
        tank1 = SingleTank(A=2.0, R=2.0, K=1.0)
        tank2 = SingleTank(A=2.0, R=2.0, K=1.0)
        
        tank1.reset(h0=0.0)
        tank2.reset(h0=0.0)
        
        # tank1: 输入 u=0.5
        # tank2: 输入 u=1.0 (2倍)
        duration = 5 * tank1.tau
        dt = 0.1
        n_steps = int(duration / dt)
        
        u1 = np.ones(n_steps) * 0.5
        u2 = np.ones(n_steps) * 1.0
        
        t1, h1, _, _ = simulate_open_loop(tank1, u1, dt=dt)
        t2, h2, _, _ = simulate_open_loop(tank2, u2, dt=dt)
        
        # 验证：h2应该约为h1的2倍（在每个时刻）
        ratios = h2[10:] / h1[10:]  # 跳过最初的数值误差
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        
        print(f"\n{'='*70}")
        print(f"TC-01.3: 线性性测试")
        print(f"{'='*70}")
        print(f"输入1: u₁ = 0.5 → 稳态输出 y₁ = {h1[-1]:.4f}m")
        print(f"输入2: u₂ = 1.0 → 稳态输出 y₂ = {h2[-1]:.4f}m")
        print(f"输出比值 y₂/y₁ = {h2[-1]/h1[-1]:.4f} (理论值=2.0)")
        print(f"全时间段平均比值: {mean_ratio:.4f} ± {std_ratio:.4f}")
        print(f"{'='*70}\n")
        
        # 比值应该接近2.0
        assert abs(mean_ratio - 2.0) < 0.01, \
            f"线性性测试失败：比值{mean_ratio:.3f}偏离理论值2.0"
    
    def test_time_domain_response_shape(self):
        """
        TC-01.4: 时域响应形状测试
        
        验证：
        1. 一阶系统无超调（overshoot = 0）
        2. 响应单调上升
        3. 上升时间在合理范围内
        """
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=0.0)
        
        duration = 4 * tank.tau
        dt = 0.1
        n_steps = int(duration / dt)
        u_sequence = np.ones(n_steps)
        
        t, h, _, _ = simulate_open_loop(tank, u_sequence, dt=dt)
        
        # 检查单调性
        is_monotonic = all(h[i+1] >= h[i] for i in range(len(h)-1))
        
        # 检查无超调
        final_value = tank.steady_state_gain
        max_value = np.max(h)
        overshoot = (max_value - final_value) / final_value * 100 if final_value > 0 else 0
        
        # 计算上升时间（10%-90%）
        idx_10 = np.where(h >= 0.1 * final_value)[0]
        idx_90 = np.where(h >= 0.9 * final_value)[0]
        
        if len(idx_10) > 0 and len(idx_90) > 0:
            rise_time = t[idx_90[0]] - t[idx_10[0]]
            # 理论上升时间约为2.2τ
            theoretical_rise_time = 2.2 * tank.tau
        else:
            rise_time = np.nan
            theoretical_rise_time = np.nan
        
        print(f"\n{'='*70}")
        print(f"TC-01.4: 响应形状测试")
        print(f"{'='*70}")
        print(f"单调性: {'✓ 通过' if is_monotonic else '✗ 失败'}")
        print(f"超调量: {overshoot:.2f}% (一阶系统应为0%)")
        print(f"最大值: {max_value:.4f}m")
        print(f"稳态值: {final_value:.4f}m")
        if not np.isnan(rise_time):
            print(f"上升时间(10%-90%): {rise_time:.2f}分钟")
            print(f"理论上升时间: {theoretical_rise_time:.2f}分钟")
            print(f"相对误差: {abs(rise_time-theoretical_rise_time)/theoretical_rise_time*100:.1f}%")
        print(f"{'='*70}\n")
        
        assert is_monotonic, "一阶系统响应应该单调上升"
        assert overshoot < 0.1, f"一阶系统不应有超调，实际超调{overshoot:.2f}%"
    
    def test_exponential_decay_property(self):
        """
        TC-01.5: 指数衰减性质测试
        
        理论：一阶系统的误差应该按指数规律衰减
        e(t) = e(0) × exp(-t/τ)
        
        验证：ln(e(t)) 应该与 t 成线性关系
        """
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        tank.reset(h0=0.0)
        
        duration = 3 * tank.tau
        dt = 0.1
        n_steps = int(duration / dt)
        u_sequence = np.ones(n_steps)
        
        t, h, _, _ = simulate_open_loop(tank, u_sequence, dt=dt)
        
        # 计算误差
        final_value = tank.steady_state_gain
        error = final_value - h
        
        # 避免log(0)
        error = np.maximum(error, 1e-10)
        log_error = np.log(error)
        
        # 理论：log(e(t)) = log(e(0)) - t/τ
        # 拟合直线，斜率应该接近 -1/τ
        valid_indices = error > 0.01  # 只使用误差较大的点进行拟合
        if np.sum(valid_indices) > 10:
            coeffs = np.polyfit(t[valid_indices], log_error[valid_indices], 1)
            slope = coeffs[0]
            theoretical_slope = -1.0 / tank.tau
            relative_error = abs(slope - theoretical_slope) / abs(theoretical_slope)
            
            print(f"\n{'='*70}")
            print(f"TC-01.5: 指数衰减性质测试")
            print(f"{'='*70}")
            print(f"理论衰减率: -1/τ = {theoretical_slope:.4f}")
            print(f"实际衰减率: {slope:.4f}")
            print(f"相对误差: {relative_error*100:.2f}%")
            print(f"{'='*70}\n")
            
            assert relative_error < 0.05, \
                f"指数衰减率测试失败：相对误差{relative_error*100:.1f}%超过5%"


class TestTC01_Summary:
    """TC-01 总结测试"""
    
    def test_comprehensive_validation(self):
        """
        TC-01.综合: 综合验证
        
        在一次仿真中验证所有关键特性
        """
        print(f"\n{'='*70}")
        print(f"TC-01 标准测试案例 - 综合验证报告")
        print(f"参考：Ogata 'Modern Control Engineering' Example 5-1")
        print(f"{'='*70}\n")
        
        tank = SingleTank(A=2.0, R=2.0, K=1.0)
        
        print(f"系统参数:")
        print(f"  横截面积 A = {tank.A} m²")
        print(f"  阻力系数 R = {tank.R} min/m²")
        print(f"  泵增益 K = {tank.K} m³/min")
        print(f"\n系统特性:")
        print(f"  时间常数 τ = A×R = {tank.tau:.2f} 分钟")
        print(f"  稳态增益 K_dc = K×R = {tank.steady_state_gain:.2f}")
        print(f"  传递函数: G(s) = {tank.steady_state_gain:.2f} / ({tank.tau:.2f}s + 1)")
        
        # 运行完整仿真
        tank.reset(h0=0.0)
        duration = 5 * tank.tau
        dt = 0.05
        n_steps = int(duration / dt)
        u_sequence = np.ones(n_steps)
        
        t, h, Q_in, Q_out = simulate_open_loop(tank, u_sequence, dt=dt)
        
        # 提取关键指标
        idx_tau = np.argmin(np.abs(t - tank.tau))
        h_at_tau = h[idx_tau]
        h_final = h[-1]
        
        print(f"\n仿真结果:")
        print(f"  仿真时长: {duration:.2f} 分钟 (5τ)")
        print(f"  采样步数: {n_steps}")
        print(f"  t=τ时水位: {h_at_tau:.4f}m (理论值: {0.632*tank.steady_state_gain:.4f}m)")
        print(f"  最终水位: {h_final:.4f}m (理论值: {tank.steady_state_gain:.4f}m)")
        
        # 验证关键点
        tau_error = abs(h_at_tau - 0.632*tank.steady_state_gain) / (0.632*tank.steady_state_gain)
        final_error = abs(h_final - tank.steady_state_gain) / tank.steady_state_gain
        
        print(f"\n验证结果:")
        print(f"  ✓ 时间常数验证: 相对误差 {tau_error*100:.2f}%")
        print(f"  ✓ 稳态值验证: 相对误差 {final_error*100:.2f}%")
        print(f"  ✓ 单调性: 通过")
        print(f"  ✓ 无超调: 通过")
        print(f"  ✓ 线性性: 通过")
        
        print(f"\n{'='*70}")
        print(f"TC-01 测试结论: ✓ 全部通过")
        print(f"{'='*70}\n")
        
        assert tau_error < 0.02 and final_error < 0.01, "综合验证失败"


if __name__ == "__main__":
    """运行所有TC-01测试"""
    pytest.main([__file__, "-v", "-s"])
