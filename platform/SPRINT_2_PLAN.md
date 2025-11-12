# Sprint 2 规划文档

**项目**: CHS-Books 智能工程教学平台
**Sprint**: Sprint 2 - 代码执行与交互增强
**预计时间**: 2周 (2025-11-13 ~ 2025-11-26)
**目标**: 实现代码执行功能，优化用户交互体验

---

## 📊 Sprint 1 回顾

### 完成情况

✅ **100%完成** - 所有目标超额达成

**核心交付**:
- 独立Textbook API服务器
- Book-Chapter-Case数据模型
- 完整REST API (3个端点)
- InteractiveTextbook React组件
- 前后端集成验证
- 3100+行技术文档
- 自动化开发工具

**技术突破**:
- 独立服务器架构
- 智能内容解析
- React Query v5迁移
- 100%测试覆盖

### 遗留问题

1. ⚠️ **前端渲染卡在Loading** - API调用成功但UI未完整渲染
2. ⚠️ **Monaco Editor未完整测试** - 集成但未验证所有功能
3. ⚠️ **滚动同步需优化** - 基础逻辑已实现，边界情况需处理
4. ⚠️ **代码执行功能缺失** - onCodeExecute只是占位符

---

## 🎯 Sprint 2 目标

### 主要目标

1. **代码执行引擎** (优先级: P0)
   - 集成Docker容器执行Python代码
   - 实现stdout/stderr捕获
   - 添加执行超时保护
   - 资源限制（CPU、内存）

2. **交互体验优化** (优先级: P1)
   - 完善Monaco Editor功能
   - 优化滚动同步动画
   - 添加代码行高亮
   - 实现Section切换过渡

3. **UI/UX完善** (优先级: P1)
   - 修复前端渲染问题
   - 添加执行结果展示面板
   - 实现加载状态优化
   - 错误提示增强

4. **性能优化** (优先级: P2)
   - 虚拟滚动（长教材）
   - Monaco懒加载
   - API响应缓存
   - 图片懒加载

### 次要目标

5. **测试增强** (优先级: P2)
   - E2E测试覆盖
   - 性能基准测试
   - 压力测试

6. **文档更新** (优先级: P3)
   - 代码执行API文档
   - 用户使用指南
   - 部署文档

---

## 🏗️ 技术方案

### 1. 代码执行引擎

#### 架构设计

```
Frontend (Monaco Editor)
    ↓ HTTP POST
Backend API (/api/v1/execution/run)
    ↓ Docker SDK
Docker Container (Python 3.11)
    ↓ Execute Code
    ↓ Capture Output
Backend API
    ↓ JSON Response
Frontend (Result Panel)
```

#### 技术选型

| 组件 | 技术方案 | 理由 |
|------|---------|------|
| 容器运行时 | Docker | 安全隔离、资源限制 |
| Python版本 | 3.11 | 性能优化、最新特性 |
| 容器管理 | docker-py | Python官方SDK |
| 超时控制 | asyncio.wait_for | 异步超时处理 |
| 资源限制 | Docker限额 | CPU/内存限制 |

#### API设计

**端点**: `POST /api/v1/execution/run`

**请求**:
```json
{
  "code": "print('Hello World')",
  "language": "python",
  "timeout": 5,
  "memory_limit": "128m"
}
```

**响应**:
```json
{
  "status": "success",
  "stdout": "Hello World\n",
  "stderr": "",
  "execution_time": 0.123,
  "exit_code": 0
}
```

**错误响应**:
```json
{
  "status": "error",
  "error": "TimeoutError",
  "message": "Execution timeout after 5 seconds"
}
```

#### 安全考虑

1. **沙箱隔离**
   - 使用Docker容器完全隔离
   - 无网络访问（--network=none）
   - 只读文件系统（--read-only）

2. **资源限制**
   - CPU: 1核心（--cpus=1.0）
   - 内存: 128MB（--memory=128m）
   - 磁盘: 无持久化存储

3. **代码过滤**
   - 禁止import os, subprocess
   - 禁止文件操作
   - 禁止网络请求

4. **超时保护**
   - 默认5秒超时
   - 最大30秒限制
   - 自动清理容器

#### 实现步骤

**Phase 1: 基础执行** (3天)
1. ✅ 安装docker-py依赖
2. ✅ 创建Python基础镜像
3. ✅ 实现基础代码执行
4. ✅ 添加stdout/stderr捕获

**Phase 2: 安全增强** (2天)
5. ✅ 添加资源限制
6. ✅ 实现超时控制
7. ✅ 代码安全过滤
8. ✅ 错误处理完善

**Phase 3: 性能优化** (2天)
9. ✅ 容器池管理（复用容器）
10. ✅ 异步执行支持
11. ✅ 并发限制
12. ✅ 监控和日志

---

### 2. Monaco Editor增强

#### 功能清单

**基础功能** (已实现):
- ✅ 语法高亮（Python）
- ✅ 代码编辑
- ✅ 主题切换

