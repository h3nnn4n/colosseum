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
  in a single cycle. Optionally a `quantity` may be specified to keep some food
  in the agent. The agent needs to be on top of the base to be able to depoist.
  Example: Actor `bar` deposits food to base `qux`:
  ```
  {
    "actor_id:" "bar",
    "action": "deposit_food",
    "base_id": "qux"
  }
  ```
