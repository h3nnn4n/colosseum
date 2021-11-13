import random
import string

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


def random_id():
    return "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6
        )
    )
