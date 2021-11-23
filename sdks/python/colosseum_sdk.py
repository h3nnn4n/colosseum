"""
Colosseum SDK
=============

Python 3 SDK for colloseum, to allow quick development of agents without
worrying about implementation details.
"""
import json
import logging
import sys
from random import choice

from .utils import distance_between, get_id, get_internal_id, get_position


FOOD_COST_TO_SPAWN_ACTOR = 100
"""int: The cost to spawn a new actor from a base"""

FOOD_COST_TO_MAKE_BASE = 500
"""int: The cost to make a new base out of an actor"""


class BaseEntity:
    """
    All entity (objects in the game) inherit from this. It contains an ID and a position
    """

    def __init__(self, entity):
        """
        Initializes an entity from a dict, typically parsed from a json blob from colosseum.

        Parameters
        ---------
        entity
            A dict describing the entity. Must contain at least a `position`
            and an `id` key to be valid.
        """
        self._position = entity["position"]
        self._id = entity["id"]
        self.data = {}
        self.tag = None

    @property
    def position(self):
        """
        Tuple with the pair of coordinates definition the entity position
        """
        return self._position

    @property
    def id(self):
        """
        The entity unique identifier. Guaranteed to stay the same as long as
        the entity is alive.
        """
        return self._id

    def distance_to(self, entity):
        """
        Returns the (euclidian) distance between this and another entity. The
        `entity` param can be a tuple or list of X coordinated, a dict that has
        a key named `position` or a python object with a `position` property.
        """
        return distance_between(self, entity)

    def _update(self, new_state):
        for k, v in new_state.items():
            if hasattr(self, f"_{k}"):
                setattr(self, f"_{k}", v)
            else:
                setattr(self, k, v)


class ActionableEntity(BaseEntity):
    def __init__(self, data):
        super(ActionableEntity, self).__init__(data)

        self._food = data["food"]
        self._health = data["health"]
        self._max_health = data["max_health"]
        self._owner_id = data["owner_id"]

        self._next_action = None

    def set_next_action(self, action, force=True):
        """
        Sets what the next action of the entity will be
        """
        if self._next_action is not None and not force:
            raise RuntimeError("action can only be set one")

        self._next_action = action

    @property
    def next_action(self):
        """
        The action the entity will execute in the next epoch, if any.
        """
        return self._next_action

    @property
    def owner_id(self):
        """
        The `agent_id` of the owner
        """
        return self._owner_id

    @property
    def food(self):
        """
        How many units of food the entity is holding
        """
        return self._food

    @property
    def health(self):
        """
        The health amount the entity has
        """
        return self._health

    @property
    def max_health(self):
        """
        The maximum amount of health the entity can have
        """
        return self._max_health

    @property
    def missing_health(self):
        """
        How much damage the entity took, i.e how much health it is missing
        """
        return self._max_health - self._health

    @property
    def alive(self):
        """
        Checks if the entity is alive
        """
        return self._health > 0

    @property
    def dead(self):
        """
        Checks if the entity is dead
        """
        return self._health <= 0


class Food(BaseEntity):
    def __init__(self, data):
        super(Food, self).__init__(data)

        self._quantity = data["quantity"]

    @property
    def quantity(self):
        """
        How many units of food are present in this food source
        """
        return self._quantity


class Base(ActionableEntity):
    @property
    def can_spawn(self):
        """
        Returns `True` if there is enough food units to spawn a new actor from
        this base
        """
        return self.food >= FOOD_COST_TO_SPAWN_ACTOR

    def spawn(self):
        """
        Action to spawn a new :class:`Actor` from this base. Only happens if
        there is enough food. In case multiple spawn commands are issued, but
        there isn't enough food for all of them, they will be spawned following
        the order in which the commands were issued.
        """
        self.set_next_action({"action": "spawn", "base_id": self.id})


