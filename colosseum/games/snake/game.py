import itertools
import logging
from collections import defaultdict
from enum import Enum
from random import choice, randint, shuffle, uniform

import chess

from colosseum.utils import random_id

from ..game import BaseGame
from .config import Config


class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    @classmethod
    def from_string(cls, string):
        match string.lower():
            case "up":
                return Direction.UP
            case "right":
                return Direction.RIGHT
            case "down":
                return Direction.DOWN
            case "left":
                return Direction.LEFT


class Game(BaseGame):
    def __init__(self):
        self.agents = set()
        self.agent_ids = set()

        self._config = Config
        self.name = self._config.game_name
        self.grid_width = self._config.grid_width
        self.grid_height = self._config.grid_height

        self.snakes = []
        self.snakes_by_id = {}
        self.foods = []

        self._tick = 0

        logging.info("snake initialized")

    def register_agent(self, agent):
        super().register_agent(agent)

        snake = self._spawn_snake(agent.id)
        self.snakes.append(snake)
        self.snakes_by_id[agent.id] = snake

    @property
    def state(self):
        return {
            "foods": self._food_state,
            "grid": self._grid_state,
        }

    @property
    def _food_state(self):
        # TODO
        return []

    @property
    def _grid_state(self):
        base_grid = []
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                row.append(Cell())

            base_grid.append(row)

        for snake in self.snakes:
            while True:
                x, y = snake.position
                base_grid[x][y].occupy(snake)
                snake = snake.next_cell

                if not snake:
                    break

        return ["".join([cell.to_string for cell in row]) for row in base_grid]

    @property
    def outcome(self):
        outcome = {"termination": "GAME_ENDED"}

        if self.has_tainted_agent:
            outcome["termination"] = "TAINTED"
            outcome["tainted_reason"] = self.tainted_agents[0].tainted_reason

        return outcome

    @property
    def scores(self):
        return {
            # foo
        }

    @property
    def finished(self):
        return self._tick >= self._config.n_epochs

    def update(self, agent_actions):
        self._tick += 1

        for agent_action in agent_actions:
            self._process_agent_action(agent_action)

        self._update_foods()

    def _process_agent_action(self, agent_action):
        owner_id = agent_action.get("agent_id")
        if owner_id not in self.agent_ids:
            logging.warning(f"agent with id {owner_id} is not registered. Ignoring")
            return

        move_direction = Direction.from_string(agent_action.get("move"))
        snake = self.snakes_by_id[owner_id]
        snake.update(move_direction)

    def _update_foods(self):
        if len(self.foods) < self._config.min_food_sources:
            # Spawn
            pass

    def _spawn_snake(self, agent_id):
        # TODO: We should make sure we do not generate invalid
        # starting positions, like OOB, instant game over, overlapping
        # with itself or other snakes, over obstacles or food.
        starting_position = Vector(
            randint(0, self.grid_width - 1), randint(0, self.grid_height - 1)
        )
        tail_position = starting_position.clone()
        tail_position.x -= 1
        snake = Snake(agent_id, position=starting_position, head=True)
        snake_tail = Snake(agent_id, position=tail_position)
        snake_tail.size = 1

        snake.next_cell = snake_tail
        snake.next_cell_direction = Direction.LEFT

        return snake


class Snake:
    def __init__(self, agent_id, position=None, head=False):
        self.agent_id = agent_id
        self.size = 2
        # FIXME: We need a proper API
        self.next_cell_direction = None
        self.next_cell = None
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
            self.next_cell._update(direction)


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def clone(self):
        return Vector(self.x, self.y)

    def __iter__(self):
        return iter([self.x, self.y])


class Cell:
    def __init__(self):
        self.occupied_by = []

    def occupy(self, thing):
        self.occupied_by.append(thing)

    @property
    def occupied(self):
        return bool(self.occupied_by)

    @property
    def occupied_count(self):
        return len(self.occupied_by)

    @property
    def to_string(self):
        if not self.occupied:
            return " "

        if self.occupied_count > 1:
            return "X"

        occupee = self.occupied_by[0]

        if occupee.is_head:
            return "C"

        match occupee.next_cell_direction:
            case Direction.DOWN:
                return "V"
            case Direction.UP:
                return "^"
            case Direction.RIGHT:
                return ">"
            case Direction.LEFT:
                return "<"

        return "S"
