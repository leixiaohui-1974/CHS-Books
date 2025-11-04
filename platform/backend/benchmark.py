"""
性能基准测试
测试各个模块和API的性能表现
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Callable
import statistics


class BenchmarkResult:
    """基准测试结果"""
    
    def __init__(self, name: str):
        self.name = name
        self.times: List[float] = []
        self.errors: List[str] = []
    
    def add_time(self, duration: float):
        """添加测试时间"""
        self.times.append(duration)
    
    def add_error(self, error: str):
        """添加错误"""
        self.errors.append(error)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if not self.times:
            return {
                "name": self.name,
                "count": 0,
                "error_count": len(self.errors),
                "success_rate": 0.0
            }
        
        return {
            "name": self.name,
            "count": len(self.times),
            "min": min(self.times),
            "max": max(self.times),
            "mean": statistics.mean(self.times),
            "median": statistics.median(self.times),
            "stdev": statistics.stdev(self.times) if len(self.times) > 1 else 0,
            "p95": self._percentile(self.times, 0.95),
            "p99": self._percentile(self.times, 0.99),
            "error_count": len(self.errors),
            "success_rate": len(self.times) / (len(self.times) + len(self.errors)) * 100
        }
    
    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]


class Benchmark:
    """基准测试器"""
    
    def __init__(self):
        self.results: Dict[str, BenchmarkResult] = {}
    
    async def run_test(
        self,
        name: str,
        func: Callable,
        iterations: int = 100,
        warmup: int = 10
    ):
        """
        运行测试
        
        Args:
            name: 测试名称
            func: 测试函数
            iterations: 迭代次数
            warmup: 预热次数
        """
        print(f"\n🧪 测试: {name}")
        print(f"   迭代次数: {iterations}")
        print(f"   预热次数: {warmup}")
        
        result = BenchmarkResult(name)
        self.results[name] = result
        
        # 预热
        print("   预热中...", end=" ", flush=True)
        for _ in range(warmup):
            try:
                if asyncio.iscoroutinefunction(func):
                    await func()
                else:
                    func()
            except Exception:
                pass
        print("✓")
        
        # 正式测试
        print("   测试中...", end=" ", flush=True)
        for i in range(iterations):
            if (i + 1) % 20 == 0:
                print(f"{i+1}", end=" ", flush=True)
            
            start = time.time()
            try:
                if asyncio.iscoroutinefunction(func):
                    await func()
                else:
                    func()
                
                duration = time.time() - start
                result.add_time(duration)
            except Exception as e:
                result.add_error(str(e))
        
        print("✓")
        
        # 显示结果
        stats = result.get_stats()
        print(f"\n   结果:")
        if stats['count'] > 0:
            print(f"     平均时间: {stats['mean']*1000:.2f}ms")
            print(f"     中位数:   {stats['median']*1000:.2f}ms")
            print(f"     最小值:   {stats['min']*1000:.2f}ms")
            print(f"     最大值:   {stats['max']*1000:.2f}ms")
            print(f"     P95:      {stats['p95']*1000:.2f}ms")
            print(f"     P99:      {stats['p99']*1000:.2f}ms")
            print(f"     标准差:   {stats['stdev']*1000:.2f}ms")
        print(f"     成功次数: {stats['count']}")
        print(f"     错误次数: {stats['error_count']}")
        print(f"     成功率:   {stats['success_rate']:.1f}%")
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 70)
        report.append(" 性能基准测试报告")
        report.append("=" * 70)
        report.append("")
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for name, result in self.results.items():
            stats = result.get_stats()
            report.append(f"测试: {name}")
            report.append("-" * 70)
            report.append(f"  迭代次数:   {stats['count']}")
            report.append(f"  平均时间:   {stats.get('mean', 0)*1000:.2f}ms")
            report.append(f"  中位数:     {stats.get('median', 0)*1000:.2f}ms")
            report.append(f"  最小值:     {stats.get('min', 0)*1000:.2f}ms")
            report.append(f"  最大值:     {stats.get('max', 0)*1000:.2f}ms")
            report.append(f"  P95:        {stats.get('p95', 0)*1000:.2f}ms")
            report.append(f"  P99:        {stats.get('p99', 0)*1000:.2f}ms")
            report.append(f"  标准差:     {stats.get('stdev', 0)*1000:.2f}ms")
            report.append(f"  错误次数:   {stats['error_count']}")
            report.append(f"  成功率:     {stats['success_rate']:.1f}%")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


# ==================== 测试用例 ====================

async def test_code_validation():
    """测试代码验证性能"""
    from app.services.code_intelligence import code_intelligence_service
    
    code = """
def test_function():
    x = 10
    y = 20
    return x + y
"""
    await code_intelligence_service.validate_code(code)


async def test_code_analysis():
    """测试代码分析性能"""
    from app.services.code_intelligence import CodeAnalyzer
    
    code = """
import numpy as np

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return np.mean(self.data)

def calculate(x, y):
    return x * y + 10
"""
    CodeAnalyzer.analyze_code(code)


async def test_ai_explanation():
    """测试AI讲解性能"""
    from app.services.ai_assistant_enhanced import ai_assistant_service
    
    code = "def add(a, b): return a + b"
    await ai_assistant_service.explain_code(code, "简单的加法函数")


async def test_result_parsing():
    """测试结果解析性能"""
    from app.services.result_parser import result_parser
    
    result_data = {
        "plots": [{"file": "plot.png", "type": "line"}],
        "console_output": "计算完成\n结果: 42",
        "execution_time": 1.5
    }
    
    await result_parser.parse_execution_result(
        "test_exec_id",
        result_data,
        output_dir="/tmp/test_output"
    )


# ==================== 主程序 ====================

async def main():
    """主测试函数"""
    print("=" * 70)
    print(" 智能知识平台 V2.0 - 性能基准测试")
    print("=" * 70)
    
    benchmark = Benchmark()
    
    # 测试1: 代码验证
    await benchmark.run_test(
        "代码验证 (Code Validation)",
        test_code_validation,
        iterations=100,
        warmup=10
    )
    
    # 测试2: 代码分析
    await benchmark.run_test(
        "代码分析 (Code Analysis)",
        test_code_analysis,
        iterations=100,
        warmup=10
    )
    
    # 测试3: AI讲解
    await benchmark.run_test(
        "AI代码讲解 (AI Explanation)",
        test_ai_explanation,
        iterations=50,
        warmup=5
    )
    
    # 测试4: 结果解析
    await benchmark.run_test(
        "结果解析 (Result Parsing)",
        test_result_parsing,
        iterations=100,
        warmup=10
    )
    
    # 生成报告
    print("\n\n")
    report = benchmark.generate_report()
    print(report)
    
    # 保存报告
    report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
