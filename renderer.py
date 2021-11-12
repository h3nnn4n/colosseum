import json
import sys

from renderer.renderer import Renderer


def main():
    filename = sys.argv[1]

    with open(filename, "rt") as f:
        data = [json.loads(line) for line in f.readlines()]

    renderer = Renderer()
    renderer.set_data(data)

    while True:
        renderer.update()


if __name__ == "__main__":
    main()
