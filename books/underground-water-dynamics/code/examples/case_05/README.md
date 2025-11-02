# 案例5：有限元方法基础

## 学习目标

1. ✅ 理解Galerkin有限元方法
2. ✅ 掌握三角形网格生成
3. ✅ 学习单元刚度矩阵组装
4. ✅ 理解弱形式和变分原理
5. ✅ 比较有限元与有限差分

## 问题描述

使用有限元方法求解二维稳态地下水流动：
- 区域：矩形 Lx=100m × Ly=80m
- 水力传导度：K = 10 m/day
- 边界条件：左边h=20m，右边h=10m，上下无流
- 网格：三角形单元

## 理论基础

### 强形式（偏微分方程）

```
-∇·(K∇h) = 0    in Ω (求解域)
h = g            on Γ_D (Dirichlet边界)
-K∂h/∂n = q      on Γ_N (Neumann边界)
```

### 弱形式（变分形式）

对强形式乘以测试函数w并在Ω上积分：

```
∫∫_Ω K ∇w · ∇h dA = 0    ∀w ∈ H₀¹(Ω)
```

这就是Galerkin弱形式。

### 有限元离散

**1. 近似解**：
```
h(x,y) ≈ h^h(x,y) = Σ N_i(x,y) · h_i
```

其中：
- N_i: 形函数（线性三角形单元）
- h_i: 节点未知量

**2. 形函数（线性三角形）**：

参考单元坐标(ξ, η)：
```
N₁ = 1 - ξ - η
N₂ = ξ
N₃ = η
```

**3. 单元刚度矩阵**：

```
K_elem[i,j] = ∫∫ K ∇N_i · ∇N_j dA
```

对于常数K的三角形单元：
```
K_elem = K · (∇N)ᵀ · (∇N) · |det(J)| / 2
```

其中J是Jacobian矩阵。

**4. 全局系统组装**：

```
[K_global]{h} = {F}
```

通过将单元刚度矩阵组装到全局矩阵。

## 数值方法对比

### 有限差分法（FDM）
- ✅ 简单直观
- ✅ 易于编程
- ❌ 限于规则网格
- ❌ 复杂边界困难

### 有限元法（FEM）
- ✅ 适应复杂几何
- ✅ 自然边界条件
- ✅ 理论基础严格
- ❌ 编程较复杂

## 运行代码

```bash
cd code/examples/case_05
python3 case_05_finite_element.py
```

## 输出结果

程序将生成：

1. **case_05_mesh.png**: 三角形网格可视化
2. **case_05_fem_solution.png**: 有限元解
3. **case_05_fd_solution.png**: 有限差分解（对比）
4. **case_05_comparison.png**: 方法对比和误差分析
5. **case_05_velocity.png**: 流速场
6. **case_05_convergence.png**: 网格收敛性分析

## 预期结果

### 数值精度

- **L² 误差**: < 1e-6 m
- **L∞ 误差**: < 1e-6 m
- **与FDM差异**: RMSE < 0.01 m

### 收敛性

线性三角形单元的理论收敛率：
- L² 范数: O(h²)
- L∞ 范数: O(h²)

其中h是网格特征尺寸。

### 网格质量

- 最小角度: ≈ 45°（结构化三角形网格）
- 单元面积: 均匀分布

## 实验探索

### 实验1：改变网格密度

```python
mesh_configs = [
    (6, 5),    # 粗网格
    (11, 9),   # 中等网格
    (21, 17),  # 细网格
    (41, 33)   # 很细网格
]
```

**观察**：误差随网格加密呈二次方下降。

### 实验2：网格质量影响

创建退化网格：
```python
# 故意创建不规则网格
vertices_perturbed = vertices + random_noise
```

**观察**：网格质量下降导致精度降低。

### 实验3：非均质问题

```python
# 分区设置K值
K_elem = np.ones(mesh.n_elements) * 10.0
K_elem[某些单元] = 1.0  # 低渗透区
```

