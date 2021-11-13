#!/usr/bin/env python3

import json
import logging
import sys

import numpy as np
from utils import object_distance, send_commands

AGENT_ID = None


def get_internal_id():
    import random
    import string
    from datetime import datetime

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


def main():
    global AGENT_ID

    logging.basicConfig(
        filename=f"food_catcher_{get_internal_id()}.log", level=logging.INFO
    )

    logging.debug("starting")
    while True:
        try:
            state = get_state()
            response = {}

            if state.get("stop"):
                logging.info(f"stopping, reason: {state.get('stop')}")
                break

            if state.get("set_agent_id"):
                AGENT_ID = state.get("set_agent_id")
                logging.info(f"{AGENT_ID=}")

            if state.get("ping"):
                logging.info("got ping")
                response["pong"] = "foobar"

            if state.get("actors"):
                logging.debug("got world state")
                my_actors = [
                    actor for actor in state["actors"] if actor["owner_id"] == AGENT_ID
                ]
                actor = my_actors[0]
                current_position = np.array(actor["position"])

                foods = state.get("foods")
                food = foods[0]
                distance_to_food = object_distance(food, actor)
                food_position = np.array(food.get("position"))

                if distance_to_food < 1:
                    response["actions"] = [
                        {
                            "action": "take_food",
                            "food_id": food["id"],
                            "actor_id": actor["id"],
                        }
                    ]
                    logging.info(
                        f"TAKE {current_position=} {food_position=} {food['quantity']}"
                    )
                else:
                    direction = food_position

                    response["actions"] = [
                        {
                            "action": "move",
                            "target": direction.tolist(),
                            "actor_id": actor["id"],
                        }
                    ]
                    logging.info(
                        f"MOVE {current_position=} {food_position=} {distance_to_food}"
                    )

            if AGENT_ID:
                response["agent_id"] = AGENT_ID

            logging.debug(f"sending {response}")
            send_commands(response)
        except Exception as e:
            logging.error(e)
            return
    logging.debug("finished")


if __name__ == "__main__":
    main()
