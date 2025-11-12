#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目21: 静水压力计算
案例：水库大坝静水压力
"""
import numpy as np

def main():
    print("="*60)
    print("项目21: 静水压力计算 - 水库大坝")
    print("="*60)
    
    # 参数
    H = 50.0  # 水深(m)
    B = 100.0  # 坝宽(m)
    rho = 1000  # 水密度(kg/m³)
    g = 9.81  # 重力加速度(m/s²)
    
    print(f"\n水库参数:")
    print(f"  水深: {H} m")
    print(f"  坝宽: {B} m")
    
    # 压力计算
    p_surface = 0  # 水面压力
    p_bottom = rho * g * H  # 坝底压力
    
    print(f"\n压力分布:")
    print(f"  水面压力: {p_surface/1000:.1f} kPa")
    print(f"  坝底压力: {p_bottom/1000:.1f} kPa")
    
    # 总压力（合力）
    F = 0.5 * rho * g * H**2 * B
    
    # 作用点（形心）
    y_cp = H / 3  # 距坝底
    
    print(f"\n总压力:")
    print(f"  合力: {F/1e6:.2f} MN")
    print(f"  作用点距坝底: {y_cp:.2f} m")
    print(f"  作用点距水面: {H - y_cp:.2f} m")
    
    print("\n✅ 项目21完成！")

if __name__ == "__main__":
    main()
