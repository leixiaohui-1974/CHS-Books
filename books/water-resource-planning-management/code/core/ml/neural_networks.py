"""
神经网络基础模块

提供通用的神经网络构建和训练工具
"""

import numpy as np
from typing import List, Optional, Tuple, Callable


class NeuralNetwork:
    """
    简单的多层感知器（MLP）
    
    用于教学目的的简化实现，实际应用建议使用TensorFlow/PyTorch
    
    Examples
    --------
    >>> nn = NeuralNetwork(layers=[10, 20, 10, 1])
    >>> nn.train(X_train, y_train, epochs=100)
    >>> y_pred = nn.predict(X_test)
    """
    
    def __init__(
        self,
        layers: List[int],
        activation: str = 'relu',
        learning_rate: float = 0.01
    ):
        """
        初始化神经网络
        
        Parameters
        ----------
        layers : List[int]
            各层神经元数量，包括输入层、隐藏层和输出层
        activation : str
            激活函数：'relu', 'sigmoid', 'tanh'
        learning_rate : float
            学习率
        """
        self.layers = layers
        self.learning_rate = learning_rate
        self.activation_name = activation
        
        # 初始化权重和偏置
        self.weights = []
        self.biases = []
        
        for i in range(len(layers) - 1):
            # Xavier初始化
            w = np.random.randn(layers[i], layers[i+1]) * np.sqrt(2.0 / layers[i])
            b = np.zeros((1, layers[i+1]))
            self.weights.append(w)
            self.biases.append(b)
        
        # 历史记录
        self.loss_history = []
    
    def _activation(self, x: np.ndarray) -> np.ndarray:
        """激活函数"""
        if self.activation_name == 'relu':
            return np.maximum(0, x)
        elif self.activation_name == 'sigmoid':
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        elif self.activation_name == 'tanh':
            return np.tanh(x)
        else:
            return x
    
    def _activation_derivative(self, x: np.ndarray) -> np.ndarray:
        """激活函数导数"""
        if self.activation_name == 'relu':
            return (x > 0).astype(float)
        elif self.activation_name == 'sigmoid':
            s = self._activation(x)
            return s * (1 - s)
        elif self.activation_name == 'tanh':
            return 1 - np.tanh(x) ** 2
        else:
            return np.ones_like(x)
    
    def forward(self, X: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        前向传播
        
        Parameters
        ----------
        X : np.ndarray
            输入数据 (n_samples, n_features)
        
        Returns
        -------
        Tuple[List[np.ndarray], List[np.ndarray]]
            (激活值列表, 线性输出列表)
        """
        activations = [X]
        linear_outputs = []
        
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            z = activations[-1] @ w + b
            linear_outputs.append(z)
            
            # 最后一层不使用激活函数（回归问题）
            if i == len(self.weights) - 1:
                a = z
            else:
                a = self._activation(z)
            
            activations.append(a)
        
        return activations, linear_outputs
    
    def backward(
        self,
        X: np.ndarray,
        y: np.ndarray,
        activations: List[np.ndarray],
        linear_outputs: List[np.ndarray]
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        反向传播
        
        Parameters
        ----------
        X : np.ndarray
            输入数据
        y : np.ndarray
            真实标签
        activations : List[np.ndarray]
            前向传播的激活值
        linear_outputs : List[np.ndarray]
            前向传播的线性输出
        
        Returns
        -------
        Tuple[List[np.ndarray], List[np.ndarray]]
            (权重梯度, 偏置梯度)
        """
        m = X.shape[0]
        n_layers = len(self.weights)
        
        # 初始化梯度
        dW = [np.zeros_like(w) for w in self.weights]
        db = [np.zeros_like(b) for b in self.biases]
        
        # 输出层误差
        delta = activations[-1] - y
        
        # 反向传播
        for i in range(n_layers - 1, -1, -1):
            dW[i] = activations[i].T @ delta / m
            db[i] = np.sum(delta, axis=0, keepdims=True) / m
            
            if i > 0:
                # 传播到前一层
                delta = (delta @ self.weights[i].T) * self._activation_derivative(linear_outputs[i-1])
        
        return dW, db
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        batch_size: Optional[int] = None,
        validation_split: float = 0.0,
        verbose: bool = True
    ):
        """
        训练神经网络
        
        Parameters
        ----------
        X : np.ndarray
            训练数据 (n_samples, n_features)
        y : np.ndarray
            标签 (n_samples, n_outputs)
        epochs : int
            训练轮数
        batch_size : int, optional
            批量大小，None表示使用全部数据
        validation_split : float
            验证集比例
        verbose : bool
            是否打印训练信息
        """
        # 数据归一化
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        
        # 划分训练集和验证集
        if validation_split > 0:
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
        else:
            X_train, y_train = X, y
            X_val, y_val = None, None
        
        n_samples = len(X_train)
        if batch_size is None:
            batch_size = n_samples
        
        for epoch in range(epochs):
            # 随机打乱数据
            indices = np.random.permutation(n_samples)
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]
            
            # 小批量训练
            epoch_loss = 0.0
            for i in range(0, n_samples, batch_size):
                X_batch = X_shuffled[i:i+batch_size]
                y_batch = y_shuffled[i:i+batch_size]
                
                # 前向传播
                activations, linear_outputs = self.forward(X_batch)
                
                # 计算损失
                loss = np.mean((activations[-1] - y_batch) ** 2)
                epoch_loss += loss
                
                # 反向传播
                dW, db = self.backward(X_batch, y_batch, activations, linear_outputs)
                
                # 更新参数
                for j in range(len(self.weights)):
                    self.weights[j] -= self.learning_rate * dW[j]
                    self.biases[j] -= self.learning_rate * db[j]
            
            avg_loss = epoch_loss / (n_samples / batch_size)
            self.loss_history.append(avg_loss)
            
            # 打印信息
            if verbose and (epoch + 1) % 10 == 0:
                info = f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}"
                
                if X_val is not None:
                    val_pred = self.predict(X_val)
                    val_loss = np.mean((val_pred - y_val) ** 2)
                    info += f", Val Loss: {val_loss:.6f}"
                
                print(info)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测
        
        Parameters
        ----------
        X : np.ndarray
            输入数据
        
        Returns
        -------
        np.ndarray
            预测结果
        """
        activations, _ = self.forward(X)
        return activations[-1]


def build_mlp(
    input_dim: int,
    hidden_dims: List[int],
    output_dim: int,
    activation: str = 'relu'
) -> NeuralNetwork:
    """
    构建多层感知器
    
    Parameters
    ----------
    input_dim : int
        输入维度
    hidden_dims : List[int]
        隐藏层维度列表
    output_dim : int
        输出维度
    activation : str
        激活函数
    
    Returns
    -------
    NeuralNetwork
        神经网络实例
    
    Examples
    --------
    >>> nn = build_mlp(input_dim=10, hidden_dims=[64, 32], output_dim=1)
    """
    layers = [input_dim] + hidden_dims + [output_dim]
    return NeuralNetwork(layers=layers, activation=activation)
