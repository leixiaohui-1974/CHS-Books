# 📚 交互式教材功能指南

## 功能概述

**交互式教材（Interactive Textbook）** 是平台的核心功能之一，实现了"左文右码"的布局方式，支持教材内容与代码的深度集成。

### 核心特性

✅ **左右分栏布局**
- 左侧：Markdown教材内容（支持数学公式、图表）
- 右侧：Monaco代码编辑器（VS Code同款）
- 可拖拽调整分栏比例（30%-70%）

✅ **滚动同步**
- 教材滚动 → 自动定位到对应代码行
- 代码行自动高亮显示
- 支持教材中的代码引用链接

✅ **Section级别解析**
- 按 `##` 二级标题自动分割内容
- 每个section可映射到特定代码行
- 支持标记：`[代码行 15-20]`

✅ **Inline代码执行**
- 教材中的代码块可直接运行
- 一键加载到编辑器
- 支持实时执行和结果展示

---

## 技术架构

### 后端 API

#### 端点1: 获取教材内容

```http
GET /api/v1/textbooks/{book_slug}/{chapter_slug}/{case_slug}
```

**响应示例:**

```json
{
  "book_slug": "water-system-intro",
  "chapter_slug": "chapter-01",
  "case_slug": "case-water-tank",
  "title": "案例1：水箱实验",
  "description": "...",
  "sections": [
    {
      "id": "experiment-goal",
      "title": "实验目标",
      "content": "学习水箱系统...",
      "code_lines": null,
      "order": 0
    },
    {
      "id": "physical-principle",
      "title": "物理原理",
      "content": "水箱的水量变化...",
      "code_lines": {
        "start": 8,
        "end": 10
      },
      "order": 1
    }
  ],
  "starter_code": "# 水箱实验\nV = 100...",
  "solution_code": "# 完整解决方案...",
  "difficulty": "beginner",
  "estimated_minutes": 30,
  "tags": ["水箱", "数值模拟"]
}
```

#### 端点2: 获取单个Section

```http
GET /api/v1/textbooks/{book}/{chapter}/{case}/sections/{section_id}
```

#### 端点3: 创建示例数据（开发用）

```http
POST /api/v1/textbooks/dev/seed-example
```

### 前端组件

#### InteractiveTextbook 组件

**位置:** `frontend/src/components/InteractiveTextbook/InteractiveTextbook.tsx`

**Props:**

```typescript
interface InteractiveTextbookProps {
  bookSlug: string         // 书籍slug
  chapterSlug: string      // 章节slug
  caseSlug: string         // 案例slug
  onCodeExecute?: (code: string) => void  // 代码执行回调
}
```

**使用示例:**

```tsx
import InteractiveTextbook from '@/components/InteractiveTextbook/InteractiveTextbook'

<InteractiveTextbook
  bookSlug="water-system-intro"
  chapterSlug="chapter-01"
  caseSlug="case-water-tank"
  onCodeExecute={(code) => {
    // 执行代码逻辑
  }}
/>
```

---

## 教材内容编写规范

### Markdown格式

```markdown
## 实验目标

这是第一个section的内容。可以包含：
- 列表项
- **粗体文本**
- `行内代码`

## 物理原理

水箱的水量变化遵循质量守恒定律 [代码行 8-10]：

$$\frac{dV}{dt} = Q_{in} - Q_{out}$$

其中这段内容会自动关联到代码的第8-10行。

## 数值求解

使用欧拉法进行数值积分：

```python
V = V + (Qin - Qout) * dt
```

## 可视化结果

绘制水量随时间的变化曲线 [代码行 14-16]。
```

### 代码行标记语法

支持两种标记方式：

1. **区间标记:** `[代码行 15-20]` → 映射到第15-20行
2. **单行标记:** `(#code-line-15)` → 映射到第15行

### 数学公式

使用 KaTeX 语法：

- 行内公式: `$E = mc^2$`
- 块级公式: `$$\int_{0}^{\infty} e^{-x} dx = 1$$`

---

## 快速开始

### 1. 启动后端服务

```bash
cd platform/backend

# 安装依赖（首次）
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问: http://localhost:8000/docs

### 2. 创建示例数据

在API文档中执行：

```http
POST /api/v1/textbooks/dev/seed-example
```

或使用curl:

```bash
curl -X POST http://localhost:8000/api/v1/textbooks/dev/seed-example
```

### 3. 启动前端服务

```bash
cd platform/frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端服务启动后访问: http://localhost:3000

### 4. 访问演示页面

打开浏览器访问:

```
http://localhost:3000/textbook-demo
```

你应该看到：
- ✅ 左侧显示教材内容（水箱实验）
- ✅ 右侧显示代码编辑器
- ✅ 中间有可拖拽的分隔符
- ✅ 滚动教材时代码自动定位

---

## 测试

### 运行后端单元测试

```bash
cd platform/backend

# 测试教材API解析功能
python test_textbook_api.py
```

**预期输出:**

