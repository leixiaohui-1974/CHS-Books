# API使用示例

## 📋 概述

本文档提供智能知识平台V2.0的API使用示例。

---

## 🔑 认证

所有API请求需要在Header中包含JWT Token：

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 1️⃣ 会话管理

### 创建学习会话

```bash
curl -X POST "http://localhost:8000/api/v1/sessions/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "book_slug": "water-environment-simulation",
    "chapter_slug": "chapter_01",
    "case_slug": "case_01_diffusion"
  }'
```

**响应示例**:
```json
{
  "session_id": "sess_abc123def456",
  "user_id": 1,
  "book_slug": "water-environment-simulation",
  "case_slug": "case_01_diffusion",
  "status": "active",
  "execution_count": 0,
  "created_at": "2025-11-03T10:00:00",
  "expires_at": "2025-11-04T10:00:00",
  "is_active": true,
  "resource_quota": {
    "max_executions": 100,
    "remaining_executions": 100,
    "max_cpu_time": 3600,
    "max_memory": "2GB"
  }
}
```

### 获取会话详情

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/{session_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 列出用户的所有会话

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 延长会话有效期

```bash
curl -X PUT "http://localhost:8000/api/v1/sessions/{session_id}/extend?hours=48" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 2️⃣ 代码管理

### 加载案例代码

```bash
curl -X POST "http://localhost:8000/api/v1/code/load" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123def456",
    "case_path": "/workspace/books/water-environment-simulation/code/examples/case_01_diffusion"
  }'
```

**响应示例**:
```json
{
  "message": "代码加载成功",
  "file_count": 5,
  "file_tree": [
    {
      "name": "main.py",
      "path": "main.py",
      "type": "file",
      "size": 8192
    },
    {
      "name": "models",
      "path": "models",
      "type": "folder",
      "children": [...]
    }
  ],
  "dependencies": ["numpy", "matplotlib", "scipy"]
}
```

### 获取文件内容

```bash
curl -X GET "http://localhost:8000/api/v1/code/{session_id}/file/main.py" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 编辑文件

```bash
curl -X PUT "http://localhost:8000/api/v1/code/{session_id}/edit" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123def456",
    "file_path": "main.py",
    "content": "# 修改后的代码\nimport numpy as np\n..."
  }'
```

### 查看文件修改差异

```bash
curl -X GET "http://localhost:8000/api/v1/code/{session_id}/diff/main.py" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "has_changes": true,
  "diff_unified": "--- main.py (原始)\n+++ main.py (修改后)\n@@ -10,7 +10,7 @@\n-    L = 10.0\n+    L = 20.0\n",
  "stats": {
    "additions": 1,
    "deletions": 1,
    "changes": 2
  }
}
```

### 验证代码语法

```bash
curl -X POST "http://localhost:8000/api/v1/code/validate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello World\")"
  }'
```

---

## 3️⃣ 代码执行

### 启动执行

```bash
curl -X POST "http://localhost:8000/api/v1/execution/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123def456",
    "script_path": "main.py",
    "input_params": {
      "L": 10.0,
      "T": 100.0,
      "nx": 100,
      "nt": 1000
    },
    "dependencies": ["numpy", "matplotlib", "scipy"]
  }'
```

**响应示例**:
```json
{
  "execution_id": "exec_xyz789abc012",
  "status": "pending",
  "message": "执行已开始，请通过WebSocket接收实时输出",
  "ws_url": "/api/v1/execution/ws/exec_xyz789abc012"
}
```

### WebSocket连接（JavaScript）

```javascript
const executionId = "exec_xyz789abc012";
const ws = new WebSocket(`ws://localhost:8000/api/v1/execution/ws/${executionId}`);

