# Food Catcher

Each agent starts with one base and one actor. The map has a random set of food
sources. The goal is to have finish the game with as much food as possible. All
food must be returned to the base for it to count.

## Actions

The following actions are available for the agents:

- `move`: Moves an actor towards a coordinate
  Example: Move actor `bar` towards (5, 5):
  ```
  {
    "actor_id:" "bar",
    "action": "move",
    "target": (5, 5)
  }
  ```

- `take_food`: Takes food from a food source. The actor must be close to it to
  be able to take food, otherwise nothing happens. Only a limited amount of
  food can be collected by game cycle.
  Example: Actor `bar` takes food from food source `foo`:
  ```
  {
    "actor_id:" "bar",
    "action": "take_food",
    "food_id": "foo"
  }
  ```

- `deposit_food`: Stores all the food in the actor to a base. All food is moved
  in a single cycle. The agent needs to be on top of the base to be able to
  deposit. There is a tolerance of 0.1 units.
  Example: Actor `bar` deposits food to base `qux`:
  ```
  {
    "actor_id:" "bar",
    "action": "deposit_food",
    "base_id": "qux"
  }
  ```

- `attack`: Short range attack against other actors and bases. The range is of
  4 units. While attacking the actor can't move or do any other action.
  Example: Attack base with id `qux`:
  ```
  {
    "actor_id:" "bar",
    "action": "attack",
    "base_id": "qux"
  }
  ```
  To attack an actor replace `base_id`  with `target_actor_id`. Having both set
  is an error and nothing happens.

- `heal`: Heals an actor at a base. Each unity of food heals one unity of
  health, until max health is reached. The agent needs to be on top of the base
  to be able to deposit. There is a tolerance of 0.1 units.
  ```
  {
    "actor_id:" "bar",
    "action": "heal",
    "base_id": "qux"
  }
  ```

- `spawn`: Spawns a new actor from a base. The actor is created right on top of
  the base. If there is another actor on top, a collision will be triggered. A
  new actor costs 100 units of food.
  Example: Spawn a new actor on top of base `qux`:
  ```
  {
    "action": "spawn",
    "base_id": "qux"
  }
  ```

- `make_base`: Turns an actor into a base. The actor is no long available after
  this command is run. A new base costs 500 units of food. All extra food on
  top of the base cost is stored in the new base. The base is created in the
  exact position the actor is ocupying when the command is issued.
  Example: Turn actor `bar` into a base:
  ```
  {
    "action": "make_base",
    "actor_id": "bar"
  }
  ```
