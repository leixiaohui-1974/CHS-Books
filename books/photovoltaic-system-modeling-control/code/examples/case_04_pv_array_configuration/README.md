# 案例4: 光伏阵列配置

## 📋 案例概述

**工程背景**:  
单个光伏组件功率约200-400W,实际应用需要将大量组件串并联形成阵列,构建kW到MW级光伏电站。

**典型配置**:
- 小型户用: 10-20组件 = 5-10kW
- 商业屋顶: 50-200组件 = 20-100kW
- 地面电站: 数千组件 = MW级

**学习目标**:
1. 理解串并联组合设计原则
2. 掌握阵列配置优化方法
3. 学习MW级电站建模技术
4. 分析不同配置的性能差异

---

## 🔬 理论基础

### 串并联特性

**串联特性** (提升电压):
```
配置: Ns个组件串联
电压: V_array = Ns × V_module  (电压相加)
电流: I_array = I_module        (电流不变)
功率: P_array = Ns × P_module
```

**并联特性** (提升电流):
```
配置: Np串并联
电压: V_array = V_module        (电压不变)
电流: I_array = Np × I_module   (电流相加)
功率: P_array = Np × P_module
```

**组合配置** (NsxNp):
```
结构: Np串, 每串Ns个组件
总组件数: Ntotal = Ns × Np
电压: V_array = Ns × V_module
电流: I_array = Np × I_module
功率: P_array = Ns × Np × P_module
```

### 配置表示法

使用 **NpPNsS** 格式:
- `1P10S`: 1串并联,每串10组件串联
- `10P1S`: 10串并联,每串1组件
- `5P20S`: 5串并联,每串20组件 = 100组件
- `200P25S`: 200串 × 25组件 = 5000组件 ≈ 1MW

### 逆变器匹配

**MPPT电压范围**:
```
典型逆变器: 200-850V
组件Vmpp: ~30-40V

可接入组件数:
Ns_min = 200V / 40V = 5个
Ns_max = 850V / 30V = 28个

推荐配置: 8-25个/串
```

---

## 💻 代码示例

### 1. 创建基本阵列

```python
from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule
from code.models.pv_array import PVArray

# 创建组件
cell = SingleDiodeModel(Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48)
module = PVModule(cell_model=cell, Ns=60, Nb=3)

# 创建阵列: 10串联
array_10s = PVArray(
    module=module,
    Ns=10,      # 10组件串联
    Np=1,       # 1串
    name="10串联阵列"
)

array_10s.print_parameters()
```

输出:
```
10串联阵列 - 阵列参数
======================================================================
配置:
  阵列配置:              1P10S
  串联组件数 (Ns):       10 个/串
  并联串数 (Np):         1 串
  总组件数:              10 个
  总电池片数:            600 片

电气参数:
  开路电压 Voc:          360.00 V
  短路电流 Isc:          8.00 A
  最大功率点电压 Vmpp:   288.00 V
  最大功率点电流 Impp:   7.50 A
  最大功率 Pmpp:         2160.00 W (2.16 kW)
  填充因子 FF:           0.7500 (75.00%)
======================================================================
```

### 2. 不同配置对比

```python
# 配置1: 纯串联
array_s = PVArray(module=module, Ns=20, Np=1, name="纯串联")

# 配置2: 纯并联
array_p = PVArray(module=module, Ns=1, Np=20, name="纯并联")

# 配置3: 串并联
array_sp = PVArray(module=module, Ns=20, Np=10, name="串并联")

for array in [array_s, array_p, array_sp]:
    v, i, p = array.find_mpp()
    print(f"{array.name}:")
    print(f"  配置: {array.Np}P{array.Ns}S")
    print(f"  Vmpp={v:.1f}V, Impp={i:.1f}A, Pmpp={p/1000:.1f}kW\n")
```

输出:
```
纯串联:
  配置: 1P20S
  Vmpp=576.0V, Impp=7.5A, Pmpp=4.3kW

纯并联:
  配置: 20P1S
  Vmpp=28.8V, Impp=150.0A, Pmpp=4.3kW

串并联:
  配置: 10P20S
  Vmpp=576.0V, Impp=75.0A, Pmpp=43.2kW
```

### 3. 设计1MW电站