ws.onopen = () => {
  console.log('✅ WebSocket连接成功');
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  switch(msg.type) {
    case 'status':
      console.log('状态更新:', msg.data.status);
      break;
    
    case 'output':
      console.log('输出:', msg.data.text);
      document.getElementById('console').appendChild(
        document.createTextNode(msg.data.text)
      );
      break;
    
    case 'completed':
      console.log('✅ 执行完成');
      console.log('执行时间:', msg.data.execution_time);
      console.log('结果文件:', msg.data.result_files);
      break;
    
    case 'failed':
      console.error('❌ 执行失败:', msg.data.error);
      break;
    
    case 'timeout':
      console.error('⏱️  执行超时');
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket错误:', error);
};

ws.onclose = () => {
  console.log('WebSocket连接关闭');
};
```

### 获取执行状态

```bash
curl -X GET "http://localhost:8000/api/v1/execution/{execution_id}/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取执行结果

```bash
curl -X GET "http://localhost:8000/api/v1/execution/{execution_id}/result" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "execution_id": "exec_xyz789abc012",
  "session_id": "sess_abc123def456",
  "status": "completed",
  "execution_time": 12,
  "console_output": "案例1：污染物在静水中的扩散\n...",
  "result_files": [
    {
      "type": "plot",
      "name": "diffusion_evolution.png",
      "path": "/results/exec_xyz/diffusion_evolution.png",
      "size": 245678
    },
    {
      "type": "table",
      "name": "error_analysis.csv",
      "path": "/results/exec_xyz/error_analysis.csv",
      "size": 1234
    }
  ],
  "resource_usage": {
    "cpu_time": 10,
    "memory_peak": "256MB"
  }
}
```

---

## 4️⃣ AI助手

### 代码讲解

```bash
curl -X POST "http://localhost:8000/api/v1/ai/explain-code" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "C_new[i] = C[i] + Fo * (C[i+1] - 2*C[i] + C[i-1])",
    "context": "这是显式有限差分法求解扩散方程"
  }'
```

**响应示例**:
```json
{
  "explanation": "## 代码功能说明\n\n这段代码实现了显式有限差分法（FTCS）求解一维扩散方程...",
  "model": "gpt-4-demo"
}
```

### 错误诊断

```bash
curl -X POST "http://localhost:8000/api/v1/ai/diagnose-error" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(undefined_variable)",
    "error_message": "NameError: name undefined_variable is not defined"
  }'
```

**响应示例**:
```json
{
  "diagnosis": "变量未定义错误",
  "suggestions": [
    "检查变量名拼写",
    "确保变量在使用前已定义",
    "检查变量作用域"
  ],
  "fixed_code": null
}
```

### 智能问答

```bash
curl -X POST "http://localhost:8000/api/v1/ai/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123def456",
    "question": "为什么Crank-Nicolson格式比显式格式精度高？",
    "context": {
      "case": "扩散方程求解",
      "topic": "数值格式"
    }
  }'
```

**响应示例**:
```json
{
  "answer": "感谢您的提问！关于Crank-Nicolson格式的精度优势...\n\n1. **时间离散精度**...",
  "session_id": "sess_abc123def456"
}
```

### 生成结果洞察

```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-insights" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "result_data": {
      "plots": [{"name": "plot1"}, {"name": "plot2"}],
      "metrics": [
        {"name": "L2误差", "value": 0.000123},
        {"name": "计算时间", "value": 10.5}
      ],
      "tables": [{"row_count": 100, "col_count": 5}]
    }
  }'
```

**响应示例**:
```json
{
  "insights": [
    "✅ 成功生成 2 个图表，可视化效果良好",
    "📊 L2误差 = 0.0001 - 精度优秀",
    "📊 计算时间 = 10.5000 s - 性能良好",
    "📋 数据表包含 100 行 × 5 列",
    "💡 可以尝试调整参数观察结果变化",
    "💡 建议与理论解对比验证精度"
  ],
  "count": 6
}
```

---

## 5️⃣ 完整工作流示例

### Python客户端示例

```python
import requests
import websocket
import json
import threading

class LearningPlatformClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_session(self, book_slug, case_slug):
        """创建学习会话"""
        url = f"{self.base_url}/sessions/create"
        data = {
            "book_slug": book_slug,
            "case_slug": case_slug
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def load_code(self, session_id, case_path):
        """加载代码"""
        url = f"{self.base_url}/code/load"
        data = {
            "session_id": session_id,
            "case_path": case_path
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def execute_code(self, session_id, script_path, params):
        """执行代码"""
        url = f"{self.base_url}/execution/start"
        data = {
            "session_id": session_id,
            "script_path": script_path,
            "input_params": params
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def monitor_execution(self, execution_id, on_output=None, on_complete=None):
        """监控执行（WebSocket）"""
        ws_url = f"ws://localhost:8000/api/v1/execution/ws/{execution_id}"
        
        def on_message(ws, message):
            msg = json.loads(message)
            
            if msg['type'] == 'output' and on_output:
                on_output(msg['data']['text'])
            elif msg['type'] == 'completed' and on_complete:
                on_complete(msg['data'])
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message
        )
        
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        return ws

# 使用示例
client = LearningPlatformClient(
    base_url="http://localhost:8000/api/v1",
    token="YOUR_JWT_TOKEN"
)

# 1. 创建会话
session = client.create_session(
    book_slug="water-environment-simulation",
    case_slug="case_01_diffusion"
)
session_id = session['session_id']
print(f"✅ 会话创建成功: {session_id}")

# 2. 加载代码
code_result = client.load_code(
    session_id=session_id,
    case_path="/workspace/books/water-environment-simulation/code/examples/case_01_diffusion"
)
print(f"✅ 代码加载成功: {code_result['file_count']} 个文件")

# 3. 执行代码
execution = client.execute_code(
    session_id=session_id,
    script_path="main.py",
    params={"L": 10.0, "T": 100.0, "nx": 100, "nt": 1000}
)
execution_id = execution['execution_id']
print(f"✅ 执行已启动: {execution_id}")

# 4. 监控执行
def on_output(text):
    print(f"[输出] {text}", end='')

def on_complete(data):
    print(f"\n✅ 执行完成！耗时: {data['execution_time']}秒")
    print(f"结果文件: {len(data['result_files'])} 个")

ws = client.monitor_execution(
    execution_id=execution_id,
    on_output=on_output,
    on_complete=on_complete
)

# 保持运行
import time
time.sleep(60)
```

---

## 📊 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token无效） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 🔗 相关文档

- [开发总结](DEVELOPMENT_SUMMARY_V2.0.md)
- [增强方案](智能知识平台增强方案-V2.0.md)
- [API文档](http://localhost:8000/docs)

---

**更新时间**: 2025-11-03  
**版本**: V2.0
