"""
地下水数字孪生模块

实现地下水系统的数字孪生框架，整合物理模型、观测系统和数据同化。

数字孪生概念:
-----------
数字孪生（Digital Twin）是物理系统的虚拟副本，能够：
1. 实时反映物理系统状态
2. 预测未来演化
3. 支持决策优化
4. 全生命周期管理

地下水数字孪生组成:
1. 物理模型：数值模拟器
2. 观测系统：监测井网
3. 数据同化：卡尔曼滤波
4. 状态估计：实时更新
5. 预测模块：未来预测

参考文献:
    - Grieves, M. (2014). Digital Twin: Manufacturing Excellence through 
      Virtual Factory Replication.
    - Liu, Y., et al. (2021). A novel cloud-based framework for the elderly 
      healthcare services using digital twin.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
import time

from .kalman_filter import KalmanFilter, EnsembleKalmanFilter, compute_rmse
from .observation import ObservationSystem


@dataclass
class DigitalTwinState:
    """数字孪生状态快照"""
    time: float
    state_estimate: np.ndarray    # 状态估计
    state_covariance: np.ndarray  # 状态协方差
    observations: np.ndarray      # 观测数据
    prediction: np.ndarray        # 预测值
    rmse: float                   # 与真实值的RMSE


class GroundwaterDigitalTwin:
    """
    地下水数字孪生系统
    
    整合物理模型、观测系统和数据同化，实现地下水系统的
    实时状态估计、预测和管理。
    
    Parameters
    ----------
    model : Callable
        地下水物理模型（函数或对象）
        应接受当前状态和时间步长，返回下一状态
    observation_system : ObservationSystem
        观测系统
    use_enkf : bool
        是否使用集合卡尔曼滤波（True）或标准卡尔曼滤波（False）
    n_ensemble : int, optional
        集合成员数（仅EnKF使用）
    process_noise_std : float
        过程噪声标准差
    name : str
        数字孪生名称
    
    Attributes
    ----------
    history : List[DigitalTwinState]
        状态历史
    
    Examples
    --------
    >>> def simple_model(state, dt):
    ...     return state * 0.99  # 简单衰减模型
    >>> obs_sys = ObservationSystem(nx=50, ny=50, dx=100, dy=100)
    >>> dt = GroundwaterDigitalTwin(simple_model, obs_sys)
    >>> dt.initialize(initial_state, initial_cov)
    >>> for t in range(100):
    ...     obs = obs_sys.generate_observations(true_state[t])
    ...     dt.assimilate_and_update(obs, dt=1.0)
    """
    
    def __init__(
        self,
        model: Callable,
        observation_system: ObservationSystem,
        use_enkf: bool = False,
        n_ensemble: int = 50,
        process_noise_std: float = 0.01,
        name: str = "GW_DigitalTwin"
    ):
        self.model = model
        self.obs_system = observation_system
        self.use_enkf = use_enkf
        self.n_ensemble = n_ensemble
        self.process_noise_std = process_noise_std
        self.name = name
        
        # 状态变量
        self.current_time = 0.0
        self.current_state = None
        self.current_cov = None
        self.ensemble = None  # 仅EnKF使用
        
        # 历史记录
        self.history: List[DigitalTwinState] = []
        
        # 数据同化器（延迟初始化）
        self.filter = None
        
        # 网格参数（从observation_system获取）
        self.nx = observation_system.nx
        self.ny = observation_system.ny
        self.n_states = self.nx * self.ny
    
    def initialize(
        self,
        initial_state: np.ndarray,
        initial_cov: Optional[np.ndarray] = None,
        initial_std: float = 1.0
    ) -> None:
        """
        初始化数字孪生
        
        Parameters
        ----------
        initial_state : np.ndarray
            初始状态（可以是2D场或1D向量）
        initial_cov : np.ndarray, optional
            初始协方差矩阵
        initial_std : float
            初始不确定性标准差（如果initial_cov未提供）
        """
        # 确保状态是1D向量
        if initial_state.ndim == 2:
            self.current_state = initial_state.flatten()
        else:
            self.current_state = initial_state.copy()
        
        # 初始化协方差
        if initial_cov is None:
            self.current_cov = (initial_std ** 2) * np.eye(self.n_states)
        else:
            self.current_cov = initial_cov.copy()
        
        # 获取观测矩阵和观测噪声协方差
        H = self.obs_system.get_observation_matrix()
        R = self.obs_system.get_observation_covariance()
        
        # 初始化滤波器
        if self.use_enkf:
            # 集合卡尔曼滤波
            self.filter = EnsembleKalmanFilter(
                n_ensemble=self.n_ensemble,
                H=H,
                R=R
            )
            # 从初始状态和协方差生成集合
            self.ensemble = np.random.multivariate_normal(
                self.current_state,
                self.current_cov,
                size=self.n_ensemble
            )
        else:
            # 标准卡尔曼滤波
            # 状态转移矩阵（简化为单位阵，实际应从模型线性化获得）
            F = np.eye(self.n_states)
            # 过程噪声协方差
            Q = (self.process_noise_std ** 2) * np.eye(self.n_states)
            self.filter = KalmanFilter(F=F, H=H, Q=Q, R=R)
        
        self.current_time = 0.0
        self.history = []
        
        print(f"[{self.name}] 初始化完成")
        print(f"  - 状态维度: {self.n_states}")
        print(f"  - 观测井数: {self.obs_system.n_wells}")
        print(f"  - 滤波方法: {'EnKF' if self.use_enkf else 'KF'}")
        if self.use_enkf:
            print(f"  - 集合规模: {self.n_ensemble}")
    
    def predict_step(self, dt: float) -> np.ndarray:
        """
        预测步：运行物理模型预测下一状态
        
        Parameters
        ----------
        dt : float
            时间步长
        
        Returns
        -------
        predicted_state : np.ndarray
            预测的状态
        """
        if self.use_enkf:
            # EnKF: 为每个集合成员运行模型
            predicted_ensemble = np.zeros_like(self.ensemble)
            for i in range(self.n_ensemble):
                state_2d = self.ensemble[i].reshape((self.ny, self.nx))
                # 添加过程噪声
                noise = np.random.normal(0, self.process_noise_std, 
                                        size=state_2d.shape)
                predicted_2d = self.model(state_2d + noise, dt)
                predicted_ensemble[i] = predicted_2d.flatten()
            
            # 集合均值作为预测
            predicted_state = np.mean(predicted_ensemble, axis=0)
            self.ensemble = predicted_ensemble
        else:
            # 标准KF: 运行模型一次
            state_2d = self.current_state.reshape((self.ny, self.nx))
            predicted_2d = self.model(state_2d, dt)
            predicted_state = predicted_2d.flatten()
        
        return predicted_state
    
    def assimilate_and_update(
        self,
        observations: np.ndarray,
        dt: float,
        true_state: Optional[np.ndarray] = None
    ) -> Dict:
        """
        数据同化和状态更新
        
        执行完整的预测-更新循环：
        1. 运行模型预测
        2. 同化观测数据
        3. 更新状态估计
        
        Parameters
        ----------
        observations : np.ndarray
            观测数据
        dt : float
            时间步长
        true_state : np.ndarray, optional
            真实状态（用于评估）
        
        Returns
        -------
        info : Dict
            包含预测、更新等信息的字典
        """
        # 1. 预测步
        predicted_state = self.predict_step(dt)
        
        # 2. 更新步（数据同化）
        if self.use_enkf:
            # EnKF更新
            self.ensemble = self.filter.assimilate(self.ensemble, observations)
            updated_state, updated_cov = self.filter.get_mean_and_cov(
                self.ensemble
            )
        else:
            # 标准KF更新
            # 首先用F @ x预测（这里简化，假设模型输出就是预测）
            # 实际应该用KF的predict方法
            result = self.filter.filter_step(
                self.current_state,
                self.current_cov,
                observations
            )
            updated_state = result.x_update
            updated_cov = result.P_update
        
        # 3. 更新当前状态
        self.current_state = updated_state
        self.current_cov = updated_cov
        self.current_time += dt
        
        # 4. 计算评估指标
        rmse = np.nan
        if true_state is not None:
            true_flat = true_state.flatten() if true_state.ndim == 2 else true_state
            rmse = compute_rmse(updated_state, true_flat)
        
        # 5. 记录历史
        snapshot = DigitalTwinState(
            time=self.current_time,
            state_estimate=updated_state.copy(),
            state_covariance=updated_cov.copy() if updated_cov is not None else None,
            observations=observations.copy(),
            prediction=predicted_state.copy(),
            rmse=rmse
        )
        self.history.append(snapshot)
        
        # 6. 返回信息
        info = {
            'time': self.current_time,
            'predicted_state': predicted_state,
            'updated_state': updated_state,
            'observations': observations,
            'rmse': rmse
        }
        
        return info
    
    def forecast(
        self,
        n_steps: int,
        dt: float
    ) -> np.ndarray:
        """
        预测未来状态（无观测数据同化）
        
        Parameters
        ----------
        n_steps : int
            预测步数
        dt : float
            时间步长
        
        Returns
        -------
        forecasts : np.ndarray
            预测轨迹 (n_steps × n_states)
        """
        forecasts = np.zeros((n_steps, self.n_states))
        current = self.current_state.copy()
        
        for step in range(n_steps):
            state_2d = current.reshape((self.ny, self.nx))
            forecast_2d = self.model(state_2d, dt)
            current = forecast_2d.flatten()
            forecasts[step] = current
        
        return forecasts
    
    def get_uncertainty_bounds(
        self,
        n_std: float = 2.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取状态估计的不确定性区间
        
        Parameters
        ----------
        n_std : float
            标准差倍数
        
        Returns
        -------
        lower_bound : np.ndarray
            下界
        upper_bound : np.ndarray
            上界
        """
        std = np.sqrt(np.diag(self.current_cov))
        lower_bound = self.current_state - n_std * std
        upper_bound = self.current_state + n_std * std
        return lower_bound, upper_bound
    
    def get_state_2d(self) -> np.ndarray:
        """
        获取当前状态的2D场
        
        Returns
        -------
        state_2d : np.ndarray
            2D状态场 (ny × nx)
        """
        return self.current_state.reshape((self.ny, self.nx))
    
    def get_history_array(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        获取历史记录的数组形式
        
        Returns
        -------
        times : np.ndarray
            时间序列
        states : np.ndarray
            状态序列 (n_times × n_states)
        rmses : np.ndarray
            RMSE序列
        """
        n_history = len(self.history)
        times = np.array([snap.time for snap in self.history])
        states = np.array([snap.state_estimate for snap in self.history])
        rmses = np.array([snap.rmse for snap in self.history])
        return times, states, rmses
    
    def summary(self) -> str:
        """
        生成数字孪生摘要信息
        
        Returns
        -------
        summary : str
            摘要文本
        """
        lines = [
            f"\n{'='*60}",
            f"地下水数字孪生系统摘要 - {self.name}",
            f"{'='*60}",
            f"当前时间: {self.current_time:.1f}",
            f"状态维度: {self.n_states}",
            f"观测井数: {self.obs_system.n_wells}",
            f"滤波方法: {'集合卡尔曼滤波 (EnKF)' if self.use_enkf else '标准卡尔曼滤波 (KF)'}",
        ]
        
        if self.use_enkf:
            lines.append(f"集合规模: {self.n_ensemble}")
        
        lines.append(f"历史记录: {len(self.history)} 个时间步")
        
        if len(self.history) > 0:
            last_rmse = self.history[-1].rmse
            if not np.isnan(last_rmse):
                lines.append(f"最新RMSE: {last_rmse:.4f} m")
        
        # 状态统计
        state_2d = self.get_state_2d()
        lines.extend([
            f"\n当前状态统计:",
            f"  均值: {np.mean(state_2d):.2f} m",
            f"  最小: {np.min(state_2d):.2f} m",
            f"  最大: {np.max(state_2d):.2f} m",
            f"  标准差: {np.std(state_2d):.2f} m",
        ])
        
        # 不确定性
        std_1d = np.sqrt(np.diag(self.current_cov))
        lines.extend([
            f"\n不确定性统计:",
            f"  平均不确定性: {np.mean(std_1d):.4f} m",
            f"  最大不确定性: {np.max(std_1d):.4f} m",
        ])
        
        lines.append(f"{'='*60}\n")
        
        return "\n".join(lines)


def run_twin_cycle(
    digital_twin: GroundwaterDigitalTwin,
    true_states: np.ndarray,
    duration: float,
    dt_model: float,
    dt_obs: float
) -> Dict:
    """
    运行数字孪生循环
    
    Parameters
    ----------
    digital_twin : GroundwaterDigitalTwin
        数字孪生对象
    true_states : np.ndarray
        真实状态序列 (用于生成观测)
    duration : float
        运行时长
    dt_model : float
        模型时间步长
    dt_obs : float
        观测间隔
    
    Returns
    -------
    results : Dict
        运行结果
    """
    n_steps = int(duration / dt_model)
    obs_interval = int(dt_obs / dt_model)
    
    results = {
        'times': [],
        'states': [],
        'observations': [],
        'rmses': []
    }
    
    start_time = time.time()
    
    for step in range(n_steps):
        current_time = step * dt_model
        
        # 每隔obs_interval生成观测并同化
        if step % obs_interval == 0:
            true_state = true_states[step]
            obs = digital_twin.obs_system.generate_observations(true_state)
            info = digital_twin.assimilate_and_update(obs, dt_model, true_state)
            
            results['times'].append(current_time)
            results['states'].append(info['updated_state'])
            results['observations'].append(obs)
            results['rmses'].append(info['rmse'])
    
    elapsed_time = time.time() - start_time
    
    results['elapsed_time'] = elapsed_time
    results['times'] = np.array(results['times'])
    results['states'] = np.array(results['states'])
    results['rmses'] = np.array(results['rmses'])
    
    return results
