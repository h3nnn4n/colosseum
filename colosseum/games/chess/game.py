import itertools
import logging
from collections import defaultdict
from random import choice, shuffle, uniform

import chess

from colosseum.utils import random_id

from .config import Config


# FIXME: We need to figure out what to call it. Probably should be ``game'',
# but the other game calls it ``World''.
class Game:
    def __init__(self):
        self.agents = set()
        self.agent_color = {}
        self.agent_by_color = {}
        self._colors_left = ["WHITE", "BLACK"]

        self._config = Config()
        self.name = self._config.game_name
        self._board = chess.Board()
        self._turn = "WHITE"

        logging.info("chess initialized")

    def register_agent(self, agent):
        if agent.id in self.agents:
            logging.warning(f"tried to register {agent.id} more than once")
            return

        # FIXME: Handle this gracefully
        assert len(self.agents) < 2

        self.agents.add(agent.id)
        agent_color = choice(self._colors_left)
        self._colors_left.remove(agent_color)
        self.agent_color[agent.id] = agent_color
        self.agent_by_color[agent_color] = agent.id

        logging.info(f"agent {agent.id} registered as {agent_color}")

    @property
    def state(self):
        legal_moves = [str(m) for m in self._legal_moves]
        return {
            "fen": self._board.fen(),
            "epd": self._board.epd(),
            "turn": self._board.turn,
            "legal_moves": legal_moves,
            "last_move": self._last_move_uci,
        }

    @property
    def outcome(self):
        outcome = self._board.outcome()
        if not outcome:
            return

        return {
            "termination": outcome.termination.__str__().split(".")[-1],
            "winner": outcome.winner,
            "result": outcome.result(),
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
    def _last_move_uci(self):
        if self._last_move is None:
            return None
        return self._board.uci(self._last_move)

    @property
    def _legal_moves(self):
        return self._board.legal_moves

    @property
    def config(self):
        return {
            "game_name": self._config.game_name,
            "update_mode": self._config.update_mode,
            "n_epochs": self._config.n_epochs,
        }

    @property
    def scores(self):
        data = {}

        result = self._board.outcome().result()
        white, black = result.split("-")

        try:
            white = int(white)
            black = int(black)
        except ValueError:
            white = 0.5
            black = 0.5

        for agent_id in self.agents:
            if self.agent_color[agent_id] == "WHITE":
                data[agent_id] = white
            else:
                data[agent_id] = black

        return data

    def update(self, agent_actions):
        for agent_action in agent_actions:
            self.process_agent_actions(agent_action)

        if self._turn == "WHITE":
            self._turn = "BLACK"
        else:
            self._turn = "WHITE"

    @property
    def finished(self):
        if self._board.outcome():
            return True
        return False

    @property
    def agent_to_move(self):
        return self.agent_by_color[self._turn]

    def process_agent_actions(self, agent_action):
        move_str = agent_action.get("move")
        # FIXME: We should handle this gracefully
        assert move_str

        move = chess.Move.from_uci(move_str)
        # FIXME: We should handle this gracefully
        assert move in self._legal_moves
        self._board.push(move)

    def assign_agent_colors(self):
        assert len(self.agents) == 2
