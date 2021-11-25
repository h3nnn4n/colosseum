import itertools
import json
import os
import shutil
import tarfile
import urllib
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

from colosseum.games.food_catcher.game import World

from .match import match


load_dotenv()


API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get("API_TOKEN")
AGENT_FOLDER = f"agents_tmp_{uuid.uuid4()}"


class Participant:
    def __init__(self, id):
        # FIXME: Doing an (rest) api call during init might not be a good idea
        data = get_participant(id)
        self.id = id
        self.name = data["name"]
        self._file_hash = data["file_hash"]
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

        if not self._agent_path:
            for dirpath, subdirs, files in os.walk(base_path):
                for file in files:
                    # FIXME: We need to support other agent types
                    if file == "agent.py":
                        self._agent_path = os.path.join(dirpath, file)
                        self._agent_path = self._agent_path.replace(" ", "_")
                        print(f"found entrypoint at {self._agent_path}")

        if not self._agent_path:
            print(f"entrypoint not found for {self.name} / {self.id}")
        else:
            print(f"using cached agent path: {self._agent_path}")


class Game:
    def __init__(self, *args, match=None):
        self._players = args
        self._result = None
        self._replay_file = None
        self._result_by_player = {}
        self._match = match

    def set_results(self, result):
        self._result = result["scores"]
        self._replay_file = result["replay_file"]

        if self.n_players != 2:
            raise RuntimeError("only pairwise matches are supported at this point")

        if self.has_winner:
            winner = self._get_player_by_agent_path(self.rankings[0]["agent_path"])
            loser = self._get_player_by_agent_path(self.rankings[1]["agent_path"])
            self._register_match([winner, loser], 1)

        if self.is_draw:
            self._register_match(self._players, 0.5)

    def _register_match(self, participants, result):
        if self._match:
            payload = {
                "result": result,
                "ran": True,
                "participants": [p.id for p in participants],
                "player1": participants[0].id,
                "player2": participants[1].id,
            }
            response = requests.patch(
                API_URL + f"matches/{self._match['id']}/",
                json=payload,
                headers={"authorization": f"token {API_TOKEN}"},
            )
            if response.status_code > 400:
                print(
                    f"got error {response.status_code} when trying to update match: {response.body}"
                )
            upload_match_replay(self._match["id"], self._replay_file)
            return

        payload = {
            "participants": [p.id for p in participants],
            "result": result,
            "ran": True,
        }
        response = requests.post(
            API_URL + "matches/",
            json=payload,
            headers={"authorization": f"token {API_TOKEN}"},
        )

        if response.status_code > 400:
            print(
                f"got error {response.status_code} when trying to register match: {response.body}"
            )
        else:
            upload_match_replay(response.json()["id"], self._replay_file)

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
        print("\nstarting tournament\n")
        n_rounds = 1
        n_participants_per_round = 2

        for n_round in range(n_rounds):
            for agent_bracket in itertools.combinations(
                self.participants, n_participants_per_round
            ):
                print(f"running game with {list([a.name for a in agent_bracket])}")
                world = World()
                game = Game(*list(agent_bracket))
                game.set_results(match(world, [a.agent_path for a in agent_bracket]))


class MatchRunner:
    def __init__(self):
        pass

    @classmethod
    def run_next_match(cls):
        next_match = get_next_match()
        if not next_match.get("id"):
            # This is usually a failure on the producer side. We just do nothing
            return

        match_data = get_match(next_match["id"])

        participant_ids = match_data["participants"]
        participants = [
            Participant(participant_id) for participant_id in participant_ids
        ]

        world = World()
        game = Game(*participants, match=match_data)
        game.set_results(match(world, [a.agent_path for a in participants]))


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
    response = requests.post(
        API_URL + f"matches/{match_id}/upload_replay/",
        headers={"authorization": f"token {API_TOKEN}"},
        files={"file": open(replay_filename).read()},
    )
    if response.status_code > 400:
        print(
            f"got error {response.status_code} while trying to upload replay: {response.body}"
        )
    else:
        os.remove(replay_filename)


def get_tournament(tournament_id):
    print(f"fetching tournament {tournament_id}")
    response = requests.get(
        API_URL + f"tournaments/{tournament_id}/",
        headers={"authorization": f"token {API_TOKEN}"},
    )
    return json.loads(response.text)


def get_participant(participant_id):
    print(f"fetching agent {participant_id}/")
    response = requests.get(
        API_URL + f"agents/{participant_id}/",
        headers={"authorization": f"token {API_TOKEN}"},
    )
    return json.loads(response.text)


def online_tournament(tournament_id=None):
    if tournament_id:
        tournament = Tournament(tournament_id)
        tournament.run()
    else:
        while True:
            MatchRunner.run_next_match()
