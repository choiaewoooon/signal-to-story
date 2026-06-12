import json
from pipeline.stage2_script import build_prompt, parse_script, generate_script
from pipeline.clients import FakeClaudeClient
from pipeline.types import Script


def test_build_prompt_includes_signal(sample_signal):
    p = build_prompt(sample_signal)
    assert "샘플전자" in p
    assert "자본시장법" in p


def test_parse_script_reads_json():
    raw = json.dumps({
        "hook": "주목받는 종목", "cuts": ["a", "b", "c"],
        "cta": "상세 보기", "disclaimer": "투자 책임은 본인에게 있습니다",
    }, ensure_ascii=False)
    s = parse_script(raw)
    assert isinstance(s, Script)
    assert s.cuts == ["a", "b", "c"]


def test_parse_script_tolerates_fenced_and_trailing_text():
    raw = '```json\n{"hook": "h", "cuts": ["a"], "cta": "c", "disclaimer": "d"}\n```\n설명을 덧붙입니다.'
    s = parse_script(raw)
    assert s.hook == "h"


def test_generate_script_uses_client(sample_signal):
    raw = json.dumps({
        "hook": "h", "cuts": ["1", "2", "3"], "cta": "c", "disclaimer": "d",
    }, ensure_ascii=False)
    client = FakeClaudeClient([raw])
    s = generate_script(sample_signal, client)
    assert s.hook == "h"
    assert "샘플전자" in client.prompts[0]
