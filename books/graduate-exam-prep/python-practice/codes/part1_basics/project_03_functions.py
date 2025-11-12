#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目3: Python函数与模块

课程目标：
1. 掌握函数的定义和调用
2. 理解参数传递（位置参数、关键字参数、默认参数）
3. 学习返回值和返回多个值
4. 掌握lambda表达式
5. 理解模块的导入和使用
6. 应用于水力计算函数库

工程案例：
构建一个水力学计算函数库，包含常用公式和计算方法

作者：Python编程实战教材组
日期：2025-11-12
"""

import math

# ============================================================
# 1. 基本函数定义
# ============================================================

def calculate_flow_area(width, depth):
    """
    计算矩形渠道过水断面积
    
    参数:
        width: 渠道宽度 (m)
        depth: 水深 (m)
    
    返回:
        area: 过水断面积 (m²)
    """
    area = width * depth
    return area


def calculate_wetted_perimeter(width, depth):
    """计算矩形渠道湿周"""
    perimeter = width + 2 * depth
    return perimeter


def calculate_hydraulic_radius(width, depth):
    """
    计算水力半径
    
    R = A / P
    """
    area = calculate_flow_area(width, depth)
    perimeter = calculate_wetted_perimeter(width, depth)
    radius = area / perimeter
    return radius


# ============================================================
# 2. 参数传递方式
# ============================================================

def calculate_manning_flow(width, depth, slope, roughness=0.025):
    """
    Manning公式计算流量（带默认参数）
    
    Q = (1/n) * A * R^(2/3) * i^(1/2)
    
    参数:
        width: 渠道宽度 (m)
        depth: 水深 (m)
        slope: 渠底坡度
        roughness: 糙率系数，默认0.025（混凝土）
    
    返回:
        flow_rate: 流量 (m³/s)
    """
    area = calculate_flow_area(width, depth)
    radius = calculate_hydraulic_radius(width, depth)
    
    flow_rate = (1.0 / roughness) * area * (radius ** (2.0/3.0)) * (slope ** 0.5)
    
    return flow_rate


def analyze_pipe_flow(diameter, length, flow_rate, roughness=0.0002, 
                      fluid_density=1000, fluid_viscosity=0.001):
    """
    管道流动综合分析（多个默认参数）
    
    参数:
        diameter: 管道直径 (m)
        length: 管道长度 (m)
        flow_rate: 流量 (m³/s)
        roughness: 绝对粗糙度 (m)，默认0.0002（钢管）
        fluid_density: 流体密度 (kg/m³)，默认1000（水）
        fluid_viscosity: 动力粘度 (Pa·s)，默认0.001（水）
    
    返回:
        字典包含：velocity, reynolds_number, friction_factor, head_loss
    """
    # 计算流速
    area = math.pi * (diameter / 2) ** 2
    velocity = flow_rate / area
    
    # 计算雷诺数
    reynolds = fluid_density * velocity * diameter / fluid_viscosity
    
    # 计算摩阻系数（简化Colebrook公式）
    if reynolds < 2300:
        friction = 64 / reynolds
    else:
        # Swamee-Jain近似
        term1 = roughness / (3.7 * diameter)
        term2 = 5.74 / (reynolds ** 0.9)
        friction = 0.25 / (math.log10(term1 + term2)) ** 2
    
    # 计算水头损失
    head_loss = friction * (length / diameter) * (velocity ** 2) / (2 * 9.81)
    
    return {
        'velocity': velocity,
        'reynolds_number': reynolds,
        'friction_factor': friction,
        'head_loss': head_loss
    }


# ============================================================
# 3. 返回多个值
# ============================================================

def calculate_weir_flow(width, head, weir_type='sharp'):
    """
    堰流计算，返回多个值
    
    参数:
        width: 堰宽 (m)
        head: 堰上水头 (m)
        weir_type: 堰型（'sharp'薄壁堰, 'broad'宽顶堰）
    
    返回:
        flow_rate: 流量 (m³/s)
        flow_coefficient: 流量系数
        velocity: 过堰流速 (m/s)
    """
    g = 9.81
    
    if weir_type == 'sharp':
        coefficient = 0.42
    elif weir_type == 'broad':
        coefficient = 0.385
    else:
        coefficient = 0.40
    
    # 流量计算
    flow_rate = coefficient * width * math.sqrt(2 * g) * (head ** 1.5)
    
    # 过堰流速
    velocity = math.sqrt(2 * g * head)
    
    return flow_rate, coefficient, velocity


def analyze_channel_section(width, depth, slope, roughness):
    """
    渠道断面综合分析，返回多个结果
    
    返回: (area, perimeter, radius, velocity, flow_rate, froude)
    """
    # 几何参数
    area = width * depth
    perimeter = width + 2 * depth
    radius = area / perimeter
    
    # 流速（Manning公式）
    velocity = (1.0 / roughness) * (radius ** (2.0/3.0)) * (slope ** 0.5)
    
    # 流量
    flow_rate = area * velocity
    
    # Froude数
    froude = velocity / math.sqrt(9.81 * depth)
    
    return area, perimeter, radius, velocity, flow_rate, froude


# ============================================================
# 4. Lambda表达式
# ============================================================

# 简单的lambda函数
area_rectangle = lambda w, h: w * h
area_triangle = lambda b, h: 0.5 * b * h
area_circle = lambda r: math.pi * r ** 2

# 水力计算中的lambda应用
reynolds_number = lambda v, d, nu: v * d / nu
froude_number = lambda v, g, h: v / math.sqrt(g * h)
darcy_friction = lambda f, L, d, v, g: f * (L / d) * (v ** 2) / (2 * g)


def demonstrate_lambda():
    """演示lambda表达式"""
    print("="*60)
    print("Lambda表达式应用")
    print("="*60)
    
    # 面积计算
    print(f"\n面积计算:")
    print(f"  矩形(10m×5m): {area_rectangle(10, 5)} m²")
    print(f"  三角形(底8m,高6m): {area_triangle(8, 6)} m²")
    print(f"  圆形(半径3m): {area_circle(3):.2f} m²")
    
    # 水力参数计算
    print(f"\n水力参数计算:")
    v, d, nu = 2.5, 0.5, 1e-6
    Re = reynolds_number(v, d, nu)
    print(f"  流速={v}m/s, 直径={d}m, 运动粘度={nu}m²/s")
    print(f"  雷诺数: {Re:.0f}")
    
    Fr = froude_number(2.0, 9.81, 3.0)
    print(f"  流速=2.0m/s, 水深=3.0m")
    print(f"  Froude数: {Fr:.3f}")
    
    # 使用lambda进行数据处理
    water_levels = [125.6, 126.3, 127.8, 125.9, 124.8]
    avg_level = (lambda x: sum(x) / len(x))(water_levels)
    print(f"\n数据处理:")
    print(f"  水位序列: {water_levels}")
    print(f"  平均水位: {avg_level:.2f} m")


# ============================================================
# 5. 工程应用：水力学函数库
# ============================================================

class HydraulicsLibrary:
    """水力学计算函数库"""
    
    @staticmethod
    def darcy_weisbach(friction_factor, length, diameter, velocity):
        """Darcy-Weisbach公式计算水头损失"""
        g = 9.81
        head_loss = friction_factor * (length / diameter) * (velocity ** 2) / (2 * g)
        return head_loss
    
    @staticmethod
    def colebrook_white(roughness, diameter, reynolds):
        """Colebrook-White公式求摩阻系数（显式近似）"""
        relative_roughness = roughness / diameter
        term1 = relative_roughness / 3.7
        term2 = 5.74 / (reynolds ** 0.9)
        friction = 0.25 / (math.log10(term1 + term2)) ** 2
        return friction
    
    @staticmethod
    def manning_velocity(hydraulic_radius, slope, roughness):
        """Manning公式计算流速"""
        velocity = (1.0 / roughness) * (hydraulic_radius ** (2.0/3.0)) * (slope ** 0.5)
        return velocity
    
    @staticmethod
    def critical_depth_rectangular(flow_rate, width):
        """矩形断面临界水深"""
        g = 9.81
        q = flow_rate / width  # 单宽流量
        depth_critical = (q ** 2 / g) ** (1.0 / 3.0)
        return depth_critical
    
    @staticmethod
    def hydraulic_jump_conjugate_depth(depth1, froude1):
        """水跃共轭水深"""
        depth2 = (depth1 / 2) * (math.sqrt(1 + 8 * froude1 ** 2) - 1)
        return depth2
    
    @staticmethod
    def energy_loss_in_jump(depth1, depth2):
        """水跃能量损失"""
        energy_loss = ((depth2 - depth1) ** 3) / (4 * depth1 * depth2)
        return energy_loss


def comprehensive_example():
    """综合应用案例"""
    print("\n" + "="*60)
    print("综合案例：供水管道系统设计")
    print("="*60)
    
    # 设计参数
    design_flow = 0.5  # m³/s
    pipe_length = 5000  # m
    pipe_diameter = 0.6  # m
    pipe_roughness = 0.0002  # m (钢管)
    
    print(f"\n设计参数:")
    print(f"  设计流量: {design_flow} m³/s")
    print(f"  管道长度: {pipe_length} m")
    print(f"  管道直径: {pipe_diameter} m")
    print(f"  绝对粗糙度: {pipe_roughness} m")
    
    # 使用函数进行计算
    result = analyze_pipe_flow(
        diameter=pipe_diameter,
        length=pipe_length,
        flow_rate=design_flow,
        roughness=pipe_roughness
    )
    
    print(f"\n水力计算结果:")
    print(f"  流速: {result['velocity']:.2f} m/s")
    print(f"  雷诺数: {result['reynolds_number']:.0f}")
    print(f"  摩阻系数: {result['friction_factor']:.4f}")
    print(f"  水头损失: {result['head_loss']:.2f} m")
    
    # 判断流态
    if result['reynolds_number'] < 2300:
        flow_regime = "层流"
    elif result['reynolds_number'] < 4000:
        flow_regime = "过渡流"
    else:
        flow_regime = "紊流"
    
    print(f"  流态: {flow_regime}")
    
    # 工程建议
    print(f"\n工程建议:")
    if result['velocity'] < 0.6:
        print(f"  ⚠ 流速过低，可能发生淤积")
    elif result['velocity'] > 3.0:
        print(f"  ⚠ 流速过高，注意磨损和水锤")
    else:
        print(f"  ✓ 流速在合理范围内")
    
    if result['head_loss'] > 50:
        print(f"  ⚠ 水头损失较大，建议增大管径")
    else:
        print(f"  ✓ 水头损失在可接受范围内")
    
    return result


def main():
    """主函数"""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "Python函数与模块应用" + " "*16 + "║")
    print("║" + " "*13 + "案例：水力学计算函数库" + " "*14 + "║")
    print("╚" + "═"*58 + "╝")
    
    # 1. 基本函数调用
    print("\n" + "="*60)
    print("1. 基本函数应用")
    print("="*60)
    
    w, h = 10.0, 3.0
    print(f"\n矩形渠道: 宽度={w}m, 水深={h}m")
    print(f"  过水面积: {calculate_flow_area(w, h)} m²")
    print(f"  湿周: {calculate_wetted_perimeter(w, h)} m")
    print(f"  水力半径: {calculate_hydraulic_radius(w, h):.3f} m")
    
    # 2. 带默认参数的函数
    print("\n" + "="*60)
    print("2. 默认参数应用")
    print("="*60)
    
    Q1 = calculate_manning_flow(10, 3, 0.001)
    Q2 = calculate_manning_flow(10, 3, 0.001, roughness=0.030)
    
    print(f"\nManning公式计算流量:")
    print(f"  使用默认糙率(0.025): {Q1:.2f} m³/s")
    print(f"  指定糙率(0.030): {Q2:.2f} m³/s")
    
    # 3. 返回多个值
    print("\n" + "="*60)
    print("3. 返回多个值")
    print("="*60)
    
    Q, C, V = calculate_weir_flow(5.0, 0.5, 'sharp')
    print(f"\n薄壁堰流量计算:")
    print(f"  堰宽: 5.0 m")
    print(f"  堰上水头: 0.5 m")
    print(f"  流量: {Q:.2f} m³/s")
    print(f"  流量系数: {C}")
    print(f"  流速: {V:.2f} m/s")
    
    # 4. Lambda表达式
    demonstrate_lambda()
    
    # 5. 函数库应用
    print("\n" + "="*60)
    print("5. 水力学函数库应用")
    print("="*60)
    
    lib = HydraulicsLibrary()
    
    print(f"\n临界水深计算:")
    Q, B = 50, 10
    hc = lib.critical_depth_rectangular(Q, B)
    print(f"  流量={Q}m³/s, 宽度={B}m")
    print(f"  临界水深: {hc:.3f} m")
    
    print(f"\n水跃计算:")
    h1, Fr1 = 1.5, 3.0
    h2 = lib.hydraulic_jump_conjugate_depth(h1, Fr1)
    E_loss = lib.energy_loss_in_jump(h1, h2)
    print(f"  跃前水深={h1}m, Froude数={Fr1}")
    print(f"  跃后水深: {h2:.3f} m")
    print(f"  能量损失: {E_loss:.3f} m")
    
    # 6. 综合案例
    result = comprehensive_example()
    
    # 总结
    print("\n" + "="*60)
    print("学习总结")
    print("="*60)
    print("""
本项目学习内容：
1. ✅ 函数定义与调用
2. ✅ 参数传递（位置参数、关键字参数、默认参数）
3. ✅ 返回值（单个值、多个值）
4. ✅ Lambda表达式
5. ✅ 静态方法（@staticmethod）
6. ✅ 函数库设计

工程应用：
• 构建水力学计算函数库
• 管道流动分析
• 明渠流动计算
• 堰流计算
• 水跃分析

最佳实践：
• 函数名使用动词，清晰表达功能
• 使用docstring编写函数文档
• 合理设置默认参数值
• 返回值类型保持一致
• 将相关函数组织成类/模块
    """)
    
    print("="*60)
    print("项目3完成！")
    print("="*60)


if __name__ == "__main__":
    main()
