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
