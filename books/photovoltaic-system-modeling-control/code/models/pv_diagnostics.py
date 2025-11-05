"""
光伏系统诊断模块
PV System Diagnostics

包含遮挡分析、故障诊断、性能评估等功能
"""

from typing import List, Tuple, Dict
import numpy as np
from .pv_module import PVModule
from .pv_array import PVArray


class ShadingAnalyzer:
    """
    遮挡分析器
    Shading Analyzer
    
    分析遮挡模式、热斑风险、功率损失
    """
    
    def __init__(self, module: PVModule):
        """
        初始化遮挡分析器
        
        Parameters:
        -----------
        module : PVModule
            待分析的组件模型
        """
        self.module = module
        self.Ns = module.Ns
        self.Nb = module.Nb
        self.cells_per_bypass = module.cells_per_bypass
    
    def analyze_shading_pattern(self, irradiances: List[float]) -> Dict:
        """
        分析遮挡模式
        
        Parameters:
        -----------
        irradiances : List[float]
            每片电池的辐照度(W/m²)
            
        Returns:
        --------
        Dict : 分析结果
        """
        irr_array = np.array(irradiances)
        
        # 计算统计信息
        mean_irr = np.mean(irr_array)
        std_irr = np.std(irr_array)
        min_irr = np.min(irr_array)
        max_irr = np.max(irr_array)
        
        # 识别遮挡电池
        threshold = mean_irr * 0.8  # 低于平均值80%视为遮挡
        shaded_cells = np.where(irr_array < threshold)[0]
        num_shaded = len(shaded_cells)
        shading_ratio = num_shaded / self.Ns
        
        # 识别受影响的旁路二极管组
        affected_groups = set()
        for cell_idx in shaded_cells:
            group_idx = cell_idx // self.cells_per_bypass
            affected_groups.add(group_idx)
        
        # 遮挡程度分类
        if shading_ratio < 0.05:
            severity = "无遮挡"
        elif shading_ratio < 0.2:
            severity = "轻度遮挡"
        elif shading_ratio < 0.5:
            severity = "中度遮挡"
        else:
            severity = "严重遮挡"
        
        return {
            'mean_irradiance': mean_irr,
            'std_irradiance': std_irr,
            'min_irradiance': min_irr,
            'max_irradiance': max_irr,
            'num_shaded_cells': num_shaded,
            'shaded_cells': shaded_cells.tolist(),
            'shading_ratio': shading_ratio,
            'affected_groups': list(affected_groups),
            'num_affected_groups': len(affected_groups),
            'severity': severity,
        }
    
    def detect_hot_spot_risk(self, irradiances: List[float], 
                            temperature: float = 298.15) -> Dict:
        """
        检测热斑风险
        
        Parameters:
        -----------
        irradiances : List[float]
            每片电池的辐照度
        temperature : float
            环境温度(K)
            
        Returns:
        --------
        Dict : 热斑风险评估
        """
        irr_array = np.array(irradiances)
        
        # 查找最弱电池
        min_idx = np.argmin(irr_array)
        min_irr = irr_array[min_idx]
        mean_irr = np.mean(irr_array)
        
        # 计算辐照度差异
        irr_diff_ratio = (mean_irr - min_irr) / mean_irr if mean_irr > 0 else 0
        
        # 估算热斑温度升高
        # 简化模型: ΔT ∝ 辐照度差异
        delta_T = irr_diff_ratio * 100  # 最大可达100°C
        
        # 风险等级
        if delta_T < 20:
            risk_level = "低风险"
            risk_score = 1
        elif delta_T < 50:
            risk_level = "中风险"
            risk_score = 2
        elif delta_T < 80:
            risk_level = "高风险"
            risk_score = 3
        else:
            risk_level = "极高风险"
            risk_score = 4
        
        # 判断旁路二极管是否会导通
        group_idx = min_idx // self.cells_per_bypass
        will_bypass = irr_diff_ratio > 0.5  # 差异>50%会导通
        
        return {
            'weakest_cell_index': int(min_idx),
            'weakest_cell_irradiance': float(min_irr),
            'irradiance_diff_ratio': irr_diff_ratio,
            'estimated_temp_rise': delta_T,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'bypass_group': int(group_idx),
            'will_bypass_activate': will_bypass,
        }
    
    def estimate_power_loss(self, irradiances: List[float]) -> Dict:
        """
        估算遮挡功率损失
        
        Parameters:
        -----------
        irradiances : List[float]
            每片电池的辐照度
            
        Returns:
        --------
        Dict : 功率损失分析
        """
        # 无遮挡基准
        self.module.set_uniform_conditions(T=298.15, G=1000.0)
        _, _, p_baseline = self.module.find_mpp()
        
        # 遮挡条件
        self.module.set_cell_irradiance(irradiances)
        _, _, p_shaded = self.module.find_mpp()
        
        # 计算损失
        power_loss = p_baseline - p_shaded
        loss_ratio = power_loss / p_baseline if p_baseline > 0 else 0
        
        # 理论最大功率(按平均辐照度)
        mean_irr = np.mean(irradiances)
        irr_ratio = mean_irr / 1000.0
        p_theoretical = p_baseline * irr_ratio
        
        # 失配损失
        mismatch_loss = p_theoretical - p_shaded
        mismatch_ratio = mismatch_loss / p_theoretical if p_theoretical > 0 else 0
        
        return {
            'baseline_power': p_baseline,
            'shaded_power': p_shaded,
            'power_loss': power_loss,
            'loss_ratio': loss_ratio,
            'loss_percentage': loss_ratio * 100,
            'theoretical_power': p_theoretical,
            'mismatch_loss': mismatch_loss,
            'mismatch_ratio': mismatch_ratio,
        }


