from pipeline.stage1_signal import load_signal
from pipeline.types import Signal


def test_load_signal_reads_fixture():
    sig = load_signal("data/sample_signal.json")
    assert isinstance(sig, Signal)
    assert sig.name == "샘플전자"
    assert sig.metrics["기관_순매수_연속일"] == 5
