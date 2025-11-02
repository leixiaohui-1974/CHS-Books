# 案例4：Streeter-Phelps溶解氧模型

## 案例背景

某城市河段接纳污水处理厂尾水，初始BOD为30 mg/L，初始DO为6 mg/L。河流流速0.3 m/s，平均水深1.5 m，水温20°C。预测河段溶解氧变化，评估是否会出现缺氧（DO < 4 mg/L）。

**水力参数**:
- 流速: u = 0.3 m/s
- 水深: H = 1.5 m
- 水温: T = 20°C
- 饱和DO: DOs = 9.09 mg/L

**水质参数**:
- 初始BOD: L₀ = 30 mg/L
- 初始DO: DO₀ = 6 mg/L
- 初始亏损: D₀ = 9.09 - 6 = 3.09 mg/L
- BOD降解系数: kd = 0.2 day⁻¹ (20°C)
- 复氧系数: ka = 0.4 day⁻¹ (20°C)

## 学习目标

1. 理解DO-BOD的相互作用
2. 掌握Streeter-Phelps方程
3. 理解氧垂曲线（Oxygen Sag Curve）
4. 学会计算临界点
5. 掌握复氧系数的计算

## 核心理论

### 1. Streeter-Phelps方程

**历史背景**: 
1925年，Streeter和Phelps提出了描述河流DO-BOD关系的经典模型，这是环境工程领域最重要的方程之一。

**基本假设**:
1. 稳态河流（流速恒定）
2. 一维模型（忽略横向和纵向混合）
3. BOD一阶降解
4. 复氧与DO亏损成正比

**控制方程**:

```
BOD降解:
dL/dt = -kd · L

DO亏损变化:
dD/dt = kd · L - ka · D
```

其中：
- L: BOD浓度 (mg/L)
- D: DO亏损 = DOs - DO (mg/L)
- kd: BOD降解系数 (day⁻¹)
- ka: 复氧系数 (day⁻¹)
- DOs: 饱和溶解氧 (mg/L)

### 2. 解析解

**BOD浓度**:
```
L(t) = L₀ · exp(-kd · t)
```

**DO亏损** (ka ≠ kd):
```
D(t) = (kd·L₀)/(ka-kd) · [exp(-kd·t) - exp(-ka·t)] + D₀·exp(-ka·t)
```

**特殊情况** (ka = kd):
```
D(t) = kd · L₀ · t · exp(-kd·t) + D₀ · exp(-ka·t)
```

**DO浓度**:
```
DO(t) = DOs - D(t)
```

### 3. 氧垂曲线（Oxygen Sag Curve）

**物理意义**:
- 污水排放后，DO先下降（BOD消耗氧 > 大气复氧）
- 达到最低点（临界点）
- 然后逐渐恢复（大气复氧 > BOD消耗氧）

**临界点计算**:

临界点条件：dD/dt = 0

**临界时间** (ka ≠ kd):
```
tc = ln[ka/kd · (1 - D₀·(ka-kd)/(kd·L₀))] / (ka - kd)
```

**临界亏损**:
```
Dc = (kd·L₀)/ka · exp(-kd·tc)
```

**临界DO**:
```
DOc = DOs - Dc
```

### 4. 复氧系数

复氧是大气中氧气溶入水体的过程，主要受以下因素影响：
1. 水流速度（湍流强度）
2. 水深
3. 温度
4. 风速

**经验公式**:

**Owens公式** (浅水河流，H < 1m):
```
ka = 5.32 · u^0.67 / H^1.85
```

**Churchill公式** (大河):
```
ka = 5.026 · u / H^1.673
```

**O'Connor-Dobbins公式** (深水河流):
```
ka = 3.93 · u^0.5 / H^1.5
```

其中：
- u: 流速 (m/s)
- H: 水深 (m)
- ka: 20°C时的复氧系数 (day⁻¹)

### 5. 温度校正

**kd温度校正**:
```
kd(T) = kd(20°C) · θd^(T-20)
θd ≈ 1.047
```

**ka温度校正**:
```
ka(T) = ka(20°C) · θa^(T-20)
θa ≈ 1.024
```

**饱和DO温度校正** (淡水，0-30°C):
```
DOs(T) = 14.652 - 0.41022·T + 0.007991·T² - 0.000077774·T³
```

## 计算任务

### 任务1：基本S-P模型求解

使用解析解计算：
1. BOD随时间的变化
2. DO随时间的变化
3. 绘制氧垂曲线

**参数**:
- L₀ = 30 mg/L
- DO₀ = 6 mg/L
- kd = 0.2 day⁻¹
- ka = 0.4 day⁻¹
- T = 20°C

### 任务2：临界点分析

计算并分析：
1. 临界时间 tc
2. 临界DO浓度 DOc
3. 临界位置（结合流速）
4. 评估是否会缺氧（DO < 4 mg/L）

### 任务3：参数影响分析

分析以下参数的影响：
1. **L₀的影响**: 比较L₀ = 20, 30, 40 mg/L
2. **kd的影响**: 比较kd = 0.1, 0.2, 0.3 day⁻¹
3. **ka的影响**: 比较ka = 0.2, 0.4, 0.6 day⁻¹
4. **ka/kd比值的影响**: 自净能力指标

