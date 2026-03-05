
from code.core.wind_hydro_storage import dispatch_wind_hydro
def test_pumped_storage_dispatch():
    assert dispatch_wind_hydro(50, 30) == 20 # surplus to pump
