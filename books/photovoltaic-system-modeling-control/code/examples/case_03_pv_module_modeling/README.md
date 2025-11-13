# 案例3: 光伏组件建模

## 📋 案例概述

**工程背景**: 
单片光伏电池的电压约0.6V,无法直接使用。实际应用中需要将多片电池串联组成组件,典型配置为60片或72片,输出电压30-40V,功率200-400W。

**学习目标**:
1. 理解光伏组件的串联特性
2. 掌握旁路二极管的作用机制
3. 学习组件参数计算方法
4. 分析部分遮挡对组件性能的影响

---

## 🔬 理论基础

### 串联特性

**电气关系**:
```python
I_module = I_cell          (电流相同)
V_module = Σ V_cell        (电压相加)
P_module = Σ P_cell        (功率相加)
```

**组件参数**:
- 开路电压: `Voc_module ≈ Ns × Voc_cell`
- 短路电流: `Isc_module ≈ Isc_cell`
- 最大功率: `Pmp_module ≈ Ns × Pmp_cell`
- 填充因子: `FF_module ≈ FF_cell`

### 旁路二极管

**配置**: 典型为60片/3个二极管 = 20片/组

**作用**:
1. 防止反向偏压
2. 避免热斑效应  
3. 减少遮挡损失
4. 保护组件安全

**工作原理**:
```python
正常情况: 二极管截止,电流通过所有电池
部分遮挡: 被遮挡组产生负压,二极管导通旁路
```

### 热斑效应

**危害**:
- 被遮挡电池消耗功率而非产生功率
- 局部温度升高至80-150°C
- 可能永久损坏电池
- 严重时引发火灾

**预防**: 旁路二极管是必需的保护元件

---

## 💻 代码示例

### 1. 创建基本组件

```python
from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule

# 创建单片电池
cell = SingleDiodeModel(
    Isc=8.0,      # 短路电流 8A
    Voc=0.6,      # 开路电压 0.6V
    Imp=7.5,      # MPP电流 7.5A
    Vmp=0.48,     # MPP电压 0.48V
    T=298.15,     # 温度 25°C
    G=1000.0      # 辐照度 1000W/m²
)

# 创建60片组件
module = PVModule(
    cell_model=cell,
    Ns=60,        # 60片串联
    Nb=3,         # 3个旁路二极管
    name="60片光伏组件"
)

# 打印参数
module.print_parameters()
```python

输出:
```
60片光伏组件 - 组件参数
============================================================
配置:
  串联电池数 Ns:         60 片
  旁路二极管数 Nb:       3 个
  每组电池数:            20 片/组

额定参数:
  开路电压 Voc:          36.00 V
  短路电流 Isc:          8.000 A
  最大功率点电压 Vmp:    28.80 V
  最大功率点电流 Imp:    7.500 A
  最大功率 Pmp:          216.00 W
============================================================
```python

### 2. 计算I-V和P-V曲线

```python
# 获取I-V曲线
V, I = module.get_iv_curve(300)

# 获取P-V曲线
V, P = module.get_pv_curve(300)

# 绘制
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(V, I)
ax1.set_xlabel('电压 (V)')
ax1.set_ylabel('电流 (A)')
ax1.set_title('I-V特性曲线')
ax1.grid(True)

ax2.plot(V, P)
ax2.set_xlabel('电压 (V)')
ax2.set_ylabel('功率 (W)')
ax2.set_title('P-V特性曲线')
ax2.grid(True)

plt.tight_layout()
plt.show()
```python

### 3. 寻找最大功率点

```python
# 计算MPP
vmpp, impp, pmpp = module.find_mpp()

print(f"最大功率点:")
print(f"  Vmpp = {vmpp:.2f} V")
print(f"  Impp = {impp:.3f} A")
print(f"  Pmpp = {pmpp:.2f} W")

# 计算填充因子
FF = pmpp / (module.Voc * module.Isc)
print(f"  FF   = {FF:.4f} ({FF*100:.2f}%)")
```python

### 4. 分析不同配置

```python
# 创建不同配置的组件
configs = [
    (36, 2, "36片传统组件"),
    (60, 3, "60片标准组件"),
    (72, 3, "72片大功率组件"),
]

for Ns, Nb, name in configs:
    mod = PVModule(cell_model=cell, Ns=Ns, Nb=Nb, name=name)
    v, i, p = mod.find_mpp()
    print(f"{name}: Voc={mod.Voc:.1f}V, Pmpp={p:.1f}W")
```python

输出:
```
36片传统组件: Voc=21.6V, Pmpp=129.6W
60片标准组件: Voc=36.0V, Pmpp=216.0W
72片大功率组件: Voc=43.2V, Pmpp=259.2W
```python

