#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目4: Python文件读写

课程目标：
1. 掌握文本文件读写
2. 学习CSV文件处理
3. 理解JSON数据格式
4. 掌握异常处理机制
5. 应用于水文数据文件处理

工程案例：
处理水文站观测数据文件，包括读取、清洗、统计和导出

作者：Python编程实战教材组
日期：2025-11-12
"""

import os
import csv
import json
from datetime import datetime

# ============================================================
# 1. 文本文件读写
# ============================================================

def write_text_file(filename, data):
    """写入文本文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"✓ 成功写入文件: {filename}")
        return True
    except Exception as e:
        print(f"✗ 写入失败: {e}")
        return False


def read_text_file(filename):
    """读取文本文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ 成功读取文件: {filename}")
        return content
    except FileNotFoundError:
        print(f"✗ 文件不存在: {filename}")
        return None
    except Exception as e:
        print(f"✗ 读取失败: {e}")
        return None


def demonstrate_text_file():
    """演示文本文件操作"""
    print("="*60)
    print("1. 文本文件操作")
    print("="*60)
    
    # 准备数据
    station_info = """长江三峡水文站观测记录
站点编号: 1001
站点名称: 三峡站
位置: 湖北省宜昌市
经度: 110.85°E
纬度: 30.72°N
高程: 185.0m
建站年份: 1950
观测项目: 水位、流量、降雨
"""
    
    # 写入文件
    filename = "station_info.txt"
    print(f"\n写入站点信息到 {filename}:")
    write_text_file(filename, station_info)
    
    # 读取文件
    print(f"\n读取文件内容:")
    content = read_text_file(filename)
    if content:
        print(content)
    
    # 逐行处理
    print(f"\n逐行读取和处理:")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                print(f"  第{i}行: {line.strip()}")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    return filename


# ============================================================
# 2. CSV文件处理
# ============================================================

def write_csv_file(filename, data, headers):
    """写入CSV文件"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"✓ 成功写入CSV: {filename}")
        return True
    except Exception as e:
        print(f"✗ 写入CSV失败: {e}")
        return False


def read_csv_file(filename):
    """读取CSV文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            data = list(reader)
        print(f"✓ 成功读取CSV: {filename}")
        return headers, data
    except FileNotFoundError:
        print(f"✗ CSV文件不存在: {filename}")
        return None, None
    except Exception as e:
        print(f"✗ 读取CSV失败: {e}")
        return None, None


def demonstrate_csv_file():
    """演示CSV文件操作"""
    print("\n" + "="*60)
    print("2. CSV文件处理")
    print("="*60)
    
    # 准备水位数据
    headers = ['日期', '水位(m)', '流量(m³/s)', '降雨(mm)']
    data = [
        ['2024-01-11', '125.68', '3856.42', '0.0'],
        ['2024-01-12', '126.32', '4125.67', '5.2'],
        ['2024-01-13', '127.15', '4589.23', '12.8'],
        ['2024-01-14', '125.89', '3921.58', '3.5'],
        ['2024-01-15', '124.56', '3542.91', '0.0']
    ]
    
    # 写入CSV
    filename = "water_level_data.csv"
    print(f"\n写入水位数据到 {filename}:")
    write_csv_file(filename, data, headers)
    
    # 读取CSV
    print(f"\n读取CSV数据:")
    headers, data = read_csv_file(filename)
    
    if headers and data:
        # 打印表格
        print(f"\n{headers[0]:<15} {headers[1]:<12} {headers[2]:<15} {headers[3]:<12}")
        print("-" * 60)
        for row in data:
            print(f"{row[0]:<15} {row[1]:<12} {row[2]:<15} {row[3]:<12}")
        
        # 统计分析
        print(f"\n数据统计:")
        water_levels = [float(row[1]) for row in data]
        flow_rates = [float(row[2]) for row in data]
        rainfalls = [float(row[3]) for row in data]
        
        print(f"  记录数: {len(data)}")
        print(f"  平均水位: {sum(water_levels)/len(water_levels):.2f} m")
        print(f"  平均流量: {sum(flow_rates)/len(flow_rates):.2f} m³/s")
        print(f"  总降雨量: {sum(rainfalls):.2f} mm")
    
    return filename


# ============================================================
# 3. JSON文件处理
# ============================================================

def write_json_file(filename, data):
    """写入JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 成功写入JSON: {filename}")
        return True
    except Exception as e:
        print(f"✗ 写入JSON失败: {e}")
        return False


