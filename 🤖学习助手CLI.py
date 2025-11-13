#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
15本考研书系列 - 交互式学习助手CLI

功能：
1. 智能学习计划推荐
2. 每日学习提醒
3. 进度查询与统计
4. 学习建议生成
5. 激励与打卡
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

class LearningAssistant:
    def __init__(self):
        self.workspace = Path("/workspace")
        self.data_file = self.workspace / "learning_assistant_data.json"
        self.load_data()
        
        # 15本书清单
        self.books = {
            "1": {"name": "数学一速成手册", "chapters": 10, "difficulty": "中等"},
            "2": {"name": "概率统计指南", "chapters": 10, "difficulty": "中等"},
            "3": {"name": "数值计算方法", "chapters": 10, "difficulty": "难"},
            "4": {"name": "水力学核心100题", "chapters": 10, "difficulty": "中等"},
            "5": {"name": "水力学进阶专题", "chapters": 10, "difficulty": "难"},
            "6": {"name": "工程水文学", "chapters": 10, "difficulty": "中等"},
            "7": {"name": "水文学进阶", "chapters": 10, "difficulty": "难"},
            "8": {"name": "水文学考研冲刺", "chapters": 10, "difficulty": "中等"},
            "9": {"name": "地下水动力学", "chapters": 10, "difficulty": "难"},
            "10": {"name": "生态水力学", "chapters": 10, "difficulty": "中等"},
            "11": {"name": "给排水工程", "chapters": 10, "difficulty": "中等"},
            "12": {"name": "水资源管理", "chapters": 10, "difficulty": "中等"},
            "13": {"name": "水工建筑物", "chapters": 10, "difficulty": "难"},
            "14": {"name": "Python编程实战", "chapters": 10, "difficulty": "中等"},
            "15": {"name": "面试求职指南", "chapters": 10, "difficulty": "简单"},
        }
        
        # 激励语录
        self.motivational_quotes = [
            "💪 坚持就是胜利！今天也要加油！",
            "🌟 每一次努力都不会白费！",
            "🚀 你比想象中更强大！",
            "📚 知识改变命运，学习成就未来！",
            "🎯 专注当下，做好眼前的事！",
            "⭐ 成功属于坚持到最后的人！",
            "💡 今天的努力，明天的收获！",
            "🏆 相信自己，你一定可以！",
            "🌈 困难只是暂时的，成功就在前方！",
            "✨ 每天进步一点点，就是了不起的成就！",
        ]
    
    def load_data(self):
        """加载用户数据"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "user_name": "",
                "start_date": "",
                "goal": "",
                "target_date": "",
                "daily_goal_hours": 4,
                "completed_books": [],
                "completed_chapters": {},
                "study_days": 0,
                "total_hours": 0,
                "last_study_date": "",
                "streak_days": 0,
            }
    
    def save_data(self):
        """保存用户数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def welcome(self):
        """欢迎界面"""
        print("\n" + "="*60)
        print("🤖 15本考研书系列 - 智能学习助手")
        print("="*60)
        
        if not self.data["user_name"]:
            self.initial_setup()
        else:
            print(f"\n👋 欢迎回来，{self.data['user_name']}！")
            self.show_status()
    
    def initial_setup(self):
        """初始设置"""
        print("\n🎉 欢迎使用学习助手！让我们开始设置吧。\n")
        
        # 获取用户信息
        self.data["user_name"] = input("📝 请输入你的名字：").strip() or "学习者"
        
        print("\n🎯 你的学习目标是什么？")
        print("  1. 考研备考")
        print("  2. 工程实践")
        print("  3. 科研深造")
        print("  4. 求职准备")
        goal_choice = input("请选择（1-4）：").strip()
        
        goals = {
            "1": "考研备考",
            "2": "工程实践",
            "3": "科研深造",
            "4": "求职准备"
        }
        self.data["goal"] = goals.get(goal_choice, "系统学习")
        
        # 设置时间
        self.data["start_date"] = datetime.now().strftime("%Y-%m-%d")
        
        print("\n⏰ 你计划用多长时间完成学习？")
        print("  1. 3个月（考研突击）")
        print("  2. 6个月（工程实践）")
        print("  3. 12个月（科研深造）")
        time_choice = input("请选择（1-3）：").strip()
        
        months = {"1": 3, "2": 6, "3": 12}
        target_months = months.get(time_choice, 6)
        target_date = datetime.now() + timedelta(days=target_months*30)
        self.data["target_date"] = target_date.strftime("%Y-%m-%d")
        
        # 每日目标
        print("\n📚 你每天能投入多少小时学习？")
        daily_hours = input("请输入小时数（建议3-5小时）：").strip()
        try:
            self.data["daily_goal_hours"] = float(daily_hours)
        except:
            self.data["daily_goal_hours"] = 4
        
        self.save_data()
        
        print(f"\n✅ 设置完成！{self.data['user_name']}，让我们开始学习之旅吧！")
        print(f"📅 目标日期：{self.data['target_date']}")
        print(f"⏰ 每日目标：{self.data['daily_goal_hours']}小时")
    
    def show_status(self):
        """显示学习状态"""
        print("\n📊 你的学习状态：")
        print(f"  🎯 学习目标：{self.data['goal']}")
        print(f"  📅 已学习：{self.data['study_days']}天")
        print(f"  ⏰ 累计时长：{self.data['total_hours']:.1f}小时")
        print(f"  📚 完成书籍：{len(self.data['completed_books'])}/15本")
        print(f"  🔥 连续打卡：{self.data['streak_days']}天")
        
        # 计算进度
        total_chapters = 150
        completed = sum(len(chapters) for chapters in self.data["completed_chapters"].values())
        progress = completed / total_chapters * 100
        print(f"  📈 整体进度：{progress:.1f}% ({completed}/{total_chapters}章)")
        
        # 距离目标
        if self.data["target_date"]:
            target = datetime.strptime(self.data["target_date"], "%Y-%m-%d")
            days_left = (target - datetime.now()).days
            if days_left > 0:
                print(f"  ⏳ 距离目标：还剩{days_left}天")
            else:
                print(f"  🎉 恭喜！已完成学习计划！")
    
    def main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "="*60)
            print("📋 主菜单")
            print("="*60)
            print("  1. 📝 记录今日学习")
            print("  2. 📊 查看学习进度")
            print("  3. 💡 获取学习建议")
            print("  4. 📚 查看书籍列表")
            print("  5. 🎯 更新学习目标")
            print("  6. 🏆 查看成就徽章")
            print("  7. 💬 获取激励")
            print("  0. 🚪 退出")
            print("="*60)
            
            choice = input("\n请选择功能（0-7）：").strip()
            
            if choice == "1":
                self.record_study()
            elif choice == "2":
                self.show_progress()
            elif choice == "3":
                self.get_suggestions()
            elif choice == "4":
                self.show_books()
            elif choice == "5":
                self.update_goal()
            elif choice == "6":
                self.show_achievements()
            elif choice == "7":
                self.show_motivation()
            elif choice == "0":
                print(f"\n👋 再见，{self.data['user_name']}！明天继续加油！")
                self.save_data()
                break
            else:
                print("\n❌ 无效选择，请重试。")
    
    def record_study(self):
        """记录学习"""
        print("\n📝 记录今日学习")
        print("-"*60)
        
        # 学习时长
        hours = input("今天学习了多少小时？").strip()
        try:
            hours = float(hours)
        except:
            print("❌ 输入无效，请输入数字。")
            return
        
        # 学习内容
        print("\n你学习了哪本书？")
        self.show_books()
        book_id = input("请输入书籍编号（1-15）：").strip()
        
        if book_id not in self.books:
            print("❌ 无效的书籍编号。")
            return
        
        book_name = self.books[book_id]["name"]
        
        # 章节
        chapters = input(f"完成了《{book_name}》的哪些章节？（如：1,2,3）：").strip()
        chapter_list = [c.strip() for c in chapters.split(",") if c.strip()]
        
        # 更新数据
        today = datetime.now().strftime("%Y-%m-%d")
        self.data["total_hours"] += hours
        self.data["study_days"] += 1
        
        # 更新连续天数
        if self.data["last_study_date"]:
            last_date = datetime.strptime(self.data["last_study_date"], "%Y-%m-%d")
            if (datetime.now() - last_date).days == 1:
                self.data["streak_days"] += 1
            elif (datetime.now() - last_date).days > 1:
                self.data["streak_days"] = 1
        else:
            self.data["streak_days"] = 1
        
        self.data["last_study_date"] = today
        
        # 记录章节
        if book_id not in self.data["completed_chapters"]:
            self.data["completed_chapters"][book_id] = []
        
        for chapter in chapter_list:
            if chapter not in self.data["completed_chapters"][book_id]:
                self.data["completed_chapters"][book_id].append(chapter)
        
        # 检查是否完成整本书
        if len(self.data["completed_chapters"][book_id]) >= self.books[book_id]["chapters"]:
            if book_id not in self.data["completed_books"]:
                self.data["completed_books"].append(book_id)
                print(f"\n🎉 恭喜！你完成了《{book_name}》！")
        
        self.save_data()
        
        # 显示鼓励
        print(f"\n✅ 记录成功！")
        print(f"  今日学习：{hours}小时")
        print(f"  累计：{self.data['total_hours']:.1f}小时")
        print(f"  连续打卡：{self.data['streak_days']}天")
        
        # 检查成就
        self.check_achievements()
        
        # 激励
        print(f"\n{random.choice(self.motivational_quotes)}")
    
    def show_progress(self):
        """显示详细进度"""
        print("\n📊 详细学习进度")
        print("="*60)
        
        for book_id, book_info in self.books.items():
            book_name = book_info["name"]
            total_chapters = book_info["chapters"]
            completed = self.data["completed_chapters"].get(book_id, [])
            completed_count = len(completed)
            progress = completed_count / total_chapters * 100
            
            # 状态图标
            if book_id in self.data["completed_books"]:
                status = "✅"
            elif completed_count > 0:
                status = "🔄"
            else:
                status = "📝"
            
            # 进度条
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"{status} {book_id:2s}. {book_name:20s} [{bar}] {progress:5.1f}% ({completed_count}/{total_chapters})")
        
        # 总体统计
        total_completed = sum(len(chapters) for chapters in self.data["completed_chapters"].values())
        total_chapters = 150
        overall_progress = total_completed / total_chapters * 100
        
        print("-"*60)
        print(f"📈 总体进度：{overall_progress:.1f}% ({total_completed}/{total_chapters}章)")
        print(f"📚 完成书籍：{len(self.data['completed_books'])}/15本")
    
    def get_suggestions(self):
        """获取学习建议"""
        print("\n💡 智能学习建议")
        print("="*60)
        
        # 分析学习情况
        total_completed = sum(len(chapters) for chapters in self.data["completed_chapters"].values())
        progress = total_completed / 150 * 100
        
        # 计算日均时长
        if self.data["study_days"] > 0:
            avg_hours = self.data["total_hours"] / self.data["study_days"]
        else:
            avg_hours = 0
        
        # 生成建议
        suggestions = []
        
        # 进度建议
        if progress < 30:
            suggestions.append("📚 建议加快学习进度，每周完成2-3章")
        elif progress < 60:
            suggestions.append("✅ 学习进度良好，保持当前节奏")
        else:
            suggestions.append("🌟 进度优秀！注意复习已学内容")
        
        # 时长建议
        if avg_hours < 2:
            suggestions.append("⏰ 日均学习时长偏低，建议增加到3-4小时")
        elif avg_hours < 4:
            suggestions.append("⏰ 学习时长合适，继续保持")
        else:
            suggestions.append("💪 学习时长充足，注意劳逸结合")
        
        # 连续性建议
        if self.data["streak_days"] < 7:
            suggestions.append("📅 建议每天坚持学习，培养学习习惯")
        elif self.data["streak_days"] < 30:
            suggestions.append(f"🔥 已连续学习{self.data['streak_days']}天，继续保持！")
        else:
            suggestions.append(f"🏆 连续学习{self.data['streak_days']}天！坚持就是胜利！")
        
        # 推荐下一本书
        uncompleted_books = [bid for bid in self.books.keys() 
                            if bid not in self.data["completed_books"]]
        
        if uncompleted_books:
            # 根据难度和前置知识推荐
            if progress < 20:
                # 初期推荐基础书籍
                recommended = [bid for bid in ["1", "2", "4", "6"] 
                             if bid in uncompleted_books]
            elif progress < 60:
                # 中期推荐中等难度
                recommended = [bid for bid in ["5", "7", "10", "11", "12"] 
                             if bid in uncompleted_books]
            else:
                # 后期推荐难度较高的
                recommended = [bid for bid in ["3", "9", "13", "14"] 
                             if bid in uncompleted_books]
            
            if recommended:
                next_book_id = recommended[0]
                next_book = self.books[next_book_id]["name"]
                suggestions.append(f"📖 建议下一本学习：《{next_book}》")
        
        # 显示建议
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        # 学习计划
        if self.data["target_date"]:
            target = datetime.strptime(self.data["target_date"], "%Y-%m-%d")
            days_left = (target - datetime.now()).days
            chapters_left = 150 - total_completed
            
            if days_left > 0 and chapters_left > 0:
                chapters_per_day = chapters_left / days_left
                print(f"\n📋 学习计划：")
                print(f"  • 剩余时间：{days_left}天")
                print(f"  • 剩余章节：{chapters_left}章")
                print(f"  • 建议进度：每天{chapters_per_day:.1f}章")
    
    def show_books(self):
        """显示书籍列表"""
        print("\n📚 书籍列表")
        print("-"*60)
        for book_id, book_info in self.books.items():
            status = "✅" if book_id in self.data["completed_books"] else "  "
            print(f"{status} {book_id:2s}. {book_info['name']:20s} (难度：{book_info['difficulty']})")
    
    def update_goal(self):
        """更新学习目标"""
        print("\n🎯 更新学习目标")
        print("-"*60)
        print(f"当前目标：{self.data['goal']}")
        print(f"目标日期：{self.data['target_date']}")
        print(f"每日目标：{self.data['daily_goal_hours']}小时")
        
        if input("\n是否修改目标？(y/n): ").lower() == 'y':
            self.initial_setup()
    
    def show_achievements(self):
        """显示成就徽章"""
        print("\n🏆 成就徽章")
        print("="*60)
        
        achievements = []
        
        # 学习时长成就
        hours = self.data["total_hours"]
        if hours >= 100:
            achievements.append("🌟 学习达人：累计学习100+小时")
        if hours >= 300:
            achievements.append("💎 学习大师：累计学习300+小时")
        if hours >= 500:
            achievements.append("👑 学习之王：累计学习500+小时")
        
        # 连续打卡成就
        streak = self.data["streak_days"]
        if streak >= 7:
            achievements.append("🔥 坚持不懈：连续打卡7天")
        if streak >= 30:
            achievements.append("💪 铁人意志：连续打卡30天")
        if streak >= 100:
            achievements.append("🚀 传奇学者：连续打卡100天")
        
        # 完成书籍成就
        completed = len(self.data["completed_books"])
        if completed >= 1:
            achievements.append("📖 初学乍成：完成第1本书")
        if completed >= 5:
            achievements.append("📚 学有所成：完成5本书")
        if completed >= 10:
            achievements.append("🎓 博学多才：完成10本书")
        if completed >= 15:
            achievements.append("🏆 满分成就：完成所有15本书！")
        
        # 学习天数成就
        days = self.data["study_days"]
        if days >= 30:
            achievements.append("📅 月度勋章：学习满30天")
        if days >= 100:
            achievements.append("📆 百日勋章：学习满100天")
        
        if achievements:
            for achievement in achievements:
                print(f"  {achievement}")
        else:
            print("  暂无成就，继续加油！")
            print("\n  💡 提示：")
            print("     • 学习100小时可获得第一个成就")
            print("     • 连续打卡7天可获得坚持成就")
            print("     • 完成第1本书可获得学习成就")
    
    def check_achievements(self):
        """检查是否解锁新成就"""
        # 这里可以在记录学习后检查是否解锁新成就
        # 并给出即时反馈
        
        if self.data["total_hours"] == 100:
            print("\n🎉 解锁成就：学习达人！累计学习100小时！")
        
        if self.data["streak_days"] == 7:
            print("\n🎉 解锁成就：坚持不懈！连续打卡7天！")
        
        if len(self.data["completed_books"]) == 1:
            print("\n🎉 解锁成就：初学乍成！完成第1本书！")
    
    def show_motivation(self):
        """显示激励语录"""
        print("\n💬 每日激励")
        print("="*60)
        
        # 随机选择3条激励语录
        quotes = random.sample(self.motivational_quotes, min(3, len(self.motivational_quotes)))
        
        for quote in quotes:
            print(f"\n  {quote}")
        
        # 根据进度给出特定激励
        total_completed = sum(len(chapters) for chapters in self.data["completed_chapters"].values())
        progress = total_completed / 150 * 100
        
        print(f"\n📊 你已经完成了{progress:.1f}%的学习内容！")
        
        if progress < 25:
            print("  💪 万事开头难，坚持下去就是胜利！")
        elif progress < 50:
            print("  🚀 已经完成四分之一，继续加油！")
        elif progress < 75:
            print("  🌟 过半了！胜利就在前方！")
        else:
            print("  🏆 最后冲刺阶段，加油完成！")

def main():
    """主程序"""
    assistant = LearningAssistant()
    assistant.welcome()
    assistant.main_menu()

if __name__ == "__main__":
    main()