### 任务4：温度影响分析

计算不同温度下的DO变化：
1. 冬季（10°C）
2. 春秋（20°C）
3. 夏季（30°C）

分析：
- 温度对kd和ka的影响
- 温度对DOs的影响
- 综合效应

### 任务5：复氧系数计算

使用3种经验公式计算ka：
1. Owens公式
2. Churchill公式
3. O'Connor-Dobbins公式

比较结果差异，分析适用条件。

### 任务6：工程应用

**场景**: 污水处理厂排放标准制定

**任务**:
1. 计算最大允许BOD排放浓度（保证DOmin > 4 mg/L）
2. 计算所需河段长度（DO恢复到7 mg/L）
3. 制定分季节排放标准
4. 评估增加曝气设施的效果

## 使用方法

```bash
# 运行主程序
python main.py

# 运行扩展实验
python experiments.py
```

## 文件说明

- `main.py` - 主程序（S-P模型基本应用）
- `README.md` - 本文件

## 预期结果

### 氧垂曲线特征

**典型S-P曲线**:
1. **Zone 1 (降解区)**: DO快速下降
2. **Zone 2 (临界区)**: DO达到最低点
3. **Zone 3 (恢复区)**: DO逐渐恢复

**临界点位置**:
- 时间: tc ≈ 1-3 天
- 距离: xc = u × tc ≈ 25-80 km
- DO: DOc ≈ 4-6 mg/L

### 参数影响

**L₀增大** → DOc降低（污染加重）  
**kd增大** → tc提前，DOc降低  
**ka增大** → tc延后，DOc升高（自净能力增强）  
**温度升高** → kd和ka都增大，但DOs降低

### 工程标准

**DO水质标准**:
- I类水: DO ≥ 7.5 mg/L
- II类水: DO ≥ 6 mg/L
- III类水: DO ≥ 5 mg/L
- IV类水: DO ≥ 3 mg/L
- V类水: DO ≥ 2 mg/L

**鱼类生存要求**:
- 鲑鱼: DO ≥ 6 mg/L
- 一般鱼类: DO ≥ 4 mg/L
- 严重缺氧: DO < 2 mg/L（死鱼）

## 工程意义

### 1. 排放标准制定

- 根据河流自净能力制定BOD排放限值
- 确保下游DO满足水质标准
- 保护水生生态系统

### 2. 污水处理厂选址

- 避免在低ka河段（深、慢、冬季）排放
- 考虑下游敏感区域（取水口、渔场）
- 评估多个排放口的累积效应

### 3. 应急措施

- 预测污染事故影响范围
- 确定需要人工曝气的河段
- 制定应急响应方案

### 4. 生态修复

- 评估河道治理效果（增加ka）
- 优化河流形态（增加湍流）
- 设置曝气设施

## 关键概念

### BOD（Biochemical Oxygen Demand）
- 生化需氧量
- 表征有机物含量
- 微生物分解有机物消耗的氧量

### DO（Dissolved Oxygen）
- 溶解氧
- 水生生物呼吸必需
- 水质评价的关键指标

### DO亏损（Oxygen Deficit）
- D = DOs - DO
- 实际DO与饱和DO的差值
- S-P方程求解的主要变量

### 氧垂曲线（Oxygen Sag Curve）
- DO沿程变化曲线
- 先降后升的"U"型曲线
- 最低点是临界点

### 自净能力（Self-Purification Capacity）
- 河流恢复水质的能力
- 主要由ka/kd比值决定
- ka/kd > 1，自净能力强

### 临界点（Critical Point）
- DO最低点
- dD/dt = 0
- 评估污染最严重时刻

## 历史意义

**Streeter-Phelps模型**（1925）是环境工程领域的里程碑：

1. **第一个定量水质模型** - 开创了水质数学模型的先河
2. **实用性强** - 100年来一直在工程中应用
3. **理论基础** - 后续复杂模型的基础
4. **教学价值** - 理解DO-BOD关系的最佳案例

## 模型局限性

**S-P模型的假设限制**:
1. 忽略了光合作用产氧
2. 忽略了底泥耗氧
3. 忽略了硝化耗氧
4. 假设参数恒定
5. 一维简化

**改进方向**:
- 加入藻类光合作用
- 考虑底泥氧消耗（SOD）
- 考虑氮循环（硝化）
- 考虑二维/三维效应

## 参考资料

1. Streeter, H.W., & Phelps, E.B. (1925). A Study of the Pollution and Natural Purification of the Ohio River.
2. Chapra, S.C. (1997). Surface Water-Quality Modeling. McGraw-Hill.
3. Thomann, R.V., & Mueller, J.A. (1987). Principles of Surface Water Quality Modeling and Control.
4. Davis, M.L., & Masten, S.J. (2004). Principles of Environmental Engineering and Science.
5. Tchobanoglous, G., & Schroeder, E.D. (1985). Water Quality.

## 扩展阅读

**经典论文**:
- Streeter-Phelps原始论文（1925）
- O'Connor-Dobbins复氧公式（1958）
- Churchill复氧公式（1962）

**现代发展**:
- QUAL2K模型
- WASP模型
- Mike11水质模块
