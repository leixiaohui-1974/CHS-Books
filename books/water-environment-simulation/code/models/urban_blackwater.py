"""
城市黑臭水体治理模型（简化版）
Simplified Urban Blackwater Treatment Model
"""

import numpy as np


class UrbanBlackwaterModel:
    """城市黑臭水体综合治理模型"""
    
    def __init__(self, river_length, width, depth):
        """
        参数：
        - river_length: 河道长度 (m)
        - width: 河宽 (m)
        - depth: 水深 (m)
        """
        self.river_length = river_length
        self.width = width
        self.depth = depth
        self.volume = river_length * width * depth
        
        print(f"黑臭水体治理模型初始化:")
        print(f"  河道: {river_length}m × {width}m × {depth}m")
        print(f"  水体积: {self.volume:.0f} m³")
    
    def assess_current_status(self, DO, NH3_N, transparency):
        """评估当前黑臭程度"""
        # 黑臭判定标准
        is_black = (DO < 2 and NH3_N > 8 and transparency < 0.25)
        
        score = 0
        if DO < 2: score += 3
        elif DO < 4: score += 1
        if NH3_N > 8: score += 3
        elif NH3_N > 2: score += 1
        if transparency < 0.25: score += 2
        
        status = "重度黑臭" if score >= 6 else ("轻度黑臭" if score >= 3 else "无黑臭")
        
        print(f"\n现状评估:")
        print(f"  DO: {DO} mg/L")
        print(f"  NH3-N: {NH3_N} mg/L")
        print(f"  透明度: {transparency} m")
        print(f"  黑臭程度: {status} (评分: {score})")
        
        return status, score
    
    def simulate_treatment_effects(self, measures):
        """
        模拟治理效果
        
        参数：
        - measures: 治理措施字典
        """
        DO_improvement = 0
        NH3_reduction = 0
        
        if measures.get('source_control', False):
            NH3_reduction += 5
        if measures.get('dredging', False):
            NH3_reduction += 2
            DO_improvement += 1
        if measures.get('aeration', False):
            DO_improvement += 3
        if measures.get('ecological_restoration', False):
            DO_improvement += 2
            NH3_reduction += 1
        
        print(f"\n治理措施效果:")
        print(f"  DO提升: +{DO_improvement} mg/L")
        print(f"  NH3-N削减: -{NH3_reduction} mg/L")
        
        return DO_improvement, NH3_reduction


def optimize_treatment_plan(budget, target_quality):
    """优化治理方案（简化）"""
    # 简化的成本-效益分析
    recommended_measures = {
        'source_control': True,  # 必选
        'dredging': budget > 500,
        'aeration': budget > 300,
        'ecological_restoration': budget > 400
    }
    
    print(f"\n方案优化:")
    print(f"  预算: {budget} 万元")
    print(f"  推荐措施: {[k for k, v in recommended_measures.items() if v]}")
    
    return recommended_measures
