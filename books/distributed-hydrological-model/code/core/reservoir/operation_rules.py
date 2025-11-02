"""
水库调度规则库
=============

实现基于规则的水库优化调度。

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum


class ReservoirZone(Enum):
    """水库分区"""
    DEAD = 1      # 死库容
    CONSERVATION = 2  # 兴利库容
    FLOOD_LIMIT = 3   # 防洪限制水位以下
    FLOOD_CONTROL = 4  # 防洪库容
    DESIGN_FLOOD = 5   # 设计洪水位以下


class OperationRule:
    """调度规则基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def apply(self, state: Dict, inflow: float, time_step: int) -> float:
        """
        应用调度规则
        
        Parameters
        ----------
        state : dict
            水库状态（水位、库容等）
        inflow : float
            入库流量 (m³/s)
        time_step : int
            时间步
            
        Returns
        -------
        outflow : float
            出库流量 (m³/s)
        """
        raise NotImplementedError


class FloodControlRule(OperationRule):
    """防洪调度规则"""
    
    def __init__(self, flood_limit_level: float, 
                 design_flood_level: float,
                 max_outflow: float):
        super().__init__("防洪调度")
        self.flood_limit_level = flood_limit_level
        self.design_flood_level = design_flood_level
        self.max_outflow = max_outflow
    
    def apply(self, state: Dict, inflow: float, time_step: int) -> float:
        """防洪调度规则"""
        level = state['level']
        
        # 超过设计洪水位：全力泄洪
        if level >= self.design_flood_level:
            return min(inflow * 1.2, self.max_outflow)
        
        # 超过防洪限制水位：加大泄流
        elif level > self.flood_limit_level:
            # 线性插值
            ratio = (level - self.flood_limit_level) / \
                   (self.design_flood_level - self.flood_limit_level)
            return inflow * (0.8 + 0.4 * ratio)
        
        # 防洪限制水位以下：正常调度
        else:
            return min(inflow * 0.6, self.max_outflow * 0.5)


class ConservationRule(OperationRule):
    """兴利调度规则"""
    
    def __init__(self, normal_level: float,
                 dead_level: float,
                 min_outflow: float,
                 target_outflow: float):
        super().__init__("兴利调度")
        self.normal_level = normal_level
        self.dead_level = dead_level
        self.min_outflow = min_outflow
        self.target_outflow = target_outflow
    
    def apply(self, state: Dict, inflow: float, time_step: int) -> float:
        """兴利调度规则"""
        level = state['level']
        
        # 接近死水位：减小出流
        if level <= self.dead_level + 2.0:
            return self.min_outflow
        
        # 正常蓄水位以上：加大出流
        elif level > self.normal_level:
            return max(inflow, self.target_outflow)
        
        # 正常范围：按目标出流
        else:
            return self.target_outflow


