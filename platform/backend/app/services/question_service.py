"""
题目管理服务
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, update
from sqlalchemy.orm import selectinload

from app.models.exercise import (
    Question, QuestionSet, Submission, WrongQuestion,
    QuestionType, QuestionDifficulty, SubmissionStatus
)
from app.models.learning import KnowledgePoint


class QuestionService:
    """题目管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================
    # 题目管理
    # ========================================
    
    async def create_question(
        self,
        title: str,
        content: str,
        question_type: QuestionType,
        difficulty: QuestionDifficulty,
        correct_answer: str,
        knowledge_point_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
        explanation: Optional[str] = None,
        score: float = 1.0,
        time_limit: Optional[int] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[int] = None
    ) -> Question:
        """创建题目"""
        question = Question(
            title=title,
            content=content,
            question_type=question_type,
            difficulty=difficulty,
            correct_answer=correct_answer,
            knowledge_point_id=knowledge_point_id,
            chapter_id=chapter_id,
            subject_id=subject_id,
            options=options,
            explanation=explanation,
            score=score,
            time_limit=time_limit,
            tags=tags or [],
            created_by=created_by
        )
        
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        
        return question
    
    async def get_question(self, question_id: int) -> Optional[Question]:
        """获取题目详情"""
        result = await self.db.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()
    
    async def get_questions(
        self,
        question_type: Optional[QuestionType] = None,
        difficulty: Optional[QuestionDifficulty] = None,
        knowledge_point_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
        is_public: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Question], int]:
        """获取题目列表"""
        query = select(Question)
        count_query = select(func.count(Question.id))
        
        # 筛选条件
        conditions = []
        if is_active:
            conditions.append(Question.is_active == True)
        if is_public:
            conditions.append(Question.is_public == True)
        if question_type:
            conditions.append(Question.question_type == question_type)
        if difficulty:
            conditions.append(Question.difficulty == difficulty)
        if knowledge_point_id:
            conditions.append(Question.knowledge_point_id == knowledge_point_id)
        if chapter_id:
            conditions.append(Question.chapter_id == chapter_id)
        if subject_id:
            conditions.append(Question.subject_id == subject_id)
        if tags:
            # 题目标签包含任一指定标签
            tag_conditions = [Question.tags.contains([tag]) for tag in tags]
            conditions.append(or_(*tag_conditions))
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # 获取总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 分页和排序
        query = query.order_by(desc(Question.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        questions = list(result.scalars().all())
        
        return questions, total
    
    async def update_question(
        self,
        question_id: int,
        **kwargs
    ) -> Optional[Question]:
        """更新题目"""
        question = await self.get_question(question_id)
        
        if not question:
            return None
        
        for key, value in kwargs.items():
            if hasattr(question, key) and value is not None:
                setattr(question, key, value)
        
        question.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(question)
        
        return question
    
    async def delete_question(self, question_id: int) -> bool:
        """删除题目（软删除）"""
        question = await self.get_question(question_id)
        
        if not question:
            return False
        
        question.is_active = False
        question.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return True
    
    # ========================================
    # 题目提交和判题
    # ========================================
    
    async def submit_answer(
        self,
        user_id: int,
        question_id: int,
        answer: str,
        time_spent: int = 0,
        exercise_id: Optional[int] = None,
        code: Optional[str] = None
    ) -> Submission:
        """提交答案"""
        # 获取题目
        question = await self.get_question(question_id)
        
        if not question:
            raise ValueError("题目不存在")
        
        # 创建提交记录
        submission = Submission(
            user_id=user_id,
            question_id=question_id,
            exercise_id=exercise_id,
            answer=answer,
            code=code,
            time_spent=time_spent,
            status=SubmissionStatus.PENDING
        )
        
        self.db.add(submission)
        await self.db.flush()
        
        # 判题
        is_correct, score, judge_result = await self._judge_answer(
            question, answer, code
        )
        
        # 更新提交记录
        submission.is_correct = is_correct
        submission.score = score
        submission.judge_result = judge_result
        submission.status = SubmissionStatus.ACCEPTED if is_correct else SubmissionStatus.WRONG_ANSWER
        submission.judged_at = datetime.utcnow()
        
        # 更新题目统计
        question.submit_count += 1
        if is_correct:
            question.correct_count += 1
        question.accuracy_rate = (question.correct_count / question.submit_count * 100) if question.submit_count > 0 else 0
        
        # 更新平均用时
        if question.average_time == 0:
            question.average_time = time_spent
        else:
            question.average_time = (question.average_time * (question.submit_count - 1) + time_spent) / question.submit_count
        
        await self.db.commit()
        await self.db.refresh(submission)
        
        # 如果答错，添加到错题本
        if not is_correct:
            await self._add_to_wrong_questions(user_id, question_id, answer)
        else:
            # 如果答对，更新错题本中的记录
            await self._update_wrong_question_correct(user_id, question_id)
        
        return submission
    
    async def _judge_answer(
        self,
        question: Question,
        answer: str,
        code: Optional[str] = None
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """判题逻辑"""
        judge_result = {
            "correct_answer": question.correct_answer,
            "user_answer": answer
        }
        
        if question.question_type == QuestionType.SINGLE_CHOICE:
            # 单选题：完全匹配
            is_correct = answer.strip().upper() == question.correct_answer.strip().upper()
            score = question.score if is_correct else 0
            
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            # 多选题：需要完全正确
            user_answers = set(answer.strip().upper().replace(" ", ""))
            correct_answers = set(question.correct_answer.strip().upper().replace(" ", ""))
            is_correct = user_answers == correct_answers
            score = question.score if is_correct else 0
            
        elif question.question_type == QuestionType.TRUE_FALSE:
            # 判断题
            is_correct = answer.strip().lower() in ['true', '正确', '对', 'yes', '是'] and \
                        question.correct_answer.strip().lower() in ['true', '正确', '对', 'yes', '是'] or \
                        answer.strip().lower() in ['false', '错误', '错', 'no', '否'] and \
                        question.correct_answer.strip().lower() in ['false', '错误', '错', 'no', '否']
            score = question.score if is_correct else 0
            
        elif question.question_type == QuestionType.FILL_BLANK:
            # 填空题：支持多个答案，任一正确即可
            correct_answers = [ans.strip() for ans in question.correct_answer.split('|')]
            is_correct = answer.strip() in correct_answers
            score = question.score if is_correct else 0
            
        elif question.question_type == QuestionType.CODE:
            # 编程题：需要运行代码测试（这里简化处理）
            # 实际应该调用代码执行引擎
            is_correct = False
            score = 0
            judge_result["message"] = "编程题判题功能开发中"
            
        elif question.question_type in [QuestionType.SHORT_ANSWER, QuestionType.CALCULATION]:
            # 简答题和计算题：需要人工批改或更复杂的判断
            # 这里简化为关键词匹配
            keywords = question.correct_answer.split(',')
            matched_count = sum(1 for keyword in keywords if keyword.strip() in answer)
            is_correct = matched_count >= len(keywords) * 0.6  # 60%关键词匹配即算正确
            score = (matched_count / len(keywords)) * question.score if keywords else 0
            judge_result["matched_keywords"] = matched_count
            judge_result["total_keywords"] = len(keywords)
            
        else:
            is_correct = False
            score = 0
        
        return is_correct, score, judge_result
    
    async def get_user_submissions(
        self,
        user_id: int,
        question_id: Optional[int] = None,
        exercise_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Submission]:
        """获取用户提交记录"""
        query = select(Submission).where(Submission.user_id == user_id)
        
        if question_id:
            query = query.where(Submission.question_id == question_id)
        if exercise_id:
            query = query.where(Submission.exercise_id == exercise_id)
        
        query = query.order_by(desc(Submission.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ========================================
    # 错题本
    # ========================================
    
    async def _add_to_wrong_questions(
        self,
        user_id: int,
        question_id: int,
        wrong_answer: str
    ) -> WrongQuestion:
        """添加到错题本"""
        # 检查是否已存在
        result = await self.db.execute(
            select(WrongQuestion).where(
                and_(
                    WrongQuestion.user_id == user_id,
                    WrongQuestion.question_id == question_id
                )
            )
        )
        wrong_question = result.scalar_one_or_none()
        
        if wrong_question:
            # 更新现有记录
            wrong_question.wrong_count += 1
            wrong_question.wrong_answers.append(wrong_answer)
            wrong_question.last_wrong_at = datetime.utcnow()
            wrong_question.is_mastered = False  # 重置掌握状态
        else:
            # 创建新记录
            wrong_question = WrongQuestion(
                user_id=user_id,
                question_id=question_id,
                wrong_count=1,
                wrong_answers=[wrong_answer],
                first_wrong_at=datetime.utcnow(),
                last_wrong_at=datetime.utcnow()
            )
            self.db.add(wrong_question)
        
        await self.db.commit()
        await self.db.refresh(wrong_question)
        
        return wrong_question
    
    async def _update_wrong_question_correct(
        self,
        user_id: int,
        question_id: int
    ) -> Optional[WrongQuestion]:
        """更新错题本中的正确记录"""
        result = await self.db.execute(
            select(WrongQuestion).where(
                and_(
                    WrongQuestion.user_id == user_id,
                    WrongQuestion.question_id == question_id
                )
            )
        )
        wrong_question = result.scalar_one_or_none()
        
        if wrong_question:
            wrong_question.correct_count += 1
            wrong_question.last_review_at = datetime.utcnow()
            
            # 连续正确3次则认为已掌握
            if wrong_question.correct_count >= 3:
                wrong_question.is_mastered = True
                wrong_question.mastered_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(wrong_question)
        
        return wrong_question
    
    async def get_wrong_questions(
        self,
        user_id: int,
        is_mastered: Optional[bool] = None,
        limit: int = 50
    ) -> List[WrongQuestion]:
        """获取错题本"""
        query = select(WrongQuestion).where(WrongQuestion.user_id == user_id)
        
        if is_mastered is not None:
            query = query.where(WrongQuestion.is_mastered == is_mastered)
        
        query = query.options(selectinload(WrongQuestion.question))
        query = query.order_by(desc(WrongQuestion.last_wrong_at)).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def add_wrong_question_note(
        self,
        user_id: int,
        question_id: int,
        notes: str
    ) -> Optional[WrongQuestion]:
        """添加错题笔记"""
        result = await self.db.execute(
            select(WrongQuestion).where(
                and_(
                    WrongQuestion.user_id == user_id,
                    WrongQuestion.question_id == question_id
                )
            )
        )
        wrong_question = result.scalar_one_or_none()
        
        if wrong_question:
            wrong_question.notes = notes
            wrong_question.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(wrong_question)
        
        return wrong_question
    
    async def remove_from_wrong_questions(
        self,
        user_id: int,
        question_id: int
    ) -> bool:
        """从错题本移除"""
        result = await self.db.execute(
            select(WrongQuestion).where(
                and_(
                    WrongQuestion.user_id == user_id,
                    WrongQuestion.question_id == question_id
                )
            )
        )
        wrong_question = result.scalar_one_or_none()
        
        if wrong_question:
            await self.db.delete(wrong_question)
            await self.db.commit()
            return True
        
        return False
    
    # ========================================
    # 题目集合/试卷
    # ========================================
    
    async def create_question_set(
        self,
        title: str,
        question_ids: List[int],
        description: Optional[str] = None,
        set_type: str = "practice",
        subject_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        total_score: float = 100.0,
        pass_score: float = 60.0,
        time_limit: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> QuestionSet:
        """创建题目集合"""
        question_set = QuestionSet(
            title=title,
            description=description,
            set_type=set_type,
            subject_id=subject_id,
            chapter_id=chapter_id,
            question_ids=question_ids,
            total_score=total_score,
            pass_score=pass_score,
            time_limit=time_limit,
            created_by=created_by
        )
        
        self.db.add(question_set)
        await self.db.commit()
        await self.db.refresh(question_set)
        
        return question_set
    
    async def get_question_set(self, set_id: int) -> Optional[QuestionSet]:
        """获取题目集合"""
        result = await self.db.execute(
            select(QuestionSet).where(QuestionSet.id == set_id)
        )
        return result.scalar_one_or_none()
    
    async def get_question_sets(
        self,
        set_type: Optional[str] = None,
        subject_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        is_active: bool = True,
        is_public: bool = True,
        limit: int = 50
    ) -> List[QuestionSet]:
        """获取题目集合列表"""
        query = select(QuestionSet)
        
        conditions = []
        if is_active:
            conditions.append(QuestionSet.is_active == True)
        if is_public:
            conditions.append(QuestionSet.is_public == True)
        if set_type:
            conditions.append(QuestionSet.set_type == set_type)
        if subject_id:
            conditions.append(QuestionSet.subject_id == subject_id)
        if chapter_id:
            conditions.append(QuestionSet.chapter_id == chapter_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(QuestionSet.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_questions_by_set(self, set_id: int) -> List[Question]:
        """获取题目集合中的所有题目"""
        question_set = await self.get_question_set(set_id)
        
        if not question_set or not question_set.question_ids:
            return []
        
        result = await self.db.execute(
            select(Question).where(Question.id.in_(question_set.question_ids))
        )
        questions_map = {q.id: q for q in result.scalars().all()}
        
        # 按题目集合中的顺序返回
        return [questions_map[qid] for qid in question_set.question_ids if qid in questions_map]
