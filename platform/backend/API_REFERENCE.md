# API文档

**生成时间**: 2025-11-04 07:45:01

**基础URL**: http://localhost:8000

---

## Sessions 模块

### POST /api/v2/sessions/create

创建学习会话

**请求体**:

```json

{
  "user_id": "user_001",
  "book_slug": "water-environment-simulation",
  "case_slug": "case_01_diffusion"
}

```

**响应体**:

```json

{
  "session_id": "session_20251104_120000",
  "user_id": "user_001",
  "status": "active",
  "created_at": "2025-11-04T12:00:00Z"
}

```

---

### GET /api/v2/sessions/{session_id}

获取会话信息

**响应体**:

```json

{
  "session_id": "session_20251104_120000",
  "status": "active",
  "files": []
}

```

---

### POST /api/v2/sessions/{session_id}/pause

暂停会话

---

### POST /api/v2/sessions/{session_id}/resume

恢复会话

---

## Code 模块

### POST /api/v2/code/load

加载案例代码

**请求体**:

```json

{
  "book_slug": "water-environment-simulation",
  "case_slug": "case_01_diffusion"
}

```

**响应体**:

```json

{
  "main_file": "main.py",
  "files": [
    {
      "name": "main.py",
      "content": "...",
      "analysis": {}
    }
  ]
}

```

---

### POST /api/v2/code/analyze

分析代码结构

**请求体**:

```json

{
  "code": "def test(): pass"
}

```

**响应体**:

```json

{
  "functions": 1,
  "classes": 0,
  "imports": []
}

```

---

## Execution 模块

### POST /api/v2/execution/start

启动代码执行

**请求体**:

```json

{
  "session_id": "session_123",
  "script_path": "main.py",
  "parameters": {}
}

```

**响应体**:

```json

{
  "execution_id": "exec_456",
  "status": "running"
}

```

---

## Ai 模块

### POST /api/v2/ai/explain-code

AI代码讲解

**请求体**:

```json

{
  "code": "def add(a, b): return a + b",
  "context": "加法函数"
}

```

**响应体**:

```json

{
  "explanation": "这是一个简单的加法函数...",
  "key_points": [
    "使用def定义函数",
    "返回两数之和"
  ]
}

```

---
