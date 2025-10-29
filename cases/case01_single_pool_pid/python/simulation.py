"""
单池明渠PID控制仿真

本程序演示单池明渠系统的PID控制，包括：
1. 阶跃响应
2. 扰动抑制
3. 不同控制器类型对比
"""

import numpy as np
import json
import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append(str(Path(__file__).parent))

from model import SinglePoolCanal
from controller import PIDController, PIController, PController
from visualization import plot_step_response, plot_disturbance_response, plot_controller_comparison
from utils import calculate_performance_metrics, save_results


def load_parameters(param_file='../data/parameters.json'):
    """加载仿真参数"""
    param_path = Path(__file__).parent / param_file

    if param_path.exists():
        with open(param_path, 'r') as f:
            params = json.load(f)
    else:
        # 默认参数
        params = {
            "system": {
                "length": 1000.0,
                "width": 10.0,
                "Cd": 0.6,
                "h_init": 2.0,
                "Q_in": 19.81
            },
            "controller": {
                "Kp": 0.5,
                "Ki": 0.01,
                "Kd": 5.0
            },
            "simulation": {
                "dt": 1.0,
                "t_end": 2000.0,
                "h_ref": 2.5,
                "disturbance_time": 1000.0,
                "disturbance_magnitude": 5.0
            }
        }

        # 创建目录并保存默认参数
        param_path.parent.mkdir(parents=True, exist_ok=True)
        with open(param_path, 'w') as f:
            json.dump(params, f, indent=4)

        print(f"已创建默认参数文件: {param_path}")

    return params


def simulate_step_response(params):
    """
    仿真阶跃响应

    Args:
        params: 参数字典

    Returns:
        results: 仿真结果字典
    """
    print("\n" + "=" * 60)
    print("仿真 1: 阶跃响应")
    print("=" * 60)

    # 提取参数
    sys_params = params['system']
    ctrl_params = params['controller']
    sim_params = params['simulation']

    # 创建系统和控制器
    canal = SinglePoolCanal(
        length=sys_params['length'],
        width=sys_params['width'],
        Cd=sys_params['Cd']
    )
    canal.reset(h_init=sys_params['h_init'])

    controller = PIDController(
        Kp=ctrl_params['Kp'],
        Ki=ctrl_params['Ki'],
        Kd=ctrl_params['Kd'],
        dt=sim_params['dt'],
        u_max=canal.a_max
    )

    # 时间数组
    dt = sim_params['dt']
    t_end = sim_params['t_end']
    time = np.arange(0, t_end, dt)
    n_steps = len(time)

    # 初始化数据记录
    h_data = np.zeros(n_steps)
    h_ref_data = np.zeros(n_steps)
    u_data = np.zeros(n_steps)
    Q_in_data = np.zeros(n_steps)
    Q_out_data = np.zeros(n_steps)

    # 设定值
    h_ref = sim_params['h_ref']
    Q_in = sys_params['Q_in']  # 恒定流入

    print(f"\n系统参数:")
    print(f"  池长: {canal.length} m")
    print(f"  池宽: {canal.width} m")
    print(f"  初始水深: {sys_params['h_init']} m")
    print(f"  流入流量: {Q_in} m³/s")

    print(f"\nPID参数:")
    print(f"  Kp = {controller.Kp}")
    print(f"  Ki = {controller.Ki}")
    print(f"  Kd = {controller.Kd}")

    print(f"\n控制目标: 水深从 {sys_params['h_init']} m → {h_ref} m")
    print(f"\n开始仿真...")

    # 仿真循环
    for i, t in enumerate(time):
        # 控制器计算
        u = controller.compute(h_ref, canal.h)

        # 系统更新
        h = canal.update(dt, Q_in, u)
        Q_out = canal.compute_outflow(h, u)

        # 记录数据
        h_data[i] = h
        h_ref_data[i] = h_ref
        u_data[i] = u
        Q_in_data[i] = Q_in
        Q_out_data[i] = Q_out

    # 计算性能指标
    metrics = calculate_performance_metrics(time, h_data, h_ref_data, sys_params['h_init'])

    print(f"\n性能指标:")
    print(f"  超调量: {metrics['overshoot']:.2f}%")
    print(f"  上升时间: {metrics['rise_time']:.1f} s")
    print(f"  调节时间: {metrics['settling_time']:.1f} s")
    print(f"  稳态误差: {metrics['steady_state_error']:.4f} m")
    print(f"  IAE: {metrics['IAE']:.2f}")
    print(f"  ISE: {metrics['ISE']:.2f}")

    # 保存结果
    results = {
        'time': time,
        'h': h_data,
        'h_ref': h_ref_data,
        'u': u_data,
        'Q_in': Q_in_data,
        'Q_out': Q_out_data,
        'metrics': metrics
    }

    return results


