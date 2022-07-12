#!/usr/bin/env python3

import argparse

from colosseum.tournament_online import _push_metric, online_tournament


def _handle_exception(exception):
    try:
        _push_metric(
            name="colosseum_worker_errors",
            values={"value": 1},
            tags={
                "source": "colosseum_worker",
                "error_class": exception.__class__.__name__,
            },
        )
    except Exception as e:
        print(
            f"failed to handle exception {exception} with the following exception: {e}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tournament matches from an API")
    parser.add_argument("--loop", action="store_true", help="Runs in a loop")
    parser.add_argument(
        "--game", action="store", help="Specify a particular game to be ran"
    )
    kwargs = vars(parser.parse_args())

    loop = kwargs.pop("loop")

    if loop:
        while True:
            try:
                online_tournament(**kwargs)
            except Exception as e:
                _handle_exception(e)
                print(f"tournament failed with: {e}")
    else:
        try:
            online_tournament(**kwargs)
        except Exception as e:
            _handle_exception(e)
            raise
