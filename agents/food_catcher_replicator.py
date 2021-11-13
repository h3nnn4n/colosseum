#!/usr/bin/env python3

import json
import logging
import sys

import numpy as np
from utils import (
    deposit_food,
    get_internal_id,
    get_nearest_base_to_actor,
    get_state,
    move,
    object_distance,
    send_commands,
    spawn,
    take_food,
)


AGENT_ID = None
AGENT_NAME = "replicator"
AGENT_VERSION = "0.0.1"


def main():
    global AGENT_ID

    brain = {"my_actors": {}, "my_bases": {}}

    logging.basicConfig(
        filename=f"{AGENT_NAME}_{get_internal_id()}.log", level=logging.DEBUG
    )

    logging.debug("starting")
    while True:
        try:
            state = get_state()
            response = {"actions": []}

            if state.get("stop"):
                logging.info(f"stopping, reason: {state.get('stop')}")
                break

            if state.get("set_agent_id"):
                AGENT_ID = state.get("set_agent_id")
                response["agent_name"] = AGENT_NAME
                response["agent_version"] = AGENT_VERSION
                logging.info(f"{AGENT_ID=}")

            if state.get("ping"):
                logging.info("got ping")
                response["pong"] = "foobar"

            if state.get("actors"):
                logging.debug("got world state")

                # Update the current state of our actors
                my_actors = brain["my_actors"]
                for actor in state["actors"]:
                    if actor["owner_id"] != AGENT_ID:
                        continue

                    if actor["id"] not in my_actors:
                        my_actors[actor["id"]] = actor
                        my_actors[actor["id"]]["state"] = "take_food"

                    my_actors[actor["id"]].update(actor)

                # Update the current state of our bases
                my_bases = brain["my_bases"]
                for base in state["bases"]:
                    if base["owner_id"] != AGENT_ID:
                        continue

                    if base["id"] not in my_bases:
                        my_bases[base["id"]] = base

                    my_bases[base["id"]].update(base)

                response["actions"] = agent_logic(state, brain)

            if AGENT_ID:
                response["agent_id"] = AGENT_ID

            logging.debug(f"sending {response}")
            send_commands(response)
        except Exception as e:
            logging.exception(e)
            return
    logging.debug("finished")


def agent_logic(state, brain):
    actions = []

    my_actors = brain["my_actors"]
    for actor_id, actor in my_actors.items():
        actions.extend(actor_logic(state, brain, actor))

    my_bases = brain["my_bases"]
    for base_id, base in my_bases.items():
        actions.extend(base_logic(state, brain, base))

    return actions


def base_logic(state, brain, base):
    actions = []

    target_actor_count = 5

    actor_count = len(brain["my_actors"])

    if actor_count < target_actor_count and base["food"] > 100:
        actions.append(spawn(base["id"]))

    return actions


def actor_logic(state, brain, actor):
    actions = []
    foods = state.get("foods")
    food = foods[0]
    base = get_nearest_base_to_actor(brain["my_bases"].values(), actor)

    distance_to_food = object_distance(actor, food)
    distance_to_base = object_distance(actor, base)
    food_position = np.array(food.get("position"))
    base_position = np.array(base.get("position"))

    if actor["state"] == "take_food" and actor["food"] > 100 and distance_to_food > 1:
        actor["state"] = "deposit_food"

    logging.info(f"actor {actor['id']} has state {actor['state']} food {actor['food']}")
    if actor["state"] == "deposit_food":
        if distance_to_base <= 0.1 and actor["food"] > 0:
            actions.append(deposit_food(actor["id"], base["id"]))
        elif distance_to_base <= 0.1:
            actor["state"] = "take_food"
        else:
            actions.append(move(actor["id"], base_position))

    if actor["state"] == "take_food":
        if distance_to_food < 1:
            actions.append(take_food(actor["id"], food["id"]))
        else:
            actions.append(move(actor["id"], food_position))

    return actions


if __name__ == "__main__":
    main()
