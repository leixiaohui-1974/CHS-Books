#!/usr/bin/env python3
"""
静态设计案例: 传统水力计算
案例: 灌溉渠道闸门设计

设计方法: 按GB 50288-2018标准进行恒定流水力计算
设计内容:
1. 根据设计流量确定闸门尺寸
2. 计算不同开度下的过流能力
3. 校核最大流量工况
4. 输出设计参数

特点:
- 只计算典型工况(设计流量、校核流量)
- 人工调度,凭经验操作
- 交付物: 设计参数表、操作说明(静态文档)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


@dataclass
class GateDesignParameters:
    """闸门设计参数"""
    width: float  # 闸孔宽度(m)
    max_height: float  # 最大闸门高度(m)
    discharge_coef: float  # 流量系数μ
    design_flow: float  # 设计流量(m³/s)
    check_flow: float  # 校核流量(m³/s)


class StaticGateDesign:
    """静态设计: 闸门水力计算"""
    
    def __init__(self, params: GateDesignParameters):
        self.params = params
        self.g = 9.81  # 重力加速度
    
    def compute_discharge(self, opening: float, h_upstream: float, h_downstream: float) -> float:
        """
        闸孔出流公式计算流量(GB 50288-2018)
        
        Q = μ × B × e × √(2g × H)
        
        Parameters:
        -----------
        opening : float
            闸门开度(m)
        h_upstream : float
            上游水位(m)
        h_downstream : float
            下游水位(m)
        
        Returns:
        --------
        Q : float
            过闸流量(m³/s)
        """
        if opening <= 0:
            return 0.0
        
        # 计算作用水头(自由出流)
        if h_downstream < opening:
            # 自由出流
            H = h_upstream
        else:
            # 淹没出流
            H = h_upstream - h_downstream
        
        # 闸孔出流公式
        Q = self.params.discharge_coef * self.params.width * opening * np.sqrt(2 * self.g * H)
        
        return Q
    
    def design_gate_size(self) -> dict:
        """
        步骤1: 根据设计流量确定闸门尺寸
        
        设计依据: GB 50288-2018 §7.3
        """
        print("="*70)
        print("  静态设计: 闸门尺寸设计")
        print("="*70)
        
        # 设计条件
        Q_design = self.params.design_flow  # 设计流量10 m³/s
        h_upstream = 2.5  # 上游设计水位2.5m
        h_downstream = 2.0  # 下游设计水位2.0m
        
        print(f"\n设计条件:")
        print(f"  设计流量: {Q_design} m³/s")
        print(f"  上游水位: {h_upstream} m")
        print(f"  下游水位: {h_downstream} m")
        
        # 假设开度e = 0.6 × 闸孔高度(经验值)
        # 反推闸孔宽度
        opening_ratio = 0.6
        H = h_upstream - h_downstream  # 作用水头
        
        # Q = μ × B × e × √(2gH)
        # e = opening_ratio × max_height
        # 假设 max_height = 3.0m (根据经验)
        max_height = 3.0
        opening = opening_ratio * max_height  # 1.8m
        
        # 计算所需宽度
        required_width = Q_design / (
            self.params.discharge_coef * opening * np.sqrt(2 * self.g * H)
        )
        
        print(f"\n计算过程:")
        print(f"  假设闸门最大高度: {max_height} m")
        print(f"  设计开度: {opening} m (60%最大高度)")
        print(f"  作用水头: {H} m")
        print(f"  计算所需宽度: {required_width:.2f} m")
        
        # 圆整到工程常用尺寸
        if required_width <= 3.0:
            design_width = 3.0
        elif required_width <= 5.0:
            design_width = 5.0
        else:
            design_width = 6.0
        
        print(f"  采用标准宽度: {design_width} m")
        
        # 更新设计参数
        self.params.width = design_width
        self.params.max_height = max_height
        
        # 复核设计流量
        Q_actual = self.compute_discharge(opening, h_upstream, h_downstream)
        
        print(f"\n复核:")
        print(f"  实际过流能力: {Q_actual:.2f} m³/s")
        print(f"  设计流量: {Q_design} m³/s")
        
        if Q_actual >= Q_design:
            print(f"  ✓ 满足设计要求 (余量{(Q_actual/Q_design-1)*100:.1f}%)")
        else:
            print(f"  ✗ 不满足要求!")
        
        return {
            'width': design_width,
            'max_height': max_height,
            'design_opening': opening,
            'design_discharge': Q_actual
        }
    
    def check_max_flow(self) -> dict:
        """
        步骤2: 校核最大流量工况
        
        设计依据: GB 50288-2018 §7.3
        """
        print("\n" + "="*70)
        print("  静态设计: 校核流量工况")
        print("="*70)
        
        Q_check = self.params.check_flow  # 校核流量15 m³/s
        h_upstream = 3.0  # 洪水期上游水位3.0m
        h_downstream = 2.3  # 洪水期下游水位2.3m
        
        print(f"\n校核条件:")
        print(f"  校核流量: {Q_check} m³/s")
        print(f"  上游水位: {h_upstream} m")
        print(f"  下游水位: {h_downstream} m")
        
        # 闸门全开
        opening = self.params.max_height
        Q_max = self.compute_discharge(opening, h_upstream, h_downstream)
        
        print(f"\n计算结果:")
        print(f"  闸门开度: {opening} m (全开)")
        print(f"  最大过流能力: {Q_max:.2f} m³/s")
        print(f"  校核流量: {Q_check} m³/s")
        
        if Q_max >= Q_check:
            print(f"  ✓ 满足校核要求 (余量{(Q_max/Q_check-1)*100:.1f}%)")
        else:
            print(f"  ✗ 不满足要求!")
        
        return {
            'max_discharge': Q_max,
            'check_discharge': Q_check,
            'passed': Q_max >= Q_check
        }
    
    def generate_discharge_table(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        步骤3: 生成流量-开度关系表
        
        用途: 运行操作手册
        """
        print("\n" + "="*70)
        print("  静态设计: 流量-开度关系表")
        print("="*70)
        
        # 固定水位条件(正常运行)
        h_upstream = 2.5
        h_downstream = 2.0
        
        print(f"\n计算条件: 上游{h_upstream}m, 下游{h_downstream}m")
        print(f"\n{'开度(m)':<12}{'流量(m³/s)':<15}{'备注'}")
        print("-" * 50)
        
        openings = np.linspace(0.5, self.params.max_height, 10)
        discharges = []
        
        for opening in openings:
            Q = self.compute_discharge(opening, h_upstream, h_downstream)
            discharges.append(Q)
            
            remark = ""
            if abs(Q - self.params.design_flow) < 0.5:
                remark = "← 设计流量"
            
            print(f"{opening:<12.2f}{Q:<15.2f}{remark}")
        
        return openings, np.array(discharges)
    
    def plot_discharge_curve(self, openings: np.ndarray, discharges: np.ndarray):
        """
        绘制流量-开度曲线
        """
        plt.figure(figsize=(10, 6))
        plt.plot(openings, discharges, 'b-', linewidth=2, label='流量-开度曲线')
        plt.axhline(y=self.params.design_flow, color='r', linestyle='--', 
                   label=f'设计流量 {self.params.design_flow} m³/s')
        plt.axhline(y=self.params.check_flow, color='orange', linestyle='--', 
                   label=f'校核流量 {self.params.check_flow} m³/s')
        
        plt.xlabel('闸门开度 (m)', fontsize=12)
        plt.ylabel('过闸流量 (m³/s)', fontsize=12)
        plt.title('静态设计: 闸门流量-开度关系曲线', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        plt.tight_layout()
        plt.savefig('static_design_discharge_curve.png', dpi=150)
        print("\n✓ 流量-开度曲线已保存: static_design_discharge_curve.png")
    
    def generate_operation_manual(self):
        """
        步骤4: 生成运行操作手册(静态文档)
        """
        print("\n" + "="*70)
        print("  静态设计: 运行操作手册")
        print("="*70)
        
        manual = f"""
运行操作手册
=============

一、闸门设计参数
    闸孔宽度: {self.params.width} m
    闸门高度: {self.params.max_height} m
    流量系数: {self.params.discharge_coef}
    设计流量: {self.params.design_flow} m³/s
    校核流量: {self.params.check_flow} m³/s

二、操作规程
    1. 正常工况(灌溉季)
       - 上游水位: 2.5m
       - 下游目标水位: 2.0m
       - 推荐开度: 1.5-1.8m
       - 对应流量: 10-12 m³/s
    
    2. 高峰工况
       - 上游水位: 3.0m
       - 下游目标水位: 2.3m
       - 推荐开度: 2.0-2.5m
       - 对应流量: 13-15 m³/s
    
    3. 泄洪工况
       - 闸门全开(3.0m)
       - 最大过流能力: 约18 m³/s

三、调节方法
    1. 根据下游水位人工判断是否需要调节
    2. 参考流量-开度表选择开度
    3. 手动/电动启闭机调节闸门
    4. 观察水位变化,逐步微调
    5. 达到目标后保持开度

四、注意事项
    1. 调节速度不宜过快(避免水锤)
    2. 每次调节后观察10-15分钟
    3. 夜间一般不调节(无人值守)
    4. 异常情况及时报告

五、巡查要求
    1. 每日巡查2次(上午、下午)
    2. 记录上下游水位、闸门开度
    3. 检查启闭机、闸门运行状态
    4. 发现问题及时处理或报告
"""
        print(manual)
        
        with open('static_design_operation_manual.txt', 'w', encoding='utf-8') as f:
            f.write(manual)
        
        print("\n✓ 操作手册已保存: static_design_operation_manual.txt")


def main():
    """
    主函数: 静态设计完整流程
    """
    print("\n" + "="*70)
    print("  静态设计案例: 灌溉渠道闸门水力计算")
    print("  设计标准: GB 50288-2018 《灌溉与排水工程设计标准》")
    print("="*70)
    
    # 设计参数
    params = GateDesignParameters(
        width=0,  # 待设计
        max_height=0,  # 待设计
        discharge_coef=0.85,  # 流量系数(经验值)
        design_flow=10.0,  # 设计流量10 m³/s
        check_flow=15.0   # 校核流量15 m³/s
    )
    
    # 创建设计对象
    designer = StaticGateDesign(params)
    
    # 设计流程
    print("\n【静态设计流程】")
    print("="*70)
    
    # 步骤1: 闸门尺寸设计
    design_result = designer.design_gate_size()
    
    # 步骤2: 校核最大流量
    check_result = designer.check_max_flow()
    
    # 步骤3: 生成流量-开度关系表
    openings, discharges = designer.generate_discharge_table()
    
    # 步骤4: 绘制流量-开度曲线
    designer.plot_discharge_curve(openings, discharges)
    
    # 步骤5: 生成操作手册
    designer.generate_operation_manual()
    
    # 设计总结
    print("\n" + "="*70)
    print("  静态设计总结")
    print("="*70)
    print(f"\n设计参数:")
    print(f"  闸孔宽度: {params.width} m")
    print(f"  闸门高度: {params.max_height} m")
    print(f"  设计流量: {params.design_flow} m³/s")
    print(f"  最大流量: {check_result['max_discharge']:.2f} m³/s")
    
    print(f"\n设计特点:")
    print(f"  ✓ 计算工况: 仅2个(设计+校核)")
    print(f"  ✓ 运行方式: 人工调度")
    print(f"  ✓ 交付物: 设计参数表 + 操作手册(静态文档)")
    print(f"  ✓ 设计周期: 1-2天")
    print(f"  ✓ 投资: 30万元")
    
    print(f"\n存在问题:")
    print(f"  ✗ 只考虑典型工况,应对复杂变化能力弱")
    print(f"  ✗ 人工调度,响应慢(30-60分钟)")
    print(f"  ✗ 夜间无人值守")
    print(f"  ✗ 依赖人工经验")
    print(f"  ✗ 下游水位波动大(±0.3m)")
    
    print("\n" + "="*70)
    print("  静态设计完成!")
    print("  下一步: 查看动态设计案例(L2、L3级)了解智能化改进")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
