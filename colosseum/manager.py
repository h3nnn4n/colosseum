import json
import logging

from .agent import Agent


class Manager:
    def __init__(self, world, agent_paths):
        self._agent_paths = agent_paths
        self.agents = [Agent(agent_path) for agent_path in agent_paths]
        self.world = world
        self._replay_enable = True
        self._replay_filename = None

        self._tick = 1
        self._number_of_ticks = 1000

        self._set_replay_file()

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
        logging.info("started")

    def ping(self):
        for agent in self.agents:
            agent.ping()

        logging.info("ping completed")

    def loop(self):
        for _ in range(self._number_of_ticks):
            self.tick()

    def tick(self):
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
        return {"scores": self.scores, "replay_file": self._replay_filename}

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
                }
            )

        return sorted(scores, key=lambda x: x["score"], reverse=True)

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
