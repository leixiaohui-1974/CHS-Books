
from code.core.sil_testing import verify_control_logic
def test_sil_handover():
    assert verify_control_logic('OK') == True
