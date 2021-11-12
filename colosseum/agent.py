import json
import logging
from uuid import uuid4

import pexpect


class Agent:
    def __init__(self, agent_path):
        self._child_process = None
        self._agent_path = agent_path
        self.id = str(uuid4())

    def start(self):
        self._child_process = pexpect.spawn(self._agent_path)
        self._child_process.setecho(False)
        self._child_process.sendline(json.dumps({"set_agent_id": self.id}).encode())
        logging.info(f"agent {self.id} started")

    def ping(self):
        try:
            self._child_process.sendline(json.dumps({"ping": "foobar"}).encode())
            raw_data = self._child_process.readline().decode().strip()
            data = json.loads(raw_data)
            return data.get("pong") is not None
        except Exception:
            logging.warning(f"agent {self.id} failed to ack ping\n{locals()}")
            return False

    def stop(self, reason="end_of_game"):
        data = {"stop": {"reason": reason}}
        self._child_process.sendline(json.dumps(data).encode())
        self._child_process.close()
        logging.info(f"agent {self.id} stopped")

    def update_state(self, state):
        self._child_process.sendline(json.dumps(state).encode())

    def get_actions(self):
        actions_raw = self._child_process.readline().decode().strip()
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
