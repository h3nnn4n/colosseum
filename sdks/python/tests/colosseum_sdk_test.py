import json

from ..colosseum_sdk import Actor, Base, Food, State
from .fixtures import fixture_state_late


def make_state(fixture, agent_id=None):
    world_state = json.loads(fixture)
    state = State(world_state["world_state"], agent_id)
    return state


def get_agent_ids(fixture):
    world_state = json.loads(fixture)
    state = State(world_state["world_state"], None)
    return state.agent_ids


def test_empty():
    state = make_state(fixture_state_late)
    assert not state.empty


def test_actors():
    state = make_state(fixture_state_late)
    assert len(state.actors) > 0


def test_first_actor():
    state = make_state(fixture_state_late)
    assert isinstance(state.actors.first, Actor)


def test_last_actor():
    state = make_state(fixture_state_late)
    assert isinstance(state.actors.last, Actor)


def test_random_actor():
    state = make_state(fixture_state_late)
    assert isinstance(state.actors.random, Actor)


def test_bases():
    state = make_state(fixture_state_late)
    assert len(state.bases) > 0


def test_first_base():
    state = make_state(fixture_state_late)
    assert isinstance(state.bases.first, Base)


def test_foods():
    state = make_state(fixture_state_late)
    assert len(state.foods) > 0


def test_first_food():
    state = make_state(fixture_state_late)
    assert isinstance(state.foods.first, Food)


def test_actors_owner_is():
    state = make_state(fixture_state_late)
    agent_ids = state.agent_ids

    assert state.actors.owner_is(agent_ids[0]).count == 1
    assert state.actors.owner_is(agent_ids[1]).count == 1
    assert state.actors.owner_is(agent_ids[2]).count == 5


def test_actors_mine():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = make_state(fixture_state_late, agent_id)

    assert state.actors.count == 7
    assert state.actors.mine.count == 5


def test_actors_enemy():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = make_state(fixture_state_late, agent_id)

    assert state.actors.count == 7
    assert state.actors.enemy.count == 2


def test_actors_get_by_id():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = make_state(fixture_state_late, agent_id)

    actor = state.actors.mine.first

    assert state.actors.get_by_id(actor.id) == actor


def test_actors_id_in():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = make_state(fixture_state_late, agent_id)

    actor = state.actors.mine.first

    assert state.actors.mine.count == 5
    assert state.actors.mine.id_in([actor.id]).count == 1


def test_actors_id_not_in():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = make_state(fixture_state_late, agent_id)

    actor = state.actors.mine.first

    assert state.actors.mine.count == 5
    assert state.actors.mine.id_not_in([actor.id]).count == 4


def test_bases_owner_is():
    state = make_state(fixture_state_late)
    agent_ids = state.agent_ids

    assert state.bases.owner_is(agent_ids[0]).count == 1
    assert state.bases.owner_is(agent_ids[1]).count == 1
    assert state.bases.owner_is(agent_ids[2]).count == 1


def test_move():
    state = make_state(fixture_state_late)
    state.actors.first.move((1, 1))
    actions = state.actions

    assert actions == [{"action": "move", "actor_id": "L0AZFC", "target": (1, 1)}]


def test_distance_to():
    state = make_state(fixture_state_late)

    assert state.actors.first.distance_to(state.bases.first) == 9.890839498372266


def test_foods_sort_by_distance_to():
    state = make_state(fixture_state_late)

    by_distance = state.foods.sort_by_distance_to((0, 0))
    closest = by_distance[0]
    farthest = by_distance[-1]

    assert closest.distance_to((0, 0)) < farthest.distance_to((0, 0))


def test_foods_closest_and_farthest():
    state = make_state(fixture_state_late)

    closest = state.foods.closest_to((0, 0))
    farthest = state.foods.farthest_from((0, 0))

    assert closest.distance_to((0, 0)) < farthest.distance_to((0, 0))


def test_update_delete_records():
    state = make_state(fixture_state_late)

    assert state.actors.count == 7
    assert state.bases.count == 3
    assert state.foods.count == 5

    new_state = {"foods": [], "actors": [], "bases": []}

    state._update(new_state)

    assert state.actors.count == 0
    assert state.bases.count == 0
    assert state.foods.count == 0


def test_update_create_food():
    state = make_state(fixture_state_late)

    assert state.foods.count == 5

    new_state = {"foods": [{"id": "foobar", "position": [1, 2], "quantity": 50}]}

    state._update(new_state)

    assert state.foods.count == 1
    assert state.foods.first.id == "foobar"
    assert state.foods.first.position == [1, 2]


def test_update_create_base():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = make_state(fixture_state_late, agent_id)

    assert state.bases.count == 3
    assert state.bases.mine.count == 1

    new_state = {
        "bases": [
            {
                "id": "spamegg",
                "position": [0, 1],
                "food": 0,
                "health": 50,
                "max_health": 50,
                "owner_id": agent_id,
            }
        ]
    }

    state._update(new_state)

    assert state.bases.count == 1
    assert state.bases.mine.count == 1
    assert state.bases.first.id == "spamegg"
    assert state.bases.first.position == [0, 1]


def test_update_create_actor():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = make_state(fixture_state_late, agent_id)

    assert state.actors.count == 7
    assert state.actors.mine.count == 5

    new_state = {
        "actors": [
            {
                "id": "quxqax",
                "position": [2, 3],
                "food": 0,
                "health": 50,
                "max_health": 50,
                "owner_id": agent_id,
            }
        ]
    }

    state._update(new_state)

    assert state.actors.count == 1
    assert state.actors.mine.count == 1
    assert state.actors.first.id == "quxqax"
    assert state.actors.first.position == [2, 3]


def test_update_food():
    state = make_state(fixture_state_late)

    assert state.foods.count == 5

    new_state = {"foods": [{"id": "foobar", "position": [1, 2], "quantity": 50}]}

    state._update(new_state)

    assert state.foods.count == 1
    assert state.foods.first.id == "foobar"
    assert state.foods.first.quantity == 50
    assert state.foods.first.position == [1, 2]

    new_state = {"foods": [{"id": "foobar", "position": [2, 3], "quantity": 40}]}

    state._update(new_state)

    assert state.foods.count == 1
    assert state.foods.first.id == "foobar"
    assert state.foods.first.quantity == 40
    assert state.foods.first.position == [2, 3]


def test_update_keep_tag():
    state = make_state(fixture_state_late)

    assert state.foods.count == 5

    new_state = {"foods": [{"id": "foobar", "position": [1, 2], "quantity": 50}]}

    state._update(new_state)

    state.foods.first.tag = "foo"

    assert state.foods.count == 1
    assert state.foods.first.id == "foobar"
    assert state.foods.first.tag == "foo"

    new_state = {"foods": [{"id": "foobar", "position": [2, 3], "quantity": 40}]}

    state._update(new_state)

    assert state.foods.count == 1
    assert state.foods.first.id == "foobar"
    assert state.foods.first.tag == "foo"


def test_update_empty():
    agent_id = get_agent_ids(fixture_state_late)[2]
    state = State({}, agent_id)

    assert state.empty

    new_state = {"actors": []}
    state._update(new_state)

    assert not state.empty
