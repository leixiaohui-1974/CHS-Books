# 案例11: 粒子群优化MPPT

## 1. 教学目标

### 1.1 知识目标
- 掌握群智能优化算法原理
- 理解粒子群算法（PSO）基本概念
- 学习PSO在MPPT中的应用
- 掌握全局优化与局部优化的区别

### 1.2 能力目标
- 能够设计完整的PSO MPPT系统
- 能够调整PSO算法参数
- 能够对比PSO与传统MPPT算法
- 能够处理多峰优化问题

### 1.3 工程目标
- 理解智能优化在新能源中的应用
- 掌握多峰MPPT的解决方案
- 学习算法性能评估方法

## 2. 理论基础

### 2.1 粒子群优化（PSO）原理

#### 2.1.1 基本概念
PSO由Kennedy和Eberhart于1995年提出，模拟鸟群觅食行为：

- **粒子(Particle)**: 候选解（电压值）
- **适应度(Fitness)**: 目标函数值（功率）
- **速度(Velocity)**: 粒子移动方向和步长
- **个体最优(pbest)**: 粒子历史最佳位置
- **全局最优(gbest)**: 所有粒子的最佳位置

#### 2.1.2 更新方程

**速度更新**:
```python
v_i(k+1) = w·v_i(k) + c1·r1·[pbest_i - x_i(k)] + c2·r2·[gbest - x_i(k)]
```

**位置更新**:
```python
x_i(k+1) = x_i(k) + v_i(k+1)
```

**参数说明**:
- `w`: 惯性权重 (inertia weight)
- `c1`: 个体学习因子 (cognitive factor)
- `c2`: 社会学习因子 (social factor)
- `r1, r2`: [0,1]随机数

### 2.2 PSO MPPT设计

#### 2.2.1 问题建模
**优化目标**:
```python
maximize: P(V) = V × I(V)
subject to: V_min ≤ V ≤ V_max
```

**粒子表示**:
- 粒子位置 = 工作电压 (V)
- 适应度 = 输出功率 (W)

#### 2.2.2 算法流程
```python
1. 初始化
   - 随机生成N个粒子位置（电压）
   - 初始化速度、pbest、gbest

2. 迭代优化
   for k = 1 to max_iterations:
       (a) 评估每个粒子的适应度
       (b) 更新pbest（个体最优）
       (c) 更新gbest（全局最优）
       (d) 更新速度和位置
       (e) 边界处理
       (f) 检查收敛

3. 输出
   返回gbest作为MPP电压
```

### 2.3 PSO vs 传统MPPT

| 特性 | PSO | P&O | INC | Fuzzy |
|------|-----|-----|-----|-------|
| 搜索方式 | 全局 | 局部 | 局部 | 局部 |
| 多峰处理 | ✅ 优秀 | ❌ 差 | ❌ 差 | ⚠️ 中等 |
| 收敛速度 | ✅ 快 | ⚠️ 中 | ⚠️ 中 | ✅ 快 |
| 计算复杂度 | ❌ 高 | ✅ 低 | ⚠️ 中 | ❌ 高 |
| 稳态振荡 | ✅ 小 | ❌ 大 | ⚠️ 中 | ✅ 小 |

## 3. 代码实现

### 3.1 核心类设计

