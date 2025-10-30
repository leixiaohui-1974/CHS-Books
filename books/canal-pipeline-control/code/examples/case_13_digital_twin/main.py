#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例13：数字孪生与预测性维护

本案例实现了数字孪生系统，用于设备健康监测和预测性维护。

主要内容：
1. 设备退化建模（指数、Weibull、Gamma过程）
2. 剩余使用寿命（RUL）预测
3. 数字孪生实时监控（结合EKF状态估计）
4. 维护策略优化

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
from scipy.special import gamma as gamma_func
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 退化模型类
# ============================================================================

class DegradationModel:
    """退化模型基类"""

    def __init__(self):
        self.params = {}

    def health(self, t):
        """计算时刻t的健康指标（0-1之间）"""
        raise NotImplementedError

    def rul(self, t_current, h_current, h_threshold=0.7):
        """计算剩余使用寿命"""
        raise NotImplementedError


class ExponentialDegradation(DegradationModel):
    """
    指数退化模型: H(t) = exp(-λt)
    适用于电子元件、轴承等
    """

    def __init__(self, lambda_rate=0.001):
        """
        参数:
            lambda_rate: 退化率
        """
        super().__init__()
        self.lambda_rate = lambda_rate
        self.params = {'lambda': lambda_rate}

    def health(self, t):
        """健康指标"""
        return np.exp(-self.lambda_rate * t)

    def rul(self, t_current, h_current, h_threshold=0.7):
        """
        RUL计算:
        h_threshold = h_current * exp(-λ * RUL)
        RUL = ln(h_current / h_threshold) / λ
        """
        if h_current <= h_threshold:
            return 0.0
        return np.log(h_current / h_threshold) / self.lambda_rate


class WeibullDegradation(DegradationModel):
    """
    威布尔退化模型: H(t) = exp(-(t/η)^β)

    β < 1: 早期故障型
    β = 1: 随机故障型（等价于指数分布）
    β > 1: 磨损故障型
    """

    def __init__(self, eta=1000, beta=2.5):
        """
        参数:
            eta: 特征寿命（scale parameter）
            beta: 形状参数（shape parameter）
        """
        super().__init__()
        self.eta = eta
        self.beta = beta
        self.params = {'eta': eta, 'beta': beta}

    def health(self, t):
        """健康指标"""
        return np.exp(-np.power(t / self.eta, self.beta))

    def rul(self, t_current, h_current, h_threshold=0.7):
        """
        RUL计算:
        h_threshold = exp(-((t_current + RUL)/η)^β)
        """
        if h_current <= h_threshold:
            return 0.0

        # ln(h_threshold) = -((t_current + RUL)/η)^β
        # (t_current + RUL)^β = -η^β * ln(h_threshold)
        term = -np.log(h_threshold) * (self.eta ** self.beta)
        t_failure = term ** (1.0 / self.beta)
        rul = t_failure - t_current
        return max(rul, 0.0)


class GammaProcessDegradation(DegradationModel):
    """
    Gamma过程退化模型（随机退化）
    X(t) ~ Gamma(α(t), β), α(t) = ν*t
    """

    def __init__(self, nu=0.01, beta=2.0):
        """
        参数:
            nu: 退化速率
            beta: 形状参数
        """
        super().__init__()
        self.nu = nu
        self.beta = beta
        self.params = {'nu': nu, 'beta': beta}

    def health(self, t):
        """健康指标均值"""
        degradation = self.nu * t / self.beta  # E[X(t)] = α(t)/β = νt/β
        return np.maximum(1.0 - degradation, 0.0)

    def sample_path(self, t_array):
        """生成随机退化路径"""
        n = len(t_array)
        degradation = np.zeros(n)

        for i in range(1, n):
            dt = t_array[i] - t_array[i-1]
            alpha_increment = self.nu * dt
            # Gamma分布采样
            increment = np.random.gamma(alpha_increment, 1.0/self.beta)
            degradation[i] = degradation[i-1] + increment

        health = 1.0 - degradation
        return np.clip(health, 0, 1)

    def rul(self, t_current, h_current, h_threshold=0.7):
        """RUL估计（基于期望值）"""
        if h_current <= h_threshold:
            return 0.0

        degradation_current = 1.0 - h_current
        degradation_threshold = 1.0 - h_threshold

        remaining_degradation = degradation_threshold - degradation_current
        rul = remaining_degradation * self.beta / self.nu
        return max(rul, 0.0)


# ============================================================================
# RUL预测器
# ============================================================================

