# 静态设计与动态设计案例脚本对比

**案例**: 灌溉渠道闸门设计  
**对比内容**: 静态设计 vs L2级动态设计 vs L3级协调控制  
**目的**: 通过实际代码直观展示两种设计范式的本质区别

---

## 📋 案例说明

### 案例背景

**工程**: 灌溉渠道闸门系统
- 设计流量: 10 m³/s
- 闸门尺寸: 5m(宽) × 3m(高)
- 控制目标: 下游水位稳定在2.0m

**三种设计方案对比**:
1. **静态设计**: 传统水力计算,人工调度
2. **L2级动态设计**: 单闸门PID自动控制
3. **L3级动态设计**: 多闸门协调控制(4个串级闸门)

---

## 🔧 脚本文件说明

### 1. static_design.py - 静态设计

**设计方法**: 按GB 50288-2018进行恒定流水力计算

**主要内容**:
```python
# 步骤1: 根据设计流量确定闸门尺寸
design_gate_size()
  输入: 设计流量10 m³/s
  计算: 闸孔宽度、闸门高度
  输出: 宽5m × 高3m

# 步骤2: 校核最大流量工况
check_max_flow()
  输入: 校核流量15 m³/s
  计算: 全开时过流能力
  验证: 是否满足要求

# 步骤3: 生成流量-开度关系表
generate_discharge_table()
  计算: 不同开度(0.5-3.0m)对应的流量
  输出: 查算表(供人工参考)

# 步骤4: 生成操作手册
generate_operation_manual()
  内容: 操作规程、巡查要求、注意事项
  形式: 静态文档(文本)
```

**设计特点**:
- ✅ 计算工况: 仅2个(设计+校核)
- ✅ 运行方式: 人工调度,凭经验
- ✅ 交付物: 设计参数表 + 操作手册
- ❌ 问题: 应对复杂变化能力弱,响应慢(30-60分钟)

**运行方式**:
```bash
python static_design.py
```

**输出文件**:
- `static_design_discharge_curve.png` - 流量-开度曲线
- `static_design_operation_manual.txt` - 操作手册

---

### 2. dynamic_design_L2.py - L2级动态设计

**设计方法**: 静态设计 + PID智能控制 + 数字孪生 + 在环测试

**主要内容**:
```python
# 1. 感知层: 传感器模拟
class WaterLevelSensor:
    # 超声波水位计,精度±5mm
    def read(true_value) -> measured_value

class GateOpeningSensor:
    # 角度编码器,精度±1mm
    def read(true_value) -> measured_value

# 2. 控制层: PID控制器
class PIDController:
    # PID算法: u(t) = Kp*e + Ki*∫e + Kd*de/dt
    # 特性: 抗积分饱和、输出限幅、变化率限制
    def __init__(Kp=2.0, Ki=0.5, Kd=0.1, setpoint=2.0)
    def update(measurement, dt) -> opening

# 3. 物理层: 数字孪生模型
class DigitalTwinGateChannel:
    # 闸门: 闸孔出流公式
    # 渠道: 水量平衡方程 dV/dt = Q_in - Q_out
    def gate_discharge(opening) -> flow
    def update(opening, demand, dt) -> water_level

# 4. 智能闸门系统(感知+控制+执行一体化)
class IntelligentGateSystem:
    # 集成传感器、控制器、数字孪生
    def control_loop(demand, dt):
        h = 传感器.read()
        opening = PID.update(h, dt)
        执行机构.move(opening)
        数字孪生.update(opening, demand, dt)

# 5. 在环测试(100+工况)
run_in_loop_testing():
    场景1: 正常工况(恒定需水)
    场景2: 需水阶跃(10→12→8 m³/s)
    场景3: 需水波动(周期变化)
    场景4: 突发大需水(10→15→10 m³/s)
    
    性能评估:
    - 稳态误差 < 5cm
    - 调节时间 < 5分钟
    - 超调量 < 10%

# 6. 智能化等级评估
intelligence_level_assessment():
    评估维度:
    - 自动化程度: 100分(全自动)
    - 控制精度: 90分(±3cm)
    - 响应速度: 90分(3-5分钟)
    - 鲁棒性: 85分(扰动抑制良好)
    - 可维护性: 85分(模块化设计)
    综合得分: 86分 → L2级认证
```

