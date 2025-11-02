# 🌊 生态水力学教材 - 快速入门

欢迎使用《生态水力学》教材！这是一门将**水力学**与**生态学**相结合的交叉学科课程。

---

## ⚡ 5分钟快速开始

### 1. 检查环境

```bash
python3 --version  # 需要 Python 3.8+
```

### 2. 安装依赖

```bash
cd /workspace/books/ecohydraulics
pip install -r requirements.txt
```

### 3. 运行第一个案例

```bash
cd code/examples/case_01_ecological_flow
python3 main.py
```

### 4. 查看结果

运行后会生成3张图表：
- `wetted_perimeter_curve.png` - 湿周-流量曲线
- `depth_discharge_curve.png` - 水深-流量曲线
- `ecological_flow_comparison.png` - 方法对比图

### 5. 运行测试

```bash
cd /workspace/books/ecohydraulics
python3 -m pytest tests/ -v
```

预期结果：✅ 30 passed in 0.09s

---

## 📚 学什么？

### 案例1：河流生态基流计算

**问题**: 水库建设后，如何确定下游最小流量以保护鱼类？

**学到的**:
- ✅ 3种生态流量计算方法（Tennant、湿周、R2-Cross）
- ✅ 水力学基础（Manning公式、水深计算）
- ✅ Python编程与可视化

**计算结果**:
```
推荐生态流量: 1.98 m³/s
占多年平均流量: 13.2%
生态等级: 良好
```

---

## 🎯 下一步

### 继续学习

1. **阅读案例说明**: `code/examples/case_01_ecological_flow/README.md`
2. **理解代码**: 查看 `main.py` 和核心模型
3. **修改参数**: 尝试不同的河流条件
4. **查看提纲**: `/workspace/books/生态水力学教材提纲.md`

### 深入研究

1. **测试代码**: `tests/test_*.py` - 学习如何写测试
2. **模型代码**: `code/models/` - 理解算法实现
3. **完整文档**: `README.md` - 查看完整项目说明

---

## 📖 教材结构

```
第一部分 | 生态水力学基础（案例1-6）
    ├─ 案例1: 河流生态基流计算 ✅ 已完成
    ├─ 案例2: 鱼类栖息地评价 ⏳ 规划中
    ├─ 案例3: 生态指标体系 ⏳ 规划中
    ├─ 案例4: 水生植物 ⏳ 规划中
    ├─ 案例5: 水温与溶解氧 ⏳ 规划中
    └─ 案例6: 底栖生物 ⏳ 规划中

第二部分 | 鱼类生态水力学（案例7-12）
    └─ 鱼道设计、产卵场保护等 ⏳ 规划中

第三部分 | 河流生态修复（案例13-18）
    └─ 近自然河道、生态护岸等 ⏳ 规划中

第四部分 | 水工建筑物生态化（案例19-22）
    └─ 生态堰、生态调度等 ⏳ 规划中

第五部分 | 湖泊与湿地（案例23-26）
    └─ 富营养化控制、湿地设计等 ⏳ 规划中

第六部分 | 综合应用（案例27-28）
    └─ 流域模型、气候变化响应 ⏳ 规划中
```

---

## 💡 常见问题

### Q1: 需要什么基础？

**A**: 建议先学习《明渠水力学》，了解基本的水力计算方法。

### Q2: 如何运行案例？

**A**: 
```bash
cd code/examples/case_XX_xxxxx
python3 main.py
```

### Q3: 测试失败怎么办？

**A**: 
1. 检查Python版本（需要3.8+）
2. 确认依赖已安装（numpy, scipy, matplotlib, pytest）
3. 查看错误信息

### Q4: 图表中文乱码？

**A**: 这是字体问题，不影响计算结果。图表的数值是正确的。

### Q5: 如何修改参数？

**A**: 编辑 `main.py` 文件中的参数定义部分，通常在文件开头。

---

## 📊 项目状态

```
✅ 项目结构完整
✅ 核心模型开发完成
✅ 案例1开发完成
✅ 30个测试全部通过（100%）
✅ 文档完整
✅ 可视化功能完善

当前版本: v1.0.0-alpha
完成度: 3.6% (1/28案例)
代码质量: ⭐⭐⭐⭐⭐
```

---

## 🔗 重要链接

- **主README**: `README.md` - 完整项目说明
- **教材提纲**: `/workspace/books/生态水力学教材提纲.md` - 28个案例规划
- **开发总结**: `DEVELOPMENT_SUMMARY.md` - 技术文档
- **案例1说明**: `code/examples/case_01_ecological_flow/README.md`

---

## 🤝 需要帮助？

- 查看文档: `README.md`, `DEVELOPMENT_SUMMARY.md`
- 运行测试: `pytest tests/ -v`
- 查看代码: `code/models/`
- 提交问题: GitHub Issues

---

## 🌟 开始学习吧！

```bash
# 一键运行案例1
cd /workspace/books/ecohydraulics/code/examples/case_01_ecological_flow
python3 main.py
```

**祝学习愉快！🌊🐟🌿**

---

**版本**: v1.0.0-alpha  
**更新日期**: 2025-11-02  
**作者**: CHS-Books 生态水力学课程组
