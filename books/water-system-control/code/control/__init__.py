#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
控制模块包
"""

# 导入教学用基础控制器（优先）
try:
    from .basic_controllers import (OnOffController, ProportionalController, 
                                   PIController, PIDController, 
                                   ziegler_nichols_first_method)
    __all__ = ['OnOffController', 'ProportionalController', 'PIController', 
               'PIDController', 'ziegler_nichols_first_method']
except ImportError as e:
    __all__ = []

# 导入原有控制器（可选，如果存在）
try:
    from .base_controller import BaseController
    __all__.append('BaseController')
except ImportError:
    pass

try:
    from .pid import PIDController
    __all__.append('PIDController')
except ImportError:
    pass
