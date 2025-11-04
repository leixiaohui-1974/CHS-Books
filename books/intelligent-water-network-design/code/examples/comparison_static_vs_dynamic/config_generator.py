#!/usr/bin/env python3
"""
案例配置生成器
==============

功能: 快速生成自定义工程案例的配置文件

使用方法:
    python3 config_generator.py
    
    或交互式使用:
    python3 config_generator.py --interactive
    
输出:
    - project_config.json (项目配置文件)
    - 可直接用于其他脚本
"""

import json
import sys
from typing import Dict, Any

print("="*80)
print("  案例配置生成器 v1.0")
print("="*80)
print()

# ============================================================================
# 配置模板
# ============================================================================

DEFAULT_CONFIG = {
    "project_info": {
        "name": "示例工程",
        "location": "某灌区",
        "scale": "中型",
        "design_standard": "GB 50288-2018",
        "design_year": 2024
    },
    
    "gate_design": {
        "width": 3.0,              # 闸孔宽度(m)
        "max_height": 3.0,         # 最大高度(m)
        "discharge_coef": 0.85,    # 流量系数
        "design_flow": 10.0,       # 设计流量(m³/s)
        "check_flow": 15.0         # 校核流量(m³/s)
    },
    
    "hydraulic_conditions": {
        "upstream_level": 2.5,     # 上游水位(m)
        "downstream_level": 2.0,   # 下游水位(m)
        "channel_slope": 0.0001,   # 渠道坡度
        "roughness": 0.02          # 糙率
    },
    
    "control_system": {
        "level": "L2",             # 智能化等级: L0/L1/L2/L3/L4/L5
        "sensors": {
            "upstream_level": True,
            "downstream_level": True,
            "gate_opening": True,
            "flow_rate": False
        },
        "controller": {
            "type": "PID",
            "Kp": 2.0,
            "Ki": 0.5,
            "Kd": 0.1,
            "control_cycle": 10    # 控制周期(秒)
        },
        "target_precision": 5.0,   # 目标精度(cm)
        "response_time": 5.0       # 目标响应时间(分钟)
    },
    
    "cost_parameters": {
        "static": {
            "initial_cost": 30,           # 初始投资(万元)
            "annual_staff": 13,           # 年运行人员数
            "staff_salary": 12,           # 人员年薪(万元)
            "annual_power": 20,           # 年电费(万元)
            "annual_maintain": 4          # 年维护费(万元)
        },
        "l2": {
            "sensor_cost": 1.5,           # 传感器成本(万元)
            "controller_cost": 3.5,       # 控制系统成本(万元)
            "annual_staff": 3,            # 年运行人员数
            "power_saving_rate": 0.4,     # 电费节省率
            "annual_maintain": 12         # 年维护费(万元)
        }
    },
    
    "simulation_settings": {
        "duration": 3600,          # 仿真时长(秒)
        "time_step": 10,           # 时间步长(秒)
        "test_scenarios": [
            "normal",              # 正常工况
            "step",                # 阶跃响应
            "disturbance",         # 扰动工况
            "extreme"              # 极端工况
        ]
    }
}

TEMPLATES = {
    "小型单闸": {
        "project_info": {"name": "小型灌溉闸门", "scale": "小型"},
        "gate_design": {"width": 2.0, "max_height": 2.0, "design_flow": 5.0, "check_flow": 8.0},
        "cost_parameters": {
            "static": {"initial_cost": 20, "annual_staff": 8},
            "l2": {"sensor_cost": 1.0, "controller_cost": 2.5, "annual_staff": 2}
        }
    },
    
    "中型单闸": {
        "project_info": {"name": "中型灌溉闸门", "scale": "中型"},
        "gate_design": {"width": 3.0, "max_height": 3.0, "design_flow": 10.0, "check_flow": 15.0},
        "cost_parameters": {
            "static": {"initial_cost": 30, "annual_staff": 13},
            "l2": {"sensor_cost": 1.5, "controller_cost": 3.5, "annual_staff": 3}
        }
    },
    
    "大型单闸": {
        "project_info": {"name": "大型灌溉闸门", "scale": "大型"},
        "gate_design": {"width": 5.0, "max_height": 4.0, "design_flow": 20.0, "check_flow": 30.0},
        "cost_parameters": {
            "static": {"initial_cost": 50, "annual_staff": 18},
            "l2": {"sensor_cost": 2.0, "controller_cost": 5.0, "annual_staff": 4}
        }
    },
    
    "串级4闸": {
        "project_info": {"name": "串级渠道4闸门", "scale": "中型", "control_points": 4},
        "gate_design": {"width": 3.0, "max_height": 3.0, "design_flow": 10.0, "check_flow": 15.0},
        "control_system": {"level": "L3"},
        "cost_parameters": {
            "static": {"initial_cost": 120, "annual_staff": 52},
            "l2": {"sensor_cost": 6.0, "controller_cost": 14.0, "annual_staff": 12}
        }
    }
}

