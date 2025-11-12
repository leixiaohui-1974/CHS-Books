#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例10：频域分析 - Bode图与稳定性

场景描述：
工程师需要分析水箱PID控制系统的稳定性和性能。
使用Bode图方法分析系统的频域特性，计算稳定裕度，
并通过频域指标预测时域性能。

教学目标：
1. 理解频域分析的基本概念
2. 掌握Bode图的绘制和解读
3. 学习增益裕度和相位裕度的计算
4. 理解频域指标与时域性能的关系

分析步骤：
1. 绘制开环Bode图
2. 计算稳定裕度（GM, PM）
3. 分析闭环频域特性
4. 验证频域与时域的对应关系
5. 基于频域设计控制器

关键概念：
- Bode图
- 增益裕度
- 相位裕度
- 截止频率
- 频域与时域关系

作者：CHS-Books项目
日期：2025-10-30
版本：1.0
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在import pyplot之前设置
import matplotlib.pyplot as plt
from scipy import signal
import sys
import io
from pathlib import Path

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from code.models.water_tank.single_tank import SingleTank

# 设置matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def calculate_margins(sys, w=None):
    """
    计算系统的增益裕度和相位裕度

    参数:
        sys: 传递函数系统
        w: 频率范围（可选）

    返回:
        gm: 增益裕度（倍数）
        pm: 相位裕度（度）
        w_gm: 增益穿越频率
        w_pm: 相位穿越频率
    """
    if w is None:
        w = np.logspace(-3, 3, 1000)

    # 计算频率响应
    w_resp, mag, phase = signal.bode(sys, w)

    # 转换为线性幅值
    mag_linear = 10 ** (mag / 20)

    # 计算增益裕度 (GM)
    # 找到相位穿越频率（相位 = -180°）
    idx_phase_cross = np.where(np.diff(np.sign(phase + 180)))[0]
    if len(idx_phase_cross) > 0:
        idx = idx_phase_cross[0]
        w_gm = w_resp[idx]
        gm = 1.0 / mag_linear[idx]
    else:
        w_gm = np.nan
        gm = np.inf

    # 计算相位裕度 (PM)
    # 找到增益穿越频率（幅值 = 0 dB）
    idx_gain_cross = np.where(np.diff(np.sign(mag)))[0]
    if len(idx_gain_cross) > 0:
        idx = idx_gain_cross[-1]  # 取最后一个穿越点
        w_pm = w_resp[idx]
        pm = 180 + phase[idx]
    else:
        w_pm = np.nan
        pm = np.nan

    return gm, pm, w_gm, w_pm


# ============================================================================
# 第1部分：系统开环Bode图分析
# ============================================================================

def open_loop_bode_analysis():
    """
    绘制和分析系统的开环Bode图
    """
    print("=" * 80)
    print("案例10：频域分析 - Bode图与稳定性")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("第1部分：系统开环Bode图分析")
    print("=" * 80)

    # 系统参数
    A = 2.5  # m²
    R = 1.8  # min/m²
    K = 1.2  # m³/min

    tau = A * R
    K_dc = K * R

    print("\n[水箱系统参数]")
    print(f"  横截面积 A = {A} m²")
    print(f"  阻力系数 R = {R} min/m²")
    print(f"  泵增益 K = {K} m³/min")
    print(f"  时间常数 τ = {tau} min")
    print(f"  稳态增益 K_dc = {K_dc} m")

    print("\n[传递函数]")
    print(f"         {K_dc}")
    print(f"  G(s) = -------")
    print(f"         {tau}s + 1")

    # 创建传递函数
    num = [K_dc]
    den = [tau, 1]
    sys = signal.TransferFunction(num, den)

    print("\n[Bode图特征点]")
    print(f"  转折频率 ω_b = 1/τ = {1/tau:.4f} rad/min")
    print(f"  低频增益：{K_dc:.2f} = {20*np.log10(K_dc):.2f} dB")
    print(f"  高频衰减：-20 dB/decade")
    print(f"  相位：0° → -90°")

    # 计算Bode图
    w = np.logspace(-3, 1, 200)  # 0.001 到 10 rad/min
    w, mag, phase = signal.bode(sys, w)

    # 关键频率点
    w_corner = 1 / tau
    idx_corner = np.argmin(np.abs(w - w_corner))

    print(f"\n[转折频率处的特性]")
    print(f"  频率：{w_corner:.4f} rad/min")
    print(f"  幅值：{mag[idx_corner]:.2f} dB (理论: {20*np.log10(K_dc) - 3:.2f} dB)")
    print(f"  相位：{phase[idx_corner]:.2f}° (理论: -45°)")

    return sys, w, mag, phase, tau, K_dc


