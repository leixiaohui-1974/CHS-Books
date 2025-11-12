# Sprint 1 详细任务清单（第3-4周）

**Sprint 目标：** 实现基础的左文右码布局和同步机制

**时间：** 2 周（10 个工作日）

**参与人员：**
- 前端工程师 D（主力）
- 前端工程师 E（支持）
- 后端工程师 A（API 支持）
- UI/UX 设计师（设计）
- 产品经理（需求澄清）

---

## 第1天（周一）：Sprint 启动与设计

### 上午：Sprint Planning Meeting

**时间：** 9:00 - 11:00

**议程：**
1. 回顾 Sprint 目标和验收标准
2. 分解任务到小时级别
3. 分配任务到个人
4. 识别风险和依赖

**输出：**
- [ ] 所有任务录入 Jira
- [ ] 任务分配完成
- [ ] 风险登记表

### 下午：设计评审

**时间：** 14:00 - 17:00

**任务：**
- [ ] **UI/UX 设计师：** 展示左文右码布局设计（Figma）
  - 桌面端布局（1440px、1920px）
  - 平板端布局（768px、1024px）
  - 移动端布局（375px、414px）
  - 交互原型（滚动同步、代码高亮）

- [ ] **前端工程师 D：** 技术可行性评估
  - Monaco Editor 集成方案
  - Markdown 渲染方案
  - 滚动同步实现方案

- [ ] **产品经理：** 确认需求细节
  - 用户故事验收标准
  - 边界情况处理

**输出：**
- [ ] 设计稿确认（Figma）
- [ ] 技术方案文档
- [ ] 风险和依赖清单

---

## 第2天（周二）：环境搭建与基础框架

### 前端工程师 D

**任务：** 搭建基础框架（6小时）

- [ ] **创建新组件：InteractiveTextbook.tsx** (1h)
  ```typescript
  // components/InteractiveTextbook/InteractiveTextbook.tsx
  interface InteractiveTextbookProps {
    bookSlug: string
    chapterSlug: string
    caseSlug: string
    onCodeExecute?: (code: string) => void
  }
  ```

- [ ] **实现左右分栏布局** (2h)
  - 使用 CSS Grid 或 Flexbox
  - 响应式断点（Desktop/Tablet/Mobile）
  - 拖拽分隔符调整大小

- [ ] **集成 Monaco Editor** (2h)
  - 安装 `@monaco-editor/react`
  - 基础配置（主题、语言、只读模式）
  - 测试编辑器渲染

- [ ] **集成 Markdown 渲染器** (1h)
  - 使用 `react-markdown` + `remark-gfm`
  - 配置 KaTeX 数学公式支持
  - 测试 Markdown 渲染

**验收标准：**
- [ ] 页面显示左右两栏
- [ ] 左侧可以渲染 Markdown
- [ ] 右侧显示代码编辑器
- [ ] 分隔符可以拖拽

### 后端工程师 A

**任务：** 准备测试数据和 API（4小时）

- [ ] **创建测试教材内容** (1h)
  - 编写示例 Markdown 教材（含 section ID）
  - 准备示例代码片段
  - 定义教材-代码映射关系

- [ ] **优化教材 API** (2h)
  - 支持按 section 查询
  - 返回代码引用信息
  - 添加缓存（Redis）

- [ ] **编写 API 文档** (1h)
  - OpenAPI 规范
  - 示例请求/响应

**验收标准：**
- [ ] API 返回正确的教材内容
- [ ] API 返回代码引用关系
- [ ] API 文档完整

---

## 第3天（周三）：教材渲染与样式

### 前端工程师 D

**任务：** 教材内容渲染（7小时）

- [ ] **实现教材加载逻辑** (2h)
  ```typescript
  const { data: textbook, isLoading } = useQuery(
    ['textbook', bookSlug, chapterSlug],
    () => fetchTextbook(bookSlug, chapterSlug)
  )
  ```

- [ ] **自定义 Markdown 组件** (3h)
  - 代码块高亮（syntax-highlighter）
  - 公式渲染（KaTeX）
  - 图片懒加载
  - 表格样式优化

