#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
15本考研书系列 - 学习提醒系统

功能：
1. 设置学习提醒时间
2. 检查今日是否已学习
3. 生成每日学习计划
4. 发送学习提醒（终端显示）
"""

import json
from datetime import datetime, time, timedelta
from pathlib import Path
import os

class StudyReminder:
    def __init__(self):
        self.config_file = Path("/workspace/study_reminder_config.json")
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "reminder_times": ["09:00", "14:00", "19:00"],
                "daily_plan": [],
                "last_check": "",
                "enabled": True,
                "study_hours_goal": 4,
                "break_interval": 25,  # 番茄工作法：25分钟
            }
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def setup_reminders(self):
        """设置提醒时间"""
        print("\n⏰ 设置学习提醒时间")
        print("="*60)
        print("当前提醒时间：")
        for i, t in enumerate(self.config["reminder_times"], 1):
            print(f"  {i}. {t}")
        
        if input("\n是否修改提醒时间？(y/n): ").lower() == 'y':
            print("\n请输入新的提醒时间（24小时制，如：09:00）")
            print("输入'done'结束")
            
            new_times = []
            while True:
                time_input = input(f"提醒时间{len(new_times)+1}（或输入done）: ").strip()
                if time_input.lower() == 'done':
                    break
                
                # 验证时间格式
                try:
                    datetime.strptime(time_input, "%H:%M")
                    new_times.append(time_input)
                except:
                    print("❌ 时间格式错误，请使用HH:MM格式")
            
            if new_times:
                self.config["reminder_times"] = sorted(new_times)
                print(f"\n✅ 已设置{len(new_times)}个提醒时间")
                self.save_config()
    
    def generate_daily_plan(self):
        """生成每日学习计划"""
        print("\n📋 生成每日学习计划")
        print("="*60)
        
        print("今天计划学习哪些内容？")
        print("（输入书籍编号和章节，如：1-2表示第1本书第2章）")
        print("输入'done'结束")
        
        plan = []
        while True:
            item = input(f"学习内容{len(plan)+1}（或输入done）: ").strip()
            if item.lower() == 'done':
                break
            
            plan.append({
                "content": item,
                "completed": False,
                "start_time": "",
                "end_time": ""
            })
        
        self.config["daily_plan"] = plan
        self.config["last_check"] = datetime.now().strftime("%Y-%m-%d")
        self.save_config()
        
        print(f"\n✅ 今日计划已设置（{len(plan)}项）")
        self.show_daily_plan()
    
    def show_daily_plan(self):
        """显示每日计划"""
        if not self.config["daily_plan"]:
            print("\n📋 今日暂无学习计划")
            return
        
        print("\n📋 今日学习计划")
        print("-"*60)
        
        for i, item in enumerate(self.config["daily_plan"], 1):
            status = "✅" if item["completed"] else "⬜"
            content = item["content"]
            
            time_info = ""
            if item["start_time"]:
                time_info = f" ({item['start_time']}"
                if item["end_time"]:
                    time_info += f" - {item['end_time']})"
                else:
                    time_info += " - 进行中)"
            
            print(f"{status} {i}. {content}{time_info}")
        
        # 统计
        completed = sum(1 for item in self.config["daily_plan"] if item["completed"])
        total = len(self.config["daily_plan"])
        progress = completed / total * 100 if total > 0 else 0
        
        print("-"*60)
        print(f"完成度：{completed}/{total} ({progress:.0f}%)")
    
    def mark_completed(self):
        """标记任务完成"""
        self.show_daily_plan()
        
        if not self.config["daily_plan"]:
            return
        
        try:
            item_num = int(input("\n请输入要标记完成的任务编号："))
            if 1 <= item_num <= len(self.config["daily_plan"]):
                self.config["daily_plan"][item_num-1]["completed"] = True
                self.config["daily_plan"][item_num-1]["end_time"] = datetime.now().strftime("%H:%M")
                self.save_config()
                print(f"\n✅ 任务{item_num}已标记完成！")
                
                # 检查是否全部完成
                if all(item["completed"] for item in self.config["daily_plan"]):
                    print("\n🎉 恭喜！今日学习计划全部完成！")
                    print(self.get_random_encouragement())
            else:
                print("❌ 无效的任务编号")
        except:
            print("❌ 输入无效")
    
    def start_pomodoro(self):
        """番茄工作法计时器"""
        print("\n🍅 番茄工作法")
        print("="*60)
        
        print(f"当前设置：{self.config['break_interval']}分钟工作，5分钟休息")
        
        if input("开始番茄钟？(y/n): ").lower() != 'y':
            return
        
        work_minutes = self.config['break_interval']
        
        print(f"\n⏰ 开始工作{work_minutes}分钟...")
        print("（实际使用时这里会有倒计时功能）")
        print(f"💡 提示：专注当前任务，避免干扰")
        
        # 这里可以添加实际的倒计时功能
        # 简化版本，直接显示信息
        
        input("\n按Enter键表示完成工作阶段...")
        
        print("\n✅ 工作阶段完成！")
        print("💚 休息5分钟，放松一下...")
        
        input("\n按Enter键继续...")
        
        print("🔄 准备开始下一个番茄钟")
    
    def check_study_status(self):
        """检查学习状态"""
        print("\n📊 今日学习状态")
        print("="*60)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 检查是否已有今日计划
        if self.config["last_check"] != today:
            print("⚠️ 今日还未设置学习计划")
            if input("是否现在设置？(y/n): ").lower() == 'y':
                self.generate_daily_plan()
            return
        
        # 显示计划
        self.show_daily_plan()
        
        # 当前时间
        current_time = datetime.now().strftime("%H:%M")
        print(f"\n⏰ 当前时间：{current_time}")
        
        # 下一个提醒时间
        next_reminder = None
        for reminder_time in self.config["reminder_times"]:
            if reminder_time > current_time:
                next_reminder = reminder_time
                break
        
        if next_reminder:
            print(f"⏰ 下一次提醒：{next_reminder}")
        else:
            print("⏰ 今日提醒已结束")
    
    def send_reminder(self):
        """发送学习提醒"""
        current_time = datetime.now().strftime("%H:%M")
        
        # 检查是否是提醒时间
        if current_time in self.config["reminder_times"]:
            self.display_reminder()
    
    def display_reminder(self):
        """显示提醒信息"""
        print("\n" + "="*60)
        print("🔔 学习提醒")
        print("="*60)
        print(f"⏰ 时间到了！该学习了！")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # 显示今日计划
        if self.config["daily_plan"]:
            print("\n今日学习计划：")
            for i, item in enumerate(self.config["daily_plan"], 1):
                status = "✅" if item["completed"] else "⬜"
                print(f"  {status} {i}. {item['content']}")
        else:
            print("\n还未设置今日学习计划")
        
        print(f"\n{self.get_random_encouragement()}")
        print("="*60)
    
    def get_random_encouragement(self):
        """获取随机鼓励语"""
        encouragements = [
            "💪 加油！每一次学习都是进步！",
            "🌟 坚持就是胜利！",
            "🚀 你比想象中更强大！",
            "📚 知识改变命运！",
            "⭐ 今天的努力，明天的收获！",
            "💡 专注当下，做好眼前的事！",
            "🏆 相信自己，你一定可以！",
            "✨ 每天进步一点点！",
        ]
        
        import random
        return random.choice(encouragements)
    
    def settings(self):
        """设置"""
        print("\n⚙️ 设置")
        print("="*60)
        print(f"1. 提醒功能：{'开启' if self.config['enabled'] else '关闭'}")
        print(f"2. 每日学习目标：{self.config['study_hours_goal']}小时")
        print(f"3. 番茄钟时长：{self.config['break_interval']}分钟")
        print(f"4. 提醒时间数量：{len(self.config['reminder_times'])}个")
        
        print("\n要修改什么？")
        print("  1. 开启/关闭提醒")
        print("  2. 修改学习目标")
        print("  3. 修改番茄钟时长")
        print("  4. 修改提醒时间")
        print("  0. 返回")
        
        choice = input("\n请选择：").strip()
        
        if choice == "1":
            self.config["enabled"] = not self.config["enabled"]
            status = "开启" if self.config["enabled"] else "关闭"
            print(f"\n✅ 提醒功能已{status}")
            self.save_config()
        
        elif choice == "2":
            hours = input("请输入每日学习目标（小时）：").strip()
            try:
                self.config["study_hours_goal"] = float(hours)
                print(f"\n✅ 每日目标已设置为{hours}小时")
                self.save_config()
            except:
                print("❌ 输入无效")
        
        elif choice == "3":
            minutes = input("请输入番茄钟时长（分钟）：").strip()
            try:
                self.config["break_interval"] = int(minutes)
                print(f"\n✅ 番茄钟时长已设置为{minutes}分钟")
                self.save_config()
            except:
                print("❌ 输入无效")
        
        elif choice == "4":
            self.setup_reminders()
    
    def main_menu(self):
        """主菜单"""
        print("\n" + "="*60)
        print("⏰ 学习提醒系统")
        print("="*60)
        
        while True:
            print("\n📋 主菜单")
            print("-"*60)
            print("  1. 📝 设置今日计划")
            print("  2. 📊 查看学习状态")
            print("  3. ✅ 标记任务完成")
            print("  4. ⏰ 设置提醒时间")
            print("  5. 🍅 番茄工作法")
            print("  6. ⚙️ 设置")
            print("  0. 🚪 退出")
            print("-"*60)
            
            choice = input("\n请选择功能（0-6）：").strip()
            
            if choice == "1":
                self.generate_daily_plan()
            elif choice == "2":
                self.check_study_status()
            elif choice == "3":
                self.mark_completed()
            elif choice == "4":
                self.setup_reminders()
            elif choice == "5":
                self.start_pomodoro()
            elif choice == "6":
                self.settings()
            elif choice == "0":
                print("\n👋 再见！继续加油！")
                break
            else:
                print("\n❌ 无效选择，请重试。")

def main():
    """主程序"""
    reminder = StudyReminder()
    
    # 检查今日计划
    today = datetime.now().strftime("%Y-%m-%d")
    if reminder.config["last_check"] != today:
        print("\n⚠️ 新的一天开始了！")
        if input("是否设置今日学习计划？(y/n): ").lower() == 'y':
            reminder.generate_daily_plan()
    
    # 进入主菜单
    reminder.main_menu()

if __name__ == "__main__":
    main()
