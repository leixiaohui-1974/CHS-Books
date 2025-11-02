"""
案例25：智能水文预报平台
========================

演示智能水文预报平台，集成多种预报方法、
机器学习后处理、不确定性量化和智能决策支持。

核心内容：
1. 多模型集成预报
2. 机器学习后处理
3. 不确定性量化
4. 智能决策支持
5. 综合评估

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys
import os
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MultiModelEnsemble:
    """多模型集成预报"""
    
    def __init__(self):
        """初始化多模型集成"""
        self.models = {}
        self.weights = {}
        
    def add_model(self, name: str, params: Dict, weight: float = 1.0):
        """添加模型"""
        model = XinAnJiangModel(params)
        self.models[name] = model
        self.weights[name] = weight
    
    def forecast(self, rainfall: np.ndarray, evaporation: np.ndarray) -> Dict:
        """
        集成预报
        
        Returns
        -------
        results : dict
            包含各模型预报和集成结果
        """
        forecasts = {}
        
        # 各模型预报
        for name, model in self.models.items():
            result = model.run(rainfall, evaporation)
            Q = result['Q']
            Q = np.nan_to_num(Q, nan=0.0, posinf=0.0, neginf=0.0)
            Q = np.maximum(Q, 0.0)
            forecasts[name] = Q
        
        # 加权集成
        ensemble = np.zeros(len(rainfall))
        total_weight = sum(self.weights.values())
        
        for name, forecast in forecasts.items():
            ensemble += forecast * self.weights[name] / total_weight
        
        # 简单平均
        simple_mean = np.mean(list(forecasts.values()), axis=0)
        
        return {
            'forecasts': forecasts,
            'ensemble_weighted': ensemble,
            'ensemble_mean': simple_mean
        }


class MLPostProcessor:
    """机器学习后处理（简化版线性回归）"""
    
    def __init__(self, method: str = 'linear'):
        """
        初始化后处理器
        
        Parameters
        ----------
        method : str
            方法：'linear' (线性回归) 或 'poly' (多项式回归)
        """
        self.method = method
        self.coef_ = None
        self.intercept_ = None
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        训练后处理模型（线性回归）
        
        Parameters
        ----------
        X : np.ndarray
            特征 (n_samples, n_features)
        y : np.ndarray
            目标 (n_samples,)
        """
        # 添加偏置项
        X_bias = np.column_stack([np.ones(len(X)), X])
        
        # 最小二乘法: β = (XᵀX)⁻¹Xᵀy
        try:
            XtX = X_bias.T @ X_bias
            Xty = X_bias.T @ y
            beta = np.linalg.solve(XtX, Xty)
            
            self.intercept_ = beta[0]
            self.coef_ = beta[1:]
            self.is_trained = True
        except:
            # 如果失败，使用简单的比例校正
            self.coef_ = np.array([np.mean(y) / (np.mean(X) + 1e-10)])
            self.intercept_ = 0
            self.is_trained = True
    
    def correct(self, forecast: np.ndarray, features: np.ndarray = None) -> np.ndarray:
        """
        校正预报
        
        Parameters
        ----------
        forecast : np.ndarray
            原始预报
        features : np.ndarray
            额外特征
            
        Returns
        -------
        corrected : np.ndarray
            校正后的预报
        """
        if not self.is_trained:
            return forecast
        
        # 构建特征
        if features is None:
            X = forecast.reshape(-1, 1)
        else:
            X = np.column_stack([forecast.reshape(-1, 1), features])
        
        # 线性预测
        corrected = self.intercept_ + X @ self.coef_
        return np.maximum(corrected, 0.0)


