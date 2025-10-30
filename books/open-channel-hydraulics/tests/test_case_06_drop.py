"""
案例6单元测试：跌水消能设计

测试内容：
1. 共轭水深计算
2. 能量损失计算
3. 消能率计算
4. 水跃长度估算
5. 水跃类型判别
6. 弗劳德数关系
7. 动量守恒验证
8. 完整水跃分析
9. 不同Fr1范围测试
10. 边界条件测试

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from models.structures import HydraulicJump


class TestCase06DropStructure:
    """案例6：跌水消能设计测试"""

    def test_conjugate_depth_calculation(self):
        """测试1：共轭水深计算"""
        b = 2.5  # 渠道宽度
        g = 9.81

        jump = HydraulicJump(b=b)

        # 给定跃前参数
        h1 = 0.5  # 跃前水深（急流）
        Fr1 = 5.0  # 跃前弗劳德数

        # 共轭水深公式：h2 = h1/2 * (sqrt(1 + 8*Fr1²) - 1)
        h2_calc = jump.conjugate_depth(h1, Fr1)
        h2_theoretical = h1 / 2 * (np.sqrt(1 + 8*Fr1**2) - 1)

        # 验证计算正确
        assert abs(h2_calc - h2_theoretical) / h2_theoretical < 0.001

        # 跃后水深应大于跃前水深
        assert h2_calc > h1

    def test_energy_loss_calculation(self):
        """测试2：能量损失计算"""
        b = 2.5
        jump = HydraulicJump(b=b)

        h1 = 0.5
        h2 = 2.8  # 共轭水深

        # 能量损失公式：ΔE = (h2 - h1)³ / (4 * h1 * h2)
        dE_calc = jump.energy_loss(h1, h2)
        dE_theoretical = (h2 - h1)**3 / (4 * h1 * h2)

        # 验证计算正确
        assert abs(dE_calc - dE_theoretical) / dE_theoretical < 0.001

        # 能量损失应为正
        assert dE_calc > 0

    def test_energy_dissipation_ratio(self):
        """测试3：消能率计算"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # 从Fr1反推h1，确保数据一致
        Fr1 = 5.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)
        h2 = jump.conjugate_depth(h1, Fr1)

        # 消能率
        eta = jump.energy_dissipation_ratio(h1, h2, Q)

        # 消能率应在合理范围（0-100%）
        assert 0 < eta < 100

        # 对于Fr1=5.0的强水跃，消能率应该较高（>45%）
        assert eta > 45

    def test_jump_length_estimation(self):
        """测试4：水跃长度估算"""
        b = 2.5
        jump = HydraulicJump(b=b)

        h1 = 0.5
        h2 = 2.8

        # 水跃长度经验公式：Lj = 6.0 * (h2 - h1)
        Lj_calc = jump.jump_length(h1, h2)
        Lj_theoretical = 6.0 * (h2 - h1)

        # 验证计算正确
        assert abs(Lj_calc - Lj_theoretical) < 0.001

        # 水跃长度应为正
        assert Lj_calc > 0

        # 长度系数应在合理范围（5-7倍跃高）
        assert 5 * (h2 - h1) < Lj_calc < 7 * (h2 - h1)

    def test_jump_type_classification(self):
        """测试5：水跃类型判别"""
        b = 2.5
        jump = HydraulicJump(b=b)

        # 测试不同Fr1的水跃类型
        test_cases = [
            (1.5, "波状水跃"),
            (2.0, "弱水跃"),
            (3.5, "稳定水跃"),
            (6.0, "强水跃"),
            (10.0, "剧烈水跃")
        ]

        for Fr1, expected_type in test_cases:
            jump_type = jump.jump_type(Fr1)
            # 验证类型字符串包含预期关键词
            assert expected_type in jump_type

    def test_froude_number_relationships(self):
        """测试6：弗劳德数关系"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # 从Fr1反推h1
        Fr1 = 5.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        # 计算共轭水深
        h2 = jump.conjugate_depth(h1, Fr1)

        # 计算跃后弗劳德数
        v1 = Q / (b * h1)
        v2 = Q / (b * h2)
        Fr2 = v2 / np.sqrt(g * h2)

        # 验证Fr1计算一致性
        Fr1_calc = v1 / np.sqrt(g * h1)
        assert abs(Fr1_calc - Fr1) / Fr1 < 0.01

        # 跃前应为急流（Fr1 > 1）
        assert Fr1 > 1

        # 跃后应为缓流（Fr2 < 1）
        assert Fr2 < 1

    def test_momentum_conservation(self):
        """测试7：动量守恒验证"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # 从Fr1反推h1
        Fr1 = 5.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        # 计算共轭水深
        h2 = jump.conjugate_depth(h1, Fr1)

        # 动量函数：M = Q²/(g*A) + A*yc
        # 对于矩形断面，yc = h/2
        A1 = b * h1
        A2 = b * h2
        M1 = Q**2/(g*A1) + A1*h1/2
        M2 = Q**2/(g*A2) + A2*h2/2

        # 水跃前后动量应守恒
        assert abs(M1 - M2) / M1 < 0.01

    def test_complete_jump_analysis(self):
        """测试8：完整水跃分析"""
        b = 2.5
        Q = 5.0
        h1 = 0.5

        jump = HydraulicJump(b=b)
        results = jump.analyze_jump(Q, h1)

        # 验证返回所有必需参数
        required_keys = [
            "跃前水深_h1", "跃前流速_v1", "跃前Fr_Fr1", "跃前比能_E1",
            "跃后水深_h2", "跃后流速_v2", "跃后Fr_Fr2", "跃后比能_E2",
            "能量损失_dE", "消能率_%", "水跃长度_Lj", "水跃类型"
        ]

        for key in required_keys:
            assert key in results

        # 验证数值合理性
        assert results["跃前水深_h1"] == h1
        assert results["跃后水深_h2"] > h1
        assert results["跃前Fr_Fr1"] > 1  # 急流
        assert results["跃后Fr_Fr2"] < 1  # 缓流
        assert results["能量损失_dE"] > 0
        assert 0 < results["消能率_%"] < 100
        assert results["水跃长度_Lj"] > 0

    def test_weak_jump(self):
        """测试9：弱水跃（Fr1 = 1.7-2.5）"""
        b = 2.5
        Q = 5.0
        jump = HydraulicJump(b=b)

        # 构造弱水跃条件
        Fr1 = 2.0
        # 从Fr1反推h1：v1 = Fr1 * sqrt(g*h1), Q = b*h1*v1
        # Q = b*h1*Fr1*sqrt(g*h1) = b*Fr1*sqrt(g)*h1^(3/2)
        # h1 = (Q / (b*Fr1*sqrt(g)))^(2/3)
        g = 9.81
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        results = jump.analyze_jump(Q, h1)

        # 弱水跃特征
        assert 1.7 < results["跃前Fr_Fr1"] < 2.5
        assert "弱水跃" in results["水跃类型"]
        # 弱水跃消能率较低（<50%）
        assert results["消能率_%"] < 50

    def test_stable_jump(self):
        """测试10：稳定水跃（Fr1 = 2.5-4.5）"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # 构造稳定水跃条件
        Fr1 = 3.5
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        results = jump.analyze_jump(Q, h1)

        # 稳定水跃特征
        assert 2.5 < results["跃前Fr_Fr1"] < 4.5
        assert "稳定水跃" in results["水跃类型"]
        # 稳定水跃消能率中等（25-50%）
        assert 25 < results["消能率_%"] < 55

    def test_strong_jump(self):
        """测试11：强水跃（Fr1 = 4.5-9.0）"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # 构造强水跃条件
        Fr1 = 6.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        results = jump.analyze_jump(Q, h1)

        # 强水跃特征
        assert 4.5 < results["跃前Fr_Fr1"] < 9.0
        assert "强水跃" in results["水跃类型"]
        # 强水跃消能率高（>50%）
        assert results["消能率_%"] > 50

    def test_energy_balance(self):
        """测试12：能量平衡验证"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # 从Fr1反推h1
        Fr1 = 5.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        # 计算共轭水深和能量损失
        h2 = jump.conjugate_depth(h1, Fr1)
        dE = jump.energy_loss(h1, h2)

        # 计算比能
        v1 = Q / (b * h1)
        v2 = Q / (b * h2)
        E1 = h1 + v1**2 / (2*g)
        E2 = h2 + v2**2 / (2*g)

        # 验证能量平衡：E1 = E2 + dE
        assert abs((E1 - E2) - dE) / dE < 0.01


class TestEdgeCases:
    """边界条件测试"""

    def test_small_froude_number(self):
        """测试小Fr1（接近临界）"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # Fr1 = 1.2（勉强急流）
        Fr1 = 1.2
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        results = jump.analyze_jump(Q, h1)

        # 应该能计算，但消能效果很差
        assert results["跃后水深_h2"] > h1
        assert results["能量损失_dE"] > 0
        # 消能率很低
        assert results["消能率_%"] < 10

    def test_large_froude_number(self):
        """测试大Fr1（剧烈水跃）"""
        b = 2.5
        Q = 5.0
        g = 9.81
        jump = HydraulicJump(b=b)

        # Fr1 = 12.0（剧烈水跃）
        Fr1 = 12.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        results = jump.analyze_jump(Q, h1)

        # 应该能计算，消能效果极好
        assert results["跃后水深_h2"] > h1
        assert "剧烈水跃" in results["水跃类型"]
        # 消能率很高
        assert results["消能率_%"] > 70

    def test_shallow_depth(self):
        """测试浅水深"""
        b = 2.5
        jump = HydraulicJump(b=b)

        h1 = 0.1  # 很浅
        Fr1 = 5.0

        h2 = jump.conjugate_depth(h1, Fr1)

        # 应该能计算
        assert h2 > h1
        assert h2 > 0

    def test_deep_depth(self):
        """测试深水深"""
        b = 2.5
        jump = HydraulicJump(b=b)

        h1 = 3.0  # 较深
        Fr1 = 5.0

        h2 = jump.conjugate_depth(h1, Fr1)

        # 应该能计算
        assert h2 > h1
        assert h2 < 20.0  # 合理上限

    def test_narrow_channel(self):
        """测试窄渠道"""
        b = 0.5  # 窄渠道
        Q = 1.0
        g = 9.81
        jump = HydraulicJump(b=b)

        Fr1 = 5.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        results = jump.analyze_jump(Q, h1)

        # 应该能正常计算
        assert results["跃后水深_h2"] > h1
        assert results["能量损失_dE"] > 0

    def test_wide_channel(self):
        """测试宽渠道"""
        b = 10.0  # 宽渠道
        Q = 20.0
        g = 9.81
        jump = HydraulicJump(b=b)

        Fr1 = 5.0
        h1 = (Q / (b * Fr1 * np.sqrt(g)))**(2/3)

        results = jump.analyze_jump(Q, h1)

        # 应该能正常计算
        assert results["跃后水深_h2"] > h1
        assert results["能量损失_dE"] > 0

    def test_invalid_froude_number(self):
        """测试无效Fr1（缓流）"""
        b = 2.5
        jump = HydraulicJump(b=b)

        h1 = 0.5
        Fr1 = 0.8  # 缓流，不应发生水跃

        # 应该抛出异常
        with pytest.raises(ValueError):
            jump.conjugate_depth(h1, Fr1)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
