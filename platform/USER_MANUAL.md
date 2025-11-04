# 智能知识平台 V2.0 - 用户手册

**版本**: V2.0.0  
**更新日期**: 2025-11-04

---

## 📖 目录

1. [快速入门](#快速入门)
2. [功能介绍](#功能介绍)
3. [详细使用说明](#详细使用说明)
4. [常见问题](#常见问题)
5. [技巧与最佳实践](#技巧与最佳实践)

---

## 快速入门

### 第一步：启动平台

```bash
cd /workspace/platform/backend
./manage.py docker up
```

等待服务启动完成（约30秒）。

### 第二步：访问平台

打开浏览器访问：
- **API文档**: http://localhost:8000/docs
- **前端界面**: http://localhost:3000 (如果启动了前端)

### 第三步：创建第一个学习会话

#### 方式1：使用Python SDK

```python
from platform_sdk import PlatformSDK

# 初始化SDK
sdk = PlatformSDK()

# 创建会话
session = sdk.create_session(
    user_id="your_user_id",
    book_slug="water-environment-simulation",
    case_slug="case_01_diffusion"
)

print(f"会话已创建: {session['session_id']}")
```

#### 方式2：使用API

```bash
curl -X POST "http://localhost:8000/api/v2/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "book_slug": "water-environment-simulation",
    "case_slug": "case_01_diffusion"
  }'
```

---

## 功能介绍

### 1. 会话管理

**功能说明**：管理您的学习会话，包括创建、暂停、恢复、延长和终止。

**主要特性**：
- ✅ 自动超时管理（默认2小时）
- ✅ 会话状态追踪
- ✅ 文件版本控制
- ✅ 会话历史记录

**使用场景**：
- 开始学习某个案例
- 暂停学习，稍后继续
- 查看学习历史

### 2. 代码智能

**功能说明**：智能分析、验证和管理您的代码。

**主要特性**：
- ✅ AST语法分析
- ✅ 代码结构提取
- ✅ 依赖自动检测
- ✅ 语法验证
- ✅ 代码格式化
- ✅ 差异对比

**使用场景**：
- 加载案例代码
- 修改代码参数
- 查看代码结构
- 验证语法正确性

### 3. 代码执行

**功能说明**：在安全的Docker环境中执行Python代码。

**主要特性**：
- ✅ 隔离执行环境
- ✅ 实时输出反馈
- ✅ 资源限制保护
- ✅ 依赖自动安装

**使用场景**：
- 运行案例脚本
- 测试代码修改
- 验证计算结果

### 4. AI助手

**功能说明**：智能AI助手，帮助您理解代码、诊断错误、分析结果。

**主要特性**：
- ✅ 代码智能讲解
- ✅ 错误诊断建议
- ✅ 知识问答
- ✅ 结果深度分析

**使用场景**：
- 理解代码逻辑
- 解决运行错误
- 提出学习问题
- 分析计算结果

### 5. 结果展示

**功能说明**：标准化展示代码执行结果。

**主要特性**：
- ✅ 图表自动识别
- ✅ 数据表格展示
- ✅ 关键指标提取
- ✅ 报告生成

**使用场景**：
- 查看计算结果
- 分析图表数据
- 导出研究报告

---

## 详细使用说明

### 会话管理详解

#### 创建会话

```python
session = sdk.create_session(
    user_id="user_001",
    book_slug="water-environment-simulation",  # 书籍标识
    case_slug="case_01_diffusion"              # 案例标识
)
```

**返回信息**：
```json
{
  "session_id": "session_20251104_120000",
  "user_id": "user_001",
  "book_slug": "water-environment-simulation",
  "case_slug": "case_01_diffusion",
  "status": "active",
  "created_at": "2025-11-04T12:00:00Z",
  "expires_at": "2025-11-04T14:00:00Z"
}
```

#### 查询会话

```python
# 获取单个会话
session = sdk.get_session("session_20251104_120000")

# 获取用户的所有会话
sessions = sdk.list_sessions("user_001")
```

#### 暂停和恢复会话

```python
# 暂停会话（保存当前状态）
sdk.pause_session("session_20251104_120000")

# 稍后恢复
sdk.resume_session("session_20251104_120000")
```

#### 延长会话

```python
# 延长2小时（默认）
sdk.extend_session("session_20251104_120000")

# 延长指定时间
sdk.extend_session("session_20251104_120000", hours=4)
```

#### 终止会话

```python
# 终止会话（清理所有资源）
sdk.terminate_session("session_20251104_120000")
```

### 代码管理详解

#### 加载案例代码

```python
code = sdk.load_code(
    book_slug="water-environment-simulation",
    case_slug="case_01_diffusion"
)

print(f"主文件: {code['main_file']}")
print(f"文件数: {len(code['files'])}")

# 查看文件内容
for file in code['files']:
    print(f"\n文件: {file['name']}")
    print(f"行数: {file['lines']}")
    print(f"函数数: {file['analysis']['functions']}")
```

#### 代码分析

```python
code = """
import numpy as np

def solve_equation(a, b, c):
    delta = b**2 - 4*a*c
    if delta < 0:
        return None
    x1 = (-b + np.sqrt(delta)) / (2*a)
    x2 = (-b - np.sqrt(delta)) / (2*a)
    return x1, x2
"""

analysis = sdk.analyze_code(code)

print(f"函数: {analysis['functions']}")
print(f"导入: {analysis['imports']}")
print(f"复杂度: {analysis['complexity']}")
```

#### 编辑文件

```python
# 修改代码
new_code = """
import numpy as np

def solve_equation(a, b, c):
    # 增加输入验证
    if a == 0:
        raise ValueError("a不能为0")
    
    delta = b**2 - 4*a*c
    if delta < 0:
        return None
    
    x1 = (-b + np.sqrt(delta)) / (2*a)
    x2 = (-b - np.sqrt(delta)) / (2*a)
    return x1, x2
"""

sdk.edit_file(
    session_id="session_20251104_120000",
    file_path="solver.py",
    content=new_code
)
```

#### 查看差异

```python
# 查看修改前后的差异
diff = sdk.get_diff(
    session_id="session_20251104_120000",
    file_path="solver.py"
)

print("差异:")
print(diff['diff'])
```

#### 代码验证

```python
# 验证代码语法
result = sdk.validate_code(code)

if result['is_valid']:
    print("✓ 代码语法正确")
else:
    print("✗ 语法错误:")
    for error in result['errors']:
        print(f"  - {error}")
```

#### 代码格式化

```python
# 使用Black格式化代码
formatted = sdk.format_code(code)
print(formatted['formatted_code'])
```

### 代码执行详解

#### 启动执行

```python
execution = sdk.start_execution(
    session_id="session_20251104_120000",
    script_path="main.py",
    parameters={
        "D": 0.2,      # 扩散系数
        "nx": 100,     # 网格数
        "nt": 1000     # 时间步数
    }
)

print(f"执行ID: {execution['execution_id']}")
print(f"状态: {execution['status']}")
```

#### 查询执行状态

```python
import time

execution_id = execution['execution_id']

# 轮询状态
while True:
    status = sdk.get_execution(execution_id)
    
    print(f"状态: {status['status']}")
    
    if status['status'] == 'completed':
        print("✓ 执行完成")
        print(f"结果: {status['results']}")
        break
    elif status['status'] == 'failed':
        print("✗ 执行失败")
        print(f"错误: {status['error']}")
        break
    
    time.sleep(2)
```

#### WebSocket实时输出

```python
import websocket

def on_message(ws, message):
    data = json.loads(message)
    
    if data['type'] == 'output':
        print(f"输出: {data['data']}")
    elif data['type'] == 'status':
        print(f"状态: {data['status']}")

ws = websocket.WebSocketApp(
    f"ws://localhost:8000/api/v2/execution/ws/{execution_id}",
    on_message=on_message
)

ws.run_forever()
```

### AI助手详解

#### 代码讲解

```python
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

explanation = sdk.explain_code(
    code=code,
    context="斐波那契数列计算"
)

print("讲解:")
print(explanation['explanation'])

print("\n关键要点:")
for point in explanation['key_points']:
    print(f"  • {point}")
```

#### 错误诊断

```python
error = """
Traceback (most recent call last):
  File "main.py", line 15, in <module>
    result = solve_equation(0, 1, 1)
  File "main.py", line 8, in solve_equation
    x = -b / (2*a)
ZeroDivisionError: division by zero
"""

diagnosis = sdk.diagnose_error(
    error=error,
    code=code
)

print("诊断结果:")
print(diagnosis['diagnosis'])

print("\n建议:")
for suggestion in diagnosis['suggestions']:
    print(f"  • {suggestion}")
```

#### 知识问答

```python
answer = sdk.ask_question(
    question="什么是有限差分法？",
    context={
        "book": "water-environment-simulation",
        "case": "case_01_diffusion"
    }
)

print("回答:")
print(answer['answer'])

if 'references' in answer:
    print("\n参考资料:")
    for ref in answer['references']:
        print(f"  • {ref}")
```

#### 结果分析

```python
results = {
    "max_concentration": 0.85,
    "diffusion_distance": 12.5,
    "computation_time": 3.2,
    "grid_points": 100
}

insights = sdk.generate_insights(results)

print("分析:")
print(insights['summary'])

print("\n关键发现:")
for finding in insights['key_findings']:
    print(f"  • {finding}")

if 'recommendations' in insights:
    print("\n建议:")
    for rec in insights['recommendations']:
        print(f"  • {rec}")
```

---

## 常见问题

### Q1: 会话超时了怎么办？

**A**: 有两种方法：

1. **提前延长会话**（推荐）
   ```python
   sdk.extend_session(session_id, hours=4)
   ```

2. **创建新会话并恢复进度**
   ```python
   # 创建新会话
   new_session = sdk.create_session(...)
   
   # 加载之前的代码修改
   # （系统会自动恢复文件版本）
   ```

### Q2: 代码执行失败怎么办？

**A**: 按以下步骤排查：

1. **查看错误信息**
   ```python
   status = sdk.get_execution(execution_id)
   print(status['error'])
   ```

2. **使用AI诊断**
   ```python
   diagnosis = sdk.diagnose_error(
       error=status['error'],
       code=your_code
   )
   ```

3. **检查代码语法**
   ```python
   result = sdk.validate_code(your_code)
   ```

### Q3: 如何查看历史会话？

**A**: 使用list_sessions方法：

```python
sessions = sdk.list_sessions("your_user_id")

for session in sessions:
    print(f"会话: {session['session_id']}")
    print(f"案例: {session['case_slug']}")
    print(f"状态: {session['status']}")
    print(f"创建时间: {session['created_at']}")
    print()
```

### Q4: 可以同时运行多个会话吗？

**A**: 可以！每个会话都是独立的，您可以：
- 在不同的书籍/案例中同时学习
- 同时运行多个实验
- 对比不同参数的结果

### Q5: 如何导出结果？

**A**: 执行结果会自动保存，您可以：

1. **下载图表**
   ```python
   # 图表文件保存在results目录
   import shutil
   shutil.copy(
       f"/results/{execution_id}/plot.png",
       "/your/path/plot.png"
   )
   ```

2. **导出数据**
   ```python
   import json
   
   status = sdk.get_execution(execution_id)
   with open('results.json', 'w') as f:
       json.dump(status['results'], f, indent=2)
   ```

### Q6: AI助手的回答不够准确怎么办？

**A**: 尝试以下方法提高准确性：

1. **提供更多上下文**
   ```python
   answer = sdk.ask_question(
       question="为什么结果不收敛？",
       context={
           "book": "water-environment-simulation",
           "case": "case_01_diffusion",
           "code": your_code,
           "results": your_results,
           "parameters": your_parameters
       }
   )
   ```

2. **细化问题**
   - ❌ 不好: "这个代码有问题吗？"
   - ✅ 更好: "为什么时间步长设为0.01时计算不稳定？"

---

## 技巧与最佳实践

### 技巧1: 使用上下文管理器

```python
from platform_sdk import PlatformSDK, SessionContext

sdk = PlatformSDK()

# 自动管理会话生命周期
with SessionContext(sdk, "user_001", "book", "case") as ctx:
    # 执行操作
    execution = ctx.execute('main.py')
    
    # 等待完成
    # ...

# 会话自动终止，资源自动清理
```

### 技巧2: 批量执行实验

```python
# 对比不同参数的效果
parameters_list = [
    {"D": 0.1, "nx": 50},
    {"D": 0.2, "nx": 50},
    {"D": 0.1, "nx": 100},
    {"D": 0.2, "nx": 100},
]

results = []

for params in parameters_list:
    execution = sdk.start_execution(
        session_id=session_id,
        script_path='main.py',
        parameters=params
    )
    
    # 等待完成...
    status = wait_for_completion(execution['execution_id'])
    
    results.append({
        'parameters': params,
        'results': status['results']
    })

# 对比分析
analyze_results(results)
```

### 技巧3: 渐进式代码修改

```python
# 1. 加载原始代码
code = sdk.load_code("book", "case")
original_code = code['files'][0]['content']

# 2. 小步修改并测试
modifications = [
    ("修改1: 增加输入验证", modify_1),
    ("修改2: 优化算法", modify_2),
    ("修改3: 添加可视化", modify_3),
]

for desc, modify_func in modifications:
    print(f"\n{desc}")
    
    # 应用修改
    new_code = modify_func(original_code)
    sdk.edit_file(session_id, 'main.py', new_code)
    
    # 执行测试
    execution = sdk.start_execution(session_id, 'main.py')
    
    # 查看结果
    # ...
    
    # 如果成功，保存为基准
    if is_successful(execution):
        original_code = new_code
    else:
        print("  修改失败，回滚")
```

### 技巧4: 利用AI助手学习

```python
# 学习流程
def learning_workflow(sdk, session_id, code):
    # 1. 先理解整体
    overview = sdk.explain_code(code, "整体概览")
    print("整体理解:", overview['explanation'])
    
    # 2. 逐个函数深入
    functions = extract_functions(code)
    for func in functions:
        detail = sdk.explain_code(func, f"详细讲解: {func['name']}")
        print(f"\n{func['name']}:", detail['explanation'])
    
    # 3. 提出问题
    questions = [
        "这个算法的时间复杂度是多少？",
        "为什么使用这种数据结构？",
        "有哪些优化空间？"
    ]
    
    for q in questions:
        answer = sdk.ask_question(q, {"code": code})
        print(f"\nQ: {q}")
        print(f"A: {answer['answer']}")
```

### 技巧5: 性能优化工作流

```python
def optimization_workflow(sdk, session_id, code):
    # 1. 基准测试
    baseline = run_execution(sdk, session_id, code)
    baseline_time = baseline['results']['computation_time']
    
    print(f"基准性能: {baseline_time}s")
    
    # 2. 询问AI优化建议
    suggestions = sdk.ask_question(
        "如何优化这段代码的性能？",
        {"code": code, "baseline_time": baseline_time}
    )
    
    print("\n优化建议:")
    for sug in suggestions['suggestions']:
        print(f"  • {sug}")
    
    # 3. 逐个尝试优化
    for i, optimization in enumerate(suggestions['suggestions'], 1):
        print(f"\n尝试优化 {i}: {optimization}")
        
        # 应用优化
        optimized_code = apply_optimization(code, optimization)
        
        # 测试性能
        result = run_execution(sdk, session_id, optimized_code)
        new_time = result['results']['computation_time']
        
        improvement = (baseline_time - new_time) / baseline_time * 100
        print(f"  性能提升: {improvement:.1f}%")
        
        if improvement > 0:
            code = optimized_code
            baseline_time = new_time
    
    return code
```

---

## 获取帮助

### 文档

- **快速开始**: [QUICK_START.md](QUICK_START.md)
- **API文档**: http://localhost:8000/docs
- **工具文档**: [TOOLS_DOCUMENTATION.md](TOOLS_DOCUMENTATION.md)

### 命令行帮助

```bash
# 查看所有命令
./manage.py --help

# 查看系统信息
./manage.py info

# 健康检查
python3 health_check.py
```

### 反馈与建议

如有问题或建议，请：
1. 查看本手册的常见问题部分
2. 阅读工具文档
3. 运行健康检查诊断系统

---

**版本**: V2.0.0  
**更新日期**: 2025-11-04  
**祝您学习愉快！** 🎓
