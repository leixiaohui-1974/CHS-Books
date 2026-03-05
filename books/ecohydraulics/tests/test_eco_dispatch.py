
from code.core.ecological_dispatch import calculate_ecological_baseflow
def test_baseflow_constraint():
    assert calculate_ecological_baseflow(100) == 10.0
