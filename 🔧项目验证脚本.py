#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
15本考研书系列 - 项目完整性验证脚本

功能：
1. 检查所有15本书的文件完整性
2. 统计详细文件数量
3. 验证配套文档是否齐全
4. 生成验证报告
"""

import os
from pathlib import Path
from datetime import datetime

class ProjectValidator:
    def __init__(self, workspace_path="/workspace"):
        self.workspace = Path(workspace_path)
        self.books_path = self.workspace / "books" / "graduate-exam-prep"
        
        # 15本书的标准配置
        self.expected_books = {
            "hydraulics-core-100": 10,
            "math-quick": 10,
            "probability-stats-guide": 10,
            "ecohydraulics": 10,
            "groundwater": 10,
            "hydraulics-advanced": 10,
            "python-practice": 10,
            "interview-guide": 10,
            "numerical-methods": 10,
            "water-structures": 10,
            "hydrology-exam-sprint": 10,
            "hydrology-advanced": 10,
            "water-supply-drainage": 10,
            "water-resources-mgmt": 10,
            "engineering-hydrology": 10,
        }
        
        # 配套文档清单
        self.expected_docs = [
            "README.md",
            "🚀快速开始指南-START_HERE.md",
            "📑Python代码速查手册.md",
            "❓常见问题FAQ.md",
            "🗺️知识体系导航图.md",
            "📚文档索引目录.md",
            "📊15本书系列最终统计报告.md",
            "🎓15本考研书系列-项目完成证书.md",
            "🏆Phase6完美收官-174文件-100%达成-2025-11-12.md",
            "🎊🎊🎊项目100%完成-最终总结.md",
            "📋学习进度追踪表.md",
            "🎯3个月学习计划模板.md",
        ]
        
        self.results = {
            "books": {},
            "docs": {},
            "total_files": 0,
            "missing_files": [],
            "extra_files": [],
            "errors": []
        }
    
    def validate_books(self):
        """验证所有书籍文件"""
        print("\n" + "="*60)
        print("📚 正在验证15本书的文件完整性...")
        print("="*60)
        
        for book_name, expected_count in self.expected_books.items():
            book_path = self.books_path / book_name
            
            if not book_path.exists():
                self.results["errors"].append(f"❌ 书籍目录不存在: {book_name}")
                self.results["books"][book_name] = {
                    "expected": expected_count,
                    "actual": 0,
                    "status": "❌ MISSING"
                }
                print(f"❌ {book_name}: 目录不存在")
                continue
            
            # 统计详细文件
            detail_files = list(book_path.rglob("*详细*.md"))
            actual_count = len(detail_files)
            
            status = "✅ OK" if actual_count >= expected_count else "⚠️ INCOMPLETE"
            
            self.results["books"][book_name] = {
                "expected": expected_count,
                "actual": actual_count,
                "files": [str(f.relative_to(self.books_path)) for f in detail_files],
                "status": status
            }
            
            if actual_count >= expected_count:
                print(f"✅ {book_name}: {actual_count}/{expected_count} 文件")
            else:
                print(f"⚠️ {book_name}: {actual_count}/{expected_count} 文件 (缺少{expected_count - actual_count}个)")
                self.results["missing_files"].append(f"{book_name}: 缺少{expected_count - actual_count}个文件")
            
            self.results["total_files"] += actual_count
    
    def validate_docs(self):
        """验证配套文档"""
        print("\n" + "="*60)
        print("📖 正在验证配套文档...")
        print("="*60)
        
        for doc_name in self.expected_docs:
            doc_path = self.workspace / doc_name
            
            if doc_path.exists():
                file_size = doc_path.stat().st_size / 1024  # KB
                self.results["docs"][doc_name] = {
                    "status": "✅ OK",
                    "size": f"{file_size:.1f} KB"
                }
                print(f"✅ {doc_name} ({file_size:.1f} KB)")
            else:
                self.results["docs"][doc_name] = {
                    "status": "❌ MISSING",
                    "size": "0 KB"
                }
                print(f"❌ {doc_name} - 文件缺失")
                self.results["missing_files"].append(f"文档: {doc_name}")
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("📊 生成验证报告...")
        print("="*60)
        
        # 统计
        total_expected = sum(self.expected_books.values())
        total_actual = self.results["total_files"]
        books_ok = sum(1 for b in self.results["books"].values() 
                      if b["status"] == "✅ OK")
        docs_ok = sum(1 for d in self.results["docs"].values() 
                     if d["status"] == "✅ OK")
        
        # 生成报告
        report = []
        report.append("# 🔧 项目完整性验证报告\n")
        report.append(f"**验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("---\n")
        
        # 总体情况
        report.append("## 📊 总体情况\n")
        report.append(f"- 📚 书籍文件: {total_actual}/{total_expected} ({total_actual/total_expected*100:.1f}%)\n")
        report.append(f"- 📖 完整书籍: {books_ok}/{len(self.expected_books)} ({books_ok/len(self.expected_books)*100:.1f}%)\n")
        report.append(f"- 📄 配套文档: {docs_ok}/{len(self.expected_docs)} ({docs_ok/len(self.expected_docs)*100:.1f}%)\n")
        
        if not self.results["missing_files"] and not self.results["errors"]:
            report.append(f"\n**✅ 项目完整性: 100% - 所有文件完整！**\n")
        else:
            report.append(f"\n**⚠️ 项目完整性: {(total_actual/total_expected*100):.1f}%**\n")
        
        report.append("\n---\n")
        
        # 书籍详情
        report.append("## 📚 书籍文件详情\n\n")
        report.append("| 书籍 | 预期 | 实际 | 状态 |\n")
        report.append("|------|------|------|------|\n")
        
        for book_name, info in sorted(self.results["books"].items()):
            report.append(f"| {book_name} | {info['expected']} | {info['actual']} | {info['status']} |\n")
        
        report.append("\n---\n")
        
        # 文档详情
        report.append("## 📖 配套文档详情\n\n")
        report.append("| 文档 | 状态 | 大小 |\n")
        report.append("|------|------|------|\n")
        
        for doc_name, info in self.results["docs"].items():
            report.append(f"| {doc_name} | {info['status']} | {info['size']} |\n")
        
        # 问题汇总
        if self.results["missing_files"] or self.results["errors"]:
            report.append("\n---\n")
            report.append("## ⚠️ 问题汇总\n\n")
            
            if self.results["errors"]:
                report.append("### ❌ 错误\n\n")
                for error in self.results["errors"]:
                    report.append(f"- {error}\n")
            
            if self.results["missing_files"]:
                report.append("\n### 📋 缺失文件\n\n")
                for missing in self.results["missing_files"]:
                    report.append(f"- {missing}\n")
        else:
            report.append("\n---\n")
            report.append("## ✅ 完美！没有发现问题\n")
        
        # 保存报告
        report_path = self.workspace / f"验证报告-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(report)
        
        print(f"\n✅ 报告已生成: {report_path}")
        
        # 打印摘要
        print("\n" + "="*60)
        print("📊 验证摘要")
        print("="*60)
        print(f"书籍文件: {total_actual}/{total_expected} ({total_actual/total_expected*100:.1f}%)")
        print(f"完整书籍: {books_ok}/{len(self.expected_books)}")
        print(f"配套文档: {docs_ok}/{len(self.expected_docs)}")
        
        if not self.results["missing_files"] and not self.results["errors"]:
            print("\n🎉 恭喜！项目100%完整！")
        else:
            print(f"\n⚠️ 发现{len(self.results['missing_files'])}个问题")
        
        return report_path
    
    def run(self):
        """运行完整验证"""
        print("\n🔧 15本考研书系列 - 项目完整性验证")
        print("="*60)
        
        self.validate_books()
        self.validate_docs()
        report_path = self.generate_report()
        
        return self.results

def main():
    validator = ProjectValidator()
    results = validator.run()
    
    # 返回状态码
    if not results["missing_files"] and not results["errors"]:
        return 0  # 成功
    else:
        return 1  # 有问题

if __name__ == "__main__":
    exit(main())
