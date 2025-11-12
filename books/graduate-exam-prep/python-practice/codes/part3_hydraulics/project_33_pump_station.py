#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目33: 泵站设计计算
案例：灌溉泵站设计
"""
import numpy as np

def main():
    print("="*60)
    print("项目33: 泵站设计 - 灌溉泵站")
    print("="*60)
    
    # 设计参数
    Q_design = 5.0  # 设计流量(m³/s)
    H_geom = 15.0   # 几何扬程(m)
    L_suction = 50   # 吸水管长(m)
    L_delivery = 200 # 压水管长(m)
    d = 0.8          # 管径(m)
    
    print(f"\n设计参数:")
    print(f"  设计流量: {Q_design} m³/s")
    print(f"  几何扬程: {H_geom} m")
    print(f"  吸水管长: {L_suction} m")
    print(f"  压水管长: {L_delivery} m")
    
    # 流速
    A = np.pi * (d/2)**2
    v = Q_design / A
    
    # 水头损失估算
    h_f_suction = 0.5  # 吸水管损失(m)
    h_f_delivery = 2.0  # 压水管损失(m)
    h_local = 1.0  # 局部损失(m)
    
    # 总扬程
    H_total = H_geom + h_f_suction + h_f_delivery + h_local
    
    print(f"\n水力计算:")
    print(f"  吸水管流速: {v:.2f} m/s")
    print(f"  吸水管损失: {h_f_suction:.2f} m")
    print(f"  压水管损失: {h_f_delivery:.2f} m")
    print(f"  局部损失: {h_local:.2f} m")
    print(f"  总扬程: {H_total:.2f} m")
    
    # 功率计算
    rho = 1000
    g = 9.81
    eta = 0.75  # 效率
    P = rho * g * Q_design * H_total / (1000 * eta)
    
    print(f"\n泵选型:")
    print(f"  水力功率: {rho*g*Q_design*H_total/1000:.1f} kW")
    print(f"  轴功率: {P:.1f} kW")
    print(f"  装机功率: {P*1.1:.1f} kW (1.1安全系数)")
    
    # 台数确定
    n_pumps = 3
    Q_unit = Q_design / n_pumps
    print(f"\n机组配置:")
    print(f"  台数: {n_pumps}台")
    print(f"  单泵流量: {Q_unit:.2f} m³/s")
    print(f"  单泵扬程: {H_total:.2f} m")
    
    print("\n✅ 项目33完成！")

if __name__ == "__main__":
    main()