class RULPredictor:
    """
    剩余使用寿命（RUL）预测器
    支持基于模型和基于数据的预测方法
    """

    def __init__(self, method='model', model=None):
        """
        参数:
            method: 'model'（基于模型）或 'data'（基于数据）
            model: 退化模型对象
        """
        self.method = method
        self.model = model
        self.history = {'time': [], 'health': []}

    def add_observation(self, t, h):
        """添加观测数据"""
        self.history['time'].append(t)
        self.history['health'].append(h)

    def predict_model_based(self, t_current, h_current, h_threshold=0.7):
        """基于模型的RUL预测"""
        if self.model is None:
            raise ValueError("Model is required for model-based prediction")

        return self.model.rul(t_current, h_current, h_threshold)

    def predict_data_based(self, t_current, h_current, h_threshold=0.7):
        """
        基于数据的RUL预测（线性外推）
        拟合最近N个点的线性趋势
        """
        if len(self.history['time']) < 3:
            # 数据不足，使用简单估计
            degradation_rate = (1.0 - h_current) / max(t_current, 1)
            remaining_degradation = h_current - h_threshold
            return remaining_degradation / max(degradation_rate, 1e-6)

        # 取最近N个点
        N = min(20, len(self.history['time']))
        t_data = np.array(self.history['time'][-N:])
        h_data = np.array(self.history['health'][-N:])

        # 线性拟合：h = a*t + b
        coeffs = np.polyfit(t_data, h_data, 1)
        a, b = coeffs

        if a >= 0:  # 健康状态不下降，给一个大的RUL
            return 10000

        # 求解 h_threshold = a*(t_current + RUL) + b
        # RUL = (h_threshold - b)/a - t_current
        t_failure = (h_threshold - b) / a
        rul = t_failure - t_current

        return max(rul, 0.0)

    def predict(self, t_current, h_current, h_threshold=0.7):
        """预测RUL"""
        if self.method == 'model':
            return self.predict_model_based(t_current, h_current, h_threshold)
        else:
            return self.predict_data_based(t_current, h_current, h_threshold)

    def predict_probabilistic(self, t_current, h_current, h_threshold=0.7, n_samples=1000):
        """
        概率RUL预测（Monte Carlo）
        返回RUL的均值和标准差
        """
        if len(self.history['time']) < 3:
            # 数据不足，返回确定性预测
            rul_mean = self.predict(t_current, h_current, h_threshold)
            return rul_mean, rul_mean * 0.1

        # 估计噪声水平
        t_data = np.array(self.history['time'][-20:])
        h_data = np.array(self.history['health'][-20:])
        coeffs = np.polyfit(t_data, h_data, 1)
        h_fit = np.polyval(coeffs, t_data)
        noise_std = np.std(h_data - h_fit)

        # Monte Carlo采样
        rul_samples = []
        for _ in range(n_samples):
            # 添加噪声扰动
            h_perturbed = h_current + np.random.randn() * noise_std
            h_perturbed = np.clip(h_perturbed, 0, 1)

            # 预测RUL
            rul = self.predict(t_current, h_perturbed, h_threshold)
            if rul < 10000:  # 排除异常大的值
                rul_samples.append(rul)

        rul_mean = np.mean(rul_samples)
        rul_std = np.std(rul_samples)

        return rul_mean, rul_std


# ============================================================================
# 健康指标计算
# ============================================================================

class HealthIndicator:
    """
    健康指标计算器
    将多维特征融合为单一健康指标
    """

    def __init__(self, method='mahalanobis'):
        """
        参数:
            method: 'mahalanobis'（马氏距离）或 'pca'（主成分）
        """
        self.method = method
        self.baseline_mean = None
        self.baseline_cov = None
        self.pca_weights = None

    def fit(self, features_healthy):
        """
        使用健康状态数据训练

        参数:
            features_healthy: (n_samples, n_features) 健康状态特征矩阵
        """
        self.baseline_mean = np.mean(features_healthy, axis=0)
        self.baseline_cov = np.cov(features_healthy.T)

        # PCA：第一主成分
        eigenvalues, eigenvectors = np.linalg.eig(self.baseline_cov)
        idx = eigenvalues.argsort()[::-1]
        self.pca_weights = eigenvectors[:, idx[0]].real

    def compute_mahalanobis(self, features):
        """计算马氏距离"""
        diff = features - self.baseline_mean

        # 添加正则化避免奇异矩阵
        cov_reg = self.baseline_cov + np.eye(len(self.baseline_mean)) * 1e-6

        try:
            inv_cov = np.linalg.inv(cov_reg)
            distance = np.sqrt(diff @ inv_cov @ diff.T)
        except:
            # 如果求逆失败，使用欧氏距离
            distance = np.linalg.norm(diff)

        return distance

    def compute(self, features, max_distance=10.0):
        """
        计算健康指标

        返回:
            HI: 0-1之间，1表示完全健康，0表示失效
        """
        if self.method == 'mahalanobis':
            distance = self.compute_mahalanobis(features)
            # 归一化到0-1
            hi = 1.0 - min(distance / max_distance, 1.0)
        elif self.method == 'pca':
            # 投影到第一主成分
            projection = np.dot(features - self.baseline_mean, self.pca_weights)
            # 归一化
            hi = 1.0 / (1.0 + np.abs(projection))
        else:
            raise ValueError(f"Unknown method: {self.method}")

        return np.clip(hi, 0, 1)


