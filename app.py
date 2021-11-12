#!/usr/bin/env python3

import logging
import sys

from colosseum.games.food_catcher.world import World
from colosseum.manager import Manager


def main():
    agent_paths = sys.argv[1:]
    logging.basicConfig(level=logging.INFO)

    world = World()

    manager = Manager(world, agent_paths)
    manager.start()
    manager.ping()

    for epoch in range(10):
        manager.tick()

    manager.stop()


if __name__ == "__main__":
    main()
