#!/usr/bin/env python3

import argparse

from colosseum.tournament_online import online_tournament


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tournament matches from an API")
    parser.add_argument("--loop", action="store_true", help="Runs in a loop")
    args = vars(parser.parse_args())

    if not args.get("loop"):
        online_tournament()
    else:
        while True:
            try:
                online_tournament()
            except Exception:
                pass
