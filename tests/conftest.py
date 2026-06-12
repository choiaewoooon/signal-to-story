import pytest
from pathlib import Path
from pipeline.stage1_signal import load_signal


@pytest.fixture
def sample_signal():
    return load_signal(str(Path(__file__).parent.parent / "data" / "sample_signal.json"))
