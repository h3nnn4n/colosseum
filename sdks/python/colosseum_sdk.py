import json
import logging
import sys


class BaseEntity:
    def __init__(self, entity):
        self._position = entity["position"]
        self._id = entity["id"]

    @property
    def position(self):
        return self._position

    @property
    def id(self):
        return self._id


class ActionableEntity(BaseEntity):
    def __init__(self, data):
        super(ActionableEntity, self).__init__(data)

        self._food = data["food"]
        self._health = data["health"]
        self._max_health = data["max_health"]
        self._owner_id = data["owner_id"]

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def health(self):
        return self._health

    @property
    def max_health(self):
        return self._max_health

    @property
    def missing_health(self):
        return self._max_health - self._health

    @property
    def alive(self):
        return self._health > 0

    @property
    def dead(self):
        return self._health <= 0


class Food(BaseEntity):
    def __init__(self, data):
        super(Food, self).__init__(data)

        self._quantity = data["quantity"]

    @property
    def quantity(self):
        return self._quantity


class Base(ActionableEntity):
    pass


class Actor(ActionableEntity):
    pass


class BaseCollection:
    def __init__(self, records):
        self._records = records

    def __inject(self, records):
        self._records.extend(records)
        return self

    def by_owner(self, owner_id):
        return self.filter(lambda x: x.owner_id == owner_id)

    def filter(self, filter_function):
        filtered_records = [r for r in self._records if filter_function(r)]
        return self.__class__([]).__inject(filtered_records)

    def __len__(self):
        return len(self._records)

    @property
    def count(self):
        return len(self)


class Actors(BaseCollection):
    def __init__(self, actors):
        records = [Actor(actor) for actor in actors]
        super(Actors, self).__init__(records)


class Bases(BaseCollection):
    def __init__(self, bases):
        records = [Base(base) for base in bases]
        super(Bases, self).__init__(records)


class Foods(BaseCollection):
    def __init__(self, foods):
        records = [Food(food) for food in foods]
        super(Foods, self).__init__(records)


class State:
    def __init__(self, state):
        self._state = state
        self._actors = Actors(state["world_state"]["actors"])
        self._bases = Bases(state["world_state"]["bases"])
        self._foods = Foods(state["world_state"]["foods"])
        self._agent_ids = state["agent_ids"]

    @property
    def actors(self):
        return self._actors

    @property
    def bases(self):
        return self._bases

    @property
    def foods(self):
        return self._foods

    @property
    def agent_ids(self):
        return self._agent_ids


def send_commands(data):
    data_encoded = json.dumps(data)
    sys.stdout.write(data_encoded + "\n")
    sys.stdout.flush()


def get_state():
    data = sys.stdin.readline()
    state_data = json.loads(data)
    state = State(state_data)
    return state