class Actor(ActionableEntity):
    def attack(self, target):
        """
        Issues an action to attack a target. Must be closer than 5 units for it
        to have an effect.

        Parameters
        ----------
        target
            Can be a string with an entity `id`, a dict that has an `id` key or
            an object with an `id` property.
        """
        target = get_id(target)

        self.set_next_action(
            {"action": "attack", "actor_id": self.id, "target": target}
        )

    def move(self, target):
        """
        Moves towards a `target` direction. When the direction is reached the
        actor no longer moves, unless a new target is issued.

        Parameters
        ----------
        target
            Can be either a `tuple` or `list` with a pair of coordinates, a
            `dict` that has a key named `position` or an object which has a
            `position` property.
        """
        target = get_position(target)

        self.set_next_action({"action": "move", "actor_id": self.id, "target": target})

    def take(self, target):
        """
        Parameters
        ----------
        target
            Can be a string with an entity `id`, a dict that has an `id` key or
            an object with an `id` property. Only works on a food source.
        """
        target = get_id(target)

        self.set_next_action(
            {"action": "take_food", "actor_id": self.id, "food_id": target}
        )

    def deposit_food(self, target):
        """
        Deposits all food on an Actor into a Base. Must be on top of the base
        for it to work. Lasts one epoch.

        Parameters
        ----------
        target
            Can be a string with an entity `id`, a dict that has an `id` key or
            an object with an `id` property. Only works on bases.
        """
        target = get_id(target)
        self.set_next_action(
            {"action": "deposit_food", "actor_id": self.id, "base_id": target}
        )

    def heal(self, target):
        """
        Heals an Actor on a Base. Must be on top of the base for it to work.
        Lasts one epoch. All health is restored, at the cost of one unity of
        food for one unity of health. If there are not enough food units to
        fully heal, the number of health restored is the amount of food
        available.

        Parameters
        ----------
        target
            Can be a string with an entity `id`, a dict that has an `id` key or
            an object with an `id` property. Only works on bases.
        """
        self.set_next_action({"action": "heal", "actor_id": self.id, "base_id": target})


