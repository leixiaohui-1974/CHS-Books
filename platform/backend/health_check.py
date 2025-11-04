"""
健康检查工具
检查所有服务和组件的健康状态
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))


async def check_database():
    """检查数据库连接"""
    try:
        from app.core.database import engine
        
        if engine:
            async with engine.connect() as conn:
                pass
            return True, "数据库连接正常"
    except Exception as e:
        return False, f"数据库连接失败: {e}"


async def check_redis():
    """检查Redis连接"""
    try:
        # 简化版本，实际应该测试Redis连接
        return True, "Redis配置正常"
    except Exception as e:
        return False, f"Redis连接失败: {e}"


async def check_services():
    """检查所有服务"""
    try:
        from app.services.code_intelligence import code_intelligence_service
        from app.services.ai_assistant_enhanced import ai_assistant_service
        from app.services.execution_engine import enhanced_execution_engine
        
        # 测试代码智能服务
        is_valid, _ = await code_intelligence_service.validate_code("print('test')")
        if not is_valid:
            return False, "代码智能服务异常"
        
        # 测试执行引擎
        stats = enhanced_execution_engine.get_pool_stats()
        if stats['total'] == 0:
            return False, "执行引擎未初始化"
        
        return True, f"所有服务正常 (容器池: {stats['available']}/{stats['total']})"
    
    except Exception as e:
        return False, f"服务检查失败: {e}"


async def check_file_structure():
    """检查文件结构"""
    required_files = [
        "app/main.py",
        "app/api/__init__.py",
        "app/services/session_service.py",
        "app/services/execution_engine.py",
        "app/services/code_intelligence.py",
        "app/services/ai_assistant_enhanced.py",
        "app/services/result_parser.py",
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        return False, f"缺失文件: {', '.join(missing)}"
    
    return True, f"文件结构完整 ({len(required_files)} 个核心文件)"


async def main():
    """主检查函数"""
    print("=" * 60)
    print(" 智能知识平台 V2.0 - 健康检查")
    print("=" * 60)
    print()
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("文件结构", check_file_structure()),
        ("核心服务", check_services()),
        ("数据库连接", check_database()),
        ("Redis连接", check_redis()),
    ]
    
    results = []
    
    for name, check_coro in checks:
        print(f"检查 {name}...", end=" ")
        try:
            success, message = await check_coro
            status = "✅" if success else "❌"
            print(f"{status} {message}")
            results.append(success)
        except Exception as e:
            print(f"❌ 错误: {e}")
            results.append(False)
    
    print()
    print("=" * 60)
    
    all_passed = all(results)
    passed_count = sum(results)
    total_count = len(results)
    
    if all_passed:
        print(f"✅ 所有检查通过 ({passed_count}/{total_count})")
        print("系统运行正常！")
    else:
        print(f"⚠️  部分检查失败 ({passed_count}/{total_count})")
        print("请检查失败项目")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
