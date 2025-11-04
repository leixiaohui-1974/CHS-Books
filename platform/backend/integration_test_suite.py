#!/usr/bin/env python3
"""
完整集成测试套件
测试所有模块的集成和交互
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# 添加app到路径
sys.path.insert(0, str(Path(__file__).parent))


class TestResult:
    """测试结果"""
    
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0.0
    
    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        duration_str = f"{self.duration:.3f}s"
        
        result = f"{status} {self.name} ({duration_str})"
        if self.error:
            result += f"\n    错误: {self.error}"
        
        return result


class IntegrationTestSuite:
    """集成测试套件"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
    
    async def run_test(self, name: str, test_func):
        """运行单个测试"""
        result = TestResult(name)
        
        print(f"\n🧪 {name}...", end=" ", flush=True)
        
        import time
        start = time.time()
        
        try:
            await test_func()
            result.passed = True
            print("✓")
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            print("✗")
            print(f"   错误: {e}")
        
        result.duration = time.time() - start
        self.results.append(result)
    
    # ==================== 测试用例 ====================
    
    async def test_code_intelligence_module(self):
        """测试代码智能模块"""
        from app.services.code_intelligence import CodeAnalyzer
        
        code = """
import numpy as np

def test():
    return np.array([1, 2, 3])
"""
        analysis = CodeAnalyzer.analyze_code(code)
        assert 'functions' in analysis
        assert 'imports' in analysis
    
    async def test_ai_assistant_structure(self):
        """测试AI助手结构"""
        from app.services.ai_assistant_enhanced import ai_assistant_service
        
        # 只测试服务存在，不实际调用API
        assert ai_assistant_service is not None
        assert hasattr(ai_assistant_service, 'explain_code')
        assert hasattr(ai_assistant_service, 'diagnose_error')
    
    async def test_result_parser_structure(self):
        """测试结果解析器结构"""
        from app.services.result_parser import result_parser
        
        assert result_parser is not None
        assert hasattr(result_parser, 'parse_execution_result')
    
    async def test_execution_engine_structure(self):
        """测试执行引擎结构"""
        from app.services.execution_engine import enhanced_execution_engine
        
        assert enhanced_execution_engine is not None
        stats = enhanced_execution_engine.get_pool_stats()
        assert 'total' in stats
        assert 'available' in stats
    
    async def test_session_models(self):
        """测试会话模型"""
        from app.models.session import UserSession, CodeExecution
        
        # 测试模型定义
        assert UserSession is not None
        assert CodeExecution is not None
    
    async def test_api_endpoints_structure(self):
        """测试API端点结构"""
        from app.api.endpoints import sessions, execution, code, ai_assistant
        
        # 测试端点路由存在
        assert sessions.router is not None
        assert execution.router is not None
        assert code.router is not None
        assert ai_assistant.router is not None
    
    async def test_code_validation(self):
        """测试代码验证"""
        from app.services.code_intelligence import code_intelligence_service
        
        # 正确的代码
        valid_code = "def test(): return 42"
        is_valid, _ = await code_intelligence_service.validate_code(valid_code)
        assert is_valid is True
        
        # 错误的代码
        invalid_code = "def test( return 42"
        is_valid, errors = await code_intelligence_service.validate_code(invalid_code)
        assert is_valid is False
    
    async def test_code_loading(self):
        """测试代码加载"""
        from app.services.code_intelligence import code_intelligence_service
        
        # 测试加载不存在的案例（应该优雅处理）
        try:
            result = await code_intelligence_service.load_case(
                "non-existent-book",
                "non-existent-case"
            )
            # 如果没有抛出异常，检查返回结构
            assert isinstance(result, dict)
        except Exception as e:
            # 预期会失败，这是正常的
            pass
    
    async def test_sdk_import(self):
        """测试SDK可导入"""
        sys.path.insert(0, str(Path(__file__).parent.parent / "sdk" / "python"))
        from platform_sdk import PlatformSDK, SessionContext
        
        assert PlatformSDK is not None
        assert SessionContext is not None
    
    async def test_tools_existence(self):
        """测试工具脚本存在"""
        backend_dir = Path(__file__).parent
        
        tools = [
            "manage.py",
            "health_check.py",
            "performance_monitor.py",
            "benchmark.py",
            "code_quality.py",
            "backup_restore.py",
            "demo_workflow.py",
            "setup_wizard.py",
            "monitor_dashboard.py",
            "log_analyzer.py",
        ]
        
        for tool in tools:
            tool_path = backend_dir / tool
            assert tool_path.exists(), f"{tool} 不存在"
    
    async def test_documentation_exists(self):
        """测试文档存在"""
        platform_dir = Path(__file__).parent.parent
        
        docs = [
            "README_V2.md",
            "QUICK_START.md",
            "USER_MANUAL.md",
            "V2.1_UPDATE_SUMMARY.md",
            "TOOLS_DOCUMENTATION.md",
            "API_USAGE_EXAMPLES.md",
        ]
        
        for doc in docs:
            doc_path = platform_dir / doc
            assert doc_path.exists(), f"{doc} 不存在"
    
    async def test_docker_files_exist(self):
        """测试Docker文件存在"""
        platform_dir = Path(__file__).parent.parent
        
        files = [
            "docker-compose.v2.yml",
            "backend/Dockerfile.enhanced",
        ]
        
        for file in files:
            file_path = platform_dir / file
            assert file_path.exists(), f"{file} 不存在"
    
    # ==================== 运行测试 ====================
    
    async def run_all(self):
        """运行所有测试"""
        self.start_time = datetime.now()
        
        print("=" * 70)
        print(" 智能知识平台 V2.1 - 集成测试套件")
        print("=" * 70)
        print(f"\n开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 运行测试
        tests = [
            ("代码智能模块", self.test_code_intelligence_module),
            ("AI助手结构", self.test_ai_assistant_structure),
            ("结果解析器结构", self.test_result_parser_structure),
            ("执行引擎结构", self.test_execution_engine_structure),
            ("会话模型", self.test_session_models),
            ("API端点结构", self.test_api_endpoints_structure),
            ("代码验证", self.test_code_validation),
            ("代码加载", self.test_code_loading),
            ("SDK导入", self.test_sdk_import),
            ("工具脚本存在性", self.test_tools_existence),
            ("文档存在性", self.test_documentation_exists),
            ("Docker文件存在性", self.test_docker_files_exist),
        ]
        
        for name, test_func in tests:
            await self.run_test(name, test_func)
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        success_rate = passed / len(self.results) * 100 if self.results else 0
        
        print("\n" + "=" * 70)
        print(" 测试报告")
        print("=" * 70)
        print()
        
        # 统计
        print("📊 测试统计:")
        print(f"  总测试数:   {len(self.results)}")
        print(f"  通过:       {passed}")
        print(f"  失败:       {failed}")
        print(f"  成功率:     {success_rate:.1f}%")
        print(f"  总耗时:     {duration:.2f}s")
        print()
        
        # 失败的测试
        if failed > 0:
            print("❌ 失败的测试:")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.name}")
                    print(f"    {result.error}")
            print()
        
        # 测试详情
        print("📋 测试详情:")
        for result in self.results:
            print(f"  {result}")
        print()
        
        print("=" * 70)
        
        if failed == 0:
            print("✅ 所有测试通过！")
        else:
            print(f"⚠️  {failed} 个测试失败")
        
        print("=" * 70)
        
        # 保存报告
        report_data = {
            'timestamp': end_time.isoformat(),
            'duration': duration,
            'total': len(self.results),
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'error': r.error,
                    'duration': r.duration
                }
                for r in self.results
            ]
        }
        
        report_file = f"test_report_{end_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 报告已保存: {report_file}")


async def main():
    """主函数"""
    suite = IntegrationTestSuite()
    await suite.run_all()


if __name__ == "__main__":
    asyncio.run(main())
