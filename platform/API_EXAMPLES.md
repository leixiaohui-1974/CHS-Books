# 📖 API使用示例

**版本:** v1.0.0  
**基础URL:** `http://localhost:8000/api/v1`

---

## 🔐 认证

### 注册用户

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user123",
    "password": "SecurePass123",
    "full_name": "张三"
  }'
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user123",
    "full_name": "张三",
    "role": "user"
  }
}
```

### 登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123"
```

### 获取当前用户信息

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📚 书籍管理

### 获取书籍列表

```bash
# 基础查询
curl -X GET "http://localhost:8000/api/v1/books"

# 带分页
curl -X GET "http://localhost:8000/api/v1/books?page=1&page_size=10"

# 按难度筛选
curl -X GET "http://localhost:8000/api/v1/books?difficulty=beginner"

# 按状态筛选
curl -X GET "http://localhost:8000/api/v1/books?status=published"

# 搜索
curl -X GET "http://localhost:8000/api/v1/books?search=水系统"
```

**响应:**
```json
{
  "total": 3,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 1,
      "slug": "water-system-control",
      "title": "水系统控制论",
      "subtitle": "基于水箱案例的控制理论入门",
      "cover_image": "/covers/book1.jpg",
      "difficulty": "beginner",
      "price": 299.0,
      "is_free": false,
      "total_chapters": 6,
      "total_cases": 24,
      "enrollments": 1523,
      "avg_rating": 4.8
    }
  ]
}
```

### 获取书籍详情

```bash
# 通过ID
curl -X GET "http://localhost:8000/api/v1/books/1"

# 通过slug
curl -X GET "http://localhost:8000/api/v1/books/water-system-control"
```

**响应:**
```json
{
  "id": 1,
  "slug": "water-system-control",
  "title": "水系统控制论",
  "subtitle": "基于水箱案例的控制理论入门",
  "description": "通过12个经典水箱案例系统讲解控制理论...",
  "cover_image": "/covers/book1.jpg",
  "authors": ["张教授", "李工程师"],
  "version": "1.0.0",
  "status": "published",
  "difficulty": "beginner",
  "is_free": false,
  "price": 299.0,
  "original_price": 399.0,
  "total_chapters": 6,
  "total_cases": 24,
  "estimated_hours": 192,
  "enrollments": 1523,
  "avg_rating": 4.8,
  "tags": ["控制理论", "水利工程"]
}
```

### 获取书籍章节

```bash
curl -X GET "http://localhost:8000/api/v1/books/1/chapters"
```

**响应:**
```json
{
  "book_id": 1,
  "total_chapters": 2,
  "chapters": [
    {
      "id": 1,
      "order": 1,
      "title": "第1章：控制系统基础",
      "slug": "chapter-01",
      "is_free": true,
      "estimated_minutes": 120,
      "cases": [
        {
          "id": 1,
          "order": 1,
          "title": "案例1：家庭水塔自动供水系统",
          "slug": "case-01-water-tower",
          "difficulty": "beginner",
          "estimated_minutes": 90,
          "has_tool": true
        }
      ]
    }
  ]
}
```

---

## 📊 学习进度

### 注册学习（报名课程）

```bash
curl -X POST "http://localhost:8000/api/v1/progress/enroll/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应:**
```json
{
  "message": "注册学习成功",
  "progress_id": 1,
  "book_id": 1
}
```

### 获取我的学习进度

```bash
curl -X GET "http://localhost:8000/api/v1/progress/my-progress" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应:**
```json
{
  "total": 2,
  "items": [
    {
      "id": 1,
      "book_id": 1,
      "book_title": "水系统控制论",
      "enrollment_date": "2025-10-31T10:00:00",
      "last_accessed": "2025-10-31T15:30:00",
      "progress_percentage": 45.5,
      "completed_cases": 11,
      "total_cases": 24,
      "total_time_spent": 1200
    }
  ]
}
```

