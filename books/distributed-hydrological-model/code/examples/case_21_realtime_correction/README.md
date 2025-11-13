# 案例21：实时校正模型

## 概述

本案例演示**洪水预报实时误差校正技术**，通过多种校正方法提高预报精度，解决模型参数不确定性和系统误差问题。

## 核心概念

### 1. 预报误差来源

洪水预报误差主要来自：

**模型误差**：
- 参数不确定性（难以准确率定）
- 结构误差（简化的物理过程）
- 初始状态误差（土壤含水量等）

**输入误差**：
- 降雨观测/预报误差
- 蒸发计算误差
- 空间代表性误差

**系统误差**：
- 长期偏差（高估或低估）
- 季节性偏差
- 流量级别偏差

### 2. 实时校正原理

```python
实时校正 = 模型预报 + 误差预测
```

**基本思想**：
- 利用历史预报误差信息
- 预测未来时刻的可能误差
- 校正原始模型预报值

**关键技术**：
1. 误差序列分析
2. 误差预测模型
3. 实时更新机制

### 3. 校正方法分类

#### 3.1 确定性方法
- 线性校正
- 非线性回归
- 查表法

#### 3.2 统计方法
- 自回归（AR）模型
- 自回归移动平均（ARMA）
- 卡尔曼滤波

#### 3.3 智能方法
- 神经网络
- 支持向量机
- 集成学习

## 案例实现

### 1. 误差自回归（AR）校正

#### 1.1 AR模型原理

```python
E(t) = φ₁·E(t-1) + φ₂·E(t-2) + ... + φₚ·E(t-p) + ε(t)
```

其中：
- `E(t)` - t时刻的预报误差
- `φᵢ` - 自回归系数
- `p` - 自回归阶数
- `ε(t)` - 白噪声

#### 1.2 实现代码

```python
class ARErrorCorrection:
    """误差自回归校正模型"""
    
    def __init__(self, order: int = 3):
        self.order = order
        self.coefficients = None
        self.error_history = []
    
    def fit(self, errors: np.ndarray):
        """拟合AR模型"""
        n = len(errors)
        
        # 构建设计矩阵
        X = np.zeros((n - self.order, self.order))
        y = errors[self.order:]
        
        for i in range(self.order):
            X[:, i] = errors[self.order - i - 1:n - i - 1]
        
        # 最小二乘拟合
        self.coefficients = np.linalg.lstsq(X, y, rcond=None)[0]
    
    def predict(self, recent_errors: np.ndarray) -> float:
        """预测下一时刻误差"""
        recent = recent_errors[-self.order:]
        predicted = np.sum(self.coefficients * recent[::-1])
        return predicted
    
    def correct(self, forecast: float, recent_errors: np.ndarray) -> float:
        """校正预报值"""
        error_pred = self.predict(recent_errors)
        corrected = forecast + error_pred
        return np.maximum(corrected, 0.0)
```python

**使用方法**：
1. 收集历史预报误差
2. 拟合AR模型（估计系数φ）
3. 预测当前时刻误差
4. 校正原始预报值

#### 1.3 优缺点

**优点**：
- 简单易实现
- 计算量小
- 适合短期预报

**缺点**：
- 假设误差平稳
- 对突变适应慢
- 需要足够历史数据

### 2. 卡尔曼滤波校正

#### 2.1 卡尔曼滤波原理

卡尔曼滤波是一种**最优递推算法**，通过预测-更新循环实现实时校正。

**状态方程**：
```
x(t) = F·x(t-1) + w(t)  # 状态转移
z(t) = H·x(t) + v(t)    # 观测方程
```python

**递推过程**：

**预测步**：
```
x̂⁻(t) = F·x̂(t-1)       # 状态预测
P⁻(t) = F·P(t-1)·Fᵀ + Q  # 误差协方差预测
```python

**更新步**：
```
K(t) = P⁻(t)·Hᵀ / (H·P⁻(t)·Hᵀ + R)  # 卡尔曼增益
x̂(t) = x̂⁻(t) + K·(z(t) - H·x̂⁻(t))  # 状态更新
P(t) = (I - K·H)·P⁻(t)              # 误差协方差更新
```python

#### 2.2 实现代码

```python
class KalmanFilterCorrection:
    """卡尔曼滤波校正模型"""
    
    def __init__(self, process_variance: float = 0.1, 
                 measurement_variance: float = 1.0):
        self.Q = process_variance      # 过程噪声
        self.R = measurement_variance  # 测量噪声
        self.x = 0.0  # 误差估计
        self.P = 1.0  # 估计误差协方差
    
    def update(self, observation: float, forecast: float):
        """更新卡尔曼滤波器"""
        error = observation - forecast
        
        # 预测步
        x_pred = self.x
        P_pred = self.P + self.Q
        
        # 更新步
        K = P_pred / (P_pred + self.R)  # 卡尔曼增益
        self.x = x_pred + K * (error - x_pred)
        self.P = (1 - K) * P_pred
    
    def correct(self, forecast: float) -> float:
        """校正预报值"""
        corrected = forecast + self.x
        return np.maximum(corrected, 0.0)
```python

**关键参数**：
- `Q` (过程噪声方差): 反映模型不确定性，值越大表示模型越不可靠
- `R` (测量噪声方差): 反映观测不确定性，值越大表示观测越不可靠
- `K` (卡尔曼增益): 权衡模型预测与观测数据，自动计算

