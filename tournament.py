#!/usr/bin/env python3

import sys

from colosseum.tournament import tournament


def main():
    agent_paths = sys.argv[1:]

    result = tournament(agent_paths, "ROUND_ROBIN")

    for ranking, participant in result.rankings.items():
        print(
            f"{ranking:2d}: {participant.score:5.1f} {participant.elo:4d} {participant.pretty_name:<40}"
        )


if __name__ == "__main__":
    main()
