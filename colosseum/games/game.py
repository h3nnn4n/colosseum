import logging


# TODO: We have a bunch more of things to move here, like the
# register agent method, outcome, etc
class BaseGame:
    @property
    def initial_config(self):
        return self._config

    @property
    def tainted_agents(self):
        return [agent for agent in self.agents if agent.tainted]

    @property
    def has_tainted_agent(self):
        for agent in self.agents:
            if agent.tainted:
                return True
        return False

    @property
    def config(self):
        return {
            k: v
            for k, v in dict(self._config.__dict__).items()
            if not k.startswith("_")
        }

    @property
    def state(self):
        raise NotImplementedError

    @property
    def outcome(self):
        raise NotImplementedError

    @property
    def scores(self):
        raise NotImplementedError

    @property
    def finished(self):
        raise NotImplementedError

    def update(self, agent_actions):
        raise NotImplementedError

    def _get_agent(self, id):
        return next((agent for agent in self.agents if agent.id == id), None)

    def register_agent(self, agent):
        if agent.id in self.agent_ids:
            logging.warning(f"tried to register {agent.id} more than once")
            return

        self.agent_ids.add(agent.id)
        self.agents.add(agent)

        logging.info(f"agent {agent.id} registered")
