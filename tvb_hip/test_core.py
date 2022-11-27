from tvb_hip import tools


def test_fs_found():
    assert tools.Local().fs_ok

def test_mrt_found():
    assert tools.Local().mrt_ok

def test_fsl_found():
    assert tools.Local().fsl_ok
