import json
from pathlib import Path
from pipeline.types import Script, ComplianceReport, ComplianceFlag

_PROMPT = Path("prompts/compliance.md").read_text(encoding="utf-8")


def _script_text(script: Script) -> str:
    return " / ".join([script.hook, *script.cuts, script.cta])


def build_prompt(script: Script) -> str:
    return _PROMPT.format(script_text=_script_text(script))


def parse_report(raw: str) -> ComplianceReport:
    data = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
    flags = [
        ComplianceFlag(text=f["text"], reason=f["reason"], severity=f["severity"])
        for f in data["flags"]
    ]
    return ComplianceReport(flags=flags)


def check(script: Script, client) -> ComplianceReport:
    raw = client.complete(build_prompt(script))
    return parse_report(raw)
