"""
地面沉降模型

整合地下水流动和土层压缩
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
from .consolidation import SoilLayer, consolidation_settlement


def compute_effective_stress_change(
    head_change: float,
    gamma_water: float = 9.81
) -> float:
    """
    计算有效应力变化
    
    Terzaghi有效应力原理：
    Δσ' = -Δu = -γw * Δh
    
    水位下降 → 孔压降低 → 有效应力增加
    
    Parameters
    ----------
    head_change : float
        水头变化 [m]（负值表示下降）
    gamma_water : float, optional
        水的重度 [kN/m³]，默认9.81
    
    Returns
    -------
    delta_sigma : float
        有效应力增量 [kPa]
    """
    delta_sigma = -gamma_water * head_change
    return delta_sigma


def compute_layer_compression(
    layer: SoilLayer,
    delta_sigma: float,
    method: str = 'linear',
    sigma_0: Optional[float] = None
) -> float:
    """
    计算土层压缩量
    
    Parameters
    ----------
    layer : SoilLayer
        土层对象
    delta_sigma : float
        有效应力增量 [kPa]
    method : str, optional
        计算方法：'linear'（线性）或'logarithmic'（对数）
    sigma_0 : float, optional
        初始有效应力 [kPa]，对数法需要
    
    Returns
    -------
    compression : float
        压缩量 [m]
    """
    if method == 'linear':
        return layer.compute_compression_linear(delta_sigma)
    elif method == 'logarithmic':
        if sigma_0 is None:
            raise ValueError("sigma_0 required for logarithmic method")
        sigma_f = sigma_0 + delta_sigma
        return layer.compute_compression_logarithmic(sigma_0, sigma_f)
    else:
        raise ValueError(f"Unknown method: {method}")


class SubsidenceModel:
    """
    地面沉降模型
    
    整合地下水模型和土层压缩
    """
    
    def __init__(self, name: str = "SubsidenceModel"):
        """
        Parameters
        ----------
        name : str
            模型名称
        """
        self.name = name
        self.layers: List[SoilLayer] = []
    
    def add_layer(self, layer: SoilLayer):
        """添加土层"""
        self.layers.append(layer)
    
    def get_total_thickness(self) -> float:
        """获取总厚度"""
        return sum(layer.thickness for layer in self.layers)
    
    def compute_initial_stress(
        self,
        water_table: float,
        gamma_water: float = 9.81
    ) -> Dict[str, float]:
        """
        计算初始应力状态
        
        Parameters
        ----------
        water_table : float
            初始地下水位标高 [m]
        gamma_water : float
            水的重度 [kN/m³]
        
        Returns
        -------
        stress_profile : dict
            各层的初始有效应力 {layer_name: sigma_0}
        """
        stress_profile = {}
        
        for layer in self.layers:
            # 土层中点深度（从地表算）
            depth_mid = -layer.z_mid  # 假设地表为0，向下为负
            
            # 总应力
            sigma_total = layer.gamma_sat * depth_mid
            
            # 孔隙水压力
            if layer.z_mid < water_table:
                # 水位以下
                u = gamma_water * (water_table - layer.z_mid)
            else:
                # 水位以上
                u = 0
            
            # 有效应力
            sigma_0 = sigma_total - u
            stress_profile[layer.name] = sigma_0
        
        return stress_profile
    
    def compute_subsidence(
        self,
        head_changes: Dict[str, float],
        method: str = 'linear',
        sigma_0_dict: Optional[Dict[str, float]] = None
    ) -> Tuple[Dict[str, float], float]:
        """
        计算总沉降
        
        Parameters
        ----------
        head_changes : dict
            各层的水头变化 {layer_name: delta_h} [m]
        method : str
            压缩计算方法
        sigma_0_dict : dict, optional
            初始有效应力
        
        Returns
        -------
        layer_compressions : dict
            各层压缩量 {layer_name: delta_H} [m]
        total_subsidence : float
            总沉降量 [m]
        """
        layer_compressions = {}
        
        for layer in self.layers:
            delta_h = head_changes.get(layer.name, 0)
            delta_sigma = compute_effective_stress_change(delta_h)
            
            if method == 'logarithmic':
                sigma_0 = sigma_0_dict.get(layer.name, 100)  # 默认100kPa
            else:
                sigma_0 = None
            
            compression = compute_layer_compression(
                layer, delta_sigma, method, sigma_0
            )
            layer_compressions[layer.name] = compression
        
        total_subsidence = sum(layer_compressions.values())
        
        return layer_compressions, total_subsidence
    
    def simulate_time_series(
        self,
        head_history: Dict[str, np.ndarray],
        times: np.ndarray,
        method: str = 'linear',
        include_consolidation: bool = False
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        时间序列沉降模拟
        
        Parameters
        ----------
        head_history : dict
            水头历史 {layer_name: h(t)} [m]
        times : ndarray
            时间数组 [day]
        method : str
            压缩方法
        include_consolidation : bool
            是否考虑固结时间过程
        
        Returns
        -------
        total_subsidence : ndarray
            总沉降历史 [m]
        layer_subsidence : dict
            各层沉降历史 {layer_name: S(t)}
        """
        n_times = len(times)
        total_subsidence = np.zeros(n_times)
        layer_subsidence = {layer.name: np.zeros(n_times) for layer in self.layers}
        
        for i in range(1, n_times):
            dt = times[i] - times[i-1]
            
            for layer in self.layers:
                # 水头变化
                if layer.name in head_history:
                    delta_h = head_history[layer.name][i] - head_history[layer.name][i-1]
                else:
                    delta_h = 0
                
                # 有效应力变化
                delta_sigma = compute_effective_stress_change(delta_h)
                
                # 即时压缩量
                delta_S_instant = compute_layer_compression(layer, delta_sigma, method='linear')
                
                if include_consolidation and layer.Cv is not None:
                    # 考虑固结过程
                    H = layer.thickness / 2  # 双面排水
                    Tv = layer.Cv * dt / H**2
                    
                    # 简化：假设瞬时加载
                    from .consolidation import consolidation_degree
                    U = consolidation_degree(Tv)
                    delta_S = U * delta_S_instant
                else:
                    # 不考虑固结过程，瞬时发生
                    delta_S = delta_S_instant
                
                layer_subsidence[layer.name][i] = layer_subsidence[layer.name][i-1] + delta_S
            
            # 累加各层
            total_subsidence[i] = sum(
                layer_subsidence[name][i] for name in layer_subsidence
            )
        
        return total_subsidence, layer_subsidence
    
    def compute_subsidence_map(
        self,
        head_change_field: np.ndarray,
        X: np.ndarray,
        Y: np.ndarray,
        representative_layer_compression: float
    ) -> np.ndarray:
        """
        计算沉降空间分布
        
        Parameters
        ----------
        head_change_field : ndarray
            水头变化场 [m]
        X, Y : ndarray
            网格坐标
        representative_layer_compression : float
            代表性土层的单位水头降深压缩系数 [m/m]
        
        Returns
        -------
        subsidence_field : ndarray
            沉降场 [m]
        """
        # 简化：假设沉降与水头降深成正比
        subsidence_field = -head_change_field * representative_layer_compression
        return subsidence_field
    
    def get_statistics(self) -> Dict:
        """获取模型统计信息"""
        return {
            'n_layers': len(self.layers),
            'total_thickness': self.get_total_thickness(),
            'layer_names': [layer.name for layer in self.layers],
            'compressible_layers': sum(
                1 for layer in self.layers if layer.av is not None or layer.Cc is not None
            )
        }
    
    def __repr__(self):
        return f"SubsidenceModel('{self.name}', n_layers={len(self.layers)})"
