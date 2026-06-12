import json
from pipeline.orchestrator import Pipeline
from pipeline.clients import FakeClaudeClient, FakeImageClient


def _claude():
    script = json.dumps({"hook": "h", "cuts": ["1", "2", "3"], "cta": "c", "disclaimer": "d"}, ensure_ascii=False)
    report = json.dumps({"flags": []})
    return FakeClaudeClient([script, report])


def test_run_until_gate_stops_before_storyboard(tmp_path, sample_signal):
    p = Pipeline(_claude(), FakeImageClient(), out_dir=str(tmp_path))
    p.run_until_gate(sample_signal)
    assert p.state == "AWAITING_APPROVAL"
    assert p.script is not None
    assert p.report is not None
    assert p.storyboard is None      # 승인 전엔 콘티 없음


def test_approve_then_resume_builds_storyboard(tmp_path, sample_signal):
    p = Pipeline(_claude(), FakeImageClient(), out_dir=str(tmp_path))
    p.run_until_gate(sample_signal)
    p.approve()
    p.resume()
    assert p.state == "DONE"
    assert len(p.storyboard.cuts) == 4
    assert p.conversion is not None


def test_reject_returns_to_script(tmp_path, sample_signal):
    p = Pipeline(_claude(), FakeImageClient(), out_dir=str(tmp_path))
    p.run_until_gate(sample_signal)
    p.reject()
    assert p.state == "REJECTED"
    assert p.storyboard is None