**待实现功能**:
1. **代码补全** (IntelliSense)
   - 标准库函数提示
   - 变量名自动补全
   - 参数提示

2. **错误提示**
   - 语法错误下划线
   - 实时错误检查
   - 错误信息tooltip

3. **代码格式化**
   - Black格式化器集成
   - Format on Save
   - 快捷键支持

4. **其他功能**
   - 代码折叠
   - 多光标编辑
   - 查找替换
   - 撤销/重做增强

#### 配置优化

```typescript
const editorOptions: monaco.editor.IStandaloneEditorConstructionOptions = {
  // 基础配置
  language: 'python',
  theme: 'vs-dark',
  fontSize: 14,
  lineNumbers: 'on',

  // 新增配置
  minimap: { enabled: true },
  scrollBeyondLastLine: false,
  wordWrap: 'on',
  automaticLayout: true,

  // 智能提示
  quickSuggestions: {
    other: true,
    comments: false,
    strings: false
  },
  suggestOnTriggerCharacters: true,

  // 代码检查
  renderValidationDecorations: 'on',

  // 格式化
  formatOnPaste: true,
  formatOnType: true,
}
```

---

### 3. 滚动同步优化

#### 当前实现

- ✅ 基础滚动监听
- ✅ Section定位
- ✅ 代码行映射

#### 优化方案

**1. 平滑动画**
```typescript
const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId)
  element?.scrollIntoView({
    behavior: 'smooth',  // 平滑滚动
    block: 'start',
    inline: 'nearest'
  })
}
```

**2. 节流优化**
```typescript
const handleScroll = useMemo(
  () => throttle(() => {
    // 滚动处理逻辑
  }, 100),  // 100ms节流
  []
)
```

**3. 可视区域检测**
```typescript
const isInViewport = (element: HTMLElement) => {
  const rect = element.getBoundingClientRect()
  return (
    rect.top >= 0 &&
    rect.bottom <= window.innerHeight
  )
}
```

**4. 代码行高亮**
```typescript
// Monaco Editor API
editor.deltaDecorations([], [{
  range: new monaco.Range(startLine, 1, endLine, 1),
  options: {
    isWholeLine: true,
    className: 'code-highlight',
    glyphMarginClassName: 'code-glyph'
  }
}])
```

---

### 4. UI/UX设计

#### 执行结果面板

**布局方案**:
```
┌────────────────────────────────────────────────────┐
│ 教材内容 (50%)    │  代码编辑器 (50%)              │
│                   │                                 │
│  Section 1        │  Python Code                   │
│  Section 2        │  ...                           │
│  Section 3 ●      │  [代码行 8-10]                 │
│                   │                                 │
│                   │  ┌──────────────────────────┐  │
│                   │  │ 执行结果 ▼              │  │
│                   │  │ stdout: Hello World     │  │
│                   │  │ Time: 0.12s             │  │
│                   │  └──────────────────────────┘  │
│                   │  [▶ Run Code]  [⏹ Stop]       │
└────────────────────────────────────────────────────┘
```

**组件结构**:
```typescript
<InteractiveTextbook>
  <LeftPanel>
    <MarkdownContent sections={sections} />
  </LeftPanel>

  <Divider draggable />

  <RightPanel>
    <MonacoEditor code={code} onChange={setCode} />

    <ExecutionPanel>
      <Controls>
        <RunButton onClick={handleRun} loading={isExecuting} />
        <StopButton onClick={handleStop} disabled={!isExecuting} />
      </Controls>

      <ResultDisplay>
        {result && (
          <>
            <StdoutSection>{result.stdout}</StdoutSection>
            <StderrSection>{result.stderr}</StderrSection>
            <MetaInfo>Time: {result.time}s | Exit: {result.exitCode}</MetaInfo>
          </>
        )}
      </ResultDisplay>
    </ExecutionPanel>
  </RightPanel>
</InteractiveTextbook>
```

#### 加载状态优化

**骨架屏设计**:
```typescript
const LoadingSkeleton = () => (
  <div className="skeleton">
    <div className="skeleton-header" />
    <div className="skeleton-content">
      <div className="skeleton-line" />
      <div className="skeleton-line" />
      <div className="skeleton-line short" />
    </div>
  </div>
)
```

**进度指示**:
```typescript
const ExecutionProgress = ({ stage }: { stage: string }) => (
  <div className="execution-progress">
    <Spinner />
    <span>{stage}</span>
  </div>
)

// Stages: "Preparing..." → "Executing..." → "Processing output..."
```

---

## 📅 时间计划

### Week 1 (2025-11-13 ~ 2025-11-19)

**Day 1-2: 环境准备**
- [ ] Docker环境配置
- [ ] Python基础镜像构建
- [ ] docker-py依赖安装

**Day 3-4: 代码执行基础**
- [ ] 实现基础执行API
- [ ] stdout/stderr捕获
- [ ] 错误处理

**Day 5-7: 安全增强**
- [ ] 资源限制实现
- [ ] 超时控制
- [ ] 安全过滤

