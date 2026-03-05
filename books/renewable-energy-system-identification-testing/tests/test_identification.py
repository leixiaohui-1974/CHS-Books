from code.core.system_identification import identify_system_order
def test_sys_id(): assert identify_system_order([1.1, 2.2, 3.3]) == 3
