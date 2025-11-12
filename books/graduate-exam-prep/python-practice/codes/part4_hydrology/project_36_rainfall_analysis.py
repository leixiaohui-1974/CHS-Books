#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目36: 降雨统计分析
案例：设计暴雨计算
"""
import numpy as np

def main():
    print("="*60)
    print("项目36: 降雨统计分析")
    print("="*60)
    
    # 年最大降雨量序列
    rainfall = np.array([120, 95, 145, 87, 156, 112, 98, 134, 
                        108, 142, 89, 125, 167, 91, 138])
    
    print(f"\n年最大降雨序列（{len(rainfall)}年）:")
    print(rainfall)
    
    # 统计特征
    mean = np.mean(rainfall)
    std = np.std(rainfall, ddof=1)
    cv = std / mean
    cs = 2 * cv  # 简化：偏态系数=2*变差系数
    
    print(f"\n统计参数:")
    print(f"  均值: {mean:.2f} mm")
    print(f"  标准差: {std:.2f} mm")
    print(f"  变差系数Cv: {cv:.3f}")
    print(f"  偏态系数Cs: {cs:.3f}")
    
    # 设计值（P-III分布）
    frequencies = [0.01, 0.02, 0.05, 0.1, 0.2]
    print(f"\n设计降雨量:")
    for p in frequencies:
        # 简化计算
        Kp = 1 + cv * (2/cs) * ((1 - p)**(cs/2) - 1)
        Xp = mean * Kp
        print(f"  P={p*100:.0f}%: {Xp:.1f} mm (重现期{1/p:.0f}年)")
    
    print("\n✅ 项目36完成！")

if __name__ == "__main__":
    main()