**观察**：有限元更容易处理非均质。

### 实验4：复杂边界

```python
# 尝试使用meshpy生成圆形或L形区域
import meshpy.triangle as triangle
# ... 生成复杂几何
```

**观察**：有限元的几何灵活性优势。

### 实验5：高阶单元

```python
# 使用二次三角形单元（6节点）
# 需要修改形函数和刚度矩阵计算
```

**观察**：高阶单元精度更高但计算量更大。

## 常见问题

### Q1: 为什么使用弱形式？

**A**: 
1. 降低对解的光滑性要求（从C²到C¹）
2. 自然包含Neumann边界条件
3. 能量极小化的物理意义
4. 更容易处理非均质和各向异性

### Q2: Jacobian矩阵的作用？

**A**: 
将参考单元映射到物理单元：
```
J = [∂x/∂ξ  ∂x/∂η]
    [∂y/∂ξ  ∂y/∂η]
```

用于：
- 坐标变换
- 形函数导数变换
- 积分测度变换（det(J)）

### Q3: 如何确保系统矩阵正定？

**A**: 
1. 至少有一个Dirichlet边界条件
2. K > 0（物理要求）
3. 网格不退化（det(J) > 0）

### Q4: 为什么与FDM结果略有不同？

**A**: 
1. 离散化方式不同
2. 网格节点位置相同但单元不同
3. 边界处理方式差异
4. 对于线性问题，差异很小（< 1%）

### Q5: 如何选择网格密度？

**A**: 
通过网格收敛性分析：
1. 逐步加密网格
2. 观察解的变化
3. 当相邻网格解差异 < 容差时停止
4. 平衡精度与计算成本

## 数学推导补充

### 从强形式到弱形式

**步骤1**：乘以测试函数
```
-∇·(K∇h) · w = 0
```

**步骤2**：在Ω上积分
```
-∫∫_Ω ∇·(K∇h) · w dA = 0
```

**步骤3**：分部积分（散度定理）
```
∫∫_Ω K∇h · ∇w dA - ∫_Γ K∂h/∂n · w ds = 0
```

**步骤4**：应用Neumann边界条件
```
∫∫_Ω K∇h · ∇w dA = ∫_Γ_N q · w ds
```

### Galerkin方法

选择测试函数w与形函数N相同：
```
w = N_i,  i = 1, 2, ..., n
```

得到离散系统：
```
[K]{h} = {F}
```

### 单元刚度矩阵推导

对于线性三角形单元：

```
K_elem[i,j] = ∫∫_Ω_e K ∇N_i · ∇N_j dA
```

因为∇N_i在单元内为常数：

```
K_elem[i,j] = K · ∇N_i · ∇N_j · A_e
```

其中A_e是单元面积。

## 程序结构

```python
# 1. 生成网格
mesh = generate_triangular_mesh(...)

# 2. 设置边界条件
boundary_conditions = {...}

# 3. 组装全局矩阵
for each element:
    K_elem = compute_element_stiffness(...)
    assemble_to_global(K_global, K_elem, ...)

# 4. 应用边界条件
apply_dirichlet_bc(K_global, F, bc)

# 5. 求解
h = solve(K_global, F)

# 6. 后处理
grad_h = compute_gradient(h, mesh)
```

## 延伸阅读

1. Hughes, T. J. R. (2000). *The Finite Element Method: Linear Static and Dynamic Finite Element Analysis*
2. Zienkiewicz, O. C., et al. (2005). *The Finite Element Method: Its Basis and Fundamentals*
3. Brenner, S. C., & Scott, L. R. (2008). *The Mathematical Theory of Finite Element Methods*

## 下一步

完成本案例后，继续学习：
- **案例6**：参数率定方法
- **案例7**：PEST自动率定
- **案例8**：贝叶斯推断

或者深入有限元方法：
- 二次单元
- 自适应网格加密
- 非线性问题
- 时间依赖问题的FEM
