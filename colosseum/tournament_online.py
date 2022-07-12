import itertools
import json
import logging
import lzma
import os
import random
import shutil
import tarfile
import urllib
import uuid
from enum import Enum
from pathlib import Path
from time import sleep, time

import requests
from decouple import config
from dotenv import load_dotenv

from colosseum.games.cherry_picker.game import Game as CherryPickerGame
from colosseum.games.chess.game import Game as ChessGame
from colosseum.games.food_catcher.game import World as FoodCatcherGame
from colosseum.utils import get_internal_id

from .agent import Agent
from .match import run_match


load_dotenv()


API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get("API_TOKEN")
USE_DOCKER = config("USE_DOCKER", default=False, cast=bool)
AGENT_FOLDER = "agents_tmp"


class Participant:
    def __init__(self, id):
        data = get_participant(id)
        self.id = id
        self.name = data["name"]
        self._file_hash = data["file_hash"]
        self._ran = False
        self._agent_path = None
        self._download_url = data["file"]

        self.agent_path

    @property
    def agent_path(self):
        if self._ran:
            return self._agent_path

        self._ran = True
        base_path = os.path.join(AGENT_FOLDER, self.name, self._file_hash)
        base_path = base_path.replace(" ", "_")
        if not os.path.exists(base_path):
            Path(base_path).mkdir(parents=True, exist_ok=True)

            original_name = urllib.parse.urlparse(self._download_url).path.split("/")[
                -1
            ]
            agent_file = os.path.join(base_path, original_name)

            print(f"downloading agent into {agent_file}")
            urllib.request.urlretrieve(self._download_url, agent_file)

            # FIXME: Detect file format
            file = tarfile.open(agent_file)
            file.extractall(base_path)
            file.close()

        agent_path_python = None
        agent_path_docker = None

        if not self._agent_path:
            for dirpath, subdirs, files in os.walk(base_path):
                for file in files:
                    if file == "Dockerfile" and USE_DOCKER:
                        agent_path_docker = os.path.join(dirpath, file)
                        agent_path_docker = agent_path_docker.replace(" ", "_")
                        print(f"found DOCKER entrypoint at {agent_path_docker}")

                    if file == "agent.py" and not self._agent_path:
                        agent_path_python = os.path.join(dirpath, file)
                        agent_path_python = agent_path_python.replace(" ", "_")
                        print(f'found "agent.py" entrypoint at {agent_path_python}')

        if USE_DOCKER:
            if agent_path_docker:
                print("using DOCKER agent_path")
                self._agent_path = agent_path_docker
                push_agent_type_metrics("docker")
            else:
                print("USE_DOCKER is set but not docker agent was found!")

                if agent_path_python:
                    print("falling back to python agent")
                    self._agent_path = agent_path_python
                    push_agent_type_metrics("python")
                else:
                    print("no fallback agent was found! Panicking!!!")
                    raise RuntimeError(f"No agent was found for {base_path}")
        else:
            if agent_path_python:
                print("using PYTHON agent_path")
                self._agent_path = agent_path_python
                push_agent_type_metrics("python")
            else:
                print("no PYTHON agent_path was found! Panicking!!!")
                push_agent_type_metrics("not_found")
                raise RuntimeError(f"No agent was found for {base_path}")

        if not self._agent_path:
            print(f"entrypoint not found for {self.name} / {self.id}")
        else:
            print(f"using cached agent path: {self._agent_path}")


class GameRunner:
    def __init__(self, *args, match=None):
        self._players = args
        self._result = None
        self._raw_result = None
        self._replay_file = None
        self._result_by_player = {}
        self._match = match
        self._start_time = time()

    def set_results(self, result):
        self._raw_result = result
        self._result = result["scores"]
        self._replay_file = result["replay_file"]
        has_tainted_agent = result["has_tainted_agent"]
        outcome = result["outcome"]

        if has_tainted_agent:
            end_reason = "TAINTED"
        else:
            end_reason = "RULES"

        if self.n_players != 2:
            raise RuntimeError("only pairwise matches are supported at this point")

        if self.has_winner:
            winner = self._get_player_by_agent_path(self.rankings[0]["agent_path"])
            loser = self._get_player_by_agent_path(self.rankings[1]["agent_path"])
            self._register_match([winner, loser], 1, outcome, end_reason, result)

        if self.is_draw:
            self._register_match(self._players, 0.5, outcome, end_reason, result)

    def _register_match(self, participants, result, outcome, end_reason, raw_result):
        _end_time = time()
        duration = _end_time - self._start_time
        payload = {
            "errors": self._error_payload(self._raw_result),
            "result": result,
            "ran": True,
            "player1": participants[0].id,
            "player2": participants[1].id,
            "duration": duration,
            "end_reason": end_reason,
            "outcome": outcome,
            "raw_result": raw_result,
        }
        response = requests.patch(
            API_URL + f"matches/{self._match['id']}/",
            json=payload,
            headers={"authorization": f"token {API_TOKEN}"},
        )

        if response.status_code >= 400:
            print(
                f"got error {response.status_code} when trying to update match: {response.text}"
            )
        else:
            upload_match_replay(self._match["id"], self._replay_file)

    @property
    def players(self):
        return self._players

    @property
    def n_players(self):
        return len(self.players)

    @property
    def rankings(self):
        return sorted(self._result, key=lambda x: x["score"], reverse=True)

    @property
    def is_draw(self):
        return self.rankings[0]["score"] == self.rankings[1]["score"]

    @property
    def has_winner(self):
        return self.rankings[0]["score"] > self.rankings[1]["score"]

    @property
    def winner(self):
        return self._get_player_by_agent_path(self.rankings[0]["agent_path"])

    def _get_player_by_agent_path(self, agent_path):
        for player in self._players:
            if player.agent_path == agent_path:
                return player

    def _error_payload(self, raw_results):
        payload = {}
        for score in raw_results["scores"]:
            payload[score["agent_id"]] = {"error": score.get("tainted", False)}
        return payload