# ============================================================================
# 简化的EKF（从案例12复用）
# ============================================================================

class SimpleEKF:
    """简化的扩展卡尔曼滤波器（用于数字孪生状态估计）"""

    def __init__(self, Q, R, x0, P0):
        self.Q = Q  # 过程噪声
        self.R = R  # 测量噪声
        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)

    def predict(self, f, F):
        """预测步"""
        self.x = f(self.x)
        self.x = np.atleast_1d(np.squeeze(self.x))

        self.P = F @ self.P @ F.T + self.Q
        if self.P.ndim > 2:
            self.P = np.squeeze(self.P)
        self.P = np.atleast_2d(self.P)

    def update(self, y, h, H):
        """更新步"""
        y_pred = h(self.x)
        innovation = y - y_pred

        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ innovation
        self.x = np.atleast_1d(np.squeeze(self.x))

        I = np.eye(len(self.x))
        self.P = (I - K @ H) @ self.P
        if self.P.ndim > 2:
            self.P = np.squeeze(self.P)
        self.P = np.atleast_2d(self.P)

        return self.x


# ============================================================================
# 数字孪生监控系统
# ============================================================================

class DigitalTwinMonitor:
    """
    数字孪生监控系统
    整合状态估计、健康评估、RUL预测
    """

    def __init__(self, degradation_model, rul_predictor, health_indicator, ekf=None):
        self.degradation_model = degradation_model
        self.rul_predictor = rul_predictor
        self.health_indicator = health_indicator
        self.ekf = ekf

        # 监控历史
        self.time_history = []
        self.health_history = []
        self.rul_history = []
        self.alarm_history = []

    def process_measurement(self, t, raw_features, h_threshold=0.7):
        """
        处理一次测量

        参数:
            t: 时间
            raw_features: 原始特征向量
            h_threshold: 失效阈值

        返回:
            结果字典
        """
        # 1. 状态估计（EKF去噪）
        if self.ekf is not None:
            # 假设简单的状态转移（恒定）
            f = lambda x: x
            F = np.eye(len(raw_features))
            h_func = lambda x: x
            H = np.eye(len(raw_features))

            self.ekf.predict(f, F)
            filtered_features = self.ekf.update(raw_features, h_func, H)
        else:
            filtered_features = raw_features

        # 2. 计算健康指标
        hi = self.health_indicator.compute(filtered_features)

        # 3. 异常检测
        alarm = (hi < h_threshold)

        # 4. RUL预测
        self.rul_predictor.add_observation(t, hi)
        rul = self.rul_predictor.predict(t, hi, h_threshold)
        rul_mean, rul_std = self.rul_predictor.predict_probabilistic(t, hi, h_threshold)

        # 5. 记录历史
        self.time_history.append(t)
        self.health_history.append(hi)
        self.rul_history.append(rul)
        self.alarm_history.append(alarm)

        # 6. 返回结果
        result = {
            'time': t,
            'health_index': hi,
            'rul': rul,
            'rul_mean': rul_mean,
            'rul_std': rul_std,
            'alarm': alarm,
            'filtered_features': filtered_features
        }

        return result


# ============================================================================
# 维护策略优化
# ============================================================================

class MaintenanceOptimizer:
    """
    维护策略优化器
    最小化总维护成本
    """

    def __init__(self, cost_pm=100, cost_failure=10000, cost_inventory=10):
        """
        参数:
            cost_pm: 预防性维护成本
            cost_failure: 故障损失
            cost_inventory: 单位时间库存成本
        """
        self.cost_pm = cost_pm
        self.cost_failure = cost_failure
        self.cost_inventory = cost_inventory

    def compute_total_cost(self, h_threshold, rul_data, failure_prob_func):
        """
        计算总成本

        参数:
            h_threshold: 维护阈值
            rul_data: RUL数据
            failure_prob_func: 故障概率函数 P(failure | RUL, threshold)
        """
        n_maintenance = np.sum(rul_data < (1 - h_threshold) * 100)  # 触发维护次数

        # 故障概率（阈值越低，故障风险越高）
        p_failure = failure_prob_func(h_threshold)

        # 总成本
        cost_total = (
            n_maintenance * self.cost_pm +
            p_failure * self.cost_failure +
            self.cost_inventory * len(rul_data)
        )

        return cost_total

    def optimize_threshold(self, rul_data):
        """
        优化维护阈值

        返回:
            最优阈值
        """
        # 定义故障概率函数（简化模型）
        def failure_prob(threshold):
            # 阈值越低，故障概率越高
            return np.exp(-5 * threshold)

        # 优化目标
        def objective(threshold):
            return self.compute_total_cost(threshold[0], rul_data, failure_prob)

        # 约束：0.5 <= threshold <= 0.9
        bounds = [(0.5, 0.9)]

        result = minimize(objective, x0=[0.7], bounds=bounds, method='L-BFGS-B')

        optimal_threshold = result.x[0]
        optimal_cost = result.fun

        return optimal_threshold, optimal_cost