- [ ] **Section ID 标记** (2h)
  - 为每个 section 添加唯一 ID
  - 支持锚点跳转
  - 高亮当前 section

**验收标准：**
- [ ] 教材内容正确渲染
- [ ] 公式显示正常
- [ ] 代码块高亮
- [ ] Section 有唯一 ID

### UI/UX 设计师

**任务：** 样式设计（6小时）

- [ ] **设计左侧教材样式** (3h)
  - 字体、行距、段落间距
  - 标题层级样式
  - 代码块样式
  - 公式样式

- [ ] **设计分隔符样式** (1h)
  - 正常状态
  - Hover 状态
  - 拖拽状态

- [ ] **设计响应式断点** (2h)
  - 桌面端（左右分栏）
  - 平板端（上下布局）
  - 移动端（单栏，可切换）

**输出：**
- [ ] CSS/SCSS 样式文件
- [ ] 设计 Token（颜色、字体、间距）

---

## 第4天（周四）：滚动同步机制

### 前端工程师 D

**任务：** 实现滚动同步（8小时）

- [ ] **教材滚动监听** (2h)
  ```typescript
  const handleTextbookScroll = () => {
    const sections = document.querySelectorAll('[data-section-id]')
    const currentSection = getCurrentVisibleSection(sections)
    syncCodeEditor(currentSection)
  }
  ```

- [ ] **代码定位逻辑** (3h)
  - 根据 section ID 找到对应代码行
  - 使用 Monaco API 滚动到指定行
  - 高亮对应代码块

- [ ] **反向同步（代码→教材）** (2h)
  - 监听代码编辑器滚动
  - 定位对应教材 section
  - 滚动教材到对应位置

- [ ] **优化滚动体验** (1h)
  - 防抖（debounce）
  - 平滑滚动动画
  - 避免循环触发

**验收标准：**
- [ ] 滚动教材时，代码自动定位
- [ ] 滚动代码时，教材自动定位
- [ ] 滚动流畅，无卡顿

### 前端工程师 E

**任务：** 支持和测试（6小时）

- [ ] **编写单元测试** (3h)
  - 测试滚动同步逻辑
  - 测试 section 识别
  - 测试边界情况

- [ ] **性能测试** (2h)
  - 大教材加载时间
  - 滚动帧率
  - 内存占用

- [ ] **兼容性测试** (1h)
  - Chrome、Firefox、Safari
  - 不同屏幕尺寸

**输出：**
- [ ] 单元测试覆盖率 > 80%
- [ ] 性能报告

---

## 第5天（周五）：代码高亮引用

### 前端工程师 D

**任务：** 实现代码引用功能（7小时）

- [ ] **教材中代码引用标记** (2h)
  ```markdown
  请看下面的代码 [→ 跳转到代码](#code-line-15)
  ```
  - 识别代码引用链接
  - 添加点击事件
  - 视觉样式（图标、颜色）

- [ ] **点击跳转逻辑** (3h)
  ```typescript
  const handleCodeReference = (lineNumber: number) => {
    editorRef.current?.revealLineInCenter(lineNumber)
    editorRef.current?.setSelection({
      startLineNumber: lineNumber,
      endLineNumber: lineNumber
    })
  }
  ```
  - 跳转到指定代码行
  - 高亮目标代码
  - 添加动画效果

- [ ] **高亮样式** (2h)
  - 代码行背景色
  - 闪烁动画
  - 持续时间（2秒后淡出）

**验收标准：**
- [ ] 点击教材中的代码引用，右侧代码跳转
- [ ] 目标代码行高亮
- [ ] 动画流畅自然

### 后端工程师 A

**任务：** API 优化（4小时）

- [ ] **添加代码引用解析** (2h)
  - 解析 Markdown 中的代码引用
  - 返回引用关系映射

- [ ] **缓存优化** (1h)
  - 缓存热门教材
  - 缓存失效策略

- [ ] **性能测试** (1h)
  - 并发请求测试
  - 响应时间统计

**输出：**
- [ ] API 响应时间 < 100ms
- [ ] 缓存命中率 > 80%

---

