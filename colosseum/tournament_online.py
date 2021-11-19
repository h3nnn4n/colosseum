import json
import os

import requests
from dotenv import load_dotenv


load_dotenv()


API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get("API_TOKEN")


class Participant:
    def __init__(self, data):
        self.wins = 0
        self.loses = 0
        self.draws = 0
        self.score = 0
        self.elo = 0

    def win(self):
        self.wins += 1
        self.score += 1

    def lose(self):
        self.loses += 1

    def draws(self):
        self.draws += 0
        self.score += 0.5

    def _update_elo(self, elo):
        self.elo = elo


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


def make_participant(participant_id):
    data = get_participant(participant_id)
    return Participant(data)


def online_tournament(tournament_id):
    tournament = get_tournament(tournament_id)
    participant_ids = tournament["participants"]
    participants = [
        make_participant(participant_id) for participant_id in participant_ids
    ]
    __import__("pprint").pprint(tournament)

    for p in participants:
        __import__("pprint").pprint(p)
