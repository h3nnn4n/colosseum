import json
from random import randint

import pexpect


class Agent:
    def __init__(self, agent_path):
        self._child_process = None
        self._agent_path = agent_path

    def start(self):
        self._child_process = pexpect.spawn(self._agent_path)
        self._child_process.setecho(False)

    def test(self):
        x = {}
        x["x"] = randint(0, 10)
        x["y"] = randint(0, 10)

        self._child_process.sendline(json.dumps(x).encode())
        raw_data = self._child_process.readline().decode().strip()
        data = json.loads(raw_data)
        assert data["out"] == x["x"] + x["y"]

    def stop(self):
        self._child_process.sendline(json.dumps('{"die": True}').encode())
        self._child_process.close()
