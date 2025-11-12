#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目6: NumPy数组操作
案例：水深流速数据处理
"""
import numpy as np

def main():
    print("="*60)
    print("项目6: NumPy数组操作 - 水深流速数据处理")
    print("="*60)
    
    # 1. 数组创建
    depths = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    velocities = np.array([1.2, 1.6, 1.9, 2.2, 2.4, 2.6])
    
    print(f"\n水深: {depths}")
    print(f"流速: {velocities}")
    
    # 2. 计算流量（Q = A * v, 假设宽度10m）
    width = 10.0
    areas = width * depths
    flows = areas * velocities
    
    print(f"\n断面积: {areas}")
    print(f"流量: {flows}")
    print(f"平均流量: {np.mean(flows):.2f} m³/s")
    print(f"最大流量: {np.max(flows):.2f} m³/s")
    
    # 3. 数组运算
    froude = velocities / np.sqrt(9.81 * depths)
    print(f"\nFroude数: {froude}")
    print(f"流态: {['急流' if f > 1 else '缓流' for f in froude]}")
    
    # 4. 统计分析
    print(f"\n统计结果:")
    print(f"  水深均值: {np.mean(depths):.2f} m")
    print(f"  水深标准差: {np.std(depths):.3f} m")
    print(f"  流速均值: {np.mean(velocities):.2f} m/s")
    
    print("\n✅ 项目6完成！")

if __name__ == "__main__":
    main()
