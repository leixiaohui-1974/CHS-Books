"""
水库模型

包含单库和梯级水库系统的基本模型
"""

import numpy as np
from typing import List, Dict, Tuple


class Reservoir:
    """
    单个水库模型
    
    包含水库的基本特性和计算方法
    """
    
    def __init__(self, config: Dict):
        """
        初始化
        
        Parameters
        ----------
        config : Dict
            水库配置参数
        """
        self.id = config['id']
        self.name = config['name']
        self.normal_level = config['normal_level']
        self.dead_level = config['dead_level']
        self.max_capacity = config['max_capacity']
        self.installed_capacity = config['installed_capacity']
        self.efficiency = config['efficiency']
        self.initial_level = config['initial_level']
        
        # 库容曲线参数
        self.vs_params = None
        # 尾水位曲线参数
        self.tw_params = None
    
    def level_to_storage(self, level: float) -> float:
        """
        水位转库容
        
        V = a + b*Z + c*Z^2
        
        Parameters
        ----------
        level : float
            水位 (m)
        
        Returns
        -------
        float
            库容 (亿m³)
        """
        if self.vs_params is None:
            # 简化：线性关系
            return (level - self.dead_level) / (self.normal_level - self.dead_level) * self.max_capacity
        
        a, b, c = self.vs_params['a'], self.vs_params['b'], self.vs_params['c']
        return a + b * level + c * level ** 2
    
    def storage_to_level(self, storage: float) -> float:
        """
        库容转水位（数值求解）
        
        Parameters
        ----------
        storage : float
            库容 (亿m³)
        
        Returns
        -------
        float
            水位 (m)
        """
        # 简化：线性插值
        return self.dead_level + (storage / self.max_capacity) * (self.normal_level - self.dead_level)
    
    def get_tailwater_level(self, discharge: float) -> float:
        """
        计算尾水位
        
        Z_tail = a + b*Q
        
        Parameters
        ----------
        discharge : float
            出库流量 (m³/s)
        
        Returns
        -------
        float
            尾水位 (m)
        """
        if self.tw_params is None:
            # 简化：固定尾水位
            return self.dead_level - 100
        
        a, b = self.tw_params['a'], self.tw_params['b']
        return a + b * discharge
    
    def calculate_power(
        self,
        storage: float,
        discharge: float,
        next_storage: float = None
    ) -> float:
        """
        计算发电功率
        
        P = 9.81 × Q × H × η / 1000  (MW)
        
        Parameters
        ----------
        storage : float
            库容 (亿m³)
        discharge : float
            出库流量 (m³/s)
        next_storage : float, optional
            下一时段库容，用于计算平均水头
        
        Returns
        -------
        float
            发电功率 (MW)
        """
        # 当前水位
        level = self.storage_to_level(storage)
        
        # 平均水位
        if next_storage is not None:
            next_level = self.storage_to_level(next_storage)
            avg_level = (level + next_level) / 2
        else:
            avg_level = level
        
        # 尾水位
        tailwater = self.get_tailwater_level(discharge)
        
        # 净水头
        net_head = avg_level - tailwater
        
        # 发电功率（不超过装机容量）
        power = min(
            9.81 * discharge * net_head * self.efficiency / 1000,
            self.installed_capacity
        )
        
        return max(0, power)
    
    def water_balance(
        self,
        storage: float,
        inflow: float,
        discharge: float,
        delta_t: float = 864000  # 10天 (秒)
    ) -> float:
        """
        水量平衡方程
        
        V_t+1 = V_t + (I_t - Q_t) × Δt
        
        Parameters
        ----------
        storage : float
            当前库容 (亿m³)
        inflow : float
            入流 (m³/s)
        discharge : float
            出库流量 (m³/s)
        delta_t : float
            时段长度 (秒)，默认10天
        
        Returns
        -------
        float
            下一时段库容 (亿m³)
        """
        # 转换单位：m³/s × s → m³ → 亿m³
        delta_storage = (inflow - discharge) * delta_t / 1e8
        
        next_storage = storage + delta_storage
        
        # 约束在库容范围内
        next_storage = np.clip(
            next_storage,
            self.level_to_storage(self.dead_level),
            self.max_capacity
        )
        
        return next_storage