```
🚀 开始测试教材API功能

📚 教材内容解析测试
解析结果: 找到 3 个 sections

Section ID: intro
  标题: 介绍
  内容长度: 45 字符
  代码行: 无

Section ID: physical-principle
  标题: 物理原理
  内容长度: 67 字符
  代码行: 5-10

✅ 所有测试通过！
```

### 运行集成测试

```bash
cd platform/backend

# 完整集成测试（数据库 + API + 解析）
python test_integration.py
```

**预期输出:**

```
🚀 开始集成测试：教材API完整流程

📦 步骤1: 创建数据库引擎
✅ 数据库表创建成功

📦 步骤2: 创建测试数据
✅ 测试数据创建成功

📦 步骤3: 测试教材内容解析
   解析到 3 个sections
✅ 教材内容解析测试通过

📦 步骤4: 测试API端点
   API响应:
   - 标题: 水箱模拟实验
   - Sections: 4
✅ API端点测试通过

🎉 所有集成测试通过！
```

### 前端组件测试

```bash
cd platform/frontend

# 运行Jest测试（TODO：待添加）
npm test
```

---

## API使用示例

### Python客户端

```python
import requests

# 1. 创建示例数据
response = requests.post('http://localhost:8000/api/v1/textbooks/dev/seed-example')
print(response.json())

# 2. 获取教材内容
response = requests.get(
    'http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank'
)
textbook = response.json()

print(f"标题: {textbook['title']}")
print(f"Sections: {len(textbook['sections'])}")

for section in textbook['sections']:
    print(f"\n### {section['title']}")
    print(section['content'][:100] + '...')
    if section['code_lines']:
        print(f"代码行: {section['code_lines']['start']}-{section['code_lines']['end']}")
```

### JavaScript客户端

```javascript
// 1. 获取教材内容
const response = await fetch(
  '/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank'
)
const textbook = await response.json()

console.log('标题:', textbook.title)
console.log('Sections:', textbook.sections.length)

// 2. 遍历sections
textbook.sections.forEach(section => {
  console.log(`\n### ${section.title}`)
  console.log(section.content.substring(0, 100))

  if (section.code_lines) {
    console.log(`代码行: ${section.code_lines.start}-${section.code_lines.end}`)
  }
})

// 3. 获取初始代码
console.log('\n初始代码:')
console.log(textbook.starter_code)
```

---

## 开发指南

### 添加新的教材案例

#### 方法1: 使用数据库种子脚本

```python
from app.models.book import Book, Chapter, Case

async def create_new_case(db: AsyncSession):
    # 1. 查找或创建书籍
    book = await db.execute(
        select(Book).where(Book.slug == "your-book-slug")
    )
    book = book.scalar_one()

    # 2. 创建章节
    chapter = Chapter(
        book_id=book.id,
        slug="chapter-02",
        title="第二章：高级主题",
        order=2
    )
    db.add(chapter)
    await db.flush()

    # 3. 创建案例
    case = Case(
        chapter_id=chapter.id,
        slug="advanced-case",
        title="高级案例",
        order=1,
        difficulty="intermediate",
        estimated_minutes=45,
        description="""
## 案例目标

学习高级数值方法。

## 核心算法

使用Runge-Kutta方法 [代码行 10-25]。

## 结果分析

对比不同方法的精度。
        """,
        starter_code="""
# 高级数值模拟
import numpy as np

def runge_kutta(f, y0, t):
    # RK4实现
    pass
        """,
        solution_code="# 完整解决方案...",
        tags=["高级", "RK4"]
    )
    db.add(case)
    await db.commit()
```

#### 方法2: 使用API（开发环境）

修改 `app/api/endpoints/textbooks.py` 中的 `seed_example_textbook` 函数，添加你的案例数据。

### 扩展代码行映射规则

在 `app/api/endpoints/textbooks.py` 中修改 `extract_code_line_mapping` 函数：

```python
def extract_code_line_mapping(content: str, code: str) -> Optional[CodeLineMapping]:
    """扩展支持新的标记格式"""

    # 现有格式
    match = re.search(r'\[代码行\s+(\d+)-(\d+)\]', content)
    if match:
        return CodeLineMapping(...)

    # 新格式1: 英文标记
    match = re.search(r'\[line\s+(\d+)-(\d+)\]', content)
    if match:
        return CodeLineMapping(...)

    # 新格式2: 函数名引用
    match = re.search(r'\[@function\s+(\w+)\]', content)
    if match:
        # 在代码中搜索函数定义...
        return CodeLineMapping(...)

    return None
