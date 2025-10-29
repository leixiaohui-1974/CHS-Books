# CHS-Books 项目结构说明

本文档详细说明 CHS-Books 多书籍教材项目的目录结构和组织方式。

## 设计理念

本项目采用**模块化多书籍架构**，每本书都是一个独立的模块，拥有完整的代码、文档、测试和资源。

### 设计原则

1. **独立性**: 每本书可以独立开发、测试和发布
2. **一致性**: 所有书籍遵循统一的目录结构
3. **可扩展性**: 易于添加新的书籍
4. **共享性**: 通用工具和模板集中管理

## 项目总体结构

```
CHS-Books/
├── README.md                 # 项目总说明
├── docs/                     # 项目级文档
│   ├── PROJECT_STRUCTURE.md  # 本文件
│   └── ...
├── books/                    # 所有书籍
│   ├── water-system-control/ # 水系统控制论
│   ├── book-template/        # 书籍模板
│   └── [future-books]/       # 未来的书籍
└── shared/                   # 共享资源
    ├── utils/               # 通用工具
    └── templates/           # 模板文件
```

## 书籍标准结构

每本书应该遵循以下标准结构：

```
books/[book-name]/
├── README.md                # 书籍主说明文档
├── START_HERE.md            # 快速入门指南（推荐）
│
├── chapters/                # 书籍章节内容
│   ├── chapter-01-xxx/
│   ├── chapter-02-xxx/
│   └── ...
│
├── code/                    # 代码和实现
│   ├── models/             # 模型实现
│   ├── examples/           # 示例代码
│   ├── utils/              # 工具函数
│   └── ...
│
├── docs/                    # 详细文档
│   ├── zh/                 # 中文文档
│   ├── en/                 # 英文文档（可选）
│   └── ...
│
├── tests/                   # 测试代码
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── ...
│
└── resources/              # 资源文件
    ├── images/             # 图片
    ├── data/               # 数据文件
    └── ...
```

## 现有书籍详情

### 1. 水系统控制论 (water-system-control)

**路径**: `books/water-system-control/`

**简介**: 基于12个经典水箱案例的控制理论入门教材

**特点**:
- 案例驱动教学
- Python 代码实现
- 完整测试覆盖
- 中文教学文档

**目录结构**:
```
water-system-control/
├── README.md                    # 书籍说明
├── START_HERE.md               # 快速开始
├── PRODUCT_README.md           # 产品说明
├── README_教材开发.md          # 开发说明
├── chapters/                   # 章节（待开发）
├── code/
│   ├── models/water_tank/      # 水箱模型
│   │   ├── single_tank.py
│   │   └── double_tank.py
│   ├── control/                # 控制器
│   │   ├── on_off.py
│   │   ├── pid.py
│   │   └── basic_controllers.py
│   └── examples/               # 案例代码
│       ├── case_01_home_water_tower/
│       ├── case_02_cooling_tower/
│       ├── case_03_water_supply_station/
│       └── case_04_pid_tuning/
├── docs/zh/                    # 中文文档
│   ├── 水箱案例驱动教学体系.md
│   ├── 水系统控制论教材开发方案.md
│   ├── 零基础教材开发详细方案.md
│   ├── 立即开始指南.md
│   └── 功能索引.md
├── tests/                      # 测试代码
│   └── tests/
│       ├── models/water_tank/
│       └── standard_cases/
└── resources/                  # 资源文件
```

**核心内容**:
- 单水箱模型（一阶系统）
- 双水箱模型（二阶系统）
- 基础控制器（On-Off, P, PI, PID）
- 4个已完成的教学案例
- 44个单元测试（100%通过）

### 2. 书籍模板 (book-template)

**路径**: `books/book-template/`

**用途**: 作为新书籍的起始模板

**使用方法**:
```bash
# 复制模板创建新书
cp -r books/book-template books/your-new-book

# 修改内容
cd books/your-new-book
# 编辑 README.md 等文件
```

## 共享资源

### shared/utils/

存放通用的工具函数和类，可被所有书籍共享使用。

