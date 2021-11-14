#!/usr/bin/env python3

import json
import sys

from utils import send_commands


AGENT_NAME = "dummy"


def main():
    agent_id = None
    while True:
        data = sys.stdin.readline()
        state = json.loads(data)
        response = {}

        if state.get("stop"):
            break

        if state.get("set_agent_id"):
            agent_id = state.get("set_agent_id")
            response["agent_name"] = AGENT_NAME

        if state.get("ping"):
            response["pong"] = "boofar"

        if agent_id:
            response["agent_id"] = agent_id

        send_commands(response)


if __name__ == "__main__":
    main()