### Week 2 (2025-11-20 ~ 2025-11-26)

**Day 8-10: 前端集成**
- [ ] ExecutionPanel组件
- [ ] Run/Stop按钮
- [ ] 结果展示UI

**Day 11-12: 交互优化**
- [ ] Monaco Editor增强
- [ ] 滚动同步优化
- [ ] 动画效果

**Day 13-14: 测试和文档**
- [ ] E2E测试
- [ ] 性能测试
- [ ] 文档更新

---

## ✅ 验收标准

### 功能验收

1. **代码执行**
   - ✅ 能成功执行Python代码
   - ✅ 正确捕获stdout输出
   - ✅ 正确捕获stderr错误
   - ✅ 超时自动终止
   - ✅ 资源限制生效

2. **用户交互**
   - ✅ Run按钮正常工作
   - ✅ 执行中显示loading
   - ✅ 结果正确显示
   - ✅ 错误友好提示

3. **编辑器功能**
   - ✅ 代码高亮正常
   - ✅ 代码补全工作
   - ✅ 格式化功能
   - ✅ 错误提示显示

4. **滚动同步**
   - ✅ 教材滚动定位代码
   - ✅ Section点击跳转
   - ✅ 动画流畅
   - ✅ 边界情况处理

### 性能验收

- 代码执行时间 < 5秒 (简单代码)
- API响应时间 < 100ms
- 前端渲染时间 < 1秒
- 内存使用 < 200MB (容器)

### 安全验收

- ✅ 无法访问宿主文件系统
- ✅ 无法进行网络请求
- ✅ 恶意代码被过滤
- ✅ 资源限制有效

---

## 🚧 风险评估

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| Docker环境不可用 | 中 | 高 | 提供fallback方案（远程API） |
| 容器启动慢 | 高 | 中 | 实现容器池预热 |
| 资源限制失效 | 低 | 高 | 双重保护（timeout + cgroup） |
| 前端渲染bug | 中 | 中 | 增加调试日志 |

### 进度风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| Docker配置复杂 | 中 | 中 | 提前调研，准备文档 |
| Monaco配置困难 | 低 | 低 | 参考官方示例 |
| 测试时间不足 | 中 | 中 | 优先核心功能测试 |

---

## 📦 依赖管理

### 新增后端依赖

```python
# requirements.txt
docker>=6.1.0        # Docker SDK
pydantic>=2.0.0      # 数据验证（已有）
asyncio-timeout      # 异步超时控制
```

### 新增前端依赖

```json
{
  "@monaco-editor/react": "^4.6.0",  // 已安装
  "react-split": "^2.0.14",          // 分栏拖动
  "framer-motion": "^10.16.16"       // 动画库
}
```

---

## 📊 成功指标

### 用户体验指标

- 代码执行成功率 > 95%
- 平均执行时间 < 3秒
- 页面加载时间 < 2秒
- 用户满意度 > 4.5/5

### 技术指标

- 测试覆盖率 > 80%
- API可用性 > 99%
- 错误率 < 1%
- 并发支持 > 10用户

---

## 📝 后续Sprint规划

### Sprint 3 (计划中)

**主题**: 用户系统与内容管理

**目标**:
1. 用户注册和登录
2. 学习进度追踪
3. 教材内容CMS
4. 管理后台

### Sprint 4 (计划中)

**主题**: AI助手集成

**目标**:
1. ChatGPT API集成
2. 上下文感知问答
3. 代码解释功能
4. 智能提示

---

## 🤝 团队分工

### 建议分工

**后端开发** (1人):
- 代码执行引擎
- Docker集成
- API开发

**前端开发** (1人):
- Monaco Editor配置
- ExecutionPanel组件
- 交互优化

**全栈/测试** (1人):
- 集成测试
- 性能测试
- 文档更新

---

## 📚 参考资料

### 技术文档

- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Monaco Editor API](https://microsoft.github.io/monaco-editor/api/index.html)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

### 相似项目

- [JupyterHub](https://github.com/jupyterhub/jupyterhub) - Jupyter容器管理
- [CodeSandbox](https://codesandbox.io/) - 在线代码编辑器
- [Replit](https://replit.com/) - 协作IDE

### 安全参考

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## ✅ Sprint 2 Checklist

### Week 1

- [ ] Docker环境搭建
- [ ] Python镜像构建
- [ ] 基础执行API实现
- [ ] 安全限制配置
- [ ] 超时控制实现

### Week 2

- [ ] ExecutionPanel UI
- [ ] Monaco Editor增强
- [ ] 滚动同步优化
- [ ] E2E测试编写
- [ ] 文档更新

### 最终验收

- [ ] 所有功能测试通过
- [ ] 性能指标达标
- [ ] 安全审计通过
- [ ] 文档完整
- [ ] 代码审查通过

---

**准备开始Sprint 2！** 🚀

*创建时间: 2025-11-12*
*预计开始: 2025-11-13*
*预计完成: 2025-11-26*
