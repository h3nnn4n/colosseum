#!/usr/bin/env python3

import sys
from time import sleep, time

import numpy as np
import pygame
from pygame.colordict import THECOLORS as colors


class Renderer:
    def __init__(self):
        pygame.init()
        self.size = 800, 600
        self.screen = pygame.display.set_mode(self.size)
        self._data = None
        self._current_tick = None

        # FIXME: This should be read from the replay file
        self._scale = np.array(self.size) / np.array([10, 10])

        # Update the game state 10 times per second
        self.tick_duration = 1.0 / 10.0

        self._frame_timer = time()
        self._tick_timer = time()

    def set_data(self, data):
        self._data = data
        self._current_tick = 0

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

        self._advance_tick()

        self.screen.fill(colors["white"])

        world_state = self.data["world_state"]
        foods = world_state["food_positions"]
        actors = world_state["actors"]
        all_bases = world_state["agent_bases"]

        # FIXME: Each agent should have its own color
        for agent_id, bases in all_bases.items():
            for base in bases:
                position = np.array(base["position"]) * self._scale
                pygame.draw.circle(self.screen, colors["seagreen3"], position, 9, 0)

        for actor in actors:
            position = np.array(actor["position"]) * self._scale
            pygame.draw.circle(self.screen, colors["turquoise3"], position, 9, 0)

        for food in foods:
            position = np.array(food["position"]) * self._scale
            pygame.draw.circle(self.screen, colors["maroon2"], position, 9, 0)

        pygame.display.flip()

        now = time()
        diff = now - self._frame_timer
        if diff < (1.0 / 60.0):
            sleep(diff)
        self._frame_timer = time()
