import json
from pipeline.types import Signal


def load_signal(path: str) -> Signal:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return Signal(
        ticker=raw["ticker"],
        name=raw["name"],
        thesis=raw["thesis"],
        metrics=raw["metrics"],
    )
