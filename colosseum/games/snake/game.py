import itertools
import logging
from collections import defaultdict
from enum import Enum
from random import choice, shuffle, uniform

import chess

from colosseum.utils import random_id

from ..game import BaseGame
from .config import Config


class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Game(BaseGame):
    def __init__(self):
        self.agents = set()
        self.agent_ids = set()

        self._config = Config
        self.name = self._config.game_name
        self.snakes = []
        self.snakes_by_id = []

        self.foods = []

        logging.info("snake initialized")

    def register(self, agent_id):
        super().register_agent(agent_id)

        snake = Snake(agent_id)
        self.snakes.append(snake)
        self.snakes_by_id[agent_id] = snake

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

        self._update_foods()

    def _process_agent_actions(self, agent_action):
        pass

    def _update_foods(self):
        if len(self.foods) < self._config.min_food_sources:
            # Spawn
            pass


class Snake:
    def __init__(self, agent_id, position=None, head=False):
        self.agent_id = agent_id
        self.size = 2
        # FIXME: Should be based on spawn position
        self.next_cell_direction = Direction.DOWN
        self.is_head = head
        self.position = position

    def update(self, direction):
        if not self.is_head:
            raise TypeError("update can only be called at the snake's head")

        self._update(direction)

    def _update(self, direction):
        match direction:
            case Direction.UP:
                self.position.y -= 1
                self.next_cell_direction = Direction.DOWN
            case Direction.RIGHT:
                self.position.x += 1
                self.next_cell_direction = Direction.LEFT
            case Direction.DOWN:
                self.position.y += 1
                self.next_cell_direction = Direction.UP
            case Direction.LEFT:
                self.position.x -= 1
                self.next_cell_direction = Direction.RIGHT

        if self.size > 1:
            self.next_cell._update()


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
