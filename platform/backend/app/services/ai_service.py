"""
AI助手服务
支持多种LLM API集成
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.models.user import User
from app.models.book import Book, Chapter, Case


class AIService:
    """AI助手服务类"""
    
    def __init__(self):
        """初始化AI服务"""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("AI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "1000"))
    
    async def chat(
        self,
        message: str,
        user_id: int,
        context: Optional[Dict[str, Any]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        AI聊天功能
        
        Args:
            message: 用户消息
            user_id: 用户ID
            context: 上下文信息
            db: 数据库会话
        
        Returns:
            AI响应
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(context)
            
            # 获取用户上下文
            if db:
                user_context = await self._get_user_context(db, user_id)
                system_prompt += f"\n\n用户背景：{user_context}"
            
            # TODO: 实际调用AI API
            # import openai
            # openai.api_key = self.api_key
            # response = openai.ChatCompletion.create(
            #     model=self.model,
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": message}
            #     ],
            #     temperature=self.temperature,
            #     max_tokens=self.max_tokens
            # )
            # ai_message = response.choices[0].message.content
            
            # 模拟AI响应
            ai_message = self._generate_mock_response(message, context)
            
            logger.info(f"AI响应生成成功 - 用户: {user_id}, 消息长度: {len(message)}")
            
            return {
                "success": True,
                "message": ai_message,
                "model": self.model,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI响应生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "抱歉，我现在无法回答您的问题。请稍后再试。"
            }
    
    async def explain_concept(
        self,
        concept: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        解释工程概念
        
        Args:
            concept: 概念名称
            context: 上下文（如所属章节）
        
        Returns:
            概念解释
        """
        try:
            system_prompt = """你是一位工程学专家，擅长用简单易懂的语言解释复杂概念。
请用以下结构解释概念：
1. 简单定义（1-2句话）
2. 核心原理（3-5句话）
3. 实际应用（2-3个例子）
4. 常见误解（1-2个）
5. 相关概念（3-5个）
"""
            
            # TODO: 调用AI API
            # response = self._call_ai_api(system_prompt, f"请解释：{concept}")
            
            # 模拟响应
            explanation = f"""
**{concept}**

**简单定义**：
{concept}是工程学中的重要概念，用于描述和分析特定问题。

**核心原理**：
1. 基于数学模型和物理定律
2. 通过定量分析来预测系统行为
3. 考虑多种影响因素和边界条件

**实际应用**：
- 水利工程设计
- 建筑结构分析
- 流体力学计算

**常见误解**：
很多人认为{concept}只适用于理论研究，实际上它在工程实践中应用广泛。

**相关概念**：
流体力学、水力学、明渠流动、渠道设计、水力计算
"""
            
            logger.info(f"概念解释生成成功: {concept}")
            
            return {
                "success": True,
                "concept": concept,
                "explanation": explanation.strip(),
                "context": context
            }
            
        except Exception as e:
            logger.error(f"概念解释失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def recommend_cases(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        推荐学习案例
        
        基于用户学习历史推荐相关案例
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回数量
        
        Returns:
            推荐案例列表
        """
        try:
            from app.models.progress import CaseProgress, UserProgress, ProgressStatus
            
            # 获取用户已完成的案例
            result = await db.execute(
                select(CaseProgress.case_id)
                .join(UserProgress, UserProgress.id == CaseProgress.user_progress_id)
                .where(
                    UserProgress.user_id == user_id,
                    CaseProgress.status == ProgressStatus.COMPLETED
                )
            )
            completed_case_ids = [row[0] for row in result.all()]
            
            # 获取未完成的案例（简单推荐算法）
            result = await db.execute(
                select(Case)
                .where(Case.id.notin_(completed_case_ids) if completed_case_ids else True)
                .limit(limit * 2)  # 多获取一些以便过滤
            )
            cases = result.scalars().all()
            
            # 构建推荐列表
            recommendations = []
            for case in cases[:limit]:
                recommendations.append({
                    "case_id": case.id,
                    "title": case.title,
                    "difficulty": case.difficulty.value if hasattr(case, 'difficulty') else "beginner",
                    "estimated_minutes": case.estimated_minutes if hasattr(case, 'estimated_minutes') else 30,
                    "reason": self._generate_recommendation_reason(case)
                })
            
            logger.info(f"案例推荐成功 - 用户: {user_id}, 推荐数: {len(recommendations)}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"案例推荐失败: {e}")
            return []
    
    async def analyze_learning_path(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        分析学习路径
        
        基于用户当前进度，生成个性化学习建议
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            学习路径分析
        """
        try:
            from app.models.progress import UserProgress, CaseProgress, ProgressStatus
            
            # 获取用户所有进度
            result = await db.execute(
                select(UserProgress)
                .where(UserProgress.user_id == user_id)
            )
            user_progresses = result.scalars().all()
            
            if not user_progresses:
                return {
                    "status": "beginner",
                    "message": "您还没有开始学习，建议从基础课程开始。",
                    "recommendations": []
                }
            
            # 计算整体进度
            total_time = sum(up.total_time_spent for up in user_progresses)
            total_completed = sum(up.cases_completed for up in user_progresses)
            
            # 生成分析报告
            analysis = {
                "learning_stage": self._determine_learning_stage(total_time, total_completed),
                "total_study_hours": round(total_time / 3600, 1),
                "completed_cases": total_completed,
                "enrolled_courses": len(user_progresses),
                "strengths": self._identify_strengths(user_progresses),
                "areas_for_improvement": self._identify_weaknesses(user_progresses),
                "next_steps": self._generate_next_steps(user_progresses)
            }
            
            logger.info(f"学习路径分析完成 - 用户: {user_id}")
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"学习路径分析失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]]) -> str:
        """构建系统提示词"""
        base_prompt = """你是一位工程学习助手，专门帮助学生学习水利工程、明渠水力学等课程。
你的职责是：
1. 回答学生的技术问题
2. 解释工程概念和原理
3. 提供学习建议和方法
4. 推荐相关案例和资源

请用友好、专业的语气回答，适当使用例子和类比来帮助理解。"""
        
        if context:
            if "chapter" in context:
                base_prompt += f"\n\n当前章节：{context['chapter']}"
            if "case" in context:
                base_prompt += f"\n当前案例：{context['case']}"
        
        return base_prompt
    
    async def _get_user_context(self, db: AsyncSession, user_id: int) -> str:
        """获取用户学习背景"""
        from app.models.progress import UserProgress
        
        result = await db.execute(
            select(func.count(UserProgress.id))
            .where(UserProgress.user_id == user_id)
        )
        course_count = result.scalar() or 0
        
        if course_count == 0:
            return "新用户，刚开始学习"
        elif course_count < 3:
            return "初学者，正在学习基础课程"
        else:
            return "有经验的学习者，已完成多门课程"
    
    def _generate_mock_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """生成模拟AI响应（用于测试）"""
        message_lower = message.lower()
        
        # 简单的关键词匹配
        if any(word in message_lower for word in ["什么是", "解释", "定义"]):
            return "这是一个很好的问题。让我来解释一下：这个概念涉及到工程学的基本原理，在实际应用中非常重要..."
        
        elif any(word in message_lower for word in ["怎么", "如何", "方法"]):
            return "关于这个问题，我建议采取以下步骤：\n1. 首先理解基本概念\n2. 然后通过案例学习\n3. 最后进行实践练习"
        
        elif any(word in message_lower for word in ["推荐", "建议"]):
            return "根据您的学习进度，我建议：\n- 继续巩固基础知识\n- 尝试更多实践案例\n- 参与讨论和交流"
        
        else:
            return f"感谢您的提问。关于'{message}'，这是一个很有价值的问题。让我们一起来探讨..."
    
    def _generate_recommendation_reason(self, case) -> str:
        """生成推荐理由"""
        reasons = [
            "适合您当前的学习阶段",
            "与您已完成的案例相关",
            "帮助巩固重要概念",
            "热门案例，推荐学习",
            "由浅入深，循序渐进"
        ]
        import random
        return random.choice(reasons)
    
    def _determine_learning_stage(self, total_time: int, completed_cases: int) -> str:
        """判断学习阶段"""
        if completed_cases < 5:
            return "初学阶段"
        elif completed_cases < 20:
            return "进阶阶段"
        else:
            return "高级阶段"
    
    def _identify_strengths(self, progresses) -> List[str]:
        """识别优势领域"""
        # 简化版：基于完成率
        strengths = []
        for progress in progresses:
            if progress.cases_completed > 5:
                strengths.append("基础知识扎实")
                break
        
        if not strengths:
            strengths.append("学习态度积极")
        
        return strengths
    
    def _identify_weaknesses(self, progresses) -> List[str]:
        """识别改进领域"""
        weaknesses = []
        
        total_cases = sum(p.cases_total for p in progresses if p.cases_total > 0)
        completed_cases = sum(p.cases_completed for p in progresses)
        
        if total_cases > 0:
            completion_rate = completed_cases / total_cases
            if completion_rate < 0.3:
                weaknesses.append("建议提高案例完成率")
        
        if not weaknesses:
            weaknesses.append("继续保持当前学习节奏")
        
        return weaknesses
    
    def _generate_next_steps(self, progresses) -> List[str]:
        """生成下一步建议"""
        return [
            "继续完成当前课程的剩余案例",
            "定期复习已学内容",
            "尝试更高难度的挑战"
        ]


# 全局实例
ai_service = AIService()


# 便捷函数
async def chat_with_ai(
    message: str,
    user_id: int,
    context: Optional[Dict[str, Any]] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """AI聊天"""
    return await ai_service.chat(message, user_id, context, db)


async def explain_concept(
    concept: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """解释概念"""
    return await ai_service.explain_concept(concept, context)


async def recommend_cases(
    db: AsyncSession,
    user_id: int,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """推荐案例"""
    return await ai_service.recommend_cases(db, user_id, limit)
