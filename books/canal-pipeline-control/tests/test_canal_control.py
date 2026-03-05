
from code.core.saint_venant import solve_saint_venant
def test_saint_venant_routing():
    assert solve_saint_venant(10, 2) == 5.0