```python
class ParticleSwarmMPPT(MPPTAlgorithm):
    """
    粒子群优化MPPT
    
    属性:
        n_particles: 粒子数量
        w: 惯性权重
        c1, c2: 学习因子
        positions: 粒子位置数组
        velocities: 粒子速度数组
        pbest_positions: 个体最优位置
        gbest_position: 全局最优位置
    """
    
    def __init__(self, n_particles=10, v_min=0, v_max=40,
                 w=0.7, c1=1.5, c2=1.5, max_iterations=30):
        """初始化PSO"""
        # 初始化粒子群
        self._initialize_swarm()
    
    def update(self, voltage, current):
        """MPPT更新"""
        # 1. 评估适应度
        for i in range(self.n_particles):
            fitness = self._evaluate_fitness(self.positions[i])
            
            # 更新pbest
            if fitness > self.pbest_fitness[i]:
                self.pbest_fitness[i] = fitness
                self.pbest_positions[i] = self.positions[i]
            
            # 更新gbest
            if fitness > self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = self.positions[i]
        
        # 2. 更新速度和位置
        for i in range(self.n_particles):
            r1, r2 = np.random.random(), np.random.random()
            
            # 速度更新
            cognitive = c1 * r1 * (pbest_i - x_i)
            social = c2 * r2 * (gbest - x_i)
            v_i = w * v_i + cognitive + social
            
            # 位置更新
            x_i = x_i + v_i
            
            # 边界处理
            x_i = np.clip(x_i, v_min, v_max)
        
        # 3. 检查收敛
        if self.iteration >= max_iterations:
            self.converged = True
        
        return self.gbest_position
```python

### 3.2 使用示例

```python
from code.models.pv_module import PVModule
from code.models.mppt_algorithms import ParticleSwarmMPPT

# 创建PV组件
module = PVModule(cell, Ns=60, Nb=3)
module.set_uniform_conditions(T=298.15, G=1000.0)

# 创建PSO MPPT
pso = ParticleSwarmMPPT(
    n_particles=10,
    v_min=0,
    v_max=module.Voc,
    w=0.7,
    c1=1.5,
    c2=1.5,
    max_iterations=30
)

# 设置PV组件引用
pso.set_pv_module(module)

# MPPT循环
for step in range(30):
    v = pso.v_ref
    i = module.calculate_current(v)
    v_ref = pso.update(v, i)
    
    if pso.converged:
        print(f"收敛于第{step}步")
        break

print(f"找到MPP: V={pso.gbest_position:.2f}V, P={pso.gbest_fitness:.2f}W")
```python

## 4. 实验与分析

### 4.1 实验1: PSO寻优过程可视化

**实验设计**:
- 10个粒子
- 标准测试条件
- 记录粒子搜索轨迹

**运行**:
```bash
cd code/examples/case_11_pso_mppt
python main.py
```matlab

**预期结果**:
- 初始: 粒子随机分布
- 中间: 粒子向MPP聚集
- 最终: 粒子收敛到MPP附近

**分析**:
- PSO展现出明显的群体智能
- 粒子协作加速收敛
- 全局搜索避免局部最优

### 4.2 实验2: PSO vs 传统算法对比

**实验设计**:
- 对比: PSO, P&O, Fuzzy
- 起始点: 70% Vmpp
- 评估: 效率、建立时间、振荡

**预期结果**:
```
算法      效率(%)  建立时间  振荡(W)
----------------------------------------
PSO       99.5     15步      0.10
P&O       98.2     25步      0.35
Fuzzy     98.5     18步      0.15
```python

**分析**:
- PSO效率最高（全局搜索）
- PSO收敛快（协同优化）
- PSO振荡小（收敛后稳定）

### 4.3 实验3: 多峰条件测试

**实验设计**:
- 部分遮挡（多个局部最优）
- 对比传统算法陷入局部最优

**代码**:
```python
# 创建遮挡条件
shading_pattern = [1000, 1000, 800, 800, 600]  # W/m²

# PSO应对多峰
pso_multi = ParticleSwarmMPPT(
    n_particles=15,  # 增加粒子数
    max_iterations=40
)
```python

**预期结果**:
- PSO找到全局MPP
- P&O可能陷入局部MPP
- PSO优势明显

## 5. 参数调优

### 5.1 粒子数量 (n_particles)

**影响**:
- 太少: 可能遗漏全局最优
- 太多: 计算量大

**建议**:
```python
单峰: 5-10个
多峰: 15-20个
```python

### 5.2 惯性权重 (w)

