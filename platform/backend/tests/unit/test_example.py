"""
示例单元测试

这个文件展示了如何编写单元测试。
运行: pytest tests/unit/test_example.py -v
"""
import pytest
from datetime import datetime, timedelta


# ==================== 简单的单元测试 ====================

def test_addition():
    """测试简单的加法"""
    result = 1 + 1
    assert result == 2


def test_string_operations():
    """测试字符串操作"""
    text = "Hello World"

    assert text.lower() == "hello world"
    assert text.upper() == "HELLO WORLD"
    assert len(text) == 11


# ==================== 使用 Fixtures 的测试 ====================

@pytest.fixture
def sample_list():
    """示例列表 fixture"""
    return [1, 2, 3, 4, 5]


def test_list_operations(sample_list):
    """测试列表操作"""
    assert len(sample_list) == 5
    assert sum(sample_list) == 15
    assert max(sample_list) == 5


# ==================== 参数化测试 ====================

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_double(input, expected):
    """测试数字翻倍"""
    result = input * 2
    assert result == expected


@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    (10, 20, 30),
    (-1, 1, 0),
])
def test_addition_parametrized(a, b, expected):
    """参数化加法测试"""
    assert a + b == expected


# ==================== 异常测试 ====================

def test_division_by_zero():
    """测试除零异常"""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0


def test_value_error():
    """测试值错误"""
    with pytest.raises(ValueError):
        int("not a number")


# ==================== 模型测试示例 ====================

class TestUserModel:
    """用户模型测试示例（实际测试需要真实模型）"""

    def test_user_creation(self):
        """测试用户创建"""
        # 这是一个示例，实际测试需要真实的 User 模型
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }

        assert user_data["email"] == "test@example.com"
        assert user_data["username"] == "testuser"

    def test_user_validation(self):
        """测试用户验证"""
        # 示例：邮箱格式验证
        valid_email = "user@example.com"
        invalid_email = "invalid-email"

        assert "@" in valid_email
        assert "@" not in invalid_email


# ==================== 异步测试示例 ====================

@pytest.mark.asyncio
async def test_async_function():
    """异步函数测试示例"""
    import asyncio

    async def async_add(a, b):
        await asyncio.sleep(0.01)  # 模拟异步操作
        return a + b

    result = await async_add(1, 2)
    assert result == 3


# ==================== 测试类示例 ====================

class TestCalculator:
    """计算器测试示例"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前自动运行的设置"""
        self.calculator_state = {"result": 0}

    def test_add(self):
        """测试加法"""
        self.calculator_state["result"] = 5 + 3
        assert self.calculator_state["result"] == 8

    def test_subtract(self):
        """测试减法"""
        self.calculator_state["result"] = 10 - 4
        assert self.calculator_state["result"] == 6

    def test_multiply(self):
        """测试乘法"""
        self.calculator_state["result"] = 6 * 7
        assert self.calculator_state["result"] == 42


# ==================== Mock 示例 ====================

@pytest.mark.asyncio
async def test_with_mock(mocker):
    """使用 Mock 的测试示例"""
    # Mock 一个函数
    mock_function = mocker.Mock(return_value=42)

    result = mock_function()

    assert result == 42
    mock_function.assert_called_once()


# ==================== 慢速测试标记 ====================

@pytest.mark.slow
def test_slow_operation():
    """慢速测试示例（使用 --run-slow 运行）"""
    import time
    time.sleep(1)  # 模拟慢速操作
    assert True


# ==================== 跳过测试 ====================

@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature():
    """未来功能的测试"""
    pass


@pytest.mark.skipif(
    datetime.now().hour < 12,
    reason="仅在下午运行"
)
def test_afternoon_only():
    """仅在下午运行的测试"""
    assert True


# ==================== 测试运行指南 ====================

"""
运行所有测试:
    pytest tests/unit/test_example.py -v

运行特定测试:
    pytest tests/unit/test_example.py::test_addition -v

运行测试类:
    pytest tests/unit/test_example.py::TestCalculator -v

运行带标记的测试:
    pytest tests/unit -m "not slow" -v  # 跳过慢速测试

显示覆盖率:
    pytest tests/unit/test_example.py --cov=app --cov-report=term

生成 HTML 覆盖率报告:
    pytest tests/unit --cov=app --cov-report=html
"""
