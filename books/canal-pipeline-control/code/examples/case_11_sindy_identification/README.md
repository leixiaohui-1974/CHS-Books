# 案例11：SINDy稀疏辨识

## 问题描述

在案例8-10中，我们学习了各种系统辨识方法，但它们都有一个共同点：**需要预先假设模型结构**（如状态空间、NARX、Hammerstein-Wiener）。

但如果我们**不知道系统的控制方程**呢？能否从数据中**自动发现**控制方程？

**SINDy（Sparse Identification of Nonlinear Dynamics）**正是为此而生的革命性方法！

```python
传统辨识 vs SINDy：

传统方法：                    SINDy：
已知模型结构                  未知模型结构
  ↓                            ↓
估计参数                      发现方程
  ↓                            ↓
y(k) = 0.7y(k-1) + ...       dy/dt = -0.1y + 0.5u - 0.2y²

需要领域知识                  数据驱动发现
```

**SINDy的核心思想**：

大多数物理系统的控制方程是**稀疏的**，即只包含少量项。例如：

- 单摆：$\ddot{\theta} = -\frac{g}{L}\sin(\theta)$（只有$\sin(\theta)$一项）
- 洛伦兹系统：$\dot{x} = \sigma(y-x)$（只有两项）
- 渠道系统：$\frac{\partial h}{\partial t} + \frac{\partial Q}{\partial x} = 0$（只有导数项）

**SINDy方法**：
1. 构造大量候选函数（多项式、三角函数等）
2. 使用稀疏优化选择最重要的几项
3. 得到简洁的控制方程

**优势**：
- **可解释性**：得到符号方程，而非黑盒模型
- **泛化能力**：发现真实物理规律，外推能力强
- **数据高效**：稀疏约束减少过拟合
- **适应性强**：不需要预设模型结构

**应用场景**：
- 未知系统的方程发现
- 从复杂仿真中提取简化模型
- 物理定律验证
- 异常检测（偏离已知方程）

## 理论基础

### 1. SINDy核心算法

**问题陈述**：

给定时间序列数据$\mathbf{X} = [\mathbf{x}(t_1), \mathbf{x}(t_2), \ldots, \mathbf{x}(t_m)]$，其中$\mathbf{x} \in \mathbb{R}^n$。

目标：找到控制方程
$$\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x}, \mathbf{u})$$

**SINDy假设**：

控制方程可以表示为**函数库**$\Theta(\mathbf{X})$中少量函数的线性组合：

$$\dot{\mathbf{x}} = \Theta(\mathbf{X}) \boldsymbol{\Xi}$$

其中：
- $\Theta(\mathbf{X})$：函数库矩阵（m × p）
- $\boldsymbol{\Xi}$：系数矩阵（p × n），**稀疏的**！

**函数库示例**（以2维系统为例）：

$$\Theta(\mathbf{X}) = \begin{bmatrix}
1 & x_1 & x_2 & x_1^2 & x_1 x_2 & x_2^2 & \sin(x_1) & \cdots \\
1 & x_1 & x_2 & x_1^2 & x_1 x_2 & x_2^2 & \sin(x_1) & \cdots \\
\vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \ddots
\end{bmatrix}$$

每一行对应一个时刻，每一列对应一个候选函数。

**稀疏优化问题**：

$$\min_{\boldsymbol{\Xi}} \|\dot{\mathbf{X}} - \Theta(\mathbf{X})\boldsymbol{\Xi}\|_2^2 + \lambda \|\boldsymbol{\Xi}\|_0$$

其中$\|\boldsymbol{\Xi}\|_0$是L0范数（非零元素个数）。

**难点**：L0优化是NP困难问题！

### 2. Sequential Threshold Least Squares (STLS)

由于L0优化困难，SINDy使用**序贯阈值最小二乘**：

**算法步骤**：

1. **初始化**：普通最小二乘
   $$\boldsymbol{\Xi} = \arg\min \|\dot{\mathbf{X}} - \Theta(\mathbf{X})\boldsymbol{\Xi}\|_2^2$$

2. **阈值化**：将小于阈值$\lambda$的系数置零
   $$\Xi_{ij} = \begin{cases}
   \Xi_{ij}, & |\Xi_{ij}| > \lambda \\
   0, & |\Xi_{ij}| \leq \lambda
   \end{cases}$$

