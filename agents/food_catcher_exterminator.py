#!/usr/bin/env python3

import logging

from sdks.python.colosseum_sdk import Agent


AGENT_NAME = "Exterminator"


class Exterminator(Agent):
    def __init__(self):
        super(Exterminator, self).__init__(agent_name=AGENT_NAME)


def main():
    exterminator = Exterminator()

    while exterminator.run:
        exterminator.read_state()
        exterminator.common_handlers()
        exterminator.send_commands()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