# ============================================================================
# 配置生成器类
# ============================================================================

class ConfigGenerator:
    """配置文件生成器"""
    
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
    
    def load_template(self, template_name: str) -> bool:
        """加载模板"""
        if template_name not in TEMPLATES:
            print(f"错误: 模板 '{template_name}' 不存在")
            print(f"可用模板: {', '.join(TEMPLATES.keys())}")
            return False
        
        template = TEMPLATES[template_name]
        self._merge_config(self.config, template)
        print(f"✓ 已加载模板: {template_name}")
        return True
    
    def _merge_config(self, base: Dict, updates: Dict):
        """递归合并配置"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def update_config(self, path: str, value: Any):
        """更新配置项
        
        Args:
            path: 配置路径，如 "gate_design.width"
            value: 新值
        """
        keys = path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        print(f"✓ 已更新: {path} = {value}")
    
    def get_config(self, path: str = None) -> Any:
        """获取配置项"""
        if path is None:
            return self.config
        
        keys = path.split('.')
        current = self.config
        
        for key in keys:
            if key not in current:
                return None
            current = current[key]
        
        return current
    
    def save_config(self, filename: str = "project_config.json"):
        """保存配置到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"✓ 配置已保存: {filename}")
    
    def load_config(self, filename: str):
        """从文件加载配置"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✓ 配置已加载: {filename}")
            return True
        except FileNotFoundError:
            print(f"错误: 文件不存在 '{filename}'")
            return False
        except json.JSONDecodeError:
            print(f"错误: 文件格式错误 '{filename}'")
            return False
    
    def print_config(self):
        """打印配置"""
        print("\n" + "="*80)
        print("  当前配置")
        print("="*80)
        print(json.dumps(self.config, indent=2, ensure_ascii=False))
        print("="*80)
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        errors = []
        
        # 检查必要字段
        required_fields = [
            "project_info.name",
            "gate_design.width",
            "gate_design.design_flow"
        ]
        
        for field in required_fields:
            if self.get_config(field) is None:
                errors.append(f"缺少必要字段: {field}")
        
        # 检查数值合理性
        width = self.get_config("gate_design.width")
        if width and width <= 0:
            errors.append("闸门宽度必须大于0")
        
        flow = self.get_config("gate_design.design_flow")
        if flow and flow <= 0:
            errors.append("设计流量必须大于0")
        
        if errors:
            print("\n配置验证失败:")
            for error in errors:
                print(f"  ✗ {error}")
            return False
        
        print("\n✓ 配置验证通过")
        return True
    
    def generate_python_code(self, output_file: str = "generated_case.py"):
        """生成Python代码"""
        code_lines = [
            "#!/usr/bin/env python3",
            '"""',
            f'自动生成的案例: {self.get_config("project_info.name")}',
            '"""',
            "",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "",
            "# 项目信息",
            f"PROJECT_NAME = \"{self.get_config('project_info.name')}\"",
            f"DESIGN_STANDARD = \"{self.get_config('project_info.design_standard')}\"",
            "",
            "# 闸门设计参数",
            f"GATE_WIDTH = {self.get_config('gate_design.width')}  # m",
            f"GATE_HEIGHT = {self.get_config('gate_design.max_height')}  # m",
            f"DESIGN_FLOW = {self.get_config('gate_design.design_flow')}  # m³/s",
            f"CHECK_FLOW = {self.get_config('gate_design.check_flow')}  # m³/s",
            "",
            "# 控制参数",
            f"CONTROL_LEVEL = \"{self.get_config('control_system.level')}\"",
            f"PID_KP = {self.get_config('control_system.controller.Kp')}",
            f"PID_KI = {self.get_config('control_system.controller.Ki')}",
            f"PID_KD = {self.get_config('control_system.controller.Kd')}",
            "",
            "# TODO: 在此添加你的代码",
            "",
            "if __name__ == '__main__':",
            "    print(f'项目: {PROJECT_NAME}')",
            f"    print(f'闸门尺寸: {{GATE_WIDTH}}m × {{GATE_HEIGHT}}m')",
            f"    print(f'设计流量: {{DESIGN_FLOW}} m³/s')",
            f"    print(f'智能化等级: {{CONTROL_LEVEL}}')",
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(code_lines))
        
        print(f"✓ Python代码已生成: {output_file}")

