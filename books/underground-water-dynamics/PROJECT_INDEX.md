# 地下水动力学模型教材 - 项目索引

> **完整的文件导航和快速参考**

---

## 📂 项目结构总览

```
underground-water-dynamics/
├── 📖 文档目录 (Documentation)
├── 📦 gwflow工具包 (Core Package)
├── 💻 案例代码 (Examples)
├── 🧪 测试套件 (Tests)
└── 📊 数据集 (Data)
```

---

## 📖 核心文档

### 入门文档（必读）

| 文档 | 描述 | 字数 | 状态 |
|------|------|------|------|
| [README.md](README.md) | 项目概述和快速开始 | 2,000 | ✅ |
| [START_HERE.md](START_HERE.md) | 快速入门指南 | 4,000 | ✅ |
| [INSTALL.md](INSTALL.md) | 详细安装指南 | 2,000 | ✅ |

**推荐阅读顺序**：README → START_HERE → INSTALL

### 设计文档

| 文档 | 描述 | 字数 | 状态 |
|------|------|------|------|
| [教程提纲-完整版.md](教程提纲-完整版.md) | 详细教材方案 | 15,000 | ✅ |
| [项目总结.md](项目总结.md) | 方案设计总结 | 4,000 | ✅ |
| [DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md) | 开发进度总结 | 6,000 | ✅ |

### 依赖文件

| 文件 | 描述 | 状态 |
|------|------|------|
| [requirements.txt](requirements.txt) | Python依赖包列表 | ✅ |
| [setup.py](setup.py) | 安装配置文件 | ✅ |

---

## 📦 gwflow工具包

### 模块结构

```
gwflow/
├── __init__.py              # 包初始化
├── grid/                    # 网格生成模块
│   ├── __init__.py
│   └── structured.py        # 结构化网格 ✅
├── solvers/                 # 求解器模块
│   ├── __init__.py
│   ├── steady_state.py      # 稳态求解器 ✅
│   └── transient.py         # 瞬态求解器 ✅
├── visualization/           # 可视化模块
│   ├── __init__.py
│   └── plots.py             # 绘图功能 ✅
└── utils/                   # 工具模块
    ├── __init__.py
    ├── validation.py        # 参数验证 ✅
    └── units.py             # 单位转换 ✅
```

### 核心功能列表

#### 1. 网格生成 (`gwflow.grid`)

| 函数 | 功能 | 状态 |
|------|------|------|
| `create_1d_grid()` | 一维均匀网格 | ✅ |
| `create_2d_grid()` | 二维矩形网格 | ✅ |
| `create_3d_grid()` | 三维长方体网格 | ✅ |
| `refine_grid_2d()` | 二维网格加密 | ✅ |

#### 2. 稳态求解器 (`gwflow.solvers.steady_state`)

| 函数 | 功能 | 状态 |
|------|------|------|
| `solve_1d_steady_gw()` | 一维稳态求解 | ✅ |
| `solve_2d_steady_gw()` | 二维稳态求解 | ✅ |
| `compute_darcy_velocity()` | 达西速度计算 | ✅ |

#### 3. 瞬态求解器 (`gwflow.solvers.transient`)

| 函数 | 功能 | 状态 |
|------|------|------|
| `solve_2d_transient_gw()` | 二维瞬态求解（隐式/显式） | ✅ |
| `compute_drawdown()` | 降深计算 | ✅ |

#### 4. 可视化 (`gwflow.visualization`)

| 函数 | 功能 | 状态 |
|------|------|------|
| `plot_1d_head()` | 一维水头分布图 | ✅ |
| `plot_2d_head()` | 二维等值线图 | ✅ |
| `plot_2d_velocity()` | 流速场矢量图 | ✅ |
| `plot_transient_animation()` | 瞬态动画 | ✅ |
| `plot_comparison()` | 数值解与解析解对比 | ✅ |

#### 5. 工具函数 (`gwflow.utils`)

| 函数 | 功能 | 状态 |
|------|------|------|
| `validate_parameters()` | 参数验证 | ✅ |
| `convert_units()` | 单位转换 | ✅ |

---

## 💻 案例代码

### 第一篇：基础理论与数值方法

#### ✅ 案例1：一维稳态地下水流动

**路径**: `code/examples/case_01/`

| 文件 | 描述 | 行数 | 状态 |
|------|------|------|------|
| `case_01_1d_steady.py` | 主程序 | 300 | ✅ |
| `README.md` | 教程文档 | - | ✅ |

**学习重点**:
- ✅ 达西定律
- ✅ 有限差分法
- ✅ 边界条件处理
- ✅ 与解析解对比
- ✅ 网格收敛性分析

