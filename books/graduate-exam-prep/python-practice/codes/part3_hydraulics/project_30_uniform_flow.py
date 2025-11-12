#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目30: 明渠均匀流
案例：灌溉渠道设计
"""
import numpy as np

def manning_flow(b, h, i, n):
    """Manning公式计算流量"""
    A = b * h
    P = b + 2 * h
    R = A / P
    v = (1/n) * (R**(2/3)) * (i**0.5)
    Q = A * v
    return Q, v, A, R

def main():
    print("="*60)
    print("项目30: 明渠均匀流 - 灌溉渠道")
    print("="*60)
    
    # 渠道参数
    b = 10.0   # 底宽(m)
    h = 2.0    # 水深(m)
    i = 0.0005 # 坡度
    n = 0.025  # 糙率
    
    print(f"\n渠道参数:")
    print(f"  底宽: {b} m")
    print(f"  设计水深: {h} m")
    print(f"  渠底坡度: {i}")
    print(f"  Manning糙率: {n}")
    
    # 计算
    Q, v, A, R = manning_flow(b, h, i, n)
    
    print(f"\n水力计算结果:")
    print(f"  过水面积: {A:.2f} m²")
    print(f"  水力半径: {R:.3f} m")
    print(f"  流速: {v:.2f} m/s")
    print(f"  流量: {Q:.2f} m³/s")
    
    # Froude数
    Fr = v / np.sqrt(9.81 * h)
    print(f"  Froude数: {Fr:.3f}")
    
    if Fr < 1:
        print(f"  流态: 缓流")
    elif Fr > 1:
        print(f"  流态: 急流")
    else:
        print(f"  流态: 临界流")
    
    # 设计校核
    if 0.6 <= v <= 2.5:
        print(f"  ✓ 流速在合理范围")
    else:
        print(f"  ⚠ 流速需要调整")
    
    print("\n✅ 项目30完成！")

if __name__ == "__main__":
    main()