class ReservoirRules:
    """
    水库调度规则集
    
    整合多个调度规则，根据水库状态选择合适的规则
    """
    
    def __init__(self):
        self.rules: List[OperationRule] = []
        self.characteristics = None
        
    def set_characteristics(self, 
                          dead_level: float,
                          normal_level: float,
                          flood_limit_level: float,
                          design_flood_level: float,
                          max_level: float,
                          dead_storage: float,
                          total_storage: float,
                          max_outflow: float):
        """
        设置水库特征参数
        
        Parameters
        ----------
        dead_level : float
            死水位 (m)
        normal_level : float
            正常蓄水位 (m)
        flood_limit_level : float
            防洪限制水位 (m)
        design_flood_level : float
            设计洪水位 (m)
        max_level : float
            校核洪水位 (m)
        dead_storage : float
            死库容 (万m³)
        total_storage : float
            总库容 (万m³)
        max_outflow : float
            最大泄流能力 (m³/s)
        """
        self.characteristics = {
            'dead_level': dead_level,
            'normal_level': normal_level,
            'flood_limit_level': flood_limit_level,
            'design_flood_level': design_flood_level,
            'max_level': max_level,
            'dead_storage': dead_storage,
            'total_storage': total_storage,
            'max_outflow': max_outflow
        }
        
        # 自动生成水位-库容关系（简化为线性）
        self.level_storage_curve = self._generate_level_storage_curve()
        
    def _generate_level_storage_curve(self) -> callable:
        """生成水位-库容关系曲线（简化线性）"""
        c = self.characteristics
        
        def curve(level: float) -> float:
            """水位→库容"""
            if level <= c['dead_level']:
                return c['dead_storage']
            elif level >= c['max_level']:
                return c['total_storage']
            else:
                # 线性插值
                ratio = (level - c['dead_level']) / \
                       (c['max_level'] - c['dead_level'])
                return c['dead_storage'] + \
                       (c['total_storage'] - c['dead_storage']) * ratio
        
        return curve
    
    def add_rule(self, rule: OperationRule):
        """添加调度规则"""
        self.rules.append(rule)
    
    def get_zone(self, level: float) -> ReservoirZone:
        """判断水库所在分区"""
        c = self.characteristics
        
        if level <= c['dead_level']:
            return ReservoirZone.DEAD
        elif level <= c['normal_level']:
            return ReservoirZone.CONSERVATION
        elif level <= c['flood_limit_level']:
            return ReservoirZone.FLOOD_LIMIT
        elif level <= c['design_flood_level']:
            return ReservoirZone.FLOOD_CONTROL
        else:
            return ReservoirZone.DESIGN_FLOOD
    
    def operate(self, 
                initial_level: float,
                inflow_series: np.ndarray,
                dt: float = 3600.0) -> Dict[str, np.ndarray]:
        """
        执行水库调度
        
        Parameters
        ----------
        initial_level : float
            初始水位 (m)
        inflow_series : ndarray
            入库流量序列 (m³/s)
        dt : float
            时间步长 (s)
            
        Returns
        -------
        results : dict
            调度结果
        """
        n_steps = len(inflow_series)
        
        # 初始化结果数组
        levels = np.zeros(n_steps)
        storages = np.zeros(n_steps)
        outflows = np.zeros(n_steps)
        zones = np.zeros(n_steps, dtype=int)
        
        # 初始状态
        levels[0] = initial_level
        storages[0] = self.level_storage_curve(initial_level)
        
        # 时间推进
        for t in range(n_steps - 1):
            inflow = inflow_series[t]
            level = levels[t]
            storage = storages[t]
            
            # 当前状态
            state = {
                'level': level,
                'storage': storage,
                'zone': self.get_zone(level)
            }
            zones[t] = state['zone'].value
            
            # 应用调度规则（选择第一个匹配的规则）
            outflow = self._select_and_apply_rule(state, inflow, t)
            
            # 限制出流范围
            outflow = np.clip(outflow, 0, self.characteristics['max_outflow'])
            outflows[t] = outflow
            
            # 水量平衡更新
            delta_storage = (inflow - outflow) * dt / 1e4  # 万m³
            new_storage = storage + delta_storage
            
            # 限制库容范围
            new_storage = np.clip(
                new_storage,
                self.characteristics['dead_storage'],
                self.characteristics['total_storage']
            )
            storages[t + 1] = new_storage
            
            # 反算水位
            levels[t + 1] = self._storage_to_level(new_storage)
        
        # 最后一步
        zones[-1] = self.get_zone(levels[-1]).value
        outflows[-1] = outflows[-2]  # 延续上一步
        
        return {
            'level': levels,
            'storage': storages,
            'outflow': outflows,
            'zone': zones,
            'inflow': inflow_series
        }
    
    def _select_and_apply_rule(self, state: Dict, 
                               inflow: float, 
                               time_step: int) -> float:
        """选择并应用调度规则"""
        zone = state['zone']
        
        # 根据分区选择规则
        if zone in [ReservoirZone.FLOOD_CONTROL, ReservoirZone.DESIGN_FLOOD]:
            # 防洪调度
            for rule in self.rules:
                if isinstance(rule, FloodControlRule):
                    return rule.apply(state, inflow, time_step)
        
        # 兴利调度
        for rule in self.rules:
            if isinstance(rule, ConservationRule):
                return rule.apply(state, inflow, time_step)
        
        # 默认：等流量泄放
        return inflow * 0.8
    
    def _storage_to_level(self, storage: float) -> float:
        """库容→水位（反算）"""
        c = self.characteristics
        
        if storage <= c['dead_storage']:
            return c['dead_level']
        elif storage >= c['total_storage']:
            return c['max_level']
        else:
            # 线性反算
            ratio = (storage - c['dead_storage']) / \
                   (c['total_storage'] - c['dead_storage'])
            return c['dead_level'] + \
                   (c['max_level'] - c['dead_level']) * ratio


if __name__ == '__main__':
    """测试水库调度规则"""
    print("测试水库调度规则...")
    
    # 创建水库
    reservoir = ReservoirRules()
    reservoir.set_characteristics(
        dead_level=100.0,
        normal_level=110.0,
        flood_limit_level=115.0,
        design_flood_level=120.0,
        max_level=125.0,
        dead_storage=1000.0,
        total_storage=10000.0,
        max_outflow=500.0
    )
    
    # 添加规则
    reservoir.add_rule(FloodControlRule(115.0, 120.0, 500.0))
    reservoir.add_rule(ConservationRule(110.0, 100.0, 10.0, 50.0))
    
    # 模拟入流
    n_days = 100
    inflow = np.ones(n_days) * 50.0
    inflow[30:40] = np.linspace(50, 300, 10)
    inflow[40:50] = np.linspace(300, 50, 10)
    
    # 调度
    results = reservoir.operate(110.0, inflow, dt=86400.0)
    
    print(f"初始水位: {results['level'][0]:.2f} m")
    print(f"最高水位: {np.max(results['level']):.2f} m")
    print(f"最大出流: {np.max(results['outflow']):.1f} m³/s")
    print("测试通过！")
