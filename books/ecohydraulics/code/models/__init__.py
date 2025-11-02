"""生态水力学模型类"""

from .channel import River, RiverReach
from .ecological_flow import EcologicalFlowCalculator
from .habitat import (
    SuitabilityCurve, 
    HabitatSuitabilityModel,
    create_carp_adult_model,
    create_carp_juvenile_model
)
from .indicators import (
    IHACalculator,
    HydraulicDiversityIndex,
    HydrologicAlterationAssessment,
    generate_iha_report
)

__all__ = [
    'River', 
    'RiverReach', 
    'EcologicalFlowCalculator',
    'SuitabilityCurve',
    'HabitatSuitabilityModel',
    'create_carp_adult_model',
    'create_carp_juvenile_model',
    'IHACalculator',
    'HydraulicDiversityIndex',
    'HydrologicAlterationAssessment',
    'generate_iha_report'
]
