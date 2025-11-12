#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目51: 水库优化调度
案例：多目标优化调度
"""
import numpy as np

def main():
    print("="*60)
    print("项目51: 水库优化调度")
    print("="*60)
    
    print("\n多目标优化:")
    print("  目标1: 最大发电量")
    print("  目标2: 保障供水")
    print("  目标3: 防洪安全")
    
    # 简化的优化问题
    months = 12
    V_init = 20000  # 初始库容(万m³)
    V_target = 25000  # 目标库容
    
    print(f"\n优化条件:")
    print(f"  初始库容: {V_init}万m³")
    print(f"  目标库容: {V_target}万m³")
    print(f"  优化时段: {months}个月")
    
    # 模拟入流
    inflows = np.array([800, 900, 1200, 1500, 2000, 2500,
                       3000, 2800, 2200, 1800, 1200, 1000])
    
    print(f"\n入流过程(万m³/月):")
    print(inflows)
    
    # 简单调度规则
    releases = []
    volumes = [V_init]
    
    for i in range(months):
        V_current = volumes[-1]
        I = inflows[i]
        
        # 调度规则
        if V_current > V_target:
            R = I + (V_current - V_target) * 0.3
        else:
            R = I * 0.8
        
        V_next = V_current + I - R
        releases.append(R)
        volumes.append(V_next)
    
    print(f"\n调度结果:")
    print(f"  最终库容: {volumes[-1]:.0f}万m³")
    print(f"  平均下泄: {np.mean(releases):.0f}万m³/月")
    print(f"  总发电量: {sum(releases)*0.8:.0f}万kW·h")
    
    print("\n✅ 项目51完成！")

if __name__ == "__main__":
    main()
