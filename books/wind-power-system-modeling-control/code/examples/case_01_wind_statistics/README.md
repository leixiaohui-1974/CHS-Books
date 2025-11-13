# 案例1: 风速统计分析

**难度**: ⭐⭐  
**类型**: 风资源评估基础

---

## 📋 案例说明

### 工程背景

风电场开发的第一步是评估风资源。本案例演示如何对风速数据进行统计分析，包括：
- Weibull分布建模
- 风功率密度计算
- 参数拟合与验证

这些分析结果是风电场选址、机型选择和经济性评估的基础。

### 学习目标

1. **理解Weibull分布**：掌握风速概率分布的数学描述
2. **掌握风功率密度**：理解风速与功率的三次方关系
3. **学会数据分析**：从实测数据提取关键参数
4. **工程应用**：评估风电场风资源等级

---

## 🎯 核心知识点

### 1. Weibull分布

风速通常服从**Weibull分布**：

```python
f(v) = (k/c) * (v/c)^(k-1) * exp(-(v/c)^k)
```

**参数意义**：
- `k` (形状参数): 控制分布形状，典型值1.5-3.0
  - k < 2: 右偏分布
  - k = 2: **Rayleigh分布**（常用）
  - k > 2: 接近正态分布
  
- `c` (尺度参数): 接近平均风速，单位m/s

**统计量**：
```python
平均风速: v_mean = c * Γ(1 + 1/k)
方差: σ² = c² * [Γ(1 + 2/k) - Γ²(1 + 1/k)]
```

### 2. 风功率密度

风的功率密度（W/m²）：

```python
P/A = 0.5 * ρ * v³
```

其中：
- `ρ`: 空气密度 (kg/m³)，海平面标准值1.225
- `v`: 风速 (m/s)

**关键特性**：
- 功率与风速的**三次方**成正比
- 高风速的能量贡献远大于低风速

**平均功率密度**（从Weibull分布）：

```python
P_avg = 0.5 * ρ * c³ * Γ(1 + 3/k)
```

### 3. 能量模式因子 (EPF)

```python
EPF = P_avg / (0.5 * ρ * v_mean³)
```

- EPF > 1: 高风速出现频率较高（有利于发电）
- EPF ≈ 1: 风速分布均匀
- EPF < 1: 理论值（实际不存在）

对于Rayleigh分布（k=2）：
```python
EPF = Γ(1 + 3/k) / Γ³(1 + 1/k) ≈ 1.91
```

### 4. 风资源分级

根据IEC标准，风功率密度分级：

| 等级 | 功率密度 (W/m²) | 评价 |
|------|----------------|------|
| 1 | < 100 | 差 |
| 2 | 100-150 | 较差 |
| 3 | 150-200 | 一般 |
| 4 | 200-250 | 较好 |
| 5 | 250-300 | 好 |
| 6 | 300-400 | 很好 |
| 7 | > 400 | 优秀 |

---

## 💻 代码结构

### 核心类

#### 1. `WeibullDistribution`
```python
class WeibullDistribution:
    def __init__(self, k, c):
        """
        k: 形状参数
        c: 尺度参数
        """
    
    def pdf(self, v):
        """概率密度函数"""
    
    def cdf(self, v):
        """累积分布函数"""
    
    def sample(self, size):
        """生成随机样本"""
    
    @staticmethod
    def fit_from_data(wind_speeds):
        """从数据拟合参数"""
```python

#### 2. `WindPowerDensity`
```python
class WindPowerDensity:
    def __init__(self, rho=1.225):
        """rho: 空气密度"""
    
    def calculate(self, v):
        """计算功率密度"""
    
    def average_from_weibull(self, weibull):
        """从Weibull分布计算平均功率密度"""
    
    def energy_pattern_factor(self, weibull):
        """计算EPF"""
```python

#### 3. `WindStatistics`
```python
class WindStatistics:
    def __init__(self, wind_speeds, rho=1.225):
        """wind_speeds: 风速数据数组"""
    
    def histogram(self, bins=20):
        """计算直方图"""
    
    def average_power_density(self):
        """实测平均功率密度"""
    
    def get_report(self):
        """生成统计报告"""
```python

---

## 🚀 运行案例

### 安装依赖
```bash
pip install numpy scipy matplotlib
```python

### 运行
```bash
cd code/examples/case_01_wind_statistics
python main.py
```python

### 输出

**1. Weibull分布特性**
- 不同参数的PDF和CDF曲线
- 统计量对比

**2. 风功率密度**
- 功率密度随风速变化
- 风速分布与功率贡献

**3. 数据分析**
- 时间序列图
- 概率分布直方图
- 累积分布对比
- 箱线图

---

## 📊 实验结果

### 典型输出

```
演示1: Weibull分布特性
========================================

k=1.5, c=6:
  平均风速: 5.40 m/s
  标准差: 3.47 m/s
  最可能风速: 2.45 m/s

k=2.0, c=7:
  平均风速: 6.20 m/s
  标准差: 3.18 m/s
  最可能风速: 4.95 m/s

k=2.5, c=8:
  平均风速: 7.09 m/s
  标准差: 2.93 m/s
  最可能风速: 6.45 m/s
```python