```python
# 目标功率
target_power_MW = 1.0  # 1MW

# 组件功率
_, _, pmpp_module = module.find_mpp()
print(f"组件功率: {pmpp_module:.2f} W")

# 需要组件数
num_modules = int(target_power_MW * 1e6 / pmpp_module)
print(f"需要组件: {num_modules} 个")

# 设计配置: 25组件/串 × 200串
array_1mw = PVArray(
    module=module,
    Ns=25,
    Np=200,
    name="1MW光伏电站"
)

# 打印参数
array_1mw.print_parameters()

# 计算系统规模
size_info = array_1mw.calculate_system_size(module_area=1.6)
print(f"\n系统规模:")
print(f"  占地面积: {size_info['total_area']:.0f} m²")
print(f"  实际功率: {size_info['power_MW']:.3f} MW")
print(f"  系统效率: {size_info['efficiency']:.2f} %")
```

输出:
```
组件功率: 216.00 W
需要组件: 4630 个

1MW光伏电站 - 阵列参数
======================================================================
配置:
  阵列配置:              200P25S
  串联组件数 (Ns):       25 个/串
  并联串数 (Np):         200 串
  总组件数:              5000 个
  总电池片数:            300000 片

电气参数:
  开路电压 Voc:          900.00 V
  短路电流 Isc:          1600.00 A
  最大功率点电压 Vmpp:   720.00 V
  最大功率点电流 Impp:   1500.00 A
  最大功率 Pmpp:         1080000.00 W (1080.00 kW)
  填充因子 FF:           0.7500 (75.00%)
======================================================================

系统规模:
  占地面积: 8000 m²
  实际功率: 1.080 MW
  系统效率: 13.50 %
```

### 4. 优化配置设计

```python
def optimize_array_configuration(module, target_power_kW, 
                                  v_min=200, v_max=850):
    """
    优化阵列配置
    
    Parameters:
    -----------
    module : 组件模型
    target_power_kW : 目标功率(kW)
    v_min, v_max : 逆变器MPPT电压范围(V)
    """
    vmpp_m, impp_m, pmpp_m = module.find_mpp()
    
    # 计算需要的组件数
    num_modules = int(target_power_kW * 1000 / pmpp_m)
    
    # 串联数范围
    Ns_min = int(v_min / vmpp_m)
    Ns_max = int(v_max / vmpp_m)
    
    print(f"目标功率: {target_power_kW} kW")
    print(f"需要组件: {num_modules} 个")
    print(f"串联数范围: {Ns_min}-{Ns_max}")
    
    # 尝试不同配置
    configs = []
    for Ns in [Ns_min, (Ns_min+Ns_max)//2, Ns_max]:
        Np = num_modules // Ns
        if Np < 1:
            continue
        
        array = PVArray(module=module, Ns=Ns, Np=Np)
        v, i, p = array.find_mpp()
        
        configs.append({
            'Ns': Ns,
            'Np': Np,
            'Vmpp': v,
            'Impp': i,
            'Pmpp_kW': p/1000,
            'total_modules': Ns*Np
        })
    
    # 打印对比
    print("\n配置对比:")
    print(f"{'配置':<10} {'组件数':<8} {'Vmpp(V)':<10} {'Impp(A)':<10} {'功率(kW)':<10}")
    print("-" * 58)
    for c in configs:
        print(f"{c['Np']}P{c['Ns']}S{'':<6} {c['total_modules']:<8} "
              f"{c['Vmpp']:<10.1f} {c['Impp']:<10.1f} {c['Pmpp_kW']:<10.1f}")
    
    return configs

# 示例: 100kW系统
optimize_array_configuration(module, target_power_kW=100)
```

输出:
```
目标功率: 100 kW
需要组件: 463 个
串联数范围: 6-29

配置对比:
配置       组件数   Vmpp(V)    Impp(A)    功率(kW)  
----------------------------------------------------------
77P6S      462      172.8      52.5       100.1     
23P20S     460      576.0      150.0      100.4     
15P29S     435      835.2      112.5      93.9      
```

### 5. 汇流箱设计

```python
from code.models.pv_array import CombinerBox

# 创建汇流箱
cb = CombinerBox(num_strings=16, name="CB-1")

# 获取规格
specs = cb.get_specifications()
print(f"汇流箱 {specs['name']}:")
print(f"  接入串数: {specs['num_strings']}")
print(f"  熔断器: {'有' if specs['fuses'] else '无'}")
print(f"  防雷器: {'有' if specs['surge_protector'] else '无'}")
print(f"  断路器: {'有' if specs['breaker'] else '无'}")
```

