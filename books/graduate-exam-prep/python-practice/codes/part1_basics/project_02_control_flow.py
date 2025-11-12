#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目2: Python控制流程

课程目标：
1. 掌握条件语句（if-elif-else）
2. 掌握for循环和while循环
3. 学习循环控制（break, continue）
4. 应用于洪水等级判别系统

工程案例：
开发一个洪水预警系统，根据水位自动判别洪水等级并发布预警

作者：Python编程实战教材组
日期：2025-11-12
"""

def demonstrate_if_else():
    """演示if-elif-else条件语句"""
    print("="*60)
    print("1. 条件语句 (if-elif-else)")
    print("="*60)
    
    # 单个水位判别
    water_level = 125.68
    warning_level = 120.0
    alert_level = 125.0
    danger_level = 130.0
    
    print(f"\n水位判别系统：")
    print(f"  当前水位: {water_level} m")
    print(f"  警戒水位: {warning_level} m")
    print(f"  预警水位: {alert_level} m")
    print(f"  危险水位: {danger_level} m")
    
    print(f"\n水位等级判别：")
    if water_level < warning_level:
        level = "正常"
        color = "绿色"
        action = "正常监测"
    elif water_level < alert_level:
        level = "警戒"
        color = "黄色"
        action = "加密监测"
    elif water_level < danger_level:
        level = "预警"
        color = "橙色"
        action = "启动预案"
    else:
        level = "危险"
        color = "红色"
        action = "紧急响应"
    
    print(f"  等级: {level}")
    print(f"  预警颜色: {color}")
    print(f"  建议措施: {action}")
    
    return level, action


def demonstrate_for_loop():
    """演示for循环"""
    print("\n" + "="*60)
    print("2. for循环 - 遍历序列")
    print("="*60)
    
    # 多日水位数据分析
    dates = ['2024-01-11', '2024-01-12', '2024-01-13', '2024-01-14', '2024-01-15']
    water_levels = [118.5, 122.3, 126.8, 131.2, 128.5]
    warning_level = 120.0
    alert_level = 125.0
    danger_level = 130.0
    
    print(f"\n连续5日水位分析：")
    print(f"{'日期':<15} {'水位(m)':<12} {'等级':<8} {'预警'}")
    print("-" * 60)
    
    warning_days = 0
    alert_days = 0
    danger_days = 0
    
    for i in range(len(dates)):
        date = dates[i]
        level = water_levels[i]
        
        if level < warning_level:
            status = "正常"
            warning = "✓"
        elif level < alert_level:
            status = "警戒"
            warning = "⚠"
            warning_days += 1
        elif level < danger_level:
            status = "预警"
            warning = "⚠⚠"
            alert_days += 1
        else:
            status = "危险"
            warning = "⚠⚠⚠"
            danger_days += 1
        
        print(f"{date:<15} {level:<12.2f} {status:<8} {warning}")
    
    print(f"\n统计结果：")
    print(f"  正常天数: {5 - warning_days - alert_days - danger_days} 天")
    print(f"  警戒天数: {warning_days} 天")
    print(f"  预警天数: {alert_days} 天")
    print(f"  危险天数: {danger_days} 天")
    
    # 使用enumerate获取索引
    print(f"\n使用enumerate遍历：")
    max_level = max(water_levels)
    for idx, level in enumerate(water_levels):
        if level == max_level:
            print(f"  第{idx+1}天出现最高水位: {level} m")
            break
    
    return warning_days, alert_days, danger_days


def demonstrate_while_loop():
    """演示while循环"""
    print("\n" + "="*60)
    print("3. while循环 - 条件控制")
    print("="*60)
    
    # 模拟水库泄洪过程
    initial_level = 135.0  # 初始水位 (m)
    target_level = 120.0   # 目标水位 (m)
    discharge_rate = 2.5   # 每小时降低水位 (m)
    
    print(f"\n水库泄洪模拟：")
    print(f"  初始水位: {initial_level} m")
    print(f"  目标水位: {target_level} m")
    print(f"  泄洪速率: {discharge_rate} m/h")
    
    current_level = initial_level
    hours = 0
    max_hours = 20  # 安全限制
    
    print(f"\n泄洪过程：")
    print(f"{'时间(h)':<10} {'水位(m)':<12} {'状态'}")
    print("-" * 40)
    
    while current_level > target_level and hours < max_hours:
        print(f"{hours:<10} {current_level:<12.2f} {'泄洪中...'}")
        current_level -= discharge_rate
        hours += 1
    
    print(f"{hours:<10} {current_level:<12.2f} {'达到目标'}")
    
    print(f"\n泄洪结果：")
    print(f"  最终水位: {current_level:.2f} m")
    print(f"  耗时: {hours} 小时")
    print(f"  降低幅度: {initial_level - current_level:.2f} m")
    
    if current_level <= target_level:
        print(f"  ✓ 泄洪成功！")
    else:
        print(f"  ✗ 未达到目标水位")
    
    return hours, current_level


def demonstrate_break_continue():
    """演示break和continue"""
    print("\n" + "="*60)
    print("4. 循环控制 (break & continue)")
    print("="*60)
    
    # 示例1: 使用break - 寻找超标数据
    print(f"\n示例1: 使用break寻找第一个超标数据")
    water_quality = [5.2, 6.8, 7.4, 8.9, 6.5, 7.2]  # pH值
    max_ph = 8.5
    
    print(f"  pH值序列: {water_quality}")
    print(f"  标准上限: {max_ph}")
    
    for i, ph in enumerate(water_quality):
        if ph > max_ph:
            print(f"  ✗ 第{i+1}个数据超标: pH = {ph}")
            print(f"  停止检查，立即报警！")
            break
        else:
            print(f"  ✓ 第{i+1}个数据正常: pH = {ph}")
    
    # 示例2: 使用continue - 跳过无效数据
    print(f"\n示例2: 使用continue跳过无效数据")
    flow_rates = [125.6, -1.0, 138.9, 0.0, -1.0, 142.3, 136.7]  # -1表示无效数据
    
    print(f"  原始数据: {flow_rates}")
    print(f"  处理过程:")
    
    valid_data = []
    for flow in flow_rates:
        if flow < 0:
            print(f"    跳过无效数据: {flow}")
            continue
        if flow == 0:
            print(f"    跳过零值: {flow}")
            continue
        
        valid_data.append(flow)
        print(f"    ✓ 有效数据: {flow}")
    
    print(f"\n  有效数据: {valid_data}")
    print(f"  平均流量: {sum(valid_data)/len(valid_data):.2f} m³/s")
    
    return valid_data


def flood_warning_system():
    """综合案例：洪水预警系统"""
    print("\n" + "="*60)
    print("5. 综合案例：洪水预警系统")
    print("="*60)
    
    # 系统配置
    stations = {
        '三峡站': {
            'warning': 145.0,
            'alert': 150.0,
            'danger': 155.0,
            'current': 152.3
        },
        '寸滩站': {
            'warning': 175.0,
            'alert': 180.0,
            'danger': 185.0,
            'current': 178.5
        },
        '汉口站': {
            'warning': 25.0,
            'alert': 27.0,
            'danger': 29.0,
            'current': 26.2
        },
        '大通站': {
            'warning': 12.0,
            'alert': 13.5,
            'danger': 15.0,
            'current': 11.8
        }
    }
    
    print(f"\n长江流域洪水预警系统")
    print(f"监测站点: {len(stations)}个")
    print(f"\n" + "="*80)
    print(f"{'站点':<10} {'当前水位':<12} {'警戒':<8} {'预警':<8} {'危险':<8} {'等级':<8} {'预警'}")
    print("="*80)
    
    # 统计各等级站点数
    normal_count = 0
    warning_count = 0
    alert_count = 0
    danger_count = 0
    
    # 存储需要响应的站点
    response_needed = []
    
    for name, data in stations.items():
        current = data['current']
        warning = data['warning']
        alert = data['alert']
        danger = data['danger']
        
        # 判别等级
        if current < warning:
            level = "正常"
            symbol = "✓"
            normal_count += 1
        elif current < alert:
            level = "警戒"
            symbol = "⚠"
            warning_count += 1
            response_needed.append((name, level, current))
        elif current < danger:
            level = "预警"
            symbol = "⚠⚠"
            alert_count += 1
            response_needed.append((name, level, current))
        else:
            level = "危险"
            symbol = "⚠⚠⚠"
            danger_count += 1
            response_needed.append((name, level, current))
        
        print(f"{name:<10} {current:<12.2f} {warning:<8.2f} {alert:<8.2f} {danger:<8.2f} {level:<8} {symbol}")
    
    # 系统汇总
    print("\n" + "="*80)
    print(f"系统汇总：")
    print(f"  ✓ 正常站点: {normal_count}个")
    print(f"  ⚠ 警戒站点: {warning_count}个")
    print(f"  ⚠⚠ 预警站点: {alert_count}个")
    print(f"  ⚠⚠⚠ 危险站点: {danger_count}个")
    
    # 发布预警信息
    if danger_count > 0:
        system_level = "红色预警"
        action = "启动一级响应，紧急转移人员"
    elif alert_count > 0:
        system_level = "橙色预警"
        action = "启动二级响应，准备转移人员"
    elif warning_count > 0:
        system_level = "黄色预警"
        action = "启动三级响应，加密监测"
    else:
        system_level = "无预警"
        action = "维持正常监测"
    
    print(f"\n流域整体预警：")
    print(f"  预警等级: {system_level}")
    print(f"  响应措施: {action}")
    
    # 需要响应的站点详情
    if response_needed:
        print(f"\n需要响应的站点详情：")
        for name, level, current in response_needed:
            print(f"  • {name}: {level} (水位 {current:.2f}m)")
            
            # 针对不同等级给出具体措施
            if level == "危险":
                print(f"    → 立即启动泄洪")
                print(f"    → 紧急转移下游人员")
                print(f"    → 24小时值守")
            elif level == "预警":
                print(f"    → 加大泄洪力度")
                print(f"    → 通知下游做好准备")
                print(f"    → 增加巡查频次")
            elif level == "警戒":
                print(f"    → 开始预泄")
                print(f"    → 加密监测")
                print(f"    → 准备应急物资")
    
    return system_level, response_needed


def simulate_flood_process():
    """模拟洪水过程 - 综合应用"""
    print("\n" + "="*60)
    print("6. 高级案例：洪水过程模拟")
    print("="*60)
    
    # 模拟24小时洪水过程
    initial_level = 142.0  # 初始水位
    peak_level = 155.0     # 洪峰水位
    final_level = 145.0    # 最终水位
    
    warning_level = 145.0
    alert_level = 150.0
    danger_level = 155.0
    
    print(f"\n模拟参数：")
    print(f"  初始水位: {initial_level} m")
    print(f"  洪峰水位: {peak_level} m")
    print(f"  最终水位: {final_level} m")
    print(f"  模拟时长: 24 小时")
    
    print(f"\n洪水过程模拟：")
    print(f"{'时间(h)':<10} {'水位(m)':<12} {'涨幅(m/h)':<12} {'等级':<8} {'预警'}")
    print("-" * 70)
    
    max_level_reached = initial_level
    peak_time = 0
    warning_hours = 0
    alert_hours = 0
    danger_hours = 0
    
    for hour in range(25):  # 0-24小时
        # 简化的洪水过程曲线（三角形）
        if hour <= 12:
            # 涨水阶段
            current_level = initial_level + (peak_level - initial_level) * (hour / 12)
        else:
            # 退水阶段
            current_level = peak_level - (peak_level - final_level) * ((hour - 12) / 12)
        
        # 计算涨幅
        if hour == 0:
            rise_rate = 0
        else:
            if hour <= 12:
                rise_rate = (peak_level - initial_level) / 12
            else:
                rise_rate = -(peak_level - final_level) / 12
        
        # 判别等级
        if current_level < warning_level:
            level = "正常"
            symbol = "✓"
        elif current_level < alert_level:
            level = "警戒"
            symbol = "⚠"
            warning_hours += 1
        elif current_level < danger_level:
            level = "预警"
            symbol = "⚠⚠"
            alert_hours += 1
        else:
            level = "危险"
            symbol = "⚠⚠⚠"
            danger_hours += 1
        
        # 记录最高水位
        if current_level > max_level_reached:
            max_level_reached = current_level
            peak_time = hour
        
        # 每4小时输出一次（减少输出）
        if hour % 4 == 0 or hour == peak_time:
            print(f"{hour:<10} {current_level:<12.2f} {rise_rate:<12.2f} {level:<8} {symbol}")
    
    print(f"\n模拟结果统计：")
    print(f"  最高水位: {max_level_reached:.2f} m")
    print(f"  洪峰时刻: 第{peak_time}小时")
    print(f"  警戒时长: {warning_hours} 小时")
    print(f"  预警时长: {alert_hours} 小时")
    print(f"  危险时长: {danger_hours} 小时")
    
    return max_level_reached, peak_time


def main():
    """主函数"""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "Python控制流程工程应用" + " "*14 + "║")
    print("║" + " "*15 + "案例：洪水预警系统开发" + " "*14 + "║")
    print("╚" + "═"*58 + "╝")
    
    # 1. 条件语句
    level, action = demonstrate_if_else()
    
    # 2. for循环
    warning_days, alert_days, danger_days = demonstrate_for_loop()
    
    # 3. while循环
    hours, final_level = demonstrate_while_loop()
    
    # 4. break和continue
    valid_data = demonstrate_break_continue()
    
    # 5. 综合案例：洪水预警系统
    system_level, response_needed = flood_warning_system()
    
    # 6. 高级案例：洪水过程模拟
    max_level, peak_time = simulate_flood_process()
    
    # 总结
    print("\n" + "="*60)
    print("7. 学习总结")
    print("="*60)
    print("""
本项目学习内容：
1. ✅ if-elif-else：条件判断，用于等级划分
2. ✅ for循环：遍历序列，处理时间序列数据
3. ✅ while循环：条件控制，模拟连续过程
4. ✅ break：提前终止循环（发现异常立即响应）
5. ✅ continue：跳过本次循环（过滤无效数据）
6. ✅ enumerate：同时获取索引和值
7. ✅ range：生成数值序列

工程应用要点：
• 多级预警系统：正常→警戒→预警→危险
• 时间序列分析：逐时段/逐日数据处理
• 过程模拟：水库泄洪、洪水演进
• 数据质量控制：过滤无效数据
• 实时监测预警：自动判别并响应

洪水预警系统架构：
1. 数据采集：获取各站点实时水位
2. 等级判别：根据阈值划分预警等级
3. 统计分析：汇总流域整体情况
4. 预警发布：生成预警信息
5. 响应措施：针对不同等级采取相应措施
    """)
    
    print("="*60)
    print("项目2完成！")
    print("="*60)


if __name__ == "__main__":
    main()
