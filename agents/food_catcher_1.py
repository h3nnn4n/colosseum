#!/usr/bin/env python3

import json
import logging
import sys

import numpy as np
from utils import get_internal_id, get_state, object_distance, send_commands

AGENT_ID = None


def main():
    global AGENT_ID

    my_actors = {}

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

                # Update the current state of our actors
                for actor in state["actors"]:
                    if actor["owner_id"] != AGENT_ID:
                        continue

                    if actor["id"] not in my_actors:
                        my_actors[actor["id"]] = actor
                        my_actors[actor["id"]]["state"] = "take_food"

                    my_actors[actor["id"]].update(actor)

                actor = list(my_actors.values())[0]
                current_position = np.array(actor["position"])

                foods = state.get("foods")
                bases = [
                    base for base in state.get("bases") if base["owner_id"] == AGENT_ID
                ]
                food = foods[0]
                base = bases[0]

                distance_to_food = object_distance(actor, food)
                distance_to_base = object_distance(actor, base)
                food_position = np.array(food.get("position"))
                base_position = np.array(base.get("position"))

                if (
                    actor["state"] == "take_food"
                    and actor["food"] > 100
                    and distance_to_food > 1
                ):
                    actor["state"] = "deposit_food"

                logging.info(
                    f"actor {actor['id']} has state {actor['state']} food {actor['food']}"
                )
                if actor["state"] == "deposit_food":
                    if distance_to_base <= 0.1 and actor["food"] > 0:
                        response["actions"] = [
                            {
                                "action": "deposit_food",
                                "base_id": base["id"],
                                "actor_id": actor["id"],
                            }
                        ]
                        logging.info(
                            f"DEPOSIT {current_position=} {actor['food']} / {base['id']} {base['food']}"
                        )
                    elif distance_to_base <= 0.1:
                        actor["state"] = "take_food"
                    else:
                        direction = base_position

                        response["actions"] = [
                            {
                                "action": "move",
                                "target": direction.tolist(),
                                "actor_id": actor["id"],
                            }
                        ]
                        logging.info(
                            f"MOVE {current_position=} {base_position=} {distance_to_base=}"
                        )

                if actor["state"] == "take_food":
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
            logging.exception(e)
            return
    logging.debug("finished")


if __name__ == "__main__":
    main()
