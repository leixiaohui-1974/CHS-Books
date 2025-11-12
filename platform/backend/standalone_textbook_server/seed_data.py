"""
示例数据生成 - 独立Textbook服务器
创建水箱实验教材示例数据
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Book, Chapter, Case


async def seed_example_data(db: AsyncSession):
    """创建示例教材数据"""
    print("🌱 开始创建示例教材数据...")

    # 1. 创建或获取书籍
    stmt = select(Book).where(Book.slug == "water-system-intro")
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()

    if not book:
        print("  📚 创建书籍: 智慧水利入门")
        book = Book(
            slug="water-system-intro",
            title="智慧水利入门",
            description="从零开始学习智慧水利系统",
            difficulty="beginner",
            status="published",
            is_free=True,
            price=0.0,
            estimated_hours=5,
            tags=["水利", "入门", "Python"]
        )
        db.add(book)
        await db.flush()
    else:
        print("  ✓ 书籍已存在")

    # 2. 创建章节
    stmt = select(Chapter).where(
        Chapter.book_id == book.id,
        Chapter.slug == "chapter-01"
    )
    result = await db.execute(stmt)
    chapter = result.scalar_one_or_none()

    if not chapter:
        print("  📖 创建章节: 第一章 - 基础概念")
        chapter = Chapter(
            book_id=book.id,
            slug="chapter-01",
            title="第一章：基础概念",
            order=1,
            content="# 第一章\n\n这是第一章的内容"
        )
        db.add(chapter)
        await db.flush()
    else:
        print("  ✓ 章节已存在")

    # 3. 创建案例
    stmt = select(Case).where(
        Case.chapter_id == chapter.id,
        Case.slug == "case-water-tank"
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()

    if not case:
        print("  📝 创建案例: 水箱实验")
        case = Case(
            chapter_id=chapter.id,
            slug="case-water-tank",
            title="案例1：水箱实验",
            order=1,
            difficulty="beginner",
            estimated_minutes=30,
            description="""## 实验目标

在这个实验中，我们将学习如何模拟一个简单的水箱系统。

## 物理原理

水箱的水量变化遵循质量守恒定律：

$$\\frac{dV}{dt} = Q_{in} - Q_{out}$$

其中：
- $V$ 是水箱中的水量（立方米）
- $Q_{in}$ 是入流量（立方米/秒）
- $Q_{out}$ 是出流量（立方米/秒）

## 数值求解

我们使用欧拉法进行数值积分 [代码行 8-10]：

```python
V = V + (Qin - Qout) * dt
```

## 可视化结果

最后，我们绘制水量随时间的变化曲线 [代码行 14-16]。

## 思考题

1. 如果入流量大于出流量，水量会如何变化？
2. 如果要保持水量恒定，应该如何调整？
""",
            starter_code="""# 水箱实验
# 初始化参数
V = 100.0  # 初始水量 (m³)
Qin = 10.0  # 入流量 (m³/s)
Qout = 8.0  # 出流量 (m³/s)
dt = 1.0  # 时间步长 (s)
T = 100  # 总时间 (s)

# 数值求解
time_list = []
volume_list = []

for t in range(T):
    V = V + (Qin - Qout) * dt
    time_list.append(t)
    volume_list.append(V)

# 可视化
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(time_list, volume_list, linewidth=2)
plt.xlabel('时间 (秒)')
plt.ylabel('水量 (立方米)')
plt.title('水箱水量变化')
plt.grid(True)
plt.show()

print(f"最终水量: {V:.2f} 立方米")
""",
            solution_code="""# 完整解决方案（带注释）
import matplotlib.pyplot as plt

# 初始化参数
V = 100.0  # 初始水量 (m³)
Qin = 10.0  # 入流量 (m³/s)
Qout = 8.0  # 出流量 (m³/s)
dt = 1.0  # 时间步长 (s)
T = 100  # 总时间 (s)

# 存储数据
time_list = []
volume_list = []

# 数值求解（欧拉法）
for t in range(T):
    # 质量守恒方程
    dV_dt = Qin - Qout
    V = V + dV_dt * dt

    # 记录数据
    time_list.append(t)
    volume_list.append(V)

# 可视化
plt.figure(figsize=(12, 6))

# 子图1：水量变化
plt.subplot(1, 2, 1)
plt.plot(time_list, volume_list, 'b-', linewidth=2, label='水量')
plt.axhline(y=100, color='r', linestyle='--', label='初始水量')
plt.xlabel('时间 (秒)')
plt.ylabel('水量 (立方米)')
plt.title('水箱水量随时间变化')
plt.legend()
plt.grid(True)

# 子图2：变化率
plt.subplot(1, 2, 2)
plt.axhline(y=Qin-Qout, color='g', linewidth=2)
plt.xlabel('时间 (秒)')
plt.ylabel('变化率 (m³/s)')
plt.title('水量变化率（恒定）')
plt.grid(True)

plt.tight_layout()
plt.show()

# 输出结果
print(f"初始水量: 100.00 立方米")
print(f"最终水量: {V:.2f} 立方米")
print(f"水量增加: {V - 100:.2f} 立方米")
print(f"理论值: {(Qin - Qout) * T:.2f} 立方米")
""",
            tags=["水箱", "质量守恒", "数值模拟"]
        )
        db.add(case)
    else:
        print("  ✓ 案例已存在")

    await db.commit()
    print("✅ 示例数据创建完成！")

    return {
        "book_slug": "water-system-intro",
        "chapter_slug": "chapter-01",
        "case_slug": "case-water-tank"
    }