class CascadeSystem:
    """
    梯级水库系统
    
    管理多个水库及其水力联系
    """
    
    def __init__(self, reservoirs: List[Reservoir], cascade_relations: List[Dict]):
        """
        初始化
        
        Parameters
        ----------
        reservoirs : List[Reservoir]
            水库列表
        cascade_relations : List[Dict]
            梯级关系
        """
        self.reservoirs = {r.id: r for r in reservoirs}
        self.cascade_relations = cascade_relations
        
        # 构建拓扑关系
        self.downstream_of = {}
        for rel in cascade_relations:
            self.downstream_of[rel['upstream']] = rel['downstream']
    
    def get_downstream(self, reservoir_id: int) -> int:
        """
        获取下游水库ID
        
        Parameters
        ----------
        reservoir_id : int
            水库ID
        
        Returns
        -------
        int or None
            下游水库ID，如果没有则返回None
        """
        return self.downstream_of.get(reservoir_id)
    
    def calculate_system_power(
        self,
        storages: Dict[int, float],
        discharges: Dict[int, float],
        next_storages: Dict[int, float] = None
    ) -> float:
        """
        计算系统总出力
        
        Parameters
        ----------
        storages : Dict[int, float]
            各水库库容
        discharges : Dict[int, float]
            各水库出库流量
        next_storages : Dict[int, float], optional
            各水库下一时段库容
        
        Returns
        -------
        float
            系统总出力 (MW)
        """
        total_power = 0
        
        for res_id, reservoir in self.reservoirs.items():
            ns = next_storages[res_id] if next_storages else None
            power = reservoir.calculate_power(
                storages[res_id],
                discharges[res_id],
                ns
            )
            total_power += power
        
        return total_power
    
    def simulate(
        self,
        initial_storages: Dict[int, float],
        discharges: Dict[int, List[float]],
        inflows: Dict[int, List[float]],
        delta_t: float = 864000
    ) -> Tuple[Dict, float]:
        """
        模拟梯级系统运行
        
        Parameters
        ----------
        initial_storages : Dict[int, float]
            初始库容
        discharges : Dict[int, List[float]]
            各水库各时段出库流量
        inflows : Dict[int, List[float]]
            各水库各时段区间入流
        delta_t : float
            时段长度 (秒)
        
        Returns
        -------
        Tuple[Dict, float]
            (运行结果, 总发电量)
        """
        n_periods = len(inflows[1])
        
        # 初始化结果
        results = {
            'storages': {rid: [initial_storages[rid]] for rid in self.reservoirs},
            'levels': {rid: [] for rid in self.reservoirs},
            'powers': {rid: [] for rid in self.reservoirs},
            'inflows': inflows,
            'discharges': discharges
        }
        
        total_energy = 0
        
        for t in range(n_periods):
            # 当前状态
            current_storages = {rid: results['storages'][rid][t] for rid in self.reservoirs}
            current_discharges = {rid: discharges[rid][t] for rid in self.reservoirs}
            
            # 计算各水库入流（区间入流 + 上游来水）
            total_inflows = {}
            for rid, reservoir in self.reservoirs.items():
                # 区间入流
                total_inflows[rid] = inflows[rid][t]
                
                # 上游来水
                for rel in self.cascade_relations:
                    if rel['downstream'] == rid:
                        upstream_id = rel['upstream']
                        total_inflows[rid] += discharges[upstream_id][t]
            
            # 水量平衡
            next_storages = {}
            for rid, reservoir in self.reservoirs.items():
                next_storages[rid] = reservoir.water_balance(
                    current_storages[rid],
                    total_inflows[rid],
                    current_discharges[rid],
                    delta_t
                )
                results['storages'][rid].append(next_storages[rid])
                results['levels'][rid].append(reservoir.storage_to_level(next_storages[rid]))
            
            # 计算发电量
            for rid, reservoir in self.reservoirs.items():
                power = reservoir.calculate_power(
                    current_storages[rid],
                    current_discharges[rid],
                    next_storages[rid]
                )
                results['powers'][rid].append(power)
                
                # 累计电量 (MWh)
                energy = power * delta_t / 3600
                total_energy += energy
        
        return results, total_energy
