"""
自净能力评估模型
Self-Purification Capacity Assessment

包括：
1. 环境容量计算（Environmental Capacity）
2. 水质综合评价（Water Quality Index）
3. 自净系数计算
4. 河流功能区划分
"""

import numpy as np


class SelfPurificationCapacity:
    """
    河流自净能力评估
    
    自净能力是指水体通过物理、化学和生物作用，
    降解和转化污染物，恢复到原有水质状态的能力。
    
    主要指标：
    1. ka/kd比值（复氧/耗氧比）
    2. 水力条件（流速、水深、紊流）
    3. 生物活性（微生物、水生植物）
    4. 环境因素（温度、DO、pH）
    
    参数：
        Q: 流量 (m³/s)
        u: 流速 (m/s)
        A: 断面面积 (m²)
        P: 湿周 (m)
        ka: 复氧系数 (day⁻¹)
        kd: BOD降解系数 (day⁻¹)
    """
    
    def __init__(self, Q, u, A, P, ka, kd):
        """初始化自净能力评估模型"""
        self.Q = Q      # 流量
        self.u = u      # 流速
        self.A = A      # 断面面积
        self.P = P      # 湿周
        self.ka = ka    # 复氧系数
        self.kd = kd    # BOD降解系数
        
        # 计算水力半径
        self.R = A / P  # 水力半径 (m)
        
        # 自净系数
        self.f = ka / kd  # ka/kd比值
    
    def calculate_self_purification_coefficient(self):
        """
        计算自净系数
        
        自净系数 f = ka / kd
        
        分级：
        - f < 1: 自净能力弱（污染加重）
        - 1 ≤ f < 2: 自净能力一般
        - 2 ≤ f < 5: 自净能力较强
        - f ≥ 5: 自净能力强
        
        返回：
            f: 自净系数
            grade: 自净能力等级
        """
        f = self.f
        
        if f < 1:
            grade = "弱（污染加重）"
            color = "red"
        elif f < 2:
            grade = "一般"
            color = "orange"
        elif f < 5:
            grade = "较强"
            color = "yellow"
        else:
            grade = "强"
            color = "green"
        
        print(f"自净系数 f = ka/kd = {self.ka}/{self.kd} = {f:.2f}")
        print(f"自净能力等级: {grade}")
        
        return f, grade, color
    
    def calculate_dilution_capacity(self, C_river, C_standard):
        """
        计算稀释容量
        
        稀释容量是指在保证水质达标的前提下，
        水体能够容纳的污染物最大量。
        
        W = Q * (C_standard - C_river)
        
        参数：
            C_river: 河流本底浓度 (mg/L)
            C_standard: 水质标准 (mg/L)
            
        返回：
            W: 稀释容量 (kg/day)
        """
        if C_standard <= C_river:
            print(f"⚠️  河流本底浓度 ({C_river} mg/L) 已超过标准 ({C_standard} mg/L)")
            return 0
        
        # 稀释容量 (kg/day)
        W = self.Q * (C_standard - C_river) * 86.4  # 转换为kg/day
        
        print(f"稀释容量计算:")
        print(f"  河流流量 Q = {self.Q} m³/s")
        print(f"  本底浓度 C_river = {C_river} mg/L")
        print(f"  水质标准 C_standard = {C_standard} mg/L")
        print(f"  → 稀释容量 W = {W:.2f} kg/day")
        
        return W
    
    def calculate_environmental_capacity(self, C0, C_standard, L, decay=True):
        """
        计算环境容量（降解容量）
        
        考虑污染物的降解作用，水体能够容纳的最大污染物量。
        
        对于BOD等可降解污染物：
        W = Q * (C_standard - C0) + Q * kd * L * (C_standard) / u
        
        参数：
            C0: 上游本底浓度 (mg/L)
            C_standard: 水质标准 (mg/L)
            L: 河段长度 (km)
            decay: 是否考虑降解作用
            
        返回：
            W: 环境容量 (kg/day)
        """
        # 稀释容量
        W_dilution = self.Q * (C_standard - C0) * 86.4
        
        if decay and self.kd > 0:
            # 降解容量（转换单位）
            travel_time = L * 1000 / (self.u * 86400)  # 转换为天
            W_decay = self.Q * self.kd * C_standard * travel_time * 86.4
            W_total = W_dilution + W_decay
            
            print(f"环境容量计算（考虑降解）:")
            print(f"  河段长度 L = {L} km")
            print(f"  行程时间 t = {travel_time:.2f} 天")
            print(f"  稀释容量 = {W_dilution:.2f} kg/day")
            print(f"  降解容量 = {W_decay:.2f} kg/day")
            print(f"  → 总环境容量 W = {W_total:.2f} kg/day")
        else:
            W_total = W_dilution
            print(f"环境容量（仅稀释）= {W_total:.2f} kg/day")
        
        return W_total
    
    def calculate_mixing_length(self, B, Q_waste, Q_river):
        """
        计算完全混合长度
        
        污染物从排放口到完全混合的距离。
        
        L_mix = 0.4 * B * u / (g * R * S)^0.5
        简化公式：L_mix ≈ 0.13 * B * u (经验公式)
        
        参数：
            B: 河宽 (m)
            Q_waste: 废水流量 (m³/s)
            Q_river: 河流流量 (m³/s)
            
        返回：
            L_mix: 混合长度 (m)
        """
        # 简化经验公式
        L_mix = 0.13 * B * self.u
        
        # 混合时间
        t_mix = L_mix / self.u
        
        print(f"完全混合长度:")
        print(f"  河宽 B = {B} m")
        print(f"  流速 u = {self.u} m/s")
        print(f"  → 混合长度 L_mix = {L_mix:.1f} m")
        print(f"  → 混合时间 t_mix = {t_mix:.1f} s")
        
        return L_mix


