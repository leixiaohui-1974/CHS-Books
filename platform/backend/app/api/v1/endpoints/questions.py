"""
题目和练习API端点
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.exercise import QuestionType, QuestionDifficulty, ExerciseStatus
from app.services.question_service import QuestionService


router = APIRouter()


# ========================================
# 请求/响应模型
# ========================================

class CreateQuestionRequest(BaseModel):
    """创建题目请求"""
    title: str = Field(..., description="题目标题")
    content: str = Field(..., description="题目内容（支持Markdown）")
    question_type: str = Field(..., description="题目类型")
    difficulty: str = Field(..., description="难度级别")
    correct_answer: str = Field(..., description="正确答案")
    knowledge_point_id: Optional[int] = Field(None, description="知识点ID")
    chapter_id: Optional[int] = Field(None, description="章节ID")
    subject_id: Optional[int] = Field(None, description="学科ID")
    options: Optional[dict] = Field(None, description="选项（JSON格式）")
    explanation: Optional[str] = Field(None, description="答案解析")
    score: float = Field(1.0, description="分值")
    time_limit: Optional[int] = Field(None, description="时间限制（秒）")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class UpdateQuestionRequest(BaseModel):
    """更新题目请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[str] = None
    correct_answer: Optional[str] = None
    knowledge_point_id: Optional[int] = None
    chapter_id: Optional[int] = None
    subject_id: Optional[int] = None
    options: Optional[dict] = None
    explanation: Optional[str] = None
    score: Optional[float] = None
    time_limit: Optional[int] = None
    tags: Optional[List[str]] = None


class QuestionResponse(BaseModel):
    """题目响应"""
    id: int
    title: str
    content: str
    question_type: str
    difficulty: str
    knowledge_point_id: Optional[int]
    chapter_id: Optional[int]
    subject_id: Optional[int]
    options: Optional[dict]
    explanation: Optional[str]
    score: float
    time_limit: Optional[int]
    tags: Optional[List[str]]
    submit_count: int
    correct_count: int
    accuracy_rate: float
    average_time: float
    is_active: bool
    created_at: str


class SubmitAnswerRequest(BaseModel):
    """提交答案请求"""
    question_id: int = Field(..., description="题目ID")
    answer: str = Field(..., description="用户答案")
    time_spent: int = Field(0, description="用时（秒）")
    exercise_id: Optional[int] = Field(None, description="所属练习ID")
    code: Optional[str] = Field(None, description="代码（编程题）")


class SubmissionResponse(BaseModel):
    """提交响应"""
    id: int
    question_id: int
    is_correct: bool
    score: float
    status: str
    judge_result: Optional[dict]
    time_spent: int
    submitted_at: str


class CreateQuestionSetRequest(BaseModel):
    """创建题集请求"""
    title: str = Field(..., description="题集标题")
    question_ids: List[int] = Field(..., description="题目ID列表")
    description: Optional[str] = Field(None, description="描述")
    set_type: str = Field("practice", description="题集类型")
    subject_id: Optional[int] = Field(None, description="学科ID")
    chapter_id: Optional[int] = Field(None, description="章节ID")
    total_score: float = Field(100.0, description="总分")
    pass_score: float = Field(60.0, description="及格分")
    time_limit: Optional[int] = Field(None, description="时间限制（分钟）")


class WrongQuestionResponse(BaseModel):
    """错题响应"""
    id: int
    question_id: int
    question_title: str
    question_content: str
    question_type: str
    difficulty: str
    wrong_count: int
    correct_count: int
    is_mastered: bool
    notes: Optional[str]
    last_wrong_at: str


# ========================================
# 题目管理端点
# ========================================

