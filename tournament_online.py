#!/usr/bin/env python3

import sys

from colosseum.tournament_online import online_tournament


if __name__ == "__main__":
    tournament_id = sys.argv[1]
    online_tournament(tournament_id)
