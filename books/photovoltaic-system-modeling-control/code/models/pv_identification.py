"""
光伏参数辨识模块
PV Parameter Identification

从测试数据中提取光伏电池/组件参数
"""

from typing import Tuple, Dict, List
import numpy as np
from scipy.optimize import minimize, curve_fit, least_squares


class ParameterExtractor:
    """
    参数提取器
    从I-V曲线提取光伏电池参数
    """
    
    def __init__(self):
        """初始化提取器"""
        self.k = 1.380649e-23  # 玻尔兹曼常数
        self.q = 1.602176634e-19  # 电子电荷
    
    def extract_from_key_points(self, 
                                Isc: float, 
                                Voc: float,
                                Imp: float,
                                Vmp: float,
                                T: float = 298.15,
                                Ns: int = 1) -> Dict:
        """
        从关键点提取参数(简化方法)
        
        Parameters:
        -----------
        Isc, Voc, Imp, Vmp : float
            关键点参数
        T : float
            温度(K)
        Ns : int
            串联电池数
            
        Returns:
        --------
        Dict : 提取的参数
        """
        Vt = self.k * T / self.q * Ns
        
        # 估算理想因子
        n = 1.3  # 典型值
        
        # 估算串联电阻
        Rs = (Voc - Vmp) / Imp - Vt * n / Imp * np.log(Isc / (Isc - Imp))
        Rs = max(0, Rs)
        
        # 估算并联电阻
        Rsh = (Vmp - Rs * Imp) / (Isc - Imp - Isc * np.exp((Vmp + Rs*Imp)/(n*Vt)))
        Rsh = max(10, Rsh)
        
        # 光生电流
        Iph = Isc * (1 + Rs / Rsh)
        
        # 反向饱和电流
        I0 = (Isc - Voc / Rsh) / (np.exp(Voc / (n*Vt)) - 1)
        I0 = max(1e-12, I0)
        
        return {
            'Iph': Iph,
            'I0': I0,
            'Rs': Rs,
            'Rsh': Rsh,
            'n': n,
            'method': 'key_points'
        }
    
    def extract_from_curve(self,
                          V_measured: np.ndarray,
                          I_measured: np.ndarray,
                          T: float = 298.15,
                          Ns: int = 1,
                          method: str = 'least_squares') -> Dict:
        """
        从完整I-V曲线提取参数(优化方法)
        
        Parameters:
        -----------
        V_measured, I_measured : np.ndarray
            测量的I-V数据
        T : float
            温度(K)
        Ns : int
            串联电池数
        method : str
            优化方法('least_squares', 'minimize', 'curve_fit')
            
        Returns:
        --------
        Dict : 提取的参数和拟合质量
        """
        Vt = self.k * T / self.q * Ns
        
        # 初值估计
        Isc = I_measured[0]
        Voc = V_measured[np.argmin(np.abs(I_measured))]
        
        P = V_measured * I_measured
        idx_mpp = np.argmax(P)
        Vmp = V_measured[idx_mpp]
        Imp = I_measured[idx_mpp]
        
        # 初始参数猜测
        x0 = [
            Isc * 1.01,      # Iph
            1e-9,            # I0
            0.005,           # Rs
            1000.0,          # Rsh
            1.3              # n
        ]
        
        # 参数边界
        bounds_lower = [Isc * 0.99, 1e-12, 0, 10, 1.0]
        bounds_upper = [Isc * 1.1, 1e-6, 1.0, 1e6, 2.0]
        
        def residual(params):
            """残差函数"""
            Iph, I0, Rs, Rsh, n = params
            I_model = self._current_model(V_measured, Iph, I0, Rs, Rsh, n, Vt)
            return I_measured - I_model
        
        # 优化求解
        if method == 'least_squares':
            result = least_squares(
                residual, x0,
                bounds=(bounds_lower, bounds_upper),
                ftol=1e-8,
                max_nfev=1000
            )
            params_opt = result.x
            success = result.success
            
        elif method == 'minimize':
            def objective(params):
                return np.sum(residual(params)**2)
            
            result = minimize(
                objective, x0,
                bounds=list(zip(bounds_lower, bounds_upper)),
                method='L-BFGS-B'
            )
            params_opt = result.x
            success = result.success
            
        else:  # curve_fit
            def model_func(V, Iph, I0, Rs, Rsh, n):
                return self._current_model(V, Iph, I0, Rs, Rsh, n, Vt)
            
            params_opt, _ = curve_fit(
                model_func,
                V_measured,
                I_measured,
                p0=x0,
                bounds=(bounds_lower, bounds_upper),
                maxfev=1000
            )
            success = True
        
        # 提取参数
        Iph, I0, Rs, Rsh, n = params_opt
        
        # 计算拟合质量
        I_fitted = self._current_model(V_measured, Iph, I0, Rs, Rsh, n, Vt)
        rmse = np.sqrt(np.mean((I_measured - I_fitted)**2))
        r2 = 1 - np.sum((I_measured - I_fitted)**2) / np.sum((I_measured - np.mean(I_measured))**2)
        
        return {
            'Iph': Iph,
            'I0': I0,
            'Rs': Rs,
            'Rsh': Rsh,
            'n': n,
            'rmse': rmse,
            'r2': r2,
            'success': success,
            'method': method,
            'I_fitted': I_fitted
        }
    
    def _current_model(self, V, Iph, I0, Rs, Rsh, n, Vt):
        """
        单二极管模型电流计算
        """
        from scipy.optimize import fsolve
        
        I = np.zeros_like(V)
        for i, v in enumerate(V):
            def equation(I_val):
                return Iph - I0 * (np.exp((v + I_val*Rs)/(n*Vt)) - 1) - (v + I_val*Rs)/Rsh - I_val
            
            # 初值
            I_guess = Iph * (1 - v / (V[-1] + 1))
            try:
                I[i] = fsolve(equation, I_guess, full_output=False)[0]
            except:
                I[i] = 0
        
        return I


