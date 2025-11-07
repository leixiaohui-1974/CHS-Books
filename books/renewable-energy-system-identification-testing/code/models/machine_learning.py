"""
机器学习模块

包含:
1. 时间序列预测（ARIMA）
2. 随机森林
3. 神经网络（MLP/LSTM）
4. 支持向量机（SVM）
5. 故障分类

作者: CHS Books
"""

import numpy as np
from typing import Dict, List
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


class ARIMAModel:
    """
    ARIMA时间序列模型
    
    AR(p) + I(d) + MA(q)
    """
    
    def __init__(self, p: int = 1, d: int = 0, q: int = 1, name: str = "ARIMA"):
        """
        初始化ARIMA模型
        
        Args:
            p: 自回归阶数
            d: 差分阶数
            q: 移动平均阶数
        """
        self.name = name
        self.p = p
        self.d = d
        self.q = q
        self.phi = None  # AR系数
        self.theta = None  # MA系数
    
    def difference(self, data: np.ndarray, d: int) -> np.ndarray:
        """差分操作"""
        diff_data = data.copy()
        for _ in range(d):
            diff_data = np.diff(diff_data)
        return diff_data
    
    def fit(self, data: np.ndarray):
        """
        拟合ARIMA模型（简化实现）
        
        Args:
            data: 时间序列数据
        """
        # 差分
        if self.d > 0:
            data_diff = self.difference(data, self.d)
        else:
            data_diff = data
        
        # 简化：使用LS估计AR参数
        n = len(data_diff)
        X = np.zeros((n - self.p, self.p))
        y = data_diff[self.p:]
        
        for i in range(self.p):
            X[:, i] = data_diff[self.p-1-i:n-1-i]
        
        self.phi = np.linalg.lstsq(X, y, rcond=None)[0]
        
        # 简化：MA部分设为0
        self.theta = np.zeros(self.q)
    
    def predict(self, data: np.ndarray, steps: int) -> np.ndarray:
        """
        预测未来值
        
        Args:
            data: 历史数据
            steps: 预测步数
            
        Returns:
            预测值
        """
        predictions = []
        history = list(data[-self.p:])
        
        for _ in range(steps):
            pred = np.sum(self.phi * np.array(history[-self.p:][::-1]))
            predictions.append(pred)
            history.append(pred)
        
        return np.array(predictions)


class PowerPredictionRF:
    """
    基于随机森林的功率预测
    
    适用于风电/光伏功率预测
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 20,
        name: str = "RandomForest_Power"
    ):
        """
        初始化随机森林模型
        
        Args:
            n_estimators: 树的数量
            max_depth: 最大深度
        """
        self.name = name
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        )
        self.scaler = StandardScaler()
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        训练模型
        
        Args:
            X: 特征矩阵 [n_samples, n_features]
               例如：[辐照度, 温度, 风速, 历史功率, ...]
            y: 目标功率 [n_samples]
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测功率"""
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def feature_importance(self) -> np.ndarray:
        """特征重要性"""
        return self.model.feature_importances_


class SimpleNeuralNetwork:
    """
    简单神经网络（MLP）
    
    用于功率预测或故障分类
    """
    
    def __init__(
        self,
        hidden_layers: tuple = (100, 50),
        activation: str = 'relu',
        max_iter: int = 500,
        name: str = "MLP"
    ):
        """
        初始化神经网络
        
        Args:
            hidden_layers: 隐藏层神经元数量
            activation: 激活函数
            max_iter: 最大迭代次数
        """
        self.name = name
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layers,
            activation=activation,
            max_iter=max_iter,
            random_state=42
        )
        self.scaler = StandardScaler()
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """训练模型"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


class FaultClassifier:
    """
    故障分类器
    
    基于SVM或随机森林
    """
    
    def __init__(
        self,
        method: str = 'rf',  # 'rf' or 'svm'
        n_classes: int = 4,
        name: str = "FaultClassifier"
    ):
        """
        初始化故障分类器
        
        Args:
            method: 'rf'随机森林 或 'svm'支持向量机
            n_classes: 故障类别数
        """
        self.name = name
        self.method = method
        self.n_classes = n_classes
        
        if method == 'rf':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif method == 'svm':
            self.model = SVC(kernel='rbf', probability=True)
        else:
            raise ValueError("method must be 'rf' or 'svm'")
        
        self.scaler = StandardScaler()
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        训练分类器
        
        Args:
            X: 特征矩阵（如FFT谱、统计特征等）
            y: 故障标签 (0=正常, 1=故障类型1, ...)
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测故障类别"""
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """预测概率"""
        X_scaled = self.scaler.transform(X)
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        else:
            return None


class SequencePredictor:
    """
    序列预测器（模拟LSTM功能）
    
    简化实现
    """
    
    def __init__(
        self,
        sequence_length: int = 24,
        n_features: int = 1,
        name: str = "SequencePredictor"
    ):
        """
        初始化序列预测器
        
        Args:
            sequence_length: 输入序列长度
            n_features: 特征数量
        """
        self.name = name
        self.sequence_length = sequence_length
        self.n_features = n_features
        
        # 使用MLP模拟LSTM
        self.model = MLPRegressor(
            hidden_layer_sizes=(128, 64),
            max_iter=300,
            random_state=42
        )
        self.scaler = StandardScaler()
    
    def prepare_sequences(
        self,
        data: np.ndarray
    ) -> tuple:
        """
        准备训练序列
        
        Args:
            data: 时间序列数据 [n_timesteps, n_features]
            
        Returns:
            X, y用于训练
        """
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i+self.sequence_length].flatten())
            y.append(data[i+self.sequence_length])
        return np.array(X), np.array(y)
    
    def fit(self, data: np.ndarray):
        """训练模型"""
        X, y = self.prepare_sequences(data)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def predict(self, sequence: np.ndarray) -> np.ndarray:
        """
        预测下一个值
        
        Args:
            sequence: 输入序列 [sequence_length, n_features]
            
        Returns:
            预测值
        """
        X = sequence.flatten().reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)[0]


class EnsemblePrediction:
    """
    集成预测
    
    组合多个模型
    """
    
    def __init__(self, models: List, weights: List[float] = None):
        """
        初始化集成模型
        
        Args:
            models: 模型列表
            weights: 权重列表
        """
        self.models = models
        if weights is None:
            self.weights = [1.0 / len(models)] * len(models)
        else:
            self.weights = weights
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """集成预测"""
        predictions = []
        for model in self.models:
            predictions.append(model.predict(X))
        
        # 加权平均
        ensemble_pred = np.zeros_like(predictions[0])
        for pred, weight in zip(predictions, self.weights):
            ensemble_pred += weight * pred
        
        return ensemble_pred
