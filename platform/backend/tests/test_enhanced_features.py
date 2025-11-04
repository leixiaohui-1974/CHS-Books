"""
增强功能集成测试
"""

import pytest
import asyncio
from datetime import datetime
from app.services.session_service import SessionService, ExecutionService
from app.services.code_intelligence import code_intelligence_service
from app.services.ai_assistant_enhanced import ai_assistant_service


class TestSessionService:
    """会话服务测试"""
    
    @pytest.mark.asyncio
    async def test_create_session(self, db_session):
        """测试创建会话"""
        session = await SessionService.create_session(
            db=db_session,
            user_id=1,
            book_slug="water-environment-simulation",
            case_slug="case_01_diffusion"
        )
        
        assert session is not None
        assert session.user_id == 1
        assert session.status.value == "active"
        assert session.can_execute() is True
    
    @pytest.mark.asyncio
    async def test_session_expiration(self, db_session):
        """测试会话过期"""
        session = await SessionService.create_session(
            db=db_session,
            user_id=1,
            book_slug="test-book",
            case_slug="test-case"
        )
        
        # 人工设置过期时间
        from datetime import timedelta
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
        
        assert session.is_expired() is True
        assert session.can_execute() is False


class TestCodeIntelligence:
    """代码智能服务测试"""
    
    @pytest.mark.asyncio
    async def test_validate_code(self):
        """测试代码验证"""
        valid_code = "print('Hello, World!')"
        is_valid, error = await code_intelligence_service.validate_code(valid_code)
        
        assert is_valid is True
        assert error is None
        
        invalid_code = "print('Hello World'"
        is_valid, error = await code_intelligence_service.validate_code(invalid_code)
        
        assert is_valid is False
        assert error is not None
    
    @pytest.mark.asyncio
    async def test_code_analysis(self, tmp_path):
        """测试代码分析"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import numpy as np

def calculate(x):
    '''Calculate something'''
    return x * 2

class MyClass:
    def method(self):
        pass
""")
        
        result = await code_intelligence_service.analyze_code(str(test_file))
        
        assert "imports" in result
        assert "numpy" in result["imports"]
        assert len(result["functions"]) >= 1
        assert len(result["classes"]) >= 1


class TestAIAssistant:
    """AI助手服务测试"""
    
    @pytest.mark.asyncio
    async def test_explain_code(self):
        """测试代码讲解"""
        code = "x = [i**2 for i in range(10)]"
        explanation = await ai_assistant_service.explain_code(code)
        
        assert explanation is not None
        assert len(explanation) > 0
    
    @pytest.mark.asyncio
    async def test_diagnose_error(self):
        """测试错误诊断"""
        code = "print(undefined_variable)"
        error_msg = "NameError: name 'undefined_variable' is not defined"
        
        diagnosis = await ai_assistant_service.diagnose_error(code, error_msg)
        
        assert "diagnosis" in diagnosis
        assert "suggestions" in diagnosis
        assert len(diagnosis["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_insights(self):
        """测试洞察生成"""
        result_data = {
            "plots": [{"name": "plot1"}, {"name": "plot2"}],
            "metrics": [
                {"name": "error", "value": 0.001},
                {"name": "time", "value": 10.5}
            ]
        }
        
        insights = await ai_assistant_service.generate_insights(result_data)
        
        assert isinstance(insights, list)
        assert len(insights) > 0


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, db_session, tmp_path):
        """测试完整工作流"""
        # 1. 创建会话
        session = await SessionService.create_session(
            db=db_session,
            user_id=1,
            book_slug="test-book",
            case_slug="test-case"
        )
        
        assert session is not None
        
        # 2. 创建执行记录
        execution = await ExecutionService.create_execution(
            db=db_session,
            session_id=session.session_id,
            user_id=1,
            script_path="/path/to/script.py",
            input_params={"param1": 100}
        )
        
        assert execution is not None
        assert execution.status == "pending"
        
        # 3. 更新执行状态
        updated = await ExecutionService.update_execution_status(
            db=db_session,
            execution_id=execution.execution_id,
            status="completed",
            execution_time=10
        )
        
        assert updated.status == "completed"
        
        # 4. 更新会话统计
        session = await SessionService.increment_execution_count(
            db=db_session,
            session_id=session.session_id,
            execution_id=execution.execution_id,
            execution_time=10
        )
        
        assert session.execution_count == 1
        assert session.total_execution_time == 10


# Pytest配置
@pytest.fixture
async def db_session():
    """模拟数据库会话"""
    from unittest.mock import MagicMock
    
    mock_db = MagicMock()
    mock_db.commit = asyncio.coroutine(lambda: None)
    mock_db.refresh = asyncio.coroutine(lambda x: None)
    mock_db.execute = asyncio.coroutine(lambda x: MagicMock(scalar_one_or_none=lambda: None))
    
    return mock_db


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
