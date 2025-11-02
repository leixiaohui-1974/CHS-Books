"""
营养盐循环模型
Nutrient Cycling Model

包括：
1. 氮循环（Nitrogen Cycle）
   - 氨氮（NH4-N）→ 硝态氮（NO3-N）（硝化）
   - 硝态氮 → 氮气（反硝化）
   - 有机氮 → 氨氮（氨化）
2. 磷循环（Phosphorus Cycle）
   - 有机磷 → 正磷酸盐
   - 吸附/解吸
3. 富营养化评估
   - 综合营养状态指数（TSI）
   - 限制性营养元素判断
"""

import numpy as np
from scipy.integrate import odeint


class NitrogenCycle:
    """
    氮循环模型
    
    描述水体中氮的形态转化：
    - NH4-N（氨氮）
    - NO2-N（亚硝态氮，可忽略）
    - NO3-N（硝态氮）
    - Org-N（有机氮）
    
    主要过程：
    1. 硝化作用（Nitrification）: NH4+ → NO3-
    2. 反硝化作用（Denitrification）: NO3- → N2
    3. 氨化作用（Ammonification）: Org-N → NH4+
    4. 植物吸收
    5. 沉降
    
    参数：
        NH4_0: 初始氨氮浓度 (mg/L)
        NO3_0: 初始硝态氮浓度 (mg/L)
        OrgN_0: 初始有机氮浓度 (mg/L)
        k_n: 硝化速率常数 (day^-1)
        k_dn: 反硝化速率常数 (day^-1)
        k_am: 氨化速率常数 (day^-1)
        T: 模拟时间 (day)
        nt: 时间步数
    """
    
    def __init__(self, NH4_0, NO3_0, OrgN_0, k_n, k_dn, k_am, T=30.0, nt=1000):
        """初始化氮循环模型"""
        self.NH4_0 = NH4_0
        self.NO3_0 = NO3_0
        self.OrgN_0 = OrgN_0
        self.k_n = k_n      # 硝化速率
        self.k_dn = k_dn    # 反硝化速率
        self.k_am = k_am    # 氨化速率
        self.T = T
        self.nt = nt
        
        # 时间数组
        self.t = np.linspace(0, T, nt)
        self.dt = T / (nt - 1)
        
        # 结果数组
        self.NH4 = np.zeros(nt)   # 氨氮
        self.NO3 = np.zeros(nt)   # 硝态氮
        self.OrgN = np.zeros(nt)  # 有机氮
        self.TN = np.zeros(nt)    # 总氮
        
        # DO浓度（影响硝化和反硝化）
        self.DO = 5.0  # 默认5 mg/L
    
    def set_do(self, DO):
        """设置溶解氧浓度"""
        self.DO = DO
    
    def _derivatives(self, y, t):
        """
        计算导数（用于ODE求解）
        
        y = [NH4, NO3, OrgN]
        
        dy/dt:
        dNH4/dt = k_am * OrgN - k_n * NH4
        dNO3/dt = k_n * NH4 - k_dn * NO3
        dOrgN/dt = -k_am * OrgN
        """
        NH4, NO3, OrgN = y
        
        # DO影响因子（简化）
        f_DO_n = self.DO / (self.DO + 0.5)   # 硝化需要DO
        f_DO_dn = 0.5 / (self.DO + 0.5)      # 反硝化需要低DO
        
        # 氨化
        ammonification = self.k_am * OrgN
        
        # 硝化（需要氧气）
        nitrification = self.k_n * NH4 * f_DO_n
        
        # 反硝化（厌氧条件）
        denitrification = self.k_dn * NO3 * f_DO_dn
        
        dNH4_dt = ammonification - nitrification
        dNO3_dt = nitrification - denitrification
        dOrgN_dt = -ammonification
        
        return [dNH4_dt, dNO3_dt, dOrgN_dt]
    
    def solve(self):
        """
        求解氮循环方程
        
        返回：
            NH4, NO3, OrgN, TN: 各形态氮浓度数组
        """
        # 初始条件
        y0 = [self.NH4_0, self.NO3_0, self.OrgN_0]
        
        # 求解ODE
        solution = odeint(self._derivatives, y0, self.t)
        
        self.NH4 = solution[:, 0]
        self.NO3 = solution[:, 1]
        self.OrgN = solution[:, 2]
        self.TN = self.NH4 + self.NO3 + self.OrgN  # 总氮
        
        return self.NH4, self.NO3, self.OrgN, self.TN
    
    def temperature_correction(self, k_20, T, process='nitrification'):
        """
        温度校正
        
        参数：
            k_20: 20°C时的速率常数
            T: 水温 (°C)
            process: 过程类型
                - 'nitrification': 硝化 (θ=1.08)
                - 'denitrification': 反硝化 (θ=1.045)
                - 'ammonification': 氨化 (θ=1.08)
        
        返回：
            k_T: 温度T时的速率常数
        """
        theta_dict = {
            'nitrification': 1.08,
            'denitrification': 1.045,
            'ammonification': 1.08
        }
        
        theta = theta_dict.get(process, 1.047)
        k_T = k_20 * theta**(T - 20)
        
        print(f"温度校正 ({process}, T={T}°C):")
        print(f"  k({T}°C) = {k_T:.4f} day⁻¹ (θ={theta})")
        
        return k_T


