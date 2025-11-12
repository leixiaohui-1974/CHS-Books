#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目37: 频率分析
案例：设计洪水计算
"""
import numpy as np

def pearson3_frequency(data, frequencies):
    """P-III型频率分析"""
    n = len(data)
    mean = np.mean(data)
    
    # 计算统计参数
    cv = np.std(data, ddof=1) / mean
    
    # 计算偏态系数
    m3 = np.sum((data - mean)**3) / n
    cs = m3 / (mean * cv)**3
    
    results = []
    for p in frequencies:
        # Φ值查表（简化计算）
        if cs != 0:
            phi = ((1 - p)**(cs/2) - 1) * 2 / cs
        else:
            phi = 0
        Kp = 1 + cv * phi
        Xp = mean * Kp
        results.append((p, Xp))
    
    return results, cv, cs

def main():
    print("="*60)
    print("项目37: 频率分析 - 设计洪水")
    print("="*60)
    
    # 年最大洪峰流量序列
    floods = np.array([5200, 4800, 6500, 4200, 7200, 5600, 
                       4900, 6100, 5400, 6800, 4500, 5900])
    
    print(f"\n洪峰流量序列（{len(floods)}年）:")
    print(floods)
    
    # 频率分析
    freqs = [0.01, 0.02, 0.05, 0.1, 0.2]
    results, cv, cs = pearson3_frequency(floods, freqs)
    
    print(f"\n统计参数:")
    print(f"  均值: {np.mean(floods):.0f} m³/s")
    print(f"  Cv: {cv:.3f}")
    print(f"  Cs: {cs:.3f}")
    
    print(f"\n设计洪峰流量:")
    for p, q in results:
        print(f"  P={p*100:.0f}%: {q:.0f} m³/s (重现期{1/p:.0f}年)")
    
    print("\n✅ 项目37完成！")

if __name__ == "__main__":
    main()
