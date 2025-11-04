"""
智能知识平台 Python SDK
提供简洁的API访问接口
"""

import requests
from typing import Dict, List, Optional, Any
import json
from datetime import datetime


class PlatformSDK:
    """平台SDK主类"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        初始化SDK
        
        Args:
            base_url: API基础URL
            api_key: API密钥（可选）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """统一请求方法"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {e}")
    
    # ==================== 会话管理 ====================
    
    def create_session(
        self, 
        user_id: str,
        book_slug: str,
        case_slug: str
    ) -> Dict:
        """
        创建学习会话
        
        Args:
            user_id: 用户ID
            book_slug: 书籍标识
            case_slug: 案例标识
            
        Returns:
            会话信息
        """
        return self._request(
            'POST',
            '/api/v2/sessions/create',
            json={
                'user_id': user_id,
                'book_slug': book_slug,
                'case_slug': case_slug
            }
        )
    
    def get_session(self, session_id: str) -> Dict:
        """获取会话信息"""
        return self._request('GET', f'/api/v2/sessions/{session_id}')
    
    def list_sessions(self, user_id: str) -> List[Dict]:
        """获取用户的所有会话"""
        return self._request('GET', f'/api/v2/sessions/user/{user_id}')
    
    def pause_session(self, session_id: str) -> Dict:
        """暂停会话"""
        return self._request('POST', f'/api/v2/sessions/{session_id}/pause')
    
    def resume_session(self, session_id: str) -> Dict:
        """恢复会话"""
        return self._request('POST', f'/api/v2/sessions/{session_id}/resume')
    
    def extend_session(self, session_id: str, hours: int = 2) -> Dict:
        """延长会话"""
        return self._request(
            'POST',
            f'/api/v2/sessions/{session_id}/extend',
            json={'hours': hours}
        )
    
    def terminate_session(self, session_id: str) -> Dict:
        """终止会话"""
        return self._request('DELETE', f'/api/v2/sessions/{session_id}')
    
    # ==================== 代码管理 ====================
    
    def load_code(self, book_slug: str, case_slug: str) -> Dict:
        """
        加载案例代码
        
        Args:
            book_slug: 书籍标识
            case_slug: 案例标识
            
        Returns:
            代码文件列表及分析结果
        """
        return self._request(
            'POST',
            '/api/v2/code/load',
            json={
                'book_slug': book_slug,
                'case_slug': case_slug
            }
        )
    
    def analyze_code(self, code: str) -> Dict:
        """分析代码"""
        return self._request(
            'POST',
            '/api/v2/code/analyze',
            json={'code': code}
        )
    
    def edit_file(self, session_id: str, file_path: str, content: str) -> Dict:
        """编辑文件"""
        return self._request(
            'PUT',
            f'/api/v2/code/{session_id}/edit',
            json={
                'file_path': file_path,
                'content': content
            }
        )
    
    def get_diff(self, session_id: str, file_path: str) -> Dict:
        """获取文件差异"""
        return self._request(
            'GET',
            f'/api/v2/code/{session_id}/diff/{file_path}'
        )
    
    def validate_code(self, code: str) -> Dict:
        """验证代码"""
        return self._request(
            'POST',
            '/api/v2/code/validate',
            json={'code': code}
        )
    
    def format_code(self, code: str) -> Dict:
        """格式化代码"""
        return self._request(
            'POST',
            '/api/v2/code/format',
            json={'code': code}
        )
    
    # ==================== 执行管理 ====================
    
    def start_execution(
        self,
        session_id: str,
        script_path: str,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """
        启动代码执行
        
        Args:
            session_id: 会话ID
            script_path: 脚本路径
            parameters: 执行参数
            
        Returns:
            执行信息
        """
        return self._request(
            'POST',
            '/api/v2/execution/start',
            json={
                'session_id': session_id,
                'script_path': script_path,
                'parameters': parameters or {}
            }
        )
    
    def get_execution(self, execution_id: str) -> Dict:
        """获取执行状态"""
        return self._request('GET', f'/api/v2/execution/{execution_id}')
    
    # ==================== AI助手 ====================
    
    def explain_code(self, code: str, context: Optional[str] = None) -> Dict:
        """
        AI代码讲解
        
        Args:
            code: 代码内容
            context: 上下文说明
            
        Returns:
            讲解结果
        """
        return self._request(
            'POST',
            '/api/v2/ai/explain-code',
            json={
                'code': code,
                'context': context
            }
        )
    
    def diagnose_error(self, error: str, code: Optional[str] = None) -> Dict:
        """
        AI错误诊断
        
        Args:
            error: 错误信息
            code: 相关代码
            
        Returns:
            诊断结果
        """
        return self._request(
            'POST',
            '/api/v2/ai/diagnose-error',
            json={
                'error': error,
                'code': code
            }
        )
    
    def ask_question(self, question: str, context: Optional[Dict] = None) -> Dict:
        """
        AI问答
        
        Args:
            question: 问题
            context: 上下文
            
        Returns:
            回答
        """
        return self._request(
            'POST',
            '/api/v2/ai/ask',
            json={
                'question': question,
                'context': context
            }
        )
    
    def generate_insights(self, results: Dict) -> Dict:
        """
        生成结果洞察
        
        Args:
            results: 执行结果
            
        Returns:
            分析洞察
        """
        return self._request(
            'POST',
            '/api/v2/ai/generate-insights',
            json={'results': results}
        )
    
    # ==================== 便捷方法 ====================
    
    def quick_execute(
        self,
        user_id: str,
        book_slug: str,
        case_slug: str,
        script_path: str = 'main.py'
    ) -> Dict:
        """
        快速执行（一键完成会话创建、代码加载、执行）
        
        Args:
            user_id: 用户ID
            book_slug: 书籍标识
            case_slug: 案例标识
            script_path: 脚本路径
            
        Returns:
            执行结果
        """
        # 1. 创建会话
        session = self.create_session(user_id, book_slug, case_slug)
        print(f"✓ 会话已创建: {session['session_id']}")
        
        # 2. 加载代码
        code = self.load_code(book_slug, case_slug)
        print(f"✓ 代码已加载: {len(code.get('files', []))} 个文件")
        
        # 3. 启动执行
        execution = self.start_execution(session['session_id'], script_path)
        print(f"✓ 执行已启动: {execution['execution_id']}")
        
        return {
            'session': session,
            'code': code,
            'execution': execution
        }


class SessionContext:
    """会话上下文管理器"""
    
    def __init__(self, sdk: PlatformSDK, user_id: str, book_slug: str, case_slug: str):
        self.sdk = sdk
        self.user_id = user_id
        self.book_slug = book_slug
        self.case_slug = case_slug
        self.session_id = None
    
    def __enter__(self):
        """进入上下文"""
        session = self.sdk.create_session(
            self.user_id,
            self.book_slug,
            self.case_slug
        )
        self.session_id = session['session_id']
        print(f"✓ 会话已创建: {self.session_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.session_id:
            self.sdk.terminate_session(self.session_id)
            print(f"✓ 会话已终止: {self.session_id}")
    
    def execute(self, script_path: str = 'main.py', parameters: Optional[Dict] = None):
        """执行代码"""
        return self.sdk.start_execution(self.session_id, script_path, parameters)


# ==================== 使用示例 ====================

def example_usage():
    """SDK使用示例"""
    
    # 1. 初始化SDK
    sdk = PlatformSDK(base_url="http://localhost:8000")
    
    # 2. 创建会话
    session = sdk.create_session(
        user_id="demo_user",
        book_slug="water-environment-simulation",
        case_slug="case_01_diffusion"
    )
    print(f"会话ID: {session['session_id']}")
    
    # 3. 加载代码
    code = sdk.load_code(
        book_slug="water-environment-simulation",
        case_slug="case_01_diffusion"
    )
    print(f"加载了 {len(code['files'])} 个文件")
    
    # 4. AI讲解代码
    if code['files']:
        explanation = sdk.explain_code(
            code=code['files'][0]['content'],
            context="扩散方程求解"
        )
        print(f"AI讲解: {explanation['explanation']}")
    
    # 5. 执行代码
    execution = sdk.start_execution(
        session_id=session['session_id'],
        script_path='main.py'
    )
    print(f"执行ID: {execution['execution_id']}")
    
    # 6. 终止会话
    sdk.terminate_session(session['session_id'])
    print("会话已终止")


def example_with_context():
    """使用上下文管理器的示例"""
    
    sdk = PlatformSDK()
    
    # 使用with语句自动管理会话生命周期
    with SessionContext(
        sdk,
        user_id="demo_user",
        book_slug="water-environment-simulation",
        case_slug="case_01_diffusion"
    ) as ctx:
        # 在这里执行操作
        execution = ctx.execute('main.py')
        print(f"执行ID: {execution['execution_id']}")
    
    # 会话会自动终止


if __name__ == "__main__":
    print("=" * 60)
    print(" 智能知识平台 Python SDK - 使用示例")
    print("=" * 60)
    print()
    
    # example_usage()
    # example_with_context()
    
    print("\n提示: 取消注释上面的函数来运行示例")