class IntelligentForecastPlatform:
    """智能预报平台"""
    
    def __init__(self):
        """初始化平台"""
        self.multi_model = MultiModelEnsemble()
        self.ml_processor = None
        
        # 预报记录
        self.forecast_history = []
        self.observation_history = []
        
    def setup_models(self):
        """设置多模型"""
        # 基准模型
        base_params = {
            'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.18,
            'WM': 120.0, 'B': 0.40, 'IM': 0.02, 'SM': 30.0,
            'EX': 1.2, 'KG': 0.45, 'KI': 0.35,
            'CG': 0.98, 'CI': 0.70, 'CS': 0.85
        }
        
        # 模型1：基准
        self.multi_model.add_model('模型1(基准)', base_params.copy(), weight=1.0)
        
        # 模型2：湿润情景（WM更大）
        params2 = base_params.copy()
        params2['WM'] = 140.0
        params2['B'] = 0.45
        self.multi_model.add_model('模型2(湿润)', params2, weight=1.0)
        
        # 模型3：干旱情景（WM更小）
        params3 = base_params.copy()
        params3['WM'] = 100.0
        params3['B'] = 0.35
        self.multi_model.add_model('模型3(干旱)', params3, weight=1.0)
    
    def forecast(self, rainfall: np.ndarray, evaporation: np.ndarray,
                use_ml: bool = False) -> Dict:
        """
        执行预报
        
        Parameters
        ----------
        rainfall : np.ndarray
            降雨
        evaporation : np.ndarray
            蒸发
        use_ml : bool
            是否使用ML后处理
            
        Returns
        -------
        results : dict
            预报结果
        """
        # 多模型集成预报
        ensemble_result = self.multi_model.forecast(rainfall, evaporation)
        
        # ML后处理
        if use_ml and self.ml_processor is not None and self.ml_processor.is_trained:
            forecast = ensemble_result['ensemble_weighted']
            corrected = self.ml_processor.correct(forecast)
            ensemble_result['ml_corrected'] = corrected
        
        return ensemble_result
    
    def evaluate(self, forecast: np.ndarray, observation: np.ndarray) -> Dict:
        """评估预报精度"""
        rmse = np.sqrt(np.mean((forecast - observation)**2))
        mae = np.mean(np.abs(forecast - observation))
        
        # NSE
        nse = 1 - np.sum((observation - forecast)**2) / \
                  np.sum((observation - np.mean(observation))**2)
        
        # 峰值误差
        peak_obs = np.max(observation)
        peak_for = np.max(forecast)
        peak_error = np.abs(peak_for - peak_obs) / peak_obs * 100 if peak_obs > 0 else 0
        
        # 峰现时间误差
        peak_time_obs = np.argmax(observation)
        peak_time_for = np.argmax(forecast)
        peak_time_error = peak_time_for - peak_time_obs
        
        return {
            'rmse': rmse,
            'mae': mae,
            'nse': nse,
            'peak_error': peak_error,
            'peak_time_error': peak_time_error
        }


