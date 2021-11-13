import json
import logging
import random
import string
import sys
from datetime import datetime

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
    data_encoded = json.dumps(data)
    sys.stdout.write(data_encoded + "\n")
    sys.stdout.flush()


def get_internal_id():
    now = datetime.now()

    random_string = "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6
        )
    )
    return "_".join([now.strftime("%y%m%d%H%M%S"), random_string])


def get_state():
    logging.debug("waiting for data")
    data = sys.stdin.readline()
    logging.debug(f"got data: {data}")
    state = json.loads(data)
    return state


def get_nearest_food_to_actor(state, actor):
    foods = state.get("foods")
    closest_food = foods[0]
    distance = object_distance(closest_food, actor)

    for food in foods:
        new_distance = object_distance(food, actor)
        if new_distance < distance:
            distance = new_distance
            closest_food = food

    return food