class ParameterComparator:
    """
    参数对比器
    对比不同辨识方法的结果
    """
    
    def __init__(self):
        """初始化对比器"""
        pass
    
    def compare_methods(self,
                       V_measured: np.ndarray,
                       I_measured: np.ndarray,
                       T: float = 298.15,
                       Ns: int = 1) -> Dict:
        """
        对比多种辨识方法
        
        Returns:
        --------
        Dict : 各方法的参数和性能对比
        """
        extractor = ParameterExtractor()
        
        # 方法1: 关键点法
        Isc = I_measured[0]
        Voc = V_measured[np.argmin(np.abs(I_measured))]
        P = V_measured * I_measured
        idx_mpp = np.argmax(P)
        Vmp = V_measured[idx_mpp]
        Imp = I_measured[idx_mpp]
        
        result_kp = extractor.extract_from_key_points(Isc, Voc, Imp, Vmp, T, Ns)
        
        # 方法2-4: 优化方法
        methods = ['least_squares', 'minimize', 'curve_fit']
        results = {'key_points': result_kp}
        
        for method in methods:
            try:
                result = extractor.extract_from_curve(
                    V_measured, I_measured, T, Ns, method
                )
                results[method] = result
            except Exception as e:
                print(f"方法 {method} 失败: {e}")
                results[method] = None
        
        return results
    
    def evaluate_accuracy(self, 
                         params: Dict,
                         V_measured: np.ndarray,
                         I_measured: np.ndarray,
                         T: float = 298.15,
                         Ns: int = 1) -> Dict:
        """
        评估参数精度
        """
        extractor = ParameterExtractor()
        Vt = extractor.k * T / extractor.q * Ns
        
        # 计算模型输出
        I_model = extractor._current_model(
            V_measured,
            params['Iph'],
            params['I0'],
            params['Rs'],
            params['Rsh'],
            params['n'],
            Vt
        )
        
        # 计算误差指标
        mae = np.mean(np.abs(I_measured - I_model))
        rmse = np.sqrt(np.mean((I_measured - I_model)**2))
        mape = np.mean(np.abs((I_measured - I_model) / (I_measured + 1e-10))) * 100
        r2 = 1 - np.sum((I_measured - I_model)**2) / np.sum((I_measured - np.mean(I_measured))**2)
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2': r2,
            'I_model': I_model
        }


class OnlineIdentification:
    """
    在线辨识
    实时更新参数
    """
    
    def __init__(self, initial_params: Dict):
        """
        初始化在线辨识器
        
        Parameters:
        -----------
        initial_params : Dict
            初始参数
        """
        self.params = initial_params.copy()
        self.history = []
    
    def update(self, 
              V_new: float,
              I_new: float,
              learning_rate: float = 0.1) -> Dict:
        """
        基于新数据更新参数(简化递推算法)
        
        Parameters:
        -----------
        V_new, I_new : float
            新的测量点
        learning_rate : float
            学习率
            
        Returns:
        --------
        Dict : 更新后的参数
        """
        # 简化的递推更新(实际应用中可使用RLS等)
        # 这里仅作演示
        
        # 记录历史
        self.history.append({
            'V': V_new,
            'I': I_new,
            'params': self.params.copy()
        })
        
        return self.params
