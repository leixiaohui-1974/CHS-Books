#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目52: 洪水演进计算
案例：河道洪水演进
"""
import numpy as np

def main():
    print("="*60)
    print("项目52: 洪水演进计算")
    print("="*60)
    
    # Muskingum法参数
    K = 2.0  # 流量传播时间(h)
    x = 0.2  # 权重系数
    dt = 1.0  # 时间步长(h)
    
    print(f"\nMuskingum参数:")
    print(f"  K = {K} h")
    print(f"  x = {x}")
    print(f"  Δt = {dt} h")
    
    # 入流过程
    I = np.array([100, 150, 250, 400, 600, 800, 900, 850, 
                  700, 500, 300, 200, 150, 120])
    
    # 计算系数
    C0 = (-K*x + 0.5*dt) / (K - K*x + 0.5*dt)
    C1 = (K*x + 0.5*dt) / (K - K*x + 0.5*dt)
    C2 = (K - K*x - 0.5*dt) / (K - K*x + 0.5*dt)
    
    print(f"\n演算系数:")
    print(f"  C0 = {C0:.3f}")
    print(f"  C1 = {C1:.3f}")
    print(f"  C2 = {C2:.3f}")
    print(f"  C0+C1+C2 = {C0+C1+C2:.3f}")
    
    # 洪水演进
    Q = np.zeros(len(I))
    Q[0] = I[0]
    
    for i in range(1, len(I)):
        Q[i] = C0*I[i] + C1*I[i-1] + C2*Q[i-1]
    
    print(f"\n演进结果:")
    print(f"  入流洪峰: {np.max(I):.0f} m³/s")
    print(f"  出流洪峰: {np.max(Q):.0f} m³/s")
    print(f"  削峰: {(np.max(I)-np.max(Q))/np.max(I)*100:.1f}%")
    print(f"  峰现时差: {np.argmax(Q)-np.argmax(I)} h")
    
    print("\n✅ 项目52完成！")

if __name__ == "__main__":
    main()
