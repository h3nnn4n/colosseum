import itertools
import logging
from collections import defaultdict
from random import shuffle, uniform

import chess

from colosseum.utils import random_id

from .config import Config


logging.basicConfig(level=logging.WARNING)


# FIXME: We need to figure out what to call it. Probably should be ``game'',
# but the other game calls it ``World''.
class Game:
    def __init__(self):
        self.agents = set()

        self._config = Config()
        self.name = self._config.game_name
        self._board = chess.Board()

        logging.info("chess initialized")

    def register_agent(self, agent):
        if agent.id in self.agents:
            logging.warning(f"tried to register {agent.id} more than once")
            return

        self.agents.add(agent.id)

        logging.info(f"agent {agent.id} registered")

    @property
    def state(self):
        return {
            "fen": self._board.fen(),
            "epd": self._board.epd(),
            # "outcome": self._board.outcome(),
            "last_move_san": self._last_move_san,
            "last_move_lan": self._last_move_lan,
        }

    @property
    def _last_move(self):
        try:
            return self._board.peek()
        except IndexError:
            return None

    @property
    def _last_move_san(self):
        if self._last_move is None:
            return None
        return self._board.san(self._last_move)

    @property
    def _last_move_lan(self):
        if self._last_move is None:
            return None
        return self._board.lan(self._last_move)

    @property
    def _legal_moves(self):
        return self._board.legal_moves

    @property
    def config(self):
        return {"game_name": self._config.game_name}

    @property
    def scores(self):
        return {}

    def update(self, agent_actions):
        for agent_action in agent_actions:
            self.process_agent_actions(agent_action)

    def process_agent_actions(self, agent_action):
        pass
