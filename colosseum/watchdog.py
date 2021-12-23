import os
from time import sleep

import requests
from dotenv import load_dotenv


load_dotenv()


API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get("API_TOKEN")


def create_automated_tournaments():
    requests.post(
        API_URL + "tournaments/create_automated_tournaments/",
        headers={"authorization": f"token {API_TOKEN}"},
    )


def create_pending_matches():
    requests.post(
        API_URL + "next_match/", headers={"authorization": f"token {API_TOKEN}"}
    )


# HACK: This is here so we keep the cache always fresh
def get_agents():
    requests.get(API_URL + "next_match/?format=json")


def main():
    while True:
        create_pending_matches()
        create_automated_tournaments()
        get_agents()
        sleep(5)
