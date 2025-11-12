#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目27: 有压管流计算
案例：长距离输水管道
"""
import numpy as np

def main():
    print("="*60)
    print("项目27: 有压管流 - 输水管道")
    print("="*60)
    
    # 管道参数
    L = 10000  # 管长(m)
    d = 1.0    # 管径(m)
    Q = 1.0    # 流量(m³/s)
    epsilon = 0.0002  # 粗糙度(m)
    nu = 1e-6  # 运动粘度(m²/s)
    g = 9.81
    
    print(f"\n管道参数:")
    print(f"  管长: {L/1000:.1f} km")
    print(f"  管径: {d} m")
    print(f"  流量: {Q} m³/s")
    
    # 流速
    A = np.pi * (d/2)**2
    v = Q / A
    
    # 雷诺数
    Re = v * d / nu
    
    print(f"\n水力参数:")
    print(f"  流速: {v:.2f} m/s")
    print(f"  雷诺数: {Re:.0f}")
    
    # 摩阻系数（Swamee-Jain）
    term1 = epsilon / (3.7 * d)
    term2 = 5.74 / (Re ** 0.9)
    f = 0.25 / (np.log10(term1 + term2)) ** 2
    
    # 水头损失
    h_f = f * (L / d) * (v**2 / (2 * g))
    
    print(f"  摩阻系数: {f:.4f}")
    print(f"  沿程损失: {h_f:.2f} m")
    print(f"  水力坡度: {h_f/L:.6f}")
    
    # 所需扬程
    H_pump = h_f + 0  # 加上高程差
    P = rho * g * Q * H_pump / 1000  # kW
    
    print(f"\n泵站参数:")
    print(f"  所需扬程: {H_pump:.2f} m")
    print(f"  理论功率: {P:.1f} kW")
    
    print("\n✅ 项目27完成！")

rho = 1000
if __name__ == "__main__":
    main()