def read_json_file(filename):
    """读取JSON文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ 成功读取JSON: {filename}")
        return data
    except FileNotFoundError:
        print(f"✗ JSON文件不存在: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ JSON格式错误: {e}")
        return None
    except Exception as e:
        print(f"✗ 读取JSON失败: {e}")
        return None


def demonstrate_json_file():
    """演示JSON文件操作"""
    print("\n" + "="*60)
    print("3. JSON文件处理")
    print("="*60)
    
    # 准备结构化数据
    station_data = {
        "station_id": 1001,
        "station_name": "长江三峡水文站",
        "location": {
            "province": "湖北省",
            "city": "宜昌市",
            "coordinates": {
                "longitude": 110.85,
                "latitude": 30.72,
                "elevation": 185.0
            }
        },
        "characteristics": {
            "start_year": 1950,
            "drainage_area": 1084000,
            "is_active": True
        },
        "equipment": ["水位计", "流量计", "雨量计"],
        "recent_observations": [
            {"date": "2024-01-15", "water_level": 125.68, "flow_rate": 3856.42},
            {"date": "2024-01-16", "water_level": 126.32, "flow_rate": 4125.67},
            {"date": "2024-01-17", "water_level": 127.15, "flow_rate": 4589.23}
        ]
    }
    
    # 写入JSON
    filename = "station_data.json"
    print(f"\n写入站点数据到 {filename}:")
    write_json_file(filename, station_data)
    
    # 读取JSON
    print(f"\n读取JSON数据:")
    data = read_json_file(filename)
    
    if data:
        print(f"\n站点信息:")
        print(f"  ID: {data['station_id']}")
        print(f"  名称: {data['station_name']}")
        print(f"  位置: {data['location']['province']} {data['location']['city']}")
        print(f"  坐标: {data['location']['coordinates']['longitude']}°E, "
              f"{data['location']['coordinates']['latitude']}°N")
        print(f"  建站年份: {data['characteristics']['start_year']}")
        print(f"  控制面积: {data['characteristics']['drainage_area']:,} km²")
        
        print(f"\n观测设备:")
        for equipment in data['equipment']:
            print(f"  • {equipment}")
        
        print(f"\n近期观测:")
        for obs in data['recent_observations']:
            print(f"  {obs['date']}: 水位={obs['water_level']}m, "
                  f"流量={obs['flow_rate']}m³/s")
    
    return filename


# ============================================================
# 4. 异常处理
# ============================================================

def safe_read_file(filename):
    """安全读取文件（带异常处理）"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, None
    except FileNotFoundError:
        return None, f"文件不存在: {filename}"
    except PermissionError:
        return None, f"没有读取权限: {filename}"
    except UnicodeDecodeError:
        return None, f"编码错误: {filename}"
    except Exception as e:
        return None, f"未知错误: {e}"


def safe_parse_number(value):
    """安全解析数字"""
    try:
        return float(value), None
    except ValueError:
        return None, f"无法转换为数字: {value}"
    except TypeError:
        return None, f"类型错误: {value}"


def demonstrate_exception_handling():
    """演示异常处理"""
    print("\n" + "="*60)
    print("4. 异常处理")
    print("="*60)
    
    # 示例1: 文件不存在
    print(f"\n示例1: 处理文件不存在")
    content, error = safe_read_file("nonexistent.txt")
    if error:
        print(f"  ✗ {error}")
    else:
        print(f"  ✓ 读取成功")
    
    # 示例2: 数据解析
    print(f"\n示例2: 安全解析数据")
    test_values = ["125.68", "abc", "126.32", None, "127.15"]
    valid_data = []
    
    for val in test_values:
        num, error = safe_parse_number(val)
        if error:
            print(f"  ✗ {error}")
        else:
            valid_data.append(num)
            print(f"  ✓ 解析成功: {val} → {num}")
    
    print(f"\n有效数据: {valid_data}")
    print(f"平均值: {sum(valid_data)/len(valid_data):.2f}")


# ============================================================
# 5. 综合案例：水文数据处理系统
# ============================================================

