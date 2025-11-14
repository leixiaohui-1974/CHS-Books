# 案例20: 直流母线电压控制

## 案例简介

本案例演示光伏系统中直流母线电压的PI控制和前馈补偿技术。直流母线电压稳定性是光伏并网系统的关键性能指标，直接影响逆变器效率和电能质量。通过Boost变换器的占空比控制，实现母线电压的精确调节，同时通过前馈补偿提高系统动态响应速度。

## 理论背景

### Boost变换器模型

Boost变换器通过PWM控制开关管占空比d，实现输入电压V_in到输出电压V_out的升压：

```
V_out = V_in / (1 - d)
```

连续导通模式(CCM)下的状态方程：

```
L * di_L/dt = V_in - (1-d)*v_C
C * dv_C/dt = (1-d)*i_L - v_C/R
```

其中：
- L: 电感值
- C: 电容值
- R: 负载电阻
- i_L: 电感电流
- v_C: 电容电压（母线电压）

### PI控制器

PI控制器根据电压误差计算占空比：

```
d(t) = Kp * e(t) + Ki * ∫e(t)dt
```

其中：
- e(t) = v_ref - v_C(t)：电压误差
- Kp: 比例增益
- Ki: 积分增益

### 前馈补偿

前馈补偿根据负载电流快速调整占空比：

```
d_feedforward = 1 - V_in / V_ref
```

## 代码说明

### 主要类

1. **BoostConverter**: Boost变换器模型
   - `__init__(L, C, R)`: 初始化电感、电容、负载
   - `step(V_in, d, dt)`: 单步仿真，返回电容电压和电感电流

2. **DCBusVoltageController**: PI控制器
   - `__init__(Kp, Ki, v_ref)`: 初始化控制参数和参考电压
   - `compute(v_C, dt)`: 计算控制量（占空比）

3. **FeedforwardCompensator**: 前馈补偿器
   - `__init__(V_in_nominal, V_ref)`: 初始化标称参数
   - `compute(i_load)`: 计算前馈补偿量

### 演示函数

- `experiment_1_pi_control()`: 实验1 - PI控制电压稳定
- `experiment_2_feedforward()`: 实验2 - 前馈补偿效果
- `experiment_3_load_disturbance()`: 实验3 - 负载扰动响应

## 运行方法

```bash
cd /home/user/CHS-Books/books/photovoltaic-system-modeling-control/code/examples/case_20_dc_bus_control
python main.py
```

## 参数说明

| 参数 | 含义 | 典型值 | 单位 |
|------|------|--------|------|
| L | 电感值 | 100 | μH |
| C | 电容值 | 100 | μF |
| R | 负载电阻 | 20 | Ω |
| V_in | 输入电压 | 100 | V |
| V_ref | 参考电压 | 400 | V |
| Kp | 比例增益 | 0.001 | - |
| Ki | 积分增益 | 0.5 | - |
| dt | 仿真步长 | 1 | μs |

## 预期结果说明

程序将生成以下可视化结果：

### 实验1: PI控制
- 母线电压曲线：从0V快速上升至400V，超调小
- 占空比变化：初始较大后收敛至稳态值~0.75
- 电压误差：快速收敛至接近0

### 实验2: 前馈补偿
- 对比PI控制和PI+前馈两种方案
- 前馈补偿显著减小超调和振荡
- 调节时间缩短约30%

### 实验3: 负载扰动
- t=0.01s时负载电阻从20Ω突变至10Ω
- 母线电压跌落后快速恢复
- PI控制器自动调整占空比补偿负载变化

典型性能指标：
- 电压稳态误差：<1V（<0.25%）
- 调节时间：<10ms
- 超调量：<5%

## 工程应用

1. **光伏并网逆变器**：稳定直流侧电压，提高逆变效率
2. **储能系统**：电池充放电过程中维持母线电压稳定
3. **电动汽车充电桩**：DC-DC变换器电压控制
4. **数据中心UPS**：关键负载供电的电压稳定性保障

## 参考文献

1. Erickson R W, Maksimovic D. Fundamentals of Power Electronics[M]. 3rd ed. Springer, 2020.
2. Rashid M H. Power Electronics: Circuits, Devices and Applications[M]. 4th ed. Pearson, 2014.
3. 张兴, 杜少武. 光伏并网发电及其逆变控制[M]. 机械工业出版社, 2015.
4. 王兆安, 刘进军. 电力电子技术[M]. 第5版. 机械工业出版社, 2009.
