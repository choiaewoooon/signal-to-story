import json
from pathlib import Path
from pipeline.types import Signal, Script

_PROMPT = (Path(__file__).parent.parent / "prompts" / "script.md").read_text(encoding="utf-8")


def build_prompt(signal: Signal) -> str:
    return _PROMPT.format(
        name=signal.name, ticker=signal.ticker,
        thesis=signal.thesis, metrics=json.dumps(signal.metrics, ensure_ascii=False),
    )


def parse_script(raw: str) -> Script:
    s = raw.strip()
    start, end = s.find("{"), s.rfind("}")
    data = json.loads(s[start : end + 1])
    return Script(
        hook=data["hook"], cuts=data["cuts"],
        cta=data["cta"], disclaimer=data["disclaimer"],
    )


def generate_script(signal: Signal, client) -> Script:
    raw = client.complete(build_prompt(signal))
    return parse_script(raw)
