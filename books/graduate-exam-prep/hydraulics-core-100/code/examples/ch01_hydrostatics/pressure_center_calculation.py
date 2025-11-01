#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平面压力中心计算

问题：第一章 - 矩形闸门压力中心计算
描述：计算静水总压力及其作用点（压力中心）

知识点：
1. 静水总压力：P = γ·h_c·A
2. 压力中心深度：y_D = y_c + I_c/(y_c·A)
3. 偏心距：e = y_D - y_c
4. 不同形状的惯性矩

作者：CHS-Books项目组
日期：2025-11-01
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def rectangular_gate_pressure(b, h, h_top, gamma=9810):
    """
    矩形闸门静水总压力
    
    参数:
        b: 闸门宽度 (m)
        h: 闸门高度 (m)
        h_top: 闸门顶部水深 (m)
        gamma: 水的容重 (N/m³)
    
    返回:
        P: 总压力 (N)
        h_c: 形心水深 (m)
        A: 面积 (m²)
    """
    A = b * h
    h_c = h_top + h / 2  # 形心水深
    P = gamma * h_c * A
    return P, h_c, A


def pressure_center_depth(h_c, A, I_c):
    """
    压力中心深度计算
    
    y_D = y_c + I_c/(y_c·A)
    
    参数:
        h_c: 形心深度 (m)
        A: 面积 (m²)
        I_c: 对形心轴的惯性矩 (m⁴)
    
    返回:
        y_D: 压力中心深度 (m)
        e: 偏心距 (m)
    """
    y_D = h_c + I_c / (h_c * A)
    e = y_D - h_c
    return y_D, e


def moment_of_inertia_rectangular(b, h):
    """
    矩形对形心轴惯性矩
    
    I_c = b·h³/12
    
    参数:
        b: 宽度 (m)
        h: 高度 (m)
    
    返回:
        I_c: 惯性矩 (m⁴)
    """
    return b * h**3 / 12


