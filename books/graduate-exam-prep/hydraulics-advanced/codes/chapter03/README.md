# 第03章 管流与明渠流 - 代码实现

## 📋 概述

本目录包含第03章"管流与明渠流"的Python代码实现，涵盖5个核心题目，共计约3400行高质量代码。

**完成状态**: ✅ 100%完成（5/5个程序）

## 📁 文件清单

### 1. 雷诺数与流态判别
**文件**: `ch03_problem01_reynolds_number.py` (约680行)  
**难度**: ⭐⭐ 基础  
**核心知识**:
- 雷诺数计算公式 Re = vd/ν
- 流态判别（层流/过渡流/紊流）
- 临界雷诺数（2000-4000）
- 影响因素分析（流速、管径、温度、粘度）

**主要功能**:
- 计算雷诺数并判别流态
- 临界流速计算
- 不同流速下的流态转换分析
- 温度对流态的影响分析
- 管径对雷诺数的影响
- 多维度可视化（4个子图）

**运行示例**:
```python
from ch03_problem01_reynolds_number import ReynoldsNumberAnalysis

# 创建分析对象
reynolds = ReynoldsNumberAnalysis(d=0.1, v=2.0, nu=1.0e-6)

# 计算雷诺数
Re = reynolds.reynolds_number()  # 200000

# 判别流态
regime = reynolds.flow_regime()  # "紊流"

# 打印结果并绘图
reynolds.print_results()
reynolds.plot_analysis()
```

---

### 2. 管道沿程损失计算
**文件**: `ch03_problem03_friction_loss.py` (约680行)  
**难度**: ⭐⭐⭐ 强化  
**核心知识**:
- 达西-魏斯巴赫公式 h_f = λ(L/d)(v²/2g)
- 曼宁公式 v = (1/n)R^(2/3)i^(1/2)
- 沿程阻力系数计算
- Colebrook-White公式
- 水力坡度 J = h_f/L

**主要功能**:
- 计算沿程阻力系数λ
- 计算沿程水头损失h_f
- 计算压力降低值Δp
- 不同粗糙度的影响分析
- 不同管径的影响分析
- 不同管长的影响分析
- 能量线与压力分布（6个子图）

**运行示例**:
```python
from ch03_problem03_friction_loss import FrictionLossAnalysis

# 创建分析对象
friction = FrictionLossAnalysis(L=1000.0, d=0.3, Q=0.1, n=0.012)

# 计算沿程损失
h_f = friction.head_loss()  # 水头损失 (m)

# 计算压力降
dp = friction.pressure_drop()  # 压力降 (Pa)

# 打印结果并绘图
friction.print_results()
friction.plot_analysis()
```

---

### 3. 明渠均匀流计算
**文件**: `ch03_problem06_open_channel_flow.py` (约700行)  
**难度**: ⭐⭐⭐⭐ 强化  
**核心知识**:
- 曼宁公式 v = (1/n)R^(2/3)i^(1/2)
- 谢才公式 v = C√(Ri)
- 水力半径 R = A/χ
- 佛汝德数 Fr = v/√(gh)
- 水力最优断面（矩形：h = b/2）

**主要功能**:
- 计算过水断面面积A与湿周χ
- 计算水力半径R
- 用曼宁公式计算流速v
- 计算流量Q
- 佛汝德数计算与流态判别
- 水力最优断面设计
- 不同水深/坡度/粗糙度影响分析
- 输水效率分析（9个子图）

**运行示例**:
```python
from ch03_problem06_open_channel_flow import OpenChannelUniformFlow

# 创建明渠对象
channel = OpenChannelUniformFlow(b=3.0, h=1.2, i=0.001, n=0.025)

# 计算水力参数
A = channel.cross_section_area()  # 断面面积
R = channel.hydraulic_radius()    # 水力半径
v = channel.velocity_manning()    # 流速
Q = channel.discharge()           # 流量
Fr = channel.froude_number()      # 佛汝德数

# 最优断面分析
h_opt, A_opt, chi_opt, R_opt, v_opt, Q_opt = channel.optimal_section_analysis()

# 打印结果并绘图
channel.print_results()
channel.plot_analysis()
```

---

