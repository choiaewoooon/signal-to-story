from pathlib import Path
from pipeline.types import Script, Storyboard, StoryboardCut

# 운영 시 각 콘티 프레임은 Veo 3.1 Lite의 레퍼런스 이미지로 image-to-video 변환됨 (이 데모는 흉내).
_STYLE = "한국 증권 숏폼용 깔끔한 플랫 일러스트, 세로 9:16, 텍스트 없음, 일관된 색감. 장면: "


def split_cuts(script: Script) -> list[str]:
    return [script.hook, *script.cuts]


def generate_storyboard(script: Script, image_client, out_dir: str) -> Storyboard:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    cuts = []
    for i, caption in enumerate(split_cuts(script)):
        path = str(Path(out_dir) / f"cut_{i}.png")
        image_client.generate(_STYLE + caption, path)
        cuts.append(StoryboardCut(caption=caption, image_path=path))
    return Storyboard(cuts=cuts)
