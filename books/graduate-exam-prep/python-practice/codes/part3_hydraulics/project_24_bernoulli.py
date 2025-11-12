#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目24: Bernoulli方程应用
案例：虹吸管流量计算
"""
import numpy as np

def main():
    print("="*60)
    print("项目24: Bernoulli方程 - 虹吸管")
    print("="*60)
    
    # 虹吸管参数
    z1 = 10.0  # 上游水位(m)
    z2 = 0.0   # 下游水位(m)
    z_top = 12.0  # 虹吸管顶部高程(m)
    d = 0.5  # 管径(m)
    g = 9.81
    
    print(f"\n虹吸管参数:")
    print(f"  上游水位: {z1} m")
    print(f"  下游水位: {z2} m")
    print(f"  管顶高程: {z_top} m")
    print(f"  管径: {d} m")
    
    # Bernoulli方程（忽略损失）
    v = np.sqrt(2 * g * (z1 - z2))
    A = np.pi * (d/2)**2
    Q = A * v
    
    print(f"\n流速和流量:")
    print(f"  流速: {v:.2f} m/s")
    print(f"  流量: {Q:.2f} m³/s")
    
    # 顶部压力
    v_top = v  # 假设等截面
    p_top = -rho * g * (z_top - z1 + v_top**2/(2*g))
    
    print(f"\n管顶真空度:")
    print(f"  压力水头: {p_top/(rho*g):.2f} m")
    print(f"  绝对压力: {p_top/1000:.1f} kPa")
    
    if p_top < -90000:
        print(f"  ⚠ 真空度过大，可能发生气穴！")
    
    print("\n✅ 项目24完成！")

rho = 1000
if __name__ == "__main__":
    main()
