import logging
from collections import defaultdict
from random import shuffle, uniform

import numpy as np


class World:
    def __init__(self):
        self.width = 10
        self.height = 10

        self.food_positions = [(5, 5)]
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

    def process_agent_actions(self, agent_actions):
        agent_id = agent_actions.get("agent_id")
        if agent_id not in self.agents:
            logging.warning(f"agent with id {agent_id} is not registered. Ignoring")
            return

        for agent_action in agent_actions.get("actions"):
            action_type = agent_action.get("action")

            if action_type == "move":
                target_ = agent_action.get("target")
                target = np.array(target_)
                print(target)