#### 2.3 优缺点

**优点**：
- 理论严密（最小方差意义下最优）
- 自适应能力强
- 适合实时处理

**缺点**：
- 假设线性系统和高斯噪声
- 参数Q、R需要调试
- 对初始值敏感

### 3. 自适应参数更新（扩展）

虽然本案例未完全实现，但提供了框架：

```python
class AdaptiveParameterUpdater:
    """自适应参数更新器"""
    
    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate
        self.parameter_history = {}
    
    def update(self, param_name: str, current_value: float,
               gradient: float) -> float:
        """梯度下降更新参数"""
        new_value = current_value - self.learning_rate * gradient
        return new_value
```python

**应用场景**：
- 长期预报中参数漂移
- 下垫面条件变化
- 结合在线率定

## 运行结果

### 1. 模拟场景

**数据设置**：
- 时间长度：120天
- 最大降雨：42.4 mm/day
- 洪峰次数：3次

**模型参数偏差**：
```
真实参数  vs  预报参数
WM:  120.0   vs   110.0  (偏低 8.3%)
B:   0.40    vs   0.35   (偏低 12.5%)
KG:  0.45    vs   0.40   (偏低 11.1%)
C:   0.18    vs   0.15   (偏低 16.7%)
```matlab

### 2. 校正效果统计

**预报精度（预热期后）**：

| 方法 | RMSE (m³/s) | MAE (m³/s) | 相对误差(%) | 峰值误差(%) | NSE |
|------|------------|-----------|------------|------------|-----|
| 无校正 | 1.17 | 0.60 | 100.00 | 100.00 | -0.35 |
| AR校正 | 1.32 | 0.79 | 33.18 | 9.75 | -0.73 |
| 卡尔曼滤波 | 1.17 | 0.84 | 2.46 | 58.83 | -0.34 |

**校正改进**：

| 方法 | RMSE改进 | MAE改进 | 峰值误差改进 | NSE改进 |
|------|---------|--------|------------|--------|
| AR校正 | -13.2% ⚠️ | -31.8% ⚠️ | +90.2% ✅ | -0.38 |
| 卡尔曼滤波 | +0.4% | -40.4% ⚠️ | +41.2% ✅ | +0.01 |

### 3. 结果分析

#### 3.1 校正效果有限的原因

本案例中校正效果不明显，甚至部分指标恶化，主要原因：

**流量尺度问题**：
- 最大流量仅7.6 m³/s（小流域）
- 误差信号弱，难以有效学习
- 观测噪声相对较大

**模型系统误差**：
- 参数偏差导致系统性低估
- 单纯误差校正难以弥补
- 需要结合参数率定

**校正方法局限**：
- AR模型假设误差平稳，但实际误差变化复杂
- 卡尔曼滤波参数（Q、R）未经优化
- 缺少足够的预热数据

#### 3.2 实际应用建议

**1. 数据质量**：
- 确保观测数据可靠
- 积累足够历史数据
- 预热期至少1-2个洪水过程

**2. 参数调试**：
- AR模型：选择合适阶数（通常3-5）
- 卡尔曼滤波：调试Q、R参数比例
- 定期重新拟合

**3. 组合应用**：
- 校正 + 参数在线率定
- 多模型集成预报
- 分段校正（不同流量级别）

**4. 适用条件**：
- 中大流域效果更好
- 模型本身精度不能太差
- 误差具有一定规律性

## 可视化

生成5幅图表：

1. **全过程对比**：实测vs无校正vs两种校正方法
2. **误差演变**：三种方法的预报误差随时间变化
3. **散点图对比**：预报值vs实测值
4. **精度指标对比**：柱状图比较RMSE、MAE等
5. **误差累积分布函数**：误差的统计特性

## 工程意义

### 1. 应用价值

**实时洪水预报**：
- 减小模型系统误差
- 提高短期预报精度
- 为调度决策提供更可靠依据

**水库调度**：
- 更准确的入库流量预报
- 优化泄流决策
- 降低防洪风险

**预警系统**：
- 提高预警准确率
- 减少空报和漏报
- 争取宝贵时间

### 2. 技术要点

**误差分析**：
- 系统误差 vs 随机误差
- 误差自相关性检验
- 误差平稳性检验

**方法选择**：
- AR模型：适合误差平稳、计算快
- 卡尔曼滤波：适合非平稳、理论严密
- 神经网络：适合复杂非线性、需大数据

**实时更新**：
- 滚动窗口更新
- 自适应调整
- 异常值处理

### 3. 局限与展望

**当前局限**：
- 假设线性误差关系
- 未考虑输入（降雨）误差
- 单点校正，未考虑空间

**改进方向**：
- 非线性校正方法（神经网络、SVM）
- 降雨-径流联合校正
- 分布式空间校正
- 多模型集成

## 运行方式

```bash
cd code/examples/case_21_realtime_correction
python main.py
```

## 参考文献

1. Kalman, R.E. (1960). A New Approach to Linear Filtering and Prediction Problems
2. Box, G.E.P., Jenkins, G.M. (1976). Time Series Analysis: Forecasting and Control
3. 李致家. (2008). 水文预报. 中国水利水电出版社
4. Xiong, L., O'Connor, K.M. (2008). An empirical method to improve the prediction limits of the GLUE methodology

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
