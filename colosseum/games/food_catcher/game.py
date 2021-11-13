import logging
from collections import defaultdict
from random import shuffle, uniform

import numpy as np

from colosseum.utils import object_distance, random_id

from .actor import Actor
from .food import Food


class World:
    def __init__(self):
        self.width = 10
        self.height = 10

        self.agent_bases = defaultdict(list)

        self.foods = []
        self.actors = []
        self.agents = set()

        self.name = "food_catcher"

        self._max_food_sources = 5
        self._eat_max_distance = 1
        self._eat_speed = 5

        self._spawn_food()

        logging.info("food_catcher initialized")

    def register_agent(self, agent):
        if agent.id in self.agents:
            logging.warning(f"tried to register {agent.id} more than once")
            return

        self.agents.add(agent.id)

        x = uniform(0, self.width)
        y = uniform(0, self.width)

        self.agent_bases[agent.id].append({"position": (x, y), "id": 1})
        self.actors.append(Actor().set_owner(agent.id).set_position((x, y)))

        logging.info(f"agent {agent.id} registered")

    def _spawn_food(self):
        self.foods = [
            Food().set_position((uniform(0, self.width), uniform(0, self.height)))
            for _ in range(self._max_food_sources)
        ]

    def _update_food(self):
        self.foods = [food for food in self.foods if not food.vanished]

        for food in self.foods:
            food.update()

        if len(self.foods) < self._max_food_sources:
            self.foods.append(
                Food().set_position((uniform(0, self.width), uniform(0, self.height)))
            )

    @property
    def state(self):
        return {
            "foods": self.foods_state,
            "actors": self.actors_state,
            "agent_bases": self.agent_bases,
        }

    @property
    def actors_state(self):
        return [actor.state for actor in self.actors]

    @property
    def foods_state(self):
        return [food.state for food in self.foods]

    def update(self, agent_actions):
        self._update_food()

        # We shuffle to use as a tiebreaker when multiple agents are trying to
        # do the same thing at the same time
        shuffle(agent_actions)

        for agent_action in agent_actions:
            self.process_agent_actions(agent_action)

    def process_agent_actions(self, agent_action):
        owner_id = agent_action.get("agent_id")
        if owner_id not in self.agents:
            logging.warning(f"agent with id {owner_id} is not registered. Ignoring")
            return

        actions = agent_action.get("actions", [])

        for action in actions:
            action_type = action.get("action")
            actor_id = action.get("actor_id")

            if action_type == "move":
                target = action.get("target")
                self.move_actor(owner_id, actor_id, target)

            if action_type == "take_food":
                food_id = action.get("food_id")
                self.take_food(owner_id, actor_id, food_id)

    # TODO: resolve collisions
    def move_actor(self, owner_id, actor_id, target):
        # TODO: Handle actor not existing
        actor = self._get_actor(actor_id)

        # TODO: Ensure that the actor belongs to the owner
        actor.move(target)

    def take_food(self, owner_id, actor_id, food_id):
        actor = self._get_actor(actor_id)
        food = self._get_food(food_id)

        if not food:
            return

        distance = object_distance(actor, food)
        if distance > self._eat_max_distance:
            return

        food_taken = food.take(self._eat_speed)
        actor.add_food(food_taken)

    def _get_food(self, id):
        return next((food for food in self.foods if food.id == id), None)

    def _get_actor(self, id):
        return next((actor for actor in self.actors if actor.id == id), None)
