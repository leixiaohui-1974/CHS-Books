# 水力学考研1000题 - Python代码索引

**版本**: v1.0  
**代码总数**: 10个（持续更新中）  
**语言**: Python 3.8+  
**依赖**: numpy, matplotlib

---

## 📦 代码清单

### 已完成代码（10个）

| 序号 | 文件名 | 题号 | 主题 | 难度 | 行数 |
|------|--------|------|------|------|------|
| 1 | `problem_001_pressure_distribution.py` | 001 | 静水压强分布 | ⭐ | ~200 |
| 2 | `problem_002_utube_manometer.py` | 002 | U型管压差计 | ⭐⭐ | ~250 |
| 3 | `problem_003_multilayer_pressure.py` | 003 | 多层液体压强 | ⭐⭐ | ~280 |
| 4 | `problem_011_rectangular_gate.py` | 011 | 矩形闸门压力 | ⭐⭐ | ~350 |
| 5 | `problem_021_curved_surface.py` | 021 | 曲面总压力 | ⭐⭐⭐ | ~380 |
| 6 | `problem_023_arc_gate.py` | 023 | 圆弧闸门 | ⭐⭐⭐ | ~400 |
| 7 | `problem_033_floating_body.py` | 033 | 浮力与稳定性 | ⭐⭐⭐ | ~420 |
| 8 | `problem_126_bernoulli_basic.py` | 126 | 伯努利方程基础 | ⭐⭐⭐⭐ | ~320 |
| 9 | `problem_281_darcy_friction.py` | 281 | 达西阻力公式 | ⭐⭐⭐⭐ | ~360 |
| 10 | `problem_461_manning_formula.py` | 461 | 曼宁公式 | ⭐⭐⭐⭐ | ~380 |

---

## 🎯 按知识点分类

### 一、静水力学（7个代码）

#### 1.1 静水压强（3个）
- **problem_001**: 基础压强分布
  - 类: `WaterTank`
  - 功能: 计算不同深度压强，可视化压强分布
  - 公式: `p = p0 + γh`

- **problem_002**: U型管压差计
  - 类: `UtubeManometer`
  - 功能: 计算U型管和倒U型管压差
  - 应用: 测压装置

- **problem_003**: 多层液体
  - 类: `MultilayerFluid`
  - 功能: 计算油-水-汞多层液体压强
  - 特点: 处理不同密度液体

#### 1.2 平面总压力（1个）
- **problem_011**: 矩形闸门
  - 类: `RectangularGate`
  - 功能: 计算总压力、压力中心、启闭力
  - 公式: `P = γh_cA`, `y_p = h_c + I_c/(h_cA)`
  - 可视化: 压力分布图、力矩分析

#### 1.3 曲面总压力（2个）
- **problem_021**: 圆柱曲面
  - 类: `CurvedSurfacePressure`
  - 功能: 计算水平分力、垂直分力
  - 方法: 压力体法

- **problem_023**: 圆弧闸门
  - 类: `ArcGatePressure`
  - 功能: 圆弧闸门受力分析
  - 特性: 总压力过圆心

#### 1.4 浮力（1个）
- **problem_033**: 浮力与稳定性
  - 类: `FloatingBody`
  - 功能: 计算浮力、吃水、初稳性高GM
  - 公式: `F = ρ_液gV_排`, `GM = BM - BG`
  - 应用: 船舶设计

### 二、水动力学（1个）

#### 2.1 伯努利方程（1个）
- **problem_126**: 伯努利方程基础
  - 类: `BernoulliPipe`
  - 功能: 渐缩管流速和压强计算
  - 公式: `p1/γ + v1²/2g + z1 = p2/γ + v2²/2g + z2`
  - 可视化: 水头线图、速度压强对比

### 三、管流（1个）

#### 3.1 沿程阻力（1个）
- **problem_281**: 达西公式
  - 类: `DarcyFriction`
  - 功能: 计算Re、λ、h_f、Δp
  - 公式: `h_f = λ(L/d)(v²/2g)`
  - 特色: 科尔布鲁克迭代、莫迪图绘制

### 四、明渠流（1个）

