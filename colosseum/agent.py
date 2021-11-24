import json
import logging
from signal import SIGTERM
from uuid import uuid4

from pexpect.popen_spawn import PopenSpawn


class Agent:
    def __init__(self, agent_path):
        self._child_process = None
        self._agent_path = agent_path
        self.id = str(uuid4())
        self.name = None
        self.version = None

    def start(self):
        self._child_process = PopenSpawn(self._agent_path)
        self._child_process.sendline(json.dumps({"set_agent_id": self.id}))
        response_str = self._child_process.readline()
        response = json.loads(response_str)

        if response.get("agent_id") != self.id:
            logging.warning(f"agent failed to set id. got: {response}")

        if response.get("agent_name"):
            self.name = response.get("agent_name")

        if response.get("agent_version"):
            self.version = response.get("agent_version")

        if self.name:
            logging.info(f"agent name {self.name} {self.version}")

        logging.info(f"agent {self.id} started")

    def ping(self):
        try:
            payload = {"ping": "foobar"}
            self._child_process.sendline(json.dumps(payload))
            raw_data = self._child_process.readline()
            data = json.loads(raw_data)
            valid_ping = data.get("pong") is not None
            if not valid_ping:
                logging.warning(
                    f"agent {self.id} sent invalid response to ping: {data}"
                )
            return valid_ping
        except Exception as e:
            logging.warning(
                f"agent {self.id} failed to ack ping: Exception {e}\n{locals()}"
            )
            return False

    def set_config(self, config):
        payload = {"config": config}
        self._child_process.sendline(json.dumps(payload))
        self._child_process.readline()

    def stop(self, reason="end_of_game"):
        data = {"stop": {"reason": reason}}
        self._child_process.sendline(json.dumps(data))
        self._child_process.kill(SIGTERM)
        logging.info(f"agent {self.id} stopped")

    def update_state(self, state):
        payload = json.dumps(state)
        self._child_process.sendline(payload)

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
            print(e)
            print(actions_raw)
            return {}

    @property
    def agent_path(self):
        return self._agent_path
