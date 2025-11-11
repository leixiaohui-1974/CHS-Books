# Python数值计算函数速查表 💻

**《水利类数学一速成手册》配套编程资料**

---

## 📚 核心库

```python
import numpy as np              # 数值计算
import scipy as sp              # 科学计算
from scipy import integrate     # 积分
from scipy import optimize      # 优化
from scipy import linalg        # 线性代数
from scipy import stats         # 统计
import sympy as sp              # 符号计算
import matplotlib.pyplot as plt # 绘图
import pandas as pd             # 数据处理
```

---

## NumPy核心函数

### 数组创建
```python
np.array([1, 2, 3])            # 创建数组
np.zeros((3, 4))               # 零数组
np.ones((2, 3))                # 全1数组
np.eye(3)                      # 单位矩阵
np.linspace(0, 10, 100)        # 等间距数组
np.arange(0, 10, 0.1)          # 范围数组
```

### 数学运算
```python
np.sin(x)                      # 三角函数
np.exp(x)                      # 指数
np.log(x)                      # 自然对数
np.sqrt(x)                     # 平方根
np.power(x, 2)                 # 幂运算
```

### 统计函数
```python
np.mean(x)                     # 均值
np.std(x)                      # 标准差
np.var(x)                      # 方差
np.max(x), np.min(x)           # 最大最小值
np.median(x)                   # 中位数
```

### 矩阵运算
```python
A @ B                          # 矩阵乘法
np.dot(A, B)                   # 点积
np.linalg.inv(A)               # 逆矩阵
np.linalg.det(A)               # 行列式
np.linalg.eig(A)               # 特征值
np.linalg.solve(A, b)          # 解方程Ax=b
np.linalg.matrix_rank(A)       # 秩
```

---

## SciPy科学计算

### 积分
```python
from scipy import integrate

# 定积分
result, error = integrate.quad(lambda x: x**2, 0, 1)

# 二重积分
result = integrate.dblquad(lambda y, x: x*y, 0, 1, 0, 1)

# 数值积分（已知离散点）
result = integrate.trapz(y, x)  # 梯形法
result = integrate.simps(y, x)  # 辛普森法
```

### 微分方程
```python
from scipy.integrate import odeint, solve_ivp

# 求解ODE：dy/dt = f(y, t)
def model(y, t):
    return -0.5 * y

y0 = 1
t = np.linspace(0, 10, 100)
y = odeint(model, y0, t)

# 高级求解器
sol = solve_ivp(model, [0, 10], [y0], dense_output=True)
```

### 优化
```python
from scipy import optimize

# 求最小值
result = optimize.minimize(lambda x: x**2, x0=1)

# 求根
root = optimize.fsolve(lambda x: x**2 - 4, x0=1)

# 曲线拟合
popt, pcov = optimize.curve_fit(lambda x, a, b: a*x + b, x_data, y_data)
```

### 统计
```python
from scipy import stats

# 正态分布
mu, sigma = 0, 1
x = stats.norm.ppf(0.95, mu, sigma)  # 95%分位数
p = stats.norm.cdf(1.96, mu, sigma)  # 累积分布函数

# t分布
t_stat, p_value = stats.ttest_1samp(data, popmean=0)

# 卡方检验
chi2_stat, p_value = stats.chisquare(observed, expected)

# 线性回归
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
```

---

## SymPy符号计算

### 基本操作
```python
import sympy as sp

x = sp.Symbol('x')
y = sp.Symbol('y')

# 展开
sp.expand((x + 1)**2)

# 因式分解
sp.factor(x**2 - 1)

# 简化
sp.simplify(sp.sin(x)**2 + sp.cos(x)**2)
```

### 微积分
```python
# 求导
dy = sp.diff(x**2, x)           # 2*x

# 积分
I = sp.integrate(x**2, x)       # x**3/3
I = sp.integrate(x**2, (x, 0, 1))  # 定积分

# 极限
L = sp.limit(sp.sin(x)/x, x, 0)  # 1

# 级数展开
series = sp.series(sp.exp(x), x, 0, n=5)
```

