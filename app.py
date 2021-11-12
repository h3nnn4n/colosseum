#!/usr/bin/env python3

import sys

from colosseum.manager import Manager


def main():
    agent_paths = sys.argv[1:]
    manager = Manager(agent_paths)
    manager.start()
    manager.test()
    manager.stop()


if __name__ == "__main__":
    main()
