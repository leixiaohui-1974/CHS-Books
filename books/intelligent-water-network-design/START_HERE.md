# 快速开始指南

欢迎学习《智能水网工程设计教材》！

---

## 📋 开始之前

### 前置要求

1. **已完成前三本书的学习**（至少浏览过）：
   - 第1本：《水系统控制论》
   - 第2本：《明渠水力学计算》
   - 第3本：《渠道与管道控制》

2. **编程基础**：
   - Python 3.8+
   - 基本的NumPy、Matplotlib使用

3. **工程背景**：
   - 水利水电或水务设计工作经验
   - 了解水网工程的基本概念

---

## 🚀 快速安装

### 步骤1：克隆或下载项目

```bash
cd /workspace/books
ls intelligent-water-network-design  # 确认目录存在
```

### 步骤2：安装依赖

```bash
cd intelligent-water-network-design

# 安装本书依赖
pip install -r requirements.txt

# 如果还没有安装前三本书的依赖，也需要安装
pip install -r ../open-channel-hydraulics/requirements.txt
pip install -r ../water-system-control/requirements.txt
```

### 步骤3：验证安装

```bash
python -c "import numpy, matplotlib, scipy; print('✓ 依赖安装成功')"
```

---

## 📖 学习路线

### 路线1：设计人员（推荐）⭐

**目标**：快速掌握智能水网设计方法，应用到实际项目

**学习步骤**：
1. 阅读 `README.md`，了解教材定位（30分钟）
2. 学习案例1：灌区智能化升级（8学时）
   ```bash
   cd code/examples/case_01
   python main.py
   ```
3. 学习案例2：供水管网智能调压（12学时）
4. 根据工作需要选学案例3-5（各12-16学时）
5. 应用到自己的设计项目

**总学时**：约60-80学时（1.5-2个月业余时间）

---

### 路线2：研究生（深度学习）

**目标**：全面掌握理论和方法，具备科研能力

**学习步骤**：
1. 系统复习前三本书的核心内容（2周）
2. 完成全部5个案例（10周）
3. 阅读相关论文，了解前沿技术（2周）
4. 开展创新性研究（根据课题）

**总学时**：约200学时

---

### 路线3：工程师（实战导向）

**目标**：解决具体工程问题

**学习步骤**：
1. 直接查找与自己项目相似的案例
2. 阅读该案例的设计文档
3. 运行代码，理解设计流程
4. 修改配置，适配自己的项目
5. 使用在环测试工具验证设计

**总学时**：根据项目需求，10-40学时

---

## 🎯 五个案例概览

| 案例 | 主题 | 智能化等级 | 学时 | 适合人群 |
|------|------|-----------|------|----------|
| 案例1 | 灌区智能化升级 | L2 | 8 | 所有人（必学） |
| 案例2 | 供水管网智能调压 | L3 | 12 | 供水设计人员 |
| 案例3 | 水库群防洪调度 | L4 | 16 | 水库调度工程师 |
| 案例4 | 长距离输水智能控制 | L4 | 16 | 调水工程设计师 |
| 案例5 | 流域水资源智能管理 | L5 | 20 | 高级工程师/研究生 |

**学习建议**：
- 按顺序学习，难度递增
- 案例1是基础，必须掌握
- 根据工作需要选学案例2-5

---

## 💻 运行第一个案例

### 案例1：灌区智能化升级

```bash
# 进入案例目录
cd code/examples/case_01

# 阅读案例说明
cat README.md  # 或用文本编辑器打开

# 运行主程序
python main.py

# 查看结果
ls *.png  # 会生成结果图表
```

**预期输出**：
- 控制台显示设计计算过程
- 生成仿真结果图表（PNG格式）
- 显示智能化等级评估结果

**常见问题**：
- 如果提示缺少某个包，用 `pip install 包名` 安装
- 如果导入前三本书的模块失败，代码会自动使用简化版本

---

## 📚 核心概念速查

### 智能化等级（L1-L5）

