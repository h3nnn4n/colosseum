#!/usr/bin/env python3

import itertools
from collections import defaultdict
from pathlib import Path

from colosseum.games.food_catcher.game import World

from .match import match


def tournament(agents):
    results = defaultdict(list)

    for agent_bracket in itertools.combinations(agents, 2):
        print(f"{Path(agent_bracket[0]).stem} vs {Path(agent_bracket[1]).stem}")

        world = World()
        scores = match(world, agent_bracket)
        key = "_agents".join(agent_bracket)

        print(
            f"result: {scores[0]['name']} with {scores[0]['score']:.2f} to {scores[1]['score']:.2f}"
        )
        print()

        results[key].append(scores)

    return results
