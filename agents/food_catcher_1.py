#!/usr/bin/env python3

import json
import logging
import sys

import numpy as np
from utils import object_distance, send_commands


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


def main():
    logging.basicConfig(
        filename=f"food_catcher_{get_internal_id()}.log", level=logging.DEBUG
    )
    agent_id = None

    logging.debug("starting")
    while True:
        try:
            logging.debug("waiting for data")
            data = sys.stdin.readline().strip()
            logging.debug("got data")
            state = json.loads(data)
            response = {}

            if state.get("stop"):
                logging.info(f"stopping, reason: {state.get('stop')}")

            if state.get("set_agent_id"):
                agent_id = state.get("set_agent_id")
                logging.info(f"{agent_id=}")

            if state.get("ping"):
                logging.info("got ping")
                response["pong"] = "foobar"

            if state.get("actors"):
                logging.debug("got world state")
                my_actors = [
                    actor for actor in state["actors"] if actor["owner_id"] == agent_id
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

            if agent_id:
                response["agent_id"] = agent_id

            send_commands(response)
        except Exception as e:
            logging.info(data)
            logging.error(e)
            return


if __name__ == "__main__":
    main()
