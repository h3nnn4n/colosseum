#!/usr/bin/env python3

import json
import logging
import os
import shlex
import socket
import subprocess
import tempfile
import uuid


self_id = str(uuid.uuid4())

logging.basicConfig(filename=f"network_wrapper_{self_id}.log", level=logging.DEBUG)

SERVER_ADDRESS_PATH = tempfile.mkdtemp()
SERVER_FILE = f"colosseum_{self_id}.socket"
SERVER_ADDRESS = os.path.join(SERVER_ADDRESS_PATH, SERVER_FILE)
SEPARATOR = "\n"


def reader(socket, read_size=64):
    buffer = ""
    while True:
        new_data = socket.recv(read_size).decode()
        buffer += new_data

        if SEPARATOR in buffer:
            data, _, buffer = buffer.partition(SEPARATOR)
            if "\n" not in data:
                data = data + "\n"
            yield data


def main(agent_path, agent_id):
    logging.debug(f"running with {agent_path=} {agent_id=}")
    network_agent = NetworkAgent(agent_path, agent_id)
    try:
        network_agent.boot()
    finally:
        network_agent.cleanup()


class NetworkAgent:
    def __init__(self, agent_path, agent_id):
        self._agent_path = agent_path
        self.id = agent_id

    def boot(self):
        agent_path = self._agent_path.replace("Dockerfile", "")
        tag = self.id

        self.build_container(tag, agent_path)

        self._server_start()

        self.container_id = self.start_container(tag)

        self._server_connect()
        self._event_loop()

    def cleanup(self):
        clean_socket()
        self.kill_container(self.container_id)

    def _server_start(self):
        logging.info(f"starting server on {SERVER_ADDRESS}")
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(SERVER_ADDRESS)
        self._server.listen()
        logging.info("server started")

    def _server_connect(self):
        logging.info("waiting for connection")
        self._clientsocket, self._clientaddress = self._server.accept()
        logging.info("connected")

    def _event_loop(self):
        while True:
            data_out = sys.stdin.readline().encode()
            self._clientsocket.sendall(data_out)

            if check_stop(data_out):
                logging.info("sending stop")
                break

            data = next(reader(self._clientsocket))
            logging.debug(f"sent: {data_out}   got: {data}")
            sys.stdout.write(data)
            sys.stdout.flush()

    def start_container(self, tag):
        logging.info(f"starting container with {tag=}")
        cmd = (
            "docker run --rm=true --tty=true --interactive=true --detach "
            + f"--volume {SERVER_ADDRESS_PATH}:/var/colosseum/ "
            + tag
        )
        logging.debug(f"starting server with {cmd}")
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        return proc.stdout.readline().decode()[:-1]

    def kill_container(self, container_id):
        logging.info(f"killing container with {container_id=}")
        subprocess.call(["docker", "kill", container_id], stdout=subprocess.PIPE)

    def build_container(self, tag, dockerfile):
        logging.info(f"building container with {tag=}")
        cmd = f"docker build --tag={tag} {dockerfile}"
        logging.debug(f"building container with {cmd}")
        if (
            subprocess.call(
                shlex.split(cmd),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            != 0
        ):
            logging.info(f"failed to build")
            raise Exception("Couldn't build container")
        logging.info(f"finished building container with {tag=}")
        return


def clean_socket():
    if os.path.exists(SERVER_ADDRESS):
        os.remove(SERVER_ADDRESS)


def check_stop(raw_message):
    try:
        payload = json.loads(raw_message)
        if payload.get("stop"):
            logging.info("found stop command")
            return True
    except Exception as e:
        return False


if __name__ == "__main__":
    import sys

    main(*sys.argv[1:])
