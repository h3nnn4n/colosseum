from ..game import Actor


def test_id():
    actor1 = Actor()
    actor2 = Actor()

    assert actor1.id
    assert actor2.id
    assert actor1.id != actor2.id


def test_add_food():
    actor = Actor()
    assert actor.food == 0

    actor.add_food(10)
    assert actor.food == 10

    actor.add_food(5)
    assert actor.food == 15


def test_take_food():
    actor = Actor()
    assert actor.food == 0

    actor.add_food(10)
    assert actor.food == 10
    assert actor.take_food() == 10
    assert actor.food == 0


def test_set_position():
    actor = Actor()

    actor.set_position((0, 0))
    assert actor.position == (0, 0)

    actor.set_position((5, 5))
    assert actor.position == (5, 5)


def test_set_owner():
    actor = Actor()

    actor.set_owner("foo")
    assert actor.owner_id == "foo"

    actor.set_owner("bar")
    assert actor.owner_id == "bar"


def test_move():
    actor = Actor().set_position((0, 0))
    assert actor.position == (0, 0)

    actor.move((1, 0))
    actor.move((1, 0))
    assert actor.position == (1, 0)

    actor.move((1, 1))
    actor.move((1, 1))
    assert actor.position == (1, 1)


def test_health():
    actor = Actor()
    assert actor.health > 0


def test_missing_health():
    actor = Actor()
    assert actor.missing_health == 0

    actor.deal_damage(1)
    assert actor.missing_health == 1


def test_missing_heal():
    actor = Actor()
    assert actor.missing_health == 0

    actor.deal_damage(10)
    assert actor.missing_health == 10

    actor.heal(5)
    assert actor.missing_health == 5

    actor.heal(5)
    assert actor.missing_health == 0


def test_alive():
    actor = Actor()
    assert actor.alive
    actor.deal_damage(actor.health)
    assert not actor.alive


def test_dead():
    actor = Actor()
    assert not actor.dead
    actor.deal_damage(actor.health)
    assert actor.dead