class IVCurveDiagnostics:
    """
    I-V曲线诊断
    IV Curve Diagnostics
    
    通过I-V曲线特征识别故障
    """
    
    def __init__(self):
        """初始化诊断器"""
        pass
    
    def analyze_curve_shape(self, V: np.ndarray, I: np.ndarray) -> Dict:
        """
        分析I-V曲线形状
        
        Parameters:
        -----------
        V, I : np.ndarray
            电压和电流数组
            
        Returns:
        --------
        Dict : 曲线特征
        """
        P = V * I
        
        # 关键点
        isc = I[0]
        voc = V[np.argmin(np.abs(I))]
        
        idx_mpp = np.argmax(P)
        vmpp = V[idx_mpp]
        impp = I[idx_mpp]
        pmpp = P[idx_mpp]
        
        # 填充因子
        FF = pmpp / (voc * isc) if (voc * isc) > 0 else 0
        
        # 串联电阻影响(从MPP附近斜率估算)
        if idx_mpp < len(V) - 10:
            dV = V[idx_mpp+5] - V[idx_mpp-5]
            dI = I[idx_mpp+5] - I[idx_mpp-5]
            Rs_estimated = -dV / dI if dI != 0 else 0
        else:
            Rs_estimated = 0
        
        # 并联电阻影响(从开路附近估算)
        idx_voc = np.argmin(np.abs(V - voc))
        if idx_voc > 10:
            dV_oc = V[idx_voc] - V[idx_voc-10]
            dI_oc = I[idx_voc] - I[idx_voc-10]
            Rsh_estimated = dV_oc / dI_oc if dI_oc != 0 else np.inf
        else:
            Rsh_estimated = np.inf
        
        # 检测台阶(遮挡特征)
        dI_dV = np.diff(I) / (np.diff(V) + 1e-10)
        num_steps = np.sum(np.abs(np.diff(dI_dV)) > np.std(dI_dV) * 3)
        
        return {
            'Isc': isc,
            'Voc': voc,
            'Vmpp': vmpp,
            'Impp': impp,
            'Pmpp': pmpp,
            'FF': FF,
            'Rs_estimated': Rs_estimated,
            'Rsh_estimated': Rsh_estimated,
            'num_steps': int(num_steps),
            'has_shading': num_steps > 2,
        }
    
    def detect_faults(self, V: np.ndarray, I: np.ndarray, 
                     reference: Dict = None) -> List[str]:
        """
        故障检测
        
        Parameters:
        -----------
        V, I : np.ndarray
            测试曲线
        reference : Dict
            参考参数(正常条件)
            
        Returns:
        --------
        List[str] : 检测到的故障列表
        """
        faults = []
        
        analysis = self.analyze_curve_shape(V, I)
        
        # 检测低填充因子
        if analysis['FF'] < 0.65:
            faults.append("低填充因子 - 可能串联电阻过大")
        
        # 检测开路电压异常
        if reference and 'Voc' in reference:
            voc_ratio = analysis['Voc'] / reference['Voc']
            if voc_ratio < 0.9:
                faults.append("开路电压过低 - 可能电池损坏")
        
        # 检测短路电流异常
        if reference and 'Isc' in reference:
            isc_ratio = analysis['Isc'] / reference['Isc']
            if isc_ratio < 0.9:
                faults.append("短路电流过低 - 可能遮挡或污染")
        
        # 检测遮挡
        if analysis['has_shading']:
            faults.append(f"检测到遮挡特征 - {analysis['num_steps']}个台阶")
        
        # 检测开路
        if analysis['Isc'] < 0.1:
            faults.append("开路故障 - 电流过低")
        
        # 检测短路
        if analysis['Voc'] < 0.1:
            faults.append("短路故障 - 电压过低")
        
        return faults if faults else ["无明显故障"]