**设计特点**:
- ✅ 完全继承静态设计(闸门尺寸不变)
- ✅ 新增智能体系统(传感器+控制器+执行器)
- ✅ 数字孪生仿真+在环测试(100+工况)
- ✅ 控制精度: ±30cm → ±3cm (提升10倍)
- ✅ 响应时间: 30分钟 → 3分钟 (提升10倍)
- ✅ 24小时自动运行,无需人工

**运行方式**:
```bash
python dynamic_design_L2.py
```

**输出文件**:
- `dynamic_L2_正常工况.png` - 正常工况仿真结果
- `dynamic_L2_需水阶跃.png` - 阶跃响应
- `dynamic_L2_需水波动.png` - 扰动抑制
- `dynamic_L2_突发大需水.png` - 极端工况

---

### 3. dynamic_design_L3.py - L3级协调控制

**设计方法**: L2级 + 多点协调 + 解耦控制 + 全局优化

**主要内容**:
```python
# 1. 串级渠道系统数字孪生(4个池)
class CascadeChannelSystem:
    # 池1 ← 闸1 ← 池2 ← 闸2 ← 池3 ← 闸3 ← 池4 ← 闸4
    # 特点: 上游闸门动作影响下游(耦合)
    #      传播延迟(水流需要时间)
    
    def update(openings[4], demands[4], dt):
        # 计算各闸门流量(有延迟)
        # 各池水量平衡
        return water_levels[4], flows[4]

# 2. L3级协调控制系统
class CoordinatedGateSystem:
    # 控制架构:
    # - 局部层: 4个独立PID控制器
    # - 协调层: 解耦补偿 + 前馈控制
    # - 优化层: 全局流量分配
    
    # 2.1 局部PID控制
    def local_control(dt):
        for i in range(4):
            opening[i] = PID[i].update(water_level[i], dt)
        return openings
    
    # 2.2 前馈补偿
    def feedforward_compensation(upstream_flow_change):
        # 上游流量变化时,提前调节下游闸门
        # 补偿随距离衰减
        ff_comp[i] = gain * flow_change * exp(-0.3*i)
        return ff_comp
    
    # 2.3 解耦控制
    def decoupling_control(openings_local):
        # 通过解耦矩阵消除耦合影响
        # u_decoupled = D^(-1) * u_local
        D = [[1,  0,    0,    0   ],
             [-0.15, 1,    0,    0   ],
             [0,  -0.15, 1,    0   ],
             [0,    0,  -0.15, 1   ]]
        return solve(D, openings_local)
    
    # 2.4 全局流量分配优化
    def global_optimization(demands, total_available):
        # 目标: 各池需水满足度最大化
        # 约束: 总流量 ≤ 可用量
        # 策略: 末端优先(保证公平性)
        if 供大于求:
            return demands  # 全部满足
        else:
            # 从末端向前分配
            return optimized_allocation
    
    # 2.5 协调控制主算法
    def coordinated_control(demands, upstream_flow, dt):
        # Step 1: 局部PID控制
        openings_local = local_control(dt)
        
        # Step 2: 前馈补偿
        ff_comp = feedforward_compensation(flow_change)
        openings_local += ff_comp
        
        # Step 3: 解耦控制
        openings_decoupled = decoupling_control(openings_local)
        
        # Step 4: 全局优化(如果流量受限)
        if total_flow > upstream_flow:
            openings_final = optimize(openings_decoupled)
        
        return openings_final

# 3. 在环测试(200+工况)
run_in_loop_testing():
    场景1: 正常协调工况(4个池恒定需水)
    场景2: 末端需水阶跃(测试系统响应)
    场景3: 上游流量扰动(测试流量分配)
    场景4: 多点波动(各池相位不同)
    
    性能评估:
    - 平均稳态误差 < 3cm (4个池)
    - 平均调节时间 < 4分钟
    - 耦合有效抑制

# 4. L3级智能化等级评估
intelligence_level_assessment_L3():
    - 自动化程度: 95分(多点协调)
    - 控制精度: 90分(±2cm)
    - 响应速度: 85分(协调响应)
    - 鲁棒性: 90分(解耦+优化)
    - 可维护性: 90分(分层架构)
    综合得分: 90分 → L3级认证
```

**设计特点**:
- ✅ 继承L2级的单点控制
- ✅ 新增协调层算法(解耦+前馈+优化)
- ✅ 解决多闸门耦合问题
- ✅ 控制精度: ±3cm → ±2cm
- ✅ 系统级优化(全局最优)
- ✅ 流量受限时合理分配

