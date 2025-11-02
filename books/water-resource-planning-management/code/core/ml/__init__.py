"""
机器学习模块

提供水资源领域的机器学习算法：
- 时间序列预测（LSTM、GRU）
- 异常检测（Isolation Forest、Autoencoder）
- 强化学习（DQN、PPO）
- 神经网络工具
"""

from .neural_networks import NeuralNetwork, build_mlp
from .time_series import LSTMPredictor, TimeSeriesPreprocessor
from .anomaly_detection import IsolationForestDetector, AutoencoderDetector

__all__ = [
    "NeuralNetwork",
    "build_mlp",
    "LSTMPredictor",
    "TimeSeriesPreprocessor",
    "IsolationForestDetector",
    "AutoencoderDetector",
]
