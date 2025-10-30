#!/usr/bin/env python3
"""
案例1可执行示例：农村灌溉渠道设计

问题描述：
某农村灌区灌溉渠道设计，已知：
- 设计流量 Q = 5.0 m³/s
- 渠底宽度 b = 3.0 m
- 边坡系数 m = 1.5
- 渠底坡度 S0 = 0.0003
- Manning糙率 n = 0.02（混凝土衬砌）

求解：
1. 正常水深 h_n
2. 流速 v
3. Froude数和流态
4. 所有水力要素

运行方式：
    python main.py

作者：CHS-Books项目
日期：2025-10-30
"""

import numpy as np


# ========== 水力计算函数 ==========

def trapezoidal_area(b, h, m):
    """计算梯形断面面积 [m²]"""
    A = (b + m * h) * h
    return A


def wetted_perimeter(b, h, m):
    """计算湿周 [m]"""
    P = b + 2 * h * np.sqrt(1 + m**2)
    return P


def hydraulic_radius(A, P):
    """计算水力半径 [m]"""
    if P == 0:
        return 0
    R = A / P
    return R


def top_width(b, h, m):
    """计算水面宽度 [m]"""
    B = b + 2 * m * h
    return B


def manning_velocity(R, S0, n):
    """Manning流速公式 [m/s]"""
    v = (1/n) * R**(2/3) * S0**(1/2)
    return v


def compute_discharge(A, v):
    """计算流量 [m³/s]"""
    Q = A * v
    return Q


def froude_number(v, A, b, m, h, g=9.81):
    """计算Froude数"""
    B = b + 2 * m * h
    D = A / B
    Fr = v / np.sqrt(g * D)
    return Fr


def determine_flow_regime(Fr):
    """判别流态"""
    if Fr < 1.0:
        return "subcritical"
    elif Fr > 1.0:
        return "supercritical"
    else:
        return "critical"


def print_header(title, width=70):
    """打印标题"""
    print("\n" + "="*width)
    print(f"  {title}")
    print("="*width)


def print_param(name, value, unit="", width=50):
    """打印参数"""
    if unit:
        print(f"  {name:.<{width}} {value:>12.4f} {unit}")
    else:
        print(f"  {name:.<{width}} {value:>12}")


def calculate_normal_depth(Q, b, m, S0, n, g=9.81, tol=1e-6, max_iter=100):
    """
    迭代计算正常水深

    使用Newton-Raphson方法求解隐式方程：
    Q = A * (1/n) * R^(2/3) * S0^(1/2)
    """
    h = 1.0  # 初始猜测值

    for iteration in range(max_iter):
        # 计算当前水深对应的流量
        A = trapezoidal_area(b, h, m)
        P = wetted_perimeter(b, h, m)
        R = hydraulic_radius(A, P)
        v = manning_velocity(R, S0, n)
        Q_calc = compute_discharge(A, v)

        # 计算残差
        residual = Q_calc - Q

        if abs(residual) < tol * Q:
            return h, iteration + 1

        # Newton-Raphson更新
        dA_dh = b + 2 * m * h
        dP_dh = 2 * np.sqrt(1 + m**2)
        dR_dh = (P * dA_dh - A * dP_dh) / P**2
        dv_dh = (1/n) * S0**0.5 * (2/3) * R**(-1/3) * dR_dh
        dQ_dh = dA_dh * v + A * dv_dh

        h = h - residual / dQ_dh

        # 限制水深范围
        h = max(0.1, min(h, 10.0))

    return h, max_iter


