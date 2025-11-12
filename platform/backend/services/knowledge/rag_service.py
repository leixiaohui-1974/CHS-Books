"""
RAG (检索增强生成) 服务
"""
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import openai
from anthropic import Anthropic
from config.settings import settings
from .models import KnowledgeEntry, QueryLog, AcademicLevel
from .vector_store import vector_store
from .knowledge_service import knowledge_service
# from .mock_llm_service import  # Optional module mock_llm_service


class RAGService:
    """RAG服务"""
    
    def __init__(self):
        """初始化"""
        self.openai_client = None
        self.anthropic_client = None
    
    def _get_llm_client(self, provider: str = None):
        """获取LLM客户端"""
        provider = provider or settings.default_llm_provider
        
        if provider == "openai":
            if not self.openai_client:
                openai.api_key = settings.openai_api_key
                self.openai_client = openai
            return self.openai_client
        elif provider == "anthropic":
            if not self.anthropic_client:
                self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
            return self.anthropic_client
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def retrieve_context(
        self,
        db: Session,
        query: str,
        category_id: Optional[str] = None,
        level: Optional[AcademicLevel] = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        检索相关知识上下文
        
        Args:
            db: 数据库会话
            query: 用户问题
            category_id: 分类ID
            level: 学术层级
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        top_k = top_k or settings.top_k_results
        
        # 使用知识服务进行搜索
        results = knowledge_service.search_knowledge(
            db=db,
            query=query,
            category_id=category_id,
            level=level,
            top_k=top_k
        )
        
        return results
    
    def build_prompt(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        system_role: str = None
    ) -> str:
        """
        构建提示词
        
        Args:
            query: 用户问题
            context_docs: 上下文文档列表
            system_role: 系统角色描述
            
        Returns:
            完整的提示词
        """
        if not system_role:
            system_role = """你是一位水利水电水务领域的专家，拥有深厚的专业知识和丰富的实践经验。
你的任务是基于提供的知识库内容，准确、专业地回答用户的问题。

回答要求：
1. 仔细阅读提供的知识内容，确保答案准确
2. 使用专业术语，保持学术严谨性
3. 在回答中引用具体的知识来源（用【】标注）
4. 如果知识库内容不足以回答问题，请明确说明
5. 答案要条理清晰，必要时使用列表或分点说明
6. 涉及规范标准时，要明确标注规范编号和版本"""
        
        # 构建上下文
        context_text = "\n\n".join([
            f"【知识{i+1}】{doc['title']}\n来源：{doc.get('source_type', '')}\n内容：{doc['content_snippet']}"
            for i, doc in enumerate(context_docs)
        ])
        
        # 构建完整提示
        prompt = f"""{system_role}

## 相关知识内容：

{context_text}

## 用户问题：
{query}

## 专家回答：
"""
        
        return prompt
    
    def generate_answer(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        context_docs: List[Dict[str, Any]] = None,
        query: str = None
    ) -> str:
        """
        生成回答
        
        Args:
            prompt: 提示词
            provider: LLM提供商
            model: 模型名称
            context_docs: 上下文文档（用于mock模式）
            query: 原始问题（用于mock模式）
            
        Returns:
            生成的回答
        """
        provider = provider or settings.default_llm_provider
        
        # 如果没有配置API Key，使用模拟服务
        if provider == "openai" and not settings.openai_api_key:
            provider = "mock"
        elif provider == "anthropic" and not settings.anthropic_api_key:
            provider = "mock"
        
        try:
            if provider == "mock":
                # 使用模拟LLM服务
                return mock_llm_service.generate_answer(
                    prompt=prompt,
                    context_docs=context_docs or [],
                    query=query or ""
                )
            
            elif provider == "openai":
                model = model or "gpt-3.5-turbo"
                client = self._get_llm_client("openai")
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                return response.choices[0].message.content
            
            elif provider == "anthropic":
                model = model or "claude-3-sonnet-20240229"
                client = self._get_llm_client("anthropic")
                
                response = client.messages.create(
                    model=model,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return response.content[0].text
            
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        except Exception as e:
            return f"生成回答时出错：{str(e)}"
    
    def answer_question(
        self,
        db: Session,
        query: str,
        category_id: Optional[str] = None,
        level: Optional[AcademicLevel] = None,
        user_id: Optional[str] = None,
        provider: str = None,
        save_log: bool = True
    ) -> Dict[str, Any]:
        """
        回答问题（完整的RAG流程）
        
        Args:
            db: 数据库会话
            query: 用户问题
            category_id: 分类ID
            level: 学术层级
            user_id: 用户ID
            provider: LLM提供商
            save_log: 是否保存日志
            
        Returns:
            包含答案和元信息的字典
        """
        # 记录开始时间
        start_time = time.time()
        
        # 1. 检索相关知识
        retrieval_start = time.time()
        context_docs = self.retrieve_context(
            db=db,
            query=query,
            category_id=category_id,
            level=level
        )
        retrieval_time = time.time() - retrieval_start
        
        # 2. 构建提示词
        prompt = self.build_prompt(query, context_docs)
        
        # 3. 生成回答
        generation_start = time.time()
        answer = self.generate_answer(
            prompt=prompt, 
            provider=provider,
            context_docs=context_docs,
            query=query
        )
        generation_time = time.time() - generation_start
        
        # 4. 整理返回结果
        result = {
            'query': query,
            'answer': answer,
            'context_docs': context_docs,
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'total_time': time.time() - start_time,
        }
        
        # 5. 保存查询日志
        if save_log:
            log = QueryLog(
                user_id=user_id,
                query=query,
                response=answer,
                retrieved_docs=[doc['knowledge_id'] for doc in context_docs],
                relevance_scores=[doc.get('distance', 0) for doc in context_docs],
                retrieval_time=retrieval_time,
                generation_time=generation_time
            )
            db.add(log)
            db.commit()
        
        return result
    
    def evaluate_answer(
        self,
        db: Session,
        query_log_id: str,
        is_helpful: bool,
        feedback: str = None
    ) -> bool:
        """
        评价回答质量
        
        Args:
            db: 数据库会话
            query_log_id: 查询日志ID
            is_helpful: 是否有帮助
            feedback: 反馈内容
            
        Returns:
            是否评价成功
        """
        log = db.query(QueryLog).filter(QueryLog.id == query_log_id).first()
        if not log:
            return False
        
        log.is_helpful = 1 if is_helpful else 0
        if feedback:
            log.feedback = feedback
        
        db.commit()
        return True


# 全局RAG服务实例
rag_service = RAGService()
