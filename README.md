# CHS-Books | 控制系统教材系列

这是一个多书籍教材开发项目，采用案例驱动的教学方法，涵盖控制系统理论与实践。

## 项目结构

```
CHS-Books/
├── README.md                 # 项目总说明（本文件）
├── books/                    # 所有书籍内容
│   ├── water-system-control/ # 水系统控制论教材
│   ├── book-template/        # 书籍模板
│   └── ...                   # 未来的其他书籍
├── shared/                   # 共享资源
│   ├── utils/               # 通用工具
│   └── templates/           # 模板文件
└── docs/                    # 项目级文档
```

## 现有书籍

### 1. 水系统控制论 (Water System Control Theory)

**目录**: `books/water-system-control/`

基于12个经典水箱案例的控制理论入门教材，适合高中及以上水平的学习者。

**内容特点**:
- 案例驱动教学方法
- 从简单到复杂的渐进式学习路径
- 完整的代码示例和测试
- 理论与实践相结合

**快速开始**: 请查看 `books/water-system-control/START_HERE.md`

## 教学理念

本系列教材采用**案例驱动学习**（Case-Based Learning）方法：
- 从真实工程问题出发
- 在解决问题中学习理论
- 强调动手实践和代码实现
- 培养完整的工程思维

## 如何使用

1. **浏览书籍列表**: 在 `books/` 目录下查看所有可用的书籍
2. **选择感兴趣的书**: 进入对应的书籍目录
3. **阅读 START_HERE 或 README**: 了解该书的内容和学习路径
4. **跟随案例学习**: 结合文档和代码进行学习

## 添加新书籍

使用 `books/book-template/` 作为模板创建新的书籍项目：

```bash
cp -r books/book-template books/your-new-book
```

然后根据需要修改内容和结构。

## 贡献

欢迎贡献新的书籍内容、案例或改进建议！

## 许可证

各书籍的许可证请查看对应书籍目录中的 LICENSE 文件。

---

**项目更新日期**: 2025-10-29