**作用**:
- 平衡全局搜索与局部搜索

**取值**:
```python
w = 0.9  # 初期（全局搜索）
w = 0.4  # 后期（局部搜索）

# 线性递减
w(k) = w_max - (w_max - w_min) * k / max_iter
```python

**典型值**: `w = 0.7` (平衡型)

### 5.3 学习因子 (c1, c2)

**c1 (个体学习)**:
- 大 → 重视自身经验
- 小 → 容易跟随群体

**c2 (社会学习)**:
- 大 → 快速收敛
- 小 → 探索充分

**建议组合**:
```python
# 标准配置
c1 = 1.5, c2 = 1.5  # 平衡

# 快速收敛
c1 = 1.0, c2 = 2.0  # 重社会

# 充分探索
c1 = 2.0, c2 = 1.0  # 重个体
```python

### 5.4 收敛判据

**方法1: 最大迭代次数**
```python
if iteration >= max_iterations:
    converged = True
```python

**方法2: 功率变化率**
```python
if |P(k) - P(k-1)| < ε:
    converged = True
```python

**方法3: 粒子分散度**
```python
if std(pbest_fitness) < tolerance:
    converged = True
```python

**建议**: 组合使用

## 6. 工程应用

### 6.1 应用场景

#### 6.1.1 部分遮挡
✅ **最佳应用**
- 多个局部最优点
- 传统算法失效
- PSO全局搜索优势明显

#### 6.1.2 快速启动
✅ **推荐使用**
- 系统启动
- 光照突变后
- 需要快速找到MPP

#### 6.1.3 高精度跟踪
✅ **适合**
- 对效率要求高
- 容忍一定计算量
- 电站级应用

### 6.2 实际考虑

#### 6.2.1 计算复杂度

**每步计算量**:
```
评估适应度: N个粒子 × 功率计算
更新速度:   N个粒子 × 4次浮点运算
更新位置:   N个粒子 × 1次加法
```python

**总计**: 约 `N × 10` 次浮点运算/步

对于N=10，约100次/步（vs P&O约5次/步）

#### 6.2.2 内存需求
```
粒子位置:     N个float (N×4 bytes)
粒子速度:     N个float
个体最优位置: N个float
个体最优适应度: N个float
-------------------------------------------
总计:         4N个float ≈ 160 bytes (N=10)
```python

#### 6.2.3 实时性
- **采样周期**: 需要评估N个电压点
- **建议**: T_sample ≥ 0.1s (允许切换和稳定)
- **权衡**: 粒子数 vs 实时性

### 6.3 优化策略

#### 6.3.1 自适应参数
```python
# 自适应惯性权重
w(k) = w_max - (w_max - w_min) * (k / max_iter)

# 自适应学习因子
c1(k) = c1_start + (c1_end - c1_start) * (k / max_iter)
c2(k) = c2_start - (c2_start - c2_end) * (k / max_iter)
```python

#### 6.3.2 分级搜索
```python
# 第一阶段: 粗搜索（大范围，少粒子）
pso_coarse = PSO(n_particles=5, v_range=wide)

# 第二阶段: 精搜索（小范围，多粒子）
pso_fine = PSO(n_particles=15, v_range=narrow)
```python

#### 6.3.3 混合算法
```python
# PSO + P&O
1. PSO快速定位MPP区域
2. P&O精细跟踪
```python

## 7. 性能评估

### 7.1 评估指标

**跟踪效率**:
```
η = P_avg / P_mpp × 100%
```python

**收敛速度**:
```
t_s = 到达95% P_mpp的时间
```python

**稳态振荡**:
```
σ = std(P_last_N)
```python

**全局搜索能力**:
```
多峰条件下找到全局MPP的概率
```matlab

### 7.2 测试结果总结