def main():
    """主函数"""

    print_header("案例1：农村灌溉渠道设计")

    # ========== 输入参数 ==========
    print("\n【输入参数】")
    Q = 5.0       # 设计流量 (m³/s)
    b = 3.0       # 底宽 (m)
    m = 1.5       # 边坡系数
    S0 = 0.0003   # 底坡
    n = 0.02      # Manning糙率系数（混凝土衬砌）
    g = 9.81      # 重力加速度 (m/s²)

    print_param("设计流量 Q", Q, "m³/s")
    print_param("渠道底宽 b", b, "m")
    print_param("边坡系数 m", m, "")
    print_param("渠底坡度 S₀", S0, "")
    print_param("Manning糙率系数 n", n, "")
    print(f"\n  边坡形式: 1:{m} (垂直:水平)")
    print(f"  渠道材料: 混凝土衬砌 (n={n})")

    # ========== 计算正常水深 ==========
    print_header("计算正常水深")
    print("\n  方法: Newton-Raphson迭代法")
    print(f"  求解方程: Q = A × (1/n) × R^(2/3) × S₀^(1/2) = {Q} m³/s")

    h_normal, iterations = calculate_normal_depth(Q, b, m, S0, n, g)

    print(f"\n  迭代次数: {iterations}")
    print(f"  收敛精度: {1e-6 * Q:.2e} m³/s")

    # ========== 计算水力要素 ==========
    print_header("水力要素计算")

    A = trapezoidal_area(b, h_normal, m)
    P = wetted_perimeter(b, h_normal, m)
    R = hydraulic_radius(A, P)
    B = top_width(b, h_normal, m)
    v = manning_velocity(R, S0, n)
    Q_check = compute_discharge(A, v)

    print("\n【断面几何】")
    print_param("正常水深 h_n", h_normal, "m")
    print_param("过流面积 A", A, "m²")
    print_param("湿周 P", P, "m")
    print_param("水力半径 R", R, "m")
    print_param("水面宽度 B", B, "m")

    print("\n【流速与流量】")
    print_param("平均流速 v", v, "m/s")
    print_param("实际流量 Q", Q_check, "m³/s")
    print_param("流量误差", abs(Q_check - Q) / Q * 100, "%")

    # ========== 流态分析 ==========
    print_header("流态分析")

    Fr = froude_number(v, A, b, m, h_normal, g)
    regime = determine_flow_regime(Fr)

    print("\n【Froude数分析】")
    print_param("Froude数 Fr", Fr, "")
    print_param("临界Froude数", 1.0, "")
    print_param("流态类型", regime, "")

    if regime == "subcritical":
        print("\n  ✓ 缓流状态 (Fr < 1)：水深较大，流速较小")
        print("    - 水流稳定，适合灌溉渠道")
        print("    - 水面线为壅水曲线")
    elif regime == "supercritical":
        print("\n  ✗ 急流状态 (Fr > 1)：水深较小，流速较大")
        print("    - 可能产生冲刷")
        print("    - 需要采取防护措施")
    else:
        print("\n  ! 临界流状态 (Fr = 1)")
        print("    - 不稳定状态，需要调整设计")

    # ========== 设计校核 ==========
    print_header("设计校核")

    print("\n【流速校核】")
    v_min = 0.5   # 最小不淤流速 (m/s)
    v_max = 1.5   # 最大不冲流速 (m/s，混凝土衬砌)

    print_param("计算流速", v, "m/s")
    print_param("最小不淤流速", v_min, "m/s")
    print_param("最大不冲流速", v_max, "m/s")

    if v_min <= v <= v_max:
        print("  ✓ 流速在允许范围内")
    elif v < v_min:
        print("  ✗ 流速过小，可能产生淤积")
    else:
        print("  ✗ 流速过大，可能产生冲刷")

    print("\n【流态校核】")
    if regime == "subcritical":
        print("  ✓ 流态为缓流，符合灌溉渠道要求")
    else:
        print("  ✗ 流态不符合要求，需要调整设计")

    # ========== 断面设计建议 ==========
    print_header("断面设计建议")

    # 安全超高（20%水深，最小0.3m）
    freeboard = max(0.3, 0.2 * h_normal)
    H_total = h_normal + freeboard
    B_top = b + 2 * m * H_total

    print("\n【断面尺寸】")
    print_param("渠底宽度 b", b, "m")
    print_param("设计水深 h", h_normal, "m")
    print_param("安全超高 Δh", freeboard, "m")
    print_param("总深度 H", H_total, "m")
    print_param("顶部宽度 B_top", B_top, "m")
    print_param("边坡比例", f"1:{m}", "")

    print("\n【土方量估算】（每100m渠道长度）")
    L = 100  # 渠道长度 (m)
    V_excavation = ((b + B_top) / 2) * H_total * L
    V_concrete = ((b + b + 2*m*h_normal) / 2) * h_normal * L

    print_param("开挖土方量", V_excavation, "m³")
    print_param("混凝土衬砌量（估算）", V_concrete * 0.1, "m³")

    # ========== 工程建议 ==========
    print_header("工程建议")

    print("\n  1. 渠道断面采用：")
    print(f"     • 底宽 b = {b:.2f} m")
    print(f"     • 设计水深 h = {h_normal:.2f} m")
    print(f"     • 总深度 H = {H_total:.2f} m（含超高）")
    print(f"     • 边坡 1:{m}")

    print("\n  2. 水力特性：")
    print(f"     • 设计流量 Q = {Q:.2f} m³/s")
    print(f"     • 平均流速 v = {v:.2f} m/s")
    print(f"     • 流态：{regime}（缓流稳定）")

    print("\n  3. 施工建议：")
    print(f"     • 渠底坡度：i = {S0:.4f} = {S0*1000:.2f}‰")
    print(f"     • 衬砌材料：混凝土（n = {n}）")
    print(f"     • 衬砌厚度：8-10 cm")
    print(f"     • 每隔20-30m设置伸缩缝")

    print("\n  4. 运行维护：")
    print(f"     • 定期清理淤泥和杂草")
    print(f"     • 检查衬砌是否开裂")
    print(f"     • 雨季前检查边坡稳定性")

    print("\n" + "="*70)
    print("  计算完成！")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
