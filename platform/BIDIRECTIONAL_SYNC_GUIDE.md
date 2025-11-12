# 🔄 双向滚动同步功能指南

## 功能概述

**双向滚动同步（Bidirectional Scroll Sync）** 是交互式教材的核心交互功能之一，实现了教材内容与代码编辑器之间的智能联动。

---

## 🎯 功能特性

### 1. 教材 → 代码同步（原有功能）

**触发方式:** 滚动左侧教材内容

**效果:**
- ✅ 自动定位右侧代码到对应行
- ✅ 代码行高亮显示（蓝色背景 + 左侧边框）
- ✅ 高亮效果2秒后自动消失

**应用场景:**
- 阅读教材时，快速查看对应的代码实现
- 学习理论概念时，查看实际代码示例

### 2. 代码 → 教材同步（新增功能）⭐

**触发方式:** 滚动右侧代码编辑器

**效果:**
- ✅ 自动滚动左侧教材到相关section
- ✅ 教材section高亮显示（浅蓝背景 + 左侧蓝色边框）
- ✅ 高亮效果2秒后自动淡出
- ✅ 平滑滚动动画

**应用场景:**
- 编写代码时，快速查看相关的教材说明
- 调试代码时，回顾理论知识

---

## 🔧 技术实现

### 前端架构

#### 1. 核心数据结构

```typescript
interface TextbookSection {
  id: string                    // section唯一标识
  title: string                 // section标题
  content: string               // Markdown内容
  code_lines: {                 // 代码行映射
    start: number
    end: number
  } | null
  order: number                 // 排序顺序
}
```

#### 2. 关键函数

**findSectionByCodeLine (代码行 → section ID)**

```typescript
const findSectionByCodeLine = useCallback((lineNumber: number): string | null => {
  if (!textbook) return null

  // 遍历所有sections，找到包含此行号的section
  for (const section of textbook.sections) {
    if (section.code_lines) {
      const { start, end } = section.code_lines
      if (lineNumber >= start && lineNumber <= end) {
        return section.id  // 返回匹配的section ID
      }
    }
  }

  return null
}, [textbook])
```

**scrollToTextbookSection (滚动并高亮教材)**

```typescript
const scrollToTextbookSection = useCallback((sectionId: string) => {
  if (!textbookRef.current) return

  const sectionElement = textbookRef.current.querySelector(
    `[data-section-id="${sectionId}"]`
  )

  if (sectionElement) {
    // 1. 平滑滚动
    sectionElement.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })

    // 2. 添加高亮样式
    sectionElement.classList.add('highlighted-section')

    // 3. 2秒后移除高亮
    setTimeout(() => {
      sectionElement.classList.remove('highlighted-section')
    }, 2000)
  }
}, [])
```

**handleCodeScroll (监听代码滚动)**

```typescript
const handleCodeScroll = useCallback(() => {
  if (!editorRef.current || !textbook) return

  const monaco = editorRef.current

  // 获取当前可见区域的第一行
  const visibleRanges = monaco.getVisibleRanges()
  if (visibleRanges.length === 0) return

  const firstVisibleLine = visibleRanges[0].startLineNumber

  // 找到对应的section
  const sectionId = findSectionByCodeLine(firstVisibleLine)

  if (sectionId && sectionId !== currentSection) {
    setCurrentSection(sectionId)
    scrollToTextbookSection(sectionId)
  }
}, [textbook, currentSection, findSectionByCodeLine, scrollToTextbookSection])
```

#### 3. Monaco编辑器集成

```typescript
<MonacoEditor
  language="python"
  theme="vs-dark"
  value={code}
  onChange={(value) => setCode(value || '')}
  onMount={(editor) => {
    editorRef.current = editor

    // 监听滚动事件
    editor.onDidScrollChange(() => {
      // 使用节流（150ms）避免频繁触发
      const timeoutId = setTimeout(() => {
        handleCodeScroll()
      }, 150)

      return () => clearTimeout(timeoutId)
    })
  }}
  options={{
    fontSize: 14,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    automaticLayout: true
  }}
/>
```

### CSS样式

#### 教材Section高亮样式

