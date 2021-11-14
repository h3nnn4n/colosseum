import random
import string
from datetime import datetime

import numpy as np


def get_internal_id():
    now = datetime.now()

    random_string = "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6
        )
    )
    return "_".join([now.strftime("%y%m%d_%H%M%S"), random_string])


def distance_between(a, b):
    assert a is not None
    assert b is not None

    a_pos = np.array(get_position(a))
    b_pos = np.array(get_position(b))

    return np.linalg.norm(a_pos - b_pos)


def get_position(entity):
    if isinstance(entity, (tuple, list)):
        return entity
    elif hasattr(entity, "position"):
        return entity.position
    elif entity.get("position"):
        return entity.get("position")


def get_id(entity):
    if isinstance(entity, (str)):
        return entity
    elif hasattr(entity, "id"):
        return entity.id
    elif entity.get("id"):
        return entity.get("id")
