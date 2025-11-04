# 智能知识平台 V2.2 - 完整教程

**版本**: V2.2.0  
**更新日期**: 2025-11-04

---

## 📚 目录

1. [第一章：平台概述](#第一章平台概述)
2. [第二章：环境搭建](#第二章环境搭建)
3. [第三章：基础使用](#第三章基础使用)
4. [第四章：进阶功能](#第四章进阶功能)
5. [第五章：SDK开发](#第五章sdk开发)
6. [第六章：运维管理](#第六章运维管理)
7. [第七章：故障排查](#第七章故障排查)
8. [第八章：最佳实践](#第八章最佳实践)

---

## 第一章：平台概述

### 1.1 什么是智能知识平台？

智能知识平台是一个为水利工程教材设计的在线学习和代码执行环境。它集成了：

- 📚 **知识管理** - 管理多本教材和案例
- 💻 **代码执行** - 在线运行Python脚本
- 🤖 **AI助手** - 智能讲解和问答
- 📊 **结果展示** - 标准化可视化
- 🔧 **开发工具** - 完整的工具链

### 1.2 核心特性

- ✅ 零配置环境 - 无需安装Python、依赖包
- ✅ 实时执行 - WebSocket实时反馈
- ✅ 智能辅助 - AI代码讲解和错误诊断
- ✅ 安全隔离 - Docker容器沙箱
- ✅ 会话管理 - 支持暂停、恢复、历史记录

### 1.3 技术架构

```
前端 (React + TypeScript)
    ↓ HTTP/WebSocket
后端 (FastAPI + Python)
    ↓
执行引擎 (Docker容器池)
    ↓
数据存储 (PostgreSQL + Redis + MongoDB)
```

---

## 第二章：环境搭建

### 2.1 系统要求

**最低配置**:
- CPU: 2核
- 内存: 4GB
- 磁盘: 20GB
- 操作系统: Linux/macOS/Windows

**推荐配置**:
- CPU: 4核+
- 内存: 8GB+
- 磁盘: 50GB+

### 2.2 安装Docker

#### Linux

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### macOS

下载并安装 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

#### Windows

下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### 2.3 安装Python依赖

```bash
cd /workspace/platform/backend
pip install -r requirements.txt
```

### 2.4 配置平台

使用配置向导：

```bash
python3 setup_wizard.py
```

按提示完成配置：
1. 数据库配置
2. Redis配置
3. AI服务密钥
4. 安全密钥

---

## 第三章：基础使用

### 3.1 启动平台

#### 方法1：自动部署（推荐）

```bash
python3 deploy.py
```

#### 方法2：手动启动

```bash
cd backend
./manage.py server start --reload
```

### 3.2 访问平台

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 3.3 第一个学习会话

#### 使用SDK

```python
from sdk.python.platform_sdk import PlatformSDK

# 初始化
sdk = PlatformSDK()

# 创建会话
session = sdk.create_session(
    user_id="student_001",
    book_slug="water-environment-simulation",
    case_slug="case_01_diffusion"
)

print(f"会话已创建: {session['session_id']}")

# 加载代码
code = sdk.load_code(
    book_slug="water-environment-simulation",
    case_slug="case_01_diffusion"
)

print(f"加载了 {len(code['files'])} 个文件")

# 执行代码
execution = sdk.start_execution(
    session_id=session['session_id'],
    script_path='main.py'
)

print(f"执行ID: {execution['execution_id']}")
```

#### 使用API

```bash
# 创建会话
curl -X POST "http://localhost:8000/api/v2/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student_001",
    "book_slug": "water-environment-simulation",
    "case_slug": "case_01_diffusion"
  }'
```

---

## 第四章：进阶功能

### 4.1 代码智能分析

```python
# 分析代码结构
code = """
import numpy as np

def calculate_flow(Q, A):
    v = Q / A
    return v
"""

analysis = sdk.analyze_code(code)

print(f"函数: {analysis['functions']}")
print(f"导入: {analysis['imports']}")
print(f"依赖: {analysis['dependencies']}")
```

### 4.2 代码验证和格式化

```python
# 验证语法
result = sdk.validate_code(code)

if not result['is_valid']:
    print("语法错误:")
    for error in result['errors']:
        print(f"  - {error}")

# 格式化代码
formatted = sdk.format_code(code)
print(formatted['formatted_code'])
```

### 4.3 实时执行监控

```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    
    if data['type'] == 'output':
        print(f"输出: {data['data']}")
    elif data['type'] == 'status':
        print(f"状态: {data['status']}")
        if data['status'] in ['completed', 'failed']:
            ws.close()

execution_id = "exec_123"
ws = websocket.WebSocketApp(
    f"ws://localhost:8000/api/v2/execution/ws/{execution_id}",
    on_message=on_message
)

ws.run_forever()
```

### 4.4 AI代码讲解

```python
# 请求AI讲解
explanation = sdk.explain_code(
    code=code,
    context="流速计算函数"
)

print("讲解:")
print(explanation['explanation'])

print("\n关键点:")
for point in explanation['key_points']:
    print(f"  • {point}")

print("\n建议:")
for suggestion in explanation['suggestions']:
    print(f"  • {suggestion}")
```

### 4.5 错误诊断

```python
error = """
ZeroDivisionError: division by zero
  File "main.py", line 15, in calculate_flow
    v = Q / A
"""

diagnosis = sdk.diagnose_error(
    error=error,
    code=code
)

print("诊断:")
print(diagnosis['diagnosis'])

print("\n建议:")
for suggestion in diagnosis['suggestions']:
    print(f"  • {suggestion}")
```

---

## 第五章：SDK开发

### 5.1 SDK架构

```python
from platform_sdk import PlatformSDK

# SDK提供5大模块：
# 1. 会话管理
# 2. 代码管理
# 3. 执行管理
# 4. AI助手
# 5. 便捷方法
```

### 5.2 会话管理完整示例

```python
sdk = PlatformSDK()

# 创建会话
session = sdk.create_session("user", "book", "case")
session_id = session['session_id']

# 查询会话
info = sdk.get_session(session_id)
print(f"状态: {info['status']}")

# 暂停会话
sdk.pause_session(session_id)

# 恢复会话
sdk.resume_session(session_id)

# 延长会话
sdk.extend_session(session_id, hours=4)

# 获取用户所有会话
sessions = sdk.list_sessions("user")

# 终止会话
sdk.terminate_session(session_id)
```

### 5.3 使用上下文管理器

```python
from platform_sdk import SessionContext

sdk = PlatformSDK()

# 自动管理会话生命周期
with SessionContext(sdk, "user", "book", "case") as ctx:
    # 执行操作
    execution = ctx.execute('main.py')
    
    # 等待完成
    result = wait_for_result(execution['execution_id'])
    
    # 分析结果
    insights = sdk.generate_insights(result)

# 会话自动终止
```

### 5.4 批量实验

```python
# 对比不同参数的效果
experiments = [
    {"D": 0.1, "nx": 50},
    {"D": 0.2, "nx": 50},
    {"D": 0.1, "nx": 100},
    {"D": 0.2, "nx": 100},
]

results = []

for params in experiments:
    with SessionContext(sdk, "user", "book", "case") as ctx:
        # 修改参数
        sdk.edit_file(ctx.session_id, 'config.py', 
                     f"D = {params['D']}\nnx = {params['nx']}")
        
        # 执行
        execution = ctx.execute('main.py')
        
        # 等待结果
        result = wait_for_result(execution['execution_id'])
        
        results.append({
            'parameters': params,
            'results': result
        })

# 分析对比
compare_results(results)
```

---

## 第六章：运维管理

### 6.1 系统诊断

```bash
# 运行系统诊断
python3 system_diagnostics.py

# 输出示例：
# ✓ Python版本正常
# ✓ 磁盘空间充足
# ✓ 内存正常
# ✗ Docker未安装
# ⚠️ 缺少配置文件
```

### 6.2 健康检查

```bash
# 定期运行健康检查
python3 health_check.py

# 或使用cron定时任务
# */5 * * * * cd /workspace/platform/backend && python3 health_check.py
```

### 6.3 性能监控

```bash
# 实时监控仪表板
python3 monitor_dashboard.py

# 性能基准测试
python3 benchmark.py

# 性能追踪
python3 performance_monitor.py
```

### 6.4 日志分析

```bash
# 分析应用日志
python3 log_analyzer.py

# 分析特定日志文件
python3 log_analyzer.py --file /path/to/log

# 导出分析结果
# 自动生成 log_analysis_*.json
```

### 6.5 数据库迁移

```bash
# 创建迁移
python3 db_migrate.py create add_user_profile

# 查看迁移列表
python3 db_migrate.py list

# 执行升级
python3 db_migrate.py upgrade

# 回滚
python3 db_migrate.py downgrade --steps 1
```

### 6.6 容器管理

```bash
# 查看容器列表
python3 container_manager.py list

# 查看容器统计
python3 container_manager.py stats

# 查看日志
python3 container_manager.py logs --container backend

# 重启容器
python3 container_manager.py restart --container backend

# 清理停止的容器
python3 container_manager.py clean
```

### 6.7 代码质量检查

```bash
# 运行代码质量检查
python3 code_quality.py

# 使用manage.py
./manage.py lint check

# 格式化代码
./manage.py lint format
```

---

## 第七章：故障排查

### 7.1 常见问题

#### 问题1：服务启动失败

**症状**: 启动命令执行后服务无法访问

**诊断**:
```bash
python3 system_diagnostics.py
```

**常见原因**:
1. 端口被占用
   ```bash
   lsof -i :8000
   # 解决：停止占用进程或更换端口
   ```

2. Docker未运行
   ```bash
   sudo systemctl start docker
   ```

3. 缺少依赖
   ```bash
   pip install -r requirements.txt
   ```

#### 问题2：执行超时

**症状**: 代码执行长时间无响应

**诊断**:
```bash
# 查看容器资源使用
python3 container_manager.py usage

# 查看容器日志
python3 container_manager.py logs --container backend
```

**解决方案**:
1. 增加超时时间
2. 优化代码性能
3. 增加容器资源限制

#### 问题3：内存不足

**症状**: 系统变慢或崩溃

**诊断**:
```bash
python3 system_diagnostics.py
```

**解决方案**:
1. 清理不用的容器
   ```bash
   python3 container_manager.py clean
   docker system prune -a
   ```

2. 增加系统内存
3. 优化容器资源配置

### 7.2 日志查看

```bash
# 查看应用日志
python3 container_manager.py logs --container backend --lines 100

# 分析错误
python3 log_analyzer.py
```

### 7.3 性能诊断

```bash
# 运行性能测试
python3 benchmark.py

# 实时监控
python3 monitor_dashboard.py

# 查看资源使用
python3 container_manager.py usage
```

---

## 第八章：最佳实践

### 8.1 开发工作流

**日常开发**:
```bash
# 1. 启动服务
./manage.py server start --reload

# 2. 修改代码
# ... 编辑文件 ...

# 3. 测试
python3 simple_test.py

# 4. 代码质量检查
python3 code_quality.py

# 5. 提交前测试
python3 integration_test_suite.py
```

### 8.2 生产部署

**部署流程**:
```bash
# 1. 系统诊断
python3 system_diagnostics.py

# 2. 配置检查
python3 setup_wizard.py

# 3. 部署
python3 deploy.py

# 4. 健康检查
python3 health_check.py

# 5. 性能验证
python3 benchmark.py
```

### 8.3 监控和维护

**日常监控**:
```bash
# 每天
python3 health_check.py

# 每周
python3 log_analyzer.py
python3 code_quality.py

# 每月
python3 system_diagnostics.py
python3 integration_test_suite.py
```

### 8.4 性能优化

**优化清单**:
1. **容器池大小** - 根据并发调整
2. **缓存策略** - Redis缓存热点数据
3. **数据库索引** - 优化常用查询
4. **代码优化** - 使用性能分析工具
5. **资源限制** - 合理设置容器资源

### 8.5 安全建议

**安全清单**:
1. **定期更新** - 更新依赖包
2. **密钥管理** - 妥善保管API密钥
3. **访问控制** - 配置防火墙规则
4. **日志审计** - 定期查看日志
5. **备份恢复** - 定期备份数据

### 8.6 学习建议

**学习路径**:

1. **入门阶段** (1-2天)
   - 阅读QUICK_START.md
   - 运行quickstart_example.py
   - 熟悉基本操作

2. **熟练阶段** (3-5天)
   - 阅读USER_MANUAL.md
   - 尝试SDK开发
   - 运行示例代码

3. **精通阶段** (1-2周)
   - 阅读源码
   - 自定义功能
   - 性能优化

---

## 🎓 总结

本教程涵盖了从入门到精通的全过程：

- ✅ **第一章**: 了解平台概念和架构
- ✅ **第二章**: 搭建开发和运行环境
- ✅ **第三章**: 掌握基础使用方法
- ✅ **第四章**: 学习进阶功能
- ✅ **第五章**: 使用SDK进行开发
- ✅ **第六章**: 掌握运维管理技能
- ✅ **第七章**: 排查和解决问题
- ✅ **第八章**: 应用最佳实践

---

## 📖 延伸阅读

- **QUICK_START.md** - 5分钟快速开始
- **USER_MANUAL.md** - 完整用户手册
- **TOOLS_DOCUMENTATION.md** - 工具文档
- **API_USAGE_EXAMPLES.md** - API示例
- **V2.2_RELEASE_NOTES.md** - 版本说明

---

## 💡 获取帮助

遇到问题？

1. 查看文档
2. 运行诊断工具
3. 查看示例代码
4. 阅读API文档

---

**版本**: V2.2.0  
**更新**: 2025-11-04  
**祝您学习愉快！** 🚀
