# 🤖 AI增强功能设计方案

**版本**: v1.0  
**制定日期**: 2025-11-12  
**负责模块**: AI智能化功能

---

## 📋 目录

- [系统概述](#系统概述)
- [智能推荐系统](#智能推荐系统)
- [智能答疑系统](#智能答疑系统)
- [代码智能分析](#代码智能分析)
- [学习路径规划](#学习路径规划)
- [技术架构](#技术架构)

---

## 🎯 系统概述

### AI功能全景图

```
Platform AI能力矩阵
┌─────────────────────────────────────────────┐
│                                             │
│  🎯 智能推荐                                 │
│  ├─ 内容推荐 (课程、章节、案例)              │
│  ├─ 协同过滤 (基于相似用户)                  │
│  ├─ 知识图谱推荐                             │
│  └─ 自适应难度推荐                           │
│                                             │
│  💬 智能答疑                                 │
│  ├─ 多轮对话                                 │
│  ├─ 上下文理解                               │
│  ├─ 知识检索增强 (RAG)                       │
│  └─ 循序渐进提示                             │
│                                             │
│  💻 代码分析                                 │
│  ├─ 代码质量分析                             │
│  ├─ Bug检测                                  │
│  ├─ 性能优化建议                             │
│  └─ 最佳实践推荐                             │
│                                             │
│  📚 学习规划                                 │
│  ├─ 个性化学习路径                           │
│  ├─ 薄弱环节诊断                             │
│  ├─ 进度预测                                 │
│  └─ 复习计划生成                             │
│                                             │
│  🎓 内容生成                                 │
│  ├─ 练习题生成                               │
│  ├─ 解释生成                                 │
│  ├─ 示例代码生成                             │
│  └─ 知识总结                                 │
│                                             │
└─────────────────────────────────────────────┘
```

### 核心目标

```yaml
准确性: 
  - 答案准确率 > 90%
  - 推荐准确率 > 85%
  - 代码分析准确率 > 95%

响应速度:
  - 推荐响应 < 500ms
  - 对话响应 < 2s
  - 代码分析 < 3s

用户体验:
  - 用户满意度 > 4.5/5
  - 采纳率 > 70%
  - 反馈改进率 > 80%

成本控制:
  - API调用成本 < ¥0.1/次
  - 缓存命中率 > 60%
  - 本地模型覆盖率 > 40%
```

---

## 🎯 智能推荐系统

### 1. 多维推荐引擎

```python
from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    """多维推荐引擎"""
    
    def __init__(self):
        self.user_embeddings = {}
        self.content_embeddings = {}
        self.knowledge_graph = KnowledgeGraph()
        
    async def recommend(
        self, 
        user_id: int, 
        context: dict,
        limit: int = 10
    ) -> List[Dict]:
        """综合推荐"""
        # 1. 获取用户画像
        user_profile = await self.get_user_profile(user_id)
        
        # 2. 多路召回
        candidates = await self.multi_recall(user_id, user_profile, context)
        
        # 3. 特征工程
        features = await self.extract_features(candidates, user_profile)
        
        # 4. 排序
        ranked = await self.rank_candidates(candidates, features)
        
        # 5. 多样性&去重
        final = self.diversify(ranked, limit)
        
        return final
    
    async def multi_recall(
        self, 
        user_id: int, 
        user_profile: dict,
        context: dict
    ) -> List[Dict]:
        """多路召回策略"""
        candidates = []
        
        # 路径1: 协同过滤
        cf_items = await self.collaborative_filtering(user_id, limit=50)
        candidates.extend(cf_items)
        
        # 路径2: 内容匹配
        content_items = await self.content_based_filtering(
            user_profile, limit=50
        )
        candidates.extend(content_items)
        
        # 路径3: 知识图谱
        kg_items = await self.knowledge_graph_recommend(
            user_profile, context, limit=30
        )
        candidates.extend(kg_items)
        
        # 路径4: 热门推荐
        popular_items = await self.popular_recommend(limit=20)
        candidates.extend(popular_items)
        
        # 路径5: 序列推荐
        seq_items = await self.sequence_recommend(user_id, limit=30)
        candidates.extend(seq_items)
        
        return candidates
    
    async def collaborative_filtering(
        self, 
        user_id: int, 
        limit: int
    ) -> List[Dict]:
        """协同过滤推荐"""
        # 1. 找到相似用户
        similar_users = await self.find_similar_users(user_id, k=20)
        
        # 2. 收集相似用户的学习内容
        items = []
        for sim_user, similarity in similar_users:
            # 获取该用户最近学习的内容
            user_items = await LearningProgress.filter(
                user_id=sim_user,
                completed=True
            ).order_by('-updated_at').limit(10)
            
            for item in user_items:
                # 检查当前用户是否已学习
                learned = await LearningProgress.filter(
                    user_id=user_id,
                    chapter_id=item.chapter_id
                ).exists()
                
                if not learned:
                    items.append({
                        'chapter_id': item.chapter_id,
                        'score': similarity,
                        'reason': f'相似用户也在学习',
                        'source': 'collaborative_filtering'
                    })
        
        # 3. 按相似度得分排序
        items.sort(key=lambda x: x['score'], reverse=True)
        
        return items[:limit]
    
    async def find_similar_users(
        self, 
        user_id: int, 
        k: int = 20
    ) -> List[tuple]:
        """找到相似用户"""
        # 1. 获取用户的学习向量
        user_vector = await self.get_user_vector(user_id)
        
        # 2. 计算与所有用户的相似度
        all_users = await User.all()
        similarities = []
        
        for other_user in all_users:
            if other_user.id == user_id:
                continue
                
            other_vector = await self.get_user_vector(other_user.id)
            similarity = cosine_similarity(
                [user_vector], 
                [other_vector]
            )[0][0]
            
            similarities.append((other_user.id, similarity))
        
        # 3. 返回Top-K
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    async def get_user_vector(self, user_id: int) -> np.ndarray:
        """获取用户向量"""
        # 基于用户的学习历史构建向量
        # [章节偏好, 难度偏好, 主题偏好, ...]
        
        progress = await LearningProgress.filter(
            user_id=user_id
        ).prefetch_related('chapter')
        
        # 特征维度
        features = {
            'total_chapters': len(progress),
            'completion_rate': sum(1 for p in progress if p.completed) / len(progress) if progress else 0,
            'avg_time_spent': np.mean([p.time_spent for p in progress]) if progress else 0,
            # ... 更多特征
        }
        
        # 转换为向量
        vector = np.array(list(features.values()))
        
        # 缓存
        self.user_embeddings[user_id] = vector
        
        return vector
    
    async def content_based_filtering(
        self, 
        user_profile: dict, 
        limit: int
    ) -> List[Dict]:
        """基于内容的推荐"""
        # 1. 获取用户偏好的主题
        preferred_topics = user_profile.get('preferred_topics', [])
        
        # 2. 获取用户当前水平
        current_level = user_profile.get('level', 'intermediate')
        
        # 3. 查询匹配的内容
        chapters = await Chapter.filter(
            tags__overlap=preferred_topics,
            difficulty=current_level
        ).order_by('-created_at').limit(limit)
        
        items = []
        for chapter in chapters:
            items.append({
                'chapter_id': chapter.id,
                'score': 0.8,  # 基础得分
                'reason': f'匹配您的兴趣: {", ".join(preferred_topics)}',
                'source': 'content_based'
            })
        
        return items
    
    async def knowledge_graph_recommend(
        self, 
        user_profile: dict,
        context: dict,
        limit: int
    ) -> List[Dict]:
        """基于知识图谱的推荐"""
        # 1. 获取用户当前学习的知识点
        current_chapter_id = context.get('current_chapter_id')
        if not current_chapter_id:
            return []
        
        # 2. 从知识图谱中查找相关知识点
        related_points = await self.knowledge_graph.get_related(
            current_chapter_id,
            relation_types=['prerequisite', 'related', 'advanced']
        )
        
        # 3. 推荐包含这些知识点的章节
        items = []
        for point, relation, strength in related_points:
            chapters = await Chapter.filter(
                knowledge_points__contains=[point]
            ).limit(5)
            
            for chapter in chapters:
                items.append({
                    'chapter_id': chapter.id,
                    'score': strength,
                    'reason': f'{relation}: {point}',
                    'source': 'knowledge_graph'
                })
        
        items.sort(key=lambda x: x['score'], reverse=True)
        return items[:limit]
    
    async def sequence_recommend(
        self, 
        user_id: int, 
        limit: int
    ) -> List[Dict]:
        """序列推荐 (基于学习路径)"""
        # 1. 获取用户的学习序列
        learning_seq = await LearningProgress.filter(
            user_id=user_id,
            completed=True
        ).order_by('completed_at').values_list('chapter_id', flat=True)
        
        # 2. 使用序列模型预测下一个章节
        # (可以使用RNN/LSTM/Transformer等序列模型)
        next_chapters = await self.predict_next_chapters(
            learning_seq, 
            limit
        )
        
        items = []
        for chapter_id, prob in next_chapters:
            items.append({
                'chapter_id': chapter_id,
                'score': prob,
                'reason': '推荐的学习路径',
                'source': 'sequence'
            })
        
        return items
    
    async def rank_candidates(
        self, 
        candidates: List[Dict],
        features: np.ndarray
    ) -> List[Dict]:
        """候选排序"""
        # 使用LightGBM或深度学习模型进行排序
        # 这里简化为加权组合
        
        weights = {
            'collaborative_filtering': 0.3,
            'content_based': 0.25,
            'knowledge_graph': 0.25,
            'sequence': 0.15,
            'popular': 0.05
        }
        
        for candidate in candidates:
            source = candidate['source']
            candidate['final_score'] = (
                candidate['score'] * weights.get(source, 0.1)
            )
        
        # 去重 (同一章节只保留得分最高的)
        seen = {}
        for candidate in candidates:
            chapter_id = candidate['chapter_id']
            if chapter_id not in seen or \
               candidate['final_score'] > seen[chapter_id]['final_score']:
                seen[chapter_id] = candidate
        
        # 排序
        ranked = list(seen.values())
        ranked.sort(key=lambda x: x['final_score'], reverse=True)
        
        return ranked
    
    def diversify(self, items: List[Dict], limit: int) -> List[Dict]:
        """多样性处理"""
        # MMR (Maximal Marginal Relevance) 算法
        selected = []
        candidates = items.copy()
        
        if not candidates:
            return []
        
        # 选择得分最高的作为第一个
        selected.append(candidates.pop(0))
        
        while len(selected) < limit and candidates:
            max_mmr = -float('inf')
            max_idx = 0
            
            for i, candidate in enumerate(candidates):
                # 计算与已选项的相似度
                similarities = [
                    self.item_similarity(candidate, s) 
                    for s in selected
                ]
                max_sim = max(similarities) if similarities else 0
                
                # MMR得分
                mmr = 0.7 * candidate['final_score'] - 0.3 * max_sim
                
                if mmr > max_mmr:
                    max_mmr = mmr
                    max_idx = i
            
            selected.append(candidates.pop(max_idx))
        
        return selected
    
    def item_similarity(self, item1: dict, item2: dict) -> float:
        """计算项目相似度"""
        # 简化版: 基于章节所属的书籍
        # 实际可以使用更复杂的相似度计算
        if item1.get('book_id') == item2.get('book_id'):
            return 0.8
        return 0.2
```

### 2. 自适应难度推荐

```python
class AdaptiveDifficultyRecommender:
    """自适应难度推荐"""
    
    async def recommend_exercises(
        self, 
        user_id: int, 
        knowledge_point_id: int,
        count: int = 5
    ) -> List[Exercise]:
        """推荐合适难度的练习"""
        # 1. 评估用户能力
        user_ability = await self.estimate_user_ability(
            user_id, 
            knowledge_point_id
        )
        
        # 2. 选择合适难度的练习
        exercises = await self.select_exercises(
            knowledge_point_id,
            user_ability,
            count
        )
        
        return exercises
    
    async def estimate_user_ability(
        self, 
        user_id: int, 
        knowledge_point_id: int
    ) -> float:
        """估计用户能力 (IRT模型)"""
        # 获取用户的历史表现
        records = await ExerciseRecord.filter(
            user_id=user_id,
            exercise__knowledge_points__contains=[knowledge_point_id]
        ).order_by('-created_at').limit(20)
        
        if not records:
            return 0.5  # 默认中等能力
        
        # 计算正确率
        correct = sum(1 for r in records if r.passed)
        total = len(records)
        accuracy = correct / total
        
        # 考虑题目难度
        # (简化版IRT，实际可以使用更复杂的模型)
        ability = accuracy
        
        # 调整: 如果最近表现好，提高能力评估
        recent_records = records[:5]
        recent_accuracy = sum(1 for r in recent_records if r.passed) / len(recent_records)
        
        if recent_accuracy > accuracy + 0.2:
            ability = min(1.0, ability + 0.1)
        elif recent_accuracy < accuracy - 0.2:
            ability = max(0.0, ability - 0.1)
        
        return ability
    
    async def select_exercises(
        self, 
        knowledge_point_id: int,
        user_ability: float,
        count: int
    ) -> List[Exercise]:
        """选择练习"""
        # 选择难度接近用户能力的练习
        target_difficulty = user_ability
        
        # 分布: 70%接近能力, 20%稍难, 10%稍易
        exercises = []
        
        # 70% 接近能力
        near_count = int(count * 0.7)
        near_exercises = await Exercise.filter(
            knowledge_points__contains=[knowledge_point_id],
            difficulty_score__gte=target_difficulty - 0.1,
            difficulty_score__lte=target_difficulty + 0.1
        ).order_by('?').limit(near_count)
        exercises.extend(near_exercises)
        
        # 20% 稍难
        hard_count = int(count * 0.2)
        hard_exercises = await Exercise.filter(
            knowledge_points__contains=[knowledge_point_id],
            difficulty_score__gt=target_difficulty + 0.1,
            difficulty_score__lte=target_difficulty + 0.3
        ).order_by('?').limit(hard_count)
        exercises.extend(hard_exercises)
        
        # 10% 稍易
        easy_count = count - len(exercises)
        easy_exercises = await Exercise.filter(
            knowledge_points__contains=[knowledge_point_id],
            difficulty_score__gte=target_difficulty - 0.3,
            difficulty_score__lt=target_difficulty - 0.1
        ).order_by('?').limit(easy_count)
        exercises.extend(easy_exercises)
        
        return exercises
```

---

## 💬 智能答疑系统

### RAG (检索增强生成) 架构

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

class IntelligentTutorSystem:
    """智能导师系统"""
    
    def __init__(self):
        # 初始化组件
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    async def answer_question(
        self, 
        user_id: int,
        question: str,
        context: dict = None
    ) -> dict:
        """回答问题"""
        # 1. 理解问题意图
        intent = await self.understand_intent(question)
        
        # 2. 检索相关知识
        relevant_docs = await self.retrieve_knowledge(
            question, 
            context,
            k=5
        )
        
        # 3. 获取用户学习历史
        user_context = await self.get_user_context(user_id)
        
        # 4. 生成答案
        answer = await self.generate_answer(
            question,
            relevant_docs,
            user_context,
            intent
        )
        
        # 5. 后处理
        answer = await self.post_process(answer, intent)
        
        return {
            'answer': answer['text'],
            'sources': answer['sources'],
            'confidence': answer['confidence'],
            'follow_up_questions': answer['follow_ups']
        }
    
    async def understand_intent(self, question: str) -> dict:
        """理解问题意图"""
        prompt = f"""
        分析以下问题的意图类型:
        问题: {question}
        
        可能的意图类型:
        - concept_explanation: 概念解释
        - problem_solving: 问题求解
        - code_debug: 代码调试
        - learning_guidance: 学习指导
        - comparison: 概念对比
        - application: 实际应用
        
        返回JSON格式:
        {{
            "intent": "意图类型",
            "entities": ["提取的实体"],
            "difficulty": "easy/medium/hard"
        }}
        """
        
        response = await self.llm.agenerate([prompt])
        intent = json.loads(response.generations[0][0].text)
        
        return intent
    
    async def retrieve_knowledge(
        self, 
        question: str,
        context: dict,
        k: int = 5
    ) -> List[Document]:
        """检索相关知识"""
        # 1. 基础检索
        docs = self.vectorstore.similarity_search(question, k=k)
        
        # 2. 如果有上下文，进行过滤
        if context and context.get('current_chapter_id'):
            chapter_id = context['current_chapter_id']
            # 优先返回当前章节的内容
            chapter_docs = [
                d for d in docs 
                if d.metadata.get('chapter_id') == chapter_id
            ]
            
            if chapter_docs:
                docs = chapter_docs + [
                    d for d in docs 
                    if d not in chapter_docs
                ][:k-len(chapter_docs)]
        
        return docs
    
    async def get_user_context(self, user_id: int) -> dict:
        """获取用户上下文"""
        # 获取用户的学习历史
        progress = await LearningProgress.filter(
            user_id=user_id
        ).order_by('-updated_at').limit(5)
        
        # 获取用户的知识掌握情况
        mastery = await KnowledgeMastery.filter(
            user_id=user_id
        ).order_by('-confidence_score').limit(10)
        
        return {
            'recent_chapters': [p.chapter_id for p in progress],
            'strong_topics': [m.knowledge_point_id for m in mastery if m.confidence_score > 0.7],
            'weak_topics': [m.knowledge_point_id for m in mastery if m.confidence_score < 0.5]
        }
    
    async def generate_answer(
        self,
        question: str,
        docs: List[Document],
        user_context: dict,
        intent: dict
    ) -> dict:
        """生成答案"""
        # 构建提示词
        context_text = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""
        你是一位耐心的工程学导师。根据以下信息回答学生的问题。
        
        学生问题: {question}
        问题类型: {intent['intent']}
        
        相关知识:
        {context_text}
        
        学生背景:
        - 最近学习: {user_context.get('recent_chapters', [])}
        - 擅长领域: {user_context.get('strong_topics', [])}
        - 薄弱环节: {user_context.get('weak_topics', [])}
        
        要求:
        1. 回答要准确、清晰、易懂
        2. 根据学生背景调整解释深度
        3. 如果涉及公式，使用LaTeX格式
        4. 如果有代码，提供完整可运行的示例
        5. 提供2-3个后续问题建议
        6. 评估答案的置信度 (0-1)
        
        返回JSON格式:
        {{
            "text": "答案内容",
            "sources": ["引用来源"],
            "confidence": 0.95,
            "follow_ups": ["后续问题1", "后续问题2"]
        }}
        """
        
        response = await self.llm.agenerate([prompt])
        answer = json.loads(response.generations[0][0].text)
        
        return answer
    
    async def post_process(self, answer: dict, intent: dict) -> dict:
        """后处理答案"""
        # 1. 格式化数学公式
        answer['text'] = self.format_math(answer['text'])
        
        # 2. 语法高亮代码
        answer['text'] = self.highlight_code(answer['text'])
        
        # 3. 添加相关资源链接
        answer['resources'] = await self.find_related_resources(intent)
        
        return answer
    
    def format_math(self, text: str) -> str:
        """格式化数学公式"""
        # 将LaTeX公式包装为前端可识别的格式
        import re
        
        # 行内公式 $...$
        text = re.sub(
            r'\$([^\$]+)\$',
            r'\\(\1\\)',
            text
        )
        
        # 行间公式 $$...$$
        text = re.sub(
            r'\$\$([^\$]+)\$\$',
            r'\\[\1\\]',
            text
        )
        
        return text
    
    def highlight_code(self, text: str) -> str:
        """代码高亮"""
        # 使用Pygments进行代码高亮
        import re
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter
        
        # 匹配代码块 ```language\ncode\n```
        pattern = r'```(\w+)\n(.*?)\n```'
        
        def replace_code(match):
            language = match.group(1)
            code = match.group(2)
            
            try:
                lexer = get_lexer_by_name(language)
                formatter = HtmlFormatter()
                return highlight(code, lexer, formatter)
            except:
                return match.group(0)
        
        text = re.sub(pattern, replace_code, text, flags=re.DOTALL)
        
        return text
    
    async def provide_hints(
        self,
        user_id: int,
        exercise_id: int,
        user_code: str
    ) -> List[str]:
        """提供循序渐进的提示"""
        # 1. 分析用户代码
        code_analysis = await self.analyze_code(user_code)
        
        # 2. 获取练习的标准答案
        exercise = await Exercise.get(id=exercise_id)
        solution = exercise.solution
        
        # 3. 生成渐进式提示
        prompt = f"""
        学生正在解决以下练习:
        题目: {exercise.title}
        描述: {exercise.description}
        
        学生代码:
        ```python
        {user_code}
        ```
        
        代码分析:
        {code_analysis}
        
        标准答案:
        ```python
        {solution}
        ```
        
        请生成3个渐进式提示,从最不具体到最具体:
        1. 第一个提示: 方向性指导,不暴露具体实现
        2. 第二个提示: 具体到某个步骤或方法
        3. 第三个提示: 接近答案,但仍需学生思考
        
        返回JSON数组格式。
        """
        
        response = await self.llm.agenerate([prompt])
        hints = json.loads(response.generations[0][0].text)
        
        return hints
```

### 多轮对话管理

```python
class DialogueManager:
    """对话管理器"""
    
    def __init__(self):
        self.sessions = {}  # user_id -> conversation history
        
    async def chat(
        self,
        user_id: int,
        message: str,
        session_id: str = None
    ) -> dict:
        """多轮对话"""
        # 1. 获取或创建会话
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'history': [],
                'context': {},
                'created_at': datetime.utcnow()
            }
        
        session = self.sessions[session_id]
        
        # 2. 添加用户消息
        session['history'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.utcnow()
        })
        
        # 3. 上下文理解
        context = await self.understand_context(
            session['history'],
            session['context']
        )
        
        # 4. 生成回复
        response = await self.generate_response(
            user_id,
            message,
            session['history'],
            context
        )
        
        # 5. 添加助手消息
        session['history'].append({
            'role': 'assistant',
            'content': response['text'],
            'timestamp': datetime.utcnow()
        })
        
        # 6. 更新上下文
        session['context'].update(response.get('context_update', {}))
        
        return response
    
    async def understand_context(
        self,
        history: List[dict],
        current_context: dict
    ) -> dict:
        """理解对话上下文"""
        # 分析对话历史,提取关键信息
        # - 当前讨论的主题
        # - 用户的困惑点
        # - 需要澄清的地方
        
        recent_messages = history[-5:]  # 最近5轮对话
        
        # 使用LLM提取上下文
        messages_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in recent_messages
        ])
        
        prompt = f"""
        分析以下对话,提取关键上下文信息:
        
        {messages_text}
        
        返回JSON格式:
        {{
            "topic": "当前讨论的主题",
            "user_confusion": "用户的困惑点",
            "resolved": true/false,
            "next_step": "建议的下一步"
        }}
        """
        
        # ... LLM调用
        
        return context
    
    async def generate_response(
        self,
        user_id: int,
        message: str,
        history: List[dict],
        context: dict
    ) -> dict:
        """生成回复"""
        # 1. 判断是否需要检索知识
        needs_retrieval = await self.needs_knowledge_retrieval(message)
        
        if needs_retrieval:
            # 使用RAG生成回复
            tutor = IntelligentTutorSystem()
            return await tutor.answer_question(user_id, message, context)
        else:
            # 直接对话生成
            return await self.direct_chat(message, history, context)
    
    async def direct_chat(
        self,
        message: str,
        history: List[dict],
        context: dict
    ) -> dict:
        """直接对话"""
        # 构建对话历史
        messages = [
            {"role": "system", "content": "你是一位友好的学习助手。"}
        ]
        
        for msg in history[-10:]:  # 最近10轮
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # 调用ChatGPT
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        
        return {
            'text': response.choices[0].message.content,
            'type': 'chat'
        }
```

---

## 💻 代码智能分析

### 代码质量分析器

```python
import ast
import radon.complexity as radon_complexity
import radon.metrics as radon_metrics
from pylint import lint
from pylint.reporters.text import TextReporter

class CodeIntelligenceService:
    """代码智能分析服务"""
    
    async def analyze_code(
        self,
        code: str,
        language: str = 'python'
    ) -> dict:
        """综合代码分析"""
        if language == 'python':
            return await self.analyze_python_code(code)
        else:
            return {'error': f'Unsupported language: {language}'}
    
    async def analyze_python_code(self, code: str) -> dict:
        """Python代码分析"""
        results = {
            'quality': {},
            'complexity': {},
            'style': {},
            'bugs': [],
            'suggestions': [],
            'score': 0
        }
        
        try:
            # 1. 语法检查
            ast.parse(code)
            results['quality']['syntax'] = 'valid'
            
            # 2. 复杂度分析
            results['complexity'] = self.analyze_complexity(code)
            
            # 3. 代码风格检查
            results['style'] = self.check_style(code)
            
            # 4. Bug检测
            results['bugs'] = self.detect_bugs(code)
            
            # 5. 生成建议
            results['suggestions'] = await self.generate_suggestions(
                code,
                results
            )
            
            # 6. 计算总分
            results['score'] = self.calculate_score(results)
            
        except SyntaxError as e:
            results['quality']['syntax'] = 'invalid'
            results['bugs'].append({
                'type': 'SyntaxError',
                'line': e.lineno,
                'message': str(e),
                'severity': 'high'
            })
        
        return results
    
    def analyze_complexity(self, code: str) -> dict:
        """复杂度分析"""
        # 圈复杂度
        cc_results = radon_complexity.cc_visit(code)
        
        # 计算平均圈复杂度
        if cc_results:
            avg_complexity = sum(r.complexity for r in cc_results) / len(cc_results)
        else:
            avg_complexity = 0
        
        # 可维护性指数
        mi = radon_metrics.mi_visit(code, True)
        
        # Halstead复杂度
        h = radon_metrics.h_visit(code)
        
        return {
            'cyclomatic_complexity': {
                'average': round(avg_complexity, 2),
                'functions': [
                    {
                        'name': r.name,
                        'complexity': r.complexity,
                        'rating': self.complexity_rating(r.complexity)
                    }
                    for r in cc_results
                ]
            },
            'maintainability_index': round(mi, 2),
            'halstead': {
                'volume': round(h.total.volume, 2) if h.total else 0,
                'difficulty': round(h.total.difficulty, 2) if h.total else 0
            }
        }
    
    def complexity_rating(self, complexity: int) -> str:
        """复杂度评级"""
        if complexity <= 5:
            return 'A (简单)'
        elif complexity <= 10:
            return 'B (中等)'
        elif complexity <= 20:
            return 'C (复杂)'
        elif complexity <= 30:
            return 'D (很复杂)'
        else:
            return 'F (极其复杂)'
    
    def check_style(self, code: str) -> dict:
        """代码风格检查"""
        from io import StringIO
        
        # 使用pylint检查
        output = StringIO()
        reporter = TextReporter(output)
        
        # 写入临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            lint.Run([temp_file], reporter=reporter, exit=False)
            lint_output = output.getvalue()
            
            # 解析pylint输出
            issues = self.parse_pylint_output(lint_output)
            
            return {
                'issues': issues,
                'count': len(issues)
            }
        finally:
            import os
            os.unlink(temp_file)
    
    def parse_pylint_output(self, output: str) -> List[dict]:
        """解析pylint输出"""
        issues = []
        
        for line in output.split('\n'):
            if ':' in line and ('error' in line.lower() or 'warning' in line.lower()):
                parts = line.split(':')
                if len(parts) >= 3:
                    issues.append({
                        'line': parts[1].strip(),
                        'type': parts[0].strip(),
                        'message': ':'.join(parts[2:]).strip()
                    })
        
        return issues
    
    def detect_bugs(self, code: str) -> List[dict]:
        """Bug检测"""
        bugs = []
        
        try:
            tree = ast.parse(code)
            
            # 1. 检查常见错误模式
            for node in ast.walk(tree):
                # 除零错误
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    if isinstance(node.right, ast.Constant) and node.right.value == 0:
                        bugs.append({
                            'type': 'ZeroDivisionError',
                            'line': node.lineno,
                            'message': '可能的除零错误',
                            'severity': 'high'
                        })
                
                # 未使用的变量
                # ... 更多检查
        
        except:
            pass
        
        return bugs
    
    async def generate_suggestions(
        self,
        code: str,
        analysis: dict
    ) -> List[dict]:
        """生成优化建议"""
        suggestions = []
        
        # 1. 基于复杂度的建议
        cc = analysis['complexity']['cyclomatic_complexity']
        if cc['average'] > 10:
            suggestions.append({
                'type': 'complexity',
                'priority': 'high',
                'message': '代码复杂度较高,建议拆分函数',
                'detail': f'平均圈复杂度: {cc["average"]}, 建议每个函数的复杂度不超过10'
            })
        
        # 2. 基于风格的建议
        style_issues = analysis['style']['issues']
        if len(style_issues) > 5:
            suggestions.append({
                'type': 'style',
                'priority': 'medium',
                'message': f'发现{len(style_issues)}个代码风格问题',
                'detail': '建议按照PEP 8规范调整代码风格'
            })
        
        # 3. 使用AI生成更智能的建议
        ai_suggestions = await self.ai_suggest(code, analysis)
        suggestions.extend(ai_suggestions)
        
        return suggestions
    
    async def ai_suggest(self, code: str, analysis: dict) -> List[dict]:
        """AI生成优化建议"""
        prompt = f"""
        分析以下Python代码并提供优化建议:
        
        ```python
        {code}
        ```
        
        代码分析结果:
        - 平均复杂度: {analysis['complexity']['cyclomatic_complexity']['average']}
        - 可维护性指数: {analysis['complexity']['maintainability_index']}
        - 风格问题数: {analysis['style']['count']}
        - Bug数: {len(analysis['bugs'])}
        
        请提供3-5个具体的优化建议,每个建议包括:
        1. 问题描述
        2. 优化方法
        3. 优化后的示例代码
        
        返回JSON数组格式。
        """
        
        # 调用LLM
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位资深的Python代码审查专家。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        suggestions = json.loads(response.choices[0].message.content)
        
        return [
            {
                'type': 'ai_suggestion',
                'priority': 'medium',
                'message': s['description'],
                'detail': s['method'],
                'example': s.get('example_code')
            }
            for s in suggestions
        ]
    
    def calculate_score(self, analysis: dict) -> int:
        """计算代码质量得分 (0-100)"""
        score = 100
        
        # 语法错误: -50分
        if analysis['quality'].get('syntax') == 'invalid':
            score -= 50
        
        # Bug: 每个-5分
        score -= len(analysis['bugs']) * 5
        
        # 复杂度: 超过10, 每1点-2分
        cc_avg = analysis['complexity']['cyclomatic_complexity']['average']
        if cc_avg > 10:
            score -= int((cc_avg - 10) * 2)
        
        # 风格问题: 每个-1分
        score -= analysis['style']['count']
        
        # 可维护性: 低于60, 每低1点-0.5分
        mi = analysis['complexity']['maintainability_index']
        if mi < 60:
            score -= int((60 - mi) * 0.5)
        
        return max(0, min(100, score))

# API端点
@router.post("/code/analyze")
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """代码分析"""
    service = CodeIntelligenceService()
    analysis = await service.analyze_code(
        request.code,
        request.language
    )
    
    return {'success': True, 'data': analysis}
```

---

## 📚 学习路径规划

```python
class LearningPathPlanner:
    """学习路径规划器"""
    
    async def generate_learning_path(
        self,
        user_id: int,
        goal: str,
        timeframe: int  # 天数
    ) -> dict:
        """生成个性化学习路径"""
        # 1. 评估用户当前水平
        current_level = await self.assess_user_level(user_id)
        
        # 2. 分析目标
        goal_requirements = await self.analyze_goal(goal)
        
        # 3. 识别知识缺口
        knowledge_gaps = await self.identify_gaps(
            current_level,
            goal_requirements
        )
        
        # 4. 生成学习路径
        path = await self.plan_path(
            knowledge_gaps,
            timeframe
        )
        
        # 5. 预估完成时间
        estimation = self.estimate_completion(path, user_id)
        
        return {
            'path': path,
            'estimation': estimation,
            'milestones': self.create_milestones(path, timeframe)
        }
    
    async def assess_user_level(self, user_id: int) -> dict:
        """评估用户水平"""
        # 获取用户的知识掌握情况
        mastery = await KnowledgeMastery.filter(
            user_id=user_id
        ).all()
        
        # 按主题分组
        by_topic = {}
        for m in mastery:
            topic = m.knowledge_point.topic
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(m.confidence_score)
        
        # 计算每个主题的平均掌握度
        level = {
            topic: {
                'score': np.mean(scores),
                'count': len(scores)
            }
            for topic, scores in by_topic.items()
        }
        
        return level
    
    async def analyze_goal(self, goal: str) -> dict:
        """分析学习目标"""
        # 使用LLM分析目标
        prompt = f"""
        分析以下学习目标,提取需要掌握的知识点和技能:
        
        目标: {goal}
        
        返回JSON格式:
        {{
            "topics": ["主题1", "主题2", ...],
            "skills": ["技能1", "技能2", ...],
            "difficulty": "beginner/intermediate/advanced",
            "estimated_hours": 100
        }}
        """
        
        # ... LLM调用
        
        return requirements
    
    async def identify_gaps(
        self,
        current_level: dict,
        goal_requirements: dict
    ) -> List[dict]:
        """识别知识缺口"""
        gaps = []
        
        required_topics = goal_requirements['topics']
        
        for topic in required_topics:
            current = current_level.get(topic, {'score': 0, 'count': 0})
            
            if current['score'] < 0.7:  # 需要提升
                gap = {
                    'topic': topic,
                    'current_score': current['score'],
                    'target_score': 0.8,
                    'priority': 'high' if current['score'] < 0.5 else 'medium'
                }
                gaps.append(gap)
        
        # 按优先级排序
        gaps.sort(key=lambda x: (
            0 if x['priority'] == 'high' else 1,
            x['current_score']
        ))
        
        return gaps
    
    async def plan_path(
        self,
        knowledge_gaps: List[dict],
        timeframe: int
    ) -> List[dict]:
        """规划学习路径"""
        path = []
        
        # 为每个知识缺口规划学习内容
        for gap in knowledge_gaps:
            topic = gap['topic']
            
            # 查找相关章节
            chapters = await Chapter.filter(
                topic=topic
            ).order_by('order')
            
            # 查找相关练习
            exercises = await Exercise.filter(
                topic=topic
            ).order_by('difficulty_score')
            
            path.append({
                'topic': topic,
                'chapters': [
                    {
                        'id': c.id,
                        'title': c.title,
                        'estimated_time': c.estimated_time
                    }
                    for c in chapters
                ],
                'exercises': [
                    {
                        'id': e.id,
                        'title': e.title,
                        'difficulty': e.difficulty
                    }
                    for e in exercises[:10]  # 每个主题10个练习
                ],
                'target_score': gap['target_score']
            })
        
        return path
    
    def create_milestones(
        self,
        path: List[dict],
        timeframe: int
    ) -> List[dict]:
        """创建里程碑"""
        milestones = []
        
        # 将学习路径分成几个阶段
        stages = len(path)
        days_per_stage = timeframe // stages
        
        current_day = 0
        for i, stage in enumerate(path):
            milestone = {
                'stage': i + 1,
                'title': f'掌握{stage["topic"]}',
                'target_date': (
                    datetime.now() + timedelta(days=current_day + days_per_stage)
                ).isoformat(),
                'criteria': {
                    'chapters_completed': len(stage['chapters']),
                    'exercises_passed': len(stage['exercises']),
                    'target_score': stage['target_score']
                }
            }
            
            milestones.append(milestone)
            current_day += days_per_stage
        
        return milestones
```

---

## 🏗️ 技术架构

### AI服务架构

```
┌────────────────────────────────────────────┐
│            前端应用层                       │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 推荐展示 │  │ 对话界面 │  │代码分析 │ │
│  └──────────┘  └──────────┘  └─────────┘ │
└────────────────────────────────────────────┘
             ▲           ▲            ▲
             │           │            │
             ▼           ▼            ▼
┌────────────────────────────────────────────┐
│            API网关层                        │
│  ┌──────────────────────────────────────┐ │
│  │   路由 | 鉴权 | 限流 | 缓存          │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
             ▲           ▲            ▲
             │           │            │
             ▼           ▼            ▼
┌────────────────────────────────────────────┐
│            AI服务层                         │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 推荐服务 │  │ 对话服务 │  │分析服务 │ │
│  └──────────┘  └──────────┘  └─────────┘ │
└────────────────────────────────────────────┘
             ▲           ▲            ▲
             │           │            │
             ▼           ▼            ▼
┌────────────────────────────────────────────┐
│            模型层                           │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 推荐模型 │  │   LLM    │  │静态分析 │ │
│  │(LightGBM)│  │(GPT-4)   │  │(Pylint) │ │
│  └──────────┘  └──────────┘  └─────────┘ │
└────────────────────────────────────────────┘
             ▲           ▲            ▲
             │           │            │
             ▼           ▼            ▼
┌────────────────────────────────────────────┐
│            数据层                           │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │PostgreSQL│  │ ChromaDB │  │  Redis  │ │
│  │(用户数据)│  │(向量库)  │  │(缓存)   │ │
│  └──────────┘  └──────────┘  └─────────┘ │
└────────────────────────────────────────────┘
```

### 成本优化策略

```python
class AIServiceOptimizer:
    """AI服务成本优化"""
    
    def __init__(self):
        self.cache = Redis()
        self.local_model = LocalModel()  # 本地轻量模型
        self.api_model = OpenAIModel()   # API模型
        
    async def query(self, request: dict) -> dict:
        """智能查询 (成本优化)"""
        # 1. 检查缓存
        cache_key = self.generate_cache_key(request)
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 2. 判断复杂度
        complexity = self.assess_complexity(request)
        
        # 3. 选择模型
        if complexity == 'simple':
            # 使用本地模型 (免费)
            result = await self.local_model.predict(request)
        else:
            # 使用API模型 (付费)
            result = await self.api_model.predict(request)
        
        # 4. 缓存结果
        await self.cache.setex(
            cache_key,
            3600,  # 1小时
            json.dumps(result)
        )
        
        return result
    
    def assess_complexity(self, request: dict) -> str:
        """评估请求复杂度"""
        # 简单规则:
        # - 问题长度 < 100字符 -> simple
        # - 有上下文 -> complex
        # - 需要推理 -> complex
        
        if len(request.get('query', '')) < 100:
            return 'simple'
        
        return 'complex'
```

---

**文档版本**: v1.0  
**最后更新**: 2025-11-12
