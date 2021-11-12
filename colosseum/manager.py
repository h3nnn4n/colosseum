import logging

from .agent import Agent


class Manager:
    def __init__(self, world, agent_paths):
        self._agent_paths = agent_paths
        self.agents = [Agent(agent_path) for agent_path in agent_paths]
        self.world = world

        self._tick = 0

    def start(self):
        for agent in self.agents:
            agent.start()
            self.world.register_agent(agent)
        logging.info("started")

    def ping(self):
        for _ in range(2):
            for agent in self.agents:
                agent.ping()
        logging.info("ping completed")

    def tick(self):
        world_state = self.world.state
        for agent in self.agents:
            agent.update_state(world_state)

        for agent in self.agents:
            agent.get_actions()

        logging.info(f"tick {self._tick}")
        self._tick += 1

    def stop(self):
        for agent in self.agents:
            agent.stop()
        logging.info("stopped")
