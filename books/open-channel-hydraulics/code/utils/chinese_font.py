"""
中文字体配置模块

用于matplotlib图形中正确显示中文字符

作者：CHS-Books项目
日期：2025-10-29
"""

import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path


def configure_chinese_font():
    """
    配置matplotlib以支持中文显示

    尝试多种方法：
    1. SimHei（黑体）
    2. Microsoft YaHei（微软雅黑）
    3. Arial Unicode MS
    4. 使用无衬线字体回退

    同时解决负号显示问题
    """
    # 尝试多种中文字体
    chinese_fonts = [
        'SimHei',  # 黑体（Windows）
        'Microsoft YaHei',  # 微软雅黑
        'Heiti TC',  # 黑体-繁（macOS）
        'STHeiti',  # 华文黑体（macOS）
        'Arial Unicode MS',  # 包含中文的Arial
        'WenQuanYi Micro Hei',  # 文泉驿微米黑（Linux）
        'Noto Sans CJK SC',  # 思源黑体（Linux）
        'DejaVu Sans'  # 回退（不显示中文，但不报错）
    ]

    # 设置字体族
    plt.rcParams['font.sans-serif'] = chinese_fonts

    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False

    # 设置默认字体大小
    plt.rcParams['font.size'] = 10

    return chinese_fonts[0]


def check_font_availability():
    """
    检查可用的中文字体

    Returns:
        available_fonts: 可用中文字体列表
    """
    import matplotlib.font_manager as fm

    # 获取所有可用字体
    all_fonts = set([f.name for f in fm.fontManager.ttflist])

    # 中文字体列表
    chinese_fonts = [
        'SimHei', 'Microsoft YaHei', 'Heiti TC', 'STHeiti',
        'Arial Unicode MS', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC'
    ]

    # 检查可用性
    available = [font for font in chinese_fonts if font in all_fonts]

    if not available:
        print("警告：未检测到中文字体，中文可能无法正确显示")
        print(f"建议安装：{', '.join(chinese_fonts[:3])}")
    else:
        print(f"检测到可用中文字体：{', '.join(available)}")

    return available


if __name__ == "__main__":
    # 测试
    available = check_font_availability()
    configure_chinese_font()
    print("中文字体配置完成")
