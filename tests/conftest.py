import pytest
from pipeline.stage1_signal import load_signal


@pytest.fixture
def sample_signal():
    return load_signal("data/sample_signal.json")
