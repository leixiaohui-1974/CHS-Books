"""
数据库索引优化配置
"""

from sqlalchemy import Index
from app.models.user import User
from app.models.book import Book, Chapter, Case
from app.models.progress import UserProgress, ChapterProgress, CaseProgress


# 用户表索引
user_email_index = Index('idx_user_email', User.email)
user_username_index = Index('idx_user_username', User.username)
user_created_index = Index('idx_user_created', User.created_at)

# 书籍表索引
book_slug_index = Index('idx_book_slug', Book.slug)
book_status_index = Index('idx_book_status', Book.status)
book_difficulty_index = Index('idx_book_difficulty', Book.difficulty)
book_published_index = Index('idx_book_published', Book.published_at)

# 章节表索引
chapter_book_index = Index('idx_chapter_book', Chapter.book_id)
chapter_order_index = Index('idx_chapter_order', Chapter.book_id, Chapter.order)

# 案例表索引
case_book_index = Index('idx_case_book', Case.book_id)
case_chapter_index = Index('idx_case_chapter', Case.chapter_id)
case_book_order_index = Index('idx_case_book_order', Case.book_id, Case.order)

# 进度表索引
user_progress_user_index = Index('idx_user_progress_user', UserProgress.user_id)
user_progress_book_index = Index('idx_user_progress_book', UserProgress.book_id)
user_progress_unique_index = Index('idx_user_progress_unique', UserProgress.user_id, UserProgress.book_id, unique=True)

chapter_progress_user_index = Index('idx_chapter_progress_user', ChapterProgress.user_progress_id)
chapter_progress_chapter_index = Index('idx_chapter_progress_chapter', ChapterProgress.chapter_id)

case_progress_user_index = Index('idx_case_progress_user', CaseProgress.user_progress_id)
case_progress_case_index = Index('idx_case_progress_case', CaseProgress.case_id)


# 索引列表（用于批量创建）
ALL_INDEXES = [
    # 用户索引
    user_email_index,
    user_username_index,
    user_created_index,
    
    # 书籍索引
    book_slug_index,
    book_status_index,
    book_difficulty_index,
    book_published_index,
    
    # 章节索引
    chapter_book_index,
    chapter_order_index,
    
    # 案例索引
    case_book_index,
    case_chapter_index,
    case_book_order_index,
    
    # 进度索引
    user_progress_user_index,
    user_progress_book_index,
    # user_progress_unique_index,  # 已在模型中定义
    chapter_progress_user_index,
    chapter_progress_chapter_index,
    case_progress_user_index,
    case_progress_case_index,
]


def get_index_definitions():
    """获取所有索引定义"""
    return {
        "user_indexes": [user_email_index, user_username_index, user_created_index],
        "book_indexes": [book_slug_index, book_status_index, book_difficulty_index, book_published_index],
        "chapter_indexes": [chapter_book_index, chapter_order_index],
        "case_indexes": [case_book_index, case_chapter_index, case_book_order_index],
        "progress_indexes": [
            user_progress_user_index,
            user_progress_book_index,
            chapter_progress_user_index,
            chapter_progress_chapter_index,
            case_progress_user_index,
            case_progress_case_index,
        ]
    }
