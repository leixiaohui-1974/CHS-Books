# 案例6: DFIG建模

## 简介

本案例深入研究双馈感应发电机(Doubly-Fed Induction Generator, DFIG)的建模与特性分析。DFIG是目前应用最广泛的风力发电机类型之一，具有变速恒频运行、变流器容量小(约30%额定功率)的显著优势。本案例演示DFIG的稳态特性曲线、次同步/超同步运行模式、转差率-功率关系以及变速范围与转子功率的关系。理解DFIG的工作原理对于风力发电系统的设计、控制和并网运行至关重要。

## 理论背景

DFIG由定子直接接入电网、转子通过背靠背变流器接入电网的异步发电机构成。其核心特点是转差率s=(n_s-n_r)/n_s可正可负，实现超同步和次同步双向运行。定子功率Ps≈-T_e·ω_s，转子功率Pr≈-s·Ps，总机械功率Pm=Ps+Pr。当s<0(超同步运行，转速高于同步转速)时，转子向电网馈电；当s>0(次同步运行)时，转子从电网吸收功率。变流器容量需满足最大转子功率需求，通常为|s_max|×P_rated，典型值为±30%。DFIG的等效电路包括定转子电阻、漏感和励磁支路，电磁转矩T_e与转差率s呈复杂非线性关系。

## 代码说明

### 主要类

**DFIGModel**: 双馈发电机模型类
- `__init__(P_rated, V_rated, poles, Rs, Rr, Lm, Lls, Llr)`: 初始化DFIG参数
  - P_rated: 额定功率 (W)
  - V_rated: 额定电压 (V)
  - poles: 极对数
  - Rs, Rr: 定转子电阻 (pu)
  - Lm, Lls, Llr: 励磁电感、定转子漏感 (pu)

- `steady_state(s)`: 计算给定转差率下的稳态特性
  - 输入: 转差率s
  - 输出: 定子功率Ps、电磁转矩Te、转子转速ω_r等

- 属性:
  - `n_sync`: 同步转速 (RPM)
  - `omega_s`: 同步角速度 (rad/s)

### 演示函数

- `demo_dfig_characteristics()`: DFIG稳态特性曲线
  - 功率-转差率特性
  - 转矩-转差率特性
  - 转矩-转速特性
  - 功率-转速特性

- `demo_operating_modes()`: 运行模式分析
  - 次同步运行 (s>0)
  - 同步运行 (s=0)
  - 超同步运行 (s<0)
  - 功率流向示意

- `demo_speed_range()`: 变速范围分析
  - 转子功率需求
  - 变流器容量计算

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_06_dfig_modeling

# 运行案例
python main.py
```

## 参数说明

### DFIG电气参数
- **P_rated**: 额定功率 (2 MW)
- **V_rated**: 额定电压 (690 V)
- **poles**: 极对数 (4, 对应同步转速1500 RPM@50Hz)
- **Rs**: 定子电阻 (0.01 pu)
- **Rr**: 转子电阻 (0.01 pu)
- **Lm**: 励磁电感 (3.0 pu)
- **Lls, Llr**: 定转子漏感 (0.1 pu)

### 运行参数
- **转差率范围**: s ∈ [-0.3, 0.3]
  - s = -0.3: 超同步，1950 RPM
  - s = 0: 同步，1500 RPM
  - s = 0.3: 次同步，1050 RPM
- **变速范围**: ±30%，对应变流器容量

## 预期结果说明

运行本案例后将生成3张图表：

1. **case06_dfig_characteristics.png** (四图):
   - 功率-转差率: S型曲线，s<0时Ps>0(发电)
   - 转矩-转差率: 超同步区Te<0(发电转矩)
   - 转矩-转速: 工作区在1050-1950 RPM
   - 功率-转速: 额定功率线

2. **case06_operating_modes.png** (三图):
   - 次同步运行 (s=0.05, n=1425 RPM):
     - 机械功率 > 定子功率
     - 转子吸收功率
   - 同步运行 (s=0, n=1500 RPM):
     - 转子功率为零
   - 超同步运行 (s=-0.05, n=1575 RPM):
     - 机械功率 < 定子功率
     - 转子释放功率

3. **case06_speed_range.png**:
   - 转子功率需求: Pr = -s × Ps
     - 额定功率下最大转子功率: ±0.6 MW
   - 变流器容量曲线
     - 容量需求: 30% × 2MW = 0.6 MW

### 控制台输出
- 同步转速和同步角速度
- 关键运行点的功率和转矩
- 不同运行模式的功率流向
- 变流器容量需求

## 工程应用

DFIG技术的优势：
1. **变流器容量小**: 仅需30%，降低成本
2. **变速范围**: ±30%，满足MPPT需求
3. **功率因数控制**: 独立的有功/无功控制
4. **电网友好**: 可提供无功支撑

技术挑战：
1. 电网故障敏感性 (需要Crowbar保护)
2. 低电压穿越能力弱
3. 滑环和碳刷维护

## 参考文献

1. Abad, G., et al. (2011). *Doubly Fed Induction Machine: Modeling and Control for Wind Energy Generation*. Wiley-IEEE Press.
2. Ekanayake, J. B., et al. (2012). *Wind Turbine Generator Modeling and Control*. John Wiley & Sons.
3. Muller, S., Deicke, M., & De Doncker, R. W. (2002). Doubly fed induction generator systems for wind turbines. *IEEE Industry Applications Magazine*, 8(3), 26-33.
