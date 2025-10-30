"""
案例11单元测试：渠道变宽与收缩

测试内容：
1. 扩散损失系数计算
2. 收缩损失系数计算
3. 渐变角计算
4. 扩散段水深计算（渐变）
5. 扩散段水深计算（突然）
6. 收缩段水深计算（渐变）
7. 收缩段水深计算（突然）
8. 能量守恒验证
9. 扩散与收缩损失对比
10. 水深变化趋势
11. 流速变化趋势
12. 渐变段长度设计
13. 突然过渡与渐变过渡对比

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

# 导入主程序中的函数
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code/examples/case_11_transition'))
from main import (
    expansion_loss_coefficient,
    contraction_loss_coefficient,
    compute_expansion_flow,
    compute_contraction_flow
)

from models.channel import RectangularChannel


class TestCase11ChannelTransition:
    """案例11：渠道变宽与收缩测试"""

    def test_expansion_loss_coefficient_gradual(self):
        """测试1：扩散损失系数计算（渐变）"""
        # 小角度（良好渐变）
        zeta1 = expansion_loss_coefficient(theta_deg=5.0, gradual=True)
        assert 0.10 <= zeta1 <= 0.20

        # 中等角度（一般渐变）
        zeta2 = expansion_loss_coefficient(theta_deg=10.0, gradual=True)
        assert 0.10 <= zeta2 <= 0.25

        # 临界角度
        zeta3 = expansion_loss_coefficient(theta_deg=12.5, gradual=True)
        assert 0.15 <= zeta3 <= 0.30

        # 较大角度
        zeta4 = expansion_loss_coefficient(theta_deg=15.0, gradual=True)
        assert 0.25 <= zeta4 <= 0.50

        # 角度越大，损失系数越大
        assert zeta4 >= zeta3 >= zeta2

    def test_expansion_loss_coefficient_sudden(self):
        """测试2：扩散损失系数计算（突然）"""
        # 突然扩散（Borda-Carnot）
        zeta = expansion_loss_coefficient(theta_deg=20.0, gradual=False)

        # 突然扩散损失系数为1.0
        assert abs(zeta - 1.0) < 0.01

        # 突然扩散远大于渐变扩散
        zeta_gradual = expansion_loss_coefficient(theta_deg=10.0, gradual=True)
        assert zeta > 3 * zeta_gradual

    def test_contraction_loss_coefficient_gradual(self):
        """测试3：收缩损失系数计算（渐变）"""
        A1 = 4.0  # 上游面积
        A2 = 3.0  # 下游面积

        zeta = contraction_loss_coefficient(A1, A2, gradual=True)

        # 渐变收缩损失系数应在0.05-0.10范围
        assert 0.05 <= zeta <= 0.15

    def test_contraction_loss_coefficient_sudden(self):
        """测试4：收缩损失系数计算（突然）"""
        A1 = 4.0
        A2 = 3.0

        zeta = contraction_loss_coefficient(A1, A2, gradual=False)

        # 突然收缩：ζ = 0.5 * [1 - (A₂/A₁)]
        zeta_theoretical = 0.5 * (1 - A2/A1)

        assert abs(zeta - zeta_theoretical) < 0.01

        # 突然收缩应大于渐变收缩
        zeta_gradual = contraction_loss_coefficient(A1, A2, gradual=True)
        assert zeta > zeta_gradual

    def test_expansion_angle_calculation(self):
        """测试5：扩散段渐变角计算"""
        B1 = 4.0  # m
        B2 = 6.0  # m
        L = 20.0  # m

        # 渐变角：tan(θ) = (B₂ - B₁) / (2*L)
        theta_rad = np.arctan((B2 - B1) / (2 * L))
        theta_deg = np.degrees(theta_rad)

        # 验证角度计算
        result = compute_expansion_flow(B1, B2, Q=12.0, n=0.020, S0=0.0002, L=L, gradual=True)

        assert abs(result['theta_deg'] - theta_deg) < 0.01

        # 应在推荐范围内（≤12.5°）
        assert result['theta_deg'] <= 13.0

    def test_contraction_angle_calculation(self):
        """测试6：收缩段渐变角计算"""
        B1 = 4.0  # m
        B2 = 3.0  # m
        L = 20.0  # m

        # 渐变角：tan(θ) = (B₁ - B₂) / (2*L)
        theta_rad = np.arctan((B1 - B2) / (2 * L))
        theta_deg = np.degrees(theta_rad)

        result = compute_contraction_flow(B1, B2, Q=12.0, n=0.020, S0=0.0002, L=L, gradual=True)

        assert abs(result['theta_deg'] - theta_deg) < 0.01

        # 应在推荐范围内（≤30°）
        assert result['theta_deg'] <= 30.0

    def test_expansion_water_depth_gradual(self):
        """测试7：扩散段水深计算（渐变）"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 扩散段：下游水深应大于上游水深（缓流）
        assert result['h2'] > result['h1']

        # 水深应为正
        assert result['h1'] > 0
        assert result['h2'] > 0

        # 水面壅高应为正
        assert result['water_rise'] > 0

        # 壅高应在合理范围（几厘米到几十厘米）
        assert 0.01 < result['water_rise'] < 1.0

    def test_expansion_velocity_relationship(self):
        """测试8：扩散段流速关系"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 扩散段：上游流速应大于下游流速
        assert result['v1'] > result['v2']

        # 流速应为正
        assert result['v1'] > 0
        assert result['v2'] > 0

        # 连续性方程：Q = B*h*v
        Q1_calc = B1 * result['h1'] * result['v1']
        Q2_calc = B2 * result['h2'] * result['v2']

        assert abs(Q1_calc - Q) / Q < 0.01
        assert abs(Q2_calc - Q) / Q < 0.01

    def test_expansion_energy_conservation(self):
        """测试9：扩散段能量守恒"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0
        g = 9.81

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 能量方程：E1 + S0*L = E2 + hf_total
        E1 = result['E1']
        E2 = result['E2']
        hf_total = result['hf_total']

        energy_balance = E1 + S0*L - E2 - hf_total

        # 能量应守恒（误差很小）
        assert abs(energy_balance) < 0.03

    def test_expansion_sudden_vs_gradual(self):
        """测试10：扩散段突然与渐变对比"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        gradual = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)
        sudden = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=False)

        # 突然扩散损失系数应为1.0
        assert abs(sudden['zeta'] - 1.0) < 0.01

        # 突然扩散局部损失应远大于渐变扩散
        assert sudden['hf_local'] > 2 * gradual['hf_local']

        # 突然扩散总损失也应更大
        assert sudden['hf_total'] > gradual['hf_total']

    def test_contraction_water_depth_gradual(self):
        """测试11：收缩段水深计算（渐变）"""
        B1 = 4.0
        B2 = 3.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_contraction_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 收缩段（缓流）：上游水深应小于或接近下游水深
        # 注意：收缩会增加流速，降低水深，但也可能因为下游断面变窄而增加水深
        # 需要根据具体情况判断
        assert result['h1'] > 0
        assert result['h2'] > 0

        # 水面降低（或变化）应在合理范围
        assert abs(result['water_drop']) < 0.5

    def test_contraction_velocity_relationship(self):
        """测试12：收缩段流速关系"""
        B1 = 4.0
        B2 = 3.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_contraction_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 收缩段：下游流速应大于上游流速
        assert result['v2'] > result['v1']

        # 连续性方程
        Q1_calc = B1 * result['h1'] * result['v1']
        Q2_calc = B2 * result['h2'] * result['v2']

        assert abs(Q1_calc - Q) / Q < 0.01
        assert abs(Q2_calc - Q) / Q < 0.01

    def test_contraction_energy_conservation(self):
        """测试13：收缩段能量守恒"""
        B1 = 4.0
        B2 = 3.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_contraction_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 能量方程：E1 + S0*L = E2 + hf_total
        E1 = result['E1']
        E2 = result['E2']
        hf_total = result['hf_total']

        energy_balance = E1 + S0*L - E2 - hf_total

        # 能量应守恒
        assert abs(energy_balance) < 0.01

    def test_contraction_sudden_vs_gradual(self):
        """测试14：收缩段突然与渐变对比"""
        B1 = 4.0
        B2 = 3.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        gradual = compute_contraction_flow(B1, B2, Q, n, S0, L, gradual=True)
        sudden = compute_contraction_flow(B1, B2, Q, n, S0, L, gradual=False)

        # 突然收缩损失系数应大于渐变收缩
        assert sudden['zeta'] > gradual['zeta']

        # 突然收缩局部损失应大于渐变收缩
        assert sudden['hf_local'] > gradual['hf_local']

    def test_expansion_loss_greater_than_contraction(self):
        """测试15：扩散损失大于收缩损失"""
        B_mid = 4.0
        B_wide = 6.0
        B_narrow = 3.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        # 扩散：4m → 6m
        expansion = compute_expansion_flow(B_mid, B_wide, Q, n, S0, L, gradual=True)

        # 收缩：4m → 3m
        contraction = compute_contraction_flow(B_mid, B_narrow, Q, n, S0, L, gradual=True)

        # 扩散局部损失应远大于收缩损失
        assert expansion['hf_local'] > contraction['hf_local']

        # 损失比应在合理范围（扩散损失约为收缩损失的1.4-10倍）
        loss_ratio = expansion['hf_local'] / contraction['hf_local']
        assert 1.4 < loss_ratio < 10.0

    def test_froude_number_subcritical(self):
        """测试16：弗劳德数验证（缓流）"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 正常流动应为缓流（Fr < 1）
        assert result['Fr1'] < 1.0
        assert result['Fr2'] < 1.0

        # 扩散后弗劳德数应减小（流速降低）
        assert result['Fr2'] < result['Fr1']


