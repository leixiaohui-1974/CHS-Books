#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目7: Matplotlib绘图
案例：水文过程线绘制
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def main():
    print("="*60)
    print("项目7: Matplotlib绘图 - 水文过程线")
    print("="*60)
    
    # 数据
    days = np.arange(1, 31)
    water_levels = 120 + 10 * np.sin(days * 0.5) + np.random.randn(30) * 2
    flows = 3000 + 1000 * np.sin(days * 0.5) + np.random.randn(30) * 200
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 水位过程线
    ax1.plot(days, water_levels, 'b-o', linewidth=2, markersize=4, label='水位')
    ax1.axhline(y=125, color='r', linestyle='--', label='警戒水位')
    ax1.set_xlabel('时间 (天)')
    ax1.set_ylabel('水位 (m)')
    ax1.set_title('水位过程线', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 流量过程线
    ax2.plot(days, flows, 'g-s', linewidth=2, markersize=4, label='流量')
    ax2.fill_between(days, flows, alpha=0.3, color='green')
    ax2.set_xlabel('时间 (天)')
    ax2.set_ylabel('流量 (m³/s)')
    ax2.set_title('流量过程线', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('water_process_lines.png', dpi=100, bbox_inches='tight')
    print("\n✅ 图表已保存: water_process_lines.png")
    print("✅ 项目7完成！")

if __name__ == "__main__":
    main()
