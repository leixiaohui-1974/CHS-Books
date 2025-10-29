import pytest
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture
def sample_config():
    """提供示例配置"""
    return {
        "simulation_time": 3600,
        "time_step": 60,
        "reaches": [
            {
                "name": "reach1",
                "length": 1000,
                "slope": 0.001,
                "roughness": 0.025,
                "width": 10,
                "initial_flow": 5.0,
                "initial_depth": 2.0
            }
        ],
        "controllers": [
            {
                "type": "pid",
                "reach": "reach1",
                "setpoint": 2.0,
                "kp": 0.5,
                "ki": 0.1,
                "kd": 0.2
            }
        ]
    }