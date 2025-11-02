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
from .vegetation import (
    VegetationType,
    VegetatedChannel,
    VegetationGrowthModel,
    create_reed,
    create_cattail,
    create_submerged_plant,
    create_willow_shrub
)
from .thermal import (
    ThermalStratificationModel,
    DissolvedOxygenModel,
    ReservoirStratificationAnalyzer,
    create_summer_stratification,
    create_winter_stratification
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
    'generate_iha_report',
    'VegetationType',
    'VegetatedChannel',
    'VegetationGrowthModel',
    'create_reed',
    'create_cattail',
    'create_submerged_plant',
    'create_willow_shrub',
    'ThermalStratificationModel',
    'DissolvedOxygenModel',
    'ReservoirStratificationAnalyzer',
    'create_summer_stratification',
    'create_winter_stratification'
]