class HydroDataProcessor:
    """水文数据处理类"""
    
    def __init__(self, station_name):
        self.station_name = station_name
        self.data = []
    
    def load_from_csv(self, filename):
        """从CSV加载数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
            print(f"✓ 加载 {len(self.data)} 条记录")
            return True
        except Exception as e:
            print(f"✗ 加载失败: {e}")
            return False
    
    def clean_data(self):
        """清洗数据"""
        print(f"\n数据清洗:")
        original_count = len(self.data)
        cleaned_data = []
        
        for i, record in enumerate(self.data):
            try:
                # 验证必要字段
                date = record.get('日期')
                level_str = record.get('水位(m)')
                flow_str = record.get('流量(m³/s)')
                
                if not (date and level_str and flow_str):
                    print(f"  第{i+1}行: 缺少必要字段，跳过")
                    continue
                
                # 转换数值
                level = float(level_str)
                flow = float(flow_str)
                
                # 数据合理性检查
                if level < 0 or flow < 0:
                    print(f"  第{i+1}行: 数据异常（负值），跳过")
                    continue
                
                cleaned_data.append(record)
                
            except ValueError as e:
                print(f"  第{i+1}行: 数据格式错误，跳过")
                continue
        
        self.data = cleaned_data
        print(f"  原始记录: {original_count}")
        print(f"  有效记录: {len(self.data)}")
        print(f"  清理掉: {original_count - len(self.data)}")
    
    def calculate_statistics(self):
        """计算统计数据"""
        if not self.data:
            return None
        
        levels = [float(r['水位(m)']) for r in self.data]
        flows = [float(r['流量(m³/s)']) for r in self.data]
        
        stats = {
            '记录数': len(self.data),
            '平均水位': sum(levels) / len(levels),
            '最高水位': max(levels),
            '最低水位': min(levels),
            '平均流量': sum(flows) / len(flows),
            '最大流量': max(flows),
            '最小流量': min(flows)
        }
        
        return stats
    
    def export_report(self, filename):
        """导出统计报告"""
        stats = self.calculate_statistics()
        if not stats:
            return False
        
        report = f"""水文站数据分析报告
{'='*50}

站点名称: {self.station_name}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

数据概况:
  记录数量: {stats['记录数']}

水位统计:
  平均水位: {stats['平均水位']:.2f} m
  最高水位: {stats['最高水位']:.2f} m
  最低水位: {stats['最低水位']:.2f} m
  变化幅度: {stats['最高水位'] - stats['最低水位']:.2f} m

流量统计:
  平均流量: {stats['平均流量']:.2f} m³/s
  最大流量: {stats['最大流量']:.2f} m³/s
  最小流量: {stats['最小流量']:.2f} m³/s
  变化幅度: {stats['最大流量'] - stats['最小流量']:.2f} m³/s

{'='*50}
"""
        
        return write_text_file(filename, report)


def comprehensive_example():
    """综合案例"""
    print("\n" + "="*60)
    print("5. 综合案例：水文数据处理系统")
    print("="*60)
    
    # 创建处理器
    processor = HydroDataProcessor("长江三峡水文站")
    
    # 加载数据
    print(f"\n步骤1: 加载数据")
    processor.load_from_csv("water_level_data.csv")
    
    # 清洗数据
    print(f"\n步骤2: 清洗数据")
    processor.clean_data()
    
    # 计算统计
    print(f"\n步骤3: 计算统计")
    stats = processor.calculate_statistics()
    if stats:
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    
    # 导出报告
    print(f"\n步骤4: 导出报告")
    processor.export_report("hydro_report.txt")
    
    # 读取并显示报告
    print(f"\n生成的报告:")
    content = read_text_file("hydro_report.txt")
    if content:
        print(content)


def main():
    """主函数"""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*16 + "Python文件读写应用" + " "*16 + "║")
    print("║" + " "*13 + "案例：水文数据文件处理" + " "*14 + "║")
    print("╚" + "═"*58 + "╝")
    
    # 1. 文本文件
    demonstrate_text_file()
    
    # 2. CSV文件
    demonstrate_csv_file()
    
    # 3. JSON文件
    demonstrate_json_file()
    
    # 4. 异常处理
    demonstrate_exception_handling()
    
    # 5. 综合案例
    comprehensive_example()
    
    # 总结
    print("\n" + "="*60)
    print("学习总结")
    print("="*60)
    print("""
本项目学习内容：
1. ✅ 文本文件读写（txt）
2. ✅ CSV文件处理
3. ✅ JSON文件操作
4. ✅ 异常处理机制
5. ✅ 数据清洗和验证
6. ✅ 统计报告生成

工程应用：
• 水文站点信息存储
• 观测数据文件读写
• 结构化数据处理
• 数据质量控制
• 自动生成报告

最佳实践：
• 使用with语句自动关闭文件
• 指定encoding='utf-8'避免乱码
• try-except处理异常
• 数据验证和清洗
• 统一文件格式（CSV, JSON）
    """)
    
    # 清理临时文件
    print("\n清理临时文件...")
    temp_files = [
        "station_info.txt",
        "water_level_data.csv",
        "station_data.json",
        "hydro_report.txt"
    ]
    
    for f in temp_files:
        try:
            if os.path.exists(f):
                os.remove(f)
                print(f"  ✓ 删除: {f}")
        except:
            pass
    
    print("\n" + "="*60)
    print("项目4完成！")
    print("="*60)


if __name__ == "__main__":
    main()
