"""
案例10单元测试：复式断面河道

测试内容：
1. 主槽几何计算（梯形断面）
2. 滩地几何计算
3. 总面积计算（主槽+滩地）
4. 漫滩流量计算
5. 各分区流量分配
6. 流量分配比
7. 主槽与滩地流速差异
8. 水深-流量关系
9. 边界条件测试

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from models.channel import CompoundChannel


class TestCase10CompoundChannel:
    """案例10：复式断面河道测试"""

    def test_main_channel_geometry(self):
        """测试1：主槽几何计算"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 测试未漫滩水深（h < hm）
        h = 2.0
        Am = channel.main_channel_area(h)
        Pm = channel.main_channel_wetted_perimeter(h)
        Tm = channel.main_channel_top_width(h)

        # 梯形面积：A = (b + m*h) * h
        Am_theoretical = (bm + m1 * h) * h
        assert abs(Am - Am_theoretical) < 0.001

        # 湿周：P = b + 2*h*sqrt(1+m²)
        Pm_theoretical = bm + 2 * h * np.sqrt(1 + m1**2)
        assert abs(Pm - Pm_theoretical) < 0.001

        # 水面宽：T = b + 2*m*h
        Tm_theoretical = bm + 2 * m1 * h
        assert abs(Tm - Tm_theoretical) < 0.001

    def test_floodplain_geometry(self):
        """测试2：滩地几何计算"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 测试漫滩水深（h > hm）
        h = 4.5
        hf = h - hm  # 漫滩深度

        # 左滩地面积
        Al = channel.floodplain_area(h, 'left')
        # 理论值：A = b*hf + 0.5*m2*hf²
        Al_theoretical = bl * hf + 0.5 * m2 * hf**2
        assert abs(Al - Al_theoretical) < 0.001

        # 右滩地面积
        Ar = channel.floodplain_area(h, 'right')
        Ar_theoretical = br * hf + 0.5 * m2 * hf**2
        assert abs(Ar - Ar_theoretical) < 0.001

        # 左滩地湿周
        Pl = channel.floodplain_wetted_perimeter(h, 'left')
        Pl_theoretical = bl + hf * np.sqrt(1 + m2**2)
        assert abs(Pl - Pl_theoretical) < 0.001

    def test_total_area_calculation(self):
        """测试3：总面积计算"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 未漫滩时（h < hm）：只有主槽
        h_no_flood = 2.0
        A_total = channel.total_area(h_no_flood)
        Am = channel.main_channel_area(h_no_flood)
        assert abs(A_total - Am) < 0.001

        # 漫滩时（h > hm）：主槽 + 滩地
        h_flood = 4.5
        A_total = channel.total_area(h_flood)
        Am = channel.main_channel_area(h_flood)
        Al = channel.floodplain_area(h_flood, 'left')
        Ar = channel.floodplain_area(h_flood, 'right')
        A_sum = Am + Al + Ar
        assert abs(A_total - A_sum) < 0.001

    def test_bankfull_discharge(self):
        """测试4：漫滩流量计算"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 漫滩流量（主槽满流量）
        Q_bankfull = channel.bankfull_discharge()

        # 应为正值
        assert Q_bankfull > 0

        # 应在合理范围
        assert 50 < Q_bankfull < 500

    def test_discharge_distribution(self):
        """测试5：流量分配计算"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 漫滩水深
        h = 4.5

        result = channel.discharge(h)

        # 验证返回字段
        assert 'total' in result
        assert 'main' in result
        assert 'left' in result
        assert 'right' in result
        assert 'alpha_main' in result
        assert 'alpha_flood' in result

        # 总流量应等于各分区之和
        Q_sum = result['main'] + result['left'] + result['right']
        assert abs(result['total'] - Q_sum) / result['total'] < 0.001

        # 所有流量应为正
        assert result['total'] > 0
        assert result['main'] > 0
        assert result['left'] >= 0
        assert result['right'] >= 0

    def test_discharge_ratio(self):
        """测试6：流量分配比"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 漫滩水深
        h = 4.5
        result = channel.discharge(h)

        # 流量分配比之和应等于1
        assert abs(result['alpha_main'] + result['alpha_flood'] - 1.0) < 0.001

        # 各分配比应在0-1之间
        assert 0 <= result['alpha_main'] <= 1
        assert 0 <= result['alpha_flood'] <= 1

        # 主槽流量比应大于0（因为主槽总是过流）
        assert result['alpha_main'] > 0

    def test_velocity_difference(self):
        """测试7：主槽与滩地流速差异"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 漫滩水深
        h = 4.5

        # 计算各分区流速
        vm = channel.velocity_subsection(h, 'main')
        vl = channel.velocity_subsection(h, 'left')
        vr = channel.velocity_subsection(h, 'right')

        # 主槽流速应大于滩地（主槽糙率小）
        assert vm > vl
        assert vm > vr

        # 左右滩地流速应接近（参数对称）
        assert abs(vl - vr) / vl < 0.1

    def test_depth_discharge_relationship(self):
        """测试8：水深-流量关系"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 测试不同水深的流量
        depths = [1.0, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0]
        discharges = []

        for h in depths:
            result = channel.discharge(h)
            discharges.append(result['total'])

        # 水深增加，流量应增加
        for i in range(len(discharges) - 1):
            assert discharges[i] < discharges[i+1]

        # 验证漫滩前后流量增长特性
        # 注意：虽然面积增加，但滩地糙率较大，流量增长可能减缓
        idx_bankfull = depths.index(3.5)
        Q_before = discharges[idx_bankfull - 1]
        Q_bankfull = discharges[idx_bankfull]
        Q_after = discharges[idx_bankfull + 1]

        # 漫滩后仍有流量增量（虽然可能减缓）
        dQ_after = Q_after - Q_bankfull
        assert dQ_after > 0

        # 漫滩后总流量应显著大于漫滩流量
        assert Q_after > Q_bankfull * 1.05

    def test_no_floodplain_case(self):
        """测试9：未漫滩情况"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 未漫滩水深
        h = 2.0
        result = channel.discharge(h)

        # 滩地流量应为0
        assert result['left'] == 0.0
        assert result['right'] == 0.0

        # 总流量应等于主槽流量
        assert abs(result['total'] - result['main']) < 0.001

        # 主槽流量比应为100%
        assert abs(result['alpha_main'] - 1.0) < 0.001
        assert abs(result['alpha_flood']) < 0.001


