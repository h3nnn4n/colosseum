#!/usr/bin/env python3

import json
import logging
import sys

import numpy as np


def get_internal_id():
    import random
    import string
    from datetime import datetime

    now = datetime.now()

    random_string = "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6))
    return "_".join([now.strftime("%y%m%d%H%M%S"), random_string])


def main():
    logging.basicConfig(filename=f"food_catcher_{get_internal_id()}.log", level=logging.INFO)
    agent_id = None

    while True:
        try:
            data = sys.stdin.readline().strip()
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

            if state.get("agent_positions"):
                current_position = np.array(state["agent_positions"][agent_id][0]["position"])

                food_positions = state.get("food_positions")
                if food_positions is not None:
                    food_position = np.array(food_positions[0].get("position"))
                    direction = food_position

                    response["actions"] = [{"action": "move", "target": direction.tolist()}]
                    logging.info(f"{current_position=} {food_position=} {direction}")

            if agent_id:
                response["agent_id"] = agent_id

            print(json.dumps(response))
        except Exception as e:
            logging.info(data)
            logging.error(e)
            return


if __name__ == "__main__":
    main()
