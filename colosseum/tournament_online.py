import itertools
import json
import os
import shutil
import urllib
from pathlib import Path

import requests
from dotenv import load_dotenv

from colosseum.games.food_catcher.game import World

from .match import match


load_dotenv()


API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get("API_TOKEN")
AGENT_FOLDER = "agents_tmp"


class Participant:
    def __init__(self, id):
        # FIXME: Doing an (rest) api call during init might not be a good idea
        data = get_participant(id)
        self.id = id
        self.name = data["name"]
        self._ran = False
        self._agent_path = None
        self._download_url = data["file"]

        self.wins = data["wins"]
        self.loses = data["loses"]
        self.draws = data["draws"]
        self.score = data["score"]
        self.elo = data["elo"]
        self.agent_path

    @property
    def agent_path(self):
        if self._ran:
            return self._agent_path

        self._ran = True
        base_path = os.path.join(AGENT_FOLDER, self.name)
        if os.path.exists(base_path):
            shutil.rmtree(base_path)

        Path(base_path).mkdir(parents=True, exist_ok=True)

        original_name = urllib.parse.urlparse(self._download_url).path.split("/")[-1]
        self._agent_path = os.path.join(base_path, original_name)

        print(f"downloading agent into {self._agent_path}")
        urllib.request.urlretrieve(self._download_url, self._agent_path)


class Game:
    def __init__(self, *args):
        self.players = args
        self.result = None
        self.result_by_player = {}

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


class Tournament:
    def __init__(self, id):
        data = get_tournament(id)
        self.id = id
        self.mode = "ROUND_ROBIN"
        self.participant_ids = data["participants"]
        self.participants = [
            Participant(participant_id) for participant_id in self.participant_ids
        ]

    def run(self):
        n_rounds = 1
        n_participants_per_round = 2

        for n_round in range(n_rounds):
            for agent_bracket in itertools.combinations(
                self.participants, n_participants_per_round
            ):
                world = World()
                game = Game(*list(agent_bracket))
                game.result(match(world, [a.agent_path for a in agent_bracket]))


def get_tournament(tournament_id):
    print("fetching tournament")
    response = requests.get(
        API_URL + f"tournaments/{tournament_id}",
        headers={"authorization": f"token {API_TOKEN}"},
    )
    return json.loads(response.text)


def get_participant(participant_id):
    print(f"fetching agent {participant_id}")
    response = requests.get(
        API_URL + f"agents/{participant_id}",
        headers={"authorization": f"token {API_TOKEN}"},
    )
    return json.loads(response.text)


def online_tournament(tournament_id):
    tournament = Tournament(tournament_id)
    tournament.run()
