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
            data[agent_id] = 1

        return data

    @property
    def state(self):
        return {"foo": "bar"}

    def update(self, agent_actions):
        self._tick += 1
