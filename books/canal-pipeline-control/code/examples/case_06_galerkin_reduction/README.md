# 案例6：Galerkin投影与有限元降阶

## 问题描述

在案例4-5中，我们学习了数据驱动的降阶方法（POD和DMD）。它们从数据快照中提取模态，然后进行降阶。

**Galerkin投影**是另一类降阶方法，基于**数学理论**而非数据。其核心思想是：选择一组基函数，将PDE解表示为基函数的线性组合，然后通过Galerkin投影将无限维PDE降为有限维ODE。

```
降阶方法分类：

数据驱动方法              理论驱动方法
┌──────────┐            ┌──────────┐
│ POD/DMD  │            │ Galerkin │
│ 从数据   │            │ 从理论   │
│ 学习模态 │            │ 选择基函数│
└──────────┘            └──────────┘
     ↓                       ↓
 需要快照数据            需要数学模型
 最优但特定工况          通用但需调整
```

**Galerkin方法的优势**：
- 不需要收集大量快照数据
- 可以利用先验知识选择合适的基函数
- 理论保证（如能量守恒）
- 适合参数化问题

**Galerkin方法的挑战**：
- 需要选择合适的基函数（非平凡）
- 计算质量矩阵和刚度矩阵
- 处理非线性项（可能需要额外技巧）
- 边界条件的处理

## 理论基础

### 1. Galerkin方法概述

假设我们要求解PDE：
$$\frac{\partial u}{\partial t} = L(u) + f$$

其中$L$是空间微分算子，$f$是源项。

**步骤1：选择基函数**

选择一组基函数$\{\phi_1(x), \phi_2(x), \ldots, \phi_r(x)\}$，近似解为：
$$u(x,t) \approx \sum_{i=1}^{r} a_i(t) \phi_i(x) = \boldsymbol{\Phi}(x) \mathbf{a}(t)$$

其中$\mathbf{a}(t) = [a_1(t), a_2(t), \ldots, a_r(t)]^T$是待求的时间系数。

**步骤2：代入PDE**

$$\sum_{i=1}^{r} \frac{da_i}{dt} \phi_i(x) = L\left(\sum_{i=1}^{r} a_i \phi_i\right) + f$$

这个等式不能精确满足（因为使用了近似），会有残差$R(x,t)$。

**步骤3：Galerkin投影**

要求残差与每个测试函数正交（即在该函数的"方向"上残差为零）：
$$\int_{\Omega} R(x,t) \phi_j(x) dx = 0, \quad j=1,2,\ldots,r$$

这给出r个常微分方程，形式为：
$$\mathbf{M} \frac{d\mathbf{a}}{dt} = \mathbf{K} \mathbf{a} + \mathbf{f}$$

其中：
- **质量矩阵**：$M_{ij} = \int \phi_i \phi_j dx$
- **刚度矩阵**：$K_{ij} = \int \phi_i L(\phi_j) dx$
- **力向量**：$f_i = \int \phi_i f dx$

### 2. 应用于Saint-Venant方程

连续性方程（简化）：
$$\frac{\partial h}{\partial t} + \frac{1}{B}\frac{\partial Q}{\partial x} = 0$$

Galerkin近似：
$$h(x,t) = \sum_{i=1}^{r} a_i(t) \phi_i(x)$$

代入并投影：
$$\int_0^L \left[\sum_i \frac{da_i}{dt}\phi_i + \frac{1}{B}\frac{\partial Q}{\partial x}\right] \phi_j dx = 0$$

整理得：
$$\sum_i M_{ij} \frac{da_i}{dt} = -\frac{1}{B} \int_0^L \frac{\partial Q}{\partial x} \phi_j dx$$

通过分部积分可以进一步处理空间导数项。

### 3. 基函数选择

**方法1：正弦/余弦基**
$$\phi_i(x) = \sin\left(\frac{i\pi x}{L}\right) \quad \text{或} \quad \cos\left(\frac{i\pi x}{L}\right)$$

优点：正交性好，易于积分
缺点：边界条件限制

**方法2：多项式基（Legendre）**
$$\phi_0(x) = 1, \quad \phi_1(x) = x, \quad \phi_2(x) = \frac{1}{2}(3x^2-1), \ldots$$

优点：适合任意边界条件
缺点：高阶多项式可能数值不稳定

