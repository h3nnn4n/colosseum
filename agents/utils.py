import json
import sys

import numpy as np


def object_distance(a, b):
    assert a is not None
    assert b is not None

    if hasattr(a, "position"):
        a_pos = np.array(a.position)
    else:
        a_pos = np.array(a["position"])

    if hasattr(b, "position"):
        b_pos = np.array(b.position)
    else:
        b_pos = np.array(b["position"])

    return np.linalg.norm(a_pos - b_pos)


def send_commands(data):
    print(json.dumps(data))
    sys.stdout.flush()