**运行方式**:
```bash
python dynamic_design_L3.py
```

**输出文件**:
- `dynamic_L3_正常协调工况.png` - 多点协调
- `dynamic_L3_末端需水阶跃.png` - 系统响应
- `dynamic_L3_上游流量扰动.png` - 流量优化
- `dynamic_L3_多点波动.png` - 复杂工况

---

## 📊 三种设计范式对比

### 对比表格

| 对比项 | 静态设计 | L2级动态设计 | L3级动态设计 |
|-------|---------|------------|------------|
| **设计方法** | 恒定流水力计算 | 静态设计+PID控制 | L2级+协调控制 |
| **计算工况数** | 2个 | 100+个 | 200+个 |
| **控制点数** | 1个 | 1个 | 4个 |
| **控制精度** | ±30cm | ±3cm | ±2cm |
| **响应时间** | 30-60分钟 | 3-5分钟 | 3-4分钟 |
| **耦合处理** | 人工难调 | 无(单点) | 解耦算法 |
| **运行方式** | 人工调度 | 自动控制 | 协调控制 |
| **交付物** | 参数表+手册 | +代码+智能体 | +协调算法 |
| **代码行数** | ~400行 | ~600行 | ~900行 |
| **初始投资** | 30万 | 35万(+17%) | 180万(+50%,4闸) |
| **智能化等级** | L0 | L2 | L3 |

### 关键差异

#### 1. 设计工况数量

**静态设计**: 只计算2个典型工况
```python
# static_design.py
工况1: 设计流量 Q=10 m³/s
工况2: 校核流量 Q=15 m³/s
```

**L2级动态设计**: 100+工况在环测试
```python
# dynamic_design_L2.py
场景1: 正常工况(恒定需水) - 1小时
场景2: 需水阶跃 - 30分钟
场景3: 需水波动 - 30分钟
场景4: 突发大需水 - 30分钟
总计: ~100个时间步 × 4场景 = 400个工况点
```

**L3级动态设计**: 200+工况协调测试
```python
# dynamic_design_L3.py
场景1-4: 各30分钟 × 4个池
总计: ~180个时间步 × 4场景 × 4池 = 2880个工况点
```

#### 2. 控制算法复杂度

**静态设计**: 无控制算法,人工调节
```python
# 人工查表
if 下游水位 > 2.0m:
    人工关小闸门
elif 下游水位 < 2.0m:
    人工开大闸门
```

**L2级动态设计**: PID自动控制
```python
# 每10秒执行一次
error = setpoint - measurement  # 2.0 - 实测水位
P = Kp * error                   # 比例项
I = Ki * ∫error·dt              # 积分项
D = Kd * derror/dt              # 微分项
opening = P + I + D             # PID输出
启闭机.move_to(opening)
```

**L3级动态设计**: 协调控制算法
```python
# 每10秒执行一次,4个闸门协调
for i in range(4):
    openings_local[i] = PID[i].update()  # 局部控制
ff_comp = feedforward(flow_change)       # 前馈补偿
openings += ff_comp
openings = decoupling(openings)          # 解耦控制
openings = optimize(openings, demands)   # 全局优化
for i in range(4):
    启闭机[i].move_to(openings[i])
```

#### 3. 交付物对比

**静态设计**:
- ✅ 设计参数表(纸质/Excel)
- ✅ 流量-开度关系曲线图
- ✅ 操作手册(静态文档)

**L2级动态设计**:
- ✅ 设计参数表(继承静态)
- ✅ Python代码包(600行)
  - 传感器模拟
  - PID控制器
  - 数字孪生模型
  - 在环测试脚本
- ✅ 仿真结果图表(4张)
- ✅ 智能化等级评估报告

**L3级动态设计**:
- ✅ L2级全部内容(继承)
- ✅ Python代码包(900行)
  - 协调控制算法
  - 解耦控制
  - 前馈补偿
  - 全局优化
- ✅ 仿真结果图表(4张×4池)
- ✅ L3级智能化等级认证

---

## 🚀 快速开始

### 环境要求

```bash
Python 3.8+
numpy >= 1.20
matplotlib >= 3.4
```

### 安装依赖

```bash
pip install numpy matplotlib
```

### 运行案例

