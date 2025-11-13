# 案例8：贝叶斯推断与MCMC

## 学习目标

1. ✅ 理解贝叶斯推断原理
2. ✅ 掌握MCMC采样方法
3. ✅ 学习后验分布估计
4. ✅ 理解不确定性量化
5. ✅ 对比频率学派与贝叶斯方法

## 问题描述

使用贝叶斯推断方法率定地下水模型参数：
- 水力传导度 K
- 边界条件 h_left, h_right

**方法**：
- Metropolis-Hastings MCMC采样
- 后验分布估计
- 预测不确定性量化
- 与频率学派方法对比

## 贝叶斯推断基础

### 贝叶斯定理

**核心公式**：
```python
p(θ|D) = p(D|θ) p(θ) / p(D)
```

或写成比例形式：
```python
p(θ|D) ∝ p(D|θ) p(θ)
后验 ∝ 似然 × 先验
```

其中：
- **θ**: 参数
- **D**: 观测数据
- **p(θ|D)**: 后验分布（推断目标）
- **p(D|θ)**: 似然函数
- **p(θ)**: 先验分布
- **p(D)**: 边际似然（归一化常数）

### 三个核心概念

**1. 先验分布 p(θ)**
- 在看到数据之前对参数的认识
- 可以是信息性的或无信息性的
- 例：均匀分布、正态分布

**2. 似然函数 p(D|θ)**
- 给定参数θ，观测数据D的概率
- 连接数据和模型
- 例：正态似然、泊松似然

**3. 后验分布 p(θ|D)**
- 结合先验和数据后的参数分布
- 包含关于参数的全部信息
- 可计算均值、方差、置信区间等

### 与频率学派的区别

| 方面 | 频率学派 | 贝叶斯学派 |
|------|---------|-----------|
| 参数 | 固定但未知 | 随机变量 |
| 估计 | 点估计 | 分布估计 |
| 不确定性 | 置信区间 | 可信区间 |
| 先验知识 | 不使用 | 可融合 |
| 计算 | 通常简单 | 通常复杂 |

## MCMC方法

### 为什么需要MCMC？

**问题**：后验分布通常无法解析计算

```python
p(θ|D) = p(D|θ)p(θ) / ∫p(D|θ)p(θ)dθ
                      ↑
              积分通常无法计算
```

**解决**：使用MCMC从后验分布采样，无需计算归一化常数

### Metropolis-Hastings算法

**算法流程**：

```python
1. 初始化：选择初始参数θ₀
2. For t = 1, 2, ..., T:
   a) 从提议分布生成候选：θ* ~ q(·|θₜ)
   b) 计算接受概率：
      α = min(1, [p(θ*|D)q(θₜ|θ*)] / [p(θₜ|D)q(θ*|θₜ)])
   c) 以概率α接受θ*：
      - 接受：θₜ₊₁ = θ*
      - 拒绝：θₜ₊₁ = θₜ
3. 返回样本链{θ₁, θ₂, ..., θₜ}
```

**关键特性**：
- ✅ 最终收敛到真实后验分布
- ✅ 无需归一化常数
- ✅ 实现简单

**调节参数**：
- 提议分布标准差
- 燃烧期长度
- 稀疏化间隔

### 对称提议分布

当使用对称提议分布（如正态分布）时：
```python
q(θ*|θₜ) = q(θₜ|θ*)
```

接受概率简化为：
```python
α = min(1, p(θ*|D) / p(θₜ|D))
```

这就是**Metropolis算法**。

## 似然函数

### 正态似然

假设观测误差为独立正态分布：
```python
h_obs,i ~ N(h_sim,i(θ), σ²)
```

似然函数：
```python
p(D|θ) = Π N(h_obs,i | h_sim,i(θ), σ²)
```

对数似然：
```python
log p(D|θ) = -n/2 log(2πσ²) - Σ(h_obs - h_sim)² / (2σ²)
```

### 误差方差

**已知σ²**：作为给定常数

**未知σ²**：作为额外参数推断
```python
θ_augmented = [θ, σ²]
```

## 先验分布

### 无信息先验（均匀分布）

```python
p(θ) = 1/(b-a)    if a ≤ θ ≤ b
     = 0          otherwise
```

**特点**：
- 让数据主导推断
- 适合无先验知识时
- 需指定合理范围

### 信息性先验（正态分布）

```python
p(θ) ~ N(μ_prior, σ_prior²)
```

**特点**：
- 融合专家知识
- 正则化效果
- 减小不确定性

### 共轭先验

特殊的先验-似然组合，使后验具有闭式解。

例：正态似然 + 正态先验 → 正态后验

## 后验分析

### 点估计

**后验均值**（最常用）：
```python
E[θ|D] = ∫ θ p(θ|D) dθ
```

**后验中位数**：
```python
Median[θ|D]
```

