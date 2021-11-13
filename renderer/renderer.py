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
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)

        # FIXME: This should be read from the replay file
        self._scale = np.array(self.size) / np.array([10, 10])

        # Update the game state 10 times per second
        self.tick_duration = 1.0 / 10.0
        self._target_frame_duration = 1.0 / 60.0

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

        self.clock.tick()
        self._advance_tick()

        self.screen.fill(colors["white"])

        world_state = self.data["world_state"]
        foods = world_state["foods"]
        actors = world_state["actors"]
        bases = world_state["bases"]

        # FIXME: Each agent should have its own color
        for base in bases:
            position = np.array(base["position"]) * self._scale
            pygame.draw.circle(self.screen, colors["seagreen3"], position, 9, 0)

        for actor in actors:
            position = np.array(actor["position"]) * self._scale
            pygame.draw.circle(self.screen, colors["turquoise3"], position, 9, 0)

        for food in foods:
            position = np.array(food["position"]) * self._scale
            pygame.draw.circle(self.screen, colors["maroon2"], position, 9, 0)

        now = time()
        diff = self._target_frame_duration - (now - self._frame_timer)
        if diff < self._target_frame_duration and diff > 0:
            sleep(diff)

        self._text(f"fps: {self.clock.get_fps():6.2f}", (10, 10))
        self._text(f"     {diff:.4f} (ms)", (10, 30))
        self._frame_timer = time()

        pygame.display.flip()

    def _text(self, text, position, antialias=True, color=(220, 230, 225)):
        text_surface = self.font.render(text, antialias, color)
        self.screen.blit(text_surface, dest=position)