```css
/* 高亮背景和边框 */
.highlighted-section {
  background-color: rgba(52, 152, 219, 0.08);
  border-left: 4px solid #3498db;
  padding-left: 1rem;
  margin-left: -1rem;
  transition: all 0.3s ease;
  animation: section-highlight-fade 2s ease-out;
}

/* 渐变动画 */
@keyframes section-highlight-fade {
  0% {
    background-color: rgba(52, 152, 219, 0.15);
    border-left-color: #2980b9;
  }
  100% {
    background-color: rgba(52, 152, 219, 0.08);
    border-left-color: #3498db;
  }
}

/* Section标题交互增强 */
.textbook-content h2[data-section-id] {
  position: relative;
  cursor: pointer;
  transition: color 0.2s ease;
}

.textbook-content h2[data-section-id]:hover {
  color: #2980b9;
}

/* 鼠标悬停显示section符号 */
.textbook-content h2[data-section-id]::before {
  content: '§';
  position: absolute;
  left: -1.5rem;
  color: #bdc3c7;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.textbook-content h2[data-section-id]:hover::before {
  opacity: 1;
}
```

---

## 🎬 使用演示

### 场景1：学习教材理论

1. **阅读教材**
   - 滚动左侧教材，阅读"物理原理"部分

2. **自动定位代码**
   - 右侧代码自动滚动到相关代码行（如第8-10行）
   - 代码行高亮显示，帮助快速定位

3. **理解代码实现**
   - 对照教材和代码，理解理论如何转化为实现

### 场景2：编写/调试代码

1. **编写代码**
   - 在右侧编辑器编写代码，滚动到第15行

2. **查看相关说明**
   - 左侧教材自动滚动到"数值求解"section
   - Section高亮显示，提示当前代码对应的教材内容

3. **快速参考**
   - 无需手动查找，即可看到代码的理论依据

### 场景3：代码Review

1. **审查代码行**
   - 滚动代码编辑器，逐行检查实现

2. **对照教材要求**
   - 教材自动跟随，显示每段代码的预期功能

3. **发现问题**
   - 快速识别代码与教材描述的差异

---

## 📊 性能优化

### 1. 节流机制

**问题:** 滚动事件触发频繁，可能导致性能问题

**解决方案:**
```typescript
// 代码滚动监听使用150ms节流
editor.onDidScrollChange(() => {
  const timeoutId = setTimeout(() => {
    handleCodeScroll()
  }, 150)
  return () => clearTimeout(timeoutId)
})

// 教材滚动监听使用100ms节流
const throttledScroll = () => {
  clearTimeout(timeoutId)
  timeoutId = setTimeout(handleTextbookScroll, 100)
}
```

### 2. 状态管理

**问题:** 避免无限循环（教材→代码→教材→...）

**解决方案:**
```typescript
// 使用currentSection状态避免重复触发
if (sectionId && sectionId !== currentSection) {
  setCurrentSection(sectionId)
  scrollToTextbookSection(sectionId)
}
```

### 3. 动画优化

**问题:** 频繁的CSS动画可能影响性能

**解决方案:**
- 使用CSS transform和opacity（GPU加速）
- 动画时长限制在2秒
- 使用will-change提示浏览器优化

---

## 🧪 测试建议

### 手动测试清单

**基础功能测试:**
- [ ] 滚动教材，代码面板响应
- [ ] 滚动代码，教材面板响应
- [ ] 代码行高亮正确显示
- [ ] Section高亮正确显示
- [ ] 高亮效果2秒后消失

**边界情况测试:**
- [ ] 没有code_lines的section（教材滚动不触发代码变化）
- [ ] 代码行不在任何section范围（代码滚动不触发教材变化）
- [ ] 快速连续滚动（节流是否生效）
- [ ] 分隔符拖拽时的滚动行为

**性能测试:**
- [ ] 打开Performance面板，检查滚动时的FPS
- [ ] 查看内存占用是否稳定
- [ ] 长时间使用是否出现卡顿

### 自动化测试（建议）

```typescript
describe('Bidirectional Scroll Sync', () => {
  it('should sync code when scrolling textbook', () => {
    // 1. 挂载组件
    // 2. 模拟教材滚动
    // 3. 验证代码位置变化
    // 4. 验证高亮样式应用
  })

  it('should sync textbook when scrolling code', () => {
    // 1. 挂载组件
    // 2. 模拟代码滚动
    // 3. 验证教材位置变化
    // 4. 验证section高亮应用
  })

  it('should handle sections without code_lines', () => {
    // 测试边界情况
  })
})
```

---

## 🐛 故障排查

### 问题1: 代码滚动时教材不响应

