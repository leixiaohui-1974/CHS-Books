"""
数字孪生模块 (Digital Twin Module)

实现地下水系统的数字孪生框架，整合物理模型、观测系统和数据同化。

主要组件:
---------
- KalmanFilter: 标准卡尔曼滤波器
- EnsembleKalmanFilter: 集合卡尔曼滤波器（EnKF）
- ObservationSystem: 监测井观测系统
- GroundwaterDigitalTwin: 地下水数字孪生主类

Examples
--------
>>> from gwflow.digital_twin import GroundwaterDigitalTwin, ObservationSystem
>>> obs_sys = ObservationSystem(nx=50, ny=50, dx=100, dy=100)
>>> obs_sys.add_well(2500, 2500, noise_std=0.05)
>>> dt = GroundwaterDigitalTwin(model, obs_sys)
>>> dt.initialize(initial_state, initial_cov)
>>> dt.assimilate_and_update(observations, dt=1.0)
"""

from .kalman_filter import (
    KalmanFilter,
    EnsembleKalmanFilter,
    KalmanFilterResult,
    compute_rmse,
    compute_mae
)

from .observation import (
    ObservationWell,
    ObservationSystem,
    state_to_observations,
    compute_innovation,
    compute_observation_likelihood
)

from .digital_twin import (
    GroundwaterDigitalTwin,
    DigitalTwinState,
    run_twin_cycle
)

__all__ = [
    # Kalman Filter
    'KalmanFilter',
    'EnsembleKalmanFilter',
    'KalmanFilterResult',
    'compute_rmse',
    'compute_mae',
    
    # Observation System
    'ObservationWell',
    'ObservationSystem',
    'state_to_observations',
    'compute_innovation',
    'compute_observation_likelihood',
    
    # Digital Twin
    'GroundwaterDigitalTwin',
    'DigitalTwinState',
    'run_twin_cycle',
]