# ============================================================================
# 交互式界面
# ============================================================================

def interactive_mode():
    """交互式模式"""
    print("进入交互式配置模式")
    print("输入 'help' 查看帮助")
    print()
    
    generator = ConfigGenerator()
    
    while True:
        try:
            cmd = input("config> ").strip()
            
            if not cmd:
                continue
            
            if cmd == 'help':
                print("""
可用命令:
  template <name>       - 加载模板 (小型单闸/中型单闸/大型单闸/串级4闸)
  set <path> <value>    - 设置配置项
  get <path>            - 查看配置项
  show                  - 显示完整配置
  validate              - 验证配置
  save <file>           - 保存配置到文件 (默认: project_config.json)
  load <file>           - 从文件加载配置
  generate <file>       - 生成Python代码 (默认: generated_case.py)
  help                  - 显示帮助
  exit/quit             - 退出

示例:
  template 中型单闸
  set gate_design.width 4.0
  get gate_design.width
  save my_project.json
  generate my_case.py
                """)
            
            elif cmd.startswith('template '):
                template_name = cmd[9:].strip()
                generator.load_template(template_name)
            
            elif cmd.startswith('set '):
                parts = cmd[4:].split(maxsplit=1)
                if len(parts) != 2:
                    print("用法: set <path> <value>")
                    continue
                path, value_str = parts
                # 尝试转换为数值
                try:
                    if '.' in value_str:
                        value = float(value_str)
                    else:
                        value = int(value_str)
                except ValueError:
                    # 布尔值
                    if value_str.lower() in ['true', 'false']:
                        value = value_str.lower() == 'true'
                    else:
                        value = value_str
                generator.update_config(path, value)
            
            elif cmd.startswith('get '):
                path = cmd[4:].strip()
                value = generator.get_config(path)
                if value is not None:
                    print(f"{path} = {value}")
                else:
                    print(f"配置项不存在: {path}")
            
            elif cmd == 'show':
                generator.print_config()
            
            elif cmd == 'validate':
                generator.validate_config()
            
            elif cmd.startswith('save'):
                parts = cmd.split()
                filename = parts[1] if len(parts) > 1 else "project_config.json"
                generator.save_config(filename)
            
            elif cmd.startswith('load'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("用法: load <filename>")
                    continue
                generator.load_config(parts[1])
            
            elif cmd.startswith('generate'):
                parts = cmd.split()
                filename = parts[1] if len(parts) > 1 else "generated_case.py"
                generator.generate_python_code(filename)
            
            elif cmd in ['exit', 'quit']:
                print("再见!")
                break
            
            else:
                print(f"未知命令: {cmd}")
                print("输入 'help' 查看帮助")
        
        except KeyboardInterrupt:
            print("\n使用 'exit' 退出")
        except Exception as e:
            print(f"错误: {e}")

# ============================================================================
# 命令行模式
# ============================================================================

def command_line_mode():
    """命令行模式"""
    print("【示例1】使用默认配置")
    print("-" * 80)
    
    generator = ConfigGenerator()
    generator.print_config()
    generator.save_config("default_config.json")
    print()
    
    print("【示例2】使用模板")
    print("-" * 80)
    
    generator2 = ConfigGenerator()
    generator2.load_template("中型单闸")
    generator2.update_config("project_info.name", "某灌区主渠闸门")
    generator2.update_config("gate_design.design_flow", 12.0)
    generator2.validate_config()
    generator2.save_config("medium_gate_config.json")
    print()
    
    print("【示例3】生成Python代码")
    print("-" * 80)
    
    generator2.generate_python_code("medium_gate_case.py")
    print()
    
    print("="*80)
    print("  配置生成完成!")
    print("="*80)
    print()
    print("生成的文件:")
    print("  1. default_config.json - 默认配置")
    print("  2. medium_gate_config.json - 中型闸门配置")
    print("  3. medium_gate_case.py - Python代码模板")
    print()
    print("使用方法:")
    print("  1. 命令行模式: python3 config_generator.py")
    print("  2. 交互式模式: python3 config_generator.py --interactive")
    print("  3. 作为模块导入: from config_generator import ConfigGenerator")
    print()
    print("="*80)

# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    if '--interactive' in sys.argv or '-i' in sys.argv:
        interactive_mode()
    else:
        command_line_mode()
