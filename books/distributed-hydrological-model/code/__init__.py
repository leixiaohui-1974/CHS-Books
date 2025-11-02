"""
分布式水文模型 (Distributed Hydrological Model)
===================================================

CHS-Books系列第五本教材的配套Python包

主要模块:
---------
- basin: 流域分析与处理
- interpolation: 空间插值方法
- runoff_generation: 产流模拟
- slope_routing: 坡面汇流
- channel_routing: 河道汇流
- evapotranspiration: 蒸散发计算
- calibration: 参数率定
- assimilation: 数据同化
- coupling: 耦合模拟
- human_impact: 人类活动影响
- utils: 工具函数

版本: 0.1.0-alpha
作者: CHS-Books项目组
日期: 2025-11-02
"""

__version__ = '0.1.0-alpha'
__author__ = 'CHS-Books Team'

# 导入核心模块
from . import core
from . import models

# 导出常用类和函数
__all__ = [
    'core',
    'models',
    '__version__',
    '__author__',
]