def simulate_disturbance_rejection(params):
    """
    仿真扰动抑制

    在稳态后，上游流量突然增加
    """
    print("\n" + "=" * 60)
    print("仿真 2: 扰动抑制")
    print("=" * 60)

    sys_params = params['system']
    ctrl_params = params['controller']
    sim_params = params['simulation']

    canal = SinglePoolCanal(
        length=sys_params['length'],
        width=sys_params['width'],
        Cd=sys_params['Cd']
    )

    # 先运行到稳态
    h_ref = sys_params['h_init']
    Q_in = sys_params['Q_in']
    a0 = Q_in / (canal.Cd * canal.width * np.sqrt(2 * canal.g * h_ref))
    canal.reset(h_init=h_ref)

    controller = PIDController(
        Kp=ctrl_params['Kp'],
        Ki=ctrl_params['Ki'],
        Kd=ctrl_params['Kd'],
        dt=sim_params['dt'],
        u_max=canal.a_max
    )

    # 时间数组
    dt = sim_params['dt']
    t_end = sim_params['t_end']
    time = np.arange(0, t_end, dt)
    n_steps = len(time)

    # 数据记录
    h_data = np.zeros(n_steps)
    h_ref_data = np.zeros(n_steps)
    u_data = np.zeros(n_steps)
    Q_in_data = np.zeros(n_steps)

    # 扰动参数
    t_dist = sim_params['disturbance_time']
    dQ = sim_params['disturbance_magnitude']

    print(f"\n扰动设置:")
    print(f"  扰动时刻: {t_dist} s")
    print(f"  流量变化: {Q_in} → {Q_in + dQ} m³/s")
    print(f"\n开始仿真...")

    # 仿真循环
    for i, t in enumerate(time):
        # 扰动
        if t >= t_dist:
            Q_in_current = Q_in + dQ
        else:
            Q_in_current = Q_in

        # 控制
        u = controller.compute(h_ref, canal.h)
        h = canal.update(dt, Q_in_current, u)

        # 记录
        h_data[i] = h
        h_ref_data[i] = h_ref
        u_data[i] = u
        Q_in_data[i] = Q_in_current

    # 分析扰动响应
    idx_dist = int(t_dist / dt)
    h_before = np.mean(h_data[max(0, idx_dist-50):idx_dist])
    h_peak = np.max(h_data[idx_dist:])
    max_deviation = abs(h_peak - h_ref)

    # 计算恢复时间（回到±2%误差带）
    h_band = 0.02 * h_ref
    recovery_idx = idx_dist
    for i in range(idx_dist, n_steps):
        if abs(h_data[i] - h_ref) <= h_band:
            recovery_idx = i
            break
    recovery_time = (recovery_idx - idx_dist) * dt

    print(f"\n扰动响应:")
    print(f"  扰动前水深: {h_before:.4f} m")
    print(f"  最大偏差: {max_deviation:.4f} m")
    print(f"  恢复时间: {recovery_time:.1f} s")

    results = {
        'time': time,
        'h': h_data,
        'h_ref': h_ref_data,
        'u': u_data,
        'Q_in': Q_in_data,
        't_disturbance': t_dist,
        'max_deviation': max_deviation,
        'recovery_time': recovery_time
    }

    return results


