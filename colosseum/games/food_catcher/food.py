from random import uniform

from colosseum.utils import random_id


class Food:
    def __init__(self):
        self.position = None
        self.id = random_id()

        self.quantity_max = 50
        self.quantity_min = 0.1
        self.growth_rate = 0.05

        self.quantity = uniform(self.quantity_min, self.quantity_max)

    def set_quantity(self, quantity):
        self.quantity = quantity
        return self

    def set_position(self, position):
        self.position = position
        return self

    def update(self):
        self.grow()

    def grow(self):
        self.quantity = min(self.quantity * (1.0 + self.growth_rate), self.quantity_max)

    def take(self, amount):
        if amount < self.quantity:
            self.quantity -= amount
            return amount

        taken = self.quantity
        self.quantity = 0
        return taken

    @property
    def vanished(self):
        return self.quantity < self.quantity_min

    @property
    def state(self):
        return {"position": self.position, "quantity": self.quantity, "id": self.id}
