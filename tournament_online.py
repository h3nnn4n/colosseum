#!/usr/bin/env python3

import argparse

from colosseum.tournament_online import online_tournament


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tournament matches from an API")
    parser.add_argument("--loop", action="store_true", help="Runs in a loop")
    parser.add_argument(
        "--game", action="store", help="Specify a particular game to be ran"
    )
    kwargs = vars(parser.parse_args())

    loop = kwargs.pop("loop")

    if loop:
        while True:
            try:
                online_tournament(**kwargs)
            except Exception as e:
                print(f"tournament failed with: {e}")
    else:
        online_tournament(**kwargs)