**输出图形**:
- `case_01_comparison.png` - 数值解与解析解对比
- `case_01_velocity.png` - 达西速度分布
- `case_01_convergence.png` - 网格收敛性分析

---

#### ✅ 案例2：二维稳态流动与网格剖分

**路径**: `code/examples/case_02/`

| 文件 | 描述 | 行数 | 状态 |
|------|------|------|------|
| `case_02_2d_steady.py` | 主程序 | 450 | ✅ |
| `README.md` | 教程文档 | - | ✅ |

**学习重点**:
- ✅ 二维网格剖分
- ✅ Dirichlet和Neumann边界条件
- ✅ 二维可视化
- ✅ 网格独立性验证
- ✅ 抽水井影响分析

**输出图形**:
- `case_02_head_contour.png` - 水头等值线图
- `case_02_velocity.png` - 流速场矢量图
- `case_02_centerline.png` - 中心线水头分布
- `case_02_grid_independence.png` - 网格独立性分析
- `case_02_pumping.png` - 抽水影响
- `case_02_drawdown.png` - 降深分布

---

#### ⏳ 案例3：非均质含水层模拟

**路径**: `code/examples/case_03/`

**状态**: ⏳ 待开发

**计划功能**:
- 分区非均质K场
- 随机场生成
- 地质统计插值
- 透镜体影响

---

#### ✅ 案例4：瞬态地下水流动

**路径**: `code/examples/case_04/`

| 文件 | 描述 | 行数 | 状态 |
|------|------|------|------|
| `case_04_transient.py` | 主程序 | 500 | ✅ |
| `README.md` | 教程文档 | - | ✅ |

**学习重点**:
- ✅ 瞬态渗流方程
- ✅ 隐式/显式时间离散
- ✅ 储水系数作用
- ✅ 抽水试验模拟
- ✅ Theis解析解对比

**输出图形**:
- `case_04_final_head.png` - 最终水头分布
- `case_04_drawdown.png` - 降落漏斗
- `case_04_well_head_time.png` - 井处水头时间曲线
- `case_04_drawdown_time.png` - 降深时间曲线
- `case_04_profile_comparison.png` - 与Theis解对比
- `case_04_multi_time.png` - 多时刻降深分布
- `case_04_animation.gif` - 瞬态动画

---

#### ⏳ 案例5：有限元方法基础

**路径**: `code/examples/case_05/`

**状态**: ⏳ 待开发

**计划功能**:
- 三角形网格生成（meshpy）
- Galerkin有限元
- 单元刚度矩阵
- 复杂几何边界

---

### 第二篇：参数率定与不确定性分析

**状态**: ⏳ 待开发（案例6-10）

---

### 第三篇：地表地下水耦合系统

**状态**: ⏳ 待开发（案例11-15）

---

### 第四篇：人类活动影响评估

**状态**: ⏳ 待开发（案例16-18）

---

### 第五篇：智能化与数字孪生

**状态**: ⏳ 待开发（案例19-20）

---

## 🧪 测试套件

### 测试文件

| 文件 | 测试模块 | 测试数 | 状态 |
|------|----------|--------|------|
| `tests/test_grid.py` | 网格生成 | 10 | ✅ |
| `tests/test_solvers.py` | 求解器 | 15 | ✅ |
| `tests/run_simple_tests.py` | 简单测试运行器 | 4 | ✅ |

### 运行测试

```bash
# 方法1：使用pytest（推荐）
cd /workspace/books/underground-water-dynamics
pytest tests/ -v

# 方法2：简单测试（不需要pytest）
python3 tests/run_simple_tests.py
```

---

## 📊 数据集

### 目录结构

```
data/
├── synthetic/          # 合成数据
│   └── (待添加)
└── real_world/         # 真实数据
    └── (待添加)
```

**状态**: ⏳ 待添加

**计划数据集**:
- 标准测试数据
- 华北平原地下水数据
- 美国高平原含水层数据

---

## 🎓 学习路径

### 路径1：本科生（8周）

```
Week 1-2: 案例1, 2 → 基础建模
Week 3: 案例3, 4 → 进阶方法
Week 4: 案例5 → 有限元
Week 5: 案例6 → 参数率定入门
Week 6-7: 综合项目
Week 8: 总结答辩
```

### 路径2：研究生（16周）

```
Week 1-2: 快速回顾案例1-5
Week 3-6: 案例6-10 → 参数率定深入
Week 7-10: 案例11-18 → 耦合与应用
Week 11-12: 案例19-20 → 智能化
Week 13-16: 研究项目 + 论文
```

### 路径3：工程师（8周）

