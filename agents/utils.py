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


def get_nearest_base_to_actor(bases, actor):
    closest_base = list(bases)[0]
    distance = object_distance(closest_base, actor)

    for base in bases:
        new_distance = object_distance(base, actor)
        if new_distance < distance:
            distance = new_distance
            closest_base = base

    return base


def take_food(actor_id, food_id):
    logging.info(f"TAKE {actor_id} from {food_id}")
    return {"action": "take_food", "food_id": food_id, "actor_id": actor_id}


def deposit_food(actor_id, base_id):
    logging.info(f"DEPOSIT {actor_id} from {base_id}")
    return {"action": "deposit_food", "base_id": base_id, "actor_id": actor_id}


def move(actor_id, target):
    if not isinstance(target, (list, tuple)):
        target = target.tolist()

    logging.info(f"MOVE {actor_id} -> {target}")

    return {"action": "move", "target": target, "actor_id": actor_id}


def spawn(base_id):
    logging.info(f"SPAWN {base_id}")
    return {"action": "spawn", "base_id": base_id}