**后验众数（MAP）**：
```python
arg max p(θ|D)
```

### 区间估计

**95% 可信区间**：
```python
P(θ_lower ≤ θ ≤ θ_upper | D) = 0.95
```

通常使用百分位数：
```python
θ_lower = 2.5th percentile
θ_upper = 97.5th percentile
```

### 预测分布

对于新数据点y_new：
```python
p(y_new|D) = ∫ p(y_new|θ) p(θ|D) dθ
```

**实现**：
1. 从后验抽取参数样本θᵢ
2. 对每个θᵢ，从p(y_new|θᵢ)采样
3. 收集所有y_new样本

**包含**：
- 参数不确定性
- 观测噪声

## MCMC诊断

### 收敛诊断

**1. 链迹图（Trace Plot）**
- 观察链是否"毛毛虫"状
- 检查是否稳定
- 识别燃烧期

**2. 自相关图**
- 检查样本独立性
- 决定稀疏化间隔

**3. Gelman-Rubin统计量（R-hat）**
- 需要多条独立链
- R-hat ≈ 1: 收敛
- R-hat > 1.1: 未充分收敛

### 接受率调节

**目标接受率**：
- 1维：~0.44
- 多维：~0.234
- 实践中：0.2-0.5 均可接受

**调节方法**：
- 接受率过低（< 0.1）：减小提议标准差
- 接受率过高（> 0.7）：增大提议标准差

### 有效样本数

考虑自相关后的有效独立样本数：
```python
n_eff = n_samples / (1 + 2Σρₖ)
```

其中ρₖ是滞后k的自相关系数。

## 模型选择

### DIC（偏差信息准则）

```python
DIC = D̄ + p_D
```

其中：
- **D̄**: 后验均值处的偏差
- **p_D**: 有效参数数量

**解释**：
- DIC = 拟合 + 复杂度惩罚
- DIC越小越好
- 用于比较不同模型

### WAIC（广泛适用信息准则）

更一般的信息准则，优于DIC。

## 运行代码

```bash
cd code/examples/case_08
python3 case_08_bayesian.py
```matlab

**注意**：MCMC采样需要较长时间（几分钟）。

## 输出结果

程序将生成：

1. **case_08_trace_plots.png**: MCMC链迹图
2. **case_08_posterior_distributions.png**: 后验分布直方图
3. **case_08_parameter_correlations.png**: 参数相关性散点图
4. **case_08_prediction_uncertainty.png**: 预测不确定性
5. **case_08_log_posterior_history.png**: 对数后验演化

## 预期结果

### 后验统计量

| 参数 | 真值 | 后验均值 | 后验标准差 | 95% CI |
|------|------|---------|-----------|--------|
| K | 10.0 | ~10.0 | ~0.3 | [9.4, 10.6] |
| h_left | 20.0 | ~20.0 | ~0.15 | [19.7, 20.3] |
| h_right | 10.0 | ~10.0 | ~0.15 | [9.7, 10.3] |

### MCMC性能

- **接受率**: ~0.30（良好）
- **有效样本数**: ~1,500
- **计算时间**: ~2-3分钟

### 与L-M对比

- 点估计非常接近
- 贝叶斯提供完整不确定性
- L-M计算速度快~100倍

## 实验探索

### 实验1：先验影响

尝试不同先验：
```python
# 强信息先验
prior_params = {
    'mean': np.array([12.0, 20.0, 10.0]),
    'std': np.array([1.0, 0.5, 0.5])
}
```python

**观察**：
- 强先验拉后验向先验
- 弱先验让数据主导
- 数据越多，先验影响越小

### 实验2：MCMC参数调节

改变提议标准差：
```python
# 过小
proposal_std = np.array([0.1, 0.05, 0.05])  # 接受率高，收敛慢

# 过大
proposal_std = np.array([5.0, 2.0, 2.0])    # 接受率低，探索不充分

# 适中
proposal_std = np.array([0.5, 0.2, 0.2])    # 最优
```python

**观察**：
- 提议标准差影响接受率
- 接受率影响收敛速度
- 需要平衡探索和利用

### 实验3：燃烧期长度

改变燃烧期：
```python
burn_in = 1000   # 短：可能未充分收敛
burn_in = 5000   # 中等：通常足够
burn_in = 10000  # 长：保守但浪费
```python

**观察**：
- 通过链迹图判断
- 链稳定后即可停止燃烧期

### 实验4：多链诊断

运行多条独立链：
```python
chains = []
for i in range(3):
    result = metropolis_hastings(
        initial_params=random_initial,
        ...
    )
    chains.append(result['chain_burned'])

R_hat = gelman_rubin_diagnostic(chains)
```python

**观察**：
- R-hat接近1表示收敛
- 多链更可靠

### 实验5：观测噪声影响

改变观测误差：
```python
sigma_obs = 0.01  # 小噪声：后验尖锐
sigma_obs = 0.5   # 大噪声：后验宽泛
```python