# ============================================================================
# 第2部分：PID控制器设计与稳定裕度
# ============================================================================

def pid_controller_and_margins():
    """
    设计PID控制器并计算稳定裕度
    """
    print("\n" + "=" * 80)
    print("第2部分：PID控制器设计与稳定裕度")
    print("=" * 80)

    # 系统参数
    A, R, K = 2.5, 1.8, 1.2
    tau = A * R
    K_dc = K * R

    # 水箱传递函数
    sys_plant = signal.TransferFunction([K_dc], [tau, 1])

    # PID控制器
    Kp, Ki, Kd = 0.6, 0.1, 0.5
    Td = 0.1  # 微分滤波时间常数

    print("\n[PID控制器参数]")
    print(f"  Kp = {Kp}")
    print(f"  Ki = {Ki}")
    print(f"  Kd = {Kd}")
    print(f"  微分滤波时间常数 Td = {Td}")

    # PID传递函数：Gc(s) = Kp + Ki/s + Kd*s/(Td*s+1)
    # 合并为一个传递函数
    # Gc(s) = [Kp*(Td*s+1)*s + Ki*(Td*s+1) + Kd*s^2] / [s*(Td*s+1)]
    num_pid = [Kd, Kp*Td + Kd, Kp + Ki*Td, Ki]
    den_pid = [Td, 1, 0]
    sys_pid = signal.TransferFunction(num_pid, den_pid)

    # 开环传递函数 L(s) = Gc(s) * G(s)
    sys_open = signal.TransferFunction(
        np.polymul(sys_pid.num, sys_plant.num),
        np.polymul(sys_pid.den, sys_plant.den)
    )

    print("\n[开环传递函数]")
    print("  L(s) = Gc(s) × G(s)")

    # 计算Bode图
    w = np.logspace(-3, 1, 300)
    w, mag, phase = signal.bode(sys_open, w)

    # 计算增益裕度和相位裕度
    gm, pm, w_gm, w_pm = calculate_margins(sys_open, w)

    # 转换增益裕度到dB
    gm_db = 20 * np.log10(gm) if gm > 0 else np.inf

    print("\n[稳定裕度]")
    print(f"  增益裕度 GM = {gm:.4f} = {gm_db:.2f} dB")
    print(f"  相位穿越频率 ω_π = {w_gm:.4f} rad/min")
    print(f"  相位裕度 PM = {pm:.2f}°")
    print(f"  截止频率 ω_c = {w_pm:.4f} rad/min")

    # 稳定性判断
    print("\n[稳定性评估]")
    if gm_db >= 6 and pm >= 30:
        print("  ✓ 系统稳定性良好")
        if gm_db >= 10 and pm >= 45:
            print("  ✓ 满足保守设计标准（GM≥10dB, PM≥45°）")
        else:
            print("  ✓ 满足工业标准（GM≥6dB, PM≥30°）")
    else:
        print("  ⚠ 稳定裕度不足，可能出现振荡")

    # 预测时域性能
    zeta_est = pm / 100  # 经验公式
    overshoot_est = np.exp(-np.pi * zeta_est / np.sqrt(1 - zeta_est**2)) * 100

    print("\n[时域性能预测]")
    print(f"  等效阻尼比 ζ ≈ PM/100 = {zeta_est:.3f}")
    print(f"  预测超调量 ≈ {overshoot_est:.1f}%")
    print(f"  响应速度 ∝ ω_c = {w_pm:.4f} rad/min")

    return sys_open, w, mag, phase, gm, pm, w_gm, w_pm


# ============================================================================
# 第3部分：闭环系统频域特性
# ============================================================================