class PerformanceEvaluator:
    """
    性能评估器
    Performance Evaluator
    
    评估光伏系统性能指标
    """
    
    def __init__(self):
        """初始化评估器"""
        pass
    
    def calculate_performance_ratio(self, 
                                    actual_energy: float,
                                    expected_energy: float) -> float:
        """
        计算性能比(PR)
        
        PR = 实际发电量 / 理论发电量
        
        Parameters:
        -----------
        actual_energy : float
            实际发电量(kWh)
        expected_energy : float
            理论发电量(kWh)
            
        Returns:
        --------
        float : 性能比
        """
        return actual_energy / expected_energy if expected_energy > 0 else 0
    
    def evaluate_system_health(self, 
                               current_power: float,
                               rated_power: float,
                               irradiance: float = 1000.0,
                               temperature: float = 25.0) -> Dict:
        """
        评估系统健康状况
        
        Parameters:
        -----------
        current_power : float
            当前功率(W)
        rated_power : float
            额定功率(W, STC条件)
        irradiance : float
            当前辐照度(W/m²)
        temperature : float
            当前温度(°C)
            
        Returns:
        --------
        Dict : 健康评估结果
        """
        # 温度修正系数(简化)
        temp_coef = -0.004  # -0.4%/°C
        temp_factor = 1 + temp_coef * (temperature - 25)
        
        # 辐照度修正
        irr_factor = irradiance / 1000.0
        
        # 期望功率
        expected_power = rated_power * irr_factor * temp_factor
        
        # 性能比
        pr = current_power / expected_power if expected_power > 0 else 0
        
        # 健康评级
        if pr > 0.90:
            health_grade = "优秀"
            health_score = 5
        elif pr > 0.85:
            health_grade = "良好"
            health_score = 4
        elif pr > 0.75:
            health_grade = "一般"
            health_score = 3
        elif pr > 0.60:
            health_grade = "较差"
            health_score = 2
        else:
            health_grade = "差"
            health_score = 1
        
        return {
            'current_power': current_power,
            'expected_power': expected_power,
            'performance_ratio': pr,
            'pr_percentage': pr * 100,
            'health_grade': health_grade,
            'health_score': health_score,
            'temp_factor': temp_factor,
            'irr_factor': irr_factor,
        }
