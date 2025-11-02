"""
案例4.1：需水量深度学习预测 - 主程序

对比传统时间序列、机器学习和深度学习（LSTM）方法

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

from core.ml import LSTMPredictor, TimeSeriesPreprocessor
from core.forecasting import GreyPredictor  # 使用之前的灰色预测


class WaterDemandForecastSystem:
    """需水量预测系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 加载数据
        self.data = self._load_data()
        
        print(f"需水量预测系统: 数据{len(self.data)}天")
    
    def _load_data(self):
        """加载数据"""
        data_file = "data/water_demand_data.csv"
        
        if not Path(data_file).exists():
            print("数据文件不存在，生成模拟数据...")
            self._generate_data()
        
        df = pd.read_csv(data_file)
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def _generate_data(self):
        """生成模拟数据"""
        np.random.seed(42)
        n_days = 730
        
        dates = pd.date_range(start='2022-01-01', periods=n_days)
        
        # 基础需水量 + 趋势 + 季节 + 噪声
        t = np.arange(n_days)
        base = 50000
        trend = base * (1 + 0.02 * t / 365)
        
        day_of_year = np.array([d.timetuple().tm_yday for d in dates])
        seasonal = 5000 * np.sin(2 * np.pi * (day_of_year - 90) / 365)
        
        day_of_week = np.array([d.weekday() for d in dates])
        weekly = np.where(day_of_week < 5, 2000, -3000)
        
        temperature = 15 + 10 * np.sin(2 * np.pi * (day_of_year - 90) / 365) + np.random.normal(0, 3, n_days)
        rainfall = np.random.gamma(2, 5, n_days)
        rainfall = np.minimum(rainfall, 50)
        
        demand = trend + seasonal + weekly + 100 * (temperature - 15) - 50 * rainfall
        demand += np.random.normal(0, 1000, n_days)
        demand = np.maximum(demand, 10000)
        
        df = pd.DataFrame({
            'date': dates,
            'demand': demand,
            'temperature': temperature,
            'rainfall': rainfall,
            'day_of_week': day_of_week,
            'is_weekend': (day_of_week >= 5).astype(int),
            'month': [d.month for d in dates],
            'is_holiday': np.zeros(n_days)
        })
        
        df.to_csv("data/water_demand_data.csv", index=False)
        print("  模拟数据已生成")
    
    def method1_moving_average(self, window=7):
        """方法1：移动平均"""
        print("\n" + "=" * 70)
        print(f"方法1: 移动平均（窗口={window}天）")
        print("=" * 70)
        
        # 准备数据
        train_size = int(len(self.data) * 0.8)
        train_data = self.data[:train_size]
        test_data = self.data[train_size:]
        
        # 预测
        predictions = []
        for i in range(len(test_data)):
            if i < window:
                # 使用训练集最后window个点
                history = train_data['demand'].iloc[-window:].values
            else:
                # 使用测试集前面的点
                history = test_data['demand'].iloc[max(0, i-window):i].values
            
            pred = np.mean(history)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        actual = test_data['demand'].values
        
        # 评估
        mae = np.mean(np.abs(actual - predictions))
        rmse = np.sqrt(np.mean((actual - predictions) ** 2))
        mape = np.mean(np.abs((actual - predictions) / actual)) * 100
        
        print(f"\nMAE: {mae:.2f} m³/day")
        print(f"RMSE: {rmse:.2f} m³/day")
        print(f"MAPE: {mape:.2f}%")
        
        return {
            'method': 'Moving Average',
            'predictions': predictions,
            'actual': actual,
            'dates': test_data['date'].values,
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
    
    def method2_grey_prediction(self):
        """方法2：灰色预测"""
        print("\n" + "=" * 70)
        print("方法2: 灰色预测GM(1,1)")
        print("=" * 70)
        
        # 准备数据
        train_size = int(len(self.data) * 0.8)
        train_data = self.data[:train_size]['demand'].values
        test_data = self.data[train_size:]
        
        # 使用最近30个点训练
        gm = GreyPredictor()
        gm.fit(train_data[-30:])
        
        # 预测
        n_pred = len(test_data)
        predictions = gm.predict(n_pred)
        
        actual = test_data['demand'].values
        
        # 评估
        mae = np.mean(np.abs(actual - predictions))
        rmse = np.sqrt(np.mean((actual - predictions) ** 2))
        mape = np.mean(np.abs((actual - predictions) / actual)) * 100
        
        print(f"\nMAE: {mae:.2f} m³/day")
        print(f"RMSE: {rmse:.2f} m³/day")
        print(f"MAPE: {mape:.2f}%")
        
        return {
            'method': 'Grey GM(1,1)',
            'predictions': predictions,
            'actual': actual,
            'dates': test_data['date'].values,
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
    
    def method3_lstm(self, window_size=30):
        """方法3：LSTM深度学习"""
        print("\n" + "=" * 70)
        print(f"方法3: LSTM深度学习（窗口={window_size}天）")
        print("=" * 70)
        
        start_time = time.time()
        
        # 准备数据
        train_size = int(len(self.data) * 0.8)
        train_data = self.data[:train_size]['demand'].values
        test_data = self.data[train_size:]
        
        # 创建LSTM预测器
        lstm = LSTMPredictor(
            window_size=window_size,
            hidden_size=64,
            learning_rate=0.001
        )
        
        # 训练
        print("\n训练LSTM模型...")
        lstm.fit(
            train_data,
            epochs=50,
            validation_split=0.2,
            add_features=True,
            verbose=True
        )
        
        # 预测（逐步预测）
        print("\n进行预测...")
        predictions = []
        current_data = train_data.copy()
        
        for i in range(len(test_data)):
            # 预测下一个值
            pred = lstm.predict(current_data, steps=1, add_features=True)[0]
            predictions.append(pred)
            
            # 更新数据（使用真实值，避免误差累积）
            current_data = np.append(current_data, test_data['demand'].iloc[i])
        
        predictions = np.array(predictions)
        actual = test_data['demand'].values
        
        elapsed_time = time.time() - start_time
        
        # 评估
        mae = np.mean(np.abs(actual - predictions))
        rmse = np.sqrt(np.mean((actual - predictions) ** 2))
        mape = np.mean(np.abs((actual - predictions) / actual)) * 100
        
        print(f"\nMAE: {mae:.2f} m³/day")
        print(f"RMSE: {rmse:.2f} m³/day")
        print(f"MAPE: {mape:.2f}%")
        print(f"训练时间: {elapsed_time:.2f} 秒")
        
        return {
            'method': 'LSTM',
            'predictions': predictions,
            'actual': actual,
            'dates': test_data['date'].values,
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'time': elapsed_time
        }
    
    def visualize(self, results_list):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # 1. 预测曲线对比（前100天）
        n_show = min(100, len(results_list[0]['actual']))
        
        axes[0, 0].plot(range(n_show), results_list[0]['actual'][:n_show],
                       'k-', label='真实值', linewidth=2, alpha=0.7)
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        for i, result in enumerate(results_list):
            axes[0, 0].plot(range(n_show), result['predictions'][:n_show],
                          label=result['method'], linewidth=1.5, alpha=0.8, color=colors[i])
        
        axes[0, 0].set_xlabel('天数', fontsize=11)
        axes[0, 0].set_ylabel('需水量 (m³/day)', fontsize=11)
        axes[0, 0].set_title('预测曲线对比（前100天）', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. MAE对比
        methods = [r['method'] for r in results_list]
        maes = [r['mae'] for r in results_list]
        
        axes[0, 1].bar(methods, maes, color=colors, alpha=0.7)
        axes[0, 1].set_ylabel('MAE (m³/day)', fontsize=11)
        axes[0, 1].set_title('平均绝对误差对比', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        for i, (method, mae) in enumerate(zip(methods, maes)):
            axes[0, 1].text(i, mae, f'{mae:.0f}', 
                          ha='center', va='bottom', fontsize=10)
        
        # 3. MAPE对比
        mapes = [r['mape'] for r in results_list]
        
        axes[1, 0].bar(methods, mapes, color=colors, alpha=0.7)
        axes[1, 0].set_ylabel('MAPE (%)', fontsize=11)
        axes[1, 0].set_title('平均绝对百分比误差对比', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        for i, (method, mape) in enumerate(zip(methods, mapes)):
            axes[1, 0].text(i, mape, f'{mape:.2f}%', 
                          ha='center', va='bottom', fontsize=10)
        
        # 4. 散点图（预测vs实际）
        for i, result in enumerate(results_list):
            axes[1, 1].scatter(result['actual'], result['predictions'],
                             alpha=0.3, s=20, label=result['method'], color=colors[i])
        
        # 添加理想线
        all_actual = results_list[0]['actual']
        min_val, max_val = all_actual.min(), all_actual.max()
        axes[1, 1].plot([min_val, max_val], [min_val, max_val],
                       'r--', label='理想预测', linewidth=2)
        
        axes[1, 1].set_xlabel('实际需水量 (m³/day)', fontsize=11)
        axes[1, 1].set_ylabel('预测需水量 (m³/day)', fontsize=11)
        axes[1, 1].set_title('预测精度散点图', fontsize=12, fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/forecast_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: figures/forecast_comparison.png")
    
    def run(self):
        """运行完整预测系统"""
        print("\n" + "*" * 70)
        print(" " * 20 + "需水量深度学习预测")
        print(" " * 28 + "案例4.1")
        print("*" * 70)
        
        try:
            ma_result = self.method1_moving_average(window=7)
            gm_result = self.method2_grey_prediction()
            lstm_result = self.method3_lstm(window_size=30)
            
            results_list = [ma_result, gm_result, lstm_result]
            
            self.visualize(results_list)
            
            print("\n" + "=" * 70)
            print("预测完成！")
            print("=" * 70)
            
            # 性能总结
            print(f"\n性能总结:")
            for result in results_list:
                print(f"\n  {result['method']}:")
                print(f"    MAE: {result['mae']:.2f} m³/day")
                print(f"    RMSE: {result['rmse']:.2f} m³/day")
                print(f"    MAPE: {result['mape']:.2f}%")
            
            # LSTM改进
            lstm_improvement = (ma_result['mape'] - lstm_result['mape']) / ma_result['mape'] * 100
            print(f"\n  LSTM相比移动平均改进: {lstm_improvement:.1f}%")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = WaterDemandForecastSystem()
    system.run()


if __name__ == "__main__":
    main()
