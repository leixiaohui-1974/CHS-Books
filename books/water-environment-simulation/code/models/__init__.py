"""
核心模型模块
"""

from .diffusion import Diffusion1D, Diffusion2D
from .advection_diffusion import AdvectionDiffusion1D
from .reaction import ReactionKinetics, ReactionTransport1D
from .dissolved_oxygen import StreeterPhelps, DOBODCoupled, calculate_reaeration_coefficient
from .nutrients import NitrogenCycle, PhosphorusCycle, EutrophicationIndex, calculate_oxygen_consumption
from .self_purification import (SelfPurificationCapacity, WaterQualityIndex, 
                                calculate_assimilative_capacity, functional_zone_classification)
from .multi_source import MultiSourceRiver1D, PointSource, calculate_superposition_factor
from .nonpoint_source import (SCSCurveNumber, EventMeanConcentration, NonPointSourceRiver1D,
                              calculate_first_flush_factor, calculate_buildup_washoff)
from .thermal_pollution import (ThermalPlume2D, calculate_surface_heat_exchange,
                                 calculate_thermal_tolerance, calculate_cooling_efficiency)
from .lateral_mixing import (LateralMixing2D, calculate_mixing_time,
                              calculate_complete_mixing_distance, calculate_concentration_at_bank)
from .river_bend import (RiverBend2D, calculate_bend_mixing_length,
                          calculate_curvature_radius, calculate_secondary_flow_strength)
from .estuary import (EstuarySaltIntrusion1D, calculate_stratification_parameter,
                      calculate_mixing_parameter, calculate_salt_wedge_length, estimate_intake_risk)
from .lake_cmfr import (LakeCMFR, calculate_critical_load, calculate_flushing_efficiency)
from .lake_nutrient import (VollenweiderModel, calculate_trophic_state, 
                             calculate_vollenweider_loading, calculate_phosphorus_budget,
                             predict_response_time)
from .stratified_reservoir import (StratifiedReservoir1D, calculate_buoyancy_frequency,
                                    calculate_richardson_number, estimate_mixing_depth)
from .density_current import (DensityCurrent2D, calculate_densimetric_froude,
                               estimate_underflow_velocity)

__all__ = [
    'Diffusion1D',
    'Diffusion2D',
    'AdvectionDiffusion1D',
    'ReactionKinetics',
    'ReactionTransport1D',
    'StreeterPhelps',
    'DOBODCoupled',
    'calculate_reaeration_coefficient',
    'NitrogenCycle',
    'PhosphorusCycle',
    'EutrophicationIndex',
    'calculate_oxygen_consumption',
    'SelfPurificationCapacity',
    'WaterQualityIndex',
    'calculate_assimilative_capacity',
    'functional_zone_classification',
    'MultiSourceRiver1D',
    'PointSource',
    'calculate_superposition_factor',
    'SCSCurveNumber',
    'EventMeanConcentration',
    'NonPointSourceRiver1D',
    'calculate_first_flush_factor',
    'calculate_buildup_washoff',
    'ThermalPlume2D',
    'calculate_surface_heat_exchange',
    'calculate_thermal_tolerance',
    'calculate_cooling_efficiency',
    'LateralMixing2D',
    'calculate_mixing_time',
    'calculate_complete_mixing_distance',
    'calculate_concentration_at_bank',
    'RiverBend2D',
    'calculate_bend_mixing_length',
    'calculate_curvature_radius',
    'calculate_secondary_flow_strength',
    'EstuarySaltIntrusion1D',
    'calculate_stratification_parameter',
    'calculate_mixing_parameter',
    'calculate_salt_wedge_length',
    'estimate_intake_risk',
    'LakeCMFR',
    'calculate_critical_load',
    'calculate_flushing_efficiency',
    'VollenweiderModel',
    'calculate_trophic_state',
    'calculate_vollenweider_loading',
    'calculate_phosphorus_budget',
    'predict_response_time',
    'StratifiedReservoir1D',
    'calculate_buoyancy_frequency',
    'calculate_richardson_number',
    'estimate_mixing_depth',
    'DensityCurrent2D',
    'calculate_densimetric_froude',
    'estimate_underflow_velocity',
]
