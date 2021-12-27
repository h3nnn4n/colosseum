import logging

from ..food_catcher.game import World as FoodCatcherWorld
from .config import Config


class Game:
    def __init__(self):
        self._config = Config

        self._tick = 0
        self._n_epochs = self._config.n_epochs
        self.name = self._config.game_name

        self.agents = set()
        self.agent_worlds = {}

    def register_agent(self, agent):
        if agent.id in self.agents:
            logging.warning(f"tried to register {agent.id} more than once")
            return

        self.agents.add(agent.id)
        self.agent_worlds[agent.id] = FoodCatcherWorld(config=self._config)
        self.agent_worlds[agent.id].register_agent(agent)

        logging.info(f"agent {agent.id} registered")

    @property
    def finished(self):
        return self._tick >= self._n_epochs

    @property
    def outcome(self):
        return {}

    @property
    def config(self):
        return {
            k: v
            for k, v in dict(self._config.__dict__).items()
            if not k.startswith("_")
        }

    @property
    def scores(self):
        data = {}

        for agent_id in self.agents:
            data[agent_id] = self.agent_worlds[agent_id].scores[agent_id]

        return data

    @property
    def state(self):
        return {
            "state_by_agent": {
                agent_id: world.state for agent_id, world in self.agent_worlds.items()
            }
        }

    def update(self, agent_actions):
        self._tick += 1

        for agent_action in agent_actions:
            self._process_agent_actions(agent_action)

    def _process_agent_actions(self, agent_action):
        owner_id = agent_action.get("agent_id")
        if owner_id not in self.agents:
            logging.warning(f"agent with id {owner_id} is not registered. Ignoring")
            return

        self.agent_worlds[owner_id].update([agent_action])
