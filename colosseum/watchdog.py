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


def main():
    while True:
        create_automated_tournaments()
        sleep(5)
