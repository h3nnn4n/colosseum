#!/usr/bin/env python3

import json
import logging
import os
import shlex
import subprocess
import tempfile
import uuid
from random import randint

import requests
from retrying import retry


self_id = str(uuid.uuid4())

DOCKER_AGENT_PORT = randint(1024, 65535)

logging.basicConfig(filename=f"network_wrapper_{self_id}.log", level=logging.DEBUG)


@retry(wait_exponential_multiplier=10, wait_exponential_max=5000)
def _exchange_data(data):
    response = requests.post(
        f"http://localhost:{DOCKER_AGENT_PORT}", json=json.loads(data)
    )
    return response.content.decode()


def main(agent_path, agent_id):
    logging.info(f"running with {agent_path=} {agent_id=}")
    http_agent = HttpAgent(agent_path, agent_id)
    try:
        http_agent.boot()
    finally:
        http_agent.cleanup()


class HttpAgent:
    def __init__(self, agent_path, agent_id):
        self._agent_path = agent_path
        self.id = agent_id

    def boot(self):
        agent_path = self._agent_path.replace("Dockerfile", "")

        self.build_container(self.id, agent_path)
        self.container_id = self.start_container(self.id)

        self._event_loop()

    def cleanup(self):
        self.kill_container(self.container_id)

    def _event_loop(self):
        logging.info("starting event loop")
        while True:
            logging.debug("-------------------")
            logging.debug("1")
            data_out = sys.stdin.readline().encode()
            logging.debug("2")
            logging.debug(f"sending to agent: {data_out}")
            try:
                data_in = _exchange_data(data_out)
            except Exception as e:
                logging.exception(e)

            logging.debug("3")

            logging.debug("4")
            logging.debug(f"got from agent: {data_in}")
            sys.stdout.write(data_in)
            logging.debug("5")
            sys.stdout.flush()
            logging.debug("6")

    def start_container(self, tag):
        logging.info(f"starting container with {tag=}")
        cmd = (
            f"docker run -p 127.0.0.1:{DOCKER_AGENT_PORT}:80/tcp --rm=true --detach "
            + tag
        )
        logging.info(f"starting container with {cmd}")
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        output = proc.stdout.readline().decode()[:-1]
        logging.debug(f"docker start returned {output=}")
        return output

    def kill_container(self, container_id):
        logging.info(f"killing container with {container_id=}")
        subprocess.call(["docker", "kill", container_id], stdout=subprocess.PIPE)

    def build_container(self, tag, dockerfile):
        logging.info(f"building container with {tag=}")
        cmd = f"docker build --tag={tag} {dockerfile}"
        logging.info(f"building container with {cmd}")
        if (
            subprocess.call(
                shlex.split(cmd),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            != 0
        ):
            logging.info("failed to build")
            raise Exception("Couldn't build container")
        logging.info(f"finished building container with {tag=}")
        return


if __name__ == "__main__":
    import sys

    main(*sys.argv[1:])
