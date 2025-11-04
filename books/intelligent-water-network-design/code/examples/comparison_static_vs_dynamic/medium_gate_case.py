#!/usr/bin/env python3
"""
自动生成的案例: 某灌区主渠闸门
"""

import numpy as np
import matplotlib.pyplot as plt

# 项目信息
PROJECT_NAME = "某灌区主渠闸门"
DESIGN_STANDARD = "GB 50288-2018"

# 闸门设计参数
GATE_WIDTH = 3.0  # m
GATE_HEIGHT = 3.0  # m
DESIGN_FLOW = 12.0  # m³/s
CHECK_FLOW = 15.0  # m³/s

# 控制参数
CONTROL_LEVEL = "L2"
PID_KP = 2.0
PID_KI = 0.5
PID_KD = 0.1

# TODO: 在此添加你的代码

if __name__ == '__main__':
    print(f'项目: {PROJECT_NAME}')
    print(f'闸门尺寸: {GATE_WIDTH}m × {GATE_HEIGHT}m')
    print(f'设计流量: {DESIGN_FLOW} m³/s')
    print(f'智能化等级: {CONTROL_LEVEL}')