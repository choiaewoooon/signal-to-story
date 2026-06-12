import json
from pathlib import Path
from pipeline.types import Signal, Script

_PROMPT = Path("prompts/script.md").read_text(encoding="utf-8")


def build_prompt(signal: Signal) -> str:
    return _PROMPT.format(
        name=signal.name, ticker=signal.ticker,
        thesis=signal.thesis, metrics=json.dumps(signal.metrics, ensure_ascii=False),
    )


def parse_script(raw: str) -> Script:
    data = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
    return Script(
        hook=data["hook"], cuts=data["cuts"],
        cta=data["cta"], disclaimer=data["disclaimer"],
    )


def generate_script(signal: Signal, client) -> Script:
    raw = client.complete(build_prompt(signal))
    return parse_script(raw)