**示例**:
- 数据处理工具
- 绘图工具
- 文件IO工具
- 数学计算工具

### shared/templates/

存放各种模板文件。

**示例**:
- README 模板
- 测试文件模板
- 文档模板
- 代码模板

## 添加新书籍的步骤

### 方法1: 使用模板

```bash
# 1. 复制模板
cp -r books/book-template books/your-book-name

# 2. 进入新书目录
cd books/your-book-name

# 3. 修改 README.md
vim README.md

# 4. 开始开发内容
```

### 方法2: 手动创建

```bash
# 1. 创建目录结构
mkdir -p books/your-book-name/{chapters,code,docs/zh,tests,resources}

# 2. 创建 README
touch books/your-book-name/README.md

# 3. 添加内容
```

### 新书籍检查清单

在添加新书籍时，确保：

- [ ] 创建了完整的目录结构
- [ ] 编写了详细的 README.md
- [ ] 如果需要，创建了 START_HERE.md
- [ ] 代码有适当的注释
- [ ] 添加了测试代码
- [ ] 文档完整且易懂
- [ ] 更新了项目根目录的 README.md

## 命名规范

### 目录命名

- 使用小写字母
- 单词之间用连字符 `-` 分隔
- 避免使用空格和特殊字符

**示例**:
- `water-system-control` ✓
- `machine-learning-basics` ✓
- `WaterSystemControl` ✗
- `water_system_control` ✗

### 文件命名

- Python 文件: 使用小写字母和下划线 `_`
- Markdown 文件: 使用大写字母和下划线，或中文
- 其他文件: 遵循各语言的惯例

**示例**:
- `single_tank.py` ✓
- `README.md` ✓
- `水箱案例驱动教学体系.md` ✓
- `START_HERE.md` ✓

## 版本控制

### 分支策略

- `main`: 主分支，包含稳定版本
- `claude/*`: Claude 开发分支
- `feature/*`: 功能开发分支
- `docs/*`: 文档更新分支

### 提交规范

提交信息格式：
```
<type>: <subject>

<body>
```

**类型（type）**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**:
```
feat: 添加水系统控制论教材

- 从 Canal-Simulation 复制水箱系统代码
- 创建多书籍项目结构
- 编写项目和书籍 README
```

## 维护指南

### 定期维护任务

1. **更新依赖**: 定期更新各书籍的依赖包
2. **测试检查**: 确保所有测试通过
3. **文档同步**: 保持代码和文档一致
4. **清理临时文件**: 删除不需要的临时文件

### 质量标准

每本书应该满足：

- [ ] 代码可以正常运行
- [ ] 测试通过率 > 90%
- [ ] 有完整的 README
- [ ] 代码有适当注释
- [ ] 文档清晰易懂

## 常见问题

### Q: 如何在多本书之间共享代码？

A: 将共享代码放在 `shared/utils/` 目录，然后在各书籍中导入：

```python
import sys
sys.path.append('../../shared/utils')
from myutil import some_function
```

### Q: 每本书需要独立的虚拟环境吗？

A: 推荐每本书使用独立的虚拟环境，避免依赖冲突：

```bash
cd books/your-book
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Q: 如何处理不同书籍之间的依赖关系？

A: 如果一本书依赖另一本书的内容，在 README 中明确说明，并提供链接。

### Q: 是否需要为每本书创建独立的仓库？

A: 不需要。所有书籍都在 CHS-Books 这个单一仓库中，便于统一管理。

## 未来规划

### 计划添加的书籍

- 机器学习基础 (machine-learning-basics)
- 信号处理入门 (signal-processing)
- 优化算法实践 (optimization-algorithms)
- 数字信号处理 (digital-signal-processing)

### 功能增强

- [ ] 自动化书籍生成工具
- [ ] 统一的测试框架
- [ ] 在线文档系统
- [ ] 交互式教学环境

## 贡献指南

欢迎贡献！请遵循：

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

详细贡献指南见各书籍的 CONTRIBUTING.md（如有）。

---

**文档版本**: 1.0
**最后更新**: 2025-10-29
**维护者**: CHS-Books 团队