### 更新案例进度

```bash
curl -X POST "http://localhost:8000/api/v1/progress/cases/1/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "score": 95.5,
    "time_spent": 90
  }'
```

### 获取学习仪表盘

```bash
curl -X GET "http://localhost:8000/api/v1/progress/dashboard" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应:**
```json
{
  "user_info": {
    "username": "user123",
    "level": 5,
    "total_points": 1250,
    "streak_days": 7
  },
  "statistics": {
    "enrolled_courses": 3,
    "completed_courses": 1,
    "total_learning_hours": 42.5,
    "completed_cases": 35,
    "average_score": 87.3
  },
  "enrolled_courses": [...]
}
```

---

## 🛠️ 工具执行

### 提交工具执行任务

```bash
curl -X POST "http://localhost:8000/api/v1/tools/execute" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": 1,
    "input_params": {
      "tank_height": 10.0,
      "flow_rate": 2.5,
      "initial_level": 3.0
    }
  }'
```

**响应:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "工具执行已提交，请稍后查询结果"
}
```

### 查询执行结果

```bash
curl -X GET "http://localhost:8000/api/v1/tools/result/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应（进行中）:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "任务执行中...",
  "result": null
}
```

**响应（完成）:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "执行成功",
  "result": {
    "status": "success",
    "output": {
      "equilibrium_time": 45.2,
      "final_level": 8.5,
      "flow_chart_data": [...]
    },
    "execution_time": 2.3,
    "created_at": "2025-10-31T15:45:00"
  }
}
```

---

## 🔍 高级查询示例

### Python requests库

```python
import requests

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_access_token_here"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. 获取书籍列表
response = requests.get(f"{BASE_URL}/books", params={
    "page": 1,
    "page_size": 10,
    "difficulty": "beginner"
})
books = response.json()

# 2. 报名课程
book_id = books["items"][0]["id"]
response = requests.post(
    f"{BASE_URL}/progress/enroll/{book_id}",
    headers=headers
)

# 3. 执行工具
response = requests.post(
    f"{BASE_URL}/tools/execute",
    headers=headers,
    json={
        "case_id": 1,
        "input_params": {
            "tank_height": 10.0,
            "flow_rate": 2.5
        }
    }
)
task_id = response.json()["task_id"]

# 4. 查询结果
import time
while True:
    response = requests.get(
        f"{BASE_URL}/tools/result/{task_id}",
        headers=headers
    )
    result = response.json()
    if result["status"] in ["completed", "failed"]:
        break
    time.sleep(1)

print(result)
```

### JavaScript/TypeScript

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your_access_token_here';

// 配置axios
import axios from 'axios';
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${TOKEN}`
  }
});

// 1. 获取书籍列表
const books = await api.get('/books', {
  params: { page: 1, page_size: 10 }
});

// 2. 获取书籍详情
const book = await api.get(`/books/${books.data.items[0].slug}`);

// 3. 报名课程
await api.post(`/progress/enroll/${book.data.id}`);

// 4. 执行工具
const execution = await api.post('/tools/execute', {
  case_id: 1,
  input_params: {
    tank_height: 10.0,
    flow_rate: 2.5
  }
});

// 5. 轮询结果
const taskId = execution.data.task_id;
let result;
do {
  await new Promise(resolve => setTimeout(resolve, 1000));
  const response = await api.get(`/tools/result/${taskId}`);
  result = response.data;
} while (result.status === 'running');

console.log(result);
```

---

## 🔒 认证流程完整示例

```bash
#!/bin/bash

# 1. 注册
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123456",
    "full_name": "测试用户"
  }')

# 2. 提取token
TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

# 3. 获取用户信息
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 4. 获取书籍列表
curl -X GET "http://localhost:8000/api/v1/books" \
  -H "Authorization: Bearer $TOKEN"

# 5. 报名课程
curl -X POST "http://localhost:8000/api/v1/progress/enroll/1" \
  -H "Authorization: Bearer $TOKEN"