## 第6天（周一）：Inline 代码运行

### 前端工程师 D

**任务：** 实现 Inline 运行按钮（7小时）

- [ ] **识别可运行代码块** (2h)
  ```markdown
  ```python runnable
  print("Hello World")
  ```
  ```
  - 自定义 Markdown 渲染
  - 添加"运行"按钮
  - 按钮样式和位置

- [ ] **点击运行逻辑** (3h)
  ```typescript
  const handleInlineRun = async (code: string) => {
    // 1. 将代码加载到右侧编辑器
    editorRef.current?.setValue(code)

    // 2. 触发执行
    await executeCode(code)

    // 3. 显示结果（内联或底部面板）
    showExecutionResult(result)
  }
  ```

- [ ] **结果展示** (2h)
  - 内联展示（代码块下方）
  - 底部面板展示
  - 错误提示样式

**验收标准：**
- [ ] 可运行代码块显示"运行"按钮
- [ ] 点击后代码加载到编辑器
- [ ] 执行结果正确显示

### 前端工程师 E

**任务：** 集成测试（6小时）

- [ ] **完整流程测试** (3h)
  - 用户打开教材
  - 滚动教材，代码同步
  - 点击代码引用，跳转
  - 点击"运行"按钮，执行

- [ ] **错误场景测试** (2h)
  - 网络错误
  - 代码执行失败
  - 超时处理

- [ ] **编写 E2E 测试** (1h)
  ```typescript
  test('完整的左文右码流程', async ({ page }) => {
    await page.goto('/session?case=case_001')
    // ... 测试步骤
  })
  ```

**输出：**
- [ ] E2E 测试通过
- [ ] 测试覆盖率报告

---

## 第7天（周二）：响应式优化

### 前端工程师 E

**任务：** 响应式布局优化（8小时）

- [ ] **平板端适配** (3h)
  - 上下布局
  - 切换按钮（教材/代码）
  - 触摸交互优化

- [ ] **移动端适配** (3h)
  - 单栏布局
  - 底部 Tab 切换
  - 代码编辑器简化

- [ ] **响应式测试** (2h)
  - 不同设备测试
  - 横屏/竖屏切换
  - 触摸手势

**验收标准：**
- [ ] 平板端体验良好
- [ ] 移动端可用
- [ ] 无布局错乱

### UI/UX 设计师

**任务：** 移动端设计优化（6小时）

- [ ] **移动端交互设计** (3h)
  - 手势交互
  - 按钮大小（至少 44px）
  - 触摸区域

- [ ] **性能优化建议** (2h)
  - 减少动画
  - 懒加载优化
  - 首屏加载

- [ ] **可访问性检查** (1h)
  - 对比度检查
  - 键盘导航
  - 屏幕阅读器支持

**输出：**
- [ ] 移动端设计规范
- [ ] 可访问性检查报告

---

## 第8天（周三）：性能优化

### 前端工程师 D

**任务：** 性能优化（8小时）

- [ ] **代码分割** (2h)
  ```typescript
  const InteractiveTextbook = lazy(() =>
    import('./components/InteractiveTextbook')
  )
  ```

- [ ] **虚拟滚动** (3h)
  - 大教材内容虚拟化
  - 仅渲染可见部分
  - 使用 `react-window` 或自实现

- [ ] **Memoization** (2h)
  ```typescript
  const MemoizedMarkdown = React.memo(MarkdownRenderer)
  const syncedCode = useMemo(() =>
    calculateSyncedCode(currentSection),
    [currentSection]
  )
  ```

- [ ] **Lazy Loading** (1h)
  - 图片懒加载
  - 代码块懒加载

**输出：**
- [ ] Lighthouse 性能分数 > 90
- [ ] 首屏加载时间 < 2s

### 后端工程师 A

**任务：** 后端性能优化（6小时）

- [ ] **数据库查询优化** (2h)
  - 添加索引
  - 避免 N+1 查询
  - 使用 JOIN 优化

- [ ] **API 响应压缩** (1h)
  - 启用 Gzip
  - JSON 压缩

