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
