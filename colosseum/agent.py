import atexit
import json
import logging
import os
import os.path
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
from tempfile import mkdtemp
from time import time
from uuid import uuid4

import pexpect
from pexpect.popen_spawn import PopenSpawn

from colosseum.utils import get_internal_id


DOCKER_AGENT_TIMEOUT = 30
NATIVE_AGENT_TIMEOUT = 5

DEFAULT_AGENT_CHANNEL = "STDIO"


class Agent:
    def __init__(self, agent_path, id=None, time_config=None):
        self.id = id or str(uuid4())
        self.logger = logging.getLogger(f"AGENT_{self.id}")
        self._child_process = None
        self._agent_path = agent_path
        self.name = None
        self._machine_name = None
        self.version = None

        self._agent_started = None
        self._successful_ping = None
        self._set_config = None
        self._set_agent_id = None
        self._errors = []
        self._tainted = False
        self._tainted_reason = None
        self._max_errors_allowed = 10

        self._time_config = time_config
        self.t_start = None
        self.t_end = None
        self._step_durations = []
        self._step_time_limit = time_config.step_time_limit
        self._step_limit_pool = time_config.step_limit_pool
        self._overtime = None

    def start(self):
        # The log message is both helpful, and warms the cache too
        self.logger.info(f"using agent_channel = {self.agent_channel}")

        self._child_process = self._boot_agent()

        response = self._exchange_message({"set_agent_id": self.id})

        if not response:
            self.logger.warn(f"agent {self.id} failed to start")
            self._agent_started = False
            self.logger.warn("This is an unrecoverable error")
            self._tainted = True
            self._tainted_reason = "STARTUP_FAIL"
            return

        if response.get("agent_id") != self.id or response.get("agent_id") is None:
            self.logger.warning(f"agent failed to set id. got: {response}")
            self._set_agent_id = False
            self._log_error_count()
        else:
            self._set_agent_id = True

        if response.get("agent_name"):
            self.name = response.get("agent_name")

        if response.get("agent_version"):
            self.version = response.get("agent_version")

        if self.name:
            self.logger.info(f"agent name {self.name} {self.version}")

        self.logger.info(f"agent {self.id} started")
        self._agent_started = True

    def ping(self):
        response = self._exchange_message({"ping": "ping"})

        if not response:
            self._successful_ping = False
            return False

        valid_ping = response.get("pong") is not None
        if not valid_ping:
            self.logger.warning(
                f"agent {self.id} sent invalid response to ping: {response}"
            )
        self._successful_ping = valid_ping
        return valid_ping

    def set_config(self, config):
        response = self._exchange_message({"config": config})

        if response is None:
            self._set_config = False

    def stop(self, reason="end_of_game"):
        self._exchange_message({"stop": {"reason": reason}})

    def update_state(self, state):
        self._tick()
        self.__next_action = self._exchange_message(state)
        self._tock()

    def get_actions(self):
        if self.__next_action is None:
            self.logger.info("failed to get agent actions")
            return {}

        actions = self.__next_action
        agent_id = actions.get("agent_id")

        if agent_id is None:
            self.logger.warning(f"agent {self.id} did not give an agent id")
        elif agent_id != self.id:
            self.logger.warning(f"agent {self.id} return invalid agent id")

        return actions

    def _log_error_count(self):
        self.logger.warning(f"error_count: {self.error_count}")

    @property
    def agent_path(self):
        return self._agent_path

    @property
    def agent_manifest(self):
        if hasattr(self, "_manifest"):
            return self._manifest

        agent_folder = os.path.dirname(os.path.normpath(self.agent_path))
        manifest_path = os.path.join(agent_folder, "manifest.json")

        self.logger.info(f"reading manifest from {manifest_path=}")

        if not os.path.isfile(manifest_path):
            self.logger.info(
                f"manifest file at {manifest_path=} does not exist. Assuming defaults"
            )
            self._manifest = {}
            return self._manifest

        with open(manifest_path, "rt") as f:
            manifest_raw = f.read()

        try:
            manifest = json.loads(manifest_raw)
            self._manifest = manifest
            self.logger.info(f"manifest file at {manifest_path=} parsed successfully")
        except Exception:
            self.logger.info(f"failed to parsemanifest file at {manifest_path=}")

        return self._manifest

    @property
    def agent_channel(self):
        return self.agent_manifest.get("agent_channel", DEFAULT_AGENT_CHANNEL).upper()

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
        if self._tainted:
            return True

        # TODO: Report why the agent got tainted
        if self.error_count > self._max_errors_allowed:
            # Too many errors
            self._tainted_reason = "TOO_MANY_ERRORS"
            self._tainted = True

        if self._agent_started is False:
            # Agent failed to start
            self._tainted_reason = "STARTUP_FAIL"
            self._tainted = True

        if self._successful_ping is False:
            # Agent failed to ack ping
            self._tainted_reason = "PING_FAIL"
            self._tainted = True

        if self._set_config is False:
            # Agent failed to ack set config
            self._tainted_reason = "SET_CONFIG_FAIL"
            self._tainted = True

        if self._set_agent_id is False:
            # Agent failed to ack set agent id
            self._tainted_reason = "SET_AGENT_ID_FAIL"
            self._tainted = True

        self._step_duration_check()
        if self._overtime:
            # Agent took too long to respond
            self._tainted_reason = "TIMEOUT"
            self._tainted = True

        return self._tainted

    @property
    def tainted_reason(self):
        return self._tainted_reason

    def _tick(self):
        if self.t_end is not None:
            raise RuntimeError("Called _tick twice")

        self.t_start = time()

    def _tock(self):
        if self.t_start is None:
            raise RuntimeError("Called _tock without calling _tick first")

        self.t_end = time()
        duration = self.t_end - self.t_start
        self._step_durations.append(duration)
        self.t_start = None
        self.t_end = None

        if duration > self._step_time_limit:
            self.logger.warning(
                f"agent {self.name} tick took {duration}. "
                f"Limit is {self._step_time_limit}. "
                f"Spent {duration - self._step_time_limit}. "
                f"Time pool remaining {self._overtime_pool}"
            )

    @property
    def _overtime_pool(self):
        times_above_limit = [
            x - self._step_time_limit
            for x in self._step_durations
            if x > self._step_time_limit
        ]
        overtime = sum(times_above_limit)
        return self._step_limit_pool - overtime

    def _step_duration_check(self):
        if self._overtime_pool < 0:
            self.logger.warning(f"agent is overtime by {self._overtime_pool}")
            self._overtime = True

    def _exchange_message(self, message):
        if not self.agent_channel or self.agent_channel == "STDIO":
            return self._exchange_stdio_message(message)

        return self._exchange_http_message(message)

    def _exchange_stdio_message(self, message):
        try:
            payload = json.dumps(message)
            self._child_process.sendline(payload, timeout=NATIVE_AGENT_TIMEOUT)
        except Exception as e:
            self._errors.append(
                {
                    "error": "failed to send message",
                    "payload": payload,
                    "exception": e.__str__(),
                }
            )

            self._log_error_count()
            return None

        try:
            response_str = self._child_process.readline(timeout=NATIVE_AGENT_TIMEOUT)
            response = json.loads(response_str)
            return response
        except json.JSONDecodeError as e:
            self.logger.info(
                f"failed to parse agent actions. Got invalid json payload. Error: {e}"
            )
            self.logger.info("agent said:")

            if hasattr(self, "response_str"):
                self.logger.info(response_str)

            while True:
                try:
                    agent_output = self._child_process.read_nonblocking(
                        size=2048, timeout=1
                    )
                    if agent_output:
                        self.logger.info(agent_output)
                except pexpect.exceptions.EOF:
                    break

            self._errors.append(
                {
                    "error": "failed to receive message",
                    "payload": response_str,
                    "exception": e.__str__(),
                }
            )
            self._log_error_count()
            return None
        except Exception as e:
            if not hasattr(self, "response_str"):
                response_str = "NOT_SET"
            else:
                self.logger.info(f"agent said: {response_str}")

            self._errors.append(
                {
                    "error": "failed to receive message",
                    "payload": response_str,
                    "exception": e.__str__(),
                }
            )
            self._log_error_count()
            return None
        else:
            return response

    def _exchange_http_message(self, message):
        pass

    def _boot_agent(self):
        # Pure python agent
        if "agent.py" in self.agent_path:
            return PopenSpawn([self._agent_path], timeout=NATIVE_AGENT_TIMEOUT)

        # Pure node agent
        if "agent.js" in self.agent_path:
            return PopenSpawn([self._agent_path], timeout=NATIVE_AGENT_TIMEOUT)

        # Docker agent
        return PopenSpawn(
            ["./colosseum/docker_http_wrapper.py", self._agent_path, self.id],
            timeout=DOCKER_AGENT_TIMEOUT,
        )
