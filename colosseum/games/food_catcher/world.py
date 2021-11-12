import logging
from collections import defaultdict
from random import shuffle, uniform

import numpy as np


class World:
    def __init__(self):
        self.width = 10
        self.height = 10

        self.agent_speed = 0.5

        self.food_positions = [{"position": (5, 5), "quantity": 10}]
        self.agent_positions = defaultdict(list)
        self.agent_bases = defaultdict(list)

        self.agents = set()

        logging.info("food_catcher initialized")

    def register_agent(self, agent):
        if agent.id in self.agents:
            logging.warning(f"tried to register {agent.id} more than once")
            return

        self.agents.add(agent.id)

        x = uniform(0, self.width)
        y = uniform(0, self.width)

        self.agent_bases[agent.id].append({"position": (x, y), "id": 1})
        self.agent_positions[agent.id].append({"position": (x, y), "id": 1})
        logging.info(f"agent {agent.id} registered")

    @property
    def state(self):
        return {
            "food_positions": self.food_positions,
            "agent_positions": self.agent_positions,
            "agent_bases": self.agent_bases,
        }

    def update(self, agent_actions):
        # We shuffle to use as a tiebreaker when multiple agents are trying to
        # do the same thing at the same time
        shuffle(agent_actions)

        for agent_action in agent_actions:
            self.process_agent_actions(agent_action)

    def process_agent_actions(self, agent_action):
        agent_id = agent_action.get("agent_id")
        if agent_id not in self.agents:
            logging.warning(f"agent with id {agent_id} is not registered. Ignoring")
            return

        actions = agent_action.get("actions", [])

        for action in actions:
            action_type = action.get("action")

            if action_type == "move":
                target = action.get("target")
                self.move_agent(agent_id, target)

    def move_agent(self, agent_id, target):
        target = np.array(target)
        agent_position = np.array(self.agent_positions[agent_id][0]["position"])
        move_direction = target - agent_position
        distance_to_target = np.linalg.norm(move_direction)
        distance_to_move = min(self.agent_speed, distance_to_target)

        if distance_to_move > 1e-4:
            agent_position_new = agent_position + (move_direction / distance_to_target * distance_to_move)
            self.agent_positions[agent_id][0]["position"] = agent_position_new.tolist()
            logging.info(f"agent {agent_id} moved from {agent_position} to {agent_position_new} with target {target} speed {distance_to_move}")
            return

        logging.info(f"agent {agent_id} {agent_position=} is already at {target=}")
