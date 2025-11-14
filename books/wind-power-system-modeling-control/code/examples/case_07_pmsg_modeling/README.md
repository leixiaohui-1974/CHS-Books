# 案例7: PMSG建模

## 简介

本案例研究永磁同步发电机(Permanent Magnet Synchronous Generator, PMSG)的建模与控制策略。PMSG是直驱式风力发电机的核心部件，具有无齿轮箱、效率高、可靠性好的优点，是大型海上风电的主流技术路线。本案例演示PMSG的dq坐标系数学模型、Id=0控制策略、电磁转矩计算以及恒转矩区和恒功率区的运行特性。掌握PMSG的建模与控制对于直驱式风力发电系统的设计和优化具有重要价值。

## 理论背景

PMSG采用dq坐标系建模，d轴与转子磁场对齐，q轴超前d轴90°。电压方程为：Vd = -Rs×Id - ωe×Lq×Iq, Vq = -Rs×Iq + ωe×Ld×Id + ωe×ψf，其中ψf为永磁磁链。电磁转矩为Te = 1.5×p×[ψf×Iq + (Ld-Lq)×Id×Iq]，对于表贴式PMSG(Ld=Lq)，转矩简化为Te = 1.5×p×ψf×Iq。Id=0控制策略是最常用的方法，即Id=0、Iq控制转矩，优点是控制简单、磁链恒定、效率高。PMSG的运行分为两个区域：基速以下的恒转矩区(Iq=常数)和基速以上的弱磁恒功率区(Id<0)。直驱PMSG极对数多(60-120极)，转速低(10-20 RPM)，扭矩大。

## 代码说明

### 主要类

**PMSGModel**: 永磁同步发电机模型类
- `__init__(P_rated, V_rated, poles, Rs, Ld, Lq, psi_f)`: 初始化PMSG参数
  - P_rated: 额定功率 (W)
  - V_rated: 额定电压 (V)
  - poles: 极对数 (直驱通常60-120)
  - Rs: 定子电阻 (pu)
  - Ld, Lq: d轴和q轴电感 (pu)
  - psi_f: 永磁磁链 (pu)

- `steady_state(omega_r, Iq, Id)`: 计算稳态特性
  - 输入: 转子转速ω_r, q轴电流Iq, d轴电流Id
  - 输出: 电磁转矩Te、输出功率Ps、dq轴电压Vd/Vq

- `electromagnetic_torque(Id, Iq)`: 电磁转矩计算

### 演示函数

- `demo_pmsg_characteristics()`: PMSG稳态特性
  - 转矩-转速特性
  - 功率-转速特性
  - dq轴电压特性
  - 端电压幅值

- `demo_torque_control()`: 转矩控制策略
  - Id=0控制(标准)
  - 弱磁控制(Id<0)
  - 增磁控制(Id>0)

- `demo_operating_region()`: 运行区域分析
  - 恒转矩区
  - 恒功率弱磁区

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_07_pmsg_modeling

# 运行案例
python main.py
```

## 参数说明

### PMSG电气参数
- **P_rated**: 额定功率 (2 MW)
- **V_rated**: 额定电压 (690 V)
- **poles**: 极对数 (60, 直驱式)
- **Rs**: 定子电阻 (0.01 pu)
- **Ld = Lq**: 同步电感 (0.8 pu, 表贴式)
- **psi_f**: 永磁磁链 (1.0 pu)

### 控制参数
- **Id**: d轴电流指令
  - Id=0: 标准控制
  - Id<0: 弱磁控制(高速区)
  - Id>0: 增磁控制(少用)
- **Iq**: q轴电流指令(转矩控制)

### 运行范围
- **转速范围**: 5-20 RPM (直驱低速)
- **额定转速**: ~12 RPM
- **基速**: 定义恒转矩区和弱磁区的分界点

## 预期结果说明

运行本案例后将生成3张图表：

1. **case07_pmsg_characteristics.png** (四图):
   - 转矩-转速: Id=0控制下Te≈常数(恒转矩区)
   - 功率-转速: P = Te × ω，线性增长
   - dq轴电压: Vd随转速线性增加，Vq也增加
   - 端电压幅值: V = √(Vd²+Vq²)

2. **case07_torque_control.png** (三图):
   - Id=0控制: Te = kIq，线性关系，最常用
   - 弱磁控制(Id=-500A): Te略减小，适用于高速
   - 增磁控制(Id=+500A): Te略增大，但损耗增加

3. **case07_operating_region.png**:
   - 恒转矩区(< 基速): Te = Te_rated，Iq = 常数
   - 弱磁区(> 基速): P = P_rated = 常数，Te ∝ 1/ω
   - 额定电流曲线和恒功率曲线
   - 分界点: 基速(Base Speed)

### 控制台输出
- PMSG参数总结
- 不同转速下的转矩和功率
- 不同Id控制策略下的转矩
- 基速点的转矩和功率

## 工程应用

PMSG直驱技术优势：
1. **无齿轮箱**: 可靠性高、维护少
2. **高效率**: 全速范围效率>94%
3. **低噪声**: 无齿轮箱啮合噪声
4. **适合海上**: 维护难度低

技术挑战：
1. **重量大**: 低速大扭矩→发电机尺寸大
2. **成本高**: 永磁材料(NdFeB)成本
3. **退磁风险**: 短路故障可能导致退磁
4. **全功率变流器**: 100%容量，成本高

### 控制策略选择
- **Id=0**: 表贴式PMSG首选
- **MTPA**: 内置式PMSG(Ld≠Lq)
- **弱磁控制**: 扩展高速运行范围

## 参考文献

1. Chinchilla, M., et al. (2006). Control of permanent-magnet generators applied to variable-speed wind-energy systems connected to the grid. *IEEE Transactions on Energy Conversion*, 21(1), 130-135.
2. Polinder, H., et al. (2006). Comparison of direct-drive and geared generator concepts for wind turbines. *IEEE Transactions on Energy Conversion*, 21(3), 725-733.
3. Morimoto, S., et al. (1994). Wide-speed operation of interior permanent magnet synchronous motors with high-performance current regulator. *IEEE Transactions on Industry Applications*, 30(4), 920-926.