### 5. 模拟部分遮挡

```python
# 设置非均匀辐照度
irradiances = [1000.0] * 40 + [200.0] * 20  # 后20片遮挡

module.set_cell_irradiance(irradiances)

# 重新计算MPP
vmpp_shaded, impp_shaded, pmpp_shaded = module.find_mpp()

print(f"部分遮挡条件:")
print(f"  Pmpp = {pmpp_shaded:.2f} W")
print(f"  功率损失 = {pmpp - pmpp_shaded:.2f} W")
```python

---

## 🧪 实验内容

### 实验1: 不同串联片数对比

**目标**: 研究串联片数对组件性能的影响

**步骤**:
1. 创建36/60/72/96片组件
2. 计算各配置的Voc、Isc、Pmpp
3. 绘制对比图表
4. 验证线性缩放关系

**运行**:
```bash
cd code/examples/case_03_pv_module_modeling
python3 experiments.py  # 选择实验1
```matlab

**关键发现**:
- 电压与片数成正比: Voc = Ns × Voc_cell
- 电流保持不变: Isc ≈ Isc_cell
- 功率与片数成正比: Pmpp ≈ Ns × Pmpp_cell

### 实验2: 部分遮挡效应分析

**目标**: 分析不同遮挡程度的功率损失

**场景**:
1. 无遮挡(基准)
2. 1片遮挡50%
3. 5片遮挡50%
4. 1组遮挡50% (20片)
5. 1组全遮挡 (20片)

**预期结果**:
- 轻微遮挡: 损失5-10%
- 整组遮挡: 损失30-50%
- 旁路二极管可减少损失

### 实验3: 旁路二极管作用演示

**目标**: 理解旁路二极管的保护机制

**内容**:
- 旁路二极管工作原理图解
- 有/无旁路二极管对比
- 热斑效应说明

**关键点**:
- 正常: 二极管截止
- 遮挡: 二极管导通,保护电池
- 必要性: 防止永久损坏

### 实验4: 功率扩展分析

**目标**: 验证线性缩放特性

**方法**:
- 测试Ns = 12, 24, 36, 48, 60, 72, 84, 96
- 绘制Voc vs Ns, Pmpp vs Ns
- 线性拟合验证

**预期关系**:
```
Voc(Ns) = slope × Ns + intercept
Pmpp(Ns) = slope × Ns + intercept
```matlab

---

## 📊 典型配置参数

### 标准组件类型

| 类型 | 片数Ns | 二极管Nb | Voc(V) | Isc(A) | Pmpp(W) | 应用场景 |
|------|--------|----------|--------|--------|---------|----------|
| 小型 | 36     | 2        | 21.6   | 8.0    | 130     | 离网系统 |
| 标准 | 60     | 3        | 36.0   | 8.0    | 216     | 屋顶并网 |
| 大功率 | 72   | 3        | 43.2   | 8.0    | 259     | 地面电站 |
| 超大 | 96     | 4        | 57.6   | 8.0    | 346     | 大型项目 |

### 商业组件示例

**隆基 LR5-72HPH-540M** (72片):
- Pmpp: 540W
- Voc: 49.15V
- Isc: 13.93A
- Vmpp: 41.65V
- Impp: 12.97A
- 效率: 21.1%

**晶科 Tiger Pro JKM580M-72HL4-V** (72片):
- Pmpp: 580W
- Voc: 49.80V
- Isc: 14.87A
- Vmpp: 41.99V
- Impp: 13.81A
- 效率: 22.3%

---

## 🎯 工程应用

### 1. 组件选型

**小型离网系统** (家庭):
- 选择: 36片组件
- 电压: 12V/24V电池系统
- 功率: 100-200W

**屋顶并网系统** (住宅/商业):
- 选择: 60片组件
- 电压: 适配并网逆变器(30-40V)
- 功率: 300-400W

**地面电站** (MW级):
- 选择: 72片或更大
- 电压: 高压并网(40-50V)
- 功率: 400-600W

### 2. 组串设计

**串联数量计算**:
```python
# 逆变器输入电压范围: 200-850V
V_mppt_min = 200  # V
V_mppt_max = 850  # V

# 组件Vmpp = 41V
Vmpp_module = 41.0

# 计算串联数量
Ns_min = V_mppt_min / Vmpp_module  # 4.9 → 5片
Ns_max = V_mppt_max / Vmpp_module  # 20.7 → 20片

print(f"串联数量范围: {int(Ns_min)}-{int(Ns_max)} 片")
```python