### 4. 临界水深计算
**文件**: `ch03_problem09_critical_depth.py` (约690行)  
**难度**: ⭐⭐⭐⭐⭐ 强化  
**核心知识**:
- 临界水深公式（矩形）h_c = (Q²/(gb²))^(1/3)
- 临界条件 Fr = 1, v² = gh
- 临界比能 E_c = (3/2)h_c
- 比能曲线 E = h + v²/(2g)
- 共轭水深（急流与缓流）

**主要功能**:
- 计算临界水深h_c
- 计算临界流速v_c
- 计算临界比能E_c
- 绘制水深-比能曲线
- 佛汝德数随水深变化
- 不同流量下的临界水深
- 共轭水深分析
- 流态分类（9个子图）

**运行示例**:
```python
from ch03_problem09_critical_depth import CriticalDepthAnalysis

# 创建分析对象
critical = CriticalDepthAnalysis(b=2.0, Q=4.0)

# 计算临界参数
h_c = critical.critical_depth()              # 临界水深
v_c = critical.critical_velocity()           # 临界流速
E_c = critical.critical_specific_energy()    # 临界比能

# 计算给定比能的共轭水深
h1, h2 = critical.depth_for_energy(E=3.0)   # 急流水深, 缓流水深

# 比能曲线
h_array, E_array = critical.specific_energy_curve()

# 打印结果并绘图
critical.print_results()
critical.plot_analysis()
```

---

### 5. 综合应用：管渠联合输水系统
**文件**: `ch03_problem15_comprehensive.py` (约700行)  
**难度**: ⭐⭐⭐⭐⭐ 综合  
**核心知识**:
- 管渠联合能量方程 H₀ = H₁ + h_管道 + E_明渠
- 管道达西公式
- 明渠曼宁公式
- 系统优化设计
- 流态综合判别

**主要功能**:
- 计算系统流量Q（能量方程迭代求解）
- 计算管道出口压力
- 计算明渠正常水深
- 判断明渠流态
- 系统效率分析
- 管径优化建议
- 能量分配分析
- 系统综合可视化（9个子图）

**运行示例**:
```python
from ch03_problem15_comprehensive import PipeChannelSystem

# 创建系统对象
system = PipeChannelSystem(
    H0=50.0,           # 上游水库水位
    H1=20.0,           # 下游水位
    d=0.5,             # 管道直径
    L=500.0,           # 管道长度
    b=2.0,             # 明渠宽度
    i=0.002,           # 明渠坡度
    n_pipe=0.013,      # 管道粗糙系数
    n_channel=0.020    # 明渠粗糙系数
)

# 计算系统参数
Q = system.system_flow_rate()              # 系统流量
h_pipe = system.pipe_head_loss(Q)         # 管道损失
p_out = system.pipe_outlet_pressure(Q)    # 出口压力
h_n = system.channel_normal_depth(Q)      # 明渠水深
Fr = system.channel_froude_number(Q, h_n) # 佛汝德数
efficiency = system.system_efficiency(Q)   # 系统效率

# 管径优化
d_array, Q_array, h_loss_array, eff_array = system.diameter_optimization()

# 打印结果并绘图
system.print_results()
system.plot_analysis()
```

---

## 🎯 代码特色

### 1. 完整的OOP设计
- 每个问题封装为独立的类
- 清晰的方法命名和参数传递
- 易于扩展和维护

### 2. 丰富的可视化
- 每个程序包含4-9个专业图表
- 流态判别图、能量线图、比能曲线
- 系统示意图、优化曲线
- 参数对比图、影响因素分析

### 3. 详细的物理解释
- 公式逐步推导
- 单位标注完整
- 物理意义阐述
- 考试要点总结

### 4. 实用的工程应用
- 参数优化建议
- 系统效率分析
- 流态判别标准
- 设计优化方案

### 5. 严谨的数值计算
- 迭代求解（scipy.optimize.fsolve）
- 多方案对比
- 敏感性分析
- 误差控制

## 🔧 使用方法

### 环境要求
```bash
Python >= 3.8
numpy >= 1.20.0
matplotlib >= 3.3.0
scipy >= 1.6.0
```

### 安装依赖
```bash
pip install numpy matplotlib scipy
```

### 运行示例
```bash
# 运行单个文件
cd /workspace/books/graduate-exam-prep/hydraulics-advanced/codes/chapter03
python ch03_problem01_reynolds_number.py

# 或者作为模块导入
python
>>> from ch03_problem01_reynolds_number import ReynoldsNumberAnalysis
>>> reynolds = ReynoldsNumberAnalysis(d=0.1, v=2.0)
>>> reynolds.print_results()
```