def plot_pressure_center_analysis(filename='pressure_center_calculation.png'):
    """
    绘制压力中心分析图（4子图）
    
    参数:
        filename: 文件名
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 示例参数
    b = 2.0      # 闸门宽度
    h = 3.0      # 闸门高度
    h_top = 2.0  # 顶部水深
    gamma = 9810
    
    # 计算
    A = b * h
    h_c = h_top + h / 2
    I_c = moment_of_inertia_rectangular(b, h)
    P, _, _ = rectangular_gate_pressure(b, h, h_top, gamma)
    y_D, e = pressure_center_depth(h_c, A, I_c)
    
    # 子图1：压力分布与压力中心
    ax1 = axes[0, 0]
    
    # 闸门轮廓
    y_gate = np.array([h_top, h_top+h, h_top+h, h_top, h_top])
    x_gate = np.array([0, 0, 0.5, 0.5, 0])
    ax1.plot(x_gate, y_gate, 'k-', linewidth=3, label='闸门')
    ax1.fill(x_gate, y_gate, alpha=0.2, color='gray')
    
    # 水面
    ax1.axhline(0, color='b', linestyle='--', linewidth=1.5, label='水面')
    ax1.fill_between([0, 2], 0, h_top+h, alpha=0.1, color='cyan')
    
    # 压力分布（三角形）
    p_top = gamma * h_top
    p_bot = gamma * (h_top + h)
    x_pressure = np.array([0, p_top/5000, p_bot/5000, 0])
    y_pressure = np.array([h_top, h_top, h_top+h, h_top+h])
    ax1.plot(x_pressure, y_pressure, 'r-', linewidth=2, label='压力分布')
    ax1.fill(x_pressure, y_pressure, alpha=0.3, color='red')
    
    # 标注形心
    ax1.plot(0.25, h_c, 'go', markersize=12, label=f'形心 h_c={h_c:.2f}m')
    ax1.text(0.35, h_c, f'C\nh_c={h_c:.2f}m', fontsize=10, va='center')
    
    # 标注压力中心
    ax1.plot(0.25, y_D, 'ro', markersize=12, label=f'压力中心 y_D={y_D:.2f}m')
    ax1.text(0.35, y_D, f'D\ny_D={y_D:.2f}m', fontsize=10, va='center')
    
    # 偏心距
    ax1.annotate('', xy=(0.6, y_D), xytext=(0.6, h_c),
                arrowprops=dict(arrowstyle='<->', color='orange', lw=2))
    ax1.text(0.7, (h_c+y_D)/2, f'e={e:.3f}m', fontsize=10, color='orange')
    
    # 总压力箭头
    ax1.arrow(p_bot/5000+0.1, y_D, 0.5, 0, 
             head_width=0.2, head_length=0.1, fc='red', ec='red', linewidth=2)
    ax1.text(p_bot/5000+0.7, y_D+0.3, f'P={P/1000:.1f}kN', fontsize=10, color='red')
    
    ax1.set_xlabel('距离 (m)', fontsize=12)
    ax1.set_ylabel('水深 (m)', fontsize=12)
    ax1.set_title('矩形闸门压力分布与压力中心', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.invert_yaxis()  # 水深向下
    ax1.set_xlim([0, 2])
    
    # 子图2：偏心距随水深变化
    ax2 = axes[0, 1]
    
    h_top_range = np.linspace(0.5, 10, 50)
    e_range = []
    
    for ht in h_top_range:
        hc = ht + h / 2
        _, e_val = pressure_center_depth(hc, A, I_c)
        e_range.append(e_val)
    
    ax2.plot(h_top_range, e_range, 'b-', linewidth=2.5)
    ax2.axvline(h_top, color='r', linestyle='--', linewidth=1.5, 
                label=f'设计水深 h_top={h_top}m')
    ax2.axhline(e, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax2.plot(h_top, e, 'ro', markersize=10)
    
    ax2.set_xlabel('顶部水深 h_top (m)', fontsize=12)
    ax2.set_ylabel('偏心距 e (m)', fontsize=12)
    ax2.set_title('偏心距随水深变化', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：不同形状的惯性矩
    ax3 = axes[1, 0]
    ax3.axis('off')
    
    # 绘制不同形状
    shapes_info = """
    【常见形状惯性矩与压力中心】
    
    1. 矩形（宽b，高h）：
       I_c = b·h³/12
       e = h²/(12h_c)
       y_D = h_c + h²/(12h_c)
    
    2. 三角形（底边b，高h，顶点在上）：
       I_c = b·h³/36
       e = h²/(18h_c)
       y_D = h_c + h²/(18h_c)
    
    3. 圆形（直径D）：
       I_c = πD⁴/64
       e = D²/(16h_c)
       y_D = h_c + D²/(16h_c)
    
    4. 梯形（上底a，下底b，高h）：
       I_c = h³(a²+4ab+b²)/(36(a+b))
       需要数值计算
    
    关键结论：
      • 偏心距e > 0（压力中心在形心下方）
      • 水深越大，e越小
      • e = I_c/(h_c·A)
      • 浅水时偏心距较大
    """
    
    ax3.text(0.05, 0.95, shapes_info, transform=ax3.transAxes,
             fontsize=10, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    # 子图4：计算结果表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # 计算更多参数
    p_c = gamma * h_c  # 形心处压强
    p_D = gamma * y_D  # 压力中心处压强
    M_bottom = P * (h_top + h - y_D)  # 对闸门底部的力矩
    
    results_text = f"""
    【计算结果详表】
    
    闸门参数：
      宽度 b = {b:.1f} m
      高度 h = {h:.1f} m
      顶部水深 h_top = {h_top:.1f} m
      底部水深 h_bot = {h_top+h:.1f} m
    
    几何特性：
      面积 A = {A:.2f} m²
      形心深度 h_c = {h_c:.2f} m
      惯性矩 I_c = {I_c:.4f} m⁴
    
    压力计算：
      总压力 P = γ·h_c·A
              = {gamma}×{h_c:.2f}×{A:.2f}
              = {P:.0f} N
              = {P/1000:.1f} kN
    
    压力中心：
      深度 y_D = h_c + I_c/(h_c·A)
              = {h_c:.2f} + {I_c:.4f}/({h_c:.2f}×{A:.2f})
              = {y_D:.4f} m
      
      偏心距 e = y_D - h_c
              = {y_D:.4f} - {h_c:.2f}
              = {e:.4f} m
              = {e*100:.2f} cm
    
    压强分布：
      形心处 p_c = {p_c/1000:.2f} kPa
      压力中心 p_D = {p_D/1000:.2f} kPa
    
    力矩（对闸门底部）：
      M = P × (h_bot - y_D)
        = {P/1000:.1f} × {h_top+h-y_D:.3f}
        = {M_bottom/1000:.1f} kN·m
    
    工程意义：
      • 设计闸门支承结构
      • 计算启闭力
      • 确定铰链位置
      • 稳定性验算
    
    验算：
      y_D > h_c ✓（压力中心在形心下方）
      e/h = {e/h*100:.2f}%（偏心比<10% ✓）
    """
    
    ax4.text(0.05, 0.95, results_text, transform=ax4.transAxes,
             fontsize=8.5, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """主程序：压力中心计算"""
    print("="*70)
    print("第一章 - 矩形闸门压力中心计算")
    print("="*70)
    
    # 题目数据
    b = 2.0      # 闸门宽度 (m)
    h = 3.0      # 闸门高度 (m)
    h_top = 2.0  # 顶部水深 (m)
    gamma = 9810 # 水的容重 (N/m³)
    
    print(f"\n【题目】")
    print(f"矩形闸门，宽b={b}m，高h={h}m")
    print(f"闸门顶部位于水面下{h_top}m")
    print(f"求：(1) 静水总压力P")
    print(f"    (2) 压力中心深度y_D")
    
    # 计算
    A = b * h
    h_c = h_top + h / 2
    I_c = moment_of_inertia_rectangular(b, h)
    P, _, _ = rectangular_gate_pressure(b, h, h_top, gamma)
    y_D, e = pressure_center_depth(h_c, A, I_c)
    
    print(f"\n【解】")
    print(f"\n(1) 静水总压力：")
    print(f"    面积：A = b×h = {b}×{h} = {A} m²")
    print(f"    形心深度：h_c = h_top + h/2 = {h_top} + {h/2} = {h_c} m")
    print(f"    总压力：P = γ·h_c·A")
    print(f"           = {gamma}×{h_c}×{A}")
    print(f"           = {P:.0f} N")
    print(f"           = {P/1000:.1f} kN")
    
    print(f"\n(2) 压力中心：")
    print(f"    惯性矩：I_c = b·h³/12 = {b}×{h}³/12 = {I_c:.4f} m⁴")
    print(f"    ")
    print(f"    压力中心深度：y_D = h_c + I_c/(h_c·A)")
    print(f"                  = {h_c} + {I_c:.4f}/({h_c}×{A})")
    print(f"                  = {h_c} + {I_c/(h_c*A):.4f}")
    print(f"                  = {y_D:.4f} m")
    print(f"    ")
    print(f"    偏心距：e = y_D - h_c")
    print(f"           = {y_D:.4f} - {h_c}")
    print(f"           = {e:.4f} m")
    print(f"           = {e*100:.2f} cm")
    print(f"    ")
    print(f"    结论：压力中心位于形心下方{e*100:.2f}cm处 ✓")
    
    # 绘图
    print(f"\n正在生成分析图...")
    plot_pressure_center_analysis()
    
    print(f"\n" + "="*70)
    print("压力中心计算完成！")
    print("="*70)


def exercise():
    """练习题"""
    print("\n" + "="*70)
    print("【练习题】")
    print("="*70)
    print("""
    1. 如果闸门倾斜45°放置，压力中心如何计算？
    2. 圆形闸门（直径D=2m）的压力中心在哪里？
    3. 为什么压力中心总是在形心下方？
    4. 浅水和深水时偏心距有何不同？
    
    提示：
    - 倾斜：投影面积和深度都需转换
    - 圆形：I_c = πD⁴/64，e = D²/(16h_c)
    - 物理原因：下部压强更大
    - 浅水：e相对较大；深水：e相对较小
    """)


if __name__ == "__main__":
    main()
    exercise()