3. **重新拟合**：仅对非零项重新最小二乘

4. **迭代**：重复步骤2-3直到收敛

**伪代码**：

```python
def STLS(Theta, Xdot, lambda):
    # 初始最小二乘
    Xi = lstsq(Theta, Xdot)

    for iteration in range(max_iter):
        # 阈值化
        small_inds = abs(Xi) < lambda
        Xi[small_inds] = 0

        # 对非零项重新拟合
        for i in range(n):
            big_inds = Xi[:, i] != 0
            Xi[big_inds, i] = lstsq(Theta[:, big_inds], Xdot[:, i])

    return Xi
```bash

**阈值$\lambda$的选择**：
- 太小：保留太多项，不够稀疏
- 太大：可能丢失重要项
- 经验值：$\lambda = 0.01 \sim 0.1$
- 交叉验证选择

### 3. 函数库设计

函数库的选择直接影响SINDy的性能。

**常用函数库**：

1. **多项式库**（最常用）：
   - 1阶：$1, x_1, x_2, \ldots, x_n$
   - 2阶：$x_1^2, x_1 x_2, \ldots, x_n^2$
   - 3阶及以上

2. **三角函数库**：
   - $\sin(x_i), \cos(x_i), \sin(x_i x_j), \ldots$

3. **有理函数库**：
   - $\frac{1}{x_i}, \frac{x_i}{x_j}, \ldots$

4. **自定义函数**：
   - 根据物理先验添加（如$e^x, \log(x)$）

**对于渠道系统**：

基于Saint-Venant方程的物理知识：
- 线性项：$h, Q, \frac{\partial h}{\partial x}$
- 非线性项：$h^{5/3}, \sqrt{h}, h Q$
- 空间导数项

**函数库维度控制**：

对于n维系统，p阶多项式库有$\binom{n+p}{p}$项。快速增长！

控制策略：
- 限制阶数（通常不超过3阶）
- 自适应选择（先简单后复杂）
- 领域知识筛选

### 4. 数值微分

SINDy需要计算$\dot{\mathbf{X}}$，但数据通常只有$\mathbf{X}$。

**数值微分方法**：

1. **有限差分**：
   $$\dot{x}(t_i) \approx \frac{x(t_{i+1}) - x(t_i)}{\Delta t}$$

   问题：对噪声极其敏感！

2. **中心差分**：
   $$\dot{x}(t_i) \approx \frac{x(t_{i+1}) - x(t_{i-1})}{2\Delta t}$$

   稍好，但仍敏感。

3. **多项式拟合**（推荐）：
   - 在局部窗口用多项式拟合
   - 解析求导
   - 更稳定

4. **总变分正则化（TVR）**：
   $$\min_{\dot{x}} \|x - \int \dot{x} dt\|^2 + \alpha \|\dot{x}\|_{TV}$$

   最稳健，但计算昂贵。

**对于噪声数据**：
- 先去噪（滤波、平滑）
- 使用稳健微分方法
- 或者使用弱SINDy（见下文）

### 5. 弱SINDy

**动机**：传统SINDy需要计算导数，对噪声敏感。

**弱SINDy思路**：不直接计算导数，而是使用积分形式。

**弱形式**：

对于ODE $\dot{x} = f(x)$，乘以测试函数$\phi(t)$并积分：

$$\int \phi(t) \dot{x}(t) dt = \int \phi(t) f(x(t)) dt$$

分部积分左边：
$$\int \phi(t) \dot{x}(t) dt = -\int \phi'(t) x(t) dt + [\text{边界项}]$$

最终形式：
$$-\int \phi'(t) x(t) dt = \int \phi(t) \Theta(x) \boldsymbol{\xi} dt$$

**优势**：
- 不需要计算导数
- 对噪声鲁棒
- 测试函数可以平滑数据

**测试函数选择**：
- 多项式
- 三角函数
- 高斯函数

### 6. 集成SINDy (Ensemble SINDy)

**问题**：SINDy对噪声和初始条件敏感，结果可能不稳定。

**集成策略**：

1. **多次采样**：
   - Bootstrap采样（有放回）
   - 或添加不同噪声

2. **多次运行SINDy**：
   - 每次得到一组系数$\boldsymbol{\Xi}_k$