class BaseCollection:
    """
    Base class for all Collection objects, such as :class:`Foods`,
    :class:`Bases` and :class:`Actors`. It provides multiple helper functions
    to select and filter objects.
    """

    def __init__(self, records, agent_id):
        """
        Parameters
        ----------
        records: list[object]
            A list of records belonging to a collection

        agent_id: string
            The `agent_id` of the Actor owning the collection. This is used to
            filter records owned or not by the owner of the collection.
        """
        self._records = records
        self._agent_id = agent_id

    def __inject(self, records):
        self._records.extend(records)
        return self

    def _update(self, new_state, agent_id=None):
        if agent_id:
            self._agent_id = agent_id

        logging.debug(f"{new_state=}")
        new_state_ids = set(x["id"] for x in new_state)

        # Delete entities that doesn't exist anymore
        self._records = [r for r in self._records if r.id in new_state_ids]

        # Update existing entities and create new ones
        for new_record_state in new_state:
            record = self.get_by_id(new_record_state["id"])
            if record:
                record._update(new_record_state)
            else:
                new_record = self._base_record(new_record_state)
                self._records.append(new_record)

    def filter(self, filter_function):
        """
        Parameters
        ----------
        func
            Takes a function (or lambda) that receives one argument, an entity,
            and returns a boolean. When `True` is returned the entity is kept
            in the collection, otherwise it is removed.

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`filter`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results.
        """
        filtered_records = [r for r in self._records if filter_function(r)]
        return self.__class__([], self._agent_id).__inject(filtered_records)

    @property
    def ids(self):
        """
        Returns
        -------
        list[string]
            Returns a list of ids from the records present in the collection.
        """
        return [x.id for x in self._records]

    def get_by_id(self, id):
        """
        Finds an object by `id`. If none is found, `None` is returned.

        Parameters
        ----------
        id: string
            Id too look for

        Returns
        -------
        object
            Returns an object with `id` (as defined by the `id` property, not
            the python internal `id`)
        """
        for r in self._records:
            if r.id == id:
                return r

    def id_in(self, collection):
        """
        Returns all objects which has an `id` in `collection`.

        Parameters
        ----------
        collection
            A list, tuple, set or any other object that can be tested for includeness.

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`id_in`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results.
        """
        return self.filter(lambda x: x.id in collection)

    def id_not_in(self, collection):
        """
        Returns all objects which doesn't have an `id` in `collection`.

        Parameters
        ----------
        collection
            A list, tuple, set or any other object that can be tested for includeness.

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`id_in`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results.
        """
        return self.filter(lambda x: x.id not in collection)

    def owner_is(self, owner_id):
        """
        Returns all objects with a given `owner_id`.

        Parameters
        ----------
        owner_id: string
            The `owner_id` to filter for

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`id_in`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results.
        """
        return self.filter(lambda x: x.owner_id == owner_id)

    def owner_is_not(self, owner_id):
        """
        Returns all objects not owned by `owner_id`.

        Parameters
        ----------
        owner_id: string
            The `owner_id` to filter for

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`id_in`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results.
        """
        return self.filter(lambda x: x.owner_id != owner_id)

    def sort_by_distance_to(self, entity):
        """
        Returns a sorted collection, ordered by distance to entity.

        Parameters
        ----------
        entity
            Can be either a `tuple` or `list` with a pair of coordinates, a
            `dict` that has a key named `position` or an object which has a
            `position` property.

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`id_in`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results. The contents are sorted by
            closest to farthest.

        Example
        -------
        All of the followin calls are equivalent and returns the same results::

            actor = Actor({"id": "foo", "position": (1, 1)})
            state.actors.sort_by_distance_to(actor)
            state.actors.sort_by_distance_to((1, 1))
            state.actors.sort_by_distance_to([1, 1])
            state.actors.sort_by_distance_to({"id": "foo", "position": (1, 1)})
        """
        records = sorted(self._records, key=lambda x: distance_between(x, entity))
        return self.__class__([], self._agent_id).__inject(records)

    def closest_to(self, entity):
        """
        Returns the closest entity in a collection to a given `entity`.

        Parameters
        ----------
        entity
            Can be either a `tuple` or `list` with a pair of coordinates, a
            `dict` that has a key named `position` or an object which has a
            `position` property.

        Returns
        -------
        object
            The closest object in the collection
        """
        if self.empty:
            return None
        return self.sort_by_distance_to(entity)[0]

    def farthest_from(self, entity):
        """
        Returns the farthest entity in a collection to a given `entity`.

        Parameters
        ----------
        entity
            Can be either a `tuple` or `list` with a pair of coordinates, a
            `dict` that has a key named `position` or an object which has a
            `position` property.

        Returns
        -------
        object
            The farthest object in the collection
        """
        if self.empty:
            return None
        return self.sort_by_distance_to(entity)[-1]

    @property
    def enemy(self):
        """
        Returns all objects not owned by the Agent.

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`id_in`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results.
        """
        return self.owner_is_not(self._agent_id)

    @property
    def mine(self):
        """
        Returns all objects owned by the Agent.

        Returns
        -------
        object
            Returns an object of the same type. e.g. if calling :meth:`id_in`
            from an :class:`Actors` object, an object of type :class:`Actors`
            will be returned, with the results.
        """
        return self.owner_is(self._agent_id)

    @property
    def count(self):
        """
        Returns
        -------
        int
            The number of records in the collection
        """
        return len(self)

    @property
    def empty(self):
        """
        Returns
        -------
        bool
            Returns `True` if there are records in the collection, `False` otherwise.
        """
        return self.count == 0

    @property
    def first(self):
        """
        Returns the first object of a collection, if any. First is definied as
        the in the json blob used to communicate the world state to the Agent.
        The order isn't guaranteed. The result of this method may change between
        different simulation epochs.

        Returns
        -------
        object
            Returns the first object from the collection, if any, othewise
            `None` is returned.
        """
        if self.count > 0:
            return self._records[0]

        return None

    @property
    def last(self):
        """
        Returns the last object of a collection, if any. Last is definied as
        the in the json blob used to communicate the world state to the Agent.
        The order isn't guaranteed. The result of this method may change between
        different simulation epochs.

        Returns
        -------
        object
            Returns the last object from the collection, if any, othewise
            `None` is returned.
        """
        if self.count > 0:
            return self._records[0]

        return None

    @property
    def random(self):
        """
        Returns a random object from a collection, or None if it is empty.
        Returns
        -------
        object
            Returns a random object from a collection. If the collection is
            empty, `None` is returned.
        """
        if self.count > 0:
            return choice(self._records)

        return None

    @property
    def actions(self):
        """
        Returns a list of actions that where issued to entities in this collection.
        """
        return [x.next_action for x in self._records if x.next_action]

    def __len__(self):
        return len(self._records)

    def __getitem__(self, key):
        return self._records[key]

    def __iter__(self):
        return (x for x in self._records)


