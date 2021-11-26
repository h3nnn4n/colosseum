#!/usr/bin/env python3

import json
import logging
import sys

from colosseum.games.food_catcher.game import World
from colosseum.match import match
from colosseum.utils import get_internal_id


def main():
    agent_paths = sys.argv[1:]

    logging.basicConfig(filename=f"match_{get_internal_id()}.log", level=logging.INFO)

    world = World()
    scores = match(world, agent_paths=agent_paths)

    print(json.dumps(scores))


if __name__ == "__main__":
    main()
