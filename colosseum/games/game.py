# TODO: We have a bunch more of things to move here, like the
# register agent method, outcome, etc
class BaseGame:
    def _get_agent(self, id):
        return next((agent for agent in self.agents if agent.id == id), None)

    @property
    def initial_config(self):
        return self._config