3. **集成结果**：
   - **投票**：某项在多数结果中非零→保留
   - **平均**：对非零系数取平均
   - **中位数**：更稳健

**优势**：
- 提高鲁棒性
- 识别真正重要的项
- 量化不确定性

**缺点**：
- 计算量增加

### 7. SINDy变体

近年来SINDy有多种扩展：

1. **SINDy-PI**（偏微分方程）：
   - 处理时空数据
   - 发现PDE（如Saint-Venant方程）

2. **SINDy-c**（控制）：
   - 同时辨识系统和控制输入
   - 用于控制器设计

3. **Implicit SINDy**：
   - 隐式方程$f(\dot{x}, x) = 0$
   - 更一般形式

4. **SINDy-BayesOpt**：
   - 贝叶斯优化选择函数库
   - 自适应稀疏度

5. **Neural SINDy**：
   - 神经网络学习函数库
   - 结合深度学习和SINDy

## 实验设计

### Part 1: SINDy基础算法验证

**实验目的**：在已知系统上验证SINDy

**系统**：Lorenz系统（混沌）
$$\begin{aligned}
\dot{x} &= \sigma(y - x) \\
\dot{y} &= x(\rho - z) - y \\
\dot{z} &= xy - \beta z
\end{aligned}$$

**步骤**：
1. 生成Lorenz系统数据
2. 构造多项式函数库
3. 应用SINDy算法
4. 对比发现的方程与真实方程

**评价指标**：
- 系数误差
- 稀疏度（非零项数量）
- 长期预测误差

### Part 2: 函数库设计与对比

**实验目的**：研究不同函数库的影响

**对比**：
- 多项式库（1-3阶）
- 三角函数库
- 混合库

**系统**：简单摆
$$\ddot{\theta} = -\frac{g}{L}\sin(\theta)$$

### Part 3: 渠道系统方程发现

**实验目的**：使用SINDy发现渠道系统的简化控制方程

**步骤**：
1. 使用Saint-Venant仿真生成数据
2. 构造基于物理先验的函数库
3. 应用SINDy
4. 验证发现的方程

**期望**：发现类似于$\frac{dh}{dt} \propto Q, \frac{dQ}{dt} \propto h$的方程

### Part 4: 噪声鲁棒性与集成SINDy

**实验目的**：测试SINDy对噪声的鲁棒性

**方法**：
- 添加不同水平噪声
- 对比普通SINDy vs 集成SINDy
- 对比不同微分方法

## 工程意义

### 1. SINDy的独特价值

**场景1：复杂仿真的简化**

某水利工程使用CFD仿真设计渠道，但CFD太慢无法用于实时控制。

使用SINDy：
1. 从CFD结果提取时间序列
2. 发现简化的ODE模型
3. 用于快速MPC

**结果**：保留95%精度，速度提升1000倍。

**场景2：未知系统的快速建模**

新建灌区，没有历史数据和经验公式。

传统方法：
- 需要长时间观测
- 需要专家建模
- 模型可能不准确

SINDy方法：
- 几周数据即可
- 自动发现方程
- 可解释的模型

### 2. 与其他辨识方法对比

| 方法 | 模型形式 | 可解释性 | 数据需求 | 外推能力 |
|------|---------|---------|---------|---------|
| N4SID | 状态空间 | 低 | 中 | 差 |
| NARX | 差分方程 | 中 | 中 | 中 |
| 神经网络 | 黑盒 | 很低 | 高 | 很差 |
| SINDy | 微分方程 | **很高** | 低-中 | **很好** |

**SINDy最适合**：
- 需要理解物理机制
- 需要外推到未测试工况
- 数据量有限但高质量
- 需要简洁模型用于控制

### 3. 实际应用建议

**数据采集**：
- **质量>数量**：SINDy对噪声敏感，宁缺毋滥
- **充分激励**：覆盖系统动态范围
- **高采样率**：便于数值微分
- **长时间**：捕捉慢动态

**函数库设计**：
- **从简单开始**：先低阶多项式
- **利用先验**：加入物理相关函数
- **控制规模**：避免组合爆炸
- **迭代添加**：根据残差添加项

**阈值选择**：
- **交叉验证**：测试集性能最优
- **稀疏度权衡**：太稀疏→精度低，太密→过拟合
- **经验起点**：$\lambda = 0.05 \times \max(|\boldsymbol{\Xi}_{LS}|)$

