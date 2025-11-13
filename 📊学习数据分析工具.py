#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
15本考研书系列 - 学习数据分析工具

功能：
1. 记录学习时间
2. 统计学习进度
3. 生成可视化图表
4. 分析学习效率
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'WenQuanYi Micro Hei']
matplotlib.rcParams['axes.unicode_minus'] = False

class LearningTracker:
    def __init__(self, data_file="learning_data.json"):
        self.data_file = Path(data_file)
        self.data = self.load_data()
        
    def load_data(self):
        """加载学习数据"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "daily_records": [],
                "books": {},
                "projects": {},
                "goals": []
            }
    
    def save_data(self):
        """保存学习数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存到: {self.data_file}")
    
    def add_daily_record(self, date, hours, content, notes=""):
        """添加每日学习记录"""
        record = {
            "date": date,
            "hours": hours,
            "content": content,
            "notes": notes
        }
        self.data["daily_records"].append(record)
        print(f"✅ 已添加 {date} 的学习记录（{hours}小时）")
    
    def update_book_progress(self, book_name, chapters_completed):
        """更新书籍学习进度"""
        if book_name not in self.data["books"]:
            self.data["books"][book_name] = {
                "total_chapters": 10,
                "completed_chapters": 0,
                "start_date": datetime.now().strftime("%Y-%m-%d")
            }
        
        self.data["books"][book_name]["completed_chapters"] = chapters_completed
        self.data["books"][book_name]["last_update"] = datetime.now().strftime("%Y-%m-%d")
        
        progress = chapters_completed / self.data["books"][book_name]["total_chapters"] * 100
        print(f"✅ {book_name} 进度更新: {chapters_completed}/10章 ({progress:.1f}%)")
    
    def update_project_status(self, project_name, status, code_lines=0):
        """更新项目状态"""
        self.data["projects"][project_name] = {
            "status": status,
            "code_lines": code_lines,
            "last_update": datetime.now().strftime("%Y-%m-%d")
        }
        print(f"✅ {project_name} 状态更新: {status}")
    
    def get_statistics(self):
        """获取学习统计"""
        total_hours = sum(r["hours"] for r in self.data["daily_records"])
        total_days = len(self.data["daily_records"])
        avg_hours = total_hours / total_days if total_days > 0 else 0
        
        books_completed = sum(1 for b in self.data["books"].values() 
                            if b["completed_chapters"] >= b["total_chapters"])
        books_total = len(self.data["books"])
        
        projects_completed = sum(1 for p in self.data["projects"].values() 
                               if p["status"] == "completed")
        projects_total = len(self.data["projects"])
        
        return {
            "total_hours": total_hours,
            "total_days": total_days,
            "avg_hours_per_day": avg_hours,
            "books_completed": books_completed,
            "books_total": books_total,
            "projects_completed": projects_completed,
            "projects_total": projects_total
        }
    
    def plot_daily_hours(self, save_path="学习时长统计.png"):
        """绘制每日学习时长"""
        if not self.data["daily_records"]:
            print("⚠️ 暂无学习记录")
            return
        
        dates = [r["date"] for r in self.data["daily_records"][-30:]]  # 最近30天
        hours = [r["hours"] for r in self.data["daily_records"][-30:]]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(range(len(dates)), hours, color='#3498db', alpha=0.7)
        ax.axhline(y=np.mean(hours), color='r', linestyle='--', 
                  label=f'平均: {np.mean(hours):.1f}小时/天')
        
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('学习时长（小时）', fontsize=12)
        ax.set_title('每日学习时长统计（最近30天）', fontsize=14, fontweight='bold')
        ax.set_xticks(range(0, len(dates), max(1, len(dates)//10)))
        ax.set_xticklabels([dates[i] for i in range(0, len(dates), max(1, len(dates)//10))], 
                          rotation=45)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 图表已保存: {save_path}")
        plt.close()
    
    def plot_book_progress(self, save_path="书籍学习进度.png"):
        """绘制书籍学习进度"""
        if not self.data["books"]:
            print("⚠️ 暂无书籍记录")
            return
        
        books = list(self.data["books"].keys())
        progress = [b["completed_chapters"] / b["total_chapters"] * 100 
                   for b in self.data["books"].values()]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#2ecc71' if p >= 100 else '#3498db' if p >= 50 else '#e74c3c' 
                 for p in progress]
        bars = ax.barh(books, progress, color=colors, alpha=0.7)
        
        # 添加百分比标签
        for i, (bar, p) in enumerate(zip(bars, progress)):
            ax.text(p + 2, i, f'{p:.0f}%', va='center', fontsize=10)
        
        ax.set_xlabel('完成度（%）', fontsize=12)
        ax.set_title('书籍学习进度', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 110)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 图表已保存: {save_path}")
        plt.close()
    
    def plot_overall_progress(self, save_path="整体学习进度.png"):
        """绘制整体学习进度饼图"""
        stats = self.get_statistics()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 书籍完成情况
        books_data = [stats["books_completed"], 
                     stats["books_total"] - stats["books_completed"]]
        ax1.pie(books_data, labels=['已完成', '进行中'], autopct='%1.1f%%',
               colors=['#2ecc71', '#95a5a6'], startangle=90)
        ax1.set_title(f'书籍完成情况\n({stats["books_completed"]}/{stats["books_total"]}本)', 
                     fontsize=12, fontweight='bold')
        
        # 项目完成情况
        projects_data = [stats["projects_completed"], 
                        stats["projects_total"] - stats["projects_completed"]]
        ax2.pie(projects_data, labels=['已完成', '进行中'], autopct='%1.1f%%',
               colors=['#3498db', '#95a5a6'], startangle=90)
        ax2.set_title(f'项目完成情况\n({stats["projects_completed"]}/{stats["projects_total"]}个)', 
                     fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 图表已保存: {save_path}")
        plt.close()
    
    def generate_report(self):
        """生成学习报告"""
        stats = self.get_statistics()
        
        report = []
        report.append("# 📊 学习数据分析报告\n")
        report.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**学习开始日期**: {self.data['start_date']}\n")
        
        # 计算学习天数
        start = datetime.strptime(self.data['start_date'], '%Y-%m-%d')
        days_since_start = (datetime.now() - start).days + 1
        report.append(f"**累计天数**: {days_since_start}天\n")
        report.append("\n---\n\n")
        
        # 时间统计
        report.append("## ⏰ 时间统计\n\n")
        report.append(f"- 总学习时长: **{stats['total_hours']:.1f}小时**\n")
        report.append(f"- 实际学习天数: **{stats['total_days']}天**\n")
        report.append(f"- 日均学习时长: **{stats['avg_hours_per_day']:.1f}小时/天**\n")
        report.append(f"- 学习连续性: **{stats['total_days']/days_since_start*100:.1f}%**\n")
        report.append("\n")
        
        # 进度统计
        report.append("## 📚 进度统计\n\n")
        report.append(f"- 完成书籍: **{stats['books_completed']}/{stats['books_total']}本** "
                     f"({stats['books_completed']/max(stats['books_total'],1)*100:.1f}%)\n")
        report.append(f"- 完成项目: **{stats['projects_completed']}/{stats['projects_total']}个** "
                     f"({stats['projects_completed']/max(stats['projects_total'],1)*100:.1f}%)\n")
        report.append("\n")
        
        # 书籍详情
        if self.data["books"]:
            report.append("## 📖 书籍学习详情\n\n")
            report.append("| 书籍 | 进度 | 完成度 | 状态 |\n")
            report.append("|------|------|--------|------|\n")
            
            for book, info in self.data["books"].items():
                progress = info["completed_chapters"] / info["total_chapters"] * 100
                status = "✅ 完成" if progress >= 100 else "🔄 进行中" if progress > 0 else "📝 未开始"
                report.append(f"| {book} | {info['completed_chapters']}/{info['total_chapters']}章 | "
                            f"{progress:.0f}% | {status} |\n")
            report.append("\n")
        
        # 项目详情
        if self.data["projects"]:
            report.append("## 💻 项目开发详情\n\n")
            report.append("| 项目 | 状态 | 代码量 | 最后更新 |\n")
            report.append("|------|------|--------|----------|\n")
            
            for project, info in self.data["projects"].items():
                status_icon = "✅" if info["status"] == "completed" else "🔄" if info["status"] == "in_progress" else "📝"
                report.append(f"| {project} | {status_icon} {info['status']} | "
                            f"{info['code_lines']}行 | {info['last_update']} |\n")
            report.append("\n")
        
        # 最近学习记录
        if self.data["daily_records"]:
            report.append("## 📅 最近学习记录（最近7天）\n\n")
            report.append("| 日期 | 时长 | 学习内容 | 备注 |\n")
            report.append("|------|------|----------|------|\n")
            
            for record in self.data["daily_records"][-7:]:
                report.append(f"| {record['date']} | {record['hours']}h | "
                            f"{record['content']} | {record.get('notes', '')} |\n")
            report.append("\n")
        
        # 学习建议
        report.append("## 💡 学习分析与建议\n\n")
        
        if stats['avg_hours_per_day'] < 2:
            report.append("- ⚠️ 日均学习时长偏低，建议增加到3-4小时/天\n")
        elif stats['avg_hours_per_day'] < 4:
            report.append("- ✅ 学习时长适中，保持当前节奏\n")
        else:
            report.append("- 🌟 学习时长充足，注意劳逸结合\n")
        
        if stats['books_total'] > 0 and stats['books_completed'] / stats['books_total'] < 0.3:
            report.append("- 📚 建议加快学习进度，每周至少完成1本书的2-3章\n")
        
        if stats['total_days'] / days_since_start < 0.7:
            report.append("- 📅 学习连续性有待提高，建议每天坚持学习\n")
        
        report.append("\n---\n\n")
        report.append("*本报告由学习数据分析工具自动生成*\n")
        
        # 保存报告
        report_path = Path(f"学习报告-{datetime.now().strftime('%Y%m%d')}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(report)
        
        print(f"✅ 学习报告已生成: {report_path}")
        return report_path

def demo():
    """演示功能"""
    print("\n🎓 15本考研书系列 - 学习数据分析工具")
    print("="*60)
    
    tracker = LearningTracker()
    
    # 添加示例数据
    print("\n📝 添加示例学习记录...")
    today = datetime.now()
    for i in range(30):
        date = (today - timedelta(days=29-i)).strftime("%Y-%m-%d")
        hours = np.random.uniform(2, 6)
        tracker.add_daily_record(date, hours, f"学习Day{i+1}", "正常")
    
    # 更新书籍进度
    print("\n📚 更新书籍进度...")
    books = [
        ("hydraulics-core-100", 10),
        ("math-quick", 8),
        ("probability-stats-guide", 6),
        ("ecohydraulics", 4),
        ("groundwater", 2),
    ]
    for book, chapters in books:
        tracker.update_book_progress(book, chapters)
    
    # 更新项目状态
    print("\n💻 更新项目状态...")
    projects = [
        ("静水压力计算器", "completed", 200),
        ("伯努利方程求解器", "completed", 300),
        ("管道水力计算器", "in_progress", 250),
        ("明渠水力计算器", "pending", 0),
    ]
    for project, status, lines in projects:
        tracker.update_project_status(project, status, lines)
    
    # 保存数据
    tracker.save_data()
    
    # 生成统计
    print("\n📊 学习统计...")
    stats = tracker.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 生成图表
    print("\n📈 生成可视化图表...")
    tracker.plot_daily_hours()
    tracker.plot_book_progress()
    tracker.plot_overall_progress()
    
    # 生成报告
    print("\n📋 生成学习报告...")
    tracker.generate_report()
    
    print("\n✅ 演示完成！")
    print("\n💡 使用方法:")
    print("  1. tracker = LearningTracker()")
    print("  2. tracker.add_daily_record('2025-11-12', 4, '学习水力学')")
    print("  3. tracker.update_book_progress('hydraulics-core-100', 5)")
    print("  4. tracker.save_data()")
    print("  5. tracker.generate_report()")

if __name__ == "__main__":
    demo()
