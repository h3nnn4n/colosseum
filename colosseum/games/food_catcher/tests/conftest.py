import random
import pytest


@pytest.fixture(autouse=True)
def fixed_random_seed():
    """keeps tests that use random number generation reproducible."""
    random.seed(42)
