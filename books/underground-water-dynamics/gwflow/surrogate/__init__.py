"""
代理模型模块 (Surrogate Model Module)

提供神经网络代理模型和采样方法，用于快速近似数值模拟。

主要组件:
---------
- NeuralNetworkSurrogate: 神经网络代理模型
- latin_hypercube_sampling: 拉丁超立方采样
- sobol_sampling: Sobol序列采样
- random_sampling: 随机采样

Examples
--------
>>> from gwflow.surrogate import NeuralNetworkSurrogate, latin_hypercube_sampling
>>> # 生成训练数据
>>> X = latin_hypercube_sampling(100, 3, [(0,1), (0,10), (5,15)])
>>> y = expensive_simulation(X)
>>> # 训练代理模型
>>> nn = NeuralNetworkSurrogate(hidden_layers=(50, 30))
>>> nn.train(X, y)
>>> # 快速预测
>>> y_pred = nn.predict(X_new)
"""

from .neural_network import (
    NeuralNetworkSurrogate,
    compare_predictions
)

from .sampling import (
    latin_hypercube_sampling,
    sobol_sampling,
    random_sampling,
    plot_sampling_comparison,
    compute_discrepancy
)

__all__ = [
    # Neural Network
    'NeuralNetworkSurrogate',
    'compare_predictions',
    
    # Sampling
    'latin_hypercube_sampling',
    'sobol_sampling',
    'random_sampling',
    'plot_sampling_comparison',
    'compute_discrepancy',
]