class WaterQualityIndex:
    """
    水质综合评价指数
    
    常用的水质评价方法：
    1. 单因子指数法
    2. 综合污染指数法
    3. 水质标识指数法
    """
    
    @staticmethod
    def single_factor_index(C_measured, C_standard):
        """
        单因子指数法
        
        P_i = C_i / S_i
        
        其中：
        - C_i: 实测浓度
        - S_i: 标准浓度
        - P_i < 1: 达标
        - P_i ≥ 1: 超标
        
        参数：
            C_measured: 实测浓度 (mg/L)
            C_standard: 标准浓度 (mg/L)
            
        返回：
            P: 单因子指数
        """
        P = C_measured / C_standard
        return P
    
    @staticmethod
    def comprehensive_pollution_index(C_measured_list, C_standard_list, weights=None):
        """
        综合污染指数法（加权平均）
        
        P = Σ(w_i * P_i) / Σw_i
        
        参数：
            C_measured_list: 实测浓度列表
            C_standard_list: 标准浓度列表
            weights: 权重列表（可选）
            
        返回：
            P: 综合污染指数
        """
        if weights is None:
            weights = [1.0] * len(C_measured_list)
        
        P_list = [c / s for c, s in zip(C_measured_list, C_standard_list)]
        P_weighted = sum(w * p for w, p in zip(weights, P_list))
        P = P_weighted / sum(weights)
        
        return P
    
    @staticmethod
    def water_quality_identification_index(C_measured_list, parameter_names, 
                                          standards_dict):
        """
        水质标识指数法（中国标准）
        
        WQII = X1.X2X3
        
        其中：
        - X1: 功能类别（1-5）
        - X2X3: 污染分指数（01-99）
        
        参数：
            C_measured_list: 实测浓度列表
            parameter_names: 参数名称列表
            standards_dict: 标准字典 {类别: {参数: 标准值}}
            
        返回：
            WQII: 水质标识指数
            category: 水质类别
        """
        # 确定水质类别（最差的单因子）
        worst_category = 1
        worst_parameter = None
        
        for param, C_measured in zip(parameter_names, C_measured_list):
            for category in range(1, 6):
                if category in standards_dict and param in standards_dict[category]:
                    C_standard = standards_dict[category][param]
                    if C_measured > C_standard:
                        if category > worst_category:
                            worst_category = category
                            worst_parameter = param
        
        X1 = worst_category
        
        # 计算污染分指数（简化）
        if worst_parameter:
            C_measured_worst = C_measured_list[parameter_names.index(worst_parameter)]
            C_standard_worst = standards_dict[X1][worst_parameter]
            P = C_measured_worst / C_standard_worst
            X2X3 = min(int((P - 1) * 10), 99)
        else:
            X2X3 = 0
        
        WQII = X1 + X2X3 / 100
        
        return WQII, X1, X2X3