class Actors(BaseCollection):
    """
    Collection with all :class:`Actor` entities in the world
    """

    def __init__(self, actors, agent_id):
        self._base_record = Actor
        records = [Actor(actor) for actor in actors]
        super(Actors, self).__init__(records, agent_id)


class Bases(BaseCollection):
    """
    Collection with all :class:`Base` entities in the world
    """

    def __init__(self, bases, agent_id):
        self._base_record = Base
        records = [Base(base) for base in bases]
        super(Bases, self).__init__(records, agent_id)


class Foods(BaseCollection):
    """
    Collection with all :class:`Food` entities in the world
    """

    def __init__(self, foods, agent_id):
        self._base_record = Food
        records = [Food(food) for food in foods]
        super(Foods, self).__init__(records, agent_id)


class State:
    """
    Encapsulates the world state. Can be used to issue commands to controlable
    entities, filter entities, etc. The state is writable, but only actions set
    by calling the action methods have an efect in the simulation. The
    :class:`State` and its children entities (food, actors and bases) are
    persisted across epochs and can have custom data set on them.
    """

    def __init__(self, state, owner_id):
        """
        Parameters
        ----------
        state: dict
            Receives the dict, parsed from the stdin json blob, representing
            the current world state.
        owner_id: string
            String with the `agent_id`. This is used to identify which entities
            belong to the agent holding the :class:`State` object.

            Manipulating this somehow will be automatically flagged as
            cheating.
        """
        self._state = state
        self._actors = Actors(state.get("actors", []), owner_id)
        self._bases = Bases(state.get("bases", []), owner_id)
        self._foods = Foods(state.get("foods", []), owner_id)
        self._agent_ids = state.get("agent_ids", [])

    @property
    def actors(self):
        """
        Returns
        -------
        list
            All actors present in the world
        """
        return self._actors

    @property
    def bases(self):
        """
        Returns
        -------
        list
            All bases present in the world
        """
        return self._bases

    @property
    def foods(self):
        """
        Returns
        -------
        List[str]
            All food pieces present in the world
        """
        return self._foods

    @property
    def agent_ids(self):
        """
        Returns
        -------
        list[string]
            A list with all the `agent_id` registered in the game match. This can be combined with other methods to filter units from a specifc agent, including the one holding the current :class:`State` object.
        """
        return self._agent_ids

    @property
    def actions(self):
        """
        Returns
        -------
        list[dict]
            Returns a list with all actions issued to all objects of type :class:`Actor` and :class:`Base`.
        """
        return self.actors.actions + self.bases.actions

    @property
    def empty(self):
        """
        Checks if there is data in the collection.

        Returns
        -------
        bool
            Returns `True` if :class:`State` has no data.
        """
        return self._state.get("actors") is None

    def _update(self, new_state, agent_id=None):
        """
        Apply changes from a new state on top of the existing entity
        collections. Existing instances are kept, dead ones are removed and new
        ones are created automatically.
        """
        self._actors._update(new_state.get("actors", []), agent_id)
        self._bases._update(new_state.get("bases", []), agent_id)
        self._foods._update(new_state.get("foods", []), agent_id)
        self._state = new_state


