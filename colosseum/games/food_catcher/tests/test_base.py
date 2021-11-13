from ..game import Base


def test_health():
    base = Base()
    assert base.health > 0


def test_missing_health():
    base = Base()
    assert base.missing_health == 0

    base.deal_damage(1)
    assert base.missing_health == 1


def test_missing_heal():
    base = Base()
    assert base.missing_health == 0

    base.deal_damage(10)
    assert base.missing_health == 10

    base.heal(5)
    assert base.missing_health == 5

    base.heal(5)
    assert base.missing_health == 0


def test_alive():
    base = Base()
    assert base.alive
    base.deal_damage(base.health)
    assert not base.alive


def test_dead():
    base = Base()
    assert not base.dead
    base.deal_damage(base.health)
    assert base.dead