**噪声处理**：
- **预处理**：滤波、平滑
- **稳健微分**：多项式拟合、TVR
- **集成方法**：提高稳定性
- **弱SINDy**：强噪声时优先考虑

**模型验证**：
- **物理检查**：发现的方程是否合理？
- **稳定性**：系统是否稳定？
- **守恒律**：是否满足质量/能量守恒？
- **长期预测**：10倍时间尺度测试

### 4. 局限性与注意事项

**不适合场景**：
- 强噪声数据（SNR < 10dB）
- 非常高维系统（n > 10）
- 没有稀疏性的系统
- 纯随机过程

**常见陷阱**：
1. **虚假稀疏**：巧合的项组合
2. **欠拟合**：阈值太大，丢失重要项
3. **数值微分失败**：噪声放大
4. **函数库不足**：真实项不在库中

**解决方案**：
- 多次实验验证
- 物理合理性检查
- 残差分析
- 领域专家审查

## 参数说明

### SINDy参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 阈值 λ | 0.01-0.1 | 稀疏度控制 |
| 多项式阶数 | 2-3 | 函数库复杂度 |
| 最大迭代次数 | 10 | STLS迭代 |

### 数值微分参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 窗口大小 | 5-11 | 多项式拟合 |
| 多项式阶数 | 3-5 | 平滑程度 |

### 集成SINDy参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 集成次数 | 100 | Bootstrap采样 |
| 噪声水平 | 1-5% | 添加扰动 |
| 投票阈值 | 50-80% | 保留频率 |

### 渠道系统参数
| 参数 | 数值 | 单位 |
|------|------|------|
| 长度 L | 1000 | m |
| 宽度 B | 5 | m |
| 坡度 i₀ | 0.001 | - |
| 糙率 n | 0.025 | s/m^(1/3) |

## 运行说明

```bash
python main.py
```

输出：
- `part1_sindy_lorenz.png`: Lorenz系统SINDy验证
- `part2_library_comparison.png`: 函数库对比
- `part3_canal_discovery.png`: 渠道系统方程发现
- `part4_ensemble_sindy.png`: 集成SINDy鲁棒性

## 总结

案例11展示了SINDy稀疏辨识方法。关键要点：

1. **SINDy是数据驱动的方程发现工具**，不需要预设模型结构
2. **稀疏优化是核心**，假设控制方程只包含少量项
3. **函数库设计很关键**，需要平衡表达能力和计算复杂度
4. **数值微分是挑战**，对噪声敏感，需要稳健方法
5. **集成SINDy提高鲁棒性**，通过多次采样和投票
6. **可解释性是最大优势**，发现符号方程而非黑盒
7. **适合高质量数据**，对噪声敏感，需要预处理

SINDy代表了系统辨识的新范式：从"参数估计"到"方程发现"。它特别适合：
- 科学发现（发现未知物理定律）
- 复杂系统简化（从CFD/FEM提取ODE）
- 可解释AI（符号回归）
- 混合建模（物理+数据驱动）

## 参考文献

1. Brunton, S. L., Proctor, J. L., & Kutz, J. N. (2016). Discovering governing equations from data by sparse identification of nonlinear dynamical systems. *Proceedings of the National Academy of Sciences*, 113(15), 3932-3937.

2. Rudy, S. H., Brunton, S. L., Proctor, J. L., & Kutz, J. N. (2017). Data-driven discovery of partial differential equations. *Science Advances*, 3(4), e1602614.

3. Champion, K., Lusch, B., Kutz, J. N., & Brunton, S. L. (2019). Data-driven discovery of coordinates and governing equations. *Proceedings of the National Academy of Sciences*, 116(45), 22445-22451.

4. Messenger, D. A., & Bortz, D. M. (2021). Weak SINDy for partial differential equations. *Journal of Computational Physics*, 443, 110525.

5. Fasel, U., Kutz, J. N., Brunton, B. W., & Brunton, S. L. (2022). Ensemble-SINDy: Robust sparse model discovery in the low-data, high-noise limit, with active learning and control. *Proceedings of the Royal Society A*, 478(2260), 20210904.

6. Kaptanoglu, A. A., et al. (2021). PySINDy: A comprehensive Python package for robust sparse system identification. *arXiv preprint arXiv:2111.08481*.
