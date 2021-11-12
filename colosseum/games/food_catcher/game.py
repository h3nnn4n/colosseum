import logging
from random import uniform
from random import shuffle
from collections import defaultdict


class World:
    def __init__(self):
        self.width = 10
        self.height = 10

        self.food_positions = {}
        self.agent_positions = defaultdict(list)
        self.agent_bases = defaultdict(list)

        self.agents = set()

    def register_agent(self, agent):
        if agent.id in self.agents:
            logging.warning(f"tried to register {agent_id} more than once")
            return

        self.agents.append(agent.id)

        x = uniform(0, self.width)
        y = uniform(0, self.width)

        self.agent_bases[agent.id].append({"position": (x, y)})
        self.agent_positions[agent.id].append({"position": (x, y)})
        logging.info(f"agent {agent_id} registered")

    @property
    def state(self):
        return {
            "food_positions": self.food_positions,
            "agent_positions": self.agent_positions,
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

        for agent_action in agent_actions:
            action_type = agent_action.get("action")

            if action_type == "move":
                pass
