from .agent import Agent


class Manager:
    def __init__(self, agent_paths):
        self._agent_paths = agent_paths
        self.agents = [Agent(agent_path) for agent_path in agent_paths]

    def start(self):
        for agent in self.agents:
            agent.start()

    def ping(self):
        for _ in range(2):
            for agent in self.agents:
                agent.ping()

    def stop(self):
        for agent in self.agents:
            agent.stop()
