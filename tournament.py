#!/usr/bin/env python3

import sys

from colosseum.tournament import tournament


def main():
    agent_paths = sys.argv[1:]

    tournament(agent_paths)


if __name__ == "__main__":
    main()
