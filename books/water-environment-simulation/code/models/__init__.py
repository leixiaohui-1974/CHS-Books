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
]
