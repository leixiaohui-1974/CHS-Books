"""
案例22：二次调频（AGC）控制仿真

展示内容：
1. AGC控制器设计
2. 频率扰动响应
3. ACE计算与控制
4. CPS性能评估

作者: CHS Books
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
from models.grid_support import SecondaryFrequencyControl

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def simulate_power_system_dynamics(
    delta_P_load: float,
    delta_P_agc: float,
    H: float = 5.0,
    D: float = 1.0,
    f_nominal: float = 50.0,
    dt: float = 1.0
):
    """
    简化电力系统动态仿真
    
    摇摆方程: 2H * df/dt = ΔP_m - ΔP_load - D * Δf
    
    Args:
        delta_P_load: 负荷扰动 (pu)
        delta_P_agc: AGC控制量 (pu)
        H: 惯量常数 (s)
        D: 阻尼系数
        f_nominal: 额定频率
        dt: 时间步长
        
    Returns:
        delta_f: 频率偏差 (Hz)
    """
    # 简化：假设一次调频提供一部分响应
    delta_P_primary = -0.05 * delta_P_agc  # 简化模型
    
    # 功率不平衡
    delta_P = delta_P_agc + delta_P_primary - delta_P_load
    
    # 频率变化 (简化为静态关系)
    delta_f = -delta_P / D * 0.1  # 转换为Hz
    
    return delta_f


def main():
    """主函数"""
    
    print("=" * 70)
    print("案例22：二次调频（AGC）控制仿真")
    print("=" * 70)
    
    # 1. 创建AGC控制器
    agc = SecondaryFrequencyControl(
        beta=20.0,  # 频率偏差系数 (MW/0.1Hz)
        Kp=0.8,
        Ki=0.15,
        name="区域AGC控制器"
    )
    
    print(f"\nAGC控制器参数：")
    print(f"  频率偏差系数β: {agc.beta} MW/0.1Hz")
    print(f"  比例增益Kp: {agc.Kp}")
    print(f"  积分增益Ki: {agc.Ki}")
    
    # 2. 仿真参数
    T_sim = 600  # 仿真时长 600秒
    dt = 1  # 时间步长 1秒
    N = int(T_sim / dt)
    
    t = np.arange(0, T_sim, dt)
    
    # 3. 负荷扰动场景
    print(f"\n仿真场景设置：")
    print(f"  仿真时长: {T_sim}秒")
    print(f"  时间步长: {dt}秒")
    
    # 创建负荷扰动
    delta_P_load = np.zeros(N)
    
    # 场景1：100s时负荷突增50MW
    delta_P_load[100:300] = 50
    
    # 场景2：300s时负荷突降30MW
    delta_P_load[300:500] = 20
    
    # 场景3：500s后恢复
    delta_P_load[500:] = 0
    
    print(f"  负荷扰动:")
    print(f"    t=100s: +50MW")
    print(f"    t=300s: -30MW (总+20MW)")
    print(f"    t=500s: 恢复")
    
    # 联络线偏差（简化为0）
    delta_Ptie = np.zeros(N)
    
    # 4. 初始化状态变量
    delta_f = np.zeros(N)  # 频率偏差
    P_agc = np.zeros(N)  # AGC控制指令
    ACE = np.zeros(N)  # 区域控制偏差
    
    # 系统参数
    H_system = 5.0  # 惯量常数
    D_system = 1.0  # 阻尼系数
    
    # 5. 仿真循环
    print(f"\n开始仿真...")
    
    for i in range(1, N):
        # 当前频率偏差（简化动态）
        # 实际应该求解微分方程，这里简化处理
        power_imbalance = P_agc[i-1] - delta_P_load[i]
        delta_f[i] = -power_imbalance / (D_system * 50) * 0.5
        
        # 一阶滤波（模拟系统惯性）
        tau = 5  # 时间常数
        delta_f[i] = delta_f[i-1] + (delta_f[i] - delta_f[i-1]) * dt / tau
        
        # 计算ACE
        ACE[i] = agc.compute_ACE(delta_f[i], delta_Ptie[i])
        
        # AGC控制
        P_agc[i] = agc.compute_control(delta_f[i], delta_Ptie[i], dt)
        
        # 限幅
        P_agc[i] = np.clip(P_agc[i], -200, 200)
    
    print(f"仿真完成！")
    
    # 6. 结果分析
    print(f"\n频率偏差统计：")
    print(f"  最大偏差: {delta_f.max():.4f} Hz")
    print(f"  最小偏差: {delta_f.min():.4f} Hz")
    print(f"  RMS偏差: {np.sqrt(np.mean(delta_f**2)):.4f} Hz")
    
    print(f"\nAGC控制量统计：")
    print(f"  最大调节: {P_agc.max():.1f} MW")
    print(f"  最小调节: {P_agc.min():.1f} MW")
    
    print(f"\nACE统计：")
    print(f"  最大ACE: {ACE.max():.2f}")
    print(f"  最小ACE: {ACE.min():.2f}")
    print(f"  平均ACE: {np.mean(np.abs(ACE)):.2f}")
    
    # 7. CPS性能评估
    CPS1 = agc.evaluate_CPS(ACE, epsilon=0.0002)
    print(f"\n性能评估：")
    print(f"  CPS1标准: {CPS1:.2f}%")
    if CPS1 >= 100:
        print(f"  评价: ✅ 达标 (≥100%)")
    else:
        print(f"  评价: ❌ 未达标 (<100%)")
    
    # 8. 绘图
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    
    # 8.1 负荷扰动
    ax = axes[0]
    ax.plot(t, delta_P_load, 'b-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax.fill_between(t, 0, delta_P_load, alpha=0.3)
    ax.set_ylabel('功率扰动 (MW)')
    ax.set_title('负荷扰动场景')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, T_sim)
    
    # 8.2 频率偏差
    ax = axes[1]
    ax.plot(t, delta_f, 'r-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax.axhline(y=0.05, color='g', linestyle=':', label='±0.05Hz限值')
    ax.axhline(y=-0.05, color='g', linestyle=':')
    ax.fill_between(t, 0, delta_f, alpha=0.3, color='red')
    ax.set_ylabel('频率偏差 (Hz)')
    ax.set_title('系统频率响应')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, T_sim)
    
    # 8.3 ACE
    ax = axes[2]
    ax.plot(t, ACE, 'm-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax.fill_between(t, 0, ACE, alpha=0.3, color='magenta')
    ax.set_ylabel('ACE')
    ax.set_title('区域控制偏差（ACE）')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, T_sim)
    
    # 8.4 AGC控制指令
    ax = axes[3]
    ax.plot(t, P_agc, 'g-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax.fill_between(t, 0, P_agc, alpha=0.3, color='green')
    ax.set_xlabel('时间 (秒)')
    ax.set_ylabel('控制指令 (MW)')
    ax.set_title('AGC控制输出')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, T_sim)
    
    plt.tight_layout()
    plt.savefig('example_22_agc_control.png', dpi=150, bbox_inches='tight')
    print(f"\n图表已保存: example_22_agc_control.png")
    plt.show()
    
    # 9. 性能指标
    print(f"\n详细性能指标：")
    
    # 超调量
    overshoot = np.max(np.abs(delta_f)) / 0.05 * 100  # 相对于±0.05Hz限值
    print(f"  最大频率偏差（相对限值）: {overshoot:.1f}%")
    
    # 调节时间（2%误差带）
    settling_threshold = 0.02 * np.max(np.abs(delta_f))
    settling_idx = np.where(np.abs(delta_f[100:]) < settling_threshold)[0]
    if len(settling_idx) > 0:
        settling_time = settling_idx[0]
        print(f"  调节时间（2%误差带）: {settling_time}秒")
    else:
        print(f"  调节时间: >500秒")
    
    # AGC动作频率
    agc_changes = np.sum(np.abs(np.diff(P_agc)) > 0.1)
    print(f"  AGC动作次数: {agc_changes}")
    
    print("\n" + "=" * 70)
    print("案例22完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