def run_intelligent_forecast():
    """运行智能预报平台"""
    print("\n" + "="*70)
    print("案例25：智能水文预报平台")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 初始化平台
    print("1. 初始化智能预报平台...")
    platform = IntelligentForecastPlatform()
    platform.setup_models()
    
    print(f"   模型数量: {len(platform.multi_model.models)}")
    for name in platform.multi_model.models.keys():
        print(f"   - {name}")
    print()
    
    # 2. 生成训练数据
    print("2. 生成训练数据...")
    np.random.seed(42)
    
    # 历史数据（用于训练ML）
    n_train = 60
    train_rainfall = np.ones(n_train) * 5.0
    train_rainfall += np.random.normal(0, 2, n_train)
    train_rainfall = np.maximum(train_rainfall, 0)
    
    # 添加几次洪峰
    for peak_start in [15, 35]:
        for i in range(10):
            if peak_start + i < n_train:
                train_rainfall[peak_start + i] += 30 * np.exp(-((i - 5) / 2)**2)
    
    train_evap = np.ones(n_train) * 4.0
    
    # 生成"观测"数据
    true_params = {
        'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.20,  # C稍大
        'WM': 125.0, 'B': 0.42, 'IM': 0.02, 'SM': 30.0,
        'EX': 1.2, 'KG': 0.47, 'KI': 0.35,
        'CG': 0.98, 'CI': 0.70, 'CS': 0.85
    }
    true_model = XinAnJiangModel(true_params)
    train_obs_result = true_model.run(train_rainfall, train_evap)
    train_obs = train_obs_result['Q']
    train_obs = np.nan_to_num(train_obs, nan=0.0, posinf=0.0, neginf=0.0)
    train_obs = np.maximum(train_obs, 0.0)
    
    # 添加观测噪声
    train_obs += np.random.normal(0, 0.3, n_train)
    train_obs = np.maximum(train_obs, 0.0)
    
    print(f"   训练样本数: {n_train}")
    print(f"   最大观测流量: {np.max(train_obs):.1f} m³/s\n")
    
    # 3. 训练ML后处理
    print("3. 训练机器学习后处理器...")
    
    # 获取训练期的集成预报
    train_forecast_result = platform.forecast(train_rainfall, train_evap, use_ml=False)
    train_forecast = train_forecast_result['ensemble_weighted']
    
    # 构建训练特征
    X_train = train_forecast.reshape(-1, 1)
    y_train = train_obs
    
    # 训练线性回归
    platform.ml_processor = MLPostProcessor(method='linear')
    platform.ml_processor.train(X_train, y_train)
    
    print(f"   后处理方法: 线性回归")
    print(f"   训练完成\n")
    
    # 4. 测试预报
    print("4. 执行预报测试...")
    
    # 测试数据
    n_test = 48
    test_rainfall = np.ones(n_test) * 5.0
    test_rainfall += np.random.normal(0, 2, n_test)
    test_rainfall = np.maximum(test_rainfall, 0)
    
    # 添加洪峰
    for i in range(12):
        if 10 + i < n_test:
            test_rainfall[10 + i] += 35 * np.exp(-((i - 6) / 2.5)**2)
    
    test_evap = np.ones(n_test) * 4.0
    
    # 生成测试观测
    test_obs_result = true_model.run(test_rainfall, test_evap)
    test_obs = test_obs_result['Q']
    test_obs = np.nan_to_num(test_obs, nan=0.0, posinf=0.0, neginf=0.0)
    test_obs = np.maximum(test_obs, 0.0)
    test_obs += np.random.normal(0, 0.3, n_test)
    test_obs = np.maximum(test_obs, 0.0)
    
    # 多种预报方法
    test_result = platform.forecast(test_rainfall, test_evap, use_ml=True)
    
    print(f"   测试样本数: {n_test}")
    print(f"   最大观测流量: {np.max(test_obs):.1f} m³/s\n")
    
    # 5. 评估对比
    print("="*70)
    print("预报方法对比评估")
    print("="*70)
    
    # 各种方法
    methods = {
        '模型1(基准)': test_result['forecasts']['模型1(基准)'],
        '模型2(湿润)': test_result['forecasts']['模型2(湿润)'],
        '模型3(干旱)': test_result['forecasts']['模型3(干旱)'],
        '加权集成': test_result['ensemble_weighted'],
        '简单平均': test_result['ensemble_mean'],
        'ML后处理': test_result.get('ml_corrected', test_result['ensemble_weighted'])
    }
    
    evaluations = {}
    for name, forecast in methods.items():
        eval_result = platform.evaluate(forecast, test_obs)
        evaluations[name] = eval_result
        
        print(f"\n【{name}】")
        print(f"  RMSE:         {eval_result['rmse']:.2f} m³/s")
        print(f"  MAE:          {eval_result['mae']:.2f} m³/s")
        print(f"  NSE:          {eval_result['nse']:.4f}")
        print(f"  峰值误差:      {eval_result['peak_error']:.1f}%")
        print(f"  峰现时间误差:  {eval_result['peak_time_error']} h")
    
    # 6. 可视化
    print(f"\n5. 生成智能预报平台可视化...")
    
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(4, 3, hspace=0.45, wspace=0.3)
    
    time = np.arange(n_test)
    
    # 图1: 多模型预报对比
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(time, test_obs, 'k-', linewidth=3, label='观测', alpha=0.8)
    
    colors = ['blue', 'green', 'red']
    for i, (name, model_name) in enumerate(zip(['模型1(基准)', '模型2(湿润)', '模型3(干旱)'],
                                                 ['模型1(基准)', '模型2(湿润)', '模型3(干旱)'])):
        ax1.plot(time, test_result['forecasts'][model_name], 
                color=colors[i], linewidth=1.5, label=name, alpha=0.7, linestyle='--')
    
    ax1.set_xlabel('时间 (h)', fontsize=11)
    ax1.set_ylabel('流量 (m³/s)', fontsize=11)
    ax1.set_title('多模型预报对比', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10, ncol=4, loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 图2: 集成方法对比
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(time, test_obs, 'k-', linewidth=3, label='观测', alpha=0.8)
    ax2.plot(time, test_result['ensemble_weighted'], 'b-', 
            linewidth=2, label='加权集成', alpha=0.8)
    ax2.plot(time, test_result['ensemble_mean'], 'g--',
            linewidth=2, label='简单平均', alpha=0.8)
    
    if 'ml_corrected' in test_result:
        ax2.plot(time, test_result['ml_corrected'], 'r-',
                linewidth=2, label='ML后处理', alpha=0.8)
    
    ax2.set_xlabel('时间 (h)', fontsize=11)
    ax2.set_ylabel('流量 (m³/s)', fontsize=11)
    ax2.set_title('集成预报与ML后处理', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10, ncol=4, loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # 图3: RMSE对比
    ax3 = fig.add_subplot(gs[2, 0])
    method_names = list(evaluations.keys())
    rmse_values = [evaluations[name]['rmse'] for name in method_names]
    
    bars = ax3.barh(method_names, rmse_values, color='steelblue', alpha=0.7)
    # 标记最优
    best_idx = np.argmin(rmse_values)
    bars[best_idx].set_color('red')
    
    ax3.set_xlabel('RMSE (m³/s)', fontsize=10)
    ax3.set_title('RMSE对比', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # 图4: NSE对比
    ax4 = fig.add_subplot(gs[2, 1])
    nse_values = [evaluations[name]['nse'] for name in method_names]
    
    bars = ax4.barh(method_names, nse_values, color='green', alpha=0.7)
    # 标记最优
    best_idx = np.argmax(nse_values)
    bars[best_idx].set_color('red')
    
    ax4.set_xlabel('NSE', fontsize=10)
    ax4.set_title('NSE对比', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='x')
    
    # 图5: 峰值误差对比
    ax5 = fig.add_subplot(gs[2, 2])
    peak_errors = [evaluations[name]['peak_error'] for name in method_names]
    
    bars = ax5.barh(method_names, peak_errors, color='orange', alpha=0.7)
    # 标记最优
    best_idx = np.argmin([abs(e) for e in peak_errors])
    bars[best_idx].set_color('red')
    
    ax5.set_xlabel('峰值误差 (%)', fontsize=10)
    ax5.set_title('峰值误差对比', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    
    # 图6: 散点图（ML前后对比）
    ax6 = fig.add_subplot(gs[3, 0])
    ensemble = test_result['ensemble_weighted']
    ax6.scatter(test_obs, ensemble, alpha=0.6, s=50, label='集成预报')
    if 'ml_corrected' in test_result:
        ax6.scatter(test_obs, test_result['ml_corrected'], 
                   alpha=0.6, s=50, c='red', label='ML校正')
    
    max_val = max(np.max(test_obs), np.max(ensemble)) * 1.1
    ax6.plot([0, max_val], [0, max_val], 'k--', linewidth=1, alpha=0.5)
    
    ax6.set_xlabel('观测 (m³/s)', fontsize=10)
    ax6.set_ylabel('预报 (m³/s)', fontsize=10)
    ax6.set_title('预报 vs 观测', fontsize=12, fontweight='bold')
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3)
    ax6.axis('equal')
    ax6.set_xlim([0, max_val])
    ax6.set_ylim([0, max_val])
    
    # 图7: 降雨过程
    ax7 = fig.add_subplot(gs[3, 1])
    ax7.bar(time, test_rainfall, color='blue', alpha=0.6, width=1.0)
    ax7.set_xlabel('时间 (h)', fontsize=10)
    ax7.set_ylabel('降雨 (mm/h)', fontsize=10)
    ax7.set_title('降雨过程', fontsize=12, fontweight='bold')
    ax7.grid(True, alpha=0.3, axis='y')
    
    # 图8: 综合评分
    ax8 = fig.add_subplot(gs[3, 2])
    
    # 计算综合评分（归一化RMSE和NSE）
    rmse_norm = 1 - (np.array(rmse_values) - min(rmse_values)) / (max(rmse_values) - min(rmse_values) + 1e-10)
    nse_norm = (np.array(nse_values) - min(nse_values)) / (max(nse_values) - min(nse_values) + 1e-10)
    composite_score = (rmse_norm + nse_norm) / 2 * 100
    
    bars = ax8.barh(method_names, composite_score, color='purple', alpha=0.7)
    # 标记最优
    best_idx = np.argmax(composite_score)
    bars[best_idx].set_color('red')
    
    ax8.set_xlabel('综合评分', fontsize=10)
    ax8.set_title('综合评分（RMSE+NSE）', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3, axis='x')
    ax8.set_xlim([0, 100])
    
    plt.savefig(f'{output_dir}/intelligent_forecast.png',
                dpi=300, bbox_inches='tight')
    print(f"   可视化已保存: {output_dir}/intelligent_forecast.png")
    plt.close()
    
    # 7. 最优方法推荐
    print(f"\n6. 智能推荐...")
    best_method = method_names[best_idx]
    print(f"   最优方法: {best_method}")
    print(f"   综合评分: {composite_score[best_idx]:.1f}/100")
    
    print(f"\n可视化已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_intelligent_forecast()