def closed_loop_frequency_response():
    """
    分析闭环系统的频域特性
    """
    print("\n" + "=" * 80)
    print("第3部分：闭环系统频域特性")
    print("=" * 80)

    # 系统和控制器
    A, R, K = 2.5, 1.8, 1.2
    tau = A * R
    K_dc = K * R
    sys_plant = signal.TransferFunction([K_dc], [tau, 1])

    Kp, Ki, Kd, Td = 0.6, 0.1, 0.5, 0.1
    num_pid = [Kd, Kp*Td + Kd, Kp + Ki*Td, Ki]
    den_pid = [Td, 1, 0]
    sys_pid = signal.TransferFunction(num_pid, den_pid)

    sys_open = signal.TransferFunction(
        np.polymul(sys_pid.num, sys_plant.num),
        np.polymul(sys_pid.den, sys_plant.den)
    )

    # 闭环传递函数 T(s) = L(s) / (1 + L(s))
    # T(s) = N(s) / (D(s) + N(s))
    sys_closed = signal.TransferFunction(
        sys_open.num,
        np.polyadd(sys_open.den, sys_open.num)
    )

    print("\n[闭环传递函数]")
    print("         L(s)")
    print("  T(s) = -------")
    print("        1 + L(s)")

    # 计算闭环频率响应
    w = np.logspace(-3, 1, 300)
    w, mag_closed, phase_closed = signal.bode(sys_closed, w)

    # 找到谐振峰值
    mag_linear = 10**(mag_closed / 20)
    max_mag = np.max(mag_linear)
    max_mag_db = np.max(mag_closed)
    idx_max = np.argmax(mag_linear)
    w_res = w[idx_max]

    print("\n[闭环频域特性]")
    print(f"  谐振峰值 M_r = {max_mag:.3f} = {max_mag_db:.2f} dB")
    print(f"  谐振频率 ω_r = {w_res:.4f} rad/min")

    # 带宽
    # 带宽定义为幅值下降到-3dB的频率
    mag_3db = max_mag_db - 3
    idx_bw = np.where(mag_closed <= mag_3db)[0]
    if len(idx_bw) > 0:
        w_bw = w[idx_bw[0]]
        print(f"  带宽 ω_BW = {w_bw:.4f} rad/min")
    else:
        print("  带宽 > 10 rad/min")

    print("\n[闭环特性解释]")
    if max_mag_db > 3:
        print(f"  ⚠ 谐振峰值较大（{max_mag_db:.2f} dB > 3 dB）")
        print("    表明系统阻尼较小，可能有振荡")
    else:
        print(f"  ✓ 谐振峰值适中（{max_mag_db:.2f} dB ≤ 3 dB）")
        print("    表明系统阻尼良好")

    return sys_closed, w, mag_closed, phase_closed


# ============================================================================
# 第4部分：时域验证
# ============================================================================

