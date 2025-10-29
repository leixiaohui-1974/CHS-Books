# 案例库 (Cases)

欢迎来到CHS-Books案例库！本目录包含27个渐进式案例，从基础的单池PID控制到复杂的智慧水务系统。

## 快速开始

### 🎯 如果你是初学者
从 **Case 01** 开始，按顺序学习Level 1的所有案例：
```bash
cd case01_single_pool_pid/python
pip install -r requirements.txt
python simulation.py
```

### 🚀 如果你有控制理论基础
直接跳到感兴趣的领域：
- **模型预测控制**: Case 03, 06
- **鲁棒控制**: Case 14, 15
- **智能控制**: Case 17-20
- **数字孪生**: Case 21-24

### 📊 查看完整学习路线
详见 [CASES.md](../CASES.md)

---

## 案例列表

### 🎓 Level 1: 基础篇（已实现）

| 案例 | 名称 | 难度 | 状态 | 代码 |
|------|------|------|------|------|
| **Case 01** | 单池明渠水位PID控制 | ⭐ | ✅ 完成 | [Python](case01_single_pool_pid/python) |
| Case 02 | 单池明渠状态空间建模 | ⭐⭐ | 📝 计划中 | - |
| Case 03 | 单池明渠MPC控制 | ⭐⭐⭐ | 📝 计划中 | - |
| Case 04 | 单池明渠扰动抑制 | ⭐⭐ | 📝 计划中 | - |

### 🚀 Level 2: 进阶篇

| 案例 | 名称 | 难度 | 状态 |
|------|------|------|------|
| Case 05 | 双池级联系统控制 | ⭐⭐⭐ | 📝 计划中 |
| Case 06 | 多池级联分布式MPC | ⭐⭐⭐⭐ | 📝 计划中 |
| Case 07 | 长距离输水渠道控制 | ⭐⭐⭐⭐ | 📝 计划中 |

### ⚙️ Level 3: 有压系统篇

| 案例 | 名称 | 难度 | 状态 |
|------|------|------|------|
| Case 08 | 管道水锤效应仿真与控制 | ⭐⭐⭐ | 📝 计划中 |
| Case 09 | 泵站变频调速控制 | ⭐⭐⭐ | 📝 计划中 |
| Case 10 | 管网压力优化控制 | ⭐⭐⭐⭐ | 📝 计划中 |

### 🧠 Level 4-8

更多高级案例正在开发中，详见 [CASES.md](../CASES.md)

---

## 案例结构说明

每个案例遵循统一的目录结构：

```
case_XX_name/
├── README.md              # 📖 案例说明（必读）
├── docs/                  # 📚 详细文档
│   ├── theory.md         #   理论推导
│   ├── algorithm.md      #   算法说明
│   └── results.md        #   结果分析
├── python/                # 🐍 Python实现
│   ├── requirements.txt  #   依赖库
│   ├── model.py         #   系统模型
│   ├── controller.py    #   控制器
│   ├── simulation.py    #   仿真主程序
│   └── visualization.py #   可视化
├── matlab/                # 🔧 MATLAB实现
├── data/                  # 💾 数据和参数
└── results/               # 📊 结果输出
    ├── figures/
    └── logs/
```

---

## 使用指南

### Python环境配置

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 进入案例目录
cd case01_single_pool_pid/python

# 安装依赖
pip install -r requirements.txt

# 运行仿真
python simulation.py
```

### MATLAB使用

```matlab
% 进入案例目录
cd('case01_single_pool_pid/matlab')

% 运行仿真
simulation
```

### 参数修改

编辑 `data/parameters.json` 文件：
```json
{
    "system": {
        "length": 1000.0,
        "width": 10.0,
        ...
    },
    "controller": {
        "Kp": 0.5,
        "Ki": 0.01,
        "Kd": 5.0
    }
}
```

---

## 学习建议

### 📖 阅读顺序
1. 案例README.md（了解问题背景）
2. docs/theory.md（理论推导）
3. 代码实现（model.py, controller.py）
4. 运行仿真并分析结果
5. docs/results.md（结果讨论）
6. 尝试修改参数，观察影响

### 💡 实践建议
1. **先运行再理解**：先看到效果，再深入原理
2. **动手修改**：调整参数，观察系统响应变化
3. **对比实验**：改变控制器类型，对比性能
4. **扩展思考**：README中的思考题

### 🔧 调试技巧
1. 降低仿真时长（修改t_end）加快测试
2. 增加打印输出（print调试）
3. 单独运行模块测试：`python model.py`
4. 使用Jupyter Notebook交互式探索

---

## 常见问题

### Q1: 仿真运行很慢？
**A**:
- 减小仿真时长（t_end）
- 增大时间步长（dt）
- 使用更高效的求解器

### Q2: 控制效果不好？
**A**:
- 检查PID参数是否合理
- 查看是否有约束饱和
- 尝试Ziegler-Nichols整定法

### Q3: 图表显示不出来？
**A**:
- 检查matplotlib是否正确安装
- 尝试 `plt.show()` 显示图表
- 查看results/figures/目录下的保存图片

### Q4: 如何应用到实际工程？
**A**:
- 案例代码主要用于教学
- 实际应用需要：
  - 硬件接口适配
  - 异常处理
  - 安全保护
  - 现场测试验证

---

## 贡献指南

欢迎贡献新案例或改进现有案例！

### 贡献流程
1. Fork仓库
2. 创建新分支
3. 实现案例（遵循标准结构）
4. 提交Pull Request

### 案例要求
- ✅ 完整的README说明
- ✅ 可运行的代码
- ✅ 详细的注释
- ✅ 理论文档
- ✅ 测试验证

---

## 致谢

感谢所有为案例库贡献代码、文档和建议的开发者！

---

## 许可证

（待补充）

---

**最后更新**: 2025-10-29
**当前进度**: 1/27 案例完成
