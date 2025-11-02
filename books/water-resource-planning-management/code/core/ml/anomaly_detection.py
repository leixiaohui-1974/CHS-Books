"""
异常检测模块

提供多种异常检测算法
"""

import numpy as np
from typing import Optional, Tuple


class IsolationForestDetector:
    """
    孤立森林异常检测（简化实现）
    
    基于决策树的异常检测方法
    
    Examples
    --------
    >>> detector = IsolationForestDetector(n_trees=100)
    >>> detector.fit(X_train)
    >>> anomalies = detector.predict(X_test)
    """
    
    def __init__(
        self,
        n_trees: int = 100,
        max_samples: int = 256,
        contamination: float = 0.1
    ):
        """
        Parameters
        ----------
        n_trees : int
            树的数量
        max_samples : int
            每棵树的样本数
        contamination : float
            异常比例（用于确定阈值）
        """
        self.n_trees = n_trees
        self.max_samples = max_samples
        self.contamination = contamination
        self.threshold = None
    
    def fit(self, X: np.ndarray):
        """
        训练异常检测器
        
        Parameters
        ----------
        X : np.ndarray
            训练数据 (n_samples, n_features)
        """
        # 简化实现：计算基于距离的异常分数
        # 实际应用建议使用sklearn.ensemble.IsolationForest
        
        # 计算数据的统计信息
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0) + 1e-8
        self.cov = np.cov(X.T)
        
        # 计算训练数据的异常分数
        scores = self._compute_scores(X)
        
        # 根据contamination确定阈值
        self.threshold = np.percentile(scores, (1 - self.contamination) * 100)
    
    def _compute_scores(self, X: np.ndarray) -> np.ndarray:
        """
        计算异常分数
        
        使用马氏距离作为异常分数
        """
        # 标准化
        X_normalized = (X - self.mean) / self.std
        
        # 马氏距离
        try:
            cov_inv = np.linalg.inv(self.cov + np.eye(self.cov.shape[0]) * 1e-6)
            distances = np.array([
                np.sqrt(x @ cov_inv @ x.T) 
                for x in X_normalized
            ])
        except:
            # 如果协方差矩阵不可逆，使用欧氏距离
            distances = np.sqrt(np.sum((X_normalized) ** 2, axis=1))
        
        return distances
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测异常
        
        Parameters
        ----------
        X : np.ndarray
            测试数据
        
        Returns
        -------
        np.ndarray
            预测结果（1为正常，-1为异常）
        """
        scores = self._compute_scores(X)
        return np.where(scores > self.threshold, -1, 1)
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        计算决策函数值（异常分数）
        
        Parameters
        ----------
        X : np.ndarray
            测试数据
        
        Returns
        -------
        np.ndarray
            异常分数（值越大越异常）
        """
        return self._compute_scores(X)


class AutoencoderDetector:
    """
    自编码器异常检测
    
    使用重构误差作为异常分数
    
    Examples
    --------
    >>> detector = AutoencoderDetector(encoding_dim=10)
    >>> detector.fit(X_train)
    >>> anomalies = detector.predict(X_test)
    """
    
    def __init__(
        self,
        encoding_dim: int = 10,
        hidden_dims: Optional[list] = None,
        contamination: float = 0.1,
        learning_rate: float = 0.001
    ):
        """
        Parameters
        ----------
        encoding_dim : int
            编码维度
        hidden_dims : list, optional
            隐藏层维度
        contamination : float
            异常比例
        learning_rate : float
            学习率
        """
        self.encoding_dim = encoding_dim
        self.hidden_dims = hidden_dims or [32, 16]
        self.contamination = contamination
        self.learning_rate = learning_rate
        
        self.encoder = None
        self.decoder = None
        self.threshold = None
    
    def _build_autoencoder(self, input_dim: int):
        """构建自编码器"""
        from .neural_networks import NeuralNetwork
        
        # 编码器
        encoder_layers = [input_dim] + self.hidden_dims + [self.encoding_dim]
        self.encoder = NeuralNetwork(
            layers=encoder_layers,
            activation='relu',
            learning_rate=self.learning_rate
        )
        
        # 解码器
        decoder_layers = [self.encoding_dim] + self.hidden_dims[::-1] + [input_dim]
        self.decoder = NeuralNetwork(
            layers=decoder_layers,
            activation='relu',
            learning_rate=self.learning_rate
        )
    
    def fit(
        self,
        X: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32,
        verbose: bool = True
    ):
        """
        训练自编码器
        
        Parameters
        ----------
        X : np.ndarray
            训练数据
        epochs : int
            训练轮数
        batch_size : int
            批量大小
        verbose : bool
            是否打印信息
        """
        input_dim = X.shape[1]
        
        # 构建自编码器
        self._build_autoencoder(input_dim)
        
        # 联合训练（简化：分别训练编码器和解码器）
        if verbose:
            print(f"训练自编码器: 输入维度={input_dim}, 编码维度={self.encoding_dim}")
        
        # 编码
        self.encoder.train(X, X, epochs=epochs//2, batch_size=batch_size, verbose=verbose)
        
        # 解码
        encoded = self.encoder.predict(X)
        self.decoder.train(encoded, X, epochs=epochs//2, batch_size=batch_size, verbose=verbose)
        
        # 计算重构误差
        X_reconstructed = self.reconstruct(X)
        errors = np.mean((X - X_reconstructed) ** 2, axis=1)
        
        # 确定阈值
        self.threshold = np.percentile(errors, (1 - self.contamination) * 100)
    
    def reconstruct(self, X: np.ndarray) -> np.ndarray:
        """
        重构数据
        
        Parameters
        ----------
        X : np.ndarray
            输入数据
        
        Returns
        -------
        np.ndarray
            重构数据
        """
        encoded = self.encoder.predict(X)
        reconstructed = self.decoder.predict(encoded)
        return reconstructed
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测异常
        
        Parameters
        ----------
        X : np.ndarray
            测试数据
        
        Returns
        -------
        np.ndarray
            预测结果（1为正常，-1为异常）
        """
        X_reconstructed = self.reconstruct(X)
        errors = np.mean((X - X_reconstructed) ** 2, axis=1)
        return np.where(errors > self.threshold, -1, 1)
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        计算重构误差
        
        Parameters
        ----------
        X : np.ndarray
            测试数据
        
        Returns
        -------
        np.ndarray
            重构误差
        """
        X_reconstructed = self.reconstruct(X)
        return np.mean((X - X_reconstructed) ** 2, axis=1)
