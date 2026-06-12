from __future__ import annotations
import os


class ClaudeClient:
    """텍스트 인→아웃. 실제 Anthropic 호출."""

    def __init__(self, model: str = "claude-opus-4-8"):
        from anthropic import Anthropic
        self._client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model

    def complete(self, prompt: str) -> str:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text


class ImageClient:
    """프롬프트→이미지 파일 저장. 실제 OpenAI 이미지 호출."""

    def __init__(self, model: str = "gpt-image-1"):
        from openai import OpenAI
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._model = model

    def generate(self, prompt: str, out_path: str) -> str:
        import base64
        result = self._client.images.generate(
            model=self._model, prompt=prompt, size="1024x1536", n=1
        )
        data = base64.b64decode(result.data[0].b64_json)
        with open(out_path, "wb") as f:
            f.write(data)
        return out_path


class FakeClaudeClient:
    """테스트용. 주어진 응답을 순서대로 반환."""

    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self._responses:
            raise IndexError(f"FakeClaudeClient exhausted (no response for prompt: {prompt[:60]!r})")
        return self._responses.pop(0)


class FakeImageClient:
    """테스트용. 빈 파일을 만들고 경로 반환."""

    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def generate(self, prompt: str, out_path: str) -> str:
        self.calls.append((prompt, out_path))
        with open(out_path, "w") as f:
            f.write("fake-image")
        return out_path


class ClaudeCliClient:
    """Claude Code CLI 헤드리스(`claude -p`). 별도 API 결제 없이 구독으로 동작 (krx-ai-bot 패턴)."""

    def __init__(self, runner=None):
        self._runner = runner or _claude_cli_runner

    def complete(self, prompt: str) -> str:
        return self._runner(prompt)


def _claude_cli_runner(prompt: str) -> str:
    import subprocess
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {result.stderr[:200]}")
    return result.stdout


class PlaceholderImageClient:
    """PIL 캡션 카드 렌더(외부 서비스·키 0). 영상이 '흉내'이듯 콘티도 키리스로 흉내."""

    def generate(self, prompt: str, out_path: str) -> str:
        from PIL import Image, ImageDraw
        W, H = 720, 1280  # 9:16
        img = Image.new("RGB", (W, H), (20, 24, 33))
        draw = ImageDraw.Draw(img)
        caption = prompt.split("장면: ")[-1].strip()
        font = _load_korean_font(44)
        small = _load_korean_font(26)
        lines = _wrap(caption, 16)
        y = H // 2 - len(lines) * 32
        for line in lines:
            draw.text((60, y), line, font=font, fill=(235, 238, 245))
            y += 64
        draw.text((60, H - 90), "signal-to-story · 콘티(흉내)", font=small, fill=(120, 130, 150))
        img.save(out_path)
        return out_path


def _load_korean_font(size: int):
    from PIL import ImageFont
    for path in [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(text: str, width: int) -> list[str]:
    return [text[i : i + width] for i in range(0, len(text), width)] or [""]
