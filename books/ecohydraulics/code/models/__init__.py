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
from .benthic import BenthicHabitatModel
from .fish_swimming import (
    FishSwimmingModel,
    create_grass_carp,
    create_black_carp,
    create_common_carp,
    create_silver_carp
)
from .fishway import VerticalSlotFishway, create_standard_fishway
from .spawning_ground import (
    FishEgg, SpawningGround,
    create_chinese_carp_egg,
    create_standard_spawning_ground
)
from .denil_fishway import (
    DenilFishway,
    create_denil_design
)
from .fish_behavior import (
    FeedingGroundModel,
    create_grass_carp_feeding_model
)
from .fish_population import (
    RiverConnectivityIndex,
    FishPopulationModel,
    create_connectivity_scenario
)
from .river_morphology import (
    PoolRiffleSequence,
    MeanderChannel,
    BedStability,
    design_naturalized_channel
)
from .ecological_revetment import (
    EcologicalRevetment,
    VegetatedRevetment,
    RevetmentStability,
    design_ecological_revetment
)
from .floodplain_wetland import (
    FloodplainHydraulics,
    WetlandConnectivity,
    JuvenileFishGrowth,
    design_ecological_gate_operation
)
from .sediment_gravel import (
    GravelSupplementDesign,
    EstuaryHydraulics,
    RestorationAssessment
)
from .hydraulic_structures import (
    EcologicalWeir,
    StockingArea,
    HydropowerScheduling,
    DamSprayImpact
)
from .integrated_assessment import (
    WatershedEcohydrology,
    ClimateChangeImpact,
    RiverHealthAssessment,
    IntegratedManagement
)
from .lake_wetland import (
    LakeHydrodynamics,
    ConstructedWetland,
    RiparianBuffer,
    LakeStratification,
    WetlandRestoration,
    simulate_lake_wind_event,
    design_wetland_system
)
from .urban_ecohydraulics import (
    SpongeCityDesign,
    UrbanRiverRestoration,
    RainGarden,
    UrbanFloodControl,
    design_sponge_city_system
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
    'create_winter_stratification',
    'BenthicHabitatModel',
    'FishSwimmingModel',
    'create_grass_carp',
    'create_black_carp',
    'create_common_carp',
    'create_silver_carp',
    'VerticalSlotFishway',
    'create_standard_fishway',
    'DenilFishway',
    'create_denil_design',
    'FishEgg',
    'SpawningGround',
    'create_chinese_carp_egg',
    'create_standard_spawning_ground',
    'FeedingGroundModel',
    'create_grass_carp_feeding_model',
    'RiverConnectivityIndex',
    'FishPopulationModel',
    'create_connectivity_scenario',
    'PoolRiffleSequence',
    'MeanderChannel',
    'BedStability',
    'design_naturalized_channel',
    'EcologicalRevetment',
    'VegetatedRevetment',
    'RevetmentStability',
    'design_ecological_revetment',
    'FloodplainHydraulics',
    'WetlandConnectivity',
    'JuvenileFishGrowth',
    'design_ecological_gate_operation',
    'GravelSupplementDesign',
    'EstuaryHydraulics',
    'RestorationAssessment',
    'EcologicalWeir',
    'StockingArea',
    'HydropowerScheduling',
    'DamSprayImpact',
    'WatershedEcohydrology',
    'ClimateChangeImpact',
    'RiverHealthAssessment',
    'IntegratedManagement',
    'LakeHydrodynamics',
    'ConstructedWetland',
    'RiparianBuffer',
    'LakeStratification',
    'WetlandRestoration',
    'simulate_lake_wind_event',
    'design_wetland_system',
    'SpongeCityDesign',
    'UrbanRiverRestoration',
    'RainGarden',
    'UrbanFloodControl',
    'design_sponge_city_system'
]
