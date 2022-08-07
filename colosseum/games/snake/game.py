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

        self._update_food_spawning()

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
            "grid": self._grid_state_str,
            "snakes": self._snake_states,
        }

    @property
    def _snake_states(self):
        states = {}

        for snake in self.snakes:
            state = {}
            state["alive"] = snake.alive
            state["head_position"] = snake.position.as_list
            state["positions"] = [p.as_list for p in snake.positions]

            states[snake.agent_id] = state

        return states

    @property
    def _food_state(self):
        return [[x.position.x, x.position.y] for x in self.foods]

    @property
    def _grid_state(self):
        base_grid = []
        for _ in range(self.grid_width):
            row = []
            for _ in range(self.grid_height):
                row.append(Cell())

            base_grid.append(row)

        for snake in self.snakes:
            if snake.dead:
                continue

            while True:
                x, y = snake.position
                base_grid[x][y].occupy(snake)
                snake = snake.next_cell

                if not snake:
                    break

        for food in self.foods:
            x, y = food.position
            base_grid[x][y].occupy(food)

        return base_grid

    @property
    def _grid_state_str(self):
        rows = []

        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                row.append(self._grid_state[x][y].to_string)

            rows.append("".join(row))

        return rows

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
        return self._tick >= self._config.n_epochs or self._snake_alive_count == 0

    def update(self, agent_actions):
        self._tick += 1

        for agent_action in agent_actions:
            self._process_agent_action(agent_action)

        self._check_snake_bounds()
        self._update_collision()
        self._update_eaten_food()
        self._update_food_spawning()

    def _process_agent_action(self, agent_action):
        agent_id = agent_action.get("agent_id")
        if agent_id not in self.agent_ids:
            logging.warning(f"agent with id {agent_id} is not registered. Ignoring")
            return

        move_direction_str = agent_action.get("move")
        if not move_direction_str:
            logging.warning(f"got null move from {agent_action=} from {agent_id=}")
            return

        move_direction = Direction.from_string(move_direction_str)
        snake = self.snakes_by_id[agent_id]
        snake.update(move_direction)

    def _update_collision(self):
        grid = self._grid_state

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if grid[x][y].contains_multiple_snakes:
                    snakes = grid[x][y].occupying_snakes
                    logging.warning(f"found multiple snakes at cell {x=} {y=}")
                    for snake in snakes:
                        snake.die()

    def _update_food_spawning(self):
        if len(self.foods) >= self._config.min_food_sources:
            return

        grid = self._grid_state

        logging.info(f"spawing {self._config.food_sources_to_spawn - len(self.foods)} foods")
        for _ in range(self._config.food_sources_to_spawn - len(self.foods)):
            position = Vector(
                randint(0, self.grid_width - 1), randint(0, self.grid_height - 1)
            )

            # TODO: Ensure we spawn a food piece if there is an empty cell available
            if grid[position.x][position.y].empty:
                self.foods.append(Food(position))

    def _update_eaten_food(self):
        grid = self._grid_state

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if grid[x][y].contains_snake and grid[x][y].contains_food:
                    snake = grid[x][y].occupying_snakes[0]
                    food = grid[x][y].occupying_foods[0]

                    snake.eat()
                    food.eat()

        self.foods = [x for x in self.foods if not x.eaten]

    def _check_snake_bounds(self):
        for snake in self.snakes:
            if snake.dead:
                continue

            if snake.position.x < 0 or snake.position.x >= self.grid_width:
                snake.die()

            if snake.position.y < 0 or snake.position.y >= self.grid_height:
                snake.die()

    @property
    def _snake_alive_count(self):
        return len([snake for snake in self.snakes if snake.alive])

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
        self.alive = True
        self.grow = False

    @property
    def dead(self):
        return not self.alive

    def eat(self):
        if self.size > 1:
            self.next_cell.eat()
        else:
            self.grow = True

    def die(self):
        if self.next_cell:
            self.next_cell.die()

        self.alive = False

    def update(self, direction):
        if not self.is_head:
            raise TypeError("update can only be called at the snake's head")

        self._update(direction)

    def _update(self, direction, new_position=None):
        old_position = self.position.clone()

        match direction:
            case Direction.UP:
                self.next_cell_direction = Direction.DOWN
            case Direction.RIGHT:
                self.next_cell_direction = Direction.LEFT
            case Direction.DOWN:
                self.next_cell_direction = Direction.UP
            case Direction.LEFT:
                self.next_cell_direction = Direction.RIGHT

        if new_position is None:
            match direction:
                case Direction.UP:
                    self.position.y -= 1
                case Direction.RIGHT:
                    self.position.x += 1
                case Direction.DOWN:
                    self.position.y += 1
                case Direction.LEFT:
                    self.position.x -= 1
        else:
            self.position = new_position.clone()

        # This grow logic is a mini pile of goo
        if self.size > 1:
            self.next_cell._update(direction, new_position=old_position)
        elif self.grow:
            self.next_cell = Snake(self.agent_id, position=old_position)
            self.next_cell.size = 1
            self.size += 1
            self.grow = False

        if self.grow:
            self.size += 1

    @property
    def positions(self):
        p = [self.position]

        if self.size > 1:
            p.extend(self.next_cell.positions)

        return p


class Food:
    def __init__(self, position):
        self.position = position
        self.eaten = False

    def eat(self):
        self.eaten = True


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def clone(self):
        return Vector(self.x, self.y)

    def __iter__(self):
        return iter([self.x, self.y])

    @property
    def as_list(self):
        return [self.x, self.y]


class Cell:
    def __init__(self):
        self.occupied_by = []

    def occupy(self, thing):
        self.occupied_by.append(thing)

    @property
    def occupied(self):
        return bool(self.occupied_by)

    @property
    def empty(self):
        return not self.occupied

    @property
    def occupied_count(self):
        return len(self.occupied_by)

    @property
    def occupying_foods(self):
        return [x for x in self.occupied_by if isinstance(x, Food)]

    @property
    def contains_food(self):
        return len(self.occupying_foods) > 0

    @property
    def occupying_snakes(self):
        return [x for x in self.occupied_by if isinstance(x, Snake)]

    @property
    def contains_snake(self):
        return len(self.occupying_snakes) > 0

    @property
    def contains_multiple_snakes(self):
        return len(self.occupying_snakes) > 1

    @property
    def to_string(self):
        if not self.occupied:
            return " "

        if self.contains_food:
            return "@"

        if self.occupied_count > 1:
            return "X"

        occupee = self.occupied_by[0]

        if occupee.is_head:
            return "C"

        match occupee.next_cell_direction:
            case Direction.DOWN:
                return "^"
            case Direction.UP:
                return "V"
            case Direction.RIGHT:
                return "<"
            case Direction.LEFT:
                return ">"

        return "S"
