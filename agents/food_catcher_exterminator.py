#!/usr/bin/env python3

import logging

from sdks.python.colosseum_sdk import Agent


AGENT_NAME = "exterminator"


class Exterminator(Agent):
    def __init__(self):
        super(Exterminator, self).__init__(agent_name=AGENT_NAME)

    def post_state_update(self):
        pass


def main():
    exterminator = Exterminator()

    while exterminator.run:
        exterminator.read_state()

        state = exterminator.state
        actor = state.actors.mine.first
        base = state.bases.mine.first
        food = state.foods.closest_to(actor)

        if actor.distance_to(food) < 0.1:
            actor.take(food)
        elif actor.food > 100:
            if actor.distance_to(base) >= 0.1:
                actor.move(base)
            else:
                actor.deposit_food(base)
        else:
            actor.move(food)

        exterminator.send_commands()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
