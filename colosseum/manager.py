import json
import logging

from .agent import Agent


class Manager:
    def __init__(self, world, agent_paths=None, agents=None):
        self.world = world
        self._replay_enable = True
        self._replay_filename = None

        self._tick = 1
        self._number_of_ticks = 1000

        self._stop = False

        self._set_replay_file()

        if agents:
            self.agents = agents
        else:
            self.agents = [Agent(agent_path) for agent_path in agent_paths]

    def _set_replay_file(self):
        if not self._replay_enable:
            return

        import random
        import string
        from datetime import datetime

        now = datetime.now()
        random_string = "".join(
            random.choices(
                string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6
            )
        )
        random_part = "_".join([now.strftime("%y%m%d_%H%M%S"), random_string])
        self._replay_filename = f"replay_{self.world.name}_{random_part}.jsonl"

    def start(self):
        for agent in self.agents:
            agent.start()
            self.world.register_agent(agent)
            agent.ping()
            agent.set_config(self.world.config)

        self._check_for_tainted_agents()
        logging.info("started")

    def ping(self):
        for agent in self.agents:
            agent.ping()

        self._check_for_tainted_agents()
        logging.info("ping completed")

    def loop(self):
        while not self.world.finished():
            self.tick()
            if self._check_for_tainted_agents():
                break

    def tick(self):
        if self.world.config["update_mode"] == "ALTERNATING":
            self._tick_alternating()
        else:
            self._tick_simultaneous()

    def _tick_alternating(self):
        world_state = self.world.state
        world_state["epoch"] = self._tick
        world_state["max_epoch"] = self._number_of_ticks
        world_state["agent_ids"] = [agent.id for agent in self.agents]

        agent_index = self._tick % len(self.agents)
        agent_to_update = self.agents[agent_index]
        agent_to_update.update_state(world_state)

        agent_actions = [agent_to_update.get_actions()]
        self._save_replay(world_state, agent_actions)
        self.world.update(agent_actions)

        logging.info(f"tick {self._tick}")
        self._tick += 1

    def _tick_simultaneons(self):
        world_state = self.world.state
        world_state["epoch"] = self._tick
        world_state["max_epoch"] = self._number_of_ticks
        world_state["agent_ids"] = [agent.id for agent in self.agents]

        for agent in self.agents:
            agent.update_state(world_state)

        agent_actions = [agent.get_actions() for agent in self.agents]

        self._save_replay(world_state, agent_actions)

        self.world.update(agent_actions)

        logging.info(f"tick {self._tick}")
        self._tick += 1

    def stop(self):
        for agent in self.agents:
            agent.stop()

        logging.info("stopped")

    @property
    def results(self):
        return {
            "scores": self.scores,
            "replay_file": self._replay_filename,
            "outcome": self.world.outcome,
        }

    @property
    def scores(self):
        scores = []

        for agent_id, score in self.world.scores.items():
            agent = self._get_agent(agent_id)
            scores.append(
                {
                    "name": agent.name,
                    "version": agent.version,
                    "score": score,
                    "agent_id": agent_id,
                    "agent_path": agent.agent_path,
                    "tainted": agent.tainted,
                }
            )

        return sorted(scores, key=lambda x: x["score"], reverse=True)

    @property
    def has_tainted_agent(self):
        return len(self.tainted_agents) > 0

    @property
    def tainted_agents(self):
        return [agent for agent in self.agents if agent.tainted]

    def _check_for_tainted_agents(self):
        if not self.has_tainted_agent:
            return False

        self._stop = True
        return True

    def _save_replay(self, world_state, agent_actions):
        if not self._replay_enable:
            return

        data = {
            "game_config": self.world.config,
            "epoch": self._tick,
            "max_epoch": self._number_of_ticks,
            "world_state": world_state,
            "agent_actions": agent_actions,
            "agent_ids": [agent.id for agent in self.agents],
        }

        with open(self._replay_filename, "at") as f:
            f.write(json.dumps(data))
            f.write("\n")

    def _get_agent(self, id):
        return next((agent for agent in self.agents if agent.id == id), None)
