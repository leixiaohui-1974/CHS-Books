# -*- coding: utf-8 -*-
"""
增强所有案例的示意图说明
添加详细的中英文对照和指标说明
"""
import sys
import io
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = BASE_DIR / "books" / "water-system-control" / "code" / "examples"

# 各案例的关键指标说明
CASE_PARAMETERS = {
    'case_01_home_water_tower': {
        'title': '家庭水塔开关控制系统',
        'params': [
            ('h(t)', '水位高度（Water Level）', '单位：米（m）'),
            ('h_upper', '上限水位（Upper Limit）', '2.8m，泵停止工作'),
            ('h_lower', '下限水位（Lower Limit）', '2.3m，泵启动工作'),
            ('h_setpoint', '目标水位（Target）', '2.55m（中间值）'),
            ('Δh', '滞环宽度（Hysteresis）', '0.5m = h_upper - h_lower'),
            ('A', '水箱横截面积（Tank Area）', 'A = 2.0 m²'),
            ('R', '阻力系数（Resistance）', 'R = 5.0 min/m²'),
            ('K', '泵流量（Pump Flow）', 'K = 1.2 m³/min'),
            ('u(t)', '泵状态（Pump State）', 'ON/OFF（1/0）'),
            ('Q_in', '进水流量（Inflow）', 'Q_in = K·u(t)'),
            ('Q_out', '出水流量（Outflow）', '用户用水，扰动源'),
        ]
    },
    'case_02_cooling_tower': {
        'title': '冷却塔比例控制系统',
        'params': [
            ('h(t)', '水位高度（Water Level）', '单位：米（m）'),
            ('h_setpoint', '目标水位（Setpoint）', '3.0m'),
            ('A', '水箱横截面积（Tank Area）', 'A = 2.0 m²'),
            ('R', '阻力系数（Resistance）', 'R = 2.0 min/m²'),
            ('K', '泵增益（Pump Gain）', 'K = 1.0 m³/min'),
            ('Kp', '比例增益（Proportional Gain）', 'Kp = 1.2'),
            ('e(t)', '误差（Error）', 'e = h_setpoint - h(t)'),
            ('u(t)', '控制输出（Control Signal）', 'u = Kp·e（0-100%）'),
            ('Q_in', '进水流量（Inflow）', 'Q_in = K·u(t)'),
            ('Q_out', '出水流量（Outflow）', '蒸发+冷却负载'),
        ]
    },
    'case_03_water_supply_station': {
        'title': '供水泵站PI控制系统',
        'params': [
            ('h(t)', '水位高度（Water Level）', '单位：米（m）'),
            ('h_setpoint', '目标水位（Setpoint）', '3.0m'),
            ('A', '水箱横截面积（Tank Area）', 'A = 2.0 m²'),
            ('R', '阻力系数（Resistance）', 'R = 2.0 min/m²'),
            ('K', '泵增益（Pump Gain）', 'K = 1.0 m³/min'),
            ('Kp', '比例增益（Proportional Gain）', 'Kp = 1.5'),
            ('Ki', '积分增益（Integral Gain）', 'Ki = 0.3'),
            ('u(t)', '控制输出（Control Signal）', '0-100%'),
            ('Q_in', '进水流量（Inflow）', 'Q_in = K·u(t)'),
            ('Q_out', '出水流量（Outflow）', '用户需求，扰动源'),
        ]
    },
    'case_04_pid_tuning': {
        'title': 'PID控制系统',
        'params': [
            ('h(t)', '水位高度（Water Level）', '单位：米（m）'),
            ('h_setpoint', '目标水位（Setpoint）', '3.0m'),
            ('Kp', '比例增益（Proportional Gain）', 'Kp = 2.0'),
            ('Ki', '积分增益（Integral Gain）', 'Ki = 0.5'),
            ('Kd', '微分增益（Derivative Gain）', 'Kd = 0.5'),
            ('e(t)', '误差（Error）', 'e = h_setpoint - h(t)'),
            ('P(t)', '比例项（P-term）', 'P = Kp·e'),
            ('I(t)', '积分项（I-term）', 'I = Ki·∫e dt'),
            ('D(t)', '微分项（D-term）', 'D = Kd·de/dt'),
            ('u(t)', '控制输出（Control Output）', 'u = P + I + D'),
        ]
    },
}

def generate_parameter_description(case_id):
    """生成参数说明文本"""
    if case_id not in CASE_PARAMETERS:
        return None
    
    info = CASE_PARAMETERS[case_id]
    lines = []
    lines.append('**🔍 图中关键指标说明：**')
    
    for param, desc_cn, value in info['params']:
        lines.append(f'- **{param}**：{desc_cn}，{value}')
    
    return '\n'.join(lines)

def main():
    print("="*80)
    print("  📝 增强示意图说明 - 添加中英文对照")
    print("="*80)
    print()
    
    # 目前只手动增强了案例3
    # 其他案例需要根据实际情况定制
    
    print("✅ 案例3已手动增强完成")
    print()
    print("📋 可用参数模板：")
    for case_id, info in CASE_PARAMETERS.items():
        print(f"\n{case_id}:")
        print(f"  标题: {info['title']}")
        print(f"  参数数: {len(info['params'])}")
    
    print()
    print("="*80)
    print("  💡 说明")
    print("="*80)
    print("""
为了确保准确性，建议手动为每个案例添加参数说明：

1. 参考案例3的格式
2. 列出图中所有可见的参数
3. 提供中英文对照
4. 说明参数的具体数值
5. 解释参数的物理意义

格式示例：
**🔍 图中关键指标说明：**
- **参数符号**：中文名称（English Name），具体数值或说明
    """)
    print("="*80)

if __name__ == '__main__':
    main()