#### 4.1 曼宁公式（1个）
- **problem_461**: 曼宁公式
  - 类: `ManningChannel`
  - 功能: 计算A、P、R、v、Q、Fr、E
  - 公式: `v = (1/n)R^(2/3)i^(1/2)`
  - 可视化: 断面图、比能曲线

---

## 💻 使用方法

### 方法1：直接运行

```bash
cd /workspace/books/graduate-exam-prep/hydraulics-1000/codes
python3 problem_001_pressure_distribution.py
```

### 方法2：导入使用

```python
from problem_001_pressure_distribution import WaterTank

# 创建对象
tank = WaterTank(depth=5.0, p0=101325)

# 打印结果
tank.print_results()

# 可视化
fig = tank.visualize()
plt.show()

# 获取特定深度压强
p_at_3m = tank.get_pressure(depth=3.0)
print(f"3m处压强: {p_at_3m/1000:.2f} kPa")
```

### 方法3：批量测试

```python
# 测试所有已实现的代码
test_files = [
    'problem_001_pressure_distribution.py',
    'problem_002_utube_manometer.py',
    # ... 其他文件
]

for file in test_files:
    print(f"\n测试 {file}...")
    exec(open(file).read())
```

---

## 🔧 代码特性

### 1. 面向对象设计
所有代码采用OOP设计：
- **输入**: 构造函数传参
- **计算**: `calculate()` 方法
- **输出**: `print_results()` 方法
- **可视化**: `visualize()` 方法

示例结构：
```python
class HydraulicsProblem:
    def __init__(self, param1, param2, ...):
        self.param1 = param1
        # ...
        self.calculate()
    
    def calculate(self):
        # 执行计算
        pass
    
    def print_results(self):
        # 打印结果
        pass
    
    def visualize(self):
        # 可视化
        fig = plt.figure()
        # ...
        return fig
```

### 2. 单元测试
每个文件都包含测试函数：
```python
def test_problem_XXX():
    # 已知条件
    param1 = value1
    
    # 创建对象
    obj = SomeClass(param1, ...)
    
    # 验证结果
    assert condition1, "错误信息1"
    assert condition2, "错误信息2"
    
    print("✓ 所有测试通过！")
```

### 3. 详细注释
- 文件头：题目描述、考点、作者
- 函数注释：参数说明、返回值
- 行内注释：关键步骤解释

### 4. 专业可视化
- 使用matplotlib绘图
- 多子图布局
- 中文标注
- 颜色编码
- 图例说明

---

## 📊 代码统计

### 功能覆盖率

| 主题 | 代码数 | 占比 | 计划数 | 进度 |
|------|--------|------|--------|------|
| 静水力学 | 7 | 70% | 10 | 70% |
| 水动力学 | 1 | 10% | 5 | 20% |
| 管流 | 1 | 10% | 10 | 10% |
| 明渠流 | 1 | 10% | 10 | 10% |
| 渗流 | 0 | 0% | 5 | 0% |
| 水泵 | 0 | 0% | 5 | 0% |
| **总计** | **10** | **100%** | **45** | **22%** |

### 代码量统计

- 总行数: ~3500行
- 平均每个: ~350行
- 注释率: ~30%
- 可视化: 10个 (100%)

---

## 🎓 学习路径

### 初学者路径
1. **problem_001** (压强分布) - 最简单
2. **problem_002** (U型管) - 进一步
3. **problem_011** (平面压力) - 综合应用
4. **problem_033** (浮力) - 实际应用
5. **problem_126** (伯努利) - 核心公式

### 进阶路径
1. **problem_126** (伯努利) - 能量方程
2. **problem_281** (达西) - 阻力计算
3. **problem_461** (曼宁) - 明渠流动
4. **problem_021** (曲面) - 复杂几何
5. **problem_023** (圆弧闸门) - 工程应用

### 考研冲刺路径
只看高频考点代码：
1. **problem_126** (伯努利) ⭐⭐⭐⭐⭐
2. **problem_281** (达西) ⭐⭐⭐⭐⭐
3. **problem_461** (曼宁) ⭐⭐⭐⭐⭐
4. **problem_011** (平面压力) ⭐⭐⭐⭐
5. **problem_033** (浮力) ⭐⭐⭐

---

## 🔮 计划开发的代码

### 近期计划（优先级高）