- [ ] **CDN 配置** (2h)
  - 静态资源 CDN
  - 图片 CDN
  - 缓存策略

- [ ] **负载测试** (1h)
  ```bash
  locust -f test_load.py --users 100 --spawn-rate 10
  ```

**输出：**
- [ ] API P95 延迟 < 200ms
- [ ] 支持 100 并发用户

---

## 第9天（周四）：Bug 修复与打磨

### 全员

**任务：** Bug 修复（8小时）

- [ ] **前端工程师 D&E：** 修复前端 Bug (6h)
  - 滚动同步 Bug
  - 响应式布局问题
  - 性能问题

- [ ] **后端工程师 A：** 修复后端 Bug (4h)
  - API 错误处理
  - 缓存问题
  - 性能瓶颈

- [ ] **UI/UX 设计师：** 视觉打磨 (6h)
  - 细节优化
  - 动画调优
  - 一致性检查

**输出：**
- [ ] 所有 P0/P1 Bug 修复
- [ ] 测试通过

---

## 第10天（周五）：Sprint Review & Retrospective

### 上午：Sprint Review

**时间：** 9:00 - 11:00

**议程：**
1. 演示左文右码功能（10分钟）
2. 产品经理验收（30分钟）
3. 利益相关者反馈（30分钟）
4. 决策：功能是否可发布（10分钟）

**验收标准检查：**
- [ ] 左文右码布局在桌面端完美展示
- [ ] 教材滚动时，代码自动定位到对应部分
- [ ] 点击教材中的"运行"按钮，代码立即执行
- [ ] 移动端有合理的降级方案（上下布局）
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E 测试通过
- [ ] Lighthouse 性能分数 > 90

### 下午：Sprint Retrospective

**时间：** 14:00 - 16:00

**议程：**
1. What went well? （30分钟）
2. What could be improved? （30分钟）
3. Action items for Sprint 2 （30分钟）
4. 庆祝成就 （30分钟）

**输出：**
- [ ] Retrospective 记录
- [ ] 改进行动项
- [ ] Sprint 2 优化计划

---

## 关键指标（KPI）

### 功能完成度
- [ ] 所有任务完成率：**目标 100%**
- [ ] Story Points 完成：**目标 100%**

### 质量指标
- [ ] 单元测试覆盖率：**目标 > 80%**
- [ ] E2E 测试通过率：**目标 100%**
- [ ] Bug 数量：**目标 < 5 个 P0/P1**

### 性能指标
- [ ] 首屏加载时间：**目标 < 2s**
- [ ] Lighthouse 性能分数：**目标 > 90**
- [ ] API P95 延迟：**目标 < 200ms**

### 用户体验
- [ ] 设计师评分：**目标 > 4.5/5**
- [ ] 产品经理评分：**目标 > 4.5/5**

---

## 风险与依赖

### 风险
1. **Monaco Editor 集成复杂度** - 高
   - 缓解：提前技术预研，准备 Plan B（使用简单的 textarea）

2. **滚动同步性能问题** - 中
   - 缓解：使用防抖，虚拟滚动

3. **移动端体验不佳** - 中
   - 缓解：提前移动端测试，降级方案

### 依赖
1. 后端 API 必须在第2天完成
2. 设计稿必须在第1天确认
3. 测试环境必须稳定

---

## 沟通计划

### 每日站会
- **时间：** 每天 9:30
- **时长：** 15分钟
- **地点：** 线上/线下

### 代码审查
- **频率：** 每天至少1次
- **Reviewer：** 技术负责人 + 另一名工程师

### 设计评审
- **时间：** 第3天、第7天
- **参与者：** 全员

---

## 工具与资源

### 开发工具
- Jira：任务管理
- Figma：设计稿
- GitHub：代码仓库
- Slack：即时通讯

### 测试工具
- Jest：单元测试
- Playwright：E2E 测试
- Lighthouse：性能测试

### 监控工具
- Sentry：错误追踪
- LogRocket：用户会话录制

---

**Sprint 负责人：** 前端工程师 D
**Scrum Master：** 产品经理
**创建日期：** 2025-11-12
**最后更新：** 2025-11-12
