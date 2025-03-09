#!/usr/bin/env python3

import atexit
import logging
import shlex
import subprocess
import uuid
import sys
import pexpect
from pexpect.popen_spawn import PopenSpawn


self_id = str(uuid.uuid4())

logging.basicConfig(filename=f"docker_wrapper_{self_id}.log", level=logging.DEBUG)


def main(agent_path, agent_id):
    logging.info(f"running with {agent_path=} {agent_id=}")
    docker_agent = DockerAgent(agent_path, agent_id)

    @atexit.register
    def cleanup():
        docker_agent.cleanup()

    try:
        docker_agent.boot()
    finally:
        cleanup()


class DockerAgent:
    def __init__(self, agent_path, agent_id):
        self._agent_path = agent_path
        self.id = agent_id
        self.container_process = None

    def boot(self):
        agent_path = self._agent_path.replace("Dockerfile", "")

        self.build_container(self.id, agent_path)
        self.start_container(self.id)

        self._event_loop()

    def cleanup(self):
        if self.container_process:
            try:
                self.container_process.sendcontrol('c')
                self.container_process.sendline('exit')
                self.container_process.close()
            except:
                logging.info("Terminating container forcefully")
                subprocess.call(["docker", "kill", self.id], stdout=subprocess.PIPE)

    def _event_loop(self):
        got_blank_from_agent = False
        got_blank_from_master = False
        logging.info("starting event loop")

        while not got_blank_from_agent and not got_blank_from_master:
            logging.info(f"{got_blank_from_agent=} {got_blank_from_master=}")
            logging.debug("-------------------")
            logging.debug("1")
            data_out = sys.stdin.readline()
            if data_out:
                data_out = data_out.strip()
            logging.debug("2")
            logging.debug(f"sending to agent: {data_out}")

            if not data_out:
                got_blank_from_master = True
                logging.info("breaking because got blank from master")
                break

            try:
                data_in = self._exchange_data(data_out)

                if not data_in:
                    got_blank_from_agent = True
                    logging.info("breaking because got blank from agent")
                    break

            except Exception as e:
                logging.debug("3")
                logging.exception(e)
                logging.debug("4")
                logging.debug("got no data from agent")
                sys.stdout.write("{}")
                logging.debug("5")
                sys.stdout.flush()
                logging.debug("6")
                continue

            logging.debug("3")
            logging.debug("4")
            logging.debug(f"got from agent: {data_in}")
            sys.stdout.write(data_in)
            logging.debug("5")
            sys.stdout.flush()
            logging.debug("6")

    def _exchange_data(self, data_out: str) -> str:
        try:
            self.container_process.sendline(data_out.strip())

            response_str = self.container_process.readline()
            if response_str:
                response_str = response_str.strip()
            logging.debug(f"response from container: {response_str}")
            return response_str
        except Exception as e:
            logging.exception(f"Error communicating with container: {e}")
            return "{}"

    def start_container(self, tag):
        logging.info(f"starting container in interactive mode with: {tag=}")
        cmd = f"docker run -i --rm {tag}"
        logging.info(f"starting container with: {cmd}")

        # Use PopenSpawn for interactive communication
        self.container_process = PopenSpawn(cmd, encoding='utf-8')
        logging.debug("Container started in interactive mode")

    def build_container(self, tag, dockerfile):
        logging.info(f"building container with: {tag=}")
        cmd = f"docker build --tag={tag} {dockerfile}"
        logging.info(f"building container with: {cmd}")
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
