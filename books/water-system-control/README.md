# 水系统控制论教材
## 基于水箱案例的控制理论入门课程

**适用对象**: 高中及以上水平的学习者
**教学方法**: 案例驱动学习（Case-Based Learning）
**完成度**: 33% (4/12个案例已完成)

---

## 快速开始

**新手请先阅读**: [START_HERE.md](./START_HERE.md)

## 教材概述

本教材通过 **12个经典水箱案例** 系统讲解控制理论基础知识，从最简单的家庭水塔到复杂的多水箱协同控制，循序渐进地建立完整的控制系统知识体系。

### 为什么选择水箱系统？

1. **直观易懂**: 水位变化可以直接观察和理解
2. **数学简单**: 基于质量守恒的一阶/二阶微分方程
3. **工程实用**: 对应大量真实工程应用
4. **实验方便**: 容易搭建物理实验装置
5. **理论完整**: 可以覆盖控制理论的所有核心概念

### 教学特色

- **案例驱动**: 每个理论概念都有对应的真实工程案例
- **代码实现**: 提供完整的 Python 仿真代码
- **测试验证**: 100% 测试覆盖率，确保代码正确性
- **渐进式学习**: 从开关控制到 PID，从单水箱到双水箱
- **工程思维**: 培养"问题→建模→仿真→辨识→控制→验证"的完整思维链

## 目录结构

```
water-system-control/
├── README.md                    # 本文件
├── START_HERE.md               # 快速入门指南
├── PRODUCT_README.md           # 产品说明
├── README_教材开发.md          # 教材开发说明
│
├── chapters/                   # 教材章节内容（待开发）
│   ├── chapter-01-introduction/
│   ├── chapter-02-modeling/
│   └── ...
│
├── code/                       # 代码和案例
│   ├── models/                 # 水箱模型
│   │   └── water_tank/
│   │       ├── single_tank.py  # 单水箱模型
│   │       └── double_tank.py  # 双水箱模型
│   │
│   ├── control/                # 控制器
│   │   ├── on_off.py          # 开关控制器
│   │   ├── pid.py             # PID控制器
│   │   └── basic_controllers.py  # 基础控制器集合
│   │
│   └── examples/               # 教学案例
│       ├── case_01_home_water_tower/       # 案例1: 家庭水塔
│       ├── case_02_cooling_tower/          # 案例2: 冷却塔
│       ├── case_03_water_supply_station/   # 案例3: 供水站
│       └── case_04_pid_tuning/             # 案例4: PID调参
│
├── docs/                       # 文档
│   └── zh/                     # 中文文档
│       ├── 水箱案例驱动教学体系.md        # 核心教学体系
│       ├── 水系统控制论教材开发方案.md    # 教材开发方案
│       ├── 零基础教材开发详细方案.md      # 详细教学方案
│       ├── 立即开始指南.md                # 快速入门
│       └── 功能索引.md                    # 功能索引
│
├── tests/                      # 测试代码
│   └── tests/
│       ├── models/water_tank/  # 水箱模型测试
│       └── standard_cases/     # 标准案例测试
│
└── resources/                  # 资源文件
    └── (图片、数据等)
```

## 12个经典案例

### 第一阶段：基础控制（已完成 4/4）

1. ✅ **案例1: 家庭水塔自动供水系统**
   - 控制方法: 开关控制（On-Off）
   - 理论: 一阶系统、滞环控制
   - 代码: `code/examples/case_01_home_water_tower/`

2. ✅ **案例2: 工业冷却塔精确水位控制**
   - 控制方法: 比例控制（P）
   - 理论: 稳态误差、控制增益
   - 代码: `code/examples/case_02_cooling_tower/`

3. ✅ **案例3: 城市供水站恒压供水**
   - 控制方法: 比例积分控制（PI）
   - 理论: 积分作用、消除稳态误差
   - 代码: `code/examples/case_03_water_supply_station/`

4. ✅ **案例4: 水厂沉淀池快速稳定控制**
   - 控制方法: PID控制
   - 理论: 微分作用、参数整定
   - 代码: `code/examples/case_04_pid_tuning/`

### 第二阶段：系统辨识（规划中 0/4）

