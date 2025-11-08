# -*- coding: utf-8 -*-
"""
第15章 考前冲刺与模拟题 - 模拟试卷1：基础巩固型

试卷结构：
    总分：150分
    时间：3小时（180分钟）
    难度：⭐⭐⭐
    目标：120分
    
题型分布：
    一、选择题（30分，10×3分）
    二、填空题（20分，10×2分）
    三、简答题（30分，3×10分）
    四、计算题（50分，5×10分）
    五、设计题（20分，1×20分）

考察重点：
    - 基础概念（40%）
    - 公式应用（30%）
    - 计算能力（20%）
    - 分析能力（10%）

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from datetime import datetime

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FoundationExam:
    """基础巩固型模拟试卷"""
    
    def __init__(self):
        self.exam_name = "模拟试卷1：基础巩固型"
        self.total_score = 150
        self.time_limit = 180  # 分钟
        self.target_score = 120
        
        # 题型分数
        self.scores = {
            'choice': 30,
            'fill': 20,
            'short': 30,
            'calculation': 50,
            'design': 20
        }
        
    def choice_questions(self) -> Dict:
        """选择题（30分）"""
        questions = [
            {
                'id': 1,
                'question': '静水压强随深度增加的规律是',
                'options': ['A.线性增加', 'B.指数增加', 'C.对数增加', 'D.二次方增加'],
                'answer': 'A',
                'points': 3,
                'explanation': 'p = p0 + γh，线性关系'
            },
            {
                'id': 2,
                'question': '伯努利方程适用条件不包括',
                'options': ['A.理想流体', 'B.恒定流', 'C.沿流线', 'D.可压缩流体'],
                'answer': 'D',
                'points': 3,
                'explanation': '伯努利方程适用于不可压缩流体'
            },
            {
                'id': 3,
                'question': '圆管层流的临界雷诺数约为',
                'options': ['A.500', 'B.2320', 'C.4000', 'D.10000'],
                'answer': 'B',
                'points': 3,
                'explanation': 'Re_c = 2320（层流→紊流）'
            },
            {
                'id': 4,
                'question': '明渠均匀流的判别条件是',
                'options': ['A.i=J', 'B.i>J', 'C.i<J', 'D.i=0'],
                'answer': 'A',
                'points': 3,
                'explanation': '底坡i等于水力坡度J'
            },
            {
                'id': 5,
                'question': '达西定律适用于',
                'options': ['A.层流', 'B.紊流', 'C.过渡流', 'D.任意流态'],
                'answer': 'A',
                'points': 3,
                'explanation': '达西定律仅适用于层流渗流'
            },
            {
                'id': 6,
                'question': '水跃发生在',
                'options': ['A.缓流→急流', 'B.急流→缓流', 'C.临界流', 'D.均匀流'],
                'answer': 'B',
                'points': 3,
                'explanation': '水跃：急流过渡到缓流'
            },
            {
                'id': 7,
                'question': '重力坝抗滑稳定安全系数一般不小于',
                'options': ['A.1.0', 'B.1.5', 'C.3.0', 'D.5.0'],
                'answer': 'C',
                'points': 3,
                'explanation': 'Kc ≥ 3.0（规范要求）'
            },
            {
                'id': 8,
                'question': '泵的相似工况点是指',
                'options': ['A.流量相同', 'B.扬程相同', 'C.效率相同', 'D.工况参数相似'],
                'answer': 'D',
                'points': 3,
                'explanation': '满足相似定律的对应工况点'
            },
            {
                'id': 9,
                'question': '水库年调节的调节系数β范围是',
                'options': ['A.β<0.2', 'B.0.2≤β<0.5', 'C.0.5≤β<1.0', 'D.β≥1.0'],
                'answer': 'C',
                'points': 3,
                'explanation': '年调节：0.5 ≤ β < 1.0'
            },
            {
                'id': 10,
                'question': '弗劳德数Fr表示',
                'options': ['A.粘滞力/惯性力', 'B.惯性力/重力', 'C.惯性力/弹性力', 'D.重力/粘滞力'],
                'answer': 'B',
                'points': 3,
                'explanation': 'Fr = v/√(gh)，惯性力与重力之比'
            }
        ]
        
        return {
            'questions': questions,
            'total_points': sum([q['points'] for q in questions])
        }
    
    def fill_questions(self) -> Dict:
        """填空题（20分）"""
        questions = [
            {
                'id': 1,
                'question': '连续性方程的物理意义是______',
                'answer': '质量守恒',
                'points': 2
            },
            {
                'id': 2,
                'question': '圆管层流的沿程损失系数λ = ______',
                'answer': '64/Re',
                'points': 2
            },
            {
                'id': 3,
                'question': '明渠临界水深hc = ______（q为单宽流量）',
                'answer': '(q²/g)^(1/3)',
                'points': 2
            },
            {
                'id': 4,
                'question': '水力最优断面是指______最小的断面',
                'answer': '湿周（或过水断面最大）',
                'points': 2
            },
            {
                'id': 5,
                'question': '水跃共轭水深关系式：h2/h1 = ______',
                'answer': '(√(1+8Fr1²)-1)/2',
                'points': 2
            },
            {
                'id': 6,
                'question': '重力坝坝基应力公式：σ = ______',
                'answer': 'ΣV/B ± 6ΣM/B²',
                'points': 2
            },
            {
                'id': 7,
                'question': '泵的相似定律：Q1/Q2 = ______',
                'answer': '(n1/n2)(D1/D2)³',
                'points': 2
            },
            {
                'id': 8,
                'question': '水电站出力公式：N = ______',
                'answer': '9.81ηQH/1000 (MW)',
                'points': 2
            },
            {
                'id': 9,
                'question': '曼宁公式中糙率n的量纲是______',
                'answer': 's/m^(1/3) 或 T/L^(1/3)',
                'points': 2
            },
            {
                'id': 10,
                'question': '泥沙沉速公式（Stokes）：ω = ______',
                'answer': '(γs-γ)d²/(18μ)',
                'points': 2
            }
        ]
        
        return {
            'questions': questions,
            'total_points': sum([q['points'] for q in questions])
        }
    
    def short_questions(self) -> Dict:
        """简答题（30分）"""
        questions = [
            {
                'id': 1,
                'question': '简述能量方程（伯努利方程）的物理意义和适用条件。（10分）',
                'answer_points': [
                    '物理意义（5分）：',
                    '- 单位重量流体具有的总机械能守恒',
                    '- z：位置水头（位能）',
                    '- p/γ：压强水头（压能）',
                    '- v²/(2g)：流速水头（动能）',
                    '适用条件（5分）：',
                    '- 不可压缩流体',
                    '- 理想流体（或实际流体考虑损失）',
                    '- 恒定流',
                    '- 沿同一流线'
                ],
                'points': 10
            },
            {
                'id': 2,
                'question': '什么是明渠非均匀流？分析缓坡上的水面线类型。（10分）',
                'answer_points': [
                    '定义（3分）：',
                    '- 流速、水深沿程变化',
                    '- 水面线不平行于渠底',
                    '缓坡水面线（7分）：',
                    '- M1型：h>h0>hc，壅水曲线',
                    '- M2型：h0>h>hc，降水曲线',
                    '- M3型：h0>hc>h，降水曲线（急流）',
                    '- 判别：i<Jc（缓坡）'
                ],
                'points': 10
            },
            {
                'id': 3,
                'question': '简述重力坝的主要荷载及其作用方向。（10分）',
                'answer_points': [
                    '主要荷载（10分）：',
                    '1. 坝体自重（竖直向下）',
                    '2. 上游水压力（水平指向下游）',
                    '3. 下游水压力（水平指向上游）',
                    '4. 扬压力（竖直向上）',
                    '5. 泥沙压力（水平指向下游）',
                    '6. 浪压力（水平指向下游）',
                    '7. 地震力（水平+竖直）',
                    '8. 温度荷载'
                ],
                'points': 10
            }
        ]
        
        return {
            'questions': questions,
            'total_points': sum([q['points'] for q in questions])
        }
    
    def calculation_questions(self) -> Dict:
        """计算题（50分）"""
        questions = [
            {
                'id': 1,
                'question': '一平底闸门，宽度b=2m，上游水深h1=4m，下游水深h2=1m，'
                          '求作用在闸门上的总水压力及作用点位置。（10分）',
                'solution': {
                    'given': ['b=2m', 'h1=4m', 'h2=1m', 'γ=9810 N/m³'],
                    'steps': [
                        '上游水压力：',
                        'p_c1 = γh1/2 = 9810×4/2 = 19620 Pa',
                        'P1 = p_c1×A1 = 19620×(4×2) = 156960 N',
                        'y_c1 = h1/3 = 4/3 = 1.33 m（从水面算起）',
                        '',
                        '下游水压力：',
                        'p_c2 = γh2/2 = 9810×1/2 = 4905 Pa',
                        'P2 = p_c2×A2 = 4905×(1×2) = 9810 N',
                        'y_c2 = h2/3 = 1/3 = 0.33 m',
                        '',
                        '总水压力：',
                        'P = P1 - P2 = 156960 - 9810 = 147150 N ≈ 147.2 kN',
                        '',
                        '作用点（对底部取矩）：',
                        'y_p = (P1×y_c1 - P2×y_c2)/P',
                        '    = (156960×1.33 - 9810×0.33)/147150',
                        '    = 1.40 m（从底部算起）'
                    ],
                    'answer': 'P = 147.2 kN，作用点距底部1.40 m'
                },
                'points': 10
            },
            {
                'id': 2,
                'question': '圆管直径d=0.2m，流量Q=0.05m³/s，水温20°C（ν=1.0×10⁻⁶m²/s），'
                          '判断流态并计算沿程损失系数λ。（10分）',
                'solution': {
                    'given': ['d=0.2m', 'Q=0.05m³/s', 'ν=1.0×10⁻⁶m²/s'],
                    'steps': [
                        '计算流速：',
                        'A = πd²/4 = π×0.2²/4 = 0.0314 m²',
                        'v = Q/A = 0.05/0.0314 = 1.59 m/s',
                        '',
                        '计算Re数：',
                        'Re = vd/ν = 1.59×0.2/(1.0×10⁻⁶)',
                        '   = 318000 > 2320',
                        '',
                        '流态判断：紊流',
                        '',
                        '计算λ（紊流光滑区，Blasius公式）：',
                        'λ = 0.3164/Re^0.25',
                        '  = 0.3164/318000^0.25',
                        '  = 0.0133'
                    ],
                    'answer': '紊流，λ = 0.0133'
                },
                'points': 10
            },
            {
                'id': 3,
                'question': '矩形明渠，底宽b=3m，水深h=2m，流量Q=12m³/s，糙率n=0.02，'
                          '底坡i=0.001，判断流态。（10分）',
                'solution': {
                    'given': ['b=3m', 'h=2m', 'Q=12m³/s', 'n=0.02', 'i=0.001'],
                    'steps': [
                        '计算过水断面积：',
                        'A = bh = 3×2 = 6 m²',
                        '',
                        '计算流速：',
                        'v = Q/A = 12/6 = 2 m/s',
                        '',
                        '计算Fr数：',
                        'Fr = v/√(gh) = 2/√(9.81×2) = 0.45 < 1',
                        '',
                        '流态判断：缓流',
                        '',
                        '验证（计算正常水深h0）：',
                        'R = A/P = 6/(3+2×2) = 0.857 m',
                        'Q = A×R^(2/3)×i^(1/2)/n',
                        '12 ≈ 6×0.857^(2/3)×0.001^(1/2)/0.02',
                        '12 ≈ 11.8（接近，h≈h0）',
                        '',
                        '判断：近似均匀流，缓流'
                    ],
                    'answer': 'Fr = 0.45，缓流'
                },
                'points': 10
            },
            {
                'id': 4,
                'question': '重力坝高H=50m，底宽b=40m，坝体容重γc=24kN/m³，上游水深h1=45m，'
                          '下游无水，扬压力折减系数α=0.25，摩擦系数f=0.7，计算抗滑稳定安全系数。（10分）',
                'solution': {
                    'given': ['H=50m', 'b=40m', 'γc=24kN/m³', 'h1=45m', 'α=0.25', 'f=0.7'],
                    'steps': [
                        '坝体自重（单宽）：',
                        'W = γc×b×H = 24×40×50 = 48000 kN/m',
                        '',
                        '上游水压力：',
                        'P1 = γh1²/2 = 9.81×45²/2 = 9934 kN/m',
                        '',
                        '扬压力：',
                        'U = αγh1×b = 0.25×9.81×45×40 = 4415 kN/m',
                        '',
                        '有效重力：',
                        'ΣV = W - U = 48000 - 4415 = 43585 kN/m',
                        '',
                        '水平力：',
                        'ΣH = P1 = 9934 kN/m',
                        '',
                        '抗滑稳定安全系数：',
                        'Kc = f·ΣV/ΣH = 0.7×43585/9934 = 3.07 > 3.0',
                        '',
                        '结论：满足抗滑稳定要求'
                    ],
                    'answer': 'Kc = 3.07，满足要求'
                },
                'points': 10
            },
            {
                'id': 5,
                'question': '某泵站设计流量Q=0.5m³/s，扬程H=20m，选用泵的额定参数：'
                          'Q0=0.25m³/s，H0=22m，η0=0.80，n0=1450r/min，'
                          '求需要并联的泵台数及总功率。（10分）',
                'solution': {
                    'given': ['Q=0.5m³/s', 'H=20m', 'Q0=0.25m³/s', 
                             'H0=22m', 'η0=0.80', 'n0=1450r/min'],
                    'steps': [
                        '并联台数：',
                        'n_泵 = Q/Q0 = 0.5/0.25 = 2台',
                        '',
                        '验证扬程（并联扬程不变）：',
                        'H_并联 ≈ H0 = 22m > 20m ✓',
                        '',
                        '单泵功率：',
                        'P_单 = ρgQH/(η×1000)',
                        '    = 1000×9.81×0.25×20/(0.80×1000)',
                        '    = 61.3 kW',
                        '',
                        '总功率：',
                        'P_总 = 2×P_单 = 2×61.3 = 122.6 kW',
                        '',
                        '考虑电机效率（0.95）和安全系数（1.1）：',
                        'P_电机 = P_总×1.1/0.95 = 142 kW',
                        '',
                        '选择标准电机：2×75kW = 150kW'
                    ],
                    'answer': '2台并联，总功率150kW'
                },
                'points': 10
            }
        ]
        
        return {
            'questions': questions,
            'total_points': sum([q['points'] for q in questions])
        }
    
    def design_question(self) -> Dict:
        """设计题（20分）"""
        question = {
            'id': 1,
            'question': '设计一梯形灌溉渠道，已知：流量Q=5m³/s，底坡i=0.0005，'
                       '糙率n=0.025，边坡系数m=1.5，底宽与水深比b/h=2。'
                       '求：(1)渠道断面尺寸；(2)流速；(3)Fr数并判断流态。（20分）',
            'solution': {
                'given': ['Q=5m³/s', 'i=0.0005', 'n=0.025', 'm=1.5', 'b/h=2'],
                'steps': [
                    '(1) 断面设计（曼宁公式）：',
                    '',
                    '设h为水深，则b=2h',
                    '过水断面积：A = (b+mh)h = (2h+1.5h)h = 3.5h²',
                    '湿周：P = b + 2h√(1+m²) = 2h + 2h√(1+1.5²) = 2h + 3.606h = 5.606h',
                    '水力半径：R = A/P = 3.5h²/(5.606h) = 0.624h',
                    '',
                    '由曼宁公式：Q = A×R^(2/3)×i^(1/2)/n',
                    '5 = 3.5h²×(0.624h)^(2/3)×0.0005^(1/2)/0.025',
                    '5 = 3.5h²×0.786h^(2/3)×0.0224/0.025',
                    '5 = 2.45h^(8/3)',
                    'h^(8/3) = 2.04',
                    'h = 1.35 m',
                    '',
                    'b = 2h = 2×1.35 = 2.70 m',
                    '',
                    '(2) 流速：',
                    'A = 3.5h² = 3.5×1.35² = 6.38 m²',
                    'v = Q/A = 5/6.38 = 0.78 m/s',
                    '',
                    '(3) Fr数：',
                    'Fr = v/√(gh) = 0.78/√(9.81×1.35) = 0.21 < 1',
                    '',
                    '流态判断：缓流'
                ],
                'answer': {
                    '水深': 'h = 1.35 m',
                    '底宽': 'b = 2.70 m',
                    '流速': 'v = 0.78 m/s',
                    '流态': 'Fr = 0.21，缓流'
                }
            },
            'points': 20
        }
        
        return {
            'question': question,
            'total_points': question['points']
        }
    
    def time_management(self) -> Dict:
        """时间管理建议"""
        return {
            'total_time': 180,
            'allocation': [
                {'section': '选择题', 'time': 15, 'percentage': 8.3, 
                 'strategy': '快速作答，确定答案，不纠结'},
                {'section': '填空题', 'time': 15, 'percentage': 8.3,
                 'strategy': '准确填写，注意单位和格式'},
                {'section': '简答题', 'time': 30, 'percentage': 16.7,
                 'strategy': '分点作答，条理清晰'},
                {'section': '计算题', 'time': 90, 'percentage': 50.0,
                 'strategy': '详细步骤，公式明确，单位统一'},
                {'section': '设计题', 'time': 20, 'percentage': 11.1,
                 'strategy': '完整设计，结果合理，图文并茂'},
                {'section': '检查', 'time': 10, 'percentage': 5.6,
                 'strategy': '核对计算，检查单位，查看遗漏'}
            ]
        }
    
    def scoring_analysis(self, user_answers: Dict = None) -> Dict:
        """评分分析"""
        sections = {
            'choice': {'name': '选择题', 'total': 30, 'target': 24},
            'fill': {'name': '填空题', 'total': 20, 'target': 16},
            'short': {'name': '简答题', 'total': 30, 'target': 24},
            'calculation': {'name': '计算题', 'total': 50, 'target': 42},
            'design': {'name': '设计题', 'total': 20, 'target': 14}
        }
        
        total_target = sum([s['target'] for s in sections.values()])
        
        return {
            'sections': sections,
            'total_target': total_target,
            'difficulty_level': '基础',
            'pass_score': 90,
            'good_score': 120,
            'excellent_score': 135
        }
    
    def plot_analysis(self):
        """绘制试卷分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        choice = self.choice_questions()
        fill = self.fill_questions()
        short = self.short_questions()
        calculation = self.calculation_questions()
        design = self.design_question()
        time_mgmt = self.time_management()
        scoring = self.scoring_analysis()
        
        # 1. 试卷结构
        ax1 = plt.subplot(3, 3, 1)
        
        sections = ['选择题', '填空题', '简答题', '计算题', '设计题']
        scores = [30, 20, 30, 50, 20]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        wedges, texts, autotexts = ax1.pie(scores, labels=sections, autopct='%1.1f%%',
                                           colors=colors, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax1.set_title(f'{self.exam_name}\n总分{self.total_score}分', 
                     fontsize=12, fontweight='bold')
        
        # 2. 题型分值
        ax2 = plt.subplot(3, 3, 2)
        
        bars = ax2.barh(sections, scores, color=colors, alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, scores):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2,
                    f'{val}分', ha='left', va='center',
                    fontsize=10, fontweight='bold')
        
        ax2.set_xlabel('分值', fontsize=10)
        ax2.set_title('题型分值分布', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 3. 时间分配
        ax3 = plt.subplot(3, 3, 3)
        
        time_sections = [t['section'] for t in time_mgmt['allocation']]
        time_values = [t['time'] for t in time_mgmt['allocation']]
        
        bars = ax3.bar(range(len(time_sections)), time_values, 
                      color=colors, alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, time_values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val}分钟', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        
        ax3.set_xticks(range(len(time_sections)))
        ax3.set_xticklabels(time_sections, rotation=45, ha='right')
        ax3.set_ylabel('时间（分钟）', fontsize=10)
        ax3.set_title(f'时间分配建议（共{self.time_limit}分钟）', 
                     fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 得分目标
        ax4 = plt.subplot(3, 3, 4)
        
        target_sections = list(scoring['sections'].keys())
        target_names = [scoring['sections'][s]['name'] for s in target_sections]
        target_totals = [scoring['sections'][s]['total'] for s in target_sections]
        target_scores = [scoring['sections'][s]['target'] for s in target_sections]
        
        x = np.arange(len(target_names))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, target_totals, width, label='满分',
                       color='lightblue', alpha=0.7, edgecolor='black')
        bars2 = ax4.bar(x + width/2, target_scores, width, label='目标',
                       color='gold', alpha=0.7, edgecolor='black')
        
        ax4.set_xlabel('题型', fontsize=10)
        ax4.set_ylabel('分数', fontsize=10)
        ax4.set_title(f'得分目标（总目标{scoring["total_target"]}分）', 
                     fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(target_names, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. 知识点分布
        ax5 = plt.subplot(3, 3, 5)
        
        knowledge_areas = ['静水力学', '动水力学', '管流', '明渠流', 
                          '渗流', '水工', '泵站', '综合']
        knowledge_weights = [10, 15, 20, 25, 5, 15, 5, 5]
        
        bars = ax5.bar(knowledge_areas, knowledge_weights, 
                      color='skyblue', alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, knowledge_weights):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val}%', ha='center', va='bottom',
                    fontsize=8, fontweight='bold')
        
        ax5.set_xlabel('知识点', fontsize=10)
        ax5.set_ylabel('占比（%）', fontsize=10)
        ax5.set_title('知识点分布', fontsize=12, fontweight='bold')
        ax5.tick_params(axis='x', rotation=45)
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. 难度分析
        ax6 = plt.subplot(3, 3, 6)
        
        difficulty_levels = ['容易', '中等', '较难']
        difficulty_scores = [60, 70, 20]  # 分值分布
        colors_diff = ['green', 'orange', 'red']
        
        wedges, texts, autotexts = ax6.pie(difficulty_scores, labels=difficulty_levels,
                                           autopct='%1.1f%%', colors=colors_diff,
                                           startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax6.set_title('难度分布', fontsize=12, fontweight='bold')
        
        # 7. 答题策略
        ax7 = plt.subplot(3, 3, 7)
        ax7.axis('off')
        
        ax7.text(0.5, 0.95, '答题策略', fontsize=11, ha='center', fontweight='bold')
        
        strategies = [
            '1. 先易后难，保证基础分',
            '2. 计算题详写步骤，公式明确',
            '3. 选择题用排除法，提高准确率',
            '4. 填空题注意单位和有效数字',
            '5. 简答题分点作答，条理清晰',
            '6. 设计题画图辅助，结果合理',
            '7. 留出检查时间，避免低级错误',
            '8. 遇难题先跳过，回头再战'
        ]
        
        y_pos = 0.82
        for strategy in strategies:
            ax7.text(0.05, y_pos, strategy, fontsize=9, va='top')
            y_pos -= 0.10
        
        ax7.set_title('考试技巧', fontsize=12, fontweight='bold')
        
        # 8. 评分标准
        ax8 = plt.subplot(3, 3, 8)
        
        score_ranges = ['<90分\n不及格', '90-120分\n及格', 
                       '120-135分\n良好', '135-150分\n优秀']
        score_colors = ['red', 'orange', 'lightgreen', 'darkgreen']
        
        y_positions = [0, 90, 120, 135, 150]
        for i in range(len(score_ranges)):
            ax8.barh([i], [y_positions[i+1]-y_positions[i]], 
                    left=y_positions[i], color=score_colors[i],
                    alpha=0.7, edgecolor='black')
            ax8.text((y_positions[i]+y_positions[i+1])/2, i,
                    score_ranges[i], ha='center', va='center',
                    fontsize=9, fontweight='bold')
        
        ax8.axvline(self.target_score, color='blue', linestyle='--', 
                   linewidth=2, label=f'目标{self.target_score}分')
        
        ax8.set_xlabel('总分', fontsize=10)
        ax8.set_title('评分标准', fontsize=12, fontweight='bold')
        ax8.set_yticks([])
        ax8.legend()
        ax8.grid(True, alpha=0.3, axis='x')
        
        # 9. 试卷信息汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '信息'],
            ['试卷名称', self.exam_name],
            ['总分', f'{self.total_score}分'],
            ['时间', f'{self.time_limit}分钟'],
            ['目标分数', f'{self.target_score}分'],
            ['难度', '⭐⭐⭐'],
            ['题型数', '5种'],
            ['题目总数', '29题'],
            ['适用对象', '基础扎实学生']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='left', loc='center',
                         colWidths=[0.40, 0.55])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        for i in range(2):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键信息
        for i in [2, 4, 5]:
            for j in range(2):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('试卷信息', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch15_exam01_foundation_test.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch15_exam01_foundation_test.png")
        plt.show()
    
    def print_exam(self):
        """打印完整试卷"""
        print("\n" + "="*70)
        print(self.exam_name.center(70))
        print("="*70)
        print(f"\n总分：{self.total_score}分    时间：{self.time_limit}分钟    目标：{self.target_score}分\n")
        print("="*70)
        
        # 选择题
        print("\n一、选择题（共30分，每题3分）\n")
        choice = self.choice_questions()
        for q in choice['questions']:
            print(f"{q['id']}. {q['question']}")
            for opt in q['options']:
                print(f"   {opt}")
            print(f"   【答案】{q['answer']} - {q['explanation']}")
            print()
        
        # 填空题
        print("\n二、填空题（共20分，每空2分）\n")
        fill = self.fill_questions()
        for q in fill['questions']:
            print(f"{q['id']}. {q['question']}")
            print(f"   【答案】{q['answer']}")
            print()
        
        # 简答题
        print("\n三、简答题（共30分）\n")
        short = self.short_questions()
        for q in short['questions']:
            print(f"{q['id']}. {q['question']}")
            print(f"   【答案要点】")
            for point in q['answer_points']:
                print(f"   {point}")
            print()
        
        # 计算题
        print("\n四、计算题（共50分）\n")
        calculation = self.calculation_questions()
        for q in calculation['questions']:
            print(f"{q['id']}. {q['question']}")
            print(f"   【解答】")
            print(f"   已知：{', '.join(q['solution']['given'])}")
            print(f"   解：")
            for step in q['solution']['steps']:
                print(f"   {step}")
            print(f"   【答案】{q['solution']['answer']}")
            print()
        
        # 设计题
        print("\n五、设计题（共20分）\n")
        design = self.design_question()
        q = design['question']
        print(f"{q['id']}. {q['question']}")
        print(f"   【解答】")
        print(f"   已知：{', '.join(q['solution']['given'])}")
        print(f"   解：")
        for step in q['solution']['steps']:
            print(f"   {step}")
        print(f"   【答案】")
        for key, val in q['solution']['answer'].items():
            print(f"   {key}: {val}")
        
        print(f"\n{'='*70}")
        print("试卷完成！祝考试顺利！")
        print(f"{'='*70}\n")


def main():
    exam = FoundationExam()
    exam.print_exam()
    exam.plot_analysis()


if __name__ == "__main__":
    main()
