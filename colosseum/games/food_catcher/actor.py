import logging

import numpy as np

from colosseum.utils import object_distance, random_id

from .config import Config


class Actor:
    def __init__(self):
        self.position = None
        self.id = random_id()
        self.owner_id = None
        self.food = 0

        self.config = Config
        self.speed = self.config.actor_speed
        self.damage = self.config.actor_damage
        self.health = self.config.actor_max_health
        self.max_health = self.config.actor_max_health

    def set_owner(self, owner_id):
        self.owner_id = owner_id
        return self

    def set_position(self, position):
        self.position = position
        return self

    def add_food(self, food):
        self.food += food

    def take_food(self):
        food_taken = self.food
        self.food = 0
        return food_taken

    def deal_damage(self, damage):
        self.health -= damage

    def heal(self, amount):
        self.health += amount

    @property
    def missing_health(self):
        return self.max_health - self.health

    @property
    def alive(self):
        return self.health > 0

    @property
    def dead(self):
        return self.health <= 0

    def move(self, target):
        target = np.array(target)
        actor_position = np.array(self.position)
        move_direction = target - actor_position
        distance_to_target = np.linalg.norm(move_direction)
        distance_to_move = min(self.speed, distance_to_target)

        if distance_to_move > 1e-4:
            actor_position_new = actor_position + (
                move_direction / distance_to_target * distance_to_move
            )
            self.position = tuple(actor_position_new.tolist())
            logging.info(
                f"actor {self.id} moved from {actor_position} to {actor_position_new} with target {target} speed {distance_to_move}"
            )
            return

        logging.info(f"actor {self.id} {actor_position=} is already at {target=}")

    def kill(self):
        self.health = 0

    @property
    def state(self):
        return {
            "position": self.position,
            "id": self.id,
            "owner_id": self.owner_id,
            "food": self.food,
            "health": self.health,
            "max_health": self.max_health,
        }