**观察**：
- 噪声越大，不确定性越大
- 后验标准差 ∝ σ_obs

## 常见问题

### Q1: 为什么使用贝叶斯方法？

**A**:
**优势**：
1. 完整的不确定性量化
2. 自然融合先验知识
3. 小样本情况更稳健
4. 概率解释直观

**劣势**：
1. 计算成本高
2. 需要选择先验
3. MCMC需要调参
4. 收敛诊断复杂

### Q2: 如何选择先验分布？

**A**:

**无先验知识**：
- 使用无信息先验（均匀、Jeffreys）
- 宽泛的正态分布

**有专家知识**：
- 信息性正态先验
- 基于历史数据

**原则**：
- 先验应可防御（可解释）
- 可做敏感性分析
- 让数据主导（弱先验）

### Q3: 如何判断MCMC收敛？

**A**:

**必做检查**：
1. ✅ 链迹图平稳
2. ✅ 多链R-hat < 1.1
3. ✅ 足够的有效样本数（> 1000）

**建议检查**：
4. 自相关快速衰减
5. 后验分布合理
6. 不同初值得到相似后验

### Q4: 贝叶斯vs最大似然的区别？

**A**:

**最大似然（MLE）**：
```
θ_MLE = arg max p(D|θ)
```python
- 点估计
- 频率学派
- 快速计算

**最大后验（MAP）**：
```
θ_MAP = arg max p(θ|D) = arg max [p(D|θ)p(θ)]
```python
- 点估计
- 包含先验
- 当先验均匀时，MAP = MLE

**全贝叶斯**：
```
完整后验分布 p(θ|D)
```python
- 分布估计
- 完整不确定性
- MCMC采样

### Q5: 如何加速MCMC？

**A**:

**方法**：
1. **并行链**：多核同时运行
2. **更好的采样器**：HMC、NUTS
3. **降维**：识别不重要参数
4. **初值优化**：从MLE开始
5. **自适应MCMC**：自动调节提议分布

**实践**：
- 先用优化找好初值
- 调节提议标准差达到最优接受率
- 使用专业库（PyMC3、Stan）

## 数学推导补充

### 后验推导

**从贝叶斯定理**：
```
p(θ|D) = p(D|θ)p(θ) / p(D)
```python

**对数后验**：
```
log p(θ|D) = log p(D|θ) + log p(θ) - log p(D)
             ↑             ↑           ↑
           似然          先验        常数
```python

**MCMC只需相对概率**：
```
p(θ*|D) / p(θₜ|D) = exp[log p(D|θ*) + log p(θ*) - 
                         log p(D|θₜ) - log p(θₜ)]
```python

不需要p(D)！

### 正态似然推导

**假设**：
```
h_obs,i = h_sim,i(θ) + εᵢ
εᵢ ~ N(0, σ²) i.i.d.
```python

**联合概率**：
```
p(D|θ) = Π (1/√(2πσ²)) exp[-(h_obs,i - h_sim,i)²/(2σ²)]
```python

**对数似然**：
```
log p(D|θ) = -n/2 log(2πσ²) - Σ(h_obs - h_sim)²/(2σ²)
           = const - RSS/(2σ²)
```python

其中RSS是残差平方和。

## 代码结构

```python
# 1. 定义对数后验
def log_posterior(params):
    log_prior = compute_log_prior(params)
    if log_prior == -inf:
        return -inf
    
    sim = forward_model(params)
    log_lik = compute_log_likelihood(obs, sim, sigma)
    
    return log_lik + log_prior

# 2. MCMC采样
result = metropolis_hastings(
    forward_model=my_model,
    initial_params=p0,
    observations=data,
    sigma=sigma_obs,
    prior_type='uniform',
    prior_params={'bounds': bounds},
    n_iterations=20000,
    burn_in=5000
)

# 3. 后验分析
posterior_mean = result['posterior_mean']
posterior_ci = [result['posterior_ci_lower'],
                result['posterior_ci_upper']]

# 4. 预测
predictions = predictive_distribution(
    result['chain_burned'],
    forward_model,
    sigma_obs
)
```

## 延伸阅读

1. Gelman, A., et al. (2013). *Bayesian Data Analysis* (3rd ed.). Chapman and Hall/CRC.

2. Brooks, S., et al. (2011). *Handbook of Markov Chain Monte Carlo*. Chapman and Hall/CRC.

3. Kruschke, J. (2014). *Doing Bayesian Data Analysis*. Academic Press.

4. McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press.

## 下一步

完成本案例后，继续学习：
- **案例9**：敏感性分析深入
- **案例10**：不确定性量化

或者深入贝叶斯方法：
- 高级MCMC（HMC、NUTS）
- 变分推断
- 贝叶斯模型选择
- 层次贝叶斯模型
