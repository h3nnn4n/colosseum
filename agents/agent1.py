#!/usr/bin/env python3

import json
import sys


def main():
    while True:
        data = sys.stdin.readline()

        state = json.loads(data)

        if state.get("die"):
            return

        if state.get("ping"):
            print('{"pong": "foobar"}')


if __name__ == "__main__":
    main()