def calculate_assimilative_capacity(Q, ka, kd, DOs, DO_standard, L0_bg):
    """
    计算同化容量（基于S-P模型）
    
    在保证DO达标的前提下，水体能够接纳的最大BOD量。
    
    参数：
        Q: 流量 (m³/s)
        ka: 复氧系数 (day⁻¹)
        kd: BOD降解系数 (day⁻¹)
        DOs: 饱和DO (mg/L)
        DO_standard: DO标准 (mg/L)
        L0_bg: 上游本底BOD (mg/L)
        
    返回：
        L0_max: 最大允许BOD (mg/L)
        W: 同化容量 (kg/day)
    """
    # 简化计算：假设初始DO=DOs
    D0 = 0
    D_standard = DOs - DO_standard
    
    # 临界点条件：Dc = D_standard
    # 反推L0_max（简化公式）
    if ka > kd:
        L0_max = D_standard * ka / kd
    else:
        # ka <= kd时，自净能力弱，限制严格
        L0_max = D_standard * 0.5
    
    # 考虑本底BOD
    L0_max = max(L0_max - L0_bg, 0)
    
    # 同化容量
    W = Q * L0_max * 86.4  # kg/day
    
    print(f"同化容量计算（基于DO标准）:")
    print(f"  DO标准 = {DO_standard} mg/L")
    print(f"  最大允许DO亏损 = {D_standard:.2f} mg/L")
    print(f"  → 最大允许BOD = {L0_max:.2f} mg/L")
    print(f"  → 同化容量 W = {W:.2f} kg/day")
    
    return L0_max, W


def functional_zone_classification(parameters_dict, use='drinking'):
    """
    河流功能区划分
    
    根据GB 3838-2002地表水环境质量标准
    
    功能类别：
    - I类: 源头水、国家自然保护区
    - II类: 集中式生活饮用水水源地一级保护区
    - III类: 集中式生活饮用水水源地二级保护区、一般鱼类保护区
    - IV类: 一般工业用水区、非直接接触娱乐用水区
    - V类: 农业用水区、一般景观要求水域
    
    参数：
        parameters_dict: 水质参数字典 {参数名: 浓度}
        use: 水体功能用途
        
    返回：
        category: 推荐功能类别
        suitable_uses: 适用用途列表
    """
    # 标准限值（简化版）
    standards = {
        1: {'DO': 7.5, 'COD': 15, 'BOD5': 3, 'NH3-N': 0.15, 'TP': 0.02},
        2: {'DO': 6, 'COD': 15, 'BOD5': 3, 'NH3-N': 0.5, 'TP': 0.1},
        3: {'DO': 5, 'COD': 20, 'BOD5': 4, 'NH3-N': 1.0, 'TP': 0.2},
        4: {'DO': 3, 'COD': 30, 'BOD5': 6, 'NH3-N': 1.5, 'TP': 0.3},
        5: {'DO': 2, 'COD': 40, 'BOD5': 10, 'NH3-N': 2.0, 'TP': 0.4},
    }
    
    # 用途对应
    use_requirements = {
        'drinking': [1, 2],
        'fishery': [2, 3],
        'swimming': [2, 3],
        'industrial': [3, 4],
        'agricultural': [4, 5],
        'landscape': [4, 5],
    }
    
    # 判断最差类别
    worst_category = 1
    for param, value in parameters_dict.items():
        if param in ['DO']:
            # DO越高越好
            for cat in range(1, 6):
                if value < standards[cat][param]:
                    worst_category = max(worst_category, cat)
        else:
            # 其他参数越低越好
            for cat in range(1, 6):
                if param in standards[cat] and value > standards[cat][param]:
                    worst_category = max(worst_category, cat)
    
    # 推荐类别
    recommended = worst_category
    
    # 适用用途
    suitable_uses = []
    for use_name, required_cats in use_requirements.items():
        if recommended in required_cats or recommended < min(required_cats):
            suitable_uses.append(use_name)
    
    print(f"功能区划分结果:")
    print(f"  实际水质类别: {recommended}类")
    print(f"  适用用途: {', '.join(suitable_uses)}")
    
    return recommended, suitable_uses