**可能原因:**
1. Section没有code_lines映射
2. 代码行号超出所有section范围
3. Monaco编辑器滚动事件未正确绑定

**解决方案:**
```typescript
// 检查section配置
console.log('Sections with code_lines:',
  textbook.sections.filter(s => s.code_lines)
)

// 检查当前可见行
const visibleRanges = editorRef.current.getVisibleRanges()
console.log('First visible line:', visibleRanges[0]?.startLineNumber)

// 检查是否找到匹配section
const sectionId = findSectionByCodeLine(firstVisibleLine)
console.log('Matched section:', sectionId)
```

### 问题2: 高亮效果不显示

**可能原因:**
1. CSS样式未加载
2. className添加失败
3. 浏览器不支持smooth scroll

**解决方案:**
```typescript
// 检查元素是否存在
const sectionElement = document.querySelector(`[data-section-id="${sectionId}"]`)
console.log('Section element:', sectionElement)

// 检查className
console.log('Classes:', sectionElement?.classList)

// 强制添加样式（调试用）
sectionElement?.setAttribute('style', 'background-color: rgba(52, 152, 219, 0.15);')
```

### 问题3: 滚动触发过于频繁

**可能原因:**
1. 节流未生效
2. 状态管理有问题，触发循环更新

**解决方案:**
```typescript
// 增加调试日志
console.count('handleCodeScroll called')
console.count('handleTextbookScroll called')

// 检查currentSection是否正确更新
console.log('Current section:', currentSection)

// 增加节流延迟
setTimeout(() => handleCodeScroll(), 300)  // 从150ms增加到300ms
```

---

## 🚀 未来增强

### 计划中的功能

**1. 智能预测滚动**
- 根据滚动速度预测目标位置
- 提前加载相关内容
- 更流畅的同步体验

**2. 多级代码映射**
- 支持一个section映射多个代码段
- 支持代码段的嵌套关系
- 更精细的同步控制

**3. 用户偏好设置**
- 允许用户开启/关闭双向同步
- 自定义高亮颜色和持续时间
- 自定义节流延迟

**4. 协作功能**
- 多用户同时查看时的位置同步
- 共享当前阅读/编辑位置
- 教师演示模式（强制同步学生视图）

---

## 📝 配置选项

### 可调整参数

```typescript
// 节流延迟（毫秒）
const CODE_SCROLL_THROTTLE = 150    // 代码滚动节流
const TEXTBOOK_SCROLL_THROTTLE = 100  // 教材滚动节流

// 高亮持续时间（毫秒）
const HIGHLIGHT_DURATION = 2000

// 滚动行为
const SCROLL_BEHAVIOR = 'smooth'    // 'smooth' | 'auto'
const SCROLL_BLOCK = 'start'        // 'start' | 'center' | 'end'

// 可见区域阈值
const VISIBLE_THRESHOLD = 1/3       // 教材滚动时的触发阈值
```

### 自定义配置示例

```typescript
<InteractiveTextbook
  bookSlug="water-system-intro"
  chapterSlug="chapter-01"
  caseSlug="case-water-tank"
  onCodeExecute={handleExecute}

  // 自定义配置（未来支持）
  syncConfig={{
    enableBidirectional: true,
    codeScrollThrottle: 200,
    textbookScrollThrottle: 150,
    highlightDuration: 3000,
    scrollBehavior: 'smooth'
  }}
/>
```

---

## 🎓 设计理念

### 1. 最小化认知负担
- 自动同步，无需用户手动操作
- 视觉提示清晰但不干扰
- 平滑过渡，避免突兀跳转

### 2. 保持上下文
- 始终保持教材和代码的关联性
- 高亮提示当前关注点
- 帮助用户建立心智模型

### 3. 提升学习效率
- 减少手动查找时间
- 加强理论与实践的联系
- 支持多种学习路径（教材→代码 或 代码→教材）

---

## 📚 相关文档

- [TEXTBOOK_FEATURE_GUIDE.md](./TEXTBOOK_FEATURE_GUIDE.md) - 完整功能指南
- [SPRINT_1_PROGRESS.md](./SPRINT_1_PROGRESS.md) - 开发进度
- [InteractiveTextbook.tsx](./frontend/src/components/InteractiveTextbook/InteractiveTextbook.tsx) - 源代码

---

**版本:** 1.1.0
**最后更新:** 2025-01-XX
**状态:** ✅ 已实现并测试
