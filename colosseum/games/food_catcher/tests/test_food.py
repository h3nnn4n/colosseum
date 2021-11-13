from ..game import Food


def test_set_quantity():
    food = Food().set_quantity(10)

    assert food.quantity == 10

    food = food.set_quantity(20)

    assert food.quantity == 20


def test_take():
    food = Food().set_quantity(10)

    assert food.quantity == 10
    assert food.take(7) == 7
    assert food.quantity == 3
    assert food.take(7) == 3
    assert food.quantity == 0