```

### 自定义Markdown渲染

在 `InteractiveTextbook.tsx` 中修改 `components` 对象：

```typescript
const components = {
  // 添加自定义组件
  blockquote: ({ children, ...props }: any) => (
    <div className="custom-blockquote" {...props}>
      💡 {children}
    </div>
  ),

  // 自定义表格样式
  table: ({ children, ...props }: any) => (
    <table className="custom-table" {...props}>
      {children}
    </table>
  ),

  // 现有组件...
  code: ...,
  a: ...,
  h2: ...
}
```

---

## 故障排查

### 问题1: API返回404

**症状:** `GET /api/v1/textbooks/...` 返回404

**解决方案:**

1. 检查路由注册:
   ```python
   # app/api/__init__.py
   api_router.include_router(textbooks.router, prefix="/textbooks", tags=["教材内容"])
   ```

2. 检查数据是否存在:
   ```bash
   curl http://localhost:8000/api/v1/textbooks/dev/seed-example -X POST
   ```

### 问题2: 前端无法加载数据

**症状:** 前端显示"教材加载失败"

**解决方案:**

1. 检查CORS配置:
   ```python
   # app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. 检查API URL:
   ```typescript
   // 确保使用正确的base URL
   const response = await fetch(
     `/api/v1/textbooks/${bookSlug}/${chapterSlug}/${caseSlug}`
   )
   ```

3. 检查浏览器控制台:
   - 打开开发者工具 (F12)
   - 查看Network标签
   - 检查API请求状态

### 问题3: 代码行映射不工作

**症状:** 滚动教材时代码不高亮

**解决方案:**

1. 检查section的`code_lines`字段:
   ```json
   {
     "code_lines": {
       "start": 8,
       "end": 10
     }
   }
   ```

2. 检查标记格式:
   ```markdown
   正确: [代码行 8-10]
   错误: [代码行8-10]  // 缺少空格
   错误: (代码行 8-10)  // 错误的括号
   ```

3. 检查Monaco Editor是否已挂载:
   ```typescript
   // InteractiveTextbook.tsx
   onMount={(editor) => {
     editorRef.current = editor
     console.log('Editor mounted:', editor)
   }}
   ```

### 问题4: Markdown渲染异常

**症状:** 数学公式不显示、代码块无语法高亮

**解决方案:**

1. 检查依赖:
   ```bash
   npm list react-markdown remark-gfm remark-math rehype-katex
   ```

2. 确保导入KaTeX CSS:
   ```typescript
   import 'katex/dist/katex.min.css'
   ```

3. 检查插件配置:
   ```typescript
   <ReactMarkdown
     remarkPlugins={[remarkGfm, remarkMath]}
     rehypePlugins={[rehypeKatex]}
   >
   ```

---

## 性能优化

### 后端优化

1. **数据库查询优化:**
   ```python
   # 使用eager loading
   stmt = select(Case).options(
       selectinload(Case.chapter).selectinload(Chapter.book)
   )
   ```

2. **添加缓存:**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=128)
   def parse_content_to_sections(content: str, code: str):
       # 缓存解析结果
       pass
   ```

### 前端优化

1. **使用React Query缓存:**
   ```typescript
   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 5 * 60 * 1000,  // 5分钟
         cacheTime: 10 * 60 * 1000, // 10分钟
       },
     },
   })
   ```

2. **滚动节流:**
   ```typescript
   const throttledScroll = useCallback(
     throttle(handleTextbookScroll, 100),
     [handleTextbookScroll]
   )
   ```

3. **代码懒加载:**
   ```typescript
   const MonacoEditor = dynamic(
     () => import('@monaco-editor/react'),
     { ssr: false }
   )
   ```

---

## 路线图

### Sprint 2 (已规划)
- [ ] 双向滚动同步（代码 → 教材）
- [ ] 代码执行结果内联显示
- [ ] 支持多种编程语言
- [ ] 代码diff对比（初始代码 vs 解决方案）

### Sprint 3 (已规划)
- [ ] 实时协作编辑
- [ ] 教材版本控制
- [ ] AI智能提示（代码补全、错误诊断）
- [ ] 学习进度追踪

### 未来规划
- [ ] 移动端适配
- [ ] 离线模式
- [ ] 教材导出（PDF、EPUB）
- [ ] 社区分享功能

---

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交Pull Request

### 代码规范

- **Python:** 遵循PEP 8，使用black格式化
- **TypeScript:** 遵循Airbnb风格，使用prettier格式化
- **提交信息:** 使用约定式提交 (Conventional Commits)

---

## 许可证

本项目采用 MIT 许可证。

---

## 联系方式

- 项目主页: [GitHub](https://github.com/...)
- 文档: [https://docs.example.com](https://docs.example.com)
- 问题反馈: [GitHub Issues](https://github.com/.../issues)

---

## 更新日志

### v1.0.0 (2025-01-XX)

**新功能:**
- ✨ 左文右码布局
- ✨ Section级别内容解析
- ✨ 代码行映射 (`[代码行 X-Y]`)
- ✨ Markdown渲染（支持数学公式）
- ✨ 滚动同步（教材 → 代码）
- ✨ 可拖拽分隔符

**API端点:**
- `GET /api/v1/textbooks/{book}/{chapter}/{case}`
- `GET /api/v1/textbooks/{book}/{chapter}/{case}/sections/{id}`
- `POST /api/v1/textbooks/dev/seed-example`

**前端组件:**
- `InteractiveTextbook` 组件
- `/textbook-demo` 演示页面

---

**最后更新:** 2025-01-XX
**版本:** 1.0.0
**状态:** ✅ 生产就绪
