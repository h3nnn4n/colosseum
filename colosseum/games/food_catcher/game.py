import logging
import random
import string
from collections import defaultdict
from random import shuffle, uniform

import numpy as np


def random_id():
    return "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6))


class Actor:
    def __init__(self):
        self.position = None
        self.id = random_id()
        self.owner_id = None
        self.speed = 0.5

    def set_owner(self, owner_id):
        self.owner_id = owner_id
        return self

    def set_position(self, position):
        self.position = position
        return self

    def move(self, target):
        target = np.array(target)
        actor_position = np.array(self.position)
        move_direction = target - actor_position
        distance_to_target = np.linalg.norm(move_direction)
        distance_to_move = min(self.speed, distance_to_target)

        if distance_to_move > 1e-4:
            actor_position_new = actor_position + (move_direction / distance_to_target * distance_to_move)
            self.position = actor_position_new.tolist()
            logging.info(
                f"actor {self.id} moved from {actor_position} to {actor_position_new} with target {target} speed {distance_to_move}"
            )
            return

        logging.info(f"actor {self.id} {actor_position=} is already at {target=}")

    @property
    def state(self):
        return {"position": self.position, "id": self.id, "owner_id": self.owner_id}


class World:
    def __init__(self):
        self.width = 10
        self.height = 10

        self.max_food_sources = 5
        self.food_quantity_max = 50
        self.food_quantity_min = 0.1
        self.food_growth_rate = 0.1

        self.food_positions = []
        self.agent_bases = defaultdict(list)

        self.actors = []
        self.agents = set()

        self.name = "food_catcher"

        self._current_food_id = 0
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

    def new_food_id(self):
        self._current_food_id += 1
        return self._current_food_id - 1

    def _spawn_food(self):
        self.food_positions = [
            {
                "position": (uniform(0, self.width), uniform(0, self.height)),
                "quantity": uniform(1, self.food_quantity_max),
                "id": self.new_food_id(),
            }
            for _ in range(self.max_food_sources)
        ]

    def _update_food(self):
        for food in self.food_positions:
            food["quantity"] = min(food["quantity"] * (1.0 + self.food_growth_rate), self.food_quantity_max)

        self.food_positions = [food for food in self.food_positions if food["quantity"] >= self.food_quantity_min]

    @property
    def state(self):
        return {"food_positions": self.food_positions, "actors": self.actors_state, "agent_bases": self.agent_bases}

    @property
    def actors_state(self):
        return [actor.state for actor in self.actors]

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

    def move_actor(self, owner_id, actor_id, target):
        actor = next((a for a in self.actors if a.id == actor_id), None)

        # TODO: Ensure that the actor belongs to the owner
        actor.move(target)