**方法3：POD模态**

直接使用POD提取的模态作为基函数：
$$\phi_i = \text{POD模态}_i$$

优点：数据驱动，针对特定问题最优
缺点：需要先收集数据

**方法4：有限元基（帽函数）**
$$\phi_i(x) = \begin{cases}
\frac{x - x_{i-1}}{x_i - x_{i-1}} & x_{i-1} \leq x \leq x_i \\
\frac{x_{i+1} - x}{x_{i+1} - x_i} & x_i \leq x \leq x_{i+1} \\
0 & \text{otherwise}
\end{cases}$$

优点：局部支撑，稀疏矩阵
缺点：需要很多基函数才能达到高精度

### 4. 质量矩阵和刚度矩阵计算

**质量矩阵**（内积矩阵）：
$$M_{ij} = \int_0^L \phi_i(x) \phi_j(x) dx$$

如果基函数正交归一，则$\mathbf{M} = \mathbf{I}$（单位矩阵）。

**刚度矩阵**（取决于算子$L$）：

对于一阶导数算子$L = \frac{\partial}{\partial x}$：
$$K_{ij} = \int_0^L \phi_i(x) \frac{\partial \phi_j}{\partial x} dx$$

可以通过分部积分转换：
$$K_{ij} = \left[\phi_i \phi_j\right]_0^L - \int_0^L \frac{\partial \phi_i}{\partial x} \phi_j dx$$

## 实验设计

### Part 1: 不同基函数性能对比

**实验目的**：比较不同基函数的降阶效果

**基函数类型**：
1. 正弦基函数
2. Legendre多项式基
3. POD模态基

**评价指标**：
- 重构误差
- 计算效率
- 收敛速度

### Part 2: Galerkin降阶模型求解

**实验目的**：使用Galerkin方法构建降阶模型并求解

**步骤**：
1. 选择基函数（r=10）
2. 计算质量矩阵M和刚度矩阵K
3. 构建降阶ODE系统
4. 求解并重构

### Part 3: 边界条件处理

**实验目的**：展示如何在Galerkin框架中处理边界条件

**方法**：
- 强制边界条件：基函数满足边界条件
- 弱边界条件：通过罚函数加入

## 工程意义

### 1. Galerkin方法的应用场景

**适合场景**：
- 有明确数学模型但数据稀缺
- 需要参数化降阶模型（不同参数下复用）
- 边界条件复杂
- 需要理论保证（如守恒律）

**不适合场景**：
- 没有数学模型（纯黑盒系统）
- 数据充足但模型不准确
- 强非线性（需要DEIM等技术）

### 2. Galerkin vs POD

| 特性 | Galerkin | POD |
|------|----------|-----|
| 基函数来源 | 先验选择 | 数据驱动 |
| 需要数据 | 否 | 是 |
| 参数化能力 | 强 | 弱 |
| 最优性 | 依赖基函数选择 | 能量最优 |
| 计算成本 | 积分计算 | SVD计算 |

**混合方法**：POD-Galerkin
- 使用POD提取基函数
- 使用Galerkin投影构建降阶模型
- 结合两者优势

## 参数说明

### 渠道参数
| 参数 | 数值 | 单位 |
|------|------|------|
| 长度 L | 1000 | m |
| 宽度 B | 5 | m |
| 坡度 i₀ | 0.001 | - |
| 糙率 n | 0.025 | s/m^(1/3) |
| 节点数 N | 51 | - |

### Galerkin参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 基函数数量 r | 5-15 | 降阶维数 |
| 积分点数 | 100 | 数值积分 |

## 运行说明

```bash
python main.py
```

输出：
- part1_basis_comparison.png: 基函数对比
- part2_galerkin_reconstruction.png: Galerkin重构
- part3_galerkin_vs_pod.png: Galerkin vs POD对比

## 总结

案例6展示了Galerkin投影方法的理论和实现。关键要点：

1. **Galerkin是理论驱动的降阶方法**，基于数学投影
2. **基函数选择至关重要**，影响精度和效率
3. **质量矩阵和刚度矩阵**是Galerkin方法的核心
4. **Galerkin可以与POD结合**，形成POD-Galerkin方法
5. **适合有明确数学模型的问题**

Galerkin方法是有限元方法（FEM）的理论基础，在结构力学、流体力学等领域广泛应用。
