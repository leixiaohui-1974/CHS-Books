"""
核心模型模块
"""

from .diffusion import Diffusion1D, Diffusion2D
from .advection_diffusion import AdvectionDiffusion1D
from .reaction import ReactionKinetics, ReactionTransport1D
from .dissolved_oxygen import StreeterPhelps, DOBODCoupled, calculate_reaeration_coefficient

__all__ = [
    'Diffusion1D',
    'Diffusion2D',
    'AdvectionDiffusion1D',
    'ReactionKinetics',
    'ReactionTransport1D',
    'StreeterPhelps',
    'DOBODCoupled',
    'calculate_reaeration_coefficient',
]
