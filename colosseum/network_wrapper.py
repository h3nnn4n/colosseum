#!/usr/bin/env python3

import atexit
import logging
import os
import shlex
import socket
import subprocess
import tempfile


logging.basicConfig(level=logging.DEBUG)

# FIXME: This probably needs to be random to allow multiple agents to run at
# the same time without issues
SERVER_ADDRESS = os.path.join(tempfile.mkdtemp(), "colosseum.socket")
SERVER_ADDRESS = "colosseum.socket"
SEPARATOR = "\n"


def reader(socket, read_size=64):
    buffer = ""
    while True:
        print(f"try to read from sock with blocksize of {read_size}")
        new_data = socket.recv(read_size).decode()
        buffer += new_data
        print(f"got: {new_data}")

        if SEPARATOR in buffer:
            data, _, buffer = buffer.partition(SEPARATOR)
            yield data


def main(agent_path, agent_id):
    NetworkAgent(agent_path, agent_id).boot()


class NetworkAgent:
    def __init__(self, agent_path, agent_id):
        self._agent_path = agent_path
        self.id = agent_id

    def boot(self):
        logging.info("Using docker boot")
        atexit.register(clean_socket)

        agent_path = self._agent_path.replace("Dockerfile", "")
        tag = self.id

        self.build_container(tag, agent_path)

        self._server_start()

        container_id = self.start_container(tag)
        atexit.register(self.kill_container, container_id)

        self._server_connect()
        self._event_loop()

        logging.info(f"agent {tag} running on container {container_id}")

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
        print(f"using separator {SEPARATOR}")
        print("stating event loop")
        while True:
            data_out = sys.stdin.readline().encode()
            print(f"sending: {data_out}")
            self._clientsocket.sendall(data_out)
            print("sent, waiting for response")
            data_in = next(reader(self._clientsocket))
            print(f"got: {data_in}")

    def start_container(self, tag):
        logging.info(f"starting container with {tag=}")
        cmd = (
            # "docker run --rm=true --tty=true --interactive=true --detach "
            "docker run --rm=true --tty=true --interactive=true "
            # + f'--env SEPARATOR="{SEPARATOR}" '
            + f"--volume {SERVER_ADDRESS}:/var/colosseum.socket "
            + tag
        )
        logging.debug(f"starting server with {cmd}")
        # proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        # return proc.stdout.readline().decode()[:-1]
        return "foo"

    def kill_container(self, container_id):
        logging.info(f"killing container with {container_id=}")
        subprocess.call(["docker", "kill", container_id], stdout=subprocess.PIPE)

    def build_container(self, tag, dockerfile):
        logging.info(f"building container with {tag=}")
        cmd = f"docker build --tag={tag} {dockerfile}"
        logging.debug(f"building container with {cmd}")
        if subprocess.call(shlex.split(cmd)) != 0:
            raise Exception("Couldn't build container")
        return


def clean_socket():
    os.remove(SERVER_ADDRESS)


if __name__ == "__main__":
    import sys

    main(*sys.argv[1:])
