import pytest

from ..games.food_catcher.game import Actor, Food
from ..utils import object_distance


def test_object_distance_two_objects():
    food = Food().set_position((0, 0))
    actor = Actor().set_position((1, 0))

    assert object_distance(food, actor) == 1
    assert object_distance(actor, food) == 1


def test_object_distance_object_and_dict():
    food = Food().set_position((0, 0))
    actor = {"position": (0, 1)}

    assert object_distance(food, actor) == 1
    assert object_distance(actor, food) == 1


def test_object_distance_object_two_dicts():
    food = {"position": (1, 0)}
    actor = {"position": (2, 0)}

    assert object_distance(food, actor) == 1
    assert object_distance(actor, food) == 1


def test_object_distance_null_object():
    actor = Actor()

    with pytest.raises(AssertionError):
        object_distance(None, actor)

    with pytest.raises(AssertionError):
        assert object_distance(actor, None)