## 📊 代码统计

| 程序 | 文件名 | 行数 | 类/函数 | 可视化 |
|------|--------|------|---------|--------|
| 题1 | ch03_problem01_reynolds_number.py | ~680 | 1类/10方法 | 4图 |
| 题3 | ch03_problem03_friction_loss.py | ~680 | 1类/10方法 | 6图 |
| 题6 | ch03_problem06_open_channel_flow.py | ~700 | 1类/12方法 | 9图 |
| 题9 | ch03_problem09_critical_depth.py | ~690 | 1类/11方法 | 9图 |
| 题15 | ch03_problem15_comprehensive.py | ~700 | 1类/13方法 | 9图 |
| **总计** | **5个文件** | **~3450行** | **5类/56方法** | **37图** |

## 🎓 学习建议

### 基础学习路径
1. **题1：雷诺数判别** → 理解流态基本概念
2. **题3：沿程损失** → 掌握管道能量损失计算
3. **题6：明渠均匀流** → 学习明渠基本理论

### 进阶学习路径
4. **题9：临界水深** → 深入理解比能与流态转换
5. **题15：综合应用** → 掌握管渠联合系统设计

### 考研重点
- 雷诺数计算与流态判别（必考）
- 达西公式与曼宁公式（核心）
- 临界水深与比能曲线（重点）
- 佛汝德数与流态转换（常考）
- 综合应用题（压轴）

## 💡 典型考题示例

### 例1：雷诺数判别（基础题）
> 圆管输水，d=0.1m，v=2m/s，ν=1.0×10⁻⁶ m²/s，求雷诺数并判别流态。

**解答**: 运行 `ch03_problem01_reynolds_number.py`

### 例2：沿程损失（强化题）
> 管道L=1000m，d=0.3m，Q=0.1m³/s，n=0.012，求沿程损失。

**解答**: 运行 `ch03_problem03_friction_loss.py`

### 例3：明渠均匀流（强化题）
> 矩形明渠b=3m，h=1.2m，i=0.001，n=0.025，求流量。

**解答**: 运行 `ch03_problem06_open_channel_flow.py`

### 例4：临界水深（强化题）
> 矩形明渠b=2m，Q=4m³/s，求临界水深和临界比能。

**解答**: 运行 `ch03_problem09_critical_depth.py`

### 例5：管渠联合系统（综合题）
> 设计管渠联合输水系统，计算流量并优化。

**解答**: 运行 `ch03_problem15_comprehensive.py`

## 📖 常见问题

### Q1: 如何判断流态？
A: 使用雷诺数Re = vd/ν，Re<2000层流，Re>4000紊流。

### Q2: 临界水深有什么物理意义？
A: 临界水深对应Fr=1的状态，是缓流与急流的分界，也是最小比能对应的水深。

### Q3: 如何计算明渠流量？
A: 使用曼宁公式v = (1/n)R^(2/3)i^(1/2)，再乘以断面面积Q=Av。

### Q4: 管道损失如何减小？
A: 增大管径、使用光滑管材、减小管长、避免不必要的局部损失。

### Q5: 如何设计水力最优断面？
A: 对于矩形断面，水力最优条件是h=b/2，使得在相同面积下湿周最小。

## 📚 参考资料

1. 《水力学》（第五版），吴持恭主编，高等教育出版社
2. 《明渠水力学》，张瑞瑾主编，水利电力出版社
3. 各大高校考研真题（985/211）
4. 国家注册公用设备工程师考试参考用书

## 📝 更新日志

### v1.0 - 2025-11-07
- ✅ 完成题1：雷诺数判别（680行）
- ✅ 完成题3：管道沿程损失（680行）
- ✅ 完成题6：明渠均匀流（700行）
- ✅ 完成题9：临界水深（690行）
- ✅ 完成题15：综合应用（700行）
- ✅ 第3章代码100%完成
- ✅ 总计约3450行代码
- ✅ 包含37个专业图表
- ✅ 5个完整的工程案例

---

**作者**: CHS-Books Team  
**日期**: 2025-11-07  
**状态**: ✅ 第3章代码开发完成（100%）
