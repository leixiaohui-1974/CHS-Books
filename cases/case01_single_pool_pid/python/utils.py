"""
工具函数

提供性能评估、数据保存等辅助功能
"""

import numpy as np
import json
from pathlib import Path


def calculate_performance_metrics(time, y, y_ref, y_init):
    """
    计算控制系统性能指标

    Args:
        time: 时间数组
        y: 输出响应
        y_ref: 参考值（可以是数组或标量）
        y_init: 初始值

    Returns:
        metrics: 性能指标字典
    """
    dt = time[1] - time[0]
    n = len(time)

    # 确保y_ref是数组
    if np.isscalar(y_ref):
        y_ref = np.full_like(y, y_ref)

    # 最终值（取最后10%的平均值）
    y_final = np.mean(y[int(0.9*n):])
    ref_final = np.mean(y_ref[int(0.9*n):])

    # 超调量
    if y_init < ref_final:  # 上升
        y_peak = np.max(y)
        overshoot = max(0, (y_peak - ref_final) / (ref_final - y_init) * 100)
    else:  # 下降
        y_peak = np.min(y)
        overshoot = max(0, (ref_final - y_peak) / (y_init - ref_final) * 100)

    # 上升时间（10%-90%）
    y_range = ref_final - y_init
    y_10 = y_init + 0.1 * y_range
    y_90 = y_init + 0.9 * y_range

    idx_10 = np.argmax(y >= y_10) if y_init < ref_final else np.argmax(y <= y_10)
    idx_90 = np.argmax(y >= y_90) if y_init < ref_final else np.argmax(y <= y_90)
    rise_time = (idx_90 - idx_10) * dt if idx_90 > idx_10 else 0

    # 调节时间（进入±2%误差带的时间）
    error_band = 0.02 * abs(ref_final - y_init)
    settling_idx = n - 1  # 默认为最后

    for i in range(n-1, 0, -1):
        if abs(y[i] - ref_final) > error_band:
            settling_idx = i
            break

    settling_time = settling_idx * dt

    # 稳态误差
    steady_state_error = abs(y_final - ref_final)

    # 积分性能指标
    error = y_ref - y
    IAE = np.sum(np.abs(error)) * dt  # Integral Absolute Error
    ISE = np.sum(error**2) * dt       # Integral Square Error
    ITAE = np.sum(time * np.abs(error)) * dt  # Integral Time Absolute Error

    metrics = {
        'overshoot': overshoot,
        'rise_time': rise_time,
        'settling_time': settling_time,
        'steady_state_error': steady_state_error,
        'peak_value': y_peak,
        'final_value': y_final,
        'IAE': IAE,
        'ISE': ISE,
        'ITAE': ITAE
    }

    return metrics


def save_results(results, filename):
    """
    保存仿真结果到文件

    Args:
        results: 结果字典
        filename: 文件路径
    """
    # 转换为可保存的格式
    save_dict = {}
    for key, value in results.items():
        if isinstance(value, np.ndarray):
            save_dict[key] = value
        elif isinstance(value, dict):
            # 递归处理嵌套字典
            for k, v in value.items():
                save_dict[f"{key}_{k}"] = v if isinstance(v, np.ndarray) else np.array([v])
        else:
            save_dict[key] = np.array([value]) if np.isscalar(value) else value

    np.savez(filename, **save_dict)
    print(f"结果已保存到: {filename}")


def load_results(filename):
    """
    从文件加载仿真结果

    Args:
        filename: 文件路径

    Returns:
        results: 结果字典
    """
    data = np.load(filename, allow_pickle=True)
    results = {key: data[key] for key in data.files}
    return results


def export_to_csv(results, filename):
    """
    导出结果为CSV文件

    Args:
        results: 结果字典
        filename: CSV文件路径
    """
    import pandas as pd

    # 准备DataFrame
    df_dict = {}
    for key, value in results.items():
        if isinstance(value, np.ndarray) and value.ndim == 1:
            df_dict[key] = value

    df = pd.DataFrame(df_dict)
    df.to_csv(filename, index=False)
    print(f"数据已导出到CSV: {filename}")


def moving_average(data, window_size):
    """
    移动平均滤波

    Args:
        data: 输入数据
        window_size: 窗口大小

    Returns:
        filtered_data: 滤波后的数据
    """
    if window_size <= 1:
        return data

    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size


def low_pass_filter(data, alpha):
    """
    一阶低通滤波器

    Args:
        data: 输入数据
        alpha: 滤波系数 (0-1)，越小越平滑

    Returns:
        filtered_data: 滤波后的数据
    """
    filtered = np.zeros_like(data)
    filtered[0] = data[0]

    for i in range(1, len(data)):
        filtered[i] = alpha * data[i] + (1 - alpha) * filtered[i-1]

    return filtered


def analyze_frequency_response(time, output, input_signal=None):
    """
    频率响应分析（简单FFT）

    Args:
        time: 时间数组
        output: 输出信号
        input_signal: 输入信号（可选）

    Returns:
        freq: 频率数组
        magnitude: 幅值
        phase: 相位
    """
    from scipy.fft import fft, fftfreq

    n = len(time)
    dt = time[1] - time[0]

    # FFT
    yf = fft(output)
    freq = fftfreq(n, dt)

    # 只取正频率部分
    pos_mask = freq > 0
    freq = freq[pos_mask]
    yf = yf[pos_mask]

    magnitude = np.abs(yf)
    phase = np.angle(yf)

    return freq, magnitude, phase


def print_system_info(canal, controller):
    """
    打印系统和控制器信息

    Args:
        canal: 水渠模型对象
        controller: 控制器对象
    """
    print("\n" + "=" * 60)
    print("系统配置信息")
    print("=" * 60)

    print("\n系统参数:")
    print(f"  池长: {canal.length} m")
    print(f"  池宽: {canal.width} m")
    print(f"  水面面积: {canal.A} m²")
    print(f"  流量系数: {canal.Cd}")
    print(f"  最大闸门开度: {canal.a_max} m")

    print("\n控制器参数:")
    print(f"  类型: {controller.__class__.__name__}")
    print(f"  Kp = {controller.Kp}")
    print(f"  Ki = {controller.Ki}")
    print(f"  Kd = {controller.Kd}")
    print(f"  采样时间: {controller.dt} s")
    print(f"  输出范围: [{controller.u_min}, {controller.u_max}]")
    print(f"  抗积分饱和: {'启用' if controller.anti_windup else '禁用'}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    # 测试代码
    print("工具函数测试\n")

    # 测试性能指标计算
    time = np.linspace(0, 100, 1000)
    y_ref = np.ones_like(time) * 2.5
    y_ref[:100] = 2.0
    y = 2.0 + 0.5 * (1 - np.exp(-time/20)) * (1 + 0.1*np.sin(time/5))

    metrics = calculate_performance_metrics(time, y, 2.5, 2.0)

    print("性能指标:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

    # 测试移动平均
    print("\n移动平均测试:")
    data = np.random.randn(100) + 10
    filtered = moving_average(data, 10)
    print(f"  原始数据std: {np.std(data):.4f}")
    print(f"  滤波后std: {np.std(filtered):.4f}")

    # 测试低通滤波
    print("\n低通滤波测试:")
    filtered_lp = low_pass_filter(data, alpha=0.1)
    print(f"  滤波后std: {np.std(filtered_lp):.4f}")

    print("\n测试完成!")
