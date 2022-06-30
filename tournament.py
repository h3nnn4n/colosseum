#!/usr/bin/env python3

import argparse

from colosseum.tournament import tournament


def main(game, agent_paths, mode):
    if len(agent_paths) == 0:
        raise ValueError("No agents were provided")

    print(f"GAME: {game}")
    print(f"MODE: {mode}")

    print("agents:")
    for participant in agent_paths:
        print(f" -> {participant}")
    print()

    result = tournament(game, agent_paths, mode)

    for ranking, participant in result.rankings.items():
        print(
            f"{ranking:2d}: {participant.score:5.1f} {participant.elo:4d} {participant.pretty_name:<40}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tournament locally with agents")
    parser.add_argument(
        "--game",
        action="store",
        help="Specify a particular game to be ran",
        required=True,
    )
    parser.add_argument(
        "--mode",
        action="store",
        default="ROUND_ROBIN",
        help="Tournament mode. Options are ROUND_ROBIN, DOUBLE_ROUND_ROBIN and TRIPLE_ROUND_ROBIN. Default is ROUND_ROBIN",
    )
    parser.add_argument("agent_paths", nargs=argparse.REMAINDER)
    kwargs = vars(parser.parse_args())

    main(**kwargs)
