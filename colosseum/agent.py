import atexit
import json
import logging
import os
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
        except Exception as e:
            if not hasattr(self, "response_str"):
                response_str = "NOT_SET"

            self._agent_started = False
            self.logger.warn(
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
            self.logger.info(f"failed to send ping payload {payload} {e}")
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
                self.logger.warning(
                    f"agent {self.id} sent invalid response to ping: {data}"
                )
            self._successful_ping = valid_ping
            return valid_ping
        except Exception as e:
            self.logger.warning(
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
            self.logger.info(f"failed to send config payload {payload} {e}")
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
            self.logger.info(f"failed to get config payload back {payload} {e}")
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
            self.logger.info(f"agent {self.id} stopped")
        except Exception as e:
            self.logger.info(f"failed to stop agent {payload} {e}")
            self._log_error_count()
            self._errors.append(
                {"error": "stop_failed", "payload": payload, "exception": e.__str__()}
            )

    def update_state(self, state):
        payload = json.dumps(state)
        try:
            self._tick()
            self._child_process.sendline(payload)
        except Exception as e:
            self.logger.info(f"failed to update agent state {payload} {e}")
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
        # FIXME: The duration should start counting when update_state is called
        # and stop when get_actions gets called
        self._tock()
        try:
            actions = json.loads(actions_raw)
            agent_id = actions.get("agent_id")

            if agent_id is None:
                self.logger.warning(f"agent {self.id} did not give an agent id")
            elif agent_id != self.id:
                self.logger.warning(f"agent {self.id} return invalid agent id")

            return actions
        except Exception as e:
            self.logger.info(f"failed to get agent actions{e}")
            self._log_error_count()
            self._errors.append(
                {"error": "get_actions_failed", "exception": e.__str__()}
            )
            return {}

    def _log_error_count(self):
        self.logger.warning(f"error_count: {self.error_count}")

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
        if self._tainted:
            return True

        # TODO: Report why the agent got tainted
        if self.error_count > self._max_errors_allowed:
            # Too many errors
            self._tainted_reason = "TOO_MANY_ERRORS"
            self._tainted = True

        if self._agent_started is False:
            # Agent failed to start
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
        self._step_durations.append(self.t_end - self.t_start)
        self.t_start = None
        self.t_end = None

    def _step_duration_check(self):
        times_above_limit = [
            x - self._step_time_limit
            for x in self._step_durations
            if x > self._step_time_limit
        ]
        overtime = sum(times_above_limit)
        if overtime > self._step_limit_pool:
            self.logger.warning(
                f"agent is overtime by {overtime - self._step_limit_pool}"
            )
            self._overtime = True

    def _boot_agent(self):
        # Pure python agent
        if "agent.py" in self.agent_path:
            return PopenSpawn([self._agent_path])

        # Docker agent
        return PopenSpawn(["./colosseum/network_wrapper.py", self._agent_path, self.id])