### 方程求解
```python
# 代数方程
solution = sp.solve(x**2 - 4, x)  # [-2, 2]

# 微分方程
y = sp.Function('y')
eq = sp.Eq(y(x).diff(x), y(x))
sol = sp.dsolve(eq, y(x))
```

---

## Matplotlib绘图

### 基本绘图
```python
import matplotlib.pyplot as plt

# 线图
plt.plot(x, y, 'b-', label='y=f(x)')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Title')
plt.legend()
plt.grid(True)
plt.show()

# 散点图
plt.scatter(x, y, c='red', marker='o')

# 多子图
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes[0, 0].plot(x, y)
```

### 3D绘图
```python
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z)
```

---

## 常用代码片段

### 1. 数值求导
```python
def numerical_derivative(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
```

### 2. 牛顿迭代法求根
```python
def newton_method(f, df, x0, tol=1e-6, max_iter=100):
    x = x0
    for i in range(max_iter):
        x_new = x - f(x) / df(x)
        if abs(x_new - x) < tol:
            return x_new
        x = x_new
    return None
```

### 3. 梯度下降
```python
def gradient_descent(f, grad_f, x0, learning_rate=0.01, max_iter=1000):
    x = x0
    for i in range(max_iter):
        x = x - learning_rate * grad_f(x)
    return x
```

### 4. 蒙特卡洛积分
```python
def monte_carlo_integration(f, a, b, n=10000):
    x = np.random.uniform(a, b, n)
    return (b - a) * np.mean(f(x))
```

### 5. 欧拉法求解ODE
```python
def euler_method(f, y0, t):
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        dt = t[i+1] - t[i]
        y[i+1] = y[i] + f(y[i], t[i]) * dt
    return y
```

---

## 水利工程常用代码

### 1. 水库调洪计算
```python
from scipy.integrate import odeint

def reservoir_routing(V, t, Q_in, k):
    """水库调洪模型"""
    Q_out = k * V
    dVdt = Q_in - Q_out
    return dVdt

V0 = 0  # 初始蓄水量
t = np.linspace(0, 100, 1000)
V = odeint(reservoir_routing, V0, t, args=(100, 0.01))
```

### 2. 渗流计算
```python
def darcy_flow(K, I, A):
    """达西定律"""
    Q = K * I * A
    return Q

# 例：K=0.01 m/s, I=0.05, A=100 m²
Q = darcy_flow(0.01, 0.05, 100)  # 0.05 m³/s
```

### 3. 管流阻力计算
```python
def friction_factor(Re, epsilon_d=0):
    """摩阻系数（Colebrook-White）"""
    if Re < 2000:
        return 64 / Re
    else:
        # 使用迭代求解
        f = 0.02
        for _ in range(10):
            f = 0.25 / (np.log10(epsilon_d/3.7 + 2.51/(Re*np.sqrt(f))))**2
        return f
```

### 4. 频率分析
```python
from scipy import stats

def frequency_analysis(data, return_period):
    """频率分析"""
    # 拟合P-III分布
    params = stats.pearson3.fit(data)
    p = 1 / return_period
    x = stats.pearson3.ppf(1 - p, *params)
    return x

# 例：100年一遇洪水
Q100 = frequency_analysis(annual_floods, 100)
```

### 5. 水质模型
```python
def water_quality_model(C0, k, t):
    """一维水质模型（一阶反应）"""
    C = C0 * np.exp(-k * t)
    return C

# 例：初始浓度10 mg/L，降解系数0.1 /day
C = water_quality_model(10, 0.1, np.linspace(0, 30, 100))
```

---

## 🎯 学习建议

### 入门建议
1. 从NumPy基础开始
2. 掌握数组操作和矩阵运算
3. 学习SciPy的积分、优化、统计模块
4. 用SymPy验证手算结果

### 进阶建议
1. 学习编写高效的NumPy代码（向量化）
2. 掌握Matplotlib高级绘图
3. 学习Pandas数据处理
4. 结合工程问题编程实现

### 调试技巧
1. 使用`print()`输出中间结果
2. 使用`plt.plot()`可视化数据
3. 检查数组形状：`print(arr.shape)`
4. 使用Jupyter Notebook交互式开发

---

**《水利类数学一速成手册》**  
**Python函数速查表**  
**快速查阅 · 高效编程** 💻
