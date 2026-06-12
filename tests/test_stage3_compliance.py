import json
from pipeline.stage3_compliance import build_prompt, parse_report, check
from pipeline.clients import FakeClaudeClient
from pipeline.types import Script, ComplianceReport


def _script():
    return Script(hook="h", cuts=["반드시 오른다", "b", "c"], cta="c", disclaimer="d")


def test_build_prompt_includes_script():
    p = build_prompt(_script())
    assert "반드시 오른다" in p
    assert "자본시장법" in p


def test_parse_report_high_severity_fails():
    raw = json.dumps({"flags": [
        {"text": "반드시 오른다", "reason": "확정적 단정", "severity": "high"}
    ]}, ensure_ascii=False)
    rep = parse_report(raw)
    assert isinstance(rep, ComplianceReport)
    assert rep.passed is False


def test_parse_report_empty_passes():
    rep = parse_report(json.dumps({"flags": []}))
    assert rep.passed is True


def test_check_uses_client():
    raw = json.dumps({"flags": []})
    client = FakeClaudeClient([raw])
    rep = check(_script(), client)
    assert rep.passed is True
    assert "반드시 오른다" in client.prompts[0]
