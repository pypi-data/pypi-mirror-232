import sys
from pathlib import Path


def load_path():
    file = Path(__file__).resolve()
    parent, root = file.parent, file.parents[1]
    sys.path.append(str(root))

    # Additionally remove the current file's directory from sys.path
    try:
        sys.path.remove(str(parent))
    except ValueError:  # Already removed
        pass


# actually load all user-defined paths
load_path()
