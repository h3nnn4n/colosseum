#!/usr/bin/env python3

import sys

from colosseum.tournament_online import online_tournament


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tournament_id = sys.argv[1]
        online_tournament(tournament_id)
    else:
        online_tournament()