@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    request: CreateQuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建题目"""
    service = QuestionService(db)
    
    try:
        question = await service.create_question(
            title=request.title,
            content=request.content,
            question_type=QuestionType(request.question_type),
            difficulty=QuestionDifficulty(request.difficulty),
            correct_answer=request.correct_answer,
            knowledge_point_id=request.knowledge_point_id,
            chapter_id=request.chapter_id,
            subject_id=request.subject_id,
            options=request.options,
            explanation=request.explanation,
            score=request.score,
            time_limit=request.time_limit,
            tags=request.tags,
            created_by=current_user.id
        )
        
        return QuestionResponse(
            id=question.id,
            title=question.title,
            content=question.content,
            question_type=question.question_type.value,
            difficulty=question.difficulty.value,
            knowledge_point_id=question.knowledge_point_id,
            chapter_id=question.chapter_id,
            subject_id=question.subject_id,
            options=question.options,
            explanation=question.explanation,
            score=question.score,
            time_limit=question.time_limit,
            tags=question.tags,
            submit_count=question.submit_count,
            correct_count=question.correct_count,
            accuracy_rate=question.accuracy_rate,
            average_time=question.average_time,
            is_active=question.is_active,
            created_at=question.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/questions", response_model=dict)
async def get_questions(
    question_type: Optional[str] = Query(None, description="题目类型"),
    difficulty: Optional[str] = Query(None, description="难度级别"),
    knowledge_point_id: Optional[int] = Query(None, description="知识点ID"),
    chapter_id: Optional[int] = Query(None, description="章节ID"),
    subject_id: Optional[int] = Query(None, description="学科ID"),
    tags: Optional[str] = Query(None, description="标签（逗号分隔）"),
    limit: int = Query(50, le=100, description="每页数量"),
    offset: int = Query(0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取题目列表"""
    service = QuestionService(db)
    
    tag_list = tags.split(',') if tags else None
    
    try:
        questions, total = await service.get_questions(
            question_type=QuestionType(question_type) if question_type else None,
            difficulty=QuestionDifficulty(difficulty) if difficulty else None,
            knowledge_point_id=knowledge_point_id,
            chapter_id=chapter_id,
            subject_id=subject_id,
            tags=tag_list,
            limit=limit,
            offset=offset
        )
        
        return {
            "total": total,
            "questions": [
                {
                    "id": q.id,
                    "title": q.title,
                    "question_type": q.question_type.value,
                    "difficulty": q.difficulty.value,
                    "score": q.score,
                    "tags": q.tags,
                    "submit_count": q.submit_count,
                    "accuracy_rate": q.accuracy_rate,
                    "created_at": q.created_at.isoformat()
                }
                for q in questions
            ]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取题目详情"""
    service = QuestionService(db)
    question = await service.get_question(question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    return QuestionResponse(
        id=question.id,
        title=question.title,
        content=question.content,
        question_type=question.question_type.value,
        difficulty=question.difficulty.value,
        knowledge_point_id=question.knowledge_point_id,
        chapter_id=question.chapter_id,
        subject_id=question.subject_id,
        options=question.options,
        explanation=question.explanation,
        score=question.score,
        time_limit=question.time_limit,
        tags=question.tags,
        submit_count=question.submit_count,
        correct_count=question.correct_count,
        accuracy_rate=question.accuracy_rate,
        average_time=question.average_time,
        is_active=question.is_active,
        created_at=question.created_at.isoformat()
    )


@router.put("/questions/{question_id}")
async def update_question(
    question_id: int,
    request: UpdateQuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新题目"""
    service = QuestionService(db)
    
    update_data = request.dict(exclude_unset=True)
    
    # 转换枚举类型
    if 'question_type' in update_data and update_data['question_type']:
        update_data['question_type'] = QuestionType(update_data['question_type'])
    if 'difficulty' in update_data and update_data['difficulty']:
        update_data['difficulty'] = QuestionDifficulty(update_data['difficulty'])
    
    question = await service.update_question(question_id, **update_data)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    return {"message": "题目更新成功"}


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除题目"""
    service = QuestionService(db)
    
    success = await service.delete_question(question_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    return {"message": "题目删除成功"}


# ========================================
# 提交和判题端点
# ========================================

@router.post("/submissions", response_model=SubmissionResponse)
async def submit_answer(
    request: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交答案"""
    service = QuestionService(db)
    
    try:
        submission = await service.submit_answer(
            user_id=current_user.id,
            question_id=request.question_id,
            answer=request.answer,
            time_spent=request.time_spent,
            exercise_id=request.exercise_id,
            code=request.code
        )
        
        return SubmissionResponse(
            id=submission.id,
            question_id=submission.question_id,
            is_correct=submission.is_correct,
            score=submission.score,
            status=submission.status.value,
            judge_result=submission.judge_result,
            time_spent=submission.time_spent,
            submitted_at=submission.submitted_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/submissions")
async def get_submissions(
    question_id: Optional[int] = Query(None),
    exercise_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取提交记录"""
    service = QuestionService(db)
    
    submissions = await service.get_user_submissions(
        user_id=current_user.id,
        question_id=question_id,
        exercise_id=exercise_id,
        limit=limit
    )
    
    return {
        "submissions": [
            {
                "id": s.id,
                "question_id": s.question_id,
                "is_correct": s.is_correct,
                "score": s.score,
                "status": s.status.value,
                "time_spent": s.time_spent,
                "submitted_at": s.submitted_at.isoformat()
            }
            for s in submissions
        ]
    }


# ========================================
# 错题本端点
# ========================================

@router.get("/wrong-questions", response_model=List[WrongQuestionResponse])
async def get_wrong_questions(
    is_mastered: Optional[bool] = Query(None, description="是否已掌握"),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取错题本"""
    service = QuestionService(db)
    
    wrong_questions = await service.get_wrong_questions(
        user_id=current_user.id,
        is_mastered=is_mastered,
        limit=limit
    )
    
    return [
        WrongQuestionResponse(
            id=wq.id,
            question_id=wq.question_id,
            question_title=wq.question.title if wq.question else "",
            question_content=wq.question.content if wq.question else "",
            question_type=wq.question.question_type.value if wq.question else "",
            difficulty=wq.question.difficulty.value if wq.question else "",
            wrong_count=wq.wrong_count,
            correct_count=wq.correct_count,
            is_mastered=wq.is_mastered,
            notes=wq.notes,
            last_wrong_at=wq.last_wrong_at.isoformat()
        )
        for wq in wrong_questions
    ]


@router.post("/wrong-questions/{question_id}/note")
async def add_wrong_question_note(
    question_id: int,
    notes: str = Field(..., description="笔记内容"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加错题笔记"""
    service = QuestionService(db)
    
    wrong_question = await service.add_wrong_question_note(
        user_id=current_user.id,
        question_id=question_id,
        notes=notes
    )
    
    if not wrong_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="错题不存在"
        )
    
    return {"message": "笔记添加成功"}


@router.delete("/wrong-questions/{question_id}")
async def remove_wrong_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从错题本移除"""
    service = QuestionService(db)
    
    success = await service.remove_from_wrong_questions(
        user_id=current_user.id,
        question_id=question_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="错题不存在"
        )
    
    return {"message": "已从错题本移除"}


# ========================================
# 题集端点
# ========================================

@router.post("/question-sets")
async def create_question_set(
    request: CreateQuestionSetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建题集"""
    service = QuestionService(db)
    
    question_set = await service.create_question_set(
        title=request.title,
        question_ids=request.question_ids,
        description=request.description,
        set_type=request.set_type,
        subject_id=request.subject_id,
        chapter_id=request.chapter_id,
        total_score=request.total_score,
        pass_score=request.pass_score,
        time_limit=request.time_limit,
        created_by=current_user.id
    )
    
    return {
        "message": "题集创建成功",
        "question_set_id": question_set.id
    }


@router.get("/question-sets")
async def get_question_sets(
    set_type: Optional[str] = Query(None),
    subject_id: Optional[int] = Query(None),
    chapter_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取题集列表"""
    service = QuestionService(db)
    
    question_sets = await service.get_question_sets(
        set_type=set_type,
        subject_id=subject_id,
        chapter_id=chapter_id,
        limit=limit
    )
    
    return {
        "question_sets": [
            {
                "id": qs.id,
                "title": qs.title,
                "description": qs.description,
                "set_type": qs.set_type,
                "total_questions": len(qs.question_ids),
                "total_score": qs.total_score,
                "pass_score": qs.pass_score,
                "time_limit": qs.time_limit,
                "attempt_count": qs.attempt_count,
                "average_score": qs.average_score,
                "created_at": qs.created_at.isoformat()
            }
            for qs in question_sets
        ]
    }


@router.get("/question-sets/{set_id}")
async def get_question_set(
    set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取题集详情"""
    service = QuestionService(db)
    
    question_set = await service.get_question_set(set_id)
    
    if not question_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    return {
        "id": question_set.id,
        "title": question_set.title,
        "description": question_set.description,
        "set_type": question_set.set_type,
        "question_ids": question_set.question_ids,
        "total_score": question_set.total_score,
        "pass_score": question_set.pass_score,
        "time_limit": question_set.time_limit,
        "attempt_count": question_set.attempt_count,
        "average_score": question_set.average_score,
        "is_active": question_set.is_active,
        "created_at": question_set.created_at.isoformat()
    }


@router.get("/question-sets/{set_id}/questions")
async def get_questions_by_set(
    set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取题集中的题目"""
    service = QuestionService(db)
    
    questions = await service.get_questions_by_set(set_id)
    
    return {
        "questions": [
            {
                "id": q.id,
                "title": q.title,
                "content": q.content,
                "question_type": q.question_type.value,
                "difficulty": q.difficulty.value,
                "options": q.options,
                "score": q.score,
                "time_limit": q.time_limit
            }
            for q in questions
        ]
    }
