#!/usr/bin/env python3

import argparse
import json
import logging
import sys

from colosseum.games.cherry_picker.game import Game as CherryPickerGame
from colosseum.games.chess.game import Game as ChessGame
from colosseum.games.food_catcher.game import World
from colosseum.match import match
from colosseum.utils import get_internal_id


parser = argparse.ArgumentParser(
    description="Play a one-off match between local agents, without persisting any results."
)
parser.add_argument("--game", required=True, type=str)
parser.add_argument("--agent", action="append", required=True, type=str)


def main(game_name, agent_paths):
    logging.basicConfig(
        filename=f"skirmish_{get_internal_id()}.log", level=logging.INFO
    )

    if game_name == "chess":
        game = ChessGame()
    elif game_name == "cherry_picker":
        game = CherryPickerGame()
    elif game_name == "food_catcher":
        game = World()
    else:
        raise ValueError(f"{game_name} is not a valid game")

    scores = match(game, agent_paths=agent_paths)

    print(json.dumps(scores))


if __name__ == "__main__":
    config = vars(parser.parse_args())
    main(game_name=config["game"], agent_paths=config["agent"])