```
Week 1: 案例2, 4 → 核心方法
Week 2-3: 案例6, 7, 14 → 率定与工具
Week 4: 案例15, 16 → 3D与优化
Week 5-8: 真实项目演练
```

### 路径4：科研人员（16周）

```
Week 1-2: 快速浏览案例1-8
Week 3-4: 深入案例9-10 → 系统辨识
Week 5-6: 案例19 → 数字孪生
Week 7-8: 案例20 → 智能决策
Week 9-12: 创新研究
Week 13-16: 论文撰写
```

---

## 📈 开发进度

### 整体进度：35%

```
[████████████░░░░░░░░░░░░░░░░░░░░] 35%
```

### 分篇进度

| 篇章 | 案例 | 完成度 | 状态 |
|------|------|--------|------|
| 第一篇：基础理论 | 1-5 | 80% | 🟡 进行中 |
| 第二篇：参数率定 | 6-10 | 0% | ⏳ 未开始 |
| 第三篇：耦合系统 | 11-15 | 0% | ⏳ 未开始 |
| 第四篇：人类活动 | 16-18 | 0% | ⏳ 未开始 |
| 第五篇：智能化 | 19-20 | 0% | ⏳ 未开始 |

### 里程碑

- ✅ **M0**: 方案设计完成（2025-11-02）
- 🟡 **M1**: 基础篇完成（预计+2周）
- ⏳ **M2**: 参数率定篇完成（预计+2个月）
- ⏳ **M3**: 所有案例完成（预计+6个月）
- ⏳ **M4**: v1.0正式发布（预计+8个月）

---

## 🔍 快速查找

### 我想学习...

- **一维问题** → [案例1](code/examples/case_01/)
- **二维问题** → [案例2](code/examples/case_02/)
- **瞬态问题** → [案例4](code/examples/case_04/)
- **边界条件** → [案例2](code/examples/case_02/)
- **网格剖分** → [案例2](code/examples/case_02/)
- **参数率定** → 案例6（待开发）
- **数字孪生** → 案例19（待开发）

### 我想了解...

- **项目概述** → [README.md](README.md)
- **快速开始** → [START_HERE.md](START_HERE.md)
- **如何安装** → [INSTALL.md](INSTALL.md)
- **完整方案** → [教程提纲-完整版.md](教程提纲-完整版.md)
- **开发进度** → [DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md)
- **项目结构** → 本文件

### 我想使用...

- **网格生成** → `from gwflow.grid import create_2d_grid`
- **稳态求解** → `from gwflow.solvers import solve_2d_steady_gw`
- **瞬态求解** → `from gwflow.solvers import solve_2d_transient_gw`
- **可视化** → `from gwflow.visualization import plot_2d_head`

---

## 💡 常见问题

### Q1: 我应该从哪里开始？

**A**: 按顺序阅读：
1. [README.md](README.md) - 了解项目
2. [START_HERE.md](START_HERE.md) - 快速入门
3. [INSTALL.md](INSTALL.md) - 安装环境
4. [案例1](code/examples/case_01/) - 第一个案例

### Q2: 如何运行案例代码？

**A**: 
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 进入案例目录
cd code/examples/case_01

# 3. 运行代码
python3 case_01_1d_steady.py
```

### Q3: 我想贡献代码，应该看什么？

**A**: 
1. [DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md) - 了解开发状态
2. [教程提纲-完整版.md](教程提纲-完整版.md) - 了解设计方案
3. 待开发案例列表（案例3, 5, 6-20）

### Q4: 遇到bug怎么办？

**A**: 
1. 检查[INSTALL.md](INSTALL.md)确保环境正确
2. 运行测试：`python3 tests/run_simple_tests.py`
3. 查看代码注释和docstring
4. 提交Issue到GitHub

### Q5: 这个项目与MODFLOW等成熟软件的关系？

**A**: 
- 本项目是**教学工具**，重点是理解原理
- MODFLOW是**工程软件**，重点是实际应用
- 案例14会展示如何集成MODFLOW
- 可以将本项目作为学习MODFLOW的前置课程

---

## 📞 联系方式

- **GitHub**: （待提供）
- **Email**: （待提供）
- **讨论论坛**: GitHub Discussions

---

## 🎉 致谢

感谢以下项目的启发和支持：
- 《明渠水力学》
- 《水系统控制论》
- 《运河与管道控制》
- 《智能水网设计》
- MODFLOW
- FloPy
- NumPy/SciPy社区

---

**索引文档更新日期**: 2025-11-02
**项目版本**: v0.1.0-alpha
**文档维护者**: Underground Water Dynamics Team

---

**Happy Learning! 🎓💧**
