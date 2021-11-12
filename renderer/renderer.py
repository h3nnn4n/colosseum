#!/usr/bin/env python3

import sys

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

    def set_data(self, data):
        self._data = data
        self._current_tick = 0

    def advance_tick(self):
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

        self.screen.fill(colors["white"])

        world_state = self.data["world_state"]
        foods = world_state["food_positions"]
        all_agents = world_state["agent_positions"]
        all_bases = world_state["agent_bases"]

        # FIXME: Each agent should have its own color
        for agent_id, bases in all_bases.items():
            for base in bases:
                position = np.array(base["position"]) * self._scale
                pygame.draw.circle(self.screen, colors["seagreen3"], position, 9, 0)

        for agent_id, agents in all_agents.items():
            for agent in agents:
                position = np.array(agent["position"]) * self._scale
                pygame.draw.circle(self.screen, colors["turquoise3"], position, 9, 0)

        for food in foods:
            position = np.array(food["position"]) * self._scale
            pygame.draw.circle(self.screen, colors["maroon2"], position, 9, 0)

        pygame.display.flip()
