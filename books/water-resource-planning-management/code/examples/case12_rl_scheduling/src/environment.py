"""
水库调度环境

定义强化学习环境：状态、动作、奖励
"""

import numpy as np
from typing import Tuple, Dict


class ReservoirEnv:
    """
    水库调度环境
    
    遵循OpenAI Gym接口规范
    """
    
    def __init__(
        self,
        min_storage: float = 50,      # 死库容（万m³）
        max_storage: float = 500,     # 最大库容
        normal_storage: float = 400,  # 正常库容
        min_discharge: float = 50,    # 最小出流（m³/s）
        max_discharge: float = 500,   # 最大出流
        n_actions: int = 10,          # 动作数量
        n_periods: int = 12,          # 时段数
        inflow_mean: float = 200,     # 平均入流
        inflow_std: float = 50        # 入流标准差
    ):
        """
        初始化环境
        
        Parameters
        ----------
        min_storage : float
            死库容（万m³）
        max_storage : float
            最大库容
        normal_storage : float
            正常库容
        min_discharge : float
            最小出流（m³/s）
        max_discharge : float
            最大出流
        n_actions : int
            离散动作数量
        n_periods : int
            调度时段数
        inflow_mean : float
            平均入流（m³/s）
        inflow_std : float
            入流标准差
        """
        self.min_storage = min_storage
        self.max_storage = max_storage
        self.normal_storage = normal_storage
        self.min_discharge = min_discharge
        self.max_discharge = max_discharge
        self.n_actions = n_actions
        self.n_periods = n_periods
        self.inflow_mean = inflow_mean
        self.inflow_std = inflow_std
        
        # 离散化动作空间
        self.actions = np.linspace(min_discharge, max_discharge, n_actions)
        
        # 状态
        self.current_storage = None
        self.current_inflow = None
        self.current_period = None
        
        # 历史记录
        self.episode_storage = []
        self.episode_discharge = []
        self.episode_power = []
    
    def reset(self, initial_storage: float = None) -> np.ndarray:
        """
        重置环境
        
        Parameters
        ----------
        initial_storage : float, optional
            初始库容，默认为正常库容
        
        Returns
        -------
        np.ndarray
            初始状态
        """
        if initial_storage is None:
            self.current_storage = self.normal_storage
        else:
            self.current_storage = initial_storage
        
        self.current_period = 0
        self.current_inflow = self._generate_inflow()
        
        # 清空历史
        self.episode_storage = [self.current_storage]
        self.episode_discharge = []
        self.episode_power = []
        
        return self._get_state()
    
    def step(self, action_idx: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        执行一步
        
        Parameters
        ----------
        action_idx : int
            动作索引
        
        Returns
        -------
        Tuple[np.ndarray, float, bool, Dict]
            (下一状态, 奖励, 是否结束, 信息)
        """
        # 获取动作
        discharge = self.actions[action_idx]
        
        # 计算发电功率
        power = self._calculate_power(discharge)
        
        # 水量平衡（时段长度1小时，转换单位）
        delta_storage = (self.current_inflow - discharge) * 3.6 / 10000  # 万m³
        next_storage = self.current_storage + delta_storage
        
        # 检查约束
        spill = 0.0  # 弃水量
        shortage = 0.0  # 水量短缺
        
        if next_storage > self.max_storage:
            spill = next_storage - self.max_storage
            next_storage = self.max_storage
        elif next_storage < self.min_storage:
            shortage = self.min_storage - next_storage
            next_storage = self.min_storage
        
        # 计算奖励
        reward = self._calculate_reward(power, spill, shortage, next_storage)
        
        # 更新状态
        self.current_storage = next_storage
        self.current_period += 1
        self.current_inflow = self._generate_inflow()
        
        # 记录
        self.episode_storage.append(next_storage)
        self.episode_discharge.append(discharge)
        self.episode_power.append(power)
        
        # 判断是否结束
        done = (self.current_period >= self.n_periods)
        
        # 下一状态
        next_state = self._get_state()
        
        # 额外信息
        info = {
            'power': power,
            'spill': spill,
            'shortage': shortage,
            'storage': next_storage
        }
        
        return next_state, reward, done, info
    
    def _get_state(self) -> np.ndarray:
        """
        获取当前状态
        
        Returns
        -------
        np.ndarray
            状态向量 [归一化库容, 归一化入流, 时段/周期]
        """
        # 归一化
        norm_storage = (self.current_storage - self.min_storage) / (self.max_storage - self.min_storage)
        norm_inflow = self.current_inflow / (2 * self.inflow_mean)  # 归一化到[0,1]
        norm_period = self.current_period / self.n_periods
        
        return np.array([norm_storage, norm_inflow, norm_period])
    
    def _generate_inflow(self) -> float:
        """
        生成入流（考虑季节性）
        
        Returns
        -------
        float
            入流量（m³/s）
        """
        # 季节因子
        season_factor = 1 + 0.3 * np.sin(2 * np.pi * self.current_period / self.n_periods)
        
        # 随机入流
        inflow = self.inflow_mean * season_factor + np.random.randn() * self.inflow_std
        
        return max(50, inflow)  # 确保非负
    
    def _calculate_power(self, discharge: float) -> float:
        """
        计算发电功率
        
        P = 9.81 * Q * H * η / 1000  (MW)
        
        Parameters
        ----------
        discharge : float
            出流（m³/s）
        
        Returns
        -------
        float
            发电功率（MW）
        """
        # 水头（简化：与库容线性相关）
        head = 50 + (self.current_storage - self.min_storage) / (self.max_storage - self.min_storage) * 50
        
        # 效率
        efficiency = 0.85
        
        # 功率
        power = 9.81 * discharge * head * efficiency / 1000
        
        return power
    
    def _calculate_reward(
        self,
        power: float,
        spill: float,
        shortage: float,
        storage: float
    ) -> float:
        """
        计算奖励
        
        Parameters
        ----------
        power : float
            发电功率（MW）
        spill : float
            弃水量（万m³）
        shortage : float
            短缺量（万m³）
        storage : float
            库容（万m³）
        
        Returns
        -------
        float
            奖励值
        """
        # 发电效益
        power_reward = power / 100  # 归一化
        
        # 弃水惩罚
        spill_penalty = -spill / 10
        
        # 短缺惩罚
        shortage_penalty = -shortage / 5
        
        # 偏离正常库容惩罚（终端时刻）
        deviation_penalty = 0
        if self.current_period == self.n_periods:
            deviation = abs(storage - self.normal_storage) / self.normal_storage
            deviation_penalty = -deviation * 2
        
        # 总奖励
        reward = power_reward + spill_penalty + shortage_penalty + deviation_penalty
        
        return reward
    
    def render(self):
        """显示当前状态（可选）"""
        print(f"Period {self.current_period}: Storage={self.current_storage:.1f}, "
              f"Inflow={self.current_inflow:.1f}")