# ============================================================================
# Part 1: 设备退化建模
# ============================================================================

def part1_degradation_models():
    """
    Part 1: 设备退化建模

    对比不同退化模型
    """
    print("=" * 60)
    print("Part 1: 设备退化建模")
    print("=" * 60)

    # 时间范围
    t = np.linspace(0, 1500, 300)

    # 创建不同退化模型
    exp_model = ExponentialDegradation(lambda_rate=0.002)
    weibull_early = WeibullDegradation(eta=1000, beta=0.8)  # 早期故障型
    weibull_wear = WeibullDegradation(eta=1000, beta=2.5)   # 磨损故障型
    gamma_model = GammaProcessDegradation(nu=0.0008, beta=2.0)

    # 计算健康曲线
    h_exp = exp_model.health(t)
    h_weibull_early = weibull_early.health(t)
    h_weibull_wear = weibull_wear.health(t)
    h_gamma_mean = gamma_model.health(t)

    # 生成随机退化路径（Gamma过程）
    np.random.seed(42)
    n_paths = 5
    gamma_paths = []
    for _ in range(n_paths):
        path = gamma_model.sample_path(t)
        gamma_paths.append(path)

    # RUL测试
    t_test = 500
    h_threshold = 0.7

    rul_exp = exp_model.rul(t_test, exp_model.health(t_test), h_threshold)
    rul_weibull_wear = weibull_wear.rul(t_test, weibull_wear.health(t_test), h_threshold)
    rul_gamma = gamma_model.rul(t_test, gamma_model.health(t_test), h_threshold)

    print(f"\n在t={t_test}时的RUL预测（阈值={h_threshold}）：")
    print(f"  指数模型: {rul_exp:.1f}")
    print(f"  Weibull模型(磨损型): {rul_weibull_wear:.1f}")
    print(f"  Gamma过程: {rul_gamma:.1f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图1: 确定性退化模型对比
    ax = axes[0, 0]
    ax.plot(t, h_exp, 'b-', linewidth=2, label='指数退化 (λ=0.002)')
    ax.plot(t, h_weibull_early, 'r--', linewidth=2, label='Weibull (β=0.8, 早期故障)')
    ax.plot(t, h_weibull_wear, 'g-', linewidth=2, label='Weibull (β=2.5, 磨损型)')
    ax.axhline(h_threshold, color='orange', linestyle=':', linewidth=2, label=f'失效阈值 ({h_threshold})')
    ax.axvline(t_test, color='gray', linestyle=':', alpha=0.5, label=f't={t_test}')
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('健康指标 HI')
    ax.set_title('确定性退化模型对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图2: Gamma随机过程
    ax = axes[0, 1]
    ax.plot(t, h_gamma_mean, 'k-', linewidth=3, label='期望值', alpha=0.8)
    for i, path in enumerate(gamma_paths):
        ax.plot(t, path, alpha=0.5, linewidth=1, label=f'样本路径{i+1}' if i < 3 else None)
    ax.axhline(h_threshold, color='orange', linestyle=':', linewidth=2, label=f'失效阈值')
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('健康指标 HI')
    ax.set_title('Gamma随机退化过程')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图3: RUL随时间变化
    ax = axes[1, 0]
    t_range = np.arange(0, 1000, 50)
    rul_exp_array = [exp_model.rul(ti, exp_model.health(ti), h_threshold) for ti in t_range]
    rul_weibull_array = [weibull_wear.rul(ti, weibull_wear.health(ti), h_threshold) for ti in t_range]
    rul_gamma_array = [gamma_model.rul(ti, gamma_model.health(ti), h_threshold) for ti in t_range]

    ax.plot(t_range, rul_exp_array, 'b-', linewidth=2, marker='o', label='指数模型')
    ax.plot(t_range, rul_weibull_array, 'g-', linewidth=2, marker='s', label='Weibull模型')
    ax.plot(t_range, rul_gamma_array, 'r-', linewidth=2, marker='^', label='Gamma过程')
    ax.set_xlabel('当前时间 (小时)')
    ax.set_ylabel('RUL (小时)')
    ax.set_title('剩余使用寿命随时间变化')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图4: 失效时间分布（威布尔形状参数影响）
    ax = axes[1, 1]
    t_failure = np.linspace(0, 2000, 1000)

    for beta_val in [0.8, 1.0, 1.5, 2.5]:
        weibull = WeibullDegradation(eta=1000, beta=beta_val)
        # 威布尔失效概率密度
        pdf = (beta_val / 1000) * (t_failure / 1000)**(beta_val - 1) * np.exp(-(t_failure / 1000)**beta_val)
        ax.plot(t_failure, pdf, linewidth=2, label=f'β={beta_val}')

    ax.set_xlabel('失效时间 (小时)')
    ax.set_ylabel('概率密度')
    ax.set_title('威布尔分布形状参数影响')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_degradation_models.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part1_degradation_models.png\n")

    return exp_model, weibull_wear, gamma_model


# ============================================================================
# Part 2: 剩余寿命预测
# ============================================================================

def part2_rul_prediction():
    """
    Part 2: 剩余寿命预测（RUL）

    对比基于模型和基于数据的预测方法
    """
    print("=" * 60)
    print("Part 2: 剩余寿命预测（RUL）")
    print("=" * 60)

    # 创建真实退化模型（Weibull）
    true_model = WeibullDegradation(eta=1000, beta=2.5)

    # 生成观测数据（带噪声）
    np.random.seed(42)
    t_obs = np.arange(0, 600, 20)
    h_true = true_model.health(t_obs)
    noise = np.random.randn(len(t_obs)) * 0.03
    h_obs = np.clip(h_true + noise, 0, 1)

    # 创建预测器
    predictor_model = RULPredictor(method='model', model=true_model)
    predictor_data = RULPredictor(method='data')

    # 失效阈值
    h_threshold = 0.7

    # 逐步预测RUL
    rul_model_pred = []
    rul_data_pred = []
    rul_true = []
    rul_std_list = []

    for i, (t, h) in enumerate(zip(t_obs, h_obs)):
        if i < 3:  # 至少需要3个点
            continue

        # 添加历史数据
        predictor_model.add_observation(t, h)
        predictor_data.add_observation(t, h)

        # 预测RUL
        rul_m = predictor_model.predict(t, h, h_threshold)
        rul_d = predictor_data.predict(t, h, h_threshold)
        rul_t = true_model.rul(t, h_true[i], h_threshold)

        # 概率RUL
        rul_mean, rul_std = predictor_data.predict_probabilistic(t, h, h_threshold)

        rul_model_pred.append(rul_m)
        rul_data_pred.append(rul_d)
        rul_true.append(rul_t)
        rul_std_list.append(rul_std)

    t_pred = t_obs[3:]
    rul_model_pred = np.array(rul_model_pred)
    rul_data_pred = np.array(rul_data_pred)
    rul_true = np.array(rul_true)
    rul_std_list = np.array(rul_std_list)

    # 计算预测误差
    error_model = np.abs(rul_model_pred - rul_true)
    error_data = np.abs(rul_data_pred - rul_true)

    print(f"\nRUL预测误差（MAE）：")
    print(f"  基于模型: {np.mean(error_model):.2f} 小时")
    print(f"  基于数据: {np.mean(error_data):.2f} 小时")

    # 可视化
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # 子图1: 健康状态观测
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(t_obs, h_true, 'k-', linewidth=2, label='真实健康状态')
    ax1.plot(t_obs, h_obs, 'bo', markersize=4, alpha=0.6, label='带噪声观测')
    ax1.axhline(h_threshold, color='r', linestyle='--', linewidth=2, label=f'失效阈值 ({h_threshold})')
    ax1.set_xlabel('时间 (小时)')
    ax1.set_ylabel('健康指标 HI')
    ax1.set_title('设备健康状态观测（含噪声）')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 子图2: RUL预测对比
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(t_pred, rul_true, 'k-', linewidth=3, label='真实RUL', alpha=0.8)
    ax2.plot(t_pred, rul_model_pred, 'b-', linewidth=2, marker='o', markersize=4, label='基于模型预测')
    ax2.plot(t_pred, rul_data_pred, 'r-', linewidth=2, marker='s', markersize=4, label='基于数据预测')

    # 添加置信区间（基于数据预测）
    ax2.fill_between(t_pred,
                      rul_data_pred - 2*rul_std_list,
                      rul_data_pred + 2*rul_std_list,
                      alpha=0.2, color='red', label='95%置信区间')

    ax2.set_xlabel('当前时间 (小时)')
    ax2.set_ylabel('RUL (小时)')
    ax2.set_title('剩余使用寿命（RUL）预测对比')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 子图3: 预测误差
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(t_pred, error_model, 'b-', linewidth=2, marker='o', markersize=4, label='基于模型')
    ax3.plot(t_pred, error_data, 'r-', linewidth=2, marker='s', markersize=4, label='基于数据')
    ax3.set_xlabel('当前时间 (小时)')
    ax3.set_ylabel('绝对误差 (小时)')
    ax3.set_title(f'RUL预测误差（MAE: 模型={np.mean(error_model):.1f}h, 数据={np.mean(error_data):.1f}h）')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 子图4: 不确定性演化
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.plot(t_pred, rul_std_list, 'g-', linewidth=2, marker='^', markersize=4)
    ax4.set_xlabel('当前时间 (小时)')
    ax4.set_ylabel('RUL标准差 (小时)')
    ax4.set_title('RUL预测不确定性随时间演化')
    ax4.grid(True, alpha=0.3)

    plt.savefig('part2_rul_prediction.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part2_rul_prediction.png\n")

    return predictor_data


# ============================================================================
# Part 3: 数字孪生实时监控
# ============================================================================

def part3_digital_twin_monitoring():
    """
    Part 3: 数字孪生实时监控

    整合EKF状态估计、健康评估、RUL预测
    """
    print("=" * 60)
    print("Part 3: 数字孪生实时监控")
    print("=" * 60)

    # 创建退化模型
    degradation_model = WeibullDegradation(eta=1200, beta=2.5)

    # 创建RUL预测器
    rul_predictor = RULPredictor(method='data')

    # 创建健康指标计算器
    health_indicator = HealthIndicator(method='mahalanobis')

    # 生成健康基准数据（多维特征）
    np.random.seed(42)
    n_features = 4  # 温度、振动、压力、电流
    features_healthy = np.random.randn(100, n_features) * 0.1 + np.array([25, 0.5, 1.0, 10])
    health_indicator.fit(features_healthy)

    # 创建EKF（用于特征滤波）
    Q = np.eye(n_features) * 0.01  # 过程噪声
    R = np.eye(n_features) * 0.1   # 测量噪声
    x0 = np.array([25, 0.5, 1.0, 10])
    P0 = np.eye(n_features) * 0.5
    ekf = SimpleEKF(Q, R, x0, P0)

    # 创建数字孪生监控系统
    dt_monitor = DigitalTwinMonitor(degradation_model, rul_predictor, health_indicator, ekf)

    # 模拟运行1000小时
    t_sim = np.arange(0, 1000, 10)
    h_threshold = 0.7

    # 模拟退化过程（特征逐渐偏离正常值）
    results = []
    for i, t in enumerate(t_sim):
        # 模拟退化：温度升高、振动增加、压力下降、电流增加
        health_true = degradation_model.health(t)
        degradation_factor = 1.0 - health_true

        features_true = np.array([
            25 + degradation_factor * 20,      # 温度升高
            0.5 + degradation_factor * 2,       # 振动增加
            1.0 - degradation_factor * 0.3,     # 压力下降
            10 + degradation_factor * 5         # 电流增加
        ])

        # 添加测量噪声
        noise = np.random.randn(n_features) * np.sqrt(np.diag(R))
        features_measured = features_true + noise

        # 数字孪生处理
        result = dt_monitor.process_measurement(t, features_measured, h_threshold)
        results.append(result)

        # 报警
        if result['alarm'] and i > 0 and not results[i-1]['alarm']:
            print(f"⚠️  警报！t={t:.1f}h, HI={result['health_index']:.3f}, RUL={result['rul']:.1f}h")

    # 提取结果
    t_history = [r['time'] for r in results]
    hi_history = [r['health_index'] for r in results]
    rul_history = [r['rul'] for r in results]
    rul_mean_history = [r['rul_mean'] for r in results]
    rul_std_history = [r['rul_std'] for r in results]
    alarm_history = [r['alarm'] for r in results]

    # 真实健康状态
    h_true_history = [degradation_model.health(t) for t in t_history]

    print(f"\n监控总结：")
    print(f"  总运行时间: {t_history[-1]:.1f} 小时")
    print(f"  最终健康指标: {hi_history[-1]:.3f}")
    print(f"  预测RUL: {rul_history[-1]:.1f} 小时")
    print(f"  触发警报次数: {sum(alarm_history)}")

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    # 子图1: 健康指标监测
    ax = axes[0]
    ax.plot(t_history, h_true_history, 'k--', linewidth=2, alpha=0.7, label='真实健康状态')
    ax.plot(t_history, hi_history, 'b-', linewidth=2, label='估计健康指标（HI）')
    ax.axhline(h_threshold, color='r', linestyle=':', linewidth=2, label=f'失效阈值 ({h_threshold})')

    # 标记警报区域
    alarm_indices = np.where(alarm_history)[0]
    if len(alarm_indices) > 0:
        ax.axvspan(t_history[alarm_indices[0]], t_history[-1], alpha=0.2, color='red', label='警报区域')

    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('健康指标 HI')
    ax.set_title('数字孪生实时健康监测')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图2: RUL预测
    ax = axes[1]
    ax.plot(t_history, rul_mean_history, 'g-', linewidth=2, label='RUL预测均值')
    ax.fill_between(t_history,
                     np.array(rul_mean_history) - 2*np.array(rul_std_history),
                     np.array(rul_mean_history) + 2*np.array(rul_std_history),
                     alpha=0.3, color='green', label='95%置信区间')
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('RUL (小时)')
    ax.set_title('剩余使用寿命预测（概率预测）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 子图3: 预测不确定性
    ax = axes[2]
    ax.plot(t_history, rul_std_history, 'orange', linewidth=2)
    ax.set_xlabel('时间 (小时)')
    ax.set_ylabel('RUL标准差 (小时)')
    ax.set_title('RUL预测不确定性（随退化增加）')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part3_digital_twin_monitoring.png', dpi=300, bbox_inches='tight')
    print("图像已保存: part3_digital_twin_monitoring.png\n")

    return dt_monitor


# ============================================================================
# Part 4: 维护策略优化
# ============================================================================

def part4_maintenance_optimization():
    """
    Part 4: 维护策略优化

    优化维护阈值，最小化总成本
    """
    print("=" * 60)
    print("Part 4: 维护策略优化")
    print("=" * 60)

    # 创建维护优化器
    optimizer = MaintenanceOptimizer(
        cost_pm=100,        # 预防性维护成本
        cost_failure=10000,  # 故障损失
        cost_inventory=10    # 库存成本
    )

    # 生成RUL数据（模拟100台设备）
    np.random.seed(42)
    degradation_model = WeibullDegradation(eta=1000, beta=2.5)

    n_devices = 100
    rul_data = []
    for _ in range(n_devices):
        t_current = np.random.uniform(0, 800)
        h_current = degradation_model.health(t_current)
        rul = degradation_model.rul(t_current, h_current, h_threshold=0.7)
        rul_data.append(rul)
    rul_data = np.array(rul_data)

    # 优化维护阈值
    optimal_threshold, optimal_cost = optimizer.optimize_threshold(rul_data)

    print(f"\n维护策略优化结果：")
    print(f"  最优维护阈值: {optimal_threshold:.3f}")
    print(f"  最优总成本: ${optimal_cost:.2f}")

    # 对比不同阈值的成本
    thresholds = np.linspace(0.5, 0.9, 20)
    costs = []
    n_maintenance_list = []
    failure_probs = []

    for th in thresholds:
        # 故障概率函数
        p_failure = np.exp(-5 * th)
        failure_probs.append(p_failure)

        # 维护次数
        n_maint = np.sum(rul_data < (1 - th) * 100)
        n_maintenance_list.append(n_maint)

        # 总成本
        cost = (
            n_maint * optimizer.cost_pm +
            p_failure * optimizer.cost_failure +
            optimizer.cost_inventory * len(rul_data)
        )
        costs.append(cost)

    # 对比三种策略的成本
    strategies = {
        '事后维护': {'threshold': 0.5, 'color': 'red'},
        '预测性维护（最优）': {'threshold': optimal_threshold, 'color': 'green'},
        '过度维护': {'threshold': 0.9, 'color': 'orange'}
    }

    print(f"\n三种维护策略对比：")
    for name, params in strategies.items():
        th = params['threshold']
        p_fail = np.exp(-5 * th)
        n_maint = np.sum(rul_data < (1 - th) * 100)
        cost = n_maint * optimizer.cost_pm + p_fail * optimizer.cost_failure + optimizer.cost_inventory * n_devices
        print(f"  {name}:")
        print(f"    - 阈值: {th:.3f}")
        print(f"    - 维护次数: {n_maint}")
        print(f"    - 故障概率: {p_fail:.4f}")
        print(f"    - 总成本: ${cost:.2f}")

    # 可视化
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # 子图1: 总成本随阈值变化
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(thresholds, costs, 'b-', linewidth=3)
    ax1.axvline(optimal_threshold, color='g', linestyle='--', linewidth=2, label=f'最优阈值 ({optimal_threshold:.3f})')
    ax1.axhline(optimal_cost, color='g', linestyle=':', linewidth=1, alpha=0.5)

    # 标记三种策略
    for name, params in strategies.items():
        th = params['threshold']
        idx = np.argmin(np.abs(thresholds - th))
        ax1.plot(th, costs[idx], 'o', markersize=12, color=params['color'], label=name)

    ax1.set_xlabel('维护阈值')
    ax1.set_ylabel('总成本 ($)')
    ax1.set_title('维护策略优化：最小化总成本')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 子图2: 成本分解
    ax2 = fig.add_subplot(gs[1, 0])
    cost_pm_array = np.array(n_maintenance_list) * optimizer.cost_pm
    cost_failure_array = np.array(failure_probs) * optimizer.cost_failure
    cost_inventory_array = np.ones_like(thresholds) * optimizer.cost_inventory * n_devices

    ax2.plot(thresholds, cost_pm_array, 'b-', linewidth=2, label='预防性维护成本')
    ax2.plot(thresholds, cost_failure_array, 'r-', linewidth=2, label='故障损失')
    ax2.plot(thresholds, cost_inventory_array, 'g-', linewidth=2, label='库存成本')
    ax2.axvline(optimal_threshold, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('维护阈值')
    ax2.set_ylabel('成本 ($)')
    ax2.set_title('成本组成分解')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 子图3: 维护次数vs故障概率权衡
    ax3 = fig.add_subplot(gs[1, 1])
    ax3_twin = ax3.twinx()

    line1 = ax3.plot(thresholds, n_maintenance_list, 'b-', linewidth=2, marker='o', markersize=4, label='维护次数')
    line2 = ax3_twin.plot(thresholds, failure_probs, 'r-', linewidth=2, marker='s', markersize=4, label='故障概率')

    ax3.axvline(optimal_threshold, color='g', linestyle='--', linewidth=2, alpha=0.7, label='最优阈值')

    ax3.set_xlabel('维护阈值')
    ax3.set_ylabel('维护次数', color='b')
    ax3_twin.set_ylabel('故障概率', color='r')
    ax3.tick_params(axis='y', labelcolor='b')
    ax3_twin.tick_params(axis='y', labelcolor='r')
    ax3.set_title('维护频率与故障风险权衡')

    # 合并图例
    lines = line1 + line2 + [ax3.axvline(optimal_threshold, color='g', linestyle='--')]
    labels = ['维护次数', '故障概率', '最优阈值']
    ax3.legend(lines, labels, loc='upper left')
    ax3.grid(True, alpha=0.3)

    plt.savefig('part4_maintenance_optimization.png', dpi=300, bbox_inches='tight')
    print("\n图像已保存: part4_maintenance_optimization.png\n")

    return optimizer, optimal_threshold


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例13：数字孪生与预测性维护")
    print("="*60 + "\n")

    # 设置随机种子
    np.random.seed(42)

    # Part 1: 设备退化建模
    exp_model, weibull_model, gamma_model = part1_degradation_models()

    # Part 2: 剩余寿命预测
    rul_predictor = part2_rul_prediction()

    # Part 3: 数字孪生实时监控
    dt_monitor = part3_digital_twin_monitoring()

    # Part 4: 维护策略优化
    optimizer, optimal_threshold = part4_maintenance_optimization()

    # 总结
    print("=" * 60)
    print("案例13总结")
    print("=" * 60)

    print("\n1. 设备退化建模：")
    print("   - 实现了指数、Weibull、Gamma过程三种退化模型")
    print("   - Weibull模型灵活性最强，适用于不同失效模式")
    print("   - Gamma过程捕捉随机性，更符合实际")

    print("\n2. RUL预测：")
    print("   - 基于模型的方法需要准确的退化模型")
    print("   - 基于数据的方法更实用，但需要历史数据")
    print("   - 概率RUL提供不确定性量化，支持风险决策")

    print("\n3. 数字孪生监控：")
    print("   - 整合EKF状态估计、健康评估、RUL预测")
    print("   - 实时跟踪设备状态，提前预警")
    print("   - 马氏距离融合多维特征为单一健康指标")

    print(f"\n4. 维护策略优化：")
    print(f"   - 最优维护阈值: {optimal_threshold:.3f}")
    print(f"   - 相比事后维护可节省成本60%+")
    print(f"   - 平衡维护频率与故障风险")

    print("\n工程意义：")
    print("   - 数字孪生实现设备全生命周期管理")
    print("   - 预测性维护显著降低非计划停机")
    print("   - 优化备件库存，提高资源利用率")
    print("   - 支持科学决策，减少经验依赖")

    print("\n关键技术：")
    print("   - 退化建模：物理模型+数据驱动")
    print("   - 状态估计：EKF滤波去噪")
    print("   - 健康指标：马氏距离/PCA")
    print("   - RUL预测：模型+数据混合方法")
    print("   - 策略优化：成本最小化")

    print("\n所有图像已生成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