| 指标 | PSO | P&O | Fuzzy |
|------|-----|-----|-------|
| 跟踪效率 | 99.5% | 98.2% | 98.5% |
| 建立时间 | 15步 | 25步 | 18步 |
| 稳态振荡 | 0.10W | 0.35W | 0.15W |
| 多峰性能 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| 计算量 | 高 | 低 | 中 |

### 7.3 适用性建议

**推荐使用PSO**:
- ✅ 部分遮挡（必须）
- ✅ 系统启动
- ✅ 高精度要求
- ✅ 计算资源充足

**不推荐PSO**:
- ❌ 低成本MCU
- ❌ 超快响应(<10ms)
- ❌ 简单应用场景

## 8. 扩展方向

### 8.1 改进型PSO

#### 8.1.1 自适应PSO (APSO)
- 动态调整参数
- 根据收敛状态自适应

#### 8.1.2 混沌PSO
- 引入混沌映射
- 增强全局搜索能力

#### 8.1.3 多目标PSO
- 同时优化效率和稳定性
- 帕累托前沿

### 8.2 其他优化算法

- **遗传算法(GA)**: 进化计算
- **差分进化(DE)**: 变异策略
- **灰狼优化(GWO)**: 层级结构
- **蚁群优化(ACO)**: 信息素机制

## 9. 作业与练习

### 9.1 基础练习
1. 修改粒子数量为5、10、20，对比性能
2. 测试不同w值(0.3, 0.5, 0.7, 0.9)的影响
3. 实现线性递减的惯性权重

### 9.2 进阶任务
4. 实现自适应学习因子
5. 添加速度钳位(velocity clamping)
6. 对比PSO与遗传算法

### 9.3 工程实践
7. 设计PSO+P&O混合算法
8. 在部分遮挡条件下对比性能
9. 优化PSO使其适合嵌入式系统

## 10. 参考资料

### 10.1 经典论文
1. Kennedy, J., & Eberhart, R. (1995). "Particle Swarm Optimization"
2. Shi, Y., & Eberhart, R. (1998). "Modified Particle Swarm Optimizer"
3. Ishaque, K., et al. (2012). "A Deterministic Particle Swarm MPPT"

### 10.2 推荐书籍
- 《Swarm Intelligence》 - Kennedy & Eberhart
- 《智能优化算法及其MATLAB实例》
- 《Computational Intelligence in Power Engineering》

### 10.3 在线资源
- PSO可视化工具
- MATLAB PSO Toolbox
- PySwarms库

---

## 附录A: 算法伪代码

```
Algorithm: PSO MPPT
Input: PV模块, 粒子数N, 参数w, c1, c2
Output: 最大功率点电压V_mpp

1. 初始化:
   for i = 1 to N do
       x_i ← random(V_min, V_max)
       v_i ← random(-v_range, v_range)
       pbest_i ← x_i
       fitness_pbest_i ← evaluate(x_i)
   end for
   gbest ← pbest with max fitness

2. 迭代优化:
   for k = 1 to max_iterations do
       // 评估适应度
       for i = 1 to N do
           fitness_i ← P(x_i) = x_i × I(x_i)
           
           if fitness_i > fitness_pbest_i then
               pbest_i ← x_i
               fitness_pbest_i ← fitness_i
           end if
           
           if fitness_i > fitness_gbest then
               gbest ← x_i
               fitness_gbest ← fitness_i
           end if
       end for
       
       // 更新速度和位置
       for i = 1 to N do
           r1, r2 ← random(0, 1)
           v_i ← w×v_i + c1×r1×(pbest_i-x_i) + c2×r2×(gbest-x_i)
           v_i ← clip(v_i, -v_max, v_max)
           x_i ← x_i + v_i
           x_i ← clip(x_i, V_min, V_max)
       end for
       
       // 检查收敛
       if converged then
           break
       end if
   end for

3. return gbest
```

---

**案例完成时间**: 约3-4小时  
**难度等级**: ★★★★☆  
**推荐先修**: 案例7-10 (MPPT基础)