class PhosphorusCycle:
    """
    磷循环模型
    
    描述水体中磷的形态转化：
    - PO4-P（正磷酸盐，溶解态）
    - Org-P（有机磷，颗粒态）
    
    主要过程：
    1. 矿化作用: Org-P → PO4-P
    2. 沉降
    3. 吸附/解吸
    
    参数：
        PO4_0: 初始正磷酸盐浓度 (mg/L)
        OrgP_0: 初始有机磷浓度 (mg/L)
        k_mp: 矿化速率常数 (day^-1)
        k_s: 沉降速率常数 (day^-1)
        T: 模拟时间 (day)
        nt: 时间步数
    """
    
    def __init__(self, PO4_0, OrgP_0, k_mp, k_s, T=30.0, nt=1000):
        """初始化磷循环模型"""
        self.PO4_0 = PO4_0
        self.OrgP_0 = OrgP_0
        self.k_mp = k_mp   # 矿化速率
        self.k_s = k_s     # 沉降速率
        self.T = T
        self.nt = nt
        
        # 时间数组
        self.t = np.linspace(0, T, nt)
        self.dt = T / (nt - 1)
        
        # 结果数组
        self.PO4 = np.zeros(nt)   # 正磷酸盐
        self.OrgP = np.zeros(nt)  # 有机磷
        self.TP = np.zeros(nt)    # 总磷
    
    def _derivatives(self, y, t):
        """
        计算导数
        
        y = [PO4, OrgP]
        
        dy/dt:
        dPO4/dt = k_mp * OrgP
        dOrgP/dt = -k_mp * OrgP - k_s * OrgP
        """
        PO4, OrgP = y
        
        # 矿化
        mineralization = self.k_mp * OrgP
        
        # 沉降
        settling = self.k_s * OrgP
        
        dPO4_dt = mineralization
        dOrgP_dt = -mineralization - settling
        
        return [dPO4_dt, dOrgP_dt]
    
    def solve(self):
        """
        求解磷循环方程
        
        返回：
            PO4, OrgP, TP: 各形态磷浓度数组
        """
        # 初始条件
        y0 = [self.PO4_0, self.OrgP_0]
        
        # 求解ODE
        solution = odeint(self._derivatives, y0, self.t)
        
        self.PO4 = solution[:, 0]
        self.OrgP = solution[:, 1]
        self.TP = self.PO4 + self.OrgP  # 总磷
        
        return self.PO4, self.OrgP, self.TP


