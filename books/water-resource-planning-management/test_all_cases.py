#!/usr/bin/env python
"""
测试所有案例

快速验证所有案例是否可以正常运行

使用方法:
    python test_all_cases.py

作者：教材编写组
日期：2025-11-02
"""

import os
import sys
import subprocess
from pathlib import Path


class CasesTester:
    """案例测试器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.examples_dir = self.project_root / "code" / "examples"
        
        # 所有案例列表
        self.cases = [
            "case01_frequency_analysis",
            "case02_runoff_forecast",
            "case03_carrying_capacity",
            "case04_multi_objective_allocation",
            "case05_cascade_reservoir",
            "case06_uncertainty_optimization",
            "case07_canal_control",
            "case08_network_dispatch",
            "case09_realtime_reservoir",
            "case10_deep_learning_forecast",
            "case11_anomaly_detection",
            "case12_rl_scheduling",
            "case13_digital_twin",
            "case14_network_estimation",
            "case15_data_assimilation",
            "case16_flood_risk",
            "case17_water_security",
            "case18_robust_dispatch",
            "case19_decision_support",
            "case20_basin_management",
        ]
        
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def test_case(self, case_name):
        """测试单个案例"""
        case_dir = self.examples_dir / case_name
        main_file = case_dir / "main.py"
        
        if not main_file.exists():
            return False, f"主文件不存在: {main_file}"
        
        try:
            # 运行案例（捕获输出）
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd=case_dir,
                capture_output=True,
                timeout=30,  # 30秒超时
                text=True
            )
            
            if result.returncode == 0:
                return True, "运行成功"
            else:
                return False, f"退出码: {result.returncode}\n{result.stderr[:200]}"
        
        except subprocess.TimeoutExpired:
            return False, "运行超时（>30秒）"
        
        except Exception as e:
            return False, f"运行异常: {str(e)}"
    
    def test_all(self):
        """测试所有案例"""
        print("=" * 70)
        print("测试所有案例")
        print("=" * 70)
        print(f"\n总案例数: {len(self.cases)}\n")
        
        for i, case_name in enumerate(self.cases, 1):
            self.results['total'] += 1
            
            print(f"[{i}/{len(self.cases)}] 测试 {case_name}...", end=' ')
            
            success, message = self.test_case(case_name)
            
            if success:
                self.results['passed'] += 1
                print("✓ 通过")
            else:
                self.results['failed'] += 1
                print("✗ 失败")
                self.results['errors'].append({
                    'case': case_name,
                    'message': message
                })
        
        self.print_summary()
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 70)
        print("测试摘要")
        print("=" * 70)
        
        print(f"\n总计:   {self.results['total']}个案例")
        print(f"通过:   {self.results['passed']}个 ✓")
        print(f"失败:   {self.results['failed']}个✗")
        print(f"成功率: {self.results['passed']/self.results['total']*100:.1f}%")
        
        if self.results['errors']:
            print("\n失败详情:")
            print("-" * 70)
            for error in self.results['errors']:
                print(f"\n案例: {error['case']}")
                print(f"原因: {error['message']}")
        
        print("\n" + "=" * 70)
        
        if self.results['failed'] == 0:
            print("🎉 所有案例测试通过！")
        else:
            print(f"⚠️  有 {self.results['failed']} 个案例未通过测试")
        
        print("=" * 70)


def main():
    """主函数"""
    print("\n" + "*" * 70)
    print(" " * 22 + "案例测试工具")
    print(" " * 15 + "水资源规划与管理教材")
    print("*" * 70 + "\n")
    
    tester = CasesTester()
    tester.test_all()


if __name__ == "__main__":
    main()
