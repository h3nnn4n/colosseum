import logging
import os
from time import sleep, time

import requests
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(level=logging.INFO)


API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get("API_TOKEN")
LOOP_INTERVAL = 3


def create_automated_seasons():
    logging.info("Creating automated seasons")
    response = requests.post(
        API_URL + "automated_seasons/", headers={"authorization": f"token {API_TOKEN}"}
    )

    if response.status_code >= 400:
        logging.warning(f"{response.status_code} {response.content}")


def create_automated_tournaments():
    logging.info("Creating automated tournaments")
    response = requests.post(
        API_URL + "tournaments/create_automated_tournaments/",
        headers={"authorization": f"token {API_TOKEN}"},
    )

    if response.status_code >= 400:
        logging.warning(f"{response.status_code} {response.content}")


def create_pending_matches():
    logging.info("Creating pending matches")
    response = requests.post(
        API_URL + "next_match/", headers={"authorization": f"token {API_TOKEN}"}
    )

    if response.status_code >= 400:
        logging.warning(f"{response.status_code} {response.content}")


# HACK: This is here so we keep the cache always fresh
def get_agents():
    logging.info("Refreshing agent cache (games played)")
    response = requests.get(
        API_URL + "next_match/?format=json",
        headers={"authorization": f"token {API_TOKEN}"},
    )

    if response.status_code >= 400:
        logging.warning(f"{response.status_code} {response.content}")


def main():
    while True:
        logging.info("-" * 64)
        t = time()
        create_automated_seasons()
        create_automated_tournaments()
        create_pending_matches()
        get_agents()
        t_diff = time() - t

        if t_diff < LOOP_INTERVAL:
            logging.info(f"sleeping {LOOP_INTERVAL - t_diff}")
            sleep(LOOP_INTERVAL - t_diff)