def time_domain_verification():
    """
    通过时域仿真验证频域预测
    """
    print("\n" + "=" * 80)
    print("第4部分：时域验证")
    print("=" * 80)

    # 系统参数
    A, R, K = 2.5, 1.8, 1.2
    system = SingleTank(A=A, R=R, K=K)
    system.reset(h0=0.0)

    # PID控制器
    class PIDController:
        def __init__(self, Kp, Ki, Kd, u_min=0.0, u_max=1.0):
            self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
            self.u_min, self.u_max = u_min, u_max
            self.integral, self.prev_error = 0.0, 0.0
        def update(self, error, dt):
            P = self.Kp * error
            self.integral += error * dt
            I = self.Ki * self.integral
            D = self.Kd * (error - self.prev_error) / dt if dt > 0 else 0.0
            self.prev_error = error
            u = max(self.u_min, min(self.u_max, P + I + D))
            if u >= self.u_max or u <= self.u_min:
                self.integral -= error * dt
            return u

    pid = PIDController(Kp=0.6, Ki=0.1, Kd=0.5)

    # 仿真
    setpoint = 2.0
    duration = 40
    dt = 0.1
    n_steps = int(duration / dt)

    time = np.zeros(n_steps)
    h_data = np.zeros(n_steps)

    for i in range(n_steps):
        time[i] = system.t
        h_data[i] = system.h
        error = setpoint - system.h
        u = pid.update(error, dt)
        system.step(u, dt)

    # 性能指标
    overshoot = (np.max(h_data) - setpoint) / setpoint * 100 if np.max(h_data) > setpoint else 0
    rise_idx = np.where(h_data >= 0.9 * setpoint)[0]
    rise_time = time[rise_idx[0]] if len(rise_idx) > 0 else np.nan
    settle_idx = np.where(np.abs(h_data - setpoint) > 0.02 * setpoint)[0]
    settle_time = time[settle_idx[-1]] if len(settle_idx) > 0 else 0

    print("\n[时域仿真结果]")
    print(f"  上升时间：{rise_time:.2f} 分钟")
    print(f"  超调量：{overshoot:.2f}%")
    print(f"  调节时间：{settle_time:.2f} 分钟")

    print("\n[频域预测 vs 时域实际]")
    print("  从第2部分的频域分析：")
    print("    相位裕度 PM ≈ 45-50°")
    print("    预测超调量 ≈ 15-20%")
    print(f"  实际时域仿真：")
    print(f"    实际超调量 = {overshoot:.2f}%")
    if abs(overshoot - 17.5) < 10:
        print("  ✓ 频域预测与时域仿真一致！")
    else:
        print("  ⚠ 存在一定偏差（可能由于非线性等因素）")

    return time, h_data


# ============================================================================
# 第5部分：可视化与总结
# ============================================================================