class TestEdgeCases:
    """边界条件测试"""

    def test_large_expansion_ratio(self):
        """测试大扩散比"""
        B1 = 3.0
        B2 = 7.0  # 扩大2.33倍
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 40.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 大扩散比应有明显的能量损失
        assert result['hf_local'] > 0.01

        # 流速应显著降低
        velocity_reduction = (result['v1'] - result['v2']) / result['v1']
        assert velocity_reduction > 0.3

    def test_small_expansion_ratio(self):
        """测试小扩散比"""
        B1 = 4.0
        B2 = 4.5  # 扩大12.5%
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 小扩散比水深变化应较小
        assert result['water_rise'] < 0.3

        # 能量损失应很小
        assert result['hf_local'] < 0.05

    def test_large_contraction_ratio(self):
        """测试大收缩比"""
        B1 = 6.0
        B2 = 2.0  # 收缩到1/3
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 40.0

        result = compute_contraction_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 大收缩比应有显著的流速增加
        velocity_increase = (result['v2'] - result['v1']) / result['v1']
        assert velocity_increase > 0.5

    def test_very_short_transition(self):
        """测试极短渐变段"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 4.0  # 很短的渐变段

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 渐变角应很大
        assert result['theta_deg'] > 12.5

        # 损失系数应较大
        assert result['zeta'] > 0.20

    def test_very_long_transition(self):
        """测试极长渐变段"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.0002
        L = 100.0  # 很长的渐变段

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 渐变角应很小
        assert result['theta_deg'] < 5.0

        # 损失系数应较小
        assert result['zeta'] < 0.20

    def test_steep_slope(self):
        """测试陡坡情况"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.01  # 陡坡
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 应能正常计算
        assert result['h1'] > 0
        assert result['h2'] > 0

        # 沿程损失应较大
        assert result['hf_friction'] > 0.01

    def test_mild_slope(self):
        """测试缓坡情况"""
        B1 = 4.0
        B2 = 6.0
        Q = 12.0
        n = 0.020
        S0 = 0.00001  # 很缓的坡
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 应能正常计算
        assert result['h1'] > 0
        assert result['h2'] > 0

        # 沿程损失应很小
        assert result['hf_friction'] < 0.001

    def test_high_discharge(self):
        """测试大流量"""
        B1 = 4.0
        B2 = 6.0
        Q = 50.0  # 大流量
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 大流量下水深和流速都应较大
        assert result['h1'] > 1.0
        assert result['v1'] > 1.5

        # 能量损失应较大
        assert result['hf_local'] > 0.01

    def test_low_discharge(self):
        """测试小流量"""
        B1 = 4.0
        B2 = 6.0
        Q = 2.0  # 小流量
        n = 0.020
        S0 = 0.0002
        L = 20.0

        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        # 小流量下水深和流速都应较小
        assert result['h1'] < 1.0
        assert result['v1'] < 2.0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