class TestEdgeCases:
    """边界条件测试"""

    def test_critical_depth_at_bankfull(self):
        """测试临界漫滩水深"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 恰好满槽
        h = hm
        result = channel.discharge(h)

        # 滩地流量应为0
        assert result['left'] == 0.0
        assert result['right'] == 0.0

    def test_shallow_flooding(self):
        """测试浅层漫滩"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 轻微漫滩
        h = hm + 0.1
        result = channel.discharge(h)

        # 滩地应有流量
        assert result['left'] > 0
        assert result['right'] > 0

        # 但主槽流量仍占主导
        assert result['main'] > result['left'] + result['right']

    def test_deep_flooding(self):
        """测试深层漫滩"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        # 深度漫滩
        h = hm + 2.0
        result = channel.discharge(h)

        # 滩地流量应占较大比例
        assert result['left'] + result['right'] > 0.3 * result['total']

    def test_narrow_main_channel(self):
        """测试窄主槽"""
        bm = 10.0  # 窄主槽
        hm = 3.5
        m1 = 2.0
        bl = 50.0
        br = 50.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        h = hm + 1.0
        result = channel.discharge(h)

        # 窄主槽情况下，滩地流量应有显著贡献
        # 但由于主槽糙率小，主槽仍可能占主导
        assert result['alpha_flood'] > 0.3

        # 滩地应有流量
        assert result['left'] > 0
        assert result['right'] > 0

    def test_wide_main_channel(self):
        """测试宽主槽"""
        bm = 80.0  # 宽主槽
        hm = 3.5
        m1 = 2.0
        bl = 20.0
        br = 20.0
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        h = hm + 1.0
        result = channel.discharge(h)

        # 宽主槽情况下，主槽流量占比应更大
        assert result['alpha_main'] > 0.7

    def test_asymmetric_floodplains(self):
        """测试不对称滩地"""
        bm = 30.0
        hm = 3.5
        m1 = 2.0
        bl = 30.0  # 左窄
        br = 70.0  # 右宽
        m2 = 3.0
        nm = 0.028
        nf = 0.035
        S0 = 0.0003

        channel = CompoundChannel(
            bm=bm, hm=hm, m1=m1,
            bl=bl, br=br, m2=m2,
            nm=nm, nf=nf, S0=S0
        )

        h = hm + 1.0
        result = channel.discharge(h)

        # 右滩地更宽，流量应更大
        assert result['right'] > result['left']


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