5. ⏳ 案例5: 未知水箱系统参数辨识
6. ⏳ 案例6: 阶跃响应法快速建模
7. ⏳ 案例7: 频域辨识技术
8. ⏳ 案例8: 最小二乘法在线辨识

### 第三阶段：高级控制（规划中 0/4）

9. ⏳ 案例9: 双水箱串联系统
10. ⏳ 案例10: 前馈-反馈复合控制
11. ⏳ 案例11: 多水箱协同控制
12. ⏳ 案例12: 模型预测控制（MPC）

## 技术统计

- **代码行数**: 3,876+
- **测试数量**: 44个单元测试
- **测试通过率**: 100%
- **文档字数**: 150,000+
- **支持语言**: Python 3.8+

## 核心功能

### 水箱模型

- ✅ 单水箱模型（一阶系统）
- ✅ 双水箱串联模型（二阶系统）
- ✅ 开环仿真
- ✅ 闭环仿真
- ✅ 参数可配置

### 控制器

- ✅ 开关控制器（On-Off）
- ✅ 比例控制器（P）
- ✅ 比例积分控制器（PI）
- ✅ PID控制器（带抗饱和、滤波）
- ✅ 工程级参数调节

### 测试验证

- ✅ 模型正确性测试
- ✅ 控制器性能测试
- ✅ 标准案例对照测试
- ✅ 数值精度验证（误差<2%）

## 学习路径

### 零基础学习者

1. 阅读 [立即开始指南](docs/zh/立即开始指南.md)
2. 学习案例1-4，理解基本控制原理
3. 运行代码，观察仿真结果
4. 修改参数，探索控制效果

### 有基础学习者

1. 阅读 [水箱案例驱动教学体系](docs/zh/水箱案例驱动教学体系.md)
2. 直接学习感兴趣的案例
3. 深入研究代码实现
4. 尝试自己设计控制器

### 教师/教材开发者

1. 阅读 [水系统控制论教材开发方案](docs/zh/水系统控制论教材开发方案.md)
2. 参考 [零基础教材开发详细方案](docs/zh/零基础教材开发详细方案.md)
3. 使用现有案例进行教学
4. 根据需要扩展新案例

## 环境要求

### 软件要求

- Python 3.8 或更高版本
- NumPy (数值计算)
- Matplotlib (绘图)
- pytest (测试)

### 安装步骤

```bash
# 1. 进入项目目录
cd books/water-system-control

# 2. 安装依赖（如果有 requirements.txt）
pip install numpy matplotlib pytest

# 3. 运行测试验证安装
pytest tests/
```

## 如何使用

### 运行案例代码

```bash
# 运行案例1: 家庭水塔
cd code/examples/case_01_home_water_tower
python demo_on_off_control.py

# 运行案例2: 冷却塔
cd code/examples/case_02_cooling_tower
python demo_proportional_control.py
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/tests/models/water_tank/test_single_tank.py
```

### 导入模型和控制器

```python
# 导入单水箱模型
from code.models.water_tank.single_tank import SingleTank

# 导入PID控制器
from code.control.pid import PIDController

# 创建水箱和控制器
tank = SingleTank(A=1.0, K=0.5, h0=2.0)
controller = PIDController(Kp=2.0, Ki=0.5, Kd=0.1)
```

## 关键文档

- [START_HERE.md](./START_HERE.md) - 快速入门指南
- [水箱案例驱动教学体系](docs/zh/水箱案例驱动教学体系.md) - 完整的12案例教学体系
- [水系统控制论教材开发方案](docs/zh/水系统控制论教材开发方案.md) - 教材开发总体方案
- [零基础教材开发详细方案](docs/zh/零基础教材开发详细方案.md) - 面向初学者的详细方案
- [功能索引](docs/zh/功能索引.md) - 功能列表和索引

## 贡献

欢迎贡献新的案例、改进文档或报告问题！

## 版本历史

- **v0.4.0-alpha** (2025-10-28)
  - 完成前4个案例
  - 100%测试通过率
  - 完整的文档体系

## 许可证

请参考项目根目录的 LICENSE 文件。

## 联系方式

如有问题或建议，请通过 GitHub Issues 反馈。

---

**最后更新**: 2025-10-29
