from colosseum.utils import random_id


class Base:
    def __init__(self):
        self.position = None
        self.id = random_id()
        self.owner_id = None
        self.food = 0
        self.health = 50
        self.max_health = self.health

    def set_owner(self, owner_id):
        self.owner_id = owner_id
        return self

    def set_position(self, position):
        self.position = position
        return self

    def add_food(self, food):
        self.food += food

    def drain_food(self, amount):
        self.food -= amount

    def deal_damage(self, damage):
        self.health -= damage

    def heal(self, amount):
        self.health += amount

    @property
    def missing_health(self):
        return self.max_health - self.health

    @property
    def alive(self):
        return self.health > 0

    @property
    def dead(self):
        return self.health <= 0

    @property
    def state(self):
        return {
            "position": self.position,
            "id": self.id,
            "owner_id": self.owner_id,
            "food": self.food,
            "health": self.health,
            "max_health": self.max_health,
        }
