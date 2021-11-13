import json

from ..colosseum_sdk import State
from .fixtures import fixture_state_late


def make_state(fixture):
    state_data = json.loads(fixture)
    state = State(state_data)
    return state


def test_actors():
    state = make_state(fixture_state_late)
    assert len(state.actors) > 0


def test_bases():
    state = make_state(fixture_state_late)
    assert len(state.bases) > 0


def test_foods():
    state = make_state(fixture_state_late)
    assert len(state.foods) > 0


def test_actors_by_owner():
    state = make_state(fixture_state_late)
    agent_ids = state.agent_ids

    assert state.actors.by_owner(agent_ids[0]).count == 1
    assert state.actors.by_owner(agent_ids[1]).count == 1
    assert state.actors.by_owner(agent_ids[2]).count == 5


def test_bases_by_owner():
    state = make_state(fixture_state_late)
    agent_ids = state.agent_ids

    assert state.bases.by_owner(agent_ids[0]).count == 1
    assert state.bases.by_owner(agent_ids[1]).count == 1
    assert state.bases.by_owner(agent_ids[2]).count == 1