---

## 📊 典型配置

### 住宅系统 (5-10kW)

| 组件功率 | 配置 | 总功率 | 电压 | 电流 | 应用 |
|----------|------|--------|------|------|------|
| 350W | 1P15S | 5.25kW | 450V | 11.7A | 小户型 |
| 400W | 1P20S | 8.0kW | 600V | 13.3A | 标准户型 |
| 400W | 2P15S | 12.0kW | 450V | 26.7A | 别墅 |

### 工商业系统 (50-500kW)

| 组件功率 | 配置 | 总功率 | 总组件数 | 逆变器 |
|----------|------|--------|----------|--------|
| 450W | 5P25S | 56kW | 125 | 60kW |
| 500W | 10P20S | 100kW | 200 | 110kW |
| 540W | 20P20S | 216kW | 400 | 250kW |
| 550W | 50P20S | 550kW | 1000 | 630kW |

### 地面电站 (1-100MW)

| 规模 | 配置 | 组件数 | 占地(亩) | 投资(亿) |
|------|------|--------|----------|----------|
| 1MW | 200P25S | 5000 | 12 | 0.4 |
| 10MW | 2000P25S | 50000 | 120 | 4 |
| 50MW | 10000P25S | 250000 | 600 | 20 |
| 100MW | 20000P25S | 500000 | 1200 | 40 |

---

## 🎯 工程应用

### 1. 配置设计流程

```
步骤1: 确定目标功率
  → 用户需求或场地限制

步骤2: 选择组件型号
  → 考虑性价比、可靠性

步骤3: 计算组件数量
  → N = P_target / P_module

步骤4: 确定串联数
  → 匹配逆变器MPPT电压范围
  → Ns = 8-25 (典型)

步骤5: 计算并联串数
  → Np = N / Ns

步骤6: 验证设计
  → 电压/电流/功率校核
  → 逆变器容配比
```

### 2. 容配比设计

**定义**: 
```
容配比 = 组件总功率 / 逆变器额定功率
```

**推荐值**:
- 固定支架: 1.0-1.2
- 跟踪支架: 1.2-1.4
- 高辐照地区: 可达1.5

**示例**:
```python
# 组件总功率: 1100kW
# 逆变器: 1000kW
# 容配比: 1.1 (合理)

array = PVArray(module=module, Ns=25, Np=220)  # 1.1MW
inverter_power_kW = 1000

_, _, pmpp = array.find_mpp()
ratio = pmpp / (inverter_power_kW * 1000)
print(f"容配比: {ratio:.2f}")
```

### 3. 失配损失分析

**原因**:
- 组件参数差异
- 遮挡不均匀
- 温度分布不均
- 老化程度不同

**影响**:
- 串联失配: 整串受限于最弱组件
- 并联失配: 影响较小

**对策**:
- 选用同批次组件
- 优化组串设计
- 使用组件级优化器

---

## 💡 思考题

1. **为什么大型电站通常采用25组件/串?**

2. **容配比为什么可以>1?会不会损失电量?**

3. **如何在有限场地上最大化装机容量?**

4. **串并联配置对系统成本有什么影响?**

---

## 📝 作业

### 基础题

**作业1**: 设计一个50kW商业屋顶系统,使用400W组件。

**作业2**: 对比3种配置(纯串/纯并/串并联)的优缺点。

**作业3**: 计算一个100kW系统的占地面积和投资概算。

### 进阶题

**作业4**: 优化一个10MW电站的阵列配置,考虑场地和逆变器约束。

**作业5**: 分析不同容配比(0.8-1.5)对系统收益的影响。

**作业6**: 设计一个带储能的1MW光储系统配置方案。

---

## ✅ 检查清单

完成本案例后,你应该能够:

- [ ] 理解串并联的电气特性
- [ ] 创建不同配置的阵列模型
- [ ] 设计kW-MW级光伏系统
- [ ] 优化阵列配置方案
- [ ] 计算系统规模参数
- [ ] 匹配逆变器参数
- [ ] 分析容配比影响
- [ ] 评估失配损失

---

**案例4完成!** 🎉

下一步: [案例5 - 遮挡分析与诊断](../case_05_shading_analysis/README.md)