#### 水动力学（4个）
- [ ] **problem_136**: 文丘里管（流量测量）
- [ ] **problem_146**: 毕托管（测速原理）
- [ ] **problem_156**: 虹吸管（真空问题）
- [ ] **problem_176**: 动量方程（射流冲击）

#### 管流（4个）
- [ ] **problem_351**: 管道第一类问题（已知Q、d求h_f）
- [ ] **problem_366**: 管道第二类问题（已知h_f、d求Q）
- [ ] **problem_381**: 管道第三类问题（已知Q、h_f求d）
- [ ] **problem_401**: 管网分析（节点法）

#### 明渠流（3个）
- [ ] **problem_481**: 临界水深（Fr=1）
- [ ] **problem_511**: 水跃（共轭水深）
- [ ] **problem_536**: 正常水深（迭代求解）

#### 渗流（2个）
- [ ] **problem_681**: 承压井（裘布依公式）
- [ ] **problem_701**: 潜水井（杜比公式）

#### 水泵（2个）
- [ ] **problem_751**: 水泵扬程功率
- [ ] **problem_791**: 工况点分析

### 远期计划（优先级中）

- [ ] 综合应用案例（5个）
- [ ] 真题精选代码（10个）
- [ ] 交互式计算器（Web版）
- [ ] 3D可视化（VPython）

---

## 🛠️ 环境配置

### 依赖安装

```bash
pip install numpy matplotlib
```

### Python版本
- 推荐: Python 3.8+
- 最低: Python 3.6

### IDE推荐
- VS Code (推荐)
- PyCharm
- Jupyter Notebook (适合学习)

### 运行环境
所有代码在以下环境测试通过：
- macOS 12+ ✓
- Ubuntu 20.04+ ✓
- Windows 10+ ✓

---

## 📖 代码规范

### 命名规范
- 文件名: `problem_XXX_description.py`
- 类名: 大驼峰 `WaterTank`
- 函数名: 小写下划线 `calculate_pressure`
- 常量: 大写 `GRAVITY = 9.8`

### 注释规范
```python
"""
文件级注释（文件开头）
题目、考点、作者
"""

def function_name(param1, param2):
    """
    函数注释
    
    参数:
        param1: 说明
        param2: 说明
    
    返回:
        返回值说明
    """
    pass
```

### 测试规范
每个文件必须包含：
1. 测试函数 `test_problem_XXX()`
2. 至少3个断言验证
3. 测试通过提示

---

## 🤝 贡献指南

### 如何贡献新代码

1. **选择题目**: 从计划列表选择
2. **创建文件**: `problem_XXX_description.py`
3. **实现功能**: 
   - 类设计
   - 计算逻辑
   - 打印结果
   - 可视化
4. **测试验证**: 单元测试
5. **更新索引**: 在本文件添加记录

### 代码质量要求
- [ ] 通过pylint检查
- [ ] 包含完整注释
- [ ] 有单元测试
- [ ] 可视化美观
- [ ] 结果正确

---

## 📞 技术支持

### 常见问题

**Q1: 中文显示乱码？**
```python
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS
```

**Q2: 图片不显示？**
```python
plt.show()  # 添加这一行
```

**Q3: 导入错误？**
```bash
pip install numpy matplotlib
```

**Q4: 运行报错？**
检查Python版本：
```bash
python3 --version  # 应该 >= 3.6
```

---

## 📚 参考资源

### 教材
- 《水力学》（吴持恭主编）
- 《工程流体力学》（闻德荪主编）
- 《水力学解题指导》

### 在线资源
- Python官方文档: https://docs.python.org/3/
- Matplotlib文档: https://matplotlib.org/
- NumPy文档: https://numpy.org/doc/

---

## 🎉 更新日志

### v1.0 (2025-11-10)
- ✅ 完成10个基础代码
- ✅ 覆盖静水力学、伯努利、达西、曼宁
- ✅ 所有代码测试通过
- ✅ 生成可视化图片

### 计划中 (v1.1)
- [ ] 新增15个代码
- [ ] 覆盖管道三类问题
- [ ] 添加管网分析
- [ ] 增加水泵计算

---

**持续更新中...** 🚀

**最后更新**: 2025-11-10  
**维护者**: CHS-Books开发团队