# 6. 查看进度
curl -X GET "http://localhost:8000/api/v1/progress/my-progress" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 完整学习流程示例

```python
#!/usr/bin/env python3
"""
完整学习流程示例
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

class LearningClient:
    def __init__(self):
        self.token = None
        self.headers = {}
    
    def register(self, email, username, password):
        """注册用户"""
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "username": username,
            "password": password,
            "full_name": "学习者"
        })
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print(f"✅ 注册成功: {username}")
        return data
    
    def get_books(self):
        """获取书籍列表"""
        response = requests.get(f"{BASE_URL}/books")
        books = response.json()
        print(f"📚 找到 {books['total']} 本书籍")
        return books["items"]
    
    def enroll_book(self, book_id):
        """报名课程"""
        response = requests.post(
            f"{BASE_URL}/progress/enroll/{book_id}",
            headers=self.headers
        )
        print(f"✅ 报名成功: Book ID {book_id}")
        return response.json()
    
    def get_chapters(self, book_id):
        """获取章节"""
        response = requests.get(f"{BASE_URL}/books/{book_id}/chapters")
        chapters = response.json()
        print(f"📖 找到 {chapters['total_chapters']} 个章节")
        return chapters["chapters"]
    
    def execute_tool(self, case_id, params):
        """执行工具"""
        response = requests.post(
            f"{BASE_URL}/tools/execute",
            headers=self.headers,
            json={"case_id": case_id, "input_params": params}
        )
        task_id = response.json()["task_id"]
        print(f"🔧 工具执行中: {task_id}")
        
        # 等待结果
        while True:
            response = requests.get(
                f"{BASE_URL}/tools/result/{task_id}",
                headers=self.headers
            )
            result = response.json()
            if result["status"] in ["completed", "failed"]:
                break
            time.sleep(1)
        
        print(f"✅ 执行完成")
        return result
    
    def update_progress(self, case_id, score):
        """更新进度"""
        response = requests.post(
            f"{BASE_URL}/progress/cases/{case_id}/update",
            headers=self.headers,
            json={
                "status": "completed",
                "score": score,
                "time_spent": 90
            }
        )
        print(f"📊 进度已更新: 得分 {score}")
        return response.json()
    
    def get_dashboard(self):
        """获取仪表盘"""
        response = requests.get(
            f"{BASE_URL}/progress/dashboard",
            headers=self.headers
        )
        return response.json()


# 使用示例
if __name__ == "__main__":
    client = LearningClient()
    
    # 1. 注册
    client.register("student@example.com", "student", "Pass123")
    
    # 2. 浏览课程
    books = client.get_books()
    first_book = books[0]
    
    # 3. 报名课程
    client.enroll_book(first_book["id"])
    
    # 4. 查看章节
    chapters = client.get_chapters(first_book["id"])
    
    # 5. 学习第一个案例
    if chapters and chapters[0]["cases"]:
        first_case = chapters[0]["cases"][0]
        
        # 执行工具
        result = client.execute_tool(first_case["id"], {
            "tank_height": 10.0,
            "flow_rate": 2.5
        })
        
        # 更新进度
        client.update_progress(first_case["id"], 95.0)
    
    # 6. 查看学习仪表盘
    dashboard = client.get_dashboard()
    print("\n📊 学习统计:")
    print(f"  已报名课程: {dashboard['statistics']['enrolled_courses']}")
    print(f"  完成案例: {dashboard['statistics']['completed_cases']}")
    print(f"  平均得分: {dashboard['statistics']['average_score']}")
```

---

## 🔗 相关文档

- [API完整文档](http://localhost:8000/docs)
- [ReDoc文档](http://localhost:8000/redoc)
- [README](README_CN.md)
- [部署指南](DEPLOYMENT_CHECKLIST.md)

---

**文档版本:** v1.0.0  
**最后更新:** 2025-10-31
