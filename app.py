#!/usr/bin/env python3

import json
import logging
import sys

from colosseum.games.food_catcher.game import World
from colosseum.manager import Manager


def main():
    agent_paths = sys.argv[1:]
    logging.basicConfig(level=logging.INFO)

    world = World()

    manager = Manager(world, agent_paths)
    manager.start()
    manager.ping()

    for epoch in range(1000):
        manager.tick()

    manager.stop()

    scores = manager.scores

    print(json.dumps(scores))


if __name__ == "__main__":
    main()