class Agent:
    """
    Encapsulates the game state and handles communication with the parent
    process and provides a framework to hold an Agent logic to play the
    colosseum games.
    """

    def __init__(self, agent_name, agent_version="0.1.0"):
        """
        Parameters
        ----------
        agent_name: string
            The agent name. This is reported back to the parent process and can
            appear in places like the leaderboards or match results.
        agent_version: string
            A string defining the agent version. This can be used to isolate
            performance from different agent versions.
        """
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.agent_id = None
        self.state = None
        self.run = True
        self.stop_reason = None

        self._raw_state = None
        self._next_response = {}

        logging.basicConfig(
            filename=f"{self.agent_name}_{get_internal_id()}.log", level=logging.INFO
        )

    def common_handlers(self):
        """
        Handles main actions common to colosseum. Such actions are `ping`,
        `stop` and `set_agent_id`. This must be called in every iteration in
        order to comply with the colosseum protocol.
        """
        self.handle_ping()
        self.handle_stop()
        self.handle_agent_id()

    def handle_ping(self):
        """
        Handles ping from the parent process. This can happen any number of
        times during the Agent lifetime, but is typically zero or one.

        The ping consists of a key named `ping`, where the value is a truthy
        statement, usually a string. The contents are irrelevant. The reply is
        made by adding a key named `pong` to the response, with a truthy value.
        """
        if self._raw_state.get("ping"):
            self._next_response["pong"] = "foobar"
            logging.debug("got ping")

    def handle_stop(self):
        """
        When received indicates that the agent must stop. No further reply back
        to the parent process is necessary. Attempting to communicate after
        receiving a `stop` message can result in a deadlock, which in turn is
        an autolose.

        This `self.run` is set to `False` and `self.stop_reason` to the payload
        from `stop`, which contains the reason why the agent was stoped.
        Usually because the game ended. Other causes may be because the
        cheating was detected, or because the agent lost all units and can't
        continue to play.
        """
        stop = self._raw_state.get("stop")

        if not stop:
            return

        self.run = False
        self.stop_reason = stop
        logging.debug(f"got stop reason: {stop}")

    def handle_agent_id(self):
        """
        Handles exchange of the `agent_id` from the parent process. This `id`
        is used to identify which agent owns the entities in the game. Every
        message after this one must include `agent_id`.
        """

        agent_id = self._raw_state.get("set_agent_id")

        if not agent_id:
            return

        self.agent_id = agent_id
        self._next_response["agent_name"] = self.agent_name
        self._next_response["agent_version"] = self.agent_version
        logging.debug(f"got agent id: {agent_id}")

    def read_state(self):
        """
        Reads data from stdin, containing the world state and extra messages
        from the parent process. When only internal messages are sent (such as
        a ping), this function automatically replies and reads the next
        message, until a world state is received.

        The full parsed response is stored in `self._raw_state`. An object of
        type :class:`State` encapsulating the world state is stored in
        `self.state`

        When a new world state is received :meth:`post_state_update` is
        caled. When inheriting from :class:`Agent`, this method can be
        overriden to trigger the Agent logic.
        """
        logging.debug("waiting state update")
        self._next_response = {}
        self._raw_state = get_state()
        self._update_state(self._raw_state)
        logging.debug("got state update")
        self.common_handlers()

        while self.state.empty:
            logging.debug("found empty")
            logging.debug(self._raw_state)
            self.send_commands()
            self._raw_state = get_state()
            self._update_state(self._raw_state)
            self.common_handlers()

        self.post_state_update()

    def send_commands(self):
        """
        calls :func:`send_commands` to send the Agent actions and
        communication messages back to the parent process.

        If `self.run` is false, nothing is sent.
        """
        # If the simulation tells us to stop, we dont talk back. This can
        # deadlock and cause the agent to deadlock, which is an autolose
        if not self.run:
            return

        payload = {}
        payload["actions"] = self.state.actions

        if self.agent_id:
            payload["agent_id"] = self.agent_id

        payload.update(self._next_response)

        send_commands(payload)

    def post_state_update(self):
        """
        Can be overriden by child classes. It is called immediately after a new
        world state is received.
        """
        pass

    def _update_state(self, raw_state):
        """
        Takes a new state and update the previous one, keeping the
        same object instances. New entities are automatically created,
        and the ones that died are automatically removed.
        """
        if self.state:
            self.state._update(raw_state, self.agent_id)
        else:
            self.state = State(raw_state, self.agent_id)


def send_commands(data):
    """
    Encodes a dict containing the commands and send them to the process
    wrapping the Agent. Data is sent to `stdout`.

    Parameters
    ----------
    dict
        A dict containing the data to send to parent process.
    """
    logging.debug(f"commands sent: {data}")
    data_encoded = json.dumps(data)
    sys.stdout.write(data_encoded + "\n")
    sys.stdout.flush()


def get_state():
    """
    Reads a line from stdin, parses it from json and returns the result.

    Returns
    -------
    dict
        Returns a dict with the data in the json blob read from stdin.
    """
    state_raw = sys.stdin.readline()
    state_data = json.loads(state_raw)
    return state_data
