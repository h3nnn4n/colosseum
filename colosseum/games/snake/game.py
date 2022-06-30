import itertools
import logging
from collections import defaultdict
from random import choice, shuffle, uniform

import chess

from colosseum.utils import random_id

from ..game import BaseGame
from .config import Config


class Game(BaseGame):
    def __init__(self):
        self.agents = set()
        self.agent_ids = set()

        self._config = Config
        self.name = self._config.game_name

        logging.info("snake initialized")

    @property
    def state(self):
        return {
            # foo
        }

    @property
    def outcome(self):
        return {
            # foo
        }

    @property
    def scores(self):
        return {
            # foo
        }

    @property
    def finished(self):
        return False

    def update(self, agent_actions):
        for agent_action in agent_actions:
            self._process_agent_action(agent_action)

    def _process_agent_actions(self, agent_action):
        pass