### 3. 遮挡影响评估

**方法**:
```python
def evaluate_shading_loss(Ns, Nb, shaded_cells, shade_level):
    """
    评估遮挡损失
    
    Parameters:
    -----------
    Ns : 总片数
    Nb : 旁路二极管数量
    shaded_cells : 被遮挡电池数量
    shade_level : 遮挡程度 (0-1)
    
    Returns:
    --------
    power_loss : 功率损失百分比
    """
    # 简化估算
    cells_per_bypass = Ns // Nb
    affected_groups = (shaded_cells // cells_per_bypass) + 1
    
    if shade_level > 0.5:
        # 严重遮挡,旁路导通
        loss = (affected_groups / Nb) * 100
    else:
        # 轻微遮挡
        loss = (shaded_cells / Ns) * shade_level * 100
    
    return loss

# 示例
loss = evaluate_shading_loss(60, 3, 20, 0.8)
print(f"预计功率损失: {loss:.1f}%")
```python

### 4. 热斑检测

**红外热成像检测**:
- 正常温度: 40-60°C
- 热斑温度: 80-150°C
- 危险阈值: >100°C

**检测周期**:
- 新装: 1个月
- 运行: 每年1-2次
- 异常: 立即检查

---

## 🔧 参数设计

### 旁路二极管选型

**电气参数**:
- 额定电流: ≥ 1.5 × Isc (典型12A)
- 正向压降: 0.5-0.9V (典型0.7V)
- 反向耐压: ≥ Voc × Ns/Nb (典型20V)

**常用型号**:
- 肖特基二极管: SS34, SS36
- 快恢复二极管: MUR160

### 接线盒设计

**结构**:
```
┌─────────────────┐
│   接线盒        │
│  ┌──┐ ┌──┐ ┌──┐│
│  │D1│ │D2│ │D3││  (3个旁路二极管)
│  └──┘ └──┘ └──┘│
│  [+]      [-]   │  (正负端子)
└─────────────────┘
```

**防护等级**: IP65/IP67

---

## 💡 进阶思考

### 思考题

1. **电压分配**: 为什么60片组件电压约36V而不是正好36V?

2. **失配损失**: 如果60片中有1片性能下降10%,整个组件功率会下降多少?

3. **旁路设计**: 为什么通常3个旁路二极管而不是6个或更多?

4. **双面组件**: 如果组件背面也能发电,如何建模?

---

## 📝 作业

### 基础题

**作业1**: 创建一个72片组件,计算其Voc、Isc、Pmpp,并与60片组件对比。

**作业2**: 设计一个适配48V电池系统的组件配置(选择Ns和Nb)。

**作业3**: 分析遮挡程度(0%, 25%, 50%, 75%, 100%)对组件功率的影响。

### 进阶题

**作业4**: 实现一个更精确的遮挡模型,考虑每片电池的实际辐照度。

**作业5**: 设计一个组件性能测试程序,输出标准测试报告(STC条件)。

**作业6**: 分析温度不均匀分布(如边缘温度高5°C)的影响。

### 挑战题

**作业7**: 实现多峰值MPPT算法,处理部分遮挡条件。

**作业8**: 设计一个热斑检测算法,基于电流-电压曲线识别异常。

**作业9**: 建立一个组件退化模型,模拟25年寿命期的性能衰减。

---

## 📚 参考资料

### 标准

- IEC 61215: 晶体硅光伏组件设计鉴定
- IEC 61730: 光伏组件安全鉴定
- IEC 61853: 光伏组件性能测试

### 文献

1. King, D. L., et al. "Photovoltaic module and array performance characterization methods for all system operating conditions." 
2. Bishop, J. W. "Computer simulation of the effects of electrical mismatches in photovoltaic cell interconnection circuits."
3. Quaschning, V., & Hanitsch, R. "Numerical simulation of current-voltage characteristics of photovoltaic systems with shaded solar cells."

### 在线资源

- NREL PVWatts Calculator
- PVsyst Software Documentation
- Sandia PV Performance Model

---

## ✅ 检查清单

完成本案例后,你应该能够:

- [ ] 创建不同配置的光伏组件模型
- [ ] 计算组件的I-V和P-V特性曲线
- [ ] 理解串联电池的电气特性
- [ ] 解释旁路二极管的工作原理
- [ ] 分析部分遮挡对功率的影响
- [ ] 评估不同配置的适用场景
- [ ] 进行组件选型和组串设计
- [ ] 识别和预防热斑效应

---

**案例3完成!** 🎉

下一步: [案例4 - 光伏阵列配置](../case_04_pv_array_modeling/README.md)
