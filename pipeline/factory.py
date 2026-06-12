import os
from pipeline.clients import (
    ClaudeClient, ImageClient, ClaudeCliClient, PlaceholderImageClient,
)
from pipeline.orchestrator import Pipeline


def build_claude():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ClaudeClient()
    return ClaudeCliClient()


def build_image():
    if os.environ.get("OPENAI_API_KEY"):
        return ImageClient()
    return PlaceholderImageClient()


def mode_label() -> str:
    txt = "실제 API (Anthropic)" if os.environ.get("ANTHROPIC_API_KEY") else "키리스 (Claude CLI)"
    img = "실제 API (GPT Image)" if os.environ.get("OPENAI_API_KEY") else "키리스 (PIL 콘티)"
    return f"대본: {txt} · 콘티: {img}"


def make_pipeline(out_dir: str) -> Pipeline:
    return Pipeline(build_claude(), build_image(), out_dir=out_dir)
