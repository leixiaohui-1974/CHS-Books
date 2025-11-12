# -*- coding: utf-8 -*-
"""
统一所有案例的参数
确保README说明、示意图、main.py三者参数一致
"""
import sys
import io
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "books" / "water-system-control" / "code" / "examples"

# 各案例的标准参数（从main.py中提取的实际使用参数）
STANDARD_PARAMETERS = {
    'case_01_home_water_tower': {
        'A': 2.0,
        'R': 5.0,
        'K': 1.2,
        'h_lower': 2.5,
        'h_upper': 3.5,
        'h_setpoint': 3.0,
        'hysteresis': 1.0,
        'h0': 2.8,
    },
    'case_02_cooling_tower': {
        'A': 2.0,
        'R': 2.0,
        'K': 1.0,
        'Kp': 1.2,
        'h_setpoint': 3.0,
        'h0': 1.5,
    },
    'case_03_water_supply_station': {
        'A': 2.0,
        'R': 2.0,
        'K': 1.0,
        'Kp': 1.5,
        'Ki': 0.3,
        'h_setpoint': 3.0,
        'h0': 1.5,
    },
    'case_04_pid_tuning': {
        'A': 2.0,
        'R': 2.0,
        'K': 1.0,
        'Kp': 2.0,
        'Ki': 0.5,
        'Kd': 0.5,
        'h_setpoint': 3.0,
        'h0': 1.5,
    },
}

def main():
    print("="*80)
    print("  🔧 统一参数配置")
    print("="*80)
    print()
    
    print("📊 标准参数配置：")
    print()
    
    for case_id, params in STANDARD_PARAMETERS.items():
        case_num = case_id.split('_')[1]
        print(f"案例{case_num} - {case_id}:")
        for key, value in params.items():
            print(f"  {key} = {value}")
        print()
    
    print("="*80)
    print("  ⚠️  需要手动更新")
    print("="*80)
    print("""
由于参数嵌入在不同格式的文本中，建议手动更新以下文件：

对于每个案例：
1. 检查 main.py 中的实际参数
2. 更新 README.md 中的参数说明
3. 确认 generate_diagram.py 中的示意图标注

特别注意：
- 案例1：h_lower=2.5, h_upper=3.5 (滞环1.0m)
- 其他案例：使用上述标准参数表
    """)
    print("="*80)

if __name__ == '__main__':
    main()



