import json
import logging
import sys


FOOD_COST_TO_SPAWN_ACTOR = 100
FOOD_COST_TO_MAKE_BASE = 500


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

        self._next_action = None

    def set_next_action(self, action, force=True):
        if self._next_action is not None and not force:
            raise RuntimeError("action can only be set one")

        self._next_action = action

    @property
    def next_action(self):
        return self._next_action

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
    @property
    def can_spawn(self):
        return self.food >= FOOD_COST_TO_SPAWN_ACTOR

    def spawn(self):
        self.set_next_action({"action": "spawn", "base_id": self.id})


class Actor(ActionableEntity):
    def move(self, target):
        self.set_next_action({"action": "move", "actor_id": self.id, "target": target})

    def take_food(self, target):
        self.set_next_action(
            {"action": "take_food", "actor_id": self.id, "food_id": target}
        )

    def deposit_food(self, target):
        self.set_next_action(
            {"action": "deposit_food", "actor_id": self.id, "base_id": target}
        )

    def heal(self, target):
        self.set_next_action({"action": "heal", "actor_id": self.id, "base_id": target})


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

    @property
    def count(self):
        return len(self)

    @property
    def first(self):
        if self.count > 0:
            return self._records[0]

        return None

    @property
    def actions(self):
        return [x.next_action for x in self._records if x.next_action]

    def __len__(self):
        return len(self._records)


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

    @property
    def actions(self):
        return self.actors.actions + self.bases.actions


def send_commands(data):
    data_encoded = json.dumps(data)
    sys.stdout.write(data_encoded + "\n")
    sys.stdout.flush()


def get_state():
    data = sys.stdin.readline()
    state_data = json.loads(data)
    state = State(state_data)
    return state