def compare_controllers(params):
    """
    对比不同控制器性能

    对比 P、PI、PID 控制器
    """
    print("\n" + "=" * 60)
    print("仿真 3: 控制器对比 (P vs PI vs PID)")
    print("=" * 60)

    sys_params = params['system']
    sim_params = params['simulation']

    # 控制器配置
    controllers_config = {
        'P': {'Kp': 0.8, 'Ki': 0.0, 'Kd': 0.0},
        'PI': {'Kp': 0.5, 'Ki': 0.01, 'Kd': 0.0},
        'PID': {'Kp': 0.5, 'Ki': 0.01, 'Kd': 5.0}
    }

    dt = sim_params['dt']
    t_end = sim_params['t_end']
    time = np.arange(0, t_end, dt)
    n_steps = len(time)

    h_ref = sim_params['h_ref']
    Q_in = sys_params['Q_in']

    results_all = {}

    for name, ctrl_params in controllers_config.items():
        print(f"\n测试 {name} 控制器: Kp={ctrl_params['Kp']}, "
              f"Ki={ctrl_params['Ki']}, Kd={ctrl_params['Kd']}")

        canal = SinglePoolCanal(
            length=sys_params['length'],
            width=sys_params['width'],
            Cd=sys_params['Cd']
        )
        canal.reset(h_init=sys_params['h_init'])

        controller = PIDController(
            Kp=ctrl_params['Kp'],
            Ki=ctrl_params['Ki'],
            Kd=ctrl_params['Kd'],
            dt=dt,
            u_max=canal.a_max
        )

        h_data = np.zeros(n_steps)
        u_data = np.zeros(n_steps)

        for i, t in enumerate(time):
            u = controller.compute(h_ref, canal.h)
            h = canal.update(dt, Q_in, u)
            h_data[i] = h
            u_data[i] = u

        metrics = calculate_performance_metrics(
            time, h_data, np.full(n_steps, h_ref), sys_params['h_init']
        )

        print(f"  超调: {metrics['overshoot']:.1f}%, "
              f"调节时间: {metrics['settling_time']:.0f}s, "
              f"稳态误差: {metrics['steady_state_error']:.4f}m")

        results_all[name] = {
            'h': h_data,
            'u': u_data,
            'metrics': metrics
        }

    results_all['time'] = time
    results_all['h_ref'] = h_ref

    return results_all


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("单池明渠PID控制仿真")
    print("=" * 60)

    # 加载参数
    params = load_parameters()

    # 创建结果目录
    results_dir = Path(__file__).parent.parent / 'results'
    figures_dir = results_dir / 'figures'
    logs_dir = results_dir / 'logs'
    figures_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # 1. 阶跃响应
    results_step = simulate_step_response(params)
    fig_step = plot_step_response(results_step)
    fig_step.savefig(figures_dir / 'step_response.png', dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {figures_dir / 'step_response.png'}")

    # 2. 扰动抑制
    results_dist = simulate_disturbance_rejection(params)
    fig_dist = plot_disturbance_response(results_dist)
    fig_dist.savefig(figures_dir / 'disturbance_response.png', dpi=300, bbox_inches='tight')
    print(f"图表已保存: {figures_dir / 'disturbance_response.png'}")

    # 3. 控制器对比
    results_comp = compare_controllers(params)
    fig_comp = plot_controller_comparison(results_comp)
    fig_comp.savefig(figures_dir / 'controller_comparison.png', dpi=300, bbox_inches='tight')
    print(f"图表已保存: {figures_dir / 'controller_comparison.png'}")

    # 保存数据
    save_results(results_step, logs_dir / 'step_response.npz')
    save_results(results_dist, logs_dir / 'disturbance_response.npz')
    print(f"\n数据已保存到: {logs_dir}")

    print("\n" + "=" * 60)
    print("仿真完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
