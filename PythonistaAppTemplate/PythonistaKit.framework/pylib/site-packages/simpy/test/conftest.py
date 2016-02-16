import pytest

import simpy


@pytest.fixture
def log():
    return []


@pytest.fixture
def env():
    return simpy.Environment()
