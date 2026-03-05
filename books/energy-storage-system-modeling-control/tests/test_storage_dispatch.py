from code.core.battery_hydro_storage import hybrid_storage_soc
def test_soc(): assert hybrid_storage_soc(80, 60) == 70.0
