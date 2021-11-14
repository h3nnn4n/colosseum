import json

import pexpect
import pytest


agent_paths = [
    "./agents/dummy_agent.py",
    "./agents/food_catcher_take_first_food.py",
    "./agents/food_catcher_take_nearest_food.py",
    "./agents/food_catcher_replicator.py",
    "./agents/food_catcher_exterminator.py",
]


@pytest.mark.parametrize("agent_path", agent_paths)
def test_agent_smoke_test(agent_path):
    runner = pexpect.spawn(agent_path)
    runner.setecho(False)

    runner.sendline(json.dumps({"ping": "foo"}))
    response = json.loads(runner.readline())

    assert response.get("pong") is not None

    runner.sendline(json.dumps({"set_agent_id": "bar"}))
    response = json.loads(runner.readline())

    runner.sendline(json.dumps({}))
    assert response.get("agent_id") == "bar"

    runner.sendline(json.dumps({"stop": {}}))

    runner.close()