class EutrophicationIndex:
    """
    富营养化评估
    
    计算综合营养状态指数（Trophic State Index, TSI）
    
    方法：
    1. Carlson TSI（基于叶绿素a、总磷、透明度）
    2. 综合营养状态指数（中国标准）
    
    分级：
    - 贫营养（Oligotrophic）: TSI < 30
    - 中营养（Mesotrophic）: 30 ≤ TSI < 50
    - 富营养（Eutrophic）: 50 ≤ TSI < 70
    - 超富营养（Hypereutrophic）: TSI ≥ 70
    """
    
    @staticmethod
    def carlson_tsi_chl(Chl):
        """
        基于叶绿素a的TSI
        
        参数：
            Chl: 叶绿素a浓度 (μg/L)
            
        返回：
            TSI(Chl)
        """
        if Chl <= 0:
            return 0
        return 9.81 * np.log(Chl) + 30.6
    
    @staticmethod
    def carlson_tsi_tp(TP):
        """
        基于总磷的TSI
        
        参数：
            TP: 总磷浓度 (μg/L)
            
        返回：
            TSI(TP)
        """
        if TP <= 0:
            return 0
        return 14.42 * np.log(TP) + 4.15
    
    @staticmethod
    def carlson_tsi_sd(SD):
        """
        基于透明度的TSI
        
        参数：
            SD: 透明度 (m)
            
        返回：
            TSI(SD)
        """
        if SD <= 0:
            return 100
        return 60 - 14.41 * np.log(SD)
    
    @staticmethod
    def carlson_tsi_综合(Chl, TP, SD):
        """
        Carlson综合TSI
        
        TSI = [TSI(Chl) + TSI(TP) + TSI(SD)] / 3
        
        参数：
            Chl: 叶绿素a (μg/L)
            TP: 总磷 (μg/L)
            SD: 透明度 (m)
            
        返回：
            TSI: 综合营养状态指数
            status: 营养状态描述
        """
        tsi_chl = EutrophicationIndex.carlson_tsi_chl(Chl)
        tsi_tp = EutrophicationIndex.carlson_tsi_tp(TP)
        tsi_sd = EutrophicationIndex.carlson_tsi_sd(SD)
        
        TSI = (tsi_chl + tsi_tp + tsi_sd) / 3
        
        # 判断营养状态
        if TSI < 30:
            status = "贫营养（Oligotrophic）"
        elif TSI < 50:
            status = "中营养（Mesotrophic）"
        elif TSI < 70:
            status = "富营养（Eutrophic）"
        else:
            status = "超富营养（Hypereutrophic）"
        
        return TSI, status
    
    @staticmethod
    def china_tli(Chl, TP, TN, SD, CODMn):
        """
        中国湖泊综合营养状态指数（TLI）
        
        TLI(Σ) = Σ Wj · TLI(j)
        
        参数：
            Chl: 叶绿素a (mg/m³ = μg/L)
            TP: 总磷 (mg/L)
            TN: 总氮 (mg/L)
            SD: 透明度 (m)
            CODMn: 高锰酸盐指数 (mg/L)
            
        返回：
            TLI: 综合营养状态指数
            status: 营养状态
        """
        # 各指标权重（叶绿素a为基准）
        W_chl = 1.0
        
        # 计算各指标的TLI
        TLI_chl = 10 * (2.5 + 1.086 * np.log(Chl)) if Chl > 0 else 0
        TLI_tp = 10 * (9.436 + 1.624 * np.log(TP * 1000)) if TP > 0 else 0  # 转换为μg/L
        TLI_tn = 10 * (5.453 + 1.694 * np.log(TN)) if TN > 0 else 0
        TLI_sd = 10 * (5.118 - 1.94 * np.log(SD)) if SD > 0 else 100
        TLI_cod = 10 * (0.109 + 2.661 * np.log(CODMn)) if CODMn > 0 else 0
        
        # 计算权重
        r_chl_tp = 0.84  # 经验相关系数
        W_tp = r_chl_tp**2
        W_tn = r_chl_tp**2 * 0.9
        W_sd = r_chl_tp**2 * 0.95
        W_cod = r_chl_tp**2 * 0.85
        
        # 归一化权重
        W_sum = W_chl + W_tp + W_tn + W_sd + W_cod
        W_chl /= W_sum
        W_tp /= W_sum
        W_tn /= W_sum
        W_sd /= W_sum
        W_cod /= W_sum
        
        # 综合TLI
        TLI = W_chl * TLI_chl + W_tp * TLI_tp + W_tn * TLI_tn + \
              W_sd * TLI_sd + W_cod * TLI_cod
        
        # 判断营养状态
        if TLI < 30:
            status = "贫营养"
        elif TLI < 50:
            status = "中营养"
        elif TLI < 60:
            status = "轻度富营养"
        elif TLI < 70:
            status = "中度富营养"
        else:
            status = "重度富营养"
        
        return TLI, status
    
    @staticmethod
    def limiting_nutrient(TN, TP, N_P_ratio=16):
        """
        判断限制性营养元素
        
        Redfield比值: N:P = 16:1 (原子比)
        质量比: N:P ≈ 7.2:1
        
        参数：
            TN: 总氮浓度 (mg/L)
            TP: 总磷浓度 (mg/L)
            N_P_ratio: N/P阈值（质量比）
            
        返回：
            limiting: 限制元素（'N', 'P', 或 'Co-limitation'）
        """
        if TP <= 0:
            return 'P'
        
        ratio = TN / TP
        
        if ratio < N_P_ratio * 0.8:  # N/P < 5.76
            limiting = 'N'
            desc = "氮限制（控制氮可有效防止富营养化）"
        elif ratio > N_P_ratio * 1.2:  # N/P > 8.64
            limiting = 'P'
            desc = "磷限制（控制磷可有效防止富营养化）"
        else:
            limiting = 'Co-limitation'
            desc = "氮磷共同限制（需同时控制氮和磷）"
        
        print(f"N/P比值 = {ratio:.2f}")
        print(f"限制性营养元素: {limiting}")
        print(f"  → {desc}")
        
        return limiting


def calculate_oxygen_consumption(NH4, k_n):
    """
    计算硝化耗氧量
    
    硝化反应：
    NH4+ + 2O2 → NO3- + 2H+ + H2O
    
    理论耗氧量：1 mg NH4-N 需要 4.57 mg O2
    
    参数：
        NH4: 氨氮浓度 (mg/L)
        k_n: 硝化速率 (day^-1)
        
    返回：
        O2_consumption: 耗氧速率 (mg O2/L/day)
    """
    O2_consumption = 4.57 * k_n * NH4
    return O2_consumption