```
演示2: 风功率密度计算
========================================

Weibull参数: k=2.0, c=8.0
平均风速: 7.09 m/s
平均风功率密度: 417.62 W/m²
能量模式因子 (EPF): 1.908

不同风速的功率密度:
  v =  3 m/s → P/A =   16.5 W/m²
  v =  5 m/s → P/A =   76.6 W/m²
  v =  7 m/s → P/A =  210.4 W/m²
  v =  9 m/s → P/A =  445.7 W/m²
  v = 11 m/s → P/A =  815.6 W/m²
  v = 13 m/s → P/A = 1347.0 W/m²
  v = 15 m/s → P/A = 2067.2 W/m²
```python

**关键发现**：
- 风速从5 m/s增加到15 m/s，功率密度增加了**27倍**
- 这就是风电场选址要求高风速的原因

---

## 🔬 进阶实验

### 实验1：不同Weibull参数的影响

**任务**：改变k和c值，观察对平均功率密度的影响

```python
# 修改main.py中的参数
distributions = [
    WeibullDistribution(k=1.5, c=7.0),
    WeibullDistribution(k=2.0, c=7.0),
    WeibullDistribution(k=2.5, c=7.0),
    WeibullDistribution(k=3.0, c=7.0),
]
```python

**问题**：
1. k值如何影响EPF？
2. 相同平均风速下，哪个k值的功率密度最大？

### 实验2：海拔对空气密度的影响

**任务**：计算不同海拔的空气密度

```python
from models.wind_resource import WindPowerDensity

# 不同海拔
elevations = [0, 1000, 2000, 3000]  # m
T = 15  # °C

for h in elevations:
    rho = WindPowerDensity.air_density(T=T, P=None, elevation=h)
    print(f"海拔 {h:4d} m: ρ = {rho:.3f} kg/m³")
```python

**问题**：
1. 海拔3000m处的空气密度比海平面低多少？
2. 这对风电场功率有何影响？

### 实验3：真实数据拟合

**任务**：使用真实风速数据进行分析

```python
# 读取真实数据（CSV文件）
import pandas as pd

data = pd.read_csv('wind_data.csv')
wind_speeds = data['wind_speed'].values

# 分析
stats = WindStatistics(wind_speeds)
report = stats.get_report()
```matlab

---

## 📝 作业练习

### 练习1：基础计算

已知某地风速服从Weibull分布，k=2.2, c=7.5 m/s：

1. 计算平均风速
2. 计算风速大于10 m/s的概率
3. 计算平均功率密度
4. 评估该地风资源等级

### 练习2：数据分析

给定一年的风速数据（8760小时）：

1. 绘制风速时间序列图
2. 拟合Weibull参数
3. 对比实测与拟合的分布
4. 计算实测和理论的平均功率密度

### 练习3：工程应用

某风电场风速数据统计：
- 平均风速：7.2 m/s
- 标准差：3.1 m/s
- 功率密度：380 W/m²

问题：
1. 估算Weibull参数k和c
2. 该风电场是否适合开发？
3. 如果装机容量100 MW，估算年发电量

**提示**：
- 风机容量因子典型值：20-40%
- 年发电量 = 装机容量 × 8760 × 容量因子

---

## 🌟 工程意义

### 风电场开发流程

```
风速数据采集 (1年+)
    ↓
统计分析 (本案例)
    ↓
风资源评估
    ↓
机型选择
    ↓
微观选址
    ↓
经济性分析
```

### 实际应用

1. **风电场选址**
   - 根据功率密度确定是否开发
   - 典型要求：P_avg > 200 W/m²

2. **机型选择**
   - 高风速区：选大功率机组
   - 低风速区：选低风速型机组

3. **发电量预测**
   - 基于Weibull分布和风机功率曲线
   - 计算年发电量

4. **经济性分析**
   - 风资源越好，投资回收期越短
   - 典型IRR: 8-12%

---

## 📚 参考资料

### 标准规范
- IEC 61400-12-1: 风力发电机组功率特性测试
- GB/T 18709: 风电场风能资源评估方法

### 相关书籍
1. 《风能资源评估方法》，贺德馨
2. "Wind Energy Explained", J.F. Manwell

### 在线资源
- [Global Wind Atlas](https://globalwindatlas.info/)
- [NREL Wind Resource Data](https://www.nrel.gov/wind/)

---

## 🔗 相关案例

- **案例2**: 风切变与湍流 - 风速随高度的变化
- **案例4**: 风轮功率特性 - 从风速到功率
- **案例11**: 最优叶尖速比 - MPPT控制基础

---

**更新日期**: 2025-11-04  
**作者**: CHS-BOOKS  
**难度**: ⭐⭐ 入门

🌬️ **开始风资源评估之旅！**
