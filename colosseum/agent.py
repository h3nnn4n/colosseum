import atexit
import json
import logging
import os
import shlex
import shutil
import subprocess
import sys
from signal import SIGTERM
from tempfile import mkdtemp
from uuid import uuid4

import pexpect
from pexpect.popen_spawn import PopenSpawn


logging.basicConfig(level=logging.INFO)


class Agent:
    def __init__(self, agent_path, id=None):
        self._child_process = None
        self._agent_path = agent_path
        self.id = id or str(uuid4())
        self.name = None
        self._machine_name = None
        self.version = None

        self._agent_started = None
        self._successful_ping = None
        self._set_config = None
        self._set_agent_id = None
        self._errors = []
        self._max_errors_allowed = 10

    def start(self):
        self._child_process = self._boot_agent()

        try:
            payload = json.dumps({"set_agent_id": self.id})
            self._child_process.sendline(payload)
        except Exception as e:
            self._agent_started = False
            self._log_error_count()
            self._errors.append(
                {
                    "error": "startup_failed",
                    "payload": payload,
                    "exception": e.__str__(),
                }
            )
            return

        try:
            response_str = self._child_process.readline()
            response = json.loads(response_str)

            if response.get("agent_id") != self.id or response.get("agent_id") is None:
                logging.warning(f"agent failed to set id. got: {response}")
                self._set_agent_id = False
                self._log_error_count()
            else:
                self._set_agent_id = True

            if response.get("agent_name"):
                self.name = response.get("agent_name")

            if response.get("agent_version"):
                self.version = response.get("agent_version")

            if self.name:
                logging.info(f"agent name {self.name} {self.version}")

            logging.info(f"agent {self.id} started")
            self._agent_started = True
        except Exception as e:
            if not hasattr(self, "response_str"):
                response_str = "NOT_SET"

            self._agent_started = False
            logging.warn(
                f"agent {self.id} failed to start with error: {e}"
                f"payload sent: {payload}   payload_received: {response_str}"
            )
            self._log_error_count()
            self._errors.append(
                {
                    "error": "startup_failed",
                    "payload": response_str,
                    "exception": e.__str__(),
                }
            )

    def ping(self):
        try:
            payload = {"ping": "foobar"}
            self._child_process.sendline(json.dumps(payload))
        except Exception as e:
            logging.info(f"failed to send ping payload {payload} {e}")
            self._log_error_count()
            self._errors.append(
                {
                    "error": "send_ping_failed",
                    "payload": payload,
                    "exception": e.__str__(),
                }
            )
            self._successful_ping = False
            return False

        try:
            response_str = self._child_process.readline()
            data = json.loads(response_str)
            valid_ping = data.get("pong") is not None
            if not valid_ping:
                logging.warning(
                    f"agent {self.id} sent invalid response to ping: {data}"
                )
            self._successful_ping = valid_ping
            return valid_ping
        except Exception as e:
            logging.warning(
                f"agent {self.id} failed to ack ping: Exception {e}\n{locals()}"
            )
            self._log_error_count()
            self._errors.append(
                {
                    "error": "ping_failed",
                    "payload": response_str,
                    "exception": e.__str__(),
                }
            )
            self._successful_ping = False
            return False

    def set_config(self, config):
        try:
            payload = {"config": config}
            self._child_process.sendline(json.dumps(payload))
        except Exception as e:
            logging.info(f"failed to send config payload {payload} {e}")
            self._log_error_count()
            self._errors.append(
                {
                    "error": "send_set_config",
                    "payload": payload,
                    "exception": e.__str__(),
                }
            )
            self._set_config = False
            return

        try:
            self._child_process.readline()
            self._set_config = True
        except Exception as e:
            logging.info(f"failed to get config payload back {payload} {e}")
            self._log_error_count()
            self._errors.append(
                {
                    "error": "send_ping_failed",
                    "payload": payload,
                    "exception": e.__str__(),
                }
            )
            self._set_config = False

    def stop(self, reason="end_of_game"):
        try:
            payload = json.dumps({"stop": {"reason": reason}})
            self._child_process.sendline(payload)
            self._child_process.kill(SIGTERM)
            logging.info(f"agent {self.id} stopped")
        except Exception as e:
            logging.info(f"failed to stop agent {payload} {e}")
            self._log_error_count()
            self._errors.append(
                {"error": "stop_failed", "payload": payload, "exception": e.__str__()}
            )

    def update_state(self, state):
        payload = json.dumps(state)
        try:
            self._child_process.sendline(payload)
        except Exception as e:
            logging.info(f"failed to update agent state {payload} {e}")
            self._log_error_count()
            self._errors.append(
                {
                    "error": "update_state_failed",
                    "payload": payload,
                    "exception": e.__str__(),
                }
            )

    def get_actions(self):
        actions_raw = self._child_process.readline()
        try:
            actions = json.loads(actions_raw)
            agent_id = actions.get("agent_id")

            if agent_id is None:
                logging.warning(f"agent {self.id} did not give an agent id")
            elif agent_id != self.id:
                logging.warning(f"agent {self.id} return invalid agent id")

            return actions
        except Exception as e:
            logging.info(f"failed to get agent actions{e}")
            self._log_error_count()
            self._errors.append(
                {"error": "get_actions_failed", "exception": e.__str__()}
            )
            return {}

    def _log_error_count(self):
        logging.warning(f"error_count: {self.error_count}")

    @property
    def agent_path(self):
        return self._agent_path

    @property
    def error_count(self):
        return len(self._errors)

    @property
    def tainted(self):
        """
        Returns True when agent is in an invalid or unrecoverable state.  Can
        also return True if cheating is detected or the error count is
        exceeded. Returns False otherwise.
        """
        if self.error_count > self._max_errors_allowed:
            # Too many errors
            return True

        if self._agent_started is False:
            # Agent failed to start
            return True

        if self._successful_ping is False:
            # Agent failed to ack ping
            return True

        if self._set_config is False:
            # Agent failed to ack set config
            return True

        if self._set_agent_id is False:
            # Agent failed to ack set agent id
            return True

        return False

    def _boot_agent(self):
        # FIXME: In the future we might want to just support docker
        # based agents to not have to maintain two versions
        if "Dockerfile" not in self._agent_path:
            logging.info("Using old agent boot")
            return PopenSpawn(self._agent_path)

        logging.info("Using docker boot")
        # self._build_image()
        # return self._run_image()
        agent_path = self._agent_path.replace("Dockerfile", "")
        runner = spawnu(self.id, agent_path)
        # __import__("ipdb").set_trace(context=11)
        runner.sendline("{}")
        logging.info(runner.readline())
        logging.info(runner.readline())
        runner.sendline("{}")
        logging.info(runner.readline())
        logging.info(runner.readline())
        # __import__("ipdb").set_trace(context=11)
        return runner

    def _build_image(self):
        agent_path = self._agent_path.replace("Dockerfile", "")
        raw_command = f"docker build -t {self.id} {agent_path}"
        logging.info(f"{raw_command=}")
        cmd = shlex.split(raw_command)
        logging.info(f"{cmd=}")
        subprocess.run(cmd)

    def _run_image(self):
        raw_command = (
            f"docker run --rm=true --interactive=true --tty=true --detach {self.id}"
        )
        logging.info(f"{raw_command=}")
        cmd = shlex.split(raw_command)
        logging.info(f"{cmd=}")
        runner = PopenSpawn(cmd)
        return runner


def spawnu(tag, dockerfile):
    build_container(tag, dockerfile)
    container_id = run(tag)
    logging.info(f"agent {tag} running on container {container_id}")
    atexit.register(kill, container_id)

    raw_command = f"docker attach {container_id}"
    cmd = shlex.split(raw_command)
    logging.info(f"{cmd=}")
    # runner = PopenSpawn(cmd)
    # runner = pexpect.spawn(cmd)
    runner = pexpect.spawnu("docker", ["attach", container_id], logfile=sys.stderr)
    runner.setecho(False)
    print(runner.waitnoecho())

    # runner = pexpect.spawnu("docker", ["attach", container_id], logfile=sys.stderr)

    # runner.docker_container_id = container_id
    return runner


def run(tag):
    proc = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm=true",
            "--tty=true",
            "--interactive=true",
            "--detach",
            tag,
        ],
        stdout=subprocess.PIPE,
    )
    return proc.stdout.readline().decode()[:-1]


def kill(container_id):
    subprocess.call(["docker", "kill", container_id], stdout=subprocess.PIPE)


def build_container(tag, dockerfile):
    if subprocess.call(["docker", "build", "--tag={}".format(tag), dockerfile]) != 0:
        raise Exception("Couldn't build container")
    return