| 等级 | 名称 | 能力 | 典型应用 |
|------|------|------|----------|
| L1 | 辅助监测 | 数据采集、报警 | 传感器网络 |
| L2 | 局部控制 | PID控制 | 水位/流量控制 |
| L3 | 协调控制 | MPC、多目标 | 多闸门协调 |
| L4 | 优化调度 | 全局优化、自适应 | 水网智能调度 |
| L5 | 自主管理 | 数字孪生、自愈 | 智慧水务 |

### 设计流程

```
1. 工程调研 → 2. 水力设计（复用第2本书）
       ↓
3. 智能体设计（复用第1、3本书） → 4. 系统集成
       ↓
5. 在环测试（本书新增） → 6. 性能评估
       ↓
7. 设计交付（工程文档 + 代码 + 智能体）
```

### 复用前序教材的代码

```python
# 从第2本书导入明渠模型
from books.open_channel_hydraulics.code.models.channel import TrapezoidalChannel

# 从第1本书导入PID控制器
from books.water_system_control.code.control.pid import PIDController

# 使用本书的设计工具
from books.intelligent_water_network_design.code.tools.design_wizard import DesignWizard
```

---

## 🔧 设计工具包

本书提供以下设计工具（位于 `code/tools/`）：

1. **design_wizard.py** - 设计向导（交互式设计）
2. **scenario_generator.py** - 工况生成器（自动生成测试场景）
3. **intelligence_grader.py** - 智能化等级评估器
4. **report_generator.py** - 设计文档生成器
5. **cost_estimator.py** - 投资概算工具

**示例使用**：
```bash
# 使用设计向导
python code/tools/design_wizard.py --project 我的灌区改造

# 生成测试工况
python code/tools/scenario_generator.py --type irrigation --n 100

# 评估智能化等级
python code/tools/intelligence_grader.py --config config.json
```

---

## 📂 目录结构

```
intelligent-water-network-design/
├── README.md           # 教材总体介绍（详细）
├── START_HERE.md       # 本文件（快速开始）
├── requirements.txt    # Python依赖包
│
├── code/              # 代码
│   ├── models/        # 模型（主要复用前三本书）
│   ├── agents/        # 智能体框架
│   ├── simulator/     # 仿真引擎
│   ├── tools/         # 设计工具包（本书核心）
│   └── examples/      # 5个案例
│       ├── case_01/   # 案例1：灌区（✓已完成）
│       ├── case_02/   # 案例2：供水
│       ├── case_03/   # 案例3：水库群
│       ├── case_04/   # 案例4：长距离输水
│       └── case_05/   # 案例5：流域管理
│
├── docs/              # 文档
│   └── zh/           # 中文文档
│
├── tests/             # 测试代码
│
└── resources/         # 资源文件
    ├── templates/     # 设计文档模板
    ├── schemas/       # 配置文件模式
    └── images/        # 图片资源
```

---

## 🆘 遇到问题？

### 常见问题

**Q1: 无法导入前三本书的模块？**

A: 确保前三本书的代码在正确的位置：
```bash
ls /workspace/books/open-channel-hydraulics
ls /workspace/books/water-system-control
ls /workspace/books/canal-pipeline-control
```

如果不在，需要先下载/克隆这些项目。或者，代码会自动使用简化版本。

**Q2: 运行案例时出错？**

A: 检查依赖是否安装完整：
```bash
pip list | grep numpy
pip list | grep matplotlib
```

**Q3: 如何将设计方法应用到自己的项目？**

A: 
1. 选择最相似的案例作为起点
2. 修改 `config.json` 配置文件（修改参数、拓扑等）
3. 运行仿真验证
4. 使用设计文档生成器生成交付物

---

## 📞 获取帮助

- 📖 详细文档：查看 `README.md` 和 `docs/` 目录
- 💬 技术讨论：GitHub Issues
- 📧 联系作者：chs-books@example.com

---

## 🎉 开始学习！

**推荐第一步**：
```bash
cd code/examples/case_01
python main.py
```

运行案例1，开启智能水网设计之旅！

---

**最后更新**：2025-10-31  
**版本**：v1.0.0
