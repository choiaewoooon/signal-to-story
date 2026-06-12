import os
from PIL import Image
from pipeline.clients import ClaudeCliClient, PlaceholderImageClient, ClaudeClient, ImageClient
from pipeline import factory


def test_claude_cli_client_uses_injected_runner():
    c = ClaudeCliClient(runner=lambda p: f"echo:{p}")
    assert c.complete("hi") == "echo:hi"


def test_placeholder_image_writes_valid_png(tmp_path):
    out = str(tmp_path / "cut.png")
    p = PlaceholderImageClient().generate("스타일. 장면: 기관 순매수 유입", out)
    assert os.path.exists(p)
    assert Image.open(out).size == (720, 1280)


def test_factory_keyless_when_no_keys(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert isinstance(factory.build_claude(), ClaudeCliClient)
    assert isinstance(factory.build_image(), PlaceholderImageClient)


def test_factory_real_when_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    assert isinstance(factory.build_claude(), ClaudeClient)
    assert isinstance(factory.build_image(), ImageClient)
