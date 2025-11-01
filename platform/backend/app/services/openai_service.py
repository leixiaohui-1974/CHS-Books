"""
OpenAI API服务
提供LLM问答功能
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai package not available")


class OpenAIService:
    """OpenAI API服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化OpenAI服务
        
        Args:
            api_key: OpenAI API密钥
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.success(f"OpenAI client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI package not available, using mock responses")
            else:
                logger.warning("OpenAI API key not provided, using mock responses")
    
    async def generate_answer(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        使用OpenAI生成答案
        
        Args:
            question: 问题
            context: 上下文
            system_prompt: 系统提示
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            生成的答案和元信息
        """
        if self.client is not None:
            try:
                # 构建提示
                if system_prompt is None:
                    system_prompt = """你是一个专业的AI助手，擅长根据提供的上下文信息回答问题。
请遵循以下规则：
1. 仅基于提供的上下文信息回答问题
2. 如果上下文中没有相关信息，请明确说明
3. 回答要准确、简洁、易懂
4. 可以适当引用上下文中的关键信息
"""
                
                user_prompt = f"""上下文信息：
{context}

问题：{question}

请根据上述上下文信息回答问题。"""
                
                # 调用OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                # 提取答案
                answer = response.choices[0].message.content
                
                return {
                    "answer": answer,
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
                
            except Exception as e:
                logger.error(f"Failed to generate answer with OpenAI: {str(e)}")
                return self._generate_mock_answer(question, context)
        else:
            # 使用mock回答
            return self._generate_mock_answer(question, context)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        使用OpenAI生成文本嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if self.client is not None:
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Failed to generate embedding: {str(e)}")
                return self._generate_mock_embedding(text)
        else:
            return self._generate_mock_embedding(text)
    
    def _generate_mock_answer(self, question: str, context: str) -> Dict[str, Any]:
        """生成模拟答案"""
        # 简单的提取式回答
        context_lines = [line.strip() for line in context.split('\n') if line.strip()]
        relevant_lines = [line for line in context_lines if not line.startswith('[')]
        
        if relevant_lines:
            answer = "根据提供的信息：\n\n" + "\n".join(relevant_lines[:2])
        else:
            answer = "抱歉，我无法从提供的上下文中找到相关信息来回答这个问题。"
        
        answer += "\n\n(注：这是模拟回答。实际部署时请配置OPENAI_API_KEY环境变量以使用真实的AI模型。)"
        
        return {
            "answer": answer,
            "model": "mock",
            "tokens_used": 0,
            "finish_reason": "stop"
        }
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """生成模拟嵌入向量"""
        import hashlib
        hash_bytes = hashlib.md5(text.encode()).digest()
        vector = []
        for i in range(0, len(hash_bytes), 2):
            val = (int.from_bytes(hash_bytes[i:i+2], 'little') / 65535.0) * 2 - 1
            vector.append(val)
        
        # 扩展到1536维（OpenAI ada-002的维度）
        while len(vector) < 1536:
            vector.extend(vector[:1536 - len(vector)])
        
        return vector[:1536]


# 全局OpenAI服务实例
openai_service = OpenAIService()
