#!/usr/bin/env python3

import json
import sys


def main():
    while True:
        data = sys.stdin.readline()

        state = json.loads(data)

        if state.get("die"):
            return

        state["out"] = state["x"] + state["y"]
        state["ping"] = "yes"

        print(json.dumps(state))


if __name__ == "__main__":
    main()