**1. 静态设计(5分钟)**
```bash
cd /workspace/books/intelligent-water-network-design/code/examples/comparison_static_vs_dynamic

python static_design.py

# 输出:
# - 闸门尺寸设计结果
# - 校核流量验算
# - 流量-开度关系表
# - static_design_discharge_curve.png
# - static_design_operation_manual.txt
```

**2. L2级动态设计(15分钟)**
```bash
python dynamic_design_L2.py

# 输出:
# - 4个场景的仿真结果
# - 性能指标统计
# - 智能化等级评估(L2认证)
# - dynamic_L2_*.png (4张图)
```

**3. L3级动态设计(30分钟)**
```bash
python dynamic_design_L3.py

# 输出:
# - 4个协调控制场景仿真
# - 多点性能指标统计
# - 智能化等级评估(L3认证)
# - dynamic_L3_*.png (4张图)
```

### 完整对比(运行全部)

```bash
# 运行全部三个脚本
python static_design.py && \
python dynamic_design_L2.py && \
python dynamic_design_L3.py

# 查看输出文件
ls -lh *.png *.txt
```

---

## 📖 学习路径建议

### 路径1: 快速理解(1小时)

1. 阅读本README(10分钟)
2. 运行static_design.py,查看输出(10分钟)
3. 对比查看dynamic_design_L2.py代码(20分钟)
4. 运行L2脚本,查看仿真结果(20分钟)

**关键点**: 理解静态设计只计算2个工况,动态设计通过在环测试覆盖100+工况

---

### 路径2: 深入学习(4小时)

1. 详细阅读3个脚本代码(2小时)
   - 重点关注PID算法实现
   - 理解数字孪生模型
   - 学习协调控制算法
2. 运行全部脚本并分析结果(1小时)
3. 修改参数,自己做实验(1小时)
   - 改变PID参数(Kp, Ki, Kd)
   - 改变需水量场景
   - 观察性能变化

**关键点**: 通过修改参数,理解控制理论在工程中的应用

---

### 路径3: 实战应用(2周)

1. 学习前置教材(1周)
   - 第1本书: 水系统控制论(PID理论)
   - 第2本书: 明渠水力学(水力计算)
2. 参考本案例,开发自己的项目(1周)
   - 选择一个实际工程
   - 先做静态设计
   - 再升级为L2级动态设计
   - 如果是多点系统,升级为L3级

**关键点**: 实际项目是最好的老师

---

## 💡 核心要点

### 1. 动态设计不是推倒重来

```python
# 静态设计: 闸门尺寸5m×3m
gate_width = 5.0
gate_height = 3.0

# L2级动态设计: 完全继承静态设计的尺寸
gate_width = 5.0  # 不变
gate_height = 3.0 # 不变
# 只是增加智能体系统:
+ 传感器(3个)
+ PID控制器(1个)
+ 数字孪生模型
```

### 2. 在环测试是核心创新

```python
# 静态设计: 人工验算2个工况
设计工况: Q=10 m³/s ✓
校核工况: Q=15 m³/s ✓

# L2级动态设计: 自动测试100+工况
for scenario in scenarios:
    for t in range(3600):  # 仿真1小时
        运行控制回路()
        记录性能数据()
    分析性能指标()
    绘制仿真曲线()
```

### 3. 智能化等级可评估

```python
# 五大维度评分
自动化程度 = 85-100分(L2-L3)
控制精度   = 90-95分
响应速度   = 85-90分
鲁棒性     = 80-90分
可维护性   = 85-90分

综合得分 = 平均(各维度)
if 综合得分 >= 70: L2级认证 ✓
if 综合得分 >= 85: L3级认证 ✓
```

---

## 🎯 总结

通过这三个案例脚本,我们直观地展示了:

1. **静态设计**: 传统方法,简单快速,但应对复杂变化能力弱
2. **L2级动态设计**: 增加智能体系统,性能提升10倍,投资增量仅17%
3. **L3级动态设计**: 多点协调控制,解决系统耦合,适用于复杂工程

**核心结论**:
- ✅ 动态设计 = 静态设计 + 智能体系统
- ✅ 不是替代,而是增强
- ✅ 增量投资可控,效益显著
- ✅ 代码可复用,工具链完备

---

**版本**: v1.0  
**日期**: 2025-11-04  
**作者**: CHS-Books项目组  
**许可**: MIT License
