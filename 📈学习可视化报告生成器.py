#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
15本考研书系列 - 学习可视化报告生成器

功能：
1. 生成精美的学习报告
2. 创建多种可视化图表
3. 导出HTML/Markdown格式
4. 生成学习证书
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random

class VisualizationReportGenerator:
    def __init__(self):
        self.workspace = Path("/workspace")
        self.data_file = self.workspace / "learning_data.json"
        self.load_data()
    
    def load_data(self):
        """加载学习数据"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            print("⚠️ 未找到学习数据，请先使用学习数据分析工具记录数据")
            self.data = {}
    
    def generate_html_report(self):
        """生成HTML格式报告"""
        if not self.data:
            return
        
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='zh-CN'>")
        html.append("<head>")
        html.append("    <meta charset='UTF-8'>")
        html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append("    <title>学习成果报告</title>")
        html.append("    <style>")
        html.append("        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }")
        html.append("        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }")
        html.append("        h1 { color: #667eea; text-align: center; font-size: 36px; margin-bottom: 10px; }")
        html.append("        .subtitle { text-align: center; color: #666; font-size: 18px; margin-bottom: 40px; }")
        html.append("        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }")
        html.append("        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }")
        html.append("        .stat-number { font-size: 48px; font-weight: bold; margin: 10px 0; }")
        html.append("        .stat-label { font-size: 16px; opacity: 0.9; }")
        html.append("        .progress-section { margin: 40px 0; }")
        html.append("        .progress-item { margin: 20px 0; }")
        html.append("        .progress-bar { width: 100%; height: 30px; background: #f0f0f0; border-radius: 15px; overflow: hidden; position: relative; }")
        html.append("        .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); transition: width 0.5s; }")
        html.append("        .progress-text { position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%); text-align: center; font-weight: bold; color: #333; }")
        html.append("        .achievement-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }")
        html.append("        .achievement-badge { background: #f8f9fa; border: 2px solid #667eea; border-radius: 10px; padding: 20px; text-align: center; transition: transform 0.3s; }")
        html.append("        .achievement-badge:hover { transform: translateY(-5px); }")
        html.append("        .badge-icon { font-size: 48px; }")
        html.append("        .badge-name { font-size: 14px; color: #666; margin-top: 10px; }")
        html.append("        .footer { text-align: center; color: #999; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }")
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")
        html.append("    <div class='container'>")
        
        # 标题
        html.append("        <h1>🎓 学习成果报告</h1>")
        html.append(f"        <div class='subtitle'>生成时间：{datetime.now().strftime('%Y年%m月%d日')}</div>")
        
        # 统计卡片
        stats = self.calculate_stats()
        html.append("        <div class='stats'>")
        html.append(f"            <div class='stat-card'>")
        html.append(f"                <div class='stat-label'>📚 完成书籍</div>")
        html.append(f"                <div class='stat-number'>{stats['books_completed']}</div>")
        html.append(f"                <div class='stat-label'>/ 15本</div>")
        html.append(f"            </div>")
        html.append(f"            <div class='stat-card'>")
        html.append(f"                <div class='stat-label'>⏰ 学习时长</div>")
        html.append(f"                <div class='stat-number'>{stats['total_hours']:.0f}</div>")
        html.append(f"                <div class='stat-label'>小时</div>")
        html.append(f"            </div>")
        html.append(f"            <div class='stat-card'>")
        html.append(f"                <div class='stat-label'>📅 学习天数</div>")
        html.append(f"                <div class='stat-number'>{stats['study_days']}</div>")
        html.append(f"                <div class='stat-label'>天</div>")
        html.append(f"            </div>")
        html.append(f"            <div class='stat-card'>")
        html.append(f"                <div class='stat-label'>📈 整体进度</div>")
        html.append(f"                <div class='stat-number'>{stats['progress']:.0f}%</div>")
        html.append(f"                <div class='stat-label'>完成度</div>")
        html.append(f"            </div>")
        html.append("        </div>")
        
        # 书籍进度
        html.append("        <div class='progress-section'>")
        html.append("            <h2>📚 书籍学习进度</h2>")
        
        books = self.get_books_progress()
        for book_name, progress in books:
            html.append(f"            <div class='progress-item'>")
            html.append(f"                <div style='margin-bottom: 5px;'>{book_name}</div>")
            html.append(f"                <div class='progress-bar'>")
            html.append(f"                    <div class='progress-fill' style='width: {progress}%'></div>")
            html.append(f"                    <div class='progress-text'>{progress:.0f}%</div>")
            html.append(f"                </div>")
            html.append(f"            </div>")
        
        html.append("        </div>")
        
        # 成就徽章
        achievements = self.get_achievements()
        if achievements:
            html.append("        <div class='progress-section'>")
            html.append("            <h2>🏆 成就徽章</h2>")
            html.append("            <div class='achievement-grid'>")
            
            for achievement in achievements:
                html.append(f"                <div class='achievement-badge'>")
                html.append(f"                    <div class='badge-icon'>{achievement['icon']}</div>")
                html.append(f"                    <div class='badge-name'>{achievement['name']}</div>")
                html.append(f"                </div>")
            
            html.append("            </div>")
            html.append("        </div>")
        
        # 页脚
        html.append("        <div class='footer'>")
        html.append("            <p>💪 坚持就是胜利！继续加油！</p>")
        html.append("            <p>📚 15本考研书系列 · 学习可视化报告</p>")
        html.append("        </div>")
        
        html.append("    </div>")
        html.append("</body>")
        html.append("</html>")
        
        # 保存HTML
        report_path = self.workspace / f"学习报告-{datetime.now().strftime('%Y%m%d')}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))
        
        print(f"✅ HTML报告已生成: {report_path}")
        print(f"💡 用浏览器打开查看精美报告")
        
        return report_path
    
    def generate_certificate(self):
        """生成学习证书"""
        stats = self.calculate_stats()
        
        # 简化版证书（Markdown格式）
        cert = []
        cert.append("```")
        cert.append("╔═══════════════════════════════════════════════════════════╗")
        cert.append("║                                                           ║")
        cert.append("║                  🎓 学习成就证书                          ║")
        cert.append("║                                                           ║")
        cert.append("║  ═══════════════════════════════════════════════════    ║")
        cert.append("║                                                           ║")
        cert.append(f"║      特此证明                                             ║")
        cert.append("║                                                           ║")
        cert.append(f"║      已完成 {stats['books_completed']}本 考研书系列学习                       ║")
        cert.append(f"║      累计学习 {stats['total_hours']:.0f}小时                              ║")
        cert.append(f"║      学习天数 {stats['study_days']}天                                 ║")
        cert.append(f"║      整体进度 {stats['progress']:.0f}%                                 ║")
        cert.append("║                                                           ║")
        cert.append("║      学习项目：15本考研书系列                             ║")
        cert.append("║                                                           ║")
        cert.append(f"║      颁发日期：{datetime.now().strftime('%Y年%m月%d日')}                        ║")
        cert.append("║                                                           ║")
        cert.append("║  ═══════════════════════════════════════════════════    ║")
        cert.append("║                                                           ║")
        cert.append("║                    💪 坚持就是胜利！                      ║")
        cert.append("║                                                           ║")
        cert.append("╚═══════════════════════════════════════════════════════════╝")
        cert.append("```")
        
        cert_path = self.workspace / f"学习证书-{datetime.now().strftime('%Y%m%d')}.md"
        with open(cert_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cert))
        
        print(f"✅ 学习证书已生成: {cert_path}")
        
        # 在终端显示
        print("\n" + '\n'.join(cert))
        
        return cert_path
    
    def calculate_stats(self):
        """计算统计数据"""
        if not self.data:
            return {
                "books_completed": 0,
                "total_hours": 0,
                "study_days": 0,
                "progress": 0
            }
        
        books_completed = len(self.data.get("completed_books", []))
        total_hours = sum(r.get("hours", 0) for r in self.data.get("daily_records", []))
        study_days = len(self.data.get("daily_records", []))
        
        # 计算进度
        total_chapters = 0
        completed_chapters = 0
        for book_info in self.data.get("books", {}).values():
            total_chapters += book_info.get("total_chapters", 10)
            completed_chapters += book_info.get("completed_chapters", 0)
        
        progress = (completed_chapters / max(total_chapters, 1)) * 100
        
        return {
            "books_completed": books_completed,
            "total_hours": total_hours,
            "study_days": study_days,
            "progress": progress
        }
    
    def get_books_progress(self):
        """获取书籍进度"""
        books_progress = []
        
        if "books" in self.data:
            for book_name, book_info in self.data["books"].items():
                total = book_info.get("total_chapters", 10)
                completed = book_info.get("completed_chapters", 0)
                progress = (completed / total) * 100
                books_progress.append((book_name, progress))
        
        return books_progress
    
    def get_achievements(self):
        """获取成就列表"""
        achievements = []
        stats = self.calculate_stats()
        
        # 时长成就
        if stats["total_hours"] >= 100:
            achievements.append({"icon": "🌟", "name": "学习达人"})
        if stats["total_hours"] >= 300:
            achievements.append({"icon": "💎", "name": "学习大师"})
        
        # 书籍成就
        if stats["books_completed"] >= 1:
            achievements.append({"icon": "📖", "name": "初学乍成"})
        if stats["books_completed"] >= 5:
            achievements.append({"icon": "📚", "name": "学有所成"})
        if stats["books_completed"] >= 10:
            achievements.append({"icon": "🎓", "name": "博学多才"})
        
        # 进度成就
        if stats["progress"] >= 50:
            achievements.append({"icon": "⭐", "name": "半程勋章"})
        if stats["progress"] >= 100:
            achievements.append({"icon": "🏆", "name": "完美达成"})
        
        return achievements
    
    def main_menu(self):
        """主菜单"""
        print("\n" + "="*60)
        print("📈 学习可视化报告生成器")
        print("="*60)
        
        while True:
            print("\n📋 功能菜单")
            print("-"*60)
            print("  1. 📊 生成HTML精美报告")
            print("  2. 🎓 生成学习证书")
            print("  3. 📈 查看统计数据")
            print("  0. 🚪 退出")
            print("-"*60)
            
            choice = input("\n请选择功能（0-3）：").strip()
            
            if choice == "1":
                self.generate_html_report()
            elif choice == "2":
                self.generate_certificate()
            elif choice == "3":
                stats = self.calculate_stats()
                print("\n📊 学习统计")
                print("-"*60)
                print(f"完成书籍：{stats['books_completed']}/15本")
                print(f"学习时长：{stats['total_hours']:.1f}小时")
                print(f"学习天数：{stats['study_days']}天")
                print(f"整体进度：{stats['progress']:.1f}%")
            elif choice == "0":
                print("\n👋 再见！")
                break
            else:
                print("\n❌ 无效选择，请重试。")

def main():
    """主程序"""
    generator = VisualizationReportGenerator()
    generator.main_menu()

if __name__ == "__main__":
    main()