class MatchRunner:
    @classmethod
    def run_next_match(cls, game=None):
        print(f"{USE_DOCKER=}")
        send_heartbeat()
        next_match = get_next_match()
        if not next_match.get("id"):
            # This is usually a failure on the producer side, or there are no
            # matches left to play. We sleep for ~1 second and check again if
            # there is a new match to be played.
            sleep(random.uniform(0.9, 1.1))
            return

        match_data = get_match(next_match["id"])

        game_name = match_data["game"]["name"]

        if game and game_name != game:
            # HACK: This is dumb, because we are taking thinks out of the queue
            # and throwing it away. If we ever wanna super high throuput for a
            # particular game it can basically prevent other games from running
            print(f"skipping match {game_name}:{match_data['id']}. Only playing {game}")
            return

        if game_name == "food_catcher":
            game = FoodCatcherGame()
        elif game_name == "cherry_picker":
            game = CherryPickerGame()
        elif game_name == "chess":
            game = ChessGame()
        else:
            raise ValueError(f"{game_name} is not a supported game!")

        participant_ids = match_data["participants"]
        participants = [
            Participant(participant_id) for participant_id in participant_ids
        ]

        agents = [
            Agent(p.agent_path, id=p.id, time_config=game.initial_config)
            for p in participants
        ]

        game_runner = GameRunner(*participants, match=match_data)
        game_runner.set_results(run_match(game, agents=agents))


def get_next_match():
    print("fetching next match")
    response = requests.get(
        API_URL + "next_match/", headers={"authorization": f"token {API_TOKEN}"}
    )
    return json.loads(response.text)


def get_match(match_id):
    print(f"fetching match {match_id}")
    response = requests.get(
        API_URL + f"matches/{match_id}/",
        headers={"authorization": f"token {API_TOKEN}"},
    )
    return json.loads(response.text)


def upload_match_replay(match_id, replay_filename):
    print(f"uploading match replay {match_id} {replay_filename}")

    with open(replay_filename) as f:
        data = lzma.compress(f.read().encode())

    response = requests.post(
        API_URL + f"matches/{match_id}/upload_replay/",
        headers={"authorization": f"token {API_TOKEN}"},
        files={"file": data},
    )
    if response.status_code >= 400:
        print(
            f"got error {response.status_code} while trying to upload replay: {response.text}"
        )
    else:
        os.remove(replay_filename)


def push_agent_type_metrics(agent_type):
    _push_metric(
        name="agent_type",
        values={"value": 1},
        tags={
            "source": "colosseum_worker",
            "agent_type": agent_type,
            "use_docker": USE_DOCKER,
        },
    )


def _push_metric(name, values, tags):
    payload = {
        "measurement": name,
        "fields": values,
        "tags": tags,
    }

    print(f"pushing metrics {payload=}")

    requests.post(
        API_URL + "metrics/",
        headers={"authorization": f"token {API_TOKEN}"},
        json=payload,
    )


def get_participant(participant_id):
    print(f"fetching agent {participant_id}/")
    response = requests.get(
        API_URL + f"agents/{participant_id}/",
        headers={"authorization": f"token {API_TOKEN}"},
    )
    return json.loads(response.text)


def send_heartbeat():
    print("sending heartbeat")
    requests.post(
        API_URL + "colosseum_heartbeat/",
        headers={"authorization": f"token {API_TOKEN}"},
    )
    _push_metric(
        name="heartbeat",
        values={"value": 1},
        tags={
            "source": "colosseum_worker",
            "use_docker": USE_DOCKER,
        },
    )


def online_tournament(**kwargs):
    logging.basicConfig(
        filename=f"online_tournament_{get_internal_id()}.log", level=logging.INFO
    )
    MatchRunner.run_next_match(**kwargs)