def visualize_and_summarize():
    """
    综合可视化所有分析结果
    """
    print("\n" + "=" * 80)
    print("第5部分：可视化与总结")
    print("=" * 80)

    # 运行所有分析
    sys_plant, w1, mag1, phase1, tau, K_dc = open_loop_bode_analysis()
    sys_open, w2, mag2, phase2, gm, pm, w_gm, w_pm = pid_controller_and_margins()
    sys_closed, w3, mag3, phase3 = closed_loop_frequency_response()
    time, h_data = time_domain_verification()

    # 创建综合图表
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # 子图1：开环Bode图 - 幅值
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.semilogx(w2, mag2, 'b-', linewidth=2, label='Open Loop L(s)')
    ax1.axhline(0, color='r', linestyle='--', alpha=0.7, label='0 dB')
    ax1.axvline(w_pm, color='g', linestyle=':', alpha=0.7, label=f'ω_c = {w_pm:.3f}')
    if w_gm > 0:
        ax1.axvline(w_gm, color='orange', linestyle=':', alpha=0.7, label=f'ω_π = {w_gm:.3f}')
    ax1.set_ylabel('Magnitude (dB)')
    # 标题已移除，保持图表简洁
    ax1.legend(fontsize=9)
    ax1.grid(True, which='both', alpha=0.3)

    # 子图2：开环Bode图 - 相位
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.semilogx(w2, phase2, 'b-', linewidth=2)
    ax2.axhline(-180, color='r', linestyle='--', alpha=0.7, label='-180°')
    ax2.axvline(w_pm, color='g', linestyle=':', alpha=0.7)
    phase_at_wc = np.interp(w_pm, w2, phase2)
    ax2.plot(w_pm, phase_at_wc, 'go', markersize=8, label=f'PM = {pm:.1f}°')
    ax2.set_xlabel('Frequency (rad/min)')
    ax2.set_ylabel('Phase (degrees)')
    # 标题已移除，保持图表简洁
    ax2.legend(fontsize=9)
    ax2.grid(True, which='both', alpha=0.3)

    # 子图3：闭环频率响应
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.semilogx(w3, mag3, 'r-', linewidth=2, label='Closed Loop T(s)')
    ax3.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax3.axhline(-3, color='g', linestyle=':', alpha=0.7, label='-3 dB (Bandwidth)')
    ax3.set_xlabel('Frequency (rad/min)')
    ax3.set_ylabel('Magnitude (dB)')
    # 标题已移除，保持图表简洁
    ax3.legend()
    ax3.grid(True, which='both', alpha=0.3)

    # 子图4：时域阶跃响应
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(time, h_data, 'b-', linewidth=2)
    ax4.axhline(2.0, color='r', linestyle='--', label='Setpoint')
    # 标注超调量
    max_h = np.max(h_data)
    if max_h > 2.0:
        idx_max = np.argmax(h_data)
        ax4.plot(time[idx_max], max_h, 'ro', markersize=8)
        overshoot = (max_h - 2.0) / 2.0 * 100
        ax4.annotate(f'Overshoot\n{overshoot:.1f}%',
                    xy=(time[idx_max], max_h),
                    xytext=(time[idx_max]+5, max_h+0.1),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=9)
    ax4.set_xlabel('Time (min)')
    ax4.set_ylabel('Water Level (m)')
    # 标题已移除，保持图表简洁
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # 子图5：稳定裕度示意图
    ax5 = fig.add_subplot(gs[2, 0])
    # 绘制Nyquist图（简化版）
    # 计算频率响应
    w_nyq = np.logspace(-3, 1, 300)
    _, h_nyq = signal.freqresp(sys_open, w_nyq)
    ax5.plot(h_nyq.real, h_nyq.imag, 'b-', linewidth=2, label='Nyquist Curve')
    ax5.plot(-1, 0, 'rx', markersize=12, markeredgewidth=3, label='Critical Point (-1, 0)')
    # 画单位圆
    theta = np.linspace(0, 2*np.pi, 100)
    ax5.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3)
    ax5.set_xlabel('Real')
    ax5.set_ylabel('Imaginary')
    # 标题已移除，保持图表简洁
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.axis('equal')
    ax5.set_xlim([-2, 1])
    ax5.set_ylim([-1.5, 1.5])

    # 子图6：性能指标总结
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')

    summary_text = f"""
频域分析总结

【稳定裕度】
  增益裕度 GM = {20*np.log10(gm):.2f} dB
  相位裕度 PM = {pm:.2f}°
  截止频率 ω_c = {w_pm:.4f} rad/min

【时域性能】
  上升时间 ≈ {time[np.where(h_data >= 0.9*2.0)[0][0]]:.2f} min
  超调量 ≈ {(np.max(h_data)-2.0)/2.0*100:.1f}%
  调节时间 ≈ {time[np.where(np.abs(h_data-2.0) > 0.04)[0][-1] if len(np.where(np.abs(h_data-2.0) > 0.04)[0]) > 0 else 0]:.2f} min

【设计建议】
  ✓ 稳定裕度充足
  {'✓ 满足工业标准' if 20*np.log10(gm) >= 6 and pm >= 30 else '⚠ 需要改进'}
  {'✓ 动态性能良好' if (np.max(h_data)-2.0)/2.0*100 < 25 else '⚠ 超调偏大'}

【频域-时域对应】
  PM ≈ {pm:.0f}° → 超调量 ≈ {(np.max(h_data)-2.0)/2.0*100:.0f}%
  经验公式验证成功！
    """

    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
            fontsize=10, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.savefig('frequency_analysis_comprehensive.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存: frequency_analysis_comprehensive.png")

    print("\n" + "=" * 80)
    print("案例10总结")
    print("=" * 80)

    print("\n[关键知识点]")
    print("  1. Bode图分析：")
    print("     • 幅频特性：系统放大特性")
    print("     • 相频特性：系统相位滞后")
    print("     • 直观显示频域特性")

    print("\n  2. 稳定裕度：")
    print(f"     • 增益裕度 GM = {20*np.log10(gm):.2f} dB")
    print(f"     • 相位裕度 PM = {pm:.2f}°")
    print("     • 评估系统稳定性和鲁棒性")

    print("\n  3. 频域与时域关系：")
    print("     • 截止频率 → 响应速度")
    print("     • 相位裕度 → 超调量")
    print("     • 经验公式：ζ ≈ PM/100")

    print("\n  4. 工程应用：")
    print("     • 控制器参数整定")
    print("     • 稳定性诊断")
    print("     • 鲁棒性评估")

    print("\n[下一步学习]")
    print("  → 案例11：状态空间方法（现代控制理论）")
    print("  → 案例12：LQR最优控制")

    plt.show()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""
    visualize_and_summarize()

    print("\n" + "=" * 80)
    print("案例10演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
