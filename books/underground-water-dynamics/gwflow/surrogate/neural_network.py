"""
神经网络代理模型模块

使用神经网络构建快速代理模型，替代耗时的数值模拟。

代理模型（Surrogate Model）概念:
-------------------------------
在优化、不确定性分析等需要大量模型评估的场景中，数值模拟可能
非常耗时。代理模型是一个快速的近似模型，能够：
- 以毫秒级速度预测（相比数值模拟的分钟级）
- 保持足够的精度
- 支持大规模优化和采样

常用代理模型:
- 多项式响应面 (Polynomial Response Surface)
- 径向基函数 (Radial Basis Function)
- 克里金 (Kriging / Gaussian Process)
- 神经网络 (Neural Network)

本模块实现神经网络代理模型，使用scikit-learn的MLPRegressor。
"""

import numpy as np
from typing import Tuple, Optional, Dict
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


class NeuralNetworkSurrogate:
    """
    神经网络代理模型
    
    使用多层感知器（MLP）构建输入-输出映射。
    
    Parameters
    ----------
    hidden_layers : tuple
        隐藏层结构，如(50, 30)表示两个隐藏层
    activation : str
        激活函数，'relu', 'tanh', 'logistic'
    max_iter : int
        最大迭代次数
    random_state : int
        随机种子
    
    Attributes
    ----------
    model : MLPRegressor
        sklearn神经网络模型
    scaler_X : StandardScaler
        输入标准化器
    scaler_y : StandardScaler
        输出标准化器
    is_trained : bool
        是否已训练
    
    Examples
    --------
    >>> nn = NeuralNetworkSurrogate(hidden_layers=(50, 30, 20))
    >>> nn.train(X_train, y_train)
    >>> y_pred = nn.predict(X_test)
    >>> metrics = nn.evaluate(X_test, y_test)
    >>> print(f"R² = {metrics['r2']:.4f}")
    """
    
    def __init__(
        self,
        hidden_layers: tuple = (100, 50, 30),
        activation: str = 'relu',
        max_iter: int = 500,
        random_state: int = 42
    ):
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.max_iter = max_iter
        self.random_state = random_state
        
        # 创建模型
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layers,
            activation=activation,
            max_iter=max_iter,
            random_state=random_state,
            early_stopping=True,
            validation_fraction=0.1,
            alpha=0.001,  # L2正则化
            verbose=False
        )
        
        # 标准化器
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
        self.is_trained = False
        self.training_history = {}
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        verbose: bool = True
    ) -> Dict:
        """
        训练神经网络
        
        Parameters
        ----------
        X_train : np.ndarray
            训练输入 (n_samples × n_features)
        y_train : np.ndarray
            训练输出 (n_samples × n_outputs)
        verbose : bool
            是否打印训练信息
        
        Returns
        -------
        history : Dict
            训练历史
        """
        if verbose:
            print(f"\n训练神经网络代理模型...")
            print(f"  输入维度: {X_train.shape[1]}")
            print(f"  输出维度: {y_train.shape[1] if y_train.ndim > 1 else 1}")
            print(f"  训练样本: {X_train.shape[0]}")
            print(f"  网络结构: {self.hidden_layers}")
        
        # 标准化
        X_scaled = self.scaler_X.fit_transform(X_train)
        y_scaled = self.scaler_y.fit_transform(
            y_train.reshape(-1, 1) if y_train.ndim == 1 else y_train
        )
        
        # 训练
        self.model.fit(X_scaled, y_scaled.ravel() if y_train.ndim == 1 else y_scaled)
        
        self.is_trained = True
        
        # 记录训练历史
        self.training_history = {
            'n_samples': X_train.shape[0],
            'n_features': X_train.shape[1],
            'n_iter': self.model.n_iter_,
            'loss': self.model.loss_
        }
        
        if verbose:
            print(f"  训练完成！")
            print(f"  迭代次数: {self.model.n_iter_}")
            print(f"  最终损失: {self.model.loss_:.6f}")
        
        return self.training_history
    
    def predict(
        self,
        X: np.ndarray
    ) -> np.ndarray:
        """
        预测输出
        
        Parameters
        ----------
        X : np.ndarray
            输入 (n_samples × n_features)
        
        Returns
        -------
        y_pred : np.ndarray
            预测输出 (n_samples × n_outputs)
        """
        if not self.is_trained:
            raise RuntimeError("模型未训练！请先调用train()方法。")
        
        X_scaled = self.scaler_X.transform(X)
        y_pred_scaled = self.model.predict(X_scaled)
        y_pred = self.scaler_y.inverse_transform(
            y_pred_scaled.reshape(-1, 1) if y_pred_scaled.ndim == 1 
            else y_pred_scaled
        )
        
        return y_pred.ravel() if y_pred_scaled.ndim == 1 else y_pred
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        评估模型性能
        
        Parameters
        ----------
        X_test : np.ndarray
            测试输入
        y_test : np.ndarray
            测试输出（真实值）
        
        Returns
        -------
        metrics : Dict
            评估指标
            - r2: 决定系数
            - rmse: 均方根误差
            - mae: 平均绝对误差
            - max_error: 最大误差
        """
        y_pred = self.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        max_error = np.max(np.abs(y_test - y_pred))
        
        metrics = {
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'max_error': max_error,
            'n_test': len(y_test)
        }
        
        return metrics
    
    def summary(self) -> str:
        """
        生成模型摘要
        
        Returns
        -------
        summary : str
            摘要文本
        """
        if not self.is_trained:
            return "模型未训练"
        
        lines = [
            "\n" + "="*60,
            "神经网络代理模型摘要",
            "="*60,
            f"网络结构: {self.hidden_layers}",
            f"激活函数: {self.activation}",
            f"训练样本: {self.training_history.get('n_samples', 'N/A')}",
            f"输入维度: {self.training_history.get('n_features', 'N/A')}",
            f"训练迭代: {self.training_history.get('n_iter', 'N/A')}",
            f"训练损失: {self.training_history.get('loss', 'N/A'):.6f}",
            "="*60
        ]
        
        return "\n".join(lines)


def compare_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model"
) -> None:
    """
    比较真实值和预测值
    
    Parameters
    ----------
    y_true : np.ndarray
        真实值
    y_pred : np.ndarray
        预测值
    model_name : str
        模型名称
    """
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 子图1：预测vs真实
    ax1 = axes[0]
    ax1.scatter(y_true, y_pred, alpha=0.6, edgecolors='k', linewidths=0.5)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='理想线')
    ax1.set_xlabel('真实值')
    ax1.set_ylabel('预测值')
    ax1.set_title(f'{model_name}: 预测 vs 真实')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # 子图2：残差
    ax2 = axes[1]
    residuals = y_pred - y_true
    ax2.scatter(y_true, residuals, alpha=0.6, edgecolors='k', linewidths=0.5)
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=2)
    ax2.set_xlabel('真实值')
    ax2.set_ylabel('残差 (预测 - 真实)')
    ax2.set_title(f'{model_name}: 残差分析')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig
