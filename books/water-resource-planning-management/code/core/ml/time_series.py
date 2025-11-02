"""
时间序列预测模块

提供LSTM等深度学习时间序列预测方法（简化实现）
"""

import numpy as np
from typing import Tuple, Optional
from .neural_networks import NeuralNetwork


class TimeSeriesPreprocessor:
    """
    时间序列数据预处理器
    
    Examples
    --------
    >>> preprocessor = TimeSeriesPreprocessor(window_size=10)
    >>> X, y = preprocessor.create_sequences(data)
    """
    
    def __init__(self, window_size: int = 10):
        """
        Parameters
        ----------
        window_size : int
            时间窗口大小
        """
        self.window_size = window_size
        self.mean = None
        self.std = None
    
    def normalize(self, data: np.ndarray, fit: bool = True) -> np.ndarray:
        """
        标准化数据
        
        Parameters
        ----------
        data : np.ndarray
            原始数据
        fit : bool
            是否拟合参数
        
        Returns
        -------
        np.ndarray
            标准化后的数据
        """
        if fit:
            self.mean = np.mean(data)
            self.std = np.std(data)
        
        return (data - self.mean) / (self.std + 1e-8)
    
    def denormalize(self, data: np.ndarray) -> np.ndarray:
        """
        反标准化
        
        Parameters
        ----------
        data : np.ndarray
            标准化的数据
        
        Returns
        -------
        np.ndarray
            原始尺度的数据
        """
        return data * self.std + self.mean
    
    def create_sequences(
        self,
        data: np.ndarray,
        target_offset: int = 1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        创建时间序列训练数据
        
        Parameters
        ----------
        data : np.ndarray
            时间序列数据 (n_samples,)
        target_offset : int
            预测偏移量（预测未来第几步）
        
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            (X, y) 输入序列和目标值
        
        Examples
        --------
        >>> data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> X, y = preprocessor.create_sequences(data)
        >>> # X: [[1,2,3,...,10]], y: [11]
        """
        X, y = [], []
        
        for i in range(len(data) - self.window_size - target_offset + 1):
            X.append(data[i:i+self.window_size])
            y.append(data[i+self.window_size+target_offset-1])
        
        return np.array(X), np.array(y)
    
    def add_features(self, X: np.ndarray) -> np.ndarray:
        """
        添加特征（统计特征）
        
        Parameters
        ----------
        X : np.ndarray
            输入序列 (n_samples, window_size)
        
        Returns
        -------
        np.ndarray
            增强特征 (n_samples, window_size + n_features)
        """
        # 基本统计特征
        mean_vals = np.mean(X, axis=1, keepdims=True)
        std_vals = np.std(X, axis=1, keepdims=True)
        max_vals = np.max(X, axis=1, keepdims=True)
        min_vals = np.min(X, axis=1, keepdims=True)
        
        # 趋势特征（线性拟合斜率）
        trends = []
        for seq in X:
            x = np.arange(len(seq))
            slope = np.polyfit(x, seq, 1)[0]
            trends.append(slope)
        trends = np.array(trends).reshape(-1, 1)
        
        # 合并特征
        features = np.hstack([X, mean_vals, std_vals, max_vals, min_vals, trends])
        
        return features


class LSTMPredictor:
    """
    LSTM时间序列预测器（简化实现）
    
    注：这是一个简化的教学实现，使用MLP模拟LSTM的行为
    实际应用建议使用TensorFlow/PyTorch的LSTM
    
    Examples
    --------
    >>> predictor = LSTMPredictor(window_size=10, hidden_size=64)
    >>> predictor.fit(train_data)
    >>> predictions = predictor.predict(test_data)
    """
    
    def __init__(
        self,
        window_size: int = 10,
        hidden_size: int = 64,
        learning_rate: float = 0.001
    ):
        """
        Parameters
        ----------
        window_size : int
            时间窗口大小
        hidden_size : int
            隐藏层大小
        learning_rate : float
            学习率
        """
        self.window_size = window_size
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        
        self.preprocessor = TimeSeriesPreprocessor(window_size)
        self.model = None
    
    def fit(
        self,
        data: np.ndarray,
        epochs: int = 100,
        validation_split: float = 0.2,
        add_features: bool = True,
        verbose: bool = True
    ):
        """
        训练模型
        
        Parameters
        ----------
        data : np.ndarray
            训练数据 (n_samples,)
        epochs : int
            训练轮数
        validation_split : float
            验证集比例
        add_features : bool
            是否添加统计特征
        verbose : bool
            是否打印训练信息
        """
        # 标准化
        data_normalized = self.preprocessor.normalize(data, fit=True)
        
        # 创建序列
        X, y = self.preprocessor.create_sequences(data_normalized)
        
        # 添加特征
        if add_features:
            X = self.preprocessor.add_features(X)
        
        # 构建模型
        input_dim = X.shape[1]
        self.model = NeuralNetwork(
            layers=[input_dim, self.hidden_size, self.hidden_size // 2, 1],
            activation='relu',
            learning_rate=self.learning_rate
        )
        
        # 训练
        if verbose:
            print(f"训练LSTM预测器: 输入维度={input_dim}, 隐藏层={self.hidden_size}")
        
        self.model.train(
            X, y,
            epochs=epochs,
            validation_split=validation_split,
            verbose=verbose
        )
    
    def predict(
        self,
        data: np.ndarray,
        steps: int = 1,
        add_features: bool = True
    ) -> np.ndarray:
        """
        预测未来值
        
        Parameters
        ----------
        data : np.ndarray
            历史数据（至少window_size个点）
        steps : int
            预测步数
        add_features : bool
            是否添加特征
        
        Returns
        -------
        np.ndarray
            预测结果（原始尺度）
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用fit()")
        
        # 标准化
        data_normalized = self.preprocessor.normalize(data, fit=False)
        
        predictions = []
        current_data = data_normalized.copy()
        
        for _ in range(steps):
            # 准备输入
            X = current_data[-self.window_size:].reshape(1, -1)
            
            if add_features:
                X = self.preprocessor.add_features(X)
            
            # 预测
            pred_normalized = self.model.predict(X)[0, 0]
            
            # 更新数据
            current_data = np.append(current_data, pred_normalized)
            
            # 反标准化
            pred = self.preprocessor.denormalize(np.array([pred_normalized]))[0]
            predictions.append(pred)
        
        return np.array(predictions)
    
    def evaluate(self, data: np.ndarray, add_features: bool = True) -> dict:
        """
        评估模型
        
        Parameters
        ----------
        data : np.ndarray
            测试数据
        add_features : bool
            是否添加特征
        
        Returns
        -------
        dict
            评估指标
        """
        # 标准化
        data_normalized = self.preprocessor.normalize(data, fit=False)
        
        # 创建序列
        X, y_true = self.preprocessor.create_sequences(data_normalized)
        
        if add_features:
            X = self.preprocessor.add_features(X)
        
        # 预测
        y_pred = self.model.predict(X).flatten()
        
        # 反标准化
        y_true_orig = self.preprocessor.denormalize(y_true)
        y_pred_orig = self.preprocessor.denormalize(y_pred)
        
        # 计算指标
        mse = np.mean((y_true_orig - y_pred_orig) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_true_orig - y_pred_orig))
        mape = np.mean(np.abs((y_true_orig - y_pred_orig) / (y_true_orig + 1e-8))) * 100
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }
