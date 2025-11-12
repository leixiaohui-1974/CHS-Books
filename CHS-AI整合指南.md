# CHS-AI知识库整合完成指南

## ✅ 已完成的工作

### 1. 后端服务整合
- 位置: `platform/backend/services/knowledge/`
- 包含模块:
  - knowledge_manager.py - 知识管理
  - rag_service.py - RAG问答
  - hybrid_search.py - 混合检索
  - knowledge_graph.py - 知识图谱
  - knowledge_recommender.py - 智能推荐
  - optimized_search.py - 性能优化
  - vector_store.py - 向量存储
  - embeddings.py - 向量嵌入
  - cache_manager.py - 缓存管理

### 2. API路由集成
- 位置: `platform/backend/api/knowledge_routes.py`
- 端点: 11个RESTful API
- 功能: 搜索、问答、分类、推荐、图谱

### 3. 前端组件
- 位置: `platform/frontend/knowledge/`
- 包含:
  - index_enhanced.html - 增强版知识库界面
  - knowledge_graph_viz.html - 知识图谱可视化
- 组件: `platform/frontend/knowledge_component.html`

## 🚀 下一步操作

### 步骤1：安装依赖

```bash
cd platform/backend
pip install chromadb sentence-transformers fastapi[all]
```

### 步骤2：初始化知识库数据

```bash
# 方式A：从chs-ai复制数据库
cd E:/OneDrive/Documents/GitHub/Test/CHS-Books
cp E:/OneDrive/Documents/GitHub/CHS-SDK/products/chs-ai/knowledge.db ./data/

# 方式B：重新生成
cd platform/backend/services/knowledge
python -c "from knowledge_manager import knowledge_manager; knowledge_manager.init()"
```

### 步骤3：启动服务器

```bash
cd platform/backend
python full_server.py
```

访问: http://localhost:8000

### 步骤4：测试知识库API

```bash
# 测试健康检查
curl http://localhost:8000/api/v1/knowledge/health

# 测试搜索
curl -X POST http://localhost:8000/api/v1/knowledge/search \ 
  -H "Content-Type: application/json" \
  -d '{"query":"水力学","top_k":5,"mode":"hybrid"}'

# 测试问答
curl -X POST http://localhost:8000/api/v1/knowledge/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是水力学？","top_k":5}'
```

### 步骤5：集成到前端

在 `platform/frontend/unified.html` 中添加：

```html
<!-- 在导航栏添加知识库入口 -->
<nav>
  <button onclick="showKnowledgeLibrary()">知识库</button>
</nav>

<!-- 引入知识库组件 -->
<script src="/knowledge_component.html"></script>
```

## 🎯 功能验证清单

- [ ] 后端服务正常启动
- [ ] API健康检查通过
- [ ] 知识搜索功能正常
- [ ] RAG问答功能正常
- [ ] 知识图谱显示正常
- [ ] 智能推荐功能正常
- [ ] 前端组件显示正常
- [ ] 案例-知识关联正常

## 📚 API文档

启动服务器后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 配置说明

### 环境变量

可选的环境变量配置：

```bash
# 向量数据库路径
CHROMA_DB_PATH=./data/chroma_db

# 缓存设置
CACHE_SIZE=1000
CACHE_TTL=3600

# LLM设置（可选）
USE_REAL_LLM=false
OPENAI_API_KEY=your_key_here
```

### 配置文件

编辑 `platform/backend/services/knowledge/config.py`:

```python
# 知识库配置
KNOWLEDGE_CONFIG = {
    'vector_db_path': './data/chroma_db',
    'embedding_model': 'paraphrase-multilingual-MiniLM-L12-v2',
    'cache_size': 1000,
    'search_top_k': 5
}
```

## ⚠️ 注意事项

1. **依赖安装**: 确保安装了所有必需的Python包
2. **数据初始化**: 首次运行需要初始化知识库数据
3. **向量数据库**: ChromaDB需要约600MB磁盘空间
4. **性能优化**: 首次向量化需要几分钟时间
5. **缓存预热**: 建议预热常用查询的缓存

## 🐛 故障排除

### 问题1: 导入失败

**症状**: `ImportError: No module named 'knowledge_manager'`

**解决**:
```bash
pip install -r requirements.txt
# 或者手动安装缺失的包
```

### 问题2: 向量数据库错误

**症状**: `ChromaDB connection error`

**解决**:
```bash
# 重新初始化数据库
rm -rf ./data/chroma_db
python -c "from vector_store import vector_store; vector_store.init()"
```

### 问题3: API返回500错误

**症状**: 知识库API调用失败

**解决**:
1. 检查日志: `tail -f logs/server.log`
2. 验证健康检查: `curl http://localhost:8000/api/v1/knowledge/health`
3. 检查服务状态

## 📞 技术支持

如遇到问题，请查看:
1. 日志文件: `logs/server.log`
2. API文档: http://localhost:8000/docs
3. 健康检查: http://localhost:8000/api/v1/knowledge/health

---

**整合完成时间**: 2025-11-10 14:58:50  
**系统版本**: CHS-Books v2.0 + CHS-AI v2.1.0
