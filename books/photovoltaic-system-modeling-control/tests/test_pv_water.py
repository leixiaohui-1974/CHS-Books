
from code.core.water_energy_nexus import optimize_floating_pv
def test_floating_pv_yield():
    assert optimize_floating_pv(1000) == 150.0
