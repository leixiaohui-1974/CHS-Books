#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目1: Python变量与数据类型入门

课程目标：
1. 掌握Python基本数据类型（int, float, str, list, tuple, dict）
2. 理解变量的定义和使用
3. 学习基本运算符
4. 应用于水文站点数据存储

工程案例：
某流域有5个水文站，需要存储和管理每个站点的基本信息和监测数据

作者：Python编程实战教材组
日期：2025-11-12
"""

import math

def demonstrate_basic_types():
    """演示Python基本数据类型"""
    print("="*60)
    print("1. 基本数据类型演示")
    print("="*60)
    
    # 整数类型（int）
    station_id = 1001
    year = 2024
    print(f"\n整数类型：")
    print(f"  站点编号: {station_id} (类型: {type(station_id).__name__})")
    print(f"  观测年份: {year} (类型: {type(year).__name__})")
    
    # 浮点数类型（float）
    water_level = 125.68  # 米
    flow_rate = 3856.42   # 立方米/秒
    print(f"\n浮点数类型：")
    print(f"  水位: {water_level} m (类型: {type(water_level).__name__})")
    print(f"  流量: {flow_rate} m³/s (类型: {type(flow_rate).__name__})")
    
    # 字符串类型（str）
    station_name = "长江三峡水文站"
    location = "湖北省宜昌市"
    print(f"\n字符串类型：")
    print(f"  站点名称: {station_name} (类型: {type(station_name).__name__})")
    print(f"  所在位置: {location} (类型: {type(location).__name__})")
    
    # 布尔类型（bool）
    is_active = True
    has_rainfall_data = False
    print(f"\n布尔类型：")
    print(f"  是否在运行: {is_active} (类型: {type(is_active).__name__})")
    print(f"  有降雨数据: {has_rainfall_data} (类型: {type(has_rainfall_data).__name__})")
    
    return station_id, water_level, station_name, is_active


def demonstrate_list():
    """演示列表（list）类型"""
    print("\n" + "="*60)
    print("2. 列表（List）- 可变序列")
    print("="*60)
    
    # 创建水位数据列表
    water_levels = [125.68, 126.32, 127.15, 125.89, 124.56]
    print(f"\n水位数据列表:")
    print(f"  数据: {water_levels}")
    print(f"  类型: {type(water_levels).__name__}")
    print(f"  长度: {len(water_levels)}")
    
    # 列表操作
    print(f"\n列表操作：")
    print(f"  第1天水位: {water_levels[0]} m")
    print(f"  第5天水位: {water_levels[-1]} m")
    print(f"  前3天水位: {water_levels[:3]}")
    
    # 列表计算
    avg_level = sum(water_levels) / len(water_levels)
    max_level = max(water_levels)
    min_level = min(water_levels)
    print(f"\n统计结果：")
    print(f"  平均水位: {avg_level:.2f} m")
    print(f"  最高水位: {max_level:.2f} m")
    print(f"  最低水位: {min_level:.2f} m")
    print(f"  水位变幅: {max_level - min_level:.2f} m")
    
    # 添加新数据
    water_levels.append(126.78)
    print(f"\n添加新数据后: {water_levels}")
    
    return water_levels, avg_level


def demonstrate_tuple():
    """演示元组（tuple）类型"""
    print("\n" + "="*60)
    print("3. 元组（Tuple）- 不可变序列")
    print("="*60)
    
    # 创建站点坐标（经度，纬度，高程）
    station_coords = (110.85, 30.72, 185.0)
    print(f"\n站点坐标（元组）:")
    print(f"  数据: {station_coords}")
    print(f"  类型: {type(station_coords).__name__}")
    
    # 元组解包
    longitude, latitude, elevation = station_coords
    print(f"\n坐标信息：")
    print(f"  经度: {longitude}°E")
    print(f"  纬度: {latitude}°N")
    print(f"  高程: {elevation} m")
    
    # 元组不可修改（这会报错，仅作演示）
    # station_coords[0] = 111.0  # TypeError: 'tuple' object does not support item assignment
    print(f"\n注意：元组创建后不能修改元素值")
    
    return station_coords


def demonstrate_dict():
    """演示字典（dict）类型"""
    print("\n" + "="*60)
    print("4. 字典（Dictionary）- 键值对集合")
    print("="*60)
    
    # 创建水文站信息字典
    station_info = {
        'id': 1001,
        'name': '长江三峡水文站',
        'location': '湖北省宜昌市',
        'longitude': 110.85,
        'latitude': 30.72,
        'elevation': 185.0,
        'start_year': 1950,
        'is_active': True,
        'equipment': ['水位计', '流量计', '雨量计'],
        'recent_data': {
            'date': '2024-01-15',
            'water_level': 125.68,
            'flow_rate': 3856.42,
            'rainfall': 0.0
        }
    }
    
    print(f"\n水文站信息字典:")
    print(f"  类型: {type(station_info).__name__}")
    print(f"  键的数量: {len(station_info)}")
    print(f"\n字典内容：")
    for key, value in station_info.items():
        if isinstance(value, (dict, list)):
            print(f"  {key}: {type(value).__name__}")
        else:
            print(f"  {key}: {value}")
    
    # 访问字典元素
    print(f"\n访问字典元素：")
    print(f"  站点名称: {station_info['name']}")
    print(f"  建站年份: {station_info['start_year']}")
    print(f"  运行年数: {2024 - station_info['start_year']}年")
    
    # 访问嵌套字典
    recent = station_info['recent_data']
    print(f"\n最新观测数据：")
    print(f"  日期: {recent['date']}")
    print(f"  水位: {recent['water_level']} m")
    print(f"  流量: {recent['flow_rate']} m³/s")
    print(f"  降雨: {recent['rainfall']} mm")
    
    return station_info


def demonstrate_operators():
    """演示运算符"""
    print("\n" + "="*60)
    print("5. 运算符应用")
    print("="*60)
    
    # 水力计算示例
    print(f"\n水力计算示例：")
    
    # 算术运算符
    width = 50.0      # 渠道宽度 (m)
    depth = 3.5       # 水深 (m)
    velocity = 2.8    # 流速 (m/s)
    
    area = width * depth  # 过水断面积
    flow_rate = area * velocity  # 流量
    wetted_perimeter = width + 2 * depth  # 湿周
    hydraulic_radius = area / wetted_perimeter  # 水力半径
    
    print(f"  渠道宽度: {width} m")
    print(f"  水深: {depth} m")
    print(f"  流速: {velocity} m/s")
    print(f"  断面积: {area} m²")
    print(f"  流量: {flow_rate:.2f} m³/s")
    print(f"  湿周: {wetted_perimeter} m")
    print(f"  水力半径: {hydraulic_radius:.3f} m")
    
    # 比较运算符
    design_flow = 500.0  # 设计流量
    print(f"\n流量校核：")
    print(f"  设计流量: {design_flow} m³/s")
    print(f"  实际流量: {flow_rate:.2f} m³/s")
    print(f"  是否满足设计要求: {flow_rate >= design_flow}")
    
    # 逻辑运算符
    min_depth = 2.0
    max_depth = 5.0
    is_safe = (depth >= min_depth) and (depth <= max_depth)
    print(f"\n安全校核：")
    print(f"  最小水深: {min_depth} m")
    print(f"  最大水深: {max_depth} m")
    print(f"  当前水深: {depth} m")
    print(f"  是否在安全范围: {is_safe}")
    
    return flow_rate, is_safe


class WaterStation:
    """水文站类 - 演示面向对象基础"""
    
    def __init__(self, station_id, name, location, longitude, latitude):
        """初始化水文站对象"""
        self.station_id = station_id
        self.name = name
        self.location = location
        self.longitude = longitude
        self.latitude = latitude
        self.water_levels = []  # 水位数据列表
        self.flow_rates = []    # 流量数据列表
    
    def add_observation(self, water_level, flow_rate):
        """添加观测数据"""
        self.water_levels.append(water_level)
        self.flow_rates.append(flow_rate)
    
    def get_statistics(self):
        """计算统计数据"""
        if not self.water_levels:
            return None
        
        stats = {
            'count': len(self.water_levels),
            'avg_level': sum(self.water_levels) / len(self.water_levels),
            'max_level': max(self.water_levels),
            'min_level': min(self.water_levels),
            'avg_flow': sum(self.flow_rates) / len(self.flow_rates),
            'max_flow': max(self.flow_rates),
            'min_flow': min(self.flow_rates)
        }
        return stats
    
    def __str__(self):
        """字符串表示"""
        return f"水文站[{self.station_id}] {self.name} @ {self.location}"


def demonstrate_class():
    """演示类的使用"""
    print("\n" + "="*60)
    print("6. 类与对象 - 面向对象编程入门")
    print("="*60)
    
    # 创建水文站对象
    station = WaterStation(
        station_id=1001,
        name="长江三峡水文站",
        location="湖北省宜昌市",
        longitude=110.85,
        latitude=30.72
    )
    
    print(f"\n创建水文站对象:")
    print(f"  {station}")
    
    # 添加观测数据
    observations = [
        (125.68, 3856.42),
        (126.32, 4125.67),
        (127.15, 4589.23),
        (125.89, 3921.58),
        (124.56, 3542.91)
    ]
    
    print(f"\n添加观测数据:")
    for i, (level, flow) in enumerate(observations, 1):
        station.add_observation(level, flow)
        print(f"  第{i}天: 水位={level}m, 流量={flow}m³/s")
    
    # 计算统计数据
    stats = station.get_statistics()
    print(f"\n统计结果:")
    print(f"  观测次数: {stats['count']}")
    print(f"  平均水位: {stats['avg_level']:.2f} m")
    print(f"  水位变幅: {stats['max_level'] - stats['min_level']:.2f} m")
    print(f"  平均流量: {stats['avg_flow']:.2f} m³/s")
    print(f"  流量变幅: {stats['max_flow'] - stats['min_flow']:.2f} m³/s")
    
    return station, stats


def engineering_example():
    """工程应用案例：流域水文站网数据管理"""
    print("\n" + "="*60)
    print("7. 工程应用案例：流域水文站网数据管理")
    print("="*60)
    
    # 创建多个水文站
    stations = [
        {
            'id': 1001,
            'name': '长江三峡水文站',
            'location': '湖北省宜昌市',
            'coords': (110.85, 30.72, 185.0),
            'drainage_area': 1084000,  # 控制流域面积 (km²)
            'data': [125.68, 126.32, 127.15, 125.89, 124.56]
        },
        {
            'id': 1002,
            'name': '长江寸滩水文站',
            'location': '重庆市',
            'coords': (106.58, 29.58, 162.0),
            'drainage_area': 865000,
            'data': [162.45, 163.28, 164.12, 162.89, 161.76]
        },
        {
            'id': 1003,
            'name': '长江汉口水文站',
            'location': '湖北省武汉市',
            'coords': (114.30, 30.58, 23.3),
            'drainage_area': 1488000,
            'data': [23.45, 24.12, 24.89, 23.98, 23.21]
        },
        {
            'id': 1004,
            'name': '长江大通水文站',
            'location': '安徽省铜陵市',
            'coords': (117.62, 30.77, 7.1),
            'drainage_area': 1705000,
            'data': [7.23, 7.85, 8.42, 7.67, 7.12]
        },
        {
            'id': 1005,
            'name': '长江南京水文站',
            'location': '江苏省南京市',
            'coords': (118.78, 32.06, 8.9),
            'drainage_area': 1750000,
            'data': [8.95, 9.52, 10.18, 9.34, 8.76]
        }
    ]
    
    print(f"\n流域水文站网概况:")
    print(f"  水文站总数: {len(stations)}")
    print(f"  覆盖流域: 长江流域")
    print(f"  控制面积: {stations[-1]['drainage_area']:,} km²")
    
    # 计算每个站点的统计数据
    print(f"\n各站点水位统计:")
    print(f"{'站点ID':<8} {'站点名称':<20} {'平均水位(m)':<12} {'最高水位(m)':<12} {'最低水位(m)':<12} {'变幅(m)':<10}")
    print("-" * 90)
    
    for station in stations:
        data = station['data']
        avg = sum(data) / len(data)
        max_val = max(data)
        min_val = min(data)
        range_val = max_val - min_val
        
        print(f"{station['id']:<8} {station['name']:<20} {avg:<12.2f} {max_val:<12.2f} {min_val:<12.2f} {range_val:<10.2f}")
    
    # 找出水位最高和最低的站点
    all_levels = []
    for station in stations:
        for level in station['data']:
            all_levels.append((station['name'], level))
    
    all_levels.sort(key=lambda x: x[1])
    
    print(f"\n全流域水位分析:")
    print(f"  最低水位: {all_levels[0][1]:.2f} m @ {all_levels[0][0]}")
    print(f"  最高水位: {all_levels[-1][1]:.2f} m @ {all_levels[-1][0]}")
    print(f"  水位跨度: {all_levels[-1][1] - all_levels[0][1]:.2f} m")
    
    return stations


def main():
    """主函数"""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "Python数据类型工程应用" + " "*15 + "║")
    print("║" + " "*12 + "案例：流域水文站网数据管理" + " "*12 + "║")
    print("╚" + "═"*58 + "╝")
    
    # 1. 基本类型
    demonstrate_basic_types()
    
    # 2. 列表
    water_levels, avg_level = demonstrate_list()
    
    # 3. 元组
    coords = demonstrate_tuple()
    
    # 4. 字典
    station_info = demonstrate_dict()
    
    # 5. 运算符
    flow_rate, is_safe = demonstrate_operators()
    
    # 6. 类与对象
    station, stats = demonstrate_class()
    
    # 7. 工程案例
    stations = engineering_example()
    
    # 总结
    print("\n" + "="*60)
    print("8. 学习总结")
    print("="*60)
    print("""
本项目学习内容：
1. ✅ 基本数据类型：int, float, str, bool
2. ✅ 列表（list）：可变序列，用于存储时间序列数据
3. ✅ 元组（tuple）：不可变序列，用于存储坐标等固定数据
4. ✅ 字典（dict）：键值对集合，用于存储结构化信息
5. ✅ 运算符：算术、比较、逻辑运算在水力计算中的应用
6. ✅ 类与对象：面向对象编程入门
7. ✅ 工程案例：流域水文站网数据管理

关键要点：
• Python是动态类型语言，变量无需声明类型
• 列表适合存储可变的序列数据（如时间序列）
• 字典适合存储结构化数据（如站点信息）
• 面向对象编程使代码更模块化、可维护

工程应用：
• 水文站基础信息管理
• 水位流量时间序列存储
• 统计分析与数据汇总
• 多站点数据联合分析
    """)
    
    print("="*60)
    print("项目1完成！")
    print("="*60)


if __name__ == "__main__":
    main()
