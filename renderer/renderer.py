#!/usr/bin/env python3

import itertools
import sys
from time import sleep, time

import numpy as np
import pygame
from pygame.colordict import THECOLORS as colors


def load_image(name):
    image = pygame.image.load(name).convert_alpha()
    return image


def get_food_sprite():
    image = load_image("./sprites/food.png")
    image = pygame.transform.scale(image, (20, 30))
    return image


def get_base_sprite():
    image = load_image("./sprites/base.png")
    image = pygame.transform.scale(image, (20, 20))
    return image


def get_actor_sprite():
    image = load_image("./sprites/actor.png")
    image = pygame.transform.scale(image, (20, 20))
    return image


class Renderer:
    def __init__(self):
        pygame.init()
        self.size = 600 * 1.5, 600 * 1.5
        self.screen = pygame.display.set_mode(self.size)
        self._data = None
        self._current_tick = None
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)

        self.food_sprite = get_food_sprite()
        self.actor_sprite = get_actor_sprite()
        self.base_sprite = get_base_sprite()

        # FIXME: This should be read from the replay file
        self._scale = np.array(self.size) / np.array([40, 40])

        # Update the game state 30 times per second
        self.tick_duration = 1.0 / 30.0
        self._target_frame_duration = 1.0 / 60.0

        self._frame_timer = time()
        self._tick_timer = time()

        self.color_map = {}

        self.agent_colors = [
            colors["cadetblue"],
            colors["mediumorchid3"],
            colors["yellow3"],
            colors["darkolivegreen3"],
        ]

    def set_data(self, data):
        self._data = data
        self._current_tick = 0

        first_data = data[0]
        bases = first_data["world_state"]["bases"]
        agent_ids = [base["owner_id"] for base in bases]

        for index, agent_id in enumerate(agent_ids):
            self.color_map[agent_id] = self.agent_colors[index]

    def _advance_tick(self):
        now = time()
        if now - self._tick_timer < self.tick_duration:
            return

        self._tick_timer = now

        self._current_tick += 1
        if self._current_tick >= len(self._data):
            self._current_tick = 0

    @property
    def data(self):
        return self._data[self._current_tick]

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        self.clock.tick()
        self._advance_tick()

        self.screen.fill(colors["white"])

        world_state = self.data["world_state"]
        actions = list(
            itertools.chain.from_iterable(
                [x["actions"] for x in self.data["agent_actions"]]
            )
        )
        foods = world_state["foods"]
        actors = world_state["actors"]
        bases = world_state["bases"]

        # FIXME: Each agent should have its own color
        for base in bases:
            self._draw_base(base)

        for actor in actors:
            position = np.array(actor["position"]) * self._scale
            self._draw_actor(position, actor["owner_id"])

            for action in actions:
                if action.get("actor_id") == actor["id"]:
                    if action["action"] == "move":
                        pygame.draw.line(
                            self.screen,
                            colors["gray"],
                            np.array(actor["position"]) * self._scale,
                            np.array(action["target"]) * self._scale,
                            2,
                        )
                    if action["action"] == "attack":
                        pygame.draw.line(
                            self.screen,
                            colors["red"],
                            np.array(actor["position"]) * self._scale,
                            np.array(self._get_object_position(action["target"]))
                            * self._scale,
                            4,
                        )

        for food in foods:
            position = np.array(food["position"]) * self._scale
            self._draw_food(position)

        now = time()
        diff = self._target_frame_duration - (now - self._frame_timer)
        if diff < self._target_frame_duration and diff > 0:
            sleep(diff)

        self._text(f"fps: {self.clock.get_fps():6.2f}", (10, 10))
        self._text(f"     {diff:.4f} (ms)", (10, 30))
        self._frame_timer = time()

        pygame.display.flip()

    def _get_object_position(self, object_id):
        objects = [
            self.data["world_state"]["foods"],
            self.data["world_state"]["actors"],
            self.data["world_state"]["bases"],
        ]

        for obj in itertools.chain.from_iterable(objects):
            if obj["id"] == object_id:
                return obj["position"]

    def _text(self, text, position, antialias=True, color=(220, 230, 225)):
        text_surface = self.font.render(text, antialias, color)
        self.screen.blit(text_surface, dest=position)

    def _draw_actor(self, position, owner_id):
        color = self.color_map[owner_id]
        pygame.draw.circle(self.screen, color, position, 14, 0)
        self.screen.blit(self.actor_sprite, position + np.array([-10, -10]))

    def _draw_base(self, base):
        position = np.array(base["position"]) * self._scale
        color = self.color_map[base["owner_id"]]
        pygame.draw.circle(self.screen, color, position, 14, 0)
        self.screen.blit(self.base_sprite, position + np.array([-10, -10]))

        self._text(
            f"food: {base['food']:.1f}",
            position + np.array([-7, -22]),
            color=colors["brown3"],
        )

    def _draw_food(self, position):
        self.screen.blit(self.food_sprite, position + np.array([-10, -25]))
