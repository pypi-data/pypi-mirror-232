import os
import pathlib
import sys
"""
TEST USER-DEFINED PATHS
"""


def test_paths():
    prj_dir = (pathlib.Path(__file__)).parent.resolve().parent.resolve()
    assert str(prj_dir) in sys.path
    # module_path = os.path.dirname(bmservices.__file__)
    # assert module_path in sys.path
