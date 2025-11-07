# 案例6: 参数辨识方法

## 📋 案例概述

**工程背景**:
光伏系统建模需要准确的参数,但厂商数据往往不够精确。参数辨识技术可以:
- 验证新组件参数
- 现场测试获取实际参数
- 跟踪老化参数变化
- 提升模型精度

**学习目标**:
1. 掌握参数辨识原理
2. 学习多种辨识方法
3. 理解参数物理意义
4. 评估辨识精度

---

## 🔬 理论基础

### 单二极管模型参数

**5个关键参数**:
```
Iph - 光生电流 (A)
I0  - 反向饱和电流 (A)
Rs  - 串联电阻 (Ω)
Rsh - 并联电阻 (Ω)  
n   - 理想因子
```

**模型方程**:
```
I = Iph - I0[exp((V+I*Rs)/(n*Vt)) - 1] - (V+I*Rs)/Rsh
```

### 辨识方法分类

**1. 解析法**:
- 基于关键点(Isc, Voc, Vmp, Imp)
- 计算简单快速
- 精度有限

**2. 优化法**:
- 最小二乘法
- 非线性优化
- 精度高,需要迭代

**3. 智能算法**:
- 遗传算法
- 粒子群算法
- 全局搜索能力强

---

## 💻 代码示例

### 1. 关键点法(解析法)

```python
from code.models.pv_identification import ParameterExtractor

# 创建提取器
extractor = ParameterExtractor()

# 从关键点提取参数
params = extractor.extract_from_key_points(
    Isc=8.0,      # 短路电流
    Voc=0.6,      # 开路电压
    Imp=7.5,      # MPP电流
    Vmp=0.48,     # MPP电压
    T=298.15,     # 温度(K)
    Ns=1          # 串联数
)

print(f"Iph = {params['Iph']:.6f} A")
print(f"I0  = {params['I0']:.3e} A")
print(f"Rs  = {params['Rs']:.6f} Ω")
print(f"Rsh = {params['Rsh']:.3f} Ω")
print(f"n   = {params['n']:.3f}")
```

### 2. 优化法(曲线拟合)

```python
# 准备测量数据
V_measured = np.array([...])  # 电压测量值
I_measured = np.array([...])  # 电流测量值

# 提取参数(最小二乘法)
result = extractor.extract_from_curve(
    V_measured,
    I_measured,
    T=298.15,
    Ns=1,
    method='least_squares'  # 或 'minimize', 'curve_fit'
)

print(f"提取参数:")
for key in ['Iph', 'I0', 'Rs', 'Rsh', 'n']:
    print(f"  {key} = {result[key]}")

print(f"\n拟合质量:")
print(f"  RMSE = {result['rmse']:.6f} A")
print(f"  R²   = {result['r2']:.6f}")
```

### 3. 方法对比

```python
from code.models.pv_identification import ParameterComparator

# 创建对比器
comparator = ParameterComparator()

# 对比多种方法
results = comparator.compare_methods(
    V_measured,
    I_measured,
    T=298.15,
    Ns=1
)

# 打印对比
for method, result in results.items():
    if result and 'rmse' in result:
        print(f"{method}: RMSE={result['rmse']:.6f}, R²={result['r2']:.6f}")
```

### 4. 精度评估

```python
# 评估参数精度
accuracy = comparator.evaluate_accuracy(
    params=result,  # 提取的参数
    V_measured=V_measured,
    I_measured=I_measured
)

print(f"误差指标:")
print(f"  MAE  = {accuracy['mae']:.6f} A")
print(f"  RMSE = {accuracy['rmse']:.6f} A")
print(f"  MAPE = {accuracy['mape']:.3f} %")
print(f"  R²   = {accuracy['r2']:.6f}")
```

---

## 📊 方法对比

| 方法 | 优点 | 缺点 | 精度 | 速度 | 推荐场景 |
|------|------|------|------|------|----------|
| 关键点法 | 简单快速 | 精度有限 | 中 | 极快 | 快速估算 |
| 最小二乘 | 精度高 | 需要迭代 | 高 | 快 | **推荐** |
| 非线性优化 | 精度高 | 可能局部最优 | 高 | 中 | 精密场合 |
| 曲线拟合 | 精度高 | 需好初值 | 高 | 中 | 数据充足 |
| 遗传算法 | 全局搜索 | 计算慢 | 高 | 慢 | 复杂情况 |

---

## 🎯 现场测试方法

### 测试设备

**必备**:
- I-V曲线测试仪
- 辐照度计
- 温度计
- 数据采集器

**可选**:
- 可调负载
- 示波器
- 记录仪

### 测试步骤

```
步骤1: 环境准备
  → 选择晴朗天气
  → 辐照度 >800 W/m²
  → 避开遮挡

步骤2: 设备连接
  → 连接I-V测试仪
  → 安装温度传感器
  → 校准辐照度计

步骤3: 数据采集
  → 测量I-V曲线(>50点)
  → 记录温度
  → 记录辐照度

步骤4: 参数辨识
  → 导入测量数据
  → 运行辨识程序
  → 评估拟合质量

步骤5: 结果验证
  → 对比标称值
  → 检查参数合理性
  → 重复测试确认
```

---

## 💡 参数物理意义

### 各参数含义

**Iph (光生电流)**:
- 与辐照度成正比
- Iph ≈ Isc (略大)
- 反映光电转换能力

**I0 (饱和电流)**:
- 温度敏感
- 数量级: 10⁻⁹ ~ 10⁻¹² A
- 影响Voc

**Rs (串联电阻)**:
- 接触电阻 + 引线电阻
- 典型值: 0.001 ~ 0.01 Ω
- 影响FF和Pmp

**Rsh (并联电阻)**:
- 漏电流路径
- 典型值: >1000 Ω
- 影响低压区特性

**n (理想因子)**:
- 反映复合机制
- 理想值: 1.0
- 典型值: 1.0 ~ 2.0

### 参数与性能关系

```
Rs ↑  → FF ↓, Pmp ↓  (串联电阻增大降低性能)
Rsh ↓ → FF ↓, Voc ↓ (并联电阻减小降低性能)
n ↑   → FF ↓, Voc ↓ (理想因子增大降低性能)
```

---

## 📝 思考题

1. **为什么参数辨识比使用厂商数据更准确?**

2. **如何判断辨识结果是否可信?**

3. **现场测试应注意哪些环境因素?**

4. **老化后哪些参数会显著变化?**

---

## 📚 作业

### 基础题

**作业1**: 用关键点法计算组件参数。

**作业2**: 对比不同优化方法的精度和速度。

**作业3**: 分析参数对I-V曲线形状的影响。

### 进阶题

**作业4**: 实现基于遗传算法的参数辨识。

**作业5**: 开发在线参数跟踪系统。

**作业6**: 研究温度/辐照度对参数的影响规律。

---

## ✅ 检查清单

完成本案例后,你应该能够:

- [ ] 理解单二极管模型5个参数
- [ ] 使用关键点法快速估算
- [ ] 使用优化法精确提取参数
- [ ] 评估辨识精度
- [ ] 进行现场I-V测试
- [ ] 判断参数合理性
- [ ] 分析参数物理意义

---

**案例6完成!** 🎉  
**🏆 阶段一(基础建模)全部完成!** 

下一步: [阶段二 - MPPT控制技术](../../README.md)
