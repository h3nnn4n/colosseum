#!/usr/bin/env python3

import logging

from sdks.python.colosseum_sdk import Agent


AGENT_NAME = "exterminator"


class Exterminator(Agent):
    def __init__(self):
        super(Exterminator, self).__init__(agent_name=AGENT_NAME)

        self.gatherers = set()
        self.killers = set()

    def what_to_spawn_next(self):
        target_gather_kill_ratio = 2
        self.gather_kill_ratio = len(self.gatherers) / (len(self.killers) or 1)

        if self.gather_kill_ratio < target_gather_kill_ratio:
            return "gatherer"
        else:
            return "killer"

    def post_state_update(self):
        assigned_actors = self.gatherers | self.killers
        idle_actors = self.state.actors.mine.id_not_in(assigned_actors)

        for actor in idle_actors:
            what = self.what_to_spawn_next()
            logging.info(f"added a {what}")
            if what == "killer":
                self.killers.add(actor.id)
            if what == "gatherer":
                self.gatherers.add(actor.id)

        enemies_left = self.state.actors.enemy.count
        enemies_left += self.state.bases.enemy.count
        if enemies_left == 0 and len(self.killers) > 0:
            logging.info(
                f"turning {len(self.killers)} killers into gatherers since there are no enemies left"
            )
            self.gatherers.update(self.killers)
            self.killers.clear()


def main():
    exterminator = Exterminator()

    while exterminator.run:
        exterminator.read_state()

        state = exterminator.state
        for actor in state.actors.mine.id_in(exterminator.gatherers):
            food = state.foods.closest_to(actor)

            if actor.distance_to(food) < 0.1:
                actor.take(food)
            elif actor.food > 100:
                base = state.bases.closest_to(actor)
                if actor.distance_to(base) >= 0.1:
                    actor.move(base)
                else:
                    actor.deposit_food(base)
            else:
                actor.move(food)

        if len(exterminator.killers) >= 2:
            base = state.bases.first
            enemy = state.actors.enemy.closest_to(base) or state.bases.enemy.closest_to(
                base
            )

            for actor in state.actors.mine.id_in(exterminator.killers):
                if not enemy:
                    break

                if actor.distance_to(enemy) < 4:
                    actor.attack(enemy)
                else:
                    actor.move(enemy)

        for base in state.bases.mine:
            if base.food > 100 and state.actors.mine.count < 6:
                base.spawn()

        exterminator.send_commands()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
